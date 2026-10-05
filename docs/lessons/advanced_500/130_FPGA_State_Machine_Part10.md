# Lesson 130: FPGA State Machine Part 10 - Timing Closure & Retiming (タイミングクロージャとリタイミング: Critical Path Unrolling, Multicycle Path & Register Balancing)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ทฤษฎีบทการปรับสมดุลรีจิสเตอร์ของไลเซอร์สัน-แซกซ์ (Leiserson-Saxe Retiming Theorem)
ในการปรับแต่งความเร็วของวงจรดิจิทัลระดับสูง เทคนิคการทำ **Register Retiming** คือกระบวนการทางคณิตศาสตร์ในการย้ายตำแหน่งของ Flip-Flops ข้ามผ่านเกตตรรกะคอมบิเนชัน (Combinational Gates) โดยไม่เปลี่ยนแปลงพฤติกรรมการทำงานภายนอก (Latency and Functional Equivalence) ของวงจร

แบบจำลองของวงจรลำดับสามารถแทนได้ด้วยกราฟระบุทิศทาง $G = (V, E, d, w)$:
* จุดยอด $v \in V$ แทน เกตหรือบล็อกลอจิก โดยมีค่าน้ำหนักความหน่วงเวลา $d(v) \ge 0$
* เส้นเชื่อม $e = (u, v) \in E$ แทน การเชื่อมต่อสายสัญญาณ โดยมีค่าน้ำหนัก $w(e)$ แทนจำนวนของ Flip-Flops บนสายนั้น

```
                 ทฤษฎีบทการย้าย Register (Retiming Mechanism)
   
   [ ก่อนทำ Retiming: เส้นทางช่วงแรกยาวเกินไป -> ติด Setup Slack Violation ]
   +----+                                                              +----+
   | FF |--->[ Logic A: 2.8 ns ]--->[ Logic B: 2.6 ns ]--------------->| FF |
   +----+                                                              +----+
   <------------------- Total Delay = 5.4 ns (T_clk = 3.3 ns -> Slack ติดลบ!) ---->
   
   [ หลังทำ Retiming: แทรก/ย้าย Flip-Flop ข้ามมาคั่นกลางอย่างสมดุล ]
   +----+                                    +----+                    +----+
   | FF |--->[ Logic A: 2.8 ns ]------------>| FF |--->[ Logic B: 2.6 ns ]->| FF |
   +----+                                    +----+                    +----+
   <------- Delay = 2.8 ns (Slack ผ่าน) ------> <---- Delay = 2.6 ns (Slack ผ่าน) ---->
```

#### 1.1.1 เงื่อนไขทางคณิตศาสตร์สำหรับการ Retiming ที่ถูกต้อง (Retiming Invariants)
ฟังก์ชันการทำ Retiming ถูกกำหนดโดยเวกเตอร์จำนวนเต็ม $r: V \rightarrow \mathbb{Z}$ โดยที่ $r(v)$ คือจำนวนของรีจิสเตอร์ที่ถูกเคลื่อนย้ายข้ามจุดยอด $v$ จากฝั่งเอาต์พุตไปยังฝั่งอินพุต:

1. **เงื่อนไขความถูกต้องของน้ำหนัก (Weight Non-negativity):**
   $$w_r(e) = w(e) + r(v) - r(u) \ge 0 \quad \forall e = (u, v) \in E$$
2. **คาบเวลาสัญญาณนาฬิกาต่ำสุดใหม่ ($c$):**
   $$T_{clk\_min} = \max_{p: w_r(p) = 0} d(p)$$
   โดยที่ $d(p)$ คือผลรวมความหน่วงเวลาบนเส้นทางคอมบิเนชันใดๆ ที่ไม่มีรีจิสเตอร์กั้น ($w_r(p) = 0$)

---

### 1.2 กับดักอันตรายสูงสุด: Retiming on FSM Reset State (กับดักสเตตรีเซ็ต)
แม้ว่าการเปิดคำสั่ง `-retiming` ใน Vivado หรือ Quartus จะช่วยแก้ปัญหา Setup Time Violation ได้อย่างมหัศจรรย์ **แต่มันแฝงอันตรายระดับหายนะสำหรับ State Machine!**

```
              กับดักการบิดเบือนสเตตรีเซ็ตจากการทำ Automatic Retiming
   
   [ RTL ดั้งเดิม: รีเซ็ตแล้วได้ State = 3'b001 (ST_IDLE) ชัดเจน ]
                  +--------------------------------+
                  |                                |
   Next Logic --->+--->[ LUT Decoder ]---> D     Q +---> Current State (3'b001)
                                           |FF_RST |
                                           +-------+
   
   [ หลัง EDA Tool ทำ Retiming: ย้าย FF ข้ามไปอยู่หน้า LUT Decoder ]
                  +--------------------------------+
                  |                                |
   Next Logic --->+---> D     Q --->[ LUT Decoder ]+---> Scrambled Output!
                        |FF_RST |
                        +-------+
```

