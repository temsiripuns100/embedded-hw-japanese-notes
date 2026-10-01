# บทที่ 9: Thermal Management in PCB Routing - ระดับ Senior

## ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
ในอุปกรณ์ที่ใช้กำลังไฟสูง (High Power) หรือมีขนาดเล็กกะทัดรัด แผ่น PCB ทำหน้าที่เป็น Heatsink ตัวหลัก การออกแบบการระบายความร้อนต้องพิจารณา Thermal Resistance ($\theta_{JA}$, $\theta_{JC}$) การใช้ Thermal Vias ใต้ Thermal Pad ของ IC (เช่น QFN, DPAK) เพื่อนำความร้อนไปยัง Plane ทองแดงชั้นในหรือฝั่งตรงข้าม การคำนวณพื้นที่ทองแดง (Copper Area) สำหรับระบายความร้อน และการหลีกเลี่ยง Thermal Choke

## ทริคหน้างาน OJT (現場のコツ)
- **Thermal Vias**: อย่าเจาะรู Via ใหญ่เกินไปใต้ IC Pad เพราะตะกั่ว (Solder) อาจไหลลงไปหมด (Solder wicking) ทำให้ชิปลอยหรือระบายความร้อนไม่ได้ ควรใช้ Via ขนาด $\leq 0.3mm$ (หรือ 12 mil) และตี Grid 
- **Thermal Relief vs Solid Connection**: กราวด์แพดของ IC ที่ต้องการระบายความร้อน ห้ามใช้ Thermal Relief (แฉกๆ) เด็ดขาด ให้ต่อตรง (Solid / Direct connect) แม้ว่าฝ่ายผลิตจะบ่นว่าบัดกรียากขึ้น (ต้องใช้ Pre-heater ช่วย)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語 - けんずようご)
- **熱設計 (Netsu sekkei):** Thermal Design / การออกแบบการระบายความร้อน
- **放熱ビア (Hōnetsu bia):** Thermal Via / เวียสำหรับระบายความร้อน
- **熱抵抗 (Netsu teikō):** Thermal Resistance / ความต้านทานความร้อน
- **サーマルリリーフ (Sāmaru rirīfu):** Thermal Relief / การทำรอยเว้าที่แพดเพื่อลดการดึงความร้อนตอนบัดกรี
- **はんだ吸い上がり (Handa suiagari):** Solder Wicking / ตะกั่วไหลลงรู

## ควิซท้ายบท (確認テスト)
1. สำหรับ IC ประเภท Power MOSFET แบบ SMD การต่อ Copper Plane เข้ากับ Thermal Pad ควรใช้วิธีใดเพื่อการระบายความร้อนที่ดีที่สุด?
   a) ใช้ Thermal Relief Connection เพื่อให้บัดกรียากน้อยลง
   b) ใช้ Solid (Direct) Connection พื้นที่กว้างๆ พร้อมเจาะ Thermal Vias
   c) ต่อด้วยสาย (Trace) ขนาดเล็กเพื่อจำกัดความร้อนไม่ให้กระจายไปกวนวงจรอื่น
   d) ไม่ต้องทำอะไรพิเศษ อาศัยเพียงอากาศรอบๆ บอร์ด

*(เฉลย: b - การต่อตรงด้วยพื้นที่ขนาดใหญ่และการเจาะ Thermal Vias ช่วยถ่ายเทความร้อนลง Plane ชั้นอื่นๆ ได้ดีที่สุด)*
