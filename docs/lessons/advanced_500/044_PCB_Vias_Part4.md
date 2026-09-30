# Lesson 44: HDI, Microvias, and Reliability

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
HDI (High Density Interconnect) อาศัย Microvias ที่เจาะด้วย Laser (Laser Drilled) ซึ่งปกติจะมีความลึกเพียง 1 ชั้น (เช่น L1 ไป L2) ขนาดรูเจาะประมาณ 3-6 mils (75-150 $\mu$m) หากต้องการเชื่อมต่อหลายชั้น จะต้องใช้เทคนิค Staggered Vias หรือ Stacked Vias ในด้าน Reliability การทำ Stacked Vias หลายชั้น (มากกว่า 2-3 ชั้น) มีความเสี่ยงสูงที่จะเกิดรอยแตก (Crack) บริเวณรอยต่อทองแดงระหว่างชั้น (Target Pad) เมื่อผ่านการทดสอบ Thermal Cycling เนื่องจาก CTE (Coefficient of Thermal Expansion) ที่ต่างกันของ Z-axis

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick:** หากไม่มีข้อจำกัดเรื่องพื้นที่จริงๆ พยายามบังคับให้ Layout Engineer ใช้ Staggered Microvias แทน Stacked Microvias เสมอ เพราะผลิตง่ายกว่า (Yield สูงกว่า) และลดความเสี่ยงจากการแตกหักเมื่อเจอความร้อน (Reliability ดีกว่า)
- **Design Review Check:** ตรวจสอบโครงสร้าง Stack-up ว่าเป็นแบบ 1+N+1 หรือ 2+N+2 และเช็ค Aspect Ratio ของ Microvia ว่าไม่ควรเกิน 0.8:1 หรือ 1:1 ตามความสามารถของโรงงาน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **マイクロビア (Maikurobia):** Microvia
- **スタガードビア (Sutagādo bia):** Staggered Via (ビアずらし)
- **スタックビア (Sutakku bia):** Stacked Via (段積みビア)
- **熱膨張係数 (Netsubōchō keisū):** CTE (Coefficient of Thermal Expansion)
- **信頼性試験 (Shinraisei shiken):** Reliability Testing

## ควิซท้ายบท (Quiz)
**Q1:** ในการออกแบบ HDI Board การเลือกใช้ Staggered Microvias เมื่อเทียบกับ Stacked Microvias มีข้อดีหลักคืออะไร?
1. ใช้พื้นที่น้อยกว่า (Higher Density)
2. มีค่า Impedance ต่ำกว่า
3. ความน่าเชื่อถือ (Reliability) สูงกว่าและผลิตง่ายกว่า
4. สามารถเชื่อมต่อกระแสไฟฟ้าได้มากกว่าถึง 2 เท่า
*(เฉลย: 3)*
