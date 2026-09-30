# 1.2 スイッチング電源（DCDC）の効率とリップル (ประสิทธิภาพและ Ripple Noise ของ DCDC)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**DCDC Converter (Switching Regulator)** เป็นวงจรแปลงแรงดันที่มีประสิทธิภาพสูงกว่า LDO มาก โดยใช้การเปิดปิดสวิตช์ (MOSFET) ควบคู่กับตัวเก็บพลังงานอย่าง Inductor และ Capacitor เพื่อสร้างแรงดัน Output
- **ประสิทธิภาพ (Efficiency):** ถึงแม้จะมีประสิทธิภาพสูง (มักจะ 85-95%) แต่ประสิทธิภาพจะตกลงในช่วงโหลดต่ำๆ (Light Load) เพราะพลังงานที่สูญเสียไปกับการสลับสวิตช์ (Switching Loss) มีสัดส่วนมากกว่ากำลังงานที่จ่ายออก
- **Ripple Noise:** เนื่องจากการทำงานแบบสวิตชิ่ง ทำให้เกิดแรงดันกระเพื่อม (Voltage Ripple) ที่ Output ซึ่งเป็นผลมาจากกระแสกระเพื่อมใน Inductor ไหลผ่านความต้านทานแฝง (ESR) ของ Capacitor ขาออก

## 💡 ทริคหน้างาน (OJT Tricks)
- **การเลือกโหมด PFM/PWM:** ในแอปพลิเคชันที่ต้องประหยัดแบตเตอรี่ในโหมด Standby ควรเลือก DCDC ที่มีฟังก์ชันเปลี่ยนโหมดอัตโนมัติ (PFM/PWM Auto-switch) เพื่อรักษาระดับประสิทธิภาพในช่วงโหลดต่ำ
- **การวัด Ripple Noise ให้ถูกต้อง:** บ่อยครั้งที่ Engineer ตกใจว่าทำไม Ripple สูงกว่าสเปค! การวัด Ripple ด้วย Oscilloscope ต้องถอดสายกราวด์ยาวๆ แบบคลิปหนีบออก แล้วใช้การวัดแบบสายกราวด์สั้น (Pigtail / Spring clip) ขนานไปกับ Capacitor ตัวสุดท้าย เพื่อป้องกันการเหนี่ยวนำสัญญาณรบกวนจากอากาศ
- **ESR สำคัญมาก:** การเปลี่ยนประเภท Capacitor จาก Tantalum มาเป็น Ceramic (MLCC) จะทำให้ ESR ลดลงอย่างมหาศาล ช่วยลด Ripple ได้ดี แต่ระวัง Phase Margin ของวงจรอาจจะพังจนเกิด Oscillation ได้ ต้องเช็ค Data sheet ให้ดี!

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **スイッチング電源 (Suitchingu Dengen):** Switching Power Supply (DCDC)
- **変換効率 (Henkan Kōritsu):** Conversion Efficiency (ประสิทธิภาพการแปลงไฟ)
- **リップル電圧 (Rippuru Den'atsu):** Ripple Voltage (แรงดันกระเพื่อม)
- **軽負荷時 (Keifukaji):** Light Load Condition (สภาวะโหลดต่ำ)
- **スイッチング周波数 (Suitchingu Shūhasū):** Switching Frequency

**ประโยคที่ใช้บ่อย:**
> 「軽負荷時の効率を改善するために、PFMモードに対応したDCDCコンバータを選定しました。」
> *(Keifukaji no kōritsu o kaizen suru tame ni, PFM mōdo ni taiō shita DCDC konbāta o sentei shimashita.)*
> "เพื่อปรับปรุงประสิทธิภาพในช่วงโหลดต่ำ จึงได้เลือกใช้ DCDC Converter ที่รองรับโหมด PFM ครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** ในการแก้ปัญหา Output Ripple Voltage ที่สูงเกินไปในวงจร Buck Converter การเปลี่ยนตัวเก็บประจุขาออก (Output Capacitor) ที่มีค่า ESR (Equivalent Series Resistance) ลดลง จะส่งผลอย่างไรต่อ Ripple Voltage?
