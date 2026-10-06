# Lesson 181: FPGA FIFO Part 1 - Synchronous FIFO Microarchitecture (Circular Buffer Pointer Physics, Pipeline Latencies, FWFT vs Standard Read Modes & LUTRAM vs BRAM Trade-offs)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมระดับไมโครของ Synchronous Single-Clock FIFO
ในบรรดาโครงสร้างหน่วยความจำชั่วคราวบน FPGA **Synchronous FIFO (First-In, First-Out Memory ทำงานบนสัญญาณนาฬิกาเดี่ยว)** คือองค์ประกอบพื้นฐานที่สำคัญที่สุดในการจัดการทราฟฟิกข้อมูล ทำหน้าที่เป็นตัวดูดซับความผันผวนของอัตราการส่งข้อมูล (Burst Rate Absorber), ตัวปรับอัตราความเร็วของ Pipeline (Rate-Matching Buffer), และอินเทอร์เฟซรองรับการไหลของข้อมูลในโปรโตคอล AXI4-Stream

```
               สถาปัตยกรรมระดับไมโคร SYNCHRONOUS FIFO (SINGLE CLOCK)
               
                             ┌─────────────────────────┐
      wdata ════════════════►│ D                     Q ├════════════════► rdata
                             │   DUAL-PORT SRAM ARRAY  │
      wr_en ──┐              │   (LUTRAM หรือ BRAM)    │
              ▼              │                         │
      ┌───────────────┐      │                         │      ┌───────────────┐
      │ Write Pointer ├─────►│ WADDR             RADDR │◄─────┤ Read Pointer  │◄── rd_en
      │ Counter (wptr)│      └─────────────────────────┘      │ Counter (rptr)│
      └───────┬───────┘                                       └───────┬───────┘
              │                                                       │
              └───────────────────────┬───────────────────────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │ OCCUPANCY & STATUS LOGIC  │
                        │   (fifo_count, full, empty│
                        └─────────────┬─────────────┘
                                      ├──► full
                                      └──► empty
```

#### หลักการทำงานเชิงฟิสิกส์ของ Circular Ring Buffer:
1. **Pointer Traversal:** หน่วยความจำถูกมองเป็นวงแหวนปิด (Circular Ring) ที่มีขนาดความจุ $Depth = 2^{ADDR\_WIDTH}$:
   * **Write Pointer (`wptr`):** ชี้ไปยังตำแหน่งถัดไปที่จะเขียนข้อมูลลงหน่วยความจำ
   * **Read Pointer (`rptr`):** ชี้ไปยังตำแหน่งถัดไปที่จะอ่านข้อมูลออกจากหน่วยความจำ
2. **เงื่อนไขสถานะ Empty และ Full:**
   * **Empty Condition:** เมื่อ `wptr == rptr` (พอยน์เตอร์เขียนและอ่านอยู่ที่ตำแหน่งเดียวกัน และไม่มีข้อมูลสะสม)
   * **Full Condition:** เมื่อพอยน์เตอร์เขียนวิ่งวนรอบมาไล่กวดพอยน์เตอร์อ่านจนทัน (ระยะห่างเท่ากับ $Depth$)
3. **การแก้ปัญหาความคลุมเครือของสถานะ (Disambiguation Physics):**
   * หากใช้พอยน์เตอร์ขนาด $ADDR\_WIDTH$ บิต สภาวะ `wptr == rptr` จะคลุมเครือระหว่าง "FIFO ว่างเปล่า ($Count = 0$)" กับ "FIFO เต็มพิกัด ($Count = Depth$)"
   * วิธีแก้ปัญหาที่นิยมใน Synchronous FIFO มี 2 วิธี:
     * **วิธีที่ 1 (Occupancy Counter):** ใช้ตัวนับจำนวนข้อมูลจริง `fifo_count` ขนาด $ADDR\_WIDTH + 1$ บิต
       $$\text{fifo\_count} \Leftarrow \text{fifo\_count} + \text{wr\_en} - \text{rd\_en}$$
     * **วิธีที่ 2 (Pointer MSB Expansion):** ขยายพอยน์เตอร์เป็น $ADDR\_WIDTH + 1$ บิต โดยใช้บิตบนสุดเป็นตัวนับรอบการหมุน (Wrap-around Bit)

---

### 1.2 โหมดการอ่าน: Standard Read เทียบกับ First-Word-Fall-Through (FWFT)

หนึ่งในสาเหตุยอดฮิตที่ทำให้วิศวกรเชื่อมต่อ FIFO เข้ากับบัสมาตรฐาน (เช่น AXI-Stream, PCIe TLP) ผิดพลาด คือการเลือก **โหมดการอ่าน (Read Mode)** ผิดประเภท:

```
          การเปรียบเทียบระหว่าง STANDARD READ MODE และ FWFT MODE
          
   [ 1. STANDARD READ MODE (1-Cycle Latency) ]
   
       CLK   : ──/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_
     empty   : ‾‾‾‾‾‾‾‾‾‾\_______________________  (ข้อมูลพร้อมแล้ว แต่ยังไม่โผล่ที่เอาต์พุต!)
     rd_en   : ____________/‾‾‾\_________________  (ต้องร้องขอก่อน!)
                               ▲
      dout   : ════════════════< Data 0 >════════  (โผล่ในไซเคิลถัดไปหลังจาก rd_en)
                               ├───────┤
                             Latency = 1 Cycle
                             
   [ 2. FIRST-WORD-FALL-THROUGH: FWFT (0-Cycle Fall-Through) ]
   
       CLK   : ──/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_
     empty   : ‾‾‾‾‾‾‾‾‾‾\_______________________
      dout   : ══════════< Data 0 >══════════════  (ข้อมูลคำแรก "หล่นลงมารอ" ทันที!)
     rd_en   : ____________/‾‾‾\_________________  (rd_en หมายถึง: "รับ Data 0 ไปแล้ว และดึงคำถัดไปมา!")
                               ▲
      dout   : ════════════════< Data 1 >════════
```

#### การวิเคราะห์เชิงสถาปัตยกรรม (Architectural Breakdown):

