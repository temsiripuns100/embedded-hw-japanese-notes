# 📘 บทเรียนเชิงวิศวกรรม: การสร้างระบบค้นหาและพิมพ์ภาพถ่ายท่องเที่ยวอัตโนมัติด้วย Edge AI
## (Building an Edge AI Smart Photo Kiosk with Python, OpenCV DNN & PySide6)

---

## 📑 สารบัญ (Table of Contents)
1. [บทนำและโจทย์ทางวิศวกรรม (The Engineering Challenge)](#1-บทนำและโจทย์ทางวิศวกรรม)
2. [สถาปัตยกรรมระบบภาพรวม (System Architecture Overview)](#2-สถาปัตยกรรมระบบภาพรวม)
3. [ทฤษฎี Computer Vision & Face Recognition](#3-ทฤษฎี-computer-vision--face-recognition)
   - [3.1 การตรวจจับใบหน้า (Face Detection: YuNet)](#31-การตรวจจับใบหน้า-face-detection-yunet)
   - [3.2 การปรับระนาบใบหน้า (Face Alignment & Landmark Normalization)](#32-การปรับระนาบใบหน้า-face-alignment)
   - [3.3 การแปลงใบหน้าเป็นเวกเตอร์ (Face Embedding: SFace)](#33-การแปลงใบหน้าเป็นเวกเตอร์-face-embedding-sface)
   - [3.4 การจับคู่และค้นหาเวกเตอร์ความเร็วสูง (Vectorized Cosine Similarity)](#34-การจับคู่และค้นหาเวกเตอร์ความเร็วสูง)
4. [การออกแบบสถาปัตยกรรมซอฟต์แวร์ (Software Engineering & Concurrency)](#4-การออกแบบสถาปัตยกรรมซอฟต์แวร์)
   - [4.1 ปัญหา Multi-threading Race Condition บน OpenCV DNN](#41-ปัญหา-multi-threading-race-condition)
   - [4.2 การดัชนีรูปภาพแบบเพิ่มขึ้นทีละส่วน (Incremental Indexing & Caching ด้วย SQLite)](#42-การดัชนีรูปภาพแบบ-incremental)
   - [4.3 โครงสร้าง Signal & Slot ใน PySide6 (Event-Driven Architecture)](#43-โครงสร้าง-signal--slot-ใน-pyside6)
5. [เจาะลึกการทำงานของโค้ดหลัก (Code Walkthrough)](#5-เจาะลึกการทำงานของโค้ดหลัก)
   - [5.1 Face Engine: ตรวจจับและสกัด Feature](#51-face-engine)
   - [5.2 Photo Indexer: คลังเวกเตอร์และการคำนวณแบบ Matrix](#52-photo-indexer)
   - [5.3 Camera Worker: การประมวลผลสตรีมวิดีโอแบบเรียลไทม์](#53-camera-worker)
6. [โจทย์หน้างานจริงและการแก้ปัญหา (Production Engineering & Best Practices)](#6-โจทย์หน้างานจริงและการแก้ปัญหา)
   - [6.1 การจัดการรูปถ่ายความละเอียดสูง (DSLR 24MP–48MP)](#61-การจัดการรูปถ่ายความละเอียดสูง)
   - [6.2 การตรวจจับรูปภาพแบบกลุ่ม (Group & Family Photos)](#62-การตรวจจับรูปภาพแบบกลุ่ม)
   - [6.3 สภาพแสง มุมกล้อง และการปรับแต่ง Sensitivity Threshold](#63-สภาพแสง-มุมกล้อง-และ-threshold)
   - [6.4 การเชื่อมต่อเครื่องพิมพ์ภาพถ่ายและการบริหารจัดการคิวพิมพ์](#64-การเชื่อมต่อเครื่องพิมพ์ภาพถ่าย)
   - [6.5 ความปลอดภัยของข้อมูลและความเป็นส่วนตัว (Privacy & PDPA)](#65-ความเป็นส่วนตัวและ-pdpa)
7. [แบบฝึกหัดทบทวนและแนวทางต่อยอด (Exercises & Further Development)](#7-แบบฝึกหัดทบทวนและแนวทางต่อยอด)

---

## 1. บทนำและโจทย์ทางวิศวกรรม

### บริบททางธุรกิจ (Business Context)
ในแหล่งท่องเที่ยว เช่น สวนสนุก สวนสัตว์ พิพิธภัณฑ์ หรือจุดชมวิว ช่างภาพมักจะยืนถ่ายรูปนักท่องเที่ยวตามจุดไฮไลต์ต่างๆ ตลอดทั้งวัน รูปถ่ายหลายพันใบจะถูกส่งกลับมายังเคาน์เตอร์พิมพ์ภาพหน้าร้าน

### ปัญหาของระบบเดิม (The Bottleneck)
* นักท่องเที่ยวต้องมายืนเปิดดูรูปทีละโฟลเดอร์ หรือพนักงานต้องจำหน้าลูกค้าแล้วเลื่อนหารูปในคลังภาพขนาดใหญ่
* ใช้เวลาต่อคิวนาน ลูกค้าหมดความสนใจ เกิดความแออัดหน้าร้าน และสูญเสียโอกาสในการขาย (Lost Revenue)

### เป้าหมายทางวิศวกรรม (Engineering Goals)
1. **ความเร็ว (Latency):** เมื่อลูกค้าเดินเข้ามาหยุดยืนหน้าจอ Kiosk ระบบต้องดึงรูปภาพที่ตรงกันทั้งหมดขึ้นมาแสดงผลภายใน **< 1 วินาที**
2. **ความคุ้มค่า (Edge Computing):** ทำงานแบบ Offline ในคอมพิวเตอร์ประจำเคาน์เตอร์ (Windows Host) ไม่ต้องเสียค่า API รายเดือนบน Cloud
3. **ความแม่นยำ (Accuracy):** สามารถแยกแยะใบหน้าได้แม้ถ่ายจากคนละมุม เปลี่ยนสีหน้า หรือมีคนอื่นยืนร่วมอยู่ในภาพ

---

## 2. สถาปัตยกรรมระบบภาพรวม

ระบบแบ่งการทำงานออกเป็น **2 Pipeline คู่ขนาน** ที่ทำงานเป็นอิสระต่อกัน:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│ [PIPELINE 1: Background Photo Ingestion]                                         │
│                                                                                  │
│ กล้องช่างภาพ ──(Wi-Fi/LAN)──► โฟลเดอร์ Windows (C:\TourPhotos\)                   │
│                                      │                                           │
│                             Folder Watcher (ดักจับไฟล์ใหม่)                        │
│                                      │                                           │
│                             YuNet (ตรวจจับทุกใบหน้าในภาพ)                         │
│                                      │                                           │
│                             SFace (สกัดเวกเตอร์ 128 มิติ)                         │
│                                      │                                           │
│                             SQLite Cache + In-Memory Matrix                      │
└──────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│ [PIPELINE 2: Live Kiosk Sensor & Instant Match]                                 │
│                                                                                  │
│ กล้องหน้า Kiosk ──► Real-time Camera Worker (OpenCV QThread)                     │
│                               │                                                  │
│                      YuNet (ตรวจพบใบหน้าลูกค้าสด)                                │
│                               │                                                  │
│                      SFace (สกัดเวกเตอร์ลูกค้า 128 มิติ)                          │
│                               │                                                  │
│             Vector Dot Product: Q @ DB_Matrix.T (ใช้เวลา < 1ms)                 │
│                               │                                                  │
│         PySide6 UI: กรองภาพที่คล้ายกันเกินเกณฑ์ (Threshold >= 0.36)                │
│                               │                                                  │
│         แสดงผลบนจอ Display ──► ลูกค้าเลือกภาพ ──► สั่งพิมพ์ออกเครื่องพิมพ์          │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. ทฤษฎี Computer Vision & Face Recognition

การเปรียบเทียบใบหน้าไม่สามารถใช้การเทียบพิกเซลตรงๆ (Pixel Matching) หรือ Template Matching ได้ เพราะมุมกล้อง สภาพแสง ทรงผม และสีหน้าของลูกค้าเปลี่ยนตลอดเวลา วิทยาการสมัยใหม่จึงใช้ **Deep Metric Learning** ซึ่งแบ่งออกเป็น 4 ขั้นตอน:

### 3.1 การตรวจจับใบหน้า (Face Detection: YuNet)
* **YuNet** เป็นโมเดล CNN น้ำหนักเบา (ขนาดเพียง ~232 KB) ที่พัฒนาขึ้นสำหรับ OpenCV โดยเฉพาะ
* ทำงานด้วยโครงสร้างแบบ Single-Stage Anchor-based Detector
* จุดเด่น: ตรวจจับใบหน้าได้เร็วกว่าโมเดลเดิม (เช่น Haar Cascade หรือ MTCNN) หลายสิบเท่า โดยใช้เวลาเพียง **~15-30 มิลลิวินาที** บน CPU ทั่วไป
* ผลลัพธ์ที่ได้จาก YuNet ในแต่ละใบหน้าประกอบด้วย 15 ค่า:
  $$\text{Face Output} = [x, y, w, h, x_{re}, y_{re}, x_{le}, y_{le}, x_{nt}, y_{nt}, x_{rcm}, y_{rcm}, x_{lcm}, y_{lcm}, \text{score}]$$
  * $(x, y, w, h)$: พิกัด Bounding Box
  * 5 Landmark Points: ตาขวา, ตาซ้าย, จมูก, มุมปากขวา, มุมปากซ้าย
  * $\text{score}$: ค่าความเชื่อมั่น (Confidence Score 0.0 – 1.0)

### 3.2 การปรับระนาบใบหน้า (Face Alignment)
หากลูกค้าเอียงคอ หรือกล้องถ่ายจากมุมเฉียง ใบหน้าจะบิดเบี้ยว โมเดลจดจำใบหน้าจะไม่สามารถเทียบได้แม่นยำ  
ฟังก์ชัน `recognizer.alignCrop(image, face)` จะคำนวณ **Affine Transformation** โดยหมุนและยืดภาพให้:
* ตำแหน่งดวงตาทั้งสองข้างอยู่ในระนาบแนวนอนเดียวกันเสมอ
* จุดกึ่งกลางจมูกและปากอยู่ตรงกลางกรอบภาพขนาดมาตรฐาน (112 $\times$ 112 พิกเซล)

### 3.3 การแปลงใบหน้าเป็นเวกเตอร์ (Face Embedding: SFace)
* **SFace** ใช้โครงสร้างเครือข่ายประสาทเทียมแบบ Deep CNN ฝึกฝนด้วยฟังก์ชันการสูญเสีย **SphereFace (Angular Margin Loss)**
* โมเดลจะแปลงภาพใบหน้าที่ผ่านการ Align แล้ว ให้กลายเป็น **เวกเตอร์ตัวเลข 128 มิติ (128-dimensional Embedding Vector)**:
  $$\vec{V} = [v_1, v_2, v_3, \dots, v_{128}] \in \mathbb{R}^{128}$$
* **คุณสมบัติทางคณิตศาสตร์:**
  * ใบหน้าของ "คนเดียวกัน" (แม้จะต่างมุม ต่างแสง ต่างทรงผม) เวกเตอร์จะชี้ไปใน **ทิศทางใกล้เคียงกัน** บน Hypersphere
  * ใบหน้าของ "คนละคน" เวกเตอร์จะชี้ไปใน **ทิศทางที่ห่างกันมาก**

### 3.4 การจับคู่และค้นหาเวกเตอร์ความเร็วสูง (Vectorized Cosine Similarity)
หลังจากทำการ Normalize เวกเตอร์ให้มีความยาว 1 ($\|\vec{V}\| = 1$) ค่าความคล้ายคลึงระหว่างเวกเตอร์สองตัวคำนวณได้จาก **Cosine Similarity**:

$$\text{Similarity}(\vec{A}, \vec{B}) = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|} = \sum_{i=1}^{128} A_i B_i$$

เมื่อมีรูปถ่ายในระบบ $N$ ใบหน้า เราสามารถนำเวกเตอร์ทั้งหมดมารวมกันเป็นเมทริกซ์ $\mathbf{M} \in \mathbb{R}^{N \times 128}$  
เมื่อมีลูกค้ามายืนหน้ากล้อง และได้เวกเตอร์ใบหน้าสด $\vec{Q} \in \mathbb{R}^{128}$ เราสามารถคำนวณความเหมือนกับทุกใบหน้าในคลังได้ด้วยการคูณเมทริกซ์เพียงครั้งเดียว:

$$\vec{S} = \mathbf{M} \times \vec{Q}^T \quad \in \mathbb{R}^N$$

* การคำนวณนี้ใน NumPy หรือ BLAS Library ใช้เวลาเพียง **0.0005 วินาที สำหรับ 10,000 ใบหน้า!**
* **การตัดสินผล (Thresholding):**
  * สำหรับโมเดล SFace ค่า Cosine Similarity ปกติ:
    * $\ge 0.363$: จัดว่าเป็น "บุคคลเดียวกัน" (Same Identity)
    * $< 0.300$: จัดว่าเป็น "คนละคน" (Different Person)

---

## 4. การออกแบบสถาปัตยกรรมซอฟต์แวร์

### 4.1 ปัญหา Multi-threading Race Condition บน OpenCV DNN
ในการพัฒนา Desktop App ที่มีกล้องวิดีโอสด (Live Video) ร่วมกับระบบประมวลผลพื้นหลัง:
* **ปัญหาที่มักพบ:** หากเธรดกล้อง (Camera Thread) และเธรดสแกนโฟลเดอร์ (Scan Thread) เรียกใช้งานอ็อบเจกต์ `cv2.FaceDetectorYN` เดียวกันพร้อมกัน จะเกิดข้อผิดพลาดรุนแรงระดับ C++:
  ```text
  cv2.error: Unknown C++ exception from OpenCV code
  ```
  เนื่องจากฟังก์ชัน `setInputSize()` และ `detect()` ใน OpenCV C++ ภายในมีการแก้ไขหน่วยความจำ Buffer เดียวกัน (Not Thread-Safe)
* **วิธีแก้:**
  1. ใช้ **Mutex Lock (`threading.Lock()`)** ครอบทุกจุดที่มีการเรียกตรวจจับใบหน้า
  2. หรือแยก Instance ของโมเดลให้แต่ละ Thread ถือครองอิสระต่อกัน

### 4.2 การดัชนีรูปภาพแบบ Incremental ด้วย SQLite
เพื่อไม่ให้ระบบต้องเสียเวลาสแกนรูปเดิมซ้ำๆ ทุกครั้งที่เปิดโปรแกรม:
* บันทึกข้อมูลเมทาดาทาของไฟล์ภาพ: `mtime` (เวลาแก้ไขล่าสุด) และ `file_size` ลงในตาราง `photos`
* เมื่อตรวจพบไฟล์ใหม่ ระบบจะตรวจสอบ:
  ```sql
  SELECT mtime, file_size FROM photos WHERE photo_path = ?
  ```
  ถ้าค่าเดิมตรงกัน ให้ **ข้าม (Skip)** ทันที ทำให้การรีสแกนโฟลเดอร์ที่มีภาพเป็นหมื่นๆ รูป ใช้เวลาไม่ถึง 0.1 วินาที

### 4.3 โครงสร้าง Signal & Slot ใน PySide6 (Event-Driven Architecture)
UI ของ Desktop App จะต้องไม่เกิดอาการค้าง (Freeze) หรือ "Not Responding":
* **CameraWorker (QThread):** ทำหน้าที่ดึงเฟรมจาก Webcam และวาดกล่องเล็ง (HUD) อย่างต่อเนื่อง 30 FPS
* ส่งข้อมูลข้าม Thread ด้วย Qt Signal:
  * `frame_ready(QImage)` $\to$ ส่งภาพไปเรนเดอร์บน QLabel
  * `face_detected(crop, feat)` $\to$ ส่งเวกเตอร์ไปค้นหาในฐานข้อมูล
  * `face_cleared()` $\to$ แจ้งเตือนเมื่อลูกค้าเดินออกจากหน้ากล้อง

---

## 5. เจาะลึกการทำงานของโค้ดหลัก

### 5.1 Face Engine: ตรวจจับและสกัด Feature
ไฟล์: [`core/face_engine.py`](file:///c:/Users/ndrs-admin/Documents/antigravity/learning/smart_photo_kiosk/core/face_engine.py)

```python
# การแปลงขนาดภาพก่อน Detect เพื่อความเร็ว และแปลงพิกัดกลับ
scale = max_detect_dim / float(max(orig_h, orig_w)) if max(orig_h, orig_w) > max_detect_dim else 1.0
detect_img = cv2.resize(img_bgr, (int(orig_w * scale), int(orig_h * scale)))

with self._lock:
    self.detector.setInputSize((detect_img.shape[1], detect_img.shape[0]))
    _, faces = self.detector.detect(detect_img)

    for face in faces:
        # สเกลพิกัดใบหน้ากลับสู่ขนาดของรูปต้นฉบับ เพื่อให้ภาพ Crop ชัดที่สุด
        face_orig = face / scale
        aligned_face = self.recognizer.alignCrop(img_bgr, face_orig)
        feat = self.recognizer.feature(aligned_face).flatten()
        feat = feat / np.linalg.norm(feat)  # Normalize เป็นความยาว 1
```

### 5.2 Photo Indexer: คลังเวกเตอร์และการคำนวณแบบ Matrix
ไฟล์: [`core/indexer.py`](file:///c:/Users/ndrs-admin/Documents/antigravity/learning/smart_photo_kiosk/core/indexer.py)

```python
def search_by_face(self, query_feat: np.ndarray, threshold: float = 0.36):
    # คูณเมทริกซ์ (N, 128) x (128,) ได้ค่า Cosine Similarity ของทุกรูปพร้อมกัน
    sims = np.dot(self.matrix, query_feat)

    # กรองเฉพาะภาพที่ความเหมือนมากกว่า Threshold
    matched_indices = np.where(sims >= threshold)[0]

    # กรณีภาพกลุ่ม (1 ภาพมีหลายใบหน้า) ให้เลือกคะแนนสูงสุดของภาพนั้น
    photo_matches = {}
    for idx in matched_indices:
        sim = float(sims[idx])
        path = self.records[idx]["photo_path"]
        if path not in photo_matches or sim > photo_matches[path]["similarity"]:
            photo_matches[path] = {"photo_path": path, "similarity": sim}

    return sorted(photo_matches.values(), key=lambda x: x["similarity"], reverse=True)
```

### 5.3 Camera Worker: การประมวลผลสตรีมวิดีโอแบบเรียลไทม์
ไฟล์: [`core/camera_worker.py`](file:///c:/Users/ndrs-admin/Documents/antigravity/learning/smart_photo_kiosk/core/camera_worker.py)

* ดึงภาพผ่าน `cv2.VideoCapture`
* ใช้เทคนิค **Throttling (หน่วงรอบการ Match):** ตรวจจับกล่องใบหน้าทุก 30 FPS เพื่อให้ภาพลื่นไหล แต่นำเวกเตอร์ไป Query ในฐานข้อมูลทุกๆ 400ms เพื่อป้องกันไม่ให้หน้าจอผลลัพธ์กระพริบเปลี่ยนไปมา
* วาด HUD (กรอบมุมเล็งเป้า Neon Cyberpunk สไตล์ Kiosk) ช่วยให้ลูกค้ารู้ว่ากล้องกำลังตรวจจับใบหน้าอยู่

---

## 6. โจทย์หน้างานจริงและการแก้ปัญหา (Production Engineering)

### 6.1 การจัดการรูปถ่ายความละเอียดสูง (DSLR 24MP–48MP)
* **ปัญหา:** หากนำรูปจากกล้องโปร (ขนาด 6000 $\times$ 4000 พิกเซล) เข้าโมเดล YuNet ตรงๆ จะใช้เวลา 300–500ms ต่อรูป ทำให้เครื่องช้า
* **แนวทางแก้ไข (Resolution Pyramiding):**
  1. ย่อภาพลงมาเหลือความยาวด้านมากสุดไม่เกิน `1280px` ก่อนส่งเข้า Face Detector
  2. เมื่อได้ตำแหน่งพิกัด Landmark 5 จุด ให้นำตัวคูณ $(1 / scale)$ ไปขยายพิกัดกลับ
  3. สั่ง Align และ Crop ใบหน้าจาก **ภาพขนาดเต็มต้นฉบับ (Original Raw Image)** ผลลัพธ์คือได้ความเร็วสูงระดับ 25ms แต่ความคมชัดของรายละเอียดใบหน้าไม่สูญเสียเลย

### 6.2 การตรวจจับรูปภาพแบบกลุ่ม (Group & Family Photos)
* ในตาราง `faces` ของฐานข้อมูล SQLite เราไม่ได้ผูก 1 รูป ต่อ 1 คน แต่ใช้ความสัมพันธ์แบบ **One-to-Many**:
  * 1 แถวในตาราง `photos` สามารถเชื่อมกับหลายแถวในตาราง `faces`
* **ตัวอย่าง:** รูป `family_trip.jpg` มี พ่อ, แม่, ลูก รวม 3 คน
  * ถ้า "พ่อ" เดินผ่านกล้อง $\to$ แสดงรูป `family_trip.jpg`
  * ถ้า "ลูก" เดินผ่านกล้อง $\to$ แสดงรูป `family_trip.jpg` เช่นกัน

### 6.3 สภาพแสง มุมกล้อง และการปรับแต่ง Sensitivity Threshold
* **สภาพแสงหน้าร้าน:** ควรติดตั้งไฟ Soft Light หรือ Ring Light เล็กๆ ส่องใบหน้าลูกค้า เพื่อไม่ให้เกิดเงามืดใต้ตาหรือหน้ามืดเวลาย้อนแสง
* **การจูน Slider Threshold:**
  * `0.30 - 0.34`: ผ่อนปรน (ตรวจจับง่ายขึ้น เหมาะสำหรับคนใส่แว่น/มุมหน้าเอียง แต่อาจมีรูปคนอื่นที่หน้าคล้ายกันปนมาบ้าง)
  * `0.36 - 0.40`: **จุดสมดุลที่ดีที่สุดสำหรับงานผลิตจริง (Recommended)**
  * `> 0.45`: เข้มงวดมาก (ป้องกันคนหน้าคล้าย 100% แต่อาจหลุดบางรูปถ้าลูกค้าเปลี่ยนทรงผมหรือหันข้าง)

### 6.4 การเชื่อมต่อเครื่องพิมพ์ภาพถ่าย
ในระบบโปรดักชันจริง สามารถส่งพิมพ์รูปได้ 2 วิธี:
1. **ผ่าน Windows GDI / Print Spooler (Win32 API):**  
   ใช้คำสั่ง `ShellExecute(0, "print", photo_path, None, ".", 0)` สั่งพิมพ์ผ่านไดรเวอร์ของ Windows โดยตรง
2. **เครื่องพิมพ์ภาพด่วน (Dye-Sublimation Printers):**  
   เช่น **DNP DS620** หรือ **Citizen CY-02** จะมี Hot Folder หรือ SDK เฉพาะที่สามารถสั่งพิมพ์ภาพขนาด 4$\times$6 นิ้ว ได้เสร็จสิ้นภายใน 8.9 วินาทีต่อใบ

### 6.5 ความปลอดภัยของข้อมูลและความเป็นส่วนตัว (Privacy & PDPA)
* ควรตั้งระบบ **Auto-Purge Job** ลบรูปถ่ายและเวกเตอร์ใบหน้าเก่าที่เกิน 24 หรือ 48 ชั่วโมงทิ้งอัตโนมัติ เพื่อประหยัดพื้นที่ดิสก์และไม่ละเมิดความเป็นส่วนตัวของนักท่องเที่ยว
* ติดตั้งป้ายแจ้งเตือนหน้าร้านว่า "ระบบกล้องตรวจจับภาพถ่ายอัตโนมัติเพื่อความสะดวกรวดเร็วในการเลือกซื้อภาพถ่าย"

---

## 7. แบบฝึกหัดทบทวนและแนวทางต่อยอด (Exercises & Roadmap)

### 💡 แบบฝึกหัดท้าทาย (Challenges)
1. **Challenge 1 (QR Code Photo Delivery):**  
   เขียนส่วนต่อยอด ให้เมื่อลูกค้าเลือกรูปแล้ว สามารถสร้าง QR Code บนหน้าจอ เพื่อให้ลูกค้าใช้มือถือสแกนดาวน์โหลดไฟล์ JPEG ภาพต้นฉบับเข้ามือถือได้โดยตรง
2. **Challenge 2 (Face Clustering / Unsupervised Grouping):**  
   ใช้ขั้นตอนวิธี **DBSCAN** รวมรูปถ่ายของนักท่องเที่ยวคนเดียวกันที่ถ่ายไว้ตลอดทั้งวัน เข้าเป็นอัลบั้มส่วนตัว (Album ID) โดยอัตโนมัติก่อนที่ลูกค้าจะเดินมาถึงเคาน์เตอร์
3. **Challenge 3 (Multiple Kiosk Sync):**  
   ปรับจาก SQLite เป็น PostgreSQL + Milvus Vector Database เพื่อให้มี Kiosk ตั้งอยู่หลายจุดทั่วสวนสนุก เชื่อมต่อคลังภาพเดียวกันพร้อมกันได้ 10–20 จุด
