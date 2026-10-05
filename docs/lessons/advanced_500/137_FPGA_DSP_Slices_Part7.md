# Lesson 137: FPGA DSP Slices Part 7 - Cascading & Pre-Adders for Symmetric FIR (カスケード接続とプリ加算器: Symmetric Linear-Phase FIR, 50% DSP Reduction, Hardware Pre-Adder Exploitation)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ทฤษฎีตัวกรองเฟสเชิงเส้นแบบสมมาตร (Linear-Phase Symmetric FIR Filter Mathematics)
ในระบบสื่อสารดิจิทัลความเร็วสูง (Digital Communications) และระบบประมวลผลสัญญาณภาพทางการแพทย์ (Ultrasound / MRI Imaging) การบิดเบือนของเฟส (Phase Distortion) เป็นสิ่งที่ไม่สามารถยอมรับได้ ตัวกรองตอบสนองสัญญาณพัลส์จำกัดแบบเฟสเชิงเส้น (Linear-Phase FIR Filter) มีคุณสมบัติเด่นคือ **ความล่าช้ากลุ่มคงที่ (Constant Group Delay: $\tau_g$)** ตลอดทุกย่านความถี่:

$$\tau_g = -\frac{d\theta(\omega)}{d\omega} = \frac{M - 1}{2} \text{ [samples]}$$

คุณสมบัติเฟสเชิงเส้นจะเกิดขึ้นได้ก็ต่อเมื่อชุดสัมประสิทธิ์ของตัวกรอง $h[k]$ มีความสมมาตรแบบคู่ (Even Symmetry) หรือความสมมาตรแบบคี่ (Odd Symmetry):

$$h[k] = h[M - 1 - k] \quad \text{สำหรับ } k = 0, 1, \dots, M-1$$

```
               คุณสมบัติความสมมาตรของสัมประสิทธิ์ตัวกรอง 8 Taps (Even Symmetry)
   
        h[0]       h[1]       h[2]       h[3]   |   h[4]       h[5]       h[6]       h[7]
         ●          ●          ●          ●     |    ●          ●          ●          ●
         |          |          |          |     |    |          |          |          |
         +----------+----------+----------+-----+----+----------+----------+----------+
         ^                                                                            ^
         |========================= h[0] == h[7] =====================================|
                    ^                                                      ^
                    |============== h[1] == h[6] ==========================|
                               ^                                ^
                               |=== h[2] == h[5] ===============|
                                          ^          ^
                                          |== h[3]==h[4] ==|
```

#### 1.1.1 การจัดรูปสมการเพื่อลดจำนวนตัวคูณลง 50% (Symmetric Folding Formulation)
จากสมการคอนโวลูชันดั้งเดิม:
$$y[n] = \sum_{k=0}^{M-1} h[k] \cdot x[n-k]$$

เมื่อดึงตัวคูณร่วม $h[k] = h[M-1-k]$ ออกมา เราสามารถเขียนสมการใหม่ได้เป็น:

$$y[n] = \sum_{k=0}^{\lfloor M/2 \rfloor - 1} h[k] \cdot \Big( x[n-k] + x[n - (M - 1 - k)] \Big) + \text{Center Tap}$$

* **นัยสำคัญทางวิศวกรรม:** เราสามารถ **บวกสัญญาณตัวอย่างคู่สมมาตรเข้าด้วยกันก่อน ($x[n-k] + x[n-M+1+k]$) แล้วค่อยส่งเข้าตัวคูณเพียงครั้งเดียว**!
* ผลลัพธ์: จำนวนตัวคูณที่ต้องใช้ลดลงเหลือเพียง **ครึ่งหนึ่ง ($M/2$ Multipliers)** พอดี!

---

### 1.2 การใช้ประโยชน์จากฮาร์ดแวร์ Pre-Adder ใน DSP48E2
ในอดีต (เช่น ยุค Spartan-3 หรือ Virtex-4) ตัว DSP Slice ไม่มีวงจรบวกก่อนหน้า (No Pre-Adder) วิศวกรจึงต้องสร้างวงจรบวกสัญญาณ $x$ บน Soft Fabric LUT ก่อนส่งเข้า DSP ซึ่งทำให้เปลือง LUT นับพันตัวและปิด Timing ได้ยาก

ทว่าในชิปสถาปัตยกรรมยุคใหม่ (AMD Xilinx 7-Series, UltraScale, UltraScale+) ภายใน DSP48E1/DSP48E2 ได้ฝัง **Hardwired Pre-Adder ขนาด 27 บิต** ไว้ในตัวซิลิคอนเรียบร้อยแล้ว:

```
            การทำงานของ Hardware Pre-Adder ใน DSP48E2 สำหรับ Symmetric FIR
   
   x[n-k] (พอร์ต D: 27 บิต) --------+
                                    |
                                    v
   x[n-M+1+k] (พอร์ต A: 27 บิต) -> [ Hard Pre-Adder ] ---> (27-bit Sum) ---+
                                   [    D + A       ]                      |
                                                                           v
   h[k] (พอร์ต B: 18 บิต) -----------------------------------------------> [ 27 x 18 Multiplier ]
                                                                           |
                                                                           v
                                 PCIN ---> [ 48-bit Accumulator ] -------> PCOUT (Cascade)
```

การบวก $(D + A)$ เกิดขึ้นภายใน Hard Macro ด้วยความเร็วสูงระดับ sub-nanosecond โดย **ไม่ใช้ Soft LUT Fabric แม้แต่ตัวเดียว** ทำให้ฟิลเตอร์ขนาด $64$ Taps สามารถยุบการใช้งาน DSP จากเดิม 64 ตัว เหลือเพียง **$32$ DSP Slices เท่านั้น**!

---

### 1.3 สถาปัตยกรรม Systolic Cascade สำหรับ Symmetric FIR (Folded Systolic Architecture)
การนำ Pre-Adder มาต่อเป็นสาย Cascade จำเป็นต้องมีเส้นทางสายหน่วงเวลาสองชุด:
1. **Forward Delay Line ($x[n-k]$):** สัญญาณตัวอย่างใหม่วิ่งไปข้างหน้าผ่านสาย Cascade ขาเข้า (`ACOUT` $\rightarrow$ `ACIN`)
2. **Backward Delay Line ($x[n-M+1+k]$):** สัญญาณตัวอย่างเก่าที่ถูกหน่วงไว้วิ่งย้อนกลับมาบรรจบที่พอร์ต $D$ ผ่าน Shift Register ใน Fabric หรือ Block RAM

```
           Folded Systolic FIR Topology
   
   Forward Line:   x[n] ---> [Tap 0] ---> [Tap 1] ---> ... ---> [Tap N/2-1] (Center)
                               |            |                        |
                              (D)          (D)                      (D)
                            [DSP #0]     [DSP #1]               [DSP #Center]
                              (A)          (A)                      (A)
                               ^            ^                        ^
                               |            |                        |
   Backward Line:  x[n-M+1] <--+------------+------------------------+ (Return Delay)
```

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Symmetric FIR Tap อาศัย Pre-Adder 100%

```systemverilog
//=============================================================================
// Module: symmetric_fir_tap.sv
// Description: Fully Inferred Symmetric FIR Tap exploiting DSP48E2 Hard Pre-Adder
// Target: AMD UltraScale+ (50% DSP Reduction & Zero Soft-Adder LUTs)
//=============================================================================
`timescale 1ns / 1ps

module symmetric_fir_tap #(
    parameter bit IS_FIRST_TAP = 1'b0,
    parameter int DATA_WIDTH   = 16,
    parameter int COEFF_WIDTH  = 16,
    parameter int ACCUM_WIDTH  = 48
)(
    input  logic                          clk,
    input  logic                          rst_sync,
    // สัญญาณตัวอย่างคู่สมมาตร (Forward & Backward Samples)
    input  logic signed [DATA_WIDTH-1:0]  x_fwd_in,  // x[n-k]
    input  logic signed [DATA_WIDTH-1:0]  x_bwd_in,  // x[n - (M-1-k)]
    // สัมประสิทธิ์ฟิลเตอร์
    input  logic signed [COEFF_WIDTH-1:0] coeff_in,
    // สาย Cascade ทางด่วน
    input  logic signed [ACCUM_WIDTH-1:0] pcin,
    output logic signed [ACCUM_WIDTH-1:0] pcout
);

    // Stage 1: Input Registers (DREG และ AREG ใน DSP48E2)
    logic signed [DATA_WIDTH-1:0]  d_reg;
    logic signed [DATA_WIDTH-1:0]  a_reg;
    logic signed [COEFF_WIDTH-1:0] b_reg1, b_reg2;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            d_reg  <= '0;
            a_reg  <= '0;
            b_reg1 <= '0;
        end else begin
            d_reg  <= x_fwd_in; // เข้าพอร์ต D
            a_reg  <= x_bwd_in; // เข้าพอร์ต A
            b_reg1 <= coeff_in; // เข้าพอร์ต B
        end
    end

    // Stage 2: Pre-Adder Stage (ADREG)
    // ผลบวกคู่สมมาตร (D + A) ขนาด 17 บิต บรรจุลงใน Pre-Adder 27 บิตได้สบาย
    logic signed [DATA_WIDTH:0]    pre_add_reg;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            pre_add_reg <= '0;
            b_reg2      <= '0;
        end else begin
            pre_add_reg <= d_reg + a_reg; // Inferred to DSP48E2 Pre-Adder
            b_reg2      <= b_reg1;
        end
    end

    // Stage 3: Multiplier Stage (MREG)
    logic signed [33:0] mult_reg;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            mult_reg <= '0;
        end else begin
            mult_reg <= pre_add_reg * b_reg2;
        end
    end

    // Stage 4: Accumulation Stage with Cascade (PREG)
    logic signed [ACCUM_WIDTH-1:0] p_reg;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            p_reg <= '0;
        end else begin
            if (IS_FIRST_TAP) begin
                p_reg <= mult_reg;
            end else begin
                p_reg <= mult_reg + pcin; // ใช้ Hard Cascade Path
            end
        end
    end

    assign pcout = p_reg;

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในโครงการพัฒนาระบบเครื่องอัลตราซาวด์สแกนหัวใจ 8 แชนเนล (8-Channel Cardiac Ultrasound Beamformer) บนชิป Kintex-7 FPGA แต่ละแชนเนลต้องใช้ตัวกรอง 64-Tap Linear-Phase FIR ทำงานที่ความถี่ $f_{clk} = 350\text{ MHz}$ หากออกแบบแบบธรรมดาโดยไม่ยุบความสมมาตร ระบบจะต้องใช้ DSP ทั้งสิ้น:

$$N_{dsp} = 8 \text{ channels} \times 64 \text{ taps} = 512 \text{ DSP Slices}$$

ทว่าชิป Kintex-7 เบอร์ที่เลือกใช้มี DSP ทั้งชิปเพียง **$400$ Slices** เท่านั้น!

**ผลลัพธ์ที่ล้มเหลว:** วิศวกรจบใหม่พยายามแก้ปัญหาโดยเขียนลอจิกบวกคู่สมมาตร $(x_1 + x_2)$ บน Fabric RTL ก่อนส่งเข้าตัวคูณ แต่กลับเขียนโค้ดแบบไม่ใส่ Register คั่นกลาง ผลปรากฏว่าวงจรบวก Soft Adder จำนวน 256 ตัวบน Fabric สร้าง Logic Depth ลึกขวางหน้าทางเข้า DSP ส่งผลให้รายงาน STA ติดลบอย่างรุนแรง: $WNS = -1.680\text{ ns}$ ไม่สามารถทำงานที่ความถี่ $350\text{ MHz}$ ได้ ภาพอัลตราซาวด์เกิดอาการเฟรมค้างและแตกเป็นเม็ดทราย

```
                 ความล้มเหลวของการทำ Symmetric นอกตัวชิป DSP
   
   [ ความพยายามที่ล้มเหลว: บวกบน Soft Fabric โดยไม่ใช้ Hard Pre-Adder ]
   x[n-k] ----+
              v
   x[n-M+k] -> [ 256 x Soft Fabric Adders ] === สายไฟยาว ===> [ DSP Multiplier ]
               (กิน LUT มหาศาล + Delay 1.8ns)                  (WNS ติดลบ -1.68ns!)
   
   [ การแก้ปัญหาที่ถูกต้อง: ดึง Hard Pre-Adder ใน DSP48E1 มาใช้งาน 100% ]
   x[n-k] --------> Port D [ DSP48E1 Hard Pre-Adder ] ---> Multiplier ---> WNS = +0.45ns!
   x[n-M+k] ------> Port A [ (Zero LUT, Latency ตรง) ]     (ใช้ DSP เพียง 256 ตัว พอดีงบ!)
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมระบบอัลตราซาวด์ถึงคำนวณบีมฟอร์มมิ่งไม่ทันและภาพแตก?**
   * *ตอบ:* ตัวกรอง 64-Tap FIR ในทั้ง 8 แชนเนลเกิด Setup Time Violation อย่างรุนแรงที่ $350\text{ MHz}$
2. **ทำไมตัวกรองถึงเกิด Setup Time Violation?**
   * *ตอบ:* เส้นทางสัญญาณขาเข้าของ DSP มีความหน่วงสะสมจากวงจรบวกบนผืน Fabric ขวางอยู่
3. **ทำไมจึงต้องมีวงจรบวกบนผืน Fabric ขวางอยู่หน้า DSP?**
   * *ตอบ:* วิศวกรต้องการลดจำนวน DSP จาก 512 ตัวให้เหลือ 256 ตัว เพื่อให้พอกับทรัพยากรชิปที่มี 400 ตัว จึงเขียนวงจรบวกคู่สมมาตรดักหน้าตัวคูณ
4. **ทำไมวงจรบวกคู่สมมาตรถึงหลุดไปสร้างบนผืน Fabric?**
   * *ตอบ:* วิศวกรเขียนโค้ดโดยไม่ตรงตามโครงสร้าง Template การอนุมาน (Inference Template) ของ Hard Pre-Adder
5. **ทำไมวิศวกรจึงไม่รู้ว่ามี Hard Pre-Adder อยู่ในตัว DSP?**
   * *ตอบ:* วิศวกรขาดความรู้เรื่องสถาปัตยกรรมภายในของ DSP48E1/E2 และไม่ทราบว่าพอร์ต $D$ และพอร์ต $A$ สามารถบวกกันในตัวชิปได้โดยตรงโดยไม่ต้องพึ่งพา Fabric LUT ภายนอก

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของตัวกรองอัลตราซาวด์
   
   ความรู้เรื่องสถาปัตยกรรมชิป (Architecture Knowledge)   การเขียนโค้ด RTL (RTL Inferencing)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ไม่รู้ว่ามี    เข้าใจผิดว่า                   เขียนตัวบวก    ไม่มีการใส่
   Hard Pre-Adder ต้องใช้ Fabric                แยกอยู่นอกบล็อก Pipeline Register
   ในตัว DSP     บวกคู่สมมาตร                    Always ของ DSP ให้ตรงจังหวะ
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> WNS ติดลบ -1.68ns
                                                                |     ภาพอัลตราซาวด์ค้าง
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   ข้อจำกัดงบ     Kintex-7                      ไม่ได้ตรวจสอบ  ไม่ได้ใช้คำสั่ง
   มี DSP เพียง   มีพื้นที่จำกัด                 Synthesis Log  (* use_dsp = "yes" *)
   400 Slices     (8ch x 64 = 512)              ว่ามี Pre-Adder บังคับ
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   งบประมาณทรัพยากร (Resource Constraints)        การตรวจสอบในขั้นตอนคอมไพล์ (EDA Audit)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ตรวจสอบคุณสมบัติความสมมาตรของฟิลเตอร์ (Symmetry Audit)
ตรวจสอบชุดสัมประสิทธิ์ฟิลเตอร์จาก MATLAB/Python หากพบว่าเป็น Linear-Phase ($h[k] == h[M-1-k]$) ต้องบังคับใช้ Pre-Adder Architecture ทันทีเพื่อประหยัดทรัพยากร $50\%$

#### ขั้นตอนที่ 2: เขียนโค้ดตามเทมเพลต Hard Pre-Adder ของ Vivado
เขียนสัญญาณอินพุตทั้งสองให้เข้าไปบวกกันภายในบล็อก Sequential Always ที่ผูกกับ DSP:
```systemverilog
always_ff @(posedge clk) begin
    d_reg       <= x_forward;
    a_reg       <= x_backward;
    pre_add_reg <= d_reg + a_reg; // บรรทัดนี้จะถูกดูดเข้า Pre-Adder 100%
    mult_reg    <= pre_add_reg * coeff_reg;
