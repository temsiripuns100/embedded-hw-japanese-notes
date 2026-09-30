# Lesson 063: PCB Decoupling Part 3 - Placement and Routing Strategies

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
กุญแจสำคัญที่สุดของ Decoupling ไม่ใช่แค่ค่า C แต่คือ "Loop Inductance" ($L_{loop}$) ยิ่ง Loop ของกระแสที่ไหลจาก C ไปหา IC และกลับมายัง C มีพื้นที่มากเท่าไหร่ Inductance ก็จะยิ่งสูง ($V_{noise} = L_{loop} \frac{di}{dt}$)
Loop Inductance ประกอบด้วย:
1. ESL ของตัว Capacitor
2. Inductance ของ Trace/Pad บนผิวด้านบน
3. Inductance ของ Via (Via Inductance)
4. Spreading Inductance ใน Power/Ground Planes
เพื่อลด $L_{loop}$ เราต้องวาง C ให้ชิด IC ที่สุด เจาะ Via ให้ใกล้ Pad ของ C มากที่สุด (หรือใช้ Via-in-Pad) และให้ระยะห่างระหว่าง Power Plane กับ Ground Plane ใน Stack-up แคบที่สุด

## ทริคหน้างาน OJT (OJT Field Tricks)
- **The "Dog-Bone" vs "Via-in-Pad":** การต่อแบบ Dog-bone (ลากเส้นจาก Pad ไปหา Via) เพิ่ม Inductance อย่างมหาศาล ถ้าเป็นบอร์ด High-Speed ให้ขอ Budget จัดทำ Via-in-Pad (เจาะ Via ลงบน Pad เลย) เพื่อลด $L_{loop}$ ให้เหลือน้อยที่สุด
- **Shared Vias = Bad Idea:** อย่าใช้ Via ร่วมกันระหว่าง C สองตัว เพราะกระแสจะแย่งกันไหลและเกิด Mutual Inductance ควรให้ C 1 ตัวมี Via ของตัวเองอย่างน้อย 1 คู่ (Power/GND)
- **GND Via Position:** วาง GND Via ของ C ให้ใกล้กับ GND Pin ของ IC มากที่สุด เพื่อให้ Return Current Path สั้นที่สุด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **配置 (Haichi):** Placement (การวางตำแหน่งอุปกรณ์)
- **配線 (Haisen):** Routing (การเดินสาย)
- **ループインダクタンス (Ruupu Indakutansu):** Loop Inductance
- **ビア (Bia):** Via
- **リターンパス (Ritaan Pasu):** Return Path

## ควิซท้ายบท (Quiz)
1. ระหว่างการวาง C ไว้ด้านเดียวกับ IC แต่อยู่ไกล กับการวาง C ไว้ด้านตรงข้าม IC (Bottom layer) แต่เจาะ Via ทะลุตรงๆ อันไหนมักจะให้ผลลัพธ์ที่ดีกว่าสำหรับ PDN ความถี่สูง? (สมมติว่าเป็นบอร์ด 6-8 layers)
2. ทำไมการใช้ Via ร่วมกันระหว่าง Capacitor หลายๆ ตัวจึงเป็นสิ่งที่ไม่ควรทำ?
