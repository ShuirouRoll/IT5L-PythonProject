from Project.Model.Database import Database
from Project.Model.Positions import Position


class PositionController:
    """Controller for position operations - handles all business logic and queries"""

    @staticmethod
    def initialize_tables():
        """Initialize positions table and seed default positions"""
        Position.initialize()

    @staticmethod
    def get_all_positions():
        """
        Fetch all positions ordered by name

        Returns:
            List of position dictionaries
        """
        db = Database.get()
        query = "SELECT * FROM positions ORDER BY name"
        return db.query_all(query)

    @staticmethod
    def get_position_by_id(position_id):
        """
        Get a specific position by ID

        Args:
            position_id: Position ID

        Returns:
            Dictionary with position data or None
        """
        db = Database.get()
        query = "SELECT * FROM positions WHERE id = %s"
        return db.query_one(query, (position_id,))

    @staticmethod
    def add_position(name, late_time_str, grace_period):
        """
        Add a new position to the system

        Args:
            name: Position name
            late_time_str: Time when employee is considered late (HH:MM:SS format)
            grace_period: Grace period in minutes after late_time

        Returns:
            Tuple of (success: bool, message: str)
        """
        db = Database.get()
        try:
            # Check if position name already exists
            exists = db.query_one(
                "SELECT id FROM positions WHERE name = %s",
                (name,)
            )
            if exists:
                return False, "Position name already exists."

            # Insert new position
            query = """
                    INSERT INTO positions
                        (name, late_time, grace_period_minutes)
                    VALUES (%s, %s, %s) \
                    """
            db.execute(query, (name, late_time_str, grace_period))
            return True, "Position added successfully."

        except Exception as e:
            print(f"[PositionC] Error adding position: {e}")
            return False, str(e)

    @staticmethod
    def update_position(position_id, name=None, late_time=None, grace_period=None):
        """
        Update an existing position

        Args:
            position_id: Position ID to update
            name: New name (optional)
            late_time: New late time (optional)
            grace_period: New grace period (optional)

        Returns:
            Tuple of (success: bool, message: str)
        """
        db = Database.get()
        try:
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)

            if late_time is not None:
                updates.append("late_time = %s")
                params.append(late_time)

            if grace_period is not None:
                updates.append("grace_period_minutes = %s")
                params.append(grace_period)

            if not updates:
                return False, "No fields to update."

            params.append(position_id)
            query = f"UPDATE positions SET {', '.join(updates)} WHERE id = %s"
            db.execute(query, tuple(params))

            return True, "Position updated successfully."

        except Exception as e:
            print(f"[PositionC] Error updating position: {e}")
            return False, str(e)

    @staticmethod
    def delete_position(position_id):
        """
        Delete a position (if no employees are assigned to it)

        Args:
            position_id: Position ID to delete

        Returns:
            Tuple of (success: bool, message: str)
        """
        db = Database.get()
        try:
            # Check if any employees are using this position
            employee_count = db.query_one(
                "SELECT COUNT(*) as count FROM employees WHERE position_id = %s",
                (position_id,)
            )

            if employee_count and employee_count['count'] > 0:
                return False, f"Cannot delete position: {employee_count['count']} employee(s) are assigned to it."

            # Delete position
            query = "DELETE FROM positions WHERE id = %s"
            db.execute(query, (position_id,))
            return True, "Position deleted successfully."

        except Exception as e:
            print(f"[PositionC] Error deleting position: {e}")
            return False, str(e)

    @staticmethod
    def get_employees_by_position(position_id):
        """
        Get all employees assigned to a specific position

        Args:
            position_id: Position ID

        Returns:
            List of employee dictionaries
        """
        db = Database.get()
        try:
            query = """
                    SELECT e.id, \
                           CONCAT(e.first_name, ' ', IFNULL(e.middle_initial, ''), ' ', e.last_name) as full_name, \
                           e.email_address, \
                           e.username
                    FROM employees e
                    WHERE e.position_id = %s
                    ORDER BY e.first_name, e.last_name \
                    """
            return db.query_all(query, (position_id,))
        except Exception as e:
            print(f"[PositionC] Error getting employees by position: {e}")
            return []

    @staticmethod
    def get_position_count():
        """
        Get total number of positions

        Returns:
            Integer count of positions
        """
        db = Database.get()
        try:
            result = db.query_one("SELECT COUNT(*) as count FROM positions")
            return result['count'] if result else 0
        except Exception as e:
            print(f"[PositionC] Error getting position count: {e}")
            return 0