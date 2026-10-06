# Lesson 194: FPGA Testbench Part 4 — Functional Coverage & Cross-Coverage Engineering (วิศวกรรมการวัดความครอบคลุมเชิงฟังก์ชันและการทำ Cross-Coverage)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในการพัฒนาฮาร์ดแวร์ระดับมืออาชีพ คำถามที่สำคัญที่สุดไม่ใช่ "เราทดสอบไปกี่ชั่วโมง?" หรือ "รันไปกี่ล้านรอบคล็อก?" แต่คือ **"เรารู้ได้อย่างไรว่าเราทดสอบวงจรอย่างครบถ้วนแล้ว? (How do we know verification is complete?)"**

วิศวกรมือใหม่มักพึ่งพาเฉพาะ **Code Coverage (Line, Branch, Condition, Toggle, FSM State)** ซึ่งเป็นตัววัดที่สะท้อนเพียงว่า *"บรรทัดโค้ด RTL ที่เขียนขึ้นมาถูกสั่งให้ทำงานแล้วหรือยัง"* แต่ Code Coverage มีจุดบอดร้ายแรงที่เรียกว่า **Unimplemented Feature Blindspot**: หากวิศวกรลืมเขียน RTL สำหรับฟังก์ชันใดฟังก์ชันหนึ่งในสเปก Code Coverage ก็ยังคงรายงานว่าได้ 100% เต็มได้!

มาตรฐานอุตสาหกรรม (เช่น ISO 26262 ASIL-D และ DO-254 DAL-A) จึงบังคับใช้ **Functional Coverage (機能カバレッジ)** ซึ่งเป็นการเขียนตัวตรวจวัด (Coverage Monitors) ที่อิงตามเอกสารข้อกำหนด (Design Specification) โดยตรง เพื่อพิสูจน์ว่าพฤติกรรม, ลำดับการทำงาน (Sequences), และการผสมผสานของสถานะ (Cross Combinations) ทั้งหมดเกิดขึ้นจริงในระบบ

```
+--------------------------------------------------------------------------------------------------+
|                  FUNCTIONAL COVERAGE & CROSS-COVERAGE ARCHITECTURAL MODEL                        |
+--------------------------------------------------------------------------------------------------+
                                                                                                    
                  +----------------------------------------------------+                            
                  |              Design Specification Matrix           |                            
                  |    - Protocol States: IDLE, HEADER, PAYLOAD, CRC   |                            
                  |    - Packet Sizes: 64B, 128B, 1518B, Jumbo (9KB)   |                            
                  |    - Backpressure: Immediate, Delayed, Sustained   |                            
                  +----------------------------------------------------+                            
                                            |                                                       
                                            v                                                       
                  +----------------------------------------------------+                            
                  |          SystemVerilog Functional Coverage         |                            
                  +----------------------------------------------------+                            
                     |                                              |                               
                     v                                              v                               
      +-----------------------------+                +-----------------------------+                
      |       Single Coverpoints    |                |        Cross Coverage       |                
      |  cp_state: bins [4 states]  |                |  cross cp_state, cp_size    |                
      |  cp_size : bins [4 sizes]   | =======X======>|  Total Combinations: 16     |                
      |  cp_stall: bins [3 levels]  |                |  - ignore_bins (illegal)    |                
      +-----------------------------+                |  = Effective Bins: 12       |                
                     |                               +-----------------------------+                
                     +----------------------+-----------------------+                               
                                            |                                                       
                                            v                                                       
                  +----------------------------------------------------+                            
                  |              Coverage Metric Engine                |                            
                  |  Cov% = (Sampled Bins / Total Valid Bins) x 100%   |                            
                  |  Target: 100% Coverage Closure Sign-Off            |                            
                  +----------------------------------------------------+                            
```

---

### 1.1 คณิตศาสตร์ของความครอบคลุมและการตัดทอนพื้นที่สถานะ (Coverage Metric & Pruning Mathematics)

#### 1. Coverage Percentage Formula
ความครอบคลุมรวมของ Covergroup ($Cov_{CG}$) คำนวณจากค่าเฉลี่ยถ่วงน้ำหนักของแต่ละ Coverpoint และ Cross:
$$Cov_{CG} = \frac{\sum_{i=1}^{N} W_i \cdot Cov_i}{\sum_{i=1}^{N} W_i} \times 100\%$$
โดยที่ความครอบคลุมของ Coverpoint แต่ละตัว ($Cov_i$) คำนวณจากจำนวน Bins ที่ถูกสัมผัสถึงเกณฑ์ขั้นต่ำ (At-least threshold: $N_{hit} \ge \text{at\_least}$):
$$Cov_i = \frac{\sum_{b \in Bins_i} \mathbf{1}(count(b) \ge at\_least)}{|Bins_{valid\_i}|}$$

