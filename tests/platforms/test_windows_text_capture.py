from PySide6.QtCore import QMimeData, QObject, Signal

from platforms.windows.input_sender import (
    INPUT_KEYBOARD,
    KEYEVENTF_KEYUP,
    VK_C,
    VK_CONTROL,
    WindowsCopyKeySender,
)
from platforms.windows.text_capture import WindowsClipboardTextCapture


class FakeClipboard(QObject):
    dataChanged = Signal()

    def __init__(self, text: str = "") -> None:
        super().__init__()
        self._mime_data = QMimeData()
        self._mime_data.setText(text)

    def mimeData(self) -> QMimeData:
        return self._mime_data

    def text(self) -> str:
        return self._mime_data.text()

    def setText(self, text: str) -> None:
        mime_data = QMimeData()
        mime_data.setText(text)
        self._mime_data = mime_data
        self.dataChanged.emit()

    def setMimeData(self, mime_data: QMimeData) -> None:
        self._mime_data = mime_data
        self.dataChanged.emit()

    def clear(self) -> None:
        self._mime_data = QMimeData()
        self.dataChanged.emit()


class FakeInputSender:
    def __init__(self, result: bool = True) -> None:
        self.result = result
        self.send_count = 0

    def send_copy_shortcut(self) -> bool:
        self.send_count += 1
        return self.result


class FakeUser32:
    def __init__(self, send_result: int = 4) -> None:
        self.send_result = send_result
        self.events = []

    def SendInput(self, count, inputs, input_size) -> int:
        self.events = [
            (
                inputs[index].type,
                inputs[index].ki.wVk,
                inputs[index].ki.dwFlags,
            )
            for index in range(count)
        ]
        return self.send_result


def test_copy_sender_sends_ctrl_c_press_and_release() -> None:
    user32 = FakeUser32()
    sender = WindowsCopyKeySender(user32=user32)

    assert sender.send_copy_shortcut()
    assert user32.events == [
        (INPUT_KEYBOARD, VK_CONTROL, 0),
        (INPUT_KEYBOARD, VK_C, 0),
        (INPUT_KEYBOARD, VK_C, KEYEVENTF_KEYUP),
        (INPUT_KEYBOARD, VK_CONTROL, KEYEVENTF_KEYUP),
    ]


def test_capture_returns_selected_text_and_restores_clipboard(qtbot) -> None:
    clipboard = FakeClipboard("original clipboard")
    input_sender = FakeInputSender()
    capture = WindowsClipboardTextCapture(
        clipboard=clipboard,
        input_sender=input_sender,
        timeout_ms=500,
        copy_delay_ms=0,
    )
    captured_texts: list[str] = []
    capture.text_captured.connect(captured_texts.append)

    capture.capture_selected_text()
    assert clipboard.text().startswith("trade-translator-capture-")
    qtbot.waitUntil(lambda: input_sender.send_count == 1)

    clipboard.setText("  selected text  ")

    assert captured_texts == ["selected text"]
    assert clipboard.text() == "original clipboard"


def test_capture_accepts_text_equal_to_old_clipboard(qtbot) -> None:
    clipboard = FakeClipboard("same text")
    input_sender = FakeInputSender()
    capture = WindowsClipboardTextCapture(
        clipboard=clipboard,
        input_sender=input_sender,
        timeout_ms=500,
        copy_delay_ms=0,
    )
    captured_texts: list[str] = []
    capture.text_captured.connect(captured_texts.append)

    capture.capture_selected_text()
    qtbot.waitUntil(lambda: input_sender.send_count == 1)
    clipboard.setText("same text")

    assert captured_texts == ["same text"]
    assert clipboard.text() == "same text"


def test_capture_timeout_restores_clipboard_and_reports_error(qtbot) -> None:
    clipboard = FakeClipboard("keep me")
    capture = WindowsClipboardTextCapture(
        clipboard=clipboard,
        input_sender=FakeInputSender(),
        timeout_ms=30,
        copy_delay_ms=0,
    )
    errors: list[str] = []
    capture.capture_failed.connect(errors.append)

    capture.capture_selected_text()
    qtbot.waitUntil(lambda: len(errors) == 1, timeout=300)

    assert errors == ["未读取到所选文字，请先选择文本"]
    assert clipboard.text() == "keep me"


def test_send_input_failure_restores_clipboard(qtbot) -> None:
    clipboard = FakeClipboard("keep me")
    capture = WindowsClipboardTextCapture(
        clipboard=clipboard,
        input_sender=FakeInputSender(result=False),
        timeout_ms=500,
        copy_delay_ms=0,
    )
    errors: list[str] = []
    capture.capture_failed.connect(errors.append)

    capture.capture_selected_text()
    qtbot.waitUntil(lambda: len(errors) == 1)

    assert "无法模拟复制" in errors[0]
    assert clipboard.text() == "keep me"
