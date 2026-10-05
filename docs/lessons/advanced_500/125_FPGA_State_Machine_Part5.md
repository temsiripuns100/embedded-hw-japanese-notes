# Lesson 125: FPGA State Machine - Part 5: FSM Verification & SystemVerilog Assertions (FSM検証とSVAアサーション設計)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 รากฐานทางคณิตศาสตร์ของการตรวจสอบยืนยันสเตตแมชชีน (Mathematical Foundations of FSM Verification)
ในการออกแบบระบบดิจิทัลที่มีความสำคัญต่อชีวิตมนุษย์และภารกิจวิกฤต (Safety-Critical / Mission-Critical Systems: เช่น มาตรฐานยานยนต์ ISO 26262 ASIL-D, มาตรฐานการบิน DO-254 DAL-A, หรือมาตรฐานเครื่องมือแพทย์ IEC 62304) การทดสอบสเตตแมชชีนด้วยแบบจำลองพฤติกรรมธรรมดา (Dynamic Directed Simulation) ไม่เพียงพออีกต่อไป เนื่องจากข้อจำกัดของการสร้างสัญญาณทดสอบ (Stimulus Space) ที่ไม่สามารถครอบคลุมทุกมุมอับได้

การตรวจสอบเชิงรูปแบบ (Formal Property Verification: FPV) และการตรวจสอบด้วยประพจน์ยืนยัน (Assertion-Based Verification: ABV) ถูกสร้างขึ้นบนพื้นฐานของ **ตรรกศาสตร์เชิงเวลาเชิงเส้น (Linear Temporal Logic: LTL)** และ **ตรรกศาสตร์ต้นไม้การคำนวณ (Computation Tree Logic: CTL)**

```
                  สเปซสถานะทั้งหมดและขอบเขตของการตรวจสอบยืนยัน
   +-------------------------------------------------------------------------+
   |  สเปซฮาร์ดแวร์ที่เป็นไปได้ทั้งหมด (Total Hardware State Space: 2^m)    |
   |                                                                         |
   |  +-------------------------------------+                                |
   |  | สเปซสถานะที่เข้าถึงได้ (Reachable)  |                                |
   |  |                                     |                                |
   |  |  [ ถูกต้องตามกฎ ]   [ Deadlock ]    |                                |
   |  |  (Legal States)     (Bug State)     |                                |
   |  |         ^                ^          |                                |
   |  +---------|----------------|----------+                                |
   |            |                |                                           |
   |    SVA Cover Property  SVA Safety Assert                                |
   |                                                                         |
   |  สเปซสถานะผิดกฎหมายที่เข้าถึงไม่ได้ในภาวะปกติ (Unreachable / Trap)      |
   |  (แต่ถูกกระตุ้นได้จากรังสีคอสมิก / EMI Surge / SEU Bit-Flip)            |
   |  -> ต้องดักจับด้วย $onehot assertion และ Safe State Hardware Recovery   |
   +-------------------------------------------------------------------------+
```

#### 1.1.1 คุณสมบัติด้านความปลอดภัย (Safety Properties)
นิยามทางคณิตศาสตร์คือ: *"สิ่งเลวร้ายจะต้องไม่มีวันเกิดขึ้น"* ($\mathbf{G}(\neg \text{Bad})$):
* FSM จะต้องไม่อยู่ในสถานะที่ไม่ถูกนิยาม (Illegal State)
* FSM จะต้องไม่มีวันเปลี่ยนสถานะไปยังสเตตที่ผิดกฎหมาย (Illegal Transition)
* ในเวลาเดียวกัน จะต้องไม่มีสัญญาณควบคุมสองตัวที่ขัดแย้งกันถูกเปิดใช้งานพร้อมกัน (Mutual Exclusion)

#### 1.1.2 คุณสมบัติด้านความต่อเนื่องของชีวิตระบบ (Liveness Properties)
นิยามทางคณิตศาสตร์คือ: *"สิ่งที่ดีจะต้องเกิดขึ้นในที่สุดอย่างแน่นอน"* ($\mathbf{G}(\text{Req} \rightarrow \mathbf{F}(\text{Ack}))$):
* FSM จะต้องไม่ติดหล่มอยู่ในสถานะใดสถานะหนึ่งตลอดกาล (No Deadlock / Livelock)
* เมื่อมีคำร้องขอเข้ามา ระบบจะต้องกลับสู่สถานะพร้อมทำงานภายในกรอบเวลาจำกัด ($T_{timeout}$)

---

### 1.2 โครงสร้างทางไวยากรณ์ของ SystemVerilog Assertions (SVA) สำหรับ FSM

SVA มีโครงสร้างทางคณิตศาสตร์ที่ทรงพลังในการดักจับความผิดปกติของ State Machine:

#### 1.2.1 ตัวดำเนินการ Implication (`|->` vs `|=>`)
* **Overlapping Implication (`|->`):** หากเงื่อนไขฝั่งซ้าย (Antecedent) เป็นจริง ณ ขอบสัญญาณนาฬิกาปัจจุบัน เงื่อนไขฝั่งขวา (Consequent) จะต้องเป็นจริง **ในขอบสัญญาณนาฬิกาเดียวกันทันที**
* **Non-overlapping Implication (`|=>` $\equiv$ `##1`):** หากเงื่อนไขฝั่งซ้ายเป็นจริง ณ ขอบปัจจุบัน เงื่อนไขฝั่งขวาจะต้องเป็นจริง **ในขอบสัญญาณนาฬิการอบถัดไป (Next Cycle)**

#### 1.2.2 การตรวจสอบความสมบูรณ์ของ One-Hot Encoding ด้วย System Functions
* `$onehot(expression)`: คืนค่าจริงเมื่อเวกเตอร์มีบิต 1 **เพียงตัวเดียวเท่านั้น** (ตรวจจับได้ทั้ง All-Zeros และ Multi-Hot)
* `$onehot0(expression)`: คืนค่าจริงเมื่อเวกเตอร์มีบิต 1 ไม่เกิน 1 ตัว (ยอมรับค่า 0 ทั้งหมดได้)
* `$isunknown(expression)`: คืนค่าจริงเมื่อมีบิตใดบิตหนึ่งหลุดเป็นค่า 'X' หรือ 'Z'

