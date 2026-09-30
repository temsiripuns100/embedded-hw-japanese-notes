# Lesson 127: FPGA State Machine Part 7 - Glitch Minimization & Output Registering (グリッチの最小化と出力レジスタ)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ปัญหาคลาสสิกของ Mealy Machine คือการที่ Output ขึ้นอยู่กับทั้ง Current State และ Input ซึ่งทำให้เกิด Glitch (Spike) ได้ง่ายหาก Input เปลี่ยนแปลงแบบไม่ซิงโครนัส ในระบบ High-Speed Design ระดับวิศวกรอาวุโส เรามักจะใช้ **Registered Output** หรือเปลี่ยนเป็น **Moore Machine** (ที่ Output ขึ้นกับ State เท่านั้น) เพื่อให้ Output ออกมาผ่าน Flip-Flop ทำให้สัญญาณ Clean และมี Timing ที่แน่นอน

## ทริคหน้างาน OJT (OJT Field Tricks)
- เมื่อออกแบบวงจรเพื่อไปควบคุมโมดูลภายนอก (เช่น ส่งสัญญาณ Write Enable ให้ SRAM) ห้ามส่งสัญญาณ Combinational จาก FSM ออกไปเด็ดขาด ต้องจับสัญญาณนั้นผ่าน Register (D-FF) เสมอ (Registered Output) เพื่อป้องกันปัญหา Data Corruption จาก Glitch
- เทคนิค **Look-ahead Output**: ในกรณีที่ Registered Output ทำให้เกิด Latency ไป 1 Clock เราสามารถคำนวณ Output ล่วงหน้าจาก Next-State Logic เพื่อชดเชย Latency ได้

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **グリッチ (Guritchi)** - Glitch (สัญญาณรบกวนช่วงสั้นๆ)
- **出力レジスタ (Shutsuryoku Rejisuta)** - Output Register (เรจิสเตอร์ขาออก)
- **同期化 (Doukika)** - Synchronization (การซิงโครไนซ์)
- **誤動作 (Godosasa)** - Malfunction (การทำงานผิดพลาด)

## ควิซท้ายบท (Quiz)
**คำถาม:** วิธีแก้ปัญหา Glitch จากเอาต์พุตของ Mealy Machine ที่ดีที่สุดในแง่ของความเสถียรของวงจรคืออะไร?
1. เพิ่มตัวเก็บประจุ (Capacitor) ที่เอาต์พุต
2. เปลี่ยนไปใช้ Asynchronous Reset
3. ต่อเอาต์พุตผ่าน Flip-Flop อีกหนึ่งสเตจ (Registered Output)
4. ลดความถี่คลื่นนาฬิกา (Clock Frequency)

**เฉลย:** 3. ต่อเอาต์พุตผ่าน Flip-Flop อีกหนึ่งสเตจ (Registered Output)
