from __future__ import annotations

from datetime import datetime, timedelta

from PySide6.QtCore import QMimeData, QPoint, Qt, Signal
from PySide6.QtGui import QDrag, QMouseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .database import Task


TASK_MIME = "application/x-task-planner-id"
IMPORTANCE_LABELS = {1: "Низкая", 2: "Средняя", 3: "Высокая"}


def clear_layout(layout: QVBoxLayout | QHBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())


class TaskCard(QFrame):
    completion_changed = Signal(int, bool)
    edit_requested = Signal(int)

    def __init__(self, task: Task, *, compact: bool = False, draggable: bool = True) -> None:
        super().__init__()
        self.task = task
        self.draggable = draggable
        self._drag_start: QPoint | None = None
        self.setObjectName("taskCard")
        self.setCursor(Qt.OpenHandCursor if draggable else Qt.ArrowCursor)
        self.setToolTip("Правый клик — редактировать" if draggable else task.description)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 9 if compact else 11, 12, 9 if compact else 11)
        root.setSpacing(10)
        self.checkbox = QCheckBox()
        self.checkbox.setCursor(Qt.ArrowCursor)
        self.checkbox.setChecked(task.completed)
        self.checkbox.setToolTip("Вернуть в работу" if task.completed else "Отметить выполненной")
        self.checkbox.toggled.connect(lambda checked: self.completion_changed.emit(task.id, checked))
        root.addWidget(self.checkbox, 0, Qt.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        title = QLabel(task.title)
        title.setObjectName("taskTitle")
        title.setWordWrap(True)
        title.setAttribute(Qt.WA_TransparentForMouseEvents)
        if task.completed:
            title.setStyleSheet("color: #8d96a8; text-decoration: line-through;")
        text_layout.addWidget(title)

        details = QHBoxLayout()
        details.setSpacing(8)
        if task.deadline:
            deadline = QLabel(task.deadline.strftime("%d.%m.%Y · %H:%M"))
            deadline.setObjectName("deadline")
            deadline.setProperty("urgent", task.deadline <= datetime.now() + timedelta(hours=48))
            deadline.setAttribute(Qt.WA_TransparentForMouseEvents)
            details.addWidget(deadline)
        if task.importance:
            badge = QLabel(IMPORTANCE_LABELS[task.importance])
            badge.setObjectName("badge")
            badge.setAttribute(Qt.WA_TransparentForMouseEvents)
            details.addWidget(badge)
        details.addStretch()
        text_layout.addLayout(details)
        if task.description and not compact:
            description = QLabel(task.description)
            description.setObjectName("muted")
            description.setWordWrap(True)
            description.setMaximumHeight(42)
            description.setAttribute(Qt.WA_TransparentForMouseEvents)
            text_layout.addWidget(description)
        root.addLayout(text_layout, 1)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.RightButton:
            self.edit_requested.emit(self.task.id)
            event.accept()
            return
        if event.button() == Qt.LeftButton and self.draggable:
            self._drag_start = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self.draggable
            and self._drag_start is not None
            and event.buttons() & Qt.LeftButton
            and (event.position().toPoint() - self._drag_start).manhattanLength() >= 8
        ):
            drag = QDrag(self)
            mime = QMimeData()
            mime.setData(TASK_MIME, str(self.task.id).encode("ascii"))
            drag.setMimeData(mime)
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(self._drag_start)
            self.setCursor(Qt.ClosedHandCursor)
            drag.exec(Qt.MoveAction)
            self.setCursor(Qt.OpenHandCursor)
            self._drag_start = None
        super().mouseMoveEvent(event)


