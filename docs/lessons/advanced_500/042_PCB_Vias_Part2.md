# Lesson 42: PCB Vias - Signal Integrity (SI) & Return Path

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
Via บน High-speed signal line มีผลอย่างมากต่อ Signal Integrity (SI) เพราะ Via ทำให้เกิด Impedance Discontinuity โดย Via จะมีคุณสมบัติคล้าย Capacitor หากมี Anti-pad เล็กเกินไป หรือเป็น Inductor หากเจาะรูใหญ่เกินไป นอกจากนี้ การเปลี่ยน Layer ของสัญญาณ (Layer Transition) จะต้องคำนึงถึง Return Path หากสัญญาณเปลี่ยนจาก Top ไป Bottom Return current ก็ต้องเปลี่ยน Reference plane ด้วย หากไม่มี Stitching via (Return via) อยู่ใกล้ๆ จะเกิด Ground Bounce และ EMI อย่างรุนแรง

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick:** ทุกครั้งที่มีการเจาะทะลุ Layer (Layer Transition) สำหรับสัญญาณความเร็วสูง (เช่น PCIe, USB3.0) ต้องบังคับให้ Layout Engineer วาง GND Stitching Via ไว้ใกล้เคียงเสมอ (ระยะห่างไม่ควรเกิน 1-2 mm จาก Signal Via)
- **Design Review Check:** ตรวจสอบ Anti-pad (Clearance รอบ Via ในชั้น Plane) ว่าใหญ่พอที่จะลด Parasitic Capacitance แต่ไม่ใหญ่จนตัด Return Path ของสัญญาณอื่น (Plane Split)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **信号完全性 (Shingō kanzensei):** Signal Integrity (SI)
- **インピーダンス不整合 (Inpīdansu fuseigō):** Impedance Discontinuity
- **リターンパス (Ritān pasu):** Return Path
- **アンチパッド (Anchipaddo):** Anti-pad
- **層間移動 (Sōkan idō):** Layer Transition

## ควิซท้ายบท (Quiz)
**Q1:** การเพิ่มขนาดของ Anti-pad รอบๆ Signal Via จะส่งผลอย่างไรต่อคุณสมบัติทางไฟฟ้าของ Via?
1. เพิ่ม Parasitic Capacitance
2. ลด Parasitic Capacitance และเพิ่ม Impedance
3. ลด Impedance ของ Via
4. ไม่มีผลต่อ Impedance
*(เฉลย: 2. ลด Parasitic Capacitance และเพิ่ม Impedance)*
