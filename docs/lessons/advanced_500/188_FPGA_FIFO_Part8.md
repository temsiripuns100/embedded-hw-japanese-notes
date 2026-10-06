# Lesson 188: FPGA FIFO Part 8 - Priority FIFOs & Virtual Channel Queuing (Multi-Queue Architecture, Head-of-Line Blocking Avoidance, Weighted Round-Robin Scheduling & PCIe/Ethernet QoS)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์การติดขัดหัวแถว (Head-of-Line Blocking Dilemma)
ในโครงสร้าง FIFO คิวเดี่ยวแบบดั้งเดิม (Single-Queue FIFO) ข้อมูลทุกประเภทจะถูกจัดเรียงตามลำดับเวลาที่ไหลเข้ามาตามกฎเหล็ก "มาก่อน ออกก่อน (First-In, First-Out)"

ทว่า ในระบบโครงข่ายความปลอดภัยสูงและการสื่อสารมัลติเพล็กซ์ เช่น **เครือข่ายยานยนต์ Time-Sensitive Networking (TSN / IEEE 802.1Qbv), PCIe Virtual Channels (VC0/VC1), หรือ Data Center RoCEv2 (RDMA over Converged Ethernet)**: ข้อมูลในระบบจะมีความสำคัญและข้อกำหนดด้านเวลาที่แตกต่างกันอย่างสิ้นเชิง:
* **ข้อมูลวิกฤตความปลอดภัย (Critical Safety / Urgent Control):** เช่น คำสั่งเบรกฉุกเฉิน (AEB), สัญญาณ Heartbeat, หรือข้อความ Interrupt ต้องการความหน่วงเวลาต่ำสุดระดับไมโครวินาที ($Latency < 10\mu s$)
* **ข้อมูลทั่วไปความเร็วปกติ (Best-Effort / Bulk Traffic):** เช่น การดาวน์โหลดไฟล์อัปเดตแผนที่ GPS, สตรีมมิ่งวิดีโอเพื่อความบันเทิงในรถยนต์

```
              ปรากฏการณ์ HEAD-OF-LINE (HoL) BLOCKING ในคิวเดี่ยว
              
    Queue Output                                                            Queue Input
         ◄── [ Low-Pri 4KB Data ] ── [ Low-Pri 4KB Data ] ── [ CRITICAL BRAKE! ] ◄──
                      ▲
                      │ (แพ็กเก็ตดาวน์โหลดขนาดใหญ่ขวางหัวแถวอยู่!)
                      │
    วิกฤตการณ์ HoL Blocking:
    1. แพ็กเก็ตเบรกฉุกเฉิน [CRITICAL BRAKE!] เพิ่งถูกยิงเข้ามาใน FIFO
    2. ทว่า หัวแถวของ FIFO ถูกบล็อกด้วยแพ็กเก็ตดาวน์โหลดขนาดยักษ์ 2 ก้อน
    3. บัสปลายทางมีความเร็วจำกัด ทำให้แพ็กเก็ตฉุกเฉินต้อง "ติดหล่มรอคอย" นานถึง 100ms!
    ===> ผลลัพธ์: คำสั่งเบรกล่าช้า รถยนต์ชนสิ่งกีดขวาง เกิดโศกนาฏกรรมร้ายแรง!
```

**Head-of-Line (HoL) Blocking** คือปรากฏการณ์ที่: *ข้อมูลที่มีความสำคัญสูงสุดต้องติดค้างรอคอยอยู่ในคิว เพียงเพราะข้อมูลขยะหรือข้อมูลความสำคัญต่ำที่อยู่หัวแถวยังระบายออกไปไม่หมด* ซึ่งทำลายข้อกำหนดความปลอดภัย (Deterministic Latency Guarantee) ลงอย่างสิ้นเชิง!

---

### 1.2 สถาปัตยกรรม Multi-Queue Priority FIFO และ Virtual Channels (VC)

เพื่อขจัด HoL Blocking ให้หมดไป $100\%$ สถาปัตยกรรมขั้นสูงจะแบ่งบัฟเฟอร์ออกเป็น **หลายคิวขนานกัน (Multi-Queue Architecture)** โดยมีระบบจำแนกประเภท (Traffic Classifier) และช่องทางเสมือน (Virtual Channels):

```
               สถาปัตยกรรม MULTI-QUEUE PRIORITY FIFO & SCHEDULER
               
                         ┌─────────────────────────────────┐
                         │   TRAFFIC CLASSIFIER / PARSER   │
                         └────────────────┬────────────────┘
                                          │ จัดเส้นทางตาม Priority Tag
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
             ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
             │   QUEUE 3   │       │   QUEUE 2   │       │   QUEUE 0   │
             │ (Strict Pri/│       │ (High Pri   │       │(Best Effort │
             │  Emergency) │       │  Control)   │       │ Bulk Data)  │
             └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
                    │                     │                     │
                    └─────────────────────┼─────────────────────┘
                                          ▼
                         ┌─────────────────────────────────┐
                         │   QoS ARBITRATION SCHEDULER     │
                         │   (Strict Priority / WRR / DWRR)│
                         └────────────────┬────────────────┘
                                          ▼
                               Selected Output Stream
```

#### แนวทางการจัดสรรหน่วยความจำ (Memory Allocation Strategies):
1. **Dedicated Independent FIFOs (บัฟเฟอร์แยกอิสระ):**
   * ใช้ก้อน BRAM แยกกันอย่างเด็ดขาดสำหรับแต่ละคิว
   * ข้อดี: ปลอดภัยสูงสุด คิวหนึ่งล้นจะไม่ส่งผลกระทบต่อคิวอื่น (Fault Isolation $100\%$)
   * ข้อเสีย: สิ้นเปลือง BRAM หากบางคิวไม่มีทราฟฟิกเข้ามา
