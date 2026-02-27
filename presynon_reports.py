import sys
import psutil
import random
from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg

pg.setConfigOptions(antialias=True)


# =========================================================
# DAILY REPORT WINDOW
# =========================================================

class DailyReportWindow(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Select Day — Prediction")
        self.resize(350, 450)

        layout = QVBoxLayout(self)

        self.list = QListWidget()
        for i in range(1, 31):
            self.list.addItem(f"Day {i}")

        layout.addWidget(self.list)

        btn = QPushButton("Download Report")
        btn.clicked.connect(self.download)
        layout.addWidget(btn)

    def download(self):

        item = self.list.currentItem()
        if not item:
            return

        day = item.text()

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        prediction = random.choice([
            "System stable",
            "Moderate load expected",
            "High workload predicted",
            "Performance slowdown possible"
        ])

        suggestion = random.choice([
            "Close background apps",
            "Restart system",
            "Clean disk",
            "Check cooling system"
        ])

        report = f"""
PRESYMON DAILY REPORT — {day}
Generated: {datetime.now()}

CPU: {cpu} %
RAM: {ram} %
Disk: {disk} %

Prediction:
{prediction}

Do:
- {suggestion}

Don't:
- Ignore warnings
- Run heavy apps continuously
"""

        filename = f"Presymon_{day.replace(' ','_')}.txt"

        # ✅ UTF-8 FIX
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)

        QMessageBox.information(self, "Saved", f"Report saved as {filename}")


# =========================================================
# MONTH REPORT
# =========================================================

def generate_month_report():

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    report = f"""
PRESYMON 30-DAY REPORT
Generated: {datetime.now()}

CPU: {cpu} %
RAM: {ram} %
Disk: {disk} %

Trend:
System expected to remain stable.

Maintenance Tips:
- Update OS
- Clean storage
- Monitor background processes
"""

    filename = "Presymon_30Day_Report.txt"

    # ✅ UTF-8 FIX
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    return filename


# =========================================================
# MAIN DASHBOARD
# =========================================================

class PresymonDashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PRESYMON PROFESSIONAL DASHBOARD")
        self.resize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)

        main = QHBoxLayout(central)

        # ======================================================
        # LEFT — AI SYSTEM DOCTOR
        # ======================================================

        left = QVBoxLayout()

        title = QLabel("AI SYSTEM DOCTOR")
        title.setStyleSheet("font-size:24px; font-weight:bold; color:#00ffc6;")
        left.addWidget(title)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("background:#0b0f14; color:white;")
        left.addWidget(self.chat)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask about system...")
        left.addWidget(self.input)

        ask_btn = QPushButton("Ask")
        ask_btn.clicked.connect(self.ask_ai)
        left.addWidget(ask_btn)

        daily_btn = QPushButton("Daily Report")
        daily_btn.clicked.connect(self.daily_report)
        left.addWidget(daily_btn)

        month_btn = QPushButton("30 Day Report")
        month_btn.clicked.connect(self.month_report)
        left.addWidget(month_btn)

        main.addLayout(left, 2)

        # ======================================================
        # RIGHT — GRAPHS
        # ======================================================

        right = QGridLayout()

        self.cpu_plot = self.make_plot("CPU")
        self.ram_plot = self.make_plot("RAM")
        self.disk_plot = self.make_plot("Disk")
        self.net_plot = self.make_plot("Network")

        right.addWidget(self.cpu_plot, 0, 0)
        right.addWidget(self.ram_plot, 0, 1)
        right.addWidget(self.disk_plot, 1, 0)
        right.addWidget(self.net_plot, 1, 1)

        main.addLayout(right, 3)

        # DATA
        self.cpu_data = [0]*60
        self.ram_data = [0]*60
        self.disk_data = [0]*60
        self.net_data = [0]*60

        self.prev_net = psutil.net_io_counters().bytes_sent

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    # ======================================================
    # GRAPH
    # ======================================================

    def make_plot(self, title):
        plot = pg.PlotWidget(title=title)
        plot.setBackground((10, 15, 20))
        plot.setYRange(0, 100)
        plot.showGrid(x=True, y=True)
        return plot

    # ======================================================
    # LIVE UPDATE
    # ======================================================

    def update_stats(self):

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        net_now = psutil.net_io_counters().bytes_sent
        net_speed = (net_now - self.prev_net) / 1024
        self.prev_net = net_now

        self.shift(self.cpu_data, cpu)
        self.shift(self.ram_data, ram)
        self.shift(self.disk_data, disk)
        self.shift(self.net_data, net_speed)

        self.cpu_plot.clear(); self.cpu_plot.plot(self.cpu_data, pen='#00ffc6')
        self.ram_plot.clear(); self.ram_plot.plot(self.ram_data, pen='#00ffc6')
        self.disk_plot.clear(); self.disk_plot.plot(self.disk_data, pen='#00ffc6')
        self.net_plot.clear(); self.net_plot.plot(self.net_data, pen='#00ffc6')

    def shift(self, arr, val):
        arr.pop(0)
        arr.append(val)

    # ======================================================
    # AI RESPONSE (LOCAL SYSTEM AI)
    # ======================================================

    def ask_ai(self):

        q = self.input.text().lower()
        self.input.clear()

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        if "cpu" in q:
            ans = f"CPU usage is {cpu}%"
        elif "ram" in q or "memory" in q:
            ans = f"RAM usage is {ram}%"
        elif "disk" in q:
            ans = f"Disk usage is {disk}%"
        elif "health" in q:
            health = 100 - (cpu + ram + disk)/3
            ans = f"System health is {health:.1f}%"
        else:
            ans = "Ask about CPU, RAM, Disk or Health."

        self.chat.append(f"You: {q}")
        self.chat.append(f"AI: {ans}")
        self.chat.append("")

    # ======================================================
    # BUTTONS
    # ======================================================

    def daily_report(self):
        DailyReportWindow().exec_()

    def month_report(self):
        file = generate_month_report()
        QMessageBox.information(self, "Saved", f"Saved as {file}")


# =========================================================
# RUN
# =========================================================

app = QApplication(sys.argv)
win = PresymonDashboard()
win.show()
sys.exit(app.exec_())