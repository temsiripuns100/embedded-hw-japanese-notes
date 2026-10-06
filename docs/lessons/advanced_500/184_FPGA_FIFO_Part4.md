# Lesson 184: FPGA FIFO Part 4 - Packet-Based FIFOs & Buffer Rewind Mechanisms (Multi-Frame Buffering, CRC Error Packet Dropping, Cut-Through vs Store-and-Forward & Commit/Rollback Pointer Physics)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์การส่งข้อมูลแบบสตรีมธรรมดา เทียบกับ ข้อมูลแบบแพ็กเก็ต
ในโครงสร้าง FIFO ทั่วไปที่ศึกษาในบทก่อนๆ ข้อมูลจะถูกประมวลผลแบบ **คำต่อคำ (Word-by-Word Streaming)** กล่าวคือ เมื่อมีสัญญาณ `wr_en = 1` ข้อมูลจะถูกบันทึกลงหน่วยความจำทันที และฝั่งอ่านจะสามารถดึงข้อมูลนั้นออกไปใช้งานได้ทันที

ทว่า ในสถาปัตยกรรมระบบสื่อสารและเครือข่ายสมัยใหม่ เช่น Ethernet MAC (IEEE 802.3), PCIe Transaction Layer (TLP), Serial RapidIO, หรือระบบควบคุมยานอวกาศ SpaceWire ข้อมูลจะถูกจัดส่งในรูปของ **กรอบแพ็กเก็ต (Discrete Packet / Frame Boundaries)** ซึ่งประกอบด้วย:
* **Start-of-Packet (SOP):** จุดเริ่มต้นของแพ็กเก็ต
* **Header & Payload:** ส่วนหัวควบคุมและข้อมูลเนื้อหา (ความยาวแปรผันได้ตั้งแต่ $64$ ถึง $9000\text{ ไบต์}$ ใน Jumbo Frame)
* **End-of-Packet (EOP):** จุดสิ้นสุดของแพ็กเก็ต
* **Frame Check Sequence (FCS / CRC-32):** รหัสตรวจสอบความถูกต้องที่ติดอยู่ท้ายสุดของแพ็กเก็ต

```
                 วิกฤตของ FIFO ธรรมดาเมื่อเจอแพ็กเก็ตที่ CRC ผิดพลาด
                 
    Packet Stream : [ SOP ] ──► [ Data Byte 0 .. 1496 ] ──► [ EOP ] ──► [ CRC-32 FAIL! ]
                                                                        ▲
    FIFO ธรรมดา  : ═════════════════════════════════════════════════════╡
                    ข้อมูล 1496 ไบต์แรกถูกปล่อยออกไปให้ระบบประมวลผลแล้ว! │
                    เพิ่งมารู้ว่า "ข้อมูลทั้งหมดเสีย" ที่ไบต์สุดท้าย! ────┘
                    ===> ระบบปลายทางต้องเสียเวลา Flush Pipeline ทิ้ง 
                         และเกิดสภาวะ Pipeline Pollution ขั้นรุนแรง!
```

หากเราใช้ FIFO ทั่วไป ข้อมูลเนื้อหาเกือบทั้งหมดของแพ็กเก็ตจะถูกทะลักส่งต่อไปยังเอนจินประมวลผลปลายทางล่วงหน้าแล้ว และเมื่อตัวตรวจสอบ CRC ที่ท้ายแพ็กเก็ตพบความผิดพลาด ระบบปลายทางจะต้องเขียนโค้ดที่ซับซ้อนมหาศาลเพื่อไล่ตามลบข้อมูลขยะ หรือสั่ง Abort ธุรกรรมที่ค้างท่อ ซึ่งเพิ่มความเสี่ยงต่อการเกิด Deadlock อย่างยิ่ง!

---

### 1.2 สถาปัตยกรรม Commit / Rollback Pointer (Buffer Rewind Physics)

เพื่อแก้ปัญหานี้ สถาปัตยกรรมชั้นสูงของระบบเครือข่ายจะใช้ **Packet-Based FIFO พร้อมกลไก Buffer Rewind (巻き戻し機構)** ซึ่งใช้ระบบพอยน์เตอร์ 3 ตัวในฝั่งเขียน เพื่อให้สามารถ **"ลบทิ้งแพ็กเก็ตที่เสียทิ้งได้ใน 1 ไซเคิล (Single-Cycle Zero-Cost Packet Dropping)"**:

```
               สถาปัตยกรรม COMMIT & ROLLBACK BUFFER REWIND
               
    wptr_committed (ชี้ที่จุดเริ่มต้นของแพ็กเก็ตปัจจุบัน)
         │
         ▼
    ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
    │ D0 │ D1 │ D2 │ D3 │ D4 │ D5 │    │    │    │    │  (SRAM Ring Buffer)
    └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
                                  ▲
                                  │
                             wptr_current (พอยน์เตอร์เขียนจริง เดินหน้าไปเรื่อยๆ)
                             
    [ กรณีที่ 1: CRC PASS (COMMIT) ]
    * wptr_committed <= wptr_current + 1
    * packet_count   <= packet_count + 1
    ===> ข้อมูลทั้งแพ็กเก็ตได้รับการรับรองความถูกต้อง พร้อมให้ฝั่งอ่านดึงไปใช้!
    
    [ กรณีที่ 2: CRC FAIL หรือ ABORT (ROLLBACK / REWIND) ]
    * wptr_current   <= wptr_committed   <=== ดึงพอยน์เตอร์ถอยหลังกลับใน 1 ไซเคิล!
    * packet_count   <= packet_count (ไม่เพิ่ม)
    ===> ข้อมูลขยะ [D0 .. D5] ถูกทับทิ้งในรอบถัดไปทันที ปราศจากต้นทุนเวลา!
```

