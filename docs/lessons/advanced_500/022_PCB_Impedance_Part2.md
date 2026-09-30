# Lesson 22: Microstrip vs Stripline & Material Selection (基板材質と配線構造)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
โครงสร้างสายส่งสัญญาณบน PCB มีสองแบบหลัก:
1. **Microstrip (マイクロストリップ):** เส้นทองแดงอยู่ผิวนอก (Top/Bottom Layer) และมี Reference Plane ด้านล่างด้านเดียว ความเร็วในการเคลื่อนที่ของสัญญาณเร็วกว่าเพราะด้านบนเป็นอากาศ ($D_k \approx 1$)
2. **Stripline (ストリップライン):** เส้นทองแดงอยู่ชั้นใน (Inner Layer) ขนาบด้วย Reference Plane ทั้งด้านบนและล่าง (GND/PWR) ช่วยป้องกัน EMI ได้ดีเยี่ยม แต่ทำให้เกิด Delay มากกว่า
**Dielectric Constant (Dk หรือ $\epsilon_r$ - 誘電率):** วัสดุ FR-4 ทั่วไปมี Dk ประมาณ 4.2-4.6 ซึ่งไม่เสถียรที่ความถี่สูง หากความถี่ระดับ GHz ขึ้นไป ควรใช้วัสดุ High-speed เช่น Megtron, Rogers ซึ่งมี Dk ต่ำและเสถียร (Dk $\approx$ 3.0-3.5) รวมถึงมี Loss Tangent (Df - 誘電正接) ที่ต่ำเพื่อลด Signal Attenuation (信号減衰).

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Microstrip:** ใช้สำหรับสัญญาณที่ไม่ Critical มาก หรือความถี่ไม่สูงเว่อร์ เพราะจะถูกกวนจากภายนอกได้ง่าย
- **Stripline:** บังคับใช้กับสัญญาณ Clock, High-speed Data เพื่อลด Crosstalk และการแผ่รังสี EMI
- **Material Request:** เวลาสั่งผลิตบอร์ด (Fab) ถ้ามี Impedance Control ต้องบอกโรงงานว่า "Allow stack-up adjustment to meet impedance" โรงงานจะปรับ Trace width หรือ Dielectric thickness เล็กน้อยเพื่อให้ได้ค่าที่เป๊ะ

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **誘電率 (Yuudenritsu):** Dielectric Constant (Dk)
- **誘電正接 (Yuuden Seisetsu):** Dissipation Factor / Loss Tangent (Df)
- **表層 (Hyousou):** Outer Layer / Surface layer (ชั้นนอก)
- **内層 (Naisou):** Inner Layer (ชั้นใน)
- **層構成 (Sou Kousei):** Stack-up (โครงสร้างชั้น PCB)

## ควิซท้ายบท (End of Chapter Quiz)
**Q:** ถ้าต้องการลดการแผ่สัญญาณรบกวน (EMI) ของเส้น Clock ควรเลือกเดินสายแบบใด?
1. Microstrip
2. Stripline
3. Coplanar Waveguide ไม่มี Plane

*เฉลย: 2*