| คุณลักษณะ (Characteristics) | Standard Read Mode (โหมดมาตรฐาน) | FWFT Mode (First-Word-Fall-Through) |
|:---|:---|:---|
| **พฤติกรรมของข้อมูลที่ขาออก** | ข้อมูลจะปรากฏ **หลังจาก** ที่ยกสัญญาณ `rd_en` ขึ้น 1 ไซเคิล | ข้อมูลคำแรกจะ **ปรากฏรออยู่ที่ขาออกทันที** ที่ FIFO ไม่ว่าง (`empty = 0`) |
| **ความหมายของสัญญาณ `rd_en`** | "ขออ่านข้อมูล (Read Request)" | "ยอมรับข้อมูลปัจจุบัน (Acknowledge / Consume Data)" |
| **ความล่าช้า (Read Latency)** | $1\text{ Clock Cycle}$ | **$0\text{ Clock Cycle}$ (Zero-latency Lookahead)** |
| **การเชื่อมต่อกับ AXI-Stream** | ต้องใช้วงจร Skid Buffer เพิ่มเติม | **ต่อตรงเข้า `TVALID` และ `TDATA` ได้ทันที $100\%$** |
| **ความซับซ้อนของลอจิก** | เรียบง่ายที่สุด (Direct Memory Output) | ต้องใช้วงจร Output Shadow Register (Skid Buffer) |

---

### 1.3 สถาปัตยกรรม Skid Buffer (Output Register Architecture สำหรับ FWFT บน Block RAM)

เนื่องจากฮาร์ดแวร์ Block RAM (BRAM) บน FPGA เป็นหน่วยความจำแบบ **Synchronous Read เสมอ** (ต้องใช้เวลา 1 รอบสัญญาณนาฬิกาในการโหลดค่าแอดเดรสเข้าพอร์ตและขับข้อมูลออกมา) การจะสร้างโหมด FWFT บน Block RAM จึงจำเป็นต้องมีวงจร **Skid Buffer (Shadow Register)** อยู่ที่เอาต์พุต:

```
               สถาปัตยกรรม SKID BUFFER สำหรับสร้าง FWFT BRAM FIFO
               
    ┌────────────────┐
    │   BLOCK RAM    │       bram_dout
    │   MEMORY CORE  ├──────────────────────┐
    │ (Synchronous)  │                      │
    └────────────────┘                      ▼
                                      ┌───────────┐
                                      │ 1       M │
                               ┌─────►│   MUX   X ├────► fwft_dout (Valid Data)
                               │      │ 0       U │
                               │      └─────▲─────┘
                               │            │
                               │      ┌─────┴─────┐
                               └──────┤ Shadow Reg│◄── (กักเก็บข้อมูลสำรองไว้ 1 คำ
                                      │ (Skid Reg)│     เมื่อปลายทางหยุดรับกะทันหัน)
                                      └───────────┘
```

#### กลไกการทำงานของ Skid Buffer:
1. **สภาวะ Pre-fetch:** เมื่อมีข้อมูลถูกเขียนเข้า BRAM เป็นคำแรก ลอจิกจะสั่งอ่าน BRAM ออกมาเก็บไว้ที่ `fwft_dout` ล่วงหน้าทันที 1 ไซเคิล ทำให้ข้อมูลพร้อมให้ระบบภายนอกอ่านแบบ 0-Cycle
2. **สภาวะ Skid:** หากระบบภายนอกอ่านข้อมูลคำนั้นไป (`rd_en = 1`) ในขณะที่ BRAM กำลังส่งข้อมูลคำที่ 2 ออกมา ทว่าระบบภายนอกเกิดปลดสัญญาณอ่านกะทันหัน (`rd_en = 0` ในรอบถัดไป): ข้อมูลคำที่ 2 ที่หลุดออกมาจาก BRAM แล้ว จะถูกเบี่ยงเส้นทางเข้าไปกักเก็บไว้ใน **Shadow Register (Skid Register)** เพื่อไม่ให้ข้อมูลสูญหาย
3. เมื่อระบบภายนอกกลับมาอ่านใหม่ ข้อมูลใน Shadow Register จะถูกส่งออกไปเป็นลำดับแรก จากนั้นจึงสลับกลับไปอ่านจาก BRAM ตามปกติ

---

### 1.4 การเลือกใช้ทรัพยากร: Distributed LUTRAM เทียบกับ Dedicated Block RAM

| มิติการเปรียบเทียบ (Metric) | Distributed LUTRAM (SLICEM) | Dedicated Block RAM (BRAM / URAM) |
|:---|:---|:---|
| **โครงสร้างทางกายภาพ** | ใช้ Function Generators (LUT) ใน SLICEM | ใช้ฮาร์ดแวร์ก้อนสำเร็จรูป (RAMB18E2 / RAMB36E2) |
| **ความสามารถด้าน Read** | **Asynchronous Read ได้ (Combinational Output)** | **Synchronous Read เท่านั้น (ต้องมี Clock)** |
| **ขนาดความลึกที่เหมาะสม** | ขนาดเล็กถึงปานกลาง ($Depth \le 64$ หรือ $128$) | ขนาดใหญ่ ($Depth \ge 512$ ถึง $32,768$) |
| **ประสิทธิภาพความเร็ว ($F_{max}$)** | สูงมากบนขนาดเล็ก แต่จะลดลงเร็วหากขยายขนาด | สูงมาก ($> 450\text{ MHz}$ บน UltraScale+) |
| **ผลกระทบต่อ Logic Slices** | แย่งชิงทรัพยากร LUT ที่ใช้ทำลอจิกทั่วไป | ไม่กินพื้นที่ LUT ลอจิกเลยแม้แต่ตัวเดียว |
| **โหมด FWFT โดยธรรมชาติ** | ทำได้ทันทีโดยไม่ต้องใช้ Skid Buffer | **ต้องติดตั้ง Skid Buffer เสมอ** |

---

### 1.5 โค้ดแม่แบบภาษา Verilog ระดับ Senior สำหรับ Synchronous FIFO (รองรับ FWFT)

