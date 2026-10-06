# Lesson 185: FPGA FIFO Part 5 - Asymmetrical & Gearbox FIFOs (Data Width Conversion, Word Assembly/Disassembly, Endianness Alignment & Partial-Word Flush Protocols)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์การแปลงขนาดความกว้างบัสข้อมูล (The Data Width Mismatch Dilemma)
ในระบบประมวลผลบนชิป FPGA วิศวกรต้องเผชิญกับสถานการณ์ที่โมดูลต้นทางและโมดูลปลายทางมีความกว้างของบัสข้อมูล (Data Width) แตกต่างกันอย่างสิ้นเชิง:
* **ฝั่งอินพุตความกว้างแคบ (Narrow Interface):** เช่น ชิป ADC สุ่มสัญญาณ 16 บิต, พอร์ตรับส่งข้อมูลอนุกรม SPI/UART ขนาด 8 บิต, หรืออินเทอร์เฟซ I2S Audio
* **ฝั่งประมวลผลความกว้างสูง (Wide Interface):** เช่น บัสระบบ AXI4 Memory Interconnect ขนาด 64 บิต, 128 บิต, หรือ 512 บิต, และเอนจิน DMA Accelerator

```
                 สถาปัตยกรรม ASYMMETRICAL DATA WIDTH CONVERSION
                 
    [ 1. UPSIZING CONVERSION (แคบไปกว้าง: เช่น 8-bit -> 32-bit, อัตราส่วน R = 4) ]
    
    din (8-bit)  : ──[B0]──► [B1]──► [B2]──► [B3] ──► (สะสมครบ 4 ไบต์)
                                                        │
    dout (32-bit): ═════════════════════════════════════▼═══< [B3, B2, B1, B0] >═══
    
    [ 2. DOWNSIZING CONVERSION (กว้างไปแคบ: เช่น 64-bit -> 16-bit, อัตราส่วน R = 4) ]
    
    din (64-bit) : ═══════════════════════< [W3, W2, W1, W0] >═════════════════════
                                            │       │       │       │
    dout (16-bit): ──────────[W0]───────────┴►[W1]──┴►[W2]──┴►[W3]──┴──────────────
                              (ทะยอยปล่อยทีละ 16 บิตติดต่อกัน 4 ไซเคิล)
```

#### อัตราส่วนการแปลงขนาด (Conversion Ratio: $R$):
ในการออกแบบฮาร์ดแวร์ อัตราส่วนความกว้างของบัสทั้งสองฝั่งมักถูกจำกัดให้เป็น **เลขยกกำลังของสอง ($R = 2^K$)** เสมอ เพื่อให้การแปลงแอดเดรสหน่วยความจำสามารถทำได้ด้วยการเลื่อนบิต (Bit Slicing / Shifting) โดยไม่ต้องใช้วงจรหาร (Divider Logic) ที่สิ้นเปลืองทรัพยากร:
$$R = \frac{W_{wide}}{W_{narrow}} = 2^K \quad (R \in \{2, 4, 8, 16, 32\})$$

---

### 1.2 โครงสร้างหน่วยความจำ Asymmetrical Dual-Port RAM ใน FPGA

บนชิป FPGA ระดับอุตสาหกรรม (เช่น AMD Xilinx 7-Series, UltraScale+, Versal) ฮาร์ดแวร์ **Block RAM Primitive (`RAMB36E2` / `RAMB18E2`)** มีคุณสมบัติพิเศษที่รองรับการกำหนดอัตราส่วนพอร์ต (Aspect Ratio) อิสระทั้งสองฝั่ง:
* พอร์ต A สามารถกำหนดให้เป็น $512 \times 64\text{ บิต}$
* พอร์ต B สามารถกำหนดให้เป็น $2048 \times 16\text{ บิต}$ (หรือ $4096 \times 8\text{ บิต}$) ได้ในก้อน BRAM เดียวกัน!

```
               ความสัมพันธ์ของแอดเดรสหน่วยความจำแบบ ASYMMETRICAL
               
    WIDE PORT ADDRESS  (N บิต)   : [ ADDR_MSB ....................... ADDR_0 ]
                                   │                                         │
    NARROW PORT ADDRESS (N+K บิต): [ ADDR_MSB ....................... ADDR_0 │ SUB_INDEX ]
                                                                             ├────────────┤
                                                                               K บิตย่อย
```

#### การจัดการพอยน์เตอร์เมื่อขนาดความกว้างบัสไม่เท่ากัน:
สมมติระบบทำ Upsizing จากฝั่งเขียน $8\text{ บิต}$ ไปยังฝั่งอ่าน $32\text{ บิต}$ ($R = 4$, $K = 2$):
* พอยน์เตอร์ฝั่งเขียน (`wptr`) จะต้องมีขนาดความละเอียด $M + 2$ บิต
* พอยน์เตอร์ฝั่งอ่าน (`rptr`) จะต้องมีขนาดความละเอียด $M$ บิต
* การเปรียบเทียบสถานะ Empty/Full จะต้องทำโดยการจัดสเกล (Scaling Alignment):
  $$\text{Empty Condition} \iff \text{rptr} == (\text{wptr} \gg 2)$$
  $$\text{Full Condition} \iff (\text{wptr} \gg 2) \text{ วิ่งวนมาชน } \text{rptr}$$

---

### 1.3 วิกฤตการณ์การจัดเรียงไบต์ (Endianness Alignment Pitfalls)

เมื่อนำข้อมูลขนาดเล็กมารวมกันเป็นคำขนาดใหญ่ ความผิดพลาดที่สร้างความปวดหัวให้แก่วิศวกรมากที่สุดคือ **การสลับลำดับไบต์ผิดทิศทาง (Byte Swapping / Endianness Bug)**:

```
          การประกอบคำในโหมด UPSIZING: LITTLE-ENDIAN vs BIG-ENDIAN
          
    ลำดับข้อมูลขาเข้า (8-bit) : ไบต์แรก [A] ──► ไบต์ที่สอง [B] ──► ไบต์ที่สาม [C] ──► ไบต์ที่สี่ [D]
    
    [ 1. LITTLE-ENDIAN ORDER (สถาปัตยกรรม x86, ARM, AXI มาตรฐาน) ]
    * ไบต์แรกสุด [A] จะถูกจัดเก็บที่บิตต่ำสุด [7:0]
    * ไบต์ล่าสุด [D] จะถูกจัดเก็บที่บิตสูงสุด [31:24]
    ===> เอาต์พุต 32-bit: 32'h[D][C][B][A] = {D, C, B, A}
    
    [ 2. BIG-ENDIAN ORDER (สถาปัตยกรรมเครือข่าย Network Byte Order, Motorola) ]
    * ไบต์แรกสุด [A] จะถูกจัดเก็บที่บิตสูงสุด [31:24]
    * ไบต์ล่าสุด [D] จะถูกจัดเก็บที่บิตต่ำสุด [7:0]
    ===> เอาต์พุต 32-bit: 32'h[A][B][C][D] = {A, B, C, D}
```

> [!CAUTION]
> หากวิศวกรสลับลำดับการประกอบไบต์ในฮาร์ดแวร์ผิด สัญญาณภาพ, แอดเดรสหน่วยความจำ, หรือตัวเลขพอยน์เตอร์จะกลายสภาพเป็นตัวเลขขยะ (เช่น ตัวเลข $0x12345678$ กลายเป็น $0x78563412$) ส่งผลให้โปรแกรมซอฟต์แวร์บน CPU แครชทันที!

---

### 1.4 วิกฤตการณ์ข้อมูลเศษตกค้าง (The Partial-Word Flush Crisis)

ในโหมด **Upsizing ($Narrow \to Wide$)** มีภัยเงียบที่ร้ายแรงอย่างยิ่งคือ: **"การที่จำนวนข้อมูลทั้งหมดที่ส่งเข้ามา หารด้วยอัตราส่วน $R$ ไม่ลงตัว (Partial Word Residual)"**:

```
                 สภาวะข้อมูลเศษค้างท่อ (PARTIAL WORD HANG)
                 
    อัตราส่วนการประกอบคำ : R = 8 (ต้องการ 8 ไบต์ เพื่อส่งออก 64 บิต 1 คำ)
    สตรีมข้อมูลส่งเข้ามา   : ส่งมาเพียง 5 ไบต์ [D0, D1, D2, D3, D4] แล้วจบสตรีม!
    
    ┌────┬────┬────┬────┬────┬────┬────┬────┐
    │ D0 │ D1 │ D2 │ D3 │ D4 │ ?? │ ?? │ ?? │  <=== ขาดอีก 3 ไบต์!
    └────┴────┴────┴────┴────┴────┴────┴────┘
                               ▲
    ผลลัพธ์อันตราย:
    * วงจร Gearbox กำลัง "จมปลักรอคอย" ข้อมูลอีก 3 ไบต์ที่ไม่มีวันเดินทางมาถึง!
    * ข้อมูลสำคัญ 5 ไบต์ค้างเติ่งอยู่ใน Shifter ชั่วกัลปวสาน (Permanent Pipeline Stall)!
    * ฝั่งอ่านมองเห็นว่า FIFO ว่างเปล่า ไม่เคยได้รับข้อมูล 5 ไบต์นี้เลย!
```

