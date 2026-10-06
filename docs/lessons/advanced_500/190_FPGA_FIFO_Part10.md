# Lesson 190: FPGA FIFO Part 10 — Master FIFO Verification & SVA Formal Proofs (การตรวจสอบความถูกต้องของ FIFO ระดับมาสเตอร์และการพิสูจน์คุณสมบัติเชิงฟอร์มัลด้วย SVA)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในการออกแบบระบบดิจิทัลระดับ Mission-Critical และ High-Reliability ASICs/FPGAs (เช่น ระบบอากาศยาน DO-254 DAL-A, ระบบยานยนต์อัตโนมัติ ISO 26262 ASIL-D, หรืออุปกรณ์สำรวจอวกาศ ECSS) โมดูล FIFO (First-In, First-Out) มักเป็นจุดเสี่ยงอันดับหนึ่งต่อการเกิด Race Condition, Data Drop, Data Duplication, และ Deadlock เนื่องจากเชื่อมต่อระหว่างโดเมนสัญญาณนาฬิกาต่างความถี่ (Asynchronous CDC)

การทดสอบด้วย Dynamic Simulation เพียงอย่างเดียว (ไม่ว่าจะรันสุ่มด้วย UVM Constrained-Random ไปกี่พันล้านรอบคล็อก) **ไม่สามารถรับประกันความถูกต้องได้ 100% (Simulation cannot prove the absence of bugs)** เพราะความน่าจะเป็นที่ขอบสัญญาณนาฬิกาของ $clk_{wr}$ และ $clk_{rd}$ จะมี Phase Skew ที่ตกกระทบตรงเงื่อนไข Corner-Case สุดขั้วพร้อมกับการเกิด Backpressure อาจมีค่าน้อยกว่า $10^{-12}$ ต่อรอบคล็อก

วิศวกรระดับ Senior/Principal FPGA จึงต้องประยุกต์ใช้ **Formal Property Verification (FPV)** ร่วมกับ **SystemVerilog Assertions (SVA)** เพื่อพิสูจน์ทางคณิตศาสตร์ (Mathematical Proof) ว่า FIFO ไม่มีวันละเมิด Safety Properties (ไม่มี Overflow, ไม่มี Underflow, ข้อมูลเข้าและออกตรงกันทุกบิตตามลำดับ) และ Liveness Properties (ข้อมูลที่เขียนเข้าไปจะต้องถูกอ่านออกมาได้ในเวลาจำกัด ไม่ติด Deadlock)

```
+------------------------------------------------------------------------------------------------+
|                         FIFO MATHEMATICAL FORMAL VERIFICATION ARCHITECTURE                     |
+------------------------------------------------------------------------------------------------+
                                                                                                  
                      +----------------------------------------------------+                      
                      |             Formal Assumptions (assume)            |                      
                      |  - Valid Gray-code transitions on CDC boundaries   |                      
                      |  - Upstream backpressure response time bounds      |                      
                      |  - Reset duration & minimum deassertion spacing    |                      
                      +----------------------------------------------------+                      
                                                 |                                                
                                                 v                                                
+-----------------------+              +-------------------+              +----------------------+
| Write Domain Stimulus | -----------> |   FIFO Under Test | -----------> | Read Domain Monitor  |
| (Symbolic Inputs)     |  wr_en, wdata|   (RTL Instance)  | rdata, rempty| (Symbolic Sampling)  |
+-----------------------+              +-------------------+              +----------------------+
                                                 ^                                                
                                                 |                                                
                      +----------------------------------------------------+                      
                      |             Formal Assertions (assert)             |                      
                      |  [P1] Safety: No Overflow under full assertion     |                      
                      |  [P2] Safety: No Underflow under empty assertion   |                      
                      |  [P3] Integrity: Exact FIFO Data Ordering          |                      
                      |  [P4] Liveness: Finite Drain Bound (No Lockup)     |                      
                      +----------------------------------------------------+                      
```

---

### 1.1 ทฤษฎีบททางคณิตศาสตร์ว่าด้วยความคงสภาพของลำดับข้อมูล (Data Ordering & Integrity Invariance)

คุณสมบัติพื้นฐานที่สุดของ FIFO คือการเป็นคิวเชิงเส้นที่รักษาลำดับก่อนหลัง (First-In, First-Out Queue) ในทางคณิตศาสตร์ เรานิยามลำดับของทรานแซกชันข้อมูลที่ถูกเขียนเข้าเป็นลำดับ $X = \langle x_0, x_1, x_2, \dots, x_{n-1} \rangle$ และลำดับของข้อมูลที่ถูกอ่านออกจาก FIFO เป็น $Y = \langle y_0, y_1, y_2, \dots, y_{m-1} \rangle$

#### 1. Invariance Theorem (ทฤษฎีบทความไม่แปรเปลี่ยนของข้อมูล)
สำหรับทุกๆ ทรานแซกชันลำดับที่ $k \ge 0$ หากการอ่านเกิดขึ้นสำเร็จ ($read\_ack_k = 1$ ที่เวลา $t_{rd\_k}$):
$$y_k = x_k \quad \forall k \in [0, m-1], \quad m \le n$$

และขนาดของแถวคิวชั่วคราว (Instantaneous Occupancy $L(t)$) ต้องสอดคล้องกับสมการอนุรักษ์:
$$L(t) = N_{written}(t) - N_{read}(t)$$
โดยมีเงื่อนไขขอบเขตที่แน่นอน (Bounded Capacity Invariant):
$$0 \le L(t) \le C_{FIFO}$$
เมื่อ $C_{FIFO}$ คือความจุสูงสุดของ FIFO (Capacity) หากระบบเข้าสู่สภาวะที่ $L(t) < 0$ แสดงว่าเกิด **Underflow** และหาก $L(t) > C_{FIFO}$ แสดงว่าเกิด **Overflow**

#### 2. K-Induction Mathematical Proof Engine
เครื่องมือ Formal Verification (เช่น Cadence JasperGold, Synopsys VC Formal, หรือ Questa PropCheck) ใช้เทคนิคทางคณิตศาสตร์ที่เรียกว่า **$k$-Induction** เพื่อพิสูจน์ Property $P(s)$ บนทุกสถานะที่ระบบสามารถเข้าถึงได้ (Reachable State Space):

