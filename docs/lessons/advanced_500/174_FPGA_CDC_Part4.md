# Lesson 174: FPGA CDC Part 4 - Handshake Protocols (4-Phase vs 2-Phase Handshake CDC, Level vs Toggle Req-Ack, Backpressure Flow Control & Round-Trip Latency Bounds)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์การส่งข้อมูลแบบวงเปิด เทียบกับ วงปิด (Open-Loop vs Closed-Loop CDC)
ในสถาปัตยกรรม **Data MUX Synchronizer (DMUX)** ที่ศึกษาในบทที่ 173 การส่งข้อมูลเป็นแบบ **วงเปิด (Open-Loop)** ซึ่งฝั่งส่ง (Sender) จะต้อง "คาดเดา" หรือ "หน่วงเวลารอคอย" ให้ยาวนานพอตามสูตรคณิตศาสตร์ เพื่อให้ฝั่งรับ (Receiver) มีเวลาแซมเปิลข้อมูลได้อย่างปลอดภัย

ทว่า ในสภาวะแวดล้อมระบบ Mission-Critical ขั้นสูง:
1. **Clock Frequency Drift & Dynamic Frequency Scaling (DFS):** หากสัญญาณนาฬิกาของฝั่งรับมีความถี่แปรผันตามภาระงาน หรือเกิด Clock Throttle เพื่อประหยัดพลังงาน เวลาคาดการณ์ที่ฝั่งส่งตั้งไว้ล่วงหน้าจะผิดเพี้ยนทันที
2. **Clock Gating Interruption:** หากฝั่งรับถูก Clock-Gated ชั่วขณะ สัญญาณ Enable อาจผ่านไปโดยที่ฝั่งรับไม่เคยได้แซมเปิลข้อมูล ส่งผลให้ข้อมูลสูญหายอย่างถาวร
3. **Data Loss on Consecutive Transfers:** หากฝั่งส่งปล่อยข้อมูลชุดใหม่เร็วเกินไปแม้เพียง 1 ไซเคิล ข้อมูลชุดเดิมจะถูกเขียนทับ (Data Overwrite / Race Condition)

เพื่อขจัดสมมติฐานการคาดเดาเวลาให้หมดไป $100\%$ วิศวกรต้องนำระบบ **Closed-Loop Handshake CDC** มาใช้งาน ซึ่งใช้สัญญาณตอบรับสองทิศทาง (**Request-Acknowledge Protocol**) ยืนยันว่าฝั่งรับได้รับข้อมูลและบันทึกลงรีจิสเตอร์อย่างปลอดภัยแล้ว จึงจะอนุญาตให้ฝั่งส่งเริ่มส่งข้อมูลชุดถัดไป

---

### 1.2 สถาปัตยกรรม Four-Phase Handshake (Level-Sensitive Req-Ack)

สถาปัตยกรรม Four-Phase Handshake (หรือ Level-Sensitive Handshake) เป็นโปรโตคอลวงปิดที่ได้รับความนิยมสูงสุดในมาตรฐานความปลอดภัยทางทหารและการบิน (MIL-STD, DO-254) เนื่องจากวงจรจะคืนค่ากลับสู่ระดับลอจิกเริ่มต้น (`0`) เสมอในทุกๆ ธุรกรรมการส่งข้อมูล ทำให้ป้องกันสัญญาณรบกวน (Noise Immunity) ได้อย่างยอดเยี่ยม:

```
               สถาปัตยกรรม 4-PHASE LEVEL HANDSHAKE CDC
               
    [ SENDER DOMAIN: CLK_SRC ]                     [ RECEIVER DOMAIN: CLK_DST ]
    
    data_src ═════════════════════════════════════════════════════════► data_dst
    
             ┌───────────┐     req_level                 ┌───────────┐
    req_src ─┤ FSM_SRC   ├────────────────►[ 2-FF Sync ]►┤ FSM_DST   │
             │           │                               │           │
             │           │     ack_level                 │           │
    ack_src ◄┤           │◄────[ 2-FF Sync ]─────────────┤           ├─► dst_valid
             └───────────┘                               └───────────┘
```

#### กลไกการทำงาน 4 ลำดับขั้น (The 4 Distinct Phases):
```
    Phase 1: Src ขับข้อมูล เสถียรแล้วจึงยก  REQ: 0 -> 1
             ─────────────────────────────────────────►
    Phase 2: Dst แซมเปิลข้อมูลเสร็จ ยกตอบ   ACK: 0 -> 1
             ◄─────────────────────────────────────────
    Phase 3: Src เห็น ACK รับทราบ จึงปลด   REQ: 1 -> 0
             ─────────────────────────────────────────►
    Phase 4: Dst เห็น REQ ตก จึงปลดกลับ    ACK: 1 -> 0 (พร้อมสำหรับรอบใหม่)
             ◄─────────────────────────────────────────
```

```
                        TIMING DIAGRAM OF 4-PHASE HANDSHAKE
                        
    data_src  : ─────<============ D A T A   V A L I D ==============>──────
    req_level : ─────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\___________________
                     │ Phase 1                          │ Phase 3
    req_dst   : ───────────[ 2-FF Sync ]───/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\______
                                           │ (Latch Data)
    ack_level : ───────────────────────────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\______
                                           │ Phase 2                 │ Phase 4
    ack_src   : ────────────────────────────────[ 2-FF Sync ]───/‾‾‾‾\______
                                                                ▲
                                                    (Src รับรู้: พร้อมเตรียมส่งชุดถัดไป)
```

#### การคำนวณ Round-Trip Latency ของ 4-Phase Handshake ($T_{RTT,4P}$):
ในแต่ละรอบการส่ง 1 ข้อมูล สัญญาณควบคุมต้องเดินทางข้ามโดเมนไป-กลับถึง 4 ครั้ง โดยผ่านวงจร 2-Stage Synchronizer:
1. **Phase 1 (REQ เดินทางไป Dst):** ใช้เวลา $T_{P1} = (N_{sync,dst} + 1) \cdot T_{dst}$
2. **Phase 2 (ACK เดินทางกลับ Src):** ใช้เวลา $T_{P2} = (N_{sync,src} + 1) \cdot T_{src}$
3. **Phase 3 (REQ=0 เดินทางไป Dst):** ใช้เวลา $T_{P3} = (N_{sync,dst} + 1) \cdot T_{dst}$
4. **Phase 4 (ACK=0 เดินทางกลับ Src):** ใช้เวลา $T_{P4} = (N_{sync,src} + 1) \cdot T_{src}$

ผลรวมเวลารอบการส่งข้อมูลสมบูรณ์ 1 คำ (Total Round-Trip Latency):
$$T_{RTT,4P} = 2 \cdot \left[ (N_{sync,dst} + 1) \cdot T_{dst} + (N_{sync,src} + 1) \cdot T_{src} \right]$$

