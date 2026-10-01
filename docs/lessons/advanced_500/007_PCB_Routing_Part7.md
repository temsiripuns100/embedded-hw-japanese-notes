# บทที่ 7: RF/Microwave PCB Routing - ระดับ Senior

## ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
สำหรับวงจรความถี่วิทยุ (RF) พฤติกรรมของสายสัญญาณจะเปลี่ยนเป็น Distributed Element การคำนวณ Transmission Line (เช่น Coplanar Waveguide, Microstrip) ต้องคำนึงถึง Dielectric Constant (Dk) และ Dissipation Factor (Df) ของวัสดุ PCB (เช่น Rogers, Teflon) อย่างยิ่ง การทำ Via Fencing (Grounded Vias) ตามขอบสาย RF ช่วยป้องกันการแพร่กระจายของคลื่นแม่เหล็กไฟฟ้าและการรบกวนระหว่างช่องสัญญาณ (Isolation) รัศมีการโค้งงอของสาย (Bend) ต้องใช้ Mitered Bend หรือเส้นโค้ง (Arc) เพื่อลด Mismatch ที่มุม

## ทริคหน้างาน OJT (現場のコツ)
- **RF Trace Clearance**: ระยะห่างจากสาย RF ถึง Ground Pour ควรคำนวณตาม Coplanar Waveguide Fencing ทั่วไปจะแนะนำให้ห่างอย่างน้อย 2-3 เท่าของความกว้างสาย (Trace Width)
- **Via Fencing Pitch**: ระยะห่างระหว่าง Ground Vias ที่ใช้บล็อกสัญญาณ ต้องน้อยกว่า $\lambda/10$ ของความถี่สูงสุดในระบบ เพื่อป้องกันไม่ให้คลื่นเล็ดลอดผ่านไปได้

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語 - けんずようご)
- **高周波 (Kōshūha):** High Frequency / ความถี่สูง
- **誘電率 (Yūdenritsu):** Dielectric Constant (Dk) / ค่าคงที่ไดอิเล็กทริก
- **誘電正接 (Yūden seisetsu):** Dissipation Factor (Df) / ค่าการสูญเสียในไดอิเล็กทริก
- **ビアフェンス (Bia fensu):** Via Fence / การตีกรอบด้วย Via
- **アイソレーション (Aisorēshon):** Isolation / การแยกสัญญาณไม่ให้กวนกัน

## ควิซท้ายบท (確認テスト)
1. ระยะห่างของ Via (Via Pitch) ในการทำ Via Fencing สำหรับ RF Board ควรมีค่าเท่าใด?
   a) มากกว่าความยาวคลื่น ($\lambda$)
   b) น้อยกว่า $\lambda/20$ ถึง $\lambda/10$ ของความถี่สูงสุด
   c) 50 mil เสมอ
   d) เท่ากับความหนาของบอร์ด

*(เฉลย: b - เพื่อให้กำแพง Via ทำงานเสมือนผนังทึบสำหรับความถี่นั้นๆ)*
