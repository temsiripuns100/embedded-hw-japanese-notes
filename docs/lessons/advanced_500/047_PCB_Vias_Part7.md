# Lesson 047: PCB Vias Part 7 - Via Stub Effect and Backdrilling

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
Via Stub คือส่วนของ Via ที่ยื่นเกินจาก Layer ที่สัญญาณใช้งานจริง ทำตัวเหมือน Open-ended transmission line เกิดการสะท้อนกลับของสัญญาณ (Reflection) และสร้าง Quarter-wave resonance ซึ่งทำให้เกิด Signal Attenuation อย่างรุนแรงที่ความถี่เฉพาะ (Resonant frequency) การแก้ปัญหาคือใช้เทคนิค Backdrilling (การเจาะคว้าน) เอาเนื้อทองแดงส่วน Stub ทิ้ง หรือใช้ Blind/Buried Vias แทน

## ทริคหน้างาน OJT
เวลาสั่งทำ Backdrill อย่าลืมเช็ค Clearance จากรู Backdrill ไปยัง Trace ข้างเคียงด้วย เพราะดอกสว่าน Backdrill จะใหญ่กว่ารู Via ปกติประมาณ 6-8 mils เสมอ พลาดตรงนี้ short แน่นอน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図)
- **スタブ (Sutabu):** Stub (ส่วนปลายที่เหลืออยู่)
- **バックドリル (Bakku-doriru):** Backdrilling
- **共振 (Kyoushin):** Resonance

## ควิซท้ายบท
Q: เหตุใดจึงต้องทำ Backdrilling ในบอร์ด High-speed?
A: เพื่อลด Via Stub ซึ่งทำให้เกิด Signal Resonance และ Reflection