สมมติให้ $N_{sync} = 2$ ทั้งสองฝั่ง:
$$T_{RTT,4P} = 2 \cdot [ 3 \cdot T_{dst} + 3 \cdot T_{src} ] = 6 \cdot T_{dst} + 6 \cdot T_{src}$$

> [!NOTE]
> หาก $f_{src} = 100\text{ MHz}$ ($T_{src} = 10\text{ ns}$) และ $f_{dst} = 50\text{ MHz}$ ($T_{dst} = 20\text{ ns}$):
> $$T_{RTT,4P} = 6(20\text{ ns}) + 6(10\text{ ns}) = 120\text{ ns} + 60\text{ ns} = 180\text{ ns}$$
> อัตราการส่งข้อมูลสูงสุด (Maximum Throughput) จะได้เพียง:
> $$\text{Throughput}_{4P} = \frac{1}{180\text{ ns}} \approx 5.55\text{ Mega-words/second}$$

---

### 1.3 สถาปัตยกรรม Two-Phase Handshake (Toggle / Transition-Sensitive Req-Ack)

สำหรับแอปพลิเคชันที่ต้องการ Throughput สูงกว่าเดิม 2 เท่า สถาปัตยกรรม **Two-Phase Handshake** ถูกนำมาใช้งาน โดยโปรโตคอลนี้จะมอง **"ทุกๆ ขอบสัญญาณที่เปลี่ยนสถานะ (Every Edge Transition: $0 \to 1$ และ $1 \to 0$)"** เป็น 1 ธุรกรรม ไม่ต้องเสียเวลาปลดสัญญาณกลับเป็นศูนย์ใน Phase 3 และ Phase 4:

```
               สถาปัตยกรรม 2-PHASE TOGGLE HANDSHAKE CDC
               
    [ SENDER DOMAIN: CLK_SRC ]                     [ RECEIVER DOMAIN: CLK_DST ]
    
    data_src ═════════════════════════════════════════════════════════► data_dst
    
             ┌───────────┐     req_toggle                ┌───────────┐
    tx_start ┤ T-FF      ├────────────────►[ 2-FF Sync ]►┤ Edge/XOR  ├─► dst_valid
             │ Logic     │                               │ T-FF      │
             │           │     ack_toggle                │ Logic     │
    tx_done ◄┤ XOR Sense │◄────[ 2-FF Sync ]─────────────┤           │
             └───────────┘                               └───────────┘
```

#### กลไกการทำงาน 2 ลำดับขั้น (The 2 Transitions):
1. **Transition 1 (REQ Toggle):**
   ฝั่งส่งเตรียมข้อมูลให้เสร็จ จากนั้นสั่งสลับสถานะของสาย `req_toggle` ($\text{req} \Leftarrow \sim\text{req}$)
2. **Transition 2 (ACK Toggle):**
   ฝั่งรับตรวจจับการเปลี่ยนระดับสัญญาณ (`req_sync2 ^ req_sync3`) จากนั้น Latch ข้อมูลเข้าสู่รีจิสเตอร์ปลายทาง และสั่งสลับสถานะของสาย `ack_toggle` ($\text{ack} \Leftarrow \sim\text{ack}$) ตอบกลับทันที!

```
                        TIMING DIAGRAM OF 2-PHASE HANDSHAKE
                        
    Word Index: ────[ Word 0 ]────►├──────[ Word 1 ]──────►├──────[ Word 2 ]──────►
    data_src  : ════< Data 0 >═════╡══════< Data 1 >═══════╡══════< Data 2 >══════
    req_toggle: ────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾\_______________________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
                    ▲ Trans 1 (0->1)▲ Trans 1 (1->0)       ▲ Trans 1 (0->1)
    ack_toggle: ───────────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\_______________________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾
                           ▲ Trans 2 (0->1)▲ Trans 2 (1->0)       ▲ Trans 2 (0->1)
```

#### การคำนวณ Round-Trip Latency ของ 2-Phase Handshake ($T_{RTT,2P}$):
$$T_{RTT,2P} = (N_{sync,dst} + 1) \cdot T_{dst} + (N_{sync,src} + 1) \cdot T_{src}$$

สำหรับ $N_{sync} = 2$:
$$T_{RTT,2P} = 3 \cdot T_{dst} + 3 \cdot T_{src}$$

> [!TIP]
> ด้วยพารามิเตอร์เดียวกัน ($f_{src} = 100\text{ MHz}$, $f_{dst} = 50\text{ MHz}$):
> $$T_{RTT,2P} = 3(20\text{ ns}) + 3(10\text{ ns}) = 60\text{ ns} + 30\text{ ns} = 90\text{ ns}$$
> Throughput เพิ่มขึ้นเป็น **$11.11\text{ Mega-words/second}$** (เพิ่มขึ้น $100\%$ เต็มเมื่อเทียบกับ 4-Phase!)

---

### 1.4 การเปรียบเทียบเชิงสถาปัตยกรรม (Comprehensive Trade-off Matrix)

| ปัจจัยทางวิศวกรรม (Engineering Metric) | 4-Phase Handshake (Level) | 2-Phase Handshake (Toggle) | Asynchronous FIFO (BRAM) |
|:---|:---|:---|:---|
| **Round-Trip Latency** | $2 \cdot [(N+1)T_{dst} + (N+1)T_{src}]$ | $(N+1)T_{dst} + (N+1)T_{src}$ | $(N+1)T_{dst}$ (Write-to-Read) |
| **Throughput สูงสุด** | ต่ำ ($\sim 1 / T_{RTT,4P}$) | ปานกลาง ($\sim 1 / T_{RTT,2P}$) | **สูงสุด (1 Word / Cycle)** |
| **Logic Resource Cost** | ต่ำมาก ($\sim 15$ LUTs, $12$ FFs) | ต่ำ ($\sim 20$ LUTs, $14$ FFs) | สูง (ใช้ BRAM + $\sim 120$ LUTs) |
| **ความทนทานต่อ Glitch/Noise** | **สูงสุด (คืนค่า 0 เสมอ)** | ปานกลาง (ไวต่อ False Edge) | สูงมาก |
| **ความซับซ้อนของ Reset** | เรียบง่าย (เคลียร์ FSM สู่ IDLE) | **สูงมาก (ต้อง Sync Reset ทั้งคู่)** | ปานกลาง |
| **ความเหมาะสมในการใช้งาน** | คอนฟิกค่า, พารามิเตอร์ระบบ | ควบคุมแพ็กเก็ต, Data Block | สตรีมมิ่งวิดีโอ, DSP ADC/DAC |

---

