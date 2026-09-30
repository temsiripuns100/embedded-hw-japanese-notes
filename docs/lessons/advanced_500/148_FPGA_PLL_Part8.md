# Lesson 148: FPGA PLL Advanced - Part 8 (Spread Spectrum Clocking)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
**Spread Spectrum Clock Generation (SSCG)** คือเทคนิคการลดคลื่นแม่เหล็กไฟฟ้ารบกวน (EMI) โดยการมอดูเลตความถี่ของ PLL ให้แกว่งเป็นช่วงเล็กๆ (เช่น Down-spread -0.5%) พลังงานที่เคยกระจุกตัวอยู่ที่ความถี่หลักจะถูกกระจาย (Spread) ออกไป ทำให้ค่า Peak บน Spectrum Analyzer ลดลงและผ่าน EMI Test ได้ง่ายขึ้น

## 2. ทริคหน้างาน OJT (On-the-Job Tricks)
- **Timing Analysis Impact**: SSCG ทำให้คาบเวลา (Period) ของ Clock เปลี่ยนแปลงอยู่ตลอดเวลา ดังนั้นการทำ Static Timing Analysis (STA) ต้องเผื่อ Margin สำหรับความถี่ที่เร็วที่สุดเสมอ (Worst-case Period)
- **Interface Compatibility**: อย่าใช้ SSCG กับระบบเครือข่ายความเร็วสูงที่มี Clock Tolerance ต่ำๆ (เช่น Gigabit Ethernet, PCIe บางโหมด) เพราะจะทำให้ Receiver ฝั่งตรงข้ามเสีย Sync และเกิด Data Error (CRC Error)

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **スペクトラム拡散 (Supekutoramu Kakusan)**: Spread Spectrum
- **放射ノイズ (Housha Noizu)**: Radiated Noise / EMI
- **タイミング解析 (Taimingu Kaiseki)**: Timing Analysis
- **マージン (Maajin)**: Margin (ระยะเผื่อ)
- *"放射ノイズ対策でスペクトラム拡散を有効にする場合、タイミングマージンに注意してください。"* (กรณีเปิดใช้ Spread Spectrum เพื่อแก้ปัญหา Radiated Noise ให้ระวังเรื่อง Timing Margin ด้วย)

## 4. ควิซท้ายบท (Quiz)
**Q:** การใช้ SSCG แบบ Down-spread -1% จะมีผลกับ Setup Time หรือ Hold Time มากกว่ากัน?
**A:** Setup Time เพราะความถี่อาจจะเร็วขึ้น/ช้าลง (คาบสั้นลง) ในการตั้งค่าทั่วไปต้องวิเคราะห์ที่คาบเวลาสั้นที่สุดเสมอ