#### ส่วนประกอบหลักของวงจร Commit / Rollback:
1. **`wptr_current` (Active Write Pointer):** ทำหน้าที่เป็นพอยน์เตอร์เดินหน้าเขียนข้อมูลคำต่อคำลงใน Memory Core ตามปกติในระหว่างที่แพ็กเก็ตกำลังไหลเข้ามา
2. **`wptr_committed` (Committed Checkpoint Pointer):** ทำหน้าที่จำลองสถานะ "จุดคืนค่าปลอดภัยล่าสุด (Safe Checkpoint)" โดยจะชี้อยู่ที่แอดเดรสถัดจากแพ็กเก็ตสุดท้ายที่ผ่านการตรวจสอบ CRC เรียบร้อยแล้ว
3. **`packet_counter`:** ตัวนับจำนวนแพ็กเก็ตที่สมบูรณ์และพร้อมให้อ่าน ฝั่งอ่านจะมองเห็นว่า FIFO "มีข้อมูล" ก็ต่อเมื่อ `packet_counter > 0` เท่านั้น
4. **การดำเนินการ Commit:** เมื่อสัญญาณ `eop = 1` มาถึงพร้อมกับ `crc_pass = 1`:
   $$\text{wptr\_committed} \Leftarrow \text{wptr\_current} + 1$$
   $$\text{packet\_counter} \Leftarrow \text{packet\_counter} + 1$$
5. **การดำเนินการ Rollback (Rewind):** เมื่อพบข้อผิดพลาด `crc_fail = 1` หรือสัญญาณ `abort = 1`:
   $$\text{wptr\_current} \Leftarrow \text{wptr\_committed}$$
   ข้อมูลของแพ็กเก็ตที่เพิ่งเขียนเข้าไปจะถูกยกเลิกเสมือนไม่เคยมีอยู่จริง โดยไม่ต้องเสียเวลาเขียนล้างค่า `0` ลงในหน่วยความจำแม้แต่ไซเคิลเดียว!

---

### 1.3 การเปรียบเทียบเชิงสถาปัตยกรรม: Store-and-Forward เทียบกับ Cut-Through

| ปัจจัยทางวิศวกรรม (Engineering Metric) | Store-and-Forward Switching | Cut-Through Switching |
|:---|:---|:---|
| **จังหวะที่เริ่มอ่านข้อมูลออกได้** | **ต้องรอจนกว่าทั้งแพ็กเก็ตจะเขียนเสร็จสมบูรณ์** และได้รับการ Commit (`rempty = (pkt_cnt == 0)`) | **เริ่มอ่านได้ทันที** ที่ Header หรือ SOP มาถึง โดยไม่ต้องรอให้ถึง EOP |
| **ความหน่วงเวลาของระบบ (Latency)** | สูงมาก: เท่ากับระยะเวลาของทั้งแพ็กเก็ต ($T_{packet} = Length \times T_{clk}$) | **ต่ำมากระดับนาโนวินาที (Ultra-Low Latency):** เพียงไม่กี่ไซเคิล |
| **การกำจัดแพ็กเก็ตที่เสีย (CRC Error)** | **สมบูรณ์แบบ 100%:** แพ็กเก็ตที่เสียจะถูก Rollback ทิ้งใน FIFO ปลายทางจะไม่เคยเห็นขยะ | **ไม่สามารถทิ้งได้:** ต้องแทรก Error Control Symbol (EEDB) ที่ท้ายแพ็กเก็ตเพื่อสั่งให้ปลายทางช่วยทิ้ง |
| **การป้องกัน Buffer Starvation** | ดีเยี่ยม: ข้อมูลในแพ็กเก็ตไหลต่อเนื่องทุกไซเคิลแน่นอน | มีความเสี่ยง: หากฝั่งส่งเกิดสะดุดกลางคัน บัสปลายทางจะเกิด Underflow |
| **การใช้งานในอุตสาหกรรม** | อุปกรณ์เครือข่ายความปลอดภัยสูง, ระบบการบินและอวกาศ | ระบบเทรดหุ้นความเร็วสูง (HFT), Data Center Spine Switches |

---

### 1.4 โค้ดแม่แบบภาษา Verilog ระดับ Senior สำหรับ Packet FIFO with Commit/Rollback

