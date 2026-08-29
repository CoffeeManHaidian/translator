from PySide6.QtCore import QObject, Signal

from translation.models import TranslationRequest

class TranslationProvider(QObject):
    started = Signal(str)
    chunk_received = Signal(str, str)
    completed = Signal(str)
    failed = Signal(str, object)
    cancelled = Signal(str)

    def translate(self, request: TranslationRequest) -> None:
        """开始翻译请求"""
        raise NotImplementedError

    def cancel(self, request_id: str) -> None:
        """取消翻译请求"""
        raise NotImplementedError
