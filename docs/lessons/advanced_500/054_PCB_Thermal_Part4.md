# Lesson 054: PCB Thermal Part 4 - Metal Core PCB (MCPCB / IMS) and High-Power Thermal Management

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในงานอิเล็กทรอนิกส์กำลังสูง (High-Power Electronics) เช่น ออสซิลเลเตอร์ขับมอเตอร์รถยนต์ไฟฟ้า (EV Traction Inverter), ตัวแปลงกำลังออนบอร์ด (On-Board Charger: OBC), และไฟส่องสว่างยานยนต์กำลังสูง (Automotive High-Flux LED Headlamps) ค่าความหนาแน่นความร้อน (Heat Flux Density, $q''$) ที่ผิวของสวิตช์กำลัง (SiC MOSFETs, GaN FETs, หรือ High-Power LEDs) มักพุ่งสูงเกินกว่า $50 - 150 \text{ W/cm}^2$ ซึ่งเกินขีดจำกัดสูงสุดของการระบายความร้อนผ่าน FR-4 มาตรฐานแบบ Multilayer ร่วมกับ Thermal Vias (ซึ่งจำกัดความหนาแน่นความร้อนที่มีประสิทธิภาพอยู่ที่ไม่เกิน $10 - 25 \text{ W/cm}^2$ แม้จะวาง Via แบบอัดแน่นก็ตาม) โซลูชันระดับ Senior Hardware Architecture จึงต้องเปลี่ยนโครงสร้างวัสดุฐาน (Substrate) ไปสู่ **Metal Core PCB (MCPCB)** หรือที่เรียกว่า **Insulated Metal Substrate (IMS)**

```
+-------------------------------------------------------------------+
|               Top Copper Circuit Foil (1 oz - 4 oz / 35 - 140 µm)  |
+-------------------------------------------------------------------+
|  Thermally Conductive Dielectric Layer (38 - 150 µm, k = 1-12 W/mK)  |
+===================================================================+
|                                                                   |
|              Metal Base Plate (Aluminum 5052/6061 or Copper)       |
|                       Thickness: 1.0 - 3.0 mm                     |
|                                                                   |
+-------------------------------------------------------------------+
```

### 1.1 สถาปัตยกรรมและโครงสร้างทางกายภาพของ IMS (Insulated Metal Substrate)

โครงสร้างของ 1-Layer Single-Sided MCPCB ประกอบด้วย 3 ชั้นหลักที่มีปฏิสัมพันธ์เชิงกลและเชิงความร้อนอย่างใกล้ชิด:

1. **Circuit Layer (แผ่นฟอยล์ทองแดงเดินลายวงจร):** 
   ความหนามาตรฐานตั้งแต่ $1 \text{ oz } (35 \ \mu\text{m})$ จนถึง $4 \text{ oz } (140 \ \mu\text{m})$ หรือมากกว่าในงาน High-Current Busbar เพื่อลดการสูญเสียพลังงาน $I^2 R$ Conduction Loss และช่วยกระจายความร้อนในแนวระนาบ ($x-y$ plane heat spreading) ก่อนส่งผ่านลงชั้นล่าง

2. **Dielectric Layer (ฉนวนนำความร้อนสูง):** 
   เป็นชั้นที่สำคัญและวิกฤตที่สุดในแง่ Reliability เป็นพอลิเมอร์เรซิน (อีพ็อกซีหรือโพลีอิไมด์) ที่ผสมผสานอนุภาคเซรามิก (Ceramic Fillers เช่น $\text{Al}_2\text{O}_3$ (Alumina), $\text{AlN}$ (Aluminum Nitride), หรือ $\text{BN}$ (Boron Nitride)) เพื่อให้มีสภาพนำความร้อน ($k_{diel}$) ระหว่าง $1.0 \text{ W/(m}\cdot\text{K)}$ ถึง $12.0 \text{ W/(m}\cdot\text{K)}$ (เปรียบเทียบกับ FR-4 ทั่วไปที่มี $k \approx 0.25 - 0.3 \text{ W/(m}\cdot\text{K)}$) โดยมีความหนาของชั้นฉนวน ($t_{diel}$) เพียง $38 \ \mu\text{m} - 150 \ \mu\text{m}$ เพื่อลดความต้านทานความร้อนในแกน $z$

3. **Base Plate (แผ่นฐานโลหะรองรับ):** 
   มักเป็นอลูมิเนียมอัลลอยด์เกรด **Al 5052** (งานทั่วไป ดัดงอได้ดี, $k \approx 138 \text{ W/(m}\cdot\text{K)}$) หรือ **Al 6061** (งานโครงสร้างความแข็งแรงสูง ชุบอะโนไดซ์ได้, $k \approx 167 \text{ W/(m}\cdot\text{K)}$) หรือในกรณี Extreme Power Density จะใช้ **Copper Base Plate (C1100)** ($k \approx 390 \text{ W/(m}\cdot\text{K)}$) โดยมีความหนา $1.0 \text{ mm}, 1.5 \text{ mm}, 2.0 \text{ mm},$ จนถึง $3.0 \text{ mm}$

### 1.2 สมการวิเคราะห์ความต้านทานความร้อนและการกระจายความร้อน (1D & 2D Thermal Resistance Model)

