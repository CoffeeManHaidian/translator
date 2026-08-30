from PySide6.QtWidgets import QDialog, QPlainTextEdit

from ui.Ui_floatingdialog import Ui_floating_dialog


def create_floating_dialog(qtbot) -> tuple[QDialog, Ui_floating_dialog]:
    dialog = QDialog()
    ui = Ui_floating_dialog()
    ui.setupUi(dialog)
    qtbot.addWidget(dialog)
    return dialog, ui


def test_floating_dialog_uses_semantic_component_names(qtbot) -> None:
    dialog, ui = create_floating_dialog(qtbot)

    assert dialog.objectName() == "floating_dialog"
    assert ui.main_layout.objectName() == "main_layout"
    assert (
        ui.translation_direction_widget.objectName()
        == "translation_direction_widget"
    )
    assert (
        ui.target_language_combo_box.objectName()
        == "target_language_combo_box"
    )
    assert ui.source_text_edit.objectName() == "source_text_edit"
    assert ui.translation_output_widget.objectName() == (
        "translation_output_widget"
    )
    assert ui.translation_text_edit.objectName() == "translation_text_edit"
    assert ui.copy_translation_push_button.objectName() == (
        "copy_translation_push_button"
    )


def test_floating_dialog_uses_editable_source_and_read_only_translation(
    qtbot,
) -> None:
    _dialog, ui = create_floating_dialog(qtbot)

    assert isinstance(ui.source_text_edit, QPlainTextEdit)
    assert isinstance(ui.translation_text_edit, QPlainTextEdit)
    assert not ui.source_text_edit.isReadOnly()
    assert ui.translation_text_edit.isReadOnly()
    assert ui.translation_direction_label.text() == "翻译方向"
    assert ui.source_text_label.text() == "原文"
    assert ui.translation_text_label.text() == "译文"


def test_floating_dialog_uses_compact_direction_control(qtbot) -> None:
    dialog, ui = create_floating_dialog(qtbot)
    dialog.ensurePolished()
    dialog.layout().activate()

    assert ui.target_language_combo_box.height() <= 30
    assert "chevron-down.svg" in dialog.styleSheet()
    assert "QComboBox#target_language_combo_box::down-arrow" in (
        dialog.styleSheet()
    )
    assert not ui.translation_direction_icon_label.pixmap().isNull()
    assert ui.target_language_combo_box.itemText(0) == "简体中文"
    assert ui.target_language_combo_box.itemText(1) == "英文"


def test_translation_output_has_borderless_copy_button(qtbot) -> None:
    dialog, ui = create_floating_dialog(qtbot)
    dialog.ensurePolished()
    dialog.layout().activate()

    assert ui.translation_output_widget.styleSheet() == ""
    assert ui.copy_translation_push_button.toolTip() == "复制译文"
    assert ui.copy_translation_push_button.accessibleName() == "复制译文"
    assert not ui.copy_translation_push_button.icon().isNull()
    assert ui.copy_translation_push_button.width() <= 28
    assert "QWidget#translation_output_widget" in dialog.styleSheet()
    assert "QPushButton#copy_translation_push_button" in (
        dialog.styleSheet()
    )
