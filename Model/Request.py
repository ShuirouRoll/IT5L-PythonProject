from Project.Model.Database import Database


class LeaveRequest:
    """Leave Request model - handles table initialization only"""

    @classmethod
    def initialize(cls):
        """Create the leave_requests table if it doesn't exist"""
        db = Database.get()
        db.execute("""
                   CREATE TABLE IF NOT EXISTS leave_requests
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
                       leave_type
                       VARCHAR
                   (
                       100
                   ) NOT NULL,
                       start_date DATE NOT NULL,
                       end_date DATE NOT NULL,
                       reason TEXT,
                       status VARCHAR
                   (
                       20
                   ) DEFAULT 'Pending',
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY
                   (
                       employee_id
                   ) REFERENCES employees
                   (
                       id
                   ) ON DELETE CASCADE
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                   """)