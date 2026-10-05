# Lesson 129: FPGA State Machine Part 9 - CDC & Asynchronous Domains (非同期ドメイン間のFSMインターフェース)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การรับส่งข้อมูลหรือสัญญาณควบคุมข้าม Clock Domain (CDC - Clock Domain Crossing) นำมาซึ่งความเสี่ยงอย่างร้ายแรงเรื่อง Metastability การให้ FSM หนึ่งคุยกับอีก FSM หนึ่งต่าง Clock Domain กัน ห้ามต่อสัญญาณโดยตรงเด็ดขาด ต้องใช้เทคนิคเช่น **Multi-Flop Synchronizer** สำหรับสัญญาณควบคุมเส้นเดียว หรือใช้ **Asynchronous FIFO / Handshake Protocols** (เช่น Request-Acknowledge) สำหรับการส่งผ่านข้อมูลที่เกี่ยวข้องกัน (Bus)

## ทริคหน้างาน OJT (OJT Field Tricks)
- กฎเหล็ก (Golden Rule): สัญญาณที่จะส่งผ่าน Synchronizer ต้องเป็นแบบ Registered Output เท่านั้น และต้องไม่มี Combinational Logic คั่นระหว่างต้นทางและ Synchronizer
- ในการทำ 4-Phase Handshaking ระหว่าง FSM ควรวาด Timing Diagram ระหว่าง FSM-A (Tx) และ FSM-B (Rx) ให้ชัดเจนก่อนเขียนโค้ดเสมอ และใช้คำสั่งจำกัด False Path ใน SDC (Synopsys Design Constraints) เพื่อป้องกันไม่ให้ Tool ไปฝืนทำ Timing Analysis ผิดจุด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **非同期 (Hidouki)** - Asynchronous (อซิงโครนัส / ไม่ประสานจังหวะกัน)
- **メタスタビリティ (Metasutabiriti)** - Metastability (สภาวะกึ่งเสถียร)
- **クロックドメイン交差 (Kurokku Domein Kousa)** - Clock Domain Crossing (CDC)
- **ハンドシェイク (Handosheiku)** - Handshake (การจับมือสื่อสาร)

## ควิซท้ายบท (Quiz)
**คำถาม:** เทคนิคใดเหมาะสมที่สุดสำหรับการส่งข้อมูลขนาด 32-bit ระหว่าง FSM สองตัวที่ทำงานด้วย Clock ต่างความถี่กันอย่างมาก?
1. Multi-Flop Synchronizer ขนานกัน 32 เส้น
2. 4-Phase Handshaking ขนาน 32 เส้น
3. Asynchronous FIFO
4. ต่อสายตรงและกำหนด False Path

**เฉลย:** 3. Asynchronous FIFO
