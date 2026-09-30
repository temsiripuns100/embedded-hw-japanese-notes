# Lesson 8: Crosstalk Mitigation and Isolation (クロストーク対策とアイソレーション)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Crosstalk เกิดจากการเหนี่ยวนำทางสนามแม่เหล็ก (Inductive coupling - NEXT/FEXT) และสนามไฟฟ้า (Capacitive coupling) ระหว่างเส้นสัญญาณที่อยู่ใกล้กัน (Aggressor และ Victim)
- **Forward Crosstalk (FEXT) & Backward Crosstalk (NEXT):** ใน Microstrip จะมีทั้ง FEXT และ NEXT แต่ใน Stripline (ถูกประกบด้วย Plane บนล่าง) FEXT จะมีค่าเกือบเป็นศูนย์ ทำให้ Stripline ดีกว่าสำหรับสัญญาณที่วิ่งขนานกันยาวๆ
- **3W Rule:** เพื่อลด Crosstalk ระยะห่างระหว่างเส้นสัญญาณ (Center-to-center) ควรเป็น 3 เท่าของความกว้างเส้น (Width) ซึ่งจะช่วยลด Crosstalk ได้ถึง 70%
- **Orthogonal Routing:** ถ้าจำเป็นต้องเดินสัญญาณข้ามกันคนละ Layer ควรเดินในทิศทางตั้งฉากกัน (90 องศา) เพื่อให้พื้นที่ทับซ้อน (Coupling area) น้อยที่สุด

## ทริคหน้างาน OJT (On-the-Job Tricks)
- สัญญาณนาฬิกา (Clock) เป็น Aggressor ตัวร้ายที่สุด: ต้องพยายาม Isolate สัญญาณคล็อกให้ไกลจากสัญญาณอื่น (อาจใช้กฎ 5W หรือมี Ground guard ring)
- Guard Trace: การใช้เส้น Ground คั่นกลางสัญญาณความเร็วสูง ต้องมีการตี Ground via เป็นระยะๆ ตลอดแนว (Stitching vias) ถ้าระยะห่าง Via กว้างเกินไป Guard trace จะกลายเป็นเสาอากาศ (Antenna) แผ่คลื่นรบกวนเสียเอง

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **クロストーク (Kurosutooku):** Crosstalk
- **並行配線 (Heikou haisen):** Parallel routing (การเดินสายขนานกัน ซึ่งอาจทำให้เกิด Crosstalk)
- **ガードパターン (Gaado pataan):** Guard trace / Guard ring
- **直交配線 (Chokkou haisen):** Orthogonal routing (การเดินสายข้ามชั้นแบบตั้งฉาก)

## ควิซท้ายบท (Quiz)
1. การเดินสายแบบ Stripline ช่วยลด FEXT ได้เพราะสาเหตุใด?
2. ข้อควรระวังที่สุดในการใช้ Guard Trace คืออะไร?
