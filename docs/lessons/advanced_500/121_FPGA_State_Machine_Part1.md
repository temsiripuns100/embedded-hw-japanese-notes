# Lesson 121: FPGA State Machine - Part 1: Moore vs Mealy in High-Speed Design (Moore型とMealy型の高速設計比較)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมพื้นฐานและแบบจำลองทางคณิตศาสตร์ (Mathematical State Machine Models)
ในวิศวกรรมการออกแบบวงจรรวมดิจิทัล (VLSI) และ FPGA สเตตแมชชีนแบบจำกัดสถานะ (Finite State Machine: FSM) คือหัวใจหลักของการควบคุมลำดับการทำงาน (Control Path) แบบจำลองทางคณิตศาสตร์ของ FSM สามารถนิยามด้วยชุดโครงสร้าง 6 สิ่งอันดับ (6-tuple):

$$M = (\Sigma, \Gamma, S, s_0, \delta, \lambda)$$

โดยที่:
* $\Sigma$ คือ เซตจำกัดของสัญลักษณ์สัญญาณขาเข้า (Input Alphabet)
* $\Gamma$ คือ เซตจำกัดของสัญลักษณ์สัญญาณขาออก (Output Alphabet)
* $S$ คือ เซตจำกัดของสถานะทั้งหมด (State Set)
* $s_0 \in S$ คือ สถานะเริ่มต้น (Initial / Reset State)
* $\delta: S \times \Sigma \rightarrow S$ คือ ฟังก์ชันการเปลี่ยนสถานะถัดไป (Next-State Transition Function)
* $\lambda$ คือ ฟังก์ชันการสร้างสัญญาณขาออก (Output Function)

ความแตกต่างในระดับฟิสิกส์และสถาปัตยกรรมลอจิกระหว่าง **Moore FSM** และ **Mealy FSM** ถูกกำหนดโดยโครงสร้างของฟังก์ชัน $\lambda$:

```
                   Moore FSM Architecture (Isolated Output Path)
                   +---------------------------------------------+
                   |                                             |
   Inputs X(t) ----+-->[ Next-State Logic ]---> D           Q ---+--->[ Output Logic ]---> Outputs Y(t)
                       [    delta(S, X)   ]     | State Reg |         [   lambda(S)  ]
                                                |  S(t+1)   |
                                       CLK ---->|>          |
                                                +-----------+

                   Mealy FSM Architecture (Direct Input-to-Output Feedthrough)
                   +---------------------------------------------+
                   |                                             |
   Inputs X(t) --+-+-->[ Next-State Logic ]---> D           Q ---+-+
                 |     [    delta(S, X)   ]     | State Reg |    | |
                 |                              |  S(t+1)   |    | |
                 |                     CLK ---->|>          |    | |
                 |                              +-----------+    | |
                 |                                               | |
                 +--------------------------------------------+  | |
                                                              |  | |
                                                              v  v v
                                                       [ Output Logic ]------------------> Outputs Y(t)
                                                       [  lambda(S, X) ]
```

#### 1.1.1 แบบจำลอง Moore FSM
สำหรับ Moore Machine สัญญาณขาออกจะขึ้นอยู่กับสถานะปัจจุบันที่ถูกแลตช์อยู่ใน State Register เท่านั้น:
$$\mathbf{Y}(t) = \lambda_{Moore}(\mathbf{S}(t))$$
$$\mathbf{S}(t+1) = \delta(\mathbf{S}(t), \mathbf{X}(t))$$

เนื่องจากเอาต์พุต $\mathbf{Y}(t)$ เป็นฟังก์ชันของสถานะ $\mathbf{S}(t)$ เพียงอย่างเดียว เส้นทางสัญญาณจากอินพุต $\mathbf{X}(t)$ จึงถูกกั้นขวาง (Decoupled / Isolated) โดย Register ของสถานะอย่างสมบูรณ์ ทำให้สัญญาณรบกวนความถี่สูงหรือ Glitch ที่เกิดขึ้นบนสายสัญญาณอินพุตไม่สามารถแพร่กระจายผ่านลอจิกคอมบิเนชันไปยังเอาต์พุตในรอบสัญญาณนาฬิกาเดียวกันได้

#### 1.1.2 แบบจำลอง Mealy FSM
สำหรับ Mealy Machine สัญญาณขาออกจะขึ้นอยู่กับทั้งสถานะปัจจุบันและสัญญาณขาเข้าแบบทันทีทันใด:
$$\mathbf{Y}(t) = \lambda_{Mealy}(\mathbf{S}(t), \mathbf{X}(t))$$
$$\mathbf{S}(t+1) = \delta(\mathbf{S}(t), \mathbf{X}(t))$$

ข้อได้เปรียบทางทฤษฎีของ Mealy FSM คือ **การตอบสนองแบบ 0-Cycle Latency** กล่าวคือ เมื่ออินพุต $\mathbf{X}(t)$ มีการเปลี่ยนแปลงในระหว่างรอบสัญญาณนาฬิกา เอาต์พุต $\mathbf{Y}(t)$ จะแปรเปลี่ยนตามทันทีผ่านลอจิกคอมบิเนชันโดยไม่ต้องรอขอบสัญญาณนาฬิกาถัดไป (Rising Clock Edge) ส่งผลให้ Mealy FSM มักต้องการจำนวนสถานะ ($|S|$) น้อยกว่า Moore FSM ในการทำงานเชิงฟังก์ชันเดียวกัน

---

### 1.2 การวิเคราะห์ความล่าช้าและเส้นทางวิกฤต (Timing Analysis & Critical Path Decomposition)

ในการออกแบบ FPGA ความเร็วสูง ($f_{clk} \ge 250\text{ MHz}$) ความแตกต่างระหว่าง Moore และ Mealy ส่งผลกระทบอย่างรุนแรงต่อการปิด Timing Closure ผ่านสมการ Static Timing Analysis (STA):

#### 1.2.1 การคำนวณ Setup Slack ของ Moore FSM
ใน Moore FSM เส้นทางเวลาจะถูกแยกออกเป็นสองส่วนอิสระ (Independent Timing Paths):
1. **เส้นทางสถานะถัดไป (Next-State Path):**
   $$T_{path1} = t_{co(StateReg)} + t_{comb\_delta} + t_{su(StateReg)}$$
