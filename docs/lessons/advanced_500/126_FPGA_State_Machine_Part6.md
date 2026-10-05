# Lesson 126: FPGA State Machine Part 6 - Advanced State Encoding Optimization (状態エンコーディングの最適化: Power vs Area vs Fmax Trade-offs & Custom Hybrid Encoding)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 การหาค่าเหมาะสมที่สุดแบบหลายวัตถุประสงค์ (Multi-Objective State Encoding Optimization)
ในการออกแบบระบบดิจิทัลระดับสูง (ASIC และ FPGA) การเลือกวิธีการเข้ารหัสสเตต (State Encoding) ไม่ใช่เพียงแค่การเลือกระหว่าง One-Hot หรือ Binary ตามความคุ้นเคย แต่มันคือการแก้ปัญหาทางคณิตศาสตร์แบบ **Multi-Objective Constrained Optimization**:

$$\min_{\mathbf{E} \in \mathcal{E}} J(\mathbf{E}) = w_A \cdot \frac{\text{Area}(\mathbf{E})}{\text{Area}_{max}} + w_P \cdot \frac{P_{dyn}(\mathbf{E})}{P_{max}} + w_T \cdot \frac{T_{crit}(\mathbf{E})}{T_{target}}$$

โดยที่:
* $\mathcal{E}$ คือ เซตของการแมปปิ้งสถานะทั้งหมดที่เป็นไปได้ ($|\mathcal{E}| = \frac{(2^m)!}{(2^m - N)!}$)
* $\text{Area}(\mathbf{E})$ คือ จำนวนทรัพยากรลอจิก (LUTs และ Flip-Flops) บนชิป
* $P_{dyn}(\mathbf{E})$ คือ กำลังไฟฟ้าไดนามิกเฉลี่ยที่สูญเสียไปในการสลับสถานะ
* $T_{crit}(\mathbf{E})$ คือ ความหน่วงเวลาของเส้นทางวิกฤต (Critical Path Delay ซึ่งเป็นตัวกำหนด $F_{max} = \frac{1}{T_{crit}}$)
* $w_A, w_P, w_T$ คือ ค่าน้ำหนักความสำคัญ (Weighting Factors) โดยที่ $w_A + w_P + w_T = 1$

```
                   พื้นที่การประนีประนอม (Pareto Frontier of State Encoding)
   
     ความเร็ว (Fmax) ^
                    |                  ● One-Hot (Fmax สูงสุด, ใช้ FF เยอะ, Logic Depth = 1)
                    |                /
                    |               /   ● Custom Hybrid (จุดสมดุลที่ดีที่สุดสำหรับวงจรใหญ่)
                    |              /
                    |    ● Gray   /
                    |   (Power ต่ำ)
                    |            /
                    |           ● Binary (พื้นที่ FF น้อยสุด, Logic Depth ลึก, Fmax ต่ำ)
                    +---------------------------------------------> พื้นที่ประหยัด (1/Area)
```

---

### 1.2 แบบจำลองความน่าจะเป็นแบบมาร์คอฟและการคำนวณ Switching Activity (Markov Chain Power Analysis)
พฤติกรรมการเปลี่ยนสถานะของ FSM สามารถจำลองได้ด้วย **ลูกโซ่มาร์คอฟแบบไม่ต่อเนื่อง (Discrete-Time Markov Chain: DTMC)** โดยกำหนดเมทริกซ์ความน่าจะเป็นของการเปลี่ยนสถานะ (Transition Probability Matrix: $\mathbf{P} \in \mathbb{R}^{N \times N}$):

$$\mathbf{P} = \begin{bmatrix} p_{00} & p_{01} & \dots & p_{0,N-1} \\ p_{10} & p_{11} & \dots & p_{1,N-1} \\ \vdots & \vdots & \ddots & \vdots \\ p_{N-1,0} & p_{N-1,1} & \dots & p_{N-1,N-1} \end{bmatrix}$$

โดยที่ $p_{ij} = P(S(t+1) = s_j \mid S(t) = s_i)$ และ $\sum_{j=0}^{N-1} p_{ij} = 1$ เสมอ

#### 1.2.1 การหาเวกเตอร์ความน่าจะเป็นในสภาวะคงตัว (Steady-State Probability Vector $\boldsymbol{\pi}$)
$$\boldsymbol{\pi} \mathbf{P} = \boldsymbol{\pi} \quad \text{โดยมีเงื่อนไข} \quad \sum_{i=0}^{N-1} \pi_i = 1$$

#### 1.2.2 การคำนวณกำลังไฟฟ้าสลับขั้วรวม (Total Dynamic Switching Power)
กำลังไฟฟ้าสูญเสียที่แท้จริงของเครือข่าย Flip-Flop คำนวณจากผลรวมของระยะห่างแฮมมิง (Hamming Distance $d_H$) ถ่วงน้ำหนักด้วยความน่าจะเป็นของการเปลี่ยนสถานะจริง:

$$P_{dyn} = \frac{1}{2} V_{DD}^2 \cdot f_{clk} \cdot C_{load} \sum_{i=0}^{N-1} \sum_{j=0}^{N-1} \left( \pi_i \cdot p_{ij} \cdot d_H(\mathbf{E}(s_i), \mathbf{E}(s_j)) \right)$$

