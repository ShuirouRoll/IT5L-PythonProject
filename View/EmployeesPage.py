from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
)


class EmployeesPage(QWidget):
    """Employee management page with improved styling"""

    def __init__(self):
        super().__init__()
        self.on_add_employee = None
        self.on_delete_employee = None
        self.on_edit_employee = None
        self.all_employees = []
        self.selected_row = -1
        self.build_ui()
        self.apply_theme("light")

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # Container
        self.container = QFrame()
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setSpacing(20)

        # Top row with buttons and sort
        top_row = QHBoxLayout()

        self.add_btn = QPushButton("+ Add Employee")
        self.add_btn.setFixedHeight(42)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        top_row.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Edit Employee")
        self.edit_btn.setFixedHeight(42)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.on_edit_clicked)
        top_row.addWidget(self.edit_btn)

        top_row.addStretch(1)

        self.sort_label = QLabel("Sort by:")
        top_row.addWidget(self.sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Name (A-Z)", "Name (Z-A)",
            "Email (A-Z)", "Email (Z-A)",
            "Date Hired (Newest)", "Date Hired (Oldest)"
        ])
        self.sort_combo.setFixedWidth(200)
        self.sort_combo.setFixedHeight(38)
        self.sort_combo.currentTextChanged.connect(self.sort_employees)
        top_row.addWidget(self.sort_combo)

        container_layout.addLayout(top_row)

        # Table - ADDED POSITION COLUMN
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "NAME", "POSITION", "EMAIL ADDRESS", "PHONE NUMBER",
            "USERNAME", "PASSWORD", "DATE HIRED"
        ])
        self.table.setRowCount(0)
        self.table.horizontalHeader().setVisible(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # FULL ROW CLICK - Connect to cellClicked instead of itemSelectionChanged
        self.table.cellClicked.connect(self.on_row_clicked)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        # Set column widths
        self.table.setColumnWidth(0, 230)
        self.table.setColumnWidth(1, 150)  # Position column
        self.table.setColumnWidth(2, 230)
        self.table.setColumnWidth(3, 140)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 120)

        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        container_layout.addWidget(self.table)
        layout.addWidget(self.container)

    def on_row_clicked(self, row, column):
        """Handle clicking anywhere on a row - only selects, doesn't edit"""
        if row >= 0 and row < len(self.all_employees):
            self.selected_row = row
            self.edit_btn.setEnabled(True)

    def on_selection_changed(self):
        """Handle row selection changes"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            self.selected_row = selected_rows[0].row()
            self.edit_btn.setEnabled(True)
        else:
            self.selected_row = -1
            self.edit_btn.setEnabled(False)

    def on_edit_clicked(self):
        """Handle edit button click"""
        if self.selected_row >= 0 and self.on_edit_employee:
            employee_data = self.all_employees[self.selected_row]
            self.on_edit_employee(employee_data)

    def populate_table(self, employees):
        """Populate table with employee data"""
        self.all_employees = employees
        self.sort_employees(self.sort_combo.currentText())

    def sort_employees(self, sort_option):
        """Sort employees based on selected criteria"""
        if not self.all_employees:
            return

        sorted_employees = self.all_employees.copy()

        if sort_option == "Name (A-Z)":
            sorted_employees.sort(key=lambda x: x.get("full_name", "").lower())
        elif sort_option == "Name (Z-A)":
            sorted_employees.sort(key=lambda x: x.get("full_name", "").lower(), reverse=True)
        elif sort_option == "Email (A-Z)":
            sorted_employees.sort(key=lambda x: x.get("email_address", "").lower())
        elif sort_option == "Email (Z-A)":
            sorted_employees.sort(key=lambda x: x.get("email_address", "").lower(), reverse=True)
        elif sort_option == "Date Hired (Newest)":
            sorted_employees.sort(key=lambda x: x.get("date_hired", ""), reverse=True)
        elif sort_option == "Date Hired (Oldest)":
            sorted_employees.sort(key=lambda x: x.get("date_hired", ""))

        self.display_employees(sorted_employees)

    def display_employees(self, employees):
        """Display employees in table"""
        self.table.setRowCount(len(employees))

        for row, emp in enumerate(employees):
            # Get data
            full_name = str(emp.get("full_name", ""))
            position = str(emp.get("position", "Staff"))  # Position data
            email = str(emp.get("email_address", ""))
            phone = str(emp.get("phone_number", ""))
            username = str(emp.get("username", ""))
            password = "••••••••"
            date_hired = emp.get("date_hired", "N/A")
            date_hired_str = str(date_hired) if date_hired and date_hired != "N/A" else "N/A"

            # Create items
            name_item = QTableWidgetItem(full_name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            position_item = QTableWidgetItem(position)
            position_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            email_item = QTableWidgetItem(email)
            email_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            phone_item = QTableWidgetItem(phone)
            phone_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            username_item = QTableWidgetItem(username)
            username_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            password_item = QTableWidgetItem(password)
            password_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

            date_item = QTableWidgetItem(date_hired_str)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

            # Set items
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, position_item)  # Position
            self.table.setItem(row, 2, email_item)
            self.table.setItem(row, 3, phone_item)
            self.table.setItem(row, 4, username_item)
            self.table.setItem(row, 5, password_item)
            self.table.setItem(row, 6, date_item)

        self.table.resizeRowsToContents()

    def apply_theme(self, theme):
        """Apply light or dark theme"""
        if theme == "dark":
            self.setStyleSheet("background-color: #111827;")
            self.container.setStyleSheet("""
                QFrame { 
                    background-color: #1f2937; 
                    border: 1px solid #374151; 
                    border-radius: 12px; 
                }
            """)
            self.add_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #374151; 
                    color: #f9fafb; 
                    border: none; 
                    border-radius: 8px; 
                    padding: 0 24px; 
                    font-weight: 600;
                    font-size: 14px;
                } 
                QPushButton:hover { 
                    background-color: #4b5563; 
                }
            """)
            self.edit_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #2563eb; 
                    color: #ffffff; 
                    border: none; 
                    border-radius: 8px; 
                    padding: 0 24px; 
                    font-weight: 600;
                    font-size: 14px;
                } 
                QPushButton:hover { 
                    background-color: #1d4ed8; 
                } 
                QPushButton:disabled { 
                    background-color: #4b5563; 
                    color: #9ca3af; 
                }
            """)
            self.sort_label.setStyleSheet("""
                color: #9ca3af; 
                background: transparent; 
                border: none;
                font-size: 14px;
            """)
            self.sort_combo.setStyleSheet("""
                background-color: #374151; 
                border: 1px solid #4b5563; 
                border-radius: 8px; 
                padding: 8px 14px; 
                color: #f9fafb;
                font-size: 14px;
            """)
            self.table.setStyleSheet("""
                QTableWidget { 
                    background-color: #1f2937; 
                    color: #f9fafb;
                    font-size: 14px;
                    gridline-color: #374151;
                    border: 1px solid #374151;
                }
                QTableWidget::item { 
                    padding: 14px; 
                    color: #f9fafb;
                }
                QTableWidget::item:selected {
                    background-color: #2563eb;
                    color: #ffffff;
                }
                QTableWidget::item:alternate { 
                    background-color: #111827; 
                }
                QHeaderView::section { 
                    background: #374151; 
                    padding: 14px 10px; 
                    border: none; 
                    font-weight: 600; 
                    color: #d1d5db;
                    font-size: 13px;
                }
            """)
        else:
            self.setStyleSheet("background-color: #f9fafb;")
            self.container.setStyleSheet("""
                QFrame { 
                    background-color: #ffffff; 
                    border: 1px solid #e5e7eb; 
                    border-radius: 12px; 
                }
            """)
            self.add_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #1f2937; 
                    color: #ffffff; 
                    border: none; 
                    border-radius: 8px; 
                    padding: 0 24px; 
                    font-weight: 600;
                    font-size: 14px;
                } 
                QPushButton:hover { 
                    background-color: #374151; 
                }
            """)
            self.edit_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #2563eb; 
                    color: #ffffff; 
                    border: none; 
                    border-radius: 8px; 
                    padding: 0 24px; 
                    font-weight: 600;
                    font-size: 14px;
                } 
                QPushButton:hover { 
                    background-color: #1d4ed8; 
                } 
                QPushButton:disabled { 
                    background-color: #d1d5db; 
                    color: #9ca3af; 
                }
            """)
            self.sort_label.setStyleSheet("""
                color: #6b7280; 
                background: transparent; 
                border: none;
                font-size: 14px;
            """)
            self.sort_combo.setStyleSheet("""
                background-color: #f9fafb; 
                border: 1px solid #d1d5db; 
                border-radius: 8px; 
                padding: 8px 14px; 
                color: #1f2937;
                font-size: 14px;
            """)
            self.table.setStyleSheet("""
                QTableWidget { 
                    background-color: #ffffff; 
                    color: #1f2937;
                    font-size: 14px;
                    gridline-color: #e5e7eb;
                    border: 1px solid #d1d5db;
                }
                QTableWidget::item { 
                    padding: 14px; 
                    color: #1f2937;
                }
                QTableWidget::item:selected {
                    background-color: #2563eb;
                    color: #ffffff;
                }
                QTableWidget::item:alternate { 
                    background-color: #f9fafb; 
                }
                QHeaderView::section { 
                    background: #f3f4f6; 
                    padding: 14px 10px; 
                    border: none; 
                    font-weight: 600; 
                    color: #4b5563;
                    font-size: 13px;
                }
            """)