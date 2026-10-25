from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta

from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .database import Task, TaskDatabase
from .widgets import DropZone, TaskCard, TaskList, clear_layout


MONTHS = (
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
)
WEEKDAYS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")


class HomePage(QWidget):
    edit_requested = Signal(int)
    changed = Signal()

    def __init__(self, database: TaskDatabase) -> None:
        super().__init__()
        self.database = database
        self.settings = QSettings()
        self._open_ids: list[int] = []
        self._focus_ids: list[int] = []
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 25, 30, 25)
        root.setSpacing(13)
        title = QLabel("Мои задачи")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        subtitle = QLabel("Перетаскивайте задачи, чтобы менять порядок или переносить их в фокус")
        subtitle.setObjectName("muted")
        root.addWidget(subtitle)
        self.open_list = TaskList(accept_drops=True, empty_text="Все открытые задачи перенесены или выполнены")
        self.open_list.completion_changed.connect(self._set_completed)
        self.open_list.edit_requested.connect(self.edit_requested)
        self.open_list.task_dropped.connect(self._remove_from_focus)
        root.addWidget(self.open_list, 3)
        self.focus_zone = DropZone()
        self.focus_zone.setMinimumHeight(230)
        self.focus_zone.completion_changed.connect(self._set_completed)
        self.focus_zone.edit_requested.connect(self.edit_requested)
        self.focus_zone.task_dropped.connect(self._add_to_focus)
        root.addWidget(self.focus_zone, 2)

    def _load_order(self, key: str) -> list[int]:
        try:
            values = json.loads(self.settings.value(key, "[]"))
            return [int(value) for value in values]
        except (TypeError, ValueError, json.JSONDecodeError):
            return []

    def _save_order(self, key: str, task_ids: list[int]) -> None:
        self.settings.setValue(key, json.dumps(task_ids))

    def _ordered(self, tasks: list[Task], key: str) -> list[Task]:
        by_id = {task.id: task for task in tasks}
        saved = self._load_order(key)
        ordered_ids = [task_id for task_id in saved if task_id in by_id]
        ordered_ids.extend(task.id for task in tasks if task.id not in ordered_ids)
        self._save_order(key, ordered_ids)
        return [by_id[task_id] for task_id in ordered_ids]

    def refresh(self) -> None:
        open_tasks = self._ordered(self.database.open_tasks(), "order/open")
        focus_tasks = self._ordered(self.database.focus_tasks(), "order/focus")
        self._open_ids = [task.id for task in open_tasks]
        self._focus_ids = [task.id for task in focus_tasks]
        self.open_list.set_tasks(open_tasks)
        self.focus_zone.set_tasks(focus_tasks)

    def _set_completed(self, task_id: int, completed: bool) -> None:
        self.database.set_completed(task_id, completed)
        self.changed.emit()

    def _move_task(self, task_id: int, to_focus: bool, position: int) -> None:
        was_focused = self.database.get_task(task_id).in_focus
        open_ids = [item for item in self._open_ids if item != task_id]
        focus_ids = [item for item in self._focus_ids if item != task_id]
        target = focus_ids if to_focus else open_ids
        original = self._focus_ids if to_focus else self._open_ids
        if position < 0:
            position = len(target)
        elif was_focused == to_focus and task_id in original:
            old_position = original.index(task_id)
            if old_position < position:
                position -= 1
        target.insert(max(0, min(position, len(target))), task_id)
        self._save_order("order/open", open_ids)
        self._save_order("order/focus", focus_ids)
        self.database.set_focus(task_id, to_focus)
        self.changed.emit()

    def _add_to_focus(self, task_id: int, position: int) -> None:
        self._move_task(task_id, True, position)

    def _remove_from_focus(self, task_id: int, position: int) -> None:
        self._move_task(task_id, False, position)


