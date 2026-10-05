# Lesson 060: PCB Thermal Part 10 - Thermal Design Review (Kenzu) and Failure Troubleshooting

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในขั้นตอนการตรวจรับแบบและรีวิววงจร (Design Review / 検図 - Kenzu) ของทีมวิศวกรรมอาวุโส ความร้อนไม่ได้เป็นเพียงเรื่องของ "ชิปไม่ร้อนเกินลิมิต" แต่เป็นเรื่องของ **ความน่าเชื่อถือตลอดอายุการใช้งาน (Mission-Life Reliability)** ความร้อนที่เพิ่มขึ้นเพียงเล็กน้อยจะเร่งให้เกิดกลไกความล้มเหลวระดับโมเลกุลในเซมิคอนดักเตอร์และรอยต่อบัดกรีอย่างก้าวกระโดดผ่านความสัมพันธ์แบบเอกซ์โพเนนเชียล

```
+-------------------------------------------------------------------------+
|                  Arrhenius Thermal Acceleration Physics                 |
|                                                                         |
|      Reliability & Lifetime exponentially degrade with Temperature!     |
|                                                                         |
|                 AF = exp[ (E_a / k_B) * (1/T_use - 1/T_stress) ]        |
|                                                                         |
|      Rule of Thumb (Arrhenius 10°C Rule):                               |
|      "Every 10°C increase in Junction Temperature (T_j)                 |
|       cuts the component mean time to failure (MTTF) by HALF (50%)!"    |
+-------------------------------------------------------------------------+
```

### 1.1 ทฤษฎีการเร่งความเสื่อมสภาพด้วยความร้อน (Arrhenius Acceleration & Black's Electromigration Equation)

กลไกความล้มเหลวของสารกึ่งตัวนำส่วนใหญ่ (เช่น การเสื่อมของเกตออกไซด์ Time-Dependent Dielectric Breakdown: TDDB, การกัดกร่อนของสารเคลือบ, และการกระจายตัวของอะตอมโลหะ) เป็นไปตาม **สมการของอาร์เรเนียส (Arrhenius Equation)**:

$$\text{Reaction Rate } (k) = A \cdot \exp\left( -\frac{E_a}{k_B \cdot T} \right)$$

ปัจจัยเร่งความล้มเหลวเนื่องจากความร้อน (Thermal Acceleration Factor: $AF_{thermal}$) เมื่อชิปทำงานที่อุณหภูมิ $T_{stress}$ เทียบกับอุณหภูมิออกแบบปกติ $T_{use}$ คือ:

$$AF_{thermal} = \frac{\text{Rate}(T_{stress})}{\text{Rate}(T_{use})} = \exp\left[ \frac{E_a}{k_B} \left( \frac{1}{T_{use}} - \frac{1}{T_{stress}} \right) \right]$$

โดยที่:
- $E_a$ คือ พลังงานกระตุ้นของกลไกความล้มเหลว (Activation Energy, ปกติ $\approx 0.6 - 0.9 \text{ eV}$ สำหรับซิลิคอน IC)
- $k_B = 8.617 \times 10^{-5} \text{ eV/K}$ (Boltzmann Constant)
- $T_{use}, T_{stress}$ คือ อุณหภูมิสัมบูรณ์ของรอยต่อ ($\text{K}$)

