# Lesson 6: High-Speed Differential Pairs Routing (高速差動配線)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Differential pair routing เป็นหัวใจสำคัญของการส่งสัญญาณความเร็วสูง (เช่น USB 3.0, PCIe, HDMI) หลักการคือการส่งสัญญาณที่มีเฟสต่างกัน 180 องศา (D+ และ D-) เพื่อหักล้าง Common-mode noise 
- **Intra-pair skew (Phase tolerance):** ความยาวของสองเส้นใน pair เดียวกันต้องเท่ากันเป๊ะ (มักจะยอมให้ต่างกันได้ระดับ mil หรือน้อยกว่า) เพื่อไม่ให้เกิด Phase shift ซึ่งจะเปลี่ยนโหมดจาก Differential ไปเป็น Common-mode ทำให้เกิด EMI
- **Coupling:** ต้องรักษาระยะห่าง (Spacing) ระหว่าง D+ และ D- ให้สม่ำเสมอตลอดเส้นทาง เพื่อรักษา Differential Impedance (มักจะเป็น 90 หรือ 100 โอห์ม)
- **Return Path:** ระนาบอ้างอิง (Reference Plane) ต้องเป็นเนื้อเดียวกัน ห้ามลากผ่านรอยแยก (Split plane) เด็ดขาด

## ทริคหน้างาน OJT (On-the-Job Tricks)
- การทำ Length matching ควรทำที่บริเวณจุดที่เกิดความไม่เท่ากัน (Mismatch) ทันที ไม่ควรไปทดความยาวที่ปลายทาง
- หลีกเลี่ยงการใช้ Via กับสัญญาณ High-speed ให้มากที่สุด แต่ถ้าจำเป็นต้องเปลี่ยน Layer ต้องเพิ่ม Ground return via ไว้ข้างๆ เพื่อให้กระแสไหลกลับได้สะดวก (Return path continuity)
- การเลี้ยว (Bending) ควรใช้มุม 45 องศา หรือการทำ Arc (โค้ง) แทนมุม 90 องศา

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **等長配線 (Touchou haisen):** การเดินสายให้ยาวเท่ากัน (Length matching)
- **差動インピーダンス (Sadou inpiidansu):** Differential impedance
- **リターンパス (Ritaan pasu):** Return path
- **ベタ抜け (Beta nuke):** การเกิดช่องว่างในระนาบทองแดง (Void in copper pour) ซึ่งควรระวังไม่ให้รบกวน Return path

## ควิซท้ายบท (Quiz)
1. การเกิด Intra-pair skew ที่มากเกินไปส่งผลเสียอย่างไร?
2. ทำไมถึงต้องวาง Ground via ใกล้ๆ กับ Signal via เมื่อมีการเปลี่ยน Layer ของสัญญาณ Differential?
