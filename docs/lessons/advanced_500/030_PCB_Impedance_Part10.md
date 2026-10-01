# Advanced PCB Impedance Part 10: Manufacturing Tolerance & Coupons (製造公差とテストクーポン)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
แม้โปรแกรมจำลอง (Simulation) จะแม่นยำแค่ไหน แต่ความจริงในกระบวนการผลิต PCB (เช่น Over-etching, Resin flow, Dielectric tolerance) จะทำให้ Impedance คลาดเคลื่อนไปจากอุดมคติ ±10% เป็นมาตรฐานอุตสาหกรรม
เพื่อการันตีคุณภาพ Vendor จะสร้าง "Impedance Coupon" ไว้ที่ขอบของ Panel การผลิต (Panel edge) ซึ่งเป็นแบบจำลองของเส้นสัญญาณจริงในบอร์ด เมื่อผลิตเสร็จ Vendor จะเอาเครื่อง TDR มาวัดค่าจาก Coupon นี้ การออกแบบคูปองที่ดี ต้องมี Pitch, Trace width, Spacing, และแวดล้อมที่สะท้อน "Worst-case scenario" หรือเทียบเท่าโครงสร้างในบอร์ดจริงๆ ให้ได้มากที่สุด 

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- เมื่อได้รับเอกสาร TDR Report จากโรงงาน ให้ตรวจสอบเสมอว่าโรงงานไม่ได้แอบไปแก้ไข Trace width หรือ Spacing ของเรามากเกินไป (ที่เรียกว่า Line width compensation) จนผิดจากกฎ Design Rule ที่เราเผื่อ Crosstalk ไว้ หากโรงงานปรับเกิน ±1 mil ให้ตั้งคำถามกับ Stackup ที่ตกลงกันไว้
- บางโรงงานสร้าง Coupon ให้ได้ Impedance สวยงาม แต่ในบอร์ดจริงกลับมีปัญหาสัญญาณ (เช่น Copper thieving กวน) ต้องทำความเข้าใจและเช็ค DFM ร่วมกับโรงงานอย่างเคร่งครัด 

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **テストクーポン (Tesuto kūpon):** Test coupon
- **公差 (Kōsa):** Tolerance
- **エッチング過剰 (Etchingu kajō):** Over-etching
- **線幅補正 (Senhaba hosei):** Line width compensation / Trace adjust
- **検査成績書 (Kensa seisekisho):** Inspection report / TDR report

## ควิซท้ายบท (Quiz)
**Q:** ทำไมจึงต้องใช้ Test Coupon ในการวัด Impedance แทนที่จะวัดจาก Trace บนบอร์ดโดยตรง?
1. เพราะ Trace บนบอร์ดจริงมักสั้นเกินไปและมีจุดต่อเข้าชิป ทำให้วัดด้วย TDR ลำบากและไม่แม่นยำ
2. เพื่อปกปิดความผิดพลาดของโรงงาน
3. เพราะบอร์ดจริงไม่มี Ground plane
**Ans:** 1. เพราะ Trace บนบอร์ดจริงมักสั้นเกินไปและมีจุดต่อเข้าชิป ทำให้วัดด้วย TDR ลำบากและไม่แม่นยำ
