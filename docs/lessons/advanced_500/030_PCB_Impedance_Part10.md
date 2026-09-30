# Lesson 030: PCB Impedance Part 10 - Manufacturing Tolerances and TDR Measurements

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Impedance ที่คำนวณในโปรแกรม (เช่น Polar SI9000) เป็นเพียงค่าทางทฤษฎี ในการผลิตจริง PCB Fabrication จะมีความคลาดเคลื่อน (Tolerance) โดยทั่วไปอยู่ที่ $\pm 10\%$ ปัจจัยหลักที่ทำให้ค่า Impedance เปลี่ยนคือ:
1. **Trace Width ($W$)**: การกัดกรด (Etching) ทำให้เส้นเล็กลง หรือเกิดเป็นรูปคางหมู (Trapezoidal shape)
2. **Dielectric Thickness ($H$)**: การอัด Prepreg (Pressing) อาจทำให้ความหนาเปลี่ยน ขึ้นอยู่กับปริมาณทองแดง (Resin starvation)
3. **Dielectric Constant ($\epsilon_r$)**: วัสดุผสมมีค่าไม่คงที่ตามแต่ละ Lot
เพื่อวัดค่าที่แท้จริง เราใช้เครื่องมือที่เรียกว่า **TDR (Time Domain Reflectometry)** ซึ่งจะส่ง Pulse ลงไปแล้ววัดสัญญาณที่สะท้อนกลับมา (Reflection) ตามแกนเวลา ทำให้รู้ได้ว่า Impedance เปลี่ยนแปลงไปตรงจุดไหนของบอร์ดบ้าง (Spatial resolution)

## 2. ทริคหน้างาน OJT (On-the-Job Training Tips)
- **Senior Tip:** เวลาสั่งผลิตบอร์ดที่มี Controlled Impedance ต้องส่ง "Impedance Profile" หรือตารางให้โรงงานเสมอ และบอกให้โรงงาน "ปรับแก้ความกว้างเส้น (Trace width) เล็กน้อยได้" เพื่อให้ได้ Impedance ตามเป้า (โรงงานเขาจะคำนวณด้วย Stackup จริงของเขา)
- ขอ **TDR Report** และ **Test Coupon** จากโรงงานเสมอ เพื่อใช้ยืนยันว่าบอร์ดที่ได้มาตรงตามสเปคจริงๆ

## 3. คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **公差 (Kōsa):** Tolerance (ค่าความเผื่อ/ความคลาดเคลื่อน)
- **エッチング残渣 (Etchingu zansa):** Etching Residue/Undercut (ร่องรอย/การกัดกรดไม่หมดหรือเกิน)
- **テストクーポン (Tesuto kūpon):** Test Coupon (ชิ้นส่วนบอร์ดที่ยื่นออกมาเพื่อใช้วัด TDR)
- **インピーダンス測定 (Inpīdansu sokutei):** Impedance Measurement
- **仕上がり厚 (Shiagari atsu):** Final Thickness (ความหนาหลังกระบวนการอัด Press)

## 4. ควิซท้ายบท (End-of-chapter Quiz)
**Q:** ในกราฟ TDR หากเห็นค่า Impedance พุ่งสูงขึ้น (Spike ขึ้น) บริเวณที่เป็น Connector มักหมายความว่าอย่างไร?
**A:** การที่ Impedance พุ่งสูงขึ้น (Spike) แสดงว่าบริเวณนั้นมีลักษณะเป็น Inductive (Inductance สูงเกินไปเมื่อเทียบกับ Capacitance) ซึ่งมักเกิดจาก Pin ของ Connector หรือสายสัญญาณที่ลอยตัวสูงขึ้นจาก Reference plane (GND) ขาด Return path ที่ดี วิธีแก้คืออาจต้องเพิ่มการเชื่อมต่อ GND บริเวณรอบๆ Connector ให้มากขึ้น