#### 2. Cross-Coverage State Space Explosion & Pruning Math
เมื่อเราทำ Cross-Coverage ระหว่างหลายตัวแปร ขนาดของพื้นที่สถานะจะขยายตัวแบบทวีคูณ (Combinatorial Explosion):
$$N_{raw\_cross} = \prod_{k=1}^{M} |Bins(Var_k)|$$
หากมี 3 ตัวแปร: ขนาดแพ็กเก็ต (10 bins), สถานะบัฟเฟอร์ (8 bins), และประเภทข้อผิดพลาด (6 bins) จะได้:
$$N_{raw} = 10 \times 8 \times 6 = 480 \text{ bins}$$

ในทางปฏิบัติ จะมีสถานะผสมบางอย่างที่เป็นไปไม่ได้ตามข้อกำหนดฮาร์ดแวร์ หรือผิดกฎของฟิสิกส์ (Invalid Combinations) เราจึงต้องใช้เทคนิคคณิตศาสตร์ในการตัดทอน (Pruning):
- **Ignore Bins (`ignore_bins`):**
  ตัด Bins ที่ไม่สนใจออกจากตัวหาร (Denominator Pruning) ทำให้ไม่ต้องรันให้โดน:
  $$|Bins_{valid}| = |Bins_{raw}| - |Bins_{ignore}|$$
- **Illegal Bins (`illegal_bins`):**
  นอกจากจะตัดออกจากตัวหารแล้ว หากในระหว่าง Simulation สัญญาณหลุดเข้าไปใน Bin นี้แม้แต่ครั้งเดียว Simulator จะสั่ง **Abort Simulation ทันที (Fatal Runtime Violation)**

#### 3. Transition Bins Math
การตรวจสอบลำดับการเปลี่ยนสถานะ (FSM State Transitions) รองรับการเขียนแบบลูกโซ่:
$$S_{seq} = (A \implies B \implies C)$$
หรือการวนซ้ำแบบไม่กำหนดรอบ:
$$S_{repeat} = (A \implies B [* 3:5] \implies C)$$
จำนวน Bins ที่ถูกสร้างขึ้นจะสอดคล้องกับจำนวนเส้นทางเดิน (Paths) ที่เป็นไปได้ทั้งหมดใน Directed Graph ของ FSM

---

### 1.2 โครงสร้างไวยากรณ์ขั้นสูง: Wildcard, Array Bins & Binsof Intersection

1. **Array Bins (`bins b[]`):** สร้าง Bin แยกเดี่ยวให้กับทุกค่าในช่วงโดยอัตโนมัติ
2. **Wildcard Bins (`wildcard bins`):** ใช้จับคู่บิตที่มี Don't-Care (`x` หรือ `z` หรือ `?`) เหมาะสำหรับตรวจสอบ Address Decode
3. **Cross Pruning with `binsof`:**
   ```systemverilog
   cross cp_pkt_type, cp_pkt_len {
       ignore_bins no_payload = binsof(cp_pkt_type) intersect {READ_REQ} &&
                                binsof(cp_pkt_len) intersect {[2:$]};
   }
   ```

---

### 1.3 RTL & SystemVerilog Code: Master Coverage Model สำหรับ AXI4-Stream Protocol

โค้ดชุดนี้แสดงสถาปัตยกรรมการเก็บ Functional Coverage และ Cross-Coverage ขั้นสูงสำหรับโปรโตคอลสตรีมมิ่งความเร็วสูง

```systemverilog
//=============================================================================
// Module: tb_axi_stream_coverage
// Description: Advanced Functional Coverage & Cross-Coverage Model
// Standards: AMBA AXI4-Stream Protocol Specification / DO-254 DAL-A
//=============================================================================

`timescale 1ns / 1ps

typedef enum bit [2:0] {
    AXI_PKT_STANDARD = 3'b000,
    AXI_PKT_CONTROL  = 3'b001,
    AXI_PKT_EXTENDED = 3'b010,
    AXI_PKT_ERROR    = 3'b100
} axi_pkt_type_e;

typedef enum bit [1:0] {
    STALL_NONE       = 2'b00, // Zero wait states
    STALL_SHORT      = 2'b01, // 1-3 cycles wait
    STALL_BURST      = 2'b10  // > 4 cycles sustained backpressure
} stall_profile_e;

