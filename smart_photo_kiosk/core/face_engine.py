"""
Face Engine: High-performance Face Detection (YuNet) & Recognition (SFace) using OpenCV DNN.
Optimized for high-resolution DSLR photos & real-time video streams.
"""

import os
import cv2
import numpy as np
import threading
from typing import List, Dict, Tuple, Optional


class FaceRecord:
    """Represents a detected face in a photo."""
    def __init__(self, photo_path: str, bbox: Tuple[int, int, int, int], embedding: np.ndarray, score: float):
        self.photo_path = photo_path
        self.bbox = bbox  # (x, y, w, h)
        self.embedding = embedding  # (128,) normalized float32
        self.score = score


class FaceEngine:
    def __init__(self, yunet_model_path: str, sface_model_path: str, score_threshold: float = 0.75):
        if not os.path.exists(yunet_model_path):
            raise FileNotFoundError(f"YuNet model not found: {yunet_model_path}")
        if not os.path.exists(sface_model_path):
            raise FileNotFoundError(f"SFace model not found: {sface_model_path}")

        self.yunet_model_path = yunet_model_path
        self.sface_model_path = sface_model_path
        self.score_threshold = score_threshold
        self._lock = threading.Lock()

        # Initialize detector with default dummy size
        self.detector = cv2.FaceDetectorYN.create(
            model=self.yunet_model_path,
            config="",
            input_size=(320, 320),
            score_threshold=self.score_threshold,
            nms_threshold=0.3,
            top_k=5000
        )

        # Initialize recognizer
        self.recognizer = cv2.FaceRecognizerSF.create(
            model=self.sface_model_path,
            config="",
            backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
            target_id=cv2.dnn.DNN_TARGET_CPU
        )

    def extract_faces_from_image(self, img_bgr: np.ndarray, max_detect_dim: int = 1280) -> List[Tuple[Tuple[int, int, int, int], np.ndarray, float]]:
        """
        Detects all faces in an image, extracts 128D embeddings for each face.
        Returns: list of [(x, y, w, h), embedding_vector, confidence_score]
        """
        if img_bgr is None or img_bgr.size == 0:
            return []

        orig_h, orig_w = img_bgr.shape[:2]

        # For large photos (e.g. 24MP DSLR), downsample for detection speed
        scale = 1.0
        if max(orig_h, orig_w) > max_detect_dim:
            scale = max_detect_dim / float(max(orig_h, orig_w))
            detect_w = int(orig_w * scale)
            detect_h = int(orig_h * scale)
            detect_img = cv2.resize(img_bgr, (detect_w, detect_h), interpolation=cv2.INTER_AREA)
        else:
            detect_w, detect_h = orig_w, orig_h
            detect_img = img_bgr

        with self._lock:
            self.detector.setInputSize((detect_w, detect_h))
            status, faces = self.detector.detect(detect_img)

            if faces is None or len(faces) == 0:
                return []

            results = []
            for face in faces:
                # face format: [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt, x_rcm, y_rcm, x_lcm, y_lcm, score]
                score = float(face[-1])
                if score < self.score_threshold:
                    continue

                # Scale face landmarks back to original image coordinates if scaled
                if scale != 1.0:
                    face_orig = face.copy()
                    face_orig[:-1] = face_orig[:-1] / scale
                else:
                    face_orig = face

                x, y, w, h = int(face_orig[0]), int(face_orig[1]), int(face_orig[2]), int(face_orig[3])
                # Clamp coordinates to image boundaries
                x = max(0, x)
                y = max(0, y)
                w = min(orig_w - x, w)
                h = min(orig_h - y, h)

                if w <= 10 or h <= 10:
                    continue

                try:
                    # Align and crop face from original image
                    aligned_face = self.recognizer.alignCrop(img_bgr, face_orig)
                    raw_feat = self.recognizer.feature(aligned_face)  # shape (1, 128)
                    feat = raw_feat.flatten()

                    # Normalize to unit length for ultra-fast dot product cosine similarity
                    norm = np.linalg.norm(feat)
                    if norm > 1e-6:
                        feat = feat / norm

                    results.append(((x, y, w, h), feat, score))
                except Exception as e:
                    # Skip if face alignment fails (e.g. extreme angle on boundary)
                    continue

            return results

    def extract_faces_from_file(self, file_path: str) -> List[Tuple[Tuple[int, int, int, int], np.ndarray, float]]:
        """Reads image file supporting Thai/Unicode filenames on Windows, then extracts faces."""
        if not os.path.exists(file_path):
            return []
        try:
            # Use imdecode to support Unicode / Thai characters in file paths on Windows
            with open(file_path, "rb") as f:
                bytes_data = bytearray(f.read())
            nparr = np.asarray(bytes_data, dtype=np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return []
            return self.extract_faces_from_image(img)
        except Exception:
            return []

    @staticmethod
    def compute_similarity(feat1: np.ndarray, feat2: np.ndarray) -> float:
        """Computes Cosine Similarity between two 128D vectors. (1.0 = identical, 0.0 = unrelated)."""
        # Both are already unit normalized
        return float(np.dot(feat1, feat2))

    @staticmethod
    def match_against_features(query_feat: np.ndarray, db_matrix: np.ndarray) -> np.ndarray:
        """
        Matrix dot product: query_feat (128,) @ db_matrix (N, 128).T -> (N,) similarities.
        Runs in < 1ms for tens of thousands of faces!
        """
        if db_matrix.size == 0:
            return np.array([], dtype=np.float32)
        return np.dot(db_matrix, query_feat)
