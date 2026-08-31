import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QEvent, QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from app.main import configure_global_hotkey
from history.repository import HistoryRepository
from platforms.global_hotkey import GlobalHotkey
from platforms.models import DEFAULT_WINDOWS_HOTKEY
from platforms.text_capture import TextCapture
from providers.base import TranslationProvider
from providers.config import ProviderConfig
from translation.manager import TranslationManager
from ui.main_window import MainWindow
import ui.system_tray as tray_module


class FakeTray(QObject):
    """只模拟托盘外壳，窗口和事件循环仍使用真实 Qt。"""

    activated = Signal(object)
    messageClicked = Signal()
    ActivationReason = QSystemTrayIcon.ActivationReason
    MessageIcon = QSystemTrayIcon.MessageIcon
    available = True

    def __init__(self, parent=None):
        super().__init__(parent)
        self.visible = False
        self.messages = []

    @classmethod
    def isSystemTrayAvailable(cls):
        return cls.available

    @staticmethod
    def supportsMessages():
        return True

    def setIcon(self, icon):
        self.icon = icon

    def setToolTip(self, text):
        self.tooltip = text

    def setContextMenu(self, menu):
        self.menu = menu

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def isVisible(self):
        return self.visible

    def showMessage(self, *args):
        self.messages.append(args)


class MemorySettings:
    def load_active_config(self):
        return ProviderConfig("openai-compatible", "https://example.test", "test")

    def load_default_target_language(self):
        return "zh-CN"

    def load_hotkey(self):
        return DEFAULT_WINDOWS_HOTKEY

    def save_hotkey(self, hotkey):
        self.hotkey = hotkey


class ControlledProvider(TranslationProvider):
    def __init__(self):
        super().__init__()
        self.requests = []
        self.cancellations = []

    def translate(self, request):
        self.requests.append(request)
        self.started.emit(request.request_id)

    def cancel(self, request_id):
        self.cancellations.append(request_id)
        self.cancelled.emit(request_id)


class FakeHotkey(GlobalHotkey):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.registered = False
        QApplication.instance().aboutToQuit.connect(self.close)

    def register_hotkey(self, hotkey):
        self.registered = True
        return True

    def close(self):
        self.registered = False


class FakeCapture(TextCapture):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.closed = False

    def capture_selected_text(self):
        self.capture_started.emit()
        self.text_captured.emit("Selected text")

    def close(self):
        self.closed = True


@pytest.fixture
def create_tray_window(qapp, qtbot, monkeypatch):
    initial_quit_policy = qapp.quitOnLastWindowClosed()
    monkeypatch.setattr(tray_module, "QSystemTrayIcon", FakeTray)
    monkeypatch.setattr(FakeTray, "available", True)
    windows = []

    def create(available=True):
        FakeTray.available = available
        qapp.setQuitOnLastWindowClosed(True)
        provider = ControlledProvider()
        window = MainWindow(TranslationManager(provider), MemorySettings())
        qtbot.addWidget(window)
        qtbot.addWidget(window._floating_dialog)
        controller = tray_module.SystemTrayController(qapp, window)
        windows.append((window, controller))
        window.show()
        return window, provider, controller

    yield create

    for window, controller in reversed(windows):
        controller.close()
        window.prepare_to_quit()
    qapp.setQuitOnLastWindowClosed(initial_quit_policy)


def test_close_keeps_window_handle_content_and_live_request(
    create_tray_window, qapp,
):
    window, provider, controller = create_tray_window()
    native_handle = window.winId()
    window.on_selected_text_captured("Hello")
    request_id = provider.requests[-1].request_id
    provider.chunk_received.emit(request_id, "你")

    assert not window.close()

    assert not window.isVisible()
    assert not window._floating_dialog.isVisible()
    assert window.winId() == native_handle
    assert window.ui.origin_plainTextEdit.toPlainText() == "Hello"
    assert not provider.cancellations
    assert not qapp.quitOnLastWindowClosed()
    assert controller.tray_icon.isVisible()
    provider.chunk_received.emit(request_id, "好")
    provider.completed.emit(request_id)
    assert window.ui.translation_plainTextEdit.toPlainText() == "你好"


def test_restore_menu_preserves_translation_and_notice_is_only_shown_once(
    create_tray_window,
):
    window, _provider, controller = create_tray_window()
    window.ui.translation_plainTextEdit.setPlainText("保留译文")
    window.close()

    controller.show_action.trigger()

    assert window.isVisible()
    assert window.ui.translation_plainTextEdit.toPlainText() == "保留译文"
    window.close()
    assert len(controller.tray_icon.messages) == 1
    assert controller.show_action.text() == "显示主窗口"
    assert controller.quit_action.text() == "退出"
    assert not controller.tray_icon.icon.pixmap(22, 22).isNull()


