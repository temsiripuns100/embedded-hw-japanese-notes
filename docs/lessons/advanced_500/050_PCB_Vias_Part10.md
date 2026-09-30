# Lesson 50: Via Array, Stitching & Crosstalk Mitigation (シールドビアとリターンパス)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในโครงสร้าง PCB หลายชั้น (Multilayer PCB) เมื่อสัญญาณวิ่งข้ามชั้น (Layer Transition) สัญญาณขากลับ (Return Current) จะต้องหาทางวิ่งข้ามชั้นตามไปด้วย 
- **Return Path Vias (Ground Transfer Vias):** หากไม่มี Via เชื่อมต่อ Ground Plane สองชั้นอยู่ใกล้ๆ รู Via ของสัญญาณ (Signal Via) Return current จะต้องวิ่งอ้อมไปหาจุดเชื่อมที่ใกล้ที่สุด ทำให้เกิดพื้นที่ลูปขนาดใหญ่ (Large Loop Area) ส่งผลให้เกิด EMI (Electromagnetic Interference) และ Crosstalk
- **Shielding Vias (Picket Fence):** การสร้างรั้ว Via ตามแนวสายสัญญาณ (Trace) ความถี่สูง จะช่วยกักเก็บคลื่นแม่เหล็กไฟฟ้า (Electromagnetic fields) คล้ายคลึงกับ Coaxial Cable ป้องกันคลื่นรบกวนแผ่ออกไปหรือรับคลื่นแทรกซ้อน

## ทริคหน้างาน OJT (現場のコツ)
- **Spacing of Shielding Vias:** กฎเหล็ก (Rule of Thumb) ของการวาง Shielding Via คือระยะห่าง (Pitch) ระหว่าง Via ต้องน้อยกว่า $\lambda/10$ หรือ $\lambda/20$ ของความถี่สูงสุดที่มีอยู่ในสัญญาณนั้น (มักจะคิดรวมไปถึง Harmonic ที่ 3 หรือ 5 ของสัญญาณ Digital) หากห่างเกินไป คลื่นจะสามารถลอดออกไปได้ (Waveguide leakage)
- **Stitching near connectors:** บริเวณที่มีการเสียบสาย (Connector) หรือเปลี่ยนชั้นสัญญาณอย่างรุนแรง จำเป็นต้องทำ 検図 (Kenzu) ให้แน่ใจว่ามี Ground Stitching Vias วางอยู่ชิดกับ Signal Vias มากที่สุด โดยปกติในระดับ Senior เราจะวางเป็นแบบสมมาตร (Symmetrical) เพื่อรักษาเสถียรภาพของ Differential Mode

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **リターンパス (Ritaan Pasu / Return Path):** เส้นทางไหลกลับของกระแสไฟฟ้า
- **シールドビア (Shiirudo Bia / Shielding Via):** Via ที่ทำหน้าที่เป็นเกราะกำบังคลื่น
- **クロストーク (Kurosutooku / Crosstalk):** สัญญาณรบกวนข้ามสาย
- **差動ペア (Sadou Pea / Differential Pair):** สายสัญญาณแบบคู่ดิฟเฟอเรนเชียล
- **ノイズ対策 (Noizu Taisaku / Noise Countermeasure):** มาตรการป้องกัน/จัดการสัญญาณรบกวน
- **ビアピッチ (Bia Pitchi / Via Pitch):** ระยะห่างระหว่างศูนย์กลางรู Via

## ควิซท้ายบท (Quiz)
**Q:** เพื่อป้องกันไม่ให้คลื่นแม่เหล็กไฟฟ้าความถี่สูงรั่วไหลออกจากสายสัญญาณ (Trace) ระยะห่างระหว่าง Shielding Vias ควรถูกกำหนดโดยอ้างอิงจากอะไร?
1. ความกว้างของสายสัญญาณ
2. ต้องไม่เกิน 1/10 ถึง 1/20 ของความยาวคลื่น ($\lambda$) ของความถี่สูงสุดในระบบ
3. ต้องเท่ากับระยะห่างระหว่าง Layer (Dielectric thickness) พอดี
4. ต้องไม่เกิน 50 mil เสมอ

*(คำตอบที่ถูกต้อง: 2. ต้องไม่เกิน 1/10 ถึง 1/20 ของความยาวคลื่น ($\lambda$) เพื่อป้องกันการลอดผ่านของคลื่นความถี่สูง)*
