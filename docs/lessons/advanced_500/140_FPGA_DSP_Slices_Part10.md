# Lesson 140: FPGA DSP Slices Part 10 - Floating Point DSP and Synthesis Pragmas (浮動小数点DSPと論理合成プラグマ: IEEE 754 Single/Double Precision Hard DSP, Synthesis Attributes USE_DSP & Resource Sign-off)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 เลขคณิตจุดลอยตัวมาตรฐาน IEEE 754 บนสถาปัตยกรรม FPGA (IEEE 754 Floating-Point Arithmetic on FPGA)
ในการประมวลผลเชิงวิทยาศาสตร์ (Scientific Computing), การจำลองทางการเงิน (Monte Carlo Financial Modeling), และการควบคุมการบินอวกาศขั้นสูง ช่วงการแสดงค่าของตัวเลข (Dynamic Range) ของระบบจุดคงที่ (Fixed-Point) อาจไม่เพียงพอต่อการรับมือกับค่าที่แปรผันหลายร้อยเท่า มาตรฐาน **IEEE 754 Floating-Point** จึงถูกนำมาใช้:

```
              โครงสร้างมาตรฐาน IEEE 754 Single-Precision (32-bit Float)
   
    1 bit       8 bits                         23 bits (แฝง 1 bit = 24 bits)
   +------+----------------+---------------------------------------------------+
   | Sign | Exponent (E)   | Fraction / Mantissa (M)                           |
   | (s)  | (Bias = 127)   | 1.m_22 m_21 m_20 ... m_0                          |
   +------+----------------+---------------------------------------------------+
   
   สมการค่าจริง: V = (-1)^s · (1 + M) · 2^(E - 127)
   ช่วงค่าตัวเลข: ~ 1.18 x 10^-38 ถึง 3.40 x 10^+38 (กว้างกว่า Fixed-point มหาศาล!)
```

#### 1.1.1 สถาปัตยกรรม Hard Floating-Point vs Soft DSP Emulation
1. **Native Hard Floating-Point DSPs:**
   * ชิปตระกูล **Intel Arria 10 / Stratix 10** และ **AMD Versal AI Core (DSP58)** มีวงจรคูณและบวก IEEE 754 Single-Precision ฝังอยู่ในตัว Hard Macro โดยตรง สามารถคำนวณการคูณและบวกทศนิยม 32 บิตได้ภายใน 1 DSP Slice ที่ความถี่ $> 600\text{ MHz}$
2. **Soft Floating-Point Mapping บน DSP48E2 (UltraScale+):**
   * บล็อก DSP48E2 บน UltraScale+ เป็นเซลล์แบบ Fixed-Point เป็นหลัก ($27 \times 18$ Multiplier)
   * ในการคูณ Mantissa ขนาด $24 \times 24$ บิต: ต้องใช้การแยกส่วนประกอบของตัวคูณ หรือใช้ **DSP48E2 จำนวน 2 ตัว** ร่วมกับ Soft Fabric ในการคำนวณ Exponent Adder และ Normalization Barrel Shifter

$$\text{Mantissa Mult: } 24 \times 24 \text{ bits} \longrightarrow \text{ต้องการ } 2 \text{ DSP48E2 Slices}$$

```
                การแบ่งหน้าที่การคูณ Float 32 บิตบน DSP48E2
   
   Exponent A, B (8-bit) -------> [ Soft LUT Adder & Bias Adjust ] ---> Exponent Out (8-bit)
                                                                             |
   Mantissa A, B (24-bit) ------> [ 2 x DSP48E2 Hard Multiplier ] ----> [ Normalizer ] ---> Mantissa Out
                                  (คำนวณ 24 x 24 บิตด้วย Carry Cascade)  [ Barrel Shifter ]
```

---

### 1.2 การควบคุมคอมไพเลอร์ด้วยคำสั่ง Synthesis Pragmas (`USE_DSP`)
ในการสังเคราะห์วงจรระดับ RTL โปรแกรมอย่าง Vivado มีอัลกอริทึมเดาใจ (Heuristic Algorithm) ในการดึงบล็อก DSP มาใช้งาน หากวิศวกรไม่ระบุคำสั่งควบคุมอย่างชัดเจน ตัวคอมไพเลอร์มักจะสร้างปัญหา 2 ประการ:
1. **DSP Starvation:** วงจรคูณขนาดใหญ่ไม่ยอมลง DSP แต่ทะลักไปกิน LUT จนชิปแน่น
2. **DSP Squandering:** วงจรบวกขนาดเล็ก เช่น ตัวนับแอดเดรส 12 บิต (`addr <= addr + 1;`) กลับถูกคอมไพเลอร์จับยัดลงบล็อก DSP48E2 จนโควตา DSP ของทั้งชิปหมดเกลี้ยง!

