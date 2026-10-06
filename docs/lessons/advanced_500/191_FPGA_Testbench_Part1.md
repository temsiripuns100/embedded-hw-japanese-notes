# Lesson 191: FPGA Testbench Part 1 — Self-Checking Testbench Architecture & Golden Models (สถาปัตยกรรม Self-Checking Testbench และโมเดลอ้างอิงระดับโกลเดน)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในยุคเริ่มต้นของการออกแบบดิจิทัล วิศวกรมักตรวจสอบการทำงานของวงจรด้วยการรัน Simulation แล้วกวาดสายตาดูสัญญาณรูปคลื่นใน Waveform Viewer (เช่น ModelSim, Vivado XSIM) แต่วิธีการนี้ **ล้าสมัยและอันตรายอย่างยิ่งสำหรับการออกแบบระดับอุตสาหกรรม (Visual Waveform Inspection is Obsolete and Hazardous)** เพราะวงจรขนาดใหญ่ทำงานระดับพันล้านไซเคิล การที่มนุษย์จะสังเกตเห็นสัญญาณกระพริบผิดพลาดเพียง 1 บิตใน 1 นาโนวินาทีนั้นมีความเป็นไปได้เกือบเท่ากับศูนย์

สถาปัตยกรรมการทดสอบระดับมืออาชีพจึงต้องเป็น **Self-Checking Testbench** ที่มีคุณสมบัติ:
1. **Automated Stimulus Generation:** สร้างสัญญาณกระตุ้นได้ทั้งแบบ Deterministic และ Constrained-Random
2. **Transaction-Level Modeling (TLM):** สื่อสารระหว่างโมดูลด้วย Packet/Transaction แทนที่จะเป็นสายไฟเดี่ยวๆ
3. **Golden Reference Model:** คำนวณผลลัพธ์ที่ถูกต้องตามอุดมคติ (Expected Value)
4. **Autonomous Scoreboard & Checker:** เปรียบเทียบผลลัพธ์จริงจาก RTL (Actual Value) กับโมเดลอ้างอิงทุกไซเคิลแบบอัตโนมัติ พร้อมส่งสัญญาณหยุดและบันทึกรายงานความผิดพลาดทันทีที่เกิด Mismatch

```
+--------------------------------------------------------------------------------------------------+
|                       SELF-CHECKING TESTBENCH SYSTEM ARCHITECTURE                                |
+--------------------------------------------------------------------------------------------------+
                                                                                                    
                  +----------------------------------------------+                                  
                  |              Stimulus Generator              |                                  
                  |   (Deterministic Sequences & Random Scenarios) |                                  
                  +----------------------------------------------+                                  
                            |                                |                                      
                 Transaction|                                |Transaction                           
                            v                                v                                      
             +----------------------------+       +------------------------------------+            
             | Bus Functional Model (BFM) |       |       Golden Reference Model       |            
             |       (Driver Agent)       |       |   (C/C++ DPI or Behavioral Alg)    |            
             +----------------------------+       +------------------------------------+            
                            | (Pin-Level Signals)                    | (Expected Packets)           
                            v                                        v                              
             +----------------------------+       +------------------------------------+            
             |      DUT (RTL Under Test)  |       |                                    |            
             |  Pipelined Hardware Block  |       |             SCOREBOARD             |            
             +----------------------------+       |       (Comparator & Mailbox)       |            
                            | (Pin-Level Signals) |                                    |            
                            v                     |  [Assert: Actual == Expected]      |            
             +----------------------------+       |  [Error Counter & Exit Code]       |            
             |       Monitor Agent        | ----> |                                    |            
             |    (Transaction Decoder)   |       +------------------------------------+            
             +----------------------------+                                                         
```

---

### 1.1 ทฤษฎีทางคณิตศาสตร์ว่าด้วยการตรวจสอบความถูกต้องของระบบประมวลผลไปป์ไลน์ (Pipelined Latency & Scoreboard Matching Math)

พิจารณาโมดูลฮาร์ดแวร์ภายใต้การทดสอบ (Device Under Test: DUT) ที่มีโครงสร้างแบบ Pipelined Processor โดยมีฟังก์ชันการคำนวณทางคณิตศาสตร์คือ $f(X)$  
กำหนดให้สัญญาณนำเข้าที่ไซเคิล $k$ คือเวกเตอร์ $X[k]$ และสัญญาณเอาต์พุตจริงที่ออกจาก DUT คือ $Y_{act}[k]$

#### 1. Pipeline Delay & Validity Mapping
หาก DUT มีการหน่วงเวลาคงที่ (Fixed Pipeline Latency) เท่ากับ $L_{pipe}$ ไซเคิล ความสัมพันธ์ระหว่างสัญญาณเข้าและออกคือ:
$$Y_{act}[k + L_{pipe}] = f(X[k]) \quad \text{เมื่อ } valid_{in}[k] = 1$$

แต่ในฮาร์ดแวร์จริง ระบบอาจมีสัญญาณควบคุมการหยุดชั่วคราว (Backpressure / Pipeline Stall: $stall[k]$) ทำให้เวลาหน่วงจริงไม่คงที่ เราจึงนิยามเวลาที่ข้อมูลออก (Completion Timestamp: $t_{out}(k)$) ด้วยสมการอินทิกรัลเชิงแยกส่วน:
$$t_{out}(k) = t_{in}(k) + L_{pipe} + \sum_{t = t_{in}(k)}^{t_{out}(k)} stall(t)$$

