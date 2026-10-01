# บทที่ 8: Power Integrity (PI) & Power Delivery Network (PDN) - ระดับ Senior

## ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
Power Integrity ไม่ใช่แค่เรื่องการเดินสายไฟให้ใหญ่พอ แต่คือการออกแบบ PDN Impedance ให้ต่ำกว่า Target Impedance ตลอดช่วงความถี่กว้าง (DC ถึง GHz) การวาง Decoupling Capacitors ต้องวิเคราะห์ ESL (Equivalent Series Inductance) รอยต่อ BGA breakout, Via placement, และ Plane capacitance มีผลต่อ High-Frequency PI อย่างมาก การทำ PDN Simulation (AC Impedance & DC IR Drop) เป็นสิ่งจำเป็นในการยืนยันเสถียรภาพของ Power

## ทริคหน้างาน OJT (現場のコツ)
- **Decap Placement**: การวาง Decap แค่ใกล้ IC ไม่พอ ทิศทางการวาง Via ของ Decap สำคัญมาก ควรวาง Via แบบ "Via-in-pad" (ถ้าต้นทุนบอร์ดอนุญาต) หรือวาง Via ติด Pad ให้ชิดที่สุด และให้กระแสไหลจาก Plane -> Via -> Cap -> IC (หลีกเลี่ยงการเกิด Parasitic loop inductance)
- **IR Drop**: อย่าวางใจเพียงแค่โพลีกอนกว้างๆ หากมี Via จำนวนมากขวางทาง (Swiss-cheese effect) พื้นที่หน้าตัดทองแดงอาจลดลงจนทำให้เกิดคอขวด (Bottleneck) และแรงดันตก

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語 - けんずようご)
- **電源品質 (Dengen hinshitsu):** Power Integrity (PI) / คุณภาพของระบบจ่ายไฟ
- **電圧降下 (Den'atsu kōka):** IR Drop / Voltage Drop / แรงดันตก
- **バイパスコンデンサ (Baipasu kondensa):** Bypass Capacitor (Decap) / ตัวเก็บประจุบายพาส (มักเรียกสั้นๆ ว่า バイコン - Baikon)
- **寄生インダクタンス (Kisei indakutansu):** Parasitic Inductance / อินดักแตนซ์แฝง
- **ベタパターン (Beta patān):** Copper Pour / Solid Plane / พื้นที่ทองแดงทึบ

## ควิซท้ายบท (確認テスト)
1. ปัจจัยใดที่มีผลเสียต่อ High-Frequency Power Integrity มากที่สุดเมื่อต่อ Decoupling Capacitor?
   a) ค่า Capacitance ที่สูงเกินไป
   b) Loop Inductance (ESL) จากรอยเชื่อมต่อ Via และ Trace
   c) ชนิดของ Dielectric material ของ Capacitor (เช่น X7R)
   d) การใช้ Plane capacitance

*(เฉลย: b - ค่า ESL ที่สูงจะทำให้ Impedance ของ PDN เพิ่มขึ้นอย่างรวดเร็วในย่านความถี่สูง)*
