# Lesson 150: FPGA PLL Advanced - Part 10 (Hardware Debugging, Active Probing & Multi-Corner Verification - High-Bandwidth RF Probing, S-Parameters, PVT Shmoo Plots & DO-254 Sign-Off)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ฟิสิกส์ของการวัดสัญญาณความถี่สูงและผลกระทบของสายกราวด์ (RF Clock Probing Physics & Ground Lead Inductance)
ในขั้นตอนการตรวจสอบฮาร์ดแวร์จริงบนบอร์ด (Board Bring-up & Validation) การแตะหัววัด (Oscilloscope Probe) ลงบนจุดทดสอบสัญญาณนาฬิกา (Clock Testpoint) ไม่ใช่กระบวนการแบบอุดมคติ แต่คือการนำวงจรอนาล็อกที่มีค่าความจุและความเหนี่ยวนำแฝงไปต่อขนานเข้ากับสายส่งสัญญาณความเร็วสูง:

```
               แบบจำลองทางกายภาพของ PROBE TIP และ GROUND LEAD INDUCTANCE
               
  High-Speed Clock Trace (Z_0 = 50 Ohm)
  ======================+===========================================> To FPGA Pin
                        |
                        v Probe Contact Point
                 +------+------+
                 | C_p (0.2~10pF)
                 +------+------+
                        |
                        +---------[ R_tip = 50k~1M ]--------+
                        |                                   |
                  +-----+-----+                             v
                  | L_gnd     | (Alligator Clip = 25~30 nH)  To Oscilloscope Frontend
                  | (Parasitic|  (Spring Ground   = 0.5~1 nH) (50 Ohm / 1 MOhm)
                  +-----+-----+
                        |
                       GND (PCB Ground Plane)
```

#### การเกิดวงจรเรโซแนนซ์ $LC$ อนุกรมที่ปลายโพรบ:
ความจุไฟฟ้าของปลายโพรบ ($C_p$) ต่ออนุกรมกับความเหนี่ยวนำของสายกราวด์ ($L_{gnd}$) สร้างวงจรเรโซแนนซ์อนุกรม (Series LC Resonant Tank):

$$f_{res} = \frac{1}{2\pi \sqrt{L_{gnd} \cdot C_p}}$$
$$Q = \frac{1}{R_{total}} \sqrt{\frac{L_{gnd}}{C_p}}$$

#### เปรียบเทียบความแตกต่างระหว่างสายกราวด์ปากจระเข้ vs สปริงกราวด์สั้นพิเศษ:
1. **สายกราวด์แบบหนีบปากจระเข้ (Alligator Clip Lead, ยาว $7.5\text{ cm} \approx 3\text{ inches}$):**
   * ค่าความเหนี่ยวนำแฝงสูงถึง **$L_{gnd} \approx 25 - 30\text{ nH}$**
   * เมื่อใช้กับโพรบพาสซีฟทั่วไป ($C_p \approx 10\text{ pF}$):
     $$f_{res} = \frac{1}{2\pi \sqrt{(25 \times 10^{-9}) \times (10 \times 10^{-12})}} \approx 318\text{ MHz}$$
   * **ผลกระทบทางกายภาพ:** ที่ความถี่ $318\text{ MHz}$ วงจรจะเกิดการสั่นพ้องอย่างรุนแรง ($Q > 8$) ส่งผลให้รูปคลื่นสัญญาณนาฬิกาเกิด Overshoot และ Ringing ขนาดมหึมาหลายโวลต์ วิศวกรจะเข้าใจผิดว่าสัญญาณนาฬิกาของ FPGA เสียหาย ทั้งที่แท้จริงเกิดจากสายกราวด์ของโพรบเอง!
2. **สปริงกราวด์สั้นพิเศษ (Coaxial Spring Ground, ยาว $< 3\text{ mm}$):**
   * ค่าความเหนี่ยวนำแฝงลดลงเหลือ **$L_{gnd} \approx 0.5 - 1.0\text{ nH}$**
   * เมื่อใช้ร่วมกับ Active Differential Probe ความจุต่ำ ($C_p \approx 0.25\text{ pF}$):
     $$f_{res} = \frac{1}{2\pi \sqrt{(0.8 \times 10^{-9}) \times (0.25 \times 10^{-12})}} \approx 11.2\text{ GHz}$$
   * ความถี่เรโซแนนซ์ถูกผลักออกไปไกลกว่า $10\text{ GHz}$ ทำให้การวัดรูปคลื่นที่ความถี่ $1\text{ GHz}$ มีความเที่ยงตรงแม่นยำ 100%!

---

### 1.2 พารามิเตอร์การกระเจิง (S-Parameters) และการสูญเสียการส่งผ่าน (Insertion Loss $S_{21}$ & Return Loss $S_{11}$)
ในการตรวจสอบโครงข่ายสัญญาณนาฬิกาบน PCB ระดับมืออาชีพ (เช่น ลายวงจรจาก Oscillator ไปยังขา FPGA ผ่าน SMA Connectors) ต้องใช้ Vector Network Analyzer (VNA) ตรวจสอบพารามิเตอร์ $S$:
* **$S_{11}$ (Return Loss / การสะท้อนกลับ):** ต้องมีค่าต่ำกว่า **$-15\text{ dB}$** ที่ความถี่มูลฐานและฮาร์มอนิกที่ 3 เพื่อยืนยันว่าการแมตช์อิมพีแดนซ์ ($50\ \Omega$ หรือ $100\ \Omega$ Differential) สมบูรณ์แบบ ไม่เกิดคลื่นนิ่งสะท้อน (Standing Waves)
* **$S_{21}$ (Insertion Loss / การสูญเสียในการส่งผ่าน):** ต้องมีความลาดเอียงที่สม่ำเสมอ ปราศจากรอยเว้าลึก (Resonance Dips) ซึ่งบ่งชี้ถึงการเกิด Stub หรือการสูญเสียจากไดอิเล็กทริก

---

### 1.3 วิธีการทดสอบพรมแดนการทำงานแบบ Shmoo Plot ข้ามสภาวะ PVT (PVT Shmoo Plot Methodology)