#### 2. Scoreboard Verification Invariant
Scoreboard ทำหน้าที่เก็บผลลัพธ์ที่คาดหวังจาก Golden Model ลงในแถวคิว $\mathcal{Q}_{exp} = \langle E_0, E_1, E_2, \dots \rangle$  
และเมื่อ Monitor สังเกตเห็นข้อมูล $A_j$ ปรากฏที่เอาต์พุตของ DUT พร้อมสัญญาณ `valid_out = 1`:
$$\text{Check: } A_j \stackrel{?}{=} \mathbf{pop}(\mathcal{Q}_{exp})$$
เงื่อนไขความถูกต้องสมบูรณ์ (Mathematical Soundness Invariant) คือ:
$$\forall j \in [0, M-1]: \quad \| A_j - E_j \| \le \epsilon_{tolerance}$$
สำหรับวงจร Fixed-Point DSP ค่า $\epsilon_{tolerance} = 0$ (Bit-Exact Match) แต่สำหรับอัลกอริทึม Floating-Point จะต้องมีค่าคลาดเคลื่อนยอมรับได้ตามมาตรฐาน IEEE 754

---

### 1.2 โครงสร้าง SystemVerilog Architecture สำหรับ Golden Model และ Scoreboard

ในการเขียน Self-Checking Testbench ระดับสูง มีเทคนิคสำคัญ 3 ประการ:
1. **Clocking Blocks (`default clocking cb @(posedge clk);`):** ป้องกันปัญหา Race Condition ระหว่าง Testbench Stimulus กับ DUT Signals
2. **Mailboxes & Queues (`mailbox #(transaction) mbx;`):** ใช้ส่งผ่านข้อมูล Transaction แบบ Asynchronous Decoupling
3. **Automatic Watchdog Timer:** ตรวจจับสัญญาณค้าง (Hang / Livelock) หากระบบเงียบไปเกิน $N_{timeout}$ ไซเคิล Testbench ต้องตัดจบพร้อมรายงาน Fatal Error ทันที

---

### 1.3 RTL Code: Master Self-Checking Testbench Framework (`tb_dsp_engine_selfcheck.sv`)

ตัวอย่างนี้สาธิตระบบ Self-Checking Testbench สมบูรณ์แบบสำหรับโมดูล **Pipelined Multiply-Accumulate (MAC) Engine** พร้อม Golden Model ในตัว

```systemverilog
//=============================================================================
// Module: tb_dsp_engine_selfcheck
// Description: Master Self-Checking Testbench Architecture with Golden Model
// Standards: DO-254 / ISO 26262 Verification Methodology Standard
//=============================================================================

`timescale 1ns / 1ps

// 1. Transaction Definition Class
class MacTransaction;
    rand bit signed [15:0] operand_a;
    rand bit signed [15:0] operand_b;
    rand bit signed [31:0] operand_c;
    bit signed [31:0]      result_act;
    bit signed [31:0]      result_exp;
    int                    trans_id;

    // Constrained Random Constraints for Corner Cases
    constraint c_corner_cases {
        operand_a dist { 16'h7FFF := 5, 16'h8000 := 5, 0 := 5, [-100:100] := 20, [-32768:32767] := 65 };
        operand_b dist { 16'h7FFF := 5, 16'h8000 := 5, 0 := 5, [-100:100] := 20, [-32768:32767] := 65 };
    }

    function void print(string tag = "");
        $display("[%0t ns][%s] ID=%0d | A=%0d, B=%0d, C=%0d | Act=%0d, Exp=%0d", 
                 $time, tag, trans_id, operand_a, operand_b, operand_c, result_act, result_exp);
    endfunction
endclass

// 2. Hardware Module Under Test (DUT: Pipelined MAC Engine)
module dsp_mac_dut #(
    parameter int LATENCY = 3
)(
    input  logic               clk,
    input  logic               rst_n,
    input  logic               valid_in,
    input  logic signed [15:0] a_in,
    input  logic signed [15:0] b_in,
    input  logic signed [31:0] c_in,
    output logic signed [31:0] p_out,
    output logic               valid_out
);
    // Pipeline Registers
    logic signed [31:0] mult_stage1;
    logic signed [31:0] c_stage1, c_stage2;
    logic signed [31:0] acc_stage2;
    logic [LATENCY-1:0] v_pipe;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mult_stage1 <= '0;
            c_stage1    <= '0;
            c_stage2    <= '0;
            acc_stage2  <= '0;
            p_out       <= '0;
            v_pipe      <= '0;
        end else begin
            // Stage 1: Multiplication
            mult_stage1 <= a_in * b_in;
            c_stage1    <= c_in;

            // Stage 2: Accumulation
            acc_stage2  <= mult_stage1 + c_stage1;

            // Stage 3: Output Register
            p_out       <= acc_stage2;

            // Valid pipeline
            v_pipe      <= {v_pipe[LATENCY-2:0], valid_in};
        end
    end

    assign valid_out = v_pipe[LATENCY-1];

endmodule

