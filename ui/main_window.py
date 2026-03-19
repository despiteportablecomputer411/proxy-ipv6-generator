import sys
from core.i18n import _
from ui.dialogs import ThemedMessageBox
from ui.theme import DARK_THEME
import os
import psutil
import ipaddress
import random
import subprocess
import time
import json
import socket
import threading
import winreg as reg

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QApplication, QLabel, QFrame, QPushButton,
                               QLineEdit, QSpinBox, QComboBox, QCheckBox, QRadioButton, 
                               QButtonGroup, QGridLayout, QMessageBox, QStackedWidget, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
                               QTextEdit, QMenu)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QFont, QAction

def is_admin():
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_public_ip():
    import urllib.request
    try:
        url = urllib.request.urlopen('https://api.ipify.org', timeout=3)
        return url.read().decode('utf8').strip()
    except:
        return get_lan_ip()



class MainWindow(QMainWindow):
    update_status_signal = Signal(str, str)
    conn_update_signal = Signal(int, int, int, int) # row, count, done, total
    # Signal check proxy: (row, alive, done_count, total, port)
    check_result_signal = Signal(int, bool, int, int, int)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("PROXY_GENERATOR_TITLE"))
        self.resize(1100, 750) 
        self.setStyleSheet(DARK_THEME)
        
        icon_path = os.path.abspath("logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.running = False
        self.process = None
        self.active_ips = []
        self.rotation_thread = None
        self.current_proxy_list = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. SIDEBAR
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("QFrame { background-color: #11111b; border-right: 1px solid #2a2b3c; }")
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 35, 15, 20)
        sidebar_layout.setSpacing(8)

        lbl_logo = QLabel("""
            <div style='text-align: center;'>
                <span style='color: #89b4fa; font-family: "Segoe UI Black", "Arial Black", sans-serif; font-size: 32px; font-weight: 900; letter-spacing: 2px;'>PROXY</span>
                <br>
                <span style='color: #bac2de; font-family: "Segoe UI", Arial, sans-serif; font-size: 14px; font-weight: 600; letter-spacing: 5px;'>GENERATOR</span>
            </div>
        """)
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setStyleSheet("border: none; margin-bottom: 30px;")
        sidebar_layout.addWidget(lbl_logo)

        self.btn_nav_proxy = QPushButton(_("NAV_CREATE"))
        self.btn_nav_proxy.setCursor(Qt.PointingHandCursor)
        self.btn_nav_proxy.clicked.connect(lambda: self.switch_tab(0))
        sidebar_layout.addWidget(self.btn_nav_proxy)
        
        self.btn_nav_list = QPushButton(_("NAV_LIST"))
        self.btn_nav_list.setCursor(Qt.PointingHandCursor)
        self.btn_nav_list.clicked.connect(lambda: self.switch_tab(1))
        sidebar_layout.addWidget(self.btn_nav_list)
        
        self.btn_nav_tools = QPushButton(_("NAV_TOOLS"))
        self.btn_nav_tools.setCursor(Qt.PointingHandCursor)
        self.btn_nav_tools.clicked.connect(lambda: self.switch_tab(2))
        sidebar_layout.addWidget(self.btn_nav_tools)

        from core.i18n import i18n
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Tiếng Việt", "English"])
        self.combo_lang.setStyleSheet("QComboBox { font-size: 13px; font-weight: bold; padding: 10px; border-radius: 8px; border: 1px solid #45475a; }")
        self.combo_lang.setCursor(Qt.PointingHandCursor)
        
        # Set active language in combo box
        if i18n.current_lang == "vi":
            self.combo_lang.setCurrentIndex(0)
        else:
            self.combo_lang.setCurrentIndex(1)
            
        self.combo_lang.currentIndexChanged.connect(self.change_language)
        sidebar_layout.addWidget(self.combo_lang)

        sidebar_layout.addStretch()

        self.lbl_expire = QLabel("⏳ Trạng Thái Bản: <span style='color:#a6e3a1;'>Vĩnh Viễn</span>")
        self.lbl_expire.setAlignment(Qt.AlignCenter)
        self.lbl_expire.setStyleSheet("""
            QLabel { color: #f9e2af; font-size: 13px; font-weight: bold; 
            background-color: #181825; border: 1px solid #2a2b3c; border-radius: 8px; padding: 12px 10px; }
        """)
        sidebar_layout.addWidget(self.lbl_expire)

        self.lbl_sys_info = QLabel(_("LBL_SYS_LOAD"))
        self.lbl_sys_info.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_sys_info.setStyleSheet("QLabel { color: #a6adc8; font-size: 13px; font-weight: bold; background-color: #181825; border: 1px solid #2a2b3c; border-radius: 8px; padding: 12px 20px; }")
        sidebar_layout.addWidget(self.lbl_sys_info)

        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self.update_system_info)
        self.sys_timer.start(2000)

        main_layout.addWidget(self.sidebar)

        # KHUNG BÊN PHẢI (Chứa StackedWidget và Footer)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # 2. KHUNG NỘI DUNG CHÍNH - STACKED WIDGET
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #1e1e2e;")
        right_layout.addWidget(self.stacked_widget, stretch=1)
        
        # 3. FOOTER
        footer_frame = QFrame()
        footer_frame.setFixedHeight(45)
        footer_frame.setStyleSheet("QFrame { background-color: #11111b; border-top: 1px solid #2a2b3c; border-bottom: none; border-left: none; border-right: none; }")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(10, 0, 10, 0)
        
        zalo_icon = "file:///" + os.path.abspath("zalo.png").replace("\\", "/")
        tele_icon = "file:///" + os.path.abspath("telegram.png").replace("\\", "/")
        
        lbl_footer = QLabel(f"""
            <span style='color: #bac2de; font-size: 14px; font-weight: bold;'>
                🚀 {_('FOOTER_DEV')} <span style='color:#a6e3a1;'>HÙNG ZERO</span> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; 
                <img src='{zalo_icon}' width='22' height='22' style='vertical-align: middle;'> <span style='color:#89b4fa;'>ZALO : 058.916.1110</span> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; 
                <img src='{tele_icon}' width='22' height='22' style='vertical-align: middle;'> <span style='color:#89dceb;'>TELEGRAM : t.me/HUNGZEROMMO</span>
            </span>
        """)
        lbl_footer.setAlignment(Qt.AlignCenter)
        lbl_footer.setTextFormat(Qt.RichText)
        footer_layout.addWidget(lbl_footer)
        
        right_layout.addWidget(footer_frame)
        main_layout.addWidget(right_container)
        
        # === TRANG 1: CẤU HÌNH TẠO PROXY ===
        self.page_create = QWidget()
        create_layout = QVBoxLayout(self.page_create)
        create_layout.setContentsMargins(40, 40, 40, 30)

        lbl_title_1 = QLabel(_("TXT_CONFIG_TITLE"))
        lbl_title_1.setStyleSheet("color: #cdd6f4; font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        create_layout.addWidget(lbl_title_1)

        form_label_style = "color: #cdd6f4; font-size: 14px; font-weight: bold;"
        form_chk_style = "color: #bac2de; font-size: 13px; font-weight: 600;"
        form_container = QFrame()
        form_container.setStyleSheet("QFrame { background-color: #181825; border: 1px solid #313244; border-radius: 12px; } QLabel { border: none; background: transparent; } QCheckBox { border: none; background: transparent;} QRadioButton { border: none; background: transparent;}")
        form_layout = QGridLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(30, 30, 30, 30)

        form_layout.setColumnStretch(1, 1)
        form_layout.setColumnStretch(3, 1)

        self.sp_start_port = QSpinBox()
        self.sp_start_port.setRange(1000, 65000)
        self.sp_start_port.setValue(1980)

        self.le_proxy_count = QLineEdit("5")

        self.le_user = QLineEdit()
        self.le_user.setPlaceholderText("Enter username...")

        self.le_password = QLineEdit()
        self.le_password.setPlaceholderText("Enter password...")
        self.le_password.setEchoMode(QLineEdit.Password)

        self.sp_rotation_time = QSpinBox()
        self.sp_rotation_time.setRange(1, 1440)
        self.sp_rotation_time.setValue(10)

        self.cb_interface = QComboBox()
        self.cb_ipv6 = QComboBox()
        self.cb_interface.currentIndexChanged.connect(self.on_interface_selected)

        def make_form_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(form_label_style)
            return lbl

        form_layout.addWidget(make_form_label(_("TXT_START_PORT")), 0, 0)
        form_layout.addWidget(self.sp_start_port, 0, 1)

        form_layout.addWidget(make_form_label(_("TXT_PROXY_COUNT")), 1, 0)
        form_layout.addWidget(self.le_proxy_count, 1, 1)

        form_layout.addWidget(make_form_label(_("TXT_USER")), 2, 0)
        form_layout.addWidget(self.le_user, 2, 1)

        form_layout.addWidget(make_form_label(_("TXT_PASS")), 3, 0)
        form_layout.addWidget(self.le_password, 3, 1)

        form_layout.addWidget(make_form_label(_("TXT_ROT_TIME")), 4, 0)
        form_layout.addWidget(self.sp_rotation_time, 4, 1)

        form_layout.addWidget(make_form_label(_("TXT_INTERFACE")), 0, 2)
        form_layout.addWidget(self.cb_interface, 0, 3)

        form_layout.addWidget(make_form_label(_("TXT_IPV6_ADD")), 1, 2)
        form_layout.addWidget(self.cb_ipv6, 1, 3)

        chk_layout = QGridLayout()
        chk_layout.setSpacing(15)
        self.chk_no_sec = QCheckBox(_("CHK_NO_SEC"))
        self.chk_no_sec.setStyleSheet(form_chk_style)
        self.chk_no_sec.setChecked(True)
        self.chk_no_sec.toggled.connect(self.toggle_auth)

        self.chk_no_rot = QCheckBox(_("CHK_NO_ROT"))
        self.chk_no_rot.setStyleSheet(form_chk_style)
        self.chk_no_rot.setChecked(True)
        self.chk_no_rot.toggled.connect(self.toggle_rotation)

        self.chk_public = QCheckBox(_("CHK_PUB_PROX"))
        self.chk_public.setStyleSheet(form_chk_style)
        self.chk_recreate = QCheckBox(_("CHK_RECREATE"))
        self.chk_recreate.setStyleSheet(form_chk_style)

        chk_layout.addWidget(self.chk_no_sec, 0, 0)
        chk_layout.addWidget(self.chk_public, 0, 1)
        chk_layout.addWidget(self.chk_no_rot, 1, 0)
        chk_layout.addWidget(self.chk_recreate, 1, 1)

        form_layout.addLayout(chk_layout, 2, 2, 2, 2)

        rad_layout = QHBoxLayout()
        lbl_netmask = make_form_label(_("TXT_NETMASK"))
        rad_layout.addWidget(lbl_netmask)
        self.rb_64 = QRadioButton("X64")
        self.rb_80 = QRadioButton("X80")
        self.rb_48 = QRadioButton("X48")
        self.rb_64.setChecked(True)

        self.netmask_group = QButtonGroup()
        self.netmask_group.addButton(self.rb_64, 64)
        self.netmask_group.addButton(self.rb_80, 80)
        self.netmask_group.addButton(self.rb_48, 48)

        rad_layout.addWidget(self.rb_64)
        rad_layout.addSpacing(10)
        rad_layout.addWidget(self.rb_80)
        rad_layout.addSpacing(10)
        rad_layout.addWidget(self.rb_48)
        rad_layout.addStretch()

        form_layout.addLayout(rad_layout, 4, 2, 1, 2)
        
        app_settings_layout = QHBoxLayout()
        self.chk_auto_run = QCheckBox(_("CHK_AUTO_RUN"))
        self.chk_startup = QCheckBox(_("CHK_STARTUP"))
        
        self.app_config = {"auto_run": False, "startup": False}
        if os.path.exists("app_config.json"):
            try:
                with open("app_config.json", "r", encoding="utf-8") as f:
                    self.app_config = json.load(f)
            except: pass
            
        self.chk_auto_run.setChecked(self.app_config.get("auto_run", False))
        self.chk_startup.setChecked(self.app_config.get("startup", False))
        
        self.chk_auto_run.toggled.connect(self.save_app_config)
        self.chk_startup.toggled.connect(self.toggle_win_startup)
        
        app_settings_layout.addWidget(self.chk_auto_run)
        app_settings_layout.addSpacing(15)
        app_settings_layout.addWidget(self.chk_startup)
        app_settings_layout.addStretch()

        form_layout.addLayout(app_settings_layout, 5, 2, 1, 2)
        
        create_layout.addWidget(form_container)

        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 20, 0, 10)
        self.btn_action = QPushButton(_("BTN_START_PROXY"))
        self.set_button_class(self.btn_action, "primary")
        self.btn_action.setFixedHeight(50)
        self.btn_action.setCursor(Qt.PointingHandCursor)
        self.btn_action.clicked.connect(self.toggle_process)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_action, stretch=2)
        action_layout.addStretch()

        create_layout.addLayout(action_layout)

        self.lbl_status = QLabel(_("TXT_READY"))
        self.lbl_status.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 15px;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        create_layout.addWidget(self.lbl_status)
        create_layout.addStretch()

        # === TRANG 2: DANH SÁCH PROXY (TRUNG TÂM ĐIỀU KHIỂN) ===
        self.page_list = QWidget()
        list_layout = QVBoxLayout(self.page_list)
        list_layout.setContentsMargins(30, 30, 30, 20)
        list_layout.setSpacing(10)

        lbl_title_2 = QLabel(_("PROXY_LIST_HEADER"))
        lbl_title_2.setStyleSheet("color: #cdd6f4; font-size: 24px; font-weight: bold; margin-bottom: 5px;")
        list_layout.addWidget(lbl_title_2)
        
        # Hàng nút điều khiển
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)
        
        self.btn_check_proxy = QPushButton(_("BTN_CHECK_PROX"))
        self.set_button_class(self.btn_check_proxy, "secondary")
        self.btn_check_proxy.setCursor(Qt.PointingHandCursor)
        self.btn_check_proxy.clicked.connect(self.check_all_proxies)
        
        self.btn_rotate_all = QPushButton(_("BTN_ROT_ALL"))
        self.set_button_class(self.btn_rotate_all, "secondary")
        self.btn_rotate_all.setCursor(Qt.PointingHandCursor)
        self.btn_rotate_all.clicked.connect(self.rotate_all_ips)
        
        self.btn_count_conn = QPushButton(_("BTN_CNT_CONN"))
        self.set_button_class(self.btn_count_conn, "secondary")
        self.btn_count_conn.setCursor(Qt.PointingHandCursor)
        self.btn_count_conn.clicked.connect(self.count_connections)
        
        ctrl_layout.addWidget(self.btn_check_proxy)
        ctrl_layout.addWidget(self.btn_rotate_all)
        ctrl_layout.addWidget(self.btn_count_conn)
        ctrl_layout.addStretch()
        list_layout.addLayout(ctrl_layout)
        
        # Bảng proxy 5 cột
        self.table_proxies = QTableWidget(0, 5)
        self.table_proxies.setHorizontalHeaderLabels([_("COL_INDEX"), _("COL_PROXY"), _("COL_IPV6"), _("COL_STATUS"), _("COL_CONN")])
        self.table_proxies.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_proxies.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_proxies.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_proxies.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_proxies.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_proxies.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_proxies.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_proxies.verticalHeader().setVisible(False)
        self.table_proxies.setAlternatingRowColors(True)
        self.table_proxies.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_proxies.customContextMenuRequested.connect(self.show_proxy_context_menu)
        
        list_layout.addWidget(self.table_proxies, stretch=5)
        
        # Log hoạt động real-time
        lbl_log = QLabel(_("LBL_LOG_ACT"))
        lbl_log.setStyleSheet("color: #89b4fa; font-size: 13px; font-weight: bold; margin-top: 5px;")
        list_layout.addWidget(lbl_log)
        
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(150)
        self.txt_log.setStyleSheet("""
            QTextEdit {
                background-color: #11111b; color: #a6adc8; font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                border: 1px solid #313244; border-radius: 8px; padding: 8px;
            }
        """)
        list_layout.addWidget(self.txt_log, stretch=2)
        
        # Hàng nút dưới cùng
        btns_layout = QHBoxLayout()
        btn_copy = QPushButton(_("BTN_COPY_PROX"))
        self.set_button_class(btn_copy, "primary")
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.clicked.connect(self.copy_proxies)
        
        btn_open_file = QPushButton(_("BTN_OPEN_TXT2"))
        self.set_button_class(btn_open_file, "secondary")
        btn_open_file.setCursor(Qt.PointingHandCursor)
        btn_open_file.clicked.connect(self.open_exported_list)
        
        btns_layout.addStretch()
        btns_layout.addWidget(btn_open_file)
        btns_layout.addSpacing(15)
        btns_layout.addWidget(btn_copy)
        
        list_layout.addLayout(btns_layout)

        # === TRANG 3: CÔNG CỤ CỨU HỘ MẠNG ===
        self.page_tools = QWidget()
        tools_layout = QVBoxLayout(self.page_tools)
        tools_layout.setContentsMargins(50, 50, 50, 50)
        tools_layout.setSpacing(25)
        
        lbl_title_3 = QLabel(_("LBL_TOOL_TITLE"))
        lbl_title_3.setStyleSheet("color: #f38ba8; font-size: 26px; font-weight: bold; margin-bottom: 10px;")
        lbl_title_3.setAlignment(Qt.AlignCenter)
        tools_layout.addWidget(lbl_title_3)
        
        lbl_desc = QLabel(_("LBL_TOOL_DESC"))
        lbl_desc.setStyleSheet("color: #bac2de; font-size: 15px;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignCenter)
        tools_layout.addWidget(lbl_desc)
        tools_layout.addSpacing(20)

        # Nút 1: Clear IPv6
        btn_tool_clean = QPushButton(_("BTN_TL_CLN"))
        self.set_button_class(btn_tool_clean, "danger")
        btn_tool_clean.setFixedHeight(55)
        btn_tool_clean.setCursor(Qt.PointingHandCursor)
        btn_tool_clean.clicked.connect(self.tool_clean_ipv6)
        
        # Nút 2: Kill Port
        btn_tool_kill = QPushButton(_("BTN_TL_KILL"))
        self.set_button_class(btn_tool_kill, "danger")
        btn_tool_kill.setFixedHeight(55)
        btn_tool_kill.setCursor(Qt.PointingHandCursor)
        btn_tool_kill.clicked.connect(self.tool_kill_ports)
        
        # Nút 3: Open Firewall
        btn_tool_firewall = QPushButton(_("BTN_TL_FW"))
        self.set_button_class(btn_tool_firewall, "primary")
        btn_tool_firewall.setFixedHeight(55)
        btn_tool_firewall.setCursor(Qt.PointingHandCursor)
        btn_tool_firewall.clicked.connect(self.tool_open_firewall)

        tools_layout.addWidget(btn_tool_clean)
        tools_layout.addWidget(btn_tool_kill)
        tools_layout.addWidget(btn_tool_firewall)
        tools_layout.addStretch()

        # Thêm các trang vào StackedWidget
        self.stacked_widget.addWidget(self.page_create)
        self.stacked_widget.addWidget(self.page_list)
        self.stacked_widget.addWidget(self.page_tools)

        # Mặc định mở trang 0 (Tạo proxy)
        self.switch_tab(0)

        self.toggle_auth()
        self.toggle_rotation()
        self.load_network_data()
        self.update_status_signal.connect(self.handle_status_update)
        self.conn_update_signal.connect(self._on_conn_update)
        self.check_result_signal.connect(self._on_check_result)
        self._checking_proxies = False
        self._counting_conns = False
        self._check_alive = 0
        self._check_dead = 0

        # Đọc dữ liệu từ session trước nếu có
        self.load_exported_to_view()
        
        if self.app_config.get("auto_run", False):
            QTimer.singleShot(1500, self.start_proxy)

    # --------------- CẤU HÌNH APP & KHỞI ĐỘNG ---------------
    def change_language(self, index):
        new_lang = "vi" if index == 0 else "en"
        from core.i18n import i18n
        if i18n.current_lang != new_lang:
            self.app_config["language"] = new_lang
            self.save_app_config()
            
            ThemedMessageBox.show_info(self, _("INFO_TITLE"), 
                "Language changed! Please close and reopen the application to apply.\n\nNgôn ngữ đã thay đổi! Vui lòng tắt và mở lại ứng dụng để áp dụng.")
    
    def save_app_config(self):
        self.app_config["auto_run"] = self.chk_auto_run.isChecked()
        self.app_config["startup"] = self.chk_startup.isChecked()
        try:
            with open("app_config.json", "w", encoding="utf-8") as f:
                json.dump(self.app_config, f)
        except: pass

    def toggle_win_startup(self):
        self.save_app_config()
        is_checked = self.chk_startup.isChecked()
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "ProxyV6_Generator_Zero"
        
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
            if is_checked:
                script_path = os.path.abspath(sys.argv[0])
                if script_path.endswith('.py'):
                    run_cmd = f'"{sys.executable}" "{script_path}"'
                else:
                    run_cmd = f'"{script_path}"'
                reg.SetValueEx(key, app_name, 0, reg.REG_SZ, run_cmd)
            else:
                try: reg.DeleteValue(key, app_name)
                except: pass
            reg.CloseKey(key)
        except Exception as e:
            ThemedMessageBox.show_warning(self, "Lỗi Registry", f"Chưa thể ghi hệ thống do thiếu quyền Admin: {e}")

    # --------------- HỆ THỐNG GIAO DIỆN & STYLE ---------------
    def set_button_class(self, btn, cls_name):
        if cls_name == "primary":
            btn.setStyleSheet("QPushButton { background-color: #89b4fa; color: #11111b; font-weight: bold; font-size: 15px; padding: 12px 20px; border-radius: 8px; border: none; } QPushButton:hover { background-color: #b4befe; }")
        elif cls_name == "danger":
            btn.setStyleSheet("QPushButton { background-color: #f38ba8; color: #11111b; font-weight: bold; font-size: 15px; padding: 12px 20px; border-radius: 8px; border: none; } QPushButton:hover { background-color: #eba0ac; }")
        elif cls_name == "secondary":
            btn.setStyleSheet("QPushButton { background-color: #313244; color: #cdd6f4; font-weight: bold; font-size: 14px; padding: 10px 15px; border-radius: 8px; border: 1px solid #45475a; } QPushButton:hover { background-color: #45475a; color: #89b4fa; }")
        
    def switch_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        active_style = """
            QPushButton { 
                background-color: #89b4fa; color: #11111b; 
                font-weight: bold; font-size: 14px; 
                padding: 14px 18px; border-radius: 8px; border: none; text-align: left; 
            }
        """
        inactive_style = """
            QPushButton { 
                background-color: transparent; color: #bac2de; 
                font-weight: bold; font-size: 14px; 
                padding: 14px 18px; border-radius: 8px; border: none; text-align: left; 
            }
            QPushButton:hover { background-color: #313244; color: #cdd6f4; }
        """
        
        self.btn_nav_proxy.setStyleSheet(active_style if index == 0 else inactive_style)
        self.btn_nav_list.setStyleSheet(active_style if index == 1 else inactive_style)
        self.btn_nav_tools.setStyleSheet(active_style if index == 2 else inactive_style)

    def handle_status_update(self, text, color):
        self.lbl_status.setText(text)
        self.lbl_status.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 15px;")

    def update_system_info(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            color_cpu = "#f38ba8" if cpu > 85 else "#a6e3a1"
            color_ram = "#f38ba8" if ram > 85 else "#89dceb"
            self.lbl_sys_info.setText(
                f"🖥️ CPU: <span style='color:{color_cpu}'>{cpu}%</span><br><br>"
                f"🧠 RAM: <span style='color:{color_ram}'>{ram}%</span>"
            )
        except Exception:
            pass

    def toggle_auth(self):
        state = not self.chk_no_sec.isChecked()
        self.le_user.setEnabled(state)
        self.le_password.setEnabled(state)
        if not state:
            self.le_user.setStyleSheet("background-color: #11111b; color: #6c7086;")
            self.le_password.setStyleSheet("background-color: #11111b; color: #6c7086;")
        else:
            self.le_user.setStyleSheet("")
            self.le_password.setStyleSheet("")

    def toggle_rotation(self):
        state = not self.chk_no_rot.isChecked()
        self.sp_rotation_time.setEnabled(state)

    def load_network_data(self):
        self.network_data = {}
        cmd = "powershell \"Get-NetIPAddress -AddressFamily IPv6 | Where-Object { $_.IPAddress -notmatch '^fe80' } | Select-Object InterfaceAlias, IPAddress | ConvertTo-Json\""
        try:
            out = subprocess.getoutput(cmd)
            if out.strip():
                data = json.loads(out)
                if isinstance(data, dict): data = [data]
                for item in data:
                    iface = item.get('InterfaceAlias', 'Unknown')
                    ip = item.get('IPAddress')
                    if iface not in self.network_data: self.network_data[iface] = []
                    self.network_data[iface].append(ip)
        except Exception:
            pass
            
        if not self.network_data:
            self.network_data = {"Ethernet 2": ["2402:800:61af:c337::1"]}

        interfaces = list(self.network_data.keys())
        self.cb_interface.clear()
        self.cb_interface.addItems(interfaces)
        if interfaces: self.on_interface_selected()

    def on_interface_selected(self):
        iface = self.cb_interface.currentText()
        ips = self.network_data.get(iface, [])
        self.cb_ipv6.clear()
        self.cb_ipv6.addItems(ips)

    # --------------- HỆ THỐNG DANH SÁCH BẢNG (TABLE) ---------------
    def load_exported_to_view(self):
        old_proxies_file = "last_proxies.json"
        if os.path.exists(old_proxies_file):
            try:
                with open(old_proxies_file, "r") as f:
                    proxy_list = json.load(f)
                
                if proxy_list:
                    self.chk_recreate.setChecked(True)
                    self.le_proxy_count.setText(str(len(proxy_list)))
                    self.sp_start_port.setValue(int(proxy_list[0].get("port", 1980)))
                    
                self.update_table_view(proxy_list)
            except:
                pass

    def update_table_view(self, proxy_list):
        self.current_proxy_list = proxy_list
        self.table_proxies.setRowCount(0)

        display_ip = get_public_ip() if self.chk_public.isChecked() else "127.0.0.1"
        has_auth = not self.chk_no_sec.isChecked() and self.le_user.text() != ""
        auth_suffix = f":{self.le_user.text()}:{self.le_password.text()}" if has_auth else ""
        
        for i, p in enumerate(proxy_list):
            row = self.table_proxies.rowCount()
            self.table_proxies.insertRow(row)
            
            idx_item = QTableWidgetItem(str(i + 1))
            idx_item.setTextAlignment(Qt.AlignCenter)
            
            proxy_str = f"{display_ip}:{p['port']}{auth_suffix}"
            proxy_item = QTableWidgetItem(proxy_str)
            ipv6_item = QTableWidgetItem(p['out_ip'])
            
            status_item = QTableWidgetItem("—")
            status_item.setTextAlignment(Qt.AlignCenter)
            
            conn_item = QTableWidgetItem("—")
            conn_item.setTextAlignment(Qt.AlignCenter)
            
            self.table_proxies.setItem(row, 0, idx_item)
            self.table_proxies.setItem(row, 1, proxy_item)
            self.table_proxies.setItem(row, 2, ipv6_item)
            self.table_proxies.setItem(row, 3, status_item)
            self.table_proxies.setItem(row, 4, conn_item)

    # --------------- LOG HOẠT ĐỘNG ---------------
    def append_log(self, message):
        timestamp = time.strftime('%H:%M:%S')
        self.txt_log.append(f"<span style='color:#585b70'>[{timestamp}]</span> {message}")
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())

    # --------------- KIỂM TRA PROXY SỐNG/CHẾT ---------------

    def check_all_proxies(self):
        """Kiểm tra toàn bộ proxy - tuần tự từng cái một, không lag."""
        if not self.current_proxy_list:
            ThemedMessageBox.show_warning(self, _("WARN_TITLE"), "Chưa có proxy nào để kiểm tra!")
            return
        
        if self._checking_proxies:
            ThemedMessageBox.show_warning(self, _("WARN_TITLE"), "Đang kiểm tra proxy, vui lòng chờ...")
            return
        
        self._checking_proxies = True
        self._check_alive = 0
        self._check_dead = 0
        self.btn_check_proxy.setEnabled(False)
        total = len(self.current_proxy_list)
        self.btn_check_proxy.setText(f"⏳ 0/{total}")
        self.append_log(f"🔍 <span style='color:#89b4fa'>{_('LOG_CHECK_START').format(total=total)}</span>")
        
        t = threading.Thread(target=self._check_sequential_worker, daemon=True)
        t.start()
    
    def _check_sequential_worker(self):
        """Check từng proxy một trong 1 thread duy nhất."""
        total = len(self.current_proxy_list)
        for i, p in enumerate(self.current_proxy_list):
            if not self._checking_proxies:
                return  # Bị hủy
            alive = self._check_one_proxy(p['port'])
            # Emit signal để cập nhật 1 cell duy nhất
            self.check_result_signal.emit(i, alive, i + 1, total, p['port'])
        # Signal hoàn tất (row=-1)
        self.check_result_signal.emit(-1, False, total, total, 0)
    
    def _check_one_proxy(self, port):
        """Check 1 proxy, trả về True/False. Không chạm UI."""
        proxy_ip = "127.0.0.1"
        
        # Bước 1: Socket check nhanh
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((proxy_ip, port))
            sock.close()
            if result != 0:
                return False
        except Exception:
            return False
        
        # Bước 2: HTTP check với fallback
        import urllib.request
        test_urls = [
            'http://httpbin.org/ip',
            'http://ip-api.com/json',
            'http://icanhazip.com',
        ]
        
        proxy_handler = urllib.request.ProxyHandler({
            'http': f'http://{proxy_ip}:{port}',
            'https': f'http://{proxy_ip}:{port}',
        })
        
        if not self.chk_no_sec.isChecked() and self.le_user.text():
            user = self.le_user.text()
            pwd = self.le_password.text()
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, f'http://{proxy_ip}:{port}', user, pwd)
            auth_handler = urllib.request.ProxyBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(proxy_handler, auth_handler)
        else:
            opener = urllib.request.build_opener(proxy_handler)
        
        for url in test_urls:
            try:
                resp = opener.open(url, timeout=10)
                if resp.status == 200:
                    return True
            except Exception:
                continue
        
        return True  # Port mở nhưng HTTP fail → vẫn coi là sống

    def _on_check_result(self, row, alive, done, total, port):
        """Xử lý kết quả check 1 proxy trên UI thread."""
        if row == -1:
            # Hoàn tất
            self._checking_proxies = False
            self.btn_check_proxy.setEnabled(True)
            self.btn_check_proxy.setText(_("BTN_CHECK_PROX"))
            self.append_log(
                f"✅ <span style='color:#a6e3a1'>{_('LOG_CHECK_DONE').format(total=total)} "
                f"{self._check_alive} {_('LOG_ALIVE')}, {self._check_dead} {_('LOG_DEAD')}</span>"
            )
            return
        
        # Cập nhật 1 cell duy nhất
        if row < self.table_proxies.rowCount():
            item = self.table_proxies.item(row, 3)
            if item:
                if alive:
                    item.setText(_("PROXY_ALIVE"))
                    item.setForeground(Qt.green)
                    self._check_alive += 1
                else:
                    item.setText(_("PROXY_DEAD"))
                    item.setForeground(Qt.red)
                    self._check_dead += 1
        
        # Cập nhật nút progress
        self.btn_check_proxy.setText(f"⏳ {done}/{total}")

    # --------------- XOAY IP TOÀN BỘ (THỦ CÔNG) ---------------
    def rotate_all_ips(self):
        """Xoay toàn bộ IP proxy ngay lập tức."""
        if not self.running:
            ThemedMessageBox.show_warning(self, _("WARN_TITLE"), "Proxy chưa được khởi chạy!\nHãy bấm _('BTN_START_PROXY') trước.")
            return
        
        self.append_log("🔄 <span style='color:#f9e2af'>Đang xoay toàn bộ IP...</span>")
        self.handle_status_update("Trạng thái: Đang xoay toàn bộ IP (Thủ công)...", "#f9e2af")
        QApplication.processEvents()
        
        # Dừng 3proxy
        if self.process:
            self.process.terminate()
            self.process.wait()
        
        # Tạo batch mới (force_new=True)
        if self.create_proxy_batch(force_new=True):
            exe_path = r"3proxy\bin64\3proxy.exe"
            if not os.path.exists(exe_path): exe_path = "3proxy.exe"
            self.process = subprocess.Popen([exe_path, "3proxy.cfg"], creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.handle_status_update(f"Trạng thái: Proxy hoạt động (Đã xoay IP lúc {time.strftime('%H:%M:%S')})", "#a6e3a1")
            self.append_log(f"✅ <span style='color:#a6e3a1'>Xoay toàn bộ IP thành công! ({len(self.current_proxy_list)} proxy)</span>")
        else:
            self.append_log("❌ <span style='color:#f38ba8'>Xoay IP thất bại!</span>")

    # --------------- XOAY IP RIÊNG LẺ (CONTEXT MENU) ---------------
    def show_proxy_context_menu(self, position):
        """Hiển thị menu chuột phải trên bảng proxy."""
        row = self.table_proxies.rowAt(position.y())
        if row < 0:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244;
                border-radius: 8px; padding: 5px;
            }
            QMenu::item { padding: 8px 20px; border-radius: 4px; }
            QMenu::item:selected { background-color: #313244; color: #89b4fa; }
        """)
        
        action_rotate = menu.addAction(_("MENU_ROTATE_SINGLE"))
        action_check = menu.addAction(_("MENU_CHECK_SINGLE"))
        
        action = menu.exec(self.table_proxies.viewport().mapToGlobal(position))
        
        if action == action_rotate:
            self.rotate_single_proxy(row)
        elif action == action_check:
            if row < len(self.current_proxy_list):
                p = self.current_proxy_list[row]
                item = self.table_proxies.item(row, 3)
                if item:
                    item.setText(_("PROXY_CHECKING"))
                    item.setForeground(Qt.yellow)
                def _check_one(r=row, pt=p['port']):
                    alive = self._check_one_proxy(pt)
                    self.check_result_signal.emit(r, alive, 0, 0, pt)
                t = threading.Thread(target=_check_one, daemon=True)
                t.start()

    def rotate_single_proxy(self, row):
        """Xoay IP của 1 proxy riêng lẻ."""
        if not self.running:
            ThemedMessageBox.show_warning(self, _("WARN_TITLE"), "Proxy chưa được khởi chạy!\nHãy bấm _('BTN_START_PROXY') trước.")
            return
        
        if row >= len(self.current_proxy_list):
            return
        
        p = self.current_proxy_list[row]
        old_ip = p['out_ip']
        iface = self.cb_interface.currentText()
        base_ipv6 = self.cb_ipv6.currentText()
        prefix_len = self.netmask_group.checkedId()
        
        self.append_log(f"🔄 <span style='color:#f9e2af'>Đang xoay IP proxy :{p['port']}...</span>")
        
        try:
            # Xóa IP cũ
            cmd_del = f'netsh interface ipv6 delete address interface="{iface}" address="{old_ip}"'
            subprocess.run(cmd_del, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Tạo IP mới
            network = ipaddress.IPv6Network(f"{base_ipv6}/{prefix_len}", strict=False)
            network_int = int(network.network_address)
            random_host = random.getrandbits(128 - prefix_len)
            new_ipv6 = str(ipaddress.IPv6Address(network_int + random_host))
            
            # Add IP mới vào card mạng
            cmd_add = f'netsh interface ipv6 add address interface="{iface}" address="{new_ipv6}"'
            subprocess.run(cmd_add, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Cập nhật proxy_list
            p['out_ip'] = new_ipv6
            
            # Cập nhật active_ips
            for item in self.active_ips:
                if item['ip'] == old_ip:
                    item['ip'] = new_ipv6
                    break
            
            # Cập nhật bảng
            ipv6_item = self.table_proxies.item(row, 2)
            if ipv6_item:
                ipv6_item.setText(new_ipv6)
            
            status_item = self.table_proxies.item(row, 3)
            if status_item:
                status_item.setText("🔄 Mới")
                status_item.setForeground(Qt.cyan)
            
            # Ghi lại config 3proxy + restart
            self._rewrite_and_restart_3proxy()
            
            # Lưu lại file
            try:
                with open("last_proxies.json", "w") as f:
                    json.dump(self.current_proxy_list, f)
            except: pass
            
            self.export_proxies_to_txt(self.current_proxy_list)
            self.append_log(f"✅ <span style='color:#a6e3a1'>Proxy :{p['port']} đã đổi IP → {new_ipv6}</span>")
            
        except Exception as e:
            self.append_log(f"❌ <span style='color:#f38ba8'>Lỗi xoay IP :{p['port']}: {e}</span>")

    def _rewrite_and_restart_3proxy(self):
        """Ghi lại file 3proxy.cfg và restart 3proxy."""
        if self.process:
            self.process.terminate()
            self.process.wait()
        
        config_path = "3proxy.cfg"
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("maxconn 500\nnscache 65536\nflush\n\n")
            if self.chk_no_sec.isChecked():
                f.write("auth none\n")
            else:
                user = self.le_user.text().strip()
                password = self.le_password.text().strip()
                f.write("auth strong\n")
                if user and password: f.write(f"users {user}:CL:{password}\n")
            f.write("allow *\n\n")
            for p in self.current_proxy_list:
                if p['in_ip'] == "0.0.0.0":
                    f.write(f"proxy -6 -n -a -p{p['port']} -e{p['out_ip']}\n")
                else:
                    f.write(f"proxy -6 -n -a -p{p['port']} -i{p['in_ip']} -e{p['out_ip']}\n")
        
        exe_path = r"3proxy\bin64\3proxy.exe"
        if not os.path.exists(exe_path): exe_path = "3proxy.exe"
        self.process = subprocess.Popen([exe_path, "3proxy.cfg"], creationflags=subprocess.CREATE_NO_WINDOW)

    # --------------- ĐẾM KẾT NỐI ---------------
    def count_connections(self):
        """Đếm số kết nối đang hoạt động trên mỗi port proxy."""
        if not self.current_proxy_list:
            ThemedMessageBox.show_warning(self, _("WARN_TITLE"), "Chưa có proxy nào!")
            return
        
        if self._counting_conns:
            ThemedMessageBox.show_warning(self, _("WARN_TITLE"), "Đang đếm kết nối, vui lòng chờ...")
            return
        
        self._counting_conns = True
        self.btn_count_conn.setEnabled(False)
        self.btn_count_conn.setText("⏳ Đang đếm...")
        self.append_log(f"📊 <span style='color:#89b4fa'>{_('LOG_COUNT_START')}</span>")
        
        ports = [p['port'] for p in self.current_proxy_list]
        t = threading.Thread(target=self._count_conn_worker, args=(ports,), daemon=True)
        t.start()
    
    def _count_conn_worker(self, ports):
        """Worker đếm kết nối trong background thread, cập nhật tuần tự cho mượt UI."""
        port_set = set(ports)
        port_count = {port: 0 for port in port_set}
        total_connections = 0
        total_proxies = len(ports)
        
        try:
            # Thu thập kết nối qua psutil (~ 50ms)
            connections = psutil.net_connections(kind='tcp')
            for conn in connections:
                if conn.laddr and conn.laddr.port in port_set:
                    if conn.status == 'ESTABLISHED':
                        port_count[conn.laddr.port] += 1
                        total_connections += 1
        except Exception:
            pass
            
        # Emit kết quả tuần tự từng dòng với delay ngắn để UI kịp vẽ
        for i, port in enumerate(ports):
            if not self._counting_conns:
                break
            count = port_count[port]
            self.conn_update_signal.emit(i, count, i + 1, total_proxies)
            time.sleep(0.005) # Delay 5ms tạo hiệu ứng lướt mượt mà ~5s cho 1000 proxies
        
        # Emit hoàn tất
        self.conn_update_signal.emit(-1, total_connections, total_proxies, total_proxies)
    
    def _on_conn_update(self, row, count, done, total):
        """Xử lý cập nhật kết quả đếm từng proxy trên UI thread."""
        if row == -1:
            self._counting_conns = False
            self.btn_count_conn.setEnabled(True)
            self.btn_count_conn.setText(_("BTN_CNT_CONN"))
            self.append_log(f"✅ <span style='color:#a6e3a1'>Đã đếm xong! Tổng: {count} kết nối</span> trên {total} proxy")
            return
            
        if row < self.table_proxies.rowCount():
            item = self.table_proxies.item(row, 4)
            if item:
                item.setText(str(count))
                if count > 0:
                    item.setForeground(Qt.green)
                else:
                    item.setForeground(Qt.gray)
                    
        # Cập nhật nút bấm text
        if done % 5 == 0 or done == total:
            self.btn_count_conn.setText(f"⏳ {done}/{total}")

    def copy_proxies(self):
        text = ""
        for row in range(self.table_proxies.rowCount()):
            item = self.table_proxies.item(row, 1)
            if item:
                text += item.text() + "\n"
                
        if text.strip():
            QApplication.clipboard().setText(text.strip())
            ThemedMessageBox.show_info(self, "Thành công", f"Đã chép {self.table_proxies.rowCount()} Proxy vào khay nhớ tạm!")
        else:
            ThemedMessageBox.show_warning(self, _("WARN_TITLE"), "Bảng đang trống!")

    def open_exported_list(self):
        export_file = "exported_proxies.txt"
        if os.path.exists(export_file):
            os.startfile(export_file)
        else:
            ThemedMessageBox.show_info(self, "Chưa Tạo Proxy", "Chưa có file proxy nào được lưu!")

    # --------------- CHỨC NĂNG CỨU HỘ & TƯỜNG LỬA ---------------
    def tool_clean_ipv6(self):
        iface = self.cb_interface.currentText()
        base_ip = self.cb_ipv6.currentText()
        if not iface:
            ThemedMessageBox.show_warning(self, _("ERR_TITLE"), "Vui lòng đợi Interface load xong mạng.")
            return
            
        ans = ThemedMessageBox.show_question(self, "Xác nhận xóa IPv6", 
            f"Thao tác này sẽ càn quét Interface '{iface}' và xóa sạch toàn bộ IPv6 tồn tại (NGOẠI TRỪ cái IP gốc bạn đang chọn là {base_ip}). Lợi ích là giúp máy nhẹ gánh mạng, không bị quá tải IP.\n\nTiếp tục xử lý?")
            
        if ans:
            self.handle_status_update("Trạng thái: Đang càn quét và dọn 10,000+ IPv6 rác (Vui lòng chờ)...", "#f9e2af")
            QApplication.processEvents()
            
            # Lấy list IP cần xóa
            cmd = f"powershell \"Get-NetIPAddress -InterfaceAlias '{iface}' -AddressFamily IPv6 | Where-Object {{ $_.IPAddress -notmatch '^fe80' -and $_.IPAddress -ne '{base_ip}' }} | Select-Object -ExpandProperty IPAddress\""
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            ips_to_remove = [ip.strip() for ip in proc.stdout.split('\n') if ip.strip()]
            
            if ips_to_remove:
                script_file = "tool_del_ips.txt"
                with open(script_file, "w") as f:
                    for ip in ips_to_remove:
                        f.write(f'interface ipv6 delete address interface="{iface}" address="{ip}"\n')
                
                proc2 = subprocess.Popen(f'netsh -f "{script_file}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                while proc2.poll() is None:
                    QApplication.processEvents()
                    time.sleep(0.05)
                try: os.remove(script_file)
                except: pass
            
            self.active_ips = []
            self.handle_status_update("Trạng thái: Đã dọn sạch IPv6 rác, máy cực mượt!", "#a6e3a1")
            ThemedMessageBox.show_info(self, "Hoàn tất", f"Đã xóa sạch IP rác trên cổng {iface}. Máy đã nhẹ nhàng hơn!")

    def tool_kill_ports(self):
        cmd = "taskkill /F /IM 3proxy.exe /T"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.stopped_running_state()
        
        self.handle_status_update("Trạng thái: Đã tiêu diệt 3Proxy ẩn kẹt trong máy!", "#a6e3a1")
        if "SUCCESS" in res.stdout or "thành công" in res.stdout.lower() or "đã kết thúc" in res.stdout.lower() or "đã hủy" in res.stdout.lower():
            ThemedMessageBox.show_info(self, "Thành công", "Đã diệt sạch các tiến trình 3proxy.exe rác đang ngậm kẹt Port!")
        else:
            ThemedMessageBox.show_info(self, "Hoàn tất", "Máy rất sạch, không có tiến trình 3proxy rác nào đang kẹt.")
            
    def tool_open_firewall(self):
        exe_path = os.path.abspath(r"3proxy\bin64\3proxy.exe")
        if not os.path.exists(exe_path):
            exe_path = os.path.abspath("3proxy.exe")
            
        # Add Firewall Rules (In/Out) Allow 3proxy
        r1 = f'netsh advfirewall firewall add rule name="3Proxy Allow IN" dir=in action=allow program="{exe_path}" enable=yes profile=any'
        r2 = f'netsh advfirewall firewall add rule name="3Proxy Allow OUT" dir=out action=allow program="{exe_path}" enable=yes profile=any'
        
        subprocess.run(r1, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(r2, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        self.handle_status_update("Trạng thái: Đục lỗ Tường Lửa cho Proxy thành công!", "#a6e3a1")
        ThemedMessageBox.show_info(self, "Thành công", f"Đã mở cửa Firewall IN/OUT cho 3proxy.exe mượt mà!\n\nBây giờ Proxy của bạn đã thâm nhập được từ bên ngoài VPS / Lan nếu bật Public Proxy.")

    # --------------- HỆ THỐNG PROXY ENGINE ---------------
    def add_ips_batch(self, ips, interface):
        if not ips: return
        script_file = "add_ips.txt"
        with open(script_file, "w") as f:
            for ip in ips:
                f.write(f'interface ipv6 add address interface="{interface}" address="{ip}"\n')
        
        proc = subprocess.Popen(f'netsh -f "{script_file}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        while proc.poll() is None:
            QApplication.processEvents()
            time.sleep(0.05)
            
        try: os.remove(script_file)
        except: pass

    def create_proxy_batch(self, force_new=False):
        try:
            start_port = self.sp_start_port.value()
            count = int(self.le_proxy_count.text())
            prefix_len = self.netmask_group.checkedId()
        except ValueError:
            ThemedMessageBox.show_critical(self, "Lỗi", "Vui lòng nhập số lượng Proxy hợp lệ!")
            return False

        iface = self.cb_interface.currentText()
        base_ipv6 = self.cb_ipv6.currentText()
        if not iface or not base_ipv6: return False

        self.cleanup_ips()
        
        proxy_list = []
        old_proxies_file = "last_proxies.json"
        
        ips_to_add = []
        input_ip = "0.0.0.0" if self.chk_public.isChecked() else "127.0.0.1"

        if not force_new and self.chk_recreate.isChecked() and os.path.exists(old_proxies_file):
            try:
                with open(old_proxies_file, "r") as f:
                    old_list = json.load(f)
                # Giữ lại proxy cũ, tối đa bằng count
                kept = old_list[:count]
                for p in kept:
                    ips_to_add.append(p['out_ip'])
                    self.active_ips.append({"ip": p['out_ip'], "interface": iface})
                    proxy_list.append(p)
            except Exception:
                pass

        self.handle_status_update(f"Trạng thái: Đang nạp {count} IP vào card mạng...", "#f9e2af")
        QApplication.processEvents()

        # Nếu còn thiếu so với count thì tạo thêm proxy mới
        remaining = count - len(proxy_list)
        if remaining > 0:
            try:
                network = ipaddress.IPv6Network(f"{base_ipv6}/{prefix_len}", strict=False)
                network_int = int(network.network_address)
            except Exception as e:
                ThemedMessageBox.show_critical(self, "Lỗi Subnet", f"Không thể tính dải IP từ IPv6 cung cấp:\n{e}")
                return False

            next_port = proxy_list[-1]['port'] + 1 if proxy_list else start_port
            
            for i in range(remaining):
                random_host = random.getrandbits(128 - prefix_len)
                new_ipv6 = str(ipaddress.IPv6Address(network_int + random_host))
                ips_to_add.append(new_ipv6)
                self.active_ips.append({"ip": new_ipv6, "interface": iface})
                proxy_list.append({"port": next_port + i, "in_ip": input_ip, "out_ip": new_ipv6})

        try:
            with open(old_proxies_file, "w") as f:
                json.dump(proxy_list, f)
        except Exception: pass
            
        self.add_ips_batch(ips_to_add, iface)

        # Config cho 3proxy
        config_path = "3proxy.cfg"
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("maxconn 500\nnscache 65536\nflush\n\n")
            if self.chk_no_sec.isChecked():
                f.write("auth none\n")
            else:
                user = self.le_user.text().strip()
                password = self.le_password.text().strip()
                f.write("auth strong\n")
                if user and password: f.write(f"users {user}:CL:{password}\n")
            f.write("allow *\n\n")
            for p in proxy_list:
                if p['in_ip'] == "0.0.0.0":
                    f.write(f"proxy -6 -n -a -p{p['port']} -e{p['out_ip']}\n")
                else:
                    f.write(f"proxy -6 -n -a -p{p['port']} -i{p['in_ip']} -e{p['out_ip']}\n")
                
        self.export_proxies_to_txt(proxy_list)
        self.update_table_view(proxy_list)
        return True

    def export_proxies_to_txt(self, proxy_list):
        export_file = "exported_proxies.txt"
        display_ip = get_public_ip() if self.chk_public.isChecked() else "127.0.0.1"
            
        with open(export_file, "w", encoding="utf-8") as f:
            if not self.chk_no_sec.isChecked() and self.le_user.text():
                for p in proxy_list:
                    f.write(f"{display_ip}:{p['port']}:{self.le_user.text()}:{self.le_password.text()}\n")
            else:
                for p in proxy_list:
                    f.write(f"{display_ip}:{p['port']}\n")

    def toggle_process(self):
        if self.running:
            self.stop_proxy()
        else:
            self.start_proxy()

    def start_proxy(self):
        success = self.create_proxy_batch(force_new=False)
        if not success: return

        try:
            exe_path = r"3proxy\bin64\3proxy.exe"
            if not os.path.exists(exe_path): exe_path = "3proxy.exe"
            
            self.process = subprocess.Popen([exe_path, "3proxy.cfg"], creationflags=subprocess.CREATE_NO_WINDOW)
            self.running = True
            
            self.btn_action.setText(_("BTN_STOP_PROXY_CLEAN"))
            self.set_button_class(self.btn_action, "danger")
            self.handle_status_update(_("STATUS_RUNNING"), "#a6e3a1")

            self.cb_interface.setEnabled(False)
            self.cb_ipv6.setEnabled(False)

            if not self.chk_no_rot.isChecked():
                self.rotation_thread = threading.Thread(target=self.rotation_worker, daemon=True)
                self.rotation_thread.start()
        except Exception as e:
            ThemedMessageBox.show_critical(self, "Lỗi khởi chạy", f"Có lỗi khi bật 3proxy: {e}")
            self.cleanup_ips()

    def stopped_running_state(self):
        self.running = False
        self.btn_action.setText(_("BTN_START_PROXY"))
        self.set_button_class(self.btn_action, "primary")
        self.cb_interface.setEnabled(True)
        self.cb_ipv6.setEnabled(True)

    def stop_proxy(self):
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            
        self.cleanup_ips()
        self.stopped_running_state()
        self.handle_status_update(_("STATUS_STOPPED"), "#f38ba8")

    def cleanup_ips(self):
        if not self.active_ips: return
        
        ifaces = {}
        for item in self.active_ips:
            iface = item["interface"]
            if iface not in ifaces: ifaces[iface] = []
            ifaces[iface].append(item["ip"])
            
        script_file = "del_ips.txt"
        with open(script_file, "w") as f:
            for iface, ips in ifaces.items():
                for ip in ips:
                    f.write(f'interface ipv6 delete address interface="{iface}" address="{ip}"\n')
        
        proc = subprocess.Popen(f'netsh -f "{script_file}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        while proc.poll() is None:
            QApplication.processEvents()
            time.sleep(0.05)
            
        try: os.remove(script_file)
        except: pass
        self.active_ips = []

    def rotation_worker(self):
        try: minutes = self.sp_rotation_time.value()
        except: minutes = 10
        seconds_to_wait = minutes * 60
        
        while self.running:
            for _ in range(seconds_to_wait):
                if not self.running: return
                time.sleep(1)
            
            if not self.running: return
                
            self.update_status_signal.emit("Trạng thái: Đang xoay IP (Rotation)...", "#f9e2af")
            if self.process:
                self.process.terminate()
                self.process.wait()
            
            if self.create_proxy_batch(force_new=True):
                self.process = subprocess.Popen([r"3proxy\bin64\3proxy.exe", "3proxy.cfg"], creationflags=subprocess.CREATE_NO_WINDOW)
                self.update_status_signal.emit(f"Trạng thái: Proxy hoạt động (Đã xoay lúc {time.strftime('%H:%M:%S')})", "#a6e3a1")
            else:
                self.stop_proxy()
                break

    def closeEvent(self, event):
        if self.running: self.stop_proxy()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