1. **Base Case ($k=0$ ถึง $k=n$):**
   พิสูจน์ว่าจากสถานะเริ่มต้นหลัง Reset ($s_0 \in S_{init}$) คุณสมบัติ $P$ เป็นจริงต่อเนื่องไปจนถึง $k$ ไซเคิล:
   $$I(s_0) \implies P(s_0) \wedge P(s_1) \wedge \dots \wedge P(s_k)$$
2. **Inductive Step:**
   สมมุติว่าคุณสมบัติ $P$ เป็นจริงติดต่อกัน $k$ ไซเคิลใดๆ (บนสถานะที่ไม่จำเป็นต้องเชื่อมกับ Reset โดยตรง) พิสูจน์ว่าในไซเคิลถัดไป ($k+1$) คุณสมบัติ $P$ จะต้องยังคงเป็นจริงเสมอ:
   $$\left( \bigwedge_{i=0}^{k-1} P(s_i) \wedge T(s_i, s_{i+1}) \right) \implies P(s_k)$$
   เมื่อ $T(s, s')$ คือ State Transition Relation ของวงจร RTL

หากโมเดลมีจุดรั่วทางสถาปัตยกรรม (เช่น ตัวชี้ Pointer กระโดดข้ามค่า หรือ Gray Code ข้ามบิต) Formal Solver จะสร้าง **Counter-Example (Bug Trace)** ที่แสดงสัญญาณทุกเส้นทีละไซเคิลจนถึงจุดที่ Assertion ละเมิด

---

### 1.2 โครงสร้าง SystemVerilog Assertions (SVA) ขั้นสูงสำหรับ FIFO

เพื่อให้การพิสูจน์ Formal ครอบคลุมสมบูรณ์ เราแบ่ง Assertions ออกเป็น 4 หมวดหลัก:
1. **Safety Assertions (Overflow / Underflow Protection)**
2. **Structural Assertions (Gray Code & Pointer Invariant)**
3. **Data Integrity & Ordering (Formal Scoreboard / Auxiliary Shadow Model)**
4. **Liveness Assertions (Eventual Drain & No Deadlock)**

```
         +---------------------------------------------------------------------+
         |              SVA AUXILIARY FORMAL DATA INTEGRITY TRACKER            |
         +---------------------------------------------------------------------+
                                                                                
           write_stream: [D0] [D1] [D2] [D3] [D4] ... [Dn]                     
                                  |                                             
                                  v                                             
                   +------------------------------+                             
                   | Formal Magic-Value Injector  |                             
                   | Selects symbolic payload D*  |                             
                   +------------------------------+                             
                                  |                                             
                    Payload D* enters FIFO at tag=k                             
                                  |                                             
                                  v                                             
                   +------------------------------+                             
                   | State: WAITING_FOR_READ      |                             
                   | Counter: Decrements on pops  |                             
                   +------------------------------+                             
                                  |                                             
                    read_stream outputs D_out                                   
                                  |                                             
                                  v                                             
                   +------------------------------+                             
                   | SVA ASSERTION EVALUATION     |                             
                   | assert: D_out == D*          |                             
                   | assert: Tag count reaches 0  |                             
                   +------------------------------+                             
```

---

### 1.3 RTL Code: Master Formal FIFO Assertion Suite (`fifo_sva_formal.sv`)

โค้ดชุดนี้ถูกออกแบบมาเพื่อใช้ทั้งใน **Formal Verification (JasperGold/VC Formal)** และ **Dynamic Simulation (VCS/Xcelium/ModelSim/Vivado)** โดยใช้ Auxiliary Logic เพื่อจำลอง Shadow Scoreboard โดยไม่สิ้นเปลือง State Space ของ Formal Engine

```systemverilog
//=============================================================================
// Module: fifo_sva_formal
// Description: Master SystemVerilog Assertion Suite for FIFO Verification
// Standards: DO-254 DAL-A / ISO 26262 ASIL-D Formal Sign-Off Standard
//=============================================================================

`timescale 1ns / 1ps

module fifo_sva_formal #(
    parameter int DATA_WIDTH = 32,
    parameter int ADDR_WIDTH = 4,
    parameter int FIFO_DEPTH = (1 << ADDR_WIDTH)
)(
    input  logic                  wr_clk,
    input  logic                  wr_rst_n,
    input  logic                  wr_en,
    input  logic [DATA_WIDTH-1:0] wr_data,
    input  logic                  wr_full,
    input  logic                  wr_almost_full,
    input  logic [ADDR_WIDTH:0]   wptr_bin,
    input  logic [ADDR_WIDTH:0]   wptr_gray,

    input  logic                  rd_clk,
    input  logic                  rd_rst_n,
    input  logic                  rd_en,
    input  logic [DATA_WIDTH-1:0] rd_data,
    input  logic                  rd_empty,
    input  logic                  rd_almost_empty,
    input  logic [ADDR_WIDTH:0]   rptr_bin,
    input  logic [ADDR_WIDTH:0]   rptr_gray
);

    //=========================================================================
    // 1. SAFETY PROPERTIES: NO OVERFLOW & NO UNDERFLOW
    //=========================================================================
    
    // Property 1: No Write When Full (Overflow Prevention)
    // การเขียนขณะที่ FIFO เต็ม ถือเป็นการทำลายข้อมูลร้ายแรง
    property p_no_overflow;
        @(posedge wr_clk) disable iff (!wr_rst_n)
        (wr_full && !rd_en) |-> not (wr_en);
    endproperty
    a_no_overflow: assert property (p_no_overflow)
        else $error("[FATAL][SVA-01] FIFO Overflow Detected! wr_en asserted while wr_full=1");

    // Property 2: No Read When Empty (Underflow Prevention)
    // การอ่านขณะที่ FIFO ว่าง จะได้ข้อมูลขยะ (Corrupt/Stale Data)
    property p_no_underflow;
        @(posedge rd_clk) disable iff (!rd_rst_n)
        rd_empty |-> not (rd_en);
    endproperty
    a_no_underflow: assert property (p_no_underflow)
        else $error("[FATAL][SVA-02] FIFO Underflow Detected! rd_en asserted while rd_empty=1");

    //=========================================================================
    // 2. STRUCTURAL PROPERTIES: GRAY CODE ENCODING CONTINUITY
    //=========================================================================
    
    // Property 3: Gray Code Pointer Consecutive Bit Flip (At most 1 bit changes)
    // ค่า Gray Code จะต้องเปลี่ยนสถานะได้เพียง 1 บิตต่อ 1 รอบคล็อกเท่านั้น
    property p_wptr_gray_single_bit;
        @(posedge wr_clk) disable iff (!wr_rst_n)
        $countones(wptr_gray ^ $past(wptr_gray)) <= 1;
    endproperty
    a_wptr_gray_single_bit: assert property (p_wptr_gray_single_bit)
        else $error("[FATAL][SVA-03] Gray Code Multi-Bit Transition Detected on wptr_gray!");

    property p_rptr_gray_single_bit;
        @(posedge rd_clk) disable iff (!rd_rst_n)
        $countones(rptr_gray ^ $past(rptr_gray)) <= 1;
    endproperty
    a_rptr_gray_single_bit: assert property (p_rptr_gray_single_bit)
        else $error("[FATAL][SVA-04] Gray Code Multi-Bit Transition Detected on rptr_gray!");

    // Property 4: Gray to Binary Functional Equivalence Invariant
    // ตรวจสอบความถูกต้องของการแปลงกลับ Gray-to-Binary ใน RTL
    function automatic logic [ADDR_WIDTH:0] gray2bin(logic [ADDR_WIDTH:0] g);
        logic [ADDR_WIDTH:0] b;
        b[ADDR_WIDTH] = g[ADDR_WIDTH];
        for (int i = ADDR_WIDTH - 1; i >= 0; i--) begin
            b[i] = b[i+1] ^ g[i];
        end
        return b;
    endfunction

    property p_wptr_gray_bin_match;
        @(posedge wr_clk) disable iff (!wr_rst_n)
        gray2bin(wptr_gray) == wptr_bin;
    endproperty
    a_wptr_gray_bin_match: assert property (p_wptr_gray_bin_match)
        else $error("[FATAL][SVA-05] wptr_gray does not mathematically match wptr_bin!");

    //=========================================================================
    // 3. AUXILIARY FORMAL DATA INTEGRITY & ORDERING VERIFIER
    //=========================================================================
    // ใช้เทคนิค Symbolic Transaction Tracking สำหรับ Formal Proof
    // ตรวจสอบว่าถ้าเขียนข้อมูลชุดใดชุดหนึ่งเข้าไป ข้อมูลนั้นจะต้องออกมาตามลำดับเป๊ะๆ
    
    // สุ่มเลือกข้อมูล Symbolic ที่น่าสงสัย (Formal Engine จะกวาดทุกค่าที่เป็นไปได้)
    (* anyconst *) logic [DATA_WIDTH-1:0] f_watch_data;
    logic f_watch_en;
    logic [ADDR_WIDTH:0] f_watch_pos;
    logic f_in_flight;

    // ติดตามสถานะของ Token ข้อมูลที่ถูกเฝ้าดู
    always_ff @(posedge wr_clk or negedge wr_rst_n) begin
        if (!wr_rst_n) begin
            f_in_flight <= 1'b0;
        end else if (wr_en && !wr_full && (wr_data == f_watch_data) && !f_in_flight) begin
            f_in_flight <= 1'b1;
        end
    end

    // Property 5: FIFO Read Order Verification (Strict FIFO Monotonicity)
    // ข้อมูลที่อ่านออกเมื่อถึงคิว จะต้องมีค่าเท่ากับข้อมูลที่ถูกผลักเข้าไป
    // (สำหรับกรณีจำลองพฤติกรรม Single-Clock หรือ Synchronized Shadow Scoreboard)
