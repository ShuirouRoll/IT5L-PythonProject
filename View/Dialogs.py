from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox, QFrame, QComboBox, QDateEdit, QTextEdit,
    QTimeEdit, QSpinBox
)


# --- Helper to load positions ---
def get_position_items():
    try:
        from Project.Controller.PositionC import PositionController
        return PositionController.get_all_positions()
    except:
        return []


# --- BASE DIALOG STYLE (Fixed All Text Colors) ---
class BaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # FIXED: All text colors set to black for visibility
        self.setStyleSheet("""
            QDialog { 
                background-color: #ffffff; 
            }
            QLabel { 
                color: #1a1a1a !important;
                font-weight: 500; 
                font-size: 13px;
                background: transparent;
                border: none;
            }
            QLineEdit, QDateEdit, QTextEdit, QTimeEdit, QSpinBox {
                background-color: #ffffff;
                color: #1a1a1a !important;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus, QDateEdit:focus, QTextEdit:focus, QTimeEdit:focus, QSpinBox:focus {
                border: 2px solid #3b82f6;
            }
            QComboBox {
                background-color: #ffffff;
                color: #1a1a1a !important;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                min-height: 30px;
            }
            QComboBox:focus {
                border: 2px solid #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #1a1a1a;
                width: 0;
                height: 0;
                margin-right: 8px;
            }
           QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #1a1a1a !important;
                selection-background-color: #3b82f6;
                selection-color: #ffffff !important;
                border: 1px solid #d1d5db;
                padding: 4px;
            }
            QPushButton { 
                font-weight: bold; 
                font-size: 14px;
                color: #ffffff !important;
            }
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QLabel {
                color: #1a1a1a !important;
            }
            QCalendarWidget QWidget {
                background-color: #ffffff;
                color: #1a1a1a !important;
            }
            QCalendarWidget QTableView {
                background-color: #ffffff;
                color: #1a1a1a !important;
                selection-background-color: #3b82f6;
                selection-color: #ffffff !important;
            }
            QCalendarWidget QAbstractItemView {
                background-color: #ffffff;
                color: #1a1a1a !important;
                selection-background-color: #3b82f6;
                selection-color: #ffffff !important;
            }
            QCalendarWidget QMenu {
                background-color: #ffffff;
                color: #1a1a1a !important;
            }
            QCalendarWidget QSpinBox {
                background-color: #ffffff;
                color: #1a1a1a !important;
            }
            QCalendarWidget QToolButton {
                background-color: #ffffff;
                color: #1a1a1a !important;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #1a1a1a !important;
            }
            QCalendarWidget QTableView QHeaderView::section {
                background-color: #f3f4f6;
                color: #1a1a1a !important;
            }""")


