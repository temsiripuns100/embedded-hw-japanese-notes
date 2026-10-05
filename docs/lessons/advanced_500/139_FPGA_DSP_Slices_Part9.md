# Lesson 139: FPGA DSP Slices Part 9 - Complex Multiplication Optimization (複素数乗算の最適化: 3-DSP vs 4-DSP Gauss Algorithm, Resource vs Pipeline Balancing, I/Q Modulation)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 แบบจำลองทางคณิตศาสตร์ของการคูณจำนวนเชิงซ้อน (Complex Multiplication Formulations)
ในการประมวลผลสัญญาณแถบความถี่วิทยุ (RF Signal Processing) เช่น การแปลงฟูเรียร์เร็ว (FFT / IFFT), การมอดูเลตสัญญาณ I/Q, และการประมวลผลสัญญาณ MIMO การคูณจำนวนเชิงซ้อนสองจำนวน $(a + jb)$ และ $(c + jd)$ คือการดำเนินการที่มีความถี่ในการเรียกใช้งานสูงสุดในระบบ:

$$(a + jb) \cdot (c + jd) = (ac - bd) + j(ad + bc)$$

โดยที่:
* ส่วนจริง (Real Part): $R = ac - bd$
* ส่วนจินตภาพ (Imaginary Part): $I = ad + bc$

ในการแปลงสมการนี้ลงสู่ฮาร์ดแวร์ FPGA มี 2 แนวทางหลักในประวัติศาสตร์วิศวกรรมคอมพิวเตอร์:

```
                  เปรียบเทียบสถาปัตยกรรมคูณเชิงซ้อน 4-DSP vs 3-DSP
   
   [ 1. สถาปัตยกรรมแบบมาตรฐาน 4-DSP (Direct 4-Multiplier) ]
   - ตัวคูณ 4 ตัว: ac, bd, ad, bc
   - ตัวบวก/ลบ 2 ตัว: (ac - bd), (ad + bc)
   - ใช้ DSP48E2 ทั้งสิ้น = 4 Slices
   - ข้อดี: Pipeline สมดุลสมบูรณ์แบบ 100%, Fmax สูงสุด (> 750 MHz)
   
   [ 2. สถาปัตยกรรมแบบเกาส์ 3-DSP (Gauss's 3-Multiplier Algorithm) ]
   - k1 = c · (a + b)
   - k2 = a · (d - c)
   - k3 = b · (c + d)
   - Real Part = k1 - k3 = ac - bd
   - Imag Part = k1 + k2 = ad + bc
   - ใช้ DSP48E2 ทั้งสิ้น = 3 Slices (ประหยัด DSP ลง 25%!)
   - ความท้าทาย: ต้องจัดสมดุล Pipeline ระหว่าง 3 เส้นทางอย่างระมัดระวัง
```

---

### 1.2 การพิสูจน์ทางคณิตศาสตร์ของอัลกอริทึมเกาส์ (Mathematical Proof of Gauss's Algorithm)
Carl Friedrich Gauss ได้ค้นพบว่า การคูณจำนวนจริงสามารถลดลงจาก 4 ครั้งเหลือเพียง 3 ครั้ง โดยแลกกับการเพิ่มจำนวนการบวก/ลบ:

1. **คำนวณส่วนจริง (Real Part Verification):**
   $$R = k_1 - k_3 = c(a + b) - b(c + d) = ca + cb - bc - bd = ac - bd \quad \text{(ถูกต้องสมบูรณ์)}$$
2. **คำนวณส่วนจินตภาพ (Imaginary Part Verification):**
   $$I = k_1 + k_2 = c(a + b) + a(d - c) = ca + cb + ad - ac = cb + ad = ad + bc \quad \text{(ถูกต้องสมบูรณ์)}$$

#### 1.2.1 การนำ Hard Pre-Adder ของ DSP48E2 มารับมือกับตัวบวกของเกาส์
ในอดีต อัลกอริทึมของเกาส์ไม่เป็นที่นิยมบน FPGA เพราะแม้จะประหยัดตัวคูณได้ 1 ตัว แต่ต้องไปเสีย Soft LUT Fabric เพิ่มขึ้นถึง 3 ตัวเพื่อคำนวณ $(a+b), (d-c),$ และ $(c+d)$

ทว่าในชิปยุคใหม่ที่มี **Hardware Pre-Adder ในตัว DSP48E2**:
* พจน์ $(a + b)$ ถูกคำนวณใน Pre-Adder ของ DSP ตัวที่ 1 ($k_1$)
* พจน์ $(d - c)$ ถูกคำนวณใน Pre-Adder ของ DSP ตัวที่ 2 ($k_2$)
* พจน์ $(c + d)$ ถูกคำนวณใน Pre-Adder ของ DSP ตัวที่ 3 ($k_3$)
* **ผลลัพธ์:** การบวกทั้ง 3 ตัวเกิดขึ้นภายใน Hard Macro ของ DSP โดย **ไม่เสีย Soft LUT บน Fabric แม้แต่ตัวเดียว**! ทำให้สถาปัตยกรรม 3-DSP กลายเป็นทางเลือกทองคำสำหรับการประหยัดทรัพยากรชิป

