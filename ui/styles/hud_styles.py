"""
JARVIS Futuristic Dark HUD Theme Stylesheet (QSS)
"""

DARK_HUD_QSS = """
/* Global Window & Base Styles */
QMainWindow, QDialog {
    background-color: #070b14;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}

QWidget {
    color: #cbd5e1;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}

/* Glassmorphism / HUD Card Panels */
QFrame.hud-panel {
    background-color: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 12px;
}

QFrame.hud-panel:hover {
    border: 1px solid rgba(0, 240, 255, 0.4);
}

QFrame.hud-panel-active {
    background-color: rgba(15, 23, 42, 0.9);
    border: 1px solid #00f0ff;
    border-radius: 12px;
}

/* Headers & Titles */
QLabel.hud-title {
    color: #00f0ff;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

QLabel.hud-subtitle {
    color: #94a3b8;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel.hud-stat-value {
    color: #38bdf8;
    font-size: 24px;
    font-weight: 800;
}

/* Sidebar Buttons */
QPushButton.sidebar-btn {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    font-size: 14px;
}

QPushButton.sidebar-btn:hover {
    background-color: rgba(0, 240, 255, 0.1);
    color: #00f0ff;
}

QPushButton.sidebar-btn:checked, QPushButton.sidebar-btn.active {
    background-color: rgba(0, 240, 255, 0.18);
    color: #00f0ff;
    border-left: 4px solid #00f0ff;
    border-top-left-radius: 2px;
    border-bottom-left-radius: 2px;
}

/* Primary Action Buttons */
QPushButton.hud-btn-primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0088ff, stop:1 #00f0ff);
    color: #050b14;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QPushButton.hud-btn-primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0099ff, stop:1 #33f3ff);
}

QPushButton.hud-btn-primary:pressed {
    background: #0088ff;
}

/* Secondary / Cyber Buttons */
QPushButton.hud-btn-secondary {
    background-color: rgba(30, 41, 59, 0.8);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.hud-btn-secondary:hover {
    background-color: rgba(56, 189, 248, 0.15);
    border: 1px solid #38bdf8;
    color: #00f0ff;
}

/* Command Prompt Input */
QLineEdit.hud-input {
    background-color: rgba(10, 15, 29, 0.85);
    color: #00f0ff;
    border: 1px solid rgba(0, 240, 255, 0.3);
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 14px;
    selection-background-color: #00f0ff;
    selection-color: #070b14;
}

QLineEdit.hud-input:focus {
    border: 1px solid #00f0ff;
    background-color: rgba(10, 15, 29, 0.95);
}

/* Status Badges */
QLabel.status-online {
    background-color: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid #10b981;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
}

QLabel.status-processing {
    background-color: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid #f59e0b;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
}

/* Console Log & Text Area */
QTextEdit.hud-log {
    background-color: rgba(5, 8, 16, 0.9);
    color: #38bdf8;
    border: 1px solid rgba(0, 240, 255, 0.15);
    border-radius: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 10px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: rgba(15, 23, 42, 0.5);
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: rgba(0, 240, 255, 0.3);
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #00f0ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
