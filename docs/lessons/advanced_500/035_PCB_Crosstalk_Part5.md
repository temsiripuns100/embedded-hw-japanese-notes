# Lesson 035: PCB Crosstalk - Part 5: SI Simulation & Kenzu Checklist (SIシミュレーションと検図リスト)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การประเมิน Crosstalk ในปัจจุบัน ต้องใช้ 3D Electromagnetic (EM) Solver (เช่น Ansys HFSS, ADS, HyperLynx) เพื่อสกัดพารามิเตอร์ S-Parameters (Touchstone format) โดยดูค่า **Insertion Loss (S21/S12)** และ **Isolation/Crosstalk (S31, S41)**
Crosstalk ที่ยอมรับได้มักตั้งเป้าไว้ที่ < -40dB ถึง -50dB ที่ความถี่ Nyquist ของสัญญาณ หากกราฟ Crosstalk มีการแกว่ง (Resonance/Dip) มักบ่งชี้ว่ามีปัญหา Impedance Mismatch, Via stub ยาวเกินไป หรือ Return path แย่

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
**Kenzu (検図) Checklist สำหรับระดับ Senior:**
1. ตรวจสอบ "プレーン跨ぎ (Plane Matagi)" หรือรอยต่อ Split plane ใต้ High-speed routing ทุกเส้น
2. เช็ค Spacing rules ว่า 3W/5W ถูก Apply ใน Rule Manager ของ EDA tool แล้วหรือยัง
3. สุ่มตรวจ Via ของ Guard trace ว่าเว้นระยะ (Pitch) ถี่กว่า $\lambda/10$ ของความถี่สูงสุดของสัญญาณหรือไม่
4. Backdrill ถูกกำหนดใช้กับ Via ที่มี Stub ยาวสำหรับสัญญาณ > 10 Gbps หรือไม่

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **シグナルインテグリティ (Shigunaru Integuriti):** Signal Integrity (SI)
- **スタブ (Sutabu):** Stub (ส่วนเกินของ Via ที่ทำให้เกิด Resonance)
- **バックドリル (Bakku Doriru):** Backdrill (การเจาะเอา Stub ออก)
- **検図リスト (Kenzu Risuto):** Design Review Checklist
- **歩留まり (Budomari):** Yield (อัตราผลตอบแทน/ความสำเร็จในการผลิต)

## ควิซท้ายบท (Quiz)
**Q1:** พารามิเตอร์ใดใน S-Parameters ที่ใช้วัดระดับ Crosstalk ระหว่างพอร์ต 1 และพอร์ต 3?
**A:** S31
**Q2:** การทำ Backdrill มีวัตถุประสงค์เพื่ออะไร?
**A:** เพื่อกำจัด Via stub ที่ไม่ได้ใช้งาน ซึ่งเป็นตัวทำให้เกิด Resonance ในย่านความถี่สูง
