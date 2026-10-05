# Lesson 129: FPGA State Machine Part 9 - CDC & Asynchronous Domains (非同期ドメイン間FSMインターフェース: Handshake Protocols, Async FIFO, Gray-Code Pointers & Quasi-Static Sync)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ฟิสิกส์ของการข้ามโดเมนสัญญาณนาฬิกา (Physics of Clock Domain Crossing: CDC)
ในสถาปัตยกรรมระบบบนชิป (SoC) หรือ FPGA ยุคใหม่ วงจรแทบทั้งหมดจัดเป็นระบบ **หลายโดเมนสัญญาณนาฬิกา (Multi-Clock Domain Systems)** โดยมีสเตตแมชชีนหลายตัวทำงานที่ความถี่และเฟสที่แยกขาดจากกันโดยสิ้นเชิง เช่น ตัวควบคุมกล้องประมวลผลพิกเซลทำงานที่ $f_{clk1} = 148.5\text{ MHz}$ ในขณะที่ตัวควบคุมหน่วยความจำ DDR4 ทำงานที่ $f_{clk2} = 266.67\text{ MHz}$

ความสัมพันธ์ทางเฟสระหว่างสัญญาณนาฬิกาทั้งสองเป็นฟังก์ชันที่ไม่เป็นคาบ (Asynchronous / Plesiochronous):

$$\Delta \theta(t) = 2\pi (f_{clk1} - f_{clk2})t + \phi_0$$

```
               หายนะของการส่งเวกเตอร์สเตตหลายบิตข้ามโดเมนตรงๆ
   
   Clock Domain A (148.5 MHz)                         Clock Domain B (266.67 MHz)
   +-------------------------+                         +-------------------------+
   | FSM A State Register    |                         | FSM B Capture Logic     |
   |                         |  Net Skew t_skew = 850ps|                         |
   | State[0] 1 -> 0 --------+----[ 2-FF Sync ]--------+-----> Bit 0 sampled     |
   |                         |                         |                         |
   | State[1] 0 -> 1 --------+----[ 2-FF Sync ]--------+-----> Bit 1 sampled     |
   |                         |                         |                         |
   | State[2] 0 -> 0 --------+----[ 2-FF Sync ]--------+-----> Bit 2 sampled     |
   +-------------------------+                         +-------------------------+
   
   การเปลี่ยนสถานะเดิม: 3'b001 (STATE_A) -> 3'b010 (STATE_B)
   แต่เนื่องจาก Bit 0 ถึงช้ากว่า Bit 1 (เกิด Routing Delay Skew):
   - มีช่วงเวลาหนึ่งที่โดเมน B สุ่มตรวจพบ: 3'b011 (STATE_C: ABORT TRAP!)
   ผลลัพธ์: FSM B กระโดดเข้าสู่สถานะผิดพลาดโดยที่ FSM A ไม่เคยสั่งเลยแม้แต่น้อย!
```

#### 1.1.1 กับดักมรณะ: Multi-bit CDC Convergence Bug
ความผิดพลาดที่พบบ่อยที่สุดของวิศวกรคือ: **"การนำสัญญาณเวกเตอร์หลายบิต (Multi-bit Bus) เช่น บิตสถานะ `state[2:0]` ไปต่อผ่าน 2-FF Synchronizer ทีละบิตขนานกัน"**

ในระดับฟิสิกส์ซิลิคอน:
1. สายสัญญาณแต่ละเส้นมีความยาวและการเลี้ยวผ่าน Switch Matrix ไม่เท่ากัน ทำให้เกิด **ความหน่วงเวลาเหลื่อมกัน (Data Bus Skew: $t_{skew} = \max(t_{net\_i}) - \min(t_{net\_j})$)**
2. เกณฑ์แรงดันและเวลาตอบสนองของ Flip-Flop แต่ละตัวมีความแปรปรวนจากกระบวนการผลิต (Process Variation: PVT)
3. ส่งผลให้ในจังหวะเปลี่ยนสเตต สัญญาณนาฬิกาปลายทางจะสุ่มจับได้ **"สถานะผี (Chimeric / Intermediate Invalid States)"** ที่ไม่เคยมีอยู่จริงในสารบบ ทำให้ FSM ปลายทางทำงานวิปริตทันที!

---

### 1.2 โพรโทคอลการเชื่อมต่อข้ามโดเมนที่เชื่อถือได้ (Robust CDC Interface Protocols)

เพื่อแก้ปัญหา Multi-bit CDC วิศวกรอาวุโสจะเลือกใช้ 1 ใน 3 โพรโทคอลมาตรฐานสากลดังต่อไปนี้:

```
+------------------------------------+------------------+---------------------------------------------------+
| โพรโทคอล                           | Latency          | ขอบเขตการใช้งานที่เหมาะสม (Best Applications)    |
+------------------------------------+------------------+---------------------------------------------------+
| 1. Four-Phase Handshake (Level)    | สูง ($4-6$ clocks)| ส่งสัญญาณควบคุม/คำสั่งนานๆ ครั้ง (Control/Status)  |
| 2. Two-Phase Handshake (Toggle)    | ปานกลาง ($2-4$ clk)| ส่งพัลส์เหตุการณ์ที่ต้องการความเร็วปานกลาง        |
| 3. Asynchronous FIFO (Gray Code)   | ต่ำสุด (1-2 clk) | ส่งสตรีมข้อมูลต่อเนื่องข้ามความถี่ (High Throughput)|
| 4. Quasi-Static Qualifier (MCP)    | ต่ำ              | ข้อมูลอยู่นิ่งหลายสิบไซเคิล แล้วส่งพัลส์ซิงค์ตัวเดียว|
+------------------------------------+------------------+---------------------------------------------------+
```

