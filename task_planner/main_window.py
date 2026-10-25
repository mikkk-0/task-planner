from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QAction, QCloseEvent, QColor, QIcon, QKeySequence, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from .database import TaskDatabase
from .dialogs import TaskDialog
from .pages import ArchivePage, HomePage, WeekPage


class MainWindow(QMainWindow):
    def __init__(self, database: TaskDatabase) -> None:
        super().__init__()
        self.database = database
        self.setWindowTitle("Планировщик задач")
        self.resize(1180, 920)
        self.setMinimumSize(900, 620)
        self._quit_requested = False
        self.tray: QSystemTrayIcon | None = None
        self._setup_tray()

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 17, 14, 17)
        side_layout.setSpacing(7)
        brand = QLabel("✓  Планировщик")
        brand.setObjectName("brand")
        side_layout.addWidget(brand)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.nav_buttons: list[QPushButton] = []
        for index, label in enumerate(("Задачи", "Неделя", "Архив")):
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, i=index: self._show_page(i))
            self.button_group.addButton(button)
            self.nav_buttons.append(button)
            side_layout.addWidget(button)
        self.nav_buttons[0].setChecked(True)
        side_layout.addStretch()
        add_button = QPushButton("＋  Новая задача")
        add_button.setObjectName("addButton")
        add_button.clicked.connect(self.create_task)
        side_layout.addWidget(add_button)
        root.addWidget(sidebar)

        self.pages = QStackedWidget()
        self.home_page = HomePage(database)
        self.week_page = WeekPage(database)
        self.archive_page = ArchivePage(database)
        for page in (self.home_page, self.week_page, self.archive_page):
            page.edit_requested.connect(self.edit_task)
            page.changed.connect(self.refresh_all)
            self.pages.addWidget(page)
        root.addWidget(self.pages, 1)

        shortcut = QAction(self)
        shortcut.setShortcut(QKeySequence.New)
        shortcut.triggered.connect(self.create_task)
        self.addAction(shortcut)
        self.refresh_all()

    @staticmethod
    def _tray_icon() -> QIcon:
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#7168ee"))
        painter.drawEllipse(4, 4, 56, 56)
        pen = QPen(QColor("#ffffff"), 7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(QPointF(17, 33), QPointF(28, 44))
        painter.drawLine(QPointF(28, 44), QPointF(48, 22))
        painter.end()
        return QIcon(pixmap)

    def _setup_tray(self) -> None:
        icon = self._tray_icon()
        self.setWindowIcon(icon)
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("Планировщик задач")

        menu = QMenu(self)
        open_action = QAction("Открыть планировщик", self)
        open_action.triggered.connect(self.show_from_tray)
        menu.addAction(open_action)
        create_action = QAction("Новая задача", self)
        create_action.triggered.connect(self._create_from_tray)
        menu.addAction(create_action)
        menu.addSeparator()
        quit_action = QAction("Выйти", self)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.show_from_tray()

    def show_from_tray(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _create_from_tray(self) -> None:
        self.show_from_tray()
        self.create_task()

    def quit_application(self) -> None:
        self._quit_requested = True
        if self.tray is not None:
            self.tray.hide()
        self.close()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _show_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        (self.home_page, self.week_page, self.archive_page)[index].refresh()

    def create_task(self) -> None:
        dialog = TaskDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.database.create_task(**dialog.values())
            self.refresh_all()

    def edit_task(self, task_id: int) -> None:
        try:
            task = self.database.get_task(task_id)
        except KeyError:
            return
        dialog = TaskDialog(self, task)
        if dialog.exec() == QDialog.Accepted:
            self.database.update_task(task_id, **dialog.values())
            self.refresh_all()

    def refresh_all(self) -> None:
        self.home_page.refresh()
        self.week_page.refresh()
        self.archive_page.refresh()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.tray is not None and self.tray.isVisible() and not self._quit_requested:
            self.hide()
            event.ignore()
            return
        self.database.close()
        event.accept()
