import threading
from collections.abc import Callable

from PySide6.QtCore import QCoreApplication, QObject

from platforms.global_hotkey import GlobalHotkey
from platforms.macos.quartz_api import (
    CG_EVENT_TAP_CALLBACK,
    K_CG_EVENT_FLAG_MASK_ALTERNATE,
    K_CG_EVENT_FLAG_MASK_COMMAND,
    K_CG_EVENT_FLAG_MASK_CONTROL,
    K_CG_EVENT_FLAG_MASK_SHIFT,
    K_CG_EVENT_KEY_DOWN,
    K_CG_EVENT_TAP_DISABLED_BY_TIMEOUT,
    K_CG_EVENT_TAP_DISABLED_BY_USER_INPUT,
    K_CG_KEYBOARD_EVENT_AUTOREPEAT,
    K_CG_KEYBOARD_EVENT_KEYCODE,
    K_CG_MODIFIER_MASK,
    MacOSQuartzApi,
)
from platforms.models import Hotkey, validate_hotkey


MACOS_KEY_CODES = {
    "A": 0,
    "S": 1,
    "D": 2,
    "F": 3,
    "H": 4,
    "G": 5,
    "Z": 6,
    "X": 7,
    "C": 8,
    "V": 9,
    "B": 11,
    "Q": 12,
    "W": 13,
    "E": 14,
    "R": 15,
    "Y": 16,
    "T": 17,
    "1": 18,
    "2": 19,
    "3": 20,
    "4": 21,
    "6": 22,
    "5": 23,
    "9": 25,
    "7": 26,
    "8": 28,
    "0": 29,
    "O": 31,
    "U": 32,
    "I": 34,
    "P": 35,
    "L": 37,
    "J": 38,
    "K": 40,
    "N": 45,
    "M": 46,
}


def hotkey_key_code(hotkey: Hotkey) -> int:
    hotkey = validate_hotkey(hotkey)
    return MACOS_KEY_CODES[hotkey.key]


def hotkey_modifier_flags(hotkey: Hotkey) -> int:
    hotkey = validate_hotkey(hotkey)
    flags = 0
    if hotkey.ctrl:
        flags |= K_CG_EVENT_FLAG_MASK_CONTROL
    if hotkey.shift:
        flags |= K_CG_EVENT_FLAG_MASK_SHIFT
    if hotkey.alt:
        flags |= K_CG_EVENT_FLAG_MASK_ALTERNATE
    if hotkey.meta:
        flags |= K_CG_EVENT_FLAG_MASK_COMMAND
    return flags


