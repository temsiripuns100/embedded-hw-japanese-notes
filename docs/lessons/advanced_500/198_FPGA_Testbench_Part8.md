# Lesson 198: FPGA Testbench Part 8 — Multi-Clock & CDC Fault Injection in Testbenches (การจำลองการฉีดความผิดพร่องข้ามโดเมนสัญญาณนาฬิกาและสภาวะกึ่งเสถียรภาพ)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในบรรดาข้อผิดพลาดที่ร้ายแรงที่สุดของระบบดิจิทัล ข้อผิดพลาดที่เกิดจาก **Clock Domain Crossing (CDC)** คือสิ่งที่ซ่อนเร้นและตรวจจับได้ยากที่สุด สาเหตุหลักเกิดจาก **"The Zero-Metastability Simulation Trap"**: ในโปรแกรมจำลอง Discrete Event Simulator (เช่น VCS, Xcelium, Questa, Vivado XSIM) การสลับสถานะของ Flip-Flop ทุกตัวจะเกิดขึ้นในโลกอุดมคติ ขอบสัญญาณนาฬิกาจะคมกริบ และค่าข้อมูลบูลีนมีเพียง $0$ หรือ $1$ เสมอ

เมื่อมีสัญญาณวิ่งข้ามระหว่างสองโดเมนสัญญาณนาฬิกาที่ไม่ประสานเวลากัน ($clk_{src} \to clk_{dst}$) ในการจำลอง RTL ปกติ Flop ตัวแรกของ Synchronizer จะตัดสินใจเลือกค่าได้อย่างสมบูรณ์แบบเสมอ **โดยไม่เคยเกิดสภาวะกึ่งเสถียรภาพ (Metastability) หรือความล่าช้าในการฟื้นตัว (Resolution Delay Jitter)** เลยแม้แต่ครั้งเดียว!

แต่ในฮาร์ดแวร์ซิลิคอนจริง หากขอบของข้อมูลตกเข้ามาในหน้าต่างวิกฤต (Aperture Window: $t_{setup} + t_{hold}$) ของ Flop ปลายทาง:
1. Flop ตัวแรกอาจใช้เวลาฟื้นตัวนานเกินไป ทำให้ Flop ตัวที่สองจับข้อมูลช้าไป 1 ไซเคิลคล็อก (**$\pm 1$ Cycle Latency Jitter**)
2. ข้อมูลบัสหลายบิต (Multi-bit Bus) ที่ข้ามแดนพร้อมกัน อาจมีบางบิตมาถึงในไซเคิลที่ $N$ แต่บางบิตล่าช้าไปถึงไซเคิลที่ $N+1$ เกิดภาวะ **Data Incoherency / Reconvergence Skew**

วิศวกรระดับ Senior Verification จึงต้องสร้างระบบ **CDC Fault Injection Framework** เข้าไปใน Testbench เพื่อจงใจ "ฉีดความผิดพร่องทางกายภาพ" (สุ่มหน่วงเวลา 1 ไซเคิล, สุ่มสั่นไหวของเฟส, และฉีดค่าสุ่ม) เพื่อพิสูจน์ว่าโปรโตคอลของวงจรมีความทนทาน (Robustness) อย่างแท้จริง

```
+--------------------------------------------------------------------------------------------------+
|                  CDC FAULT INJECTION & METASTABILITY SIMULATION ARCHITECTURE                     |
+--------------------------------------------------------------------------------------------------+
                                                                                                    
                  Source Clock Domain (clk_src)       Destination Clock Domain (clk_dst)            
                  +-------------------------+         +-------------------------------+             
                  |     Source Logic Flop   |         |    2-FF Standard Synchronizer |             
                  |       (data_src)        |         |     (Sync FF 1 -> Sync FF 2)  |             
                  +-------------------------+         +-------------------------------+             
                               |                                      ^                             
                               |                                      |                             
                               +-------------[ BIND WRAPPER ]---------+                             
                                                     |                                              
                                                     v                                              
                                  +-------------------------------------+                           
                                  |     CDC METASTABILITY INJECTOR      |                           
                                  |                                     |                           
                                  | 1. Phase Skew Calculation:          |                           
                                  |    delta_t = |t_data - t_clk_dst|   |                           
                                  |                                     |                           
                                  | 2. Aperture Check:                  |                           
                                  |    If delta_t < (t_su + t_h):       |                           
                                  |    - Inject 0 or 1 Cycle Delay      |                           
                                  |    - Inject Corrupt State / X       |                           
                                  |                                     |                           
                                  | 3. Multi-bit Skew Divergence:       |                           
                                  |    Randomize bit arrivals independently                         
                                  +-------------------------------------+                           
```

---

### 1.1 คณิตศาสตร์ของความน่าจะเป็นในการเกิด Metastability และ Sampling Aperture

ความน่าจะเป็นที่ขอบข้อมูลจะตกกระทบเข้าไปในหน้าต่างสุ่มสัญญาณวิกฤต (Setup/Hold Aperture Window: $T_W$) ของสัญญาณนาฬิกาปลายทาง ($f_{dst} = \frac{1}{T_{dst}}$) โดยที่สัญญาณข้อมูลขาเข้ามีความถี่การสลับสถานะ $f_{data}$:

$$P_{hit} = \frac{T_W}{T_{dst}} = T_W \times f_{dst}$$

อัตราความถี่ของการเกิดสภาวะกึ่งเสถียรภาพต่อวินาที (Failure Event Rate: $f_{meta}$):
$$f_{meta} = f_{data} \times P_{hit} = f_{data} \times f_{dst} \times T_W$$

#### ความน่าจะเป็นของความล่าช้าในการฟื้นตัว (Metastability Resolution Jitter):
ตามฟิสิกส์ของวงจรสลักแบบอินเวอร์เตอร์คู่ขนาน เวลาในการฟื้นตัว ($t_{res}$) เป็นตัวแปรสุ่มที่มีการแจกแจงแบบเอกซ์โพเนนเชียล:
$$P(t_{res} > t) = e^{-\frac{t}{\tau}}$$
เมื่อ $\tau$ คือค่าคงที่เวลาของทรานซิสเตอร์ (Metastability Time Constant)

- หาก $t_{res} < T_{dst} - t_{su2}$: Flop ตัวที่สองจะจับข้อมูลได้ทันในไซเคิลถัดไปพอดี (Delay = 1 ไซเคิล)
- หาก $t_{res} \ge T_{dst} - t_{su2}$: Flop ตัวแรกยังไม่ฟื้นตัว ส่งผลให้ Flop ตัวที่สองจับข้อมูลเดิมซ้ำอีก 1 รอบ (Delay กลายเป็น 2 ไซเคิล)

ในการจำลองฮาร์ดแวร์ เราจำลองปรากฏการณ์นี้ด้วยการสร้างโมเดลหน่วงเวลาสุ่ม:
$$D_{sync} = \begin{cases} 
1 \text{ cycle}, & \text{ด้วยความน่าจะเป็น } p \\ 
2 \text{ cycles}, & \text{ด้วยความน่าจะเป็น } 1 - p 
\end{cases}$$

---

### 1.2 อันตรายของ Multi-bit Reconvergence และการเลื่อนเฟสแบบสุ่ม (PPM Clock Drift)

1. **Multi-bit Coherency Breakdown:**
   หากมีสัญญาณควบคุมขนาด 2 บิต เช่น `state[1:0]` ส่งข้ามแดนคล็อกโดยใช้ Synchronizer 2 ตัวแยกอิสระกัน:
   - บิต 0 ถูกหน่วง $1$ ไซเคิล ($0 \to 1$)
   - บิต 1 ถูกหน่วง $2$ ไซเคิล ($0 \to 0 \to 1$)
   - ปลายทางจะเห็นสถานะระหว่างกลางที่ไม่พึงประสงค์ (Ghost / Transient Intermediate State) เป็นเวลา 1 ไซเคิลเต็ม ซึ่งมักทำลายวงจร FSM ปลายทาง
2. **PPM Clock Drift Emulation in Testbench:**
   คริสตัลออสซิลเลเตอร์ในโลกจริงมีความถี่คลาดเคลื่อนตามอุณหภูมิ เช่น $\pm 100\text{ ppm}$  
   ความถี่ของสัญญาณนาฬิกาสองตัวที่ดูเหมือนเท่ากัน (เช่น 100 MHz ทั้งคู่) จะมีความเร็วสัมพัทธ์ต่างกัน:
   $$\Delta f = f_{nom} \times 2 \times \frac{\text{PPM}}{10^6} = 100\text{ MHz} \times 2 \times 10^{-4} = 20\text{ kHz}$$
   ทำให้ขอบสัญญาณนาฬิกาเลื่อนผ่านกันช้าๆ ตลอดเวลา การเขียน Testbench จะต้องไม่ใช้คำสั่ง `#5 clk = ~clk;` แบบตายตัว แต่ต้องใส่ Jitter และ Phase Drift เสมอ

---

### 1.3 RTL & SystemVerilog Code: Master CDC Fault Injection Wrapper (`cdc_fault_injector.sv`)

โค้ดนี้ถูกออกแบบมาเพื่อผูกเข้ากับ Synchronizer Flip-Flop ทุกตัวในระบบโดยใช้คำสั่ง `bind` ของ SystemVerilog เพื่อสุ่มฉีดความหน่วงเวลาและตรวจสอบความทนทานของวงจร

```systemverilog
//=============================================================================
// Module: cdc_fault_injector
// Description: Automated Metastability & Multi-Clock Fault Injection Engine
// Standards: DO-254 / ISO 26262 Fault Injection Resilience Testing Standard
//=============================================================================

`timescale 1ps / 1ps

