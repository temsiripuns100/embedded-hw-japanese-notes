# Lesson 9: Signal Integrity (SI) and Impedance Control (シグナルインテグリティとインピーダンス制御)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เมื่อความเร็วการเปิด-ปิด (Rise/Fall time) ของสัญญาณสั้นมากเมื่อเทียบกับความยาวของเส้นลวด เส้นลวดนั้นจะทำตัวเป็น Transmission Line ซึ่งต้องมี Impedance Control
- **Characteristic Impedance ($Z_0$):** ถูกกำหนดโดย ความกว้างของเส้น (W), ความหนาของทองแดง (T), ระยะห่างจาก Reference plane (H), และค่า Dielectric constant ($D_k$) ของวัสดุ PCB (เช่น FR4)
- **Reflection:** หาก Impedance ตลอดเส้นทางไม่ต่อเนื่อง (Impedance mismatch) จะเกิดการสะท้อนกลับของสัญญาณ ทำให้เกิด Overshoot, Undershoot, หรือ Ringing ส่งผลให้เกิด Data error
- **Termination:** การใส่ Resistor อนุกรมที่ต้นทาง (Source termination) หรือขนานที่ปลายทาง (End termination) เพื่อจับคู่ Impedance (Match) ลดการสะท้อนของคลื่น

## ทริคหน้างาน OJT (On-the-Job Tricks)
- เมื่อออกแบบบอร์ด ให้ขอ Stack-up (โครงสร้างชั้น PCB) จากโรงงาน (Fabricator) เสมอ และใช้ค่าความกว้างเส้นตามที่โรงงานคำนวณมาให้ (Impedance calculation report)
- ระวังตรงจุดที่เป็น Connector หรือ IC pad ซึ่งมักจะกว้างกว่าเส้น Trace ทำให้ Impedance ลดลง (Capacitive) บางครั้งต้องเจาะ Ground plane ใต้ Pad นั้นออก (Anti-pad) เพื่อดัน Impedance ขึ้น
- Via ก็ทำให้เกิด Impedance discontinuity ได้ ควรลดจำนวน Via ในสัญญาณที่อ่อนไหว

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **インピーダンス整合 (Inpiidansu seigou):** Impedance matching
- **波形割れ (Hakei ware):** Signal distortion / Ringing (รูปคลื่นแตกหรือมีรอยหยัก)
- **層構成 (Sou kousei):** Stack-up (โครงสร้างชั้นของ PCB)
- **ビア削り (Bia kezuri):** การทำ Anti-pad (เจาะเอาทองแดงรอบๆ Via ออก)

## ควิซท้ายบท (Quiz)
1. ถ้าลดระยะห่างระหว่าง Trace กับ Reference plane (H ลดลง) จะส่งผลต่อค่า $Z_0$ อย่างไร?
2. การใส่ Source Termination มีจุดประสงค์หลักเพื่ออะไร?
