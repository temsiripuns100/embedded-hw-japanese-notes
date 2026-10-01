# Lesson 053: PCB Thermal Part 3 - Copper Pour and Thermal Reliefs (Thermals)

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
การใช้ Solid Copper Pour กว้างๆ ช่วยกระจายความร้อน (Spreading Resistance ต่ำลง) แต่ในการบัดกรี (Soldering) ความร้อนจากหัวแร้งหรือ Wave จะถูกดึงออกไปเร็วเกินไป ทำให้บัดกรีไม่ติด (Cold Solder) จึงต้องสร้าง Thermal Relief (Spoke) เพื่อลดการไหลของความร้อนชั่วคราว อย่างไรก็ตาม ในทาง High-current (Power) และ Thermal Dissipation ขั้นสูง การใช้ Thermal Relief จะเพิ่ม DCR และ R_th จึงมักหลีกเลี่ยง และใช้ Solid connection ควบคู่กับการควบคุม Reflow Profile แทน

## ทริคหน้างาน OJT
ในการตรวจ Kenzu พวกวงจร Switching Regulator, Pad ของ MOSFET ห้ามมี Thermal Relief เด็ดขาด ให้ต่อตรง (Direct Connect) เสมอ แม้จะต้องใช้หัวแร้งวัตต์สูงซ่อมก็ตาม

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図)
- **ベタ塗布 (Beta Tofu) / ベタパターン:** Solid Copper Pour / Polygon Pour
- **サーマルリリーフ (Saamaru Ririifu):** Thermal Relief
- **芋はんだ (Imo Handa):** Cold Solder Joint (บัดกรีไม่ติด/ตะกั่วด้าน)

## ควิซท้ายบท
Q: เพราะเหตุใดจึงห้ามใช้ Thermal Relief กับ Pad ของ Power MOSFET?
A: เพราะเป็นการจำกัดการไหลของกระแสสูงและจำกัดการระบายความร้อน ทำให้เกิดความร้อนสะสม