```systemverilog
// กฎเหล็ก: ตรวจสอบความถูกต้องของ One-Hot State Register ทุกขอบสัญญาณนาฬิกา
property p_valid_onehot_state;
    @(posedge clk) disable iff (!rst_n)
    $onehot(current_state);
endproperty
a_valid_onehot_state: assert property (p_valid_onehot_state)
    else $fatal(1, "[CRITICAL FSM FAULT] State vector corrupted: %b", current_state);
```

#### 1.2.3 การสร้างตาราง Transition Matrix Checker แบบเคร่งครัด
เพื่อป้องกันไม่ให้ FSM กระโดดข้ามสถานะอย่างผิดกฎหมาย:
```systemverilog
// ตรวจสอบว่าจาก ST_IDLE สามารถไปได้เฉพาะ ST_IDLE หรือ ST_RUN เท่านั้น
property p_legal_trans_from_idle;
    @(posedge clk) disable iff (!rst_n)
    (current_state == ST_IDLE) |=> (current_state inside {ST_IDLE, ST_RUN});
endproperty
a_legal_trans_idle: assert property (p_legal_trans_from_idle);
```

#### 1.2.4 การป้องกัน Deadlock ด้วย Bounded Liveness Property
```systemverilog
// ตรวจสอบว่าระบบต้องไม่ค้างในสถานะ BUSY เกินกว่า 1024 ไซเคิล
property p_fsm_no_deadlock;
    @(posedge clk) disable iff (!rst_n)
    (current_state == ST_BUSY) |-> strong(##[1:1024] (current_state == ST_DONE));
endproperty
a_no_deadlock: assert property (p_fsm_no_deadlock)
    else $error("[TIMEOUT FAULT] FSM deadlock in ST_BUSY detected!");
```

---

### 1.3 สถาปัตยกรรม Binding และการแยกโค้ดตรวจสอบ (Non-intrusive SVA Binding)
ตามมาตรฐาน DO-254 และวิศวกรรมระดับสูง โค้ดสำหรับตรวจสอบความปลอดภัย (Verification IP / SVA Checkers) จะต้อง **ไม่ถูกเขียนปะปนลงในโค้ด RTL ที่จะนำไปผลิตชิป (Synthesizable RTL)** เพื่อป้องกันไม่ให้เกิดความผิดพลาดจากการแก้ไขโค้ดโปรดักชัน

เราใช้คำสั่ง **`bind`** ใน SystemVerilog เพื่อเชื่อมต่อโมดูลตรวจสอบเข้ากับอินสแตนซ์ของวงจรฮาร์ดแวร์โดยอัตโนมัติ:

```
          สถาปัตยกรรม Non-Intrusive SVA Binding ใน SystemVerilog
   +---------------------------------------------------------------+
   | Production RTL Module (fsm_controller.sv)                     |
   | - Synthesizable Only                                          |
   | - สะอาด ปราศจาก Assertion โค้ดที่รกรุงรัง                    |
   |   [ Internal Signals: current_state, timeout_cnt, tx_en ]     |
   +-------------------------------+-------------------------------+
                                   ^
                                   | bind fsm_controller fsm_sva_checker u_sva (...)
   +-------------------------------+-------------------------------+
   | Dedicated SVA Checker Module (fsm_sva_checker.sv)             |
   | - รันใน Formal Verification (SymbiYosys / JasperGold)         |
   | - รันใน Dynamic Simulation Coverage Reporting                 |
   | - ไม่ถูกนำไปสังเคราะห์ลงซิลิคอนจริง                           |
   +---------------------------------------------------------------+
```

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Reusable Golden SVA Checker & Binding

```systemverilog
//=============================================================================
// Module: fsm_protocol_sva_checker.sv
// Description: Industrial-Grade SVA Checker for Mission-Critical FSM
// Standards: DO-254 / ISO 26262 ASIL-D Compliant Verification Module
//=============================================================================
`timescale 1ns / 1ps