2. **Shared Memory with Linked-List Pointers (บัฟเฟอร์ใช้ร่วมกัน):**
   * ใช้หน่วยความจำก้อนใหญ่ก้อนเดียว และจัดการพื้นที่ว่างผ่าน Linked List
   * ข้อดี: ประหยัดหน่วยความจำสูงสุด
   * ข้อเสีย: ลอจิกซับซ้อนมาก และเสี่ยงต่อการที่ Low-Priority Traffic จะกินพื้นที่จนหมด (Buffer Starvation) เว้นแต่จะติดตั้งระบบ **Per-Queue Watermark Limits**

---

### 1.3 อัลกอริทึมการจัดสรรคิว: Strict Priority เทียบกับ Weighted Round-Robin (WRR)

หัวใจสำคัญของการเลือกข้อมูลออกจากคิวขึ้นอยู่กับ **Scheduling Algorithm**:

```
          การเปรียบเทียบระหว่าง STRICT PRIORITY และ WEIGHTED ROUND-ROBIN
          
   [ 1. STRICT PRIORITY (SP SCHEDULING) ]
   
       Queue 3 (Urgent) : มีข้อมูลเมื่อไหร่ ──► ได้ส่งทันที 100%!
       Queue 0 (Bulk)   : ต้องรอให้ Queue 3, 2, 1 ว่างเปล่าสนิท จึงจะได้ส่ง!
       ===> ข้อดี: Latency ของคิวสูงสุดต่ำที่สุดในระดับอุดมคติ
       ===> วิกฤต: เกิด STARVATION! หากคิวบนมีข้อมูลตลอดเวลา คิวล่างจะไม่ได้ส่งเลยตลอดกาล!
       
   [ 2. WEIGHTED ROUND-ROBIN (WRR SCHEDULING) ]
   
       กำหนดโควตาน้ำหนัก (Weights): Queue 2 = 60%, Queue 1 = 30%, Queue 0 = 10%
       * รอบที่ 1: ดึงจาก Q2 จำนวน 6 คำ
       * รอบที่ 2: ดึงจาก Q1 จำนวน 3 คำ
       * รอบที่ 3: ดึงจาก Q0 จำนวน 1 คำ
       ===> ข้อดี: ปลอด Starvation 100%! ทุกคิวได้รับการการันตีแบนด์วิดท์ขั้นต่ำเสมอ!
```

#### ทฤษฎี Deficit Weighted Round-Robin (DWRR) สำหรับแพ็กเก็ตความยาวแปรผัน:
ในระบบเครือข่ายจริง ข้อมูลไม่ได้มีขนาดเท่ากันทุกคำ แต่ละแพ็กเก็ตมีขนาดแปรผันตั้งแต่ $64\text{ ไบต์}$ ถึง $1500\text{ ไบต์}$:
หากใช้ WRR ธรรมดาที่นับจำนวนแพ็กเก็ต คิวที่ส่งแพ็กเก็ตขนาดยักษ์ $1500\text{ ไบต์}$ จะแย่งแบนด์วิดท์ไปมากกว่าคิวที่ส่งแพ็กเก็ตเล็ก $64\text{ ไบต์}$ มหาศาล
เพื่อแก้ปัญหานี้ จึงต้องใช้ **Deficit Weighted Round-Robin (DWRR)**:
* แต่ละคิวจะมีตัวนับเครดิตสะสม (**Deficit Counter: $DC_i$**)
* ในแต่ละรอบ คอนโทรลเลอร์จะเพิ่มเครดิตให้แต่ละคิวเท่ากับค่า **Quantum ($Q_i = Weight_i \times Base\_Quantum$)**
* คิวจะสามารถส่งแพ็กเก็ตได้ก็ต่อเมื่อ:
  $$DC_i \ge Packet\_Length$$
* เมื่อส่งแพ็กเก็ตเสร็จ จะหักลบเครดิตออก: $DC_i \Leftarrow DC_i - Packet\_Length$
* หากเครดิตไม่พอ คิวจะเก็บเศษเครดิตที่เหลือไว้ใช้ในรอบถัดไป ทำให้การแบ่งแบนด์วิดท์มีความยุติธรรมทางคณิตศาสตร์อย่างแท้จริง!

---

### 1.4 โค้ดแม่แบบภาษา Verilog ระดับ Senior สำหรับ 4-Queue Multi-Priority FIFO พร้อม WRR Scheduler

