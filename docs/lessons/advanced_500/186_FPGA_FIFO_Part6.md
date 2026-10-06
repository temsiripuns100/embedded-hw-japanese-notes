# Lesson 186: FPGA FIFO Part 6 - Ultra-Deep FIFOs with External Memory (BRAM-DDR4 Hybrid Architecture, Ping-Pong Page Caching, Burst DMA Controllers & Ring-Buffer Addressing)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์ข้อจำกัดหน่วยความจำภายในชิป (On-Chip Memory Exhaustion Dilemma)
แม้ว่าชิป FPGA ยุคใหม่จะมีหน่วยความจำภายในชิป (Block RAM และ UltraRAM) มากขึ้นอย่างต่อเนื่อง ทว่าความจุรวมก็ยังคงอยู่ในระดับจำกัด เช่น ชิปขนาดกลางมี BRAM รวมเพียง $10 \sim 36\text{ Mb}$ ($1.25 \sim 4.5\text{ MB}$) และแม้กระทั่งชิปขนาดใหญ่อย่าง Virtex UltraScale+ ก็มีพื้นที่ UltraRAM สูงสุดไม่เกิน $500\text{ Mb}$ ($\approx 60\text{ MB}$)

ทว่า ในแอปพลิเคชันระดับภารกิจสำคัญ (Mission-Critical Applications):
* **เครื่องบันทึกคลื่นสัญญาณออสซิลโลสโคปความเร็วสูง (High-End DSO):** ต้องการบันทึกสัญญาณสุ่มที่ความเร็ว $10\text{ GSa/s}$ ต่อเนื่องนานหลายวินาที ($Depth \ge 4\text{ GB}$)
* **ระบบกล้องอุตสาหกรรมและภาพยนตร์ 8K Raw:** สตรีมวิดีโอ 8K 60fps มีอัตราข้อมูลสูงกว่า $48\text{ Gbps}$ ต้องการเก็บบัฟเฟอร์ข้ามเฟรมหลายกิกะไบต์
* **ระบบบันทึกสัญญาณเรดาร์ความยาวนาน (Radar Long-Duration Capture):** ต้องดักจับสัญญาณคลื่นสะท้อนความยาวหลายนาทีเพื่อวิเคราะห์สัญญาณกวน

การพยายามใช้เฉพาะ BRAM ภายในชิปจะทำให้ **ทรัพยากร BRAM หมดเกลี้ยง $100\%$** ในทันที ทางเลือกเดียวที่เป็นไปได้ในทางวิศวกรรมคือ **สถาปัตยกรรมลูกผสมระหว่าง On-Chip BRAM และหน่วยความจำภายนอก (BRAM-DDR4 / LPDDR4 Hybrid FIFO)**:

```
                  สถาปัตยกรรม 3 ชั้นของ BRAM-DDR4 HYBRID FIFO
                  
    [ LAYER 1: INGRESS CACHE ]         [ LAYER 2: MAIN STORAGE ]         [ LAYER 3: EGRESS CACHE ]
    (On-chip Dual-Port BRAM)           (External DDR4/LPDDR4 SDRAM)       (On-chip Dual-Port BRAM)
    
       din (Continuous Stream)                                               dout (Continuous Stream)
          │                                                                     ▲
          ▼                                                                     │
    ┌───────────┐    AXI-MM Burst Write   ┌───────────────────┐    AXI-MM Burst Read┌───────────┐
    │  INGRESS  ├────────────────────────►│   EXTERNAL DDR4   ├────────────────────►│  EGRESS   │
    │ BRAM FIFO │                         │  CIRCULAR BUFFER  │                     │ BRAM FIFO │
    └───────────┘                         │   (1GB - 32GB)    │                     └───────────┘
    (ดูดซับ Burst &                       └───────────────────┘                     (กักเก็บข้อมูลล่วงหน้า
     สะสมให้ครบก้อน AXI)                   ▲ AXI4 Memory Map                        ลด Latency ของ DDR4)
                                           │
                                  ┌────────┴────────┐
                                  │ HARD DDR4 MC IP │
                                  │ (MIG / NoC)     │
                                  └─────────────────┘
```

---

### 1.2 ฟิสิกส์ของความล่าช้าในหน่วยความจำ DDR4 SDRAM (DDR4 Latency Physics)

ทำไมเราจึงไม่สามารถต่อสตรีมข้อมูลเข้ากับ DDR4 Controller ตรงๆ ได้โดยไม่ต้องมี Ingress/Egress BRAM Cache?

#### ข้อจำกัดพื้นฐาน 3 ประการของ DDR4 SDRAM:
1. **ความหน่วงเวลาเริ่มต้นสูง (High Access Latency):**
   การเปิดใช้งานแถวข้อมูล (Row Activation) ในชิป DRAM ต้องใช้เวลาตามค่าพารามิเตอร์ทางกายภาพ $t_{RCD}$ (RAS-to-CAS Delay $\approx 14\text{ ns}$), $t_{CL}$ (CAS Latency $\approx 14\text{ ns}$), และ $t_{RP}$ (Precharge Time $\approx 14\text{ ns}$) ทำให้การอ่าน/เขียนคำแรกต้องใช้เวลาหน่วงสะสมไม่น้อยกว่า **$40 \sim 60\text{ นาโนวินาที}$**!
2. **การถ่ายโอนข้อมูลต้องทำเป็นก้อนใหญ่ (Burst-Oriented Efficiency):**
   เพื่อให้ได้แบนด์วิดท์สูงสุดตามสเปกของ DDR4 ($> 19.2\text{ GB/s}$ บน DDR4-2400) การเข้าถึงจะต้องทำผ่านคำสั่ง AXI4 Burst ขนาดความยาว **$64 \sim 256\text{ Beats}$** ติดต่อกัน การเขียน/อ่านทีละคำเดี่ยวๆ จะทำให้ประสิทธิภาพการใช้บัส (Bus Efficiency) ดิ่งลงเหลือไม่ถึง **$5\%$**!
3. **การถูกขัดจังหวะด้วยรอบรีเฟรช (Periodic Refresh Interruption - $t_{REFI}$ & $t_{RFC}$):**
   เซลล์ตัวเก็บประจุในชิป DRAM สูญเสียประจุไฟฟ้าตลอดเวลา คอนโทรลเลอร์จึงต้องสั่งหยุดการทำงานเพื่อทำ Auto-Refresh ทุกๆ **$7.8\text{ ไมโครวินาที}$ ($t_{REFI}$)** โดยในระหว่างที่รีเฟรชกินเวลา **$350\text{ นาโนวินาที}$ ($t_{RFC}$)** DDR4 จะไม่สามารถรับคำสั่งเขียนหรืออ่านใดๆ ได้เลยแม้แต่คำสั่งเดียว!