module fsm_protocol_sva_checker #(
    parameter int TIMEOUT_LIMIT = 512
)(
    input logic       clk,
    input logic       rst_n,
    input logic [3:0] current_state,
    input logic [3:0] next_state,
    input logic       start_cmd,
    input logic       abort_cmd,
    input logic       done_pulse,
    input logic       tx_valid,
    input logic       tx_ready
);

    // นิยามสเตตตรงตาม RTL
    localparam logic [3:0] ST_RESET = 4'b0001;
    localparam logic [3:0] ST_IDLE  = 4'b0010;
    localparam logic [3:0] ST_BUSY  = 4'b0100;
    localparam logic [3:0] ST_ERROR = 4'b1000;

    //-------------------------------------------------------------------------
    // 1. Safety Assertions: One-Hot & Unknown State Detection
    //-------------------------------------------------------------------------
    // ตรวจสอบว่าบิตสถานะไม่มีค่า X/Z
    a_no_unknown_state: assert property (
        @(posedge clk) disable iff (!rst_n)
        !$isunknown(current_state)
    ) else $fatal(1, "[SVA FATAL] Current state contains X or Z: %b", current_state);

    // ตรวจสอบว่าเป็น One-Hot ถูกต้องเสมอ
    a_strict_onehot: assert property (
        @(posedge clk) disable iff (!rst_n)
        $onehot(current_state)
    ) else $fatal(1, "[SVA FATAL] One-Hot property violated! Multi-hot or All-zero: %b", current_state);

    //-------------------------------------------------------------------------
    // 2. Transition Correctness Assertions (State Transition Matrix)
    //-------------------------------------------------------------------------
    // จาก ST_RESET ต้องไป ST_IDLE เท่านั้น
    a_trans_from_reset: assert property (
        @(posedge clk) disable iff (!rst_n)
        (current_state == ST_RESET) |=> (current_state == ST_IDLE)
    ) else $error("[SVA ERROR] Illegal transition from ST_RESET");

    // จาก ST_IDLE: ถ้ามี start_cmd ต้องไป ST_BUSY, ถ้าไม่มีต้องอยู่ ST_IDLE
    a_trans_from_idle: assert property (
        @(posedge clk) disable iff (!rst_n)
        (current_state == ST_IDLE && start_cmd) |=> (current_state == ST_BUSY)
    ) else $error("[SVA ERROR] Failed to enter ST_BUSY upon start_cmd");

    // จาก ST_BUSY: ถ้ามี abort_cmd ต้องเข้าสู่ ST_ERROR ทันทีในรอบถัดไป
    a_trans_abort_prio: assert property (
        @(posedge clk) disable iff (!rst_n)
        (current_state == ST_BUSY && abort_cmd) |=> (current_state == ST_ERROR)
    ) else $error("[SVA ERROR] Abort command failed to force ST_ERROR");

    //-------------------------------------------------------------------------
    // 3. Handshake & Output Correctness
    //-------------------------------------------------------------------------
    // ห้ามส่ง tx_valid หากไม่ได้อยู่ในสถานะ ST_BUSY
    a_tx_only_in_busy: assert property (
        @(posedge clk) disable iff (!rst_n)
        tx_valid |-> (current_state == ST_BUSY)
    ) else $error("[SVA ERROR] tx_valid asserted outside ST_BUSY state!");

    // AXI4-Stream Rule: เมื่อ tx_valid ขึ้นแล้ว ต้องไม่เปลี่ยนข้อมูลจนกว่า tx_ready จะรับ
    a_valid_stability: assert property (
        @(posedge clk) disable iff (!rst_n)
        (tx_valid && !tx_ready) |=> tx_valid
    ) else $error("[SVA ERROR] Protocol Violation: tx_valid dropped before ready!");

    //-------------------------------------------------------------------------
    // 4. Liveness Assertions (Deadlock Freedom)
    //-------------------------------------------------------------------------
    a_busy_bounded_exit: assert property (
        @(posedge clk) disable iff (!rst_n)
        (current_state == ST_BUSY && !abort_cmd) |-> strong(##[1:TIMEOUT_LIMIT] (current_state inside {ST_IDLE, ST_ERROR}))
    ) else $error("[SVA TIMEOUT] FSM trapped in ST_BUSY beyond timeout limit!");

    //-------------------------------------------------------------------------
    // 5. Functional Coverage (Cover Properties for Sign-off Metrics)
    //-------------------------------------------------------------------------
    // ต้องครอบคลุมเส้นทาง Happy Path
    c_happy_path: cover property (
        @(posedge clk) disable iff (!rst_n)
        (current_state == ST_IDLE) ##1 (current_state == ST_BUSY) [*5:20] ##1 (current_state == ST_IDLE)
    );

    // ต้องครอบคลุมเส้นทาง Abort Path
    c_abort_path: cover property (
        @(posedge clk) disable iff (!rst_n)
        (current_state == ST_BUSY && abort_cmd) ##1 (current_state == ST_ERROR)
    );

endmodule
```

```systemverilog
//=============================================================================
// Bind File: fsm_bind_top.sv
// Description: Binds the SVA checker to production instance without editing RTL
//=============================================================================
module fsm_bind_top;
    bind fsm_engine fsm_protocol_sva_checker #(
        .TIMEOUT_LIMIT(512)
    ) u_fsm_sva_inst (
        .clk           (clk),
        .rst_n         (rst_n),
        .current_state (current_state),
        .next_state    (next_state),
        .start_cmd     (start_cmd),
        .abort_cmd     (abort_cmd),
        .done_pulse    (done_pulse),
        .tx_valid      (tx_valid),
        .tx_ready      (tx_ready)
    );
endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในเครื่องช่วยหายใจสำหรับห้องผ่าตัดฉุกเฉิน (Intensive Care Mechanical Ventilator) โมดูล FPGA ควบคุมวาล์วออกซิเจนและโซลินอยด์วาล์วแรงดันสูง มี FSM ขนาด 10 สถานะ ในขั้นตอนการทดสอบความเข้ากันได้ทางแม่เหล็กไฟฟ้า (EMC Transient Surge Testing ตามมาตรฐาน IEC 60601-1-2) มีการยิงสัญญาณพัลส์สัญญาณรบกวน $2\text{ kV}$ เข้าสายเมนบอร์ด

**ผลลัพธ์ที่ล้มเหลว:** วาล์วออกซิเจนค้างเปิดค้าง $100\%$ ทำให้แรงดันในท่อช่วยหายใจพุ่งเกินเกณฑ์วิกฤต (Barotrauma Hazard) เมื่อต่อโพรบตรวจสอบพบว่า สเตตแมชชีนค้างนิ่งสนิทและหยุดรับสัญญาณจากเซนเซอร์แรงดันทั้งหมด ทั้งที่ในโค้ด RTL มีการใส่บรรทัด `default: state <= ST_INIT;` ไว้อยู่แล้ว

