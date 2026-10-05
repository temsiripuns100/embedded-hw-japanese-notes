# Lesson 098: PCB DFA Part 8 - Design for Testability (DFT) Integration, IEEE 1149.1/1149.6 Boundary Scan, and High-Fault Coverage Strategy

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในยุคของระบบคอมพิวเตอร์สมรรถนะสูง (HPC), โมดูลสวิตช์เครือข่ายความเร็วสูงระดับศูนย์ข้อมูล (100G/400G Network Switches), และระบบประมวลผลยานยนต์ขับขี่อัตโนมัติ (Autonomous Driving Platforms) สถาปัตยกรรมแผงวงจรพิมพ์ประกอบด้วยชิป **BGA ขนาดใหญ่ที่มีพินมากกว่า 2,000 พินบนพิตช์ $0.8\text{ mm} - 0.5\text{ mm}$** และการส่งสัญญาณผ่านคู่สายอนุพันธ์ความเร็วสูงระดับ **PCIe Gen5/Gen6, PAM4, และ SerDes 56G/112G**

การทดสอบแผงวงจรด้วยเข็มสัมผัสแบบดั้งเดิม (In-Circuit Test - ICT Bed-of-Nails) ต้องเผชิญกับ **ทางตันทางกายภาพ (Physical Access Wall)**:
1. ใต้ตัวถัง BGA ไม่มีพื้นที่ว่างสำหรับเจาะหรือวางจุดทดสอบ (Test Points)
2. การวางจุดทดสอบ Test Point Pad บนลายวงจรความเร็วสูงจะทำหน้าที่เป็น **กิ่งนำสัญญาณปรสิต (Capacitive Stub)** ที่ทำลายค่าอิมพีแดนซ์ (Impedance Dip) จนสัญญาณสะท้อนและสูญเสียช่องสัญญาณ
3. แท่นทดสอบ ICT แบบหลายพันเข็มสร้างแรงกดดัดงอมหาศาลที่เสี่ยงต่อการเกิด Pad Cratering

เพื่อก้าวข้ามข้อจำกัดนี้ วิศวกรอาวุโสจำเป็นต้องผสมผสานหลักการ **การออกแบบเพื่อความสามารถในการทดสอบ (Design for Testability - DFT)** เข้ากับการประกอบ (DFA) โดยใช้สถาปัตยกรรม **Boundary Scan ตามมาตรฐาน IEEE 1149.1** สำหรับระบบดิจิทัลกระแสตรง และ **IEEE 1149.6** สำหรับคู่สายสัญญาณความเร็วสูงที่มีตัวเก็บประจุคั่นตัดสัญญาณกระแสตรง (AC-Coupled High-Speed Differential Nets)

```
+-----------------------------------------------------------------------------------------+
|                  IEEE 1149.1 / IEEE 1149.6 Boundary Scan & DFT Architecture             |
|                                                                                         |
|   [ 1. IEEE 1149.1 TAP Controller & Boundary Cells ]   [ 2. Daisy-Chain Scan Ring ]     |
|                                                                                         |
|       TDI ──► [ BSC Cell ] ──► Core Logic ──► [ BSC Cell ] ──► TDO                      |
|                     ▲                               ▲                                   |
|                     │       Boundary Scan Path      │                                   |
|       TCK, TMS ─────┴───► [ TAP FSM 16 States ] ────┴──► Controls Capture/Shift/Update  |
|                                                                                         |
|       Board Daisy Chain: TDI ──► [ IC 1 ] ──► [ IC 2 ] ──► [ IC 3 ] ──► TDO             |
|       Tests interconnects without a SINGLE physical bed-of-nails probe!                 |
|                                                                                         |
|   [ 3. IEEE 1149.6 AC-Coupled Testing ]        [ 4. High-Speed Stub Elimination ]       |
|                                                                                         |
|       Driver (Step/Pulse)   AC Capacitor (0.1 μF)  Receiver (Edge Detect)               |
|       ┌───────────────┐          ┌───┐             ┌───────────────┐                    |
|       │  1149.6 Cell  ├───[TX]───┤   ├───[RX]──────┤  1149.6 Cell  │                    |
|       └───────────────┘          └───┘             └───────────────┘                    |
|       Detects Open Caps, Shorted Lines, and Value Deficits across High-Speed SerDes!     |
|       NO Physical Test Points on 28 GHz Traces! (Zero Stub Degradation)                 |
+-----------------------------------------------------------------------------------------+
```

---

### 1.1 แบบจำลองความครอบคลุมข้อบกพร่องตามมาตรฐาน PCOLA-SOQ (Fault Coverage Modeling)

เพื่อประเมินความสมบูรณ์ของการทดสอบเชิงโครงสร้าง อุตสาหกรรมใช้วิธีการจัดหมวดหมู่ข้อบกพร่องตามมาตรฐาน **PCOLA-SOQ Scorecard**:

#### องค์ประกอบของ PCOLA (สำหรับตัวชิ้นส่วน - Components):
- **P (Presence):** มีชิ้นส่วนติดตั้งอยู่จริงหรือไม่ (ตรวจจับ Missing Component)
- **C (Correctness):** เป็นชิ้นส่วนที่ถูกต้องตามค่าสเปกหรือไม่ (Wrong Component / Value)
- **O (Orientation):** ชิ้นส่วนวางถูกขั้วหรือไม่ (Reverse Polarity / Inverted Pin 1)
- **L (Live):** ตัวชิ้นส่วนทำงานได้ทางไฟฟ้าหรือไม่ (Internal Die Functional)
- **A (Alignment):** ตำแหน่งการวางตรงศูนย์กลางแพดหรือไม่ (Placement Offset / Skew)

#### องค์ประกอบของ SOQ (สำหรับรอยต่อบัดกรี - Solder Joints):
- **S (Short):** รอยบัดกรีลัดวงจรข้ามพินหรือไม่ (Solder Bridging)
- **O (Open):** รอยบัดกรีขาดออกจากแพดหรือไม่ (Cold Joint / Non-wetting)
- **Q (Quality):** ปริมาตรและรูปทรงของรอยเชื่อมเป็นไปตามเกณฑ์มาตรฐานหรือไม่ (Excess Solder, Voids, Fillet Meniscus)

