from PySide6.QtCore import QObject, Signal


class TextCapture(QObject):
    capture_started = Signal()
    text_captured = Signal(str)
    capture_failed = Signal(str)

    def capture_selected_text(self) -> None:
        """异步读取当前应用中选中的文字。"""
        raise NotImplementedError

    def close(self) -> None:
        """释放取词过程中的临时资源；无资源的实现无需覆盖。"""
        pass