```
                ลำดับการเกิดความล้มเหลวในเครื่องช่วยหายใจ
   EMC Transient Noise Spike 2kV เหนี่ยวนำเข้าพินชิป FPGA
                            |
                            v
   State Register เกิด Single Event Upset (SEU) พลิกบิตเป็นค่า 4'b1101 (State 13)
                            |
                            v
   โค้ดดักจับใน RTL:
   case (state)
       ST_0..ST_9: ...
       default: state <= ST_INIT;  <--- โค้ดนี้ถูก EDA Tool ลบออกไปแล้วในขั้นตอนคอมไพล์!
   endcase
                            |
                            v
   ไม่มีวงจรฮาร์ดแวร์พาออกจากสถานะ 13 -> วงจรหลุดเข้า Trap State ตลอดกาล!
   วาล์วเปิดค้าง -> แรงดันก๊าซในปอดคนไข้เกินพิกัดอันตราย!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมเครื่องช่วยหายใจถึงปล่อยแรงดันก๊าซเกินพิกัดอันตราย?**
   * *ตอบ:* วาล์วควบคุมแรงดันเปิดค้าง และไม่ตอบสนองต่อสัญญาณตัดฉุกเฉินจากเซนเซอร์
2. **ทำไมวาล์วควบคุมถึงไม่ยอมตัดการทำงาน?**
   * *ตอบ:* สเตตแมชชีนควบคุมวาล์วบน FPGA ค้างนิ่งสนิทในสถานะผิดปกติ
3. **ทำไมสเตตแมชชีนถึงหลุดเข้าไปค้างในสถานะผิดปกติได้?**
   * *ตอบ:* บิตของ State Register ถูกคลื่นรบกวน EMI พลิกค่าจากสถานะปกติไปยังสถานะที่ไม่มีการใช้งาน (Unused State `4'b1101`)
4. **ทำไมบล็อก `default` ในโค้ด RTL ถึงไม่ดึงสถานะกลับมาที่ `ST_INIT`?**
   * *ตอบ:* โปรแกรมสังเคราะห์วงจร (Synthesis Tool) ตีความว่าสถานะที่ไม่ได้ประกาศในตารางเป็นสถานะ "Don't Care" จึงทำการตัด (Prune) ลอจิกของบล็อก `default` ทิ้งเพื่อประหยัดพื้นที่ชิป
5. **ทำไมทีมพัฒนาจึงไม่พบปัญหานี้ตั้งแต่ขั้นตอนการทดสอบ (Verification)?**
   * *ตอบ:* ทีมทดสอบรันเฉพาะ Dynamic Simulation แบบปกติ ซึ่งป้อนเฉพาะสัญญาณอินพุตที่เป็นไปตามสเปก โดยไม่ได้เขียน **SVA Assertions ดักจับ Illegal State** และไม่ได้ทำ **Fault Injection Testing** เพื่อจำลองกรณีเกิด Bit-Flip!

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของเครื่องช่วยหายใจ
   
   กระบวนการตรวจสอบ (Verification Process)       เครื่องมือและการคอมไพล์ (EDA Synthesis)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ขาดการเขียน    ขาดการทำ                      EDA Tool มอง   ไม่ได้ระบุ
   SVA Assertions Fault Injection               Unused State   fsm_safe_state
   ตรวจ Illegal  เพื่อทดสอบบิตฟลิป              เป็น Don't Care แอตทริบิวต์
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> เครื่องช่วยหายใจค้าง
                                                                |     จาก Unhandled Trap
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   สัญญาณ EMI     การทดสอบ                      เข้าใจผิดว่า    ขาดกระบวนการ
   รุนแรงระดับ     ตามสเปกทั่วไป                 default ใน RTL Formal Proof
   2kV Transient  ไม่กระตุ้น Illegal             จะกลายเป็นเกต  ของวงจร FSM
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   สภาพแวดล้อมหน้างาน (EMC Transient)            ความรู้ทางเทคนิค (Engineering Mindset)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ฝัง SVA Checker ผ่าน Bind Directive เสมอ
ในสภาพแวดล้อม Simulation และ Formal Verification ต้องคอมไพล์ไฟล์ Bind ที่ผูกเข้ากับ State Register ทุกตัวของระบบ:
```systemverilog
bind my_fsm fsm_protocol_sva_checker u_sva_inst (.*);
```

#### ขั้นตอนที่ 2: รันการทดสอบฉีดข้อผิดพลาด (Fault Injection Simulation)
เขียน Task ใน Testbench เพื่อบังคับเปลี่ยนบิตสถานะให้เป็นค่า Illegal State ชั่วขณะผ่านคำสั่ง `force` แล้วตรวจสอบว่าวงจรดีดตัวกลับสู่ Reset State ภายใน 1 ไซเคิลหรือไม่:
```systemverilog
initial begin
    #1000;
    @(posedge clk);
    // ฉีด Bit-Flip ปลอมเข้าไปใน State Register
    force u_dut.current_state = 4'b1101;
    @(posedge clk);
    release u_dut.current_state;
    // ยืนยันว่าฮาร์ดแวร์ดีดกลับมา ST_RESET ทันที
    assert (u_dut.current_state == ST_RESET)
        else $fatal(1, "[HARDWARE TRAP FAILED] System remained in illegal state!");
end
```

