# Lesson 180: FPGA CDC Part 10 - Master CDC Sign-Off & DO-254 / ISO 26262 Production Audit (Multi-Stage Verification Gates, Formal Liveness, Waiver Governance & Final Release Checklist)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 กรอบมาตรฐานระดับสากล: DO-254 DAL-A และ ISO 26262 ASIL-D ในบริบทของ CDC
เมื่อระบบฝังตัวที่พัฒนาบน FPGA ต้องก้าวเข้าสู่การใช้งานในอุตสาหกรรมที่มีเดิมพันด้วยชีวิตมนุษย์ เช่น อากาศยานพาณิชย์ (Civil Aviation), ระบบขับเคลื่อนยานยนต์อัตโนมัติ (Autonomous Driving), หรืออุปกรณ์การแพทย์พยุงชีพ (Life-Support Medical Devices) ข้อผิดพลาดที่เกิดจากการข้ามโดเมนสัญญาณนาฬิกา (Clock Domain Crossing - CDC) จะไม่ถูกมองว่าเป็นเพียง "บั๊กซอฟต์แวร์ที่รอแพตช์" แต่ถือเป็น **"ข้อบกพร่องเชิงระบบร้ายแรง (Catastrophic Systematic Fault)"**

```
             มาตรฐานความปลอดภัยสากลและข้อกำหนด CDC SIGN-OFF
             
    [ DO-254 DAL-A (AEROSPACE) ]               [ ISO 26262 ASIL-D (AUTOMOTIVE) ]
    
    * Design Assurance Level A                 * Automotive Safety Integrity Level D
    * ความล้มเหลวนำไปสู่เครื่องบินตก           * ความล้มเหลวนำไปสู่อุบัติเหตุร้ายแรง
    * ต้องมีหลักฐานการวิเคราะห์แบบวิเคราะห์     * ต้องการ Single-Point Fault Metric (SPFM) >= 99%
      (Analytical & Formal Evidence)           * Latent Fault Metric (LFM) >= 90%
    * "Zero-Undocumented Waiver Policy"        * ห้ามมี Unsynchronized Crossing 100%
```

#### ข้อกำหนดเฉพาะของ DO-254 และ ISO 26262 ต่อ CDC:
1. **Determinism of Domain Crossings:** ทุกจุดเชื่อมต่อระหว่างโดเมนสัญญาณนาฬิกา จะต้องมีสถาปัตยกรรมที่ชัดเจน (Deterministic Architecture) เช่น 2-FF Sync, DMUX, Handshake, หรือ Async FIFO โดยห้ามมีการเชื่อมต่อแบบลอยหรือปราศจากการควบคุม
2. **Exhaustive Formal Verification:** ต้องมีการพิสูจน์ทางคณิตศาสตร์ว่าวงจรปราศจากสภาวะ Deadlock, ปราศจาก Data Corruption จาก Bus Skew, และไม่มี Reconvergence Hazards
3. **Traceability of Waivers:** ทุกคำสั่งยกเว้นข้อผิดพลาด (Waiver) จะต้องผูกโยงกับข้อกำหนดความปลอดภัย (Safety Requirement) และได้รับการอนุมัติแบบสองชั้น (Dual Independent Sign-Off)

---

### 1.2 สถาปัตยกรรมกระบวนการ 4-Tier Master CDC Sign-Off Gate Flow

เพื่อให้การตรวจสอบความถูกต้องของ CDC มีความรัดกุมสูงสุดในระดับ Production-Grade องค์กรวิศวกรรมชั้นนำจะใช้กระบวนการคัดกรอง 4 ลำดับขั้น (The 4-Tier Sign-Off Verification Gates):

```
               สถาปัตยกรรม 4-TIER MASTER CDC SIGN-OFF FLOW
               
    [ TIER 1: RTL STRUCTURAL LINTING & TOPOLOGY CHECK ]
    * เครื่องมือ: Synopsys SpyGlass CDC / Questa CDC / Vivado report_cdc
    * เกณฑ์ผ่าน: ZERO CDC-1 (Unsync), ZERO CDC-6 (Unsafe Bus), ZERO CDC-8 (Reconv)
    * ทุก 2-FF ต้องมี (* ASYNC_REG = "TRUE" *)
                         │
                         ▼ (PASS)
    [ TIER 2: SDC/XDC TIMING CONSTRAINTS & STA AUDIT ]
    * เครื่องมือ: Vivado Timing Engine / Synopsys PrimeTime
    * เกณฑ์ผ่าน: ห้ามมี Blanket `set_clock_groups -asynchronous`
    * ตรวจสอบ P2P `set_max_delay -datapath_only` และ `set_bus_skew`
    * Recovery Slack > 0 และ Removal Slack > 0 บน Reset Bridges ทุกโดเมน
                         │
                         ▼ (PASS)
    [ TIER 3: FORMAL PROTOCOL & SVA PROPERTY PROOFS ]
    * เครื่องมือ: Siemens Questa PropCheck / Cadence JasperGold CDC
    * เกณฑ์ผ่าน: พิสูจน์ Liveness (No Deadlock) บน Handshake FSM
    * พิสูจน์ Data Stability ($stable throughout transfer) บน DMUX
    * พิสูจน์ Gray Code Hamming Distance = 1 ตลอดทุก Cycle
                         │
                         ▼ (PASS)
    [ TIER 4: GATE-LEVEL EMULATION WITH CDC JITTER INJECTION ]
    * เครื่องมือ: Gate-Level Simulation (GLS) พร้อม Random Metastability Emulation
    * เกณฑ์ผ่าน: ยิง Asynchronous Phase Drift และ Metastability Random Delay
    * ทดสอบระบบต่อเนื่องเกิน 10^8 Cycles ปราศจาก Data Incoherency
                         │
                         ▼ (PASS)
             ┌───────────────────────┐
             │ BITSTREAM SIGN-OFF    │
             │ PRODUCTION RELEASE OK │
             └───────────────────────┘
```

