# Advanced FPGA/Verilog Part 4: Finite State Machine (FSM) Optimization & Deadlock Prevention

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การออกแบบ State Machine มี 2 แบบหลักคือ Moore (Output ขึ้นกับ State อย่างเดียว) และ Mealy (Output ขึ้นกับ State และ Input)
ในระดับ Senior ต้องคำนึงถึง FSM Encoding ด้วย ปกติจะใช้ Binary, Gray Code, หรือ One-Hot
- **One-Hot Encoding:** ใช้ Flip-Flop มาก (1 บิตต่อ 1 State) แต่ Combinational Logic ในการถอดรหัสจะน้อยมาก ทำให้ทำงานที่ความถี่สูงได้ดีมาก เหมาะกับ FPGA ที่มี Flip-Flop เหลือเฟือ
- **Deadlock Prevention:** ต้องมี `default` case หรือกลไก Timeout เสมอ ป้องกันการเกิด Single Event Upset (SEU) ที่ทำให้ FSM หลุดไปอยู่ใน State ที่ไม่มีอยู่จริงแล้วค้างถาวร

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick 1:** เขียน FSM แบบ 3-Block (Next State Logic, State Register, Output Logic) จะทำให้โค้ดอ่านง่าย ตรวจสอบง่าย (検図しやすい) และ Maintain ง่ายกว่าแบบ 1-Block หรือ 2-Block ยำรวมกัน
- **OJT Trick 2:** ห้ามใช้เงื่อนไขที่อาจเกิด Glitch (เช่น สัญญาณจากภายนอกที่ยังไม่ผ่าน Synchronizer) มาเป็นเงื่อนไขในการเปลี่ยน State เด็ดขาด
- **OJT Trick 3:** กำหนด State ให้เป็น Parameter หรือ `localparam` แทนการใช้ตัวเลข Magic Number เพื่อความชัดเจน

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **状態遷移図 (Jōtai sen'i-zu):** State Transition Diagram
- **初期化 (Shokika):** Initialization
- **抜け出せない (Nukedasenai):** Cannot exit (ใช้เรียกอาการ Deadlock)
- **冗長 (Jōchō):** Redundancy
- **例外処理 (Reigai shori):** Exception handling / Default case

## ควิซท้ายบท (Quiz)
**Q1:** ข้อใดคือข้อดีของ One-Hot Encoding ใน FSM เมื่อเทียบกับ Binary Encoding?
a) ประหยัดจำนวน Flip-Flop มากที่สุด
b) ใช้ Combinational Logic น้อย ทำให้ได้ Clock Frequency ที่สูงขึ้น
c) ป้องกันปัญหาสัญญาณรบกวนภายนอกได้ 100%
d) ใช้เขียนโปรแกรมบนไมโครคอนโทรลเลอร์ได้ดีกว่า

*(เฉลย: b)*
