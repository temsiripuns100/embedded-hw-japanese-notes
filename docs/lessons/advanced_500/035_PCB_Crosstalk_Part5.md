# 035: PCB Crosstalk เจาะลึก Part 5 - 3W Rule, Guard Traces & Via Stitching

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การป้องกัน Crosstalk เชิงเรขาคณิต:
- **3W Rule:** กฎพื้นฐานที่ให้ระยะห่างศูนย์กลาง-ถึง-ศูนย์กลาง ระหว่างเส้นเป็น 3 เท่าของความกว้างเส้น (Trace Width) ซึ่งทางทฤษฎีจะช่วยลด Magnetic flux linkage ระหว่างเส้นได้ประมาณ 70% และลด Crosstalk ลงมาอยู่ระดับ ~-20dB ถึง -25dB
- **Guard Traces:** การลากเส้น Ground คั่นระหว่าง Aggressor และ Victim. *คำเตือนขั้นสูง:* Guard trace ที่ไม่ได้ทำการ "Stitching via" ลง Ground Plane เป็นระยะๆ อย่างถี่พอ จะทำหน้าที่เป็น **Resonator** รับสัญญาณจาก Aggressor แล้ว Re-radiate ไปหา Victim ทำให้ Crosstalk *แย่ลง* ที่ความถี่เรโซแนนซ์!
- **Via Stitching Pitch ($\lambda$ rule):** ระยะห่างของ Via บน Guard trace ต้องน้อยกว่า $\lambda/10$ ของความถี่สูงสุดที่มีนัยสำคัญในสัญญาณ (รวมถึง Knee frequency: $F_{knee} = 0.5 / T_{rise}$) เพื่อป้องกันไม่ให้เกิด Standing wave บน Guard trace

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **เมื่อไหร่ห้ามใช้ Guard Trace:** ในการออกแบบ High-Density Interconnect (HDI) การเว้นระยะว่าง (Air gap / Substrate gap) ล้วนๆ ให้ผลดีกว่าการยัด Guard Trace แล้วใส่ Via ไม่ได้ หากไม่มีพื้นที่ตี Via ถี่ๆ จงใช้แค่ Space (5W Rule) แทน Guard Trace!
- **Edge Routing (GND Pour):** เวลาเท Copper Polygon รอบๆ Trace ความเร็วสูง ระวังระยะ Clearance (Anti-pad) ถ้าเทใกล้ไปจะเปลี่ยน Impedance ของ Trace นั้น จงใช้ Co-planar waveguide (CPWG) calculator คำนวณหาช่องว่างที่เหมาะสม ไม่ใช่เทชิดมั่วๆ

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ガードパタン (Gādo patan):** Guard pattern / Guard trace
- **ビアスティッチング (Bia sutitchingu):** Via stitching
- **クリアランス (Kuriaransu):** Clearance (ระยะห่าง)
- **共振 (Kyōshin):** Resonance (การสั่นพ้อง / การเกิด Standing Wave)
- **銅箔ベタ (Dōhaku beta):** Copper pour / Solid copper

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** เหตุใด Guard trace ที่ลากยาวโดยไม่มีการวาง Ground Vias ตลอดแนว ถึงทำให้ปัญหา Crosstalk แย่ลงได้?
**คำตอบ:** เพราะ Guard trace ที่ไม่ถูกต่อลง Ground อย่างแน่นหนาจะทำตัวเป็นสายอากาศ (Antenna) หรือ Resonator ที่ความถี่สูง มันจะรับการเหนี่ยวนำจาก Aggressor และสะท้อน/แผ่พลังงานนั้นต่อไปยัง Victim ซึ่งรุนแรงกว่าการไม่ใส่ Guard trace เสียอีก
