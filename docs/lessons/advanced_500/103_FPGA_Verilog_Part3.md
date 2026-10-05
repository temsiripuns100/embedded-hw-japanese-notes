# Advanced FPGA/Verilog Part 3: AXI Protocol & High-Speed Interconnects

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
AMBA AXI (Advanced eXtensible Interface) เป็นมาตรฐานโปรโตคอลการสื่อสารบนชิป (SoC) ที่ใช้กันแพร่หลายใน FPGA/ASIC ปัจจุบัน AXI4 แยกช่องทาง (Channels) ออกจากกันอย่างชัดเจน ได้แก่ Read Address, Read Data, Write Address, Write Data, และ Write Response ทำให้สามารถทำ Burst Transfer และ Outstanding Transactions ได้ (ส่ง Request ไปก่อนโดยไม่ต้องรอ Response ค่อยรับรวดเดียว)
การออกแบบ AXI Master/Slave ที่ดีต้องเข้าใจเรื่อง Valid/Ready Handshake อย่างถ่องแท้ กฎเหล็กคือ ห้ามให้สัญญาณ Valid ตก (De-assert) ถ้า Ready ยังไม่มา และห้ามให้สัญญาณ Valid ขึ้นอยู่กับ Ready (เพื่อป้องกัน Deadlock)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick 1:** Deadlock มักเกิดจากการออกแบบ Combinational Path ระหว่าง Valid กับ Ready (เช่น ให้ Valid = 1 ก็ต่อเมื่อ Ready = 1) ซึ่งผิดสเปก ต้องใช้ Register ขับสัญญาณ Valid ออกไปเสมอ
- **OJT Trick 2:** ในการดึงข้อมูลปริมาณมาก (เช่น จาก DDR) ควรใช้ AXI Burst Transfer (เช่น Burst Length 16 หรือ 256) แทนการทำ Single Transfer เพื่อรีดแบนด์วิดท์สูงสุด
- **OJT Trick 3:** ใช้ AXI Protocol Checker (IP จากผู้ผลิต) หรือ SystemVerilog Assertions (SVA) จับผิดพฤติกรรม Valid/Ready เสมอตอน Simulate

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **握手 (Akushu):** Handshake
- **転送 (Tensō):** Transfer
- **帯域幅 (Taiiki-haba):** Bandwidth
- **応答 (Ōtō):** Response
- **停滞 (Teitai):** Stagnation/Deadlock (การค้างของ Bus)

## ควิซท้ายบท (Quiz)
**Q1:** กฎเหล็กของ Valid/Ready Handshake ใน AXI Protocol คืออะไร?
a) Valid ต้องรอ Ready ก่อนถึงจะ Assert ได้
b) Ready ห้าม De-assert เด็ดขาด
c) ทันทีที่ Valid ถูก Assert แล้ว ห้าม De-assert จนกว่า Ready จะมาตอบรับ
d) Valid และ Ready ต้อง Assert พร้อมกันใน Cycle เดียวกัน

*(เฉลย: c)*