เมื่อ Flip-Flop ถูกย้ายข้าม LUT:
1. ค่าเริ่มต้นของรีจิสเตอร์หลังถูกรีเซ็ต (Reset Initialization Value) จะต้องถูกคำนวณย้อนกลับ (Backward Computation) ผ่านฟังก์ชันบูลีนของ LUT
2. หากฟังก์ชันลอจิกเป็นแบบหลายต่อหนึ่ง (Non-bijective Mapping) หรือมีเงื่อนไขอะซิงโครนัสรีเซ็ต (Asynchronous Reset Pin) เครื่องมือสังเคราะห์วงจรจะไม่สามารถกำหนดค่า Reset State Vector ที่สอดคล้องกับพฤติกรรมเดิมได้ $100\%$!
3. ผลลัพธ์: **เมื่อเปิดเครื่องขึ้นมา สเตตแมชชีนจะตื่นขึ้นมาในสถานะขยะ (Scrambled Invalid State)** และทำให้ระบบทำงานผิดพลาดทันทีตั้งแต่เริ่มเปิดเครื่อง!

> [!IMPORTANT] กฎการทำ Retiming บน FSM
> หากสเตตแมชชีนเป็นตัวควบคุมหลักของระบบ **ห้ามเปิด Global Retiming แบบสุ่มสี่สุ่มห้า** หรือหากจำเป็นต้องใช้ ให้ทำ Manual Retiming ในระดับโค้ด RTL โดยการแตกสเตจด้วยตนเอง หรือใส่ Attribute `(* DONT_TOUCH = "TRUE" *)` บน State Register เพื่อป้องกันไม่ให้ Tool เคลื่อนย้ายรีจิสเตอร์สถานะ!

---

### 1.3 เทคนิค Critical Path Unrolling และ Speculative Evaluation
เมื่อเส้นทาง Next-State Logic ติดลบและไม่สามารถใช้ Retiming ได้ วิธีการของ Senior Architect คือ **การคลี่เส้นทางวิกฤต (Critical Path Unrolling)**:

พิจารณาสเตตแมชชีนที่มีเงื่อนไขการเปลี่ยนสถานะขึ้นกับการเปรียบเทียบข้อมูลขนาดใหญ่ เช่น การตรวจสอบฟิลด์ IP Address 32 บิต และการตรวจความยาวเพย์โหลด:
* **เดิม (Serial Bottleneck):** รอรับข้อมูล $\rightarrow$ เปรียบเทียบ 32 บิต ($Logic\ Depth = 3$) $\rightarrow$ ถอดรหัสสเตตถัดไป ($Depth = 2$) $\rightarrow$ เข้า State Register (รวม $Depth = 5$ ทำให้ Slack ติดลบ)
* **ใหม่ (Unrolled Speculation):** แตกกิ่งการตัดสินใจออกเป็น 2 ทางคู่ขนาน:
  - สาขาที่ 1: คำนวณสเตตถัดไปล่วงหน้าโดยสมมติว่า Address Match เป็นจริง
  - สาขาที่ 2: คำนวณสเตตถัดไปล่วงหน้าโดยสมมติว่า Address Match เป็นเท็จ
  - ที่สเตจสุดท้าย: ใช้ผลลัพธ์ของ Address Match มาเป็นสัญญาณ Select เข้ามัลติเพล็กเซอร์ (MUX) ชั้นเดียว ($Depth = 1$)!

```
                โครงสร้าง Speculative Next-State Unrolling
                                  +--->[ Pre-decode IF Addr==Match ]--->[ 1 ]--+
                                  |                                            |
   Current State -----------------+                                            +->[ Fast MUX ]---> D [FF]
                                  |                                            |    ^
                                  +--->[ Pre-decode IF Addr!=Match ]--->[ 0 ]--+    |
                                                                                    |
   32-bit Address Comparator Output ------------------------------------------------+ (Late Arrival)
```

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Manual Pipelined Retimed State Machine สำหรับ 500MHz

```systemverilog
//=============================================================================
// Module: hft_fix_parser_fsm.sv
// Description: Ultra-Low-Latency 500MHz FIX Protocol Parser FSM
// Architecture: Manual Retimed Pipeline with Speculative Next-State Logic
// Sign-off: AMD UltraScale+ -2 Speed Grade (T_clk = 2.0ns, WNS > +0.150ns)
//=============================================================================
`timescale 1ns / 1ps