นอกจากนี้ ในลายทองแดงและสายบอนด์ที่นำกระแสความหนาแน่นสูง ($J > 10^5 \text{ A/cm}^2$) การย้ายถิ่นของอะตอมโลหะเนื่องจากแรงผลักของอิเล็กตรอน (Electromigration: EM) ถูกควบคุมโดย **สมการของแบล็ก (Black's Equation)**:

$$\text{MTTF} = \frac{A}{J^n} \cdot \exp\left( \frac{E_{a, EM}}{k_B \cdot T} \right)$$

โดยที่ $n \approx 1 - 2$ เมื่ออุณหภูมิของจุดเชื่อมต่อหรือลายทองแดงเพิ่มขึ้น อะตอมทองแดงจะเคลื่อนที่เร็วขึ้น เกิดโพรงขาด (Voids) ที่ปลายข้างหนึ่ง และเกิดการงอกของหนวดโลหะ (Whiskers/Hillocks) ลัดวงจรที่ปลายอีกข้างหนึ่ง

### 1.2 เกณฑ์การลดทอนพิกัดกำลังตามความร้อน (Thermal Derating Guidelines)

เพื่อป้องกันความเสียหายตลอดอายุรับประกัน $10 - 15$ ปี (โดยเฉพาะมาตรฐานยานยนต์ AEC-Q100/104 และเกณฑ์อุตสาหกรรม IEC 60068) วิศวกรอาวุโสจะต้องกำหนดเกณฑ์ **Thermal Derating Policy** ไว้อย่างเข้มงวด:

```
Silicon Junction Rating (Datasheet Absolute Max: e.g. 150°C)
  │
  ├── [ 150°C : Absolute Maximum (CATASTROPHIC RISK) ]
  │
  ▼ [ 20°C - 25°C Safety Margin Buffer ]
  ├── [ 125°C : Automotive De-rated Limit (AEC-Q Grade 1) ]
  │
  ▼ [ Nominal Operating Zone ]
  └── [ <= 105°C : Target Design Limit for 15-Year Life ]
```

| ประเภทส่วนประกอบ (Component Type) | ค่าพิกัดสูงสุดใน Datasheet ($T_{max}$) | ขีดจำกัดหลัง Derating ($T_{derated}$) | เหตุผลเชิงฟิสิกส์และความน่าเชื่อถือ |
| :--- | :--- | :--- | :--- |
| **Power MOSFETs / IGBTs** | $T_{j, max} = 150^{\circ}\text{C} - 175^{\circ}\text{C}$ | $T_j \le 125^{\circ}\text{C}$ (หรือ $\le 80\% T_{max}$) | ป้องกัน Thermal Runaway จาก $R_{DS(on)}$ ที่เพิ่มขึ้นตามอุณหภูมิ |
| **Microcontrollers / SoCs** | $T_{j, max} = 125^{\circ}\text{C}$ | $T_j \le 100^{\circ}\text{C} - 105^{\circ}\text{C}$ | ป้องกัน Timing Jitter, Clock Skew, และ Leakage Current |
| **Aluminum Electrolytic Caps** | Rated Life: 2,000h @ $105^{\circ}\text{C}$ | $T_{case} \le 75^{\circ}\text{C} - 85^{\circ}\text{C}$ | อิเล็กโทรไลต์แห้งตัวเร็วขึ้น 2 เท่าทุกๆ $10^{\circ}\text{C}$ ที่เพิ่มขึ้น |
| **Precision Voltage Reference / ADC**| $T_{op, max} = 125^{\circ}\text{C}$ | $T_{pcb} \le 70^{\circ}\text{C}$ | Thermal Drift ของ Bandgap และความเครียดเชิงกล Piezoelectric |
| **Crystal Oscillators (XTAL)** | Operating: $-40^{\circ}\text{C} \sim +105^{\circ}\text{C}$ | $T_{pcb} \le 80^{\circ}\text{C}$ | Frequency Drift เกินช่วงชดเชยของ PLL |

### 1.3 ทฤษฎีการตัดแยกระนาบความร้อนด้วยร่องตัด (Thermal Isolation Slits / Thermal Moats)

เมื่อมีชิ้นส่วนกำลังสูง (Hot Power Source เช่น Switching Regulator, BLDC Driver) ติดตั้งอยู่บนบอร์ดเดียวกับวงจรที่มีความอ่อนไหวต่ออุณหภูมิ (Cold Sensitive Analog/Sensor เช่น RTD Input, Shunt Resistor Amplifier, Crystal) การนำความร้อนผ่านระนาบทองแดง (Ground Plane Conduction) จะแผ่ความร้อนเข้าหาวงจรแอนะล็อกโดยตรง

การสกัดกั้นฟลักซ์ความร้อนในแนวระนาบสามารถทำได้โดยการเซาะร่องตัดทะลุเนื้อบอร์ด (**Thermal Slit / Isolation Milling**):

$$q_{cond} = -k_{eff} \cdot A_{cross} \cdot \frac{dT}{dx} = -k_{eff} \cdot (W_{bridge} \cdot t_{board}) \cdot \frac{\Delta T}{L}$$

```
+-------------------------------------------------------------+
|               Thermal Isolation Slit Physics                |
|                                                             |
|   [ Hot Power Stage ]                 [ Sensitive Analog ]  |
|      (T = 110°C)                          (T <= 55°C)       |
|   ──────────────────┐                 ┌──────────────────   |
|   Solid Ground Pour │                 │ Clean Analog GND    |
|   ==================│   AIR SLIT      │==================   |
|                     │ (k = 0.026 W/mK)│                     |
|                     │                 │                     |
|   ==================│   (Cut-out)     │==================   |
|   ──────────────────┘                 └──────────────────   |
|                             ▲                               |
|                     Narrow Neck Bridge                      |
|                  (W_bridge <= 1.5 - 2.0 mm)                 |
+-------------------------------------------------------------+
```

โดยการเซาะร่องแอร์สลิต ค่าความต้านทานความร้อนในแนวราบ ($R_{\theta, slit}$) จะพุ่งสูงขึ้นหลายสิบเท่า บังคับให้ความร้อนต้องเดินทางอ้อมผ่านคอคอดแคบๆ (Narrow Bridge Neck) ความร้อนส่วนใหญ่จึงถูกระบายออกสู่อากาศก่อนที่จะข้ามไปยังฝั่งแอนะล็อก

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)

**เหตุการณ์:** กล่องควบคุมพวงมาลัยพาวเวอร์ไฟฟ้า (Electric Power Steering: EPS ECU) ติดตั้งในห้องเครื่องยนต์ ประกอบด้วยบอร์ด 8-Layer ทำงานร่วมกับมอเตอร์ 3 เฟส (กระแสสูงสุด $80 \text{ A}$) และไมโครคอนโทรลเลอร์ Dual-Core Lockstep ทำงานร่วมกับ Precision Crystal Oscillator ขนาด $20 \text{ MHz}$ 

