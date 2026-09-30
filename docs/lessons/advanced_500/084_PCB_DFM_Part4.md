# บทที่ 84: PCB DFM Part 4 - Solder Mask, Silkscreen และ Surface Finishes

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
Solder Mask Clearance ต้องเปิดเผื่อ Tolerance ของกระบวนการพิมพ์ (ประมาณ 2-3 mil) เพื่อป้องกัน Solder Mask ไปเกยบน Pad (Mask onto Pad) 
เรื่อง Solder Mask Web (Solder Dam) ระหว่าง Pad ของชิปที่มี Pitch ละเอียดๆ อย่าง QFP หรือ BGA ควรมีความกว้างอย่างน้อย 3-4 mil เพื่อป้องกัน Solder bridging
การเลือก Surface Finishes เช่น ENIG, HASL (Lead-free), OSP, Immersion Silver/Tin มีผลโดยตรงต่อ Shelf life และ Planarity (ความเรียบของ Pad) เช่น BGA ต้องใช้ ENIG หรือ OSP เพราะผิวเรียบสนิท ในขณะที่ HASL อาจเป็นโดมโค้ง

## ทริคหน้างาน OJT (OJT Tricks)
- อย่าให้เส้น Silkscreen ทับลงบนจุดบัดกรี (Pad) เด็ดขาด เพราะหมึก Silkscreen ทนความร้อนสูง เมื่อบัดกรีจะทำให้เกิดรอยรั่วหรือรอยแตก ทางผู้ผลิตมักจะตัด (Clip) Silkscreen ทิ้งหากพบว่าทับ Pad แต่อย่าหวังพึ่งโรงงาน ให้ทำ Rule check (DRC) ด้วยตัวเอง
- ถ้าชิ้นงานต้องผ่าน Wave Soldering ให้ใช้ Solder Dam ป้องกันตะกั่วไหลติดกัน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **レジスト (Rejisuto):** Solder Mask (โซลเดอร์มาสก์)
- **シルク (Shiruku):** Silkscreen (ซิลค์สกรีน/ตัวอักษร)
- **表面処理 (Hyoumen Shori):** Surface Finish (การเคลือบผิว)
- **金フラッシュ (Kin Furasshu):** ENIG (Electroless Nickel Immersion Gold)
- **半田ブリッジ (Handa Burijji):** Solder bridge (ตะกั่วชอร์ตติดกัน)

## ควิซท้ายบท (Quiz)
Q1: ผิวเคลือบแบบใดที่เหมาะสมที่สุดสำหรับอุปกรณ์ BGA เพราะให้ผิวสัมผัสที่เรียบเนียนที่สุด?
A) HASL
B) OSP หรือ ENIG (Correct)
C) Hot Air Leveling
D) เคลือบด้วยสารกันความชื้น
