from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QFileDialog)
from PyQt6.QtCore import Qt, QMarginsF, QSizeF, QPointF, QRectF
from PyQt6.QtGui import (QTextDocument, QPageSize, QPageLayout, QPainter,
                         QPen, QColor, QPixmap, QFont, QBrush)
from PyQt6.QtPrintSupport import QPrinter
from datetime import datetime, timedelta, date
from Project.Model.Database import Database
import os
import calendar


class ReportDetails(QDialog):
    """Details for a Single Day (Present/Late/Absent lists)"""

    COLOR_PRESENT = "#0EA574"
    COLOR_LATE = "#D97706"
    COLOR_ABSENT = "#C41230"

    def __init__(self, report_date, report_data, parent=None):
        super().__init__(parent)
        self.report_date = report_date
        self.report_data = report_data
        self.setWindowTitle(f"Daily Report - {report_date}")
        self.setFixedSize(1000, 750)
        self.setStyleSheet("QDialog { background-color: #f9fafb; } QLabel { color: #1f2937; }")
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel(f"Attendance Report - {self.report_date}")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #111827;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Statistics
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        present_count = len(self.report_data['present'])
        late_count = len(self.report_data['late'])
        absent_count = len(self.report_data['absent'])
        total_count = present_count + late_count + absent_count

        p_pct = (present_count / total_count * 100) if total_count > 0 else 0
        l_pct = (late_count / total_count * 100) if total_count > 0 else 0
        a_pct = (absent_count / total_count * 100) if total_count > 0 else 0

        stats_layout.addWidget(
            self.create_stat_card("Present", str(present_count), f"{p_pct:.1f}%", self.COLOR_PRESENT))
        stats_layout.addWidget(self.create_stat_card("Late", str(late_count), f"{l_pct:.1f}%", self.COLOR_LATE))
        stats_layout.addWidget(self.create_stat_card("Absent", str(absent_count), f"{a_pct:.1f}%", self.COLOR_ABSENT))
        layout.addLayout(stats_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #e5e7eb;")
        layout.addWidget(line)

        # Tabs
        self.tab_layout = QHBoxLayout()
        self.tab_layout.setSpacing(12)
        self.present_tab = self.create_tab_button("Present", self.COLOR_PRESENT, False)
        self.late_tab = self.create_tab_button("Late", self.COLOR_LATE, False)
        self.absent_tab = self.create_tab_button("Absent", self.COLOR_ABSENT, False)

        self.tab_layout.addWidget(self.present_tab)
        self.tab_layout.addWidget(self.late_tab)
        self.tab_layout.addWidget(self.absent_tab)
        self.tab_layout.addStretch()
        layout.addLayout(self.tab_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Position", "Email", "Phone", "Time In", "Time Out"])
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #d1d5db; border-radius: 8px; font-size: 13px; gridline-color: #f3f4f6; }
            QHeaderView::section { background-color: #f3f4f6; padding: 12px; border: none; font-weight: bold; color: #374151; border-bottom: 1px solid #d1d5db; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f3f4f6; color: #4b5563; }
            QTableWidget::item:selected { background-color: #e5e7eb; color: #1f2937; }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Footer
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        pdf_btn = QPushButton("Export PDF")
        pdf_btn.setFixedSize(140, 45)
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.setStyleSheet(
            "QPushButton { background-color: #1f2937; color: white; border-radius: 8px; font-weight: 600; font-size: 14px; }")
        pdf_btn.clicked.connect(self.export_to_pdf_simple)

        close_btn = QPushButton("Close")
        close_btn.setFixedSize(110, 45)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(
            "QPushButton { background-color: #f3f4f6; color: #4b5563; border: 1px solid #d1d5db; border-radius: 8px; font-weight: 600; font-size: 14px; }")

        button_layout.addWidget(pdf_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        if present_count > 0:
            self.switch_tab("Present")
        elif late_count > 0:
            self.switch_tab("Late")
        elif absent_count > 0:
            self.switch_tab("Absent")
        else:
            self.switch_tab("Present")

    def create_stat_card(self, title, count, percentage, color):
        card = QFrame()
        card.setFixedSize(180, 110)
        card.setStyleSheet(f"background-color: {color}; border-radius: 12px;")
        l = QVBoxLayout(card)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_t = QLabel(title.upper());
        lbl_t.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 11px; font-weight: bold;")
        lbl_c = QLabel(count);
        lbl_c.setStyleSheet("color: white; font-size: 36px; font-weight: 800;")
        lbl_p = QLabel(percentage);
        lbl_p.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 500;")
        l.addWidget(lbl_t);
        l.addWidget(lbl_c);
        l.addWidget(lbl_p)
        return card

    def create_tab_button(self, text, color, is_active):
        btn = QPushButton(text)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        base = "border-radius: 6px; font-weight: 600; font-size: 13px; padding: 0 25px;"
        if is_active:
            btn.setStyleSheet(f"background-color: {color}; color: white; border: none; {base}")
        else:
            btn.setStyleSheet(f"background-color: #f3f4f6; color: #6b7280; border: 1px solid #d1d5db; {base}")
        btn.clicked.connect(lambda: self.switch_tab(text))
        return btn

    def switch_tab(self, name):
        inact = "background-color: #f3f4f6; color: #6b7280; border: 1px solid #d1d5db; border-radius: 6px; font-weight: 600; font-size: 13px; padding: 0 25px;"
        self.present_tab.setStyleSheet(inact);
        self.late_tab.setStyleSheet(inact);
        self.absent_tab.setStyleSheet(inact)
        colors = {"Present": self.COLOR_PRESENT, "Late": self.COLOR_LATE, "Absent": self.COLOR_ABSENT}
        act = f"background-color: {colors[name]}; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 13px; padding: 0 25px;"
        if name == "Present":
            self.present_tab.setStyleSheet(act); self.show_present_data()
        elif name == "Late":
            self.late_tab.setStyleSheet(act); self.show_late_data()
        elif name == "Absent":
            self.absent_tab.setStyleSheet(act); self.show_absent_data()

    def populate_table(self, data):
        self.table.setRowCount(0)
        for i, emp in enumerate(data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(emp.get('employee_id', ''))))
            self.table.setItem(i, 1, QTableWidgetItem(str(emp.get('full_name', ''))))
            self.table.setItem(i, 2, QTableWidgetItem(str(emp.get('position', ''))))
            self.table.setItem(i, 3, QTableWidgetItem(str(emp.get('email', ''))))
            self.table.setItem(i, 4, QTableWidgetItem(str(emp.get('phone', ''))))
            self.table.setItem(i, 5, QTableWidgetItem(str(emp.get('clock_in', '-'))))
            self.table.setItem(i, 6, QTableWidgetItem(str(emp.get('clock_out', '-'))))

    def show_present_data(self):
        self.populate_table(self.report_data['present'])

    def show_late_data(self):
        self.populate_table(self.report_data['late'])

    def show_absent_data(self):
        self.populate_table(self.report_data['absent'])

    def export_to_pdf_simple(self):
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

            fname = f"Daily_Report_{self.report_date}.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "Save PDF",
                                                  os.path.join(os.path.expanduser("~"), "Desktop", fname),
                                                  "PDF (*.pdf)")
            if not path: return
            printer.setOutputFileName(path)

            p = len(self.report_data['present']);
            l = len(self.report_data['late']);
            a = len(self.report_data['absent'])
            t = p + l + a

            html = f"""
            <html><body style="font-family: Arial; font-size: 11pt; color: #333;">
                <h1 style="font-size: 22pt; font-weight: bold; margin-bottom: 10pt;">Daily Report - {self.report_date}</h1>
                <p style="font-size: 12pt; color: #666; margin-bottom: 20pt;">Total Employees: {t}</p>
                <table width="100%" cellspacing="0" cellpadding="8" style="border: 1px solid #ddd; border-collapse: collapse; margin-bottom: 20pt;">
                    <tr style="background-color: #f3f4f6; color: #333;">
                        <th style="font-size: 11pt; border: 1px solid #ddd;">Metric</th>
                        <th style="font-size: 11pt; border: 1px solid #ddd;">Count</th>
                        <th style="font-size: 11pt; border: 1px solid #ddd;">Percentage</th>
                    </tr>
                    <tr><td style="border: 1px solid #ddd;">Present</td><td style="border: 1px solid #ddd;">{p}</td><td style="border: 1px solid #ddd;">{(p / t * 100 if t else 0):.1f}%</td></tr>
                    <tr><td style="border: 1px solid #ddd;">Late</td><td style="border: 1px solid #ddd;">{l}</td><td style="border: 1px solid #ddd;">{(l / t * 100 if t else 0):.1f}%</td></tr>
                    <tr><td style="border: 1px solid #ddd;">Absent</td><td style="border: 1px solid #ddd;">{a}</td><td style="border: 1px solid #ddd;">{(a / t * 100 if t else 0):.1f}%</td></tr>
                </table>
                <h3 style="font-size: 14pt; margin-top: 15pt; color: {self.COLOR_PRESENT};">Present Employees</h3>
                {self.create_pdf_table(self.report_data['present'])}
                <h3 style="font-size: 14pt; margin-top: 15pt; color: {self.COLOR_LATE};">Late Employees</h3>
                {self.create_pdf_table(self.report_data['late'])}
                <h3 style="font-size: 14pt; margin-top: 15pt; color: {self.COLOR_ABSENT};">Absent Employees</h3>
                {self.create_pdf_table(self.report_data['absent'])}
                <div style="margin-top: 30pt; font-size: 9pt; color: #999; border-top: 1px solid #eee; padding-top: 10pt;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            </body></html>"""
            doc = QTextDocument();
            doc.setHtml(html);
            doc.print(printer)
            from Project.View.Dialogs import CompactMessageDialog
            CompactMessageDialog.show_success(self, "Success", "PDF Exported!")
        except Exception as e:
            print(e)

    def create_pdf_table(self, data):
        if not data: return "<p style='font-style: italic; color: #666;'>No records found.</p>"
        html = '<table width="100%" cellspacing="0" cellpadding="5" style="border-collapse: collapse; font-size: 10pt;">'
        html += '<tr style="background-color: #f3f4f6;">'
        html += '<th align="left" style="border-bottom: 1px solid #ddd;">ID</th><th align="left" style="border-bottom: 1px solid #ddd;">Name</th><th align="left" style="border-bottom: 1px solid #ddd;">Position</th><th align="left" style="border-bottom: 1px solid #ddd;">Time In</th><th align="left" style="border-bottom: 1px solid #ddd;">Time Out</th></tr>'
        for i, emp in enumerate(data):
            bg = "#ffffff" if i % 2 == 0 else "#fafafa"
            html += f'<tr style="background-color: {bg};"><td style="border-bottom: 1px solid #eee;">{emp.get("employee_id")}</td><td style="border-bottom: 1px solid #eee;">{emp.get("full_name")}</td><td style="border-bottom: 1px solid #eee;">{emp.get("position")}</td><td style="border-bottom: 1px solid #eee;">{emp.get("clock_in", "-")}</td><td style="border-bottom: 1px solid #eee;">{emp.get("clock_out", "-")}</td></tr>'
        return html + '</table>'


# === PERIODIC REPORT DETAILS (15-Day & Monthly) ===
class PeriodicReportDetails(QDialog):
    """Details for Aggregated Reports with Graph"""

    def __init__(self, title, employee_data, parent=None):
        super().__init__(parent)
        self.title = title
        self.data = employee_data
        self.setWindowTitle(title)
        self.setFixedSize(1000, 750)
        self.setStyleSheet("QDialog { background-color: #f9fafb; } QLabel { color: #1f2937; }")
        self.top_employee = self.data[0] if self.data else None
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel(self.title)
        header.setStyleSheet("font-size: 24px; font-weight: 800; color: #111827;")
        layout.addWidget(header)

        if self.top_employee:
            top_frame = QFrame()
            top_frame.setFixedHeight(120)
            top_frame.setStyleSheet("""
                QFrame { background-color: white; border: 1px solid #e5e7eb; border-radius: 12px; border-left: 6px solid #F59E0B; }
            """)
            top_layout = QHBoxLayout(top_frame)
            top_layout.setContentsMargins(20, 15, 20, 15)

            info_l = QVBoxLayout();
            info_l.setSpacing(2)
            lbl = QLabel("🏆 TOP PERFORMER");
            lbl.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
            name = QLabel(self.top_employee.get('full_name', 'Unknown'));
            name.setStyleSheet("font-size: 24px; font-weight: bold; color: #111827; border: none;")
            pos = QLabel(self.top_employee.get('position', 'Staff'));
            pos.setStyleSheet("color: #6b7280; font-size: 14px; border: none;")
            info_l.addWidget(lbl);
            info_l.addWidget(name);
            info_l.addWidget(pos)

            stats_l = QVBoxLayout()
            rate = float(self.top_employee.get('attendance_rate', 0))
            hours = float(self.top_employee.get('total_hours_worked', 0))
            r_lbl = QLabel(f"{rate:.1f}% Attendance");
            r_lbl.setStyleSheet("color: #059669; font-weight: bold; font-size: 20px; border: none;")
            h_lbl = QLabel(f"{hours:.1f} Total Hours");
            h_lbl.setStyleSheet("border: none; color: #4b5563;")
            stats_l.addWidget(r_lbl, 0, Qt.AlignmentFlag.AlignRight);
            stats_l.addWidget(h_lbl, 0, Qt.AlignmentFlag.AlignRight)
            top_layout.addLayout(info_l);
            top_layout.addStretch();
            top_layout.addLayout(stats_l)
            layout.addWidget(top_frame)

        self.table = QTableWidget()
        cols = ["Name", "Position", "Present", "Late", "Absent", "Total Hours", "Rate %"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #d1d5db; border-radius: 8px; font-size: 13px; }
            QHeaderView::section { background-color: #f3f4f6; padding: 12px; border: none; font-weight: bold; color: #374151; border-bottom: 1px solid #d1d5db; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f3f4f6; color: #374151; }
        """)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.populate_table()
        layout.addWidget(self.table)

        btn_row = QHBoxLayout();
        btn_row.addStretch()
        pdf_btn = QPushButton("Export PDF")
        pdf_btn.setFixedSize(140, 45)
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.setStyleSheet(
            "QPushButton { background-color: #1f2937; color: white; border-radius: 8px; font-weight: 600; font-size: 14px; }")
        pdf_btn.clicked.connect(self.export_pdf)
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(110, 45)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(
            "QPushButton { background-color: #f3f4f6; color: #4b5563; border: 1px solid #d1d5db; border-radius: 8px; font-weight: 600; font-size: 14px; }")
        btn_row.addWidget(pdf_btn);
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def populate_table(self):
        self.table.setRowCount(len(self.data))
        for i, emp in enumerate(self.data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(emp.get('full_name')))
            self.table.setItem(i, 1, QTableWidgetItem(emp.get('position')))

            def c(val): it = QTableWidgetItem(str(val)); it.setTextAlignment(Qt.AlignmentFlag.AlignCenter); return it

            self.table.setItem(i, 2, c(emp.get('present_days')))
            self.table.setItem(i, 3, c(emp.get('late_days')))
            self.table.setItem(i, 4, c(emp.get('absent_days')))
            self.table.setItem(i, 5, c(f"{float(emp.get('total_hours_worked', 0)):.1f}"))
            self.table.setItem(i, 6, c(f"{float(emp.get('attendance_rate', 0)):.1f}%"))

    def create_trend_graph(self, start_date, end_date):
        """Generates a line graph image with Legend, Axis Labels, and Grid"""
        try:
            db = Database.get()
            query = """SELECT date, total_present_employees, total_late_employees, total_absent_employees
                       FROM reports \
                       WHERE date BETWEEN %s \
                         AND %s \
                       ORDER BY date ASC"""
            results = db.query_all(query, (start_date, end_date))

            if not results: return None

            width, height = 800, 320
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.GlobalColor.white)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Margins
            m_left, m_right, m_top, m_bottom = 70, 30, 50, 50
            draw_w = width - m_left - m_right
            draw_h = height - m_top - m_bottom

            # Find scales
            max_val = 0
            for r in results:
                max_val = max(max_val, r['total_present_employees'], r['total_late_employees'],
                              r['total_absent_employees'])
            max_val = max(max_val, 10)

            # Draw Legend
            legend_items = [("Present", "#0EA574"), ("Late", "#D97706"), ("Absent", "#C41230")]
            legend_x = width - 300
            legend_y = 15

            font = QFont("Arial", 10)
            font.setBold(True)
            painter.setFont(font)

            for label, color_hex in legend_items:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(color_hex)))
                painter.drawRect(legend_x, legend_y, 12, 12)
                painter.setPen(QPen(QColor("#374151")))
                painter.drawText(legend_x + 20, legend_y + 11, label)
                legend_x += 90

            # --- DRAW Y-AXIS (Count) ---
            painter.setPen(QPen(QColor("#d1d5db"), 1))
            painter.drawLine(m_left, m_top, m_left, height - m_bottom)  # Y Line

            # Y-Axis Title
            painter.save()
            painter.translate(20, height / 2)
            painter.rotate(-90)
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(0, 0, "Count")
            painter.restore()

            # Y-Axis Ticks & Labels
            font_small = QFont("Arial", 9)
            painter.setFont(font_small)
            step_y = max(1, int(max_val / 5))
            for i in range(0, max_val + 1, step_y):
                y = (height - m_bottom) - (i / max_val) * draw_h
                # Grid line
                painter.setPen(QPen(QColor("#f3f4f6"), 1))
                painter.drawLine(m_left, int(y), width - m_right, int(y))
                # Tick & Label
                painter.setPen(QPen(QColor("#6b7280")))
                painter.drawLine(m_left - 5, int(y), m_left, int(y))
                painter.drawText(QRectF(m_left - 40, y - 10, 30, 20),
                                 Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(i))

            # --- DRAW X-AXIS (Date) ---
            painter.setPen(QPen(QColor("#d1d5db"), 2))
            painter.drawLine(m_left, height - m_bottom, width - m_right, height - m_bottom)  # X Line

            # X-Axis Labels (Date)
            step_x = max(1, len(results) // 7)  # Show roughly 7 dates max
            for i in range(0, len(results), step_x):
                row = results[i]
                x = m_left + (i / (len(results) - 1 if len(results) > 1 else 1)) * draw_w

                # Tick
                painter.drawLine(int(x), height - m_bottom, int(x), height - m_bottom + 5)

                # Date Text
                date_str = row['date'].strftime("%m-%d")
                painter.drawText(QRectF(x - 20, height - m_bottom + 5, 40, 20), Qt.AlignmentFlag.AlignCenter, date_str)

            # X-Axis Title
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(QRectF(m_left, height - 20, draw_w, 20), Qt.AlignmentFlag.AlignCenter, "Date")

            # --- DRAW LINES ---
            lines = [('total_present_employees', "#0EA574"), ('total_late_employees', "#D97706"),
                     ('total_absent_employees', "#C41230")]

            def get_pt(idx, val):
                x = m_left + (idx / (len(results) - 1 if len(results) > 1 else 1)) * draw_w
                y = (height - m_bottom) - (val / max_val) * draw_h
                return QPointF(x, y)

            for key, color_hex in lines:
                painter.setPen(QPen(QColor(color_hex), 3))
                path = []
                for i, row in enumerate(results):
                    path.append(get_pt(i, row[key]))

                for i in range(len(path) - 1):
                    painter.drawLine(path[i], path[i + 1])

            painter.end()

            temp_path = os.path.join(os.path.expanduser("~"), "temp_report_graph.png")
            pixmap.save(temp_path)
            return temp_path
        except Exception as e:
            print(f"Graph error: {e}")
            return None

    def export_pdf(self):
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

            fname = f"{self.title.replace(' ', '_')}.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "Save PDF",
                                                  os.path.join(os.path.expanduser("~"), "Desktop", fname),
                                                  "PDF (*.pdf)")
            if not path: return
            printer.setOutputFileName(path)

            # Parse Dates
            graph_html = ""
            start_date, end_date = None, None
            try:
                if "15-Day" in self.title:
                    parts = self.title.split('(')[1].split(')')[0].split(' to ')
                    start_date = parts[0];
                    end_date = parts[1]
                elif "Monthly" in self.title:
                    parts = self.title.split(' - ')[1].split(' ')
                    month_num = list(calendar.month_name).index(parts[0])
                    year = int(parts[1])
                    start_date = date(year, month_num, 1)
                    end_date = date(year, month_num, calendar.monthrange(year, month_num)[1])

                if start_date and end_date:
                    img_path = self.create_trend_graph(start_date, end_date)
                    if img_path:
                        graph_html = f'<div style="text-align:center; margin-bottom: 20pt;"><img src="{img_path}" width="600" height="240"></div>'
            except Exception as e:
                print(f"Date parse error: {e}")

            html = f"""
            <html><body style="font-family: Arial; font-size: 11pt; color: #333;">
                <h1 style="font-size: 22pt; font-weight: bold; margin-bottom: 20pt; color: #111827;">{self.title}</h1>
                <div style="font-size: 10pt; color: #666; margin-bottom: 25pt;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                {graph_html}
            """

            if self.top_employee:
                html += f"""
                <div style="border: 2px solid #F59E0B; padding: 15pt; border-radius: 8pt; margin-bottom: 30pt; background-color: #FFFBEB;">
                    <div style="color: #F59E0B; font-weight: bold; font-size: 10pt; text-transform: uppercase; margin-bottom: 5pt;">Top Performer</div>
                    <div style="font-size: 20pt; font-weight: bold; color: #111827; margin-bottom: 5pt;">{self.top_employee.get('full_name')}</div>
                    <div style="color: #4B5563; font-size: 12pt; margin-bottom: 10pt;">{self.top_employee.get('position')}</div>
                    <div style="font-size: 16pt; font-weight: bold; color: #059669;">
                        {float(self.top_employee.get('attendance_rate', 0)):.1f}% Attendance Rate
                    </div>
                </div>"""

            html += """<table width="100%" cellspacing="0" cellpadding="6" style="border-collapse: collapse; font-size: 10pt;">
                    <thead><tr style="background-color: #1F2937; color: white;">
                            <th align="left" style="padding: 8pt;">Name</th>
                            <th align="left" style="padding: 8pt;">Position</th>
                            <th align="center" style="padding: 8pt;">Present</th>
                            <th align="center" style="padding: 8pt;">Late</th>
                            <th align="center" style="padding: 8pt;">Absent</th>
                            <th align="center" style="padding: 8pt;">Hours</th>
                            <th align="center" style="padding: 8pt;">Rate</th>
                    </tr></thead><tbody>"""

            for i, emp in enumerate(self.data):
                bg = "#ffffff" if i % 2 == 0 else "#f9fafb"
                html += f"""<tr style="background-color: {bg};">
                    <td style="padding: 8pt; border-bottom: 1px solid #e5e7eb;">{emp.get('full_name')}</td>
                    <td style="padding: 8pt; border-bottom: 1px solid #e5e7eb;">{emp.get('position')}</td>
                    <td align="center" style="padding: 8pt; border-bottom: 1px solid #e5e7eb;">{emp.get('present_days')}</td>
                    <td align="center" style="padding: 8pt; border-bottom: 1px solid #e5e7eb;">{emp.get('late_days')}</td>
                    <td align="center" style="padding: 8pt; border-bottom: 1px solid #e5e7eb;">{emp.get('absent_days')}</td>
                    <td align="center" style="padding: 8pt; border-bottom: 1px solid #e5e7eb;">{float(emp.get('total_hours_worked', 0)):.1f}</td>
                    <td align="center" style="padding: 8pt; border-bottom: 1px solid #e5e7eb; font-weight: bold;">{float(emp.get('attendance_rate', 0)):.1f}%</td>
                </tr>"""
            html += "</tbody></table></body></html>"

            doc = QTextDocument();
            doc.setHtml(html);
            doc.print(printer)
            from Project.View.Dialogs import CompactMessageDialog
            CompactMessageDialog.show_success(self, "Exported", f"Saved to {path}")
        except Exception as e:
            print(e)