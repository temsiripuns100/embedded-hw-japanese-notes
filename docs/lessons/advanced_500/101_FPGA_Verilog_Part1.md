# Advanced FPGA/Verilog Part 1: Clock Domain Crossing (CDC) & Metastability

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior, ปัญหาที่เจอบ่อยที่สุดและแก้ยากที่สุดคือเรื่องของ Clock Domain Crossing (CDC) เมื่อสัญญาณข้ามจาก Clock หนึ่งไปยังอีก Clock หนึ่งที่ทำงานไม่พร้อมกัน (Asynchronous) จะเกิดปัญหา Metastability ซึ่งทำให้ Flip-Flop ไม่สามารถตัดสินใจได้ว่าจะเป็น Logic 1 หรือ 0 ภายในเวลาที่กำหนด
การแก้ไขปัญหาเบื้องต้นใช้ 2-Stage Synchronizer (Dual Flip-Flop) แต่สำหรับข้อมูลที่เป็น Data Bus ไม่สามารถใช้ Synchronizer ธรรมดาได้ ต้องใช้เทคนิคอย่าง Asynchronous FIFO หรือ Handshake Protocol (Request/Acknowledge) เพื่อให้แน่ใจว่า Data นั้น Stable แล้วก่อนที่ฝั่งรับจะนำไปใช้

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick 1:** ห้ามใช้ 2-Stage Synchronizer กับสัญญาณที่เป็น Bus เด็ดขาด เพราะสัญญาณแต่ละบิตจะ Delay ไม่เท่ากัน ทำให้เกิด Skew และฝั่งรับจะได้ข้อมูลที่ผิดพลาด (Coherency Issue)
- **OJT Trick 2:** สัญญาณที่จะเอาไปเข้า Synchronizer ควรจะลง Register ฝั่งส่งก่อน 1 ครั้ง (Glitch-free) เพื่อป้องกัน Combinational Glitch ไปทำให้เกิด Metastability ที่แย่ลง
- **OJT Trick 3:** ในการจำลอง (Simulation) มักจะไม่เห็นปัญหา CDC ต้องใช้เครื่องมือ CDC Analysis (เช่น SpyGlass CDC) ช่วยวิเคราะห์เสมอ

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **非同期 (Hidōki):** Asynchronous (อซิงโครนัส)
- **準安定状態 (Jun-antei jōtai):** Metastability
- **同期化回路 (Dōkika kairo):** Synchronizer circuit
- **受け渡し (Ukewatashi):** Handover/Transfer (การส่งผ่านข้อมูล)
- **すれ違い (Surechigai):** Passing each other (มักใช้เรียกจังหวะที่สัญญาณและ Clock ขัดกันจนเกิด Glitch)

## ควิซท้ายบท (Quiz)
**Q1:** ทำไมถึงไม่ควรใช้ 2-Stage Synchronizer กับ Data Bus 32-bit ข้าม Clock Domain?
a) เปลือง Flip-Flop
b) ทำให้เกิด Routing Congestion
c) สัญญาณแต่ละบิตอาจไปถึงไม่พร้อมกัน ทำให้ข้อมูลผิดพลาด
d) ถูกทุกข้อ

*(เฉลย: c)*
