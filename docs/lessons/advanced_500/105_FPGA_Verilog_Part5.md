# Lesson 105: DSP Slices & Pipeline Architecture (DSPスライスと高効率パイプライン演算アーキテクチャ)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมฮาร์ดแวร์เฉพาะทางของ DSP Slice (DSP48E2 Architecture)
ในการประมวลผลสัญญาณดิจิทัลความเร็วสูง (Digital Signal Processing: DSP) เช่น ตัวกรอง FIR, การแปลง FFT, มอเตอร์คอนโทรลเลอร์ความแม่นยำสูง, และอัลกอริทึมปัญญาประดิษฐ์ (Edge AI) การใช้ Look-Up Table (LUT) ทั่วไปในการคำนวณการคูณจะสิ้นเปลืองพื้นที่ซิลิคอนและทำให้ความเร็วลดลงอย่างรุนแรง ชิป FPGA สมัยใหม่จึงบรรจุบล็อกฮาร์ดแวร์เฉพาะทางที่เรียกว่า **DSP Slice** (เช่น Xilinx DSP48E2 บน UltraScale+ หรือ Variable Precision DSP บน Intel Stratix 10)

บล็อกสถาปัตยกรรม DSP48E2 ประกอบด้วยองค์ประกอบการคำนวณคณิตศาสตร์ 4 ส่วนหลัก:

```
                     Xilinx UltraScale+ DSP48E2 Block Architecture
         A [29:0]              D [26:0]
            |                     |
            v                     v
         [ AREG ]              [ DREG ]
            |                     |
            +-------->[ Pre-Adder (27-bit) ]<-- (Symmetric FIR optimization)
            |                     |
            v                     v
       A_mult [26:0]           [ ADREG ]
            \                     /
             \                   /
              v                 v
            [ 27 x 18 Multiplier ]     B [17:0] ---> [ BREG ]
                      |
                      v
                   [ MREG ] (Pipeline Stage)
                      |
                      v
             +-->[ Multiplexer (X, Y, Z, W) ]<-- C [47:0] ---> [ CREG ]
             |        |
             |        v
             |   [ 48-bit ALU / Accumulator ]
             |        |
             |        v
             +-----[ PREG ] (Output Register)
                      |
                      v
                   P [47:0] / PCOUT (Dedicated Cascade Bus)
```

