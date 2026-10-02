# Lesson 061: PCB Decoupling Part 1 - Introduction to PDN & Target Impedance (プリント基板のデカップリング - PDNと目標インピーダンス)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

การออกแบบระบบ Power Delivery Network (PDN) เป็นหัวใจสำคัญของวงจรดิจิทัลความเร็วสูง (High-Speed Digital Circuits) เป้าหมายหลักของการทำ Decoupling คือการรักษาแรงดันไฟฟ้า (Voltage) ให้คงที่ภายใต้การเปลี่ยนแปลงของกระแส (Transient Current) อย่างฉับพลัน

### Target Impedance ($Z_{target}$)
เพื่อให้มั่นใจว่า Ripple Voltage ($\Delta V$) จะไม่เกินขอบเขตที่ยอมรับได้ (Ripple Margin) เมื่อ IC ดึงกระแสสูงสุด (Transient Current, $\Delta I$) เราต้องรักษาระดับ Impedance ของ PDN ไม่ให้เกินค่า **Target Impedance** ซึ่งคำนวณได้จากสมการ:

$$ Z_{target} = \frac{\Delta V}{\Delta I} = \frac{V_{DD} \times \%Ripple}{I_{max} \times \%Transient} $$

ตัวอย่างเช่น หาก $V_{DD}$ = 1.2V, ยอมรับ Ripple ได้ 5%, และ $\Delta I$ = 2A:
$$ Z_{target} = \frac{1.2 \times 0.05}{2} = 0.03 \ \Omega \ (30 \ m\Omega) $$

ในทางปฏิบัติ $Z_{target}$ จะไม่ได้คงที่ทุกความถี่ แต่จะถูกจำกัดด้วยความถี่สูงสุด (Bandwidth) ที่สัญญาณมีผล ซึ่งหาได้จากเวลาเพิ่มขึ้นของสัญญาณ (Rise time, $t_r$):
$$ f_{max} = \frac{0.35}{t_r} $$

ระบบ PDN ที่ดีต้องมี Impedance ต่ำกว่า $Z_{target}$ ตลอดช่วงความถี่ตั้งแต่ DC จนถึง $f_{max}$

## 2. ทริคหน้างาน OJT แบบ Step-by-step (現場の実践テクニック)
เวลาลงมือออกแบบจริง (OJT: On-the-Job Training) การลด Impedance ไม่ใช่แค่การเพิ่มจำนวน Capacitor แต่คือการลด Inductance (ESL) ในลูป (Loop Inductance)

**Step-by-step:**
1. **คำนวณ $Z_{target}$** สำหรับแต่ละ Power Rail (VDD, VCC, VREF)
2. **ประเมินความถี่ใช้งาน** (Operating Frequency Band) เพื่อเลือกชนิดของ Capacitor (Bulk, MLCC) ให้เหมาะสม
3. **วาง Capacitor ใกล้ขา IC ที่สุด** โดยเน้นที่การลดพื้นที่ Loop (Loop Area) ระหว่าง VDD และ GND
4. **ใช้ Via หลายตัว (Multiple Vias)** ต่อ 1 Pad ของ Capacitor เพื่อลด Via Inductance
5. **วาง VDD และ GND Plane ให้ชิดกันมากที่สุด** (Thin Dielectric) เพื่อเพิ่ม Inter-plane Capacitance และลด Spreading Inductance

## 3. คำศัพท์ญี่ปุ่นเชิงเทคนิคสำหรับการตรวจแบบ (検図用語)

ในการทำ 検図 (Ken-zu: Design Review) ของบอร์ดญี่ปุ่น คำศัพท์ที่ต้องรู้:
- **電源供給網 (Dengen kyoukyuumou)**: Power Delivery Network (PDN)
- **過渡電流 (Kato denryuu)**: Transient Current
- **目標インピーダンス (Mokuhyou inpiidansu)**: Target Impedance
- **バイパスコンデンサ / パスコン (Bypass Capacitor / Pasukon)**: Decoupling Capacitor
- **寄生インダクタンス (Kisei indakutansu)**: Parasitic Inductance
- **面間容量 (Menkan youryou)**: Inter-plane Capacitance

## 4. ควิซวิเคราะห์ปัญหาระดับยาก (高度な問題分析クイズ)

**คำถาม (問題):**
วิศวกรคนหนึ่งออกแบบ PDN สำหรับ FPGA โดยคำนวณ $Z_{target}$ ได้ $20 \ m\Omega$ และใช้ MLCC $0.1\mu F$ จำนวน 10 ตัว ต่อขนานกัน อย่างไรก็ตาม เมื่อวัดจริงพบว่ามี Voltage Drop ข้ามเกณฑ์ที่ความถี่ 50 MHz สาเหตุที่เป็นไปได้มากที่สุดคืออะไร และจะแก้ไขอย่างไรในระดับ Layout?

**เฉลยและคำอธิบาย (解答と解説):**
ปัญหาเกิดจาก **Mounting Inductance (ESL รวมจากการวาง Layout)** 
ถึงแม้จะใช้ MLCC 10 ตัว แต่ถ้าการวาง Layout ทำให้ Loop Inductance สูง (เช่น เดินเส้น Trace ยาวก่อนลง Via, หรือใช้ Via แค่ 1 ตัวต่อ Pad) Impedance รวมที่ความถี่สูงจะถูก Dominant โดย Inductance ($Z = 2\pi f L_{mount}$) ทำให้ที่ 50 MHz Impedance พุ่งสูงเกิน $20 \ m\Omega$
**วิธีแก้:**
1. นำ Capacitor ไปวางใกล้ขา Power/GND ของ FPGA ให้มากที่สุด (ลด Trace length)
2. วาง Via ติดกับ Pad (Via-in-Pad ถ้าเป็นไปได้ หรือ Dog-bone ที่สั้นที่สุด)
3. ใช้ Capacitor แบบ Low-ESL (เช่น Reverse Geometry 0402 หรือ X2Y)
4. ลดระยะห่างระหว่าง Layer ของ Power และ GND (Thin Dielectric)
