# 039: PCB Crosstalk เจาะลึก Part 9 - 3D EM Solvers (HFSS/CST)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เมื่อความถี่ขึ้นระดับ GHz, กฎ Rule of Thumb อย่าง 3W เริ่มใช้ไม่ได้ผลในโครงสร้าง 3 มิติ (Vias, Connectors, BGA Breakouts) วิศวกรระดับ Senior ต้องพึ่งพา Full-Wave 3D Electromagnetic Solvers (เช่น Ansys HFSS, CST Microwave Studio):
- **S-Parameters (Scattering Parameters):** ผลลัพธ์หลักที่ใช้วิเคราะห์ Crosstalk S31 (Near-End Crosstalk) และ S41 (Far-End Crosstalk) โดยปกติเราต้องการให้ S31 และ S41 มีค่าต่ำกว่า -40dB (1%) ในแถบความถี่ใช้งาน (Nyquist Frequency)
- **Via Crosstalk in 3D:** สนามแม่เหล็กหมุนวนรอบ Via barrel แบบขนานกัน (Parallel cylinder coupling) การใส่ Return Via (GND Via) ข้างๆ Signal Via จะบังคับทิศทางสนามแม่เหล็ก (H-Field) ไม่ให้แผ่กระจายไปโดน Via ของ Victim 
- **Mode Conversion Simulation:** 3D Solvers สามารถคำนวณ Mixed-Mode S-Parameters เช่น $S_{cd21}$ (Differential-to-Common Mode Conversion) ซึ่งสำคัญมากในการทำนาย EMI radiation จากโครงสร้างที่ไม่สมมาตร

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Boundary Conditions:** เวลาเซ็ตอัพ 3D Solver อย่าลืมกำหนด Wave Port ให้ถูกต้อง (Reference impedance และขนาด Port ต้องครอบคลุม Fringing field ทั้งหมด) ถ้าย่อ Port เล็กไป ผล Simulation S-Parameter จะดีเกินจริง (Optimistic error)
- **Mesh Optimization:** โฟกัสการตี Mesh แบบละเอียดมากบริเวณ "ขอบ" ของ Trace (Edge) และตรงช่องว่าง (Gap) เพราะนั่นคือบริเวณที่สนามไฟฟ้า (E-Field) กระจุกตัวสูงที่สุด (Skin effect & Current crowding)

## 3. คำศัพท์ภาษาญี่ปุ่นที่社ใช้ในการตรวจแบบ (検図 - Kenzu)
- **電磁界シミュレータ (Denjikai shimyurēta):** Electromagnetic field simulator
- **Sパラメータ (Es-paramēta):** S-Parameters
- **メッシュ分割 (Messhu bunkatsu):** Meshing / Mesh generation
- **境界条件 (Kyōkai jōken):** Boundary conditions
- **ビア間干渉 (Bia-kan kanshō):** Via-to-Via interference / crosstalk

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** ในกราฟ Mixed-Mode S-Parameter พารามิเตอร์ $S_{cd21}$ บ่งบอกถึงอะไรในการออกแบบ Differential Pair?
**คำตอบ:** บ่งบอกถึง Mode Conversion อัตราส่วนที่สัญญาณ Differential (d) ฝั่ง Input (Port 1) ถูกแปลงและหลุดลอดออกไปเป็นสัญญาณ Common-Mode (c) ที่ฝั่ง Output (Port 2) ซึ่งค่านี้ยิ่งสูงยิ่งแสดงถึงความไม่สมมาตรของโครงสร้างและมีความเสี่ยงต่อ EMI สูง
