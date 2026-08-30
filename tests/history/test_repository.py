from history.repository import HistoryRepository
from translation.models import TranslationRequest


def make_request(request_id: str, text: str = "Hello") -> TranslationRequest:
    return TranslationRequest(
        request_id=request_id,
        text=text,
        source_language="auto",
        target_language="zh-CN",
    )


def test_history_repository_saves_and_lists_recent_translations() -> None:
    repository = HistoryRepository(":memory:")

    first_id = repository.add(
        make_request("first"),
        "你好",
        provider="deepseek",
        model="deepseek-chat",
    )
    second_id = repository.add(
        make_request("second", "Goodbye"),
        "再见",
        provider="deepseek",
        model="deepseek-chat",
    )

    entries = repository.list_recent()

    assert first_id is not None
    assert second_id is not None
    assert [entry.source_text for entry in entries] == ["Goodbye", "Hello"]
    assert entries[0].translated_text == "再见"
    assert entries[0].target_language == "zh-CN"
    assert entries[0].provider == "deepseek"
    repository.close()


def test_history_repository_ignores_empty_results_and_can_clear() -> None:
    repository = HistoryRepository(":memory:")

    assert repository.add(
        make_request("empty"),
        "   ",
        provider="deepseek",
        model="deepseek-chat",
    ) is None

    repository.add(
        make_request("saved"),
        "你好",
        provider="deepseek",
        model="deepseek-chat",
    )
    repository.clear()

    assert repository.list_recent() == []
    repository.close()
