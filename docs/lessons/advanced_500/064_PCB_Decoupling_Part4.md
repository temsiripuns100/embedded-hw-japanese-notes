# Lesson 064: PCB Decoupling Part 4 - Multi-Layer Stacks and Power/Ground Planes

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ Senior เราไม่ได้พึ่งพาแค่ Discrete Capacitors แต่อีกหนึ่งพระเอกคือ **Planar Capacitance** (หรือ Embedded Capacitance) ที่เกิดจากระนาบ Power และ Ground ที่อยู่ติดกันใน PCB Stack-up
$C = \frac{\epsilon_r \epsilon_0 A}{d}$ โดยที่ $d$ คือระยะห่างระหว่าง Plane
ข้อดีของ Planar Capacitance คือมี ESL ต่ำมากๆ (แทบจะเป็นศูนย์) จึงตอบสนองต่อความถี่สูงจัดๆ (ระดับ 100MHz ถึง GHz) ได้ดีกว่า Discrete Capacitors ทั่วไป
การออกแบบ Stack-up ที่ดีจะต้องจับคู่ Power Plane และ Ground Plane ให้ชิดกันที่สุด (เช่น ใช้ Prepreg หนา 2-3 mil หรือ 50-75 ไมครอน) และวางอยู่ใกล้กับผิว (Top/Bottom) ที่มี IC ติดตั้งอยู่ เพื่อลด Via Inductance ขาลงไปหา Plane

## ทริคหน้างาน OJT (OJT Field Tricks)
- **20-H Rule (บางครั้งก็เกินจำเป็น):** ทฤษฎี 20-H Rule (ดึง Power Plane ร่นเข้ามาจากขอบ Ground Plane เป็นระยะ 20 เท่าของระยะห่าง) ช่วยลด Fringing Effect (EMI ที่ขอบบอร์ด) ได้ แต่ในยุคที่ Plane อยู่ชิดกันมาก (2-3 mil) ทฤษฎีนี้อาจลดพื้นที่ Planar Capacitance จนไม่คุ้มค่า ต้องพิจารณา trade-off ให้ดี
- **Stitching Vias:** วาง GND Vias กระจายทั่วๆ ระนาบ Power/GND เพื่อลด Plane Inductance และป้องกันขอบเขตที่เป็น Resonant Cavity
- **อย่าตัด Plane ยับเยิน:** การทำ Split Plane เยอะๆ ทำให้ Return Path เสีย และลด Planar Capacitance ถ้าระเบียบการจัดวางไม่ดี จะกลายเป็นแหล่งกำเนิด EMI ชั้นดี

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **層構成 / スタックアップ (Sou Kousei / Sutakkuappu):** Stack-up
- **電源層 (Dengen Sou):** Power Plane
- **グラウンド層 (Guraundo Sou):** Ground Plane
- **プレーン間容量 (Pureen-kan Youryou):** Planar Capacitance / Inter-plane Capacitance
- **スプリットプレーン (Supuritto Pureen):** Split Plane

## ควิซท้ายบท (Quiz)
1. ทำไม Planar Capacitance จึงมีความสำคัญอย่างมากในความถี่ระดับ GHz?
2. การลดระยะห่าง ($d$) ระหว่าง Power Plane และ Ground Plane มีผลดีอย่างไรต่อระบบ PDN นอกเหนือจากการเพิ่มค่า Capacitance?
