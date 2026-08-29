import ctypes
import sys
from ctypes import wintypes


INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_C = ord("C")

ULONG_PTR = ctypes.c_size_t


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUTUNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("data",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("data", INPUTUNION),
    ]


def load_user32():
    if sys.platform != "win32":
        raise RuntimeError("Windows 输入模拟只能在 Windows 上使用")

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.SendInput.argtypes = [
        wintypes.UINT,
        ctypes.POINTER(INPUT),
        ctypes.c_int,
    ]
    user32.SendInput.restype = wintypes.UINT
    return user32


class WindowsCopyKeySender:
    """通过 SendInput 向当前前台应用发送一次 Ctrl+C。"""

    def __init__(self, user32=None) -> None:
        self._user32 = user32 or load_user32()

    def send_copy_shortcut(self) -> bool:
        inputs = (INPUT * 4)(
            self._key_input(VK_CONTROL),
            self._key_input(VK_C),
            self._key_input(VK_C, KEYEVENTF_KEYUP),
            self._key_input(VK_CONTROL, KEYEVENTF_KEYUP),
        )
        sent_count = self._user32.SendInput(
            len(inputs),
            inputs,
            ctypes.sizeof(INPUT),
        )
        return int(sent_count) == len(inputs)

    @staticmethod
    def _key_input(virtual_key: int, flags: int = 0) -> INPUT:
        keyboard_input = INPUT()
        keyboard_input.type = INPUT_KEYBOARD
        keyboard_input.ki = KEYBDINPUT(
            wVk=virtual_key,
            wScan=0,
            dwFlags=flags,
            time=0,
            dwExtraInfo=0,
        )
        return keyboard_input