class QuartzHotkeyListener:
    """在独立 CFRunLoop 中监听一个 Quartz 全局快捷键。"""

    def __init__(
        self,
        hotkey: Hotkey,
        callback: Callable[[], None],
        api: MacOSQuartzApi | None = None,
    ) -> None:
        self._hotkey = validate_hotkey(hotkey)
        self._activation_callback = callback
        self._api = api or MacOSQuartzApi()
        self._ready = threading.Event()
        self._stop_requested = threading.Event()
        self._thread: threading.Thread | None = None
        self._run_loop: int | None = None
        self._event_tap: int | None = None
        self._event_callback = None
        self._start_error = ""

    @property
    def start_error(self) -> str:
        return self._start_error

    def start(self) -> bool:
        if not self._api.request_listen_event_access():
            self._start_error = "missing-permission"
            return False

        self._thread = threading.Thread(
            target=self._run,
            name="macOS-global-hotkey",
            daemon=True,
        )
        self._thread.start()
        if not self._ready.wait(timeout=2.0):
            self._start_error = "start-timeout"
            self.stop()
            return False
        return not self._start_error

    def stop(self) -> None:
        self._stop_requested.set()
        run_loop = self._run_loop
        if run_loop is not None:
            self._api.stop_run_loop(run_loop)
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=1.0)
        self._thread = None

    def _run(self) -> None:
        source = None
        try:
            self._event_callback = CG_EVENT_TAP_CALLBACK(
                self._handle_event
            )
            self._event_tap = self._api.create_event_tap(
                self._event_callback
            )
            if not self._event_tap:
                self._start_error = "event-tap-unavailable"
            else:
                source = self._api.create_run_loop_source(
                    self._event_tap
                )
                if not source:
                    self._start_error = "run-loop-source-unavailable"
                else:
                    self._run_loop = self._api.current_run_loop()
                    self._api.add_run_loop_source(
                        self._run_loop,
                        source,
                    )
                    self._api.enable_event_tap(self._event_tap)
        except Exception:
            self._start_error = "native-listener-error"
        finally:
            self._ready.set()

        if self._start_error or self._stop_requested.is_set():
            self._release_native_resources(source)
            return

        try:
            self._api.run_loop()
        finally:
            self._release_native_resources(source)

    def _release_native_resources(self, source: int | None) -> None:
        if self._run_loop is not None and source:
            self._api.remove_run_loop_source(
                self._run_loop,
                source,
            )
        self._api.release(source)
        self._api.release(self._event_tap)
        self._run_loop = None
        self._event_tap = None
        self._event_callback = None

    def _handle_event(
        self,
        _proxy,
        event_type: int,
        event: int,
        _user_info,
    ) -> int:
        if event_type in {
            K_CG_EVENT_TAP_DISABLED_BY_TIMEOUT,
            K_CG_EVENT_TAP_DISABLED_BY_USER_INPUT,
        }:
            if self._event_tap:
                self._api.enable_event_tap(self._event_tap)
            return event

        if event_type != K_CG_EVENT_KEY_DOWN:
            return event

        try:
            key_code = self._api.event_integer(
                event,
                K_CG_KEYBOARD_EVENT_KEYCODE,
            )
            is_repeat = self._api.event_integer(
                event,
                K_CG_KEYBOARD_EVENT_AUTOREPEAT,
            )
            modifier_flags = (
                self._api.event_flags(event) & K_CG_MODIFIER_MASK
            )
            if (
                not is_repeat
                and key_code == hotkey_key_code(self._hotkey)
                and modifier_flags
                == hotkey_modifier_flags(self._hotkey)
            ):
                self._activation_callback()
        except Exception:
            # ctypes 回调中的异常不能越过 C 边界。
            pass
        return event


class MacOSGlobalHotkey(GlobalHotkey):
    def __init__(
        self,
        listener_factory: Callable[..., QuartzHotkeyListener] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._listener_factory = listener_factory or QuartzHotkeyListener
        self._listener: QuartzHotkeyListener | None = None
        self._registered_hotkey: Hotkey | None = None

        application = QCoreApplication.instance()
        if application is not None:
            application.aboutToQuit.connect(self.close)

    def register_hotkey(self, hotkey: Hotkey) -> bool:
        try:
            hotkey = validate_hotkey(hotkey)
            hotkey_key_code(hotkey)
        except (KeyError, ValueError) as error:
            self.registration_failed.emit(str(error))
            return False

        previous_hotkey = self._registered_hotkey
        self.unregister_hotkey()

        listener = self._listener_factory(
            hotkey,
            self.activated.emit,
        )
        if listener.start():
            self._listener = listener
            self._registered_hotkey = hotkey
            return True

        if previous_hotkey is not None:
            self._restore_hotkey(previous_hotkey)
        self.registration_failed.emit(
            "无法启用全局快捷键，请在系统设置 > 隐私与安全性 > "
            "输入监控中允许 Trade Translator，然后重新启动应用"
        )
        return False

    def unregister_hotkey(self) -> None:
        if self._listener is not None:
            self._listener.stop()
        self._listener = None
        self._registered_hotkey = None

    def close(self) -> None:
        self.unregister_hotkey()

    def _restore_hotkey(self, hotkey: Hotkey) -> None:
        listener = self._listener_factory(
            hotkey,
            self.activated.emit,
        )
        if listener.start():
            self._listener = listener
            self._registered_hotkey = hotkey
