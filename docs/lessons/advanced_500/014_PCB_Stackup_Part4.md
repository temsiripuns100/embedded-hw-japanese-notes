# Advanced PCB Stackup - Part 4: Power Integrity (PI) & Plane Capacitance (Senior Level)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Power Integrity (PI) คือการออกแบบให้ Target Impedance ของระบบจ่ายไฟ (PDN - Power Delivery Network) ต่ำกว่าที่กำหนดในทุกช่วงความถี่ (DC ถึง GHz)
- **Plane Capacitance (プレーン間容量):** การจัด Stackup ให้ชั้น Power และ Ground อยู่ติดกัน (Adjacent) โดยมีระยะห่างน้อยๆ (เช่น 2-3 mil) จะสร้าง Inter-plane capacitance (Buried capacitance) ที่มีประโยชน์อย่างมหาศาล เพราะมี ESL (Equivalent Series Inductance) ต่ำมาก ช่วยจ่ายกระแส Transient ให้ IC ในช่วงความถี่สูง (100MHz - 1GHz) ได้ดีกว่า Decoupling Capacitor แบบ SMD
- **Loop Inductance:** การจัดวาง Capacitor ต้องคำนึงถึง Via placement การวาง Via ของ C ใกล้กับ Pad และใช้ Via หลายรูต่อ 1 Pad จะช่วยลด Loop Inductance ได้

## 2. ทริคหน้างาน OJT (Field Tricks)
- **OJT Trick 1:** อย่าเอาชั้น Power คู่ Ground ที่อยู่ห่างกันเกิน 5 mil มาหวังพึ่ง PI ที่ความถี่สูง มันแทบไม่ได้ช่วยอะไรเลย หากบอร์ดหนาและจำนวนชั้นจำกัด ให้เลือกประกบ Power/Ground คู่ที่สำคัญที่สุดของ Core CPU/FPGA ให้ชิดกันมากที่สุด (เช่น Layer 4=GND, Layer 5=VDD_CORE ระยะห่าง 2 mil)
- **OJT Trick 2:** Plane cavity resonance ถ้าแผ่น Plane มีขนาดใหญ่ จะเกิดคลื่นนิ่ง (Standing wave) ที่ขอบบอร์ด ทำให้เกิดสัญญาณรบกวนแผ่ออกไป (EMI) สามารถลดได้โดยใช้หลักการ "20H Rule" หรือวาง Stitching vias รอบขอบบอร์ดระยะห่างน้อยกว่าความยาวคลื่น/20

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **電源品質 (Dengen Hinshitsu):** Power Integrity (PI)
- **プレーン間容量 (Purēn-kan yōryō):** Inter-plane capacitance
- **デカップリングコンデンサ (Dekappuringu Kondensa):** Decoupling capacitor
- **ループインダクタンス (Rūpu Indakutansu):** Loop inductance
- **ベタパターン (Beta patān):** Solid copper pour / Plane

**ตัวอย่างประโยคตรวจแบบ:**
"VCCプレーンとGNDプレーンの距離が離れすぎています。高周波でのインピーダンスを下げるため、コア材を薄くしてプレーン間容量を増やしてください。" 
(ระยะห่างระหว่าง VCC Plane กับ GND Plane ห่างเกินไป เพื่อลด Impedance ที่ความถี่สูง กรุณาทำให้ Core material บางลงเพื่อเพิ่ม Inter-plane capacitance ครับ)

## 4. ควิซท้ายบท (Quiz)
**Q1:** ในการออกแบบ PDN (Power Delivery Network) อุปกรณ์ใดทำหน้าที่หลักในการรักษาระดับแรงดันในช่วงความถี่สูงมากๆ (> 500 MHz)?
A) VRM (Voltage Regulator Module)
B) Bulk Capacitors (เช่น Tantalum)
C) Inter-plane Capacitance (Plane ตัวบอร์ดเอง)
*(เฉลย: C) ที่ความถี่สูงมากๆ Capacitor แบบ SMD จะหมดสภาพเพราะ ESL ของตัวถังและ Via ดังนั้น Inter-plane capacitance จึงเป็นแหล่งจ่ายประจุที่มี ESL ต่ำที่สุดที่ช่วยได้)*
