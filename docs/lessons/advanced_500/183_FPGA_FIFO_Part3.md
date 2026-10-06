# Lesson 183: FPGA FIFO Part 3 - Dual-Clock FIFO Latency & Sizing Physics (Pessimistic Flag Latency Bounds, Empty-to-Read & Full-to-Write Propagation Math, Burst Size Formulas)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 คณิตศาสตร์ความหน่วงเวลาของสถานะใน Dual-Clock FIFO (Pessimistic Latency Bounds)
ในบทที่ 175 เราได้ศึกษาฟิสิกส์พื้นฐานของ **Dual-Clock Asynchronous FIFO** และเข้าใจหลักการทำงานของ Gray Code Pointer แล้ว ทว่า ในการประยุกต์ใช้งานจริงในระดับ Lead Architect วิศวกรจะต้องสามารถ **คำนวณและพยากรณ์กรอบเวลาความหน่วง (Quantitative Latency Bounds)** ของการอัปเดตสถานะแฟล็ก `rempty` และ `wfull` ข้ามโดเมนนาฬิกาได้อย่างแม่นยำระดับนาโนวินาที:

```
               กรอบเวลาการแพร่กระจายของสัญญาณแฟล็กข้ามโดเมน CDC
               
    [ WRITE DOMAIN: WCLK ]                             [ READ DOMAIN: RCLK ]
    
    1. เขียนคำแรก (wr_en = 1)
       wptr_gray ขยับ!
          │
          └───► [ 2-FF Sync (RCLK) ] ─────────────────────────► 2. wptr_sync2 มาถึง!
                (ใช้เวลา 2-3 รอบ RCLK)                            rempty ปลดเป็น 0
                                                                  (เริ่มอ่านได้!)
                                                                  
    4. wfull ปลดเป็น 0 ◄──────────────────────── [ 2-FF Sync (WCLK) ] ◄─── 3. อ่านคำแรก (rd_en = 1)
       (เริ่มเขียนต่อได้!)                         (ใช้เวลา 2-3 รอบ WCLK)        rptr_gray ขยับ!
```

#### 1. ความหน่วงเวลาตั้งแต่เขียนคำแรกจนเริ่มอ่านได้ (Empty-to-Read Latency: $T_{empty\_deassert}$):
สมมติว่าในตอนเริ่มต้น FIFO ว่างเปล่าสนิท (`rempty = 1`):
เมื่อฝั่งเขียนยิงข้อมูลคำแรกเข้ามาที่ขอบสัญญาณนาฬิกา $WCLK$ ข้อมูลจะถูกบันทึกลง Memory Core ทันที ทว่า ฝั่งอ่านจะยังไม่รู้เรื่องจนกว่า `wptr_gray` จะเดินทางผ่าน Synchronizer:
1. การอัปเดตพอยน์เตอร์ในโดเมนเขียน: $1 \cdot T_w$
2. การเดินทางผ่านสายส่ง Interconnect ข้ามชิป: $t_{prop}(wptr)$
3. การเข้าแซมเปิลและเคลื่อนผ่าน 2-FF Synchronizer ในโดเมนอ่าน: ในกรณีเลวร้ายที่สุด สัญญาณอาจมาถึงเฉียดฉิวไม่ทันขอบแรกของ $RCLK$ ทำให้ต้องรอเพิ่มอีก 1 รอบ:
   $$t_{sync,r} = (N_{sync} + 1) \cdot T_r$$
4. ลอจิกเปรียบเทียบและขับสัญญาณ `rempty = 0`: $1 \cdot t_{comb}$

$$\mathbf{T_{empty\_deassert} = T_w + t_{prop} + (N_{sync} + 1) \cdot T_r}$$

#### 2. ความหน่วงเวลาตั้งแต่เริ่มอ่านจนเริ่มเขียนต่อได้ (Full-to-Write Latency: $T_{full\_deassert}$):
สมมติว่า FIFO เต็มพิกัด (`wfull = 1`) และฝั่งเขียนหยุดส่งข้อมูล:
เมื่อฝั่งอ่านทำการอ่านข้อมูลออกไป 1 คำที่ขอบสัญญาณนาฬิกา $RCLK$ พื้นที่ใน Memory Core ว่างลงแล้ว 1 ช่อง ทว่า ฝั่งเขียนจะยังไม่ได้รับอนุญาตให้เขียนต่อ จนกว่าข่าวสาร `rptr_gray` จะเดินทางกลับมาถึง:

$$\mathbf{T_{full\_deassert} = T_r + t_{prop} + (N_{sync} + 1) \cdot T_w}$$

> [!NOTE]
> สมการทั้งสองนี้แสดงให้เห็นความจริงทางฟิสิกส์ว่า: **"ฝั่งที่เร็วกว่าจะต้องรอคอยคาบเวลาของฝั่งที่ช้ากว่าเสมอ!"**
> หาก $f_w = 500\text{ MHz}$ ($T_w = 2\text{ ns}$) และ $f_r = 25\text{ MHz}$ ($T_r = 40\text{ ns}$):
> $$T_{full\_deassert} = 40\text{ ns} + t_{prop} + (2+1)(2\text{ ns}) = 40 + t_{prop} + 6 \approx 47\text{ ns}$$
> ฝั่งเขียนความเร็วสูงจะต้องจมปลักรอคอยนานถึง $47\text{ ns}$ (หรือเกือบ 24 ไซเคิลของตนเอง) จึงจะสามารถเขียนข้อมูลคำถัดไปได้!

---

### 1.2 ทฤษฎีการคำนวณขนาดความลึกขั้นต่ำของ FIFO (Asynchronous FIFO Sizing Physics)

คำถามที่วิศวกรอาวุโสทุกคนต้องตอบในการตรวจแบบ Kenzu คือ: **"FIFO ตัวนี้ต้องมีความลึกขั้นต่ำกี่ช่อง จึงจะรับประกันได้ว่าข้อมูลจะไม่ล้น (No Overflow) ในสภาวะ Worst-Case Burst?"**