@pytest.mark.parametrize("platform", ["win32", "darwin"])
def test_tray_opens_floating_window_without_showing_main_window(
    create_tray_window, monkeypatch, platform,
):
    monkeypatch.setattr(tray_module, "sys", SimpleNamespace(platform=platform))
    window, provider, controller = create_tray_window()
    floating = window._floating_dialog
    window.close()

    controller.floating_action.trigger()

    assert controller.floating_action.text() == "打开悬浮窗"
    assert not window.isVisible()
    assert floating.isVisible()
    assert floating.focusWidget() is floating.ui.source_text_edit
    assert not provider.requests

    floating.close()
    controller.floating_action.trigger()

    assert window._floating_dialog is floating
    assert floating.isVisible()
    assert not window.isVisible()
    assert not provider.requests


def test_tray_open_preserves_floating_content_language_and_live_translation(
    create_tray_window,
):
    window, provider, controller = create_tray_window()
    floating = window._floating_dialog
    window._start_floating_translation("Hello", "en")
    request_id = provider.requests[-1].request_id
    provider.chunk_received.emit(request_id, "Existing")
    window.close()

    controller.floating_action.trigger()
    controller.floating_action.trigger()

    assert window._floating_dialog is floating
    assert floating.ui.source_text_edit.toPlainText() == "Hello"
    assert floating.ui.translation_text_edit.toPlainText() == "Existing"
    assert floating.current_target_language() == "en"
    assert len(provider.requests) == 1
    assert not provider.cancellations
    provider.chunk_received.emit(request_id, " translation")
    provider.completed.emit(request_id)
    assert floating.ui.translation_text_edit.toPlainText() == "Existing translation"


def test_floating_window_opened_from_tray_can_translate_typed_text(
    create_tray_window, qtbot,
):
    window, provider, controller = create_tray_window()
    window.close()
    controller.floating_action.trigger()
    floating = window._floating_dialog

    floating.ui.source_text_edit.setPlainText("Hello from tray")

    qtbot.waitUntil(lambda: len(provider.requests) == 1, timeout=2000)
    request = provider.requests[0]
    assert request.text == "Hello from tray"
    assert not window.isVisible()
    provider.chunk_received.emit(request.request_id, "托盘翻译")
    provider.completed.emit(request.request_id)
    assert floating.ui.translation_text_edit.toPlainText() == "托盘翻译"


@pytest.mark.parametrize("reason", [
    FakeTray.ActivationReason.Trigger,
    FakeTray.ActivationReason.DoubleClick,
])
def test_windows_tray_click_restores_minimized_window(
    create_tray_window, monkeypatch, reason,
):
    monkeypatch.setattr(tray_module, "sys", SimpleNamespace(platform="win32"))
    window, _provider, controller = create_tray_window()
    window.showMinimized()
    window.close()

    controller.tray_icon.activated.emit(reason)

    assert window.isVisible()
    assert not window.isMinimized()


def test_macos_tray_click_leaves_restoration_to_menu(
    create_tray_window, monkeypatch,
):
    monkeypatch.setattr(tray_module, "sys", SimpleNamespace(platform="darwin"))
    window, _provider, controller = create_tray_window()
    window.close()

    controller.tray_icon.activated.emit(FakeTray.ActivationReason.Trigger)

    assert not window.isVisible()
    assert controller.tray_icon.icon.isMask()
    controller.show_action.trigger()
    assert window.isVisible()


def test_background_notification_can_restore_window(create_tray_window):
    window, _provider, controller = create_tray_window()
    window.close()

    controller.tray_icon.messageClicked.emit()

    assert window.isVisible()


def test_no_tray_keeps_normal_close_behavior(create_tray_window, qapp):
    window, _provider, controller = create_tray_window(available=False)

    assert qapp.quitOnLastWindowClosed()
    assert controller.tray_icon is None
    assert "系统托盘不可用" in window.statusBar().currentMessage()
    assert window.close()


def test_tray_disappearance_falls_back_to_normal_exit(create_tray_window, qapp):
    window, _provider, _controller = create_tray_window()
    FakeTray.available = False

    assert window.close()
    assert qapp.quitOnLastWindowClosed()


def test_explicit_quit_does_not_get_intercepted_as_hide(
    create_tray_window, qapp, monkeypatch,
):
    window, _provider, controller = create_tray_window()
    quit_mock = Mock()
    monkeypatch.setattr(qapp, "quit", quit_mock)

    controller.quit_action.trigger()

    quit_mock.assert_called_once_with()
    assert window.close()
    assert not controller.tray_icon.messages


def test_system_quit_event_allows_window_to_close(create_tray_window, qapp):
    window, _provider, controller = create_tray_window()

    assert not controller.eventFilter(qapp, QEvent(QEvent.Type.Quit))
    assert window.close()
    assert not controller.tray_icon.messages


def test_close_during_session_shutdown_is_not_hidden(
    create_tray_window, qapp, monkeypatch,
):
    window, _provider, controller = create_tray_window()
    monkeypatch.setattr(qapp, "isSavingSession", lambda: True)

    assert window.close()
    assert not controller.tray_icon.messages


