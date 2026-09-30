# Lesson 128: FPGA State Machine Part 8 - Fault-Tolerant FSM Design (耐故障性ステートマシン)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระบบที่มีความเสี่ยงต่อรังสี (เช่น Aerospace, Automotive) อนุภาคสามารถชน Flip-Flop ทำให้เกิดปรากฏการณ์ Single Event Upset (SEU) ส่งผลให้ FSM กระโดดไปอยู่ State ที่ไม่ได้นิยามไว้ (Illegal State) วิศวกรระดับสูงต้องออกแบบ **Safe State Machine** โดยการครอบคลุมกรณี `default` หรือ `when others` เสมอ และมักใช้เทคนิค TMR (Triple Modular Redundancy) หรือใช้ Hamming Code ใน State Encoding เพื่อแก้ไขข้อผิดพลาดโดยอัตโนมัติ

## ทริคหน้างาน OJT (OJT Field Tricks)
- การใส่แค่ `default: next_state = IDLE;` ใน Verilog หรือ `when others => next_state <= IDLE;` ใน VHDL อาจไม่เพียงพอ เพราะ Synthesis Tool มักจะ Optimize ส่วนนี้ทิ้งไป (เนื่องจากมันมองว่าเป็น Unreachable Code) เราต้องบังคับ Synthesis Tool ไม่ให้ Optimize ทิ้ง เช่น การใช้แอตทริบิวต์ `(* safe_recovery_state = "true" *)` (ใน Vivado) หรือการใช้ Custom Logic คอยตรวจสอบ State Bit
- ในงานระดับยานยนต์ (ISO 26262) การทำ Lockstep FSM ถือเป็นมาตรฐานสำคัญ

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **耐故障性 (Taikoshousei)** - Fault Tolerance (ความทนทานต่อความผิดพร่อง)
- **未定義状態 (Miteigi Joutai)** - Undefined State (สถานะที่ไม่ได้นิยาม)
- **冗長化 (Jouchouka)** - Redundancy (การทำซ้ำเพื่อสำรอง)
- **回復 (Kaifuku)** - Recovery (การฟื้นฟู/การกลับคืนสู่สภาพปกติ)

## ควิซท้ายบท (Quiz)
**คำถาม:** ปัญหาที่ Synthesis Tool อาจมองข้ามและ Optimize โค้ดส่วน "Safe Recovery" ทิ้งไป เกิดจากสาเหตุใด?
1. Tool มีบั๊ก
2. Tool มองว่า Illegal State เป็น Unreachable Condition (เงื่อนไขที่ไม่มีวันไปถึง) ภายใต้การทำงานปกติ
3. Tool ต้องการประหยัดพลังงานมากเกินไป
4. โค้ดไม่ได้ระบุ Clock Signal

**เฉลย:** 2. Tool มองว่า Illegal State เป็น Unreachable Condition (เงื่อนไขที่ไม่มีวันไปถึง) ภายใต้การทำงานปกติ
