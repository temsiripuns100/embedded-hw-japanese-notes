# 052: PCB Thermal Management - Part 2: Thermal Vias and Copper Pours
## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
1. **Thermal Vias (サーマルビア):** คือทางด่วนระบายความร้อนลงสู่ Ground Plane ทฤษฎีระบุว่าค่า Thermal Resistance ($\theta_{via}$) ลดลงตามจำนวน via แต่จะไม่เป็นเส้นตรง (Diminishing returns). หากเจาะ via มากเกินไป จะสูญเสียพื้นที่ Copper pour ซึ่งเป็น Heat Spreader ทำให้ประสิทธิภาพลดลง. กฎทั่วไปคือ วาง via ห่างกันประมาณ 1.0 - 1.2 mm.
2. **Copper Pours (銅箔ベタ - Douhaku Beta):** การเททองแดงกว้างๆ ทำหน้าที่เหมือน Heat Sink ชั่วคราว. สำหรับความถี่สูง (RF/High-speed) ต้องระวังเรื่อง Parasitic Capacitance แต่สำหรับ Power/Thermal, More is better. ความหนาของทองแดง (1 oz vs 2 oz) มีผลโดยตรงต่อ Thermal Spreading.

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **Via Tenting & Plugging:** อย่าวาง Thermal via เปลือยใต้ Thermal Pad ของ IC โดยตรงถ้าไม่ใช่ Via-in-Pad with plating (VIPPO) เพราะตะกั่วจะไหลลงรู (Solder wicking) ทำให้ชิปเอียงหรือบัดกรีไม่ติด (Tombstoning/Voiding). ถ้าทำ VIPPO ไม่ได้ ให้ใช้ Solder Mask tenting หรือแบ่งตะกั่วบัดกรีเป็นช่องๆ (Window pane).
- **Symmetry (สมมาตร):** การเททองแดงแบบไม่สมมาตร (Top เทเยอะ Bottom ไม่มี) ทำให้บอร์ดโก่ง (Warpage / 弓なり) ตอนผ่านเตาอบ (Reflow).

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **サーマルビア (Saamaru Bia):** Thermal via
- **熱抵抗 (Netsuteikou):** Thermal resistance
- **はんだ吸い上がり (Handa Suiagari):** Solder wicking (ตะกั่วถูกดูดลงรู via)
- **反り (Sori):** Warpage (การโก่งงอของบอร์ด)

## ควิซท้ายบท (Quiz)
1. ปัญหาใดที่มักเกิดหากวาง Thermal via ใต้แผ่น Thermal pad ของ IC โดยไม่ทำการปิดรู?
   a) Parasitic inductance เพิ่ม
   b) ขาดพื้นที่เททองแดง
   c) Solder wicking (ตะกั่วไหลลงรู)
   d) บอร์ดโก่ง
*(เฉลย: c)*
