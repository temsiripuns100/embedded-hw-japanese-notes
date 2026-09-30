# Lesson 071: BGA Pad Design Strategy (NSMD vs SMD)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การออกแบบ Pad สำหรับ BGA (Ball Grid Array) มีสองรูปแบบหลักคือ NSMD (Non-Solder Mask Defined) และ SMD (Solder Mask Defined) 
- **NSMD**: แผ่นทองแดง (Copper Pad) จะมีขนาดเล็กกว่าช่องเปิดของ Solder Mask (Solder Mask Opening) ทำให้บัดกรีสามารถเกาะด้านข้างของแผ่นทองแดงได้ เพิ่มความแข็งแรงทางกล (Mechanical Strength) และลดความเครียด (Stress) ที่จุดเชื่อมต่อ
- **SMD**: ช่องเปิดของ Solder Mask จะเล็กกว่าขนาดของแผ่นทองแดง รูปแบบนี้มักใช้กับ BGA ขนาดใหญ่หรือบอร์ดที่มีความหนาแน่นสูงเพื่อป้องกันไม่ให้ Pad หลุดร่อน (Pad Cratering) แต่ความแข็งแรงของรอยเชื่อม (Solder Joint) จะน้อยกว่า NSMD

## ทริคหน้างาน OJT (OJT Field Tricks)
- เมื่อออกแบบบอร์ดที่มี BGA pitch ขนาดเล็ก (เช่น < 0.5mm) การควบคุม tolerance ของ Solder Mask (Solder Mask Registration) ในกระบวนการผลิตเป็นเรื่องท้าทาย หากใช้ NSMD ต้องระวัง Solder Mask Web (ส่วนของ Solder Mask ระหว่าง Pad) ขาด ซึ่งอาจทำให้เกิด Solder Bridge ได้
- ให้ตรวจสอบข้อกำหนดจากผู้ผลิต IC เสมอ บางบริษัทจะระบุชัดเจนว่าให้ใช้ SMD สำหรับขา Power/Ground และ NSMD สำหรับ Signal

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ランド (Rando)** - Pad (แผ่นทองแดง)
- **ソルダーレジスト (Sorudārejisuto)** - Solder Mask
- **レジスト開口 (Rejisuto kaikō)** - Solder Mask Opening
- **パッド剥がれ (Paddo hagare)** - Pad peeling / Pad cratering
- **ショート (Shōto)** - Short circuit (เช่น Solder bridge)

## ควิซท้ายบท (Quiz)
**คำถาม:** เหตุใด NSMD จึงให้ความแข็งแรงของรอยเชื่อมที่สูงกว่า SMD?
<details>
<summary>ดูเฉลย</summary>
**คำตอบ:** เพราะ Solder สามารถเกาะที่ด้านข้าง (Sidewalls) ของแผ่นทองแดงได้ ทำให้พื้นที่ยึดเกาะเพิ่มขึ้นและการกระจายความเครียด (Stress Distribution) ทำได้ดีกว่า
</details>