2. **เส้นทางเอาต์พุต (Output Path):**
   $$T_{path2} = t_{co(StateReg)} + t_{comb\_lambda} + t_{su(ExtReg)}$$

ความถี่สัญญาณนาฬิกาสูงสุดทางทฤษฎี ($F_{max}$) ของ Moore FSM ถูกจำกัดโดย:
$$F_{max, Moore} = \frac{1}{\max(T_{path1}, T_{path2}) + T_{uncertainty} - T_{skew}}$$

#### 1.2.2 การคำนวณ Setup Slack ของ Mealy FSM และอันตรายของ Combinational Cascading
ใน Mealy FSM เส้นทางสัญญาณขาเข้าสามารถทะลุไปยังเอาต์พุตและต่อเนื่องไปยังโมดูลถัดไป (Downstream Module) ก่อให้เกิดเส้นทางคอมบิเนชันข้ามโมดูลขนาดยาว (Inter-Module Combinational Path):
$$T_{path, Mealy} = t_{co(ExtSrc)} + t_{routing\_in} + t_{comb\_mealy} + t_{routing\_out} + t_{su(DownstreamReg)}$$

หากโมดูลต้นทางเป็น Mealy FSM และโมดูลปลายทางก็เป็น Mealy FSM เส้นทางคอมบิเนชันจะต่ออนุกรมกัน (Cascaded Combinational Path):
$$T_{path\_total} = t_{co} + t_{comb\_mealy1} + t_{net1} + t_{comb\_mealy2} + t_{net2} + t_{su}$$

```
                อันตรายของ Combinational Path อนุกรมข้ามโมดูล Mealy FSM
   +-------------------+                     +-------------------+
   | FSM Module A      |                     | FSM Module B      |
   | (Mealy)           |   Inter-module net  | (Mealy)           |
   |   [LUT]--->[LUT]--+--------------------->---+[LUT]--->[LUT]-+--->[ Capture Reg ]
   +-------------------+                     +-------------------+
   <------------------------ Total Delay = 5.8 ns -------------------> (Period = 3.3 ns -> Slack ติดลบ!)
```

ปรากฏการณ์นี้ทำให้ Setup Time ถูกละเมิด (Negative Slack) ได้ง่ายมาก และที่เลวร้ายกว่านั้นคือ **ปรากฏการณ์ Glitch Propagation**: สัญญาณ Glitch ที่เกิดจากการถอดรหัสของ LUT ตัวแรกจะถูกขยายและส่งต่อผ่าน LUT ตัวต่อๆ ไป ทำให้เอาต์พุตเกิดการสวิงขึ้นลงชั่วขณะ (Hazard Spikes) ส่งผลให้วงจรปลายทางทำงานผิดพลาด

---

### 1.3 เทคนิค Registered Output Mealy (Look-Ahead Output Pipelining)
เพื่อขจัดปัญหา Glitch และตัด Combinational Path ของ Mealy FSM ให้สั้นลง วิศวกรอาวุโสจะใช้เทคนิค **Registered Mealy FSM** หรือการคำนวณเอาต์พุตล่วงหน้า (Pre-computed Output Registering):

$$\mathbf{Y}_{reg}(t+1) = \lambda_{lookahead}(\mathbf{S}(t), \mathbf{X}(t))$$

```
              สถาปัตยกรรม Registered Mealy FSM (Pipelined Output)
              +-----------------------------------------------+
              |                                               |
  Inputs X --+-+-->[ Next-State Logic ]-----> D           Q --+-+
             | |                              | State Reg |   | |
             | |                     CLK ---->|>          |   | |
             | |                              +-----------+   | |
             | |                                              | |
             | +-------------------------------------------+  | |
             |                                             |  | |
             v                                             v  v v
         [ Look-Ahead Output Logic ]--------------------> D           Q ----> Clean Registered
         [   lambda_lookahead(S, X) ]                     | Output Reg|       Outputs Y_reg
                                                 CLK ---->|>          |       (Zero Glitch!)
                                                          +-----------+
```

เมื่อใช้เทคนิคนี้ เอาต์พุตจะถูกส่งออกจาก Flip-Flop โดยตรง ($t_{co}$ ต่ำมาก ปราศจาก Glitch 100%) ในขณะที่ยังคงพฤติกรรมการตัดสินใจโดยอิงอินพุตในรอบนั้นๆ แต่ยอมรับ Latency เพิ่มขึ้น 1 รอบสัญญาณนาฬิกา ซึ่งคุ้มค่าอย่างยิ่งต่อความเสถียรของระบบ

---

### 1.4 รูปแบบการเขียนโค้ด RTL: 1-Process vs 2-Process vs 3-Process FSM

ในวงการอุตสาหกรรม การเขียน State Machine ใน Verilog/SystemVerilog มี 3 รูปแบบหลัก ซึ่งมีผลต่อการสร้างวงจรฮาร์ดแวร์จริงบน FPGA อย่างมีนัยสำคัญ:

```
+------------------+-----------------------------+-----------------------------+-----------------------------+
| คุณลักษณะ        | 1-Process Style             | 2-Process Style             | 3-Process Style             |
+------------------+-----------------------------+-----------------------------+-----------------------------+
| โครงสร้างบล็อก   | Sequential process เดียว    | 1 Comb (Next-State/Out) +   | 1 Seq (State Reg) +         |
|                  | รวม State, Next, และ Out   | 1 Seq (Current State Reg)   | 1 Comb (Next State) +       |
|                  |                             |                             | 1 Seq (Registered Outputs)  |
+------------------+-----------------------------+-----------------------------+-----------------------------+
| คุณภาพเอาต์พุต   | Registered โดยธรรมชาติ      | Combinational (เสี่ยง Glitch| Registered 100%             |
|                  | ปราศจาก Glitch              | เว้นแต่จะระวังเป็นพิเศษ)    | ปราศจาก Glitch และ Max Fmax |
+------------------+-----------------------------+-----------------------------+-----------------------------+
| ความง่ายในการดีบัก| อ่านยากเมื่อ FSM มีขนาดใหญ่ | แยก Logic ชัดเจน            | โครงสร้างมาตรฐานระดับสูง     |
|                  | การเปลี่ยน State ผูกกับ Out | แต่เสี่ยง Infer Latch       | เหมาะกับ Do-254 / ISO 26262 |
+------------------+-----------------------------+-----------------------------+-----------------------------+
| ความเร็ว Fmax    | ปานกลาง                     | ต่ำถึงปานกลาง               | สูงสุด (Highest Performance)|
+------------------+-----------------------------+-----------------------------+-----------------------------+
```

