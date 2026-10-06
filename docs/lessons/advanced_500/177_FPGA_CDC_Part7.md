# Lesson 177: FPGA CDC Part 7 - Multi-Bit Coherency & Reconvergence Hazards (Data Bus Skew, Reconvergent Logic Glitches, Coherency Protocols & Formal Verification)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์ความไม่สอดคล้องกันของข้อมูลหลายบิต (Multi-Bit Coherency Breakdown)
ในระบบดิจิทัลระดับองค์กร ข้อมูลและสัญญาณควบคุมแทบทั้งหมดไม่ได้มีอยู่โดดเดี่ยวในรูปของสัญญาณ 1 บิต แต่ทำงานร่วมกันเป็นกลุ่มก้อน เช่น บัสข้อมูลขนาด $32\text{ บิต}$, เวกเตอร์แอดเดรส, หรือชุดแฟล็กแจ้งเตือนความผิดพลาด (Fault Status Flags):

```
                     นิยามของ DATA COHERENCY ข้ามโดเมนสัญญาณนาฬิกา
                     
      [ CLOCK DOMAIN A (TX) ]                       [ CLOCK DOMAIN B (RX) ]
      
      Status Group:                                 Sampling Clock ตกในจังหวะบัสกำลังเปลี่ยน:
      ┌───────────────────────────┐                 ┌───────────────────────────┐
      │ Fault_OverCurrent = 1'b1  │                 │ Fault_OverCurrent = 1'b1  │
      │ Fault_OverTemp    = 1'b0  │                 │ Fault_OverTemp    = 1'b1  │ (เกิด Phantom Bit!)
      │ Fault_UnderVolt   = 1'b0  │                 │ Fault_UnderVolt   = 1'b0  │
      └───────────────────────────┘                 └───────────────────────────┘
                 ▲                                             ▲
                 │ (ความหมายทางตรรกะ:                          │ (ความหมายพังทลาย:
                 │  "กระแสเกินอย่างเดียว")                     │  "กระแสเกิน และอุณหภูมิเกินพร้อมกัน"
                 │                                             │   ===> เข้าสู่ Safe-State ผิดโหมด!)
```

#### นิยามทางวิศวกรรมของ Coherency (ความสอดคล้องเชิงบริบท):
**Data Coherency (データコヒーレンシ)** คือคุณสมบัติที่รับประกันว่า: *เมื่อกลุ่มสัญญาณที่มีความเกี่ยวข้องกันในเชิงตรรกะถูกส่งข้ามโดเมนนาฬิกา โดเมนปลายทางจะต้องแซมเปิลข้อมูลทั้งกลุ่มนั้นใน **สถานะเวลาเดียวกัน (Same Atomic Temporal State)** เสมอ*

หากเกิดสภาวะที่บิตหนึ่งในกลุ่มถูกแซมเปิลจากสถานะใหม่ (New Value) ในขณะที่อีกบิตหนึ่งถูกแซมเปิลจากสถานะเดิม (Old Value) สภาวะความสอดคล้องจะถูกทำลายลงทันที (**Coherency Violation**) ก่อให้เกิด:
1. **Phantom Value Sampling:** ปลายทางเห็นค่าผสมระหว่างอดีตกับอนาคต ซึ่งไม่เคยเกิดขึ้นจริงในระบบ
2. **Invalid State Transition:** สเตตแมชชีนในโดเมนปลายทางเปลี่ยนสถานะผิดเส้นทาง หรือหลุดเข้าสู่วงจรรอคอยที่ไม่สิ้นสุด (Hang / Deadlock)

---

### 1.2 วิกฤตการณ์ Reconvergence Hazards (อันตรายจากการบรรจบของสัญญาณซิงโครไนซ์)

หนึ่งในข้อผิดพลาดที่แยบยลและตรวจจับยากที่สุดในการออกแบบวงจร CDC คือปรากฏการณ์ **Reconvergence Hazard (再収束ハザード)**:

```
                  กลไกการเกิด RECONVERGENCE HAZARD ข้ามโดเมน CLOCK
                  
    [ DOMAIN A: CLK_TX ]                          [ DOMAIN B: CLK_RX ]
    
                          ┌──────────────┐
                     ┌───►│ 2-FF Sync A  ├──── sig_a_sync ───┐
                     │    └──────────────┘                   │
                     │    (Resolve เร็ว: ไซเคิล N)          ▼
      tx_event ──────┤                                     ┌───┐
                     │    ┌──────────────┐                 │AND├──► rx_trigger
                     └───►│ 2-FF Sync B  ├──── sig_b_sync ─┤   │    (SPURIOUS GLITCH!)
                          └──────────────┘                 └───┘
                          (Resolve ช้า: ไซเคิล N+1)
```

#### กลไกการเกิดความผิดพลาดทางฟิสิกส์ (Cycle-Skew Breakdown):
สมมติว่าสัญญาณ `tx_event` จากโดเมน $CLK_{tx}$ ถูกแยกออกเป็น 2 สาขา และถูกนำมาผ่านวงจร 2-Stage Flip-Flop Synchronizer แยกกันอิสระ ($Sync_A$ และ $Sync_B$) เพื่อส่งไปยังโดเมน $CLK_{rx}$:
1. ในจังหวะที่ `tx_event` เปลี่ยนสถานะจาก $0 \to 1$ ขอบสัญญาณเดินทางมาถึงฟลิปฟล็อปสเตจแรกของทั้ง $Sync_A$ และ $Sync_B$ ในจังหวะที่เฉียดฉิวกับขอบสัญญาณนาฬิกา $CLK_{rx}$
2. ฟลิปฟล็อปตัวแรกของทั้งสองวงจรอาจเกิดสภาวะ Metastable พร้อมกัน!
3. **การคลายตัวของ Metastability ไม่มีความเท่าเทียมกัน (Non-deterministic Resolution):**
   * ฟลิปฟล็อปใน $Sync_A$ อาจมีพลังงานคลายตัวลงอย่างรวดเร็ว ทำให้เอาต์พุตของ $Sync_A$ เปลี่ยนเป็น `1` ใน **ไซเคิลที่ $N$**
   * ฟลิปฟล็อปใน $Sync_B$ อาจใช้เวลาแกว่งนานกว่าเล็กน้อย ทำให้เอาต์พุตของ $Sync_B$ ต้องรอจนถึง **ไซเคิลที่ $N+1$** จึงจะเปลี่ยนเป็น `1`
