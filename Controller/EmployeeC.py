import secrets
from datetime import date
from Project.Model.Database import Database
from Project.Model.Employee import Employee


class EmployeeController:

    @staticmethod
    def initialize_tables():
        Employee.initialize()

    @staticmethod
    def list_employees():
        """Get formatted list of all employees"""
        db = Database.get()
        # Join with positions to show position name
        query = """
                SELECT e.*, p.name as position_name
                FROM employees e
                         LEFT JOIN positions p ON e.position_id = p.id
                ORDER BY e.id DESC \
                """
        employees = db.query_all(query)

        formatted = []
        for emp in employees:
            formatted.append({
                'id': emp['id'],
                'full_name': Employee.concat_name(emp['first_name'], emp.get('middle_initial'), emp['last_name']),
                'email_address': emp.get('email_address'),
                'phone_number': emp.get('phone_number'),
                'username': emp.get('username'),
                'position': emp.get('position_name', 'Staff'),
                'date_hired': str(emp.get('date_hired'))
            })
        return formatted

    @staticmethod
    def authenticate(username, password):
        db = Database.get()
        user = db.query_one("SELECT * FROM employees WHERE username = %s", (username,))

        if not user: return None

        salt = bytes.fromhex(user["salt"])
        # Verify password
        if secrets.compare_digest(Employee.hash_password(password, salt), user["password_hash"]):
            return {
                "id": user["id"],
                "full_name": Employee.concat_name(user["first_name"], user["middle_initial"], user["last_name"]),
                "position_id": user.get("position_id")
            }
        return None

    @staticmethod
    def add_employee(data):
        db = Database.get()
        # Check duplicates
        if EmployeeController._check_duplicates(data['username'], data['email_address'], data['phone_number']):
            raise Exception("Duplicate credentials found (Username, Email, or Phone).")

        salt = secrets.token_bytes(16)
        pw_hash = Employee.hash_password(data['password'], salt)

        query = """
                INSERT INTO employees
                (first_name, middle_initial, last_name, email_address, phone_number,
                 username, password_hash, salt, date_hired, position_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                """
        db.execute(query, (
            data['first_name'], data.get('middle_initial', ''), data['last_name'],
            data['email_address'], data['phone_number'], data['username'],
            pw_hash, salt.hex(), date.today(), data.get('position_id', 1)
        ))

    @staticmethod
    def update_employee(emp_id, data):
        db = Database.get()
        updates = []
        params = []

        fields = ['email_address', 'phone_number', 'username', 'position_id']
        keys = ['email', 'phone', 'username', 'position_id']

        for field, key in zip(fields, keys):
            if key in data and data[key] is not None:
                updates.append(f"{field} = %s")
                params.append(data[key])

        if 'password' in data and data['password']:
            salt = secrets.token_bytes(16)
            pw_hash = Employee.hash_password(data['password'], salt)
            updates.append("password_hash = %s")
            updates.append("salt = %s")
            params.extend([pw_hash, salt.hex()])

        if not updates: return

        params.append(emp_id)
        db.execute(f"UPDATE employees SET {', '.join(updates)} WHERE id = %s", tuple(params))

    @staticmethod
    def delete_employee(emp_id):
        Database.get().execute("DELETE FROM employees WHERE id = %s", (emp_id,))

    @staticmethod
    def _check_duplicates(u, e, p, exclude=None):
        db = Database.get()
        q = "SELECT id FROM employees WHERE username=%s OR email_address=%s OR phone_number=%s"
        args = [u, e, p]
        if exclude:
            q += " AND id != %s"
            args.append(exclude)
        return db.query_one(q, tuple(args)) is not None