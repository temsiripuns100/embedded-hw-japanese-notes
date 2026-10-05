# Lesson 124: FPGA State Machine - Part 4: Pipelining State Machines for Timing Closure (パイプライン化によるタイミング収束)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ข้อจำกัดของทฤษฎีลูปป้อนกลับ (The Fundamental FSM Loop Bound Theorem)
ในการปรับแต่งความเร็วของวงจรดิจิทัลระดับสูง เทคนิคการทำ **Pipelining** มักถูกนำมาใช้เพื่อแบ่งเส้นทางข้อมูลขนาดยาว (Long Datapath) ออกเป็นท่อนย่อยๆ ด้วยการแทรก D-Flip-Flop คั่นกลาง สำหรับวงจรประเภททิศทางเดียว (Feedforward Datapath / Directed Acyclic Graph: DAG) การใส่ Register เพิ่มเติมจะส่งผลกระทบเพียงแค่เพิ่มความล่าช้าในหน่วยรอบสัญญาณนาฬิกา (Latency) แต่จะไม่รบกวนตรรกะความถูกต้องของการประมวลผล

ทว่าสำหรับ **State Machine (FSM)** โครงสร้างของมันคือ **ระบบป้อนกลับแบบวนลูป (Feedback Cyclic System)**:

$$\mathbf{S}(t+1) = \delta(\mathbf{S}(t), \mathbf{X}(t))$$

```
               ข้อแตกต่างทางโครงสร้างระหว่าง Datapath และ FSM Loop
   
   [ 1. Feedforward Datapath: ตัดต่อ Pipeline ได้อิสระ ]
   In --->[ Logic A ]--->| Reg |--->[ Logic B ]--->| Reg |--->[ Logic C ]---> Out
   
   [ 2. FSM Feedback Loop: มีข้อจำกัดของ Iteration Bound อย่างเคร่งครัด ]
                 +---------------------------------------+
                 |       State Feedback Path             |
                 v                                       |
   Inputs X ---->+--->[ Next-State Logic ]---> D       Q +----> Current State S(t)
                      [   delta(S, X)   ]     |StateReg|
                                              +--------+
```

ตามทฤษฎีสถาปัตยกรรมประมวลผลสัญญาณของ Keshab K. Parhi ขีดจำกัดความเร็วสูงสุดของระบบที่มีลูปป้อนกลับถูกควบคุมโดย **Iteration Bound ($T_{\infty}$)**:

$$T_{\infty} = \max_{l \in \text{Loops}} \left( \frac{D_l}{N_l} \right)$$

โดยที่:
* $D_l$ คือ ความหน่วงเวลารวมของลอจิกคอมบิเนชันภายในลูปป้อนกลับที่ $l$ ($D_l = t_{co} + t_{comb\_loop} + t_{su}$)
* $N_l$ คือ จำนวนรีจิสเตอร์ (Flip-Flops) ภายในลูปป้อนกลับนั้น

เนื่องจากใน FSM มาตรฐานทั่วไป วงจรต้องตัดสินใจสถานะรอบถัดไปเพื่อนำกลับมาใช้ในรอบติดกันทันทีเสมอ จำนวนรีจิสเตอร์ในลูปป้อนกลับจึงมีค่าคงที่เท่ากับ **$N_l = 1$ เสมอ**!
ส่งผลให้คาบเวลาต่ำสุดของสัญญาณนาฬิกาถูกล็อกด้วยสมการเด็ดขาด:

$$T_{clk\_min} \ge T_{\infty} = t_{co} + t_{comb\_delta} + t_{su} + T_{uncertainty}$$

**วิศวกรไม่สามารถแทรก Register เข้าไปในลูปป้อนกลับของ FSM แบบสุ่มสี่สุ่มห้าได้** เพราะการเพิ่ม $N_l = 2$ โดยไม่ปรับตรรกะ จะทำให้ FSM มองเห็นสถานะของตัวเองล่าช้าไป 1 ไซเคิล ($S(t)$ กลายเป็น $S(t-1)$) ส่งผลให้เงื่อนไขการตัดสินใจของโพรโทคอลหลุดจังหวะ (Protocol Phase Misalignment) และระบบพังทลายทันที!

---

### 1.2 เทคนิคขั้นสูงในการทำลายขีดจำกัด Loop Bound (Breaking the FSM Bottleneck)

เพื่อให้ FSM สามารถทำงานทะลุเพดานความเร็วระดับ $400 - 600\text{ MHz}$ บน FPGA ยุคใหม่ วิศวกรอาวุโสจะประยุกต์ใช้ 4 กลยุทธ์สถาปัตยกรรมขั้นสูงดังต่อไปนี้:

```
+------------------------------------+---------------------------------------------------------------+
| เทคนิคทางสถาปัตยกรรม               | กลไกการทำงานทางวิศวกรรม (Engineering Mechanism)               |
+------------------------------------+---------------------------------------------------------------+
| 1. Look-Ahead State Pre-computation| คลี่ลูปทรานซิชันล่วงหน้า 2 ไซเคิล ($S_{n+2} = \delta(\delta(S_n, X_n), X_{n+1})$) |
| 2. Speculative Branch Shadow FSM   | คำนวณล่วงหน้าทั้งสองกิ่งเงื่อนไข แล้วใช้ Registered MUX สลับ |
| 3. Output Register Decoupling      | แยกตรรกะการขับ Output ออกมาเป็น Pipeline Stage อิสระ          |
| 4. Hierarchical FSM Decomposition  | แตก FSM ยักษ์เป็น Macro-Sequencer + Fast Micro-Controller      |
+------------------------------------+---------------------------------------------------------------+
```

