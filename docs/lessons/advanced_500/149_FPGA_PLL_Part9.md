# Lesson 149: FPGA PLL Advanced - Part 9 (PLL Cascading & CDC)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
**PLL Cascading** คือการนำ Output ของ PLL ตัวแรก ไปเข้าเป็น Input ของ PLL ตัวที่สอง มักใช้เมื่อต้องการความถี่ที่คำนวณจาก Clock หลักไม่ได้โดยตรง สิ่งที่ต้องระวังขั้นสุดคือ **Jitter Peaking** เมื่อ Jitter จากตัวแรกเข้าสู่ Loop Filter ของตัวที่สองในช่วง Bandwidth ที่ทับซ้อนกัน จะเกิดการขยาย Jitter ให้ใหญ่ขึ้นอย่างมาก

## 2. ทริคหน้างาน OJT (On-the-Job Tricks)
- **Bandwidth Tuning**: หากจำเป็นต้อง Cascade ให้ตั้งค่า Bandwidth ของ PLL ตัวแรกให้แคบ (Low Bandwidth) เพื่อกรอง High-frequency Jitter และตั้งค่า PLL ตัวที่สองให้กว้าง (High Bandwidth) เพื่อให้มัน Track การเปลี่ยนแปลงได้ทัน
- **Clock Domain Crossing (CDC)**: สัญญาณที่ข้ามโดเมนระหว่าง Clock จาก PLL ต่างตัวกัน **ห้าม** ถือว่าเป็น Synchronous เด็ดขาด แม้จะมาจาก Source เดียวกัน ต้องใช้เทคนิค CDC (เช่น Async FIFO, 2-FF Synchronizer) เสมอ

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **カスケード接続 (Kasukeedo Setsuzoku)**: Cascade Connection
- **帯域幅 (Taiikihaba)**: Bandwidth
- **クロックドメインクロッシング (Kurokku Domein Kurosshingu)**: CDC
- **ジッタピーキング (Jitta Piikingu)**: Jitter Peaking
- *"カスケード接続時の帯域幅の設定と、CDCの処理が検図のポイントです。"* (จุดสำคัญในการตรวจแบบคือ การตั้งค่า Bandwidth ตอนต่อ Cascade และการจัดการ CDC)

## 4. ควิซท้ายบท (Quiz)
**Q:** หากหลีกเลี่ยงการต่อ PLL แบบ Cascade ไม่ได้ ควรตั้งค่า Bandwidth ของ PLL1 และ PLL2 อย่างไร?
**A:** PLL1 = Low Bandwidth, PLL2 = High Bandwidth เพื่อลดปัญหา Jitter Peaking
