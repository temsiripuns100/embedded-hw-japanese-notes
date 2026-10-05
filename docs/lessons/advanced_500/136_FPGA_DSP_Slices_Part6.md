# Lesson 136: FPGA DSP Slices Part 6 - Advanced Pipelining & Multi-Stage Retiming (高度なパイプライン化とリタイミング: Multi-Stage Balancing, Clock Jitter Budgets, Latency Equalization)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 งบประมาณเวลาและการวิเคราะห์ความผันผวนของสัญญาณนาฬิกาที่ความถี่สูงพิเศษ (Ultra-High-Frequency Timing & Jitter Budget)
เมื่อต้องออกแบบระบบประมวลผลสัญญาณดิจิทัลบน FPGA ที่ความถี่สูงระดับสากล ($f_{clk} \ge 700\text{ MHz} - 800\text{ MHz}$) คาบเวลาของสัญญาณนาฬิกาจะมีค่าแคบมากในระดับ sub-nanosecond เช่น ที่ความถี่ $750\text{ MHz}$:

$$T_{clk} = \frac{1}{750 \times 10^6\text{ Hz}} \approx 1.333\text{ ns} = 1,333\text{ ps}$$

ในหน้าต่างเวลาที่บีบคั้นนี้ วิศวกรไม่สามารถมองข้ามค่า **ความไม่แน่นอนของสัญญาณนาฬิกา (Clock Uncertainty: $T_{uncertainty}$)** ได้อีกต่อไป เนื่องจากผลรวมของความผันผวนของสัญญาณนาฬิกา (Clock Jitter) จาก PLL/MMCM และความคลาดเคลื่อนของโครงข่ายกระจายสัญญาณนาฬิกา (Clock Tree Distortion) จะกลืนกินเวลาว่างไปอย่างมหาศาล:

$$T_{uncertainty} = T_{jitter\_period} + T_{jitter\_phase} + T_{pll\_noise} + T_{clock\_tree\_skew}$$

ในเทคโนโลยีชิป 16nm FinFET ค่า $T_{uncertainty}$ ทั่วไปจะอยู่ที่ประมาณ $120 - 180\text{ ps}$ ซึ่งคิดเป็นสัดส่วนสูงถึง **$9 - 13.5\%$ ของคาบเวลาทั้งหมด**!

```
                งบประมาณเวลาที่ 750 MHz (Total Timing Budget = 1,333 ps)
   +-------------------------------------------------------------------------+
   | Clock Uncertainty (140 ps: 10.5%)                                       |
   +---------------------------------------+---------------------------------+
   | Flip-Flop t_co + t_su (280 ps: 21.0%) | Data Path Budget (913 ps: 68.5%)|
   +---------------------------------------+---------------------------------+
   
   ความหน่วงลอจิกรวมความหน่วงสายไฟ (Logic + Net) มีเวลาให้วิ่งเพียง 913 ps เท่านั้น!
   หากไม่มีการเปิดใช้งาน Pipeline ครบทุกสเตจใน DSP เส้นทางจะทะลุเกิน 1,333 ps ทันที!
```

---

### 1.2 สถาปัตยกรรมรีจิสเตอร์ของพอร์ตควบคุมแบบไดนามิก (Pipelining Dynamic Control Ports)
ข้อผิดพลาดระดับคลาสสิกที่พบในวิศวกรระดับกลางคือ: **"การใส่ใจเฉพาะการทำ Pipeline บนพอร์ตข้อมูล ($A, B, C, D$) แต่ลืมใส่ Pipeline บนพอร์ตควบคุมแบบไดนามิก (`OPMODE`, `ALUMODE`, `CARRYINSEL`, `INMODE`)"**

ในสถาปัตยกรรม DSP48E2 พอร์ตควบคุมเหล่านี้ทำหน้าที่สั่งการให้ ALU สลับการทำงานแบบ Cycle-by-Cycle (เช่น สลับระหว่างการคูณสะสม $P + M$ กับการส่งผ่านค่า $P$ หรือการลบ $P - M$):
* หากปล่อยให้พอร์ตควบคุมเชื่อมต่อตรงมาจาก Soft Fabric โดยไม่มีการ Register ภายใน:
  - ขาควบคุมจะต้องวิ่งผ่านเส้นทางยาวจาก Fabric เข้าสู่ Hard Macro
  - ความหน่วงเวลาของ Control Path ($t_{control} \approx 1.25\text{ ns}$) จะกลายเป็น **เส้นทางวิกฤตใหม่ (New Critical Path)** ที่ฉุดรั้งให้ $F_{max}$ ดิ่งลงต่ำกว่า $400\text{ MHz}$ ทันที!

