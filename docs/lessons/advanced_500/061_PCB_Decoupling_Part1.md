# Lesson 061: PCB Decoupling Part 1 - Fundamentals of Power Distribution Network (PDN)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior Engineer เราไม่มอง Decoupling Capacitor เป็นแค่ "C คร่อมไฟ" อีกต่อไป แต่เรากำลังออกแบบ **Power Distribution Network (PDN)** เป้าหมายหลักคือการรักษา Target Impedance ($Z_{target}$) ให้ต่ำกว่าค่าที่กำหนดในทุกช่วงความถี่ตั้งแต่ DC ไปจนถึงหลาย GHz
สูตรพื้นฐาน: $Z_{target} = \frac{\Delta V_{noise}}{I_{transient}}$
เราต้องเข้าใจว่า IC สมัยใหม่ที่มีความเร็วสูง (High-Speed Digital) จะดึงกระแสแบบ Transient (di/dt) ซึ่งหาก PDN มีค่า Inductance (ESL + Trace Inductance) สูง จะทำให้เกิด Voltage Drop ($V = L \frac{di}{dt}$) ที่ขา IC นำไปสู่ปัญหา Signal Integrity (SI) และ EMI

## ทริคหน้างาน OJT (OJT Field Tricks)
- **อย่าไว้ใจ Auto-Router:** เวลาวาง Decoupling Cap ให้วางด้วยมือเสมอ วางให้ใกล้ขา Power (VCC/VDD) และ Ground ของ IC มากที่สุด
- **มองหา "ขวดโหล":** จินตนาการว่า Decoupling Cap เป็นถังน้ำเล็กๆ ใกล้ๆ IC เมื่อ IC ต้องการน้ำ (กระแส) กะทันหัน ถังน้ำนี้ต้องจ่ายน้ำให้ทันก่อนที่น้ำจากถังใหญ่ (Power Supply) จะเดินทางมาถึง
- **ระวัง Via:** การเจาะ Via เพื่อต่อ C ลง Plane มีผลต่อ Inductance (Loop Inductance) มากกว่าระยะห่างบนแกน X-Y เสียอีก!

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **PDN (電源分配ネットワーク - Dengen Bunpai Nettowaaku):** Power Distribution Network
- **バイパスコンデンサ / パスコン (Baipasu Kondensa / Pasukon):** Bypass Capacitor / Decoupling Capacitor
- **インピーダンス (Inpiidansu):** Impedance
- **電圧降下 (Den'atsu Kouka):** Voltage Drop
- **過渡応答 (Kato Outou):** Transient Response

## ควิซท้ายบท (Quiz)
1. สาเหตุหลักที่ทำให้เกิด Voltage Drop เมื่อ IC ดึงกระแสแบบรวดเร็วคืออะไร?
2. Target Impedance คืออะไร และมีวิธีคำนวณเบื้องต้นอย่างไร?
(เฉลยอยู่ในบทเรียนถัดไป)