### 1.5 โค้ดแม่แบบภาษา Verilog สำหรับ 4-Phase Handshake CDC

```verilog
// ==============================================================================
// 4-PHASE LEVEL-SENSITIVE HANDSHAKE SYNCHRONIZER
// Fully Parameterized, Clean FSM Architecture with ASYNC_REG
// ==============================================================================
(* keep_hierarchy = "yes" *)
module handshake_4phase_cdc #(
    parameter integer DATA_WIDTH = 32
)(
    // Sender Domain (CLK_SRC)
    input  wire                  clk_src,
    input  wire                  rst_src_n,
    input  wire [DATA_WIDTH-1:0] src_data_in,
    input  wire                  src_valid_in,
    output reg                   src_ready_out,

    // Receiver Domain (CLK_DST)
    input  wire                  clk_dst,
    input  wire                  rst_dst_n,
    output reg  [DATA_WIDTH-1:0] dst_data_out,
    output reg                   dst_valid_out
);

    // -------------------------------------------------------------------------
    // Sender State Machine
    // -------------------------------------------------------------------------
    localparam [1:0] S_SRC_IDLE = 2'b00,
                     S_SRC_WAIT_ACK_HIGH = 2'b01,
                     S_SRC_WAIT_ACK_LOW  = 2'b10;

    reg [1:0]            src_state;
    reg [DATA_WIDTH-1:0] src_data_hold;
    reg                  src_req;

    // Cross-domain 2-FF Synchronizer: ACK (Dst -> Src)
    (* ASYNC_REG = "TRUE" *) reg ack_sync_ff1, ack_sync_ff2;
    always @(posedge clk_src or negedge rst_src_n) begin
        if (!rst_src_n) begin
            ack_sync_ff1 <= 1'b0;
            ack_sync_ff2 <= 1'b0;
        end else begin
            ack_sync_ff1 <= ack_dst_reg;
            ack_sync_ff2 <= ack_sync_ff1;
        end
    end

    always @(posedge clk_src or negedge rst_src_n) begin
        if (!rst_src_n) begin
            src_state     <= S_SRC_IDLE;
            src_data_hold <= {DATA_WIDTH{1'b0}};
            src_req       <= 1'b0;
            src_ready_out <= 1'b0;
        end else begin
            case (src_state)
                S_SRC_IDLE: begin
                    src_ready_out <= 1'b1;
                    if (src_valid_in && src_ready_out) begin
                        src_data_hold <= src_data_in;
                        src_req       <= 1'b1;        // Phase 1: REQ = 1
                        src_ready_out <= 1'b0;
                        src_state     <= S_SRC_WAIT_ACK_HIGH;
                    end
                end

                S_SRC_WAIT_ACK_HIGH: begin
                    if (ack_sync_ff2 == 1'b1) begin
                        src_req   <= 1'b0;            // Phase 3: REQ = 0
                        src_state <= S_SRC_WAIT_ACK_LOW;
                    end
                end

                S_SRC_WAIT_ACK_LOW: begin
                    if (ack_sync_ff2 == 1'b0) begin
                        src_ready_out <= 1'b1;        // Complete 4-phase cycle
                        src_state     <= S_SRC_IDLE;
                    end
                end

                default: src_state <= S_SRC_IDLE;
            endcase
        end
    end

    // -------------------------------------------------------------------------
    // Receiver State Machine
    // -------------------------------------------------------------------------
    localparam [1:0] S_DST_IDLE = 2'b00,
                     S_DST_HOLD = 2'b01;

    reg [1:0] dst_state;
    reg       ack_dst_reg;

    // Cross-domain 2-FF Synchronizer: REQ (Src -> Dst)
    (* ASYNC_REG = "TRUE" *) reg req_sync_ff1, req_sync_ff2;
    always @(posedge clk_dst or negedge rst_dst_n) begin
        if (!rst_dst_n) begin
            req_sync_ff1 <= 1'b0;
            req_sync_ff2 <= 1'b0;
        end else begin
            req_sync_ff1 <= src_req;
            req_sync_ff2 <= req_sync_ff1;
        end
    end

    always @(posedge clk_dst or negedge rst_dst_n) begin
        if (!rst_dst_n) begin
            dst_state     <= S_DST_IDLE;
            dst_data_out  <= {DATA_WIDTH{1'b0}};
            dst_valid_out <= 1'b0;
            ack_dst_reg   <= 1'b0;
        end else begin
            case (dst_state)
                S_DST_IDLE: begin
                    dst_valid_out <= 1'b0;
                    if (req_sync_ff2 == 1'b1) begin
                        dst_data_out  <= src_data_hold; // Latch stable data
                        dst_valid_out <= 1'b1;          // Pulse valid to local logic
                        ack_dst_reg   <= 1'b1;          // Phase 2: ACK = 1
                        dst_state     <= S_DST_HOLD;
                    end
                end

                S_DST_HOLD: begin
                    dst_valid_out <= 1'b0;              // 1-cycle valid strobe
                    if (req_sync_ff2 == 1'b0) begin
                        ack_dst_reg <= 1'b0;            // Phase 4: ACK = 0
                        dst_state   <= S_DST_IDLE;
                    end
                end

                default: dst_state <= S_DST_IDLE;
            endcase
        end
    end

endmodule
```

---

### 1.6 ข้อกำหนด SystemVerilog Assertions (SVA) เพื่อพิสูจน์ Formal Correctness

```systemverilog
// SVA Formal Verification Suite for 4-Phase Handshake CDC
module handshake_4phase_sva (
    input wire clk_src,
    input wire rst_src_n,
    input wire src_req,
    input wire ack_sync_ff2,
    input wire [31:0] src_data_hold,
    
    input wire clk_dst,
    input wire rst_dst_n,
    input wire req_sync_ff2,
    input wire ack_dst_reg
);

    // 1. Data Invariance Assertion:
    // While REQ is high and ACK has not returned, data MUST NOT change!
    property p_src_data_invariant;
        @(posedge clk_src) disable iff (!rst_src_n)
        (src_req && !ack_sync_ff2) |=> $stable(src_data_hold);
    endproperty
    assert_data_invariant: assert property (p_src_data_invariant)
        else $error("[HANDSHAKE_VIOLATION]: src_data modified during active transfer!");

    // 2. Handshake Phase Progression (Liveness / No-Deadlock Check):
    // If REQ is asserted, ACK must eventually assert (Bounded by 30 cycles)
    property p_ack_eventually_asserts;
        @(posedge clk_src) disable iff (!rst_src_n)
        src_req |-> strong(##[1:50] ack_sync_ff2);
    endproperty
    assert_no_deadlock_high: assert property (p_ack_eventually_asserts)
        else $error("[DEADLOCK]: System hung waiting for ACK high!");

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】ระบบกล้องสำรวจอวกาศความละเอียดสูง เกิดอาการค้างถาวร (Permanent Freeze)
ในสภาวะอุณหภูมิติดลบ (-40°C) จากบั๊ก Polarity Inversion Deadlock ใน 2-Phase Handshake
================================================================================
```

