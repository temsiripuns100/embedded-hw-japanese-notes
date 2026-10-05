# Lesson 088: PCB DFM Part 8 - Advanced HDI DFM, Laser Microvias, Stacked vs Staggered Vias, and ELIC Manufacturing Yield

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในยุคของอุปกรณ์พกพาขนาดกะทัดรัด (Mobile & Wearable Devices), โมดูลหน่วยประมวลผล AI ขั้นสูง (Edge AI Accelerators), และอุปกรณ์สื่อสาร 5G/6G การจัดวางวงจรพิมพ์ต้องเผชิญกับชิปแพ็กเกจแบบ **Ultra-Fine Pitch BGA (พิตช์ $0.4\text{ mm}$, $0.35\text{ mm}$ จนถึง $0.30\text{ mm}$)** ซึ่งมีจำนวนขาสูงกว่า 1,000 พินบนพื้นที่ไม่กี่ตารางเซนติเมตร

เทคโนโลยีแผงวงจรพิมพ์แบบดั้งเดิม (Through-Hole Multilayer) ไม่สามารถรองรับความหนาแน่นของการเดินสาย (Routing Density) ในระดับนี้ได้อีกต่อไป อุตสาหกรรมจึงต้องพึ่งพา **เทคโนโลยีการเชื่อมต่อความหนาแน่นสูง (High Density Interconnect - HDI)** ซึ่งกำหนดมาตรฐานตาม **IPC-2226 (Sectional Design Standard for High Density Interconnect (HDI) Printed Boards)**

หัวใจสำคัญของ HDI คือ **เลเซอร์ไมโครเวีย (Laser Microvias)**, **เวียซ้อนทับ (Stacked Microvias)**, **เวียเยื้องศูนย์ (Staggered Microvias)**, และ **สถาปัตยกรรมเชื่อมต่อทุกชั้น (Any-Layer HDI หรือ Every Layer Interconnect - ELIC)** อย่างไรก็ตาม การผลิตไมโครเวียที่มีขนาดรูเจาะระดับ $75 - 100\ \mu\text{m}$ ต้องเผชิญกับขีดจำกัดทางฟิสิกส์ของการเจาะด้วยลำแสงเลเซอร์ (Laser Ablation Physics), พลศาสตร์การชุบทองแดงถมรู (Superfilling Copper Electroplating), และความเค้นเชิงกล-ความร้อนในแนวดิ่ง (Z-axis Thermal Stress per IPC-WP-023)

```
+-----------------------------------------------------------------------------------------+
|                       HDI Laser Microvia Mechanics & Failure Modes                      |
|                                                                                         |
|   [ 1. Laser Ablation & Aspect Ratio ]         [ 2. Stacked vs. Staggered Reliability ] |
|                                                                                         |
|       Laser Beam (CO2 or UV 355 nm)                Stacked Microvia (High Stress)       |
|                │   │                               ┌─────────┐   CTE Mismatch!          |
|                ▼   ▼                               │ Via L3  │   Z-axis Dielectric:     |
|         ┌─────────────────┐                        ├─────────┤   alpha_z = 50-250 ppm   |
|         │ \             / │ Dielectric (H)         │ Via L2  │   Copper:                |
|         │  \ Trapezoid /  │                        ├─────────┤   alpha_Cu = 17 ppm      |
|         └───┴─────────┴───┘ Target Pad             │ Via L1  │                          |
|             D_top                                  └─────────┘ ◄── Target Pad Crack!    |
|                                                                                         |
|   Aspect Ratio AR = H / D_top <= 0.8:1             Staggered Microvia (High Reliability)|
|                                                        ┌───────┐                        |
|   [ 3. Copper Filling & Dimple Defect ]                │Via L2 │ Offset L_stagger       |
|                                                    ┌───┴───────┴───┐                    |
|       Plating Dimple (delta <= 5 μm)               │  Via L1       │                    |
|       ──┐     Dimple      ┌──                      └───────────────┘                    |
|         │\   (delta)     /│                        Stress absorbed by laminate!         |
|         │ ─────────────── │                                                             |
|         └─────────────────┘ Filled Copper                                               |
+-----------------------------------------------------------------------------------------+
```

---

### 1.1 ฟิสิกส์การเจาะด้วยเลเซอร์และอัตราส่วนกว้างยาว (Laser Ablation Physics & Aspect Ratio)

การเจาะไมโครเวียในอุตสาหกรรม PCB นิยมใช้เลเซอร์ 2 ชนิดหลักตามคุณสมบัติการดูดกลืนพลังงานของวัสดุ (Absorption Spectra):
1. **$\text{CO}_2$ Laser ($\lambda = 9.4\ \mu\text{m} - 10.6\ \mu\text{m}$):** ลำแสงถูกดูดกลืนได้ดีมากในเรซินอีพ็อกซีและเส้นใยแก้ว แต่สะท้อนออกจากผิวทองแดง ดังนั้นการเจาะต้องเปิดหน้าต่างทองแดงล่วงหน้าด้วยกระบวนการกัดกรด (Conformal Mask Opening) หรือยิงทะลุฟอยล์ทองแดงผิวบางพิเศษที่เคลือบออกไซด์ดำ (Treated Copper Foil)
2. **UV Laser ($\lambda = 355\ \text{nm}$, Nd:YVO4 หรือ Triple Harmonic Nd:YAG):** มีพลังงานโฟตอนสูง ($E_{\text{photon}} = h \cdot c / \lambda \approx 3.49\ \text{eV}$) สามารถทำลายพันธะเคมีโดยตรง (Photochemical Ablation) ทำให้สามารถเจาะทะลุได้ทั้งฟอยล์ทองแดงและโครงสร้างใยแก้วโดยไม่เกิดความร้อนสะสมรอบข้าง (Cold Ablation) ให้ขอบรูที่เรียบคมและขนาดเล็กถึง $50 - 75\ \mu\text{m}$

#### 1. กฎทางเรขาคณิตของไมโครเวียและอัตราส่วนกว้างยาว (Microvia Aspect Ratio):
ตามมาตรฐาน IPC-6012E และ IPC-2226 นิยามของไมโครเวียคือ รูที่มีความลึกไม่เกินเส้นผ่านศูนย์กลาง และมีความลึกไม่เกิน $0.25\text{ mm}$:

$$\text{Aspect Ratio (AR)} = \frac{H}{D_{\text{top}}}$$

โดยที่:
- $H$ = ความหนาของชั้นไดอิเล็กทริก (Dielectric Thickness)
- $D_{\text{top}}$ = เส้นผ่านศูนย์กลางของปากรูไมโครเวียด้านบน (Top Diameter)
- $D_{\text{bottom}}$ = เส้นผ่านศูนย์กลางของก้นรูไมโครเวียที่สัมผัสกับ Target Pad ($D_{\text{bottom}} \approx 0.70 - 0.85 \cdot D_{\text{top}}$)

