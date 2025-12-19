from Project.Model.Admin import Admin


class AuthController:
    _current_admin = None

    @classmethod
    def login(cls, username, password):
        admin = Admin.authenticate(username, password)
        if admin:
            cls._current_admin = admin
            return admin
        return None

    @classmethod
    def logout(cls):
        cls._current_admin = None

    @classmethod
    def get_current_admin(cls):
        return cls._current_admin

    @classmethod
    def change_credentials(cls, admin_id, current_password, new_username, new_password):
        """Change admin username and password"""
        # Verify current password
        if not Admin.verify_password(admin_id, current_password):
            return False

        # Update credentials
        Admin.update_credentials(admin_id, new_username, new_password)
        return True

    @classmethod
    def change_theme(cls, admin_id, theme):
        Admin.update_theme(admin_id, theme)
        if cls._current_admin and cls._current_admin.get("id") == admin_id:
            cls._current_admin["theme"] = theme