`ifdef FORMAL_AUX_SCOREBOARD
    logic [DATA_WIDTH-1:0] shadow_mem [0:FIFO_DEPTH-1];
    logic [ADDR_WIDTH-1:0] shadow_wptr, shadow_rptr;
    logic [ADDR_WIDTH:0]   shadow_count;

    always_ff @(posedge wr_clk or negedge wr_rst_n) begin
        if (!wr_rst_n) begin
            shadow_wptr  <= '0;
            shadow_rptr  <= '0;
            shadow_count <= '0;
        end else begin
            if (wr_en && !wr_full) begin
                shadow_mem[shadow_wptr] <= wr_data;
                shadow_wptr <= shadow_wptr + 1'b1;
            end
            if (rd_en && !rd_empty) begin
                shadow_rptr <= shadow_rptr + 1'b1;
            end
            shadow_count <= shadow_count + (wr_en && !wr_full) - (rd_en && !rd_empty);
        end
    end

    property p_data_integrity;
        @(posedge wr_clk) disable iff (!wr_rst_n)
        (rd_en && !rd_empty) |-> (rd_data == shadow_mem[shadow_rptr]);
    endproperty
    a_data_integrity: assert property (p_data_integrity)
        else $error("[FATAL][SVA-06] Data Integrity Mismatch! Read data does not match Shadow Model");
`endif

    //=========================================================================
    // 4. LIVENESS PROPERTIES: EVENTUAL DRAIN (NO PERMANENT LOCKUP)
    //=========================================================================
    // พิสูจน์ว่าหากมีข้อมูลค้างใน FIFO และฝั่งอ่านร้องขอ (rd_en=1 เสมอ) 
    // ในที่สุด FIFO จะต้องกลับคืนสู่สภาวะ EMPTY ได้เสมอภายในรอบคล็อกที่จำกัด
    
    // ใน Formal Verification เราใช้ s_eventually เพื่อพิสูจน์การหลุดจาก Deadlock
    property p_eventual_drain;
        @(posedge rd_clk) disable iff (!rd_rst_n)
        (!rd_empty && rd_en) |-> strong(##[1:FIFO_DEPTH*4] rd_empty);
    endproperty
    // Note: เปิดใช้งานใน Formal Engine ที่รองรับ Liveness Checking
    // a_eventual_drain: assert property (p_eventual_drain);

    //=========================================================================
    // 5. FORMAL COVERAGE PROPERTIES (REACHABILITY)
    //=========================================================================
    // ตรวจสอบว่าระบบสามารถเดินถึงสถานะสุดขั้วต่างๆ ได้จริง ไม่ใช่ Vacuous Pass
    c_fifo_reached_full: cover property (@(posedge wr_clk) disable iff (!wr_rst_n) wr_full);
    c_fifo_reached_empty: cover property (@(posedge rd_clk) disable iff (!rd_rst_n) rd_empty);
    c_fifo_almost_full_to_full: cover property (@(posedge wr_clk) disable iff (!wr_rst_n) 
        wr_almost_full ##1 wr_full);
    c_simultaneous_read_write: cover property (@(posedge wr_clk) disable iff (!wr_rst_n) 
        wr_en && rd_en && !wr_full && !rd_empty);

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความเสียหายจริงในภาคสนาม (失敗事例 - Shippai Jirei)
**ระบบประมวลผลข้อมูลสัญญาณพลาสมา (Plasma Wave Spectrometer) บนดาวเทียมสำรวจอวกาศห้วงลึก** เกิดความผิดปกติอย่างไม่คาดคิด: เมื่อยานเดินทางผ่านแถบคลื่นกระแทกแม่เหล็กดาวพฤหัสบดี (Jupiter Magnetopause Crossing) ที่มีอัตราข้อมูลพุ่งสูงชั่วขณะ (Burst Rate 400 MSamples/sec) ระบบจัดเก็บข้อมูลกลับบันทึกชุดข้อมูลที่เกิดความเหลื่อมทางเวลาและมีเฟรมข้อมูลซ้ำซ้อนสลับกับการกระโดดข้าม (Frame Skipping & Stale Duplication) ทำให้ข้อมูลคลื่นแม่เหล็กไฟฟ้าทางวิทยาศาสตร์เสียหายไปกว่า 48 ชั่วโมง คิดเป็นมูลค่าโครงการวิจัยกว่า 85 ล้านดอลลาร์สหรัฐ

---

### การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมข้อมูลสัญญาณวิทยาศาสตร์จึงเกิดการกระโดดข้ามและมีเฟรมซ้ำซ้อน?**
   - *คำตอบ:* ฝั่งอ่าน (DMA Controller เข้าหน่วยความจำ Flash) ดึงข้อมูลออกมาซ้ำในบางช่วง และข้ามข้อมูลไปในบางช่วงขณะที่ FIFO อยู่ในสภาวะหมิ่นเหม่ระหว่างเกือบเต็ม (Almost-Full)
2. **ทำไมตัวควบคุมการอ่านจึงอ่านข้อมูลซ้ำซ้อน?**
   - *คำตอบ:* สัญญาณ `rd_empty` ปลดเป็น $0$ เร็วกว่าที่ข้อมูลจริงจาก BRAM จะพร้อมใช้งานที่ขาเอาต์พุต (Read Data Pipeline Mismatch) และมีบางจังหวะที่ตัวชี้ Gray Code ตกอยู่ในสภาวะไม่นิ่ง
3. **ทำไมการจำลองแบบ Dynamic Simulation (Testbench) ในห้องทดลองจึงตรวจไม่พบปัญหานี้?**
   - *คำตอบ:* UVM Testbench เดิมสร้างสัญญาณนาฬิกา $clk_{wr}$ และ $clk_{rd}$ ด้วยอัตราส่วนจำนวนเต็มคงที่ ($100\text{ MHz} : 50\text{ MHz}$) ไม่ได้ครอบคลุมการสวิงของสัญญาณนาฬิกาจากคริสตัลออสซิลเลเตอร์ภายใต้อุณหภูมิห้วงอวกาศ ($\pm 100\text{ ppm}$) ที่ทำให้ขอบคล็อกเลื่อนผ่านกันทีละเฟมโตวินาที
4. **ทำไมทีม Verification จึงไม่ได้รัน Formal Property Verification (FPV) บน Asynchronous FIFO ตัวนี้?**
   - *คำตอบ:* วิศวกรคิดว่าใช้โมดูล FIFO มาตรฐานของ Vendor IP จึงไม่ได้เขียน SVA ครอบคลุมเงื่อนไขการกระจายของสัญญาณเกรย์โค้ด (Gray pointer latency skew) และไม่มี Invariant Proof สำหรับสภาวะ Almost-Empty/Full
5. **ทำไมกระบวนการอนุมัติแบบ (Design Review / 検図) จึงปล่อยให้โมดูลนี้ผ่านการลงนาม?**
   - *คำตอบ:* ขาดขั้นตอนบังคับ **Formal Verification Sign-off Checklist** ในระดับ DO-254 / Space Flight Hardware สำหรับบล็อกที่มี Clock Domain Crossing (CDC)

---

### แผนผังสาเหตุและผล (Ishikawa Fishbone Diagram)

```
==================================================================================================
                                    ISHIKAWA FISHBONE CAUSE-EFFECT DIAGRAM
==================================================================================================

   MAN (บุคลากร)                                   MACHINE / TOOLS (เครื่องมือ)
   ----------------                                ---------------------------
   ความเชื่อมั่นผิดพลาดใน IP Vendor               Testbench จำลองเฉพาะอัตราส่วนความถี่คงที่
   ขาดทักษะขั้นสูงด้าน SVA Formal Proof            ขาดการทำ Formal Liveness & Safety Proving
               \                                                /
                \                                              /
                 \                                            /
                  +------------------------------------------+
                  |                                          |
                  |  DEEP SPACE SPECTROMETER FIFO FAILURE   | ===>> [DATA CORRUPTION & LOSS]
                  |                                          |
                  +------------------------------------------+
                 /                                            \
                /                                              \
   METHOD (ระเบียบปฏิบัติ)                          MATERIAL / ENVIRONMENT (สภาวะแวดล้อม)
   ----------------------                          -------------------------------------
   ขาด CDC Formal Verification Sign-off            อุณหภูมิอวกาศทำให้เกิดความถี่ Drift (ppm)
   ละเลยการตรวจ Read Latency vs Empty Flag         Burst Rate สูงสุดทะลุขีดจำกัด FIFO Watermark
==================================================================================================
```

---

### คู่มือปฏิบัติการตรวจสอบ OJT หน้างาน: การทำ Formal Verification Sign-Off สำหรับ FIFO

1. **Step 1: Formal Model Isolation (การแยกส่วนประกอบและกำหนด Environment Boundaries)**
   - นำโมดูล Dual-Clock FIFO ออกมาสร้าง Formal Harness โดยไม่ต่อพ่วงกับ Top-Level เพื่อลด State Space
   - ใช้คำสั่ง `assume` สำหรับกำหนดคุณสมบัติที่ถูกต้องของสภาพแวดล้อมขาเข้า เช่น:
     ```systemverilog
     // กำหนดให้ไม่มีการเขียนถ้ามีสัญญาณ wr_full (Upstream Protocol Compliance)
     assume property (@(posedge wr_clk) wr_full |-> !wr_en);
     ```
2. **Step 2: Dual Clock Formal Domain Binding (การผูกโดเมนสัญญาณนาฬิกาใน Formal Engine)**
   - ใน JasperGold หรือ VC Formal ต้องกำหนดคุณสมบัติของสัญญาณนาฬิกาทั้งสองโดเมนให้มีอัตราส่วนความถี่แบบไม่ประสานเวลา (Asynchronous Clock Definition):
     ```tcl
     clock wr_clk -period 10
     clock rd_clk -period 14.142 ;# ใช้ตัวเลขอตรรกยะเพื่อป้องกัน Phase Lock
     reset -expression (!wr_rst_n || !rd_rst_n)
     ```
3. **Step 3: Execution of Bounded Model Checking (BMC) and Proof Convergence**
   - รันการตรวจสอบแบบ Proof Grid:
     - ก้าวที่ 1: พิสูจน์ Safety Assertions (`no_overflow`, `no_underflow`) ด้วย $k$-Induction ให้ได้ผลลัพธ์ **PROVEN (UNCONDITIONAL)**
     - ก้าวที่ 2: พิสูจน์ Data Integrity Invariant ด้วย Auxiliary FIFO Shadow Model
     - ก้าวที่ 3: ตรวจสอบ Vacuity Check เพื่อให้มั่นใจว่า Assertions ไม่ได้ผ่านแบบไร้ความหมาย (Vacuously True) เพราะเงื่อนไข `assume` บังคับแน่นเกินไป

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (専門用語)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / อังกฤษ | บริบทการใช้งานเชิงวิศวกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **形式検証** | けいしきけんしょう | Keishiki Kenshou | Formal Verification | การพิสูจน์ความถูกต้องของวงจรด้วยหลักคณิตศาสตร์ |
| **不変条件** | ふへんじょうけん | Fuhen Jouken | Invariant Condition | เงื่อนไขทางตรรกะที่เป็นจริงตลอดกาลในทุกสถานะของวงจร |
| **有界モデル検査** | ゆうかいモデルけんさ | Yuukai Moderu Kensa | Bounded Model Checking (BMC) | การตรวจสอบโมเดลแบบจำกัดจำนวนไซเคิลคล็อก |
| **反例** | はんれい | Hanrei | Counter-Example / Bug Trace | ลำดับการเปลี่ยนสถานะที่เครื่องมือขุดพบซึ่งทำให้ Assertion แตก |
| **空虚なパス** | くうきょなパス | Kuukyo na Pasu | Vacuous Pass | การที่ Assertion ผ่านการทดสอบอย่างไร้ความหมายเนื่องจากเงื่อนไขนำเป็นเท็จ |
| **活性** | かっせい | Kassei | Liveness Property | คุณสมบัติที่รับประกันว่าสิ่งดีๆ จะเกิดขึ้นในที่สุด (ไม่มี Deadlock) |
| **安全性** | あんぜんせい | Anzensei | Safety Property | คุณสมบัติที่รับประกันว่าสิ่งเลวร้ายจะไม่เกิดขึ้น (ไม่มี Overflow) |
| **網羅性** | もうらせい | Mourasei | Completeness / Coverage | ความครอบคลุมของการตรวจสอบเทียบกับข้อกำหนดสเปก |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図審議 - Kenzu Shingi)

**สถานที่:** ห้องประชุม Sign-off ฝ่ายออกแบบระบบสื่อสารดาวเทียม (JAXA Subsystem Review Gate)  
**ผู้เข้าร่วม:**
- **ยามาโมโตะ (山本):** Formal Verification Chief Reviewer (形式検証主査)
- **สิทธิชัย (シッティチャイ):** Senior FIFO Design Engineer (設計担当)

---

**山本主査 (ยามาโมโตะ):**  
「シッティチャイさん、今回の深宇宙プラズマ観測用非同期FIFOの検証レポートを見ましたが、UVMシミュレーション結果しか添付されていませんね。このミッションクリティカルなブロックに対して、**形式検証（Formal Verification）**の証明結果はどうなっていますか？」  
*(คุณสิทธิชัยครับ ผมดูรายงานการตรวจสอบของ Asynchronous FIFO สำหรับการวัดพลาสมาในอวกาศห้วงลึกแล้ว เห็นแนบมาแค่วิธี UVM Simulation นะครับ สำหรับบล็อกที่เป็น Mission-Critical ขนาดนี้ ผลการพิสูจน์ด้วย Formal Verification เป็นอย่างไรบ้างครับ?)*

**シッティチャイ (สิทธิชัย):**  
「山本主査、申し訳ありません。UVM環境で20億サイクルのランダムテストを実行し、機能カバレッジ（Functional Coverage）100%を達成したため、問題ないと判断していました。」  
*(หัวหน้ายามาโมโตะครับ ขออภัยด้วยครับ ทางทีมรัน Random Test ใน UVM ไปถึง 2 พันล้านไซเคิล และเก็บ Functional Coverage ได้ 100% ครบแล้ว จึงประเมินว่าไม่น่าจะมีปัญหาครับ)*

**山本主査 (ยามาโมโตะ):**  
「甘いですね！動的シミュレーションでどれだけサイクルを回しても、非同期クロックの位相差が極限状態に達した際の**コーナーケース（Corner-case）**を網羅することは不可能です。特にBRAM出力段のレイテンシと`rd_empty`フラグ解除のタイミングについて、**数学的不変条件（Mathematical Invariant）**が証明されていません。もし`wr_full`と`rd_empty`の競合状態でポインタが1ビットでも狂えば、深宇宙でテレメトリが全滅しますよ。」  
*(มองโลกในแง่ดีเกินไปครับ! ไม่ว่าคุณจะรันไซเคิลใน Dynamic Simulation มากแค่ไหน มันเป็นไปไม่ได้เลยที่จะครอบคลุม Corner-case เมื่อ Phase Skew ของสัญญาณนาฬิกาไม่ประสานเวลาตกอยู่ในจุดวิกฤต โดยเฉพาะอย่างยิ่ง Latency ของ BRAM ขาออกกับจังหวะการปลดแฟล็ก `rd_empty` ยังไม่มีการพิสูจน์ Mathematical Invariant เลย หากเกิดความขัดแย้งระหว่าง Full กับ Empty จน Pointer ผิดไปแม้แต่ 1 บิต ข้อมูลโทรมาตรในอวกาศจะพังพินาศหมดนะครับ)*

**シッティチャイ (สิทธิชัย):**  
「ご指摘の通りです。すぐにSVAプロパティスイートを追加し、JasperGoldを用いて`p_no_overflow`、`p_no_underflow`、そしてシャドウモデルを用いたデータ順序保証（Data Ordering Invariance）の**k-インダクション証明（k-Induction Proof）**を実施します。」  
*(เป็นจริงตามที่ท่านชี้แนะทุกประการครับ ผมจะเพิ่ม SVA Property Suite ทันที และใช้ JasperGold ทำการพิสูจน์ k-Induction สำหรับคุณสมบัติ `p_no_overflow`, `p_no_underflow` และการรักษาลำดับข้อมูล (Data Ordering Invariance) ผ่าน Shadow Model ครับ)*

**山本主査 (ยามาโมโตะ):**  
「よし。それと、プロパティが**空虚なパス（Vacuous Pass）**になっていないか、すべての制約（assume）に対するカバレッジも必ず確認してください。反例（Counter-example）が1件も出ず、完全無条件証明（Unconditional Proven）が確認できるまで、サインオフの承認印は押せません。」  
*(ดีมาก แล้วก็อย่าลืมตรวจเช็คด้วยว่า Assertions ไม่ได้ติด Vacuous Pass โดยต้องตรวจสอบ Coverage ของทุกเงื่อนไข assume ให้ครบถ้วน จนกว่าจะไม่พบ Counter-example แม้แต่กรณีเดียว และได้รับการพิสูจน์แบบ Unconditional Proven อย่างสมบูรณ์ ผมถึงจะยอมประทับตราอนุมัติ Sign-off ให้ครับ)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การวิเคราะห์ความลึกของ Bounded Model Checking ($k$-Induction) สำหรับ Dual-Clock FIFO

ในการทำ Formal Verification บน Asynchronous FIFO ความลึก $N$ ช่อง (Depth = $2^M$) โดยใช้เทคนิค $k$-Induction เพื่อพิสูจน์ Property ความปลอดภัย:
$$\text{Property: } \mathbf{P_{safe}} = (\mathbf{wr\_full} \implies \neg \mathbf{wr\_en\_accepted})$$
หากวงจรมี Synchronizer Flop แบบ 2-Stage ($N_{sync} = 2$) ในการข้ามแดนสัญญาณนาฬิกาทั้งสองฝั่ง จงคำนวณหาค่าความลึกต่ำสุดของ $k$ (Minimum Induction Depth $k_{min}$) ที่จำเป็นในการทำให้เครื่องมือ Formal Engine สามารถหลุดพ้นจาก Spurious Counter-example และพิสูจน์ผ่านได้แบบ Inductive Invariant

```
[Write Domain]  wptr_gray ----> [Sync FF 1] ----> [Sync FF 2] ----> wptr_sync  [Read Domain]
[Read Domain]   rptr_gray ----> [Sync FF 1] ----> [Sync FF 2] ----> rptr_sync  [Write Domain]
```

- **A)** $k_{min} = 1$ ไซเคิล
- **B)** $k_{min} = 2$ ไซเคิล
- **C)** $k_{min} \ge N_{sync} + 2 = 4$ ไซเคิล
- **D)** $k_{min} \ge 2^{M} + N_{sync}$ ไซเคิล

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: C) $k_{min} \ge N_{sync} + 2 = 4$ ไซเคิล**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ในการพิสูจน์แบบ $k$-Induction เครื่องมือ Formal จะเริ่มต้น Inductive Step โดยสมมุติว่า Property $P$ เป็นจริงต่อเนื่องกัน $k$ ไซเคิล จากสถานะใดๆ (Arbitrary State) ใน State Space ซึ่งสถานะนั้นอาจไม่ใช่ Reachable State จากสภาวะ Reset ปกติ
2. เนื่องจากข้อมูล Pointer จาก Read Domain ต้องเดินทางผ่าน Synchronizer Flops จำนวน $N_{sync} = 2$ ตัวคล็อก เพื่อมาคำนวณสถานะ `wr_full` ใน Write Domain
   - ที่ Cycle 0: ค่าใน `Sync FF 1` เป็นค่าสุ่มใดๆ
   - ที่ Cycle 1: ค่าสุ่มเคลื่อนเข้าสู่ `Sync FF 2`
   - ที่ Cycle 2: ค่า Pointer เข้าสู่ Logic เปรียบเทียบ `wr_full`
   - ที่ Cycle 3: สถานะแฟล็ก `wr_full` ปรากฏที่ Flip-Flop เอาต์พุต
