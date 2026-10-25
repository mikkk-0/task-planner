# Task Planner

> Тёмный локальный планировщик задач для Linux и Android — с фокусом, неделей,
> архивом и свободной сортировкой карточек.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/Desktop-PySide6-41CD52?logo=qt&logoColor=white)
![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?logo=android&logoColor=white)
![Version](https://img.shields.io/badge/version-1.0-7168EE)

Task Planner хранит данные только на устройстве и не требует регистрации или
подключения к облаку. Desktop-клиент написан на Python/PySide6, мобильный — на
Kotlin/Jetpack Compose.

## Возможности

- создание и редактирование задач с необязательными дедлайном, важностью и описанием;
- красная подсветка ближайших и просроченных дедлайнов;
- произвольная drag-and-drop сортировка открытых задач и зоны «Фокус»;
- недельное представление с переключением между неделями;
- архив завершённых задач;
- постоянная тёмная тема;
- локальное хранение в SQLite;
- сворачивание desktop-версии в системный трей;
- single-instance запуск: повторная команда открывает уже работающее окно.

## Desktop

### Быстрый запуск

```bash
git clone git@github.com:mikkk-0/task-planner.git
cd task-planner
chmod +x run.sh
./run.sh
```

`run.sh` сам создаёт `.venv`, устанавливает зависимости и запускает приложение в
фоне. Если системный Python обновится и окружение перестанет работать, launcher
автоматически пересоздаст его.

Для запуска командой `task-planner` можно создать символическую ссылку:

```bash
sudo ln -s "$(pwd)/run.sh" /usr/local/bin/task-planner
task-planner
```

### Управление

| Действие | Результат |
| --- | --- |
| `Ctrl+N` или «Новая задача» | Создать задачу |
| Правый клик / касание двумя пальцами | Открыть редактирование |
| Зажать карточку и перетащить | Изменить порядок или перенести в «Фокус» |
| Чекбокс | Завершить задачу или вернуть её в работу |
| Закрыть окно | Свернуть приложение в трей |
| Повторно выполнить `task-planner` | Показать уже запущенное окно |

## Android

Android-клиент находится в каталоге [`android`](android/README.md). Откройте этот
каталог как отдельный проект в Android Studio или соберите APK вручную:

```bash
cd android
./gradlew assembleDebug
```

Минимальная версия — Android 8.0 (API 26). Для сборки нужны JDK 17+ и Android SDK 37.0.

## Данные

Desktop-версия создаёт `tasks.sqlite3` в стандартном каталоге данных Qt. Android
использует собственную SQLite-базу приложения. Порядок карточек считается состоянием
интерфейса и хранится отдельно от таблицы задач.

Ни один из клиентов не отправляет задачи в сеть.

## Разработка

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q
```

Структура проекта:

```text
task_planner/   desktop-интерфейс и работа с SQLite
tests/          тесты desktop-репозитория
android/        нативный Android-проект
main.py         запуск desktop-приложения и single-instance IPC
run.sh          автономный launcher
```