// Coverage Subscriber Class
class AxiStreamCoverageCollector;
    // Sampled Transaction Variables
    axi_pkt_type_e  sample_type;
    int             sample_len;
    int             sample_dest;
    stall_profile_e sample_stall;
    bit             sample_user_err;

    // Covergroup Definition
    covergroup cg_axi_stream @(sample_event);
        option.per_instance = 1;
        option.comment = "AXI4-Stream Protocol Completeness Coverage";

        // Coverpoint 1: Packet Type Coverage
        cp_type: coverpoint sample_type {
            bins std_type = {AXI_PKT_STANDARD};
            bins ctrl_type = {AXI_PKT_CONTROL};
            bins ext_type = {AXI_PKT_EXTENDED};
            bins err_type = {AXI_PKT_ERROR};
        }

        // Coverpoint 2: Packet Length (Bytes) with Explicit Corner Bins
        cp_length: coverpoint sample_len {
            bins len_min_1B     = {1};
            bins len_dw_4B      = {4};
            bins len_small      = {[2:3], [5:15]};
            bins len_cache_line = {64};
            bins len_jumbo_9K   = {9000};
            bins len_oversized  = {[9001:16384]};
            illegal_bins zero_or_neg = {0, [-100:-1]}; // ความยาว 0 หรือติดลบ ถือว่าผิดกฎหมาย
        }

        // Coverpoint 3: Destination Routing ID
        cp_dest: coverpoint sample_dest {
            bins core_ports[] = {[0:3]};
            bins memory_port  = {4};
            bins mgmt_port    = {7};
            ignore_bins unused_ports = {[5:6], [8:15]}; // พอร์ตที่ไม่มีอยู่จริงทางกายภาพ
        }

        // Coverpoint 4: Backpressure Stall Latency Profile
        cp_stall: coverpoint sample_stall {
            bins no_wait   = {STALL_NONE};
            bins short_wait = {STALL_SHORT};
            bins long_wait  = {STALL_BURST};
        }

        // Coverpoint 5: FSM Sequence Transition Coverage
        // ตรวจสอบว่าระบบเคยผ่านลำดับ: ไม่มี Stall -> มี Stall ยาว -> กลับสู่ไม่มี Stall หรือไม่
        cp_stall_transition: coverpoint sample_stall {
            bins clean_to_jam_to_clean = (STALL_NONE => STALL_BURST => STALL_NONE);
            bins gradual_recovery      = (STALL_BURST => STALL_SHORT => STALL_NONE);
        }

        // CROSS COVERAGE 1: Packet Type vs Packet Length
        // ยืนยันว่ามีการทดสอบแพ็กเก็ตทุกชนิดในทุกขนาด
        cross_type_x_len: cross cp_type, cp_length {
            // แพ็กเก็ต CONTROL มีขนาดไม่เกิน 64 ไบต์เสมอ ตัดขนาดใหญ่ทิ้ง
            ignore_bins ctrl_no_jumbo = binsof(cp_type) intersect {AXI_PKT_CONTROL} &&
                                        binsof(cp_length) intersect {len_jumbo_9K, len_oversized};
            // ห้ามเกิดกรณี Error Packet มีขนาดยักษ์ในสเปก
            illegal_bins err_too_big = binsof(cp_type) intersect {AXI_PKT_ERROR} &&
                                       binsof(cp_length) intersect {len_oversized};
        }

        // CROSS COVERAGE 2: Packet Size vs Backpressure Stress
        // ตรวจสอบว่าเคยเกิดสภาวะ Backpressure ยาวนานขณะที่ส่ง Jumbo Frame 9KB หรือไม่
        cross_len_x_stall: cross cp_length, cp_stall {
            bins jumbo_under_heavy_stall = binsof(cp_length) intersect {len_jumbo_9K} &&
                                           binsof(cp_stall) intersect {STALL_BURST};
        }

    endgroup

    event sample_event;

    function new();
        cg_axi_stream = new();
    endfunction

    // Function to sample transaction
    function void sample(axi_pkt_type_e ptype, int plen, int pdest, stall_profile_e pstall);
        this.sample_type  = ptype;
        this.sample_len   = plen;
        this.sample_dest  = pdest;
        this.sample_stall = pstall;
        -> sample_event;
    endfunction

    // Get overall coverage score
    function real get_coverage_score();
        return cg_axi_stream.get_coverage();
    endfunction
endclass

// Testbench Module Demonstrating Coverage Sampling
module tb_axi_stream_coverage;
    AxiStreamCoverageCollector cov;

    initial begin
        $display("===============================================================");
        $display("   STARTING FUNCTIONAL COVERAGE SAMPLING & CLOSURE SUITE      ");
        $display("===============================================================");

        cov = new();

        // Stimulus Loop simulating transactions
        $display("\n>>> Stimulating Scenario 1: Standard Traffic Flow...");
        cov.sample(AXI_PKT_STANDARD, 64, 0, STALL_NONE);
        cov.sample(AXI_PKT_STANDARD, 4, 1, STALL_SHORT);
        cov.sample(AXI_PKT_CONTROL, 1, 7, STALL_NONE);

        $display("Coverage after Scenario 1: %0.2f%%", cov.get_coverage_score());

        $display("\n>>> Stimulating Scenario 2: Heavy Backpressure & Jumbo Frame...");
        cov.sample(AXI_PKT_STANDARD, 9000, 4, STALL_BURST);
        cov.sample(AXI_PKT_EXTENDED, 64, 2, STALL_BURST);
        cov.sample(AXI_PKT_EXTENDED, 64, 2, STALL_SHORT);
        cov.sample(AXI_PKT_STANDARD, 64, 0, STALL_NONE); // Trigger transition bin

        $display("Coverage after Scenario 2: %0.2f%%", cov.get_coverage_score());

        $display("\n>>> Stimulating Scenario 3: Corner-Case Boundary Exercise...");
        cov.sample(AXI_PKT_ERROR, 1, 0, STALL_NONE);
        cov.sample(AXI_PKT_CONTROL, 64, 7, STALL_SHORT);

        $display("===============================================================");
        $display("  FINAL FUNCTIONAL COVERAGE SCORE: %0.2f%%", cov.get_coverage_score());
        $display("===============================================================");

        if (cov.get_coverage_score() >= 80.0) begin
            $display("[STATUS] Coverage threshold met or approaching closure target.");
        end else begin
            $display("[STATUS] Coverage holes detected! Needs targeted directed seeds.");
        end

        $finish(0);
    end
endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความเสียหายจริงในภาคสนาม (失敗事例 - Shippai Jirei)
**ระบบตัวควบคุมปั๊มสารละลายและเซนเซอร์ในเครื่องฟอกไตเทียมทางการแพทย์ (Class III Medical Hemodialysis Device)** เกิดเหตุการณ์วิกฤติต่อชีวิตผู้ป่วย: ในระหว่างกระบวนการเตรียมระบบล้างท่อล่วงหน้า (Priming Phase) ปั๊มเกิดสูบฟองอากาศขนาดเล็กลอดผ่านท่อเลือดโดยที่วาล์วตัดวงจรฉุกเฉิน (Venous Line Clamp) ไม่ตอบสนอง ทำให้เกิดความเสี่ยงต่อภาวะฟองอากาศอุดตันในหลอดเลือด (Air Embolism Hazard) จนเครื่องตัดเข้าสู่ Safety Shutdown เคราะห์ดีที่สัญญาณเตือนหน้าจอทำงานทันเวลา แต่สำนักงานคณะกรรมการอาหารและยาแห่งสหรัฐฯ (US FDA) สั่งเรียกคืนอุปกรณ์ทั่วประเทศจำนวน 4,200 เครื่อง และสั่งระงับสายการผลิต คิดเป็นมูลค่าความเสียหายทางธุรกิจและการฟ้องร้องกว่า 12 ล้านดอลลาร์สหรัฐ

---

### การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมวาล์วตัดวงจรฉุกเฉินจึงไม่ยอมปิดกั้นสายเลือดเมื่อมีฟองอากาศ?**
   - *คำตอบ:* ตรรกะประมวลผลเซนเซอร์อัลตราโซนิกบน FPGA เกิดการบล็อกสัญญาณขัดจังหวะ (Interrupt Suppression) ชั่วขณะ
2. **ทำไมสัญญาณ Interrupt จึงถูกบล็อกชั่วขณะ?**
   - *คำตอบ:* สัญญาณเตือน Air-Bubble เกิดขึ้นพร้อมกับจังหวะที่ระบบปรับระดับความเร็วการไหลของปั๊มแบบฉับพลัน (Rapid Flow Transition) ในขณะที่แรงดันตกชั่วขณะ ทำให้ FSM ตัดสินใจเข้าสู่โหมดปรับสมดุลแรงดันก่อน
3. **ทำไมการทดสอบด้วย Testbench ก่อนส่งมอบจึงตรวจไม่พบความบกพร่องนี้?**
   - *คำตอบ:* ทีมวิศวกรส่งมอบงานโดยอิงผลลัพธ์ของ **Code Coverage 100% (Line, Branch, Toggle Coverage ครบ 100%)** แต่ไม่มีการกำหนดตัวชี้วัด **Functional Cross-Coverage** สำหรับการผสมผสานระหว่าง "Air-Bubble Event" กับ "Rapid Flow Transition"
4. **ทำไมจึงไม่มี Cross-Coverage ตัวนี้ใน Verification Plan?**
   - *คำตอบ:* แผนการทดสอบเดิมมุ่งเน้นไปที่การทดสอบเซนเซอร์ทีละตัวแบบแยกส่วน โดยไม่ได้นำตารางวิเคราะห์ความเสี่ยงอันตราย (Hazard Analysis & Risk Assessment - ISO 14971) มาผูกโยงเข้ากับ Covergroup Bins
5. **ทำไมกระบวนการตรวจแบบ (Kenzu) จึงยอมให้ผ่านการอนุมัติ?**
   - *คำตอบ:* ขาดขั้นตอนการตรวจทาน **Traceability Matrix ระหว่าง System Hazards กับ Functional Coverage Bins** ทำให้ปล่อยให้เกิดช่องโหว่ความคุ้มครอง (Coverage Holes) ขนาดใหญ่

---

### แผนผังสาเหตุและผล (Ishikawa Fishbone Diagram)

