import sys

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QCursor, QGuiApplication, QIcon
from PySide6.QtWidgets import QDialog, QWidget

from translation.manager import TranslationManager
from translation.models import TranslationRequest
from ui.Ui_floatingdialog import Ui_floating_dialog


class FloatingTranslationDialog(QDialog):
    target_language_changed = Signal(str)
    translation_requested = Signal(str, str)

    AUTO_TRANSLATE_DELAY_MS = 800

    def __init__(
        self,
        translation_manager: TranslationManager,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.ui = Ui_floating_dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        if sys.platform == "darwin":
            # Qt 默认会在应用失去激活时隐藏 macOS 工具窗。
            self.setAttribute(
                Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow,
                True,
            )

        self._translation_manager = translation_manager
        self._request_id: str | None = None
        self._awaiting_request = False
        self._source_change_timer = QTimer(self)
        self._source_change_timer.setSingleShot(True)
        self._source_change_timer.setInterval(
            self.AUTO_TRANSLATE_DELAY_MS
        )

        self.ui.target_language_combo_box.clear()
        self.ui.target_language_combo_box.addItem("简体中文", "zh-CN")
        self.ui.target_language_combo_box.addItem("英文", "en")
        self.ui.copy_translation_push_button.setEnabled(False)

        self.ui.copy_translation_push_button.clicked.connect(
            self.copy_translation
        )
        self.ui.source_text_edit.textChanged.connect(
            self.schedule_source_translation
        )
        self._source_change_timer.timeout.connect(
            self.request_current_translation
        )
        self.ui.target_language_combo_box.currentIndexChanged.connect(
            self._emit_target_language_changed
        )
        translation_manager.request_created.connect(self._on_request_created)
        translation_manager.translation_progress.connect(
            self._on_translation_progress
        )
        translation_manager.translation_succeeded.connect(
            self._on_translation_succeeded
        )
        translation_manager.translation_error.connect(
            self._on_translation_error
        )
        translation_manager.translation_stopped.connect(
            self._on_translation_stopped
        )

    def begin_translation(self, text: str, target_language: str) -> None:
        self._source_change_timer.stop()
        self._request_id = None
        self._awaiting_request = True
        blocked = self.ui.source_text_edit.blockSignals(True)
        self.ui.source_text_edit.setPlainText(text.strip())
        self.ui.source_text_edit.blockSignals(blocked)
        self.ui.translation_text_edit.clear()
        self.ui.translation_text_edit.setPlaceholderText("正在翻译…")
        self.ui.copy_translation_push_button.setIcon(
            QIcon(":/mainwindow/icons/copy.svg")
        )
        self.ui.copy_translation_push_button.setToolTip("复制译文")
        self.ui.copy_translation_push_button.setEnabled(False)
        self.set_target_language(target_language)
        self._show_near_cursor()

    def show_capture_error(self, message: str) -> None:
        self._source_change_timer.stop()
        self._request_id = None
        self._awaiting_request = False
        blocked = self.ui.source_text_edit.blockSignals(True)
        self.ui.source_text_edit.clear()
        self.ui.source_text_edit.blockSignals(blocked)
        self.ui.translation_text_edit.setPlainText(message)
        self.ui.copy_translation_push_button.setEnabled(False)
        self._show_near_cursor()

    def set_target_language(self, target_language: str) -> None:
        index = self.ui.target_language_combo_box.findData(target_language)
        if index < 0:
            index = 0
        blocked = self.ui.target_language_combo_box.blockSignals(True)
        self.ui.target_language_combo_box.setCurrentIndex(index)
        self.ui.target_language_combo_box.blockSignals(blocked)

    def current_target_language(self) -> str:
        return str(self.ui.target_language_combo_box.currentData())

    def copy_translation(self) -> None:
        translated_text = self.ui.translation_text_edit.toPlainText().strip()
        if not translated_text:
            return
        QGuiApplication.clipboard().setText(translated_text)
        self.ui.copy_translation_push_button.setIcon(
            QIcon(":/mainwindow/icons/check.svg")
        )
        self.ui.copy_translation_push_button.setToolTip("译文已复制")

    def schedule_source_translation(self) -> None:
        """停止编辑一段时间后翻译悬浮窗中的最新全文。"""
        self._source_change_timer.stop()
        source_text = self.ui.source_text_edit.toPlainText().strip()

        self._request_id = None
        self._awaiting_request = False
        self._translation_manager.cancel_current()
        if not source_text:
            self.ui.translation_text_edit.clear()
            self.ui.translation_text_edit.setPlaceholderText(
                "输入原文后自动翻译"
            )
            self.ui.copy_translation_push_button.setEnabled(False)
            return

        self.ui.translation_text_edit.setPlaceholderText("等待输入完成…")
        self._source_change_timer.start()

    def request_current_translation(self) -> None:
        """立即提交悬浮窗当前文本，供窗口协调器发起翻译。"""
        self._source_change_timer.stop()
        source_text = self.ui.source_text_edit.toPlainText().strip()
        if not source_text:
            return

        self._request_id = None
        self._awaiting_request = True
        self.ui.translation_text_edit.setPlaceholderText("正在翻译…")
        self.ui.copy_translation_push_button.setIcon(
            QIcon(":/mainwindow/icons/copy.svg")
        )
        self.ui.copy_translation_push_button.setToolTip("复制译文")
        self.translation_requested.emit(
            source_text,
            self.current_target_language(),
        )

    def _emit_target_language_changed(self, _index: int) -> None:
        self.target_language_changed.emit(self.current_target_language())

    def _on_request_created(self, request: TranslationRequest) -> None:
        if not self._awaiting_request:
            return
        self._awaiting_request = False
        self._request_id = request.request_id

    def _on_translation_progress(
        self,
        request_id: str,
        translated_text: str,
    ) -> None:
        if request_id != self._request_id:
            return
        self.ui.translation_text_edit.setPlainText(translated_text)

    def _on_translation_succeeded(
        self,
        request: TranslationRequest,
        translated_text: str,
    ) -> None:
        if request.request_id != self._request_id:
            return
        self.ui.translation_text_edit.setPlainText(translated_text)
        self.ui.copy_translation_push_button.setEnabled(
            bool(translated_text.strip())
        )
        self._request_id = None

    def _on_translation_error(self, request_id: str, message: str) -> None:
        if request_id != self._request_id:
            return
        self.ui.translation_text_edit.setPlainText(message)
        self.ui.copy_translation_push_button.setEnabled(False)
        self._request_id = None

    def _on_translation_stopped(self, request_id: str) -> None:
        if request_id != self._request_id:
            return
        self.ui.translation_text_edit.setPlaceholderText("翻译已取消")
        self.ui.copy_translation_push_button.setEnabled(False)
        self._request_id = None

    def _show_near_cursor(self) -> None:
        self.adjustSize()
        cursor_position = QCursor.pos()
        screen = QGuiApplication.screenAt(cursor_position)
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            x = min(
                cursor_position.x() + 16,
                available.right() - self.width(),
            )
            y = min(
                cursor_position.y() + 20,
                available.bottom() - self.height(),
            )
            self.move(max(x, available.left()), max(y, available.top()))
        self.show()
        self.raise_()
        if sys.platform == "darwin":
            # 原生窗口在 show() 后才创建，再提升一次可避免首次显示层级偏低。
            QTimer.singleShot(0, self.raise_)
