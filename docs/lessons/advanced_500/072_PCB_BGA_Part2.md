# Lesson 072: BGA Escape Routing (Fanout)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Escape Routing (หรือ Fanout) คือการลากเส้นสัญญาณออกจากใต้ตัวถัง BGA เพื่อไปเชื่อมต่อกับส่วนอื่นของวงจร
- **Dog-bone Fanout**: ใช้สำหรับ BGA ที่มี pitch กว้าง (>0.5mm) โดยลากเส้นสั้นๆ ไปยัง Via ที่อยู่ข้างๆ Pad
- **Via-in-Pad (VIP)**: ใช้สำหรับ Fine-pitch BGA (<0.5mm) โดยเจาะ Via ลงไปตรงกลาง Pad เลย ข้อดีคือประหยัดพื้นที่และลด Inductance แต่ต้องผ่านกระบวนการ Via Filling (Plated Over Filled Via - POFV) เพื่อป้องกันไม่ให้ตะกั่วไหลลงไปในรู (Solder wicking) ซึ่งจะทำให้เกิด Void ในรอยเชื่อม

## ทริคหน้างาน OJT (OJT Field Tricks)
- การทำ Via-in-Pad มีต้นทุนการผลิตสูงขึ้น 15-20% ควรคุยกับทีมจัดซื้อและโรงงานผลิต (Fab) ก่อนเลือกใช้
- การลากสายสัญญาณออกจาก BGA ต้องคำนึงถึง Layer Stackup ควรแบ่ง Layer ให้สัญญาณความเร็วสูง (High-speed signals) อยู่ติดกับ Reference Plane (GND) ทันทีเพื่อคุม Impedance

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **引き出し線 (Hikidashisen)** - Escape routing / Fanout
- **ビアインパッド (Bia in Paddo)** - Via-in-Pad
- **穴埋め (Ana ume)** - Via filling / Plugging
- **層構成 (Sō kōsei)** - Layer Stackup
- **ボイド (Boido)** - Void (ฟองอากาศในตะกั่ว)

## ควิซท้ายบท (Quiz)
**คำถาม:** ปัญหาหลักที่จะเกิดขึ้นหากทำ Via-in-Pad แต่ไม่ได้สั่งโรงงานทำ Via Filling คืออะไร?
<details>
<summary>ดูเฉลย</summary>
**คำตอบ:** Solder Wicking (ตะกั่วบัดกรีไหลลงไปในรู Via) ทำให้ปริมาณตะกั่วบน Pad ไม่พอ เกิดปัญหารอยเชื่อมไม่สมบูรณ์ (Open joint) หรือมี Void ปริมาณมาก
</details>