```verilog
// ==============================================================================
// ADVANCED PACKET-BASED SYNCHRONOUS FIFO WITH SINGLE-CYCLE REWIND
// Senior Gold Standard: Commit/Rollback Pointer Management & Multi-Frame Buffering
// ==============================================================================
(* keep_hierarchy = "yes" *)
module packet_fifo_rewind #(
    parameter integer DATA_WIDTH = 64,
    parameter integer ADDR_WIDTH = 10   // Depth = 1024 words
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // Write Port (Packet Stream Interface)
    input  wire                  wr_en,
    input  wire [DATA_WIDTH-1:0] din,
    input  wire                  sop,           // Start of Packet
    input  wire                  eop,           // End of Packet
    input  wire                  pkt_valid_commit, // Assert at EOP if CRC passes
    input  wire                  pkt_abort_rollback, // Assert if CRC fails or Error
    output wire                  full,

    // Read Port
    input  wire                  rd_en,
    output wire [DATA_WIDTH-1:0] dout,
    output wire                  rd_sop,
    output wire                  rd_eop,
    output wire                  empty,

    // Status
    output wire [ADDR_WIDTH:0]   committed_words_count,
    output reg  [7:0]            stored_packet_count
);

    localparam integer DEPTH = 1 << ADDR_WIDTH;

    // Memory array stores Data + SOP bit + EOP bit
    reg [DATA_WIDTH+1:0] mem [0:DEPTH-1];

    reg [ADDR_WIDTH-1:0] wptr_current;
    reg [ADDR_WIDTH-1:0] wptr_committed;
    reg [ADDR_WIDTH-1:0] rptr;

    // -------------------------------------------------------------------------
    // 1. Write Memory & Current Pointer Logic
    // -------------------------------------------------------------------------
    wire write_active = wr_en && !full;

    always @(posedge clk) begin
        if (write_active)
            mem[wptr_current] <= {sop, eop, din};
    end

    // Committed words count represents real available data for reading
    assign committed_words_count = (wptr_committed >= rptr) ? 
                                   (wptr_committed - rptr) : 
                                   (DEPTH - (rptr - wptr_committed));

    // Space available for writing considers uncommitted active words
    wire [ADDR_WIDTH:0] uncommitted_occupancy = (wptr_current >= rptr) ? 
                                                (wptr_current - rptr) : 
                                                (DEPTH - (rptr - wptr_current));
    assign full = (uncommitted_occupancy >= DEPTH - 2);

    // -------------------------------------------------------------------------
    // 2. Commit and Rollback State Machine Logic
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wptr_current    <= {ADDR_WIDTH{1'b0}};
            wptr_committed  <= {ADDR_WIDTH{1'b0}};
            stored_packet_count <= 8'd0;
        end else begin
            if (pkt_abort_rollback) begin
                // ROLLBACK ACTION: Rewind pointer back to safe committed checkpoint in 1 cycle!
                wptr_current <= wptr_committed;
            end else if (write_active && eop && pkt_valid_commit) begin
                // COMMIT ACTION: Finalize current packet, advance committed pointer!
                wptr_current   <= wptr_current + 1'b1;
                wptr_committed <= wptr_current + 1'b1;
                if (!rd_packet_finished)
                    stored_packet_count <= stored_packet_count + 1'b1;
            end else if (write_active) begin
                // Normal word write advance
                wptr_current <= wptr_current + 1'b1;
                if (rd_packet_finished && stored_packet_count > 0)
                    stored_packet_count <= stored_packet_count - 1'b1;
            end else begin
                if (rd_packet_finished && stored_packet_count > 0)
                    stored_packet_count <= stored_packet_count - 1'b1;
            end
        end
    end

    // -------------------------------------------------------------------------
    // 3. Read Domain Logic (Store-and-Forward: Only read when packets exist)
    // -------------------------------------------------------------------------
    assign empty = (stored_packet_count == 0);
    wire read_active = rd_en && !empty;

    reg [DATA_WIDTH+1:0] dout_raw;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rptr     <= {ADDR_WIDTH{1'b0}};
            dout_raw <= {(DATA_WIDTH+2){1'b0}};
        end else if (read_active) begin
            dout_raw <= mem[rptr];
            rptr     <= rptr + 1'b1;
        end
    end

    assign rd_sop = dout_raw[DATA_WIDTH+1];
    assign rd_eop = dout_raw[DATA_WIDTH];
    assign dout   = dout_raw[DATA_WIDTH-1:0];

    wire rd_packet_finished = read_active && rd_eop;

endmodule
```

---

### 1.5 SystemVerilog Assertions (SVA) เพื่อตรวจจับ Pointer Corruption

```systemverilog
// SVA Verification Suite สำหรับการตรวจสอบกลไก Commit/Rollback ใน Packet FIFO
module packet_fifo_sva #(
    parameter integer ADDR_WIDTH = 10
)(
    input wire clk,
    input wire rst_n,
    input wire pkt_abort_rollback,
    input wire [ADDR_WIDTH-1:0] wptr_current,
    input wire [ADDR_WIDTH-1:0] wptr_committed,
    input wire [7:0] stored_packet_count
);

    // Property 1: Rollback Restoration Check
    // When rollback pulses, wptr_current must strictly restore to wptr_committed in next cycle!
    property p_rollback_exact_restore;
        @(posedge clk) disable iff (!rst_n)
        pkt_abort_rollback |=> (wptr_current == $past(wptr_committed));
    endproperty
    assert_rollback_restore: assert property (p_rollback_exact_restore)
        else $error("[FATAL_POINTER_BUG]: Rollback failed to restore wptr_current to checkpoint!");

    // Property 2: Packet Count Consistency Check
    // Stored packet count must never exceed physical capacity limits
    property p_packet_count_sane;
        @(posedge clk) disable iff (!rst_n)
        stored_packet_count <= 8'd128;
    endproperty
    assert_pkt_sane: assert property (p_packet_count_sane)
        else $error("[OVERFLOW]: Stored packet count exceeded safe limits!");

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】เราเตอร์เครือข่ายดาวเทียมวงโคจรต่ำ (LEO Satellite Intersatellite Link)
เกิดอาการหน่วยความจำบัฟเฟอร์ค้างสนิทอย่างถาวร (Permanent Buffer Lockup)
เมื่อเผชิญกับคลื่นรบกวนในอวกาศ จากบั๊ก Ghost Occupancy ในลอจิก Rollback
================================================================================
```

#### บริบทของระบบ (System Context):
สถาบันวิจัยการบินและอวกาศพัฒนาเราเตอร์สื่อสารระหว่างดาวเทียม (Inter-Satellite Optical Link Router) บนชิป FPGA เกรดอวกาศ Microchip RTG4:
* รับส่งแพ็กเก็ตข้อมูลโปรโตคอล CCSDS (Consultative Committee for Space Data Systems) ขนาดความยาวแปรผัน $128 \sim 1024\text{ ไบต์}$
* มี Packet FIFO พร้อมกลไก Rewind ขนาดความลึก $Depth = 4096\text{ คำ}$
* หากแพ็กเก็ตที่รับมาผ่านการคำนวณ CRC-32 ถูกต้อง วงจรจะส่งสัญญาณ `pkt_commit = 1` แต่หากพบ Bit Error จากรังสีคอสมิก จะส่งสัญญาณ `pkt_rollback = 1` เพื่อลบแพ็กเก็ตทิ้ง
* วิศวกรออกแบบตัวนับคำสะสมใน FIFO (`total_word_count`) โดยเขียนสมการอัปเดตดังนี้:
  ```verilog
  always @(posedge clk) begin
      if (wr_en) count <= count + 1'b1; // บวกคำสะสมทุกครั้งที่เขียน!
      if (rd_en) count <= count - 1'b1;
  end
  ```

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
เมื่อดาวเทียมถูกยิงขึ้นสู่วงโคจรระดับต่ำ (LEO) และเริ่มส่งข้อมูลผ่านช่องสัญญาณเลเซอร์: ในช่วงที่ดาวเทียมบินผ่านเขตความปั่นป่วนของสนามแม่เหล็กโลก (South Atlantic Anomaly - SAA) ซึ่งมีอนุภาคพลังงานสูงรบกวนจนเกิด CRC Error ติดต่อกันหลายสิบแพ็กเก็ต: เราเตอร์เกิดอาการ **"หยุดส่งต่อข้อมูลโดยสิ้นเชิง (Total Traffic Freeze)"** บัฟเฟอร์ FIFO ฟ้องสัญญาณ `full = 1` ค้างเติ่งอย่างถาวร แม้ว่าจะไม่มีการส่งข้อมูลเข้ามาอีกแล้ว และการสั่งอ่านก็ทำไม่ได้เพราะไม่มีแพ็กเก็ตที่สมบูรณ์ กลายเป็นดาวเทียมตาบอด (Silent Satellite) ตัดขาดจากการสื่อสาร!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมเราเตอร์ดาวเทียมจึงหยุดส่งต่อข้อมูลอย่างถาวร?**
   * *เพราะ Packet FIFO ส่งสัญญาณ `full = 1` ค้างไว้ตลอดเวลา ทำให้ไม่ยอมรับแพ็กเก็ตใหม่เข้ามาอีกเลย*
