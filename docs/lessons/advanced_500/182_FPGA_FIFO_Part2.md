# Lesson 182: FPGA FIFO Part 2 - Programmable Flags & Flow Control Physics (Almost Full/Empty Thresholds, High/Low Watermarks, Backpressure Margins & Skid Buffer Flow Control)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์ความล่าช้าของระบบควบคุมการไหล (Backpressure Latency Breakdown)
ในระบบส่งผ่านข้อมูลความเร็วสูงระดับกิกะบิตต่อวินาที เช่น เครือข่ายอีเทอร์เน็ต 100GbE, อินเทอร์เฟซ PCIe Gen4/Gen5, หรือระบบเชื่อมต่อหน่วยความจำ AXI4 Interconnect: ความเข้าใจผิดที่ร้ายแรงที่สุดของวิศวกรคือการคิดว่า **"สัญญาณ `full` ปกติของ FIFO สามารถนำมาใช้ส่งสัญญาณ Backpressure เพื่อหยุดโมดูลส่งข้อมูลได้โดยตรง"**

```
             ภาพลวงตาอันตราย: การใช้ FULL FLAG ควบคุม BACKPRESSURE
             
    [ TRANSMITTER PIPELINE ]                         [ RECEIVER FIFO ]
    
    Data Source ──► [Pipe 1] ──► [Pipe 2] ──► [Pipe 3] ══════► [ FIFO CORE ]
                         ▲                                          │
                         │                                          ▼
                         └───[Pipe R2] ◄─── [Pipe R1] ◄──── full (ยกขึ้นเมื่อเต็ม!)
                         
    วิกฤตความล่าช้า:
    1. FIFO เต็มพิกัด จึงยกสัญญาณ `full = 1`
    2. สัญญาณ `full` ต้องเดินทางย้อนกลับผ่าน Pipeline Registers เป็นเวลา 3 ไซเคิล
    3. ข้อมูลที่ค้างอยู่ในท่อ [Pipe 1], [Pipe 2], [Pipe 3] อีก 3 คำ ยังคงไหลเข้าสู่ FIFO ต่อไป!
    ===> ผลลัพธ์: เกิด BUFFER OVERFLOW ทันที! ข้อมูลสูญหายและระบบเกิด FATAL CRASH!
```

#### นิยามฟิสิกส์ของ Round-Trip Backpressure Latency ($T_{RTB}$):
ระยะเวลารวมตั้งแต่เสี้ยววินาทีที่ FIFO ตัดสินใจสั่งหยุดรับข้อมูล จนกระทั่งข้อมูลคำสุดท้ายที่ตกค้างในระบบเดินทางมาถึงและหยุดลงหน้าประตู FIFO เรียกว่า **Total Backpressure Skid Latency**:

$$N_{skid\_total} = N_{pipe,fwd} + N_{pipe,rev} + N_{tx\_reaction} + N_{wire}$$

* $N_{pipe,fwd}$: จำนวนรอบ Pipeline Register บนเส้นทางเดินข้อมูล (Datapath) จากฝั่งส่งถึงฝั่งรับ
* $N_{pipe,rev}$: จำนวนรอบ Pipeline Register บนเส้นทางส่งสัญญาณตอบรับ (Control Backpressure Path เช่น `ready` หรือ `pause`)
* $N_{tx\_reaction}$: จำนวนรอบสัญญาณนาฬิกาที่ฝั่งส่งต้องใช้ในการหยุดการสร้างข้อมูลใหม่
* $N_{wire}$: ความหน่วงเวลาของสายส่ง Interconnect ข้ามชิปหรือข้าม SLR

หากความจุของ FIFO คือ $Depth = 1024$ และค่า $N_{skid\_total} = 6\text{ ไซเคิล}$:
หากเราใช้สัญญาณ `full` ปกติ (ซึ่งยกเมื่อมีข้อมูลครบ 1024 คำ) ข้อมูลที่ค้างท่ออีก 6 คำจะถูกยิงกระแทกเข้าใส่ FIFO ที่เต็มแล้ว เกิด **Write Overflow อย่างหลีกเลี่ยงไม่ได้ $100\%$!**

---

### 1.2 สถาปัตยกรรม Programmable Almost Full (Prog_Full) และ High Watermark

เพื่อดูดซับข้อมูลที่ตกค้างอยู่ในท่อ (In-Flight Data) สถาปัตยกรรมระดับ Senior Engineer จึงต้องนำ **Programmable Almost Full Flag (High Watermark - 高水準点)** มาใช้งาน โดยสัญญาณนี้จะยกเตือนภัยล่วงหน้าก่อนที่ FIFO จะเต็มจริง:

```
               สถาปัตยกรรม HIGH WATERMARK & IN-FLIGHT SKID MARGIN
               
    FIFO DEPTH (เช่น 1024) ┌───────────────────────────────┐
                           │   IN-FLIGHT SKID MARGIN       │ <── สำรองไว้สำหรับ
                           │  (พื้นที่ดูดซับข้อมูลค้างท่อ)   │     ข้อมูลที่ยังหยุดไม่ทัน!
    HIGH WATERMARK (1016) ├───────────────────────────────┤ <── สั่งตัด Backpressure ตรงนี้!
                           │                               │
                           │   NORMAL USABLE BUFFER        │
                           │  (พื้นที่ใช้งานปกติ)           │
                           │                               │
    EMPTY (0)              └───────────────────────────────┘
```

#### สูตรการคำนวณขีดจำกัด High Watermark Threshold ($H_{wm}$):
$$H_{wm} = \text{Depth} - \text{Margin}_{skid}$$

โดยที่ข้อกำหนดด้านความปลอดภัยขั้นต่ำ (Safety Margin Bound) คือ:
$$\text{Margin}_{skid} \ge N_{skid\_total} + N_{safety\_guard}$$