**อาการล้มเหลว:**
1. ในขั้นตอนการทดสอบขับขี่ในสนามทดสอบอุณหภูมิสูง (Vehicle Hot Chamber Test ที่ $45^{\circ}\text{C}$ แดดจัด) รถยนต์ตัดการทำงานของระบบพวงมาลัยพาวเวอร์กะทันหัน และขึ้นโค้ดข้อผิดพลาด "CAN-FD Synchronization Loss & MCU Clock Plausibility Fault"
2. บอร์ด ECU ไม่มีความเสียหายจากการระเบิด ชิปทุกตัวยังทำงานได้ แต่เมื่อตรวจสอบบันทึก Log พบว่าวงจร PLL ของ MCU หลุดการล็อก (Loss of Lock) เพราะความถี่ของคริสตัลออสซิลเลเตอร์เกิดการเบี่ยงเบน (Frequency Drift) เกินกว่า $\pm 50 \text{ ppm}$
3. เมื่อส่องภาพถ่ายความร้อน IR Thermography พบว่าตัวถังคริสตัล (X101) ซึ่งควรจะอยู่ที่อุณหภูมิไม่เกิน $75^{\circ}\text{C}$ กลับมีอุณหภูมิพุ่งสูงถึง **$108^{\circ}\text{C}$**!

```
[Defect Mechanism: Thermal Bleed into Crystal Oscillator]
   MOSFET Inverter Stage (T = 125°C)
         │
         ▼  (Solid Unbroken Ground Plane Conduction)
   ═══════════════════════════════════════════════════════════
   Copper Pour (Continuous L2/L4 Ground Plane)
   ═══════════════════════════════════════════════════════════
         │
         ▼  (Heat dumps directly into Crystal package!)
   [ 20MHz Crystal X101 ] ---> Drifted to 108°C! (PLL Loss of Lock!)
```

**Root Cause Analysis (RCA):**
1. **การนำความร้อนผ่าน Solid Ground Plane:** วิศวกร PCB วางคริสตัล X101 อยู่ห่างจาก MOSFET เฟส U เพียง $8 \text{ mm}$ โดยมีระนาบ Ground Plane ชั้น 2 และชั้น 4 เป็นทองแดงหนา $2 \text{ oz}$ ทึบต่อเนื่อง ความร้อน $125^{\circ}\text{C}$ จากเพาเวอร์สเตจจึงไหลลัดเลาะผ่านระนาบทองแดงเข้าสู่ Thermal Ground Pad ของคริสตัลโดยตรง (Thermal Bleed)
2. **Crystal Temperature Gradient:** ตัวถังคริสตัลมีฝั่งหนึ่งร้อนกว่าอีกฝั่งหนึ่งถึง $15^{\circ}\text{C}$ ทำให้เกิดความเค้นเชิงกลบนแผ่นผลึกควอตซ์ (Piezoelectric Stress) ส่งผลให้ความถี่แกว่งตัวหลุดออกจากช่วงที่ฟังก์ชันชดเชยอุณหภูมิรับได้
3. **การขาด Thermal Relief & Isolation:** ไม่มีร่องตัดความร้อน (Thermal Slit) หรือการบีบคอคอดทองแดงเพื่อแยกวงจร Clock ออกจากโซนพลังงาน

---

### Step-by-Step Engineering Checklist: เช็กลิสต์ตรวจแบบความร้อน 10 ข้อ (熱設計検図 10箇条)

ก่อนที่ Senior Engineer จะลงนามอนุมัติปล่อยไฟล์บอร์ด (Gerber Sign-off) จะต้องตรวจผ่านเช็กลิสต์ทั้ง 10 ข้อนี้อย่างเคร่งครัด:

```
[ SENIOR THERMAL DESIGN REVIEW CHECKLIST ]
[ ] 1. Power Budget & Worst-Case Loss Matrix Validation
[ ] 2. Thermal Derating Rule Verification (T_j <= T_max - 20°C)
[ ] 3. ePad Thermal Via Treatment (VIPPO or Stencil Matrix)
[ ] 4. Thermal Relief vs Solid Copper Pour Rule Compliance
[ ] 5. Thermal Isolation of Sensitive Components (XTAL, ADC, Vref)
[ ] 6. Electrolytic Capacitor Life Expectancy Margin (>10,000 hrs)
[ ] 7. Airflow Obstruction & Component Staggering Verification
[ ] 8. TIM Selection & Clamping Pressure Tolerances (BLT Control)
[ ] 9. Chassis Screw Thermal Grounding & Keep-out Clearances
[ ] 10. Thermal Bow & Twist Warpage Control (IPC-TM-650 <= 0.75%)
```

#### รายละเอียดขั้นตอนปฏิบัติสำคัญ:

- **ข้อที่ 1: การแยกโซนร้อนออกจากโซนอ่อนไหว (Zoning & Slit Routing):**
  - คริสตัลออสซิลเลเตอร์และวงจรแอนะล็อกความแม่นยำสูง ต้องอยู่ห่างจากเพาเวอร์สเตจอย่างน้อย $\ge 25 \text{ mm}$
  - เซาะร่องตัดบอร์ด (Milled Slit) ความกว้าง $1.0 - 1.5 \text{ mm}$ ลึกตลอดแนวระหว่างเพาเวอร์และแอนะล็อก โดยเหลือสะพานทองแดงเชื่อม Ground ข้ามเพียงจุดเดียว (Narrow Ground Neck กว้างไม่เกิน $1.5 \text{ mm}$) เพื่อให้อิมพีแดนซ์กราวด์ต่ำ แต่ความต้านทานความร้อนสูง