```
                 ตัวอย่าง SHMOO PLOT: OPERATING ENVELOPE (F_clk vs Core V_dd)
                 
 Core V_dd (V)
       ^
 0.90V +  *  *  *  *  *  *  *  *  *  *  *  *  *  .  .  .  (Pass up to 340 MHz)
 0.88V +  *  *  *  *  *  *  *  *  *  *  *  *  .  .  .  .
 0.85V +  *  *  *  *  *  *  *  *  *  *  .  .  .  .  .  .  <-- Nominal Point (0.85V, 250MHz)
 0.82V +  *  *  *  *  *  *  *  *  .  .  .  .  .  .  .  .      Margin = (300 - 250) / 250 = +20%
 0.80V +  *  *  *  *  *  *  .  .  .  .  .  .  .  .  .  .
 0.76V +  *  *  *  .  .  .  .  .  .  .  .  .  .  .  .  .  (Fail due to Setup Violation)
       +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--> Frequency (MHz)
        100   150   200   250   300   350
        
 [* = PASS (Lock & Zero Error),  . = FAIL (Loss of Lock or Data Corruption)]
```

#### มิติทั้ง 3 ของการทดสอบ Multi-Corner Validation:
1. **Process Corners:** Slow-Slow (SS: ทรานซิสเตอร์ช้าสุด), Typical-Typical (TT), Fast-Fast (FF: ทรานซิสเตอร์เร็วสุด มีความเสี่ยงต่อ Hold Violation)
2. **Voltage Corners:** $V_{nom} \pm 5\%$ และ $\pm 10\%$ ($V_{core}, V_{CCAUX}, V_{CCO}$)
3. **Temperature Corners:**
   * สภาวะแช่เย็นจัด (Cold Soak): $-40^\circ\text{C}$ (วิกฤตต่อการล็อกเริ่มต้นของ VCO และ Fast Hold Time)
   * สภาวะแช่ร้อนจัด (Hot Soak): $+100^\circ\text{C}$ ถึง $+125^\circ\text{C}$ (วิกฤตต่อ Setup Time และ Junction Leakage)
   * สภาวะความร้อนช็อคไล่ระดับ (Thermal Gradient Ramp): $dT/dt \ge 10^\circ\text{C/min}$ (วิกฤตต่อ Dynamic Phase Drift ระหว่าง MMCM)

---

### 1.4 เกณฑ์การตรวจสอบความสมบูรณ์สำหรับมาตรฐานอากาศยานและอวกาศ (DO-254 DAL-A / ISO 26262 ASIL-D Sign-Off)

```
+------------------------------------+-----------------------------------------------------------------------+
| การทดสอบความปลอดภัยระดับสูงสุด     | เกณฑ์และข้อกำหนดชี้ขาดสำหรับการอนุมัติ (Sign-off Criteria)             |
+------------------------------------+-----------------------------------------------------------------------+
| 1. 10,000-Cycle Power-On Lock Test | สั่งเปิด-ปิดไฟเลี้ยงระบบ 10,000 ครั้งข้ามทุกย่านอุณหภูมิ               |
|                                    | **ต้องเกิด Lock สำเร็จ 100% (Zero Lock Failure Allowed!)**             |
+------------------------------------+-----------------------------------------------------------------------+
| 2. Loss-of-Lock Reaction Time      | เมื่อจำลองเหตุการณ์ไฟตกชั่วขณะ วงจร Fail-Safe ต้องตัด Clock ภายใน       |
|                                    | **$T_{react} < 5.0\ \mu\text{s}$** และสั่ง State Machine เข้าสภาวะปลอดภัย|
+------------------------------------+-----------------------------------------------------------------------+
| 3. Jitter Bathtub Curve Sign-Off   | ตรวจสอบ Total Jitter ด้วยการสแกน BER Bathtub Curve                     |
|                                    | ยืนยันว่าค่า TJ ที่ $BER = 10^{-12}$ หรือ $10^{-15}$ มี Margin $> 30\%$|
+------------------------------------+-----------------------------------------------------------------------+
| 4. Thermal Phase Drift Immunity    | ยืนยันว่าเส้นทาง CDC ข้าม MMCM ไม่มี Metastability เมื่ออุณหภูมิเปลี่ยน|
+------------------------------------+-----------------------------------------------------------------------+
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** บอร์ดประมวลผลดาวเทียมสื่อสารวงโคจรต่ำ (Low Earth Orbit: LEO CubeSat Telemetry Transponder) ใช้ FPGA อวกาศตระกูล Space-Grade Kintex UltraScale (XQRKU060):
* MMCM ทำหน้าที่สร้างสัญญาณนาฬิกา $F_{rf} = 400.0\text{ MHz}$ ให้กับตัวปรับสัญญาณคลื่นความถี่วิทยุ (RF Modulator)

**วิกฤตหน้างาน:** ในระหว่างขั้นตอนการทดสอบจำลองสภาวะแวดล้อมอวกาศในห้องสุญญากาศความร้อน (Thermal Vacuum Chamber: TVAC) ในขณะที่อุณหภูมิเปลี่ยนผ่านจากสภาวะเงามืดของโลก (Eclipse Cold: $-30^\circ\text{C}$) สู่สภาวะโดนแสงอาทิตย์เต็มที่ (Sunlight Hot: $+75^\circ\text{C}$) ด้วยอัตราเร่งความร้อน $dT/dt = 12^\circ\text{C/min}$ บล็อก MMCM เกิดอาการ **หลุดล็อก (Loss of Lock: LOL)** กะทันหัน ส่งผลให้เครื่องส่งสัญญาณวิทยุดาวเทียมดับลง  
แต่เมื่อนำบอร์ดกลับมาทดสอบบนโต๊ะทดลองที่อุณหภูมิห้อง $+25^\circ\text{C}$ ระบบกลับล็อกได้ปกติและวัดรูปคลื่นผ่านฉลุย ทีมวิศวกรจึงติดหล่มการวิเคราะห์ปัญหาจนเกือบหลุดกำหนดการปล่อยดาวเทียมขึ้นสู่วงโคจร!

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] MMCM ของดาวเทียมหลุด Lock ในระหว่างการเปลี่ยนผ่านอุณหภูมิในห้อง TVAC
      |
      +---> [Why 1] ทำไม MMCM ถึงหลุด Lock ในระหว่างช่วงอุณหภูมิเปลี่ยนผ่าน?
      |             --> เพราะแรงดันควบคุม V_ctrl ของ VCO เกิดการแกว่งกวัดไม่เสถียร (Loop Instability)
      |
      +---> [Why 2] ทำไม V_ctrl ถึงแกว่งไม่เสถียรเฉพาะช่วงที่มีการเปลี่ยนอุณหภูมิอย่างรวดเร็ว?
      |             --> เพราะค่าความจุไฟฟ้าของตัวเก็บประจุ Loop Filter ภายในและภายนอกเกิดการเบี่ยงเบน
      |                 ร่วมกับริปเปิลบนรางไฟ VCCAUX พุ่งสูงขึ้นในช่วงที่มี Thermal Gradient
      |
      +---> [Why 3] ทำไมริปเปิลบน VCCAUX ถึงพุ่งสูงขึ้นในช่วง Thermal Gradient?
      |             --> เพราะตัวเก็บประจุเซรามิก MLCC (X7R) ที่ใช้ มีค่า Dielectric Aging และสูญเสียความจุไป 40%
      |                 เมื่อเจอความร้อนสูง ทำให้เกิด Anti-Resonance กับ Ferrite Bead ที่ความถี่ 1.8 MHz!
      |
      +---> [Why 4] ทำไมตอนทดสอบบนโต๊ะทดลองในแล็บถึงตรวจไม่พบการแกว่งกวัดนี้?
      |             --> เพราะวิศวกรใช้โพรบพาสซีฟธรรมดา (Cp = 10 pF) จิ้มวัด ซึ่งความจุของโพรบเข้าไปหน่วง
      |                 และกลบสัญญาณแกว่งกวัดนั้นไว้ (Probe Loading Masking Effect)!
      |
      +---> [Why 5 - Root Cause] ทำไมความผิดพลาดเชิงซ้อนนี้จึงหลุดรอดการตรวจสอบ?
                    --> เพราะทีมงานขาด SOP ในการใช้ Active Differential Probe แบนด์วิดท์สูงในการวัดจริง
                        และละเลยการทำ Shmoo Plot Testing แบบต่อเนื่องในระหว่างการเกิด Thermal Ramp!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการหลุด Lock ของ MMCM บนดาวเทียมระหว่างการเปลี่ยนผ่านอุณหภูมิ

   PROBING ARTIFACTS (Measurement Blindspot)   POWER INTEGRITY (Thermal Derating)
         |                                          |
   ใช้โพรบพาสซีฟ 10 pF กลบสัญญาณแกว่งกวัด            MLCC สูญเสียความจุ 40% ที่อุณหภูมิสูง
         \                                          /
          \   สายกราวด์ปากจระเข้เหนี่ยวนำนอยส์ปลอม  /   เกิด Anti-Resonance กับ Ferrite Bead ที่ 1.8 MHz
           \   เข้าใจผิดว่าสัญญาณนาฬิกาเสถียร       /   ริปเปิลทะลุเข้าสู่ Charge Pump
            +------------------------------------+
            |                                    |
            |   SATELLITE MMCM LOSS OF LOCK      |===> [CRITICAL FLIGHT DISQUALIFICATION]
            |   DURING TVAC THERMAL GRADIENT     |
            +------------------------------------+
           /                                      \
          /   ทดสอบเฉพาะจุดคงที่ (Static Soak)      \   ไม่มีการรัน 10,000-Cycle Power-On Lock Test
         /                                          \
   ละเลยการสแกน Shmoo Plot ขณะอุณหภูมิเปลี่ยนผ่าน       ขาดการทำ Worst-Case Circuit Tolerance Analysis
         |                                          |
   TEST METHODOLOGY GAPS                      SAFETY COMPLIANCE AUDIT
```

