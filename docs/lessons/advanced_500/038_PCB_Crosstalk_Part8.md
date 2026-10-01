# 038: PCB Crosstalk เจาะลึก Part 8 - DDR Memory Interface

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
บัส DDR (DDR4/DDR5) เป็นระบบขนานที่มีจำนวนเส้นสัญญาณมหาศาล (Parallel Bus) ทำให้ปัญหา Crosstalk หนักหน่วงในลักษณะ **SSO (Simultaneous Switching Output) Crosstalk**:
- **Data (DQ) & Strobe (DQS):** กลุ่ม Byte Lane (8 บิต) จะถูกกระหน่ำสวิตช์พร้อมกัน เมื่อ DQ ทั้ง 8 เส้นเปลี่ยนจาก 0 -> 1 พร้อมกัน พลังงานรวมที่ Coupling ไปกวน DQS จะมหาศาล (Aggregated Crosstalk)
- **Crosstalk-Induced Jitter (CIJ):** หากเส้น DQ ขยับพร้อมกันในทิศทางเดียวกัน สัญญาณ Crosstalk จะดึงหรือดัน Edge ของ Victim ทำให้สัญญาณมาถึงเร็วขึ้น (Speed-up) หรือช้าลง (Push-out) เกิดเป็น Timing Jitter มหาศาล ขโมย Timing Margin (Setup/Hold Time) ไป
- **Fly-by Topology:** ใน Address/Command/Control bus การเดินสายแบบ Daisy-chain ทำให้ Impedance สวิงตามจุดแยก เกิด Reflection สะท้อนกลับไปมา ผสมกับ Crosstalk เกิดเป็น ISI (Inter-Symbol Interference)

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **แยก Byte Lane:** กลุ่ม DQ0-DQ7+DQS0 ต้องถูก Route ให้อยู่รวมกันแบบแน่นๆ ในกลุ่มเดียวกัน (เพื่อรักษาระยะเวลา) แต่ต้องทิ้งห่างจากกลุ่ม DQ8-DQ15 อย่างน้อย 4W-5W เพื่อป้องกัน Cross-byte interference
- **DQS Isolation:** เส้น DQS (Strobe) คือหัวใจของ Timing (เพราะใช้ Trigger Data) จงให้สิทธิพิเศษกับ DQS เสมอ! ให้ระยะ Spacing พิเศษ (+3W/4W ภายในกลุ่มตัวเอง) และห้ามทำ Snake routing (Length match) ถี่ๆ ในบริเวณที่ชิดเส้นอื่น

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **同時スイッチングノイズ (Dōji suitchingu noizu):** Simultaneous Switching Noise (SSO/SSN)
- **ジッタ (Jitta):** Jitter
- **タイミング余裕 (Taimingu yoyū):** Timing margin
- **波形品質 (Hakei hinshitsu):** Signal Quality (Signal Integrity)
- **分岐 (Bunki):** Branching / Stub (จุดแยกของสาย)

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** ในการทำบัส DDR ปรากฏการณ์ Crosstalk-Induced Jitter (CIJ) จะรุนแรงที่สุดเมื่อเส้น Data (DQ) มีพฤติกรรมอย่างไร?
**คำตอบ:** เมื่อเส้น DQ รอบๆ ตัว Victim ทำการเปลี่ยนสถานะ (Switching) พร้อมกันในทิศทางเดียวกันทั้งหมด (เช่น เปลี่ยนจาก 0 เป็น 1 พร้อมกัน 7 เส้น) พลังงานจะรวมศูนย์ดันให้ Edge ของสัญญาณ Victim มี Timing เปลี่ยนแปลงไปมากที่สุด (เกิด Jitter หนักสุด)
