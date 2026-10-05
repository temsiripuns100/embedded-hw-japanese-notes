# 095 - PCB DFA Part 5: Inspection, Testing, and Yield Optimization

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การออกแบบเพื่อการทดสอบ (Design for Testability - DFT) เป็นส่วนหนึ่งที่แยกไม่ออกจาก DFA บอร์ดที่ประกอบเสร็จต้องสามารถตรวจสอบได้ง่าย ไม่ว่าจะเป็นด้วย AOI (Automated Optical Inspection), AXI (Automated X-ray Inspection) หรือ ICT (In-Circuit Testing)
การจัดเตรียม Test Point สำหรับสัญญาณสำคัญ (Power, Ground, Communication Buses) ต้องคำนึงถึงขนาดของ Probe (เช่น 0.8mm หรือ 1.0mm) และระยะห่างระหว่าง Test Point เพื่อไม่ให้ Probe ช็อตกัน นอกจากนี้ การวาง Test Point ควรอยู่ฝั่งเดียวกัน (มักเป็น Bottom side) เพื่อลดความซับซ้อนของ Test Fixture (Jig)

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Test Point on Vias:** การทำ Test Point บน Via สามารถทำได้ แต่ต้องไม่เอา Solder Mask มาคลุม (Tent) และต้องระวังการใช้ Probe แบบแหลม (Crown or Spear) ทิ่มลงไปในรู Via ซึ่งอาจทำให้ผนังทองแดงเสียหายได้ ควรใช้ Via ที่มีการเติมเต็ม (Plugged/Capped) หรือใช้ Test Pad แยกออกมา
- **AOI Blind Spots:** อุปกรณ์ที่มีตัวถังสูงๆ อาจบังจุดบัดกรีของอุปกรณ์ตัวเตี้ย ทำให้กล้อง AOI มองไม่เห็น (Shadowing) ต้องระวังในการจัดวางอุปกรณ์สูงๆ ให้อยู่ห่างจากชิ้นส่วนสำคัญ

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図用語 - Kenzu Yōgo)
- **検査 (Kensa):** Inspection, Testing / การตรวจสอบ, การทดสอบ
- **テストパッド (Tesuto Paddo):** Test Point, Test Pad / จุดทดสอบบนบอร์ด
- **検査治具 (Kensa Jigu):** Test Fixture, Jig / จิ๊กทดสอบ
- **歩留まり (Budomari):** Yield rate / อัตราผลตอบแทนหรือสัดส่วนของดีในสายการผลิต
- **X線検査 (Ekkusu-sen Kensa):** X-ray Inspection / การตรวจด้วยรังสีเอ็กซ์ (ใช้กับ BGA)

## ควิซท้ายบท (Quiz)
1. ทำไมเราจึงควรหลีกเลี่ยงการวาง Test Point ไว้ทั้งสองด้านของบอร์ด (Top และ Bottom)?
2. สำหรับอุปกรณ์ประเภท BGA ทำไม AOI ถึงไม่เพียงพอ และต้องใช้ AXI (X-ray) แทน?