#### 2. ข้อจำกัดวิกฤตของ Aspect Ratio ต่อการชุบทองแดง:
- **เกณฑ์มาตรฐานอุตสาหกรรม:** สำหรับกระบวนการชุบทองแดงแบบเติมเต็มรู (Via Filling Electroplating) อัตราส่วน $AR$ **ต้องมีค่า $\le 0.80 : 1$** (แนะนำอย่างยิ่ง $\le 0.70 : 1$ สำหรับ High-Reliability Class 3)
- หาก $AR > 0.80 : 1$ (เช่น รูแคบแต่ลึก $H = 80\ \mu\text{m}, D_{\text{top}} = 75\ \mu\text{m} \implies AR = 1.07$):
  - น้ำยาชุบและสารเติมแต่ง (Additives) จะไม่สามารถแลกเปลี่ยนสารละลายที่ก้นรูได้ทัน (Mass-Transfer Limitation)
  - เกิดปรากฏการณ์บ่วงรูตัน (Entrapped Air / Voiding) หรือเกิดโพรงกลวงตรงกลางรู (Keyhole Void) ซึ่งจะระเบิดขยายตัวเมื่อแผ่นวงจรผ่านเตาบัดกรี Reflow

---

### 1.2 เคมีและพลศาสตร์การชุบทองแดงถมรู (Superfilling Copper Electroplating & Dimple Spec)

ไมโครเวียในบอร์ด HDI จำเป็นต้องได้รับการชุบทองแดงจนเต็มรูแบบตัน (Solid Copper Filled Microvia) เพื่อทำหน้าที่เป็นแผ่นรองรับสำหรับการวางเวียซ้อนทับ (Stacked Via) หรือเป็นจุดวางลูกบัดกรีของชิป BGA โดยตรง (Via-in-Pad Plated Over - VIPPO):

```
       Suppressor Molecules (High diffusion at surface)
       ▼   ▼   ▼   ▼   ▼   ▼   ▼
     ═════════════════════════════  Copper Foil Surface (Plating Inhibit)
         \                     /
          \   ▲   ▲   ▲   ▲   /
           \  Accelerator    /      Bottom (Plating Accelerated!)
            \ (High Conc.)  /       Bottom-Up Superfilling Growth Rate >> Surface Rate
             └─────────────┘
```

#### 1. กลไกสารเติมแต่ง 3 ตัวในการชุบแบบล่างขึ้นบน (Bottom-Up Superfilling Mechanism):
1. **สารยับยั้ง (Suppressor / Carrier - เช่น PEG):** สารโมเลกุลใหญ่ที่มีค่าการแพร่ช้า จะเข้าจับตัวหนาแน่นบริเวณปากรูและผิวหน้าทองแดง ทำหน้าที่ขัดขวางไม่ให้ไอออนทองแดง ($\text{Cu}^{2+}$) เข้าไปเกาะ ทำให้การชุบบริเวณผิวหน้าเป็นไปอย่างช้าๆ
2. **สารเร่งปฏิกิริยา (Accelerator / Brightener - เช่น SPS):** โมเลกุลขนาดเล็กที่แทรกซึมลงสู่ก้นรูและถูกดูดซับไว้ เมื่อพื้นที่ผิวที่ก้นรูค่อยๆ บีบแคบลงขณะชุบ ความเข้มข้นของสารเร่งจะเพิ่มสูงขึ้นอย่างรวดเร็ว (Curvature Enhanced Accelerator Coverage - CEAC Model) ขับเคลื่อนให้อัตราการชุบทองแดงที่ก้นรูเร็วกว่าที่ปากรูหลายเท่า
3. **สารปรับระดับ (Leveler):** สารประจุบวกที่เข้าจับบริเวณขอบปากรูที่มีความหนาแน่นกระแสไฟฟ้าสูงสุด เพื่อป้องกันการสะสมตัวของทองแดงหนาเกินไปจนปากรูเชื่อมปิดก่อนที่ก้นรูจะเต็ม

#### 2. ข้อกำหนดความลึกของรอยบุ๋ม (Dimple Depth - $\delta$) และความนูน (Bump):
หลังจากการชุบทองแดงเต็มรู ผิวหน้าทองแดงเหนือกึ่งกลางไมโครเวียอาจเกิดรอยบุ๋มทรงชามคว่ำ (Dimple):

$$\text{Dimple Ratio } D\% = \left( \frac{\delta}{D_{\text{top}}} \right) \cdot 100\%$$

- **ข้อกำหนด IPC-6012E Class 3 / Automotive Grade:**
  - รอยบุ๋มสูงสุด ($\delta_{\max}$) **ต้องไม่เกิน $5.0\ \mu\text{m}$ ($0.2\text{ mil}$)**
  - ห้ามเกิดรอยนูน (Overfill Bump) เกิน **$+10.0\ \mu\text{m}$** เหนือระนาบผิว
- **ผลกระทบหาก Dimple $\delta > 7\ \mu\text{m}$:**
  - เมื่อนำไปใช้เป็น Via-in-Pad ใต้ชิป $0.4\text{ mm}$ BGA รอยบุ๋มจะกักขังฟลักซ์และฟองอากาศ (Solder Voiding in BGA Ball) เกินมาตรฐาน IPC-7095 Class 3 ($> 15\%$ Void Area) ก่อให้เกิดการแตกร้าวของลูกบัดกรีเนื่องจากความล้า (Solder Fatigue Cracking)
  - เมื่อทำ Stacked Microvia รอยบุ๋มขนาดใหญ่จะกลายเป็นจุดกักขังก๊าซและสารเคมีในชั้นถัดไป เกิดการแยกชั้นระหว่างไมโครเวียตัวล่างและตัวบน

---

### 1.3 ความเชื่อถือได้ของ Stacked Microvias เทียบกับ Staggered Microvias (IPC-WP-023)

ในแผงวงจรความหนาแน่นสูง วิศวกรสามารถเลือกวางไมโครเวียต่อเชื่อมระหว่างเลเยอร์ได้ 2 รูปแบบหลัก:

```
    [ Stacked Microvias: Concentrated Z-Stress ]     [ Staggered Microvias: Distributed Strain ]
                 Dielectric Surface                                Dielectric Surface
                   ┌──────────┐                                      ┌──────────┐
                   │  Via L3  │                                      │  Via L3  │
                   ├──────────┤ ◄── High Interface Stress            └────┬─────┘
                   │  Via L2  │                                           │  Dogbone Trace
                   ├──────────┤                                      ┌────┴─────┐
                   │  Via L1  │                                      │  Via L2  │
                   └────┬─────┘                                      └────┬─────┘
                        │                                                 │
            ════════════╧═════════════                        ════════════╧═════════════
                 Internal Core                                     Internal Core
```

#### 1. กลไกความเค้นเนื่องจากความไม่เข้ากันของการขยายตัวทางความร้อน (CTE Mismatch):
- สัมประสิทธิ์การขยายตัวทางความร้อนของทองแดงในรู: $\alpha_{\text{Cu}} \approx 16 - 17\text{ ppm}/^\circ\text{C}$
- สัมประสิทธิ์การขยายตัวทางความร้อนในแนวแกน $Z$ ของวัสดุไดอิเล็กทริก FR-4/Laminate:
  - ต่ำกว่าอุณหภูมิเปลี่ยนสถานะคล้ายแก้ว ($T < T_g$): $\alpha_{z} \approx 45 - 65\text{ ppm}/^\circ\text{C}$
  - สูงกว่าอุณหภูมิเปลี่ยนสถานะคล้ายแก้ว ($T > T_g$): $\alpha_{z} \approx 250 - 320\text{ ppm}/^\circ\text{C}$!

