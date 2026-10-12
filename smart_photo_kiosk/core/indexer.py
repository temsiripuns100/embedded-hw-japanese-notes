"""
Photo Indexer: Manages persistent SQLite storage of photo face embeddings,
provides incremental folder scanning and vectorized sub-millisecond similarity search.
"""

import os
import glob
import sqlite3
import numpy as np
from typing import List, Dict, Tuple, Optional, Callable
from .face_engine import FaceEngine


class PhotoIndexer:
    def __init__(self, db_path: str, face_engine: FaceEngine):
        self.db_path = db_path
        self.face_engine = face_engine

        # In-memory fast search cache
        self.matrix: np.ndarray = np.empty((0, 128), dtype=np.float32)
        self.records: List[Dict] = []  # [{photo_path, bbox, score}]

        self._init_db()
        self.load_cache_from_db()

    def _init_db(self):
        """Initializes SQLite database tables."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS photos (
                    photo_path TEXT PRIMARY KEY,
                    mtime REAL,
                    file_size INTEGER,
                    face_count INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    photo_path TEXT,
                    bbox_x INTEGER,
                    bbox_y INTEGER,
                    bbox_w INTEGER,
                    bbox_h INTEGER,
                    embedding BLOB,
                    score REAL,
                    FOREIGN KEY (photo_path) REFERENCES photos(photo_path) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_path ON faces(photo_path)")
            conn.commit()

    def load_cache_from_db(self):
        """Loads all face embeddings into an in-memory numpy matrix for instant search."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT photo_path, bbox_x, bbox_y, bbox_w, bbox_h, embedding, score
                FROM faces
            """)
            rows = cursor.fetchall()

        if not rows:
            self.matrix = np.empty((0, 128), dtype=np.float32)
            self.records = []
            return

        embeddings_list = []
        records_list = []
        for photo_path, bx, by, bw, bh, emb_blob, score in rows:
            emb = np.frombuffer(emb_blob, dtype=np.float32)
            if emb.shape == (128,):
                embeddings_list.append(emb)
                records_list.append({
                    "photo_path": photo_path,
                    "bbox": (bx, by, bw, bh),
                    "score": score
                })

        if embeddings_list:
            self.matrix = np.vstack(embeddings_list).astype(np.float32)
            self.records = records_list
        else:
            self.matrix = np.empty((0, 128), dtype=np.float32)
            self.records = []

    def get_indexed_photo_count(self) -> int:
        """Returns total distinct indexed photos count."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM photos")
            return cursor.fetchone()[0]

    def get_total_face_count(self) -> int:
        """Returns total detected faces count across all photos."""
        return len(self.records)

    def scan_and_index_folder(self, folder_path: str, progress_callback: Optional[Callable[[int, int, str], None]] = None) -> Tuple[int, int]:
        """
        Scans folder for JPEG/PNG images.
        Incrementally detects and indexes faces only for new/modified files.
        Returns: (new_or_updated_photos_count, total_photos_count)
        """
        if not os.path.exists(folder_path):
            return (0, 0)

        # Collect image files
        extensions = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
        image_files = []
        for ext in extensions:
            image_files.extend(glob.glob(os.path.join(folder_path, ext)))
        image_files = sorted(list(set(image_files)))
        total_files = len(image_files)

        if total_files == 0:
            return (0, 0)

        # Retrieve existing metadata from DB
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT photo_path, mtime, file_size FROM photos")
            db_records = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

        files_to_process = []
        for fpath in image_files:
            try:
                stat = os.stat(fpath)
                mtime = stat.st_mtime
                fsize = stat.st_size
                if fpath not in db_records or db_records[fpath] != (mtime, fsize):
                    files_to_process.append((fpath, mtime, fsize))
            except OSError:
                continue

        updated_count = 0
        if files_to_process:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for idx, (fpath, mtime, fsize) in enumerate(files_to_process):
                    if progress_callback:
                        progress_callback(idx + 1, len(files_to_process), os.path.basename(fpath))

                    # Remove existing records for this file if modified
                    cursor.execute("DELETE FROM faces WHERE photo_path = ?", (fpath,))
                    cursor.execute("DELETE FROM photos WHERE photo_path = ?", (fpath,))

                    # Extract faces
                    faces = self.face_engine.extract_faces_from_file(fpath)
                    cursor.execute(
                        "INSERT INTO photos (photo_path, mtime, file_size, face_count) VALUES (?, ?, ?, ?)",
                        (fpath, mtime, fsize, len(faces))
                    )

                    for bbox, emb, score in faces:
                        cursor.execute(
                            "INSERT INTO faces (photo_path, bbox_x, bbox_y, bbox_w, bbox_h, embedding, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (fpath, bbox[0], bbox[1], bbox[2], bbox[3], emb.tobytes(), score)
                        )

                    updated_count += 1
                conn.commit()

            # Refresh in-memory matrix
            self.load_cache_from_db()

        return (updated_count, total_files)

    def search_by_face(self, query_feat: np.ndarray, threshold: float = 0.38, top_k: int = 50) -> List[Dict]:
        """
        Fast vectorized search against all cached faces.
        Returns matching photos grouped by photo_path, sorted by highest similarity.
        """
        if self.matrix.shape[0] == 0 or query_feat is None:
            return []

        # Vectorized dot product cosine similarity: (N,)
        sims = self.face_engine.match_against_features(query_feat, self.matrix)

        # Filter matches above threshold
        matched_indices = np.where(sims >= threshold)[0]
        if len(matched_indices) == 0:
            return []

        # Group matches by photo_path (take max similarity per photo)
        photo_matches: Dict[str, Dict] = {}
        for idx in matched_indices:
            sim = float(sims[idx])
            rec = self.records[idx]
            photo_path = rec["photo_path"]

            # Calculate a user-friendly match percentage (0.35 -> ~70%, 0.60 -> ~95%)
            match_pct = int(min(100, max(0, (sim - 0.20) / 0.50 * 100)))

            if photo_path not in photo_matches or sim > photo_matches[photo_path]["similarity"]:
                photo_matches[photo_path] = {
                    "photo_path": photo_path,
                    "similarity": sim,
                    "match_percentage": match_pct,
                    "bbox": rec["bbox"]
                }

        results = list(photo_matches.values())
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