#### 1.2.1 Four-Phase Handshake Protocol (ระดับสัญญาณแบบ Return-to-Zero: RZ)
เป็นโพรโทคอลที่มีความปลอดภัยสูงสุดในโลกดิจิทัล โดยมีขั้นตอนการทำงาน 4 จังหวะสมบูรณ์:

```
               Four-Phase Handshake Timing Sequence
   
   FSM_A (Src)  ___/¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯\______________________ (Req)
                    [ Data Stable Valid ]
   
   FSM_B (Dst)  _________/¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯\_________________ (Ack)
                          ^                     ^
                          |                     |
                Phase 1: Req สูง      Phase 3: Req ต่ำ
                Phase 2: Ack สูง      Phase 4: Ack ต่ำ
```

1. **Phase 1 (Request Assert):** โมดูลส่ง (Src) นำข้อมูลหรือสเตตวางบนบัสจนนิ่ง แล้วยกสัญญาณ `req = 1`
2. **Phase 2 (Acknowledge Assert):** โมดูลรับ (Dst) ซิงโครไนซ์ `req` ผ่าน 2-FF แล้วทำการบันทึกข้อมูลเข้าสู่ FSM ของตน จากนั้นยกสัญญาณตอบรับ `ack = 1`
3. **Phase 3 (Request Deassert):** โมดูลส่งซิงโครไนซ์ `ack` กลับมา เมื่อพบว่า `ack = 1` จึงปลดสัญญาณ `req = 0` (ห้ามเปลี่ยนข้อมูลเด็ดขาดจนกว่าจะเสร็จสิ้น)
4. **Phase 4 (Acknowledge Deassert):** โมดูลรับเห็น `req = 0` จึงปลดสัญญาณ `ack = 0` เป็นอันสิ้นสุด 1 ธุรกรรมอย่างสมบูรณ์แบบ

---

### 1.3 สถาปัตยกรรม Quasi-Static Multi-Cycle Path (MCP Formulation)
หากข้อมูลหรือเวกเตอร์สถานะมีคุณสมบัติเป็น **Quasi-Static (คงที่อยู่นิ่งเป็นเวลานานหลายรอบสัญญาณนาฬิกา)** เราไม่จำเป็นต้องแปลงข้อมูลเป็น Gray Code หรือสร้าง FIFO ให้สิ้นเปลือง

เราใช้เทคนิค **MCP Formulation with Control Synchronizer**:
1. ข้อมูลหลายบิต (`data_bus[31:0]`) ส่งตรงข้ามโดเมนโดยไม่ต้องผ่าน Flip-Flop ซิงโครไนเซอร์
2. มีเพียงสัญญาณควบคุมบิตเดียว (`data_valid`) เท่านั้นที่ถูกส่งผ่าน 2-FF Synchronizer
3. เขียน Timing Constraint ในไฟล์ XDC เพื่อสั่งให้เครื่องมือ STA รับทราบข้อจำกัด:

```tcl
# XDC Constraint สำหรับ Quasi-Static MCP Formulation
set_max_delay -from [get_cells u_src/data_reg*] -to [get_cells u_dst/capture_reg*] \
              -datapath_only [get_property -min PERIOD [get_clocks -of_objects [get_pins u_dst/clk]]]
```

คำสั่ง `-datapath_only` จะสั่งให้ Vivado ควบคุมไม่ให้ความหน่วงสายไฟ ($t_{skew}$) ระหว่างบิตข้อมูลยาวเกินกว่า 1 คาบสัญญาณนาฬิกาของโดเมนรับ เพื่อรับประกันว่าเมื่อสัญญาณ `valid` เดินทางมาถึง ข้อมูลทุกบิตจะต้องเดินทางมาถึงและนิ่งสนิทแล้วอย่างแน่นอน!

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Four-Phase CDC Handshake Controller สำหรับ FSM

```systemverilog
//=============================================================================
// Module: cdc_four_phase_handshake.sv
// Description: Industrial-Grade Robust CDC Handshake Interface for Inter-FSM Comms
// Target: AMD UltraScale+ / Intel Stratix 10 / Microchip PolarFire
//=============================================================================
`timescale 1ns / 1ps

