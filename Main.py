import sys
import os

# CRITICAL: Set these BEFORE any PyQt6 imports
os.environ['QT_QPA_PLATFORM'] = 'windows'
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

# Import Views
from Project.View.LoginBoard import LoginBoard
from Project.View.Sidebar import Sidebar
from Project.View.Header import Header
from Project.View.MainWindow import MainWindow
from Project.View.DashboardPage import DashboardPage
from Project.View.EmployeesPage import EmployeesPage
from Project.View.ReportsPage import ReportsPage
from Project.View.RequestPage import RequestsPage
from Project.View.SettingsPage import SettingsPage

# Import Controllers
from Project.Controller.MainC import MainController
from Project.Controller.EmployeeC import EmployeeController
from Project.Controller.AttendanceC import AttendanceController
from Project.Controller.ReportsC import ReportController
from Project.Controller.PositionC import PositionController
from Project.Controller.RequestC import LeaveRequestController

# Import Scheduler
try:
    from Project.Controller.DailyScheduler import start_scheduler, stop_scheduler, get_status

    SCHEDULER_AVAILABLE = True
    print("[Boot] Scheduler module imported successfully")
except ImportError as e:
    print(f"[Boot] Warning: Scheduler not available - {e}")
    SCHEDULER_AVAILABLE = False

# Import Models
from Project.Model.Database import Database
from Project.Model.Admin import Admin
from Project.Model.Employee import Employee
from Project.Model.Positions import Position
from Project.Model.Attendance import Attendance
from Project.Model.Reports import Reports
from Project.Model.PeriodicReports import PeriodicReports
from Project.Model.Request import LeaveRequest

# === GLOBAL STYLESHEET TO FIX INVISIBLE TEXT IN DIALOGS ===
GLOBAL_STYLESHEET = """
    QMessageBox {
        background-color: #ffffff;
    }
    QMessageBox QLabel {
        color: #1a1a1a !important; /* Force Black Text */
        font-size: 14px;
    }
    QMessageBox QPushButton {
        background-color: #f3f4f6;
        color: #1a1a1a;
        border: 1px solid #d1d5db;
        border-radius: 5px;
        padding: 6px 18px;
        font-weight: 600;
        min-width: 80px;
    }
    QMessageBox QPushButton:hover {
        background-color: #e5e7eb;
        border-color: #9ca3af;
    }
    QMessageBox QPushButton:pressed {
        background-color: #d1d5db;
    }
"""


def show_login_success_dialog(parent, user_type, user_name):
    """Show a success dialog after login with fixed text color"""
    try:
        msg = QMessageBox(parent)
        msg.setWindowTitle("Login Successful")
        msg.setIcon(QMessageBox.Icon.Information)

        if user_type == "admin":
            msg.setText(f"Welcome back, {user_name}!")
            msg.setInformativeText("You are logged in as Administrator")
        else:
            msg.setText(f"Welcome, {user_name}!")
            msg.setInformativeText("You are logged in as Employee")

        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    except Exception as e:
        print(f"[Main] Dialog error: {e}")


def print_scheduler_status():
    """Print scheduler status (optional)"""
    if not SCHEDULER_AVAILABLE:
        return

    try:
        status = get_status()
        print("\n[Scheduler] Status Report:")
        print(f"  Running: {status['running']}")
        print(f"  Absent marking at: {status['absent_time']}")
        print(f"  Report generation at: {status['report_time']}")
        print(f"  Last absent run: {status['absent_last_run']}")
        print(f"  Last report run: {status['report_last_run']}\n")
    except Exception as e:
        print(f"[Scheduler] Error getting status: {e}")
        import traceback
        traceback.print_exc()


