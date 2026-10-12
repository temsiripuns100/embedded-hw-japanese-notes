"""
Gallery and Photo Card Widgets for displaying matched tourist photos.
"""

import os
from typing import List, Dict, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QFrame, QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPen


class PhotoCardWidget(QFrame):
    clicked = Signal(str)
    print_clicked = Signal(str)
    checked_changed = Signal(str, bool)

    def __init__(self, record: Dict, parent=None):
        super().__init__(parent)
        self.record = record
        self.photo_path = record["photo_path"]
        self.similarity = record["similarity"]
        self.match_percentage = record.get("match_percentage", 90)

        self.setObjectName("photoCard")
        self.setStyleSheet("""
            #photoCard {
                background-color: #1A212E;
                border: 2px solid #2B364C;
                border-radius: 12px;
            }
            #photoCard:hover {
                border: 2px solid #00B4D8;
                background-color: #20293A;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedWidth(240)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Image thumbnail container
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(220, 160)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet("background-color: #0E121A; border-radius: 8px;")

        # Load thumbnail with caching / scaling
        pix = QPixmap(self.photo_path)
        if not pix.isNull():
            scaled = pix.scaled(220, 160, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            # Crop to exact 220x160 from center
            cropped = scaled.copy((scaled.width() - 220) // 2, (scaled.height() - 160) // 2, 220, 160)
            self.thumb_label.setPixmap(cropped)
        else:
            self.thumb_label.setText("📷 ไม่พบไฟล์ภาพ")

        layout.addWidget(self.thumb_label)

        # Badges row: Match % and Checkbox
        badge_row = QHBoxLayout()
        badge_row.setSpacing(6)

        self.checkbox = QCheckBox("เลือก")
        self.checkbox.setChecked(True)
        self.checkbox.toggled.connect(lambda checked: self.checked_changed.emit(self.photo_path, checked))
        badge_row.addWidget(self.checkbox)

        badge_row.addStretch()

        match_badge = QLabel(f"🎯 ตรงกัน {self.match_percentage}%")
        match_badge.setStyleSheet("""
            background-color: #064E3B;
            color: #6EE7B7;
            font-size: 11px;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid #059669;
        """)
        badge_row.addWidget(match_badge)

        layout.addLayout(badge_row)

        # File name
        fname = os.path.basename(self.photo_path)
        name_label = QLabel(fname)
        name_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        name_label.setWordWrap(False)
        name_label.setToolTip(self.photo_path)
        layout.addWidget(name_label)

        # Print button
        print_btn = QPushButton("🖨️ สั่งพิมพ์ภาพนี้")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #242D3E;
                color: #38BDF8;
                border: 1px solid #38BDF8;
                border-radius: 6px;
                padding: 6px 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #00B4D8;
                color: #FFFFFF;
            }
        """)
        print_btn.clicked.connect(lambda: self.print_clicked.emit(self.photo_path))
        layout.addWidget(print_btn)

    def mousePressEvent(self, event):
        # Click opens large viewer
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.photo_path)
        super().mousePressEvent(event)

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        self.checkbox.setChecked(checked)


class GalleryWidget(QWidget):
    photo_clicked = Signal(str)
    print_single_requested = Signal(str)
    selection_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards: List[PhotoCardWidget] = []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(12, 12, 12, 12)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)

    def set_photos(self, photo_records: List[Dict]):
        """Populates gallery with matched photo records."""
        self.clear_photos()

        columns = 3  # 3 columns layout
        for idx, rec in enumerate(photo_records):
            card = PhotoCardWidget(rec)
            card.clicked.connect(self.photo_clicked.emit)
            card.print_clicked.connect(self.print_single_requested.emit)
            card.checked_changed.connect(self._on_card_checked)

            row = idx // columns
            col = idx % columns
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)

        self.selection_changed.emit(len(self.get_selected_photos()))

    def clear_photos(self):
        """Clears all photo cards from gallery."""
        for card in self.cards:
            self.grid_layout.removeWidget(card)
            card.deleteLater()
        self.cards.clear()
        self.selection_changed.emit(0)

    def _on_card_checked(self, path: str, checked: bool):
        self.selection_changed.emit(len(self.get_selected_photos()))

    def select_all(self, select: bool = True):
        for card in self.cards:
            card.set_checked(select)
        self.selection_changed.emit(len(self.get_selected_photos()))

    def get_selected_photos(self) -> List[str]:
        return [card.photo_path for card in self.cards if card.is_checked()]