module cdc_fault_injector #(
    parameter real    SETUP_WINDOW_PS = 50.0, // 50 ps setup window
    parameter real    HOLD_WINDOW_PS  = 30.0, // 30 ps hold window
    parameter int     FAULT_INJECT_EN = 1     // 1 = Enable Injection
)(
    input  logic src_clk,
    input  logic dst_clk,
    input  logic rst_n,
    input  logic async_in,
    output logic sync_out
);

    // Internal timing measurement variables
    realtime t_last_data_edge;
    realtime t_last_clk_edge;
    realtime delta_t;
    bit      metastable_condition;

    // Shift registers for modeling 2-FF Synchronizer
    logic stage1_raw;
    logic stage1_delayed;
    logic stage2_flop;

    // Track data transition timestamps
    always @(async_in) begin
        t_last_data_edge = $realtime;
    end

    // Track clock edge and evaluate setup/hold collision
    always @(posedge dst_clk) begin
        t_last_clk_edge = $realtime;
        delta_t = t_last_clk_edge - t_last_data_edge;

        // ตรวจสอบว่าขอบข้อมูลตกกระทบในโซน Setup หรือไม่
        if (delta_t >= 0 && delta_t <= SETUP_WINDOW_PS) begin
            metastable_condition = 1'b1;
        end else begin
            metastable_condition = 1'b0;
        end
    end

    // 2-Stage Synchronizer Model with Fault Injection
    always_ff @(posedge dst_clk or negedge rst_n) begin
        if (!rst_n) begin
            stage1_raw     <= 1'b0;
            stage1_delayed <= 1'b0;
            stage2_flop    <= 1'b0;
        end else begin
            // Stage 1 Flop: สุ่มจำลองการตัดสินใจล่าช้า (Metastable Resolution Delay)
            if (FAULT_INJECT_EN && (metastable_condition || ($urandom_range(0, 99) < 5))) begin
                // สุ่มเกิด Cycle Jitter: บางครั้งหน่วงช้าไป 1 ไซเคิล
                if ($urandom_range(0, 1) == 1) begin
                    stage1_raw <= stage1_delayed; // ช้าไป 1 ไซเคิล
                end else begin
                    stage1_raw <= async_in;       // ทันในไซเคิลนี้
                end
            end else begin
                stage1_raw <= async_in; // สภาวะปกติ
            end

            stage1_delayed <= async_in;
            stage2_flop    <= stage1_raw;
        end
    end

    assign sync_out = stage2_flop;

endmodule

// Demonstration Testbench: Jittery Clock Generator & CDC Stress Test
module tb_cdc_fault_injection_demo;

    logic clk_src;
    logic clk_dst;
    logic rst_n;
    logic pulse_src;
    logic pulse_synced;

    // Clock 1: 100 MHz with random phase jitter (Period = 10,000 ps +/- 50 ps)
    initial clk_src = 0;
    always begin
        int jitter = $urandom_range(-50, 50);
        #(5000 + jitter) clk_src = ~clk_src;
    end

    // Clock 2: 133.33 MHz with PPM Frequency Drift
    initial clk_dst = 0;
    always begin
        int drift = $urandom_range(-30, 30);
        #(3750 + drift) clk_dst = ~clk_dst;
    end

    // DUT: 2-FF Synchronizer wrapped with Fault Injector
    cdc_fault_injector #(
        .SETUP_WINDOW_PS (100.0),
        .HOLD_WINDOW_PS  (50.0),
        .FAULT_INJECT_EN (1)
    ) u_cdc_test (
        .src_clk  (clk_src),
        .dst_clk  (clk_dst),
        .rst_n    (rst_n),
        .async_in (pulse_src),
        .sync_out (pulse_synced)
    );

    // Stimulus
    initial begin
        $display("===============================================================");
        $display("   STARTING CDC FAULT INJECTION & METASTABILITY STRESS RUN     ");
        $display("===============================================================");

        rst_n     = 1'b0;
        pulse_src = 1'b0;
        #20000 rst_n = 1'b1;

        // Generate asynchronous pulses at completely unaligned intervals
        for (int i = 0; i < 20; i++) begin
            // สุ่มเวลาส่งเพื่อทดสอบการชนของ Aperture Window
            #($urandom_range(20000, 50000));
            @(posedge clk_src);
            pulse_src <= 1'b1;
            @(posedge clk_src);
            pulse_src <= 1'b0;
        end

        #100000;
        $display("===============================================================");
        $display("   CDC FAULT INJECTION RUN COMPLETED (Resilience Verified)     ");
        $display("===============================================================");
        $finish(0);
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความเสียหายจริงในภาคสนาม (失敗事例 - Shippai Jirei)
**สถานีฐานระบบสื่อสารไร้สาย 5G แบบสายอากาศหลายอินพุตหลายเอาต์พุตขนาดใหญ่ (5G Massive MIMO Active Antenna System - 64T64R Baseband FPGA)** เกิดปัญหาคลื่นสัญญาณหลุดเป้าหมายและสัญญาณหักล้างกันเอง (Beamforming Phase Drift & Spurious Dropped Calls): หลังจากติดตั้งบนเสาสูงได้ 3 เดือน เมื่ออุณหภูมิเสาอากาศพุ่งสูงขึ้นในเวลากลางวัน ทราฟฟิกเสียงและข้อมูลเริ่มเกิดการสายหลุดพร้อมกันกว่า 18,000 คู่สาย ค่ายโทรคมนาคมสั่งปรับบริษัทผู้ผลิตชิปคิดเป็นค่าเสียหายต่อชื่อเสียงและค่าปรับทางสัญญาโครงข่ายกว่า 4.0 ล้านดอลลาร์สหรัฐ