- **ข้อที่ 2: กฎการใช้ Thermal Relief บนขาต่อและบอร์ด:**
  - จุดต่อสายไฟภายนอก (High-Current Connectors, Screw Terminals): **ห้ามใช้ Solid Copper Connection เด็ดขาด** เพราะความร้อนจากหัวแร้งบัดกรีหรือเตา Wave Solder จะถูกดูดหายไปหมด ทำให้เกิดรอยบัดกรีเย็น (Cold Solder Joint) ให้ใช้ Thermal Relief แบบซี่ล้อกว้าง (Spoke Width $\ge 0.5 \text{ mm}$, 4 ซี่ขึ้นไป)
  - แผ่น Exposed Thermal Pad ใต้ไอซีเพาเวอร์ (ePad): **ต้องเชื่อมต่อแบบ Solid Pour เต็มแผ่น $100\%$ เข้ากับระนาบทองแดงและ Thermal Vias เสมอ** ห้ามใส่ Thermal Relief ใต้ชิปเด็ดขาด มิฉะนั้นความต้านทานความร้อนจะพุ่งสูง

- **ข้อที่ 3: การประเมินอายุการใช้งานของตัวเก็บประจุเคมี (Capacitor Life Audit):**
  - คำนวณอายุการใช้งานของ E-Cap ตามกฎ $10^{\circ}\text{C}$ ของอาร์เรเนียส:
    $$L_{expected} = L_{base} \cdot 2^{\frac{T_{rated} - T_{actual}}{10}} \cdot \left( \frac{I_{ripple, max}}{I_{ripple, actual}} \right)^2$$
  - ต้องมั่นใจว่า $L_{expected}$ มีค่าเกินอายุใช้งานของผลิตภัณฑ์อย่างน้อย $1.5$ เท่า

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คันจิ (Kanji) | คานะ (Kana) | คำอ่าน (Romaji) | ภาษาอังกฤษ / คำแปลภาษาไทย |
| :--- | :--- | :--- | :--- |
| **熱設計検図** | ねつせっけいけんず | Netsu Sekkei Kenzu | Thermal Design Review (การตรวจแบบความร้อน) |
| **熱スリット** | ねつすりっと | Netsu Suritto | Thermal Isolation Slit / Milled Slot |
| **ディレーティング基準** | でぃれーてぃんぐきじゅん | Dirētingu Kijun | Derating Criteria / Standard |
| **アレニウス則** | あれにうすそく | Areniusu-soku | Arrhenius Rule (กฎการเร่งความเสื่อมสภาพ) |
| **熱回り込み** | ねつまわりこみ | Netsu Mawarikomi | Thermal Bleed / Conductive Heat Ingress |
| **局所発熱** | きょくしょはつねつ | Kyokusho Hatsunetsu | Localized Hotspot (จุดความร้อนสะสมเฉพาะที่) |
| **サーマルリリーフ** | さーまるりりーふ | Sāmaru Rirīfu | Thermal Relief (ซี่ระบายความร้อนเพื่อการบัดกรี) |
| **はんだ濡れ性** | はんだぬれせい | Handa Nure-sei | Solder Wettability (การเปียกกระจายของตะกั่ว) |
| **芋はんだ** | いもはんだ | Imo-handa | Cold Solder Joint (รอยต่อบัดกรีเย็น/ไม่ละลาย) |
| **反り許容値** | そりきょようち | Sori Kyoyōchi | Warpage Tolerance (ค่าความโก่งงอที่ยอมรับได้) |
| **エレクトロマイグレーション** | えれくとろまいぐれーしょん | Erekutromaigurēshon | Electromigration (การย้ายถิ่นของเนื้อโลหะ) |
| **放熱経路** | ほうねつけいろ | Hōnetsu Keiro | Heat Dissipation Path |

---

### 3.2 บันทึกการตรวจแบบของ Senior Engineer (検図指摘事項 - Kenzu Comments)

#### คอมเมนต์ที่ 1: ตรวจพบความร้อนจาก Power Stage ไหลย้อนเข้าคริสตัลออสซิลเลเตอร์
> **検図指摘 (Kenzu Feedback 1):**  
> 「MCUクロック回路周辺の熱レイアウトについて重大な指摘を行います。20MHz水晶振動子（X101）が三相モーター駆動用MOSFET（Q101〜Q106）のドレイン銅箔プレーンから僅か6.5mmの位置に配置されており、L2/L4のGNDプレーンを介して直接的な熱伝導（熱回り込み）が発生しています。熱解析シミュレーション結果では、MOSFETフル負荷時に水晶振動子表面温度が$+105^\circ\text{C}$（許容限界近傍）まで上昇し、周波数熱ドリフトに起因するCAN-FD通信同期外れ（Loss of Lock）を引き起こす危険性があります。直ちに水晶振動子および発振負荷容量をパワーラインから最低25mm以上離隔したクリーンエリアへ再配置してください。また、パワーゾーンとMCUゾーンの境界基板に幅1.2mmの『熱スリット（スリット穴加工）』を挿入し、熱遮断対策を講じることを強く指示します。」  
> *(คำแปล: ขอให้คอมเมนต์ร้ายแรงเกี่ยวกับเลย์เอาต์ความร้อนรอบวงจร Clock ของ MCU พบว่าคริสตัล 20 MHz (X101) ถูกวางห่างจาก Drain Copper Pour ของ MOSFET ขับมอเตอร์เพียง 6.5 mm ทำให้เกิดการนำความร้อนโดยตรงผ่านระนาบ GND ชั้น L2/L4 ผลจำลอง CFD ชี้ว่าเมื่อ MOSFET ทำงานเต็มโหลด อุณหภูมิผิวของคริสตัลจะพุ่งถึง +105°C เสี่ยงต่อการเกิด Frequency Drift หลุดการซิงโครไนซ์ของระบบสื่อสาร CAN-FD ขอให้ย้ายคริสตัลและโหลด C ออกไปห่างจากแนวพลังงานอย่างน้อย 25 mm เข้าสู่ Clean Area ทันที และเพิ่มการเซาะร่องตัดความร้อน Thermal Slit กว้าง 1.2 mm ที่ขอบระหว่างโซน Power กับโซน MCU เพื่อสกัดกั้นฟลักซ์ความร้อนโดยเด็ดขาด)*

