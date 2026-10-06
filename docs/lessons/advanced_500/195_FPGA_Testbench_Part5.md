# Lesson 195: FPGA Testbench Part 5 — SVA & Formal Property Verification in Simulation (การยืนยันคุณสมบัติเชิงฟอร์มัลและการประยุกต์ใช้ SystemVerilog Assertions ในการจำลอง)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในการตรวจสอบวงจรระดับลึก การเฝ้าดูเฉพาะสัญญาณที่ขาพินภายนอก (Black-Box Verification ผ่าน Monitor และ Scoreboard) มีข้อจำกัดที่เรียกว่า **"Bug Latency Problem"**: เมื่อเกิดข้อผิดพลาดขึ้นในสถานะภายในลึกๆ ของวงจร (เช่น บิตสถานะของ Arbiter ผิด หรือ Pointer ของคิวล้นไป 1 บิต) กว่าที่ผลกระทบนั้นจะเดินทางทะลุผ่าน Pipeline Stages หลายสิบชั้นจนกระทั่งปรากฏเป็นความเสียหายที่ขาพินภายนอก อาจต้องใช้เวลาอีกหลายร้อยหรือหลายพันไซเคิลคล็อก ทำให้การแกะรอยหาสาเหตุรากเหง้า (Root Cause Localization) ทำได้ยากลำบากอย่างยิ่ง

**Assertion-Based Verification (ABV)** โดยใช้ **SystemVerilog Assertions (SVA - IEEE 1800)** เข้ามาแก้ปัญหานี้โดยการทำหน้าที่เป็น "White-Box Sensor" ที่ฝังตัวอยู่ตามจุดสำคัญทั่วทั้ง RTL และ Testbench เพื่อตรวจจับความผิดปกติที่จุดเกิดเหตุทันทีภายในไซเคิลที่เกิดความผิดพลาด (Zero Bug Latency) และข้อดีสูงสุดของ SVA คือมันเป็น **ภาษาคู่ขนาน (Dual-Use Formal Language)** ที่สามารถนำไปรันได้ทั้งใน **Dynamic Simulation** และเครื่องมือ **Formal Property Verification (FPV)**

```
+--------------------------------------------------------------------------------------------------+
|               SYSTEMVERILOG ASSERTIONS (SVA) EXECUTION IN SIMULATION ENGINE                      |
+--------------------------------------------------------------------------------------------------+
                                                                                                    
                  IEEE 1800 SIMULATION SCHEDULING TIME SLOT                                         
  =============================================================================                     
  [1] PREPONED REGION  : Values sampled for Concurrent Assertions (Noise-Free)                     
  -----------------------------------------------------------------------------                     
  [2] ACTIVE REGION    : RTL Combinational evaluations, Blocking assignments (=)                    
  -----------------------------------------------------------------------------                     
  [3] INACTIVE REGION  : #0 procedural updates                                                      
  -----------------------------------------------------------------------------                     
  [4] NBA REGION       : Non-blocking assignments updates (<=) (Clocked Flops)                      
  -----------------------------------------------------------------------------                     
  [5] OBSERVED REGION  : Evaluation of Concurrent Assertion Properties                              
  -----------------------------------------------------------------------------                     
  [6] REACTIVE REGION  : Assertion Pass/Fail Action Blocks ($error, $fatal)                         
  -----------------------------------------------------------------------------                     
  [7] POSTPONED REGION : $strobe, Waveform dump ($dumpvars)                                         
  =============================================================================                     
```

---

### 1.1 ลำดับเวลาในการประมวลผลและการขจัดปัญหา Glitch (Simulation Scheduling Physics)

ความผิดพลาดที่วิศวกรมือใหม่พบบ่อยที่สุดคือการใช้ **Immediate Assertions (`assert (cond)`)** ภายในบล็อกลอจิกเชิงผสมผสาน (`always_comb`) ซึ่งส่งผลให้เกิดการแจ้งเตือนข้อผิดพลาดหลอก (Spurious Glitch Failures) เนื่องจากสัญญาณอินพุตเดินทางผ่านเกตลอจิกด้วยความเร็วไม่เท่ากัน ทำให้เกิด Hazard สั้นๆ ก่อนที่เอาต์พุตจะนิ่ง

#### 1. กลไกของ Concurrent Assertions
Concurrent Assertions ถูกออกแบบมาเพื่อแก้ปัญหานี้อย่างเด็ดขาดโดยอาศัยพื้นที่เวลาตามมาตรฐาน IEEE 1800:
1. **Sampling at Preponed Region:** ค่าของสัญญาณทั้งหมดที่ใช้ในการคำนวณ Property จะถูกสุ่มบันทึกค่าไว้ตั้งแต่ **Preponed Region** (ซึ่งเป็นช่วงเวลาก่อนที่ขอบสัญญาณนาฬิกาจะเปลี่ยนแปลงในไซเคิลนั้น) จึงรับประกันว่าจะได้ค่าที่นิ่งและปราศจาก Glitch เสมอ
2. **Evaluation at Observed Region:** การประเมินสมการบูลีนเชิงเวลาจะเกิดขึ้นใน **Observed Region** หลังจากที่วงจร Flip-Flop ทั้งหมดอัปเดตสถานะใน NBA Region เรียบร้อยแล้ว
3. **Execution at Reactive Region:** หาก Assertion ไม่ผ่าน โค้ดในส่วน Action Block เช่น `$error()` หรือ `$fatal()` จะถูกสั่งประมวลผลใน **Reactive Region**

