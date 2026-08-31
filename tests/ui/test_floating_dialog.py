from PySide6.QtCore import Qt

from providers.base import TranslationProvider
from translation.manager import TranslationManager
from translation.models import TranslationRequest
from ui.floating_dialog import FloatingTranslationDialog


class ControlledProvider(TranslationProvider):
    def __init__(self) -> None:
        super().__init__()
        self.request: TranslationRequest | None = None

    def translate(self, request: TranslationRequest) -> None:
        self.request = request
        self.started.emit(request.request_id)

    def cancel(self, request_id: str) -> None:
        self.cancelled.emit(request_id)


def test_floating_dialog_streams_only_its_translation(qtbot) -> None:
    provider = ControlledProvider()
    manager = TranslationManager(provider)
    dialog = FloatingTranslationDialog(manager)
    qtbot.addWidget(dialog)

    dialog.begin_translation("Hello", "zh-CN")
    request_id = manager.translate("Hello", "zh-CN")

    assert dialog.isVisible()
    assert dialog.ui.source_text_edit.toPlainText() == "Hello"
    assert dialog.current_target_language() == "zh-CN"
    assert not dialog.ui.copy_translation_push_button.isEnabled()

    provider.chunk_received.emit(request_id, "你")
    provider.chunk_received.emit(request_id, "好")
    provider.completed.emit(request_id)

    assert dialog.ui.translation_text_edit.toPlainText() == "你好"
    assert dialog.ui.copy_translation_push_button.isEnabled()


def test_floating_dialog_target_language_change_is_emitted(qtbot) -> None:
    provider = ControlledProvider()
    dialog = FloatingTranslationDialog(TranslationManager(provider))
    qtbot.addWidget(dialog)
    languages: list[str] = []
    dialog.target_language_changed.connect(languages.append)

    dialog.ui.target_language_combo_box.setCurrentIndex(1)

    assert languages == ["en"]


def test_manual_open_preserves_an_in_progress_translation(qtbot) -> None:
    provider = ControlledProvider()
    manager = TranslationManager(provider)
    dialog = FloatingTranslationDialog(manager)
    qtbot.addWidget(dialog)
    dialog.begin_translation("Hello", "zh-CN")
    request_id = manager.translate("Hello", "zh-CN")

    dialog.open_window()
    provider.chunk_received.emit(request_id, "你好")
    provider.completed.emit(request_id)

    assert dialog.ui.translation_text_edit.toPlainText() == "你好"
    assert dialog.ui.copy_translation_push_button.isEnabled()


def test_manual_open_restores_a_minimized_dialog(qtbot, monkeypatch) -> None:
    provider = ControlledProvider()
    dialog = FloatingTranslationDialog(TranslationManager(provider))
    qtbot.addWidget(dialog)
    activations = []
    monkeypatch.setattr(dialog, "activateWindow", lambda: activations.append(True))
    dialog.showMinimized()

    dialog.open_window()

    assert dialog.isVisible()
    assert not dialog.isMinimized()
    assert activations == [True]
    assert provider.request is None


def test_editing_source_requests_debounced_translation(qtbot) -> None:
    provider = ControlledProvider()
    manager = TranslationManager(provider)
    dialog = FloatingTranslationDialog(manager)
    qtbot.addWidget(dialog)
    dialog.translation_requested.connect(manager.translate)

    dialog.ui.source_text_edit.setPlainText("First draft")
    qtbot.wait(400)
    dialog.ui.source_text_edit.setPlainText("Final text")
    qtbot.wait(500)

    assert provider.request is None

    qtbot.waitUntil(lambda: provider.request is not None, timeout=700)
    assert provider.request is not None
    assert provider.request.text == "Final text"
    assert provider.request.target_language == "zh-CN"


def test_macos_floating_dialog_remains_visible_when_app_is_inactive(
    qtbot,
    monkeypatch,
) -> None:
    import ui.floating_dialog as floating_dialog_module

    monkeypatch.setattr(floating_dialog_module.sys, "platform", "darwin")
    provider = ControlledProvider()
    dialog = FloatingTranslationDialog(TranslationManager(provider))
    qtbot.addWidget(dialog)

    assert dialog.windowFlags() & Qt.WindowType.Tool
    assert dialog.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
    assert dialog.testAttribute(
        Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow
    )
    assert dialog.testAttribute(
        Qt.WidgetAttribute.WA_ShowWithoutActivating
    )


def test_floating_dialog_shows_capture_error_without_translation(qtbot) -> None:
    provider = ControlledProvider()
    dialog = FloatingTranslationDialog(TranslationManager(provider))
    qtbot.addWidget(dialog)

    dialog.show_capture_error("未读取到所选文字")

    assert dialog.isVisible()
    assert dialog.ui.translation_text_edit.toPlainText() == "未读取到所选文字"
    assert not dialog.ui.copy_translation_push_button.isEnabled()
