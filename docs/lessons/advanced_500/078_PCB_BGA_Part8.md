# Lesson 078: BGA Power Integrity - PDN and Decoupling Capacitors

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การวาง Power Delivery Network (PDN) สำหรับ BGA ขนาดใหญ่ (เช่น FPGA, CPU) ต้องการ Target Impedance ต่ำครอบคลุมตั้งแต่ DC จนถึงหลายร้อย MHz
- **Decoupling Placement**: ตัวเก็บประจุ (Capacitors) ที่มีความจุต่ำ (High frequency) ควรวางไว้ใกล้ BGA pins มากที่สุด หรือใต้บอร์ดตรงข้ามกับ BGA (Bottom side) เพื่อลด Loop Inductance ให้เหลือน้อยที่สุด
- **Plane Assignment**: Power plane และ Ground plane ควรวางชิดกัน (Closely coupled planes) เพื่อเพิ่ม Inter-plane capacitance ซึ่งทำหน้าที่เป็น High-frequency bypass ชั้นเยี่ยม โดยไม่มี ESL (Equivalent Series Inductance) ของชิ้นส่วนมารบกวน

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick**: ระวังเรื่อง "Via Sharing" ตอนต่อ Decoupling Caps. การแชร์ Via 1 รู ให้ Cap 2 ตัว อาจดูประหยัดพื้นที่ แต่จะทำให้ Inductance รวมสูงขึ้น (ESL) ให้ใช้ Via อย่างน้อย 1 คู่ (Power + Ground) ต่อ 1 Pad ของ Cap เสมอเพื่อลด Inductance ให้ต่ำสุด
- **IR Drop Analysis**: ในดีไซน์กระแสสูง ต้องรัน DC IR Drop เพื่อดูว่าคอขวด (Bottleneck) ของทองแดงบริเวณ BGA Anti-pad ทำให้กระแสกระจุกตัวจนความร้อนพุ่ง (Current density limits) หรือไม่

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **電源品質 (Dengen hinshitsu)**: Power Integrity (PI)
- **デカップリングコンデンサ (Dekappuringu kondensa)**: Decoupling capacitor (มักเรียกย่อว่า バイパスコン - Bypass con)
- **インダクタンス (Indakutansu)**: Inductance
- **電圧降下 (Den'atsu kouka)**: Voltage drop / IR Drop
- **電流密度 (Denryuu mitsudo)**: Current density

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: ปัจจัยใดที่ขัดขวางไม่ให้ High-frequency Decoupling Capacitor ทำงานได้อย่างมีประสิทธิภาพที่สุดเมื่อวางไว้ใต้ BGA?
A. ค่า ESR ของตัวเก็บประจุต่ำเกินไป
B. Loop Inductance จาก Via และรอยเชื่อมที่มากเกินไป
C. Inter-plane capacitance มีค่าสูงเกินไป
D. การเลือกใช้ตัวเก็บประจุแบบ X7R
**เฉลย**: B. Inductance ของ Via และเส้นทางเดินสาย (Mounting Inductance) เป็นตัวจำกัดความถี่ตอบสนอง การวาง Cap ใต้ BGA เป้าหมายคือทำให้ Loop นี้สั้นที่สุด