class WeekPage(QWidget):
    edit_requested = Signal(int)
    changed = Signal()

    def __init__(self, database: TaskDatabase) -> None:
        super().__init__()
        self.database = database
        today = date.today()
        self.week_start = today - timedelta(days=today.weekday())
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 25, 30, 25)
        root.setSpacing(14)
        toolbar = QHBoxLayout()
        title = QLabel("Неделя")
        title.setObjectName("pageTitle")
        toolbar.addWidget(title)
        toolbar.addStretch()
        previous = QPushButton("←  Прошлая")
        previous.setObjectName("secondaryButton")
        previous.clicked.connect(lambda: self._move_week(-1))
        current = QPushButton("Сегодня")
        current.setObjectName("secondaryButton")
        current.clicked.connect(self._go_today)
        next_button = QPushButton("Следующая  →")
        next_button.setObjectName("secondaryButton")
        next_button.clicked.connect(lambda: self._move_week(1))
        toolbar.addWidget(previous)
        toolbar.addWidget(current)
        toolbar.addWidget(next_button)
        root.addLayout(toolbar)
        self.range_label = QLabel()
        self.range_label.setObjectName("muted")
        root.addWidget(self.range_label)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.days_widget = QWidget()
        self.days_layout = QVBoxLayout(self.days_widget)
        self.days_layout.setContentsMargins(0, 0, 7, 4)
        self.days_layout.setSpacing(10)
        self.days_layout.setAlignment(Qt.AlignTop)
        self.days_layout.setSizeConstraint(QLayout.SetMinimumSize)
        scroll.setWidget(self.days_widget)
        root.addWidget(scroll)

    def _move_week(self, amount: int) -> None:
        self.week_start += timedelta(days=7 * amount)
        self.refresh()

    def _go_today(self) -> None:
        today = date.today()
        self.week_start = today - timedelta(days=today.weekday())
        self.refresh()

    def _set_completed(self, task_id: int, completed: bool) -> None:
        self.database.set_completed(task_id, completed)
        self.changed.emit()

    def refresh(self) -> None:
        end_date = self.week_start + timedelta(days=7)
        tasks = self.database.tasks_between(
            datetime.combine(self.week_start, time.min), datetime.combine(end_date, time.min)
        )
        by_day: dict[date, list[Task]] = {self.week_start + timedelta(days=i): [] for i in range(7)}
        for task in tasks:
            if task.deadline:
                by_day[task.deadline.date()].append(task)
        last = end_date - timedelta(days=1)
        self.range_label.setText(
            f"{self.week_start.day} {MONTHS[self.week_start.month - 1]} — "
            f"{last.day} {MONTHS[last.month - 1]} {last.year}"
        )
        clear_layout(self.days_layout)
        for index, day in enumerate(by_day):
            row = QFrame()
            row.setObjectName("dayRow")
            row.setProperty("today", day == date.today())
            task_count = len(by_day[day])
            row.setMinimumHeight(max(92, 32 + task_count * 72))
            layout = QHBoxLayout(row)
            layout.setContentsMargins(14, 12, 14, 12)
            layout.setSpacing(16)

            date_block = QVBoxLayout()
            date_block.setSpacing(2)
            day_name = QLabel(WEEKDAYS[index].upper())
            day_name.setObjectName("dayName")
            day_number = QLabel(str(day.day))
            day_number.setObjectName("dayNumber")
            date_block.addWidget(day_name)
            date_block.addWidget(day_number)
            if day == date.today():
                today_badge = QLabel("СЕГОДНЯ")
                today_badge.setObjectName("todayBadge")
                today_badge.setAlignment(Qt.AlignCenter)
                date_block.addWidget(today_badge)
            date_block.addStretch()
            layout.addLayout(date_block)

            divider = QFrame()
            divider.setFrameShape(QFrame.VLine)
            divider.setStyleSheet("color: #303846;")
            layout.addWidget(divider)

            tasks_layout = QVBoxLayout()
            tasks_layout.setSpacing(8)
            if not by_day[day]:
                empty = QLabel("Нет задач")
                empty.setObjectName("muted")
                empty.setMinimumHeight(52)
                empty.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                tasks_layout.addWidget(empty)
            for task in by_day[day]:
                card = TaskCard(task, compact=True, draggable=False)
                card.setMinimumHeight(64)
                card.completion_changed.connect(self._set_completed)
                card.edit_requested.connect(self.edit_requested)
                tasks_layout.addWidget(card)
            layout.addLayout(tasks_layout, 1)
            self.days_layout.addWidget(row)


class ArchivePage(QWidget):
    edit_requested = Signal(int)
    changed = Signal()

    def __init__(self, database: TaskDatabase) -> None:
        super().__init__()
        self.database = database
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 25, 30, 25)
        root.setSpacing(13)
        title = QLabel("Архив")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        subtitle = QLabel("Выполненные задачи. Снимите отметку, чтобы вернуть задачу в работу.")
        subtitle.setObjectName("muted")
        root.addWidget(subtitle)
        self.task_list = TaskList(empty_text="В архиве пока пусто")
        self.task_list.completion_changed.connect(self._set_completed)
        self.task_list.edit_requested.connect(self.edit_requested)
        root.addWidget(self.task_list)

    def _set_completed(self, task_id: int, completed: bool) -> None:
        self.database.set_completed(task_id, completed)
        self.changed.emit()

    def refresh(self) -> None:
        self.task_list.set_tasks(self.database.archived_tasks())
