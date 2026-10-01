# Advanced Lesson: EMC - Radiated Emissions (Premium)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
EMC ไม่ใช่เรื่องของโชค แต่เป็นวิทยาศาสตร์ของการจัดการ Return Path และ Loop Area การป้องกัน Radiated Emission เริ่มต้นที่ Stackup และการวาง Decoupling Capacitor ที่มีค่า ESL ต่ำที่สุด ในหัวข้อ **Radiated Emissions** นี้ เราจะต้องพิจารณาตัวแปรแฝงต่างๆ (Parasitic elements) ที่ส่งผลกระทบต่อระบบโดยรวมอย่างหลีกเลี่ยงไม่ได้.

## 2. ทริคหน้างาน OJT (Field Tricks)
**💡 ข้อคิดจากรุ่นพี่:** เวลาทำ Design Review กับคนญี่ปุ่น ให้เตรียม Data หรือ Waveform จาก Oscilloscope ไปด้วยเสมอ

## 3. คำศัพท์ภาษาญี่ปุ่นสำหรับตรวจแบบ (検図用語)
* 信頼性 (Shinraisei) - ความน่าเชื่อถือ (Reliability)
* 解析 (Kaiseki) - การวิเคราะห์
* 手戻り (Temodori) - การทำงานซ้ำ/รื้อทำใหม่

## 4. ควิซท้ายบท (Quiz)
**Q:** ปัจจัยใดที่สำคัญที่สุดเมื่อต้องทำ Design Review ในหัวข้อ Radiated Emissions?
**A:** การตรวจสอบเอกสารอ้างอิงและขีดจำกัดสูงสุด (Maximum Ratings) ของระบบ
