from PyQt6.QtCore import Qt, QTime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTimeEdit, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QScrollArea, QAbstractItemView
)

from Project.View.Dialogs import CompactMessageDialog


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.logo_paths = None
        self.build_ui()

    def set_logo_paths(self, paths):
        """Store logo paths for theme switching"""
        self.logo_paths = paths

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(25)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- 1. SETTINGS CARD (Theme & Security) ---
        self.setup_general_card()

        # --- 2. ATTENDANCE CONFIGURATION CARD ---
        self.setup_attendance_card()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        self.load_positions()
        self.load_cutoff_time()

    def create_card_frame(self, title):
        card = QFrame()
        card.setObjectName("SettingsCard")
        card.setStyleSheet("""
            #SettingsCard {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(20)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a1a1a; margin-bottom: 5px;")
        card_layout.addWidget(lbl_title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #f0f0f0;")
        card_layout.addWidget(line)

        return card, card_layout

    def setup_general_card(self):
        card, layout = self.create_card_frame("Settings")

        # --- APPEARANCE ---
        lbl_theme = QLabel("Appearance")
        lbl_theme.setStyleSheet("font-size: 14px; font-weight: 600; color: #333;")
        layout.addWidget(lbl_theme)

        # FIXED: Re-added theme_combo so Main.py doesn't crash
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setFixedWidth(200)
        self.theme_combo.setFixedHeight(35)
        self.theme_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 5px;
                color: #333;
                background-color: white;
            }
        """)
        layout.addWidget(self.theme_combo)

        layout.addSpacing(10)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #f0f0f0;")
        layout.addWidget(line)
        layout.addSpacing(10)

        # --- SECURITY ---
        lbl_sec_title = QLabel("Security")
        lbl_sec_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #333;")
        layout.addWidget(lbl_sec_title)

        lbl_sec_desc = QLabel("Manage your admin username and password.")
        lbl_sec_desc.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 5px;")
        layout.addWidget(lbl_sec_desc)

        self.change_credentials_btn = QPushButton("Change Username & Password")
        self.change_credentials_btn.setFixedSize(250, 40)
        self.change_credentials_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_credentials_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-weight: 600;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        layout.addWidget(self.change_credentials_btn)

        self.content_layout.addWidget(card)

    def setup_attendance_card(self):
        card, layout = self.create_card_frame("Attendance Configuration")

        # -- CUTOFF TIME --
        lbl_cutoff = QLabel("Daily Absence Cutoff")
        lbl_cutoff.setStyleSheet("font-size: 14px; font-weight: 600; color: #333;")

        desc_cutoff = QLabel("Employees who haven't clocked in by this time will be marked Absent.")
        desc_cutoff.setStyleSheet("font-size: 12px; color: #666;")

        row_cutoff = QHBoxLayout()
        row_cutoff.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.cutoff_time_edit = QTimeEdit()
        self.cutoff_time_edit.setDisplayFormat("hh:mm AP")
        self.cutoff_time_edit.setFixedWidth(150)
        self.cutoff_time_edit.setFixedHeight(35)
        self.cutoff_time_edit.setStyleSheet("""
            QTimeEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 5px;
                color: #333;
                background-color: white;
            }
        """)

        self.save_cutoff_btn = QPushButton("Save Cutoff")
        self.save_cutoff_btn.setFixedSize(120, 35)
        self.save_cutoff_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_cutoff_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-weight: 600;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        # Connect internally to handle saving & popup
        self.save_cutoff_btn.clicked.connect(self.save_cutoff_setting)

        row_cutoff.addWidget(self.cutoff_time_edit)
        row_cutoff.addWidget(self.save_cutoff_btn)

        layout.addWidget(lbl_cutoff)
        layout.addWidget(desc_cutoff)
        layout.addLayout(row_cutoff)

        layout.addSpacing(20)

        # -- POSITIONS TABLE --
        lbl_pos = QLabel("Position Late Settings")
        lbl_pos.setStyleSheet("font-size: 14px; font-weight: 600; color: #333;")
        desc_pos = QLabel("Configure standard late times and grace periods for each job position.")
        desc_pos.setStyleSheet("font-size: 12px; color: #666;")

        self.position_table = QTableWidget()
        self.position_table.setColumnCount(4)
        self.position_table.setHorizontalHeaderLabels(["Position Name", "Late Time", "Grace (min)", "Action"])
        self.position_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.position_table.verticalHeader().setVisible(False)
        self.table_style()
        self.position_table.setMinimumHeight(250)
        self.position_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.position_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addWidget(lbl_pos)
        layout.addWidget(desc_pos)
        layout.addWidget(self.position_table)

        self.content_layout.addWidget(card)
        self.content_layout.addStretch()

    def table_style(self):
        self.position_table.setShowGrid(False)
        self.position_table.setAlternatingRowColors(True)
        self.position_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 13px;
                color: #333;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: 600;
                color: #555;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:alternate {
                background-color: #faf5ff;
            }
        """)

    def load_cutoff_time(self):
        try:
            from Project.Controller.AttendanceC import AttendanceController
            cutoff = AttendanceController.get_cutoff_time()
            self.set_cutoff_time(cutoff.hour, cutoff.minute)
        except Exception as e:
            print(f"Error loading cutoff: {e}")

    def save_cutoff_setting(self):
        """Save cutoff time and show popup"""
        try:
            from Project.Controller.AttendanceC import AttendanceController
            h, m = self.get_cutoff_time()
            AttendanceController.set_cutoff_time(h, m)
            # SUCCESS POPUP
            CompactMessageDialog.show_success(self, "Success", f"Absence cutoff set to {h:02d}:{m:02d}")
        except Exception as e:
            CompactMessageDialog.show_warning(self, "Error", str(e))

    def load_positions(self):
        try:
            from Project.Controller.PositionC import PositionController
            positions = PositionController.get_all_positions()
            self.position_table.setRowCount(0)

            for i, pos in enumerate(positions):
                self.position_table.insertRow(i)

                name_item = QTableWidgetItem(pos['name'])
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.position_table.setItem(i, 0, name_item)

                time_edit = QTimeEdit()
                time_edit.setDisplayFormat("hh:mm AP")

                lt = pos.get('late_time')
                if hasattr(lt, 'total_seconds'):
                    s = int(lt.total_seconds())
                    time_edit.setTime(QTime(s // 3600, (s % 3600) // 60))
                elif hasattr(lt, 'hour'):
                    time_edit.setTime(QTime(lt.hour, lt.minute))
                else:
                    time_edit.setTime(QTime(8, 0))

                time_edit.setStyleSheet(
                    "border: 1px solid #d1d5db; border-radius: 4px; background: white; color: #333;")
                self.position_table.setCellWidget(i, 1, time_edit)

                spin = QSpinBox()
                spin.setRange(0, 60)
                spin.setValue(pos.get('grace_period_minutes', 15))
                spin.setStyleSheet("border: 1px solid #d1d5db; border-radius: 4px; background: white; color: #333;")
                self.position_table.setCellWidget(i, 2, spin)

                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                update_btn = QPushButton("Update")
                update_btn.setFixedSize(70, 28)
                update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                update_btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #3B82F6; color: white; 
                        border-radius: 4px; font-weight: 600; font-size: 12px; border: none;
                    }
                    QPushButton:hover { background-color: #2563EB; }
                """)
                update_btn.clicked.connect(lambda checked, r=i, pid=pos['id']: self.update_position_settings(r, pid))

                btn_layout.addWidget(update_btn)
                self.position_table.setCellWidget(i, 3, btn_widget)

        except Exception as e:
            print(f"[Settings] Load Error: {e}")

    def update_position_settings(self, row, pid):
        """Update position settings and show popup"""
        try:
            from Project.Controller.PositionC import PositionController
            t_widget = self.position_table.cellWidget(row, 1)
            g_widget = self.position_table.cellWidget(row, 2)

            t = t_widget.time().toString("HH:mm:ss")
            g = g_widget.value()

            success, msg = PositionController.update_position(pid, late_time=t, grace_period=g)

            if success:
                # SUCCESS POPUP
                CompactMessageDialog.show_success(self, "Success", "Position settings updated successfully!")
            else:
                CompactMessageDialog.show_warning(self, "Error", msg)
        except Exception as e:
            CompactMessageDialog.show_warning(self, "Error", str(e))

    def get_cutoff_time(self):
        t = self.cutoff_time_edit.time()
        return t.hour(), t.minute()

    def set_cutoff_time(self, h, m):
        self.cutoff_time_edit.setTime(QTime(h, m))

    def apply_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet("background-color: #1a1a1a; color: white;")
        else:
            self.setStyleSheet("background-color: #f5f5f5; color: #1a1a1a;")