end
```

#### ขั้นตอนที่ 3: ตรวจสอบยืนยันใน Vivado Synthesis Log
```text
INFO: [Synth 8-5844] Detected Inferred DSP 'u_fir/tap_inst' with Pre-Adder:
  Pre-Adder Input D: 16 bits
  Pre-Adder Input A: 16 bits
  Multiplier: (D+A)*B (Inferred to Hard Macro DSP48E1)
  DSP Slices Used: 256 (Reduced from 512, 50% Savings Achieved!)
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| 線形位相フィルタ | せんけいいそうふぃるた | Senkei Isou Firuta | Linear-Phase Filter |
| 対称係数 | たいしょうけいすう | Taishou Keisuu | Symmetric Coefficients |
| プリ加算器活用 | ぷりかさんきかつよう | Puri Kasanki Katsuyou | Pre-Adder Exploitation |
| 乗算器半減化 | じょうざんきはんげんか | Jouzanki Hangenka | 50% Multiplier Reduction |
| 群遅延時間一定 | ぐんちえんじかんいってい | Gun-chien Jikan Ittei | Constant Group Delay |
| 後方遅延ライン | こうほうちえんらいん | Kouhou Chien Rain | Backward Delay Line |
| リソース枯渇 | りそーすこかつ | Risoosu Kokatsu | Resource Depletion / Starvation |
| 折返し構造 | おりかえしこうぞう | Orikaeshi Kouzou | Folded / Symmetric Topology |
| ビームフォーマ | びーむふぉーま | Biimufooma | Beamformer (วงจรรวมสัญญาณคลื่น) |
| 推論成功確認 | すいろんせいこうかくにん | Suiron Seikou Kakunin | Inferencing Success Verification |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** การประชุมตรวจแบบระบบประมวลผลสัญญาณเครื่องอัลตราซาวด์หัวใจ (Medical Ultrasound Beamformer Kenzu)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** อุเอโนะ ซัง (Ueno-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** คาวามุระ คุง (Kawamura-kun)

---

**上野技師 (Ueno):**  
「川村君、この心臓超音波ビームフォーマの DSP リソース見積もりだが、Kintex-7 の上限 400 スライスに対して、512 個も要求されてリソースエラー（Over-utilization）で論理合成が止まっているぞ。さらに無理やりファブリック加算器で対称合成しようとした形跡があるが、350MHz で WNS が $-1.680\text{ ns}$ も大破滅している。なぜ DSP48E1 の内蔵プリ加算器（Hard Pre-Adder）を使って乗算器数を半減させなかったのかね？」  
*(Kawamura-kun, kono shinzou chouonpa biimufooma no DSP risoosu mitsumori dakedo, Kintex-7 no jougen 400 suraisu ni taishite, 512-ko mo youkyuu sarete risoosu eraa (Over-utilization) de ronri gousei ga tomatte iru zo. Sara ni muriyari faburikku kasanki de taishou gousei shiyou to shita keiseki ga aru ga, 350MHz de WNS ga $-1.680\text{ ns}$ mo dai-hametsu shite iru. Naze DSP48E1 no naizou puri kasanki (Hard Pre-Adder) wo tsukatte jouzankisuu wo hangen sase nakatta no kane?)*  
**ความหมาย:** คุณคาวามุระ การประเมินทรัพยากร DSP ของเครื่องอัลตราซาวด์หัวใจตัวนี้ ชิป Kintex-7 มีเพดานแค่ 400 สไลซ์ แต่วงจรกลับเรียกใช้ถึง 512 ตัวจนเกิด Resource Error สังเคราะห์ไม่ผ่านนะ แถมยังมีร่องรอยการพยายามเอา Soft Adder ภายนอกมาบวกคู่สมมาตรจนเวลาที่ 350MHz พังพินาศถึง $-1.680\text{ ns}$ อีก ทำไมถึงไม่ใช้ Hard Pre-Adder ในตัว DSP48E1 เพื่อลดจำนวนตัวคูณลงครึ่งหนึ่งครับ?

---

**川村技師 (Kawamura):**  
「はい、上野さん。8 チャンネルの 64 タップフィルタですので、単純計算で $8 \times 64 = 512$ 個の乗算器が必要となってしまいました。リソースを削減するためにファブリック上で $x[n-k] + x[n-M+1+k]$ を加算してから DSP に入れようとしたのですが、外付け加算器の配線遅延が大きすぎてタイミングが破綻してしまいました。DSP の中に加算器が内蔵されているとは知りませんでした。」  
*(Hai, Ueno-san. 8-channeru no 64-tappu firuta desu node, tanjun keisan de $8 \times 64 = 512$-ko no jouzanki ga hitsuyou to natte shimaimashita. Risoosu wo sakugen suru tame ni faburikku-jou de $x[n-k] + x[n-M+1+k]$ wo kasan shite kara DSP ni ireyou to shita no desu ga, sotodzuke kasanki no haisen chien ga ookisugite taimingu ga hatan shite shimaimashita. DSP no naka ni kasanki ga naizou sarete iru to wa shirimasen deshita.)*  
**ความหมาย:** ครับคุณอุเอโนะ เนื่องจากเป็นฟิลเตอร์ 64 Tap จำนวน 8 แชนเนล คิดเลขตรงๆ จึงต้องใช้ตัวคูณ $8 \times 64 = 512$ ตัวครับ ผมพยายามลดทรัพยากรโดยนำสัญญาณคู่สมมาตรมาบวกกันบน Fabric ก่อนส่งเข้า DSP แต่ความหน่วงสายไฟของวงจรบวกภายนอกมันยาวเกินไปจน Timing พังครับ ผมไม่เคยทราบมาก่อนเลยว่าภายใน DSP มีวงจรบวกพรีแอดเดอร์ในตัวอยู่แล้วครับ

---

**上野技師 (Ueno):**  
「デバイスの基本機能を把握せずにアーキテクチャを決めるな！Kintex-7 の DSP48E1 には、乗算器の直前に 25 ビット（UltraScale+ では 27 ビット）のハードウェア・プリ加算器が最初から組み込まれているんだ！正しい RTL 記述を用いれば、外付け LUT を 1 個も使わずにシリコン内部で対称加算を実行できる。これにより 512 個必要だった DSP は一気に**半分の 256 個に激減**し、400 スライスの枠内に余裕で収まり、350MHz のタイミングも軽々と収束する！**重大是正事項とする！** 直ちに全 8 チャンネルのフィルタ記述を DSP 内蔵プリ加算器の推論パターンへ全面改修し、DSP 使用量 256 個、WNS プラス収束を達成しなさい！」  
*(Debaisu no kihon kinou wo haaku sezu ni aakitekucha wo kimeru na! Kintex-7 no DSP48E1 ni wa, jouzanki no chokuzen ni 25-bitto (UltraScale+ dewa 27-bitto) no haadowea puri kasanki ga saisho kara kumikomarete irunda! Tadashii RTL kijutsu wo mochiireba, sotodzuke LUT wo 1-ko mo tsukawazu ni shirikon naibu de taishou kasan wo jikkou dekiru. Kore ni yori 512-ko hitsuyou datta DSP wa ikki ni **hanbun no 256-ko ni gekigen** shi, 400 suraisu no waku-nai ni yoyuu de osamari, 350MHz no taimingu mo karugaruto shuusoku suru! **Juudai zeisei jikou to suru!** Tadachini zen 8-channeru no firuta kijutsu wo DSP naizou puri kasanki no suiron pataan e zenmen kaishuu shi, DSP shiyouryou 256-ko, WNS purasu shuusoku wo tassei shinasai!)*  
**ความหมาย:** อย่าริอ่านกำหนดสถาปัตยกรรมโดยไม่รู้ฟังก์ชันพื้นฐานของชิปสิ! ใน DSP48E1 ของ Kintex-7 มันมี Hardware Pre-Adder ขนาด 25 บิต (บน UltraScale+ มี 27 บิต) ฝังอยู่หน้าตัวคูณมาตั้งแต่เกิดแล้ว! ถ้าเขียน RTL ให้ถูกต้อง การบวกคู่สมมาตรจะเกิดขึ้นในซิลิคอนโดยไม่เสีย LUT ภายนอกแม้แต่ตัวเดียว! ส่งผลให้ DSP ที่เคยต้องใช้ 512 ตัวจะ**ลดฮวบลงครึ่งหนึ่งเหลือเพียง 256 ตัวทันที** บรรจุลงในโควตา 400 สไลซ์ได้อย่างสบายๆ และปิด Timing ที่ 350MHz ได้อย่างง่ายดาย! **ผมสั่งเป็นข้อแก้ไขเร่งด่วน!** จงรีบแก้โค้ดฟิลเตอร์ทั้ง 8 แชนเนลให้เข้าแพตเทิร์น Pre-Adder ในตัว DSP เดี๋ยวนี้ โดยต้องใช้ DSP เพียง 256 ตัวและค่า WNS ต้องเป็นบวก!

---

**川村技師 (Kawamura):**  
「内蔵プリ加算器による乗算器数半減の効果に目を見張る思いです…！外付け LUT を排除して内部で完結させる重要性を骨身にしみて理解いたしました。直ちに全チャンネルをハード・プリ加算器推論構造へ改修し、DSP 256 個での完全動作を実証して再提出いたします！」  
*(Naizou puri kasanki ni yoru jouzankisuu hangen no kouka ni me wo miharuto omoi desu...! Sotodzuke LUT wo haijo shite naibu de kanketsu saseru juuyousei wo honemi ni shimite rikai itashimashita. Tadachini zen-channeru wo haado puri kasanki suiron kouzou e kaishuu shi, DSP 256-ko de no kanzen dousa wo jisshou shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ผลลัพธ์ของการลดตัวคูณลงครึ่งหนึ่งด้วย Pre-Adder ในตัวมันน่าทึ่งมากครับ...! ผมเข้าใจอย่างลึกซึ้งแล้วว่าการกำจัด Soft LUT และจบงานในชิปสำคัญเพียงใด ผมจะรีบแก้โค้ดทุกแชนเนลให้แมปลง Pre-Adder ทันที และพิสูจน์การทำงานด้วย DSP 256 ตัวให้สำเร็จแล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณเปรียบเทียบทรัพยากรและกำลังไฟฟ้าระหว่าง Standard FIR vs Symmetric Pre-Adder FIR

ในระบบประมวลผลสัญญาณคลื่นเรดาร์ ตัวกรอง 64-Tap Linear-Phase FIR ทำงานที่ความถี่ $f_{clk} = 400\text{ MHz}$ บน UltraScale+ FPGA ($V_{DD} = 0.85\text{ V}$):
* กำลังไฟฟ้าเฉลี่ยต่อ 1 DSP Slice ที่ทำงานเต็มกำลัง: $P_{dsp} = 18.5\text{ mW}$
* หากออกแบบด้วย **วิธีที่ 1 (Standard Non-Symmetric FIR):** ต้องใช้ DSP48E2 จำนวน $64$ สไลซ์
* หากออกแบบด้วย **วิธีที่ 2 (Symmetric Folded FIR อาศัย Hard Pre-Adder):** ยุบเหลือ DSP48E2 เพียง $32$ สไลซ์ โดยมี Shift Register (SRL) ภายนอกสำหรับ Backward Delay Line ซึ่งกินพลังงานเพิ่มขึ้นรวม $12.0\text{ mW}$

จงคำนวณหากำลังไฟฟ้ารวม ($P_{total}$) ของวิธีที่ 1 เทียบกับวิธีที่ 2 และระบุเปอร์เซ็นต์พลังงานที่ประหยัดได้?

---

#### ตัวเลือก:
A) วิธีที่ 1: $1.184\text{ W}$, วิธีที่ 2: $0.604\text{ W}$ (ประหยัดพลังงานลง $49.0\%$)  
B) วิธีที่ 1: $1.184\text{ W}$, วิธีที่ 2: $0.592\text{ W}$ (ประหยัดพลังงานลง $50.0\%$)  
C) วิธีที่ 1: $2.368\text{ W}$, วิธีที่ 2: $1.208\text{ W}$  
D) ทั้งสองวิธีใช้พลังงานเท่ากันเพราะคำนวณสมการเดียวกัน

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) วิธีที่ 1: $1.184\text{ W}$, วิธีที่ 2: $0.604\text{ W}$ (ประหยัดพลังงานลง $49.0\%$)**

