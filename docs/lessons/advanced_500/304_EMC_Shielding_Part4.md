# Advanced Lesson: EMC - Shielding (Premium)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
EMC ไม่ใช่เรื่องของโชค แต่เป็นวิทยาศาสตร์ของการจัดการ Return Path และ Loop Area การป้องกัน Radiated Emission เริ่มต้นที่ Stackup และการวาง Decoupling Capacitor ที่มีค่า ESL ต่ำที่สุด ในหัวข้อ **Shielding** นี้ เราจะต้องพิจารณาตัวแปรแฝงต่างๆ (Parasitic elements) ที่ส่งผลกระทบต่อระบบโดยรวมอย่างหลีกเลี่ยงไม่ได้.

## 2. ทริคหน้างาน OJT (Field Tricks)
**💡 ข้อคิดจากรุ่นพี่:** ถ้าเจอปัญหาแปลกๆ ให้ลองจับอุณหภูมิดู บางทีเกิดจาก Thermal Runaway

## 3. คำศัพท์ภาษาญี่ปุ่นสำหรับตรวจแบบ (検図用語)
* 実装 (Jissou) - การลงอุปกรณ์ (Mounting)
* 対策 (Taisaku) - การแก้ไขปัญหา/มาตรการ
* 検図 (Kenzu) - การตรวจแบบ

## 4. ควิซท้ายบท (Quiz)
**Q:** ปัจจัยใดที่สำคัญที่สุดเมื่อต้องทำ Design Review ในหัวข้อ Shielding?
**A:** การตรวจสอบเอกสารอ้างอิงและขีดจำกัดสูงสุด (Maximum Ratings) ของระบบ
