# Advanced PCB Stackup Part 2: Symmetrical Stackup & Warpage Prevention (対称スタックアップと反り防止)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
การออกแบบ Stackup ที่ดีต้องมีความสมมาตร (Symmetry) รอบแกนกลาง (Z-axis center) เสมอ เพื่อลดความเค้นตกค้าง (Residual Stress) ที่เกิดจากสัมประสิทธิ์การขยายตัวทางความร้อน (CTE - Coefficient of Thermal Expansion) ที่ต่างกันระหว่างชั้นเรซินและทองแดง หาก Stackup ไม่สมมาตร เมื่อผ่านกระบวนการ Reflow (ที่มีอุณหภูมิสูงกว่า 240°C สำหรับ Lead-free) บอร์ดจะเกิดอาการโค้งงอ (Warpage) ซึ่งส่งผลร้ายแรงต่อการประกอบ BGA (Ball Grid Array) ที่มีระยะ Pitch ต่ำกว่า 0.8mm ทำให้เกิด Open/Short joints

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- การเช็คความสมมาตรไม่ใช่แค่จำนวนชั้น หรือชนิดของ Prepreg/Core แต่ต้องคำนึงถึง **Copper Retention (อัตราส่วนพื้นที่ทองแดง)** ในแต่ละชั้นด้วย หาก Layer 2 เป็น Ground plane ทึบ (90% copper) Layer N-1 ก็ควรมีเปอร์เซ็นต์ทองแดงที่ใกล้เคียงกัน (เช่น การทำ Copper Pour หรือ Thieving/Hatching) เพื่อบาลานซ์ความเค้น
- ค่า Warpage ที่ยอมรับได้สำหรับ BGA pitch เล็ก มักจะต้อง < 0.75% ตามมาตรฐาน IPC-A-600

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **反り (Sori):** Warpage / Bow - การโก่งตัว
- **ねじれ (Nejire):** Twist - การบิดตัว
- **対称性 (Taishōsei):** Symmetry - ความสมมาตร
- **残銅率 (Zandōritsu):** Copper retention rate - อัตราส่วนพื้นที่ทองแดงที่เหลืออยู่

## ควิซท้ายบท (Quiz)
**Q:** หาก Layer 3 มี Copper Retention 85% และ Layer 8 มี Copper Retention 20% ในบอร์ด 10 Layers สิ่งใดมีโอกาสเกิดขึ้นมากที่สุดหลังผ่าน Reflow?
1. Impedance mismatch
2. บอร์ดเกิดอาการ Bow & Twist (Warpage)
3. Delamination
**Ans:** 2. บอร์ดเกิดอาการ Bow & Twist (Warpage)