1. **Pre-Adder ขนาด 27 บิต:** ทำหน้าที่บวกหรือลบสัญญาณ $D \pm A$ ก่อนเข้าสู่ตัวคูณ ออกแบบมาโดยเฉพาะสำหรับตัวกรอง FIR ชนิด Symmetric ซึ่งช่วยลดจำนวนตัวคูณลงได้ถึง $50\%$
2. **ตัวคูณความแม่นยำสูงขนาด $27 \times 18$ บิต:** รองรับการคูณจำนวนเต็มแบบคิดเครื่องหมาย (Signed Two's Complement Multiplier) ในไซเคิลเดียว
3. **ALU / Accumulator ขนาด 48 บิต:** ทำหน้าที่สะสมผลคูณ (Multiply-Accumulate: MAC), ทำการบวก/ลบ ($P = M \pm C$ หรือ $P = P \pm M$), ลอจิกบิตไวส์ (AND/OR/XOR), และตรวจจับลวดลายบิต (Pattern Detector)
4. **Dedicated Dedicated Cascade Bus (`ACOUT`, `BCOUT`, `PCOUT`):** เส้นทางสายด่วนทองแดงเฉพาะทางที่เชื่อมต่อผลลัพธ์ของ DSP Slice ตัวหนึ่งไปยัง DSP Slice ตัวถัดไปที่อยู่ติดกัน โดยไม่ต้องวิ่งผ่าน Routing Fabric ทั่วไป ช่วยลดเวลาหน่วงและประหยัดพลังงาน

---

### 1.2 การวิเคราะห์ความล่าช้าและการทำ Pipelining ภายใน DSP
ความเร็วสูงสุด ($F_{max}$) ของ DSP Slice ขึ้นอยู่กับจำนวนของรีจิสเตอร์ภายใน (Pipeline Registers) ที่เปิดใช้งานในเส้นทางข้อมูล:

$$\text{Critical Path Delay} = t_{in\_reg} + t_{pre\_add} + t_{mult} + t_{alu} + t_{out\_reg}$$

ตารางเปรียบเทียบความสัมพันธ์ของระดับ Pipelining และความถี่สูงสุด ($F_{max}$) บน Xilinx UltraScale+ (-2 Speed Grade):

| การกำหนดค่า Pipelining | รีจิสเตอร์ที่เปิดใช้งาน | จำนวน Latency (Cycles) | ความถี่สูงสุด $F_{max}$ | ลักษณะการใช้งาน |
| :--- | :--- | :---: | :---: | :--- |
| **Bypassed (Zero Pipeline)** | ไม่มี (ใช้ Combinational ทั้งหมด) | 0 | $\approx 210\text{ MHz}$ | ระบบความเร็วต่ำมาก หรือลอจิกควบคุมง่ายๆ |
| **Basic Pipeline** | เปิดเฉพาะ $AREG/BREG$ และ $PREG$ | 2 | $\approx 480\text{ MHz}$ | มอเตอร์ไดรฟ์, วงจรควบคุมความเร็วปานกลาง |
| **Fully Pipelined (Optimal)** | เปิด $AREG=2, BREG=2, MREG=1, PREG=1$ | 4 | **$\ge 750\text{ MHz}$** | **5G Wireless, Radar, 4K Image Processing** |

> **กฎเหล็กของวิศวกร DSP:** หากต้องการให้การคำนวณคณิตศาสตร์รันที่ความเร็วเกิน $400\text{ MHz}$ จะต้องเปิดใช้งาน **$MREG$ (Multiplier Pipeline Register)** เสมอ เพราะตัวคูณ $27 \times 18$ มี Delay ในตัวเองประมาณ $1.5 - 2.0\text{ ns}$ การตัดแบ่งด้วย $MREG$ จะลด Critical Path เหลือเพียงเศษส่วนของนาโนวินาที

---

### 1.3 ทฤษฎีคณิตศาสตร์จุดคงที่ (Fixed-Point Arithmetic) และรูปแบบ $Q$-Format
ในการออกแบบฮาร์ดแวร์ การใช้เลขทศนิยมลอยตัว (Floating-Point: IEEE 754) สิ้นเปลืองทรัพยากรและเกิด Latency สูง วิศวกรอาวุโสจึงใช้ **Fixed-Point Arithmetic** ในรูปแบบ $Q$-format:

$$Qm.n \implies 1\text{ Sign Bit} + m\text{ Integer Bits} + n\text{ Fractional Bits}$$

ความกว้างของบิตทั้งหมดคือ $W = 1 + m + n$ บิต  
ค่าจริงทางคณิตศาสตร์มีค่าเท่ากับ:

$$X_{real} = X_{integer} \times 2^{-n}$$

#### การเติบโตของบิตในการคูณ (Bit Growth Mechanics)
เมื่อนำจำนวนจุดคงที่สองตัวมาคูณกัน:

$$Q(m_1, n_1) \times Q(m_2, n_2) \implies Q(m_1 + m_2 + 1, n_1 + n_2)$$

* ตัวอย่าง: สัญญาณอินพุตเสียง $Q1.15$ (16 บิต) คูณกับสัมประสิทธิ์ตัวกรอง $Q1.15$ (16 บิต):
  $$\text{ผลลัพธ์ที่ได้จะมีขนาด } Q(1 + 1 + 1, 15 + 15) = Q3.30 \implies \text{กว้างถึง } 32\text{ บิต}$$
* **Truncation vs Rounding:** หากตัดปลายบิตล่างทิ้งดื้อๆ (Truncation) จะเกิดค่าความผิดพลาดเฉลี่ยแบบมีทิศทาง (DC Bias / Negative Drift) ในระบบตัวกรองแบบ IIR การปัดเศษที่ถูกต้องต้องใช้วิธี **Round-to-Nearest (四捨五入)** โดยการบวกค่า $0.5 \times LSB$ (นั่นคือการบวกค่า $2^{n-1}$ เข้าไปที่ตำแหน่งทศนิยมก่อนตัดบิต)

#### การป้องกันการกลับขั้วของเครื่องหมายด้วย Saturation Logic (飽和処理)
หากเกิดภาวะเลขล้น (Arithmetic Overflow) ในระบบ Two's Complement ค่าบวกสูงสุด ($+0111...$) เมื่อบวกเพิ่มอีก 1 จะพลิกกลับกลายเป็นค่าลบต่ำสุด ($-1000...$) ทันที ซึ่งเรียกว่า **Sign-Wrap Around** ส่งผลให้เกิดเสียงกระแทกความถี่สูงในระบบเสียง หรือเกิดการสั่นพริ้วจนมอเตอร์ระเบิด
การออกแบบระดับมืออาชีพต้องมีวงจร **Saturating Logic** ดักจับ:
* หากล้นฝั่งบวก: บังคับให้ค้างไว้ที่ $+V_{max}$
* หากล้นฝั่งลบ: บังคับให้ค้างไว้ที่ $-V_{min}$

```
                  พฤติกรรมของ Overflow: Wrap-Around vs Saturation
   แรงดันคำนวณจริง
        ^
  +Vmax |            /|                +Vmax |     /-----------\ (Saturated)
        |           / |                      |    /             \
        |          /  |                      |   /               \
      0 +---------/---+------->            0 +--/-----------------\---->
        |        /    |                      | /                   \
  -Vmin |-------/     | (Wrap-Around)  -Vmin |/                     \
        +-------------+                      +-----------------------+
        [ แบบผิด: เสียงแตกกระชาก ]             [ แบบถูก: มีวงจรดักจับ Saturation ]
```

---

### 1.4 โค้ดต้นแบบ SystemVerilog สำหรับ Pipelined DSP MAC Unit
โค้ดนี้ถูกเขียนขึ้นเพื่อให้เครื่องมือสังเคราะห์วงจร Infer บล็อก DSP48E2 โดยอัตโนมัติพร้อมเปิดใช้ Register ทุกระดับอย่างถูกต้อง:

```verilog
// Professional Fully-Pipelined DSP48E2 MAC with Saturation Logic
module dsp_mac_pipelined #(
    parameter int DATA_WIDTH = 16,
    parameter int COEFF_WIDTH = 16,
    parameter int ACCUM_WIDTH = 48
)(
    input  logic                          clk,
    input  logic                          rst_n,
    input  logic                          clr_accum,
    input  logic signed [DATA_WIDTH-1:0]  din_a,
    input  logic signed [COEFF_WIDTH-1:0] din_b,
    output logic signed [DATA_WIDTH-1:0]  dout_saturated
);

    // Stage 1: Input Registers (A & B)
    (* use_dsp = "yes" *) logic signed [DATA_WIDTH-1:0]  a_reg;
    (* use_dsp = "yes" *) logic signed [COEFF_WIDTH-1:0] b_reg;

    // Stage 2: Multiplier Output Register (MREG)
    logic signed [DATA_WIDTH+COEFF_WIDTH-1:0] mult_reg;

    // Stage 3: Accumulator Output Register (PREG)
    logic signed [ACCUM_WIDTH-1:0] accum_reg;
    logic                          clr_accum_d1, clr_accum_d2;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            a_reg        <= '0;
            b_reg        <= '0;
            mult_reg     <= '0;
            accum_reg    <= '0;
            clr_accum_d1 <= 1'b0;
            clr_accum_d2 <= 1'b0;
        end else begin
            // Pipeline Delay for Clear signal
            clr_accum_d1 <= clr_accum;
            clr_accum_d2 <= clr_accum_d1;

            // Pipeline Stage 1: Inputs
            a_reg <= din_a;
            b_reg <= din_b;

            // Pipeline Stage 2: Multiplier (Inferred MREG)
            mult_reg <= a_reg * b_reg;

            // Pipeline Stage 3: Accumulator (Inferred PREG)
            if (clr_accum_d2) begin
                accum_reg <= mult_reg;
            end else begin
                accum_reg <= accum_reg + mult_reg;
            end
        end
    end

    // Saturation and Rounding Output Stage
    localparam signed [DATA_WIDTH-1:0] MAX_POS = {1'b0, {(DATA_WIDTH-1){1'b1}}};
    localparam signed [DATA_WIDTH-1:0] MAX_NEG = {1'b1, {(DATA_WIDTH-1){1'b0}}};

    always_comb begin
        // ตรวจจับ Overflow บนบิตทศนิยมบน
        if (accum_reg[ACCUM_WIDTH-1:DATA_WIDTH-1] > 0 && accum_reg[ACCUM_WIDTH-1] == 1'b0) begin
            dout_saturated = MAX_POS;
        end else if (accum_reg[ACCUM_WIDTH-1:DATA_WIDTH-1] < -1 && accum_reg[ACCUM_WIDTH-1] == 1'b1) begin
            dout_saturated = MAX_NEG;
        end else begin
            // นำเฉพาะบิตข้อมูลที่ปัดเศษแล้วออกมา
            dout_saturated = accum_reg[DATA_WIDTH-1:0];
        end
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน (失敗事例: Shippai Jirei)
* **บริบท:** การ์ดประมวลผล Digital Beamforming สำหรับเรดาร์สำรวจอากาศ ทำงานบนบอร์ด FPGA Kintex UltraScale ความถี่เป้าหมาย $450\text{ MHz}$
* **สถาปัตยกรรม:** ตัวกรองสัญญาณ Digital Down Converter (DDC) 64-Tap Symmetric FIR Filter
* **อาการเสียหน้างาน:** การสังเคราะห์และทำ Place & Route ผ่านได้ แต่ผลการวิเคราะห์เวลาล้มเหลวอย่างรุนแรง โดยมีค่า Setup Slack ติดลบถึง **$\text{WNS} = -1.850\text{ ns}$** ความถี่สูงสุดทำได้จริงเพียง $245\text{ MHz}$ ส่งผลให้ไม่สามารถรันระบบที่ $450\text{ MHz}$ ได้
* **การตรวจสอบ RTL:** ตรวจสอบโค้ด Verilog ของวิศวกรผู้พัฒนา พบว่าเขียนสมการ FIR Filter ในสไตล์ Behavioral ระดับสูง:

```verilog
// โค้ดที่ก่อให้เกิดความล้มเหลวหน้างาน (Shippai Code)
always_ff @(posedge clk) begin
    y_out <= (x[0] + x[63]) * c[0] + (x[1] + x[62]) * c[1] + ... + accum;
end
```

```
            ผลลัพธ์จากการเขียนโค้ดคณิตศาสตร์แบบก้อนเดียว (Shippai Analysis)
   +--------------------------------------------------------------------------+
   | โค้ด Verilog รวม Pre-Add, Multiply, และ Accumulate ไว้ใน 1 ไซเคิล          |
   +--------------------------------------------------------------------------+
                                       |
                                       v
   +--------------------------------------------------------------------------+
   | คอมไพเลอร์มองไม่เห็นจังหวะให้ตัด Register:                                |
   | จึงสั่ง Bypass รีจิสเตอร์ภายใน DSP48E2 ทั้งหมด (AREG=0, MREG=0, PREG=0)  |
   +--------------------------------------------------------------------------+
                                       |
                                       v
   +--------------------------------------------------------------------------+
   | ความหน่วงรวมพุ่งสูง:                                                      |
   | Pre-adder (1.2ns) + Multiplier (1.8ns) + Adder Tree (1.6ns) = 4.6ns       |
   | ในขณะที่คาบเวลา 450MHz คือ 2.22ns -> เกิด SETUP VIOLATION มหาศาล          |
   +--------------------------------------------------------------------------+
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (Root Cause Analysis: 5 Whys & Ishikawa)

```mermaid
graph TD
    A[FIR Filter ไม่ผ่าน Timing ที่ 450MHz (WNS = -1.85ns)] --> B{5 Whys Analysis}
    B --> C[Why 1: ทำไมไทม์มิ่งติดลบ? -> Critical Path มีความหน่วงรวมถึง 4.6ns]
    C --> D[Why 2: ทำไมดีเลย์ถึงยาว 4.6ns? -> ลอจิกบวกและคูณทั้งหมดต่ออนุกรมใน 1 ไซเคิล]
    D --> E[Why 3: ทำไมไม่มี Register คั่น? -> เขียนสมการคณิตศาสตร์แบบสมการเดียวใน RTL]
    E --> F[Why 4: ทำไมฮาร์ดแวร์ DSP ไม่ช่วย? -> คอมไพเลอร์ Bypass รีจิสเตอร์ภายใน DSP หมด]
    F --> G[Why 5: ทำไมผู้ออกแบบเขียนเช่นนั้น? -> ขาดความเข้าใจสถาปัตยกรรมภายในของ DSP48]
```

#### Ishikawa Diagram (ผังก้างปลา)
* **Design/RTL:** เขียนสมการรวมก้อนเดียวโดยไม่กระจาย Latency Pipeline ให้สอดคล้องกับพอร์ต DSP48
* **Technology Knowledge:** ไม่รู้ว่า DSP48 มีรีจิสเตอร์ $AREG$, $MREG$, $PREG$ ที่ต้องเขียนคำสั่ง Sequential ดักไว้ในแต่ละชั้น
* **Cascading:** ไม่ได้ใช้พอร์ตด่วน `PCOUT` $\to$ `PCIN` ทำให้สัญญาณ Accumulator ต้องวิ่งผ่าน General Fabric ซึ่งช้ากว่า 3 เท่า
* **Review Process:** การตรวจแบบก่อนหน้านี้ไม่ได้ตรวจสอบรายงาน *"DSP Utilization and Pipeline Report"* ของ Vivado

---

### 2.3 มาตรการแก้ไขและปรับปรุงสถาปัตยกรรมสู่ Systolic FIR Architecture
1. **จัดโครงสร้างเป็นแบบ Systolic FIR Filter:** กระจายข้อมูล $x[n]$ และผลรวมสะสมผ่านทางสายด่วน Cascade Bus (`PCOUT` $\to$ `PCIN`)
2. **แทรก Pipeline Registers ให้ครบ 3 สเตจ:**
   * สเตจ 1: ดักรับสัญญาณอินพุต ($AREG=1, BREG=1$)
   * สเตจ 2: ดักผลคูณ ($MREG=1$)
   * สเตจ 3: ดักผลสะสม ($PREG=1$)
3. **ผลลัพธ์หลังแก้ไข:** Setup Slack ดีดกลับมาเป็นบวก **$\text{WNS} = +0.340\text{ ns}$** และระบบสามารถทำงานได้เสถียรที่ **$500\text{ MHz}$** ($F_{max} = 531\text{ MHz}$) เกินกว่าเป้าหมายเดิม

---

### 2.4 ตารางตรวจสอบหน้างาน SOP สำหรับการออกแบบ DSP บน FPGA (DSP SOP Checklist)

| ลำดับ | จุดตรวจสอบทางวิศวกรรม | เกณฑ์การยอมรับ (Acceptance Criteria) | เครื่องมือตรวจสอบ | ผลการตรวจ |
| :---: | :--- | :--- | :--- | :---: |
| 1 | MREG Utilization | ความถี่ $\ge 350\text{ MHz}$ ต้องเปิดใช้งาน $MREG$ ($100\%$ ของ DSP blocks) | Vivado DSP Report | ผ่าน / ไม่ผ่าน |
| 2 | Cascade Bus Mapping | ตัวกรอง FIR แบบหลายแท็ปต้องเชื่อมต่อผ่าน `PCOUT` $\to$ `PCIN` (ไม่วิ่งบน Fabric) | Device Schematics View | ผ่าน / ไม่ผ่าน |
| 3 | Saturation Protection | เอาต์พุตของวงจรสะสมผลรวม (Accumulator) ต้องมี Saturating Logic ป้องกัน Wrap-around | RTL Code Review / SVA | ผ่าน / ไม่ผ่าน |
| 4 | Fixed-Point Rounding Mode | ห้ามตัดบิต (Truncate) ในลูปป้อนกลับของ IIR ให้ใช้ Round-to-Nearest ($+0.5\text{ LSB}$) | MATLAB / RTL Bit Match | ผ่าน / ไม่ผ่าน |
| 5 | Dynamic Power & Clock Gating | บล็อก DSP ที่ไม่ได้ทำงานต่อเนื่อง ต้องมีสัญญาณ Clock Enable ควบคุม | Power Report (XPE/Vivado) | ผ่าน / ไม่ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ/คาตาคานะ | การอ่าน (Romaji) | คำแปลภาษาไทย / ภาษาอังกฤษ |
| :--- | :--- | :--- |
| **積和演算** | Sekiwa enzan | การคูณสะสม (Multiply-Accumulate: MAC) |
| **乗算累算器** | Jōzan ruisanki | ตัวคูณและสะสมผลลัพธ์ (MAC Unit / Multiplier-Accumulator) |
| **固定小数点数** | Kotei shōsūten-sū | เลขทศนิยมจุดคงที่ (Fixed-Point Number) |
| **飽和処理** | Hōwa shori | การจำกัดค่าอิ่มตัวป้องกันเลขล้น (Saturation Arithmetic) |
| **丸め処理** | Marume shori | การปัดเศษทศนิยม (Rounding Processing) |
| **切り捨て** | Kirisute | การตัดเศษทิ้ง (Truncation) |
| **四捨五入** | Shishagonyū | การปัดเศษทศนิยมแบบปัดขึ้นเมื่อถึง 5 (Round-to-Nearest) |
| **カスケード接続** | Kasukēdo setsuzoku | การต่ออนุกรมผ่านสายส่งด่วน (Cascade Connection) |
| **前段加算器** | Zendan kasanki | พรีแอดเดอร์ (Pre-Adder Unit) |
| **符号反転オーバーフロー** | Fugō hanten ōbāfurō | การล้นของตัวเลขจนเครื่องหมายกลับขั้ว (Sign-Wrap Around Overflow) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図での指摘事項)

