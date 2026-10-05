# Lesson 151: FPGA BRAM Architecture and True Dual-Port Operations (RAMB36E2 Silicon Microarchitecture, True Dual-Port TDP Matrix, Asynchronous Reset Traps & Address Collision Hazards)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมกายภาพของ Block RAM ในซิลิคอน (Silicon Architecture of RAMB36E2)
ในชิปประมวลผล FPGA ระดับสูง (เช่น AMD/Xilinx UltraScale+, Versal และ Intel Stratix 10) **Block RAM (BRAM)** ไม่ได้ถูกสร้างขึ้นจากตารางลอจิก LUT (Look-Up Table) แต่เป็นบล็อกฮาร์ดแวร์หน่วยความจำแบบ **SRAM Hard Macro** ประสิทธิภาพสูงที่ฝังตัวอยู่เป็นคอลัมน์แนวตั้ง (Memory Columns) ขนานไปกับคอลัมน์ของ DSP Slices

```
               สถาปัตยกรรมภายในบล็อกฮาร์ดแวร์ RAMB36E2 (36 Kbit HARD MACRO)
               
 +-----------------------------------------------------------------------------------------+
 |                                     RAMB36E2 (36,864 Bits)                              |
 |                                                                                         |
 |   +------------------------------------+   +------------------------------------+       |
 |   |         RAMB18E2 (LOWER HALF)      |   |         RAMB18E2 (UPPER HALF)      |       |
 |   |              18,432 Bits           |   |              18,432 Bits           |       |
 |   |                                    |   |                                    |       |
 |   |  +------------------------------+  |   |  +------------------------------+  |       |
 |   |  | 6T SRAM Bitcell Core Array   |  |   |  | 6T SRAM Bitcell Core Array   |  |       |
 |   |  | Sense Amplifiers & Precharge |  |   |  | Sense Amplifiers & Precharge |  |       |
 |   |  +------------------------------+  |   |  +------------------------------+  |       |
 |   +------------------------------------+   +------------------------------------+       |
 |                     ^                                        ^                          |
 |                     +-------------------+--------------------+                          |
 |                                         |                                               |
 |            +----------------------------+----------------------------+                  |
 |            |                                                         |                  |
 |            v PORT A (Indep. Clock, Addr, Data)                       v PORT B           |
 |     [ CLKA, ADDRA, DINA, DOUTA, WEA ]                         [ CLKB, ADDRB, DINB, ... ]|
 |                                                                                         |
 |     +-----------------------------------------------------------------------------+     |
 |     | OPTIONAL EMBEDDED PIPELINE REGISTERS: DOA_REG = 1, DOB_REG = 1              |     |
 |     +-----------------------------------------------------------------------------+     |
 |     | HARDWARE BUILT-IN SEC-DED ECC ENGINE (Single Error Correct, Double Detect)   |     |
 |     +-----------------------------------------------------------------------------+     |
 +-----------------------------------------------------------------------------------------+
```

#### คุณลักษณะทางกายภาพที่สำคัญของ RAMB36E2:
1. **ขนาดความจุ (Capacity):** ความจุรวม $36,864\text{ บิต}$ (36 Kbits) ซึ่งสามารถแยกอิสระเป็นบล็อก $18\text{ Kbit}$ (RAMB18E2) สองตัวที่ทำงานขนานกันได้
2. **True Dual-Port (TDP) Mode:** มีพอร์ตการทำงาน 2 พอร์ต (Port A และ Port B) ที่แยกจากกันอย่างสมบูรณ์:
   * แต่ละพอร์ตมีสัญญาณนาฬิกา ($CLKA, CLKB$), สายแอดเดรส ($ADDR$), สายข้อมูลเข้า ($DIN$), สายข้อมูลออก ($DOUT$), และสายควบคุมการเขียน ($WE$) เป็นของตนเอง
   * สามารถทำการอ่าน (Read) หรือเขียน (Write) พร้อมกันทั้งสองพอร์ตได้ในไซเคิลเดียวกัน
3. **การแปลงอัตราส่วนข้อมูลอิสระ (Independent Port Aspect Ratio):** แต่ละพอร์ตสามารถกำหนดความกว้างบัสข้อมูลต่างกันได้บนแอดเดรสสเปซเดียวกัน (เช่น Port A กว้าง 32 บิต เขียนข้อมูลเข้า แต่ Port B กว้าง 64 บิต อ่านข้อมูลออก)

#### ตารางการจัดสรรความกว้างข้อมูลและความลึก (Port Aspect Ratio Configurations):
| ความจุบล็อก | ความลึกของแอดเดรส (Depth) | ความกว้างบัสข้อมูล (Data Width) | จำนวนบิตตรวจสอบพาริตี (Parity Bits) | ความกว้างบัสรวม (Total Bus) |
|:---:|:---:|:---:|:---:|:---:|
| **36 Kb** | $512$ | $64$ บิต | $8$ บิต | $72$ บิต |
| **36 Kb** | $1,024$ | $32$ บิต | $4$ บิต | $36$ บิต |
| **36 Kb** | $2,048$ | $16$ บิต | $2$ บิต | $18$ บิต |
| **36 Kb** | $4,096$ | $8$ บิต | $1$ บิต | $9$ บิต |
| **36 Kb** | $8,192$ | $4$ บิต | $0$ บิต | $4$ บิต |
| **36 Kb** | $16,384$ | $2$ บิต | $0$ บิต | $2$ บิต |
| **36 Kb** | $32,768$ | $1$ บิต | $0$ บิต | $1$ บิต |

---

### 1.2 กับดักของการใช้ Asynchronous Reset บน BRAM (The Asynchronous Reset Disaster)

สิ่งที่สร้างความเสียหายอย่างรุนแรงต่อการใช้ทรัพยากรชิป FPGA คือการที่วิศวกรติดนิสัยเขียนโค้ดรีเซ็ตแบบ Asynchronous ให้กับทุกสัญญาณใน RTL:

```verilog
// ==============================================================================
// สไตล์โค้ดที่เป็นอันตราย: การใช้ ASYNCHRONOUS RESET บนหน่วยความจำ
// ==============================================================================
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        dout <= 32'd0; // <--- ข้อผิดพลาดระดับวิกฤต: BRAM Hard Macro ไม่รองรับ Async Reset!
    end else begin
        if (we) ram[addr] <= din;
        dout <= ram[addr];
    end
end
```

