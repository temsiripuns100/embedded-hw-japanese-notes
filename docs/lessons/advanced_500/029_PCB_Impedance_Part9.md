# Lesson 029: PCB Impedance Part 9 - Vias and Impedance Discontinuities (Stub Effect)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Via ใน PCB ทำหน้าที่เหมือน Parasitic Capacitor (จาก Barrel ไปยัง Plane) และ Parasitic Inductor (ความยาวของ Barrel) แต่ปัญหาที่ใหญ่ที่สุดในระดับ High-speed คือ **Via Stub** (ส่วนที่ยื่นเลยเกินจากชั้นสัญญาณที่ใช้งานไปถึงจุดสิ้นสุดของ Via) Stub นี้ทำหน้าที่เหมือน Open-ended Transmission Line ซึ่งจะเกิด Resonance (Quarter-wave resonance) ทำให้สัญญาณที่ความถี่ใดความถี่หนึ่ง (และ Harmonices) ถูกดูดกลืนไปจนหมด (Null) ส่งผลให้ Signal Integrity พังพินาศ

## 2. ทริคหน้างาน OJT (On-the-Job Training Tips)
- **Senior Tip:** ถ้าเจาะทะลุบอร์ด (Through-hole via) แล้วใช้งานแค่ Layer 1 ถึง Layer 3 ส่วนที่เหลือจนถึง Bottom layer คือ Stub! ทางแก้คือใช้เทคนิค **Backdrill** เจาะเนื้อทองแดงส่วนเกินทิ้ง หรือใช้ Blind/Buried vias แต่จะเพิ่มต้นทุนอย่างมาก
- การออกแบบ Via pad และ Anti-pad: การเพิ่มขนาด Anti-pad ในชั้น Plane ช่วยลด Parasitic capacitance ซึ่งสามารถใช้ปรับ Impedance ของ Via ให้เข้ากับ $50\Omega$ หรือ $100\Omega$ ได้ (Via optimization)

## 3. คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **ビアスタブ (Biasutabu):** Via Stub (ส่วนปลายของ Via ที่ไม่ได้ใช้งาน)
- **バックドリル (Bakkudoriru):** Backdrill (การเจาะ Via จากด้านหลังเพื่อตัด Stub)
- **クリアランス (Kuriaransu):** Clearance / Anti-pad (ระยะห่างระหว่าง Via กับ Plane)
- **不連続点 (Furenzokuten):** Discontinuity point (จุดที่ Impedance ไม่ต่อเนื่อง)
- **共振 (Kyōshin):** Resonance (การสั่นพ้อง)

## 4. ควิซท้ายบท (End-of-chapter Quiz)
**Q:** สูตรการคำนวณความถี่ Resonance ของ Via Stub คืออะไร และถ้า Stub ยาว 100 mil (ประมาณ 2.54 mm) จะเกิดปัญหาที่ความถี่ประมาณเท่าไหร่ใน FR4?
**A:** $f_{res} = \frac{c}{4 \times \text{Length} \times \sqrt{\epsilon_r}}$. สำหรับ FR4 ($\epsilon_r \approx 4.0$), ความเร็วคลื่นประมาณ 6 inch/ns. ดังนั้น Resonance ของ 100 mil stub จะอยู่ที่ $f = \frac{6 \text{ inch/ns}}{4 \times 0.1 \text{ inch}} = 15 \text{ GHz}$