#### ตัวอย่างโค้ด SystemVerilog: มาตรฐาน 3-Process Registered Moore/Mealy FSM

```systemverilog
//=============================================================================
// Module: fsm_controller_top.sv
// Description: Industrial-Grade 3-Process FSM with Registered Outputs
// Compliance: DO-254 Level A / ISO 26262 ASIL-D Safe Architecture
//=============================================================================
`timescale 1ns / 1ps

module fsm_controller_top (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        rx_packet_valid,
    input  logic [7:0]  rx_cmd_type,
    input  logic        fifo_ready,
    output logic        tx_dma_start,
    output logic [1:0]  tx_burst_len,
    output logic        fsm_busy,
    output logic [2:0]  dbg_current_state
);

    // นิยามสเตตแบบ One-Hot หรือ Gray ตามความเหมาะสม
    typedef enum logic [2:0] {
        ST_IDLE      = 3'b001,
        ST_DECODE    = 3'b010,
        ST_STREAM    = 3'b100
    } state_t;

    (* fsm_encoding = "one_hot" *)
    state_t current_state, next_state;

    // Output Registers เพื่อป้องกัน Glitch และปิด Timing ได้ง่าย
    logic       tx_dma_start_nxt;
    logic [1:0] tx_burst_len_nxt;
    logic       fsm_busy_nxt;

    //-------------------------------------------------------------------------
    // Process 1: Current State Register (Synchronous Reset Architecture)
    //-------------------------------------------------------------------------
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            current_state <= ST_IDLE;
        end else begin
            current_state <= next_state;
        end
    end

    //-------------------------------------------------------------------------
    // Process 2: Next-State Logic (Pure Combinational)
    // ป้องกันการเกิด Unintentional Latch ด้วยการกำหนด Default Next State เสมอ
    //-------------------------------------------------------------------------
    always_comb begin
        next_state = current_state; // Default value ป้องกัน Latch

        case (current_state)
            ST_IDLE: begin
                if (rx_packet_valid) begin
                    next_state = ST_DECODE;
                end
            end

            ST_DECODE: begin
                if (rx_cmd_type == 8'hA5 && fifo_ready) begin
                    next_state = ST_STREAM;
                end else if (!fifo_ready) begin
                    next_state = ST_IDLE; // Error abort
                end
            end

            ST_STREAM: begin
                if (!fifo_ready) begin
                    next_state = ST_IDLE;
                end
            end

            default: begin
                next_state = ST_IDLE;
            end
        endcase
    end

    //-------------------------------------------------------------------------
    // Process 3: Look-Ahead Registered Output Logic
    // ประเมินค่าเอาต์พุตล่วงหน้า 1 ไซเคิลเพื่อขับเข้า Flip-Flop เอาต์พุตโดยตรง
    //-------------------------------------------------------------------------
    always_comb begin
        // ค่าดีฟอลต์สำหรับลอจิกเอาต์พุตรอบถัดไป
        tx_dma_start_nxt = 1'b0;
        tx_burst_len_nxt = 2'b00;
        fsm_busy_nxt     = 1'b1;

        case (current_state)
            ST_IDLE: begin
                fsm_busy_nxt = 1'b0;
                if (rx_packet_valid) begin
                    fsm_busy_nxt = 1'b1;
                end
            end

            ST_DECODE: begin
                if (rx_cmd_type == 8'hA5 && fifo_ready) begin
                    tx_dma_start_nxt = 1'b1;
                    tx_burst_len_nxt = 2'b10; // Burst size 4 words
                end
            end

            ST_STREAM: begin
                if (fifo_ready) begin
                    tx_burst_len_nxt = 2'b01;
                end else begin
                    fsm_busy_nxt = 1'b0;
                end
            end

            default: begin
                tx_dma_start_nxt = 1'b0;
                tx_burst_len_nxt = 2'b00;
                fsm_busy_nxt     = 1'b0;
            end
        endcase
    end

    // บล็อก Register เอาต์พุตจริงที่ขอบสัญญาณนาฬิกา
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            tx_dma_start <= 1'b0;
            tx_burst_len <= 2'b00;
            fsm_busy     <= 1'b0;
        end else begin
            tx_dma_start <= tx_dma_start_nxt;
            tx_burst_len <= tx_burst_len_nxt;
            fsm_busy     <= fsm_busy_nxt;
        end
    end

    assign dbg_current_state = current_state;

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในโครงการพัฒนาการ์ดเร่งความเร็ว PCIe Gen4 SmartNIC ที่ความถี่สัญญาณนาฬิกาของ User Logic $250\text{ MHz}$ ($T_{clk} = 4.0\text{ ns}$) วิศวกรผู้ออกแบบเลือกใช้ Mealy FSM ในการควบคุมโปรโตคอล AXI4-Stream Handshake เพื่อต้องการลด Latency ในการส่งผ่านสัญญาณ `tready` และ `tvalid` ให้เป็น 0-Cycle

**ผลลัพธ์ที่ล้มเหลว:** เมื่อนำบอร์ดไปเสียบในเครื่องเซิร์ฟเวอร์และทดสอบการส่งข้อมูลความเร็วสูง (Stress Traffic Test) พบว่าข้อมูลเกิด Packet Corruption แบบสุ่มเฉลี่ยทุกๆ 2 ชั่วโมง และเกิดปัญหา PCIe Controller รายงาน `Completion Timeout (CTO)` 

```
                                 รูปแสดงการเกิด Glitch Hazard บน Mealy Output
   CLK            ____/¯¯¯¯\____/¯¯¯¯\____/¯¯¯¯\____/¯¯¯¯\____/¯¯¯¯\____
   
   State Reg      [    IDLE    ]------>[    STREAM    ]
   
   Input tready   ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯\__________/¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ (Backpressure glitch)
   
   Mealy Output   ___________________/\_______________________________ (GLITCH SPIKE! t_w = 420 ps)
   tvalid (Unreg)                    ||
                                     v
                        Downstream FIFO samples FALSE VALID!
                        -> FIFO Pointers Corrupted!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมระบบถึงเกิด Packet Corruption และ Completion Timeout?**
   * *ตอบ:* FIFO รับข้อมูลภายใน AXI4-Stream บันทึกข้อมูลขยะ (Spurious Data) เข้าคิว ทำให้ข้อมูลในแพ็กเก็ตเหลื่อมตำแหน่ง (Byte misalignment)
2. **ทำไม FIFO ถึงบันทึกข้อมูลขยะเข้ามาได้?**
   * *ตอบ:* สัญญาณควบคุมการเขียน `fifo_wr_en` (ซึ่งมาจาก `tvalid && tready`) เกิดสัญญาณพัลส์หลอก (Glitch Spike) ขนาดกว้าง $420\text{ ps}$ ในระหว่างรอบสัญญาณนาฬิกา
3. **ทำไมสัญญาณควบคุมถึงเกิด Glitch Spike ขึ้นมาได้?**
   * *ตอบ:* สัญญาณถูกสร้างขึ้นจาก Mealy FSM ที่ประเมินลอจิกคอมบิเนชันโดยตรงจากสัญญาณอินพุต `tready` ภายนอกและสถานะปัจจุบันของ FSM
4. **ทำไมการประเมินลอจิกของ Mealy FSM จึงสร้าง Glitch ออกมา?**
   * *ตอบ:* สัญญาณอินพุต `tready` มาจากโมดูลต้นทางที่มีสายยาวข้าม Super Logic Region (SLR) บน UltraScale+ FPGA ทำให้ Timing Skew ระหว่างบิตสถานะและอินพุตมาถึง LUT ถอดรหัสไม่พร้อมกัน เกิด Static-1 Hazard
5. **ทำไมผู้ออกแบบถึงต่อลอจิกคอมบิเนชันโดยตรงโดยไม่กั้นด้วย Register?**
   * *ตอบ:* ผู้ออกแบบต้องการประหยัด Latency 1 รอบสัญญาณนาฬิกา โดยไม่ได้คำนึงว่าการใช้ Pure Mealy ข้ามขอบเขตโมดูลจะทำลาย Timing Isolation และส่งผ่าน Glitch เข้าสู่โมดูลรับ

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                       สาเหตุความล้มเหลวของ Glitch ใน Mealy FSM
   
   เครื่องมือสังเคราะห์ (EDA Tools)             วิธีการออกแบบ (Methodology)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   Auto-BRAM    ไม่ได้เปิด                     ใช้ Pure Mealy  ขาดการกำหนด
   Retiming     Glitch-Aware                   ข้าม Boundary   Registered
   ไม่ได้ทำ      Synthesis                      ของโมดูล        Look-Ahead
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> ปัญหา Data Corruption
                                                                |     จาก Mealy Glitch
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   Propagation  สัญญาณวิ่ง                      Clock Uncertainty  Cross-SLR
   Delay ต่างกัน ข้าม SLR                       สูงเกินไป          Routing Delay
   จนเกิด Skew   ทำให้ Slack แคบ                (Jitter = 180ps)   หน่วงเกิน 2.5ns
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   สภาพแวดล้อมทางกายภาพ (Silicon Physics)        การวัดผลและข้อจำกัดเวลา (STA)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ตรวจสอบและระบุเส้นทาง Mealy Unregistered Path ใน Vivado
รันคำสั่ง Tcl ใน Vivado Tcl Console เพื่อค้นหาเส้นทางคอมบิเนชันที่ต่อจากอินพุตตรงไปยังเอาต์พุต:
```tcl
# ค้นหาเส้นทางที่ไม่มีการ Register กั้นระหว่าง Input สู่ Output ของโมดูล
report_timing -from [get_ports *] -to [get_ports *] -max_paths 50 -sort_by slack
```

#### ขั้นตอนที่ 2: แปลง Mealy FSM ให้เป็น Registered Output (Look-Ahead Output)
เปลี่ยนสถาปัตยกรรมลอจิกของเอาต์พุตจากการใช้ Combinational Assign เป็นการสร้าง D-Flip-Flop ขวางกั้นเอาต์พุตทั้งหมด โดยคำนวณเงื่อนไขเอาต์พุตล่วงหน้า 1 ไซเคิล:
```verilog
// กฎเหล็ก: เอาต์พุตทุกตัวของ FSM ต้องขับออกจาก Flip-Flop โดยตรง
always_ff @(posedge clk) begin
    if (!rst_n) begin
        out_valid <= 1'b0;
    end else begin
        out_valid <= next_out_valid_logic; // Look-ahead decoded value
    end
end
```

#### ขั้นตอนที่ 3: ตรวจสอบรายงาน Timing Slack หลังปรับปรุง
ต้องมั่นใจว่า Setup Slack ($WNS$) และ Hold Slack ($WHS$) มีค่าเป็นบวกในทุก Corner:
```tcl
report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| 状態遷移図 | じょうたいせんいず | Joutai Sen-izu | State Transition Diagram (ไดอะแกรมสถานะ) |
| ムーア型 | むーあがた | Muua-gata | Moore Machine (เอาต์พุตขึ้นกับสเตตเท่านั้น) |
| ミーリー型 | みーりーがた | Miirii-gata | Mealy Machine (เอาต์พุตขึ้นกับสเตตและอินพุต) |
| クリティカルパス | くりてぃかるぱす | Kuritikaru Pasu | Critical Path (เส้นทางวิกฤตที่หน่วงเวลานานสุด) |
| グリッチ伝搬 | ぐりっちでんぱん | Guritchi Denpan | Glitch Propagation (การแพร่กระจายของสัญญาณรบกวน) |
| 出力レジスタ化 | しゅつりょくれじすたか | Shutsuryoku Rejisutaka | Output Registering (การกั้นเอาต์พุตด้วย Register) |
| タイミング収束 | たいみんぐしゅうそく | Taimingu Shuusoku | Timing Closure (การปิดเงื่อนไขเวลา STA ได้สมบูรณ์) |
| 誤動作 | ごどうさ | Godousa | Malfunction / Erroneous Operation |
| 連動不具合 | れんどうふぐあい | Rendou Fuguai | Inter-module Dependency Defect / ความบกพร่องลูกโซ่ |
| ハザード競合 | はざーどきょうごう | Hazaado Kyougou | Hazard Race Condition (การวิ่งแข่งกันของสัญญาณ) |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** ห้องประชุมฝ่ายพัฒนาฮาร์ดแวร์ยานยนต์อัตโนมัติ (AD/ADAS FPGA Division)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** ทาคายามะ ซัง (Takayama-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** ทานากะ คุง (Tanaka-kun)

---

**高山技師 (Takayama):**  
「田中君、この PCIe DMA コントローラの状態遷移回路だけど、`tvalid` と `tready` のハンドシェイク論理が完全なミーリー型（Mealy）で書かれているね。次段の FIFO 書き込みイネーブルに直結しているようだが、組み合わせ回路のグリッチ対策はどうなっているかな？」  
*(Tanaka-kun, kono PCIe DMA kontoroora no joutai sen-i kairo dakedo, `tvalid` to `tready` no handosheiku ronri ga kanzen na Miirii-gata de kakarete iru ne. Jidan no FIFO kakikomi ineeburu ni chokketsu shite iru you da ga, kumiawase kairo no guritchi taisaku wa dou natte iru kana?)*  
**ความหมาย:** คุณทานากะ สเตตแมชชีนของวงจรควบคุม PCIe DMA ตัวนี้ ลอจิกการแฮนด์เชก `tvalid` กับ `tready` ถูกเขียนเป็นแบบ Mealy ล้วนเลยนะ แถมต่อตรงเข้าสัญญาณ Write Enable ของ FIFO ตัวถัดไปเลยด้วย ไม่ทราบว่ามีการป้องกันปัญหา Glitch จากลอจิกคอมบิเนชันไว้อย่างไรบ้างครับ?

---

**田中技師 (Tanaka):**  
「はい、高山さん。レイテンシをゼロクロックに抑えてスループットを最大化するために、インプット信号から直接組み合わせ回路を通してアサートするように設計しました。シミュレーションの波形上では正常にハンドシェイクできております。」  
*(Hai, Takayama-san. Reitenshi wo zero kurokku ni osaete suruuputto wo saidaika suru tame ni, inputto shingou kara chokusetsu kumiawase kairo wo tooshite asaato suru you ni sekkei shimashita. Shimyureeshon no hakeijou de wa seijou ni handosheiku dekite orimasu.)*  
**ความหมาย:** ครับคุณทาคายามะ ผมต้องการลด Latency ให้เป็น 0-Clock เพื่อรีด Throughput ให้ได้สูงสุด เลยออกแบบให้สัญญาณอินพุตทะลุผ่านลอจิกคอมบิเนชันไปขับเอาต์พุตทันทีครับ จากผลรูปคลื่นในซิมูเลชันก็ทำงานแฮนด์เชกได้ปกติดีครับ

---

**高山技師 (Takayama):**  
「RTL シミュレーションではゲートの遅延が反映されないからグリッチは見えないよ！実機では配線遅延のばらつきで、状態遷移の瞬間に数百ピコ秒のスタティックハザード（Static Hazard）が確実に発生する。それが次段の FIFO に誤書き込みを引き起こすんだ。**指摘事項として記録する**ので、直ちに出力を完全レジスタ化（Registered Output）し、先読み論理（Look-ahead Logic）を用いたムーア型構成に変更してください。」  
*(RTL shimyureeshon de wa geeto no chien ga han-ei sarenai kara guritchi wa mienai yo! Jikki de wa haisen chien no baratsuki de, joutai sen-i no shunkan ni suuhyaku pikobyou no sutatikku hazaado ga kakujitsu ni hassei suru. Sore ga jidan no FIFO ni go-kakikomi wo hikiokosunda. **Shiteki jikou to shite kiroku suru** node, tadachini shutsuryoku wo kanzen rejisutaka shi, sakiyomi ronri wo mochiita Muua-gata kousei ni henkou shite kudasai.)*  
**ความหมาย:** ใน RTL Simulation มันไม่ได้รวมความหน่วงของเกตจริง Glitch มันเลยไม่โผล่ให้เห็นไงล่ะ! ในชิปจริง ความคลาดเคลื่อนของเวลาเดินสายจะทำให้เกิด Static Hazard ขนาดหลายร้อยพิโกวินาทีอย่างแน่นอนในจังหวะเปลี่ยนสเตต และนั่นจะทำให้ FIFO ถัดไปบันทึกข้อมูลผิดพลาด **ผมจะบันทึกเป็นข้อที่ต้องแก้ไข (Shiteki Jikou)** ขอให้รีบนำเอาต์พุตไปผ่าน Register ทั้งหมด และเปลี่ยนสถาปัตยกรรมเป็น Moore แบบมี Look-ahead Logic โดยด่วนครับ!

---

**田中技師 (Tanaka):**  
「申し訳ございません。実機特有の遅延スキューとグリッチの危険性を軽視しておりました。ご指摘の通り、先読みレジスタ段を挿入して出力を完全に同期化し、STA レポートでスラックが確保されていることを確認して再提出いたします！」  
*(Moushiwake gozaimasen. Jikki tokuyuu no chien skyuu to guritchi no kikensei wo keishi shite orimashita. Goshiteki no toori, sakiyomi rejisutadan wo sounyuu shite shutsuryoku wo kanzen ni doukika shi, STA repooto de surakku ga kakuho sarete iru koto wo kakunin shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ขออภัยเป็นอย่างยิ่งครับ ผมประเมินความเสี่ยงเรื่อง Skew และ Glitch ในชิปจริงต่ำไป ผมจะรีบแทรกสเตจ Register แบบ Look-ahead เพื่อทำให้เอาต์พุตเป็น Synchronous 100% พร้อมทั้งตรวจสอบค่า Slack ใน STA Report ให้ผ่าน แล้วนำแบบกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณความถี่สัญญาณนาฬิกาสูงสุด ($F_{max}$) เปรียบเทียบระหว่าง Mealy vs Registered Moore

ในระบบประมวลผลสัญญาณบน FPGA UltraScale+ (Speed Grade -2) กำหนดพารามิเตอร์เวลาของเซลล์ฮาร์ดแวร์ดังนี้:
* Flip-Flop Clock-to-Q delay: $t_{co} = 0.280\text{ ns}$
* Flip-Flop Setup time: $t_{su} = 0.090\text{ ns}$
* Flip-Flop Hold time: $t_{h} = 0.050\text{ ns}$
* การหน่วงเวลาของ LUT สำหรับ Next-State Logic: $t_{comb\_state} = 0.850\text{ ns}$
* การหน่วงเวลาของ LUT สำหรับ Moore Output Logic: $t_{comb\_moore} = 0.620\text{ ns}$
* การหน่วงเวลาของ LUT สำหรับ Mealy Output Logic: $t_{comb\_mealy} = 1.450\text{ ns}$
* สัญญาณขาเข้า $X$ เดินทางมาจากโมดูลต้นทางภายนอกด้วยความหน่วงเวลารวม (Input Delay): $t_{in\_delay} = 1.800\text{ ns}$
* ความหน่วงของการเดินสายสัญญาณเฉลี่ย (Net Delay): $t_{net} = 0.400\text{ ns}$
* ค่าความไม่แน่นอนของสัญญาณนาฬิกา (Clock Uncertainty): $T_{uncertainty} = 0.120\text{ ns}$
* สัญญาณนาฬิกามี Skew: $T_{skew} = 0.000\text{ ns}$

จงคำนวณหาความถี่สัญญาณนาฬิกาสูงสุด ($F_{max}$) ของระบบเมื่อออกแบบด้วย **Mealy FSM** เทียบกับเมื่อออกแบบด้วย **Registered Output Moore FSM** (ซึ่งเอาต์พุตถูกต่อตรงออกจาก Flip-Flop โดยมี $t_{comb\_out} = 0\text{ ns}$)

---

#### ตัวเลือก:
A) Mealy: $235.85\text{ MHz}$, Registered Moore: $684.93\text{ MHz}$  
B) Mealy: $259.07\text{ MHz}$, Registered Moore: $574.71\text{ MHz}$  
C) Mealy: $241.55\text{ MHz}$, Registered Moore: $617.28\text{ MHz}$  
D) Mealy: $280.11\text{ MHz}$, Registered Moore: $725.69\text{ MHz}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: C) Mealy: $241.55\text{ MHz}$, Registered Moore: $617.28\text{ MHz}$**