#### โปรโตคอลการแก้ไข: วงจร Partial-Word Flush และ Byte-Valid Mask:
เพื่อป้องกันไม่ให้ข้อมูลค้างเติ่ง สถาปัตยกรรมระดับ Senior Engineer จะต้องติดตั้ง **กลไก Partial-Word Flush Controller**:
1. **สัญญาณสั่งขับข้อมูลเศษ (`flush` หรือ `eop_flush`):** เมื่อฝั่งส่งส่งข้อมูลคำสุดท้ายของเฟรมเสร็จ จะส่งสัญญาณพัลส์ `flush = 1`
2. **การเติมช่องว่างให้เต็ม (Zero-Padding):** วงจรจะบังคับนำศูนย์ (`8'h00`) เข้าไปเติมในช่องไบต์ที่ขาดหายไปให้ครบขนาดคำกว้างในทันที
3. **การส่งออกบิตระบุความถูกต้องของแต่ละไบต์ (Byte Enable / TKEEP Mask):**
   เพื่อบอกให้ระบบปลายทาง (เช่น บัส AXI4-Stream) ทราบว่าไบต์ใดเป็นข้อมูลจริง และไบต์ใดเป็นขยะ:
   $$\text{TKEEP}[7:0] = 8\text{'b0001\_1111} \quad (\text{แปลว่า 5 ไบต์ล่างใช้ได้, 3 ไบต์บนเป็นขยะ})$$
4. **Hardware Flush Timeout Watchdog:** หากไม่มีสัญญาณ `flush` จากภายนอก ให้ติดตั้งตัวนับเวลา (เช่น หากไม่มีข้อมูลใหม่เข้ามาเกิน 64 ไซเคิล) ให้วงจรทำการ Auto-Flush ข้อมูลเศษที่ตกค้างออกไปโดยอัตโนมัติ!

---

### 1.5 โค้ดแม่แบบภาษา Verilog ระดับ Senior สำหรับ Asymmetrical Gearbox FIFO (8-to-32 bit พร้อม Flush)

```verilog
// ==============================================================================
// ASYMMETRICAL GEARBOX FIFO (8-BIT INPUT TO 32-BIT OUTPUT)
// Senior Gold Standard: Little-Endian Assembly, TKEEP Mask & Zero-Latency Flush
// ==============================================================================
(* keep_hierarchy = "yes" *)
module gearbox_fifo_8to32 #(
    parameter integer ADDR_WIDTH = 8   // Depth = 256 words of 32-bit (1024 bytes)
)(
    input  wire        clk,
    input  wire        rst_n,

    // 8-bit Narrow Write Interface
    input  wire        wr_en,
    input  wire [7:0]  din_byte,
    input  wire        flush_req,      // Force push partial word
    output wire        full,

    // 32-bit Wide Read Interface
    input  wire        rd_en,
    output wire [31:0] dout_word,
    output wire [3:0]  dout_keep,      // AXI-Stream TKEEP byte mask
    output wire        empty,

    // Status
    output wire [ADDR_WIDTH:0] word_count
);

    localparam integer DEPTH = 1 << ADDR_WIDTH;

    // -------------------------------------------------------------------------
    // 1. Memory Core (32-bit wide array)
    // -------------------------------------------------------------------------
    reg [35:0] mem [0:DEPTH-1]; // 32-bit Data + 4-bit Keep
    reg [ADDR_WIDTH-1:0] wptr;
    reg [ADDR_WIDTH-1:0] rptr;
    reg [ADDR_WIDTH:0]   count;

    // -------------------------------------------------------------------------
    // 2. Word Assembly Buffer (Gearbox Barrel Shifter)
    // -------------------------------------------------------------------------
    reg [31:0] assembly_reg;
    reg [3:0]  assembly_keep;
    reg [1:0]  byte_idx;

    wire word_ready_to_write;
    wire [35:0] assembled_packet;

    // Little-Endian byte packing logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            assembly_reg  <= 32'd0;
            assembly_keep <= 4'b0000;
            byte_idx      <= 2'b00;
        end else begin
            if (wr_en && !full) begin
                case (byte_idx)
                    2'b00: begin
                        assembly_reg[7:0]   <= din_byte;
                        assembly_keep[0]    <= 1'b1;
                        byte_idx            <= 2'b01;
                    end
                    2'b01: begin
                        assembly_reg[15:8]  <= din_byte;
                        assembly_keep[1]    <= 1'b1;
                        byte_idx            <= 2'b10;
                    end
                    2'b10: begin
                        assembly_reg[23:16] <= din_byte;
                        assembly_keep[2]    <= 1'b1;
                        byte_idx            <= 2'b11;
                    end
                    2'b11: begin
                        assembly_reg[31:24] <= din_byte;
                        assembly_keep[3]    <= 1'b1;
                        byte_idx            <= 2'b00; // Reset after full word
                    end
                endcase
            end else if (flush_req && (byte_idx != 2'b00) && !full) begin
                // Flush action: Clear index and keep mask for next word
                assembly_reg  <= 32'd0;
                assembly_keep <= 4'b0000;
                byte_idx      <= 2'b00;
            end
        end
    end

    // Condition to write into 32-bit FIFO:
    // Either 4th byte arrived, OR flush requested on non-empty buffer
    wire full_word_complete = (wr_en && !full && (byte_idx == 2'b11));
    wire flush_word_active  = (flush_req && !full && (byte_idx != 2'b00));
    assign word_ready_to_write = full_word_complete || flush_word_active;

    // Pack data and mask
    assign assembled_packet = full_word_complete ? 
        {4'b1111, din_byte, assembly_reg[23:0]} : 
        {assembly_keep, assembly_reg};

    // -------------------------------------------------------------------------
    // 3. FIFO Memory Write Operation
    // -------------------------------------------------------------------------
    always @(posedge clk) begin
        if (word_ready_to_write && (count < DEPTH))
            mem[wptr] <= assembled_packet;
    end

    // -------------------------------------------------------------------------
    // 4. Pointer and Occupancy Tracking
    // -------------------------------------------------------------------------
    wire read_active = rd_en && (count > 0);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wptr  <= {ADDR_WIDTH{1'b0}};
            rptr  <= {ADDR_WIDTH{1'b0}};
            count <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            case ({word_ready_to_write, read_active})
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

    assign full       = (count >= DEPTH - 1);
    assign empty      = (count == 0);
    assign word_count = count;

    // Read Output Register
    reg [35:0] dout_raw;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            dout_raw <= 36'd0;
        else if (read_active)
            dout_raw <= mem[rptr];
    end

    assign dout_word = dout_raw[31:0];
    assign dout_keep = dout_raw[35:32];

endmodule
```

---

### 1.6 SystemVerilog Assertions (SVA) เพื่อตรวจจับ Data Loss ใน Gearbox

```systemverilog
// SVA Verification Checker สำหรับ Asymmetrical Gearbox FIFO
module gearbox_fifo_sva #(
    parameter integer ADDR_WIDTH = 8
)(
    input wire clk,
    input wire rst_n,
    input wire wr_en,
    input wire flush_req,
    input wire full,
    input wire [1:0] byte_idx,
    input wire [3:0] dout_keep
);

    // Property 1: Flush Integrity
    // When flush_req is asserted on residual bytes, byte_idx must reset to 0 in next cycle
    property p_flush_clears_residual;
        @(posedge clk) disable iff (!rst_n)
        (flush_req && byte_idx != 0 && !full) |=> (byte_idx == 0);
    endproperty
    assert_flush_clears: assert property (p_flush_clears_residual)
        else $error("[FATAL_FLUSH]: Gearbox failed to flush partial residual bytes!");

    // Property 2: TKEEP Validity
    // Output keep mask must never be zero on valid read
    property p_tkeep_non_zero;
        @(posedge clk) disable iff (!rst_n)
        $past(dout_keep) != 4'b0000;
    endproperty

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】กล้องถ่ายภาพความร้อนอินฟราเรดทางทหาร (Military FLIR Thermal Camera)
เกิดอาการภาพค้าง 1 วินาทีทุกครั้งที่กดหยุดบันทึก (Last-Frame Pipeline Freeze)
จากบั๊กข้อมูลเศษตกค้างใน Asymmetrical Gearbox FIFO โดยไม่มี Partial Flush
================================================================================
```

#### บริบทของระบบ (System Context):
บริษัทพัฒนาอุปกรณ์อิเล็กทรอนิกส์ป้องกันประเทศ พัฒนากล้องตรวจจับความร้อนอินฟราเรดระยะไกล (Forward Looking Infrared - FLIR) บนชิป FPGA AMD Xilinx Artix-7:
* เซนเซอร์ตรวจวัดความร้อน Microbolometer ส่งสัญญาณดิจิทัลพิกเซลขนาด **$16\text{ บิต}$** ความเร็ว $40\text{ MHz}$
* เอนจินประมวลผลสัญญาณภาพและบันทึกวิดีโอลง SD Card ทำงานบนบัส **$128\text{ บิต}$** AXI4-Stream ความเร็ว $100\text{ MHz}$
* ระหว่างเซนเซอร์และ AXI Bus มีวงจร Asymmetrical Gearbox FIFO ทำการแปลงขนาดจาก $16\text{-bit} \to 128\text{-bit}$ (อัตราส่วน $R = \frac{128}{16} = 8\text{ พิกเซลต่อ 1 คำ AXI}$)
* กล้องมีความละเอียดภาพแปลกเฉพาะทาง: $640 \times 512\text{ พิกเซล}$ พร้อมบิตส่วนหัวและเทเลเมทรีอีก $13\text{ คำ}$ รวมเป็น $327,693\text{ คำ 16 บิต}$ ต่อ 1 เฟรม

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
ในการทดสอบภาคสนามโดยหน่วยรบพิเศษ เมื่อผู้ใช้งานกดปุ่มหยุดบันทึกวิดีโอ (Stop Recording) หรือสลับโหมดภาพ: หน้าจอแสดงผลเกิดอาการ **"ภาพกระตุกค้างนิ่งสนิทเป็นเวลา 1 ถึง 2 วินาที (Last-Frame Hang)"** และไฟล์วิดีโอที่บันทึกลงการ์ดเกิดความเสียหาย (Corrupted MP4/RAW Video Container) ท้ายไฟล์ขาดหายไป ทำให้สูญเสียพยานหลักฐานในภารกิจลาดตระเวนทางยุทธวิธี!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมภาพวิดีโอจึงค้างและไฟล์วิดีโอท้ายไฟล์จึงเสียหาย?**
   * *เพราะเอนจินเขียนไฟล์วิดีโอลง SD Card จมปลักรอคอยสัญญาณ `TLAST` (End of Frame) จากสตรีม AXI และไม่ยอมปิดไฟล์*
2. **ทำไมสัญญาณ `TLAST` จึงไม่เดินทางมาถึงเอนจินเขียนไฟล์?**
   * *เพราะข้อมูลพิกเซลและสัญญาณ `TLAST` ที่ท้ายเฟรมค้างเติ่งอยู่ภายในวงจร Gearbox FIFO ไม่ถูกส่งออกมา*
3. **ทำไมข้อมูลท้ายเฟรมจึงค้างเติ่งอยู่ใน Gearbox FIFO?**
   * *เพราะจำนวนข้อมูลทั้งหมดใน 1 เฟรมคือ $327,693\text{ คำ}$ ซึ่งเมื่อนำมาหารด้วยอัตราส่วนการประกอบคำ $R = 8$:
     $$327,693 \div 8 = 40,961\text{ คำ AXI} \quad \text{เหลือเศษ } \mathbf{5\text{ พิกเซล!}}$$
4. **ทำไมเศษ 5 พิกเซลจึงทำให้ทั้งระบบหยุดชะงัก?**
   * *เพราะวงจร Gearbox ต้องการสะสมให้ครบ 8 พิกเซลจึงจะยอมส่งข้อมูลขนาด 128 บิตออกมา 1 คำ เมื่อข้อมูลขาดไปอีก 3 พิกเซล วงจรจึงหยุดรอคอยอย่างไม่มีกำหนด (Permanent Residual Stall)*
5. **ทำไมวิศวกรจึงไม่ใส่วงจร Partial-Word Flush ในขั้นตอนออกแบบ?**
   * *เพราะวิศวกรคิดคำนวณเฉพาะขนาดภาพ $640 \times 512 = 327,680$ (ซึ่งหารด้วย 8 ลงตัวพอดี) แต่ลืมคิดว่าในเฟรมจริงมี Header Telemetry แปะเพิ่มเข้ามาอีก 13 คำ ทำให้ตัวเลขรวมหารไม่ลงตัว!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                         สาเหตุของความล้มเหลว: LAST-FRAME GEARBOX FREEZE
                         
   METHOD (การออกแบบ Gearbox Protocol)         MACHINE (ฮาร์ดแวร์และการประกอบคำ)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ขาดกลไก Partial-Word Flush     │          │ อัตราส่วน Upsizing R = 8       │
   │ คิดเฉพาะขนาดภาพ ละเลย Header   │          │ เฟรมรวม 327,693 คำ เหลือเศษ 5  │
   │ ไม่มี Hardware Flush Watchdog  │          │ Shifter ค้างรอข้อมูลอีก 3 คำ   │
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ Testbench ทดสอบเฉพาะภาพหารลงตัว│          │ ไม่เคยทดสอบคำสั่ง Stop Record  │
   │ ละเลยสัญญาณ TKEEP ใน AXI-Stream│          │ ปล่อยผ่านเพราะเห็นว่าภาพไหลลื่น│
   │ ขาด SVA ตรวจจับ Residual Hang  │          │ ในโหมดสตรีมต่อเนื่องปกติ       │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (ข้อกำหนดและการตรวจสอบ)             MEASUREMENT (สภาวะการจำลองระบบ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediations):
1. **ติดตั้งวงจร Zero-Latency Flush Controller:**
   * เชื่อมต่อสัญญาณ `frame_end_eop` จากเซนเซอร์เข้ากับขา `flush_req` ของ Gearbox
   * เมื่อ `flush_req = 1` ให้วงจรดันเศษ 5 พิกเซลที่เหลือออกไปเป็นคำขนาด 128 บิตทันที โดยเติมศูนย์ใน 3 ช่องที่เหลือ
2. **สร้างสัญญาณ `TKEEP` กำกับขนาดความกว้างไบต์:**
   * สัญญาณ `TKEEP[15:0]` ถูกขับเป็น `16'h03FF` (10 ไบต์แรกที่มาจาก 5 พิกเซลมีผลใช้งานได้, 6 ไบต์บนเป็นโมฆะ)
   * ส่งสัญญาณ `TLAST = 1` ออกไปพร้อมกับคำที่ถูก Flush เพื่อสั่งปิดเฟรมวิดีโออย่างสมบูรณ์แบบ
3. **ติดตั้ง Watchdog Flush Timer:** หากไม่มีพิกเซลใหม่เข้ามาเกิน $100\text{ ไซเคิล}$ ให้สั่งทำ Auto-Flush ทันทีเพื่อป้องกันสภาวะตกค้าง

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Gearbox FIFO (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | การแปลง Upsizing ($Narrow \to Wide$) มีวงจร Partial Flush หรือไม่? | **ต้องมี $100\%$ ทุกจุด** | [ ] ผ่าน |
| 2 | มีสัญญาณ Byte Enable หรือ AXI `TKEEP` ระบุความถูกต้องของไบต์เศษหรือไม่? | Full TKEEP Generation | [ ] ผ่าน |
| 3 | มีการตรวจสอบและจัดเรียง Endianness (Little vs Big) ตรงตามสเปกบัส? | Verified Byte Order | [ ] ผ่าน |
| 4 | มีการติดตั้ง Hardware Watchdog Timeout Flush สำรองในกรณีฉุกเฉินหรือไม่? | Automatic Timeout Flush | [ ] ผ่าน |
| 5 | มีการเขียน SVA ยืนยันว่าไม่มีข้อมูลเศษค้างท่อเกิน $N$ ไซเคิลหลังจบสตรีม? | Formal Liveness Passed | [ ] ผ่าน |
| 6 | Testbench มีการทดสอบขนาดข้อมูลที่หารไม่ลงตัว ($Remainder \ne 0$) ครบถ้วน? | Non-aligned Stream Tests | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | 非対称データ幅FIFO | ひたいしょうデータはばFIFO | Hitai-shō dēta-haba Faifo | Asymmetrical Data Width FIFO |
| 2 | ギアボックス回路 | ギアボックスかいろ | Giabokkusu kairo | Gearbox Circuit (Width Converter) |
| 3 | アップサイズ / ダウンサイズ | アップサイズ / ダウンサイズ | Appusaizu / Daunsaizu | Upsizing / Downsizing |
| 4 | エンディアン整合 | エンディアンせいごう | Endian seigō | Endianness Alignment (Byte Order) |
| 5 | 端数フラッシュプロトコル | はすうフラッシュプロトコル | Hasū furasshu purotokoru | Partial-Word Flush Protocol |
| 6 | バイト有効マスク | バイトゆうこうマスク | Baito yūkō masuku | Byte Enable Mask (`TKEEP` / `WSTRB`) |
| 7 | パイプライン滞留 | パイプラインたいりゅう | Paipurain tairyū | Pipeline Stagnation / Residual Hang |
| 8 | ゼロ詰めパディング | ゼロづめパディング | Zero-zume paddingu | Zero-Padding Fill |
| 9 | タイムアウト強制排出 | タイムアウトきょうせいはいしゅつ | Taimuauto kyōsei haishutsu | Timeout Forced Flush |
| 10 | アスペクト比変換 | アスペクトひへんかん | Asupekuto-hi henkan | BRAM Aspect Ratio Conversion |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ห้องตรวจแบบระบบเซนเซอร์ความแม่นยำสูง (Precision Sensor Systems Review Room), เมืองคิตะคิวชู (Kitakyushu)  
**ผู้เข้าร่วม:**
* **ทาเคดะซัง (Takeda-san):** หัวหน้าผู้เชี่ยวชาญด้านระบบถ่ายภาพอินฟราเรด (Lead Thermal Imaging Specialist / 首席技師)
* **ชลกร (Chonnakorn):** วิศวกรออกแบบระบบประมวลผลวิดีโอ FPGA (Video Processing FPGA Designer)

---

**武田首席 (Takeda):**  
「チョンナコーン君、この暗視赤外線カメラのビデオパイプライン設計書をレビューしたが、ギアボックスFIFO（16ビットから128ビットへのアップサイズ）に致命的な欠陥がある。センサの解像度データとテレメトリを合算すると、1フレームあたり327,693ワードになるね。これを128ビット（16バイト＝8ワード）へ変換する際、**端数の5ワード**に対するフラッシュ制御が一切記述されていない。録画停止時にこの5ワードはどうなるのかね？」  
*(Chonnakōn-kun, kono anshi sekigaisen kamera no bideo paipurain sekkeisho wo rebyū shita ga, giabokkusu FIFO (16-bit kara 128-bit e no appusaizu) ni chimeiteki na kekkan ga aru. Sensa no kaizōdo dēta to teremetry wo gassan suru to, 1-furēmu atari 327,693-wādo ni naru ne. Kore wo 128-bit (16-baito = 8-wādo) e henkan suru sai, hasū no 5-wādo ni taisuru furasshu seigyo ga issai kijutsu sarete inai. Rokuga teishi-ji ni kono 5-wādo wa dō naru no kane?)*  
**คำแปล:** คุณชลกร ผมได้ตรวจเอกสารออกแบบไปป์ไลน์วิดีโอของกล้องมองกลางคืนอินฟราเรดตัวนี้แล้ว พบข้อบกพร่องร้ายแรงในวงจร Gearbox FIFO (แปลงขยายจาก 16 บิตเป็น 128 บิต) นะ เมื่อรวมข้อมูลความละเอียดของเซนเซอร์กับเทเลเมทรีแล้ว จะได้ข้อมูล 327,693 คำต่อเฟรม ตอนแปลงข้อมูลนี้เป็น 128 บิต (16 ไบต์ = 8 คำ) คุณไม่ได้เขียนลอจิกควบคุมการ Flush สำหรับ **เศษที่เหลือ 5 คำ** เอาไว้เลยแม้แต่น้อย ในจังหวะที่กดหยุดบันทึก ข้อมูล 5 คำนี้จะเกิดอะไรขึ้นหรือครับ?

**チョンナコーン (Chonnakorn):**  
「武田首席、センサからのデータは連続的に入力され続けるため、次のフレームの先頭データが入力されれば、残りの3ワードが埋まって自然に128ビットとして出力されると考えておりました。連続撮影中であればデータが失われることはございません。」  
*(Takeda-shuseki, sensa kara no dēta wa renzokuteki ni nyūryoku sare-tsuzukeru tame, tsugi no furēmu no sentō dēta ga nyūryoku sareba, nokori no 3-wādo ga umatte shizen ni 128-bit to shite shutsuryoku sareru to kangaete orimashita. Renzoku satsuei-chū de areba dēta ga ushinawareru koto wa gozaimasen.)*  
**คำแปล:** หัวหน้าทาเคดะครับ เนื่องจากข้อมูลจากเซนเซอร์จะไหลเข้ามาต่อเนื่อง หากมีข้อมูลของเฟรมถัดไปเข้ามา มันก็จะมาเติม 3 คำที่ขาดหายไปและส่งออกเป็น 128 บิตได้เองตามธรรมชาติครับ ในระหว่างการถ่ายภาพต่อเนื่อง ข้อมูลจึงไม่สูญหายแน่นอนครับ

**武田首席 (Takeda):**  
「『次のフレーム』が来なかったらどうするんだ！ユーザーが録画停止ボタンを押した瞬間、センサのストリームは停止する！その時、最後のフレームの末尾5ワードは、次のフレームが来ないために永久にギアボックス内に滞留（Stall）したままになるんだよ！後段のAXI4-Streamは`TLAST`を受け取れず、ファイル書き込みエンジンはタイムアウトして録画ファイル全体が破損（Corrupted）する！さらに、エンディアンの定義も曖昧だ。Little-EndianなのかBig-Endianなのか、TKEEPバイトマスクをどう生成するのか、設計書に1行も書かれていないじゃないか！」  
*("Tsugi no furēmu" ga konakattara dō suru n da! Yūzā ga rokuga teishi botan wo oshita shunkan, sensa no sutorīmu wa teishi suru! Sono toki, saigo no furēmu no matsubi 5-wādo wa, tsugi no furēmu ga konai tame ni eikyū ni giabokkusu-nai ni tairyū shita mama ni naru n da yo! Kōdan no AXI4-Stream wa TLAST wo uketorezu, fairu kakikomi enjin wa taimuauto shite rokuga fairu zentai ga hason suru! Sarani, endian no teigi mo aimai da. Little-Endian nano ka Big-Endian nano ka, TKEEP baito masuku wo dō seisei suru no ka, sekkeisho ni 1-gyō mo kakarete inai ja nai ka!)*  
**คำแปล:** แล้วถ้า "เฟรมถัดไป" มันไม่มาล่ะจะทำยังไง! วินาทีที่ผู้ใช้กดปุ่มหยุดบันทึก สตรีมจากเซนเซอร์ก็จะหยุดลงทันที! เมื่อนั้น ข้อมูล 5 คำสุดท้ายของเฟรมจะค้างเติ่งอยู่ใน Gearbox ไปตลอดกาลเพราะไม่มีเฟรมใหม่มาเติม! บัส AXI4-Stream ข้างหลังก็จะไม่ได้รับสัญญาณ `TLAST` เอนจินเขียนไฟล์จะเกิด Timeout และไฟล์วิดีโอทั้งไฟล์จะเสียหายไปทั้งหมด! ยิ่งไปกว่านั้น การกำหนด Endianness ก็คลุมเครือ เป็น Little หรือ Big Endian แล้วจะสร้างบิตมาสก์ TKEEP อย่างไร ในเอกสารไม่ได้เขียนไว้เลยแม้แต่บรรทัดเดียว!

**チョンナコーン (Chonnakorn):**  
「ハッ……！ストリームの末尾において、端数データが原因でパイプライン全体がデッドロックに陥るリスクを完全に見落としておりました……！録画ファイルの破損という致命的な不具合を招くところでした！」  
*(Ha'... Sutorīmu no matsubi ni oite, hasū dēta ga gen'in de paipurain zentai ga deddorokku ni ochīru risuku wo kanzen ni miotoshite orimashita...! Rokuga fairu no hason to iu chimeiteki na fuguai wo maneku tokoro deshita!)*  
**คำแปล:** อึก...! ผมมองข้ามความเสี่ยงที่ข้อมูลเศษที่ปลายสตรีมจะทำให้ทั้งไปป์ไลน์ติด Deadlock ไปอย่างสิ้นเชิงเลยครับ...! เกือบจะก่อให้เกิดข้อผิดพลาดร้ายแรงจนไฟล์วิดีโอเสียหายแล้วครับ!

**武田首席 (Takeda):**  
「即座に設計を変更しなさい。EOP（フレーム終了）時に端数をゼロパディングして強制出力する**フラッシュ回路（Flush Logic）**を追加し、後段へは有効バイトを示す`TKEEP`信号（16'h03FF）を同時に出力してAXI4-Streamの仕様に完全準拠させること。さらに無通信が続いた場合のタイムアウト排出機能も組み込み、端数データを含むストレステスト波形を揃えて再検図を受けに来なさい。」  
*(Sokuzani sekkei wo henkō shinasai. EOP-ji ni hasū wo zero-paddingu shite kyōsei shutsuryoku suru furasshu kairo wo tsuika shi, kōdan e wa yūkō baito wo shimesu TKEEP shingō (16'h03FF) wo dōji ni shutsuryoku shite AXI4-Stream no shiyō ni kanzen junkyo saseru koto. Sarani mu-tsūshin ga tsuzuita baai no taimuauto haishutsu kinō mo kumikomi, hasū dēta wo fukumu sutoresu tesuto hakei wo soroete sai-kenzu wo uke ni kinasai.)*  
**คำแปล:** จงรีบแก้ไขการออกแบบทันที เพิ่ม **วงจร Flush Logic** เพื่อเติมศูนย์ในช่องเศษและบังคับส่งข้อมูลออกทันทีเมื่อเจอ EOP และส่งสัญญาณ `TKEEP` (16'h03FF) เพื่อระบุไบต์ที่ถูกต้องควบคู่กันตามมาตรฐาน AXI4-Stream อย่างสมบูรณ์ พร้อมทั้งใส่วงจร Timeout Flush สำรองเมื่อไม่มีข้อมูล และเตรียมรูปคลื่นทดสอบกรณีข้อมูลเศษมาให้ครบถ้วนก่อนกลับมาตรวจแบบใหม่

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณและสร้างสัญญาณ TKEEP ในวงจร Upsizing Gearbox
ในระบบประมวลผลข้อมูลเครือข่าย วงจร Gearbox ทำการรวมข้อมูลจากอินพุตขนาด $16\text{ บิต}$ (2 ไบต์) ไปเป็นเอาต์พุตขนาด $64\text{ บิต}$ (8 ไบต์) สำหรับอินเทอร์เฟซ AXI4-Stream ($R = 4$):
* ในการส่งข้อมูลแพ็กเก็ตหนึ่ง แพ็กเก็ตมีความยาวทั้งหมด $11\text{ ไบต์}$ ซึ่งหมายความว่าประกอบด้วย:
  * ข้อมูล 16 บิต (2 ไบต์) จำนวน 5 คำเต็ม
  * และข้อมูล 8 บิต (1 ไบต์) คำสุดท้าย พร้อมสัญญาณ `eop_flush = 1`
* การจัดเรียงไบต์ในสถาปัตยกรรมเป็นแบบ **Little-Endian Order** (ไบต์แรกสุดอยู่ที่ตำแหน่งบิตต่ำสุด `[7:0]` เสมอ)

เมื่อคำขนาด 64 บิตคำที่สองถูกส่งออกหลังการทำ Flush จงหาค่าของ **บิตมาสก์ `TKEEP[7:0]`** และค่าการจัดวางข้อมูลในบัส 64 บิต `dout[63:0]` สำหรับคำที่สองนี้! (สมมติให้ไบต์ที่ 8, 9, 10 มีค่าเป็น `0xAA`, `0xBB`, `0xCC` ตามลำดับ)

---

#### ตัวเลือก:
* **ก)** `TKEEP = 8'b0000_0111` ($8\text{'h07}$), `dout[63:0] = {40'h0, 8'hCC, 8'hBB, 8'hAA}`
* **ข)** `TKEEP = 8'b1110_0000` ($8\text{'hE0}$), `dout[63:0] = {8'hAA, 8'hBB, 8'hCC, 40'h0}`
* **ค)** `TKEEP = 8'b0000_1111` ($8\text{'h0F}$), `dout[63:0] = {32'h0, 8'h00, 8'hCC, 8'hBB, 8'hAA}`
* **ง)** `TKEEP = 8'b1111_1111` ($8\text{'hFF}$), `dout[63:0] = {40'h0, 8'hCC, 8'hBB, 8'hAA}`

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การวิเคราะห์จำนวนไบต์ในคำที่หนึ่งและคำที่สอง:
* แพ็กเก็ตมีความยาวรวม $11\text{ ไบต์}$:
  * **คำที่ 1 (64 บิต / 8 ไบต์):** ประกอบด้วยไบต์ที่ $0$ ถึง $7$ ครบถ้วนทั้ง 8 ไบต์ $\implies$ `TKEEP = 8'b1111_1111` ($8\text{'hFF}$)
  * **คำที่ 2 (64 บิต / 8 ไบต์):** ประกอบด้วยไบต์ที่เหลือ คือไบต์ที่ $8, 9, 10$ รวมเป็น **$3\text{ ไบต์}$**
  * ขาดอีก 5 ไบต์ (ไบต์ที่ 3 ถึง 7) ซึ่งถูกเติมด้วยศูนย์ (Zero-Padding) จากการ Flush

##### 2. การสร้างสัญญาณ `TKEEP` ตามมาตรฐาน ARM AMBA AXI4-Stream:
* ในระบบ Little-Endian บิตของ `TKEEP[n]` สอดคล้องกับไบต์ที่ $n$ บนเส้นทาง `TDATA[(8n+7) : 8n]`
* ไบต์ที่ 0 มีข้อมูลจริง $\implies \text{TKEEP}[0] = 1$
* ไบต์ที่ 1 มีข้อมูลจริง $\implies \text{TKEEP}[1] = 1$
* ไบต์ที่ 2 มีข้อมูลจริง $\implies \text{TKEEP}[2] = 1$
* ไบต์ที่ 3 ถึง 7 ไม่มีข้อมูล (เป็นศูนย์) $\implies \text{TKEEP}[7:3] = 5\text{'b00000}$
$$\mathbf{TKEEP[7:0] = 8'b0000\_0111 \quad (8'h07)}$$

##### 3. การจัดวางข้อมูลบนบัส 64 บิต (`dout`):
* Byte 0 (`0xAA`) อยู่ที่ `dout[7:0]`
* Byte 1 (`0xBB`) อยู่ที่ `dout[15:8]`
* Byte 2 (`0xCC`) อยู่ที่ `dout[23:16]`
* Byte 3..7 อยู่ที่ `dout[63:24]` ถูก Padding ด้วยค่าศูนย์:
$$\mathbf{dout[63:0] = \{40'h00\_0000\_0000, 8'hCC, 8'hBB, 8'hAA\}}$$

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** สับสนนำการจัดเรียงแบบ Big-Endian มาใช้ ซึ่งขัดแย้งกับข้อกำหนด Little-Endian
* **ข้อ ค):** คิดจำนวนไบต์ผิดเป็น 4 ไบต์
* **ข้อ ง):** กำหนด `TKEEP = 8'hFF` ซึ่งจะทำให้ปลายทางตีความว่า 5 ไบต์บนที่เป็นศูนย์คือข้อมูลจริง นำไปสู่ Data Corruption

---

### ข้อที่ 2: ความสัมพันธ์ของแอดเดรสและพอยน์เตอร์ใน Asymmetrical Dual-Port RAM
พิจารณาหน่วยความจำ Asymmetrical BRAM ที่ใช้ทำ Downsizing FIFO จากฝั่งเขียนกว้าง $64\text{ บิต}$ ($W_{write} = 64$) ไปยังฝั่งอ่านแคบ $16\text{ บิต}$ ($W_{read} = 16$, อัตราส่วน $R = 4$):
* ฝั่งเขียนมีความลึก $Depth_{write} = 256\text{ คำ}$ ทำให้พอยน์เตอร์ฝั่งเขียนมีความกว้าง $ADDR\_WIDTH_{write} = 8\text{ บิต}$
* ฝั่งอ่านมีความลึก $Depth_{read} = 1024\text{ คำ}$ ทำให้พอยน์เตอร์ฝั่งอ่านมีความกว้าง $ADDR\_WIDTH_{read} = 10\text{ บิต}$

หากต้องการตรวจจับสภาวะ **FIFO Full** ในโดเมนเขียน ข้อใดต่อไปนี้คือ **สมการตรรกะเปรียบเทียบพอยน์เตอร์ที่ถูกต้องที่สุด**? (กำหนดให้ใช้พอยน์เตอร์ที่ขยาย MSB เพิ่ม 1 บิตเพื่อแยก Full/Empty)

---

#### ตัวเลือก:
* **ก)** `wfull = (wptr == rptr);`
* **ข)** `wfull = (wptr[8:0] == {~rptr[10], rptr[9:2]});`
* **ค)** `wfull = (wptr[8:0] == (rptr[10:0] >> 2));`
* **ง)** `wfull = (wptr[8:0] == {rptr[10], ~rptr[9:2]});`

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **การปรับสเกลของพอยน์เตอร์ (Pointer Alignment):**
   * ฝั่งอ่านมีพอยน์เตอร์ขนาด $11\text{ บิต}$ (บิต 0 ถึง 9 คือแอดเดรส 1024 คำ, บิต 10 คือ Wrap-around bit)
   * ฝั่งเขียนมีพอยน์เตอร์ขนาด $9\text{ บิต}$ (บิต 0 ถึง 7 คือแอดเดรส 256 คำ, บิต 8 คือ Wrap-around bit)
   * เนื่องจาก $1\text{ คำเขียน} = 4\text{ คำอ่าน}$ ดังนั้น แอดเดรสของฝั่งอ่านเมื่อหารด้วย 4 (`rptr >> 2`) จะสอดคล้องกับพอยน์เตอร์ของฝั่งเขียน
2. **เงื่อนไข Full ด้วยการขยายบิต MSB:**
   * สภาวะ FIFO Full เกิดขึ้นเมื่อ:
     1. พอยน์เตอร์ฝั่งเขียนและพอยน์เตอร์ฝั่งอ่านอยู่ที่ **แอดเดรสเดียวกัน** (`wptr[7:0] == rptr[9:2]`)
     2. และบิต Wrap-around บิตบนสุดมี **สถานะตรงกันข้ามกัน (Inverted MSB)** เพื่อบอกว่าฝั่งเขียนวนรอบแซงหน้าไป 1 รอบเต็ม (`wptr[8] == ~rptr[10]`)
   * เมื่อนำทั้งสองเงื่อนไขมารวมกันจะได้สมการ:
     $$\mathbf{wfull = (wptr[8:0] == \{\sim rptr[10], rptr[9:2]\})}$$

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ความกว้างของพอยน์เตอร์ไม่เท่ากัน (9 บิต vs 11 บิต) ไม่สามารถเปรียบเทียบตรงๆ ได้
* **ข้อ ค):** การเลื่อนบิต `rptr >> 2` จะทำให้บิต MSB ไม่ถูกกลับด้าน ส่งผลให้กลายเป็นเงื่อนไข Empty แทนที่จะเป็น Full
* **ข้อ ง):** กลับด้านผิดบิต (ไปกลับด้านบิตแอดเดรสแทนที่จะกลับด้านบิต Wrap-around)