```
               ผลกระทบของการใส่ ASYNCHRONOUS RESET ต่อการสังเคราะห์วงจร
               
 [ โค้ดที่ถูกต้อง: Synchronous Reset ]         [ โค้ดที่มีปัญหา: Asynchronous Reset ]
 ------------------------------------         --------------------------------------
 Inferred เป็น RAMB36E2 Hard Macro            Synthesizer ไม่สามารถแมปเข้า BRAM ได้!
 ใช้ทรัพยากร:                                 ถูกบังคับแยกส่วนออกเป็น Flip-Flops & LUTs!
 - BRAM: 1 บล็อก (100% ประสิทธิภาพ)            ใช้ทรัพยากร:
 - LUTs: 0 ตัว                                - BRAM: 0 บล็อก (ทิ้งว่างเปล่า)
 - FFs : 0 ตัว                                - LUTs: > 1,024 ตัว (Distributed RAM)
                                              - FFs : > 1,024 ตัว (พุ่งสูงขึ้น 10,000%!)
```

#### ฟิสิกส์ของซิลิคอน (Silicon Reality):
ในระดับเซลล์ทรานซิสเตอร์ เซลล์หน่วยความจำ 6T SRAM และรีจิสเตอร์ขาออกของ BRAM Hard Macro **รองรับเฉพาะ Synchronous Set/Reset (พอร์ต `RSTREG_A` / `RSTREG_B`) เท่านั้น!** ไม่มีทางเดินสายสัญญาณรีเซ็ตแบบอะซิงโครนัสเข้าสู่เซลล์  
เมื่อเครื่องมือสังเคราะห์ (Vivado หรือ Quartus) ตรวจพบคำสั่ง `or negedge rst_n`:
1. มันจะปฏิเสธการ Infer โค้ดดังกล่าวเป็น BRAM
2. มันจะแปลงอาร์เรย์หน่วยความจำทั้งหมดไปเป็น **Distributed RAM (LUT RAM) หรือ Slice Flip-Flops**
3. ผลลัพธ์: การใช้ทรัพยากร Logic บน FPGA พุ่งทะลุเพดานทันที บอร์ดเต็ม และ Fmax พังทลายลงจาก $500\text{ MHz}$ เหลือต่ำกว่า $120\text{ MHz}$!

---

### 1.3 พลศาสตร์ของการชนกันของแอดเดรส (True Dual-Port Address Collision Physics)

ในโหมด True Dual-Port เมื่อพอร์ตทั้งสองเข้าถึงแอดเดรสเดียวกัน ($ADDR_A == ADDR_B$) ในเวลาใกล้เคียงกัน จะเกิดปรากฏการณ์ **Address Collision**:

```
                       หน้าต่างเวลาของการชนกันของแอดเดรส (COLLISION WINDOW)
                       
  CLKA (Write Port)   ------+   +-----------------------+   +-----------------------+
                            |   |                       |   |                       |
                      ------+---+                       +---+                       +---
                      |<--->| t_write_pulse
 
  CLKB (Read Port)    ----------+   +-----------------------+   +-----------------------+
                                |   |                       |   |                       |
                      ----------+---+                       +---+                       +
                            |<->| Delta t_collision
 
  Bitcell Bitlines    ==========[ X X X X X X X X X X ]=================================
                                ^
                                |-- สภาวะอันตราย: Bitline เกิดแรงดันก้ำกึ่ง (Metastable Level)
                                    วงจร Sense Amp ขยายสัญญาณผิดพลาด ข้อมูลกลายเป็นสุ่ม!
```

#### หน้าต่างเวลาวิกฤตของการชนกัน (Collision Timing Window $\Delta t_{collision}$):
เซลล์ 6T SRAM ต้องการเวลาในการดึงประจุ (Discharge) บนสาย Bitline และ Precharge สำหรับการอ่าน/เขียน หากขอบสัญญาณนาฬิกาของ $CLKA$ และ $CLKB$ มีความคลาดเคลื่อนทางเวลาเข้าใกล้กันเกินไป:

$$|\Delta t| < t_{collision\_window} \approx t_{setup\_addr} + t_{hold\_addr} + t_{internal\_write}$$
บนเทคโนโลยี UltraScale+ ค่า $\Delta t_{collision\_window}$ มีขนาดประมาณ **$500\text{ ps}$ ถึง $1.2\text{ ns}$**

#### ผลลัพธ์ทางกายภาพเมื่อเกิดการชนกันข้ามพอร์ต:
1. **Write-Read Collision (พอร์ตหนึ่งเขียน อีกพอร์ตอ่าน):**
   * ข้อมูลที่ถูกเขียนลงในเซลล์ SRAM จะถูกบันทึกอย่างถูกต้อง
   * **แต่ข้อมูลที่พอร์ตอ่านดึงออกไปจะกลายเป็นค่าขยะ (Corrupted Data / Undefined X) ที่ไม่สามารถคาดเดาได้!**
2. **Write-Write Collision (ทั้งสองพอร์ตพยายามเขียนข้อมูลลงแอดเดรสเดียวกัน):**
   * ทรานซิสเตอร์ Pass-Gate ของทั้งสองพอร์ตจะพยายามดึงสาย Bitline ไปคนละระดับแรงดัน (Contention)
   * ข้อมูลที่ถูกบันทึกลงในเซลล์ SRAM จะเสียหายทั้งคู่ (Bit Corruption ถาวรในรอบนั้น)!

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** จอแสดงผลข้อมูลการบินในห้องนักบิน (Aerospace Glass Cockpit Primary Flight Display: PFD) ใช้ชิป FPGA Defense-Grade Kintex UltraScale (XCKU060):
* BRAM ถูกใช้เป็น Double-Buffer Framebuffer จัดเก็บข้อมูลภาพสัญลักษณ์เครื่องบิน (Artificial Horizon, Altitude Tape, Compass Rose) ความละเอียด $1920 \times 1080$ ที่ $60\text{ fps}$
* **Port A (Write):** รับข้อมูลเวกเตอร์กราฟิกจากโปรเซสเซอร์ควบคุมการบินที่ความถี่ $CLK_A = 100.0\text{ MHz}$
* **Port B (Read):** ส่งข้อมูลพิกเซลออกสู่ชิปส่งสัญญาณจอภาพ HDMI/ARINC-818 ที่ความถี่ $CLK_B = 148.5\text{ MHz}$

