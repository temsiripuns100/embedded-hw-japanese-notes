# Lesson 127: FPGA State Machine Part 7 - Glitch Minimization & Output Registering (グリッチの最小化と出力レジスタ化: Hazard-Free Moore/Mealy & Look-Ahead Output Architecture)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ฟิสิกส์ของการเกิดสัญญาณรบกวนชั่วขณะ (Physics of Combinational Hazards & Glitches)
ในวงจรตรรกะคอมบิเนชัน (Combinational Logic) สัญญาณอินพุตแต่ละสายจะเดินทางผ่านเส้นทางที่มีความยาวและจำนวนเกตไม่เท่ากัน ทำให้เกิด **ความหน่วงเวลาที่ไม่สมมาตร (Path Delay Skew)** ปรากฏการณ์นี้ส่งผลให้เอาต์พุตของลอจิกเกิดการกระเพื่อมสวิงชั่วขณะก่อนที่จะเข้าสู่สถานะคงตัว เราเรียกการกระเพื่อมนี้ว่า **กลิตช์ (Glitch)** หรือ **สภาวะอันตราย (Hazard)**

```
                      การเกิด Static-1 Hazard ในลอจิกสองระดับ
   
   สมการ: F = (A · /B) + (B · C)   เมื่อกำหนดให้ A = 1, C = 1 และ B เปลี่ยนค่าจาก 1 -> 0
   
   B           ¯¯¯¯¯¯¯¯¯¯¯¯¯¯\_______________________ (ขอบขาลง)
   /B (Invert) _______________/¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ (หน่วงเวลา t_inv)
   
   Term 1 (B·C)¯¯¯¯¯¯¯¯¯¯¯¯¯¯\_______________________ (ตกทันที)
   Term 2(A·/B)_______________/¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ (ขึ้นช้าไป t_inv)
   
   Output F    ¯¯¯¯¯¯¯¯¯¯¯¯¯¯\_/¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ (STATIC-1 HAZARD SPIKE!)
                              | |
                              <-t_w-> (ร่วงลง 0 ชั่วขณะกว้าง t_w = t_inv)
```

#### 1.1.1 การจำแนกประเภทของ Hazard ในวงจรดิจิทัล
1. **Static-1 Hazard:** สภาวะที่เอาต์พุตควรจะมีค่าคงที่อยู่ที่ระดับสูง ('1') ตลอดเวลา แต่กลับตกวูบลงสู่ระดับต่ำ ('0') ชั่วขณะ
2. **Static-0 Hazard:** สภาวะที่เอาต์พุตควรจะมีค่าคงที่อยู่ที่ระดับต่ำ ('0') ตลอดเวลา แต่กลับมีพัลส์แหลมพุ่งขึ้นสู่ระดับสูง ('1') ชั่วขณะ
3. **Dynamic Hazard:** สภาวะที่เอาต์พุตกำลังเปลี่ยนผ่านระหว่าง 0 ไป 1 (หรือ 1 ไป 0) แต่กลับเกิดการสวิงกลับไปกลับมาหลายครั้ง ($0 \rightarrow 1 \rightarrow 0 \rightarrow 1$) ก่อนจะนิ่ง

#### 1.1.2 ทฤษฎีบทการใส่เทอมพ้อง (Karnaugh Consensus Theorem)
ในทางทฤษฎีบูลีนแบบคลาสสิก เราสามารถกำจัด Static-1 Hazard ได้โดยการเพิ่ม **เทอมพ้อง (Consensus Term)** ที่ครอบคลุมรอยต่อระหว่างกลุ่มมินเทอมใน K-Map:

$$F_{hazard\_free} = A \bar{B} + B C + A C$$

เทอม $AC$ จะทำหน้าที่ค้ำยันให้เอาต์พุต $F = 1$ ตลอดช่วงเวลาที่สัญญาณ $B$ กำลังเปลี่ยนสถานะ!

> [!WARNING] กับดักร้ายกาจของ EDA Synthesis Tools ในปัจจุบัน
> ในกระบวนการสังเคราะห์วงจรระดับลึก (FPGA Logic Optimization) คอมไพเลอร์อย่าง Vivado หรือ Quartus ถูกตั้งโปรแกรมมาให้ **"ลดทอนพื้นที่ลอจิกให้เหลือน้อยที่สุด (Minimize Logic Area)"**  
> เครื่องมือจะมองว่าเทอม $AC$ เป็น **"เทอมที่ซ้ำซ้อนไร้ประโยชน์ (Redundant Logic)"** และจะ **ทำการตัดทิ้ง (Prune)** โดยอัตโนมัติ! ส่งผลให้วงจรฮาร์ดแวร์จริงบนชิปกลับมามี Hazard และเกิด Glitch เช่นเดิม!

---

### 1.2 สถาปัตยกรรมการกำจัด Glitch แบบสมบูรณ์ด้วยการ Register เอาต์พุต (Registered Output Topologies)