---

### 1.3 กลไก Ping-Pong Page Buffering & Ingress Sizing Math

เพื่อซ่อนความหน่วงเวลาของรอบรีเฟรช ($t_{RFC}$) และจัดเตรียมข้อมูลให้ครบขนาดก้อน AXI Burst **Ingress BRAM FIFO** จะต้องมีขนาดความจุใหญ่เพียงพอที่จะรองรับข้อมูลที่ไหลเข้ามาอย่างต่อเนื่องในระหว่างที่ DDR4 ถูกล็อคการทำงาน:

```
               สถาปัตยกรรม PING-PONG PAGE BUFFER ใน INGRESS CACHE
               
    Continuous Stream In ═══════════════════════════════════════════╗
                                                                    ▼
                                                              ┌───────────┐
                                                    Page Sel ─┤ 1       M │
                                                    (สลับหน้า)│   DEMUX X ├─────┐
                                                              │ 0       U │     │
                                                              └───────────┘     │
                                                                │               │
                                                                ▼               ▼
                                                          ┌───────────┐   ┌───────────┐
                                                          │  PAGE A   │   │  PAGE B   │
                                                          │ (512 คำ)  │   │ (512 คำ)  │
                                                          └─────┬─────┘   └─────┬─────┘
                                                                │               │
                                                                └───────┬───────┘
                                                                        ▼
                                                          AXI4 Burst Write to DDR4
                                                          (ยิงออกเต็มความเร็วเมื่อหน้าใดหน้าหนึ่งเต็ม!)
```

#### สูตรการคำนวณขนาด Ingress Cache ขั้นต่ำ ($Size_{ingress\_min}$):
$$Size_{ingress\_min} \ge \left( \frac{t_{RFC} + t_{arbitration} + t_{page\_miss}}{T_{stream\_in}} \right) + Burst\_Size_{AXI}$$

สมมติว่าสตรีมข้อมูลไหลเข้าที่ความถี่ $250\text{ MHz}$ ($T_{stream} = 4.0\text{ ns}$):
* ระยะเวลารีเฟรชของ DDR4: $t_{RFC} = 350\text{ ns}$
* เวลาหน่วงในการแย่งบัสและการสลับคิว (Arbitration): $t_{arbitration} = 150\text{ ns}$
* ขนาดของ 1 AXI Burst: $Burst\_Size_{AXI} = 256\text{ คำ}$

$$N_{lockout\_words} = \frac{350\text{ ns} + 150\text{ ns}}{4.0\text{ ns}} = \frac{500\text{ ns}}{4.0\text{ ns}} = 125\text{ คำ}$$
$$Size_{ingress\_min} = 125 + 256 = 381\text{ คำ} \implies \text{ปัดขึ้นเป็น } \mathbf{512\text{ คำ (หรือ Ping-Pong หน้าละ 256 คำ)}}$$

หาก Ingress BRAM มีขนาดเล็กกว่า 381 คำ ในจังหวะที่ DDR4 เข้าสู่รอบ Auto-Refresh บัฟเฟอร์หน้าชิปจะเต็มและเกิด **Write Overflow พังทลายทันที!**

---

### 1.4 การจัดการแอดเดรสวงแหวนบนหน่วยความจำภายนอก (DDR4 Ring Addressing)

บนพื้นที่หน่วยความจำภายนอก (เช่น จัดสรรไว้ขนาด $4\text{ GB}$ ตั้งแต่แอดเดรส `0x8000_0000` ถึง `0xFFFF_FFFF`):
เอนจิน DMA จะต้องสร้างพอยน์เตอร์เขียน (`ddr_waddr`) และพอยน์เตอร์อ่าน (`ddr_raddr`) ทำงานในลักษณะ Circular Ring:

```
                 การหมุนวนแอดเดรสบน DDR4 CIRCULAR BUFFER
                 
       DDR_BASE_ADDR (0x8000_0000) ┌───────────────────────────┐
                                   │                           │
                                   │     OCCUPIED DATA         │
                                   │    (รอคอยการอ่านออก)      │
                                   │                           │
       ddr_waddr                   ├───────────────────────────┤ ◄── DMA Write Burst
                                   │                           │
                                   │     FREE SPACE            │
                                   │    (พื้นที่ว่างสำหรับเขียน)│
                                   │                           │
       ddr_raddr                   ├───────────────────────────┤ ◄── DMA Read Burst
                                   │                           │
       DDR_HIGH_ADDR (0xFFFF_FFFF) └───────────────────────────┘
                                   │ (Wrap-around กลับไป Base!)
```

#### เงื่อนไขการคำนวณสถานะ External Full และ Empty:
* **Empty Condition:** เมื่อ `ddr_waddr == ddr_raddr` และ Ingress/Egress Caches ว่างเปล่า
* **Full Condition:** เมื่อพอยน์เตอร์เขียนวิ่งวนรอบมาไล่กวดพอยน์เตอร์อ่านจนเหลือระยะห่างน้อยกว่าขนาดของ $1\text{ AXI Burst}$ ($256 \times Byte\_Width$)

---

### 1.5 โค้ดแม่แบบภาษา Verilog สำหรับ Hybrid BRAM-DDR4 FIFO Controller Interface

