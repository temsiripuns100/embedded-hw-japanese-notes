# Lesson 7: Power Delivery Network (PDN) and Decoupling Strategy (電源供給網とパスコン配置)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เป้าหมายของ PDN ที่ดีคือการรักษาระดับแรงดันให้คงที่ ภายใต้สภาวะที่มีการดึงกระแสแบบชั่วขณะ (Transient current) อย่างรวดเร็วจาก IC 
- **Target Impedance ($Z_{target}$):** ต้องออกแบบ PDN ให้มี Impedance ต่ำกว่า Target Impedance ตั้งแต่ DC ไปจนถึงความถี่สูงสุดที่ระบบทำงาน
- **Decoupling Capacitors:** ไม่ใช่แค่การ "กรอง" แต่เป็นการทำหน้าที่เป็น "แหล่งจ่ายประจุชั่วคราว" ที่อยู่ใกล้ IC มากที่สุด การเลือกค่า C (Bulk, High-frequency) และแพ็กเกจ (0402, 0201) มีผลต่อ Equivalent Series Inductance (ESL) ซึ่ง ESL นี้เองที่เป็นตัวขัดขวางการจ่ายกระแสความถี่สูง
- **Plane Capacitance:** การวาง Power Plane ให้ชิดกับ Ground Plane มากๆ (เช่น ระยะห่าง < 4 mil) จะสร้าง Capacitance ธรรมชาติที่มี ESL ต่ำมาก ซึ่งสำคัญมากสำหรับความถี่ระดับ GHz

## ทริคหน้างาน OJT (On-the-Job Tricks)
- การวาง Decoupling Capacitor: วางตัวเล็ก (ความจุต่ำ/แพ็กเกจเล็ก) ให้ใกล้ขา IC ที่สุด แล้วค่อยไล่ตัวใหญ่ (Bulk) ออกมา
- การเดินเส้นทาง (Routing) ไปยัง C: ควรใช้ Via ให้อยู่ใกล้ Pad ของ C มากที่สุด (Via-in-pad ถ้าโรงงานทำได้ หรือวางชิด Pad) เพื่อลด Loop Inductance
- การแบ่ง Power Island (電源分割): ต้องระวังการ overlap กับสัญญาณความเร็วสูงบนชั้นติดกัน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **パスコン (Pasukon):** Decoupling capacitor (มาจาก Bypass Capacitor)
- **電源分割 (Dengen bunkatsu):** Power plane split / Island
- **ノイズ対策 (Noizu taisaku):** Noise countermeasure (การจัดการนอยส์)
- **実装面積 (Jissou menseki):** พื้นที่ลงอุปกรณ์ (Mounting area)

## ควิซท้ายบท (Quiz)
1. ESL ใน Capacitor มีผลเสียอย่างไรต่อการออกแบบ PDN?
2. Plane Capacitance เกิดจากอะไร และมีประโยชน์อย่างไรในช่วงความถี่สูง?