ความเครียดในแนวแกน $Z$ ($\varepsilon_z$) ในช่วงอุณหภูมิการบัดกรีไร้สารตะกั่ว ($25^\circ\text{C} \to 260^\circ\text{C}$):
$$\varepsilon_z = \int_{25}^{T_g} (\alpha_z(T) - \alpha_{\text{Cu}})\,dT + \int_{T_g}^{260} (\alpha_{z,\text{post}}(T) - \alpha_{\text{Cu}})\,dT$$

#### 2. รายงานคำเตือนของมาตรฐาน IPC-WP-023 และ IPC-TM-650 2.6.27:
- ใน **Stacked Microvias (เวียซ้อนทับตรงกัน 3 ถึง 4 ชั้นขึ้นไป)**: โครงสร้างทองแดงทำหน้าที่เป็นเสาค้ำแข็ง (Rigid Copper Pillar) เมื่อเรซินรอบข้างขยายตัวอย่างมหาศาลตามแกน $Z$ แรงดึงทั้งหมดจะไปรวมศูนย์อยู่ที่ **รอยต่อระหว่างก้นไมโครเวียกับเป้าทองแดงชั้นล่าง (Microvia Base-to-Target Pad Interface)**
- ปรากฏการณ์นี้เรียกว่า **"Post-Separation" หรือรอยร้าวที่ก้นไมโครเวีย** ซึ่งมักเป็นรอยแยกระดับซับไมครอนที่ไม่แสดงอาการในขั้นตอนทดสอบ In-Circuit Test (ICT) ที่อุณหภูมิห้อง แต่จะเปิดวงจรเป็นช่วงๆ (Intermittent Open) ขณะอุปกรณ์ทำงานที่อุณหภูมิสูง
- **Staggered Microvias (เวียเยื้องศูนย์):** แรงเค้นในแนวแกน $Z$ จะถูกตัดขาดและกระจายตัวเข้าไปในเนื้อเรซินที่คั่นระหว่างตัวเวีย ทำให้ความเค้นเฉือนและแรงดึงที่ก้นเวียลดลงมากกว่า **$60\% - 75\%$** เมื่อเทียบกับ Stacked Microvia

#### ตารางเปรียบเทียบการตัดสินใจเลือกระหว่าง Stacked และ Staggered Microvias:

| คุณสมบัติทางวิศวกรรม | Stacked Microvias (ซ้อนทับกัน) | Staggered Microvias (เยื้องศูนย์) |
| :--- | :--- | :--- |
| **พื้นที่ในการเดินสาย (Routing Space)** | ใช้พื้นที่น้อยที่สุด (ยอดเยี่ยมสำหรับ $0.4\text{ mm}$ BGA) | ต้องใช้พื้นที่เพิ่มสำหรับกิ่ง Trace ($50-100\ \mu\text{m}$) |
| **ความเชื่อถือได้ทางความร้อน (Thermal Reliability)** | ต่ำถึงปานกลาง (ห้ามซ้อนเกิน 3 ชั้นในงานยานยนต์) | สูงมาก (ผ่านการทดสอบ 1000+ Cycles per IPC-Class 3) |
| **ความทนทานต่อ Reflow ($260^\circ\text{C}$)** | ไวต่อการแยกชั้นที่ก้นเวีย (Post Separation Risk) | ทนทานต่อการขยายตัวแกน $Z$ ได้ยอดเยี่ยม |
| **ความลึกรอยบุ๋มที่ยอมรับได้ (Dimple Requirement)** | เข้มงวดมาก ($\delta \le 5\ \mu\text{m}$) | ยืดหยุ่นกว่า ($\delta \le 10\ \mu\text{m}$) |
| **ต้นทุนการผลิต (Fabrication Cost)** | สูงกว่า (ต้องควบคุมการชุบถมรูและขัดผิวระนาบ Planarization) | ต่ำกว่าเล็กน้อย (ควบคุมความเรียบระนาบง่ายกว่า) |

---

### 1.4 ความท้าทายของ Every Layer Interconnect (ELIC) และค่าทนทานแรงดันเบรกดาวน์

สถาปัตยกรรม **ELIC (Any-Layer HDI)** อนุญาตให้สามารถวางไมโครเวียเชื่อมระหว่างชั้นคู่ใดๆ ก็ได้ในโครงสร้างบอร์ด ทำให้มีอิสระในการออกแบบสูงสุด แต่ต้องผ่านรอบการอัดลามิเนตแบบต่อเนื่อง (Sequential Lamination Cycles):

```
       ELIC 10-Layer Cross-Section (Sequential Buildup Lamination)
       Layer 1   ┌──┐            ┌──┐            ┌──┐
                 │  │ (Via 1-2)  │  │            │  │
       Layer 2   └──┴──┬──────┬──┴──┘            └──┘
                       │      │ (Via 2-3)
       Layer 3   ──────┴──────┴──────────────────────
                 Each pair drilled, plated, filled, and laminated sequentially!
                 -> Accumulative shrinkage and dimensional registration errors!
```

#### 1. ความคลาดเคลื่อนจากการหดตัวสะสม (Accumulative Material Shrinkage & Registration):
- แผงวงจร 10-Layer ELIC ต้องผ่านการอบอัดด้วยความร้อนและความดันสูงถึง **$4$ ถึง $5$ รอบ (Lamination Press Cycles)**
- เรซินและแผ่นทองแดงจะเกิดการหดตัวและยืดตัวที่ไม่สมมาตรในระนาบ $X-Y$ (Dimensional Instability: $\Delta L/L \approx \pm 0.04\% - 0.08\%$ ต่อรอบ)
- หากไม่ควบคุม **การขยายสเกลฟิล์ม (CAM Tooling Dynamic Scaling)** ลำแสงเลเซอร์จะยิงพลาดเป้าก้นรู (Target Pad Misalignment) ทำให้ขอบเวียหลุดออกจากแพด (Breakout)

#### 2. ความต้านทานแรงดันทะลวงของฉนวนบาง (Dielectric Breakdown Voltage):
ในบอร์ด Any-Layer ชั้นไดอิเล็กทริกมักมีความหนาเพียง **$35\ \mu\text{m}$ ถึง $50\ \mu\text{m}$** (เช่น การใช้พรีเพร็ก 1027 หรือ 1037 ชนิดเส้นใยบางพิเศษ):

$$V_{\text{breakdown}} = E_{\text{dielectric}} \cdot t_{\text{dielectric}}$$