```verilog
// ==============================================================================
// HYBRID BRAM-DDR4 ULTRA-DEEP FIFO CONTROLLER (STREAM TO AXI4-MM DMA BRIDGE)
// Senior Gold Standard: Refresh-Resilient Ingress Ping-Pong & Circular DMA Math
// ==============================================================================
(* keep_hierarchy = "yes" *)
module hybrid_ddr_fifo_controller #(
    parameter integer DATA_WIDTH     = 64,
    parameter integer AXI_ADDR_WIDTH = 32,
    parameter integer BURST_LEN      = 256,         // 256 beats per AXI burst
    parameter [31:0]  DDR_BASE_ADDR  = 32'h80000000,
    parameter [31:0]  DDR_HIGH_ADDR  = 32'hFFFF0000
)(
    input  wire                      clk,
    input  wire                      rst_n,

    // Ingress Stream Interface (From High-Speed Sensor/ADC)
    input  wire                      stream_in_valid,
    input  wire [DATA_WIDTH-1:0]     stream_in_data,
    output wire                      stream_in_ready,

    // Egress Stream Interface (To Downstream Consumer)
    output wire                      stream_out_valid,
    output wire [DATA_WIDTH-1:0]     stream_out_data,
    input  wire                      stream_out_ready,

    // AXI4 Master Write Channel (To DDR4 Memory Controller)
    output reg  [AXI_ADDR_WIDTH-1:0] m_axi_awaddr,
    output reg  [7:0]                m_axi_awlen,
    output reg                       m_axi_awvalid,
    input  wire                      m_axi_awready,
    output wire [DATA_WIDTH-1:0]     m_axi_wdata,
    output wire                      m_axi_wlast,
    output wire                      m_axi_wvalid,
    input  wire                      m_axi_wready,
    input  wire                      m_axi_bvalid,
    output wire                      m_axi_bready,

    // Status Flags
    output wire                      fifo_full_alarm,
    output wire                      fifo_empty_alarm
);

    localparam integer BURST_BYTES = BURST_LEN * (DATA_WIDTH / 8);

    // -------------------------------------------------------------------------
    // 1. Ingress BRAM FIFO (Absorbs DDR4 Latency & Auto-Refresh Lockout)
    // -------------------------------------------------------------------------
    wire [10:0] ingress_count;
    wire        ingress_full;
    wire        ingress_empty;
    wire        ingress_rd_en;
    wire [DATA_WIDTH-1:0] ingress_dout;

    // Instance of Sync FIFO from Lesson 181 with FWFT mode
    sync_fifo #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(10),            // Depth = 1024 words (Well above 381-word bound!)
        .FWFT_MODE(1)
    ) ingress_bram_inst (
        .clk(clk),
        .rst_n(rst_n),
        .wr_en(stream_in_valid && stream_in_ready),
        .din(stream_in_data),
        .full(ingress_full),
        .almost_full(),
        .rd_en(ingress_rd_en),
        .dout(ingress_dout),
        .empty(ingress_empty),
        .almost_empty(),
        .data_count(ingress_count)
    );

    assign stream_in_ready = !ingress_full;

    // -------------------------------------------------------------------------
    // 2. AXI4 DMA Write Burst FSM
    // -------------------------------------------------------------------------
    localparam [1:0] S_DMA_IDLE  = 2'b00,
                     S_DMA_ADDR  = 2'b01,
                     S_DMA_DATA  = 2'b10,
                     S_DMA_RESP  = 2'b11;

    reg [1:0]  dma_state;
    reg [8:0]  burst_cnt;
    reg [31:0] ddr_wptr;
    reg [31:0] ddr_rptr;

    // Trigger AXI Write Burst when Ingress FIFO has at least BURST_LEN words!
    wire start_write_burst = (ingress_count >= BURST_LEN) && (dma_state == S_DMA_IDLE);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dma_state     <= S_DMA_IDLE;
            m_axi_awvalid <= 1'b0;
            m_axi_awaddr  <= DDR_BASE_ADDR;
            m_axi_awlen   <= BURST_LEN - 1;
            burst_cnt     <= 9'd0;
            ddr_wptr      <= DDR_BASE_ADDR;
            ddr_rptr      <= DDR_BASE_ADDR;
        end else begin
            case (dma_state)
                S_DMA_IDLE: begin
                    if (start_write_burst) begin
                        m_axi_awaddr  <= ddr_wptr;
                        m_axi_awvalid <= 1'b1;
                        dma_state     <= S_DMA_ADDR;
                    end
                end

                S_DMA_ADDR: begin
                    if (m_axi_awready && m_axi_awvalid) begin
                        m_axi_awvalid <= 1'b0;
                        burst_cnt     <= 9'd0;
                        dma_state     <= S_DMA_DATA;
                    end
                end

                S_DMA_DATA: begin
                    if (m_axi_wready && m_axi_wvalid) begin
                        if (burst_cnt == BURST_LEN - 1) begin
                            dma_state <= S_DMA_RESP;
                        end else begin
                            burst_cnt <= burst_cnt + 1'b1;
                        end
                    end
                end

                S_DMA_RESP: begin
                    if (m_axi_bvalid && m_axi_bready) begin
                        // Advance DDR Write Pointer with Circular Wrap-Around
                        if (ddr_wptr >= DDR_HIGH_ADDR - BURST_BYTES)
                            ddr_wptr <= DDR_BASE_ADDR;
                        else
                            ddr_wptr <= ddr_wptr + BURST_BYTES;

                        dma_state <= S_DMA_IDLE;
                    end
                end

                default: dma_state <= S_DMA_IDLE;
            endcase
        end
    end

    assign ingress_rd_en = (dma_state == S_DMA_DATA) && m_axi_wready;
    assign m_axi_wdata   = ingress_dout;
    assign m_axi_wvalid  = (dma_state == S_DMA_DATA) && !ingress_empty;
    assign m_axi_wlast   = (burst_cnt == BURST_LEN - 1);
    assign m_axi_bready  = 1'b1;

    // Status alarms
    assign fifo_empty_alarm = (ddr_wptr == ddr_rptr) && ingress_empty;
    assign fifo_full_alarm  = ingress_full;

endmodule
```

---

### 1.6 SystemVerilog Assertions (SVA) เพื่อตรวจจับ Data Loss ระหว่าง DDR Refresh

```systemverilog
// SVA Verification Checker สำหรับ Hybrid BRAM-DDR4 FIFO
module hybrid_fifo_sva (
    input wire clk,
    input wire rst_n,
    input wire stream_in_valid,
    input wire stream_in_ready,
    input wire ingress_full
);

    // Property 1: Ingress Buffer Must Never Assert Hard Full during Stream In
    // An assertion of ingress_full while stream_in_valid is high indicates
    // that the BRAM cache was too small to hide the DDR4 Refresh/Arbitration latency!
    property p_no_ingress_overflow;
        @(posedge clk) disable iff (!rst_n)
        stream_in_valid |-> !ingress_full;
    endproperty
    assert_no_overflow: assert property (p_no_ingress_overflow)
        else $error("[FATAL_HYBRID_OVERFLOW]: Ingress BRAM overflowed during DDR4 lockout!");

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】เครื่องดิจิทัลสตอเรจออสซิลโลสโคปความเร็วสูง (High-End 10GSa/s DSO)
เกิดจุดข้อมูลรูปคลื่นขาดหายเป็นเส้นประ (Periodic Waveform Gaps / Blind Spots)
ทุกๆ 7.8 ไมโครวินาที จากการคำนวณ Ingress BRAM ไม่ครอบคลุมรอบ DDR4 Auto-Refresh
================================================================================
```