```
                  แบบจำลองการไหลของข้อมูลในสภาวะ BURST TRANSFER
                  
    ฝั่งเขียน (Producer)                           ฝั่งอ่าน (Consumer)
    ความถี่ fw, คาบ Tw                             ความถี่ fr, คาบ Tr
    ยิง Burst ติดต่อกัน B คำ                      อ่านได้ 1 คำทุกๆ M ไซเคิล
    อัตราการไหล: B คำ / T_burst                    อัตราการดึง: fr / M
    
                        ┌────────────────────────┐
    Data In (fw) ══════►│  ASYNCHRONOUS FIFO     │══════► Data Out (fr)
                        │  (ต้องมีความลึก Depth) │
                        └────────────────────────┘
```

#### การอนุพัทธ์สูตรคำนวณขนาดความลึกทางคณิตศาสตร์ (Step-by-Step Derivation):
1. **ระยะเวลาทั้งหมดที่ฝั่งเขียนใช้ในการยิง Burst ข้อมูล ($T_{burst}$):**
   $$T_{burst} = B \cdot T_w = \frac{B}{f_w}$$
2. **เวลาที่มีให้ฝั่งอ่านสามารถดึงข้อมูลออกได้จริง ($T_{effective\_read}$):**
   เนื่องจากในตอนเริ่มต้น FIFO ว่างเปล่า ฝั่งอ่านจะไม่สามารถอ่านข้อมูลได้ทันทีจนกว่าจะพ้นช่วงเวลา $T_{empty\_deassert}$:
   $$T_{effective\_read} = \max(0, T_{burst} - T_{empty\_deassert})$$
3. **จำนวนข้อมูลที่ฝั่งอ่านสามารถระบายออกไปได้ทันในระหว่างช่วง Burst ($N_{read}$):**
   สมมติว่าฝั่งอ่านสามารถอ่านได้ 1 คำในทุกๆ $M$ ไซเคิลของ $RCLK$ (หากอ่านได้ทุกไซเคิล $M = 1$):
   $$N_{read} = \left\lfloor \frac{T_{effective\_read}}{M \cdot T_r} \right\rfloor = \left\lfloor \frac{T_{burst} - T_{empty\_deassert}}{M \cdot T_r} \right\rfloor$$
4. **ความจุข้อมูลส่วนเกินที่ต้องตกค้างสะสมอยู่ใน FIFO ($Depth_{min}$):**
   $$Depth_{min} = B - N_{read} + N_{guard}$$
   *(โดยที่ $N_{guard}$ คือ Safety Guard Band มักกำหนดไว้ที่ $2 \sim 4\text{ คำ}$)*
5. **การปรับขนาดเข้าสู่เลขยกกำลังของสอง ($Depth_{actual}$):**
   ตามทฤษฎี Gray Code Wrap-Around จากบทที่ 175 ขนาดจริงจะต้องปัดขึ้นเป็นเลขยกกำลังของ 2 เสมอ:
   $$\mathbf{Depth_{actual} = 2^{\lceil \log_2(Depth_{min}) \rceil}}$$

---

### 1.3 ตัวอย่างการคำนวณเปรียบเทียบ: สูตรดั้งเดิม vs สูตรฟิสิกส์จริง

สมมติสถานการณ์จริงในระบบประมวลผลเรดาร์:
* ฝั่งเขียน: ความถี่สูง $f_w = 200\text{ MHz}$ ($T_w = 5.0\text{ ns}$)
* ฝั่งอ่าน: ความถี่ต่ำ $f_r = 50\text{ MHz}$ ($T_r = 20.0\text{ ns}$) โดยอ่านได้ต่อเนื่องทุกไซเคิล ($M = 1$)
* ขนาดข้อมูล Burst: $B = 100\text{ คำ}$ ยิงติดต่อกัน
* วงจร Synchronizer ใช้แบบ 2-Stage ($N_{sync} = 2$)

#### วิธีที่ 1: การคำนวณแบบดั้งเดิมที่ผิดพลาด (The Naive Trap):
วิศวกรส่วนใหญ่มักใช้สูตรง่ายๆ โดยไม่คิดค่าความหน่วงของ Synchronizer:
$$T_{burst} = 100 \times 5.0\text{ ns} = 500\text{ ns}$$
$$N_{read,naive} = \frac{500\text{ ns}}{20.0\text{ ns}} = 25\text{ คำ}$$
$$Depth_{min,naive} = 100 - 25 = 75\text{ คำ} \implies \text{ปัดเป็น } \mathbf{128\text{ คำ}}$$

#### วิธีที่ 2: การคำนวณเชิงฟิสิกส์ระดับ Senior Engineer (The Accurate Sizing):
ต้องคิดค่า $T_{empty\_deassert}$ เข้าไปด้วย:
$$T_{empty\_deassert} = T_w + (N_{sync} + 1) \cdot T_r = 5.0\text{ ns} + (2 + 1) \times 20.0\text{ ns} = 5.0 + 60.0 = 65.0\text{ ns}$$
เวลาที่ฝั่งอ่านมีโอกาสอ่านจริงเหลือเพียง:
$$T_{effective\_read} = 500\text{ ns} - 65.0\text{ ns} = 435.0\text{ ns}$$
จำนวนคำที่อ่านออกได้จริง:
$$N_{read,actual} = \left\lfloor \frac{435.0\text{ ns}}{20.0\text{ ns}} \right\rfloor = 21\text{ คำ! (หายไปถึง 4 คำ!)}$$
คำนวณความจุขั้นต่ำจริง:
$$Depth_{min} = 100 - 21 + 2 (\text{guard}) = 81\text{ คำ}$$
แม้ว่าทั้งสองวิธีจะได้ค่า $Depth_{actual} = 128\text{ คำ}$ เหมือนกันในตัวอย่างนี้ แต่หากขนาด Burst เปลี่ยนเป็น $B = 120$ คำ:
* วิธีที่ 1 จะคำนวณได้ $Depth_{min} = 90$ (ปัดเป็น 128)
* แต่วิธีจริงจะคำนวณได้ $Depth_{min} = 120 - 27 + 2 = 95$ (ซึ่งใกล้ขีดจำกัด 128 มาก) และหากมีการติดขัดเพียงเล็กน้อย FIFO ขนาด 128 จะ **ล้นทะลัก (Overflow)** ทันที!

---

### 1.4 โค้ดแม่แบบภาษา Verilog สำหรับ Dual-Clock FIFO พร้อม Dynamic Capacity Assertions

