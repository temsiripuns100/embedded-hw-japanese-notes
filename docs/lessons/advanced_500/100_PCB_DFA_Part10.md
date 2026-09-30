# PCB DFA Part 10: DFA Validation, SPC, and Zero-Defect Strategies

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Senior Engineer จะไม่รอให้บอร์ดผลิตเสร็จแล้วค่อยแก้ปัญหา แต่จะนำ Statistical Process Control (SPC) และ Design Rule Checking (DRC/DFA Check) Software มาใช้ตั้งแต่ขั้นออกแบบ 
- **Tolerance Analysis:** การคำนวณ Stack-up tolerance ไม่ใช่แค่ความหนาบอร์ด แต่รวมถึง Component placement tolerance จากเครื่อง Pick-and-Place ผนวกกับ PCB Fabrication tolerance. 
- **DFM/DFA Software (e.g., Valor NPI):** การทำ Virtual Prototyping เพื่อจำลองหาจุดชน (Collisions), การวิเคราะห์ Solder Joint Reliability (SJR), และการประเมิน Yield ของกระบวนการผลิต

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **DFM Report Review:** เมื่อได้รับ DFM Report จากผู้ผลิต (Fab house / EMS) อย่าตอบตกลงง่ายๆ (Approve blindy) ให้วิเคราะห์ทุกข้อที่มีการเสนอเปลี่ยนขนาด Pad หรือ Mask opening เพราะมันอาจกระทบ High-speed signal integrity ได้
- **Feedback Loop:** นำข้อมูลจาก SPI (Solder Paste Inspection) และ AOI (Automated Optical Inspection) ในรอบ NPI (New Product Introduction) มาปรับแก้ Footprint library ในบริษัท เพื่อให้บอร์ดรุ่นต่อๆ ไปเป็น Zero Defect

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **歩留まり (Budomari):** Yield / อัตราของดี (Yield rate)
- **公差 (Kousa):** Tolerance / ค่าพิกัดความเผื่อ
- **はんだ印刷 (Handa Insatsu):** Solder paste printing / การพิมพ์ตะกั่ว
- **量産移行 (Ryousan ikou):** Transition to mass production / การส่งมอบเข้าสู่การผลิตจริง
- **不良解析 (Furyou Kaiseki):** Failure Analysis / การวิเคราะห์ของเสีย

## ควิซท้ายบท (Quiz)
**Q:** ระบบ SPI (Solder Paste Inspection) ในไลน์การผลิต มีประโยชน์อย่างไรต่อการทำ DFA Validation?
A) เพื่อตรวจสอบว่าชิ้นส่วนถูกวางตรงตำแหน่งหรือไม่
B) เพื่อวัดปริมาตร พื้นที่ และความหนาของ Solder Paste ที่พิมพ์ลงบน Pad ช่วยยืนยันว่า Stencil Design เหมาะสมหรือไม่
C) ตรวจสอบความถูกต้องของซอร์สโค้ดในไมโครคอนโทรลเลอร์
**เฉลย:** B) SPI วัดคุณภาพการพิมพ์ตะกั่ว ซึ่งเกี่ยวโยงกับ Stencil design (Aperture) ที่เป็นส่วนสำคัญของ DFA
