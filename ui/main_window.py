import sqlite3

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QCloseEvent, QGuiApplication, QIcon
from PySide6.QtWidgets import QDialog, QMainWindow, QWidget

from providers.config import ProviderConfig
from providers.connection import ProviderConnectionTester
from providers.registry import validate_provider_config
from history.repository import HistoryRepository
from translation.manager import TranslationManager
from translation.models import TranslationRequest
from ui.Ui_mainwindow import Ui_MainWindow
from ui.floating_dialog import FloatingTranslationDialog
from ui.history_dialog import HistoryDialog
from ui.setting_dialog import SettingsDialog
from settings.store import CredentialStoreError, SettingsStore


class MainWindow(QMainWindow):
    provider_config_changed = Signal(object)
    hotkey_change_requested = Signal(object)

    def __init__(
        self,
        translation_manager: TranslationManager,
        settings_store: SettingsStore,
        connection_tester: ProviderConnectionTester | None = None,
        history_repository: HistoryRepository | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._settings_store = settings_store
        self._history_repository = history_repository
        self._current_provider_config = settings_store.load_active_config()
        self._connection_tester = connection_tester or ProviderConnectionTester(
            parent=self
        )

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # combox 内置语言
        self.ui.translation_comboBox.setItemData(0, "zh-CN")
        self.ui.translation_comboBox.setItemData(1, "en")
        default_target_language = (
            self._settings_store.load_default_target_language()
        )
        default_target_index = self.ui.translation_comboBox.findData(
            default_target_language
        )
        self.ui.translation_comboBox.setCurrentIndex(
            max(default_target_index, 0)
        )

        self._translation_manager = translation_manager
        self._floating_dialog = FloatingTranslationDialog(
            translation_manager,
        )
        self._floating_dialog.set_target_language(
            self.current_target_language()
        )

        self.ui.translation_plainTextEdit.setReadOnly(True)     # 设置翻译文本框只读

        # 自动翻译定时器
        self.auto_translate_timer = QTimer(self)
        self.auto_translate_timer.setSingleShot(True)
        self.auto_translate_timer.setInterval(800)      # 设置 800 毫秒无输入时自动翻译

        # 按钮定时器
        self.copy_button_timer = QTimer(self)
        self.copy_button_timer.setSingleShot(True)

        ## 连接信号和槽
        # 定时器超时自动翻译槽
        self.auto_translate_timer.timeout.connect(
            self.start_auto_translation
            )
        # 定时器超时自动复原按钮
        self.copy_button_timer.timeout.connect(
            self.reset_button
        )
        # 连接输入框
        self.ui.origin_plainTextEdit.textChanged.connect(
            self.schedule_auto_translation
        )
        # 目标语言改变自动翻译
        self.ui.translation_comboBox.currentIndexChanged.connect(
            self.on_target_language_changed
        )

        # 连接按钮槽
        self.ui.copy_pushButton.clicked.connect(
            self.copy_translation
            )
        self.ui.translation_plainTextEdit.textChanged.connect(
            self.update_copy_button
            )

        self._translation_manager.translation_started.connect(
            self.on_translation_started
            )
        self._translation_manager.translation_updated.connect(
            self.on_translation_updated
            )
        self._translation_manager.translation_completed.connect(
            self.on_translation_completed
            )
        self._translation_manager.translation_failed.connect(
            self.on_translation_failed
            )
        self._translation_manager.translation_cancelled.connect(
            self.on_translation_cancelled
            )
        self._translation_manager.translation_succeeded.connect(
            self.save_translation_history
        )

        self._floating_dialog.target_language_changed.connect(
            self.on_floating_target_language_changed
        )
        self._floating_dialog.translation_requested.connect(
            self.on_floating_translation_requested
        )

        # 打开设置
        self.ui.settings_pushButton.clicked.connect(
            self.on_settings_clicked
            )
        self.ui.history_pushButton.clicked.connect(
            self.on_history_clicked
        )
        self.ui.history_pushButton.setEnabled(
            self._history_repository is not None
        )

        # 复制按钮不使能
        self.update_copy_button()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._floating_dialog.close()
        super().closeEvent(event)

    def copy_translation(self) -> None:
        """将文本复制到剪贴板"""
        translated_text = self.ui.translation_plainTextEdit.toPlainText().strip()

        if not translated_text:
            return

        icon_path = ":/mainwindow/icons/check.svg"
        self.ui.copy_pushButton.setIcon(QIcon(icon_path))
        self.copy_button_timer.start(1500)

        QGuiApplication.clipboard().setText(translated_text)
        self.statusBar().showMessage("译文已复制", 2000)

    def reset_button(self) -> None:
        """重置界面状态"""
        icon_path = ":/mainwindow/icons/copy.svg"
        self.ui.copy_pushButton.setIcon(QIcon(icon_path))

    def update_copy_button(self) -> None:
        """更新复制按钮状态"""
        has_translation = bool(
            self.ui.translation_plainTextEdit.toPlainText().strip()
        )
        self.ui.copy_pushButton.setEnabled(has_translation)

    def schedule_auto_translation(self) -> None:
        """用户停止输入一段时间后自动翻译"""
        self.auto_translate_timer.stop()

        source_text = (
            self.ui.origin_plainTextEdit
            .toPlainText()
            .strip()
            )

        if not source_text:
            self._translation_manager.cancel_current()
            self.ui.translation_plainTextEdit.clear()
            self.statusBar().clearMessage()
            return

        # 修改原文后旧的请求失效
        self._translation_manager.cancel_current()

        self.statusBar().showMessage("正在翻译...")
        self.auto_translate_timer.start()

    def current_target_language(self) -> str:
        return str(self.ui.translation_comboBox.currentData())

    def on_target_language_changed(self, _index: int) -> None:
        target_language = self.current_target_language()
        self._settings_store.save_default_target_language(target_language)
        self._floating_dialog.set_target_language(target_language)
        self.schedule_auto_translation()

    def on_floating_target_language_changed(
        self,
        target_language: str,
    ) -> None:
        self._settings_store.save_default_target_language(target_language)
        target_index = self.ui.translation_comboBox.findData(target_language)
        if target_index >= 0:
            blocked = self.ui.translation_comboBox.blockSignals(True)
            self.ui.translation_comboBox.setCurrentIndex(target_index)
            self.ui.translation_comboBox.blockSignals(blocked)

        source_text = (
            self._floating_dialog.ui.source_text_edit
            .toPlainText()
            .strip()
        )
        if source_text:
            self._floating_dialog.request_current_translation()

    def on_floating_translation_requested(
        self,
        source_text: str,
        target_language: str,
    ) -> None:
        """同步悬浮窗原文，并提交它发起的翻译请求。"""
        blocked = self.ui.origin_plainTextEdit.blockSignals(True)
        self.ui.origin_plainTextEdit.setPlainText(source_text)
        self.ui.origin_plainTextEdit.blockSignals(blocked)
        self.auto_translate_timer.stop()
        self._translation_manager.translate(
            text=source_text,
            target_language=target_language,
        )

    def start_auto_translation(self) -> None:
        """自动翻译"""
        source_text = (
            self.ui.origin_plainTextEdit
            .toPlainText()
            .strip()
            )

        if not source_text:
            return

        target_language = self.current_target_language()

        self._translation_manager.translate(
            text=source_text,
            target_language=target_language
        )


    def on_translation_started(self, request_id: str) -> None:
        # 保留上一条译文，直到新请求返回第一个有效片段。
        self.statusBar().showMessage("正在翻译…")

    def on_translation_updated(self, translated_text: str) -> None:
        self.ui.translation_plainTextEdit.setPlainText(
            translated_text
        )

    def on_translation_completed(self, translated_text: str) -> None:
        self.ui.translation_plainTextEdit.setPlainText(
            translated_text
        )
        self.statusBar().showMessage("翻译完成", 2000)

    def on_translation_failed(self, message: str) -> None:
        self.statusBar().showMessage(message, 3000)

    def on_translation_cancelled(self) -> None:
        self.statusBar().showMessage("已取消旧翻译")

    def on_global_hotkey_registered(
        self,
        display_text: str = "Ctrl + Shift + T",
    ) -> None:
        self.statusBar().showMessage(
            f"全局快捷键 {display_text} 已启用",
            3000,
        )

    def on_global_hotkey_activated(self) -> None:
        self.statusBar().showMessage(
            "已收到全局快捷键，正在读取所选文字…"
        )

    def on_global_hotkey_registration_failed(self, message: str) -> None:
        self.statusBar().showMessage(message, 5000)

    def on_text_capture_started(self) -> None:
        self.statusBar().showMessage("正在读取所选文字…")

    def on_selected_text_captured(self, text: str) -> None:
        """在独立悬浮窗中显示取词结果并立即开始翻译。"""
        text = text.strip()
        if not text:
            self.on_text_capture_failed("未读取到所选文字")
            return

        blocked = self.ui.origin_plainTextEdit.blockSignals(True)
        self.ui.origin_plainTextEdit.setPlainText(text)
        self.ui.origin_plainTextEdit.blockSignals(blocked)
        self.auto_translate_timer.stop()
        self._start_floating_translation(
            text,
            self.current_target_language(),
        )

    def _start_floating_translation(
        self,
        text: str,
        target_language: str,
    ) -> None:
        self._floating_dialog.begin_translation(text, target_language)
        self.on_floating_translation_requested(text, target_language)

    def on_text_capture_failed(self, message: str) -> None:
        self._floating_dialog.show_capture_error(message)
        self.statusBar().showMessage(message, 5000)

    def save_translation_history(
        self,
        request: TranslationRequest,
        translated_text: str,
    ) -> None:
        if self._history_repository is None:
            return
        try:
            self._history_repository.add(
                request,
                translated_text,
                provider=self._current_provider_config.provider_id,
                model=self._current_provider_config.model,
            )
        except sqlite3.Error:
            self.statusBar().showMessage("无法保存翻译历史", 3000)

    def on_history_clicked(self) -> None:
        if self._history_repository is None:
            return
        dialog = HistoryDialog(self._history_repository, self)
        dialog.reuse_requested.connect(self.reuse_history_entry)
        dialog.exec()

    def reuse_history_entry(
        self,
        source_text: str,
        target_language: str,
    ) -> None:
        target_index = self.ui.translation_comboBox.findData(target_language)
        if target_index >= 0:
            self.ui.translation_comboBox.setCurrentIndex(target_index)
        self.ui.origin_plainTextEdit.setPlainText(source_text)
        self.auto_translate_timer.stop()
        self.showNormal()
        self.show()
        self.raise_()
        self.activateWindow()
        self.start_auto_translation()

    def on_settings_clicked(self) -> None:
        dialog = SettingsDialog(
            self,
            initial_config=self._settings_store.load_active_config(),
            config_loader=self._settings_store.load_provider_config,
            connection_tester=self._connection_tester,
            initial_hotkey=self._settings_store.load_hotkey(),
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            config = validate_provider_config(dialog.provider_config())
            hotkey = dialog.hotkey()
            self._settings_store.save_provider_config(config)
        except (ValueError, CredentialStoreError) as error:
            self.statusBar().showMessage(str(error), 3000)
            return

        self.statusBar().showMessage("设置已保存并应用", 2000)
        self._current_provider_config = config
        self.provider_config_changed.emit(config)
        # 同步注册结果会覆盖上面的通用成功提示，确保冲突信息可见。
        self.hotkey_change_requested.emit(hotkey)