4. **ผลลัพธ์ที่จุดบรรจบ (Reconvergence Point):**
   ในระหว่างไซเคิลที่ $N$:
   $$\text{sig\_a\_sync} = 1 \quad \text{แต่} \quad \text{sig\_b\_sync} = 0$$
   เกิดความต่างของเวลาขนาด **$1\text{ Full Clock Cycle}$ เต็มๆ!**

```
                         TIMING DIAGRAM OF RECONVERGENCE SKEW
                         
    CLK_RX       : ──/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_
    tx_event     : ──────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    sig_a_sync   : ──────────────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾ (ออกที่ Cycle 2)
    sig_b_sync   : ──────────────────────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾ (ออกที่ Cycle 3)
                                 ├──────┤
                              Cycle-Skew (1 ไซเคิลเต็ม!)
    rx_trigger   : ──────────────/‾‾‾‾‾‾\____________________________ (Glitch กว้าง 1 Cycle!)
                   (หากลอจิกเป็น XOR หรือ Logic สลับขั้ว จะเกิดพัลส์ปลอมทันที!)
```

> [!CAUTION]
> **กฎเหล็กการออกแบบ CDC ข้อห้ามเด็ดขาด (Strict CDC Rule):**
> **"ห้ามซิงโครไนซ์สัญญาณที่สัมพันธ์กันแยกเส้นทาง แล้วนำกลับมารวมกันในประตูลอจิกเดียวกันในโดเมนปลายทางเด็ดขาด!"**
> สัญญาณใดๆ ที่มีฟังก์ชันทางตรรกะสัมพันธ์กัน จะต้องถูกยุบรวม (Consolidated) ให้เสร็จสิ้นในโดเมนต้นทางก่อน แล้วส่งข้ามโดเมนในรูปของ **"สัญญาณรวมเพียง 1 บิต"** หรือส่งผ่านสถาปัตยกรรม **DMUX / Handshake** เท่านั้น!

---

### 1.3 ยุทธศาสตร์การซิงโครไนซ์ Multi-Bit: การเปรียบเทียบเชิงลึก

| หมวดหมู่ของข้อมูล (Data Category) | รูปแบบพฤติกรรม (Behavioral Pattern) | สถาปัตยกรรม CDC ที่ถูกต้อง (Valid CDC Architecture) | สถาปัตยกรรมที่ห้ามใช้เด็ดขาด (Forbidden Architecture) |
|:---|:---|:---|:---|
| **Sequential Counter** (เช่น ตัวนับแอดเดรส FIFO) | ค่าเพิ่มขึ้นทีละ 1 สเตปอย่างต่อเนื่องตามลำดับ | **Gray Code Pointer Synchronizer** (Hamming Distance = 1) | Bit-by-bit 2-FF บน Binary Counter |
| **Quasi-Static Control** (เช่น บัสคอนฟิก, ค่า Gain) | นานๆ เปลี่ยนที แต่ละบิตเปลี่ยนเป็นอิสระ | **Data MUX Synchronizer (DMUX)** หรือ Level Handshake | Bit-by-bit 2-FF ขนานกัน |
| **Non-contiguous Data** (เช่น ค่าพารามิเตอร์ระบบ) | ข้อมูลกระโดดข้ามค่าแบบสุ่ม ไม่เรียงลำดับ | **4-Phase / 2-Phase Handshake CDC** | Gray Code (ไม่สามารถแปลงแบบต่อเนื่องได้) |
| **Streaming High-Rate Data** (เช่น แพ็กเก็ต Ethernet) | ข้อมูลไหลต่อเนื่องทุกไซเคิล แบนด์วิดท์เต็ม | **Dual-Clock Asynchronous FIFO** (LUTRAM / BRAM) | Handshake (Throughput ไม่พอ) |

---

### 1.4 การตรวจจับ Reconvergence ใน Static CDC Checkers (SpyGlass / Questa CDC)

ในกระบวนการพัฒนาชิปความน่าเชื่อถือสูง เครื่องมือตรวจสอบ Static CDC เช่น **Synopsys SpyGlass CDC**, **Siemens Questa CDC**, หรือ **AMD Vivado `report_cdc`** จะมีกฎเฉพาะสำหรับตรวจจับโครงสร้างนี้:

```
                     SPYGLASS / QUESTA CDC VIOLATION CODES
                     
    * Rule CDC_RECONV_DATA : ตรวจพบสัญญาณจากโดเมนเดียวกันที่ถูกซิงโครไนซ์แยก 2-FF 
                             แล้วกลับมารวมกันที่ Data Path ของโดเมนปลายทาง
    * Rule CDC_RECONV_CTRL : ตรวจพบสัญญาณควบคุมแยก 2 สายที่ซิงโครไนซ์แยกกัน 
                             แล้วกลับมารวมกันเข้าขา Control/Enable เดียวกัน
    * Vivado CDC-8         : "Re-convergence of synchronized signals"
```

#### ตัวอย่างโค้ดที่ไม่ปลอดภัย (Anti-Pattern):
```verilog
// โค้ดอันตราย: Reconvergence Hazard บนสัญญาณควบคุมสองตัว
module unsafe_reconvergence (
    input  wire clk_a,
    input  wire mode_a,
    input  wire enable_a,
    
    input  wire clk_b,
    output wire fsm_start_b
);

    // ซิงโครไนซ์แยกกัน 2 ชุด
    (* ASYNC_REG = "TRUE" *) reg mode_sync1, mode_sync2;
    (* ASYNC_REG = "TRUE" *) reg en_sync1, en_sync2;

    always @(posedge clk_b) begin
        mode_sync1 <= mode_a;
        mode_sync2 <= mode_sync1;
        
        en_sync1   <= enable_a;
        en_sync2   <= en_sync1;
    end

    // RECONVERGENCE POINT: นำสัญญาณ 2 เส้นมารวมกันในโดเมน B
    // หาก en_sync2 มาถึงก่อน mode_sync2 จะทำให้ระบบเริ่มทำงานด้วย Mode ผิดพลาด!
    assign fsm_start_b = mode_sync2 & en_sync2;

endmodule
```

#### แนวทางแก้ไขที่ถูกต้องสมบูรณ์แบบ (Senior Consolidation Pattern):
```verilog
// โค้ดที่ปลอดภัย 100%: รวมลอจิกในโดเมน A ให้เสร็จก่อนส่งข้าม!
module safe_consolidated_cdc (
    input  wire clk_a,
    input  wire mode_a,
    input  wire enable_a,
    
    input  wire clk_b,
    output wire fsm_start_b
);

    // รวมลอจิกให้เสร็จในโดเมน A และจัดเก็บใน Register ทันที
    reg combined_trigger_a;
    always @(posedge clk_a) begin
        combined_trigger_a <= mode_a & enable_a;
    end

    // ส่งสัญญาณรวมขนาด 1 บิต ข้ามโดเมนผ่าน 2-FF Synchronizer เพียงชุดเดียว!
    (* ASYNC_REG = "TRUE" *) reg sync1_b, sync2_b;
    always @(posedge clk_b) begin
        sync1_b <= combined_trigger_a;
        sync2_b <= sync1_b;
    end

    assign fsm_start_b = sync2_b; // ปราศจาก Reconvergence Hazard 100%!

endmodule
```

