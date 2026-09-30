# FPGA PLL Deep Dive - Part 2: Jitter, Phase Noise, and Stability Analysis

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
Jitter และ Phase Noise คือสองด้านของเหรียญเดียวกัน Jitter คือความคลาดเคลื่อนทางเวลา (Time Domain) ส่วน Phase Noise คือความคลาดเคลื่อนทางความถี่ (Frequency Domain)
- **Deterministic Jitter (DJ)**: เกิดจากสัญญาณรบกวนที่มีขอบเขตชัดเจน เช่น Power Supply Noise, Crosstalk
- **Random Jitter (RJ)**: เกิดจาก Thermal Noise ใน Semiconductor เป็นกระบวนการทางสถิติแบบ Gaussian (Unbounded)
- **Total Jitter (TJ)** = DJ + $N \times RJ$ (ที่ BER $10^{-12}$, $N \approx 14$)

ในการวิเคราะห์ Stability ของ PLL จะใช้ **Bode Plot** เพื่อหา Phase Margin และ Gain Margin:
- **Phase Margin (PM)**: โดยทั่วไปควรอยู่ระหว่าง $45^\circ$ ถึง $60^\circ$ หาก PM ต่ำไป ระบบจะเกิด Ringing และ Jitter Peaking ถ้าน้อยกว่า 0 ระบบจะแกว่ง (Unstable)

## 2. ทริคหน้างาน OJT (現場のOJTテクニック)
- **Jitter Peaking**: เมื่อต่อ PLL แบบ Cascading (ต่ออนุกรมกัน) ต้องระวัง Jitter Peaking หาก Loop Bandwidth ของตัวที่สองกว้างกว่าหรือเท่ากับตัวแรก Jitter ที่ความถี่ใกล้เคียง Bandwidth จะถูกขยาย (Amplified) กฎเหล็กคือ Cascaded PLL ต้องมี Bandwidth ห่างกันอย่างน้อย 1 decade
- **Power Supply Rejection Ratio (PSRR)**: Jitter ส่วนใหญ่ของ PLL ใน FPGA มาจากไฟเลี้ยง ดังนั้น LDO ที่จ่ายไฟให้ VCC_PLL ต้องมี Noise ต่ำมาก (< 10mVpp) การวาง Bypass Capacitor (0.1uF, 0.01uF) ต้องชิดขา FPGA ที่สุด (最短距離で配置)

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語)
- **位相雑音 (いそうざつおん, Isou Zatsuon)**: Phase Noise
- **電源変動 (でんげんへんどう, Dengen Hendou)**: Power Supply Fluctuation / Noise
- **直列接続 (ちょくれつせつぞく, Chokuretsu Setsuzoku)**: Cascading (การต่ออนุกรม)
- **余裕度 (よゆうど, Yoyuudo)**: Margin (เช่น Phase Margin = 位相余裕)
- **ジッタ耐性 (じったたいせい, Jitta Taisei)**: Jitter Tolerance

## 4. ควิซท้ายบท (理解度チェック)
**Q2:** การต่อ PLL 2 ตัวแบบ Cascading หากต้องการป้องกันปัญหา Jitter Peaking รุนแรง ควรตั้งค่า Bandwidth อย่างไร?
A) ตั้ง Bandwidth ให้เท่ากันทั้งสองตัว
B) PLL ตัวแรกตั้งให้แคบ, ตัวที่สองตั้งให้กว้างกว่ามาก
C) PLL ตัวแรกตั้งให้กว้าง, ตัวที่สองตั้งให้แคบกว่ามาก
D) ไม่สามารถต่อ Cascading ใน FPGA ได้

*เฉลย:* C) Loop Bandwidth ของ PLL ตัวหลังควรแคบกว่าตัวแรกอย่างน้อย 1 decade เพื่อกรอง Jitter Peaking ที่เกิดจากตัวแรก
