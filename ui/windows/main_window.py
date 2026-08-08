from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)

from core.events import events
from core.state import state
from core.logger import logger
from core.config import config
from ui.styles.hud_styles import DARK_HUD_QSS

# Widgets
from ui.widgets.ticker_bar import TickerBarWidget
from ui.widgets.hud_panel import HUDPanel
from ui.widgets.device_snapshot import DeviceSnapshotWidget
from ui.widgets.activity_graph import ActivityGraphWidget
from ui.widgets.reactor_orb import ReactorOrbWidget
from ui.widgets.state_controls import StateControlsWidget
from ui.widgets.log_console import IntegratedConsolePanel
from ui.widgets.schedule_panel import SchedulePanelWidget
from ui.widgets.audio_eq import AudioEQWidget
from ui.widgets.subsystem_status import SubsystemStatusWidget

class JARVISMainWindow(QMainWindow):
    """
    JARVIS Milestone 2 Production Main Window.
    Implements 3-column HUD desktop interface with Top Ticker Bar, AI Reactor Core,
    Chamfered Cut-Corner Glass Panels, Integrated Console, and Realtime Telemetry.
    """
    def __init__(self):
        super().__init__()
        
        # Load configuration
        title = config.get("ui.window_title", "JARVIS — Personal AI Operating System")
        width = config.get("ui.width", 1280)
        height = config.get("ui.height", 800)

        self.setWindowTitle(title)
        self.resize(width, height)
        self.setMinimumSize(1024, 650)
        
        # Apply QSS stylesheet
        self.setStyleSheet(DARK_HUD_QSS)

        # Main Base Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        base_layout = QVBoxLayout(central_widget)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)

        # 1. Top Ticker Bar
        self.ticker_bar = TickerBarWidget()
        base_layout.addWidget(self.ticker_bar)

        # 2. Main 3-Column HUD Workspace Layout
        workspace = QWidget()
        body_layout = QHBoxLayout(workspace)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(12)

        # Left, Center, Right Columns
        left_col = self._create_left_column()
        center_col = self._create_center_column()
        right_col = self._create_right_column()

        body_layout.addWidget(left_col, 0)
        body_layout.addWidget(center_col, 1)
        body_layout.addWidget(right_col, 0)

        base_layout.addWidget(workspace, 1)

        # Event Bus Signal Wiring
        events.system_status_changed.connect(self._on_status_changed)
        events.ai_response_received.connect(self.console_panel.append_system_msg)
        events.user_command_submitted.connect(self.console_panel.append_user_msg)

        logger.info("JARVIS Milestone 2 HUD Interface initialized.")

    def _create_left_column(self) -> QWidget:
        col = QWidget()
        col.setFixedWidth(230)
        layout = QVBoxLayout(col)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Navigation Bar Panel
        nav_panel = HUDPanel()
        nav_title = QLabel("NAVIGATION")
        nav_title.setProperty("class", "hud-subtitle")
        nav_panel.content_layout.addWidget(nav_title)

        nav_items = ["Dashboard", "AI Core", "Voice Engine", "Vision Engine", "Plugins", "Settings"]
        self.sidebar_btns = {}
        for item in nav_items:
            btn = QPushButton(f"⚡  {item}")
            btn.setProperty("class", "sidebar-btn")
            if item == "Dashboard":
                btn.setProperty("class", "sidebar-btn active")
            btn.clicked.connect(lambda _, name=item: self._on_nav_clicked(name))
            nav_panel.content_layout.addWidget(btn)
            self.sidebar_btns[item] = btn

        layout.addWidget(nav_panel)

        # Device Snapshot Panel
        self.device_panel = DeviceSnapshotWidget()
        layout.addWidget(self.device_panel)

        # Weekly Activity Graph Panel
        self.activity_panel = ActivityGraphWidget()
        layout.addWidget(self.activity_panel, 1)

        return col

    def _create_center_column(self) -> QWidget:
        col = QWidget()
        layout = QVBoxLayout(col)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Central AI Reactor Core Zone
        reactor_container = QWidget()
        reactor_layout = QVBoxLayout(reactor_container)
        reactor_layout.setContentsMargins(0, 0, 0, 0)
        reactor_layout.setSpacing(6)

        # Reactor Core Visualizer
        self.reactor_widget = ReactorOrbWidget()
        reactor_layout.addWidget(self.reactor_widget, 0, Qt.AlignCenter)

        # Dynamic State Label
        self.state_label = QLabel("STATE: IDLE")
        self.state_label.setProperty("class", "hud-title")
        self.state_label.setAlignment(Qt.AlignCenter)
        reactor_layout.addWidget(self.state_label)

        # Developer State Control Bar
        self.state_controls = StateControlsWidget()
        self.state_controls.state_requested.connect(self._on_state_changed)
        reactor_layout.addWidget(self.state_controls, 0, Qt.AlignCenter)

        layout.addWidget(reactor_container, 0)

        # Integrated Console & Stream Panel
        self.console_panel = IntegratedConsolePanel()
        self.console_panel.set_active(True)
        self.console_panel.command_submitted.connect(self._handle_user_command)
        layout.addWidget(self.console_panel, 1)

        return col

    def _create_right_column(self) -> QWidget:
        col = QWidget()
        col.setFixedWidth(260)
        layout = QVBoxLayout(col)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Schedule Panel
        self.schedule_panel = SchedulePanelWidget()
        layout.addWidget(self.schedule_panel, 1)

        # Audio EQ Panel
        self.audio_eq_panel = AudioEQWidget()
        layout.addWidget(self.audio_eq_panel)

        # Subsystem Status Panel
        self.subsystem_panel = SubsystemStatusWidget()
        layout.addWidget(self.subsystem_panel)

        return col

    # State & Command Handlers
    def _on_state_changed(self, new_state: str):
        self.state_label.setText(f"STATE: {new_state}")
        self.reactor_widget.set_state(new_state)
        self.audio_eq_panel.set_state(new_state)
        state.set("status", new_state)

        # Echo log
        self.console_panel.append_system_msg(f"System State Transition: {new_state}")

    def _handle_user_command(self, cmd: str):
        events.user_command_submitted.emit(cmd)

        # Execute built-in browser plugin command check
        if "browser" in cmd.lower() or "google" in cmd.lower() or "search" in cmd.lower():
            from plugins.browser.plugin import BrowserPlugin
            b = BrowserPlugin()
            b.search_web(cmd)
            self.console_panel.append_system_msg(f"Executed Browser Plugin query: '{cmd}'")
        else:
            self.console_panel.append_system_msg(f"Command '{cmd}' received into EventBus.")

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
        self._on_state_changed(status)
