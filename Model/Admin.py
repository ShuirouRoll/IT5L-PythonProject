import hashlib
import secrets

from Project.Model.Database import Database
from Project.Model.Employee import ITERATIONS, SALT_BYTES


class Admin:
    """Admin model - handles table initialization and utility functions only"""

    @classmethod
    def initialize(cls):
        """Create the admins table if it doesn't exist"""
        db = Database.get()
        db.execute("""
                   CREATE TABLE IF NOT EXISTS admins
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
                       theme VARCHAR
                   (
                       32
                   ) DEFAULT 'light'
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

    @classmethod
    def authenticate(cls, username, password):
        """
        Authenticate an admin - utility function
        """
        cls.initialize()
        db = Database.get()
        user = db.query_one("SELECT * FROM admins WHERE username = %s", (username,))
        if not user:
            return None

        salt = bytes.fromhex(user["salt"])
        if secrets.compare_digest(cls.hash_password(password, salt), user["password_hash"]):
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": cls.concat_name(
                    user["first_name"],
                    user["middle_initial"],
                    user["last_name"]
                ),
                "theme": user.get("theme", "light")
            }
        return None

    @classmethod
    def create_admin(cls, first_name, middle_initial, last_name, email, phone, username, password):
        """Create a new admin - utility for seeding"""
        cls.initialize()
        db = Database.get()
        salt = secrets.token_bytes(SALT_BYTES)
        pw_hash = cls.hash_password(password, salt)
        cur = db.execute(
            """INSERT INTO admins
               (first_name, middle_initial, last_name, email_address, phone_number,
                username, password_hash, salt)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (first_name, middle_initial, last_name, email, phone, username, pw_hash, salt.hex())
        )
        return cur.lastrowid

    @classmethod
    def update_password(cls, admin_id, new_password):
        """Update admin password - utility"""
        db = Database.get()
        salt = secrets.token_bytes(SALT_BYTES)
        pw_hash = cls.hash_password(new_password, salt)
        db.execute(
            "UPDATE admins SET password_hash = %s, salt = %s WHERE id = %s",
            (pw_hash, salt.hex(), admin_id)
        )

    @classmethod
    def update_theme(cls, admin_id, theme):
        """Update admin theme preference - utility"""
        db = Database.get()
        db.execute("UPDATE admins SET theme = %s WHERE id = %s", (theme, admin_id))

    @classmethod
    def verify_password(cls, admin_id, password):
        """Verify admin password - utility"""
        db = Database.get()
        user = db.query_one("SELECT password_hash, salt FROM admins WHERE id = %s", (admin_id,))
        if not user:
            return False
        salt = bytes.fromhex(user["salt"])
        return secrets.compare_digest(cls.hash_password(password, salt), user["password_hash"])

    @classmethod
    def ensure_default_admin(cls):
        """Create default admin if none exists - utility"""
        cls.initialize()
        db = Database.get()
        row = db.query_one("SELECT COUNT(1) AS c FROM admins")
        if row and row["c"] == 0:
            cls.create_admin("System", "", "Administrator", "admin@company.com", "", "admin", "admin123")
            print("[Admin] Default admin created: admin / admin123")

    @classmethod
    def update_credentials(cls, admin_id, new_username, new_password):
        """Update admin credentials - utility"""
        db = Database.get()
        salt = secrets.token_bytes(SALT_BYTES)
        pw_hash = cls.hash_password(new_password, salt)
        db.execute(
            "UPDATE admins SET username = %s, password_hash = %s, salt = %s WHERE id = %s",
            (new_username, pw_hash, salt.hex(), admin_id)
        )