#### บริบทของระบบ (System Context):
บริษัทเครื่องมือวัดทางอิเล็กทรอนิกส์ชั้นนำ พัฒนาเครื่องดิจิทัลออสซิลโลสโคปความเร็วสูง (High-Bandwidth Digital Storage Oscilloscope) บน FPGA Xilinx UltraScale+ (`xcku060`):
* ภาคสุ่มสัญญาณ ADC แปลงสัญญาณความถี่สูงส่งข้อมูลเข้าชิปความเร็ว $2.5\text{ GWords/s}$ (บัสข้อมูล 64 บิต ความถี่ $312.5\text{ MHz}$)
* โหมด Deep Memory Capture จัดสรรพื้นที่บันทึกบนชิปหน่วยความจำภายนอก DDR4-2400 ขนาด $8\text{ GB}$
* ระหว่าง ADC และ DDR4 DMA Controller มีบัฟเฟอร์ Ingress BRAM FIFO ความจุ $Depth = 128\text{ คำ}$
* วิศวกรคำนวณว่า 1 AXI Burst มีขนาด 64 คำ ดังนั้นขนาดบัฟเฟอร์ 128 คำ (สามารถจุได้ถึง 2 Bursts) ก็น่าจะเพียงพออย่างเหลือเฟือสำหรับการเขียน

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
เมื่อเปิดโหมดบันทึกคลื่นสัญญาณระยะยาว (Long-Time Trigger Capture) เพื่อจับสัญญาณความผิดปกติของบัส PCIe: รูปคลื่นสัญญาณแอนะล็อกที่แสดงผลบนหน้าจอเกิดอาการ **"มีรูโหว่ของข้อมูลขาดหายไปเป็นจังหวะ (Periodic Waveform Blind Holes)"** ทุกๆ ประมาณ $7.8\text{ ไมโครวินาที}$ ส่งผลให้วิศวกรที่นำเครื่องมือไปใช้งานไม่สามารถจับความผิดปกติของ Glitch สัญญาณได้ ลูกค้าห้องปฏิบัติการปฏิเสธการตรวจรับสินค้าและส่งคืนเครื่องทั้งล็อต!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมรูปคลื่นบนจอออสซิลโลสโคปจึงขาดหายไปเป็นรูโหว่ทุกๆ 7.8 ไมโครวินาที?**
   * *เพราะจุดข้อมูลสัญญาณสุ่มของ ADC จำนวนประมาณ 110 คำสูญหายไปเป็นช่วงๆ ในระหว่างการบันทึก*
2. **ทำไมข้อมูล ADC จึงสูญหายไปเป็นช่วงๆ ทุก 7.8 ไมโครวินาที?**
   * *เพราะ Ingress BRAM FIFO เกิดสภาวะ Overflow (เต็มพิกัดและล้นทะลัก) ทุกๆ 7.8 ไมโครวินาที*
3. **ทำไม Ingress FIFO จึงล้นทะลักตามคาบเวลา 7.8 ไมโครวินาทีพอดี?**
   * *เพราะ $7.8\mu s$ คือคาบเวลามาตรฐานของการทำ **Auto-Refresh ($t_{REFI}$)** ของชิป DDR4 SDRAM*
4. **ทำไมรอบ Auto-Refresh ของ DDR4 จึงทำให้ Ingress FIFO ล้นทะลัก?**
   * *เพราะในระหว่างที่ DDR4 กำลังทำ Refresh คอนโทรลเลอร์จะระงับการเขียนเป็นเวลา $t_{RFC} = 350\text{ ns}$ บวกกับเวลา Re-arbitration อีก $100\text{ ns}$ รวมเป็นเวลาล็อคยาวนานถึง $450\text{ ns}$*
5. **ทำไมบัฟเฟอร์ขนาด 128 คำจึงทนทานต่อช่วงเวลารีเฟรช 450 ns ไม่ได้?**
   * *เพราะที่ความถี่ $312.5\text{ MHz}$ ($T = 3.2\text{ ns}$) ในช่วงเวลา 450 ns จะมีข้อมูลจาก ADC ไหลทะลักเข้ามาอย่างต่อเนื่องถึง:
     $$N_{incoming} = \frac{450\text{ ns}}{3.2\text{ ns}} \approx 141\text{ คำ!}$$
     ซึ่งเกินกว่าความจุของ Ingress BRAM (128 คำ) อย่างสิ้นเชิง ข้อมูลส่วนเกินจึงล้นทะลักทิ้งไปทั้งหมด!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                         สาเหตุของความล้มเหลว: DSO WAVEFORM BLIND HOLES
                         
   METHOD (การคำนวณขนาด Ingress BRAM)          MACHINE (ฟิสิกส์ของชิป DDR4 SDRAM)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ตั้งขนาดไว้เพียง 128 คำ        │          │ Auto-Refresh t_REFI = 7.8us    │
   │ ละเลยค่า Refresh Recovery t_RFC│          │ Lockout Duration ยาวนาน 450ns  │
   │ คิดเฉพาะขนาด AXI Burst         │          │ อัตราสตรีมสูงถึง 3.2ns ต่อคำ   │
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ Testbench ปิดโหมด Refresh DDR  │          │ การทดสอบรันสั้นไม่ถึง 7.8us    │
   │ ขาด SVA ตรวจจับ Overflow Risk  │          │ ไม่ได้จับตาดูขา FIFO Full Alarm│
   │ ละเลยคู่มือ Micron DDR4 Spec   │          │ ปล่อยผ่านเพราะเห็นว่าเขียนผ่าน │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (ข้อกำหนดและการตรวจสอบ)             MEASUREMENT (สภาวะการจำลองระบบ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediations):
1. **คำนวณและขยายขนาด Ingress BRAM FIFO:**
   * คำนวณความจุขั้นต่ำเพื่อดูดซับช่วงรีเฟรช:
     $$N_{min} = \frac{450\text{ ns}}{3.2\text{ ns}} + Burst\_Size (64) + Guard (32) = 141 + 64 + 32 = 237\text{ คำ}$$
   * ขยายขนาด Ingress BRAM FIFO จาก $128\text{ คำ}$ ขึ้นเป็น **$512\text{ คำ}$** (ใช้ `RAMB36E2` เพียง 1 ก้อน) เพื่อให้มีมาร์จินดูดซับข้อมูลได้นานถึง $1,638\text{ ns}$ (นานกว่ารอบรีเฟรชถึง 3 เท่า!)
