# 2.5 波形なまりとリンギングの対策 (การแก้ปัญหารูปคลื่นมน และคลื่นสั่น Ringing)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**波形なまり (Waveform Dulling / Slew Rate Degradation):** คือการที่ขอบขาขึ้น (Rising Edge) หรือขาลง (Falling Edge) ของสัญญาณใช้เวลานานเกินไปในการเปลี่ยนสถานะ (Rise time / Fall time สูง) สาเหตุมักเกิดจากการที่ลายปริ้นท์มีความจุแฝง (Parasitic Capacitance) มาก หรือตัวต้านทาน Pull-up มีค่าสูงเกินไป (เกิด RC Delay)
**リンギング (Ringing):** คือการแกว่งสั่นของแรงดัน (Overshoot / Undershoot) ที่ขอบสัญญาณ เกิดจากการเหนี่ยวนำแฝง (Parasitic Inductance - $L$) และความจุแฝง ($C$) บนลายปริ้นท์ทำตัวเป็นวงจรเรโซแนนซ์ (LC Tank) เมื่อถูกกระตุ้นด้วยสัญญาณที่มี Slew Rate ที่ชันและเร็วมากๆ

## 💡 ทริคหน้างาน (OJT Tricks)
- **ช้าไปก็แย่ เร็วไปก็พัง:** Slew Rate ที่ช้าไป (なまり) ทำให้ Timing ผิดพลาด (Setup/Hold time violation) แต่ถ้าแก้ให้ขอบชันและเร็วปรี๊ด (Fast edge) จะทำให้เกิด Ringing อย่างรุนแรง และแผ่คลื่นแม่เหล็กไฟฟ้า (EMI) กระจุยกระจาย 
- **วิธีกำราบ Ringing นอกเหนือจาก Resistor:** นอกจากการใส่ Damping Resistor แล้ว หากชิปไมโครคอนโทรลเลอร์หรือ FPGA มีฟังก์ชัน "Slew Rate Control" หรือ "Drive Strength Control" ในรีจิสเตอร์ ให้สั่งลดความแรง (Slow Slew Rate / Low Drive Strength) ผ่าน Software จะแก้ปัญหา Ringing ได้โดยไม่ต้องแตะหัวแร้งบัคกรีเลย!
- **I2C ขอบขึ้นจะมนเป็นปกติ:** บัสแบบ Open-Drain อย่าง I2C ขาขึ้นจะมนๆ เป็นฟันฉลามเสมอ เพราะใช้ Pull-up resistor ดึงขึ้น ไม่ต้องตกใจ แค่คำนวณ RC ให้อยู่ในสเปค Timing ก็พอ

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **波形なまり (Hakei Namari):** Waveform dulling / Slow edge (รูปคลื่นมน/ขอบไม่ชัน)
- **リンギング (Ringingu):** Ringing (คลื่นสั่นที่ขอบสัญญาณ)
- **オーバーシュート (Ōbāshūto):** Overshoot (แรงดันพุ่งเกินขอบเขตบน)
- **立ち上がり時間 (Tachiagari Jikan):** Rise Time ($T_r$)
- **駆動能力 (Kudō Nōryoku):** Drive Strength

**ประโยคที่ใช้บ่อย:**
> 「クロック信号のリンギングが激しいため、放射ノイズ（EMI）の懸念があります。」
> *(Kurokku shingō no ringingu ga hageshii tame, hōsha noizu (Ī-Emu-Ai) no kenen ga arimasu.)*
> "เนื่องจากสัญญาณ Clock เกิด Ringing อย่างรุนแรง จึงมีความกังวลเรื่องการแผ่กระจายสัญญาณรบกวน (EMI) ครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** หากคุณพบว่าสัญญาณ SPI Clock มีอาการ Ringing (Overshoot) สูงถึง 4V บนบอร์ดระบบไฟ 3.3V แต่บน PCB ไม่ได้เผื่อที่วาง Damping Resistor ไว้เลย หากคุณเป็นวิศวกรซอฟต์แวร์ คุณจะลองแก้ปัญหานี้ผ่านการตั้งค่า Register ภายในชิปไมโครคอนโทรลเลอร์อย่างไร?