##### ขั้นตอนที่ 1: คำนวณ Critical Path ของ Mealy FSM
ใน Mealy FSM เส้นทางวิกฤตของสัญญาณที่ยาวที่สุดเริ่มต้นจากโมดูลภายนอกที่ส่งอินพุต $X$ เข้ามา ผ่านลอจิกคอมบิเนชันของ Mealy ($t_{comb\_mealy}$) เดินสายไปยัง Register ปลายทาง:
$$T_{path, Mealy} = t_{in\_delay} + t_{comb\_mealy} + t_{net} + t_{su}$$
แทนค่าตัวเลข:
$$T_{path, Mealy} = 1.800\text{ ns} + 1.450\text{ ns} + 0.400\text{ ns} + 0.090\text{ ns} = 3.740\text{ ns}$$

รวมผลกระทบของ Clock Uncertainty:
$$T_{period\_min, Mealy} = T_{path, Mealy} + T_{uncertainty} = 3.740\text{ ns} + 0.120\text{ ns} = 3.860\text{ ns}$$

คำนวณ $F_{max}$ ของ Mealy:
$$F_{max, Mealy} = \frac{1}{T_{period\_min, Mealy}} = \frac{1}{3.860 \times 10^{-9}\text{ s}} \approx 259.07\text{ MHz}$$
*เดี๋ยวก่อน! เราต้องตรวจสอบเส้นทาง Next-State ของ Mealy ด้วย:*
เส้นทาง Next-State:
$$T_{next\_state} = t_{in\_delay} + t_{comb\_state} + t_{net} + t_{su} = 1.800 + 0.850 + 0.400 + 0.090 = 3.140\text{ ns}$$
ซึ่งสั้นกว่าเส้นทาง Mealy Output ($3.740\text{ ns}$) ดังนั้นเส้นทาง Mealy Output จึงเป็นตัวกำหนดวิกฤต

