from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QLockFile, QStandardPaths, QThread
from PySide6.QtGui import QFont
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication

from task_planner.database import TaskDatabase
from task_planner.main_window import MainWindow
from task_planner.styles import APP_STYLE, dark_palette


def data_path() -> Path:
    location = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    return Path(location) / "tasks.sqlite3"


def instance_name() -> str:
    return f"task-planner-{os.getuid()}"


def instance_lock() -> QLockFile:
    location = QStandardPaths.writableLocation(QStandardPaths.RuntimeLocation)
    if not location:
        location = QStandardPaths.writableLocation(QStandardPaths.TempLocation)
    directory = Path(location) / "task-planner"
    directory.mkdir(parents=True, exist_ok=True)
    return QLockFile(str(directory / "instance.lock"))


def activate_running_instance(name: str) -> bool:
    socket = QLocalSocket()
    socket.connectToServer(name)
    if not socket.waitForConnected(400):
        return False
    socket.write(b"show\n")
    socket.waitForBytesWritten(400)
    socket.disconnectFromServer()
    return True


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Task Planner")
    app.setOrganizationName("Local")
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    app.setPalette(dark_palette())
    app.setStyleSheet(APP_STYLE)
    app.setFont(QFont("Segoe UI", 10))

    name = instance_name()
    lock = instance_lock()
    if not lock.tryLock(0):
        # The first process can hold the lock a moment before its local server
        # starts listening, so give it a short window to finish initialization.
        for _ in range(10):
            if activate_running_instance(name):
                return 0
            QThread.msleep(100)
        return 0

    QLocalServer.removeServer(name)
    server = QLocalServer(app)
    if not server.listen(name):
        lock.unlock()
        activate_running_instance(name)
        return 0

    database = TaskDatabase(data_path())
    window = MainWindow(database)

    def show_existing_window() -> None:
        while server.hasPendingConnections():
            connection = server.nextPendingConnection()
            window.show_from_tray()
            connection.write(b"ok\n")
            connection.flush()
            connection.disconnectFromServer()

    server.newConnection.connect(show_existing_window)
    window.show()
    result = app.exec()
    server.close()
    lock.unlock()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