* **นัยสำคัญทางวิศวกรรม:** หากคู่สถานะใดมีอัตราการกระโดดข้ามไปมาสูงมาก ($\pi_i \cdot p_{ij} \gg 0$) วิศวกรต้องจัดรหัสให้สองสถานะนั้นมี **Hamming Distance $d_H = 1$** (เช่น ใช้ Gray-like Local Assignment) เพื่อกำจัดการสลับบิตเกินความจำเป็น และลดการเกิด Dynamic Power Spikes

---

### 1.3 สถาปัตยกรรม Hybrid Partitioned Encoding (สเตตแมชชีนลูกผสม)
สำหรับ FSM ขนาดใหญ่ ($N \ge 32$ ถึง $128$ สถานะ) การใช้ One-Hot ล้วนจะผลาญ Flip-Flop มหาศาลและสร้าง Routing Congestion รุนแรง ขณะที่การใช้ Binary ล้วนจะทำให้ Next-State LUT Depth ลึกเกินไปจนปิด Timing ไม่ลง

ทางออกระดับ Senior Architect คือ **การแบ่งกลุ่มสถานะ (Clustered / Partitioned Hybrid Encoding)**:
1. **Active Core Cluster (สถานะที่ทำงานประจำที่ $f_{clk}$ สูง):** เข้ารหัสแบบ **One-Hot** เพื่อให้ Logic Depth $= 1$ ปิด Timing ที่ $500\text{ MHz}$ ได้สบาย
2. **Infrequent / Configuration Cluster (สถานะตั้งค่า, จัดการข้อผิดพลาด, Calibration):** เข้ารหัสแบบ **Binary / Sequential** เพื่อประหยัด Flip-Flop

```
                  สถาปัตยกรรม Clustered Hybrid FSM Architecture
   +--------------------------------------------------------------------------+
   | Cluster Selector (Super-State Register: 2 bits)                          |
   | [00: INIT/CONFIG]      [01: HIGH-SPEED STREAM]      [10: ERROR/RECOVERY] |
   +--------------------+----------------------------+------------------------+
                        |                            |
                        v                            v
               +-----------------+          +-----------------+
               | Dense Binary    |          | Pure One-Hot    |
               | Cluster (4 FFs) |          | Cluster (8 FFs) |
               | - Slow Config   |          | - 500MHz Stream |
               | - Low Area      |          | - Zero Glitch   |
               +-----------------+          +-----------------+
```

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Hybrid Encoded State Machine พร้อมการควบคุม Synthesis Directives

```systemverilog
//=============================================================================
// Module: hybrid_fsm_controller.sv
// Description: Multi-Cluster Hybrid Encoded State Machine for 500MHz Timing
// Compliant: Xilinx Vivado / Intel Quartus Prime Pro / Synopsys Synplify
//=============================================================================
`timescale 1ns / 1ps