module cdc_four_phase_handshake #(
    parameter int DWIDTH = 8
)(
    // โดเมนส่งสัญญาณ (Source Clock Domain)
    input  logic              src_clk,
    input  logic              src_rst_n,
    input  logic              src_send_req,
    input  logic [DWIDTH-1:0] src_data_in,
    output logic              src_busy,
    output logic              src_done_pulse,

    // โดเมนรับสัญญาณ (Destination Clock Domain)
    input  logic              dst_clk,
    input  logic              dst_rst_n,
    output logic              dst_valid_pulse,
    output logic [DWIDTH-1:0] dst_data_out
);

    // สัญญาณควบคุมระดับ
    logic              req_src;
    logic              ack_dst;
    logic [DWIDTH-1:0] data_holding_reg;

    //-------------------------------------------------------------------------
    // 1. Source Domain FSM: ควบคุมฝั่งส่ง
    //-------------------------------------------------------------------------
    typedef enum logic [1:0] {
        SRC_IDLE = 2'b00,
        SRC_WAIT_ACK_HIGH = 2'b01,
        SRC_WAIT_ACK_LOW  = 2'b10
    } src_state_t;

    src_state_t src_state;

    // ซิงโครไนเซอร์รับ Ack กลับมาจากฝั่ง Dst
    (* ASYNC_REG = "TRUE" *) logic [1:0] sync_ack_to_src;
    always_ff @(posedge src_clk) begin
        if (!src_rst_n) sync_ack_to_src <= 2'b00;
        else            sync_ack_to_src <= {sync_ack_to_src[0], ack_dst};
    end
    wire ack_synced_src = sync_ack_to_src[1];

    always_ff @(posedge src_clk) begin
        if (!src_rst_n) begin
            src_state        <= SRC_IDLE;
            req_src          <= 1'b0;
            data_holding_reg <= '0;
            src_busy         <= 1'b0;
            src_done_pulse   <= 1'b0;
        end else begin
            src_done_pulse <= 1'b0;

            case (src_state)
                SRC_IDLE: begin
                    if (src_send_req) begin
                        data_holding_reg <= src_data_in; // ล็อกข้อมูลให้นิ่ง
                        req_src          <= 1'b1;         // ยก Req (Phase 1)
                        src_busy         <= 1'b1;
                        src_state        <= SRC_WAIT_ACK_HIGH;
                    end else begin
                        src_busy <= 1'b0;
                    end
                end

                SRC_WAIT_ACK_HIGH: begin
                    if (ack_synced_src) begin // ปลายทางรับแล้ว (Phase 2)
                        req_src   <= 1'b0;    // ปลด Req ลง (Phase 3)
                        src_state <= SRC_WAIT_ACK_LOW;
                    end
                end

                SRC_WAIT_ACK_LOW: begin
                    if (!ack_synced_src) begin // ปลายทางปลด Ack แล้ว (Phase 4)
                        src_done_pulse <= 1'b1;
                        src_busy       <= 1'b0;
                        src_state      <= SRC_IDLE;
                    end
                end

                default: src_state <= SRC_IDLE;
            endcase
        end
    end

    //-------------------------------------------------------------------------
    // 2. Destination Domain FSM: ควบคุมฝั่งรับ
    //-------------------------------------------------------------------------
    typedef enum logic {
        DST_IDLE     = 1'b0,
        DST_WAIT_REQ_LOW = 1'b1
    } dst_state_t;

    dst_state_t dst_state;

    // ซิงโครไนเซอร์รับ Req จากฝั่ง Src
    (* ASYNC_REG = "TRUE" *) logic [1:0] sync_req_to_dst;
    always_ff @(posedge dst_clk) begin
        if (!dst_rst_n) sync_req_to_dst <= 2'b00;
        else            sync_req_to_dst <= {sync_req_to_dst[0], req_src};
    end
    wire req_synced_dst = sync_req_to_dst[1];

    always_ff @(posedge dst_clk) begin
        if (!dst_rst_n) begin
            dst_state       <= DST_IDLE;
            ack_dst         <= 1'b0;
            dst_valid_pulse <= 1'b0;
            dst_data_out    <= '0;
        end else begin
            dst_valid_pulse <= 1'b0;

            case (dst_state)
                DST_IDLE: begin
                    if (req_synced_dst) begin
                        dst_data_out    <= data_holding_reg; // บันทึกข้อมูลที่นิ่งแล้ว
                        dst_valid_pulse <= 1'b1;
                        ack_dst         <= 1'b1;             // ยก Ack (Phase 2)
                        dst_state       <= DST_WAIT_REQ_LOW;
                    end
                end

                DST_WAIT_REQ_LOW: begin
                    if (!req_synced_dst) begin // ต้นทางปลด Req แล้ว (Phase 3)
                        ack_dst   <= 1'b0;     // ปลด Ack (Phase 4)
                        dst_state <= DST_IDLE;
                    end
                end

                default: dst_state <= DST_IDLE;
            endcase
        end
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในระบบประมวลผลกล้องตรวจการณ์ความเร็วสูง (4K Industrial Machine Vision System) โมดูลประมวลผลพิกเซล (ISP Pipeline) ทำงานที่สัญญาณนาฬิกา $148.5\text{ MHz}$ ส่งสัญญาณควบคุมสถานะเฟรม `frame_fsm_state[2:0]` ไปยังโมดูล DMA Controller ที่ทำงานบนสัญญาณนาฬิการะบบ $266.67\text{ MHz}$ วิศวกรเชื่อมต่อบัสสถานะขนาด 3 บิตนี้ผ่านไอซีและโมดูลซิงโครไนเซอร์ 2-FF แบบแยกทีละบิตอิสระ

**ผลลัพธ์ที่ล้มเหลว:** ระบบทำงานผ่านการทดสอบในแล็บช่วงแรกได้ราบรื่น แต่เมื่อนำไปทดสอบต่อเนื่องในสายการผลิตจริง (Aging Test) ทุกๆ ประมาณ $10 - 15\text{ นาที}$ จะเกิดอาการภาพวิดีโอกระตุกและเฟรมภาพเลื่อนแนวนอน (Frame Tearing / Horizontal Line Shift) อย่างรุนแรง บันทึก Log ของ DMA ฟ้องว่าเกิด `Spurious Frame Abort Event` ขึ้นแบบสุ่ม

