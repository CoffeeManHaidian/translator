# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settingsdialog.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHBoxLayout,
    QKeySequenceEdit, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)
import resource_rc

class Ui_settings_Dialog(object):
    def setupUi(self, settings_Dialog):
        if not settings_Dialog.objectName():
            settings_Dialog.setObjectName(u"settings_Dialog")
        settings_Dialog.resize(460, 390)
        settings_Dialog.setMinimumSize(QSize(440, 0))
        settings_Dialog.setStyleSheet(u"QDialog#settings_Dialog {\n"
"    background-color: #F8FAFC;\n"
"    color: #0F172A;\n"
"}\n"
"\n"
"QLabel#title_label {\n"
"    color: #0F172A;\n"
"    font-size: 18px;\n"
"    font-weight: 600;\n"
"}\n"
"\n"
"QLabel#description_label,\n"
"QLabel#api_key_hint_label {\n"
"    color: #64748B;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QLabel#provider_label,\n"
"QLabel#model_label,\n"
"QLabel#api_key_label,\n"
"QLabel#base_url_label,\n"
"QLabel#hotkey_label {\n"
"    color: #334155;\n"
"    font-size: 12px;\n"
"    font-weight: 500;\n"
"}\n"
"\n"
"QWidget#form_widget,\n"
"QWidget#advanced_widget {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}\n"
"\n"
"QLineEdit#api_key_lineEdit,\n"
"QLineEdit#base_url_lineEdit,\n"
"QComboBox#provider_comboBox,\n"
"QComboBox#model_comboBox,\n"
"QKeySequenceEdit#hotkey_keySequenceEdit {\n"
"    min-height: 26px;\n"
"    max-height: 26px;\n"
"    padding: 0 10px;\n"
"    background-color: #FFFFFF;\n"
"    color: #0F172A;\n"
"    border: 1px solid #CBD5E1;\n"
"    "
                        "border-radius: 7px;\n"
"}\n"
"\n"
"QComboBox#provider_comboBox,\n"
"QComboBox#model_comboBox {\n"
"    padding: 0 28px 0 9px;\n"
"}\n"
"\n"
"QLineEdit#api_key_lineEdit:hover,\n"
"QLineEdit#base_url_lineEdit:hover,\n"
"QComboBox#provider_comboBox:hover,\n"
"QComboBox#model_comboBox:hover,\n"
"QKeySequenceEdit#hotkey_keySequenceEdit:hover {\n"
"    border-color: #94A3B8;\n"
"}\n"
"\n"
"QLineEdit#api_key_lineEdit:focus,\n"
"QLineEdit#base_url_lineEdit:focus,\n"
"QComboBox#provider_comboBox:focus,\n"
"QComboBox#model_comboBox:focus,\n"
"QKeySequenceEdit#hotkey_keySequenceEdit:focus {\n"
"    border-color: #2563EB;\n"
"}\n"
"\n"
"QComboBox#provider_comboBox::drop-down,\n"
"QComboBox#model_comboBox::drop-down {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position: top right;\n"
"    width: 26px;\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}\n"
"\n"
"QComboBox#provider_comboBox::down-arrow,\n"
"QComboBox#model_comboBox::down-arrow {\n"
"    image: url(:/settings/icons/chevron-down.svg);"
                        "\n"
"    width: 10px;\n"
"    height: 10px;\n"
"}\n"
"\n"
"QComboBox#provider_comboBox QAbstractItemView,\n"
"QComboBox#model_comboBox QAbstractItemView {\n"
"    padding: 4px;\n"
"    color: #0F172A;\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #CBD5E1;\n"
"    outline: none;\n"
"    selection-color: #1E3A8A;\n"
"    selection-background-color: #EFF6FF;\n"
"}\n"
"\n"
"QComboBox#provider_comboBox QAbstractItemView::item,\n"
"QComboBox#model_comboBox QAbstractItemView::item {\n"
"    min-height: 26px;\n"
"    padding: 0 8px;\n"
"}\n"
"\n"
"QPushButton#visibility_pushButton,\n"
"QPushButton#refresh_models_pushButton {\n"
"    min-width: 28px;\n"
"    max-width: 28px;\n"
"    min-height: 28px;\n"
"    max-height: 28px;\n"
"    padding: 0;\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"}\n"
"\n"
"QPushButton#visibility_pushButton:hover,\n"
"QPushButton#refresh_models_pushButton:hover {\n"
"    background-color: #EAF0F7;\n"
"}\n"
"\n"
"QPushButton#visibi"
                        "lity_pushButton:pressed,\n"
