import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class SystemTrayController(QObject):
    """有托盘入口时，关闭主窗口只隐藏；显式退出仍交给 Qt。"""

    def __init__(
        self,
        application: QApplication,
        window: "MainWindow",
    ) -> None:
        super().__init__(window)
        self._application = application
        self._window = window
        self._previous_quit_policy = application.quitOnLastWindowClosed()
        self._quitting = False
        self._closed = False
        self._background_notice_shown = False
        self._enabled = QSystemTrayIcon.isSystemTrayAvailable()
        self.tray_icon: QSystemTrayIcon | None = None

        if not self._enabled:
            window.statusBar().showMessage(
                "系统托盘不可用，关闭主窗口将退出程序",
                5000,
            )
            return

        self.menu = QMenu(window)
        self.show_action = self.menu.addAction("显示主窗口")
        self.floating_action = self.menu.addAction("打开悬浮窗")
        self.menu.addSeparator()
        self.quit_action = self.menu.addAction("退出")
        self.quit_action.setMenuRole(QAction.MenuRole.QuitRole)
        self.show_action.triggered.connect(window.show_main_window)
        self.floating_action.triggered.connect(window.open_floating_window)
        self.quit_action.triggered.connect(self.quit_application)

        icon = QIcon(":/app/icons/languages.svg")
        if sys.platform == "darwin":
            # 单色模板图标由 macOS 按菜单栏明暗主题着色。
            icon.setIsMask(True)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Trade Translator")
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self._on_activated)
        self.tray_icon.messageClicked.connect(window.show_main_window)
        self.tray_icon.show()

        application.setQuitOnLastWindowClosed(False)
        application.installEventFilter(self)
        application.aboutToQuit.connect(self.close)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._application and event.type() == QEvent.Type.Quit:
            # 系统退出也可能先关闭窗口，不能把这次关闭拦截为后台运行。
            self._quitting = True

        if (
            watched is self._window
            and event.type() == QEvent.Type.Close
            and self._enabled
            and not self._quitting
            and not self._application.isSavingSession()
        ):
            if (
                self.tray_icon is not None
                and self.tray_icon.isVisible()
                and QSystemTrayIcon.isSystemTrayAvailable()
            ):
                self._window.hide_to_background()
                event.ignore()
                self._show_background_notice()
                return True

            # 托盘在运行中消失时，允许关闭退出，避免无法恢复的隐形进程。
            self._application.setQuitOnLastWindowClosed(True)

        return super().eventFilter(watched, event)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        # macOS 单击会打开原生菜单，不额外弹出窗口打断菜单操作。
        if sys.platform != "darwin" and reason in {
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        }:
            self._window.show_main_window()

    def _show_background_notice(self) -> None:
        if self._background_notice_shown or self.tray_icon is None:
            return
        self._background_notice_shown = True
        if QSystemTrayIcon.supportsMessages():
            self.tray_icon.showMessage(
                "Trade Translator 仍在后台运行",
                "全局快捷键仍可使用。通过托盘菜单显示主窗口或退出程序。",
                QSystemTrayIcon.MessageIcon.Information,
                3000,
            )

    def quit_application(self) -> None:
        self._quitting = True
        self._application.quit()

    def close(self) -> None:
        """释放托盘入口；实际业务资源由应用的退出信号统一清理。"""
        if self._closed:
            return
        self._closed = True
        if not self._enabled:
            return
        self._enabled = False
        self._application.removeEventFilter(self)
        self._application.aboutToQuit.disconnect(self.close)
        self._application.setQuitOnLastWindowClosed(self._previous_quit_policy)
        if self.tray_icon is not None:
            self.tray_icon.hide()
        self.menu.close()