```verilog
// ==============================================================================
// 4-QUEUE MULTI-PRIORITY FIFO WITH WEIGHTED ROUND-ROBIN (WRR) SCHEDULER
// Senior Gold Standard: Head-of-Line Blocking Free & Starvation-Proof Architecture
// Weights: Q3 (Strict/Urgent), Q2 (Weight 4), Q1 (Weight 2), Q0 (Weight 1)
// ==============================================================================
(* keep_hierarchy = "yes" *)
module priority_wrr_fifo #(
    parameter integer DATA_WIDTH = 32,
    parameter integer QUEUE_ADDR = 6   // Depth = 64 words per queue
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // Ingress Interface with 2-bit Priority Tag
    input  wire                  wr_en,
    input  wire [DATA_WIDTH-1:0] din,
    input  wire [1:0]            din_priority, // 3: Urgent, 2: High, 1: Med, 0: Low
    output wire [3:0]            queue_full,

    // Egress Interface
    input  wire                  rd_en,
    output reg  [DATA_WIDTH-1:0] dout,
    output reg  [1:0]            dout_priority,
    output wire                  empty
);

    // -------------------------------------------------------------------------
    // 1. Four Independent Dedicated BRAM FIFOs
    // -------------------------------------------------------------------------
    wire [DATA_WIDTH-1:0] q_dout [0:3];
    wire [3:0]            q_empty;
    reg  [3:0]            q_rd_en;

    genvar i;
    generate
        for (i = 0; i < 4; i = i + 1) begin : gen_queues
            wire wr_match = wr_en && (din_priority == i) && !queue_full[i];
            
            sync_fifo #(
                .DATA_WIDTH(DATA_WIDTH),
                .ADDR_WIDTH(QUEUE_ADDR),
                .FWFT_MODE(1)
            ) fifo_inst (
                .clk(clk),
                .rst_n(rst_n),
                .wr_en(wr_match),
                .din(din),
                .full(queue_full[i]),
                .almost_full(),
                .rd_en(q_rd_en[i]),
                .dout(q_dout[i]),
                .empty(q_empty[i]),
                .almost_empty(),
                .data_count()
            );
        end
    endgenerate

    // -------------------------------------------------------------------------
    // 2. WRR Arbitration Scheduler Logic
    // -------------------------------------------------------------------------
    // Weights: Q2 = 4 words, Q1 = 2 words, Q0 = 1 word. (Q3 is Strict Priority!)
    reg [2:0] wrr_credit;
    reg [1:0] active_queue;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            active_queue <= 2'b10;
            wrr_credit   <= 3'd4;
        end else begin
            // Q3 has absolute Strict Priority: overrides any WRR state!
            if (!q_empty[3]) begin
                // Maintain current WRR queue pointer during urgent interruption
            end else if (rd_en && !q_empty[active_queue]) begin
                if (wrr_credit > 3'd1) begin
                    wrr_credit <= wrr_credit - 1'b1;
                end else begin
                    // Advance to next available round-robin queue
                    case (active_queue)
                        2'b10: begin
                            active_queue <= 2'b01;
                            wrr_credit   <= 3'd2; // Weight for Q1
                        end
                        2'b01: begin
                            active_queue <= 2'b00;
                            wrr_credit   <= 3'd1; // Weight for Q0
                        end
                        2'b00: begin
                            active_queue <= 2'b10;
                            wrr_credit   <= 3'd4; // Weight for Q2
                        end
                        default: active_queue <= 2'b10;
                    endcase
                end
            end else if (q_empty[active_queue]) begin
                // Skip empty queues immediately without wasting clock cycles
                case (active_queue)
                    2'b10: begin active_queue <= 2'b01; wrr_credit <= 3'd2; end
                    2'b01: begin active_queue <= 2'b00; wrr_credit <= 3'd1; end
                    2'b00: begin active_queue <= 2'b10; wrr_credit <= 3'd4; end
                    default: active_queue <= 2'b10;
                endcase
            end
        end
    end

    // -------------------------------------------------------------------------
    // 3. Output Multiplexing & Read Enable Driving
    // -------------------------------------------------------------------------
    wire [1:0] selected_queue = (!q_empty[3]) ? 2'b11 : active_queue;
    assign empty = &q_empty; // Empty only if ALL 4 queues are empty

    always @(*) begin
        q_rd_en = 4'b0000;
        if (rd_en && !empty) begin
            q_rd_en[selected_queue] = 1'b1;
        end
    end

    always @(*) begin
        dout          = q_dout[selected_queue];
        dout_priority = selected_queue;
    end

endmodule
```

---

### 1.5 SystemVerilog Assertions (SVA) เพื่อตรวจจับ Starvation & HoL Blocking

```systemverilog
// SVA Verification Suite สำหรับ Multi-Priority FIFO
module priority_fifo_sva (
    input wire clk,
    input wire rst_n,
    input wire rd_en,
    input wire [3:0] q_empty,
    input wire [1:0] dout_priority
);

    // Property 1: Strict Priority Liveness (Q3 must NEVER be blocked by Q0..Q2!)
    // If Q3 has data, the selected output must strictly be Q3!
    property p_strict_priority_unblocked;
        @(posedge clk) disable iff (!rst_n)
        (!q_empty[3] && rd_en) |-> (dout_priority == 2'b11);
    endproperty
    assert_strict_pri: assert property (p_strict_priority_unblocked)
        else $error("[HOL_BLOCKING_ERROR]: Urgent Queue 3 was blocked by lower priority queue!");

    // Property 2: Starvation Freedom
    // If Queue 0 has data, it must eventually be granted within bounded cycles (e.g., 50 cycles)
    // assuming higher queues are not 100% saturated by infinite Q3 traffic.
    
endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】ระบบเบรกฉุกเฉินอัตโนมัติของรถยนต์ไร้คนขับ (Autonomous Emergency Braking - AEB)
เกิดความล่าช้าของคำสั่งเบรก 120 มิลลิวินาที ส่งผลให้รถทดสอบพุ่งชนหุ่นจำลองคนข้ามถนน
จากบั๊ก Head-of-Line Blocking ใน Single-Queue FIFO ของสวิตช์เครือข่าย TSN Ethernet
================================================================================
```

#### บริบทของระบบ (System Context):
บริษัทพัฒนายานยนต์อัตโนมัติระดับ Level 4 พัฒนากล่องควบคุมส่วนกลาง (Central Autonomous Domain Controller) โดยใช้ FPGA เกรดรถยนต์ Xilinx Zynq UltraScale+ (`xazu7ev`):
* เซนเซอร์รอบคันเชื่อมต่อผ่านสวิตช์เครือข่าย TSN Ethernet (1000BASE-T) ภายใน FPGA
* สวิตช์ทำหน้าที่รวมสัญญาณ 2 ประเภทเข้าสู่พอร์ตเอาต์พุตเดียวกัน:
  1. **สตรีมแผนที่ความละเอียดสูง (HD Map Point Cloud Data):** เป็นข้อมูลแบบ Best-Effort ส่งแพ็กเก็ตต่อเนื่องขนาดใหญ่ $1500\text{ ไบต์}$ หลายพันแพ็กเก็ตต่อวินาที
  2. **คำสั่งเบรกฉุกเฉิน (AEB Trigger Message):** เป็นแพ็กเก็ตขนาดเล็กเพียง $64\text{ ไบต์}$ ที่ต้องส่งถึงระบบเบรกภายในไม่เกิน $1\text{ มิลลิวินาที}$