ความต้านทานความร้อนในแนวตั้งฉาก ($z$-axis) ผ่านชั้น Dielectric ของ MCPCB สามารถคำนวณได้จากกฎการนำความร้อนของฟูริเยร์ (Fourier's Law of Heat Conduction):

$$R_{\theta,diel} = \frac{t_{diel}}{k_{diel} \cdot A_{eff}} \quad [^{\circ}\text{C/W}]$$

โดยที่:
- $t_{diel}$ คือ ความหนาของชั้นไดอิเล็กทริก ($\text{m}$)
- $k_{diel}$ คือ สภาพนำความร้อนของไดอิเล็กทริก ($\text{W/(m}\cdot\text{K)}$)
- $A_{eff}$ คือ พื้นที่หน้าตัดที่มีประสิทธิผลในการส่งผ่านความร้อน ($\text{m}^2$)

เมื่อความร้อนแพร่กระจายจากหน้าสัมผัสของ Component Pad (ขนาด $W_{pad} \times L_{pad}$) ลงสู่ชั้น Dielectric มุมการกระจายความร้อนแบบมุมสมมุติ (Spreading Angle $\theta \approx 45^{\circ}$) จะขยายพื้นที่ $A_{eff}$ ขึ้นเล็กน้อยตามความหนา $t_{diel}$:

$$A_{eff} = (W_{pad} + 2 \cdot t_{diel} \cdot \tan\theta) \cdot (L_{pad} + 2 \cdot t_{diel} \cdot \tan\theta)$$

เนื่องจากชั้น Dielectric มีความบางมาก ($t_{diel} \ll W_{pad}$), พื้นที่ $A_{eff} \approx A_{pad}$ ทำให้ $R_{\theta,diel}$ ขึ้นอยู่กับอัตราส่วน $t_{diel} / k_{diel}$ โดยตรง ซึ่งอุตสาหกรรมมักระบุในรูปของ **Thermal Impedance ต่อหนึ่งหน่วยพื้นที่ (Unit Thermal Impedance)**:

$$\Theta_{diel} = \frac{t_{diel}}{k_{diel}} \quad [^{\circ}\text{C}\cdot\text{cm}^2/\text{W} \text{ หรือ } \text{K}\cdot\text{in}^2/\text{W}]$$

| ชนิดของ Substrate / Dielectric | ความหนา Dielectric ($t_{diel}$) | สภาพนำความร้อน ($k$) | Unit Thermal Impedance ($\Theta$) | Breakdown Voltage ($V_{bd}$) |
| :--- | :--- | :--- | :--- | :--- |
| **Standard FR-4 (1.6 mm)** | 1600 µm | 0.3 W/(m·K) | 53.3 °C·cm²/W | > 40 kV (AC) |
| **Thin FR-4 Core** | 100 µm | 0.3 W/(m·K) | 3.33 °C·cm²/W | ~ 4 - 5 kV |
| **Commercial IMS (Standard)** | 75 µm | 1.5 W/(m·K) | 0.50 °C·cm²/W | ~ 3.0 kV (AC) |
| **High-Performance IMS** | 75 µm | 3.0 W/(m·K) | 0.25 °C·cm²/W | ~ 4.0 kV (AC) |
| **Ultra-High Thermal IMS (AlN Filled)** | 38 µm | 8.0 - 10.0 W/(m·K) | 0.038 - 0.048 °C·cm²/W | ~ 2.0 - 3.0 kV (AC) |
| **Direct Bond Copper (DBC) on $\text{Al}_2\text{O}_3$** | 380 µm (Ceramic) | 25 W/(m·K) | 0.15 °C·cm²/W | > 10 kV (AC) |
| **DBC / AMB on $\text{Si}_3\text{N}_4$ (Silicon Nitride)** | 320 µm (Ceramic) | 90 W/(m·K) | 0.035 °C·cm²/W | > 15 kV (AC) |

### 1.3 การประนีประนอมระหว่างค่าฉนวนไฟฟ้าและความต้านทานความร้อน (Thermal Resistance vs. Dielectric Breakdown Trade-off)

ปัญหาทางวิศวกรรมที่ท้าทายที่สุดของ MCPCB คือ **Trade-off สามเส้า (Trilemma)** ระหว่าง:
1. **Thermal Resistance ($R_{\theta} \propto t_{diel} / k_{diel}$):** ต้องการลด $t_{diel}$ ให้บางที่สุด และเพิ่ม Ceramic Filler ให้มากที่สุด
2. **Dielectric Withstand Voltage ($V_{bd} = E_{bd} \cdot t_{diel}$):** ต้องการเพิ่ม $t_{diel}$ ให้หนา เพื่อรองรับแรงดันไฟฟ้ารั่วและแรงดันทดสอบ Hi-Pot (High Potential Test) ตามมาตรฐานความปลอดภัย (เช่น IEC/UL 62368, UL 746B, IEC 60664-1)
3. **Mechanical Flexibility & Peel Strength:** เมื่อเรซินถูกอัดแน่นด้วยอนุภาคเซรามิก ($>60\%$ โดยปริมาตร) เรซินจะเปราะ (Brittle), แรงยึดเหนี่ยวทองแดง (Peel Strength) ลดลงต่ำกว่า $1.0 \text{ N/mm}$, และเสี่ยงต่อการเกิด Micro-cracks เมื่อเกิดความเค้นจากการตัดเจาะ (Shearing/Punching) หรือ Thermal Cycling

แรงดันพังทลายของฉนวน (Dielectric Breakdown Voltage, $V_{bd}$) ถูกกำหนดโดย:

$$V_{bd} = E_{bd} \cdot t_{diel}$$

โดยที่ $E_{bd}$ คือ Dielectric Strength ของฉนวน (โดยทั่วไปอยู่ที่ $20 - 60 \text{ kV/mm}$ ขึ้นอยู่กับประเภทของเรซินและปริมาณฟิลเลอร์) 
สำหรับระบบอินเวอร์เตอร์ 400V - 800V EV แรงดันทดสอบ Hi-Pot มาตรฐานอุตสาหกรรมยานยนต์ตาม ISO 6469-3 หรือ UL 840 มักกำหนดไว้ที่:

$$V_{test} = 2 \cdot V_{working} + 1000 \text{ V}_{\text{RMS}} \quad \text{หรือ } 2.5 - 3.5 \text{ kV}_{\text{AC}} \text{ เป็นเวลา 60 วินาที}$$

หากวิศวกรเลือกชั้น Dielectric บางเกินไป เช่น $38 \ \mu\text{m}$ ที่มี $E_{bd} = 30 \text{ kV/mm}$ แรงดันพังทลายทางทฤษฎีคือ $1,140 \text{ V}$ ซึ่งไม่สามารถผ่านการทดสอบ Hi-Pot ได้ และจะเกิดไฟฟ้าลัดวงจรระหว่างวงจรกับ Base Plate ทันที

### 1.4 ปัญหา Thermal Expansion Mismatch ($\Delta\text{CTE}$) และความเค้นเชิงกล (Thermo-Mechanical Stress)

ค่าสัมประสิทธิ์การขยายตัวเนื่องจากความร้อน (Coefficient of Thermal Expansion, CTE) ในแนวราบ ($x-y$ plane) ระหว่างวัสดุต่างๆ ในระบบ MCPCB มีความแตกต่างกันอย่างมีนัยสำคัญ:

- **Silicon / SiC / GaN Die:** $\text{CTE} \approx 2.5 - 3.5 \text{ ppm/}^{\circ}\text{C}$
- **Ceramic Package ($\text{Al}_2\text{O}_3$):** $\text{CTE} \approx 6.5 - 7.5 \text{ ppm/}^{\circ}\text{C}$
- **Copper Foil:** $\text{CTE} \approx 16.5 - 17.0 \text{ ppm/}^{\circ}\text{C}$
- **Aluminum Base Plate (Al 5052/6061):** $\text{CTE} \approx 23.0 - 24.0 \text{ ppm/}^{\circ}\text{C}$
- **Dielectric Resin (Above $T_g$):** $\text{CTE} \approx 40 - 80 \text{ ppm/}^{\circ}\text{C}$

```
+-------------------------------------------------------------+
|  Package (CTE ~ 6 ppm/°C)       <--- Low Expansion          |
|    |      |  (Solder Joint)                                 |
|  Copper Pad (CTE ~ 17 ppm/°C)                               |
|  Dielectric Layer                                           |
|  Aluminum Base (CTE ~ 24 ppm/°C) <--- Huge Thermal Expansion|
+-------------------------------------------------------------+
               ===> High Shear Strain on Solder Joint!
```

เมื่อระบบเริ่มทำงานและอุณหภูมิแกว่งตัวจาก $-40^{\circ}\text{C}$ ไปยัง $+125^{\circ}\text{C}$ หรือ $+150^{\circ}\text{C}$ ความเค้นเฉือน (Shear Strain, $\Delta\gamma$) ที่กระทำต่อจุดบัดกรี (Solder Joint) และชั้น Dielectric สามารถประมาณการได้ตามสมการของ Coffin-Manson:

$$\Delta\gamma = \frac{L_{package}}{2 \cdot h_{solder}} \cdot (\alpha_{base} - \alpha_{pkg}) \cdot \Delta T$$

โดยที่:
- $L_{package}$ คือ ขนาดความยาวของตัวถังอุปกรณ์ ($\text{m}$)
- $h_{solder}$ คือ ความสูงของชั้นประสานบัดกรี (Solder Standoff Height, $\text{m}$)
- $\alpha_{base}, \alpha_{pkg}$ คือ CTE ของแผ่นฐานอลูมิเนียมและตัวถังอุปกรณ์ ($\text{ppm/}^{\circ}\text{C}$)
- $\Delta T$ คือ ช่วงการแกว่งตัวของอุณหภูมิในการทำงาน ($\Delta T = T_{max} - T_{min}$)

เนื่องจากอลูมิเนียมขยายตัวเร็วกว่าตัวถังเซรามิกหรือชิปสารกึ่งตัวนำเกือบ 4 เท่า ความเค้นเฉือนที่เกิดขึ้นจะสะสมในเม็ดบัดกรี นำไปสู่การเกิด Thermal Fatigue Cracking ในระยะยาวอย่างรวดเร็ว (มักล้มเหลวก่อน 1,000 รอบ Thermal Shock หากออกแบบ Standoff ไม่เหมาะสม)

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)