```verilog
// ==============================================================================
// SENIOR ASYNCHRONOUS DUAL-CLOCK FIFO (ROBUST TIMING & SIZING ARCHITECTURE)
// Supports Accurate Empty/Full Flag Generation with Parameterized Depth
// ==============================================================================
(* keep_hierarchy = "yes" *)
module async_fifo_sized #(
    parameter integer DATA_WIDTH = 32,
    parameter integer ADDR_WIDTH = 8   // Depth = 256 words
)(
    // Write Domain
    input  wire                  wclk,
    input  wire                  wrst_n,
    input  wire                  wr_en,
    input  wire [DATA_WIDTH-1:0] wdata,
    output wire                  wfull,
    output wire [ADDR_WIDTH:0]   w_estimated_count,

    // Read Domain
    input  wire                  rclk,
    input  wire                  rrst_n,
    input  wire                  rd_en,
    output wire [DATA_WIDTH-1:0] rdata,
    output wire                  rempty,
    output wire [ADDR_WIDTH:0]   r_estimated_count
);

    localparam integer DEPTH = 1 << ADDR_WIDTH;

    // -------------------------------------------------------------------------
    // 1. Dual-Port Memory Core
    // -------------------------------------------------------------------------
    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];
    reg [ADDR_WIDTH:0]   wbin, rbin;
    reg [ADDR_WIDTH:0]   wptr_gray, rptr_gray;

    always @(posedge wclk) begin
        if (wr_en && !wfull)
            mem[wbin[ADDR_WIDTH-1:0]] <= wdata;
    end

    assign rdata = mem[rbin[ADDR_WIDTH-1:0]];

    // -------------------------------------------------------------------------
    // 2. Write Domain Logic
    // -------------------------------------------------------------------------
    wire [ADDR_WIDTH:0] wbin_next  = wbin + (wr_en & ~wfull);
    wire [ADDR_WIDTH:0] wgray_next = wbin_next ^ (wbin_next >> 1);

    always @(posedge wclk or negedge wrst_n) begin
        if (!wrst_n) begin
            wbin      <= {(ADDR_WIDTH+1){1'b0}};
            wptr_gray <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            wbin      <= wbin_next;
            wptr_gray <= wgray_next;
        end
    end

    // -------------------------------------------------------------------------
    // 3. Read Domain Logic
    // -------------------------------------------------------------------------
    wire [ADDR_WIDTH:0] rbin_next  = rbin + (rd_en & ~rempty);
    wire [ADDR_WIDTH:0] rgray_next = rbin_next ^ (rbin_next >> 1);

    always @(posedge rclk or negedge rrst_n) begin
        if (!rrst_n) begin
            rbin      <= {(ADDR_WIDTH+1){1'b0}};
            rptr_gray <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            rbin      <= rbin_next;
            rptr_gray <= rgray_next;
        end
    end

    // -------------------------------------------------------------------------
    // 4. Synchronizers with ASYNC_REG
    // -------------------------------------------------------------------------
    (* ASYNC_REG = "TRUE" *) reg [ADDR_WIDTH:0] wptr_sync1, wptr_sync2;
    always @(posedge rclk or negedge rrst_n) begin
        if (!rrst_n) begin
            wptr_sync1 <= {(ADDR_WIDTH+1){1'b0}};
            wptr_sync2 <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            wptr_sync1 <= wptr_gray;
            wptr_sync2 <= wptr_sync1;
        end
    end

    (* ASYNC_REG = "TRUE" *) reg [ADDR_WIDTH:0] rptr_sync1, rptr_sync2;
    always @(posedge wclk or negedge wrst_n) begin
        if (!wrst_n) begin
            rptr_sync1 <= {(ADDR_WIDTH+1){1'b0}};
            rptr_sync2 <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            rptr_sync1 <= rptr_gray;
            rptr_sync2 <= rptr_sync1;
        end
    end

    // -------------------------------------------------------------------------
    // 5. Flag Generations
    // -------------------------------------------------------------------------
    assign rempty = (rptr_gray == wptr_sync2);

    wire wfull_condition = (wgray_next == {~rptr_sync2[ADDR_WIDTH:ADDR_WIDTH-1],
                                           rptr_sync2[ADDR_WIDTH-2:0]});
    reg wfull_reg;
    always @(posedge wclk or negedge wrst_n) begin
        if (!wrst_n)
            wfull_reg <= 1'b0;
        else
            wfull_reg <= wfull_condition;
    end
    assign wfull = wfull_reg;

endmodule
```

---

### 1.5 SystemVerilog Assertions (SVA) เพื่อตรวจจับ Latency Deadlock

```systemverilog
// SVA Verification Checker for Dual-Clock FIFO Latency & Sizing
module async_fifo_latency_sva #(
    parameter integer ADDR_WIDTH = 8
)(
    input wire wclk,
    input wire wrst_n,
    input wire wr_en,
    input wire wfull,
    
    input wire rclk,
    input wire rrst_n,
    input wire rd_en,
    input wire rempty
);

    // 1. Liveness Assertion: After write into empty FIFO, rempty must fall within bounded cycles
    // (Bounded by 10 read clock cycles)
    property p_rempty_deasserts_eventually;
        @(posedge rclk) disable iff (!rrst_n)
        $fell(rempty) or (rempty throughout (##[1:15] !rempty));
    endproperty

    // 2. No Overflow Assertion in Write Domain
    property p_strict_no_overflow;
        @(posedge wclk) disable iff (!wrst_n)
        wfull |-> !wr_en;
    endproperty
    assert_no_overflow: assert property (p_strict_no_overflow)
        else $error("[FATAL_SIZING_FAILURE]: Asynchronous FIFO overflowed! Depth was insufficient!");

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】ระบบกล่องดำบันทึกข้อมูลการบินของเครื่องบินขับไล่ (Avionics Crash Recorder)
เกิดข้อมูลเซนเซอร์เรดาร์สูญหาย (Data Drop) ในระหว่างการทดสอบบินท่าผาดแผลง 9-G Turn
จากการคำนวณขนาด Asynchronous FIFO โดยละเลย Synchronizer Latency
================================================================================
```

