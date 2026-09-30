# Lesson 41: Advanced PCB Vias - Fabrication & Types (Senior Level)

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
ในระดับ Senior การเลือกใช้ Via ไม่ใช่แค่การเชื่อมต่อ Layer แต่คือการพิจารณา Aspect Ratio (AR) ซึ่งมีผลโดยตรงต่อ Plating thickness ในรูเจาะ (Barrel) โรงงานทั่วไปรับ AR ได้ที่ 8:1 ถึง 10:1 หากสูงกว่านี้ น้ำยา Plating จะเข้าไปเคลือบผนังรูได้ยาก ส่งผลให้เกิด Void หรือ Copper thickness ไม่สม่ำเสมอ นอกจากนี้ ต้องเข้าใจความแตกต่างระหว่าง Mechanical Drilling และ Laser Drilling อย่างลึกซึ้ง

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick:** เมื่อออกแบบบอร์ดที่มีความหนามากกว่า 2.0mm ให้ตรวจสอบ Tolerance ของดอกสว่านเสมอ หากใช้ Via hole size เล็กเกินไป ดอกสว่านจะหักบ่อย (Drill Breakage) และโรงงานจะขอเพิ่ม Cost หรือเปลี่ยนขนาดรูเจาะ
- **Design Review Check:** ตอนตรวจแบบ (検図) ให้เช็คว่ามี Via วางอยู่ใกล้ขอบบอร์ด (Board Edge) เกินไปหรือไม่ เพราะตอนทำ V-cut หรือ Routing อาจทำให้ Via แตกได้ (Crack)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ビア (Bia):** Via
- **アスペクト比 (Asupekuto-hi):** Aspect Ratio
- **めっき (Mekki):** Plating
- **ドリル折れ (Doriru ore):** Drill Breakage
- **基板端面 (Kiban tanmen):** Board Edge / ปลายขอบบอร์ด

## ควิซท้ายบท (Quiz)
**Q1:** หากบอร์ดหนา 1.6mm และ Aspect Ratio สูงสุดที่โรงงานทำได้คือ 8:1 ขนาด Drill size ที่เล็กที่สุดที่ยอมรับได้คือเท่าไร?
1. 0.15mm
2. 0.20mm
3. 0.25mm
4. 0.30mm
*(เฉลย: 2. 0.20mm)*
