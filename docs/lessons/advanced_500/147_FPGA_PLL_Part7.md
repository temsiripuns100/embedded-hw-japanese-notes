# Lesson 147: FPGA PLL Advanced - Part 7 (Dynamic Reconfiguration)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
**Dynamic Reconfiguration** (หรือ DRP - Dynamic Reconfiguration Port ใน Xilinx) คือเทคนิคการเปลี่ยนค่าพารามิเตอร์ของ PLL (M, D, O dividers, Phase Shift) ในขณะที่ระบบกำลังทำงานอยู่ (Run-time) โดยไม่ต้องโหลด Bitstream ใหม่ วิธีนี้ใช้เมื่อระบบต้องรองรับหลายมาตรฐานความถี่ (เช่น Video format ต่างๆ) การเข้าถึง DRP จะทำผ่าน AXI interface หรือ Register โดยตรง ซึ่งต้องระวังเรื่อง Timing และสถานะของ VCO

## 2. ทริคหน้างาน OJT (On-the-Job Tricks)
- **State Machine Management**: การเขียนค่าใหม่ลง DRP ต้องควบคุมด้วย State Machine เสมอ ห้ามเขียนรัวๆ
- **Reset & Lock**: หลังจากการปรับค่าผ่าน DRP สำเร็จ **ต้อง** สั่ง Reset PLL และรอสัญญาณ `LOCKED` (ロック信号) กลับมาเป็น High ก่อนถึงจะปล่อยให้วงจร Downstream ทำงานต่อ ไม่เช่นนั้นจะเกิด Metastability จาก Clock ที่ยังไม่นิ่ง
- **Glitch-less Switch**: หากมีหลาย Clock ให้ใช้ BUFGMUX ในการสลับเพื่อไม่ให้เกิด Glitch

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **動的再構成 (Douteki Saikousei)**: Dynamic Reconfiguration
- **ロック信号 (Rokku Shingou)**: Lock Signal (สัญญาณว่า PLL นิ่งแล้ว)
- **位相シフト (Ishou Shifuto)**: Phase Shift (การเลื่อนเฟส)
- **ステートマシン (Suteeto Mashin)**: State Machine
- *"動的再構成のステートマシンが正しくロック信号を待っているか確認して。"* (ช่วยยืนยันหน่อยว่า State Machine ของการทำ Dynamic Reconfiguration ได้รอ Lock Signal อย่างถูกต้องแล้ว)

## 4. ควิซท้ายบท (Quiz)
**Q:** หลังจากเขียนค่า DRP เสร็จ ขั้นตอนที่สำคัญที่สุดก่อนใช้งาน Clock คืออะไร?
**A:** ต้อง Reset PLL และรอให้ Lock Signal แจ้งสถานะ Locked ก่อนใช้งาน
