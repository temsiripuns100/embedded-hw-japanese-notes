# PCB Decoupling Part 10: EMI/EMC Considerations in Decoupling

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
โครงข่าย Decoupling ที่ไม่ดีไม่เพียงทำให้วงจรทำงานผิดพลาด (Signal Integrity issues) แต่ยังเป็นแหล่งกำเนิด EMI (Electromagnetic Interference) ที่สำคัญ Noise จาก Power Plane สามารถแผ่รังสีออกไปที่ขอบของ PCB (Edge Radiation) เนื่องจาก Power และ GND plane ทำตัวคล้ายเสาอากาศแบบ Cavity Resonator
การแก้อาการเหล่านี้สามารถทำได้โดยการวาง Decoupling Capacitor กระจายตามขอบของบอร์ด (Peripheral Decoupling) หรือใช้เทคนิค 20-H rule คือการดึง Power Plane ร่นเข้ามาจากขอบ Ground Plane เป็นระยะ 20 เท่าของความห่างชั้น Dielectric เพื่อบังคับให้ Fringing field กลับลง Ground

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Stitching Capacitors:** เมื่อมีสัญญาณความเร็วสูงวิ่งข้าม Split Plane (รอยแยกของ Power Plane) จะต้องมี Stitching C ข้ามรอยแยกนั้นทันที เพื่อเป็น Return path สำหรับกระแสความถี่สูง ป้องกันไม่ให้ Loop area กว้างจนแผ่ EMI สอดคล้องกับหลักการ "Always provide a continuous return path"
- **Edge Decoupling:** ในการทำบอร์ด Automotive หรืออุตสาหกรรมที่เคร่ง EMC มากๆ ซีเนียร์มักจะสั่งให้วาง C (เช่น 1nF หรือ 10nF) ล้อมรอบขอบบอร์ดทุกๆ ระยะ 1-2 นิ้ว เพื่อกด Resonance ที่ขอบบอร์ด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
1. **Electromagnetic Interference (EMI):** 電磁干渉 / 不要輻射 (Denji kanshou / Fuyou fukusha)
2. **Edge Radiation:** エッジ放射 (Ejji housha)
3. **20-H Rule:** 20Hルール (Nijuu Eichi ruuru)
4. **Stitching Capacitor:** スティッチングキャパシタ (Suticchingu kyapashita)
5. **Return Path:** リターンパス (Ritaan pasu)

## ควิซท้ายบท (Quiz)
**คำถาม:** กฎ 20-H (20-H Rule) ในการออกแบบ PCB มีวัตถุประสงค์เพื่ออะไร?
1. เพื่อป้องกันไม่ให้ชิ้นส่วนหลุดออกจากบอร์ดระหว่างขนส่ง
2. เพื่อจำกัด Fringing fields ไม่ให้แผ่รังสีออกนอกขอบบอร์ด (ลด EMI)
3. เพื่อให้ง่ายต่อการประกอบลง Case
4. เพื่อระบายความร้อนได้ดีขึ้น 20 เท่า

*เฉลย:* ข้อ 2 (เพื่อดึง Power Plane เข้ามา ลดการแผ่รังสีจากขอบบอร์ด)