> [!IMPORTANT]
> สำหรับระบบความเร็วสูงระดับ UltraScale+ ที่ทำงานที่ความถี่ $300\text{ MHz} \sim 500\text{ MHz}$ ค่าความปลอดภัย $N_{safety\_guard}$ ควรกำหนดไว้อย่างน้อย **$2\text{ ไซเคิล}$** เพื่อรองรับความผันผวนของ Clock Skew และจังหวะรอยต่อของสเตตแมชชีน!

---

### 1.3 ปัญหา Chattering Oscillation และสถาปัตยกรรม Dual-Threshold Hysteresis

หากระบบใช้เงื่อนไขตรวจสอบระดับน้ำแบบจุดเดียว (Single Threshold):
* เมื่อข้อมูลแตะค่า $1016$: สัญญาณ `almost_full` ยกขึ้น $\to$ ฝั่งส่งหยุดส่ง
* ในไซเคิลถัดไป ฝั่งรับอ่านข้อมูลออกไป 1 คำ ข้อมูลลดลงเหลือ $1015$: สัญญาณ `almost_full` ดับลง $\to$ ฝั่งส่งเริ่มส่งใหม่
* วงจรจะเกิดอาการ **กระพริบเปิด-ปิดสลับกันทุกไซเคิล (Chattering / Ping-Pong Oscillation)**:

```
                 ปรากฏการณ์ CHATTERING จากการใช้ SINGLE THRESHOLD
                 
    almost_full : ──/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_ (กระพริบไม่หยุด!)
    Throughput  : ดิ่งลงเหลือเพียง 50% หรือต่ำกว่า เพราะ Pipeline เริ่มๆ หยุดๆ ตลอดเวลา!
```

#### วิธีแก้ไข: สถาปัตยกรรม Hysteresis (Dual-Watermark Architecture):
ในระบบมืออาชีพ จะมีการกำหนดจุดตัด 2 ระดับแยกจากกัน:
1. **Assert Threshold ($T_{assert}$ / High Watermark):** ขีดจำกัดระดับสูงที่สัญญาณ `prog_full` จะ **ยกขึ้นทำงาน** (สั่งให้ฝั่งส่งหยุดส่ง)
2. **Negate/Deassert Threshold ($T_{negate}$ / Low Watermark):** ขีดจำกัดระดับต่ำที่สัญญาณ `prog_full` จะ **ดับลง** (ยอมให้ฝั่งส่งเริ่มส่งใหม่)

```
                     กลไก HYSTERESIS สองระดับ (DUAL-WATERMARK)
                     
    FIFO Count
        ▲
        │
    T_assert (1016) ├───────────────────────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
        │                                  /                   \
        │                                 /                     \
    T_negate (960)  ├──────/‾‾‾‾‾‾‾‾‾‾‾‾‾/                       \_______
        │             /                                                 ▲
        └────────────/───────────────────────────────────────────────────┴──► Time
        
    prog_full       : ___________________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\_________
                                         ▲ ยกขึ้นเมื่อถึง 1016    ▲ ดับลงเมื่อลดถึง 960!
                                         ├────────────────────────┤
                                            Hysteresis Band (56 คำ)
```

**ประโยชน์มหาศาลของ Hysteresis:**
* เมื่อฝั่งส่งหยุดส่ง ระบบจะปล่อยให้ฝั่งรับอ่านข้อมูลออกไปจนกระทั่ง FIFO มีพื้นที่ว่างขนาดใหญ่ก้อนหนึ่ง (เช่น ว่าง 56 คำ)
* เมื่อ `prog_full` ปลดลง ฝั่งส่งจะสามารถยิงข้อมูลแบบ **Full-Speed Continuous Burst** ก้อนใหญ่เข้ามาได้อย่างต่อเนื่องเต็มท่อ โดยไม่มีการสะดุดหรือเกิด Chattering แม้แต่ครั้งเดียว!

---

### 1.4 Programmable Almost Empty และการเร่งประสิทธิภาพ Burst DMA

ในฝั่งการอ่าน (Read Domain) ปัญหาที่พบบ่อยคือการที่วงจร DMA Controller เริ่มต้นยิงคำสั่งอ่านข้อมูลแบบ Burst (เช่น AXI4 Burst Length = 16 คำ) ทว่า FIFO มีข้อมูลสะสมอยู่เพียง 4 คำ:
* ผลลัพธ์: หลังจากอ่านไปได้ 4 คำ FIFO จะเกิดสภาวะ **Read Stall / Underflow**
* บัส AXI เกิดสภาวะฟองอากาศ (Bus Bubbles / Idle Cycles) แย่งชิงแบนด์วิดท์ของระบบ

#### ประโยชน์ของ Programmable Almost Empty (Low Watermark):
การตั้งค่า `prog_empty` ให้ยกเตือนว่า *"ข้อมูลยังมีไม่พอ ($Count < Burst\_Size$)"* และจะปลดลงก็ต่อเมื่อ **มีข้อมูลสะสมเกินขนาด Burst เสมอ ($Count \ge Burst\_Size$)**:
$$\text{Threshold}_{prog\_empty} = \text{Burst\_Size}$$
ทำให้ DMA Controller มั่นใจได้ $100\%$ ว่าเมื่อเริ่มยิง Burst Read ข้อมูลจะไหลต่อเนื่องจนจบรอบ Burst โดยไม่มีการหยุดชะงักกลางคัน!

---

### 1.5 โค้ดแม่แบบภาษา Verilog ระดับ Senior สำหรับ FIFO ที่มี Programmable Hysteresis Flags