โดยที่:
- $E_{\text{dielectric}}$ = ความแข็งแรงไดอิเล็กทริกของเรซิน ($\approx 40 - 60\ \text{kV/mm} = 40 - 60\ \text{V}/\mu\text{m}$)
- $t_{\text{dielectric}}$ = ความหนาของไดอิเล็กทริกหลังอัด ($40\ \mu\text{m}$)

แรงดันทะลวงทางทฤษฎี:
$$V_{\text{breakdown}} \approx 40\ \text{V}/\mu\text{m} \times 40\ \mu\text{m} = 1,600\ \text{V}$$

**อันตรายในสายการผลิตจริง:** หากมีเสี้ยนทองแดงจากการยิงเลเซอร์ (Laser Splatter / Copper Flash) ยื่นออกมา หรือเนื้อแก้วเกิดฟองอากาศ ความหนาประสิทธิผลอาจลดลงเหลือเพียง $15\ \mu\text{m}$ ส่งผลให้ฉนวนทะลุ (Dielectric Breakdown) เมื่อทดสอบ Hi-Pot Test ที่ $500\text{ V}$ หรือเกิดการลัดวงจรแบบนำกระแสของเส้นใยขั้วบวก (CAF - Conductive Anodic Filamentation) ระหว่างไมโครเวียกับระนาบดินข้างเคียง

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน (失敗事例): 5G Processor Module พังดับกลางอากาศจากรอยแยกก้น Stacked Microvia (Post-Separation)

ในโครงการสมาร์ตโฟน 5G เรือธง แผงวงจรหลักใช้เทคโนโลยี 10-Layer Any-Layer ELIC บอร์ดหนา $0.75\text{ mm}$ บริเวณชิปหน่วยประมวลผล Application Processor (AP, พิตช์ $0.35\text{ mm}$) มีการออกแบบ **Stacked Microvias ซ้อนทับกันตั้งแต่ชั้น L1 $\to$ L2 $\to$ L3 $\to$ L4** เพื่อดึงสัญญาณความเร็วสูงและระบบจ่ายไฟแกนกลาง (0.75V VDD_CORE, กระแส 25A):
- หลังจากส่งมอบล็อตทดลองผลิต (EVT) เครื่องสมาร์ตโฟนผ่านการทดสอบ Functional Test ที่อุณหภูมิห้อง $100\%$ แต่เมื่อนำไปทดสอบความทนทานต่อสภาวะแวดล้อม **Thermal Shock Test ($-40^\circ\text{C} \leftrightarrow +125^\circ\text{C}$ ย้ายอุณหภูมิภายใน 10 วินาที)** เครื่องเริ่มดับและเกิดอาการรีบูตวนซ้ำ (Kernel Panic / Infinite Reboot) ตั้งแต่รอบที่ 150
- ทีมวิเคราะห์ความล้มเหลว (FA) นำบอร์ดไปตัดตรวจทางโลหะวิทยาและส่องด้วยกล้องจุลทรรศน์อิเล็กตรอนแบบส่องกราด (FE-SEM):
  1. พบรอยแยกแตกขาดที่ชั้นรอยต่อระหว่างก้นเวีย L2 กับผิวบนของเวีย L3 (Post-Separation Interface Crack) ความกว้างของรอยแยกเพียง $0.8\ \mu\text{m}$
  2. รอยบุ๋ม (Dimple) ของเวีย L3 มีความลึกมากถึง **$14\ \mu\text{m}$** (เกินข้อกำหนด $5\ \mu\text{m}$) โรงงานไม่ได้ทำการเจียรผิวเรียบ (Planarization) สารเคมีเตรียมผิวตกค้างอยู่ในก้นหลุม ทำให้การเกาะตัวของผลึกทองแดงระหว่าง L2 กับ L3 ไม่เป็นเนื้อเดียวกัน (Poor Intermetallic Bonding)
  3. เมื่อไดอิเล็กทริกขยายตัวในแนวแกน $Z$ ความเค้นที่สะสมทำให้พันธะผลึกทองแดงขาดออกจากกัน เกิดเป็นวงจรเปิดชั่วคราว (Intermittent Open) ตัดไฟจ่าย VDD_CORE จนเครื่องดับ

```
                                Root Cause Breakdown (Ishikawa)
                                
       Fabrication & Chemical Defect                     Design Architecture Defect
    ┌──────────────────────────────────┐              ┌─────────────────────────────┐
    │ Excessive Dimple (> 14 μm)       │              │ 4-Layer Stacked Microvia    │
    │ Poor Micro-etch at Target Pad    │              │ (High Z-axis CTE Strain)    │
    └────────────────┬─────────────────┘              └──────────────┬──────────────┘
                     │                                               │
                     ▼                                               ▼
          [ Interface Contamination ]                     [ Z-axis Tensile Stress ]
                     │                                               │
                     └───────────────────────┬───────────────────────┘
                                             │
                                             ▼
                             [ POST-SEPARATION INTERFACE CRACK ]
                                             │
                                             ▼
                               Intermittent Open at 125°C
                               -> AP Reset & Kernel Crash!
```

---

### ขั้นตอนการแก้ปัญหาและการปฏิบัติหน้างาน (Standard Operating Procedures)

#### Step 1: แปลงสถาปัตยกรรม Stacked Microvias เป็น Staggered Microvias (Stagger Conversion Rule)
หากผลิตภัณฑ์ต้องทำงานในสภาวะที่มีการเปลี่ยนแปลงอุณหภูมิสูง (เช่น Automotive Grade 1 หรือ Industrial Power Modulator):
1. หลีกเลี่ยงการซ้อนทับไมโครเวียเกิน 2 ชั้น (Maximum 2-Stack Rule: อนุญาต L1-L2 ซ้อนกัน แต่ L2-L3 ต้องเยื้องศูนย์)
2. กำหนดระยะเยื้องขั้นต่ำ (Minimum Stagger Offset Distance $L_{\text{stagger}}$):
   $$L_{\text{stagger}} \ge D_{\text{pad}} + S_{\min} = D_{\text{pad}} + 50\ \mu\text{m}$$
   เพื่อให้มีเนื้อโครงสร้างผ้าใยแก้วและเรซินคั่นกลางคอยดูดซับแรงดึงในแนวแกน $Z$

#### Step 2: ควบคุมและระบุค่า Dimple Depth ในเอกสารข้อกำหนดการผลิต (Fabrication Drawing Callout)
ในแบบสั่งผลิต PCB สำหรับชิป Fine-Pitch BGA และ Any-Layer:
1. เขียนข้อกำหนดควบคุมลงใน Drawing Note:
   > *"All laser microvias located under BGA packages and stacked structures must be 100% copper filled per IPC-6012 Class 3. Maximum allowable dimple depth shall not exceed $5.0\ \mu\text{m}$ ($\le 0.2\text{ mil}$). No planar bump exceeding $+10.0\ \mu\text{m}$ is permitted."*
2. กำหนดให้โรงงานส่งผลทดสอบหน้าตัด (Micro-section Coupon Report) และการตรวจวัดความเรียบผิวด้วยเครื่อง White Light Interferometry (WLI 3D Surface Profiler) ทุกล็อตการผลิต

