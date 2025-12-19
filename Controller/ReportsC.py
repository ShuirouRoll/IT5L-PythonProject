from datetime import date
from Project.Model.Database import Database
from Project.Model.Reports import Reports
from Project.Controller.PeriodicReportsC import PeriodicReportsController

class ReportController:

    @staticmethod
    def initialize_tables():
        Reports.initialize()

    @staticmethod
    def get_report_history(limit=30):
        """Get daily report history"""
        db = Database.get()
        try:
            results = db.query_all(
                "SELECT date, total_present_employees, total_absent_employees, total_late_employees FROM reports ORDER BY date DESC LIMIT %s",
                (limit,)
            )
            return results if results else []
        except Exception as e:
            print(f"[ReportsC] Error getting history: {e}")
            return []

    @staticmethod
    def get_15day_reports(limit=10):
        return PeriodicReportsController.get_15day_reports(limit)

    @staticmethod
    def get_monthly_reports(limit=12):
        return PeriodicReportsController.get_monthly_reports(limit)

    @staticmethod
    def get_attendance_details_by_date(report_date):
        """
        Get detailed attendance for a date, INCLUDING POSITION.
        """
        db = Database.get()

        try:
            # JOIN FIX: Changed 'DATE(a.clock_in) = %s' to 'a.date = %s'
            # This ensures we catch 'Absent' records where clock_in is NULL.
            query = """
                SELECT e.id as employee_id,
                       CONCAT(e.first_name, ' ', IFNULL(e.middle_initial, ''), ' ', e.last_name) as full_name,
                       e.email_address,
                       e.phone_number,
                       COALESCE(p.name, 'Staff') as position,
                       COALESCE(a.status, 'Absent') as status,
                       a.clock_in,
                       a.clock_out
                FROM employees e
                LEFT JOIN positions p ON e.position_id = p.id
                LEFT JOIN attendance a ON e.id = a.employee_id AND a.date = %s
                ORDER BY
                    CASE
                        WHEN a.status = 'Present' THEN 1
                        WHEN a.status = 'Late' THEN 2
                        WHEN a.status = 'Absent' OR a.status IS NULL THEN 3
                    END,
                    e.first_name
            """

            results = db.query_all(query, (report_date,))

            present = []
            late = []
            absent = []

            for row in results:
                employee_data = {
                    'employee_id': row['employee_id'],
                    'full_name': row['full_name'],
                    'position': row['position'],
                    'email': row['email_address'] or 'N/A',
                    'phone': row['phone_number'] or 'N/A',
                    'status': row['status'],
                    'clock_in': row['clock_in'].strftime('%I:%M %p') if row['clock_in'] else '',
                    'clock_out': row['clock_out'].strftime('%I:%M %p') if row['clock_out'] else ''
                }

                if row['status'] == 'Present':
                    present.append(employee_data)
                elif row['status'] == 'Late':
                    late.append(employee_data)
                else:
                    absent.append(employee_data)

            return {
                'date': report_date,
                'present': present,
                'late': late,
                'absent': absent
            }

        except Exception as e:
            print(f"[ReportsC] Error getting details: {e}")
            return None