```verilog
// ==============================================================================
// ADVANCED SYNCHRONOUS FIFO WITH DUAL-WATERMARK HYSTERESIS FLOW CONTROL
// Senior Gold Standard: Chattering-Free Programmable Flags & Skid Margins
// ==============================================================================
(* keep_hierarchy = "yes" *)
module sync_fifo_programmable_flags #(
    parameter integer DATA_WIDTH     = 64,
    parameter integer ADDR_WIDTH     = 10,   // Depth = 1024 words
    parameter integer PROG_FULL_SET  = 1016, // Assert Threshold (High Watermark)
    parameter integer PROG_FULL_RST  = 960,  // Negate Threshold
    parameter integer PROG_EMPTY_SET = 16,   // Negate Threshold (Low Watermark for DMA Burst)
    parameter integer PROG_EMPTY_RST = 32    // Assert Threshold
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // Write Port
    input  wire                  wr_en,
    input  wire [DATA_WIDTH-1:0] din,
    output wire                  full,
    output reg                   prog_full,

    // Read Port
    input  wire                  rd_en,
    output wire [DATA_WIDTH-1:0] dout,
    output wire                  empty,
    output reg                   prog_empty,

    // Occupancy
    output reg  [ADDR_WIDTH:0]   count
);

    localparam integer DEPTH = 1 << ADDR_WIDTH;

    // -------------------------------------------------------------------------
    // 1. Dual-Port Memory Core
    // -------------------------------------------------------------------------
    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];
    reg [ADDR_WIDTH-1:0] wptr;
    reg [ADDR_WIDTH-1:0] rptr;

    wire write_valid = wr_en && (count < DEPTH);
    wire read_valid  = rd_en && (count > 0);

    always @(posedge clk) begin
        if (write_valid)
            mem[wptr] <= din;
    end

    // Direct Synchronous Output
    reg [DATA_WIDTH-1:0] dout_reg;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            dout_reg <= {DATA_WIDTH{1'b0}};
        else if (read_valid)
            dout_reg <= mem[rptr];
    end
    assign dout = dout_reg;

    // -------------------------------------------------------------------------
    // 2. Pointers and Occupancy Calculation
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wptr  <= {ADDR_WIDTH{1'b0}};
            rptr  <= {ADDR_WIDTH{1'b0}};
            count <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            case ({write_valid, read_valid})
                2'b10: begin
                    wptr  <= wptr + 1'b1;
                    count <= count + 1'b1;
                end
                2'b01: begin
                    rptr  <= rptr + 1'b1;
                    count <= count - 1'b1;
                end
                2'b11: begin
                    wptr  <= wptr + 1'b1;
                    rptr  <= rptr + 1'b1;
                    count <= count;
                end
                default: ;
            endcase
        end
    end

    assign full  = (count == DEPTH);
    assign empty = (count == 0);

    // -------------------------------------------------------------------------
    // 3. Hysteresis Programmable Flags Logic (Glitch-Free Registered Outputs)
    // -------------------------------------------------------------------------
    // Next-state count prediction for immediate cycle response
    wire [ADDR_WIDTH:0] count_next = count + write_valid - read_valid;

    // Programmable Full Hysteresis
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prog_full <= 1'b0;
        end else begin
            if (prog_full) begin
                // Deassert only when occupancy drops below reset threshold
                if (count_next <= PROG_FULL_RST)
                    prog_full <= 1'b0;
            end else begin
                // Assert when occupancy reaches or exceeds set threshold
                if (count_next >= PROG_FULL_SET)
                    prog_full <= 1'b1;
            end
        end
    end

    // Programmable Empty Hysteresis
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prog_empty <= 1'b1; // Initially empty
        end else begin
            if (prog_empty) begin
                // Deassert (data ready for burst) when occupancy reaches reset threshold
                if (count_next >= PROG_EMPTY_RST)
                    prog_empty <= 1'b0;
            end else begin
                // Assert when occupancy drops below set threshold
                if (count_next <= PROG_EMPTY_SET)
                    prog_empty <= 1'b1;
            end
        end
    end

endmodule
```

---

### 1.6 SystemVerilog Assertions (SVA) เพื่อตรวจจับการละเมิด Skid Margin

```systemverilog
// SVA Verification Suite สำหรับการตรวจสอบ Skid Margin และ In-Flight Backpressure
module prog_fifo_sva #(
    parameter integer DEPTH = 1024,
    parameter integer PROG_FULL_SET = 1016
)(
    input wire clk,
    input wire rst_n,
    input wire wr_en,
    input wire full,
    input wire prog_full,
    input wire [10:0] count
);

    // Property 1: Hard Full must NEVER be reached during normal backpressure operation!
    // If prog_full asserts, transmitter must react and count must never hit DEPTH.
    property p_skid_margin_safe;
        @(posedge clk) disable iff (!rst_n)
        prog_full |-> (count < DEPTH);
    endproperty
    assert_skid_safe: assert property (p_skid_margin_safe)
        else $error("[OVERFLOW_RISK]: FIFO hit HARD FULL! Skid margin was insufficient!");

    // Property 2: No write attempts while hard full
    property p_no_write_overflow;
        @(posedge clk) disable iff (!rst_n)
        full |-> !wr_en;
    endproperty
    assert_overflow: assert property (p_no_write_overflow)
        else $error("[FATAL_DATA_LOSS]: wr_en asserted while FIFO count was at DEPTH!");

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】การ์ดเร่งความเร็วเครือข่าย 100GbE SmartNIC ในศูนย์ข้อมูลคลาวด์
เกิดอาการ Packet Drop และทราฟฟิก TCP สะดุดขั้นรุนแรงในสภาวะ Congestion Burst
จากการคำนวณ Skid Margin ของ Programmable Full ต่ำกว่าความเป็นจริง 4 ไซเคิล
================================================================================
```

