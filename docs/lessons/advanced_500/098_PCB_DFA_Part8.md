# PCB DFA Part 8: Testability (DFT integration with DFA) & ICT/FCT

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Design for Testability (DFT) เป็นส่วนหนึ่งที่แยกไม่ออกจากการทำ DFA. หากประกอบบอร์ดเสร็จแล้วแต่ทดสอบ (Test) ไม่ได้ หรือ Test Coverage ต่ำ บอร์ดนั้นก็ถือว่าไม่สมบูรณ์
- **In-Circuit Test (ICT):** ต้องการ Test Point สำหรับทุุก Net (Node) ข้อกำหนดสำคัญคือ Test Point ต้องอยู่ฝั่งเดียวกันหมด (มักจะเป็น Bottom side) และห่างจาก SMT Component มากพอเพื่อไม่ให้ Test Probe ชนอุปกรณ์แตก
- **Probe Washability & Flux Residue:** หากใช้ No-Clean Flux, Test Point อาจจะมีฟิล์มบางๆ เคลือบอยู่ ทำให้ Probe สัมผัสไม่ดี (Contact Failure) การออกแบบรูปร่าง Test point เป็นแบบเจาะทะลุผ่าน (Via-based) หรือเพิ่มขนาดเส้นผ่านศูนย์กลางจะช่วยลดปัญหานี้

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Rule of Thumb for Test Points:** ขนาด Test point ขั้นต่ำควรเป็น 0.8mm (32mil) และเว้นระยะห่างระหว่างจุด (Pitch) อย่างน้อย 1.27mm (50mil) เพื่อให้ใช้ Probe มาตรฐาน (100mil/50mil) ได้ในราคาถูก
- **Avoid Tall Components:** อย่าประเมินความสูงอุปกรณ์ผิดพลาด เวลาออกแบบ Test fixture อุปกรณ์ที่สูงมาก (เช่น Capacitor ตัวใหญ่) อาจกีดขวางการทำงานของ Press-down mechanism

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **テストポイント (Tesutopointo):** Test Point / จุดทดสอบ
- **接触不良 (Sesshoku furyou):** Contact failure / สัมผัสไม่ดี
- **プローブピン (Purobu Pin):** Probe pin / เข็มทดสอบ
- **検査治具 (Kensa Jigu):** Test Fixture/Jig / จิ๊กทดสอบ
- **実装高さ制限 (Jissou takasa seigen):** Component height restriction / ข้อจำกัดความสูงอุปกรณ์

## ควิซท้ายบท (Quiz)
**Q:** หากเกิดปัญหา False Failure (ทดสอบตกทั้งที่วงจรไม่พัง) บ่อยครั้งในสถานี ICT สาเหตุเชิง DFA ที่พบบ่อยที่สุดคืออะไร?
A) ชิปหน่วยความจำทำงานผิดปกติ
B) ฟลักซ์ (Flux Residue) เคลือบอยู่บน Test Point ทำให้ Probe จิ้มไม่โดนทองแดง
C) แรงดันไฟฟ้าของโรงงานไม่เสถียร
**เฉลย:** B) ฟลักซ์เคลือบบน Test point ทำให้เกิด Contact issue มักเจอในกระบวนการ No-clean