// 3. Top-Level Self-Checking Testbench
module tb_dsp_engine_selfcheck;

    // Testbench Clock and Reset
    logic clk;
    logic rst_n;
    logic valid_in;
    logic signed [15:0] a_in, b_in;
    logic signed [31:0] c_in;
    logic signed [31:0] p_out;
    logic valid_out;

    // Clock Generation (100 MHz, Period = 10ns)
    initial clk = 0;
    always #5 clk = ~clk;

    // DUT Instantiation
    dsp_mac_dut #(.LATENCY(3)) dut (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .a_in(a_in),
        .b_in(b_in),
        .c_in(c_in),
        .p_out(p_out),
        .valid_out(valid_out)
    );

    // Verification Mailboxes & Queues
    mailbox #(MacTransaction) gen2drv_mbx = new(16);
    MacTransaction exp_queue[$]; // Queue for Expected Values

    // Verification Statistics
    int match_count   = 0;
    int mismatch_count = 0;
    int total_stimulus = 500;

    // Clocking Block for Race-Free Signal Driving & Sampling
    default clocking cb @(posedge clk);
        default input #1step output #1ns;
        output valid_in, a_in, b_in, c_in;
        input  valid_out, p_out;
    endclocking

    //-------------------------------------------------------------------------
    // Task: Reset Sequence
    //-------------------------------------------------------------------------
    task automatic apply_reset();
        rst_n <= 1'b0;
        cb.valid_in <= 1'b0;
        cb.a_in     <= '0;
        cb.b_in     <= '0;
        cb.c_in     <= '0;
        repeat (5) @(cb);
        rst_n <= 1'b1;
        repeat (2) @(cb);
        $display("[%0t ns] Reset completed successfully.", $time);
    endtask

    //-------------------------------------------------------------------------
    // Process 1: Stimulus Generator
    //-------------------------------------------------------------------------
    task automatic stimulus_generator();
        MacTransaction tr;
        for (int i = 0; i < total_stimulus; i++) begin
            tr = new();
            if (!tr.randomize()) begin
                $fatal(1, "[GENERATOR] Randomization Failed!");
            end
            tr.trans_id = i;
            gen2drv_mbx.put(tr);
        end
        $display("[%0t ns] Generator: All %0d transactions generated.", $time, total_stimulus);
    endtask

    //-------------------------------------------------------------------------
    // Process 2: Driver & Golden Model Calculator
    //-------------------------------------------------------------------------
    task automatic driver_and_golden_model();
        MacTransaction tr;
        while (1) begin
            gen2drv_mbx.get(tr);

            // Compute Golden Model Expected Value
            tr.result_exp = (tr.operand_a * tr.operand_b) + tr.operand_c;
            exp_queue.push_back(tr); // Push to Scoreboard FIFO

            // Drive DUT Pins synchronously via Clocking Block
            cb.valid_in <= 1'b1;
            cb.a_in     <= tr.operand_a;
            cb.b_in     <= tr.operand_b;
            cb.c_in     <= tr.operand_c;
            @(cb);

            // Insert random bubble (0 to 2 idle cycles) for backpressure stress
            if ($urandom_range(0, 3) == 0) begin
                cb.valid_in <= 1'b0;
                repeat ($urandom_range(1, 2)) @(cb);
            end

            if (tr.trans_id == total_stimulus - 1) break;
        end
        // Clear bus
        cb.valid_in <= 1'b0;
    endtask

    //-------------------------------------------------------------------------
    // Process 3: Autonomous Monitor & Scoreboard
    //-------------------------------------------------------------------------
    task automatic monitor_and_scoreboard();
        MacTransaction exp_tr;
        int checked = 0;

        while (checked < total_stimulus) begin
            @(cb);
            if (cb.valid_out === 1'b1) begin
                if (exp_queue.size() == 0) begin
                    $fatal(1, "[SCOREBOARD] Unexpected DUT output! exp_queue is EMPTY.");
                end

                exp_tr = exp_queue.pop_front();
                exp_tr.result_act = cb.p_out;

                // Bit-Exact Comparison
                if (exp_tr.result_act === exp_tr.result_exp) begin
                    match_count++;
                end else begin
                    mismatch_count++;
                    $error("[SCOREBOARD MISMATCH] ID=%0d | Act=0x%08h (%0d) != Exp=0x%08h (%0d)",
                           exp_tr.trans_id, exp_tr.result_act, exp_tr.result_act, 
                           exp_tr.result_exp, exp_tr.result_exp);
                end
                checked++;
            end
        end
    endtask

    //-------------------------------------------------------------------------
    // Process 4: Watchdog Timer (Deadlock Prevention)
    //-------------------------------------------------------------------------
    task automatic watchdog_timer(int max_cycles);
        repeat (max_cycles) @(cb);
        $fatal(1, "[WATCHDOG TIMEOUT] Simulation exceeded %0d cycles! Pipeline Deadlock detected.", max_cycles);
    endtask

    //-------------------------------------------------------------------------
    // Main Verification Flow
    //-------------------------------------------------------------------------
    initial begin
        $display("===============================================================");
        $display("   STARTING SELF-CHECKING VERIFICATION SUITE: DSP MAC ENGINE  ");
        $display("===============================================================");

        apply_reset();

        fork
            stimulus_generator();
            driver_and_golden_model();
            monitor_and_scoreboard();
            watchdog_timer(10000); // 10,000 cycles watchdog limit
        join_any

        // Wait extra cycles for pipeline flush
        repeat (10) @(cb);

        // Final Report and Exit Code Assertion
        $display("\n===============================================================");
        $display("                    VERIFICATION SUMMARY REPORT                ");
        $display("===============================================================");
        $display("  Total Transactions : %0d", total_stimulus);
        $display("  Matched Passed     : %0d", match_count);
        $display("  Mismatched Failed  : %0d", mismatch_count);
        $display("===============================================================");

        if (mismatch_count == 0 && match_count == total_stimulus) begin
            $display("[TEST STATUS] >>>>> TEST PASSED 100%% BIT-EXACT <<<<<");
            $finish(0); // Exit code 0 (Success)
        end else begin
            $display("[TEST STATUS] >>>>> TEST FAILED WITH %0d ERRORS <<<<<", mismatch_count);
            $fatal(2, "Regression Failed with Data Inconsistency!");
        end
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความเสียหายจริงในภาคสนาม (失敗事例 - Shippai Jirei)
**ระบบเรดาร์ตรวจวัดสภาพอากาศของท่าอากาศยานนานาชาติ (Airport Terminal Doppler Weather Radar)** ประสบเหตุการณ์แจ้งเตือนพายุทอร์นาโดรุนแรงระดับผิดพลาด (False Tornado Warning Trigger): ระบบสั่งการให้หอบังคับการบินระงับการขึ้นลงของเที่ยวบินฉุกเฉินจำนวน 42 เที่ยวบิน และส่งเสียงไซเรนเตือนภัยทั่วสนามบิน แต่เมื่อตรวจสอบสภาพอากาศจริงภายนอกกลับพบว่าเป็นเพียงลมพัดปานกลาง ท้องฟ้าแจ่มใส

---

### การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมเรดาร์จึงประมวลผลความเร็วลมผิดเพี้ยนจนระบบเตือนภัยทอร์นาโดทำงาน?**
   - *คำตอบ:* โมดูลคำนวณ Doppler FFT มีค่าเอาต์พุตพุ่งสูงเกินจริง (Spurious Energy Spike) ในความถี่บางย่าน
2. **ทำไมอัลกอริทึม FFT จึงสร้างค่าพลังงานพุ่งสูงเกินจริง?**
   - *คำตอบ:* เวกเตอร์คำนวณเกิดสภาวะ **Sign-Bit Overflow Wrap-around** จากค่าติดลบกลายเป็นค่าบวกสูงสุดในขั้นตอนการทำ Butterfly Stage ที่ 4
3. **ทำไมการทดสอบโมดูล FFT ใน Testbench ก่อนส่งมอบจึงไม่พบบักนี้?**
   - *คำตอบ:* วิศวกรผู้พัฒนาใช้วิธี **Visual Waveform Inspection (ดูรูปคลื่นด้วยตาเปล่า)** ใน ModelSim โดยป้อนสัญญาณ Sinusoidal คงที่ 16 ตัวอย่าง แล้วดูว่ายอดคลื่นมีหน้าตาคล้ายไซน์เวฟหรือไม่
4. **ทำไมจึงไม่ใช้ Self-Checking Testbench เปรียบเทียบกับ MATLAB / Golden Model?**
   - *คำตอบ:* ทีมวิศวกรอ้างว่าเร่งรีบส่งมอบงาน จึงไม่ได้เสียเวลาเขียน Scoreboard อัตโนมัติ และไม่มีการรัน Constrained Random Stimulus ที่กวาดทุก Dynamic Range
5. **ทำไมขั้นตอน Kenzu (検図) จึงยอมให้ผ่านการอนุมัติได้?**
   - *คำตอบ:* ทีมตรวจสอบขาดกฎเหล็ก **"Zero Visual Inspection Sign-off Policy"** ที่ระบุว่า Testbench ทุกตัวต้องมี Automatic Pass/Fail Exit Code

---

### แผนผังสาเหตุและผล (Ishikawa Fishbone Diagram)

```
==================================================================================================
                                    ISHIKAWA FISHBONE CAUSE-EFFECT DIAGRAM
==================================================================================================

   MAN (บุคลากร)                                   MACHINE / TOOLS (เครื่องมือ)
   ----------------                                ---------------------------
   ใช้สายตามนุษย์ตรวจคลื่น (Visual Check)         ขาด Automated Scoreboard ใน Testbench
   ขาดความตระหนักเรื่อง Corner-case Wrap-around    ไม่มี MATLAB / C DPI Golden Reference Link
               \                                                /
                \                                              /
                 \                                            /
                  +------------------------------------------+
                  |                                          |
                  |  AIRPORT RADAR DOPPLER FALSE ALARM       | ===>> [AIRPORT SHUTDOWN & FLIGHT LOSS]
                  |                                          |
                  +------------------------------------------+
                 /                                            \
                /                                              \
   METHOD (ระเบียบปฏิบัติ)                          MATERIAL / ENVIRONMENT (สภาวะแวดล้อม)
   ----------------------                          -------------------------------------
   ไม่มีนโยบายห้ามตรวจด้วยรูปคลื่น                Dynamic Range ของสัญญาณเรดาร์จริงกว้างมาก
   ขาด Watchdog และ Exit Code บังคับ              สัญญาณกวน (Noise Burst) ทำให้เกิด Overflow
==================================================================================================
```

---

### คู่มือปฏิบัติการตรวจสอบ OJT หน้างาน: ขั้นตอนการสร้าง Self-Checking Testbench ระดับอุตสาหกรรม

1. **Step 1: แบนการตัดสินใจด้วยสายตาอย่างเด็ดขาด (Strict Ban on Visual Waveform Inspection)**
   - กำหนดในนโยบายของแผนกว่า: *"ห้ามส่งมอบโค้ด RTL หาก Testbench ต้องเปิด Waveform เพื่อยืนยันผล"*
   - ทุก Testbench ต้องมีคำสั่ง `$finish(0)` เมื่อผ่าน และ `$fatal(1)` เมื่อพบ Mismatch
2. **Step 2: การพัฒนา Golden Model ควบคู่ไปกับเอกสารสเปก (Golden Model Co-Development)**
   - ต้องเขียนโมเดลอ้างอิงด้วย C++, Python, หรือ Behavioral SystemVerilog ก่อนหรือพร้อมกับการเขียน RTL
   - เชื่อมโยงโมเดลด้วย SystemVerilog DPI-C (Direct Programming Interface) สำหรับอัลกอริทึมที่ซับซ้อน
3. **Step 3: การใส่ Watchdog Timer ป้องกันวงจรค้าง (Mandatory Watchdog Integration)**
   - กำหนด Timeout Limit ตามสูตร:
     $$N_{timeout} = N_{transactions} \times (L_{pipe} + Margin_{stall})$$
   - หากสัญญาณไม่ขยับเกินขีดจำกัด ต้องพิมพ์ Trace Dump และตัดจบการทำงานทันที

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (専門用語)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / อังกฤษ | บริบทการใช้งานเชิงวิศวกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **自己検証テストベンチ** | じこけんしょうテストベンチ | Jiko Kenshou Tesutobenchi | Self-Checking Testbench | เทสต์เบนช์ที่ตรวจสอบและตัดสินผลถูกผิดได้ด้วยตนเอง |
| **期待値** | きたいち | Kitaichi | Expected Value / Golden Value | ค่าที่คาดหวังซึ่งคำนวณจากโมเดลอ้างอิงระดับโกลเดน |
| **照合器** | しょうごうき | Shougouki | Comparator / Scoreboard | โมดูลเปรียบเทียบผลลัพธ์ระหว่าง DUT กับค่าที่คาดหวัง |
| **波形目視確認** | はけいもくしかくにん | Hakei Mokushi Kakunin | Visual Waveform Inspection | การใช้สายตาเพ่งดูรูปคลื่น (วิธีการต้องห้ามระดับโปร) |
| **不一致** | ふいっち | Fuicchi | Mismatch / Discrepancy | ความไม่ตรงกันของข้อมูลระหว่างค่าจริงกับค่าที่คาดหวัง |
| **番犬タイマー** | ばんけんタイマー | Banken Taimaa | Watchdog Timer | วงจรจับเวลาตัดจบเมื่อระบบเกิดสภาวะ Deadlock/ค้าง |
| **合格判定** | ごうかくはんてい | Goukaku Hantei | Pass Judgment | การตัดสินผลการทดสอบว่าผ่านเกณฑ์ 100% |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図審議 - Kenzu Shingi)

