from PySide6.QtCore import QObject, QTimer

from providers.base import TranslationProvider
from translation.models import TranslationRequest


class FakeTranslationProvider(TranslationProvider):
    """使用 QTimer 模拟异步流式翻译。"""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        # 每个请求对应一个定时器。
        # 保存定时器是为了后续能够取消指定请求。
        self._timers: dict[str, QTimer] = {}

    def translate(self, request: TranslationRequest) -> None:
        """启动模拟翻译请求。"""
        request_id = request.request_id

        # 理论上 request_id 应当唯一。
        # 如果出现重复 ID，先取消旧任务。
        if request_id in self._timers:
            self.cancel(request_id)

        translated_text = self._build_fake_translation(request)
        chunks = self._split_into_chunks(translated_text)

        timer = QTimer(self)
        timer.setInterval(150)

        self._timers[request_id] = timer

        chunk_index = 0

        def send_next_chunk() -> None:
            nonlocal chunk_index

            # 如果定时器已经被 cancel() 移除，
            # 后续内容就不能再发送。
            if self._timers.get(request_id) is not timer:
                return

            chunk = chunks[chunk_index]
            chunk_index += 1

            self.chunk_received.emit(request_id, chunk)

            # 最后一段已经发出，结束请求。
            if chunk_index >= len(chunks):
                self._finish_request(request_id, timer)

        timer.timeout.connect(send_next_chunk)

        self.started.emit(request_id)
        timer.start()

    def cancel(self, request_id: str) -> None:
        """取消指定模拟请求。"""
        timer = self._timers.pop(request_id, None)

        if timer is None:
            return

        timer.stop()
        timer.deleteLater()

        self.cancelled.emit(request_id)

    def _finish_request(
        self,
        request_id: str,
        timer: QTimer,
    ) -> None:
        """清理定时器并发送完成信号。"""
        active_timer = self._timers.get(request_id)

        # 防止已经取消或被替换的请求发送完成信号。
        if active_timer is not timer:
            return

        self._timers.pop(request_id)

        timer.stop()
        timer.deleteLater()

        self.completed.emit(request_id)

    @staticmethod
    def _build_fake_translation(
        request: TranslationRequest,
    ) -> str:
        """根据目标语言生成模拟结果。"""
        if request.target_language.lower().startswith("zh"):
            prefix = "[模拟中文译文] "
        else:
            prefix = "[Mock English translation] "

        return prefix + request.text

    @staticmethod
    def _split_into_chunks(
        text: str,
        chunk_size: int = 6,
    ) -> list[str]:
        """将模拟译文切成多个流式片段。"""
        return [
            text[index:index + chunk_size]
            for index in range(0, len(text), chunk_size)
        ]