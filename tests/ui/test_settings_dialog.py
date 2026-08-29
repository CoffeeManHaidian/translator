from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QDialog

from ui.setting_dialog import SettingsDialog
from platforms.models import Hotkey


class StubConnectionTester(QObject):
    started = Signal()
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.configs = []

    def test(self, config) -> None:
        self.configs.append(config)
        self.started.emit()


def test_settings_dialog_returns_trimmed_api_key(qtbot) -> None:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    dialog.ui.api_key_lineEdit.setText("  secret-key  ")

    assert dialog.api_key() == "secret-key"


def test_settings_dialog_uses_compact_controls(qtbot) -> None:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    dialog.ensurePolished()
    dialog.layout().activate()

    assert dialog.ui.provider_comboBox.height() <= 30
    assert dialog.ui.model_comboBox.height() <= 30
    assert dialog.ui.save_pushButton.height() <= 30
    assert dialog.ui.cancel_pushButton.height() <= 30
    assert dialog.ui.test_pushButton.height() <= 30
    assert "QComboBox#provider_comboBox::down-arrow" in dialog.styleSheet()
    assert "chevron-down.svg" in dialog.styleSheet()


def test_provider_and_model_are_icon_and_dropdown_controls(qtbot) -> None:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    assert not dialog.ui.provider_comboBox.itemIcon(0).isNull()
    assert not dialog.ui.model_comboBox.isEditable()
    assert dialog.ui.refresh_models_pushButton.toolTip() == "刷新模型列表"


def test_advanced_api_address_is_collapsed_by_default(qtbot) -> None:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    assert dialog.ui.advanced_widget.isHidden()
    assert dialog.ui.base_url_label.text() == "API 地址"

    qtbot.mouseClick(
        dialog.ui.advanced_toggleButton,
        Qt.MouseButton.LeftButton,
    )

    assert not dialog.ui.advanced_widget.isHidden()
    assert dialog.ui.advanced_toggleButton.text() == "收起高级设置"


def test_save_button_accepts_dialog(qtbot) -> None:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    assert dialog.ui.save_pushButton.text() == "保存"

    qtbot.mouseClick(
        dialog.ui.save_pushButton,
        Qt.MouseButton.LeftButton,
    )

    assert dialog.result() == QDialog.DialogCode.Accepted


def test_cancel_button_rejects_dialog(qtbot) -> None:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    qtbot.mouseClick(
        dialog.ui.cancel_pushButton,
        Qt.MouseButton.LeftButton,
    )

    assert dialog.result() == QDialog.DialogCode.Rejected


def test_visibility_button_toggles_api_key_echo_mode(qtbot) -> None:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    assert (
        dialog.ui.api_key_lineEdit.echoMode()
        is dialog.ui.api_key_lineEdit.EchoMode.Password
    )

    qtbot.mouseClick(
        dialog.ui.visibility_pushButton,
        Qt.MouseButton.LeftButton,
    )

    assert (
        dialog.ui.api_key_lineEdit.echoMode()
        is dialog.ui.api_key_lineEdit.EchoMode.Normal
    )
    assert dialog.ui.visibility_pushButton.toolTip() == "隐藏 API Key"

    qtbot.mouseClick(
        dialog.ui.visibility_pushButton,
        Qt.MouseButton.LeftButton,
    )

    assert (
        dialog.ui.api_key_lineEdit.echoMode()
        is dialog.ui.api_key_lineEdit.EchoMode.Password
    )


def test_connection_test_uses_current_configuration(qtbot) -> None:
    tester = StubConnectionTester()
    dialog = SettingsDialog(connection_tester=tester)
    qtbot.addWidget(dialog)

    dialog.ui.api_key_lineEdit.setText("test-key")
    qtbot.mouseClick(
        dialog.ui.test_pushButton,
        Qt.MouseButton.LeftButton,
    )

    assert len(tester.configs) == 1
    assert tester.configs[0].provider_id == "deepseek"
    assert not dialog.ui.test_pushButton.isEnabled()

    tester.succeeded.emit(["deepseek-chat", "deepseek-reasoner"])

    assert dialog.ui.test_pushButton.isEnabled()
    assert dialog.ui.refresh_models_pushButton.isEnabled()
    assert dialog.ui.status_label.text() == "● 连接成功"
    assert "#15803D" in dialog.ui.status_label.styleSheet()


def test_refresh_models_updates_dropdown_and_inline_status(qtbot) -> None:
    tester = StubConnectionTester()
    dialog = SettingsDialog(connection_tester=tester)
    qtbot.addWidget(dialog)

    qtbot.mouseClick(
        dialog.ui.refresh_models_pushButton,
        Qt.MouseButton.LeftButton,
    )

    assert len(tester.configs) == 1
    assert not dialog.ui.refresh_models_pushButton.isEnabled()

    tester.succeeded.emit(["deepseek-chat", "deepseek-reasoner"])

    models = [
        dialog.ui.model_comboBox.itemText(index)
        for index in range(dialog.ui.model_comboBox.count())
    ]
    assert "deepseek-chat" in models
    assert "deepseek-reasoner" in models
    assert dialog.ui.status_label.text() == "● 已刷新 2 个"


def test_connection_failure_shows_inline_error_status(qtbot) -> None:
    tester = StubConnectionTester()
    dialog = SettingsDialog(connection_tester=tester)
    qtbot.addWidget(dialog)

    qtbot.mouseClick(
        dialog.ui.test_pushButton,
        Qt.MouseButton.LeftButton,
    )
    tester.failed.emit("API Key 无效")

    assert dialog.ui.status_label.text() == "● 连接失败"
    assert dialog.ui.status_label.toolTip() == "API Key 无效"
    assert "#B91C1C" in dialog.ui.status_label.styleSheet()


def test_provider_selection_loads_separate_configuration(qtbot) -> None:
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    custom_index = dialog.ui.provider_comboBox.findData(
        "openai-compatible"
    )
    dialog.ui.provider_comboBox.setCurrentIndex(custom_index)

    assert dialog.current_provider_id() == "openai-compatible"
    assert dialog.ui.base_url_lineEdit.text() == "http://localhost:11434/v1"
    assert "可选" in dialog.ui.api_key_hint_label.text()


def test_settings_dialog_loads_and_returns_hotkey(qtbot) -> None:
    dialog = SettingsDialog(
        initial_hotkey=Hotkey(key="Y", ctrl=True, alt=True)
    )
    qtbot.addWidget(dialog)

    assert dialog.hotkey() == Hotkey(
        key="Y",
        ctrl=True,
        alt=True,
    )