**สถานที่:** ศูนย์วิจัยและพัฒนาอุปกรณ์สื่อสารการบิน (Avionics Review Conference)  
**ผู้เข้าร่วม:**
- **ซาซากิ (佐々木):** Chief Verification Architect (検証主査)
- **สิทธิชัย (シッティチャイ):** Senior DSP FPGA Engineer (設計担当)

---

**佐々木主査 (ซาซากิ):**  
「シッティチャイさん、レーダー信号処理ブロックの検証ログを見ましたが、テストベンチの末尾で`$display("Done")`としか出力されていませんね。このテストベンチ、**自己検証（Self-Checking）**機能が入っていますか？」  
*(คุณสิทธิชัยครับ ผมดู Log การทดสอบของบล็อกประมวลผลเรดาร์แล้ว เห็นตอนท้ายพ่นแค่ `$display("Done")` ออกมาเองนี่ครับ เทสต์เบนช์ตัวนี้มีฟังก์ชัน Self-Checking อยู่ข้างในหรือเปล่าครับ?)*

**シッティチャイ (สิทธิชัย):**  
「佐々木主査、波形ビューアでFFTの出力スペクトラムを目視確認し、ピーク位置が合っていることを確認済みです。」  
*(หัวหน้าซาซากิครับ ใน Waveform Viewer ผมใช้สายตาตรวจสอบสเปกตรัมเอาต์พุตของ FFT แล้ว ยืนยันว่าตำแหน่งยอดคลื่นตรงกับเป้าหมายครับ)*

