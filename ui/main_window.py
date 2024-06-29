from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout
from .web_engine import WebEngineView
from monitoring.health_monitor import HealthMonitor
from management.food_manager import FoodManager
from management.threshold_manager import ThresholdManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Melvor Idle Auto Eater")
        self.setGeometry(100, 100, 1200, 800)

        self.browser = WebEngineView()
        self.health_label = QLabel("Health: N/A")
        self.max_health_label = QLabel("Max Health: N/A")
        self.danger_label = QLabel("In Danger: N/A")

        self.threshold_manager = ThresholdManager()
        self.food_manager = FoodManager(self.browser)

        self.threshold_input = QLineEdit()
        self.threshold_button = QPushButton("Set Threshold")
        self.threshold_button.clicked.connect(self.set_threshold)

        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Health Threshold (%):"))
        threshold_layout.addWidget(self.threshold_input)
        threshold_layout.addWidget(self.threshold_button)

        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.health_label)
        layout.addWidget(self.max_health_label)
        layout.addWidget(self.danger_label)
        layout.addLayout(threshold_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.health_monitor = HealthMonitor(self.browser, self.health_label, self.max_health_label, self.danger_label, self.threshold_manager, self.food_manager)
        self.health_monitor.start_monitoring()

    def set_threshold(self):
        try:
            percentage = float(self.threshold_input.text()) / 100
            self.threshold_manager.set_threshold_percentage(percentage)
        except ValueError:
            print("Invalid threshold input")
