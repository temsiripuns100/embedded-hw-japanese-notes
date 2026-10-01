# บทที่ 6: High-Speed Digital Routing (DDR, PCIe) - ระดับ Senior

## ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
การเดินสายสำหรับสัญญาณ High-Speed (เช่น DDR4/5, PCIe Gen4/5) ต้องคำนึงถึง Signal Integrity (SI) เป็นหลัก การควบคุม Impedance (特性インピーダンス) ต้องแม่นยำ ทั้ง Single-ended (50Ω) และ Differential (85Ω/100Ω) การทำ Length Matching หรือ Delay Matching ต้องคิดถึง Propagation Delay ที่ต่างกันในชั้นผิว (Microstrip) และชั้นใน (Stripline) รวมถึงผลกระทบจาก Fiber Weave Effect (ガラス織り効果) ของวัสดุ FR4 ที่ความถี่สูง ซึ่งอาจทำให้เกิด Skew ระหว่างคู่สัญญาณ 

## ทริคหน้างาน OJT (現場のコツ)
- **การเดินสาย Differential Pair**: ระวังการแตกคู่ (Uncoupling) เมื่อผ่าน Via หรือ BGA breakout ให้รักษาช่องว่างให้สม่ำเสมอ หากต้องหลบ Via ให้ชดเชยความยาวทันทีที่จุดเกิด Skew (Phase Matching) ไม่ใช่ไปชดเชยที่ปลายสาย
- **Return Path**: ห้ามเดินสายข้ามรอยแยก (Split Plane) ของ Ground โดยเด็ดขาด (リターンパスの分断) หากจำเป็นจริงๆ ต้องมี Stitching Capacitor ใกล้ๆ 

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語 - けんずようご)
- **等長配線 (Tōchō haisen):** Length Matching / การทำให้สายยาวเท่ากัน
- **特性インピーダンス (Tokusei inpīdansu):** Characteristic Impedance / อิมพีแดนซ์เฉพาะ
- **クロストーク (Kurosutōku):** Crosstalk / สัญญาณรบกวนข้ามสาย
- **リターンパス (Ritān pasu):** Return Path / เส้นทางไหลกลับของกระแส
- **ガラス織り (Garasu ori):** Glass weave / ลายทอของไฟเบอร์กลาส

## ควิซท้ายบท (確認テスト)
1. การชดเชยความยาว (Phase Matching) ใน Differential Pair ควรทำที่ตำแหน่งใด?
   a) ที่ปลายสายฝั่ง Receiver
   b) ที่ต้นสายฝั่ง Transmitter
   c) ใกล้กับจุดที่เกิดความไม่สมดุล (Mismatch) มากที่สุด
   d) ตรงกลางสายพอดี

*(เฉลย: c - เพื่อลดโอกาสการเกิด Common-mode noise สะสมในสาย)*
