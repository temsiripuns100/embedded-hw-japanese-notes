# 3.7 カスタムIPの作成とアドレスマッピング (การสร้าง Custom IP ด้วย VHDL และการจัดสรร Address)

## 📖 ทฤษฎี (Theory - Engineering Perspective)
**Custom IP (Intellectual Property)** คือวงจรลอจิกเฉพาะทางที่เราเขียนขึ้นเองด้วย VHDL หรือ Verilog (เช่น วงจรขับมอเตอร์, ตัวถอดรหัสเฉพาะกิจ) เพื่อนำมาใช้งานร่วมกับ CPU แกนหลัก (เช่น Nios II หรือ ARM Cortex ใน SoC) 
**アドレスマッピング (Address Mapping)** เมื่อเราแปลงวงจรของเราให้กลายเป็น Peripheral ตัวหนึ่งของ CPU เราต้องกำหนด "Address Base" ให้มัน เพื่อให้วิศวกรซอฟต์แวร์ (Firmware Engineer) สามารถใช้คำสั่งพอยน์เตอร์ภาษา C ชี้มาอ่าน/เขียนรีจิสเตอร์ในวงจรของเราได้ถูกต้อง

## 💡 ทริคหน้างาน (OJT Tricks)
- **ระวัง Word Alignment:** ปัญหาคลาสสิกเวลาทำงานข้ามสาย (HW vs SW)! ในฝั่ง FPGA รีจิสเตอร์จะนับเรียงทีละ 1 (Address 0, 1, 2, 3...) แต่ CPU แบบ 32-bit มักจะมองหน่วยความจำเป็น Byte ทำให้การก้าว Address ของรีจิสเตอร์ 32-bit จะต้องกระโดดทีละ 4 (Address 0x00, 0x04, 0x08, 0x0C) ถ้าสื่อสารไม่ตรงกัน ซอฟต์แวร์จะอ่านค่าขยะออกมาทันที
- **ทำ Register Map Document ให้เป๊ะ:** ก่อนเริ่มเขียนโค้ด VHDL ให้ตกลงตาราง Register Map (ที่อยู่, บิตไหนทำอะไร, Read/Write status) กับทีม Software ให้จบก่อน และอย่าแอบเปลี่ยนกลางคัน!

## 🗣️ คำศัพท์และประโยคภาษาญี่ปุ่น
- **カスタムIP (Kasutamu IP):** Custom IP (วงจรที่พัฒนาขึ้นเอง)
- **アドレスマッピング (Adoresu Mappingu):** Address Mapping (การผังที่อยู่หน่วยความจำ)
- **レジスタ (Rejisuta):** Register (รีจิสเตอร์/หน่วยความจำภายใน)
- **仕様書 (Shiyōsho):** Specification Document (เอกสารสเปค)
- **ファームウェア (Fāmuwea):** Firmware

**ประโยคที่ใช้บ่อย:**
> 「カスタムIPのレジスタマップ仕様書を作成しました。SWチームはこちらのアドレス空間を参照してください。」
> *(Kasutamu IP no rejisuta mappu shiyōsho o sakusei shimashita. Sofutowea chīmu wa kochira no adoresu kūkan o sanshō shite kudasai.)*
> "ได้จัดทำเอกสารสเปค Register Map ของ Custom IP เรียบร้อยแล้วครับ ขอให้ทีม Software อ้างอิง Address Space จากเอกสารนี้ได้เลยครับ/ค่ะ"

## 📝 ควิซทดสอบ (Quiz)
**คำถาม:** หากคุณกำหนดให้รีจิสเตอร์ `CONTROL_REG` (32-bit) อยู่ที่ Base Address `0x1000` และรีจิสเตอร์ตัวถัดไปคือ `STATUS_REG` (32-bit) หาก CPU เป็นสถาปัตยกรรมที่อ้างอิง Address แบบ Byte-addressable ที่อยู่ (Address) ของ `STATUS_REG` ควรจะเป็นค่า Hexadecimal ใด?
