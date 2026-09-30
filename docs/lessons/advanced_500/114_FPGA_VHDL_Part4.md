# Lesson 114: DSP Blocks & Memory Inferencing

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การประมวลผลสัญญาณดิจิทัล (DSP) ใน FPGA ปัจจุบันจะใช้ DSP48 slices (ใน Xilinx) หรือ DSP Blocks (ใน Intel) การเขียน VHDL แบบเดิมที่เป็นเครื่องหมาย `*` หรือ `+` โดยไม่มี Pipeline register จะทำให้ชิปดึง LUT มาทำคณิตศาสตร์แทนที่จะใช้ Hard IP ทำให้เปลืองพื้นที่และทำงานช้า
สำหรับการใช้ Memory (BRAM/URAM) ควรเขียนโค้ดตาม Template ของผู้ผลิตเพื่อให้เครื่องมือสามารถอนุมาน (Infer) ไปใช้ Block RAM ได้ ไม่เช่นนั้นจะกลายเป็น Distributed RAM ซึ่งสูญเสียทรัพยากรอย่างหนัก

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Pipeline Multipliers:** สังเกต Document ของ FPGA เสมอว่า DSP Block มี Register ภายในกี่สเตจ (เช่น MREG, PREG) แล้วเขียน VHDL ให้มี Delay เทียบเท่ากัน
- **RAM Initialization:** สามารถใส่ค่าเริ่มต้นให้ Block RAM ได้โดยตรงผ่าน `$readmemb` หรือการประกาศ array ค่าคงที่ใน VHDL ซึ่งจะถูกโหลดพร้อมกระบวนการ Configuration
- **Resource Sharing:** หากระบบทำงานที่ความถี่สูงกว่า Data Rate มากๆ ให้ใช้ Time-division multiplexing (TDM) ใช้ DSP ตัวเดียวคำนวณหลายค่าเพื่อประหยัด Resource

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **積和演算 (Sekiwa Enzan):** Multiply-Accumulate / MAC (การคูณและบวกสะสม)
- **内部メモリ (Naibu Memori):** Internal Memory (หน่วยความจำภายใน)
- **パイプライン処理 (Paipurain Shori):** Pipeline Processing (การประมวลผลแบบไปป์ไลน์)
- **最適化 (Saitekika):** Optimization (การปรับให้เหมาะสมที่สุด)

## ควิซท้ายบท (Quiz)
1. การเขียนโค้ดที่ทำให้เครื่องมือตีความ RAM ไปเป็น Distributed RAM แทน Block RAM มีผลเสียอย่างไร?
2. 内部メモリ มีประโยชน์อย่างไรเมื่อเทียบกับการใช้ External DDR?