---

### 1.5 SystemVerilog Assertions (SVA) เพื่อตรวจจับ Coherency Violations

```systemverilog
// SVA Verification Suite สำหรับการตรวจสอบความสอดคล้องของบัส (Coherency Protocol)
module coherency_sva_checker #(
    parameter integer DATA_WIDTH = 32
)(
    input wire                  clk_src,
    input wire                  rst_src_n,
    input wire [DATA_WIDTH-1:0] data_bus_src,
    input wire                  data_valid_src,

    input wire                  clk_dst,
    input wire                  rst_dst_n,
    input wire [DATA_WIDTH-1:0] data_bus_dst,
    input wire                  data_valid_dst
);

    // Property 1: ห้ามมีการเปลี่ยนแปลงค่าข้อมูลในขณะที่ Valid ยังคงแอคทีฟ (Atomic Stability)
    property p_atomic_src_data_stable;
        @(posedge clk_src) disable iff (!rst_src_n)
        data_valid_src |=> $stable(data_bus_src);
    endproperty
    assert_src_atomic: assert property (p_atomic_src_data_stable)
        else $error("[COHERENCY_ERROR]: Source data bus mutated during active valid strobe!");

    // Property 2: ข้อมูลที่ปลายทางแซมเปิลได้เมื่อ Valid ขึ้น ต้องตรงกับค่าที่เคยส่งมาจริง (No Intermediate Values)
    // ใน Formal Verification จะโมเดลความสัมพันธ์ของชุดข้อมูลใน Queue
    
endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】ระบบควบคุมอินเวอร์เตอร์มอเตอร์รถยนต์ไฟฟ้า (EV Traction Inverter)
เกิดอาการเบรกกระตุกฉุกเฉินกะทันหัน (Spurious Hard Braking) บนถนนไฮเวย์
จากบั๊ก Reconvergence Hazard บนสัญญาณแจ้งเตือนข้อผิดพลาด (Fault Flags)
================================================================================
```

#### บริบทของระบบ (System Context):
ทีมวิศวกรระบบส่งกำลังยานยนต์ไฟฟ้า พัฒนากล่องควบคุมมอเตอร์ขับเคลื่อน (Traction Inverter ECU) โดยใช้ FPGA เกรดรถยนต์ (AEC-Q100 Xilinx Zynq-7000):
* **Fast Motor Sensor Domain (`clk_pwm`):** ความถี่ $100\text{ MHz}$ ทำหน้าที่สุ่มอ่านกระแสเฟสและอุณหภูมิขดลวดสเตเตอร์
* **Safety Supervisor Domain (`clk_safe`):** ความถี่ $20\text{ MHz}$ ทำหน้าที่ประเมินความปลอดภัยระดับ ASIL-D ตามมาตรฐาน ISO 26262
* สัญญาณความผิดพลาดประกอบด้วย 2 แฟล็ก:
  1. `FAULT_OVERCURRENT`: กระแสลัดวงจร
  2. `FAULT_OVERTEMP`: อุณหภูมิมอเตอร์สูงเกินพิกัด
* สถาปัตยกรรมความปลอดภัยกำหนดว่า: หากเกิด `FAULT_OVERCURRENT` **พร้อมกับ** `FAULT_OVERTEMP` ระบบจะต้องสั่งปลดโหมดเบรกและเข้าสู่สถานะ Free-Wheel Coasting แต่ถ้าเกิด `FAULT_OVERCURRENT` **เพียงตัวเดียวอย่างโดดเดี่ยว** ระบบจะต้องสั่งทำ Dynamic Short-Circuit Braking (Active Short Circuit - ASC) ทันที

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
ในระหว่างการทดสอบวิ่งบนถนนไฮเวย์ที่ความเร็ว $110\text{ km/h}$ เมื่อมอเตอร์มีอุณหภูมิสะสมสูงและเกิดสัญญาณ `FAULT_OVERTEMP = 1` ค้างอยู่ ต่อมาผู้ขับขี่กดคันเร่งแซงอย่างรวดเร็วจนกระแสพุ่งแตะขีดจำกัดเกิด `FAULT_OVERCURRENT = 1`: แทนที่ระบบจะเข้าสู่โหมด Free-Wheel ตามที่ออกแบบไว้ รถยนต์กลับเกิดอาการ **"ล้อกระตุกดึงเบรกอย่างรุนแรง (Violent Spurious Braking)"** กะทันหันเป็นเวลา 50 นาโนวินาที ส่งผลให้รถยนต์เสียการทรงตัว เกือบเกิดอุบัติเหตุชนท้าย!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมระบบจึงสั่งตัดวงจรเป็น Active Short Circuit Braking แทนที่จะเป็น Free-Wheel?**
   * *เพราะโมดูล Safety FSM ในโดเมน 20 MHz ได้รับสถานะชั่วขณะว่า "มี Overcurrent แต่ไม่มี Overtemp" ชั่วคราว*
2. **ทำไม Safety FSM จึงมองเห็นว่าไม่มี Overtemp ทั้งที่สัญญาณ Overtemp ทำงานอยู่ก่อนแล้ว?**
   * *เพราะวิศวกรส่งสัญญาณแฟล็กทั้งสองข้ามโดเมนโดยใช้ 2-FF Synchronizer แยกกันอิสระ และสัญญาณทั้งสองถูกนำมาเข้าประตูลอจิกเปรียบเทียบในโดเมนความปลอดภัย (Reconvergence Point)*
3. **ทำไมสัญญาณที่ซิงโครไนซ์แยกกันจึงทำให้เงื่อนไขตรรกะผิดพลาด?**
   * *เพราะเกิดสภาวะ 1-Cycle Synchronizer Skew ระหว่างตัวซิงโครไนซ์ทั้งสองชุด ทำให้ขอบสัญญาณ Overcurrent ถูกแซมเปิลได้ในไซเคิล $N$ แต่ลอจิกถอดรหัสของ Overtemp ถูก Delay ไปที่ไซเคิล $N+1$ ชั่วขณะ เกิด Window of Incoherency กว้าง $50\text{ ns}$*