#### บริบทของระบบ (System Context):
บริษัทพัฒนาอุปกรณ์เครือข่าย Data Center พัฒนาการ์ด 100GbE SmartNIC บนชิป FPGA AMD Xilinx Virtex UltraScale+ (`xcvu9p`):
* บัสข้อมูลภายใน: 512-bit AXI4-Stream ทำงานที่ความถี่ $322.265625\text{ MHz}$
* มีแพ็กเก็ตบัฟเฟอร์ FIFO ขนาดความลึก $Depth = 512\text{ คำ}$ คั่นระหว่าง Ethernet MAC และตัวประมวลผล Packet Parser
* สายสัญญาณควบคุม `TREADY` วิ่งผ่าน AXI Register Slice (Pipeline Stage) จำนวน 2 สเตจบน Datapath และ 2 สเตจบน Ready Path เพื่อทำ Timing Closure ให้ผ่าน $322\text{ MHz}$
* วิศวกรตั้งค่า Almost Full Threshold ไว้ที่:
  $$\text{PROG\_FULL\_THRESHOLD} = 512 - 2 = 510\text{ คำ}$$
  โดยเข้าใจว่าต้องการเผื่อพื้นที่ไว้เพียง 2 คำสำหรับคำสั่งหยุดส่ง

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
เมื่อทำการทดสอบในห้องปฏิบัติการที่มีทราฟฟิกระดับต่ำ ระบบทำงานได้ราบรื่นสมบูรณ์แบบ ทว่า เมื่อนำไปติดตั้งในเซิร์ฟเวอร์คลาวด์จริงและเกิดสภาวะ **Micro-burst Traffic (มีข้อมูลแพ็กเก็ตขนาดใหญ่พุ่งเข้ามาเต็มความเร็ว 100Gbps พร้อมกัน)**: สถิติการ์ดเครือข่ายเริ่มฟ้องอาการ **Ethernet Frame Checksum Error และ Packet Loss** อย่างมหาศาล ทราฟฟิก TCP มี Throughput ดิ่งลงจาก 100Gbps เหลือไม่ถึง 10Gbps เนื่องจากเกิด TCP Retransmission พายุใหญ่ เซิร์ฟเวอร์สูญเสียการตอบสนองต่อฐานข้อมูล!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมเครือข่ายจึงเกิด Packet Loss และ TCP Throughput ดิ่งลง?**
   * *เพราะเฟรมข้อมูลอีเทอร์เน็ตที่กักเก็บใน FIFO สูญหายไปบางส่วน ทำให้แพ็กเก็ตปลายทางเกิด FCS CRC Error และถูกทิ้ง*
2. **ทำไมข้อมูลใน FIFO จึงสูญหาย?**
   * *เพราะ FIFO เกิดสภาวะ Write Overflow (ข้อมูลส่วนเกินถูกเขียนทับลงในช่องที่เต็มแล้ว)*
3. **ทำไมจึงเกิด Write Overflow ทั้งที่มีการใช้ Programmable Almost Full?**
   * *เพราะเมื่อสัญญาณ `prog_full` ยกขึ้นเตือนภัย ข้อมูลจาก MAC ยังคงไหลทะลักเข้ามาต่ออีกถึง 6 คำ เกินกว่ามาร์จิน 2 คำที่วิศวกรสำรองไว้*
4. **ทำไมจึงมีข้อมูลทะลักเข้ามาอีกถึง 6 คำหลังจาก Almost Full ทำงาน?**
   * *เพราะมี Pipeline Register บนสาย `TREADY` 2 ไซเคิล, Pipeline บน `TDATA` 2 ไซเคิล, วงจร FSM ภายใน MAC ใช้เวลาตอบสนองอีก 1 ไซเคิล, และ Skid Buffer ภายใน Register Slice อีก 1 คำ รวมเป็นความล่าช้าขั้นต่ำ $6\text{ ไซเคิล}$!*
5. **ทำไมวิศวกรจึงคำนวณมาร์จินไว้เพียง 2 คำ?**
   * *เพราะวิศวกรคิดเฉพาะความล่าช้าของฟลิปฟล็อปที่หน้าพอร์ต FIFO เท่านั้น โดยไม่ได้คำนวณผลรวมความหน่วงเวลาของทั้งเส้นทาง (End-to-End Skid Latency Budget) บน AXI Register Slices!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                         สาเหตุของความล้มเหลว: 100GBE PACKET SPILL OVERFLOW
                         
   METHOD (การคำนวณ Skid Budget)               MACHINE (ฮาร์ดแวร์และการเดินสายชิป)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ตั้ง Margin ไว้เพียง 2 คำ     │          │ AXI Register Slice 4 สเตจ      │
   │ ละเลย Pipeline Latency รวม     │          │ ทำงานที่ความถี่สูง 322.26MHz   │
   │ ขาดการคำนวณ Round-Trip Skid    │          │ In-Flight Data ค้างท่อ 6 คำ    │
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ขาด SVA ตรวจจับ Overflow Risk  │          │ Testbench ไม่เคยยิง Micro-burst│
   │ ละเลยคู่มือ Xilinx PG085       │          │ ไม่ได้จับตาดู Overflow Counter │
   │ ตรวจแบบ Kenzu ขาดความลึกซึ้ง   │          │ ปล่อยผ่านเพราะเห็นว่า Timing ผ่าน│
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (ข้อกำหนดและการตรวจสอบ)             MEASUREMENT (สภาวะการทดสอบระบบ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediations):
1. **คำนวณค่า Skid Latency Budget ใหม่ทั้งหมด:**
   $$N_{skid} = 2 (\text{Data Pipe}) + 2 (\text{Ready Pipe}) + 1 (\text{MAC FSM}) + 1 (\text{Skid Reg}) + 2 (\text{Safety Guard}) = 8\text{ ไซเคิล}$$
2. **ปรับแต่ง Threshold ของ Programmable Almost Full:**
   $$\text{PROG\_FULL\_SET} = 512 - 8 = 504\text{ คำ}$$
   และตั้งค่า Deassert Threshold สำหรับ Hysteresis:
   $$\text{PROG\_FULL\_RST} = 504 - 32 = 472\text{ คำ}$$