##### ขั้นตอนที่ 1: คำนวณกำลังไฟฟ้าของวิธีที่ 1 (Standard 64 DSPs)
$$P_{total1} = 64 \times P_{dsp} = 64 \times 18.5\text{ mW} = 1,184\text{ mW} = 1.184\text{ W}$$

##### ขั้นตอนที่ 2: คำนวณกำลังไฟฟ้าของวิธีที่ 2 (Symmetric 32 DSPs + SRL)
กำลังไฟฟ้าของ 32 DSP Slices:
$$P_{dsp\_part2} = 32 \times 18.5\text{ mW} = 592\text{ mW}$$
รวมกำลังไฟฟ้าของ Backward Delay SRL:
$$P_{total2} = 592\text{ mW} + 12.0\text{ mW} = 604\text{ mW} = 0.604\text{ W}$$

##### ขั้นตอนที่ 3: คำนวณเปอร์เซ็นต์พลังงานที่ประหยัดได้
$$\% \text{Saved} = \frac{1.184\text{ W} - 0.604\text{ W}}{1.184\text{ W}} \times 100\% = \frac{0.580}{1.184} \times 100\% \approx 48.986\% \approx 49.0\%$$

นอกจากจะประหยัดพื้นที่ชิปไปถึง **$32$ DSP Slices** แล้ว การใช้ Hard Pre-Adder ยังช่วยลดการใช้พลังงานและความร้อนของระบบลงได้เกือบ **$50\%$** ทันที!

