# Lesson 038: SerDes and Equalization Techniques against Crosstalk (SerDesとイコライザ技術)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับชิป SerDes การรับมือกับ Signal Integrity จะใช้ Equalizer เช่น FFE (Feed-Forward Equalization) ที่ฝั่ง TX, และ CTLE (Continuous Time Linear Equalizer) กับ DFE (Decision Feedback Equalizer) ที่ฝั่ง RX แม้ว่า DFE จะเก่งมากในการลบ Inter-Symbol Interference (ISI) ที่เกิดจาก Insertion Loss และ Reflection แต่ **DFE ไม่สามารถแก้ Crosstalk ได้ดีนัก** เนื่องจาก Crosstalk (โดยเฉพาะ Alien Crosstalk จากช่องสัญญาณอื่น) มักเป็นสัญญาณที่ไม่มีความสัมพันธ์ (Uncorrelated / Asynchronous Noise) กับสัญญาณหลัก 

## 2. ทริคหน้างาน OJT (OJT Field Tricks)
- **อย่าฝากความหวังไว้ที่ DFE:** หากปัญหาหลักคือ Crosstalk ไม่ใช่ Loss การพึ่งพา RX Equalizer อย่างเดียวมักทำให้ BER (Bit Error Rate) ไม่ผ่าน ต้องกลับไปแก้ Layout PCB เช่น เพิ่ม Spacing หรืองาน Shielding
- **TX FFE Tuning:** ระวังการปรับ TX FFE (Tap weights) ให้แรงเกินไป (Over-equalization) เพราะพลังงานความถี่สูงที่อัดเข้าไปจะกลายเป็น Aggressor ที่รุนแรง สร้าง NEXT ให้กับคู่สายข้างเคียง

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **イコライザ (Ikoraiza):** Equalizer (วงจรปรับแต่งสัญญาณ)
- **符号間干渉 (Fugou-kan kanshou):** Inter-Symbol Interference / ISI (สัญญาณรบกวนข้ามบิต)
- **受信端 (Jushin-tan):** RX End / Receiver (ฝั่งรับสัญญาณ)
- **非同期ノイズ (Hidouki noizu):** Asynchronous noise (สัญญาณรบกวนที่ไม่ซิงค์กับ Clock หลัก)

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** ทำไม DFE (Decision Feedback Equalizer) ถึงใช้ลบ Crosstalk ที่มาจากคู่สายอื่นไม่ค่อยได้ผล?
**คำตอบ:** เพราะ DFE ใช้ประวัติของ Data ตัวมันเองในอดีตมาคาดเดาและลบสัญญาณรบกวน (ISI) แต่ Crosstalk เป็น Noise แบบสุ่มหรือมาจาก Data สายอื่นที่ DFE ไม่รู้ประวัติ
