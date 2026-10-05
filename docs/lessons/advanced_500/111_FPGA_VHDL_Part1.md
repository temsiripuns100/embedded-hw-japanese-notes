# Lesson 111: FPGA Architecture & VHDL Fundamentals (Senior Level)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior เราไม่ได้มองแค่โค้ด VHDL เป็นเพียงซอฟต์แวร์ แต่มันคือฮาร์ดแวร์ การทำความเข้าใจโครงสร้างภายในของ FPGA (Look-Up Tables, Flip-Flops, Routing Matrix, DSP slices, และ Block RAMs) เป็นสิ่งสำคัญในการเขียนโค้ดที่สามารถทำ Synthesis และ Place & Route ได้อย่างมีประสิทธิภาพ 
การเขียน VHDL ที่ดีต้องคำนึงถึง Inferencing เสมอ ว่าโค้ดที่เราเขียนจะถูกตีความเป็นฮาร์ดแวร์ชิ้นไหนในชิปจริง

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Avoid Latch Inferencing:** ห้ามลืมปิดเคสใน `case` หรือ `if-else` เพราะจะทำให้เกิด Unintentional Latches ซึ่งส่งผลร้ายแรงต่อ Timing Analysis
- **Register All Outputs:** เพื่อป้องกัน Glitch และทำให้ Timing ดีขึ้น ควร Register สัญญาณขาออกทุกครั้ง (Pipelining)
- **Hierarchy Design:** ออกแบบเป็นโมดูลย่อยๆ และใช้ `generate` statement สำหรับโครงสร้างที่ซ้ำซาก เพื่อลดความซ้ำซ้อนของโค้ด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **論理合成 (Rongi Gousei):** Logic Synthesis (การสังเคราะห์ลอจิก)
- **配置配線 (Haichi Haisen):** Place and Route (การจัดวางและเดินสายสัญญาณ)
- **組み合わせ回路 (Kumiawase Kairo):** Combinational Logic (วงจรเชิงผสม)
- **順序回路 (Junjo Kairo):** Sequential Logic (วงจรลำดับ)
- **ラッチ発生 (Latchi Hassei):** Latch Generation (การเกิด Latch)

## ควิซท้ายบท (Quiz)
1. การเกิด Latch ที่ไม่ได้ตั้งใจใน VHDL มักเกิดจากสาเหตุใด? (คำตอบ: การระบุเงื่อนไขในกระบวนการแบบ Combinational ไม่ครบถ้วน)
2. อธิบายความแตกต่างระหว่าง 論理合成 และ 配置配線
