# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)
import resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 500)
        MainWindow.setMinimumSize(QSize(680, 420))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.origin_comboBox = QComboBox(self.centralwidget)
        self.origin_comboBox.addItem("")
        self.origin_comboBox.addItem("")
        self.origin_comboBox.addItem("")
        self.origin_comboBox.setObjectName(u"origin_comboBox")

        self.horizontalLayout_3.addWidget(self.origin_comboBox)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(36, 36))
        self.label.setMaximumSize(QSize(36, 36))
        self.label.setTextFormat(Qt.TextFormat.AutoText)
        self.label.setPixmap(QPixmap(u":/mainwindow/icons/arrow-right-left.svg"))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.label)

        self.translation_comboBox = QComboBox(self.centralwidget)
        self.translation_comboBox.addItem("")
        self.translation_comboBox.addItem("")
        self.translation_comboBox.setObjectName(u"translation_comboBox")

        self.horizontalLayout_3.addWidget(self.translation_comboBox)

        self.history_pushButton = QPushButton(self.centralwidget)
        self.history_pushButton.setObjectName(u"history_pushButton")
        self.history_pushButton.setStyleSheet(u"QPushButton#history_pushButton {\n"
"    min-width: 36px;\n"
"    max-width: 36px;\n"
"    min-height: 36px;\n"
"    max-height: 36px;\n"
"\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"QPushButton#history_pushButton:hover {\n"
"    background-color: #F1F5F9;\n"
"}\n"
"\n"
"QPushButton#history_pushButton:pressed {\n"
"    background-color: #E2E8F0;\n"
"}\n"
"\n"
"QPushButton#history_pushButton:focus {\n"
"    border: 1px solid #2563EB;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/mainwindow/icons/rotate-ccw-clock.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.history_pushButton.setIcon(icon)
        self.history_pushButton.setIconSize(QSize(18, 18))

        self.horizontalLayout_3.addWidget(self.history_pushButton)

        self.settings_pushButton = QPushButton(self.centralwidget)
        self.settings_pushButton.setObjectName(u"settings_pushButton")
        self.settings_pushButton.setStyleSheet(u"QPushButton#settings_pushButton {\n"
"    min-width: 36px;\n"
"    max-width: 36px;\n"
"    min-height: 36px;\n"
"    max-height: 36px;\n"
"\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"QPushButton#settings_pushButton:hover {\n"
"    background-color: #F1F5F9;\n"
"}\n"
"\n"
"QPushButton#settings_pushButton:pressed {\n"
"    background-color: #E2E8F0;\n"
"}\n"
"\n"
"QPushButton#settings_pushButton:focus {\n"
"    border: 1px solid #2563EB;\n"
"}\n"
"\n"
"QPushButton#settings_pushButton:disabled {\n"
"    background-color: transparent;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/mainwindow/icons/settings.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.settings_pushButton.setIcon(icon1)
        self.settings_pushButton.setIconSize(QSize(18, 18))

        self.horizontalLayout_3.addWidget(self.settings_pushButton)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.origin_widget = QWidget(self.centralwidget)
        self.origin_widget.setObjectName(u"origin_widget")
        self.origin_widget.setStyleSheet(u"QWidget#origin_widget {\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E4E7EB;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPlainTextEdit#origin_plainTextEdit {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    padding: 4px;\n"
"    color: #0F172A;\n"
"}\n"
"")
        self.verticalLayout_3 = QVBoxLayout(self.origin_widget)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.origin_plainTextEdit = QPlainTextEdit(self.origin_widget)
        self.origin_plainTextEdit.setObjectName(u"origin_plainTextEdit")

        self.verticalLayout_3.addWidget(self.origin_plainTextEdit)


        self.horizontalLayout.addWidget(self.origin_widget)

        self.translation_widget = QWidget(self.centralwidget)
        self.translation_widget.setObjectName(u"translation_widget")
        self.translation_widget.setStyleSheet(u"QWidget#translation_widget {\n"
"    background-color: #FFFFFF;\n"
"    border: 1px solid #E4E7EB;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPlainTextEdit#translation_plainTextEdit {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    padding: 4px;\n"
"    color: #0F172A;\n"
"}\n"
"\n"
"QPushButton#copy_pushButton {\n"
"    min-width: 36px;\n"
"    max-width: 36px;\n"
"    min-height: 36px;\n"
"    max-height: 36px;\n"
"\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"QPushButton#copy_pushButton:hover {\n"
"    background-color: #F1F5F9;\n"
"}\n"
"\n"
"QPushButton#copy_pushButton:pressed {\n"
"    background-color: #E2E8F0;\n"
"}\n"
"\n"
"QPushButton#copy_pushButton:focus {\n"
"    border: 1px solid #2563EB;\n"
"}\n"
"\n"
"QPushButton#copy_pushButton:disabled {\n"
"    background-color: transparent;\n"
"}")
        self.verticalLayout_2 = QVBoxLayout(self.translation_widget)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(12, 12, 12, 8)
        self.translation_plainTextEdit = QPlainTextEdit(self.translation_widget)
        self.translation_plainTextEdit.setObjectName(u"translation_plainTextEdit")
        self.translation_plainTextEdit.setStyleSheet(u"")
        self.translation_plainTextEdit.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.translation_plainTextEdit)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.copy_pushButton = QPushButton(self.translation_widget)
        self.copy_pushButton.setObjectName(u"copy_pushButton")
        self.copy_pushButton.setEnabled(False)
        icon2 = QIcon()
        icon2.addFile(u":/mainwindow/icons/copy.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.copy_pushButton.setIcon(icon2)
        self.copy_pushButton.setIconSize(QSize(18, 18))
        self.copy_pushButton.setCheckable(True)

        self.horizontalLayout_4.addWidget(self.copy_pushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)


        self.horizontalLayout.addWidget(self.translation_widget)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        MainWindow.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        MainWindow.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.origin_comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u8bc6\u522b\u8bed\u8a00", None))
        self.origin_comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"\u82f1\u8bed", None))
        self.origin_comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"\u7b80\u4f53\u4e2d\u6587", None))

        self.label.setText("")
        self.translation_comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"\u7b80\u4f53\u4e2d\u6587", None))
        self.translation_comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"\u82f1\u8bed", None))

#if QT_CONFIG(tooltip)
        self.history_pushButton.setToolTip(QCoreApplication.translate("MainWindow", u"\u7ffb\u8bd1\u5386\u53f2", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.history_pushButton.setAccessibleName(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u7ffb\u8bd1\u5386\u53f2", None))
#endif // QT_CONFIG(accessibility)
        self.history_pushButton.setText("")
#if QT_CONFIG(tooltip)
        self.settings_pushButton.setToolTip(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.settings_pushButton.setAccessibleName(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u8bbe\u7f6e", None))
#endif // QT_CONFIG(accessibility)
        self.settings_pushButton.setText("")
#if QT_CONFIG(tooltip)
        self.copy_pushButton.setToolTip(QCoreApplication.translate("MainWindow", u"\u590d\u5236\u8bd1\u6587", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.copy_pushButton.setAccessibleName(QCoreApplication.translate("MainWindow", u"\u590d\u5236\u8bd1\u6587", None))
#endif // QT_CONFIG(accessibility)
        self.copy_pushButton.setText("")
    # retranslateUi