#### บริบทของระบบ (System Context):
ทีมวิศวกรออกแบบระบบควบคุมการถ่ายภาพของดาวเทียมสังเกตการณ์โลก (Earth Observation Satellite) บนชิป FPGA เกรดอวกาศ (Space-Grade Microchip RTG4):
* **Sensor Core Controller (`clk_sensor`):** ความถี่ $120\text{ MHz}$
* **Telemetry Data Logger (`clk_tlm`):** ความถี่ $20\text{ MHz}$
* เพื่อบีบ Throughput ให้ส่งข้อมูลเมทริกซ์การวัดแสงได้ทันโดยไม่เปลืองบล็อก RAM วิศวกรเลือกใช้ **Two-Phase Toggle Handshake CDC**
* สัญญาณรีเซ็ตของทั้งสองโดเมนมาจากวงจรตรวจวัดแรงดันตก (Brown-out Detector) ภายนอก

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
ในระหว่างการทดสอบในตู้สุญญากาศความร้อนอวกาศ (Thermal Vacuum Chamber - TVAC) เมื่ออุณหภูมิลดลงถึง $-40^\circ\text{C}$ ระบบกล้องทำงานไปได้ประมาณ 4 ชั่วโมง แล้วเกิดอาการ **"ระบบค้างนิ่งสนิท (Total Freeze)"** การสื่อสารข้อมูลทาง Telemetry หยุดชะงัก $100\%$ การส่งสัญญาณ Telecommand สั่งรีเซ็ตย่อยเฉพาะโมดูล Sensor ไม่สามารถกู้ระบบกลับมาได้ ต้องทำการตัดไฟดาวเทียมหลัก (Hard Power Cycle) เท่านั้น!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมระบบส่งข้อมูล Telemetry จึงค้างนิ่งสนิท?**
   * *เพราะโมดูล Two-Phase Handshake ติดอยู่ในสถานะ Deadlock ทั้งฝั่งส่งและฝั่งรับหยุดนิ่ง ไม่มีการขยับขอบสัญญาณอีกเลย*
2. **ทำไม Handshake จึงเกิดสภาวะ Deadlock ไม่ขยับขอบสัญญาณ?**
   * *เพราะฝั่งส่งกำลังรอให้สาย `ack_toggle` เปลี่ยนสถานะ ในขณะที่ฝั่งรับคิดว่าตนเองกำลังรอให้สาย `req_toggle` เปลี่ยนสถานะ เกิดสถานะขั้วสัญญาณสลับข้างกัน (Polarity Inversion)*
3. **ทำไมขั้วสัญญาณ Toggle จึงเกิด Polarity Inversion ไม่ตรงกัน?**
   * *เพราะมีการสั่ง Sub-system Warm Reset เข้ามายังโดเมน `clk_sensor` เพียงโดเมนเดียว ทำให้รีจิสเตอร์ `req_toggle` ถูกรีเซ็ตกลับเป็น `0` ในขณะที่โดเมน `clk_tlm` ไม่ได้ถูกรีเซ็ตและคงค้างสถานะ `ack_toggle = 1` ไว้อยู่เดิม*
4. **ทำไมสถาปัตยกรรม Two-Phase จึงฟื้นตัวจาก Reset แบบแยกโดเมนไม่ได้?**
   * *เพราะโปรโตคอล Two-Phase ตัดสินใจโดยใช้ "การเปลี่ยนระดับสัญญาณ (Edge Transition)" ไม่ได้ใช้ระดับแรงดันคงที่ (Level) เมื่อระดับสัญญาณเริ่มต้นของทั้งสองฝั่งไม่เท่ากัน วงจรจะมองไม่เห็นขอบ และไม่มีกลไก Recovery Time-out ใดๆ*
5. **ทำไมทีมออกแบบจึงไม่พบปัญหานี้ตั้งแต่ขั้นตอน Simulation?**
   * *เพราะในการจำลองพฤติกรรม (Testbench Simulation) วิศวกรสั่งปลด Reset ของทุกโดเมนพร้อมกันที่เวลา $t = 0\text{ ns}$ เสมอ และไม่เคยจำลองการเกิด Asynchronous Independent Reset Crossing เลย!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                       สาเหตุของความล้มเหลว: POLARITY INVERSION DEADLOCK
                       
   METHOD (กระบวนการออกแบบโปรโตคอล)             MACHINE (พฤติกรรมฮาร์ดแวร์ & Reset)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ใช้ 2-Phase โดยไม่มี Time-out  │          │ Reset Unbalanced Deassertion   │
   │ เลือกลด Latency แต่ทิ้ง Safety │          │ สภาพอุณหภูมิต่ำ RC Delay เปลี่ยน│
   │ ขาดกลไก Clear-on-Error Handshake│         │ ขาดวงจร Global Reset Sequencer │
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ไม่ได้รัน Reset Domain Crossing│          │ Testbench ยิง Reset พร้อมกัน   │
   │ ละเลยคู่มือการกู้คืนระบบฉุกเฉิน │          │ ไม่เคยทดสอบ Warm Reboot ฝั่งเดียว│
   │ ขาด SVA Liveness Time-out Check│          │ ขาดการจำลอง Corner Case        │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (มาตรฐานการตรวจสอบ RDC)            MEASUREMENT (สภาวะการจำลอง Testbench)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขเชิงระบบ (Engineering Fixes):
1. **เปลี่ยนมาใช้ 4-Phase Handshake ในจุดที่มี Reset อิสระ:** สำหรับสัญญาณควบคุมระดับระบบ ให้ใช้ 4-Phase Handshake เสมอ เพราะเมื่อโดเมนใดโดเมนหนึ่งถูกรีเซ็ต สัญญาณจะตกลงสู่ `0` โดยอัตโนมัติ ซึ่งสอดคล้องกับสภาวะ IDLE ของอีกฝั่งหนึ่งทันที (Self-Healing Topology)
2. **หากจำเป็นต้องใช้ 2-Phase Handshake ต้องติดตั้ง Hardware Watchdog Time-out:**
   * เพิ่มตัวนับเวลา (Counter Timer) ในฝั่งส่ง หากส่ง `req_toggle` ไปแล้วไม่ได้รับ `ack_toggle` กลับมาภายใน $256$ ไซเคิล ให้วงจรทำการ Force Resync และยิงสัญญาณเตือนระบบ
