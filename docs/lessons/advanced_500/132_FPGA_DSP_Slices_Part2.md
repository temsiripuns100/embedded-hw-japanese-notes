# Lesson 132: FPGA DSP Slices - Part 2 (Pipelining & Retiming)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
การเพิ่ม Pipelining Registers ภายใน DSP Slice เป็นสิ่งจำเป็นเพื่อให้ได้ความถี่สัญญาณนาฬิกา (Fmax) สูงสุด DSP48E2 มี Registers หลายชั้น (MREG, PREG, AREG, BREG) หากใช้งานไม่ครบ Fmax จะตกอย่างมาก การทำ Retiming โดย Synthesis tool สามารถช่วยย้าย Register เข้าไปใน DSP ได้ แต่ Senior Engineer ควรเขียนโค้ด (RTL) ให้ตรงกับโครงสร้าง Pipeline ของ DSP ตั้งแต่แรก (Instantiating หรือ Inference อย่างระมัดระวัง)

## ทริคหน้างาน OJT (OJT Tricks)
- **Register Packing:** ตรวจสอบ Timing Report เสมอว่า Registers ถูกแพ็คเข้าไปใน DSP (เช่น MREG=1, PREG=1) หรือไม่ หาก Register ติดอยู่ข้างนอก แสดงว่าอาจมีปัญหา Fan-out หรือ Reset ไม่ตรงกัน
- **Latency Balancing:** เมื่อต่อ DSP หลายตัวเรียงกัน ต้องมั่นใจว่า Latency ของ Data path และ Control path (เช่น Reset/Enable) สมดุลกันพอดี

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **パイプライン段数 (Paipurain Dansuu):** Pipeline Stages (จำนวนสเตจไปป์ไลน์)
- **遅延最適化 (Chien Saitekika):** Delay Optimization (การปรับแต่งดีเลย์)
- **最大動作周波数 (Saidai Dousa Shuuhasuu):** Maximum Operating Frequency (Fmax)
- **フリップフロップ (Furippu Furoppu):** Flip-Flop (ฟลิปฟล็อป)

## ควิซท้ายบท (Quiz)
**Q:** MREG ใน DSP48E2 ของ Xilinx มีหน้าที่หลักอะไร?
**A:** เป็น Pipeline Register หลังตัวคูณ (Multiplier) เพื่อแยกระยะเวลา Delay ของตัวคูณและ Post-adder ออกจากกัน ช่วยเพิ่ม Fmax