2. **ทำไม FIFO จึงส่งสัญญาณ Full ค้าง ทั้งที่ในหน่วยความจำไม่มีข้อมูลจริงเหลืออยู่?**
   * *เพราะตัวนับจำนวนข้อมูล `total_word_count` มีค่าเท่ากับ 4096 (เต็มพิกัด) อย่างถาวร (เกิดอาการ Ghost Occupancy Lockup)*
3. **ทำไมตัวนับ `total_word_count` จึงสะสมค่าจนเต็ม ทั้งที่แพ็กเก็ตถูกลบทิ้งไปแล้ว?**
   * *เพราะทุกครั้งที่แพ็กเก็ตเสียถูกเขียนเข้ามา ตัวนับจะนับเพิ่มขึ้นทีละ 1 คำ (`count <= count + 1`) แต่เมื่อเกิดสัญญาณ Rollback พอยน์เตอร์เขียน `wptr_current` ถูกดึงถอยหลังกลับจริง ทว่าวิศวกร **ลืมลบตัวเลขคำของแพ็กเก็ตที่ถูกทิ้งออกจากตัวนับ `count`**!*
4. **ทำไมวิศวกรจึงลืมหักลบจำนวนคำออกจากตัวนับ `count` ตอน Rollback?**
   * *เพราะวิศวกรเข้าใจผิดว่าตัวนับ `count` ผูกติดอยู่กับระยะห่างของพอยน์เตอร์โดยอัตโนมัติ และไม่ตระหนักว่าตนเองเขียนตัวนับแบบแยกต่างหาก (Independent Accumulator Counter) โดยไม่ได้นำขนาดของแพ็กเก็ตที่ถูกทิ้ง (`packet_len`) มาหักลบออก*
5. **ทำไมการทดสอบภาคพื้นดิน (Ground Testing) จึงตรวจไม่พบปัญหานี้?**
   * *เพราะในการทดสอบในห้องปฏิบัติการ วิศวกรยิงเฉพาะแพ็กเก็ตที่สมบูรณ์ $100\%$ (Gold Stimulus) เพื่อวัดค่าความเร็ว และไม่เคยจำลองการฉีดสัญญาณรบกวน (Noise & CRC Fault Injection) ที่ทำให้เกิด Rollback ต่อเนื่องหลายสิบครั้งเลย!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                         สาเหตุของความล้มเหลว: GHOST OCCUPANCY BUFFER LOCKUP
                         
   METHOD (การคำนวณตัวนับ Occupancy)          MACHINE (ฮาร์ดแวร์และสภาพแวดล้อมอวกาศ)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ลืมหักลบคำในจังหวะ Rollback    │          │ สัญญาณรบกวนในย่าน SAA สูง      │
   │ ใช้ Accumulator Counter แยก    │          │ เกิด CRC Error ต่อเนื่องหลายสิบครั้ง│
   │ ขาดสมการคำนวณจากระยะห่างพอยน์เตอร์│      │ ตัวนับสะสมตัวเลขขยะจนแตะ 4096   │
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ Ground Test ยิงเฉพาะ Good Packet│         │ ไม่เคยทำ Error Injection Test  │
   │ ละเลยคู่มือ SpaceWire ECSS     │          │ ไม่มี SVA ตรวจจับ Ghost Lockup │
   │ ตรวจแบบ Kenzu ขาดการจำลอง Fault│          │ ไม่ได้จับตาดูค่า wptr vs count │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (ข้อกำหนดและการตรวจสอบ)             MEASUREMENT (สภาวะการทดสอบระบบ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediations):
1. **กำจัดตัวนับอิสระ Accumulator Counter ทิ้ง:** เปลี่ยนมาคำนวณพื้นที่ใช้งานจาก **ผลต่างของพอยน์เตอร์จริง (Direct Pointer Subtraction)** เสมอ:
   ```verilog
   // แก้ไขเป็นสูตรที่ปลอดภัย 100%: อัปเดตตามตำแหน่งพอยน์เตอร์จริงทันที!
   wire [ADDR_WIDTH:0] true_occupancy = (wptr_current >= rptr) ? 
                                        (wptr_current - rptr) : 
                                        (DEPTH - (rptr - wptr_current));
   assign full = (true_occupancy >= DEPTH - 2);
   ```
   เมื่อเกิด Rollback (`wptr_current <= wptr_committed`) ค่า `true_occupancy` จะหดตัวกลับสู่ขนาดที่แท้จริงในไซเคิลเดียวกันทันที ปราศจากปัญหา Ghost Occupancy อย่างถาวร!
