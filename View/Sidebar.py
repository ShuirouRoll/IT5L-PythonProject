import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton


class Sidebar(QFrame):
    """Modern sidebar with improved styling"""

    def __init__(self, app_name, logo_paths):
        super().__init__()
        self.app_name = app_name
        self.logo_paths = logo_paths
        self.active_button = None
        self.setFixedWidth(240)
        self.setStyleSheet("background-color: #1f2937;")
        self.build()

    def build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(12)

        # Logo container
        logo_container = QHBoxLayout()
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(56, 56)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("""
            background-color: transparent; 
            border: none;
        """)

        # Try to load white logo for sidebar
        logo_loaded = False
        try:
            logo_path = None
            if isinstance(self.logo_paths, dict):
                logo_path = self.logo_paths.get('white')

            if logo_path and os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
                    self.logo_label.setPixmap(scaled)
                    logo_loaded = True
        except Exception as e:
            print(f"[Sidebar] Logo error: {e}")

        if not logo_loaded:
            self.logo_label.setText("◉")
            self.logo_label.setStyleSheet("""
                font-size: 32px; 
                color: #f9fafb; 
                background-color: transparent; 
                border: none;
            """)

        logo_container.addWidget(self.logo_label)
        layout.addLayout(logo_container)

        # App name
        self.app_name_label = QLabel(self.app_name)
        self.app_name_label.setWordWrap(True)
        self.app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_name_label.setStyleSheet("""
            color: #f9fafb; 
            font-size: 14px; 
            font-weight: 600; 
            padding: 10px;
        """)
        layout.addWidget(self.app_name_label)

        layout.addSpacing(28)

        # Navigation buttons with icons from logo_paths
        self.btn_overview = self.create_nav_button("Overview", self.logo_paths.get('overview'))
        self.btn_employees = self.create_nav_button("Employees", self.logo_paths.get('employee'))
        self.btn_reports = self.create_nav_button("Reports", self.logo_paths.get('reports'))
        self.btn_requests = self.create_nav_button("Requests", self.logo_paths.get('requests'))
        self.btn_settings = self.create_nav_button("Settings", self.logo_paths.get('settings'))

        layout.addWidget(self.btn_overview)
        layout.addWidget(self.btn_employees)
        layout.addWidget(self.btn_reports)
        layout.addWidget(self.btn_requests)
        layout.addWidget(self.btn_settings)

        # Set Overview as default active
        self.set_active_button(self.btn_overview)

        layout.addStretch(1)

        # Logout button
        self.btn_logout = QPushButton("Log out")
        self.btn_logout.setFixedHeight(44)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ef4444;
                border: 2px solid #ef4444;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                outline: none;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: #ffffff;
            }
            QPushButton:focus {
                outline: none;
                border: 2px solid #ef4444;
            }
        """)
        layout.addWidget(self.btn_logout)

    def create_nav_button(self, text, icon_path):
        """Create a navigation button with icon"""
        btn = QPushButton(text)
        btn.setFixedHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Add click handler to update active state
        btn.clicked.connect(lambda: self.set_active_button(btn))

        # Try to load icon if provided
        if icon_path and os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                btn.setIcon(icon)
                btn.setIconSize(QSize(20, 20))
                print(f"[Sidebar] Icon loaded for {text}: {icon_path}")
            except Exception as e:
                print(f"[Sidebar] Icon error for {text}: {e}")
        else:
            print(f"[Sidebar] Icon path not found for {text}: {icon_path}")

        # Set initial inactive style
        self.set_button_inactive(btn)

        return btn

    def set_active_button(self, button):
        """Set a button as active and deactivate others"""
        # Deactivate all buttons
        for btn in [self.btn_overview, self.btn_employees, self.btn_reports,
                    self.btn_requests, self.btn_settings]:
            self.set_button_inactive(btn)

        # Activate selected button
        self.set_button_active(button)
        self.active_button = button

    def set_button_active(self, button):
        """Apply active button style"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding-left: 16px;
                text-align: left;
                font-size: 14px;
                font-weight: 600;
                outline: none;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)

    def set_button_inactive(self, button):
        """Apply inactive button style"""
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #d1d5db;
                border: none;
                border-radius: 8px;
                padding-left: 16px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                outline: none;
            }
            QPushButton:hover {
                background-color: #374151;
                color: #f9fafb;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)