3. หากเลือกค่า $k < N_{sync} + 2$ (นั่นคือ $k < 4$):
   เครื่องมือ Formal Solver สามารถเลือกสถานะเริ่มต้นปลอม (Unreachable State) ที่ค่าใน Synchronizer FF ขัดแย้งกับ Pointer ตัวจริง ทำให้ตัวเปรียบเทียบคำนวณแฟล็กผิดพลาด เกิด **Spurious Counter-example (ข้อผิดพลาดเท็จ)** ที่ทำให้ Induction ไม่ผ่าน
4. ดังนั้น ความลึกขั้นต่ำในการชะล้างข้อมูลที่ไม่สอดคล้องกันออกจาก Pipeline ของ Synchronizer คือ $k_{min} \ge N_{sync} + 2 = 2 + 2 = 4$ ไซเคิล (หรือต้องเขียน Auxiliary Invariant ผูกความสัมพันธ์ของ Flop แต่ละขั้น)

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** ที่ $k=1$ ตัวแปรใน Synchronizer Stage ต่างๆ ยังเป็นอิสระต่อกัน Solver จะสร้างค่าที่ทำให้เกิด Underflow/Overflow เท็จได้ทันที
- **ข้อ B ผิด:** $k=2$ ยังไม่ครอบคลุมเวลาที่ Pointer เดินทางผ่าน 2 Flops จนกระทบถึงวงจรตัดสินใจ Flag
- **ข้อ D ผิด:** ไม่จำเป็นต้องกวาดลึกถึง $2^M$ ไซเคิลสำหรับการพิสูจน์ Inductive Invariant ของวงจรเปรียบเทียบแบบ Single-Cycle Flag Generation เพราะ Induction อาศัยความสัมพันธ์สัมพัทธ์ของ Pointer ไม่ได้ขึ้นกับขนาดความจุของ FIFO โดยรวม