**佐々木主査 (ซาซากิ):**  
「馬鹿な！**波形目視確認（Visual Inspection）**で何十万ポイントもの演算結果を検証できるわけがないでしょう！もし途中でサチュレーション処理の1ビットの符号反転（Sign-bit flip）が起きていたら、画面の目視で見落とすに決まっています。航空機向けDO-254の監査官がこれを見たら、即座に不合格判定ですよ。」  
*(เหลวไหลสิ้นดี! การใช้สายตาเพ่งดูรูปคลื่นมันจะไปตรวจผลการคำนวณนับแสนๆ จุดได้อย่างไรกันครับ! ถ้าเกิดกรณีบิตเครื่องหมายกลับด้านจากการทำ Saturation ขึ้นมาเพียงบิตเดียว สายตามนุษย์มองข้ามไปร้อยเปอร์เซ็นต์แน่นอนครับ ถ้าผู้ตรวจประเมิน DO-254 ของการบินมาเห็นเข้า เขาปรับตกทันทีเลยนะ)*

**シッティチャイ (สิทธิชัย):**  
「申し訳ありません！私の認識が甘かったです。すぐにC言語の**期待値モデル（Golden Reference Model）**とDPI経由で接続し、自動スコアボード（Scoreboard）を構築します。」  
*(ขออภัยอย่างยิ่งครับ! ความตระหนักของผมยังอ่อนหัดเกินไป ผมจะรีบเชื่อมต่อ C-Language Golden Reference Model ผ่าน DPI ทันที และสร้าง Scoreboard อัตโนมัติขึ้นมาครับ)*