#### บริบทของระบบ (System Context):
บริษัทพัฒนาอุปกรณ์อิเล็กทรอนิกส์การบินทางทหาร พัฒนากล่องบันทึกข้อมูลการบินความเร็วสูง (Crash-Survivable Memory Unit - CSMU) บน FPGA เกรดทหาร Xilinx Kintex-7:
* ข้อมูลเรดาร์ AESA ถูกยิงออกมาเป็น Burst ในสภาวะล็อกเป้าหมาย: ความถี่ $f_w = 200\text{ MHz}$ ($T_w = 5.0\text{ ns}$), ขนาด Burst = $256\text{ คำ}$
* หน่วยความจำแฟลชคอนโทรลเลอร์ฝั่งอ่านทำงานที่: ความถี่ $f_r = 66.67\text{ MHz}$ ($T_r = 15.0\text{ ns}$)
* ระหว่างสองโดเมนมี Asynchronous FIFO คั่นกลาง
* วิศวกรคำนวณขนาด FIFO โดยใช้สูตรลบอัตราความเร็วปกติ:
  $$N_{read} = 256 \times \frac{5.0\text{ ns}}{15.0\text{ ns}} \approx 85.3\text{ คำ}$$
  $$Depth_{min} = 256 - 85 = 171\text{ คำ} \implies \text{วิศวกรจึงเลือกใช้ } \mathbf{Depth = 256\text{ คำ}}$$

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
ในการทดสอบบินขับไล่จริงเมื่อเครื่องบินทำท่าเลี้ยวหักศอกด้วยแรงเหวี่ยงหนีศูนย์กลาง $9\text{-G}$ (High-G Maneuver) และเรดาร์ตรวจจับเป้าหมายหลายจุดพร้อมกัน: เมื่อนำกล่องบันทึกข้อมูลมาเปิดอ่าน พบว่า **ข้อมูลวิถีการบินของเรดาร์ขาดหายไปเป็นช่วงๆ (Packet Truncation)** ข้อมูลสำคัญในเสี้ยววินาทีวิกฤตสูญหาย ส่งผลให้การประเมินประสิทธิภาพเรดาร์ล้มเหลว กองทัพสั่งระงับการส่งมอบเครื่องบินทั้งล็อต!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมข้อมูลเรดาร์ในกล่องบันทึกข้อมูลจึงขาดหายไป?**
   * *เพราะ FIFO ส่งสัญญาณ `wfull` ขึ้นมาตัดทราฟฟิก และข้อมูลคำที่เกินมาถูกทำลายทิ้ง*
2. **ทำไม FIFO จึงเต็มเร็ว ทั้งที่คำนวณไว้ว่าต้องการความจุเพียง 171 คำ และใช้ขนาด 256 คำแล้ว?**
   * *เพราะในความเป็นจริง ฝั่งอ่านไม่ได้เริ่มอ่านตั้งแต่คำแรก แต่เริ่มอ่านช้ากว่านั้นมาก ทำให้ระบายข้อมูลออกไปได้เพียง 55 คำ (แทนที่จะเป็น 85 คำตามที่คำนวณไว้)*
3. **ทำไมฝั่งอ่านจึงระบายข้อมูลออกไปได้น้อยกว่าที่คำนวณไว้ถึง 30 คำ?**
   * *เพราะฝั่งอ่านต้องรอเวลา $T_{empty\_deassert}$ นานถึง $50\text{ ns}$ (กว่าสัญญาณ Gray Code จะผ่าน 2-FF Sync) และเมื่ออ่านคำแรกออกไป ฝั่งเขียนก็ต้องรออีก $35\text{ ns}$ กว่าจะรู้ว่ามีพื้นที่ว่าง*
4. **ทำไมความหน่วงเวลาของตัวซิงโครไนซ์จึงส่งผลรุนแรงขนาดนี้?**
   * *เพราะสัญญาณนาฬิกาของฝั่งอ่านช้ากว่าฝั่งเขียนถึง 3 เท่า ($15\text{ ns}$ vs $5\text{ ns}$) ทุกๆ 1 ไซเคิลที่ฝั่งอ่านหน่วงเวลา ฝั่งเขียนจะยิงข้อมูลพุ่งเข้ามาถึง 3 คำ!*
5. **ทำไมวิศวกรจึงใช้สูตรคำนวณแบบ Synchronous มาใช้กับ Asynchronous FIFO?**
   * *เพราะวิศวกรขาดความเข้าใจเรื่อง Pessimistic Synchronization Latency Bounds และไม่เคยได้รับการฝึกอบรมการคำนวณขนาด FIFO ตามมาตรฐาน DO-254!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                         สาเหตุของความล้มเหลว: RADAR FLIGHT DATA OVERFLOW
                         
   METHOD (สูตรการคำนวณขนาด FIFO)              MACHINE (ฮาร์ดแวร์และอัตราส่วนนาฬิกา)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ใช้สูตรลบอัตราเร็วแบบ Synchronous│         │ นาฬิกาต่างกัน 3 เท่า (200M/66M)│
   │ ละเลย Pessimistic Sync Latency │          │ Gray Pointer Sync Delay 50ns   │
   │ คิดว่า Depth = 256 มีมาร์จินพอ │          │ ฝั่งเขียนยิงเร็ว 3 คำต่อรอบอ่าน│
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ขาด SVA ตรวจจับ Overflow ใน Sim │         │ Testbench ไม่เคยยิง Burst 256  │
   │ ขาดการรีวิวแบบ Kenzu เชิงลึก   │          │ ในสภาวะความถี่คลาดเคลื่อน      │
   │ ละเลยคู่มือ DO-254 Hardware Math│         │ ไม่ได้รัน Full-load Corner Sim │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (ข้อกำหนดและการตรวจสอบ)             MEASUREMENT (สภาวะการจำลองระบบ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediations):
1. **คำนวณขนาด FIFO ใหม่โดยใช้สูตรฟิสิกส์แท้จริง:**
   * $T_{burst} = 256 \times 5.0\text{ ns} = 1,280\text{ ns}$
   * $T_{empty\_deassert} = 5.0\text{ ns} + (2 + 1) \times 15.0\text{ ns} = 50.0\text{ ns}$
   * $T_{effective\_read} = 1,280 - 50.0 = 1,230\text{ ns}$
   * $N_{read,actual} = \lfloor 1,230 / 15.0 \rfloor = 82\text{ คำ}$
   * แต่ในสภาวะ Full Flag Pessimistic: เมื่อ FIFO จวนจะเต็ม ฝั่งเขียนต้องหยุดก่อนเวลาจริงเพราะสัญญาณ Full ช้าไปอีก $(2+1) \times 5.0 = 15.0\text{ ns}$
   * ขนาดความลึกที่ปลอดภัยจริงเมื่อคิด Guard Band:
     $$Depth_{min} = 256 - 82 + 16 (\text{Margin}) = 190\text{ คำ}$$
   * เพื่อความปลอดภัยสมบูรณ์แบบ $100\%$ ให้ขยายขนาด FIFO ขึ้นเป็น **$Depth = 512\text{ คำ}$ ($ADDR\_WIDTH = 9$)**
