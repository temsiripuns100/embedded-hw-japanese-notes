# Lesson 062: PCB Decoupling Part 2 - Capacitor Characteristics & ESL/ESR (コンデンサの特性とESL/ESR)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

Capacitor ในโลกความเป็นจริงไม่ใช่ Ideal Component แต่มันมีค่าแฝง (Parasitics) อยู่ด้วย ซึ่งสามารถจำลองได้ด้วย RLC Series Equivalent Circuit Model ประกอบด้วย:
- **C (Capacitance)**: ความจุไฟฟ้าหลัก
- **ESR (Equivalent Series Resistance)**: ความต้านทานแฝง
- **ESL (Equivalent Series Inductance)**: ความเหนี่ยวนำแฝง

สมการ Impedance ของ Capacitor คือ:
$$ Z(f) = \sqrt{ ESR^2 + \left( 2\pi f \cdot ESL - \frac{1}{2\pi f \cdot C} \right)^2 } $$

จุดที่ Capacitor ทำงานได้ดีที่สุดคือที่ **Self-Resonant Frequency (SRF)** ซึ่งค่า Reactance ของ C และ ESL หักล้างกันพอดี ทำให้ Impedance มีค่าเท่ากับ ESR อย่างเดียว:
$$ f_{SRF} = \frac{1}{2\pi\sqrt{ESL \cdot C}} $$

ต่ำกว่า SRF, Capacitor จะมีพฤติกรรมเป็น Capacitive (Impedance ลดลงตามความถี่)
สูงกว่า SRF, Capacitor จะมีพฤติกรรมเป็น Inductive (Impedance เพิ่มขึ้นตามความถี่)

## 2. ทริคหน้างาน OJT แบบ Step-by-step (現場の実践テクニック)
การลดค่า ESL คือหัวใจของการ Decoupling ความถี่สูง (High-Frequency Decoupling)

**Step-by-step OJT:**
1. **เลือก Package Size ให้เล็กที่สุด**: ยิ่ง Package เล็ก (เช่น 0402 หรือ 0201) ค่า ESL ยิ่งต่ำ
2. **การจัดวาง (Orientation)**: การใช้ Capacitor แบบ Reverse Geometry (เช่น 0306 แทนที่จะเป็น 0603) จะช่วยให้กระแสไหลผ่านระยะทางที่สั้นกว่า ทำให้ ESL ต่ำลงอย่างมาก
3. **Optimize Via Placement**:
   - ห้ามใช้ Trace ยาวๆ ลากออกจาก Pad ไปหา Via (Trace Inductance $\approx 1 nH/mm$)
   - ให้วาง Via ขนาบข้าง Pad (Side-placement) หรือใกล้ที่สุดแบบ Dog-bone
   - ต่อ 2-3 Vias ต่อ 1 Pad เพื่อขนานค่า Via Inductance ($L_{total} = L/n$)

## 3. คำศัพท์ญี่ปุ่นเชิงเทคนิคสำหรับการตรวจแบบ (検図用語)

- **等価直列抵抗 (Touka chokuretsu teikou)**: Equivalent Series Resistance (ESR)
- **等価直列インダクタンス (Touka chokuretsu indakutansu)**: Equivalent Series Inductance (ESL)
- **自己共振周波数 (Jiko kyoushin shuuhasuu)**: Self-Resonant Frequency (SRF)
- **実装インダクタンス (Jissou indakutansu)**: Mounting Inductance
- **逆ジオメトリ (Gyaku jiometori)**: Reverse Geometry (e.g., 0306 package)

## 4. ควิซวิเคราะห์ปัญหาระดับยาก (高度な問題分析クイズ)

**คำถาม (問題):**
มี Capacitor สองตัว: 
ตัวที่ 1: $10\mu F$ (Package 1206), SRF = 1 MHz, ESR = $10 m\Omega$
ตัวที่ 2: $0.1\mu F$ (Package 0402), SRF = 20 MHz, ESR = $50 m\Omega$
เมื่อนำทั้งสองตัวมาต่อขนานกันเพื่อทำ Decoupling ทำไมเราอาจจะเจอปัญหา Impedance พุ่งสูงอย่างรุนแรงที่ความถี่ประมาณ 5 MHz?

**เฉลยและคำอธิบาย (解答と解説):**
ปรากฏการณ์นี้เรียกว่า **Anti-Resonance (Parallel Resonance)** 
ที่ความถี่ 5 MHz (ซึ่งอยู่ระหว่าง 1 MHz และ 20 MHz):
- ตัวที่ 1 ($10\mu F$) อยู่เหนือ SRF ของมัน จึงมีพฤติกรรมเป็น **Inductor (L)**
- ตัวที่ 2 ($0.1\mu F$) อยู่ต่ำกว่า SRF ของมัน จึงมีพฤติกรรมเป็น **Capacitor (C)**
เมื่อ L และ C มาต่อขนานกัน จะเกิดการเรโซแนนซ์แบบขนาน (Parallel LC Tank Circuit) ซึ่งที่จุดเรโซแนนซ์นี้ Impedance รวมของระบบจะ **พุ่งขึ้นสูงสุด (Impedance Peak)** ทำให้เกิด Noise รุนแรงได้
**วิธีแก้:** เลือก Capacitor ที่มีค่า ESR เหมาะสมเพื่อ Damping ยอด Peak นี้ หรือซ้อนค่า Capacitance ให้ถี่ขึ้นเพื่อลดช่องว่างของความถี่ SRF
