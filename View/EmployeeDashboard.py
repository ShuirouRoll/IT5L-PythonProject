import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox
)
from Project.View.Dialogs import ChangeCredentialsDialog, CompactMessageDialog, LeaveRequestDialog


class EmployeeDashboard(QMainWindow):
    def __init__(self, employee_data):
        super().__init__()
        self.employee_data = employee_data
        self.employee_id = employee_data.get('id')
        self.setWindowTitle("Employee Portal")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #f5f5f5;")
        self.build_ui()
        self.start_clock_timer()

    def closeEvent(self, event):
        """Handle window close event with confirmation - FIXED"""
        reply = QMessageBox.question(
            self,
            'Exit Confirmation',
            'Are you sure you want to exit?',  # This text was there but might not show
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Header with time (centered)
        header = QFrame()
        header.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e0e0e0;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setSpacing(10)

        welcome = QLabel(f"Hello, {self.employee_data.get('full_name')}!")
        welcome.setStyleSheet("font-size: 26px; font-weight: bold; color: #1a1a1a;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.time_label = QLabel("00:00:00 AM")
        self.time_label.setStyleSheet("font-size: 20px; color: #666; font-family: monospace;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(welcome)
        header_layout.addWidget(self.time_label)
        main_layout.addWidget(header)

        # Clock Actions Card
        clock_card = QFrame()
        clock_card.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e0e0e0;")
        clock_layout = QVBoxLayout(clock_card)
        clock_layout.setContentsMargins(30, 30, 30, 30)
        clock_layout.setSpacing(20)

        actions_title = QLabel("Attendance Actions")
        actions_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1a1a1a;")
        actions_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clock_layout.addWidget(actions_title)

        # Clock In Button
        self.btn_clock_in = QPushButton("🕐 Clock In")
        self.btn_clock_in.setFixedHeight(60)
        self.btn_clock_in.setStyleSheet("""
            QPushButton {
                background-color: #10B981; 
                color: white; 
                border-radius: 8px; 
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.btn_clock_in.clicked.connect(self.handle_clock_in)

        # Clock Out Button
        self.btn_clock_out = QPushButton("🕐 Clock Out")
        self.btn_clock_out.setFixedHeight(60)
        self.btn_clock_out.setStyleSheet("""
            QPushButton {
                background-color: #EF4444; 
                color: white; 
                border-radius: 8px; 
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.btn_clock_out.clicked.connect(self.handle_clock_out)

        clock_layout.addWidget(self.btn_clock_in)
        clock_layout.addWidget(self.btn_clock_out)
        main_layout.addWidget(clock_card)

        main_layout.addStretch()

        # Bottom buttons row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(15)

        # Change Credentials Button
        btn_credentials = QPushButton("🔒 Change Credentials")
        btn_credentials.setFixedHeight(50)
        btn_credentials.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6; 
                color: white; 
                border-radius: 8px; 
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        btn_credentials.clicked.connect(self.open_change_credentials)

        # Request Leave Button
        self.btn_leave = QPushButton("📋 Request Leave")
        self.btn_leave.setFixedHeight(50)
        self.btn_leave.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B; 
                color: white; 
                border-radius: 8px; 
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
        """)
        self.btn_leave.clicked.connect(self.open_leave_request)

        # Log Out Button
        btn_logout = QPushButton("🚪 Log Out")
        btn_logout.setFixedHeight(50)
        btn_logout.setStyleSheet("""
            QPushButton {
                border: 2px solid #666; 
                color: #666; 
                background: white;
                border-radius: 8px; 
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
            }
        """)
        btn_logout.clicked.connect(self.close)

        bottom_row.addWidget(btn_credentials)
        bottom_row.addWidget(self.btn_leave)
        bottom_row.addWidget(btn_logout)

        main_layout.addLayout(bottom_row)

    def open_change_credentials(self):
        from Project.View.Dialogs import ChangeCredentialsDialog, CompactMessageDialog
        from Project.Controller.EmployeeC import EmployeeController
        from Project.Model.Database import Database
        from Project.Model.Employee import Employee
        import secrets

        dialog = ChangeCredentialsDialog(self)
        if dialog.exec() and dialog.credentials_data:
            try:
                # Get current employee's stored hash and salt
                db = Database.get()
                user = db.query_one(
                    "SELECT username, password_hash, salt FROM employees WHERE id = %s",
                    (self.employee_id,)
                )

                if not user:
                    CompactMessageDialog.show_warning(self, "Error", "Employee not found.")
                    return

                # DEBUG: Print information
                print(f"\n=== PASSWORD CHANGE DEBUG ===")
                print(f"Employee ID: {self.employee_id}")
                print(f"Username from DB: {user['username']}")
                print(f"Input password: '{dialog.credentials_data['current']}'")
                print(f"Stored hash (first 20 chars): {user['password_hash'][:20]}...")
                print(f"Stored salt (first 10 chars): {user['salt'][:10]}...")

                # Verify current password using hash comparison
                salt = bytes.fromhex(user['salt'])
                input_hash = Employee.hash_password(dialog.credentials_data["current"], salt)

                print(f"Generated hash (first 20 chars): {input_hash[:20]}...")
                print(f"Hashes match: {secrets.compare_digest(input_hash, user['password_hash'])}")
                print(f"=== END DEBUG ===\n")

                if not secrets.compare_digest(input_hash, user['password_hash']):
                    CompactMessageDialog.show_warning(self, "Error", "Current password incorrect.")
                    return

                # Update credentials (this method properly handles password hashing)
                EmployeeController.update_employee(self.employee_id, {
                    'username': dialog.credentials_data["username"],
                    'password': dialog.credentials_data["password"]
                })

                CompactMessageDialog.show_success(self, "Success",
                                                  "Credentials updated. Please login again.")
                self.close()

            except Exception as e:
                print(f"[EmployeeDashboard] Error changing credentials: {e}")
                import traceback
                traceback.print_exc()
                CompactMessageDialog.show_warning(self, "Error", str(e))


    def start_clock_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        from datetime import datetime
        self.time_label.setText(datetime.now().strftime("%I:%M:%S %p"))

    def handle_clock_in(self):
        from Project.Controller.AttendanceC import AttendanceController
        res = AttendanceController.clock_in(self.employee_id)
        if res['success']:
            CompactMessageDialog.show_success(self, "Success", res['message'])
        else:
            CompactMessageDialog.show_warning(self, "Error", res['message'])

    def handle_clock_out(self):
        from Project.Controller.AttendanceC import AttendanceController
        res = AttendanceController.clock_out(self.employee_id)
        if res['success']:
            CompactMessageDialog.show_success(self, "Success", res['message'])
        else:
            CompactMessageDialog.show_warning(self, "Error", res['message'])

    def open_leave_request(self):
        from Project.Controller.RequestC import LeaveRequestController

        dialog = LeaveRequestDialog(self)
        if dialog.exec():
            data = dialog.data
            success = LeaveRequestController.submit_request(
                self.employee_id,
                data['type'],
                data['start'],
                data['end'],
                data['reason']
            )

            if success:
                CompactMessageDialog.show_success(self, "Submitted", "Leave request sent for approval.")
            else:
                CompactMessageDialog.show_warning(self, "Error", "Failed to submit request.")