#### 2. คณิตศาสตร์ของ Temporal Operators และ Implication

- **Overlapping Implication (`|->`):**
  หากเงื่อนไขนำ (Antecedent $P$) เป็นจริงที่ไซเคิลปัจจุบัน ผลลัพธ์ตาม (Consequent $Q$) จะต้องเป็นจริง **ในไซเคิลเดียวกันทันที**:
  $$(P \ |-> \ Q) \equiv \forall t: P(t) \implies Q(t)$$

- **Non-Overlapping Implication (`|=>`):**
  หากเงื่อนไขนำเป็นจริงที่ไซเคิลปัจจุบัน ผลลัพธ์ตามจะต้องเป็นจริง **ในรอบคล็อกถัดไป ($1$ ไซเคิลข้างหน้า)**:
  $$(P \ |=> \ Q) \equiv \forall t: P(t) \implies Q(t + 1)$$
  มีความหมายเทียบเท่ากับ $P \ |-> \ \#\#1 \ Q$

- **Repetition Operators:**
  - **Consecutive Repetition (`a [* 3]`):** สัญญาณ $a$ ต้องมีค่าเป็นจริงติดต่อกัน 3 ไซเคิลรวด ($a \wedge \#\#1 \ a \wedge \#\#1 \ a$)
  - **Non-Consecutive Repetition (`a [= 3]`):** สัญญาณ $a$ ต้องปรากฏเป็นจริงครบ 3 ไซเคิล ณ เวลาใดๆ ก็ได้ โดยหลังจากที่ครบ 3 ครั้งแล้ว สัญญาณสามารถคงอยู่หรือเปลี่ยนไปได้ก่อนที่จะเกิดเงื่อนไขถัดไป
  - **Goto Repetition (`a [-> 3]`):** สัญญาณ $a$ ต้องปรากฏเป็นจริงครบ 3 ไซเคิล และการตรวจสอบขั้นถัดไปต้องเกิดขึ้น **ณ ไซเคิลที่ $a$ กลายเป็นจริงเป็นครั้งที่ 3 นั้นทันที**

---

### 1.2 ฟังก์ชันวิเคราะห์การเปลี่ยนสถานะสัญญาณ (Built-in System Functions)

- `$rose(sig)`: สัญญาณเปลี่ยนจาก $0 \to 1$ (เทียบกับค่าใน Preponed ของไซเคิลก่อนหน้า)
- `$fell(sig)`: สัญญาณเปลี่ยนจาก $1 \to 0$
- `$stable(sig)`: สัญญาณคงที่เดิม ไม่มีการเปลี่ยนแปลง ($sig == \$past(sig)$)
- `$past(sig, k)`: ค่าของสัญญาณเมื่อ $k$ รอบสัญญาณนาฬิกาก่อนหน้า
- `$onehot(sig)`: บิตในเวกเตอร์มีค่าเป็น $1$ ได้เพียงบิตเดียวเท่านั้น (Exactly one bit high)
- `$onehot0(sig)`: บิตในเวกเตอร์มีค่าเป็น $1$ ได้สูงสุดไม่เกิน 1 บิต (At most one bit high, 0 or 1)

---

### 1.3 RTL Code: Master SVA Suite สำหรับ Multi-Channel Round-Robin Arbiter

ตัวอย่างนี้สาธิตโมดูล **4-Channel High-Speed Arbiter** พร้อมชุดคำสั่ง SVA เต็มรูปแบบเพื่อการันตี Mutual Exclusion, การตอบสนองต่อคำขอในเวลาจำกัด (Bounded Latency), และความปราศจากการอดอยากของสัญญาณ (Starvation-Free Proof)

```systemverilog
//=============================================================================
// Module: arbiter_4ch_with_sva
// Description: 4-Channel Arbiter with Comprehensive SVA Property Suite
// Standards: DO-254 DAL-A / ISO 26262 ASIL-D Formal Verification Standards
//=============================================================================

`timescale 1ns / 1ps

module arbiter_4ch_with_sva (
    input  logic       clk,
    input  logic       rst_n,
    input  logic [3:0] req,
    output logic [3:0] gnt
);

    // Simple Priority/Round-Robin Logic (Arbitration State)
    logic [1:0] current_ptr;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            gnt         <= 4'b0000;
            current_ptr <= 2'b00;
        end else begin
            // Clear grant by default
            gnt <= 4'b0000;

            // Grant generation based on active requests
            case (current_ptr)
                2'd0: if (req[0]) gnt[0] <= 1'b1; else if (req[1]) gnt[1] <= 1'b1;
                2'd1: if (req[1]) gnt[1] <= 1'b1; else if (req[2]) gnt[2] <= 1'b1;
                2'd2: if (req[2]) gnt[2] <= 1'b1; else if (req[3]) gnt[3] <= 1'b1;
                2'd3: if (req[3]) gnt[3] <= 1'b1; else if (req[0]) gnt[0] <= 1'b1;
            endcase

            // Update arbitration pointer
            if (|req) begin
                current_ptr <= current_ptr + 1'b1;
            end
        end
    end

    //=========================================================================
    // SYSTEMVERILOG ASSERTIONS (SVA) PROTOCOL CHECKERS
    //=========================================================================

    //-------------------------------------------------------------------------
    // Property 1: Mutual Exclusion (Safety Invariant)
    // สัญญาณ Grant จะต้องมีค่าเป็น 1 ได้พร้อมกันไม่เกิน 1 ช่องทางเสมอ
    //-------------------------------------------------------------------------
    property p_mutual_exclusion;
        @(posedge clk) disable iff (!rst_n)
        $onehot0(gnt);
    endproperty
    a_mutual_exclusion: assert property (p_mutual_exclusion)
        else $fatal(1, "[FATAL][SVA-ARB-01] Mutual Exclusion Violated! Multiple Grants Active: %b", gnt);

    //-------------------------------------------------------------------------
    // Property 2: No Spurious Grants (No Phantom Grant)
    // การให้ Grant จะต้องเกิดขึ้นก็ต่อเมื่อช่องทางนั้นมีการร้องขอ (req) อยู่จริง
    //-------------------------------------------------------------------------
    genvar i;
    generate
        for (i = 0; i < 4; i++) begin : gen_spurious_check
            property p_no_spurious_grant;
                @(posedge clk) disable iff (!rst_n)
                gnt[i] |-> (req[i] || $past(req[i]));
            endproperty
            a_no_spurious_grant: assert property (p_no_spurious_grant)
                else $error("[ERROR][SVA-ARB-02] Spurious Grant on Ch[%0d] without active Request!", i);
        end
    endgenerate

    //-------------------------------------------------------------------------
    // Property 3: Handshake Stability & Latch
    // หากช่องทางใดได้รับ Grant แล้ว และยังคง Req ค้างอยู่ สถานะ Grant จะต้องคงที่
    // จนกว่าการส่งมอบจะเสร็จสิ้น
    //-------------------------------------------------------------------------
    property p_gnt_duration;
        @(posedge clk) disable iff (!rst_n)
        (gnt[0] && req[0]) |=> (gnt[0] || !req[0]);
    endproperty
    // a_gnt_duration: assert property (p_gnt_duration);

    //-------------------------------------------------------------------------
    // Property 4: Bounded Grant Latency & Starvation Freedom (Liveness)
    // หากช่องทาง k มีการร้องขอแบบต่อเนื่อง (Req ค้าง) ระบบต้องให้ Grant ภายใน 4 ไซเคิล
    //-------------------------------------------------------------------------
    generate
        for (i = 0; i < 4; i++) begin : gen_starvation_check
            property p_bounded_latency;
                @(posedge clk) disable iff (!rst_n)
                req[i] |-> ##[1:4] gnt[i];
            endproperty
            a_bounded_latency: assert property (p_bounded_latency)
                else $fatal(1, "[FATAL][SVA-ARB-04] Starvation Detected! Ch[%0d] not granted within 4 cycles", i);
        end
    endgenerate

    //-------------------------------------------------------------------------
    // SVA COVERAGE PROPERTIES (Reachability Check)
    //-------------------------------------------------------------------------
    // ตรวจสอบว่าทุกช่องทางเคยได้รับการ Grant และเคยมีเหตุการณ์แย่งชิงพร้อมกันทั้ง 4 พอร์ต
    c_all_req_conflict: cover property (@(posedge clk) disable iff (!rst_n) req == 4'b1111);
    c_ch0_granted:      cover property (@(posedge clk) disable iff (!rst_n) gnt[0]);
    c_ch1_granted:      cover property (@(posedge clk) disable iff (!rst_n) gnt[1]);
    c_ch2_granted:      cover property (@(posedge clk) disable iff (!rst_n) gnt[2]);
    c_ch3_granted:      cover property (@(posedge clk) disable iff (!rst_n) gnt[3]);

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความเสียหายจริงในภาคสนาม (失敗事例 - Shippai Jirei)
**ตัวควบคุมสวิตช์เราเตอร์ใยแก้วนำแสงความเร็วสูงในศูนย์ข้อมูลคลาวด์ (Multi-Terabit Crossbar Packet Switch ASIC)** เกิดสภาวะหยุดส่งสัญญาณฉับพลัน (Network Traffic Freeze / Complete Livelock): เมื่อทราฟฟิกของดาต้าเซ็นเตอร์พุ่งแตะระดับ 94% สวิตช์เกิดอาการไม่ส่งต่อแพ็กเก็ตใดๆ ออกจากคิว แม้ว่าพอร์ตปลายทางจะว่าง ส่งผลให้เครื่องเซิร์ฟเวอร์สำหรับบริการ AI inference กว่า 1,200 เครื่องขาดการติดต่อจากอินเทอร์เน็ตทันที ความเสียหายจากค่าปรับตามข้อตกลงระดับการให้บริการ (SLA Penalty) สูงถึง 3.5 ล้านดอลลาร์สหรัฐ

---

### การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมสวิตช์ใยแก้วนำแสงจึงหยุดส่งผ่านข้อมูลเมื่อโหลดทราฟฟิกสูง?**
   - *คำตอบ:* วงจรจัดสรรทรัพยากร (Arbiter) ระหว่าง Virtual Output Queues (VOQs) เข้าสู่สภาวะรอคอยซึ่งกันและกัน (Circular Wait State / Deadlock)
2. **ทำไม Arbiter จึงเกิด Circular Wait State?**
   - *คำตอบ:* ตรรกะหมุนเวียนลำดับความสำคัญ (Round-Robin Pointer Update) ถูกบล็อกโดยสัญญาณ Backpressure ที่ข้ามช่องทาง ทำให้ตัวชี้ค้างอยู่ที่แชนเนล 0 ตลอดเวลา
3. **ทำไมช่องทางอื่นจึงเกิดอาการอดอยาก (Starvation) โดยที่ระบบตรวจไม่พบ?**
   - *คำตอบ:* สัญญาณ Request ของแชนเนล 1, 2, 3 ค้างอยู่ที่ $1$ ตลอดเวลา แต่ Arbiter ไม่เคยปล่อยสัญญาณ Grant ให้เลย
4. **ทำไม Testbench ของทีม Verification จึงไม่สามารถตรวจจับปัญหานี้ได้ก่อน Tape-out?**
   - *คำตอบ:* Testbench ใช้วิธีการแบบ End-to-End Black-Box ตรวจสอบเฉพาะแพ็กเก็ตที่สำเร็จ แต่ไม่มีการเขียน **Concurrent SVA Starvation Assertions (`req |-> ##[1:N] gnt`)** เพื่อเฝ้าดูความล่าช้าสูงสุดของแต่ละคิวภายในวงจร
5. **ทำไมขั้นตอน Kenzu (検図) จึงปล่อยให้อนุมัติแบบวงจรนี้?**
   - *คำตอบ:* ทีมตรวจแบบขาดข้อกำหนด **Protocol Temporal Invariance Sign-off Policy** ไม่ได้บังคับให้ทุกบล็อกที่มีการตัดสินใจแบบ Arbiter/Crossbar ต้องมี SVA Liveness Proofs

---

### แผนผังสาเหตุและผล (Ishikawa Fishbone Diagram)

```
==================================================================================================
                                    ISHIKAWA FISHBONE CAUSE-EFFECT DIAGRAM
==================================================================================================

   MAN (บุคลากร)                                   MACHINE / TOOLS (เครื่องมือ)
   ----------------                                ---------------------------
   พึ่งพาเฉพาะ Black-Box Verification             ไม่ได้เปิดใช้งาน SVA Engine ใน Dynamic Simulation
   ขาดความเข้าใจเรื่อง Liveness vs Safety          ไม่มีตัวตรวจจับ Unbounded Latency ใน Testbench
               \                                                /
                \                                              /
                 \                                            /
                  +------------------------------------------+
                  |                                          |
                  |  DATACENTER CROSSBAR ROUTER FREEZE       | ===>> [3.5M USD SLA PENALTY]
                  |                                          |
                  +------------------------------------------+
                 /                                            \
                /                                              \
   METHOD (ระเบียบปฏิบัติ)                          MATERIAL / ENVIRONMENT (สภาวะแวดล้อม)
   ----------------------                          -------------------------------------
   ขาด SVA Arbiter Starvation Sign-off Gate        โหลดทราฟฟิก 94% สร้าง Circular Dependency
   ละเลยการจำลองสถานการณ์ Heavy Congestion          VOQ เกิดสภาวะ Head-of-Line Blocking
==================================================================================================
```

---

### คู่มือปฏิบัติการตรวจสอบ OJT หน้างาน: มาตรฐานการเขียน SVA คุณภาพสูงและปลอด Glitch

1. **Rule 1: การห้ามใช้ Immediate Assertion ตรวจลอจิกเชิงผสมผสาน (No Immediate Assertions in Combinational Paths)**
   - ห้ามเขียน: `always_comb begin assert(a == b); end` เพราะจะเกิด Glitch ผิดพลาดขณะคำนวณ
   - ให้เปลี่ยนไปใช้ **Deferred Immediate Assertions** หรือ **Concurrent Assertions**:
     ```systemverilog
     // แบบที่ปลอดภัย: รอจนค่าคงที่ในไซเคิลนั้น
     always_comb begin
         assert #0 (a == b) else $error("Mismatch detected!");
     end
     ```
2. **Rule 2: การใช้ `disable iff (!rst_n)` เสมอในทุก Concurrent Assertion**
   - ทุกคำสั่ง `property` ต้องมีเงื่อนไขการปิดใช้งานระหว่างช่วง Reset เสมอ เพื่อป้องกันการแจ้งเตือนขยะขณะที่ระบบกำลังเริ่มทำงานใหม่
3. **Rule 3: การตั้งค่า Action Blocks ที่ถูกต้องสำหรับระบบ CI/CD**
   - ใช้ `$fatal(1, ...)` สำหรับการละเมิด Safety ร้ายแรง (เช่น Data Corruption, Bus Contention, Overflow) เพื่อสั่งตัดการทดสอบทันที
   - ใช้ `$error(...)` สำหรับข้อผิดพลาดด้าน Protocol หรือ Latency ที่ต้องการเก็บข้อมูลสถิติต่อ

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (専門用語)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / อังกฤษ | บริบทการใช้งานเชิงวิศวกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **アサーションベース検証** | アサーションベースけんしょう | Asaashon Beesu Kenshou | Assertion-Based Verification (ABV) | การตรวจสอบวงจรดิจิทัลโดยใช้คำยืนยันคุณสมบัติ |
| **並行アサーション** | へいこうアサーション | Heikou Asaashon | Concurrent Assertion | คำยืนยันคุณสมบัติเชิงเวลาที่สุ่มตรวจตามรอบสัญญาณนาฬิกา |
| **即時アサーション** | そくじアサーション | Sokuji Asaashon | Immediate Assertion | คำยืนยันคุณสมบัติเชิงกระบวนการที่ประมวลผลทันที |
| **重複含意** | ちょうふくがんい | Choufuku Gan'i | Overlapping Implication (`\|->`) | การสอดคล้องของผลลัพธ์ในรอบสัญญาณนาฬิกาเดียวกัน |
| **非重複含意** | ひちょうふくがんい | Hi-choufuku Gan'i | Non-Overlapping Implication (`\|=>`) | การสอดคล้องของผลลัพธ์ในรอบสัญญาณนาฬิกาถัดไป |
| **飢餓状態** | きがじょうたい | Kiga Joutai | Starvation State | สภาวะอดอยากที่สัญญาณร้องขอไม่เคยได้รับการตอบสนอง |
| **事前サンプリング領域** | じぜんサンプリングりょういき | Jizen Sanpuringu Ryouiki | Preponed Sampling Region | พื้นที่เวลาสุ่มจับสัญญาณล่วงหน้าเพื่อขจัดสัญญาณรบกวน |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図審議 - Kenzu Shingi)

**สถานที่:** ศูนย์ตรวจสอบความสมบูรณ์ของโครงสร้างเครือข่ายความเร็วสูง (Network Router Verification Gate)  
**ผู้เข้าร่วม:**
- **ทาคานาชิ (小鳥遊):** Principal Protocol Verification Specialist (プロトコル検証主査)
- **สิทธิชัย (シッティチャイ):** Senior Interconnect Design Engineer (設計担当)

---

**小鳥遊主査 (ทาคานาชิ):**  
「シッティチャイさん、クロスバースイッチのアービタ回路の検証コードを拝見しました。`always_comb`文の中に**即時アサーション（Immediate Assertion）**がベタ書きされていますが、シミュレーション実行時に大量の**グリッチ（Glitch）誤検知**が発生していませんか？」  
*(คุณสิทธิชัยครับ ผมตรวจดูโค้ดการทดสอบของวงจร Arbiter ใน Crossbar Switch แล้ว พบว่ามีการเขียน Immediate Assertion ลงไปตรงๆ ใน `always_comb` ในระหว่างรัน Simulation ไม่เกิดข้อผิดพลาดหลอกตาจาก Glitch ขึ้นมาเต็มไปหมดหรือครับ?)*

**シッティチャイ (สิทธิชัย):**  
「小鳥遊主査、おっしゃる通りです。論理ゲートの伝搬遅延による過渡的なスパイクで`$display`が頻発し、ログファイルが数十ギガバイトに肥大化して困惑しておりました。」  
*(หัวหน้าทาคานาชิครับ เป็นจริงอย่างที่ท่านกล่าวเลยครับ เกิด Spikes ชั่วคราวจาก Propagation Delay ของลอจิกเกต ทำให้เกิด `$display` พ่นออกมาตลอดเวลาจนไฟล์ Log บวมขึ้นไปหลายสิบกิกะไบต์ ผมกำลังปวดหัวอยู่เลยครับ)*

**小鳥遊主査 (ทาคานาชิ):**  
「それは当たり前です！組み合わせ回路の過渡状態を即時アサーションで叩いてはいけません。クロック同期の**並行アサーション（Concurrent Assertion）**に変更し、**事前サンプリング領域（Preponed Region）**で確定した値を評価させるべきです。それと、このアービタには**飢餓状態（Starvation）**を防ぐための応答レイテンシ制約が一切書かれていませんね？」  
*(มันก็แน่อยู่แล้วสิครับ! จะเอา Immediate Assertion ไปจับสถานะชั่วคราวของลอจิกเชิงผสมผสานไม่ได้เด็ดขาด ต้องเปลี่ยนไปใช้ Concurrent Assertion ที่ประสานเวลากับคล็อก เพื่อให้เครื่องมือประเมินผลจากค่าที่นิ่งสนิทแล้วใน Preponed Region ครับ และอีกเรื่องหนึ่ง ใน Arbiter ตัวนี้ไม่มีการเขียนเงื่อนไขควบคุม Response Latency เพื่อป้องกันภาวะ Starvation เลยใช่ไหมครับ?)*

**シッティチャイ (สิทธิชัย):**  
「はい。現在は相互排他（Mutual Exclusion）の1点のみを監視しておりました。」  
*(ใช่ครับ ปัจจุบันผมเฝ้าดูเพียงคุณสมบัติ Mutual Exclusion จุดเดียวเท่านั้นครับ)*

**小鳥遊主査 (ทาคานาชิ):**  
「それだけでは不十分です！相互排他は『安全性の性質（Safety Property）』に過ぎず、『誰も永久に処理されないデッドロック状態』でもパスしてしまいます。`req[i] |-> ##[1:4] gnt[i]`という**『活性の性質（Liveness Property）』**をSVAで定義し、最大4サイクル以内に必ずグラントが付与されることを数学的に保証してください。このプロパティが通らなければ、基板への実装は許可できません。」  
*(แค่นั้นมันไม่พอครับ! Mutual Exclusion เป็นเพียง Safety Property ซึ่งต่อให้อยู่ในสภาวะ Deadlock ที่ไม่มีใครได้รับบริการตลอดกาล มันก็ยังรายงานว่าผ่านอยู่ดี คุณต้องเขียน Liveness Property เช่น `req[i] |-> ##[1:4] gnt[i]` เพื่อรับประกันทางคณิตศาสตร์ว่าสัญญาณ Grant จะต้องถูกจ่ายภายในไม่เกิน 4 ไซเคิลเสมอ หาก Property ตัวนี้ยังไม่ผ่าน ผมไม่อนุญาตให้นำไปต่อลงบอร์ดเด็ดขาดครับ)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: ความแตกต่างเชิงความหมายและลำดับเวลาระหว่าง `|->` และ `|=>`

พิจารณา SystemVerilog Concurrent Assertion สองชุดต่อไปนี้:
```systemverilog
// รูปแบบที่ 1: Overlapping Implication
property p_prop1;
    @(posedge clk) req |-> ##2 ack;
endproperty

// รูปแบบที่ 2: Non-Overlapping Implication
property p_prop2;
    @(posedge clk) req |=> ##1 ack;
endproperty
```
หากสัญญาณ `req` มีค่ากลายเป็น $1$ ที่ไซเคิลคล็อกที่ $T = 10$  
จงระบุไซเคิลคล็อก ($T_{ack1}$ และ $T_{ack2}$) ที่สัญญาณ `ack` จะต้องมีค่าเป็น $1$ จึงจะทำให้ `p_prop1` และ `p_prop2` ผ่านการตรวจสอบตามลำดับ:

- **A)** $T_{ack1} = 12$, $T_{ack2} = 12$ (ทั้งสองรูปแบบมีความหมายทางเวลาเท่ากันทุกประการ)
- **B)** $T_{ack1} = 12$, $T_{ack2} = 11$
- **C)** $T_{ack1} = 13$, $T_{ack2} = 12$
- **D)** $T_{ack1} = 11$, $T_{ack2} = 12$

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: A) $T_{ack1} = 12$, $T_{ack2} = 12$ (ทั้งสองรูปแบบมีความหมายทางเวลาเท่ากันทุกประการ)**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. **พิจารณารูปแบบที่ 1: `req |-> ##2 ack`**
   - โอเปอเรเตอร์ `|->` คือ **Overlapping Implication** หมายถึง การเริ่มประเมินผลฝั่งขวา (Consequent) จะเริ่มต้น ณ ไซเคิลเดียวกับที่เงื่อนไขฝั่งซ้าย (Antecedent) เป็นจริง
   - เมื่อ `req` เป็นจริงที่เวลา $T = 10$:
   - ฝั่งขวาคือ `##2 ack` หมายถึง ต้องนับถอยหลังไปอีก 2 ไซเคิลจากไซเคิลปัจจุบัน:
     $$T_{ack1} = 10 + 2 = 12$$