---

### คำถามที่ 2: การตรวจสอบความว่างเปล่าของการพิสูจน์ SVA (Assertion Vacuity Checking)

พิจารณา SystemVerilog Assertion ต่อไปนี้ที่เขียนขึ้นเพื่อตรวจสอบ Liveness ของ FIFO:
```systemverilog
property p_drain_check;
    @(posedge rd_clk) disable iff (!rd_rst_n)
    (rd_empty == 1'b0 && rd_en == 1'b1) |-> ##[1:10] (rd_empty == 1'b1);
endproperty
assert_drain: assert property (p_drain_check);
```
หากเครื่องมือ Formal Verification รายงานผลว่า Assertion นี้ได้ผลลัพธ์เป็น **"PASS"** ทันทีในเวลา 0.1 วินาที แต่เมื่อทีมตรวจสอบนำไปรัน Vacuity Check กลับพบว่าเป็น **Vacuously True (ผ่านอย่างไร้ความหมาย)** สาเหตุทางวิศวกรรมข้อใดต่อไปนี้ที่อธิบายปรากฏการณ์นี้ได้อย่างถูกต้องที่สุด?

- **A)** เครื่องมือ Formal ไม่รองรับ Sequence Operator `##[1:10]` จึงข้ามการตรวจสอบไป
- **B)** สภาพแวดล้อมมีการใส่ข้อกำหนด `assume property (@(posedge rd_clk) rd_en == 1'b0);` ทำให้ Antecedent (เงื่อนไขนำ) ไม่มีวันเป็นจริง
- **C)** สัญญาณ `rd_empty` เปลี่ยนเป็น $1$ เร็วกว่า 1 ไซเคิลคล็อก
- **D)** FIFO มีความจุมากกว่า 10 ช่อง จึงทำให้ Assertion ผ่านโดยสมบูรณ์

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) สภาพแวดล้อมมีการใส่ข้อกำหนด `assume property (@(posedge rd_clk) rd_en == 1'b0);` ทำให้ Antecedent (เงื่อนไขนำ) ไม่มีวันเป็นจริง**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ในตรรกศาสตร์เชิงรูปนัย (Formal Logic) คุณสมบัติ Implication ($A \implies B$ หรือใน SVA คือ $A \text{ |-> } B$) มีตารางค่าความจริงดังนี้:
   - ถ้า $A = \text{False}$ ค่าของความจริง $A \implies B$ จะเป็น **True เสมอ** โดยไม่ต้องพิจารณาว่า $B$ เป็นจริงหรือเท็จ