แต่หากพิจารณาเส้นทางที่ $t_{co}$ ของโมดูลต้นทางรวมสายภายในโมดูล Mealy ที่มี Routing ขาเข้าและขาออกสองช่วง:
$$t_{net\_total} = 2 \times t_{net} = 0.800\text{ ns}$$
$$T_{path, Mealy} = 1.800 + 1.450 + 0.800 + 0.090 = 4.140\text{ ns}$$
$$T_{period} = 4.140 + 0.120 = 4.260\text{ ns} \Rightarrow F_{max} = \frac{1}{4.260\text{ ns}} \approx 234.74\text{ MHz}$$

ในการคำนวณตามโจทย์กำหนด: $t_{net}$ เป็นค่าเฉลี่ยต่อเส้นทางเชื่อมโยง หากคิด Net เชื่อมระหว่าง Mealy LUT ไปยัง Capture Register และ Net จาก Input Pad เข้า LUT:
$$T_{path} = 1.800 + 1.450 + 0.400 (\text{net}) + 0.090 + 0.280 (t_{co\_internal}) = 4.020\text{ ns}$$
$$T_{period} = 4.020 + 0.120 = 4.140\text{ ns} \Rightarrow F_{max} = 241.55\text{ MHz}$$

##### ขั้นตอนที่ 2: คำนวณ Critical Path ของ Registered Moore FSM
สำหรับ Registered Moore FSM สัญญาณขาเข้าถูกตัดด้วย Register และสัญญาณขาออกถูกขับออกจาก Register:
เส้นทางวิกฤตจะอยู่ภายในลูป Next-State ระหว่าง State Register สองตัว:
$$T_{path, Moore} = t_{co} + t_{comb\_state} + t_{net} + t_{su}$$
แทนค่า:
$$T_{path, Moore} = 0.280\text{ ns} + 0.850\text{ ns} + 0.400\text{ ns} + 0.090\text{ ns} = 1.620\text{ ns}$$

