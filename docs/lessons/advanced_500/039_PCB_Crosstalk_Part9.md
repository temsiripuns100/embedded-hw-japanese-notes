# Lesson 039: Crosstalk in High-Density Memory (DDR5/GDDR6) (高密度メモリインターフェースのクロストーク)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
สถาปัตยกรรมหน่วยความจำความเร็วสูงอย่าง DDR5 (ระดับ 6400+ MT/s) และ GDDR6 มีความหนาแน่นของลายวงจรสูงมาก (High-Density Routing) ปัญหาใหญ่คือ **FEXT ใน Microstrip Lines** และ Crosstalk ภายใน Byte-lane เดียวกัน (ระหว่าง Data DQ และ Strobe DQS) การทำ Length Matching ที่เข้มงวดทำให้ต้องตีงู (Serpentine Routing) จำนวนมาก ซึ่งโครงสร้าง Serpentine หากออกแบบไม่ดีจะทำให้เกิด Intra-pair Skew และ Broadside Coupling จนกลายร่างเป็นตัวกระจาย Common-mode noise

## 2. ทริคหน้างาน OJT (OJT Field Tricks)
- **การตีงู (Meander):** อย่าทำ Serpentine ห่างกันน้อยกว่า 3 เท่าของความกว้างเส้น (3W rule สำหรับ Meander spacing) เพื่อป้องกัน Self-coupling
- **Match length ที่ต้นทาง:** พยายามปรับ Length Matching ให้เสร็จตั้งแต่ฝั่งใกล้ชิปต้นทาง (Source) อย่าไปกองรวมกันปรับใกล้ชิปปลายทาง เพราะจะทำให้ Skew สะสมและเกิด Crosstalk ตลอดความยาวสาย
- **Stripline เหนือ Microstrip:** สำหรับ DDR5 แนะนำให้เดินสาย DQ/DQS ไว้ที่ Layer ด้านใน (Stripline) เพราะมีปัญหา FEXT น้อยกว่า Microstrip ชั้นนอกมาก

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **等長配線 (Touchou haisen):** Length matching (การปรับความยาวสายให้เท่ากัน)
- **ミアンダ配線 (Mianda haisen):** Meander/Serpentine routing (การเดินสายแบบตีงู)
- **バイトレーン (Baito reen):** Byte lane (กลุ่มสายสัญญาณ 8-bit Data + Strobe)
- **同相ノイズ (Dousou noizu):** Common-mode noise (สัญญาณรบกวนเฟสตรงกัน)

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** การเดินสายแบบตีงู (Serpentine) แคบๆ และชิดกันมากเกินไป ส่งผลเสียอย่างไรต่อ Signal Integrity?
**คำตอบ:** ทำให้เกิด Self-coupling ภายในเส้นเดียวกัน ทำให้สัญญาณกระโดดข้ามลูป (Signal velocity เปลี่ยนแปลง) เกิด Skew และทำให้เกิด Crosstalk ไปกวนเส้นข้างเคียงได้ง่ายขึ้น