หนทางเดียวที่เชื่อถือได้ $100\%$ ในระดับฟิสิกส์ฮาร์ดแวร์เพื่อรับประกันว่าเอาต์พุตจะปราศจาก Glitch (Hazard-Free Clean Waveform) คือ **การส่งสัญญาณเอาต์พุตผ่าน D-Flip-Flop เสมอ** โดยมี 3 สถาปัตยกรรมหลักดังนี้:

```
+------------------------------------+---------------------------------------------------------------+
| สถาปัตยกรรม                        | ลักษณะการทำงานและผลกระทบ (Characteristics & Trade-offs)       |
+------------------------------------+---------------------------------------------------------------+
| 1. Pure Combinational Output       | ห้ามใช้ในงานควบคุมเด็ดขาด! เสี่ยง Glitch สูงมาก                |
| 2. Pipelined Moore Output          | สะอาด ปราศจาก Glitch แต่เพิ่ม Latency 1 รอบสัญญาณนาฬิกา       |
| 3. Look-Ahead Registered Output    | สะอาด ปราศจาก Glitch และให้ค่าตรงกับไซเคิลที่ต้องการ (0 Latency)|
| 4. State-Bit Output Embedding      | ฝังค่าเอาต์พุตไว้ในบิตของ State Register โดยตรง (เร็วสุด)     |
+------------------------------------+---------------------------------------------------------------+
```

#### 1.2.1 Look-Ahead Registered Output Architecture
ประเมินเอาต์พุตล่วงหน้าโดยใช้ฟังก์ชัน $\lambda_{lookahead}(\mathbf{S}(t), \mathbf{X}(t))$ เพื่อส่งเข้า D-Flip-Flop ในขอบสัญญาณนาฬิกาเดียวกันกับการเปลี่ยนสถานะ ทำให้เอาต์พุตจริงที่ขอบถัดไปมีค่าถูกต้องตรงตามความต้องการโดยปราศจาก Glitch:

```
               สถาปัตยกรรม Look-Ahead Registered Output
   Inputs X ----+--->[ Next-State Logic ]-----> D         Q ----+---> State S(t)
                |                               |State Reg|     |
                |                      CLK ---->|>        |     |
                |                               +---------+     |
                +-------------------------------------------+   |
                |                                           |   |
                v                                           v   v
            [ Look-Ahead Output Logic ]---------------> D         Q ----> Clean Registered
            [  lambda_lookahead(S, X) ]                 |OutputReg|       Outputs Y_reg
                                               CLK ---->|>        |       (ZERO GLITCH!)
                                                        +---------+
```

#### 1.2.2 เทคนิค State-Bit Output Embedding (การฝังเอาต์พุตในบิตสถานะ)
หาก FSM มีสัญญาณเอาต์พุตที่สำคัญมาก $k$ สัญญาณ เราสามารถจัดโครงสร้างเวกเตอร์สถานะให้อินพุตของ State Register มีบิตเอาต์พุตเหล่านั้นฝังอยู่โดยตรง (Embedded Bits):

$$\mathbf{S}_{vector} = [\mathbf{Y}_{embedded} \mid \mathbf{S}_{internal}]$$

* **ข้อได้เปรียบ:** สัญญาณเอาต์พุตจะถูกดึงออกมาจากขา $Q$ ของ State Register โดยตรงโดยไม่ต้องผ่าน LUT ถอดรหัสแม้แต่ตัวเดียว ($t_{decode} = 0.000\text{ ns}$)! ขจัดปัญหา Glitch ได้อย่างเด็ดขาดและได้ $F_{max}$ สูงสุด

---

### 1.3 โค้ดตัวอย่าง SystemVerilog: Look-Ahead Registered vs State-Bit Embedded FSM

```systemverilog
//=============================================================================
// Module: hazard_free_adc_controller.sv
// Description: Glitch-Free FSM Controller for High-Precision 16-bit SAR ADC
// Architecture: Look-Ahead Registered Output & Embedded State Bits
//=============================================================================
`timescale 1ns / 1ps