2. **ปรับปรุงการใช้ Block RAM:** เปลี่ยนจาก BRAM แบบ Half-block เป็น 1 ก้อนเต็ม `RAMB36E2` ซึ่งรองรับ 512 คำได้โดยไม่เพิ่มจำนวนชิป
3. **เขียน SVA Assertion:** บังคับให้ตรวจสอบว่าในระหว่างการยิง Burst 256 คำ สัญญาณ `wfull` ต้องไม่ยกขึ้นแม้แต่ไซเคิลเดียว!

#### ใบตรวจสอบมาตรฐาน SOP สำหรับการคำนวณขนาด Async FIFO (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | การคำนวณขนาด FIFO ได้หักลบ $T_{empty\_deassert}$ ออกจากเวลา Burst หรือไม่? | Subtracted Sync Latency | [ ] ผ่าน |
| 2 | มีการบวกค่า Safety Guard Band อย่างน้อย $8 \sim 16\text{ คำ}$ หรือไม่? | Guard Band Added | [ ] ผ่าน |
| 3 | ขนาดความลึกที่เลือกใช้เป็นเลขยกกำลังของสอง ($2^{ADDR\_WIDTH}$) หรือไม่? | Power of 2 | [ ] ผ่าน |
| 4 | มีการวิเคราะห์กรณีเลวร้ายที่สุดที่ฝั่งอ่านติดภาระงาน (Consumer Stalling)? | Worst-Case Read Rate | [ ] ผ่าน |
| 5 | มีการเขียน SVA ยืนยันว่าไม่มีการเกิด Overflow ในสภาวะ Maximum Burst หรือไม่? | Formal Proof Passed | [ ] ผ่าน |
| 6 | ทำการทดสอบ Stress Test ด้วย Burst ข้อมูลต่อเนื่องใน Testbench แล้ว $100\%$? | Verified Full Burst | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | 非同期FIFO容量設計 | ひどうきFIFOようりょうせっけい | Hidōki Faifo yōryō sekkei | Asynchronous FIFO Capacity Sizing |
| 2 | 悲観的遅延限界 | ひかんてきちえんげんかい | Hikanteki chien genkai | Pessimistic Latency Bound |
| 3 | バースト吸収深度 | バーストきゅうしゅうしんど | Bāsuto kyūshū shindo | Burst Absorbing Depth |
| 4 | 読出開始遅延 | よみ出しかいしちえん | Yomidashi kaishi chien | Empty-to-Read Latency ($T_{empty\_deassert}$) |
| 5 | 書込解除遅延 | かきこみかいじょちえん | Kakikomi kaijo chien | Full-to-Write Latency ($T_{full\_deassert}$) |
| 6 | 有効読出時間 | ゆうこうよみだしじかん | Yūkō yomidashi jikan | Effective Read Time ($T_{effective\_read}$) |
| 7 | ガードバンド | ガードバンド | Gādobando | Guard Band / Safety Margin |
| 8 | 速度比不整合 | そくどひふせいごう | Sokudohi fuseigō | Clock Frequency Ratio Mismatch |
| 9 | 最悪バースト長 | さいあくバーストちょう | Saiaku bāsuto-chō | Worst-Case Burst Length ($B_{max}$) |
| 10 | 欠落ゼロ保証 | けつらくゼロほしょう | Ketsuraku zero hoshō | Zero-Data-Loss Guarantee |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ศูนย์พัฒนาอิเล็กทรอนิกส์การบินขั้นสูง (Advanced Avionics Development Center), เมืองกิฟุ (Gifu)  
**ผู้เข้าร่วม:**
* **โยชิดะซัง (Yoshida-san):** หัวหน้าวิศวกรตรวจสอบระบบการบินทหาร (Senior Military Avionics Reviewer / 主幹技師)
* **ปรเมษฐ์ (Poramet):** วิศวกรออกแบบระบบเรดาร์ FPGA (Radar Signal Processing Engineer)

---

**吉田主幹 (Yoshida):**  
「ポラメット君、このフライトレコーダー用非同期FIFOの容量計算書だが、根本的な計算ミスがある。送信側クロック200MHz、受信側66.6MHzで、最大バースト長が256ワードに対して、君はFIFO深度を`256`で十分だと判定しているね。計算式を見ると、単に速度差の比率から`256 - (256 * 66.6/200) = 171`と引いただけだ。なぜシンクロナイザの伝播遅延（Pessimistic Latency）を計算に入れていないのかね？」  
*(Porametto-kun, kono furaitorekōdā-yō hidōki FIFO no yōryō keisansho daga, komponteki na keisan misu ga aru. Sōshin-gawa kurokku 200MHz, jushin-gawa 66.6MHz de, saidai bāsuto-chō ga 256-wādo ni taishite, kimi wa FIFO shindo wo 256 de jūbun da to hantei shite iru ne. Keisanshiki wo miru to, tan ni sokudosa no hiritsu kara 256 - (256 * 66.6/200) = 171 to hiita dake da. Naze shinkuronaiza no dempa chien wo keisan ni irete inai no kane?)*  
**คำแปล:** คุณปรเมษฐ์ ในเอกสารคำนวณความจุ Asynchronous FIFO สำหรับกล่องบันทึกข้อมูลการบินตัวนี้ มีข้อผิดพลาดขั้นรากฐานอยู่นะ ฝั่งส่งความถี่ $200\text{ MHz}$, ฝั่งรับความถี่ $66.6\text{ MHz}$, ขนาด Burst สูงสุด 256 คำ แต่คุณตัดสินว่าความลึก FIFO ขนาด `256` นั้นเพียงพอแล้ว พอดูสูตรคำนวณ คุณแค่เอาอัตราส่วนความเร็วมาหักลบดื้อๆ ว่า $256 - (256 \times 66.6/200) = 171$ เท่านั้น ทำไมคุณถึงไม่นำความหน่วงเวลาของตัวซิงโครไนซ์ (Pessimistic Latency) มาคิดคำนวณด้วยครับ?

