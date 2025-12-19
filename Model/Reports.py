from Project.Model.Database import Database


class Reports:
    """Reports model - handles table initialization only"""

    @classmethod
    def initialize(cls):
        """Create the reports table if it doesn't exist"""
        db = Database.get()
        db.execute("""
                   CREATE TABLE IF NOT EXISTS reports
                   (
                       id
                       INT
                       AUTO_INCREMENT
                       PRIMARY
                       KEY,
                       date
                       DATE
                       NOT
                       NULL
                       UNIQUE,
                       total_present_employees
                       INT
                       DEFAULT
                       0,
                       total_absent_employees
                       INT
                       DEFAULT
                       0,
                       total_late_employees
                       INT
                       DEFAULT
                       0
                   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                   """)