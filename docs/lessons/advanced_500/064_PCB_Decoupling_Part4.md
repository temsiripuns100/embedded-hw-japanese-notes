# Lesson 064: PCB Decoupling Part 4 - OJT Tricks for Decoupling Placement & Routing (パスコンの配置と配線の実践的テクニック)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

การกระจายตัวของกระแสบน Power/GND Plane (Plane Spreading Inductance) เป็นสิ่งที่ต้องนำมาคำนวณ เมื่อ Capacitor ถูกวางไกลจากขาของ IC
Spreading Inductance ($L_{spread}$) สามารถประมาณการได้ด้วยสมการ:
$$ L_{spread} = \mu_0 \cdot d \cdot \frac{l}{w} $$
โดยที่ $d$ คือระยะห่างระหว่าง Power Plane กับ GND Plane (Dielectric Thickness)
ยิ่ง $d$ มีค่าน้อย (Thin Dielectric) ค่า $L_{spread}$ จะยิ่งลดลงอย่างรวดเร็ว

ด้วยเหตุนี้ การออกแบบ Board Stackup ให้มี Solid Power Plane ติดกับ Solid GND Plane ภายใต้ระยะห่างที่น้อยที่สุด (เช่น 2-3 mils) จึงเป็นเทคนิคขั้นสุดยอดที่ช่วยลด Plane Inductance และเพิ่ม Plane Capacitance (Inter-plane Capacitance)

## 2. ทริคหน้างาน OJT แบบ Step-by-step (現場の実践テクニック)
เทคนิคการวาง Capacitor (Placement) และการลากเส้น (Routing/Fanout)

**Step-by-step:**
1. **IC Package Type Matters**: สำหรับ BGA (Ball Grid Array) ให้วาง High-frequency MLCC ที่ด้านล่างของบอร์ด (Bottom Side) ตรงตำแหน่งกึ่งกลางของ BGA (Directly Under the Die)
2. **Via-in-Pad หรือ Offset Dog-bone**: การทำ Via-in-Pad ลด ESL ได้ดีที่สุด แต่แพง (ต้องทำ Filled/Capped) ถ้าทำไม่ได้ ให้ใช้ Offset Dog-bone ที่ลากยาวไม่เกิน 10 mils
3. **Power/GND Layer Assignment**: ให้กำหนด Layer ชั้น Power ให้ชิดกับ Layer GND เสมอ และ พยายามให้ Capacitor Vias เจาะทะลุผ่าน Layer ทั้งสองนี้ให้ตื้นที่สุด (Top layer C to Top-half planes) เพื่อหลีกเลี่ยง Via Inductance จากส่วนที่ไม่ได้ใช้ (Via Stub)
4. **Current Crowding Avoidance**: หลีกเลี่ยงการวาง Vias เป็นกำแพงขวางทางเดินของกระแส (Swiss-cheese effect บน Plane) ต้องเว้นระยะ (Anti-pad) ให้กระแสไหลผ่านได้สะดวก

## 3. คำศัพท์ญี่ปุ่นเชิงเทคนิคสำหรับการตรวจแบบ (検図用語)

- **ビア・イン・パッド (Bia in Paddo)**: Via-in-Pad
- **プレーンインダクタンス (Pureen indakutansu)**: Plane Inductance
- **スタックアップ / 層構成 (Sutakkuappu / Sou-kousei)**: Layer Stackup
- **這いまわし (Haimawashi)**: Routing / Trace Layout
- **ボイド / スイスチーズ現象 (Boido / Suisu chiizu genshou)**: Voiding / Swiss-cheese effect (on copper planes)

## 4. ควิซวิเคราะห์ปัญหาระดับยาก (高度な問題分析クイズ)

**คำถาม (問題):**
บอร์ด 12-Layer มีการจัด Stackup ดังนี้: 
Top, L2(GND), L3(Sig), L4(Power), ...
ผู้ออกแบบวาง 0402 Decoupling Capacitor ที่ Top Layer เพื่อเลี้ยง IC BGA ที่ Top Layer เช่นกัน
เมื่อคำนวณ Mounting Inductance พบว่าสูงเกินไป ทั้งที่วาง Capacitor ชิด BGA มากแล้ว เกิดจากอะไร?

**เฉลยและคำอธิบาย (解答と解説):**
ปัญหาเกิดจาก **Loop Area ในแกน Z (Vertical Loop Inductance)**
กระแสจะต้องไหลจาก Capacitor ขา Power (Top) มุดลง Via ไปที่ L4 (Power) แล้ววิ่งผ่าน Plane ไปหา BGA Via แล้วมุดขึ้นไปที่ Top
ขณะที่ขากลับ กระแสไหลจาก BGA มุดลง L2 (GND) กลับมาที่ Capacitor ขา GND มุดขึ้น Top
ระยะทางตามแกน Z ระหว่าง L2 กับ L4 ทำให้เกิด **Loop Inductance** ที่มองไม่เห็นใน Layout แบบ 2D
**วิธีแก้:**
ย้าย Layer Power มาไว้ที่ L3 แทน (สลับกับ Sig) เพื่อให้ L2(GND) และ L3(Power) ชิดกัน (ลด Z-axis Loop) และทำให้ระยะการเจาะ Via จาก Top มา L2/L3 สั้นที่สุด