#### คอมเมนต์ที่ 2: ข้อผิดพลาดเรื่อง Thermal Relief บนขั้วต่อกระแสสูงและ Exposed Pad
> **検図指摘 (Kenzu Feedback 2):**  
> 「コネクタ端子およびパワーICのランド設計について2点検図修正を求めます。第一に、大電流電源入力コネクタ（J101：定格40A）のPTHピンにおいて、内層ベタGNDへの接続がダイレクト接続（Solid Connect）となっています。熱容量が過大となり、フローはんだ付け（Wave Soldering）工程において十分な熱が伝わらず、はんだ濡れ不良およびボイドによる『芋はんだ（Cold Solder Joint）』を誘発します。接続方式を4本スポークのサーマルリリーフ（スポーク幅$\ge 0.6\text{mm}$）に変更してください。第二に、D2PAKパッケージの放熱タブ（Drain Pad）直下のベタパターンに誤ってサーマルリリーフが設定されています。放熱パッド直下のサーマルリリーフは熱伝導経路を絞り、熱抵抗を跳ね上がらせる致命的ミスです。放熱タブ直下はリリーフを完全撤廃し、ベタ直結（Solid Pour）＋放熱ビアアレイ（VIPPO）仕様へ是正してください。」  
> *(คำแปล: ขอให้แก้ไขแบบจุดบัดกรีของขั้วต่อและเพาเวอร์ไอซี 2 จุด ประการแรก ขั้วต่อสายไฟกำลังสูง J101 (พิกัด 40 A) ขา Through-hole มีการต่อตรงเข้ากับระนาบ Ground เต็มแผ่น (Solid Connect) ความจุความร้อนที่มากเกินไปจะทำให้ความร้อนจากเตา Wave Solder ไม่เพียงพอ เกิดตะกั่วไม่เปียกและรอยต่อบัดกรีเย็น (Cold Solder) ขอให้เปลี่ยนเป็น Thermal Relief แบบ 4 ก้าน (Spoke Width ≥ 0.6 mm) ประการที่สอง บน Thermal Tab ใต้ตัวถัง D2PAK มีการใส่ Thermal Relief ไว้โดยผิดพลาด ซึ่งจะบีบเส้นทางนำความร้อนและทำให้ค่า Thermal Resistance พุ่งสูงขึ้น ขอให้ลบ Thermal Relief ใต้แผ่นระบายความร้อนออกทั้งหมด เปลี่ยนเป็น Solid Pour 100% เชื่อมต่อกับ Thermal Vias Array (VIPPO) ทันที)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณอายุการใช้งานแบบเร่งด้วยความร้อนตามสมการ Arrhenius (Junction Temperature Reduction Impact)

ในระบบอินเวอร์เตอร์ขับเคลื่อนมอเตอร์รถยนต์ไฟฟ้า (EV Inverter) วิศวกรกำลังประเมินความน่าเชื่อถือของชิป Gate Driver IC โดยสเปกกำหนดเงื่อนไขการทดสอบความน่าเชื่อถือที่อุณหภูมิความเครียด $T_{stress} = 125^{\circ}\text{C} = 398.15 \text{ K}$ มีอายุเฉลี่ยก่อนเกิดความล้มเหลว (Mean Time to Failure: $\text{MTTF}_{stress}$) เท่ากับ $2,500 \text{ ชั่วโมง}$ กำหนดให้พลังงานกระตุ้นของกลไกความล้มเหลวในเนื้อซิลิคอน $E_a = 0.70 \text{ eV}$ และค่าคงที่โบลต์ซมันน์ $k_B = 8.617 \times 10^{-5} \text{ eV/K}$

ทีมออกแบบมี 2 ทางเลือกในการจัดการความร้อนของบอร์ด:
- **การออกแบบแบบเดิม (Original PCB Layout):** ชิปทำงานที่อุณหภูมิรอยต่อ $T_{j, 1} = 105^{\circ}\text{C} = 378.15 \text{ K}$
- **การปรับปรุงความร้อน (Upgraded Thermal Design):** เพิ่ม Thermal Vias และขยายระนาบทองแดง ช่วยลดอุณหภูมิรอยต่อลงมาอยู่ที่ $T_{j, 2} = 85^{\circ}\text{C} = 358.15 \text{ K}$ (ลดลงได้ $20^{\circ}\text{C}$)

จงคำนวณ:
1. ปัจจัยเร่งความเสื่อมสภาพ ($AF$) และค่า $\text{MTTF}$ คาดการณ์ของการออกแบบเดิมที่อุณหภูมิทำงานจริง ($T_{j, 1} = 105^{\circ}\text{C}$)
2. ค่า $\text{MTTF}$ คาดการณ์ของการออกแบบที่ปรับปรุงใหม่ ($T_{j, 2} = 85^{\circ}\text{C}$)
3. อัตราการยืดอายุการใช้งาน (Lifetime Improvement Ratio: $\text{MTTF}_2 / \text{MTTF}_1$) ที่ได้รับจากการลดอุณหภูมิลงเพียง $20^{\circ}\text{C}$?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณพารามิเตอร์ $\frac{E_a}{k_B}$:**
$$\frac{E_a}{k_B} = \frac{0.70 \text{ eV}}{8.617 \times 10^{-5} \text{ eV/K}} \approx 8,123.48 \text{ K}$$