```
              โครงสร้าง Control Pipeline ภายในเซลล์ DSP48E2
   
   Fabric Logic ---> [ OPMODEREG (Stage 1) ] ---> (OPMODE Decoders) ---> ALU MUX
   Fabric Logic ---> [ ALUMODEREG (Stage 1) ] ---> (ALUMODE Decoders) ---> 48-bit Adder/Sub
   Fabric Logic ---> [ INMODEREG (Stage 1) ] ---> (INMODE Decoders) ---> Pre-Adder
```

> [!IMPORTANT] กฎการ Sign-off ความเร็ว 750MHz+
> ต้องเปิดใช้งานแอตทริบิวต์ควบคุมรีจิสเตอร์ภายใน DSP48E2 ให้ครบทั้งระบบ:
> `OPMODEREG = 1`, `ALUMODEREG = 1`, `INMODEREG = 1`, และ `CARRYINSELREG = 1` เสมอ!

---

### 1.3 การจัดสมดุลความหน่วงหลายสเตจ (Multi-Stage Latency Equalization)
เมื่อเชื่อมต่อสเตตแมชชีนหรือบล็อกประมวลผลขนาดใหญ่เข้ากับแถวลำดับ DSP ที่มีความลึกของ Pipeline ไม่เท่ากัน ข้อมูลจากเส้นทางต่างๆ จะเดินทางมาถึงไม่พร้อมกัน เกิดปัญหา **เฟสเหลื่อมกัน (Latency Skew)**

หลักการทางคณิตศาสตร์ของการจัดสมดุลเวลา:

$$\text{Latency}(P_{path\_i}) = \text{Latency}(P_{path\_j}) \quad \forall i, j \in \text{Inputs}$$

หากเส้นทาง $A$ ผ่าน DSP ที่มี Pipeline รวม 4 สเตจ (`AREG=1, ADREG=1, MREG=1, PREG=1`) ในขณะที่เส้นทางสัญญาณควบคุมแฟล็ก $V$ เดินทางผ่าน Fabric ตรง:
* สัญญาณแฟล็ก $V$ จะต้องถูกหน่วงเวลาด้วย **Shift Register Delay Line (SRL32E)** เป็นจำนวน $4$ รอบสัญญาณนาฬิกาเต็ม เพื่อให้ผลลัพธ์ของข้อมูลและแฟล็กตรงรอบกันอย่างแม่นยำ (Cycle-Accurate Alignment)

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Full Control-Pipelined DSP48E2 Engine สำหรับความเร็ว 750MHz

```systemverilog
//=============================================================================
// Module: ultra_high_speed_dsp_core.sv
// Description: Fully Pipelined DSP48E2 with Dynamic Control Port Registration
// Target: AMD UltraScale+ -2 Speed Grade (Sign-off Target: 750MHz)
//=============================================================================
`timescale 1ns / 1ps

