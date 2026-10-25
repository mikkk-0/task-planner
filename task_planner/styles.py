from PySide6.QtGui import QColor, QPalette


def dark_palette() -> QPalette:
    """Palette for native Qt controls that are not fully covered by QSS."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#11151d"))
    palette.setColor(QPalette.WindowText, QColor("#e7eaf0"))
    palette.setColor(QPalette.Base, QColor("#171b24"))
    palette.setColor(QPalette.AlternateBase, QColor("#1d222d"))
    palette.setColor(QPalette.ToolTipBase, QColor("#242a36"))
    palette.setColor(QPalette.ToolTipText, QColor("#f4f5f8"))
    palette.setColor(QPalette.Text, QColor("#e7eaf0"))
    palette.setColor(QPalette.Button, QColor("#202631"))
    palette.setColor(QPalette.ButtonText, QColor("#e7eaf0"))
    palette.setColor(QPalette.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.Highlight, QColor("#7168ee"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.PlaceholderText, QColor("#687286"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#626b7a"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#626b7a"))
    return palette


APP_STYLE = """
QWidget {
    color: #e7eaf0;
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 14px;
}
QMainWindow, QDialog, QWidget#page { background: #11151d; }
QFrame#sidebar { background: #0a0d12; border: none; }
QLabel#brand { color: #f7f7fb; font-size: 20px; font-weight: 700; padding: 12px 8px; }
QPushButton {
    color: #e4e7ed; background: #202631; border: 1px solid #343c4b;
    border-radius: 9px; padding: 8px 14px;
}
QPushButton:hover { background: #29303d; border-color: #4b5568; }
QPushButton:pressed { background: #181d26; }
QPushButton#navButton {
    color: #9ba6ba; background: transparent; border: none;
    border-radius: 9px; padding: 12px 14px; text-align: left;
}
QPushButton#navButton:hover { background: #171c25; color: #f7f7fb; }
QPushButton#navButton:checked { background: #7168ee; color: white; font-weight: 600; }
QPushButton#addButton {
    color: white; background: #7168ee; border: none; border-radius: 10px;
    padding: 11px 20px; font-weight: 700;
}
QPushButton#addButton:hover { background: #8179f5; }
QPushButton#secondaryButton {
    background: #1c222c; border: 1px solid #343c4b; border-radius: 9px; padding: 9px 15px;
}
QLabel#pageTitle { font-size: 25px; font-weight: 750; color: #f3f4f7; }
QLabel#sectionTitle { font-size: 16px; font-weight: 700; color: #e2e5eb; }
QLabel#muted { color: #929bad; }
QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; border: none; }
QFrame#taskCard {
    background: #1b202a; border: 1px solid #2c3442; border-radius: 11px;
}
QFrame#taskCard:hover { background: #202631; border: 1px solid #7770e8; }
QFrame#focusZone {
    background: #17182a; border: 2px dashed #504c88; border-radius: 14px;
}
QFrame#focusZone[dragActive="true"] { background: #202044; border-color: #8179f5; }
QLabel#taskTitle { color: #edf0f4; font-size: 15px; font-weight: 650; }
QLabel#deadline { color: #9aa5b7; }
QLabel#deadline[urgent="true"] { color: #ff6275; font-weight: 700; }
QLabel#badge { color: #f1ce73; background: #3a321d; border-radius: 7px; padding: 3px 7px; }
QCheckBox { color: #e7eaf0; spacing: 8px; }
QCheckBox::indicator { width: 19px; height: 19px; }
QLineEdit, QTextEdit, QComboBox, QDateTimeEdit {
    color: #edf0f4; background: #171b24; border: 1px solid #343c4b;
    border-radius: 8px; padding: 8px; selection-background-color: #7168ee;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateTimeEdit:focus { border-color: #8179f5; }
QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled, QDateTimeEdit:disabled {
    color: #697385; background: #131720; border-color: #282f3b;
}
QComboBox QAbstractItemView {
    color: #e7eaf0; background: #1b202a; border: 1px solid #3b4454;
    selection-background-color: #7168ee; outline: none;
}
QDialogButtonBox QPushButton { min-width: 90px; padding: 8px 14px; }
QFrame#dayRow { background: #171b24; border: 1px solid #2b3340; border-radius: 12px; }
QFrame#dayRow[today="true"] { background: #1a1b2d; border-color: #625cc1; }
QLabel#dayName { color: #a4aec0; font-size: 13px; font-weight: 650; }
QLabel#dayNumber { color: #f1f3f6; font-size: 22px; font-weight: 750; }
QLabel#todayBadge {
    color: #ffffff; background: #7168ee; border-radius: 7px;
    padding: 3px 7px; font-size: 11px; font-weight: 700;
}
QScrollBar:vertical { background: #11151d; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #3b4352; min-height: 32px; border-radius: 5px; }
QScrollBar::handle:vertical:hover { background: #596274; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #11151d; height: 10px; }
QScrollBar::handle:horizontal { background: #3b4352; min-width: 32px; border-radius: 5px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QCalendarWidget QWidget { alternate-background-color: #1b202a; }
QCalendarWidget QAbstractItemView {
    color: #e7eaf0; background: #171b24; selection-background-color: #7168ee;
    selection-color: white;
}
QCalendarWidget QToolButton { color: #e7eaf0; background: #202631; border: none; }
QToolTip { color: #edf0f4; background: #242a36; border: 1px solid #434c5d; padding: 6px; }
"""
