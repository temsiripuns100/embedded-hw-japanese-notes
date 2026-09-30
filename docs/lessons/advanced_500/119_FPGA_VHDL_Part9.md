# FPGA & VHDL Part 9: DSP Blocks & Pipelining in FPGA

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในงาน Signal Processing, AI หรือเรดาร์ ต้องมีการใช้สมการคณิตศาสตร์จำนวนมาก (โดยเฉพาะ MAC: Multiply-Accumulate)
- FPGA มี Hardware พิเศษที่เรียกว่า **DSP Slices** (เช่น DSP48E ใน Xilinx) ซึ่งทำหน้าที่คูณและบวกได้อย่างรวดเร็ว
- การเขียนโค้ด `A * B` เฉยๆ อาจทำให้ Tool แปลงเป็น LUTs จำนวนมหาศาล (Logic ธรรมดา) ซึ่งกินพื้นที่และทำงานช้า
- **Pipelining:** การแบ่งขั้นตอนคำนวณออกเป็นส่วนย่อยๆ แล้วคั่นด้วย Register เพื่อเพิ่ม Data Throughput และ Fmax

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Inferring DSP:** การจะให้ Synthesis Tool เรียกใช้ DSP Block อัตโนมัติ ต้องเขียน RTL ให้สอดคล้องกับสถาปัตยกรรมของ DSP นั้นๆ เช่น ต้องมี Pipeline Register ที่ Input, ขาออก (Output) ต้องมี Register ทันที และควรใช้ Synchronous Reset (DSP บางรุ่นไม่รองรับ Async Reset)
- หาก Tool ไม่ดึง DSP มาใช้ ให้เช็คว่าเราไม่ได้ตั้ง Reset ผิดประเภท หรือลืมใส่ Register ตรงจังหวะที่กำหนด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **パイプライン化 (Paipurain-ka)** - Pipelining (การทำไพป์ไลน์)
- **乗算器 (Jousanki)** - Multiplier (ตัวคูณ)
- **演算器 (Enzanki)** - Arithmetic Logic Unit / DSP (หน่วยคำนวณ)
- **動作周波数 (Dousa shuuhasuu)** - Operating frequency (ความถี่ในการทำงาน)

## ควิซท้ายบท (Quiz)
**Q:** สาเหตุหลักที่ Synthesis Tool ไม่ยอมแปลงการคูณ (`*`) ไปเป็น **DSP Slice** แต่ดันไปสร้างจาก LUTs แทน คืออะไร?
**A:** อาจเกิดจากการเขียนโค้ดใช้ Asynchronous Reset (ซึ่ง DSP block บางตระกูลไม่รองรับ) หรือไม่ได้ใส่ Pipeline registers ให้ตรงกับโครงสร้างของ DSP block
