# Lesson 88: PCB DFM Part 8 - Advanced HDI (High Density Interconnect)

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
HDI PCB ใช้ Microvia (Laser drilled) และเทคนิค Sequential Lamination เพื่อเพิ่มความหนาแน่นในการเดินเส้น การออกแบบ HDI มักใช้โครงสร้าง 1+N+1, 2+N+2 หรือ Any-layer HDI ข้อจำกัด DFM ที่สำคัญคือ Aspect Ratio ของ Microvia (มักไม่เกิน 0.8:1 - 1:1) และความแม่นยำในการทำ Layer Registration (Misregistration) การออกแบบ Stacked Microvia ต้องระวังเรื่อง Reliability เนื่องจากเกิด Stress สะสมจาก Thermal Expansion (CTE Mismatch) แนะนำให้ใช้ Staggered Microvia หากพื้นที่เอื้ออำนวย เพราะผลิตง่ายกว่าและทนทานกว่า

## ทริคหน้างาน OJT (OJT Practical Tricks)
- ถ้าไม่จำเป็นจริงๆ (พื้นที่บอร์ดไม่วิกฤต) ให้หลีกเลี่ยง Stacked Via และเปลี่ยนไปใช้ Staggered Via แทน จะช่วยเพิ่ม Yield และลดปัญหา Via crack ตอนทำ Thermal Cycling Test
- การทำ BGA Fanout สำหรับพิทช์เล็กๆ (<= 0.5mm) ต้องเช็คความสามารถของโรงงานเสมอเรื่อง Annular Ring ของ Microvia และระยะ Clearance
- การทำ Any-layer HDI มีราคาสูงมาก ให้ประเมิน Cost-Benefit เทียบกับ 2+N+2 เสมอ

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ビルドアップ基板 (Birudo Appu Kiban):** Build-up Board / HDI PCB
- **レーザービア (Reezaa Bia):** Laser Via / Microvia
- **スタックビア (Sutakku Bia):** Stacked Via (เวียซ้อนทับ)
- **スタッガードビア (Sutaggaado Bia):** Staggered Via (เวียเยื้อง)
- **層間ズレ (Soukan Zure):** Layer Misregistration (การเคลื่อนของชั้น PCB)

## ควิซท้ายบท (Quiz)
**คำถาม:** ในแง่ของความน่าเชื่อถือ (Reliability) และ DFM ทำไมวิศวกรจึงมักแนะนำให้ใช้ Staggered Microvia (スタッガードビア) มากกว่า Stacked Microvia?
**เฉลย:** เพราะ Stacked Microvia มีโอกาสเกิดรอยร้าว (Crack) ได้ง่ายกว่าเมื่อได้รับความร้อน (Thermal Stress) เนื่องจาก CTE Mismatch สะสมในแกน Z และ Staggered Microvia ผลิตได้ง่ายกว่า (Yield สูงกว่า)
