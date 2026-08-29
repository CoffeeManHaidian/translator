import ctypes
import ctypes.util
import sys


K_CG_HID_EVENT_TAP = 0
K_CG_SESSION_EVENT_TAP = 1
K_CG_HEAD_INSERT_EVENT_TAP = 0
K_CG_EVENT_TAP_OPTION_LISTEN_ONLY = 1

K_CG_EVENT_KEY_DOWN = 10
K_CG_EVENT_TAP_DISABLED_BY_TIMEOUT = 0xFFFFFFFE
K_CG_EVENT_TAP_DISABLED_BY_USER_INPUT = 0xFFFFFFFF

K_CG_KEYBOARD_EVENT_AUTOREPEAT = 8
K_CG_KEYBOARD_EVENT_KEYCODE = 9

K_CG_EVENT_FLAG_MASK_SHIFT = 0x00020000
K_CG_EVENT_FLAG_MASK_CONTROL = 0x00040000
K_CG_EVENT_FLAG_MASK_ALTERNATE = 0x00080000
K_CG_EVENT_FLAG_MASK_COMMAND = 0x00100000
K_CG_MODIFIER_MASK = (
    K_CG_EVENT_FLAG_MASK_SHIFT
    | K_CG_EVENT_FLAG_MASK_CONTROL
    | K_CG_EVENT_FLAG_MASK_ALTERNATE
    | K_CG_EVENT_FLAG_MASK_COMMAND
)

CG_EVENT_TAP_CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_uint32,
    ctypes.c_void_p,
    ctypes.c_void_p,
)


def _framework_path(name: str) -> str:
    discovered = ctypes.util.find_library(name)
    if discovered:
        return discovered
    return f"/System/Library/Frameworks/{name}.framework/{name}"


class MacOSQuartzApi:
    """Quartz 和 Core Foundation 的最小 ctypes 封装。"""

    def __init__(self) -> None:
        if sys.platform != "darwin":
            raise OSError("MacOSQuartzApi 只能在 macOS 上使用")

        self._quartz = ctypes.CDLL(
            _framework_path("ApplicationServices")
        )
        self._core_foundation = ctypes.CDLL(
            _framework_path("CoreFoundation")
        )
        self._configure_functions()
        self._common_modes = ctypes.c_void_p.in_dll(
            self._core_foundation,
            "kCFRunLoopCommonModes",
        ).value

    def _configure_functions(self) -> None:
        quartz = self._quartz
        core = self._core_foundation

        quartz.CGEventTapCreate.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint64,
            CG_EVENT_TAP_CALLBACK,
            ctypes.c_void_p,
        ]
        quartz.CGEventTapCreate.restype = ctypes.c_void_p
        quartz.CGEventTapEnable.argtypes = [
            ctypes.c_void_p,
            ctypes.c_bool,
        ]
        quartz.CGEventGetFlags.argtypes = [ctypes.c_void_p]
        quartz.CGEventGetFlags.restype = ctypes.c_uint64
        quartz.CGEventGetIntegerValueField.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        quartz.CGEventGetIntegerValueField.restype = ctypes.c_int64
        quartz.CGEventCreateKeyboardEvent.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint16,
            ctypes.c_bool,
        ]
        quartz.CGEventCreateKeyboardEvent.restype = ctypes.c_void_p
        quartz.CGEventSetFlags.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint64,
        ]
        quartz.CGEventSetFlags.restype = None
        quartz.CGEventPost.argtypes = [
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        quartz.CGEventPost.restype = None

        for function_name in (
            "CGPreflightListenEventAccess",
            "CGRequestListenEventAccess",
            "CGPreflightPostEventAccess",
            "CGRequestPostEventAccess",
        ):
            function = getattr(quartz, function_name, None)
            if function is not None:
                function.restype = ctypes.c_bool

        core.CFMachPortCreateRunLoopSource.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_long,
        ]
        core.CFMachPortCreateRunLoopSource.restype = ctypes.c_void_p
        core.CFRunLoopGetCurrent.restype = ctypes.c_void_p
        core.CFRunLoopAddSource.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        core.CFRunLoopAddSource.restype = None
        core.CFRunLoopRemoveSource.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        core.CFRunLoopRemoveSource.restype = None
        core.CFRunLoopStop.argtypes = [ctypes.c_void_p]
        core.CFRunLoopStop.restype = None
        core.CFRunLoopWakeUp.argtypes = [ctypes.c_void_p]
        core.CFRunLoopWakeUp.restype = None
        core.CFRelease.argtypes = [ctypes.c_void_p]
        core.CFRelease.restype = None

    def request_listen_event_access(self) -> bool:
        return self._request_access(
            "CGPreflightListenEventAccess",
            "CGRequestListenEventAccess",
        )

    def request_post_event_access(self) -> bool:
        return self._request_access(
            "CGPreflightPostEventAccess",
            "CGRequestPostEventAccess",
        )

    def _request_access(
        self,
        preflight_name: str,
        request_name: str,
    ) -> bool:
        preflight = getattr(self._quartz, preflight_name, None)
        request = getattr(self._quartz, request_name, None)
        if preflight is None:
            return True
        if bool(preflight()):
            return True
        return bool(request()) if request is not None else False

    def create_event_tap(self, callback) -> int | None:
        mask = 1 << K_CG_EVENT_KEY_DOWN
        return self._quartz.CGEventTapCreate(
            K_CG_SESSION_EVENT_TAP,
            K_CG_HEAD_INSERT_EVENT_TAP,
            K_CG_EVENT_TAP_OPTION_LISTEN_ONLY,
            mask,
            callback,
            None,
        )

    def enable_event_tap(self, event_tap: int) -> None:
        self._quartz.CGEventTapEnable(event_tap, True)

    def event_flags(self, event: int) -> int:
        return int(self._quartz.CGEventGetFlags(event))

    def event_integer(self, event: int, field: int) -> int:
        return int(
            self._quartz.CGEventGetIntegerValueField(event, field)
        )

    def create_run_loop_source(self, event_tap: int) -> int | None:
        return self._core_foundation.CFMachPortCreateRunLoopSource(
            None,
            event_tap,
            0,
        )

    def current_run_loop(self) -> int:
        return self._core_foundation.CFRunLoopGetCurrent()

    def add_run_loop_source(self, run_loop: int, source: int) -> None:
        self._core_foundation.CFRunLoopAddSource(
            run_loop,
            source,
            self._common_modes,
        )

    def remove_run_loop_source(self, run_loop: int, source: int) -> None:
        self._core_foundation.CFRunLoopRemoveSource(
            run_loop,
            source,
            self._common_modes,
        )

    def run_loop(self) -> None:
        self._core_foundation.CFRunLoopRun()

    def stop_run_loop(self, run_loop: int) -> None:
        self._core_foundation.CFRunLoopStop(run_loop)
        self._core_foundation.CFRunLoopWakeUp(run_loop)

    def release(self, value: int | None) -> None:
        if value:
            self._core_foundation.CFRelease(value)

    def create_keyboard_event(
        self,
        key_code: int,
        is_key_down: bool,
    ) -> int | None:
        return self._quartz.CGEventCreateKeyboardEvent(
            None,
            key_code,
            is_key_down,
        )

    def post_event(self, event: int) -> None:
        self._quartz.CGEventPost(K_CG_HID_EVENT_TAP, event)

    def set_event_flags(self, event: int, flags: int) -> None:
        self._quartz.CGEventSetFlags(event, flags)
