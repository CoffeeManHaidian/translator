from providers.base import TranslationProvider
from translation.manager import TranslationManager
from translation.models import TranslationRequest


class StubTranslationProvider(TranslationProvider):
    """可由测试主动控制信号的翻译 Provider。"""

    def __init__(self) -> None:
        super().__init__()
        self.requests: list[TranslationRequest] = []
        self.cancelled_request_ids: list[str] = []

    def translate(self, request: TranslationRequest) -> None:
        self.requests.append(request)
        self.started.emit(request.request_id)

    def cancel(self, request_id: str) -> None:
        self.cancelled_request_ids.append(request_id)
        self.cancelled.emit(request_id)


def test_manager_accumulates_streamed_translation() -> None:
    provider = StubTranslationProvider()
    manager = TranslationManager(provider)

    started_ids: list[str] = []
    updates: list[str] = []
    completed_texts: list[str] = []

    manager.translation_started.connect(started_ids.append)
    manager.translation_updated.connect(updates.append)
    manager.translation_completed.connect(completed_texts.append)

    request_id = manager.translate(
        text="Hello",
        target_language="zh-CN",
    )

    assert request_id is not None
    assert started_ids == [request_id]

    provider.chunk_received.emit(request_id, "你")
    provider.chunk_received.emit(request_id, "好")
    provider.completed.emit(request_id)

    assert updates == ["你", "你好"]
    assert completed_texts == ["你好"]


def test_manager_rejects_empty_text() -> None:
    provider = StubTranslationProvider()
    manager = TranslationManager(provider)

    errors: list[str] = []
    manager.translation_failed.connect(errors.append)

    request_id = manager.translate(
        text="   ",
        target_language="zh-CN",
    )

    assert request_id is None
    assert provider.requests == []
    assert errors == ["请输入文本"]


def test_manager_cancels_current_request() -> None:
    provider = StubTranslationProvider()
    manager = TranslationManager(provider)

    cancelled_count = 0

    def record_cancellation() -> None:
        nonlocal cancelled_count
        cancelled_count += 1

    manager.translation_cancelled.connect(record_cancellation)

    request_id = manager.translate(
        text="Hello",
        target_language="zh-CN",
    )
    manager.cancel_current()

    assert request_id is not None
    assert provider.cancelled_request_ids == [request_id]
    assert cancelled_count == 1


def test_manager_ignores_stale_provider_events() -> None:
    provider = StubTranslationProvider()
    manager = TranslationManager(provider)

    updates: list[str] = []
    manager.translation_updated.connect(updates.append)

    old_request_id = manager.translate(
        text="Old text",
        target_language="zh-CN",
    )
    new_request_id = manager.translate(
        text="New text",
        target_language="zh-CN",
    )

    assert old_request_id is not None
    assert new_request_id is not None

    provider.chunk_received.emit(old_request_id, "旧")
    provider.chunk_received.emit(new_request_id, "新")

    assert updates == ["新"]


def test_manager_switches_provider_and_disconnects_old_one() -> None:
    old_provider = StubTranslationProvider()
    new_provider = StubTranslationProvider()
    manager = TranslationManager(old_provider)

    old_request_id = manager.translate("Old", "zh-CN")
    manager.set_provider(new_provider)
    new_request_id = manager.translate("New", "zh-CN")

    updates: list[str] = []
    manager.translation_updated.connect(updates.append)
    old_provider.chunk_received.emit(old_request_id, "旧")
    new_provider.chunk_received.emit(new_request_id, "新")

    assert old_provider.cancelled_request_ids == [old_request_id]
    assert updates == ["新"]