3. **ติดตั้งวงจร SVA Assertion:** บังคับให้ Simulator ฟ้องข้อผิดพลาดทันทีหากตัวนับ `count` ใน FIFO พุ่งขึ้นเกิน 510 คำ

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Flow Control Flags (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | มีการคำนวณผลรวม Pipeline Latency ตลอดเส้นทาง (Round-Trip Skid) หรือไม่? | Complete Skid Budget Sheet | [ ] ผ่าน |
| 2 | ค่า Skid Margin ได้รวมค่า Safety Guard ไว้อย่างน้อย $+2\text{ ไซเคิล}$ หรือไม่? | Guard Band Added | [ ] ผ่าน |
| 3 | มีการใช้สถาปัตยกรรม Dual-Threshold Hysteresis เพื่อป้องกัน Chattering หรือไม่? | Hysteresis Implemented | [ ] ผ่าน |
| 4 | ขนาดความลึก FIFO หลังหัก Margin ยังเพียงพอรองรับขนาด Max Burst หรือไม่? | Usable Depth $\ge$ Max Burst | [ ] ผ่าน |
| 5 | มีการเขียน SVA ยืนยันว่าไม่มีวันชน Hard Full แม้ในสภาวะ Burst โหดสุด? | Formal Property Passed | [ ] ผ่าน |
| 6 | ทำการทดสอบ Stress Test ด้วยทราฟฟิก Micro-burst ใน Testbench หรือไม่? | Pass 100GbE Line-rate Burst | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | プログラマブル・フラグ | プログラマブル・フラグ | Puroguramaburu furagu | Programmable Flags (Almost Full/Empty) |
| 2 | 高水準点 / 低水準点 | こうすいじゅんてん / ていすいじゅんてん | Kōsuijunten / Teisuijunten | High Watermark / Low Watermark |
| 3 | スキッド余裕度 | スキッドよゆうど | Sukiddo yoyūdo | Skid Margin / Backpressure Allowance |
| 4 | パイプライン段数遅延 | パイプラインだんすうちえん | Paipurain dansū chien | Pipeline Stage Latency |
| 5 | チャタリング振動 | チャタリングしんどう | Chataringu shindō | Chattering / Ping-Pong Oscillation |
| 6 | ヒステリシス制御 | ヒステリシスせいぎょ | Hisuterishisu seigyo | Hysteresis Control (Dual Threshold) |
| 7 | バッファ溢れ | バッファあふれ | Baffa afure | Buffer Overflow / Buffer Spill |
| 8 | 飛行中データ | ひこうちゅうデータ | Hikō-chū dēta | In-Flight Data (ข้อมูลตกค้างในท่อ) |
| 9 | バースト途切れ防止 | バーストとぎれぼうし | Bāsuto togire bōshi | Burst Disruption Prevention |
| 10 | 流量制御 | りゅうりょうせいぎょ | Ryūryō seigyo | Flow Control / Traffic Throttling |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ศูนย์วิจัยและพัฒนาอุปกรณ์สื่อสารความเร็วสูง (High-Speed Networking R&D Center), เมืองฟุกุโอกะ (Fukuoka)  
**ผู้เข้าร่วม:**
* **โคบายาชิซัง (Kobayashi-san):** ผู้จัดการฝ่ายตรวจแบบสถาปัตยกรรมเครือข่าย (Network Architecture Review Manager / 技師長)
* **ชานนท์ (Chanon):** วิศวกรออกแบบระบบ 100GbE SmartNIC (High-Speed FPGA Designer)

---

**小林技師長 (Kobayashi):**  
「チャノン君、この100GbE用パケットバッファのFIFO設計書だが、プログラマブル・フル（Almost Full）の閾値設定に重大な懸念がある。FIFO深度が512ワードに対して、閾値（PROG_FULL_THRESH）を`510`に設定しているね。つまりスキッドマージンをわずか2ワードしか取っていない。このデータパスにはAXI Register Sliceが複数段挿入されているが、本当に2ワードで溢れずに止まり切れるのかね？」  
*(Chanon-kun, kono 100GbE-yō paketto baffa no FIFO sekkeisho daga, puroguramaburu furu no ikichi settei ni jūdai na kenen ga aru. FIFO shindo ga 512-wādo ni taishite, ikichi wo 510 ni settei shite iru ne. Tsumari sukiddo mājin wo wazuka 2-wādo shika totte inai. Kono dētapasu ni wa AXI Register Slice ga fukusū-dan sōnyū sarete iru ga, hontō ni 2-wādo de afurezu ni tomarikireru no kane?)*  
**คำแปล:** คุณชานนท์ ในเอกสารออกแบบ FIFO สำหรับบัฟเฟอร์แพ็กเก็ต 100GbE ตัวนี้ ผมมีความกังวลอย่างยิ่งเกี่ยวกับการตั้งค่าขีดจำกัด Almost Full นะ ในขนาดความลึก 512 คำ คุณตั้งค่า Threshold ไว้ที่ `510` หมายความว่าคุณเผื่อ Skid Margin ไว้เพียงแค่ 2 คำเท่านั้น ใน Datapath นี้มีการแทรก AXI Register Slice ไปหลายสเตจ คุณแน่ใจจริงๆ หรือว่าพื้นที่แค่ 2 คำนี้จะหยุดข้อมูลได้ทันโดยไม่ล้นทะลัก?

**チャノン (Chanon):**  
「小林技師長、送信側のMACに対してバックプレッシャー信号（TREADY低下）を送れば、直ちに送信が停止されるため、FIFO手前のフリップフロップ分として2サイクルの余裕があれば十分安全だと見積もっておりました。できる限りバッファを限界まで有効活用したいと考えたためです。」  
*(Kobayashi-gishichō, sōshin-gawa no MAC ni taishite bakku puresshā shingō wo sokureba, tadachini sōshin ga teishi sareru tame, FIFO temae no furippu-furoppu bun to shite 2-saikuru no yoyū ga areba jūbun anzen da to mitsumotte orimashita. Dekiru kagiri baffa wo genkai made yūkō katsuyō shitai to kangaeta tame desu.)*  
**คำแปล:** หัวหน้าโคบายาชิครับ เมื่อเราส่งสัญญาณ Backpressure (ลด TREADY) ไปยัง MAC ฝั่งส่ง การส่งข้อมูลจะหยุดลงทันที ผมจึงประเมินว่าการเผื่อไว้ 2 ไซเคิลสำหรับฟลิปฟล็อปหน้า FIFO น่าจะปลอดภัยเพียงพอแล้วครับ ทั้งนี้เพราะผมต้องการใช้พื้นที่ของบัฟเฟอร์ให้คุ้มค่าที่สุดจนถึงขีดจำกัดครับ

**小林技師長 (Kobayashi):**  
「君は**『パイプラインの往復遅延（Round-Trip Skid Latency）』**の概念を全く計算に入れていない！Timing Closureを通すために挿入したAXI Register Sliceを数えてみなさい。TREADYの逆方向パスに2段、TDATAの順方向パスに2段、さらにMAC内部のFSM応答に1サイクル、そしてRegister Slice内のSkid Registerに1ワードある。合計で**最低6サイクルのインフライト（飛行中）データ**がパイプラインの中に残っているんだよ！510でフラグを立てても、6ワードが雪崩れ込んできたら`510 + 6 = 516`で完全にバッファオーバーフローを引き起こす！」  
*(Kimi wa "paipurain no ōfuku chien no gainen wo mattaku keisan ni irete inai! Timing Closure wo tōsu tame ni sōnyū shita AXI Register Slice wo kazoete minasai. TREADY no gyakkōkō pasu ni 2-dan, TDATA no junkōkō pasu ni 2-dan, sarani MAC naibu no FSM ōtō ni 1-saikuru, soshite Register Slice nai no Skid Register ni 1-wādo aru. Gōkei de saitei 6-saikuru no infuraito dēta ga paipurain no naka ni nokotte iru n da yo! 510 de furagu wo tatetemo, 6-wādo ga nadarekonde kitara 510 + 6 = 516 de kanzen ni baffa ōbāfurō wo hikiokosu!)*  
**คำแปล:** นี่คุณไม่ได้คิดถึงแนวคิดเรื่อง **"Round-Trip Skid Latency ของทั้งไปป์ไลน์"** เลยสักนิด! ลองไปนับดูจำนวน AXI Register Slice ที่ใส่เข้าไปเพื่อปิด Timing ดูซิ ขาสัญญาณ TREADY ขากลับมี 2 สเตจ, ขาสัญญาณ TDATA ขาไปมี 2 สเตจ, ลอจิก FSM ภายใน MAC ตอบสนองอีก 1 ไซเคิล, และมี Skid Register ภายใน Register Slice อีก 1 คำ รวมแล้วมี **ข้อมูลที่กำลังบินค้างอยู่ในท่ออย่างน้อย 6 คำ** เต็มๆ! ต่อให้คุณยกเตือนภัยที่ 510 แต่ข้อมูล 6 คำทะลักเข้ามา มันจะกลายเป็น `510 + 6 = 516` ซึ่งล้นทะลักและเกิด Buffer Overflow ทันที!

**チャノン (Chanon):**  
「ハッ……！Register Sliceの往復遅延とIn-Flightデータのことを見落としておりました……！2ワードの余裕では、データ破壊を自ら招いているようなものでした……！」  
*(Ha'... Register Slice no ōfuku chien to In-Flight dēta no koto wo miotoshite orimashita...! 2-wādo no yoyū dewa, dēta hakai wo mizukara maneite iru yō na mono deshita...!)*  
**คำแปล:** อ๊ะ...! ผมมองข้ามความล่าช้าไป-กลับของ Register Slice และข้อมูล In-Flight ไปอย่างสิ้นเชิงเลยครับ...! การเผื่อไว้แค่ 2 คำ มันเหมือนกับการสร้างกับดักทำลายข้อมูลด้วยตัวเองชัดๆ เลยครับ...!

**小林技師長 (Kobayashi):**  
「そうだ。さらに単一の閾値ではチャタリングが発生してスループットが激減する。直ちに**ヒステリシス付きのDual Watermark方式**へ改版しなさい。Assert閾値を`504`（マージン8ワード）、Negate閾値を`472`に設定すれば、チャタリングを防ぎつつ100GbEのフルラインレートを維持できる。SVAアサーションでHard Full到達がゼロであることを形式証明した上で、再提出しなさい！」  
*(Sō da. Sarani tan'itsu no ikichi dewa chataringu ga hassei shite surūputto ga gekigen suru. Tadachini hisuterishisu-tsuki no Dual Watermark hōshiki e kaihan shinasai. Assert ikichi wo 504, Negate ikichi wo 472 ni settei sureba, chataringu wo fusegitsutsu 100GbE no furu rain rēto wo iji dekiru. SVA asāshon de Hard Full tōtatsu ga zero de aru koto wo keishiki shōmei shita ue de, sai-teishutsu shinasai!)*  
**คำแปล:** ถูกต้อง และยิ่งไปกว่านั้น การใช้เกณฑ์ตัวเลขระดับเดียวจะทำให้เกิด Chattering จน Throughput หดหายอย่างรุนแรง จงรีบแก้ไขเป็น **ระบบ Dual Watermark แบบมี Hysteresis** ทันที ตั้งเกณฑ์ Assert ไว้ที่ `504` (มาร์จิน 8 คำ) และตั้งเกณฑ์ Negate ไว้ที่ `472` วิธีนี้จะป้องกัน Chattering และรักษาความเร็ว 100GbE Full Line-Rate ได้อย่างมั่นคง พร้อมทั้งเขียน SVA Assertion พิสูจน์ว่าไม่มีวันชน Hard Full แล้วค่อยส่งมาให้ตรวจใหม่!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณ Skid Margin Budget สำหรับ High-Speed AXI4-Stream Pipeline
ในระบบประมวลผลเครือข่ายความเร็วสูง สัญญาณข้อมูล $512\text{ บิต}$ เชื่อมต่อระหว่างโมดูลส่งและโมดูลรับ FIFO ผ่านเครือข่ายที่ต้องทำ Timing Closure ที่ $400\text{ MHz}$ ($T_{clk} = 2.50\text{ ns}$):
* เพื่อให้ความเร็วถึง $400\text{ MHz}$ วิศวกรใส่ AXI Register Slice บน Datapath (`TDATA/TVALID`) จำนวน $3\text{ สเตจ}$
* บนเส้นทางส่งสัญญาณตอบรับ Backpressure (`TREADY`) มีการใส่ Register Slice จำนวน $2\text{ สเตจ}$
* ตัวส่งสัญญาณต้นทาง (Data Producer) ใช้สเตตแมชชีนที่มีเวลาตอบสนองในการหยุดส่ง (Reaction Time) เท่ากับ $1\text{ ไซเคิล}$ หลังจากที่ขา `TREADY` หน้าโมดูลตกลงเป็น `0`
* แต่ละ Register Slice มีโครงสร้าง Skid Buffer ภายในที่อาจกักเก็บข้อมูลไว้ได้ $1\text{ คำ}$
* ข้อกำหนดความปลอดภัยตามมาตรฐาน DO-254 DAL-A กำหนดให้ต้องใส่ Safety Guard Band อย่างน้อย $+2\text{ ไซเคิล}$

หาก FIFO มีขนาดความลึกทั้งหมด $Depth = 2048\text{ คำ}$ จงคำนวณหาค่า **Total Skid Margin ($Margin_{skid}$)** และค่า **Programmable Almost Full Assert Threshold ($H_{wm}$)** ที่ปลอดภัยสูงสุด!

---

#### ตัวเลือก:
* **ก)** $Margin_{skid} = 9\text{ คำ}$, $H_{wm} = 2039\text{ คำ}$
* **ข)** $Margin_{skid} = 6\text{ คำ}$, $H_{wm} = 2042\text{ คำ}$
* **ค)** $Margin_{skid} = 3\text{ คำ}$, $H_{wm} = 2045\text{ คำ}$
* **ง)** $Margin_{skid} = 15\text{ คำ}$, $H_{wm} = 2033\text{ คำ}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การวิเคราะห์ In-Flight Data และ Round-Trip Latency:
* ความหน่วงบน Datapath ขาไป ($N_{pipe,fwd}$): มี Register Slices 3 สเตจ $\implies 3\text{ ไซเคิล}$
* ความหน่วงบน Backpressure ขากลับ ($N_{pipe,rev}$): มี Register Slices 2 สเตจ $\implies 2\text{ ไซเคิล}$
* เวลาตอบสนองของตัวส่ง ($N_{tx\_reaction}$): $\implies 1\text{ ไซเคิล}$
* สรุปจำนวนคำที่อาจตกค้างอยู่ในท่อ (In-Flight Data คำนวณตามเวลา):
  $$N_{flight} = N_{pipe,fwd} + N_{pipe,rev} + N_{tx\_reaction} = 3 + 2 + 1 = 6\text{ ไซเคิล (6 คำ)}$$
