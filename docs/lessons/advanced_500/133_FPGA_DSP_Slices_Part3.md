# Lesson 133: FPGA DSP Slices - Part 3 (Multiply-Accumulate (MAC) & Filtering - Direct Form vs Transposed Form FIR, Systolic Filter Architecture)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 คณิตศาสตร์ของการคอนโวลูชันและสถาปัตยกรรมตัวกรองดิจิทัล (FIR Filtering Mathematics)
สมการพื้นฐานของตัวกรองตอบสนองสัญญาณพัลส์แบบมีขอบเขต (Finite Impulse Response: FIR Filter) ในโดเมนเวลาไม่ต่อเนื่องคือการคำนวณผลรวมของการคอนโวลูชัน (Discrete Linear Convolution):

$$y[n] = \sum_{k=0}^{M-1} h[k] \cdot x[n-k] = h[0]x[n] + h[1]x[n-1] + h[2]x[n-2] + \dots + h[M-1]x[n-M+1]$$

โดยที่:
* $x[n]$ คือ สัญญาณอินพุตในเวลาจริง (Input Samples)
* $h[k]$ คือ ชุดสัมประสิทธิ์ของฟิลเตอร์จำนวน $M$ ค่า (Filter Coefficients / Taps)
* $y[n]$ คือ สัญญาณเอาต์พุตที่ผ่านการกรองแล้ว (Filtered Output)

ในการแปลงสมการคณิตศาสตร์นี้ให้กลายเป็นวงจรฮาร์ดแวร์จริงบน FPGA มี 3 สถาปัตยกรรมหลักที่วิศวกรต้องเผชิญ:

```
                   เปรียบเทียบสถาปัตยกรรมตัวกรอง FIR 3 รูปแบบ
   
   [ 1. Direct Form FIR: ติดคอขวดที่ Adder Tree ]
   x[n] --->|z^-1|--->|z^-1|--->|z^-1|
              |         |         |
              v         v         v
            (*)h0     (*)h1     (*)h2
              \         |         /
               v        v        v
              [   Big Adder Tree   ] ---------> y[n] (Logic Depth ลึกมาก ปิด Timing ยาก!)
   
   [ 2. Transposed Form FIR: ติดคอขวดที่ High Fan-out ]
   x[n] ----+------------+------------+ (เส้นนี้ขับขนานทุกตัวคูณ -> Fan-out สูงมาก!)
            |            |            |
            v            v            v
          (*)h0        (*)h1        (*)h2
            |            |            |
            v            v            v
          (+)-------->[|z^-1|]----->[|z^-1|]---> y[n]
   
   [ 3. Systolic Form FIR: มาตรฐานสากลระดับสูงสุด (Zero Soft LUT, Max Fmax) ]
   x[n] --->[|z^-2|]--------------------->[|z^-2|]---------------------> Pipelined Data
               |                             |
               v                             v
           [DSP #0: (*)h0]               [DSP #1: (*)h1]
               |                             |
               +--- PCOUT === PCIN Dedicated Cascade Path ===> y[n] (750MHz+ ไร้สาย Fabric!)
```

---

### 1.2 ข้อจำกัดทางฟิสิกส์ของ Direct Form และ Transposed Form

#### 1.2.1 ปัญหาคอขวดของ Direct Form (Adder Tree Bottleneck)
ใน Direct Form สัญญาณอินพุตจะวิ่งผ่าน Shift Register แบบหน่วงเวลา $z^{-1}$ แต่ผลคูณของทุก Tap ($M$ ตัว) จะต้องถูกนำมาบวกทบรวมกันในไซเคิลเดียว:
* หาก $M = 128$ Taps: จะต้องใช้วงจรบวกที่มีขนาดต้นไม้ลอจิก (Adder Tree Depth) สูงถึง:
  $$\text{Tree Levels} = \lceil \log_2 128 \rceil = 7 \text{ ระดับ}$$
* การบวก 7 ระดับบน Fabric LUT จะกินเวลาหน่วงมากกว่า $3.5 - 5.0\text{ ns}$ ทำให้ไม่สามารถทำงานที่ความถี่เกินกว่า $200\text{ MHz}$ ได้เลย เว้นแต่จะยอมใส่ Pipeline คั่นทุกชั้น ซึ่งจะผลาญพื้นที่ Register มหาศาล