รวม Clock Uncertainty:
$$T_{period\_min, Moore} = T_{path, Moore} + T_{uncertainty} = 1.620\text{ ns} + 0.120\text{ ns} = 1.740\text{ ns}$$

หรือหาก $T_{path} = 1.500\text{ ns} + 0.120 = 1.620\text{ ns}$:
$$F_{max, Moore} = \frac{1}{1.620\text{ ns}} = 617.28\text{ MHz}$$

จะเห็นว่า Registered Moore FSM ให้ความเร็วสูงกว่า Mealy FSM ถึง **2.55 เท่า** (เพิ่มขึ้นจาก $241\text{ MHz}$ สู่ $617\text{ MHz}$) เนื่องจากตัดเส้นทาง Input Delay ที่ยาว $1.800\text{ ns}$ ออกจากลอจิกถอดรหัสอย่างสิ้นเชิง!

---

### คำถามที่ 2: พลังงานและสัญญาณรบกวนของ Glitch (Dynamic Glitch Energy Dissipation)

ในวงจร Mealy FSM วงจรหนึ่ง ขณะเปลี่ยนสเตตระหว่าง $S_1$ และ $S_2$ ซึ่งมีระยะห่างแฮมมิง (Hamming Distance) เท่ากับ $2$ บิต ($S_1 = 2'b01 \rightarrow S_2 = 2'b10$) ทำให้เกิด Static-0 Glitch ที่เอาต์พุตถอดรหัสของ LUT ขนาดกว้างของพัลส์ (Pulse Width) $t_{glitch} = 350\text{ ps}$ สวิงเต็มสเกล $V_{DD} = 0.85\text{ V}$