* ข้อมูลสำรองที่อาจถูกปล่อยออกจาก Skid Buffer ในสเตจสุดท้าย: $\implies 1\text{ คำ}$
* Safety Guard Band ตามข้อกำหนด: $\implies +2\text{ ไซเคิล}$

##### 2. การคำนวณ Total Skid Margin:
$$Margin_{skid} = N_{flight} + N_{skid\_buf} + N_{guard} = 6 + 1 + 2 = 9\text{ คำ}$$

##### 3. การคำนวณ High Watermark Assert Threshold ($H_{wm}$):
$$H_{wm} = \text{Depth} - Margin_{skid} = 2048 - 9 = 2039\text{ คำ}$$

ดังนั้น ระบบจะต้องยกสัญญาณ `prog_full = 1` ทันทีที่ข้อมูลสะสมแตะ **$2039\text{ คำ}$** เพื่อรับประกันว่าในกรณีเลวร้ายที่สุด ข้อมูลตกค้างจะไม่เกิน 9 คำ และ FIFO จะไม่มีวันชนขีดจำกัด $2048$ จนเกิด Overflow!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** คิดเฉพาะเวลาหน่วงรวม $3+2+1 = 6$ โดยลืมคิด Skid Buffer และ Guard Band
* **ข้อ ค):** คิดเฉพาะ Datapath ขาไป 3 สเตจ โดยลืมคิดความล่าช้าของสายส่ง Backpressure ขากลับ
* **ข้อ ง):** เผื่อค่ามากเกินไปโดยไม่จำเป็น (Over-design) ซึ่งลดทอนความจุใช้งานจริงของบัฟเฟอร์

