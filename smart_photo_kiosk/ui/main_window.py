"""
Main Kiosk Window: The unified user interface for the Smart Tourist Photo Kiosk.
Integrates live camera feed, real-time face matching, and photo printing.
"""

import os
import cv2
import numpy as np
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QSlider, QComboBox, QMessageBox, QStackedWidget,
    QProgressBar, QSplitter
)
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPixmap, QImage

try:
    from core.face_engine import FaceEngine
    from core.indexer import PhotoIndexer
    from core.camera_worker import CameraWorker
    from ui.styles import MAIN_STYLESHEET
    from ui.gallery_widget import GalleryWidget
    from ui.photo_viewer_dialog import PhotoViewerDialog
except ImportError:
    from ..core.face_engine import FaceEngine
    from ..core.indexer import PhotoIndexer
    from ..core.camera_worker import CameraWorker
    from .styles import MAIN_STYLESHEET
    from .gallery_widget import GalleryWidget
    from .photo_viewer_dialog import PhotoViewerDialog


class MainWindow(QMainWindow):
    def __init__(self, face_engine: FaceEngine, indexer: PhotoIndexer, photos_dir: str):
        super().__init__()
        self.face_engine = face_engine
        self.indexer = indexer
        self.photos_dir = os.path.abspath(photos_dir)

        self.setWindowTitle("Smart Tour Photo Kiosk - ระบบค้นหาและพิมพ์ภาพท่องเที่ยวอัตโนมัติ")
        self.resize(1280, 800)
        self.setStyleSheet(MAIN_STYLESHEET)

        # Matching threshold state
        self.threshold = 0.36

        # Build UI
        self._init_ui()

        # Start camera worker thread
        self.camera_worker = CameraWorker(self.face_engine, camera_index=0)
        self.camera_worker.frame_ready.connect(self._on_camera_frame)
        self.camera_worker.face_detected.connect(self._on_face_detected)
        self.camera_worker.face_cleared.connect(self._on_face_cleared)
        self.camera_worker.start()

        # Initial folder scan after UI shows
        QTimer.singleShot(500, self._initial_scan)

        # Background folder watcher (auto checks for new photos every 3 seconds)
        self.watch_timer = QTimer(self)
        self.watch_timer.setInterval(3000)
        self.watch_timer.timeout.connect(self._auto_check_folder)
        self.watch_timer.start()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_vbox = QVBoxLayout(central_widget)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        # 1. Header Bar
        main_vbox.addWidget(self._create_header_bar())

        # 2. Main Body Splitter (Left: Camera & Controls, Right: Gallery)
        body_splitter = QSplitter(Qt.Horizontal)
        body_splitter.setHandleWidth(1)

        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        body_splitter.addWidget(left_panel)
        body_splitter.addWidget(right_panel)
        body_splitter.setStretchFactor(0, 0)
        body_splitter.setStretchFactor(1, 1)

        main_vbox.addWidget(body_splitter)

    def _create_header_bar(self) -> QWidget:
        header = QFrame()
        header.setObjectName("headerBar")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(16)

        # App Title & Icon
        title_box = QVBoxLayout()
        title = QLabel("📸 SMART PHOTO KIOSK")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8; letter-spacing: 1px;")
        subtitle = QLabel("ระบบจดจำใบหน้าและค้นหาภาพท่องเที่ยวอัตโนมัติ")
        subtitle.setStyleSheet("font-size: 11px; color: #94A3B8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        layout.addStretch()

        # Status Badges
        self.folder_badge = QLabel(f"📁 {os.path.basename(self.photos_dir)}")
        self.folder_badge.setProperty("class", "badge")
        self.folder_badge.setToolTip(self.photos_dir)
        layout.addWidget(self.folder_badge)

        self.photos_count_badge = QLabel("🖼️ 0 ภาพ")
        self.photos_count_badge.setProperty("class", "badge")
        layout.addWidget(self.photos_count_badge)

        self.faces_count_badge = QLabel("👤 0 ใบหน้า")
        self.faces_count_badge.setProperty("class", "badge")
        layout.addWidget(self.faces_count_badge)

        # Header Buttons
        change_folder_btn = QPushButton("📁 เลือกโฟลเดอร์")
        change_folder_btn.clicked.connect(self._on_change_folder)
        layout.addWidget(change_folder_btn)

        rescan_btn = QPushButton("🔄 สแกนใหม่")
        rescan_btn.clicked.connect(self._rescan_folder)
        layout.addWidget(rescan_btn)

        test_sim_btn = QPushButton("🧪 ทดสอบด้วยภาพ")
        test_sim_btn.setStyleSheet("background-color: #3730A3; color: #C7D2FE; font-weight: bold;")
        test_sim_btn.setToolTip("เลือกรูปถ่ายนักท่องเที่ยว 1 รูปเพื่อจำลองคนเดินผ่านกล้อง")
        test_sim_btn.clicked.connect(self._on_simulate_test_face)
        layout.addWidget(test_sim_btn)

        return header

    def _create_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("leftPanel")
        panel.setFixedWidth(380)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Section Title
        sec_title = QLabel("🎥 กล้องตรวจจับลูกค้า (Kiosk Sensor)")
        sec_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F1F5F9;")
        layout.addWidget(sec_title)

        # Video Stream Viewport
        self.video_label = QLabel()
        self.video_label.setFixedSize(348, 260)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            background-color: #0A0D14;
            border: 2px solid #242D3E;
            border-radius: 12px;
        """)
        self.video_label.setText("กำลังเชื่อมต่อกล้อง...")
        layout.addWidget(self.video_label)

        # Detection Status Banner
        self.status_banner = QLabel("👀 กำลังรอนักท่องเที่ยวเดินผ่านหน้ากล้อง...")
        self.status_banner.setAlignment(Qt.AlignCenter)
        self.status_banner.setStyleSheet("""
            background-color: #1A212E;
            color: #94A3B8;
            font-size: 12px;
            font-weight: 600;
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid #2B364C;
        """)
        layout.addWidget(self.status_banner)

        # Customer Snapshot Box
        snap_box = QFrame()
        snap_box.setProperty("class", "kioskCard")
        snap_layout = QHBoxLayout(snap_box)
        snap_layout.setContentsMargins(12, 10, 12, 10)

        self.face_thumb = QLabel()
        self.face_thumb.setFixedSize(70, 70)
        self.face_thumb.setAlignment(Qt.AlignCenter)
        self.face_thumb.setStyleSheet("background-color: #0F131C; border-radius: 8px; border: 1px solid #2A3449;")
        self.face_thumb.setText("👤")
        snap_layout.addWidget(self.face_thumb)

        snap_info = QVBoxLayout()
        self.snap_name = QLabel("ใบหน้าปัจจุบัน")
        self.snap_name.setStyleSheet("font-weight: bold; color: #F1F5F9;")
        self.snap_details = QLabel("ยังไม่พบใบหน้า")
        self.snap_details.setStyleSheet("font-size: 11px; color: #64748B;")
        snap_info.addWidget(self.snap_name)
        snap_info.addWidget(self.snap_details)
        snap_layout.addLayout(snap_info)

        layout.addWidget(snap_box)

        # Settings: Threshold Slider
        thresh_card = QFrame()
        thresh_card.setProperty("class", "kioskCard")
        t_layout = QVBoxLayout(thresh_card)
        t_layout.setContentsMargins(12, 12, 12, 12)
        t_layout.setSpacing(8)

        t_header = QHBoxLayout()
        t_label = QLabel("ความเข้มงวดในการตรวจจับ (Threshold)")
        t_label.setStyleSheet("font-size: 11px; color: #CBD5E1;")
        self.t_val_label = QLabel(f"{self.threshold:.2f}")
        self.t_val_label.setStyleSheet("font-weight: bold; color: #38BDF8;")
        t_header.addWidget(t_label)
        t_header.addStretch()
        t_header.addWidget(self.t_val_label)
        t_layout.addLayout(t_header)

        self.thresh_slider = QSlider(Qt.Horizontal)
        self.thresh_slider.setRange(25, 55)  # 0.25 to 0.55
        self.thresh_slider.setValue(int(self.threshold * 100))
        self.thresh_slider.valueChanged.connect(self._on_threshold_changed)
        t_layout.addWidget(self.thresh_slider)

        layout.addWidget(thresh_card)

        layout.addStretch()

        # Camera Toggle Button
        self.cam_toggle_btn = QPushButton("⏸️ หยุดการทำงานกล้อง")
        self.cam_toggle_btn.clicked.connect(self._on_toggle_camera)
        layout.addWidget(self.cam_toggle_btn)

        return panel

    def _create_right_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("rightPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Gallery Action Bar
        action_bar = QHBoxLayout()
        self.results_title = QLabel("✨ กรุณายืนหน้ากล้อง หรือจำลองภาพเพื่อค้นหา")
        self.results_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F1F5F9;")
        action_bar.addWidget(self.results_title)

        action_bar.addStretch()

        self.select_all_btn = QPushButton("เลือกทั้งหมด")
        self.select_all_btn.clicked.connect(lambda: self.gallery.select_all(True))
        self.select_all_btn.setEnabled(False)
        action_bar.addWidget(self.select_all_btn)

        self.print_batch_btn = QPushButton("🖨️ สั่งพิมพ์ภาพที่เลือก (0 ใบ)")
        self.print_batch_btn.setProperty("class", "successBtn")
        self.print_batch_btn.setEnabled(False)
        self.print_batch_btn.clicked.connect(self._on_print_batch)
        action_bar.addWidget(self.print_batch_btn)

        clear_btn = QPushButton("ล้างผลลัพธ์")
        clear_btn.clicked.connect(self._clear_results)
        action_bar.addWidget(clear_btn)

        layout.addLayout(action_bar)

        # Stacked display (Empty State vs Gallery)
        self.stack = QStackedWidget()

        # Empty State
        empty_widget = QWidget()
        e_layout = QVBoxLayout(empty_widget)
        e_layout.setAlignment(Qt.AlignCenter)
        e_layout.setSpacing(12)

        e_icon = QLabel("📸")
        e_icon.setStyleSheet("font-size: 54px;")
        e_icon.setAlignment(Qt.AlignCenter)
        e_title = QLabel("ยินดีต้อนรับสู่ Smart Photo Kiosk")
        e_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #E2E8F0;")
        e_title.setAlignment(Qt.AlignCenter)
        e_desc = QLabel("เมื่อนักท่องเที่ยวเดินผ่านหน้ากล้อง ระบบจะตรวจจับใบหน้า\nและดึงภาพถ่ายที่ตรงกันขึ้นมาแสดงบนหน้าร้านทันที")
        e_desc.setStyleSheet("font-size: 13px; color: #94A3B8; line-height: 1.5;")
        e_desc.setAlignment(Qt.AlignCenter)

        e_layout.addWidget(e_icon)
        e_layout.addWidget(e_title)
        e_layout.addWidget(e_desc)
        self.stack.addWidget(empty_widget)

        # Gallery Widget
        self.gallery = GalleryWidget()
        self.gallery.photo_clicked.connect(self._on_photo_clicked)
        self.gallery.print_single_requested.connect(self._on_print_single)
        self.gallery.selection_changed.connect(self._on_selection_changed)
        self.stack.addWidget(self.gallery)

        layout.addWidget(self.stack)

        return panel

    # -------------------------------------------------------------
    # Slots & Handlers
    # -------------------------------------------------------------
    @Slot(QImage)
    def _on_camera_frame(self, q_img: QImage):
        # Scale to fit video viewport smoothly
        scaled = q_img.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(QPixmap.fromImage(scaled))

    @Slot(np.ndarray, np.ndarray)
    def _on_face_detected(self, face_crop_bgr: np.ndarray, feat: np.ndarray):
        # Update customer snapshot
        rgb_crop = cv2.cvtColor(face_crop_bgr, cv2.COLOR_BGR2RGB)
        ch, cw = rgb_crop.shape[:2]
        q_crop = QImage(rgb_crop.data, cw, ch, cw * 3, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(q_crop).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.face_thumb.setPixmap(pix)

        self.status_banner.setText("✨ ตรวจพบคุณลูกค้า! กำลังจับคู่ภาพ...")
        self.status_banner.setStyleSheet("""
            background-color: #064E3B; color: #6EE7B7; font-size: 12px;
            font-weight: bold; padding: 8px 12px; border-radius: 8px; border: 1px solid #059669;
        """)

        # Execute instant vector search against indexed photos!
        matches = self.indexer.search_by_face(feat, threshold=self.threshold)
        self._display_search_results(matches)

    @Slot()
    def _on_face_cleared(self):
        self.status_banner.setText("👀 กำลังรอนักท่องเที่ยวเดินผ่านหน้ากล้อง...")
        self.status_banner.setStyleSheet("""
            background-color: #1A212E; color: #94A3B8; font-size: 12px;
            font-weight: 600; padding: 8px 12px; border-radius: 8px; border: 1px solid #2B364C;
        """)

    def _display_search_results(self, matches: List[Dict]):
        if not matches:
            self.results_title.setText("🔍 ตรวจพบใบหน้า แต่ยังไม่มีรูปที่ตรงกันในระบบ")
            self.snap_details.setText("ไม่พบรูปที่ตรงกัน")
            return

        self.results_title.setText(f"🎉 พบภาพถ่ายของคุณลูกค้าทั้งหมด {len(matches)} ภาพ!")
        self.snap_details.setText(f"พบภาพตรงกัน {len(matches)} ภาพ")

        self.gallery.set_photos(matches)
        self.stack.setCurrentIndex(1)
        self.select_all_btn.setEnabled(True)

    def _on_selection_changed(self, count: int):
        self.print_batch_btn.setEnabled(count > 0)
        self.print_batch_btn.setText(f"🖨️ สั่งพิมพ์ภาพที่เลือก ({count} ใบ)")

    def _clear_results(self):
        self.gallery.clear_photos()
        self.stack.setCurrentIndex(0)
        self.results_title.setText("✨ กรุณายืนหน้ากล้อง หรือจำลองภาพเพื่อค้นหา")
        self.select_all_btn.setEnabled(False)
        self.print_batch_btn.setEnabled(False)
        self.face_thumb.setText("👤")
        self.snap_details.setText("ยังไม่พบใบหน้า")

    def _on_threshold_changed(self, val: int):
        self.threshold = val / 100.0
        self.t_val_label.setText(f"{self.threshold:.2f}")

    def _on_toggle_camera(self):
        if self.camera_worker._paused:
            self.camera_worker.pause_capture(False)
            self.cam_toggle_btn.setText("⏸️ หยุดการทำงานกล้อง")
        else:
            self.camera_worker.pause_capture(True)
            self.cam_toggle_btn.setText("▶️ เริ่มการทำงานกล้อง")

    def _on_photo_clicked(self, photo_path: str):
        dialog = PhotoViewerDialog(photo_path, self)
        dialog.print_requested.connect(self._on_print_single)
        dialog.exec()

    def _on_print_single(self, photo_path: str):
        QMessageBox.information(
            self,
            "สั่งพิมพ์สำเร็จ (Print Sent)",
            f"🖨️ ส่งคำสั่งพิมพ์ภาพไปยังเครื่องพิมพ์แล้ว:\n{os.path.basename(photo_path)}\n\n(ขนาด: 4x6 นิ้ว / ความละเอียดสูง)"
        )

    def _on_print_batch(self):
        selected = self.gallery.get_selected_photos()
        if not selected:
            return

        filenames = "\n".join([f"- {os.path.basename(p)}" for p in selected[:5]])
        if len(selected) > 5:
            filenames += f"\n... และอีก {len(selected) - 5} ภาพ"

        QMessageBox.information(
            self,
            "สั่งพิมพ์สำเร็จ (Batch Print Sent)",
            f"🖨️ ส่งคำสั่งพิมพ์ทั้งหมด {len(selected)} ภาพเรียบร้อยแล้ว!\n\n{filenames}"
        )

    def _on_change_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์เก็บภาพถ่าย", self.photos_dir)
        if folder:
            self.photos_dir = folder
            self.folder_badge.setText(f"📁 {os.path.basename(self.photos_dir)}")
            self.folder_badge.setToolTip(self.photos_dir)
            self._rescan_folder()

    def _initial_scan(self):
        self._rescan_folder()

    def _rescan_folder(self):
        new_or_updated, total = self.indexer.scan_and_index_folder(self.photos_dir)
        total_photos = self.indexer.get_indexed_photo_count()
        total_faces = self.indexer.get_total_face_count()

        self.photos_count_badge.setText(f"🖼️ {total_photos} ภาพ")
        self.faces_count_badge.setText(f"👤 {total_faces} ใบหน้า")

    def _auto_check_folder(self):
        """Silently indexes new photos dropped into the folder by photographers."""
        new_or_updated, _ = self.indexer.scan_and_index_folder(self.photos_dir)
        if new_or_updated > 0:
            total_photos = self.indexer.get_indexed_photo_count()
            total_faces = self.indexer.get_total_face_count()
            self.photos_count_badge.setText(f"🖼️ {total_photos} ภาพ")
            self.faces_count_badge.setText(f"👤 {total_faces} ใบหน้า")

    def _on_simulate_test_face(self):
        """Allows testing without webcam by selecting an image of a person."""
        fpath, _ = QFileDialog.getOpenFileName(
            self, "เลือกภาพใบหน้าสำหรับทดสอบ", self.photos_dir,
            "Images (*.jpg *.jpeg *.png *.JPG *.PNG)"
        )
        if not fpath:
            return

        faces = self.face_engine.extract_faces_from_file(fpath)
        if not faces:
            QMessageBox.warning(self, "ไม่พบใบหน้า", "ไม่พบใบหน้าในภาพที่เลือก กรุณาเลือกภาพที่เห็นใบหน้าชัดเจน")
            return

        # Pick first face
        bbox, feat, score = faces[0]

        # Load image and crop face
        img = cv2.imread(fpath)
        if img is not None:
            x, y, w, h = bbox
            crop = img[y:y+h, x:x+w]
            self._on_face_detected(crop, feat)
        else:
            dummy_crop = np.zeros((100, 100, 3), dtype=np.uint8)
            self._on_face_detected(dummy_crop, feat)

    def closeEvent(self, event):
        self.camera_worker.stop()
        super().closeEvent(event)
