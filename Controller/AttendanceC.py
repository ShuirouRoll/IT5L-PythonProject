from datetime import datetime, date, time, timedelta
from Project.Model.Database import Database
from Project.Model.Attendance import Attendance


class AttendanceController:
    """Controller for attendance operations - handles all business logic and queries"""

    ABSENT_CUTOFF = time(17, 0, 0)  # 5 PM - after this, clock-in is considered absent
    MIN_WORK_HOURS = 8  # Minimum work hours before clock-out

    @staticmethod
    def initialize_tables():
        """Initialize attendance table"""
        Attendance.initialize()

    @staticmethod
    def get_recent_attendance(limit=50):
        db = Database.get()
        query = """
                SELECT a.id,
                       a.employee_id,
                       CONCAT(e.first_name, ' ', IFNULL(e.middle_initial, ''), ' ', e.last_name) as employee_name,
                       e.email_address,
                       e.phone_number,
                       p.name                                                                    as position_name,
                       p.late_time,
                       p.grace_period_minutes,
                       a.clock_in,
                       a.clock_out,
                       a.status,
                       a.date
                FROM attendance a
                         JOIN employees e ON a.employee_id = e.id
                         LEFT JOIN positions p ON e.position_id = p.id
                WHERE a.date = %s
                ORDER BY a.clock_in DESC
                    LIMIT %s \
                """
        return db.query_all(query, (date.today(), limit))

    @staticmethod
    def get_today_stats():
        db = Database.get()
        today = date.today()
        now = datetime.now()

        # Get total employees
        total_res = db.query_one("SELECT COUNT(*) as c FROM employees")
        total = total_res['c'] if total_res else 0

        # If past cutoff time, mark all employees who haven't clocked in as absent
        if now.time() > AttendanceController.ABSENT_CUTOFF:
            AttendanceController.mark_absent_employees()

        # Count by status for today
        stats_query = """
                      SELECT SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
                             SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END)    as late,
                             SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END)  as marked_absent
                      FROM attendance
                      WHERE date = %s \
                      """
        stats = db.query_one(stats_query, (today,))

        present = int(stats['present'] or 0)
        late = int(stats['late'] or 0)
        marked_absent = int(stats['marked_absent'] or 0)

        # Calculate total signed in (present + late)
        signed_in = present + late

        # Calculate absent (total employees - signed in)
        actual_absent = total - signed_in
        if actual_absent < 0:
            actual_absent = 0

        return {
            "total": total,
            "present": signed_in,
            "late": late,
            "absent": actual_absent
        }

    # === UPDATED METHOD: Mark Absent for Specific Date ===
    @staticmethod
    def mark_absent_employees(target_date=None):
        """
        Mark employees as absent if they have no record for the target date.
        Args:
            target_date: Date to check (default: today)
        """
        db = Database.get()
        if target_date is None:
            target_date = date.today()

        try:
            # Get all employees who have NO attendance record for the target date
            query = """
                    SELECT e.id
                    FROM employees e
                    WHERE NOT EXISTS (SELECT 1
                                      FROM attendance a
                                      WHERE a.employee_id = e.id
                                        AND a.date = %s) \
                    """
            absent_employees = db.query_all(query, (target_date,))

            # Mark each as absent
            for emp in absent_employees:
                db.execute(
                    """INSERT INTO attendance (employee_id, date, status, clock_in, clock_out)
                       VALUES (%s, %s, 'Absent', NULL, NULL)""",
                    (emp['id'], target_date)
                )

            if absent_employees:
                print(f"[Attendance] Marked {len(absent_employees)} employees as absent for {target_date}")

        except Exception as e:
            print(f"[Attendance] Error marking absent employees: {e}")

    @classmethod
    def clock_in(cls, emp_id):
        """
        Process employee clock-in with position-based late calculation

        Args:
            emp_id: Employee ID

        Returns:
            Dictionary with success status and message
        """
        db = Database.get()
        today = date.today()
        now = datetime.now()

        try:
            # 1. Check if already clocked in today
            existing = db.query_one(
                "SELECT id FROM attendance WHERE employee_id=%s AND date=%s",
                (emp_id, today)
            )
            if existing:
                return {"success": False, "message": "Already clocked in today."}

            # 2. Check if past cutoff time
            if now.time() > cls.ABSENT_CUTOFF:
                # Still allow clock-in but mark as absent for being too late
                status = "Absent"
                db.execute(
                    "INSERT INTO attendance (employee_id, clock_in, date, status) VALUES (%s, %s, %s, %s)",
                    (emp_id, now, today, status)
                )
                return {
                    "success": True,
                    "message": f"Clocked in after cutoff time ({cls.ABSENT_CUTOFF.strftime('%I:%M %p')}). Marked as Absent.",
                    "status": status
                }

            # 3. Fetch employee's position settings for late calculation
            settings = db.query_one("""
                                    SELECT p.late_time, p.grace_period_minutes
                                    FROM employees e
                                             LEFT JOIN positions p ON e.position_id = p.id
                                    WHERE e.id = %s
                                    """, (emp_id,))

            # Default values if no position found or settings are None
            if settings and settings.get('late_time'):
                target_time = settings['late_time']
                # Handle if late_time is returned as timedelta or string
                if isinstance(target_time, timedelta):
                    total_seconds = int(target_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    target_time = time(hours, minutes, seconds)
                elif isinstance(target_time, str):
                    parts = target_time.split(':')
                    target_time = time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
                grace = settings.get('grace_period_minutes', 15)
            else:
                target_time = time(8, 0, 0)
                grace = 15

            # 4. Calculate late threshold (target time + grace period)
            target_datetime = datetime.combine(today, target_time)
            threshold_datetime = target_datetime + timedelta(minutes=grace)
            threshold_time = threshold_datetime.time()

            # 5. Determine status based on current time
            current_time = now.time()

            if current_time > threshold_time:
                status = "Late"
            else:
                status = "Present"

            # 6. Insert attendance record
            db.execute(
                "INSERT INTO attendance (employee_id, clock_in, date, status) VALUES (%s, %s, %s, %s)",
                (emp_id, now, today, status)
            )

            return {
                "success": True,
                "message": f"Clocked in as {status}",
                "status": status
            }

        except Exception as e:
            print(f"[AttendanceC] Clock-in error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Clock-in failed: {str(e)}"}

    @classmethod
    def clock_out(cls, employee_id):
        """
        Process employee clock-out with 8-hour minimum work requirement

        Args:
            employee_id: Employee ID

        Returns:
            Dictionary with success status and message
        """
        db = Database.get()
        today = date.today()
        now = datetime.now()

        try:
            # Find today's clock-in record
            record = db.query_one(
                "SELECT id, clock_in, clock_out, status FROM attendance WHERE employee_id = %s AND date = %s",
                (employee_id, today)
            )

            if not record:
                return {"success": False, "message": "No clock-in record found today"}

            if record['clock_out']:
                return {"success": False, "message": "Already clocked out"}

            # Check if employee was marked absent
            if record['status'] == 'Absent' and not record['clock_in']:
                return {"success": False, "message": "Cannot clock out - marked as absent (no clock-in)"}

            # Calculate work duration (8 hours minimum)
            if record['clock_in']:
                duration_hours = (now - record['clock_in']).total_seconds() / 3600

                if duration_hours < cls.MIN_WORK_HOURS:
                    hours_remaining = cls.MIN_WORK_HOURS - duration_hours
                    hours = int(hours_remaining)
                    minutes = int((hours_remaining - hours) * 60)
                    return {
                        "success": False,
                        "message": f"Must work at least {cls.MIN_WORK_HOURS} hours. Time remaining: {hours}h {minutes}m"
                    }

            # Update attendance record with clock-out time
            db.execute(
                "UPDATE attendance SET clock_out = %s WHERE id = %s",
                (now, record['id'])
            )

            return {
                "success": True,
                "message": "Clocked out successfully",
                "time": now.strftime("%I:%M %p")
            }

        except Exception as e:
            print(f"[AttendanceC] Clock-out error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Clock-out failed: {str(e)}"}

    @staticmethod
    def get_attendance_by_date(attendance_date):
        """
        Get all attendance records for a specific date WITH FULL EMPLOYEE INFO

        Args:
            attendance_date: Date to query

        Returns:
            List of attendance records with complete employee details
        """
        db = Database.get()
        query = """
                SELECT a.id,
                       a.employee_id,
                       CONCAT(e.first_name, ' ', IFNULL(e.middle_initial, ''), ' ', e.last_name) as employee_name,
                       e.email_address,
                       e.phone_number,
                       p.name as position_name,
                       a.clock_in,
                       a.clock_out,
                       a.status,
                       a.date,
                       TIMESTAMPDIFF(HOUR, a.clock_in, a.clock_out) as hours_worked
                FROM attendance a
                         JOIN employees e ON a.employee_id = e.id
                         LEFT JOIN positions p ON e.position_id = p.id
                WHERE a.date = %s
                ORDER BY a.clock_in ASC
                """
        return db.query_all(query, (attendance_date,))

    @staticmethod
    def get_employee_attendance_history(employee_id, limit=30):
        """
        Get attendance history for a specific employee

        Args:
            employee_id: Employee ID
            limit: Maximum number of records

        Returns:
            List of attendance records for the employee
        """
        db = Database.get()
        query = """
                SELECT a.date,
                       a.clock_in,
                       a.clock_out,
                       a.status,
                       TIMESTAMPDIFF(HOUR, a.clock_in, a.clock_out) as hours_worked
                FROM attendance a
                WHERE a.employee_id = %s
                ORDER BY a.date DESC
                    LIMIT %s
                """
        return db.query_all(query, (employee_id, limit))

    @staticmethod
    def generate_daily_report(target_date=None):
        """
        Generate end-of-day report and store in reports table.
        Args:
            target_date: Date to generate report for. Defaults to TODAY.
        """
        db = Database.get()

        # Use target_date if provided, otherwise use today
        report_date = target_date if target_date else date.today()

        try:
            # 1. Fill in blanks for that specific date
            AttendanceController.mark_absent_employees(report_date)

            # 2. Count statuses for that specific date
            stats = db.query_one("""
                                 SELECT SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_count,
                                        SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END)    as late_count,
                                        SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END)  as absent_count
                                 FROM attendance
                                 WHERE date = %s
                                 """, (report_date,))

            present = int(stats['present_count'] or 0)
            late = int(stats['late_count'] or 0)
            absent = int(stats['absent_count'] or 0)

            # 3. Update the historical record
            db.execute("""
                       INSERT INTO reports (date, total_present_employees, total_late_employees, total_absent_employees)
                       VALUES (%s, %s, %s, %s) ON DUPLICATE KEY
                       UPDATE
                           total_present_employees = %s,
                           total_late_employees = %s,
                           total_absent_employees = %s
                       """, (report_date, present, late, absent, present, late, absent))

            print(f"[Attendance] Report generated for {report_date}: Present={present}, Late={late}, Absent={absent}")
            return True

        except Exception as e:
            print(f"[Attendance] Error generating report: {e}")
            return False

    @staticmethod
    def get_cutoff_time():
        """Get the current absence cutoff time"""
        return AttendanceController.ABSENT_CUTOFF

    @staticmethod
    def set_cutoff_time(hour, minute):
        """
        Set the absence cutoff time

        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
        """
        AttendanceController.ABSENT_CUTOFF = time(hour, minute, 0)
        print(f"[Attendance] Cutoff time set to {hour:02d}:{minute:02d}")

    @staticmethod
    def set_min_work_hours(hours):
        """
        Set minimum work hours requirement

        Args:
            hours: Minimum hours required before clock-out
        """
        AttendanceController.MIN_WORK_HOURS = hours
        print(f"[Attendance] Minimum work hours set to {hours}")