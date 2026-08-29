from uuid import uuid4

from PySide6.QtCore import QMimeData, QObject, QTimer
from PySide6.QtGui import QClipboard, QGuiApplication

from platforms.macos.input_sender import MacOSCopyKeySender
from platforms.text_capture import TextCapture


class MacOSClipboardTextCapture(TextCapture):
    """模拟 Command+C，读取所选文字后恢复原剪贴板。"""

    def __init__(
        self,
        clipboard: QClipboard | None = None,
        input_sender: MacOSCopyKeySender | None = None,
        timeout_ms: int = 1_000,
        copy_delay_ms: int = 120,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._clipboard = clipboard or QGuiApplication.clipboard()
        self._input_sender = input_sender or MacOSCopyKeySender()
        self._timeout_ms = timeout_ms
        self._copy_delay_ms = copy_delay_ms
        self._capturing = False
        self._marker = ""
        self._original_mime_data: QMimeData | None = None

        self._copy_delay_timer = QTimer(self)
        self._copy_delay_timer.setSingleShot(True)
        self._copy_delay_timer.timeout.connect(self._send_copy)

        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._on_timeout)
        self._clipboard.dataChanged.connect(
            self._on_clipboard_changed
        )

    def capture_selected_text(self) -> None:
        self._cancel_active_capture()
        self.capture_started.emit()
        self._original_mime_data = self._clone_mime_data(
            self._clipboard.mimeData()
        )
        self._marker = f"trade-translator-capture-{uuid4().hex}"

        self._clipboard.setText(self._marker)
        self._capturing = True
        self._timeout_timer.start(self._timeout_ms)
        self._copy_delay_timer.start(self._copy_delay_ms)

    def close(self) -> None:
        self._cancel_active_capture()

    def _send_copy(self) -> None:
        if not self._capturing:
            return
        if self._input_sender.send_copy_shortcut():
            return
        self._finish_with_error(
            "无法模拟复制，请在系统设置 > 隐私与安全性 > "
            "辅助功能中允许 Trade Translator"
        )

    def _on_clipboard_changed(self) -> None:
        if not self._capturing:
            return
        captured_text = self._clipboard.text().strip()
        if not captured_text or captured_text == self._marker:
            return

        self._capturing = False
        self._stop_timers()
        self._restore_clipboard()
        self.text_captured.emit(captured_text)

    def _on_timeout(self) -> None:
        if self._capturing:
            self._finish_with_error("未读取到所选文字，请先选择文本")

    def _finish_with_error(self, message: str) -> None:
        self._capturing = False
        self._stop_timers()
        self._restore_clipboard()
        self.capture_failed.emit(message)

    def _cancel_active_capture(self) -> None:
        if not self._capturing:
            return
        self._capturing = False
        self._stop_timers()
        self._restore_clipboard()

    def _stop_timers(self) -> None:
        self._copy_delay_timer.stop()
        self._timeout_timer.stop()

    def _restore_clipboard(self) -> None:
        original = self._original_mime_data
        self._original_mime_data = None
        self._marker = ""
        if original is None:
            self._clipboard.clear()
        else:
            self._clipboard.setMimeData(original)

    @staticmethod
    def _clone_mime_data(source: QMimeData | None) -> QMimeData:
        clone = QMimeData()
        if source is None:
            return clone

        for mime_format in source.formats():
            clone.setData(mime_format, source.data(mime_format))
        if source.hasText():
            clone.setText(source.text())
        if source.hasHtml():
            clone.setHtml(source.html())
        if source.hasUrls():
            clone.setUrls(source.urls())
        if source.hasImage():
            clone.setImageData(source.imageData())
        if source.hasColor():
            clone.setColorData(source.colorData())
        return clone