* เพื่อประหยัดพื้นที่ BRAM วิศวกรสร้างคิวบัฟเฟอร์ขาออกเป็น **Single-Queue FIFO ขนาดความจุ 64KB** โดยไม่มีการแยกช่องทาง Priority

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
ในการทดสอบรถยนต์บนสนามจำลองเสมือนจริง เมื่อรถยนต์วิ่งด้วยความเร็ว $60\text{ km/h}$ และระบบเซนเซอร์ Lidar ตรวจพบหุ่นจำลองคนเดินข้ามถนนกะทันหัน อัลกอริทึม AI ตัดสินใจยิงคำสั่งเบรกฉุกเฉินทันที ทว่า รถยนต์กลับ **ไม่เบรกในทันที แต่พุ่งต่อไปอีก 2 เมตร และชนเข้ากับหุ่นจำลองอย่างรุนแรง!** จากการวิเคราะห์ Log พบว่า แพ็กเก็ตคำสั่งเบรกฉุกเฉินต้องใช้เวลาถึง **$124\text{ มิลลิวินาที}$** กว่าจะหลุดออกจากพอร์ตสวิตช์ของ FPGA!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมรถยนต์จึงพุ่งชนหุ่นจำลองคนข้ามถนน?**
   * *เพราะคำสั่งสั่งการเบรกไฮดรอลิกเดินทางไปถึงคาลิปเปอร์เบรกล่าช้ากว่ากำหนดถึง 120 มิลลิวินาที*
2. **ทำไมคำสั่งเบรกจึงเดินทางล่าช้าไป 120 มิลลิวินาที?**
   * *เพราะแพ็กเก็ตคำสั่งเบรกติดค้างอยู่ในบัฟเฟอร์คิวขาออกของสวิตช์เครือข่าย Ethernet บน FPGA*
3. **ทำไมแพ็กเก็ตคำสั่งเบรกจึงติดค้างอยู่ในบัฟเฟอร์?**
   * *เพราะเกิดสภาวะ Head-of-Line (HoL) Blocking โดยแพ็กเก็ตสตรีมแผนที่ HD Map ขนาด 1500 ไบต์จำนวนกว่า 80 แพ็กเก็ตอัดแน่นขวางอยู่หน้าคิว*
4. **ทำไมแพ็กเก็ตฉุกเฉินจึงไม่สามารถแซงหน้าแพ็กเก็ตแผนที่ขึ้นไปก่อนได้?**
   * *เพราะวิศวกรใช้ FIFO คิวเดี่ยวแบบ FIFO ทั่วไปที่ไม่มีการแบ่งแยก Priority หรือ Virtual Channels*
5. **ทำไมวิศวกรจึงไม่ใช้ Multi-Queue Priority Architecture ตั้งแต่แรก?**
   * *เพราะวิศวกรต้องการลดการใช้ Block RAM ให้น้อยที่สุด และคิดว่าแบนด์วิดท์กิกะบิตอีเทอร์เน็ตมีมากพอ จึงไม่คาดคิดว่าจะเกิด Micro-burst Traffic ของแผนที่มาอุดตันคิวในเสี้ยววินาทีวิกฤต!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                         สาเหตุของความล้มเหลว: AEB BRAKE LATENCY COLLAPSE
                         
   METHOD (การออกแบบสถาปัตยกรรมคิว)            MACHINE (ฮาร์ดแวร์และทราฟฟิกเครือข่าย)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ใช้ Single-Queue FIFO สำหรับทุกข้อมูล│     │ HD Map Burst อัดแน่น 80 แพ็กเก็ต│
   │ ขาดการแยกลำดับความสำคัญ (QoS)  │          │ เกิด HoL Blocking ล่าช้า 120ms │
   │ ไม่มี Strict Priority Channel  │          │ สัญญาณเบรกติดหล่มท้ายคิว       │
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ละเลยมาตรฐาน ISO 26262 ASIL-D  │          │ Testbench ไม่เคยยิง Map พร้อมเบรก│
   │ ขาดการทดสอบ Worst-Case Latency │          │ ทดสอบเฉพาะเวลาที่ไม่มีทราฟฟิกอื่น│
   │ ตรวจแบบ Kenzu ไม่ตรวจ HoL Risk │          │ ปล่อยผ่านเพราะเห็นว่าส่งถึงครบ │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (ข้อกำหนดและการตรวจสอบ)             MEASUREMENT (สภาวะการทดสอบระบบ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediations):
1. **เปลี่ยนโครงสร้างเป็น 4-Queue Multi-Priority Architecture ทันที:**
   * **Queue 3 (Strict Priority):** สำหรับข้อความควบคุมความปลอดภัย ASIL-D (เช่น คำสั่งเบรก, ถุงลมนิรภัย) ซึ่งมีสิทธิ์ส่งออกทันทีในไซเคิลถัดไป $100\%$ โดยไม่มีเงื่อนไข
   * **Queue 2 (High Priority):** สำหรับข้อมูลควบคุมระบบขับเคลื่อน (Powertrain)
   * **Queue 1 (Medium Priority):** สำหรับข้อมูลเซนเซอร์สภาพแวดล้อม
   * **Queue 0 (Best-Effort):** สำหรับข้อมูลแผนที่ความละเอียดสูง (HD Map)
