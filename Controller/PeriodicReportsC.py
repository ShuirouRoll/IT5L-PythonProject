from datetime import date, timedelta
from Project.Model.Database import Database
from Project.Model.PeriodicReports import PeriodicReports


class PeriodicReportsController:
    """Controller for generating and managing 15-day and monthly attendance reports"""

    @staticmethod
    def initialize_tables():
        """Initialize periodic reports tables"""
        PeriodicReports.initialize()

    # ... [Keep existing generate methods: generate_15day_report, generate_monthly_report, etc.] ...
    # ... [Paste the previous generation logic here if you are replacing the whole file,
    #      OR just add the NEW methods below to your existing file] ...

    # === NEW METHODS FOR POPUP DETAILS ===

    @staticmethod
    def get_details_for_15day(period_start, period_end):
        """Get detailed employee stats for a specific 15-day period"""
        db = Database.get()
        try:
            query = """
                SELECT 
                    ep.*,
                    CONCAT(e.first_name, ' ', IFNULL(e.middle_initial, ''), ' ', e.last_name) as full_name,
                    p.name as position
                FROM employee_15day_performance ep
                JOIN employees e ON ep.employee_id = e.id
                LEFT JOIN positions p ON e.position_id = p.id
                WHERE ep.period_start = %s AND ep.period_end = %s
                ORDER BY ep.attendance_rate DESC, ep.total_hours_worked DESC
            """
            return db.query_all(query, (period_start, period_end))
        except Exception as e:
            print(f"[PeriodicC] Error getting 15-day details: {e}")
            return []

    @staticmethod
    def get_details_for_month(year, month):
        """Get detailed employee stats for a specific month"""
        db = Database.get()
        try:
            query = """
                SELECT 
                    ep.*,
                    CONCAT(e.first_name, ' ', IFNULL(e.middle_initial, ''), ' ', e.last_name) as full_name,
                    p.name as position
                FROM employee_monthly_performance ep
                JOIN employees e ON ep.employee_id = e.id
                LEFT JOIN positions p ON e.position_id = p.id
                WHERE ep.year = %s AND ep.month = %s
                ORDER BY ep.attendance_rate DESC, ep.total_hours_worked DESC
            """
            return db.query_all(query, (year, month))
        except Exception as e:
            print(f"[PeriodicC] Error getting monthly details: {e}")
            return []

    # ... [Keep existing getter methods: get_15day_reports, get_monthly_reports, etc.] ...

    @staticmethod
    def generate_15day_report(start_date=None, end_date=None):
        # [Use previous code for this method]
        pass # Placeholder to indicate existing code remains

    @staticmethod
    def generate_monthly_report(year=None, month=None):
        # [Use previous code for this method]
        pass # Placeholder to indicate existing code remains

    @staticmethod
    def get_15day_reports(limit=10):
        db = Database.get()
        try:
            return db.query_all("SELECT * FROM reports_15day ORDER BY period_end DESC LIMIT %s", (limit,))
        except: return []

    @staticmethod
    def get_monthly_reports(limit=12):
        db = Database.get()
        try:
            return db.query_all("SELECT * FROM reports_monthly ORDER BY year DESC, month DESC LIMIT %s", (limit,))
        except: return []

    # Internal helpers (_generate_employee_...) also remain