#### 1.2.1 รูปแบบการบังคับใช้งานแอตทริบิวต์ `(* use_dsp *)`

```
+------------------------------------+---------------------------------------------------------------+
| ค่าคอนฟิกกูเรชัน                   | พฤติกรรมการสังเคราะห์ของ EDA Tool (Vivado Synthesis Behavior)  |
+------------------------------------+---------------------------------------------------------------+
| `(* use_dsp = "yes" *)`            | **บังคับ 100%:** ต้องแมปลง DSP48E2 เท่านั้น หากทำไม่ได้ให้ฟ้อง Error|
| `(* use_dsp = "no" *)`             | **สั่งห้ามเด็ดขาด:** ห้ามใช้ DSP ให้สร้างบน Soft Fabric LUT เท่านั้น|
| `(* use_dsp = "logic" *)`          | สั่งให้สร้างเฉพาะวงจรบวก/ลบขนาดเล็กบน Fabric เพื่อสงวน DSP ไว้ |
| `(* use_dsp = "auto" *)` (Default) | ให้ Tool ตัดสินใจเองตามขนาดบิต (อันตราย! มักดึงตัวนับลง DSP)  |
+------------------------------------+---------------------------------------------------------------+
```

```systemverilog
// ตัวอย่าง: บังคับให้ตัวนับแอดเดรสอยู่บน Fabric เพื่อสงวน DSP ไว้ให้ตัวคูณ
(* use_dsp = "no" *) logic [15:0] dma_address_counter;
always_ff @(posedge clk) begin
    if (rst_sync) dma_address_counter <= '0;
    else          dma_address_counter <= dma_address_counter + 1'b1;
end
```

---

### 1.3 กระบวนการตรวจสอบและอนุมัติทรัพยากรขั้นสุดท้าย (DSP Resource Sign-off Criteria)
ก่อนส่งมอบบิตสตรีมสู่สายการผลิตจริง วิศวกรอาวุโสจะต้องตรวจสอบรายงานการใช้งานฮาร์ดแวร์ (Utilization & DSP Audit) ตามเกณฑ์มาตรฐานสากล:

```
                      เกณฑ์การประเมิน DSP Resource Sign-off
   
   [ 1. DSP Utilization Threshold ]
   - ต้องไม่เกิน 80 - 85% ของชิปทั้งหมด (เหลือ 15% เผื่อ Routing และ ECO Fix)
   
   [ 2. Zero Fabric Spillover Check ]
   - ตรวจสอบว่าไม่มีตัวคูณความเร็วสูงหลุดไปสร้างบน LUT Fabric
   
   [ 3. Hard Cascade Continuity Check ]
   - สาย PCOUT/PCIN ต้องไม่ถูกตัดขาดข้าม Column หรือข้าม SLR Boundary
   
   [ 4. Full Pipeline Absorption Check ]
   - รีจิสเตอร์ทุกสเตจ (AREG, BREG, MREG, PREG) ต้องมีสถานะเป็น "Absorbed" 100%
```

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Hybrid Fixed/Float Architecture พร้อมการควบคุม Pragmas

```systemverilog
//=============================================================================
// Module: hybrid_precision_dsp_unit.sv
// Description: Multi-Precision DSP Unit with Explicit USE_DSP Pragma Enforcement
// Target: AMD UltraScale+ (Sign-off Compliant Architecture)
//=============================================================================
`timescale 1ns / 1ps