**เหตุการณ์:** บอร์ดไฟหน้าอัจฉริยะ (Adaptive Driving Beam: ADB) สำหรับรถยนต์หรู ผลิตโดยใช้ Single-Layer MCPCB ฐานอลูมิเนียมหนา $1.5 \text{ mm}$ พร้อมชั้น Dielectric หนา $75 \ \mu\text{m}$ ($k = 3.0 \text{ W/(m}\cdot\text{K)}$) ติดตั้ง High-Power Matrix LED จำนวน 24 ตัว (กินกำลังไฟรวม $70 \text{ W}$) 

**อาการล้มเหลว:**
1. ในขั้นตอนการผลิต Mass Production (EOL - End of Line Test) เกิด Fail การทดสอบ Hi-Pot (Dielectric Withstand Test ที่ $2.5 \text{ kV}_{\text{AC}}$) ถึง $4.2\%$ ของจำนวนบอร์ดทั้งหมด เกิด Breakdown Arcing ที่ขอบบอร์ดและรูยึดน็อต
2. บอร์ดที่ผ่านการทดสอบ เมื่อส่งไปทำ Thermal Cycling Test ($-40^{\circ}\text{C} \leftrightarrow +125^{\circ}\text{C}$, 500 cycles) พบอาการ LED ดับแบบ Intermittent เกิดจากเม็ดบัดกรีใต้ตัวถัง LED แตก (Solder Joint Cracking)
3. รูเจาะยึดน็อตลงฮีตซิงก์เกิดอาการแตกร้าวของฉนวนทองแดง (Delamination & Copper Cracking) หลังขันสกรูด้วยทอร์ก $1.2 \text{ N}\cdot\text{m}$

```
[Defect Mechanism: Edge Flashover & Dielectric Breakdown]
                     Screw Head
                         │
      Copper Trace       ▼
       ┌────┐       ╔═════════╗
       │    │       ║ Screw   ║
═══════╪════╪═══════╬═════════╬════════ (Creepage < 1.0mm)
Dielectric  │       ║ (Metal) ║ ────► Spark Arc! (2.5kV Hi-Pot)
────────────────────╨─────────╨────────────────────────
Aluminum Baseplate (GND/Chassis)
```

**Root Cause Analysis (RCA):**
1. **Edge Creepage Distance สั้นเกินไป:** วิศวกร PCB ลาก Copper Trace และ Copper Pour ห่างจากขอบตัดขอบบอร์ด (V-cut / Shearing Edge) และขอบรูเจาะสกรูเพียง $0.5 \text{ mm}$ ในขณะที่กระบวนการ V-cut และ Die Punching ดึงเศษเสี้ยนโลหะอลูมิเนียม (Aluminum Burrs) ขึ้นมาตามรอยตัด ทำให้ระยะ Creepage/Clearance ทางอากาศและพื้นผิวเหลือไม่ถึง $0.2 \text{ mm}$ เกิด Arcing ทะลุฉนวนที่ $2.5 \text{ kV}$
2. **Solder Fatigue จาก $\Delta\text{CTE}$:** วิศวกรเลือกใช้ความหนาตะกั่วบัดกรี (Solder Standoff) ต่ำเกินไป (Stencil Aperture $1:1$ หนาเพียง $100 \ \mu\text{m}$ ทำให้ยุบตัวเหลือ Standoff ต่ำกว่า $35 \ \mu\text{m}$) เมื่อเจอแรงเฉือนจากความต่าง CTE ของอลูมิเนียม ($24 \text{ ppm}$) กับ Ceramic Package ($7 \text{ ppm}$) ตะกั่วจึงล้าและแตกร้าว
3. **การกดทับของหัวสกรู:** รูเจาะยึดสกรูไม่มีการเว้นระยะห่างทองแดง (Screw Keep-out Zone) พอหัวสกรูและแหวนสปริงกดลงไป แรงกด Mechanically Creep บดขยี้ชั้น Dielectric จนบางลงและแตกร้าว

