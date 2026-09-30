# 1.7 バイパスコンデンサ（パスコン）の最適配置 (การวาง Decoupling Capacitor อย่างเหมาะสมที่สุด)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**Bypass Capacitor** หรือ Decoupling Capacitor มีหน้าที่เป็นแหล่งพลังงานสำรองขนาดเล็ก (Local Charge Reservoir) ที่จ่ายกระแสความถี่สูง (High-frequency transient current) ให้กับ IC ทันทีที่ต้องการ เพื่อลดความต้านทาน (Impedance) ของเส้นทางไฟเลี้ยง
**ESL (Equivalent Series Inductance):** ประสิทธิภาพของ Capacitor ที่ความถี่สูงจะถูกจำกัดด้วยค่า ESL ซึ่งเป็นผลมาจากแพ็กเกจของอุปกรณ์และการเดินลายปริ้นท์ (PCB Trace) ยิ่งความถี่สูงมาก Impedance จะถูกกำหนดโดย ESL มากกว่าความจุ ($C$) ของมัน
> $Z = \sqrt{ESR^2 + (X_L - X_C)^2}$

## 💡 ทริคหน้างาน (OJT Tricks)
- **ใกล้ที่สุดคือดีที่สุด:** ตัวเก็บประจุความจุต่ำ (เช่น 0.01uF หรือ 0.1uF) ที่มีแพ็กเกจเล็กที่สุด (0402 หรือ 0201) จะมีค่า ESL ต่ำสุด ต้องวาง **"ใกล้ขาไฟเลี้ยงของ IC มากที่สุดเท่าที่จะทำได้"** เพื่อให้ Loop Inductance สั้นที่สุด
- **ตำแหน่งการเจาะ Via:** การเดินลายปริ้นท์เข้า Capacitor แล้วค่อยเจาะ Via ลงไป Power Plane เป็นเรื่องต้องห้ามในการออกแบบ High-Speed! ทริคคือให้เจาะ Via ไว้ใกล้แพด (Pad) ของ Capacitor ให้มากที่สุด (หรือใช้เทคนิค Via-in-Pad ถ้าบอร์ดรองรับและมีงบ)
- **การจัดเรียงค่า C:** หากมี C หลายค่า ให้วางค่าที่น้อยที่สุด (ความถี่เรโซแนนซ์สูงสุด) ไว้ใกล้ชิปที่สุด แล้วค่อยวางค่าที่ใหญ่ขึ้นห่างออกไป

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **バイパスコンデンサ / パスコン (Baipasu Kondensa / Pasukon):** Bypass Capacitor / Decoupling Cap
- **最適配置 (Saiteki Haichi):** Optimal Placement (การจัดวางอย่างเหมาะสม)
- **寄生インダクタンス (Kisei Indakutansu):** Parasitic Inductance
- **実装面積 (Jissō Menseki):** Mounting Area (พื้นที่ลงอุปกรณ์)
- **直近 (Chokkin):** Closest / Very near

**ประโยคที่ใช้บ่อย:**
> 「ノイズ対策として、パスコンはICの電源ピンの直近に配置してください。」
> *(Noizu taisaku toshite, pasukon wa aishī no dengen pin no chokkin ni haichi shite kudasai.)*
> "เพื่อมาตรการป้องกันสัญญาณรบกวน กรุณาวางพาสคอน (Bypass Cap) ไว้ตรงจุดที่ใกล้ที่สุดของขาไฟเลี้ยง IC ด้วยครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** เพราะเหตุใดการเลือกใช้ Capacitor ขนาด 0.1uF แพ็กเกจ 0402 จึงมีความสามารถในการกรองสัญญาณรบกวนความถี่ระดับ 100MHz ได้ดีกว่า Capacitor ขนาด 0.1uF แพ็กเกจ 1206 ทั้งที่มีค่าความจุเท่ากัน?
