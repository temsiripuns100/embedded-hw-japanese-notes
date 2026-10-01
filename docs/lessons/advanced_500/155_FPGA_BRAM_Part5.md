# Lesson 155: BRAM for High-Speed FIFOs and Clock Domain Crossing (CDC)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
BRAM ถูกใช้งานอย่างกว้างขวางเพื่อทำเป็น Asynchronous FIFO สำรับการรับส่งข้อมูลข้าม Clock Domain (CDC) ระดับ Senior ต้องระมัดระวังเรื่องของ Pointer Synchronization โดยใช้ Gray Code เพื่อป้องกันการส่งค่า Pointer ที่มีบิตเปลี่ยนพร้อมกันหลายบิต (Multi-bit transition) ข้ามโดเมนนาฬิกา ซึ่งอาจนำไปสู่ Metastability การคำนวณ FIFO Depth ให้เพียงพอต่อ Burst size และ Latency ระหว่างโดเมนก็เป็นเรื่องที่ต้องคำนวณตามหลักคณิตศาสตร์

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Gray Code Counters:** ในการทำ Async FIFO ด้วย BRAM ต้องแปลง Binary pointer เป็น Gray code ก่อนนำข้าม Clock domain โดยใช้ 2-stage (หรือ 3-stage) Synchronizer
- **Almost Full / Almost Empty Flags:** การคำนวณ Flag เหล่านี้ควรเผื่อ Latency ในฝั่งรับเสมอ มิฉะนั้นอาจเกิด Data Overrun แม้ว่าจะเห็น Flag ช้าไปก็ตาม

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- 非同期 (Hidouki) - Asynchronous
- クロック乗せ換え (Kurokku nosekae) - Clock Domain Crossing (CDC)
- 空/満杯フラグ (Kara / Manpai furagu) - Empty / Full flag
- メタスタビリティ (Metasutabiriti) - Metastability

## ควิซท้ายบท (Quiz)
**คำถาม:** เหตุใดจึงต้องเข้ารหัส Read/Write Pointer เป็น Gray Code ก่อนส่งข้าม Clock Domain ใน Asynchronous FIFO?
**คำตอบ:** (เฉลย: เพื่อให้ในแต่ละครั้งที่ Pointer มีการนับเพิ่มหรือลด จะมีเพียง 1 บิตเท่านั้นที่เปลี่ยนแปลง ป้องกันปัญหา Metastability จากการอ่านข้อมูลแบบ Multi-bit ที่กำลัง transition)
