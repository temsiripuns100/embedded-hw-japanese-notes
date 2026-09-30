# FPGA & VHDL Part 7: Advanced FSM Design (Mealy vs Moore, One-Hot)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
การออกแบบ FSM (Finite State Machine) ระดับสูงสำหรับ FPGA:
- **State Encoding:** ในขณะที่ CPLD หรือ ASIC อาจจะชอบ Binary หรือ Gray code, FPGA มักจะทำงานได้ดีที่สุดกับ **One-Hot Encoding** เพราะ FPGA มี Flip-Flop จำนวนมาก (Register-rich) การใช้ One-Hot ช่วยลด Combinational Logic ที่ใช้ในการถอดรหัส (Decode) สถานะ ทำให้ได้ Fmax (ความถี่สูงสุด) ที่สูงขึ้น
- **Safe FSM:** สภาพแวดล้อมที่มีสัญญาณรบกวนหรือรังสี (เช่น Aerospace) อาจทำให้เกิด SEU (Single Event Upset) ทำให้ FSM หลุดไปอยู่ State ที่ไม่ได้นิยาม ต้องมี `when others =>` เพื่อดึงกลับมาที่ Safe State เสมอ

## ทริคหน้างาน OJT (OJT Field Tricks)
- **การแยกกระบวนการ (Two-Process vs Three-Process Methodology):** การเขียน FSM แนะนำให้แยก Process ชัดเจน: 1 Process สำหรับ State Register (Sequential), 1 Process สำหรับ Next-State Logic (Combinational) และอาจมีอีก 1 Process สำหรับ Output เพื่อให้อ่านง่ายและไม่เผลอสร้าง Unintended Latch
- อย่าลืมกำหนดค่าเริ่มต้น (Default value) ของทุกสัญญาณใน Combinational Process เพื่อป้องกัน Latch

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **状態遷移図 (Joutai sen'i zu)** - State transition diagram (แผนภาพการเปลี่ยนสถานะ)
- **不正状態 (Fusei joutai)** - Illegal state (สถานะที่ไม่ถูกต้อง/ไม่ได้กำหนด)
- **ラッチ (Ratchi)** - Latch (แลตช์ - สิ่งที่มักเกิดจากความผิดพลาดในการเขียน Combinational logic)
- **組み合わせ回路 (Kumiawase kairo)** - Combinational logic (วงจรตรรกะเชิงจัดหมู่)

## ควิซท้ายบท (Quiz)
**Q:** ทำไม One-Hot Encoding จึงเป็นที่นิยมในการออกแบบ FSM บน FPGA มากกว่า Binary Encoding?
**A:** เพราะ FPGA มีทรัพยากรประเภท Flip-Flop จำนวนมาก และ One-Hot ช่วยลดความซับซ้อนของ Combinational Logic ในการแปลงสถานะ ทำให้วงจรทำงานที่ความถี่สูงขึ้นได้
