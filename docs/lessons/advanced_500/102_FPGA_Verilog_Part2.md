# Advanced FPGA/Verilog Part 2: Timing Closure & Static Timing Analysis (STA)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Timing Closure คือกระบวนการที่ทำให้ Design สามารถทำงานได้ที่ความถี่ที่ตั้งเป้าหมายไว้ โดยไม่เกิด Setup/Hold Time Violation การทำ Static Timing Analysis (STA) จะตรวจสอบทุก Path ของวงจร
- **Setup Time ($T_{setup}$):** เวลาที่ข้อมูลต้องคงที่ "ก่อน" ขอบ Clock ถัดไป เพื่อให้ Flip-Flop บันทึกค่าได้ทัน
- **Hold Time ($T_{hold}$):** เวลาที่ข้อมูลต้องคงที่ "หลัง" ขอบ Clock เพื่อป้องกันการบันทึกค่าซ้ำ
สมการสำคัญ:
$T_{clk} \ge T_{cq} + T_{comb} + T_{setup} - T_{skew}$
ถ้า Setup Time ไม่ผ่าน มักเกิดจาก Combinational Logic ยาวเกินไป (Deep Logic Levels) ต้องทำ Pipelining ถ้า Hold Time ไม่ผ่าน มักเกิดจาก Data เดินทางเร็วเกินไป (Clock Skew) เครื่องมือมักจะเติม Delay Buffer ให้อัตโนมัติ

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick 1:** หาก Setup Time Violation เกิดใน Path ที่มีการคำนวณทางคณิตศาสตร์เยอะๆ ให้แบ่งการคำนวณออกเป็นหลาย Clock Cycle (Pipelining)
- **OJT Trick 2:** ระวังการใช้ Reset แบบ Asynchronous ที่ปลดพร้อมกัน (De-assertion) อาจทำให้เกิด Recovery/Removal Time Violation ให้ใช้เทคนิค Asynchronous Assert, Synchronous De-assert
- **OJT Trick 3:** การกำหนด False Path ใน SDC file (Synopsys Design Constraints) จะช่วยให้เครื่องมือ Synthesis ไม่ต้องเสียเวลา Optimize Path ที่ไม่ได้ทำงานใน Clock เดียวกันจริงๆ

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **タイミング制約 (Taimingu Seiyaku):** Timing Constraints
- **セットアップ時間 (Settoappu jikan):** Setup Time
- **ホールド時間 (Hōrudo jikan):** Hold Time
- **余裕 (Yoyū):** Slack (ไทม์มิ่งสแล็ค)
- **経路 (Keiro):** Path
- **パイプライン化 (Paipurain-ka):** Pipelining

## ควิซท้ายบท (Quiz)
**Q1:** หากเกิด Setup Time Violation อย่างหนัก (Negative Slack ติดลบเยอะมาก) วิธีใดแก้ปัญหาได้ตรงจุดที่สุดระดับ RTL?
a) เพิ่ม Buffer ในสาย Data
b) ลดความถี่ Clock ลง
c) แทรก Register เพื่อแบ่ง Combinational Logic (Pipelining)
d) เปลี่ยนไปใช้ FPGA เบอร์ที่ใหญ่ขึ้น

*(เฉลย: c)*