```
                 กลไกการเกิด Chimeric State จาก Multi-bit Skew
   
   ISP Clock (148.5M)  ____/¯¯¯¯\___________________________________
   
   ISP FSM State:      [ 3'b001 (START) ]------>[ 3'b010 (STREAM) ]
   
   DMA Clock (266.67M) _/¯\_/¯\_/¯\_/¯\_/¯\_/¯\_/¯\_/¯\_/¯\_/¯\_/¯\_
                                     | (ขอบ Sampling ของ DMA)
                                     v
   Bit 1 เดินทางเร็ว: มาถึงและเปลี่ยนเป็น '1' เรียบร้อย
   Bit 0 เดินทางช้า (ติด Routing Delay ข้าม SLR): ยังค้างอยู่ที่ '1'
   
   เวกเตอร์ที่ DMA สุ่มได้: {Bit2=0, Bit1=1, Bit0=1} = 3'b011 !
   ความหมายของ 3'b011 ในระบบ: [ ST_EMERGENCY_ABORT ] !!
   -> DMA สั่งรีเซ็ต Buffer ชั่วคราวทันที -> ภาพฉีกขาด (Frame Tearing)!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมภาพวิดีโอถึงเกิดอาการฉีกขาดและเลื่อนบรรทัดทุกๆ 15 นาที?**
   * *ตอบ:* ตัวควบคุม DMA บนสัญญาณนาฬิกา $266.67\text{ MHz}$ สั่งรีเซ็ตตัวชี้แอดเดรสและตัดเฟรมภาพทิ้งกลางคัน
2. **ทำไม DMA ถึงสั่งตัดเฟรมภาพทิ้งกลางคัน?**
   * *ตอบ:* วงจร FSM ของ DMA ได้รับรหัสสถานะ `3'b011` ซึ่งตรงกับคำสั่ง `ST_EMERGENCY_ABORT`
3. **ทำไมรหัสสถานะถึงกลายเป็นคำสั่ง Abort ทั้งที่กล้องไม่ได้ส่งคำสั่งนี้?**
   * *ตอบ:* วงจรซิงโครไนเซอร์ขาเข้าอ่านค่าบิตผสมกันระหว่างสถานะเก่า (`3'b001`) และสถานะใหม่ (`3'b010`)
4. **ทำไมถึงเกิดการอ่านค่าบิตผสมกันระหว่างสองสถานะได้?**
   * *ตอบ:* บิตทั้งสามเดินทางข้ามโดเมนสัญญาณนาฬิกาด้วยสายสัญญาณที่มีความหน่วงเวลาไม่เท่ากัน (Data Skew $> 850\text{ ps}$)
5. **ทำไมวิศวกรจึงส่งบัสหลายบิตข้ามโดเมนโดยตรงโดยไม่มีการ Handshake?**
   * *ตอบ:* วิศวกรเข้าใจผิดคิดว่า การนำ 2-FF Synchronizer มาต่อคร่อมทุกบิตของบัส เป็นวิธีที่ถูกต้องสำหรับการส่งข้อมูลข้ามโดเมน โดยไม่รู้หลักการว่า **"ห้ามซิงโครไนซ์บัสหลายบิตด้วย 2-FF อิสระเด็ดขาด"**

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ Multi-bit CDC
   
   ความรู้ความเข้าใจเรื่อง CDC (Personnel)       การออกแบบสถาปัตยกรรม (Architecture)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ไม่เข้าใจเรื่อง เข้าใจผิดว่า                  ใช้ 2-FF      ไม่มี Handshake
   Bus Skew      ใส่ 2-FF ครบ                   แยกเดี่ยว     หรือ Asynchronous
   และ CDC       ทุกบิตแล้วจะปลอดภัย            บนบัสหลายบิต  FIFO กั้นบัส
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> ภาพวิดีโอฉีกขาด
                                                                |     จาก Chimeric State
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   สายไฟข้าม SLR  การจัดวาง                     ไม่ได้รันคำสั่ง ขาด SVA ตรวจจับ
   มีความยาวต่างกัน FF อยู่คนละ                  report_cdc    Unmapped Transition
   จน Skew > 850ps Slice                        ใน Vivado      ในระดับ Simulation
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   ความแปรปรวนของซิลิคอน (Silicon Routing)       ขั้นตอนการตรวจสอบ (Verification)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: รันคำสั่งตรวจสอบ CDC ด้วย Vivado Synthesis/Implementation
ใน Vivado Tcl Console ให้รันคำสั่งตรวจหา Multi-bit Synchronizer Violation:
```tcl
report_cdc -details -file cdc_violation_report.rpt
```
หากพบข้อความแจ้งเตือน:
```text
Critical Warning: [CDC-6] Multi-bit bus 'frame_fsm_state[2:0]' is synchronized using individual 2-FF synchronizers. Bus skew may cause intermediate state corruption.
```
ต้องสั่งระงับการ Release แบบทันที!

#### ขั้นตอนที่ 2: เปลี่ยนสถาปัตยกรรมเป็น 4-Phase Handshake หรือ Pulse Synchronizer
* หากต้องการส่งสเตต: ให้ผู้ส่งตั้งค่าสเตตค้างไว้ แล้วส่งสัญญาณพัลส์ควบคุม `state_valid` ผ่าน Single-bit Synchronizer ไปสั่งให้ฝั่งรับแลตช์ค่า
* หากต้องการส่งสตรีมข้อมูล: ให้ใช้ **Asynchronous FIFO IP Core** ของผู้ผลิตชิป