2. **ติดตั้งระบบ Packet Length Tracker:** หากจำเป็นต้องใช้ตัวนับคำสะสม ให้สร้างรีจิสเตอร์บันทึกความยาวของแพ็กเก็ตปัจจุบัน (`current_pkt_len`) และเมื่อเกิด Rollback ให้นำค่านั้นไปหักลบออกจากตัวนับทันที
3. **ปรับปรุง Testbench Verification:** เพิ่มการจำลอง **Continuous Fault Injection** โดยยิง CRC Error สุ่มติดต่อกัน $1000$ ครั้ง เพื่อยืนยันว่าบัฟเฟอร์สามารถฟื้นตัวกลับสู่สภาวะปกติได้ $100\%$

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Packet FIFO (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | การคำนวณ Full/Empty ใช้ผลต่างของพอยน์เตอร์จริง (`wptr - rptr`) หรือไม่? | Direct Pointer Math | [ ] ผ่าน |
| 2 | เมื่อเกิดสัญญาณ Rollback พอยน์เตอร์ `wptr_current` ฟื้นฟูกลับใน 1 ไซเคิล? | Single-Cycle Restoration | [ ] ผ่าน |
| 3 | ตัวนับจำนวนแพ็กเก็ต (`packet_counter`) มีการป้องกัน Underflow หรือไม่? | Saturated / Protected | [ ] ผ่าน |
| 4 | หากแพ็กเก็ตมีความยาวเกินขนาดความจุ FIFO (Oversized Packet) มีวงจรตัดทิ้ง? | Truncation Protection | [ ] ผ่าน |
| 5 | มีการเขียน SVA ยืนยันว่าไม่มีสภาวะ Ghost Occupancy หลังการทำ Rollback? | Formal Property Passed | [ ] ผ่าน |
| 6 | Testbench มีการทดสอบฉีด CRC Error ต่อเนื่องหลายร้อยครั้งแล้วหรือไม่? | Pass Fault Injection Test | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | パケット単位FIFO | パケットたんいFIFO | Paketto tan'i Faifo | Packet-Based FIFO |
| 2 | 巻き戻し機構 | まきもどしきこう | Makimodoshi kikō | Buffer Rewind Mechanism (Rollback) |
| 3 | コミット確定 | コミットかくてい | Komitto kakutei | Transaction Commit |
| 4 | ストア＆フォワード | ストアアンドフォワード | Sutoa ando fowādo | Store-and-Forward Switching |
| 5 | カットスルー転送 | カットスルーてんそう | Kattosurū tensō | Cut-Through Forwarding |
| 6 | ゴースト占有ロック | ゴーストせんゆうロック | Gōsuto sen'yū rokku | Ghost Occupancy Lockup |
| 7 | パケット破棄 | パケットはき | Paketto haki | Packet Dropping / Discarding |
| 8 | チェックサム不一致 | チェックサムふいっち | Chekkusamu fuicchi | Checksum / CRC Mismatch |
| 9 | 境界識別子 | きょうかいしきべつし | Kyōkai shikibetsushi | Boundary Delimiters (SOP / EOP) |
| 10 | 擬似フル状態 | ぎじフルじょうたい | Giji furu jōtai | Spurious / Pseudo Full State |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ศูนย์ปฏิบัติการวิศวกรรมดาวเทียมสื่อสาร (Satellite Communications Engineering Center), เมืองสึกุบะ (Tsukuba)  
**ผู้เข้าร่วม:**
* **มิเนะกิชิซัง (Minegishi-san):** ผู้เชี่ยวชาญอาวุโสด้านความน่าเชื่อถือระบบอวกาศ (Senior Space Systems Reliability Specialist / 技師長)
* **กวิน (Kawin):** วิศวกรออกแบบระบบสื่อสารข้อมูลผ่านดาวเทียม (Satellite Payload FPGA Designer)

---

**峰岸技師長 (Minegishi):**  
「カウィン君、このCCSDSパケットバッファのFIFO設計だが、非常に危険なバグが潜んでいる。RTLを見ると、パケットエラー時に`wptr_current`を`wptr_committed`へ巻き戻す（Rollback）機構を実装しているね。しかし、バッファの空き容量を計算している`fifo_word_count`レジスタの記述を見なさい。書き込み時にインクリメントしているが、ロールバック発生時に破棄されたパケットのワード数を減算していないじゃないか！これでは何が起きるかね？」  
*(Kawin-kun, kono CCSDS paketto baffa no FIFO sekkei daga, hijō ni kiken na bagu ga hisonde iru. RTL wo miru to, paketto erā-ji ni wptr_current wo wptr_committed e makimodosu kikō wo jissō shite iru ne. Shikashi, baffa no aki yōryō wo keisan shite iru fifo_word_count rejisuta no kijutsu wo minasai. Kakikomi-ji ni inkurimento shite iru ga, rōrubakku hassei-ji ni haki sareta paketto no wādo-sū wo gensan shite inai ja nai ka! Kore dewa nani ga okiru kane?)*  
**คำแปล:** คุณกวิน ในการออกแบบ FIFO สำหรับบัฟเฟอร์แพ็กเก็ต CCSDS ตัวนี้ มีบั๊กที่อันตรายมากแฝงอยู่นะ พอตรวจดูโค้ด RTL คุณได้ใส่วงจรย้อนพอยน์เตอร์ (Rollback) จาก `wptr_current` กลับไปที่ `wptr_committed` เมื่อเกิดข้อผิดพลาดขึ้นในแพ็กเก็ตก็จริง แต่ลองดูโค้ดของรีจิสเตอร์ `fifo_word_count` ที่ใช้คำนวณพื้นที่ว่างในบัฟเฟอร์สิ คุณสั่งนับเพิ่มตอนเขียนข้อมูลเข้ามา แต่ตอนเกิด Rollback คุณไม่ได้สั่งลบจำนวนคำของแพ็กเก็ตที่ถูกทิ้งออกไปเลยไม่ใช่หรือ! ถ้าเป็นแบบนี้จะเกิดอะไรขึ้นรู้ไหมครับ?

**カウィン (Kawin):**  
「峰岸技師長、ポインタ自体は正しく前回の確定位置に戻るため、次に受信するパケットは壊れたデータを上書きして正常に格納されます。そのため、カウントレジスタの微小な誤差は、次の読み出し動作が進めば自然に解消されると安易に考えておりました。」  
*(Minegishi-gishichō, pointa jitai wa tadashiku zenkai no kakutei ichi ni modoru tame, tsugi ni jushin suru paketto wa kowareta dēta wo uwagaki shite seijō ni kakunō saremasu. Sono tame, kaunto rejisuta no bishō na gosa wa, tsugi no yomidashi dōsa ga susumeba shizen ni kaishō sareru to an'i ni kangaete orimashita.)*  
**คำแปล:** หัวหน้ามิเนะกิชิครับ เนื่องจากตัวพอยน์เตอร์ได้ถอยกลับไปยังตำแหน่งปลอดภัยเดิมอย่างถูกต้องแล้ว แพ็กเก็ตถัดไปก็จะเขียนทับข้อมูลที่เสียและจัดเก็บได้ตามปกติครับ ผมจึงคิดง่ายๆ ไปว่าความคลาดเคลื่อนเล็กน้อยของตัวนับ `count` คงจะค่อยๆ ปรับคืนสู่ปกติได้เองเมื่อมีการอ่านข้อมูลออกไปครับ

**峰岸技師長 (Minegishi):**  
「自然に解消などされるものか！放射線やノイズで連続して10個のパケットがCRCエラーでロールバックされたらどうなる？物理メモリには1ワードもデータが残っていないのに、`fifo_word_count`だけが加算され続け、あっという間に上限に達して**疑似フル状態（Ghost Full Lockup）**に陥るんだ！一度フルになったら受信回路は新しいパケットを一切受け付けなくなり、しかも読み出し側は正常パケットが存在しないから読み出せず、衛星が軌道上で永久に通信不能（Brick）になるぞ！宇宙機設計で最も恥ずべきデッドロックの典型例だよ！」  
*(Shizen ni kaishō nado sareru mono ka! Hōshasen ya noizu de renzoku shite 10-ko no paketto ga CRC erā de rōrubakku saretara dō naru? Butsuri memori ni wa 1-wādo mo dēta ga nokotte inai noni, fifo_word_count dake ga kasan sare-tsuzuke, atto iu ma ni jōgen ni tasshite giji furu jōtai ni ochīru n da! Ichido furu ni nattara jushin kairo wa atarashī paketto wo issai uketsukenaku nari, shikamo yomidashi-gawa wa seijō paketto ga sonzai shinai kara yomidasezu, eisei ga kidō-jō de eikyū ni tsūshin funō ni naru zo! Uchūki sekkei de mottomo hazubeki deddorokku no tenkeirei da yo!)*  
**คำแปล:** มันจะไปคืนสู่ปกติเองได้ยังไงกันเล่า! ถ้าเกิดรังสีหรือสัญญาณรบกวนทำให้เกิด CRC Error และสั่ง Rollback ติดต่อกันสัก 10 แพ็กเก็ตจะเกิดอะไรขึ้น? ในหน่วยความจำจริงไม่มีข้อมูลเหลืออยู่เลยสักคำเดียว แต่ตัวนับ `fifo_word_count` มันจะบวกสะสมขึ้นไปเรื่อยๆ จนเต็มเพดาน เกิดสภาวะ **Ghost Full Lockup** น่ะสิ! และเมื่อขึ้นสถานะ Full วงจรฝั่งรับก็จะไม่รับแพ็กเก็ตใหม่อีกเลย แถมฝั่งอ่านก็อ่านไม่ได้เพราะไม่มีแพ็กเก็ตที่สมบูรณ์ ดาวเทียมจะกลายเป็นขยะอวกาศที่ขาดการสื่อสารอย่างถาวรไปเลยนะ! นี่คือตัวอย่างคลาสสิกของ Deadlock ที่น่าอับอายที่สุดในการออกแบบยานอวกาศเชียวล่ะ!

**カウィン (Kawin):**  
「背筋が凍る思いです……！独立したカウンタ変数が、ロールバックによって実メモリと乖離し、永久停止を引き起こすシナリオを完全に失念しておりました……！直ちに独立カウンタを廃止し、ポインタ同士の差分から占有量を直接算出する真の安全ロジックへ改修いたします！」  
*(Sesuji ga kōru omoi desu...! Dokuritsu shita kaunta hensuu ga, rōrubakku ni yotte jitsu-memori to kairi shi, eikyū teishi wo hikiokosu shinario wo kanzen ni shitsunen shite orimashita...! Tadachini dokuritsu kaunta wo haishi shi, pointa-dōshi no sabun kara sen'yūryō wo chokusetsu sanshutsu suru shin no anzen rojikku e kaishū itashimasu!)*  
**คำแปล:** ผมรู้สึกขนลุกซู่ไปทั้งตัวเลยครับ...! ผมลืมคิดถึงสถานการณ์ที่ตัวนับอิสระจะผิดเพี้ยนไปจากหน่วยความจำจริงเมื่อเกิด Rollback จนทำให้ระบบค้างถาวรไปอย่างสิ้นเชิงเลยครับ...! ผมจะรีบยกเลิกตัวนับอิสระทิ้งทันที และเปลี่ยนมาคำนวณพื้นที่ใช้งานจากผลต่างของพอยน์เตอร์จริงโดยตรงเพื่อความปลอดภัยสูงสุดเดี๋ยวนี้ครับ!

**峰岸技師長 (Minegishi):**  
「分かればよろしい。ポインタ直結の演算であれば、ロールバックの瞬間に空き容量も1サイクルで完全復帰する。修正後は、Testbenchで100回連続のCRCエラーとロールバックを注入し、その後正常パケットが何事もなく受信できることをSVAで検証して結果を提出したまえ。」  
*(Wakareba yoroshii. Pointa chokketsu no enzan de areba, rōrubakku no shunkan ni aki yōryō mo 1-saikuru de kanzen fukki suru. Shūsei-go wa, Testbench de 100-kai renzoku no CRC erā to rōrubakku wo chūnyū shi, sono nochi seijō paketto ga nanigoto mo naku jushin dekiru koto wo SVA de kenshō shite kekka wo teishutsu shitamae.)*  
**คำแปล:** เข้าใจแล้วก็ดีมาก หากใช้การคำนวณที่ผูกตรงกับพอยน์เตอร์ เสี้ยววินาทีที่ Rollback พื้นที่ว่างจะฟื้นฟูกลับมาใน 1 ไซเคิลทันที หลังแก้ไขเสร็จ ให้ใช้ Testbench ยิง CRC Error และสั่ง Rollback ติดต่อกัน 100 ครั้ง แล้วยืนยันด้วย SVA ว่าระบบสามารถกลับมารับแพ็กเก็ตดีได้ตามปกติโดยไม่มีปัญหา แล้วนำผลมาส่งผม

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การวิเคราะห์และแก้ไขปัญหา Ghost Occupancy ใน Packet FIFO
ในระบบ Packet-Based FIFO ขนาดความจุ $Depth = 1024\text{ คำ}$ ที่มีตัวนับ `packet_length_counter` นับความยาวของแพ็กเก็ตที่กำลังเขียนเข้ามา:
* แพ็กเก็ตที่ 1 มีความยาว $64\text{ คำ}$ เขียนเข้ามาสำเร็จและผ่านการตรวจสอบ CRC (`pkt_commit = 1`)
* แพ็กเก็ตที่ 2 มีความยาว $128\text{ คำ}$ เขียนเข้ามา แต่ที่ท้ายแพ็กเก็ตพบว่า CRC ล้มเหลว วงจรจึงสั่ง `pkt_rollback = 1`

หากระบบใช้ตัวนับความจุรวม `total_words` แยกต่างหาก ข้อใดต่อไปนี้คือ **สมการ RTL การอัปเดตตัวแปรในไซเคิลที่เกิด Rollback** ที่ถูกต้องและป้องกันการเกิด Ghost Occupancy ได้ $100\%$?

---

#### ตัวเลือก:
* **ก)** `total_words <= total_words + 1'b1;`
* **ข)** `total_words <= total_words - packet_length_counter;`
* **ค)** `total_words <= 0;` (รีเซ็ตตัวนับทั้งหมดเป็นศูนย์)
* **ง)** `total_words <= total_words;` (คงค่าเดิมไว้โดยไม่ต้องทำอะไร)

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **พฤติกรรมในระหว่างที่แพ็กเก็ตที่ 2 กำลังเขียนเข้ามา:**
   * ในทุกๆ ไซเคิลที่คำของแพ็กเก็ตที่ 2 ถูกเขียนลงไป ตัวนับ `total_words` ถูกบวกเพิ่มไปทีละ 1 คำเป็นจำนวนทั้งหมด 128 ครั้ง
   * ตัวนับ `packet_length_counter` นับสะสมได้ค่า $128$ คำ
