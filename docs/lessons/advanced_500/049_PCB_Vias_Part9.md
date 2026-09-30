# Lesson 49: RF/Microwave Vias & High-Frequency (高速通信とビアスタブ)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระบบความถี่สูง (High-Speed Digital อย่าง PCIe Gen 4/5, PAM4 56G หรือ RF/Microwave) Via ไม่ได้เป็นแค่จุดเชื่อมต่อไฟฟ้า (Ideal Connection) แต่ทำตัวเป็น RLC Network 
- **Via Stub Effect:** เมื่อสัญญาณวิ่งจากชั้น Top ไปชั้น Inner Layer ส่วนที่เหลือของรู Via (จากชั้น Inner ทะลุไป Bottom) จะทำตัวเป็น "Stub" หรือเสาอากาศปลายเปิด (Open-ended stub) ซึ่งสร้างความต้านทานไฟฟ้าสลับ (Impedance Mismatch) และเกิดความจุแฝง (Parasitic Capacitance) ส่งผลให้สัญญาณสะท้อนกลับ (Reflection) และทำลายความสมบูรณ์ของสัญญาณ (Signal Integrity)
- **Resonant Frequency:** ความยาวของ Stub จะเป็นตัวกำหนด Quarter-wavelength resonance frequency ($f_{res}$) ยิ่ง Stub ยาว ความถี่ที่สัญญาณจะถูกกลืนหายไป (Notch frequency) ยิ่งต่ำลง

## ทริคหน้างาน OJT (現場のコツ)
- **Backdrilling (Controlled Depth Drilling):** เพื่อกำจัด Stub โรงงานจะใช้วิธี Backdrill เจาะทองแดงส่วนเกินทิ้งจากด้านล่าง (หรือด้านบน) ในการ 検図 (Kenzu) ต้องตรวจสอบ Backdrill Table ให้แน่ใจว่าได้ระบุชั้นที่เจาะถึงอย่างถูกต้อง พร้อมกับเผื่อ tolerance สำหรับ "Must Not Cut" layer (ชั้นที่ห้ามเจาะโดน) และ "Must Cut" layer 
- **Anti-Pad Optimization:** ในวงจร High-Speed ขนาดของ Clearance รอบๆ รู Via (Anti-Pad) ในชั้น Ground/Power Plane มีผลต่อ Impedance มาก การทำ Anti-pad รูปวงรีครอบทั้งสอง Vias ของ Differential Pair ช่วยควบคุม Impedance ให้คงที่และลด Capacitance ได้ดีกว่า

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **スタブ (Sutabu / Stub):** ส่วนเกินของรอยต่อ (ติ่ง)
- **バックドリル (Bakku Doriru / Backdrill):** การเจาะเอาทองแดงส่วนเกินในรูออก
- **インピーダンス整合 (Inpiidansu Seigou / Impedance Matching):** การควบคุมอิมพีแดนซ์
- **寄生容量 (Kisei Youryou / Parasitic Capacitance):** ค่าความจุแฝง
- **反射 (Hansha / Reflection):** การสะท้อนของสัญญาณ
- **信号品質 (Shingou Hinshitsu / Signal Integrity):** ความสมบูรณ์ของสัญญาณ

## ควิซท้ายบท (Quiz)
**Q:** ผลกระทบที่ร้ายแรงที่สุดของการมี "Via Stub" ขนาดยาวในระบบสื่อสารความเร็วสูงคืออะไร?
1. ทำให้กระแสไฟ DC ไหลผ่านไม่ได้
2. ทำให้เกิด Resonance ซึ่งจะสร้าง Notch Filter ที่ตัดทอนความถี่เฉพาะบางความถี่ทิ้งไป
3. เพิ่มความเหนี่ยวนำ (Inductance) ในระบบอย่างมหาศาล
4. ทำให้ PCB ร้อนขึ้น

*(คำตอบที่ถูกต้อง: 2. ทำให้เกิด Resonance (Quarter-wavelength) ซึ่งทำให้เกิดการสะท้อนสัญญาณรุนแรงและเกิดรอยหยัก (Notch) ใน Insertion Loss)*