#### ขั้นตอนที่ 3: บังคับ Attribute ป้องกันการ Prune ในขั้นตอน Synthesis
ต้องใส่คำสั่ง:
```verilog
(* fsm_encoding = "one_hot" *)
(* fsm_safe_state = "reset_state" *)
```
เพื่อสั่งให้ EDA Tool สังเคราะห์วงจรดักจับสเตตหลุดลงใน Netlist ฮาร์ดแวร์จริงเสมอ

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| アサーション検証 | あさーしょんけんしょう | Asaashon Kenshou | Assertion-Based Verification (ABV) |
| 形式検証 | けいしきけんしょう | Keishiki Kenshou | Formal Verification (การตรวจสอบเชิงรูปแบบ) |
| 到達不能状態 | とうたつふのうじょうたい | Toutatsu Funou Joutai | Unreachable State (สถานะที่เข้าไม่ถึงในภาวะปกติ) |
| デッドロック | でっどろっく | Deddorokku | Deadlock (สภาวะติดหล่มไม่ขยับ) |
| 状態網羅率 | じょうたいもうらりつ | Joutai Mouraritsu | State Coverage (ความครอบคลุมของสถานะ) |
| 遷移網羅率 | せんいもうらりつ | Sen-i Mouraritsu | Transition Coverage (ความครอบคลุมการเปลี่ยนสถานะ) |
| バインド構文 | ばいんどこうぶん | Baindo Koubun | Bind Construct (คำสั่งผูกโมดูลตรวจสอบ) |
| フォールト注入 | ふぉーるとちゅうにゅう | Fooruto Chuunyuu | Fault Injection (การฉีดข้อผิดพลาดทดสอบ) |
| 安全性特性 | あんぜんせいとくせい | Anzensei Tokusei | Safety Property (คุณสมบัติความปลอดภัย) |
| 生存性特性 | せいぞんせいとくせい | Seizonsei Tokusei | Liveness Property (คุณสมบัติความมีชีวิตของระบบ) |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** การประชุมตรวจสอบความปลอดภัยของเครื่องมือแพทย์ (Medical Device Safety Audit / ISO 13485)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** โอกาวะ ซัง (Ogawa-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** ชิมิซุ คุง (Shimizu-kun)

---

**小川技師 (Ogawa):**  
「清水君、この人工呼吸器バルブ制御 FSM の検証レポートを拝見したが、カバレッジ（Coverage）が機能網羅率 100% となっているね。しかしテストベンチを見ると、正常系のパケットシーケンスしか流していないようだ。不正状態（Illegal State）からの復帰アサーションや、IEC 60601-1-2 サージノイズ耐性を想定したフォールト注入試験（Fault Injection）が全く含まれていないが、これで IEC 62304 クラス C の承認が通ると思っているのかね？」  
*(Shimizu-kun, kono jinkou kokyuuki barubu seigyo FSM no kenshou repooto wo haiken shita ga, kabarejji (Coverage) ga kinou mouraritsu 100% to natte iru ne. Shikashi tesutobenchi wo miru to, seijoukei no paketto shiikensu shika nagashite inai you da. Fusei joutai (Illegal State) kara no fukki asaashon ya, IEC 60601-1-2 saaji noizu taisei wo soutei shita fooruto chuunyuu shiken (Fault Injection) ga mattaku fukumarete inai ga, kore de IEC 62304 Kurasu C no shounin ga tooru to omotte iru no kane?)*  
**ความหมาย:** คุณชิมิซุ ผมดูรายงานการตรวจสอบ FSM ควบคุมวาล์วเครื่องช่วยหายใจตัวนี้แล้ว เห็นรายงานว่า Coverage ฟังก์ชันครบ 100% นะ แต่พอดูใน Testbench กลับส่งเฉพาะ Sequence กรณีปกติ (Happy Path) เท่านั้น ไม่เห็นมี Assertion ดักจับการฟื้นฟูจากสเตตผิดกฎหมาย (Illegal State) หรือการทดสอบฉีดข้อผิดพลาด (Fault Injection) เพื่อรับมือกับสัญญาณรบกวนตามมาตรฐาน IEC 60601-1-2 เลย คิดว่าทำแค่นี้จะผ่านการรับรองความปลอดภัย IEC 62304 Class C ได้หรือครับ?

---

**清水技師 (Shimizu):**  
「はい、小川さん。RTL の `case` 文末尾に `default: state <= ST_RESET;` を記載してありますので、万が一の未定義状態にも確実に対応できていると判断しておりました。アサーションを追加するとシミュレーション時間が大幅に増加するため、省略しておりました。」  
*(Hai, Ogawa-san. RTL no `case` bun matsubi ni `default: state <= ST_RESET;` wo kisai shite arimasu node, man-ga-ichi no miteigi joutai ni mo kakujitsu ni taiou dekite iru to handan shite orimashita. Asaashon wo tsuika suru to shimyureeshon jikan ga oohaba ni zouka suru tame, shouryaku shite orimashita.)*  
**ความหมาย:** ครับคุณโอกาวะ ที่ท้ายบล็อก `case` ใน RTL ผมใส่ `default: state <= ST_RESET;` ดักไว้แล้ว จึงมั่นใจว่าสามารถรับมือกับสเตตที่ไม่มีนิยามได้แน่นอนครับ และเนื่องจากการใส่ Assertion มันทำให้เวลาจำลอง Simulation นานขึ้นมาก ผมจึงละเว้นไว้ครับ

---

**小川技師 (Ogawa):**  
「現場の実態を何も分かっていないな！論理合成ツールは最適化の過程で、未定義状態への遷移を『発生しない Don't Care』とみなして、その `default` 論理をごっそり削除（Prune）してしまうんだ！実機にノイズが乗ってビット反転が起きた瞬間、FSM はブラックホールに落ちて二度と戻ってこない。シミュレーション時間の短縮などを理由に安全確認を怠ることは許されない！直ちに `bind` 構文を用いて独立した SVA チェッカーを接続し、形式検証（Formal Verification）で全不正状態からの 1 サイクル復帰を数学的に証明しなさい！」  
*(Genba no jittai wo nanimo wakatte inai na! Ronri gousei tsuuru wa saitekkika no katei de, miteigi joutai e no sen-i wo "hassei shinai Don't Care" to minashite, sono `default` ronri wo gossori sakujo (Prune) shite shimaunda! Jikki ni noizu ga notte bitto hanten ga okita shunkan, FSM wa burakku hooru ni ochite nidoto modotte konai. Shimyureeshon jikan no tanshuku nado wo riyuu ni anzen kakunin wo okotaru koto wa yurusarenai! Tadachini `bind` koubun wo mochiite dokuritsu shita SVA chekkaa wo setsuzoku shi, keishiki kenshou (Formal Verification) de zen-fusei joutai kara no 1-saikuru fukki wo suugakuteki ni shoumei shinasai!)*  
**ความหมาย:** ไม่เข้าใจความเป็นจริงหน้างานเลยสักนิด! ในขั้นตอนสังเคราะห์วงจร โปรแกรม EDA มันถือว่าการกระโดดไปสเตตที่ไม่มีนิยามคือ "Don't Care ที่ไม่มีทางเกิดขึ้น" แล้วมันก็แอบตัดลอจิก `default` นั้นทิ้งไปหมดเกลี้ยง! พอชิปจริงโดนสัญญาณรบกวนจนบิตฟลิป FSM จะหลุดเข้าหลุมดำแล้วไม่มีวันกลับออกมาได้ การเอาเรื่องเวลาซิมูเลชันมาอ้างเพื่อละเลยความปลอดภัยเป็นสิ่งที่ยอมรับไม่ได้เด็ดขาด! จงรีบใช้คำสั่ง `bind` ผูก SVA Checker ที่แยกเป็นเอกเทศเข้าไป และใช้ Formal Verification พิสูจน์ทางคณิตศาสตร์ว่าวงจรสามารถดีดตัวกลับจากทุก Illegal State ได้ภายใน 1 ไซเคิลเดี๋ยวนี้!

---

**清水技師 (Shimizu):**  
「人命に関わる医療機器において、合成ツールの最適化リスクと検証の甘さを痛感いたしました。直ちに `bind` による SVA チェッカーを作成し、SymbiYosys による形式検証とフォールト注入テストを実行して安全性を完全証明いたします！」  
*(Jinmei ni kakawaru iryou kiki ni oite, gousei tsuuru no saitekkika risuku to kenshou no amasa wo tsuukan itashimashita. Tadachini `bind` ni yoru SVA chekkaa wo sakusei shi, SymbiYosys ni yoru keishiki kenshou to fooruto chuunyuu tesuto wo jikkou shite anzensei wo kanzen shoumei itashimasu!)*  
**ความหมาย:** ในอุปกรณ์การแพทย์ที่มีผลต่อชีวิตมนุษย์ ผมตระหนักถึงความหละหลวมของตัวเองและความเสี่ยงจากการ Optimize ของคอมไพเลอร์แล้วครับ ผมจะรีบสร้าง SVA Checker ด้วย `bind` แล้วนำไปรัน Formal Verification ด้วย SymbiYosys ร่วมกับการฉีด Fault Injection เพื่อพิสูจน์ความปลอดภัยอย่างสมบูรณ์แบบทันทีครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณ State Space และความเสี่ยงต่อ Single Event Upset (SEU)

ในสถาปัตยกรรมชิป FPGA สำหรับดาวเทียมสื่อสารวงโคจรต่ำ (Low Earth Orbit: LEO) มีระบบควบคุมย่อยที่ประกอบด้วย 3 สเตตแมชชีนทำงานร่วมกัน (Cooperating Interacting FSMs):
* **FSM_A (Header Parser):** มี $N_A = 8$ สถานะ เข้ารหัสแบบ **Binary** ใช้ Flip-Flop $3$ ตัว ($m_A = 3$)
* **FSM_B (Cipher Engine):** มี $N_B = 6$ สถานะ เข้ารหัสแบบ **One-Hot** ใช้ Flip-Flop $6$ ตัว ($m_B = 6$)
* **FSM_C (DMA Controller):** มี $N_C = 10$ สถานะ เข้ารหัสแบบ **Binary** ใช้ Flip-Flop $4$ ตัว ($m_C = 4$)

กำหนดให้:
1. จำนวนสถานะที่เป็นไปได้ทั้งหมดในฮาร์ดแวร์รีจิสเตอร์ (Total Physical Hardware State Space) คือ $2^{(m_A + m_B + m_C)}$
2. จำนวนสถานะที่ถูกกฎหมายในการทำงานจริง (Total Valid Functional State Space) คือ $N_A \times N_B \times N_C$

จงคำนวณหา:
1. สัดส่วนร้อยละของสถานะที่ถูกกฎหมายเทียบกับสเปซฮาร์ดแวร์ทั้งหมด
2. หากอนุภาครังสีคอสมิกชนโดน Flip-Flop ตัวใดตัวหนึ่งแบบสุ่มจนเกิด Single Bit Flip จงคำนวณความน่าจะเป็นทางสถิติ ($P_{trap}$) ที่ระบบจะกระโดดเข้าไปติดอยู่ใน **Illegal State ของ FSM_B (Cipher Engine)** ซึ่งเป็น One-Hot โดยตรง?

---

#### ตัวเลือก:
A) สัดส่วนสถานะถูกกฎหมาย: $5.86\%$, $P_{trap, B} = 83.3\%$  
B) สัดส่วนสถานะถูกกฎหมาย: $11.72\%$, $P_{trap, B} = 100.0\%$  
C) สัดส่วนสถานะถูกกฎหมาย: $5.86\%$, $P_{trap, B} = 100.0\%$  
D) สัดส่วนสถานะถูกกฎหมาย: $2.44\%$, $P_{trap, B} = 66.7\%$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: C) สัดส่วนสถานะถูกกฎหมาย: $5.86\%$, $P_{trap, B} = 100.0\%$**