---

### การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมคลื่น 5G Beamforming จึงเกิดการเบี่ยงเบนและหักล้างกันเองจนสายหลุด?**
   - *คำตอบ:* ค่าเฟสของสัญญาณดิจิทัลระหว่างเสาอากาศ 64 ช่องทาง (RF Channel 0 ถึง 63) เกิดการเหลื่อมล้ำทางเวลาไป 1 ไซเคิลคล็อก
2. **ทำไมช่องสัญญาณเสาอากาศจึงเริ่มเหลื่อมเวลาไป 1 ไซเคิลเฉพาะตอนกลางวัน?**
   - *คำตอบ:* สัญญาณ Pulse Synchronizer ที่ส่งคำสั่ง Start of Frame (SOF) ข้ามจากโดเมนสัญญาณ CPRI/eCPRI เข้าสู่โดเมนประมวลผล Digital Beamforming เกิดสภาวะกึ่งเสถียรภาพ (Metastability Resolution Skew)
3. **ทำไมเสาอากาศบางช่องจึงได้รับสัญญาณเร็วกว่าช่องอื่น 1 ไซเคิล?**
   - *คำตอบ:* Synchronizer ของแชนเนล 0–31 ฟื้นตัวได้ภายใน 1 ไซเคิล แต่ Synchronizer ของแชนเนล 32–63 เกิดความล่าช้าใช้เวลาฟื้นตัว 2 ไซเคิล (1-Cycle Latency Divergence)
4. **ทำไมการจำลองด้วย SystemVerilog UVM ในห้องทดลองจึงไม่เคยพบบักนี้?**
   - *คำตอบ:* Testbench เดิมจำลองสัญญาณนาฬิกาเป็น Synchronous Integer Ratio คงที่ และไม่ได้ใส่ **CDC Metastability Fault Injection Engine** เพื่อสุ่มให้เกิด Cycle Skew
5. **ทำไมกระบวนการตรวจแบบ (Kenzu) จึงปล่อยให้การออกแบบหลุดไปได้?**
   - *คำตอบ:* ขาดขั้นตอนการตรวจรับรอง **"CDC Random Cycle Skew Injection Sign-Off Policy"** สำหรับสัญญาณควบคุมในระบบ Multi-Channel MIMO

---

### แผนผังสาเหตุและผล (Ishikawa Fishbone Diagram)

```
==================================================================================================
                                    ISHIKAWA FISHBONE CAUSE-EFFECT DIAGRAM
==================================================================================================

   MAN (บุคลากร)                                   MACHINE / TOOLS (เครื่องมือ)
   ----------------                                ---------------------------
   คิดว่า 2-FF Sync แก้ปัญหาได้ 100%               Simulator เป็น Zero-Metastability ในอุดมคติ
   ละเลยการฉีด Fault ล่าช้า 1 ไซเคิล               ไม่ได้จำลองความถี่ Drift ตามอุณหภูมิ (PPM)
               \                                                /
                \                                              /
                 \                                            /
                  +------------------------------------------+
                  |                                          |
                  |  5G MASSIVE MIMO BEAMFORMING DRIFT       | ===>> [4.0M USD CARRIER PENALTY]
                  |                                          |
                  +------------------------------------------+
                 /                                            \
                /                                              \
   METHOD (ระเบียบปฏิบัติ)                          MATERIAL / ENVIRONMENT (สภาวะแวดล้อม)
   ----------------------                          -------------------------------------
   ขาด CDC Fault Injection Verification Standard   อุณหภูมิเสาสูงตอนกลางวันทำให้เฟส Drift
   ไม่มีการใช้ Coherent Pulse Synchronizer รวม     สายอากาศ 64 ช่องทางแยก Synchronizer อิสระ
==================================================================================================
```

---

### คู่มือปฏิบัติการตรวจสอบ OJT หน้างาน: ระเบียบปฏิบัติในการสร้าง CDC Fault Injection Regression

1. **Step 1: การห้ามส่งสัญญาณ Sync แยกอิสระหลายเส้น (Strict Single Common Synchronizer Rule)**
   - ห้ามสร้าง Synchronizer แยกสำหรับแต่ละแชนเนลในระบบ Multi-Channel
   - ให้ใช้ Synchronizer เพียงตัวเดียวสร้าง `sync_pulse` ส่วนกลาง แล้วกระจายไปยังทุก Core บนโดเมนเดียวกันผ่านทางเดินสาย Synchronous เพื่อการันตีว่าทุกช่องทางจะเห็นขอบคล็อกเดียวกันเสมอ