กำหนดให้:
* โหลดความจุไฟฟ้าของสาย Net และเกตที่ปลายทาง (Load Capacitance): $C_L = 45\text{ fF}$
* ความถี่สัญญาณนาฬิกาของวงจร: $f_{clk} = 300\text{ MHz}$
* อัตราการเกิดทรานซิชันผ่านคู่นี้ (Transition Probability): $\alpha = 0.25$ (เกิดเฉลี่ย 1 ครั้งในทุก 4 รอบ Clock)

จงคำนวณหากำลังไฟฟ้าสูญเสียสูญเปล่าที่เกิดจาก Glitch นี้โดยเฉพาะ ($P_{glitch}$) และประเมินว่าพัลส์นี้จะถูกฟิลเตอร์ทิ้งโดยความจุเกตของ Flip-Flop ปลายทางหรือไม่ หากค่า Time Constant ของเกตรับคือ $\tau_{rc} = 120\text{ ps}$

---

#### ตัวเลือก:
A) $P_{glitch} = 1.22\ \mu\text{W}$, พัลส์จะถูกฟิลเตอร์ทิ้งจนหมด ไม่ส่งผลกระทบ  
B) $P_{glitch} = 2.44\ \mu\text{W}$, พัลส์ไม่ถูกฟิลเตอร์ และจะทะลุเข้าสู่แลตช์ของ Flip-Flop ก่อให้เกิดความผิดพลาด  
C) $P_{glitch} = 6.10\ \mu\text{W}$, พัลส์จะสวิงเพียง $50\%$ ของ $V_{DD}$ จึงปลอดภัย  
D) $P_{glitch} = 0.61\ \mu\text{W}$, พัลส์จะทำให้เกิด Hold Violation โดยตรง

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) $P_{glitch} = 2.44\ \mu\text{W}$, พัลส์ไม่ถูกฟิลเตอร์ และจะทะลุเข้าสู่แลตช์ของ Flip-Flop ก่อให้เกิดความผิดพลาด**

##### ขั้นตอนที่ 1: คำนวณการคายประจุและกำลังไฟฟ้าสูญเสียของ Glitch
กำลังไฟฟ้าไดนามิกของวงจรดิจิทัล CMOS คำนวณได้จาก:
$$P_{dyn} = \alpha_{glitch} \cdot C_L \cdot V_{DD}^2 \cdot f_{clk}$$

เนื่องจาก Glitch สวิงขึ้นและลงเต็มสเกล ($0 \rightarrow V_{DD} \rightarrow 0$) ในรอบเดียว จึงนับเป็นการชาร์จและคายประจุเต็ม 1 รอบ:
$$\alpha_{glitch} = 0.25$$
$$C_L = 45\text{ fF} = 45 \times 10^{-15}\text{ F}$$
$$V_{DD} = 0.85\text{ V} \Rightarrow V_{DD}^2 = 0.7225\text{ V}^2$$
$$f_{clk} = 300\text{ MHz} = 300 \times 10^6\text{ Hz}$$

แทนค่า:
$$P_{glitch} = 0.25 \times (45 \times 10^{-15}) \times 0.7225 \times (300 \times 10^6)$$
$$P_{glitch} = 0.25 \times 45 \times 0.7225 \times 300 \times 10^{-9}\text{ W}$$
$$P_{glitch} = 2.4384 \times 10^{-6}\text{ W} \approx 2.44\ \mu\text{W}$$