---

### Step-by-Step Engineering Guideline & Checklist ในการออกแบบ MCPCB

#### ขั้นตอนที่ 1: กำหนด Edge Keep-out & Clearance สำหรับ Hi-Pot Safety
เพื่อป้องกันการเกิด Arcing ระหว่าง Copper Circuit Layer กับ Aluminum Baseplate ให้ปฏิบัติตามกฎเกณฑ์ระยะห่างขั้นต่ำ:

- **V-Cut Edge Keep-out:** ดึงทองแดงและชั้น Solder Mask ออกห่างจากแนวกึ่งกลาง V-cut อย่างน้อย $\ge 1.0 \text{ mm}$ (สำหรับ Hi-Pot $\le 1.5 \text{ kV}$) และ $\ge 1.5 - 2.0 \text{ mm}$ (สำหรับ Hi-Pot $\ge 2.5 \text{ kV}$)
- **Routed Edge (Milling):** ระยะทองแดงถึงขอบกัดอย่างน้อย $\ge 0.8 \text{ mm}$
- **Tooling / Mounting Holes (Non-Plated Through Hole):**
  - รัศมี Keep-out ทองแดงรอบขอบรู $= r_{hole} + \text{รัศมีหัวสกรู/แหวน} + 1.2 \text{ mm}$
  - ห้ามวางลายทองแดงใต้แหวนรองสกรูเด็ดขาด เพราะแรงอัด Torque จะทำลายเนื้อ Dielectric

```
+---------------------------------------------------------------+
|  MCPCB Edge Design Rule:                                      |
|                                                               |
|  |<-- 1.5mm Keepout -->|                                      |
|  [====================]  <-- Copper Trace / Pour              |
|  [--------------------]  <-- Dielectric Layer                 |
|  |                    |                                       |
|  |                    +------------------+                    |
|  |                    | Aluminum Base    | <-- V-Cut line     |
|  +--------------------+------------------+                    |
+---------------------------------------------------------------+
```

#### ขั้นตอนที่ 2: การควบคุม Solder Standoff เพื่อแก้ปัญหา CTE Mismatch
- ออกแบบความหนาของ Stencil อย่างน้อย $130 - 150 \ \mu\text{m}$ ($5 - 6 \text{ mils}$)
- เลือกใช้เม็ดบัดกรีผสมสารเติมแต่งที่ทนทานต่อ Thermal Cycling เช่น โลหะผสมที่มีส่วนผสมของ Indium, Bismuth, หรือ Antimony (เช่น SAC-Innolot: $\text{Sn3.8Ag0.7Cu3Bi1.4Sb0.15Ni}$) แทน SAC305 มาตรฐาน ซึ่ง Innolot สามารถยืดอายุความล้าของจุดบัดกรีบน MCPCB ได้มากกว่า 3 เท่า
- รักษาความสูงของ Solder Standoff หลัง Reflow ให้ได้ไม่ต่ำกว่า $50 - 75 \ \mu\text{m}$

#### ขั้นตอนที่ 3: กฎการเดินลายวงจรข้ามเส้น (Jumper vs. 2-Layer MCPCB)
ใน Single-Layer MCPCB ไม่สามารถเจาะ Plated Through Hole (PTH) ผ่านแผ่นฐานโลหะเพื่อข้ามเลเยอร์ได้เนื่องจากจะลัดวงจรลงกราวด์:
- **Low-Cost Strategy:** ใช้อุปกรณ์ **$0\ \Omega$ SMD Jumper Resistors (ขนาด 0805, 1206 หรือ 2512)** ในการลากสัญญาณข้ามรางไฟ (Power Rails) หรือข้ามสายอื่น การใช้ Jumper 2-3 ตัวคุ้มค่ากว่าการเปลี่ยนไปใช้ 2-Layer MCPCB ถึง $40 - 60\%$
- **High-Density Strategy:** หากจำเป็นต้องใช้ 2-Layer MCPCB ทางผู้ผลิตต้องเจาะรูโอเวอร์ไซส์ (Oversized Holes) ในแผ่นอลูมิเนียม ฉีดเรซินฉนวนเข้าไปอุดรู (Resin Plug) แล้วจึงเจาะรูเล็กลงเพื่อทำ Through-Hole Plating ซึ่งกระบวนการนี้ทำให้ต้นทุนเพิ่มขึ้นมหาศาล และมีจุดเสี่ยงต่อการหลุดร่อนของฉนวน

#### ขั้นตอนที่ 4: การยึดประกอบบอร์ดเข้ากับ Chasis / Heatsink (Thermal Interface Material: TIM)
แม้แผ่นอลูมิเนียมจะนำความร้อนได้ดี แต่พื้นผิวด้านหลังของ MCPCB จะมีความโก่งงอ (Bow and Twist) จากแรงดึงของ Copper Foil (ความโก่งงอมาตรฐานตาม IPC-TM-650 อนุญาตได้ถึง $0.75\% - 1.0\%$):
- ต้องทาซิลิโคนระบายความร้อน (Thermal Grease) หรือใช้ Phase Change Material (PCM) บางขนาด $25 - 50 \ \mu\text{m}$ ระหว่างแผ่นอลูมิเนียมของ MCPCB กับ Heat Sink ภายนอกเสมอ
- กำหนดระยะห่างของจุดยึดสกรู (Screw Pitch) ไม่เกิน $40 - 60 \text{ mm}$ และควบคุมแรงบิด (Torque Control) อย่างแม่นยำเพื่อป้องกันการโก่งตัวที่ทำให้เกิดช่องว่างอากาศ (Air Gap) ใต้จุดที่มีความร้อนสูง

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คันจิ (Kanji) | คานะ (Kana) | คำอ่าน (Romaji) | ภาษาอังกฤษ / คำแปลภาษาไทย |
| :--- | :--- | :--- | :--- |
| **アルミ基板** | あるみきばん | Arumi Kiban | Aluminum PCB / MCPCB (บอร์ดฐานอลูมิเนียม) |
| **金属ベース基板** | きんぞくべーすきばん | Kinzoku Bēsu Kiban | Metal Base Printed Wiring Board (IMS) |
| **高放熱絶縁層** | こうほうねつぜつえんそう | Kō-hōnetsu Zetsuen-sō | High-Thermal-Conductivity Dielectric Layer |
| **絶縁破壊電圧** | ぜつえんはかいでんあつ | Zetsuen Hakai Den'atsu | Dielectric Breakdown Voltage (แรงดันพังทลายของฉนวน) |
| **耐電圧試験** | たいでんあつしけん | Taiden'atsu Shiken | Withstand Voltage Test / Hi-Pot Test |
| **沿面距離** | えんめんきょり | Enmen Kyori | Creepage Distance (ระยะทางตามผิวฉนวน) |
| **空間距離** | くうかんきょり | Kūkan Kyori | Clearance Distance (ระยะทางผ่านอากาศ) |
| **熱膨張係数** | ねつぼうちょうけいすう | Netsu Bōchō Keisū | Coefficient of Thermal Expansion (CTE) |
| **熱応力** | ねつおうりょく | Netsu Ōryoku | Thermal Stress (ความเค้นเนื่องจากความร้อน) |
| **反り・ねじれ** | そり・ねじれ | Sori / Nejire | Bow and Twist (การโก่งงอและการบิดเบี้ยวของแผ่นวงจร) |
| **バリ** | ばり | Bari | Burr (เศษเสี้ยนโลหะคมจากการตัดเจาะ) |
| **締結トルク** | ていけつとるく | Teiketsu Toruku | Tightening Torque (แรงบิดในการขันยึดสกรู) |

