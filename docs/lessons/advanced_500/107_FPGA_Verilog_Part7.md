# Lesson 107: High-Speed Serial Interfaces (SerDes) (高速シリアルインターフェース)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เมื่อความเร็วการส่งข้อมูลระดับ Gigabit/s การส่งแบบขนาน (Parallel) จะเจอปัญหา Clock Skew จึงต้องเปลี่ยนมาใช้ SerDes (Serializer/Deserializer)
- **8b/10b Encoding:** การเข้ารหัสข้อมูลเพื่อให้มี DC Balance (มีจำนวน 0 และ 1 ใกล้เคียงกัน) และให้มี Transition มากพอที่ Receiver จะทำ Clock Data Recovery (CDR) ได้
- **Jitter & Eye Diagram:** การวิเคราะห์สัญญาณความเร็วสูง ต้องดู Eye Diagram เพื่อประเมิน Deterministic Jitter (DJ) และ Random Jitter (RJ)
- **Pre-emphasis & Equalization:** เทคนิคชดเชยการสูญเสียสัญญาณในสายส่ง (Channel Loss) โดยการปรับรูปคลื่นที่ Tx และ Rx

## 2. ทริคหน้างาน OJT (OJT Field Tricks)
- **IBIS-AMI Models:** เวลาทำ Board-level simulation สำหรับ SerDes เราจะใช้โมเดล IBIS-AMI แทน SPICE ธรรมดา เพราะรันเร็วกว่าและวิเคราะห์ระดับล้านบิตได้
- **Loopback Testing:** ในการ Debug ฮาร์ดแวร์จริง เริ่มต้นเสมอด้วย Near-end PMA loopback เพื่อเช็คว่า Transceiver ภายใน FPGA ปกติไหม ก่อนจะไปเช็คสายส่งภายนอก

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **シリアライザ (Shiriaraiza):** Serializer
- **ジッタ (Jitta):** Jitter
- **波形 (Hakei):** Waveform (รูปคลื่น)
- **アイパターン (Ai patān):** Eye pattern / Eye diagram
- **差動信号 (Sadō shingō):** Differential signal

## 4. ควิซท้ายบท (Quiz)
**Q1:** ทำไม 8b/10b encoding ถึงช่วยในการทำ Clock Data Recovery (CDR)?
**Answer:** เพราะมันบังคับให้ข้อมูลมีการเปลี่ยนสถานะ (0->1 หรือ 1->0) บ่อยเพียงพอ ทำให้วงจร PLL/CDR ฝั่งรับสามารถดึง Clock ออกจากข้อมูลได้
