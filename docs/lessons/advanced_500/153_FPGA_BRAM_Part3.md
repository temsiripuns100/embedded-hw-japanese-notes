# Lesson 153: BRAM Resource Management: Inference vs Instantiation

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การประยุกต์ใช้ BRAM สามารถทำได้ผ่าน HDL Inference (การเขียนโค้ดตาม Template) หรือการ Instantiation (การเรียกใช้ Primitive ของ Vendor โดยตรง) ระดับ Senior ต้องรู้ข้อจำกัดของ Inference เช่น การไม่สามารถใช้ฟีเจอร์พิเศษบางอย่างได้ (เช่น ECC, Asynchronous FIFO ฝังใน BRAM) การใช้ Instantiation ช่วยให้รีดประสิทธิภาพสูงสุดและใช้ฟีเจอร์เฉพาะของชิปนั้นๆ ได้ แต่จะสูญเสียความสามารถในการพอร์ต (Portability) ไปยัง FPGA ยี่ห้ออื่น

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Code Portability:** สำหรับ IP ที่ต้องนำไปใช้หลายโปรเจกต์หรือหลายตระกูล FPGA ให้พยายามใช้ Inference 
- **Check Synthesis Report:** ตรวจสอบ Synthesis log อย่างละเอียดเสมอว่า อาร์เรย์ที่ตั้งใจให้เป็น BRAM ถูกแปลงเป็น BRAM จริงๆ หรือหลุดไปเป็น Distributed RAM/Registers

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- 推論 (Suiron) - Inference
- 組み込み (Kumikomi) - Instantiation
- 記述スタイル (Kijutsu sutairu) - Coding style
- 移植性 (Ishokusei) - Portability

## ควิซท้ายบท (Quiz)
**คำถาม:** ข้อใดคือข้อเสียหลักของการทำ BRAM Instantiation แบบเจาะจง Primitive (เช่น RAMB36E1 ของ Xilinx)?
**คำตอบ:** (เฉลย: สูญเสีย Portability ทำให้ไม่สามารถนำโค้ดไปคอมไพล์บน FPGA ของผู้ผลิตรายอื่นหรือตระกูลอื่นได้ง่าย)
