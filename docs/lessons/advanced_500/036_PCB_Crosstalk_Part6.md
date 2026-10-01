# 036: PCB Crosstalk เจาะลึก Part 6 - Return Path Discontinuities (RPD)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Crosstalk ไม่ได้เกิดจากระยะห่างของ Trace บน Layer เดียวกันอย่างเดียว แต่เกิดจาก **Return Path Sharing** ด้วย!
- **Return Current Flow:** กระแสความถี่สูง (High Frequency) จะไหลกลับบน Reference Plane ในตำแหน่งที่อยู่ "ใต้" Trace อย่างแม่นยำ (Path of least inductance)
- **RPD (Return Path Discontinuity):** เมื่อ Trace วิ่งข้ามรอยแยก (Split Plane), Voids หรือ เปลี่ยน Layer โดยไม่มี Return Via ใกล้ๆ กระแสไหลกลับจะไม่มีทางไป มันต้องอ้อม!
- **Inductive Crosstalk จาก RPD:** เมื่อกระแสไหลกลับต้องอ้อมรอยแยก (Slot) พื้นที่ลูป (Loop Area) จะใหญ่ขึ้น สนามแม่เหล็กจะขยายวงกว้าง (Mutual Inductance $L_m$ พุ่งสูงมาก) หากมีเส้นสัญญาณอื่นเดินข้าม Slot เดียวกันบริเวณนั้น แม้จะอยู่ห่างกัน 1 นิ้ว ก็เกิด Crosstalk รุนแรงได้ เพราะมันต้อง *Share Return Path* อ้อม Void เดียวกัน

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **ตรวจแบบด้วย Z-Axis View:** เวลา OJT น้องใหม่ ให้เปิด Gerber แล้วซ้อน Layer สัญญาณ กับ Layer GND/VCC ทันที ดูว่ามี Trace ไหนผ่ากลางรอยแหว่ง (Anti-pad ที่เชื่อมติดกัน หรือ Split plane) หรือไม่ ห้ามปล่อยผ่านเด็ดขาด!
- **Stitching Capacitors:** หากหลีกเลี่ยงไม่ได้ที่สัญญาณต้องข้ามระหว่าง 2 Reference planes ที่มีศักย์ต่างกัน (เช่น 3.3V Plane และ GND Plane) ต้องวาง Decoupling Capacitor 0402 ไว้ข้างๆ Trace ตรงจุดที่ข้ามขอบ Plane ทันที เพื่อให้ AC Return current กระโดดข้ามผ่าน Cap ได้

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **リターンパス (Ritān pasu):** Return path (เส้นทางไหลกลับของกระแส)
- **スリット (Suritto):** Split / Slot (รอยแยกใน Plane)
- **プレーン分割 (Purēn bunkatsu):** Plane split
- **ループ面積 (Rūpu menseki):** Loop area
- **パスの不連続 (Pasu no furenzoku):** Path discontinuity

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** การที่เส้นสัญญาณความเร็วสูงสองเส้นอยู่ห่างกันมาก แต่อยู่ๆ เกิด Crosstalk รุนแรงแทรกแซงกัน สาเหตุที่เกี่ยวข้องกับ Plane มักเกิดจากอะไร?
**คำตอบ:** เกิดจากการที่เส้นทั้งสองพาดผ่านรอยแยกของ Plane (Split Plane หรือ Slot) ทำให้กระแส Return path ของทั้งสองเส้นต้องวิ่งอ้อมไปใช้เส้นทางเดียวกันที่ขอบรอยแยก ทำให้เกิด Mutual Inductance อย่างมากและเกิด Crosstalk ผ่าน Return path ร่วมนี้