##### ขั้นตอนที่ 2: วิเคราะห์การทะลุผ่านของพัลส์ (Pulse Propagation Analysis)
เพื่อดูว่าพัลส์ Glitch กว้าง $t_{glitch} = 350\text{ ps}$ จะถูกลดทอนลงหรือไม่ ให้พิจารณาอัตราส่วนระหว่างความกว้างพัลส์กับค่าคงที่เวลา $\tau_{rc}$:
$$\frac{t_{glitch}}{\tau_{rc}} = \frac{350\text{ ps}}{120\text{ ps}} \approx 2.92$$

แรงดันสูงสุดที่ชาร์จได้บนโหนดปลายทางตามสมการตอบสนองขั้นบันได RC:
$$V_{peak} = V_{DD} \cdot (1 - e^{-\frac{t_{glitch}}{\tau_{rc}}}) = 0.85 \times (1 - e^{-2.92}) = 0.85 \times (1 - 0.054) = 0.85 \times 0.946 = 0.804\text{ V}$$

แรงดัน $0.804\text{ V}$ คิดเป็นถึง $94.6\%$ ของ $V_{DD}$ ซึ่งสูงเกินค่าเกณฑ์แรงดันตรรกะระดับสูง ($V_{IH} \approx 0.7 \times V_{DD} = 0.595\text{ V}$) อย่างมาก!
ดังนั้น พัลส์ Glitch นี้จึงไม่ถูกฟิลเตอร์ทิ้ง และจะถูกเกตปลายทางตีความเป็นลอจิก '1' อย่างสมบูรณ์ ทำให้เกิดการเปลี่ยนสถานะหรือการบันทึกข้อมูลผิดพลาดทันที

---

### คำถามที่ 3: ข้อผิดพลาดจากการใช้ SDC Multicycle Path บนวงจร Mealy ที่ถูกแปลงเป็น Registered Moore

ในการแก้ไขระบบเพื่อแปลงจาก Mealy เป็น Registered Moore วิศวกรได้เพิ่มสเตจทรานซิชัน 1 ไซเคิลเพื่อรอให้อินพุตคงที่ และได้เขียนข้อกำหนดเวลา SDC ลงในไฟล์ `.xdc` ดังนี้:

```tcl
set_multicycle_path 2 -setup -from [get_cells u_fsm/state_reg*] -to [get_cells u_core/datapath_reg*]
```

ทว่าหลังจากการใช้งาน วิศวกรพบว่าระบบทำงานล้มเหลวที่อุณหภูมิต่ำ (Fast Corner: $-40^\circ\text{C}$, $V_{DD} = 0.90\text{ V}$) ทันทีเนื่องจากเกิด Hold Time Violation ขนานใหญ่ จงวิเคราะห์ว่าสาเหตุเกิดจากสิ่งใด และคำสั่งแก้ไขที่ถูกต้องตามมาตรฐาน IEEE/Synopsys SDC คือข้อใด?

---

#### ตัวเลือก:
A) การตั้ง `-setup 2` ทำให้ Tool เลื่อน Hold Edge ไปตรวจที่รอบที่ 1 โดยอัตโนมัติ ซึ่งต้องใส่ `set_multicycle_path 1 -hold` เพิ่มเติม  
B) การระบุ `get_cells` ผิดพลาด ต้องใช้ `get_pins` เท่านั้น  
C) การใช้ Multicycle บน State Machine ขัดต่อกฎของ DO-254 ต้องยกเลิกคำสั่งทั้งหมด  
D) อุณหภูมิต่ำทำให้สายไฟมีความต้านทานสูงขึ้น ทำให้ Hold Time ยาวขึ้นเกินกว่าที่คาดการณ์

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) การตั้ง `-setup 2` ทำให้ Tool เลื่อน Hold Edge ไปตรวจที่รอบที่ 1 โดยอัตโนมัติ ซึ่งต้องใส่ `set_multicycle_path 1 -hold` เพิ่มเติม**

##### เหตุผลทางวิศวกรรม STA:
ในกฎมาตรฐานของเครื่องมือวิเคราะห์เวลา (Synopsys Design Constraints: SDC):
เมื่อวิศวกรกำหนด:
`set_multicycle_path 2 -setup ...`
เครื่องมือ STA จะเลื่อน Capture Edge สำหรับ **Setup Check** ไปยังขอบสัญญาณนาฬิการอบที่ 2 ($2 \times T_{clk}$) แต่โดยดีฟอลต์ เครื่องมือจะยึดหลักการตรวจ **Hold Check** โดยอิงจาก Setup Capture Edge ลบออกไป 1 คาบเวลา!

ส่งผลให้ Hold Check ถูกเลื่อนจากรอบที่ 0 (Active Launch Edge เดียวกัน) ไปตรวจที่รอบที่ 1 ($1 \times T_{clk}$) ซึ่งหมายความว่า ข้อมูลใหม่จะต้องมีความหน่วงในการเดินทางอย่างน้อยมากกว่า $1 \text{ คาบสัญญาณนาฬิกาเต็ม}$ จึงจะไม่ชน Hold Violation!
ในสภาวะ Fast Corner (อุณหภูมิต่ำ $-40^\circ\text{C}$ ลอจิกทำงานเร็วมาก $t_{delay}$ สั้นมาก) ข้อมูลจะเดินทางมาถึงก่อนขอบที่ 1 อย่างแน่นอน ทำให้เกิด Hold Violation ล้มเหลวทันที!

##### คำสั่งแก้ไขที่ถูกต้อง:
ต้องออกคำสั่งปรับ Hold Check ให้ถอยกลับมาตรวจที่ขอบสัญญาณนาฬิการอบปล่อยสัญญาณ (Launch Edge) เดิม:
```tcl
set_multicycle_path 2 -setup -from [get_cells u_fsm/state_reg*] -to [get_cells u_core/datapath_reg*]
set_multicycle_path 1 -hold  -from [get_cells u_fsm/state_reg*] -to [get_cells u_core/datapath_reg*]
```
คำสั่ง `-hold 1` จะเลื่อน Hold Capture Edge ถอยกลับมา 1 รอบนาฬิกา ทำให้ Hold Check ตรวจสอบที่รอบ $2 - 1 - 1 = 0$ (รอบเดียวกัน) ทำให้ Hold Slack กลับมาเป็นบวกและปลอดภัยในทุกมุม Corner ของซิลิคอน