#### Step 3: คำนวณขอบแหวนทองแดงปลอดภัยรอบก้นรูเลเซอร์ (Laser Capture Pad Annular Ring Rule)
เพื่อป้องกันไม่ให้ลำแสงเลเซอร์ยิงตกขอบเป้าทองแดงชั้นล่าง (Tangency / Breakout):
1. ขนาดของ Target Pad ($D_{\text{pad}}$) ต้องสอดคล้องกับพิกัดความคลาดเคลื่อนสะสม (Tolerance Stack-up):
   $$D_{\text{pad}} \ge D_{\text{laser}} + 2 \cdot (\text{Laser Drill Drift}) + 2 \cdot (\text{Layer-to-Layer Misregistration})$$
2. ตัวอย่างสำหรับบอร์ด Any-Layer สมัยใหม่:
   - รูเจาะก้นเลเซอร์ $D_{\text{laser}} = 85\ \mu\text{m}$
   - ความคลาดเคลื่อนตำแหน่งเลเซอร์ $\pm 15\ \mu\text{m}$
   - ความคลาดเคลื่อนการประกบชั้นสะสม $\pm 25\ \mu\text{m}$
   - ความกว้างของวงแหวนทองแดงต่ำสุดที่ต้องการรอบก้นรู $AR_{\min} = 15\ \mu\text{m}$
   $$D_{\text{pad, min}} = 85 + 2(15) + 2(25) + 2(15) = 85 + 30 + 50 + 30 = 195\ \mu\text{m}\ (\approx 8.0\text{ mil})$$

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คำศัพท์ภาษาญี่ปุ่น (Kanji / Kana) | คำอ่าน (Romaji) | ความหมายภาษาไทย / ภาษาอังกฤษ |
| :--- | :--- | :--- |
| **高密度相互接続** | Koumitsudo sougo setsuzoku | การเชื่อมต่อความหนาแน่นสูง (High Density Interconnect - HDI) |
| **レーザーマイクロビア** | Rēzā maikurobia | รูไมโครเวียเจาะด้วยเลเซอร์ (Laser Microvia) |
| **スタックビア** | Sutakku bia | ไมโครเวียซ้อนทับกันตรงตำแหน่ง (Stacked Microvia) |
| **スタガードビア** | Sutagādo bia | ไมโครเวียแบบเยื้องศูนย์ (Staggered Microvia) |
| **エニレイヤー / 全層ビルドアップ** | Enireiyā / Zensou birudoappu | สถาปัตยกรรมเชื่อมต่อทุกชั้น (Any-Layer / ELIC) |
| **銅めっき充填 / フィリング** | Dou-mekki juuten / Firingu | การชุบทองแดงถมเต็มรูตัน (Copper Via Filling) |
| **ディンプル量** | Dinpuru-ryou | ความลึกของรอยบุ๋มบนผิวหน้าเวีย (Dimple Depth) |
| **界面剥離 / ポストセパレーション** | Kaimen hakuri / Posuto separēshon | การแยกชั้นที่รอยต่อก้นไมโครเวีย (Post-Separation Failure) |
| **ターゲットランド / 受パッド** | Tāgetto rando / Uke-paddo | แผ่นทองแดงเป้าหมายรองรับก้นรู (Target Pad / Capture Pad) |
| **積層ズレ** | Sekisou zure | ความคลาดเคลื่อนการประกบอัดชั้น (Layer-to-Layer Misregistration) |

---

### 3.2 บทสนทนาและข้อความคอมเมนต์ตรวจแบบจริง (Realistic Kenzu Review Comments)

#### คอมเมนต์ที่ 1: ทักท้วงการใช้ Stacked Microvia ซ้อนกัน 4 ชั้นในบอร์ดที่ต้องทนแรงสั่นและความร้อนสูง (車載環境における4層スタックビアの信頼性是正)
> **検図指摘 (Review Finding 1):**  
> 「U1（車載ミリ波レーダーSoC）直下のエリアにおいて、L1からL4まで同一軸上に配置された4層スタックビア（Stacked Microvia）が設計されています。本基板は車載グレード（-40℃〜+125℃環境）であるため、リフロー時および熱衝撃サイクル試験におけるZ軸熱膨張（CTEミスマッチ）により、L2/L3間のターゲットパッド界面でポストセパレーション（界面剥離破断）を引き起こすリスクが極めて高いです。  
> IPC-WP-023の推奨に基づき、L2-L3間を最低0.15mmオフセットさせたスタガードビア（Staggered Via）構造へと配置を変更してください。やむを得ずスタック構造を残す場合は、ディンプル量を3μm以下に抑え、めっき界面の前処理エッチング条件を厳格化する特記仕様書を基板メーカーへ発行してください。」  
> *(คำแปล: ในพื้นที่ใต้ชิป U1 (เรดาร์คลื่นมิลลิเมตรยานยนต์ SoC) มีการออกแบบ Stacked Microvia ซ้อนกัน 4 ชั้นบนแนวแกนเดียวกันตั้งแต่ L1 ถึง L4 เนื่องจากบอร์ดนี้เป็นเกรดรถยนต์ (ทำงานในสภาวะ -40°C ถึง +125°C) ความเค้นจากการขยายตัวในแนวแกน Z (CTE Mismatch) ขณะเข้าเตา Reflow และการทดสอบ Thermal Shock จะก่อให้เกิดความเสี่ยงสูงมากต่อการแตกร้าวแยกชั้นที่รอยต่อก้นเวีย L2/L3 (Post-separation) กรุณาแก้ไขโครงสร้างเป็นแบบ Staggered โดยเยื้องศูนย์อย่างน้อย 0.15 mm ตามคำแนะนำของ IPC-WP-023 หากหลีกเลี่ยงไม่ได้ ต้องระบุข้อกำหนดพิเศษไปยังโรงงานผลิตเพื่อคุมค่า Dimple ให้น้อยกว่า 3 µm และควบคุมการกัดล้างผิวทองแดงก่อนชุบอย่างเข้มงวด)*

#### คอมเมนต์ที่ 2: ตรวจพบ Aspect Ratio เกินเกณฑ์และเสี่ยงต่อการเกิดโพรงกักขังในรูชุบ (アスペクト比超過によるマイクロビア充填不良の指摘)
> **検図指摘 (Review Finding 2):**  
> 「L2-L3間の誘電体厚が85μmであるのに対し、レーザービアのトップ径がφ75μm（底径φ60μm）で設定されています。この場合、アスペクト比（AR）が1.13となり、IPC-6012 Class 3の推奨限界（0.8以下）を大幅に超過しています。  
> このアスペクト比では、ビア底へのめっき促進剤（Brightener）の供給が滞り、めっき液の置換不良によるボイド（空洞欠陥）や過大なディンプル（10μm超）が不可避となります。トップ径をφ110μm（AR ≒ 0.77）に拡大するか、またはプリプレグ厚を65μm（1067タイプ等）に変更して誘電体厚を薄肉化してください。」  
> *(คำแปล: ไดอิเล็กทริกระหว่าง L2-L3 มีความหนา 85 µm แต่ขนาดปากรูเลเซอร์ด้านบนกลับกำหนดไว้ที่ φ75 µm (ก้นรู φ60 µm) ในกรณีนี้ Aspect Ratio (AR) จะมีค่าสูงถึง 1.13 ซึ่งเกินขีดจำกัดแนะนำของ IPC-6012 Class 3 (ไม่เกิน 0.8) อย่างมาก ด้วยอัตราส่วนนี้ สารเร่งการชุบจะไม่สามารถไหลเวียนสู่ก้นรูได้อย่างทั่วถึง ก่อให้เกิดโพรงกลวง (Void) และรอยบุ๋มขนาดใหญ่เกิน 10 µm อย่างหลีกเลี่ยงไม่ได้ กรุณาขยายขนาดปากรูเป็น φ110 µm (AR ~ 0.77) หรือเปลี่ยนชนิดพรีเพร็กเป็นเบอร์ 1067 หนา 65 µm เพื่อลดความหนาไดอิเล็กทริกลง)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### Quiz 1: การคำนวณอัตราส่วน Aspect Ratio และจลนพลศาสตร์การชุบถมรู (Microvia Electroplating Kinetics & Dimple Depth)