```
==================================================================================================
                                    ISHIKAWA FISHBONE CAUSE-EFFECT DIAGRAM
==================================================================================================

   MAN (บุคลากร)                                   MACHINE / TOOLS (เครื่องมือ)
   ----------------                                ---------------------------
   หลงเชื่อภาพลวงตาของ Code Coverage 100%          Simulator ไม่ได้เปิดรายงาน Exclusion List
   ขาดการประสานงานกับทีมวิเคราะห์ความปลอดภัยชีวการแพทย์ ขาด Cross-Coverage ระหว่าง Air Alarm กับ Flow
               \                                                /
                \                                              /
                 \                                            /
                  +------------------------------------------+
                  |                                          |
                  |  HEMODIALYSIS AIR EMBOLISM RECALL        | ===>> [12M USD FDA RECALL DISASTER]
                  |                                          |
                  +------------------------------------------+
                 /                                            \
                /                                              \
   METHOD (ระเบียบปฏิบัติ)                          MATERIAL / ENVIRONMENT (สภาวะแวดล้อม)
   ----------------------                          -------------------------------------
   ไม่ได้ผูก ISO 14971 Hazard เข้ากับ Covergroups  การสั่นสะเทือนของปั๊มทำให้เซนเซอร์ส่งสัญญาณถี่
   ขาดกระบวนการ Coverage Hole Closure Audit        สภาวะแรงดันตกชั่วขณะทำให้เกิด Race Condition
==================================================================================================
```

---

### คู่มือปฏิบัติการตรวจสอบ OJT หน้างาน: กลยุทธ์การปิดช่องโหว่ความครอบคลุม (100% Coverage Closure SOP)

1. **Step 1: การจำแนกประเภทของ Coverage Hole (รูโหว่ของความครอบคลุม)**
   - เมื่อรัน Regression แล้ว Covergroup ไม่แตะ 100% ให้เปิดรายงาน HTML Coverage Report เพื่อดู Uncovered Bins
   - แบ่ง Bins ที่ไม่ถูกแตะออกเป็น 2 ชนิด:
     - **Unreachable Bins (สถานะที่เป็นไปไม่ได้ทางกายภาพ):** ต้องทำการใส่ `ignore_bins` พร้อมระบุข้อความอธิบายเหตุผลและเลขเอกสารสเปกอ้างอิง
     - **Test Hole Bins (สถานะจริงที่ยังขาดการทดสอบ):** ต้องเขียน Directed Sequence เพื่อบีบให้เกิดเหตุการณ์นั้น
2. **Step 2: ห้ามใช้การขอยกเว้น (Coverage Waiver) โดยพลการ**
   - การใส่คำสั่งยกเว้น Bin ต้องผ่านการประชุม Kenzu และมีลายเซ็นของ Chief Verification Architect เสมอ
   - ห้ามปรับลดพารามิเตอร์ `option.at_least` จากค่ามาตรฐานเพื่อทำให้ตัวเลขเปอร์เซ็นต์ดูสูงขึ้นหลอกตา
3. **Step 3: การสร้าง Directed Seeds ปิดช่องโหว่ (Targeted Seed Closure)**
   - ใช้เครื่องมือวิเคราะห์อัตโนมัติ (เช่น Synopsys Coverity หรือ Cadence vManager) ค้นหาว่า Random Seed ใดที่พาเข้าใกล้ Bin เป้าหมายมากที่สุด แล้วล็อก Seed นั้นเข้าสู่ Regression Suite ถาวร

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (専門用語)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / อังกฤษ | บริบทการใช้งานเชิงวิศวกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **機能カバレッジ** | きのうカバレッジ | Kinou Kabarejji | Functional Coverage | ความครอบคลุมเชิงฟังก์ชันตามข้อกำหนดสเปก |
| **交差カバレッジ** | こうさカバレッジ | Kousa Kabarejji | Cross Coverage | การวัดความครอบคลุมของการผสมผสานระหว่างสถานะ |
| **カバレッジホール** | カバレッジホール | Kabarejji Hooru | Coverage Hole | ช่องโหว่หรือสภาวะที่การทดสอบยังเข้าไม่ถึง |
| **除外ビン** | じょがいビン | Jogai Bin | Ignore Bins | กลุ่มสถานะที่ตัดออกจากการคำนวณตัวหารความครอบคลุม |
| **禁止ビン** | きんしビン | Kinshi Bin | Illegal Bins | กลุ่มสถานะต้องห้ามที่หากเกิดขึ้นจะสั่งตัดจบการทำงานทันที |
| **カバレッジ収束** | カバレッジしゅうそく | Kabarejji Shuusoku | Coverage Closure | การบรรลุเป้าหมายความครอบคลุม 100% ก่อนส่งมอบ |
| **コード網羅率** | コードもうらりつ | Koudo Mouraritsu | Code Coverage | ความครอบคลุมระดับบรรทัดคำสั่ง RTL |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図審議 - Kenzu Shingi)

**สถานที่:** ห้องประชุมรับรองความปลอดภัยทางการแพทย์ระดับสากล (Medical Device Sign-off Gate)  
**ผู้เข้าร่วม:**
- **ฮายาชิ (林):** Quality Assurance & Verification Director (品質保証部長/主査)
- **สิทธิชัย (シッティチャイ):** Senior FPGA Design Engineer (設計担当)