#### การตรวจแบบจุดที่ 1: การตรวจพบการไม่เปิดใช้ Pipeline Register ใน DSP Slice
* **審査役 (Lead Chief Engineer):**
  「この400MHz動作の画像フィルタ回路ですが、DSPレポートを見ると `MREG` がバイパス（0段）になっています。乗算器から後段のアキュムレータまでがコンビネーショナル直結になっているため、$-1.2\text{ ns}$ もの大きなセットアップ違反が発生しています。RTLの記述を見直し、パイプラインレジスタを乗算出力段に必ず挿入してください。」
  *(ในวงจรตัวกรองภาพที่ทำงานที่ 400MHz ตัวนี้ รายงานของ DSP ระบุว่า `MREG` ถูกบายพาส (0 สเตจ) อยู่นะครับ การที่สัญญาณจากตัวคูณวิ่งทะลุไปยังแอกคิวมูเลเตอร์เป็น Combinational ตรงๆ ทำให้เกิด Setup Violation ติดลบถึง $-1.2\text{ ns}$ ช่วยทบทวนการเขียน RTL และแทรก Pipeline Register เข้าไปที่เอาต์พุตของตัวคูณด้วยครับ)*
* **設計担当 (FPGA Design Engineer):**
  「ご指摘ありがとうございます。1クロックサイクル内で乗算と加算を同時に記述していたことが原因でした。レイテンシを1サイクル追加し、乗算結果をレジスタで受ける構造へ修正することで `MREG` を有効化し、タイミングを収束させます。」
  *(ขอบพระคุณสำหรับข้อสังเกตครับ สาเหตุเกิดจากการที่ผมเขียนคำสั่งคูณและบวกพร้อมกันใน 1 ไซเคิลครับ ผมจะเพิ่ม Latency 1 ไซเคิลและปรับโครงสร้างให้มี Register มารับผลคูณ เพื่อเปิดใช้งาน `MREG` และทำให้ไทม์มิ่งบรรลุเป้าหมายครับ)*

