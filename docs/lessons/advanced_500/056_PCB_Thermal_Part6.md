# บทที่ 56: การออกแบบ Thermal Vias และ Heat Dissipation Pads (Thermal Vias & Pad Design)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในระดับ Senior Engineer การทำ Thermal Vias ไม่ใช่แค่การเจาะรูรอบๆ ขา IC แต่คือการคำนวณ Thermal Resistance (θ) เพื่อหาความต้านทานความร้อนรวมที่เกิดขึ้น
Thermal Vias ช่วยนำความร้อนจากชั้นผิว (Top layer) ไปยังระนาบกราวด์ (Ground plane) หรือระนาบทองแดงภายในที่ทำหน้าที่เป็น Heat spreader 
สมการพื้นฐาน: $R_{thermal} = \frac{L}{k \cdot A}$
- **L**: ความยาวของ Via (ความหนาของบอร์ด)
- **k**: ค่าการนำความร้อนของทองแดง (Thermal Conductivity) ~385 W/m·K
- **A**: พื้นที่หน้าตัดของทองแดงที่ใช้ชุบ (Plated copper cross-sectional area)

การเจาะรู Via ถี่เกินไปอาจทำให้โครงสร้างบอร์ดอ่อนแอลง และเกิดปัญหา "Solder Wicking" ในระหว่างขั้นตอน Reflow 

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Tenting vs Capping vs Filling**: หากคุณวาง Vias ใต้ Thermal Pad ของ QFN หรือ DPAK ห้ามเปิดผิวโล่งโล่ง (Uncapped/Unfilled) อย่างเด็ดขาด เพราะตะกั่วบัดกรีจะไหลลงไปตามรู (Solder Wicking) ทำให้ IC เอียง หรือระบายความร้อนได้ไม่ดี ต้องระบุให้โรงงานทำ **Via In Pad Plated Over (VIPPO)** หรือใช้ Epoxy fill
- **Via Pitch & Size**: ขนาดที่เหมาะสมคือ Drill 0.2 - 0.3 mm และ Pitch ห่างกันประมาณ 1.0 - 1.2 mm การทำเล็กกว่านี้ราคาบอร์ดจะพุ่งกระฉูดโดยที่ประสิทธิภาพแทบไม่ต่างกัน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **サーマルビア (Saamaru Bia)**: Thermal Via (รูระบายความร้อน)
- **はんだ吸い上がり (Handa Suiagari)**: Solder Wicking (ตะกั่วไหลลงรู)
- **穴埋め (Anaume)**: Via Filling (การอุดรู)
- **放熱パッド (Hounetsu Paddo)**: Heat dissipation pad

## ควิซท้ายบท (End of Chapter Quiz)
**Q: หากโรงงาน PCB เสนอให้ใช้ Tenting Via ใต้ Thermal Pad ของ IC แบบ QFN คุณในฐานะ Senior Engineer ควรตอบอย่างไร?**
1. ตกลง เพราะราคาถูกที่สุด
2. ปฏิเสธ และขอให้ทำ VIPPO (Via In Pad Plated Over) แทนเพื่อป้องกันตะกั่วไหล
3. ตกลง แต่ต้องเพิ่มขนาดรูให้ใหญ่ขึ้น
4. ปฏิเสธ และให้ลบ Via ทิ้งทั้งหมด

*เฉลย: 2. ปฏิเสธ และขอให้ทำ VIPPO เพราะ Tenting ไม่เพียงพอที่จะกัน Solder Wicking ใต้ชิ้นส่วนที่มี Thermal pad.*
