# FPGA PLL Deep Dive - Part 3: Clock Distribution Networks and Skew Management

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
Clock Tree ใน FPGA ถูกออกแบบมาเพื่อรักษา Clock Skew ให้ต่ำที่สุดเมื่อสัญญาณไปถึง Flip-Flop แต่ละตัว (Global Clock Network)
การใช้ PLL ร่วมกับ Clock Network มีโครงสร้างสำคัญคือ **Zero-Delay Buffer (ZDB) Mode**
ในโหมดนี้ Feedback Path ของ PLL จะวิ่งผ่าน Global Clock Network (GCLK) ก่อนกลับเข้า PFD ทำให้ Delay ของ Clock Tree ถูกชดเชย (Compensated) ส่งผลให้ Clock ที่ขา Output ของ FPGA ตรงกับ Clock ที่ขา Input (Phase Alignment)
นอกจากนี้ยังมี **Source Synchronous Compensation**: ชดเชย Delay จาก Input Pin ไปถึง Register เพื่อให้ Setup/Hold time ดียิ่งขึ้นสำหรับการรับส่งข้อมูลความเร็วสูง

## 2. ทริคหน้างาน OJT (現場のOJTテクニック)
- **Clock Crossing (CDC)**: แม้ Clock จะมาจาก PLL เดียวกัน แต่คนละความถี่ (เช่น 100MHz กับ 200MHz) ถือว่าเป็น Synchronous Clock แต่เครื่องมือ (STA Tool) อาจวิเคราะห์พลาด หาก Edge ไม่สัมพันธ์กัน (Phase Relationship) ต้องกำหนด `create_generated_clock` ให้ชัดเจนใน SDC file
- **Feedback Path Delay**: ถ้าเดินสาย Feedback นอก FPGA (External Feedback) ระวังเรื่อง Skew ของบอร์ด (PCB Trace Delay) $1 \text{ inch} \approx 160 \text{ ps}$ (FR4) ต้องนำมาหักล้างใน TimeQuest/Timing Analyzer
- **Clock Muxing**: การสลับ Clock (Clock Switchover) ในตัว PLL ต้องใช้ Glitch-free MUX หรือรอให้ PLL Lock ใหม่ก่อน มิฉะนั้นจะเกิด Runt Pulse (Clock สั้นกว่าปกติ) ทำให้ State Machine พัง

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語)
- **配線遅延 (はいせんちえん, Haisen Chien)**: Routing Delay / Trace Delay
- **スキュー調整 (すきゅーちょうせい, Sukyuu Chousei)**: Skew Adjustment / Skew Management
- **同期化 (どうきか, Doukika)**: Synchronization
- **クロック乗り換え (くろっくのりかえ, Kurokku Norikae)**: Clock Domain Crossing (CDC)
- **切り替え (きりかえ, Kirikae)**: Switchover / Muxing

## 4. ควิซท้ายบท (理解度チェック)
**Q3:** ประโยชน์หลักของการตั้งค่า PLL เป็น Zero-Delay Buffer Mode (ZDB) คืออะไร?
A) ลด Jitter ของวงจร
B) ชดเชย Delay ของ Clock Network ภายใน FPGA
C) เพิ่มช่วงความถี่ VCO
D) ลดการกินไฟของ PLL

*เฉลย:* B) ชดเชย Delay (遅延補償) ของ Global Clock Network ทำให้ Phase ภายนอกและภายในตรงกัน
