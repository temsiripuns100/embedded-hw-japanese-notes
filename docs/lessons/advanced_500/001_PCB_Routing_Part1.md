# 001 PCB Routing Part 1: High-Speed Trace Routing (高速配線)

## ทฤษฎีวิศวกรรมเชิงลึก (In-Depth Engineering Theory)
ในการออกแบบวงจรความถี่สูง (High-Speed PCB Design) สิ่งสำคัญคือการควบคุม Impedance และลด Signal Integrity (SI) degradation. 
สัญญาณที่วิ่งใน Trace ไม่ใช่แค่กระแสไฟฟ้า แต่เป็นคลื่นแม่เหล็กไฟฟ้า (Electromagnetic Wave) ที่เดินทางผ่าน Dielectric ระหว่าง Trace และ Reference Plane
- **Characteristic Impedance ($Z_0$)**: ขึ้นอยู่กับความกว้างของ Trace (w), ความหนาของทองแดง (t), ความหนาของ Dielectric (h) และ Dielectric Constant ($D_k$)
- **Return Path**: สัญญาณความถี่สูงจะวิ่งกลับในเส้นทางที่มี Inductance ต่ำที่สุด (Least Inductance Path) ซึ่งมักจะอยู่ใต้ Trace พอดีใน Reference Plane หาก Reference Plane มีรอยแยก (Split Plane) จะเกิด Return Path Discontinuity ทำให้เกิด EMI และ Crosstalk

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **อย่าข้าม Split Plane**: หากจำเป็นต้องข้าม ให้ใช้ Stitching Capacitor เพื่อสร้างเส้นทาง Return Path
- **Length Matching**: การทำ Length matching หรือ Tuning (蛇行配線 - Meandering) ควรทำใกล้กับต้นทางของความไม่สมดุล (Mismatch source) มากที่สุด 
- **หลีกเลี่ยงมุม 90 องศา**: ถึงแม้ผลกระทบทาง SI ในความถี่ต่ำๆ จะน้อย แต่ในแง่ของ DFM (Design for Manufacturing) มุมแหลมสามารถเป็นจุดรวมตัวของน้ำยาเคลือบ (Acid Trap) แนะนำให้ใช้มุม 45 องศา หรือการโค้ง (Arc) แทนในสัญญาณที่เร็วกว่า 10 Gbps

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **高速配線 (Kōsoku Haisen)**: High-speed routing (การเดินสายความถี่สูง)
- **インピーダンス整合 (Inpīdansu Seigō)**: Impedance matching
- **リターンパス (Ritān Pasu)**: Return path
- **ベタ層 (Beta-sō)**: Solid plane / Copper pour (เพลนทองแดงเต็ม)
- **スリット跨ぎ (Suritto Matagi)**: Routing over a split plane (การเดินสายข้ามรอยแยกของเพลน) - *ข้อห้ามสำคัญ*

## ควิซท้ายบท (Quiz)
**คำถาม:** เหตุใดการเดินสายสัญญาณความถี่สูงข้าม Split Plane จึงเป็นข้อห้ามในกระบวนการ 検図 (Kenzu)?
1. ทำให้บอร์ดมีน้ำหนักเพิ่มขึ้น
2. ทำให้เกิด Return Path Discontinuity ซึ่งเพิ่ม Loop Area และ EMI
3. ทำให้การกัดกรด (Etching) ทำได้ยาก
**เฉลย:** ข้อ 2