4. **ทำไมวิศวกรจึงส่งสัญญาณแยกเส้นทางแทนที่จะรวมสัญญาณ?**
   * *เพราะวิศวกรออกแบบโมดูลแบบแยกอิสระ (Modular Design) โดยมองว่าแฟล็กแต่ละตัวมาจากเซนเซอร์คนละประเภท จึงแยกไฟล์ RTL และนำสัญญาณมารวมกันที่ Top-Level โดยไม่คำนึงถึงฟิสิกส์ของ CDC*
5. **ทำไมการจำลองการทำงาน (Simulation) จึงตรวจไม่พบปัญหานี้?**
   * *เพราะการทำ RTL Simulation แบบธรรมดาใช้สมมติฐาน Zero-Delay หรือค่าหน่วงเวลาคงที่ ทำให้ Synchronizer ทั้งสองชุดคลายตัวพร้อมกันเสมอ จึงไม่เคยเห็นสภาวะ Reconvergence Skew ในโปรแกรมจำลอง!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                         สาเหตุของความล้มเหลว: SPURIOUS HARD BRAKING
                         
   METHOD (สถาปัตยกรรมลอจิก)                   MACHINE (ฟิสิกส์ซิลิคอนและการซิงโครไนซ์)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ใช้ 2-FF แยกกันบนแฟล็กสัมพันธ์ │          │ Non-deterministic Metastability│
   │ เกิด Reconvergence Hazard      │          │ 1-Cycle Synchronizer Skew      │
   │ ขาดการรวมสถานะก่อนส่งข้าม      │          │ ช่วงเวลา Sampling กว้าง 50ns   │
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ขาดการรัน SpyGlass / Questa CDC│          │ RTL Simulation แบบ Zero-delay  │
   │ ละเลยกฎ ISO 26262 ASIL-D CDC   │          │ ไม่ได้ทำ Gate-level Sim พร้อม Jitter│
   │ ขาด SVA Reconvergence Assert  │          │ ขาดการทดสอบ Corner Case สลับเฟส│
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (มาตรฐานและการตรวจสอบ)             MEASUREMENT (การทดสอบและเครื่องมือ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Fixes):
1. **กำจัด Reconvergence ที่จุดกำเนิด (Source-side Consolidation):**
   * นำสัญญาณ Fault Flags ทั้งหมดในโดเมน $100\text{ MHz}$ มาเข้ารหัสเป็น **2-bit Atomic Action Code** หรือสร้าง **Master Fault Strobe** ตัวเดียวในโดเมนต้นทาง
   * บันทึกลง Register ให้เสถียรในโดเมนต้นทาง
2. **ใช้สถาปัตยกรรม DMUX หรือ Gray/Handshake:**
   * ส่งรหัส Fault Code ผ่านบัสที่มีคำสั่ง `set_bus_skew` และส่งสัญญาณ `fault_valid` 1 บิตผ่าน 2-FF Synchronizer
   * ปลายทางในโดเมน $20\text{ MHz}$ จะ Latch ค่า Fault Code ทั้งชุดพร้อมกันในไซเคิลเดียว ปราศจาก Reconvergence Skew $100\%$!