module hybrid_precision_dsp_unit #(
    parameter int DATA_WIDTH = 24
)(
    input  logic                          clk,
    input  logic                          rst_sync,
    input  logic                          calc_en,
    // อินพุตข้อมูลคำนวณหลัก
    input  logic signed [DATA_WIDTH-1:0]  data_a,
    input  logic signed [DATA_WIDTH-1:0]  data_b,
    // อินพุตการเลื่อนแอดเดรสบัฟเฟอร์
    input  logic [15:0]                   buf_offset,
    // เอาต์พุตผลลัพธ์
    output logic signed [2*DATA_WIDTH-1:0] mult_out,
    output logic [15:0]                   target_addr_out
);

    //-------------------------------------------------------------------------
    // 1. Core Multiplication: บังคับแมปปิ้งลง DSP48E2 100%
    //-------------------------------------------------------------------------
    (* use_dsp = "yes" *) logic signed [DATA_WIDTH-1:0]   a_reg;
    (* use_dsp = "yes" *) logic signed [DATA_WIDTH-1:0]   b_reg;
    (* use_dsp = "yes" *) logic signed [2*DATA_WIDTH-1:0] m_reg;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            a_reg    <= '0;
            b_reg    <= '0;
            m_reg    <= '0;
            mult_out <= '0;
        end else if (calc_en) begin
            a_reg    <= data_a;
            b_reg    <= data_b;
            m_reg    <= a_reg * b_reg; // Inferred to Hard DSP48E2
            mult_out <= m_reg;
        end
    end

    //-------------------------------------------------------------------------
    // 2. Address Generation Unit (AGU): สั่งห้ามกิน DSP เด็ดขาด!
    // บังคับให้ตัวบวกแอดเดรสสร้างบน Soft Fabric CARRY8 เท่านั้น
    //-------------------------------------------------------------------------
    (* use_dsp = "no" *) logic [15:0] addr_accum;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            addr_accum      <= '0;
            target_addr_out <= '0;
        end else if (calc_en) begin
            addr_accum      <= addr_accum + buf_offset; // Forced to Fabric LUTs
            target_addr_out <= addr_accum;
        end
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในโครงการพัฒนาระบบคำนวณราคาออปชันทางการเงินแบบจำลองมอนติคาร์โล (Black-Scholes Options Pricing Engine) บนการ์ดเร่งความเร็ว Virtex UltraScale+ FPGA (VU9P ที่มี 6,840 DSP Slices) วิศวกรออกแบบโมดูลคำนวณโดยใช้การจำลองแบบเลขทศนิยม Floating Point ในโค้ด Verilog และไม่ได้ระบุแอตทริบิวต์ควบคุม DSP ใดๆ เลย (ปล่อยให้เป็นดีฟอลต์ `auto`)

**ผลลัพธ์ที่ล้มเหลว:** เมื่อรันขั้นตอน Synthesis การคอมไพล์ล้มเหลวกลางคันด้วยข้อผิดพลาด **`[Place 30-484] Out of DSP resources: Design requires 9,820 DSPs, but device only has 6,840 (Utilization = 143.5%)`** เมื่อเปิดดูรายงานอย่างละเอียด พบว่า คอมไพเลอร์ได้แอบนำตัวนับแอดเดรสขนาด 16 บิต (Address Counters) และวงจรเปรียบเทียบขนาดเล็กของโมดูลนับล้านโมดูลไปสังเคราะห์ลงใน DSP48E2 จนผลาญ DSP ไปกว่า **$4,200\text{ ตัว}$ โดยเปล่าประโยชน์**!