#### ขั้นตอนที่ 3: กำหนด Timing Constraints สำหรับ MCP Bus
หากใช้วิธี Multi-Cycle Path ให้ใส่ข้อกำหนดเวลาใน XDC เพื่อควบคุม Skew:
```tcl
set_max_delay -from [get_cells u_isp/fsm_state_reg*] \
              -to [get_cells u_dma/fsm_state_capture_reg*] \
              -datapath_only 3.750
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| クロックドメイン交差 | くろっくどめいんこうさ | Kurokku Domein Kousa | Clock Domain Crossing (CDC) |
| 非同期ハンドシェイク | ひどうきはんどしぇいく | Hidouki Handosheiku | Asynchronous Handshake |
| バススキュー | ばすすきゅー | Basu Skyuu | Bus Skew (ความหน่วงเหลื่อมกันของบัส) |
| 疑似中間状態 | ぎじちゅうかんじょうたい | Giji Chuukan Joutai | Chimeric / Intermediate False State |
| 単一ビット同期化 | たんいつびっとどうきか | Tan-itsu Bitto Doukika | Single-bit Synchronization |
| マルチサイクルパス | まるちさいくるぱす | Maruchisaikuru Pasu | Multi-Cycle Path (MCP) |
| 準静的信号 | じゅんせいてきしんごう | Jun-seiteki Shingou | Quasi-Static Signal |
| 再収束障害 | さいしゅうそくしょうがい | Saishuushoku Shougai | Re-convergence Defect |
| 転送完了応答 | てんそうかんりょうおうとう | Tensou Kanryou Outou | Transfer Acknowledge Response |
| 非同期FIFO | ひどうきふぁいふぉ | Hidouki Faifo | Asynchronous FIFO |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** การประชุมตรวจแบบระบบประมวลผลวิดีโอ 4K ทางการแพทย์ (Medical Imaging FPGA Review Room)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** โยชิดะ ซัง (Yoshida-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** ฮาชิโมโตะ คุง (Hashimoto-kun)

---

**吉田技師 (Yoshida):**  
「橋本君、この画像処理パイプラインから DMA コントローラへのステート通知論理だが、148.5MHz ドメインの `state[2:0]` バスがそのまま 266MHz ドメインの 2 段 FF 同期化回路に 1 ビットずつ並列に入力されているね。CDC レポートでルール違反 [CDC-6] が出ているが、バススキュー対策はどうなっているのかね？」  
*(Hashimoto-kun, kono gazou shori paipurain kara DMA kontoroora e no suteeto tsuuchi ronri dakedo, 148.5MHz domein no `state[2:0]` basu ga sonomama 266MHz domein no nidan FF doukika kairo ni ichi-bitto zutsu heiretsu ni nyuuryoku sarete iru ne. CDC repooto de ruuru ihan [CDC-6] ga dete iru ga, basu skyuu taisaku wa dou natte iru no kane?)*  
**ความหมาย:** คุณฮาชิโมโตะ ลอจิกแจ้งสถานะจากไปป์ไลน์ประมวลผลภาพไปยัง DMA Controller ตัวนี้ บัส `state[2:0]` จากโดเมน 148.5MHz ถูกต่อตรงเข้าวงจรซิงโครไนเซอร์ 2-FF ของโดเมน 266MHz แยกทีละบิตขนานกันเลยนะ ในรายงาน CDC มีข้อผิดพลาดกฎข้อ [CDC-6] ขึ้นมาด้วย ไม่ทราบว่ามีมาตรการป้องกัน Bus Skew ไว้อย่างไรบ้างครับ?

---

**橋本技師 (Hashimoto):**  
「はい、吉田さん。全ビットに対して漏れなく 2 段の同期化レジスタを配置しましたので、メタステーブル対策は万全であると考えておりました。ステートの更新頻度も 1 フレームに 1 回程度と非常に遅いため、ビット間の遅延差は問題にならないと判断しました。」  
*(Hai, Yoshida-san. Zen-bitto ni taishite morenaku nidan no doukika rejisuta wo haichi shimashita node, metasuteeburu taisaku wa banzen de aru to kangaete orimashita. Suteeto no koushin hindo mo ichi-fureemu ni ikkai teido to hijou ni osoi tame, bitto-kan no chien-sa wa mondai ni naranai to handan shimashita.)*  
**ความหมาย:** ครับคุณโยชิดะ ผมได้วางวงจรซิงโครไนเซอร์ 2 สเตจดักไว้ครบทุกบิตอย่างไม่มีตกหล่น จึงคิดว่าป้องกัน Metastable ได้สมบูรณ์แบบแล้วครับ อีกทั้งความถี่ในการอัปเดตสเตตก็ช้ามาก ประมาณ 1 ครั้งต่อ 1 เฟรมภาพเท่านั้น ผมจึงคิดว่าความต่างของเวลาเดินทางระหว่างบิตคงไม่ส่งผลกระทบอะไรครับ

---

**吉田技師 (Yoshida):**  
「まさに絵に描いたような CDC の初歩的ミスだ！更新頻度がどんなに低くても、遷移の瞬間（トランジション）は一瞬だ。ビット 0 とビット 1 の配線遅延にわずか数百ピコ秒のスキューが生じるだけで、受信側のクロックがその過渡期を叩けば、送信側が存在すらさせていない『偽の未定義状態（Chimeric State）』がサンプリングされる！実機で時々フレームが破棄される怪現象はこれが原因だ！**直ちに重大是正事項とする！** 複数ビットの生同期化を全廃し、4 フェーズハンドシェイク回路、またはトグル同期パルスを用いた準静的（Quasi-Static）データ確定構成に全面改修しなさい！」  
*(Masani e ni kaita you na CDC no shohoteki misu da! Koushin hindo ga donna ni hikukutemo, sen-i no shunkan (toranjishon) wa isshun da. Bitto 0 to bitto 1 no haisen chien ni wazuka suuhyaku pikobyou no skyuu ga shoujiru dake de, jushin-gawa no kurokku ga sono katoki wo tatakeba, soushin-gawa ga sonzai sura sasete inai "nise no miteigi joutai (Chimeric State)" ga sanpuringu sareru! Jikki de tokidoki fureemu ga haki sareru kai-genshou wa kore ga gen-in da! **Tadachini juudai zeisei jikou to suru!** Fukusuu bitto no nama-doukika wo zenpai shi, 4-feezu handosheiku kairo, matawa toguru douki parusu wo mochiita jun-seiteki (Quasi-Static) deeta kakutei kousei ni zenmen kaishuu shinasai!)*  
**ความหมาย:** นี่มันข้อผิดพลาดเรื่อง CDC เบื้องต้นแบบคลาสสิกเลยนะเนี่ย! ต่อให้ความถี่ในการอัปเดตจะต่ำแค่ไหน แต่วินาทีที่มันเกิด Transition มันคือเสี้ยวพริบตาเดียว ขอแค่สายไฟบิต 0 กับบิต 1 มี Skew เหลื่อมกันเพียงไม่กี่ร้อยพิโกวินาที แล้วสัญญาณนาฬิกาฝั่งรับสุ่มจังหวะลงตรงรอยต่อนั้น ฝั่งรับก็จะได้ 'สถานะผีที่ไม่มีอยู่จริง (Chimeric State)' ทันที! ที่เครื่องจริงมีอาการเฟรมภาพหลุดทิ้งแบบประหลาดๆ ก็เพราะเหตุนี้แหละ! **ผมขอสั่งเป็นข้อแก้ไขเร่งด่วนขั้นวิกฤต!** จงยกเลิกการเอาบัสหลายบิตมาซิงโครไนซ์ตรงๆ ทั้งหมด แล้วเปลี่ยนไปใช้ 4-Phase Handshake หรือสถาปัตยกรรม Quasi-Static ที่ใช้พัลส์ซิงโครไนซ์ล็อกข้อมูลเดี๋ยวนี้!

---

**橋本技師 (Hashimoto):**  
「ビット同期化を行ってもバススキューで中間状態が生まれてしまうことの恐ろしさを痛感いたしました…！直ちにハンドシェイクインターフェースを実装し、Vivado CDC レポートで違反が完全にゼロになったことを確認して再提出いたします！」  
*(Bitto doukika wo okonattemo basu skyuu de chuukan joutai ga umarete shimau koto no osoroshisa wo tsuukan itashimashita...! Tadachini handosheiku intaafeesu wo jissou shi, Vivado CDC repooto de ihan ga kanzen ni zero ni natta koto wo kakunin shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ผมตระหนักถึงความน่ากลัวของการเกิด Intermediate State จาก Bus Skew แม้จะใส่ซิงโครไนเซอร์แล้วครับ...! ผมจะรีบสร้าง Handshake Interface ทันที และตรวจสอบรายงาน Vivado CDC ให้ปลอดจากข้อผิดพลาด 100% แล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณ Latency รวมของ Four-Phase Handshake Protocol

ในระบบการสื่อสารข้ามโดเมนสัญญาณนาฬิกาด้วย Four-Phase Handshake ระหว่างสองโมดูล:
* **โมดูลฝั่งส่ง (Source Domain):** ทำงานที่ความถี่ $f_{src} = 100\text{ MHz}$ ($T_{src} = 10.0\text{ ns}$)
* **โมดูลฝั่งรับ (Destination Domain):** ทำงานที่ความถี่ $f_{dst} = 200\text{ MHz}$ ($T_{dst} = 5.0\text{ ns}$)
* วงจรซิงโครไนเซอร์ทั้งสองฝั่งใช้แบบ **2-Stage D-Flip-Flop** ซึ่งสร้างความล่าช้าในการข้ามโดเมนคงที่เท่ากับ $2$ รอบสัญญาณนาฬิกาของโดเมนผู้รับสัญญาณนั้นๆ เสมอ
* สถานะของแต่ละ FSM ใช้เวลาประมวลผลภายใน $1$ รอบสัญญาณนาฬิกาหลังจากสัญญาณซิงโครไนซ์มาถึง

จงคำนวณหาเวลาหน่วงรวมแบบเต็มวงรอบ (Total Round-Trip Transaction Time: $T_{total}$) ตั้งแต่วินาทีที่ `src_send_req` เริ่มทำงาน จนกระทั่งถึงจังหวะที่ `src_done_pulse` ถูกส่งออกมาเสร็จสิ้นอย่างสมบูรณ์ในหน่วย **นาโนวินาที (ns)**?

---

#### ตัวเลือก:
A) $T_{total} = 35.0\text{ ns}$  
B) $T_{total} = 50.0\text{ ns}$  
C) $T_{total} = 65.0\text{ ns}$  
D) $T_{total} = 80.0\text{ ns}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: C) $T_{total} = 65.0\text{ ns}$**

##### ขั้นตอนการวิเคราะห์จังหวะเวลาทั้ง 4 เฟส (Transaction Time Decomposition):

1. **เฟสที่ 1 (Src ยก Req $\rightarrow$ Dst รับรู้):**
   * Src FSM เริ่มต้นยก `req = 1`: ใช้เวลา $1$ รอบ $T_{src} = 10.0\text{ ns}$
   * สัญญาณ `req` เดินทางข้ามมายังโดเมน Dst และผ่าน 2-FF Synchronizer:
     $$T_{sync1} = 2 \times T_{dst} = 2 \times 5.0\text{ ns} = 10.0\text{ ns}$$
   * Dst FSM ประมวลผลและยก `ack = 1`: ใช้เวลา $1$ รอบ $T_{dst} = 5.0\text{ ns}$
   * รวมเวลาเฟสที่ 1: $10.0 + 10.0 + 5.0 = 25.0\text{ ns}$

2. **เฟสที่ 2 (Dst ยก Ack $\rightarrow$ Src รับรู้):**
   * สัญญาณ `ack` เดินทางข้ามมายังโดเมน Src และผ่าน 2-FF Synchronizer:
     $$T_{sync2} = 2 \times T_{src} = 2 \times 10.0\text{ ns} = 20.0\text{ ns}$$
   * Src FSM ประมวลผลและปลด `req = 0`: ใช้เวลา $1$ รอบ $T_{src} = 10.0\text{ ns}$
   * รวมเวลาเฟสที่ 2: $20.0 + 10.0 = 30.0\text{ ns}$

3. **เฟสที่ 3 (Src ปลด Req $\rightarrow$ Dst รับรู้):**
   * สัญญาณ `req = 0` เดินทางข้ามมายัง Dst ผ่าน 2-FF Synchronizer:
     $$T_{sync3} = 2 \times T_{dst} = 2 \times 5.0\text{ ns} = 10.0\text{ ns}$$
   * Dst FSM ประมวลผลและปลด `ack = 0`: ใช้เวลา $1$ รอบ $T_{dst} = 5.0\text{ ns}$
   * *(หมายเหตุ: จังหวะนี้เกิดขึ้นซ้อนทับหรือต่อช่วง)*

4. **เฟสที่ 4 (Dst ปลด Ack $\rightarrow$ Src รับรู้เพื่อจบงาน):**
   * สัญญาณ `ack = 0` ข้ามกลับมายัง Src ผ่าน 2-FF Synchronizer:
     $$T_{sync4} = 2 \times T_{src} = 20.0\text{ ns}$$

*เมื่อพิจารณาในรูปแบบวงรอบพื้นฐานต่ำสุด (Ideal Boundary Cycle Breakdown):*
$$T_{total} = (1 \cdot T_{src} + 2 \cdot T_{dst} + 1 \cdot T_{dst}) + (2 \cdot T_{src} + 1 \cdot T_{src}) = 10 + 10 + 5 + 20 + 10 + 10 = 65.0\text{ ns}$$
ดังนั้น การส่งข้อมูล 1 ชุดผ่าน 4-Phase Handshake ในระบบนี้ต้องใช้เวลารวมอย่างน้อย **$65.0\text{ ns}$** ซึ่งแสดงให้เห็นว่า แม้ 4-Phase Handshake จะปลอดภัยสูงสุด แต่มี Latency ค่อนข้างสูง จึงเหมาะสำหรับการส่งสัญญาณคำสั่งหรือสถานะ ไม่เหมาะกับสตรีมข้อมูลความเร็วสูง

---

### คำถามที่ 2: การคำนวณงบประมาณความหน่วงของคำสั่ง `-datapath_only` ใน Quasi-Static MCP

ในการเชื่อมต่อบัสข้อมูลขนาด 16 บิตข้ามโดเมนไปยังโมดูลรับที่ทำงานที่ความถี่ $f_{dst} = 250\text{ MHz}$ ($T_{dst} = 4.000\text{ ns}$):
* เพื่อป้องกันไม่ให้ข้อมูลในรอบใหม่วิ่งแซงข้อมูลรอบเก่า (Data Race / Data Overtaking)
* วิศวกรกำหนดให้สัญญาณ Enable ที่ผ่านซิงโครไนเซอร์มีเวลาหน่วงในการตรวจจับ $2 \times T_{dst} = 8.000\text{ ns}$
* กำหนดค่าความไม่แน่นอนของสัญญาณนาฬิกา (Clock Uncertainty): $T_{unc} = 0.200\text{ ns}$
* Setup Time ของรีจิสเตอร์ปลายทาง: $t_{su} = 0.100\text{ ns}$

จงระบุค่าขีดจำกัดความหน่วงสูงสุดของสายสัญญาณ (`set_max_delay -datapath_only`) ที่ต้องระบุในไฟล์ XDC เพื่อให้มั่นใจว่าข้อมูลทั้ง 16 บิตจะเดินทางไปถึงและเข้าสู่สภาวะคงตัวก่อนที่สัญญาณ Enable จะถูกทริกเกอร์?

---

#### ตัวเลือก:
A) $8.000\text{ ns}$  
B) $7.700\text{ ns}$  
C) $4.000\text{ ns}$  
D) $3.700\text{ ns}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: D) $3.700\text{ ns}$**

##### การวิเคราะห์ทางวิศวกรรม STA:
ในกฎมาตรฐานของ Xilinx Vivado สำหรับคำสั่ง `set_max_delay -datapath_only`:
คำสั่งนี้จะตัดการตรวจสอบ Clock Skew ระหว่างสองโดเมนออกไป และบังคับให้ผลรวมของความหน่วงลอจิกบวกความหน่วงสายส่ง (Data Path Delay: $t_{logic} + t_{net}$) มีค่าไม่เกินตัวเลขที่ระบุ

เพื่อให้บัสข้อมูล 16 บิตมีความปลอดภัยอย่างสมบูรณ์เมื่อเทียบกับสัญญาณควบคุม Enable ที่ใช้เวลาเดินทาง 1 คาบเวลาหลักของฝั่งรับ ($T_{dst} = 4.000\text{ ns}$):
ความหน่วงสูงสุดที่ยอมรับได้คำนวณจาก:
$$\text{Max Delay Limit} = T_{dst} - t_{su} - T_{unc}$$
แทนค่า:
$$\text{Max Delay Limit} = 4.000\text{ ns} - 0.100\text{ ns} - 0.200\text{ ns} = 3.700\text{ ns}$$

คำสั่ง XDC ที่ถูกต้องจึงเป็น:
```tcl
set_max_delay -from [get_cells u_src/data_reg*] -to [get_cells u_dst/data_capture_reg*] -datapath_only 3.700
```
ค่า $3.700\text{ ns}$ จะบีบให้เครื่องมือ Place & Route วางตำแหน่งเซลล์และเดินสายข้อมูลทุกเส้นให้สั้นพอที่จะไม่ให้เกิด Bus Skew เกินหน้าต่างเวลา 1 ไซเคิล

---

### คำถามที่ 3: ทำไมตัวชี้ของ Asynchronous FIFO จึงต้องแปลงเป็น Gray Code ก่อนข้ามโดเมน?

เหตุใดในสถาปัตยกรรม Asynchronous FIFO ตัวชี้แอดเดรสการเขียน (Write Pointer) และการอ่าน (Read Pointer) จึงต้องถูกแปลงจาก Binary ไปเป็น Gray Code ก่อนป้อนเข้าสู่ 2-FF Synchronizer?

---

#### ตัวเลือก:
A) เพื่อให้ตัวชี้มีขนาดบิตที่เล็กลงครึ่งหนึ่ง  
B) เพื่อให้ในแต่ละการเพิ่มค่า (Increment) มีบิตเปลี่ยนค่าเพียง 1 บิตอย่างเคร่งครัด ทำให้หากเกิดสภาวะ Metastable ค่าที่อ่านได้จะคลาดเคลื่อนได้อย่างมากที่สุดเพียง 1 ตำแหน่งเท่านั้น และไม่มีวันเกิดค่าแอดเดรสกระโดดข้ามไปไกลจนทำให้ FIFO ล้นหรือว่างเท็จ  
C) เพื่อลดการใช้พลังงานของ Block RAM  
D) เพื่อให้สามารถใช้วงจรบวก Adder ธรรมดาในการคำนวณผลต่างได้

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เพื่อให้ในแต่ละการเพิ่มค่า (Increment) มีบิตเปลี่ยนค่าเพียง 1 บิตอย่างเคร่งครัด ทำให้หากเกิดสภาวะ Metastable ค่าที่อ่านได้จะคลาดเคลื่อนได้อย่างมากที่สุดเพียง 1 ตำแหน่งเท่านั้น และไม่มีวันเกิดค่าแอดเดรสกระโดดข้ามไปไกลจนทำให้ FIFO ล้นหรือว่างเท็จ**

##### คำอธิบายเชิงคณิตศาสตร์:
หากใช้ Binary Pointer เช่น ตัวชี้นับจาก $7 (0111_2) \rightarrow 8 (1000_2)$:
มีบิตเปลี่ยนค่าพร้อมกันถึง 4 บิต หากเกิด Bus Skew ตัวรับอาจสุ่มอ่านได้ค่าใดๆ ตั้งแต่ $0$ ถึง $15$ ซึ่งอาจเป็นค่าแอดเดรสที่กระโดดข้ามไปข้างหน้า ส่งผลให้วงจรตรวจสอบ Empty/Full Flag ตัดสินใจผิดพลาด ทำให้อ่านข้อมูลขยะหรือเขียนทับข้อมูลจริง

เมื่อแปลงเป็น **Gray Code**:
ระยะห่างแฮมมิงระหว่างแอดเดรสที่ติดกันจะมีค่า $d_H = 1$ บิตเสมอ!
หากขอบสัญญาณนาฬิกาปลายทางสุ่มตรงจังหวะบิตนั้นกำลังเปลี่ยนพอดี:
* ผลลัพธ์ที่เป็นไปได้มีเพียง 2 กรณีเท่านั้น คือ: อ่านได้ **ค่าแอดเดรสเดิม** หรืออ่านได้ **ค่าแอดเดรสใหม่**
* ระบบจะไม่มีวันอ่านได้ค่าประหลาดอื่นใดเด็ดขาด!
* ซึ่งในทางวิศวกรรม FIFO: การอ่านได้ค่าเดิมจะทำให้ FIFO มองว่าข้อมูลยังมาไม่ถึง (ปลอดภัยแบบอนุรักษนิยม: Conservative Safe) จึงไม่มีทางเกิดเหตุการณ์ Buffer Overflow หรือ Underflow อย่างเด็ดขาด
