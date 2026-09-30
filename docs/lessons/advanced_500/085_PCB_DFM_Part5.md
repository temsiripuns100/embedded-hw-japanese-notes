# บทที่ 85: PCB DFM Part 5 - การออกแบบเพื่อการประกอบ (DFA - Design for Assembly)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
DFA คือการนำบอร์ดที่ผลิตเสร็จมาใส่ชิ้นส่วนประกอบ การจัดวาง Component Orientation มีผลต่อ Wave Soldering อย่างมาก สำหรับชิ้นส่วน SMD เช่น SOIC, ทิศทางที่วิ่งผ่านคลื่นตะกั่วต้องตั้งฉากกับคลื่น เพื่อป้องกัน Shadow effect และ Solder bridging 
Profile อุณหภูมิในเตา Reflow จะถูกรบกวนได้ถ้าเราวางชิ้นส่วนที่มี Thermal mass ต่างกันมาก (เช่น ชิปขนาดใหญ่ติดกับตัวต้านทาน 0402) อาจเกิดปรากฏการณ์ Tombstoning (ตัวต้านทานกระดกขึ้น)

## ทริคหน้างาน OJT (OJT Tricks)
- เมื่อออกแบบ Stencil ให้ใช้เทคนิค Aperture modification เช่นทำ Home-plate หรือ Reduction เพื่อลดปริมาณตะกั่วในชิ้นส่วนที่มีความเสี่ยงต่อ Solder balling
- ควรเว้นระยะ Component-to-Component อย่างน้อย 0.5 mm เพื่อให้มีพื้นที่สำหรับ Inspection (AOI/AXI) และ Rework 
- การกระจายความร้อนของบอร์ดในเตาอบต้องสม่ำเสมอ พยายามอย่าวาง IC ใหญ่ๆ กองรวมกันที่มุมเดียวของบอร์ด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **実装性考慮設計 (Jissousei Kouryo Sekkei):** DFA (Design for Assembly)
- **フロー槽 / 波打ち半田 (Furoo Sou / Namiuchi Handa):** Wave Soldering
- **リフロー (Rifuroo):** Reflow Soldering
- **マンハッタン現象 / ツームストーン (Manhattan Genshou / Tsuumusutoon):** Tombstoning (ปรากฏการณ์ชิ้นส่วนกระดก)
- **メタルマスク (Metaru Masuku):** Stencil (สเตนซิลสำหรับปาดตะกั่ว)

## ควิซท้ายบท (Quiz)
Q1: ปรากฏการณ์ Tombstoning ในการบัดกรีแบบ Reflow มักเกิดจากสาเหตุใด?
A) ชิ้นส่วนมีความร้อนไม่เท่ากันที่ปลายทั้งสองด้าน ทำให้แรงตึงผิวของตะกั่วดึงชิ้นส่วนกระดกขึ้น (Correct)
B) เครื่อง Pick and Place วางชิ้นส่วนเบี้ยว
C) อุณหภูมิเตาอบต่ำเกินไป
D) ทองแดงบนบอร์ดละลาย
