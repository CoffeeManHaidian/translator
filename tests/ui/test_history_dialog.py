from history.repository import HistoryRepository
from translation.models import TranslationRequest
from ui.history_dialog import HistoryDialog


def populated_repository() -> HistoryRepository:
    repository = HistoryRepository(":memory:")
    repository.add(
        TranslationRequest(
            request_id="history-request",
            text="Hello",
            source_language="auto",
            target_language="zh-CN",
        ),
        "你好",
        provider="deepseek",
        model="deepseek-chat",
    )
    return repository


def test_history_dialog_displays_saved_translation(qtbot) -> None:
    repository = populated_repository()
    dialog = HistoryDialog(repository)
    qtbot.addWidget(dialog)

    assert dialog.history_list.count() == 1
    assert dialog.source_text_edit.toPlainText() == "Hello"
    assert dialog.translation_text_edit.toPlainText() == "你好"
    assert dialog.copy_button.isEnabled()
    assert dialog.reuse_button.isEnabled()
    repository.close()


def test_history_dialog_can_reuse_selected_translation(qtbot) -> None:
    repository = populated_repository()
    dialog = HistoryDialog(repository)
    qtbot.addWidget(dialog)
    requests: list[tuple[str, str]] = []
    dialog.reuse_requested.connect(
        lambda text, language: requests.append((text, language))
    )

    dialog.reuse_entry()

    assert requests == [("Hello", "zh-CN")]
    repository.close()
