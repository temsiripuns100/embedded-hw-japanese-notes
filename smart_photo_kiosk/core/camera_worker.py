"""
Camera Worker: QThread running OpenCV VideoCapture and real-time YuNet face detection.
Renders HUD overlays (corner brackets, landmarks, status) and emits signals for UI.
"""

import cv2
import numpy as np
import time
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from .face_engine import FaceEngine


class CameraWorker(QThread):
    # Signals
    frame_ready = Signal(QImage)
    face_detected = Signal(np.ndarray, np.ndarray)  # (face_crop_bgr, embedding_128d)
    face_cleared = Signal()

    def __init__(self, face_engine: FaceEngine, camera_index: int = 0, parent=None):
        super().__init__(parent)
        self.face_engine = face_engine
        self.camera_index = camera_index
        self._running = False
        self._paused = False

        # Throttling face recognition queries to avoid flickering
        self.last_query_time = 0.0
        self.query_interval = 0.4  # query every 400ms when face is steady
        self.last_face_time = 0.0
        self.no_face_timeout = 1.8  # clear after 1.8s of no faces

    def set_camera_index(self, index: int):
        self.camera_index = index

    def pause_capture(self, pause: bool):
        self._paused = pause

    def stop(self):
        self._running = False
        self.wait(1000)

    def run(self):
        self._running = True
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            # Fallback to default backend
            cap = cv2.VideoCapture(self.camera_index)

        # Set decent resolution for Kiosk camera feed
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while self._running:
            if self._paused:
                time.sleep(0.05)
                continue

            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.03)
                continue

            # Mirror frame horizontally for natural webcam user experience
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            # Detect faces on frame
            faces = self.face_engine.extract_faces_from_image(frame, max_detect_dim=640)

            now = time.time()
            if faces:
                self.last_face_time = now
                # Pick the largest face (closest to camera)
                faces.sort(key=lambda item: item[0][2] * item[0][3], reverse=True)
                primary_bbox, primary_feat, primary_score = faces[0]

                # Draw fancy Kiosk HUD over all detected faces
                for (fx, fy, fw, fh), feat, score in faces:
                    self._draw_hud(frame, fx, fy, fw, fh, score)

                # Emit face query if interval passed
                if now - self.last_query_time >= self.query_interval:
                    self.last_query_time = now
                    # Crop face thumbnail for preview
                    pad_x = int(fw * 0.15)
                    pad_y = int(fh * 0.20)
                    y1 = max(0, fy - pad_y)
                    y2 = min(h, fy + fh + pad_y)
                    x1 = max(0, fx - pad_x)
                    x2 = min(w, fx + fw + pad_x)
                    face_crop = frame[y1:y2, x1:x2].copy()
                    self.face_detected.emit(face_crop, primary_feat)
            else:
                # Check if face was lost for more than timeout
                if now - self.last_face_time > self.no_face_timeout and self.last_face_time > 0:
                    self.last_face_time = 0.0
                    self.face_cleared.emit()

            # Convert BGR OpenCV frame to QImage for PySide6 display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_img = QImage(
                rgb_frame.data,
                w,
                h,
                w * 3,
                QImage.Format.Format_RGB888
            )
            self.frame_ready.emit(q_img.copy())

            # Maintain ~30 FPS
            time.sleep(0.015)

        cap.release()

    def _draw_hud(self, frame: np.ndarray, x: int, y: int, w: int, h: int, score: float):
        """Draws a high-tech corner-bracket target box and status label."""
        color = (0, 255, 200)  # Neon Cyan/Green BGR
        thickness = 2
        corner_len = min(20, w // 4, h // 4)

        # Top-left corner
        cv2.line(frame, (x, y), (x + corner_len, y), color, thickness)
        cv2.line(frame, (x, y), (x, y + corner_len), color, thickness)

        # Top-right corner
        cv2.line(frame, (x + w, y), (x + w - corner_len, y), color, thickness)
        cv2.line(frame, (x + w, y), (x + w, y + corner_len), color, thickness)

        # Bottom-left corner
        cv2.line(frame, (x, y + h), (x + corner_len, y + h), color, thickness)
        cv2.line(frame, (x, y + h), (x, y + h - corner_len), color, thickness)

        # Bottom-right corner
        cv2.line(frame, (x + w, y + h), (x + w - corner_len, y + h), color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_len), color, thickness)

        # Light box around face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 180, 150), 1)

        # Label tag
        label = f"FACE {int(score * 100)}%"
        cv2.putText(frame, label, (x, max(18, y - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