module hazard_free_adc_controller (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        sample_trigger,
    input  logic        adc_busy_n,
    // สัญญาณควบคุม ADC ภายนอก (ต้องปราศจาก Glitch 100%)
    output logic        adc_convst,      // Conversion Start Pulse
    output logic        adc_sclk_gate,   // Gated SPI Clock Enable
    output logic        data_capture_en, // FIFO Write Enable
    output logic [1:0]  dbg_state
);

    //-------------------------------------------------------------------------
    // วิธีที่ 1: Look-Ahead Registered Architecture
    //-------------------------------------------------------------------------
    typedef enum logic [1:0] {
        ST_IDLE    = 2'b00,
        ST_CONVERT = 2'b01,
        ST_READ    = 2'b10,
        ST_DONE    = 2'b11
    } state_t;

    state_t current_state, next_state;

    // Look-Ahead Next Signals
    logic adc_convst_nxt;
    logic adc_sclk_gate_nxt;
    logic data_capture_en_nxt;

    // State Register
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            current_state <= ST_IDLE;
        end else begin
            current_state <= next_state;
        end
    end

    // Next-State Logic
    always_comb begin
        next_state = current_state;

        case (current_state)
            ST_IDLE: begin
                if (sample_trigger) begin
                    next_state = ST_CONVERT;
                end
            end

            ST_CONVERT: begin
                if (adc_busy_n) begin // ADC เสร็จสิ้นการแปลงสัญญาณ
                    next_state = ST_READ;
                end
            end

            ST_READ: begin
                next_state = ST_DONE;
            end

            ST_DONE: begin
                next_state = ST_IDLE;
            end

            default: next_state = ST_IDLE;
        endcase
    end

    // Look-Ahead Output Logic: ประเมินค่าล่วงหน้าเพื่อเตรียมแลตช์เข้า Register
    always_comb begin
        adc_convst_nxt      = 1'b0;
        adc_sclk_gate_nxt   = 1'b0;
        data_capture_en_nxt = 1'b0;

        case (current_state)
            ST_IDLE: begin
                if (sample_trigger) begin
                    adc_convst_nxt = 1'b1; // ส่งสัญญาณพัลส์ Convst ในรอบถัดไป
                end
            end

            ST_CONVERT: begin
                if (adc_busy_n) begin
                    adc_sclk_gate_nxt = 1'b1; // เปิด SCLK ในรอบถัดไป
                end
            end

            ST_READ: begin
                data_capture_en_nxt = 1'b1;   // บันทึกข้อมูลเข้า FIFO ในรอบถัดไป
            end

            default: ;
        endcase
    end

    // Output Registers: ขับสัญญาณออกจาก Flip-Flop โดยตรง ปราศจาก Glitch 100%
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            adc_convst      <= 1'b0;
            adc_sclk_gate   <= 1'b0;
            data_capture_en <= 1'b0;
        end else begin
            adc_convst      <= adc_convst_nxt;
            adc_sclk_gate   <= adc_sclk_gate_nxt;
            data_capture_en <= data_capture_en_nxt;
        end
    end

    assign dbg_state = current_state;

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในเครื่องตรวจจับรอยแตกร้าวของท่อส่งก๊าซด้วยคลื่นอัลตราโซนิกความแม่นยำสูง (Ultrasonic NDT Pipeline Scanner) วงจรควบคุมการเก็บสัญญาณใช้ Kintex-7 FPGA เชื่อมต่อกับไอซี 16-bit SAR ADC ความเร็วสูง ($5\text{ MSPS}$) สัญญาณสั่งแปลงค่า `adc_convst` ถูกสร้างขึ้นจาก Moore FSM โดยเขียนเอาต์พุตแบบ Combinational ด้วยคำสั่ง `assign adc_convst = (state == ST_SAMPLE);`

**ผลลัพธ์ที่ล้มเหลว:** เมื่อนำอุปกรณ์ไปทดสอบสแกนท่อจริง ข้อมูลการสแกนความลึกเกิดสัญญาณรบกวนผิดปกติแบบสุ่มขนาดใหญ่ถึง $\pm 2,048\text{ LSB}$ (คิดเป็นข้อผิดพลาดกว่า $6.25\%$ ของฟูลสเกล) ทำให้ระบบส่งสัญญาณเตือนรอยร้าวเท็จ (False Crack Alarm) ตลอดเวลา