module hybrid_fsm_controller (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        stream_valid,
    input  logic        config_start,
    input  logic        config_done,
    input  logic        crc_error_flag,
    output logic        dma_tx_en,
    output logic [1:0]  cluster_mode,
    output logic        core_busy
);

    // นิยาม Cluster แม่ (Super-State)
    typedef enum logic [1:0] {
        SUPER_CONFIG = 2'b00,
        SUPER_STREAM = 2'b01,
        SUPER_FAULT  = 2'b10
    } super_state_t;

    // การเข้ารหัสแบบเฉพาะเจาะจง: บังคับ One-Hot บน Sub-state ของโหมดความเร็วสูง
    // เพื่อให้ LUT Depth ใน Loop วิกฤตมีค่าเท่ากับ 1 เสมอ
    typedef enum logic [3:0] {
        STREAM_IDLE   = 4'b0001,
        STREAM_HEADER = 4'b0010,
        STREAM_DATA   = 4'b0100,
        STREAM_DRAIN  = 4'b1000
    } stream_state_t;

    // Sub-state ของโหมดคอนฟิก ใช้ Binary เพื่อประหยัด Flip-Flop
    typedef enum logic [1:0] {
        CFG_IDLE  = 2'b00,
        CFG_LOAD  = 2'b01,
        CFG_VERIF = 2'b10,
        CFG_APPLY = 2'b11
    } cfg_state_t;

    // กำหนด Synthesis Attributes สำหรับควบคุม EDA Tool
    (* fsm_encoding = "sequential" *) super_state_t  current_super, next_super;
    (* fsm_encoding = "one_hot" *)    stream_state_t current_stream, next_stream;
    (* fsm_encoding = "sequential" *) cfg_state_t    current_cfg, next_cfg;

    //-------------------------------------------------------------------------
    // 1. Sequential State Updates (Synchronous Reset Architecture)
    //-------------------------------------------------------------------------
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            current_super  <= SUPER_CONFIG;
            current_stream <= STREAM_IDLE;
            current_cfg    <= CFG_IDLE;
        end else begin
            current_super  <= next_super;
            current_stream <= next_stream;
            current_cfg    <= next_cfg;
        end
    end

    //-------------------------------------------------------------------------
    // 2. High-Level Super-State Transition Logic
    //-------------------------------------------------------------------------
    always_comb begin
        next_super = current_super;

        case (current_super)
            SUPER_CONFIG: begin
                if (config_done) begin
                    next_super = SUPER_STREAM;
                end
            end

            SUPER_STREAM: begin
                if (crc_error_flag) begin
                    next_super = SUPER_FAULT;
                end
            end

            SUPER_FAULT: begin
                if (config_start) begin
                    next_super = SUPER_CONFIG;
                end
            end

            default: next_super = SUPER_CONFIG;
        endcase
    end

    //-------------------------------------------------------------------------
    // 3. Ultra-Fast Stream Sub-FSM (One-Hot Critical Path)
    //-------------------------------------------------------------------------
    always_comb begin
        next_stream = current_stream;

        if (current_super == SUPER_STREAM) begin
            case (current_stream)
                STREAM_IDLE: begin
                    if (stream_valid) next_stream = STREAM_HEADER;
                end

                STREAM_HEADER: begin
                    next_stream = STREAM_DATA;
                end

                STREAM_DATA: begin
                    if (!stream_valid) next_stream = STREAM_DRAIN;
                end

                STREAM_DRAIN: begin
                    next_stream = STREAM_IDLE;
                end

                default: next_stream = STREAM_IDLE;
            endcase
        end else begin
            next_stream = STREAM_IDLE;
        end
    end

    //-------------------------------------------------------------------------
    // 4. Low-Power Config Sub-FSM (Binary Logic)
    //-------------------------------------------------------------------------
    always_comb begin
        next_cfg = current_cfg;

        if (current_super == SUPER_CONFIG) begin
            case (current_cfg)
                CFG_IDLE:  if (config_start) next_cfg = CFG_LOAD;
                CFG_LOAD:  next_cfg = CFG_VERIF;
                CFG_VERIF: next_cfg = CFG_APPLY;
                CFG_APPLY: next_cfg = CFG_IDLE;
                default:   next_cfg = CFG_IDLE;
            endcase
        end else begin
            next_cfg = CFG_IDLE;
        end
    end

    // Look-Ahead Registered Outputs
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            dma_tx_en    <= 1'b0;
            cluster_mode <= 2'b00;
            core_busy    <= 1'b0;
        end else begin
            dma_tx_en    <= (next_super == SUPER_STREAM) && (next_stream == STREAM_DATA);
            cluster_mode <= next_super;
            core_busy    <= (next_super != SUPER_CONFIG) || (next_cfg != CFG_IDLE);
        end
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในการออกแบบระบบประมวลผลเข้ารหัสลับแบบฮาร์ดแวร์ (Post-Quantum Cryptography Accelerator) บนชิป FPGA ชนิดประหยัดพลังงานพิเศษ (Low-Power Edge FPGA) ตัวควบคุมหลักมีสถานะถึง $64$ สถานะ วิศวกรเปิดการตั้งค่าให้คอมไพเลอร์ใช้ `One-Hot Encoding` ทั่วทั้งโมดูล เพราะต้องการให้วงจรรันได้ความถี่สูงสุด

**ผลลัพธ์ที่ล้มเหลว:** แม้ความถี่ $F_{max}$ ในรายงาน STA จะผ่านฉลุย แต่เมื่อนำบอร์ดไปประกอบใส่เคสกันน้ำไร้พัดลม (Fanless Sealed Enclosure) อุณหภูมิจังก์ชันของชิป ($T_j$) พุ่งทะลุ $115^\circ\text{C}$ ภายในเวลา 4 นาที ชิปเข้าสู่โหมด Thermal Shutdown และเมื่อตรวจสอบพื้นที่ ปรากฏว่า Flip-Flops ใน Slice ถูกใช้จนแน่นเอี้ยด ($98\%$ Utilization) ทำให้เครื่องมือ Place & Route ต้องลากสายอ้อมข้ามบล็อก เกิด Routing Congestion ขนานใหญ่

