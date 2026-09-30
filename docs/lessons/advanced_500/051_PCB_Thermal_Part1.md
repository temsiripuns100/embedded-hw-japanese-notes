# 051: PCB Thermal Management - Part 1: Heat Transfer Fundamentals
## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior การเข้าใจเพียงว่าทองแดงนำความร้อนได้ดีนั้นไม่เพียงพอ ต้องเข้าใจสมการและพฤติกรรมการถ่ายเทความร้อน (Heat Transfer) ทั้ง 3 รูปแบบในระดับ PCB:
1. **Conduction (伝導 - Dendou):** การนำความร้อนผ่านวัสดุ (FR4, Copper). สมการ Fourier's Law: $q = -k \nabla T$. ค่า Thermal Conductivity ($k$) ของ FR4 ต่ำมาก (0.25 W/mK) เทียบกับ Copper (385 W/mK). ดังนั้นการระบายความร้อนส่วนใหญ่ในบอร์ดคือการหาทางเชื่อมต่อทองแดงให้ความร้อนไหลไปได้.
2. **Convection (対流 - Tairyuu):** การพาความร้อนออกสู่อากาศ. Newton's Law of Cooling: $q = h A (T_s - T_\infty)$. ปัจจัยสำคัญคือพื้นที่ผิว ($A$) และลักษณะการไหลของอากาศ (Natural vs Forced Convection).
3. **Radiation (放射 - Housha):** การแผ่รังสี. Stefan-Boltzmann Law: $q = \epsilon \sigma A (T_s^4 - T_\infty^4)$. สีของ Solder Mask (เช่น สีดำ) มีผลต่อค่า Emissivity ($\epsilon$) ซึ่งช่วยในการแผ่รังสีได้ดีกว่าสีอื่นเล็กน้อย แต่มีผลมากในสภาพสุญญากาศ (Space applications).

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **อย่าไว้ใจ FR4:** เวลาออกแบบ อย่าคิดว่าบอร์ดจะเย็นถ้าไม่มีทองแดงช่วยระบาย พื้นที่ว่างบน FR4 ไม่ช่วยอะไรเลย ให้เททองแดง (Copper Pour) เสมอ.
- **การประเมินคร่าวๆ:** หาก IC ร้อนเกิน $100^\circ C$ ในอุณหภูมิห้อง โอกาสที่ใน Field (ที่มี Ambient สูง) จะพังมีสูงมาก ควรเผื่อ Margin อย่างน้อย 20%.

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **熱伝導 (Netsudendou):** Heat conduction (การนำความร้อน)
- **放熱 (Hounetsu):** Heat dissipation (การระบายความร้อน)
- **熱暴走 (Netsubousou):** Thermal runaway (ความร้อนสะสมจนวงจรทำงานผิดพลาด/ไหม้)
- **周囲温度 (Shuui Oudo):** Ambient temperature (อุณหภูมิแวดล้อม)

## ควิซท้ายบท (Quiz)
1. วัสดุใดบน PCB ที่เป็นตัวนำความร้อนหลัก?
   a) Solder Mask
   b) FR4
   c) Copper
   d) Silkscreen
*(เฉลย: c)*
