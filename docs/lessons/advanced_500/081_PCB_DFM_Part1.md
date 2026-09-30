# บทที่ 81: PCB DFM Part 1 - วัสดุและ Panelization (Materials & Panelization)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
DFM (Design for Manufacturing) คือหัวใจสำคัญในการนำ PCB จากหน้าจอ CAD ไปสู่สายการผลิตจริงโดยไม่เกิดปัญหา (Yield loss) 
ในส่วนของวัสดุ การเลือก Tg (Glass Transition Temperature) และ Dk/Df (Dielectric Constant / Dissipation Factor) ของ FR4 หรือ High-speed materials ต้องพิจารณาร่วมกับกระบวนการ Reflow หลายรอบ
การทำ Panelization เพื่อเข้าเครื่อง Pick & Place จะต้องออกแบบระยะขอบ (Breakaway/Tooling margin) อย่างน้อย 5-10 mm. และพิจารณาความเค้น (Stress) ที่จะเกิดตอนทำ Depanelization (V-cut หรือ Routing/Milling)

## ทริคหน้างาน OJT (OJT Tricks)
- ถ้าบอร์ดมีชิ้นส่วน BGA หรือ MLCC อยู่ใกล้ขอบบอร์ดมากเกินไป ห้ามใช้ V-cut เด็ดขาด เพราะความเค้นตอนหักบอร์ดจะทำให้ Solder joint ร้าว หรือ Capacitor แตก (Flex cracking) ให้ใช้ Routing พร้อมเจาะรู Mouse bites แทน
- วาง Fiducial mark ไว้บน Tooling strips อย่างน้อย 3 จุดเสมอ เพื่อให้เครื่องจักรจับ Reference ได้แม่นยำ

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **製造性考慮設計 (Seizousei Kouryo Sekkei):** DFM (Design for Manufacturing)
- **基板材質 (Kiban Zaishitsu):** วัสดุ PCB (PCB Material)
- **面付け (Mentsuke):** Panelization (การจัดเรียงบอร์ด)
- **Ｖカット (V-katto):** V-scoring (การเซาะร่องตัววี)
- **捨て基板 (Sute Kiban):** Tooling margin / Breakaway rail (ขอบบอร์ดที่ทิ้งไป)

## ควิซท้ายบท (Quiz)
Q1: ทำไมจึงไม่ควรใช้ V-cut กับบอร์ดที่มี MLCC วางชิดขอบบอร์ด?
A) สิ้นเปลืองพื้นที่
B) ความเค้นจากการหักจะทำให้ MLCC แตกร้าว (Correct)
C) เครื่องจักรไม่สามารถตัดได้
D) ทำให้สัญญาณรบกวนเพิ่มขึ้น