```
                 การเกิด Glitch บนสัญญาณควบคุมการแปลงค่า ADC
   
   Clock Edge           ____/¯¯¯¯\____/¯¯¯¯\____/¯¯¯¯\____/¯¯¯¯\____
   
   State Register Bits  [ 3'b011 ]-------------------->[ 3'b100 ] (เปลี่ยน 3 บิตพร้อมกัน!)
   (Binary Encoding)      b0: 1 -> 0 (Delay = 420 ps)
                          b1: 1 -> 0 (Delay = 580 ps)
                          b2: 0 -> 1 (Delay = 210 ps)
                                       /\
   Unregistered Output  ______________/  \__________________________ (GLITCH SPIKE! กว้าง 850 ps)
   adc_convst                          ||
                                       v
                        SAR ADC ตกใจนึกว่ามี Trigger สั่งแปลงซ้ำ!
                        -> สุ่มอ่านข้อมูลกลางช่วงเวลา Sampling Capacitance กำลังชาร์จ!
                        -> เกิด Error พุ่งกระฉูด 2,048 LSB ทันที!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมเครื่องตรวจอัลตราโซนิกถึงรายงานรอยร้าวเท็จแบบสุ่ม?**
   * *ตอบ:* ค่าแรงดันที่อ่านได้จาก SAR ADC มีสัญญาณรบกวนความผิดพลาดสูงถึง $2,048\text{ LSB}$
2. **ทำไม SAR ADC ถึงแปลงค่าแรงดันผิดพลาดมหาศาล?**
   * *ตอบ:* วงจร Sample & Hold ภายใน ADC ถูกสั่งให้เริ่มการแปลงค่า (Hold & Convert) ก่อนที่ตัวเก็บประจุภายในจะชาร์จประจุเสร็จสมบูรณ์
3. **ทำไม ADC ถึงเริ่มการแปลงค่าก่อนเวลาอันควร?**
   * *ตอบ:* ขาพินควบคุม `adc_convst` มีสัญญาณพัลส์แหลม (Glitch Spike) ขนาดกว้าง $850\text{ ps}$ โผล่ขึ้นมาล่วงหน้า
4. **ทำไมขาพิน `adc_convst` ถึงเกิด Glitch Spike ขนาด 850 ps?**
   * *ตอบ:* สัญญาณถูกถอดรหัสผ่านลอจิกคอมบิเนชันโดยตรงจากรีจิสเตอร์สถานะของ FSM ซึ่งเข้ารหัสแบบ Binary และมีบิตเปลี่ยนค่าพร้อมกันถึง 3 บิต ($011_2 \rightarrow 100_2$) โดยที่ความหน่วงเวลาของแต่ละบิตมาถึงไม่พร้อมกัน
5. **ทำไมวิศวกรจึงต่อลอจิกคอมบิเนชันออกไปยังพินภายนอกโดยตรง?**
   * *ตอบ:* วิศวกรเข้าใจผิดคิดว่า Moore FSM ปลอดภัยจาก Glitch เสมอ และไม่ตระหนักว่า **ลอจิกถอดรหัสของ Moore เอาต์พุตก็เกิด Glitch ได้** หากไม่ถูกกั้นด้วย Register เอาต์พุต!

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ Glitch บนสัญญาณ ADC
   
   ความรู้ความเข้าใจทฤษฎี (Engineering Theory)       การออกแบบสถาปัตยกรรม (RTL Architecture)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   เข้าใจผิดว่า    ไม่เข้าใจเรื่อง               ใช้ Combinational ขาดการใช้
   Moore FSM     Hamming Skew                   Decoder ขับ   Look-Ahead
   ไม่มี Glitch  ในการเปลี่ยนสเตต               ตรงสู่ Pin     Output Register
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> สัญญาณรบกวน 2,048 LSB
                                                                |     จาก Glitch Trigger
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   บิตสถานะเปลี่ยน ใช้ Binary Encoding          ไม่ได้รัน Post-  ออสซิลโลสโคป
   3 บิตพร้อมกัน   แทนที่จะเป็น One-Hot         Route Timing   Bandwidth ต่ำ
   Delay ต่างกัน  หรือ Gray                     Simulation     มองไม่เห็นพัลส์ 850ps
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   ฟิสิกส์การเปลี่ยนสถานะ (Silicon Dynamics)       เครื่องมือวัดและการทดสอบ (Instrumentation)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ตรวจสอบพินควบคุมความไวสูง (Control Pin Audit)
ระบุสัญญาณควบคุมภายนอกทุกตัวที่เป็นสัญญาณลักษณะดังนี้:
* สัญญาณจุดชนวนการแปลงค่า (ADC/DAC Trigger: `convst`, `ldac`)
* สัญญาณเปิดปิดสัญญาณนาฬิกา (Clock Gate / Enable: `sclk_gate`)
* สัญญาณควบคุมการเขียนหน่วยความจำ (Write Enable: `we_n`, `wr_en`)
* สัญญาณรีเซ็ตย่อย (Subsystem Reset: `rst_n`)

#### ขั้นตอนที่ 2: บังคับใช้กฎเหล็ก "100% Registered Driving"
สัญญาณควบคุมตามขั้นตอนที่ 1 **จะต้องขับออกจากขา $Q$ ของ D-Flip-Flop โดยตรงเท่านั้น** ห้ามมีเกตคอมบิเนชันใดๆ ขวางระหว่าง Flip-Flop และ I/O Pad เด็ดขาด:
```systemverilog
// บังคับบรรจุลงใน IOB (I/O Block Flip-Flop)
(* IOB = "TRUE" *) reg ext_adc_convst_reg;
always_ff @(posedge clk) begin
    ext_adc_convst_reg <= next_convst_logic;