#### สมการคำนวณความครอบคลุมข้อบกพร่องรวม (Comprehensive Fault Coverage - $C_{\text{total}}$):
$$C_{\text{total}} = \frac{\sum_{i=1}^{N_{\text{nets}}} W_i \cdot \text{Covered}_i}{\sum_{i=1}^{N_{\text{nets}}} W_i} \times 100\%$$

- หากใช้เฉพาะการตรวจสอบภายนอก (AOI + AXI): ความครอบคลุมมักหยุดอยู่ที่ $70\% - 75\%$ (ขาดการทดสอบทางไฟฟ้าและสัญญาณภายใน)
- หากใช้เฉพาะ ICT: ไม่สามารถเข้าถึงพินสัญญาณใต้ชิป BGA ความหนาแน่นสูงได้
- **ยุทธศาสตร์ DFT ขั้นสูง:** การผสานรวม **Boundary Scan (JTAG) + AXI + FCT (Functional Test)** จะสามารถดันความครอบคลุมขึ้นไปสู่ **$> 95\% - 98\%$** โดยไม่จำเป็นต้องเจาะจุดทดสอบบนสายสัญญาณความเร็วสูงแม้แต่จุดเดียว

---

### 1.2 สถาปัตยกรรม IEEE 1149.1 Boundary Scan (JTAG TAP Controller & Cells)

มาตรฐาน **IEEE 1149.1 (Standard Test Access Port and Boundary-Scan Architecture)** ได้ติดตั้งเซลล์ทดสอบเสมือน (Boundary Scan Cells - BSC) คั่นอยู่ระหว่างขาพินภายนอก (Package Pins) และตรรกะภายในของซิลิคอน (Core Logic):

#### 1. สัญญาณอินเทอร์เฟซของ Test Access Port (TAP Interface 4/5 Wires):
1. **TCK (Test Clock):** สัญญาณนาฬิกาทดสอบอิสระ (ปกติ $10 - 50\text{ MHz}$)
2. **TMS (Test Mode Select):** สัญญาณควบคุมสเตตัส ควบคุมการเปลี่ยนสถานะของวงจร TAP FSM โดยสุ่มตัวอย่างที่ขอบขาขึ้นของ TCK
3. **TDI (Test Data In):** สัญญาณนำเข้าข้อมูลการทดสอบแบบอนุกรม (Serial Data In)
4. **TDO (Test Data Out):** สัญญาณส่งออกข้อมูลผลการทดสอบแบบอนุกรม (Serial Data Out) ขับเคลื่อนที่ขอบขาลงของ TCK
5. **TRST\* (Test Reset - Optional):** สัญญาณรีเซ็ตวงจรทดสอบแบบ Asynchronous (Active-Low)

```
                          TAP Controller 16-State Finite State Machine (FSM)
                          
                                    Test-Logic-Reset
                                           │ (TMS=0)
                                      Run-Test/Idle
                                           │ (TMS=1)
                                      Select-DR-Scan ────────(TMS=1)────────► Select-IR-Scan
                                           │ (TMS=0)                                │
                                      Capture-DR                               Capture-IR
                                           │                                        │
                                       Shift-DR                                 Shift-IR
                                           │                                        │
                                       Update-DR                                Update-IR
```

#### 2. กลไกการทำงานของ Boundary Scan Cell (BSC):
ในโหมดทดสอบ **EXTEST (External Interconnect Test)**:
1. **Capture Stage:** บันทึกระดับลอจิกจากขาพินภายนอกเข้าสู่ Flip-Flop ตัวแรก
2. **Shift Stage:** เลื่อนข้อมูลบิตผลการทดสอบผ่านแนวระนาบวงแหวนอนุกรม (Boundary Scan Register Chain) ออกสู่พอร์ต TDO
3. **Update Stage:** สลักค่าลอจิกทดสอบชุดใหม่จาก TDI ออกสู่ขาพินภายนอก เพื่อส่งสัญญาณทดสอบข้ามไปยังชิปตัวถัดไปบนบอร์ด

ด้วยกลไกนี้ ชิปตัวขับ (Driver Chip A) สามารถสั่งขับลอจิก '1' ออกจากขาพิน และชิปตัวรับ (Receiver Chip B) สามารถอ่านค่าลอจิกที่ปลายทางได้โดยตรงผ่านคำสั่งซอฟต์แวร์ ทำให้ตรวจจับ **การขาดของรอยบัดกรี (Open Solder Joints under BGA)** และ **การลัดวงจรระหว่างเส้นทองแดง (Bridging Shorts)** ได้อย่างแม่นยำ $100\%$ โดยไม่ต้องใช้เข็มทดสอบสัมผัสทางกายภาพ

---

### 1.3 การทดสอบคู่สายความเร็วสูงด้วยมาตรฐาน IEEE 1149.6 (AC-Coupled Boundary Scan)

ในคู่สายส่งสัญญาณความเร็วสูง เช่น **PCIe Gen4/5 (16/32 GT/s)** หรือ **SATA/SAS/100GbE**:
- มีการติดตั้งตัวเก็บประจุคั่นสัญญาณกระแสตรง (AC-Coupling Capacitors ปกติ $0.1\text{ }\mu\text{F}$ หรือ $0.22\text{ }\mu\text{F}$) บนคู่สายสัญญาณทั้งสองเส้น ($TX_+, TX_-$)
- มาตรฐานเดิม IEEE 1149.1 ซึ่งทดสอบด้วยสัญญาณลอจิก DC ระดับแรงดันคงที่ จะไม่สามารถส่งผ่านตัวเก็บประจุนี้ได้ (ตัวเก็บประจุบล็อกไฟ DC: $Z_C \to \infty$) ทำให้ระบบรายงานว่าเป็นวงจรเปิด (False Open Error) ตลอดเวลา

#### 1. สถาปัตยกรรมตัวขับและตัวรับตาม IEEE 1149.6:
มาตรฐาน **IEEE 1149.6** ได้เพิ่มวงจรตรวจจับสัญญาณทรานเชียนต์ (AC Test Receivers & Advanced Pulse Drivers):
- **1149.6 Driver:** ส่งสัญญาณพัลส์กระตุ้นแบบขั้นบันได (Step Pulse) หรือพัลส์ความถี่สูงสลับขั้ว
- **1149.6 Receiver:** ประกอบด้วยวงจรตรวจจับขอบสัญญาณ (Edge Detector) และตัวเปรียบเทียบระดับความจำ (Hysteresis Memory Comparator)
- **ความสามารถในการวินิจฉัยข้อบกพร่อง:**
  1. ตรวจจับการบัดกรีไม่ติดของตัวเก็บประจุ AC Capacitor (Open Capacitor Joint)
  2. ตรวจจับการลัดวงจรระหว่างคู่สายสัญญาณบวกและลบ ($TX_+$ ช็อตกับ $TX_-$)
  3. ตรวจจับการสลับขั้วของคู่สาย (Inverted Polarity)
  4. ตรวจจับค่าความจุไฟฟ้าผิดพลาดอย่างรุนแรง (Wrong Capacitor Value)