**ポラメット (Poramet):**  
「吉田主幹、計算上は171ワードあれば理論上バーストを吸収できるため、FPGAの2のべき乗制限に合わせて256ワードを割り当てれば、約85ワードものマージンが確保されていると判断いたしました。」  
*(Yoshida-shukan, keisan-jō wa 171-wādo areba riron-jō bāsuto wo kyūshū dekiru tame, FPGA no ni no bekijō seigen ni awasete 256-wādo wo wariatereba, yaku 85-wādo mono mājin ga kakuho sarete iru to handan itashimashita.)*  
**คำแปล:** หัวหน้าโยชิดะครับ ตามการคำนวณต้องการเพียง 171 คำก็ดูดซับ Burst ได้แล้ว ดังนั้นเมื่อปัดเป็นเลขยกกำลังของ 2 ที่ 256 คำ ผมจึงประเมินว่าเรามีมาร์จินสำรองเหลือเฟือถึงเกือบ 85 คำครับ

**吉田主幹 (Yoshida):**  
「それは同期FIFOの考え方だ！非同期FIFOを甘く見てはいかん！受信側はデータが書き込まれた瞬間に読み出せるわけではない。グレイコードが2段シンクロナイザを通過して`rempty`が解除されるまでに、受信側クロックで最低3サイクル（45ns）の遅延がある。その45nsの間に、200MHzの送信側は何ワード書き込む？**9ワードも先行して書き込まれるんだ！** さらにFullフラグの悲観的遅延や受信側の初期応答遅延を足し合わせると、君が思っているマージンなど一瞬で吹き飛んでオーバーフローするぞ！」  
*(Sore wa dōki FIFO no kangaekata da! Hidōki FIFO wo amaku mite wa ikan! Jushin-gawa wa dēta ga kakikomareta shunkan ni yomidaseru wake dewa nai. Gurei kōdo ga 2-dan shinkuronaiza wo tsūka shite rempty ga kaijo sareru made ni, jushin-gawa kurokku de saitei 3-saikuru (45ns) no chien ga aru. Sono 45ns no aida ni, 200MHz no sōshin-gawa wa nan-wādo kakikomu? 9-wādo mo senkō shite kakikomareru n da! Sarani Full furagu no hikanteki chien ya jushin-gawa no shoki ōtō chien wo tashi-awaseru to, kimi ga omotte iru mājin nado isshun de fukitonde ōbāfurō suru zo!)*  
**คำแปล:** นั่นมันวิธีคิดของ Synchronous FIFO ต่างหาก! อย่ามอง Asynchronous FIFO ง่ายเกินไปสิ! ฝั่งรับไม่ได้เริ่มอ่านได้ทันทีที่เขียนเสร็จเสียหน่อย กว่ารหัสเกรย์จะผ่าน 2-FF Sync จน `rempty` ปลดตัวลง มันต้องใช้เวลาอย่างน้อย 3 ไซเคิลของฝั่งรับ (45 ns) ในช่วงเวลา 45 ns นั้น ฝั่งส่งที่วิ่ง 200 MHz มันยิงข้อมูลเข้ามาเท่าไหร่แล้ว? **มันยิงแซงเข้ามาตั้ง 9 คำแล้วนะ!** ยิ่งไปกว่านั้น ถ้านำความหน่วงของ Full Flag และความหน่วงการตอบสนองของฝั่งรับมารวมกัน มาร์จินที่คุณคิดว่ามีมันจะปลิวหายไปในพริบตาจนเกิด Overflow แน่นอน!