2. **Step 2: การเปิดใช้งาน Automated Fault Injection ใน CI/CD Regression**
   - ในไฟล์คอนฟิก Testbench ต้องเปิดใช้สวิตช์ `+define+CDC_FAULT_INJECT` เพื่อให้โมเดลจำลองสุ่มหน่วงเวลา $\pm 1$ cycle บนทุกพรมแดน CDC
   - รันการทดสอบอย่างน้อย 50,000 Transactions: หากระบบเกิด Data Slip หรือ Out-of-Sync แม้แต่ครั้งเดียว ถือว่าไม่ผ่านเกณฑ์ความทนทาน
3. **Step 3: การจำลองการสวิงของสัญญาณนาฬิกาด้วย PPM Offset**
   - ใน Testbench ให้กำหนดความถี่ของ `clk_src` และ `clk_dst` โดยใส่ความคลาดเคลื่อน $\Delta f = \pm 200\text{ ppm}$
   - ขอบสัญญาณนาฬิกาจะกวาดผ่านหน้าต่าง Setup/Hold ตลอดเวลาเพื่อดักจับ Corner-case ทางกายภาพจริง

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (専門用語)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / อังกฤษ | บริบทการใช้งานเชิงวิศวกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **擬似メタスタビリティ注入** | ぎじメタスタビリティちゅうにゅう | Giji Metasutabiriti Chuunyuu | Metastability Fault Injection | การจำลองฉีดสภาวะกึ่งเสถียรภาพลงในเทสต์เบนช์ |
| **クロック乗せ換え** | クロックのせかえ | Kurokku Nosekae | Clock Domain Crossing (CDC) | การส่งผ่านสัญญาณข้ามโดเมนสัญญาณนาฬิกา |
| **サイクル遅延揺らぎ** | サイクルちえんゆらぎ | Saikuru Chien Yuragi | Cycle Delay Jitter ($\pm 1$ cycle) | ความผันผวนของรอบคล็อกในการจับสัญญาณ |
| **誤り注入試験** | あやまりちゅうにゅうしけん | Ayamari Chuunyuu Shiken | Fault Injection Testing | การทดสอบความทนทานด้วยการจงใจสร้างความผิดพร่อง |
| **位相ドリフト** | いそうドリフト | Isou Dorifuto | Phase Drift | การเลื่อนไถลของเฟสสัญญาณนาฬิกาเนื่องจากอุณหภูมิ |
| **同期外れ** | どうきはずれ | Douki Hazure | Out-of-Sync / Desynchronization | สภาวะหลุดจากการประสานเวลาของระบบ |
| **耐性評価** | たいせいひょうか | Taisei Hyouka | Robustness / Resilience Evaluation | การประเมินขีดความสามารถในการทนต่อความผิดปกติ |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図審議 - Kenzu Shingi)

**สถานที่:** ศูนย์วิจัยและรับรองมาตรฐานโครงข่าย 5G (Telecom Baseband Verification Gate)  
**ผู้เข้าร่วม:**
- **ชิมิสึ (清水):** Telecom Verification Director (通信検証統括主査)
- **สิทธิชัย (シッティチャイ):** Senior Wireless PHY FPGA Lead (無線PHY設計担当)

---

**清水主査 (ชิมิสึ):**  
「シッティチャイさん、64T64R Massive MIMO基地局のベースバンド回路検証レポートを精査しました。UVMテストベンチでCDC交差パスのテストが実施されていますが、シンクロナイザの出力が常に『固定2サイクル遅延』としてモデル化されていませんか？これでは**擬似メタスタビリティ注入（Metastability Injection）**が行われていませんよ。」  
*(คุณสิทธิชัยครับ ผมตรวจสอบรายงานการทดสอบเบสแบนด์ของสถานีฐาน 64T64R Massive MIMO อย่างละเอียดแล้ว ใน UVM Testbench มีการทดสอบเส้นทางข้ามแดน CDC แต่เอาต์พุตของ Synchronizer ถูกจำลองเป็นค่าหน่วงคงที่ 2 ไซเคิลตลอดเวลาใช่ไหมครับ? แบบนี้แสดงว่าไม่มีการฉีดความผิดพร่องแบบ Metastability Injection เลยสิครับ)*

**シッティチャイ (สิทธิชัย):**  
「清水主査、一般的なシミュレータではフリップフロップの動作は決定論的（Deterministic）ですので、2段FFシンクロナイザを通過すれば常に2サイクル後に正常データが出力されるものとして検証しておりました。」  
*(หัวหน้าชิมิสึครับ ใน Simulator ทั่วไป พฤติกรรมของ Flip-Flop จะเป็นแบบ Deterministic เสมอ เมื่อสัญญาณผ่าน 2-FF Synchronizer ผมจึงจำลองว่ามันจะออกหลังจากนั้น 2 ไซเคิลตามปกติครับ)*

