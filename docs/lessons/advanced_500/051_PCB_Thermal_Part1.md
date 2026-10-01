# Lesson 051: PCB Thermal Part 1 - Thermal Resistance and Heat Dissipation Basics

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
การจัดการความร้อนในบอร์ดคือการลด Thermal Resistance (Theta-JA) จาก Junction ไปยัง Ambient ให้ต่ำที่สุด รอยต่อแต่ละชั้น (Die, Leadframe, PCB, TIM, Heatsink) มีค่า Thermal Resistance (R_th) ของตัวเอง กฎพื้นฐานคือ T_J = T_A + P * R_th_JA การคำนวณล่วงหน้าเป็นสิ่งจำเป็นเพื่อหลีกเลี่ยงการทำ Thermal Derating ของอุปกรณ์ในสภาพการใช้งานจริง (Worst-case scenario)

## ทริคหน้างาน OJT
อย่าเชื่อค่า Theta-JA ใน Datasheet ทันที เพราะค่านั้นทดสอบบน JEDEC Standard Board (มักมี 4 Layers) บอร์ดจริงของเรามีเงื่อนไขต่างออกไป ควรใช้ Theta-JC บวกกับค่า R_th ของ Heatsink และ TIM จริงๆ

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図)
- **熱抵抗 (Netsu Teikou):** Thermal Resistance
- **放熱 (Hounetsu):** Heat Dissipation
- **周囲温度 (Shuui Ondo):** Ambient Temperature

## ควิซท้ายบท
Q: เหตุใดจึงไม่ควรใช้ค่า Theta-JA จาก Datasheet ในการออกแบบระบบระบายความร้อนที่ซับซ้อน?
A: เพราะสภาพแวดล้อมของบอร์ดจริง (เช่น จำนวน Layer, ขนาด Copper) แตกต่างจาก JEDEC Standard Board
