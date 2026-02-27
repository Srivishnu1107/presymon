import sys, random, datetime
from collections import deque

import psutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from reportlab.pdfgen import canvas

pg.setConfigOptions(antialias=True)

# =====================================
# DAY SELECT WINDOW
# =====================================

class DailyReportWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Day")
        self.resize(300, 200)

        layout = QVBoxLayout(self)

        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)

        btn = QPushButton("Download Report")
        btn.clicked.connect(self.save_report)
        layout.addWidget(btn)

    def save_report(self):
        day = self.calendar.selectedDate().toString("yyyy-MM-dd")
        file = f"daily_prediction_{day}.pdf"

        c = canvas.Canvas(file)
        c.drawString(100, 750, f"Prediction Report — {day}")
        c.drawString(100, 720, "System expected to remain STABLE")
        c.drawString(100, 700, "Suggestion: Maintain current usage")
        c.save()

        QMessageBox.information(self, "Saved", file)


# =====================================
# MAIN DASHBOARD
# =====================================

class PresymonTitan(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PRESYMON PROFESSIONAL")
        self.resize(1250, 820)

        self.setStyleSheet("""
            QWidget {background:#0b0f14; color:white; font:12pt Segoe UI;}
            QTextEdit, QLineEdit {
                background:#0f1620;
                border:2px solid #00ffaa;
                border-radius:6px;
                color:white;
            }
            QPushButton {
                background:#00ffaa;
                color:black;
                font-weight:bold;
                padding:8px;
                border-radius:6px;
            }
        """)

        self.init_ui()

        self.cpu_hist = deque(maxlen=60)
        self.ram_hist = deque(maxlen=60)
        self.disk_hist = deque(maxlen=60)
        self.net_hist = deque(maxlen=60)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    # =====================================
    # UI
    # =====================================

    def init_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main = QGridLayout(central)

        # ===== AI DOCTOR =====

        ai_layout = QVBoxLayout()

        title = QLabel("PRESYMON BOT")
        title.setStyleSheet("font:20pt; color:#00ffaa;")
        ai_layout.addWidget(title)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        ai_layout.addWidget(self.chat)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask about system...")
        self.input.returnPressed.connect(self.ask_ai)
        ai_layout.addWidget(self.input)

        ask = QPushButton("Ask")
        ask.clicked.connect(self.ask_ai)
        ai_layout.addWidget(ask)

        daily = QPushButton("Daily Report")
        daily.clicked.connect(self.daily_report)

        month = QPushButton("30 Day Report")
        month.clicked.connect(self.month_report)

        ai_layout.addWidget(daily)
        ai_layout.addWidget(month)

        main.addLayout(ai_layout, 0, 0)

        # ===== ALERTS =====

        alert_layout = QVBoxLayout()

        alert_title = QLabel("⚠ ALERTS")
        alert_title.setStyleSheet("color:#ffcc00; font-weight:bold;")
        alert_layout.addWidget(alert_title)

        self.alert_box = QTextEdit()
        self.alert_box.setReadOnly(True)
        self.alert_box.setMinimumHeight(180)
        alert_layout.addWidget(self.alert_box)

        alert_layout.addStretch()

        main.addLayout(alert_layout, 1, 0)

        # ===== GRAPHS =====

        grid = QGridLayout()

        self.cpu_plot = self.make_plot("CPU Usage")
        self.ram_plot = self.make_plot("RAM Usage")
        self.disk_plot = self.make_plot("Disk Usage")
        self.net_plot = self.make_plot("Network")

        grid.addWidget(self.cpu_plot, 0, 0)
        grid.addWidget(self.ram_plot, 0, 1)
        grid.addWidget(self.disk_plot, 1, 0)
        grid.addWidget(self.net_plot, 1, 1)

        main.addLayout(grid, 0, 1, 2, 1)

    def make_plot(self, title):
        p = pg.PlotWidget(title=title)
        p.setBackground("#0f1620")
        p.showGrid(x=True, y=True, alpha=0.25)
        p.setYRange(0, 100)
        return p

    # =====================================
    # AI DOCTOR
    # =====================================

    def ask_ai(self):

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        jokes = [
            "Nothing is on fire 🔥 Relax",
            "Your PC is chilling 😎",
            "System behaving better than humans 👍",
            "All systems nominal 🚀"
        ]

        suggestion = "No action needed"
        if ram > 85:
            suggestion = "Close some apps — RAM high"

        prediction = "Stable"
        if cpu > 80 or ram > 90:
            prediction = "High Load Incoming"

        text = f"""
CPU: {cpu:.1f}%
RAM: {ram:.1f}%
Disk: {disk:.1f}%

Suggestion: {suggestion}
5-sec Prediction: {prediction}

{random.choice(jokes)}
"""

        self.chat.append(text)

    # =====================================
    # REPORTS
    # =====================================

    def daily_report(self):
        win = DailyReportWindow()
        win.exec_()

    def month_report(self):
        file = "30_day_prediction_report.pdf"
        c = canvas.Canvas(file)
        c.drawString(100, 750, "30 Day Prediction Report")

        for i in range(30):
            c.drawString(100, 730 - i * 15,
                         f"Day {i+1}: System Stable")

        c.save()
        QMessageBox.information(self, "Saved", file)

    # =====================================
    # GRAPH UPDATE
    # =====================================

    def smooth(self, data, w=5):
        if len(data) < w:
            return data
        return [sum(list(data)[max(0,i-w):i+1])/(i-max(0,i-w)+1)
                for i in range(len(data))]

    def update_stats(self):

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        net = psutil.net_io_counters().bytes_sent / 1e6

        self.cpu_hist.append(cpu)
        self.ram_hist.append(ram)
        self.disk_hist.append(disk)
        self.net_hist.append(net)

        pen = pg.mkPen('#00ffaa', width=2)

        for plot in [self.cpu_plot, self.ram_plot,
                     self.disk_plot, self.net_plot]:
            plot.clear()

        self.cpu_plot.plot(self.smooth(self.cpu_hist), pen=pen)
        self.ram_plot.plot(self.smooth(self.ram_hist), pen=pen)
        self.disk_plot.plot(self.smooth(self.disk_hist), pen=pen)
        self.net_plot.plot(self.smooth(self.net_hist), pen=pen)

        # Alerts
        self.alert_box.clear()

        if ram > 90:
            self.alert_box.append("🔴 RAM CRITICAL")
        elif cpu > 85:
            self.alert_box.append("🟠 CPU HIGH")
        else:
            self.alert_box.append("🟢 System Stable")


# =====================================
# RUN
# =====================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PresymonTitan()
    win.show()
    sys.exit(app.exec_())