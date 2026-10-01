# Advanced Lesson: PCB - BGA (Premium)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior Engineer การออกแบบ FPGA จะเน้นไปที่การลด Propagation Delay และการทำ Timing Closure ให้ผ่านในทุกๆ PVT (Process, Voltage, Temperature) corners การใช้งานรีซอร์สอย่าง BRAM และ DSP ต้องพิจารณา Pipeline registers เพื่อลด Critical path delay. ในหัวข้อ **BGA** นี้ เราจะต้องพิจารณาตัวแปรแฝงต่างๆ (Parasitic elements) ที่ส่งผลกระทบต่อระบบโดยรวมอย่างหลีกเลี่ยงไม่ได้.

## 2. ทริคหน้างาน OJT (Field Tricks)
**💡 ข้อคิดจากรุ่นพี่:** การใช้ Probe วัดสัญญาณ High-speed ต้องใช้สายกราวด์สั้นที่สุด (Spring ground) ไม่งั้นจะเห็น Ringing ปลอม

## 3. คำศัพท์ภาษาญี่ปุ่นสำหรับตรวจแบบ (検図用語)
* 仕様書 (Shiyousho) - เอกสาร Spec
* 評価 (Hyouka) - การประเมิน/ทดสอบ
* ノイズ (Noizu) - สัญญาณรบกวน

## 4. ควิซท้ายบท (Quiz)
**Q:** ปัจจัยใดที่สำคัญที่สุดเมื่อต้องทำ Design Review ในหัวข้อ BGA?
**A:** การตรวจสอบเอกสารอ้างอิงและขีดจำกัดสูงสุด (Maximum Ratings) ของระบบ