---

**林主査 (ฮายาชิ):**  
「シッティチャイさん、人工透析装置のFPGA検証完了レポートを拝見しました。コード網羅率（Code Coverage）はオール100%になっていますが、**機能カバレッジ（Functional Coverage）**の交差検証（Cross Coverage）結果はどうなっていますか？」  
*(คุณสิทธิชัยครับ ผมดูรายงานการตรวจสอบความถูกต้องของ FPGA สำหรับเครื่องฟอกไตแล้ว Code Coverage ได้ครบ 100% ทุกตัว แต่ผลการตรวจสอบ Cross Coverage ของ Functional Coverage เป็นอย่างไรบ้างครับ?)*

**シッティチャイ (สิทธิชัย):**  
「林主査、ステートマシンと分岐の網羅率は完全に100%を達成しておりますので、すべてのRTLロジックが実行されたことは証明されております。」  
*(หัวหน้าฮายาชิครับ ทั้ง FSM และ Branch Coverage เราเก็บได้ครบ 100% สมบูรณ์แบบแล้วครับ นั่นพิสูจน์ได้ว่าโค้ด RTL ทุกส่วนได้ถูกสั่งให้ทำงานจริงแล้วครับ)*

**林主査 (ฮายาชิ):**  
「それでは医療機器クラスIIIの監査は絶対に通りません！コード網羅率が100%でも、それは**未実装の仕様（Unimplemented Specification）**が存在しない証明にはなりません。特に、透析液の流速急変と気泡検知アラームが同時に発生した際の**交差カバレッジ（Cross Coverage）**が未達（Coverage Hole）のまま放置されていますよ。もし臨床現場でこの複合状態が発生し、バルブが誤動作したら患者の命に関わります！」  
*(ถ้าตอบแบบนั้น การตรวจสอบเครื่องมือแพทย์ Class III ไม่มีวันผ่านเด็ดขาดครับ! ต่อให้ Code Coverage เป็น 100% มันไม่ได้เป็นหลักฐานพิสูจน์ว่าไม่มีฟังก์ชันที่ตกหล่นไปจากสเปก โดยเฉพาะอย่างยิ่งจังหวะที่อัตราการไหลของสารละลายเปลี่ยนฉับพลันพร้อมกับสัญญาณเตือนฟองอากาศ Cross Coverage ของคู่นี้ยังเป็น Coverage Hole อยู่เลยครับ หากสภาวะผสมนี้เกิดขึ้นจริงในโรงพยาบาลแล้ววาล์วทำงานผิดพลาด ชีวิตของผู้ป่วยจะตกอยู่ในอันตรายทันทีนะ!)*

**シッティチャイ (สิทธิชัย):**  
「申し訳ありません！コードが動いたことだけに満足し、リスク分析に基づいた複合状態の網羅性を見落としておりました。」  
*(ขออภัยอย่างยิ่งครับ! ผมมัวแต่ดีใจที่โค้ดทำงานได้ครบทุกบรรทัด จนมองข้ามความครอบคลุมของสภาวะผสมตามรายงานการประเมินความเสี่ยงไปครับ)*

**林主査 (ฮายาชิ):**  
「分かればよろしい。直ちにリスク分析（ISO 14971）で定義された全てのハザードシナリオに対してCoverpointを作成し、交差カバレッジを100%に引き上げる**カバレッジ収束計画（Coverage Closure Plan）**を提出してください。未達ビン（Uncovered Bins）を適当に`ignore_bins`で除外することは一切認めません。すべてのビンが実際に叩かれた証跡を確認するまで、サインオフ印は押せません。」  
*(เข้าใจก็ดีแล้ว ให้รีบสร้าง Coverpoints สำหรับทุกสถานการณ์อันตรายตาม ISO 14971 ทันที และส่งแผน Coverage Closure เพื่อดัน Cross Coverage ให้แตะ 100% มาให้ผมดู การแอบเอา Bins ที่ไม่ผ่านไปใส่ `ignore_bins` แบบมักง่าย ผมไม่อนุญาตเด็ดขาด จนกว่าจะมีหลักฐานว่าทุก Bins ถูกกระตุ้นจริงในสภาพแวดล้อม ผมจะไม่มีวันประทับตราอนุมัติให้ครับ)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณจำนวน Valid Bins ใน Cross-Coverage ภายใต้เงื่อนไข `ignore_bins` และ `intersect`