#### 1.2.2 ปัญหาความแออัดของ Transposed Form (Broadcast Net Congestion)
ใน Transposed Form การบวกถูกกระจายไปอยู่ในแต่ละสเตจหลังตัวคูณ ทำให้ไม่มี Adder Tree แต่กลับเกิดปัญหาใหม่:
* สายสัญญาณอินพุต $x[n]$ จะต้องถูกส่งกระจาย (Broadcast) ไปยังตัวคูณของทุกๆ Tap พร้อมกัน
* หากฟิลเตอร์มีขนาด 128 Taps สายเส้นนี้จะมี **Fan-out สูงถึง 128 โหลด** ทอดข้ามคอลัมน์ DSP หลายมิลลิเมตร ก่อให้เกิด Wire Delay และ Clock Skew มหาศาล

---

### 1.3 สถาปัตยกรรมซิสโตลิก (Systolic FIR Architecture - The Golden Benchmark)
ทางออกที่ดีที่สุดที่ได้รับการยอมรับในอุตสาหกรรมชิปความเร็วสูงคือ **Systolic FIR Filter**:
1. ทั้งสายสัญญาณข้อมูล $x[n]$ และสายบวกสะสม $y[n]$ จะถูกกั้นด้วย Register ทุกสเตจ
2. สัญญาณข้อมูล $x[n]$ จะถูกหน่วงเวลา $2$ ไซเคิล ($z^{-2}$) ก่อนส่งต่อไปยัง Tap ถัดไป (โดยใช้ `AREG = 2` ในตัว DSP48E2)
3. สัญญาณสะสมจะเดินทางไปข้างหน้าทีละ $1$ ไซเคิล ($z^{-1}$) ผ่านทาง **Dedicated Cascade Bus (`PCOUT` $\rightarrow$ `PCIN`)** ภายในคอลัมน์ของ Hard DSP โดยตรง!

$$\text{Tap}_k \text{ Output}: P_k = P_{k-1} + (x[n - 2k] \cdot h[k])$$

* **ข้อได้เปรียบระดับสุดยอด:**
  - ไม่ใช้ Soft LUT Fabric ภายนอกแม้แต่ตัวเดียว (Zero Fabric LUTs for Addition)
  - ไม่มีการลากสายยาวข้ามชิป สายทางด่วน `PCOUT` $\rightarrow$ `PCIN` เป็นสายโลหะเฉพาะกิจความเร็วสูงระดับ sub-nanosecond
  - ทำความเร็วแตะขีดจำกัดสูงสุดของซิลิคอน ($> 741\text{ MHz}$) ได้อย่างง่ายดาย

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Systolic FIR Filter Cascade Chain

```systemverilog
//=============================================================================
// Module: systolic_fir_tap.sv
// Description: Single Tap of Ultra-High-Speed Systolic FIR Filter using DSP48E2
// Target: AMD UltraScale+ (Target Fmax: 750MHz)
//=============================================================================
`timescale 1ns / 1ps

module systolic_fir_tap #(
    parameter bit IS_FIRST_TAP = 1'b0,
    parameter int DATA_WIDTH   = 18,
    parameter int COEFF_WIDTH  = 18,
    parameter int ACCUM_WIDTH  = 48
)(
    input  logic                          clk,
    input  logic                          rst_sync,
    // อินพุตข้อมูลที่ถูกหน่วงแบบ Systolic (2-stage delay)
    input  logic signed [DATA_WIDTH-1:0]  data_in,
    output logic signed [DATA_WIDTH-1:0]  data_out,
    // สัมประสิทธิ์ประจำ Tap
    input  logic signed [COEFF_WIDTH-1:0] coeff_in,
    // ทางด่วน Hard Cascade Interconnect
    input  logic signed [ACCUM_WIDTH-1:0] pcin,
    output logic signed [ACCUM_WIDTH-1:0] pcout
);

    // Stage 1: Data Delay Line (AREG = 2 เพื่อให้ตรงกับจังหวะ Systolic)
    logic signed [DATA_WIDTH-1:0] data_pipe1, data_pipe2;
    logic signed [COEFF_WIDTH-1:0] coeff_pipe;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            data_pipe1 <= '0;
            data_pipe2 <= '0;
            coeff_pipe <= '0;
        end else begin
            data_pipe1 <= data_in;
            data_pipe2 <= data_pipe1; // 2 clocks delay per tap
            coeff_pipe <= coeff_in;
        end
    end

    assign data_out = data_pipe2; // ส่งต่อให้ Tap ถัดไป

    // Stage 2: Multiplier Stage (MREG)
    logic signed [35:0] mult_reg;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            mult_reg <= '0;
        end else begin
            mult_reg <= data_pipe1 * coeff_pipe;
        end
    end

    // Stage 3: Accumulation Stage with Cascade In (PREG)
    // บวกผลคูณเข้ากับผลรวมที่ส่งต่อมาจาก Tap ก่อนหน้าผ่าน PCIN
    logic signed [ACCUM_WIDTH-1:0] p_accum_reg;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            p_accum_reg <= '0;
        end else begin
            if (IS_FIRST_TAP) begin
                p_accum_reg <= mult_reg;       // Tap แรกไม่มี PCIN
            end else begin
                p_accum_reg <= mult_reg + pcin; // ใช้ Hard Cascade Adder
            end
        end
    end

    assign pcout = p_accum_reg; // ขับตรงเข้าสาย PCOUT

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในโครงการพัฒนาโมดูลประมวลผลสัญญาณช่องสัญญาณดาวเทียม (Satellite Polyphase Channelizer) ขนาด 128-Tap FIR บนชิป Virtex UltraScale+ FPGA กำหนดความถี่สัญญาณนาฬิกา $f_{clk} = 500\text{ MHz}$ ($T_{clk} = 2.000\text{ ns}$) วิศวกรออกแบบฟิลเตอร์ด้วยวิธี Direct Form โดยสร้างวงจร Adder Tree บนโค้ด RTL เพื่อรวมผลลัพธ์ของ DSP Slice ทั้ง 128 ตัว

