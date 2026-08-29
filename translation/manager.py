from uuid import uuid4
from PySide6.QtCore import QObject, Signal

from providers.base import TranslationProvider
from translation.models import TranslationRequest


class TranslationManager(QObject):
    """管理翻译请求生命周期"""

    translation_started = Signal(str)
    translation_updated = Signal(str)
    translation_completed = Signal(str)
    translation_failed = Signal(str)
    translation_cancelled = Signal()

    def __init__(self, provider: TranslationProvider, parent: object | None = None):
        super().__init__(parent)

        # 初始化翻译提供者和当前请求ID
        self._provider = provider
        self._current_request_id: str | None = None
        self._translation_text = ""

        self._connect_provider(self._provider)

    def set_provider(self, provider: TranslationProvider) -> None:
        """取消当前任务并切换后续请求使用的翻译服务。"""
        if provider is self._provider:
            return

        self.cancel_current()
        self._disconnect_provider(self._provider)
        self._clear_current_request()
        self._provider = provider
        self._connect_provider(provider)

    def _connect_provider(self, provider: TranslationProvider) -> None:
        provider.started.connect(self._on_started)
        provider.chunk_received.connect(self._on_chunk_received)
        provider.completed.connect(self._on_completed)
        provider.failed.connect(self._on_failed)
        provider.cancelled.connect(self._on_cancelled)

    def _disconnect_provider(self, provider: TranslationProvider) -> None:
        for signal, slot in (
            (provider.started, self._on_started),
            (provider.chunk_received, self._on_chunk_received),
            (provider.completed, self._on_completed),
            (provider.failed, self._on_failed),
            (provider.cancelled, self._on_cancelled),
        ):
            try:
                signal.disconnect(slot)
            except (RuntimeError, TypeError):
                pass

    def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto",
    ) -> str | None:
        """发起翻译请求"""
        text = text.strip()

        if not text:
            self.translation_failed.emit("请输入文本")
            return None

        # 如果有正在进行的请求，取消它
        self.cancel_current()

        # 生成新的请求 ID
        request_id = uuid4().hex

        self._current_request_id = request_id
        self._translation_text = ""

        # 创建翻译请求对象
        request = TranslationRequest(
            request_id=request_id,
            text=text,
            source_language=source_language,
            target_language=target_language
        )

        self._provider.translate(request)

        return request_id

    def cancel_current(self) -> None:
        """取消当前的翻译请求"""
        if self._current_request_id is None:
            return

        self._provider.cancel(self._current_request_id)

    def _on_started(self, request_id: str) -> None:
        if request_id != self._current_request_id:
            return

        self.translation_started.emit(request_id)

    def _on_chunk_received(self, request_id: str, chunk:str) -> None:
        if request_id != self._current_request_id:
            return

        self._translation_text += chunk
        self.translation_updated.emit(self._translation_text)

    def _on_completed(self, request_id: str) -> None:
        if request_id != self._current_request_id:
            return

        translation_text = self._translation_text
        # 清除当前请求 ID
        self._clear_current_request()
        # 发射完成信号
        self.translation_completed.emit(translation_text)

    def _on_failed(self, request_id: str, error: object) -> None:
        if request_id != self._current_request_id:
            return

        # 清除当前请求 ID
        self._clear_current_request()
        # 发射失败信号
        self.translation_failed.emit(str(error))

    def _on_cancelled(self, request_id: str) -> None:
        if request_id != self._current_request_id:
            return

        # 清除当前请求 ID
        self._clear_current_request()
        # 发射取消信号
        self.translation_cancelled.emit()

    def _clear_current_request(self) -> None:
        """清除当前请求 ID"""
        self._current_request_id = None
        self._translation_text = ""
