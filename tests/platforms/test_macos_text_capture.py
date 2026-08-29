from PySide6.QtCore import QMimeData, QObject, Signal

from platforms.macos.input_sender import (
    MACOS_KEY_CODE_C,
    MACOS_KEY_CODE_COMMAND,
    MacOSCopyKeySender,
)
from platforms.macos.quartz_api import K_CG_EVENT_FLAG_MASK_COMMAND
from platforms.macos.text_capture import MacOSClipboardTextCapture


class FakeQuartzApi:
    def __init__(self, access=True) -> None:
        self.access = access
        self.created_events = []
        self.posted_events = []
        self.event_flags = []
        self.released_events = []

    def request_post_event_access(self) -> bool:
        return self.access

    def create_keyboard_event(self, key_code, is_key_down):
        event = (key_code, is_key_down)
        self.created_events.append(event)
        return event

    def post_event(self, event) -> None:
        self.posted_events.append(event)

    def set_event_flags(self, event, flags) -> None:
        self.event_flags.append((event, flags))

    def release(self, event) -> None:
        self.released_events.append(event)


class FakeClipboard(QObject):
    dataChanged = Signal()

    def __init__(self, text="") -> None:
        super().__init__()
        self._mime_data = QMimeData()
        self._mime_data.setText(text)

    def mimeData(self):
        return self._mime_data

    def text(self) -> str:
        return self._mime_data.text()

    def setText(self, text) -> None:
        self._mime_data = QMimeData()
        self._mime_data.setText(text)
        self.dataChanged.emit()

    def setTextSilently(self, text) -> None:
        self._mime_data = QMimeData()
        self._mime_data.setText(text)

    def setMimeData(self, mime_data) -> None:
        self._mime_data = mime_data
        self.dataChanged.emit()

    def clear(self) -> None:
        self._mime_data = QMimeData()
        self.dataChanged.emit()


class FakeInputSender:
    def __init__(self, result=True) -> None:
        self.result = result
        self.send_count = 0

    def send_copy_shortcut(self) -> bool:
        self.send_count += 1
        return self.result


def test_macos_copy_sender_posts_command_c_in_order() -> None:
    api = FakeQuartzApi()
    sender = MacOSCopyKeySender(api=api)

    assert sender.send_copy_shortcut()
    assert api.posted_events == [
        (MACOS_KEY_CODE_COMMAND, True),
        (MACOS_KEY_CODE_C, True),
        (MACOS_KEY_CODE_C, False),
        (MACOS_KEY_CODE_COMMAND, False),
    ]
    assert api.event_flags == [
        (
            (MACOS_KEY_CODE_COMMAND, True),
            K_CG_EVENT_FLAG_MASK_COMMAND,
        ),
        ((MACOS_KEY_CODE_C, True), K_CG_EVENT_FLAG_MASK_COMMAND),
        ((MACOS_KEY_CODE_C, False), K_CG_EVENT_FLAG_MASK_COMMAND),
        ((MACOS_KEY_CODE_COMMAND, False), 0),
    ]
    assert api.released_events == api.posted_events


def test_macos_copy_sender_rejects_missing_permission() -> None:
    api = FakeQuartzApi(access=False)

    assert not MacOSCopyKeySender(api=api).send_copy_shortcut()
    assert api.created_events == []


def test_macos_capture_reads_text_and_restores_clipboard(qtbot) -> None:
    clipboard = FakeClipboard("original")
    input_sender = FakeInputSender()
    capture = MacOSClipboardTextCapture(
        clipboard=clipboard,
        input_sender=input_sender,
        timeout_ms=500,
        copy_delay_ms=0,
    )
    captured_texts = []
    capture.text_captured.connect(captured_texts.append)

    capture.capture_selected_text()
    qtbot.waitUntil(lambda: input_sender.send_count == 1)
    clipboard.setText("  selected on macOS  ")

    assert captured_texts == ["selected on macOS"]
    assert clipboard.text() == "original"


def test_macos_capture_reports_accessibility_failure(qtbot) -> None:
    clipboard = FakeClipboard("original")
    capture = MacOSClipboardTextCapture(
        clipboard=clipboard,
        input_sender=FakeInputSender(result=False),
        timeout_ms=500,
        copy_delay_ms=0,
    )
    errors = []
    capture.capture_failed.connect(errors.append)

    capture.capture_selected_text()
    qtbot.waitUntil(lambda: len(errors) == 1)

    assert "辅助功能" in errors[0]
    assert clipboard.text() == "original"


def test_macos_capture_polls_when_clipboard_signal_is_missing(qtbot) -> None:
    clipboard = FakeClipboard("original")
    input_sender = FakeInputSender()
    capture = MacOSClipboardTextCapture(
        clipboard=clipboard,
        input_sender=input_sender,
        timeout_ms=500,
        copy_delay_ms=0,
        poll_interval_ms=10,
    )
    captured_texts = []
    capture.text_captured.connect(captured_texts.append)

    capture.capture_selected_text()
    qtbot.waitUntil(lambda: input_sender.send_count == 1)
    clipboard.setTextSilently("selected without dataChanged")
    qtbot.waitUntil(lambda: len(captured_texts) == 1)

    assert captured_texts == ["selected without dataChanged"]
    assert clipboard.text() == "original"
