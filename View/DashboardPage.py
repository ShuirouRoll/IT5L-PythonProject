from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QGroupBox
)


class PieChartWidget(QWidget):
    """Simple pie chart widget for attendance visualization"""

    def __init__(self):
        super().__init__()
        self.setFixedSize(220, 220)
        self.present_count = 0
        self.absent_count = 1
        self.total_count = 1

    def set_data(self, present, absent):
        """Update chart data"""
        self.present_count = present
        self.absent_count = absent
        self.total_count = present + absent

        if self.total_count == 0:
            self.absent_count = 1
            self.total_count = 1

        self.update()

    def paintEvent(self, event):
        """Draw the pie chart"""
        if self.total_count == 0:
            return

        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            margin = 20
            size = min(self.width(), self.height()) - 2 * margin
            chart_rect = QRectF(
                (self.width() - size) / 2,
                (self.height() - size) / 2,
                size,
                size
            )

            # FIX: Convert to int properly to avoid float errors
            present_angle = int((self.present_count / self.total_count) * 360 * 16)
            absent_angle = int((self.absent_count / self.total_count) * 360 * 16)

            # Draw Present slice (green)
            if present_angle > 0:
                painter.setBrush(QColor("#0EA574"))
                painter.setPen(QPen(QColor("#ffffff"), 2))
                painter.drawPie(chart_rect, 90 * 16, -present_angle)

            # Draw Absent slice (red) - FIX: Calculate start angle as int
            if absent_angle > 0:
                painter.setBrush(QColor("#C41230"))
                painter.setPen(QPen(QColor("#ffffff"), 2))
                start_angle = int(90 * 16 - present_angle)  # Convert to int!
                painter.drawPie(chart_rect, start_angle, -absent_angle)

            painter.end()

        except Exception as e:
            print(f"[PieChart] Paint error: {e}")
            import traceback
            traceback.print_exc()


class StatCard(QFrame):
    """Enhanced stat card with color themes"""

    def __init__(self, icon, title, value="0", color_theme="default"):
        super().__init__()
        self.color_theme = color_theme
        self.setObjectName(f"statCard_{color_theme}")
        self.setFixedHeight(85)  # Reduced from 110
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.build(icon, title, value)

    def build(self, icon, title, value):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)  # Reduced padding
        layout.setSpacing(12)

        # Icon container
        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        icon_label.setFixedSize(40, 40)  # Reduced from 48
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

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
        self.value_label.setText(str(value))


