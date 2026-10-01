# Lesson 055: PCB Thermal Part 5 - Thermal Simulation and Testing (Thermography)

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
Thermal Simulation (เช่น Flotherm, Icepak) ใช้แก้สมการ CFD ควบคู่กับความร้อน ช่วยทำนายจุด Hotspot ล่วงหน้าก่อนสร้างบอร์ดจริง ส่วนการทดสอบจริงมักใช้ Thermal Camera (IR Camera) หรือ Thermocouple จุดระวังในการใช้ IR Camera คือค่า Emissivity (ε) ของพื้นผิว PCB มักไม่เท่ากัน (Silkscreen, Bare Copper, Solder Mask, ชิปพลาสติก) หากไม่ทาสีดำทับ (Black paint coating) ค่าอุณหภูมิที่วัดได้จะผิดเพี้ยนไปหลายองศา

## ทริคหน้างาน OJT
ก่อนถ่ายภาพความร้อนจาก IR Camera วิศวกรเก๋าๆ จะเอาสเปรย์สีดำด้าน (Matte Black) หรือใช้ Kapton Tape แปะทับบริเวณที่จะวัด เพื่อปรับ Emissivity ให้ใกล้เคียง 0.95 คงที่ทั้งบอร์ด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図)
- **熱解析 (Netsu Kaiseki):** Thermal Analysis / Simulation
- **放射率 (Housha Ritsu):** Emissivity
- **熱電対 (Netsudentai):** Thermocouple

## ควิซท้ายบท
Q: เหตุใดจึงต้องพ่นสีดำด้านบนบอร์ดก่อนใช้ Thermal Camera วัดอุณหภูมิที่แม่นยำ?
A: เพื่อปรับค่า Emissivity ของพื้นผิววัสดุที่แตกต่างกันให้เท่ากัน ป้องกันความคลาดเคลื่อนในการวัด
