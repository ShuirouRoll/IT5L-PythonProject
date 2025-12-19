from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QApplication


class MainWindow(QMainWindow):
    def __init__(self, sidebar, header, pages):
        super().__init__()
        self.sidebar = sidebar
        self.header = header
        self.pages = pages
        # Order: 0=Login, 1=Overview, 2=Employees, 3=Reports, 4=Requests, 5=Settings

        self.current_theme = "light"
        self.setWindowTitle("Attendance Monitoring System")
        self.build_ui()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        # MAIN LAYOUT (Horizontal: Sidebar | Content)
        self.main_layout = QHBoxLayout(central)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. ADD SIDEBAR (Hidden by default for login)
        self.main_layout.addWidget(self.sidebar)

        # 2. RIGHT SIDE (Header + Pages)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header
        right_layout.addWidget(self.header)

        # Stacked Pages
        self.stack = QStackedWidget()
        for page in self.pages:
            self.stack.addWidget(page)

        right_layout.addWidget(self.stack)

        self.main_layout.addWidget(right_widget)

    def show_login(self):
        """Switch to Login Mode: Small window, No Sidebar, WHITE BACKGROUND"""
        self.sidebar.hide()
        self.header.hide()
        self.stack.setCurrentIndex(0)  # Login Page

        # FORCE WHITE BACKGROUND FOR LOGIN
        self.setStyleSheet("QMainWindow { background-color: #ffffff; }")

        # Lock size for login
        self.setMinimumSize(600, 650)
        self.setMaximumSize(600, 650)
        self.resize(600, 650)
        self.center_window()

    def show_main(self):
        """Switch to App Mode: Optimal size, Show Sidebar"""
        self.sidebar.show()
        self.header.show()

        # Set optimal size (fits screen without being maximized)
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()

            # Use 90% of screen dimensions for a nice fit
            width = int(screen_geometry.width() * 0.90)
            height = int(screen_geometry.height() * 0.90)

            # Set minimum size
            self.setMinimumSize(1200, 700)

            # Remove maximum size constraint
            self.setMaximumSize(16777215, 16777215)

            # Resize to calculated size
            self.resize(width, height)

            # Center the window
            self.center_window()
        else:
            # Fallback if no screen detected
            self.setMinimumSize(1200, 700)
            self.setMaximumSize(16777215, 16777215)
            self.resize(1400, 800)
            self.center_window()

        # Default to Dashboard if we aren't already on a specific page
        if self.stack.currentIndex() == 0:
            self.show_page(1, "Overview")

    def show_page(self, index, title):
        self.stack.setCurrentIndex(index)
        self.header.set_title(title)

    def apply_theme(self, theme):
        self.current_theme = theme
        self.header.apply_theme(theme)
        # Apply to pages
        for i in range(self.stack.count()):
            page = self.stack.widget(i)
            if hasattr(page, 'apply_theme'):
                page.apply_theme(theme)

        if theme == "dark":
            self.setStyleSheet("QMainWindow { background-color: #111827; }")
        else:
            self.setStyleSheet("QMainWindow { background-color: #f9fafb; }")

    def center_window(self):
        screen = QApplication.primaryScreen()
        if screen:
            rect = screen.availableGeometry()
            center = rect.center()
            frame = self.frameGeometry()
            frame.moveCenter(center)
            self.move(frame.topLeft())

    def show_login_success(self, user_type, user_name):
        """This will be replaced by Main.py with the actual dialog function"""
        pass