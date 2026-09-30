# Advanced PCB Stackup - Part 3: Power Integrity & Return Paths

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Stackup มีผลอย่างมากต่อ Power Integrity (PI) โดยเฉพาะในวงจรที่ใช้ชิปความเร็วสูงที่มีการดึงกระแสฉับพลัน (High di/dt)
- **Planar Capacitance:** การวางชั้น Power และ GND ไว้ติดกันด้วย Dielectric ที่บางมากๆ (เช่น 2-3 mil หรือวัสดุจำพวก FaradFlex) จะสร้างตัวเก็บประจุแบบระนาบ (Interplane capacitance) ที่ตอบสนองได้เร็วในย่านความถี่สูง (High-frequency decoupling) ซึ่งตัวเก็บประจุแบบ SMD (MLCC) ธรรมดาทำไม่ได้เนื่องจากมี Equivalent Series Inductance (ESL)
- **Return Path:** กระแสไฟฟ้าไม่ได้วิ่งไปอย่างเดียว แต่มันต้อง "กลับ" เสมอ ในย่านความถี่ต่ำ Return path จะเลือกเส้นทางที่มี Resistance ต่ำสุด แต่ในย่านความถี่สูง มันจะเลือกเส้นทางที่มี **Inductance ต่ำสุด** ซึ่งก็คือระนาบอ้างอิงที่อยู่ใกล้ Trace นั้นมากที่สุดตรงๆ ข้างใต้สายสัญญาณ

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **การเรียงชั้นแบบ GND-PWR-GND (サンドイッチ構造):** การประกบชั้น Power ไว้ระหว่าง GND สองชั้นช่วยจำกัด Noise ที่เกิดจาก Power plane ไม่ให้แผ่ออกไปยังสายสัญญาณชั้นอื่นได้ดีเยี่ยม (Shielding)
- **ระวัง Via กีดขวาง Return Path (ビアの壁):** การวาง Via ถี่ๆ ติดกันเพื่อเชื่อม Ground (เช่น BGA breakout) บางครั้งเจาะทำลายระนาบชั้นในจนเกิดรอยขาดคล้ายสวิสชีส (Swiss-cheese effect) ทำให้ Return path ต้องอ้อม เกิดปัญหา Signal Integrity (SI) ตามมา ต้องจัดระยะห่างระหว่าง Via (Anti-pad) ให้มีเนื้อทองแดงเชื่อมถึงกันได้

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **電源層 (Dengen-sou):** Power plane / ชั้นไฟ
- **GND層 (Gurando-sou):** Ground plane / ชั้นกราวด์
- **リターンパス (Ritaan-pasu):** Return path / เส้นทางกระแสไหลกลับ
- **層間容量 (Soukan-youryou):** Interplane capacitance / คาปาซิแตนซ์ระหว่างชั้น
- **ベタパターン (Beta-pataan):** Solid plane / Solid copper pour / การเททองแดงแบบเต็มทึบ

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** การวางชั้น Power และ Ground ไว้ติดกัน (Adjacent) ให้ผลดีอย่างไรต่อระบบความถี่สูง?
1. ลดการสูญเสียกำลังงาน DC
2. เพิ่มความสวยงามของบอร์ด
3. สร้าง Interplane Capacitance ช่วยทำ Decoupling ที่ความถี่สูง
4. ทำให้บอร์ดระบายความร้อนได้แย่ลง

*เฉลย: 3*