##### ขั้นตอนที่ 1: คำนวณขนาดของ State Space รวม
จำนวน Flip-Flop รวมทั้งหมดในระบบ:
$$M_{total} = m_A + m_B + m_C = 3 + 6 + 4 = 13 \text{ Flip-Flops}$$
ขนาดของสเปซทางฮาร์ดแวร์ทั้งหมด:
$$S_{hardware} = 2^{13} = 8,192 \text{ สถานะ}$$

จำนวนสถานะที่ถูกกฎหมายตามตรรกะการทำงาน (Valid Functional States):
$$S_{valid} = N_A \times N_B \times N_C = 8 \times 6 \times 10 = 480 \text{ สถานะ}$$

คำนวณสัดส่วนร้อยละของสถานะถูกกฎหมาย:
$$\% \text{Valid} = \frac{S_{valid}}{S_{hardware}} \times 100\% = \frac{480}{8,192} \times 100\% \approx 5.859\% \approx 5.86\%$$
นั่นหมายความว่า มีสเปซสถานะที่เป็น **Illegal States มากถึง $94.14\%$** ของสเปซทั้งหมด!

##### ขั้นตอนที่ 2: วิเคราะห์ผลกระทบของ Single Bit Flip บน One-Hot FSM_B
ในสเตตแมชชีน One-Hot FSM_B ขนาด 6 บิต:
ในสภาวะปกติ เวกเตอร์สถานะจะมีบิตที่เป็น '1' เพียงตัวเดียวเสมอ (Hamming Weight $W = 1$) เช่น `000010`
หากเกิด **Single Bit Flip** จากอนุภาครังสีคอสมิก:
* **กรณีที่ 1 (บิตที่ถูกชนคือบิตที่เป็น '1'):** บิต 1 จะพลิกกลายเป็น 0 ทำให้เวกเตอร์กลายเป็น `000000` (All Zeros) ซึ่งมี Hamming Weight $W = 0 \rightarrow$ **เป็น Illegal State ทันที!**
* **กรณีที่ 2 (บิตที่ถูกชนคือบิตใดบิตหนึ่งใน 5 บิตที่เป็น '0'):** บิต 0 นั้นจะพลิกกลายเป็น 1 ทำให้เวกเตอร์กลายเป็นแบบมีบิต 1 สองตัว (2-Hot) เช่น `000110` ซึ่งมี Hamming Weight $W = 2 \rightarrow$ **เป็น Illegal State ทันทีเช่นกัน!**

