# Advanced PCB Stackup - Part 5: Stackup Design Review (Kenzu) & Manufacturing Tolerances

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในโลกความจริง (Real-world manufacturing) ความหนาของแผ่น Dielectric ไม่เป๊ะ 100% มีค่า Tolerance อยู่ประมาณ ±10% นอกจากนี้ Dk ของวัสดุก็แปรผันตามความถี่ (Frequency-dependent) 
การออกแบบ Stackup ที่ทนทาน (Robust) ต้องพิจารณาสิ่งเหล่านี้ตั้งแต่แรก
- **Symmetrical Stackup:** โครงสร้างของ PCB ควรสมมาตรรอบแกนกลาง ทั้งในเรื่องของความหนาชั้น, ชนิดวัสดุ, และสัดส่วนทองแดง (Copper distribution) หากไม่สมมาตร บอร์ดจะบิดงอหรือโก่งตัว (Bow and Twist / 反り) เมื่อผ่านเตา Reflow
- **Impedance Tolerance:** โดยทั่วไปเราขอ Impedance control ที่ ±10% แต่ถ้าต้องการความแม่นยำมากสามารถคุยกับโรงงานขอ ±5% ได้ (ราคาแพงขึ้น) ซึ่งผู้ผลิตอาจต้องปรับเปลี่ยน Stackup เล็กน้อย (Fab-adjusted stackup)

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **อย่าดื้อรั้นกับ Fab House:** บ่อยครั้งเราสร้าง Stackup คำนวณสวยงามบนโปรแกรม (เช่น Polar Instruments) แล้วส่งไป แต่ Fab บอกว่า "เราไม่มี Prepreg รุ่นนี้ในสต็อก ขอเปลี่ยนเป็นรุ่นเทียบเท่า" เราต้องเปิดใจตรวจสอบ Dk/Df ใหม่ แล้วยอมให้เขาปรับ Line width เล็กน้อยเพื่อให้ Impedance ตรง เพราะการรอสั่งวัสดุใหม่จะทำให้ Lead time นานมาก
- **การทำ Kenzu Checklist สำหรับ Stackup:** 
  1. บอร์ดสมมาตรหรือไม่?
  2. Impedance calculation ตรงกันกับตารางในหน้าแรก (Fab note) หรือไม่?
  3. Copper weight ในชั้นในและนอกเหมาะสมกับการรับกระแส (Current ampacity) หรือไม่?
  4. Core/Prepreg สลับกันถูกต้องตามลำดับการอัด (Pressing cycle) หรือไม่?

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **反り (Sori):** Bow and Twist / Warpage / การโก่งงอของบอร์ด
- **対称性 (Taishousei):** Symmetry / ความสมมาตรของโครงสร้าง
- **公差 (Kousa):** Tolerance / ค่าความเผื่อ (เช่น ±10%)
- **面付け (Mentsuke):** Panelization / การจัดเรียงบอร์ดลงบนแผงผลิต
- **製造元 (Seizou-moto) / 基板屋 (Kiban-ya):** Fab house / ผู้ผลิตแผ่นปริ้นท์

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** หาก Stackup ของบอร์ด (เช่น ชั้นทองแดงและความหนา Dielectric) ออกแบบมาไม่สมมาตร ปัญหาใหญ่ที่สุดที่มักพบในกระบวนการประกอบ (Assembly) คืออะไร?
1. บอร์ดจะน้ำหนักเกิน
2. Impedance จะผิดเพี้ยนไปหมด
3. บอร์ดจะเกิดการบิดงอหรือโก่ง (Warpage) เมื่อโดนความร้อนในเตา Reflow
4. ผู้ผลิตเจาะรูไม่ได้

*เฉลย: 3*