2. **ติดตั้งระบบ Packet Preemption (IEEE 802.1Qbu / 802.3br):** อนุญาตให้แพ็กเก็ตฉุกเฉินสามารถ "ผ่ากลาง (Preempt)" แพ็กเก็ต Best-Effort ที่กำลังส่งอยู่ได้ทันที ทำให้ Latency ลดลงเหลือต่ำกว่า **$1.5\text{ ไมโครวินาที}$**!
3. **เขียน SVA Assertion:** บังคับให้ตรวจสอบว่า เมื่อมีข้อมูลใน Queue 3 ข้อมูลนั้นจะต้องได้รับการส่งออกภายในไม่เกิน $10\text{ ไซเคิล}$ เสมอ!

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Priority Queue & QoS (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | ข้อมูลความปลอดภัยวิกฤต (Safety-Critical) แยกคิวเด็ดขาดจาก Bulk Data หรือไม่? | Dedicated High-Pri Queue | [ ] ผ่าน |
| 2 | คิวฉุกเฉินได้รับการจัดสรรแบบ Strict Priority หรือรับประกัน Latency หรือไม่? | Latency $\le 10\mu s$ Bound | [ ] ผ่าน |
| 3 | คิวระดับล่างมีการใช้อัลกอริทึม WRR/DWRR เพื่อป้องกันการเกิด Starvation? | Starvation-Free Proof | [ ] ผ่าน |
| 4 | มีการกำหนด Per-Queue Watermark Limits เพื่อไม่ให้คิวใดคิวหนึ่งผลาญ RAM หมด? | Per-Queue Quota System | [ ] ผ่าน |
| 5 | มีการเขียน SVA ยืนยันว่าไม่มีสภาวะ HoL Blocking เกิดขึ้นกับคิวฉุกเฉิน? | Formal Property Passed | [ ] ผ่าน |
| 6 | ทำการทดสอบ Stress Test ด้วยทราฟฟิกอัดเต็ม $100\%$ พร้อมยิงสัญญาณฉุกเฉิน? | Pass Co-existence Test | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | 優先度付きFIFO | ゆうせんどつきFIFO | Yūsendotsuki Faifo | Priority FIFO |
| 2 | 先頭ブロッキング | せんとうブロッキング | Sentō burokkingu | Head-of-Line Blocking (HoL) |
| 3 | 仮想チャネル | かそうチャネル | Kasō chaneru | Virtual Channel (VC) |
| 4 | 厳格優先制御 | げんかくゆうせんせいぎょ | Genkaku yūsen seigyo | Strict Priority (SP) |
| 5 | 重み付きラウンドロビン | おもみつきラウンドロビン | Omomitsuki raundorobin | Weighted Round-Robin (WRR) |
| 6 | 飢餓状態防止 | きがじょうたいぼうし | Kiga jōtai bōshi | Starvation Prevention |
| 7 | サービス品質保証 | サービスひんしつほしょう | Sābisu hinshitsu hoshō | Quality of Service (QoS) Guarantee |
| 8 | パケット割り込み送信 | パケットわりこみそうしん | Paketto warikomi sōshin | Packet Preemption (Frame Preemption) |
| 9 | 帯域公平配分 | たいいきこうへいはいぶん | Taiiki kōhei haibun | Fair Bandwidth Allocation |
| 10 | トラフィック分類器 | トラフィックぶんるいき | Torafikku bunruiki | Traffic Classifier / Parser |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ศูนย์ตรวจสอบความปลอดภัยเชิงฟังก์ชันยานยนต์อัตโนมัติ (Automotive Functional Safety Assessment Center), เมืองนาโกย่า (Nagoya)  
**ผู้เข้าร่วม:**
* **ฟุรุคาวะซัง (Furukawa-san):** หัวหน้าผู้ประเมินความปลอดภัย ASIL-D (Lead Functional Safety Auditor / 技監)
* **ธนบดี (Thanabodee):** วิศวกรออกแบบระบบเครือข่ายยานยนต์ FPGA (In-Vehicle Networking FPGA Designer)

---

**古川技監 (Furukawa):**  
「タナボディ君、この自動運転ECU用TSNイーサネットスイッチの出力段バッファ設計書を見たが、ISO 26262 ASIL-Dの審査において絶対に容認できない構造的欠陥がある。大容量のHDマップ点群データと、緊急ブレーキ指令（AEB）が、**単一の64KB FIFO（Single-Queue FIFO）**に混在して書き込まれているね。もしマップデータがバッファを埋め尽くしている最中にAEBパケットが届いたらどうなるのかね？」  
*(Tanabodi-kun, kono jidō unten ECU-yō TSN īsanetto suicchi no shutsuryoku-dan baffa sekkeisho wo mita ga, ISO 26262 ASIL-D no shinsa ni oite zettai ni yōnin dekinai kōzōteki kekkan ga aru. Dai-yōryō no HD mappu tengun dēta to, kinkyū burēki shirei (AEB) ga, tan'itsu no 64KB FIFO ni konzai shite kakikomarete iru ne. Moshi mappu dēta ga baffa wo umetsukushite iru saichū ni AEB paketto ga todoitara dō naru no kane?)*  
**คำแปล:** คุณธนบดี ผมได้ตรวจเอกสารออกแบบบัฟเฟอร์ขาออกของสวิตช์ TSN Ethernet สำหรับ ECU ขับเคลื่อนอัตโนมัตินี้แล้ว พบข้อบกพร่องเชิงโครงสร้างที่การประเมิน ISO 26262 ASIL-D ไม่มีทางยอมรับได้อย่างเด็ดขาด ข้อมูล Point Cloud ของแผนที่ HD ขนาดใหญ่ กับคำสั่งเบรกฉุกเฉิน (AEB) ถูกนำมาเขียนปะปนลงใน **FIFO คิวเดี่ยวขนาด 64KB** เดียวกันสินะ หากมีแพ็กเก็ต AEB ส่งเข้ามาในระหว่างที่ข้อมูลแผนที่กำลังอัดแน่นเต็มบัฟเฟอร์อยู่ จะเกิดอะไรขึ้นหรือครับ?

**タナボディ (Thanabodee):**  
「古川技監、ギガビットイーサネットの伝送帯域は非常に広いため、64KBのバッファであれば通常数百マイクロ秒で完全に掃き出されます。そのため、緊急ブレーキパケットも許容遅延時間内に十分相手先へ届くと試算しておりました。BRAMリソースの消費を最小限に抑えるためのトレードオフでした。」  
*(Furukawa-gikan, gigabitto īsanetto no densō taiiki wa hijō ni hiroi tame, 64KB no baffa de areba tsūjō sū-hyaku maikuro-byō de kanzen ni hakidasaremasu. Sono tame, kinkyū burēki paketto mo kyoyō chien jikan-nai ni jūbun aitesaki e todoku to shisan shite orimashita. BRAM risōsu no shōhi wo saishōgen ni osaeru tame no torēdoofu deshita.)*  
**คำแปล:** หัวหน้าฟุรุคาวะครับ แบนด์วิดท์ของ Gigabit Ethernet นั้นกว้างมาก บัฟเฟอร์ขนาด 64KB ปกติจะถูกระบายออกหมดภายในเวลาไม่กี่ร้อยไมโครวินาทีครับ ผมจึงประเมินว่าแพ็กเก็ตเบรกฉุกเฉินน่าจะส่งถึงปลายทางได้ทันกรอบเวลาที่ยอมรับได้ครับ นี่เป็นการประนีประนอมเพื่อประหยัดทรัพยากร BRAM ครับ

**古川技監 (Furukawa):**  
「『通常は』という言葉は、機能安全の世界では禁止用語だよ！もし外部ポートが一時的なトラフィック輻輳（Congestion）でフロー制御（PAUSEフレーム）を受けたらどうする？送信が数ミリ秒停止しただけで、64KBのキューは完全に詰まる！その背後に並んだブレーキパケットは、前方の低優先度マップデータが全て送信し尽くされるまで、100ミリ秒以上も待たされるんだ！これが典型的な**先頭ブロッキング（Head-of-Line Blocking）**だよ！100ms遅れたら、60km/hで走る車は1.7メートルも進んで歩行者を轢き殺してしまうんだぞ！」  
*("Tsūjō wa" to iu kotoba wa, kinō anzen no sekai dewa kinshi yōgo da yo! Moshi gaibu pōto ga ichijiteki na toraffikku fukusō de furō seigyo (PAUSE furēmu) wo uketara dō suru? Sōshin ga sū-miribyō teishi shita dake de, 64KB no kyū wa kanzen ni tsumaru! Sono haigo ni naranda burēki paketto wa, zempō no tei-yūsendō mappu dēta ga subete sōshin shitsukusareru made, 100-miribyō ijō mo matasareru n da! Kore ga tenkeiteki na sentō burokkingu da yo! 100ms okuretara, 60km/h de hashiru kuruma wa 1.7-mētoru mo susunde hokōsha wo hikikoroshite shimau n da zo!)*  
**คำแปล:** คำว่า "ปกติ" น่ะ เป็นคำต้องห้ามในโลกของ Functional Safety เชียวนะ! ถ้าเกิดพอร์ตภายนอกเกิดสภาวะรถติดชั่วคราวแล้วได้รับ Flow Control (PAUSE Frame) ขึ้นมาล่ะจะทำยังไง? แค่การส่งหยุดชะงักไปไม่กี่มิลลิวินาที คิวขนาด 64KB มันจะตันสนิททันที! และแพ็กเก็ตเบรกที่ต่อท้ายอยู่ จะต้องถูกบังคับให้รอนานกว่า 100 มิลลิวินาทีจนกว่าข้อมูลแผนที่ความสำคัญต่ำที่อยู่ข้างหน้าจะถูกส่งจนหมด! นี่คือตัวอย่างคลาสสิกของ **Head-of-Line Blocking** เลยนะ! ถ้าเบรกล่าช้าไป 100 ms รถที่วิ่ง 60 km/h มันจะไถลต่อไปอีก 1.7 เมตรและชนคนเดินถนนเสียชีวิตเชียวนะ!

**タナボディ (Thanabodee):**  
「ヒッ……！低優先度データの滞留が、安全臨界信号の伝送を遮断する致命的なリスクを痛感いたしました……！BRAMを惜しんで人命を危機に晒すところでした……！」  
*(Hi'... Tei-yūsendō dēta no tairyū ga, anzen rinkai shingō no densō wo shadan suru chimeiteki na risuku wo tsūkan itashimashita...! BRAM wo oshinde jinmei wo kiki ni sarasu tokoro deshita...!)*  
**คำแปล:** ฮึก...! ผมตระหนักถึงความเสี่ยงร้ายแรงที่การตกค้างของข้อมูลความสำคัญต่ำจะไปตัดขาดการส่งสัญญาณความปลอดภัยขั้นวิกฤตแล้วครับ...! เกือบจะเอาชีวิตคนไปเสี่ยงเพียงเพื่อประหยัดก้อน BRAM แล้วครับ...!

**古川技監 (Furukawa):**  
「安全を最優先にしなさい。直ちに**4レベルの仮想チャネル（Virtual Channels）を持つマルチキュー構成**へ改版すること！緊急制御パケットは独立したStrict Priorityキューに隔離し、マップデータがいくら詰まっていようと最優先で割り込み出力できる回路にしなさい。さらに、重み付きラウンドロビン（WRR）を導入して低優先度キューの飢餓（Starvation）も防止すること。SVAアサーションで緊急パケットの遅延が最悪でも10マイクロ秒以内であることを証明して再審査に提出しなさい！」  
*(Anzen wo saiyūsen ni shinasai. Tadachini 4-reberu no kasō chaneru wo motsu maruchikyū kōsei e kaihan suru koto! Kinkyū seigyo paketto wa dokuritsu shita Strict Priority kyū ni kakuri shi, mappu dēta ga ikura tsumatte iyōto saiyūsen de warikomi shutsuryoku dekiru kairo ni shinasai. Sarani, omomitsuki raundorobin wo dōnyū shite tei-yūsendō kyū no kiga mo bōshi suru koto. SVA asāshon de kinkyū paketto no chien ga saiaku demo 10-maikuro-byō inai de aru koto wo shōmei shite sai-shinsa ni teishutsu shinasai!)*  
**คำแปล:** จงให้ความสำคัญกับความปลอดภัยสูงสุดเป็นอันดับแรก รีบแก้ไขเป็น **โครงสร้าง Multi-Queue ที่มี Virtual Channels 4 ระดับ** เดี๋ยวนี้! แพ็กเก็ตควบคุมฉุกเฉินจะต้องถูกแยกขาดเข้าไปอยู่ในคิว Strict Priority อิสระ เพื่อให้สามารถแทรกตัวส่งออกไปเป็นลำดับแรกได้ทันทีไม่ว่าข้อมูลแผนที่จะอัดแน่นแค่ไหนก็ตาม และจงนำระบบ Weighted Round-Robin (WRR) มาใช้กับคิวที่เหลือเพื่อป้องกันไม่ให้คิวระดับล่างอดอาหาร (Starvation) ด้วย พร้อมทั้งพิสูจน์ด้วย SVA Assertion ว่าความหน่วงของแพ็กเก็ตฉุกเฉินในกรณีเลวร้ายที่สุดจะไม่เกิน 10 ไมโครวินาที แล้วค่อยมายื่นตรวจรับรองใหม่!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณส่วนแบ่งแบนด์วิดท์ภายใต้ Weighted Round-Robin (WRR) Scheduler
ในระบบสวิตช์เครือข่ายความเร็วสูง สถาปัตยกรรม Priority FIFO ประกอบด้วย 3 คิวที่มีทราฟฟิกไหลเข้ามาเต็มพิกัดตลอดเวลา (Fully Saturated Queues):
* **Queue 2 (High Priority):** กำหนดน้ำหนัก $W_2 = 5$
* **Queue 1 (Medium Priority):** กำหนดน้ำหนัก $W_1 = 3$
* **Queue 0 (Low Priority / Best-Effort):** กำหนดน้ำหนัก $W_0 = 2$
* สวิตช์ดึงข้อมูลออกด้วยอัตราความเร็วคงที่รวม: $BW_{total} = 10.0\text{ Gbps}$
* ทุกแพ็กเก็ตมีขนาดความยาวเท่ากันคงที่ ($Fixed\ Length$)

จงคำนวณหาค่า **แบนด์วิดท์เฉลี่ยที่ได้รับการการันตี (Guaranteed Bandwidth)** ของแต่ละคิว ($BW_2, BW_1, BW_0$) ตามหลักการคำนวณ WRR!

---

#### ตัวเลือก:
* **ก)** $BW_2 = 5.0\text{ Gbps}$, $BW_1 = 3.0\text{ Gbps}$, $BW_0 = 2.0\text{ Gbps}$
* **ข)** $BW_2 = 10.0\text{ Gbps}$, $BW_1 = 0.0\text{ Gbps}$, $BW_0 = 0.0\text{ Gbps}$ (คิวบนกินหมด)
* **ค)** $BW_2 = 3.33\text{ Gbps}$, $BW_1 = 3.33\text{ Gbps}$, $BW_0 = 3.33\text{ Gbps}$ (แบ่งเท่ากัน)
* **ง)** $BW_2 = 6.0\text{ Gbps}$, $BW_1 = 2.5\text{ Gbps}$, $BW_0 = 1.5\text{ Gbps}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การคำนวณผลรวมของค่าน้ำหนัก (Total Weights: $W_{total}$):
$$W_{total} = W_2 + W_1 + W_0 = 5 + 3 + 2 = 10$$

