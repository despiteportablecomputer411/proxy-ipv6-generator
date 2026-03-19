from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from ui.theme import DARK_THEME
from core.i18n import _

class LanguagePromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Language / Chọn Ngôn Ngữ")
        self.setFixedSize(350, 180)
        self.setStyleSheet(DARK_THEME)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.selected_lang = "vi"

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        lbl = QLabel("Vui lòng chọn ngôn ngữ / Please select your language:")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        btn_vi = QPushButton("🇻🇳 Tiếng Việt")
        btn_vi.setMinimumHeight(40)
        btn_vi.clicked.connect(lambda: self.select_lang("vi"))
        
        btn_en = QPushButton("🇬🇧 English")
        btn_en.setMinimumHeight(40)
        btn_en.clicked.connect(lambda: self.select_lang("en"))
        
        btn_layout.addWidget(btn_vi)
        btn_layout.addWidget(btn_en)
        
        layout.addLayout(btn_layout)

    def select_lang(self, lang):
        self.selected_lang = lang
        self.accept()
