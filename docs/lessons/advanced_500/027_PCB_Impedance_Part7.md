# Advanced PCB Impedance Part 7: Differential Impedance & Coupling (差動インピーダンスとカップリング)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
Differential Impedance (Zdiff) ไม่ได้มีค่าเท่ากับ 2 × Z0 (Single-ended) เสมอไป เนื่องจากมี Mutual Capacitance และ Mutual Inductance ระหว่างเส้นสัญญาณบวกและลบ 
ยิ่งระยะห่าง (Spacing) ระหว่างเส้นลดลง การจับคู่สัญญาณ (Coupling) จะยิ่งสูงขึ้น ทำให้ Zdiff ลดลง การออกแบบที่ยอดเยี่ยมต้องหาจุดสมดุลระหว่าง "Loose coupling" (ระยะห่างกว้าง ควบคุม Impedance ง่าย แต่กินพื้นที่) และ "Tight coupling" (ระยะห่างแคบ ประหยัดพื้นที่ ป้องกัน Noise ได้ดี แต่ถ้า Tolerance โรงงานเพี้ยนเพียง 0.5 mil ค่า Impedance จะหลุดสเปคทันที)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- ในพอร์ตความเร็วสูงเช่น USB 3.x หรือ PCIe ระวังการตีวงเลี้ยว (Bending/Corners) การใช้มุม 45 องศา หรือการลบมุมแบบโค้ง (Arc routing) จะช่วยรักษาระยะ Spacing ให้คงที่ได้มากกว่าการหักมุมแบบ 90 องศา 
- ในกรณีที่ต้องหนีบพินของชิป (Pin escape/Neck down) ที่มีระยะ Pitch แคบ ให้ชดเชยค่า Impedance ที่จุดนั้นด้วยการลดความกว้างของเส้นชั่วคราว เพื่อไม่ให้เกิด Zdiff Drop ที่คอขวด

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **差動信号 (Sadō shingō):** Differential signal
- **結合 (Ketsugō):** Coupling
- **配線間隔 (Haisen kankaku):** Trace spacing / Clearance
- **曲げ配線 (Mage haisen):** Bending routing / Trace corner
- **線幅 (Senhaba):** Trace width / Line width

## ควิซท้ายบท (Quiz)
**Q:** เมื่อระยะห่าง (Spacing) ระหว่างสายสัญญาณ Differential คู่หนึ่งลดลง (ชิดกันมากขึ้น) จะส่งผลต่อค่า Differential Impedance อย่างไร?
1. ค่า Differential Impedance เพิ่มขึ้น
2. ค่า Differential Impedance ลดลง
3. ค่า Differential Impedance คงที่ เพราะขึ้นกับเส้นกว้างอย่างเดียว
**Ans:** 2. ค่า Differential Impedance ลดลง (เนื่องจาก Mutual Coupling เพิ่มขึ้น)