---

### 1.4 ผลกระทบของ Test Point Stub ต่อความสมบูรณ์ของสัญญาณความเร็วสูง (High-Speed Signal Integrity)

หนึ่งในข้อผิดพลาดที่ร้ายแรงที่สุดของวิศวกรออกแบบลายวงจร คือการดึงกิ่งลายทองแดงขนาดเล็กและวางแพดทดสอบ (Test Point Pad) ลงบนเส้นส่งสัญญาณความเร็วสูงระดับไมโครเวฟ ($> 5\text{ GHz}$):

```
       Signal Reflection at Test Point Stub
       
       Microstrip Trace (50 Ohm)                     Trace Continuation (50 Ohm)
       ═════════════════════════╦════════════════════════════════════════════► Forward Signal
                                ║ Stub Length (L_stub)
                                ║
                             ┌──╨──┐ Test Point Pad
                             │     │ (C_pad = 0.3 - 0.5 pF)
                             └─────┘ (Parasitic Capacitive Discontinuity!)
                                ▼
                       Impedance Dip: Z_local drops to 38 - 42 Ohm!
                       -> Strong Signal Reflection (Gamma = -0.15)
                       -> Eye Diagram Closes & High Bit Error Rate!
```

#### 1. การคำนวณคาปาซิแตนซ์ปรสิตของแพดทดสอบ (Test Pad Capacitance - $C_{\text{pad}}$):
แพดทดสอบขนาดเส้นผ่านศูนย์กลาง $D = 0.80\text{ mm}$ ($31.5\text{ mil}$) วางอยู่เหนือระนาบกราวด์ที่ระยะห่าง $h = 0.10\text{ mm}$ บนแผ่น FR-4 ($\varepsilon_r = 4.0$):

$$C_{\text{pad}} \approx \varepsilon_0 \cdot \varepsilon_r \cdot \frac{\frac{\pi}{4} D^2}{h} = (8.854 \times 10^{-12}) \cdot 4.0 \cdot \frac{\frac{\pi}{4} (0.80 \times 10^{-3})^2}{0.10 \times 10^{-3}} \approx 0.178\ \text{pF}$$

รวมผลกระทบของฟริงจิ้งฟิลด์รอบขอบแพด (Fringing Capacitance) และความจุของก้านกิ่งสั้น:
$$C_{\text{total\_stub}} \approx 0.30 - 0.45\text{ pF}$$

#### 2. การตกฮวบของอิมพีแดนซ์เฉพาะที่ (Local Impedance Dip):
อิมพีแดนซ์ประสิทธิผลในบริเวณที่มีคาปาซิแตนซ์ปรสิตตกกระทบ:

$$Z_{\text{local}} = \frac{Z_0}{\sqrt{1 + \frac{C_{\text{stub}}}{C'_{\text{trace}} \cdot w_{\text{prop}}}}}$$

- สำหรับสายส่ง $50\ \Omega$ ค่าความจุไฟฟ้าปกติของเส้นคือ $C' \approx 0.10\text{ pF/mm}$
- การมีคาปาซิแตนซ์ก้อน $0.4\text{ pF}$ จะทำให้อิมพีแดนซ์ท้องถิ่นร่วงลงเหลือ **$38 - 42\ \Omega$**
- ก่อให้เกิดคลื่นสะท้อนกลับ (Reflection Coefficient $\Gamma \approx -0.12$ ถึง $-0.15$)
- ในสัญญาณ $28\text{ GHz}$ (112G PAM4) การสูญเสียย้อนกลับ (Return Loss) จะแย่ลงจนทำลายตาข่ายสัญญาณ (Eye Diagram ปิดทึบ) ส่งผลให้ค่าอัตราความผิดพลาดบิตพุ่งสูง (Bit Error Rate - $\text{BER} > 10^{-4}$)
- **กฎเหล็กวิศวกรอาวุโส (Zero Test Point Rule):** **ห้ามวาง Test Point บนคู่สายสัญญาณที่มีความเร็วเกิน $2.5\text{ Gbps}$ โดยเด็ดขาด!** ต้องใช้การทดสอบผ่าน IEEE 1149.6 และระบบทดสอบตัวเองภายในชิป (Built-In Self-Test - BIST) เท่านั้น

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน (失敗事例): สวิตช์ 100GbE สัญญาณพังคาสนาม และระบบ JTAG ไม่ตอบสนองจากสัญญาณสะท้อน

ในโครงการผลิตการ์ดเร่งความเร็วเครือข่ายศูนย์ข้อมูล 100GbE SmartNIC:
- แผงวงจร 16 ชั้น มีชิป ASIC Network Processor (BGA 1,849 พิน) เชื่อมต่อกับโมดูลรับส่งแสง Optical Transceiver ผ่านคู่สาย PAM4 ความเร็ว $56\text{ Gbps}$
- วิศวกรทดสอบฝ่ายผลิต (Test Engineer) ต้องการความครอบคลุมในการทดสอบ ICT สูง จึงสั่งให้ Layout ใส่จุดทดสอบ (Test Points ขนาด $\phi 0.8\text{ mm}$) ลงบนทุกคู่สายสัญญาณรวมถึงเส้น $56\text{ Gbps}$ SerDes
- นอกจากนี้ ชิปดิจิทัลขนาดใหญ่ 4 ตัวถูกต่อเชื่อมระบบ JTAG เป็นวง Daisy Chain อนุกรมยาว
- ผลการทดสอบในสนามทดสอบ (Production Commissioning):
  1. ช่องสัญญาณ $56\text{ Gbps}$ SerDes เกิดข้อผิดพลาดอย่างรุนแรง พอร์ต Optical เกิดค่า Link Flapping (ตัดการเชื่อมต่อทุกๆ ไม่กี่วินาที) การตรวจวัดด้วย TDR พบรอยกระเพื่อมอิมพีแดนซ์หลุดกรอบ $50\ \Omega \pm 10\%$ โดยดิ่งลงไปแตะที่ **$37.5\ \Omega$** บริเวณจุดทดสอบทุกจุด
  2. เมื่อพยายามรัน Boundary Scan เพื่อทดสอบการบัดกรีของชิป ASIC ปรากฏว่าโปรแกรม JTAG รายงานข้อผิดพลาด "Scan Chain Integrity Failure: Data Corrupted" สัญญาณนาฬิกา TCK ความถี่ $25\text{ MHz}$ เกิดการสะท้อนของคลื่น (Ringing & False Edge Glitch) เนื่องจากสาย TCK ถูกแยกกิ่งจ่ายไปยังชิปทั้ง 4 ตัวแบบ Star Topology โดยไม่มีตัวต้านทานต่อปลายสาย (Termination Resistor) ทำให้ TAP Controller ของชิปสับสนสถานะและหลุดออกจากโหมดทดสอบ

```
                                Root Cause Breakdown (Ishikawa)
                                
       High-Speed SI / DFT Conflict                   JTAG Clock Integrity Defect
    ┌──────────────────────────────────┐           ┌────────────────────────────────┐
    │ Physical Test Points on 56G Net  │           │ TCK Star Topology Routing      │
    │ (C_stub = 0.38 pF -> Z = 37.5 Ω) │           │ (No source termination / Glitch)│
    └────────────────┬─────────────────┘           └───────────────┬────────────────┘
                     │                                             │
                     ▼                                             ▼
          [ SERDES LINK FLAPPING ]                      [ TAP CONTROLLER RESET ERROR ]
                     │                                             │
                     │ (Eye Diagram Closed!)                       │ (JTAG Chain Broken!)
                     ▼                                             ▼
         Transmission Data Loss at 100G ────────► TOTAL BOARD FAILURE ◄── Zero Boundary Scan Coverage
```

---

### ขั้นตอนการแก้ปัญหาและการปฏิบัติหน้างาน (Standard Operating Procedures)

#### Step 1: กฎการแยกประเภทสายสัญญาณสำหรับจุดทดสอบ (Test Point Classification Protocol)
1. **Low-Speed Control / Power Nets ($< 50\text{ MHz}$):**
   - บังคับวางจุดทดสอบ Test Point Pad ขนาด $\phi 0.90\text{ mm}$ เพื่อรองรับการทดสอบ ICT และ Functional Test
2. **High-Speed Differential Nets ($> 2.5\text{ Gbps}$ เช่น PCIe, SerDes, USB3, SATA):**
   - **ห้ามใส่ Test Point ทางกายภาพใดๆ บนแนวเส้นสัญญาณหลักโดยเด็ดขาด**
   - ตรวจสอบว่าชิปทั้งสองฝั่งรองรับมาตรฐาน **IEEE 1149.6** หรือไม่ หากรองรับ ให้ใช้ซอฟต์แวร์ Boundary Scan ทดสอบการขาด/ช็อตของสายสัญญาณผ่านพอร์ต JTAG โดยตรง

#### Step 2: กฎการเดินสายสัญญาณนาฬิกา JTAG TCK (JTAG Clock Distribution Rules)
สัญญาณนาฬิกา TCK ขับเคลื่อนชิปหลายตัวและมีความอ่อนไหวต่อสัญญาณสะท้อน (False Clocking Glitches):
1. **ห้ามเดินสายแบบ Star Topology แยกกิ่งเด็ดขาด**
2. ต้องเดินสายแบบ **Point-to-Point Daisy Chain** หรือใช้บัฟเฟอร์แยกสัญญาณนาฬิกา (Clock Buffer IC) เฉพาะ
3. ต้องติดตั้งตัวต้านทานปรับความต้านทานต้นทาง (Source Series Termination Resistor):
   $$R_{\text{series}} = Z_0 - R_{\text{driver}} \approx 33\ \Omega - 43\ \Omega$$
   วางไว้ชิดกับขา TCK ของขั้วต่อ JTAG Connector ไม่เกิน $5.0\text{ mm}$
4. ใส่ตัวเก็บประจุฟิลเตอร์ขนาดเล็ก $10 - 22\text{ pF}$ ขนานตัวต้านทาน Pull-down $10\text{ k}\Omega$ ที่ปลายสายสุดท้ายเพื่อซับสัญญาณสะท้อน

#### Step 3: การตรวจรับรองไฟล์คำอธิบายชิป BSDL (BSDL File Validation)
ก่อนสรุปแบบส่งผลิต (Tape-out):
1. ขอไฟล์ Boundary Scan Description Language (**BSDL**) ของชิปทุกตัวจากผู้ผลิตเซมิคอนดักเตอร์
2. นำไฟล์ BSDL และ Netlist เข้าโปรแกรมจำลอง JTAG (เช่น Keysight x1149 หรือ Goepel CASCON)
3. รันการตรวจสอบความถูกต้องของไวยากรณ์ (Syntax Check) และประเมินอัตราความครอบคลุมของโครงข่ายสัญญาณ (Interconnect Testability Report) ล่วงหน้า

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คำศัพท์ภาษาญี่ปุ่น (Kanji / Kana) | คำอ่าน (Romaji) | ความหมายภาษาไทย / ภาษาอังกฤษ |
| :--- | :--- | :--- |
| **テスト容易性設計 (DFT)** | Tesuto youisei sekkei | การออกแบบเพื่อความสามารถในการทดสอบ (Design for Testability) |
| **バウンダリスキャン** | Baundari sukyan | สถาปัตยกรรมสแกนขอบเขตตามมาตรฐาน (Boundary Scan) |
| **JTAGテスト** | Jētagu tesuto | การทดสอบผ่านพอร์ตทดสอบมาตรฐานร่วม (JTAG Testing - IEEE 1149.1) |
| **AC結合境界スキャン** | Ei-shī ketsugou kyoukai sukyan | การทดสอบบาวน์ดารีสแกนแบบต่อคาปาซิเตอร์ (IEEE 1149.6 AC-JTAG) |
| **故障検出率 / カバレッジ** | Koshou kenshutsu-ritsu / Kabarejji | อัตราความครอบคลุมในการตรวจจับข้อบกพร่อง (Fault Coverage) |
| **スタブ容量** | Sutabu youryou | ความจุไฟฟ้าปรสิตจากกิ่งแยกจุดทดสอบ (Stub Capacitance) |
| **デイジーチェーン** | Dējī chēn | การต่อพ่วงอนุกรมแบบลูกโซ่ (Daisy-Chain Topology) |
| **BSDLファイル** | Bī-esu-dī-eru fairu | ไฟล์คำอธิบายโครงสร้างสแกนของชิป (Boundary Scan Description File) |
| **誤クロック / リンギング** | Go-kurokku / Ringingu | สัญญาณนาฬิกาหลอกจากการสะท้อนของคลื่น (Clock Glitch / Ringing) |
| **非侵入型テスト** | Hi-shin'nyuu-gata tesuto | การทดสอบแบบไม่รุกล้ำทางกายภาพ (Non-intrusive Structural Test) |

---

### 3.2 บทสนทนาและข้อความคอมเมนต์ตรวจแบบจริง (Realistic Kenzu Review Comments)

#### คอมเมนต์ที่ 1: ตรวจพบ Test Point บนคู่สาย 56Gbps SerDes ทำลายอิมพีแดนซ์ (高速差動線路上のテストランド配置禁止の指摘)
> **検図指摘 (Review Finding 1):**  
> 「PCIe Gen5（32GT/s）および56G PAM4 SerDes差動ペア（TX/RXライン）上に、ICT用テストランド（φ0.8mm）が直接配置されています。3D電磁界解析の結果、テストランドの寄生スタブ容量（約0.35pF）により、線路インピーダンスが局所的に38Ωまで急激に低下（ディップ）し、リターンロスが-8dBまで劣化しています。この設計ではアイ開口が完全に閉塞し、通信エラー（BER増大）が不可避です。  
> 2.5Gbpsを超える高速差動ライン上の物理テストランドをすべて削除してください。差動ラインの断線・短絡検査は、搭載SoCおよびPHYチップのIEEE 1149.6（ACバウンダリスキャン）機能を活用した非侵入型テストアーキテクチャへ移行してください。」  
> *(คำแปล: บนคู่สายอนุพันธ์ความเร็วสูง PCIe Gen5 (32GT/s) และ 56G PAM4 SerDes (สาย TX/RX) มีการวางจุดทดสอบ ICT (φ0.8 mm) ลงบนเส้นสัญญาณโดยตรง ผลการวิเคราะห์สนามแม่เหล็กไฟฟ้า 3 มิติพบว่า ความจุไฟฟ้าปรสิตของจุดทดสอบ (~0.35 pF) ทำให้อิมพีแดนซ์ของเส้นตกลงฮวบเหลือเพียง 38 Ω เฉพาะจุด และค่า Return Loss แย่ลงเป็น -8 dB ในสภาวะนี้ ช่องเปิด Eye Diagram จะปิดทึบและเกิดข้อผิดพลาดในการสื่อสารอย่างแน่นอน กรุณาลบจุดทดสอบทางกายภาพทั้งหมดออกจากคู่สายที่มีความเร็วเกิน 2.5 Gbps และเปลี่ยนไปใช้สถาปัตยกรรมการทดสอบแบบไม่รุกล้ำผ่านฟังก์ชัน IEEE 1149.6 (AC Boundary Scan) ของชิป SoC และ PHY แทน)*

#### คอมเมนต์ที่ 2: ทักท้วงการเดินสาย JTAG TCK แบบ Star Connection ไร้ตัวต้านทานยุติ (JTAGクロックTCKのスター配線およびダンピング抵抗欠落是正)
> **検図指摘 (Review Finding 2):**  
> 「JTAGコネクタからのTCK（テストクロック信号）が、終端抵抗なしで4個のBGAデバイスへスター状に分岐配線されています。クロック周波数20MHzにおいて、スタブ端での反射波によるリンギング（多重スレッショルドクロス）が発生し、TAPコントローラのステートマシンが誤遷移してスキャンチェーンが途絶するリスクが極めて高いです。  
> TCKラインはコネクタ直近に33Ωの直列ダンピング抵抗（ダンピング抵抗）を配置し、デバイス間を最短距離でデイジーチェーン（一筆書き配線）するか、またはクロックバッファICを経由して各チップへ等長配線する設計に修正してください。TMSラインへの10kΩプルアップ抵抗の配置確認も併せて求めます。」  
> *(คำแปล: สัญญาณ TCK (สัญญาณนาฬิกาทดสอบ) จากคอนเนกเตอร์ JTAG ถูกเดินสายแยกกิ่งแบบ Star ไปยังชิป BGA ทั้ง 4 ตัวโดยไม่มีตัวต้านทานต่อปลายสาย ที่ความถี่นาฬิกา 20 MHz คลื่นสะท้อนที่ปลายกิ่งจะทำให้เกิดสัญญาณกระเพื่อม (Ringing) ส่งผลให้ FSM ของ TAP Controller เปลี่ยนสถานะผิดพลาดจนวงแหวนสแกนล้มเหลว กรุณาแก้ไขโดยวางตัวต้านทาน 33 Ω อนุกรมชิดกับคอนเนกเตอร์ และเดินสายสัญญาณเชื่อมต่อระหว่างอุปกรณ์แบบ Daisy Chain เส้นเดียว หรือเดินผ่านชิป Clock Buffer ไปยังแต่ละชิปอย่างอิสระ พร้อมทั้งตรวจสอบว่ามีตัวต้านทาน Pull-up 10 kΩ บนสาย TMS ครบถ้วน)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### Quiz 1: การคำนวณเวลาการรันและปริมาณข้อมูลในการทดสอบ IEEE 1149.1 Boundary Scan EXTEST

**โจทย์:**  
แผงวงจรควบคุมสถานีฐาน 5G มีชิปประมวลผลขนาดใหญ่จำนวน 3 ตัว เชื่อมต่ออยู่ในวงแหวน JTAG Daisy Chain เส้นเดียวกัน:
- ข้อมูลความยาวของ Boundary Scan Register (BSR Length) ของชิปแต่ละตัวจากไฟล์ BSDL:
  - ชิปที่ 1 (Main FPGA): $N_{\text{BSR, 1}} = 1,420\ \text{บิต}$
  - ชิปที่ 2 (Network Processor ASIC): $N_{\text{BSR, 2}} = 1,860\ \text{บิต}$
  - ชิปที่ 3 (PCIe Switch): $N_{\text{BSR, 3}} = 920\ \text{บิต}$
- ความยาวของ Instruction Register (IR Length) ของชิปทั้งสามคือ $L_{\text{IR}} = 8\ \text{บิต}$ ต่อตัว (รวมความยาว IR ทั้งหมด $L_{\text{IR, total}} = 24\ \text{บิต}$)
- ความถี่ของสัญญาณนาฬิกาทดสอบ: $f_{\text{TCK}} = 20.0\text{ MHz}$ (คาบเวลา $T_{\text{TCK}} = 50.0\text{ ns}$)
- ในการทดสอบโครงข่ายลายทองแดงระหว่างชิป (Interconnect Open/Short Test) ด้วยคำสั่ง **EXTEST**:
  - ขั้นตอนเริ่มต้น: โหลดคำสั่ง EXTEST เข้าสู่ IR ของทุกชิปพร้อมกัน (ใช้เวลารวม 32 TCK Cycles)
  - ต้องส่งเวกเตอร์ทดสอบ (Test Patterns) ทั้งหมด $N_{\text{patterns}} = 450$ รูปแบบเวกเตอร์ เพื่อให้ได้ความครอบคลุมข้อบกพร่องของตาข่ายสัญญาณ $100\%$
  - แต่ละเวกเตอร์ทดสอบประกอบด้วย: การเลื่อนข้อมูลเข้าและออกผ่าน Shift-DR State (จำนวนรอบ TCK เท่ากับความยาวรวมของ BSR Chain) บวกกับสถานะควบคุมของ TAP FSM (Select-DR, Capture-DR, Exit1-DR, Update-DR รวม 5 TCK Cycles ต่อเวกเตอร์)

**คำถาม:**
1. จงคำนวณความยาวรวมของวงแหวน Boundary Scan Register ($N_{\text{BSR, total}}$ ในหน่วยบิต) ของชิปทั้งสามตัว
2. จงคำนวณจำนวนรอบสัญญาณนาฬิกา TCK รวมทั้งหมด ($N_{\text{clock\_total}}$) ที่ต้องใช้ในการรันเวกเตอร์ทดสอบทั้ง 450 รูปแบบจนเสร็จสิ้น
3. จงคำนวณระยะเวลาการทดสอบรวมทั้งหมด ($t_{\text{test\_total}}$ ในหน่วยวินาทีหรือมิลลิวินาที) ที่ความถี่ $20\text{ MHz}$ และอธิบายความได้เปรียบด้านเวลาเมื่อเทียบกับการใช้เครื่อง Flying Probe Tester ซึ่งต้องใช้เวลาประมาณ $150$ วินาที

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรม Quiz 1:

**1. คำนวณความยาวรวมของ BSR Chain ($N_{\text{BSR, total}}$):**
$$N_{\text{BSR, total}} = N_{\text{BSR, 1}} + N_{\text{BSR, 2}} + N_{\text{BSR, 3}} = 1,420 + 1,860 + 920 = 4,200\ \text{บิต}$$

---

**2. คำนวณจำนวนรอบ TCK ทั้งหมด ($N_{\text{clock\_total}}$):**
- การโหลดคำสั่งเริ่มต้น (IR Loading): $N_{\text{IR}} = 32\ \text{Cycles}$
- แต่ละเวกเตอร์ทดสอบต้องใช้รอบ TCK:
  $$N_{\text{vector}} = N_{\text{BSR, total}} + N_{\text{FSM}} = 4,200 + 5 = 4,205\ \text{Cycles}$$
- สำหรับ $N_{\text{patterns}} = 450$ เวกเตอร์:
  $$N_{\text{DR\_total}} = 450 \times 4,205 = 1,892,250\ \text{Cycles}$$

จำนวนรอบ TCK รวมทั้งหมด:
$$N_{\text{clock\_total}} = N_{\text{IR}} + N_{\text{DR\_total}} = 32 + 1,892,250 = 1,892,282\ \text{Cycles}$$

---

**3. คำนวณระยะเวลาการทดสอบรวม ($t_{\text{test\_total}}$):**
ความถี่ $f_{\text{TCK}} = 20.0\text{ MHz} = 2.0 \times 10^7\ \text{Hz}$ ($T_{\text{TCK}} = 50.0 \times 10^{-9}\ \text{s}$):
$$t_{\text{test\_total}} = \frac{N_{\text{clock\_total}}}{f_{\text{TCK}}} = \frac{1,892,282}{20.0 \times 10^6\ \text{Hz}} \approx 0.094614\ \text{วินาที} \approx 94.61\ \text{มิลลิวินาที}$$

**บทวิเคราะห์เปรียบเทียบทางวิศวกรรม:**
- การทดสอบโครงข่ายสายสัญญาณที่ซับซ้อนใต้ชิป BGA ขนาดใหญ่ 3 ตัว ด้วย Boundary Scan ใช้เวลาเพียง **$0.095$ วินาที (ไม่ถึงหนึ่งในสิบของวินาที!)**
- ในขณะที่เครื่อง Flying Probe Tester ต้องใช้เข็มกลไกวิ่งจิ้มทีละจุด ซึ่งกินเวลาถึง **$150$ วินาที** (ช้ากว่าถึง $1,585$ เท่า!)
- Boundary Scan จึงเป็นทางออกระดับคัมภีร์ที่ช่วยให้สายการผลิตสามารถตรวจสอบความสมบูรณ์ของจุดบัดกรีใต้ BGA ได้ $100\%$ โดยไม่เพิ่มเวลาในสายการผลิต (Tact Time) และไม่มีต้นทุนค่าแท่นเข็มทดสอบแม้แต่บาทเดียว

---

### Quiz 2: การคำนวณผลกระทบของคาปาซิแตนซ์ปรสิตของ Test Point ต่อสัญญาณความเร็วสูง 16 GT/s (PCIe Gen4)

**โจทย์:**  
บนคู่สายส่งสัญญาณ Microstrip ความเร็วสูง PCIe Gen4 ($16\text{ GT/s}$, ความถี่ไนควิสต์ $f_N = 8.0\text{ GHz}$) ออกแบบให้อิมพีแดนซ์คุณลักษณะเท่ากับ $Z_0 = 50.0\ \Omega$ พอดี  
- วิศวกรได้วางแพดจุดทดสอบ (Test Point Pad) ทรงกลมขนาดเส้นผ่านศูนย์กลาง $D_{\text{pad}} = 0.70\text{ mm}$ บนเส้นสัญญาณ
- จากการจำลองสนามแม่เหล็กไฟฟ้า 3 มิติ พบว่าแพดทดสอบนี้สร้างค่าความจุไฟฟ้าปรสิตก้อนเดี่ยว (Lumped Parasitic Capacitance) รวม $C_{\text{pad}} = 0.320\text{ pF}$ ($320\ \text{fF}$)
- เวลาขาขึ้นของสัญญาณ PCIe Gen4 (Rise Time: $10\% - 90\%$): $t_{\text{rise}} = 30.0\text{ ps}$ ($30.0 \times 10^{-12}\ \text{s}$)
- ความเร็วในการแพร่กระจายคลื่นบนแผ่น FR-4: $v_p = 1.50 \times 10^8\ \text{m/s}$
- อิมพีแดนซ์ประสิทธิผลเฉพาะที่ของรอยต่อคาปาซิแตนซ์ (Effective Lumped Discontinuity Impedance) ประมาณการได้จาก:
  $$Z_{\text{dip}} \approx \frac{Z_0}{1 + \frac{Z_0 \cdot C_{\text{pad}}}{2 \cdot t_{\text{rise}}}}$$

**คำถาม:**
1. จงคำนวณค่าอิมพีแดนซ์เฉพาะที่ที่จุดทดสอบ ($Z_{\text{dip}}$ ในหน่วย $\Omega$)
2. จงคำนวณค่าสัมประสิทธิ์การสะท้อนของแรงดัน (Voltage Reflection Coefficient - $|\Gamma| = \frac{|Z_{\text{dip}} - Z_0|}{Z_{\text{dip}} + Z_0}$)
3. จงคำนวณค่าการสูญเสียย้อนกลับ (Return Loss - $RL = -20\log_{10}|\Gamma|$) และตัดสินว่าผ่านข้อกำหนดมาตรฐาน PCIe Gen4 ($RL \ge 12.0\text{ dB}$ ที่ $8\text{ GHz}$) หรือไม่?

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรม Quiz 2:

**1. คำนวณอิมพีแดนซ์เฉพาะที่ ($Z_{\text{dip}}$):**
พารามิเตอร์: $Z_0 = 50.0\ \Omega$, $C_{\text{pad}} = 0.320 \times 10^{-12}\ \text{F}$, $t_{\text{rise}} = 30.0 \times 10^{-12}\ \text{s}$:
คำนวณพจน์ตัวส่วน:
$$\frac{Z_0 \cdot C_{\text{pad}}}{2 \cdot t_{\text{rise}}} = \frac{50.0 \times (0.320 \times 10^{-12}\ \text{F})}{2 \times (30.0 \times 10^{-12}\ \text{s})} = \frac{16.0 \times 10^{-12}}{60.0 \times 10^{-12}} = \frac{16.0}{60.0} \approx 0.2667$$
คำนวณ $Z_{\text{dip}}$:
$$Z_{\text{dip}} = \frac{50.0\ \Omega}{1 + 0.2667} = \frac{50.0}{1.2667} \approx 39.47\ \Omega$$

**ข้อสังเกต:** อิมพีแดนซ์ตกลงมาถึง **$39.5\ \Omega$** (เกิด Dip ลึกถึง $-21.1\%$ เกินเกณฑ์ควบคุมมาตรฐาน $\pm 10\%$ อย่างรุนแรง!)

---

**2. คำนวณสัมประสิทธิ์การสะท้อน ($|\Gamma|$):**
$$|\Gamma| = \frac{|39.47 - 50.0|}{39.47 + 50.0} = \frac{10.53}{89.47} \approx 0.1177$$

---

**3. คำนวณ Return Loss ($RL$) และการตัดสินมาตรฐาน:**
$$RL = -20 \log_{10}(|\Gamma|) = -20 \log_{10}(0.1177) \approx -20 \cdot (-0.9292) \approx 18.58\text{ dB}$$
*(หมายเหตุ: ค่านี้คิดเฉพาะตัวแพดเดี่ยวที่เวลาขาขึ้น $30\text{ ps}$ แต่เมื่อคิดการแปลงความถี่เป็น S-Parameter $S_{11}$ ที่ $8\text{ GHz}$):*
ความต้านทานเชิงซ้อนของคาปาซิเตอร์ที่ $f_N = 8.0\text{ GHz}$:
$$X_C = \frac{1}{2\pi \cdot f \cdot C_{\text{pad}}} = \frac{1}{2\pi \cdot (8.0 \times 10^9) \cdot (0.320 \times 10^{-12})} \approx \frac{1}{1.6085 \times 10^{-2}} \approx 62.17\ \Omega$$
เมื่อต่อขนานกับโหลด $50\ \Omega$:
$$Z_{\text{eff}} = 50 \parallel (-j 62.17) \approx 30.34 - j 24.40\ \Omega$$
$$|\Gamma_{\text{freq}}| \approx \frac{\omega \cdot C \cdot Z_0}{\sqrt{4 + (\omega \cdot C \cdot Z_0)^2}} = \frac{2\pi(8 \times 10^9)(0.32 \times 10^{-12})(50)}{\sqrt{4 + [2\pi(8 \times 10^9)(0.32 \times 10^{-12})(50)]^2}} \approx \frac{0.8042}{\sqrt{4 + 0.6468}} = \frac{0.8042}{2.1556} \approx 0.373$$
$$RL_{\text{freq}} = -20 \log_{10}(0.373) \approx 8.56\text{ dB}$$

**การตัดสินตามมาตรฐาน PCIe Gen4:**
- ค่า $RL_{\text{freq}} = 8.56\text{ dB} < 12.0\text{ dB}$ **ไม่ผ่านเกณฑ์มาตรฐานอย่างสิ้นเชิง!**
- คลื่นสะท้อนกลับ $37.3\%$ จะทำลายสัญญาณ Eye Height และทำให้ชิป PCIe ปรับลดความเร็วลงเหลือเพียง Gen1 หรือ Gen2 โดยอัตโนมัติ ยืนยันว่าการวาง Test Point บนสายส่งความเร็วสูงเป็นข้อผิดพลาดร้ายแรงทางวิศวกรรม

---

### Quiz 3: การคำนวณคะแนนความครอบคลุมข้อบกพร่องตามเมทริกซ์ PCOLA-SOQ ในการผลิตจริง

**โจทย์:**  
แผงวงจรคอมพิวเตอร์อุตสาหกรรมมีส่วนประกอบและจุดบัดกรีรวม:
- จำนวนชิ้นส่วนทั้งหมด: $N_{\text{comp}} = 800$ ตัว
- จำนวนจุดต่อบัดกรีทั้งหมด: $N_{\text{joints}} = 3,200$ จุด
- สายการผลิตใช้กระบวนการทดสอบ 3 ขั้นตอนต่อเนื่อง:
  1. **3D AOI:** ตรวจสอบเฉพาะผิวภายนอก
     - ครอบคลุม: Presence (P) $98\%$, Alignment (A) $95\%$, Quality (Q) $85\%$
     - แต่ไม่สามารถตรวจจับความถูกต้องทางไฟฟ้า: Correctness (C) $0\%$, Live (L) $0\%$
  2. **IEEE 1149.1 / 1149.6 Boundary Scan:** ตรวจสอบโครงข่ายดิจิทัล
     - ครอบคลุมจุดเชื่อมต่อของชิป BGA และไอซีหลักรวม $1,600$ จุดต่อ ($50\%$ ของจุดต่อทั้งหมด)
     - มีประสิทธิภาพตรวจจับ: Short (S) $100\%$, Open (O) $100\%$, Orientation (O) $95\%$, Presence (P) $100\%$ บนตาข่ายที่สแกนถึง
  3. **Functional Circuit Test (FCT):** ตรวจสอบการบูตและฟังก์ชัน
     - ทดสอบการทำงานจริงของระบบ: Live (L) $92\%$, Correctness (C) $90\%$

**คำถาม:**
1. จงคำนวณคะแนนความครอบคลุมเฉลี่ยถ่วงน้ำหนักของหมวด PCOLA (Component-level Coverage) รวมทั้งสายการผลิต
2. จงคำนวณคะแนนความครอบคลุมของหมวด SOQ (Solder Joint-level Coverage) สำหรับข้อบกพร่องประเภท Open (การขาด) และ Short (การลัดวงจร)
3. หากในล็อตการผลิตมีข้อบกพร่องประเภทขาลอย (Open Joint) ซ่อนอยู่ใต้ BGA จำนวน 20 จุด ระบบตรวจสอบนี้จะสามารถตรวจจับได้กี่จุด และจะมีข้อบกพร่องหลุดรอดสู่ลูกค้า (Escapes) หรือไม่?

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรม Quiz 3:

**1. คำนวณความครอบคลุมหมวด PCOLA:**
สมมติการรวมพลังของทั้ง 3 สถานีตรวจสอบ (AOI + JTAG + FCT):
- **Presence (P):** AOI ตรวจจับ $98\%$, JTAG ยืนยันชิปดิจิทัล $\implies P_{\text{total}} \approx 99.5\%$
- **Correctness (C):** FCT ตรวจจับการทำงานของวงจร $\implies C_{\text{total}} \approx 90.0\%$
- **Orientation (O):** AOI ตรวจมาร์ก + JTAG ตรวจพิน $\implies O_{\text{total}} \approx 96.5\%$
- **Live (L):** FCT ตรวจสอบการบูตและการตอบสนอง $\implies L_{\text{total}} \approx 92.0\%$
- **Alignment (A):** 3D AOI ตรวจวัดตำแหน่ง $X, Y, \theta \implies A_{\text{total}} \approx 95.0\%$

คะแนน PCOLA เฉลี่ย:
$$\text{PCOLA Score} = \frac{99.5 + 90.0 + 96.5 + 92.0 + 95.0}{5} = \frac{473.0}{5} = 94.60\%$$

---

**2. คำนวณความครอบคลุมหมวด SOQ สำหรับ Open และ Short:**
- **Shorts (การลัดวงจร):**
  - 3D AOI ตรวจจับตะกั่วลัดวงจรภายนอกได้ $90\%$
  - JTAG ตรวจจับการลัดวงจรใต้ BGA ได้ $100\%$ บนตาข่ายที่สแกน
  - ความครอบคลุมรวม: $S_{\text{total}} \approx 96.0\%$
- **Opens (วงจรเปิด / ขาลอย):**
  - 3D AOI ตรวจจับขาลอยภายนอกได้ $85\%$
  - JTAG ตรวจจับขาลอยใต้ BGA บนตาข่ายสแกน ($1,600$ จุด) ได้ $100\%$
  - FCT ตรวจจับวงจรเปิดที่ทำให้ระบบทำงานล้มเหลวได้เพิ่มเติม
  - ความครอบคลุมรวม: $O_{\text{total}} \approx 94.5\%$

---

**3. การประเมินข้อบกพร่องใต้ BGA 20 จุด:**
- จุดเชื่อมต่อใต้ BGA อยู่ในโครงข่ายของ Boundary Scan ($100\%$ Coverage บนสแกนเน็ต)
- อัลกอริทึม EXTEST ของ JTAG จะส่งลอจิกพัลส์ผ่านทุกพินและดักจับค่ากลับ
- จำนวนจุดที่ตรวจพบ:
  $$N_{\text{detected}} = 20 \times 1.00 = 20\ \text{จุด}\ (100\%)$$
- จำนวนข้อบกพร่องหลุดรอดสู่ลูกค้า (Escapes):
  $$N_{\text{escape}} = 0\ \text{จุด!}$$

**บทสรุปการบริหารคุณภาพเชิงวิศวกรรม:**
หากโรงงานไม่มีระบบ Boundary Scan และพึ่งพาเพียง AOI ภายนอก ข้อบกพร่องใต้ BGA ทั้ง 20 จุดจะมองไม่เห็น $100\%$ และหลุดรอดไปถึงมือลูกค้ากลายเป็นของเสียในสนาม การบูรณาการ IEEE 1149.1/1149.6 เข้ากับกระบวนการประกอบคือหัวใจสำคัญในการบรรลุเป้าหมาย **Zero Defect Quality** ของผลิตภัณฑ์อิเล็กทรอนิกส์ขั้นสูง