```verilog
// ==============================================================================
// SENIOR SYNCHRONOUS FIFO (SINGLE CLOCK) WITH CONFIGURABLE FWFT MODE
// Pure RTL, Parameterized Data Width and Depth, Dual-Port RAM Inferencing
// ==============================================================================
(* keep_hierarchy = "yes" *)
module sync_fifo #(
    parameter integer DATA_WIDTH = 32,
    parameter integer ADDR_WIDTH = 6,   // Depth = 2^ADDR_WIDTH (64 words)
    parameter integer FWFT_MODE  = 1    // 0: Standard Read, 1: First-Word-Fall-Through
)(
    input  wire                  clk,
    input  wire                  rst_n,
    
    // Write Interface
    input  wire                  wr_en,
    input  wire [DATA_WIDTH-1:0] din,
    output wire                  full,
    output wire                  almost_full,
    
    // Read Interface
    input  wire                  rd_en,
    output wire [DATA_WIDTH-1:0] dout,
    output wire                  empty,
    output wire                  almost_empty,
    
    // Occupancy
    output wire [ADDR_WIDTH:0]   data_count
);

    localparam integer DEPTH = 1 << ADDR_WIDTH;

    // -------------------------------------------------------------------------
    // 1. Dual-Port Memory Core Array (LUTRAM or BRAM Inferencing)
    // -------------------------------------------------------------------------
    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];
    reg [ADDR_WIDTH-1:0] wptr;
    reg [ADDR_WIDTH-1:0] rptr;
    reg [ADDR_WIDTH:0]   count;

    // Write Operation
    wire write_valid = wr_en && !full;
    always @(posedge clk) begin
        if (write_valid)
            mem[wptr] <= din;
    end

    // -------------------------------------------------------------------------
    // 2. Internal Read and Pointer Logic
    // -------------------------------------------------------------------------
    wire read_valid_internal;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wptr  <= {ADDR_WIDTH{1'b0}};
            rptr  <= {ADDR_WIDTH{1'b0}};
            count <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            case ({write_valid, read_valid_internal})
                2'b10: begin // Write only
                    wptr  <= wptr + 1'b1;
                    count <= count + 1'b1;
                end
                2'b01: begin // Read only
                    rptr  <= rptr + 1'b1;
                    count <= count - 1'b1;
                end
                2'b11: begin // Simultaneous Write and Read
                    wptr  <= wptr + 1'b1;
                    rptr  <= rptr + 1'b1;
                    count <= count; // Occupancy unchanged!
                end
                default: ; // Idle
            endcase
        end
    end

    wire fifo_empty_internal = (count == 0);
    wire fifo_full_internal  = (count == DEPTH);

    // -------------------------------------------------------------------------
    // 3. Output Mode Architecture (Standard vs FWFT Skid Buffer)
    // -------------------------------------------------------------------------
    generate
        if (FWFT_MODE == 0) begin : gen_standard_mode
            // Standard Read: 1-cycle latency upon rd_en
            reg [DATA_WIDTH-1:0] dout_reg;
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n)
                    dout_reg <= {DATA_WIDTH{1'b0}};
                else if (rd_en && !fifo_empty_internal)
                    dout_reg <= mem[rptr];
            end

            assign read_valid_internal = rd_en && !fifo_empty_internal;
            assign dout                = dout_reg;
            assign empty               = fifo_empty_internal;
            assign full                = fifo_full_internal;
            assign almost_empty        = (count <= 1);
            assign almost_full         = (count >= DEPTH - 1);
            assign data_count          = count;

        end else begin : gen_fwft_skid_mode
            // FWFT Mode: 0-cycle latency with Skid Buffer
            reg [DATA_WIDTH-1:0] skid_buf;
            reg [DATA_WIDTH-1:0] out_reg;
            reg                  out_valid;
            reg                  skid_valid;

            assign read_valid_internal = !fifo_empty_internal && (!out_valid || rd_en || !skid_valid);

            always @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    out_reg    <= {DATA_WIDTH{1'b0}};
                    skid_buf   <= {DATA_WIDTH{1'b0}};
                    out_valid  <= 1'b0;
                    skid_valid <= 1'b0;
                end else begin
                    // Skid Buffer Control FSM Logic
                    if (rd_en) begin
                        if (skid_valid) begin
                            out_reg    <= skid_buf;
                            skid_valid <= 1'b0;
                        end else if (read_valid_internal) begin
                            out_reg    <= mem[rptr];
                            out_valid  <= 1'b1;
                        end else begin
                            out_valid  <= 1'b0;
                        end
                    end else begin
                        if (read_valid_internal) begin
                            if (!out_valid) begin
                                out_reg   <= mem[rptr];
                                out_valid <= 1'b1;
                            end else begin
                                skid_buf   <= mem[rptr];
                                skid_valid <= 1'b1;
                            end
                        end
                    end
                end
            end

            assign dout         = out_reg;
            assign empty        = !out_valid;
            assign full         = fifo_full_internal;
            assign almost_empty = (count == 0 && out_valid);
            assign almost_full  = (count >= DEPTH - 2);
            assign data_count   = count + out_valid + skid_valid;
        end
    endgenerate

endmodule
```

---

### 1.6 SystemVerilog Assertions (SVA) Formal Property Verification

```systemverilog
// SVA Verification Checker for Synchronous FIFO
module sync_fifo_sva #(
    parameter integer DATA_WIDTH = 32,
    parameter integer DEPTH = 64
)(
    input wire clk,
    input wire rst_n,
    input wire wr_en,
    input wire rd_en,
    input wire full,
    input wire empty,
    input wire [DATA_WIDTH-1:0] din,
    input wire [DATA_WIDTH-1:0] dout
);

    // 1. Safety Assertion: No Write Overflow
    property p_no_overflow;
        @(posedge clk) disable iff (!rst_n)
        full && wr_en |=> full; // Writing while full must not be permitted
    endproperty
    assert_overflow: assert property (p_no_overflow)
        else $error("[FATAL_FIFO]: Write attempt occurred when FIFO was FULL!");

    // 2. Safety Assertion: No Read Underflow
    property p_no_underflow;
        @(posedge clk) disable iff (!rst_n)
        empty && rd_en |=> empty; // Reading while empty must not be permitted
    endproperty
    assert_underflow: assert property (p_no_underflow)
        else $error("[FATAL_FIFO]: Read attempt occurred when FIFO was EMPTY!");

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】ระบบกล้องสแกนตรวจจับข้อบกพร่องซิลิคอนเวเฟอร์ (High-Speed Wafer AOI)
เกิดอาการภาพสแกน 4K ขาดหายไป 1 คอลัมน์ทุกบรรทัด (Missing First Pixel Column)
จากการนำ Standard Read FIFO ไปต่อตรงเข้ากับ AXI4-Stream Video Pipeline
================================================================================
```

