# Lesson 115: Verification, Assertions & Board-Level Bringup

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การออกแบบฮาร์ดแวร์จะสมบูรณ์ไม่ได้เลยหากขาดการ Verification ที่เข้มงวด สำหรับ VHDL ยุคใหม่ (VHDL-2008) มีความสามารถคล้ายคลึงกับ SystemVerilog มากขึ้น การใช้ Property Specification Language (PSL) หรือ VHDL Assertions ช่วยให้ดักจับบั๊กในระดับพฤติกรรมได้ตั้งแต่เนิ่นๆ
เมื่อชิปถูกผลิตและลงบอร์ด (Bringup) เราจะต้องรับมือกับ Signal Integrity, Power Sequencing และการอ่านค่าจาก JTAG/ILA (Integrated Logic Analyzer) เพื่อหาบั๊กที่ไม่เจอใน Simulation

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Self-Checking Testbench:** อย่าใช้แค่ตาดู Waveform เพราะจะพลาดง่ายมาก ให้เขียน Testbench ที่อ่าน Reference Data จากไฟล์และเปรียบเทียบผลลัพธ์อัตโนมัติ (Automated Check)
- **ILA Probing:** การใส่ ILA เยอะเกินไปทำให้ Routing ยากและ Timing พัง ให้ Probe เฉพาะสัญญาณในระดับ Control Path ก่อนเสมอ
- **Code Coverage:** ใช้เครื่องมือวัด Code Coverage (Statement, Branch, Toggle) หากยังไม่ถึง 90%+ ห้ามเซ็นผ่าน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **実機検証 (Jikki Kenshou):** Actual Machine Verification / Bringup (การทดสอบบนเครื่องจริง)
- **テストベンチ (Tesutobenchi):** Testbench (โค้ดทดสอบ)
- **アサーション (Asaashon):** Assertion (การตรวจสอบเงื่อนไขที่คาดหวัง)
- **波形 (Hakei):** Waveform (รูปคลื่นสัญญาณ)
- **不具合 (Fuguai):** Bug / Defect (ข้อบกพร่อง/ปัญหา)

## ควิซท้ายบท (Quiz)
1. ข้อดีของการใช้ Self-Checking Testbench เมื่อเทียบกับการดู 波形 ด้วยตาเปล่าคืออะไร?
2. ทำไมการทำ 実機検証 จึงยังจำเป็นแม้ Simulation จะผ่านทั้งหมดแล้วก็ตาม?