**วิกฤตหน้างาน:** ในระหว่างการบินทดสอบจริง นักบินรายงานว่าจอแสดงผลเกิดอาการ **เส้นสแกนเขียวกะพริบและภาพฉีกขาด (Green Scanline Tearing Artifacts)** สุ่มเกิดขึ้นบนหน้าจอทุกๆ 3-10 วินาที ในจุดที่เครื่องบินกำลังเอียงเลี้ยวอย่างรวดเร็ว ส่งผลให้ระบบถูกระงับการรับรองความปลอดภัยทางการบิน (Airworthiness Certification) ทันที!

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] หน้าจอแสดงผลการบินเกิดภาพฉีกและเส้นเขียวกะพริบระหว่างการบิน
      |
      +---> [Why 1] ทำไมจึงเกิดเส้นสีเขียวและภาพฉีกขาดบนจอภาพ?
      |             --> เพราะค่าสีพิกเซลที่อ่านจาก BRAM Framebuffer มีบิตกลับขั้วเป็น 0x00FF00 (Pure Green)
      |
      +---> [Why 2] ทำไม BRAM จึงส่งข้อมูลสีที่ผิดพลาดออกมา?
      |             --> เพราะเกิด True Dual-Port Address Collision ภายใน BRAM
      |
      +---> [Why 3] ทำไมจึงเกิด Address Collision ข้ามพอร์ต?
      |             --> เพราะ Port A (กราฟิกเอนจิน) กำลังเขียนข้อมูลลงแอดเดรสเดียวกับที่ Port B (พิกเซลสแกน) กำลังอ่านพอดี
      |
      +---> [Why 4] ทำไมระบบถึงยอมให้ทั้งสองพอร์ตเข้าถึงแอดเดรสเดียวกันพร้อมกัน?
      |             --> เพราะผู้ออกแบบไม่ได้ติดตั้งวงจรตรวจจับและแยกหน้าชน (Ping-Pong Buffer Lock Arbiter)
      |                 โดยคิดว่า Double Buffering จะสลับหน้าได้ทันเองโดยอัตโนมัติ
      |
      +---> [Why 5 - Root Cause] ทำไมผู้ออกแบบถึงไม่ได้ใส่วงจรป้องกัน Address Collision?
                    --> เพราะผู้ออกแบบเข้าใจผิดว่าโหมด WRITE_FIRST ของ BRAM จะส่งข้อมูลใหม่ให้ Port B ทัน
                        โดยไม่เข้าใจว่าคุณสมบัติ WRITE_FIRST ใช้ได้เฉพาะภายใน "พอร์ตเดียวกัน" เท่านั้น
                        ไม่สามารถป้องกันการชนกันระหว่าง "สองพอร์ตที่ใช้คนละ Clock" ได้!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการเกิดภาพฉีกขาดและข้อมูลผิดพลาดจาก BRAM Address Collision

   SILICON LIMITATIONS (BRAM Hard Macro)      ARCHITECTURAL DESIGN (Memory Arbitration)
         |                                          |
   Collision Window กว้าง 1.2 ns ระหว่างสองพอร์ต       ขาดวงจร Ping-Pong Semaphore Lock
         \                                          /
          \   Bitcell Bitlines สับสนทางไฟฟ้า        /   คิดว่าโหมด WRITE_FIRST ป้องกันข้ามพอร์ตได้
           \   Sense Amplifier แซมเปิลขยะกึ่งกลาง   /   สองพอร์ตทำงานบน Clock คนละความถี่ (100M vs 148.5M)
            +------------------------------------+
            |                                    |
            |   AVIONICS DISPLAY FRAMEBUFFER     |===> [CRITICAL FLIGHT SAFETY HAZARD]
            |   TEARING & DATA CORRUPTION        |
            +------------------------------------+
           /                                      \
          /   ใส่ Async Reset จนเกือบเสีย BRAM     \   ทดสอบเฉพาะภาพนิ่ง (Static Test Pattern)
         /                                          \
   โมเดล Simulation ไม่เตือน Warning Collision         ไม่ได้รัน Stress Test ในสภาวะเปลี่ยนมุมเลี้ยวเร็ว
         |                                          |
   EDA MODELING DEFICIENCIES                  TESTING BLIND-SPOTS
```

---

### โค้ด RTL ฮาร์ดแวร์ป้องกัน Collision ด้วย Ping-Pong Buffer Semaphore Lock

```verilog
// ==============================================================================
// SOP-COMPLIANT COLLISION-FREE PING-PONG BRAM BUFFER CONTROLLER
// ==============================================================================
module collision_free_framebuffer #(
    parameter integer ADDR_WIDTH = 10,
    parameter integer DATA_WIDTH = 32
)(
    // ฝั่งเขียน (Graphics Engine Domain)
    input  wire                  clk_wr,
    input  wire                  rst_wr_n, // Synchronous Reset แนะนำสำหรับ BRAM
    input  wire [ADDR_WIDTH-1:0] wr_addr,
    input  wire [DATA_WIDTH-1:0] wr_data,
    input  wire                  wr_en,
    input  wire                  wr_frame_done, // สัญญาณแจ้งว่าวาดภาพเฟรมปัจจุบันเสร็จสิ้น
    
    // ฝั่งอ่าน (Display Scanout Domain)
    input  wire                  clk_rd,
    input  wire                  rst_rd_n,
    input  wire [ADDR_WIDTH-1:0] rd_addr,
    output reg  [DATA_WIDTH-1:0] rd_data,
    input  wire                  rd_frame_done  // สัญญาณแจ้งว่าสแกนภาพออกจอครบเฟรมแล้ว
);

    // ตัวแปรสลับหน้า Ping-Pong Buffer (0 = Page A, 1 = Page B)
    reg wr_page_ptr;
    reg rd_page_ptr;
    
    // ซิงโครไนเซอร์ส่งสัญญาณสลับหน้าข้ามโดเมนนาฬิกา
    (* ASYNC_REG = "TRUE" *) reg [1:0] rd_done_sync;
    (* ASYNC_REG = "TRUE" *) reg [1:0] wr_done_sync;

    // 1. ควบคุมตัวชี้หน้าฝั่งเขียน: ห้ามเขียนทับหน้าที่ฝั่งอ่านกำลังอ่านอยู่เด็ดขาด!
    always @(posedge clk_wr) begin
        if (!rst_wr_n) begin
            wr_page_ptr  <= 1'b0;
            rd_done_sync <= 2'b00;
        end else begin
            rd_done_sync <= {rd_done_sync[0], rd_page_ptr};
            
            if (wr_frame_done) begin
                // สลับหน้าเขียนได้เฉพาะเมื่อหน้าถัดไปไม่ใช่หน้าที่ฝั่งอ่านกำลังทำงานอยู่
                if (wr_page_ptr == rd_done_sync[1]) begin
                    wr_page_ptr <= ~wr_page_ptr;
                end
            end
        end
    end

    // 2. ควบคุมตัวชี้หน้าฝั่งอ่าน: ดึงเฉพาะหน้าที่เขียนเสร็จสมบูรณ์ 100% แล้วเท่านั้น
    always @(posedge clk_rd) begin
        if (!rst_rd_n) begin
            rd_page_ptr  <= 1'b1;
            wr_done_sync <= 2'b00;
        end else begin
            wr_done_sync <= {wr_done_sync[0], wr_page_ptr};
            
            if (rd_frame_done) begin
                if (rd_page_ptr != wr_done_sync[1]) begin
                    rd_page_ptr <= wr_done_sync[1];
                end
            end
        end
    end

    // 3. ป้องกันการชนกันอย่างสมบูรณ์แบบด้วยการต่อ MSB ของแอดเดรสเข้ากับ Page Pointer
    wire [ADDR_WIDTH:0] full_wr_addr = {wr_page_ptr, wr_addr};
    wire [ADDR_WIDTH:0] full_rd_addr = {rd_page_ptr, rd_addr};

    // อินสแตนชิเอต BRAM Hard Macro อย่างถูกต้อง (ไม่มี Asynchronous Reset)
    (* ram_style = "block" *) reg [DATA_WIDTH-1:0] memory [(2**(ADDR_WIDTH+1))-1:0];

    // Port A: Write Only
    always @(posedge clk_wr) begin
        if (wr_en) begin
            memory[full_wr_addr] <= wr_data;
        end
    end

    // Port B: Read Only (พร้อมเปิดใช้งาน BRAM Output Register เพื่อรีด Fmax)
    always @(posedge clk_rd) begin
        rd_data <= memory[full_rd_addr];
    end