#### บริบทของระบบ (System Context):
บริษัทผลิตเครื่องมือตรวจวัดทางแสงอัตโนมัติ (Automated Optical Inspection - AOI) สำหรับโรงงานผลิตเซมิคอนดักเตอร์ พัฒนากล้องตรวจสอบความเร็วสูงระดับ Line-Scan บนชิป FPGA AMD Xilinx Kintex UltraScale+ (`xcku11p`):
* เซนเซอร์ภาพความละเอียดสูงส่งข้อมูลวิดีโอผ่านสตรีม AXI4-Stream ขนาด $64\text{ บิต}$ ความเร็ว $250\text{ MHz}$
* ระหว่าง Line Buffer และตัวประมวลผล Convolutional Filter มีบัฟเฟอร์ FIFO กักเก็บข้อมูลขนาดความลึก $1024\text{ คำ}$
* วิศวกรสร้างโมดูล FIFO โดยใช้โค้ด RTL ดั้งเดิมที่เป็น **Standard Read Mode (Latency = 1 Cycle)** โดยเข้าใจว่าเพียงแค่นำ `!empty` ไปต่อเข้า `TVALID` และนำ `TREADY` ไปต่อเข้า `rd_en` วงจรก็น่าจะทำงานได้

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
เมื่อเปิดการทดสอบสแกนเวเฟอร์ขนาด 300 มิลลิเมตรจริง ภาพที่ได้จากกล้องเกิดอาการ **พิกเซลคอลัมน์แรกสุดของทุกๆ บรรทัด (Pixel [0]) สูญหายไปอย่างไร้ร่องรอย** และในจังหวะที่อัลกอริทึม AI ประมวลผลภาพ โครงสร้างวงจรรวมบนเวเฟอร์เกิดภาพเลี้ยวเบี้ยวผิดพิกัด ส่งผลให้ระบบตีตราเวเฟอร์ที่สมบูรณ์แบบว่าเป็น "ของเสีย (False Scrap)" สูญเสียมูลค่าการผลิตหลายร้อยล้านเยน!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมพิกเซลคอลัมน์แรกของทุกบรรทัดจึงสูญหาย?**
   * *เพราะโมดูล AI Filter ในปลายทาง แซมเปิลข้อมูลในรอบแรกได้ค่าว่างเปล่า (Invalid Zero) และข้อมูลพิกเซลจริงเพิ่งจะหลุดออกมาในรอบถัดไป*
2. **ทำไมข้อมูลพิกเซลจึงเดินทางมาช้ากว่าสัญญาณควบคุม 1 ไซเคิล?**
   * *เพราะสัญญาณ `TVALID` ถูกยกขึ้นพร้อมกับการที่ตัวกรองยกสัญญาณ `TREADY = 1` แต่ FIFO ในโหมด Standard Read ต้องใช้เวลาอีก 1 ไซเคิลในการขับข้อมูลออกจาก BRAM*
3. **ทำไมจึงเกิดความล่าช้า 1 ไซเคิลระหว่าง Valid และ Data?**
   * *เพราะวิศวกรนำโมดูล FIFO แบบ Standard Read Mode มาเชื่อมต่อโดยตรงกับอินเทอร์เฟซ AXI4-Stream ซึ่งมีข้อกำหนดว่า `TDATA` จะต้องพร้อมและเสถียรในไซเคิลเดียวกับที่ `TVALID = 1`*
4. **ทำไมวิศวกรจึงไม่เลือกใช้ FIFO โหมด FWFT (First-Word-Fall-Through)?**
   * *เพราะวิศวกรคิดว่าโหมด Standard Read ประหยัดทรัพยากรลอจิกมากกว่า และเข้าใจผิดว่า AXI4-Stream มีกลไกการรอคอยข้อมูล 1 ไซเคิลโดยอัตโนมัติ*
5. **ทำไม Testbench Simulation จึงตรวจไม่พบข้อบกพร่องนี้?**
   * *เพราะใน Testbench วิศวกรจำลองการอ่านโดยป้อนสัญญาณ `TREADY = 1` แช่ค้างไว้ตลอดเวลา (Continuous Streaming) จึงมองไม่เห็นจังหวะรอยต่อของคำแรก (First Handshake Boundary) ที่เกิดขึ้นจริงในระบบ!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                         สาเหตุของความล้มเหลว: MISSING FIRST PIXEL COLUMN
                         
   METHOD (การเลือกโหมด FIFO)                  MACHINE (ฮาร์ดแวร์และโปรโตคอลบัส)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ใช้ Standard Read แทนที่จะเป็น FWFT│       │ BRAM มี 1-Cycle Read Latency   │
   │ ต่อตรงเข้า AXI-Stream ผิดสเปก  │          │ AXI-Stream บังคับ TVALID/TDATA │
   │ ขาดวงจร Skid Buffer ดักจับข้อมูล│          │ ต้องเสถียรพร้อมกันใน Cycle เดียว│
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ละเลยคู่มือ ARM AMBA AXI4-Stream│         │ Testbench แช่ TREADY = 1 ตลอด  │
   │ ขาดการตรวจแบบ Kenzu เรื่อง Latency│       │ ไม่เคยทดสอบ Backpressure Burst │
   │ ขาด SVA ตรวจสอบ Handshake      │          │ ตรวจไม่พบ Latency Mismatch     │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (ข้อกำหนดและการตรวจสอบ)             MEASUREMENT (สภาวะการจำลอง Testbench)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediations):
1. **เปลี่ยนโหมด FIFO เป็น First-Word-Fall-Through (FWFT):** แก้ไขพารามิเตอร์ `FWFT_MODE = 1` และเปิดใช้งานสถาปัตยกรรม Skid Buffer
2. **ผูกสัญญาณเข้ากับ AXI4-Stream อย่างถูกต้องสมบูรณ์แบบ:**
   * สัญญาณ `TVALID` ต่อเข้ากับ `!empty` ของ FWFT FIFO
   * สัญญาณ `TDATA` ต่อเข้ากับ `dout` ของ FWFT FIFO
   * สัญญาณ `rd_en` ของ FIFO ต่อเข้ากับเงื่อนไข Handshake: `rd_en = TVALID && TREADY`
3. **ปรับปรุง Testbench Simulation:** เพิ่มการจำลองสภาวะ **Random Backpressure** โดยสลับสัญญาณ `TREADY` ขึ้น-ลงแบบสุ่ม เพื่อทดสอบความทนทานของรอยต่อการอ่านทุกคำ

