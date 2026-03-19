from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from ui.theme import DARK_THEME

class ThemedMessageBox(QDialog):
    def __init__(self, parent=None, title="", message="", icon_type="info", buttons="ok"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(450, 200)
        self.setStyleSheet(DARK_THEME)
        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px;")
        msg_label.setAlignment(Qt.AlignCenter)
        
        if icon_type == "info":
            msg_label.setText(f"ℹ️ {message}")
            msg_label.setStyleSheet("font-size: 14px; color: #89b4fa;")
        elif icon_type == "warning":
            msg_label.setText(f"⚠️ {message}")
            msg_label.setStyleSheet("font-size: 14px; color: #f9e2af;")
        elif icon_type == "error":
            msg_label.setText(f"❌ {message}")
            msg_label.setStyleSheet("font-size: 14px; color: #f38ba8;")
        elif icon_type == "question":
            msg_label.setText(f"❓ {message}")
            msg_label.setStyleSheet("font-size: 14px; color: #cba6f7;")
            
        layout.addWidget(msg_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(15)
        
        if buttons == "ok":
            btn_ok = QPushButton("OK")
            btn_ok.setMinimumWidth(120)
            btn_ok.clicked.connect(self.accept)
            btn_layout.addWidget(btn_ok)
        elif buttons == "yesno":
            btn_yes = QPushButton("Có (Yes)")
            btn_yes.setMinimumWidth(100)
            btn_yes.setStyleSheet("background-color: #a6e3a1; color: #11111b;")
            btn_yes.clicked.connect(self.accept)
            
            btn_no = QPushButton("Không (No)")
            btn_no.setMinimumWidth(100)
            btn_no.setStyleSheet("background-color: #f38ba8; color: #11111b;")
            btn_no.clicked.connect(self.reject)
            
            btn_layout.addWidget(btn_yes)
            btn_layout.addWidget(btn_no)
            
        layout.addLayout(btn_layout)
        
    @staticmethod
    def show_info(parent, title, message):
        dlg = ThemedMessageBox(parent, title, message, "info", "ok")
        dlg.exec()
        
    @staticmethod
    def show_warning(parent, title, message):
        dlg = ThemedMessageBox(parent, title, message, "warning", "ok")
        dlg.exec()
        
    @staticmethod
    def show_error(parent, title, message):
        dlg = ThemedMessageBox(parent, title, message, "error", "ok")
        dlg.exec()
    
    @staticmethod
    def show_question(parent, title, message):
        dlg = ThemedMessageBox(parent, title, message, "question", "yesno")
        return dlg.exec() == QDialog.Accepted
