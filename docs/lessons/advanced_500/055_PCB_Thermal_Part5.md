# 055: PCB Thermal Management - Part 5: Advanced Techniques and Case Studies
## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
1. **Metal Core PCB (MCPCB) / Aluminum PCB:** สำหรับงานที่ร้อนจัดอย่าง High-Power LED หรือ Automotive. ใช้แผ่นอะลูมิเนียมเป็นแกนกลางและมีชั้น Dielectric นำความร้อนอยู่ใต้ Copper. ระบายความร้อนดีมากแต่ทำ Multi-layer ยาก.
2. **Heavy Copper PCB:** การใช้ทองแดงหนา 3 oz, 4 oz หรือมากกว่าในชั้น Layer เพื่อรองรับกระแสสูงและช่วยกระจายความร้อน (Current carrying capacity & Thermal Spreading). ปัญหาคือเรื่อง Manufacturing tolerance ตอนกัดปริ้น (Etching) ต้องเผื่อระยะห่าง (Clearance) มากขึ้น.
3. **Heat Pipes & Vapor Chambers:** การใช้ Phase change cooling แบบฝัง หรือแนบกับ PCB ดึงความร้อนออกจากชิปไปสู่ครีบระบายความร้อนได้เร็วกว่าโลหะตันหลายสิบเท่า.

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **Cost vs Performance:** ในการ Design Review ให้คำนึงถึงต้นทุนเสมอ. การสั่งทำ PCB ทองแดง 4 oz หรือ MCPCB มีราคาแพงมาก. บางครั้งบอร์ด FR4 ธรรมดาที่มี Via ถี่ๆ และ Heatsink เล็กๆ อาจถูกกว่ามาก ต้อง Trade-off ให้ดี.
- **Fail-Safe Mechanism:** ออกแบบวงจรป้องกันเสมอ (Thermal Shutdown) ด้วย NTC Thermistor หรือ Temp Sensor IC ใกล้ๆ Hotspot. หากความร้อนพุ่งเกินพิกัด ระบบต้องตัดโหลดตัวเองได้ทันที.

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **アルミ基板 (Arumi Kiban):** Aluminum substrate PCB (MCPCB)
- **厚銅 (Atsudou):** Heavy copper
- **温度保護 (Ondohogo):** Thermal protection (การป้องกันอุณหภูมิเกิน)
- **原価低減 (Genka Teigen):** Cost reduction (การลดต้นทุน - สำคัญตอน Trade-off)

## ควิซท้ายบท (Quiz)
1. ข้อใดคือข้อเสียหลักของการเลือกใช้ Heavy Copper PCB (เช่น 4 oz) เมื่อเทียบกับ PCB ปกติ?
   a) นำความร้อนได้แย่ลง
   b) รับกระแสไฟฟ้าได้น้อยลง
   c) ต้นทุนสูงและต้องการระยะ Clearance ระหว่างลายวงจรมากขึ้น
   d) ทำให้บอร์ดงอง่าย
*(เฉลย: c)*