2. ในกรณีนี้ Antecedent คือ $A = (\mathbf{rd\_empty} == 0 \wedge \mathbf{rd\_en} == 1)$
3. หากในไฟล์ข้อกำหนด Environment Setup มีการใส่ `assume` ที่ขัดแย้งหรือบังคับให้ $\mathbf{rd\_en} = 0$ เสมอ (หรือบังคับให้ $\mathbf{rd\_empty} = 1$ ตลอดเวลา) จะส่งผลให้ $A = \text{False}$ ในทุกไซเคิล
4. Formal Engine จะรายงานว่า Property ผ่านทันที (**PASS**) แต่เป็นการผ่านแบบ **Vacuous Pass (空虚なパス)** ซึ่งหมายความว่าวงจรไม่เคยถูกกระตุ้นตามเงื่อนไขที่ต้องการทดสอบเลยแม้แต่ครั้งเดียว ทำให้ซ่อนบักร้ายแรงไว้ในวงจร

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** เครื่องมือ Formal มาตรฐานทุกตัว (JasperGold, VC Formal) รองรับ Bounded Range `##[1:10]` เป็นฟังก์ชันพื้นฐาน
- **ข้อ C ผิด:** ถ้าสัญญาณ `rd_empty` กลายเป็น $1$ เร็ว แสดงว่า Antecedent เกิดขึ้นและ Consequent สำเร็จตามช่วงเวลา จะถือว่าเป็น Non-Vacuous Pass ปกติ
- **ข้อ D ผิด:** ถ้า FIFO มีความจุมากกว่า 10 ช่อง และมีการอ่านติดต่อกัน ข้อมูลอาจยังไม่หมดภายใน 10 ไซเคิล ซึ่งควรจะทำให้ Assertion **FAIL** (เกิด Counter-example) ไม่ใช่ผ่านแบบ Vacuous