#### 1.2.1 Look-Ahead State Transition (การประเมินสถานะล่วงหน้า 2 ไซเคิล)
แทนที่จะรอให้สัญญาณอินพุต $X(t)$ มาถึงแล้วค่อยประเมินสถานะ $S(t+1)$ เราสามารถแบ่งอินพุตออกเป็นสองส่วน: ส่วนที่รู้ล่วงหน้าจาก Datapath Pipeline และส่วนที่มาในนาทีสุดท้าย โดยใช้สมการคลี่ลูป (Loop Unrolling):

$$\mathbf{S}(t+2) = \mathbf{F}(\mathbf{S}(t), \mathbf{X}(t), \mathbf{X}(t+1))$$

เมื่อใช้วิธีนี้ ลูปป้อนกลับจะยอมให้มี Flip-Flop $N_l = 2$ ตัว ทำให้ Iteration Bound ลดลงครึ่งหนึ่ง:
$$T_{\infty, unrolled} = \frac{D_{unrolled}}{2}$$

```
                โครงสร้าง Speculative Look-Ahead State Transition
                                 +--->[ Next State IF Cond=True  ]--->[ 1 ]--+
                                 |                                           |
   Current State S(t) -----------+                                           +->[ MUX ]---> D [Reg]
                                 |                                           |    ^
                                 +--->[ Next State IF Cond=False ]--->[ 0 ]--+    |
                                                                                  |
   Late Arriving Condition Signal X(t) -------------------------------------------+ (เร็วระดับ LUT เดียว!)
```

การจัดวางแบบนี้ย้ายการคำนวณที่ซับซ้อนไปทำล่วงหน้าแบบขนาน และเหลือไว้เพียง มัลติเพล็กเซอร์ (MUX) ชั้นเดียวที่ถูกควบคุมด้วยสัญญาณเงื่อนไขที่มาถึงช้าที่สุด ทำให้ Timing ปิดได้อย่างง่ายดาย

---

### 1.3 การแยก Output Decoupling และ Shadow Registering
ในระบบที่เอาต์พุตของ FSM มีภาระการเชื่อมต่อสูง (High Fan-Out: ขับสัญญาณควบคุมไปยังหลายสิบโมดูลทั่วทั้งชิป) สายสัญญาณที่แตกแขนงยาวจะสร้างความหน่วงเวลาเดินสาย ($t_{net}$) มหาศาล ซึ่งจะย้อนกลับมาฉุดรั้งให้ Setup Slack ของ FSM ติดลบ

วิธีแก้ไขมาตรฐานคือการสร้าง **Shadow Output Registers**:
1. เอาต์พุตควบคุมจะไม่ถูกดึงออกจาก State Register โดยตรง
2. สร้างสเตจ Pipeline Register อิสระสำหรับขับ Output โดยคำนวณเงื่อนไขล่วงหน้า (Pre-decode Output Pipeline):
   $$\mathbf{Y}_{pipe}(t+1) = \lambda_{lookahead}(\mathbf{S}(t), \mathbf{X}(t))$$

```
   State FSM Engine (Local Clock Region)               High Fanout Control Sinks
   +------------------------------------+              +------------------------+
   | Current State FSM                  |              | Datapath ALU Stage 1   |
   |   [State Reg]                      |              +------------------------+
   |        |                           |              +------------------------+
   |        v                           |  Low Skew    | Datapath Multiplier    |
   |   [Look-Ahead LUT]                 |  Fast Line   +------------------------+
   |        |                           |              +------------------------+
   |        v                           +------------->| Memory Write Port      |
   |   [Shadow Reg 1] (Replicated)      |              +------------------------+
   |   [Shadow Reg 2] (Replicated)      |              +------------------------+
   |   [Shadow Reg 3] (Replicated)      |              | DMA Engine Burst Ctrl  |
   +------------------------------------+              +------------------------+
```

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: สถาปัตยกรรม Look-Ahead Pipelined FSM สำหรับ 400MHz

```systemverilog
//=============================================================================
// Module: pipelined_packet_parser_fsm.sv
// Description: Ultra-High-Speed (400MHz+) Look-Ahead Pipelined State Machine
// Compliance: Timing Sign-off at UltraScale+ -2 Speed Grade
//=============================================================================
`timescale 1ns / 1ps