---

### 1.3 ทฤษฎีและสูตรคำนวณความน่าเชื่อถือรวมทั้งระบบ (System Cumulative MTBF Physics)

ความผิดพลาดร้ายแรงที่สุดในหมู่วิศวกรคือ การคำนวณค่า **Mean Time Between Failures (MTBF)** ของ Synchronizer แต่ละตัวแยกกัน แล้วสรุปว่าระบบมีความปลอดภัยสูง เพราะเห็นตัวเลข MTBF ของ Synchronizer แต่ละตัวสูงถึง $1,000,000\text{ ปี}$

ทว่า ในชิป FPGA ขนาดใหญ่ระดับ UltraScale+ หรือ Versal มีจุดเชื่อมต่อข้ามโดเมนนาฬิกา (Synchronizers) ใช้งานจริง **นับร้อยหรือนับพันชุด ($K$ จุดเชื่อมต่อ)** กระจายอยู่ทั่วทั้งระบบ!

```
                  ทฤษฎีความน่าเชื่อถือของระบบแบบขนาน (RELIABILITY THEORY)
                  
    ความล้มเหลวของ Synchronizer ตัวใดตัวหนึ่งเพียงตัวเดียว 
    จะทำให้ระบบล่มสลายทันที (Series Reliability Block Diagram):
    
         System Failure Rate = ผลรวมของ Failure Rate ของทุก Synchronizer!
         
                     λ_system = λ_1 + λ_2 + λ_3 + ... + λ_K
```

#### สูตรการคำนวณ System Cumulative MTBF ($\text{MTBF}_{sys}$):
$$\lambda_{sys} = \sum_{i=1}^{K} \lambda_i = \sum_{i=1}^{K} \frac{1}{\text{MTBF}_i}$$

$$\text{MTBF}_{sys} = \frac{1}{\lambda_{sys}} = \frac{1}{\sum_{i=1}^{K} \frac{1}{\text{MTBF}_i}}$$

หากสมมติให้ตัวซิงโครไนซ์ทั้ง $K$ ชุดมีสภาวะแวดล้อมและค่า $\text{MTBF}_i$ เท่ากันโดยเฉลี่ย:
$$\text{MTBF}_{sys} = \frac{\text{MTBF}_{single}}{K}$$

#### การวิเคราะห์ตัวเลขเชิงวิศวกรรมจริงในฝูงบินหรือ Data Center:
สมมติให้ FPGA ตัวหนึ่งมีจำนวน Synchronizers ทั้งหมด $K = 500\text{ ตัว}$ และวิศวกรออกแบบ 2-FF โดยมีค่า $\text{MTBF}_{single} = 100,000\text{ ปี}$ ($10^5\text{ ปี}$):
$$\text{MTBF}_{sys} = \frac{100,000\text{ ปี}}{500} = 200\text{ ปี ต่อ 1 ชิป}$$

หากผลิตภัณฑ์นี้ถูกผลิตออกสู่ตลาดจำนวน **$10,000\text{ เครื่อง}$** (เช่น ในรถยนต์ $10,000$ คัน หรือเซิร์ฟเวอร์ $10,000$ เครื่อง):
$$\text{MTBF}_{fleet} = \frac{\text{MTBF}_{sys}}{10,000} = \frac{200\text{ ปี}}{10,000} = 0.02\text{ ปี} = 0.02 \times 365 \approx 7.3\text{ วัน!}$$

> [!CRITICAL]
> **บทเรียนราคาแพงระดับ Lead Architect:**
> แม้ว่า Synchronizer แต่ละตัวจะมี MTBF สูงถึง 1 แสนปี แต่เมื่อนำมารวมกันทั้งชิปและกระจายสู่ฝูงอุปกรณ์ $10,000$ เครื่อง **ระบบจะพังทลายจาก Metastability ทุกๆ 7 วัน!**
> ดังนั้น ในระดับ Senior Sign-Off ข้อกำหนดมาตรฐานสำหรับ $\text{MTBF}_{single}$ จึงต้องถูกบีบให้สูงกว่า **$10^{9} \sim 10^{11}\text{ ปี}$ ขึ้นไปเสมอ** โดยการใช้ 3-Stage Synchronizer ในทุกจุดวิกฤต!

---

### 1.4 ระเบียบปฏิบัติการจัดการ Waiver (Waiver Governance SOP)

```
                    วงจรชีวิตของการจัดการ WAIVER (WAIVER LIFECYCLE)
                    
    [ 1. WAIVER REQUEST ]
    * วิศวกรผู้พัฒนาสร้างตั๋วคำร้อง พร้อมระบุรหัส Tool Rule และ Instance Name
    * แนบเอกสารการวิเคราะห์ผลกระทบทางกายภาพ
              │
              ▼
    [ 2. INDEPENDENT TECHNICAL REVIEW ]
    * วิศวกรอิสระ (Reviewer) ตรวจสอบความสมเหตุสมผล
    * พิสูจน์ว่าไม่สามารถแก้ไขทาง RTL ได้จริง (e.g., Hard IP Core Boundary)
              │
              ▼
    [ 3. MATHEMATICAL & FORMAL PROOF ]
    * แนบการคำนวณ Slack / SVA Formal Proof ที่ยืนยันความปลอดภัย 100%
              │
              ▼
    [ 4. DUAL CRYPTOGRAPHIC SIGN-OFF ]
    * ลงนามอนุมัติร่วมกันระหว่าง Lead FPGA Architect และ Safety Manager
    * จัดเก็บใน Git Repository พร้อม GPG Signature Tag
              │
              ▼
    [ 5. RE-EVALUATION AT EVERY RELEASE ]
    * สคริปต์ CI/CD ตรวจสอบความถูกต้องของ Waiver ซ้ำในทุกๆ Release Build
```

---

