DARK_THEME = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-size: 13px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
QGroupBox {
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 25px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 5px;
}
QPushButton {
    background-color: #89b4fa;
    color: #11111b;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton:pressed {
    background-color: #74c7ec;
}
QLineEdit, QSpinBox, QComboBox {
    background-color: #181825;
    border: 1px solid #313244;
    padding: 5px 10px;
    border-radius: 4px;
    color: #cdd6f4;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}
QTableWidget {
    background-color: #181825;
    alternate-background-color: #1e1e2e;
    border: 1px solid #313244;
    gridline-color: #313244;
    border-radius: 6px;
}
QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    padding: 6px;
    border: 1px solid #1e1e2e;
    font-weight: bold;
}
QScrollBar:vertical {
    border: none;
    background: #181825;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
