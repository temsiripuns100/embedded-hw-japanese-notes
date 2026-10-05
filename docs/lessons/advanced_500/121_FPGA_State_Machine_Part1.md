# FPGA State Machine - Part 1: Moore vs Mealy in High-Speed Design

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในการออกแบบวงจรดิจิทัลความเร็วสูง (High-Speed Digital Design) การเลือกใช้ Moore หรือ Mealy FSM มีผลอย่างมากต่อ Timing Closure
- **Moore FSM**: Output ขึ้นอยู่กับ State ปัจจุบันเท่านั้น ทำให้มีการ Register output (หรือมี combinational logic สั้นๆ จาก state register) ข้อดีคือป้องกัน Glitch ได้ดี และลดปัญหา Timing violation ในเส้นทาง Critical Path
- **Mealy FSM**: Output ขึ้นอยู่กับ State ปัจจุบันและ Input ปัจจุบัน ทำให้สามารถตอบสนองได้เร็วกว่า 1 Clock Cycle แต่ความเสี่ยงคือ Glitch จาก Input สามารถทะลุไปถึง Output ได้ทันที (Combinational feedback) และอาจทำให้ Timing ปิดยากในระบบที่มี Clock ความถี่สูง

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Senior Trick**: ในงานที่ต้องการความเสถียรสูง (เช่น ควบคุม Motor, อ่านค่า ADC) ให้ใช้ Moore หรือ Mealy แบบที่มี Register ขวาง Output เสมอ (Registered Mealy) เพื่อแยก (Isolate) Timing Path ระหว่าง Module ไม่ให้เกิดยาวเกินไป
- เวลาเจอ Timing Violation บ่อยๆ ให้ลองสังเกตดูว่ามี Combinational path ยาวๆ ที่วิ่งผ่านหลาย FSM หรือเปล่า การตัดด้วย Register (Pipelining) ช่วยได้

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- 順序回路 (Junjokairo) - Sequential Logic / State Machine
- クリティカルパス (Kuritikaru Pasu) - Critical Path
- 誤動作 (Godosah) - Malfunction (เช่น จาก Glitch)
- タイミング制約 (Taimingu Seiyaku) - Timing Constraints
- 検図 (Kenzu) - Design Review / การตรวจสอบแบบ

## ควิซท้ายบท (Quiz)
**Q1**: ข้อใดคือข้อเสียหลักของการใช้ Mealy FSM ในระบบที่มี Clock Frequency สูงๆ?
1) ตอบสนองช้าเกินไป
2) กินพื้นที่ Logic (Area) มากกว่า Moore เสมอ
3) เสี่ยงต่อการเกิด Glitch ที่ Output และทำให้ Timing ปิดยาก
4) ไม่สามารถใช้กับระบบ Synchronous ได้
**เฉลย**: 3) เพราะ Input มีผลต่อ Output ทันทีโดยไม่ผ่าน Register ทำให้ Combinational path ยาวและเกิด Glitch ได้ง่าย
