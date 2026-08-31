import sqlite3
import sys
from collections.abc import Callable
from pathlib import Path


if __package__ in {None, ""} and not getattr(sys, "frozen", False):
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

try:
    from app.version import __version__
except ModuleNotFoundError:
    # 兼容 `python app/main.py` 的直接启动方式。
    from version import __version__
from platforms.global_hotkey import GlobalHotkey
from platforms.models import (
    Hotkey,
    default_hotkey_for_platform,
    hotkey_to_text,
)
from platforms.text_capture import TextCapture
from history.repository import HistoryRepository
from providers.connection import ProviderConnectionTester
from providers.registry import create_provider
from settings.store import SettingsStore
from translation.manager import TranslationManager
from ui.main_window import MainWindow
from ui.system_tray import SystemTrayController


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


def main(argv: list[str] | None = None) -> int:
    application_args = list(sys.argv if argv is None else argv)
    smoke_test = "--smoke-test" in application_args
    application_args = [
        argument
        for argument in application_args
        if argument != "--smoke-test"
    ]

    app = QApplication(application_args)
    app.setOrganizationName("TradeTranslator")
    app.setOrganizationDomain("trade-translator.app")
    app.setApplicationName("Trade Translator")
    app.setApplicationDisplayName("Trade Translator")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(":/app/icons/languages.svg"))

    settings_store = SettingsStore()

    config = settings_store.load_active_config()
    provider = create_provider(config)
    manager = TranslationManager(provider)
    connection_tester = ProviderConnectionTester()
    try:
        history_repository = HistoryRepository(
            ":memory:" if smoke_test else None
        )
    except (OSError, sqlite3.Error):
        # 历史数据库不可用时，核心翻译功能仍然可以运行。
        history_repository = None
    window = MainWindow(
        translation_manager=manager,
        settings_store=settings_store,
        connection_tester=connection_tester,
        history_repository=history_repository,
        )

    # 先停止翻译和延迟任务，再关闭历史数据库。
    app.aboutToQuit.connect(window.prepare_to_quit)
    if history_repository is not None:
        app.aboutToQuit.connect(history_repository.close)

    window.provider_config_changed.connect(
        lambda new_config: manager.set_provider(
            create_provider(new_config)
        )
    )

    # 冒烟测试只验证打包后的应用可以创建窗口并正常退出。
    if not smoke_test:
        configure_global_hotkey(window, settings_store)
        window._system_tray = SystemTrayController(app, window)

    window.show()
    if smoke_test:
        QTimer.singleShot(500, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