3. **เปิดใช้งานการตรวจจับ Reconvergence ใน Questa CDC / Vivado:**
   ```tcl
   # ตรวจจับ Reconvergence ใน Vivado
   report_cdc -details -severity {Critical Warning} -file cdc_reconv_check.rpt
   ```
   ต้องมั่นใจว่ากฎ **CDC-8 (Re-convergence)** มีจำนวนการละเมิดเป็นศูนย์!

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Multi-Bit Coherency (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | มีสัญญาณที่ซิงโครไนซ์แยกกันแล้วกลับมารวมใน Gate เดียวกันหรือไม่? | **ห้ามมีเด็ดขาด (CDC-8 Zero Violations)** | [ ] ผ่าน |
| 2 | กลุ่มสัญญาณที่มีความสัมพันธ์กัน ถูกรวมลอจิกในโดเมนต้นทางก่อนหรือไม่? | Consolidated at Source | [ ] ผ่าน |
| 3 | บัสข้อมูลหลายบิตใช้ DMUX หรือ Asynchronous FIFO แทน 2-FF หรือไม่? | Coherent Crossing Architecture | [ ] ผ่าน |
| 4 | มีการกำหนดคำสั่ง `set_bus_skew` บนบัสข้อมูลเพื่อจำกัดความต่างของ Delay? | $T_{skew} \le 0.5 \cdot T_{dst}$ | [ ] ผ่าน |
| 5 | รันรายงาน Static CDC Checker (SpyGlass/Questa/Vivado) ผ่านทุกกฎหรือไม่? | Zero Waivers on Reconvergence | [ ] ผ่าน |
| 6 | มีการเขียน SVA ยืนยันว่าข้อมูลปลายทางไม่มีค่า Intermediate Values? | Formal Proof Completed | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | 複数ビットコヒーレンシ | ふくすうビットコヒーレンシ | Fukusū bitto kohīrenshi | Multi-bit Coherency (ความสอดคล้องของข้อมูลหลายบิต) |
| 2 | 再収束ハザード | さいしゅうそくハザード | Saishūsoku hazādo | Reconvergence Hazard |
| 3 | サイクルスキュー | サイクルスキュー | Saikuru sukyū | Cycle-Skew (ความเหลื่อมล้ำระดับรอบสัญญาณนาฬิกา) |
| 4 | アトミック遷移 | アトミックせんい | Atomikku sen'i | Atomic Transition (การเปลี่ยนสถานะแบบเป็นเนื้อเดียว) |
| 5 | 中間状態サンプリング | ちゅうかんじょうたいサンプリング | Chūkan jōtai sanpuringu | Intermediate State / Phantom Sampling |
| 6 | 送信側ロジック集約 | そうしんがわロジックしゅうやく | Sōshin-gawa rojikku shūyaku | Source-side Logic Consolidation |
| 7 | 静的検証ルール違反 | せいてきけんしょうルールいはん | Seiteki kenshō rūru ihan | Static CDC Rule Violation (e.g., CDC-8) |
| 8 | 誤制動 / 誤作動 | ごせいどう / ごさどう | Goseidō / Godōsa | Spurious Braking / Malfunction |
| 9 | 構造的検証 | こうぞうてきけんしょう | Kōzōteki kenshō | Structural CDC Verification |
| 10 | ウェイバー適用基準 | ウェイバーてきようきじゅん | Weibā tekiyō kijun | Waiver Application Criteria (เกณฑ์การอนุโลมข้อผิดพลาด) |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ห้องตรวจสอบระบบยานยนต์อัตโนมัติและความปลอดภัยสูง (Autonomous Driving Functional Safety Review), เมืองโตโยต้า (Toyota City)  
**ผู้เข้าร่วม:**
* **อิชิกาวะซัง (Ishikawa-san):** ผู้จัดการฝ่ายตรวจสอบความปลอดภัยเชิงฟังก์ชัน ASIL-D (Functional Safety Sign-Off Manager / 技監)
* **ศุภกร (Suphakon):** วิศวกรออกแบบระบบควบคุมพลังงานไฟฟ้า (Traction Power Design Engineer)

---

**石川技監 (Ishikawa):**  
「スパコーン君、このインバータ保護回路のCDC設計だが、 questa CDCの静的解析レポートで**CDC-8（再収束ハザード：Reconvergence of Synchronized Signals）**のバイオレーションが出ているのを見逃しているね。過電流フラグと過温度フラグを、それぞれ独立した2段シンクロナイザで受けて、受信ドメインの安全ロジックでAND結合している。この設計が原因で車両が誤制動を起こす危険性について、検討したのかね？」  
*(Supakōn-kun, kono inbāta hogo kairo no CDC sekkei daga, Questa CDC no seiteki kaiseki repōto de CDC-8 (Saishūsoku hazādo: Reconvergence of Synchronized Signals) no baiorēshon ga dete iru no wo minogashite iru ne. Kadenryū furagu to kaon furagu wo, sorezore dokuritsu shita 2-dan shinkuronaiza de ukete, jushin domein no anzen rojikku de AND ketsugō shite iru. Kono sekkei ga gen'in de sharyō ga go-seidō wo okosu kikensei ni tsuite, kentō shita no kane?)*  
**คำแปล:** คุณศุภกร วงจรป้องกันอินเวอร์เตอร์ส่วนนี้ ในรายงาน Static Analysis ของ Questa CDC คุณมองข้ามข้อผิดพลาด **CDC-8 (Reconvergence of Synchronized Signals)** ไปนะ คุณเอาแฟล็ก Overcurrent กับแฟล็ก Overtemp ไปผ่าน 2-FF Synchronizer แยกกันอิสระ แล้วนำมารวมกันผ่าน AND Gate ในโดเมนความปลอดภัยฝั่งรับ คุณได้วิเคราะห์ความเสี่ยงที่การออกแบบนี้จะทำให้รถยนต์เกิดอาการเบรกผิดพลาดบ้างหรือยังครับ?

**スパコーン (Suphakon):**  
「石川技監、それぞれのフラグに対して正しく`ASYNC_REG`付きの2段フリップフロップを配置してメタステーブル対策を施していたため、受信側で論理演算を行っても問題ないと考えておりました。両方の信号が同時にアサートされれば、最終的に正しい安全状態（Free-Wheel）へ移行するはずです。」  
*(Ishikawa-gikan, sorezore no furagu ni taishite tadashiku ASYNC_REG-tsuki no 2-dan furippu-furoppu wo haichi shite metastēburu taisaku wo hodokoshite ita tame, jushin-gawa de ronri enzan wo okonattemo mondai nai to kangaete orimashita. Ryōhō no shingō ga dōji ni asāto sareba, saishūteki ni tadashī anzen jōtai e ikō suru hazu desu.)*  
**คำแปล:** หัวหน้าอิชิกาวะครับ เนื่องจากผมได้ใส่ 2-FF พร้อม `ASYNC_REG` ดักจับ Metastability ให้กับแต่ละสัญญาณอย่างถูกต้องแล้ว ผมจึงคิดว่าการนำมาประมวลผลทางตรรกะในฝั่งรับไม่น่ามีปัญหาครับ หากสัญญาณทั้งสองทำงานพร้อมกัน สุดท้ายระบบก็น่าจะเข้าสู่สภาวะปลอดภัย (Free-Wheel) ได้ถูกต้องครับ

**石川技監 (Ishikawa):**  
「『最終的に』では遅すぎるんだよ！メタステーブルの収束時間は非決定的（Non-deterministic）だ。2つのシンクロナイザの間で**1サイクルのスキュー（Cycle-Skew）**が確率的に必ず生じる。過電流がサイクルNで届き、過温度がサイクルN+1で届いた場合、その間の1サイクル（50ns）だけ『過電流のみ発生』という偽の状態が出力される。その瞬間、ASC（アクティブ・ショート・サーキット）ブレーキのパルスがモーターに誤印加され、高速走行中の車両に激しい衝撃が加わるんだ！ISO 26262のASIL-D審査で即座に不合格になる重大欠陥だよ。」  
*("Saishūteki ni" dewa ososugiru n da yo! Metastēburu no shūsoku jikan wa hi-ketteiteki da. Futatsu no shinkuronaiza no aida de 1-saikuru no sukyū ga kakuritsuteki ni kanarazu shōjiru. Kadenryū ga saikuru N de todoki, kaon ga saikuru N+1 de todoita baai, sono aida no 1-saikuru dake "kadenryū nomi hassei" to iu nise no jōtai ga shutsuryoku sareru. Sono shunkan, ASC burēki no parusu ga mōtā ni go-inka sare, kōsoku sōkō-chū no sharyō ni hageshī shōgeki ga kuwawaru n da! ISO 26262 no ASIL-D shinsa de sokuzani fugōkaku ni naru jūdai kekkan da yo.)*  
**คำแปล:** คำว่า "สุดท้าย" มันช้าเกินไปน่ะสิ! เวลาในการคลายตัวของ Metastability มันคาดเดาไม่ได้ (Non-deterministic) มันจะเกิดความเหลื่อมล้ำขนาด **1 ไซเคิล (Cycle-Skew)** ขึ้นระหว่าง Synchronizer ทั้งสองตัวอย่างแน่นอนในทางสถิติ หาก Overcurrent มาถึงในไซเคิล N แต่ Overtemp มาถึงในไซเคิล N+1 ในช่วงเวลา 1 ไซเคิล (50 ns) นั้น ระบบจะปล่อยค่าลวงว่า "มีเฉพาะ Overcurrent" ออกมา ทันใดนั้น พัลส์คำสั่งเบรกแบบ ASC จะถูกยิงเข้ามอเตอร์ ทำให้รถที่วิ่งความเร็วสูงเกิดการกระตุกอย่างรุนแรง! นี่คือข้อบกพร่องร้ายแรงที่จะทำให้ตกการรับรอง ISO 26262 ASIL-D ในทันทีนะ!

**スパコーン (Suphakon):**  
「ハッ……！受信側での再収束によって、過渡的な中間不正状態が生成されることの恐ろしさを痛感いたしました……！直ちに送信側ドメイン（100MHz）にて保護状態のデコード論理を集約し、単一のステータスバスとしてDMUX構成、または単一のアラートストローブとして同期化するよう回路を根本改版いたします！」  
*(Ha'... Jushin-gawa de no saishūsoku ni yotte, katoteki na chūkan fusei jōtai ga seisei sareru koto no osoroshisa wo tsūkan itashimashita...! Tadachini sōshin-gawa domein nite hogo jōtai no dekōdo ronri wo shūyaku shi, tan'itsu no sutēt ブ basu to shite DMUX kōsei, matawa tan'itsu no arāto sutorōbu to shite dōkika suru yō kairo wo kompon kaihan itashimasu!)*  
**คำแปล:** อึก...! ผมตระหนักถึงความน่ากลัวของการเกิดสภาวะลวงระหว่างกลางจากการบรรจบของสัญญาณในฝั่งรับแล้วครับ...! ผมจะรีบนำตรรกะการถอดรหัสสถานะป้องกันมารวบยอดไว้ในโดเมนส่ง (100 MHz) ให้เสร็จสิ้น แล้วส่งข้ามผ่านโครงสร้าง DMUX หรือรวมเป็น Alert Strobe บิตเดียว เพื่อยกเครื่องสถาปัตยกรรมใหม่ทั้งหมดเดี๋ยวนี้ครับ!

**石川技監 (Ishikawa):**  
「分かってくれたなら良い。車載や人命に関わるシステムでは、1サイクルのグリッチも許されない。修正後はQuesta CDCでCDC-8違反が完全にゼロであることを示し、さらにSVAアサーションで中間状態が絶対に現れないことを形式検証して、エビデンスを検図書に添付しなさい。」  
*(Wakatte kureta nara yoi. Shasai ya jinmei ni kakawaru shisutemu dewa, 1-saikuru no guricchi mo yurusarenai. Shūsei-go wa Questa CDC de CDC-8 ihan ga kanzen ni zero de aru koto wo shimeshi, sarani SVA asāshon de chūkan jōtai ga zettai ni arawarenai koto wo keishiki kenshō shite, ebidensu wo kenzusho ni tempu shinasai.)*  
**คำแปล:** เข้าใจแล้วก็ดีแล้ว ในระบบยานยนต์และระบบที่เกี่ยวข้องกับชีวิตมนุษย์ แม้แต่ Glitch เพียงแค่ไซเคิลเดียวก่อนยอมให้มีไม่ได้ หลังแก้ไขเสร็จ จงแสดงผลว่าข้อผิดพลาด CDC-8 ใน Questa CDC เป็นศูนย์ทั้งหมด และทำ Formal Verification ด้วย SVA ยืนยันว่าจะไม่มี Intermediate State เกิดขึ้นอย่างเด็ดขาด แล้วแนบหลักฐานมาในเล่ม Kenzu ด้วย

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณโอกาสเกิด 1-Cycle Skew ใน Reconvergent Synchronizers
ในระบบความปลอดภัยทางการบิน สัญญาณแจ้งเตือนเซนเซอร์ `sensor_fire` ถูกส่งแยกเข้าสู่วงจร 2-Stage Synchronizer สองชุดคู่ขนาน ($Sync_A$ และ $Sync_B$) ในโดเมนปลายทาง ($f_{dst} = 100\text{ MHz}$, $T_{dst} = 10.0\text{ ns}$):
* การจัดวาง Placer บน FPGA ทำให้สัญญาณวิ่งถึงหน้าขา D ของฟลิปฟล็อปตัวแรกของทั้งสองชุดพร้อมกัน
* หน้าต่างเวลาเสี่ยงที่จะเกิด Metastability ของฟลิปฟล็อปตัวแรกมีขนาดความกว้าง: $T_w = 0.20\text{ ns}$
* เวลาในการคลายตัว (Resolution Time Constant) ของกระบวนการผลิตซิลิคอน: $\tau = 0.15\text{ ns}$
* เวลาที่มีให้ฟลิปฟล็อปตัวแรกคลายตัวก่อนขอบนาฬิกาถัดไป: $T_{slack} = T_{dst} - (T_{co} + T_{setup}) = 10.0 - (0.40 + 0.20) = 9.40\text{ ns}$
* อัตราความถี่ของการเปลี่ยนแปลงสัญญาณเซนเซอร์: $f_{event} = 100\text{ kHz}$ ($10^5\text{ Events/sec}$)

หากนิยาม "1-Cycle Skew Event" คือเหตุการณ์ที่ Synchronizer ตัวหนึ่งคลายตัวได้ทันในไซเคิลแรก ส่วนอีกตัวหนึ่งเกิดสภาวะ Metastable จนหลุดไปคลายตัวในไซเคิลถัดไป ทำให้เอาต์พุตของทั้งสองวงจรมีค่าไม่ตรงกันเป็นระยะเวลา $1\text{ Full Clock Cycle}$ ($10.0\text{ ns}$) จงคำนวณหาค่าความน่าจะเป็นที่การเปลี่ยนสถานะของเซนเซอร์ 1 ครั้งจะเกิด 1-Cycle Skew และคำนวณหาอัตราการเกิดข้อผิดพลาดนี้ใน 1 ปี (Failures Per Year) หากไม่มีการแก้ไขวงจร

---

#### ตัวเลือก:
* **ก)** ความน่าจะเป็น $P_{skew} \approx 4.0 \times 10^{-29}$ ต่อเหตุการณ์ และอัตราความล้มเหลว $\approx 0$ ครั้งต่อปี (ปลอดภัยอย่างยิ่งในทางสถิติ)
* **ข)** ความน่าจะเป็น $P_{skew} \approx 1.25 \times 10^{-2}$ ต่อเหตุการณ์ และเกิดความล้มเหลว $\approx 3.9 \times 10^{10}$ ครั้งต่อปี
* **ค)** ความน่าจะเป็น $P_{skew} \approx 2.0 \times 10^{-2}$ (หรือ $2\%$) ซึ่งเกิดจากช่วงเวลาที่สัญญาณตกใน Window $T_w / T_{dst}$ โดยที่ตัวหนึ่ง Resolve เป็น 0 อีกตัวเป็น 1 ส่งผลให้เกิดความล้มเหลวประมาณ **63 ล้านครั้งต่อปี!**
* **ง)** ความน่าจะเป็น $P_{skew} = 100\%$ ทุกครั้งที่มีการเปลี่ยนสถานะ

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ค)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **ความน่าจะเป็นที่ขอบสัญญาณตกในหน้าต่าง Metastability Window ($P_{hit}$):**
   ขอบสัญญาณ $CLK_{dst}$ และขอบของเหตุการณ์เซนเซอร์เกิดขึ้นโดยไม่สัมพันธ์กัน (Asynchronous):
   $$P_{hit} = \frac{T_w}{T_{dst}} = \frac{0.20\text{ ns}}{10.0\text{ ns}} = 0.020 \quad (2.0\%)$$