2. **เปิดการจำลอง Auto-Refresh ใน Testbench:** แก้ไขแบบจำลอง DDR4 Simulation Model (Micron Verification IP) ให้เปิดใช้งานวงจร Auto-Refresh เสมือนจริง $100\%$
3. **ติดตั้งวงจร SVA Monitoring:** บังคับให้ Testbench ตรวจสอบว่าสัญญาณ `ingress_full` ต้องมีค่าเป็น `0` ตลอดการจำลองการบันทึกคลื่นสัญญาณ $100,000$ ไซเคิล

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Hybrid External Memory FIFO (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | ขนาด Ingress Cache ได้คำนวณครอบคลุมรอบ DDR Refresh ($t_{RFC}$) หรือไม่? | $Size \ge Lockout\_Words + Burst$ | [ ] ผ่าน |
| 2 | มีการเปิดจำลองรอบ Auto-Refresh ในแบบจำลอง DDR Simulation Model? | Enabled in Testbench VIP | [ ] ผ่าน |
| 3 | การเข้าถึง DDR4 ทำผ่าน AXI Burst ขนาดใหญ่ ($\ge 64$ หรือ $256$ beats)? | High Bus Efficiency | [ ] ผ่าน |
| 4 | มีการจัดการ Circular Address Wrap-Around บน DDR4 ครบถ้วน? | Verified Ring Boundary | [ ] ผ่าน |
| 5 | ขนาด Egress Cache ใหญ่เพียงพอป้องกัน Underflow ขณะรอคอยคำสั่งอ่าน? | Verified Pre-fetch Depth | [ ] ผ่าน |
| 6 | มีการเขียน SVA ยืนยันว่าไม่มีการเกิด Ingress Overflow ในระหว่างรันจริง? | Formal Property Passed | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | 外部メモリ結合超大容量FIFO | がいぶメモリけつごうちょうおおようりょうFIFO | Gaibu memori ketsugō chō-ōyōryō Faifo | External Memory Ultra-Deep FIFO |
| 2 | ピンポン・ページバッファ | ピンポン・ページバッファ | Pimpon pēji baffa | Ping-Pong Page Buffer |
| 3 | オートリフレッシュ遮断 | オートリフレッシュしゃだん | Ōto rifuresshu shadan | Auto-Refresh Lockout ($t_{RFC}$) |
| 4 | リフレッシュ隠蔽 | リフレッシュいんぺい | Rifuresshu impei | Refresh Latency Hiding |
| 5 | バーストDMA転送 | バーストDMAてんそう | Bāsuto Dī-Emu-Ē tensō | Burst DMA Transfer |
| 6 | リングバッファ循環番地 | リングバッファじゅんかんばんち | Ringu baffa junkan banchi | Ring-Buffer Circular Addressing |
| 7 | 波形欠落 / 盲点 | はけいけつらく / もうてん | Hakei ketsuraku / Mōten | Waveform Holes / Blind Gaps |
| 8 | バス調停待ち時間 | バスちょうていまちじかん | Basu chōtei machi jikan | Bus Arbitration Wait Time |
| 9 | キャッシュ枯渇 | キャッシュこかつ | Kyasshu kokatsu | Cache Starvation / Underflow |
| 10 | 占有率マージン | せんゆうりつマージン | Sen'yūritsu mājin | Occupancy Safety Margin |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ห้องประชุมออกแบบเครื่องมือวัดความเร็วสูง (High-Speed Test & Measurement Review Room), เมืองฮามามัตสึ (Hamamatsu)  
**ผู้เข้าร่วม:**
* **อุเอดะซัง (Ueda-san):** หัวหน้าผู้เชี่ยวชาญด้านการออกแบบเครื่องมือวัดอิเล็กทรอนิกส์ (Principal Instrumentation Fellow / 技師長)
* **ชวัลกร (Chawankorn):** วิศวกรออกแบบระบบจัดเก็บข้อมูลความเร็วสูง (DSO Acquisition FPGA Engineer)

---

**上田技師長 (Ueda):**  
「チャワンコーン君、このオシロスコープ用大容量捕捉メモリ（DDR4ハイブリッドFIFO）の設計書だが、実機で7.8マイクロ秒周期で波形データが部分的に抜け落ちる欠陥が報告されている。RTLを見ると、ADCとDDR4 DMAコントローラの間に配置したIngress BRAMバッファの深度がわずか128ワードしかないね。クロックは312.5MHz（1ワードあたり3.2ns）だ。なぜ128ワードで足りると判断したのかね？」  
*(Chawankōn-kun, kono oshirosukōpu-yō daiyōryō hosoku memori (DDR4 haiburiddo FIFO) no sekkeisho daga, jikki de 7.8 maikuro-byō shūki de hakei dēta ga bubunteki ni nukeochiru kekkan ga hōkoku sarete iru. RTL wo miru to, ADC to DDR4 DMA kontorōra no aida ni haichi shita Ingress BRAM baffa no shindo ga wazuka 128-wādo shika nai ne. Kurokku wa 312.5MHz (1-wādo atari 3.2ns) da. Naze 128-wādo de tariru to handan shita no kane?)*  
**คำแปล:** คุณชวัลกร ในเอกสารออกแบบหน่วยความจำบันทึกคลื่นสัญญาณขนาดใหญ่ของออสซิลโลสโคป (DDR4 Hybrid FIFO) ตัวนี้ ในเครื่องจริงมีรายงานข้อบกพร่องว่าข้อมูลรูปคลื่นขาดหายไปเป็นรูโหว่ทุกๆ 7.8 ไมโครวินาทีนะ พอเปิดดูโค้ด RTL คุณวางบัฟเฟอร์ Ingress BRAM คั่นระหว่าง ADC กับ DDR4 DMA ไว้ด้วยขนาดความลึกเพียงแค่ 128 คำเท่านั้น สัญญาณนาฬิกาคือ 312.5 MHz (3.2 ns ต่อคำ) ทำไมถึงตัดสินใจว่า 128 คำมันเพียงพอล่ะครับ?

**チャワンコーン (Chawankorn):**  
「上田技師長、DDR4へのAXIバースト長を64ワードに設定していたため、128ワードあればバースト2回分の容量を保持できます。1回目のバーストを書き込んでいる間に次のバーストを蓄積できるPing-Pong動作が可能であるため、128ワードで十分に連続ストリームを維持できると計算いたしました。」  
*(Ueda-gishichō, DDR4 e no AXI bāsuto-chō wo 64-wādo ni settei shite ita tame, 128-wādo areba bāsuto 2-kai-bun no yōryō wo hoji dekimasu. 1-kai-me no bāsuto wo kakikonde iru aida ni tsugi no bāsuto wo chikuseki dekiru Pimpon dōsa ga kanō de aru tame, 128-wādo de jūbun ni renzoku sutorīmu wo iji dekiru to keisan itashimashita.)*  
**คำแปล:** หัวหน้าอุเอดะครับ เนื่องจากเราตั้งขนาด AXI Burst ไปยัง DDR4 ไว้ที่ 64 คำ ดังนั้นขนาด 128 คำจึงสามารถเก็บข้อมูลได้ถึง 2 Bursts ในขณะที่กำลังเขียน Burst แรก เราก็สามารถสะสม Burst ถัดไปแบบ Ping-Pong สลับกันได้ ผมจึงคำนวณว่า 128 คำเพียงพอที่จะรองรับสตรีมต่อเนื่องได้ครับ

**上田技師長 (Ueda):**  
「DDR4の物理仕様である**『オートリフレッシュ（Auto-Refresh）』**を完全に忘れているじゃないか！DDR4は7.8マイクロ秒ごとにリフレッシュを実行する。リフレッシュ要求が発生すると、コントローラは書き込みを中断し、メモリセルを再充電するために最低でも`t_RFC = 350ns`、バス調停を含めれば約`450ns`もの間、一切のアクセスを完全に遮断（Lockout）するんだ！3.2nsごとにデータが怒涛のように押し寄せてくるのに、450nsの間待たされたら何ワード溜まる？**140ワード以上溜まるんだよ！** 128ワードのバッファなど一瞬で溢れてデータがドロップするに決まっているだろう！」  
*(DDR4 no butsuri shiyō de aru "Ōto Rifuresshu" wo kanzen ni wasurete iru ja nai ka! DDR4 wa 7.8 maikuro-byō goto ni rifuresshu wo jikkō suru. Rifuresshu yōkyū ga hassei suru to, kontorōra wa kakikomi wo chūdan shi, memori seru wo sai-jūden suru tame ni saitei demo t_RFC = 350ns, basu chōtei wo fukumereba yaku 450ns mono aida, issai no akusesu wo kanzen ni shadan suru n da! 3.2ns goto ni dēta ga dotō no yō ni oshiyosete kuru noni, 450ns no aida matasaretara nan-wādo tamaru? 140-wādo ijō tamaru n da yo! 128-wādo no baffa nado isshun de afurete dēta ga doroppu suru ni kimatte iru darō!)*  
**คำแปล:** นี่คุณลืมสเปกทางกายภาพของ DDR4 เรื่อง **"Auto-Refresh"** ไปหมดแล้วหรือยังไง! ชิป DDR4 มันต้องทำ Auto-Refresh ทุกๆ 7.8 ไมโครวินาทีนะ เมื่อมีคำสั่งรีเฟรช คอนโทรลเลอร์จะสั่งระงับการเขียน และเพื่อชาร์จประจุเซลล์หน่วยความจำ มันจะตัดการเข้าถึงทั้งหมดโดยสิ้นเชิงนานอย่างน้อย `t_RFC = 350 ns` ถ้ารวมการแย่งบัสก็ปาเข้าไปเกือบ `450 ns`! ข้อมูลไหลทะลักเข้ามาทุกๆ 3.2 ns แต่ต้องถูกสั่งให้รอนานถึง 450 ns ข้อมูลมันจะสะสมขึ้นมากี่คำ? **มันสะสมมากกว่า 140 คำเชียวนะ!** บัฟเฟอร์ขนาดแค่ 128 คำ มันก็ต้องล้นทะลักจนข้อมูลสูญหายในพริบตาอยู่แล้ว!

**チャワンコーン (Chawankorn):**  
「ハッ……！DDR4の定期リフレッシュによるアクセス遮断時間のことを完全に見落としておりました……！128ワードでは、リフレッシュ1回で確実に溢れてしまいます……！」  
*(Ha'... DDR4 no teiki rifuresshu ni yoru akusesu shadan jikan no koto wo kanzen ni miotoshite orimashita...! 128-wādo dewa, rifuresshu 1-kai de kakujitsu ni afurete shimaimasu...!)*  
**คำแปล:** อึก...! ผมมองข้ามเวลาที่การเข้าถึงถูกตัดขาดจากรอบการรีเฟรชประจำรอบของ DDR4 ไปอย่างสิ้นเชิงเลยครับ...! ขนาด 128 คำ มันต้องล้นทะลักแน่นอนในทุกๆ ครั้งที่มีการรีเฟรชครับ...!

**上田技師長 (Ueda):**  
「オシロスコープにとって波形の欠落は致命傷だ。信頼性を失ったら測定器としての存在価値がなくなる。直ちにIngress BRAMバッファを**深度512ワード**へ拡張しなさい。512ワードあれば、450nsのリフレッシュ遮断を余裕で隠蔽（Hide）できる。さらにシミュレーション環境でDDR4のリフレッシュ動作を有効化し、10万サイクル連続書き込みでオーバーフローが絶対に起きないことをSVAで実証してレポートを提出しなさい！」  
*(Oshirosukōpu ni totte hakei no ketsuraku wa chimeishō da. Shinraisei wo ushinattara sokuteiki to shite no sonzai kachi ga nakunaru. Tadachini Ingress BRAM baffa wo shindo 512-wādo e kakuchō shinasai. 512-wādo areba, 450ns no rifuresshu shadan wo yoyū de impei dekiru. Sarani shimyurēshon kankyō de DDR4 no rifuresshu dōsa wo yūkōka shi, 10-man saikuru renzoku kakikomi de ōbāfurō ga zettai ni okinai koto wo SVA de jisshō shite repōto wo teishutsu shinasai!)*  
**คำแปล:** สำหรับออสซิลโลสโคป การที่รูปคลื่นขาดหายไปถือเป็นบาดแผลฉกรรจ์ที่ร้ายแรงที่สุด หากสูญเสียความน่าเชื่อถือ มันก็หมดคุณค่าในการเป็นเครื่องมือวัดทันที จงรีบขยาย Ingress BRAM บัฟเฟอร์เป็น **ความลึก 512 คำ** เดี๋ยวนี้เลย ถ้ามี 512 คำ เราจะสามารถซ่อนระยะเวลารีเฟรช 450 ns ได้อย่างสบายๆ และจงเปิดใช้งานรอบรีเฟรชในระบบจำลอง Simulation พร้อมพิสูจน์ด้วย SVA ว่าไม่มี Overflow เกิดขึ้นอย่างแน่นอนในการเขียนต่อเนื่อง 100,000 ไซเคิล แล้วค่อยนำรายงานมาส่งผม!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณขนาด Ingress BRAM Cache ขั้นต่ำเพื่อซ่อนรอบ DDR4 Auto-Refresh
ในระบบบันทึกภาพถ่ายดาวเทียมความเร็วสูง สตรีมข้อมูลจากเซนเซอร์กล้องไหลเข้าสู่ FPGA แบบต่อเนื่องไม่หยุดยั้งด้วยอัตราความเร็ว $f_{stream} = 200\text{ MHz}$ ($1\text{ Word (64-bit)}$ ต่อ $1\text{ ไซเคิล}$, คาบเวลา $T_{stream} = 5.0\text{ ns}$):
* ข้อมูลต้องถูกส่งต่อไปบันทึกลงหน่วยความจำ DDR4 SDRAM ผ่าน AXI4 DMA Master Interface
* การถ่ายโอน AXI Write Burst มีขนาดตายตัว $Burst\_Len = 128\text{ beats}$ ($128\text{ คำ}$)
* ชิป DDR4 มีค่ารอบการรีเฟรช $t_{RFC} = 350.0\text{ ns}$
* เวลาหน่วงในการจัดคิวและสลับคำสั่งของ DDR4 Memory Controller: $t_{arbitration} = 150.0\text{ ns}$
* ความล่าช้าในกรณีเกิด Page Miss (Precharge + Activate): $t_{page\_miss} = 40.0\text{ ns}$
* ข้อกำหนดความปลอดภัยตามมาตรฐาน DO-254 กำหนดให้บวก Safety Guard Band: $N_{guard} = 32\text{ คำ}$

จงคำนวณหาค่า **เวลารวมสูงสุดที่ DDR4 ถูกล็อคการเขียน ($t_{lockout}$)**, จำนวนคำที่ไหลเข้ามาสะสมในช่วงเวลานี้ ($N_{incoming}$), ขนาดความจุ Ingress BRAM ขั้นต่ำสุดทางทฤษฎี ($Size_{min}$), และ **ขนาดความลึกจริงที่ต้องสังเคราะห์ลง FPGA ($Depth_{actual}$)** ที่เป็นเลขยกกำลังของ 2!

---

#### ตัวเลือก:
* **ก)** $t_{lockout} = 540.0\text{ ns}$, $N_{incoming} = 108\text{ คำ}$, $Size_{min} = 268\text{ คำ}$, $Depth_{actual} = 512\text{ คำ}$
* **ข)** $t_{lockout} = 350.0\text{ ns}$, $N_{incoming} = 70\text{ คำ}$, $Size_{min} = 230\text{ คำ}$, $Depth_{actual} = 256\text{ คำ}$
* **ค)** $t_{lockout} = 540.0\text{ ns}$, $N_{incoming} = 108\text{ คำ}$, $Size_{min} = 140\text{ คำ}$, $Depth_{actual} = 256\text{ คำ}$
* **ง)** $t_{lockout} = 540.0\text{ ns}$, $N_{incoming} = 108\text{ คำ}$, $Size_{min} = 268\text{ คำ}$, $Depth_{actual} = 1024\text{ คำ}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การคำนวณเวลารวมที่ DDR4 ถูกระงับการเขียน (Worst-Case Lockout Time: $t_{lockout}$):
$$t_{lockout} = t_{RFC} + t_{arbitration} + t_{page\_miss} = 350.0\text{ ns} + 150.0\text{ ns} + 40.0\text{ ns} = 540.0\text{ ns}$$