##### 2. การคำนวณสัดส่วนแบนด์วิดท์ของแต่ละคิว:
* **Queue 2:**
  $$BW_2 = BW_{total} \times \frac{W_2}{W_{total}} = 10.0\text{ Gbps} \times \frac{5}{10} = \mathbf{5.0\text{ Gbps} \quad (50\%)}$$
* **Queue 1:**
  $$BW_1 = BW_{total} \times \frac{W_1}{W_{total}} = 10.0\text{ Gbps} \times \frac{3}{10} = \mathbf{3.0\text{ Gbps} \quad (30\%)}$$
* **Queue 0:**
  $$BW_0 = BW_{total} \times \frac{W_0}{W_{total}} = 10.0\text{ Gbps} \times \frac{2}{10} = \mathbf{2.0\text{ Gbps} \quad (20\%)}$$

##### ข้อคิดเชิงวิศวกรรม:
นี่คือความงดงามของ WRR! แม้ว่า Queue 2 จะเป็นคิวความสำคัญสูงสุดและมีข้อมูลอัดแน่นตลอดเวลา แต่ Queue 0 (Low Priority) ก็ยังคงได้รับการ **การันตีแบนด์วิดท์ขั้นต่ำอย่างแน่นอนที่ $2.0\text{ Gbps}$ ($20\%$)** เสมอ ทำให้ไม่เกิดสภาวะ Starvation ในขณะที่หากใช้ Strict Priority (ข้อ ข) Queue 0 จะได้แบนด์วิดท์เป็นศูนย์และอดอาหารอย่างถาวร!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** เป็นผลลัพธ์ของ Strict Priority ไม่ใช่ Weighted Round-Robin
* **ข้อ ค):** เป็นผลลัพธ์ของ Deficit-less Round-Robin แบบไม่คิดค่าน้ำหนัก (Equal Sharing)
* **ข้อ ง):** คำนวณสัดส่วนคณิตศาสตร์ผิดพลาด

