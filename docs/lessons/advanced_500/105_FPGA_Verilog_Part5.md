# Advanced FPGA/Verilog Part 5: DSP Slices & Pipeline Architecture

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ใน FPGA ยุคใหม่ จะมี Hard Macro ที่เรียกว่า DSP Slices (เช่น DSP48E1/E2 ใน Xilinx) ซึ่งออกแบบมาสำหรับการทำ MAC (Multiply-Accumulate) โดยเฉพาะ `P = P + A * B`
การเขียน Verilog ที่ดีเพื่อให้ Synthesis Tool แมป (Map) โค้ดลง DSP Slice อย่างมีประสิทธิภาพ (DSP Inference) ต้องเข้าใจโครงสร้าง Pipeline Register ภายใน DSP Slice นั้นๆ หากใช้ Pipeline Register ภายในครบ (เช่น ขา A, B, M, P) จะทำให้ได้ Performance ระดับ 500MHz+ โดยไม่เปลือง Slice Logic ภายนอกเลย

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick 1:** หลีกเลี่ยงการทำ Reset ภายใน Data Path ของ DSP ถ้าระบบไม่ได้ต้องการจริงๆ เพราะการใช้ Reset ร่วมกับ Pipeline Register ใน DSP อาจทำให้ Tool แมปวงจรลง DSP ไม่ได้ ต้องไปสร้างด้วย Logic ธรรมดา (เปลือง रिसอร์สและช้า)
- **OJT Trick 2:** ถ้าต้องคูณเลขค่าคงที่ (Constant Multiplication) หลายๆ ตัว ลองใช้เทคนิค Shift-and-Add แทนถ้า DSP Slice ไม่พอ
- **OJT Trick 3:** ตรวจสอบ Synthesis Report เสมอว่ามี `DSP48 inferred` ตรงตามที่ตั้งใจไว้หรือไม่ อย่าปล่อยให้มันใช้ LUTs สร้าง Multiplier ถ้าไม่จำเป็น

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **積和演算 (Sekiwa enzan):** Multiply-Accumulate (MAC) operation
- **乗算器 (Jōzan-ki):** Multiplier
- **加算器 (Kasan-ki):** Adder
- **遅延 (Chien):** Latency/Delay
- **消費電力 (Shōhi denryoku):** Power consumption

## ควิซท้ายบท (Quiz)
**Q1:** หากต้องการให้ Synthesis tool นำโค้ด $A \times B$ ไปใช้ DSP Slice ภายใน FPGA อย่างมีประสิทธิภาพที่สุด ควรทำอย่างไร?
a) เขียน Operator `*` ธรรมดาแล้วไม่ต่องใส่ Register เลย
b) ใช้ Register รับข้อมูลเข้า A, B และรับข้อมูลออก (Pipeline) ให้ตรงกับ Architecture ของ DSP เบอร์นั้นๆ
c) ใช้คำสั่ง `for` loop ในการคูณแบบ Shift and Add
d) ห้ามใช้ Operator `*` ต้องเรียกใช้ IP Core เท่านั้น

*(เฉลย: b)*