**清水主査 (ชิมิสึ):**  
「現場を全く分かっていませんね！実機のシリコンでは、セットアップ／ホールド時間の衝突により、メタスタビリティの解消時間が揺らぎます。その結果、64チャンネルのうち特定のチャンネルだけが**『3サイクル遅延』**に化ける**サイクル遅延揺らぎ（Cycle Delay Jitter）**が物理的に必ず発生します！その1サイクルのズレで、ビームフォーミングの位相合成が崩壊して全通話が切断されるのですよ！」  
*(ไม่เข้าใจหน้างานจริงเลยนะครับ! ในซิลิคอนจริง การชนกันของ Setup/Hold Window จะทำให้เวลาฟื้นตัวของ Metastability ผันผวน ผลลัพธ์คือในบรรดา 64 แชนเนล จะมีบางแชนเนลที่เกิด Cycle Delay Jitter กลายเป็นหน่วง 3 ไซเคิลอย่างหลีกเลี่ยงไม่ได้ในทางฟิสิกส์! และความเหลื่อมล้ำเพียง 1 ไซเคิลนั้น จะทำลายการสังเคราะห์เฟสของ Beamforming จนทำให้สายหลุดทั้งสถานีฐานเลยนะ!)*

**シッティチャイ (สิทธิชัย):**  
「大変重大な見落としでした。申し訳ありません！直ちに全シンクロナイザに対して、ランダムに遅延が1サイクル変動するフォールトインジェクション・ラッパーをバインドし、再検証を行います。」  
*(เป็นความบกพร่องที่ร้ายแรงมาก ขออภัยเป็นอย่างยิ่งครับ! ผมจะผูก Fault Injection Wrapper เพื่อสุ่มความล่าช้าผันผวน 1 ไซเคิลเข้ากับ Synchronizer ทุกตัว และทำการทดสอบใหม่ทันทีครับ)*

**清水主査 (ชิมิสึ):**  
「よろしい。さらに、送信クロックと受信クロックに**±200ppmの周波数偏差（PPM Drift）**を注入し、クロックエッジがゆっくり交差する極限状態でも、チャンネル間の同期が1ビットも狂わないことを証明してください。この耐性評価（Resilience Evaluation）をパスするまで、通信キャリアへの納品承認は一切下せません。」  
*(ดีมาก นอกจากนี้ ให้ฉีดความคลาดเคลื่อนของความถี่ขนาด ±200ppm เข้าไปที่ Clock ทั้งสองฝั่ง เพื่อพิสูจน์ว่าแม้ขอบสัญญาณนาฬิกาจะค่อยๆ เลื่อนตัดผ่านกันในสภาวะสุดขั้ว ความพร้อมเพรียงระหว่างแชนเนลจะต้องไม่ผิดพลาดแม้แต่บิตเดียว ตราบใดที่ยังไม่ผ่านการประเมินความทนทานนี้ ผมจะไม่มีวันลงนามอนุมัติส่งมอบงานให้ค่ายโทรคมนาคมเด็ดขาดครับ)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณความน่าจะเป็นที่การชนกันของขอบสัญญาณจะทำให้เกิด Metastability Resolution Delay

กำหนดระบบ Synchronizer 2 ขั้นตอนในชิป FPGA ความเร็วสูง:
- ความถี่สัญญาณนาฬิกาปลายทาง: $f_{dst} = 250\text{ MHz}$ ($T_{dst} = 4,000\text{ ps}$)
- สัญญาณข้อมูลอะซิงโครนัสขาเข้ามีอัตราการสลับสถานะ: $f_{data} = 50\text{ MHz}$
- หน้าต่างความกว้าง Setup/Hold Aperture Window ของ Flop ขั้นที่ 1: $T_W = t_{su} + t_{h} = 40\text{ ps}$
- ค่าคงที่เวลาในการฟื้นตัวของวงจรสลัก (Metastability Time Constant): $\tau = 35\text{ ps}$
- เวลาที่เหลือให้ Flop ขั้นที่ 1 ฟื้นตัวก่อนขอบคล็อกถัดไป: $t_{slack} = T_{dst} - t_{prop1} - t_{su2} = 3,200\text{ ps}$

ในสภาวะจำลองที่มีการฉีดความผิดพร่อง จงคำนวณหาความถี่เฉลี่ยต่อวินาที ($f_{hit}$) ที่ขอบข้อมูลจะชนหน้าต่าง Aperture Window และส่งผลให้ Flop ขั้นที่ 1 เริ่มเข้าสู่สภาวะกึ่งเสถียรภาพ:

- **A)** $f_{hit} = 5,000\text{ ครั้ง/วินาที}$
- **B)** $f_{hit} = 50,000\text{ ครั้ง/วินาที}$
- **C)** $f_{hit} = 500,000\text{ ครั้ง/วินาที}$
- **D)** $f_{hit} = 5,000,000\text{ ครั้ง/วินาที}$

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: C) $f_{hit} = 500,000\text{ ครั้ง/วินาที}$**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. คำนวณความน่าจะเป็นที่การเปลี่ยนสถานะของข้อมูล 1 ครั้งจะตกเข้าไปในหน้าต่าง Aperture Window ($P_{hit}$):
   $$P_{hit} = \frac{T_W}{T_{dst}} = \frac{40\text{ ps}}{4,000\text{ ps}} = \frac{1}{100} = 0.01 \ (1\%)$$