2. **พิจารณารูปแบบที่ 2: `req |=> ##1 ack`**
   - โอเปอเรเตอร์ `|=>` คือ **Non-Overlapping Implication** ซึ่งมีนิยามตามมาตรฐาน IEEE 1800 เทียบเท่ากับ `|-> ##1`
   - นั่นคือ การเริ่มประเมินฝั่งขวาจะกระโดดไปข้างหน้า 1 ไซเคิลทันที ($T = 10 + 1 = 11$)
   - จากนั้นตัวโอเปอเรเตอร์ `##1 ack` จะสั่งให้หน่วงเวลาเพิ่มไปอีก 1 ไซเคิล:
     $$T_{ack2} = 11 + 1 = 12$$
3. ดังนั้น ทั้งสองนิยามมีค่าเวลาสัมพัทธ์ตรงกันเป๊ะที่ไซเคิล $T = 12$
   $$(req \ |-> \ \#\#2 \ ack) \ \equiv \ (req \ |=> \ \#\#1 \ ack)$$

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ B ผิด:** สับสนคิดว่า `|=>` หน่วงเวลา 1 ไซเคิลแล้ว แต่ลืมบวก `##1` เพิ่มเข้าไป
- **ข้อ C ผิด:** คำนวณเวลาเกินไป 1 ไซเคิลในรูปแบบที่ 1
- **ข้อ D ผิด:** สลับพฤติกรรมระหว่าง overlapping และ non-overlapping

---

### คำถามที่ 2: ความแตกต่างระหว่าง Non-Consecutive Repetition (`[= 3]`) และ Goto Repetition (`[-> 3]`)

กำหนดลำดับเหตุการณ์ของสัญญาณ Boolean $A$ และ $B$ ในแต่ละไซเคิลคล็อกดังนี้:
```
Cycle:  1   2   3   4   5   6   7   8
  A  :  1   0   1   0   1   0   0   0
  B  :  0   0   0   0   0   0   1   0
```
จะเห็นว่าสัญญาณ $A$ มีค่าเป็น $1$ เกิดขึ้น 3 ครั้ง (ที่ Cycle 1, Cycle 3, และ Cycle 5) และสัญญาณ $B$ มีค่าเป็น $1$ ที่ Cycle 7

พิจารณา SystemVerilog Sequence สองรูปแบบต่อไปนี้:
```systemverilog
sequence seq_goto;
    A [-> 3] ##1 B;
endsequence

sequence seq_non_consec;
    A [= 3] ##1 B;
endsequence
```
การประเมินผลความถูกต้องของ Sequences ทั้งสอง ณ ไซเคิลที่ 7 เป็นอย่างไร?

- **A)** ทั้ง `seq_goto` และ `seq_non_consec` ผ่านการตรวจสอบทั้งคู่
- **B)** `seq_goto` ไม่ผ่าน (Fail), แต่ `seq_non_consec` ผ่านการตรวจสอบ (Match)
- **C)** `seq_goto` ผ่านการตรวจสอบ (Match), แต่ `seq_non_consec` ไม่ผ่าน (Fail)
- **D)** ทั้งสอง Sequences ล้มเหลวไม่ผ่านทั้งคู่

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) `seq_goto` ไม่ผ่าน (Fail), แต่ `seq_non_consec` ผ่านการตรวจสอบ (Match)**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. **วิเคราะห์ `seq_goto: A [-> 3] ##1 B`:**
   - โอเปอเรเตอร์ `[-> k]` คือ **Goto Repetition (Boolean Event Match)**
   - มันบังคับว่าเหตุการณ์ถัดไป (`##1 B`) จะต้องเกิดขึ้น **ทันทีใน 1 ไซเคิลถัดจากไซเคิลที่ $A$ กลายเป็น $1$ เป็นครั้งที่ 3**
   - สัญญาณ $A$ กลายเป็น $1$ ครั้งที่ 3 ที่ **Cycle 5**
   - ดังนั้น เงื่อนไข `##1 B` บังคับให้สัญญาณ $B$ จะต้องเป็น $1$ ที่ไซเคิล:
     $$T_B = 5 + 1 = \mathbf{Cycle \ 6}$$
   - แต่ในความเป็นจริง ที่ Cycle 6 สัญญาณ $B = 0$ (สัญญาณ $B$ เพิ่งมาเป็น $1$ ที่ Cycle 7)
   - ดังนั้น `seq_goto` จึง **ประเมินผลไม่สำเร็จ (FAIL)**