2. **การวิเคราะห์การคลายตัวของ Metastability สู่ลอจิก 0 หรือ 1:**
   * เมื่อสัญญาณตกในหน้าต่าง $T_w$ ฟลิปฟล็อปสเตจแรกของทั้ง $Sync_A$ และ $Sync_B$ จะเข้าสู่จุดสมดุลก้ำกึ่ง (Metastable State)
   * เมื่อเวลาผ่านไป $T_{slack} = 9.40\text{ ns}$ ฟลิปฟล็อปทั้งสองจะคลายตัว (Resolve) สู่สถานะที่เสถียรแน่นอน (เนื่องจาก $e^{-9.4/0.15} \approx 0$)
   * **ทว่า ฟิสิกส์ของการคลายตัวเป็นแบบสุ่ม $50/50$ (Fair Coin Toss Physics):**
     * ตัวหนึ่งอาจเอียงตกลงสู่ลอจิก `0` (เหมือนมองไม่เห็นขอบในไซเคิลนี้)
     * อีกตัวหนึ่งอาจเอียงตกลงสู่ลอจิก `1` (มองเห็นขอบในไซเคิลนี้)
   * ความน่าจะเป็นที่ผลลัพธ์ของฟลิปฟล็อปทั้งสองตัวจะคลายตัว **ไม่ตรงกัน (One resolves to 0, other to 1)** คือ:
     $$P(A \ne B) = P(A=1, B=0) + P(A=0, B=1) = (0.5 \times 0.5) + (0.5 \times 0.5) = 0.25 + 0.25 = 0.50$$
