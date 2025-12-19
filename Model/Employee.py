import hashlib
import secrets
from Project.Model.Database import Database

ITERATIONS = 100000
SALT_BYTES = 16


class Employee:
    """Employee model - handles table initialization and utility functions only"""

    @classmethod
    def initialize(cls):
        """Create the employees table if it doesn't exist"""
        db = Database.get()
        db.execute("""
                   CREATE TABLE IF NOT EXISTS employees
                   (
                       id
                       INT
                       AUTO_INCREMENT
                       PRIMARY
                       KEY,
                       first_name
                       VARCHAR
                   (
                       100
                   ) NOT NULL,
                       middle_initial VARCHAR
                   (
                       10
                   ),
                       last_name VARCHAR
                   (
                       100
                   ) NOT NULL,
                       email_address VARCHAR
                   (
                       255
                   ),
                       phone_number VARCHAR
                   (
                       64
                   ),
                       username VARCHAR
                   (
                       255
                   ) NOT NULL UNIQUE,
                       password_hash VARCHAR
                   (
                       512
                   ) NOT NULL,
                       salt VARCHAR
                   (
                       64
                   ) NOT NULL,
                       date_hired DATE NOT NULL,
                       position_id INT DEFAULT 1,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY
                   (
                       position_id
                   ) REFERENCES positions
                   (
                       id
                   )
                       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                   """)

    @staticmethod
    def hash_password(password, salt):
        """Hash a password with salt using PBKDF2"""
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS).hex()

    @staticmethod
    def concat_name(first, middle, last):
        """Concatenate name parts into full name"""
        parts = [first]
        if middle:
            parts.append(middle + ".")
        parts.append(last)
        return " ".join(parts)

    @staticmethod
    def authenticate(username, password):
        """
        Authenticate an employee - moved here for compatibility
        This is a utility function, not business logic
        """
        db = Database.get()
        user = db.query_one("SELECT * FROM employees WHERE username = %s", (username,))
        if not user:
            return None

        salt = bytes.fromhex(user["salt"])
        if secrets.compare_digest(Employee.hash_password(password, salt), user["password_hash"]):
            return {
                "id": user["id"],
                "full_name": Employee.concat_name(
                    user["first_name"],
                    user.get("middle_initial"),
                    user["last_name"]
                ),
                "position_id": user.get("position_id")
            }
        return None