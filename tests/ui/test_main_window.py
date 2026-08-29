from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from providers.base import TranslationProvider
from providers.config import ProviderConfig
from platforms.global_hotkey import GlobalHotkey
from platforms.models import (
    DEFAULT_MACOS_HOTKEY,
    DEFAULT_WINDOWS_HOTKEY,
    Hotkey,
)
from platforms.text_capture import TextCapture
from translation.manager import TranslationManager
from translation.models import TranslationRequest
import ui.main_window as main_window_module
from ui.main_window import MainWindow


class RecordingTranslationProvider(TranslationProvider):
    """记录窗口提交的请求，并立即返回模拟结果。"""

    def __init__(self) -> None:
        super().__init__()
        self.requests: list[TranslationRequest] = []

    def translate(self, request: TranslationRequest) -> None:
        self.requests.append(request)
        self.started.emit(request.request_id)
        self.chunk_received.emit(request.request_id, "模拟译文")
        self.completed.emit(request.request_id)

    def cancel(self, request_id: str) -> None:
        self.cancelled.emit(request_id)


class ControlledTranslationProvider(TranslationProvider):
    """由测试控制何时返回第一个流式片段。"""

    def __init__(self) -> None:
        super().__init__()
        self.request: TranslationRequest | None = None

    def translate(self, request: TranslationRequest) -> None:
        self.request = request
        self.started.emit(request.request_id)

    def cancel(self, request_id: str) -> None:
        self.cancelled.emit(request_id)


class RecordingSettingsStore:
    """避免 UI 测试读写真实的系统凭据管理器。"""

    def __init__(self, api_key: str = "") -> None:
        self.stored_api_key = api_key

    def save_api_key(self, api_key: str) -> None:
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("API Key 不能为空")
        self.stored_api_key = api_key

    def load_api_key(self) -> str:
        return self.stored_api_key

    def load_active_config(self) -> ProviderConfig:
        return self.load_provider_config("deepseek")

    def load_provider_config(self, provider_id: str) -> ProviderConfig:
        return ProviderConfig(
            provider_id=provider_id,
            base_url="https://api.deepseek.com",
            model="deepseek-v4-flash",
            api_key=self.stored_api_key,
        )

    def save_provider_config(self, config: ProviderConfig) -> None:
        self.stored_api_key = config.api_key

    def load_hotkey(self) -> Hotkey:
        return getattr(self, "stored_hotkey", DEFAULT_WINDOWS_HOTKEY)

    def save_hotkey(self, hotkey: Hotkey) -> None:
        self.stored_hotkey = hotkey


def create_window(
    qtbot,
    settings_store: RecordingSettingsStore | None = None,
) -> tuple[MainWindow, RecordingTranslationProvider]:
    provider = RecordingTranslationProvider()
    manager = TranslationManager(provider)
    window = MainWindow(
        translation_manager=manager,
        settings_store=settings_store or RecordingSettingsStore(),
    )
    qtbot.addWidget(window)
    return window, provider


def test_copy_button_is_disabled_without_translation(qtbot) -> None:
    window, _provider = create_window(qtbot)

    assert not window.ui.copy_pushButton.isEnabled()


def test_auto_translation_submits_complete_text(qtbot) -> None:
    settings_store = RecordingSettingsStore()
    window, provider = create_window(qtbot, settings_store)

    window.ui.origin_plainTextEdit.setPlainText("Hello world")

    qtbot.waitUntil(lambda: len(provider.requests) == 1, timeout=1500)

    request = provider.requests[0]
    assert request.text == "Hello world"
    assert request.source_language == "auto"
    assert request.target_language == "zh-CN"
    assert window.ui.translation_plainTextEdit.toPlainText() == "模拟译文"


def test_auto_translation_is_debounced(qtbot) -> None:
    window, provider = create_window(qtbot)

    window.ui.origin_plainTextEdit.setPlainText("Hello")
    qtbot.wait(400)
    window.ui.origin_plainTextEdit.setPlainText("Hello world")
    qtbot.wait(500)

    assert provider.requests == []

    qtbot.waitUntil(lambda: len(provider.requests) == 1, timeout=700)
    assert provider.requests[0].text == "Hello world"


def test_changing_target_language_retranslates(qtbot) -> None:
    window, provider = create_window(qtbot)

    window.ui.origin_plainTextEdit.setPlainText("你好")
    qtbot.waitUntil(lambda: len(provider.requests) == 1, timeout=1500)

    window.ui.translation_comboBox.setCurrentIndex(1)
    qtbot.waitUntil(lambda: len(provider.requests) == 2, timeout=1500)

    assert provider.requests[-1].target_language == "en"


def test_copy_button_copies_translation(qtbot, qapp) -> None:
    window, _provider = create_window(qtbot)

    window.ui.translation_plainTextEdit.setPlainText("Copied text")
    qtbot.mouseClick(
        window.ui.copy_pushButton,
        Qt.MouseButton.LeftButton,
    )

    assert qapp.clipboard().text() == "Copied text"


def test_old_translation_remains_until_first_new_chunk(qtbot) -> None:
    provider = ControlledTranslationProvider()
    manager = TranslationManager(provider)
    window = MainWindow(
        translation_manager=manager,
        settings_store=RecordingSettingsStore(),
    )
    qtbot.addWidget(window)
    window.ui.translation_plainTextEdit.setPlainText("旧译文")

    request_id = manager.translate("New source", "zh-CN")

    assert window.ui.translation_plainTextEdit.toPlainText() == "旧译文"

    provider.chunk_received.emit(request_id, "新")

    assert window.ui.translation_plainTextEdit.toPlainText() == "新"


