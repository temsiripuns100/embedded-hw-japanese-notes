# Lesson 133: FPGA DSP Slices - Part 3 (Multiply-Accumulate (MAC) & Filtering)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
Multiply-Accumulate (MAC) เป็นหัวใจของ Digital Signal Processing (เช่น FIR/IIR Filters) ในระดับ Senior เราจะไม่เขียน `a * b + c` แล้วหวังให้ Tool จัดการให้ทั้งหมด แต่จะวิเคราะห์ Data Width Growth อย่างละเอียด เช่น 18-bit x 18-bit ได้ 36-bit เมื่อทำ Accumulate 256 ครั้ง ต้องใช้ Accumulator อย่างน้อย 36 + log2(256) = 44 bit เพื่อป้องกัน Overflow 

## ทริคหน้างาน OJT (OJT Tricks)
- **Bit Growth Management:** อย่าใช้ bit-width มากเกินความจำเป็น การตัด Bit (Truncation) หรือการปัดเศษ (Rounding) ที่ถูกต้องหลังกระบวนการ MAC จะช่วยประหยัด DSP Slices ในสเตจถัดไป
- **Use DSP for Counters:** หากคุณมี Counter ขนาดใหญ่ (เช่น 48-bit) และ Fabric Logic ค่อนข้างแน่น คุณสามารถใช้ DSP slice ทำหน้าที่เป็น Counter (Accumulator +1) ได้

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **積和演算 (Sekiwa Enzan):** Multiply-Accumulate Operation (MAC)
- **桁あふれ (Keta Afure):** Overflow (โอเวอร์โฟลว์)
- **丸め処理 (Marume Shori):** Rounding Processing (การปัดเศษ)
- **切り捨て (Kirisute):** Truncation (การตัดทิ้ง)

## ควิซท้ายบท (Quiz)
**Q:** หากคูณข้อมูล 16-bit กับ 16-bit และต้องการบวกสะสม (Accumulate) 64 รอบ ต้องใช้ขนาด Accumulator อย่างน้อยกี่บิต?
**A:** 16+16 = 32 บิต. log2(64) = 6 บิต. รวมเป็น 38 บิต.