endmodule
```

---

### SOP Checklist สำหรับการตรวจรับและ Sign-off บล็อก BRAM

```
[ ] 1. Reset Architecture Audit:
       - ตรวจสอบโค้ด RTL ทั้งหมดที่แมปเป็น BRAM: ต้องไม่มีสัญญาณ Asynchronous Reset บนพอร์ตเอาต์พุต
       - โค้ดที่ถูกต้อง: `always @(posedge clk)` เท่านั้น ห้ามมี `or negedge rst_n` ใน Block RAM

[ ] 2. Synthesis Log BRAM Verification:
       - ตรวจสอบรายงาน Synthesis Log: ยืนยันว่าอาร์เรย์ถูก Infer เป็น "Block RAM" หรือ "RAMB36E2"
       - ตรวจสอบว่าไม่มี Warning: `RAM primitive inferred as distributed RAM due to asynchronous reset`

[ ] 3. True Dual-Port Collision Prevention:
       - หากใช้ TDP ข้าม Clock Domain ที่ต่างกัน ต้องมีวงจรแยกหน้า (Ping-Pong Buffer) หรือวงจร Arbiter
       - แอดเดรสของ Port A และ Port B ต้องไม่มีโอกาสตรงกันในไซเคิลเดียวกันอย่างเด็ดขาด

[ ] 4. BRAM Output Pipelining:
       - ตรวจสอบการเปิดใช้งาน BRAM Internal Register (`DOA_REG = 1` หรือ `DOB_REG = 1`)
       - ยืนยันว่า Datapath Read Latency ถูกทดแทนในตัวควบคุมเรียบร้อยแล้ว
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| ブロックRAM | ぶろっくらむ | Burokku Ramu | หน่วยความจำบล็อกแรมฮาร์ดแวร์ (Block RAM: BRAM) |
| 真のデュアルポート | しんのでゅあるぽーと | Shin no Dyuaru Pōto | โหมดทรูดูอัลพอร์ตสมบูรณ์แบบ (True Dual-Port: TDP) |
| アドレス衝突 | あどれすしょうとつ | Adoresu Shōtotsu | การเข้าถึงแอดเดรสเดียวกันพร้อมกันจนชนกัน (Address Collision) |
| 非同期リセットの罠 | ひどうきりせっとのわな | Hidōki Risetto no Wana | กับดักการใช้รีเซ็ตแบบอะซิงโครนัสบนแรม (Asynchronous Reset Trap) |
| 分散RAM展開 | ぶんさんらむてんかい | Bunsan Ramu Tenkai | การแตกตัวหลุดไปเป็น Distributed RAM (LUT RAM Fallback) |
| 読み出し中書き込み動作 | よみだしちゅうかきこみどうさ | Yomidashichū Kakikomi Dōsa | พฤติกรรมเมื่ออ่านและเขียนพร้อมกัน (Read-during-Write Behavior) |
| ピンポンバッファ | ぴんぽんばっふぁ | Pinpon Baffa | โครงสร้างสลับหน้าบัฟเฟอร์คู่ (Ping-Pong / Double Buffer) |
| 排他制御 | はいたせいぎょ | Haita Seigyo | วงจรควบคุมการเข้าถึงแบบกีดกันแต่เพียงผู้เดียว (Mutual Exclusion / Arbitration) |
| 内部パイプライン段 | ないぶぱいぷらいんだん | Naibu Paipurain-dan | รีจิสเตอร์ไปป์ไลน์ภายในตัวบล็อกแรม (BRAM Internal Output Register) |
| 資源枯渇 | しげんこかつ | Shigen Kokatsu | ภาวะทรัพยากรบนชิปหมดหรือขาดแคลน (Resource Exhaustion) |
| ビット化け | びっとばけ | Bitto Bake | ข้อมูลบิตผิดเพี้ยนหรือกลับขั้วผิดพลาด (Bit Corruption / Inversion) |
| 検図判定不合格 | けんずはんていふごうかく | Kenzu Hantei Fugōkaku | ผลการตัดสินการตรวจแบบไม่ผ่านเกณฑ์ (Design Review Rejection) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการใส่ Asynchronous Reset จนทำให้ BRAM หลุดไปเป็น Distributed RAM
**สถานที่:** ห้องประชุมตรวจสอบแบบวงจรประมวลผลสัญญาณดิจิทัล (Digital Signal Processing Design Review)  
**ผู้เข้าร่วม:** Chief Verification Architect (หัวหน้าสถาปนิกตรวจสอบแบบ) และ Senior FPGA RTL Engineer (วิศวกรออกแบบ RTL)

* **Chief Architect:**  
  「おい、この合成レポート（Synthesis Utilization Report）を見てみろ。LUTの使用率が94%まで跳ね上がってリソース不足（資源枯渇）寸前になっているぞ！一方でBRAMはわずか12%しか使われていない。何が起きているんだ？コードを確認したら、画像バッファの記述で `always @(posedge clk or negedge rst_n)` と非同期リセットを入れているじゃないか！BRAMハードウェアが非同期リセット非対応なのは常識だろう！」  
  *(Oi, kono gōsei repōto (Synthesis Utilization Report) o mite miro. LUT no shiyōritsu ga 94% made haneagatte risōsu busoku (shigen kokatsu) sunzen ni natte iru zo! Ippō de BRAM wa wazuka 12% shika tsukawarete inai. Nani ga okite iru n da? Kōdo o kakunin shitara, gazō baffa no kijutsu de `always @(posedge clk or negedge rst_n)` to hidōki risetto o irete iru ja nai ka! BRAM hādowea ga hidōki risetto hi-taiō na no wa jōshiki darō!)*  
  **ความหมาย:** "เฮ้ย ดูรายงานการใช้ทรัพยากรหลังการสังเคราะห์ (Utilization Report) ตรงนี้สิ การใช้งาน LUT พุ่งทะยานขึ้นไปถึง 94% จนทรัพยากรแทบจะหมดชิปอยู่แล้ว! ในขณะที่ BRAM ถูกใช้ไปแค่ 12% เอง เกิดอะไรขึ้นกันแน่? พอผมไปไล่ดูโค้ด ในตัวบัฟเฟอร์ภาพคุณเขียน `always @(posedge clk or negedge rst_n)` ใส่ Asynchronous Reset เข้าไปเฉยเลย! การที่ BRAM Hardware Macro ไม่รองรับ Asynchronous Reset มันเป็นความรู้พื้นฐานไม่ใช่เรอะ!"