module hft_fix_parser_fsm (
    input  logic        clk,
    input  logic        rst_n,
    // สตรีมข้อมูลคำสั่งซื้อขายความเร็วสูง
    input  logic [63:0] rx_ascii_data,
    input  logic        rx_data_valid,
    output logic        order_buy_trigger,
    output logic        order_sell_trigger,
    output logic [1:0]  parser_state_dbg
);

    // นิยามสเตตการทำงาน
    typedef enum logic [1:0] {
        ST_SEEK_TAG   = 2'b00,
        ST_PARSE_BODY = 2'b01,
        ST_EXEC_ORDER = 2'b10,
        ST_ERROR_DUMP = 2'b11
    } state_t;

    // ล็อก State Register ไม่ให้โดน Auto-Retiming เล่นงาน
    (* DONT_TOUCH = "TRUE" *) state_t current_state;

    // Stage 1: Pipelined Pre-computation (ย้ายการเปรียบเทียบ ASCII มาทำล่วงหน้า)
    logic is_tag_35_buy_reg;
    logic is_tag_35_sell_reg;
    logic is_delimiter_reg;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            is_tag_35_buy_reg  <= 1'b0;
            is_tag_35_sell_reg <= 1'b0;
            is_delimiter_reg   <= 1'b0;
        end else begin
            // เปรียบเทียบรหัส Tag 35=D (Buy) และ Tag 35=S (Sell) ใน FIX Protocol
            is_tag_35_buy_reg  <= (rx_ascii_data[31:0] == 32'h33353D44); // "35=D"
            is_tag_35_sell_reg <= (rx_ascii_data[31:0] == 32'h33353D53); // "35=S"
            is_delimiter_reg   <= (rx_ascii_data[7:0]  == 8'h01);       // SOH Delimiter
        end
    end

    // Stage 2: Speculative Next-State Generation (เหลือเพียง 1-Level LUT)
    state_t next_state_speculative;

    always_comb begin
        case (current_state)
            ST_SEEK_TAG: begin
                if (rx_data_valid) begin
                    next_state_speculative = ST_PARSE_BODY;
                end else begin
                    next_state_speculative = ST_SEEK_TAG;
                end
            end

            ST_PARSE_BODY: begin
                if (is_delimiter_reg) begin
                    next_state_speculative = ST_EXEC_ORDER;
                end else begin
                    next_state_speculative = ST_PARSE_BODY;
                end
            end

            ST_EXEC_ORDER: begin
                next_state_speculative = ST_SEEK_TAG;
            end

            default: begin
                next_state_speculative = ST_SEEK_TAG;
            end
        endcase
    end

    // อัปเดตสถานะที่ขอบสัญญาณนาฬิกา
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            current_state <= ST_SEEK_TAG;
        end else begin
            current_state <= next_state_speculative;
        end
    end

    // Stage 3: Look-Ahead Registered Trigger Outputs
    // ขับตรงออกจาก Flip-Flop เพื่อให้ได้ Clock-to-Out สั้นที่สุดสำหรับงาน HFT
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            order_buy_trigger  <= 1'b0;
            order_sell_trigger <= 1'b0;
        end else begin
            order_buy_trigger  <= (current_state == ST_PARSE_BODY) && is_delimiter_reg && is_tag_35_buy_reg;
            order_sell_trigger <= (current_state == ST_PARSE_BODY) && is_delimiter_reg && is_tag_35_sell_reg;
        end
    end

    assign parser_state_dbg = current_state;

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในบริษัทพัฒนาระบบซื้อขายหลักทรัพย์ความถี่สูงพิเศษ (Ultra-High-Frequency Trading: HFT) บนการ์ดเร่งความเร็ว AMD Alveo U50 FPGA วงจรตัวแยกข้อมูลโพรโทคอลตลาดหุ้น (FIX Parser) ต้องทำงานที่ความถี่สัญญาณนาฬิกา $500\text{ MHz}$ ($T_{clk} = 2.000\text{ ns}$) ในขั้นตอนการคอมไพล์รอบแรก รายงาน Vivado STA แจ้งเตือนความล้มเหลวด้านเวลา: $WNS = -0.580\text{ ns}$ ในลูปของ State Machine

**ผลลัพธ์ที่ล้มเหลว:** วิศวกรจบใหม่แก้ไขปัญหาด้วยการเปิดตัวเลือกคอมไพเลอร์แบบครอบจักรวาล:
```tcl
set_property STEPS.SYNTH_DESIGN.ARGS.RETIMING true [get_runs synth_1]
```
ผลปรากฏว่ารายงาน Vivado Timing ผ่านฉลุย ($WNS = +0.080\text{ ns}$) วิศวกรจึงส่งมอบบิตสตรีมขึ้นติดตั้งบนเซิร์ฟเวอร์ตลาดหลักทรัพย์ทันที ทว่าเมื่อระบบเปิดเครื่องในเช้าวันเปิดทำการซื้อขายจริง บอร์ด FPGA ส่งคำสั่งซื้อขายที่ไม่ถูกต้อง (Malformed Garbage Orders) เข้าสู่ตลาดหลักทรัพย์ทันทีตั้งแต่ไซเคิลแรก สร้างความเสียหายมูลค่ากว่า 12 ล้านเยนและถูกตลาดหลักทรัพย์สั่งระงับการเชื่อมต่อ (Circuit Breaker)!

```
               หายนะจากการเปิด Global Retiming บนสเตตแมชชีน
   
   เปิด Vivado Synthesis -retiming true โดยไม่มีข้อจำกัด
                         |
                         v
   Vivado ย้าย State Register ข้ามผ่าน LUT ถอดรหัส ASCII
   เพื่อปรับสมดุลความหน่วงของเส้นทางวิกฤต
                         |
                         v
   เวกเตอร์รีเซ็ตดั้งเดิมถูกบิดเบือน (Reset Value Reconstruction Error)
   State Register ตื่นขึ้นมาด้วยค่าเริ่มต้นที่ผิดพลาด: 2'b10 (ST_EXEC_ORDER!)
                         |
                         v
   วงจรส่งคำสั่งยิง Order ซื้อขายขยะเข้าสู่ตลาดหุ้นตั้งแต่เปิดเครื่อง!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมระบบ HFT ถึงส่งคำสั่งซื้อขายผิดพลาดเข้าตลาดหุ้นตั้งแต่เปิดเครื่อง?**
   * *ตอบ:* วงจรส่งสัญญาณสั่งยิงออร์เดอร์ (`order_buy_trigger`) ทำงานขึ้นมาทันทีหลังปลดสัญญาณรีเซ็ต
2. **ทำไมสัญญาณสั่งยิงออร์เดอร์ถึงทำงานทั้งที่ยังไม่มีข้อมูลเข้ามา?**
   * *ตอบ:* สเตตแมชชีนเริ่มต้นการทำงานที่สถานะ `ST_EXEC_ORDER` แทนที่จะเป็นสถานะ `ST_SEEK_TAG`
3. **ทำไมสเตตแมชชีนถึงตื่นขึ้นมาในสถานะ `ST_EXEC_ORDER` หลังรีเซ็ต?**
   * *ตอบ:* ค่าเริ่มต้นของ Flip-Flop หลังรีเซ็ตถูกแปลงค่าเป็นตัวเลขที่ไม่ถูกต้องในระดับเน็ตลิสต์
4. **ทำไมค่าเริ่มต้นของ Flip-Flop ในเน็ตลิสต์ถึงไม่ตรงกับโค้ด RTL?**
   * *ตอบ:* ตัวเลือกการคอมไพล์ `-retiming true` ของ Vivado ย้าย Flip-Flop ข้ามผ่านลอจิกคอมบิเนชัน และอัลกอริทึมคำนวณค่ารีเซ็ตย้อนกลับทำงานล้มเหลวกับโครงสร้าง FSM
5. **ทำไมวิศวกรถึงเปิดใช้งาน Global Retiming โดยไม่ได้ตรวจสอบเน็ตลิสต์?**
   * *ตอบ:* วิศวกรต้องการปิด Timing ให้ผ่านโดยเร็ว จึงใช้ทางลัดของ Tool โดยขาดความตระหนักว่า **การทำ Retiming ข้าม FSM มีความเสี่ยงที่จะทำลาย Reset State Vector เสมอ**!

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ FIX Parser จาก Retiming
   
   ความรู้ความเข้าใจเครื่องมือ (Tool Competence)     ระเบียบวิธีวิศวกรรม (Design Methodology)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   เข้าใจผิดเรื่อง ไม่รู้ข้อจำกัด               เปิด Retiming  ไม่ทำ Manual
   การคำนวณ      ของ Reset                      ทั้งโปรเจกต์   Pipelining
   Reset Vector   Retiming                       แบบเหมารวม     ในระดับ RTL
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> ส่ง Order ขยะเข้าตลาด
                                                                |     จาก Scrambled Reset
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   Clock Target  เวลาจำกัด                      ไม่ได้รัน Post-  ขาด Gate-Level
   สูงถึง 500MHz ต้องการส่งมอบ                   Implementation Power-on Reset
   (T_clk = 2ns) งานด่วน                        Simulation     Testbench
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   ความกดดันด้านเวลา (Schedule Pressure)          กระบวนการตรวจสอบขั้นสุดท้าย (Sign-off)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ล็อกสเตตรีเซ็ตด้วยแอตทริบิวต์ `DONT_TOUCH`
หากต้องเปิดฟีเจอร์ Synthesis Retiming ในโปรเจกต์ ให้ใส่ Attribute บน State Register ทุกตัวของระบบเสมอ:
```systemverilog
(* DONT_TOUCH = "TRUE" *) state_t current_state;
```
คำสั่งนี้จะสั่งให้ Vivado ทำ Retiming ได้เฉพาะในส่วนของ Datapath เท่านั้น และห้ามเคลื่อนย้าย State Register ของ FSM เด็ดขาด

#### ขั้นตอนที่ 2: รัน Post-Implementation Timing Simulation (Gate-Level Sim)
ห้ามปล่อยแบบโดยดูแค่ RTL Simulation! ต้องรัน Gate-Level Simulation พร้อมไฟล์ SDF (Standard Delay Format) เพื่อตรวจสอบพฤติกรรมการปลดรีเซ็ต (Reset Deassertion Behavior):
```tcl
launch_simulation -mode post-implementation -type timing
```
ยืนยันว่าเวกเตอร์สถานะในรอบแรกหลังปลดรีเซ็ตมีค่าตรงตาม `ST_IDLE` หรือ `ST_RESET` อย่างแท้จริง

#### ขั้นตอนที่ 3: ใช้การทำ Manual Retiming ใน RTL แทน Automatic Retiming
ย้ายตรรกะการเปรียบเทียบที่ซับซ้อนออกมาเป็น Pipeline Stage ใน RTL ด้วยตนเอง (Explicit RTL Pipelining) เพื่อให้การควบคุมตำแหน่งของ Flip-Flop อยู่ในความดูแลของวิศวกร $100\%$

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| タイミング収束 | たいみんぐしゅうそく | Taimingu Shuusoku | Timing Closure |
| リタイミング | りたいみんぐ | Ritaimingu | Register Retiming |
| 初期状態崩壊 | しょきじょうたいほうかい | Shoki Joutai Houkai | Reset State Corruption / Scrambling |
| クリティカルパス展開 | くりてぃかるぱすてんかい | Kuritikaru Pasu Tenkai | Critical Path Unrolling |
| 投機的状態生成 | とうきてきじょうたいせいせい | Toukiteki Joutai Seisei | Speculative State Generation |
| 最悪スラック値 | さいあくすらっくち | Saiaku Surakkuchi | Worst Negative Slack (WNS) |
| 総スラック負値 | そうすらっくふち | Sou Surakku Fuchi | Total Negative Slack (TNS) |
| ゲートレベル遅延シミュレーション | げーとれべるちえんしみゅれーしょん | Geeto Reberu Chien Shimyureeshon | Gate-Level Timing Simulation |
| 等価性検証 | とうかせいけんしょう | Toukasei Kenshou | Equivalence Checking |
| マルチサイクル制約 | まるちさいくるせいやく | Maruchisaikuru Seiyaku | Multicycle Path Constraint |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** ห้องประชุมวอร์รูมระบบเทรดดิ้งความเร็วสูงพิเศษ (HFT FPGA Engineering War Room)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** โอกาโมโตะ ซัง (Okamoto-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** ฟุคุดะ คุง (Fukuda-kun)

---

**岡本技師 (Okamoto):**  
「福田君、先週リリースした Alveo U50 用 FIX パース回路だが、今朝の本番稼働直後に未定義の注文パケットが東証ゲートウェイへ誤送信され、回線が緊急遮断されたぞ！合成ログを確認したところ、プロジェクト全体に対して `-retiming true` を無無断で適用しているようだが、ステートレジスタの初期値検証（Power-on Reset Verification）はどうなっていたんだ？」  
*(Fukuda-kun, senshuu ririisu shita Alveo U50 you FIX paasu kairo dakedo, kesa no honban kadou chokugo ni miteigi no chuumon paketto ga Toushou geetowei e go-soushin sare, kaisen ga kinkyuu shadan sareta zo! Gousei rogu wo kakunin shita tokoro, purojekuto zentai ni taishite `-retiming true` wo mudan de tekiyou shite iru you da ga, suteeto rejisuta no shokichi kenshou (Power-on Reset Verification) wa dou natte itanda?)*  
**ความหมาย:** คุณฟุคุดะ วงจรแยกแพ็กเก็ต FIX บนการ์ด Alveo U50 ที่คุณเพิ่งปล่อยไปเมื่อสัปดาห์ก่อน พอเริ่มเปิดระบบจริงเมื่อเช้านี้ มันยิงคำสั่งซื้อขายขยะเข้าเกตเวย์ของตลาดหลักทรัพย์โตเกียวทันที จนระบบโดนสั่งตัดสายฉุกเฉินแล้วนะ! ผมไปตรวจดู Synthesis Log พบว่าคุณแอบเปิดออปชัน `-retiming true` คลุมทั้งโปรเจกต์โดยพลการ แล้วแบบนี้การตรวจสอบค่าเริ่มต้นของ State Register ตอนเปิดเครื่องคุณได้ทำบ้างหรือเปล่าครับ?

---

**福田技師 (Fukuda):**  
「大変申し訳ございません…！500MHz のタイミング要件に対して WNS が $-0.580\text{ ns}$ もショートしておりました。手動で RTL を直す時間が足りなかったため、ツールの自動リタイミングを有効化しました。WNS が $+0.080\text{ ns}$ で収束したため、RTL シミュレーションの波形が正常であることを確認してリリースしてしまいました…。」  
*(Taihen moushiwake gozaimasen...! 500MHz no taimingu youken ni taishite WNS ga $-0.580\text{ ns}$ mo shooto shite orimashita. Shudou de RTL wo naosu jikan ga tarinakatta tame, tsuuru no jidou ritaimingu wo yuukouka shimashita. WNS ga $+0.080\text{ ns}$ de shuusoku shita tame, RTL shimyureeshon no hakei ga seijou de aru koto wo kakunin shite ririisu shite shimaimashita...)*  
**ความหมาย:** ต้องกราบขออภัยเป็นอย่างยิ่งครับ...! ตอนนั้นสเปก 500MHz มันขาดทุนค่า WNS ไปถึง $-0.580\text{ ns}$ ผมมีเวลาแก้ RTL ไม่พอ เลยเปิดใช้ Auto Retiming ของ Tool ครับ พอเห็นว่า WNS ปิดผ่านได้ $+0.080\text{ ns}$ และผลรูปคลื่นใน RTL Simulation ก็ปกติดี ผมจึงปล่อยบิตสตรีมออกไปครับ...

---

**岡本技師 (Okamoto):**  
「大馬鹿者！RTL シミュレーションではリタイミング後のネットリスト構造は一切反映されない！FSM のステートレジスタをツールが勝手にデコーダの反対側へ移動させた結果、リセット直後の論理値が破壊され、いきなり注文実行ステートから起動したんだ！リタイミングはデータパスにのみ適用すべきであり、ステートマシンに安易に適用すれば初期状態が崩壊するのは業界の常識だ！**懲罰的重大指摘事項とする！** 直ちにステートレジスタに `(* DONT_TOUCH = "TRUE" *)` を付与してリタイミングを禁止し、ASCII 比較を前段へ追い出す手動パイプライン（Critical Path Unrolling）へ全面改修しなさい！」  
*(Oo-bakamono! RTL shimyureeshon dewa ritaimingu-go no nettorisuto kouzou wa issai han-ei sarenai! FSM no suteeto rejisuta wo tsuuru ga katte ni dekouda no hantaigawa e idou saseta kekka, risetto chokugo no ronrichi ga hakai sare, ikinari chuumon jikkou suteeto kara kidou shitanda! Ritaimingu wa deetapasu ni nomi tekiyou subeki de ari, suteeto mashin ni an-i ni tekiyou sureba shoki joutai ga houkai suru no wa gyoukai no joushiki da! **Choubatsuteki juudai shiteki jikou to suru!** Tadachini suteeto rejisuta ni `(* DONT_TOUCH = "TRUE" *)` wo fuyo shite ritaimingu wo kinshi shi, ASCII hikaku wo zendan e oidasu shudou paipurain (Critical Path Unrolling) e zenmen kaishuu shinasai!)*  
**ความหมาย:** เจ้าบัดซบเอ๊ย! ใน RTL Simulation มันไม่ได้สะท้อนโครงสร้าง Netlist หลังทำ Retiming เลยสักนิด! การที่ Tool มันแอบย้าย State Register ข้ามไปอยู่อีกฝั่งของตัวถอดรหัส ทำให้ตรรกะตอนรีเซ็ตพังทลาย และเครื่องเลยตื่นขึ้นมาในสเตตส่งคำสั่งซื้อขายทันทีไงล่ะ! การทำ Retiming ต้องจำกัดไว้เฉพาะ Datapath เท่านั้น การเอามาใช้กับ State Machine ซี้ซั้วแล้วทำให้สเตตรีเซ็ตพังมันคือความรู้พื้นฐานของวงการนะ! **ผมสั่งลงโทษและบันทึกเป็นข้อแก้ไขขั้นเด็ดขาด!** จงรีบใส่ `(* DONT_TOUCH = "TRUE" *)` บน State Register เพื่อห้ามทำ Retiming เด็ดขาด แล้วเขียน Pipelining ด้วยมือเพื่อคลาย Critical Path ในระดับ RTL เดี๋ยวนี้!

---

**福田技師 (Fukuda):**  
「ツールの自動最適化がリセット初期値を破壊する恐怖を骨の髄まで痛感いたしました…。二度とツールの自動リタイミングに依存いたしません。直ちに手動パイプライン化と投機的状態展開を RTL レベルで実装し、配置配線後ゲートレベルシミュレーションで初期起動時の完全な安全性を証明して再提出いたします！」  
*(Tsuuru no jidou saitekika ga risetto shokichi wo hakai suru kyoufu wo hone no zui made tsuukan itashimashita... Nido to tsuuru no jidou ritaimingu ni izon itashimasen. Tadachini shudou paipurain-ka to toukiteki joutai tenkai wo RTL reberu de jissou shi, haichi haisen-go geeto reberu shimyureeshon de shoki kidouji no kanzen na anzensei wo shoumei shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ผมซาบซึ้งถึงความน่ากลัวของการที่ Tool แอบทำลายค่าเริ่มต้นรีเซ็ตจนถึงกระดูกดำแล้วครับ... ผมจะไม่พึ่งพา Auto Retiming ของ Tool มักง่ายแบบนี้อีกแล้ว จะรีบลงมือทำ Manual Pipelining และ Speculative State ในโค้ด RTL ด้วยตัวเอง พร้อมทั้งรัน Gate-Level Simulation เพื่อพิสูจน์ความปลอดภัยในการบูต 100% แล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณตำแหน่งรีจิสเตอร์ที่เหมาะสมที่สุดตามทฤษฎีบท Leiserson-Saxe Retiming

พิจารณาเส้นทางประมวลผลลำดับเส้นหนึ่งซึ่งประกอบด้วยบล็อกลอจิกคอมบิเนชัน 3 บล็อก ($L_1, L_2, L_3$) และรีจิสเตอร์ $2$ ตัว ($R_1, R_2$) วางเรียงกันดังนี้:

$$\text{Input} \rightarrow [R_1] \rightarrow [L_1: 1.4\text{ ns}] \rightarrow [L_2: 2.8\text{ ns}] \rightarrow [R_2] \rightarrow [L_3: 1.0\text{ ns}] \rightarrow \text{Output}$$

กำหนดพารามิเตอร์เวลาของรีจิสเตอร์:
* Flip-Flop Clock-to-Q delay: $t_{co} = 0.200\text{ ns}$
* Flip-Flop Setup time: $t_{su} = 0.100\text{ ns}$
* Clock Uncertainty: $T_{unc} = 0.100\text{ ns}$

หากทำการย้ายตำแหน่งของรีจิสเตอร์ $R_2$ ด้วยเทคนิค Retiming ให้มาคั่นกลางระหว่างบล็อก $L_1$ และ $L_2$ โดยที่บล็อก $L_2$ ไม่สามารถแบ่งย่อยได้อีก:
$$\text{Input} \rightarrow [R_1] \rightarrow [L_1: 1.4\text{ ns}] \rightarrow [R_{2, new}] \rightarrow [L_2: 2.8\text{ ns}] \rightarrow [L_3: 1.0\text{ ns}] \rightarrow [R_{out}]$$
*(โดยการใส่ Register เพิ่มอีก 1 สเตจที่เอาต์พุต)*

จงคำนวณหาคาบเวลาสัญญาณนาฬิกาต่ำสุด ($T_{clk\_min}$) และความถี่สูงสุด ($F_{max}$) **ก่อนและหลัง** การปรับปรุงด้วย Retiming?

---

#### ตัวเลือก:
A) ก่อน: $T_{clk} = 4.60\text{ ns}$ ($217.4\text{ MHz}$), หลัง: $T_{clk} = 3.20\text{ ns}$ ($312.5\text{ MHz}$)  
B) ก่อน: $T_{clk} = 4.20\text{ ns}$ ($238.1\text{ MHz}$), หลัง: $T_{clk} = 2.80\text{ ns}$ ($357.1\text{ MHz}$)  
C) ก่อน: $T_{clk} = 4.60\text{ ns}$ ($217.4\text{ MHz}$), หลัง: $T_{clk} = 4.20\text{ ns}$ ($238.1\text{ MHz}$)  
D) ก่อน: $T_{clk} = 5.20\text{ ns}$ ($192.3\text{ MHz}$), หลัง: $T_{clk} = 2.50\text{ ns}$ ($400.0\text{ MHz}$)

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) ก่อน: $T_{clk} = 4.60\text{ ns}$ ($217.4\text{ MHz}$), หลัง: $T_{clk} = 3.20\text{ ns}$ ($312.5\text{ MHz}$)**

##### ขั้นตอนที่ 1: คำนวณคาบเวลาเดิมก่อนทำ Retiming
เส้นทางวิกฤตเดิมอยู่ระหว่าง $R_1$ และ $R_2$ ซึ่งมีบล็อก $L_1$ และ $L_2$ ต่ออนุกรมกัน:
$$T_{comb\_orig} = d(L_1) + d(L_2) = 1.400\text{ ns} + 2.800\text{ ns} = 4.200\text{ ns}$$
สมการคาบเวลาขั้นต่ำ:
$$T_{clk\_min\_orig} = t_{co} + T_{comb\_orig} + t_{su} + T_{unc}$$
แทนค่า:
$$T_{clk\_min\_orig} = 0.200\text{ ns} + 4.200\text{ ns} + 0.100\text{ ns} + 0.100\text{ ns} = 4.600\text{ ns}$$
ความถี่สูงสุดเดิม:
$$F_{max\_orig} = \frac{1}{4.600 \times 10^{-9}\text{ s}} \approx 217.39\text{ MHz}$$

##### ขั้นตอนที่ 2: คำนวณคาบเวลาใหม่หลังทำ Retiming
หลังย้าย Register คั่นกลางระหว่าง $L_1$ และ $L_2$ พร้อมแทรก Register คั่นระหว่าง $L_2$ และ $L_3$:
เส้นทางจะถูกแบ่งออกเป็น 3 ช่วง:
1. ช่วงที่ 1 (ผ่าน $L_1$): $T_{comb1} = 1.400\text{ ns}$
2. ช่วงที่ 2 (ผ่าน $L_2$): $T_{comb2} = 2.800\text{ ns}$
3. ช่วงที่ 3 (ผ่าน $L_3$): $T_{comb3} = 1.000\text{ ns}$

เส้นทางที่ยาวที่สุดคือช่วงที่ 2 ($L_2 = 2.800\text{ ns}$):
$$T_{clk\_min\_new} = t_{co} + d(L_2) + t_{su} + T_{unc}$$
แทนค่า:
$$T_{clk\_min\_new} = 0.200\text{ ns} + 2.800\text{ ns} + 0.100\text{ ns} + 0.100\text{ ns} = 3.200\text{ ns}$$
ความถี่สูงสุดใหม่:
$$F_{max\_new} = \frac{1}{3.200 \times 10^{-9}\text{ s}} = 312.50\text{ MHz}$$

การทำ Retiming ปรับสมดุลความหน่วงช่วยเพิ่มความเร็วของวงจรขึ้นได้ถึง **$43.7\%$** (จาก $217\text{ MHz}$ สู่ $312.5\text{ MHz}$)!

---

### คำถามที่ 2: การคำนวณ Hold Check Margin ของคำสั่ง Multicycle Path บน FSM Multi-beat Transition

ในสเตตแมชชีนควบคุมหน่วยความจำ DDR4 สเตต `ST_WAIT_BURST` มีการกำหนดให้สัญญาณควบคุมเปิดค้างไว้เป็นเวลา $3$ คาบสัญญาณนาฬิกาเต็ม ($T_{clk} = 3.000\text{ ns}$) ก่อนที่ข้อมูลจะถูกบันทึกเข้าสู่รีจิสเตอร์ปลายทาง วิศวกรกำหนดคำสั่งใน XDC ดังนี้:

```tcl
set_multicycle_path 3 -setup -from [get_cells u_fsm/state_reg*] -to [get_cells u_core/buf_reg*]
set_multicycle_path 2 -hold  -from [get_cells u_fsm/state_reg*] -to [get_cells u_core/buf_reg*]
```

หากความหน่วงเวลาต่ำสุดของสายข้อมูลในสภาวะ Fast Corner (อุณหภูมิ $-40^\circ\text{C}$) คือ $T_{data\_min} = 0.850\text{ ns}$, ค่า Hold Time ของ Flip-Flop คือ $t_h = 0.050\text{ ns}$, และ Clock Uncertainty ของ Hold คือ $T_{unc\_hold} = 0.080\text{ ns}$

จงคำนวณหาค่า **Hold Slack ($S_{hold}$)** และระบุว่าขอบสัญญาณนาฬิกาที่ตรวจสอบ Hold Time (Hold Check Edge) อยู่ที่กี่นาโนวินาทีเทียบกับขอบส่งสัญญาณ (Launch Edge ที่ $0.0\text{ ns}$)?

---

#### ตัวเลือก:
A) Hold Check Edge อยู่ที่ $0.0\text{ ns}$, Hold Slack = $+0.720\text{ ns}$ (ปลอดภัยสมบูรณ์)  
B) Hold Check Edge อยู่ที่ $3.0\text{ ns}$, Hold Slack = $-2.280\text{ ns}$ (Hold Violation รุนแรง)  
C) Hold Check Edge อยู่ที่ $6.0\text{ ns}$, Hold Slack = $+0.720\text{ ns}$  
D) Hold Check Edge อยู่ที่ $0.0\text{ ns}$, Hold Slack = $-0.080\text{ ns}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) Hold Check Edge อยู่ที่ $0.0\text{ ns}$, Hold Slack = $+0.720\text{ ns}$ (ปลอดภัยสมบูรณ์)**

##### ขั้นตอนที่ 1: วิเคราะห์ตำแหน่งขอบเวลาของ Setup และ Hold ตามกฎ SDC
1. การระบุ `-setup 3`:
   ขอบ Setup Capture Edge จะถูกเลื่อนไปที่ขอบที่ 3:
   $$T_{setup\_edge} = 3 \times T_{clk} = 3 \times 3.000\text{ ns} = 9.000\text{ ns}$$
2. โดยดีฟอลต์ หากไม่มีคำสั่ง `-hold`:
   เครื่องมือ STA จะตรวจ Hold Check ที่ขอบก่อน Setup 1 คาบเวลา ($3 - 1 = 2 \Rightarrow 6.000\text{ ns}$) ซึ่งจะทำให้เกิด Hold Violation มหาศาล
3. การระบุ `-hold 2`:
   เครื่องมือ STA จะดึงขอบ Hold Check ถอยหลังกลับมาอีก 2 คาบเวลา:
   $$\text{Hold Capture Edge} = 9.000\text{ ns} - (1 \times T_{clk}) - (2 \times T_{clk}) = 9.000 - 3.000 - 6.000 = 0.000\text{ ns}$$
   ทำให้ขอบ Hold Check ถอยกลับมาอยู่ที่ **ขอบที่ 0 ($0.0\text{ ns}$)** ซึ่งเป็นขอบเดียวกับ Launch Edge พอดี!

##### ขั้นตอนที่ 2: คำนวณ Hold Slack
สมการ Hold Slack เมื่อตรวจสอบที่ขอบเดียวกัน ($0.0\text{ ns}$):
$$S_{hold} = T_{data\_min} - t_h - T_{unc\_hold}$$
แทนค่า:
$$S_{hold} = 0.850\text{ ns} - 0.050\text{ ns} - 0.080\text{ ns} = +0.720\text{ ns}$$
ค่า Hold Slack มีค่าเป็นบวก ($+0.720\text{ ns}$) ระบบจึงปลอดภัยจากปัญหา Hold Time Violation ในทุก Corner อย่างสมบูรณ์แบบ

---

### คำถามที่ 3: เกณฑ์มาตรฐานการ Sign-off ค่า Slack (WNS และ TNS) สำหรับวงจรความเร็วสูง

ในขั้นตอนการตรวจสอบเวลาขั้นสุดท้าย (Timing Sign-off Audit) ค่าตัวชี้วัดใดที่ยอมรับได้สำหรับการอนุมัติแบบเพื่อส่งผลิตบิตสตรีมโปรดักชัน?

---

#### ตัวเลือก:
A) $WNS \ge 0.000\text{ ns}$, $TNS = 0.000\text{ ns}$, $WHS \ge 0.000\text{ ns}$, และ $THS = 0.000\text{ ns}$ ในทุก Corner การทำงาน  
B) $WNS > -0.500\text{ ns}$ ตราบใดที่ค่าเฉลี่ยเป็นบวก  
C) $TNS < 10.0\text{ ns}$ ถือว่ายอมรับได้สำหรับ FPGA  
D) ตรวจสอบเฉพาะที่ Slow Corner อุณหภูมิสูงเท่านั้น Fast Corner ไม่จำเป็นต้องดู

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) $WNS \ge 0.000\text{ ns}$, $TNS = 0.000\text{ ns}$, $WHS \ge 0.000\text{ ns}$, และ $THS = 0.000\text{ ns}$ ในทุก Corner การทำงาน**

##### เหตุผลทางวิศวกรรม STA Sign-off:
* **Worst Negative Slack (WNS):** ต้องไม่ติดลบ ($WNS \ge 0.000\text{ ns}$) เพื่อรับประกันว่าไม่มีเส้นทางใดเลยที่ละเมิด Setup Time
* **Total Negative Slack (TNS):** ต้องเป็นศูนย์ ($TNS = 0.000\text{ ns}$) ซึ่งหมายความว่าไม่มีเส้นทางที่ล้มเหลวหลงเหลืออยู่แม้แต่เส้นทางเดียว
* **Worst Hold Slack (WHS) / Total Hold Slack (THS):** ต้องเป็นศูนย์หรือบวก ($WHS \ge 0$) เช่นกัน เพราะ Hold Violation จะทำให้ชิปทำงานผิดพลาดถาวรโดยไม่สามารถแก้ไขด้วยการลดความถี่ของสัญญาณนาฬิกาได้!
* และการตรวจสอบจะต้องครอบคลุม **ทุก Process Corner** (ทั้ง Slow-Cold, Slow-Hot, Fast-Cold, Fast-Hot) จึงจะถือว่าผ่านเกณฑ์มาตรฐานวิศวกรรมสากล
