# Lesson 040: System-Level Crosstalk: Connectors and Cables (システムレベルのクロストーク)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ System-level สัญญาณต้องวิ่งผ่าน Connectors, Backplanes และ Cables จุดเชื่อมต่อเหล่านี้มีการเปลี่ยนแปลงของ Impedance อย่างรุนแรงและมักเป็นจุดกำเนิด Crosstalk ที่ใหญ่ที่สุด (Connector Crosstalk) การจัดวาง Pinout ภายใน Connector มีผลอย่างมาก รูปแบบ **G-S-S-G** (Ground-Signal-Signal-Ground) จะให้ Isolation ที่ดีกว่ารูปแบบที่มีแต่ Signal เรียงติดกัน นอกจากนี้ การชีลด์ (Shielding Effectiveness) ของสาย Cable และ Grounding ของขอบ Board (Chassis Ground) ก็เป็นตัวแปรสำคัญที่ช่วยคุม EMI และ Alien Crosstalk

## 2. ทริคหน้างาน OJT (OJT Field Tricks)
- **แยก TX และ RX:** ในการกำหนด Pinout ของ Custom Connector ให้แยกกลุ่มสัญญาณ TX และ RX ออกจากกันอย่างเด็ดขาด (เช่น ให้อยู่คนละฝั่งของ Connector) และคั่นกลางด้วย Ground Pins เพื่อลดความเสี่ยงของ NEXT
- **Connector Breakout:** บริเวณจุด Breakout ออกจาก Connector มักเป็นคอขวดที่บีบให้ Trace ต้องเดินชิดกัน ให้ใช้เส้น Trace ที่เล็กที่สุดเท่าที่โรงงานทำได้ (Minimum Trace/Space) ชั่วคราวแค่บริเวณนั้น เพื่อให้หลุดออกจากเขต Connector ให้เร็วที่สุดแล้วค่อยคลี่ออก
- **Pigtail Effect:** ระวังจุดต่อ Shield ของสายเคเบิลลง Ground ของ PCB อย่าปล่อยให้สาย Shield ยาวเป็น Pigtail เพราะมันจะทำตัวเป็นเสาอากาศรับ/ส่ง Noise

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **コネクタピン配置 (Konekuta pin haichi):** Connector pinout (การจัดพินของคอนเนกเตอร์)
- **シールド効果 (Shiirudo kouka):** Shielding effectiveness (ประสิทธิภาพของชีลด์กันคลื่น)
- **筐体 (Kyoutai):** Enclosure / Chassis (เคสหรือโครงโลหะภายนอก)
- **引き出し配線 (Hikidashi haisen):** Breakout routing / Fanout (การเดินสายกระจายออกจากคอนเนกเตอร์หรือชิป)

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** การกำหนด Pinout สำหรับ High-Speed Connector เพื่อป้องกัน Near-End Crosstalk (NEXT) อย่างเด็ดขาด ควรทำอย่างไร?
**คำตอบ:** ควรแยกกลุ่มพิน TX ออกจาก RX อย่างชัดเจน (เช่น ให้อยู่คนละแถว) และมีพิน Ground คั่นกลางเสมอ (G-S-S-G)