#### การตรวจแบบจุดที่ 2: การเตือนความเสี่ยงของเสียงระเบิดจาก Wrap-Around โดยไม่มี Saturation
* **審査役 (Lead Chief Engineer):**
  「アキュムレータの出力ビット幅を48ビットからオーディオDAC用の24ビットへ削減している箇所ですが、単に上位ビットを切り捨てているだけですね。最大音量時に1ビットでもオーバーフローが発生すると、符号ビットが反転して『最大正値から最大負値』へ急落し、スピーカーを破損させる激しいポップノイズ（バリバリ音）が発生します。直ちに飽和処理（クリッピング回路）を実装してください。」
  *(ในจุดที่ลดขนาดบิตของ Accumulator จาก 48 บิตลงเหลือ 24 บิตสำหรับส่งเข้า Audio DAC คุณใช้วิธีตัดบิตบนทิ้งดื้อๆ เลยนะครับ หากมี Overflow แม้แต่บิตเดียวตอนเปิดเสียงดังสุด บิตเครื่องหมายจะกลับขั้วและกระชากจากค่าบวกสูงสุดลงสู่ค่าลบสูงสุดทันที ซึ่งจะสร้างเสียงป๊อปกระแทกอย่างรุนแรงจนลำโพงพังเสียหายได้ ช่วยใส่ลอจิก Saturation (Clipping Circuit) ในทันทีด้วยครับ)*