**2. คำนวณอัตราส่วนการเร่งและ MTTF สำหรับการออกแบบเดิม ($T_{j, 1} = 105^{\circ}\text{C} = 378.15 \text{ K}$):**
$$AF_1 = \exp\left[ \frac{E_a}{k_B} \left( \frac{1}{T_{stress}} - \frac{1}{T_{j, 1}} \right) \right]$$
$$\frac{1}{T_{stress}} - \frac{1}{T_{j, 1}} = \frac{1}{398.15} - \frac{1}{378.15} = 0.0025116 - 0.0026444 = -0.0001328 \text{ K}^{-1}$$

$$AF_1 = \exp[8,123.48 \times (-0.0001328)] = \exp[-1.0788] \approx 0.33999$$

ดังนั้น ปัจจัยการยืดอายุเมื่อเทียบกับการทดสอบที่ $125^{\circ}\text{C}$ คือ $\frac{1}{AF_1} \approx 2.941$:
$$\text{MTTF}_1 = \text{MTTF}_{stress} \times \frac{1}{AF_1} = 2,500 \text{ hours} \times 2.941 \approx 7,353 \text{ hours}$$

**3. คำนวณอัตราส่วนการเร่งและ MTTF สำหรับการออกแบบใหม่ ($T_{j, 2} = 85^{\circ}\text{C} = 358.15 \text{ K}$):**
$$\frac{1}{T_{stress}} - \frac{1}{T_{j, 2}} = \frac{1}{398.15} - \frac{1}{358.15} = 0.0025116 - 0.0027921 = -0.0002805 \text{ K}^{-1}$$

$$AF_2 = \exp[8,123.48 \times (-0.0002805)] = \exp[-2.2786] \approx 0.10242$$

$$\text{MTTF}_2 = \text{MTTF}_{stress} \times \frac{1}{AF_2} = 2,500 \text{ hours} \times \frac{1}{0.10242} \approx 24,408 \text{ hours}$$

**4. คำนวณอัตราส่วนการยืดอายุการใช้งาน:**
$$\frac{\text{MTTF}_2}{\text{MTTF}_1} = \frac{24,408}{7,353} \approx 3.32 \text{ เท่า (เพิ่มขึ้น } 232\%)$$

**บทวิเคราะห์ของ Senior Engineer:**
- การปรับปรุงการระบายความร้อนเพื่อดึงอุณหภูมิรอยต่อลงมาเพียง **$20^{\circ}\text{C}$ (จาก $105^{\circ}\text{C}$ เหลือ $85^{\circ}\text{C}$)** ช่วยยืดอายุการใช้งานเฉลี่ยของชิปเซมิคอนดักเตอร์ได้ถึง **$3.3$ เท่า** (จาก 7,353 ชั่วโมงเป็นมากกว่า 24,400 ชั่วโมง ซึ่งคิดเป็นเกือบ 3 ปีของการทำงานต่อเนื่องตลอด 24 ชม.)
- นี่คือเหตุผลที่วิศวกรอาวุโสยอมลงทุนในกระบวนการ Kenzu และปรับแก้ Layout อย่างละเอียด เพราะทุกๆ องศาที่ลดลงหมายถึงต้นทุนการเคลมประกันในสนามจริงที่ลดลงอย่างมหาศาล

---

### คำถามที่ 2: การคำนวณการสกัดกั้นความร้อนด้วย Thermal Isolation Slit และผลกระทบต่อ EMI Inductance

บอร์ด 4-Layer FR-4 หนา $t_{board} = 1.6 \text{ mm}$ มีระนาบทองแดง Ground Plane หนา $1 \text{ oz}$ ($35 \ \mu\text{m}$, $k_{Cu} = 385 \text{ W/(m}\cdot\text{K)}$) มีระยะห่างระหว่างจุดกำเนิดความร้อน (Power FET ที่ $T_{hot} = 110^{\circ}\text{C}$) ไปยังจุดรับความร้อน (Precision Reference IC ที่ต้องการ $T_{cold} \le 50^{\circ}\text{C}$) เท่ากับ $L = 20 \text{ mm}$ โดยมีหน้ากว้างของระนาบทองแดงเดิม $W = 30 \text{ mm}$

เพื่อสกัดกั้นความร้อน วิศวกรเจาะร่องตัดอากาศ (Air Slit, $k_{air} \approx 0.026 \text{ W/(m}\cdot\text{K)}$) ตัดขวางระนาบทองแดง โดยเหลือสะพานเชื่อมทองแดงแคบๆ (Ground Neck Bridge) กว้างเพียง $W_{bridge} = 2.0 \text{ mm}$ ยาว $L_{bridge} = 3.0 \text{ mm}$ 