---

### ข้อที่ 2: การวิเคราะห์ปรากฏการณ์ Throughput Collapse จาก Chattering ใน Single-Threshold FIFO
พิจารณา FIFO ขนาด $Depth = 512$ ที่เชื่อมต่อกับแหล่งกำเนิดข้อมูลที่มีความเร็วสูงสุด $1\text{ Word / Cycle}$ โดยใช้สัญญาณ `almost_full` แบบ Single Threshold ที่ค่า $Count = 500$ (ยกขึ้นเมื่อ $Count \ge 500$ และดับลงทันทีเมื่อ $Count < 500$):
* ฝั่งส่งข้อมูลมี Round-Trip Reaction Latency เท่ากับ $4\text{ ไซเคิล}$
* ฝั่งรับข้อมูลทำการอ่านข้อมูลออกอย่างต่อเนื่องด้วยอัตราความเร็ว $1\text{ Word / Cycle}$

เมื่อระบบเริ่มสะสมข้อมูลจนแตะค่า $500$ คำเป็นครั้งแรก ข้อใดต่อไปนี้อธิบาย **พฤติกรรมของ Throughput เฉลี่ยของระบบ** ได้อย่างถูกต้องที่สุด?

---

#### ตัวเลือก:
* **ก)** Throughput จะยังคงอยู่ที่ $100\%$ ($1\text{ Word/cycle}$) เพราะฝั่งรับอ่านข้อมูลอย่างต่อเนื่อง
* **ข)** Throughput จะตกลงเหลือประมาณ **$20\% \sim 25\%$** ของความเร็วสูงสุด เนื่องจากทุกครั้งที่ `almost_full` ยกขึ้น ฝั่งส่งจะหยุดส่งไป 4 ไซเคิล จากนั้นเมื่อข้อมูลลดลงเหลือ 499 สัญญาณจะดับลง แต่ฝั่งส่งต้องใช้เวลาอีก 4 ไซเคิลกว่าข้อมูลใหม่จะเดินทางมาถึง ทำให้เกิดฟองอากาศ (Bubbles) สลับหยุดพักเป็นวงจร Chattering ซ้ำๆ
* **ค)** FIFO จะเกิดความร้อนสูงจนชิปตัดการทำงาน
* **ง)** ฝั่งรับจะหยุดอ่านข้อมูลโดยอัตโนมัติ

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **วงจร Chattering Cycle Dynamic:**
   * เมื่อ $Count = 500$: สัญญาณ `almost_full` ยกขึ้น $\to$ ข่าวสารเดินทางไปถึงฝั่งส่งใน 2 ไซเคิล $\to$ ฝั่งส่งหยุดส่ง
   * ในระหว่างนั้น ฝั่งรับอ่านข้อมูลออกไป 4 คำ ทำให้ $Count$ ลดลงเหลือ $496$
   * สัญญาณ `almost_full` ดับลงทันทีที่ $Count < 500$ $\to$ ข่าวสารเดินทางไปถึงฝั่งส่งใน 2 ไซเคิล $\to$ ฝั่งส่งเริ่มส่งใหม่
   * ทว่า ข้อมูลชุดใหม่ต้องใช้เวลาเดินทางในท่ออีก 2 ไซเคิลกว่าจะมาถึง FIFO
   * ในช่วงเวลานี้ FIFO ไม่ได้รับข้อมูลใหม่เลยเป็นเวลาหลายไซเคิล
