from collections.abc import Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QKeySequence, QTransform
from PySide6.QtWidgets import QDialog, QLineEdit, QWidget

from providers.config import (
    DEEPSEEK_PROVIDER_ID,
    OPENAI_COMPATIBLE_PROVIDER_ID,
    ProviderConfig,
)
from providers.connection import ProviderConnectionTester
from providers.registry import (
    default_provider_config,
    get_provider_definition,
    provider_definitions,
)
from platforms.models import (
    Hotkey,
    default_hotkey_for_platform,
    hotkey_from_text,
    hotkey_to_text,
)
from ui.Ui_settingsdialog import Ui_settings_Dialog


PROVIDER_ICON_PATHS = {
    DEEPSEEK_PROVIDER_ID: ":/providers/icons/deepseek.svg",
    OPENAI_COMPATIBLE_PROVIDER_ID: ":/providers/icons/openai.svg",
}


class SettingsDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        initial_config: ProviderConfig | None = None,
        config_loader: Callable[[str], ProviderConfig] | None = None,
        connection_tester: ProviderConnectionTester | None = None,
        initial_hotkey: Hotkey | None = None,
    ) -> None:
        super().__init__(parent)

        self.ui = Ui_settings_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("设置")

        self._config_loader = config_loader or default_provider_config
        self._connection_tester = connection_tester or ProviderConnectionTester(
            parent=self
        )
        self._drafts: dict[str, ProviderConfig] = {}
        self._current_provider_id = ""
        self._connection_action = "test"

        self.ui.provider_comboBox.setAccessibleName("服务商")
        self.ui.model_comboBox.setAccessibleName("模型")
        self.ui.base_url_lineEdit.setAccessibleName("API 地址")
        self.ui.hotkey_keySequenceEdit.setAccessibleName("全局快捷键")
        self.ui.provider_label.setBuddy(self.ui.provider_comboBox)
        self.ui.model_label.setBuddy(self.ui.model_comboBox)
        self.ui.api_key_label.setBuddy(self.ui.api_key_lineEdit)
        self.ui.base_url_label.setBuddy(self.ui.base_url_lineEdit)
        self.ui.hotkey_label.setBuddy(self.ui.hotkey_keySequenceEdit)

        for definition in provider_definitions():
            self.ui.provider_comboBox.addItem(
                QIcon(
                    PROVIDER_ICON_PATHS.get(
                        definition.provider_id,
                        ":/mainwindow/icons/settings.svg",
                    )
                ),
                definition.display_name,
                definition.provider_id,
            )

        self.ui.status_label.clear()
        self.ui.status_label.hide()
        self.ui.advanced_widget.hide()
        self.ui.cancel_pushButton.clicked.connect(self.reject)
        self.ui.save_pushButton.clicked.connect(self.accept)
        self.ui.visibility_pushButton.toggled.connect(
            self.set_api_key_visible
        )
        self.ui.provider_comboBox.currentIndexChanged.connect(
            self._on_provider_changed
        )
        self.ui.test_pushButton.clicked.connect(self.test_connection)
        self.ui.refresh_models_pushButton.clicked.connect(
            self.refresh_models
        )
        self.ui.advanced_toggleButton.toggled.connect(
            self.set_advanced_settings_visible
        )
        self._connection_tester.started.connect(self._on_test_started)
        self._connection_tester.succeeded.connect(self._on_test_succeeded)
        self._connection_tester.failed.connect(self._on_test_failed)

        initial = initial_config or self._config_loader(DEEPSEEK_PROVIDER_ID)
        self._drafts[initial.provider_id] = initial
        index = self.ui.provider_comboBox.findData(initial.provider_id)
        self.ui.provider_comboBox.setCurrentIndex(max(index, 0))
        self._show_config(initial)
        self.set_hotkey(initial_hotkey or default_hotkey_for_platform())
        self.set_advanced_settings_visible(False)

    def api_key(self) -> str:
        return self.ui.api_key_lineEdit.text().strip()

    def set_api_key(self, api_key: str) -> None:
        self.ui.api_key_lineEdit.setText(api_key)

    def provider_config(self) -> ProviderConfig:
        return ProviderConfig(
            provider_id=self.current_provider_id(),
            base_url=self.ui.base_url_lineEdit.text().strip(),
            model=self.ui.model_comboBox.currentText().strip(),
            api_key=self.api_key(),
        )

    def current_provider_id(self) -> str:
        return str(self.ui.provider_comboBox.currentData())

    def hotkey(self) -> Hotkey:
        portable_text = (
            self.ui.hotkey_keySequenceEdit
            .keySequence()
            .toString(QKeySequence.SequenceFormat.PortableText)
        )
        return hotkey_from_text(portable_text)

    def set_hotkey(self, hotkey: Hotkey) -> None:
        self.ui.hotkey_keySequenceEdit.setKeySequence(
            QKeySequence(hotkey_to_text(hotkey))
        )

    def set_api_key_visible(self, visible: bool) -> None:
        echo_mode = (
            QLineEdit.EchoMode.Normal
            if visible
            else QLineEdit.EchoMode.Password
        )
        icon_path = (
            ":/settings/icons/eye-off.svg"
            if visible
            else ":/settings/icons/eye.svg"
        )
        action_text = "隐藏 API Key" if visible else "显示 API Key"

        self.ui.api_key_lineEdit.setEchoMode(echo_mode)
        self.ui.visibility_pushButton.setIcon(QIcon(icon_path))
        self.ui.visibility_pushButton.setToolTip(action_text)
        self.ui.visibility_pushButton.setAccessibleName(action_text)

    def test_connection(self) -> None:
        self._connection_action = "test"
        self._connection_tester.test(self.provider_config())

    def refresh_models(self) -> None:
        self._connection_action = "refresh"
        self._connection_tester.test(self.provider_config())

    def set_advanced_settings_visible(self, visible: bool) -> None:
        self.ui.advanced_widget.setVisible(visible)
        action_text = "收起高级设置" if visible else "高级设置"
        accessible_text = "收起高级设置" if visible else "展开高级设置"
        self.ui.advanced_toggleButton.setText(action_text)
        self.ui.advanced_toggleButton.setToolTip(accessible_text)
        self.ui.advanced_toggleButton.setAccessibleName(accessible_text)

        icon = QIcon(":/settings/icons/chevron-down.svg")
        if visible:
            pixmap = icon.pixmap(QSize(28, 28)).transformed(
                QTransform().rotate(180),
                Qt.TransformationMode.SmoothTransformation,
            )
            icon = QIcon(pixmap)
        self.ui.advanced_toggleButton.setIcon(icon)

        self.layout().activate()
        self.resize(self.width(), self.sizeHint().height())

    def _on_provider_changed(self, _index: int) -> None:
        new_provider_id = self.current_provider_id()
        if not new_provider_id or new_provider_id == self._current_provider_id:
            return

        if self._current_provider_id:
            self._drafts[self._current_provider_id] = ProviderConfig(
                provider_id=self._current_provider_id,
                base_url=self.ui.base_url_lineEdit.text().strip(),
                model=self.ui.model_comboBox.currentText().strip(),
                api_key=self.api_key(),
            )

        config = self._drafts.get(new_provider_id)
        if config is None:
            config = self._config_loader(new_provider_id)
            self._drafts[new_provider_id] = config
        self._show_config(config)

    def _show_config(self, config: ProviderConfig) -> None:
        self._current_provider_id = config.provider_id
        definition = get_provider_definition(config.provider_id)
        self.ui.base_url_lineEdit.setText(config.base_url)
        self.ui.model_comboBox.clear()
        if config.model:
            self.ui.model_comboBox.addItem(config.model)
            self.ui.model_comboBox.setCurrentText(config.model)
        self.ui.api_key_lineEdit.setText(config.api_key)
        hint = (
            "API Key 必填，仅保存在系统凭据库"
            if definition.requires_api_key
            else "API Key 可选，仅保存在系统凭据库"
        )
        self.ui.api_key_hint_label.setText(hint)
        self.ui.status_label.hide()

    def _on_test_started(self) -> None:
        self.ui.test_pushButton.setEnabled(False)
        self.ui.refresh_models_pushButton.setEnabled(False)
        message = (
            "正在测试…"
            if self._connection_action == "test"
            else "正在刷新…"
        )
        self._show_status(message, "#64748B")

    def _on_test_succeeded(self, models: object) -> None:
        self.ui.test_pushButton.setEnabled(True)
        self.ui.refresh_models_pushButton.setEnabled(True)
        model_names = [str(model) for model in models]
        current_model = self.ui.model_comboBox.currentText().strip()
        self.ui.model_comboBox.clear()
        self.ui.model_comboBox.addItems(model_names)
        if current_model:
            if self.ui.model_comboBox.findText(current_model) < 0:
                self.ui.model_comboBox.insertItem(0, current_model)
            self.ui.model_comboBox.setCurrentText(current_model)
        message = (
            "● 连接成功"
            if self._connection_action == "test"
            else f"● 已刷新 {len(model_names)} 个"
        )
        self._show_status(message, "#15803D")

    def _on_test_failed(self, message: str) -> None:
        self.ui.test_pushButton.setEnabled(True)
        self.ui.refresh_models_pushButton.setEnabled(True)
        status_text = (
            "● 连接失败"
            if self._connection_action == "test"
            else "● 刷新失败"
        )
        self._show_status(status_text, "#B91C1C", message)

    def _show_status(
        self,
        message: str,
        color: str,
        detail: str = "",
    ) -> None:
        self.ui.status_label.setText(message)
        self.ui.status_label.setStyleSheet(f"color: {color};")
        self.ui.status_label.setToolTip(detail)
        self.ui.status_label.show()
