# Advanced Lesson: FPGA - VHDL (Premium)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior Engineer การออกแบบ FPGA จะเน้นไปที่การลด Propagation Delay และการทำ Timing Closure ให้ผ่านในทุกๆ PVT (Process, Voltage, Temperature) corners การใช้งานรีซอร์สอย่าง BRAM และ DSP ต้องพิจารณา Pipeline registers เพื่อลด Critical path delay. ในหัวข้อ **VHDL** นี้ เราจะต้องพิจารณาตัวแปรแฝงต่างๆ (Parasitic elements) ที่ส่งผลกระทบต่อระบบโดยรวมอย่างหลีกเลี่ยงไม่ได้.

## 2. ทริคหน้างาน OJT (Field Tricks)
**💡 ข้อคิดจากรุ่นพี่:** ก่อนส่งแบบไปผลิต ให้เช็ค Gerber ด้วยตัวเองเสมอ อย่าเชื่อแค่ DRC ของโปรแกรม

## 3. คำศัพท์ภาษาญี่ปุ่นสำหรับตรวจแบบ (検図用語)
* 歩留まり (Budomari) - Yield rate
* 故障 (Koshou) - การเสีย/ชำรุด
* 妥当性 (Datousei) - ความสมเหตุสมผล (Validity)

## 4. ควิซท้ายบท (Quiz)
**Q:** ปัจจัยใดที่สำคัญที่สุดเมื่อต้องทำ Design Review ในหัวข้อ VHDL?
**A:** การตรวจสอบเอกสารอ้างอิงและขีดจำกัดสูงสุด (Maximum Ratings) ของระบบ