**โจทย์:**  
โรงงานผลิตบอร์ด HDI ต้องการชุบทองแดงถมเต็มรูไมโครเวียแบบตาบอด (Blind Microvia) ที่เชื่อมระหว่างเลเยอร์ L1 ถึง L2  
- ความหนาของชั้นไดอิเล็กทริก $H = 65\ \mu\text{m}$  
- รูเจาะเลเซอร์มีลักษณะเป็นกรวยตัด โดยมีเส้นผ่านศูนย์กลางปากรู $D_{\text{top}} = 90\ \mu\text{m}$ และเส้นผ่านศูนย์กลางก้นรู $D_{\text{bottom}} = 70\ \mu\text{m}$
- กระบวนการชุบทองแดงใช้สารเคมีระบบ Superfilling เคมีขั้นสูง โดยอัตราการชุบพอกทองแดงที่ก้นรูในแนวดิ่ง (Bottom-Up Growth Rate) มีค่าคงที่ $r_{\text{bottom}} = 1.30\ \mu\text{m/min}$ ภายใต้อิทธิพลของ Accelerator
- อัตราการชุบพอกทองแดงที่บริเวณขอบปากรูและผิวระนาบบอร์ดด้านบน (Surface Plating Rate) ถูกกดทับด้วย Suppressor จนเหลือเพียง $r_{\text{surface}} = 0.32\ \mu\text{m/min}$
- ในกระบวนการผลิต โรงงานต้องจ่ายกระแสชุบจนกระทั่งทองแดงที่ก้นรูเจริญเติบโตขึ้นมาถึงระดับความลึกเดิมของรู ($65\ \mu\text{m}$) พอดี

**คำถาม:**
1. จงคำนวณอัตราส่วนกว้างยาว (Aspect Ratio - $AR$) ของไมโครเวียนี้ และตรวจสอบว่าผ่านเกณฑ์มาตรฐาน IPC-6012 Class 3 ($AR \le 0.80$) หรือไม่
2. จงคำนวณระยะเวลาในการชุบ ($t_{\text{plating}}$ ในหน่วยนาที) ที่ต้องใช้เพื่อให้ทองแดงพอกเต็มความลึกของรู
3. เมื่อเวลาในการชุบสิ้นสุดลง จงคำนวณความหนาของทองแดงที่พอกเพิ่มบนผิวหน้าบอร์ด ($T_{\text{surf}}$) และคำนวณหาระดับความลึกของรอยบุ๋ม (Dimple Depth - $\delta$) ที่จะปรากฏขึ้นบนปากรู พร้อมระบุว่าผ่านเกณฑ์ $\delta \le 5\ \mu\text{m}$ หรือไม่

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรม Quiz 1:

**1. คำนวณ Aspect Ratio ($AR$):**
$$AR = \frac{H}{D_{\text{top}}} = \frac{65\ \mu\text{m}}{90\ \mu\text{m}} \approx 0.722$$
**บทวิเคราะห์เกณฑ์:** ค่า $AR = 0.722 \le 0.80$ จึง **ผ่านเกณฑ์มาตรฐาน IPC-6012 Class 3** ทำให้สารละลายเคมีชุบและสารเร่งปฏิกิริยาสามารถไหลเวียนเข้าสู่ก้นรูได้อย่างสะดวกโดยไม่มีปัญหา Mass-Transfer Limitation

---

**2. คำนวณระยะเวลาในการชุบ ($t_{\text{plating}}$):**
ความลึกของรูที่ต้องเติมทองแดงคือ $H = 65\ \mu\text{m}$ ด้วยอัตราการโตจากล่างขึ้นบน $r_{\text{bottom}} = 1.30\ \mu\text{m/min}$:
$$t_{\text{plating}} = \frac{H}{r_{\text{bottom}}} = \frac{65\ \mu\text{m}}{1.30\ \mu\text{m/min}} = 50.0\ \text{นาที}$$

---

**3. คำนวณความหนาผิวหน้าและรอยบุ๋ม (Surface Copper & Dimple Depth):**
ในช่วงเวลา $t_{\text{plating}} = 50.0\ \text{นาที}$ ผิวหน้าบอร์ดรอบนอกจะถูกพอกทองแดงหนาขึ้นด้วยอัตรา $r_{\text{surface}} = 0.32\ \mu\text{m/min}$:
$$T_{\text{surf}} = r_{\text{surface}} \cdot t_{\text{plating}} = 0.32\ \mu\text{m/min} \times 50.0\ \text{นาที} = 16.0\ \mu\text{m}$$

เนื่องจากจุดศูนย์กลางของไมโครเวียเติมขึ้นมาจนเสมอขอบระนาบเดิมพอดี ($65\ \mu\text{m}$) แต่ผิวทองแดงรอบนอกบวมสูงขึ้นไปอีก $16.0\ \mu\text{m}$ หากไม่มีกระบวนการ Leveling เพิ่มเติม รอยบุ๋มจะลึกเท่ากับความหนาผิวหน้า แต่ในสารละลาย Superfilling โมเลกุล Leveler จะทำหน้าที่เร่งถมจุดศูนย์กลางในช่วงปลาย ทำให้เกิดส่วนต่างความสูงประสิทธิผล:
ในโมเดลจลนพลศาสตร์จริง การปรับระดับของ Leveler จะช่วยปิดช่องว่างได้อีกประมาณ $70\%$ ส่งผลให้ Dimple จริงคำนวณจาก:
$$\delta = T_{\text{surf}} \cdot (1 - \eta_{\text{leveler}}) \quad (\text{โดยทั่วไป } \eta_{\text{leveler}} \approx 0.75)$$
$$\delta = 16.0\ \mu\text{m} \cdot (1 - 0.75) = 4.0\ \mu\text{m}$$

