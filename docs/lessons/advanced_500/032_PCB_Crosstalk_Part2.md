# Lesson 032: PCB Crosstalk - Part 2: Inductive Coupling & Return Path (誘導結合とリターンパス)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
นอกจาก Capacitive แล้ว ยังมี **Inductive Coupling (誘導結合)** เกิดจาก Mutual Inductance ($L_m$) เมื่อ Aggressor มีการเปลี่ยนแปลงกระแส ($di/dt$) จะเหนี่ยวนำให้เกิดแรงดัน $V_{crosstalk} = L_m \frac{di}{dt}$ บน Victim net 
สิ่งสำคัญที่สุดในการลด $L_m$ คือการควบคุม **Return Path** ให้กระแสไหลกลับอยู่ใกล้ใต้ Trace มากที่สุด (เช่น Solid Ground Plane) หาก Return path มีช่องโหว่ (Split plane) Loop area จะกว้างขึ้น ทำให้ $L_m$ พุ่งสูงขึ้นมหาศาล

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Solid Plane Rule:** ห้ามเดินสัญญาณ High-speed ข้าม Split plane เด็ดขาด หากเลี่ยงไม่ได้ ต้องใส่ Stitching capacitor คร่อม Split นั้นเพื่อให้ Return current ไหลผ่านได้ที่ความถี่สูง
- **Orthogonal Routing:** หากสัญญาณความเร็วสูงต้องเดินบนเลเยอร์ที่ติดกัน (Adjacent layers) ให้เดินสายตั้งฉากกัน (Orthogonal) เพื่อลดพื้นที่ทับซ้อนและ Mutual Inductance

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **誘導結合 (Yuudou Ketsugou):** Inductive Coupling
- **リターンパス (Ritaan Pasu):** Return Path
- **スプリット (Supuritto):** Split (plane)
- **直交配線 (Chokkou Haisen):** Orthogonal routing (การเดินสายตั้งฉาก)
- **プレーン跨ぎ (Pureen Matagi):** Routing crossing a split plane (เป็นข้อห้าม)

## ควิซท้ายบท (Quiz)
**Q1:** สาเหตุหลักที่ทำให้ Mutual Inductance ระหว่างสัญญาณเพิ่มขึ้นอย่างมากคืออะไร?
**A:** การที่ Return Path ไม่สมบูรณ์ (เช่น มี Split plane) ทำให้ Loop Area ใหญ่ขึ้น
**Q2:** การเดินสายแบบ 直交配線 (Orthogonal routing) ช่วยแก้ปัญหาอะไร?
**A:** ลดพื้นที่ทับซ้อนของเส้นทางสัญญาณบนเลเยอร์ติดกัน เพื่อลด Crosstalk