3. **ติดตั้ง Reset Sequencer แบบรวมศูนย์:** ควบคุมให้การรีเซ็ตระบบต้องเกิดขึ้นพร้อมกันทั้งสองโดเมนเสมอ

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Handshake CDC (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | ได้ประเมินความเสี่ยงระหว่าง 4-Phase (Safe) vs 2-Phase (Fast) แล้วหรือไม่? | มีเอกสาร Trade-off Analysis | [ ] ผ่าน |
| 2 | หากใช้ 2-Phase Handshake สัญญาณ Reset ของทั้งสองโดเมนผูกผ่าน Sequencer เดียวกันหรือไม่? | Synchronized Reset Pair | [ ] ผ่าน |
| 3 | มีวงจร Hardware Watchdog Time-out ดักจับสภาวะ Deadlock หรือไม่? | $\le 256$ Cycles Timeout | [ ] ผ่าน |
| 4 | มีการระบุ `(* ASYNC_REG = "TRUE" *)` บนขาสัญญาณ REQ และ ACK ครบทุกสเตจ? | $100\%$ Coverage | [ ] ผ่าน |
| 5 | มีการเขียน SVA Liveness Assertion ตรวจสอบการเกิด Deadlock ใน Simulation? | Verified with Formal Proof | [ ] ผ่าน |
| 6 | ทำการทดสอบ Reset โดเมนส่งโดเมนเดียวใน Testbench แล้วระบบฟื้นตัวได้ $100\%$ หรือไม่? | Pass Independent Reset Test | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | ハンドシェイク同期 | ハンドシェイクどうき | Handosheiku dōki | Handshake Synchronizer |
| 2 | 4相式プロトコル | 4そうしきプロトコル | Yonsō-shiki purotokoru | 4-Phase Protocol (Return-to-Zero) |
| 3 | 2相式プロトコル | 2そうしきプロトコル | Nisō-shiki purotokoru | 2-Phase Protocol (Non-Return-to-Zero / Toggle) |
| 4 | トグル応答 | トグルおうとう | Toguru ōtō | Toggle-based Acknowledge |
| 5 | デッドロック回避 | デッドロックかいひ | Deddorokku kaihi | Deadlock Avoidance |
| 6 | 極性反転不一致 | きょくせいはんてんふいっち | Kyokusei hanten fuicchi | Polarity Inversion Mismatch |
| 7 | ラウンドトリップ遅延 | ラウンドトリップちえん | Raundo torippu chien | Round-Trip Latency ($T_{RTT}$) |
| 8 | バックプレッシャー | バックプレッシャー | Bakku puresshā | Backpressure Flow Control |
| 9 | 独立リセット解除 | どくりつリセットかいじょ | Dokuritsu risetto kaijo | Independent Reset Deassertion |
| 10 | 自己復旧機能 | じこふっきゅうきのう | Jiko fukkyū kinō | Self-Healing / Auto-Recovery Mechanism |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ศูนย์วิจัยและพัฒนาอุปกรณ์อิเล็กทรอนิกส์ยานยนต์ (Automotive Electronics R&D Center), เมืองโยโกฮาม่า (Yokohama)  
**ผู้เข้าร่วม:**
* **ซาโต้ชิฟ (Sato-Chief):** หัวหน้าทีมตรวจสอบระบบควบคุมความปลอดภัย (Lead Sign-Off Reviewer / 主席技師)
* **กฤษดา (Kritsada):** วิศวกรอาวุโสด้าน FPGA (FPGA Senior Engineer)

---

**佐藤主席 (Sato):**  
「クリサダさん、テレメトリ制御ブロックのCDC回路について設計書を確認したよ。君はスループットを最優先して、トグル駆動の**2相ハンドシェイク（Two-Phase Toggle）**を採用しているね。だが、この構成だと送信側と受信側のリセットドメインが分かれている。もし片方のブロックだけが電源瞬低で個別リセット（Warm Reset）された場合、トグルの極性不一致（Polarity Mismatch）による永久デッドロックが発生する懸念があるが、対策は講じてあるのかね？」  
*(Kritsada-san, terem 토 ri seigyo burokku no CDC kairo ni tsuite sekkeisho wo kakunin shita yo. Kimi wa surūputto wo saiyūsen shite, toguru kudō no nisō handosheiku wo saiyō shite iru ne. Daga, kono kōsei dato sōshin-gawa to jushin-gawa no risetto domein ga wakarete iru. Moshi katahō no burokku dake ga dengen shuntei de kobetsu risetto sareta baai, toguru no kyokusei fuicchi ni yoru eikyū deddorokku ga hassei suru kenen ga aru ga, taisaku wa kōjite aru no kane?)*  
**คำแปล:** คุณกฤษดา ผมได้ตรวจเอกสารออกแบบของวงจร CDC ในบล็อก Telemetry แล้ว คุณเลือกใช้ Two-Phase Handshake แบบสลับทรานซิชันเพื่อเน้น Throughput สูงสุดสินะ แต่โครงสร้างนี้ โดเมนรีเซ็ตของฝั่งส่งกับฝั่งรับมันแยกจากกัน หากบล็อกใดบล็อกหนึ่งเกิดไฟตกชั่วขณะจนถูกรีเซ็ตแยกเดี่ยว (Warm Reset) มันจะเกิดสภาวะ Deadlock ถาวรจากขั้วของ Toggle สลับข้างกัน คุณได้เตรียมมาตรการป้องกันเรื่องนี้ไว้หรือยังครับ?

**クリサダ (Kritsada):**  
「ご指摘ありがとうございます、佐藤主席。確かにシミュレーション上では全ドメイン同時リセットしか検証できておりませんでした。2相式では、送信側がリセットされてトグル値が`0`に戻った際、受信側が前回の`1`を保持したままだと、次のエッジを互いに待ち続けるデッドロックに陥ります。」  
*(Goshiteki arigatō gozaimasu, Satō-shuseki. Tashikani shimyurēshon-jō dewa zen-domein dōji risetto shika kenshō dekite orimasendeshita. Nisō-shiki dewa, sōshin-gawa ga risetto sarete toguru-chi ga 0 ni modotta sai, jushin-gawa ga zenkai no 1 wo hoji shita mama dato, tsugi no ejji wo tagai ni machi-tsuzukeru deddorokku ni ochīrimasu.)*  
**คำแปล:** ขอบคุณสำหรับคำชี้แนะอย่างยิ่งครับหัวหน้าซาโต้ เป็นความจริงที่ใน Simulation ผมได้ทดสอบเฉพาะการรีเซ็ตพร้อมกันทุกโดเมนเท่านั้น ในระบบ 2-Phase หากฝั่งส่งถูกรีเซ็ตจนค่า Toggle กลับไปเป็น `0` ในขณะที่ฝั่งรับยังค้างค่า `1` จากรอบก่อน ทั้งสองฝั่งจะรอขอบสัญญาณของกันและกันจนติดสภาวะ Deadlock ครับ

**佐藤主席 (Sato):**  
「車載や宇宙・防衛分野の機能安全（ISO 26262 / DO-254）では、個別ドメインのリセットによる回路停止は致命的欠陥（Fatal Hazard）と判定される。今回はスループットの要求値が最大でも毎秒2メガワード程度なのだから、迷わず**4相式レベルハンドシェイク（4-Phase Level Handshake）**に切り替えなさい。4相式なら、REQもACKもアイドル時には必ずゼロに戻る（Return-to-Zero）ため、どちらが単独リセットされても次のサイクルで確実に自己復旧できる。」  
*(Shasai ya uchū bōei bun'ya no kinō anzen dewa, kobetsu domein no risetto ni yoru kairo teishi wa chimeiteki kekkan to hantei sareru. Konkai wa surūputto no yōkyūchi ga saidai demo maibyō 2 mega-wādo teido na no dakara, mayowazu yonsō-shiki reberu handosheiku ni kirikaenasai. Yonsō-shiki nara, REQ mo ACK mo aidoru-ji ni wa kanarazu zero ni modoru tame, dochira ga tandoku risetto saretemo tsugi no saikuru de kakujitsu ni jiko fukkyū dekiru.)*  
**คำแปล:** ในมาตรฐาน Functional Safety ของยานยนต์และอากาศยานอวกาศ การที่วงจรหยุดทำงานเพราะการรีเซ็ตแยกโดเมนถือเป็นข้อบกพร่องร้ายแรงระดับวิกฤต ในงานนี้ข้อกำหนด Throughput สูงสุดอยู่ที่เพียงประมาณ 2 Mega-words ต่อวินาทีเท่านั้น ดังนั้นอย่าลังเล จงเปลี่ยนไปใช้ 4-Phase Level Handshake ทันที ระบบ 4-Phase ทั้ง REQ และ ACK จะต้องคืนค่ากลับสู่ศูนย์ในสภาวะ IDLE เสมอ ไม่ว่าฝั่งใดจะถูกรีเซ็ตเดี่ยว มันจะสามารถกู้คืนระบบกลับมาได้เอง $100\%$ ในไซเคิลถัดไป

**クリサダ (Kritsada):**  
「承知いたしました！4相レベルハンドシェイク回路へ即時変更いたします。さらに念のため、送信側FSM内に32クロックでタイムアウトするハードウェア・ウォッチドッグタイマを追加し、万が一ACKの応答が途絶えた場合でもアラートを発報してIDLEへ自律復帰するフォールトトレラント設計を盛り込みます。」  
*(Shōchi itashimashita! Yonsō reberu handosheiku kairo e sokuji henkō itashimasu. Sarani nen no tame, sōshin-gawa FSM nai ni 32 kurokku de taimuauto suru hādowea wocchidoggu taima wo tsuika shi, man'gaichi ACK no ōtō ga todaeta baai demo arāto wo happō shite IDLE e jiritsu fukkyū suru fōruto toreranto sekkei wo morikomimasu.)*  
**คำแปล:** รับทราบครับ! ผมจะแก้ไขเป็นวงจร 4-Phase Level Handshake โดยทันที และจะเพิ่ม Hardware Watchdog Timer ขนาด 32 ไซเคิลเข้าไปใน FSM ฝั่งส่ง เผื่อกรณีฉุกเฉินที่ไม่มีสัญญาณ ACK ตอบกลับมา ระบบจะแจ้งเตือนและฟื้นฟูกลับสู่สถานะ IDLE ได้เองโดยอัตโนมัติตามหลัก Fault-Tolerant ครับ

**佐藤主席 (Sato):**  
「素晴らしい判断だ。設計変更後、リセットの非同期アサート・同期デアサート（Recovery/Removal）のSTAタイミングレポートと、SVAによるデッドロックフリー検証ログを添付して再提出してくれたまえ。」  
*(Subarashī handan da. Sekkei henkō-go, risetto no hidōki asāto dōki deasāto no STA taimingu repōto to, SVA ni yoru deddorokku-furī kenshō rogu wo tempu shite sai-teishutsu shite kuretamae.)*  
**คำแปล:** การตัดสินใจยอดเยี่ยมมาก หลังแก้ไขแบบเสร็จ ให้นำรายงาน STA Timing ของ Reset Recovery/Removal และบันทึกผลการตรวจสอบ Deadlock-Free ด้วย SVA แนบมาในการยื่นตรวจแบบรอบใหม่ด้วยนะ

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การเปรียบเทียบ Latency และ Throughput ระหว่าง 4-Phase และ 2-Phase Handshake
ในระบบประมวลผลสัญญาณควบคุมดาวเทียม สัญญาณนาฬิกาฝั่งส่งมีค่า $f_{src} = 100\text{ MHz}$ ($T_{src} = 10.0\text{ ns}$) และสัญญาณนาฬิกาฝั่งรับมีค่า $f_{dst} = 33.33\text{ MHz}$ ($T_{dst} = 30.0\text{ ns}$) วงจร Synchronizer ทั้งบนขา REQ และ ขา ACK ใช้แบบ 2-Stage Flip-Flop ($N_{sync} = 2$ ทั้งสองฝั่ง):
* ค่าความหน่วงเวลาของสายส่ง Interconnect ระหว่างข้ามโดเมนมีค่าน้อยมากจนตัดทิ้งได้
* สเตตแมชชีนของทั้งสองฝั่งตอบสนองใน 1 ไซเคิลทันทีที่สัญญาณ Synchronized เข้าสู่สถานะที่ถูกต้อง

จงคำนวณหาค่า **Round-Trip Latency ($T_{RTT}$)** และ **Throughput สูงสุดทางทฤษฎี ($\text{Words/sec}$)** ของวงจรแบบ **4-Phase Handshake** และแบบ **2-Phase Handshake**

---

#### ตัวเลือก:
* **ก)** 
  * 4-Phase: $T_{RTT} = 240\text{ ns}$, $\text{Throughput} = 4.17\text{ Mwords/s}$
  * 2-Phase: $T_{RTT} = 120\text{ ns}$, $\text{Throughput} = 8.33\text{ Mwords/s}$
* **ข)** 
  * 4-Phase: $T_{RTT} = 180\text{ ns}$, $\text{Throughput} = 5.55\text{ Mwords/s}$
  * 2-Phase: $T_{RTT} = 90\text{ ns}$, $\text{Throughput} = 11.11\text{ Mwords/s}$
* **ค)** 
  * 4-Phase: $T_{RTT} = 160\text{ ns}$, $\text{Throughput} = 6.25\text{ Mwords/s}$
  * 2-Phase: $T_{RTT} = 80\text{ ns}$, $\text{Throughput} = 12.50\text{ Mwords/s}$
