# 053: PCB Thermal Management - Part 3: Heatsinks, TIMs, and Component Placement
## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
1. **Thermal Interface Material (TIM):** สิ่งที่อยู่ระหว่าง IC กับ Heatsink. หน้าที่หลักคือเติมเต็มช่องว่างของอากาศ (Air gap) ซึ่งอากาศเป็นฉนวนความร้อนชั้นดี. ค่า Thermal Resistance รวม ($R_{total}$) = $R_{jc} + R_{tim} + R_{heatsink}$. TIM มีหลายแบบ (Thermal Paste, Pad, Phase Change). การกด TIM ด้วยแรงที่เหมาะสม (Mounting pressure) สำคัญมาก ถ้าน้อยไป การสัมผัสไม่ดี ถ้ามากไป บอร์ดโก่ง.
2. **Component Placement Strategy:** ไม่ควรวาง Component ที่สร้างความร้อนสูง (เช่น Power FETs, LDOs) ไว้กระจุกตัวกัน (Hotspot) ควรวางกระจายกันและให้อยู่ใกล้ขอบบอร์ด หรือในทิศทางของ Airflow (ถ้ามีพัดลม).

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **Thermal Shadowing:** ถ้าระบบมี Airflow (Fan), อย่าวาง Component ตัวใหญ่ (เช่น Capacitor) บังทิศทางลมของตัวที่ต้องการระบายความร้อน (เช่น CPU/Heatsink).
- **TIM Thickness:** อย่าใช้ Thermal Pad หนากว่าความจำเป็น เพราะยิ่งหนา Thermal Resistance ยิ่งสูง เลือกความหนาที่พอดีกับการยุบตัว (Compression) ที่สเปคกำหนด (ปกติบีบอัดประมาณ 10-30%).

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ヒートシンク (Hiito Shinku):** Heatsink
- **放熱シート (Hounetsu Shiito):** Thermal pad (TIM)
- **風流 (Fuuryuu):** Airflow (ทิศทางลม)
- **熱干渉 (Netsukanshou):** Thermal interference (ความร้อนจากตัวหนึ่งรบกวนอีกตัว)

## ควิซท้ายบท (Quiz)
1. ข้อใดคือจุดประสงค์หลักของ TIM (Thermal Interface Material)?
   a) เพิ่มความสวยงาม
   b) ขจัด Air gap ระหว่าง IC และ Heatsink เพื่อลด Thermal resistance
   c) ป้องกันไฟฟ้าสถิต (ESD)
   d) ยึด Heatsink ให้ติดกับบอร์ด
*(เฉลย: b)*
