COLORS = {
    "bg": "#0f1420",
    "surface": "#161d2e",
    "surface_alt": "#1e2740",
    "border": "#2a3450",
    "text": "#e8ecf7",
    "text_muted": "#8a93ad",
    "primary": "#5b8cff",
    "primary_hover": "#79a1ff",
    "primary_pressed": "#4574e6",
    "accent_steam": "#66c0f4",
    "accent_youtube": "#ff5c5c",
    "accent_metacritic": "#ffcc33",
    "success": "#3ecf8e",
    "danger": "#ff6b6b",
}


APP_STYLESHEET = f"""
QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}}

QLabel[role="title"] {{
    font-size: 18px;
    font-weight: 600;
    color: {COLORS['text']};
}}

QLabel[role="subtitle"] {{
    font-size: 12px;
    color: {COLORS['text_muted']};
}}

QLabel[role="section"] {{
    font-size: 12px;
    font-weight: 600;
    color: {COLORS['text_muted']};
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding-top: 6px;
}}

QFrame[role="card"] {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
}}

QFrame[role="header"] {{
    background-color: {COLORS['surface']};
    border-bottom: 1px solid {COLORS['border']};
}}

QLineEdit, QComboBox {{
    background-color: {COLORS['surface_alt']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 7px 10px;
    color: {COLORS['text']};
    selection-background-color: {COLORS['primary']};
}}

QLineEdit:focus, QComboBox:focus {{
    border: 1px solid {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QListWidget {{
    background-color: {COLORS['surface_alt']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 2px;
}}

QListWidget::item {{
    padding: 6px 8px;
    border-radius: 4px;
}}

QListWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

QListWidget::item:hover {{
    background-color: {COLORS['border']};
}}

QPushButton {{
    background-color: {COLORS['surface_alt']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 7px 14px;
    color: {COLORS['text']};
}}

QPushButton:hover {{
    background-color: {COLORS['border']};
}}

QPushButton:disabled {{
    color: {COLORS['text_muted']};
}}

QPushButton[role="primary"] {{
    background-color: {COLORS['primary']};
    border: none;
    color: white;
    font-weight: 600;
}}

QPushButton[role="primary"]:hover {{
    background-color: {COLORS['primary_hover']};
}}

QPushButton[role="primary"]:pressed {{
    background-color: {COLORS['primary_pressed']};
}}

QPushButton[role="primary"]:disabled {{
    background-color: {COLORS['surface_alt']};
    color: {COLORS['text_muted']};
}}

QPushButton[role="icon"] {{
    background-color: transparent;
    border: none;
    padding: 4px 8px;
    font-size: 16px;
}}

QPushButton[role="icon"]:hover {{
    background-color: {COLORS['surface_alt']};
    border-radius: 6px;
}}

QCheckBox {{
    spacing: 8px;
    padding: 2px 0;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['surface_alt']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QProgressBar {{
    background-color: {COLORS['surface_alt']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    text-align: center;
    color: {COLORS['text']};
    height: 18px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 6px;
}}

QTextEdit {{
    background-color: #0a0e17;
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    color: {COLORS['text_muted']};
    font-family: Consolas, monospace;
    font-size: 11px;
}}

QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    top: -1px;
    background-color: {COLORS['surface']};
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_muted']};
    padding: 9px 18px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['surface']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-bottom: none;
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS['text']};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 5px;
    min-height: 20px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QDialog {{
    background-color: {COLORS['bg']};
}}
"""
