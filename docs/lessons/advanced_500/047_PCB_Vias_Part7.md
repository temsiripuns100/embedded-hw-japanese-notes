# Lesson 47: Via-in-Pad Plated Over (VIPPO / POFV)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เทคโนโลยี Via-in-Pad (VIP) เป็นที่นิยมใน BGA ที่มี I/O หนาแน่น แต่ถ้าใช้ Via ธรรมดาบน Pad จะทำให้เกิดปัญหาตะกั่วไหลลงรู (Solder Wicking) ซึ่งนำไปสู่การเชื่อมต่อที่ไม่สมบูรณ์ (Open circuit)
กระบวนการ **Plated Over Filled Via (POFV)** หรือ VIPPO จะประกอบด้วย:
1. เจาะรู Via
2. ชุบทองแดงในรู (Through-hole plating)
3. อุดรูด้วยเรซิน (Epoxy Resin Plugging)
4. อบให้แข็ง (Curing) และขัดให้เรียบ (Planarization/Flattening)
5. ชุบทองแดงปิดทับ (Overplating) (Cap Plating)
ผลลัพธ์คือ Pad ที่เรียบสนิทเสมือนไม่มีรูเจาะเลย

## ทริคหน้างาน OJT (現場のコツ)
- **Dimple Requirement:** เวลา 검図 (Kenzu) ต้องดูสเปกของโรงงาน (Fab) ในเรื่อง "Dimple" หรือรอยบุ๋มบน VIPPO ค่า Dimple ที่ยอมรับได้มักจะไม่เกิน 15 ไมครอน (µm) หากบุ๋มลึกกว่านี้ เวลาวาง BGA จะเกิดฟองอากาศ (Solder Voiding) ในตะกั่วบัดกรี ทำให้ความแข็งแรงทางกล (Mechanical Strength) ลดลง
- **Outgassing Issues:** ถ้ายาง/เรซินที่ใช้อุด (Plugging resin) อบไม่แห้งสนิท เมื่อผ่านความร้อนจาก Reflow oven จะเกิดก๊าซดันออกมา (Outgassing) ทำให้แผ่นทองแดงที่ปิดทับไว้บวม (Pad cratering/blistering)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **穴埋めビア (Ana-ume Via / Filled Via):** Via ที่ถูกอุด
- **樹脂埋め (Jushi-ume / Resin Plugging):** การอุดด้วยเรซิน
- **平坦化 (Heitanka / Planarization):** การทำให้ผิวเรียบเสมอกัน
- **ボイド (Boido / Void):** โพรงอากาศ หรือฟองอากาศในจุดบัดกรี
- **実装不良 (Jissou Furyou / Assembly Defect):** ข้อบกพร่องในกระบวนการประกอบ (SMT)
- **蓋めっき (Futa Mekki / Cap Plating):** การชุบทองแดงปิดปากรู

## ควิซท้ายบท (Quiz)
**Q:** สาเหตุหลักที่ทำให้เกิด Solder Voiding บน Pad ที่ใช้เทคโนโลยี VIPPO คืออะไร?
1. ขบวนการ Planarization ไม่ดีพอ ทำให้เกิด Dimple ลึกเกินไป
2. อุณหภูมิ Reflow ต่ำเกินไป
3. การใช้ตะกั่วแบบ Lead-free
4. ขนาดของ BGA ใหญ่เกินไป

*(คำตอบที่ถูกต้อง: 1. ขบวนการ Planarization ไม่ดีพอ ทำให้เกิด Dimple ลึกเกินไป ส่งผลให้กักเก็บอากาศไว้ภายใน)*