---

### 1.3 ความท้าทายด้านการจัดสมดุลความหน่วง (Pipeline Balancing Challenge in 3-DSP)
ในขณะที่สถาปัตยกรรม 4-DSP มีความสมมาตรทางเวลาสมบูรณ์แบบ ($ac$ และ $bd$ ใช้เวลาเท่ากันเป๊ะ) ในสถาปัตยกรรม 3-DSP:
* พจน์ $k_1$ ต้องถูกนำไปใช้คำนวณทั้งในส่วนจริง ($k_1 - k_3$) และส่วนจินตภาพ ($k_1 + k_2$)
* สัญญาณอินพุต $c$ ใน $k_1$ เป็นค่าเดี่ยว แต่ใน $k_2$ และ $k_3$ มีการผ่าน Pre-Adder
* หากวิศวกรไม่จัดระดับ Register ให้ตรงกัน สัญญาณส่วนจริงและส่วนจินตภาพจะเกิดอาการ **เฟสเหลื่อมกัน 1 ไซเคิล (1-Cycle Latency Skew)** ซึ่งจะทำลายกลุ่มดาวของสัญญาณ (Constellation Rotation) และทำให้ค่า EVM (Error Vector Magnitude) ของระบบสื่อสารพังทลายทันที!

```
+--------------------+------------------+------------------+---------------------------------------------------+
| สถาปัตยกรรม        | จำนวน DSP        | ความเร็ว $F_{max}$| ความเหมาะสมในการประยุกต์ใช้งาน (Best Use Case)    |
+--------------------+------------------+------------------+---------------------------------------------------+
| 4-DSP Direct       | 4 Slices (100%)  | สูงสุด (> 750MHz)| งานที่เน้นความเร็วสูงสุดระดับ Extreme Performance  |
| 3-DSP Gauss        | 3 Slices (75%)   | สูง (~650-700MHz)| งานที่จำกัดจำนวน DSP เช่น FFT ขนาดใหญ่ 1024-4096pt |
+--------------------+------------------+------------------+---------------------------------------------------+
```

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Balanced Gauss 3-DSP Complex Multiplier

```systemverilog
//=============================================================================
// Module: gauss_3dsp_complex_multiplier.sv
// Description: Fully Pipelined 3-DSP Complex Multiplier using Hard Pre-Adders
// Compliance: 25% DSP Slice Savings with Zero Latency Skew
//=============================================================================
`timescale 1ns / 1ps