* **RTL Engineer:**  
  「社内のコーディング標準規約で『すべてのレジスタに非同期リセットを設けるべし』と規定されていたため、RAMの出力レジスタにも機械的に非同期リセットを記述してしまいました。まさかVivadoがBRAMへの推論を諦めて、すべて分散RAM（LUT）に展開してしまうとは思いませんでした。」  
  *(Shanai no kōdingu hyōjun kiyaku de "subete no rejisuta ni hidōki risetto o mōkeru beshi" to kitei sarete ita tame, RAM no shutsuryoku rejisuta ni mo kikaiteki ni hidōki risetto o kijutsu shite shimaimashita. Masaka Vivado ga BRAM e no suiron o akiramete, subete bunsan RAM (LUT) ni tenkai shite shimau to wa omoimasen deshita.)*  
  **ความหมาย:** "เพราะในคู่มือมาตรฐานการเขียนโค้ดของบริษัทระบุไว้ว่า 'รีจิสเตอร์ทุกตัวต้องมี Asynchronous Reset' ครับ ผมเลยใส่รีเซ็ตอะซิงโครนัสให้กับเอาต์พุตของ RAM ไปตามความเคยชิน ไม่คาดคิดเลยว่า Vivado จะยอมแพ้ในการ Infer เป็น BRAM แล้วจับแตกตัวออกไปเป็น Distributed RAM บน LUT ทั้งหมดแบบนี้ครับ"

* **Chief Architect:**  
  「愚直に規約を盲信して物理ハードウェアの構造を無視するな！BRAMの出力段は同期リセット（`RSTREG`）しか受け付けない。非同期リセットを要求されれば、ツールはスライス内のLUTとフリップフロップを何千個も消費してエミュレートするしかないんだ。直ちに感度リストから `negedge rst_n` を削除し、同期リセット記述へ修正しろ。それだけでLUT使用率は30%台まで劇的に低下するはずだ！」  
  *(Guchoku ni kiyaku o mōshin shite butsuri hādowea no kōzō o mushi suru na! BRAM no shutsuryoku-dan wa dōki risetto (`RSTREG`) shika uketsukenai. Hidōki risetto o yōkyū sarereba, tsūru wa suraisu-nai no LUT to furippufuroppu o nanzen-ko mo shōhi shite emyurēto suru shika nai n da. Tadachini kando risuto kara `negedge rst_n` o sakujo shi, dōki risetto kijutsu e shūsei shiro. Sore dake de LUT shiyōritsu wa 30%-dai made gekiteki ni teika suru hazu da!)*  
  **ความหมาย:** "อย่ามัวแต่กอดตำรากฎเกณฑ์จนมองข้ามโครงสร้างทางกายภาพของฮาร์ดแวร์จริงสิ! วงจรเอาต์พุตของ BRAM มันรับได้แค่ Synchronous Reset (`RSTREG`) เท่านั้น ถ้าคุณไปบังคับให้มันทำอะซิงโครนัส เครื่องมือมันก็ไม่มีทางเลือกนอกจากเอา LUT กับ Flip-Flop นับพันๆ ตัวมาต่อเลียนแบบให้ จงไปลบ `negedge rst_n` ออกจาก Sensitivity List ทันที แล้วแก้เป็น Synchronous Reset ซะ แค่นั้นการใช้ LUT ก็จะลดฮวบลงมาเหลือระดับ 30% ทันที!"

---