#### ใบตรวจสอบมาตรฐาน SOP สำหรับการเลือก FIFO (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | อินเทอร์เฟซปลายทางเป็น AXI4-Stream / Ready-Valid หรือไม่? | **ต้องใช้ FWFT Mode เท่านั้น** | [ ] ผ่าน |
| 2 | หากใช้ Block RAM ในโหมด FWFT ได้ติดตั้งวงจร Skid Buffer ครบถ้วน? | Verified Skid FSM | [ ] ผ่าน |
| 3 | ขนาดความลึก FIFO เป็นเลขยกกำลังของ 2 ($2^{ADDR\_WIDTH}$) หรือไม่? | Power of 2 | [ ] ผ่าน |
| 4 | มีการป้องกันการเขียนทับเมื่อเต็ม (`!full`) และอ่านเมื่อว่าง (`!empty`) ใน RTL? | Full Safety Protection | [ ] ผ่าน |
| 5 | มีการเขียน SVA ยืนยันว่าไม่มีการเกิด Underflow และ Overflow $100\%$ หรือไม่? | Formal Assertions Passed | [ ] ผ่าน |
| 6 | Testbench มีการทดสอบสภาวะ Backpressure (TREADY toggle) ครบถ้วนหรือไม่? | Handshake Corner Tests | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | 同期FIFO | どうきFIFO | Dōki Faifo | Synchronous FIFO (Single-Clock FIFO) |
| 2 | サーキュラー・バッファ | サーキュラー・バッファ | Sākyurā baffa | Circular Ring Buffer |
| 3 | ファーストワード・フォールスルー | ファーストワード・フォールスルー | Fāsutowādo fōrusurū | First-Word-Fall-Through (FWFT) |
| 4 | スキッドバッファ | スキッドバッファ | Sukiddo baffa | Skid Buffer / Shadow Register |
| 5 | 読み出しレイテンシ | よみだしレイテンシ | Yomidashi reitenshi | Read Latency |
| 6 | バックプレッシャー耐性 | バックプレッシャーたいせい | Bakku puresshā taisei | Backpressure Resilience |
| 7 | 分散RAM / LUTRAM | ぶんさんRAM | Bunsan RAM | Distributed RAM (LUTRAM) |
| 8 | 同時読み書き保証 | どうじよみかきほしょう | Dōji yomikaki hoshō | Simultaneous Read/Write Guarantee |
| 9 | 空き容量カウンタ | あきようりょうカウンタ | Aki yōryō kaunta | Occupancy Counter (`data_count`) |
| 10 | ハンドシェイク不整合 | ハンドシェイクふせいごう | Handosheiku fuseigō | Handshake Protocol Mismatch |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ศูนย์ตรวจสอบระบบตรวจวัดเวเฟอร์เซมิคอนดักเตอร์ (Semiconductor Inspection Systems Division), เมืองโยโกฮาม่า (Yokohama)  
**ผู้เข้าร่วม:**
* **ฮาเซงาวะซัง (Hasegawa-san):** หัวหน้าวิศวกรผู้เชี่ยวชาญการออกแบบสถาปัตยกรรมฮาร์ดแวร์ (Lead Hardware Architect / 主幹技師)
* **ธนกฤต (Thanakrit):** วิศวกรออกแบบระบบประมวลผลภาพ FPGA (Image Processing FPGA Designer)

---

**長谷川主幹 (Hasegawa):**  
「タナクリット君、このウェーハ外観検査装置の画像入力パイプラインだが、実機でラインの先頭ピクセルが毎フレーム欠落する不具合が出ているね。RTLを見ると、ラインバッファFIFOの出力をそのままAXI4-Streamインターフェースの`TDATA`に接続し、`!empty`を`TVALID`に繋いでいる。このFIFOの読み出しモードは、**Standard Read**なのか、それとも**FWFT（First-Word-Fall-Through）**なのかね？」  
*(Tanakritto-kun, kono wēha gaikan kensa sōchi no gazō nyūryoku paipurain daga, jikki de rain no sentō pikuseru ga mai furēmu ketsuraku suru fuguai ga dete iru ne. RTL wo miru to, rain baffa FIFO no shutsuryoku wo sonomama AXI4-Stream intāfēsu no TDATA ni setsuzoku shi, !empty wo TVALID ni tsunaide iru. Kono FIFO no yomidashi mōdo wa, Standard Read nano ka, soretomo FWFT nano kane?)*  
**คำแปล:** คุณธนกฤต ในไปป์ไลน์รับสัญญาณภาพของเครื่องตรวจวัดเวเฟอร์ตัวนี้ ในเครื่องจริงเกิดปัญหาพิกเซลหัวแถวหลุดหายไปทุกบรรทัดนะ พอเปิดดูโค้ด RTL คุณต่อเอาต์พุตของ Line Buffer FIFO เข้ากับขา `TDATA` ของ AXI4-Stream ตรงๆ และต่อ `!empty` เข้ากับ `TVALID` โหมดการอ่านของ FIFO ตัวนี้เป็นแบบ Standard Read หรือว่าเป็น FWFT ครับ?

**タナクリット (Thanakrit):**  
「長谷川主幹、リソース使用量を抑えるため、最もシンプルなStandard Readモードを採用しております。`rd_en`を入力すれば次のクロックでデータが出力されるため、AXI-Streamの`TREADY`ハンドシェイクと問題なく整合すると考えておりました。」  
*(Hasegawa-shukan, risōsu shiyōryō wo osaeru tame, mottomo shinpuru na Standard Read mōdo wo saiyō shite orimasu. rd_en wo nyūryoku sureba tsugi no kurokku de dēta ga shutsuryoku sareru tame, AXI-Stream no TREADY handosheiku to mondai naku seigō suru to kangaete orimashita.)*  
**คำแปล:** หัวหน้าฮาเซงาวะครับ เพื่อประหยัดทรัพยากร ผมเลือกใช้โหมด Standard Read แบบดั้งเดิมครับ เมื่อป้อนสัญญาณ `rd_en` ข้อมูลจะออกมาในไซเคิลถัดไป ผมจึงคิดว่ามันน่าจะทำงานเข้ากันได้กับโปรโตคอล Handshake ของ AXI-Stream `TREADY` ได้โดยไม่มีปัญหาครับ