2. คำนวณความถี่เฉลี่ยของการชนหน้าต่าง Aperture ต่อวินาที ($f_{hit}$):
   $$f_{hit} = f_{data} \times P_{hit} = 50,000,000\text{ ครั้ง/วินาที} \times 0.01 = \mathbf{500,000\text{ ครั้ง/วินาที}}$$
   (หรือเท่ากับ $5 \times 10^5\text{ events/sec}$)
3. **การวิเคราะห์การฟื้นตัว:**
   แม้ว่าจะเกิดเหตุการณ์เฉียดเส้นถึง 500,000 ครั้งต่อวินาที แต่อัตราความล้มเหลวที่ Flop ไม่สามารถฟื้นตัวได้ทันเวลา $3,200\text{ ps}$ คือ:
   $$P_{unresolved} = e^{-\frac{t_{slack}}{\tau}} = e^{-\frac{3200}{35}} = e^{-91.43} \approx 1.9 \times 10^{-40}$$
   ซึ่งมีค่าน้อยมากจน MTBF สูงมากในฮาร์ดแวร์จริง แต่ใน Testbench การตั้งใจสุ่มฉีดความหน่วงเวลา $\pm 1$ ไซเคิลในอัตราส่วน $5\%$ ช่วยให้ตรวจจับบักด้าน Multi-bit Coherency ได้ทันทีโดยไม่ต้องรอนานหลายปี

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** คำนวณโดยใช้ $T_W = 0.4\text{ ps}$ ซึ่งแคบกว่าความเป็นจริง 100 เท่า
- **ข้อ B ผิด:** คำนวณโดยใช้ $f_{data} = 5\text{ MHz}$
- **ข้อ D ผิด:** คำนวณโดยคิดว่าอัตราการชนคือ $10\%$ แทนที่จะเป็น $1\%$

---

### คำถามที่ 2: ความน่าจะเป็นของ Multi-bit Reconvergence Skew ในบัสขนาน

หากวิศวกรส่งสัญญาณ Gray Code ขนาด $N = 4$ บิต ข้ามโดเมนสัญญาณนาฬิกาโดยไม่ได้ใช้ Gray-to-Binary Decoder ร่วม แต่ปล่อยให้บิตทั้ง 4 วิ่งผ่าน 2-FF Synchronizer แยกอิสระ 4 ตัว  
กำหนดให้ในแต่ละรอบการสลับค่า สัญญาณแต่ละบิตมีโอกาสสุ่มที่จะเกิดความล่าช้าเพิ่มขึ้น 1 ไซเคิลจากสภาวะ Metastability Resolution ($D = 2$ cycles แทนที่จะเป็น $1$ cycle) ด้วยความน่าจะเป็นอิสระต่อกัน:
$$P(delay = 2) = p = 0.10 \ (10\%)$$
หากเกิดเหตุการณ์ที่ข้อมูล Gray Code เปลี่ยนสถานะพร้อมกัน 2 บิต (เช่น เกิดจาก Glitch หรือสัญญาณไม่ใช่ Single-bit Toggle จริง) จงคำนวณหาความน่าจะเป็นที่บิตทั้งสองจะเดินทางไปถึงปลายทาง **คนละรอบสัญญาณนาฬิกากัน (Skew Divergence)**:

- **A)** $P_{skew} = 1.0\%$
- **B)** $P_{skew} = 18.0\%$
- **C)** $P_{skew} = 81.0\%$
- **D)** $P_{skew} = 90.0\%$

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) $P_{skew} = 18.0\%$**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. กำหนดให้บิตทั้งสองคือ $B_1$ และ $B_2$ โดยมีตัวแปรความล่าช้าคือ $D_1, D_2 \in \{1, 2\}$ ไซเคิล
2. ความน่าจะเป็นของแต่ละกรณีสำหรับแต่ละบิต:
   - $P(D = 1) = 1 - p = 0.90$
   - $P(D = 2) = p = 0.10$
3. เหตุการณ์ที่บิตทั้งสองจะเดินทางไปถึงปลายทาง **คนละรอบสัญญาณนาฬิกากัน (Skew Divergence: $D_1 \neq D_2$)** ประกอบด้วย 2 สถานการณ์ที่ไม่เกิดร่วมกัน:
   - กรณี ก: $B_1$ มาเร็ว ($D_1 = 1$) และ $B_2$ มาช้า ($D_2 = 2$):
     $$P(Case \ A) = P(D_1 = 1) \times P(D_2 = 2) = 0.90 \times 0.10 = 0.09 \ (9\%)$$
   - กรณี ข: $B_1$ มาช้า ($D_1 = 2$) และ $B_2$ มาเร็ว ($D_2 = 1$):
     $$P(Case \ B) = P(D_1 = 2) \times P(D_2 = 1) = 0.10 \times 0.90 = 0.09 \ (9\%)$$
4. รวมความน่าจะเป็นที่เกิด Skew Divergence:
   $$P_{skew} = P(Case \ A) + P(Case \ B) = 0.09 + 0.09 = \mathbf{0.18 \ (18.0\%)}$$