* **設計担当 (FPGA Design Engineer):**
  「申し訳ございません。クリッピング処理の重要性を再認識いたしました。オーバーフロー検出ロジックを追加し、正の最大値 `0x7FFFFF` および負の最小値 `0x800000` で確実にサチュレーション（飽和）させる回路を追加いたします。」
  *(ต้องขออภัยด้วยครับ ผมตระหนักถึงความสำคัญของวงจร Clipping อย่างยิ่งแล้วครับ ผมจะเพิ่มลอจิกตรวจจับ Overflow และบังคับล็อกค่าที่ขอบเขตบวกสูงสุด `0x7FFFFF` และขอบเขตลบต่ำสุด `0x800000` เพื่อให้ระบบปลอดภัยสมบูรณ์ครับ)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณอัตราส่วนสัญญาณต่อสัญญาณรบกวนจากการควอนไทซ์ (SQNR) ของเลขจุดคงที่
ในระบบประมวลผลเซนเซอร์สั่นสะเทือนความแม่นยำสูง สัญญาณแอนะล็อกถูกแปลงเป็นดิจิทัลด้วย ADC ขนาด 16 บิต และประมวลผลในรูปแบบตัวเลขจุดคงที่ $Q1.15$ (มีบิตเครื่องหมาย 1 บิต และบิตทศนิยม 15 บิต)