**佐々木主査 (ซาซากิ):**  
「分かればよろしい。スコアボードでは全出力データの**ビット完全一致（Bit-Exact Match）**を判定し、1件でも不一致があれば`$fatal`でCI/CDパイプラインを止めるように実装してください。波形を見なくても、スクリプトが自動で合否判定（Pass/Fail）を出せる体制にすることがプロの仕事です。」  
*(เข้าใจก็ดีแล้ว ใน Scoreboard คุณต้องตัดสินผลให้ได้ Bit-Exact Match 100% ทุกตัวอักษร หากพบ Mismatch แม้แต่จุดเดียว ต้องสั่ง `$fatal` เพื่อหยุด CI/CD Pipeline ทันที งานระดับมืออาชีพคือสคริปต์ต้องตัดสิน Pass/Fail ได้เองอัตโนมัติโดยที่มนุษย์ไม่ต้องเสียเวลามาเปิดดูรูปคลื่นครับ)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การออกแบบความลึกของ Scoreboard Queue ภายใต้ความผันผวนของ Pipeline Stall

ในการทดสอบโมดูล Image Filter 2D บน FPGA ที่มี Pipeline Latency พื้นฐาน $L_{base} = 8$ ไซเคิล  
ระบบนำเข้าพิกเซลด้วยอัตรา $1\text{ pixel/cycle}$ แต่ระบบปลายทางมีการส่งสัญญาณ Backpressure ($stall\_in = 1$) แบบสุ่มด้วยความน่าจะเป็น $P(stall) = 0.20$  
กำหนดให้ช่วงเวลาต่อเนื่องกันสูงสุดที่สัญญาณ $stall\_in$ สามารถค้างอยู่ที่ค่า $1$ คือ $Burst_{stall\_max} = 12$ ไซเคิล

หากเราต้องการออกแบบขนาดของคิวพักข้อมูลที่คาดหวังใน Scoreboard (`expected_queue`) เพื่อป้องกันปัญหา Queue Overflow ขณะรัน Simulation จำนวน 1,000,000 ทรานแซกชัน จงคำนวณหาขนาดความจุของคิวต่ำสุด ($Q_{min}$) ที่ต้องจัดสรรในหน่วยความจำ:

- **A)** $Q_{min} = 8$ รายการ
- **B)** $Q_{min} = 12$ รายการ
- **C)** $Q_{min} \ge L_{base} + Burst_{stall\_max} = 20$ รายการ
- **D)** $Q_{min} \ge 1,000,000$ รายการ

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: C) $Q_{min} \ge L_{base} + Burst_{stall\_max} = 20$ รายการ**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ในโครงสร้าง Scoreboard แบบ FIFO Queue:
   - ฝั่ง Driver ทำการคำนวณ Golden Model และผลัก Expected Transaction ($E$) เข้าสู่ `expected_queue` ทันทีที่ป้อนสัญญาณเข้าสู่ DUT
   - ฝั่ง Monitor จะทำการดึงข้อมูลออกจาก `expected_queue` ก็ต่อเมื่อ DUT ประมวลผลเสร็จและส่งสัญญาณ `valid_out = 1` ออกมา
2. จำนวนข้อมูลที่ค้างอยู่ในคิว (In-Flight Occupancy $N_{queue}(t)$) ณ เวลาใดๆ คือ:
   $$N_{queue}(t) = N_{pushed}(t) - N_{popped}(t)$$