---

### คำถามที่ 2: การตรวจสอบขีดจำกัดบิตของ Pre-Adder ป้องกันการล้นค่า (Pre-Adder Bit Growth)

สัญญาณเซนเซอร์อัลตราซาวด์จาก ADC มีขนาด $16$ บิตแบบคิดเครื่องหมาย (Signed Two's Complement: $[-32,768 \dots +32,767]$):
* เมื่อนำสัญญาณสองตัวอย่าง ($x_1$ และ $x_2$) มาบวกกันใน Pre-Adder: ผลบวกจะมีโอกาสขยายขนาดเพิ่มขึ้น $1$ บิต (Bit Growth) กลายเป็น $17$ บิตแบบคิดเครื่องหมาย
* พอร์ตอินพุต $D$ และ $A$ ของ Hard Pre-Adder ใน DSP48E2 มีขนาดสูงสุดทางกายภาพเท่ากับ $27$ บิต

หากสัญญาณอินพุตจากเซนเซอร์ถูกขยายความละเอียดในอนาคตเป็น $26$ บิตแบบคิดเครื่องหมาย ผลบวกใน Pre-Adder จะเกิดปัญหาบิตล้นพอร์ตหรือไม่ และต้องจัดการอย่างไร?

---

#### ตัวเลือก:
A) ไม่เกิดปัญหา เพราะผลบวก 26 บิตยังคงเป็น 26 บิตเท่าเดิม  
B) เกิดปัญหา เพราะผลบวกของ 26 บิตสองตัวจะขยายเป็น 27 บิต ซึ่งจะเต็มพอร์ต $27$ บิตของตัวคูณพอดี แต่ถ้าอินพุตเดิมมีขนาด 27 บิต ผลบวกจะกลายเป็น 28 บิต ซึ่งจะล้นพอร์ตของ Pre-Adder และทะลักออกสู่ Fabric LUT ทันที  
C) พอร์ต Pre-Adder ขยายขนาดได้อัตโนมัติถึง 48 บิต  
D) ไม่สามารถคำนวณเลขคิดเครื่องหมายใน Pre-Adder ได้

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เกิดปัญหา เพราะผลบวกของ 26 บิตสองตัวจะขยายเป็น 27 บิต ซึ่งจะเต็มพอร์ต $27$ บิตของตัวคูณพอดี แต่ถ้าอินพุตเดิมมีขนาด 27 บิต ผลบวกจะกลายเป็น 28 บิต ซึ่งจะล้นพอร์ตของ Pre-Adder และทะลักออกสู่ Fabric LUT ทันที**