---

### ขั้นตอนการแก้ปัญหาและแนวทางป้องกันหน้างาน (Corrective Actions & SOP)

#### ขั้นตอนที่ 1: การเปลี่ยนมาใช้ Active Differential Probe และ SMA Dedicated Testpoint
* เลิกใช้การจิ้มโพรบบน Via หรือ Pad ด้วยสายปากจระเข้โดยเด็ดขาด
* ติดตั้งหัวต่อ **Micro-Coaxial Connector (U.FL หรือ SMA)** บนบอร์ด สำหรับส่งสัญญาณนาฬิกาเข้าสู่ออสซิลโลสโคป $50\ \Omega$ โดยตรง
* สำหรับการวัดจุดไฟเลี้ยง $V_{CCAUX}$ ให้ใช้ **Power Rail Probe (เช่น Keysight N7020A)** ที่มีแบนด์วิดท์ $2.0\text{ GHz}$, โหลดความจุต่ำพิเศษ ($< 0.1\text{ pF}$), และมี Dynamic Range แคบระดับมิลลิโวลต์

#### ขั้นตอนที่ 2: ปรับปรุงโครงข่าย Decoupling เพื่อรองรับการแปรผันตามอุณหภูมิ
* เปลี่ยนตัวเก็บประจุเซรามิกเกรดธรรมดาเป็นเกรด **Space-Qualified NPO/COG (Zero Temperature Coefficient)** ในตำแหน่งที่ขนานกับ Ferrite Bead
* เพิ่มตัวต้านทานแดมปิ้ง $R_{damp} = 0.5\ \Omega$ เพื่อกดค่า $Q$ ของวงจรกรองให้ต่ำกว่า $0.8$ ตลอดทุกย่านอุณหภูมิตั้งแต่ $-55^\circ\text{C}$ ถึง $+125^\circ\text{C}$

---

### SOP Checklist สำหรับการทำ Hardware Bring-up และ DO-254 Sign-off

