from datetime import datetime, timedelta

from task_planner.database import TaskDatabase


def test_task_lifecycle(tmp_path):
    db = TaskDatabase(tmp_path / "tasks.sqlite3")
    deadline = datetime.now().replace(microsecond=0) + timedelta(days=1)
    task = db.create_task("  Отчёт  ", deadline, 3, " Подготовить цифры ")
    assert task.title == "Отчёт"
    assert task.deadline == deadline
    assert task.importance == 3
    assert db.open_tasks() == [task]

    db.set_focus(task.id, True)
    assert db.open_tasks() == []
    assert db.focus_tasks()[0].id == task.id

    db.set_completed(task.id, True)
    assert db.focus_tasks()[0].completed is True
    assert db.archived_tasks()[0].id == task.id

    db.set_completed(task.id, False)
    assert db.archived_tasks() == []
    assert db.focus_tasks()[0].completed is False
    db.close()


def test_week_query_and_update(tmp_path):
    db = TaskDatabase(tmp_path / "tasks.sqlite3")
    first = db.create_task("В срок", datetime(2026, 9, 28, 12), None, "")
    db.create_task("Вне срока", datetime(2026, 10, 5, 0), 1, "")
    tasks = db.tasks_between(datetime(2026, 9, 28), datetime(2026, 10, 5))
    assert [task.id for task in tasks] == [first.id]

    db.update_task(first.id, title="Новое имя", deadline=None, importance=2, description="Текст")
    updated = db.get_task(first.id)
    assert (updated.title, updated.deadline, updated.importance, updated.description) == (
        "Новое имя", None, 2, "Текст"
    )
    db.close()


def test_tasks_persist_after_reopening_database(tmp_path):
    path = tmp_path / "tasks.sqlite3"
    first = TaskDatabase(path)
    task = first.create_task("Сохранить меня", None, None, "")
    first.close()

    reopened = TaskDatabase(path)
    assert reopened.get_task(task.id).title == "Сохранить меня"
    reopened.close()