# --- ADD POSITION ---
class AddPositionDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Position")
        self.setFixedSize(400, 380)
        self.new_position_name = None
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("Create Position")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1a1a !important;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Position Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Late Cutoff Time:"))
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("hh:mm AP")
        self.time_input.setTime(QTime(8, 0))
        layout.addWidget(self.time_input)

        layout.addWidget(QLabel("Grace Period (Minutes):"))
        self.grace_input = QSpinBox()
        self.grace_input.setRange(0, 60)
        self.grace_input.setValue(15)
        layout.addWidget(self.grace_input)

        layout.addStretch()

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Position")
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet("background-color: #2563eb; color: white !important; border-radius: 8px;")
        save_btn.clicked.connect(self.on_save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def on_save(self):
        name = self.name_input.text().strip()
        if not name: return
        try:
            from Project.Controller.PositionC import PositionController
            success, msg = PositionController.add_position(name, self.time_input.time().toString("HH:mm:ss"),
                                                           self.grace_input.value())
            if success:
                self.new_position_name = name
                self.accept()
            else:
                CompactMessageDialog.show_warning(self, "Error", msg)
        except Exception as e:
            CompactMessageDialog.show_warning(self, "Error", str(e))


# --- ADD EMPLOYEE ---
class AddEmployeeDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Employee")
        self.setFixedSize(450, 780)
        self.employee_data = None
        self.positions = get_position_items()
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)

        title = QLabel("Add New Employee")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a1a1a !important;")
        layout.addWidget(title)
        layout.addSpacing(10)

        self.first_name_input = QLineEdit()
        self.add_field(layout, "First Name *", self.first_name_input)

        self.last_name_input = QLineEdit()
        self.add_field(layout, "Last Name *", self.last_name_input)

        # Position Row
        layout.addWidget(QLabel("Position *"))
        pos_row = QHBoxLayout()
        self.position_combo = QComboBox()
        self.position_combo.setFixedHeight(40)
        self.refresh_positions()

        add_pos_btn = QPushButton("+")
        add_pos_btn.setFixedSize(40, 40)
        add_pos_btn.setStyleSheet("background-color: #10B981; color: white !important; border-radius: 8px;")
        add_pos_btn.clicked.connect(self.open_add_position)

        pos_row.addWidget(self.position_combo)
        pos_row.addWidget(add_pos_btn)
        layout.addLayout(pos_row)

        self.email_input = QLineEdit()
        self.add_field(layout, "Email *", self.email_input)

        self.phone_input = QLineEdit()
        self.add_field(layout, "Phone *", self.phone_input)

        self.username_input = QLineEdit()
        self.add_field(layout, "Username *", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.add_field(layout, "Password *", self.password_input)

        layout.addSpacing(15)
        save_btn = QPushButton("Save Employee")
        save_btn.setFixedHeight(45)
        save_btn.setStyleSheet("background-color: #2563eb; color: white !important; border-radius: 8px;")
        save_btn.clicked.connect(self.on_save)
        layout.addWidget(save_btn)

    def add_field(self, layout, text, widget):
        layout.addWidget(QLabel(text))
        widget.setFixedHeight(40)
        layout.addWidget(widget)

    def refresh_positions(self, selected=None):
        self.positions = get_position_items()
        self.position_combo.clear()
        for pos in self.positions:
            self.position_combo.addItem(pos['name'], pos['id'])
        if selected:
            idx = self.position_combo.findText(selected)
            if idx >= 0: self.position_combo.setCurrentIndex(idx)

    def open_add_position(self):
        dialog = AddPositionDialog(self)
        if dialog.exec(): self.refresh_positions(dialog.new_position_name)

    def on_save(self):
        if not self.first_name_input.text(): return
        if self.position_combo.count() == 0:
            CompactMessageDialog.show_warning(self, "Error", "No positions available. Create a position first.")
            return
        self.employee_data = {
            "first_name": self.first_name_input.text(),
            "last_name": self.last_name_input.text(),
            "email_address": self.email_input.text(),
            "phone_number": self.phone_input.text(),
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "position_id": self.position_combo.currentData()
        }
        self.accept()


# --- EDIT EMPLOYEE ---
class EditEmployeeDialog(BaseDialog):
    def __init__(self, employee_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Employee")
        self.setFixedSize(450, 700)
        self.employee_data = employee_data
        self.updated_data = None
        self.positions = get_position_items()
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)

        title = QLabel(f"Edit: {self.employee_data.get('full_name')}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a1a1a !important;")
        layout.addWidget(title)
        layout.addSpacing(10)

        # Position
        layout.addWidget(QLabel("Position"))
        pos_row = QHBoxLayout()
        self.position_combo = QComboBox()
        self.position_combo.setFixedHeight(40)
        self.refresh_positions()
        current = self.employee_data.get('position', 'Staff')
        idx = self.position_combo.findText(current)
        if idx >= 0: self.position_combo.setCurrentIndex(idx)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(40, 40)
        add_btn.setStyleSheet("background-color: #10B981; color: white !important; border-radius: 8px;")
        add_btn.clicked.connect(self.open_add_position)
        pos_row.addWidget(self.position_combo)
        pos_row.addWidget(add_btn)
        layout.addLayout(pos_row)

        self.email_input = QLineEdit(self.employee_data.get('email_address'))
        self.add_field(layout, "Email", self.email_input)
        self.phone_input = QLineEdit(self.employee_data.get('phone_number'))
        self.add_field(layout, "Phone", self.phone_input)
        self.username_input = QLineEdit(self.employee_data.get('username'))
        self.add_field(layout, "Username", self.username_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Leave blank to keep current")
        self.add_field(layout, "New Password", self.password_input)

        layout.addStretch()
        save_btn = QPushButton("Update")
        save_btn.setFixedHeight(45)
        save_btn.setStyleSheet("background-color: #2563eb; color: white !important; border-radius: 8px;")
        save_btn.clicked.connect(self.on_save)
        layout.addWidget(save_btn)

    def add_field(self, layout, text, widget):
        layout.addWidget(QLabel(text))
        widget.setFixedHeight(40)
        layout.addWidget(widget)

    def refresh_positions(self, selected=None):
        self.positions = get_position_items()
        self.position_combo.clear()
        for pos in self.positions: self.position_combo.addItem(pos['name'], pos['id'])
        if selected:
            idx = self.position_combo.findText(selected)
            if idx >= 0: self.position_combo.setCurrentIndex(idx)

    def open_add_position(self):
        dialog = AddPositionDialog(self)
        if dialog.exec(): self.refresh_positions(dialog.new_position_name)

    def on_save(self):
        self.updated_data = {
            "employee_id": self.employee_data.get("id"),
            "email": self.email_input.text(),
            "phone": self.phone_input.text(),
            "username": self.username_input.text(),
            "password": self.password_input.text() if self.password_input.text() else None,
            "position_id": self.position_combo.currentData()
        }
        self.accept()


# --- LEAVE REQUEST ---
class LeaveRequestDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Submit Request")
        self.setFixedSize(450, 650)
        self.data = None
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Request Reason:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Vacation Leave", "Sick Leave", "Others"])
        self.type_combo.setFixedHeight(40)
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedHeight(40)
        layout.addWidget(self.start_date)

        layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedHeight(40)
        layout.addWidget(self.end_date)

        layout.addWidget(QLabel("In-Depth Reasoning:"))
        self.reason_input = QTextEdit()
        layout.addWidget(self.reason_input)

        btn = QPushButton("Submit")
        btn.setFixedHeight(45)
        btn.setStyleSheet("background-color: #2563eb; color: white !important; border-radius: 8px;")
        btn.clicked.connect(self.submit)
        layout.addWidget(btn)

    def submit(self):
        if not self.reason_input.toPlainText().strip():
            CompactMessageDialog.show_warning(self, "Error", "Provide a reason.")
            return
        self.data = {
            "type": self.type_combo.currentText(),
            "start": self.start_date.date().toString("yyyy-MM-dd"),
            "end": self.end_date.date().toString("yyyy-MM-dd"),
            "reason": self.reason_input.toPlainText()
        }
        self.accept()


# --- REQUEST DETAILS ---
class RequestDetailsDialog(BaseDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Details")
        self.setFixedSize(500, 550)
        self.data = data
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        layout.addWidget(QLabel("Employee Name"))
        layout.addWidget(self.lbl(self.data.get('employee_name')))

        layout.addWidget(QLabel("Type"))
        layout.addWidget(self.lbl(self.data.get('leave_type')))

        layout.addWidget(QLabel("Dates"))
        layout.addWidget(self.lbl(f"{self.data.get('start_date')} to {self.data.get('end_date')}"))

        layout.addWidget(QLabel("Reason"))
        reason = QTextEdit()
        reason.setPlainText(self.data.get('reason', ''))
        reason.setReadOnly(True)
        layout.addWidget(reason)

        btn = QPushButton("Close")
        btn.setFixedHeight(40)
        btn.setStyleSheet("background-color: #6b7280; color: white !important; border-radius: 8px;")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)

    def lbl(self, text):
        l = QLabel(str(text))
        l.setStyleSheet("background: #f9f9f9; padding: 10px; border: 1px solid #ddd; border-radius: 6px; color: #1a1a1a !important;")
        return l


# --- CREDENTIALS ---
class ChangeCredentialsDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Credentials")
        self.setFixedSize(450, 500)
        self.credentials_data = None
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        layout.addWidget(QLabel("New Username"))
        self.new_user = QLineEdit()
        layout.addWidget(self.new_user)

        layout.addWidget(QLabel("Current Password"))
        self.curr_pass = QLineEdit()
        self.curr_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.curr_pass)

        layout.addWidget(QLabel("New Password"))
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_pass)

        layout.addWidget(QLabel("Confirm Password"))
        self.conf_pass = QLineEdit()
        self.conf_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.conf_pass)

        layout.addStretch()
        btn = QPushButton("Update")
        btn.setFixedHeight(45)
        btn.setStyleSheet("background-color: #2563eb; color: white !important; border-radius: 8px;")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)

    def save(self):
        if not self.curr_pass.text() or not self.new_user.text(): return
        self.credentials_data = {
            "username": self.new_user.text(),
            "current": self.curr_pass.text(),
            "password": self.new_pass.text()
        }
        self.accept()


