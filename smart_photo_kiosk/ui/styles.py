"""
App Theme & Stylesheets (Modern Dark Kiosk Theme)
"""

MAIN_STYLESHEET = """
QMainWindow {
    background-color: #0F1218;
}

QWidget {
    color: #E2E8F0;
    font-family: 'Segoe UI', 'Sarabun', 'Leelawadee UI', sans-serif;
    font-size: 13px;
}

/* Header & Panels */
#headerBar {
    background-color: #171C26;
    border-bottom: 2px solid #232B3C;
    padding: 10px 16px;
}

#leftPanel {
    background-color: #151922;
    border-right: 1px solid #232B3C;
}

#rightPanel {
    background-color: #0F1218;
}

/* Card Containers */
QFrame.kioskCard {
    background-color: #1A212E;
    border: 1px solid #2A3449;
    border-radius: 12px;
}

/* Buttons */
QPushButton {
    background-color: #242D3E;
    border: 1px solid #364259;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    color: #F1F5F9;
}

QPushButton:hover {
    background-color: #2F3B52;
    border-color: #4C5D7F;
}

QPushButton:pressed {
    background-color: #1D2433;
}

QPushButton.primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00B4D8, stop:1 #0077B6);
    border: none;
    color: #FFFFFF;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 8px;
}

QPushButton.primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00C4EA, stop:1 #0087CE);
}

QPushButton.successBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669);
    border: none;
    color: #FFFFFF;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 8px;
}

QPushButton.successBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 #10B981);
}

QPushButton.dangerBtn {
    background-color: #EF4444;
    border: none;
    color: #FFFFFF;
}

QPushButton.dangerBtn:hover {
    background-color: #DC2626;
}

/* Badges & Labels */
QLabel.badge {
    background-color: #242D3E;
    border-radius: 6px;
    padding: 4px 10px;
    color: #38BDF8;
    font-weight: 600;
}

QLabel.badgeSuccess {
    background-color: #064E3B;
    border: 1px solid #059669;
    border-radius: 6px;
    padding: 4px 10px;
    color: #6EE7B7;
    font-weight: 600;
}

QLabel.badgeWarning {
    background-color: #451A03;
    border: 1px solid #D97706;
    border-radius: 6px;
    padding: 4px 10px;
    color: #FCD34D;
    font-weight: 600;
}

/* Sliders */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #242D3E;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #00B4D8;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #FFFFFF;
    border: 2px solid #00B4D8;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

/* Scroll Area */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #151922;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #2D3748;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4A5568;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* CheckBox */
QCheckBox {
    spacing: 8px;
    font-size: 13px;
    color: #CBD5E1;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #4B5563;
    border-radius: 4px;
    background: #1F2937;
}

QCheckBox::indicator:checked {
    background: #00B4D8;
    border-color: #00B4D8;
}
"""
