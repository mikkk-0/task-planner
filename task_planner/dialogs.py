from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

from .database import Task


class TaskDialog(QDialog):
    def __init__(self, parent=None, task: Task | None = None) -> None:
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Редактировать задачу" if task else "Новая задача")
        self.setMinimumWidth(460)

        root = QVBoxLayout(self)
        heading = QLabel("Редактирование задачи" if task else "Создание задачи")
        heading.setObjectName("pageTitle")
        root.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(13)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Например: отправить отчёт")
        form.addRow("Название *", self.title_edit)

        self.has_deadline = QCheckBox("Указать дедлайн")
        self.deadline_edit = QDateTimeEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDisplayFormat("dd.MM.yyyy  HH:mm")
        self.deadline_edit.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.deadline_edit.setEnabled(False)
        self.has_deadline.toggled.connect(self.deadline_edit.setEnabled)
        form.addRow("", self.has_deadline)
        form.addRow("Дедлайн", self.deadline_edit)

        self.importance_combo = QComboBox()
        self.importance_combo.addItem("Не указана", None)
        self.importance_combo.addItem("Низкая", 1)
        self.importance_combo.addItem("Средняя", 2)
        self.importance_combo.addItem("Высокая", 3)
        form.addRow("Важность", self.importance_combo)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Дополнительные детали…")
        self.description_edit.setFixedHeight(105)
        form.addRow("Описание", self.description_edit)
        root.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        if task:
            self._load(task)

    def _load(self, task: Task) -> None:
        self.title_edit.setText(task.title)
        self.description_edit.setPlainText(task.description)
        if task.deadline:
            self.has_deadline.setChecked(True)
            self.deadline_edit.setDateTime(QDateTime(task.deadline))
        index = self.importance_combo.findData(task.importance)
        self.importance_combo.setCurrentIndex(max(0, index))

    def _validate_and_accept(self) -> None:
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Нет названия", "Введите название задачи.")
            self.title_edit.setFocus()
            return
        self.accept()

    def values(self) -> dict[str, object]:
        deadline: datetime | None = None
        if self.has_deadline.isChecked():
            deadline = self.deadline_edit.dateTime().toPython()
        return {
            "title": self.title_edit.text().strip(),
            "deadline": deadline,
            "importance": self.importance_combo.currentData(),
            "description": self.description_edit.toPlainText().strip(),
        }
