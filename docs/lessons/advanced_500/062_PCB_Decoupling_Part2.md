# Lesson 062: PCB Decoupling Part 2 - Capacitor Types, ESR, ESL and Target Impedance

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Capacitor ในโลกความเป็นจริงไม่ใช่ Ideal Component มันมี Equivalent Series Resistance (ESR) และ Equivalent Series Inductance (ESL) ต่ออนุกรมอยู่
โมเดลที่แท้จริง: $Z = \sqrt{ESR^2 + (X_L - X_C)^2}$ โดยที่ $X_L = 2\pi f L$ และ $X_C = \frac{1}{2\pi f C}$
จุดที่ $X_L = X_C$ คือจุด Self-Resonant Frequency (SRF) ซึ่งที่จุดนี้ Impedance จะต่ำที่สุดและเท่ากับ ESR
ในฐานะ Senior เราต้องเลือก C ที่มีค่า SRF ครอบคลุมช่วงความถี่สัญญาณรบกวน (Harmonics) ของ IC การใช้ C หลายค่า (เช่น 0.1uF, 0.01uF, 1nF) ขนานกัน จะช่วยกด Impedance ในช่วงความถี่ที่กว้างขึ้น แต่ต้องระวังปัญหา Anti-resonance ระหว่าง C ต่างชนิดกัน ซึ่งอาจทำให้ Impedance พุ่งสูงปรี๊ดที่ความถี่ใดความถี่หนึ่ง

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Anti-Resonance Trap:** อย่าใส่ C หลายค่ามั่วซั่ว ถ้าไม่แน่ใจ การใช้ C ค่าเดียวกัน (เช่น 0.1uF) หลายๆ ตัวขนานกัน จะปลอดภัยกว่าการใช้ค่าผสม (0.1uF + 0.01uF) เพราะจะลด ESL โดยรวมโดยไม่เกิด Anti-resonance peak ใหญ่ๆ
- **Size Matters:** สำหรับ High-Frequency C ขนาดเล็ก (เช่น 0402, 0201) จะมี ESL ต่ำกว่าขนาดใหญ่ (เช่น 0805, 1206) ดังนั้นให้ใช้ตัวเล็กสำหรับความถี่สูง
- **Reverse Geometry:** ลองพิจารณา C แบบ Reverse Geometry (เช่น 0306 แทน 0603) เพราะระยะห่างระหว่างขั้วสั้นกว่า ทำให้ ESL ต่ำกว่ามาก

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **等価直列抵抗 (Touka Chokuretsu Teikou):** ESR (Equivalent Series Resistance)
- **等価直列インダクタンス (Touka Chokuretsu Indakutansu):** ESL (Equivalent Series Inductance)
- **自己共振周波数 (Jiko Kyoushin Shuuhaasuu):** SRF (Self-Resonant Frequency)
- **反共振 (Han Kyoushin):** Anti-resonance
- **パッケージサイズ (Pakkeeji Saizu):** Package Size

## ควิซท้ายบท (Quiz)
1. ทำไม Capacitor ตัวเล็ก (เช่น 0402) ถึงตอบสนองต่อความถี่สูงได้ดีกว่าตัวใหญ่ (เช่น 0805)?
2. ปรากฏการณ์ Anti-resonance เกิดขึ้นได้อย่างไร และส่งผลเสียอย่างไรต่อ PDN?