3. **ความน่าจะเป็นรวมในการเกิด 1-Cycle Skew ($P_{skew}$):**
   $$P_{skew} = P_{hit} \times P(A \ne B) = 0.020 \times 0.50 = 0.010 \quad (1.0\%)$$
   *(หากพิจารณารวมสภาวะ Random Jitter และ Clock Skew ภายใน Slice ค่า $P_{skew}$ จะอยู่ในช่วง $1.0\% \sim 2.0\%$)*
4. **การคำนวณจำนวนครั้งที่เกิดความล้มเหลวใน 1 ปี:**
   จำนวนเหตุการณ์เซนเซอร์ต่อวินาที: $f_{event} = 100\text{ kHz} = 10^5\text{ เหตุการณ์/วินาที}$
   จำนวนวินาทีใน 1 ปี: $365 \times 24 \times 3600 \approx 3.1536 \times 10^7\text{ วินาที}$
   จำนวนข้อผิดพลาดที่เกิดขึ้นใน 1 ปี:
   $$\text{Failures/Year} = P_{skew} \times f_{event} \times \text{Seconds} = 0.020 \times 10^5 \times 3.1536 \times 10^7 \approx 6.307 \times 10^7 \text{ ครั้ง/ปี!}$$
   **นั่นคือเกิด Glitch มากกว่า 63 ล้านครั้งในแต่ละปี!** นี่คือเหตุผลว่าทำไม Reconvergence Hazard จึงไม่ใช่ปัญหาเชิงทฤษฎี แต่เป็นหายนะที่เกิดขึ้นซ้ำๆ ทุกชั่วโมงในระบบจริง!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** เข้าใจผิดนำสูตร MTBF ของ 2-Stage Synchronizer มาคิด ซึ่งสูตร MTBF ใช้คำนวณความน่าจะเป็นที่ Metastability จะหลุดข้ามไปถึง Stage 2 ไม่ใช่ความน่าจะเป็นที่ Stage 1 จะ Resolve คนละลอจิก!
* **ข้อ ข):** ตัวเลขการคำนวณสับสนของสเกลหน่วยวินาที
* **ข้อ ง):** สมมติว่าทุกขอบจะเกิด Skew ตลอดเวลา ซึ่งเป็นไปไม่ได้เพราะส่วนใหญ่ขอบสัญญาณจะตกนอกหน้าต่าง $T_w$

---

### ข้อที่ 2: การตรวจสอบและขจัดความขัดแย้งเชิงตรรกะใน Questa CDC Violation
เมื่อรันการตรวจสอบ Static CDC ด้วย Questa CDC บนโมดูลอินเตอร์เฟซหน่วยความจำ วิศวกรพบรายงานข้อผิดพลาด:
```
Rule: CDC_RECONV_DATA
Description: Synchronized signals 'mem_rd_ack_sync' and 'mem_wr_ack_sync' reconverge 
             at gate 'arbiter_inst/grant_next_lut' in clock domain 'clk_sys'.
```
ข้อใดต่อไปนี้คือ **แนวทางการแก้ไขทางสถาปัตยกรรม (Architectural Refactoring)** ที่ถูกต้องและปลอดภัยที่สุดตามหลักการ Senior Engineer?

---

#### ตัวเลือก:
* **ก)** ใส่คำสั่ง `waive_cdc -rule CDC_RECONV_DATA` ในไฟล์สคริปต์ เพื่อปิดการแจ้งเตือน
* **ข)** ใส่ Delay Buffer ขนาด 3 ตัวบนสายสัญญาณ `mem_wr_ack_sync` เพื่อให้ความล่าช้าเท่ากัน
* **ค)** ยุบสัญญาณตอบรับในโดเมนหน่วยความจำต้นทางให้กลายเป็นบัสรหัสสถานะร่วม 2 บิต `mem_ack_type[1:0]` หรือส่งสัญญาณรวม `mem_ack_valid` เพียงเส้นเดียวข้ามโดเมน แล้วนำไปถอดรหัสในโดเมน `clk_sys`
* **ง)** เพิ่มจำนวนสเตจของ Synchronizer จาก 2 สเตจ เป็น 5 สเตจบนทั้งสองสายสัญญาณ

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ค)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **สาเหตุของข้อผิดพลาด:**
   การมีสัญญาณ Acknowledge สองตัว (`rd_ack` และ `wr_ack`) ที่ถูกซิงโครไนซ์แยกกัน อาจเกิดสภาวะที่ทั้งสองตัวแสดงผลเป็น `1` พร้อมกันในบางไซเคิลอันเนื่องมาจาก 1-Cycle Synchronizer Skew ทั้งที่ในหน่วยความจำต้นทางไม่เคยเกิดเหตุการณ์ Read และ Write เสร็จพร้อมกัน
   วงจร Arbiter ในโดเมน `clk_sys` ที่รับสัญญาณคู่นี้ไปตัดสินใจ อาจเกิดสภาวะสับสน (Arbitration Deadlock หรือ Double Grant)
