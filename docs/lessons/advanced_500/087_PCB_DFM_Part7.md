# Lesson 87: PCB DFM Part 7 - Power Integrity (PI) & Thermal Management

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
Power Integrity (PI) มุ่งเน้นไปที่การลด PDN (Power Delivery Network) Impedance ในช่วงความถี่กว้าง การวาง Decoupling Capacitor ต้องพิจารณา Loop Inductance ที่เกิดจาก Via และ Trace ในด้าน DFM การเจาะ Via จำนวนมากใกล้ๆ กันเพื่อลด Inductance อาจทำให้เกิดปัญหาบอร์ดโก่ง (Warpage) หรือความแข็งแรงของโครงสร้างลดลง (Swiss Cheese Effect) ในส่วนของ Thermal Management การใช้ Thermal Via Array ต้องระวังเรื่อง Solder Wicking (ตะกั่วไหลลงรูเจาะ) ซึ่งแก้ได้โดยการทำ Via Tenting หรือ Via Plugging (Capping) ด้วย Epoxy Resin

## ทริคหน้างาน OJT (OJT Practical Tricks)
- เมื่อต้องระบายความร้อนจาก IC กำลังสูง (เช่น MOSFET, FPGA) การสั่งทำ Resin Plugged Via + Plated Over (POFV) จะช่วยให้บัดกรี Pad ได้เต็มพื้นที่โดยตะกั่วไม่หาย
- การวาง Copper Pour (Solid Polygon) พื้นที่กว้างๆ ควรกระจายความร้อนตอนบัดกรีให้ดี โดยใช้ Thermal Relief Pad กับขาอุปกรณ์ (ยกเว้นขาที่ต้องการกระแสสูงมาก ต้อง Balance ระหว่าง PI กับ DFM)
- ระวังปัญหา Tombstoning ของ Capacitor ขนาดเล็ก (0402, 0201) ที่เกิดจาก Pad สองฝั่งมีความสามารถในการระบายความร้อนไม่เท่ากัน (ฝั่งนึงต่อ Plane ใหญ่, ฝั่งนึงต่อ Trace เล็ก)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **熱対策 (Netsu Taisaku):** Thermal Management (การจัดการความร้อน)
- **ビア埋め (Bia Ume) / 樹脂埋め (Jushi Ume):** Via Plugging / Resin Plugging (การอุดรูเวีย)
- **熱逃げ (Netsu Nige):** Thermal Relief (การระบายความร้อน/การลดการถ่ายเทความร้อนที่ Pad)
- **反り (Sori):** Warpage (การโก่งตัวของบอร์ด)
- **マンハッタン現象 (Manhattan Genshou):** Tombstone Effect (ปรากฏการณ์อุปกรณ์ตั้งขึ้นตอนบัดกรี)

## ควิซท้ายบท (Quiz)
**คำถาม:** ปรากฏการณ์ที่ตะกั่วไหลลงไปใน Thermal Via ใต้ Thermal Pad ของ IC ทำให้ตะกั่วไม่พอเรียกว่าอะไร และแก้ไขด้วยเทคนิคใด (ระบุคำศัพท์ภาษาญี่ปุ่น)?
**เฉลย:** เรียกว่า Solder Wicking แก้ไขด้วยการทำ Resin Plugging (樹脂埋め - Jushi Ume) และ Plated Over (POFV) เพื่อปิดรูเวียให้เรียบ