module ultra_high_speed_dsp_core #(
    parameter int A_W = 27,
    parameter int B_W = 18,
    parameter int C_W = 48
)(
    input  logic              clk,
    input  logic              rst_sync,
    input  logic              clk_en,
    // Dynamic Control Inputs
    input  logic [8:0]        opmode_in,   // ควบคุม W, X, Y, Z Mux
    input  logic [3:0]        alumode_in,  // ควบคุมฟังก์ชัน Add/Sub/Logic
    input  logic [4:0]        inmode_in,   // ควบคุม Pre-Adder gating
    // Data Inputs
    input  logic signed [A_W-1:0] a_data_in,
    input  logic signed [B_W-1:0] b_data_in,
    input  logic signed [C_W-1:0] c_data_in,
    // Data Output
    output logic signed [C_W-1:0] p_data_out
);

    //-------------------------------------------------------------------------
    // 1. Control Pipeline Registers (OPMODEREG, ALUMODEREG, INMODEREG)
    // ต้อง Register ควบคู่ไปกับ Data Registers เพื่อรักษา Timing Isolation
    //-------------------------------------------------------------------------
    logic [8:0] opmode_pipe1, opmode_pipe2;
    logic [3:0] alumode_pipe1, alumode_pipe2;
    logic [4:0] inmode_pipe1;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            opmode_pipe1  <= '0;
            opmode_pipe2  <= '0;
            alumode_pipe1 <= '0;
            alumode_pipe2 <= '0;
            inmode_pipe1  <= '0;
        end else if (clk_en) begin
            opmode_pipe1  <= opmode_in;
            opmode_pipe2  <= opmode_pipe1;  // สเตจที่ 2 ให้ตรงกับ MREG
            alumode_pipe1 <= alumode_in;
            alumode_pipe2 <= alumode_pipe1; // สเตจที่ 2 ให้ตรงกับ MREG
            inmode_pipe1  <= inmode_in;     // สเตจที่ 1 ให้ตรงกับ AREG
        end
    end

    //-------------------------------------------------------------------------
    // 2. Data Pipeline Registers (AREG, BREG, CREG, MREG, PREG)
    //-------------------------------------------------------------------------
    (* use_dsp = "yes" *)
    logic signed [A_W-1:0] a_pipe1;
    logic signed [B_W-1:0] b_pipe1;
    logic signed [C_W-1:0] c_pipe1, c_pipe2;
    logic signed [44:0]    m_pipe;
    logic signed [C_W-1:0] p_pipe;

    // Data Stage 1: Input Registers (AREG=1, BREG=1, CREG=1)
    always_ff @(posedge clk) begin
        if (rst_sync) begin
            a_pipe1 <= '0;
            b_pipe1 <= '0;
            c_pipe1 <= '0;
        end else if (clk_en) begin
            a_pipe1 <= a_data_in;
            b_pipe1 <= b_data_in;
            c_pipe1 <= c_data_in;
        end
    end

    // Data Stage 2: Multiplier Register (MREG=1)
    always_ff @(posedge clk) begin
        if (rst_sync) begin
            m_pipe  <= '0;
            c_pipe2 <= '0;
        end else if (clk_en) begin
            m_pipe  <= a_pipe1 * b_pipe1;
            c_pipe2 <= c_pipe1;
        end
    end

    // Data Stage 3: ALU Accumulator Register (PREG=1)
    always_ff @(posedge clk) begin
        if (rst_sync) begin
            p_pipe <= '0;
        end else if (clk_en) begin
            // ตัวอย่างการทำงานอิงตาม dynamic opmode และ alumode
            if (alumode_pipe2 == 4'b0000) begin
                p_pipe <= m_pipe + c_pipe2; // โหมดบวกสะสม
            end else begin
                p_pipe <= m_pipe - c_pipe2; // โหมดลบ
            end
        end
    end

    assign p_data_out = p_pipe;

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในโครงการพัฒนาโมดูลตัวแปลงความถี่ดิจิทัลลง (Digital Down Converter: DDC) สำหรับเครื่องรับสัญญาณดาวเทียมความเร็วสูงบนชิป Kintex UltraScale+ FPGA กำหนดความถี่สัญญาณนาฬิกา $f_{clk} = 800\text{ MHz}$ ($T_{clk} = 1.250\text{ ns}$) วิศวกรออกแบบวงจรคูณสะสมที่สลับโหมดการทำงานระหว่าง I/Q Channel ด้วยสัญญาณควบคุม `opmode` และ `alumode` แบบไดนามิก โดยเปิดใช้คำสั่ง Auto-Retiming ของ Vivado (`synth_design -retiming`) เพื่อให้เครื่องมือช่วยปรับสมดุล

**ผลลัพธ์ที่ล้มเหลว:** รายงาน Vivado STA แจ้งเตือนความล้มเหลวรุนแรง: $WNS = -0.540\text{ ns}$ เมื่อตรวจสอบ Critical Path พบว่า เส้นทางข้อมูล ($A, B \rightarrow M \rightarrow P$) ปิดเวลาผ่านฉลุย แต่เส้นทางวิกฤตที่ติดลบคือ **สายสัญญาณควบคุม `opmode` จากโมดูล FSM ภายนอก วิ่งทะลุเข้าขา MUX ภายใน DSP48E2** โดยไม่มี Register กั้น ทำให้ความหน่วงของเส้นทางยาวถึง $1.650\text{ ns}$ ส่งผลให้ DDC คำนวณเฟสผิดเพี้ยนและสูญเสียการล็อกสัญญาณ (Loss of Carrier Lock)

```
                 สาเหตุความล้มเหลวจากการไม่ใส่ Control Pipeline
   
   FSM Controller (Soft Fabric)
   [ FSM State Reg ]
          |
          | สายไฟ Fabric ลากข้าม 3 คอลัมน์ (Delay = 1.15 ns!)
          v
   +-------------------------------------------------------------+
   | Hard Macro DSP48E2                                          |
   |   Data Path: [AREG] -> [MREG] -> [PREG] (Timing ผ่านฉลุย!)  |
   |                                                             |
   |   Control Path: opmode_in ----> [ ALU MUX ] (ไม่มี OPMODEREG!)|
   |   <--------------- Total Delay = 1.65 ns ------------------> |
   +-------------------------------------------------------------+
   
   ผลลัพธ์: คาบเวลา 1.25ns แต่ Control Path ยาว 1.65ns -> WNS ติดลบ -0.54ns!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมเครื่องรับสัญญาณดาวเทียมถึงสูญเสียการล็อกสัญญาณพาหะ (Carrier Lock)?**
   * *ตอบ:* วงจร DDC คำนวณค่าสัญญาณ I/Q สลับแชนเนลผิดพลาดและเกิดข้อมูลขยะเป็นระยะ
2. **ทำไมวงจร DDC ถึงคำนวณค่าสลับแชนเนลผิดพลาด?**
   * *ตอบ:* สัญญาณควบคุมสลับโหมด `opmode` เดินทางมาถึงบล็อก ALU ของ DSP ช้ากว่าขอบสัญญาณนาฬิกา
3. **ทำไมสัญญาณควบคุม `opmode` ถึงเดินทางมาถึงช้าเกินไป?**
   * *ตอบ:* เส้นทางสัญญาณควบคุมจาก FSM ไปยัง ALU เกิด Setup Time Violation ขนาด $-0.540\text{ ns}$
4. **ทำไมเส้นทางสัญญาณควบคุมถึงติดลบในขณะที่เส้นทางข้อมูลผ่านได้?**
   * *ตอบ:* เส้นทางข้อมูลมี `AREG, MREG, PREG` กั้นอย่างสมบูรณ์ แต่พอร์ตควบคุม `opmode` ไม่มีรีจิสเตอร์กั้นภายใน
5. **ทำไมวิศวกรถึงไม่ได้ใส่ Register บนพอร์ตควบคุม?**
   * *ตอบ:* วิศวกรเข้าใจผิดคิดว่าคำสั่ง `-retiming` ของ Vivado จะทำการสร้างและย้ายรีจิสเตอร์บนขาควบคุมให้โดยอัตโนมัติ โดยไม่รู้ว่า **Auto-Retiming ไม่สามารถสร้างรีจิสเตอร์ใหม่บนพอร์ตควบคุมของ Hard Macro ได้**!

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ DDC Control Path
   
   ความเข้าใจในเครื่องมือ (Tool Optimization)     การออกแบบสถาปัตยกรรม RTL (RTL Architecture)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   พึ่งพาคำสั่ง    เข้าใจผิดว่า                   ลืมใส่ Register ไม่ได้เปิดใช้
   Auto-Retiming Tool จะดูด                     บนสาย Dynamic  OPMODEREG = 1
   มากเกินไป     Control เข้า DSP               Control Ports  ในสเปก DSP
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> WNS ติดลบ -0.54ns
                                                                |     DDC หลุดการล็อก
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   เป้าหมายความถี่ สายไฟจาก FSM                  ไม่ได้ดู       ขาดการตรวจ
   สูงถึง 800MHz  ลากข้ามคอลัมน์                Report Timing  Control Path
   (T_clk = 1.25ns) มีความหน่วงสูง               อย่างละเอียด   ในรายงาน STA
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   ความเร็วระดับวิกฤต (Extreme Frequency)         ขั้นตอนการตรวจสอบเวลา (Timing Verification)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ตรวจสอบสถานะของ Control Registers ในรายงาน Synthesis
เปิดไฟล์ `runme.log` และตรวจสอบคุณสมบัติของคอนฟิกกูเรชัน DSP:
```text
DSP48E2 Attributes:
  AREG: 1, BREG: 1, MREG: 1, PREG: 1
  OPMODEREG: 1  <--- ต้องเป็น 1 เท่านั้น! (ห้ามเป็น 0 เด็ดขาด)
  ALUMODEREG: 1 <--- ต้องเป็น 1 เท่านั้น!
  INMODEREG: 1  <--- ต้องเป็น 1 เท่านั้น!
```

#### ขั้นตอนที่ 2: เขียน Pipeline บนพอร์ตควบคุมในระดับ RTL ให้ตรงกับ Data Path
```systemverilog
// กฎเหล็กสำหรับการควบคุม DSP ที่ความเร็ว 700MHz+
always_ff @(posedge clk) begin
    opmode_reg1 <= opmode_raw;
    opmode_reg2 <= opmode_reg1; // 2 สเตจให้ตรงกับความลึกของ Data Path
end
```

#### ขั้นตอนที่ 3: ตรวจสอบ Setup Slack บนพอร์ตควบคุมด้วยคำสั่ง Tcl
```tcl
report_timing -to [get_pins -hier *dsp*/*OPMODE*] -max_paths 10 -sort_by slack
```
ค่า Slack ต้องมีค่าเป็นบวก ($WNS \ge +0.050\text{ ns}$) ในทุก Process Corner

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| 制御ポートパイプライン | せいぎょぽーとぱいぷらいん | Seigyo Pooto Paipurain | Control Port Pipelining |
| 動的動作モード | どうてきどうさもーど | Douteki Dousa Moodo | Dynamic Operating Mode (`OPMODE`) |
| クロック不確かさ | くろっくふたしかさ | Kurokku Futashikasa | Clock Uncertainty ($T_{uncertainty}$) |
| レイテンシ整合 | れいてんしせいごう | Reitenshi Seigou | Latency Equalization / Balancing |
| 位相同期外れ | いそうどうきはずれ | Isou Douki Hazure | Loss of Phase / Carrier Lock |
| 自動リタイミング限界 | じどうりたいみんぐげんかい | Jidou Ritaimingu Genkai | Auto-Retiming Limitation |
| ハードマクロ境界遅延 | はーどまくろきょうかいちえん | Haado Makuro Kyoukai Chien | Hard Macro Boundary Delay |
| ジッター予算 | じったーよさん | Jittaa Yosan | Jitter Budget |
| 信号整合性保証 | しんごうせいごうせいほしょう | Shingou Seigousei Hoshou | Signal Integrity Assurance |
| シフトレジスタ遅延補償 | しふとれじすたちえんほしょう | Shifuto Rejisuta Chien Hoshou | Shift Register Delay Compensation (SRL) |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** ศูนย์วิจัยเทคโนโลยีอวกาศและการสื่อสารผ่านดาวเทียม (Satellite Communications DSP Lab)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** ทาคาฮาชิ ซัง (Takahashi-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** โนมุระ คุง (Nomura-kun)

---

**高橋技師 (Takahashi):**  
「野村君、この衛星受信機用 DDC モジュールの 800MHz タイミング検証結果だが、データパスのスラックは出ているのに、`OPMODE` 制御ピンへのパスで WNS が $-0.540\text{ ns}$ もショートしているぞ。合成オプションの自動リタイミング（`-retiming`）を過信して、動的制御ポートのパイプライン化をサボったのではないかね？」  
*(Nomura-kun, kono eisei jushinki-you DDC mojyuuru no 800MHz taimingu kenshou kekka dakedo, deetapasu no surakku wa dete iru no ni, `OPMODE` seigyo pin e no pasu de WNS ga $-0.540\text{ ns}$ mo shooto shite iru zo. Gousei opushon no jidou ritaimingu (`-retiming`) wo kashin shite, douteki seigyo pooto no paipurain-ka wo sabotta no dewa nai kane?)*  
**ความหมาย:** คุณโนมุระ ผลการตรวจเวลา 800MHz ของโมดูล DDC สำหรับดาวเทียมตัวนี้ ทั้งที่เส้นทางข้อมูลมี Slack ผ่านฉลุย แต่เส้นทางที่วิ่งเข้าขาควบคุม `OPMODE` กลับติดลบไปถึง $-0.540\text{ ns}$ เลยนะ มัวแต่ไปหลงเชื่อออปชัน Auto-Retiming ของโปรแกรมคอมไพล์ จนแอบอู้งานไม่ยอมทำ Pipeline ให้กับพอร์ตควบคุมแบบไดนามิกใช่ไหมครับ?

---

**野村技師 (Nomura):**  
「はい、高橋さん。Vivado の `-retiming` オプションを有効化しておけば、ツールがクリティカルパスを検知して、制御信号のフリップフロップも最適な段数へ自動的に再配置（Rebalance）してくれるものと思い込んでおりました。データパス側ばかりに気を取られておりました。」  
*(Hai, Takahashi-san. Vivado no `-retiming` opushon wo yuukouka shite okeba, tsuuru ga kuritikaru pasu wo kenchi shite, seigyo shingou no furippufuroppu mo tekisetsu na dansuu e jidouteki ni sai-haichi (Rebalance) shite kureru mono to omoikonde orimashita. Deetapasu-gawa bakari ni ki wo torawarete orimashita.)*  
**ความหมาย:** ครับคุณทาคาฮาชิ ผมเข้าใจไปเองว่าถ้าเปิดออปชัน `-retiming` ของ Vivado ไว้ ตัวโปรแกรมจะตรวจจับ Critical Path แล้วย้ายตำแหน่งของ Flip-Flop ฝั่งสัญญาณควบคุมให้สมดุลได้เองโดยอัตโนมัติครับ ผมเลยมัวแต่ไปสนใจเฉพาะฝั่ง Data Path ครับ

---

**高橋技師 (Takahashi):**  
「甘い！自動リタイミングは既存のレジスタを移動させるだけであって、ハードマクロの内部に存在しないレジスタを勝手に新設してくれる魔法の杖ではない！DSP48E2 の内部には `OPMODEREG` や `ALUMODEREG` という専用の制御パイプラインスロットが用意されているのに、君が RTL でそれらを記述（Infer）しなければ、外部のスライスから裸の組み合わせ回路がダイレクトに突っ込まれることになるんだ！クロック周期がわずか 1.25ns（800MHz）の世界で、1.6ns もかかる制御パスを通せば破綻するのは当たり前だ！**重大指摘事項とする！** 直ちに RTL 上で制御ポートに 2 段の同期パイプラインを追加し、`OPMODEREG = 1` を達成して 800MHz をクローズさせなさい！」  
*(Amai! Jidou ritaimingu wa kizon no rejisuta wo idou saseru dake de atte, haado makuro no naibu ni sonzai shinai rejisuta wo katte ni shinsetsu shite kureru mahou no tsue dewa nai! DSP48E2 no naibu ni wa `OPMODEREG` ya `ALUMODEREG` to iu sen-you no seigyo paipurain surotto ga youi sarete iru no ni, kimi ga RTL de sorera wo kijutsu (Infer) shinakereba, gaibu no suraisu kara hadaka no kumiawase kairo ga dairekuto ni tsukkomareru koto ni narunda! Kurokku shuuki ga wazuka 1.25ns (800MHz) no sekai de, 1.6ns mo kakaru seigyo pasu wo tooseba hatan suru no wa atarimae da! **Juudai shiteki jikou to suru!** Tadachini RTL jou de seigyo pooto ni nidan no douki paipurain wo tsuika shi, `OPMODEREG = 1` wo tassei shite 800MHz wo kuroozu sasenasai!)*  
**ความหมาย:** ประมาทเกินไปแล้ว! Auto-Retiming มันทำได้แค่ย้ายตำแหน่ง Register ที่มีอยู่เดิม แต่มันไม่ใช่ไม้กายสิทธิ์ที่จะมาแอบเสกสร้าง Register ใหม่ภายใน Hard Macro ให้เรานะ! ใน DSP48E2 มันมีสล็อต Dedicated Control Pipeline อย่าง `OPMODEREG` และ `ALUMODEREG` เตรียมไว้ให้อยู่แล้ว แต่ถ้าเธอไม่เขียน RTL ให้มันดูดซับเข้าไป ลอจิกคอมบิเนชันเปลือยๆ จาก Slice ภายนอกก็จะพุ่งตรงเข้ามาชนขาข้างในโดยไม่มีอะไรกั้น! ในโลกที่คาบเวลาสั้นเพียง 1.25ns (800MHz) การมี Control Path ยาวถึง 1.6ns มันจะไม่พังได้อย่างไร! **ผมสั่งเป็นข้อแก้ไขระดับวิกฤต!** จงรีบเติม Synchronous Pipeline 2 สเตจบนพอร์ตควบคุมใน RTL เพื่อให้เกิด `OPMODEREG = 1` และปิด Timing ที่ 800MHz ให้ผ่านเดี๋ยวนี้!

---

**野村技師 (Nomura):**  
「制御ポート専用のハードパイプラインレジスタの重要性を完全に失念しておりました…！ツールの自動化に頼らず、RTL で明示的に制御パイプラインを記述いたします。直ちに 800MHz で全パスのスラックがプラスになることを実証して再提出いたします！」  
*(Seigyo pooto sen-you no haado paipurain rejisuta no juuyousei wo kanzen ni shitsunen shite orimashita...! Tsuuru no jidouka ni tayorazu, RTL de meijiteki ni seigyo paipurain wo kijutsu itashimasu. Tadachini 800MHz de zen-pasu no surakku ga purasu ni naru koto wo jisshou shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ผมมองข้ามความสำคัญของ Hard Pipeline Register บนพอร์ตควบคุมไปอย่างสิ้นเชิงเลยครับ...! ผมจะไม่พึ่งพาการเดาของ Tool อีกแล้ว จะเขียน Pipelining บนสายควบคุมใน RTL อย่างชัดเจนด้วยตัวเอง และพิสูจน์ให้เห็นว่าค่า Slack ทุกเส้นทางเป็นบวกที่ 800MHz แล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณงบประมาณเวลาสูงสุดที่ยอมรับได้ (Data Path Budget) ที่ความถี่ 750 MHz

ในระบบประมวลผลเรดาร์ความเร็วสูงที่ทำงานบนชิป UltraScale+ (Speed Grade -2) ที่ความถี่สัญญาณนาฬิกา $f_{clk} = 750\text{ MHz}$ ($T_{clk} = 1.333\text{ ns}$):
* Flip-Flop Clock-to-Q delay ภายในเซลล์ DSP: $t_{co} = 0.220\text{ ns}$
* Flip-Flop Setup time ภายในเซลล์ DSP: $t_{su} = 0.080\text{ ns}$
* Phase Jitter ของ MMCM: $T_{jitter} = 0.065\text{ ns}$
* Clock Tree Skew และ Distortion รวม: $T_{skew\_dist} = 0.075\text{ ns}$
* กำหนดให้ต้องการรักษาค่าความปลอดภัยขั้นต่ำ (Design Setup Margin): $S_{margin} = 0.050\text{ ns}$

จงคำนวณหาค่าความหน่วงเวลารวมสูงสุดที่ยอมรับได้ของลอจิกและสายไฟ (Maximum Allowable Data Path Delay: $t_{logic} + t_{net}$) ในหน่วย **พิโกวินาที (ps)**?

---

#### ตัวเลือก:
A) $743\text{ ps}$  
B) $843\text{ ps}$  
C) $913\text{ ps}$  
D) $1,033\text{ ps}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) $843\text{ ps}$**

##### ขั้นตอนที่ 1: คำนวณ Clock Uncertainty รวม ($T_{unc}$)
$$T_{unc} = T_{jitter} + T_{skew\_dist} = 0.065\text{ ns} + 0.075\text{ ns} = 0.140\text{ ns} = 140\text{ ps}$$

##### ขั้นตอนที่ 2: ตั้งสมการ Setup Slack
สมการ Setup Slack:
$$S_{setup} = T_{clk} - (t_{co} + T_{data\_path} + t_{su} + T_{unc})$$
เพื่อให้ได้ Margin ตามเป้าหมาย ($S_{setup} \ge S_{margin}$):
$$T_{data\_path} \le T_{clk} - t_{co} - t_{su} - T_{unc} - S_{margin}$$

##### ขั้นตอนที่ 3: แทนค่าตัวเลขในหน่วยพิโกวินาที (ps)
* $T_{clk} = 1,333\text{ ps}$
* $t_{co} = 220\text{ ps}$
* $t_{su} = 80\text{ ps}$
* $T_{unc} = 140\text{ ps}$
* $S_{margin} = 50\text{ ps}$

$$T_{data\_path} \le 1,333 - 220 - 80 - 140 - 50 = 1,333 - 490 = 843\text{ ps}$$

ดังนั้น เส้นทางของลอจิกและสายสัญญาณ (ทั้ง $t_{logic} + t_{net}$) จะต้องมีความหน่วงเวลารวมกันไม่เกิน **$843\text{ ps}$** เท่านั้น! หากลืมเปิดใช้งาน `MREG` หรือ `OPMODEREG` ความหน่วงจะพุ่งเกิน $1,200\text{ ps}$ และทำให้ระบบล้มเหลวทันที

---

### คำถามที่ 2: การจัดสมดุลความหน่วงของเส้นทาง I/Q Demodulator

ในระบบประมวลผลสัญญาณแถบความถี่เบสแบนด์ (I/Q Demodulator):
* สัญญาณแชนเนล **In-Phase (I)** เดินทางผ่านตัวคูณสะสม DSP48E2 ที่เปิดใช้ Pipeline เต็มรูปแบบ 4 สเตจ (`AREG=1, ADREG=1, MREG=1, PREG=1`)
* สัญญาณแชนเนล **Quadrature (Q)** เดินทางผ่านตัวกรอง FIR ที่เปิดใช้ Pipeline รวม 6 สเตจ
* เพื่อนำสัญญาณทั้งสองแชนเนลมาคำนวณขนาดเวกเตอร์ $\sqrt{I^2 + Q^2}$ ในโมดูล CORDIC ถัดไป

วิศวกรจะต้องใส่ Shift Register (SRL) หน่วงเวลาชดเชยที่เส้นทางใด และเป็นจำนวนกี่รอบสัญญาณนาฬิกา?

---

#### ตัวเลือก:
A) หน่วงเส้นทาง Q เพิ่มอีก 2 รอบ  
B) หน่วงเส้นทาง I เพิ่มอีก 2 รอบ  
C) หน่วงเส้นทาง I เพิ่มอีก 4 รอบ  
D) ไม่ต้องหน่วง เพราะ CORDIC รองรับสัญญาณที่ไม่ตรงเฟสกันได้

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) หน่วงเส้นทาง I เพิ่มอีก 2 รอบ**

##### การวิเคราะห์ความล่าช้า (Latency Balancing Analysis):
* เส้นทาง Q มีความล่าช้า: $\text{Latency}_Q = 6 \text{ รอบสัญญาณนาฬิกา}$
* เส้นทาง I มีความล่าช้า: $\text{Latency}_I = 4 \text{ รอบสัญญาณนาฬิกา}$
ความเหลื่อมล้ำทางเวลา (Latency Skew):
$$\Delta \text{Latency} = \text{Latency}_Q - \text{Latency}_I = 6 - 4 = 2 \text{ รอบสัญญาณนาฬิกา}$$

เนื่องจากสัญญาณแชนเนล I เดินทางมาถึงเร็วกว่าสัญญาณ Q อยู่ 2 รอบ สัญญาณ I จึงต้องถูกหน่วงเวลาเพิ่มเติมด้วย **SRL จำนวน 2 สเตจ** เพื่อให้ตัวอย่าง $I[n]$ และ $Q[n]$ จากเวลาเดียวกันเข้าสู่โมดูล CORDIC ในรอบสัญญาณนาฬิกาเดียวกันพอดี

---

### คำถามที่ 3: ข้อใดอธิบายพฤติกรรมของคำสั่ง `synth_design -retiming` ต่อบล็อก DSP48E2 ได้ถูกต้องที่สุด?

---

#### ตัวเลือก:
A) Auto-Retiming สามารถย้าย Register ที่อยู่นอก DSP เข้าไปบรรจุในสล็อตที่ว่างอยู่ของ DSP (`AREG`, `MREG`, `PREG`) ได้ ตราบใดที่สัญญาณนาฬิกา, สัญญาณรีเซ็ต, และ Clock Enable มีพฤติกรรมทางตรรกะตรงกันทุกประการ  
B) Auto-Retiming จะแปลงบล็อก DSP ให้กลายเป็นเกต NAND อัตโนมัติ  
C) Auto-Retiming สามารถสร้าง Register ขึ้นมาใหม่บนขา OPMODE ได้เองโดยไม่ต้องมี Register เดิมใน RTL  
D) Auto-Retiming ไม่สามารถทำงานร่วมกับบล็อก DSP ได้เลยในทุกกรณี

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) Auto-Retiming สามารถย้าย Register ที่อยู่นอก DSP เข้าไปบรรจุในสล็อตที่ว่างอยู่ของ DSP (`AREG`, `MREG`, `PREG`) ได้ ตราบใดที่สัญญาณนาฬิกา, สัญญาณรีเซ็ต, และ Clock Enable มีพฤติกรรมทางตรรกะตรงกันทุกประการ**

##### หลักการทำงานของ Vivado Retiming Engine:
เครื่องมือสังเคราะห์วงจรจะทำการวิเคราะห์กราฟการเชื่อมต่อ และสามารถ "ดึง (Absorb / Retime)" รีจิสเตอร์ที่วิศวกรประกาศไว้บน Fabric ให้เลื่อนเข้าไปอยู่ในสล็อต Hard Register ของเซลล์ DSP ได้ แต่มีเงื่อนไขเหล็กว่า:
1. ต้องมีรีจิสเตอร์เดิมอยู่ใน RTL อยู่แล้ว (Retiming ย้ายได้แต่เสกเพิ่มไม่ได้)
2. สัญญาณควบคุม (`Clock`, `Reset`, `Enable`) ต้องตรงกัน 100%
3. ต้องเป็น Synchronous Reset เท่านั้น
หากเงื่อนไขเหล่านี้ผ่าน Vivado จะสามารถดึง Register เข้าสู่สล็อต `MREG` หรือ `PREG` ได้อย่างสมบูรณ์แบบ
