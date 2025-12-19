from Project.Model.Database import Database


class PeriodicReports:
    """Model for handling 15-day and monthly attendance reports"""

    @classmethod
    def initialize(cls):
        """Create tables for periodic reports if they don't exist"""
        db = Database.get()

        # 15-Day Reports Table
        db.execute("""
                   CREATE TABLE IF NOT EXISTS reports_15day
                   (
                       id
                       INT
                       AUTO_INCREMENT
                       PRIMARY
                       KEY,
                       period_start
                       DATE
                       NOT
                       NULL,
                       period_end
                       DATE
                       NOT
                       NULL,
                       total_present
                       INT
                       DEFAULT
                       0,
                       total_late
                       INT
                       DEFAULT
                       0,
                       total_absent
                       INT
                       DEFAULT
                       0,
                       total_work_days
                       INT
                       DEFAULT
                       0,
                       average_present_rate
                       DECIMAL
                   (
                       5,
                       2
                   ) DEFAULT 0.00,
                       average_late_rate DECIMAL
                   (
                       5,
                       2
                   ) DEFAULT 0.00,
                       average_absent_rate DECIMAL
                   (
                       5,
                       2
                   ) DEFAULT 0.00,
                       generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       UNIQUE KEY unique_period
                   (
                       period_start,
                       period_end
                   ),
                       INDEX idx_period_start
                   (
                       period_start
                   ),
                       INDEX idx_period_end
                   (
                       period_end
                   )
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                   """)

        # Monthly Reports Table
        db.execute("""
                   CREATE TABLE IF NOT EXISTS reports_monthly
                   (
                       id
                       INT
                       AUTO_INCREMENT
                       PRIMARY
                       KEY,
                       year
                       INT
                       NOT
                       NULL,
                       month
                       INT
                       NOT
                       NULL,
                       period_start
                       DATE
                       NOT
                       NULL,
                       period_end
                       DATE
                       NOT
                       NULL,
                       total_present
                       INT
                       DEFAULT
                       0,
                       total_late
                       INT
                       DEFAULT
                       0,
                       total_absent
                       INT
                       DEFAULT
                       0,
                       total_work_days
                       INT
                       DEFAULT
                       0,
                       average_present_rate
                       DECIMAL
                   (
                       5,
                       2
                   ) DEFAULT 0.00,
                       average_late_rate DECIMAL
                   (
                       5,
                       2
                   ) DEFAULT 0.00,
                       average_absent_rate DECIMAL
                   (
                       5,
                       2
                   ) DEFAULT 0.00,
                       generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       UNIQUE KEY unique_month
                   (
                       year,
                       month
                   ),
                       INDEX idx_year_month
                   (
                       year,
                       month
                   )
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                   """)

        # Employee 15-Day Performance Table (detailed breakdown per employee)
        db.execute("""
                   CREATE TABLE IF NOT EXISTS employee_15day_performance
                   (
                       id
                       INT
                       AUTO_INCREMENT
                       PRIMARY
                       KEY,
                       employee_id
                       INT
                       NOT
                       NULL,
                       period_start
                       DATE
                       NOT
                       NULL,
                       period_end
                       DATE
                       NOT
                       NULL,
                       present_days
                       INT
                       DEFAULT
                       0,
                       late_days
                       INT
                       DEFAULT
                       0,
                       absent_days
                       INT
                       DEFAULT
                       0,
                       total_hours_worked
                       DECIMAL
                   (
                       8,
                       2
                   ) DEFAULT 0.00,
                       attendance_rate DECIMAL
                   (
                       5,
                       2
                   ) DEFAULT 0.00,
                       generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY
                   (
                       employee_id
                   ) REFERENCES employees
                   (
                       id
                   ) ON DELETE CASCADE,
                       UNIQUE KEY unique_emp_period
                   (
                       employee_id,
                       period_start,
                       period_end
                   ),
                       INDEX idx_employee
                   (
                       employee_id
                   ),
                       INDEX idx_period
                   (
                       period_start,
                       period_end
                   )
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                   """)

        # Employee Monthly Performance Table (detailed breakdown per employee)
        db.execute("""
                   CREATE TABLE IF NOT EXISTS employee_monthly_performance
                   (
                       id
                       INT
                       AUTO_INCREMENT
                       PRIMARY
                       KEY,
                       employee_id
                       INT
                       NOT
                       NULL,
                       year
                       INT
                       NOT
                       NULL,
                       month
                       INT
                       NOT
                       NULL,
                       period_start
                       DATE
                       NOT
                       NULL,
                       period_end
                       DATE
                       NOT
                       NULL,
                       present_days
                       INT
                       DEFAULT
                       0,
                       late_days
                       INT
                       DEFAULT
                       0,
                       absent_days
                       INT
                       DEFAULT
                       0,
                       total_hours_worked
                       DECIMAL
                   (
                       8,
                       2
                   ) DEFAULT 0.00,
                       attendance_rate DECIMAL
                   (
                       5,
                       2
                   ) DEFAULT 0.00,
                       generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY
                   (
                       employee_id
                   ) REFERENCES employees
                   (
                       id
                   ) ON DELETE CASCADE,
                       UNIQUE KEY unique_emp_month
                   (
                       employee_id,
                       year,
                       month
                   ),
                       INDEX idx_employee
                   (
                       employee_id
                   ),
                       INDEX idx_year_month
                   (
                       year,
                       month
                   )
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                   """)

        print("[PeriodicReports] Tables initialized: 15-day and monthly reports")