---

### ข้อที่ 3: สถาปัตยกรรม Hardware Flush Timeout Watchdog
ทำไมในระบบประมวลผลข้อมูลความเร็วสูงที่ใช้ Gearbox FIFO จึง **ไม่ควรพึ่งพาเฉพาะสัญญาณ `flush_req` จากซอฟต์แวร์เพียงอย่างเดียว** และต้องมีวงจร Hardware Timeout Flush เสมอ?

---

#### ตัวเลือก:
* **ก)** เพราะซอฟต์แวร์ทำงานเร็วกว่าฮาร์ดแวร์มากเกินไปจนทำให้บัฟเฟอร์พัง
* **ข)** เพราะหากเกิดสภาวะสายสัญญาณภายนอกหลุดกะทันหัน (Cable Disconnection), ฝั่งส่งเกิดไฟฟ้าดับ (Transmitter Power Loss), หรือมี Bit Error ทำลายแพ็กเก็ตจนสัญญาณ EOP สูญหาย: ซอฟต์แวร์จะไม่เคยรู้ว่ามีข้อมูลเศษค้างอยู่ หากไม่มี Hardware Watchdog ตัวนับเวลาดึงข้อมูลออก ข้อมูลนั้นจะค้างเติ่งใน FIFO ตลอดกาลและบล็อกไม่ให้ระบบเริ่มรับข้อมูลในเซสชันใหม่ได้
* **ค)** เพราะฮาร์ดแวร์ Watchdog ช่วยประหยัดพื้นที่ Block RAM ได้ 50%
* **ง)** เพราะมาตรฐาน IEEE บังคับให้ห้ามใช้ซอฟต์แวร์ควบคุม FIFO

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **สภาวะข้อผิดพลาดในโลกแห่งความเป็นจริง (Real-World Fault Scenarios):**
   ในทางทฤษฎี ซอฟต์แวร์หรือตัวควบคุมโปรโตคอลควรส่งสัญญาณ `flush` เมื่อจบเฟรม แต่ในสภาพหน้างานจริง:
   * สายเคเบิลเซนเซอร์อาจถูกดึงออกขณะกำลังส่งข้อมูลกลางเฟรม
   * เกิดคลื่นรบกวน EMI ทำลายสัญญาณ EOP จนตัวตรวจจับมองไม่เห็นจุดจบ
   * โมดูลส่งข้อมูลเกิด Brown-out รีเซ็ตตัวเองกะทันหัน
