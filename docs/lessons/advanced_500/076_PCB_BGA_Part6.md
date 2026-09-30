# Lesson 076: BGA Routing Strategy - Dog Bone vs Via-in-Pad (VIP)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ High-Density Interconnect (HDI) PCB, การเลือกกลยุทธ์การลากเส้น (Routing) ออกจาก BGA (Ball Grid Array) ที่มี Pitch ต่ำกว่า 0.8mm มักจะต้องเลือกระหว่าง Dog Bone fanout หรือ Via-in-Pad (VIP).
- **Dog Bone Fanout**: เหมาะสำหรับ BGA Pitch >= 0.8mm ข้อดีคือต้นทุนการผลิตต่ำ (Standard PCB process) แต่ข้อเสียคือต้องการพื้นที่บนผิว (Surface area) ทำให้ความเหนี่ยวนำปรสิต (Parasitic Inductance) เพิ่มขึ้น
- **Via-in-Pad (VIP)**: จำเป็นสำหรับ BGA Pitch <= 0.65mm หรือในเคสที่มีข้อจำกัดเรื่อง Power/Signal Integrity (PI/SI) ขั้นสูง โดยต้องใช้กระบวนการ Via Filling (Plugging) และ Capping / Plating Over (POFV) เพื่อป้องกันปัญหาน้ำตะกั่วไหลลงรู (Solder Wicking) ซึ่งนำไปสู่รอยเชื่อมที่ไม่แข็งแรง (Cold Solder Joint)

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick**: หากใช้ Via-in-Pad อย่าลืมเช็คกับโรงงาน (Fab House) ว่าใช้ Resin plug หรือ Copper paste plug. ถ้าเป็นเรื่องระบายความร้อน (Thermal) ใต้ BGA ให้เลือกใช้ Copper paste (แม้จะแพงกว่า) หรือใช้ Thermal Vias แบบปกติแล้วกำหนด Solder mask tenting ให้ถูกต้อง
- **Design Review Check**: ตรวจสอบ Annular ring ของ Via ให้ดีเมื่อใช้ VIP เพราะหากเจาะเบี้ยว (Drill wander) อาจทำให้เกิด Breakout และส่งผลต่อความเชื่อถือได้ (Reliability)

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **引き出し線 (Hikidashi-sen)**: เส้น Fan-out หรือเส้นที่ลากออกจาก BGA pad
- **ビアインパッド (Bia-in-paddo)**: Via-in-Pad
- **はんだ吸い上がり (Handa sui-agari)**: Solder Wicking (ปัญหาตะกั่วไหลลงรู)
- **ドリルズレ (Doriru-zure)**: Drill wander / Drill registration error
- **検図 (Kenzu)**: Design review / การตรวจแบบ

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: ปัญหาใดที่มักเกิดขึ้นหากทำ Via-in-Pad โดยไม่ทำการ Capping/Plating over?
A. Crosstalk
B. Solder Wicking
C. CTE Mismatch
D. Ground Bounce
**เฉลย**: B (Solder Wicking) ตะกั่วจะไหลลงไปในรู Via ระหว่างกระบวนการ Reflow ทำให้ปริมาณตะกั่วที่จุดเชื่อม BGA ไม่พอ เกิดจุดบอดหรือการเชื่อมต่อที่ไม่แข็งแรง