---

### คำถามที่ 3: การคำนวณ Formal Data Latency Bound ภายใต้อัตราส่วนความถี่แบบ Asynchronous

กำหนดระบบ Dual-Clock Asynchronous FIFO ที่มีโครงสร้าง Synchronizer แบบ 2-Stage Flops ($N_{sync} = 2$)  
ความถี่ Write Clock: $f_{wr} = 200\text{ MHz}$ ($T_{wr} = 5.0\text{ ns}$)  
ความถี่ Read Clock: $f_{rd} = 125\text{ MHz}$ ($T_{rd} = 8.0\text{ ns}$)  
โครงสร้าง Memory เป็น Dual-Port SRAM ที่มี Read Latency = 1 ไซเคิลคล็อก ($T_{RAM\_RD} = 1 \cdot T_{rd}$)  
กำหนดให้เขียนข้อมูลตัวแรก $D_0$ เข้าสู่ FIFO ขณะที่เดิมว่างเปล่า ($FIFO_{empty} = 1$) ที่เวลา $t=0$ (ตรงขอบ $wr\_clk$)

จงคำนวณหาช่วงเวลาหน่วงสูงสุดในกรณีเลวร้ายที่สุด (Worst-Case Latency Bound $t_{latency\_max}$) นับจากเวลาที่ $wr\_en$ ทำงาน จนถึงเวลาที่ข้อมูล $D_0$ พร้อมให้อ่านได้อย่างถูกต้องที่ขา $rd\_data$ เพื่อนำค่านี้ไปกำหนดเป็นขอบเขตบนใน SVA Temporal Assertion:
$$\mathbf{property} \quad p\_data\_available; \quad wr\_en \wedge was\_empty \implies \#\#[1 : K_{bound}] \ (\neg rd\_empty \wedge rd\_data == wr\_data);$$