class DashboardPage(QWidget):
    def __init__(self, logo_paths):
        super().__init__()
        self.logo_paths = logo_paths
        self.all_records = []
        self.build_ui()

        self.pie_chart.set_data(0, 1)  # Show at least a red circle by default
        self.apply_theme("light")

        # Auto refresh - reduced to 15 seconds for faster updates during testing
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_refresh_trigger)
        self.timer.start(15000)

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(20)

        # Subtitle
        subtitle = QLabel("Today's Attendance Overview")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(subtitle)

        # Main content row (Stats + Chart)
        content_row = QHBoxLayout()
        content_row.setSpacing(20)

        # Left side - Stats cards
        stats_col = QVBoxLayout()
        stats_col.setSpacing(20)

        self.card_total = StatCard("👥", "Total Employees", "0 Employees", color_theme="default")
        self.card_clocked_in = StatCard("✓", "Clocked In", "0 Employees", color_theme="jade")
        self.card_not_clocked_in = StatCard("○", "Not Clocked In", "0 Employees", color_theme="crimson")

        stats_col.addWidget(self.card_total)
        stats_col.addWidget(self.card_clocked_in)
        stats_col.addWidget(self.card_not_clocked_in)
        stats_col.addStretch()

        content_row.addLayout(stats_col, 2)

        # Right side - Pie Chart (smaller container)
        chart_container = QFrame()
        chart_container.setObjectName("chartContainer")
        chart_container.setMaximumWidth(350)  # Limit width
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(20, 20, 20, 20)  # Reduced padding
        chart_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        chart_title = QLabel("Attendance Distribution")
        chart_title.setObjectName("chartTitle")
        chart_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_layout.addWidget(chart_title)

        self.pie_chart = PieChartWidget()
        chart_layout.addWidget(self.pie_chart, alignment=Qt.AlignmentFlag.AlignCenter)

        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(16)  # Reduced spacing
        legend_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        present_legend = QHBoxLayout()
        present_legend.setSpacing(6)
        present_color = QLabel("●")
        present_color.setStyleSheet("color: #0EA574; font-size: 16px;")  # Smaller
        self.present_legend_text = QLabel("Clocked In (0%)")
        self.present_legend_text.setObjectName("legendText")
        present_legend.addWidget(present_color)
        present_legend.addWidget(self.present_legend_text)

        absent_legend = QHBoxLayout()
        absent_legend.setSpacing(6)
        absent_color = QLabel("●")
        absent_color.setStyleSheet("color: #C41230; font-size: 16px;")  # Smaller
        self.absent_legend_text = QLabel("Not Clocked In (100%)")
        self.absent_legend_text.setObjectName("legendText")
        absent_legend.addWidget(absent_color)
        absent_legend.addWidget(self.absent_legend_text)

        legend_layout.addLayout(present_legend)
        legend_layout.addSpacing(12)
        legend_layout.addLayout(absent_legend)

        chart_layout.addLayout(legend_layout)

        content_row.addWidget(chart_container, 1)

        root.addLayout(content_row)

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

    def on_refresh_trigger(self):
        # In a real app, this would trigger controller
        pass

    def update_stats(self, total, clocked_in, not_clocked_in):
        """Update the stat cards with new values"""
        self.card_total.set_value(f"{total} Employees")
        self.card_clocked_in.set_value(f"{clocked_in} Employees")
        self.card_not_clocked_in.set_value(f"{not_clocked_in} Employees")

        # Update pie chart
        print(f"[DEBUG] Updating pie chart: clocked_in={clocked_in}, not_clocked_in={not_clocked_in}")
        self.pie_chart.set_data(clocked_in, not_clocked_in)

        # Update legend percentages
        total_count = clocked_in + not_clocked_in
        if total_count > 0:
            clocked_pct = (clocked_in / total_count) * 100
            not_clocked_pct = (not_clocked_in / total_count) * 100
        else:
            clocked_pct = 0
            not_clocked_pct = 100

        self.present_legend_text.setText(f"Clocked In ({clocked_pct:.0f}%)")
        self.absent_legend_text.setText(f"Not Clocked In ({not_clocked_pct:.0f}%)")

    def populate_attendance_table(self, records):
        """Populate the attendance table with records"""
        self.all_records = records
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
        jade = "#0EA574"
        crimson = "#C41230"

        stat_card_styles = f"""
            /* Default Card */
            #statCard_default {{ 
                background-color: white; 
                border: 1px solid #e5e7eb; 
                border-radius: 12px;
                border-left: 4px solid #3b82f6;
                min-width: 220px;
            }}
            #statCard_default #statIcon {{ 
                background-color: #f3f4f6; 
                color: #3b82f6; 
                border-radius: 20px;
                font-size: 22px;
            }}
            #statCard_default #statTitle {{ 
                color: #6b7280; 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
                border: none;
            }}
            #statCard_default #statValue {{ 
                color: #1f2937; 
                font-size: 20px; 
                font-weight: 700;
                background: transparent;
                border: none;
            }}

            /* Jade Card (Signed In) */
            #statCard_jade {{ 
                background-color: {jade}; 
                border: 1px solid {jade}; 
                border-radius: 12px;
                min-width: 220px;
            }}
            #statCard_jade #statIcon {{ 
                background-color: rgba(255, 255, 255, 0.2); 
                color: #ffffff; 
                border-radius: 20px;
                font-size: 22px;
            }}
            #statCard_jade #statTitle {{ 
                color: rgba(255, 255, 255, 0.9); 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
                border: none;
            }}
            #statCard_jade #statValue {{ 
                color: #ffffff; 
                font-size: 20px; 
                font-weight: 700;
                background: transparent;
                border: none;
            }}

            /* Crimson Card */
            #statCard_crimson {{ 
                background-color: {crimson}; 
                border: 1px solid {crimson}; 
                border-radius: 12px;
                min-width: 220px;
            }}
            #statCard_crimson #statIcon {{ 
                background-color: rgba(255, 255, 255, 0.2); 
                color: #ffffff; 
                border-radius: 20px;
                font-size: 22px;
            }}
            #statCard_crimson #statTitle {{ 
                color: rgba(255, 255, 255, 0.9); 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
                border: none;
            }}
            #statCard_crimson #statValue {{ 
                color: #ffffff; 
                font-size: 20px; 
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """

        if theme == "dark":
            base_style = """
                QWidget { background: #111827; color: #f9fafb; }
                #pageSubtitle { color: #9ca3af; font-size: 15px; font-weight: 500; }
                #chartContainer { 
                    background: #1f2937; 
                    border-radius: 12px; 
                    border: 1px solid #374151; 
                }
                #chartTitle { 
                    font-size: 16px; 
                    font-weight: 700; 
                    color: #f9fafb;
                    margin-bottom: 12px;
                }
                #legendText { 
                    color: #d1d5db; 
                    font-size: 13px; 
                    font-weight: 500;
                }
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
                #chartContainer { 
                    background: #ffffff; 
                    border-radius: 12px; 
                    border: 1px solid #e5e7eb; 
                }
                #chartTitle { 
                    font-size: 16px; 
                    font-weight: 700; 
                    color: #1f2937;
                    margin-bottom: 12px;
                }
                #legendText { 
                    color: #4b5563; 
                    font-size: 13px; 
                    font-weight: 500;
                }
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