#### สถานการณ์ที่ 2: การตรวจสอบปัญหา True Dual-Port Address Collision ในระบบสองโดเมนนาฬิกา
* **Chief Architect:**  
  「次はこのTDP（真のデュアルポート）構成だ。Port A（100MHz書き込み）とPort B（148.5MHz読み出し）が、同一のフレームメモリ領域に対して非同期にアクセスしている。お互いのアドレス衝突（コリジョン）を回避する排他制御回路がどこにも見当たらないぞ。同一アドレスに同時アクセスした場合、メモリセル内部のビット線電位が不定になり、出力に不正データ（ビット化け）が出るリスクをどう防ぐ気だ？」  
  *(Tsugi wa kono TDP (shin no dyuaru pōto) kōsei da. Port A (100MHz kakikomi) to Port B (148.5MHz yomidashi) ga, dōitsu no furēmu memori ryōiki ni taishite hidōki ni akusesu shite iru. Otagai no adoresu shōtotsu (korijon) o kaihi suru haita seigyo kairo ga doko ni mo miataranai zo. Dōitsu adoresu ni dōji akusesu shita baai, memori seru naibu no bittosen den'i ga futei ni nari, shutsuryoku ni fusei dēta (bitto bake) ga deru risuku o dō fusegu ki da?)*  
  **ความหมาย:** "ต่อไปคือโครงสร้าง True Dual-Port ตรงนี้ Port A (100MHz เขียน) กับ Port B (148.5MHz อ่าน) เข้าถึงพื้นที่หน่วยความจำเดียวกันแบบอะซิงโครนัส แต่ผมไม่เห็นวงจรควบคุมการเข้าถึง (Arbiter) เพื่อป้องกัน Address Collision เลยสักนิด ถ้าเกิดการเข้าถึงแอดเดรสเดียวกันพร้อมกัน ระดับแรงดันบนสาย Bitline ภายในเซลล์หน่วยความจำจะกลายเป็นค่า Undefined แล้วข้อมูลจะเพี้ยน คุณมีแผนป้องกันความเสี่ยงนี้อย่างไร?"

* **RTL Engineer:**  
  「BRAMのプロパティを `WRITE_FIRST` モードに設定してあるため、書き込み中のデータがそのまま読み出しポートへフォワーディングされるものと考えていました。」  
  *(BRAM no puropati o `WRITE_FIRST` mōdo ni settei shite aru tame, kakikomichū no dēta ga sonomama yomidashi pōto e fowādingu sareru mono to kangaete imashita.)*  
  **ความหมาย:** "ผมตั้ง Property ของ BRAM เป็นโหมด `WRITE_FIRST` ไว้ครับ เลยคิดว่าข้อมูลที่กำลังเขียนอยู่จะถูก Forwarding ส่งข้ามไปให้พอร์ตอ่านโดยอัตโนมัติครับ"

* **Chief Architect:**  
  「大間違いだ！`WRITE_FIRST` が保証されるのは『同一ポートで同一クロックの場合』のみだ！非同期の2ポート間で衝突が起きた場合、データシート（UG573）に明記されている通り、読み出しデータは完全に『未定義（Corrupted/X）』になる！直ちにピンポンバッファ構成へ改修し、書き込み中のページと読み出し中のページを最上位アドレスビット（MSB）で物理的に完全分離しろ。検図承認は改修完了後だ！」  
  *(Ōmachigai da! `WRITE_FIRST` ga hoshō sareru no wa "dōitsu pōto de dōitsu kurokku no baai" nomi da! Hidōki no 2-pōto-kan de shōtotsu ga okita baai, dētashīto (UG573) ni meiki sarete iru tōri, yomidashi dēta wa kanzen ni "miteigi (Corrupted/X)" ni naru! Tadachini pinpon baffa kōsei e kaishū shi, kakikomichū no pēji to yomidashichū no pēji o sai-jōi adoresu bitto (MSB) de butsuri-teki ni kanzen bunri shiro. Kenzu shōnin wa kaishū kanryō-go da!)*  
  **ความหมาย:** "เข้าใจผิดไปกันใหญ่แล้ว! โหมด `WRITE_FIRST` มันรับประกันเฉพาะ 'กรณีพอร์ตเดียวกันบน Clock เดียวกัน' เท่านั้น! ถ้าเกิดการชนกันระหว่าง 2 พอร์ตที่ต่างโดเมนนาฬิกา ในดาต้าชีต (UG573) ระบุไว้ชัดเจนว่าข้อมูลที่อ่านได้จะกลายเป็น 'Undefined/Corrupted' โดยสิ้นเชิง! จงไปแก้เป็น Ping-Pong Buffer เดี๋ยวนี้ แล้วใช้บิตสูงสุด (MSB) ของแอดเดรสแยกหน้าเขียนกับหน้าอ่านออกจากกันทางกายภาพให้ขาดสนิท ผมจะอนุมัติการตรวจแบบหลังจากแก้ไขเสร็จแล้วเท่านั้น!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณการระเบิดของทรัพยากรลอจิกจากการใช้ Asynchronous Reset (Logic Resource Explosion Calculation)
ในโมดูลประมวลผลข้อมูลเครือข่าย วิศวกรต้องการสร้างอาร์เรย์หน่วยความจำ FIFO ขนาดความจุ:
* ความลึก (Depth): $1,024\text{ เวิร์ด}$
* ความกว้างข้อมูล (Data Width): $64\text{ บิต}$
* ความจุรวม: $1,024 \times 64 = 65,536\text{ บิต}$ ($64\text{ Kbits}$)

เปรียบเทียบการสังเคราะห์สองกรณีบนชิป Kintex UltraScale+ (ที่มีสเปก 1 CLB Slice ประกอบด้วย 8 LUT6 และ 16 Flip-Flops):
* **กรณีที่ 1 (Synchronous Reset):** โค้ดถูกเขียนตามมาตรฐาน ทำให้ Vivado Infer เป็นบล็อกฮาร์ดแวร์ `RAMB36E2` (ซึ่ง 1 บล็อกจุได้สูงสุด $36\text{ Kbits}$ ในคอนฟิกูเรชัน $1024 \times 36 \times 2$)
* **กรณีที่ 2 (Asynchronous Reset บน Output Register):** โค้ดมีคำสั่ง `or negedge rst_n` บังคับให้ Vivado ไม่สามารถใช้ BRAM ได้ และต้องแปลงเป็น **Distributed RAM (LUT RAM)**:
  * ในสถาปัตยกรรม UltraScale+ การทำ Distributed RAM ลึก $64$ เวิร์ด กว้าง $1$ บิต ใช้ $1$ LUT6
  * ดังนั้นความลึก $1,024$ เวิร์ด ($16 \times 64$) กว้าง $64$ บิต ต้องใช้ LUT RAM สำหรับเซลล์เมมโมรี $= 16 \times 64 = 1,024\text{ LUTs}$
  * วงจรมัลติเพล็กเซอร์ถอดรหัสอ่านข้อมูล (Read Multiplexers): ต้องการ LUT เพิ่มเติมอีก $256\text{ LUTs}$
  * รีจิสเตอร์ขาออกพร้อมอะซิงโครนัสรีเซ็ต: ต้องการ Flip-Flops จำนวน $64\text{ FFs}$

จงคำนวณหา:
1. จำนวนบล็อก BRAM ที่ใช้ในกรณีที่ 1
2. จำนวน Slice LUTs ทั้งหมดที่ถูกผลาญไปในกรณีที่ 2
3. อัตราส่วนการเพิ่มขึ้นของการใช้ทรัพยากรลอจิก (Logic Overhead Ratio) ในกรณีที่ 2 เทียบกับกรณีที่ 1:

A) กรณี 1: $2\text{ BRAMs}$ (0 LUTs); \quad กรณี 2: $1,280\text{ LUTs}$ (เพิ่มขึ้นอนันต์เท่าตัวเทียบกับ BRAM); \quad Overhead มหาศาล  
B) กรณี 1: $4\text{ BRAMs}$ (128 LUTs); \quad กรณี 2: $512\text{ LUTs}$; \quad Overhead $4\times$  
C) กรณี 1: $1\text{ BRAM}$ (0 LUTs); \quad กรณี 2: $2,048\text{ LUTs}$; \quad Overhead $16\times$  
D) กรณี 1: $2\text{ BRAMs}$ (64 LUTs); \quad กรณี 2: $256\text{ LUTs}$; \quad Overhead $2\times$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: วิเคราะห์กรณีที่ 1 (Synchronous Reset -> BRAM Inferencing)**
ความจุรวมที่ต้องการ: $1,024 \times 64 = 65,536\text{ บิต}$
บล็อกฮาร์ดแวร์ `RAMB36E2` ในโหมดกว้าง 32/36 บิต:
* 1 บล็อก `RAMB36E2` สามารถจัดโครงสร้างเป็น $1,024\text{ depth} \times 36\text{ bits}$ (รวมพาริตี) หรือ $32\text{ bits}$ ข้อมูล
* เพื่อให้ได้ความกว้าง $64\text{ บิต}$ ที่ความลึก $1,024$:
  $$\text{จำนวน BRAM36 ที่ต้องใช้} = \frac{64\text{ บิต}}{32\text{ บิต}} = 2\text{ บล็อก}$$