**長谷川主幹 (Hasegawa):**  
「そこが根本的な間違いだよ！AXI4-Streamのプロトコル仕様書（ARM IHI 0051A）をもう一度読み直しなさい！AXI-Streamでは、**『TVALIDがアサートされたそのサイクルにおいて、TDATAは既に確定していなければならない』**と厳格に規定されている。Standard Readモードだと、受信側がTREADYを立てて読み出しを要求した瞬間、FIFOから出力されるデータはまだ前回の不定値のままであり、本物の先頭ピクセルが出てくるのは1サイクル遅れになるんだ！その結果、先頭データが化けて欠落したんだよ！」  
*(Soko ga komponteki na machigai da yo! AXI4-Stream no purotokoru shiyōsho wo mō ichido yominaoshinasai! AXI-Stream dewa, "TVALID ga asāto sareta sono saikuru ni oite, TDATA wa sudeni kakutei shite inakereba naranai" to genkaku ni kitei sarete iru. Standard Read mōdo dato, jushin-gawa ga TREADY wo tatete yomidashi wo yōkyū shita shunkan, FIFO kara shutsuryoku sareru dēta wa mada zenkai no futeichi no mama de ari, hommono no sentō pikuseru ga dete kuru no wa 1-saikuru okure ni naru n da! Sono kekka, sentō dēta ga bakete ketsuraku shita n da yo!)*  
**คำแปล:** นั่นแหละคือข้อผิดพลาดขั้นรากฐานเลย! จงกลับไปอ่านคู่มือสเปกของ AXI4-Stream ใหม่อีกรอบเดี๋ยวนี้! ใน AXI-Stream มีกฎเหล็กระบุชัดเจนว่า **"ในไซเคิลที่ TVALID ทำงาน ข้อมูลบน TDATA จะต้องนิ่งและถูกต้องพร้อมอยู่แล้ว"** แต่ถ้าคุณใช้ Standard Read เสี้ยววินาทีที่ฝั่งรับยก TREADY ร้องขอข้อมูล ข้อมูลที่ออกจาก FIFO ยังเป็นค่าขยะเดิมอยู่เลย และข้อมูลพิกเซลตัวแรกจริงๆ จะโผล่มาช้าไป 1 ไซเคิล! ผลลัพธ์คือ ข้อมูลตัวแรกจึงพังและสูญหายไปยังไงล่ะ!

**タナクリット (Thanakrit):**  
「あっ……！レイテンシが1サイクルあるStandard Readでは、0サイクル応答が前提のAXI-Streamハンドシェイクを満たせないのですね……！完全にプロトコルの基本を見落としておりました！」  
*(A'... Reitenshi ga 1-saikuru aru Standard Read dewa, 0-saikuru ōtō ga zentei no AXI-Stream handosheiku wo mitasenai no desu ne...! Kanzen ni purotokoru no kihon wo miotoshite orimashita!)*  
**คำแปล:** อ๊ะ...! ใน Standard Read ที่มีความหน่วง 1 ไซเคิล มันไม่สามารถตอบสนองเงื่อนไขของ AXI-Stream Handshake ที่ต้องการการตอบสนองทันที 0 ไซเคิลได้สินะครับ...! ผมมองข้ามหลักการพื้นฐานของโปรโตคอลไปอย่างสิ้นเชิงเลยครับ!

**長谷川主幹 (Hasegawa):**  
「そうだ。ストリーミングやReady/ValidインターフェースにFIFOを直結する場合は、必ず**FWFT（First-Word-Fall-Through）モード**を採用しなければならない。そしてBlock RAMを使うなら、受信側が突然TREADYを下げた時にデータを落とさないよう、**スキッドバッファ（Skid Buffer）**を必ず出力段に組み込みなさい。修正後、ランダムにTREADYをトグルさせるストレステストを走らせて、ピクセル欠落が完全にゼロになることを確認して報告したまえ。」  
*(Sō da. Sutorīmingu ya Ready/Valid intāfēsu ni FIFO wo chokketsu suru baai wa, kanarazu FWFT mōdo wo saiyō shinakereba naranai. Soshite Block RAM wo tsukau nara, jushin-gawa ga totsuzen TREADY wo sageta toki ni dēta wo otosanai yō, sukiddo baffa wo kanarazu shutsuryoku-dan ni kumikominasai. Shūsei-go, randamu ni TREADY wo toguru saseru sutoresu tesuto wo hashirasete, pikuseru ketsuraku ga kanzen ni zero ni naru koto wo kakunin shite hōkoku shitamae.)*  
**คำแปล:** ถูกต้อง หากจะนำ FIFO ไปต่อตรงกับ Streaming หรือ Ready/Valid Interface คุณจะต้องเลือกใช้ **โหมด FWFT เสมอ** และถ้าใช้ Block RAM คุณจะต้องติดตั้ง **Skid Buffer** ไว้ที่สเตจเอาต์พุต เพื่อป้องกันไม่ให้ข้อมูลสูญหายในจังหวะที่ฝั่งรับปลด TREADY ลงกะทันหัน หลังแก้ไขเสร็จ ให้รันการทดสอบ Stress Test โดยสลับสัญญาณ TREADY แบบสุ่ม และยืนยันว่าไม่มีพิกเซลหลุดหายแม้แต่เม็ดเดียว แล้วค่อยมารายงานผม!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การวิเคราะห์พฤติกรรมของ Skid Buffer ในโหมด FWFT เมื่อเกิด Backpressure
พิจารณาวงจร Synchronous FIFO ในโหมด FWFT ที่สร้างบน Block RAM ร่วมกับวงจร Skid Buffer (ขนาดความจุของ Skid Register = 1 คำ):
* ปัจจุบัน FIFO มีข้อมูลสะสมอยู่ภายในทั้งหมด 5 คำ: `[D0, D1, D2, D3, D4]`
* ในไซเคิลปัจจุบัน ($Cycle_1$): ข้อมูลคำแรก `D0` อยู่ที่พอร์ตเอาต์พุต `dout` เรียบร้อยแล้ว (`empty = 0`, `out_valid = 1`), Skid Register ว่างเปล่า (`skid_valid = 0`)
* ในไซเคิลที่ 2 ($Cycle_2$): ฝั่งรับอ่านข้อมูลโดยยก `rd_en = 1` เพียง 1 ไซเคิล
* ในไซเคิลที่ 3 ($Cycle_3$): ฝั่งรับเกิดสภาวะ Backpressure จึงสั่งหยุดรับทันที (`rd_en = 0`)

ข้อใดต่อไปนี้อธิบาย **การเคลื่อนที่ของข้อมูลภายใน Skid Buffer ในช่วง $Cycle_2$ และ $Cycle_3$** ได้อย่างถูกต้องตามหลักวิศวกรรม?

---

#### ตัวเลือก:
* **ก)** ใน $Cycle_2$ ข้อมูล `D0` ถูกดึงออกไป และ BRAM ส่ง `D1` ออกมา; ใน $Cycle_3$ เนื่องจาก `rd_en = 0` ข้อมูล `D1` จะสูญหายไปจากระบบทันที
* **ข)** ใน $Cycle_2$ เมื่อ `rd_en = 1` วงจรจะส่ง `D0` ให้ฝั่งรับ และส่งสัญญาณไปอ่าน BRAM ล่วงหน้าทำให้ `D1` ออกมาจ่อที่ `dout`; ใน $Cycle_3$ เมื่อ `rd_en = 0` ข้อมูล `D1` จะคงอยู่ที่ `dout` อย่างเสถียร โดยไม่ต้องเข้า Skid Register เพราะ BRAM ไม่ได้อ่านข้อมูลคำใหม่เกินออกมา
* **ค)** ใน $Cycle_2$ ข้อมูล `D0` ถูกรับไป และคำสั่งล่วงหน้าอ่าน `D1` และ `D2` ออกมาพร้อมกัน ทำให้เกิด Buffer Overflow
* **ง)** วงจร Skid Buffer จะรีเซ็ตพอยน์เตอร์ของ FIFO กลับไปที่ตำแหน่งเริ่มต้น

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **พฤติกรรมใน $Cycle_2$:**
   * เมื่อ `rd_en = 1` ฝั่งรับทำการ Latch ข้อมูล `D0` เข้าไปประมวลผล
   * ในขณะเดียวกัน ลอจิกควบคุมของ FWFT จะสั่ง `read_valid_internal = 1` ไปยังพอร์ต BRAM เพื่อดึงข้อมูลคำถัดไปคือ `D1` ออกมา