---

### 3.2 บันทึกการตรวจแบบของ Senior Engineer (検図指摘事項 - Kenzu Comments)

#### คอมเมนต์ที่ 1: ตรวจพบระยะขอบแผ่นทองแดงและรูยึดเสี่ยงต่อการเกิด Hi-Pot Breakdown
> **検図指摘 (Kenzu Feedback 1):**  
> 「基板外形VカットラインおよびM3ビス固定穴周囲の銅箔クリアランスを確認しました。現在、パターン端面から外形線までのマージンが0.5mmしか確保されていません。本製品は車載高圧環境下で使用され、出荷検査にてAC 2.5kV（1分間）の耐電圧試験（ハイポット試験）が必須仕様となっています。Vカット加工時のバリ（金属粉）や加工公差を考慮すると、沿面距離不足により絶縁破壊（フラッシュオーバー）に至るリスクが極めて高いです。外形Vカット境界からは最低1.5mm以上、ビス穴座面（ワッシャー外径）からは最低1.2mm以上の絶縁クリアランス（導体禁止エリア）を再設定し、レジスト開口部も含めて検図修正してください。」  
> *(คำแปล: ตรวจสอบระยะห่างทองแดงบริเวณแนว V-cut ขอบบอร์ดและรอบรูยึดสกรู M3 พบว่าปัจจุบันมีระยะเผื่อจากขอบลายวงจรถึงเส้นรอบรูปเพียง 0.5 mm เท่านั้น ผลิตภัณฑ์นี้ใช้งานในสภาพแวดล้อมไฟฟ้าแรงสูงยานยนต์ และมีข้อกำหนดบังคับต้องทดสอบ Withstand Voltage Test ที่ AC 2.5 kV (1 นาที) ในการตรวจสอบก่อนส่งมอบ เมื่อพิจารณาเศษเสี้ยนโลหะจากการตัด V-cut และค่าพิกัดความเผื่อในการผลิต ความเสี่ยงที่จะเกิดการพังทลายของฉนวน (Flashover) จากระยะ Creepage ไม่เพียงพอนั้นสูงมาก ขอให้แก้ไขระยะ Clearance ห้ามมีทองแดงจากแนว V-cut ออกไปอย่างน้อย 1.5 mm ขึ้นไป และจากหน้าสัมผัสแหวนรองสกรูอย่างน้อย 1.2 mm ขึ้นไป พร้อมทั้งปรับแก้ช่องเปิด Solder Mask ให้เรียบร้อย)*

#### คอมเมนต์ที่ 2: ความเค้นเชิงความร้อนบนรอยต่อบัดกรีของชิปกำลังสูง (Thermal Fatigue Warning)
> **検図指摘 (Kenzu Feedback 2):**  
> 「高出力LED（3535セラミックパッケージ）直下の放熱設計について。アルミベース（CTE $\approx 24\text{ ppm/}^\circ\text{C}$）とLEDパッケージ（CTE $\approx 7\text{ ppm/}^\circ\text{C}$）の間で熱膨張係数のミスマッチが顕著です。設計データではメタルマスク開口率が100%（厚み100µm）となっており、リフロー後のハンダスタンドオフ高さが実測30µm未満になる懸念があります。車載規格の温度サイクル試験（$-40^\circ\text{C} \sim +125^\circ\text{C}$、1000サイクル）において、ハンダ接合部のせん断疲労破壊（はんだクラック）を招く恐れがあります。メタルマスク厚を130µmに変更するとともに、熱疲労耐性に優れた車載対応高信頼性はんだ合金（Innolot等）の採用を検討してください。」  
> *(คำแปล: เกี่ยวกับการระบายความร้อนใต้ LED กำลังสูง (แพ็กเกจเซรามิก 3535) พบความแตกต่างของ CTE อย่างมีนัยสำคัญระหว่างฐานอลูมิเนียม (~24 ppm/°C) และตัวถัง LED (~7 ppm/°C) ข้อมูลการออกแบบกำหนด Aperture ของ Metal Mask ไว้ที่ 100% (ความหนา 100 µm) ซึ่งกังวลว่าความสูง Solder Standoff หลัง Reflow จะเหลือน้อยกว่า 30 µm ส่งผลให้เกิดความเสียหายจากความล้าเฉือน (Solder Cracking) ในการทดสอบ Temperature Cycle ของยานยนต์ (-40°C ถึง +125°C, 1000 cycles) ได้ ขอให้เปลี่ยนความหนาสเตนซิลเป็น 130 µm และพิจารณาใช้โลหะบัดกรีเกรดยานยนต์ความเชื่อถือได้สูง เช่น Innolot เพื่อรองรับความล้าจากความร้อน)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณเปรียบเทียบ Thermal Resistance ระหว่าง FR-4 Thermal Vias และ MCPCB