**ポラメット (Poramet):**  
「ハッ……！空フラグ解除の遅延によって、受信側が読み出しを開始できる有効時間が削られることの恐ろしさを痛感いたしました……！256深度では、実機での高G旋回時のジッタや位相変動に耐えられません！」  
*(Ha'... Kara-furagu kaijo no chien ni yotte, jushin-gawa ga yomidashi wo kaishi dekiru yūkō jikan ga kezurareru koto no osoroshisa wo tsūkan itashimashita...! 256-shindo dewa, jikki de no kō-G senkai-ji no jitta ya isō hendō ni taeraremasen!)*  
**คำแปล:** อึก...! ผมตระหนักถึงความน่ากลัวของการที่เวลาอ่านจริงถูกบั่นทอนลงจากความล่าช้าในการปลด Empty Flag แล้วครับ...! ความลึก 256 คำจะไม่สามารถทนทานต่อ Clock Jitter และความแปรปรวนของเฟสตอนเครื่องบินเลี้ยวหักศอก 9-G ในสภาพจริงได้อย่างแน่นอนครับ!

**吉田主幹 (Yoshida):**  
「そうだ。Block RAM（RAMB36E2）の物理リソースを見れば、512深度に拡張してもBRAMの消費個数は全く変わらない。迷わず**深度512ワード**へ改版し、十分なガードバンドを確保しなさい。修正後、最大バースト256ワードを連続注入して`wfull`が一度も立たないことをSVAアサーションで形式証明してレポートを再提出すること！」  
*(Sō da. Block RAM no butsuri risōsu wo mireba, 512-shindo ni kakuchō shitemo BRAM no shōhi kosū wa mattaku kawaranai. Mayowazu shindo 512-wādo e kaihan shi, jūbun na gādobando wo kakuho shinasai. Shūsei-go, saidai bāsuto 256-wādo wo renzoku chūnyū shite wfull ga ichido mo tatanai koto wo SVA asāshon de keishiki shōmei shite repōto wo sai-teishutsu suru koto!)*  
**คำแปล:** ถูกต้อง หากดูทรัพยากร Block RAM ทางกายภาพ การขยายเป็น 512 คำไม่ได้เพิ่มจำนวนก้อน BRAM ขึ้นเลยแม้แต่ตัวเดียว จงอย่าลังเล รีบแก้เป็น **ความลึก 512 คำ** เดี๋ยวนี้เพื่อสำรอง Guard Band ให้ปลอดภัย หลังแก้ไขเสร็จ ให้ทดสอบยิง Burst 256 คำต่อเนื่องและพิสูจน์ด้วย SVA Assertion ว่าไม่มีสัญญาณ `wfull` ยกขึ้นแม้แต่ครั้งเดียว แล้วค่อยส่งรายงานมาให้ตรวจใหม่!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณขนาดความลึกขั้นต่ำของ Asynchronous FIFO ภายใต้ Burst Transfer
ในระบบประมวลผลวิดีโอจากเซนเซอร์ดาวเทียม ข้อมูลถูกส่งข้าม Asynchronous FIFO ระหว่าง:
* โดเมนเขียน (Camera Sensor): $f_w = 125\text{ MHz}$ ($T_w = 8.0\text{ ns}$)
* โดเมนอ่าน (Compression Processor): $f_r = 50\text{ MHz}$ ($T_r = 20.0\text{ ns}$)
* ฝั่งเขียนทำการส่งข้อมูลแบบ Burst ติดต่อกันจำนวน $B = 160\text{ คำ}$ โดยไม่มีช่องว่าง (1 word ต่อ 1 cycle ของ $WCLK$)
* ฝั่งอ่านสามารถอ่านข้อมูลได้ต่อเนื่อง 1 คำต่อ 1 cycle ของ $RCLK$ เมื่อมีข้อมูล
* วงจร Synchronizer ใช้แบบ 2-Stage Flip-Flop ($N_{sync} = 2$) ทั้งสองทิศทาง
* ความหน่วงเวลาของสายส่ง Interconnect ข้ามชิป: $t_{prop} = 2.0\text{ ns}$
* ข้อกำหนดความปลอดภัยตามมาตรฐาน DO-254 กำหนดให้บวก Safety Guard Band: $N_{guard} = 4\text{ คำ}$

จงคำนวณหาค่า **Empty-to-Read Latency ($T_{empty\_deassert}$)**, จำนวนคำที่ฝั่งอ่านระบายออกได้ทัน ($N_{read}$), ขนาดความลึกขั้นต่ำสุดทางทฤษฎี ($Depth_{min}$), และ **ขนาดความลึกจริงที่ต้องสังเคราะห์ลง FPGA ($Depth_{actual}$)**!

---

#### ตัวเลือก:
* **ก)** $T_{empty\_deassert} = 70.0\text{ ns}$, $N_{read} = 60\text{ คำ}$, $Depth_{min} = 104\text{ คำ}$, $Depth_{actual} = 128\text{ คำ}$
* **ข)** $T_{empty\_deassert} = 70.0\text{ ns}$, $N_{read} = 60\text{ คำ}$, $Depth_{min} = 104\text{ คำ}$, $Depth_{actual} = 256\text{ คำ}$
* **ค)** $T_{empty\_deassert} = 48.0\text{ ns}$, $N_{read} = 64\text{ คำ}$, $Depth_{min} = 100\text{ คำ}$, $Depth_{actual} = 128\text{ คำ}$
* **ง)** $T_{empty\_deassert} = 70.0\text{ ns}$, $N_{read} = 40\text{ คำ}$, $Depth_{min} = 124\text{ คำ}$, $Depth_{actual} = 256\text{ คำ}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การคำนวณระยะเวลา Empty-to-Read Latency ($T_{empty\_deassert}$):
$$T_{empty\_deassert} = T_w + t_{prop} + (N_{sync} + 1) \cdot T_r$$
แทนค่าตัวเลข ($T_w = 8.0\text{ ns}$, $t_{prop} = 2.0\text{ ns}$, $N_{sync} = 2$, $T_r = 20.0\text{ ns}$):
$$T_{empty\_deassert} = 8.0\text{ ns} + 2.0\text{ ns} + (2 + 1) \times 20.0\text{ ns} = 10.0\text{ ns} + 60.0\text{ ns} = 70.0\text{ ns}$$

##### 2. การคำนวณเวลารวมของ Burst ($T_{burst}$) และเวลาที่ใช้อ่านจริง ($T_{effective\_read}$):
* เวลารวมที่ฝั่งเขียนยิงข้อมูล 160 คำ:
  $$T_{burst} = B \times T_w = 160 \times 8.0\text{ ns} = 1,280.0\text{ ns}$$
* เวลาที่ฝั่งอ่านเริ่มอ่านได้จริง:
  $$T_{effective\_read} = T_{burst} - T_{empty\_deassert} = 1,280.0\text{ ns} - 70.0\text{ ns} = 1,210.0\text{ ns}$$

##### 3. การคำนวณจำนวนคำที่ฝั่งอ่านระบายออกได้ทัน ($N_{read}$):
$$N_{read} = \left\lfloor \frac{T_{effective\_read}}{T_r} \right\rfloor = \left\lfloor \frac{1,210.0\text{ ns}}{20.0\text{ ns}} \right\rfloor = \lfloor 60.5 \rfloor = 60\text{ คำ}$$

##### 4. การคำนวณขนาดความลึกขั้นต่ำ ($Depth_{min}$) และขนาดจริง ($Depth_{actual}$):
$$Depth_{min} = B - N_{read} + N_{guard} = 160 - 60 + 4 = 104\text{ คำ}$$
ปรับขนาดขึ้นเป็นเลขยกกำลังของ 2 ($2^N$):
$$Depth_{actual} = 2^{\lceil \log_2(104) \rceil} = 2^7 = 128\text{ คำ}$$

ดังนั้น FIFO ขนาด $Depth = 128\text{ คำ}$ มีความจุเพียงพอรองรับ Burst นี้ได้อย่างปลอดภัยสมบูรณ์แบบ!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** คำนวณ $Depth_{min} = 104$ ถูกต้อง แต่ปัดขึ้นเกินความจำเป็นเป็น 256 คำ ทั้งที่ $128 \ge 104$
* **ข้อ ค):** คิดเวลา Synchronizer ผิดพลาดโดยลืมบวก 1 ไซเคิลสำหรับ Asynchronous Edge Alignment
* **ข้อ ง):** คำนวณจำนวนคำที่อ่านได้ผิดพลาดอย่างรุนแรง

---

