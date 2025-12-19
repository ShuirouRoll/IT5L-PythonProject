from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QComboBox
)

from Project.View.Dialogs import CompactMessageDialog, RequestDetailsDialog


class RequestsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cached_requests = []
        self.build_ui()
        # Initial empty state
        self.table.setRowCount(0)

    def showEvent(self, event):
        """Load data when page becomes visible"""
        super().showEvent(event)
        self.load_data()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # Header
        top_row = QHBoxLayout()
        title = QLabel("Leave Requests")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1a1a;")
        top_row.addWidget(title)
        top_row.addStretch()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Pending", "Approved", "Rejected"])
        self.filter_combo.currentTextChanged.connect(self.load_data)
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #1a1a1a;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                min-height: 30px;
            }
        """)
        top_row.addWidget(self.filter_combo)
        layout.addLayout(top_row)

        # Add View Details Button
        view_details_row = QHBoxLayout()
        view_details_row.addStretch()
        self.view_details_btn = QPushButton("View Selected Request Details")
        self.view_details_btn.setFixedHeight(40)
        self.view_details_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        self.view_details_btn.clicked.connect(self.view_selected_details)
        view_details_row.addWidget(self.view_details_btn)
        layout.addLayout(view_details_row)

        # Table - FIXED COLUMN WIDTHS
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Employee Name", "Request Date", "Request Reason", "Dates", "Status", "Action"
        ])

        # Set specific column widths
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 60)  # ID

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name

        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 120)  # Request Date

        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Reason

        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 200)  # Dates

        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 100)  # Status

        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 150)  # Action - INCREASED WIDTH

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setRowHeight(0, 50)  # Set default row height

        self.table.setStyleSheet("""
                    QTableWidget { 
                        background-color: white; 
                        border: 1px solid #e0e0e0; 
                        border-radius: 8px; 
                        font-size: 13px; 
                    }
                    QHeaderView::section { 
                        background-color: #f3f4f6; 
                        padding: 10px; 
                        border: none; 
                        font-weight: bold; 
                        color: #333; 
                    }
                    QTableWidget::item { 
                        padding: 8px;
                        color: #1a1a1a;
                        background-color: white;
                    }
                    QTableWidget::item:selected { 
                        background-color: white; 
                        color: #1a1a1a; 
                    }
                    QTableWidget::item:focus {
                        background-color: white;
                        color: #1a1a1a;
                        outline: none;
                    }
                    QTableWidget::item:hover {
                        background-color: white;
                    }
                """)
        # REMOVED cellDoubleClicked connection - no auto-popup
        layout.addWidget(self.table)

    def load_data(self):
        """Load requests data"""
        print("[RequestsPage] load_data() called")

        try:
            from Project.Controller.RequestC import LeaveRequestController
        except ImportError as e:
            print(f"[RequestsPage] Error: Could not import RequestC: {e}")
            self.table.setRowCount(0)
            return

        status_filter = self.filter_combo.currentText()
        if status_filter == "All":
            status_filter = None

        try:
            print(f"[RequestsPage] Fetching requests with filter: {status_filter}")
            self.cached_requests = LeaveRequestController.get_all_requests(status_filter)
            print(f"[RequestsPage] Fetched {len(self.cached_requests)} requests")
        except Exception as e:
            print(f"[RequestsPage] Error loading data: {e}")
            import traceback
            traceback.print_exc()
            self.cached_requests = []

        # Clear table
        self.table.setRowCount(0)

        # If no requests, show empty state
        if not self.cached_requests:
            print("[RequestsPage] No requests to display")
            return

        for i, req in enumerate(self.cached_requests):
            self.table.insertRow(i)
            self.table.setRowHeight(i, 50)  # Set row height for each row

            def item(text, align_center=True):
                it = QTableWidgetItem(str(text))
                if align_center:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                return it

            self.table.setItem(i, 0, item(req['id']))
            self.table.setItem(i, 1, item(req['employee_name'], align_center=False))

            created = req['created_at']
            date_str = created.strftime("%Y-%m-%d") if created else "N/A"
            self.table.setItem(i, 2, item(date_str))

            self.table.setItem(i, 3, item(req['leave_type'], align_center=False))
            self.table.setItem(i, 4, item(f"{req['start_date']} - {req['end_date']}"))

            status_item = item(req['status'])
            if req['status'] == 'Approved':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif req['status'] == 'Rejected':
                status_item.setForeground(Qt.GlobalColor.red)
            elif req['status'] == 'Pending':
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            self.table.setItem(i, 5, status_item)

            # FIXED: Better button layout with proper styling
            if req['status'] == 'Pending':
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(8, 6, 8, 6)  # Better margins
                btn_layout.setSpacing(8)  # More spacing
                btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                approve_btn = QPushButton("✓ Approve")
                approve_btn.setFixedSize(65, 35)  # Bigger buttons
                approve_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #10B981; 
                        color: white; 
                        border-radius: 6px; 
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #059669;
                    }
                """)
                approve_btn.clicked.connect(lambda checked, rid=req['id']: self.process_request(rid, 'Approved'))

                reject_btn = QPushButton("✗ Reject")
                reject_btn.setFixedSize(65, 35)  # Bigger buttons
                reject_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #EF4444; 
                        color: white; 
                        border-radius: 6px; 
                        font-weight: bold;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #DC2626;
                    }
                """)
                reject_btn.clicked.connect(lambda checked, rid=req['id']: self.process_request(rid, 'Rejected'))

                btn_layout.addWidget(approve_btn)
                btn_layout.addWidget(reject_btn)
                self.table.setCellWidget(i, 6, btn_widget)
            else:
                self.table.setItem(i, 6, item("-"))

    def view_selected_details(self):
        """View details of the selected request"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            CompactMessageDialog.show_warning(self, "No Selection", "Please select a request to view details.")
            return

        row = self.table.currentRow()
        if 0 <= row < len(self.cached_requests):
            req_data = self.cached_requests[row]
            dialog = RequestDetailsDialog(req_data, self)
            dialog.exec()

    def process_request(self, request_id, status):
        from Project.Controller.RequestC import LeaveRequestController

        if LeaveRequestController.update_status(request_id, status):
            CompactMessageDialog.show_success(self, "Success", f"Request {status}!")
            self.load_data()
        else:
            CompactMessageDialog.show_warning(self, "Error", "Failed to update status.")

    def apply_theme(self, theme):
        pass