* **ง)** 
  * 4-Phase: $T_{RTT} = 360\text{ ns}$, $\text{Throughput} = 2.78\text{ Mwords/s}$
  * 2-Phase: $T_{RTT} = 180\text{ ns}$, $\text{Throughput} = 5.55\text{ Mwords/s}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การคำนวณรอบการเดินทางครึ่งรอบ (One-Way Crossing Latency):
* **ขาไป (Src $\to$ Dst):** สัญญาณ REQ ถูกขับออกจาก Register ในโดเมน $CLK_{src}$ เข้าสู่ 2-FF Synchronizer ในโดเมน $CLK_{dst}$
  ต้องใช้เวลา $N_{sync} = 2$ ไซเคิลของ $CLK_{dst}$ บวกกับ 1 ไซเคิลสำหรับการประเมิน FSM/Latch Data:
  $$t_{fwd} = (N_{sync} + 1) \cdot T_{dst} = (2 + 1) \times 30.0\text{ ns} = 3 \times 30.0\text{ ns} = 90.0\text{ ns}$$
* **ขากลับ (Dst $\to$ Src):** สัญญาณ ACK ถูกขับออกจาก Register ในโดเมน $CLK_{dst}$ เข้าสู่ 2-FF Synchronizer ในโดเมน $CLK_{src}$
  ต้องใช้เวลา $N_{sync} = 2$ ไซเคิลของ $CLK_{src}$ บวกกับ 1 ไซเคิลสำหรับการประเมิน FSM ในฝั่งส่ง:
  $$t_{rev} = (N_{sync} + 1) \cdot T_{src} = (2 + 1) \times 10.0\text{ ns} = 3 \times 10.0\text{ ns} = 30.0\text{ ns}$$

