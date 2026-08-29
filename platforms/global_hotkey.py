from PySide6.QtCore import QObject, Signal

from platforms.models import Hotkey


class GlobalHotkey(QObject):
    activated = Signal()
    registration_failed = Signal(str)

    def register_hotkey(self, hotkey: Hotkey) -> bool:
        """注册系统级快捷键。"""
        raise NotImplementedError

    def unregister_hotkey(self) -> None:
        """注销系统级快捷键"""
        raise NotImplementedError