##### 2. การคำนวณจำนวนข้อมูลที่ไหลเข้ามาสะสมในระหว่างช่วงเวลา Lockout ($N_{incoming}$):
$$N_{incoming} = \left\lceil \frac{t_{lockout}}{T_{stream}} \right\rceil = \left\lceil \frac{540.0\text{ ns}}{5.0\text{ ns}} \right\rceil = 108\text{ คำ}$$

##### 3. การคำนวณขนาด Ingress BRAM ขั้นต่ำสุด ($Size_{min}$):
เนื่องจากในสภาวะปกติ Ingress FIFO ต้องสะสมข้อมูลให้ได้อย่างน้อย $1\text{ AXI Burst}$ ($128\text{ คำ}$) จึงจะเริ่มทริกเกอร์ DMA Write ได้ และในจังหวะที่พร้อมยิง DMA นั้นเอง DDR4 อาจเกิด Refresh Lockout พอดี ดังนั้น Ingress Cache จะต้องรองรับข้อมูลที่กำลังจะยิง บวกกับข้อมูลที่ไหลเข้ามาใหม่ และบวก Guard Band:
$$Size_{min} = N_{incoming} + Burst\_Len + N_{guard} = 108 + 128 + 32 = 268\text{ คำ}$$

##### 4. การปรับขนาดเข้าสู่เลขยกกำลังของสอง ($Depth_{actual}$):
$$Depth_{actual} = 2^{\lceil \log_2(268) \rceil} = 2^9 = 512\text{ คำ}$$
*(หากเลือกขนาด 256 คำ จะรองรับได้ไม่พอ เพราะ $256 < 268$ ซึ่งจะเกิด Overflow ทันที!)*