2. **จังหวะที่เกิด Rollback (`pkt_rollback = 1`):**
   * ข้อมูลทั้ง 128 คำของแพ็กเก็ตที่ 2 ถูกยกเลิกและทิ้งไป
   * ดังนั้น ตัวนับ `total_words` จะต้องถูก **หักลบออกด้วยจำนวนคำที่เพิ่งเขียนเข้าไปทั้งหมดของแพ็กเก็ตนี้**:
     $$\text{total\_words} \Leftarrow \text{total\_words} - \text{packet\_length\_counter}$$
   * ซึ่งจะทำให้ `total_words` ลดลงกลับมาอยู่ที่ $64\text{ คำ}$ (เท่ากับขนาดของแพ็กเก็ตที่ 1 ที่ Commit ผ่านไปแล้ว) อย่างถูกต้องสมบูรณ์แบบ!
3. **แนวทางที่ดียิ่งกว่า (Best Practice):**
   การคำนวณ `total_words` จากผลต่างของพอยน์เตอร์โดยตรง (`wptr_committed - rptr`) จะตัดความเสี่ยงของการบวกลบคณิตศาสตร์ผิดพลาดออกไปได้อย่างสิ้นเชิง!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ยิ่งทำให้ตัวเลขนับเกินขึ้นไปอีก
