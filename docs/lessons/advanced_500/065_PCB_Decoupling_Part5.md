# Lesson 065: PCB Decoupling Part 5 - S-Parameters, PI Simulation & Design Review (Sパラメータ、PIシミュレーションと検図)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในการตรวจสอบประสิทธิภาพของ PDN ขั้นสูง เราไม่สามารถพึ่งพาสมการอย่างง่ายได้อีกต่อไป แต่ต้องอาศัยการจำลอง (Simulation) ทางแม่เหล็กไฟฟ้า (EM Simulation) และการใช้งาน **S-Parameters** (Scattering Parameters)

สำหรับ PDN การประเมินมักใช้ $S_{11}$ (Reflection Coefficient) เพื่อดู Impedance และ $S_{21}$ (Transmission Coefficient) เพื่อดู Power Plane Transfer Impedance หรือ Coupling ระหว่างพอร์ต

สมการความสัมพันธ์ระหว่าง $S_{11}$ (กรณี 1-Port) และ Impedance ($Z_{PDN}$) คือ:
$$ Z_{PDN} = Z_0 \cdot \frac{1 + S_{11}}{1 - S_{11}} $$
โดยที่ $Z_0$ มักจะถูก Set ให้ต่ำพิเศษในเครื่องมือวัด PDN (เช่น $0.1 \Omega$ หรือต่ำกว่า) ไม่ใช่ $50 \Omega$ ปกติ

กราฟ Impedance vs Frequency ที่ได้จาก Simulation (หรือวัดจริงด้วย VNA - Vector Network Analyzer) ต้องไม่เกิน $Z_{target}$ ตลอดช่วงความถี่ หากพบ Peak เราสามารถดึง S-Parameter กลับมาวิเคราะห์สาเหตุ (Post-processing) ได้

## 2. ทริคหน้างาน OJT แบบ Step-by-step (現場の実践テクニック)
กระบวนการ PI Simulation และการตรวจแบบ (Design Review / 検図)

**Step-by-step สำหรับ 検図 (Ken-zu):**
1. **Extraction**: ดึงข้อมูล Layout จากเครื่องมือ ECAD (เช่น Allegro, Xpedition) เข้าสู่โปรแกรม SI/PI (เช่น HyperLynx, SIwave)
2. **Setup Component Models**: ใส่ RLC, SPICE หรือ Touchstone Models (S-Parameters) ให้กับตัวเก็บประจุทุกตัว 
3. **VRM Modeling**: กำหนด VRM (Voltage Regulator Module) เป็นแหล่งจ่ายไฟ พร้อมค่า R_out และ L_out ของตัว Regulator
4. **Run AC Sweep Simulation**: รันหา Profile ของ $Z_{PDN}$ 
5. **Report & Review**: นำกราฟ Z-Profile ไปเปรียบเทียบกับ $Z_{target}$ ที่คำนวณไว้ใน Part 1 หากพบว่า Pass ก็เซ็นอนุมัติ (承認: Shounin) 

## 3. คำศัพท์ญี่ปุ่นเชิงเทคนิคสำหรับการตรวจแบบ (検図用語)

- **Sパラメータ (S paramiita)**: S-Parameters
- **電磁界シミュレーション (Denjikai shimyureeshon)**: Electromagnetic Simulation (EM Sim)
- **ネットワークアナライザ (Nettowaaku anaraiza)**: Vector Network Analyzer (VNA)
- **反射係数 (Hansha keisuu)**: Reflection Coefficient ($S_{11}$)
- **検図 (Kenzu)**: Design Review / Checking the drawing
- **承認 (Shounin)**: Approval

## 4. ควิซวิเคราะห์ปัญหาระดับยาก (高度な問題分析クイズ)

**คำถาม (問題):**
ในการวัด PDN Impedance ด้วย VNA 2-Port (Shunt-Through Measurement Technique) พบว่ากราฟ Impedance ที่ได้จากเครื่องวัดต่ำมากจนติดลบในบางย่านความถี่ ทั้งที่ใน Simulation เป็นบวก สาเหตุทาง Measurement Setup ที่พบบ่อยที่สุดที่ทำให้เกิดข้อผิดพลาดนี้คืออะไร และทำไมต้องใช้เทคนิค 2-Port แทน 1-Port สำหรับการวัดระดับมิลลิโอห์ม?

**เฉลยและคำอธิบาย (解答と解説):**
ปัญหาเกิดจาก **Ground Loop Error** และความผิดพลาดจากการทำ **Calibration** ไม่สมบูรณ์
สาเหตุที่ต้องใช้ **2-Port Shunt-Through Measurement** แทน 1-Port:
การวัดค่า Impedance ที่ต่ำมากระดับมิลลิโอห์ม (เช่น $10 m\Omega$) หากใช้ 1-Port ความต้านทานและ Inductance ของสายเคเบิล (Cable Parasitics) และ Probe จะกลบค่าที่แท้จริงของ PDN ไปหมด
ในระบบ 2-Port, Port 1 จะฉีดสัญญาณ (Stimulus) และ Port 2 จะรับสัญญาณ (Response) ทำให้สามารถหักล้าง Cable/Probe Errors ได้ดีกว่า
อาการ Impedance "ติดลบ" หรือผิดเพี้ยนรุนแรง มักเกิดจาก Ground Loop Shield ระหว่าง Port 1 และ Port 2 (Transfer Impedance ของสายชิลด์)
**วิธีแก้:** ต้องใช้ Isolation Transformer หรือ Common Mode Choke ติดที่สายเคเบิลเพื่อทำลาย Ground Loop และต้องทำ 2-Port Calibration (SOLT) ให้สมบูรณ์แบบก่อนวัด
