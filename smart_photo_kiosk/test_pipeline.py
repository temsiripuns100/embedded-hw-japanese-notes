import sys
import os

sys.path.insert(0, os.path.abspath("smart_photo_kiosk"))
from core.face_engine import FaceEngine
from core.indexer import PhotoIndexer

yunet_path = "smart_photo_kiosk/models/face_detection_yunet_2023mar.onnx"
sface_path = "smart_photo_kiosk/models/face_recognition_sface_2021dec.onnx"
db_path = "smart_photo_kiosk/data/photo_index.db"
photos_dir = "smart_photo_kiosk/demo_photos"

engine = FaceEngine(yunet_path, sface_path)
indexer = PhotoIndexer(db_path, engine)

updated, total = indexer.scan_and_index_folder(photos_dir)
print(f"Indexed: {updated}/{total} photos")
print("Total photos in DB:", indexer.get_indexed_photo_count())
print("Total faces in DB:", indexer.get_total_face_count())

# Test query with Person A (tourist_A_photo1.jpg)
query_faces = engine.extract_faces_from_file("smart_photo_kiosk/demo_photos/tourist_A_photo1.jpg")
print("Query faces detected in sample:", len(query_faces))

if query_faces:
    feat = query_faces[0][1]
    matches = indexer.search_by_face(feat, threshold=0.36)
    print("\n--- MATCH RESULTS FOR PERSON A ---")
    for m in matches:
        print(f"File: {os.path.basename(m['photo_path'])}, Similarity: {m['similarity']:.4f}, Match: {m['match_percentage']}%")

# Test query with Person B (tourist_B_photo1.jpg)
query_b = engine.extract_faces_from_file("smart_photo_kiosk/demo_photos/tourist_B_photo1.jpg")
if query_b:
    feat_b = query_b[0][1]
    matches_b = indexer.search_by_face(feat_b, threshold=0.36)
    print("\n--- MATCH RESULTS FOR PERSON B ---")
    for m in matches_b:
        print(f"File: {os.path.basename(m['photo_path'])}, Similarity: {m['similarity']:.4f}, Match: {m['match_percentage']}%")
