from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QSizePolicy, QFrame
)


class StatCard(QFrame):
    """Enhanced stat card with color themes"""

    def __init__(self, icon, title, value="", color_theme="default"):
        super().__init__()
        self.color_theme = color_theme
        self.setObjectName(f"statCard_{color_theme}")
        self.setFixedHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.build(icon, title, value)

    def build(self, icon, title, value):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Icon container
        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")

        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        layout.addLayout(text_layout)
        layout.addStretch(1)

    def set_value(self, value):
        """Update the stat value"""
        self.value_label.setText(value)


class AdminDashboard(QWidget):
    """Main admin dashboard with attendance stats and log - integrated into MainWindow"""

    def __init__(self):
        super().__init__()
        self.build_ui()
        self.apply_theme("light")  # Set default theme

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(20)

        # Subtitle
        subtitle = QLabel("Today's Attendance Overview")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(subtitle)

        # Stats cards row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)

        self.card_total = StatCard("👥", "Total Employees", "", color_theme="default")
        self.card_signed = StatCard("✓", "Signed In Today", "", color_theme="jade")
        self.card_absent = StatCard("✗", "Absent Today", "", color_theme="crimson")

        cards_row.addWidget(self.card_total)
        cards_row.addWidget(self.card_signed)
        cards_row.addWidget(self.card_absent)
        root.addLayout(cards_row)

        # Attendance log container
        log_container = QGroupBox()
        log_container.setObjectName("logContainer")
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(24, 20, 24, 20)
        log_layout.setSpacing(16)

        # Header with search
        header_row = QHBoxLayout()
        log_title = QLabel("Attendance Log")
        log_title.setObjectName("logTitle")
        header_row.addWidget(log_title)
        header_row.addStretch(1)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search employees...")
        self.search_input.setObjectName("searchInput")
        self.search_input.setFixedWidth(220)
        self.search_input.setFixedHeight(38)
        header_row.addWidget(self.search_input)

        log_layout.addLayout(header_row)

        # Table
        columns = ["Employee ID", "Name", "Status", "Time In", "Time Out"]
        self.table = QTableWidget(0, len(columns))
        self.table.setObjectName("attendanceTable")
        self.table.setHorizontalHeaderLabels(columns)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        log_layout.addWidget(self.table)
        root.addWidget(log_container)

    def update_stats(self, total, signed_in, absent):
        """Update the stat cards with new values"""
        self.card_total.set_value(f"{total} Employees")
        self.card_signed.set_value(f"{signed_in} Employees")
        self.card_absent.set_value(f"{absent} Employees")

    def populate_attendance_table(self, records):
        """Populate the attendance table with records"""
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            # Employee ID
            self.table.setItem(row, 0, QTableWidgetItem(str(record.get("employee_id", ""))))

            # Name
            self.table.setItem(row, 1, QTableWidgetItem(str(record.get("employee_name", ""))))

            # Status
            status = str(record.get("status", ""))
            status_item = QTableWidgetItem(status)
            if status == "Present":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif status == "Late":
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif status == "Absent":
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 2, status_item)

            # Clock In
            self.table.setItem(row, 3, QTableWidgetItem(str(record.get("clock_in", "") or "-")))

            # Clock Out
            time_out = record.get("clock_out", "")
            self.table.setItem(row, 4, QTableWidgetItem(str(time_out) if time_out else "-"))

    def apply_theme(self, theme):
        """Apply light or dark theme"""
        # Color scheme
        jade = "#0EA574"  # Slightly darker jade
        crimson = "#C41230"  # Slightly darker crimson

        stat_card_styles = f"""
            /* Default Card */
            #statCard_default {{ 
                background-color: white; 
                border: 1px solid #e5e7eb; 
                border-radius: 12px;
                border-left: 4px solid #3b82f6;
            }}
            #statCard_default #statIcon {{ 
                background-color: #f3f4f6; 
                color: #3b82f6; 
                border-radius: 24px;
                font-size: 24px;
            }}
            #statCard_default #statTitle {{ 
                color: #6b7280; 
                font-size: 13px; 
                font-weight: 600; 
            }}
            #statCard_default #statValue {{ 
                color: #1f2937; 
                font-size: 22px; 
                font-weight: 700; 
            }}

            /* Jade Card (Signed In) */
            #statCard_jade {{ 
                background-color: {jade}; 
                border: 1px solid {jade}; 
                border-radius: 12px; 
            }}
            #statCard_jade #statIcon {{ 
                background-color: rgba(255, 255, 255, 0.2); 
                color: #ffffff; 
                border-radius: 24px;
                font-size: 24px;
            }}
            #statCard_jade #statTitle {{ 
                color: rgba(255, 255, 255, 0.9); 
                font-size: 13px; 
                font-weight: 600; 
            }}
            #statCard_jade #statValue {{ 
                color: #ffffff; 
                font-size: 22px; 
                font-weight: 700; 
            }}

            /* Crimson Card (Absent) */
            #statCard_crimson {{ 
                background-color: {crimson}; 
                border: 1px solid {crimson}; 
                border-radius: 12px; 
            }}
            #statCard_crimson #statIcon {{ 
                background-color: rgba(255, 255, 255, 0.2); 
                color: #ffffff; 
                border-radius: 24px;
                font-size: 24px;
            }}
            #statCard_crimson #statTitle {{ 
                color: rgba(255, 255, 255, 0.9); 
                font-size: 13px; 
                font-weight: 600; 
            }}
            #statCard_crimson #statValue {{ 
                color: #ffffff; 
                font-size: 22px; 
                font-weight: 700; 
            }}
        """

        if theme == "dark":
            base_style = """
                QWidget { background: #111827; color: #f9fafb; }
                #pageSubtitle { color: #9ca3af; font-size: 15px; font-weight: 500; }
                #logContainer { 
                    background: #1f2937; 
                    border-radius: 12px; 
                    border: 1px solid #374151; 
                }
                #logTitle { 
                    font-size: 18px; 
                    font-weight: 700; 
                    color: #f9fafb; 
                }
                #searchInput { 
                    border: 1px solid #374151; 
                    border-radius: 8px; 
                    padding: 8px 14px; 
                    background: #374151; 
                    color: #f9fafb;
                    font-size: 14px;
                }
                #searchInput:focus {
                    border: 1px solid #3b82f6;
                    background: #4b5563;
                }
                #attendanceTable { 
                    background: transparent; 
                    border: none; 
                    color: #f9fafb;
                    font-size: 14px;
                }
                QHeaderView::section { 
                    background: #374151; 
                    padding: 14px 10px; 
                    border: none; 
                    font-weight: 600; 
                    color: #d1d5db;
                    font-size: 13px;
                }
                #attendanceTable::item {
                    padding: 12px;
                }
                #attendanceTable::item:alternate {
                    background-color: #1f2937;
                }

                #statCard_default { 
                    background-color: #1f2937; 
                    border: 1px solid #374151;
                    border-left: 4px solid #3b82f6;
                }
                #statCard_default #statIcon { 
                    background-color: #374151; 
                    color: #3b82f6; 
                }
                #statCard_default #statTitle { color: #9ca3af; }
                #statCard_default #statValue { color: #f9fafb; }
            """
            self.setStyleSheet(base_style + stat_card_styles)
        else:
            base_style = """
                QWidget { background: #f9fafb; color: #1f2937; }
                #pageSubtitle { color: #6b7280; font-size: 15px; font-weight: 500; }
                #logContainer { 
                    background: #ffffff; 
                    border-radius: 12px; 
                    border: 1px solid #e5e7eb; 
                }
                #logTitle { 
                    font-size: 18px; 
                    font-weight: 700; 
                    color: #1f2937; 
                }
                #searchInput { 
                    border: 1px solid #d1d5db; 
                    border-radius: 8px; 
                    padding: 8px 14px; 
                    background: #f9fafb;
                    font-size: 14px;
                }
                #searchInput:focus {
                    border: 1px solid #3b82f6;
                    background: #ffffff;
                }
                #attendanceTable { 
                    background: transparent; 
                    border: none;
                    font-size: 14px;
                }
                QHeaderView::section { 
                    background: #f3f4f6; 
                    padding: 14px 10px; 
                    border: none; 
                    font-weight: 600; 
                    color: #4b5563;
                    font-size: 13px;
                }
                #attendanceTable::item {
                    padding: 12px;
                }
                #attendanceTable::item:alternate {
                    background-color: #f9fafb;
                }
            """
            self.setStyleSheet(base_style + stat_card_styles)