2. **บทบาทของ Hardware Timeout Watchdog:**
   หากเกิดเหตุการณ์ดังกล่าว ข้อมูลเศษจะติดค้างอยู่ใน Gearbox หากไม่มีตัวนับเวลาคอยตรวจจับ เมื่อระบบกลับมาเชื่อมต่อใหม่ ข้อมูลของเซสชันใหม่จะถูกนำมาต่อท้ายข้อมูลขยะเก่า เกิด Frame Alignment Error ทันที
   วงจร **Hardware Timeout Watchdog** จะทำหน้าที่เป็นตาข่ายนิรภัยขั้นสุดท้าย (Fail-Safe Net) โดยสั่ง Flush และ Reset State โดยอัตโนมัติหากไม่มีข้อมูลใหม่เข้ามาเกินเวลาที่กำหนด ช่วยให้ระบบฟื้นตัว (Self-Healing) ได้อย่างสมบูรณ์แบบ $100\%$!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ซอฟต์แวร์ทำงานช้ากว่าฮาร์ดแวร์หลายพันเท่า ไม่ใช่เร็วกว่า
* **ข้อ ค):** Watchdog ใช้เพียงตัวนับไม่กี่บิต ไม่ได้ช่วยประหยัดพื้นที่ BRAM
* **ข้อ ง):** ไม่มีมาตรฐานใดห้ามซอฟต์แวร์ส่งสัญญาณควบคุม
