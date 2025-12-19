from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget
)


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.on_report_clicked = None

        # Data storage for sorting
        self.daily_data = []
        self.data_15day = []
        self.data_monthly = []

        self.build_ui()
        self.apply_theme("light")

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(20)

        # Title
        title = QLabel("Attendance Reports")
        title.setObjectName("pageSubtitle")
        layout.addWidget(title)

        # Header Row (Sort)
        header_row = QHBoxLayout()
        header_row.addStretch()

        sort_label = QLabel("Sort by:")
        sort_label.setObjectName("sortLabel")
        header_row.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.setObjectName("sortCombo")
        self.sort_combo.setFixedWidth(180)
        self.sort_combo.setFixedHeight(35)
        # Added "Late (Most)" as requested
        self.sort_combo.addItems([
            "Date (Newest)",
            "Date (Oldest)",
            "Present (Most)",
            "Absent (Most)",
            "Late (Most)"
        ])
        self.sort_combo.currentTextChanged.connect(self.sort_reports)
        header_row.addWidget(self.sort_combo)

        layout.addLayout(header_row)

        # Tabs
        self.tabs = QTabWidget()

        # 1. Daily
        self.tab_daily = QWidget()
        l_daily = QVBoxLayout(self.tab_daily)
        l_daily.setContentsMargins(0, 15, 0, 0)
        self.table_daily = self.create_table(["Date", "Present", "Late", "Absent"])
        self.table_daily.cellClicked.connect(lambda r, c: self.handle_click('daily', r))
        l_daily.addWidget(self.table_daily)
        self.tabs.addTab(self.tab_daily, "Daily Reports")

        # 2. 15-Day
        self.tab_15day = QWidget()
        l_15 = QVBoxLayout(self.tab_15day)
        l_15.setContentsMargins(0, 15, 0, 0)
        self.table_15day = self.create_table(["Period", "Work Days", "Present", "Late", "Absent"])
        self.table_15day.cellClicked.connect(lambda r, c: self.handle_click('15day', r))
        l_15.addWidget(self.table_15day)
        self.tabs.addTab(self.tab_15day, "15-Day Reports")

        # 3. Monthly
        self.tab_monthly = QWidget()
        l_month = QVBoxLayout(self.tab_monthly)
        l_month.setContentsMargins(0, 15, 0, 0)
        self.table_monthly = self.create_table(["Month", "Work Days", "Present", "Late", "Absent"])
        self.table_monthly.cellClicked.connect(lambda r, c: self.handle_click('monthly', r))
        l_month.addWidget(self.table_monthly)
        self.tabs.addTab(self.tab_monthly, "Monthly Reports")

        layout.addWidget(self.tabs)

        # Re-sort when switching tabs
        self.tabs.currentChanged.connect(lambda: self.sort_reports(self.sort_combo.currentText()))

    def create_table(self, headers):
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t.verticalHeader().setVisible(False)
        t.setShowGrid(False)
        t.setAlternatingRowColors(True)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        return t

    # === LOGIC & SORTING ===

    def sort_reports(self, criteria):
        """Sorts the currently visible table data"""
        tab_index = self.tabs.currentIndex()

        # Determine sort order (Descending for 'Newest' or 'Most')
        reverse = "Newest" in criteria or "Most" in criteria

        # 1. DAILY REPORTS SORTING
        if tab_index == 0 and self.daily_data:
            key = 'date'
            if "Present" in criteria:
                key = 'total_present_employees'
            elif "Absent" in criteria:
                key = 'total_absent_employees'
            elif "Late" in criteria:
                key = 'total_late_employees'

            self.daily_data.sort(key=lambda x: x.get(key, 0), reverse=reverse)
            self.render_daily()

        # 2. 15-DAY REPORTS SORTING
        elif tab_index == 1 and self.data_15day:
            key = 'period_start'
            if "Present" in criteria:
                key = 'total_present'
            elif "Absent" in criteria:
                key = 'total_absent'
            elif "Late" in criteria:
                key = 'total_late'

            self.data_15day.sort(key=lambda x: x.get(key, 0), reverse=reverse)
            self.render_15day()

        # 3. MONTHLY REPORTS SORTING
        elif tab_index == 2 and self.data_monthly:
            key = 'period_start'  # 'period_start' exists in monthly reports too
            if "Present" in criteria:
                key = 'total_present'
            elif "Absent" in criteria:
                key = 'total_absent'
            elif "Late" in criteria:
                key = 'total_late'

            self.data_monthly.sort(key=lambda x: x.get(key, 0), reverse=reverse)
            self.render_monthly()

    # === POPULATION METHODS (Called by Controller) ===

    def populate_table(self, reports):
        """Load Daily Reports"""
        self.daily_data = reports
        self.sort_reports(self.sort_combo.currentText())  # Sort and Render

    def populate_15day(self, reports):
        """Load 15-Day Reports"""
        self.data_15day = reports
        self.sort_reports(self.sort_combo.currentText())

    def populate_monthly(self, reports):
        """Load Monthly Reports"""
        self.data_monthly = reports
        self.sort_reports(self.sort_combo.currentText())

    # === RENDERING METHODS (Internal) ===

    def render_daily(self):
        self.table_daily.setRowCount(0)
        for i, r in enumerate(self.daily_data):
            self.table_daily.insertRow(i)

            date_val = r.get('date')
            d_str = date_val.strftime("%Y-%m-%d") if date_val else "-"

            item = QTableWidgetItem(d_str)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, date_val)

            self.table_daily.setItem(i, 0, item)
            self.table_daily.setItem(i, 1, self.c_item(r.get('total_present_employees', 0)))
            self.table_daily.setItem(i, 2, self.c_item(r.get('total_late_employees', 0)))
            self.table_daily.setItem(i, 3, self.c_item(r.get('total_absent_employees', 0)))

    def render_15day(self):
        self.table_15day.setRowCount(0)
        for i, r in enumerate(self.data_15day):
            self.table_15day.insertRow(i)
            period = f"{r['period_start']} to {r['period_end']}"

            item = QTableWidgetItem(period)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, {'start': r['period_start'], 'end': r['period_end']})

            self.table_15day.setItem(i, 0, item)
            self.table_15day.setItem(i, 1, self.c_item(r.get('total_work_days', 0)))
            self.table_15day.setItem(i, 2, self.c_item(r.get('total_present', 0)))
            self.table_15day.setItem(i, 3, self.c_item(r.get('total_late', 0)))
            self.table_15day.setItem(i, 4, self.c_item(r.get('total_absent', 0)))

    def render_monthly(self):
        self.table_monthly.setRowCount(0)
        for i, r in enumerate(self.data_monthly):
            self.table_monthly.insertRow(i)
            import calendar
            m_name = calendar.month_name[r['month']]
            period = f"{m_name} {r['year']}"

            item = QTableWidgetItem(period)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, {'year': r['year'], 'month': r['month']})

            self.table_monthly.setItem(i, 0, item)
            self.table_monthly.setItem(i, 1, self.c_item(r.get('total_work_days', 0)))
            self.table_monthly.setItem(i, 2, self.c_item(r.get('total_present', 0)))
            self.table_monthly.setItem(i, 3, self.c_item(r.get('total_late', 0)))
            self.table_monthly.setItem(i, 4, self.c_item(r.get('total_absent', 0)))

    # === HELPERS ===

    def c_item(self, text):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def handle_click(self, type, row):
        if not self.on_report_clicked: return
        data = None

        if type == 'daily':
            item = self.table_daily.item(row, 0)
            data = item.data(Qt.ItemDataRole.UserRole)
        elif type == '15day':
            item = self.table_15day.item(row, 0)
            data = item.data(Qt.ItemDataRole.UserRole)
        elif type == 'monthly':
            item = self.table_monthly.item(row, 0)
            data = item.data(Qt.ItemDataRole.UserRole)

        if data:
            self.on_report_clicked(type, data)

    def apply_theme(self, theme):
        """Applies theme (Ensuring tables are white/clean)"""
        if theme == "dark":
            self.setStyleSheet("""
                QWidget { background: #111827; color: white; }
                #pageSubtitle { color: #9ca3af; font-size: 16px; font-weight: bold; }
                #sortLabel { color: #9ca3af; font-size: 14px; }
                QComboBox { background: #1f2937; color: white; border: 1px solid #374151; padding: 5px; }

                QTabWidget::pane { border: 1px solid #374151; background: #1f2937; border-radius: 6px; }
                QTabBar::tab { background: #374151; color: #d1d5db; padding: 10px 20px; }
                QTabBar::tab:selected { background: #2563eb; color: white; }

                QTableWidget { background-color: #1f2937; color: white; border: none; }
                QHeaderView::section { background: #374151; color: #d1d5db; padding: 8px; border: none; }
                QTableWidget::item { border-bottom: 1px solid #374151; }
            """)
        else:
            # FORCE WHITE THEME
            self.setStyleSheet("""
                QWidget { background: #f9fafb; color: #1f2937; }
                #pageSubtitle { color: #4b5563; font-size: 16px; font-weight: bold; }
                #sortLabel { color: #4b5563; font-size: 14px; }
                QComboBox { background: white; color: #333; border: 1px solid #d1d5db; padding: 5px; }

                QTabWidget::pane { 
                    border: 1px solid #e5e7eb; 
                    background: #ffffff; 
                    border-radius: 8px; 
                }
                QTabBar::tab { 
                    background: #e5e7eb; 
                    color: #4b5563; 
                    padding: 8px 20px; 
                    margin-right: 4px;
                    border-top-left-radius: 6px; 
                    border-top-right-radius: 6px; 
                    font-weight: 600;
                }
                QTabBar::tab:selected { 
                    background: #ffffff; 
                    color: #2563eb; 
                    border-bottom: 2px solid #2563eb; 
                }

                /* TABLE STYLING - Force White */
                QTableWidget { 
                    background-color: #ffffff !important; 
                    color: #1a1a1a !important; 
                    border: none; 
                    gridline-color: #f3f4f6;
                }
                QHeaderView::section { 
                    background: #f3f4f6 !important; 
                    color: #4b5563 !important; 
                    padding: 10px; 
                    border: none; 
                    font-weight: 600; 
                }
                QTableWidget::item { 
                    padding: 10px; 
                    border-bottom: 1px solid #f3f4f6; 
                    color: #1a1a1a !important;
                }
                QTableWidget::item:alternate { 
                    background-color: #f9fafb !important; 
                }
                QTableWidget::item:selected {
                    background-color: #e3f2fd !important;
                    color: #1a1a1a !important;
                }
            """)