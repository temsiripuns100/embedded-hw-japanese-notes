# บทที่ 18: Power Integrity and PDN Design in Stackup (Power Integrity และการออกแบบ PDN)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
ในมุมของ Power Integrity (PI), Stackup ที่ดีคือหัวใจของ Power Delivery Network (PDN) 
- **Planar Capacitance**: การวาง Power Plane และ Ground Plane ให้ชิดกันมากที่สุด (Dielectric บาง เช่น 2-4 mil) จะสร้างค่า Embedded Capacitance ระหว่างเลเยอร์ ช่วยจ่ายกระแสความถี่สูง (High Frequency Transient Current) ได้ดีกว่า Decoupling Capacitor แบบ SMD
- **Loop Inductance**: การลดระยะห่างระหว่าง Layer สัญญาณและ Return Plane รวมถึง Power/Ground Vias เป็นสิ่งที่กำหนด Target Impedance ของระบบ หาก Loop Inductance สูง จะเกิด Power Rail Ripple (Voltage Droop/Overshoot)

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick #1**: กฎทองคำ (Golden Rule) ของ PI คือ "อย่าให้ชั้น Power/Ground ห่างกันเกินความจำเป็น" หากโรงงาน PCB เสนอให้เพิ่มความหนา Prepreg ระหว่าง Power/GND เพื่อลดต้นทุน ต้องค้านทันทีหากบอร์ดมี IC ที่กินไฟกระชากสูง (เช่น FPGA, CPU)
- **OJT Trick #2**: Vias ที่เชื่อม Decap เข้าสู่ Power/GND plane ควรอยู่ใกล้กันที่สุด (Via sharing หรือ Via in Pad) เพื่อลด Parasitic Inductance

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **電源プレーン (Dengen Purēn)**: Power Plane
- **グラウンドプレーン (Guraundo Purēn)**: Ground Plane
- **デカップリングコンデンサ (Dekappuringu Kondensa)**: Decoupling Capacitor
- **寄生インダクタンス (Kisei Indakutansu)**: Parasitic Inductance
- **電圧降下 (Den'atsu Kōka)**: Voltage Drop (IR Drop)

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: วิธีใดมีประสิทธิภาพสูงสุดในการลด Loop Inductance ให้กับตัวเก็บประจุแบบ Decoupling บนแผงวงจรความเร็วสูง?
1. ใช้ Capacitor ที่มีค่าความจุ (Capacitance) สูงมากๆ
2. เพิ่มความหนาของทองแดงบนชั้น Power Plane
3. วางชั้น Power และ Ground ให้อยู่ติดกัน (Adjacent) ใน Stackup และเจาะ Via ให้อยู่ใกล้ Pad มากที่สุด
4. ใช้เส้น Trace ยาวๆ เดินเชื่อมจาก IC ไปยัง Capacitor

*เฉลย: 3. การวางชั้น Power/GND ชิดกันและใช้ Via สั้นๆ จะลด Inductance ได้อย่างมหาศาล ซึ่งสำคัญกว่าค่า C ในการตอบสนองต่อความถี่สูง*
