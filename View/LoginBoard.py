import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QHBoxLayout
)


class LoginBoard(QWidget):
    """Login page with clean white background"""

    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path
        self.build_ui()
        self.apply_styles()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(20)
        root.addStretch(1)

        # Top section with logo and app name
        top = QHBoxLayout()
        top.addStretch(1)

        # Logo - use the DARK logo for white background
        self.logo_label = QLabel()
        self.logo_label.setObjectName("logoIcon")
        self.logo_label.setFixedSize(60, 60)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("background: transparent; border: none;")

        # Try to load the dark/black logo for visibility on white background
        logo_loaded = False
        try:
            if isinstance(self.logo_path, dict):
                # If logo_path is a dictionary, try to get the black/dark version
                dark_logo = self.logo_path.get('black') or self.logo_path.get('dark')
                if dark_logo and os.path.exists(dark_logo):
                    pixmap = QPixmap(dark_logo)
                    if not pixmap.isNull():
                        scaled = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
                        self.logo_label.setPixmap(scaled)
                        logo_loaded = True
            elif self.logo_path and os.path.exists(self.logo_path):
                pixmap = QPixmap(self.logo_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
                    self.logo_label.setPixmap(scaled)
                    logo_loaded = True
        except Exception as e:
            print(f"[LoginBoard] Logo loading error: {e}")

        if not logo_loaded:
            self.logo_label.setText("◉")
            self.logo_label.setStyleSheet("font-size: 36px; color: #1f2937; background: transparent; border: none;")

        # App name
        app_name = QLabel("Frontera's All-Seeing Ledger")
        app_name.setObjectName("appName")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top.addWidget(self.logo_label)
        top.addSpacing(16)
        top.addWidget(app_name)
        top.addStretch(1)
        root.addLayout(top)

        root.addSpacing(20)

        # Login card
        card = QGroupBox()
        card.setObjectName("loginCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # Username field
        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.username.setObjectName("fieldInput")
        self.username.setFixedHeight(48)
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username)

        # Password field
        pwd_label = QLabel("Password")
        pwd_label.setObjectName("fieldLabel")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setObjectName("fieldInput")
        self.password.setFixedHeight(48)
        card_layout.addWidget(pwd_label)
        card_layout.addWidget(self.password)

        # Login type label
        self.login_type_label = QLabel("Logging in as: Admin or Employee")
        self.login_type_label.setObjectName("loginTypeLabel")
        self.login_type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.login_type_label)

        card_layout.addSpacing(12)

        # Login button
        self.login_btn = QPushButton("Log in")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setFixedHeight(52)
        self.login_btn.setDefault(True)
        self.login_btn.setAutoDefault(True)
        card_layout.addWidget(self.login_btn)

        # Connect Enter key to login
        self.username.returnPressed.connect(self.login_btn.click)
        self.password.returnPressed.connect(self.login_btn.click)

        # Center the card
        card_holder = QHBoxLayout()
        card_holder.addStretch(1)
        card_holder.addWidget(card)
        card_holder.addStretch(1)
        root.addLayout(card_holder)
        root.addStretch(2)

    def get_credentials(self):
        """Get entered username and password"""
        return self.username.text().strip(), self.password.text()

    def show_error(self, message):
        """Show error message (using dialog from main controller)"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Login Failed", message)

    def clear_fields(self):
        """Clear username and password fields"""
        self.username.clear()
        self.password.clear()

    def apply_styles(self):
        """Apply clean white background styling - FORCE WHITE"""
        self.setStyleSheet("""
            LoginBoard { 
                background-color: #ffffff;
            }
            QWidget { 
                background-color: #ffffff;
            }
            #loginTypeLabel { 
                color: #6b7280; 
                font-size: 12px; 
                font-style: italic;
                background: transparent;
                border: none;
                margin-top: 8px;
            }
            #logoIcon { 
                font-size: 36px; 
                color: #1f2937; 
                background: transparent;
                border: none;
            }
            #appName { 
                font-weight: 700; 
                color: #1f2937; 
                font-size: 18px;
                background: transparent;
                border: none;
            }
            #loginCard { 
                background: #f9fafb; 
                border-radius: 16px; 
                max-width: 420px;
                min-width: 420px;
                border: 1px solid #e5e7eb; 
            }
            #fieldLabel { 
                color: #374151; 
                font-size: 14px; 
                font-weight: 600; 
                margin-top: 4px;
                background: transparent;
                border: none;
            }
            QLineEdit { 
                background: #ffffff; 
                color: #1f2937; 
                border: 2px solid #d1d5db; 
                border-radius: 10px; 
                padding-left: 16px;
                padding-right: 16px;
                font-size: 15px; 
            }
            QLineEdit:focus { 
                border: 2px solid #3b82f6; 
                background: #ffffff; 
            }
            #loginBtn { 
                background: #1f2937; 
                color: #ffffff; 
                border-radius: 10px; 
                font-weight: 600; 
                font-size: 16px; 
            }
            #loginBtn:hover { 
                background: #374151; 
            }
        """)