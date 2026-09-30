# FPGA & VHDL Part 8: Clock Domain Crossing (CDC) & Metastability

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ระบบสมัยใหม่มักจะมีหลาย Clock (Multi-Clock System) สิ่งที่อันตรายที่สุดคือ **Metastability**
- **Metastability:** เกิดเมื่อข้อมูลเปลี่ยนค่าในจังหวะ Setup/Hold time ของ Clock ปลายทาง ทำให้ Flip-Flop ตัดสินใจไม่ได้ว่าเป็น 0 หรือ 1 ค่าแรงดันจะค้างอยู่ตรงกลางชั่วขณะ ส่งผลให้ลอจิกพังทั้งระบบ (MTBF: Mean Time Between Failures)
- **การแก้ปัญหา 1-bit:** ใช้ 2-Flop Synchronizer (หรือ 3-Flop)
- **การแก้ปัญหา Multi-bit:** ใช้ Asynchronous FIFO หรือ Handshake Protocol (Req/Ack)

## ทริคหน้างาน OJT (OJT Field Tricks)
- **ข้อห้ามร้ายแรง (Fatal Error):** ห้ามนำ 2-Flop Synchronizer ไปใช้กับสัญญาณ Bus (Multi-bit) เด็ดขาด เพราะสายสัญญาณแต่ละเส้นมี Routing Delay ไม่เท่ากัน ข้อมูลที่ข้ามไปอาจจะผสมกันระหว่างค่าเก่าและค่าใหม่ ทำให้ได้ค่าที่ผิดพลาด
- เมื่อใช้ Async FIFO ต้องแปลง Pointer ให้เป็น **Gray Code** ก่อนส่งข้าม Clock Domain เพราะ Gray Code เปลี่ยนแปลงทีละ 1 bit เสมอ ป้องกันปัญหาจาก Routing skew

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **非同期 (Hidouki)** - Asynchronous (อซิงโครนัส / ไม่ซิงก์กัน)
- **メタスタビリティ (Metasutabiriti)** - Metastability (สภาวะกึ่งเสถียร)
- **クロックドメイン交差 (Kurokkudomein kousa)** - Clock domain crossing (CDC)
- **同期化回路 (Doukika kairo)** - Synchronizer (วงจรซิงโครไนเซอร์)

## ควิซท้ายบท (Quiz)
**Q:** วิธีที่ถูกต้องในการส่งสัญญาณ "ค่า Counter ขนาด 16-bit" ข้ามไปยังอีก Clock Domain หนึ่งคืออะไร?
**A:** ห้ามใช้ 2-Flop synchronizer ตรงๆ แต่ควรใช้ **Asynchronous FIFO** หรือแปลง Counter เป็น **Gray Code** ก่อนข้าม Clock Domain
