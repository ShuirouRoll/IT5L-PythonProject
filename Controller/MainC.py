from PyQt6.QtCore import Qt
from Project.View.Dialogs import AddEmployeeDialog, ChangeCredentialsDialog, CompactMessageDialog, EditEmployeeDialog
# Import Controllers
from Project.Controller.EmployeeC import EmployeeController
from Project.Controller.ReportsC import ReportController
from Project.Controller.AttendanceC import AttendanceController
from Project.Controller.RequestC import LeaveRequestController
# Import Models
from Project.Model.Admin import Admin
from Project.Model.Employee import Employee


class MainController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_admin_id = None
        self.db_connected = False

    def set_db_connected(self, connected):
        self.db_connected = connected

    def on_login(self, username, password, login_page):
        if not username or not password:
            CompactMessageDialog.show_warning(self.main_window, "Error", "Please enter username and password.")
            return False

        if self.db_connected:
            try:
                # --- 1. TRY ADMIN LOGIN ---
                admin = Admin.authenticate(username, password)
                if admin:
                    self.current_admin_id = admin.get("id")
                    # Update Theme
                    theme = admin.get("theme", "light")
                    self.main_window.current_theme = theme

                    login_page.clear_fields()

                    # Show Success Dialog (defined in Main.py)
                    try:
                        self.main_window.show_login_success("admin", admin.get("full_name"))
                    except Exception as e:
                        print(f"[MainC] Dialog error (non-critical): {e}")

                    # Show main window
                    self.main_window.show_main()

                    # Apply theme after showing main
                    self.main_window.apply_theme(theme)

                    # Switch to Dashboard
                    self.main_window.show_page(1, "Overview")

                    # Load Data Immediately
                    try:
                        dashboard_page = self.main_window.stack.widget(1)
                        self.refresh_dashboard(dashboard_page)
                    except Exception as e:
                        print(f"[MainC] Dashboard refresh error: {e}")
                        import traceback
                        traceback.print_exc()

                    return True

                # --- 2. TRY EMPLOYEE LOGIN ---
                employee = Employee.authenticate(username, password)
                if employee:
                    login_page.clear_fields()

                    try:
                        self.main_window.show_login_success("employee", employee.get("full_name"))
                    except Exception as e:
                        print(f"[MainC] Dialog error (non-critical): {e}")

                    self.open_employee_dashboard(employee)
                    return True

                CompactMessageDialog.show_warning(self.main_window, "Error", "Invalid username or password.")
                return False

            except Exception as e:
                print(f"[MainController] Login error: {e}")
                import traceback
                traceback.print_exc()
                CompactMessageDialog.show_warning(self.main_window, "Error", f"Login error: {str(e)}")
                return False
        else:
            # Offline Mode
            if username == "admin" and password == "admin123":
                login_page.clear_fields()

                try:
                    self.main_window.show_login_success("admin", "System Administrator (Offline)")
                except Exception as e:
                    print(f"[MainC] Dialog error (non-critical): {e}")

                self.main_window.show_main()
                self.main_window.show_page(1, "Overview")
                return True
            else:
                CompactMessageDialog.show_warning(self.main_window, "Error",
                                                  "Invalid credentials. Use admin / admin123")
                return False

    def on_logout(self):
        try:
            if CompactMessageDialog.show_logout_confirm(self.main_window):
                self.current_admin_id = None
                return True
            return False
        except Exception as e:
            print(f"[MainC] Logout error: {e}")
            return False

    # --- REFRESH METHODS ---

    def refresh_dashboard(self, dashboard_page):
        """Refresh dashboard with latest attendance data"""
        if not self.db_connected:
            print("[MainC] Skipping dashboard refresh - DB not connected")
            return

        try:
            # Get today's attendance stats
            stats = AttendanceController.get_today_stats()

            # Extract stats
            total = stats.get('total', 0)
            clocked_in = stats.get('present', 0)
            not_clocked_in = stats.get('absent', 0)

            print(f"[Dashboard] Stats received: {stats}")
            print(f"[Dashboard] Parsed - Total: {total}, In: {clocked_in}, Out: {not_clocked_in}")

            # Update stat cards and pie chart
            dashboard_page.update_stats(total, clocked_in, not_clocked_in)

            # Get attendance records for table with full details
            records = AttendanceController.get_recent_attendance(50)

            # Format records for the table
            formatted_records = []
            for record in records:
                formatted_records.append({
                    'employee_id': record.get('employee_id'),
                    'employee_name': record.get('employee_name'),
                    'position': record.get('position_name', 'Staff'),
                    'email': record.get('email_address', 'N/A'),
                    'phone': record.get('phone_number', 'N/A'),
                    'status': record.get('status'),
                    'clock_in': record.get('clock_in').strftime('%I:%M %p') if record.get('clock_in') else '-',
                    'clock_out': record.get('clock_out').strftime('%I:%M %p') if record.get('clock_out') else '-'
                })

            dashboard_page.populate_attendance_table(formatted_records)

            print(f"[Dashboard] Refreshed successfully with {len(formatted_records)} records")

        except Exception as e:
            print(f"[Dashboard] Refresh error: {e}")
            import traceback
            traceback.print_exc()

            # Show at least something if there's an error
            dashboard_page.update_stats(0, 0, 0)
            dashboard_page.populate_attendance_table([])

    def refresh_employees(self, employees_page):
        if not self.db_connected: return
        try:
            emp_list = EmployeeController.list_employees()
            employees_page.populate_table(emp_list)
        except Exception as e:
            print(f"[MainController] Error refreshing employees: {e}")

    def refresh_reports(self, reports_page):
        if not self.db_connected: return
        try:
            # 1. Load Daily
            daily = ReportController.get_report_history()
            reports_page.populate_table(daily)

            # 2. Load 15-Day
            periodic_15 = ReportController.get_15day_reports()
            reports_page.populate_15day(periodic_15)

            # 3. Load Monthly
            monthly = ReportController.get_monthly_reports()
            reports_page.populate_monthly(monthly)

            # Wire click event (UPDATED to handle type)
            reports_page.on_report_clicked = self.on_report_row_click

        except Exception as e:
            print(f"[MainController] Error refreshing reports: {e}")

    def on_report_row_click(self, r_type, data):
        """Handle clicks from any report table"""
        try:
            if r_type == 'daily':
                # Data is a Date object
                self.show_report_details(data)

            elif r_type == '15day':
                # Data is dict {start, end}
                from Project.Controller.PeriodicReportsC import PeriodicReportsController
                details = PeriodicReportsController.get_details_for_15day(data['start'], data['end'])
                title = f"15-Day Report ({data['start']} to {data['end']})"
                self.show_periodic_details(title, details)

            elif r_type == 'monthly':
                # Data is dict {year, month}
                from Project.Controller.PeriodicReportsC import PeriodicReportsController
                details = PeriodicReportsController.get_details_for_month(data['year'], data['month'])
                import calendar
                m_name = calendar.month_name[data['month']]
                title = f"Monthly Report - {m_name} {data['year']}"
                self.show_periodic_details(title, details)

        except Exception as e:
            print(f"[MainC] Click error: {e}")
            CompactMessageDialog.show_warning(self.main_window, "Error", str(e))

    def show_periodic_details(self, title, data):
        """Show the new periodic details dialog"""
        if not data:
            CompactMessageDialog.show_warning(self.main_window, "Info", "No detailed records found for this period.")
            return

        from Project.View.ReportsDetails import PeriodicReportDetails
        dialog = PeriodicReportDetails(title, data, self.main_window)
        dialog.exec()

    def refresh_requests(self, requests_page):
        if not self.db_connected: return
        try:
            requests_page.load_data()
        except Exception as e:
            print(f"[MainController] Error refreshing requests: {e}")

    # --- ACTIONS ---

    def on_add_employee(self, employees_page):
        if not self.db_connected: return False
        try:
            dialog = AddEmployeeDialog(self.main_window)
            if dialog.exec() and dialog.employee_data:
                try:
                    EmployeeController.add_employee(dialog.employee_data)
                    CompactMessageDialog.show_success(self.main_window, "Success", "Employee added!")
                    self.refresh_employees(employees_page)
                    return True
                except Exception as e:
                    CompactMessageDialog.show_warning(self.main_window, "Error", str(e))
        except Exception as e:
            print(f"[MainC] Add employee dialog error: {e}")
            import traceback
            traceback.print_exc()
        return False

    def on_edit_employee(self, employee_data):
        if not self.db_connected: return False
        try:
            dialog = EditEmployeeDialog(employee_data, self.main_window)
            if dialog.exec() and dialog.updated_data:
                try:
                    EmployeeController.update_employee(dialog.updated_data["employee_id"], dialog.updated_data)
                    CompactMessageDialog.show_success(self.main_window, "Success", "Updated successfully!")
                    return True
                except Exception as e:
                    CompactMessageDialog.show_warning(self.main_window, "Error", str(e))
        except Exception as e:
            print(f"[MainC] Edit employee error: {e}")
            import traceback
            traceback.print_exc()
        return False

    def on_delete_employee(self, employee_id):
        if not self.db_connected: return False
        try:
            EmployeeController.delete_employee(employee_id)
            CompactMessageDialog.show_success(self.main_window, "Success", "Employee deleted.")
            return True
        except Exception as e:
            CompactMessageDialog.show_warning(self.main_window, "Error", str(e))
            return False

    def on_credentials_change(self, settings_page):
        try:
            dialog = ChangeCredentialsDialog(self.main_window)
            if dialog.exec() and dialog.credentials_data:
                if not self.db_connected: return False
                try:
                    if not Admin.verify_password(self.current_admin_id, dialog.credentials_data["current"]):
                        CompactMessageDialog.show_warning(self.main_window, "Error", "Current password incorrect.")
                        return False
                    Admin.update_credentials(
                        self.current_admin_id,
                        dialog.credentials_data["username"],
                        dialog.credentials_data["password"]
                    )
                    CompactMessageDialog.show_success(self.main_window, "Success",
                                                      "Credentials updated. Please login again.")
                    self.current_admin_id = None  # Force logout
                    return True
                except Exception as e:
                    CompactMessageDialog.show_warning(self.main_window, "Error", str(e))
        except Exception as e:
            print(f"[MainC] Credentials change error: {e}")
            import traceback
            traceback.print_exc()
        return False

    def on_theme_change(self, theme):
        if self.db_connected and self.current_admin_id:
            try:
                Admin.update_theme(self.current_admin_id, theme)
            except Exception as e:
                print(f"[MainC] Theme update error: {e}")
        self.main_window.apply_theme(theme)

    def on_cutoff_change(self, settings_page):
        """Handle absence cutoff time change"""
        try:
            hour, minute = settings_page.get_cutoff_time()
            AttendanceController.set_cutoff_time(hour, minute)
            CompactMessageDialog.show_success(
                self.main_window,
                "Success",
                f"Absence cutoff time set to {hour:02d}:{minute:02d}"
            )
        except Exception as e:
            print(f"[MainC] Cutoff time error: {e}")
            CompactMessageDialog.show_warning(self.main_window, "Error", str(e))

    # --- SUB-WINDOWS ---

    def open_employee_dashboard(self, employee_data):
        try:
            from Project.View.EmployeeDashboard import EmployeeDashboard
            self.employee_window = EmployeeDashboard(employee_data)
            self.employee_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.employee_window.destroyed.connect(lambda: self.main_window.show() or self.main_window.show_login())
            self.employee_window.show()
            self.main_window.hide()
        except Exception as e:
            print(f"[MainC] Error opening employee dashboard: {e}")
            import traceback
            traceback.print_exc()
            CompactMessageDialog.show_warning(self.main_window, "Error", str(e))

    def show_report_details(self, report_date):
        if not report_date: return
        from Project.View.ReportsDetails import ReportDetails

        try:
            # Get detailed data
            details = ReportController.get_attendance_details_by_date(report_date)
            if details:
                # Format date for display
                date_str = report_date.strftime("%Y-%m-%d") if hasattr(report_date, 'strftime') else str(report_date)

                # Show dialog
                dialog = ReportDetails(date_str, details, self.main_window)
                dialog.exec()
            else:
                CompactMessageDialog.show_warning(self.main_window, "Error", "No data found for this date.")
        except Exception as e:
            print(f"[MainC] Error showing report details: {e}")
            import traceback
            traceback.print_exc()
            CompactMessageDialog.show_warning(self.main_window, "Error", f"Failed to load report: {str(e)}")

    def on_scheduler_task(self, task_name):
            """Handle manual scheduler task execution"""
            try:
                from Project.Controller.DailyScheduler import run_task_now

                print(f"[MainC] Running scheduler task: {task_name}")
                run_task_now(task_name)

                task_display = "Absent Marking" if task_name == "absent" else "Report Generation"
                CompactMessageDialog.show_success(
                    self.main_window,
                    "Task Completed",
                    f"{task_display} task executed successfully!"
                )

                # Refresh dashboard if it's the current page
                current_index = self.main_window.stack.currentIndex()
                if current_index == 1:  # Dashboard
                    self.refresh_dashboard(self.main_window.stack.widget(1))
                elif current_index == 3:  # Reports
                    self.refresh_reports(self.main_window.stack.widget(3))

            except Exception as e:
                print(f"[MainC] Scheduler task error: {e}")
                import traceback
                traceback.print_exc()
                CompactMessageDialog.show_warning(
                    self.main_window,
                    "Error",
                    f"Failed to run task: {str(e)}"
                )

    def refresh_settings(self, settings_page):
        """Refresh settings page with scheduler status"""
        try:
            from Project.Controller.DailyScheduler import get_status
            status = get_status()
            settings_page.update_scheduler_status(status)
        except Exception as e:
            print(f"[MainC] Error refreshing settings: {e}")