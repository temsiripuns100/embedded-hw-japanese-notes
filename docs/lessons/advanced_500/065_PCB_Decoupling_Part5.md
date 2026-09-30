# Lesson 065: PCB Decoupling Part 5 - Simulation, Measurement, and Troubleshooting EMI/EMC

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การตรวจสอบผลลัพธ์ของการออกแบบ PDN ในระดับสูง จำเป็นต้องใช้ Simulation tools เช่น HyperLynx PI, Sigrity, หรือ SIwave เพื่อดู Z-parameter (Impedance Profile) ว่าอยู่ต่ำกว่า Target Impedance ในช่วงความถี่เป้าหมายหรือไม่
และหน้างานจริง ต้องใช้ Oscilloscope หรือ Vector Network Analyzer (VNA) ในการวัด
การเกิด EMI มักมีความเชื่อมโยงกับ PDN ที่ไม่ดี เมื่อมี Noise กระเพื่อมบน Power Plane มันสามารถ Couple ไปยังสายสัญญาณ หรือแผ่กระจายออกไปทางขอบบอร์ด (Edge Radiation) หรือแม้กระทั่งทำให้สายเคเบิลที่ต่อกับบอร์ดทำตัวเป็นเสาอากาศ (Common Mode Radiation) การแก้ Decoupling ให้ดี คือด่านแรกและด่านสำคัญที่สุดในการปราบ EMI

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Sniffing for Trouble:** ใช้ Near-field Probe (Magnetic & Electric Probes) จิ้มดูตาม IC และตามตัว Capacitor ถ้าพบว่า Noise แถวๆ C มีค่าสูงกว่าปกติ อาจเป็นไปได้ว่า $L_{loop}$ ตรงนั้นสูงเกินไป หรือ C ค่าไม่เหมาะสม (เกิด Anti-resonance)
- **Ferrite Bead - ดาบสองคม:** อย่าใช้ Ferrite Bead กั้นระหว่าง Power หลักกับ VCC ของ IC พร่ำเพรื่อ! ในความถี่สูง Ferrite Bead มีสภาพเป็น Inductor กีดขวางการดึงกระแสฉับพลันของ IC ทำให้ Voltage Drop รุนแรงกว่าเดิม ให้ใช้เฉพาะกรณีป้องกัน Noise จาก Analog/RF หรือตาม Data sheet ระบุอย่างเจาะจงเท่านั้น
- **PDN Target Impedance Test:** ในการวัด PDN Impedance ด้วย VNA ต้องใช้ 2-Port Shunt-Thru Measurement เพราะ 1-Port ทั่วไปใช้วัด Impedance ต่ำระดับมิลลิโอห์มไม่ไหว (ค่า Error จากสายและ Probe จะกลบหมด)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **シミュレーション (Shimyureeshon):** Simulation
- **実測 (Jissoku):** Actual Measurement
- **ノイズ対策 (Noizu Taisaku):** Noise Countermeasure
- **フェライトビーズ (Feraito Biizu):** Ferrite Bead
- **放射ノイズ (Housha Noizu):** Radiated Noise / EMI

## ควิซท้ายบท (Quiz)
1. ทำไมการใส่ Ferrite Bead อนุกรมที่ขา Power ของ High-Speed Digital IC จึงมักจะทำให้เกิดปัญหา Signal Integrity (SI)?
2. วิธีการวัด PDN Impedance ที่มีค่าต่ำมาก (ระดับมิลลิโอห์ม) ด้วย VNA อย่างถูกต้อง เรียกว่าวิธีอะไร?