เนื่องจากไม่มีกรณีอื่นที่เป็นไปได้:
$$P_{trap, B} = 100.0\%$$
ทุกครั้งที่เกิด Single Event Upset บน One-Hot FSM ระบบจะหลุดเข้าไปใน Illegal Trap State เสมอ $100\%$ โดยไม่มีข้อยกเว้น! นี่คือเหตุผลทางคณิตศาสตร์ที่วิศวกรต้องบังคับใส่ Safe State Logic และ SVA Assertion ในทุกระบบที่ใช้ One-Hot

---

### คำถามที่ 2: การประเมินหน้าต่างเวลาและผลลัพธ์ของ SystemVerilog Assertion (SVA Timing Sequence)

พิจารณาประพจน์ยืนยัน SVA ต่อไปนี้:

```systemverilog
property p_burst_handshake;
    @(posedge clk) disable iff (!rst_n)
    req ##[2:4] ack |-> ##1 valid [*3] ##1 done;
endproperty
```

กำหนดให้ไทม์มิ่งของสัญญาณที่เกิดขึ้นจริงในแบบจำลอง (Simulation Trace) เป็นดังนี้:
* ที่รอบสัญญาณนาฬิกา $T_0$: `req = 1`
* ที่รอบ $T_1$: `req = 0, ack = 0`
* ที่รอบ $T_2$: `ack = 0`
* ที่รอบ $T_3$: `ack = 1`
* ที่รอบ $T_4$: `valid = 1`
* ที่รอบ $T_5$: `valid = 1`
* ที่รอบ $T_6$: `valid = 1`
* ที่รอบ $T_7$: `valid = 0, done = 1`

จงวิเคราะห์ว่า ประพจน์ยืนยันนี้มีผลลัพธ์เป็นอย่างไร (Pass หรือ Fail) และสัญญาณ `done` ถูกประเมินค่าที่รอบสัญญาณนาฬิกาที่เท่าใด?

---

#### ตัวเลือก:
A) Assertion ล้มเหลว (Fail) ที่รอบ $T_6$ เนื่องจาก `valid` ค้างนานเกินไป  
B) Assertion ประสบความสำเร็จ (Pass) โดย `done` ถูกตรวจสอบและผ่านที่รอบ $T_7$  
C) Assertion ไม่ถูกกระตุ้น (Vacuously Pass) เนื่องจาก `ack` ไม่ตรงรอบ $T_2$  
D) Assertion ล้มเหลว (Fail) ที่รอบ $T_7$ เนื่องจาก `done` ต้องขึ้นพร้อมกับ `valid` ตัวสุดท้าย

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) Assertion ประสบความสำเร็จ (Pass) โดย `done` ถูกตรวจสอบและผ่านที่รอบ $T_7$**

##### ขั้นตอนการประเมินทีละรอบสัญญาณนาฬิกา (Cycle-by-Cycle Evaluation):
1. **รอบ $T_0$:** สัญญาณ `req = 1` เริ่มต้นกระตุ้นเงื่อนไข Antecedent (`req`)
2. **ช่วงหน่วง `##[2:4] ack`:** กำหนดว่าสัญญาณ `ack` จะต้องเป็น 1 ในช่วงระหว่าง 2 ถึง 4 รอบหลังจาก $T_0$:
   * $T_0 + 2 = T_2$: `ack = 0` (ยังอยู่ในช่วง)
   * $T_0 + 3 = T_3$: `ack = 1` $\rightarrow$ เงื่อนไข Antecedent เป็นจริงสมบูรณ์ที่รอบ $T_3$!
3. **การประเมิน Consequent (`|-> ##1 valid [*3] ##1 done`):**
   * เริ่มนับจากรอบ $T_3$ ด้วยตัวดำเนินการ `|-> ##1`: ขยับไป 1 รอบข้างหน้า คือรอบ **$T_4$**
   * ที่รอบ $T_4$: ต้องมี `valid = 1` (ครั้งที่ 1) $\rightarrow$ ใน Trace มี `valid = 1` (ผ่าน)
   * ที่รอบ $T_5$: ต้องมี `valid = 1` (ครั้งที่ 2) $\rightarrow$ ใน Trace มี `valid = 1` (ผ่าน)
   * ที่รอบ $T_6$: ต้องมี `valid = 1` (ครั้งที่ 3) $\rightarrow$ ใน Trace มี `valid = 1` ครบ 3 ไซเคิลตามเงื่อนไข `valid [*3]` (ผ่าน)
   * จากนั้นมีเงื่อนไข `##1 done`: ต้องมีสัญญาณ `done = 1` ในรอบถัดไป ($T_6 + 1 = T_7$)
   * ที่รอบ $T_7$: ตรวจสอบพบ `done = 1` (ผ่านสมบูรณ์!)