### ข้อที่ 2: การเปรียบเทียบเวลาปลด Full Flag เมื่อความถี่ไม่สมมาตร
พิจารณา Asynchronous FIFO ที่เชื่อมต่อระหว่าง $f_w = 400\text{ MHz}$ ($T_w = 2.5\text{ ns}$) และ $f_r = 40\text{ MHz}$ ($T_r = 25.0\text{ ns}$):
สมมติว่า FIFO ตกอยู่ในสภาวะเต็มพิกัด (`wfull = 1`) และฝั่งเขียนหยุดส่งข้อมูล
ทันทีที่ฝั่งอ่านทำการอ่านข้อมูลออกไป 1 คำที่เวลา $t = 0\text{ ns}$ จงคำนวณหาว่า สัญญาณ `wfull` ในฝั่งเขียนจะ **ปลดการทำงาน (`wfull = 0`)** ที่เวลาประมาณกี่นาโนวินาที? (กำหนดให้ $N_{sync} = 2$ และตัด $t_{prop}$ ทิ้ง)

---

#### ตัวเลือก:
* **ก)** $7.5\text{ ns}$ ถึง $10.0\text{ ns}$
* **ข)** $32.5\text{ ns}$ ถึง $35.0\text{ ns}$
* **ค)** $82.5\text{ ns}$ ถึง $85.0\text{ ns}$
* **ง)** $105.0\text{ ns}$ ถึง $110.0\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **การเคลื่อนที่ของข้อมูลในฝั่งอ่าน:**
   * คำสั่งอ่านเกิดขึ้นที่ขอบ $RCLK$ พอยน์เตอร์ `rptr_gray` ใช้เวลา 1 รอบของ $RCLK$ ในการอัปเดตและมีผลที่ขาออกของรีจิสเตอร์:
     $$T_{read\_update} = 1 \cdot T_r = 25.0\text{ ns}$$
2. **การเดินทางผ่าน Synchronizer ในฝั่งเขียน ($WCLK = 400\text{ MHz}$):**
   * สัญญาณ `rptr_gray` เดินทางเข้าสู่ 2-FF Synchronizer ในโดเมน $WCLK$ ซึ่งต้องใช้เวลา:
     $$t_{sync\_w} = (N_{sync} + 1) \cdot T_w = (2 + 1) \times 2.5\text{ ns} = 3 \times 2.5\text{ ns} = 7.5\text{ ns}$$
   * บวกกับเวลาในการประเมินลอจิกเปรียบเทียบ `wfull_reg`: $\approx 1 \cdot T_w = 2.5\text{ ns}$
3. **ผลรวมเวลา Full-to-Write Deassertion ($T_{full\_deassert}$):**
   $$T_{full\_deassert} = T_r + (N_{sync} + 1) \cdot T_w + T_w = 25.0\text{ ns} + 7.5\text{ ns} + 2.5\text{ ns} = 35.0\text{ ns}$$
   *(กรอบความผันผวนของ Asynchronous Edge อยู่ระหว่าง $32.5\text{ ns} \sim 35.0\text{ ns}$)*

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** คิดเฉพาะเวลาของ 2-FF ในฝั่งเขียน ($7.5\text{ ns}$) โดยลืมคิดคาบเวลาของฝั่งอ่าน ($25.0\text{ ns}$)
* **ข้อ ค):** คำนวณสลับกันโดยนำ $N_{sync}$ ไปคูณกับ $T_r$ แทนที่จะคูณกับ $T_w$
* **ข้อ ง):** เผื่อเวลาซ้ำซ้อนเกินจริง

---

### ข้อที่ 3: พฤติกรรมเมื่อฝั่งอ่านมีอัตราการอ่านไม่ต่อเนื่อง (Throttled Consumer)
หากในระบบเดิมจากข้อ 1 ฝั่งอ่านไม่ได้อ่านทุกไซเคิล แต่อ่านได้เพียง **1 คำในทุกๆ 4 ไซเคิลของ $RCLK$** ($M = 4$, $T_{interval} = 4 \times 20\text{ ns} = 80.0\text{ ns}$) ในขณะที่ฝั่งเขียนยังคงยิง Burst 160 คำด้วยความเร็วเต็มพิกัด $125\text{ MHz}$:
ข้อใดต่อไปนี้คือ **ขนาดความลึกขั้นต่ำจริง ($Depth_{actual}$)** ที่จำเป็นต้องใช้?

---

#### ตัวเลือก:
* **ก)** $Depth_{actual} = 128\text{ คำ}$
* **ข)** $Depth_{actual} = 256\text{ คำ}$
* **ค)** $Depth_{actual} = 512\text{ คำ}$
* **ง)** $Depth_{actual} = 64\text{ คำ}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **การคำนวณจำนวนคำที่อ่านได้ใหม่ ($N_{read}$):**
   * เวลาที่มีให้อ่านจริงยังคงเดิมคือ: $T_{effective\_read} = 1,210.0\text{ ns}$
   * คาบเวลาในการอ่านต่อ 1 คำคือ: $M \cdot T_r = 4 \times 20.0\text{ ns} = 80.0\text{ ns}$
   * จำนวนคำที่อ่านออกได้ทัน:
     $$N_{read} = \left\lfloor \frac{1,210.0\text{ ns}}{80.0\text{ ns}} \right\rfloor = \lfloor 15.125 \rfloor = 15\text{ คำ!}$$
2. **การคำนวณความจุขั้นต่ำ ($Depth_{min}$):**
   $$Depth_{min} = B - N_{read} + N_{guard} = 160 - 15 + 4 = 149\text{ คำ}$$
3. **การปรับขนาดเป็นเลขยกกำลังของสอง ($Depth_{actual}$):**
   เนื่องจาก $149 > 128$ ดังนั้นขนาดความลึก 128 คำจึงไม่เพียงพออีกต่อไป!
   ระบบจะต้องปัดขึ้นเป็น:
   $$\mathbf{Depth_{actual} = 2^{\lceil \log_2(149) \rceil} = 2^8 = 256\text{ คำ}}$$

การคำนวณนี้แสดงให้เห็นว่า เพียงแค่ฝั่งอ่านมีอัตราการประมวลผลช้าลง (Throttling) ขนาดความลึกของ FIFO จะต้องขยายขึ้นเป็นเท่าตัวทันที!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ความจุ 128 คำจะล้นทันทีเพราะรองรับได้เพียง 128 คำ แต่วิกฤตสะสมถึง 149 คำ
* **ข้อ ค):** 512 คำใหญ่เกินความจำเป็น
* **ข้อ ง):** 64 คำไม่เพียงพออย่างสิ้นเชิง