```
[ ] 1. RF Probing Best Practices:
       - สัญญาณนาฬิกาที่มีความถี่เกิน 100 MHz ต้องวัดผ่าน SMA/U.FL หรือใช้ Active Differential Probe (Cp <= 0.3 pF)
       - ความยาวสายกราวด์ของโพรบต้องสั้นกว่า 3.0 mm (ห้ามใช้สายปากจระเข้โดยเด็ดขาด)

[ ] 2. Multi-Corner PVT Shmoo Plot Sign-off:
       - รันการทดสอบ Shmoo Plot 2D (Frequency vs Core Voltage) ที่ -40°C, +25°C, และ +100°C
       - ยืนยันว่าระยะเผื่อความปลอดภัย (Operating Frequency Margin) มีค่ามากกว่า +20% ที่แรงดันไฟต่ำสุด (V_min)

[ ] 3. Thermal Gradient Transient Test:
       - ทดสอบการล็อกของ PLL ในระหว่างที่อุณหภูมิเปลี่ยนแปลงด้วยอัตราเร่ง dT/dt >= 10°C/min
       - สัญญาณ LOCKED ต้องนิ่งเป็น '1' ตลอดการทดสอบโดยไม่มีการสะดุดหลุดเฟสแม้แต่รอบเดียว

[ ] 4. DO-254 10,000-Cycle Reliability Test:
       - ทำการรัน Automated Power Cycling Test จำนวน 10,000 รอบในตู้ควบคุมอุณหภูมิ
       - ตรวจสอบบันทึก Non-Volatile Memory Fault Log ต้องมีข้อผิดพลาด Loss of Lock เท่ากับ 0 ครั้ง (Zero Defect)
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| 実機検証 | じっきけんしょう | Jikki Kenshō | การทดสอบยืนยันผลบนฮาร์ดแวร์บอร์ดจริง (Hardware-Level Bring-up & Validation) |
| 高周波プロービング | こうしゅうはぷろーびんぐ | Kōshūha Purōbingu | การแตะวัดสัญญาณความถี่สูงด้วยโพรบ (High-Frequency Probing) |
| 接地線インダクタンス | せっちせんいんだくたんす | Setchisen Indakutansu | ความเหนี่ยวนำแฝงของสายกราวด์ (Ground Lead Inductance: $L_{gnd}$) |
| シュムープロット | しゅむーぷろっと | Shumū Purotto | แผนภาพขอบเขตการทำงานแบบ Shmoo Plot (Shmoo Plot Operating Envelope) |
| コーナー解析 | こーなーかいせき | Kōnā Kaiseki | การวิเคราะห์ขอบเขตสภาวะสุดขั้ว PVT (PVT Corner Analysis) |
| 熱勾配試験 | ねつこうばいしけん | Netsu Kōbai Shiken | การทดสอบในสภาวะการเปลี่ยนแปลงอุณหภูมิรวดเร็ว (Thermal Gradient Ramp Test) |
| 反射損失 | はんしゃそんしつ | Hansha Sonshitsu | การสูญเสียเนื่องจากการสะท้อนกลับ (Return Loss: $S_{11}$) |
| 挿入損失 | そうにゅうそんしつ | Sōnyū Sonshitsu | การสูญเสียในการส่งผ่านสัญญาณ (Insertion Loss: $S_{21}$) |
| バスタブ曲線 | ばすたぶきょくせん | Basutabu Kyokusen | กราฟรูปอ่างอาบน้ำสำหรับวิเคราะห์อัตราความผิดพลาด (Jitter Bathtub Curve) |
| 航空宇宙規格 | こうくううちゅうきかく | Kōkū Uchū Kikaku | มาตรฐานวิศวกรรมการบินและอวกาศ (Aerospace Standards: DO-254 / ECSS) |
| 適合性証明 | てきごうせいしょうめい | Tekigōsei Shōmei | การพิสูจน์ความสอดคล้องตามข้อกำหนดมาตรฐาน (Compliance Demonstration) |
| 擬似リンギング | ぎじりんぎんぐ | Giji Ringingu | การเกิดการสั่นพ้องเท็จจากเครื่องมือวัด (False Measurement Ringing Artifact) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการใช้สายกราวด์ยาววัดสัญญาณความถี่สูงจนเกิด Ringing เท็จ
**สถานที่:** ห้องปฏิบัติการทดสอบระบบดาวเทียมและอากาศยาน (Space Systems Testing Laboratory)  
**ผู้เข้าร่วม:** Chief Hardware Quality Director (ผู้อำนวยการฝ่ายคุณภาพฮาร์ดแวร์อาวุโส) และ Test Engineer (วิศวกรทดสอบระบบ)

* **Quality Director:**  
  「おい、この測定レポートの波形写真を見てみろ。400MHzのクロック波形に1.2Vものオーバーシュートと激しいリンギングが記録されているな。『FPGA内部の出力バッファインピーダンス不整合によるリンギング発生』と結論づけているが、測定治具は何を使ったんだ？まさかオシロスコープ付属の15cmワニ口グラウンド線でプロービングしたんじゃないだろうな？」  
  *(Oi, kono sokutei repōto no hakei shashin o mite miro. 400MHz no kurokku hakei ni 1.2V mono ōbāshūto to hageshii ringingu ga kiroku sarete iru na. "FPGA naibu no shutsuryoku baffa inpīdansu fuseigō ni yoru ringingu hassei" to ketsurondukete iru ga, sokutei jigu wa nani o tsukatta n da? Masaka oshirosukōpu fuzoku no 15cm waniguchi guraundo-sen de purōbingu shita n ja nai darō na?)*  
  **ความหมาย:** "เฮ้ย ดูรูปคลื่นในรายงานผลการทดสอบฉบับนี้สิ บนสัญญาณนาฬิกา 400MHz มีบันทึกว่าเกิด Overshoot สูงถึง 1.2V แถมยังมี Ringing สะบัดอย่างรุนแรง แล้วคุณก็สรุปหน้าตาเฉยว่า 'เกิด Ringing จากการไม่แมตช์อิมพีแดนซ์ของบัฟเฟอร์เอาต์พุตภายใน FPGA' คุณใช้อุปกรณ์จับสัญญาณอะไรวัดน่ะ? คงไม่ได้เอาสายกราวด์ปากจระเข้ยาว 15 ซม. ที่แถมมากับกล่องสโคปไปจิ้มวัดหรอกนะ?"

* **Test Engineer:**  
  「プローブ先端のテストポイントに手が届きにくかったため、付属の長いアース線を使ってGNDピンへ接続しました。波形が崩れていたため、てっきり基板かFPGA側の不具合だと判断してしまいました。」  
  *(Purōbu sentan no tesuto pointo ni te ga todokinikukatta tame, fuzoku no nagai āsu-sen o tsukatte GND pin e setsuzoku shimashita. Hakei ga kuzurete ita tame, tekkiri kiban ka FPGA-gawa no fuguai da to handan shite shimaimashita.)*  
  **ความหมาย:** "จุดทดสอบมันเอื้อมเข้าไปแตะยากครับ ผมเลยต่อสายกราวด์ยาวๆ ไปหนีบที่ขา GND ใกล้ๆ เห็นรูปคลื่นมันบิดเบี้ยวสะบัดขนาดนั้น ผมเลยนึกว่าเป็นข้อบกพร่องของบอร์ดหรือชิป FPGA ครับ"

* **Quality Director:**  
  「15cmのアース線は100nH以上の寄生インダクタンスを持つ！プローブ先端の容量と組めば、数百MHzで激しい共振（擬似リンギング）を起こすのは高周波測定のイロハ（基本）だ！ICを疑う前に自分の測定手法を疑え！直ちに同軸SMAコネクタ経由で直結するか、0.5nH以下のショートスプリングアースを用いてアクティブプローブで再測定しろ。擬似波形で作成された不具合報告書は即刻却下（Reject）する！」  
  *(15cm no āsu-sen wa 100nH ijō no kisei indakutansu o motsu! Purōbu sentan no yōryō to kumeba, sūhyaku-MHz de hageshii kyōshin (giji ringingu) o okosu no wa kōshūha sokutei no iroha (kihon) da! IC o utagau mae ni jibun no sokutei shuhō o utagae! Tadachini dōjiku SMA konekuta keiyu de chokketsu suru ka, 0.5nH ika no shōto supuringu āsu o mochiite akutibu purōbu de sai-sokutei shiro. Giji hakei de sakusei sareta fuguai hōkokusho wa sokkoku kyakka (Reject) suru!)*  
  **ความหมาย:** "สายกราวด์ยาว 15 ซม. มันมีค่าความเหนี่ยวนำแฝงสูงเกิน 100nH เชียวนะ! พอไปเจอกับความจุของโพรบ มันจะเกิดการเรโซแนนซ์รุนแรงที่ความถี่ไม่กี่ร้อยเมกะเฮิรตซ์ (Ringing เท็จ) นี่มันความรู้ ก.ไก่ ข.ไข่ ของการวัดความถี่สูงชัดๆ! ก่อนจะไปสงสัยชิป IC ให้สงสัยวิธีการวัดของตัวเองก่อน! ไปต่อสายโคแอกเชียลตรงเข้าหัว SMA หรือใช้ปลายสปริงกราวด์สั้นพิเศษความเหนี่ยวนำต่ำกว่า 0.5nH ร่วมกับ Active Probe วัดใหม่เดี๋ยวนี้ รายงานข้อผิดพลาดที่เขียนขึ้นมาจากรูปคลื่นเท็จ ผมสั่งตีตกไม่อนุมัติทันที!"

---

#### สถานการณ์ที่ 2: การตรวจสอบการอนุมัติแบบโดยขาดการทดสอบ Thermal Gradient Shmoo Plot
* **Quality Director:**  
  「もう一つ見過ごせない点がある。宇宙航空機器向け（DO-254 DAL-A）の適合性証明書類だが、温度試験がマイナス40℃とプラス100℃の定常点（Static Soak）しか実施されていないぞ。軌道上の熱勾配（$dT/dt = 10^\circ\text{C/min}$）における連続シュムープロット試験データが完全に欠落しているじゃないか！これでは検図のサインオフは出せない。」  
  *(Mō hitotsu misugosenai ten ga aru. Uchū kōkū kiki muke (DO-254 DAL-A) no tekigōsei shōmei shorui da ga, ondo shiken ga mainasu 40-do to purasu 100-do no teijō-ten (Static Soak) shika jisshi sarete inai zo. Kidōjō no netsu kōbai (dT/dt = 10-do/min) ni okeru renzoku shumū purotto shiken dēta ga kanzen ni ketsuraku shite iru ja nai ka! Kore de wa kenzu no sain'ofu wa dasenai.)*  
  **ความหมาย:** "ยังมีอีกจุดหนึ่งที่จะปล่อยผ่านไปไม่ได้ ในเอกสารพิสูจน์ความสอดคล้องสำหรับอากาศยานและอวกาศ (DO-254 DAL-A) การทดสอบอุณหภูมิคุณทำแค่จุดแช่นิ่ง (Static Soak) ที่ $-40^\circ\text{C}$ กับ $+100^\circ\text{C}$ เท่านั้น ข้อมูลการทดสอบ Shmoo Plot อย่างต่อเนื่องในสภาวะความร้อนเปลี่ยนผ่านตามวงโคจรจริง ($dT/dt = 10^\circ\text{C/min}$) หายไปโดยสิ้นเชิง! แบบนี้ผมเซ็น Sign-off อนุมัติให้ไม่ได้หรอกนะ"

* **Test Engineer:**  
  「定常点での周波数マージンが $+25\%$ 確保できていたため、その間の過渡状態も線形に推移するものと推測していました。」  
  *(Teijō-ten de no shūhasū mājin ga +25% kakuho dekite ita tame, sono aida no kato jōtai mo senkei ni suii suru mono to suisoku shite imashita.)*  
  **ความหมาย:** "เพราะที่จุดคงที่มันมี Margin ความถี่เหลือถึง $+25\%$ ครับ ผมเลยอนุมานเอาว่าในสภาวะเปลี่ยนผ่านระหว่างนั้นก็น่าจะเปลี่ยนแปลงแบบเชิงเส้นเช่นเดียวกันครับ"

* **Quality Director:**  
  「熱勾配の過渡期には、Die内部の発熱分布の偏りやMLCCの誘電体過渡応答で、定常状態には現れない反共振や動的位相ドリフトが牙を剥く！推測で宇宙機を飛ばす気か？直ちにTVACチャンバーで $12^\circ\text{C/min}$ の温度スイープを行いながら、電圧と周波数の動的シュムープロットを自動測定しろ。10,000回の電源オンオフ試験データと合わせて提出すること！」  
  *(Netsu kōbai no katoki ni wa, Die naibu no hatsunetsu bumpu no katayori ya MLCC no yūdantai kato ōtō de, teijō jōtai ni wa arawarenai hankyōshin ya dōteki isō dorifuto ga kiba o muku! Suisoku de uchūki o tobasu ki ka? Tadachini TVAC chanbā de 12-do/min no ondo suīpu o okonainagara, den'atsu to shūhasū no dōteki shumū purotto o jidō sokutei shiro. 10,000-kai no dengen on-ofu shiken dēta to awasete teishutsu suru koto!)*  
  **ความหมาย:** "ในช่วงเปลี่ยนผ่านของอุณหภูมิ การเอียงของการกระจายความร้อนใน Die ร่วมกับการตอบสนองของไดอิเล็กทริกใน MLCC จะเผยตัวตนของ Anti-Resonance และ Dynamic Phase Drift ที่ไม่เคยโผล่มาในสภาวะคงที่ออกมาแว้งกัดเรา! คิดจะส่งยานอวกาศขึ้นไปด้วยการเดาสุ่มอย่างนั้นเรอะ? ไปรันตู้ TVAC ไต่ระดับความร้อน $12^\circ\text{C/min}$ แล้วเขียนสคริปต์วัด Shmoo Plot อัตโนมัติเดี๋ยวนี้ และเอาข้อมูลทดสอบเปิด-ปิดไฟ 10,000 ครั้งมาส่งให้ผมด้วย!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณการสั่นพ้องของสายกราวด์โพรบและขีดจำกัดความถี่ในการวัด (Probe Ground Inductance Resonance Calculation)
วิศวกรต้องการวัดสัญญาณนาฬิกา $F_{clk} = 500.0\text{ MHz}$ ($T_{clk} = 2.000\text{ ns}$) เพื่อตรวจสอบคุณภาพรูปคลื่น โดยเปรียบเทียบการจัดชุดโพรบสองแบบ:
* **ชุดวัด Alpha ($\alpha$ - Alligator Clip Setup):**
  * โพรบพาสซีฟความจุ: $C_{p\alpha} = 9.5\text{ pF} = 9.5 \times 10^{-12}\text{ F}$
  * ความเหนี่ยวนำของสายปากจระเข้: $L_{gnd\alpha} = 28.0\text{ nH} = 2.80 \times 10^{-8}\text{ H}$
  * ความต้านทานลูป: $R_{\alpha} = 1.20\ \Omega$
* **ชุดวัด Beta ($\beta$ - Short Spring Ground Setup):**
  * โพรบแอคทีฟความจุต่ำพิเศษ: $C_{p\beta} = 0.25\text{ pF} = 2.5 \times 10^{-13}\text{ F}$
  * ความเหนี่ยวนำของสปริงกราวด์สั้น: $L_{gnd\beta} = 0.80\text{ nH} = 8.0 \times 10^{-10}\text{ H}$
  * ความต้านทานลูป: $R_{\beta} = 0.50\ \Omega$

กำหนดสมการความถี่เรโซแนนซ์อนุกรม ($f_{res}$) และสัมประสิทธิ์คุณภาพ ($Q$):
$$f_{res} = \frac{1}{2\pi \sqrt{L_{gnd} \cdot C_p}}$$
$$Q = \frac{1}{R} \sqrt{\frac{L_{gnd}}{C_p}}$$

จงคำนวณหาค่า $f_{res}$ และ $Q$ ของทั้งสองชุดวัด พร้อมวิเคราะห์ว่าชุดวัดใดสามารถใช้วัดสัญญาณ $500\text{ MHz}$ (ซึ่งมีฮาร์มอนิกที่ 3 อยู่ที่ $1.5\text{ GHz}$) ได้อย่างถูกต้อง:

A) Alpha: $f_{res} \approx 308.7\text{ MHz}, Q \approx 45.2; \quad$ Beta: $f_{res} \approx 11.25\text{ GHz}, Q \approx 113.1$ (เลือก Beta)  
B) Alpha: $f_{res} \approx 617.4\text{ MHz}, Q \approx 22.6; \quad$ Beta: $f_{res} \approx 5.62\text{ GHz}, Q \approx 56.5$ (เลือก Beta)  
C) Alpha: $f_{res} \approx 154.3\text{ MHz}, Q \approx 90.4; \quad$ Beta: $f_{res} \approx 22.50\text{ GHz}, Q \approx 226.2$ (เลือก Beta)  
D) Alpha: $f_{res} \approx 308.7\text{ MHz}, Q \approx 1.2; \quad$ Beta: $f_{res} \approx 11.25\text{ GHz}, Q \approx 0.5$ (เลือก Alpha)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: วิเคราะห์ชุดวัด Alpha ($\alpha$ - Alligator Clip)**
$$L_{gnd\alpha} \cdot C_{p\alpha} = (2.80 \times 10^{-8}\text{ H}) \times (9.5 \times 10^{-12}\text{ F}) = 2.66 \times 10^{-19}\text{ s}^2$$
$$\sqrt{L \cdot C} = \sqrt{2.66 \times 10^{-19}} = \sqrt{26.6 \times 10^{-20}} \approx 5.1575 \times 10^{-10}\text{ s}$$
$$f_{res,\alpha} = \frac{1}{2\pi \times (5.1575 \times 10^{-10})} \approx \frac{1}{3.24056 \times 10^{-9}} \approx 308,588,000\text{ Hz} \approx 308.7\text{ MHz}$$
คำนวณค่า $Q_\alpha$:
$$Z_{0\alpha} = \sqrt{\frac{L_{gnd\alpha}}{C_{p\alpha}}} = \sqrt{\frac{2.80 \times 10^{-8}}{9.5 \times 10^{-12}}} = \sqrt{2947.37} \approx 54.2896\ \Omega$$
$$Q_\alpha = \frac{Z_{0\alpha}}{R_\alpha} = \frac{54.2896\ \Omega}{1.20\ \Omega} \approx 45.24 \approx 45.2$$
*(อันตรายมาก! ความถี่เรโซแนนซ์ $308.7\text{ MHz}$ ต่ำกว่าความถี่สัญญาณ $500\text{ MHz}$ เสียอีก และมีค่า $Q = 45.2$ สูงลิบลิ่ว จะสร้าง Ringing ปลอมขนาดมหึมากลบรูปคลื่นจริงจนดูไม่ได้!)*

**ขั้นตอนที่ 2: วิเคราะห์ชุดวัด Beta ($\beta$ - Short Spring Ground)**
$$L_{gnd\beta} \cdot C_{p\beta} = (8.0 \times 10^{-10}\text{ H}) \times (2.5 \times 10^{-13}\text{ F}) = 2.00 \times 10^{-22}\text{ s}^2$$
$$\sqrt{L \cdot C} = \sqrt{2.00 \times 10^{-22}} \approx 1.41421 \times 10^{-11}\text{ s}$$
$$f_{res,\beta} = \frac{1}{2\pi \times (1.41421 \times 10^{-11})} \approx \frac{1}{8.88576 \times 10^{-11}} \approx 11,253,950,000\text{ Hz} \approx 11.25\text{ GHz}$$
คำนวณค่า $Q_\beta$:
$$Z_{0\beta} = \sqrt{\frac{L_{gnd\beta}}{C_{p\beta}}} = \sqrt{\frac{8.0 \times 10^{-10}}{2.5 \times 10^{-13}}} = \sqrt{3200} \approx 56.5685\ \Omega$$
$$Q_\beta = \frac{Z_{0\beta}}{R_\beta} = \frac{56.5685\ \Omega}{0.50\ \Omega} \approx 113.13 \approx 113.1$$
*(ความถี่เรโซแนนซ์พุ่งสูงถึง $11.25\text{ GHz}$ ซึ่งสูงกว่าฮาร์มอนิกที่ 3 ของสัญญาณ $1.5\text{ GHz}$ ถึง 7.5 เท่า ทำให้การวัดสัญญาณ $500\text{ MHz}$ ปราศจากสิ่งประดิษฐ์แปลกปลอม แม่นยำสมบูรณ์แบบ!)*

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** (Alpha: $f_{res} \approx 308.7\text{ MHz}, Q \approx 45.2$; Beta: $f_{res} \approx 11.25\text{ GHz}, Q \approx 113.1$ โดยต้องเลือกชุดวัด Beta เท่านั้น)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคำนวณความถี่โดยลืมตัวคูณ $2$ ใน $2\pi$
* ข้อ C ผิด เพราะคำนวณตัวแปรความจุคลาดเคลื่อน 4 เท่า
* ข้อ D สับสนสูตรของ $Q$ แบบขนานกับอนุกรม

---

### คำถามที่ 2: การวิเคราะห์ระยะเผื่อความปลอดภัยจากข้อมูล Shmoo Plot (Shmoo Plot Operating Margin Analysis)
จากการรันการทดสอบ 2D Shmoo Plot อัตโนมัติบนบอร์ดประมวลผล Kintex UltraScale+ ที่สภาวะแวดล้อมเลวร้ายที่สุด (Worst-Case Corner: Slow-Slow Silicon, อุณหภูมิ $+100^\circ\text{C}$):
* ข้อมูลความสัมพันธ์ระหว่างแรงดันไฟเลี้ยง Core Logic ($V_{core}$) กับความถี่สัญญาณนาฬิกาสูงสุด ($F_{max}$) ที่ระบบยังคงทำงานได้โดยไม่มีข้อผิดพลาด (Zero Bit Error / Pass State):
  * ที่ $V_{core} = 0.760\text{ V}$ ($V_{nom} - 10\%$): $F_{max} = 220.0\text{ MHz}$
  * ที่ $V_{core} = 0.800\text{ V}$ ($V_{nom} - 5\%$): $F_{max} = 265.0\text{ MHz}$
  * ที่ $V_{core} = 0.850\text{ V}$ ($V_{nom}$ Nominal): $F_{max} = 310.0\text{ MHz}$
  * ที่ $V_{core} = 0.900\text{ V}$ ($V_{nom} + 5\%$): $F_{max} = 345.0\text{ MHz}$

ระบบมีจุดทำงานปกติที่กำหนดในสเปก (Design Target):
* $V_{target} = 0.850\text{ V}$ (โดยมีข้อกำหนด Power Supply Tolerance บนบอร์ดจริง $\pm 5\%$, นั่นคือแรงดันอาจตกต่ำสุดที่ $0.800\text{ V}$)
* ความถี่สัญญาณนาฬิกาเป้าหมาย: $F_{target} = 210.0\text{ MHz}$

กำหนดสมการการคำนวณ Frequency Operating Margin ($\text{FOM}_{\%}$):
$$\text{FOM}_{\%} = \frac{F_{max}(V_{worst}) - F_{target}}{F_{target}} \times 100\%$$
โดยที่ $V_{worst} = 0.800\text{ V}$ (ที่จุดแรงดันตกต่ำสุดตามสเปกบอร์ด $\pm 5\%$)

จงคำนวณหาค่า $\text{FOM}_{\%}$ และวิเคราะห์ว่าระบบผ่านเกณฑ์ความปลอดภัยมาตรฐานอากาศยาน DO-254 DAL-A ซึ่งบังคับว่าต้องมี $\text{FOM} \ge +20.0\%$ หรือไม่:

A) $\text{FOM} = +26.19\% \implies$ ผ่านเกณฑ์อย่างปลอดภัย  
B) $\text{FOM} = +47.62\% \implies$ ผ่านเกณฑ์  
C) $\text{FOM} = +4.76\% \implies$ ไม่ผ่านเกณฑ์ (Margin ต่ำเกินไป)  
D) $\text{FOM} = +14.28\% \implies$ ไม่ผ่านเกณฑ์

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: กำหนดจุดแรงดันเลวร้ายที่สุด ($V_{worst}$)**
สเปกบอร์ดกำหนด $V_{core} = 0.850\text{ V} \pm 5\%$:
$$V_{worst} = 0.850\text{ V} \times (1 - 0.05) = 0.850\text{ V} - 0.0425\text{ V} \approx 0.8075\text{ V} \approx 0.800\text{ V}$$
จากข้อมูล Shmoo Plot ที่ $V_{core} = 0.800\text{ V}$:
$$F_{max}(0.800\text{ V}) = 265.0\text{ MHz}$$

**ขั้นตอนที่ 2: คำนวณ Frequency Operating Margin ($\text{FOM}_{\%}$)**
ความถี่เป้าหมายของระบบ: $F_{target} = 210.0\text{ MHz}$
$$\text{FOM}_{\%} = \frac{265.0\text{ MHz} - 210.0\text{ MHz}}{210.0\text{ MHz}} \times 100\% = \frac{55.0\text{ MHz}}{210.0\text{ MHz}} \times 100\% \approx 26.1905\% \approx +26.19\%$$

**ขั้นตอนที่ 3: เปรียบเทียบกับเกณฑ์ความปลอดภัย DO-254**
เกณฑ์บังคับ: $\text{FOM} \ge +20.0\%$
เนื่องจาก $+26.19\% > +20.00\%$ ดังนั้นระบบจึง **ผ่านเกณฑ์การรับรองความปลอดภัยทางวิศวกรรมอากาศยานอย่างสมบูรณ์!**

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($\text{FOM} = +26.19\% \implies$ ผ่านเกณฑ์อย่างปลอดภัย)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะนำค่า $F_{max}$ ที่แรงดันปกติ $0.850\text{ V}$ ($310\text{ MHz}$) มาคิด ซึ่งผิดหลักการ Fail-Safe ที่ต้องคิดที่แรงดันตกต่ำสุด
* ข้อ C ผิด เพราะคิดที่แรงดันวิกฤต $0.760\text{ V}$ ($-10\%$) ซึ่งเกินสเปกบอร์ดจริง
* ข้อ D มีการคำนวณเศษส่วนผิดพลาด

---

### คำถามที่ 3: การคำนวณความเชื่อมั่นทางสถิติของความน่าเชื่อถือในการล็อก 10,000 รอบ (Statistical Confidence for 10,000-Cycle Lock Test)
ในการตรวจรับระบบควบคุมดาวเทียมตามมาตรฐานความปลอดภัย DO-254 DAL-A:
* ระบบถูกทดสอบ Power Cycling เปิด-ปิดไฟเลี้ยงและตรวจสอบสถานะ `LOCKED` ของ MMCM ต่อเนื่องในตู้ควบคุมอุณหภูมิ:
  $$N = 10,000\text{ รอบการทดสอบ (Cycles)}$$
* ผลการทดสอบ: พบจำนวนครั้งที่หลุดล็อกหรือล็อกล้มเหลว $k = 0\text{ ครั้ง}$ (Zero Defect)

ตามทฤษฎีสถิติแบบทวินาม (Binomial Distribution) และการประมาณการแบบปัวซง (Poisson Approximation):
ขีดจำกัดบนของอัตราความล้มเหลวสูงสุดที่แท้จริง (Upper Confidence Limit of Failure Rate: $p_{upper}$) ที่ระดับความเชื่อมั่น $1 - \alpha = 95\%$ ($\alpha = 0.05$) กำหนดโดย:

$$p_{upper} = 1 - \alpha^{\frac{1}{N}} \approx \frac{-\ln(\alpha)}{N} \quad (\text{เมื่อ } k = 0)$$

โดยที่สำหรับระดับความเชื่อมั่น $95\%$ มีค่า $-\ln(0.05) \approx 2.9957 \approx 3.0$ (กฎแห่งเลขสาม: Rule of Three)

จงคำนวณหา:
1. อัตราความล้มเหลวสูงสุดที่ยอมรับได้ทางสถิติ ($p_{upper}$) ต่อหนึ่งรอบการบูต
2. หากดาวเทียมมีภารกิจบูตเครื่องใหม่ในอวกาศเฉลี่ยวันละ 2 ครั้ง ความน่าจะเป็นที่ระบบจะทำงานได้โดยไม่มีความล้มเหลวเลยตลอดภารกิจ 5 ปี ($N_{mission} = 2 \times 365 \times 5 = 3650\text{ รอบ}$) ภายใต้ขีดจำกัด $p_{upper}$ ดังกล่าว:

A) $p_{upper} \approx 3.0 \times 10^{-4}, \quad P_{success} \approx 33.4\%$  
B) $p_{upper} \approx 3.0 \times 10^{-4}, \quad P_{success} \approx 95.0\%$  
C) $p_{upper} \approx 1.0 \times 10^{-4}, \quad P_{success} \approx 69.4\%$  
D) $p_{upper} \approx 3.0 \times 10^{-5}, \quad P_{success} \approx 89.6\%$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณขีดจำกัดบนของอัตราความล้มเหลว ($p_{upper}$)**
$$\alpha = 0.05$$
$$-\ln(\alpha) = -\ln(0.05) \approx 2.99573$$
$$p_{upper} \approx \frac{2.99573}{10,000} \approx 2.9957 \times 10^{-4} \approx 3.0 \times 10^{-4}\text{ ต่อรอบ}$$
*(หรือประมาณ 1 ครั้งใน 3,333 รอบการบูต ที่ระดับความเชื่อมั่น 95%)*

**ขั้นตอนที่ 2: คำนวณความน่าจะเป็นของความสำเร็จตลอดภารกิจ 5 ปี ($P_{success}$)**
จำนวนรอบการบูตตลอดภารกิจ 5 ปี:
$$N_{mission} = 2\text{ ครั้ง/วัน} \times 365\text{ วัน/ปี} \times 5\text{ ปี} = 3,650\text{ รอบ}$$
ความน่าจะเป็นที่จะไม่เกิดความล้มเหลวเลย ($k = 0$):
$$P_{success} = (1 - p_{upper})^{N_{mission}} \approx e^{-N_{mission} \cdot p_{upper}}$$
แทนค่าตัวแปร:
$$N_{mission} \cdot p_{upper} = 3,650 \times (2.9957 \times 10^{-4}) \approx 1.0934$$
คำนวณค่าเอ็กซ์โปเนนเชียล:
$$P_{success} \approx e^{-1.0934} \approx 0.33507 \approx 33.5\% \sim 33.4\%$$

*ข้อสังเกตเชิงลึกสำหรับ Senior Spacecraft Architect:*
ผลการคำนวณชี้ให้เห็นว่า การทดสอบเพียง 10,000 รอบให้ขีดจำกัด $p_{upper} \approx 3.0 \times 10^{-4}$ ซึ่งยังไม่เพียงพอสำหรับภารกิจอวกาศ 5 ปี (ความน่าจะเป็นที่จะรอดมีเพียง $\approx 33.4\%$)! เพื่อให้ได้ความน่าจะเป็นสำเร็จ $> 99.0\%$ สำหรับภารกิจ 3,650 รอบ ระบบจะต้องถูกทดสอบอย่างน้อย $N \ge 300,000\text{ cycles}$ หรือต้องติดตั้งวงจรสำรอง Triple Modular Redundancy (TMR) ในระดับสถาปัตยกรรม!

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($p_{upper} \approx 3.0 \times 10^{-4}, P_{success} \approx 33.4\%$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะสับสนระดับความเชื่อมั่นของการทดสอบ (Confidence Level 95%) กับความน่าจะเป็นสำเร็จของภารกิจ (Mission Success Probability)
* ข้อ C และ D มีการคำนวณอัตราความล้มเหลวต่ำกว่าความเป็นจริงของ Rule of Three
