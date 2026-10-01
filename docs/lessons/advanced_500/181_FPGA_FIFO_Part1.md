# Advanced Lesson: FPGA - FIFO (Premium)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior Engineer การออกแบบ FPGA จะเน้นไปที่การลด Propagation Delay และการทำ Timing Closure ให้ผ่านในทุกๆ PVT (Process, Voltage, Temperature) corners การใช้งานรีซอร์สอย่าง BRAM และ DSP ต้องพิจารณา Pipeline registers เพื่อลด Critical path delay. ในหัวข้อ **FIFO** นี้ เราจะต้องพิจารณาตัวแปรแฝงต่างๆ (Parasitic elements) ที่ส่งผลกระทบต่อระบบโดยรวมอย่างหลีกเลี่ยงไม่ได้.

## 2. ทริคหน้างาน OJT (Field Tricks)
**💡 ข้อคิดจากรุ่นพี่:** ก่อนส่งแบบไปผลิต ให้เช็ค Gerber ด้วยตัวเองเสมอ อย่าเชื่อแค่ DRC ของโปรแกรม

## 3. คำศัพท์ภาษาญี่ปุ่นสำหรับตรวจแบบ (検図用語)
* 実装 (Jissou) - การลงอุปกรณ์ (Mounting)
* 対策 (Taisaku) - การแก้ไขปัญหา/มาตรการ
* 検図 (Kenzu) - การตรวจแบบ

## 4. ควิซท้ายบท (Quiz)
**Q:** ปัจจัยใดที่สำคัญที่สุดเมื่อต้องทำ Design Review ในหัวข้อ FIFO?
**A:** การตรวจสอบเอกสารอ้างอิงและขีดจำกัดสูงสุด (Maximum Ratings) ของระบบ
