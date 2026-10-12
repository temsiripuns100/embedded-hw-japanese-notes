"""
Photo Viewer Dialog: High-resolution preview modal with print confirmation.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap


class PhotoViewerDialog(QDialog):
    print_requested = Signal(str)

    def __init__(self, photo_path: str, parent=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.setWindowTitle(f"ดูตัวอย่างภาพ - {os.path.basename(photo_path)}")
        self.resize(800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #11151F;
                border: 2px solid #2A3449;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Image view
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #0A0D14; border-radius: 8px;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        pix = QPixmap(self.photo_path)
        if not pix.isNull():
            scaled = pix.scaled(760, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("ไม่สามารถโหลดภาพความละเอียดสูงได้")

        layout.addWidget(self.image_label)

        # Footer row
        footer = QHBoxLayout()
        info_label = QLabel(f"📁 {self.photo_path}")
        info_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        footer.addWidget(info_label)

        footer.addStretch()

        print_btn = QPushButton("🖨️ สั่งพิมพ์ภาพนี้ (Print)")
        print_btn.setProperty("class", "successBtn")
        print_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669);
            color: white; font-weight: bold; padding: 10px 20px; border-radius: 8px;
        """)
        print_btn.clicked.connect(self._on_print)
        footer.addWidget(print_btn)

        close_btn = QPushButton("ปิด (Close)")
        close_btn.setStyleSheet("""
            background-color: #242D3E; color: #CBD5E1; padding: 10px 18px; border-radius: 8px;
        """)
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)

        layout.addLayout(footer)

    def _on_print(self):
        self.print_requested.emit(self.photo_path)
        self.accept()