```
                 สาเหตุความล้มเหลวจาก DSP Squandering ในระบบ Black-Scholes
   
   ปล่อยให้ Vivado ตัดสินใจ DSP Mapping แบบ Auto
                         |
                         v
   ตัวคูณหลัก (Floating Point): ใช้ DSP 5,620 ตัว (ตรงตามเป้าหมาย)
   ตัวนับแอดเดรสเล็กๆ (16-bit Counters): ถูก Tool จับยัดลง DSP ไปอีก 4,200 ตัว!
                         |
                         v
   รวมความต้องการ: 9,820 DSP Slices (เกินพิกัดชิป 6,840 ตัว -> Utilization 143%!)
   Place & Route ล้มเหลวทันที -> ไม่สามารถสร้างบิตสตรีมได้!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมขั้นตอนคอมไพล์ของระบบ Black-Scholes ถึงล้มเหลวด้วย Resource Error?**
   * *ตอบ:* จำนวน DSP Slice ที่วงจรต้องการพุ่งสูงถึง $9,820$ ตัว ซึ่งเกินกว่าจำนวนที่มีอยู่จริงในชิป ($6,840$ ตัว)
2. **ทำไมจำนวน DSP Slice ถึงพุ่งสูงเกินความจุของชิปขนาดนั้น?**
   * *ตอบ:* วงจรตัวนับแอดเดรสธรรมดาและตัวบวกขนาดเล็กถูกสังเคราะห์ลงในบล็อก DSP48E2 ทั้งหมด
3. **ทำไมตัวนับขนาดเล็กถึงถูกสังเคราะห์ลงใน DSP48E2?**
   * *ตอบ:* การตั้งค่า Synthesis เป็นแบบ Auto และตรรกะในตัวคอมไพเลอร์มองว่าตัวนับเหล่านั้นมีโครงสร้างคล้าย Accumulator จึงจับแมปลง DSP เพื่อลดการใช้ LUT
4. **ทำไมวิศวกรถึงไม่สั่งห้ามไม่ให้ตัวนับไปแย่งใช้ DSP?**
   * *ตอบ:* วิศวกรไม่ได้ใส่ Synthesis Pragma `(* use_dsp = "no" *)` กำกับไว้เหนือตัวแปรตัวนับ
5. **ทำไมวิศวกรจึงละเลยการใส่ Synthesis Pragmas?**
   * *ตอบ:* วิศวกรขาดความเข้าใจในกลไกของโปรแกรมสังเคราะห์วงจร (Inference Heuristics) และไม่ได้ทำ **การวิเคราะห์แบ่งสรรงบประมาณทรัพยากร (Resource Budgeting Audit)** ในระดับสถาปัตยกรรมก่อนเริ่มเขียนโค้ด!

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ DSP Resource Over-utilization
   
   ความรู้ความเข้าใจเครื่องมือ (Synthesis Heuristics)  การเขียนโค้ด RTL (Pragma Governance)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ไม่เข้าใจกลไก ปล่อยให้ Tool                  ละเลยการใส่    ไม่มีการแยก
   การตัดสินใจ   เดาใจแบบ                       `use_dsp=no`  โมดูลคำนวณ
   ของ Auto DSP  `auto`                         บนตัวนับเล็กๆ ออกจากตัวนับ
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> DSP ล้นบอร์ด 143%
                                                                |     สร้างบิตสตรีมไม่ได้
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   อัลกอริทึม    ชิป VU9P                       ไม่ได้ตรวจสอบ  ขาดกระบวนการ
   Floating Point มีเพดาน 6,840                 Utilization    Resource Sign-off
   ต้องการตัวคูณสูง ตัวจำกัด                     Report ย่อย    ตามเกณฑ์มาตรฐาน
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   ความซับซ้อนของคณิตศาสตร์ (Math Complexity)       การตรวจสอบก่อนคอมไพล์ (Pre-Build Audit)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: กำหนดนโยบาย Pragmas สำหรับตัวนับและแอดเดรส
ในไฟล์ RTL ทุกโมดูล สำหรับตัวนับแอดเดรส (Counters), ตัวชี้คิว FIFO (Pointers), และตัวสร้างสัญญาณคลื่น (State Timers) **ต้องใส่คำสั่งห้ามใช้ DSP อย่างเคร่งครัด**:
```verilog
(* use_dsp = "no" *) reg [N-1:0] address_ptr;
```

#### ขั้นตอนที่ 2: รันคำสั่งตรวจสอบการใช้งาน DSP ตามลำดับชั้น (Hierarchical DSP Audit)
เปิดรายงานหลังการสังเคราะห์ด้วยคำสั่ง Tcl:
```tcl
report_utilization -hierarchical -file post_synth_dsp_audit.rpt
```
ตรวจสอบคอลัมน์ `DSPs` ในทุกโมดูล:
* โมดูลที่เป็น Control Path หรือ Data Buffering: **ต้องมี DSP เป็นศูนย์ (0 DSPs)**
* หากพบว่าโมดูลตัวนับมีการใช้ DSP แม้แต่ตัวเดียว ให้ถือว่าตรวจแบบ **ไม่ผ่าน (Fail)** ทันที!

#### ขั้นตอนที่ 3: ตรวจสอบเพดาน DSP Utilization รวม
ต้องรับประกันว่ายอดการใช้งาน DSP รวมทั้งชิปจะต้อง **ไม่เกิน $80\%$** เพื่อให้เหลือช่องว่างทางกายภาพสำหรับสาย Cascade และการแก้ไขบั๊กฉุกเฉิน (Engineering Change Orders: ECO)

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวรรกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| 浮動小数点演算 | ふどうしょうすうてんえんざん | Fudou Shousuuten Enzan | Floating-Point Arithmetic (IEEE 754) |
| 合成プラグマ | ごうせいぷらぐま | Gousei Puraguma | Synthesis Pragma / Attribute (`USE_DSP`) |
| リソース枯渇障害 | りそーすこかつしょうがい | Risoosu Kokatsu Shougai | Resource Exhaustion Defect |
| カウンタ誤配置 | かうんたごはいち | Kaunta Gohaichi | Counter Mismapping (ตัวนับหลุดลง DSP) |
| 仮数部乗算 | かすうぶじょうざん | Kasuubu Jouzan | Mantissa Multiplication (24x24 bits) |
| 指数部調整 | しすうぶちょうせい | Shisuubu Chousei | Exponent Alignment / Addition |
| バレルシフタ | ばれるしふた | Bareru Shifuta | Barrel Shifter (ตัวเลื่อนบิตปรับสเกล) |
| 階層別リソース監査 | かいそうべつりそーすかんさ | Kaisoubetsu Risoosu Kansa | Hierarchical Resource Audit |
| 専有率制限 | せんゆうりつせいげん | Sen-yuuritsu Seigen | Utilization Cap Limit (80% Rule) |
| 設計承認判定 | せっけいしょうにはんてい | Sekkei Shounin Hantei | Design Sign-off Approval |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** การประชุมสรุปผลการตรวจแบบการ์ดประมวลผลทางการเงินความเร็วสูง (FinTech FPGA Acceleration Sign-off Review)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** คิตามูระ ซัง (Kitamura-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** ฮอนดะ คุง (Honda-kun)

---

**北村技師 (Kitamura):**  
「本田君、このブラック・ショールズ方程式オプション価格計算モジュールの論理合成結果だが、DSP 使用量が 9,820 個で Virtex UltraScale+（上限 6,840 個）の容量を 143% も突破して配置配線がクラッシュしているぞ。階層別リソースレポート（Hierarchical Utilization Report）を精査したところ、各計算パイプラインのアドレスカウンタだけで 4,200 個もの DSP48E2 が食い潰されているが、なぜ `(* use_dsp = "no" *)` を指定しなかったのかね？」  
*(Honda-kun, kono Burakku-Shooruzu houteishiki opushon kakaku keisan mojyuuru no ronri gousei kekka dakedo, DSP shiyouryou ga 9,820-ko de Virtex UltraScale+ (jougen 6,840-ko) no youryou wo 143% mo toppashite haichi haisen ga kurasshu shite iru zo. Kaisoubetsu risoosu repooto (Hierarchical Utilization Report) wo seisa shita tokoro, kaku keisan paipurain no adoresu kaunta dake de 4,200-ko mono DSP48E2 ga kui-tsubusarete iru ga, naze `(* use_dsp = "no" *)` wo shitei shinakatta no kane?)*  
**ความหมาย:** คุณฮอนดะ ผลการสังเคราะห์ของโมดูลคำนวณราคาออปชัน Black-Scholes ตัวนี้ จำนวน DSP ที่เรียกใช้พุ่งไปถึง 9,820 ตัว ทะลุความจุของชิป Virtex UltraScale+ (มีเพดาน 6,840 ตัว) ไปถึง 143% จนขั้นตอน Place & Route พังพินาศเลยนะ พอไปเจาะดูรายงาน Hierarchical Utilization พบว่าเฉพาะตัวนับแอดเดรสของแต่ละไปป์ไลน์แอบกิน DSP48E2 ไปถึง 4,200 ตัว ทำไมถึงไม่ใส่ `(* use_dsp = "no" *)` ดักไว้ครับ?

---

**本田技師 (Honda):**  
「はい、北村さん。Vivado の合成オプションで特に指定しなければ、ツールが最適なリソースを選択してくれるものと過信しておりました。単なる 16 ビットのインクリメント加算器が DSP スライスにマッピングされるとは夢にも思っておりませんでした。」  
*(Hai, Kitamura-san. Vivado no gousei opushon de tokuni shitei shinakereba, tsuuru ga tekisetsu na risoosu wo sentaku shite kureru mono to kashin shite orimashita. Tannaru 16-bitto no inkurimento kasanki ga DSP suraisu ni mappingu sareru to wa yume ni mo omotte orimasen deshita.)*  
**ความหมาย:** ครับคุณคิตามูระ ผมไปเชื่อใจออปชันของ Vivado มากเกินไป คิดว่าถ้าไม่ระบุอะไร Tool จะเลือกทรัพยากรที่เหมาะสมที่สุดให้เองครับ ผมไม่เคยคิดฝันมาก่อนเลยว่าตัวบวกเพิ่มค่า 16 บิตธรรมดาๆ จะถูกนำไปแมปลงใน DSP Slice ได้ครับ

---

**北村技師 (Kitamura):**  
「ツールの自動最適化の癖を知らずに設計するからこういう初歩的な過ちを犯すんだ！Vivado は LUT の消費を抑えるために、レジスタ付きの加算器を見つけると貪欲に DSP48E2 のアキュムレータへ吸い込もうとするヒューリスติกを持っている！制御用のカウンタやポインタにプラグマを付けずに放置すれば、貴重な DSP が安っぽい加算器に食い尽くされるのは当たり前だ！**重大指摘事項とする！** 直ちに全カウンタおよび AGU モジュールに `(* use_dsp = "no" *)` を徹底付与してファブリック CARRY8 へ強制追放し、DSP の総使用量を 5,600 個（占有率 82%）以下に抑えて配置配線を完了させなさい！」  
*(Tsuuru no jidou saitekika no kuse wo shirazu ni sekkei suru kara kou iu shohoteki na ayamachi wo okasunda! Vivado wa LUT no shouhi wo osaeru tame ni, rejisuta-tsuki no kasanki wo mitsukeru to don-yoku ni DSP48E2 no akyumureeta e sui-komou to suru hyuurisutikku wo motte iru! Seigyo-you no kaunta ya pointa ni puraguma wo tsukezu ni houchi sureba, kichou na DSP ga yasuppoi kasanki ni kui-tsukusareru no wa atarimae da! **Juudai shiteki jikou to suru!** Tadachini zen-kaunta oyobi AGU mojyuuru ni `(* use_dsp = "no" *)` wo tettei fuyo shite faburikku CARRY8 e kyousei tsuihou shi, DSP no sou-shiyouryou wo 5,600-ko (sen-yuuritsu 82%) ika ni osaete haichi haisen wo kanryou sasenasai!)*  
**ความหมาย:** ออกแบบงานโดยไม่รู้นิสัยของเครื่องมือถึงได้ทำผิดพลาดเบื้องต้นแบบนี้ไงล่ะ! Vivado มันมีตรรกะเดาใจว่าเพื่อประหยัด LUT ถ้ามันเจอตัวบวกที่มี Register เมื่อไหร่ มันจะตะกละตะกลามฮุบตัวบวกนั้นเข้าไปใน Accumulator ของ DSP48E2 ทันที! ถ้าเธอปล่อยให้ตัวนับควบคุมและตัวชี้ลอยอยู่โดยไม่ใส่ Pragma กักไว้ DSP อันล้ำค่าก็ถูกตัวบวกกระจอกๆ พวกนี้ผลาญจนหมดเกลี้ยงเป็นธรรมดาอยู่แล้ว! **ผมสั่งเป็นข้อแก้ไขระดับวิกฤต!** จงรีบใส่ `(* use_dsp = "no" *)` กำกับตัวนับและโมดูล AGU ทุกตัวอย่างเข้มงวดเพื่อเนรเทศพวกมันกลับไปสร้างบน CARRY8 ใน Fabric เดี๋ยวนี้ โดยต้องกดยอดการใช้ DSP รวมให้เหลือไม่เกิน 5,600 ตัว (ไม่เกิน 82%) และรัน Place & Route ให้ผ่านสมบูรณ์!

---

**本田技師 (Honda):**  
「合成ツールのヒューリスティックによる DSP 浪費の罠を骨身にしみて理解いたしました…！今後は設計初期からプラグマによるリソースガバナンスを徹底いたします。直ちに全カウンタから DSP を追放し、使用率 82% で配置配線がクリーンに通ることを実証して再提出いたします！」  
*(Gousei tsuuru no hyuurisutikku ni yoru DSP rouhi no wana wo honemi ni shimite rikai itashimashita...! Kongo wa sekkei shokiki kara puraguma ni yoru risoosu gabanansu wo tettei itashimasu. Tadachini zen-kaunta kara DSP wo tsuihou shi, shiyouritsu 82% de haichi haisen ga kuriin ni tooru koto wo jisshou shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ผมเข้าใจกับดักการผลาญ DSP จากการเดาของคอมไพเลอร์อย่างลึกซึ้งแล้วครับ...! ต่อไปผมจะควบคุมการจัดสรรทรัพยากรด้วย Pragma อย่างเข้มงวดตั้งแต่เริ่มออกแบบ จะรีบขับไล่ตัวนับทั้งหมดออกจาก DSP และนำผลงานที่มี Utilization 82% พร้อมผลการรัน P&R ที่ผ่านสะอาดมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณจำนวน DSP48E2 ที่ต้องใช้ในการคูณ Mantissa ขนาด 24x24 บิต

ในการประมวลผล Floating-Point IEEE 754 Single-Precision บนชิป UltraScale+ (ซึ่งมี DSP48E2 ขนาดพอร์ตตัวคูณทางกายภาพ $27 \times 18$ บิตแบบคิดเครื่องหมาย):
* ส่วนของ Mantissa มีขนาด $23$ บิต บวกกับบิตนำหน้าโดยนัย (Implicit Leading 1) อีก $1$ บิต รวมเป็นตัวเลขไม่คิดเครื่องหมายขนาด **$24$ บิต** ($A[23:0]$ และ $B[23:0]$)
* ผลคูณ Mantissa ขนาด $24 \times 24$ บิต จะได้ผลลัพธ์ขนาด $48$ บิต

หากทำการแยกบิต $B$ ออกเป็นสองส่วน: $B_{low}[16:0]$ (17 บิต) และ $B_{high}[23:17]$ (7 บิต) เพื่อให้เข้ากับพอร์ต 18 บิตของ DSP48E2:
$$A \times B = A \times (B_{high} \cdot 2^{17} + B_{low}) = (A \times B_{low}) + (A \times B_{high}) \cdot 2^{17}$$

จงคำนวณหาจำนวนบล็อก DSP48E2 ขั้นต่ำที่ต้องใช้ในการคำนวณการคูณ Mantissa ชุดนี้ และระบุว่าสามารถใช้สาย Cascade `PCOUT` เชื่อมต่อเพื่อบวกทบค่า $2^{17}$ ได้หรือไม่?

---

#### ตัวเลือก:
A) ต้องใช้ 1 DSP Slice เพราะ DSP48E2 มีขนาด 48 บิต  
B) ต้องใช้ 2 DSP Slices โดย DSP ตัวที่ 1 คำนวณ $A \times B_{low}$ และ DSP ตัวที่ 2 คำนวณ $A \times B_{high}$ เลื่อนบิตและบวกสะสมผ่านสายทางด่วน Cascade `PCOUT` ได้สมบูรณ์แบบ  
C) ต้องใช้ 4 DSP Slices เพราะขนาด 24 บิตเกินพอร์ต 18 บิตของทั้งสองขา  
D) ไม่สามารถคำนวณ Floating Point บน DSP48E2 ได้

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) ต้องใช้ 2 DSP Slices โดย DSP ตัวที่ 1 คำนวณ $A \times B_{low}$ และ DSP ตัวที่ 2 คำนวณ $A \times B_{high}$ เลื่อนบิตและบวกสะสมผ่านสายทางด่วน Cascade `PCOUT` ได้สมบูรณ์แบบ**

##### ขั้นตอนการวิเคราะห์ขนาดพอร์ต:
1. ขาเข้า $A$ มีขนาด $24$ บิต:
   * พอร์ต $A$ ของ DSP48E2 รองรับขนาดสูงสุด **$27$ บิต** ดังนั้นขนาด 24 บิตจึงสามารถใส่เข้าพอร์ต $A$ ของ DSP ทั้งสองตัวได้โดยตรงโดยไม่ต้องตัดแบ่ง!
2. ขาเข้า $B$ มีขนาด $24$ บิต:
   * พอร์ต $B$ ของ DSP48E2 รองรับขนาดสูงสุดเพียง **$18$ บิต** จึงไม่สามารถใส่ 24 บิตลงในพอร์ต $B$ ช่องเดียวได้
   * จึงต้องแบ่ง $B$ ออกเป็น:
     - ส่วนล่าง: $B_{low} = B[16:0]$ (17 บิต) $\rightarrow$ ใส่พอร์ต $B$ ของ DSP ตัวที่ 1
     - ส่วนบน: $B_{high} = B[23:17]$ (7 บิต) $\rightarrow$ ใส่พอร์ต $B$ ของ DSP ตัวที่ 2
3. การเชื่อมต่อผลลัพธ์:
   * DSP ตัวที่ 1 คำนวณผลคูณขนาด $24 \times 17 = 41$ บิต และส่งออกทาง `PCOUT`
   * DSP ตัวที่ 2 คำนวณ $24 \times 7 = 31$ บิต รับ `PCIN` เข้ามาเลื่อนตำแหน่ง $17$ บิต (`P shifted by 17`) และบวกทบค่าใน ALU 48 บิตได้ในตัวชิปพอดี!

ดังนั้น จึงใช้ DSP48E2 เพียง **$2$ สไลซ์** เท่านั้นในการคำนวณการคูณ Mantissa 24 บิตของ IEEE 754 Single-Precision ได้อย่างสมบูรณ์แบบ

---

### คำถามที่ 2: ผลกระทบของการบังคับ `(* use_dsp = "no" *)` ต่อจำนวน Logic Slices

ในระบบประมวลผลขนาดใหญ่ มีตัวนับขนาด 16 บิตจำนวน $100$ โมดูล:
* หากปล่อยให้สังเคราะห์ลงใน DSP: จะกิน DSP ไปถึง $100$ Slices
* หากใส่แอตทริบิวต์ `(* use_dsp = "no" *)`: ตัวนับทั้งหมดจะถูกบังคับให้สังเคราะห์ลงบน Soft Fabric CARRY8
* ในสถาปัตยกรรม UltraScale+ วงจรบวก Carry Chain 16 บิต (CARRY8 จำนวน 2 ชุด) ใช้ Look-Up Table (LUT6) เฉลี่ยประมาณ $16$ LUTs

การใส่ `use_dsp = "no"` จะทำให้จำนวน LUT6 บนผืน Fabric เพิ่มขึ้นเท่าใด เพื่อแลกกับการกอบกู้ DSP48E2 คืนมา $100$ ตัว?

---

#### ตัวเลือก:
A) เพิ่มขึ้นประมาณ 160 LUTs  
B) เพิ่มขึ้นประมาณ 1,600 LUTs  
C) เพิ่มขึ้นประมาณ 16,000 LUTs  
D) ไม่เพิ่มขึ้นเลยเพราะใช้เกตเดิม

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เพิ่มขึ้นประมาณ 1,600 LUTs**

##### การคำนวณการแลกเปลี่ยนทรัพยากร (Resource Trade-off Formulation):
* ตัวนับ 16 บิต 1 ตัว ใช้ลอจิก LUT บน Fabric:
  $$\text{LUTs per counter} \approx 16 \text{ LUT6}$$
* ตัวนับ 100 ตัว ใช้ LUT รวมทั้งสิ้น:
  $$\text{Total LUTs} = 100 \times 16 = 1,600 \text{ LUT6}$$

##### นัยสำคัญทางวิศวกรรม:
ในชิป Virtex UltraScale+ ที่มี LUT6 มากกว่า $1,000,000$ ตัว การยอมเสีย LUT เพียง $1,600$ ตัว (คิดเป็นไม่ถึง $0.16\%$ ของชิป) เพื่อแลกกับการได้ **DSP48E2 กลับคืนมาถึง 100 ตัว** ถือเป็นการตัดสินใจเชิงสถาปัตยกรรมที่คุ้มค่ามหาศาลและช่วยกอบกู้ให้โปรเจกต์สามารถปิดการคอมไพล์ผ่านได้สำเร็จ!

---

### คำถามที่ 3: กฎเหล็ก 80% DSP Utilization Cap มีขึ้นเพื่อวัตถุประสงค์ใด?

เหตุใดมาตรฐานวิศวกรรมสากลจึงกำหนดว่า ปริมาณการใช้งาน DSP บนชิป FPGA ในขั้นตอนสถาปัตยกรรมจะต้องไม่เกิน $80 - 85\%$ ของจำนวนที่มีอยู่จริงในชิป?

---

#### ตัวเลือก:
A) เพื่อประหยัดภาษีนำเข้าชิป  
B) เพื่อให้เครื่องมือ Place & Route มีพื้นที่ว่างในการจัดวางเซลล์ให้อยู่ใกล้เคียงกัน ลดปัญหา Routing Congestion และเปิดโอกาสให้สายทางด่วน Cascade (`PCOUT/PCIN`) สามารถเชื่อมต่อได้ต่อเนื่องโดยไม่ถูกสิ่งกีดขวางบีบให้ขาดตอน อีกทั้งยังมีพื้นที่สำรองสำหรับการแก้ไขจุดบกพร่องฉุกเฉิน (ECO) ในอนาคต  
C) เพราะ DSP ที่เหลืออีก 20% จะถูกล็อกไว้สำหรับระบบปฏิบัติการ Linux ของ FPGA  
D) เพื่อให้ความถี่ของสัญญาณนาฬิกาเพิ่มขึ้นเป็นสองเท่า

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เพื่อให้เครื่องมือ Place & Route มีพื้นที่ว่างในการจัดวางเซลล์ให้อยู่ใกล้เคียงกัน ลดปัญหา Routing Congestion และเปิดโอกาสให้สายทางด่วน Cascade (PCOUT/PCIN) สามารถเชื่อมต่อได้ต่อเนื่องโดยไม่ถูกสิ่งกีดขวางบีบให้ขาดตอน อีกทั้งยังมีพื้นที่สำรองสำหรับการแก้ไขจุดบกพร่องฉุกเฉิน (ECO) ในอนาคต**

##### เหตุผลทางวิศวกรรมการผลิต:
หากใช้ DSP แน่นเกิน $90 - 95\%$:
1. เครื่องมือ P&R จะถูกบีบให้ต้องกระจาย DSP Slices ข้ามไปอยู่ไกลกัน ส่งผลให้สายเชื่อมต่อยาวขึ้น ความจุสายบวม และ Setup Slack พังทลาย
2. สายทางด่วน Cascade ของฟิลเตอร์จะถูกตัดขาดเนื่องจากคอลัมน์เต็ม
3. หากในขั้นตอนทดสอบหน้างานพบข้อผิดพลาดที่ต้องเพิ่มตัวคูณแม้เพียง 1-2 ตัว ทีมงานจะไม่มีพื้นที่เหลือให้ทำ Engineering Change Order (ECO) และอาจต้องเปลี่ยนเบอร์ชิปทั้งบอร์ด ซึ่งสร้างความเสียหายต่อกำหนดการผลิตอย่างรุนแรง
