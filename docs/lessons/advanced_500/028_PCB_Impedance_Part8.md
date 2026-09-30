# Lesson 028: PCB Impedance Part 8 - Return Path and Ground Bounce

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
สัญญาณความถี่สูงไม่ได้เดินทางตามความต้านทานที่ต่ำที่สุด (Path of least resistance) แต่เดินทางตาม **ความต้านทานเชิงซ้อนที่ต่ำที่สุด (Path of least impedance)** ซึ่งหมายความว่า Return current จะเกาะติดอยู่ใต้ Trace สัญญาณพอดี (ในชั้น Reference plane) หาก Reference plane ถูกตัดขาด (Split plane) หรือมีรอยแยก (Anti-pad) Return path จะถูกบังคับให้อ้อม เกิดเป็นการเพิ่ม Inductance ($L$) อย่างมหาศาล ซึ่งส่งผลให้ Impedance ($Z = \sqrt{L/C}$) ตรงจุดนั้นกระโดดขึ้นสูง และทำให้เกิด Ground Bounce (SSN - Simultaneous Switching Noise) จากสมการ $V = L(di/dt)$

## 2. ทริคหน้างาน OJT (On-the-Job Training Tips)
- **Senior Tip:** ห้ามเดินสายสัญญาณ High-speed ข้ามรอยต่อของ Plane (Split plane) เด็ดขาด! ถ้าหลีกเลี่ยงไม่ได้จริงๆ ต้องใส่ Stitching capacitor คร่อมรอยต่อนั้นใกล้ๆ กับจุดที่สัญญาณข้าม เพื่อสร้าง AC Return path
- เวลาตรวจแบบ ให้เปิดดูชั้น Signal พร้อมกับชั้น Plane ถัดไปเสมอ เพื่อเช็คว่ามี Gap หรือ Void ไปตัด Return path หรือไม่

## 3. คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **リターンパス (Ritānpasu):** Return Path (เส้นทางไหลกลับของกระแส)
- **スプリットプレーン (Supurittopurēn):** Split Plane (การแบ่งระนาบกราวด์หรือไฟ)
- **跨ぎ配線 (Matagi haisen):** Routing over split plane (การเดินลายเส้นข้ามรอยต่อ - **มักเป็นข้อห้าม**)
- **グラウンドバウンス (Guraundobaunsu):** Ground Bounce
- **ベタGND (Beta guraundo):** Solid Ground Plane (ระนาบกราวด์ทึบ)

## 4. ควิซท้ายบท (End-of-chapter Quiz)
**Q:** ถ้าจำเป็นต้องเปลี่ยนชั้นของสัญญาณ High-speed จาก Layer 1 (อ้างอิง GND Layer 2) ไปยัง Layer 8 (อ้างอิง GND Layer 7) ต้องทำอย่างไรเพื่อรักษา Return path?
**A:** ต้องวาง Ground via (Stitching via) ไว้ใกล้ๆ กับ Signal via เสมอ เพื่อให้ Return current สามารถกระโดดจาก Layer 2 ไปยัง Layer 7 ได้อย่างราบรื่น ลดการเกิด Impedance discontinuity
