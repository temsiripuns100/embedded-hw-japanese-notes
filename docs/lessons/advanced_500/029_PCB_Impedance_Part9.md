# Advanced PCB Impedance Part 9: Impedance Discontinuities & TDR (インピーダンス不連続性とTDR)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ทุกๆ จุดที่รูปทรงเรขาคณิตของเส้นสัญญาณเปลี่ยนไป เช่น Connector pads, Vias, หรือจุดแยกต่างๆ จะเกิดการเปลี่ยนแปลงของ Capacitance และ Inductance ที่เรียกว่า Impedance Discontinuity
เครื่องมือระดับวิศวกร Senior ที่ใช้วัดและวิเคราะห์ปัญหานี้คือ TDR (Time Domain Reflectometer) TDR จะส่ง Pulse เข้าไปในสายและรับสัญญาณสะท้อน (Reflection) กลับมา หากเจอ Capacitive load (เช่น Pad ใหญ่ๆ) กราฟ TDR จะ "ดรอปลง" (Dip) หากเจอ Inductive load (เช่น Via stub ยาวๆ หรือรอยคอด) กราฟ TDR จะ "พุ่งขึ้น" (Spike) การทำ Impedance Matching ให้สำเร็จ คือการออกแบบให้กราฟ TDR เรียบที่สุดเท่าที่เป็นไปได้

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- เมื่อต้องเชื่อมต่อเส้นสัญญาณเข้ากับ Surface Mount Pad ของ Connector ขนาดใหญ่ Pad นั้นจะมี Capacitance ค่อนข้างสูง (กราฟ TDR ตก) วิธีแก้คือการ "คว้าน" (Cut-out / Void) Ground Plane ที่ชั้นด้านล่างใต้ Pad นั้นโดยตรง เพื่อเพิ่มระยะทางระหว่าง Pad และ Ground ซึ่งจะช่วยลด Parasitic Capacitance ยกระดับ Impedance ให้กลับมาสมดุล (TDR Flat)
- ลบ Via stub ด้วยกระบวนการ Back-drill ในสัญญาณ > 5Gbps เพื่อไม่ให้เกิด Resonance ที่จะดึงสัญญาณล่มทั้งแบนด์

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **不連続性 (Furenzokusei):** Discontinuity
- **反射 (Hansha):** Reflection
- **パッドの肉抜き (Paddo no nikunuki):** Pad void / Cut-out (คว้านเนื้อทองแดงออก)
- **スタブ (Sutabu):** Stub (ส่วนปลายสายที่ยื่นเกินไป)
- **波形 (Hakei):** Waveform

## ควิซท้ายบท (Quiz)
**Q:** หากดูกราฟ TDR บริเวณคอนเนคเตอร์ แล้วพบว่ากราฟ "ดรอปลง" ต่ำกว่า 50 โอห์ม (Dip) ควรแก้ไขด้วยวิธีใดทาง Layout?
1. เพิ่มความกว้างของเส้นสัญญาณก่อนเข้าคอนเนคเตอร์
2. คว้าน Ground (Void) ในชั้นที่อยู่ใต้ Pad ของคอนเนคเตอร์
3. เพิ่มตัวต้านทาน 50 โอห์มต่อขนานที่พิน
**Ans:** 2. คว้าน Ground (Void) ในชั้นที่อยู่ใต้ Pad ของคอนเนคเตอร์ (ลด Parasitic Capacitance)
