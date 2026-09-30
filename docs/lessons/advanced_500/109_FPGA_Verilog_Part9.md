# Lesson 109: Advanced Timing Closure & Constraints (SDC) (タイミング収束と制約)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การทำ Timing Closure คือเป้าหมายสูงสุดหลังจากการเขียน RTL เสร็จ
- **Setup Time & Hold Time Equations:** ความเข้าใจอย่างถ่องแท้ว่า Setup time violation เกิดจาก Data path ช้าเกินไป (หรือ Clock ไวไป) ส่วน Hold time เกิดจาก Data path ไวเกินไป
- **Multi-Cycle Paths (MCP):** การกำหนดให้บาง Path สามารถใช้เวลาเดินทางได้มากกว่า 1 Clock cycle หากมีการควบคุม Data valid flag อย่างรัดกุม
- **Pipelining & Register Retiming:** การสอดแทรก Flip-Flop ลงใน Combinational logic ที่ยาวเกินไป เพื่อตัดแบ่ง Delay ให้สั้นลง (เพิ่ม Max Frequency)

## 2. ทริคหน้างาน OJT (OJT Field Tricks)
- **Over-constraining:** เวลา Synthesis ทีมมักจะตั้งเป้า Clock ให้เร็วกว่าสเปคจริง 10-15% (Over-constrain) เพื่อเผื่อ Margin ให้กับขั้นตอน Place & Route (P&R)
- **Critical Path Analysis:** เมื่อเจอ Timing violation อย่าเพิ่งแก้โค้ดมั่ว ให้ดูรายงาน Timing report ว่า Critical path อยู่ที่ไหน บางทีสาเหตุมาจาก Fan-out สูงเกินไป แค่ทำ Register Replication ก็ผ่านแล้ว

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **タイミング収束 (Taimingu shūsoku):** Timing closure
- **制約 (Seiyaku):** Constraint
- **セットアップ時間 (Settoappu jikan):** Setup time
- **ホールド時間 (Hōrudo jikan):** Hold time
- **クリティカルパス (Kuritikaru pasu):** Critical path

## 4. ควิซท้ายบท (Quiz)
**Q1:** การเพิ่ม Pipeline stages ช่วยแก้ปัญหาอะไร และมีข้อเสียอย่างไร?
**Answer:** ช่วยแก้ปัญหา Setup time violation ทำให้วงจรทำงานที่ความถี่ (Fmax) สูงขึ้นได้ แต่ข้อเสียคือเพิ่ม Latency ในการประมวลผลและใช้ Flip-Flop (Resource) มากขึ้น
