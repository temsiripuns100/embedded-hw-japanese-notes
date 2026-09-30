# Lesson 90: PCB DFM Part 10 - PCBA Yield Optimization & DFT (Design for Test)

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
PCBA Yield ขึ้นอยู่กับทั้ง Design for Manufacturing (DFM) และ Design for Test (DFT) การเพิ่ม Test Coverage ผ่าน In-Circuit Test (ICT) หรือ Flying Probe Test จำเป็นต้องมี Test Point (TP) ที่เพียงพอ ทฤษฎีการจัดวาง Test Point ควรมีอย่างน้อย 1 TP ต่อ 1 Net (ถ้าทำได้) และควรวางไว้ด้าน Bottom (Solder Side) เป็นหลัก เพื่อให้ง่ายต่อการทำ Fixture การพิจารณาเรื่อง Clearance ระหว่าง Test Point กับอุปกรณ์อื่นๆ ต้องมีระยะเพียงพอไม่ให้เข็มทดสอบ (Probe) ไปชนกับ Component (Probing Clearance) รวมถึงขนาดของ Test Pad มักแนะนำที่ 0.8mm - 1.0mm (30-40 mil)

## ทริคหน้างาน OJT (OJT Practical Tricks)
- อย่าวาง Test Point บนรอยต่อบัดกรี (Solder Joint) หรือ Component Pad เด็ดขาด เพราะแรงกดจากเข็ม Probe อาจทำให้ตะกั่วร้าวหรืออุปกรณ์เสียหาย
- ถ้าระบบใช้ Flying Probe Test สามารถใช้ Test Pad ขนาดเล็กได้ (เช่น 0.4mm) แต่ถ้าใช้ Bed of Nails (ICT Fixture) ต้องใหญ่กว่านั้นและควรอยู่ฝั่งเดียวกันให้มากที่สุดเพื่อประหยัดค่าทำ Jig
- การออกแบบ Panel (シート割り - Sheet-wari) ต้องเผื่อ Breakaway tab (ミシン目 - V-cut หรือ Mouse Bites) ให้เหมาะสม เพื่อไม่ให้วงจรหรืออุปกรณ์ที่อยู่ริมขอบพังตอนหักบอร์ด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **テストポイント (Tesuto Pointo) / 検査用パッド (Kensayou Paddo):** Test Point (จุดทดสอบ)
- **実装利回り (Jissou Rimawari) / 歩留まり (Budomari):** PCBA Yield (ผลผลิต/อัตราส่วนของดี)
- **面付け (Mentsuke) / シート割り (Shiitowari):** Panelization (การจัดเรียงบอร์ดใน Panel)
- **治具 (Jigu):** Jig / Fixture (อุปกรณ์จับยึด/ทดสอบ)
- **ミシン目 (Mishin-me):** Mouse Bites / Perforation holes (รอยปรุสำหรับหักบอร์ด)

## ควิซท้ายบท (Quiz)
**คำถาม:** ในการทำ DFT (Design for Test) เพื่อวัดด้วย ICT Fixture (Bed of Nails) เพราะเหตุใดจึงควรวาง Test Point ไว้ที่ด้านล่าง (Bottom side) ทั้งหมดถ้าเป็นไปได้?
**เฉลย:** เพื่อให้การออกแบบและสร้าง治具 (Jig/Fixture) ทำได้ง่ายและมีราคาถูกกว่าการต้องสร้าง Fixture แบบประกบสองด้าน (Top & Bottom Probing) ซึ่งซับซ้อนและมีโอกาสผิดพลาดสูงกว่า