module gauss_3dsp_complex_multiplier #(
    parameter int D_W = 16 // ขนาดบิตข้อมูลอินพุต
)(
    input  logic                     clk,
    input  logic                     rst_sync,
    input  logic                     data_valid_in,
    // จำนวนเชิงซ้อนชุดที่ 1: (a + jb)
    input  logic signed [D_W-1:0]    a_re_in,
    input  logic signed [D_W-1:0]    b_im_in,
    // จำนวนเชิงซ้อนชุดที่ 2: (c + jd)
    input  logic signed [D_W-1:0]    c_re_in,
    input  logic signed [D_W-1:0]    d_im_in,
    // ผลลัพธ์จำนวนเชิงซ้อน: (R + jI)
    output logic signed [2*D_W:0]    r_real_out,
    output logic signed [2*D_W:0]    i_imag_out,
    output logic                     data_valid_out
);

    // Stage 1: Input & Pre-Adder Stages
    // DSP 1: k1 = c * (a + b)
    logic signed [D_W:0]     pre_add_1;
    logic signed [D_W-1:0]   c_reg1;
    // DSP 2: k2 = a * (d - c)
    logic signed [D_W:0]     pre_sub_2;
    logic signed [D_W-1:0]   a_reg1;
    // DSP 3: k3 = b * (c + d)
    logic signed [D_W:0]     pre_add_3;
    logic signed [D_W-1:0]   b_reg1;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            pre_add_1 <= '0; c_reg1 <= '0;
            pre_sub_2 <= '0; a_reg1 <= '0;
            pre_add_3 <= '0; b_reg1 <= '0;
        end else begin
            // บรรทัดเหล่านี้จะถูกดูดซับเข้า Hard Pre-Adder ของแต่ละ DSP
            pre_add_1 <= a_re_in + b_im_in;
            c_reg1    <= c_re_in;

            pre_sub_2 <= d_im_in - c_re_in;
            a_reg1    <= a_re_in;

            pre_add_3 <= c_re_in + d_im_in;
            b_reg1    <= b_im_in;
        end
    end

    // Stage 2: Multiplier Stage (MREG)
    logic signed [2*D_W:0] k1_mult, k2_mult, k3_mult;
    logic signed [2*D_W:0] k1_mult_dly; // ดีเลย์ชดเชยเพื่อกระจายไปบวกส่วนจินตภาพ

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            k1_mult     <= '0;
            k2_mult     <= '0;
            k3_mult     <= '0;
            k1_mult_dly <= '0;
        end else begin
            k1_mult     <= pre_add_1 * c_reg1;
            k2_mult     <= pre_sub_2 * a_reg1;
            k3_mult     <= pre_add_3 * b_reg1;
            k1_mult_dly <= k1_mult;
        end
    end

    // Stage 3: Output Adder/Subtractor Stage (PREG)
    // R = k1 - k3, I = k1 + k2
    logic signed [2*D_W:0] real_accum;
    logic signed [2*D_W:0] imag_accum;
    logic [2:0]            valid_pipe;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            real_accum <= '0;
            imag_accum <= '0;
            valid_pipe <= 3'b000;
        end else begin
            real_accum <= k1_mult - k3_mult;
            imag_accum <= k1_mult + k2_mult;
            valid_pipe <= {valid_pipe[1:0], data_valid_in};
        end
    end

    assign r_real_out     = real_accum;
    assign i_imag_out     = imag_accum;
    assign data_valid_out = valid_pipe[2];

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในโครงการพัฒนาโมดูลโมเด็ม Wi-Fi 6 (IEEE 802.11ax 1024-QAM Baseband Processor) บนชิป Artix UltraScale+ FPGA ต้องใช้ตัวคูณเชิงซ้อนจำนวน $96$ ตัวในการคำนวณบัตเตอร์ฟลายของ 64-Point FFT หากใช้โครงสร้างมาตรฐาน 4-DSP จะต้องใช้บล็อก DSP ทั้งสิ้น:

$$N_{dsp} = 96 \times 4 = 384 \text{ DSP Slices}$$

ซึ่งเกินกว่าโควตาทรัพยากรของชิปเบอร์ที่เลือก (ชิปมี DSP เพียง $280$ ตัว) วิศวกรจึงตัดสินใจเปลี่ยนมาใช้อัลกอริทึมเกาส์ 3-DSP เพื่อลดการใช้งานเหลือ $96 \times 3 = 288$ DSPs (และแชร์บางส่วนจนเหลือ 240 ตัว)

**ผลลัพธ์ที่ล้มเหลว:** เมื่อนำบอร์ดไปทดสอบรับสัญญาณแพ็กเก็ต Wi-Fi 6 จริงในห้องแล็บ ปรากฏว่าระบบไม่สามารถถอดรหัสข้อมูลได้เลย ค่าความผิดพลาดของเวกเตอร์สัญญาณ (Error Vector Magnitude: EVM) พังทลายดิ่งลงแตะ **$-12\text{ dB}$** (ในขณะที่มาตรฐาน 1024-QAM ต้องการ EVM ดีกว่า **$-38\text{ dB}$**) กลุ่มดาวสัญญาณ (Constellation Diagram) หมุนวนเป็นวงกลมเหมือนก้นหอย

