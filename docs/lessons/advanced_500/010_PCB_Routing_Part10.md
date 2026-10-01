# บทที่ 10: DFM / DFT for High-Density Interconnects (HDI) - ระดับ Senior

## ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
การออกแบบ HDI (High-Density Interconnect) เกี่ยวข้องกับ Microvias (Blind, Buried, Staggered, Stacked) กฎ DFM (Design for Manufacturing) และ DFT (Design for Testing) มีความเข้มงวดมาก Stack-up ต้องสมดุล (Symmetrical) เพื่อป้องกันบอร์ดโก่ง (Warpage) สัดส่วน Aspect Ratio ของ Microvia ควร $\leq 0.8:1$ การทำ Test points สำหรับการทดสอบ In-Circuit Test (ICT) ต้องวางแผนตั้งแต่เนิ่นๆ เพราะไม่มีพื้นที่เหลือให้วางในภายหลัง

## ทริคหน้างาน OJT (現場のコツ)
- **Stacked vs Staggered Vias**: ใน HDI หากหลีกเลี่ยง Stacked Microvias (เวียซ้อนทับกันตรงๆ) ได้ควรเลี่ยง เปลี่ยนไปใช้ Staggered Microvias แทน เพราะ Stacked Vias มีความเสี่ยงต่อการเกิดรอยร้าว (Microvia reliability issues) ขณะที่บอร์ดถูกความร้อนสูง (Reflow)
- **Test Points**: ในบอร์ดที่แน่นมากๆ (HDI) ให้ใช้ Test Vias หรือแม้กระทั่งเปิด Solder Mask บนสาย Trace เล็กน้อยเพื่อเป็นจุดจิ้ม Probe แต่ต้องระวังไม่ให้ใกล้กับอุปกรณ์ที่อาจลัดวงจร 

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語 - けんずようご)
- **製造性考慮設計 (Seizō-sei kōryo sekkei):** Design for Manufacturing (DFM)
- **テスト性考慮設計 (Tesuto-sei kōryo sekkei):** Design for Testing (DFT)
- **反り (Sori):** Warpage / การโก่งตัวของบอร์ด
- **止まり穴 (Tomari ana):** Blind Via (หรือใช้คำว่า ブラインドビア)
- **埋め込み穴 (Umekomi ana):** Buried Via (หรือใช้คำว่า ベリードビア)

## ควิซท้ายบท (確認テスト)
1. ในการออกแบบ HDI เหตุใด Staggered Microvias จึงมักถูกแนะนำให้ใช้มากกว่า Stacked Microvias?
   a) เพราะราคาถูกกว่ามาก
   b) เพราะมีความทนทาน (Reliability) สูงกว่า ลดความเสี่ยงจากการขยายตัวทางความร้อน (CTE mismatch) ที่ทำให้เกิดรอยร้าว
   c) เพราะใช้พื้นที่บนบอร์ดน้อยกว่า
   d) เพราะเครื่องจักรทั่วไปทำ Stacked Via ไม่ได้

*(เฉลย: b - Staggered via กระจายความเค้นได้ดีกว่า Stacked via ที่มีจุดต่อกันเป็นแกนเดียว ซึ่งเสี่ยงต่อการขาดเมื่อเจอความร้อน)*