2. **วิเคราะห์ `seq_non_consec: A [= 3] ##1 B`:**
   - โอเปอเรเตอร์ `[= k]` คือ **Non-Consecutive Repetition**
   - มันยอมรับให้มีช่องว่าง (Gaps / Idle Cycles) ที่สัญญาณ $A = 0$ คั่นอยู่กี่ไซเคิลก็ได้หลังจากที่ $A$ เกิดขึ้นครบ 3 ครั้งแล้ว ก่อนที่จะไปจับคู่กับสัญญาณ $B$
   - สัญญาณ $A$ เกิดครบ 3 ครั้งที่ Cycle 5 จากนั้น $A=0$ ที่ Cycle 6 และทันทีที่ก้าวสู่ Cycle 7 สัญญาณ $B$ กลายเป็น $1$ ตามเงื่อนไขพอดี
   - ดังนั้น `seq_non_consec` จึง **ประเมินผลสำเร็จสมบูรณ์ (MATCH)**

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** ละเลยข้อจำกัดเวลาของ Goto Repetition ที่ต้องผูกติดกับไซเคิลที่เกิดเหตุการณ์ครั้งสุดท้ายทันที
- **ข้อ C ผิด:** สลับนิยามความหมายระหว่างโอเปอเรเตอร์ทั้งสอง
- **ข้อ D ผิด:** `seq_non_consec` ถูกออกแบบมาเพื่อรองรับสถานการณ์ลักษณะนี้โดยเฉพาะ จึงทำงานได้สำเร็จ

