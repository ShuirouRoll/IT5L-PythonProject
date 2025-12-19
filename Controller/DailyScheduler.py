import time
import threading
from datetime import datetime, date, timedelta
from Project.Controller.AttendanceC import AttendanceController
from Project.Controller.PeriodicReportsC import PeriodicReportsController


class DailyScheduler:
    """
    Automated scheduler for daily attendance operations (Standard Library Version)
    No external 'schedule' library required.
    """

    _scheduler_thread = None
    _running = False

    # Configuration
    _absent_time = "17:00"
    _report_time = "23:59"

    # State tracking
    _last_absent_date = None
    _last_report_date = None
    _last_15day_date = None
    _last_monthly_date = None

    @classmethod
    def start(cls):
        """Start the scheduler in a background thread"""
        if cls._running:
            print("[Scheduler] Already running")
            return

        cls._running = True
        cls._scheduler_thread = threading.Thread(target=cls._run_scheduler, daemon=True)
        cls._scheduler_thread.start()

        print(f"[Scheduler] Started successfully (Native Mode)")
        print(f"  - Absent marking at: {cls._absent_time}")
        print(f"  - Daily report at: {cls._report_time}")

    @classmethod
    def stop(cls):
        """Stop the scheduler"""
        cls._running = False
        if cls._scheduler_thread:
            cls._scheduler_thread.join(timeout=2)
        print("[Scheduler] Stopped")

    @classmethod
    def _run_scheduler(cls):
        """Internal loop to check time every 30 seconds"""
        print("[Scheduler] Background thread started")

        while cls._running:
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                today_str = now.strftime("%Y-%m-%d")

                # --- 1. DAILY ABSENT MARKING (e.g. 17:00) ---
                if current_time == cls._absent_time:
                    if cls._last_absent_date != today_str:
                        cls._mark_absent_job()
                        cls._last_absent_date = today_str

                # --- 2. DAILY REPORT GENERATION (e.g. 23:59) ---
                if current_time == cls._report_time:
                    if cls._last_report_date != today_str:
                        cls._generate_report_job()
                        cls._last_report_date = today_str

                # --- 3. 15-DAY REPORTS (00:30 on 1st and 16th) ---
                if current_time == "00:30":
                    if cls._last_15day_date != today_str:
                        if now.day in [1, 16]:
                            cls._check_15day_report()
                        cls._last_15day_date = today_str

                # --- 4. MONTHLY REPORTS (01:00 on 1st) ---
                if current_time == "01:00":
                    if cls._last_monthly_date != today_str:
                        if now.day == 1:
                            cls._check_monthly_report()
                        cls._last_monthly_date = today_str

                # Sleep to avoid high CPU usage
                time.sleep(30)

            except Exception as e:
                print(f"[Scheduler] Error in scheduler loop: {e}")
                time.sleep(60)

    @classmethod
    def _mark_absent_job(cls):
        try:
            print(f"\n[Scheduler] === ABSENT MARKING JOB STARTED === {datetime.now()}")
            AttendanceController.mark_absent_employees()
            print(f"[Scheduler] === ABSENT MARKING JOB COMPLETED ===\n")
        except Exception as e:
            print(f"[Scheduler] Absent Job Error: {e}")

    @classmethod
    def _generate_report_job(cls):
        try:
            print(f"\n[Scheduler] === DAILY REPORT GENERATION STARTED === {datetime.now()}")
            if AttendanceController.generate_daily_report():
                print(f"[Scheduler] Daily report saved to database")
            print(f"[Scheduler] === DAILY REPORT GENERATION COMPLETED ===\n")
        except Exception as e:
            print(f"[Scheduler] Report Job Error: {e}")

    @classmethod
    def _check_15day_report(cls):
        try:
            print(f"\n[Scheduler] === 15-DAY REPORT CHECK STARTED === {datetime.now()}")
            today = date.today()

            if today.day == 1:
                # Previous month 16th to end
                prev_month = today.replace(day=1) - timedelta(days=1)
                end_date = prev_month
                start_date = prev_month.replace(day=16)
            else:  # Day 16
                # Current month 1st to 15th
                end_date = today.replace(day=15)
                start_date = today.replace(day=1)

            if PeriodicReportsController.generate_15day_report(start_date, end_date):
                print(f"[Scheduler] 15-day report generated successfully")
            print(f"[Scheduler] === 15-DAY REPORT CHECK COMPLETED ===\n")
        except Exception as e:
            print(f"[Scheduler] 15-Day Job Error: {e}")

    @classmethod
    def _check_monthly_report(cls):
        try:
            print(f"\n[Scheduler] === MONTHLY REPORT CHECK STARTED === {datetime.now()}")
            today = date.today()
            # Generate for previous month
            prev_month = today.replace(day=1) - timedelta(days=1)

            if PeriodicReportsController.generate_monthly_report(prev_month.year, prev_month.month):
                print(f"[Scheduler] Monthly report generated successfully")
            print(f"[Scheduler] === MONTHLY REPORT CHECK COMPLETED ===\n")
        except Exception as e:
            print(f"[Scheduler] Monthly Job Error: {e}")

    @classmethod
    def get_status(cls):
        # FIXED: Keys now match what Main.py expects
        return {
            'running': cls._running,
            'absent_time': cls._absent_time,
            'report_time': cls._report_time,
            'absent_last_run': cls._last_absent_date or 'Never',
            'report_last_run': cls._last_report_date or 'Never',
            '15day_last_run': cls._last_15day_date or 'Never',
            'monthly_last_run': cls._last_monthly_date or 'Never'
        }

    @classmethod
    def set_absent_time(cls, time_str):
        cls._absent_time = time_str
        print(f"[Scheduler] Absent marking time updated to {time_str}")

    @classmethod
    def set_report_time(cls, time_str):
        cls._report_time = time_str
        print(f"[Scheduler] Report generation time updated to {time_str}")

    # Manual Triggers
    @classmethod
    def run_absent_marking_now(cls):
        threading.Thread(target=cls._mark_absent_job, daemon=True).start()

    @classmethod
    def run_report_generation_now(cls):
        threading.Thread(target=cls._generate_report_job, daemon=True).start()

    @classmethod
    def run_15day_report_now(cls):
        threading.Thread(target=cls._check_15day_report, daemon=True).start()

    @classmethod
    def run_monthly_report_now(cls):
        threading.Thread(target=cls._check_monthly_report, daemon=True).start()


# Public API functions (Bridge to class methods)
def start_scheduler(): DailyScheduler.start()


def stop_scheduler(): DailyScheduler.stop()


def get_status(): return DailyScheduler.get_status()


def set_absent_time(t): DailyScheduler.set_absent_time(t)


def set_report_time(t): DailyScheduler.set_report_time(t)


def trigger_absent_marking(): DailyScheduler.run_absent_marking_now()


def trigger_daily_report(): DailyScheduler.run_report_generation_now()


def trigger_15day_report(): DailyScheduler.run_15day_report_now()


def trigger_monthly_report(): DailyScheduler.run_monthly_report_now()