##### การวิเคราะห์ขนาดบิตทางคณิตศาสตร์:
* อินพุต $A$ และ $D$ มีขนาด $N$ บิตแบบคิดเครื่องหมาย:
  $$\text{Max Sum} = (2^{N-1}-1) + (2^{N-1}-1) = 2^N - 2$$
  ซึ่งต้องการพื้นที่จัดเก็บอย่างน้อย $N + 1$ บิต
* ใน DSP48E2 พอร์ตขาเข้า $D$ และ $A$ กว้าง $27$ บิต แต่เส้นทางเอาต์พุตจาก Pre-Adder ส่งเข้าตัวคูณรองรับขนาดสูงสุดเพียง **$27$ บิต** เช่นกัน!
* ดังนั้น หากสัญญาณอินพุตมีขนาดเต็ม $27$ บิต ผลบวกขนาด $28$ บิตจะไม่สามารถส่งเข้าตัวคูณแบบตรงๆ ได้ คอมไพเลอร์จะยอมแพ้และดีดลอจิกพรีแอดเดอร์ออกไปสร้างบน Fabric LUT ทันที
* วิศวกรจึงต้องจำกัดขนาดอินพุต $x$ สำหรับ Symmetric FIR ไว้ที่ **ไม่เกิน $26$ บิต** เสมอ เพื่อให้ผลบวก $27$ บิตบรรจุลงในตัวคูณของ Hard Macro ได้อย่างสมบูรณ์แบบ $100\%$

