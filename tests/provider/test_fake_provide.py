from providers.fake import FakeTranslationProvider
from translation.models import TranslationRequest


def test_fake_provider_streams_translation(
    qtbot,
    qapp,
) -> None:
    provider = FakeTranslationProvider()

    request = TranslationRequest(
        request_id="request-1",
        text="Hello world",
        source_language="auto",
        target_language="zh-CN",
    )

    started_ids: list[str] = []
    received_chunks: list[str] = []

    provider.started.connect(started_ids.append)
    provider.chunk_received.connect(
        lambda request_id, chunk: received_chunks.append(chunk)
    )

    with qtbot.waitSignal(
        provider.completed,
        timeout=3000,
    ) as completed:
        provider.translate(request)

    # provider 仍然存活时处理 timer.deleteLater()。
    qapp.processEvents()

    assert started_ids == ["request-1"]
    assert completed.args == ["request-1"]
    assert "".join(received_chunks) == (
        "[模拟中文译文] Hello world"
    )

def test_fake_provider_can_be_cancelled(
    qtbot,
    qapp,
) -> None:
    provider = FakeTranslationProvider()

    request = TranslationRequest(
        request_id="request-2",
        text="This text should be cancelled",
        source_language="auto",
        target_language="zh-CN",
    )

    cancelled_ids: list[str] = []
    completed_ids: list[str] = []
    received_chunks: list[str] = []

    provider.cancelled.connect(cancelled_ids.append)
    provider.completed.connect(completed_ids.append)
    provider.chunk_received.connect(
        lambda request_id, chunk: received_chunks.append(chunk)
    )

    provider.translate(request)
    provider.cancel(request.request_id)

    qtbot.wait(500)

    # provider 仍然存活时完成延迟删除。
    qapp.processEvents()

    assert cancelled_ids == ["request-2"]
    assert completed_ids == []
    assert received_chunks == []