---

### คำถามที่ 3: ปรากฏการณ์ Glitch Race Condition ใน SystemVerilog Scheduling Regions

ทำไมมาตรฐาน IEEE 1800 SystemVerilog จึงกำหนดให้การสุ่มสัญญาณสำหรับ Concurrent Assertions ต้องเกิดขึ้นใน **Preponed Region** เสมอ แทนที่จะสุ่มใน Active หรือ NBA Region?

- **A)** เพื่อลดการใช้หน่วยความจำ RAM ของเครื่องเซิร์ฟเวอร์จำลอง
- **B)** เพื่อให้ได้สถานะของสัญญาณที่เสถียร 100% จากไซเคิลก่อนหน้า และป้องกันการเกิด Race Condition กับ Non-blocking Assignments (`<=`) ในไซเคิลปัจจุบัน
- **C)** เพื่อให้สามารถประเมินผลวงจร Combinational ได้ก่อนที่สัญญาณนาฬิกาจะเริ่มสั่น
- **D)** เพื่อรองรับการทำงานของคำสั่ง `$display` ในภาษา Verilog-1995

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) เพื่อให้ได้สถานะของสัญญาณที่เสถียร 100% จากไซเคิลก่อนหน้า และป้องกันการเกิด Race Condition กับ Non-blocking Assignments (`<=`) ในไซเคิลปัจจุบัน**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ในฮาร์ดแวร์จริง (Silicon Physics) Flip-Flop ต้องการ **Setup Time ($t_{su}$)** ก่อนที่ขอบสัญญาณนาฬิกาจะมาถึง สัญญาณที่ Flop จับไปใช้งานคือค่าที่คงที่อยู่ก่อนหน้านั้น
2. หาก Simulator ทำการสุ่มค่าตัวแปรใน **Active Region** หรือ **NBA Region**:
   - ขอบของสัญญาณนาฬิกากำลังทริกเกอร์ให้ Flop สลับค่า
   - จะเกิดปัญหา **Non-deterministic Race Condition**: Simulator ไม่สามารถรับประกันได้ว่าตัวตรวจวัด Assertion จะได้ค่าตัวแปรก่อนหรือหลังการอัปเดตของ Flop
3. IEEE 1800 จึงสร้าง **Preponed Region** ขึ้นมา:
   - เป็นพื้นที่เวลาแรกสุดของ Time Slot ปัจจุบัน ก่อนที่เหตุการณ์ใดๆ จะเกิดขึ้น
   - สัญญาณในพื้นที่นี้เป็นค่าที่นิ่งสนิทจากการประมวลผลของไซเคิลก่อนหน้า
   - การสุ่มค่าที่นี่จึงการันตีความแน่นอนทางคณิตศาสตร์ (Mathematical Determinism) 100% ปราศจากความผันผวนของลำดับการทำงานในซอฟต์แวร์

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** การเก็บประวัติสัญญาณใน Preponed Region มีการใช้หน่วยความจำเพิ่มขึ้นเล็กน้อย ไม่ใช่การลดการใช้หน่วยความจำ
- **ข้อ C ผิด:** วงจร Combinational จะถูกประเมินใน Active Region หลังจากขอบคล็อกขยับ ไม่ใช่ใน Preponed Region
- **ข้อ D ผิด:** คำสั่ง `$display` อยู่ใน Active Region ส่วน Verilog-1995 ไม่มีแนวคิดของ Preponed Region
