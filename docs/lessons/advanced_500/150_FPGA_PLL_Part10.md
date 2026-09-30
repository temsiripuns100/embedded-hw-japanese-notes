# Lesson 150: FPGA PLL Advanced - Part 10 (Debugging & Verification)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
การ Debug PLL บนบอร์ดจริง (Board-level Verification) ต้องพึ่งพาเครื่องมือวัดที่มีประสิทธิภาพ Oscilloscope ต้องมี Bandwidth เพียงพอ (อย่างน้อย 3-5 เท่าของความถี่ที่วัด) การใช้ Internal Logic Analyzer (เช่น Xilinx ILA, Intel SignalTap) ช่วยดึงสัญญาณ `LOCKED` หรือสัญญาณเตือนความผิดปกติออกมาดูได้ แต่ไม่สามารถดูรูปคลื่น Analog ของ Clock ได้

## 2. ทริคหน้างาน OJT (On-the-Job Tricks)
- **Probing Technique**: การวัดสัญญาณ Clock ห้ามใช้สายกราวด์ยาวๆ (Alligator Clip) ที่แถมมากับ Probe เพราะจะเกิด Ringing มหาศาล ต้องใช้ **Ground Spring** จิ้มลงจุด GND ที่ใกล้ที่สุดเสมอ หรือใช้ Active Probe
- **Voltage/Temp Corner Testing**: ต้องทดสอบว่า PLL สามารถ Lock ได้ที่สภาวะสุดขั้ว เช่น VCC ต่ำสุด/สูงสุดตาม Spec และอุณหภูมิห้องแล็บที่เย็นจัดและร้อนจัด (Thermal Chamber)

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **デバッグ (Debaggu)**: Debug
- **実機検証 (Jikki Kenshou)**: Board-level Verification (การยืนยันบนเครื่องจริง)
- **オシロスコープ (Oshirosukoopu)**: Oscilloscope
- **プロービング (Puroobingu)**: Probing (การจิ้มวัดสัญญาณ)
- *"クロックの波形を測定する際は、プロービングのグラウンド線に注意して実機検証してください。"* (ตอนวัดรูปคลื่น Clock ในช่วง実機検証 ให้ระวังเรื่องสายกราวด์ของการ Probing ด้วย)

## 4. ควิซท้ายบท (Quiz)
**Q:** ทำไมการใช้สายกราวด์แบบหนีบยาวๆ (Alligator Clip) วัดสัญญาณ Clock ถึงทำให้ผลการวัดผิดพลาด?
**A:** เพราะสายยาวทำหน้าที่เป็น Inductor (L) สร้างวงจร LC Resonant กับ Capacitance ของ Probe ทำให้เกิด Ringing สูงในรูปคลื่น