โมดูล LED กำลังสูงแบบ Ceramic Package มี Thermal Pad ขนาด $3.0 \text{ mm} \times 3.0 \text{ mm}$ ปล่อยความร้อน $P_{loss} = 9.0 \text{ W}$ วิศวกรกำลังพิจารณา 2 โซลูชัน:
- **ตัวเลือก A:** บอร์ด 4-Layer FR-4 (ความหนารวม $1.6 \text{ mm}$) เจาะ Thermal Vias ขนาด Drill $0.3 \text{ mm}$, Plating Thickness $25 \ \mu\text{m}$ จำนวน 9 รู อัดแน่นใต้ Pad โดยทองแดงมีสภาพนำความร้อน $k_{Cu} = 385 \text{ W/(m}\cdot\text{K)}$ และ FR-4 มี $k_{FR4} = 0.3 \text{ W/(m}\cdot\text{K)}$
- **ตัวเลือก B:** บอร์ด 1-Layer MCPCB ฐานอลูมิเนียมหนา $1.5 \text{ mm}$ ($k_{Al} = 160 \text{ W/(m}\cdot\text{K)}$) ใช้ชั้น Dielectric หนา $75 \ \mu\text{m}$ ที่มีสภาพนำความร้อน $k_{diel} = 3.0 \text{ W/(m}\cdot\text{K)}$

จงคำนวณหาความต้านทานความร้อนในแกน $z$ ($R_{\theta, z}$) ของทั้งสองตัวเลือก และอุณหภูมิที่เพิ่มขึ้น ($\Delta T$) จากด้านบนลงสู่ด้านล่างของบอร์ด โดยไม่คิดการ Spreading ด้านข้าง?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณตัวเลือก A (FR-4 พร้อม 9 Thermal Vias):**
- พื้นที่กระบอกทองแดงของแต่ละ Via ($d_{hole} = 0.3 \text{ mm}$, $t_{plate} = 0.025 \text{ mm}$):
  $$A_{Cu, 1} \approx \pi \cdot d_{hole} \cdot t_{plate} = \pi \cdot (0.3 \times 10^{-3}) \cdot (0.025 \times 10^{-3}) \approx 2.356 \times 10^{-8} \text{ m}^2$$
- พื้นที่ทองแดงรวม 9 รู:
  $$A_{Cu, total} = 9 \times 2.356 \times 10^{-8} \approx 2.12 \times 10^{-7} \text{ m}^2$$
- ความต้านทานความร้อนของท่อทองแดง 9 Vias ข้ามความหนา $L = 1.6 \text{ mm} = 1.6 \times 10^{-3} \text{ m}$:
  $$R_{\theta, Cu} = \frac{L}{k_{Cu} \cdot A_{Cu, total}} = \frac{1.6 \times 10^{-3}}{385 \cdot 2.12 \times 10^{-7}} \approx 19.60 \ ^{\circ}\text{C/W}$$
- พื้นที่ FR-4 ที่เหลืออยู่ ($A_{pad} - A_{holes}$):
  $$A_{pad} = (3.0 \times 10^{-3})^2 = 9.0 \times 10^{-6} \text{ m}^2$$
  $$A_{FR4} \approx 9.0 \times 10^{-6} - 9 \cdot (\frac{\pi \cdot (0.35 \times 10^{-3})^2}{4}) \approx 8.13 \times 10^{-6} \text{ m}^2$$
- ความต้านทานความร้อนของเนื้อ FR-4 ขนานกัน:
  $$R_{\theta, FR4} = \frac{1.6 \times 10^{-3}}{0.3 \cdot 8.13 \times 10^{-6}} \approx 656 \ ^{\circ}\text{C/W}$$
- ความต้านทานความร้อนรวมแบบขนาน:
  $$R_{\theta, total(A)} = \frac{R_{\theta, Cu} \cdot R_{\theta, FR4}}{R_{\theta, Cu} + R_{\theta, FR4}} \approx \frac{19.60 \times 656}{19.60 + 656} \approx 19.03 \ ^{\circ}\text{C/W}$$
- อุณหภูมิที่เพิ่มขึ้นสำหรับตัวเลือก A:
  $$\Delta T_A = P \cdot R_{\theta, total(A)} = 9.0 \text{ W} \times 19.03 \ ^{\circ}\text{C/W} \approx 171.3 \ ^{\circ}\text{C}$$
  *(ซึ่งสูงเกินขีดจำกัดอย่างสิ้นเชิง ชิปจะพังทลายทันที)*

**2. คำนวณตัวเลือก B (MCPCB):**
ความต้านทานความร้อนของ MCPCB ประกอบด้วยความต้านทานของชั้น Dielectric และแผ่นฐาน Aluminum อนุกรมกัน:
- ความต้านทานของ Dielectric Layer ($t_{diel} = 75 \ \mu\text{m} = 75 \times 10^{-6} \text{ m}$, $A_{pad} = 9.0 \times 10^{-6} \text{ m}^2$):
  $$R_{\theta, diel} = \frac{t_{diel}}{k_{diel} \cdot A_{pad}} = \frac{75 \times 10^{-6}}{3.0 \cdot 9.0 \times 10^{-6}} \approx 2.78 \ ^{\circ}\text{C/W}$$
- ความต้านทานของ Aluminum Base Plate ($t_{Al} = 1.5 \text{ mm} = 1.5 \times 10^{-3} \text{ m}$):
  $$R_{\theta, Al} = \frac{t_{Al}}{k_{Al} \cdot A_{pad}} = \frac{1.5 \times 10^{-3}}{160 \cdot 9.0 \times 10^{-6}} \approx 1.04 \ ^{\circ}\text{C/W}$$
  *(หมายเหตุ: ในความเป็นจริง อลูมิเนียมมีความหนา $1.5 \text{ mm}$ ความร้อนจะ Spreading ออกเป็นรูปปิรามิด 45 องศา ทำให้พื้นที่จริงกว้างกว่า $A_{pad}$ มาก และค่า $R_{\theta, Al}$ จริงจะเหลือต่ำกว่า $0.3 \ ^{\circ}\text{C/W}$)*
- ความต้านทานความร้อนรวมในแกน $z$ ของ MCPCB (1D Worst-Case):
  $$R_{\theta, total(B)} = R_{\theta, diel} + R_{\theta, Al} = 2.78 + 1.04 = 3.82 \ ^{\circ}\text{C/W}$$
- อุณหภูมิที่เพิ่มขึ้นสำหรับตัวเลือก B:
  $$\Delta T_B = P \cdot R_{\theta, total(B)} = 9.0 \text{ W} \times 3.82 \ ^{\circ}\text{C/W} \approx 34.4 \ ^{\circ}\text{C}$$

**บทสรุปของ Senior Engineer:** MCPCB ลด Thermal Resistance ลงได้ถึง **5 เท่า** เมื่อเทียบกับ FR-4 Thermal Vias ทำให้ $\Delta T$ ลดจาก $171.3^{\circ}\text{C}$ เหลือเพียง $34.4^{\circ}\text{C}$ ช่วยให้ LED สามารถทำงานได้ภายใต้สภาวะปกติอย่างปลอดภัย