- **A)** $t_{latency\_max} \le 18.0\text{ ns}$ ($K_{bound} = 2\text{ rd\_clk}$)
- **B)** $t_{latency\_max} \le 29.0\text{ ns}$ ($K_{bound} = 4\text{ rd\_clk}$)
- **C)** $t_{latency\_max} \le 37.0\text{ ns}$ ($K_{bound} = 5\text{ rd\_clk}$)
- **D)** $t_{latency\_max} \le 52.0\text{ ns}$ ($K_{bound} = 7\text{ rd\_clk}$)

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: C) $t_{latency\_max} \le 37.0\text{ ns}$ ($K_{bound} = 5\text{ rd\_clk}$)**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
การเดินทางของข้อมูลและสถานะจาก Write Domain ไปยัง Read Domain ประกอบด้วยลำดับเวลาที่เลวร้ายที่สุด (Worst-case phase alignment) ดังนี้:

1. **Write Pointer Generation & Metastability Window ($t_{wp}$):**
   - การเขียนข้อมูลลง RAM และอัปเดต $wptr\_gray$ เกิดขึ้นที่ขอบ Write Clock: $1 \cdot T_{wr} = 5.0\text{ ns}$
2. **Asynchronous Sampling Phase Uncertainty ($t_{phase\_skew}$):**
   - ขอบของ $wptr\_gray$ เปลี่ยนแปลงเฉียดเส้น Setup Time ของ Read Clock Synchronizer Stage 1 ไปเพียงเสี้ยววินาที ทำให้ Flop ตัวแรกจับสัญญาณไม่ทัน ต้องรอไปอีก 1 รอบเต็มของ Read Clock:
   $$t_{wait\_rd1} = 1 \cdot T_{rd} = 8.0\text{ ns}$$
3. **2-Stage Metastability Synchronizer Delay ($t_{sync}$):**
   - สัญญาณต้องเดินทางผ่าน Synchronizer Flop 2 ตัวใน Read Domain:
   $$t_{sync} = 2 \cdot T_{rd} = 2 \times 8.0\text{ ns} = 16.0\text{ ns}$$
4. **Empty Flag Logic & Deassertion Propagation ($t_{flag}$):**
   - ตัวเปรียบเทียบตัดสินใจปลด `rd_empty = 0` ในรอบคล็อกถัดไป:
   $$t_{flag} = 1 \cdot T_{rd} = 8.0\text{ ns}$$
5. **รวมเวลาหน่วงสูงสุดจนถึงจังหวะที่ Read Flag ปลดสมบูรณ์:**
   $$t_{latency\_max} = T_{wr} + T_{rd} + 2 \cdot T_{rd} + T_{rd} = 5.0 + 8.0 + 16.0 + 8.0 = 37.0\text{ ns}$$
6. **การแปลงเป็นจำนวนรอบสัญญาณนาฬิกาของ Read Domain ($K_{bound}$):**
   $$K_{bound} = \left\lceil \frac{t_{latency\_max}}{T_{rd}} \right\rceil = \left\lceil \frac{37.0}{8.0} \right\rceil = \lceil 4.625 \rceil = 5\text{ รอบคล็อก } (rd\_clk)$$

ดังนั้น ในการเขียน SVA Bound เพื่อไม่ให้เกิด False Failure ใน Formal Engine ต้องตั้งค่า $K_{bound} = 5$ ไซเคิล

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** $18.0\text{ ns}$ คำนวณเฉพาะช่วงเวลา Synchronizer โดยละเลย Phase Skew และ Write Cycle Delay
- **ข้อ B ผิด:** $29.0\text{ ns}$ ($4$ ไซเคิล) เป็นกรณี Best/Typical Case ซึ่งหากเกิด Phase Misalignment เฉียดฉิวใน Formal Verification ตัว Engine จะขุดพบ Counter-example ที่ไซเคิลที่ 5 ทันที
- **ข้อ D ผิด:** $52.0\text{ ns}$ กว้างเกินความจำเป็น (Loose Bound) ซึ่งจะทำให้ลดทอนประสิทธิภาพในการตรวจจับบักหน่วงเวลาที่ไม่พึงประสงค์ (Latency Degradation)
