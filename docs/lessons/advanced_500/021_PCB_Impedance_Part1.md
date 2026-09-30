# Lesson 21: PCB Impedance Control - Transmission Line Theory (伝送線路理論)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในวงจรความถี่สูง (High-speed digital) เมื่อเวลาที่สัญญาณเดินทาง (Flight time) มีค่ามากกว่า 1/6 ของ Rise time สัญญาณ ลายวงจรบน PCB จะไม่สามารถมองเป็นเพียง "สายไฟ" ได้อีกต่อไป แต่จะต้องมองเป็น **Transmission Line (伝送線路 - Densou Senro)** 
Impedance ($Z_0$) ของ Transmission line ขึ้นอยู่กับความต้านทาน (R), ความเหนี่ยวนำ (L), ความจุไฟฟ้า (C), และค่าความนำ (G) ตามสมการ:
$$ Z_0 = \sqrt{\frac{R + j\omega L}{G + j\omega C}} $$
ที่ความถี่สูง $j\omega L \gg R$ และ $j\omega C \gg G$ จะประมาณค่าได้เป็น $Z_0 \approx \sqrt{\frac{L}{C}}$
การควบคุม Characteristic Impedance (特性インピーダンス) ให้คงที่ตลอดสายมีความสำคัญมากเพื่อป้องกัน Signal Reflection (信号反射 - Shingou Hansha) ที่ทำให้เกิด Overshoot, Undershoot และ Ringing

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Rule of Thumb:** สัญญาณที่ Rise time < 1 ns มักจะต้องมีการทำ Impedance Control (เช่น USB, HDMI, PCIe)
- **Termination:** ถ้า $Z_0$ ไม่แมตช์กับ Source/Load ต้องใส่ Series/Parallel Resistor (終端抵抗 - Shuutan Teikou) ให้ใกล้ชิปที่สุด
- **Trace Width/Clearance:** อย่าปรับขนาดเส้นระหว่างทางเด็ดขาด (Neck-down) ถ้าไม่จำเป็น เพราะจะทำให้ $Z_0$ กระโดด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **特性インピーダンス (Tokusei Inpiidansu):** Characteristic Impedance (อิมพีแดนซ์ลักษณะเฉพาะ)
- **伝送線路 (Densou Senro):** Transmission Line (สายส่งสัญญาณ)
- **信号反射 (Shingou Hansha):** Signal Reflection (การสะท้อนของสัญญาณ)
- **終端抵抗 (Shuutan Teikou):** Termination Resistor (ตัวต้านทานเทอร์มิเนต)
- **波形割れ (Hakei Ware):** Non-monotonic/Broken waveform (รูปคลื่นแตก)

## ควิซท้ายบท (End of Chapter Quiz)
**Q:** สาเหตุหลักที่ต้องทำ Impedance Control ในบอร์ด High-speed คืออะไร?
1. เพื่อลดความร้อนของ PCB
2. เพื่อป้องกัน Signal Reflection ที่ทำให้ Data Corrupt
3. เพื่อลดราคาค่าผลิต PCB

*เฉลย: 2*