**สรุปผลวิศวกรรม:** รอยบุ๋มที่เกิดขึ้นจริงคือ $\delta \approx 4.0\ \mu\text{m}$ ซึ่ง **น้อยกว่าเกณฑ์ปลอดภัย $5.0\ \mu\text{m}$** จึงถือว่าผ่านเกณฑ์คุณภาพสำหรับนำไปทำเป็น Via-in-Pad ใต้ BGA พิตช์ $0.4\text{ mm}$ ได้อย่างปลอดภัย โดยไม่ก่อให้เกิดฟองอากาศใต้ลูกบัดกรี

---

### Quiz 2: การวิเคราะห์ความเค้นและแรงดึงขาดในแนวแกน $Z$ ของ Stacked Microvia ตามมาตรฐาน IPC-WP-023

**โจทย์:**  
แผงวงจร 8-Layer HDI มีการออกแบบ **Stacked Microvias ซ้อนกันตรงแกน 3 ชั้น (L1 $\to$ L2 $\to$ L3)** เพื่อเชื่อมต่อขาไฟเลี้ยงของชิป BGA  
- ความหนาของแต่ละชั้นไดอิเล็กทริกคือ $h_1 = h_2 = h_3 = 60\ \mu\text{m}$ รวมความสูงเสาทองแดง $H_{\text{total}} = 180\ \mu\text{m}$
- ไมโครเวียมีเส้นผ่านศูนย์กลางหน้าสัมผัสก้นรูที่เชื่อมกับเป้าทองแดงชั้น L3 คือ $D_{\text{contact}} = 65\ \mu\text{m}$ (พื้นที่หน้าสัมผัส $A_{\text{contact}} = \frac{\pi}{4} D_{\text{contact}}^2$)
- คุณสมบัติวัสดุ FR-4 ไดอิเล็กทริก:
  - $T_g = 170^\circ\text{C}$
  - ค่า CTE แนวแกน $Z$ ต่ำกว่า $T_g$: $\alpha_{z1} = 55\ \text{ppm}/^\circ\text{C}$
  - ค่า CTE แนวแกน $Z$ สูงกว่า $T_g$: $\alpha_{z2} = 260\ \text{ppm}/^\circ\text{C}$
- ค่า CTE ของทองแดงบริสุทธิ์: $\alpha_{\text{Cu}} = 17\ \text{ppm}/^\circ\text{C}$
- ค่าโมดูลัสความยืดหยุ่นของทองแดงที่อุณหภูมิสูง ($260^\circ\text{C}$): $E_{\text{Cu}} = 70\ \text{GPa} = 70,000\ \text{MPa}$
- บอร์ดถูกนำไปผ่านกระบวนการบัดกรีไร้สารตะกั่ว Reflow โดยอุณหภูมิเปลี่ยนจาก $T_0 = 25^\circ\text{C}$ ไปยังจุดสูงสุด $T_{\text{peak}} = 260^\circ\text{C}$

**คำถาม:**
1. จงคำนวณผลต่างของการยืดตัวอิสระในแนวแกน $Z$ ระหว่างไดอิเล็กทริกและเสาทองแดง ($\Delta L_{\text{mismatch}}$ ในหน่วย $\mu\text{m}$)
2. หากสมมติว่าไดอิเล็กทริกขยายตัวและดึงรั้งเสาทองแดงจนเกิดความเครียดดึง (Tensile Strain $\varepsilon_z$) จงคำนวณหาค่าความเค้นดึง ($\sigma_{\text{tensile}}$ ในหน่วย $\text{MPa}$) ที่เกิดขึ้นที่รอยต่อก้นไมโครเวีย
3. หากค่าความแข็งแรงดึงสูงสุดของทองแดงชุบ (Ultimate Tensile Strength - $\text{UTS}$) ที่อุณหภูมิ $260^\circ\text{C}$ มีค่าเพียง $220\ \text{MPa}$ โครงสร้าง Stacked Microvia นี้จะเกิดการฉีกขาด (Post-Separation Crack) หรือไม่? และวิศวกรควรแนะนำการแก้ไขอย่างไร?

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรม Quiz 2:

**1. คำนวณผลต่างการยืดตัวอิสระ ($\Delta L_{\text{mismatch}}$):**
แบ่งการคำนวณออกเป็น 2 ช่วงอุณหภูมิ:
- **ช่วงที่ 1: จาก $25^\circ\text{C}$ ถึง $T_g = 170^\circ\text{C}$ ($\Delta T_1 = 145^\circ\text{C}$)**
  $$\Delta L_1 = H_{\text{total}} \cdot (\alpha_{z1} - \alpha_{\text{Cu}}) \cdot \Delta T_1$$
  $$\Delta L_1 = 180\ \mu\text{m} \cdot (55 - 17) \times 10^{-6}/^\circ\text{C} \cdot 145^\circ\text{C} = 180 \cdot 38 \times 10^{-6} \cdot 145 \approx 0.9918\ \mu\text{m}$$

- **ช่วงที่ 2: จาก $170^\circ\text{C}$ ถึง $260^\circ\text{C}$ ($\Delta T_2 = 90^\circ\text{C}$)**
  $$\Delta L_2 = H_{\text{total}} \cdot (\alpha_{z2} - \alpha_{\text{Cu}}) \cdot \Delta T_2$$
  $$\Delta L_2 = 180\ \mu\text{m} \cdot (260 - 17) \times 10^{-6}/^\circ\text{C} \cdot 90^\circ\text{C} = 180 \cdot 243 \times 10^{-6} \cdot 90 \approx 3.9366\ \mu\text{m}$$

ผลต่างการยืดตัวรวมทั้งหมด:
$$\Delta L_{\text{mismatch}} = \Delta L_1 + \Delta L_2 = 0.9918 + 3.9366 \approx 4.928\ \mu\text{m}$$

---

**2. คำนวณความเครียดและความเค้นดึงที่ก้นเวีย ($\sigma_{\text{tensile}}$):**
ความเครียดเชิงกลที่ถูกบังคับกระทำต่อเสาทองแดงความยาว $180\ \mu\text{m}$:
$$\varepsilon_z = \frac{\Delta L_{\text{mismatch}}}{H_{\text{total}}} = \frac{4.928\ \mu\text{m}}{180\ \mu\text{m}} \approx 0.02738\ (2.738\%)$$

คำนวณความเค้นดึงตามกฎของฮุก (โดยประมาณพฤติกรรมยืดหยุ่นก่อนคราก):
$$\sigma_{\text{tensile}} = E_{\text{Cu}} \cdot \varepsilon_z = 70,000\ \text{MPa} \times 0.02738 \approx 1,916.6\ \text{MPa}$$

ในทางฟิสิกส์ ทองแดงจะเกิดการครากแบบพลาสติก (Plastic Yielding) ตั้งแต่ความเค้นประมาณ $150\ \text{MPa}$ ดังนั้นความเค้นจริงจะถูกจำกัดด้วยจุดคราก แต่ความเครียดพลาสติกสะสม (Plastic Strain) จะพุ่งสูงถึง **$2.74\%$** ต่อการ Reflow 1 รอบ

---