end
assign adc_convst_pin = ext_adc_convst_reg;
```

#### ขั้นตอนที่ 3: ตรวจสอบรูปคลื่นด้วย High-Bandwidth Scope
ใช้ดิจิทัลออสซิลโลสโคปที่มีแบนด์วิดท์อย่างน้อย $2.5\text{ GHz}$ และหัวโพรบชนิด Active Single-Ended Probe แตะวัดที่ปลายขาพิน เพื่อยืนยันว่าไม่มี Glitch เล็ดลอดออกมา

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| グリッチ最小化 | ぐりっちさいしょうか | Guritchi Saishouka | Glitch Minimization |
| 出力レジスタ化 | しゅつりょくれじすたか | Shutsuryoku Rejisutaka | Output Registering |
| 静的ハザード | せいてきはざーど | Seiteki Hazaado | Static Hazard |
| 動的ハザード | どうてきはざーど | Douteki Hazaado | Dynamic Hazard |
| 冗長論理削除 | じょうちょうろんりさくじょ | Jouchou Ronri Sakujo | Redundant Logic Pruning |
| 先読み出力 | さきよみしゅつりょく | Sakiyomi Shutsuryoku | Look-Ahead Output |
| 誤トリガ | ごとりが | Go-toriga | False Trigger / Spurious Trigger |
| サンプリング誤差 | さんぷりんぐごさ | Sanpuringu Gosa | Sampling Error |
| スキュー差 | すきゅーさ | Skyuu-sa | Skew Difference |
| 入出力ブロック格納 | にゅうしゅつりょくぶろっくかくのう | Nyuushutsuryoku Burokku Kakunou | IOB Packing (`IOB = "TRUE"`) |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** การประชุมตรวจแบบระบบเครื่องมือแพทย์และอุปกรณ์ตรวจวัดความแม่นยำสูง (Precision Medical Sensor Kenzu)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** คุโรดะ ซัง (Kuroda-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** คอนโด คุง (Kondo-kun)

---

**黒田技師 (Kuroda):**  
「近藤君、この超音波探傷器用 ADC コントローラの RTL を確認したが、ADC 変換開始信号 `adc_convst` がムーア型 FSM のステートから `assign` 文のデコーダ経由で直接外部ピンへ出力されているね。しかも状態変数はバイナリ符号化だ。これでは状態遷移の瞬間に確実に出力グリッチが発生するが、なぜレジスタで受けていないのかね？」  
*(Kondo-kun, kono chouonpa tanshouki-you ADC kontoroora no RTL wo kakunin shita ga, ADC henkan kaishi shingou `adc_convst` ga Muua-gata FSM no suteeto kara `assign` bun no dekouda keiyu de chokusetsu gaibu pin e shutsuryoku sarete iru ne. Shikamo joutai hensuu wa bainari fugouka da. Kore dewa joutai sen-i no shunkan ni kakujitsu ni shutsuryoku guritchi ga hassei suru ga, naze rejisuta de ukete inai no kane?)*  
**ความหมาย:** คุณคอนโด ผมตรวจโค้ด RTL ของวงจรควบคุม ADC เครื่องตรวจคลื่นอัลตราโซนิกตัวนี้แล้ว พบว่าสัญญาณเริ่มแปลงค่า `adc_convst` ถูกส่งออกจากสเตตของ Moore FSM ผ่านตัวถอดรหัสคำสั่ง `assign` ตรงไปยังพินภายนอกเลยนะ แถมตัวแปรสถานะยังเป็น Binary อีกด้วย ทำแบบนี้ในจังหวะเปลี่ยนสเตตจะต้องเกิด Glitch ขึ้นอย่างแน่นอน ทำไมถึงไม่นำสัญญาณไปผ่าน Register ก่อนครับ?

---

**近藤技師 (Kondo):**  
「はい、黒田さん。学生時代に『ムーア型は入力が直接出力に現れないためグリッチフリーである』と習いましたので、ミーリー型と違ってムーア型であれば組み合わせデコーダを通しても安全であると認識しておりました。レイテンシを 1 クロックでも節約したかったため、直結いたしました。」  
*(Hai, Kuroda-san. Gakusei jidai ni "Muua-gata wa nyuuryoku ga chokusetsu shutsuryoku ni arawarenai tame guritchi furii de aru" to naraimashita node, Miirii-gata to chigatte Muua-gata de areba kumiawase dekouda wo tooshitemo anzen de aru to ninshiki shite orimashita. Reitenshi wo 1-kurokku demo setsuyaku shitakatta tame, chokketsu itashimashita.)*  
**ความหมาย:** ครับคุณคุโรดะ ตอนสมัยเรียนผมจำได้ว่าอาจารย์สอนว่า "Moore Machine ปราศจาก Glitch เพราะอินพุตไม่ทะลุไปเอาต์พุต" ผมจึงเข้าใจว่า Moore ต่อผ่านคอมบิเนชันแล้วจะปลอดภัยต่างจาก Mealy ครับ และผมอยากประหยัด Latency 1 ไซเคิล จึงต่อตรงออกไปครับ

---

**黒田技師 (Kuroda):**  
「教科書の表面的な知識だけで設計するからそういう大事故を起こすんだ！ムーア型で守られるのは『入力から出力への直通パス』だけだ。状態レジスタ自身がバイナリで複数ビット同時に変化する場合、各ビットの配線遅延の差で過渡的に未定義のデコード値が出力され、数百ピコ秒のスタティックハザードが必ず発生する！実機で $\pm 2,048\text{ LSB}$ もノイズが跳ねて誤検出を起こしている元凶はこれだ！**重大指摘事項とする！** 直ちに先読み論理を用いて出力を完全レジスタ化し、さらに `(* IOB = "TRUE" *)` を付与して I/O ブロック内のフリップフロップから直出しするように改修しなさい！」  
*(Kyoukasho no hyoumendeki na chishiki dake de sekkei suru kara sou iu dai-jiko wo okosunda! Muua-gata de mamorareru no wa "nyuuryoku kara shutsuryoku e no chokutsuu pasu" dake da. Joutai rejisuta jishin ga bainari de fukusuu bitto douji ni henka suru baai, kaku bitto no haisen chien no sa de katoteki ni miteigi no dekoudochi ga shutsuryoku sare, suuhyaku pikobyou no sutatikku hazaado ga kanarazu hassei suru! Jikki de $\pm 2,048\text{ LSB}$ mo noizu ga hanete go-kenshutsu wo okoshite iru genkyou wa kore da! **Juudai shiteki jikou to suru!** Tadachini sakiyomi ronri wo mochiite shutsuryoku wo kanzen rejisutaka shi, sara ni `(* IOB = "TRUE" *)` wo fuyo shite I/O burokku nai no furippufuroppu kara jikadashi suru you ni kaishuu shinasai!)*  
**ความหมาย:** ออกแบบงานด้วยความรู้ผิวเผินจากตำราถึงได้เกิดอุบัติเหตุใหญ่แบบนี้ไงล่ะ! สิ่งที่ Moore ช่วยป้องกันมีแค่ "เส้นทางตรงจากอินพุตไปเอาต์พุต" เท่านั้น แต่ถ้ารีจิสเตอร์สถานะเป็น Binary แล้วเปลี่ยนพร้อมกันหลายบิต ความต่างของความหน่วงสายไฟจะทำให้เกิดค่าถอดรหัสขยะชั่วขณะ ก่อให้เกิด Static Hazard ขนาดหลายร้อยพิโกวินาทีอย่างแน่นอน! นี่คือต้นตอที่ทำให้ชิปจริงเกิด Noise กระฉูดถึง $\pm 2,048\text{ LSB}$ จนตรวจจับผิดพลาด! **ผมสั่งเป็นข้อแก้ไขระดับวิกฤต!** จงรีบใช้ตรรกะ Look-Ahead เพื่อนำเอาต์พุตเข้า Register ให้สมบูรณ์ และใส่ `(* IOB = "TRUE" *)` เพื่อล็อกให้เอาต์พุตขับออกจาก Flip-Flop ใน I/O Block โดยตรงเดี๋ยวนี้!

---

**近藤技師 (Kondo):**  
「ステートの複数ビット遷移によるデコーダハザード…教科書の盲点を痛感いたしました。直ちに IOB 属性を付与した完全レジスタ出力へ改修し、GHz 帯域のオシロスコープでグリッチが完全に消滅した波形を実測して再提出いたします！」  
*(Suteeto no fukusuu bitto sen-i ni yoru dekouda hazaado... kyoukasho no mouten wo tsuukan itashimashita. Tadachini IOB zokusei wo fuyo shita kanzen rejisuta shutsuryoku e kaishuu shi, GHz taiiki no oshirosukoopu de guritchi ga kanzen ni shoumetsu shita hakei wo jissoku shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ปัญหา Decoder Hazard จากการเปลี่ยนหลายบิตของสถานะ... ผมตระหนักถึงจุดบอดของความรู้ตัวเองแล้วครับ ผมจะรีบแก้เป็น Registered Output ใน IOB ทันที และจะนำออสซิลโลสโคประดับ GHz ไปจับรูปคลื่นเพื่อยืนยันว่า Glitch หายไปสนิท 100% แล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณความกว้างพัลส์ของ Static-1 Glitch จากความไม่สมมาตรของเกต

พิจารณาวงจรตรรกะสร้างสัญญาณควบคุม $F = A \cdot \bar{B} + B \cdot C$:
* สัญญาณ $A = 1$ และ $C = 1$ เป็นค่าคงที่
* สัญญาณ $B$ เปลี่ยนแปลงจากระดับลอจิกสูง ('1') เป็นระดับลอจิกต่ำ ('0')
* ความหน่วงเวลาของอินเวอร์เตอร์สร้างสัญญาณ $\bar{B}$: $t_{inv} = 150\text{ ps}$
* ความหน่วงเวลาของเกต AND แบบ 2 อินพุต: $t_{and} = 220\text{ ps}$
* ความหน่วงเวลาของเกต OR แบบ 2 อินพุต: $t_{or} = 260\text{ ps}$
* เวลาเดินทางของสายไฟเชื่อมต่อระหว่างเกต (Inter-gate Routing Delay): $t_{wire} = 80\text{ ps}$

จงคำนวณหาความกว้างของพัลส์ที่เป็นศูนย์ชั่วขณะ (Glitch Pulse Width: $t_{glitch}$) ที่ระดับเอาต์พุต $F$ ร่วงลงสู่ลอจิก '0' ในระหว่างการสลับสถานะนี้?

---

#### ตัวเลือก:
A) $t_{glitch} = 0\text{ ps}$ (ไม่มี Glitch เกิดขึ้นเพราะลอจิกสมดุล)  
B) $t_{glitch} = 150\text{ ps}$  
C) $t_{glitch} = 230\text{ ps}$  
D) $t_{glitch} = 370\text{ ps}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) $t_{glitch} = 150\text{ ps}$**

##### ขั้นตอนที่ 1: กำหนดแกนเวลาและวิเคราะห์จังหวะของแต่ละเทอม
สมมติให้ขอบขาลงของสัญญาณ $B$ ($1 \rightarrow 0$) เกิดขึ้นที่เวลา $t = 0$:
1. **เทอมที่ 2 ($T_2 = B \cdot C$):**
   * ขาเข้า $B$ เปลี่ยนจาก $1 \rightarrow 0$ ที่ $t = 0$
   * สัญญาณเดินทางผ่านเกต AND:
     $$t_{fall, T2} = 0 + t_{and} = 220\text{ ps}$$
   * ดังนั้น เทอม $T_2$ จะร่วงลงจาก $1 \rightarrow 0$ ที่เวลา $t = 220\text{ ps}$

2. **เทอมที่ 1 ($T_1 = A \cdot \bar{B}$):**
   * อินเวอร์เตอร์สร้าง $\bar{B}$ ต้องรอให้ $B$ เปลี่ยนค่าก่อน:
     $$t_{rise, \bar{B}} = 0 + t_{inv} = 150\text{ ps}$$
   * สัญญาณ $\bar{B}$ เดินทางเข้าเกต AND ของเทอมที่ 1:
     $$t_{rise, T1} = t_{rise, \bar{B}} + t_{and} = 150\text{ ps} + 220\text{ ps} = 370\text{ ps}$$
   * ดังนั้น เทอม $T_1$ จะดีดขึ้นจาก $0 \rightarrow 1$ ที่เวลา $t = 370\text{ ps}$

##### ขั้นตอนที่ 2: วิเคราะห์สถานะของเกต OR ปลายทาง
เกต OR รับสัญญาณจาก $T_1$ และ $T_2$:
* ช่วงเวลา $t < 220\text{ ps}$: $T_2 = 1, T_1 = 0 \Rightarrow F = 1$
* ที่เวลา $t = 220\text{ ps}$: $T_2$ ร่วงลงเป็น $0$ ในขณะที่ $T_1$ ยังคงเป็น $0$ อยู่! ส่งผลให้ขาเข้าทั้งสองของเกต OR กลายเป็น $0$ พร้อมกัน $\Rightarrow$ เอาต์พุตเริ่มร่วงลงเป็น $0$
* ที่เวลา $t = 370\text{ ps}$: $T_1$ เพิ่งดีดขึ้นเป็น $1 \Rightarrow$ เอาต์พุตดีดกลับขึ้นเป็น $1$

##### ขั้นตอนที่ 3: คำนวณความกว้างพัลส์ Glitch
$$t_{glitch} = t_{rise, T1} - t_{fall, T2} = 370\text{ ps} - 220\text{ ps} = 150\text{ ps}$$
พัลส์ Glitch กว้างเท่ากับความหน่วงเวลาของอินเวอร์เตอร์ $t_{inv} = 150\text{ ps}$ พอดี ซึ่งหากพัลส์นี้วิ่งเข้าขา Write Enable ของหน่วยความจำ จะสร้างความเสียหายให้ข้อมูลทันที

---

### คำถามที่ 2: การเปรียบเทียบทรัพยากรระหว่าง Standard Moore vs State-Bit Embedded FSM

สเตตแมชชีนขนาด $N = 8$ สถานะ มีสัญญาณเอาต์พุตที่ต้องส่งออกไปยังภายนอกจำนวน $K = 4$ บิต:
* หากใช้ **วิธีที่ 1 (Standard Moore + Dedicated Output Registers):**
  - ใช้ Binary State Register: $m = \lceil \log_2 8 \rceil = 3$ Flip-Flops
  - ลอจิกถอดรหัส Moore: ใช้ LUT6 จำนวน 4 ตัวเพื่อถอดรหัสเอาต์พุต 4 บิต
  - รีจิสเตอร์เอาต์พุต: ใช้ Flip-Flops ภายนอกเพิ่มอีก 4 ตัว
* หากใช้ **วิธีที่ 2 (State-Bit Output Embedding):**
  - วิศวกรจัดให้รูปแบบของบิตเอาต์พุตเป็นเอกลักษณ์เฉพาะในแต่ละสถานะ ทำให้เวกเตอร์สถานะมีขนาด 4 บิต โดยไม่มีการใช้ LUT ถอดรหัสเอาต์พุตแยกต่างหาก

จงคำนวณหาจำนวน Flip-Flop รวม และจำนวน LUT รวมที่ประหยัดได้จากวิธีที่ 2?

---

#### ตัวเลือก:
A) ประหยัด Flip-Flop ได้ 3 ตัว และประหยัด LUT ได้ 4 ตัว  
B) ประหยัด Flip-Flop ได้ 1 ตัว แต่ใช้ LUT เพิ่มขึ้น 2 ตัว  
C) ใช้ Flip-Flop เท่าเดิม และประหยัด LUT ได้ 2 ตัว  
D) ประหยัด Flip-Flop ได้ 3 ตัว แต่ใช้ LUT เท่าเดิม

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) ประหยัด Flip-Flop ได้ 3 ตัว และประหยัด LUT ได้ 4 ตัว**

##### ขั้นตอนที่ 1: นับทรัพยากรวิธีที่ 1
* Flip-Flops: $3 \text{ (State Reg)} + 4 \text{ (Output Reg)} = 7 \text{ Flip-Flops}$
* LUTs ถอดรหัสเอาต์พุต: $4 \text{ LUTs}$

##### ขั้นตอนที่ 2: นับทรัพยากรวิธีที่ 2 (State-Bit Embedding)
* Flip-Flops: ใช้บิตเอาต์พุต 4 บิตทำหน้าที่เป็น State Register ในตัว $\Rightarrow 4 \text{ Flip-Flops}$
* LUTs ถอดรหัสเอาต์พุต: ดึงตรงจากขา Q ของ Flip-Flop $\Rightarrow 0 \text{ LUTs}$

##### ขั้นตอนที่ 3: คำนวณผลต่างการประหยัดทรัพยากร
* การประหยัด Flip-Flops: $7 - 4 = 3 \text{ Flip-Flops}$
* การประหยัด LUTs: $4 - 0 = 4 \text{ LUTs}$

วิธี State-Bit Embedding ไม่เพียงแต่ขจัด Glitch ได้อย่างสมบูรณ์แบบ แต่ยังช่วยลดทั้งพื้นที่และการใช้พลังงานของชิปได้อย่างมหาศาล

---

### คำถามที่ 3: ข้อกำหนดการบรรจุ Flip-Flop ลงใน I/O Block (`IOB = "TRUE"`)

เหตุใดวิศวกรอาวุโสจึงมักระบุคำสั่ง `(* IOB = "TRUE" *)` บนรีจิสเตอร์เอาต์พุตของ FSM ที่เชื่อมต่อไปยังขา Pin ภายนอกชิป FPGA เสมอ?

---

#### ตัวเลือก:
A) เพื่อเพิ่มความถี่ของสัญญาณนาฬิกาให้สูงกว่า 1 GHz  
B) เพื่อบังคับให้ Flip-Flop ถูกวางลงในเซลล์ I/O ทางกายภาพที่ขอบชิป ขจัดความแปรปรวนของความหน่วงสายภายในผืนสวิตช์เมทริกซ์ (Fabric Routing Skew) และให้ค่า Clock-to-Pad ($T_{co}$) ที่ต่ำและคงที่ที่สุด  
C) เพื่อเปิดใช้งานตัวต้านทาน Pull-up ภายในขาพิน  
D) เพื่อเปลี่ยนสัญญาณให้เป็นแบบ Differential LVDS อัตโนมัติ

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เพื่อบังคับให้ Flip-Flop ถูกวางลงในเซลล์ I/O ทางกายภาพที่ขอบชิป ขจัดความแปรปรวนของความหน่วงสายภายในผืนสวิตช์เมทริกซ์ (Fabric Routing Skew) และให้ค่า Clock-to-Pad ($T_{co}$) ที่ต่ำและคงที่ที่สุด**

##### เหตุผลเชิงกายภาพของซิลิคอน:
หากวาง Flip-Flop ไว้ใน Slice ของ Core Fabric ทั่วไป สัญญาณเอาต์พุตจะต้องเดินทางผ่าน Programmable Interconnect หลายช่วงเพื่อไปยังขา Pad ภายนอก ทำให้ความหน่วง ($t_{co}$) เปลี่ยนแปลงไปทุกครั้งที่มีการคอมไพล์ใหม่ (Non-deterministic) และเกิด Clock-to-Out Skew ระหว่างขาสูงถึง $1.5 - 3.0\text{ ns}$

การระบุ `IOB = "TRUE"` จะบังคับให้เครื่องมือจัดวาง Flip-Flop ลงในเซลล์ฮาร์ดแวร์เฉพาะกิจที่แนบติดกับ Pad บัฟเฟอร์โดยตรง ทำให้:
1. ค่า $T_{co}$ ลดลงเหลือเพียงระดับ sub-nanosecond ($< 0.8\text{ ns}$)
2. ค่า Skew ระหว่างแต่ละพินแทบจะเป็นศูนย์ ($< 50\text{ ps}$)
3. ป้องกันไม่ให้เกิดสัญญาณรบกวนหรือ Glitch บนสายเดินข้ามผืนชิปได้อย่างเด็ดขาด
