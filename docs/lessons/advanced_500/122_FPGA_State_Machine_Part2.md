# FPGA State Machine - Part 2: State Encoding Techniques

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การเข้ารหัส State (State Encoding) ส่งผลต่อพื้นที่ (Area), ความเร็ว (Fmax), และการใช้พลังงาน (Power) ของ FPGA:
- **Binary Encoding**: ใช้จำนวน Flip-Flop น้อยที่สุด (O(log2(N))) แต่ต้องใช้ Combinational Logic ในการถอดรหัส (Decode) เยอะ เหมาะกับ State จำนวนมากและไม่แคร์ Fmax มากนัก
- **One-Hot Encoding**: ใช้ 1 Flip-Flop ต่อ 1 State (O(N)) ไม่ต้องใช้ Logic ในการ Decode ข้อดีคือได้ Fmax สูงมาก และลด Dynamic Power Consumption (เพราะมีแค่ 2 Bit ที่เปลี่ยนค่าต่อการเปลี่ยน State 1 ครั้ง) เหมาะกับ FPGA สมัยใหม่ที่มี Flip-Flop เหลือเฟือ
- **Gray Code Encoding**: เปลี่ยนค่าเพียง 1 Bit ระหว่าง State ที่ติดกัน ลดปัญหา Glitch ในการ Decode และใช้พลังงานต่ำมาก เหมาะกับ FIFO Pointers หรือ Asynchronous Systems

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Senior Trick**: เวลาเขียน RTL (Verilog/VHDL) ใน Synthesis Tool สมัยใหม่ (เช่น Vivado, Quartus) มักจะทำ Auto-Encoding ให้ (เช่น แปลง Binary เป็น One-Hot) แต่ถ้าต้องการบังคับเพื่อทำ Optimization เฉพาะจุด ให้ใช้ Attribute บังคับ (เช่น `(* fsm_encoding = "one_hot" *)` ใน Vivado)
- ระวังเวลาทำ One-Hot, อย่าลืมจัดการกรณี Illegal State (เช่น บิตติดกัน 2 บิต หรือดับหมด) เสมอ (ใช้ `default` case ไปยัง Safe State)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- 状態遷移図 (Joutaiseni-zu) - State Transition Diagram
- 消費電力 (Shouhidenryoku) - Power Consumption
- 最適化 (Saitekika) - Optimization
- フリップフロップ (Furippufuroppu) - Flip-Flop
- 不正状態 (Fusei Joutai) - Illegal State

## ควิซท้ายบท (Quiz)
**Q1**: ถ้าต้องการออกแบบ FSM สำหรับ FPGA ที่เน้นความเร็วสูงสุด (Fmax) ควรเลือกใช้ State Encoding แบบใด?
1) Binary
2) Gray Code
3) One-Hot
4) BCD
**เฉลย**: 3) One-Hot เพราะใช้ Combinational Logic ในการ Decode น้อยที่สุด ทำให้ Delay สั้นที่สุด
