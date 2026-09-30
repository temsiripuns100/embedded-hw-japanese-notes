# 2.3 スキュー（Skew）とジッタ（Jitter）の発生原因 (สาเหตุการเกิด Time Skew และ Jitter ในคลื่นความถี่สูง)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**Skew (ความเหลื่อมล้ำทางเวลา)** คือการที่สัญญาณ 2 เส้น (ที่ควรจะมาพร้อมกัน) มาถึงไม่พร้อมกัน เป็นความผิดพลาดแบบคงที่ (Static) สาเหตุหลักมักมาจากการเดินสาย (Length Mismatch) บน PCB หรือความยาวสายเคเบิลที่ไม่เท่ากัน
**Jitter (ความสั่นไหวของจังหวะเวลา)** คือการที่สัญญาณสลับสถานะ (Edge Transition) เร็วไปหรือช้าไปจากจังหวะนาฬิกาอ้างอิง เป็นความผิดพลาดแบบไม่คงที่ (Dynamic) แบ่งเป็น:
- *Random Jitter (RJ):* เกิดจากสัญญาณรบกวนจากความร้อน (Thermal Noise)
- *Deterministic Jitter (DJ):* เกิดจากสาเหตุที่ชี้ชัดได้ เช่น Power Supply Ripple, Crosstalk หรือ Duty Cycle Distortion

## 💡 ทริคหน้างาน (OJT Tricks)
- **ไฟสะอาด = คล็อคสะอาด:** ถ้าคุณจับสัญญาณ Clock ด้วย Oscilloscope แล้วพบว่า Jitter กว้างมากจน Eye Diagram ปิด ให้พุ่งเป้าไปที่ **"ไฟเลี้ยงของ PLL (Phase-Locked Loop)"** ก่อนเลย! หากไฟเลี้ยงมี Noise (Ripple จาก DCDC) จะไปกวนวงจรสร้าง Clock ทำให้เกิด Deterministic Jitter ทันที
- **วัด Jitter ต้องใช้เครื่องมือให้ถูก:** การดู Jitter ต้องใช้ Oscilloscope ที่มีแบนด์วิดท์สูงพอ และต้องใช้ฟังก์ชัน "Eye Diagram" หรือ "TIE (Time Interval Error)" ถ้าดูแค่รูปคลื่นธรรมดามองไม่ออก

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **スキュー (Sukyū):** Skew
- **ジッタ (Jitta):** Jitter
- **アイパターン / アイダイアグラム (Aipatān / Aidiaguramu):** Eye Pattern / Eye Diagram
- **電源ノイズ (Dengen Noizu):** Power Supply Noise
- **クロック (Kurokku):** Clock

**ประโยคที่ใช้บ่อย:**
> 「アイパターンが閉じている原因は、電源ノイズによるジッタの増加だと推測されます。」
> *(Aipatān ga tojite iru gen'in wa, dengen noizu ni yoru jitta no zōka da to suisoku saremasu.)*
> "สาเหตุที่ทำให้รูปคลื่น Eye Diagram ปิด สันนิษฐานว่าเกิดจากการเพิ่มขึ้นของ Jitter ซึ่งมีต้นเหตุมาจากสัญญาณรบกวนของแหล่งจ่ายไฟครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** หากวงจรของคุณมี DCDC Converter ที่ออกแบบเลย์เอาท์ไม่ดีวางอยู่ใกล้กับสายสัญญาณความเร็วสูง คุณคิดว่ามันจะก่อให้เกิด Jitter ประเภทใดมากที่สุดระหว่าง Random Jitter (RJ) หรือ Deterministic Jitter (DJ) ?