ดังนั้น Sequence ทั้งหมดจึงสอดคล้องกับพฤติกรรมใน Trace ทุกประการ และให้ผลลัพธ์การประเมินเป็น **Assertion Pass** ที่รอบ **$T_7$**

---

### คำถามที่ 3: การคำนวณอัตราความล้มเหลว FIT Rate ในอวกาศ (Cosmic Neutron Reliability Calculation)

ในภารกิจยานอวกาศโคจรระดับต่ำ (LEO Orbit) ชิป FPGA SRAM-based มีความเสี่ยงต่ออนุภาคนิวตรอนพลังงานสูง ($E > 10\text{ MeV}$) 
* ฟลักซ์ของอนุภาคนิวตรอนเฉลี่ย: $\Phi = 4.0 \times 10^3\text{ particles/(cm}^2\cdot\text{s)}$
* พื้นที่หน้าตัดประสิทธิผลของการเกิด Single Event Upset ต่อ Flip-Flop (SEU Cross-Section): $\sigma_{SEU} = 2.5 \times 10^{-14}\text{ cm}^2\text{/bit}$
* วงจรควบคุม FSM ใช้ Flip-Flop ทั้งหมด $m = 16$ ตัว ทำงานต่อเนื่อง $24/7$
* กำหนดหน่วย FIT (Failures In Time) คือ จำนวนความล้มเหลวใน $10^9$ ชั่วโมงการทำงาน ($1\text{ FIT} = 10^{-9}\text{ failures/hour}$)

หากเปรียบเทียบระหว่าง:
1. **วงจรแบบไม่มี Safe State (Unhardened FSM):** หากเกิด Bit-Flip เพียง 1 บิต ระบบจะค้างและถือเป็นความล้มเหลวระดับ Fatal ทันที ($P_{fail} = 1.0$)
2. **วงจรแบบเข้ารหัสป้องกัน (Triple Modular Redundancy / Safe FSM):** สามารถแก้ไขบิตผิดพลาดได้ 1 บิต และจะล้มเหลวก็ต่อเมื่อเกิดบิตพลิกพร้อมกัน 2 บิตในรอบเดียวกัน โดยมีปัจจัยลดทอนความเสี่ยง (Fault Mitigation Factor): $K_{mitigate} = 1.2 \times 10^{-5}$

จงคำนวณหาค่าอัตราความล้มเหลวในหน่วย **FIT Rate** ของวงจรแบบ Unhardened FSM?

---

#### ตัวเลือก:
A) $5,760\text{ FIT}$  
B) $57,600\text{ FIT}$  
C) $14,400\text{ FIT}$  
D) $1,440\text{ FIT}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) $5,760\text{ FIT}$**

##### ขั้นตอนที่ 1: คำนวณอัตราการเกิด Bit-Flip ต่อบิตต่อวินาที ($\lambda_{bit}$)
สมการคำนวณอัตราการเกิดข้อผิดพลาดจากฟลักซ์รังสี:
$$\lambda_{bit} = \Phi \times \sigma_{SEU}$$
แทนค่า:
$$\lambda_{bit} = (4.0 \times 10^3\text{ cm}^{-2}\cdot\text{s}^{-1}) \times (2.5 \times 10^{-14}\text{ cm}^2) = 1.0 \times 10^{-10}\text{ flips/(bit}\cdot\text{s)}$$

##### ขั้นตอนที่ 2: คำนวณอัตราการเกิดข้อผิดพลาดรวมของทั้งวงจร FSM 16 บิตต่อวินาที ($\lambda_{FSM, sec}$)
$$\lambda_{FSM, sec} = m \times \lambda_{bit} = 16 \times (1.0 \times 10^{-10}) = 1.6 \times 10^{-9}\text{ flips/s}$$

##### ขั้นตอนที่ 3: แปลงอัตราความล้มเหลวเป็นหน่วยต่อชั่วโมง ($\lambda_{FSM, hour}$)
ใน 1 ชั่วโมง มี 3,600 วินาที:
$$\lambda_{FSM, hour} = \lambda_{FSM, sec} \times 3,600\text{ s/hour}$$
$$\lambda_{FSM, hour} = (1.6 \times 10^{-9}) \times 3,600 = 5.76 \times 10^{-6}\text{ failures/hour}$$

##### ขั้นตอนที่ 4: แปลงเป็นหน่วย FIT (Failures In $10^9$ Hours)
$$\text{FIT Rate} = \lambda_{FSM, hour} \times 10^9$$
$$\text{FIT Rate} = (5.76 \times 10^{-6}) \times 10^9 = 5,760\text{ FIT}$$

##### ความหมายทางวิศวกรรม:
ค่า $5,760\text{ FIT}$ หมายความว่า หากส่งดาวเทียมจำนวน 100 ดวงขึ้นไป แต่ละดวงจะเกิดสภาวะ FSM ค้างเฉลี่ยทุกๆ **$1.73 \times 10^5$ ชั่วโมง (ประมาณทุกๆ 20 ปีต่อดวง)** หรือในฝูงดาวเทียม 100 ดวง จะพบดาวเทียมเกิด Deadlock เฉลี่ยปีละหลายครั้ง!
เมื่อใช้วงจร Hardened Safe FSM อัตรา FIT จะลดลงเหลือเพียง:
$$\text{FIT}_{hardened} = 5,760 \times (1.2 \times 10^{-5}) \approx 0.069\text{ FIT}$$
ซึ่งรับประกันความปลอดภัยตลอดอายุการใช้งานของภารกิจอวกาศได้อย่างสมบูรณ์แบบ
