# 031: PCB Crosstalk เจาะลึก Part 1 - Capacitive & Inductive Coupling

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Crosstalk เกิดจากปรากฏการณ์ Electromagnetic Coupling ระหว่างสองสัญญาณ (Aggressor และ Victim) โดยแบ่งออกเป็น 2 ประเภทหลักที่เกิดขึ้นพร้อมกัน:
1. **Capacitive Coupling (Mutual Capacitance - $C_m$)**: เกิดจากสนามไฟฟ้า (Electric Field) ระหว่างเส้นทองแดง เมื่อมี $dV/dt$ สูงบนเส้น Aggressor จะฉีดกระแส $I_{xtalk} = C_m \frac{dV_{aggressor}}{dt}$ เข้าสู่ Victim กระแสนี้จะแยกไหลไปทั้งสองทิศทาง (Forward และ Backward) ทำให้เกิด Voltage pulse ขึ้นที่ Victim
2. **Inductive Coupling (Mutual Inductance - $L_m$)**: เกิดจากสนามแม่เหล็ก (Magnetic Field) ตามกฎฟาราเดย์ เมื่อมี $di/dt$ บน Aggressor จะสร้างแรงดันเหนี่ยวนำ $V_{xtalk} = L_m \frac{di_{aggressor}}{dt}$ บน Victim กระแสเหนี่ยวนำนี้ตามกฎของเลนซ์ (Lenz's Law) จะไหลในทิศทางตรงข้ามกับ Aggressor (ไหลย้อนกลับ - Backward)

**บทสรุปสมการรวม:** ในสาย Microstrip, กระแสรวมที่ปลายทาง (Far-End) คือผลต่างระหว่าง Capacitive และ Inductive coupling ในขณะที่ต้นทาง (Near-End) คือผลรวม ทำให้ NEXT มักมีปัญหามากกว่า FEXT

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **การวิเคราะห์ผ่าน TDR (Time-Domain Reflectometer):** เวลาเจอ Cross-talk ในแล็บ ให้ใช้ TDR ยิงเพื่อดู Impedance Profile หากเจอ Dip หรือ Peak ณ จุดที่ Trace ตีคู่กัน (Parallel routing) แสดงว่าตรงนั้น Coupling กันแรงเกินไป
- **Layer Stackup:** ลด $C_m$ และ $L_m$ ได้ดีที่สุดไม่ใช่แค่การถ่างระยะ (3W rule) แต่คือการนำ Trace เข้าใกล้ Reference Plane ให้มากขึ้น (ลดความหนาของ Dielectric ระหว่าง Signal กับ GND) เส้นแรงแม่เหล็ก/ไฟฟ้าจะพุ่งลง Ground แทนที่จะกระจายไปหาเพื่อนบ้าน

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **クロストーク (Kurosutōku):** Crosstalk
- **アグレッサー (Aguressā):** Aggressor (สัญญาณรบกวน)
- **ビクティム (Bikutimu):** Victim (สัญญาณที่ถูกรบกวน)
- **結合 (Ketsugō):** Coupling
- **配線間隔 (Haisen kankaku):** Trace spacing (ระยะห่างระหว่างเส้น)
- **層構成 (Sōkōsei):** Layer Stackup

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** ในปรากฏการณ์ Inductive Coupling กระแสที่ถูกเหนี่ยวนำบน Victim มีทิศทางอย่างไรเมื่อเทียบกับสัญญาณเปลี่ยนสถานะบน Aggressor?
**คำตอบ:** ตามกฎของเลนซ์ กระแสที่เกิดจาก Inductive Coupling จะไหลย้อนกลับทิศ (Backward) เมื่อเทียบกับทิศทางของกระแสหลักบน Aggressor (ไหลไปทาง Near-end ของ Victim)
