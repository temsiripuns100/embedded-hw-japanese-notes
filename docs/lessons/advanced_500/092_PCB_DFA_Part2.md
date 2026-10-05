# 092 - PCB DFA Part 2: Soldering Profiles & Thermal Relief

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Thermal Relief (หรือ Thermal Pad) มีความสำคัญอย่างยิ่งยวดในการเชื่อมต่อระหว่าง Pad ของอุปกรณ์กับ Copper Pour (Plane) ขนาดใหญ่ ทองแดงเป็นตัวนำความร้อนที่ดีมาก หากต่อ Pad เข้ากับ Plane โดยตรง (Solid Connection) ความร้อนจากหัวแร้งหรือเตาอบจะถูกดึงออกไปอย่างรวดเร็ว (Heat Sink Effect) ทำให้เกิดปัญหา Cold Solder Joint หรือ Tombstoning ในอุปกรณ์ SMD เล็กๆ เนื่องจากความร้อนของ Pad ทั้งสองฝั่งไม่เท่ากัน ทำให้ตะกั่วละลายไม่พร้อมกัน เกิดแรงตึงผิวที่ดึงอุปกรณ์ให้ตั้งขึ้น

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Tombstone Killer:** สำหรับตัวต้านทานหรือคาปาซิเตอร์ขนาด 0402 หรือ 0201 ให้ตรวจสอบเสมอว่า Track ที่วิ่งเข้าหา Pad ทั้งสองข้างมีความกว้างใกล้เคียงกันหรือไม่ และถ้าต้องต่อลง Ground Plane ต้องใช้ Thermal Relief เสมอ ห้ามใช้ Solid Fill เด็ดขาด
- **Via in Pad:** หากมีความจำเป็นต้องใช้ Via in Pad สำหรับอุปกรณ์ที่ไม่ใช่ BGA ต้องสั่งทำ Via Tenting หรือ Resin Plugged ไม่งั้นตะกั่วจะไหลลง Via (Solder Wicking) ทำให้บัดกรีไม่ติด

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図用語 - Kenzu Yōgo)
- **熱逃げ (Netsunige):** Heat dissipation, Thermal relief / การระบายความร้อน (มักใช้ในบริบทของการทำ Thermal Relief เพื่อป้องกันความร้อนหนี)
- **ツームストーン現象 (Tsūmusutōn Genshō) / マンハッタン現象 (Manhattan Genshō):** Tombstone phenomenon / อาการอุปกรณ์ตั้งขึ้น
- **未はんだ (Mi-handa):** Unsoldered, Cold joint / การบัดกรีไม่ติด, ตะกั่วไม่เต็ม
- **ベタパターン (Beta patān):** Solid copper pour, Polygon pour / พื้นที่เททองแดงเต็ม

## ควิซท้ายบท (Quiz)
1. Thermal Relief ช่วยป้องกันปัญหา Tombstoning ได้อย่างไร?
2. ถ้า Track ฝั่งซ้ายของตัวต้านทาน 0603 กว้าง 1mm แต่ฝั่งขวากว้าง 0.2mm จะเกิดปัญหาอะไรตอน Reflow?