2. **พฤติกรรมใน $Cycle_3$:**
   * ที่ขอบสัญญาณนาฬิกาของ $Cycle_3$ ข้อมูล `D1` หลุดออกจากเอาต์พุตของ BRAM พอดิบพอดี
   * เนื่องจากใน $Cycle_3$ ฝั่งรับปลดสัญญาณเป็น `rd_en = 0` (ไม่พร้อมอ่านคำถัดไป)
   * ลอจิกจะนำ `D1` มาบันทึกค้างไว้ที่ `out_reg` (`dout = D1`) และตั้งค่า `out_valid = 1`
   * และเนื่องจากใน $Cycle_2$ ลอจิกไม่ได้สั่งอ่าน `D2` เผื่อล่วงหน้าเกินกว่า 1 คำ ข้อมูล `D1` จึงค้างอยู่ที่เอาต์พุตได้อย่างปลอดภัย $100\%$ โดยที่ `skid_valid` ยังคงเป็น `0` (ไม่มี Data Loss)
   * กรณีที่ต้องใช้ `skid_buf` คือกรณีที่ BRAM มี Read Latency 2 สเตจ (เช่น มีการเปิดใช้งาน Primitive Output Register `DO_REG = 1` เพื่อเพิ่ม $F_{max}$) ซึ่งทำให้มีข้อมูลค้างท่อ 2 คำ!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ผิดพลาดอย่างสิ้นเชิง เพราะ Skid Buffer ถูกสร้างขึ้นมาเพื่อป้องกันไม่ให้ข้อมูลสูญหายในกรณีนี้โดยเฉพาะ
* **ข้อ ค):** BRAM พอร์ตเดี่ยวไม่สามารถอ่านข้อมูลออกมาพร้อมกัน 2 คำในไซเคิลเดียวได้
* **ข้อ ง):** Skid Buffer เป็นวงจร Datapath ไม่มีสิทธิ์ไปยุ่งเกี่ยวกับการรีเซ็ตพอยน์เตอร์ของ FIFO

---

### ข้อที่ 2: การเปรียบเทียบการใช้ทรัพยากรระหว่าง LUTRAM และ Block RAM
ในโครงการประมวลผลเครือข่ายความเร็วสูง วิศวกรต้องการสร้าง FIFO ขนาดความกว้าง $DATA\_WIDTH = 64\text{ บิต}$ จำนวน 2 ชุด:
1. ชุดที่ 1: ขนาดความลึก $Depth_1 = 32\text{ คำ}$
2. ชุดที่ 2: ขนาดความลึก $Depth_2 = 1024\text{ คำ}$

บนสถาปัตยกรรมชิป AMD Xilinx UltraScale+ (ซึ่งมี LUT ขนาด 6-input สามารถทำ Distributed RAM ได้ขนาด $64 \times 1\text{ bit}$ ต่อ 1 LUT และมี Block RAM บล็อกละ $36\text{ Kb}$ - `RAMB36E2`): ข้อใดต่อไปนี้คือ **การจัดสรรทรัพยากรที่คุ้มค่าและมีประสิทธิภาพสูงสุด (Optimal Resource Allocation)**?

---

#### ตัวเลือก:
* **ก)** ใช้ Block RAM (RAMB36E2) ทั้งสองชุด เพื่อให้ได้ความเร็วเท่ากัน
* **ข)** ใช้ Distributed LUTRAM ทั้งสองชุด เพื่อประหยัด Block RAM ไว้ให้โปรเจกต์อื่น
* **ค)** ชุดที่ 1 ($64 \times 32$) ควรใช้ **Distributed LUTRAM** (ใช้เพียง 64 LUTs จาก SLICEM, ไม่เปลือง BRAM เลยแม้แต่ก้อนเดียว); ส่วนชุดที่ 2 ($64 \times 1024$) ควรใช้ **Dedicated Block RAM** (ใช้ `RAMB36E2` เพียง 2 บล็อก เพราะหากใช้ LUTRAM จะต้องผลาญ LUTs มากถึง 1,024 ตัวและสร้าง MUX Tree มหาศาลจนลดทอนความเร็ว)
* **ง)** ทั้งสองชุดต้องใช้ UltraRAM (URAM288) เท่านั้น

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ค)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **การวิเคราะห์ชุดที่ 1 ($64\text{ bits} \times 32\text{ words}$):**
   * ความจุรวม = $64 \times 32 = 2,048\text{ บิต}$ ($2\text{ Kb}$)
   * หากใช้ BRAM (`RAMB36E2` ขนาด 36 Kb): จะใช้พื้นที่ไปเพียง $\frac{2}{36} \approx 5.5\%$ ซึ่งถือเป็นการสิ้นเปลืองก้อน BRAM สำเร็จรูปอย่างรุนแรง (Resource Under-utilization)
   * หากใช้ LUTRAM: 1 SLICEM LUT ใน UltraScale+ บรรจุได้ $64 \times 1\text{ bit}$ หรือ $32 \times 2\text{ bits}$ ดังนั้นข้อมูล 64 บิตลึก 32 คำ ใช้ LUT เพียง **64 ตัว (เทียบเท่า 8 Slices)** สามารถทำ Asynchronous Read ได้ 0-latency ทันที!
