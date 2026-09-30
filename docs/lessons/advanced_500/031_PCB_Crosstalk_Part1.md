# Lesson 031: PCB Crosstalk - Part 1: Fundamentals & Capacitive Coupling (クロストークの基礎と容量結合)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Crosstalk คือปรากฏการณ์ที่สัญญาณจากเส้นหนึ่ง (Aggressor) ไปรบกวนสัญญาณในอีกเส้นหนึ่ง (Victim) โดยไม่พึงประสงค์ ในความถี่สูงและ Edge rate (dv/dt หรือ di/dt) ที่ชันขึ้น Crosstalk จะยิ่งรุนแรง 
กลไกแรกคือ **Capacitive Coupling (容量結合)** เกิดจาก Mutual Capacitance ($C_m$) ระหว่าง Trace สองเส้น เมื่อ Aggressor มีการเปลี่ยนแปลงแรงดัน ($dv/dt$) จะเกิดกระแส $I_{crosstalk} = C_m \frac{dv}{dt}$ ฉีดเข้าไปใน Victim net

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **3W Rule:** กฎพื้นฐานในการลด Crosstalk คือเว้นระยะห่างระหว่าง Center-to-Center ของ Trace ให้ได้อย่างน้อย 3 เท่าของความกว้าง (Width) ของ Trace กฎนี้ช่วยลด Mutual Capacitance ได้ถึง 70%
- **Guard Trace:** การใช้ Ground trace กั้นกลาง (Guard trace) ต้องมั่นใจว่ามีการเจาะ Via ลง Ground plane อย่างถี่พอ (1/10 ของความยาวคลื่น) ไม่อย่างนั้น Guard trace จะกลายเป็นสายอากาศ (Antenna) แผ่สัญญาณรบกวนเสียเอง

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **クロストーク (Kurosutooku):** Crosstalk
- **結合容量 (Ketsugou Youryou):** Coupling Capacitance / Mutual Capacitance
- **配線間隔 (Haisen Kankaku):** Trace clearance / Spacing
- **ガードパターン (Gaado Pataan):** Guard pattern / Guard trace
- **干渉 (Kanshou):** Interference

## ควิซท้ายบท (Quiz)
**Q1:** ในสมการ $I_{crosstalk} = C_m \frac{dv}{dt}$ ตัวแปรใดที่สะท้อนถึง Edge rate ของสัญญาณ?
**A:** $\frac{dv}{dt}$
**Q2:** หากไม่มีการเจาะ Via ลงกราวด์ที่เหมาะสม Guard trace จะทำให้เกิดผลเสียอย่างไร?
**A:** กลายเป็นสายอากาศ (Antenna) ที่สร้าง Resonance และแผ่สัญญาณรบกวน