"QPushButton#refresh_models_pushButton:pressed {\n"
"    background-color: #E2E8F0;\n"
"}\n"
"\n"
"QPushButton#advanced_toggleButton {\n"
"    min-height: 24px;\n"
"    max-height: 24px;\n"
"    padding: 0;\n"
"    color: #64748B;\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    text-align: left;\n"
"}\n"
"\n"
"QPushButton#advanced_toggleButton:hover,\n"
"QPushButton#advanced_toggleButton:checked {\n"
"    color: #2563EB;\n"
"}\n"
"\n"
"QPushButton#test_pushButton,\n"
"QPushButton#cancel_pushButton {\n"
"    min-height: 26px;\n"
"    max-height: 26px;\n"
"    padding: 0 10px;\n"
"    color: #334155;\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #CBD5E1;\n"
"    border-radius: 7px;\n"
"}\n"
"\n"
"QPushButton#test_pushButton:hover,\n"
"QPushButton#cancel_pushButton:hover {\n"
"    background-color: #F8FAFC;\n"
"    border-color: #94A3B8;\n"
"}\n"
"\n"
"QPushButton#test_pushButton:pressed,\n"
"QPushButton#cancel_pushButton:pressed {\n"
"    background"
                        "-color: #F1F5F9;\n"
"}\n"
"\n"
"QPushButton#save_pushButton {\n"
"    min-height: 26px;\n"
"    max-height: 26px;\n"
"    padding: 0 14px;\n"
"    color: #FFFFFF;\n"
"    background-color: #2563EB;\n"
"    border: 1px solid #2563EB;\n"
"    border-radius: 7px;\n"
"}\n"
"\n"
"QPushButton#save_pushButton:hover {\n"
"    background-color: #1D4ED8;\n"
"    border-color: #1D4ED8;\n"
"}\n"
"\n"
"QPushButton#save_pushButton:pressed {\n"
"    background-color: #1E40AF;\n"
"    border-color: #1E40AF;\n"
"}\n"
"\n"
"QPushButton#save_pushButton:focus,\n"
"QPushButton#cancel_pushButton:focus,\n"
"QPushButton#test_pushButton:focus,\n"
"QPushButton#refresh_models_pushButton:focus,\n"
"QPushButton#visibility_pushButton:focus {\n"
"    border: 1px solid #2563EB;\n"
"}\n"
"\n"
"QPushButton#save_pushButton:disabled,\n"
"QPushButton#cancel_pushButton:disabled,\n"
"QPushButton#test_pushButton:disabled,\n"
"QPushButton#refresh_models_pushButton:disabled {\n"
"    color: #94A3B8;\n"
"    background-color: #F1F5F9;\n"
"    border-co"
                        "lor: #E2E8F0;\n"