@pytest.mark.skipif(
    sys.platform not in {"win32", "darwin"}, reason="桌面平台组装",
)
def test_global_hotkey_can_open_floating_translation_while_main_is_hidden(
    create_tray_window,
):
    window, provider, _controller = create_tray_window()
    hotkey = configure_global_hotkey(
        window, MemorySettings(), FakeHotkey, FakeCapture,
    )
    window.close()

    assert hotkey.registered
    hotkey.activated.emit()

    assert not window.isVisible()
    assert window._floating_dialog.isVisible()
    assert provider.requests[-1].text == "Selected text"
    assert not window._text_capture.closed
    window._floating_dialog.close()
    assert hotkey.registered
    hotkey.activated.emit()
    assert window._floating_dialog.isVisible()
    assert len(provider.requests) == 2


def test_prepare_to_quit_stops_pending_timers_and_cancels_once(create_tray_window):
    window, provider, _controller = create_tray_window()
    window.ui.origin_plainTextEdit.setPlainText("Main pending")
    window._floating_dialog.ui.source_text_edit.setPlainText("Floating pending")
    window.copy_button_timer.start(1500)
    window._translation_manager.translate("In flight", "zh-CN")

    assert window.auto_translate_timer.isActive()
    assert window._floating_dialog._source_change_timer.isActive()

    window.prepare_to_quit()
    window.prepare_to_quit()

    assert not window.auto_translate_timer.isActive()
    assert not window.copy_button_timer.isActive()
    assert not window._floating_dialog._source_change_timer.isActive()
    assert not window._floating_dialog.isVisible()
    assert len(provider.cancellations) == 1


def test_controller_cleanup_is_idempotent_and_restores_quit_policy(
    create_tray_window, qapp,
):
    window, _provider, controller = create_tray_window()

    controller.close()
    controller.close()

    assert qapp.quitOnLastWindowClosed()
    assert not controller.tray_icon.isVisible()
    assert window.close()


@pytest.mark.parametrize("exit_mode", ["tray_quit", "system_quit", "no_tray"])
def test_real_event_loop_lifecycle_exits_in_subprocess(exit_mode):
    # 单独进程才能验证 QApplication.quit()，不会退出 pytest 自身的 Qt 应用。
    result = subprocess.run(
        [
            sys.executable, "-c",
            "import runpy; runpy.run_path('tests/ui/test_system_tray.py', "
            "run_name='__main__')",
            exit_mode,
        ],
        cwd=Path(__file__).resolve().parents[2],
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "lifecycle-ok" in result.stdout


def _run_lifecycle_probe(exit_mode, *, native_tray=False):
    application = QApplication([])
    if native_tray:
        assert QSystemTrayIcon.isSystemTrayAvailable()
    else:
        tray_module.QSystemTrayIcon = FakeTray
        FakeTray.available = exit_mode != "no_tray"
    settings = MemorySettings()
    provider = ControlledProvider()
    repository = HistoryRepository(":memory:")
    window = MainWindow(
        TranslationManager(provider), settings, history_repository=repository,
    )
    application.aboutToQuit.connect(window.prepare_to_quit)
    application.aboutToQuit.connect(repository.close)
    hotkey = configure_global_hotkey(window, settings, FakeHotkey, FakeCapture)
    controller = tray_module.SystemTrayController(application, window)
    # 手动原生托盘检查不弹出通知，避免打扰当前桌面。
    if native_tray:
        controller._background_notice_shown = True
    window.show()
    checkpoints = []

    def close_window():
        window._translation_manager.translate("In flight", "zh-CN")
        window.close()
        if exit_mode == "no_tray":
            checkpoints.append("closed")
        else:
            QTimer.singleShot(50, finish_from_background)

    def finish_from_background():
        if window.isVisible() or provider.cancellations:
            application.exit(2)
            return
        checkpoints.append("background-alive")
        if exit_mode == "tray_quit":
            controller.quit_action.trigger()
        else:
            # 先恢复窗口，再走系统 Quit，验证关闭可见窗口不会被托盘拦截。
            controller.show_action.trigger()
            application.quit()

    QTimer.singleShot(0, close_window)
    QTimer.singleShot(3000, lambda: application.exit(3))
    assert application.exec() == 0
    assert checkpoints == (
        ["closed"] if exit_mode == "no_tray" else ["background-alive"]
    )
    assert window._prepared_to_quit
    assert len(provider.cancellations) == 1
    if hotkey is not None:
        assert not hotkey.registered
        assert window._text_capture.closed
    assert controller.tray_icon is None or not controller.tray_icon.isVisible()
    # 确认退出信号真的关闭了 SQLite，而非只是隐藏窗口。
    with pytest.raises(sqlite3.ProgrammingError):
        repository.list_recent()
    print("lifecycle-ok")


if __name__ == "__main__":
    mode = sys.argv[1]
    _run_lifecycle_probe(
        "tray_quit" if mode == "native_tray" else mode,
        native_tray=mode == "native_tray",
    )