* **ข้อ ค):** การรีเซ็ตเป็นศูนย์จะทำให้ข้อมูลของแพ็กเก็ตที่ 1 (64 คำ) ที่ถูกต้องและยังไม่ได้อ่าน สูญหายไปด้วย
* **ข้อ ง):** การคงค่าเดิมไว้จะทำให้ค่า 128 คำที่เสียยังคงค้างอยู่ในตัวนับ นำไปสู่อาการ Ghost Occupancy ทันที

---

### ข้อที่ 2: การเปรียบเทียบ Latency ระหว่าง Cut-Through และ Store-and-Forward
ในระบบเราเตอร์อีเทอร์เน็ต $10\text{Gbps}$ (AXI4-Stream 64-bit ที่ความถี่ $156.25\text{ MHz}$, ส่งข้อมูลได้ $8\text{ ไบต์}$ ต่อ $1\text{ ไซเคิล}$ คาบเวลา $T_{clk} = 6.40\text{ ns}$):
มีการส่งแพ็กเก็ตอีเทอร์เน็ตขนาดมาตรฐานความยาวสูงสุด $1518\text{ ไบต์}$ ($190\text{ คำ}$ รวมเศษ):
* ในโหมด **Store-and-Forward**: แพ็กเก็ตจะต้องถูกเขียนลง FIFO จนครบทั้ง 190 คำ และผ่านการตรวจสอบ CRC เรียบร้อยแล้ว จึงจะเริ่มส่งข้อมูลคำแรกออกจากพอร์ตเอาต์พุตได้
* ในโหมด **Cut-Through**: แพ็กเก็ตสามารถเริ่มส่งออกจากพอร์ตเอาต์พุตได้ทันทีหลังจากที่ส่วนหัว (Ethernet Header ขนาด 14 ไบต์) ถูกตรวจสอบเสร็จสิ้น ซึ่งใช้เวลาเพียง $4\text{ ไซเคิล}$

จงคำนวณหาค่า **Packet Transmission Latency (เวลาตั้งแต่ไบต์แรกเข้าสู่ FIFO จนกระทั่งไบต์แรกเริ่มออกจาก FIFO)** ของทั้งสองโหมดในหน่วยนาโนวินาที ($ns$)!

---

