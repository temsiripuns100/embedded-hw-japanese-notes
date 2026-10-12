"""
Smart Tourist Photo Kiosk - Application Entrypoint
Run: python main.py
"""

import sys
import os
from PySide6.QtWidgets import QApplication

# Ensure current directory is on python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.face_engine import FaceEngine
from core.indexer import PhotoIndexer
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Photo Kiosk")
    app.setOrganizationName("TourAI")

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, "models")
    yunet_path = os.path.join(models_dir, "face_detection_yunet_2023mar.onnx")
    sface_path = os.path.join(models_dir, "face_recognition_sface_2021dec.onnx")

    db_path = os.path.join(base_dir, "data", "photo_index.db")
    photos_dir = os.path.join(base_dir, "demo_photos")

    os.makedirs(photos_dir, exist_ok=True)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print("🚀 Initializing Face Engine...")
    face_engine = FaceEngine(yunet_path, sface_path)

    print("📦 Initializing Photo Indexer Database...")
    indexer = PhotoIndexer(db_path, face_engine)

    print("🖥️ Launching Kiosk UI...")
    window = MainWindow(face_engine, indexer, photos_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
