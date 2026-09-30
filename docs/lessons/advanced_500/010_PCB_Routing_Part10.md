# Lesson 10: DFM (Design for Manufacturing) and Panelization (製造容易性設計とシート付け)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การออกแบบ PCB ไม่ใช่แค่ให้วงจรทำงานได้ แต่ต้อง "ผลิตได้จริง" ด้วยอัตราของเสียต่ำ (High yield) และต้นทุนต่ำ
- **Acid Traps & Slivers:** มุมแหลมน้อยกว่า 90 องศา (Acid traps) อาจกักเก็บน้ำยาเคมีกัดทองแดงไว้ ทำให้กัดเซาะเส้นขาดได้ในระยะยาว ส่วน Slivers คือเศษทองแดงแคบๆ ที่อาจลอกหลุดระหว่างผลิตและไปชอร์ตที่อื่น
- **Panelization (V-Score / Mouse Bites):** การจัดเรียงบอร์ดเล็กๆ หลายบอร์ดให้อยู่ในแผงใหญ่ (Panel) เพื่อให้ประกอบ (SMT) ได้เร็วขึ้น ต้องเว้นขอบบอร์ด (Fiducial, Tooling holes) และคำนึงถึงความแข็งแรงขณะเจาะหรือหักบอร์ด
- **Thermal Reliefs:** หากเชื่อม Pad เข้ากับ Plane ทองแดงผืนใหญ่โดยตรง (Solid connection) เวลาบัดกรี ความร้อนจะถูกดูดออกไปอย่างรวดเร็ว ทำให้บัดกรีไม่ติด (Cold solder) จึงต้องใช้ซี่ล้อ (Thermal reliefs) เพื่อกั้นความร้อน

## ทริคหน้างาน OJT (On-the-Job Tricks)
- อย่าลืมวาง Test points ไว้ให้ครบสำหรับสัญญาณสำคัญ เพื่อให้ฝั่งโรงงานสามารถทำ ICT (In-Circuit Testing) ได้ง่าย
- ระวังระยะห่างของชิ้นส่วนหนักๆ หรือเปราะบาง (เช่น Ceramic Capacitor) ไม่ให้ใกล้ขอบ V-Score มากเกินไป เพราะตอนหักบอร์ดอาจจะเกิด Stress ทำให้ C ร้าว (Cracked capacitor)
- การวาง Fiducial mark ให้อยู่มุมทแยง (Asymmetric) ช่วยให้เครื่อง Pick and Place ไม่ใส่บอร์ดกลับหัว

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **製造性 (Seizousei):** Manufacturability
- **捨て基板 (Sute kiban):** Breakaway tab / Panel margin (ขอบบอร์ดที่ทิ้งไปหลังประกอบ)
- **Vカット (Bui katto):** V-Score
- **サーマルランド (Saamaru rando):** Thermal relief (Land)
- **半田ブリッジ (Handa burijji):** Solder bridge (ตะกั่วไหลติดกัน)

## ควิซท้ายบท (Quiz)
1. การใช้ Thermal relief มีประโยชน์ในขั้นตอนใดของการผลิต?
2. ทำไมจึงไม่ควรวาง Capacitor แบบเซรามิกชิดกับแนว V-Score?