2. **การวิเคราะห์ชุดที่ 2 ($64\text{ bits} \times 1024\text{ words}$):**
   * ความจุรวม = $64 \times 1024 = 65,536\text{ บิต}$ ($64\text{ Kb}$)
   * หากใช้ LUTRAM: จะต้องใช้ LUTs จำนวนมหาศาลถึง $1,024\text{ ตัว}$ และต้องต่อ MUX F7/F8/F9 เพื่อรวมสายแอดเดรส Routing Delay จะพุ่งสูงจน $F_{max}$ ดิ่งลงต่ำกว่า $150\text{ MHz}$
   * หากใช้ BRAM: ใช้ `RAMB36E2` เพียง **2 บล็อกเท่านั้น** และสามารถทำความเร็วได้สูงเกิน $500\text{ MHz}$ สบายๆ!
ดังนั้น การแบ่งใช้ตามขนาดความจุ (ข้อ ค) จึงเป็นแนวทางมาตรฐานสากลระดับ Senior Architect!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** สิ้นเปลือง Dedicated BRAM โดยเปล่าประโยชน์สำหรับ FIFO ขนาดเล็ก
* **ข้อ ข):** สิ้นเปลือง Logic Fabric อย่างมหาศาล และทำให้เกิด Routing Congestion
* **ข้อ ง):** UltraRAM มีขนาดบล็อกละ 288 Kb และมี Port Width ตายตัวที่ 72 บิต ลึก 4096 คำ การนำมาทำ FIFO ลึก 32 คำเป็นการใช้ทรัพยากรผิดประเภทอย่างยิ่ง

---

### ข้อที่ 3: สภาวะ Simultaneous Read and Write ใน Synchronous FIFO
พิจารณาวงจร Synchronous FIFO ที่มีข้อมูลบรรจุอยู่ภายในจำนวน 10 คำ (`count = 10`) ในรอบสัญญาณนาฬิกาปัจจุบัน สัญญาณควบคุมทั้งสองถูกสั่งทำงานพร้อมกันพอดี:
$$\text{wr\_en} = 1 \quad \text{และ} \quad \text{rd\_en} = 1$$
ข้อใดต่อไปนี้อธิบาย **พฤติกรรมและการเปลี่ยนแปลงของตัวแปรภายใน** ที่ถูกต้องสมบูรณ์แบบที่สุด?

---

#### ตัวเลือก:
* **ก)** วงจรจะเกิดการชนกันของข้อมูล (Collision) ทำให้เกิดสถานะ undefined (`X`)
* **ข)** `wptr` จะเพิ่มขึ้น 1, `rptr` จะเพิ่มขึ้น 1, และ `count` จะยังคงมีค่าเท่ากับ **10 คำเท่าเดิม** โดยที่ข้อมูลใหม่ถูกเขียนลงในตำแหน่ง `mem[wptr]` และข้อมูลเก่าถูกอ่านออกจากตำแหน่ง `mem[rptr]` พร้อมกันได้อย่างราบรื่นใน 1 ไซเคิล
* **ค)** `count` จะเพิ่มขึ้นเป็น 11 ในไซเคิลแรก แล้วลดลงเหลือ 10 ในไซเคิลถัดไป
* **ง)** สัญญาณ `full` และ `empty` จะกระพริบเป็น `1` พร้อมกันชั่วขณะ

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **พฤติกรรมของ Dual-Port SRAM Core:**
   หน่วยความจำแบบ Dual-Port (ไม่ว่าจะเป็น Distributed RAM หรือ Block RAM) มีพอร์ตเขียน (Port A) และพอร์ตอ่าน (Port B) ที่แยกจากกันทั้ง Address Decoder และ Sense Amplifier
   * ในขณะที่ `wr_en = 1` วงจรจะเขียนข้อมูลลงในช่อง `mem[wptr]`
   * ในขณะที่ `rd_en = 1` วงจรจะอ่านข้อมูลออกจากช่อง `mem[rptr]`
   * เนื่องจาก `wptr \ne rptr` (มีข้อมูลค้างอยู่ 10 คำ) พอร์ตทั้งสองจึงเข้าถึงแอดเดรสคนละตำแหน่งกัน จึงไม่มีความขัดแย้งเชิงพื้นที่ (No Memory Contention)
2. **การอัปเดตสถานะ Occupancy Counter:**
   สมการการนับ:
   $$\text{count\_next} = \text{count} + \text{wr\_en} - \text{rd\_en} = 10 + 1 - 1 = 10$$
   ค่าจำนวนข้อมูลใน FIFO จึงยังคงที่อยู่ที่ 10 คำอย่างสมบูรณ์แบบ พอยน์เตอร์ทั้งสองขยับไปข้างหน้าพร้อมกัน 1 ช่อง ทำให้ Throughput ของระบบไหลเวียนได้อย่างต่อเนื่องโดยไม่สะดุด!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** Dual-Port RAM รองรับการอ่านและเขียนพร้อมกันเป็นคุณสมบัติมาตรฐานอยู่แล้ว
* **ข้อ ค):** ใน Synchronous RTL ลอจิกประเมินผลสมการในไซเคิลเดียว ไม่มีการแกว่งขึ้นลงสองสเต็ป
* **ข้อ ง):** เมื่อ `count = 10` ทั้ง `full` (เทียบกับ Depth) และ `empty` (เทียบกับ 0) จะเป็น `0` ทั้งคู่ ไม่มีการกระพริบ