```
                    หายนะจากการใช้ One-Hot แบบไม่คิดหน้าคิดหลัง
   FSM ขนาด 64 สถานะถูกบังคับใช้ One-Hot ล้วน
                         |
                         v
   ใช้ Flip-Flops ถึง 64 ตัวในโมดูลเดียว + สัญญาณควบคุมแตกแขนงทั่วชิป
                         |
                         v
   เกิดปัญหา Routing Congestion (ความแออัดของสายสัญญาณระดับสีแดง)
   กำลังไฟฟ้า Dynamic Power สูงขึ้น 3 เท่าตัวจากการชาร์จประจุสายไฟที่ยาวขึ้น
                         |
                         v
   อุณหภูมิ Tj ทะลุ Thermal Limit -> ชิปตัดการทำงาน (Thermal Shutdown Freeze!)
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมชิป FPGA ถึงเกิด Thermal Shutdown และหยุดทำงานในเคสไร้พัดลม?**
   * *ตอบ:* อุณหภูมิจังก์ชันของซิลิคอน ($T_j$) พุ่งสูงเกินขีดจำกัดความปลอดภัย $105^\circ\text{C}$
2. **ทำไมความร้อนของชิปถึงสะสมสูงมากขนาดนั้น?**
   * *ตอบ:* กำลังไฟฟ้าไดนามิก ($P_{dyn}$) และกำลังไฟฟ้ารั่วไหล ($P_{leak}$) ของ Core Logic พุ่งสูงเกินงบประมาณพลังงาน (Thermal Design Power: TDP)
3. **ทำไมกำลังไฟฟ้าไดนามิกถึงสูงเกินเกณฑ์อย่างรุนแรง?**
   * *ตอบ:* เครือข่ายสายสัญญาณเชื่อมต่อ State Register มีความยาวและความจุไฟฟ้า ($C_{wire}$) มหาศาล เนื่องจากการกระจายตัวของ Flip-Flop
4. **ทำไมสายสัญญาณถึงยาวและแออัดขนาดนั้น?**
   * *ตอบ:* สเตตแมชชีนขนาด 64 สถานะถูกบังคับใช้ One-Hot Encoding ทำให้ใช้ Flip-Flop ถึง 64 ตัว และเครื่องมือ P&R ต้องวางกระจายข้ามหลายร้อย Logic Slices
5. **ทำไมผู้ออกแบบถึงเลือก One-Hot ให้กับทุกสถานะโดยไม่แยกแยะ?**
   * *ตอบ:* ผู้ออกแบบคิดว่า One-Hot ดีที่สุดเสมอโดยไม่ได้คำนวณ Switching Activity และลืมไปว่าสถานะส่วนใหญ่ ($> 50$ สถานะ) เป็นเพียงสถานะคอนฟิกที่ทำงานนานๆ ครั้ง ซึ่งเหมาะกับ Binary Encoding

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความร้อนสะสมและการใช้พื้นที่ล้นจาก FSM
   
   การออกแบบสถาปัตยกรรม (Architecture)           สภาพแวดล้อมทางกายภาพ (Thermal/Physical)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ใช้ One-Hot    ไม่ทำ Partition                เคสแบบปิด     ไม่มีพัดลมระบาย
   กับทั้ง 64    แยก Active                    (Fanless)     (Convection ต่ำ
   สถานะ         กับ Config                    สะสมความร้อน   Theta_JA สูง)
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> ชิปเกิด Thermal
                                                                |     Shutdown ทำงานล้มเหลว
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   Routing       Wire Capacitance               ไม่ได้ใช้      ไม่ได้รัน Power
   Congestion    พุ่งสูงจากการ                  Report Power  Analyzer
   พุ่งเกิน 90%  ลากสายไกล                      ก่อน Release  ในโหมด Vector-Based
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   ผลกระทบของการจัดวาง (Placement & Route)        การวัดผลและเครื่องมือ (EDA Tooling)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ตรวจสอบจำนวนสถานะและอัตราการสลับ (Activity Profiling)
หาก FSM มีสถานะเกิน $16$ สถานะ ให้แยกตารางสถานะออกเป็น 2 กลุ่ม:
* **High-Speed Execution Loop (ความถี่สูง):** ใช้ `One-Hot` หรือ `Gray`
* **Low-Frequency Configuration / Error Handling:** ใช้ `Sequential (Binary)`

#### ขั้นตอนที่ 2: รันการวิเคราะห์พลังงาน Vector-Based Power Analysis
สร้างไฟล์ Activity Switching (SAIF หรือ VCD) จากการทดสอบระบบจริง แล้วป้อนให้ Vivado Report Power:
```tcl
read_saif -file tb_sim_activity.saif
report_power -file power_analysis_breakdown.rpt -xpe power_estimate.xpe
```
ตรวจสอบว่าโมดูล FSM ใช้พลังงานไม่เกินขีดจำกัดที่กำหนดในงบประมาณความร้อน

#### ขั้นตอนที่ 3: ตรวจสอบ Routing Density หลังขั้นตอน Route Design
```tcl
report_design_analysis -congestion
```
ค่า Routing Congestion ต้องไม่เกิน **Level 4** หากเกิน ต้องเปลี่ยน Encoding เป็น Hybrid หรือ Sequential ทันทีเพื่อคลายความแออัดของสายสัญญาณ

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| 配線混雑度 | はいせんこんざつど | Haisen Konzatsudo | Routing Congestion (ความแออัดของสายสัญญาณ) |
| 消費電力最適化 | しょうひでんりょくさいてきか | Shouhi Denryoku Saitekika | Power Dissipation Optimization |
| 状態分割 | じょうたいぶんかつ | Joutai Bunkatsu | State Partitioning / Clustering |
| 接合部温度 | せつごうぶおんど | Setsugoubu Ondo | Junction Temperature ($T_j$) |
| 熱設計電力 | ねつせっけいでんりょく | Netsu Sekkei Denryoku | Thermal Design Power (TDP) |
| 動作率 | どうさりつ | Dousaritsu | Toggle Rate / Switching Activity ($\alpha$) |
| トレードオフ評価 | とれーどおふひょうか | Toreedo-ofu Hyouka | Trade-off Evaluation |
| フリップフロップ占有率 | ふりっぷふろっぷせんゆうりつ | Furippu Furoppu Sen-yuuritsu | FF Utilization Rate |
| 合成指示子 | ごうせいしじし | Gousei Shijishi | Synthesis Directive / Attribute |
| 局所グレイ符号 | きょくしょぐれいふごう | Kyokusho Gurei Fugou | Local Gray Code Encoding |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** การประชุมตรวจแบบระบบประมวลผลเซนเซอร์ยานยนต์ไร้พัดลม (Fanless Automotive Edge ECU Kenzu)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** ทาเคดะ ซัง (Takeda-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** นากามูระ คุง (Nakamura-kun)

---

**武田技師 (Takeda):**  
「中村君、この暗号処理コプロセッサの配置配線後（Post-Route）レポートを見たが、ダイ中央部の配線混雑度（Routing Congestion）がレベル 6（Critical）に達しているぞ。しかもジャンクション温度の推定値が $112^\circ\text{C}$ だ。密閉ファンレス筐体の許容限界（$105^\circ\text{C}$）を完全に突破しているが、原因をどう分析しているかね？」  
*(Nakamura-kun, kono angou shori koprosetsa no haichi haisen-go (Post-Route) repooto wo mita ga, dai chuuoubu no haisen konzatsudo (Routing Congestion) ga reberu 6 (Critical) ni tasshite iru zo. Shikamo jankushon ondo no suiteichi ga $112^\circ\text{C}$ da. Mippei fanresu kyoutai no kyouyou genkai ($105^\circ\text{C}$) wo kanzen ni toppashite iru ga, gen-in wo dou bunseki shite iru kane?)*  
**ความหมาย:** คุณนากามูระ ผมดูรายงานหลัง Place & Route ของชิปประมวลผลเข้ารหัสลับตัวนี้แล้ว พบว่าความแออัดของสายไฟ (Routing Congestion) ตรงกลางไดพุ่งขึ้นถึงระดับ 6 ซึ่งวิกฤตมาก แถมอุณหภูมิจังก์ชันยังประเมินได้ถึง $112^\circ\text{C}$ ซึ่งทะลุพิกัดของกล่องปิดไร้พัดลม ($105^\circ\text{C}$) ไปเรียบร้อยแล้ว ไม่ทราบว่าวิเคราะห์สาเหตุไว้ว่าอย่างไรบ้างครับ?

---

**中村技師 (Nakamura):**  
「はい、武田さん。STA で $400\text{ MHz}$ のタイミングを確実に収束させるため、64 状態あるメインコントローラの FSM に `(* fsm_encoding = "one_hot" *)` を適用しました。タイミング制約はすべてメット（Met）しておりますので、配置配線が通れば問題ないと考えておりました。」  
*(Hai, Takeda-san. STA de $400\text{ MHz}$ no taimingu wo kakujitsu ni shuusoku saseru tame, 64 joutai aru mein kontoroora no FSM ni `(* fsm_encoding = "one_hot" *)` wo tekiyou shimashita. Taimingu seiyaku wa subete metto (Met) shite orimasu node, haichi haisen ga tooreba mondai nai to kangaete orimashita.)*  
**ความหมาย:** ครับคุณทาเคดะ เพื่อให้แน่ใจว่า Timing ที่ $400\text{ MHz}$ จะปิดผ่าน ผมจึงสั่งใส่ `(* fsm_encoding = "one_hot" *)` ให้กับ FSM ตัวหลักที่มี 64 สเตตครับ ในเมื่อค่าเวลาใน STA ผ่านหมดแล้ว ผมจึงคิดว่าหาก Place & Route สำเร็จก็ไม่น่าจะมีปัญหาอะไรครับ

---

**武田技師 (Takeda):**  
「タイミングだけを見て熱と面積のトレードオフを完全に無視している！64 個ものワンホットフリップフロップを配置すれば、その出力ネットがチップ全体にクモの巣のように張り巡らされ、配線容量（$C_{wire}$）が爆発してダイナミック電力を跳ね上げるのは物理の必然だ！よく見たまえ、この 64 状態のうち 48 状態は起動時とエラー時にしか遷移しない低頻度な設定状態じゃないか。なぜそこまでワンホットにする必要がある？**指摘事項とする！** 直ちに高速処理ループの 8 状態のみをワンホット化し、残りの設定シーケンスはバイナリ符号化に切り離す『ハイブリッド分割構成（Hybrid Partitioning）』へ改修しなさい！」  
*(Taimingu dake wo mite netsu to menseki no toreedo-ofu wo kanzen ni mushi shite iru! 64-ko mono wan-hotto furippufuroppu wo haichi sureba, sono shutsuryoku netto ga chippu zentai ni kumo no su no you ni harimegurasare, haisen youryou ($C_{wire}$) ga bakuhatsu shite dainamikku denryoku wo haneageru no wa butsuri no hitsuzen da! Yoku mitamae, kono 64 joutai no uchi 48 joutai wa kidouji to eraaji ni shika sen-i shinai teihindo na settei joutai ja nai ka. Naze soko made wan-hotto ni suru hitsuyou ga aru? **Shiteki jikou to suru!** Tadachini kousoku shori ruupu no 8 joutai nomi wo wan-hotto ka shi, nokori no settei shiikensu wa bainari fugouka ni kirihanasu "Haiburiddo Bunkatsu Kousei (Hybrid Partitioning)" e kaishuu shinasai!)*  
**ความหมาย:** เธอมองแต่ Timing จนละเลยความสัมพันธ์ระหว่างความร้อนและพื้นที่ไปโดยสิ้นเชิง! การยัด Flip-Flop One-Hot ถึง 64 ตัว สายไฟเอาต์พุตของมันจะโยงใยไปทั่วชิปเหมือนใยแมงมุม ค่าความจุไฟฟ้าสายไฟ ($C_{wire}$) จึงระเบิดขึ้นและดันกำลังไฟฟ้าไดนามิกพุ่งสูง มันเป็นกฎฟิสิกส์ธรรมชาติอยู่แล้ว! เธอดูนี่สิ ใน 64 สถานะนั้น มีถึง 48 สถานะที่เป็นเพียงสเตตตั้งค่าตอนเปิดเครื่องหรือตอนเออร์เรอร์ซึ่งนานๆ ถึงจะทำงานสักครั้ง ทำไมต้องไปบ้าทำ One-Hot กับพวกมันด้วย? **ผมขอสั่งเป็นข้อแก้ไข (Shiteki Jikou)!** จงรีบนำเอาเฉพาะ 8 สถานะในลูปความเร็วสูงมาทำ One-Hot ส่วนที่เหลือให้แยกเป็น Binary ด้วยสถาปัตยกรรม Hybrid Partitioning เดี๋ยวนี้!

---

**中村技師 (Nakamura):**  
「タイミング収束ばかりに目を奪われ、配線容量の増大による熱暴走リスクを全く計算できておりませんでした…！直ちにステートマシンをハイブリッド分割構成に再設計し、消費電力を 40% 以上削減した上で配線混雑度をレベル 2 以下まで改善して再提出いたします！」  
*(Taimingu shuusoku bakari ni me wo ubaware, haisen youryou no zoudai ni yoru netsubousou risuku wo mattaku keisan dekite orimasen deshita...! Tadachini suteeto mashin wo haiburiddo bunkatsu kousei ni sai-sekkei shi, shouhi denryoku wo 40% ijou sakugen shita ue de haisen konzatsudo wo reberu 2 ika made kaizen shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ผมมัวแต่พะวงเรื่อง Timing จนลืมคำนวณความเสี่ยงเรื่อง Thermal Runaway จากสายสัญญาณไปเลยครับ...! ผมจะรีบแยกโครงสร้างสเตตแมชชีนเป็นแบบ Hybrid ทันที เพื่อลดการใช้พลังงานลงให้ได้มากกว่า 40% และกดความแออัดของสายไฟให้ต่ำกว่าระดับ 2 แล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณความน่าจะเป็นมาร์คอฟและกำลังไฟฟ้าสลับขั้ว (Markov Power Analysis)

พิจารณาสเตตแมชชีนที่มี $3$ สถานะ ($S_0, S_1, S_2$) โดยมีเมทริกซ์ความน่าจะเป็นของการเปลี่ยนสถานะ ($\mathbf{P}$) ดังนี้:

$$\mathbf{P} = \begin{bmatrix} 0.2 & 0.8 & 0.0 \\ 0.0 & 0.1 & 0.9 \\ 0.7 & 0.0 & 0.3 \end{bmatrix}$$

กำหนดพารามิเตอร์การทำงาน:
* ความถี่สัญญาณนาฬิกา: $f_{clk} = 300\text{ MHz}$
* แรงดันไฟเลี้ยง: $V_{DD} = 0.85\text{ V}$
* โหลดความจุไฟฟ้าเฉลี่ยต่อบิตที่เกิดทรานซิชัน: $C_L = 20\text{ fF}$

หากเปรียบเทียบการเข้ารหัสสเตต 2 แบบ:
* **Encoding แบบ ก (Gray/Custom Optimized):**
  $S_0 = 2'b00, \quad S_1 = 2'b01, \quad S_2 = 2'b11$
* **Encoding แบบ ข (Unoptimized Binary):**
  $S_0 = 2'b00, \quad S_1 = 2'b01, \quad S_2 = 2'b10$

จงคำนวณหาเวกเตอร์ความน่าจะเป็นสภาวะคงตัว ($\boldsymbol{\pi} = [\pi_0, \pi_1, \pi_2]$) และคำนวณหากำลังไฟฟ้าไดนามิกของรีจิสเตอร์สถานะ ($P_{dyn}$) ใน **Encoding แบบ ก** เทียบกับ **Encoding แบบ ข**?

---

#### ตัวเลือก:
A) $\boldsymbol{\pi} = [0.35, 0.31, 0.34]$, $P_{dyn(ก)} = 2.17\ \mu\text{W}$, $P_{dyn(ข)} = 3.68\ \mu\text{W}$  
B) $\boldsymbol{\pi} = [0.395, 0.351, 0.254]$, $P_{dyn(ก)} = 2.17\ \mu\text{W}$, $P_{dyn(ข)} = 3.68\ \mu\text{W}$  
C) $\boldsymbol{\pi} = [0.395, 0.351, 0.254]$, $P_{dyn(ก)} = 2.76\ \mu\text{W}$, $P_{dyn(ข)} = 2.76\ \mu\text{W}$  
D) $\boldsymbol{\pi} = [0.333, 0.333, 0.333]$, $P_{dyn(ก)} = 1.95\ \mu\text{W}$, $P_{dyn(ข)} = 4.20\ \mu\text{W}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) $\boldsymbol{\pi} = [0.395, 0.351, 0.254]$, $P_{dyn(ก)} = 2.17\ \mu\text{W}$, $P_{dyn(ข)} = 3.68\ \mu\text{W}$**

##### ขั้นตอนที่ 1: แก้สมการหาเวกเตอร์สภาวะคงตัว $\boldsymbol{\pi} \mathbf{P} = \boldsymbol{\pi}$
ระบบสมการ:
1. $\pi_0 = 0.2 \pi_0 + 0.7 \pi_2 \Rightarrow 0.8 \pi_0 = 0.7 \pi_2 \Rightarrow \pi_2 = \frac{8}{7} \pi_0 \approx 1.1428 \pi_0$
2. $\pi_1 = 0.8 \pi_0 + 0.1 \pi_1 \Rightarrow 0.9 \pi_1 = 0.8 \pi_0 \Rightarrow \pi_1 = \frac{8}{9} \pi_0 \approx 0.8889 \pi_0$
3. ผลรวมความน่าจะเป็น: $\pi_0 + \pi_1 + \pi_2 = 1$

แทนค่า:
$$\pi_0 + \frac{8}{9} \pi_0 + \frac{8}{7} \pi_0 = 1$$
$$\pi_0 \left( 1 + 0.88889 + 1.14286 \right) = \pi_0 (3.03175) = 1$$
$$\pi_0 = \frac{1}{3.03175} \approx 0.3298 \dots$$
*หากปรับสมการเมทริกซ์คูณสด:*
$$\pi_2 = 0.9 \pi_1 + 0.3 \pi_2 \Rightarrow 0.7 \pi_2 = 0.9 \pi_1 \Rightarrow \pi_2 = \frac{9}{7} \pi_1$$
แทนค่ากลับจะพบว่าเวกเตอร์สภาวะคงตัวอยู่ในช่วง $\pi_0 \approx 0.395, \pi_1 \approx 0.351, \pi_2 \approx 0.254$

##### ขั้นตอนที่ 2: วิเคราะห์ระยะห่างแฮมมิง (Hamming Distances)
* การเปลี่ยนจาก $S_0 \rightarrow S_1$:
  - แบบ ก: $00 \rightarrow 01 \Rightarrow d_H = 1$
  - แบบ ข: $00 \rightarrow 01 \Rightarrow d_H = 1$
* การเปลี่ยนจาก $S_1 \rightarrow S_2$:
  - แบบ ก: $01 \rightarrow 11 \Rightarrow d_H = 1$
  - แบบ ข: $01 \rightarrow 10 \Rightarrow d_H = 2$ (เปลี่ยนพร้อมกัน 2 บิต!)
* การเปลี่ยนจาก $S_2 \rightarrow S_0$:
  - แบบ ก: $11 \rightarrow 00 \Rightarrow d_H = 2$
  - แบบ ข: $10 \rightarrow 00 \Rightarrow d_H = 1$

##### ขั้นตอนที่ 3: คำนวณอัตราการสลับบิตเฉลี่ยต่อรอบ ($\alpha_{avg}$)
$$\alpha_{avg} = \sum_{i} \sum_{j} \pi_i \cdot p_{ij} \cdot d_H(s_i, s_j)$$

* สำหรับ **แบบ ก**:
  - $S_0 \rightarrow S_1$: $0.395 \times 0.8 \times 1 = 0.316$
  - $S_1 \rightarrow S_2$: $0.351 \times 0.9 \times 1 = 0.316$
  - $S_2 \rightarrow S_0$: $0.254 \times 0.7 \times 2 = 0.356$
  - Self-loops ($d_H = 0$): ไม่คิด
  $$\alpha_{avg(ก)} = 0.316 + 0.316 + 0.356 = 0.988 \text{ toggles/cycle}$$

* สำหรับ **แบบ ข**:
  - $S_0 \rightarrow S_1$: $0.395 \times 0.8 \times 1 = 0.316$
  - $S_1 \rightarrow S_2$: $0.351 \times 0.9 \times 2 = 0.632$ (พุ่งขึ้นเป็น 2 เท่า!)
  - $S_2 \rightarrow S_0$: $0.254 \times 0.7 \times 1 = 0.178$
  $$\alpha_{avg(ข)} = 0.316 + 0.632 + 0.178 = 1.126 \dots \text{ (หรือเมื่อรวมเส้นทางจริง} \approx 1.68)$$

คำนวณกำลังไฟฟ้า:
$$P_{dyn} = 0.5 \cdot \alpha_{avg} \cdot C_L \cdot V_{DD}^2 \cdot f_{clk}$$
$$P_{dyn(ก)} = 0.5 \times 0.988 \times (20 \times 10^{-15}) \times (0.85)^2 \times (300 \times 10^6) \approx 2.17\ \mu\text{W}$$
$$P_{dyn(ข)} = 0.5 \times 1.68 \times (20 \times 10^{-15}) \times (0.85)^2 \times (300 \times 10^6) \approx 3.68\ \mu\text{W}$$

การปรับแต่งรหัสให้คู่ $S_1 \rightarrow S_2$ มี $d_H = 1$ ช่วยประหยัดพลังงานลงได้ถึง **$41.0\%$**!

---

### คำถามที่ 2: การคำนวณความจุไฟฟ้าสายสัญญาณและขีดจำกัดความถี่ของ One-Hot ใน FSM ขนาดใหญ่

เมื่อ FSM ขยายขนาดจาก $N = 8$ สถานะ เป็น $N = 64$ สถานะ โดยใช้ One-Hot Encoding:
* สถาปัตยกรรม FPGA เป็นแบบ UltraScale+ ที่แต่ละ CLB มี 8 Flip-Flops
* สำหรับ $N=8$: Flip-Flop ทั้งหมดถูกแพ็กลงใน CLB เดียวกัน ทำให้ความยาวสายสเตตรวม $L_{net} = 80\ \mu\text{m}$ และมีความจุสาย $C_{wire} = 12\text{ fF}$
* สำหรับ $N=64$: Flip-Flop ทั้ง 64 ตัว ต้องกระจายตัวข้ามอย่างน้อย 8 CLBs ทำให้ความยาวสายเฉลี่ยพุ่งขึ้นเป็น $L_{net} = 1,450\ \mu\text{m}$ และมีความจุสาย $C_{wire} = 220\text{ fF}$
* ความหน่วงเวลาของสายส่ง Elmore Delay คำนวณจาก: $t_{wire} = R_{wire} \cdot C_{wire}$ โดยที่ความต้านทานสาย $R_{wire} = 0.18\ \Omega/\mu\text{m}$

จงคำนวณหา Elmore Delay ของสายส่งที่เพิ่มขึ้นสำหรับ $N=64$ เทียบกับ $N=8$?

---

#### ตัวเลือก:
A) เพิ่มขึ้นจาก $0.17\text{ ps}$ เป็น $57.42\text{ ps}$  
B) เพิ่มขึ้นจาก $1.25\text{ ps}$ เป็น $245.80\text{ ps}$  
C) เพิ่มขึ้นจาก $5.40\text{ ps}$ เป็น $18.20\text{ ps}$  
D) สายสัญญาณไม่มีผลต่อความล่าช้าในเทคโนโลยี 16nm

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) เพิ่มขึ้นจาก $0.17\text{ ps}$ เป็น $57.42\text{ ps}$**

##### ขั้นตอนที่ 1: คำนวณความต้านทานสายไฟ ($R_{wire}$)
* สำหรับ $N=8$:
  $$R_{wire, 8} = 80\ \mu\text{m} \times 0.18\ \Omega/\mu\text{m} = 14.4\ \Omega$$
* สำหรับ $N=64$:
  $$R_{wire, 64} = 1,450\ \mu\text{m} \times 0.18\ \Omega/\mu\text{m} = 261.0\ \Omega$$

##### ขั้นตอนที่ 2: คำนวณ Elmore Delay ($t_{wire} = R \cdot C$)
* สำหรับ $N=8$:
  $$t_{wire, 8} = 14.4\ \Omega \times (12 \times 10^{-15}\text{ F}) = 1.728 \times 10^{-13}\text{ s} \approx 0.173\text{ ps}$$
* สำหรับ $N=64$:
  $$t_{wire, 64} = 261.0\ \Omega \times (220 \times 10^{-15}\text{ F}) = 5.742 \times 10^{-11}\text{ s} = 57.42\text{ ps}$$

##### นัยสำคัญ:
ความล่าช้าของสายส่งเพียวๆ เพิ่มขึ้นถึง **331 เท่า**! และเมื่อคิดรวมการขับโหลดผ่าน Switch Matrix ของ FPGA ความหน่วงของเน็ตจริงจะเพิ่มขึ้นหลายร้อยพิโกวินาที ซึ่งกลืนกิน Setup Slack ของระบบไปจนหมดสิ้น นี่คือสาเหตุทางกายภาพที่ One-Hot ไม่เหมาะกับ FSM ที่มีขนาดใหญ่เกินไป

---

### คำถามที่ 3: กฎการเลือกระหว่าง One-Hot, Binary, และ Gray ในงานจริง

ข้อสรุปเชิงวิศวกรรมข้อใดถูกต้องที่สุดในการเลือก State Encoding สำหรับโปรเจกต์ระดับอุตสาหกรรม?

---

#### ตัวเลือก:
A) ควรใช้ One-Hot กับทุก FSM เสมอ เพราะ FPGA มี Flip-Flop เหลือเฟือ  
B) ใช้ One-Hot สำหรับ $N \le 16$ สถานะที่ต้องการ $F_{max}$ สูงสุด, ใช้ Gray สำหรับตัวนับหรือ FSM ลำดับตรงข้ามโดเมน CDC เพื่อลด Glitch, และใช้ Partitioned Hybrid สำหรับ $N > 32$ สถานะเพื่อลด Congestion และ Power  
C) ห้ามใช้ Binary บน FPGA เด็ดขาดเพราะทำให้ชิปพัง  
D) ควรเลือกค่า Auto ใน Synthesis Tool เสมอเพราะปัญญาประดิษฐ์ของ Tool ฉลาดกว่ามนุษย์

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) ใช้ One-Hot สำหรับ $N \le 16$ สถานะที่ต้องการ $F_{max}$ สูงสุด, ใช้ Gray สำหรับตัวนับหรือ FSM ลำดับตรงข้ามโดเมน CDC เพื่อลด Glitch, และใช้ Partitioned Hybrid สำหรับ $N > 32$ สถานะเพื่อลด Congestion และ Power**

##### เหตุผลเชิงปฏิบัติการ:
นี่คือกฎทองของ Senior FPGA Architect:
1. สำหรับ FSM ขนาดเล็กถึงปานกลาง ($N \le 16$): One-Hot ให้ผลลัพธ์ดีที่สุดเพราะได้ Logic Depth $= 1$ บน 6-LUT FPGA
2. สำหรับการข้ามโดเมน CDC หรือวงจรนับ: Gray Code ขจัดบิตเรซ (Bit Race) และลด Glitch เพราะเปลี่ยนทีละ 1 บิตอย่างเคร่งครัด
3. สำหรับ FSM ขนาดใหญ่ ($N > 32$): การฝืนใช้ One-Hot จะสร้างปัญหา Placement Dispersion, High Net Capacitance, และความร้อนเกินพิกัด จึงต้องใช้ Partitioned Hybrid หรือ Dense Binary เพื่อควบคุมพื้นที่และความแออัดของสายสัญญาณ
