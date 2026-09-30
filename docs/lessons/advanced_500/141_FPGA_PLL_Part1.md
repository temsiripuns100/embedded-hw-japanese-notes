# FPGA PLL Deep Dive - Part 1: PLL Fundamentals and Loop Dynamics

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
Phase-Locked Loop (PLL) เป็นระบบควบคุมแบบป้อนกลับ (Feedback Control System) ที่มีเป้าหมายในการรักษา Phase และ Frequency ของสัญญาณ Output ให้ตรงกับสัญญาณ Input (Reference Clock).
ในระดับ Senior Engineer เราไม่ได้มองแค่ block ดำๆ ที่คูณ/หารความถี่ แต่มองถึง **Transfer Function** และ **Loop Dynamics**.
องค์ประกอบหลักของ Analog PLL ใน FPGA:
1. **Phase-Frequency Detector (PFD)**: ตรวจจับความต่างของเฟสและความถี่ $K_{pd}$
2. **Charge Pump (CP)**: แปลงสถานะจาก PFD เป็นกระแสไฟฟ้า $I_{cp}$
3. **Loop Filter (LF)**: กรองสัญญาณความถี่สูงออก (Low-pass filter) เพื่อสร้างแรงดันควบคุม (Control Voltage) ให้กับ VCO. การออกแบบ Filter เป็นตัวกำหนด Bandwidth, Damping Factor ($\zeta$) และ Loop Stability.
4. **Voltage-Controlled Oscillator (VCO)**: สร้างความถี่ตามแรงดันควบคุม มีค่า Gain $K_{vco}$
5. **Feedback Divider (N)**: หารความถี่กลับไปเทียบกับ PFD

สมการ Closed-Loop Transfer Function:
$$H(s) = \frac{\theta_{out}(s)}{\theta_{ref}(s)} = \frac{K_{pd} K_{vco} F(s) / N}{s + K_{pd} K_{vco} F(s) / N}$$

## 2. ทริคหน้างาน OJT (現場のOJTテクニック)
- **การเลือก Loop Bandwidth**: ถ้า Reference Clock มี Jitter สูง ให้เลือก Low Loop Bandwidth เพื่อให้ PLL ทำหน้าที่เป็น Jitter Attenuator แต่ถ้าระบบต้องการ Tracking ความถี่ที่เปลี่ยนไปอย่างรวดเร็ว (เช่น Spread Spectrum Clocking) ต้องเลือก High Loop Bandwidth
- **VCO Tuning Range**: ตรวจสอบเสมอว่า VCO ทำงานอยู่ในช่วงเชิงเส้นที่ดีที่สุดใน Datasheet เพราะถ้าหลุดขอบ (Saturation) จะเกิด Jitter มหาศาล
- **Lock Time**: ในระบบที่ทำ Power Management มีการเปิด/ปิด PLL บ่อยๆ (Dynamic Clock Gating) ต้องคำนวณ Lock Time ให้รอบคอบ หากวงจรดึง Clock ไปใช้ก่อน PLL Lock (LOCK signal = 1) อาจทำให้ระบบค้าง (Hang) ได้ทันที

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語)
- **位相同期回路 (いそうどうきかいろ, Isou Douki Kairo)**: Phase-Locked Loop (PLL)
- **逓倍 (ていばい, Teibai)**: การคูณความถี่ (Multiplication)
- **分周 (ぶんしゅう, Bunshuu)**: การหารความถี่ (Division)
- **発振器 (はっしんき, Hasshinki)**: Oscillator
- **同期外れ (どうきはずれ, Douki Hazure)**: Loss of Lock (PLL หลุดจากสถานะ Lock)
- **帯域幅 (たいいきはば, Taiiki Haba)**: Bandwidth

## 4. ควิซท้ายบท (理解度チェック)
**Q1:** หากต้องการให้ PLL กรอง Jitter จาก Reference Clock ได้ดีขึ้น ควรปรับพารามิเตอร์ใด?
A) ลด Feedback Divider (N)
B) เพิ่ม Loop Bandwidth
C) ลด Loop Bandwidth
D) เพิ่ม VCO Gain

*เฉลย:* C) ลด Loop Bandwidth (帯域幅を狭くする) เพื่อให้ PLL กรองสัญญาณรบกวนความถี่สูงจากฝั่ง Input ออกไป