ดังนั้น ขนาดความลึกจริงที่ต้องสังเคราะห์คือ **$512\text{ คำ}$** สมบูรณ์แบบ $100\%$!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** คิดเฉพาะเวลา $t_{RFC} = 350\text{ ns}$ โดยลืมคิดความล่าช้าในการแย่งบัสและการเปิดหน้า Page Miss
* **ข้อ ค):** คำนวณ $Size_{min}$ ผิดพลาดโดยลืมบวกขนาดของ AXI Burst ทำให้เลือกขนาด 256 คำซึ่งเสี่ยงล้นทะลัก
* **ข้อ ง):** ขนาด 1024 คำใหญ่เกินความจำเป็นสิ้นเปลืองทรัพยากร BRAM

---

### ข้อที่ 2: การวิเคราะห์สมดุลแบนด์วิดท์ (Bandwidth Balancing Equation) ของระบบ Hybrid FIFO
ในระบบประมวลผลเรดาร์ Hybrid FIFO ต้องรองรับ:
1. การเขียนข้อมูลสตรีมเข้าอย่างต่อเนื่องที่อัตรา: $BW_{write} = 4.0\text{ GB/s}$
2. การอ่านข้อมูลสตรีมออกไปยังเอนจิน FFT อย่างต่อเนื่องที่อัตรา: $BW_{read} = 4.0\text{ GB/s}$
3. บัส DDR4 SDRAM เป็นแบบแชร์ทรัพยากร (Single-Port Controller) ที่มีประสิทธิภาพการใช้งานบัสเฉลี่ย $\eta = 70\%$ (เนื่องจาก Overhead ของการสลับทิศทาง Read/Write Bus Turnaround และ Auto-Refresh)

