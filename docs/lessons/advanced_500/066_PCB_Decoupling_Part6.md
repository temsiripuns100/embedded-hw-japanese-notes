# PCB Decoupling Part 6: PDN Impedance Optimization

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Power Delivery Network (PDN) Impedance Optimization คือการออกแบบโครงข่ายจ่ายไฟให้มีค่า Impedance ($Z_{PDN}$) ต่ำกว่า Target Impedance ($Z_{target}$) ในทุกช่วงความถี่ใช้งานจนถึงความถี่สูงสุดที่วงจรตอบสนอง (Bandwidth)
สมการ: $Z_{target} = \frac{\Delta V}{I_{transient}}$
การเลือกใช้ตัวเก็บประจุ (Capacitors) ในโครงข่าย PDN ไม่ใช่เพียงการเพิ่มความจุ (Capacitance) แต่คือการจัดการกับ ESL (Equivalent Series Inductance) และ ESR (Equivalent Series Resistance) เพื่อควบคุมพฤติกรรมในโดเมนความถี่

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **การวาง C แบบ Multi-value:** ไม่ควรวางค่า C ต่างกันมากๆ (เช่น 10uF คู่กับ 100pF) โดยไม่คำนึงถึง ESR เพราะอาจเกิด Peak ของ Antiresonance ที่ทำให้ PDN Impedance พุ่งสูงในย่านความถี่เฉพาะ แนะนำให้ดู Simulation ใน HyperLynx หรือ SIwave ก่อนตัดสินใจ
- **การวางขั้ว (Via placement):** พยายามเจาะ Via ให้ใกล้ Pad ของ C มากที่สุด และให้ขั้วบวกและลบอยู่ชิดกัน (Side-by-side or end-to-end close vias) เพื่อทำ Mutual Inductance cancellation ซึ่งจะช่วยลด ESL โดยรวม

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
1. **Target Impedance:** 目標インピーダンス (Mokuhyou inpiidansu)
2. **Transient Current:** 過渡電流 (Kato denryuu)
3. **Decoupling Capacitor:** パスコン (Pasukon - Bypass Capacitor)
4. **Antiresonance:** 反共振 (Hankyoushin)
5. **Via Placement:** ビア配置 (Bia haichi)

## ควิซท้ายบท (Quiz)
**คำถาม:** การเจาะ Via แบบใดช่วยลด ESL ได้ดีที่สุดสำหรับ Decoupling Capacitor ขนาด 0402?
1. เจาะแยกไกลๆ เพื่อลดสัญญาณรบกวน
2. เจาะ Via ด้านข้าง Pad ทันทีและให้ Via ของ VCC/GND ชิดกัน
3. ใช้ Via ขนาดใหญ่ที่สุดเพียง 1 รูตรงกลาง
4. เดิน Trace ยาวๆ แล้วค่อยเจาะ Via

*เฉลย:* ข้อ 2 (เจาะ Via ด้านข้าง Pad ทันทีและให้ Via ของ VCC/GND ชิดกัน) เพื่อให้เกิด Mutual Inductance cancellation
