# PCB DFA Part 9: Flexible PCB (FPC) Assembly & Rigid-Flex Constraints

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การประกอบวงจรบนแผ่นพิมพ์โค้งงอได้ (FPC) มีความซับซ้อนกว่า Rigid PCB อย่างมาก เนื่องจากวัสดุฐาน (Polyimide) มีการขยายและหดตัว (Dimensional Stability ต่ำ)
- **Stiffener (補強板):** บริเวณที่มีการติดอุปกรณ์ SMT อย่างไอซีหรือคอนเนคเตอร์ จะต้องมีแผ่น Stiffener (เช่น FR4 หรือ Polyimide หนา) ติดอยู่ด้านหลังเพื่อป้องกันไม่ให้แผ่นโค้งงอขณะประกอบและบัดกรี ซึ่งจะทำให้จุดบัดกรีแตก (Solder Joint Cracking)
- **Teardrop & Fillet:** รอยต่อระหว่าง Trace กับ Pad บน FPC จะต้องทำ Teardrop เสมอ เพื่อลด Stress concentration ป้องกันทองแดงลอก (Pad Peeling) ระหว่างการบิดงอ

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Carrier / Pallet Design:** ในกระบวนการ SMT แผ่น FPC จะต้องถูกติดบน Magnetic Carrier หรือ Silicon Pallet ที่ทนความร้อนสูง การออกแบบ FPC Panel ต้องเว้นขอบ (Fiducial/Tooling hole) ให้พอดีกับ Pin บน Carrier 
- **Bake before use:** FPC ดูดความชื้นได้ดีมาก (Hygroscopic) ก่อนเข้าไลน์ SMT ต้องทำการอบ (Baking) เสมอ (เช่น 120C, 2-4 hrs) เพื่อไล่ความชื้น ป้องกันอาการบวมพอง (Delamination/Blistering) ตอนเข้า Reflow

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **補強板 (Hokyouban):** Stiffener / แผ่นเสริมความแข็งแรง
- **フレキ (Fureki):** Flex / Flexible PCB (ย่อมาจาก Flexible)
- **ティアドロップ (Tiadoroppu):** Teardrop / การทำทองแดงหยดน้ำที่จุดเชื่อมต่อ
- **剥離 (Hakuri):** Delamination / Peeling / การลอกออกหรือแยกชั้น
- **ベーキング (Beekingu):** Baking / การอบไล่ความชื้น

## ควิซท้ายบท (Quiz)
**Q:** ทำไมจึงต้องหลีกเลี่ยงการวาง Via บริเวณจุดที่เป็นโค้งงอ (Bending Area) ของ FPC?
A) ทำให้การส่งสัญญาณไฟฟ้าเร็วเกินไป
B) บริเวณที่มี Via จะเกิดความเค้น (Stress concentration) สูง ทำให้วงจรมีโอกาสขาด (Crack) ได้ง่ายเมื่อถูกงอ
C) เปลืองพื้นที่
**เฉลย:** B) รูเจาะ (Via) ทำให้เกิดจุดอ่อนทางโครงสร้าง (Stress concentration) จึงห้ามวางใน Bending zone เด็ดขาด
