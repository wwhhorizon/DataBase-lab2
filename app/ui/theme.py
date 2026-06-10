APP_STYLESHEET = """
QWidget {
    background: #f5f7fb;
    color: #1f2937;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei";
    font-size: 18px;
}

QMainWindow {
    background: #f5f7fb;
}

QFrame#LoginCard,
QFrame#StatCard,
QFrame#ProfileCard {
    background: #ffffff;
    border: 1px solid #d9e2ef;
    border-radius: 8px;
}

QLabel#AppTitle {
    color: #0f2f4a;
    font-size: 44px;
    font-weight: 700;
}

QLabel#PageTitle {
    color: #0f2f4a;
    font-size: 30px;
    font-weight: 700;
}

QLabel#SubtleText {
    color: #64748b;
}

QLabel#StatValue {
    color: #0f766e;
    font-size: 42px;
    font-weight: 700;
}

QLabel#StatLabel {
    color: #475569;
    font-size: 17px;
}

QLineEdit,
QComboBox,
QDateEdit,
QSpinBox,
QDoubleSpinBox,
QPlainTextEdit {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 12px 14px;
    min-height: 32px;
}

QLineEdit:focus,
QComboBox:focus,
QDateEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QPlainTextEdit:focus {
    border: 1px solid #0f766e;
}

QPushButton {
    background: #0f766e;
    color: #ffffff;
    border: 0;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 600;
    min-height: 36px;
}

QPushButton:hover {
    background: #115e59;
}

QPushButton[variant="secondary"] {
    background: #e2e8f0;
    color: #0f2f4a;
}

QPushButton[variant="secondary"]:hover {
    background: #cbd5e1;
}

QPushButton[variant="danger"] {
    background: #dc2626;
}

QPushButton[variant="danger"]:hover {
    background: #b91c1c;
}

QTabWidget::pane {
    border: 1px solid #d9e2ef;
    border-radius: 8px;
    background: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background: #e8eef7;
    color: #475569;
    padding: 14px 28px;
    margin-right: 5px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #0f766e;
    font-weight: 700;
}

QToolBar {
    background: #ffffff;
    border-bottom: 1px solid #d9e2ef;
    spacing: 12px;
    padding: 12px;
}

QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8fafc;
    gridline-color: #e2e8f0;
    border: 1px solid #d9e2ef;
    border-radius: 6px;
    selection-background-color: #ccfbf1;
    selection-color: #134e4a;
}

QHeaderView::section {
    background: #eef4fb;
    color: #334155;
    border: 0;
    border-right: 1px solid #d9e2ef;
    border-bottom: 1px solid #d9e2ef;
    padding: 12px;
    font-weight: 700;
}

QDialog {
    background: #f5f7fb;
}
"""
