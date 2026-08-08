"""
JARVIS Milestone 2 Futuristic HUD Stylesheet (QSS)
Color Palette:
- Canvas Background: #030509
- Soft Depth Glow: #0a1626
- Surface Fill: rgba(10, 18, 32, 0.75)
- Primary Accent: #4fd0ff
- Soft Cyan: #8fe3ff
- Speaking Amber: #ffb455 (RESERVED FOR SPEAKING/VOICE OUTPUT)
- Telemetry Numbers: #38bdf8
- Status Online: #10b981
- Status Error: #ef4444
"""

DARK_HUD_QSS = """
/* Global Window & Base Palette */
QMainWindow, QDialog {
    background-color: #030509;
    color: #e2e8f0;
    font-family: 'Rajdhani', 'Segoe UI', sans-serif;
}

QWidget {
    color: #cbd5e1;
    font-family: 'Rajdhani', 'Segoe UI', sans-serif;
    font-size: 13px;
}

/* Headers & Typography */
QLabel.hud-title {
    color: #4fd0ff;
    font-family: 'Rajdhani', 'Segoe UI', sans-serif;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

QLabel.hud-subtitle {
    color: #64748b;
    font-family: 'IBM Plex Mono', 'Consolas', monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

QLabel.hud-data {
    color: #38bdf8;
    font-family: 'IBM Plex Mono', 'Consolas', monospace;
    font-size: 12px;
}

QLabel.hud-stat-value {
    color: #4fd0ff;
    font-family: 'IBM Plex Mono', 'Consolas', monospace;
    font-size: 22px;
    font-weight: 700;
}

/* Ticker Chips */
QLabel.ticker-chip {
    background-color: rgba(15, 23, 42, 0.8);
    color: #8fe3ff;
    border: 1px solid rgba(79, 208, 255, 0.3);
    border-radius: 4px;
    padding: 3px 8px;
    font-family: 'IBM Plex Mono', 'Consolas', monospace;
    font-size: 11px;
    font-weight: 600;
}

/* Sidebar Navigation */
QPushButton.sidebar-btn {
    background-color: transparent;
    color: #64748b;
    border: none;
    border-radius: 6px;
    padding: 10px 14px;
    text-align: left;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 1px;
}

QPushButton.sidebar-btn:hover {
    background-color: rgba(79, 208, 255, 0.1);
    color: #4fd0ff;
}

QPushButton.sidebar-btn.active {
    background-color: rgba(79, 208, 255, 0.16);
    color: #4fd0ff;
    border-left: 3px solid #4fd0ff;
}

/* State Control Buttons */
QPushButton.state-btn {
    background-color: rgba(15, 23, 42, 0.8);
    color: #64748b;
    border: 1px solid rgba(79, 208, 255, 0.25);
    border-radius: 4px;
    padding: 5px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
}

QPushButton.state-btn:hover {
    background-color: rgba(79, 208, 255, 0.15);
    color: #4fd0ff;
    border-color: #4fd0ff;
}

QPushButton.state-btn.active-idle {
    background-color: rgba(79, 208, 255, 0.2);
    color: #4fd0ff;
    border-color: #4fd0ff;
}

QPushButton.state-btn.active-listening {
    background-color: rgba(143, 227, 255, 0.2);
    color: #8fe3ff;
    border-color: #8fe3ff;
}

QPushButton.state-btn.active-thinking {
    background-color: rgba(56, 189, 248, 0.2);
    color: #38bdf8;
    border-color: #38bdf8;
}

QPushButton.state-btn.active-speaking {
    background-color: rgba(255, 180, 85, 0.2);
    color: #ffb455;
    border-color: #ffb455;
}

QPushButton.state-btn.active-error {
    background-color: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    border-color: #ef4444;
}

/* Primary Execute Button */
QPushButton.hud-btn-primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0088ff, stop:1 #4fd0ff);
    color: #030509;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 1px;
}

QPushButton.hud-btn-primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0099ff, stop:1 #8fe3ff);
}

/* Input Fields */
QLineEdit.hud-input {
    background-color: rgba(3, 5, 9, 0.9);
    color: #4fd0ff;
    border: 1px solid rgba(79, 208, 255, 0.3);
    border-radius: 4px;
    padding: 10px 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
}

QLineEdit.hud-input:focus {
    border: 1px solid #4fd0ff;
    background-color: rgba(10, 18, 32, 0.95);
}

/* Console Log View */
QTextEdit.hud-log {
    background-color: transparent;
    color: #38bdf8;
    border: none;
    font-family: 'IBM Plex Mono', 'Consolas', monospace;
    font-size: 12px;
    padding: 4px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: rgba(15, 23, 42, 0.4);
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: rgba(79, 208, 255, 0.3);
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #4fd0ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
