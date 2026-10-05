# Lesson 079: BGA Thermal Management & Reliability (CTE Mismatch)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
BGA ที่สร้างความร้อนสูงมักจะประสบปัญหา Thermomechanical stress อันเกิดจาก Coefficient of Thermal Expansion (CTE) Mismatch ระหว่างตัวแพ็กเกจของชิป (Silicon/Substrate) และแผ่น PCB (FR4).
- **Thermal Cycling**: เมื่ออุณหภูมิเปลี่ยนไปมา โครงสร้างจะขยายและหดตัวไม่เท่ากัน ทำให้ Solder Ball ตรงขอบ (Corner balls) รับแรงเฉือน (Shear stress) มากที่สุด และมักเป็นจุดแรกที่มีการแตกร้าว (Fatigue failure)
- **Thermal Vias**: การเจาะรูระบายความร้อนที่ Thermal pad ใต้ BGA สามารถช่วยถ่ายเทความร้อนลงไปยังแผ่นทองแดงชั้นใน (Inner copper planes) ได้อย่างมีประสิทธิภาพ สูตรคือพยายามใช้ Via เล็กๆ จำนวนมาก ดีกว่าใช้ Via ใหญ่ๆ จำนวนน้อย

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick**: หากเจอปัญหา BGA cracking บ่อยในภาคสนาม แนะนำให้พิจารณาทำ Underfill (ฉีดอีพ็อกซี่ใต้ BGA) หรือเปลี่ยนวัสดุ PCB ให้มีค่า Tg (Glass Transition Temperature) สูงขึ้นและ CTE แกน Z/X-Y ต่ำลง
- **Routing at corners**: พยายามหลีกเลี่ยงการเดินเส้น Signal สำคัญๆ ผ่าน Solder ball ที่มุมสุดของ BGA หรือใช้ Redundancy (เดินขนานหลายขาถ้าทำได้สำหรับ Power/GND) เพราะเป็นจุดเสี่ยงสุด

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **熱膨張係数 (Netsubouchou keisuu)**: Coefficient of Thermal Expansion (CTE)
- **クラック (Kurakku)**: Crack / รอยร้าว
- **熱衝撃 (Netsushougeki)**: Thermal shock
- **アンダーフィル (Andaafiru)**: Underfill
- **放熱ビア (Hounetsu bia)**: Thermal via

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: Solder ball บริเวณใดของ BGA ที่เสี่ยงต่อการแตกร้าวมากที่สุดจากวัฏจักรความร้อน (Thermal cycling)?
A. ตรงกลาง (Center balls)
B. แถวในสุดรอบๆ ตรงกลาง
C. บริเวณมุมด้านนอกสุด (Corner balls)
D. แถวที่รับไฟ Power/Ground โดยเฉพาะ
**เฉลย**: C (Corner balls) เพราะมีระยะห่างจากจุดศูนย์กลาง (Distance from Neutral Point - DNP) มากที่สุด ทำให้การกระจัดสัมพัทธ์จากการขยายตัวมีค่าสูงสุด เกิดแรงเฉือนมากที่สุด