---

### ข้อที่ 2: วิกฤตการณ์ Priority Inversion ในระบบ Multi-Queue
ในระบบควบคุมเครื่องบินรบ สัญญาณข้อมูลแบ่งออกเป็น 2 คิว: คิวระดับสูง (High Priority) และคิวระดับต่ำ (Low Priority) โดยทั้งสองคิวแชร์หน่วยความจำ FIFO กลางร่วมกัน (Shared BRAM Pool) ขนาด $16\text{ KB}$:
หากวิศวกร **ไม่ได้กำหนดเพดานจำกัดความจุสูงสุดของแต่ละคิว (No Per-Queue Quota Limit)**:
เหตุการณ์ใดต่อไปนี้จะก่อให้เกิดสภาวะ **Priority Inversion / System Failure**?

---

#### ตัวเลือก:
* **ก)** คิวระดับต่ำยิงข้อมูลขนาดใหญ่ $16\text{ KB}$ เข้ามาจนเต็มหน่วยความจำ BRAM ทั้งก้อน ทำให้เมื่อแพ็กเก็ตฉุกเฉินระดับสูงเดินทางมาถึง บัฟเฟอร์ไม่มีพื้นที่ว่างเหลือให้เขียนลงไปได้ และแพ็กเก็ตฉุกเฉินถูกทิ้ง (Dropped) ทันที
* **ข)** ความถี่ของสัญญาณนาฬิกาของคิวระดับสูงลดลงเหลือครึ่งหนึ่ง
* **ค)** ข้อมูลในคิวระดับสูงจะถูกแปลงเป็น Big-Endian โดยอัตโนมัติ
* **ง)** วงจร BRAM จะเกิดกระแสไฟเกินจนชิปตัดการทำงาน

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **กับดักของ Shared Memory โดยไม่มี Quota:**
   แม้ว่าระบบจะมีตัวจัดคิว (Scheduler) ที่ฉลาดล้ำเพียงใด แต่หาก **ชั้นหน่วยความจำกายภาพ (Physical Memory)** เป็นแบบแชร์ร่วมกันโดยไม่มีการจำกัดเพดาน:
   * ทราฟฟิกความสำคัญต่ำสามารถหลั่งไหลเข้ามาจนกินพื้นที่หน่วยความจำจนหมดเกลี้ยง $16\text{ KB}$
   * เมื่อแพ็กเก็ตฉุกเฉินความสำคัญสูงเดินทางมาถึง พอร์ตเขียนจะพบว่าหน่วยความจำรวมเต็มพิกัด (`shared_full = 1`)
   * ส่งผลให้แพ็กเก็ตฉุกเฉินไม่สามารถเขียนลงบัฟเฟอร์ได้ และถูกปฏิเสธหรือถูกทิ้ง (Buffer Starvation at Ingress)
