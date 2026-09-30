# Lesson 48: Thermal Vias & Thermal Management (サーマルビアと熱設計)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในวงจร Power Electronics หรือ RF Power Amplifier การระบายความร้อนจาก Die ลงสู่ Ground Plane ภายใน PCB เป็นหัวใจสำคัญในการยืดอายุการใช้งาน Thermal Vias เป็นกลไกหลักในการลดความต้านทานความร้อน (Thermal Resistance - $\theta_{JC}$ และ $\theta_{CA}$) 
- **Thermal Resistance Equation:** ความต้านทานความร้อนของ Via แปรผกผันกับพื้นที่หน้าตัดของทองแดงที่ชุบในรู การเพิ่มจำนวนรู Thermal Vias เล็กๆ หลายๆ รู (Array) มีประสิทธิภาพในการกระจายความร้อนได้ดีกว่าการใช้รูใหญ่เพียงรูเดียว เพราะเส้นรอบวงรวม (Total Circumference) ที่ชุบทองแดงมีมากกว่า

## ทริคหน้างาน OJT (現場のコツ)
- **Solder Wicking on Thermal Pads:** หลายคนออกแบบ Thermal Via ใต้ QFN (Quad Flat No-leads) เป็นแบบ Through-hole ธรรมดา เวลาผลิต ตะกั่วบัดกรี (Solder paste) จะไหลลงไปตามรู (Wicking) ทำให้ QFN ลอย หรือเกิดช็อตด้านล่าง วิธีแก้คือ:
  1. ใช้เทคนิค Tenting จากด้านล่าง (Bottom side)
  2. การออกแบบ Metal Mask (Stencil) ให้เป็นลวดลาย "Windowpane" เพื่อลดปริมาณ Solder paste ลงเหลือ 50-70% ป้องกันปริมาณตะกั่วมากเกินไป
- **Thermal Relief vs Solid Connection:** สำหรับ Ground pad ที่ต้องการระบายความร้อน ห้ามใช้ Thermal relief (Spoke connection) เด็ดขาด ให้ต่อแบบ Solid/Direct connect ลง Plane ทันที (ベタ接続 - Beta Setsuzoku) เพื่อให้ความร้อนและกระแสไหลได้เต็มที่

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **サーマルビア (Saamaru Bia / Thermal Via):** รูผ่านสำหรับระบายความร้อน
- **放熱 (Hounetsu / Heat Dissipation):** การระบายความร้อน
- **熱抵抗 (Netsuteikou / Thermal Resistance):** ความต้านทานความร้อน
- **はんだ吸い上がり (Handa Sui-agari / Solder Wicking):** การไหลของตะกั่วลงรู
- **メタルマスク (Metaru Masuku / Metal Mask/Stencil):** แผ่นสเตนซิลสำหรับปาดตะกั่ว
- **ベタ接続 (Beta Setsuzoku / Solid Connection):** การต่อทองแดงแบบเต็มแผ่น (ไม่ทำลวดลายกากบาท)

## ควิซท้ายบท (Quiz)
**Q:** เพื่อหลีกเลี่ยงปัญหาตะกั่วไหลลงรู Thermal Vias ใต้ตัวถัง QFN ระหว่างกระบวนการ SMT ควรทำอย่างไรในขั้นตอนการทำ Stencil?
1. พิมพ์ Solder paste ให้เต็ม 100% ของพื้นที่ Thermal pad
2. ออกแบบ Stencil ให้เป็นรูปแบบ Windowpane (ตารางหมากรุก) เพื่อจำกัดปริมาณตะกั่วให้อยู่ที่ประมาณ 50-70%
3. ไม่ต้องปาด Solder paste ตรงกลางเลย
4. ใช้ขนาดรู Stencil ให้ใหญ่กว่า Pad 20%

*(คำตอบที่ถูกต้อง: 2. ออกแบบ Stencil ให้เป็นรูปแบบ Windowpane เพื่อจำกัดปริมาณตะกั่วและเว้นพื้นที่ให้อากาศ/ก๊าซระบายออก)*