**3. ประเมินความเสี่ยงการฉีกขาดและข้อแนะนำเชิงวิศวกรรม:**
- เกณฑ์ความยืดหยุ่นของทองแดงชุบไฟฟ้า (Elongation at Break) ตามมาตรฐาน IPC-4562 ที่อุณหภูมิ $260^\circ\text{C}$ มีค่าจำกัดเพียง **$2.0\% - 3.0\%$**
- การที่ความเครียดพุ่งขึ้นไปถึง $2.74\%$ ทำให้เสาทองแดงทำงานแตะขอบเขตการฉีกขาดทันทีในการบัดกรีรอบแรก และหากมีรอบบัดกรีสองหน้า (Double-sided Reflow) หรือการซ่อมงาน (Rework) รอยต่อจะฉีกขาดแบบเปราะ (Post-Separation Rupture) อย่างแน่นอน $100\%$
- **การแก้ไข:** ต้องยกเลิกโครงสร้าง 3-Stack ทันที โดยเปลี่ยนเป็น **Staggered Microvias (เยื้องศูนย์)** ที่เลเยอร์ L2-L3 ซึ่งจะลดความเค้นสะสมลงเหลือต่ำกว่า $0.8\%$ ปลอดภัยจากการแตกร้าวถาวร

---

### Quiz 3: การคำนวณความแม่นยำในการวางเป้าทองแดงและระยะเยื้องศูนย์ของ Staggered Microvia

**โจทย์:**  
วิศวกรกำลังจัดวางคู่เวียเยื้องศูนย์ (Staggered Microvias) ระหว่างเวียชั้น L1-L2 และเวียชั้น L2-L3  
- รูไมโครเวียมีขนาดเส้นผ่านศูนย์กลางปากรูด้านบน $D_{\text{top}} = 85\ \mu\text{m}$
- ความคลาดเคลื่อนตำแหน่งการยิงเลเซอร์ (Laser Registration Tooling Accuracy) = $\pm 12\ \mu\text{m}$
- ความคลาดเคลื่อนจากการบิดตัวและหดตัวสะสมของแผ่นลามิเนต (Material Distortion & Shrinkage) = $\pm 20\ \mu\text{m}$
- ข้อกำหนดระยะเว้นช่องว่างทองแดงต่ำสุดในกระบวนการผลิต (Minimum Copper Clearance / Spacing) บนชั้น L2 คือ $S_{\min} = 65\ \mu\text{m}$
- กำหนดให้ต้องมีขอบแหวนทองแดงปลอดภัยรอบก้นรูเลเซอร์ (Minimum Annular Ring) เพื่อป้องกันไม่ให้เลเซอร์หลุดออกนอกแพด เท่ากับ $AR_{\min} = 15\ \mu\text{m}$ (วัดจากขอบก้นรูเจาะ $D_{\text{bottom}} = 70\ \mu\text{m}$)

**คำถาม:**
1. จงคำนวณเส้นผ่านศูนย์กลางต่ำสุดของ Target Pad ($D_{\text{pad, min}}$) บนชั้น L2 เพื่อรองรับความคลาดเคลื่อนทั้งหมดอย่างปลอดภัย
2. จงคำนวณระยะห่างระหว่างจุดศูนย์กลางถึงจุดศูนย์กลางต่ำสุด (Center-to-Center Pitch: $P_{\text{stagger, min}}$) ระหว่างเวีย L1-L2 และเวีย L2-L3 เพื่อไม่ให้แพดของทั้งสองเวียละเมิดกฎระยะห่าง $S_{\min}$
3. หากชิป BGA มีพิตช์ระหว่างลูกบัดกรี $0.40\text{ mm}$ ($400\ \mu\text{m}$) การจัดวางแบบ Staggered นี้สามารถวางขนานกันในแนวทแยง (Diagonal Pitch $\approx 565\ \mu\text{m}$) ใต้ชิปได้หรือไม่?

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรม Quiz 3:

**1. คำนวณขนาด Target Pad ต่ำสุด ($D_{\text{pad, min}}$):**
ความคลาดเคลื่อนในแนวรัศมีสูงสุด (Total Radial Misalignment Tolerance - $R_{\text{tol}}$):
$$R_{\text{tol}} = \sqrt{(\text{Laser Accuracy})^2 + (\text{Material Distortion})^2} = \sqrt{(12)^2 + (20)^2} = \sqrt{144 + 400} = \sqrt{544} \approx 23.32\ \mu\text{m}$$

เส้นผ่านศูนย์กลางของก้นรูเจาะเลเซอร์ $D_{\text{bottom}} = 70\ \mu\text{m}$  
ต้องมีขอบแหวนทองแดงปลอดภัย $AR_{\min} = 15\ \mu\text{m}$ ในทุกทิศทาง:
$$D_{\text{pad, min}} = D_{\text{bottom}} + 2 \cdot (R_{\text{tol}} + AR_{\min})$$
$$D_{\text{pad, min}} = 70 + 2 \cdot (23.32 + 15) = 70 + 2 \cdot (38.32) = 70 + 76.64 = 146.64\ \mu\text{m} \approx 150\ \mu\text{m}\ (5.9\text{ mil})$$

---

**2. คำนวณระยะห่างระหว่างจุดศูนย์กลางต่ำสุด ($P_{\text{stagger, min}}$):**
แพดทั้งสองมีขนาดเส้นผ่านศูนย์กลาง $D_{\text{pad}} = 150\ \mu\text{m}$ โดยต้องเว้นระยะห่างระหว่างขอบแพดขั้นต่ำ $S_{\min} = 65\ \mu\text{m}$:
$$P_{\text{stagger, min}} = D_{\text{pad}} + S_{\min} = 150\ \mu\text{m} + 65\ \mu\text{m} = 215\ \mu\text{m}$$

---

**3. ตรวจสอบการจัดวางใต้ชิป BGA $0.4\text{ mm}$:**
- ระยะพิตช์ของ BGA ในแนวแกนตรงคือ $400\ \mu\text{m}$
- ระยะพิตช์ในแนวทแยงมุม (Diagonal Distance ระหว่าง 2 พินที่อยู่ติดกัน):
  $$P_{\text{diagonal}} = \sqrt{400^2 + 400^2} = 400 \cdot \sqrt{2} \approx 565.7\ \mu\text{m}$$
- เนื่องจากระยะพิตช์เซนเตอร์ของ Staggered Microvia ที่ต้องการคือ $215\ \mu\text{m}$ ซึ่ง **น้อยกว่า $565.7\ \mu\text{m}$ อย่างมาก**
- วิศวกรสามารถวางเวียหนึ่งตัวไว้ใต้ BGA Pad (Via-in-Pad) และเดินสายกิ่งสั้นๆ (Dogbone Trace) ความยาวเพียง $215\ \mu\text{m}$ ในแนวทแยงมุมเพื่อลงไปยังไมโครเวียชั้นถัดไปได้อย่างสบาย โดยยังมีพื้นที่ฉนวนเหลือเฟือรอบข้าง ช่วยลดความเค้นในแนวแกน $Z$ และทำให้บอร์ดผ่านการรับรองความทนทานระดับสูงสุดโดยไม่เพิ่มจำนวนเลเยอร์
