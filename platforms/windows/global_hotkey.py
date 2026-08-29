import ctypes
import sys
from ctypes import wintypes

from PySide6.QtCore import (
    QAbstractNativeEventFilter,
    QCoreApplication,
    QObject,
)

from platforms.global_hotkey import GlobalHotkey
from platforms.models import Hotkey, validate_hotkey


WM_HOTKEY = 0x0312

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

HOTKEY_ID = 1


def load_user32():
    """windows user32.dll"""
    if not sys.platform == "win32":
        raise OSError("WindowsGlobalHotkey 只能在 Windows 上使用")

    user32 = ctypes.WinDLL(
        "user32",
        use_last_error=True,
    )

    user32.RegisterHotKey.argtypes = [
        wintypes.HWND,
        ctypes.c_int,
        wintypes.UINT,
        wintypes.UINT,
    ]
    user32.RegisterHotKey.restype = wintypes.BOOL

    user32.UnregisterHotKey.argtypes = [
        wintypes.HWND,
        ctypes.c_int,
    ]
    user32.UnregisterHotKey.restype = wintypes.BOOL

    return user32


class WindowsHotkeyEventFilter(QAbstractNativeEventFilter):
    def __init__(self, callback) -> None:
        super().__init__()
        self._callback = callback

    def nativeEventFilter(self, event_type, message):
        """处理发送给窗口或当前线程的 Win32 消息。"""
        if bytes(event_type) not in {
            b"windows_generic_MSG",
            b"windows_dispatcher_MSG",
        }:
            return False

        message_address = int(message)
        native_message = wintypes.MSG.from_address(
            message_address
        )

        if (
            native_message.message == WM_HOTKEY
            and native_message.wParam == HOTKEY_ID
        ):
            self._callback()

        return False


class WindowsGlobalHotkey(GlobalHotkey):
    def __init__(
        self,
        user32=None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        application = QCoreApplication.instance()
        if application is None:
            raise RuntimeError(
                "创建 WindowsGlobalHotkey 前必须先创建 QApplication"
            )

        self._application = application
        self._user32 = user32 or load_user32()
        self._window_handle = self._resolve_window_handle(parent)
        self._registered = False
        self._registered_hotkey: Hotkey | None = None

        self._event_filter = WindowsHotkeyEventFilter(
            self.activated.emit
        )
        self._application.installNativeEventFilter(
            self._event_filter
        )
        self._application.aboutToQuit.connect(
            self.close
        )

    def register_hotkey(self, hotkey: Hotkey) -> bool:
        try:
            hotkey = validate_hotkey(hotkey)
            modifiers = self._build_modifiers(hotkey)
            virtual_key = self._virtual_key(hotkey.key)
        except ValueError as error:
            self.registration_failed.emit(str(error))
            return False

        previous_hotkey = self._registered_hotkey
        self.unregister_hotkey()

        registered = bool(
            self._user32.RegisterHotKey(
                self._window_handle,
                HOTKEY_ID,
                modifiers,
                virtual_key,
            )
        )

        if not registered:
            error_code = ctypes.get_last_error()
            if previous_hotkey is not None:
                restored = bool(
                    self._user32.RegisterHotKey(
                        self._window_handle,
                        HOTKEY_ID,
                        self._build_modifiers(previous_hotkey),
                        self._virtual_key(previous_hotkey.key),
                    )
                )
                if restored:
                    self._registered = True
                    self._registered_hotkey = previous_hotkey
            self.registration_failed.emit(
                f"快捷键注册失败，可能已被占用（错误码 {error_code}）"
            )
            return False

        self._registered = True
        self._registered_hotkey = hotkey
        return True

    def unregister_hotkey(self) -> None:
        if not self._registered:
            return

        self._user32.UnregisterHotKey(
            self._window_handle,
            HOTKEY_ID,
        )
        self._registered = False
        self._registered_hotkey = None

    def close(self) -> None:
        """释放系统快捷键和 Qt 原生事件过滤器。"""
        self.unregister_hotkey()
        if self._event_filter is None:
            return
        self._application.removeNativeEventFilter(
            self._event_filter
        )
        self._event_filter = None

    @staticmethod
    def _build_modifiers(hotkey: Hotkey) -> int:
        modifiers = MOD_NOREPEAT

        if hotkey.ctrl:
            modifiers |= MOD_CONTROL
        if hotkey.shift:
            modifiers |= MOD_SHIFT
        if hotkey.alt:
            modifiers |= MOD_ALT
        if hotkey.meta:
            modifiers |= MOD_WIN

        return modifiers

    @staticmethod
    def _virtual_key(key: str) -> int:
        normalized_key = key.strip().upper()

        if (
            len(normalized_key) != 1
            or not normalized_key.isascii()
            or not normalized_key.isalnum()
        ):
            raise ValueError(
                "目前快捷键只支持单个英文字母或数字"
            )

        return ord(normalized_key)

    @staticmethod
    def _resolve_window_handle(parent: QObject | None) -> int | None:
        """优先把热键绑定到主窗口，避免依赖 Qt 转发线程消息。"""
        if parent is None or not hasattr(parent, "winId"):
            return None

        return int(parent.winId())
