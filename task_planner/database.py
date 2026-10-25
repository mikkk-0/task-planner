from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Task:
    id: int
    title: str
    deadline: datetime | None
    importance: int | None
    description: str
    completed: bool
    in_focus: bool
    created_at: datetime
    completed_at: datetime | None


class TaskDatabase:
    """Small SQLite-backed repository used by the UI."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self._create_schema()

    def _create_schema(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL CHECK(length(trim(title)) > 0),
                    deadline TEXT,
                    importance INTEGER CHECK(importance IS NULL OR importance BETWEEN 1 AND 3),
                    description TEXT NOT NULL DEFAULT '',
                    completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0, 1)),
                    in_focus INTEGER NOT NULL DEFAULT 0 CHECK(in_focus IN (0, 1)),
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )
            self.connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline)"
            )
            self.connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed)"
            )

    @staticmethod
    def _serialize(value: datetime | None) -> str | None:
        return value.replace(microsecond=0).isoformat() if value else None

    @staticmethod
    def _deserialize(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            deadline=self._deserialize(row["deadline"]),
            importance=row["importance"],
            description=row["description"],
            completed=bool(row["completed"]),
            in_focus=bool(row["in_focus"]),
            created_at=self._deserialize(row["created_at"]) or datetime.now(),
            completed_at=self._deserialize(row["completed_at"]),
        )

    def create_task(
        self,
        title: str,
        deadline: datetime | None = None,
        importance: int | None = None,
        description: str = "",
    ) -> Task:
        now = datetime.now().replace(microsecond=0)
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO tasks(title, deadline, importance, description, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title.strip(), self._serialize(deadline), importance, description.strip(), self._serialize(now)),
            )
        return self.get_task(int(cursor.lastrowid))

    def get_task(self, task_id: int) -> Task:
        row = self.connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(f"Task {task_id} does not exist")
        return self._row_to_task(row)

    def update_task(
        self,
        task_id: int,
        *,
        title: str,
        deadline: datetime | None,
        importance: int | None,
        description: str,
    ) -> None:
        with self.connection:
            self.connection.execute(
                """
                UPDATE tasks
                SET title = ?, deadline = ?, importance = ?, description = ?
                WHERE id = ?
                """,
                (title.strip(), self._serialize(deadline), importance, description.strip(), task_id),
            )

    def set_completed(self, task_id: int, completed: bool) -> None:
        completed_at = datetime.now().replace(microsecond=0) if completed else None
        with self.connection:
            self.connection.execute(
                "UPDATE tasks SET completed = ?, completed_at = ? WHERE id = ?",
                (int(completed), self._serialize(completed_at), task_id),
            )

    def set_focus(self, task_id: int, in_focus: bool) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE tasks SET in_focus = ? WHERE id = ?", (int(in_focus), task_id)
            )

    def delete_task(self, task_id: int) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def _fetch(self, query: str, parameters: Iterable[object] = ()) -> list[Task]:
        rows = self.connection.execute(query, tuple(parameters)).fetchall()
        return [self._row_to_task(row) for row in rows]

    def open_tasks(self) -> list[Task]:
        return self._fetch(
            """
            SELECT * FROM tasks
            WHERE completed = 0 AND in_focus = 0
            """
        )

    def focus_tasks(self) -> list[Task]:
        return self._fetch(
            """
            SELECT * FROM tasks
            WHERE in_focus = 1
            """
        )

    def archived_tasks(self) -> list[Task]:
        return self._fetch(
            """
            SELECT * FROM tasks
            WHERE completed = 1
            ORDER BY completed_at DESC, created_at DESC
            """
        )

    def tasks_between(self, start: datetime, end: datetime) -> list[Task]:
        return self._fetch(
            """
            SELECT * FROM tasks
            WHERE deadline >= ? AND deadline < ?
            ORDER BY deadline, COALESCE(importance, 0) DESC
            """,
            (self._serialize(start), self._serialize(end)),
        )

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "TaskDatabase":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
