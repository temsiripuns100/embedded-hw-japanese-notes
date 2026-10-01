# Lesson 050: PCB Vias Part 10 - Via Reliability and Thermal Cycling

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
Via ต้องทนต่อความเค้นทางความร้อน (Thermal Stress) จากกระบวนการประกอบ (Reflow, Wave soldering) และสภาพแวดล้อม (Thermal Cycling) ค่า CTE (Coefficient of Thermal Expansion) ของ Z-axis ของ FR4 สูงกว่าทองแดงมาก ทำให้เมื่อร้อน FR4 จะยืดตัวดึงผนังรู Via (Barrel) จนอาจเกิด Barrel Crack หรือ Corner Crack ระหว่าง Pad กับ Barrel การใช้ Copper plating ที่หนาขึ้น หรือวัสดุ High-Tg สามารถบรรเทาปัญหานี้ได้

## ทริคหน้างาน OJT
ในการวิเคราะห์ Failure Analysis (FA) หากเจอ Open circuit ที่อุณหภูมิสูงแต่ปกติตอนอุณหภูมิห้อง ให้สงสัย Barrel crack ก่อนเลย ต้องนำไปทำ Cross-section ดูรอยร้าว

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図)
- **熱膨張係数 (Netsubouchou Keisuu):** CTE (Coefficient of Thermal Expansion)
- **バレルクラック (Bareru Kurakku):** Barrel Crack
- **断面観察 (Danmen Kansatsu):** Cross-section observation

## ควิซท้ายบท
Q: กลไกใดทำให้เกิด Barrel Crack ใน Via?
A: ความแตกต่างของอัตราการขยายตัวทางความร้อน (CTE) ระหว่างเนื้อ FR4 (Z-axis) กับทองแดงเคลือบรู
