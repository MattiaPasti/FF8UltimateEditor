from __future__ import annotations

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


GLOBAL_QSS = """
QWidget {
    color: #e8f2ff;
    font-family: "Segoe UI Variable Display", "Bahnschrift", "Segoe UI";
    font-size: 10pt;
}
QToolTip {
    background: #101a2b;
    color: #eef7ff;
    border: 1px solid #38557b;
    padding: 8px 10px;
}
QMainWindow, QDialog {
    background-color: #08101a;
}
QLabel {
    color: #dce8f8;
}
QPushButton, QToolButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #122133, stop: 1 #0f1b2c);
    color: #eef7ff;
    border: 1px solid #27405f;
    border-radius: 14px;
    padding: 8px 14px;
    font-weight: 700;
}
QPushButton:hover, QToolButton:hover {
    border-color: #57f0d8;
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #173149, stop: 1 #13263d);
}
QPushButton:pressed, QToolButton:pressed {
    background: #0b1522;
}
QPushButton:disabled, QToolButton:disabled {
    background: #0d1622;
    color: #59708b;
    border-color: #1b2a3f;
}
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QAbstractSpinBox {
    background: #0b1320;
    color: #eff7ff;
    border: 1px solid #22354d;
    border-radius: 12px;
    padding: 7px 10px;
    selection-background-color: #2cd5d9;
    selection-color: #041018;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QAbstractSpinBox:focus {
    border-color: #57f0d8;
    background: #0f1828;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background: #0d1625;
    color: #eef7ff;
    border: 1px solid #2a4261;
    selection-background-color: #2ad3da;
    selection-color: #041018;
}
QListWidget, QListView, QTreeWidget, QTreeView, QTableWidget, QTableView {
    background: #0b1320;
    alternate-background-color: #0f1b2a;
    color: #e7f1ff;
    border: 1px solid #22354d;
    border-radius: 14px;
    gridline-color: #1f3148;
    selection-background-color: #2dd5d9;
    selection-color: #041018;
}
QListWidget::item, QListView::item, QTreeWidget::item, QTreeView::item {
    padding: 6px;
}
QHeaderView::section {
    background: #111c2d;
    color: #dbe8f9;
    border: none;
    border-right: 1px solid #22354d;
    border-bottom: 1px solid #22354d;
    padding: 8px 10px;
    font-weight: 700;
}
QTabWidget::pane {
    border: 1px solid #22354d;
    border-radius: 16px;
    background: #09121d;
    top: -1px;
}
QTabBar::tab {
    background: #0e1828;
    color: #a9bdd6;
    border: 1px solid #22354d;
    border-bottom: none;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    padding: 10px 14px;
    margin-right: 6px;
    min-width: 72px;
    font-weight: 700;
}
QTabBar::tab:selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #22cdd8, stop: 1 #74f28d);
    color: #041018;
    border-color: #8ef7c6;
}
QTabBar::tab:hover:!selected {
    color: #eef7ff;
    border-color: #57f0d8;
}
QGroupBox {
    border: 1px solid #22354d;
    border-radius: 16px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    background: #09121d;
    font-weight: 700;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #eef7ff;
}
QCheckBox, QRadioButton {
    color: #dce9fa;
    spacing: 8px;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #2b4261;
    background: #09121d;
}
QCheckBox::indicator {
    border-radius: 6px;
}
QRadioButton::indicator {
    border-radius: 9px;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #25d5db, stop: 1 #7cf38c);
    border-color: #8ef7c6;
}
QScrollArea {
    border: none;
}
QProgressBar {
    background: #09121d;
    border: 1px solid #22354d;
    border-radius: 10px;
    min-height: 18px;
    text-align: center;
    color: #eef7ff;
}
QProgressBar::chunk {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #25d5db, stop: 1 #7cf38c);
    border-radius: 8px;
}
QMenuBar {
    background: #08101a;
    color: #dce9fa;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
}
QMenuBar::item:selected {
    background: #122133;
    border-radius: 8px;
}
QMenu {
    background: #0d1625;
    color: #eef7ff;
    border: 1px solid #2a4261;
    border-radius: 12px;
    padding: 6px;
}
QMenu::item {
    padding: 8px 18px;
    border-radius: 8px;
}
QMenu::item:selected {
    background: #1d344f;
}
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #22354d;
}
QScrollBar:vertical {
    background: #09111b;
    width: 12px;
    margin: 4px 0 4px 0;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #223956;
    min-height: 30px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background: #57f0d8;
}
QScrollBar:horizontal {
    background: #09111b;
    height: 12px;
    margin: 0 4px 0 4px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background: #223956;
    min-width: 30px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal:hover {
    background: #57f0d8;
}
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
    width: 0px;
    height: 0px;
}
"""


def build_dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#08101a"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#eef7ff"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#0b1320"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#101b2c"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#101a2b"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#eef7ff"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#eef7ff"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#111b2b"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#eef7ff"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2ad3da"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#041018"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#7cf3d9"))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor("#91a6ff"))
    try:
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#6f84a0"))
    except AttributeError:
        pass
    return palette


def apply_modern_theme(app: QApplication) -> None:
    if app.property("ff8_modern_theme_applied"):
        return

    app.setStyle("Fusion")
    app.setPalette(build_dark_palette())
    app.setStyleSheet(GLOBAL_QSS)
    app.setProperty("ff8_modern_theme_applied", True)
