# Lesson 027: PCB Impedance Part 7 - Differential Impedance and Skew Management

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Differential impedance ($Z_{diff}$) ไม่ได้มีค่าเท่ากับ $2 \times Z_0$ ของ Single-ended เสมอไป แต่ขึ้นอยู่กับ Coupling ระหว่างสายสัญญาณทั้งสองเส้น (Odd-mode impedance, $Z_{odd}$). สมการโดยประมาณคือ $Z_{diff} = 2 \times Z_{odd}$ เมื่อความถี่สูงขึ้น การรักษา Skew (ความยาวของสายคู่บวกและลบที่ไม่เท่ากัน) ให้ต่ำที่สุดเป็นสิ่งสำคัญมาก หากเกิด Intra-pair skew สัญญาณ Differential จะเปลี่ยนรูปเป็น Common-mode noise ซึ่งนอกจากจะทำให้ Eye diagram ปิดลงแล้ว ยังเพิ่ม EMI อย่างมหาศาล (Mode Conversion)

## 2. ทริคหน้างาน OJT (On-the-Job Training Tips)
- **Senior Tip:** เวลาแก้ Skew (Length matching) ต้องแก้ที่จุดที่เกิดความยาวต่างกันทันที (เช่น ตอนเลี้ยวโค้ง) อย่าไปรอแก้ที่ปลายทาง! เพราะสัญญาณจะกลายเป็น Common-mode วิ่งไปตลอดทาง ทำให้แผ่คลื่นแม่เหล็กไฟฟ้ารบกวนส่วนอื่น
- เทคนิคการเดินลาย: ให้ใช้การเลี้ยวแบบโค้ง (Arc) หรือมุม 45 องศา และใช้ "Phase bump" หรือ "Trombone" ในการชดเชยความยาว

## 3. คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **差動インピーダンス (Sadō inpīdansu):** Differential Impedance
- **等長配線 (Tōchō haisen):** Length Matching (การเดินสายให้ยาวเท่ากัน)
- **同相ノイズ (Dōsō noizu):** Common-mode Noise
- **曲げ (Mage):** Bending (การเลี้ยวโค้งของลายวงจร)
- **位相ズレ (Ishō zure):** Phase shift / Skew

## 4. ควิซท้ายบท (End-of-chapter Quiz)
**Q:** Intra-pair skew ที่ยอมรับได้สำหรับสัญญาณ 10 Gbps (UI = 100 ps) ควรอยู่ที่ประมาณเท่าไหร่?
**A:** โดยทั่วไป กฎ OJT คือไม่ควรเกิน 10-20% ของ UI (Unit Interval) หรือ Rise time ดังนั้นสำหรับ 10 Gbps ควรควบคุมให้ skew ไม่เกิน 10-15 ps (หรือความยาวต่างกันไม่เกินประมาณ 1.5-2 mm บน FR4)
