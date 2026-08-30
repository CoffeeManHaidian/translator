# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'floatingdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
    QHBoxLayout, QLabel, QPlainTextEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)
import resource_rc

class Ui_floating_dialog(object):
    def setupUi(self, floating_dialog):
        if not floating_dialog.objectName():
            floating_dialog.setObjectName(u"floating_dialog")
        floating_dialog.resize(420, 340)
        floating_dialog.setMinimumSize(QSize(360, 280))
        floating_dialog.setMaximumSize(QSize(560, 520))
        floating_dialog.setStyleSheet(u"QDialog#floating_dialog {\n"
"    color: #0F172A;\n"
"    background-color: #F8FAFC;\n"
"}\n"
"\n"
"QLabel#translation_direction_label,\n"
"QLabel#source_text_label,\n"
"QLabel#translation_text_label {\n"
"    color: #334155;\n"
"    font-size: 12px;\n"
"    font-weight: 600;\n"
"}\n"
"\n"
"QWidget#translation_direction_widget {\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"QLabel#source_language_label {\n"
"    min-height: 26px;\n"
"    max-height: 26px;\n"
"    padding: 0 10px;\n"
"    color: #475569;\n"
"    background-color: #F1F5F9;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"QLabel#translation_direction_icon_label {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}\n"
"\n"
"QComboBox#target_language_combo_box {\n"
"    min-height: 26px;\n"
"    max-height: 26px;\n"
"    padding: 0 28px 0 9px;\n"
"    color: #0F172A;\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #CBD5E1;\n"
"    border-r"
                        "adius: 7px;\n"
"}\n"
"\n"
"QComboBox#target_language_combo_box:hover {\n"
"    border-color: #94A3B8;\n"
"}\n"
"\n"
"QComboBox#target_language_combo_box:focus {\n"
"    border-color: #2563EB;\n"
"}\n"
"\n"
"QComboBox#target_language_combo_box::drop-down {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position: top right;\n"
"    width: 26px;\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}\n"
"\n"
"QComboBox#target_language_combo_box::down-arrow {\n"
"    image: url(:/settings/icons/chevron-down.svg);\n"
"    width: 10px;\n"
"    height: 10px;\n"
"}\n"
"\n"
"QComboBox#target_language_combo_box QAbstractItemView {\n"
"    padding: 4px;\n"
"    color: #0F172A;\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #CBD5E1;\n"
"    outline: none;\n"
"    selection-color: #1E3A8A;\n"
"    selection-background-color: #EFF6FF;\n"
"}\n"
"\n"
"QComboBox#target_language_combo_box QAbstractItemView::item {\n"
"    min-height: 26px;\n"
"    padding: 0 8px;\n"
"}\n"
"\n"
"QPlainTextEdit#sou"
                        "rce_text_edit {\n"
"    padding: 9px 10px;\n"
"    color: #0F172A;\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 8px;\n"
"    selection-color: #1E3A8A;\n"
"    selection-background-color: #DBEAFE;\n"
"}\n"
"\n"
"QWidget#translation_output_widget {\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E2E8F0;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"QPlainTextEdit#translation_text_edit {\n"
"    padding: 9px 10px;\n"
"    color: #0F172A;\n"
"    background-color: #FFFFFF;\n"
"    border: none;\n"
"    border-radius: 7px;\n"
"    selection-color: #1E3A8A;\n"
"    selection-background-color: #DBEAFE;\n"
"}\n"
"\n"
"QPlainTextEdit#source_text_edit:hover,\n"
"QWidget#translation_output_widget:hover {\n"
"    border-color: #94A3B8;\n"
"}\n"
"\n"
"QPlainTextEdit#source_text_edit:focus {\n"
"    border-color: #2563EB;\n"
"}\n"
"\n"
"QPushButton#copy_translation_push_button {\n"
"    min-width: 28px;\n"
"    max-width: 28px;\n"
"    min-height: 28px;\n"
"    max-"
                        "height: 28px;\n"
"    padding: 0;\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"QPushButton#copy_translation_push_button:hover {\n"
"    background-color: #F1F5F9;\n"
"}\n"
"\n"
"QPushButton#copy_translation_push_button:pressed {\n"
"    background-color: #E2E8F0;\n"
"}\n"
"\n"
"QPushButton#copy_translation_push_button:focus {\n"
"    background-color: #EFF6FF;\n"
"}\n"
"\n"
"QPlainTextEdit QScrollBar:vertical {\n"
"    width: 8px;\n"
"    margin: 4px 1px;\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"QPlainTextEdit QScrollBar::handle:vertical {\n"
"    min-height: 20px;\n"
"    background-color: #CBD5E1;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QPlainTextEdit QScrollBar::handle:vertical:hover {\n"
"    background-color: #94A3B8;\n"
"}\n"
"\n"
"QPlainTextEdit QScrollBar::add-line:vertical,\n"
"QPlainTextEdit QScrollBar::sub-line:vertical {\n"
"    height: 0;\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}\n"
"\n"
"QPlainText"
                        "Edit QScrollBar::add-page:vertical,\n"
"QPlainTextEdit QScrollBar::sub-page:vertical {\n"
"    background-color: transparent;\n"
"}")
        floating_dialog.setSizeGripEnabled(True)
        self.main_layout = QVBoxLayout(floating_dialog)
        self.main_layout.setSpacing(12)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(16, 14, 16, 16)
        self.translation_direction_layout = QVBoxLayout()
        self.translation_direction_layout.setSpacing(4)
        self.translation_direction_layout.setObjectName(u"translation_direction_layout")
        self.translation_direction_label = QLabel(floating_dialog)
        self.translation_direction_label.setObjectName(u"translation_direction_label")

        self.translation_direction_layout.addWidget(self.translation_direction_label)

        self.translation_direction_widget = QWidget(floating_dialog)
        self.translation_direction_widget.setObjectName(u"translation_direction_widget")
        self.translation_direction_control_layout = QHBoxLayout(self.translation_direction_widget)
        self.translation_direction_control_layout.setSpacing(8)
        self.translation_direction_control_layout.setObjectName(u"translation_direction_control_layout")
        self.translation_direction_control_layout.setContentsMargins(8, 5, 8, 5)
        self.source_language_label = QLabel(self.translation_direction_widget)
        self.source_language_label.setObjectName(u"source_language_label")

        self.translation_direction_control_layout.addWidget(self.source_language_label)

        self.translation_direction_icon_label = QLabel(self.translation_direction_widget)
        self.translation_direction_icon_label.setObjectName(u"translation_direction_icon_label")
        self.translation_direction_icon_label.setMinimumSize(QSize(16, 16))
        self.translation_direction_icon_label.setMaximumSize(QSize(16, 16))
        self.translation_direction_icon_label.setPixmap(QPixmap(u":/mainwindow/icons/arrow-right-left.svg"))
        self.translation_direction_icon_label.setScaledContents(True)

        self.translation_direction_control_layout.addWidget(self.translation_direction_icon_label)

        self.target_language_combo_box = QComboBox(self.translation_direction_widget)
        self.target_language_combo_box.addItem("")
        self.target_language_combo_box.setObjectName(u"target_language_combo_box")

        self.translation_direction_control_layout.addWidget(self.target_language_combo_box)


        self.translation_direction_layout.addWidget(self.translation_direction_widget)


        self.main_layout.addLayout(self.translation_direction_layout)

        self.source_section_layout = QVBoxLayout()
        self.source_section_layout.setSpacing(4)
        self.source_section_layout.setObjectName(u"source_section_layout")
        self.source_text_label = QLabel(floating_dialog)
        self.source_text_label.setObjectName(u"source_text_label")

        self.source_section_layout.addWidget(self.source_text_label)

        self.source_text_edit = QPlainTextEdit(floating_dialog)
        self.source_text_edit.setObjectName(u"source_text_edit")
        self.source_text_edit.setMinimumSize(QSize(0, 72))
        self.source_text_edit.setFrameShape(QFrame.Shape.NoFrame)
        self.source_text_edit.setReadOnly(True)

        self.source_section_layout.addWidget(self.source_text_edit)


        self.main_layout.addLayout(self.source_section_layout)

        self.translation_section_layout = QVBoxLayout()
        self.translation_section_layout.setSpacing(4)
        self.translation_section_layout.setObjectName(u"translation_section_layout")
        self.translation_text_label = QLabel(floating_dialog)
        self.translation_text_label.setObjectName(u"translation_text_label")

        self.translation_section_layout.addWidget(self.translation_text_label)

        self.translation_output_widget = QWidget(floating_dialog)
        self.translation_output_widget.setObjectName(u"translation_output_widget")
        self.translation_output_widget.setMinimumSize(QSize(0, 92))
        self.translation_output_layout = QVBoxLayout(self.translation_output_widget)
        self.translation_output_layout.setSpacing(0)
        self.translation_output_layout.setObjectName(u"translation_output_layout")
        self.translation_output_layout.setContentsMargins(0, 0, 4, 4)
        self.translation_text_edit = QPlainTextEdit(self.translation_output_widget)
        self.translation_text_edit.setObjectName(u"translation_text_edit")
        self.translation_text_edit.setMinimumSize(QSize(0, 56))
        self.translation_text_edit.setFrameShape(QFrame.Shape.NoFrame)
        self.translation_text_edit.setReadOnly(True)

        self.translation_output_layout.addWidget(self.translation_text_edit)

        self.copy_translation_push_button = QPushButton(self.translation_output_widget)
        self.copy_translation_push_button.setObjectName(u"copy_translation_push_button")
        icon = QIcon()
        icon.addFile(u":/mainwindow/icons/copy.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.copy_translation_push_button.setIcon(icon)
        self.copy_translation_push_button.setIconSize(QSize(16, 16))
        self.copy_translation_push_button.setAutoDefault(False)

        self.translation_output_layout.addWidget(self.copy_translation_push_button, 0, Qt.AlignmentFlag.AlignRight)

        self.translation_output_layout.setStretch(0, 1)

        self.translation_section_layout.addWidget(self.translation_output_widget)


        self.main_layout.addLayout(self.translation_section_layout)

        self.main_layout.setStretch(1, 1)
        self.main_layout.setStretch(2, 1)

        self.retranslateUi(floating_dialog)

        self.copy_translation_push_button.setDefault(False)


        QMetaObject.connectSlotsByName(floating_dialog)
    # setupUi

    def retranslateUi(self, floating_dialog):
        floating_dialog.setWindowTitle(QCoreApplication.translate("floating_dialog", u"\u7ffb\u8bd1\u7ed3\u679c", None))
        self.translation_direction_label.setText(QCoreApplication.translate("floating_dialog", u"\u7ffb\u8bd1\u65b9\u5411", None))
        self.source_language_label.setText(QCoreApplication.translate("floating_dialog", u"\u81ea\u52a8\u68c0\u6d4b", None))
#if QT_CONFIG(accessibility)
        self.translation_direction_icon_label.setAccessibleName(QCoreApplication.translate("floating_dialog", u"\u7ffb\u8bd1\u4e3a", None))
#endif // QT_CONFIG(accessibility)
        self.target_language_combo_box.setItemText(0, QCoreApplication.translate("floating_dialog", u"\u4e2d\u6587", None))

#if QT_CONFIG(accessibility)
        self.target_language_combo_box.setAccessibleName(QCoreApplication.translate("floating_dialog", u"\u76ee\u6807\u8bed\u8a00", None))
#endif // QT_CONFIG(accessibility)
        self.source_text_label.setText(QCoreApplication.translate("floating_dialog", u"\u539f\u6587", None))
#if QT_CONFIG(accessibility)
        self.source_text_edit.setAccessibleName(QCoreApplication.translate("floating_dialog", u"\u539f\u6587", None))
#endif // QT_CONFIG(accessibility)
        self.source_text_edit.setPlaceholderText(QCoreApplication.translate("floating_dialog", u"\u7b49\u5f85\u539f\u6587\u2026", None))
        self.translation_text_label.setText(QCoreApplication.translate("floating_dialog", u"\u8bd1\u6587", None))
#if QT_CONFIG(accessibility)
        self.translation_text_edit.setAccessibleName(QCoreApplication.translate("floating_dialog", u"\u8bd1\u6587", None))
#endif // QT_CONFIG(accessibility)
        self.translation_text_edit.setPlaceholderText(QCoreApplication.translate("floating_dialog", u"\u7b49\u5f85\u8bd1\u6587\u2026", None))
#if QT_CONFIG(tooltip)
        self.copy_translation_push_button.setToolTip(QCoreApplication.translate("floating_dialog", u"\u590d\u5236\u8bd1\u6587", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.copy_translation_push_button.setAccessibleName(QCoreApplication.translate("floating_dialog", u"\u590d\u5236\u8bd1\u6587", None))
#endif // QT_CONFIG(accessibility)
        self.copy_translation_push_button.setText("")
    # retranslateUi