```
                    หายนะจากการจัดสมดุล Pipeline ผิดพลาดในเกาส์ 3-DSP
   
   [ ปัญหาในโค้ด RTL: ลืมหน่วงเวลาพจน์ k1 ให้ตรงกับ k2 ]
   k1 = c · (a + b)  ------------> คำนวณเสร็จที่รอบ C2
   k2 = a · (d - c)  ------------> คำนวณเสร็จที่รอบ C3 (ผ่าน Pre-subtractor ช้าไป 1 ไซเคิล!)
   
   Real Part = k1[C2] - k3[C3]  <--- นำข้อมูลคนละรอบสัญญาณนาฬิกามาลบกัน!
   Imag Part = k1[C2] + k2[C3]  <--- เฟสของ Real และ Imag ฉีกขาดออกจากกัน 90 องศา!
   
   ผลลัพธ์: กลุ่มดาว 1024-QAM หมุนวนเป็นวงกลม -> EVM พังทลายที่ -12 dB -> หลุดการเชื่อมต่อ!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมโมเด็ม Wi-Fi 6 ถึงถอดรหัสแพ็กเก็ตล้มเหลวและ EVM ดิ่งลงแตะ -12 dB?**
   * *ตอบ:* กลุ่มดาวสัญญาณ (Constellation Points) เกิดการหมุนวนและบิดเบี้ยวจนแยกแยะจุด 1024-QAM ไม่ได้
2. **ทำไมกลุ่มดาวสัญญาณถึงเกิดการหมุนวนและบิดเบี้ยว?**
   * *ตอบ:* เอาต์พุตส่วนจริง (Real) และส่วนจินตภาพ (Imaginary) ของ FFT มีค่าคำนวณที่ผิดพลาดทางคณิตศาสตร์
3. **ทำไมผลลัพธ์การคูณเชิงซ้อนของ FFT ถึงผิดพลาด?**
   * *ตอบ:* วงจรคูณเชิงซ้อนแบบเกาส์ 3-DSP นำผลคูณ $k_1$ จากรอบเวลาหนึ่ง ไปบวกกับ $k_2$ และ $k_3$ ของอีกรอบเวลาหนึ่ง
4. **ทำไมข้อมูลถึงมาจากคนละรอบเวลา (Cycle Mismatch)?**
   * *ตอบ:* พจน์ $k_2$ มีการผ่าน Pre-Adder ที่มีความหน่วง Pipeline 1 สเตจ ในขณะที่พจน์ $k_1$ ส่งค่าอินพุต $c$ เข้าตัวคูณตรงๆ โดยไม่มี Register ชดเชย
5. **ทำไมวิศวกรถึงมองข้ามความไม่สมดุลของความหน่วงเวลานี้?**
   * *ตอบ:* วิศวกรสนใจเพียงแค่การลดจำนวน DSP จาก 4 เหลือ 3 ตัวตามสูตรคณิตศาสตร์ โดยไม่ได้เขียน **Bit-Accurate / Cycle-Accurate Golden Verification Testbench** เพื่อตรวจสอบความถูกต้องเชิงรอบเวลา (Cycle Alignment) ก่อนนำไปใช้งานจริง!

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ Wi-Fi 6 EVM Collapse
   
   การออกแบบสถาปัตยกรรม (Pipeline Balancing)       ขั้นตอนการตรวจสอบ (Verification & Test)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ลืมหน่วงเวลา   เกิด Latency                   ขาด Cycle-     ตรวจเฉพาะผลลัพธ์
   พจน์ k1 ชดเชย  Skew ระหว่าง                  Accurate       สเตติก ไม่ได้รัน
   ในสาย k2/k3    Real และ Imag                 Testbench      สตรีมมิ่งต่อเนื่อง
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> EVM พังทลายที่ -12dB
                                                                |     Wi-Fi 6 ถอดรหัสไม่ได้
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   ต้องการประหยัด ชิป Artix มี                   ไม่ได้รันการ   ขาดการตรวจ
   DSP ลง 25%     DSP จำกัด                     วัด EVM ใน     Constellation
   (จาก 384->288) (มีเพียง 280 ตัว)             ขั้นตอนซิม     Plot ก่อน Release
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   แรงกดดันด้านทรัพยากร (Resource Constraints)     เครื่องมือและการวัดผล (Instrumentation)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ตรวจสอบความลึกของ Pipeline ในทั้ง 3 เส้นทางของเกาส์
ตรวจสอบให้มั่นใจว่าเส้นทางทั้งสามมีจำนวน Register เท่ากันเป๊ะ:
* $\text{Path } k_1: \text{Delay}(a+b) + \text{Delay}(Mult) = 2 \text{ Clocks}$
* $\text{Path } k_2: \text{Delay}(d-c) + \text{Delay}(Mult) = 2 \text{ Clocks}$
* $\text{Path } k_3: \text{Delay}(c+d) + \text{Delay}(Mult) = 2 \text{ Clocks}$

#### ขั้นตอนที่ 2: รันการทดสอบเทียบกับ Golden MATLAB Model แบบ Cycle-by-Cycle
เขียน Testbench ป้อนข้อมูลสตรีมเวกเตอร์ต่อเนื่อง $100,000$ ตัวอย่าง และเปรียบเทียบผลลัพธ์ของ RTL กับ MATLAB:
```systemverilog
assert property (@(posedge clk) (r_real_out == expected_real && i_imag_out == expected_imag))
    else $fatal(1, "[EVM KILLER] Cycle-level mismatch detected! Skew between Real and Imag!");