#### ตัวเลือก:
* **ก)** Store-and-Forward: $1,216.0\text{ ns}$ เทียบกับ Cut-Through: $25.6\text{ ns}$ (Cut-Through เร็วกว่าเกือบ 50 เท่า!)
* **ข)** Store-and-Forward: $500.0\text{ ns}$ เทียบกับ Cut-Through: $50.0\text{ ns}$
* **ค)** ทั้งสองโหมดใช้เวลาเท่ากันคือ $1,216.0\text{ ns}$
* **ง)** Store-and-Forward: $25.6\text{ ns}$ เทียบกับ Cut-Through: $1,216.0\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การคำนวณในโหมด Store-and-Forward:
* จำนวนไซเคิลที่ต้องใช้ในการเขียนแพ็กเก็ตขนาด 1518 ไบต์:
  $$N_{cycles} = \left\lceil \frac{1518\text{ ไบต์}}{8\text{ ไบต์/ไซเคิล}} \right\rceil = \lceil 189.75 \rceil = 190\text{ ไซเคิล}$$
* ความหน่วงเวลาก่อนเริ่มอ่านคำแรกออกได้:
  $$T_{latency,SAF} = 190 \times T_{clk} = 190 \times 6.40\text{ ns} = 1,216.0\text{ ns}$$

##### 2. การคำนวณในโหมด Cut-Through:
* ตัดสินใจส่งต่อได้ทันทีหลังจากตรวจ Header 4 ไซเคิล:
  $$T_{latency,CT} = 4 \times T_{clk} = 4 \times 6.40\text{ ns} = 25.6\text{ ns}$$

##### การประเมินเชิงวิศวกรรม:
โหมด Cut-Through สามารถลดความหน่วงเวลาลงได้จาก **$1.216\text{ ไมโครวินาที}$ เหลือเพียง $25.6\text{ นาโนวินาที}$** (เร็วกว่าเดิมถึง $47.5\text{ เท่า}$!) นี่คือเหตุผลที่ระบบเครือข่ายศูนย์ข้อมูลความเร็วสูงและตลาดหลักทรัพย์ (HFT) จึงยอมรับความเสี่ยงที่จะส่ง Error Symbol ดีกว่าการยอมเสียเวลา $1.2\mu s$ ในโหมด Store-and-Forward!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** ตัวเลขสมมติที่ไม่มีที่มาจากการคำนวณความยาวแพ็กเก็ตจริง
* **ข้อ ค):** ขัดแย้งกับหลักการพื้นฐานของ Cut-Through
* **ข้อ ง):** สลับผลลัพธ์ระหว่างสองโหมด

---

### ข้อที่ 3: ข้อจำกัดของ Packet FIFO เมื่อขนาดแพ็กเก็ตยาวเกินความจุ (Oversized Packet Handling)
หากมีแพ็กเก็ตขนาดยักษ์ (Jumbo Frame หรือ Malformed Packet) ความยาว $2000\text{ คำ}$ พยายามเขียนเข้ามาใน Packet FIFO ที่มีขนาดความจุทางกายภาพ $Depth = 1024\text{ คำ}$ โดยที่สัญญาณ `eop` ยังไม่มาถึง:
การออกแบบวงจร Packet Controller ระดับ Senior Engineer ที่ถูกต้อง **จะต้องมีพฤติกรรมอย่างไร** เพื่อป้องกันระบบพังทลาย?

---

#### ตัวเลือก:
* **ก)** ปล่อยให้เขียนทับข้อมูลเก่าวนรอบไปเรื่อยๆ จนกว่าจะเจอ `eop`
* **ข)** ตรวจจับสภาวะที่ `uncommitted_words >= DEPTH - 2` ก่อนที่จะเจอ `eop` จากนั้นสั่งตัดจบการทำงานฉุกเฉิน (Force Abort), ยกเลิกคำสั่งเขียน, สั่งทำ **Rollback ทันที**, และยิงสถานะเตือนภัย `OVERSIZED_PACKET_DROPPED` เพื่อปกป้องข้อมูลแพ็กเก็ตเดิมที่ Commit อยู่ในบัฟเฟอร์ไม่ให้เสียหาย
* **ค)** ขยายขนาด Block RAM บนชิปแบบไดนามิกโดยอัตโนมัติ
* **ง)** รีเซ็ตสัญญาณนาฬิกาของระบบทั้งหมด

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **อันตรายของ Oversized Packet:**
   หากแพ็กเก็ตมีความยาวเกินขนาดความจุของ FIFO พอยน์เตอร์ `wptr_current` จะวิ่งวนรอบกลับมาไล่กวด `wptr_committed` หรือ `rptr` หากปล่อยให้เขียนต่อ ข้อมูลแพ็กเก็ตที่ดีในอดีตจะถูกเขียนทับจนเสียหายทั้งหมด
2. **กลไก Fail-Safe Protection:**
   * วงจรจะต้องมีตัวตรวจจับขีดจำกัดความยาวสูงสุด (Maximum Transmission Unit - MTU Checker)
   * เมื่อตรวจพบว่าขนาดของแพ็กเก็ตปัจจุบันกำลังจะชนเพดานบัฟเฟอร์ วงจรจะต้องทำการ **Force Rollback ทันที**
   * ข้อมูลส่วนที่เพิ่งเขียนเข้ามาของแพ็กเก็ตยักษ์นี้จะถูกทิ้งไปทั้งหมด
   * ข้อมูลแพ็กเก็ตที่ดีตัวอื่นๆ ที่รอการอ่านอยู่ใน FIFO จะได้รับการปกป้องอย่างปลอดภัย $100\%$!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** นำไปสู่การทำลายข้อมูลแพ็กเก็ตดีที่อยู่ในบัฟเฟอร์อย่างร้ายแรง
* **ข้อ ค):** โครงสร้างฮาร์ดแวร์ FPGA เป็นวงจรกายภาพคงที่ ไม่สามารถงอกขนาด RAM เพิ่มขึ้นเองแบบไดนามิกได้
* **ข้อ ง):** การรีเซ็ตสัญญาณนาฬิกาทั้งระบบเป็นพฤติกรรมที่รุนแรงเกินกว่าเหตุและทำให้ระบบหยุดชะงัก