---

### คำถามที่ 2: การวิเคราะห์ความล้มเหลวแบบ Dielectric Breakdown จาก Partial Discharge ในระบบ EV 800V

ในระบบขับเคลื่อนรถยนต์ไฟฟ้าระบบ 800V (Working Voltage $V_{DC} = 800 \text{ V}$, มีแรงดันกระชาก Transient Overshoot จากการสวิตชิ่งของ SiC สูงถึง $1,200 \text{ V}$ ที่ความถี่ $100 \text{ kHz}$) มีการใช้ 1-Layer MCPCB ควบคุมเกตและสวิตช์กำลัง วิศวกรเลือกใช้ชั้นฉนวน Dielectric หนา $50 \ \mu\text{m}$ ที่ระบุสเปก Breakdown Voltage ไว้ที่ $3.0 \text{ kV}_{\text{DC}}$ จากการทดสอบเบื้องต้น บอร์ดผ่านการทดสอบ Hi-Pot มาตรฐานที่ $2.5 \text{ kV}_{\text{AC}}$ นาน 60 วินาทีได้สำเร็จ แต่เมื่อนำไปทดสอบความทนทานระยะยาวแบบ Accelerated Life Testing (ALT) ในสภาพแวดล้อม $85^{\circ}\text{C} / 85\% \text{ RH}$ เป็นเวลา 500 ชั่วโมง บอร์ดกลับเกิดการลัดวงจรทะลุชั้นฉนวนลงแผ่นอลูมิเนียม (Catastrophic Insulation Breakdown)

จงอธิบายกลไกความล้มเหลวทางฟิสิกส์ (Root Cause Failure Mechanism) ที่เกิดขึ้น พร้อมชี้แนะแนวทางการแก้ไขเชิงวิศวกรรมวัสดุและการออกแบบ?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. ปรากฏการณ์ Partial Discharge (PD) ภายใต้ $dv/dt$ ความถี่สูง:**
- การทดสอบ Hi-Pot มาตรฐาน ($2.5 \text{ kV}_{\text{AC}}$ ที่ $50/60 \text{ Hz}$) วัดเฉพาะค่า **Short-term Breakdown Field** แต่ไม่ได้วัดพฤติกรรมระยะยาวภายใต้แรงดันสวิตชิ่งความถี่สูง ($100 \text{ kHz}, dv/dt > 50 \text{ V/ns}$)
- ภายในชั้น Dielectric ที่มีสารเติมแต่งเซรามิก ($\text{Al}_2\text{O}_3$ หรือ $\text{AlN}$) มักมีโพรงอากาศขนาดไมครอน (Micro-voids) หลงเหลือจากกระบวนการผลิตเรซิน ค่า Permittivity ของโพรงอากาศคือ $\varepsilon_r \approx 1.0$ ในขณะที่เนื้อเรซินผสมเซรามิกมี $\varepsilon_r \approx 4.5 - 6.0$
- สนามไฟฟ้าภายใน Micro-void จะมีความเข้มข้นสูงกว่าเนื้อเรซินรอบข้างตามสัดส่วนของ Permittivity ($E_{void} = \varepsilon_{r, diel} \cdot E_{bulk}$)
- เมื่อมีแรงดันพัลส์สวิตชิ่ง $1,200 \text{ V}$ ซ้ำๆ ที่ $100 \text{ kHz}$ ค่าสนามไฟฟ้าใน Micro-void จะพุ่งเกินค่าเริ่มต้นของการเกิดโคโรนา/การคายประจุบางส่วน (**Partial Discharge Inception Voltage: PDIV**) ทำให้เกิด Micro-arcs คายประจุขึ้นภายในโพรงอากาศนับแสนครั้งต่อวินาที

**2. การเสื่อมสภาพแบบก้าวหน้า (Electro-chemical Degradation & Carbon Tracking):**
- การเกิด Partial Discharge ปลดปล่อยอิเล็กตรอนพลังงานสูงและรังสี UV ทำลายพันธะโมเลกุลไฮโดรคาร์บอนของโพลีเมอร์เรซิน (Bond Scission) ก่อให้เกิดก๊าซโอโซนและคาร์บอนอิสระ (Carbonization)
- ประกอบกับสภาวะทดสอบความชื้นสูง ($85\% \text{ RH}$) โมเลกุลของน้ำซึมผ่าน Micro-cracks เข้าไปรวมตัวกับไอออน สิ่งนี้นำไปสู่ปรากฏการณ์ **Conductive Anodic Filament (CAF)** และ **Electrical Treeing** ค่อยๆ ก่อตัวเป็นเส้นนำไฟฟ้าคาร์บอนเชื่อมต่อระหว่าง Copper Trace ด้านบนกับ Aluminum Base ด้านล่าง จนกระทั่งชั้นฉนวนสูญเสียสภาพต้านทานและพังทลายลงในที่สุด

**3. แนวทางแก้ไขระดับ Senior Engineering:**
1. **เพิ่มความหนาของ Dielectric Layer:** ปรับเพิ่มความหนาจาก $50 \ \mu\text{m}$ เป็นอย่างน้อย $100 - 150 \ \mu\text{m}$ เพื่อลดความเข้มสนามไฟฟ้าเฉลี่ย ($E = V / t$) ให้ต่ำกว่าจุด PDIV
2. **คัดเลือกผู้ผลิตที่ผ่านการทดสอบ PDIV ตาม IEC 60270:** กำหนดเกณฑ์ Partial Discharge Inception Voltage ใน Specification ว่าต้องสูงกว่า $\ge 1.5 \times V_{peak} = 1,800 \text{ V}_{\text{peak}}$ ที่ $100 \text{ kHz}$
3. **ใช้ฉนวนกลุ่ม Polyimide หรือ Silicon-Organic Hybrid:** แทน Epoxy มาตรฐาน เนื่องจากมีความทนทานต่อ Corona Discharge และทนอุณหภูมิสูง ($T_g > 200^{\circ}\text{C}$) ได้ดีกว่ามาก
4. **พิจารณา Direct Bond Copper (DBC) หรือ Active Metal Brazing (AMB) บน $\text{Si}_3\text{N}_4$:** สำหรับสวิตช์กำลัง 800V หากกำลังสูญเสียสูงมาก การเปลี่ยนจาก Resin-based MCPCB ไปเป็น Ceramic Substrate แท้ๆ จะขจัดปัญหา Partial Discharge ในเรซินได้อย่างเด็ดขาด