```

#### ขั้นตอนที่ 3: เลือก 4-DSP สำหรับเส้นทาง Critical Path ความเร็วสูง
หากเส้นทางใดต้องการความถี่เกิน $700\text{ MHz}$ ให้ยอมใช้สถาปัตยกรรม 4-DSP เพื่อรักษาความเร็วและลดความซับซ้อนของท่อ Pipeline

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| 複素数乗算器 | ふくそすうじょうざんき | Fukusosuu Jouzanki | Complex Multiplier |
| ガウスのアルゴリズム | がうすのあるごりずむ | Gausu no Arugorizumu | Gauss's Algorithm (3-Multiplier) |
| コンスタレーション崩壊 | こんすたれーしょんほうかい | Konsutareeshon Houkai | Constellation Collapse / Rotation |
| 変調誤差比 | へんちょうごさひ | Henchou Gosa-hi | Error Vector Magnitude (EVM) |
| パイプライン段差ずれ | ぱいぷらいんだんさづれ | Paipurain Dansa-zure | Pipeline Stage Skew / Misalignment |
| 実部・虚部位相整合 | じつぶ・きょぶいそうせいごう | Jitsubu/Kyobu Isou Seigou | Real/Imag Phase Equalization |
| リソース削減効果 | りそーすさくげんこうか | Risoosu Sakugen Kouka | Resource Reduction Benefit (25%) |
| バタフライ演算器 | ばたふらいえんざんき | Batafurai Enzanki | Butterfly Unit (FFT) |
| ビット精度検証 | びっとせいどけんしょう | Bitto Seido Kenshou | Bit-Accurate Verification |
| 移相歪み | いそうひずみ | Isou Hizumi | Phase Distortion |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** การประชุมตรวจแบบระบบโมเด็มไร้สายความเร็วสูง Wi-Fi 6 (Wi-Fi 6 Baseband Review Meeting)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** คิริชิมะ ซัง (Kirishima-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** อาโอกิ คุง (Aoki-kun)

---

**霧島技師 (Kirishima):**  
「青木君、この Wi-Fi 6 用 1024-QAM FFT モジュールの実機測定結果を見たが、EVM が $-12\text{ dB}$ でコンスタレーションが完全に円形に回転してしまっているぞ。規格の要求値（$-38\text{ dB}$）に遠く及ばない。DSP リソースを削減するためにガウスの 3 乗算器構成を採用したようだが、実部と虚部のパイプライン段数の整合性（Latency Balancing）はどうやって検証したのかね？」  
*(Aoki-kun, kono Wi-Fi 6 you 1024-QAM FFT mojyuuru no jikki sokutei kekka wo mita ga, EVM ga $-12\text{ dB}$ de konsutareeshon ga kanzen ni enkei ni kaiten shite shimatte iru zo. Kikaku no youkyuuchi ($-38\text{ dB}$) ni tooku oyobanai. DSP risoosu wo sakugen suru tame ni Gausu no 3-jouzanki kousei wo saiyou shita you da ga, jitsubu to kyobu no paipurain dansuu no seigousei (Latency Balancing) wa dou yatte kenshou shita no kane?)*  
**ความหมาย:** คุณอาโอกิ ผมดูผลการวัดจริงของโมดูล FFT สำหรับ Wi-Fi 6 1024-QAM ตัวนี้แล้ว พบว่าค่า EVM พังไปอยู่ที่ $-12\text{ dB}$ จนกลุ่มดาวสัญญาณหมุนวนเป็นวงกลมเลยนะ ห่างไกลจากเกณฑ์มาตรฐานที่ต้องการ $-38\text{ dB}$ มาก เพื่อประหยัดทรัพยากร DSP เธอจึงเลือกใช้โครงสร้างเกาส์แบบ 3 ตัวคูณสินะ แต่ไม่ทราบว่าได้ตรวจสอบความสมดุลของความลึก Pipeline ระหว่างส่วนจริงและส่วนจินตภาพไว้อย่างไรบ้างครับ?

---

**青木技師 (Aoki):**  
「はい、霧島さん。Artix の DSP 上限が 280 個しかないため、4 乗算器構成（384 個）では面積オーバーになるためガウスのアルゴリズムへ変更いたしました。シミュレーションでは単一のテストベクタを入力して、計算結果が手計算と一致することを確認しましたので、論理的には完全に正しいはずです。」  
*(Hai, Kirishima-san. Artix no DSP jougen ga 280-ko shika nai tame, 4-jouzanki kousei (384-ko) dewa menseki oobaa ni naru tame Gausu no arugorizumu e henkou itashimashita. Shimyureeshon dewa tan-itsu no tesuto bekuta wo nyuuryoku shite, keisan kekka ga tekeisan to itchi suru koto wo kakunin shimashita node, ronriteki ni wa kanzen ni tadashii hazu desu.)*  
**ความหมาย:** ครับคุณคิริชิมะ เนื่องจากชิป Artix มีเพดาน DSP แค่ 280 ตัว หากใช้แบบ 4 ตัวคูณ (384 ตัว) พื้นที่จะล้นบอร์ด ผมจึงเปลี่ยนมาใช้อัลกอริทึมของเกาส์ครับ ใน Simulation ผมป้อนเวกเตอร์ทดสอบเดี่ยวๆ แล้วเทียบผลลัพธ์ว่าตรงกับการคำนวณด้วยมือแล้วครับ ทางตรรกะมันถูกต้องสมบูรณ์แน่นอนครับ

---

**霧島技師 (Kirishima):**  
「単発のテストしか流さないからパイプラインの段数ズレに気づかないんだ！RTL をよく見てみろ！$k_2$ と $k_3$ はプリ加算器を通るために 1 クロック遅れているのに、$k_1$ の共通項はプリ加算を通らない直接パスから供給されているじゃないか！その結果、実部には『現在の $k_1$』が引かれ、虚部には『1 クロック前の $k_1$』が足し合わされている！実部と虚部の時間軸が 1 クロックずれて直交性が崩壊しているんだ！これではコンスタレーションが回転して通信が途絶するのは当たり前だ！**重大指摘事項とする！** 直ちに $k_1$ パスに遅延補償レジスタを挿入して実部・虚部のレイテンシを完全に一致させ、サイクル単位での等価性を証明しなさい！」  
*(Tanpatsu no tesuto shika nagasanai kara paipurain no dansuu-zure ni kidzukanai nda! RTL wo yoku mite miro! $k_2$ to $k_3$ wa puri kasanki wo tooru tame ni 1-kurokku okurete iru no ni, $k_1$ no kyoutsuukou wa puri kasan wo tooranai chokusetsu pasu kara kyoukyuu sarete iru ja nai ka! Sono kekka, jitsubu ni wa "genzai no $k_1$" ga hikare, kyobu ni wa "1-kurokku mae no $k_1$" ga tashi-awasarete iru! Jitsubu to kyobu no jikanjiku ga 1-kurokku zurete chokukousei ga houkai shite irunda! Kore dewa konsutareeshon ga kaiten shite tsuushin ga tozetsu suru no wa atarimae da! **Juudai shiteki jikou to suru!** Tadachini $k_1$ pasu ni chien hoshou rejisuta wo sounyuu shite jitsubu/kyobu no reitenshi wo kanzen ni itchi sase, saikuru tan-i de no toukasei wo shoumei shinasai!)*  
**ความหมาย:** รันแค่การทดสอบแบบเดี่ยวๆ ถึงไม่รู้ตัวว่าจังหวะของ Pipeline มันเหลื่อมกันน่ะสิ! เธอดูใน RTL ให้ดีๆ! ในขณะที่ $k_2$ และ $k_3$ ต้องวิ่งผ่าน Pre-Adder ทำให้ดีเลย์ไป 1 ไซเคิล แต่พจน์ร่วมของ $k_1$ กลับถูกส่งมาจากเส้นทางตรงที่ไม่ได้ผ่าน Pre-Adder! ผลลัพธ์คือ ส่วนจริงถูกนำไปลบกับ '$k_1$ ของรอบปัจจุบัน' แต่ส่วนจินตภาพกลับถูกนำไปบวกกับ '$k_1$ ของรอบก่อนหน้า'! แกนเวลาของส่วนจริงและจินตภาพเหลื่อมกันไป 1 ไซเคิลจนความเป็นมุมฉาก (Orthogonality) พังทลาย! แบบนี้กลุ่มดาวสัญญาณมันจะไม่หมุนจนสายหลุดได้อย่างไร! **ผมสั่งเป็นข้อแก้ไขระดับวิกฤต!** จงรีบใส่ Register ชดเชยความหน่วงบนเส้นทาง $k_1$ เพื่อให้ Latency ของส่วนจริงและจินตภาพตรงกัน 100% ในระดับรอบสัญญาณนาฬิกาเดี๋ยวนี้!

---

**青木技師 (Aoki):**  
「単発テストでは見抜けない連続ストリーミング時のパイプライン段差ずれ…自らの検証の浅薄さを痛感いたしました…！直ちに $k_1$ パスに遅延補償段を挿入して直交性を完全に復元し、EVM が規格を満たす $-40\text{ dB}$ まで改善したことを実測して再提出いたします！」  
*(Tanpatsu tesuto de wa minukenai renzoku sutoriimingu-ji no paipurain dansa-zure... mizukara no kenshou no senpaku-sa wo tsuukan itashimashita...! Tadachini $k_1$ pasu ni chien hoshou-dan wo sounyuu shite chokukousei wo kanzen ni fukugen shi, EVM ga kikaku wo mitasu $-40\text{ dB}$ made kaizen shita koto wo jissoku shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ความเหลื่อมล้ำของ Pipeline ในช่วงสตรีมมิ่งต่อเนื่องที่ไม่โผล่ให้เห็นในการทดสอบเดี่ยวๆ... ผมตระหนักถึงความตื้นเขินในการตรวจสอบของตัวเองแล้วครับ...! ผมจะรีบใส่สเตจชดเชยบนเส้นทาง $k_1$ เพื่อกู้คืนความเป็นมุมฉากทันที และวัดค่า EVM จริงให้ผ่านเกณฑ์ที่ $-40\text{ dB}$ แล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณการประหยัดทรัพยากร DSP สำหรับ 1024-Point Radix-2 FFT

ในระบบประมวลผลเรดาร์ SAR (Synthetic Aperture Radar) ต้องการสร้างโมดูล 1024-Point Pipelined Radix-2 FFT:
* สถาปัตยกรรม Radix-2 FFT ขนาด $N = 1024$ ประกอบด้วยจำนวนสเตจการคำนวณบัตเตอร์ฟลาย (Butterfly Stages) ทั้งสิ้น: $S = \log_2(1024) = 10$ สเตจ
* ในแต่ละสเตจ ต้องใช้ตัวคูณเชิงซ้อน (Complex Multiplier) เพื่อคูณกับ Twiddle Factor ($W_N^k$) จำนวน $1$ ชุดต่อสเตจในสถาปัตยกรรม Pipelined Streaming (รวม 10 Complex Multipliers)

หากเปรียบเทียบการเลือกใช้:
* **ทางเลือกที่ 1 (Standard 4-DSP Multiplier):** ใช้ 4 DSP ต่อ 1 Complex Multiplier
* **ทางเลือกที่ 2 (Gauss 3-DSP Multiplier):** ใช้ 3 DSP ต่อ 1 Complex Multiplier

จงคำนวณหาจำนวน DSP Slices ทั้งหมดที่ประหยัดได้ในระบบ FFT นี้ และระบุเปอร์เซ็นต์ที่ประหยัดได้?

---

#### ตัวเลือก:
A) ประหยัดได้ 10 DSP Slices ($25.0\%$)  
B) ประหยัดได้ 20 DSP Slices ($50.0\%$)  
C) ประหยัดได้ 40 DSP Slices ($25.0\%$)  
D) ประหยัดได้ 15 DSP Slices ($37.5\%$)

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) ประหยัดได้ 10 DSP Slices ($25.0\%$)**

##### ขั้นตอนที่ 1: คำนวณจำนวน DSP ที่ต้องใช้ในทางเลือกที่ 1
จำนวน Complex Multipliers ทั้งหมด $= 10$ ชุด:
$$N_{dsp1} = 10 \times 4 = 40 \text{ DSP Slices}$$

##### ขั้นตอนที่ 2: คำนวณจำนวน DSP ที่ต้องใช้ในทางเลือกที่ 2
$$N_{dsp2} = 10 \times 3 = 30 \text{ DSP Slices}$$

##### ขั้นตอนที่ 3: คำนวณผลต่างการประหยัดทรัพยากร
$$\Delta N_{dsp} = 40 - 30 = 10 \text{ DSP Slices}$$
$$\% \text{Saved} = \frac{40 - 30}{40} \times 100\% = 25.0\%$$

ในระบบขนานขนาดใหญ่ (เช่น 64-Channel MIMO Beamformer) การประหยัด $25\%$ นี้หมายถึงการประหยัด DSP ได้หลายร้อยตัว ซึ่งสามารถช่วยลดเบอร์ของชิป FPGA จากรุ่นราคาสูงลงมาเป็นรุ่นราคาประหยัด ช่วยประหยัดต้นทุนการผลิตของบอร์ดได้หลายแสนบาทต่อเครื่อง!

---

### คำถามที่ 2: การวิเคราะห์ผลกระทบของ 1-Cycle Latency Skew ต่อเวกเตอร์สัญญาณ I/Q

สมมติให้สัญญาณเข้าสู่ตัวคูณเชิงซ้อนเป็นสัญญาณคลื่นไซน์เชิงซ้อนความถี่คงที่:
$$x[n] = e^{j \omega_0 n} = \cos(\omega_0 n) + j \sin(\omega_0 n)$$
หากวงจรคูณเชิงซ้อนเกิดความผิดพลาดของ Pipeline Skew ทำให้ส่วนจริง (Real) ออกมาช้ากว่าส่วนจินตภาพ (Imag) เป็นเวลา $1$ รอบสัญญาณนาฬิกา ($\Delta t = T_{clk}$):
$$y_{actual}[n] = \text{Real}[n-1] + j \text{Imag}[n]$$

ผลลัพธ์ทางคณิตศาสตร์ของความผิดปกตินี้ต่อรูปคลื่นสัญญาณคือข้อใด?

---

#### ตัวเลือก:
A) สัญญาณยังคงมีความเป็นมุมฉาก (Orthogonal) สมบูรณ์ เพียงแต่แอมพลิจูดลดลงครึ่งหนึ่ง  
B) เกิดความผิดเพี้ยนของเฟสและแอมพลิจูด (I/Q Phase & Amplitude Imbalance) ทำให้ความเป็นมุมฉากระหว่างแกน I และ Q ถูกทำลาย เกิด Image Frequency รั่วไหลในสเปกตรัม และทำให้กลุ่มดาวสัญญาณบิดเบี้ยวจน EVM พังทลาย  
C) ความถี่ของสัญญาณจะเพิ่มขึ้นเป็น 2 เท่า  
D) สัญญาณจะกลายเป็นศูนย์ทั้งหมด

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เกิดความผิดเพี้ยนของเฟสและแอมพลิจูด (I/Q Phase & Amplitude Imbalance) ทำให้ความเป็นมุมฉากระหว่างแกน I และ Q ถูกทำลาย เกิด Image Frequency รั่วไหลในสเปกตรัม และทำให้กลุ่มดาวสัญญาณบิดเบี้ยวจน EVM พังทลาย**

##### คำอธิบายเชิงสัญญาณและระบบสื่อสาร:
ในระบบประมวลผลสัญญาณเชิงซ้อน ความสมบูรณ์ของระบบขึ้นอยู่กับความสัมพันธ์ฉากกัน $90^\circ$ ระหว่างแกน Real (In-Phase) และ Imaginary (Quadrature):
$$\text{Phase}(I) - \text{Phase}(Q) = 90^\circ$$
หากแกน Real ถูกหน่วงเวลาช้าไป 1 ไซเคิล จะเกิดเฟสคลาดเคลื่อนเพิ่มเติม:
$$\Delta \theta = \omega_0 \cdot T_{clk}$$
ความเหลื่อมล้ำของเฟสนี้จะทำลายการหักล้างของ Image Signal ในมิกเซอร์ ทำให้เกิด **Image Leakage (ความถี่เงา)** โผล่ขึ้นมาในสเปกตรัม RF และทำให้จุด Constellation บนระนาบ I/Q หมุนวนและบวมเบี้ยว ส่งผลให้ค่า EVM พังทลายลงสู่ระดับวิกฤตทันที!

---

### คำถามที่ 3: ข้อพิจารณาในการเลือกใช้ระหว่าง 4-DSP Direct vs 3-DSP Gauss

เมื่อใดที่วิศวกรอาวุโสควรเลือกใช้สถาปัตยกรรม **4-DSP Direct** แทนที่จะเป็น 3-DSP Gauss?

---

#### ตัวเลือก:
A) เมื่อระบบต้องการความถี่สัญญาณนาฬิกาสูงสุดระดับ $750 - 800\text{ MHz}$ และมีทรัพยากร DSP บนชิปเหลือเฟือ เพราะ 4-DSP มีโครงสร้างทางเดินสายที่สมมาตรตรงไปตรงมา และมี Logic Depth ต่ำกว่า ทำให้ปิด Timing ได้ง่ายกว่า  
B) เมื่อต้องการประหยัดพลังงานมากที่สุด  
C) เมื่ออินพุตเป็นเลข Floating Point เสมอ  
D) ไม่ควรใช้ 4-DSP เลยในทุกกรณีเพราะล้าสมัยแล้ว

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) เมื่อระบบต้องการความถี่สัญญาณนาฬิกาสูงสุดระดับ 750 - 800 MHz และมีทรัพยากร DSP บนชิปเหลือเฟือ เพราะ 4-DSP มีโครงสร้างทางเดินสายที่สมมาตรตรงไปตรงมา และมี Logic Depth ต่ำกว่า ทำให้ปิด Timing ได้ง่ายกว่า**

##### เหตุผลทางวิศวกรรมการออกแบบ:
วิศวกรที่ดีจะไม่ยึดติดกับสูตรใดสูตรหนึ่ง:
1. หากชิปมี DSP เหลือเฟือ และโจทย์ต้องการความเร็วสูงสุดระดับ **$800\text{ MHz}$**: สถาปัตยกรรม 4-DSP จะให้ประสิทธิภาพเหนือกว่า เพราะแต่ละสไลซ์ทำงานแยกขาดจากกันโดยอิสระ ไร้การพึ่งพากันระหว่างพจน์ (No Cross-term Interdependency) ทำให้เครื่องมือ Place & Route จัดวางเซลล์และปิด Timing ได้ง่ายที่สุด
2. หากชิปมี DSP จำกัด (เช่น แออัดเกิน $85\%$): สถาปัตยกรรม 3-DSP คือคำตอบเดียวที่จะช่วยให้วงจรสามารถบรรจุลงในชิปได้สำเร็จ
