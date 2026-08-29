import sys
from collections.abc import Callable

from PySide6.QtWidgets import QApplication

from platforms.global_hotkey import GlobalHotkey
from platforms.models import (
    Hotkey,
    default_hotkey_for_platform,
    hotkey_to_text,
)
from platforms.text_capture import TextCapture
from providers.connection import ProviderConnectionTester
from providers.registry import create_provider
from settings.store import SettingsStore
from translation.manager import TranslationManager
from ui.main_window import MainWindow


def configure_global_hotkey(
    window: MainWindow,
    settings_store: SettingsStore | None = None,
    factory: Callable[..., GlobalHotkey] | None = None,
    text_capture_factory: Callable[..., TextCapture] | None = None,
) -> GlobalHotkey | None:
    """连接当前桌面平台的全局快捷键与跨应用取词。"""
    if sys.platform not in {"win32", "darwin"}:
        return None

    if sys.platform == "win32":
        if factory is None:
            from platforms.windows.global_hotkey import WindowsGlobalHotkey

            factory = WindowsGlobalHotkey
        if text_capture_factory is None:
            from platforms.windows.text_capture import (
                WindowsClipboardTextCapture,
            )

            text_capture_factory = WindowsClipboardTextCapture
    else:
        if factory is None:
            from platforms.macos.global_hotkey import MacOSGlobalHotkey

            factory = MacOSGlobalHotkey
        if text_capture_factory is None:
            from platforms.macos.text_capture import (
                MacOSClipboardTextCapture,
            )

            text_capture_factory = MacOSClipboardTextCapture

    global_hotkey = factory(parent=window)
    text_capture = text_capture_factory(parent=window)
    global_hotkey.activated.connect(
        window.on_global_hotkey_activated
    )
    global_hotkey.activated.connect(
        text_capture.capture_selected_text
    )
    global_hotkey.registration_failed.connect(
        window.on_global_hotkey_registration_failed
    )
    text_capture.capture_started.connect(
        window.on_text_capture_started
    )
    text_capture.text_captured.connect(
        window.on_selected_text_captured
    )
    text_capture.capture_failed.connect(
        window.on_text_capture_failed
    )
    QApplication.instance().aboutToQuit.connect(text_capture.close)

    # 保持 Python 包装对象存活，窗口销毁时 Qt 会释放它们。
    window._global_hotkey = global_hotkey
    window._text_capture = text_capture

    def apply_hotkey(hotkey: Hotkey) -> None:
        if not global_hotkey.register_hotkey(hotkey):
            return
        if settings_store is not None:
            settings_store.save_hotkey(hotkey)
        window.on_global_hotkey_registered(hotkey_to_text(hotkey))

    window.hotkey_change_requested.connect(apply_hotkey)
    initial_hotkey = (
        settings_store.load_hotkey()
        if settings_store is not None
        else default_hotkey_for_platform()
    )
    apply_hotkey(initial_hotkey)

    return global_hotkey


def main() -> int:
    app = QApplication([])
    app.setOrganizationName("TradeTranslator")
    app.setOrganizationDomain("trade-translator.app")
    app.setApplicationName("Trade Translator")

    settings_store = SettingsStore()

    config = settings_store.load_active_config()
    provider = create_provider(config)
    manager = TranslationManager(provider)
    connection_tester = ProviderConnectionTester()

    window = MainWindow(
        translation_manager=manager,
        settings_store=settings_store,
        connection_tester=connection_tester,
        )

    window.provider_config_changed.connect(
        lambda new_config: manager.set_provider(
            create_provider(new_config)
        )
    )

    # 由窗口父子关系和 aboutToQuit 信号共同保证退出时释放快捷键。
    global_hotkey = configure_global_hotkey(window, settings_store)

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
