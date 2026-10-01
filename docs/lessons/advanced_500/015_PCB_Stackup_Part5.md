# Advanced PCB Stackup Part 5: Return Path & Plane Capacitance (リターンパスとプレーン容量)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในสัญญาณ High-Speed "Return Current" จะไหลในเส้นทางที่มีค่า Impedance ต่ำที่สุด ซึ่งก็คือแผ่น Plane ที่อยู่ติดกับเส้นสัญญาณมากที่สุด (Path of least inductance) 
ปัญหาใหญ่มักเกิดเมื่อสัญญาณต้องเปลี่ยน Layer (Via transition) แล้วทำให้ Return path ถูกขัดจังหวะ (Reference Plane Change) หากเปลี่ยนจาก GND เป็น Power Plane จะเกิด Return Path Discontinuity สิ่งที่ Senior ต้องทำคือเพิ่ม "Stitching Capacitor" บริเวณใกล้ๆ Via เพื่อเชื่อมความถี่สูงระหว่าง Plane ทั้งสอง และการจัด Stackup ที่ดีควรให้ VCC/GND Plane อยู่ใกล้กันมากที่สุด (เช่น < 4 mils) เพื่อสร้าง Inter-Plane Capacitance ที่มีประสิทธิภาพในการเป็น High-frequency Decoupling

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- เมื่อออกแบบ Stackup พยายามจับคู่ (Pair) Signal Layer กับ Solid Ground Plane เสมอ หลีกเลี่ยงการใช้ Power Plane เป็น Reference หากทำได้ เพราะ Power Plane มักมีสัญญาณกวน (Noise) และถูกหั่นเป็น Island ย่อยๆ (Split planes) ทำให้ Return path อ้อม
- วาง GND plane ถัดจาก GND plane หรือ VCC plane ไว้ที่ Center core เพื่อเป็นตัวเก็บประจุแผ่นขนาน (Planar Capacitor) ช่วยแก้อาการ Voltage Ripple ที่ความถี่ระดับหลายร้อย MHz ที่ Bypass cap ธรรมดาส่งพลังงานไม่ทัน

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **リターンパス (Ritān pasu):** Return path
- **プレーン分割 (Purēn bunkatsu):** Plane split / Split plane
- **結合容量 (Ketsugō yōryō):** Coupling capacitance
- **バイパスコンデンサ (Baipasu kondensa):** Bypass capacitor / Decoupling cap (มักเรียกสั้นๆว่า バイコン - Baikon)

## ควิซท้ายบท (Quiz)
**Q:** การบีบความหนาของ Dielectric ระหว่างชั้น Power และ Ground ให้น้อยกว่า 4 mils ให้ผลดีในเรื่องใดมากที่สุด?
1. ลด Crosstalk ระหว่างสัญญาณ
2. เพิ่ม Plane Capacitance เพื่อลด Power Distribution Network (PDN) Impedance ที่ความถี่สูง
3. เพิ่มค่า Characteristic Impedance ของบอร์ด
**Ans:** 2. เพิ่ม Plane Capacitance เพื่อลด PDN Impedance ที่ความถี่สูง