class CompactMessageDialog(BaseDialog):
    @staticmethod
    def show_success(parent, title, msg):
        d = CompactMessageDialog(parent)
        d.setWindowTitle(title)
        d.setFixedSize(400, 200)
        l = QVBoxLayout(d)
        l.setContentsMargins(30, 30, 30, 30)
        l.setSpacing(20)

        msg_label = QLabel(f"✅ {msg}")
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px; color: #1a1a1a !important;")
        l.addWidget(msg_label)

        b = QPushButton("OK")
        b.setFixedHeight(45)
        b.setStyleSheet("""
            QPushButton {
                background-color: #10B981; 
                color: white !important; 
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        b.clicked.connect(d.accept)
        l.addWidget(b)
        d.exec()

    @staticmethod
    def show_warning(parent, title, msg):
        d = CompactMessageDialog(parent)
        d.setWindowTitle(title)
        d.setFixedSize(400, 200)
        l = QVBoxLayout(d)
        l.setContentsMargins(30, 30, 30, 30)
        l.setSpacing(20)

        msg_label = QLabel(f"⚠️ {msg}")
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px; color: #1a1a1a !important;")
        l.addWidget(msg_label)

        b = QPushButton("OK")
        b.setFixedHeight(45)
        b.setStyleSheet("""
            QPushButton {
                background-color: #EF4444; 
                color: white !important; 
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        b.clicked.connect(d.accept)
        l.addWidget(b)
        d.exec()

    @staticmethod
    def show_logout_confirm(parent):
        """Fixed logout confirmation dialog with black text"""
        return CompactMessageDialog.show_confirmation(parent, "Logout", "Are you sure you want to logout?")

    @staticmethod
    def show_exit_confirm(parent):
        """Fixed exit confirmation dialog with black text"""
        return CompactMessageDialog.show_confirmation(parent, "Exit Confirmation", "Are you sure you want to exit?")

    @staticmethod
    def show_confirmation(parent, title, text):
        """Generic confirmation dialog with forced black text style"""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QLabel {
                color: #1a1a1a !important;
                font-size: 14px;
                background: transparent;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white !important;
                border-radius: 6px;
                padding: 6px 20px;
                font-weight: bold;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        return msg.exec() == QMessageBox.StandardButton.Yes