พิจารณาคำสั่ง SystemVerilog Covergroup ต่อไปนี้:
```systemverilog
covergroup cg_network_quiz @(posedge clk);
    cp_port: coverpoint port_id {
        bins lan_ports[] = {[0:3]}; // 4 bins (0, 1, 2, 3)
        bins wan_port    = {4};     // 1 bin
    } // รวม 5 bins

    cp_vlan: coverpoint vlan_pri {
        bins normal_pri[] = {[0:5]}; // 6 bins (0, 1, 2, 3, 4, 5)
        bins voice_pri    = {6};     // 1 bin
        bins control_pri  = {7};     // 1 bin
    } // รวม 8 bins

    cross_port_vlan: cross cp_port, cp_vlan {
        ignore_bins no_mgmt_on_lan = binsof(cp_port.lan_ports) && 
                                     binsof(cp_vlan.control_pri);
    }
endgroup
```
จงคำนวณหาจำนวน Bins ที่ถูกต้องสมบูรณ์ (Total Valid Bins) ของ Cross Coverage `cross_port_vlan` ที่จะถูกนำไปใช้เป็นตัวหารในการคำนวณเปอร์เซ็นต์ความครอบคลุม:

- **A)** $40$ Bins
- **B)** $39$ Bins
- **C)** $36$ Bins
- **D)** $32$ Bins

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: C) $36$ Bins**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. คำนวณจำนวน Raw Cross Bins ก่อนตัดทอน:
   - `cp_port` มีจำนวน Bins: $|Bins(cp\_port)| = 4 (\text{จาก lan\_ports}) + 1 (\text{จาก wan\_port}) = 5 \text{ Bins}$
   - `cp_vlan` มีจำนวน Bins: $|Bins(cp\_vlan)| = 6 (\text{จาก normal\_pri}) + 1 (\text{จาก voice\_pri}) + 1 (\text{จาก control\_pri}) = 8 \text{ Bins}$
   - ผลคูณของจำนวน Bins ดิบทั้งหมดคือ:
     $$N_{raw} = |Bins(cp\_port)| \times |Bins(cp\_vlan)| = 5 \times 8 = 40 \text{ Bins}$$
2. คำนวณจำนวน Bins ที่ถูกตัดออกด้วย `ignore_bins no_mgmt_on_lan`:
   - เงื่อนไขกำหนดว่า: `binsof(cp_port.lan_ports) && binsof(cp_vlan.control_pri)`
   - สมาชิกใน `cp_port.lan_ports` มี 4 ตัว คือ $\{0, 1, 2, 3\}$
   - สมาชิกใน `cp_vlan.control_pri` มี 1 ตัว คือ $\{7\}$
   - คู่ลำดับที่ตรงกับเงื่อนไขนี้คือ:
     $$\{ (0, 7), (1, 7), (2, 7), (3, 7) \}$$
   - จำนวน Bins ที่ถูกระบุเป็น ignore คือ:
     $$N_{ignore} = 4 \times 1 = 4 \text{ Bins}$$
3. คำนวณจำนวน Bins ที่เหลืออยู่สำหรับคิดคะแนนจริง (Valid Bins):
   $$N_{valid} = N_{raw} - N_{ignore} = 40 - 4 = 36 \text{ Bins}$$

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** $40$ Bins คือจำนวนดิบโดยไม่ได้หัก `ignore_bins` ออก
- **ข้อ B ผิด:** คิดว่า `lan_ports` ตัดทอนออกเพียง 1 Bin ทั้งที่มีอยู่ 4 Bins ย่อยภายใน Array Bins
- **ข้อ D ผิด:** คิดว่าตัดกลุ่ม control_pri ออกจากทั้ง 5 พอร์ต ($40 - 8 = 32$) ซึ่งผิดเงื่อนไขเพราะ WAN Port ยังคงนับตามปกติ

---

### คำถามที่ 2: ผลกระทบทางพฤติกรรมระหว่าง `illegal_bins` และ `ignore_bins` ในระหว่างการทดสอบ

หากใน Covergroup มีการประกาศ Bin ดังต่อไปนี้:
```systemverilog
coverpoint cpu_opcode {
    bins legal_ops[] = {[0:14]};
    illegal_bins undefined_op = {15};
}
```
หากในระหว่างการรัน Constrained Random Simulation เกิดเหตุการณ์ที่ตัวแปร `cpu_opcode` สุ่มได้ค่าเท่ากับ `15` พฤติกรรมของ Simulator ตามมาตรฐาน IEEE 1800 SystemVerilog จะเป็นอย่างไร?

- **A)** Simulator จะละทิ้งการนับคะแนนและคิดเปอร์เซ็นต์ความครอบคลุมต่อไปตามปกติ
- **B)** Simulator จะส่งสัญญาณแจ้งเตือนระดับ Warning และทำการบันทึกค่าลงใน log file
- **C)** Simulator จะรายงานข้อผิดพลาดระดับ Fatal Error และสั่งยุติการรัน (Abort/Terminate Simulation) ทันที
- **D)** Simulator จะบังคับให้ตัวแปรเปลี่ยนค่าเป็น `0` แล้วทำการทดสอบต่อ

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: C) Simulator จะรายงานข้อผิดพลาดระดับ Fatal Error และสั่งยุติการรัน (Abort/Terminate Simulation) ทันที**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ตามมาตรฐาน IEEE 1800 SystemVerilog ความแตกต่างพื้นฐานระหว่าง `ignore_bins` และ `illegal_bins` คือ:
   - **`ignore_bins`:** ทำหน้าที่ตัดสถานะนั้นออกจากการคำนวณความครอบคลุม หากสัญญาณสุ่มโดนค่านี้ ตัวนับคะแนนจะไม่เพิ่มขึ้น และไม่มีข้อผิดพลาดใดๆ เกิดขึ้น
   - **`illegal_bins`:** ทำหน้าที่เสมือน Assertion ทางสถาปัตยกรรมระดับฮาร์ดแวร์ เพื่อประกาศว่าสภาวะนี้ **"เป็นสิ่งต้องห้ามและต้องไม่เกิดขึ้นโดยเด็ดขาดในระบบที่ถูกต้อง"**