2. **การปรับปรุงสถาปัตยกรรม (Source-Side Consolidation):**
   * วิธีแก้ปัญหาที่ถาวรและถูกต้องที่สุดคือการ **เข้ารหัสประเภทของ Acknowledge ให้เสร็จในโดเมนต้นทาง**
   * ใช้สัญญาณ `mem_ack_valid` (1 บิต) เพื่อบอกว่ามีธุรกรรมเสร็จสิ้น และใช้ `mem_ack_cmd` (1 บิต) เพื่อบอกว่าเป็น Read หรือ Write
   * ส่งสัญญาณผ่าน DMUX หรือ Handshake: โดยมี `mem_ack_valid` ผ่าน 2-FF Sync เพียงตัวเดียว และสาย `mem_ack_cmd` เป็น Datapath ที่เสถียร
   * วิธีนี้จะทำให้ปลายทางรับรู้ผลลัพธ์ได้อย่างชัดเจน $100\%$ โดยไม่มีโอกาสเกิดสภาวะ Reconvergence อีกต่อไป!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** การใส่ Waiver ปิดปากเครื่องมือตรวจสอบโดยไม่แก้สาเหตุทางกายภาพ เป็นการละเมิดจรรยาบรรณวิศวกรรมและทิ้งกับดักข้อบกพร่องไว้ในชิป
* **ข้อ ข):** Delay Buffer ไม่สามารถแก้ Synchronizer Cycle-Skew ได้ เพราะ Skew เกิดจากจังหวะการคลายตัวของ Metastability ไม่ใช่ความหน่วงของการเดินสาย
* **ข้อ ง):** การเพิ่มสเตจ Synchronizer ไม่ได้ช่วยลดความน่าจะเป็นของการเกิด 1-Cycle Skew ในสเตจแรก และยังเพิ่ม Latency ของระบบโดยเปล่าประโยชน์

---

### ข้อที่ 3: ข้อจำกัดทางคณิตศาสตร์ของ Gray Code ใน Multi-Bit CDC
ข้อใดต่อไปนี้อธิบาย **ข้อจำกัดพื้นฐานทางคณิตศาสตร์ของรหัสเกรย์ (Gray Code)** ที่ทำให้ไม่สามารถนำมาใช้แทน DMUX หรือ Handshake สำหรับการส่งพารามิเตอร์ทั่วไปข้ามโดเมนนาฬิกาได้อย่างถูกต้อง?

---

#### ตัวเลือก:
* **ก)** รหัสเกรย์ทำงานได้ช้ากว่ารหัสไบนารี 10 เท่า
* **ข)** คุณสมบัติ Hamming Distance = 1 ของรหัสเกรย์ ได้รับการรับประกัน **เฉพาะเมื่อข้อมูลเปลี่ยนค่าตามลำดับเชิงตัวเลขอย่างต่อเนื่องทีละ 1 สเตป ($X \to X+1$ หรือ $X \to X-1$)** เท่านั้น หากเป็นการส่งข้อมูลพารามิเตอร์ทั่วไปที่มีค่ากระโดดข้ามแบบสุ่ม ($X \to Y$) รหัสเกรย์จะมีบิตเปลี่ยนพร้อมกันหลายบิตเหมือนกับรหัสไบนารีทุกประการ
* **ค)** รหัสเกรย์ไม่สามารถสังเคราะห์ลงชิป FPGA ได้ เพราะไม่มีประตูเกตลอจิกที่รองรับ
* **ง)** รหัสเกรย์ใช้พลังงานไฟฟ้าสูงกว่ารหัสไบนารี 100 เท่า

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **คณิตศาสตร์ของรหัสเกรย์:**
   รหัสเกรย์ถูกสร้างขึ้นโดยมีเงื่อนไขว่า สำหรับลำดับตัวเลขที่เรียงติดกัน $N$ และ $N+1$ ค่า Gray Code $G(N)$ และ $G(N+1)$ จะต่างกันเพียง 1 บิตเสมอ
2. **ความล้มเหลวเมื่อนำไปใช้กับ Random Parameter Data:**
   * สมมติว่าพารามิเตอร์ของระบบเปลี่ยนค่าจาก $2$ ($G(2) = 0011_2$) กระโดดไปเป็น $9$ ($G(9) = 1101_2$):
   * คำนวณ Hamming Distance ระหว่าง $0011_2$ และ $1101_2$:
     $$\text{Bit 3: } 0 \to 1 \quad (\text{เปลี่ยน})$$
     $$\text{Bit 2: } 0 \to 1 \quad (\text{เปลี่ยน})$$
     $$\text{Bit 1: } 1 \to 0 \quad (\text{เปลี่ยน})$$
     $$\text{Bit 0: } 1 \to 1 \quad (\text{คงเดิม})$$
     มีบิตเปลี่ยนพร้อมกันถึง **3 บิต! ($Hamming Distance = 3$)**
3. **ข้อสรุปเชิงสถาปัตยกรรม:**
   ดังนั้น Gray Code จึงใช้งานได้กับ **Sequential Pointer / Counter** (เช่นใน Asynchronous FIFO) เท่านั้น **ห้ามนำรหัสเกรย์ไปใช้เพื่อหวังจะแก้ปัญหา CDC ให้กับ General Data Bus หรือ Configuration Register เด็ดขาด!** สำหรับบัสข้อมูลทั่วไป ต้องใช้สถาปัตยกรรม **DMUX**, **Handshake**, หรือ **Async FIFO** เท่านั้น!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ความเร็วของลอจิกแปลง Gray และ Binary ใช้เพียงประตู XOR ระดับตื้น ดีเลย์เพียงเศษเสี้ยวของนาโนวินาที ไม่ได้ช้ากว่า 10 เท่า
* **ข้อ ค):** รหัสเกรย์สังเคราะห์ลง FPGA ได้อย่างมีประสิทธิภาพสูงสุดด้วย LUT ทั่วไป
* **ข้อ ง):** ในทางตรงกันข้าม รหัสเกรย์ช่วยลด Dynamic Switching Power ด้วยซ้ำเพราะมีบิตสลับสถานะน้อยกว่าในตัวนับ
