from datetime import datetime
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)

from core.events import events
from core.state import state
from core.logger import logger
from core.config import config
from ui.styles.hud_styles import DARK_HUD_QSS
from ui.widgets.reactor_orb import ReactorOrbWidget
from ui.widgets.telemetry_bar import TelemetryBarWidget
from ui.widgets.log_console import LogConsoleWidget
from ui.widgets.prompt_bar import PromptBarWidget

class JARVISMainWindow(QMainWindow):
    """
    JARVIS Milestone 1 Production Main Window.
    """
    def __init__(self):
        super().__init__()
        
        # Load configuration
        title = config.get("ui.window_title", "JARVIS — Production AI Desktop Interface")
        width = config.get("ui.width", 1280)
        height = config.get("ui.height", 800)

        self.setWindowTitle(title)
        self.resize(width, height)
        self.setMinimumSize(1024, 650)
        
        # Apply stylesheet
        self.setStyleSheet(DARK_HUD_QSS)

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # 1. Top Navbar
        main_layout.addWidget(self._create_header())

        # 2. Main Body (Sidebar + Central Core Viewport + Right Telemetry)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        body_layout.addWidget(self._create_sidebar(), 1)
        body_layout.addWidget(self._create_center_viewport(), 4)
        body_layout.addWidget(TelemetryBarWidget(), 1)

        main_layout.addLayout(body_layout, 1)

        # Real-time Clock Timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

        # Connect Event Bus Signals
        events.system_status_changed.connect(self._on_status_changed)
        events.ai_response_received.connect(self._on_ai_response)
        events.user_command_submitted.connect(self.console_widget.append_user_msg)

        logger.info("JARVIS MainWindow setup complete [Milestone 1].")

    def _create_header(self) -> QFrame:
        frame = QFrame()
        frame.setProperty("class", "hud-panel")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)

        # Title & Subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        
        title_lbl = QLabel("J.A.R.V.I.S")
        title_lbl.setProperty("class", "hud-title")
        sub_lbl = QLabel("// SYSTEM ONLINE v1.0.0 — MILESTONE 1 SKELETON")
        sub_lbl.setProperty("class", "hud-subtitle")

        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)

        # Status Badge
        self.status_badge = QLabel("ONLINE")
        self.status_badge.setProperty("class", "status-online")
        self.status_badge.setAlignment(Qt.AlignCenter)

        # Realtime Clock
        self.clock_label = QLabel("--:--:--")
        self.clock_label.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 15px; font-family: monospace;")

        layout.addLayout(title_box)
        layout.addWidget(self.status_badge)
        layout.addStretch()
        layout.addWidget(self.clock_label)

        return frame

    def _create_sidebar(self) -> QFrame:
        frame = QFrame()
        frame.setProperty("class", "hud-panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(8)

        section_title = QLabel("NAVIGATION")
        section_title.setProperty("class", "hud-subtitle")
        layout.addWidget(section_title)

        nav_items = ["Dashboard", "AI Core", "Voice Engine", "Vision Engine", "Plugins", "Settings"]
        self.sidebar_btns = {}

        for item in nav_items:
            btn = QPushButton(f"⚡  {item}")
            btn.setProperty("class", "sidebar-btn")
            if item == "Dashboard":
                btn.setProperty("class", "sidebar-btn active")
            btn.clicked.connect(lambda _, name=item: self._on_nav_clicked(name))
            layout.addWidget(btn)
            self.sidebar_btns[item] = btn

        layout.addStretch()

        arch_lbl = QLabel("ARCHITECTURE\nModular Qt Engine")
        arch_lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        layout.addWidget(arch_lbl)

        return frame

    def _create_center_viewport(self) -> QFrame:
        frame = QFrame()
        frame.setProperty("class", "hud-panel-active")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Central Visual Reactor Core Widget & Header
        top_box = QHBoxLayout()
        title_lbl = QLabel("CENTRAL REACTOR & SYSTEM STREAM")
        title_lbl.setProperty("class", "hud-title")
        
        self.reactor_widget = ReactorOrbWidget()
        
        top_box.addWidget(title_lbl, 1)
        top_box.addWidget(self.reactor_widget)

        layout.addLayout(top_box)

        # Console Stream Widget
        self.console_widget = LogConsoleWidget()
        layout.addWidget(self.console_widget, 1)

        # Prompt Input Bar Widget
        self.prompt_bar = PromptBarWidget()
        self.prompt_bar.command_submitted.connect(self._handle_command)
        layout.addWidget(self.prompt_bar)

        return frame

    def _update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.clock_label.setText(now)

    def _handle_command(self, cmd: str):
        self.console_widget.append_user_msg(cmd)
        events.user_command_submitted.emit(cmd)
        self.console_widget.append_system_msg(f"Command '{cmd}' received into EventBus.")

    def _on_nav_clicked(self, name: str):
        for btn_name, btn in self.sidebar_btns.items():
            if btn_name == name:
                btn.setProperty("class", "sidebar-btn active")
            else:
                btn.setProperty("class", "sidebar-btn")
            btn.setStyle(btn.style())
        state.set("active_tab", name)

    @Slot(str)
    def _on_status_changed(self, status: str):
        self.status_badge.setText(status.upper())

    @Slot(str)
    def _on_ai_response(self, response: str):
        self.console_widget.append_system_msg(response)
