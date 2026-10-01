# Lesson 049: PCB Vias Part 9 - Via in Pad (VIP) and Microvias (HDI)

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
เทคโนโลยี HDI (High-Density Interconnect) บังคับให้ใช้ Via in Pad เพื่อลด Inductance และประหยัดพื้นที่ โดยใช้ Microvia เจาะด้วยเลเซอร์ (Laser drilled) ขนาดเล็ก การทำ VIP ต้องมีกระบวนการ Via Filling (Plated Over Filled Via - POFV) ไม่เช่นนั้น Solder paste จะไหลลงไปในรูระหว่าง Reflow ทำให้จุดบัดกรีขาดตะกั่ว (Solder wicking) เกิด Void หรือเปิดวงจร

## ทริคหน้างาน OJT
ถ้าใช้ VIP บน BGA Pad ห้ามลืมระบุใน Fab Note ว่า "Via in Pad Plated Over (VIPPO) with Epoxy Fill" ไม่งั้นโรงงานอาจจะแค่ Tenting ซึ่งพังแน่นอนตอนประกอบ

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図)
- **パッドオンビア (Paddo-on-bia):** Via in Pad
- **樹脂埋め (Jushi Ume):** Resin Filling / Epoxy Fill
- **はんだ吸い込み (Handa Suikomi):** Solder Wicking (ตะกั่วไหลลงรู)

## ควิซท้ายบท
Q: ปัญหาหลักหากทำ Via in Pad โดยไม่ทำ Epoxy Fill คืออะไร?
A: Solder wicking ทำให้ปริมาณตะกั่วที่ pad ไม่พอ เกิดการบัดกรีที่ไม่สมบูรณ์
