from Project.Model.Database import Database


class Attendance:
    """Attendance model - handles table initialization only"""

    @classmethod
    def initialize(cls):
        """Create the attendance table if it doesn't exist"""
        db = Database.get()
        db.execute("""
                   CREATE TABLE IF NOT EXISTS attendance
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
                       clock_in
                       DATETIME,
                       clock_out
                       DATETIME,
                       date
                       DATE
                       NOT
                       NULL,
                       status
                       VARCHAR
                   (
                       50
                   ),
                       FOREIGN KEY
                   (
                       employee_id
                   ) REFERENCES employees
                   (
                       id
                   ) ON DELETE CASCADE
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                   """)