ตามทฤษฎีสารสนเทศและการประมวลผลสัญญาณดิจิทัล:
* สัญญาณรบกวนจากการควอนไทซ์ (Quantization Noise Power, $\sigma_e^2$) มีค่าเท่ากับ $\frac{\Delta^2}{12}$ โดยที่ $\Delta = 2^{-15}$ คือขนาดของ Least Significant Bit (LSB)
* อัตราส่วนสัญญาณสูงสุดต่อสัญญาณรบกวนการควอนไทซ์ (Peak Signal-to-Quantization-Noise Ratio: SQNR) สำหรับคลื่นรูปไซน์เต็มสเกล ($V_{peak} = 1.0$) คำนวณได้จากสมการ:
  $$\text{SQNR} \approx 6.02 \cdot N + 1.76\text{ dB}$$
  (โดยที่ $N$ คือจำนวนบิตข้อมูล)

หากวิศวกรต้องการเพิ่มความแม่นยำในการคำนวณภายใน DSP Core โดยขยายขนาดตัวเลขจาก $Q1.15$ (16 บิต) ไปเป็น $Q4.27$ (32 บิต) จงคำนวณว่าค่า **SQNR ในทางทฤษฎีจะเพิ่มขึ้นกี่เดซิเบล (dB)**?

a) เพิ่มขึ้นประมาณ $12.04\text{ dB}$  
b) เพิ่มขึ้นประมาณ $72.24\text{ dB}$  
c) เพิ่มขึ้นประมาณ $96.32\text{ dB}$  
d) เพิ่มขึ้นประมาณ $6.02\text{ dB}$  