3. ในสภาวะเลวร้ายที่สุด (Worst-Case Pipeline Jam):
   - ข้อมูลจำนวน $L_{base} = 8$ รายการ ได้ถูกป้อนเข้าสู่ Pipeline ของ DUT ไปแล้ว
   - ทันใดนั้น ปลายทางส่งสัญญาณ $stall\_in = 1$ ค้างยาวนานที่สุดเท่ากับ $Burst_{stall\_max} = 12$ ไซเคิล
   - หาก Driver ยังคงป้อนข้อมูลจนเต็ม Buffer ภายใน DUT อีก $Burst_{stall\_max}$ รายการโดยที่ไม่มีข้อมูลใดหลุดออกจากขาเอาต์พุตเลย ($N_{popped} = 0$)
   - ปริมาณข้อมูล In-Flight สูงสุดที่รอการตรวจสอบคือ:
     $$Q_{max} = L_{base} + Burst_{stall\_max} = 8 + 12 = 20 \text{ รายการ}$$
4. หากจัดสรรคิวน้อยกว่า 20 รายการ ตัวแปร Array ภายใน Testbench อาจเกิดสภาวะล้น หรือในกรณีที่ใช้ Mailbox ที่มี Bounded Size ตัว Driver จะถูกระงับ (Block) อย่างไม่ถูกต้อง ทำให้ไม่สามารถสร้าง Stress Traffic ทดสอบ DUT ได้อย่างแท้จริง

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** $8$ รายการ รองรับเฉพาะกรณีไม่มี Stall เท่านั้น หากเกิด Stall เพียง 1 ไซเคิล คิวจะเต็มทันที
- **ข้อ B ผิด:** $12$ รายการ ละเลยค่าคงที่ Pipeline Latency เดิมของวงจร
- **ข้อ D ผิด:** ไม่จำเป็นต้องจัดสรรถึง $1,000,000$ รายการ เพราะข้อมูลจะถูก Pop ออกไปเปรียบเทียบและทำลายทิ้งอย่างต่อเนื่องแบบ Rolling Window ไม่ได้เก็บสะสมไว้ตลอดกาล

---

### คำถามที่ 2: กลไกการตรวจจับ Out-of-Order Execution ในโครงสร้าง Scoreboard ขั้นสูง

หากโมดูลฮาร์ดแวร์ที่กำลังทดสอบคือ **Multi-Channel Arbiter / DMA Router** ซึ่งมีช่องทางนำเข้า 4 แชนเนล และข้อมูลที่เอาต์พุตอาจเดินทางออกมาสลับลำดับกัน (Out-of-Order) ขึ้นอยู่กับขนาดของแพ็กเก็ตและระดับความสำคัญ (Priority) โครงสร้างข้อมูลใดใน SystemVerilog ที่เหมาะสมที่สุดในการนำมาสร้างเป็น Scoreboard Storage แทนที่ FIFO Queue ปกติ เพื่อให้สามารถค้นหาและตรวจสอบได้อย่างมีประสิทธิภาพสูงสุด $O(1)$?

- **A)** Dynamic Array (`bit [31:0] mem[]`)
- **B)** Associative Array indexed by Transaction ID / Tag (`MacTransaction exp_table[int]`)
- **C)** Linked List (`std::list`)
- **D)** Fixed Multi-dimensional Unpacked Array (`bit [31:0] arr[1024][1024]`)

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) Associative Array indexed by Transaction ID / Tag (`MacTransaction exp_table[int]`)**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ในระบบที่ข้อมูลสามารถส่งออกสลับลำดับกันได้ (Out-of-Order Transactions) เช่น สถาปัตยกรรม AXI, PCIe, หรือ Network Packet Routers การใช้ FIFO Queue (`queue.pop_front()`) จะล้มเหลวทันที เพราะข้อมูลตัวที่ออกมาก่อนอาจไม่ใช่ข้อมูลตัวแรกที่ใส่เข้าไป
2. ทุกๆ Transaction ที่ถูกสร้างขึ้นจะมีแท็กระบุตัวตน (Unique ID / Transaction Tag)
3. การใช้ **Associative Array (ตารางความสัมพันธ์)**:
   ```systemverilog
   MacTransaction exp_table[int]; // Key คือ Transaction ID
   ```
   - เมื่อ Driver ส่งข้อมูล: ทำการบันทึกลงตาราง: `exp_table[tr.id] = tr;`
   - เมื่อ Monitor ได้รับข้อมูลที่มี `id = k`:
     - ตรวจสอบว่ามีคีย์นี้อยู่ในตารางหรือไม่: `if (exp_table.exists(k))`
     - ดึงข้อมูลออกมาเปรียบเทียบค่า
     - ทำการลบข้อมูลออกจากตารางเพื่อคืนหน่วยความจำ: `exp_table.delete(k);`
4. การทำงานของ Associative Array ใน SystemVerilog อิงบนโครงสร้าง Hash Table หรือ Balanced Binary Tree ทำให้มีความซับซ้อนในการค้นหาและลบอยู่ที่เฉลี่ย $O(1)$ หรือ $O(\log N)$ เหมาะอย่างยิ่งสำหรับ Out-of-Order Scoreboard

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** Dynamic Array ต้องระบุขนาดล่วงหน้า และการค้นหาแบบสุ่มต้องวนลูปกวาดทั้งอาเรย์ ($O(N)$) ทำให้ Simulation ช้าลงอย่างมหาศาล
- **ข้อ C ผิด:** SystemVerilog ไม่มีคลาส Linked List มาตรฐาน และประสิทธิภาพการค้นหาแย่ ($O(N)$)
- **ข้อ D ผิด:** สิ้นเปลือง Memory ใน RAM โดยเปล่าประโยชน์สำหรับแอดเดรสที่ไม่ได้ใช้งาน (Sparse Data)