##### 2. การคำนวณ Round-Trip Latency และ Throughput ของ Two-Phase Handshake:
ในระบบ Two-Phase การส่งข้อมูล 1 Word ต้องการเพียง 1 รอบการเดินทางไปและกลับ ($\text{Trans 1} + \text{Trans 2}$):
$$T_{RTT,2P} = t_{fwd} + t_{rev} = 90.0\text{ ns} + 30.0\text{ ns} = 120.0\text{ ns}$$
$$\text{Throughput}_{2P} = \frac{1}{T_{RTT,2P}} = \frac{1}{120.0 \times 10^{-9}\text{ s}} \approx 8,333,333\text{ Words/s} = 8.33\text{ Mwords/s}$$

##### 3. การคำนวณ Round-Trip Latency และ Throughput ของ Four-Phase Handshake:
ในระบบ Four-Phase ต้องมีรอบการปลดสัญญาณกลับสู่ศูนย์ (Return-to-Zero: Phase 3 + Phase 4) เพิ่มขึ้นอีกเท่าตัว:
$$T_{RTT,4P} = 2 \cdot (t_{fwd} + t_{rev}) = 2 \times 120.0\text{ ns} = 240.0\text{ ns}$$
$$\text{Throughput}_{4P} = \frac{1}{T_{RTT,4P}} = \frac{1}{240.0 \times 10^{-9}\text{ s}} \approx 4,166,666\text{ Words/s} = 4.17\text{ Mwords/s}$$

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** คำนวณโดยใช้สูตรผิดพลาดโดยคิดเพียง $N_{sync} \cdot T$ และลืมบวก 1 ไซเคิลสำหรับการทำงานของ FSM Logic ปลายทาง
* **ข้อ ค):** สับสนนำค่าเฉลี่ยของทั้งสองความถี่มาคำนวณ
* **ข้อ ง):** คิดจำนวนสเตจของ Synchronizer ซ้ำซ้อนเกินจริง ($N_{sync} = 3$)

---

### ข้อที่ 2: การวิเคราะห์สาเหตุของ Race Condition ใน Handshake Datapath
พิจารณาวงจร 4-Phase Handshake ที่วิศวกรออกแบบขึ้น โดยไม่มีการใช้ Hold Register ในฝั่งส่ง (No `src_data_hold` buffer) แต่นำสัญญาณ `src_data_in` จากภายนอกมาต่อเข้าขา D ของ Register ปลายทางโดยตรง:
```verilog
// โค้ดของวิศวกรที่มีบั๊ก
always @(posedge clk_dst) begin
    if (req_sync2 && !ack_dst) begin
        dst_data_out <= src_data_in; // ต่อตรงจากบัสต้นทางโดยไม่ผ่าน Hold Register!
        ack_dst      <= 1'b1;
    end
end
```
เหตุการณ์ใดต่อไปนี้จะก่อให้เกิด **Data Corruption** อย่างแน่นอนที่สุด?

---

#### ตัวเลือก:
* **ก)** ขา `src_data_in` เปลี่ยนค่าทันทีหลังจากที่โมดูลต้นทางยกสัญญาณ `src_valid_in` แต่สัญญาณ `src_req` ยังเดินทางไม่ถึงโดเมนปลายทาง
* **ข)** โมดูลต้นทางทำงานที่ความถี่ $10\text{ MHz}$ และโมดูลปลายทางทำงานที่ความถี่ $200\text{ MHz}$
* **ค)** วงจร Synchronizer บนขา ACK ใช้ฟลิปฟล็อป 3 สเตจแทนที่จะเป็น 2 สเตจ
* **ง)** ฝั่งปลายทางปลดสัญญาณ `ack_dst <= 1'b0` ภายใน 1 ไซเคิลหลังจากที่ `req_sync2` กลายเป็นศูนย์

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **กฎเหล็กของ Handshake Datapath:**
   ข้อมูลที่จะถูกส่งข้ามโดเมนนาฬิกาจะต้องถูก **Latching และตรึงไว้ใน Local Holding Register ของฝั่งส่ง (`src_data_hold`)** ตลอดระยะเวลาที่กระบวนการ Handshake กำลังดำเนินอยู่