2. **ผลกระทบต่อ Throughput:**
   * ระบบจะตกอยู่ในวงจร: "ส่งข้อมูลได้ 1-2 คำ $\to$ สัญญาณตัด $\to$ หยุดชะงักรอคอย 4 ไซเคิล $\to$ ส่งใหม่ 1-2 คำ"
   * ประสิทธิภาพการส่งข้อมูล (Effective Bandwidth) จะพังทลายลงจาก $100\%$ ดิ่งลงเหลือเพียง **$20\% \sim 25\%$** ทันที!
   * การแก้ไขมีเพียงทางเดียวคือการใช้ **Hysteresis Dual Thresholds** เพื่อเปิดหน้าต่างส่งข้อมูลเป็นก้อนใหญ่ (Burst Band)!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ละเลยผลกระทบของ Pipeline Reaction Latency บนสายควบคุม
* **ข้อ ค):** ปัญหา Throughput Drop ไม่ได้ทำให้เกิดการ Overheat จนชิปตัดการทำงาน
* **ข้อ ง):** ฝั่งรับยังคงอ่านข้อมูลได้ตามปกติจนกว่า FIFO จะว่าง

---

### ข้อที่ 3: การประเมินบทบาทของ Programmable Almost Empty ในการป้องกัน AXI DMA Read Stall
ในการออกแบบระบบอ่านข้อมูลจากหน่วยความจำด้วย AXI4 DMA Engine ข้อใดต่อไปนี้คือ **เหตุผลหลักที่ต้องใช้สัญญาณ `prog_empty` (Low Watermark)** แทนที่จะใช้สัญญาณ `empty` ธรรมดา?

---

#### ตัวเลือก:
* **ก)** เพื่อประหยัดพลังงานไฟฟ้าของชิป FPGA
* **ข)** เพื่อให้มั่นใจว่า DMA Engine จะเริ่มยิงคำสั่ง AXI Read Burst (เช่น Burst Length = 16 หรือ 32) ก็ต่อเมื่อ **มีข้อมูลสะสมใน FIFO ครบตามขนาดของ Burst แล้วเท่านั้น** ป้องกันไม่ให้เกิดสภาวะ Read Stall กลางคัน ซึ่งจะทำให้บัส AXI เสียแบนด์วิดท์ไปกับการรอคอย (Idle Wait States)
* **ค)** เพราะสัญญาณ `empty` ธรรมดาไม่สามารถสังเคราะห์ลงใน FPGA ได้
* **ง)** เพื่อเพิ่มความถี่สัญญาณนาฬิกาของ DMA เป็น 1 GHz

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **ธรรมชาติของ AXI Burst Transactions:**
   การส่งข้อมูลแบบ Burst (เช่น `ARLEN = 15` หมายถึงอ่าน 16 คำติดต่อกัน) มีประสิทธิภาพสูงเพราะส่งแอดเดรสเพียงครั้งเดียวและรับข้อมูลต่อเนื่อง 16 ไซเคิล
2. **ปัญหาของการใช้ `empty` ปกติ:**
   หาก DMA เริ่มยิงคำสั่งอ่านทันทีที่ `empty = 0` (มีข้อมูลเพียง 1 หรือ 2 คำ):
   * ข้อมูล 2 คำแรกจะถูกอ่านออกไปอย่างรวดเร็ว
   * จากนั้นในคำที่ 3 FIFO จะว่างเปล่า (`empty = 1`) ทำให้ DMA ต้องดึงสัญญาณ `RREADY` หรือรอคอยข้อมูล
   * บัส AXI จะเกิดสภาวะ Stall ค้างท่อ กีดกันให้อุปกรณ์ตัวอื่นในระบบไม่สามารถเข้าถึงหน่วยความจำได้
3. **บทบาทของ `prog_empty`:**
   การตั้งค่า $\text{PROG\_EMPTY\_THRESH} = 16$ จะทำให้สัญญาณแจ้งความพร้อมถูกยกขึ้นเมื่อมีข้อมูลสะสมครบ 16 คำขึ้นไปเท่านั้น ทำให้รอบการอ่าน Burst ดำเนินไปอย่างต่อเนื่อง $100\%$ โดยไม่สะดุดแม้แต่ไซเคิลเดียว!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** การใช้แฟล็กเพิ่มเติมไม่ได้ช่วยประหยัดพลังงานโดยตรง
* **ข้อ ค):** สัญญาณ `empty` เป็นสัญญาณพื้นฐานที่สังเคราะห์ได้ในทุก FPGA
* **ข้อ ง):** ความถี่สัญญาณนาฬิกาถูกกำหนดโดย PLL/MMCM และ Timing Constraints ไม่ได้ขึ้นอยู่กับสัญญาณ Flag