* การใช้ทรัพยากร Fabric LUTs: **$0\text{ LUTs}$** (ใช้ Hard Macro ภายในทั้งหมด)

**ขั้นตอนที่ 2: วิเคราะห์กรณีที่ 2 (Asynchronous Reset -> Distributed RAM)**
ความจุ $1,024 \times 64$ บิต:
1. เซลล์หน่วยความจำ Distributed RAM:
   * 1 LUT6 บน UltraScale+ ทำหน้าที่เป็น RAM64X1D (ความลึก 64 บิต, กว้าง 1 บิต)
   * สำหรับความลึก 1,024 บิต ต้องใช้ LUT RAM ต่อขนานกันในแนวลึก:
     $$\frac{1024}{64} = 16\text{ LUTs ต่อ 1 บิตข้อมูล}$$
   * สำหรับความกว้าง 64 บิต:
     $$N_{mem\_lut} = 16 \times 64 = 1,024\text{ LUTs}$$
2. วงจรถอดรหัสและเลือกสัญญาณ (Read Address Muxing):
   * ต้องใช้ MUX 16-to-1 สำหรับแต่ละบิตข้อมูล เพื่อเลือกจาก 16 กลุ่ม:
   * MUX 16-to-1 บนสถาปัตยกรรม LUT6 ต้องใช้เฉลี่ยประมาณ $4\text{ LUTs}$ ต่อบิต
   * สำหรับ 64 บิต:
     $$N_{mux\_lut} = 64 \times 4 = 256\text{ LUTs}$$
3. รวม LUT ทั้งหมดในกรณีที่ 2:
   $$N_{total\_lut} = 1,024 + 256 = 1,280\text{ LUTs}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** (กรณี 1 ใช้เพียง $2\text{ BRAMs}$ และ $0\text{ LUTs}$ ขณะที่กรณี 2 ผลาญ LUT ไปถึง $1,280\text{ ตัว}$ โดยที่ BRAM ปล่อยทิ้งว่างเปล่า) ซึ่งสะท้อนถึงหายนะของการใส่ Asynchronous Reset เพียงบรรทัดเดียวในโค้ด RTL!

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคำนวณจำนวน BRAM สูงเกินจริง (BRAM36 รองรับ 32 บิตได้ 2 ตัว)
* ข้อ C และ D มีการคำนวณจำนวน LUT สำหรับโครงสร้าง Distributed RAM ผิดสัดส่วน

---

### คำถามที่ 2: การวิเคราะห์หน้าต่างเวลาและการชนกันของแอดเดรสในโหมด TDP (Address Collision Window Analysis)
ในระบบประมวลผลเรดาร์ True Dual-Port BRAM ทำงานด้วยสัญญาณนาฬิกาอิสระ 2 แหล่ง:
* พอร์ต A (Write Port): $F_{clkA} = 150.0\text{ MHz} \implies T_{clkA} \approx 6.667\text{ ns}$
* พอร์ต B (Read Port): $F_{clkB} = 200.0\text{ MHz} \implies T_{clkB} = 5.000\text{ ns}$

จากข้อมูลทางกายภาพของซิลิคอน (Datasheet Timing Parameters):
* หน้าต่างเวลาการชนกันของแอดเดรส (Address Collision Window):
  $$t_{collision} = \pm 650.0\text{ ps} \quad (\text{ช่วงความกว้างรวม } T_{win} = 1.300\text{ ns})$$
* หากขอบขาขึ้นของ $CLKB$ ตกอยู่ภายในช่วง $\pm 650\text{ ps}$ รอบขอบขาขึ้นของ $CLKA$ ในขณะที่ $ADDR_A == ADDR_B$ ข้อมูลที่อ่านได้จาก Port B จะเกิดความเสียหาย (Bit Corruption)

หากทั้งสองพอร์ตเข้าถึงตำแหน่งแอดเดรสเดียวกันอย่างต่อเนื่อง ($ADDR_A \equiv ADDR_B$ ตลอดเวลา):
กำหนดให้ความสัมพันธ์ของเฟสระหว่างสัญญาณนาฬิกาทั้งสองมีการเลื่อนลอยแบบสุ่มสม่ำเสมอ (Uniform Phase Distribution)  
จงคำนวณหา:
1. ความน่าจะเป็นทางสถิติ ($P_{collision}$) ที่การอ่านข้อมูลในรอบหนึ่งๆ ของ Port B จะเกิดการชนกันและได้ข้อมูลขยะ
2. หาก Port B อ่านข้อมูล $200 \times 10^6\text{ ครั้งต่อวินาที}$ จะเกิดเหตุการณ์ข้อมูลเสียหายเฉลี่ยกี่ครั้งต่อวินาที ($R_{error}$):

A) $P_{collision} \approx 19.5\%, \quad R_{error} \approx 3.90 \times 10^7\text{ ครั้ง/วินาที}$  
B) $P_{collision} \approx 9.75\%, \quad R_{error} \approx 1.95 \times 10^7\text{ ครั้ง/วินาที}$  
C) $P_{collision} \approx 26.0\%, \quad R_{error} \approx 5.20 \times 10^7\text{ ครั้ง/วินาที}$  
D) $P_{collision} \approx 1.30\%, \quad R_{error} \approx 2.60 \times 10^6\text{ ครั้ง/วินาที}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณความกว้างของหน้าต่างอันตรายเทียบกับคาบเวลาของ Port A**
ในแต่ละรอบสัญญาณนาฬิกาของ Port A ($T_{clkA} = 6.667\text{ ns}$):
ช่วงเวลาที่อันตรายคือช่วง $\pm 650\text{ ps}$ รอบขอบขาขึ้น:
$$T_{danger} = 2 \times 650\text{ ps} = 1300\text{ ps} = 1.300\text{ ns}$$

**ขั้นตอนที่ 2: คำนวณความน่าจะเป็นของการชนกัน ($P_{collision}$)**
เมื่อเฟสของ Port B กระจายตัวแบบสุ่มอย่างสม่ำเสมอทั่วทั้งคาบเวลา $T_{clkA}$:
$$P_{collision} = \frac{T_{danger}}{T_{clkA}} = \frac{1.300\text{ ns}}{6.6667\text{ ns}} = \frac{1.300}{6.6667} \approx 0.1950 \approx 19.5\%$$
*(มีความน่าจะเป็นสูงถึงเกือบ 20% ที่การอ่านจะชนเข้ากับหน้าต่างอันตราย!)*