### 1.5 ใบตรวจสอบมาตรฐาน 10 ประการสำหรับปล่อยงานจริง (Master Production Release Checklist)

| ข้อที่ | รายการตรวจสอบเชิงวิศวกรรม (Engineering Audit Item) | เกณฑ์การผ่าน (Acceptance Criteria) | วิธีการตรวจสอบ |
|:---:|:---|:---|:---:|
| 1 | **Unsynchronized Crossings (CDC-1)** | **ต้องเป็นศูนย์ (0 Violations)** | Vivado `report_cdc` |
| 2 | **Multi-bit Bit-by-bit Crossings (CDC-6)** | **ต้องเป็นศูนย์ (0 Violations)** | SpyGlass / Vivado |
| 3 | **Reconvergence of Synchronizers (CDC-8)** | **ต้องเป็นศูนย์ (0 Violations)** | Questa CDC |
| 4 | **ASYNC_REG Placement Constraints** | ระบุครบทุกสเตจของ Synchronizers | Vivado Property Check |
| 5 | **Timing Constraints on CDC** | ใช้ P2P `set_max_delay -datapath_only` + `set_bus_skew` | XDC Review & STA |
| 6 | **Reset Bridge & Recovery/Removal** | Recovery Slack $> 0$, Removal Slack $> 0$ ทุกโดเมน | `report_timing -recovery` |
| 7 | **Reset Domain Crossing (RDC)** | มี Isolation Cell และ Sequencer ครบทุกพาธ | Questa RDC / Netlist |
| 8 | **Formal Protocol Liveness & Safety** | พิสูจน์ Liveness และ Invariance ครบ $100\%$ | JasperGold / PropCheck |
| 9 | **System Cumulative MTBF** | $\text{MTBF}_{system} \ge 10^6\text{ ปี}$ สำหรับผลิตภัณฑ์ | Mathematical Sheet |
| 10 | **Waiver Governance & Audit Trail** | Zero Unreviewed Waivers + Lead Signature | Cryptographic GPG Audit |

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】ระบบคอมพิวเตอร์ควบคุมการบินหลักของอากาศยานไร้คนขับ (Autonomous eVTOL)
เกิดอาการ Flight Computer Crash ดับกลางอากาศ ส่งผลให้อากาศยานตกกระแทกพื้นเสียหายสิ้นเชิง
จากความล้มเหลวในการคำนวณ System Cumulative MTBF ในขั้นตอน CDC Sign-Off
================================================================================
```

#### บริบทของระบบ (System Context):
บริษัทพัฒนาอากาศยานไร้คนขับขึ้น-ลงแนวดิ่งพลังงานไฟฟ้า (Autonomous Electric Vertical Take-off and Landing - eVTOL) พัฒนากล่องคอมพิวเตอร์ควบคุมการบินหลัก (Flight Control Computer - FCC) บนชิป FPGA เกรดการบิน Xilinx Kintex UltraScale (`xcku060`):
* ระบบประกอบด้วย 3 โดเมนหลัก: `clk_imu` ($200\text{ MHz}$), `clk_nav` ($125\text{ MHz}$), และ `clk_actuator` ($100\text{ MHz}$)
* มีจุดเชื่อมต่อ CDC แบบ 1 บิตกระจายอยู่ทั่วทั้งระบบจำนวน $180\text{ จุด}$
* วิศวกรเลือกใช้ 2-Stage Flip-Flop Synchronizer ในทุกจุดเชื่อมต่อ โดยคำนวณ MTBF สำหรับตัวที่เร็วที่สุดได้ค่า $\text{MTBF}_i \approx 4,380\text{ ชั่วโมง}$ (ประมาณ $6\text{ เดือน}$)
* ในเอกสารขอรับรองการบิน ทีมวิศวกรบันทึกว่า *"จุดเชื่อมต่อ CDC แต่ละจุดมี MTBF สูงถึง 6 เดือน จึงปลอดภัยเพียงพอสำหรับเที่ยวบินที่ใช้เวลาเพียง 45 นาที"*

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
ในระหว่างการบินทดสอบระยะยาวของฝูงบินทดสอบจำนวน 8 ลำ (Flight Test Campaign) เมื่อเครื่องบินลำที่ 4 ทำการบินไปได้ประมาณ 40 ชั่วโมงที่ระดับความสูง 150 เมตรเหนือพื้นดิน: คอมพิวเตอร์ควบคุมการบินหลักเกิด **อาการหยุดทำงานกะทันหัน (Flight Computer Crash / CPU Core Freeze)** เซอร์โวมอเตอร์ควบคุมใบพัดดับสนิท ร่มชูชีพฉุกเฉินไม่ทำงาน อากาศยานไร้คนขับหมุนควงสว่านตกลงกระแทกพื้นรันเวย์พังยับเยิน มูลค่าความเสียหายกว่า 80 ล้านบาท!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมอากาศยานไร้คนขับจึงตกกระแทกพื้น?**
   * *เพราะคอมพิวเตอร์ควบคุมการบิน FCC หยุดประมวลผลคำสั่งปรับมุมใบพัดกะทันหัน*
2. **ทำไม FCC จึงหยุดประมวลผลคำสั่งกะทันหัน?**
   * *เพราะโมดูล Attitude Estimation FSM ค้างสนิทในสถานะ Undefined State จากการแซมเปิลข้อมูลข้ามโดเมนที่เกิด Metastability*
3. **ทำไมจึงเกิด Metastability ทั้งที่วิศวกรคำนวณ MTBF ไว้ที่ 6 เดือนแล้ว?**
   * *เพราะวิศวกรคำนวณ MTBF แยกเฉพาะตัวซิงโครไนซ์เดี่ยวๆ แต่ละตัว โดยไม่ได้นำตัวซิงโครไนซ์ทั้ง 180 จุดมารวมกันตามหลัก **System Cumulative MTBF***
4. **ทำไมค่า System Cumulative MTBF จึงนำไปสู่อุบัติเหตุเร็วกว่าที่คาดไว้มาก?**
   * *เพราะเมื่อนำ 180 จุดมารวมกัน ค่า $\text{MTBF}_{system}$ ของชิปจะลดลงเหลือเพียง $\frac{4,380\text{ ชั่วโมง}}{180} \approx 24.3\text{ ชั่วโมง}!$ และเมื่อทดสอบพร้อมกัน 8 ลำ เวลาเฉลี่ยที่ฝูงบินจะเกิดอุบัติเหตุคือทุกๆ **3 ชั่วโมงเท่านั้น!**
5. **ทำไมการออกแบบที่ล้มเหลวร้ายแรงเช่นนี้จึงผ่านขั้นตอนการตรวจแบบ Sign-off ได้?**
   * *เพราะกระบวนการ CDC Sign-off Checklist เดิมของบริษัทไม่มีการกำหนดให้ทำ System Cumulative MTBF Summation และไม่มีการบังคับใช้ 3-Stage Synchronizer ในพาธความถี่สูงตามมาตรฐาน DO-254 DAL-A!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                          สาเหตุของความล้มเหลว: EVTOL FLIGHT CRASH
                          
   METHOD (กระบวนการ Sign-off)                 MACHINE (ฮาร์ดแวร์และการคำนวณ MTBF)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ขาดการคำนวณ Cumulative MTBF    │          │ ใช้เพียง 2-FF Sync บน 200MHz   │
   │ มองข้ามผลคูณความเสี่ยงของฝูงบิน│          │ มีจุด CDC สะสมมากถึง 180 จุด   │
   │ ปล่อยให้ Single MTBF = 6 เดือนผ่าน│       │ System MTBF ลดฮวบเหลือ 24 ชม.  │
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ขาดการทำ Gate-Level Emulation  │          │ การทดสอบภาคพื้นรันเวลาไม่พอ    │
   │ ละเลยข้อกำหนด DO-254 DAL-A     │          │ ไม่มีวงจร Dual-Modular Watchdog│
   │ ขาดการสอบทานโดย Chief Reviewer │          │ ไม่ตรวจวัด Clock Jitter จริง   │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (มาตรฐานและการรับรอง)               MEASUREMENT (การตรวจสอบคุณภาพ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediations):
1. **อัปเกรดตัวซิงโครไนซ์เป็น 3-Stage Synchronizer ทั้งหมด:**
   * สัญญาณ 1 บิตทั้งหมด 180 จุด เปลี่ยนจาก 2-FF เป็น 3-Stage Synchronizer พร้อม `(* ASYNC_REG = "TRUE" *)`
   * การเพิ่มสเตจที่ 3 ทำให้ MTBF ของแต่ละจุดพุ่งขึ้นจาก $6\text{ เดือน}$ ($4,380\text{ ชั่วโมง}$) กลายเป็น **มากกว่า $10^9\text{ ปี}$**
   * ค่า $\text{MTBF}_{system}$ รวมทั้ง 180 จุด จึงมีค่ามากกว่า **$5 \times 10^6\text{ ปี}$** ปลอดภัยอย่างสิ้นเชิง!
2. **ปรับปรุงเอกสาร Master CDC Sign-Off Checklist:** บังคับให้การยื่นขออนุมัติบิตสตรีมต้องมีตารางคำนวณ Cumulative System MTBF แนบเสมอ
3. **ติดตั้งวงจรกู้คืนสภาวะฉุกเฉิน (Triple-Modular Redundant Supervisor):** เพิ่มชิปมอนิเตอร์ภายนอกที่พร้อมทำ Hardware Safe Re-engagement หากโมดูลตรวจวัดทัศนคติหยุดนิ่งเกิน 5 มิลลิวินาที

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Master CDC Sign-Off (Lead Sign-Off Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | การคำนวณ System Cumulative MTBF รวมทุกจุดเชื่อมต่อในชิปมีค่าตามเกณฑ์? | $\ge 1,000,000\text{ ปี}$ | [ ] ผ่าน |
| 2 | จุดเชื่อมต่อที่มีความถี่สูงเกิน $150\text{ MHz}$ ใช้ 3-Stage Synchronizer หรือไม่? | $100\%$ Coverage | [ ] ผ่าน |
| 3 | มีการตรวจสอบ Static CDC ด้วยเครื่องมือชั้นนำ และมี Critical Warnings เป็นศูนย์? | Zero Violations | [ ] ผ่าน |
| 4 | รายการ Waiver ทุกรายการมีเอกสารการคำนวณทางคณิตศาสตร์และ SVA รองรับครบถ้วน? | $100\%$ Documented | [ ] ผ่าน |
| 5 | มีลายเซ็นอนุมัติคู่ (Dual Sign-Off: Lead Architect + Safety Manager) หรือไม่? | Cryptographically Signed | [ ] ผ่าน |
| 6 | ทำการทดสอบ Gate-Level Simulation พร้อม Metastability Emulation ผ่าน $10^8$ Cycles? | Zero Data Glitches | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันジ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | 最終サインオフ判定 | さいしゅうサインオフはんてい | Saishū sain'ofu hantei | Final Sign-Off Decision Gate |
| 2 | 複合MTBF算出 | ふくごうMTBFさんしゅつ | Fukugō MTBF sanshutsu | System Cumulative MTBF Calculation |
| 3 | 単一故障基準 | たんいつこしょうきじゅん | Tan'itsu koshō kijun | Single-Point Fault Metric (SPFM) |
| 4 | 航空宇宙機能安全 | こうくううちゅうきのうあんぜん | Kōkū uchū kinō anzen | Aerospace Functional Safety (DO-254) |
| 5 | 形式的生存性検証 | けいしきてきせいぞんせいけんしょう | Keishikiteki seizonsei kenshō | Formal Liveness Proof (No Deadlock) |
| 6 | ゲートレベル・ジッタ注入 | ゲートレベル・ジッタちゅうにゅう | Gēto reberu jitta chūnyū | Gate-Level Jitter Injection Simulation |
| 7 | 多段階シンクロナイザ | ただんかいシンクロナイザ | Tadankai shinkuronaiza | Multi-Stage Synchronizer (3-FF / 4-FF) |
| 8 | 適用除外二重承認 | てきようじょがいにじゅうしょうにん | Tekiyō jogai nijū shōnin | Dual Waiver Sign-Off Governance |
| 9 | 監査証跡の完全性 | かんさしょうせきのかんぜんせい | Kansa shōseki no kanzensei | Audit Trail Integrity |
| 10 | ビットストリーム出図 | ビットストリームしゅつず | Bittosutorīmu shutsuzu | Bitstream Official Release / Tape-out |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ห้องประชุมพิจารณาปล่อยแบบผลิตภัณฑ์การบินและอวกาศ (Aerospace Final Sign-Off Boardroom), เมืองนาโกย่า (Nagoya)  
**ผู้เข้าร่วม:**
* **ฟุจิโมโตะฮมบุโจ (Fujimoto-Hombucho):** ผู้อำนวยการใหญ่ฝ่ายวิศวกรรมความปลอดภัยการบิน (General Manager of Avionics Safety / 航空技術本部長)
* **ภาณุพงศ์ (Phanupong):** วิศวกรอาวุโสผู้ออกแบบระบบคอมพิวเตอร์ควบคุมการบิน (Lead Avionics FPGA Engineer)

---

**藤本本部長 (Fujimoto):**  
「パヌポン君、このeVTOL飛行制御コンピュータ（FCC）用FPGAの最終出図（Sign-Off）申請書を拝見した。静的解析レポートではCDC警告がゼロになっており、一見すると完璧に見える。だが、添付されたMTBF計算書を見て愕然としたよ。君は個々の2段シンクロナイザのMTBFが約6ヶ月（4,380時間）であることを根拠に『飛行時間は45分なので安全率が高い』と結論付けているね。チップ全体で180箇所もあるCDCの**複合MTBF（System Cumulative MTBF）**をなぜ合算していないのかね？」  
*(Panupon-kun, kono eVTOL hikō seigyo konpyūta (FCC)-yō FPGA no saishū shutsuzu shinseisho wo haiken shita. Seiteki kaiseki repōto dewa CDC keikoku ga zero ni natte ori, ikken suru to kampeki ni mieru. Daga, tempu sareta MTBF keisansho wo mite gakuzen to shita yo. Kimi wa koko no 2-dan shinkuronaiza no MTBF ga yaku 6-kagetsu de aru koto wo konkyo ni "hikō jikan wa 45-fun nano de anzenritsu ga takai" to ketsuron-zukete iru ne. Chippu zentai de 180-kasho mo aru CDC no fukugō MTBF wo naze gassan shite inai no kane?)*  
**คำแปล:** คุณภาณุพงศ์ ผมได้ตรวจเอกสารยื่นขอปล่อยแบบขั้นสุดท้าย (Sign-Off) ของ FPGA สำหรับคอมพิวเตอร์ควบคุมการบิน eVTOL เครื่องนี้แล้ว ในรายงาน Static Analysis คำเตือน CDC เป็นศูนย์ทั้งหมด ดูเผินๆ เหมือนจะสมบูรณ์แบบดี แต่พอเปิดดูเอกสารคำนวณ MTBF ที่แนบมา ผมตกใจมากเลยนะ คุณเอาการที่ตัวซิงโครไนซ์ 2 สเตจแต่ละตัวมี MTBF ประมาณ 6 เดือน (4,380 ชั่วโมง) มาอ้างว่า "เนื่องจากเวลาบินแค่ 45 นาที จึงมีมาร์จินความปลอดภัยสูง" ทำไมคุณถึงไม่นำจุด CDC ที่มีมากถึง 180 จุดทั่วทั้งชิปมาคำนวณ **System Cumulative MTBF รวม** กันล่ะครับ?

**パヌポン (Phanupong):**  
「本部長、大変恐縮です。それぞれのクロッシングパスは独立した物理回路であり、同時にメタステーブルを起こす確率は極めて低いと考えたため、個別パスのMTBFが要求飛行時間を大幅に上回っていれば規格を満たすと誤認しておりました。」  
*(Hombuchō, taihen kyōshuku desu. Sorezore no kurosshingu pasu wa dokuritsu shita butsuri kairo de ari, dōji ni metastēburu wo okosu kakuritsu wa kiwamete hikui to kangaeta tame, kobetsu pasu no MTBF ga yōkyū hikō jikan wo ōhabani uwamawatte ireba kikaku wo mitasu to gonin shite orimashita.)*  
**คำแปล:** ท่านผู้อำนวยการครับ ผมต้องกราบขออภัยอย่างยิ่งครับ เนื่องจากแต่ละพาธข้ามโดเมนเป็นวงจรทางกายภาพที่แยกจากกัน และความน่าจะเป็นที่จะเกิด Metastable พร้อมกันมีต่ำมาก ผมจึงเข้าใจผิดไปว่าแค่ MTBF ของแต่ละจุดสูงกว่าเวลาบินของเที่ยวบินก็เพียงพอตามข้อกำหนดแล้วครับ

**藤本本部長 (Fujimoto):**  
「何を言っているんだ！180個のうちの**『たった1つ』**がメタステーブルを起こして姿勢制御FSMが異常停止しただけで、機体は操縦不能になって墜落するんだよ！システムの故障率は個々の故障率の単純総和（λ_sys = Σ λ_i）になる。4,380時間を180で割ってみなさい。**システム全体のMTBFは、わずか24時間強しかないんだよ！** 100機のeVTOLが毎日運航したら、毎日何機墜落すると思っているのかね！？DO-254 DAL-Aの審査基準を完全に舐めているとしか思えん！」  
*(Nani wo itte iru n da! 180-ko no uchi no "tatta hitotsu" ga metastēburu wo okoshite shisei seigyo FSM ga ijō teishi shita dake de, kitai wa sōjū funō ni natte tsuiraku suru n da yo! Shisutemu no koshōritsu wa koko no koshōritsu no tanjun sōwa ni naru. 4,380-jikan wo 180 de watte minasai. Shisutemu zentai no MTBF wa, wazuka 24-jikan kyō shika nai n da yo! 100-ki no eVTOL ga mainichi unkō shitara, mainichi nan-ki tsuiraku suru to omotte iru no kane!? DO-254 DAL-A no shinsa kijun wo kanzen ni namete iru to shika omoen!)*  
**คำแปล:** พูดอะไรออกมาน่ะ! แค่ตัวใดตัวหนึ่งใน 180 ตัวนี้เกิด Metastable ขึ้นมาเพียงตัวเดียวจน FSM ควบคุมท่าทางการบินค้าง อากาศยานก็จะเสียการทรงตัวจนตกทันทีนะ! อัตราความล้มเหลวของระบบคือผลรวมทางตรงของความล้มเหลวของทุกตัว ลองเอา 4,380 ชั่วโมงหารด้วย 180 ดูซิ **MTBF ของทั้งระบบมันเหลือเพียงแค่ 24 ชั่วโมงเศษเท่านั้นเองนะ!** ถ้ามี eVTOL 100 ลำบินทุกวัน คุณคิดว่าเครื่องจะตกวันละกี่ลำกัน!? นี่คุณกำลังดูถูกเกณฑ์การประเมิน DO-254 DAL-A อยู่ชัดๆ!

**パヌポン (Phanupong):**  
「血の気が引く思いです……！私の計算の甘さで、大惨事を招くところでした……！直ちに全180箇所のシンクロナイザを**3段構成（3-Stage Flip-Flop Synchronizer）**へ全面改修いたします！3段化により個別MTBFを10の9乗年以上に引き上げ、システム全体の複合MTBFを数百万年以上へと向上させます！」  
*(Chi no ke ga hiku omoi desu...! Watashi no keisan no amasa de, daisanji wo maneku tokoro deshita...! Tadachini zen 180-kasho no shinkuronaiza wo 3-dan kōsei e zemmenteki ni kaishū itashimasu! 3-dan-ka ni yori kobetsu MTBF wo 10 no 9-jō nen ijō e hikiage, shisutemu zentai no fukugō MTBF wo sū-hyaku-man nen ijō e to kōjō sasemasu!)*  
**คำแปล:** ผมรู้สึกหน้าชาและตกใจจนขนลุกเลยครับ...! ความสะเพร่าในการคำนวณของผมเกือบนำไปสู่หายนะครั้งใหญ่แล้ว...! ผมจะรีบยกเครื่องตัวซิงโครไนซ์ทั้ง 180 จุดให้เป็นโครงสร้าง **3-Stage Synchronizer** ทั้งหมดเดี๋ยวนี้ครับ! การเพิ่มเป็น 3 สเตจจะช่วยดัน MTBF ของแต่ละจุดให้สูงกว่า $10^9$ ปี และทำให้ค่า System Cumulative MTBF รวมพุ่งขึ้นเกินหลายล้านปีครับ!

**藤本本部長 (Fujimoto):**  
「そうだ。航空機の型式証明では、妥協は一切許されない。全パスを3段化した後、Questa CDCによる再検証レポート、複合MTBFの理論計算証明書、そしてメタステーブル注入による1億サイクルのゲートレベルシミュレーションログを揃えなさい。それら全てが完璧に揃った時、私が責任を持って出図承認印を押そう。」  
*(Sō da. Kōkūki no katashiki shōmei dewa, dakyō wa issai yurusarenai. Zen-pasu wo 3-dan-ka shita nochi, Questa CDC ni yoru sai-kenshō repōto, fukugō MTBF no riron keisan shōmeisho, soshite metastēburu chūnyū ni yoru 1-oku saikuru no gēto reberu shimyurēshon rogu wo soroenasai. Sorera subete ga kampeki ni sorotta toki, watashi ga sekinin wo motte shutsuzu shōnin-in wo osō.)*  
**คำแปล:** ถูกต้อง ในการขอใบรับรองแบบของอากาศยาน จะไม่มีการประนีประนอมใดๆ ทั้งสิ้น หลังปรับปรุงเป็น 3 สเตจทุกพาธแล้ว จงเตรียมรายงานตรวจซ้ำจาก Questa CDC, เอกสารพิสูจน์การคำนวณ Cumulative MTBF, และบันทึกผล Gate-level Sim 100 ล้านไซเคิลพร้อมการจำลอง Metastability มาให้ครบ เมื่อทุกอย่างสมบูรณ์แบบร้อยเปอร์เซ็นต์แล้ว ผมจะเป็นคนประทับตราอนุมัติปล่อยแบบด้วยความรับผิดชอบของผมเอง

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณ System Cumulative MTBF และวิเคราะห์ความน่าเชื่อถือของฝูงบิน (Fleet Reliability)
ในระบบควบคุมขีปนาวุธป้องกันภัยทางอากาศ ชิปประมวลผล FPGA มีจุดเชื่อมต่อข้ามโดเมนสัญญาณนาฬิกา (CDC 1-bit Synchronizers) ทั้งหมดจำนวน $K = 250\text{ จุด}$:
* ทุกจุดใช้ 2-Stage Flip-Flop Synchronizer ทำงานที่ความถี่ปลายทาง $f_{clk} = 200\text{ MHz}$ และความถี่เหตุการณ์ $f_{data} = 10\text{ MHz}$
* ค่าคำนวณ MTBF สำหรับตัวซิงโครไนซ์เดี่ยวแต่ละตัวมีค่าเท่ากันคือ: $\text{MTBF}_{single} = 5,000\text{ ปี}$ ($4.38 \times 10^7\text{ ชั่วโมง}$)
* ระบบขีปนาวุธถูกผลิตและติดตั้งประจำการในกองทัพจำนวน $N_{fleet} = 1,000\text{ ลูก}$ โดยเปิดสแตนด์บายตลอดเวลา 24 ชั่วโมงต่อวัน

จงคำนวณหาค่า **System Cumulative MTBF ($\text{MTBF}_{sys}$)** ของชิป FPGA แต่ละตัวในหน่วยปี และคำนวณหา **ค่าเฉลี่ยของเวลาที่ขีปนาวุธ 1 ลูกในฝูงบินจะเกิดสภาวะล้มเหลวจาก Metastability ($\text{MTBF}_{fleet}$)** ในหน่วยวัน!

---

#### ตัวเลือก:
* **ก)** $\text{MTBF}_{sys} = 20\text{ ปี}$, $\text{MTBF}_{fleet} \approx 7.30\text{ วัน}$
* **ข)** $\text{MTBF}_{sys} = 5,000\text{ ปี}$, $\text{MTBF}_{fleet} \approx 5.00\text{ ปี}$
* **ค)** $\text{MTBF}_{sys} = 20\text{ ปี}$, $\text{MTBF}_{fleet} \approx 73.0\text{ วัน}$
* **ง)** $\text{MTBF}_{sys} = 250\text{ ปี}$, $\text{MTBF}_{fleet} \approx 91.25\text{ วัน}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การคำนวณ System Cumulative MTBF ของชิป 1 ตัว ($\text{MTBF}_{sys}$):
ตามทฤษฎีความน่าเชื่อถือของระบบ (Reliability Theory for Series Systems):
$$\lambda_{sys} = \sum_{i=1}^{K} \lambda_i = \sum_{i=1}^{K} \frac{1}{\text{MTBF}_i} = K \times \frac{1}{\text{MTBF}_{single}}$$
$$\text{MTBF}_{sys} = \frac{1}{\lambda_{sys}} = \frac{\text{MTBF}_{single}}{K}$$
แทนค่าตัวเลข ($K = 250\text{ จุด}$, $\text{MTBF}_{single} = 5,000\text{ ปี}$):
$$\text{MTBF}_{sys} = \frac{5,000\text{ ปี}}{250} = 20.00\text{ ปี ต่อ 1 ชิป}$$

##### 2. การคำนวณความน่าเชื่อถือของทั้งฝูงบิน ($\text{MTBF}_{fleet}$):
เมื่อมีขีปนาวุธประจำการทั้งหมด $N_{fleet} = 1,000\text{ ลูก}$ ทำงานพร้อมกัน:
$$\lambda_{fleet} = N_{fleet} \times \lambda_{sys} = \frac{N_{fleet}}{\text{MTBF}_{sys}}$$
$$\text{MTBF}_{fleet} = \frac{\text{MTBF}_{sys}}{N_{fleet}} = \frac{20\text{ ปี}}{1,000} = 0.020\text{ ปี}$$
แปลงเป็นหน่วยวัน ($1\text{ ปี} = 365\text{ วัน}$):
$$\text{MTBF}_{fleet} = 0.020 \times 365\text{ วัน} = 7.30\text{ วัน!}$$

##### ข้อคิดเชิงวิศวกรรมอาวุโส:
นี่คือผลลัพธ์ที่น่าตระหนก! แม้ว่าตัวซิงโครไนซ์เดี่ยวแต่ละตัวจะมี MTBF นานถึง $5,000\text{ ปี}$ แต่ในกองทัพที่มีขีปนาวุธ $1,000$ ลูก จะมีขีปนาวุธ **เกิดอาการค้างหรือระบบล้มเหลวจาก Metastability ทุกๆ 7.3 วัน (สัปดาห์ละ 1 ครั้ง!)** ซึ่งยอมรับไม่ได้อย่างสิ้นเชิงในมาตรฐานทางการทหารและอวกาศ! ทางแก้เดียวคือต้องเปลี่ยนไปใช้ **3-Stage Synchronizer** ซึ่งจะดัน $\text{MTBF}_{single}$ ให้พุ่งขึ้นเกิน $10^9\text{ ปี}$ ทำให้ $\text{MTBF}_{fleet}$ ยาวนานนับแสนปี!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** คิดโดยละเลยจำนวน Synchronizer ($K=250$) ในชิป และละเลยผลรวมของฝูงบิน
* **ข้อ ค):** คำนวณวันผิดพลาดทางคณิตศาสตร์ (ลืมหารด้วย 10)
* **ข้อ ง):** นำค่า $K=250$ มาเป็นตัวเลขคำตอบโดยตรงโดยไม่ได้นำไปหารกับ 5,000 ปี

---

### ข้อที่ 2: การตรวจสอบเอกสาร DO-254 DAL-A Compliance Audit Trail
ในระหว่างการตรวจประเมินรับรองมาตรฐานการบินระดับสูงสุด DO-254 DAL-A โดยตัวแทนจาก FAA หรือ EASA วิศวกรตรวจแบบ (Auditor) จะตรวจสอบความสมบูรณ์ของแพ็กเกจเอกสาร CDC ข้อใดต่อไปนี้คือ **สิ่งที่จะทำให้ระบบ "ตกการประเมินทันที (Immediate Audit Finding / Non-Compliance)"**?

---

#### ตัวเลือก:
* **ก)** การที่วงจรมีจำนวนจุดเชื่อมต่อ CDC มากกว่า 100 จุด
* **ข)** การมีคำสั่ง `create_waiver` ในไฟล์ Constraints โดยไม่มีการอ้างอิงรหัสความปลอดภัย (Safety Requirement ID), ไม่มีการแนบการพิสูจน์ Formal Proof, หรือไม่มีลายเซ็นดิจิทัลของ Lead Safety Architect กำกับอนุมัติ
* **ค)** การใช้ 3-Stage Synchronizer แทนที่จะเป็น 2-Stage Synchronizer
* **ง)** การที่ความถี่ของสัญญาณนาฬิกาสองโดเมนไม่เป็นอัตราส่วนจำนวนเต็มต่อกัน

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **ปรัชญาของมาตรฐาน DO-254 DAL-A:**
   มาตรฐาน DO-254 กำหนดหลักการ **Complete Traceability and Accountability (ความสามารถในการตรวจสอบย้อนกลับและความรับผิดชอบอย่างสมบูรณ์)** ทุกบรรทัดของโค้ด RTL และทุกคำสั่งใน Constraints จะต้องสามารถเชื่อมโยงกลับไปยัง System Safety Requirement ได้
2. **ความร้ายแรงของ Undocumented Waiver:**
   การมีคำสั่ง Waiver ปิดคำเตือน CDC ในสคริปต์ โดยไม่มีเอกสารวิเคราะห์เหตุผล ไม่มี Formal Proof พิสูจน์ และไม่มีลายเซ็นผู้รับผิดชอบ จะถูกจัดเป็น **Category-1 Major Non-Compliance Finding ทันที** เพราะผู้ตรวจประเมินจะมองว่าทีมพัฒนาจงใจปกปิดข้อบกพร่องของฮาร์ดแวร์เพื่อหลีกเลี่ยงการแก้ไขแบบ ซึ่งส่งผลให้การรับรองแบบ (Type Certification) ของอากาศยานถูกระงับทันที!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** จำนวนจุดเชื่อมต่อ CDC ไม่ได้เป็นเกณฑ์ในการตัดสิน หากทุกจุดได้รับการออกแบบและพิสูจน์ความปลอดภัยอย่างถูกต้อง
* **ข้อ ค):** การใช้ 3-Stage Synchronizer เป็นแนวทางปฏิบัติที่ได้รับการส่งเสริมอย่างยิ่งใน DO-254 เพื่อเพิ่ม MTBF
* **ข้อ ง):** นาฬิกาที่มีความถี่ไม่ลงตัว (Asynchronous Clocks) เป็นเรื่องปกติของระบบดิจิทัลขนาดใหญ่

---

### ข้อที่ 3: ข้อจำกัดของ Gate-Level Simulation (GLS) ในการทดแทน Static CDC Analysis
ทำไมในกระบวนการรับรองมาตรฐานสากล จึงไม่อนุญาตให้นำผลการทดสอบ **Gate-Level Simulation (GLS)** แม้จะรันเป็นเวลาหลายร้อยล้านไซเคิล มาใช้ทดแทนกระบวนการ **Static CDC Verification** ได้?

---

#### ตัวเลือก:
* **ก)** เพราะ Gate-Level Simulation ใช้พื้นที่ฮาร์ดดิสก์ในการบันทึก Waveform มากเกินไป
* **ข)** เพราะ Gate-Level Simulation เป็นกระบวนการทดสอบเชิงพลวัตแบบสุ่ม (Incomplete Dynamic Sampling) ซึ่งทดสอบได้เพียงบางส่วนของ State Space เท่านั้น ในขณะที่ Static CDC Verification ทำการวิเคราะห์โครงสร้างและพิสูจน์พื้นที่สถานะทั้งหมด $100\%$ แบบเบ็ดเสร็จ (Exhaustive Formal Analysis) จึงสามารถรับประกันได้ว่าจะไม่มีมุมอับที่ซ่อนอยู่
* **ค)** เพราะคอมไพเลอร์ของ Gate-Level Simulation ไม่รองรับภาษา SystemVerilog
* **ง)** เพราะ Gate-Level Simulation ทำงานได้เร็วกว่า Static CDC มากเกินไปจนทำให้จับข้อผิดพลาดไม่ทัน

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **ข้อจำกัดทางคณิตศาสตร์ของ Dynamic Simulation:**
   แม้จะรันการจำลองระดับเกต (GLS) นานถึง $10^9\text{ ไซเคิล}$ แต่เมื่อเทียบกับพื้นที่สถานะที่เป็นไปได้ทั้งหมด (State Space) ของระบบดิจิทัลที่มีฟลิปฟล็อปหลายหมื่นตัว ($2^{10000}$) สัดส่วนของการครอบคลุมการทดสอบ (Coverage) จะมีค่าน้อยกว่า $0.00000001\%$ ยิ่งไปกว่านั้น สภาวะ Metastability เป็นปรากฏการณ์ทางสถิติที่มีลักษณะสุ่ม ซึ่งอาจไม่ปรากฏให้เห็นในระหว่างการรัน Simulation
2. **ความเหนือกว่าของ Static Verification:**
   เครื่องมือ Static CDC Verification และ Formal Property Checking ทำงานโดยการสำรวจโครงสร้างของ Netlist ทางคณิตศาสตร์ $100\%$ (Exhaustive Structural & Mathematical Exploration) ทำให้ไม่มีพาธใดหลุดรอดการตรวจสอบไปได้
   ดังนั้น มาตรฐานระดับสูงจึงบังคับว่า **ต้องใช้ Static CDC เป็นประตูด่านหลักที่ต้องผ่าน $100\%$ ก่อนเสมอ** และใช้ GLS เป็นเพียงเครื่องมือตรวจสอบซ้ำในขั้นตอนท้ายสุดเท่านั้น!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** พื้นที่จัดเก็บข้อมูลเป็นเพียงประเด็นทางไอที ไม่ใช่เหตุผลเชิงวิทยาศาสตร์ความปลอดภัย
* **ข้อ ค):** Simulator ระดับอุตสาหกรรมในปัจจุบันรองรับ SystemVerilog IEEE 1800 อย่างสมบูรณ์แบบ
* **ข้อ ง):** ในความเป็นจริง Gate-Level Sim ทำงานช้ากว่า Static Analysis เป็นพันเท่า ไม่ได้เร็วกว่า
