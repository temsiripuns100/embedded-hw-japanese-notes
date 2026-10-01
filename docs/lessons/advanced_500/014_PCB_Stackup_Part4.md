# Advanced PCB Stackup Part 4: HDI Stackup & Via Structures (HDIスタックアップとビア構造)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
High Density Interconnect (HDI) เป็นเทคโนโลยีที่ขาดไม่ได้สำหรับ SoC สมัยใหม่ที่มีพินระดับหลายพัน การเข้าใจ Stackup แบบ N+C+N (เช่น 1+N+1, 2+N+2, 3+N+3) และ Any-Layer HDI เป็นหัวใจสำคัญของ Senior Designer
ข้อจำกัดทางวิศวกรรมของ Microvia คือ "Aspect Ratio" (อัตราส่วนระหว่างความลึกต่อเส้นผ่านศูนย์กลาง) ซึ่งปกติไม่ควรเกิน 0.8:1 ถึง 1:1 การออกแบบ Stacked Microvia (ビア・オン・ビア) มีความเสี่ยงในการเกิด Microvia Reliability failure มากกว่า Staggered Microvia ในสภาวะ Thermal Cycling เนื่องจากความเค้นที่สะสมบริเวณรอยต่อของแผ่นทองแดง (Target Pad)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- การออกแบบให้เป็น Staggered Microvia ปลอดภัยต่อเรื่อง DFM (Design for Manufacturing) และความน่าเชื่อถือระยะยาว มากกว่า Stacked Microvia หากเลี่ยง Stacked Microvia ไม่ได้ ให้กำหนดให้มีการทำ Copper Plated Shut (อุดรูด้วยทองแดงเต็ม) เสมอ
- ระวังปัญหา "Z-axis Expansion" ที่ดันให้ Microvia ขาด (Open circuit) เวลาผ่านตู้อบ Reflow หลายรอบ แนะนำให้สอบถาม Vendor เกี่ยวกับค่า Tg (Glass Transition Temperature) และ Td (Decomposition Temperature) ของวัสดุ

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **ビルドアップ (Birudo appu):** Build-up (HDI process)
- **ブラインドビア (Buraindo bia):** Blind via
- **ベリードビア (Berīdo bia):** Buried via
- **スタガービア (Sutagā bia):** Staggered via - บิดเยื้องกัน
- **スタックビア (Sutakku bia):** Stacked via - วางซ้อนกันตรงๆ

## ควิซท้ายบท (Quiz)
**Q:** สาเหตุหลักที่ IPC และผู้เชี่ยวชาญหลายแห่งแนะนำให้ใช้ Staggered Microvia มากกว่า Stacked Microvia คืออะไร?
1. ลดค่าใช้จ่ายในการเจาะด้วยเลเซอร์
2. ลดปัญหาทางความน่าเชื่อถือ (Reliability) จากความเค้นช่วงขยายตัวทางความร้อน
3. ช่วยลด Signal crosstalk ได้ดีกว่า
**Ans:** 2. ลดปัญหาทางความน่าเชื่อถือ (Reliability) จากความเค้นช่วงขยายตัวทางความร้อน
