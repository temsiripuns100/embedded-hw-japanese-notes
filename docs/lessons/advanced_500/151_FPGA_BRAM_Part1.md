# Lesson 151: FPGA BRAM Architecture and True Dual-Port Operations

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
BRAM (Block RAM) ใน FPGA เป็นหน่วยความจำแบบ SRAM ที่มีโครงสร้างแข็ง (Hard Macro) ฝังอยู่ในซิลิคอน การเข้าใจสถาปัตยกรรมภายในเช่น True Dual-Port (TDP) เป็นสิ่งสำคัญ TDP อนุญาตให้อ่านและเขียนได้อย่างอิสระจากสองพอร์ตพร้อมกันที่ความถี่สัญญาณนาฬิกาต่างกันได้ การจัดการ Address collision ในระดับฮาร์ดแวร์เมื่อทั้งสองพอร์ตเข้าถึงตำแหน่งเดียวกันในเวลาเดียวกันต้องพิจารณา Timing diagram และ Behavior อย่างรอบคอบ

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Clock Domain แยกกัน:** เมื่อใช้ BRAM ในแบบ TDP ข้าม Clock domain ตรวจสอบเสมอว่า Setup/Hold time ของ Address/Data lines ได้รับการ constrain อย่างถูกต้อง
- **Avoid Asynchronous Reset:** สถาปัตยกรรม BRAM ส่วนใหญ่ไม่รองรับ Asynchronous reset หากฝืนใช้ Synthesizer อาจใช้ LUT RAM (Distributed RAM) แทน ทำให้กิน Resource มหาศาล

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- ブロックRAM (Burokku RAM) - Block RAM
- デュアルポート (Dyuaru pooto) - Dual port
- 競合 (Kyougou) - Conflict/Collision
- アドレス空間 (Adoresu kuukan) - Address space

## ควิซท้ายบท (Quiz)
**คำถาม:** การพยายามทำ Asynchronous reset ให้กับ output ของ BRAM จะส่งผลเสียอย่างไร?
**คำตอบ:** (เฉลย: เครื่องมือสังเคราะห์ (Synthesizer) อาจไม่ใช้ BRAM แต่จะไปใช้ Distributed RAM แทน ทำให้สูญเสียทรัพยากร Logic บน FPGA)
