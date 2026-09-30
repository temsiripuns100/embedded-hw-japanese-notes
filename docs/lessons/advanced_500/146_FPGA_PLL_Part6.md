# Lesson 146: FPGA PLL Advanced - Part 6 (Jitter Analysis and Mitigation)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในระดับ Senior การเข้าใจ PLL ไม่ใช่แค่การคูณ/หารความถี่ แต่คือการจัดการกับ **Jitter (ジッタ)** และ **Phase Noise (位相ノイズ)**
- **Period Jitter**: ความแปรปรวนของคาบเวลาของคลื่น 1 ไซเคิล
- **Cycle-to-Cycle Jitter**: ความแตกต่างของคาบเวลาระหว่างไซเคิลที่ติดกัน
- **Long-term Jitter**: ความคลาดเคลื่อนสะสมเมื่อเวลาผ่านไปนานๆ
แหล่งกำเนิดแบ่งเป็น Intrinsic (จากตัว PLL เอง เช่น Thermal Noise) และ Extrinsic (จากภายนอก เช่น Power Supply Noise) การคำนวณ Timing Margin ต้องนำ Jitter เหล่านี้มาหักลบออกจาก Data Valid Window เสมอ

## 2. ทริคหน้างาน OJT (On-the-Job Tricks)
- **Power Supply Filtering**: ขา VCC_PLL ต้องแยก Filter ด้วย Ferrite Bead และ Capacitor ค่าต่ำๆ (เช่น 0.1uF // 0.01uF) วางชิดขา IC ที่สุด
- **Clock Pin Routing**: สัญญาณ Clock ขาเข้าต้องเข้าผ่าน Dedicated Clock Pin (เช่น MRCC/SRCC ใน Xilinx) ห้ามเข้าผ่าน General Purpose I/O เด็ดขาดเพราะจะเกิด Routing Jitter มหาศาล

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ジッタ (Jitta)**: Jitter ความคลาดเคลื่อนของสัญญาณนาฬิกา
- **位相ノイズ (Ishou Noizu)**: Phase Noise
- **電源ノイズ (Dengen Noizu)**: Power Supply Noise (ต้องระวังใน 検図)
- **フェライトビーズ (Feraito Biizu)**: Ferrite Bead (อุปกรณ์กรองความถี่สูง)
- **検図 (Kenzu)**: การตรวจแบบ/รีวิว Design (Design Review)
- *"PLLの電源ラインにフェライトビーズが入っているか検図してください。"* (กรุณาตรวจแบบว่ามี Ferrite bead ในไลน์ไฟเลี้ยง PLL หรือไม่)

## 4. ควิซท้ายบท (Quiz)
**Q:** การใช้ I/O ธรรมดารับสัญญาณ Clock เข้า PLL จะส่งผลเสียหลักๆ คืออะไร?
**A:** ทำให้เกิด Routing Jitter ที่สูงมาก และอาจทำให้ PLL ไม่สามารถ Lock สัญญาณได้เสถียร