---

#### เฉลยและบทวิเคราะห์เชิงลึกข้อที่ 1
**คำตอบที่ถูกต้องคือ: b) เพิ่มขึ้นประมาณ $72.24\text{ dB}$**

**ขั้นตอนการคำนวณทางคณิตศาสตร์:**
1. วิเคราะห์จำนวนบิตทศนิยม ($n$) ซึ่งเป็นตัวกำหนดความละเอียดของการควอนไทซ์ (Quantization Resolution):
   * รูปแบบเดิม: $Q1.15$ มีจำนวนบิตความละเอียดทศนิยม $n_1 = 15\text{ บิต}$ (หรือคิดเป็นขนาดรวม $N_1 = 16\text{ บิต}$)
   * รูปแบบใหม่: $Q4.27$ มีจำนวนบิตความละเอียดทศนิยม $n_2 = 27\text{ บิต}$
2. คำนวณจำนวนบิตความละเอียดที่เพิ่มขึ้นจริงสำหรับการแสดงค่าระดับสัญญาณ:
   $$\Delta N = n_2 - n_1 = 27 - 15 = 12\text{ บิต}$$
3. คำนวณการปรับปรุงของค่า SQNR จากทฤษฎี $6.02\text{ dB ต่อบิต}$:
   $$\Delta \text{SQNR} = 6.02 \times \Delta N = 6.02 \times 12\text{ บิต} = 72.24\text{ dB}$$
4. **ความหมายเชิงวิศวกรรม:**
   * การเพิ่มความละเอียด 12 บิตในส่วนทศนิยมช่วยกดระดับ Noise Floor จากการคำนวณคณิตศาสตร์ลงไปได้ถึง $72.24\text{ dB}$ (หรือพลังงานสัญญาณรบกวนลดลงมากกว่า $16\text{ ล้านเท่า}$) ช่วยขจัดปัญหา Limit Cycle Oscillation ในตัวกรองความถี่ต่ำได้อย่างเด็ดขาด

---

### ข้อที่ 2: การวิเคราะห์โครงสร้าง Systolic FIR Filter เทียบกับ Direct Form FIR
ในการออกแบบตัวกรอง FIR ขนาด $N = 64\text{ Taps}$ บนชิป FPGA ความถี่ $500\text{ MHz}$ ($T_{clk} = 2.0\text{ ns}$):
* **โครงสร้าง Direct Form:** นำผลคูณของทั้ง 64 แท็ปมาบวกกันผ่าน Adder Tree ก่อนเข้าสู่ Register ปลายทาง
* **โครงสร้าง Systolic FIR (Transposed / Cascaded Form):** นำ DSP Slice มาต่ออนุกรมกันโดยใช้สายส่งด่วน `PCOUT` $\to$ `PCIN` ภายใน โดยในแต่ละแท็ปมี Delay ของ Accumulator และสาย Cascade $t_{pcin} \approx 0.35\text{ ns}$

เหตุใดโครงสร้างแบบ Systolic จึงสามารถทำความเร็วได้สูงกว่าแบบ Direct Form อย่างมหาศาลเมื่อจำนวนแท็ป ($N$) มีค่ามากขึ้น?

a) เพราะโครงสร้าง Systolic ขจัด Adder Tree ทิ้งไป และกระจายการคำนวณออกเป็น Local Pipeline Stage ในแต่ละ DSP Slice ทำให้ Critical Path Delay คงที่สม่ำเสมอไม่ขึ้นกับจำนวนแท็ป $N$  
b) เพราะโครงสร้าง Systolic ไม่จำเป็นต้องใช้สัมประสิทธิ์ตัวกรอง  
c) เพราะโครงสร้าง Systolic แปลงการคำนวณคูณให้กลายเป็นการเลื่อนบิต (Shift-Add) ทั้งหมด  
d) เพราะโครงสร้าง Systolic ใช้จำนวน DSP Slice น้อยกว่าแบบ Direct Form ครึ่งหนึ่งเสมอ  

---

#### เฉลยและบทวิเคราะห์เชิงลึกข้อที่ 2
**คำตอบที่ถูกต้องคือ: a) เพราะโครงสร้าง Systolic ขจัด Adder Tree ทิ้งไป และกระจายการคำนวณออกเป็น Local Pipeline Stage ในแต่ละ DSP Slice ทำให้ Critical Path Delay คงที่สม่ำเสมอไม่ขึ้นกับจำนวนแท็ป $N$**

