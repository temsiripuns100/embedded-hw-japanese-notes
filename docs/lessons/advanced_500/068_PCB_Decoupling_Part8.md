# PCB Decoupling Part 8: Plane Capacitance & Buried Capacitance

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เมื่อความถี่สูงเกินกว่า 100 MHz พฤติกรรมของ Decoupling Capacitor แบบ Discrete จะถูกจำกัดด้วย Mounting Inductance (ESL จาก Layout และ Via) ทำให้ประสิทธิภาพลดลง ในย่านความถี่สูงหลักหลายร้อย MHz จนถึง GHz แหล่งจ่ายประจุหลักคือ Plane Capacitance (または Embedded Capacitance)
$C = \frac{\epsilon_0 \epsilon_r A}{d}$
โดยที่ $A$ คือพื้นที่ซ้อนทับระหว่าง VCC และ GND Plane และ $d$ คือระยะห่าง การลดระยะ $d$ (เช่นใช้ Core หรือ Prepreg บางลง) จะช่วยเพิ่ม Plane Capacitance และลด Plane Inductance อย่างมีนัยสำคัญ

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Stack-up Design:** ตอนรีวิว Stack-up กับผู้ผลิต PCB (Fab vendor) ควรพยายามให้ Layer ของ Power และ GND อยู่ติดกันมากที่สุดเท่าที่เป็นไปได้ (เช่น 2-3 mil dielectric)
- **Buried Capacitance Materials:** ในงาน High-Speed ที่เข้มงวด อาจพิจารณาใช้วัสดุพิเศษเช่น 3M ECM หรือ FaradFlex ซึ่งให้ค่า Dk สูงและ Dielectric บางมาก (1 mil หรือน้อยกว่า) ช่วยเซฟพื้นที่การวาง C และลด Noise ได้ดีกว่าการใช้ C จำนวนมาก

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
1. **Stack-up:** 層構成 (Sou kousei)
2. **Dielectric Thickness:** 絶縁層厚さ (Zetsuyensou atsusa)
3. **Embedded Capacitor:** 内蔵キャパシタ (Naizou kyapashita)
4. **Mounting Inductance:** 実装インダクタンス (Jissou indakutansu)
5. **Core/Prepreg:** コア材/プリプレグ (Koa zai/Puripuregu)

## ควิซท้ายบท (Quiz)
**คำถาม:** ข้อใดเป็นเหตุผลหลักในการวาง Power Plane และ Ground Plane ให้ชิดกันมากที่สุดใน PCB Stack-up?
1. เพื่อประหยัดความหนาของบอร์ด PCB
2. เพื่อลด Plane Inductance และเพิ่ม Plane Capacitance สำหรับการ Decoupling ที่ความถี่สูง
3. เพื่อให้ง่ายต่อการเจาะ Via
4. เพื่อลดอุณหภูมิของบอร์ด

*เฉลย:* ข้อ 2 (การวางชิดกันจะลด $d$ ในสมการความจุ ทำให้ C เพิ่มขึ้น และลด Loop Inductance ลง ส่งผลดีต่อ High-frequency decoupling)