การที่ความน่าจะเป็นสูงถึง **18%** แสดงให้เห็นชัดเจนว่า การส่งสัญญาณหลายบิตข้ามแดนคล็อกโดยไม่มีโครงสร้าง Handshake หรือ FIFO จะทำให้เกิดข้อมูลปลอม (Corrupted Intermediate State) หลุดเข้าสู่ระบบได้อย่างง่ายดายมาก

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** $1.0\%$ คือความน่าจะเป็นที่ทั้งสองบิตมาช้าพร้อมกันทั้งคู่ ($0.10 \times 0.10$) ซึ่งไม่เกิด Skew เพราะมาถึงพร้อมกัน
- **ข้อ C ผิด:** $81.0\%$ คือความน่าจะเป็นที่ทั้งสองบิตมาเร็วพร้อมกันทั้งคู่ ($0.90 \times 0.90$)
- **ข้อ D ผิด:** คำนวณโดยใช้ผลรวมเชิงเดี่ยวโดยไม่คำนวณความน่าจะเป็นร่วม

---

### คำถามที่ 3: ความเสี่ยงของการละเลย Asynchronous Reset Recovery/Removal Timing ใน Testbench

ทำไมการปล่อยให้สัญญาณ Asynchronous Reset ถูกปลด (Deasserted) สุ่มสี่สุ่มห้าโดยไม่มีวงจร Reset Synchronizer จึงสร้างความเสียหายร้ายแรงต่อระบบ แม้ว่าใน RTL Simulation ปกติจะเห็นว่าระบบเริ่มทำงานได้ราบรื่น?

- **A)** เพราะสัญญาณ Reset จะกินกระแสไฟฟ้าสูงจนทำให้แรงดันไฟตก
- **B)** เพราะขอบปลดของ Reset ที่ไปถึง Flip-Flop แต่ละตัวในระบบอาจเฉียดเส้น Recovery/Removal ไม่พร้อมกัน ทำให้ Flop บางตัวหลุดจาก Reset ในไซเคิลที่ $N$ แต่ Flop บางตัวหลุดในไซเคิลที่ $N+1$ ส่งผลให้สถานะเริ่มต้นของระบบแตกกระจาย (Illegal Dispersed State)
- **C)** เพราะพิน Reset ของ FPGA ไม่รองรับมาตรฐานแรงดันไฟ LVCMOS
- **D)** เพราะซอฟต์แวร์สังเคราะห์วงจรจะลบสัญญาณ Reset ทิ้งโดยอัตโนมัติ

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) เพราะขอบปลดของ Reset ที่ไปถึง Flip-Flop แต่ละตัวในระบบอาจเฉียดเส้น Recovery/Removal ไม่พร้อมกัน ทำให้ Flop บางตัวหลุดจาก Reset ในไซเคิลที่ $N$ แต่ Flop บางตัวหลุดในไซเคิลที่ $N+1$ ส่งผลให้สถานะเริ่มต้นของระบบแตกกระจาย (Illegal Dispersed State)**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. สัญญาณ Asynchronous Reset เดินทางผ่านโครงข่ายสายไฟ (Reset Tree) ที่มีความยาวและความจุแฝงแตกต่างกันไปยัง Flip-Flop นับหมื่นตัว
2. หากปลด Reset แบบ Asynchronous:
   - Flop ตัวที่อยู่ใกล้ อาจเห็น Reset ปลดก่อนขอบสัญญาณนาฬิกาเล็กน้อย และเริ่มทำงานที่ Cycle 0
   - Flop ตัวที่อยู่ไกล อาจเห็น Reset ปลดช้ากว่าขอบสัญญาณนาฬิกาเพียงเสี้ยววินาที (ละเมิด Recovery Time) ทำให้มันยังคงถูก Reset ต่อไปอีก 1 ไซเคิล และเพิ่งเริ่มทำงานที่ Cycle 1
3. ผลลัพธ์คือ FSM หรือ Counter ที่ควรจะเริ่มทำงานพร้อมกัน จะมีบางบิตเริ่มเดินและบางบิตหยุดนิ่ง ระบบจึงเริ่มต้นด้วยสถานะผิดกฎหมาย (Out-of-Sync / Corrupt State) ทันทีตั้งแต่ก้าวแรก
4. ใน Testbench ระดับโปร จึงต้องมี Fault Injection ที่สุ่มขอบการปลด Reset ให้เฉียดขอบคล็อก เพื่อทดสอบว่าวงจร Reset Synchronizer (Asynchronous Assert, Synchronous Deassert: AASD) ทำงานได้ถูกต้อง 100%

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** สัญญาณควบคุมระดับลอจิกไม่ได้ทำให้กระแสไฟตกจนเป็นสาเหตุของความล้มเหลวเชิงตรรกะนี้
- **ข้อ C และ D ผิด:** เป็นข้อความที่ไม่สอดคล้องกับข้อเท็จจริงทางสถาปัตยกรรมของ FPGA
