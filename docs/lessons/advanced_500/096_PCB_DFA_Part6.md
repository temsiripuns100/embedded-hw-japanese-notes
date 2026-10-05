# PCB DFA Part 6: Advanced Soldering Defects & Component Placement Optimization

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior การจัดวางอุปกรณ์ (Component Placement) ไม่ใช่แค่ทำตาม Design Rule (DRC) แต่คือการวิเคราะห์ถึงผลกระทบต่อกระบวนการบัดกรี (Soldering Dynamics) เช่น Shadow effect ใน Wave Soldering หรือ Tombstoning ใน Reflow.
- **Tombstoning (Manhattan Effect):** เกิดจากความไม่สมดุลของแรงตึงผิว (Surface Tension) ระหว่างสองฝั่งของ Chip component (เช่น 0402 หรือ 0201). การออกแบบ Pad size ที่ไม่สมมาตร หรือ Thermal mass ที่ต่างกันเกินไปทำให้ตะกั่วหลอมละลายไม่พร้อมกัน
- **Shadow Effect:** สำหรับ Wave Soldering หากจัดวางอุปกรณ์ SMD ตัวเล็กไว้ด้านหลังอุปกรณ์ตัวใหญ่ตามทิศทางการไหลของคลื่น จะทำให้คลื่นตะกั่วเข้าไม่ถึง เกิดการบัดกรีไม่ติด (Skip หรือ Open)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Pad Modification:** หากเจอ Tombstoning บ่อยๆ ให้ลดขนาดของ Pad ฝั่งที่มี Thermal mass น้อยกว่าลงเล็กน้อย หรือเช็คว่ามี Via in Pad หรือไม่
- **Clearance for Nozzle:** อย่าลืมเว้นระยะรอบๆ BGA หรือ QFN เพื่อให้ Nozzle ของ Rework Station สามารถลงไปครอบได้โดยไม่ชนอุปกรณ์ข้างเคียง (อย่างน้อย 3-5mm)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **未はんだ (Mihanda):** Solder skip / บัดกรีไม่ติด
- **ツームストーン現象 (Tsumusuton gensho):** Tombstoning / Manhattan effect
- **熱容量 (Netsuyouryou):** Thermal mass / ความจุความร้อน
- **実装方向 (Jissou houkou):** Mounting direction / ทิศทางการลงอุปกรณ์
- **リワーク性 (Riwaaku-sei):** Reworkability / ความสามารถในการซ่อมแซม

## ควิซท้ายบท (Quiz)
**Q:** หากเกิด Tombstoning อย่างหนักในไลน์การผลิต สาเหตุแรกๆ ที่ Senior Engineer ควรเข้าไปเช็คใน Gerber file คืออะไร?
A) ระยะห่างระหว่าง Component (Clearance)
B) ความสมมาตรของขนาด Pad และ Thermal Relief ของฝั่ง Ground
C) ความหนาของ Solder Mask
**เฉลย:** B) ความสมมาตรของ Pad และ Thermal Relief ส่งผลโดยตรงต่ออัตราการหลอมละลายของตะกั่ว
