from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from history.models import TranslationHistoryEntry
from history.repository import HistoryRepository


TARGET_LANGUAGE_NAMES = {"zh-CN": "中文", "en": "英语"}


class HistoryDialog(QDialog):
    reuse_requested = Signal(str, str)

    def __init__(
        self,
        repository: HistoryRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._repository = repository
        self._entries: list[TranslationHistoryEntry] = []
        self.setWindowTitle("翻译历史")
        self.resize(760, 480)
        self.setMinimumSize(620, 380)

        self.history_list = QListWidget(self)
        self.history_list.setAccessibleName("翻译历史列表")
        self.history_list.currentRowChanged.connect(self._show_entry)

        self.source_text_edit = self._create_text_view("历史原文")
        self.translation_text_edit = self._create_text_view("历史译文")

        detail_widget = QWidget(self)
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.addWidget(QLabel("原文", detail_widget))
        detail_layout.addWidget(self.source_text_edit, 1)
        detail_layout.addWidget(QLabel("译文", detail_widget))
        detail_layout.addWidget(self.translation_text_edit, 1)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(self.history_list)
        splitter.addWidget(detail_widget)
        splitter.setSizes([280, 480])

        self.clear_button = QPushButton("清空历史", self)
        self.copy_button = QPushButton("复制译文", self)
        self.reuse_button = QPushButton("再次使用", self)
        close_button = QPushButton("关闭", self)
        self.copy_button.setEnabled(False)
        self.reuse_button.setEnabled(False)

        self.clear_button.clicked.connect(self.clear_history)
        self.copy_button.clicked.connect(self.copy_translation)
        self.reuse_button.clicked.connect(self.reuse_entry)
        close_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.reuse_button)
        button_layout.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(splitter, 1)
        layout.addLayout(button_layout)
        self.refresh()

    @staticmethod
    def _create_text_view(accessible_name: str) -> QPlainTextEdit:
        text_view = QPlainTextEdit()
        text_view.setReadOnly(True)
        text_view.setAccessibleName(accessible_name)
        return text_view

    def refresh(self) -> None:
        self._entries = self._repository.list_recent()
        self.history_list.clear()
        for entry in self._entries:
            target = TARGET_LANGUAGE_NAMES.get(
                entry.target_language,
                entry.target_language,
            )
            preview = " ".join(entry.source_text.split())
            if len(preview) > 48:
                preview = f"{preview[:48]}…"
            timestamp = self._format_timestamp(entry.created_at)
            self.history_list.addItem(
                QListWidgetItem(f"{target} · {timestamp}\n{preview}")
            )

        has_entries = bool(self._entries)
        self.clear_button.setEnabled(has_entries)
        if has_entries:
            self.history_list.setCurrentRow(0)
        else:
            self.source_text_edit.setPlaceholderText("还没有翻译历史")
            self.translation_text_edit.clear()
            self.copy_button.setEnabled(False)
            self.reuse_button.setEnabled(False)

    def _show_entry(self, row: int) -> None:
        if not 0 <= row < len(self._entries):
            self.copy_button.setEnabled(False)
            self.reuse_button.setEnabled(False)
            return
        entry = self._entries[row]
        self.source_text_edit.setPlainText(entry.source_text)
        self.translation_text_edit.setPlainText(entry.translated_text)
        self.copy_button.setEnabled(True)
        self.reuse_button.setEnabled(True)

    def copy_translation(self) -> None:
        text = self.translation_text_edit.toPlainText().strip()
        if text:
            QGuiApplication.clipboard().setText(text)

    def reuse_entry(self) -> None:
        row = self.history_list.currentRow()
        if not 0 <= row < len(self._entries):
            return
        entry = self._entries[row]
        self.reuse_requested.emit(entry.source_text, entry.target_language)
        self.accept()

    def clear_history(self) -> None:
        answer = QMessageBox.question(
            self,
            "清空翻译历史",
            "确定要清空全部翻译历史吗？",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._repository.clear()
        self.refresh()

    @staticmethod
    def _format_timestamp(value: str) -> str:
        try:
            return datetime.fromisoformat(value).astimezone().strftime(
                "%m-%d %H:%M"
            )
        except ValueError:
            return value