**บทวิเคราะห์เชิงลึกระดับสถาปัตยกรรม:**
* ในโครงสร้าง **Direct Form FIR**:
  * ผลคูณของแท็ปทั้งหมด 64 แท็ปจะต้องถูกนำมารวมกันใน Adder Tree
  * จำนวนระดับของ Adder Tree คือ $\lceil \log_2 64 \rceil = 6\text{ ระดับ}$
  * ความล่าช้าจะแปรผันตาม $O(\log_2 N)$ บวกกับความล่าช้าในการเดินสายข้ามชิป (Routing Congestion) ซึ่งจะทำให้ Critical Path ยาวเกินคาบเวลา $2.0\text{ ns}$ อย่างแน่นอน
* ในโครงสร้าง **Systolic FIR (Cascaded Architecture)**:
  * ผลลัพธ์ถูกสะสมและส่งต่อไปข้างหน้าทีละแท็ปผ่านสายทองแดงพิเศษ `PCOUT \to PCIN` ซึ่งวางชิดติดกันในคอลัมน์ DSP เดียวกัน
  * ในแต่ละจุดจะมี Flip-Flop คั่นกลาง (Local Pipeline Register)
  * ส่งผลให้เวลาหน่วงของ Critical Path มีค่าคงที่ $O(1)$ คือจำกัดอยู่เพียงภายใน DSP Slice ตัวเดียว ($t_{crit} \approx 1.2 - 1.5\text{ ns}$) เสมอ **ไม่ว่าจำนวนแท็ปจะขยายเป็น 64, 128 หรือ 512 แท็ปก็ตาม** ระบบจึงสามารถคงความเร็ว $500\text{ MHz}$ ได้อย่างสบาย

---

### ข้อที่ 3: กฎการอนุรักษ์ช่วงไดนามิก (Dynamic Range) ในวงจรสะสมผลรวม (Accumulator)
พิจารณาวงจรสะสมผลรวม (MAC Unit) ที่รับข้อมูลอินพุต $x[n]$ ขนาด 16 บิต (Signed Two's Complement: ค่าตั้งแต่ $-32,768$ ถึง $+32,767$) คูณกับสัมประสิทธิ์ $c[n]$ ขนาด 16 บิต (Signed) 

ผลคูณแต่ละครั้งจะมีขนาด $32\text{ บิต}$ หากวงจรทำการสะสมผลบวกต่อเนื่องกัน $K = 1,024\text{ ครั้ง}$ (1024-point Accumulation):

เพื่อรับประกันว่าตัวสะสมผลลัพธ์ (Accumulator Register) จะ **ไม่มีทางเกิดการล้น (Zero Overflow Risk)** ภายใต้สัญญาณอินพุตใดๆ โดยไม่ต้องมีวงจรลดทอนสัญญาณ ขนาดบิตขั้นต่ำของ Accumulator Register ($W_{accum}$) จะต้องมีอย่างน้อยกี่บิต?

a) $32\text{ บิต}$  
b) $40\text{ บิต}$  
c) $42\text{ บิต}$  
d) $48\text{ บิต}$  

---

#### เฉลยและบทวิเคราะห์เชิงลึกข้อที่ 3
**คำตอบที่ถูกต้องคือ: c) $42\text{ บิต}$**

**ขั้นตอนการคำนวณทางคณิตศาสตร์:**
1. คำนวณขนาดบิตของผลคูณเดี่ยว:
   $$W_{mult} = 16\text{ บิต} + 16\text{ บิต} = 32\text{ บิต}$$
   (ค่าสูงสุดที่เป็นไปได้คือ $(-32768) \times (-32768) = +1,073,741,824 \approx 2^{30}$)
2. คำนวณการเติบโตของบิตจากการบวกสะสม $K$ ครั้ง (Bit Growth from Accumulation):
   $$\text{Bit Growth} = \lceil \log_2 K \rceil$$
   เมื่อ $K = 1,024\text{ ครั้ง}$:
   $$\text{Bit Growth} = \lceil \log_2(1024) \rceil = 10\text{ บิต}$$
3. คำนวณขนาดบิตรวมขั้นต่ำที่จำเป็นของ Accumulator:
   $$W_{accum\_min} = W_{mult} + \text{Bit Growth} = 32\text{ บิต} + 10\text{ บิต} = 42\text{ บิต}$$
4. **ความสอดคล้องกับฮาร์ดแวร์จริง:**
   * สถาปัตยกรรม DSP48E2 ถูกออกแบบให้ Accumulator มีขนาด **48 บิต** พอดี ซึ่งมากกว่า 42 บิต จึงสามารถรองรับการสะสมผลคูณ 16-bit ได้สูงสุดถึง $2^{48 - 32} = 2^{16} = 65,536\text{ ครั้ง}$ อย่างปลอดภัย $100\%$ โดยไม่มีทางเกิด Overflow ในซิลิคอน
