# Lesson 112: Advanced FSM Design & Timing Closure

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Finite State Machine (FSM) ในระดับองค์กรจะนิยมใช้ Moore Machine หรือ Mealy Machine ที่มีการลงทะเบียนเอาต์พุต (Registered Mealy) เพื่อลดปัญหา Glitch การเขียน FSM แบบ 3-process (Next state logic, State register, Output logic) ช่วยให้อ่านโค้ดและดีบักได้ง่ายขึ้น
เรื่อง Timing Closure คือหัวใจสำคัญ หาก fmax ไม่ถึงตามสเปก ต้องวิเคราะห์ Critical Path ผ่านรายงาน Timing Analysis ว่าเกิดจาก Logic Delay หรือ Routing Delay เพื่อนำไปสู่การทำ Pipelining หรือ Register Retiming

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **State Encoding:** ใช้ One-Hot Encoding สำหรับ FSM ที่มีความเร็วสูงใน FPGA เพราะ Flip-Flop มีเยอะแต่ LUT มีจำกัด
- **Default State Recovery:** ใส่ `when others => state <= IDLE;` เสมอ เพื่อป้องกัน FSM ค้างใน State ที่ไม่รู้จัก (เช่น จากรังสี SEU ในอวกาศหรือสัญญาณรบกวน)
- **Critical Path Cutting:** หากมี Logic ลึกเกินไป ให้ใส่ Flip-Flop คั่นกลาง (Pipelining)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **状態遷移図 (Joutai Senizu):** State Transition Diagram (แผนภาพการเปลี่ยนสถานะ)
- **タイミング違反 (Timing Ihan):** Timing Violation (การละเมิดเงื่อนไขเวลา)
- **クリティカルパス (Kuritikaru Pasu):** Critical Path (เส้นทางวิกฤต)
- **同期式設計 (Doukishiki Sekkei):** Synchronous Design (การออกแบบแบบซิงโครนัส)

## ควิซท้ายบท (Quiz)
1. ทำไม One-Hot Encoding จึงเหมาะสมกับ FPGA มากกว่า Binary Encoding สำหรับ FSM ความเร็วสูง?
2. 状態遷移図 มีความสำคัญอย่างไรในการทำ 検図?