**ขั้นตอนที่ 3: คำนวณอัตราการเกิดข้อผิดพลาดต่อวินาที ($R_{error}$)**
Port B ทำงานที่ความถี่ $F_{clkB} = 200.0\text{ MHz} = 2.0 \times 10^8\text{ ครั้ง/วินาที}$:
$$R_{error} = F_{clkB} \times P_{collision} = (200 \times 10^6) \times 0.1950 = 39,000,000\text{ ครั้ง/วินาที} = 3.90 \times 10^7\text{ ครั้ง/วินาที}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($P_{collision} \approx 19.5\%, R_{error} \approx 3.90 \times 10^7\text{ ครั้ง/วินาที}$) ชี้ชัดว่าหากไม่มีวงจร Arbiter ข้อมูลที่อ่านได้จะพังพินาศเกือบ 40 ล้านครั้งในทุกๆ หนึ่งวินาที!

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคิดความกว้างหน้าต่างเพียงฝั่งเดียว ($650\text{ ps}$) แทนที่จะคิด $\pm 650\text{ ps}$
* ข้อ C นำคาบเวลาของ Port B ($5.0\text{ ns}$) มาเป็นตัวหาร ซึ่งผิดหลักความน่าจะเป็นของการกระจายตัวของขอบ Port A
* ข้อ D มีการคำนวณทศนิยมผิดพลาด 1 ตำแหน่ง

---

### คำถามที่ 3: การประเมินผลกระทบของการกำหนดค่าพอร์ตไม่สมมาตรต่อ Address Mapping (Asymmetric Port Aspect Ratio Address Mapping)
วิศวกรออกแบบโมดูลแปลงความกว้างข้อมูลแบบไร้ FIFO โดยใช้ BRAM36 ในโหมด True Dual-Port:
* **Port A (Write Port):** บัสข้อมูลความกว้าง $16\text{ บิต}$ ($DINA[15:0]$), ขนาดแอดเดรส $ADDR_A$ มีความกว้าง $11\text{ บิต}$ (ความลึก $2,048$ คำ)
* **Port B (Read Port):** บัสข้อมูลความกว้าง $64\text{ บิต}$ ($DOUTB[63:0]$), ขนาดแอดเดรส $ADDR_B$ มีความกว้าง $9\text{ บิต}$ (ความลึก $512$ คำ)

ความจุรวมของทั้งสองพอร์ตเท่ากันเป๊ะ:
$$\text{Port A: } 2,048 \times 16 = 32,768\text{ บิต}$$
$$\text{Port B: } 512 \times 64 = 32,768\text{ บิต}$$
กำหนดให้การจัดเรียงข้อมูลเป็นแบบ Little-Endian:
* คำข้อมูลขนาด 64 บิตที่แอดเดรส $ADDR_B = K$ ประกอบด้วยคำข้อมูลขนาด 16 บิตจำนวน 4 คำ ได้แก่คำที่เขียนจาก $ADDR_A = 4K+0, 4K+1, 4K+2, 4K+3$

หาก Port A เขียนข้อมูลลงแอดเดรสดังต่อไปนี้:
* เขียน $16'\text{hAAAA}$ ลงที่ $ADDR_A = 11'\text{d0008}$
* เขียน $16'\text{hBBBB}$ ลงที่ $ADDR_A = 11'\text{d0009}$
* เขียน $16'\text{hCCCC}$ ลงที่ $ADDR_A = 11'\text{d0010}$
* เขียน $16'\text{hDDDD}$ ลงที่ $ADDR_A = 11'\text{d0011}$

จงระบุค่าแอดเดรส $ADDR_B$ ที่ถูกต้องในการอ่านข้อมูลชุดนี้ออกมาทั้งคำ และระบุค่าข้อมูล 64-บิต ($DOUTB[63:0]$) ที่อ่านได้:

A) $ADDR_B = 9'\text{d0002}, \quad DOUTB = 64'\text{hDDDD\_CCCC\_BBBB\_AAAA}$  
B) $ADDR_B = 9'\text{d0008}, \quad DOUTB = 64'\text{hAAAA\_BBBB\_CCCC\_DDDD}$  
C) $ADDR_B = 9'\text{d0002}, \quad DOUTB = 64'\text{hAAAA\_BBBB\_CCCC\_DDDD}$  
D) $ADDR_B = 9'\text{d0004}, \quad DOUTB = 64'\text{hDDDD\_CCCC\_BBBB\_AAAA}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณความสัมพันธ์ของแอดเดรส ($ADDR_B$)**
อัตราส่วนความกว้างข้อมูล:
$$\text{Ratio} = \frac{64\text{ บิต}}{16\text{ บิต}} = 4$$
ดังนั้น 1 คำของ Port B ($64\text{ บิต}$) จะครอบคลุม 4 คำของ Port A ($16\text{ บิต}$):
$$ADDR_B = \left\lfloor \frac{ADDR_A}{4} \right\rfloor = ADDR_A[10:2]$$
แอดเดรสที่เขียน: $ADDR_A = 8, 9, 10, 11$
$$ADDR_B = \frac{8}{4} = 2 = 9'\text{d0002}$$

**ขั้นตอนที่ 2: จัดเรียงข้อมูล 64-บิตตามมาตรฐาน Little-Endian**
ในสถาปัตยกรรม Xilinx UltraScale+ BRAM:
* $ADDR_A$ เศษ 0 (แอดเดรส 8) จะแมปเข้ากับบิตต่ำสุด: $DOUTB[15:0] = 16'\text{hAAAA}$
* $ADDR_A$ เศษ 1 (แอดเดรส 9) จะแมปเข้ากับ: $DOUTB[31:16] = 16'\text{hBBBB}$
* $ADDR_A$ เศษ 2 (แอดเดรส 10) จะแมปเข้ากับ: $DOUTB[47:32] = 16'\text{hCCCC}$
* $ADDR_A$ เศษ 3 (แอดเดรส 11) จะแมปเข้ากับบิตสูงสุด: $DOUTB[63:48] = 16'\text{hDDDD}$

รวมเวิร์ด 64-บิต:
$$DOUTB[63:0] = \{16'\text{hDDDD}, 16'\text{hCCCC}, 16'\text{hBBBB}, 16'\text{hAAAA}\} = 64'\text{hDDDD\_CCCC\_BBBB\_AAAA}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($ADDR_B = 9'\text{d0002}, DOUTB = 64'\text{hDDDD\_CCCC\_BBBB\_AAAA}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะใช้แอดเดรสเท่ากับ Port A โดยไม่หาร 4
* ข้อ C ผิด เพราะจัดเรียงข้อมูลแบบ Big-Endian สลับหัวท้าย
* ข้อ D คำนวณการเลื่อนแอดเดรสผิดพลาด