---

### คำถามที่ 3: การคำนวณขอบเขตเวลาของ Deadlock Watchdog Timer ในระบบส่งถ่ายข้อมูลแบบ Burst

กำหนดให้ระบบสื่อสารความเร็วสูงส่งแพ็กเก็ตข้อมูลขนาดแปรผัน โดยมีพารามิเตอร์ดังนี้:
- ความถี่การทำงาน: $f_{clk} = 250\text{ MHz}$ ($T_{clk} = 4.0\text{ ns}$)
- ขนาดของแพ็กเก็ตสูงสุด: $Pkt_{max} = 1,518\text{ ไบต์}$
- ความกว้างของบัสข้อมูล: $W_{bus} = 32\text{ บิต}$ ($4\text{ ไบต์ต่อไซเคิล}$)
- ความล่าช้าสูงสุดในการสลับเฟรม (Inter-Packet Gap): $T_{gap\_max} = 96\text{ ไซเคิลคล็อก}$
- จำนวนแพ็กเก็ตที่ทดสอบใน 1 ชุดการทดลอง: $N_{pkts} = 500\text{ แพ็กเก็ต}$
- ค่าความเผื่อความปลอดภัยด้านความผันผวนของระบบ (Safety Overhead): $+25\%$

จงคำนวณหาจำนวนรอบสัญญาณนาฬิกาขั้นต่ำที่ต้องตั้งค่าให้กับ **Watchdog Timer ($Cycles_{watchdog}$)** ของทั้งการทดสอบ เพื่อไม่ให้เกิดปัญหา False Timeout (ตัวจับเวลาตัดจบก่อนที่การทดสอบตามปกติจะเสร็จสิ้น):

- **A)** $Cycles_{watchdog} \ge 189,750$ ไซเคิล ($\approx 0.759\text{ ms}$)
- **B)** $Cycles_{watchdog} \ge 297,500$ ไซเคิล ($\approx 1.190\text{ ms}$)
- **C)** $Cycles_{watchdog} \ge 415,000$ ไซเคิล ($\approx 1.660\text{ ms}$)
- **D)** $Cycles_{watchdog} \ge 600,000$ ไซเคิล ($\approx 2.400\text{ ms}$)

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) $Cycles_{watchdog} \ge 297,500$ ไซเคิล ($\approx 1.190\text{ ms}$)**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. คำนวณจำนวนไซเคิลคล็อกที่จำเป็นในการส่งถ่ายเนื้อหาข้อมูลของแพ็กเก็ตขนาดสูงสุด 1 แพ็กเก็ต:
   $$Cycles_{payload} = \left\lceil \frac{Pkt_{max}}{\text{Bytes per Cycle}} \right\rceil = \left\lceil \frac{1,518}{4} \right\rceil = \lceil 379.5 \rceil = 380\text{ ไซเคิล}$$
2. จำนวนไซเคิลคล็อกสูงสุดต่อ 1 แพ็กเก็ตเมื่อรวมช่วงเวลาว่างระหว่างเฟรม (Inter-Packet Gap):
   $$Cycles_{per\_pkt} = Cycles_{payload} + T_{gap\_max} = 380 + 96 = 476\text{ ไซเคิล/แพ็กเก็ต}$$
3. เวลาทางทฤษฎีในการส่งถ่ายข้อมูลทั้งหมด $N_{pkts} = 500$ แพ็กเก็ต:
   $$Cycles_{nominal} = N_{pkts} \times Cycles_{per\_pkt} = 500 \times 476 = 238,000\text{ ไซเคิล}$$
4. นำค่าความเผื่อความปลอดภัย Overhead $+25\%$ มาคำนวณเพื่อรองรับจังหวะ Pipeline Flush และ Reset:
   $$Cycles_{watchdog} = Cycles_{nominal} \times (1 + 0.25) = 238,000 \times 1.25 = 297,500\text{ ไซเคิล}$$
5. แปลงเป็นหน่วยเวลาจริง:
   $$t_{watchdog} = 297,500 \times 4.0\text{ ns} = 1,190,000\text{ ns} = 1.190\text{ ms}$$

ดังนั้น Watchdog Timer จะต้องตั้งไว้ไม่น้อยกว่า **297,500 ไซเคิล** เพื่อให้การทดสอบดำเนินไปจนจบโดยไม่ถูกตัดกลางคันจากกรณีการส่งข้อมูลปกติที่ใหญ่ที่สุด

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** $189,750$ ไซเคิล คำนวณเฉพาะส่วน Payload โดยลืมบวก Inter-Packet Gap ทำให้ Watchdog จะ Trigger ก่อนที่การทดสอบจะเสร็จสิ้น (False Alarm)
- **ข้อ C ผิด:** $415,000$ ไซเคิล คิดค่า Overhead สูงเกินจำเป็น ($\approx +74\%$)
- **ข้อ D ผิด:** $600,000$ ไซเคิล เป็นการประมาณการที่หลวมเกินไป ทำให้การค้นพบข้อผิดพลาดประเภท Deadlock ในระบบ CI/CD ต้องเสียเวลารอนานเกินความจำเป็น