"}")
        self.verticalLayout = QVBoxLayout(settings_Dialog)
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, 16, 20, 14)
        self.title_label = QLabel(settings_Dialog)
        self.title_label.setObjectName(u"title_label")

        self.verticalLayout.addWidget(self.title_label)

        self.description_label = QLabel(settings_Dialog)
        self.description_label.setObjectName(u"description_label")

        self.verticalLayout.addWidget(self.description_label)

        self.form_widget = QWidget(settings_Dialog)
        self.form_widget.setObjectName(u"form_widget")
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setSpacing(12)
        self.form_layout.setObjectName(u"form_layout")
        self.form_layout.setContentsMargins(0, 6, 0, 0)
        self.provider_field_layout = QVBoxLayout()
        self.provider_field_layout.setSpacing(4)
        self.provider_field_layout.setObjectName(u"provider_field_layout")
        self.provider_label = QLabel(self.form_widget)
        self.provider_label.setObjectName(u"provider_label")

        self.provider_field_layout.addWidget(self.provider_label)

        self.provider_comboBox = QComboBox(self.form_widget)
        self.provider_comboBox.setObjectName(u"provider_comboBox")
        self.provider_comboBox.setIconSize(QSize(16, 16))

        self.provider_field_layout.addWidget(self.provider_comboBox)


        self.form_layout.addLayout(self.provider_field_layout)

        self.model_field_layout = QVBoxLayout()
        self.model_field_layout.setSpacing(4)
        self.model_field_layout.setObjectName(u"model_field_layout")
        self.model_label = QLabel(self.form_widget)
        self.model_label.setObjectName(u"model_label")

        self.model_field_layout.addWidget(self.model_label)

        self.model_control_layout = QHBoxLayout()
        self.model_control_layout.setSpacing(6)
        self.model_control_layout.setObjectName(u"model_control_layout")
        self.model_comboBox = QComboBox(self.form_widget)
        self.model_comboBox.setObjectName(u"model_comboBox")

        self.model_control_layout.addWidget(self.model_comboBox)

        self.refresh_models_pushButton = QPushButton(self.form_widget)
        self.refresh_models_pushButton.setObjectName(u"refresh_models_pushButton")
        icon = QIcon()
        icon.addFile(u":/mainwindow/icons/rotate-ccw-clock.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.refresh_models_pushButton.setIcon(icon)
        self.refresh_models_pushButton.setIconSize(QSize(16, 16))

        self.model_control_layout.addWidget(self.refresh_models_pushButton)


        self.model_field_layout.addLayout(self.model_control_layout)


        self.form_layout.addLayout(self.model_field_layout)

        self.api_key_field_layout = QVBoxLayout()
        self.api_key_field_layout.setSpacing(4)
        self.api_key_field_layout.setObjectName(u"api_key_field_layout")
        self.api_key_label = QLabel(self.form_widget)
        self.api_key_label.setObjectName(u"api_key_label")

        self.api_key_field_layout.addWidget(self.api_key_label)

        self.api_key_control_layout = QHBoxLayout()
        self.api_key_control_layout.setSpacing(6)
        self.api_key_control_layout.setObjectName(u"api_key_control_layout")
        self.api_key_lineEdit = QLineEdit(self.form_widget)
        self.api_key_lineEdit.setObjectName(u"api_key_lineEdit")
        self.api_key_lineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.api_key_control_layout.addWidget(self.api_key_lineEdit)

        self.visibility_pushButton = QPushButton(self.form_widget)
        self.visibility_pushButton.setObjectName(u"visibility_pushButton")
        icon1 = QIcon()
        icon1.addFile(u":/settings/icons/eye.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.visibility_pushButton.setIcon(icon1)
        self.visibility_pushButton.setIconSize(QSize(16, 16))
        self.visibility_pushButton.setCheckable(True)

        self.api_key_control_layout.addWidget(self.visibility_pushButton)

        self.test_pushButton = QPushButton(self.form_widget)
        self.test_pushButton.setObjectName(u"test_pushButton")

        self.api_key_control_layout.addWidget(self.test_pushButton)

        self.status_label = QLabel(self.form_widget)
        self.status_label.setObjectName(u"status_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status_label.sizePolicy().hasHeightForWidth())
        self.status_label.setSizePolicy(sizePolicy)

        self.api_key_control_layout.addWidget(self.status_label)


        self.api_key_field_layout.addLayout(self.api_key_control_layout)

        self.api_key_hint_label = QLabel(self.form_widget)
        self.api_key_hint_label.setObjectName(u"api_key_hint_label")

        self.api_key_field_layout.addWidget(self.api_key_hint_label)


        self.form_layout.addLayout(self.api_key_field_layout)

        self.hotkey_field_layout = QVBoxLayout()
        self.hotkey_field_layout.setSpacing(4)
        self.hotkey_field_layout.setObjectName(u"hotkey_field_layout")
        self.hotkey_label = QLabel(self.form_widget)
        self.hotkey_label.setObjectName(u"hotkey_label")

        self.hotkey_field_layout.addWidget(self.hotkey_label)

        self.hotkey_keySequenceEdit = QKeySequenceEdit(self.form_widget)
        self.hotkey_keySequenceEdit.setObjectName(u"hotkey_keySequenceEdit")
        self.hotkey_keySequenceEdit.setMaximumSequenceLength(1)
        self.hotkey_keySequenceEdit.setClearButtonEnabled(True)

        self.hotkey_field_layout.addWidget(self.hotkey_keySequenceEdit)


        self.form_layout.addLayout(self.hotkey_field_layout)

        self.advanced_toggleButton = QPushButton(self.form_widget)
        self.advanced_toggleButton.setObjectName(u"advanced_toggleButton")
        icon2 = QIcon()
        icon2.addFile(u":/settings/icons/chevron-down.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.advanced_toggleButton.setIcon(icon2)
        self.advanced_toggleButton.setIconSize(QSize(14, 14))
        self.advanced_toggleButton.setCheckable(True)

        self.form_layout.addWidget(self.advanced_toggleButton)

        self.advanced_widget = QWidget(self.form_widget)
        self.advanced_widget.setObjectName(u"advanced_widget")
        self.advanced_layout = QVBoxLayout(self.advanced_widget)
        self.advanced_layout.setSpacing(4)
        self.advanced_layout.setObjectName(u"advanced_layout")
        self.advanced_layout.setContentsMargins(0, 0, 0, 0)
        self.base_url_label = QLabel(self.advanced_widget)
        self.base_url_label.setObjectName(u"base_url_label")

        self.advanced_layout.addWidget(self.base_url_label)

        self.base_url_lineEdit = QLineEdit(self.advanced_widget)
        self.base_url_lineEdit.setObjectName(u"base_url_lineEdit")

        self.advanced_layout.addWidget(self.base_url_lineEdit)


        self.form_layout.addWidget(self.advanced_widget)


        self.verticalLayout.addWidget(self.form_widget)

        self.verticalSpacer = QSpacerItem(20, 4, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(8)
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.buttonLayout.setContentsMargins(-1, 4, -1, -1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.horizontalSpacer)

        self.save_pushButton = QPushButton(settings_Dialog)
        self.save_pushButton.setObjectName(u"save_pushButton")

        self.buttonLayout.addWidget(self.save_pushButton)

        self.cancel_pushButton = QPushButton(settings_Dialog)
        self.cancel_pushButton.setObjectName(u"cancel_pushButton")

        self.buttonLayout.addWidget(self.cancel_pushButton)


        self.verticalLayout.addLayout(self.buttonLayout)


        self.retranslateUi(settings_Dialog)

        QMetaObject.connectSlotsByName(settings_Dialog)
    # setupUi

    def retranslateUi(self, settings_Dialog):
        settings_Dialog.setWindowTitle(QCoreApplication.translate("settings_Dialog", u"Dialog", None))
        self.title_label.setText(QCoreApplication.translate("settings_Dialog", u"\u8bbe\u7f6e", None))
        self.description_label.setText(QCoreApplication.translate("settings_Dialog", u"\u914d\u7f6e\u7ffb\u8bd1\u670d\u52a1\u4e0e\u5168\u5c40\u5feb\u6377\u952e", None))
        self.provider_label.setText(QCoreApplication.translate("settings_Dialog", u"\u670d\u52a1\u5546", None))
        self.model_label.setText(QCoreApplication.translate("settings_Dialog", u"\u6a21\u578b", None))
#if QT_CONFIG(tooltip)
        self.refresh_models_pushButton.setToolTip(QCoreApplication.translate("settings_Dialog", u"\u5237\u65b0\u6a21\u578b\u5217\u8868", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.refresh_models_pushButton.setAccessibleName(QCoreApplication.translate("settings_Dialog", u"\u5237\u65b0\u6a21\u578b\u5217\u8868", None))
#endif // QT_CONFIG(accessibility)
        self.refresh_models_pushButton.setText("")
        self.api_key_label.setText(QCoreApplication.translate("settings_Dialog", u"API Key", None))
#if QT_CONFIG(accessibility)
        self.api_key_lineEdit.setAccessibleName(QCoreApplication.translate("settings_Dialog", u"API Key", None))
#endif // QT_CONFIG(accessibility)
        self.api_key_lineEdit.setPlaceholderText(QCoreApplication.translate("settings_Dialog", u"\u8bf7\u8f93\u5165 API Key", None))
#if QT_CONFIG(tooltip)
        self.visibility_pushButton.setToolTip(QCoreApplication.translate("settings_Dialog", u"\u663e\u793a API Key", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.visibility_pushButton.setAccessibleName(QCoreApplication.translate("settings_Dialog", u"\u663e\u793a API Key", None))
#endif // QT_CONFIG(accessibility)
        self.visibility_pushButton.setText("")
        self.test_pushButton.setText(QCoreApplication.translate("settings_Dialog", u"\u6d4b\u8bd5\u8fde\u63a5", None))
        self.status_label.setText("")
        self.api_key_hint_label.setText(QCoreApplication.translate("settings_Dialog", u"\u5bc6\u94a5\u4ec5\u4fdd\u5b58\u5728\u5f53\u524d\u8bbe\u5907", None))
        self.hotkey_label.setText(QCoreApplication.translate("settings_Dialog", u"\u5168\u5c40\u5feb\u6377\u952e", None))
#if QT_CONFIG(tooltip)
        self.advanced_toggleButton.setToolTip(QCoreApplication.translate("settings_Dialog", u"\u5c55\u5f00\u9ad8\u7ea7\u8bbe\u7f6e", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.advanced_toggleButton.setAccessibleName(QCoreApplication.translate("settings_Dialog", u"\u5c55\u5f00\u9ad8\u7ea7\u8bbe\u7f6e", None))
#endif // QT_CONFIG(accessibility)
        self.advanced_toggleButton.setText(QCoreApplication.translate("settings_Dialog", u"\u9ad8\u7ea7\u8bbe\u7f6e", None))
        self.base_url_label.setText(QCoreApplication.translate("settings_Dialog", u"API \u5730\u5740", None))
        self.save_pushButton.setText(QCoreApplication.translate("settings_Dialog", u"\u4fdd\u5b58", None))
        self.cancel_pushButton.setText(QCoreApplication.translate("settings_Dialog", u"\u53d6\u6d88", None))
    # retranslateUi