**ผลลัพธ์ที่ล้มเหลว:** รายงาน Vivado Timing แจ้งเตือนความล้มเหลวรุนแรง: $WNS = -1.850\text{ ns}$ และเปลืองพื้นที่ไปกว่า $1,800\text{ LUTs}$ วิศวกรจึงตกใจเปลี่ยนโครงสร้างแบบฉุกเฉินเป็น Transposed Form แต่กลับพบว่าสัญญาณนาฬิกา $500\text{ MHz}$ ยังคงพังทลายด้วย $WNS = -0.740\text{ ns}$ เนื่องจากสัญญาณอินพุต $x[n]$ แตกกิ่งขับโหลดตัวคูณ 128 จุด (Fan-out = 128) เกิดปัญหา Routing Congestion สีแดงเข้มตลอดทั้งแนวดิ่งของชิป

```
              ความล้มเหลวของ Direct Form และ Transposed Form ในงานจริง
   
   [ ความพยายามครั้งที่ 1: Direct Form ]
   128 DSP Multipliers ---> [ 1,800 Soft LUT Adder Tree ] ---> Setup Violation WNS = -1.85ns!
   
   [ ความพยายามครั้งที่ 2: Transposed Form ]
   Input x[n] (Fan-out = 128) === สายไฟยาวพาดข้าม 4 คอลัมน์ ===> Routing Skew WNS = -0.74ns!
   
   [ การแก้ปัญหาที่ถูกต้อง: Systolic Cascade Form ]
   Data (Pipelined z^-2) ----> [DSP] === PCOUT ===> [DSP] === PCOUT ===> WNS = +0.32ns (PASS!)
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมตัวกรอง 128-Tap FIR ถึงปิด Timing ไม่ลงที่ 500 MHz ทั้งสองรอบ?**
   * *ตอบ:* รอบแรกติดปัญหาความล่าช้าของเกตบวกในลูป (Logic Depth) รอบสองติดปัญหาความล่าช้าของการกระจายสายสัญญาณ (Net Delay จาก High Fan-out)
2. **ทำไมรอบแรกถึงมี Logic Depth ลึกเกินไป?**
   * *ตอบ:* วิศวกรใช้ Direct Form ทำให้ต้องสร้างโครงสร้าง Adder Tree สูงถึง 7 ระดับเพื่อบวกผลคูณ 128 ตัวเข้าด้วยกัน
3. **ทำไมรอบสองถึงติดปัญหา High Fan-out?**
   * *ตอบ:* วิศวกรเปลี่ยนเป็น Transposed Form ซึ่งบังคับให้สัญญาณอินพุตตัวอย่างต้องต่อตรงเข้าตัวคูณทั้ง 128 ตัวพร้อมกัน
4. **ทำไมวิศวกรถึงไม่ใช้สายทางด่วน Cascade ของ DSP ตั้งแต่แรก?**
   * *ตอบ:* วิศวกรไม่คุ้นเคยกับ **สถาปัตยกรรมซิสโตลิก (Systolic Architecture)** และเข้าใจว่าการต่อฟิลเตอร์มีแค่ Direct Form และ Transposed Form ตามตำราเรียนทั่วไป
5. **ทำไมสายทางด่วน Cascade ถึงแก้ปัญหานี้ได้อย่างสมบูรณ์แบบ?**
   * *ตอบ:* สาย Cascade (`PCOUT/PCIN`) เชื่อมต่อระหว่าง DSP Slice ที่อยู่ติดกันในแนวดิ่งโดยใช้สายโลหะเฉพาะในซิลิคอน ไม่ต้องผ่านผืน Fabric และตัดปัญหาทั้ง Adder Tree และ High Fan-out ออกไป $100\%$

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของตัวกรอง 128-Tap FIR
   
   การเลือกสถาปัตยกรรม (Architecture Selection)   การจัดการสัญญาณ Fan-out (Signal Fan-out)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ใช้ Direct     เปลี่ยนไปใช้                  สาย Input     ไม่มีการแทรก
   Form ที่มี    Transposed Form               กระจายขับ      Pipeline Tree
   Adder Tree    ที่ติด High Fanout            128 โหลด       ในการกระจายข้อมูล
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> WNS ติดลบ -0.74ns
                                                                |     ตัวกรองดาวเทียมล้มเหลว
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   ไม่ใช้สาย      ไม่เปิดใช้                     LUT 1,800 ตัว  ขาดการคำนวณ
   Hard Cascade   AREG = 2                     แย่งพื้นที่และ   Routing Congestion
   PCOUT/PCIN     ทำ Systolic Delay            สร้างความแออัด ก่อนเขียน RTL
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   การใช้ประโยชน์จากฮาร์ดแวร์ (Silicon Hard Macro)   การวางแผนทรัพยากร (Resource Budgeting)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: บังคับใช้สถาปัตยกรรม Systolic FIR เมื่อ Tap เกิน 32 Taps
สำหรับฟิลเตอร์ความเร็วสูง ($f_{clk} \ge 300\text{ MHz}$) หากมีจำนวน Tap เกิน 32 Taps **ห้ามใช้ Direct Form หรือ Transposed Form เด็ดขาด** ให้เขียนเป็น Systolic FIR Chain เท่านั้น

#### ขั้นตอนที่ 2: เชื่อมต่อพอร์ต `PCOUT` เข้ากับ `PCIN` ระหว่าง Tap ที่ติดกัน
```systemverilog
// กฎเหล็ก: เชื่อมต่อ Cascade Bus ในระดับ Primitive หรือ Inference
assign dsp_inst[i].pcin = dsp_inst[i-1].pcout;
```

#### ขั้นตอนที่ 3: ตรวจสอบรายงาน Floorplan และ Placement ใน Vivado
เปิด Device View และยืนยันว่า DSP Slices ทั้งหมดถูกจัดวางเรียงเป็น **เสาคอลัมน์แนวตั้ง (Single Vertical DSP Column)** ติดกัน เพื่อให้สายสัญญาณ Cascade ทำงานได้อย่างสมบูรณ์แบบโดยไม่ต้องเลี้ยวออกสู่ Fabric

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| シストリック構造 | しすとりっくこうぞう | Shisutorikku Kouzou | Systolic Architecture (สถาปัตยกรรมซิสโตลิก) |
| 直接型フィルタ | ちょくせつがたふぃるた | Chokusetsu-gata Firuta | Direct Form Filter |
| 転置型フィルタ | てんちがたふぃるた | Tenchi-gata Firuta | Transposed Form Filter |
| 加算器ツリー | かさんきつりー | Kasanki Tsurii | Adder Tree |
| 高ファンアウト配線 | こうふぁんあうとはいせん | Kou-fan-auto Haisen | High Fan-out Net |
| カスケード専用配線 | かすけーどせんようはいせん | Kasukeedo Sen-you Haisen | Dedicated Cascade Interconnect (`PCIN/PCOUT`) |
| 遅延整合 | ちえんせいごう | Chien Seigou | Latency Matching / Balancing |
| 列配置制約 | れつはいちせいやく | Retsu Haichi Seiyaku | Column Placement Constraint |
| 演算精度確保 | えんざんせいどかくほ | Enzan Seido Kakuho | Arithmetic Precision Assurance |
| 帯域通過阻止 | たいいきつうかそし | Taiiki Tsuuka Soshi | Stopband Attenuation |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** ห้องประชุมวิศวกรรมดาวเทียมสื่อสารความเร็วสูง (Satellite DSP Hardware Review)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** คุโด ซัง (Kudo-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** อิโนะอุเอะ คุง (Inoue-kun)

---

**工藤技師 (Kudo):**  
「井上君、この 128 タップの衛星ポリフェーズフィルタだが、500MHz でのタイミングが全く収束していないね。最初は直接型（Direct Form）で書いて巨大な加算器ツリーで破綻し、次に転置型（Transposed Form）へ逃げたようだが、今度は入力信号のファンアウトが 128 に跳ね上がって配線遅延で全滅している。なぜ最初からシストリック（Systolic）構造を採用しなかったのかね？」  
*(Inoue-kun, kono 128-tappu no eisei porifeezu firuta dakedo, 500MHz de no taimingu ga mattaku shuusoku shite inai ne. Saisho wa chokusetsugata (Direct Form) de kaite kyodai na kasanki tsurii de hatan shi, tsugi ni tenchigata (Transposed Form) e nigeta you da ga, kondo wa nyuuryoku shingou no fan-auto ga 128 ni haneagatte haisen chien de zenmetsu shite iru. Naze saisho kara shisutorikku (Systolic) kouzou wo saiyou shinakatta no kane?)*  
**ความหมาย:** คุณอิโนะอุเอะ ตัวกรอง Polyphase 128 Tap สำหรับดาวเทียมตัวนี้ ค่า Timing ที่ 500MHz ปิดไม่ลงเลยนะ ตอนแรกเขียนแบบ Direct Form จนเกิด Adder Tree ขนาดยักษ์แล้วพัง พอหนีไปใช้ Transposed Form คราวนี้ Fan-out ของสัญญาณอินพุตก็พุ่งทะลุ 128 โหลดจนพังจากความหน่วงสายไฟอีก ทำไมตั้งแต่แรกถึงไม่เลือกใช้โครงสร้างแบบ Systolic ครับ?

---

**井上技師 (Inoue):**  
「はい、工藤さん。教科書には転置型が最も高速であると記載されていたため、加算器ツリーをなくせば 500MHz を達成できると確信しておりました。しかし 128 個もの乗算器に同一信号を分配する配線スキューがこれほど致命的になるとは予測できませんでした。シストリック構造はデータの遅延合わせが複雑に見えたため敬遠しておりました。」  
*(Hai, Kudo-san. Kyoukasho ni wa tenchigata ga mottomo kousoku de aru to kisai sarete ita tame, kasanki tsurii wo nakuseba 500MHz wo tassei dekiru to kakushin shite orimashita. Shikashi 128-ko mono jouzanki ni douitsu shingou wo bunpai suru haisen skyuu ga kore hodo chimeiteki ni naru to wa yosoku dekimasen deshita. Shisutorikku kouzou wa deeta no chien-awase ga fukuzatsu ni mieta tame keien shite orimashita.)*  
**ความหมาย:** ครับคุณคุโด ในตำราบอกไว้ว่า Transposed Form เร็วที่สุด ผมจึงมั่นใจว่าถ้าตัด Adder Tree ออกไปได้ก็จะวิ่งได้ 500MHz ครับ แต่ผมคาดไม่ถึงเลยว่าการส่งสัญญาณเดียวกันไปให้ตัวคูณถึง 128 ตัวจะเกิด Routing Skew ที่ร้ายแรงขนาดนี้ ส่วนโครงสร้างแบบ Systolic นั้น มันดูซับซ้อนเรื่องการจัดสมดุลความหน่วงของข้อมูล ผมเลยหลีกเลี่ยงไปครับ

---

**工藤技師 (Kudo):**  
「現場の実機 FPGA を見ずに机上の理論だけで逃げるな！UltraScale+ の DSP48E2 には、スライス同士を直結する 48 ビットの専用高速カスケード配線（`PCOUT/PCIN`）が垂直方向に完備されているんだ！シストリック構造を用いれば、加算器ツリーはゼロになり、入力データも各段で 2 クロックずつ遅延パイプライン（`AREG=2`）されるため、ファンアウトは常に『1』に抑えられる！配線遅延など微塵も恐れる必要がなくなるんだ。**直ちに設計是正を命じる！** 全 128 タップを `PCOUT` 直結のシストリック FIR 構成へ全面改修し、ファブリック LUT 使用量ゼロ、WNS プラス収束を達成しなさい！」  
*(Genba no jikki FPGA wo mizu ni kijou no riron dake de nigeru na! UltraScale+ no DSP48E2 ni wa, suraisu doushi wo chokketsu suru 48-bitto no sen-you kousoku kasukeedo haisen (`PCOUT/PCIN`) ga suichoku houkou ni kanbi sarete irunda! Shisutorikku kouzou wo mochiireba, kasanki tsurii wa zero ni nari, nyuuryoku deeta mo kakudan de 2-kurokku zutsu chien paipurain (`AREG=2`) sareru tame, fan-auto wa tsuneni "1" ni osaerareru! Haisen chien nado mijin mo osoreru hitsuyou ga nakunarunda. **Tadachini sekkei zeisei wo meijiru!** Zen 128-tappu wo `PCOUT` chokketsu no shisutorikku FIR kousei e zenmen kaishuu shi, faburikku LUT shiyouryou zero, WNS purasu shuusoku wo tassei shinasai!)*  
**ความหมาย:** อย่าเอาทฤษฎีบนโต๊ะมาอ้างเพื่อหนีความจริงของฮาร์ดแวร์ FPGA สิ! ใน DSP48E2 ของ UltraScale+ มันมีสายทางด่วน Cascade 48 บิต (`PCOUT/PCIN`) ที่เชื่อมต่อระหว่าง Slice ในแนวดิ่งเตรียมไว้อย่างสมบูรณ์แบบอยู่แล้ว! ถ้าใช้สถาปัตยกรรม Systolic วงจร Adder Tree จะกลายเป็นศูนย์ และข้อมูลขาเข้าก็จะถูกไปป์ไลน์หน่วงทีละ 2 ไซเคิลในแต่ละสเตจ (`AREG=2`) ทำให้ Fan-out มีค่าเป็น '1' เสมอ! เรื่องความหน่วงสายไฟจะไม่ใช่สิ่งที่ต้องกังวลอีกต่อไป **ผมขอสั่งให้แก้ไขแบบทันที!** จงรื้อทั้ง 128 Tap มาทำเป็น Systolic FIR ที่เชื่อมด้วย `PCOUT` ให้หมด โดยต้องใช้ Fabric LUT เป็นศูนย์ และปิดค่า WNS ให้เป็นบวกเดี๋ยวนี้!

---

**井上技師 (Inoue):**  
「専用カスケード配線と AREG2 を活かしたシストリック構成の真価を理解いたしました…！加算器ツリーの排除とファンアウト 1 の両立こそが 500MHz 超の世界における唯一の正解ですね。直ちにシストリック構成へ書き直し、750MHz 動作限界までマージンを稼いで再提出いたします！」  
*(Sen-you kasukeedo haisen to AREG2 wo ikashita shisutorikku kousei no shinka wo rikai itashimashita...! Kasanki tsurii no haijo to fan-auto 1 no ryouritsu koso ga 500MHz-chou no sekai ni okeru yuiitsu no seikai desu ne. Tadachini shisutorikku kousei e kakinaoshi, 750MHz dousa genkai made maajin wo kaseide sai-teishutsu itashimasu!)*  
**ความหมาย:** ผมเข้าใจคุณค่าที่แท้จริงของการนำ Cascade และ AREG2 มาทำ Systolic แล้วครับ...! การกำจัด Adder Tree ควบคู่กับการคงค่า Fan-out เป็น 1 คือหนทางที่ถูกต้องเพียงหนึ่งเดียวในย่านเกิน 500MHz จริงๆ ครับ ผมจะรีบแก้เป็นโครงสร้าง Systolic และดึง Margin ให้รองรับได้ถึง 750MHz แล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณ Latency และ Delay Matching ในตัวกรอง Systolic FIR

พิจารณาตัวกรอง Systolic FIR ขนาด $M = 32$ Taps:
* ข้อมูลนำเข้า $x[n]$ เดินทางผ่านไปป์ไลน์สเตจละ $2$ รอบสัญญาณนาฬิกา ($z^{-2}$) เพื่อส่งต่อไปยัง Tap ถัดไป
* สายสัญญาณสะสม Cascade (`PCOUT` $\rightarrow$ `PCIN`) เดินทางไปข้างหน้าสเตจละ $1$ รอบสัญญาณนาฬิกา ($z^{-1}$)
* ตัวกรอง Tap ที่ $0$ (Tap แรก) มี Latency ภายใน DSP เท่ากับ $3$ รอบสัญญาณนาฬิกา (`AREG=1, MREG=1, PREG=1`)

จงคำนวณหาความล่าช้าของผลลัพธ์แรก (Total Latency to First Valid Output Sample) นับจากวินาทีที่ตัวอย่าง $x[0]$ เข้าสู่ระบบ จนกระทั่งผลลัพธ์ $y[0]$ ออกจาก Tap สุดท้าย (Tap ที่ 31) ในหน่วย **รอบสัญญาณนาฬิกา (Clock Cycles)**?

---

#### ตัวเลือก:
A) $32$ รอบสัญญาณนาฬิกา  
B) $34$ รอบสัญญาณนาฬิกา  
C) $65$ รอบสัญญาณนาฬิกา  
D) $96$ รอบสัญญาณนาฬิกา

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) $34$ รอบสัญญาณนาฬิกา**

##### ขั้นตอนการวิเคราะห์แกนเวลาของ Systolic Architecture:
1. **การเดินทางของข้อมูลในตัวกรองแรก (Tap 0):**
   * ตัวอย่าง $x[0]$ เข้าสู่ DSP ตัวแรก:
   * ผ่าน `AREG` ($1$ คาบ) $\rightarrow$ ผ่าน `MREG` ($1$ คาบ) $\rightarrow$ ผ่าน `PREG` ($1$ คาบ)
   * ผลลัพธ์ $h[0] \cdot x[0]$ ถูกสร้างขึ้นที่เอาต์พุต $P_0$ หลังจากผ่านไป:
     $$T_{tap0} = 3 \text{ รอบสัญญาณนาฬิกา}$$

2. **การส่งต่อผลบวกผ่านสาย Cascade Chain:**
   * สัญญาณผลบวกจะเดินทางจาก Tap 0 ไปยัง Tap 1, Tap 2, $\dots$, Tap 31
   * ในแต่ละ Tap ระหว่างทาง ผลรวมจะถูกบวกเข้ากับผลคูณของ Tap นั้นๆ และถูกแลตช์ผ่าน `PREG` สเตจละ $1$ รอบสัญญาณนาฬิกาพอดี ($z^{-1}$ per hop)
   * จำนวนช่วงของการกระโดด (Hops) จาก Tap 0 ไปยัง Tap 31 คือ:
     $$N_{hops} = 32 - 1 = 31 \text{ ช่วง}$$
   * เวลาหน่วงในการเดินทางผ่าน Cascade Chain:
     $$T_{cascade} = 31 \times 1 = 31 \text{ รอบสัญญาณนาฬิกา}$$

3. **รวมเวลาความล่าช้าทั้งหมด (Total Pipeline Latency):**
   $$T_{total} = T_{tap0} + T_{cascade} = 3 + 31 = 34 \text{ รอบสัญญาณนาฬิกา}$$

*(ข้อสังเกต: ข้อมูล $x$ ที่ถูกหน่วง $z^{-2}$ จะเดินทางมาบรรจบกับผลรวม $P$ ที่เคลื่อนที่ด้วยความเร็วสัมพัทธ์ $z^{-1}$ ทำให้ข้อมูลตัวอย่าง $x[n-k]$ ตรงกับสัมประสิทธิ์ $h[k]$ ในทุกๆ จุดของแถวลำดับอย่างแม่นยำสมบูรณ์แบบ)*

---

### คำถามที่ 2: การคำนวณ Logic Depth และ Delay ของ Adder Tree ใน Direct Form FIR

พิจารณาตัวกรอง Direct Form FIR ขนาด $M = 64$ Taps บนผืน Fabric ของ Xilinx FPGA:
* ผลคูณแต่ละตัวมีขนาด 32 บิต
* หากไม่ใส่ Pipeline คั่นกลางระหว่างชั้นของ Adder Tree:
* วงจรบวกขนาด 32 บิตแต่ละชั้นสร้างขึ้นจากโครงสร้าง Carry Chain (CARRY8) มีความหน่วงรวมสายไฟเฉลี่ย: $t_{add\_stage} = 0.480\text{ ns}$ ต่อ 1 ระดับชั้น
* จำนวนชั้นของ Binary Adder Tree สำหรับ 64 อินพุตคำนวณจาก: $L = \lceil \log_2 64 \rceil = 6$ ชั้น

จงคำนวณหาความหน่วงเวลารวมของเฉพาะโครงสร้าง Adder Tree ($T_{tree}$) และประเมินความถี่สูงสุด $F_{max}$ ที่วงจรบวกนี้จะสามารถทำงานได้หากไม่นับความหน่วงของตัวคูณ?

---

#### ตัวเลือก:
A) $T_{tree} = 1.44\text{ ns}$, $F_{max} = 694.4\text{ MHz}$  
B) $T_{tree} = 2.88\text{ ns}$, $F_{max} = 347.2\text{ MHz}$  
C) $T_{tree} = 3.84\text{ ns}$, $F_{max} = 260.4\text{ MHz}$  
D) $T_{tree} = 4.80\text{ ns}$, $F_{max} = 208.3\text{ MHz}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) $T_{tree} = 2.88\text{ ns}$, $F_{max} = 347.2\text{ MHz}$**

##### ขั้นตอนที่ 1: คำนวณความหน่วงเวลารวมของ Adder Tree 6 ชั้น
$$T_{tree} = L \times t_{add\_stage} = 6 \times 0.480\text{ ns} = 2.880\text{ ns}$$

##### ขั้นตอนที่ 2: คำนวณความถี่สัญญาณนาฬิกาสูงสุด
$$F_{max} = \frac{1}{T_{tree}} = \frac{1}{2.880 \times 10^{-9}\text{ s}} \approx 347.22\text{ MHz}$$

และหากนำความหน่วงนี้ไปรวมกับตัวคูณ ($t_{mult} \approx 1.5\text{ ns}$) คาบเวลารวมจะพุ่งขึ้นเป็น $4.38\text{ ns}$ ทำให้ $F_{max}$ ดิ่งลงต่ำกว่า **$228\text{ MHz}$** ทันที นี่คือหลักฐานทางคณิตศาสตร์ที่ชี้ชัดว่า ทำไม Direct Form จึงไม่มีทางปิด Timing ที่ $500\text{ MHz}$ ได้โดยไม่ใช้ Systolic Architecture!

---

### คำถามที่ 3: ข้อได้เปรียบของการใช้ Dedicated Cascade `PCOUT/PCIN` ด้านการใช้พลังงาน

เหตุใดการเชื่อมต่อ DSP แบบ Systolic ผ่านสาย `PCOUT/PCIN` จึงช่วยลดการใช้พลังงาน (Power Dissipation) ลงได้อย่างมหาศาลเมื่อเทียบกับการเดินสายผ่าน Fabric ทั่วไป?

---

#### ตัวเลือก:
A) เพราะสาย Cascade มีความต้านทานเป็นศูนย์  
B) เพราะสาย `PCOUT/PCIN` เป็นสายเชื่อมต่อทางกายภาพเฉพาะกิจที่มีความยาวระดับไมโครเมตรภายในคอลัมน์ซิลิคอน ทำให้มีค่าความจุไฟฟ้าของสาย ($C_{wire}$) ต่ำกว่าสาย Programmable Interconnect ทั่วไปมากกว่า $80\%$ และไม่ต้องผ่าน Buffer Switch Matrix  
C) เพราะทำงานที่ความถี่ต่ำกว่า  
D) เพราะตัดตัวคูณทิ้งไปครึ่งหนึ่ง

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เพราะสาย PCOUT/PCIN เป็นสายเชื่อมต่อทางกายภาพเฉพาะกิจที่มีความยาวระดับไมโครเมตรภายในคอลัมน์ซิลิคอน ทำให้มีค่าความจุไฟฟ้าของสาย ($C_{wire}$) ต่ำกว่าสาย Programmable Interconnect ทั่วไปมากกว่า 80% และไม่ต้องผ่าน Buffer Switch Matrix**

##### เหตุผลทางฟิสิกส์เซมิคอนดักเตอร์:
ใน FPGA ทั่วไป สายไฟที่วิ่งผ่านผืน Fabric จะต้องผ่าน Pass-transistor และ Multiplexer ใน Switch Box หลายระดับ ซึ่งมีค่าความจุแฝงปรสิต (Parasitic Capacitance) สูงมาก เมื่อส่งสัญญาณบัส 48 บิตที่ความถี่ $500\text{ MHz}$ กำลังไฟฟ้าชาร์จประจุ $P = C V^2 f$ จะพุ่งสูงขึ้นอย่างรวดเร็ว

ในทางตรงกันข้าม สาย **Dedicated Cascade (`PCOUT/PCIN`)**:
1. เป็นเส้นทางโลหะตรง (Direct Hardwired Metal Track) ที่ลากเชื่อมระหว่างเซลล์ DSP ตัวล่างและตัวบนที่วางชิดกัน
2. มีค่าความจุไฟฟ้า $C_{wire}$ ต่ำมากระดับเพียงไม่กี่ femtofarads
3. จึงช่วยลดทั้งความร้อน, การกระเพื่อมของแรงดันไฟเลี้ยง (IR Drop), และประหยัดพลังงานไดนามิกของทั้งระบบได้อย่างเด็ดขาด