---

### คำถามที่ 3: ปัญหา Parasitic Capacitance ของ MCPCB กับ Common-Mode Noise ในระบบ Switching Inverter

ในวงจร Half-Bridge Inverter ที่ใช้สวิตช์ GaN FET วางอยู่บน 1-Layer Aluminum MCPCB จุดเชื่อมต่อกึ่งกลางของ Half-Bridge (Switching Node: SW) มีแผ่นทองแดง Copper Pour ขนาดพื้นที่ $A = 12 \text{ cm}^2$ เพื่อช่วยระบายความร้อนจากตัวถัง FET ลงสู่ฐานอลูมิเนียม ซึ่งแผ่นฐานอลูมิเนียมนี้ถูกยึดขันสกรูแน่นติดกับโครงตัวถังรถยนต์ (Chassis Ground) 

ชั้น Dielectric ของ MCPCB มีความหนา $t_{diel} = 75 \ \mu\text{m}$ และมีค่าความจุเหนี่ยวนำสัมพัทธ์ $\varepsilon_r = 5.2$ หากสวิตช์ GaN ทำการสวิตชิ่งด้วยความเร็ว $dv/dt = 80 \text{ V/ns}$ ที่แรงดันบัส $400 \text{ V}$

จงคำนวณ:
1. ค่าความจุปรสิต ($C_{parasitic}$) ระหว่างสวิตชิ่งโหนด (SW Node) กับโครงอลูมิเนียม Chassis Ground
2. ขนาดของกระแส Common-Mode Displacement Current ($I_{CM} = C \cdot \frac{dv}{dt}$) ที่ฉีดทะลุชั้นฉนวนลงโครงรถ และผลกระทบต่อการทดสอบ CISPR 25 Class 5 EMI Conducted Emissions?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณค่าความจุปรสิต ($C_{parasitic}$):**
โครงสร้างระหว่าง Copper Pour, ชั้น Dielectric, และ Aluminum Baseplate มีลักษณะเป็นตัวเก็บประจุแบบแผ่นขนาน (Parallel Plate Capacitor):

$$C_{parasitic} = \frac{\varepsilon_0 \cdot \varepsilon_r \cdot A}{t_{diel}}$$

โดยที่:
- $\varepsilon_0 = 8.854 \times 10^{-12} \text{ F/m}$ (Permittivity of Free Space)
- $\varepsilon_r = 5.2$
- $A = 12 \text{ cm}^2 = 12 \times 10^{-4} \text{ m}^2 = 1.2 \times 10^{-3} \text{ m}^2$
- $t_{diel} = 75 \ \mu\text{m} = 75 \times 10^{-6} \text{ m}$

แทนค่าในสมการ:
$$C_{parasitic} = \frac{(8.854 \times 10^{-12}) \cdot 5.2 \cdot (1.2 \times 10^{-3})}{75 \times 10^{-6}}$$
$$C_{parasitic} = \frac{5.5249 \times 10^{-14}}{75 \times 10^{-6}} \approx 7.37 \times 10^{-10} \text{ F} = 737 \text{ pF}$$

ค่า $C_{parasitic} \approx 737 \text{ pF}$ เป็นค่าที่สูงมากสำหรับสวิตชิ่งโหนดความเร็วสูง!

**2. คำนวณกระแส Common-Mode Displacement Current ($I_{CM}$):**
กระแสพัลส์ที่ถูกฉีดทะลุชั้น Dielectric ลง Chassis Ground เกิดจากอัตราการเปลี่ยนแปลงแรงดัน:

$$I_{CM} = C_{parasitic} \cdot \frac{dv}{dt}$$

โดยที่ $\frac{dv}{dt} = 80 \text{ V/ns} = 80 \times 10^9 \text{ V/s}$:

$$I_{CM} = (737 \times 10^{-12} \text{ F}) \cdot (80 \times 10^9 \text{ V/s}) \approx 58.96 \text{ A}!$$

**3. บทวิเคราะห์ผลกระทบต่อ EMI และแนวทางแก้ไข:**
- **ผลกระทบอย่างรุนแรงต่อ EMI (CISPR 25 Class 5):** 
  กระแสพัลส์ยอดแหลมสูงถึงเกือบ $59 \text{ A}$ ที่ฉีดลงโครงตัวถังรถยนต์ทุกครั้งที่ GaN FET สวิตชิ่ง จะไหลวนกลับผ่านระบบกราวด์และ LISN (Line Impedance Stabilization Network) ก่อให้เกิดสัญญาณรบกวน Common-Mode Noise มหาศาล ครอบคลุมแถบความถี่ตั้งแต่ $150 \text{ kHz}$ ไปจนถึงเกินกว่า $100 \text{ MHz}$ ซึ่งจะทำให้ผลการทดสอบ Conductive Emissions เกินขีดจำกัดมาตรฐาน CISPR 25 Class 5 มากกว่า $40 - 60 \text{ dB}\mu\text{V}$
- **การปรับปรุงการออกแบบเชิงสถาปัตยกรรม (Design Countermeasures):**
  1. **ลดพื้นที่ Switching Node Pad:** แยกฟังก์ชันระบายความร้อนออกจากจุด SW Node โดยให้วาง Pad ของ SW Node ให้เล็กที่สุดเท่าที่กระแสไหลได้ แล้วไประบายความร้อนที่ฝั่ง Ground Node หรือ Power Bus Node ที่มีแรงดันไฟฟ้าคงที่ ($dv/dt \approx 0$) แทน
  2. **ใช้ Shielding Layer (2-Layer MCPCB with Shield):** ใช้ MCPCB แบบ 2 เลเยอร์ โดยเพิ่มแผ่นทองแดงชั้นกลางเชื่อมต่อกับ DC Bus Return (GND ภายในวงจร) ทำหน้าที่เป็น Faraday Shield ดักจับกระแส Displacement Current ให้ไหลวนกลับแหล่งจ่ายภายใน ไม่ให้รั่วลงสู่ Aluminum Chassis Ground
  3. **ติดตั้ง Common-Mode Choke & Y-Capacitors:** เพิ่มฟิลเตอร์กรองสัญญาณรบกวนที่สเตจอินพุตของแหล่งจ่ายไฟ แต่การแก้ที่ต้นทาง (Source Suppression โดยลด $A_{SW}$ และคุม $dv/dt$) เป็นแนวทางที่มีประสิทธิภาพและคุ้มทุนที่สุด
