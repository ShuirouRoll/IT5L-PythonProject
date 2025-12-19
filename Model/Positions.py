from Project.Model.Database import Database


class Position:
    """Position model - handles table initialization and seeding only"""

    @classmethod
    def initialize(cls):
        """Create the positions table and seed default positions"""
        db = Database.get()

        # Create table
        db.execute("""
                   CREATE TABLE IF NOT EXISTS positions
                   (
                       id
                       INT
                       AUTO_INCREMENT
                       PRIMARY
                       KEY,
                       name
                       VARCHAR
                   (
                       100
                   ) NOT NULL UNIQUE,
                       late_time TIME DEFAULT '08:00:00',
                       grace_period_minutes INT DEFAULT 15,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                   """)

        # Seed default positions
        default_positions = [
            ('Staff', '08:00:00', 15),
            ('Maintenance', '07:00:00', 15),
            ('Security Guard', '06:00:00', 15),
            ('Team Head', '09:00:00', 15)
        ]

        for name, time, grace in default_positions:
            try:
                db.execute(
                    "INSERT IGNORE INTO positions (name, late_time, grace_period_minutes) VALUES (%s, %s, %s)",
                    (name, time, grace)
                )
            except:
                pass  # Position already exists