จงคำนวณ:
1. อัตราการนำความร้อนผ่านแผ่นทองแดง ($Q_{solid}$) ในกรณีเดิมที่ไม่มีร่องตัด
2. อัตราการนำความร้อนผ่านสะพานทองแดงแคบ ($Q_{slit}$) ในกรณีที่มีร่องตัดความร้อน
3. อัตราส่วนการลดทอนฟลักซ์ความร้อน ($Q_{slit} / Q_{solid}$) และอธิบายข้อควรระวังเรื่อง Ground Return Inductance สำหรับสัญญาณความถี่สูงที่วิ่งข้ามสะพานนี้?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณการนำความร้อนของแผ่นทองแดงเดิม ($W = 30 \text{ mm} = 0.03 \text{ m}$, $t_{Cu} = 35 \ \mu\text{m} = 35 \times 10^{-6} \text{ m}$):**
- พื้นที่หน้าตัดทองแดง:
  $$A_{Cu, 1} = W \cdot t_{Cu} = 0.03 \text{ m} \times (35 \times 10^{-6} \text{ m}) = 1.05 \times 10^{-6} \text{ m}^2$$
- ความต่างอุณหภูมิ $\Delta T = 110^{\circ}\text{C} - 50^{\circ}\text{C} = 60^{\circ}\text{C}$
- ความต้านทานความร้อนตามแนวความยาว $L = 20 \text{ mm} = 0.02 \text{ m}$:
  $$R_{\theta, solid} = \frac{L}{k_{Cu} \cdot A_{Cu, 1}} = \frac{0.02 \text{ m}}{385 \text{ W/(m}\cdot\text{K)} \cdot (1.05 \times 10^{-6} \text{ m}^2)} \approx 49.47 \ ^{\circ}\text{C/W}$$
- ฟลักซ์ความร้อนที่นำผ่าน:
  $$Q_{solid} = \frac{\Delta T}{R_{\theta, solid}} = \frac{60^{\circ}\text{C}}{49.47 \ ^{\circ}\text{C/W}} \approx 1.213 \text{ W}$$

**2. คำนวณการนำความร้อนเมื่อมี Thermal Slit (เหลือสะพาน $W_{bridge} = 2.0 \text{ mm} = 0.002 \text{ m}$, $L_{bridge} = 3.0 \text{ mm} = 0.003 \text{ m}$):**
- พื้นที่หน้าตัดสะพานทองแดง:
  $$A_{Cu, 2} = W_{bridge} \cdot t_{Cu} = 0.002 \text{ m} \times (35 \times 10^{-6} \text{ m}) = 7.0 \times 10^{-8} \text{ m}^2$$
- ความต้านทานความร้อนของสะพานแคบ:
  $$R_{\theta, bridge} = \frac{L_{bridge}}{k_{Cu} \cdot A_{Cu, 2}} = \frac{0.003 \text{ m}}{385 \text{ W/(m}\cdot\text{K)} \cdot (7.0 \times 10^{-8} \text{ m}^2)} \approx 111.32 \ ^{\circ}\text{C/W}$$
- รวมกับความต้านทานส่วนที่เหลือก่อนถึงสะพาน (โดยประมาณ $R_{\theta, total} \approx R_{\theta, bridge} + R_{\theta, lead-in} \approx 140 \ ^{\circ}\text{C/W}$):
- ฟลักซ์ความร้อนใหม่:
  $$Q_{slit} = \frac{\Delta T}{R_{\theta, total}} \approx \frac{60^{\circ}\text{C}}{140 \ ^{\circ}\text{C/W}} \approx 0.428 \text{ W}$$
  *(และในสภาวะจริง ความร้อนที่สะพานจะแผ่ออกสู่อากาศโดยรอบ ทำให้ความร้อนที่ไปถึงปลายทางลดลงเหลือต่ำกว่า $0.15 \text{ W}$)*

**3. ผลกระทบต่อ EMI และ Ground Return Path:**
- **ความสำเร็จด้านความร้อน:** การเซาะร่องตัดช่วยลดการส่งผ่านความร้อนลงได้มากกว่า **$75\% - 85\%$** ป้องกันไม่ให้ไอซีอ้างอิงแรงดันเกิด Thermal Drift ได้อย่างสมบูรณ์
- **กับดักด้าน EMC/EMI ที่ Senior Engineer ต้องระวัง:**
  - ร่องตัดแอร์สลิต (Air Slit) จะตัดขาดระนาบกราวด์ **ห้ามเดินสายสัญญาณความเร็วสูง (High-Speed Signals เช่น SPI, I2C, PWM) ลอยข้ามร่องตัดเด็ดขาด!**
  - หากสัญญาณวิ่งข้ามร่องตัด กระแสไหลกลับ (Return Current) จะไม่สามารถวิ่งใต้เส้นสัญญาณได้ แต่ถูกบีบให้เลี้ยวอ้อมไปตามสะพานแคบ ก่อให้เกิด **Large Return Loop Inductance** ขนาดใหญ่ ซึ่งทำหน้าที่เป็นสายอากาศกระจายคลื่นแม่เหล็กไฟฟ้า (Radiated Emission Spikes) ทะลุเกณฑ์ CISPR 25 ทันที
  - **กฎเหล็ก:** สัญญาณทุกเส้นที่ต้องเชื่อมต่อระหว่างสองโซน จะต้องวิ่งเกาะข้ามไปบนสะพานทองแดงแคบ (Bridge Neck) เดียวกันกับระนาบกราวด์เท่านั้น

---

### คำถามที่ 3: การประเมินความเสียหายจากการย้ายถิ่นของเนื้อทองแดง (Electromigration) ตามกฎของ Black

