# Lesson 43: Thermal Vias & Power Integrity (PI)

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
Thermal Vias ทำหน้าที่เป็นสะพานถ่ายเทความร้อนจากคอมโพเนนต์ที่ร้อน (เช่น Power ICs, MOSFETs) ลงสู่ Copper Planes ภายในบอร์ด จำนวนและขนาดของ Thermal Vias ต้องคำนวณจาก Thermal Resistance ($\theta_{JA}$) ของ Via การเจาะรูพรุนเกินไปอาจลดประสิทธิภาพการกระจายความร้อนเพราะหน้าสัมผัสทองแดงบน Plane หายไป สำหรับ Power Integrity (PI), Vias ที่จ่ายกระแสสูง (High Current Vias) จะเกิด Voltage Drop (IR Drop) ดังนั้นต้องคำนวณ Current Carrying Capacity ตามมาตรฐาน IPC-2152 โดยพิจารณา Temperature Rise ที่ยอมรับได้

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick:** การทำ Thermal Vias ที่ Thermal Pad ของ IC หากปล่อยรูเจาะว่างไว้ (Tented) อาจเกิดปัญหา Solder Wicking (ตะกั่วไหลลงรู) ทำให้ประสานไม่ติด ควรแนะนำให้ทำ Via Plugging ด้วย Epoxy Resin (Resin Plugged Via) หรือทำ Via in Pad Plated Over (VIPPO)
- **Design Review Check:** ในวงจร Power Supply สวิทช์ชิ่ง ให้เช็คจำนวน Via ที่ต่อระหว่าง Pad ของ Inductor กับ Power Plane ว่ารับกระแส RMS ได้เพียงพอหรือไม่ (อย่าคำนวณแค่กระแสเฉลี่ย ให้เผื่อ Ripple Current ด้วย)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **サーマルビア (Sāmaru bia):** Thermal Via
- **熱抵抗 (Netsuteikō):** Thermal Resistance
- **はんだ上がり (Handa agari):** Solder Wicking
- **樹脂埋め (Jushi ume):** Resin Plugging
- **許容電流 (Kyoyō denryū):** Current Carrying Capacity

## ควิซท้ายบท (Quiz)
**Q1:** ปัญหา Solder Wicking ที่เกิดกับ Thermal Via ใต้ IC เกิดจากสาเหตุใดและแก้ไขอย่างไร?
1. เกิดจากอุณหภูมิอบร้อนเกินไป แก้โดยลดอุณหภูมิ Reflow
2. เกิดจากตะกั่วหลอมเหลวไหลลงไปในรูเจาะกว้าง แก้โดยการทำ Resin Plug หรือลดขนาด Drill size
3. เกิดจากผิวเคลือบ Oxidation แก้โดยใช้ OSP
4. เกิดจาก Flux เยอะเกินไป แก้โดยเปลี่ยน Solder paste
*(เฉลย: 2)*
