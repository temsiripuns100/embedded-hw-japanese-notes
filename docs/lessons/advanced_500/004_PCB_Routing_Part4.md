# 004 PCB Routing Part 4: Via Placement & Stubs (ビア配置とスタブ)

## ทฤษฎีวิศวกรรมเชิงลึก (In-Depth Engineering Theory)
Via คือจุดเชื่อมต่อระหว่างชั้น (Layer) แต่มันทำหน้าที่เป็นเสมือน Discontinuity ทาง Impedance และทำให้เกิด Parasitic Capacitance/Inductance
- **Via Stub**: ส่วนของ Via ที่ยื่นเกินออกมาจากชั้นเส้นทางที่ใช้งานจริง (เช่น สัญญาณวิ่งจาก L1 ไป L3 แต่ Via ทะลุไปถึง L8, ส่วน L3-L8 คือ Stub)
- **Resonant Frequency**: Via Stub ทำหน้าที่เสมือน Quarter-Wave Resonator ที่ความถี่หนึ่งๆ มันจะทำหน้าที่เหมือน Short Circuit ทำให้สัญญาณดรอปอย่างรุนแรง (Notch Frequency) $\text{Stub Length} \approx \frac{\lambda}{4}$
- **Return Via**: เมื่อสัญญาณเปลี่ยนชั้นผ่าน Via เส้นทาง Return path ใน Reference plane ก็ต้องเปลี่ยนชั้นด้วย หากไม่มีจุดเชื่อมต่อให้ Return path สัญญาณจะเกิด Loop Area ใหญ่ขึ้น

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **Backdrilling (Controlled Depth Drilling)**: หากมี Stub ยาวในวงจร High-Speed (> 10Gbps) ให้สั่งโรงงานทำ Backdrilling เพื่อเจาะเอา Stub ทิ้ง
- **Blind/Buried Vias**: การใช้ HDI technology เพื่อลด Stub ตั้งแต่แรก แม้จะแพงกว่า
- **วาง Return Via เสมอ**: เมื่อเดินสายความถี่สูงเปลี่ยนชั้น (เช่น L1 ไป L4 ซึ่งมี L2, L3 เป็น GND Plane) ให้วาง GND Via ใกล้ๆ กับ Signal Via เสมอ (ระยะ < 1mm) เพื่อเป็นทางเดินให้ Return current

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **スタブ (Sutabu)**: Via stub
- **バックドリル (Bakkudoriru)**: Backdrilling
- **リターンビア (Ritān Bia)**: Return via / Transition via
- **貫通ビア (Kantsū Bia)**: Through-hole via
- **IVH / ブラインドビア (Aibui-eichi / Buraindo Bia)**: Interstitial Via Hole / Blind via

## ควิซท้ายบท (Quiz)
**คำถาม:** การวาง Return Via (GND Via) ข้างๆ Signal Via เมื่อมีการเปลี่ยนชั้นของสายสัญญาณความถี่สูง มีจุดประสงค์หลักเพื่ออะไร?
1. ลดค่าความต้านทาน (Resistance) ของสาย
2. ระบายความร้อนออกจาก Signal Via
3. สร้างเส้นทางต่อเนื่องให้กับ Return Current เพื่อป้องกันปัญหา Signal Integrity และ EMI
**เฉลย:** ข้อ 3
