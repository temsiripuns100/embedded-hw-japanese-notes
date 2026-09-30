# Lesson 45: Advanced Manufacturing Defects & Stub Effect

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
- **Via Stub Effect:** เมื่อเดินสัญญาณ High-speed ใน Layer บนๆ (เช่น Top ไป L2) แต่ Via เจาะทะลุไปถึง Bottom Layer ส่วนของ Via ที่ยื่นเกินออกมา (Stub) จะทำหน้าที่เป็น Antenna สะท้อนสัญญาณกลับ (Reflection) ทำให้เกิด Signal Degradation ที่ความถี่ Resonant frequency แก้ไขได้โดยใช้เทคนิค Backdrilling
- **CAF (Conductive Anodic Filament):** ปัญหาความเชื่อถือได้ขั้นสูง เกิดจากการแพร่ของไอออนทองแดง (Copper Ion Migration) ตามแนวเส้นใยแก้ว (Glass fiber) ภายในบอร์ดเมื่อมีความชื้นและ High Bias Voltage ทำให้เกิดการ Short circuit ระหว่าง Via ที่อยู่ใกล้กัน

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick:** การสั่งทำ Backdrilling มีค่าใช้จ่ายสูงและต้องกำหนด Depth Clearance ให้ดี (ปกติเผื่อ ±5-10 mils) ให้พิจารณาว่าจำเป็นไหม หากสัญญาณวิ่งไม่เกิน 10 Gbps บางทีการย้าย Layer สัญญาณไปวิ่งที่ชั้นล่างสุด (เพื่อให้ Stub สั้นที่สุด) อาจจะประหยัดกว่าการทำ Backdrill
- **Design Review Check:** สำหรับวงจร High Voltage ตรวจสอบ Pitch ระหว่าง Vias ในทิศทางที่ขนานกับ Glass Weave ว่าห่างพอไหม เพื่อป้องกัน CAF หากจำเป็นควรวาง Via แบบ Zig-zag (Off-grid) 

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **スタブ (Sutabu):** Stub (ส่วนที่ยื่นเกินออกมา)
- **バックドリル (Bakkudoriru):** Backdrill (ザグリ加工 - Zaguri kakō)
- **マイグレーション (Maigurēshon):** Ion Migration (CAF)
- **ガラスエポキシ (Garasu epokishi):** Glass Epoxy (FR4)
- **短絡 (Tanraku):** Short Circuit (ショート)

## ควิซท้ายบท (Quiz)
**Q1:** การวาง Via แบบ Zig-zag หรือหลีกเลี่ยงการวาง Via เรียงกันในแนวเดียวกับเส้นใยแก้ว มีจุดประสงค์เพื่อป้องกันปัญหาอะไร?
1. Impedance Mismatch
2. CAF (Conductive Anodic Filament) / Ion Migration
3. Solder Wicking
4. Drill Breakage
*(เฉลย: 2. CAF)*
