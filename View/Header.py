from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel


class Header(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(65)
        self.build()
        self.apply_theme("light")

    def build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        self.title_label = QLabel("Dashboard")
        layout.addWidget(self.title_label)
        layout.addStretch(1)

    def set_title(self, title):
        self.title_label.setText(title)

    def apply_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #333333;")
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        else:
            self.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #e0e0e0;")
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1a1a;")