# Lesson 46: Advanced Microvias & HDI Technology (レーザービアと高密度配線板)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior Engineer การออกแบบ High Density Interconnect (HDI) เป็นสิ่งหลีกเลี่ยงไม่ได้เมื่อต้องทำงานกับ BGA ที่มี pitch ต่ำกว่า 0.65mm การใช้ Microvias (レーザービア) มีข้อจำกัดที่อิงตามหลักฟิสิกส์ของการเจาะด้วยแสงเลเซอร์ (Laser Drilling) 
- **Aspect Ratio Limit:** สำหรับ Microvia อัตราส่วนความลึกต่อเส้นผ่านศูนย์กลาง (Aspect Ratio) มักจะถูกจำกัดไว้ที่ไม่เกิน 0.8:1 ถึง 1:1 เนื่องจากการชุบทองแดง (Plating) ลงไปในรูที่มีก้นตัน (Blind) จะเกิดปัญหาโยนตัวของกระแสไฟฟ้า (Current density) ทำให้การเคลือบทองแดงไม่สม่ำเสมอ
- **Staggered vs Stacked Microvias:** การวาง Microvias แบบเยื้องกัน (Staggered) ให้ yield ที่ดีกว่าและทนต่อความเครียดทางความร้อน (Thermal Stress) ได้ดีกว่าแบบทับซ้อนกัน (Stacked)

## ทริคหน้างาน OJT (現場のコツ)
- **Stacked Via Reliability:** หากจำเป็นต้องใช้ Stacked Microvias เกิน 2 ชั้น (เช่น 3-n-3) ให้ระวังปัญหาในกระบวนการ Reflow เพราะทองแดงที่มีค่า CTE (Coefficient of Thermal Expansion) ต่างจาก FR4 จะเกิด Z-axis expansion ทำให้ก้น Microvia ร้าว (Barrel Cracking) หรือเกิดรอยแยกที่จุดเชื่อมต่อ (Target Pad Separation) แนะนำให้ปรึกษาโรงงาน (Fab) ก่อนว่ามี Capability ในการทำ Any-Layer HDI หรือควรใช้ Staggered
- **Capture Pad Sizing:** ควรเผื่อขนาด Capture Pad อย่างน้อย +4 mil (+100um) จากขนาดของ Drill size เพื่อรองรับ Registration Tolerance

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **レーザービア (Laser Via):** Microvia ที่ใช้เลเซอร์เจาะ
- **ビアスタック (Via Stack):** การวาง Via ทับกัน
- **アスペクト比 (Aspect Ratio):** อัตราส่วนรูเจาะ
- **熱膨張係数 (Netsubouchou Keisuu / CTE):** สัมประสิทธิ์การขยายตัวทางความร้อน
- **層間剥離 (Soukan Hakuri / Delamination):** การลอกร่อนระหว่างชั้นของ PCB
- **検図 (Kenzu):** การตรวจสอบ Design (Design Review)

## ควิซท้ายบท (Quiz)
**Q:** การใช้ Stacked Microvias มีความเสี่ยงต่อการเกิดความล้มเหลว (Failure) รูปแบบใดมากที่สุดระหว่างการผ่านกระบวนการ Reflow?
1. Impedance Mismatch
2. Target Pad Separation (Microvia crack)
3. Solder Bridging
4. Crosstalk

*(คำตอบที่ถูกต้อง: 2. Target Pad Separation เนื่องจากการขยายตัวตามแนวแกน Z ของวัสดุ PCB)*