module pipelined_packet_parser_fsm (
    input  logic         clk,
    input  logic         rst_n,
    // สตรีมข้อมูลแพ็กเก็ตขาเข้า
    input  logic [63:0]  axis_tdata,
    input  logic         axis_tvalid,
    input  logic         axis_tlast,
    // สัญญาณควบคุมการประมวลผลขาออก (Registered Output)
    output logic         hdr_parse_en,
    output logic         payload_write_en,
    output logic         crc_check_en,
    output logic [1:0]   current_stage_id
);

    // นิยามสเตตการทำงาน
    typedef enum logic [1:0] {
        ST_PREAMBLE = 2'b00,
        ST_HEADER   = 2'b01,
        ST_PAYLOAD  = 2'b10,
        ST_TAIL_CRC = 2'b11
    } state_t;

    (* fsm_encoding = "one_hot" *)
    state_t current_state, next_state;

    // สัญญาณคำนวณเงื่อนไขล่วงหน้า (Pre-computed Branch Conditions)
    // สกัดล่วงหน้า 1 ไซเคิลจาก Datapath เพื่อไม่ให้หน่วงในลูป FSM
    logic is_vlan_tagged_nxt;
    logic is_payload_ending_nxt;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            is_vlan_tagged_nxt    <= 1'b0;
            is_payload_ending_nxt <= 1'b0;
        end else begin
            // ทำการ Decode บิตข้อมูลคู่ขนานไปกับช่วงเวลาก่อนหน้า
            is_vlan_tagged_nxt    <= (axis_tdata[15:0] == 16'h8100);
            is_payload_ending_nxt <= axis_tlast;
        end
    end

    //-------------------------------------------------------------------------
    // 1. State Register Process
    //-------------------------------------------------------------------------
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            current_state <= ST_PREAMBLE;
        end else begin
            current_state <= next_state;
        end
    end

    //-------------------------------------------------------------------------
    // 2. Next-State Logic: ปรับให้เหลือ Logic Depth เพียง 1 ชั้น (Fast MUX)
    //-------------------------------------------------------------------------
    always_comb begin
        next_state = current_state;

        case (current_state)
            ST_PREAMBLE: begin
                if (axis_tvalid) begin
                    next_state = ST_HEADER;
                end
            end

            ST_HEADER: begin
                // ใช้สัญญาณที่ Pre-decode มาแล้ว ทำให้ Timing Path สั้นมาก
                if (is_vlan_tagged_nxt) begin
                    next_state = ST_HEADER; // วนรอบอ่าน VLAN เพิ่มอีกคำ
                end else begin
                    next_state = ST_PAYLOAD;
                end
            end

            ST_PAYLOAD: begin
                if (is_payload_ending_nxt) begin
                    next_state = ST_TAIL_CRC;
                end
            end

            ST_TAIL_CRC: begin
                next_state = ST_PREAMBLE;
            end

            default: begin
                next_state = ST_PREAMBLE;
            end
        endcase
    end

    //-------------------------------------------------------------------------
    // 3. Decoupled Pipeline Output Stage
    // แยก Flip-Flop ขับเอาต์พุตออกจากลูป FSM เพื่อแยกเส้นทางวิกฤต (Isolate Paths)
    //-------------------------------------------------------------------------
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            hdr_parse_en     <= 1'b0;
            payload_write_en <= 1'b0;
            crc_check_en     <= 1'b0;
            current_stage_id <= 2'b00;
        end else begin
            // ขับเอาต์พุตโดยอิงจาก next_state (Look-Ahead Driving)
            hdr_parse_en     <= (next_state == ST_HEADER);
            payload_write_en <= (next_state == ST_PAYLOAD);
            crc_check_en     <= (next_state == ST_TAIL_CRC);
            current_stage_id <= next_state;
        end
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในโครงการพัฒนาโมดูลประมวลผลแพ็กเก็ตเครือข่ายความเร็วสูง 100GbE Ethernet MAC บนชิป UltraScale+ FPGA กำหนดความถี่สัญญาณนาฬิกา $f_{clk} = 322.265\text{ MHz}$ ($T_{clk} = 3.103\text{ ns}$) สเตตแมชชีนตรวจรับเฟรม (Frame Parser FSM) มีตรรกะการตรวจสอบฟิลด์ IP Header และคำนวณ CRC32 แบบในตัว ทำให้เส้นทางลอจิกในลูปของ Next-State มีความลึกของเกตถึง 6 ระดับ LUT ($Logic\ Depth = 6$) รายงาน STA ฟ้องความเสี่ยงขั้นวิกฤต: $WNS = -0.740\text{ ns}$ (Setup Slack ติดลบอย่างรุนแรง)

**ผลลัพธ์ที่ล้มเหลว:** วิศวกรจบใหม่พยายามแก้ปัญหา Timing ด้วยการ **"แทรก Flip-Flop 1 สเตจ"** เข้าไปในลูปสถานะถัดไปเพื่อตัดทอนลอจิก ผลปรากฏว่ารายงาน Vivado Timing ผ่านฉลุย ($WNS = +0.320\text{ ns}$) แต่นำบอร์ดไปเสียบทดสอบจริงกลับพบว่า แพ็กเก็ตเครือข่ายทุกแพ็กเก็ตที่ส่งผ่านโมดูลนี้เกิดการสูญเสียข้อมูลทั้งหมด ($100\%$ Packet Drop)! เนื่องจาก FSM เปลี่ยนสเตตช้าไป 1 ไซเคิล ทำให้หัวเฟรมของ Ethernet หลุดหายและตัวชี้ตำแหน่งข้อมูลใน BRAM ผิดตำแหน่งไป 8 ไบต์

```
                    ความล้มเหลวจากการแทรก Register มั่วซั่วในลูป FSM
   
   Clock Cycle:     |   C0   |   C1   |   C2   |   C3   |   C4   |
   
   Ethernet Data:   [PREAMBLE][ HEADER ][PAYLOAD0][PAYLOAD1][  CRC   ]
   
   Correct FSM:     [PREAMBLE][ HEADER ][PAYLOAD ][PAYLOAD ][  CRC   ] (ตรงจังหวะเป๊ะ)
   
   Naive Pipelined: [PREAMBLE][PREAMBLE][ HEADER ][PAYLOAD ][PAYLOAD ] (หลุดไป 1 ไซเคิล!)
   (แทรก 1 FF)                            ^
                                           |
                              อ่าน Header ผิดตำแหน่ง! นึกว่า Payload0 คือ Header!
                              -> CRC Error ทันที -> 100% Packet Discard!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมระบบเครือข่ายถึงทิ้งแพ็กเก็ตทั้งหมด (100% Packet Discard)?**
   * *ตอบ:* วงจรตรวจสอบความถูกต้องของข้อมูล (CRC Checker) รายงานว่าข้อมูลในทุกเฟรมมีความเสียหาย
2. **ทำไมข้อมูลถึงมีความเสียหายทุกเฟรม?**
   * *ตอบ:* โมดูลแยกแยะฟิลด์ (Frame Parser) เริ่มต้นตัดหัวแพ็กเก็ตผิดตำแหน่ง ทำให้ข้อมูลในเพย์โหลดถูกเลื่อนไป 8 ไบต์
3. **ทำไม Frame Parser ถึงตัดข้อมูลผิดตำแหน่ง?**
   * *ตอบ:* สเตตแมชชีนเปลี่ยนสถานะจาก `ST_HEADER` ไปเป็น `ST_PAYLOAD` ล่าช้ากว่าข้อมูลจริงไป 1 คาบสัญญาณนาฬิกา
4. **ทำไมสเตตแมชชีนถึงเปลี่ยนสถานะล่าช้าไป 1 คาบ?**
   * *ตอบ:* วิศวกรนำ Flip-Flop ตัวใหม่ไปแทรกคั่นกลางระหว่าง Next-State Logic และ Current State Register โดยตรงเพื่อแก้ปัญหา Slack
5. **ทำไมวิศวกรจึงแทรก Flip-Flop ลงในลูปป้อนกลับของ FSM?**
   * *ตอบ:* วิศวกรขาดความเข้าใจเรื่อง **Iteration Bound** คิดว่าการทำ Pipelining บน FSM ทำได้เหมือน Datapath ทั่วไป โดยไม่ตระหนักว่าการแทรก Register ในลูปป้อนกลับจะทำลายความสัมพันธ์เชิงเวลาของโพรโทคอล

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ Frame Parser FSM
   
   ความรู้ความเข้าใจสถาปัตยกรรม (Architectural)      ขั้นตอนการตรวจสอบ (Verification)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ไม่เข้าใจทฤษฎี  คิดว่า FSM                    ดูแค่ Timing   ขาด Cycle-Accurate
   Iteration     เหมือน Datapath                Slack เขียว    Protocol
   Bound         ทั่วไป                         แล้วปล่อยผ่าน  Simulation Test
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> 100% Packet Drop
                                                                |     จาก Pipelining หลุดเฟส
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   Logic Depth   รวมการคำนวณ                    ใช้ One-Hot    ไม่ทำ Look-Ahead
   ลึกถึง 6 LUT  CRC32 และความยาว               แต่เงื่อนไข     Pre-computation
   ในลูปเดียว    ไว้ใน Next-State               Fan-In กว้าง   ของสัญญาณอินพุต
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   โครงสร้าง RTL เดิม (RTL Design Structure)     ระเบียบวิธีแก้ไข (Design Methodology)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: วิเคราะห์เส้นทางวิกฤตของ FSM Feedback Loop
รันคำสั่ง Tcl ใน Vivado เพื่อตรวจสอบจำนวนระดับลอจิก (Logic Levels) ในลูปของสเตต:
```tcl
report_timing -from [get_cells -hier *current_state_reg*] \
              -to [get_cells -hier *current_state_reg*] \
              -max_paths 10 -sort_by slack
```
หากพบว่าค่า `Logic Levels` เกิน 2 หรือ 3 สำหรับความถี่ที่เกิน $300\text{ MHz}$ ห้ามแทรก Register ในลูปเด็ดขาด!

#### ขั้นตอนที่ 2: ดึงการคำนวณที่ซับซ้อนออกจากลูป FSM มาทำเป็น Look-Ahead Pipeline
แยกตรรกะการคำนวณขนาดใหญ่ (เช่น การเปรียบเทียบแอดเดรส, การนับความยาวไบต์, CRC) ออกมาเป็นโมดูลคู่ขนาน (Parallel Pre-decoder) ที่ทำงานใน Datapath ก่อนหน้าที่ข้อมูลจะเข้าสู่ FSM 1 ไซเคิล

#### ขั้นตอนที่ 3: ปรับ Next-State Logic ให้เหลือเพียง 1-Level MUX
ให้ FSM รับเพียงสัญญาณ Flag บิตเดียว (Single-bit Flag) ที่ผ่านการ Pre-decode มาแล้ว ทำให้ Next-State Logic มี Logic Depth $= 1$

#### ขั้นตอนที่ 4: รัน Cycle-Accurate Regression Testbench
ต้องมี Assertion ตรวจสอบความสัมพันธ์ระหว่างสัญญาณ `axis_tvalid`, `axis_tlast` และสเตตของ FSM เพื่อยืนยันว่าไม่มีรอบสัญญาณนาฬิกาใดที่เกิดอาการเฟสหลุด (Phase Slip)

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันジ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| 反復限界 | はんぷくげんかい | Hanpuku Genkai | Iteration Bound (ขีดจำกัดความเร็วรอบป้อนกลับ) |
| フィードバックループ | ふぃーどばっくるーぷ | Fiidobakku Ruupu | Feedback Loop (ลูปป้อนกลับของสถานะ) |
| 先読み状態遷移 | さきよみじょうたいせんい | Sakiyomi Joutai Sen-i | Look-Ahead State Transition |
| 投機実行 | とうきじっこう | Touki Jikkou | Speculative Execution (การประมวลผลเชิงเก็งกำไร) |
| パイプライン段数 | ぱいぷらいんだんすう | Paipurain Dansuu | Number of Pipeline Stages |
| レイテンシ整合性 | れいてんしせいごうせい | Reitenshi Seigousei | Latency Alignment / Consistency |
| 位相ずれ | いそうずれ | Isou-zure | Phase Shift / Phase Misalignment |
| 段数不整合 | だんすうふせいごう | Dansuu Fuseigou | Pipeline Depth Mismatch |
| シャドウレジスタ | しゃどうれじすた | Shadou Rejisuta | Shadow Register (รีจิสเตอร์คู่ขนานลดโหลด) |
| 論理階層削減 | ろんりかいそうさくげん | Ronri Kaisou Sakugen | Logic Depth Reduction (การลดทอนชั้นเกต) |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** ศูนย์พัฒนาผลิตภัณฑ์เน็ตเวิร์กขั้นสูง (Advanced Telecom ASIC/FPGA Review Lab)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** คิโนชิตะ ซัง (Kinoshita-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** อิชิกาวะ คุง (Ishikawa-kun)

---

**木下技師 (Kinoshita):**  
「石川君、この 100GbE パケット解析 FSM のタイミングレポートを見たが、WNS が $+0.320\text{ ns}$ で収束しているね。しかし RTL の変更差分（Diff）を確認すると、ステートレジスタのフィードバックループ内に無断でフリップフロップを1段追加しているようだが、プロトコルのレイテンシ整合性はどう担保したんだ？」  
*(Ishikawa-kun, kono 100GbE paketto kaiseki FSM no taimingu repooto wo mita ga, WNS ga $+0.320\text{ ns}$ de shuusoku shite iru ne. Shikashi RTL no henkou sabun (Diff) wo kakunin suru to, suteeto rejisuta no fiidobakku ruupu nai ni mudan de furippufuroppu wo ichidan tsuika shite iru you da ga, purotokoru no reitenshi seigousei wa dou tanpo shita nda?)*  
**ความหมาย:** คุณอิชิกาวะ ผมดูรายงาน Timing ของ FSM แยกแพ็กเก็ต 100GbE ตัวนี้แล้ว เห็นว่าค่า WNS ปิดผ่านได้ $+0.320\text{ ns}$ นะ แต่พอเปิดดู Diff ในโค้ด RTL กลับพบว่ามีการแอบแทรก Flip-Flop เพิ่มเข้าไป 1 สเตจในลูปป้อนกลับของ State Register แบบนี้คุณรักษาความตรงจังหวะของ Latency ตามโพรโทคอลไว้อย่างไรกันครับ?

---

**石川技師 (Ishikawa):**  
「はい、木下さん。Next-State ロジック内でパケット長比較と CRC 検証を行っていたため、ロジック階層が 6 段まで深くなりタイミングエラーが出ておりました。そこで、一般的なデータパスと同様にパイプラインレジスタを 1 段挿入してクリティカルパスを分断しました。タイミングは完全に収束しております！」  
*(Hai, Kinoshita-san. Next-State rojikku nai de paketto-chou hikaku to CRC kenshou wo okonatte ita tame, rojikku kaisou ga rokudan made fukanaku nari taimingu eraa ga dete orimashita. Sokode, ippanteki na deetapasu to douyou ni paipurain rejisuta wo ichidan sounyuu shite kuritikaru pasu wo bundan shimashita. Taimingu wa kanzen ni shuusoku shite orimasu!)*  
**ความหมาย:** ครับคุณคิโนชิตะ ในลอจิก Next-State เดิมมีการเปรียบเทียบความยาวแพ็กเก็ตและตรวจสอบ CRC ทำให้เกตลึกถึง 6 ระดับและติดลบ Timing ครับ ผมเลยแทรก Pipeline Register เข้าไป 1 ตัวเหมือนกับที่ทำใน Datapath ทั่วไปเพื่อตัด Critical Path ครับ ตอนนี้ Timing ปิดผ่านฉลุยแล้วครับ!

---

**木下技師 (Kinoshita):**  
「バカ者！FSM はデータパスのような単純な有向非巡回グラフ（DAG）ではない！状態遷移には**反復限界（Iteration Bound）**という厳格な理論的限界があるんだ。フィードバックループ内に勝手にレジスタを挟んだら、状態の更新が 1 クロック遅延してパケットの先頭データ（SOF）とステートの位相がずれてしまう！案の定、シミュレーションを実行してみたら全パケットがドロップしているじゃないか！直ちにこの安易なレジスタを撤去し、条件判定を前段のデータパスへ追い出す『先読み論理（Look-Ahead Architecture）』に再設計しなさい！」  
*(Bakamono! FSM wa deetapasu no you na tanjun na yuukou hijunkai gurafu (DAG) dewa nai! Joutai sen-i ni wa **hanpuku genkai (Iteration Bound)** to iu genkaku na rironteki genkai ga arunda. Fiidobakku ruupu nai ni katte ni rejisuta wo hasandara, joutai no koushin ga ichi-kurokku chien shite paketto no sentou deeta (SOF) to suteeto no isou ga zurete shimau! An no jou, shimyureeshon wo jikkou shite mitara zen-paketto ga doroppu shite iru ja nai ka! Tadachini kono an-i na rejisuta wo tekkyo shi, jouken hantei wo zendan no deetapasu e oidasu "Sakiyomi Ronri (Look-Ahead Architecture)" ni sai-sekkei shinasai!)*  
**ความหมาย:** เจ้าบื้อเอ๊ย! FSM มันไม่ใช่กราฟทิศทางเดียวไร้ลูป (DAG) เหมือนพวก Datapath นะ! วงจรเปลี่ยนสถานะมันถูกคุมด้วยทฤษฎี**ขีดจำกัดความเร็วรอบป้อนกลับ (Iteration Bound)** อันเข้มงวดอยู่! การไปยัด Register สุ่มสี่สุ่มห้าในลูปป้อนกลับ จะทำให้การอัปเดตสถานะช้าไป 1 ไซเคิล จนเฟสของหัวแพ็กเก็ต (SOF) กับสถานะของ FSM มันเหลื่อมกัน! แล้วผลก็เป็นไปตามคาด พอลองรัน Simulation ดู แพ็กเก็ตมันโดนทิ้งหมดทั้ง 100% เลยเห็นไหม! จงรีบถอด Register มักง่ายอันนี้ออกไปทันที แล้วย้ายเงื่อนไขที่ซับซ้อนออกไปคำนวณล่วงหน้าใน Datapath ฝั่งต้นทางด้วยสถาปัตยกรรม Look-Ahead เดี๋ยวนี้!

---

**石川技師 (Ishikawa):**  
「ぐうの音も出ません…！タイミングツールで緑色のチェックマークが出たことに満足して、プロトコルのクロック精度（Cycle-Accuracy）を完全に破壊してしまっておりました。直ちに先読みアーキテクチャへ書き直し、全テストベンチでのパケット通過を確認いたします！」  
*(Guu no ne mo demasen...! Taimingu tsuuru de midoriiro no chekkumaaku ga deta koto ni manzoku shite, purotokoru no kurokku seido (Cycle-Accuracy) wo kanzen ni hakai shite shimatte orimashita. Tadachini sakiyomi aakitekucha e kakinaoshi, zen-tesutobenchi de no paketto tsuuka wo kakunin itashimasu!)*  
**ความหมาย:** ผมเถียงไม่ออกเลยครับ...! ผมมัวแต่ดีใจที่เห็นเครื่องมือขึ้นเครื่องหมายถูกสีเขียวผ่าน Timing จนทำลายความถูกต้องในระดับรอบสัญญาณนาฬิกาของโพรโทคอลไปจนหมดสิ้น ผมจะรีบแก้ไขสถาปัตยกรรมเป็นแบบ Look-Ahead และรัน Testbench ให้แพ็กเก็ตส่งผ่านได้ครบถ้วนโดยด่วนครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณ Iteration Bound และการประเมินความเร็วสูงสุดของ FSM Loop

กำหนดพารามิเตอร์ของวงจร FSM แบบมีลูปป้อนกลับสถานะตัวหนึ่งบนบอร์ด UltraScale+ FPGA:
* Flip-Flop Clock-to-Q delay: $t_{co} = 0.240\text{ ns}$
* Flip-Flop Setup time: $t_{su} = 0.080\text{ ns}$
* ความหน่วงของเครือข่ายลอจิกคอมบิเนชันภายในลูปเปลี่ยนสถานะ ($Next-State Logic$): $t_{comb\_loop} = 2.480\text{ ns}$
* ค่าความไม่แน่นอนของสัญญาณนาฬิกา (Clock Uncertainty): $T_{unc} = 0.100\text{ ns}$
* ลูปป้อนกลับมี Flip-Flop ปัจจุบันเพียงสเตจเดียว ($N = 1$)

ระบบต้องการให้วงจรนี้ทำงานที่ความถี่สัญญาณนาฬิกาเป้าหมาย $f_{target} = 400\text{ MHz}$ ($T_{clk} = 2.500\text{ ns}$)

จงคำนวณหาค่า **Iteration Bound ($T_{\infty}$)** และประเมินค่า **Setup Slack ($WNS$)** ณ ความถี่เป้าหมาย พร้อมทั้งระบุว่า จะต้องปรับลดค่าความหน่วงของลอจิก $t_{comb\_loop}$ ลงมาอย่างน้อยกี่เปอร์เซ็นต์ จึงจะสามารถปิด Timing ได้พอดี ($WNS = 0.000\text{ ns}$)?

---

#### ตัวเลือก:
A) $T_{\infty} = 2.800\text{ ns}$, $WNS = -0.400\text{ ns}$, ต้องลด $t_{comb\_loop}$ ลงอย่างน้อย $16.1\%$  
B) $T_{\infty} = 2.900\text{ ns}$, $WNS = -0.400\text{ ns}$, ต้องลด $t_{comb\_loop}$ ลงอย่างน้อย $16.1\%$  
C) $T_{\infty} = 2.700\text{ ns}$, $WNS = -0.300\text{ ns}$, ต้องลด $t_{comb\_loop}$ ลงอย่างน้อย $12.1\%$  
D) $T_{\infty} = 3.100\text{ ns}$, $WNS = -0.600\text{ ns}$, ต้องลด $t_{comb\_loop}$ ลงอย่างน้อย $24.2\%$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) $T_{\infty} = 2.900\text{ ns}$, $WNS = -0.400\text{ ns}$, ต้องลด $t_{comb\_loop}$ ลงอย่างน้อย $16.1\%$**

##### ขั้นตอนที่ 1: คำนวณ Iteration Bound ($T_{\infty}$) และคาบเวลาขั้นต่ำ
ตามทฤษฎี Iteration Bound เมื่อ $N = 1$:
$$D_l = t_{co} + t_{comb\_loop} + t_{su} + T_{unc}$$
แทนค่า:
$$D_l = 0.240\text{ ns} + 2.480\text{ ns} + 0.080\text{ ns} + 0.100\text{ ns} = 2.900\text{ ns}$$
$$T_{\infty} = \frac{D_l}{N} = \frac{2.900\text{ ns}}{1} = 2.900\text{ ns}$$

##### ขั้นตอนที่ 2: คำนวณ Setup Slack ($WNS$) ที่ความถี่เป้าหมาย $400\text{ MHz}$
คาบเวลาเป้าหมาย:
$$T_{clk\_target} = \frac{1}{400\text{ MHz}} = 2.500\text{ ns}$$
สมการ Setup Slack:
$$WNS = T_{clk\_target} - T_{\infty} = 2.500\text{ ns} - 2.900\text{ ns} = -0.400\text{ ns}$$
(ระบบเกิด Setup Violation อย่างรุนแรง ไม่สามารถทำงานที่ $400\text{ MHz}$ ได้)

##### ขั้นตอนที่ 3: คำนวณความหน่วงลอจิกสูงสุดที่ยอมรับได้ ($t_{comb\_max}$)
เพื่อให้ $WNS = 0.000\text{ ns}$:
$$T_{clk\_target} \ge t_{co} + t_{comb\_max} + t_{su} + T_{unc}$$
$$2.500\text{ ns} \ge 0.240\text{ ns} + t_{comb\_max} + 0.080\text{ ns} + 0.100\text{ ns}$$
$$2.500\text{ ns} \ge t_{comb\_max} + 0.420\text{ ns}$$
$$t_{comb\_max} \le 2.500 - 0.420 = 2.080\text{ ns}$$

##### ขั้นตอนที่ 4: คำนวณเปอร์เซ็นต์ที่ต้องลดทอน
ความหน่วงลอจิกที่ต้องตัดออก:
$$\Delta t_{comb} = 2.480\text{ ns} - 2.080\text{ ns} = 0.400\text{ ns}$$
คิดเป็นสัดส่วนเปอร์เซ็นต์เทียบกับค่าเดิม:
$$\% \text{Reduction} = \frac{\Delta t_{comb}}{t_{comb\_loop}} \times 100\% = \frac{0.400}{2.480} \times 100\% \approx 16.129\%$$

ดังนั้นทีมออกแบบจำเป็นต้องลดทอนลอจิกในลูปของ FSM ลงอย่างน้อย **$16.13\%$** ด้วยการใช้ Look-Ahead สกัดเงื่อนไขที่ซับซ้อนออกไปประมวลผลล่วงหน้า

---

### คำถามที่ 2: การวิเคราะห์ผลกระทบของ High Fan-out และ Shadow Output Registering

ในสเตตแมชชีนขนาดใหญ่ สัญญาณควบคุมสถานะ `fsm_enable` ถูกส่งออกจาก State Register ไปขับโหลดปลายทางจำนวน $F = 64$ จุด (High Fan-Out Net) ทั่วทั้ง Die
* ค่าความหน่วงเวลาเดินสายแบบโหลดเดี่ยว (Base Net Delay): $t_{net\_base} = 0.250\text{ ns}$
* อัตราการเพิ่มของความหน่วงสายต่อจำนวน Fan-out (Fan-out Delay Penalty): $k_{fo} = 0.025\text{ ns/fanout}$
* เมื่อยังไม่ทำ Output Registering สัญญาณนี้ต้องเดินทางผ่านลอจิกถอดรหัสของ Moore $t_{lut} = 0.350\text{ ns}$
* เวลาที่มีให้ (Clock Period): $T_{clk} = 3.000\text{ ns}$, $t_{co} = 0.250\text{ ns}$, $t_{su} = 0.080\text{ ns}$, $T_{unc} = 0.120\text{ ns}$

หากทำการปรับปรุงโดยการใช้เทคนิค **Shadow Registering & Physical Fan-out Replication** โดยแบ่ง Flip-Flop ออกเป็น 4 ตัวขนานกัน ($F_{new} = 16$ โหลดต่อตัว) และวาง Register ให้แนบชิดกับบล็อกปลายทาง (Physical Clustered Placement) ทำให้ $t_{net\_base}$ ลดเหลือ $0.150\text{ ns}$

จงคำนวณหา Setup Slack ที่เพิ่มขึ้น ($\Delta WNS$) หลังการปรับปรุง?

---

#### ตัวเลือก:
A) Slack เพิ่มขึ้น $+0.850\text{ ns}$  
B) Slack เพิ่มขึ้น $+1.300\text{ ns}$  
C) Slack เพิ่มขึ้น $+1.650\text{ ns}$  
D) Slack เพิ่มขึ้น $+0.550\text{ ns}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: C) Slack เพิ่มขึ้น $+1.650\text{ ns}$**

##### ขั้นตอนที่ 1: คำนวณความหน่วงสายเดิมก่อนปรับปรุง ($t_{net\_orig}$)
$$t_{net\_orig} = t_{net\_base} + (k_{fo} \times F) = 0.250\text{ ns} + (0.025 \times 64)\text{ ns} = 0.250 + 1.600 = 1.850\text{ ns}$$
ความหน่วงเวลารวมของเส้นทางเดิม (จาก State Reg ผ่าน Moore LUT เดินสายไปยังปลายทาง):
$$T_{path\_orig} = t_{co} + t_{lut} + t_{net\_orig} + t_{su} + T_{unc}$$
$$T_{path\_orig} = 0.250 + 0.350 + 1.850 + 0.080 + 0.120 = 2.650\text{ ns}$$
Slack เดิม:
$$WNS_{orig} = T_{clk} - T_{path\_orig} = 3.000\text{ ns} - 2.650\text{ ns} = +0.350\text{ ns}$$

##### ขั้นตอนที่ 2: คำนวณความหน่วงสายใหม่หลังทำ Shadow Replicated Registering ($t_{net\_new}$)
เมื่อกระจายโหลดเหลือ $F_{new} = 16$ และมีค่า Base Net Delay ใหม่ $= 0.150\text{ ns}$:
$$t_{net\_new} = t_{net\_base\_new} + (k_{fo} \times F_{new}) = 0.150\text{ ns} + (0.025 \times 16)\text{ ns} = 0.150 + 0.400 = 0.550\text{ ns}$$

และเนื่องจากใช้เทคนิค Registered Look-Ahead ทำให้ไม่มีลอจิก $t_{lut}$ ขวางกั้น ($t_{lut\_new} = 0.000\text{ ns}$ ขับตรงจาก Flip-Flop):
$$T_{path\_new} = t_{co} + 0.000 + t_{net\_new} + t_{su} + T_{unc}$$
$$T_{path\_new} = 0.250 + 0.000 + 0.550 + 0.080 + 0.120 = 1.000\text{ ns}$$
Slack ใหม่:
$$WNS_{new} = T_{clk} - T_{path\_new} = 3.000\text{ ns} - 1.000\text{ ns} = +2.000\text{ ns}$$

##### ขั้นตอนที่ 3: คำนวณค่า Slack ที่เพิ่มขึ้น
$$\Delta WNS = WNS_{new} - WNS_{orig} = (+2.000\text{ ns}) - (+0.350\text{ ns}) = +1.650\text{ ns}$$
การทำ Register Replicating และ Look-Ahead ช่วยกอบกู้ Timing Margin ได้ถึง **$1.650\text{ ns}$** ทำให้ระบบมีเสถียรภาพสูงมาก

---

### คำถามที่ 3: สถาปัตยกรรม Hierarchical FSM Decomposition (การกระจาย FSM ขนาดใหญ่)

เมื่อสเตตแมชชีนมีขนาดใหญ่มากเกินกว่า $50$ สถานะ การรวมศูนย์ไว้ในโมดูลเดียวจะทำให้ตัวถอดรหัสมีขนาดใหญ่และกินเวลามาก วิธีแก้ที่ถูกต้องตามหลักวิศวกรรมสถาปัตยกรรมคือข้อใด?

---

#### ตัวเลือก:
A) เพิ่มความถี่ของสัญญาณนาฬิกาเป็นสองเท่าเพื่อเร่งการทำงาน  
B) แตกสเตตแมชชีนออกเป็น 2 ระดับ: **Top-level Macro-Sequencer** เพื่อควบคุมสเตจหลัก (เช่น Init, Config, Process, Shutdown) และส่งสัญญาณ Enable ไปคุม **Dedicated Micro-FSMs** ในแต่ละโหมด  
C) แปลงทุกสเตตให้เป็น Gray code ทั้งหมดและไม่ใส่เงื่อนไขดักจับ  
D) ย้ายการทำงานทั้งหมดไปรันบนซอฟต์แวร์ MicroBlaze Soft Core CPU แทน

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) แตกสเตตแมชชีนออกเป็น 2 ระดับ: Top-level Macro-Sequencer เพื่อควบคุมสเตจหลัก และส่งสัญญาณ Enable ไปคุม Dedicated Micro-FSMs ในแต่ละโหมด**

##### เหตุผลทางสถาปัตยกรรม VLSI:
การออกแบบสเตตแมชชีนขนาดใหญ่มากในลักษณะ Flat Monolithic FSM จะทำให้ขนาดของตาราง Karnaugh Map หรือตัวแปรบูลีนขยายตัวแบบ Exponential ($O(2^n)$) ซึ่งจะบังคับให้ EDA Tool ต้องสังเคราะห์ LUT ต่อเรียงกันเป็นรูปต้นไม้ลึกหลายชั้น (High Fan-In Cascaded Trees) ทำให้ความถี่สูงสุด $F_{max}$ ตกต่ำอย่างรุนแรง

การทำ **Hierarchical FSM Decomposition**:
1. ช่วยลดขนาดของ State Space ในแต่ละโมดูลให้อยู่ในระดับที่เล็ก ($4 - 8$ สถานะต่อโมดูล)
2. ทำให้ Next-State Logic ของแต่ละ Micro-FSM สามารถบรรจุลงใน 6-LUT ชั้นเดียว ($Depth = 1$)
3. สัญญาณเชื่อมต่อระหว่าง Macro และ Micro Controller จะกลายเป็นสัญญาณ Handshake ที่มีลักษณะเป็น Pipeline Stage สามารถคั่นด้วย Register ได้โดยไม่ละเมิด Iteration Bound ของการควบคุมย่อยภายใน