class TaskList(QScrollArea):
    completion_changed = Signal(int, bool)
    edit_requested = Signal(int)
    task_dropped = Signal(int, int)

    def __init__(self, *, accept_drops: bool = False, empty_text: str = "Задач пока нет") -> None:
        super().__init__()
        self.empty_text = empty_text
        self._tasks: list[Task] = []
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAcceptDrops(accept_drops)
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(2, 2, 7, 2)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignTop)
        self.setWidget(self.container)
        self.drop_indicator = QFrame(self.container)
        self.drop_indicator.setFixedHeight(3)
        self.drop_indicator.setStyleSheet("background: #918aff; border-radius: 1px;")
        self.drop_indicator.hide()

    def set_tasks(self, tasks: list[Task], *, compact: bool = False) -> None:
        self._tasks = tasks
        self.drop_indicator.hide()
        clear_layout(self.layout)
        if not tasks:
            empty = QLabel(self.empty_text)
            empty.setObjectName("muted")
            empty.setAlignment(Qt.AlignCenter)
            empty.setMinimumHeight(72)
            self.layout.addWidget(empty)
            return
        for task in tasks:
            card = TaskCard(task, compact=compact)
            card.completion_changed.connect(self.completion_changed)
            card.edit_requested.connect(self.edit_requested)
            self.layout.addWidget(card)

    def _cards(self) -> list[TaskCard]:
        cards: list[TaskCard] = []
        for index in range(self.layout.count()):
            widget = self.layout.itemAt(index).widget()
            if isinstance(widget, TaskCard):
                cards.append(widget)
        return cards

    def _drop_index(self, event) -> int:
        point = self.container.mapFrom(self.viewport(), event.position().toPoint())
        cards = self._cards()
        for index, card in enumerate(cards):
            if point.y() < card.geometry().center().y():
                return index
        return len(cards)

    def _show_drop_indicator(self, event) -> None:
        cards = self._cards()
        index = self._drop_index(event)
        if not cards:
            y = 6
        elif index < len(cards):
            y = cards[index].geometry().top() - 5
        else:
            y = cards[-1].geometry().bottom() + 4
        self.drop_indicator.setGeometry(4, y, max(20, self.container.width() - 15), 3)
        self.drop_indicator.show()
        self.drop_indicator.raise_()

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasFormat(TASK_MIME):
            self._show_drop_indicator(event)
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasFormat(TASK_MIME):
            self._show_drop_indicator(event)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:
        self.drop_indicator.hide()
        super().dragLeaveEvent(event)

    def dropEvent(self, event) -> None:
        self.drop_indicator.hide()
        try:
            task_id = int(bytes(event.mimeData().data(TASK_MIME)).decode("ascii"))
        except (ValueError, UnicodeDecodeError):
            event.ignore()
            return
        self.task_dropped.emit(task_id, self._drop_index(event))
        event.acceptProposedAction()


class DropZone(QFrame):
    completion_changed = Signal(int, bool)
    edit_requested = Signal(int)
    task_dropped = Signal(int, int)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("focusZone")
        self.setAcceptDrops(True)
        root = QVBoxLayout(self)
        root.setContentsMargins(13, 12, 13, 12)
        root.setSpacing(8)
        heading = QHBoxLayout()
        title = QLabel("Фокус")
        title.setObjectName("sectionTitle")
        hint = QLabel("Перетащите сюда нужные задачи")
        hint.setObjectName("muted")
        heading.addWidget(title)
        heading.addWidget(hint)
        heading.addStretch()
        root.addLayout(heading)
        self.task_list = TaskList(accept_drops=True, empty_text="Зажмите задачу левой кнопкой и перенесите сюда")
        self.task_list.setStyleSheet("background: transparent;")
        self.task_list.completion_changed.connect(self.completion_changed)
        self.task_list.edit_requested.connect(self.edit_requested)
        self.task_list.task_dropped.connect(self.task_dropped)
        root.addWidget(self.task_list)

    def set_tasks(self, tasks: list[Task]) -> None:
        self.task_list.set_tasks(tasks, compact=True)

    def _set_drag_active(self, active: bool) -> None:
        self.setProperty("dragActive", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasFormat(TASK_MIME):
            self._set_drag_active(True)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:
        self._set_drag_active(False)
        super().dragLeaveEvent(event)

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasFormat(TASK_MIME):
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        self._set_drag_active(False)
        try:
            task_id = int(bytes(event.mimeData().data(TASK_MIME)).decode("ascii"))
        except (ValueError, UnicodeDecodeError):
            event.ignore()
            return
        self.task_dropped.emit(task_id, -1)
        event.acceptProposedAction()