def test_windows_global_hotkey_is_registered_and_updates_status(
    qtbot,
) -> None:
    from app.main import configure_global_hotkey

    class RecordingGlobalHotkey(GlobalHotkey):
        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.registered_hotkey: Hotkey | None = None

        def register_hotkey(self, hotkey: Hotkey) -> bool:
            self.registered_hotkey = hotkey
            return True

        def unregister_hotkey(self) -> None:
            self.registered_hotkey = None

    class RecordingTextCapture(TextCapture):
        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.capture_count = 0

        def capture_selected_text(self) -> None:
            self.capture_count += 1
            self.capture_started.emit()

    settings_store = RecordingSettingsStore()
    window, provider = create_window(qtbot, settings_store)
    service = RecordingGlobalHotkey()
    text_capture = RecordingTextCapture()

    configured_service = configure_global_hotkey(
        window,
        settings_store=settings_store,
        factory=lambda parent: service,
        text_capture_factory=lambda parent: text_capture,
    )

    assert configured_service is service
    assert service.registered_hotkey == Hotkey(
        key="T",
        ctrl=True,
        shift=True,
    )
    assert "已启用" in window.statusBar().currentMessage()

    service.activated.emit()

    assert text_capture.capture_count == 1
    assert window.statusBar().currentMessage() == "正在读取所选文字…"

    text_capture.text_captured.emit("  Captured source  ")

    assert window.ui.origin_plainTextEdit.toPlainText() == "Captured source"
    assert provider.requests[-1].text == "Captured source"

    changed_hotkey = Hotkey(key="Y", ctrl=True, alt=True)
    window.hotkey_change_requested.emit(changed_hotkey)

    assert service.registered_hotkey == changed_hotkey
    assert settings_store.load_hotkey() == changed_hotkey


def test_global_hotkey_registration_failure_is_shown(qtbot) -> None:
    from app.main import configure_global_hotkey

    class FailingGlobalHotkey(GlobalHotkey):
        def register_hotkey(self, hotkey: Hotkey) -> bool:
            self.registration_failed.emit("快捷键已被其他程序占用")
            return False

        def unregister_hotkey(self) -> None:
            pass

    window, _provider = create_window(qtbot)

    class IdleTextCapture(TextCapture):
        def capture_selected_text(self) -> None:
            pass

    configure_global_hotkey(
        window,
        factory=lambda parent: FailingGlobalHotkey(parent),
        text_capture_factory=lambda parent: IdleTextCapture(parent),
    )

    assert window.statusBar().currentMessage() == "快捷键已被其他程序占用"


def test_macos_platform_uses_command_shortcut(qtbot, monkeypatch) -> None:
    import app.main as main_module

    class RecordingGlobalHotkey(GlobalHotkey):
        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.registered_hotkey = None

        def register_hotkey(self, hotkey) -> bool:
            self.registered_hotkey = hotkey
            return True

        def unregister_hotkey(self) -> None:
            pass

    class IdleTextCapture(TextCapture):
        def capture_selected_text(self) -> None:
            pass

    monkeypatch.setattr(main_module.sys, "platform", "darwin")
    window, _provider = create_window(qtbot)
    service = RecordingGlobalHotkey()

    main_module.configure_global_hotkey(
        window,
        factory=lambda parent: service,
        text_capture_factory=lambda parent: IdleTextCapture(parent),
    )

    assert service.registered_hotkey == DEFAULT_MACOS_HOTKEY


def test_accepted_settings_are_saved_and_applied(
    qtbot,
    monkeypatch,
) -> None:
    settings_store = RecordingSettingsStore("old-key")
    window, _provider = create_window(qtbot, settings_store)

    class AcceptedSettingsDialog:
        def __init__(self, _parent, **_kwargs) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def provider_config(self) -> ProviderConfig:
            return ProviderConfig(
                provider_id="deepseek",
                base_url="https://api.deepseek.com",
                model="deepseek-chat",
                api_key="  new-key  ",
            )

        def hotkey(self) -> Hotkey:
            return Hotkey(key="Y", ctrl=True, shift=True)

    monkeypatch.setattr(
        main_window_module,
        "SettingsDialog",
        AcceptedSettingsDialog,
    )

    changed_configs: list[ProviderConfig] = []
    window.provider_config_changed.connect(changed_configs.append)

    window.on_settings_clicked()

    assert settings_store.stored_api_key == "new-key"
    assert changed_configs[0].model == "deepseek-chat"
    assert changed_configs[0].api_key == "new-key"


def test_cancelled_settings_are_not_saved(
    qtbot,
    monkeypatch,
) -> None:
    settings_store = RecordingSettingsStore("old-key")
    window, _provider = create_window(qtbot, settings_store)

    class CancelledSettingsDialog:
        def __init__(self, _parent, **_kwargs) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Rejected

        def provider_config(self) -> ProviderConfig:
            raise AssertionError("取消后不应读取模型配置")

        def hotkey(self) -> Hotkey:
            raise AssertionError("取消后不应读取快捷键")

    monkeypatch.setattr(
        main_window_module,
        "SettingsDialog",
        CancelledSettingsDialog,
    )

    window.on_settings_clicked()

    assert settings_store.stored_api_key == "old-key"