2. **ความผิดพลาดของการต่อตรงโดยไม่มี Buffer:**
   หากต้นทางไม่ได้คัดลอกข้อมูลลง Holding Register แต่นำ `src_data_in` ซึ่งเป็น Dynamic Bus ภายนอกมาต่อข้ามโดเมนตรงๆ:
   * เมื่อโมดูลภายนอกยก `valid` แล้วเปลี่ยนค่า `src_data_in` ไปเป็นข้อมูลคำใหม่ในไซเคิลถัดไป
   * ในขณะนั้น สัญญาณ `src_req` เพิ่งจะเริ่มเดินทางผ่าน 2-FF Synchronizer ของโดเมนปลายทาง (ซึ่งต้องใช้เวลาอย่างน้อย 2-3 ไซเคิลของปลายทาง)
   * เมื่อ `req_sync2` ยกขึ้นเป็น `1` ในที่สุด ข้อมูลบนสายส่ง `src_data_in` ได้กลายเป็นข้อมูลของแพ็กเก็ตใหม่ไปแล้ว!
   * ฝั่งปลายทางจะ Latch ข้อมูลใหม่นั้นลงไป ส่งผลให้ข้อมูลคำแรกสูญหาย และเกิด Data Corruption อย่างไม่อาจหลีกเลี่ยงได้!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** ความถี่ต้นทางช้ากว่าปลายทาง ยิ่งทำให้ข้อมูลค้างอยู่นานขึ้น ไม่ได้เป็นสาเหตุโดยตรงของ Race Condition หากไม่มีการเปลี่ยนค่าบัสภายนอก
* **ข้อ ค):** การเพิ่มสเตจ Synchronizer เป็น 3 สเตจ ช่วยเพิ่ม MTBF ให้สูงขึ้น แม้จะเพิ่ม Latency เล็กน้อยแต่ไม่ได้ทำให้เกิด Data Corruption
* **ข้อ ง):** เป็นพฤติกรรมปกติที่ถูกต้องสมบูรณ์ของ Phase 4 ในโปรโตคอล 4-Phase Handshake

---

### ข้อที่ 3: เกณฑ์การตัดสินใจทางสถาปัตยกรรม (Architectural Decision Point)
ในโครงการพัฒนาระบบควบคุมหัวฉีดเครื่องยนต์อากาศยาน (FADEC - Full Authority Digital Engine Control) ทีมวิศวกรต้องส่งข้อมูล Telemetry ขนาด $64\text{ บิต}$ ข้ามระหว่างโดเมนควบคุมหลัก ($f_{core} = 150\text{ MHz}$) ไปยังโดเมนสื่อสารภายนอก ($f_{comm} = 25\text{ MHz}$) โดยมีข้อกำหนดทางวิศวกรรมดังนี้:
1. ปริมาณ Throughput ที่ต้องการ: ไม่เกิน $500,000\text{ Transactions/second}$ ($0.5\text{ Mwords/s}$)
2. ทรัพยากร BRAM บน FPGA ถูกใช้งานไปแล้ว $98\%$ (แทบไม่เหลือ Block RAM เลย)
3. ระบบต้องผ่านการรับรองความปลอดภัยระดับสูงสุด **DO-254 DAL-A** ซึ่งต้องการให้วงจรสามารถพิสูจน์ Formal Verification ได้ง่าย และไม่มีความเสี่ยงเรื่อง Pointer Wrap-Around

สถาปัตยกรรม CDC รูปแบบใดต่อไปนี้ **มีความเหมาะสมสูงสุดทางวิศวกรรม** ภายใต้เงื่อนไขทั้งหมดข้างต้น?

---

#### ตัวเลือก:
* **ก)** Dual-Clock Asynchronous FIFO โดยใช้ Block RAM เพื่อความเร็วสูงสุด
* **ข)** 4-Phase Handshake Synchronizer โดยใช้ Distributed Holding Registers และ 2-FF Synchronizers พร้อม Hardware Timeout Watchdog
* **ค)** 2-Phase Handshake Synchronizer โดยตัดวงจร Reset ทิ้งเพื่อป้องกัน Polarity Inversion
* **ง)** Bit-by-Bit 2-FF Synchronizer 64 ชุดขนานกันเพื่อประหยัดทรัพยากรลอจิกที่สุด

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์การตัดสินใจเชิงวิศวกรรมระดับสูง (Senior Architecture Selection):
1. **การวิเคราะห์ด้าน Throughput:**
   * ความต้องการของระบบคือเพียง $0.5\text{ Mwords/s}$ ($T_{interval} = 2,000\text{ ns}$)
   * จากการคำนวณในข้อ 1 วงจร 4-Phase Handshake ระหว่าง $150\text{ MHz}$ ($6.67\text{ ns}$) และ $25\text{ MHz}$ ($40\text{ ns}$):
     $$T_{RTT,4P} = 2 \cdot [ (2+1)(40\text{ ns}) + (2+1)(6.67\text{ ns}) ] = 2 \cdot [ 120\text{ ns} + 20\text{ ns} ] = 280\text{ ns}$$
     สามารถรองรับ Throughput ได้สูงถึง $\frac{1}{280\text{ ns}} \approx 3.57\text{ Mwords/s}$ ซึ่งเกินพอสำหรับความต้องการ $0.5\text{ Mwords/s}$ ถึง 7 เท่า!
2. **การวิเคราะห์ด้านทรัพยากร (Resource Constraints):**
   * บล็อก RAM ถูกใช้งานไปแล้ว $98\%$ การเลือกใช้ Asynchronous BRAM FIFO (ข้อ ก) เป็นไปไม่ได้ในทางกายภาพและเสี่ยงต่อการสังเคราะห์ไม่ผ่าน
   * 4-Phase Handshake ใช้เพียง Slice LUT และ Flip-Flop ทั่วไป (Distributed Logic) เพียงไม่กี่สิบตัว ไม่ใช้ BRAM เลยแม้แต่บล็อกเดียว
3. **การวิเคราะห์ด้านความปลอดภัยและการรับรอง DO-254 DAL-A:**
   * วงจร 4-Phase มีสถานะที่คาดเดาได้แน่นอน (Deterministic FSM) มีสภาวะ Return-to-Zero ในตัว และทนทานต่อการรีเซ็ต
   * การเพิ่ม Hardware Timeout Watchdog ช่วยรับประกัน Liveness Proof ได้ $100\%$ ใน Formal Verification
   * ในขณะที่ Asynchronous FIFO ต้องใช้โค้ด Gray-code Pointer และการพิสูจน์ Full/Empty flags ซึ่งซับซ้อนกว่ามากในการทำ DAL-A Sign-Off

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ขัดแย้งกับข้อจำกัดเรื่อง BRAM Usage ($98\%$) อย่างรุนแรง
* **ข้อ ค):** การตัด Reset ทิ้งในระบบอากาศยานระดับ DAL-A เป็นสิ่งที่ผิดมาตรฐานความปลอดภัยสากลอย่างสิ้นเชิง และเสี่ยงต่อสภาวะ Uninitialized State
* **ข้อ ง):** การใช้ Bit-by-Bit 2-FF บนบัส 64 บิต เป็นข้อห้ามเด็ดขาด (Strictly Forbidden) ที่จะทำให้ระบบตกการรับรองมาตรฐาน DO-254 ทันทีจากปัญหา Bus Skew และ Data Corruption
