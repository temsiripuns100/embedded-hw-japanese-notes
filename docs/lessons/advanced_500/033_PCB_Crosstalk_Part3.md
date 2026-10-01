# 033: PCB Crosstalk เจาะลึก Part 3 - Stripline vs Microstrip Routing Mitigation

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เจาะลึกโครงสร้างสนามแม่เหล็กไฟฟ้า:
- **Microstrip (Surface Layer):** สนามแม่เหล็กไฟฟ้ากระจายออกไปบนอากาศ (Fringing fields) ทำให้ $L_m$ มักจะกว้างกว่า $C_m$ ใน Inhomogeneous medium นี้ ความเร็วกระแส (Phase Velocity) ต่างกัน ทำให้มี Forward Crosstalk (FEXT) สูง
- **Stripline (Inner Layer):** Trace ถูกขนาบด้วย Solid Reference Planes (GND/VCC) ทั้งด้านบนและล่าง สนามไฟฟ้าและแม่เหล็กถูก "ล็อก" ให้อยู่ระหว่าง Plane อย่างสมมาตร (Homogeneous) ผลคือ $L_m$ และ $C_m$ หักล้างกันได้อย่างสมบูรณ์สำหรับ FEXT 
- **Broadside Crosstalk (Dual Stripline):** ในโครงสร้างที่ Layer สัญญาณ 2 ชั้นติดกันโดยไม่มี Ground กั้นตรงกลาง (เช่น Layer 3 & 4) สัญญาณจะครอสทอล์คข้าม Layer (Z-axis) อย่างรุนแรง เพราะ Broadside coupling มีพื้นที่หน้าตัด (Trace Width) หันหน้าชนกันตรงๆ!

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **กฎเหล็ก Orthogonal Routing:** ถ้าจำเป็นต้องใช้ Dual Stripline หรือ Layer สัญญาณติดกัน ให้เดินเส้นแบบตั้งฉากกัน 90 องศา (Orthogonal) เสมอ เพื่อลดระยะขนานให้เหลือแค่จุดตัด (Intersection area) ซึ่งน้อยมาก
- **การฝัง (Buried Routing) สำหรับ High-Speed:** ถ้าออกแบบบอร์ดที่วิ่งระดับ 10 Gbps+ (เช่น PCIe Gen3/4) ต้องใช้ Stripline เสมอ และต้องแน่ใจว่า Vias ที่เจาะลงไปนั้นไม่มี Stub (ใช้ Backdrill หรือ Blind/Buried Vias) ไม่งั้น Stub จะทำตัวเป็น Antenna รับ/ส่ง Crosstalk ซะเอง

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ストリップライン (Sutorippurain):** Stripline (ชั้นสายไฟด้านใน)
- **マイクロストリップ (Maikurosutorippu):** Microstrip (ชั้นสายไฟที่ผิวหน้า)
- **直交配線 (Chokkō haisen):** Orthogonal Routing (การเดินสายตั้งฉาก 90 องศา)
- **内層 (Naisō):** Inner layer
- **表層 (Hyōsō):** Surface layer

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** Broadside Crosstalk คืออะไร และจะป้องกันได้อย่างไร?
**คำตอบ:** คือ Crosstalk ที่เกิดระหว่าง Layer สัญญาณที่อยู่ติดกัน (ไม่มี Reference plane กั้น) ป้องกันโดยหลีกเลี่ยงการวาง Layer สัญญาณติดกัน หรือถ้าจำเป็น ต้องเดินเส้นสัญญาณให้ตั้งฉากกัน 90 องศา (Orthogonal routing)