2. **แนวทางแก้ไขตามมาตรฐานสากล (The Senior Fix):**
   จะต้องมีการกำหนด **Per-Queue Watermark Quota** เช่น:
   * คิวระดับต่ำอนุญาตให้ใช้พื้นที่ได้สูงสุดไม่เกิน $60\%$ ของความจุรวม ($9.6\text{ KB}$)
   * เพื่อสำรองพื้นที่อย่างน้อย $40\%$ ($6.4\text{ KB}$) ไว้ให้คิวระดับสูงเสมอ ไม่ว่าสถานการณ์ภายนอกจะเลวร้ายเพียงใดก็ตาม!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** การแบ่งปันหน่วยความจำไม่มีผลต่อความถี่ของสัญญาณนาฬิกา
* **ข้อ ค):** Endianness เป็นเรื่องของ Format ข้อมูล ไม่เกี่ยวข้องกับขนาดของบัฟเฟอร์
* **ข้อ ง):** ปัญหา Buffer Exhaustion เป็นเรื่องของลอจิก ไม่ได้ทำให้เกิดกระแสเกินทางไฟฟ้า

---

### ข้อที่ 3: บทบาทของ Virtual Channels ในบัสมาตรฐาน PCI Express
ในมาตรฐาน PCI Express (PCIe Base Specification) ทำไมจึงต้องมีการกำหนดสถาปัตยกรรม **Virtual Channels (VC0, VC1 .. VC7)** ขึ้นมาใช้งาน?

---

#### ตัวเลือก:
* **ก)** เพื่อเพิ่มความเร็วของสายทองแดงจาก 8 GT/s เป็น 16 GT/s
* **ข)** เพื่อแยกเส้นทางเดินข้อมูลและการควบคุมการไหล (Independent Credit-Based Flow Control) สำหรับทราฟฟิกแต่ละระดับความสำคัญ ทำให้ทราฟฟิกแบบ Isochronous (Real-time Audio/Video) สามารถไหลผ่าน VC1 ได้อย่างราบรื่นโดยไม่ถูกบล็อกจากการติดขัด (Congestion) ของทราฟฟิกทั่วไปใน VC0
* **ค)** เพื่อลดจำนวนพินบนขั้วต่อ PCIe Slot ลง 50%
* **ง)** เพื่อให้สามารถต่อสายดินผ่านพอร์ต PCIe ได้

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **กลไกของ PCIe Virtual Channels:**
   PCIe ใช้การควบคุมการไหลแบบอิงเครดิต (Credit-Based Flow Control) ที่ระดับ Transaction Layer:
   * หากมีช่องทางเดียว (VC0) เมื่อปลายทางมีบัฟเฟอร์เต็ม เครดิตของ VC0 จะหมดลง และทราฟฟิกทั้งหมดบนลิงก์จะหยุดชะงัก (Stall)
   * การสร้าง Virtual Channels (เช่น VC0 และ VC1) จะทำให้แต่ละช่องทางมี **พูลเครดิตและบัฟเฟอร์แยกอิสระจากกันบนสายส่งเส้นเดียวกัน**
   * แม้ว่า VC0 จะเครดิตหมดและติดขัดจากทราฟฟิกการเขียนดิสก์ขนาดใหญ่ แต่ข้อมูลเรียลไทม์บน VC1 จะยังมีเครดิตเหลืออยู่และสามารถแล่นฉิวแซงหน้าไปได้ทันที ปราศจาก HoL Blocking อย่างสมบูรณ์แบบ!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ความเร็วของสายส่งถูกกำหนดโดย Gen Rate (Gen1/2/3/4/5) และวงจร PHY ไม่ได้ขึ้นกับจำนวน VC
* **ข้อ ค):** Virtual Channels เป็นแนวคิดทางลอจิกใน Data Link/Transaction Layer ไม่ได้ลดจำนวนพินทางกายภาพ
* **ข้อ ง):** เป็นคำตอบที่ไร้สาระทางวิศวกรรม