ลายทองแดงบนเลเยอร์ผิวนอกของบอร์ด (Surface Trace) ส่งผ่านกระแสสลับพัลส์ไปยังมอเตอร์ด้วยกระแสประสิทธิผล $I_{RMS} = 15 \text{ A}$ ความกว้างของลายทองแดง $W = 1.0 \text{ mm}$ และความหนาทองแดง $t = 35 \ \mu\text{m}$ ($1 \text{ oz}$) 

ภายใต้การออกแบบเดิม ลายทองแดงนี้อยู่ใกล้จุดสะสมความร้อน ทำให้มีอุณหภูมิทำงานคงที่ที่ $T_1 = 125^{\circ}\text{C} = 398.15 \text{ K}$ และมีค่าอายุการใช้งานเฉลี่ยก่อนที่ลายทองแดงจะขาดจาก Electromigration ($\text{MTTF}_1$) เท่ากับ $40,000 \text{ ชั่วโมง}$ (ประมาณ 4.5 ปี)

กำหนดให้สมการของ Black มีค่า $n = 2$ และค่าพลังงานกระตุ้นของการย้ายถิ่นของอะตอมทองแดงตามแนวขอบผลึก (Grain Boundary Diffusion) $E_a = 0.85 \text{ eV}$ ($k_B = 8.617 \times 10^{-5} \text{ eV/K}$)

หากในขั้นตอน Kenzu วิศวกรอาวุโสสั่งปรับปรุง 2 อย่างพร้อมกัน:
1. ขยายความกว้างของลายทองแดงเป็น 2 เท่า ($W_{new} = 2.0 \text{ mm}$) ซึ่งทำให้ความหนาแน่นกระแส ($J$) ลดลงเหลือครึ่งหนึ่ง
2. เพิ่ม Copper Pour ระบายความร้อน จนทำให้อุณหภูมิของลายทองแดงลดลงมาอยู่ที่ $T_2 = 95^{\circ}\text{C} = 368.15 \text{ K}$

จงคำนวณหาค่าอายุการใช้งานเฉลี่ยใหม่ ($\text{MTTF}_2$) ในหน่วยชั่วโมง และคิดเป็นกี่เท่าของการออกแบบเดิม?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. สมการของ Black สำหรับการคำนวณเปรียบเทียบ:**
$$\text{MTTF} = \frac{A}{J^n} \cdot \exp\left( \frac{E_a}{k_B \cdot T} \right)$$

อัตราส่วนอายุการใช้งาน $\frac{\text{MTTF}_2}{\text{MTTF}_1}$:
$$\frac{\text{MTTF}_2}{\text{MTTF}_1} = \left( \frac{J_1}{J_2} \right)^n \cdot \exp\left[ \frac{E_a}{k_B} \left( \frac{1}{T_2} - \frac{1}{T_1} \right) \right]$$

**2. คำนวณผลกระทบจากการลดความหนาแน่นกระแส ($\frac{J_1}{J_2}$):**
เมื่อความกว้างเพิ่มขึ้นเป็น 2 เท่า ความหนาแน่นกระแสจะลดลงครึ่งหนึ่ง ($J_2 = 0.5 J_1$ หรือ $J_1 / J_2 = 2$):
$$\text{Current Factor} = \left( \frac{J_1}{J_2} \right)^2 = (2)^2 = 4$$

**3. คำนวณผลกระทบจากการลดอุณหภูมิ ($\frac{1}{T_2} - \frac{1}{T_1}$):**
- พารามิเตอร์ $\frac{E_a}{k_B} = \frac{0.85}{8.617 \times 10^{-5}} \approx 9,864.22 \text{ K}$
- ความต่างของส่วนกลับอุณหภูมิ:
  $$\frac{1}{T_2} - \frac{1}{T_1} = \frac{1}{368.15} - \frac{1}{398.15} = 0.0027163 - 0.0025116 = +0.0002047 \text{ K}^{-1}$$

คำนวณพจน์เอกซ์โพเนนเชียล:
$$\text{Temp Factor} = \exp[9,864.22 \times 0.0002047] = \exp[2.0192] \approx 7.532$$

**4. คำนวณอายุการใช้งานใหม่รวมกัน ($\text{MTTF}_2$):**
$$\frac{\text{MTTF}_2}{\text{MTTF}_1} = (\text{Current Factor}) \times (\text{Temp Factor}) = 4 \times 7.532 \approx 30.13 \text{ เท่า!}$$

คำนวณอายุการใช้งานใหม่:
$$\text{MTTF}_2 = 40,000 \text{ hours} \times 30.13 \approx 1,205,200 \text{ hours!}$$
*(หรือเท่ากับมากกว่า 137 ปี!)*

**บทสรุปของ Senior Engineer:**
- การลดความหนาแน่นกระแสลง $50\%$ ช่วยยืดอายุได้ 4 เท่า
- แต่การลดอุณหภูมิลง $30^{\circ}\text{C}$ ช่วยยืดอายุได้มากถึง **$7.5$ เท่า**
- เมื่อนำผลทั้งสองมารวมกัน อายุการใช้งานก่อนเกิด Electromigration เพิ่มขึ้นสูงถึง **30 เท่า** เปลี่ยนผลิตภัณฑ์จากอุปกรณ์ที่มีความเสี่ยงจะพังหลังหมดประกัน 4.5 ปี กลายเป็นผลิตภัณฑ์เกรดยานยนต์ที่มีความน่าเชื่อถือระดับตำนาน (Zero Field RMA) อย่างแท้จริง
