# 002 PCB Routing Part 2: Differential Pair Routing (差動配線)

## ทฤษฎีวิศวกรรมเชิงลึก (In-Depth Engineering Theory)
Differential Signalling ใช้การส่งสัญญาณคู่ที่มีเฟสตรงข้ามกัน (Inverting & Non-Inverting) ข้อดีคือ Common-Mode Rejection Ratio (CMRR) ที่สูง ทำให้ทนต่อ Noise ภายนอกได้ดี
- **Differential Impedance ($Z_{diff}$)**: การควบคุมความกว้าง (Width) และระยะห่าง (Spacing) ระหว่างคู่สายเป็นสิ่งสำคัญที่สุด ปกติจะตั้งเป้าที่ $100\Omega$ หรือ $90\Omega$ (เช่น USB, PCIe)
- **Phase Tolerance**: ความคลาดเคลื่อนของเฟส (Skew) ระหว่าง P (Positive) และ N (Negative) ต้องอยู่ในเกณฑ์ที่กำหนด (เช่น < 5ps) หากเกิด Skew จะทำให้เกิดการแปลงสัญญาณจาก Differential-mode เป็น Common-mode (Mode Conversion) ซึ่งเป็นสาเหตุของ EMI

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **Phase Matching ที่จุดเกิดปัญหา**: หากมีการเลี้ยว (Corner) ขาที่อยู่ด้านในจะสั้นกว่าขาด้านนอก ต้องทำการชดเชยความยาว (Length Compensation) ทันทีที่จุดนั้น (หรือให้ใกล้ที่สุด) ไม่ควรไปชดเชยที่ปลายทาง
- **รักษา Coupling ให้สม่ำเสมอ**: หลีกเลี่ยงการแยกคู่สายออกจากกัน (Uncoupling) เพื่อหลบ Via หรือ Component หากเลี่ยงไม่ได้ ต้องจำกัดระยะทางที่ Uncouple ให้น้อยที่สุด
- **Symmetry**: การออกแบบต้องมีความสมมาตร (Symmetry) ทั้งในแง่ของการจัดวางเส้นทาง และจำนวน Via ที่ใช้

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **差動配線 (Sadō Haisen)**: Differential pair routing
- **等長配線 (Tōchō Haisen)**: Length matching / Equal length routing
- **ペア内スキュー (Pea-nai Sukyū)**: Intra-pair skew (ความต่างความยาวในคู่เดียวกัน)
- **結合 (Ketsugō)**: Coupling
- **ミスマッチ (Misumacchi)**: Mismatch

## ควิซท้ายบท (Quiz)
**คำถาม:** การทำ Length Compensation สำหรับ Differential Pair เมื่อมีการเลี้ยว ควรทำที่ตำแหน่งใด?
1. ใกล้กับ IC ตัวรับ (Receiver) มากที่สุด
2. ทันทีบริเวณที่เกิดความต่างของความยาว (บริเวณมุมเลี้ยว)
3. ปล่อยไว้ไม่ต้องแก้ หากต่างกันไม่เกิน 10mm
**เฉลย:** ข้อ 2