---

### คำถามที่ 3: ทำไมตัวกรอง Symmetric Linear-Phase FIR จึงไม่มี Phase Distortion?

---

#### ตัวเลือก:
A) เพราะไม่มีตัวเก็บประจุ  
B) เพราะการตอบสนองความถี่ $H(e^{j\omega}) = A(\omega) e^{-j \omega \frac{M-1}{2}}$ มีเฟสเป็นฟังก์ชันเชิงเส้นตรงของความถี่ ทำให้ทุกความถี่ของสัญญาณเดินทางผ่านระบบด้วยความล่าช้า (Delay) เท่ากันเป๊ะ ส่งผลให้รูปคลื่นสัญญาณไม่เกิดการบิดเบี้ยว  
C) เพราะใช้ DSP48E2 เท่านั้น  
D) เพราะค่าสัมประสิทธิ์เป็นศูนย์ทั้งหมด

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เพราะการตอบสนองความถี่ $H(e^{j\omega}) = A(\omega) e^{-j \omega \frac{M-1}{2}}$ มีเฟสเป็นฟังก์ชันเชิงเส้นตรงของความถี่ ทำให้ทุกความถี่ของสัญญาณเดินทางผ่านระบบด้วยความล่าช้า (Delay) เท่ากันเป๊ะ ส่งผลให้รูปคลื่นสัญญาณไม่เกิดการบิดเบี้ยว**

##### คำอธิบายเชิงสัญญาณและระบบ:
เมื่อเฟส $\theta(\omega) = -\omega \cdot \frac{M-1}{2}$ เป็นเส้นตรง:
ค่า Group Delay $\tau_g = -\frac{d\theta}{d\omega} = \frac{M-1}{2}$ จะกลายเป็นค่าคงที่สมบูรณ์!
นั่นหมายความว่า องค์ประกอบความถี่ทุกความถี่ในสัญญาณ (ไม่ว่าจะความถี่ต่ำหรือความถี่สูง) จะถูกหน่วงเวลาเท่ากันหมดเมื่อผ่านฟิลเตอร์ ทำให้รูปทรงคลื่นของสัญญาณ (เช่น พัลส์ของสัญญาณคลื่นหัวใจ หรือ พัลส์ของเรดาร์) ไม่เกิดการบวมเบี้ยวหรือกระจายตัว (Dispersion-Free) ซึ่งตัวกรองแบบ IIR หรือฟิลเตอร์แบบไม่สมมาตรไม่สามารถทำได้