จงคำนวณหาค่า **แบนด์วิดท์ทางทฤษฎีขั้นต่ำของ DDR4 Interface ($BW_{DDR\_theo}$)** ที่จำเป็นต้องมี เพื่อไม่ให้ Ingress FIFO ล้น และไม่ให้ Egress FIFO เกิด Starvation!

---

#### ตัวเลือก:
* **ก)** $BW_{DDR\_theo} \ge 5.71\text{ GB/s}$
* **ข)** $BW_{DDR\_theo} \ge 8.00\text{ GB/s}$
* **ค)** $BW_{DDR\_theo} \ge 11.43\text{ GB/s}$
* **ง)** $BW_{DDR\_theo} \ge 16.00\text{ GB/s}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ค)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **ผลรวมแบนด์วิดท์ที่แท้จริงที่ไหลผ่าน DDR4 (Total Real-Time Traffic):**
   เนื่องจาก DDR4 ต้องทำหน้าที่รับข้อมูลเขียนจาก Ingress FIFO และส่งข้อมูลอ่านให้แก่ Egress FIFO พร้อมกันผ่านทางบัสเดียวกัน:
   $$BW_{total\_payload} = BW_{write} + BW_{read} = 4.0\text{ GB/s} + 4.0\text{ GB/s} = 8.0\text{ GB/s}$$
2. **การคิดค่าประสิทธิภาพของบัส ($\eta = 70\% = 0.70$):**
   เนื่องจากการสลับทิศทางระหว่างคำสั่ง Write และ Read บนบัส DDR4 ต้องเสียเวลา Bus Turnaround Delay ($t_{WTR}$ และ $t_{RTW}$) รวมถึงการทำ Precharge และ Refresh ทำให้แบนด์วิดท์จริงที่ใช้งานได้มีเพียง $70\%$ ของแบนด์วิดท์หน้าป้าย:
   $$BW_{DDR\_theo} \times \eta \ge BW_{total\_payload}$$
   $$BW_{DDR\_theo} \ge \frac{BW_{total\_payload}}{\eta} = \frac{8.0\text{ GB/s}}{0.70} \approx 11.4285\text{ GB/s} \approx \mathbf{11.43\text{ GB/s}}$$

ดังนั้น ระบบจะต้องเลือกใช้ชิป DDR4 ที่มีความเร็วไม่ต่ำกว่า **DDR4-1600 บัสกว้าง 64 บิต** ($12.8\text{ GB/s}$) หรือ **DDR4-2400 บัสกว้าง 40 บิต** ขึ้นไป จึงจะรักษาสมดุลแบนด์วิดท์ได้โดยไม่มี Buffer Starvation!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** คิดแบนด์วิดท์เพียงทิศทางเดียว ($4.0 / 0.7 = 5.71$) ซึ่งลืมคิดว่าต้องทำทั้ง Write และ Read บนชิปเดียวกัน
* **ข้อ ข):** คิดเพียง $4.0 + 4.0 = 8.0$ โดยลืมหารค่าประสิทธิภาพ $\eta = 0.7$
* **ข้อ ง):** เผื่อค่ามากเกินไปโดยสมมติว่าประสิทธิภาพบัสเหลือเพียง 50%

---

### ข้อที่ 3: ข้อดีของการใช้ First-Word-Fall-Through (FWFT) ใน Egress BRAM Cache
ในเลเยอร์ที่ 3 ของ Hybrid FIFO (Egress BRAM Cache) ซึ่งรับข้อมูลที่ถูก Pre-fetch มาจาก DDR4 ข้อใดต่อไปนี้คือ **เหตุผลเชิงสถาปัตยกรรมที่สำคัญที่สุดในการเลือกใช้โหมด FWFT (First-Word-Fall-Through)**?

---

#### ตัวเลือก:
* **ก)** เพื่อลดความร้อนของชิป DDR4 ภายนอก
* **ข)** เพื่อให้สตรีมข้อมูลขาออกมีคุณสมบัติ Zero-Latency Read Handshake ตอบสนองต่อสัญญาณ `TREADY` ของ AXI4-Stream ได้ทันที 0 ไซเคิล ป้องกันไม่ให้เกิดการสะดุด (Stall) หรือฟองอากาศในไปป์ไลน์ของผู้บริโภคข้อมูล
* **ค)** เพราะโหมด FWFT ทำให้ความจุของ BRAM เพิ่มขึ้นเป็น 2 เท่า
* **ง)** เพื่อตัดความจำเป็นในการต่อสายดินของบอร์ด FPGA

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **บทบาทของ Egress Cache:**
   Egress Cache ทำหน้าที่แปลงการอ่านแบบเป็นช่วงๆ (Chunked Burst Read) จาก DDR4 ให้กลายเป็น **สตรีมข้อมูลต่อเนื่องที่ราบรื่น (Smooth Continuous Stream)** สำหรับโมดูลปลายทาง
2. **ความสำคัญของโหมด FWFT:**
   เมื่อโมดูลปลายทาง (เช่น เอนจิน FFT หรือจอภาพแสดงผล) ส่งสัญญาณขอข้อมูล (`TREADY = 1`):
   * หากใช้ Standard Read โหมด ข้อมูลจะโผล่ออกมาในไซเคิลถัดไป ซึ่งไม่ตรงตามมาตรฐาน AXI-Stream และอาจทำให้เกิดฟองอากาศ (Idle Bubbles) ทุกครั้งที่มีการหยุดชะงัก
   * เมื่อใช้โหมด FWFT พร้อม Skid Buffer ข้อมูลคำแรกจะมาจ่อรอที่พอร์ตเอาต์พุตล่วงหน้าทันที ทำให้สามารถส่งมอบข้อมูลได้ในไซเคิลเดียวกับที่เกิด Handshake ตอบสนองได้ทันที $100\%$!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** โหมดของ BRAM ภายในชิปไม่มีผลต่ออุณหภูมิของ DDR4 ภายนอก
* **ข้อ ค):** FWFT ไม่ได้เพิ่มขนาดความจุของ BRAM
* **ข้อ ง):** เป็นคำตอบที่ไร้สาระทางกายภาพ
