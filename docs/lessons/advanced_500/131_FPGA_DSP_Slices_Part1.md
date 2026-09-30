# Lesson 131: FPGA DSP Slices - Part 1 (Architecture & ALU)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
DSP Slice ใน FPGA (เช่น Xilinx DSP48E2 หรือ Intel Variable Precision DSP) ไม่ใช่แค่ Multiplier แต่เป็น Arithmetic Logic Unit (ALU) ที่มีความสามารถสูง ประกอบด้วย Pre-adder, Multiplier (เช่น 27x18) และ Post-adder/Accumulator (เช่น 48-bit) การทำความเข้าใจ Routing ภายใน DSP slice เป็นกุญแจสำคัญในการออกแบบระดับ Senior Engineer โดยเฉพาะการใช้ Pre-adder เพื่อประหยัด Logic ทั่วไป และลด Delay ใน Critical Path

## ทริคหน้างาน OJT (OJT Tricks)
- **Use Pre-adder for Symmetric Filters:** ในการออกแบบ FIR Filter แบบสมมาตร ให้ใช้ Pre-adder ภายใน DSP เสมอ แทนที่จะใช้ Fabric Logic ซึ่งจะช่วยประหยัด Resource และทำให้ได้ Fmax ที่สูงขึ้น
- **Avoid Asynchronous Resets:** DSP slices ส่วนใหญ่ใน FPGA ปัจจุบันรองรับเฉพาะ Synchronous Reset การใช้ Asynchronous Reset จะทำให้ Synthesis Tool ต้องดึง Logic ออกมาใช้ภายนอก DSP ทันที

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **乗算器 (Jousanki):** Multiplier (ตัวคูณ)
- **加算器 (Kasanki):** Adder (ตัวบวก)
- **経路遅延 (Keiro Chien):** Routing Delay (ความหน่วงของเส้นทาง)
- **論理合成 (Ronri Gousei):** Logic Synthesis (การสังเคราะห์ลอจิก)

## ควิซท้ายบท (Quiz)
**Q:** ข้อใดคือเหตุผลหลักในการหลีกเลี่ยง Asynchronous Reset เมื่อใช้งาน DSP Slice?
**A:** เพราะ DSP Slices ส่วนใหญ่รองรับแต่ Synchronous Reset หากใช้ Async Reset จะต้องเปลือง Fabric Logic ภายนอก ทำให้ Fmax ลดลง