def get_resource_path(relative_path):
    """Get absolute path to resource - works for dev and PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main():
    print("[Boot] Importing modules...")
    print("[Boot] Imports successful.")
    print("[Boot] Starting Application...")

    # Create application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # APPLY GLOBAL STYLESHEET HERE
    app.setStyleSheet(GLOBAL_STYLESHEET)

    # Set application icon if available
    try:
        icon_path = get_resource_path('Project/Resources/logo_black.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except Exception as e:
        print(f"[Boot] Icon loading warning: {e}")

    # Logo paths
    logo_paths = {
        'white': r'C:\Users\Shuirou\PycharmProjects\PythonProject\Project\ui and stuff\WLogo.png',
        'black': r'C:\Users\Shuirou\PycharmProjects\PythonProject\Project\ui and stuff\Logo.png',
        'dark': r'C:\Users\Shuirou\PycharmProjects\PythonProject\Project\ui and stuff\Logo.png',
        'overview': r'C:\Users\Shuirou\PycharmProjects\PythonProject\Project\ui and stuff\OverviewLogo.png',
        'employee': r'C:\Users\Shuirou\PycharmProjects\PythonProject\Project\ui and stuff\EmployeeLogo.png',
        'reports': r'C:\Users\Shuirou\PycharmProjects\PythonProject\Project\ui and stuff\ReportsLogo.png',
        'requests': r'C:\Users\Shuirou\PycharmProjects\PythonProject\Project\ui and stuff\Request.png',
        'settings': r'C:\Users\Shuirou\PycharmProjects\PythonProject\Project\ui and stuff\SettingsLogo.png'
    }

    # Verify logo paths exist
    print("[Boot] Verifying logo paths...")
    for key, path in logo_paths.items():
        if os.path.exists(path):
            print(f" ✓ {key}: Found")
        else:
            print(f" ✗ {key}: NOT FOUND - {path}")

    # Initialize Database Connection
    print("[Boot] Connecting to Database...")
    db_connected = False
    try:
        db = Database.get()
        print("[Boot] Database connected successfully")

        # Initialize all tables in correct order
        Position.initialize()
        print(" - Positions Table OK")

        Employee.initialize()
        print(" - Employees Table OK")

        Attendance.initialize()
        print(" - Attendance Table OK")

        Reports.initialize()
        print(" - Reports Table OK")

        PeriodicReports.initialize()
        print(" - Periodic Reports Tables OK (15-day & Monthly)")

        LeaveRequest.initialize()
        print(" - Leave Requests Table OK")

        Admin.ensure_default_admin()
        print(" - Admin User OK")

        print("[Boot] Database Ready.")
        db_connected = True

        # START SCHEDULER AFTER DATABASE IS READY
        if SCHEDULER_AVAILABLE:
            try:
                print("[Boot] Starting daily scheduler...")
                start_scheduler()
                print("[Boot] Scheduler started successfully")

                # Schedule status print after 2 seconds
                QTimer.singleShot(2000, print_scheduler_status)
            except Exception as e:
                print(f"[Boot] Scheduler start error (non-critical): {e}")
                import traceback
                traceback.print_exc()
        else:
            print("[Boot] Scheduler not available - skipping")

    except Exception as e:
        print(f"[Boot] Database Error: {e}")
        import traceback
        traceback.print_exc()
        db_connected = False

    print("[Boot] Building UI...")

    # Create Views with error handling
    try:
        login_page = LoginBoard(logo_paths)
        print(" - Login page created")

        sidebar = Sidebar("Frontera's All-Seeing Ledger", logo_paths)

        # === CUSTOM STYLE FOR LOGOUT BUTTON (Color: #250903) ===
        sidebar.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #250903; 
                color: white;
                border: 1px solid #1a0602;
                border-radius: 8px;
                font-weight: 600;
                padding: 10px;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #3b0e05;
            }
        """)
        print(" - Sidebar created and Logout button styled")

        header = Header()
        print(" - Header created")

        dashboard_page = DashboardPage(logo_paths)
        print(" - Dashboard created")

        employees_page = EmployeesPage()
        print(" - Employees page created")

        reports_page = ReportsPage()
        print(" - Reports page created")

        requests_page = RequestsPage()
        print(" - Requests page created")

        settings_page = SettingsPage()
        print(" - Settings page created")

        PeriodicReports.initialize()
        print(" - Periodic Reports Tables OK (15-day & Monthly)")

        pages = [
            login_page,
            dashboard_page,
            employees_page,
            reports_page,
            requests_page,
            settings_page
        ]

        # Create Main Window
        main_window = MainWindow(sidebar, header, pages)
        print(" - Main window created")

        # Set show_login_success to use our dialog function
        main_window.show_login_success = lambda user_type, user_name: show_login_success_dialog(main_window, user_type,
                                                                                                user_name)

        # Create Controller
        controller = MainController(main_window)
        controller.set_db_connected(db_connected)
        print(" - Controller created")

    except Exception as e:
        print(f"[Boot] UI Creation Error: {e}")
        import traceback
        traceback.print_exc()

        # Stop scheduler before exiting
        if SCHEDULER_AVAILABLE:
            try:
                stop_scheduler()
                print("[Boot] Scheduler stopped due to UI error")
            except:
                pass

        return 1

    print("[Boot] Wiring Buttons...")

    try:
        # === LOGIN PAGE (FIXED: Reset Sidebar on Login) ===
        def handle_login_flow():
            username, password = login_page.get_credentials()
            if controller.on_login(username, password, login_page):
                # FORCE SIDEBAR RESET: Click 'Overview' to visually select it
                # This fixes the issue where 'Reports' stays highlighted after re-login
                print("[Main] Login success - Resetting Sidebar to Overview")
                sidebar.btn_overview.click()

        login_page.login_btn.clicked.connect(handle_login_flow)

        # === SIDEBAR ===
        sidebar.btn_overview.clicked.connect(lambda: (
            main_window.show_page(1, "Overview"),
            controller.refresh_dashboard(dashboard_page)
        ))

        sidebar.btn_employees.clicked.connect(lambda: (
            main_window.show_page(2, "Employees"),
            controller.refresh_employees(employees_page)
        ))

        sidebar.btn_reports.clicked.connect(lambda: (
            main_window.show_page(3, "Reports"),
            controller.refresh_reports(reports_page)
        ))

        sidebar.btn_requests.clicked.connect(lambda: (
            main_window.show_page(4, "Requests"),
            controller.refresh_requests(requests_page)
        ))

        sidebar.btn_settings.clicked.connect(lambda: main_window.show_page(5, "Settings"))

        sidebar.btn_logout.clicked.connect(lambda: (
            main_window.show_login() if controller.on_logout() else None
        ))

        # === EMPLOYEES PAGE ===
        employees_page.add_btn.clicked.connect(lambda: controller.on_add_employee(employees_page))
        employees_page.on_edit_employee = lambda emp_data: (
            controller.on_edit_employee(emp_data),
            controller.refresh_employees(employees_page)
        )

        # === SETTINGS PAGE ===
        settings_page.theme_combo.currentTextChanged.connect(
            lambda theme: controller.on_theme_change(theme.lower())
        )
        settings_page.change_credentials_btn.clicked.connect(
            lambda: controller.on_credentials_change(settings_page)
        )

        print(" - Button wiring complete")

    except Exception as e:
        print(f"[Boot] Button Wiring Error: {e}")
        import traceback
        traceback.print_exc()

        # Stop scheduler before exiting
        if SCHEDULER_AVAILABLE:
            try:
                stop_scheduler()
                print("[Boot] Scheduler stopped due to wiring error")
            except:
                pass

        return 1

    # Show login page
    try:
        main_window.show_login()
        main_window.show()
        print("[Boot] UI Shown.")
    except Exception as e:
        print(f"[Boot] Show Error: {e}")
        import traceback
        traceback.print_exc()

        # Stop scheduler before exiting
        if SCHEDULER_AVAILABLE:
            try:
                stop_scheduler()
                print("[Boot] Scheduler stopped due to show error")
            except:
                pass

        return 1

    print("[Boot] Event Loop Starting...")

    # Start event loop
    try:
        exit_code = app.exec()

        # STOP SCHEDULER ON EXIT
        if SCHEDULER_AVAILABLE:
            try:
                print("[Shutdown] Stopping scheduler...")
                stop_scheduler()
                print("[Shutdown] Scheduler stopped successfully")
            except Exception as e:
                print(f"[Shutdown] Error stopping scheduler: {e}")
                import traceback
                traceback.print_exc()

        print("[Shutdown] Application closed")
        return exit_code

    except Exception as e:
        print(f"[Boot] Event Loop Error: {e}")
        import traceback
        traceback.print_exc()

        # Stop scheduler before exiting
        if SCHEDULER_AVAILABLE:
            try:
                stop_scheduler()
                print("[Boot] Scheduler stopped due to event loop error")
            except:
                pass

        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[Boot] Fatal Error: {e}")
        import traceback

        traceback.print_exc()

        # Final attempt to stop scheduler
        if SCHEDULER_AVAILABLE:
            try:
                stop_scheduler()
                print("[Boot] Scheduler stopped due to fatal error")
            except:
                pass

        sys.exit(1)