2. เมื่อตัวแปรสุ่มเข้าสู่ `illegal_bins`:
   - กลไก Coverage Engine จะดักจับเหตุการณ์นี้เป็น **Runtime Violation**
   - Simulator มาตรฐานทุกตัว (VCS, Xcelium, Questa) จะส่งข้อความ Fatal Error และทำการหยุดการจำลอง (Abort/Crash) ทันที เพื่อป้องกันไม่ให้ข้อมูลขยะแพร่กระจายไปทำลายส่วนอื่น
3. วิศวกรจึงนิยมใช้ `illegal_bins` ดักจับสถานะที่บ่งชี้ถึงข้อบกพร่องร้ายแรง เช่น Unmapped Register Access หรือ Reserved FSM State

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** นั่นคือพฤติกรรมของ `ignore_bins` ไม่ใช่ `illegal_bins`
- **ข้อ B ผิด:** ข้อผิดพลาดของ `illegal_bins` อยู่ในระดับ Fatal/Error เสมอ ไม่ใช่แค่ Warning
- **ข้อ D ผิด:** ตัววัดความครอบคลุมเป็นเพียงตัวสังเกตการณ์ (Observer) ไม่มีสิทธิ์แทรกแซงหรือแก้ไขค่าในสัญญาณตัวแปร

---

### คำถามที่ 3: การคำนวณจำนวน Transition Bins ของ Finite State Machine (FSM)

พิจารณาการกำหนด Transition Bins สำหรับ FSM ควบคุมความปลอดภัยของระบบเบรก:
```systemverilog
coverpoint brake_state {
    bins safe_recovery = (STANDBY => BRAKING => ABS_ACTIVE => STANDBY);
    bins emergency_seq = (STANDBY => BRAKING => FAULT => (SAFE_STOP, STANDBY));
}
```
กำหนดให้สัญลักษณ์ `(SAFE_STOP, STANDBY)` ในลำดับสุดท้ายหมายถึง ปลายทางสามารถจบลงที่สถานะใดสถานะหนึ่งในสองสถานะนี้ได้ จงคำนวณหาจำนวนเส้นทาง (Transition Sequences) ทั้งหมดที่ถูกสร้างขึ้นจากทั้งสอง Bins รวมกัน:

- **A)** $2$ เส้นทาง
- **B)** $3$ เส้นทาง
- **C)** $4$ เส้นทาง
- **D)** $6$ เส้นทาง

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) $3$ เส้นทาง**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. พิจารณา Bin ที่ 1: `safe_recovery`
   - มีลำดับการเปลี่ยนสถานะที่ระบุเจาะจงเส้นทางเดียว:
     $$\text{Path 1: } \text{STANDBY} \to \text{BRAKING} \to \text{ABS\_ACTIVE} \to \text{STANDBY}$$
   - สร้างขึ้นเป็น $1$ Transition Sequence
2. พิจารณา Bin ที่ 2: `emergency_seq`
   - มีไวยากรณ์ `(SAFE_STOP, STANDBY)` ที่ขั้นตอนสุดท้าย ซึ่งหมายถึงการแตกกิ่ง (Branching Transition):
     $$\text{Path 2A: } \text{STANDBY} \to \text{BRAKING} \to \text{FAULT} \to \text{SAFE\_STOP}$$
     $$\text{Path 2B: } \text{STANDBY} \to \text{BRAKING} \to \text{FAULT} \to \text{STANDBY}$$
   - สร้างขึ้นเป็น $2$ Transition Sequences
3. รวมจำนวนเส้นทางทั้งหมดที่ระบบติดตาม:
   $$N_{total\_paths} = 1 + 2 = 3 \text{ เส้นทาง}$$

ดังนั้น จะมี Transition Sequences ทั้งหมด 3 เส้นทางที่ต้องถูกกระตุ้นให้เกิดขึ้นจริงในระหว่าง Simulation จึงจะถือว่า Bin ทั้งสองนี้ผ่านเกณฑ์ 100%

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** นับตามชื่อบรรทัด Bin (2 บรรทัด) โดยไม่ได้กระจายสาขาย่อยในวงเล็บ
- **ข้อ C ผิด:** คิดว่ามีการคูณไขว้ 2 เท่าในทุกจุด
- **ข้อ D ผิด:** คำนวณเกินความเป็นจริง
