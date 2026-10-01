# Advanced PCB Impedance Part 6: Single-Ended & Microstrip vs Stripline (シングルエンドとマイクロストリップ/ストリップライン)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
Characteristic Impedance (Z0) ของสัญญาณ Single-Ended เกิดจากอัตราส่วนของ Inductance และ Capacitance ต่อความยาว (Z0 = √(L/C)) 
โครงสร้าง Microstrip (อยู่ผิวนอกบอร์ด) คลื่นแม่เหล็กไฟฟ้า (EM Wave) ส่วนหนึ่งกระจายไปในอากาศ ส่วนหนึ่งอยู่ในเรซิน ทำให้ความเร็วในการเดินทาง (Propagation Delay) เร็วกว่า แต่เกิดการสูญเสียทางรังสี (Radiated Loss) และ EMI ได้ง่าย
โครงสร้าง Stripline (อยู่ชั้นในบอร์ด ขนาบด้วย Plane) EM Wave จะถูกจำกัดอยู่ใน Dielectric 100% ทำให้มี Propagation Delay คงที่ ช่วยลด EMI แต่มีปัญหา Dielectric loss สูงกว่า Microstrip และต้องการความกว้างทองแดงที่เล็กกว่าเพื่อให้ได้ Impedance เท่ากัน ซึ่งผลิตยากกว่า

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- สัญญาณความเร็วสูงมากๆ (เช่น RF หรือ Clock สำคัญ) แนะนำให้ใช้ Stripline routing แม้จะหน่วงกว่า แต่สัญญาณสะอาดและไม่แผ่รังสีรบกวน 
- เมื่อต้องเปลี่ยนชั้น (Via) จาก Microstrip เป็น Stripline จะมี Impedance Discontinuity ที่ตัว Via หากสัญญาณวิ่งที่ > 10 Gbps จำเป็นต้องทำ Via Back-drilling หรือ Blind Via เพื่อตัดส่วน Stub ทิ้ง (Stub resonance)

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **シングルエンド (Shinguru endo):** Single-ended
- **マイクロストリップ (Maikurosutorippu):** Microstrip
- **ストリップライン (Sutorippurain):** Stripline
- **特性インピーダンス (Tokusei inpīdansu):** Characteristic impedance (Z0)
- **放射ノイズ (Hōsha noizu):** Radiated noise / EMI

## ควิซท้ายบท (Quiz)
**Q:** ข้อใดคือลักษณะสำคัญของโครงสร้าง Stripline เมื่อเปรียบเทียบกับ Microstrip?
1. Propagation Delay จะเร็วกว่า Microstrip
2. คลื่นแม่เหล็กไฟฟ้า (EM Field) ถูกล้อมรอบด้วย Dielectric อย่างสมบูรณ์ ทำให้ความเร็วคงที่
3. มีความเสี่ยงต่อการแพร่กระจายของคลื่น (EMI) สูงกว่า
**Ans:** 2. คลื่นแม่เหล็กไฟฟ้า (EM Field) ถูกล้อมรอบด้วย Dielectric อย่างสมบูรณ์ ทำให้ความเร็วคงที่
