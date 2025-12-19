from Project.Model.Database import Database
# *** CHANGE THIS IMPORT TO MATCH YOUR FILENAME ***
from Project.Model.Request import LeaveRequest


class LeaveRequestController:
    @staticmethod
    def initialize_tables():
        """Creates the table if it doesn't exist"""
        LeaveRequest.initialize()

    @staticmethod
    def submit_request(employee_id, leave_type, start_date, end_date, reason):
        db = Database.get()
        try:
            db.execute("""
                       INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, reason)
                       VALUES (%s, %s, %s, %s, %s)
                       """, (employee_id, leave_type, start_date, end_date, reason))
            return True
        except Exception as e:
            print(f"[RequestC] Error submitting request: {e}")
            return False

    @staticmethod
    def get_all_requests(status_filter=None):
        db = Database.get()
        # Join with employees and positions to get names
        query = """
                SELECT r.id, \
                       r.leave_type, \
                       r.start_date, \
                       r.end_date, \
                       r.reason, \
                       r.status, \
                       r.created_at,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                       p.name as position
                FROM leave_requests r
                    JOIN employees e \
                ON r.employee_id = e.id
                    LEFT JOIN positions p ON e.position_id = p.id \
                """
        params = []
        if status_filter:
            query += " WHERE r.status = %s"
            params.append(status_filter)

        query += " ORDER BY r.created_at DESC"

        try:
            return db.query_all(query, tuple(params))
        except Exception as e:
            print(f"[RequestC] Error getting requests: {e}")
            return []

    @staticmethod
    def update_status(request_id, new_status):
        db = Database.get()
        try:
            db.execute("UPDATE leave_requests SET status = %s WHERE id = %s", (new_status, request_id))
            return True
        except Exception as e:
            print(f"[RequestC] Error updating status: {e}")
            return False