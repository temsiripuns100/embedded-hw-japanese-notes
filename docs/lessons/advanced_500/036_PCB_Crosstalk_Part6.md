# Lesson 036: 3D EM Simulation for Crosstalk Analysis (3D電磁界シミュレーション)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในระดับ High-Speed Design (เช่น 56G/112G PAM4) การวิเคราะห์ Crosstalk ด้วยสมการ Quasi-static ไม่เพียงพออีกต่อไป วิศวกรระดับ Senior ต้องพึ่งพา **Full-Wave 3D EM Simulation** (เช่น HFSS, CST) เพื่อคำนวณ S-parameters อย่างแม่นยำ โดยพิจารณา NEXT และ FEXT ผ่านพารามิเตอร์ S31 และ S41 (ระบบ 4-Port) การวิเคราะห์ต้องครอบคลุมถึงผลกระทบของ Surface Roughness และ Dielectric Weave Effect ที่ทำให้เกิด Skew และ Mode Conversion (SCD21) ซึ่งแปลง Differential Signal เป็น Common Mode ทำให้ Crosstalk แย่ลง

## 2. ทริคหน้างาน OJT (OJT Field Tricks)
- **อย่าไว้ใจ Default Mesh:** การทำ Meshing อัตโนมัติมักจะหยาบเกินไปบริเวณขอบ Trace ให้ตั้งค่า Mesh Refinement ที่บริเวณขอบเสมอ เพื่อจับ Skin Effect
- **De-embedding:** ต้องตั้งค่า Port และ Reference Plane ให้ถูกต้อง หากตั้งผิด S-parameter จะมี Phase shift ที่ผิดเพี้ยน
- **Correlation:** ก่อนเชื่อผลซิม ให้ทำ Correlation กับผลวัดจริง (TDR/VNA) เสมอ

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **電磁界解析 (Denjikai Kaiseki):** EM Simulation (การซิมมูเลชั่นคลื่นแม่เหล็กไฟฟ้า)
- **メッシュ (Messhu):** Mesh (โครงข่ายในการคำนวณ)
- **ポート設定 (Pooto settei):** Port setup (การตั้งค่าพอร์ต)
- **モード変換 (Moodo henkan):** Mode conversion (การแปลงโหมดจาก Diff เป็น Common)

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** พารามิเตอร์ใดใช้ดู Near-End Crosstalk (NEXT) ระหว่าง Port 1 และ Port 3?
**คำตอบ:** S31
