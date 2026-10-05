# Lesson 131: FPGA DSP Slices - Part 1 (Architecture & Internal ALU - DSP48E2 Architecture, Pre-Adder, Multiplier, Accumulator)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมระดับซิลิคอนของ DSP48E2 (DSP48E2 Silicon Microarchitecture)
ในการประมวลผลสัญญาณดิจิทัลความเร็วสูง (High-Speed DSP) เช่น อัลกอริทึมเรดาร์ (Radar Pulse Compression), ตัวกรองสัญญาณดิจิทัล (FIR/IIR Filtering), และการเร่งความเร็วโครงข่ายประสาทเทียม (Deep Learning GEMM Acceleration) การสร้างวงจรคูณและบวกสะสมด้วยผืนลอจิก Look-Up Table (LUT Fabric) ทั่วไปจะทำให้สูญเสียพื้นที่และพลังงานมหาศาล อีกทั้งความเร็ว $F_{max}$ จะถูกจำกัดไว้ไม่เกิน $200 - 300\text{ MHz}$

ผู้ผลิต FPGA ชั้นนำจึงได้ฝังบล็อกฮาร์ดแวร์เฉพาะกิจความเร็วสูง (Hard Macro) เรียกว่า **DSP Slice** (เช่น **DSP48E2** บน AMD Xilinx UltraScale/UltraScale+ หรือ **Variable Precision DSP** บน Intel Stratix 10/Agilex) ซึ่งสามารถทำงานได้ที่ความถี่สูงถึง **$741\text{ MHz} - 891\text{ MHz}$**

```
                 สถาปัตยกรรมภายในของ Xilinx DSP48E2 Hard Macro
   
   D (27-bit) ---+
                 |
                 v
   A (30-bit) ->[ Pre-Adder ]---> (27-bit) --+
                [   D +/- A ]                |
                                             v
   B (18-bit) ----------------------------->[ 27 x 18 Multiplier ]---> (45-bit M) ---+
                                                                                       |
   C (48-bit) -------------------------------------------------------------------------+
                                                                                       |
   PCIN (48-bit Cascade) --------------------------------------------------------------+
                                                                                       |
                                                                                       v
                                                                                [ W / X / Y / Z MUX ]
                                                                                       |
                                                                                       v
                                                                                [ 48-bit Full ALU ]
                                                                                [  Add / Sub / Logic ]
                                                                                       |
                                                                                       +---> P (48-bit Out)
                                                                                       |
                                                                                       +---> PCOUT (Cascade)
```

#### 1.1.1 องค์ประกอบพอร์ตอินพุตและโครงสร้างคณิตศาสตร์ของ DSP48E2
1. **พอร์ต A (30-bit Signed) และ พอร์ต B (18-bit Signed):**
   * อินพุตการคูณสองส่วนเติมเต็ม (Two's Complement Multiplier)
   * รองรับการคูณขนาด $27 \times 18$ บิตแบบ Sign-Extended ภายใน หรือใช้ $A[29:0]$ ขนาดเต็ม 30 บิต ร่วมกับลอจิก ALU
2. **พอร์ต D (27-bit Signed) และ Pre-Adder:**
   * พรีแอดเดอร์ในตัวสามารถคำนวณ:
     $$\text{Pre-add Out} = D \pm A[26:0]$$
   * ช่วยลดจำนวน DSP Slice ลงได้ถึง **$50\%$** เมื่อออกแบบ Symmetric FIR Filter โดยการบวกค่าตัวอย่างคู่สมมาตรเข้าด้วยกันก่อนส่งเข้าตัวคูณ
3. **ตัวคูณขนาด $27 \times 18$ บิต (Two's Complement Multiplier):**
   * สร้างผลคูณขนาด 45 บิต ($M[44:0]$) โดยคำนวณในระดับฮาร์ดแวร์ Carry-Save แบบความเร็วสูง
4. **พอร์ต C (48-bit Signed) และ 48-bit ALU / Accumulator:**
   * สามารถทำการบวกสะสม (Accumulate), ลบ (Subtract), หรือส่งผ่านค่าจาก Cascade Bus ($PCIN$)
   * สมการทางคณิตศาสตร์หลักของเอาต์พุต $P$:
     $$P = Z \pm (X + Y + CIN)$$
     โดยที่ $X, Y, Z, W$ ถูกเลือกจาก MUX ควบคุมด้วยสัญญาณ `OPMODE[8:0]`

---

### 1.2 โหมดการทำงานของ 48-bit ALU: Arithmetic vs SIMD Mode
ALU ภายใน DSP48E2 ไม่ได้จำกัดอยู่เพียงการบวกสะสมแบบ 48 บิตเดี่ยว (Scalar Accumulation) แต่สามารถกำหนดค่าให้ทำงานในโหมด **SIMD (Single Instruction Multiple Data)** ได้ผ่านแอตทริบิวต์ `USE_SIMD`:

```
+--------------------+------------------------------------+---------------------------------------------------+
| โหมด SIMD          | โครงสร้างการแบ่งบิต               | ประโยชน์ทางวิศวกรรม (Engineering Benefits)        |
+--------------------+------------------------------------+---------------------------------------------------+
| 1. ONE48 (Default) | ตัวบวก/ลบ 48 บิตเดี่ยว              | ใช้สำหรับ Accumulator ความแม่นยำสูง, 48-bit MAC   |
| 2. TWO24           | ตัวบวก/ลบ 24 บิตคู่ขนาน 2 ชุด      | ประมวลผลสัญญาณเสียง HD Audio 24-bit 2 แชนเนลพร้อมกัน|
| 3. FOUR12          | ตัวบวก/ลบ 12 บิตคู่ขนาน 4 ชุด      | เร่งความเร็วการประมวลผล ADC 12 บิต 4 ช่องทางพร้อมกัน|
+--------------------+------------------------------------+---------------------------------------------------+
```

ในโหมด SIMD ลอจิก Carry Chain ภายใน 48-bit ALU จะถูกตัดการเชื่อมต่อที่ขอบเขตบิตที่กำหนด ($Bit\ 23/24$ หรือ $Bit\ 11/12, 23/24, 35/36$) ทำให้สามารถประมวลผลข้อมูลขนาดเล็กหลายเวกเตอร์ได้พร้อมกันในรอบสัญญาณนาฬิกาเดียวโดยปราศจากการรบกวนของ Carry Overflow

---

### 1.3 การอนุมานฮาร์ดแวร์ (DSP Hardware Inferencing vs Direct Instantiation)
การเขียนโค้ด HDL เพื่อให้ Synthesis Tool (เช่น Vivado) สามารถดึงบล็อก DSP48E2 มาใช้งานได้อย่างสมบูรณ์ (Inferencing) จำเป็นต้องปฏิบัติตามกฎเกณฑ์โครงสร้างโค้ดอย่างเคร่งครัด:

```
                  กฎการเขียน RTL เพื่อให้ได้ Hard DSP48E2 100%
   
   [ ถูกต้อง: แมปปิ้งลง DSP48E2 Hard Macro ]
   - กว้างไม่เกิน: D <= 27, A <= 27 (สำหรับ Pre-adder), B <= 18
   - สัญญาณรีเซ็ต: Synchronous Reset เท่านั้น (ห้าม Asynchronous Reset!)
   - มี Register กั้น: A_reg, B_reg, M_reg, P_reg อย่างน้อย 3-4 ระดับ
   
   [ ผิดพลาด: หลุดไปสังเคราะห์เป็น LUT Fabric ]
   - กำหนดขนาด D = 32 บิต หรือ A = 32 บิต ในการบวก Pre-adder
   - ใส่ Asynchronous Reset (if (rst) p <= 0;) -> DSP ฮาร์ดแวร์ไม่มีขา Async Reset!
   - รวมลอจิก MUX ซับซ้อนขวางทางระหว่างตัวคูณและตัวบวกสะสม
```

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Pre-Adder + Multiplier + Accumulator MAC Engine

```systemverilog
//=============================================================================
// Module: dsp48e2_mac_engine.sv
// Description: Fully Inferred DSP48E2 Engine with Pre-Adder and Accumulator
// Target Architecture: AMD Xilinx UltraScale+ (-2 Speed Grade Target: 700MHz)
//=============================================================================
`timescale 1ns / 1ps

module dsp48e2_mac_engine #(
    parameter int D_WIDTH = 27,
    parameter int A_WIDTH = 27,
    parameter int B_WIDTH = 18,
    parameter int P_WIDTH = 48
)(
    input  logic                      clk,
    input  logic                      rst_sync, // ห้ามใช้ Asynchronous Reset!
    input  logic                      accum_clr,
    // อินพุตข้อมูลตามขนาดฮาร์ดแวร์จริงของ DSP48E2
    input  logic signed [D_WIDTH-1:0] d_in,
    input  logic signed [A_WIDTH-1:0] a_in,
    input  logic signed [B_WIDTH-1:0] b_in,
    // เอาต์พุตผลลัพธ์การคูณสะสม 48 บิต
    output logic signed [P_WIDTH-1:0] p_out
);

    // Stage 1: Input Pipeline Registers (DREG, AREG, BREG)
    logic signed [D_WIDTH-1:0] d_reg;
    logic signed [A_WIDTH-1:0] a_reg;
    logic signed [B_WIDTH-1:0] b_reg1;
    logic signed [B_WIDTH-1:0] b_reg2;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            d_reg <= '0;
            a_reg <= '0;
            b_reg1 <= '0;
        end else begin
            d_reg  <= d_in;
            a_reg  <= a_in;
            b_reg1 <= b_in;
        end
    end

    // Stage 2: Pre-Adder Stage (ADREG)
    // การบวก (D + A) ต้องตรงตามขนาด 27 บิตเพื่อเข้า Pre-adder ในชิป
    logic signed [D_WIDTH:0]   pre_add_result; // 28 bits with carry
    logic signed [D_WIDTH-1:0] ad_reg;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            ad_reg <= '0;
            b_reg2 <= '0;
        end else begin
            // บีบขนาดผลลัพธ์พรีแอดเดอร์ให้อยู่ใน 27 บิตสำหรับตัวคูณ
            ad_reg <= d_reg + a_reg;
            b_reg2 <= b_reg1; // จับคู่เวลาให้ตรงกับสเตจ Pre-adder
        end
    end

    // Stage 3: Multiplier Stage (MREG)
    // ผลคูณขนาด 27 x 18 = 45 บิต
    logic signed [44:0] mult_reg;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            mult_reg <= '0;
        end else begin
            mult_reg <= ad_reg * b_reg2;
        end
    end

    // Stage 4: 48-bit Accumulator Stage (PREG)
    logic signed [P_WIDTH-1:0] p_accum_reg;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            p_accum_reg <= '0;
        end else if (accum_clr) begin
            p_accum_reg <= mult_reg; // เริ่มต้นรอบสะสมใหม่
        end else begin
            p_accum_reg <= p_accum_reg + mult_reg; // สะสมต่อเนื่อง
        end
    end

    assign p_out = p_accum_reg;

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในโครงการพัฒนาเรดาร์ประมวลผลเป้าหมายตรวจจับระยะไกล (AESA Radar Pulse Compression Processor) บนชิป Kintex UltraScale+ FPGA กำหนดความถี่สัญญาณนาฬิกา $f_{clk} = 600\text{ MHz}$ ($T_{clk} = 1.667\text{ ns}$) วิศวกรออกแบบโมดูลคูณกรองสัญญาณดิจิทัล โดยกำหนดความกว้างบิตอินพุตตามมาตรฐานทั่วไป $A = 32\text{ บิต}$, $D = 32\text{ บิต}$, และ $B = 32\text{ บิต}$ และเขียนสมการ `result <= (d_in + a_in) * b_in;` ลงในโค้ด Verilog

**ผลลัพธ์ที่ล้มเหลว:** เมื่อรันการสังเคราะห์และ Place & Route รายงาน Vivado STA แจ้งเตือนความล้มเหลวด้านเวลาอย่างรุนแรง: $WNS = -1.240\text{ ns}$ เมื่อตรวจสอบ Schematic พบว่า วงจร Pre-Adder ไม่ได้ถูกสังเคราะห์ลงในบล็อก DSP48E2 แต่กลับถูกดันออกไปสร้างเป็น **Logic LUT Fabric จำนวนกว่า 90 LUTs** ต่อเรียงกันขวางหน้าทางเข้า DSP Slice ทำให้เกิดความหน่วงเวลาเดินสายและ Logic Depth ถึง 4 ระดับ ส่งผลให้ระบบเรดาร์ประมวลผลข้อมูลตกหล่น (Data Starvation)

```
                 สาเหตุความล้มเหลวจากการกำหนดพอร์ตบิตเกินสเปก DSP
   
   [ จินตนาการของวิศวกร: หวังให้ลง Hard Macro ทั้งหมด ]
   (32-bit D + 32-bit A) ---> [ Pre-Adder ] ---> * 32-bit B ---> [ DSP48E2 ] (ล้มเหลว!)
   
   [ สิ่งที่เกิดขึ้นจริงในซิลิคอน: ทะลักออกสู่ LUT Fabric ]
   32-bit D ---+
               v
   32-bit A -> [ 90 x LUT6 Fabric Adder ] ----> สายไฟยาว 1.5ns ----> [ DSP48E2 ]
               <--- Delay = 1.85 ns --->                             (Multiplier)
   
   ผลลัพธ์: ลอจิกพรีแอดเดอร์ใน LUT แบกรับความหน่วงเกินพิกัด -> Setup Slack ติดลบ -1.24ns!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมระบบเรดาร์ถึงเกิด Timing Violation รุนแรงและประมวลผลข้อมูลไม่ทัน?**
   * *ตอบ:* เส้นทางสัญญาณขาเข้าของวงจรคูณกรองสัญญาณมีความหน่วงเวลาเกินคาบสัญญาณนาฬิกา $1.667\text{ ns}$
2. **ทำไมเส้นทางสัญญาณขาเข้าถึงมีความหน่วงเวลายาวนานผิดปกติ?**
   * *ตอบ:* วงจร Pre-Adder ถูกสร้างขึ้นจาก Soft LUT Fabric ภายนอก แทนที่จะใช้ Hard Pre-Adder ภายในชิป DSP48E2
3. **ทำไมโปรแกรมสังเคราะห์วงจรถึงไม่ใช้ Hard Pre-Adder ในตัว DSP48E2?**
   * *ตอบ:* สัญญาณอินพุต $A$ และ $D$ ถูกกำหนดขนาดความกว้างไว้ที่ $32$ บิต
4. **ทำไมขนาด 32 บิตถึงทำให้ฮาร์ดแวร์ปฏิเสธการสังเคราะห์?**
   * *ตอบ:* ฮาร์ดแวร์ซิลิคอนของ Pre-Adder ภายใน DSP48E2 รองรับขนาดสัญญาณสูงสุดเพียง **$27$ บิต** เท่านั้น เมื่อเกินสเปก ตัวคอมไพเลอร์จำเป็นต้องดึงลอจิกทั้งหมดออกไปสร้างบน LUT Fabric
5. **ทำไมวิศวกรจึงกำหนดขนาดพอร์ตเป็น 32 บิตโดยไม่ตรวจสอบ?**
   * *ตอบ:* วิศวกรเคยชินกับการเขียนโค้ดตามมาตรฐานข้อมูล 32 บิตของซอฟต์แวร์ และไม่ได้เปิดอ่านคู่มือสถาปัตยกรรมระดับฮาร์ดแวร์ (Xilinx UG579: UltraScale Architecture DSP48E2 User Guide)

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ DSP Pre-Adder Spillover
   
   การศึกษาคู่มือสเปก (Documentation)            การออกแบบสถาปัตยกรรม RTL (RTL Coding)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ไม่ได้อ่าน     เข้าใจผิดว่า                   ใช้ชนิดข้อมูล  ไม่มีการทำ Bit
   UG579 DSP     DSP Slice รองรับ               32-bit ล้วน   Truncation หรือ
   User Guide    พอร์ต 32 บิตทุกขา              ตามความเคยชิน Scaling ให้เหลือ 27บิต
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> WNS ติดลบ -1.24ns
                                                                |     ระบบเรดาร์ล้มเหลว
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   ความถี่เป้าหมาย สภาพแวดล้อม                   ไม่รันคำสั่ง    ไม่ได้ตรวจสอบ
   สูงถึง 600MHz  ทางกายภาพของ                   check_timing  Utilization Report
   (T_clk = 1.6ns)ซิลิคอนจำกัด                   อย่างละเอียด  ว่ามี LUT ปนหรือไม่
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   เป้าหมายประสิทธิภาพ (Performance Goal)        การตรวจสอบในขั้นตอนคอมไพล์ (EDA Audit)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ตรวจสอบรายงานการแมปปิ้ง DSP ใน Vivado Log
หลังขั้นตอน `Synthesis` ให้ตรวจสอบไฟล์ `runme.log` หรือรันคำสั่ง Tcl:
```tcl
report_utilization -hierarchical -filter {NAME =~ *dsp*}
```
มองหาตาราง `DSP48 Blocks` และตรวจสอบว่าสัญญาณถูกแมปเป็น Hard Macro หรือไม่:
```text
DSP48E2 Details:
  Pre-Adder: INFERRED (Yes)
  Multiplier: 27x18 (Full Hard Mapping)
  Accumulator: 48-bit (Full Hard Mapping)
```
หากมีข้อความเตือนว่า `Warning: [Synth 8-3971] Logic mapped to Fabric LUTs due to bit-width overflow` ต้องแก้ไขโค้ดทันที!

#### ขั้นตอนที่ 2: ปรับลดขนาดสัญญาณให้เข้ากับพอร์ตฟิสิกส์ (Bit Scaling & Saturation)
ปรับขนาดข้อมูลเซนเซอร์ ADC ให้เหลือไม่เกิน $27$ บิตสำหรับพอร์ต $A$ และ $D$, และไม่เกิน $18$ บิตสำหรับพอร์ต $B$:
```systemverilog
// กฎเหล็กสำหรับการแมปปิ้ง DSP48E2
wire signed [26:0] d_dsp_in = d_raw[31:5]; // Truncate หรือ Rounding
wire signed [26:0] a_dsp_in = a_raw[31:5];
wire signed [17:0] b_dsp_in = b_raw[31:14];
```

#### ขั้นตอนที่ 3: เปิดใช้งานการใส่รีจิสเตอร์ขั้นต่ำ 3 ระดับ
เพื่อให้วิ่งได้ถึง $600\text{ MHz}+$ ต้องมีอินสแตนซ์ของ Register ครบทั้ง 3 สเตจ: `AREG/BREG/DREG (Stage 1)`, `ADREG/MREG (Stage 2)`, และ `PREG (Stage 3)`

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| DSPスライス | でぃーえすぴーすらいす | Diiesupii Suraisu | DSP Slice (บล็อกประมวลผลสัญญาณฮาร์ดแวร์) |
| プリ加算器 | ぷりかさんき | Puri Kasanki | Pre-Adder (ตัวบวกสัญญาณขาเข้าล่วงหน้า) |
| 積和演算 | せきわえんざん | Sekiwa Enzan | Multiply-Accumulate (MAC) Operation |
| ハードマクロ推定 | はーどまくろすいてい | Haado Makuro Suitei | Hard Macro Inferencing |
| ビット幅制限 | びっとはばせいげん | Bitto-haba Seigen | Bit-width Constraint / Limitation |
| ファブリック漏れ | ふぁぶりっくもれ | Faburikku More | Fabric Spillover (การทะลักไปใช้ Soft LUT) |
| 同期リセット制約 | どうきりせっとせいやく | Douki Risetto Seiyaku | Synchronous Reset Constraint |
| 飽和演算 | ほうわえんざん | Houwa Enzan | Saturation Arithmetic |
| 内部パイプライン段数 | ないぶぱいぷらいんだんすう | Naibu Paipurain Dansuu | Internal Pipeline Stages |
| カスケード接続 | かすけーどせつぞく | Kasukeedo Setsuzoku | Dedicated Cascade Path (`PCOUT/PCIN`) |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** การประชุมตรวจแบบระบบเรดาร์ทางทหารและอวกาศ (Aerospace Radar DSP Architecture Kenzu)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** ชิราอิชิ ซัง (Shiraishi-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** โยชิโอกะ คุง (Yoshioka-kun)

---

**白石技師 (Shiraishi):**  
「吉岡君、この AESA レーダー用パルス圧縮フィルタの配置配線結果だが、動作周波数 600MHz に対して WNS が $-1.240\text{ ns}$ で大幅に破綻しているぞ。配置図（Device View）を確認すると、DSP48E2 の前段に大量の LUT ロジックが散乱しているが、プリ加算器（Pre-Adder）をハードマクロ内にインファー（Infer）させていないのかね？」  
*(Yoshioka-kun, kono AESA reeda-you parusu asshuku firuta no haichi haisen kekka dakedo, dousa shuuhasuu 600MHz ni taishite WNS ga $-1.240\text{ ns}$ de oohaba ni hatan shite iru zo. Haichizu (Device View) wo kakunin suru to, DSP48E2 no zendan ni tairyou no LUT rojikku ga sanran shite iru ga, puri kasanki (Pre-Adder) wo haado makuro nai ni infaa (Infer) sasete inai no kane?)*  
**ความหมาย:** คุณโยชิโอกะ ผลการ Place & Route ของฟิลเตอร์บีบอัดพัลส์เรดาร์ AESA ตัวนี้ ที่ความถี่ 600MHz ค่า WNS พังยับเยินถึง $-1.240\text{ ns}$ เลยนะ พอเปิดดูผังชิป (Device View) กลับเจอลอจิก LUT กระจัดกระจายอยู่หน้าบล็อก DSP48E2 เต็มไปหมด ไม่ทราบว่าไม่ได้ออกแบบให้ Pre-Adder มันสังเคราะห์ลงในตัว Hard Macro หรอกหรือครับ?

---

**吉岡技師 (Yoshioka):**  
「はい、白石さん。RTL 上では `result <= (d_data + a_data) * b_coeff;` と 1 行で簡潔に記述いたしました。ハードウェア記述言語上では正しくプリ加算と乗算を指定しておりますので、Vivado の合成ツールが自動的に DSP48E2 のプリ加算器に割り当ててくれると信じておりました。」  
*(Hai, Shiraishi-san. RTL jou de wa `result <= (d_data + a_data) * b_coeff;` to ichigyou de kanketsu ni kijutsu itashimashita. Haadowea kijutsu gengo jou de wa tadashiku puri kasan to jouzan wo shitei shite orimasu node, Vivado no gousei tsuuru ga jidouteki ni DSP48E2 no puri kasanki ni wariatete kureru to shinjite orimashita.)*  
**ความหมาย:** ครับคุณชิราอิชิ ในโค้ด RTL ผมเขียนบรรทัดเดียวสั้นๆ กระชับว่า `result <= (d_data + a_data) * b_coeff;` ครับ ในเมื่อภาษาฮาร์ดแวร์ระบุการพรีแอดและคูณไว้ชัดเจน ผมจึงเชื่อมั่นว่า Vivado จะนำไปแมปลงใน Pre-Adder ของ DSP48E2 ให้อัตโนมัติครับ

---

**白石技師 (Shiraishi):**  
「ツールの自動推論任せでハードウェアの物理構造をまるで見ていないな！DSP48E2 のデータシート（UG579）を読んだことがあるのか？プリ加算器の入力ポート $A$ と $D$ の物理制限は**最大 27 ビット**だ！君のコードでは `d_data` も `a_data` も 32 ビットで宣言されている。27 ビットの上限を超えた瞬間、ツールはプリ加算器の利用を諦めて、ファブリックの LUT に 32 ビット加算器を追い出してしまうんだ！600MHz の高周波回路で LUT 加算器の遅延を挟めばタイミングが破綻するのは当たり前だ！**重大指摘事項とする！** 直ちに信号の上位 27 ビットへのスケーリングを行い、非同期リセットを排除して完全同期化し、ハードマクロ内への 100% 収容を達成しなさい！」  
*(Tsuuru no jidou suiron makase de haadowea no butsuri kouzou wo marude mite inai na! DSP48E2 no deetashiito (UG579) wo yonda koto ga aru no ka? Puri kasanki no nyuuryoku pooto $A$ to $D$ no butsuri seigen wa **saidai 27-bitto** da! Kimi no koudo dewa `d_data` mo `a_data` mo 32-bitto de sengen sarete iru. 27-bitto no jougen wo koeta shunkan, tsuuru wa puri kasanki no riyou wo akiramete, faburikku no LUT ni 32-bitto kasanki wo oidashite shimaunda! 600MHz no kou-shuuhasuu kairo de LUT kasanki no chien wo hasameba taimingu ga hatan suru no wa atarimae da! **Juudai shiteki jikou to suru!** Tadachini shingou no joui 27-bitto e no sukeeringu wo okonai, hidouki risetto wo haijo shite kanzen doukika shi, haado makuro nai e no 100% shuuyou wo tassei shinasai!)*  
**ความหมาย:** ฝากความหวังไว้กับการเดาของ Tool โดยไม่สนใจกายภาพของฮาร์ดแวร์เลยนะ! เคยเปิดอ่านคู่มือ DSP48E2 (UG579) บ้างหรือเปล่า? ขีดจำกัดทางกายภาพของพอร์ต Pre-Adder ขา $A$ และ $D$ มันคือ**สูงสุดแค่ 27 บิต**เท่านั้น! แต่ในโค้ดของเธอ ทั้ง `d_data` และ `a_data` ประกาศไว้ 32 บิต วินาทีที่ขนาดบิตเกิน 27 บิต Tool มันจะยอมแพ้และเตะวงจรบวก 32 บิตออกไปสร้างบน Soft LUT ข้างนอกทันที! ในวงจรความถี่สูงถึง 600MHz การมีลอจิกบวกใน LUT มาขวางหน้า เวลาจะไม่พังได้อย่างไร! **ผมสั่งเป็นข้อแก้ไขระดับวิกฤต!** จงรีบสเกลบิตข้อมูลให้เหลือ 27 บิต ตัด Asynchronous Reset ทิ้งให้เป็น Synchronous 100% เพื่อให้วงจรทั้งหมดถูกบรรจุลงใน Hard Macro โดยด่วน!

---

**吉岡技師 (Yoshioka):**  
「DSP48E2 の物理ポート制限が 27 ビットであったとは…データシートの確認不足を痛感いたしました。直ちにビット幅を 27 ビットに整合させ、ファブリック漏れを完全に解消した上で 600MHz でのタイミング収束を確認して再提出いたします！」  
*(DSP48E2 no butsuri pooto seigen ga 27-bitto de atta to wa... deetashiito no kakunin busoku wo tsuukan itashimashita. Tadachini bitto-haba wo 27-bitto ni seigou sase, faburikku more wo kanzen ni kaishou shita ue de 600MHz de no taimingu shuusoku wo kakunin shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ขีดจำกัดทางกายภาพของ DSP48E2 อยู่ที่ 27 บิต... ผมตระหนักถึงความบกพร่องในการศึกษา Data Sheet ของตัวเองแล้วครับ ผมจะรีบปรับขนาดบิตให้ตรงกับสเปก 27 บิต กำจัดการทะลักออกสู่ LUT ให้หมดสิ้น และตรวจสอบการปิด Timing ที่ 600MHz ให้ผ่านแล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณ Dynamic Range และจำนวนรอบการสะสมสูงสุดก่อนเกิด Overflow ใน DSP48E2

ในโมดูลประมวลผล FIR Filter วงจร DSP48E2 ทำการคูณสะสม (Multiply-Accumulate: MAC) อย่างต่อเนื่อง:
* อินพุต $A$ และ $D$ ผ่าน Pre-Adder ได้ผลลัพธ์ $27$ บิตแบบคิดเครื่องหมาย (Signed Two's Complement): ค่าสูงสุดคือ $2^{26}-1 \approx +6.71 \times 10^7$
* อินพุต $B$ (สัมประสิทธิ์ฟิลเตอร์) มีขนาด $18$ บิตแบบคิดเครื่องหมาย: ค่าสูงสุดคือ $2^{17}-1 = +131,071$
* ตัวคูณส่งผลลัพธ์ขนาด $45$ บิตเข้าสู่ Accumulator ขนาด $48$ บิต ($P[47:0]$)

หากสมมติสภาวะเลวร้ายที่สุด (Worst-case Constant Max Amplitude Input): อินพุตทุกตัวมีค่าสูงสุดตลอดเวลา จงคำนวณหาจำนวนรอบสัญญาณนาฬิกาการสะสมต่อเนื่องสูงสุด ($N_{max}$) ที่ Accumulator 48 บิตจะสามารถบวกทบค่าได้โดยที่ **ไม่เกิดการล้นค่า (Arithmetic Overflow)** เกินเพดาน $+2^{47}-1$?

---

#### ตัวเลือก:
A) $N_{max} = 4$ รอบสัญญาณนาฬิกา  
B) $N_{max} = 8$ รอบสัญญาณนาฬิกา  
C) $N_{max} = 16$ รอบสัญญาณนาฬิกา  
D) $N_{max} = 32$ รอบสัญญาณนาฬิกา

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) $N_{max} = 8$ รอบสัญญาณนาฬิกา**

##### ขั้นตอนที่ 1: คำนวณค่าผลคูณสูงสุดใน 1 รอบสัญญาณนาฬิกา ($M_{max}$)
ขนาดบิตของอินพุตตัวคูณ:
* สัญญาณขาเข้าตัวที่ 1 (จาก Pre-adder): ขนาด 27 บิตแบบคิดเครื่องหมาย $\Rightarrow X_{max} \approx 2^{26}$
* สัญญาณขาเข้าตัวที่ 2 ($B$): ขนาด 18 บิตแบบคิดเครื่องหมาย $\Rightarrow Y_{max} \approx 2^{17}$
ค่าผลคูณสูงสุดใน 1 รอบ:
$$M_{max} \approx 2^{26} \times 2^{17} = 2^{43}$$
*(หรือคิดแบบแม่นยำ: $(2^{26}-1) \times (2^{17}-1) \approx 2^{43} - 2^{26} - 2^{17} + 1 \approx 2^{43}$)*

##### ขั้นตอนที่ 2: คำนวณความจุการสะสมของ Accumulator 48 บิต ($P_{capacity}$)
Accumulator ภายใน DSP48E2 มีขนาด 48 บิตแบบคิดเครื่องหมาย:
ค่าบวกสูงสุดที่แทนค่าได้โดยไม่เกิด Overflow คือ:
$$P_{max} = 2^{47} - 1$$

##### ขั้นตอนที่ 3: คำนวณจำนวนรอบการสะสมสูงสุด ($N_{max}$)
จำนวนรอบสะสมก่อนล้นค่าคำนวณจาก:
$$N_{max} = \left\lfloor \frac{P_{max}}{M_{max}} \right\rfloor \approx \frac{2^{47}}{2^{43}} = 2^{47 - 43} = 2^4 = 16$$
*เดี๋ยวก่อน! ตรวจสอบขนาดของบิต Pre-Adder:*
Pre-Adder รับ $D$ (27 บิต) บวก $A$ (27 บิต):
ผลบวกของเลข 27 บิตสองตัวมีขนาดได้สูงสุดถึง **$28$ บิต** ($2 \times 2^{26} = 2^{27}$)!
เมื่อผลรวม 28 บิต ($2^{27}$) ถูกนำมาคูณกับ $B$ ($2^{17}$):
$$M_{max} = 2^{27} \times 2^{17} = 2^{44}$$
ดังนั้น จำนวนรอบการสะสมจริงสูงสุดก่อน Overflow คือ:
$$N_{max} \approx \frac{2^{47}}{2^{44}} = 2^{47 - 44} = 2^3 = 8 \text{ รอบสัญญาณนาฬิกา!}$$

##### นัยสำคัญทางวิศวกรรม:
เมื่อใช้ Pre-Adder เต็มสเกล ผลคูณจะกินพื้นที่ถึง 44 บิต เหลือ Headroom ให้บวกสะสมได้เพียง $48 - 44 = 4$ บิต (หรือ $2^3 - 2^4 = 8$ เท่า) หากฟิลเตอร์มีขนาด Tap ยาวเกินกว่า 8 Taps วิศวกรจะต้องทำการ **ลดทอนสเกลของสัมประสิทธิ์ (Coefficient Scaling / Attenuation)** เพื่อป้องกันไม่ให้เกิดความเสียหายจากการบวกทับ Overflow!

---

### คำถามที่ 2: การเปรียบเทียบ Throughput และจำนวน Slice ในโหมด SIMD FOUR12

ในระบบเร่งความเร็วโครงข่ายประสาทเทียม (Deep Learning CNN Inference Engine) ต้องการคำนวณการบวกสะสมข้อมูลขนาด 12 บิต (12-bit Integer Addition) จำนวน $100,000,000$ เวกเตอร์ต่อวินาที:
* หากใช้ **วิธีที่ 1 (โหมดมาตรฐาน ONE48):** แต่ละ DSP Slice สามารถประมวลผลการบวก 12 บิตได้เพียง $1$ ช่องสัญญาณต่อไซเคิล
* หากใช้ **วิธีที่ 2 (โหมด SIMD FOUR12):** แต่ละ DSP Slice จะตัด Carry Chain ออกเป็น 4 ส่วน และทำการบวก 12 บิตได้พร้อมกัน $4$ แชนเนลในไซเคิลเดียว

หากระบบทำงานที่ความถี่สัญญาณนาฬิกา $f_{clk} = 500\text{ MHz}$ จงคำนวณหาจำนวน DSP Slice ขั้นต่ำที่ต้องใช้ในวิธีที่ 2 เทียบกับวิธีที่ 1?

---

#### ตัวเลือก:
A) วิธีที่ 1: ต้องใช้ 1 Slice, วิธีที่ 2: ต้องใช้ 1 Slice (เนื่องจากความถี่ 500MHz สูงพอรองรับทั้งคู่)  
B) วิธีที่ 1: ต้องใช้ 4 Slices, วิธีที่ 2: ต้องใช้ 1 Slice  
C) วิธีที่ 1: ต้องใช้ 8 Slices, วิธีที่ 2: ต้องใช้ 2 Slices  
D) ไม่สามารถรัน SIMD ได้ที่ 500MHz

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) วิธีที่ 1: ต้องใช้ 1 Slice, วิธีที่ 2: ต้องใช้ 1 Slice (เนื่องจากความถี่ 500MHz สูงพอรองรับทั้งคู่)**  
*(หรือหากมองในมุมของ Throughput สูงสุดที่ทำได้):*
ที่ความถี่ $f_{clk} = 500\text{ MHz} = 500 \times 10^6\text{ cycles/second}$:
* ในวิธีที่ 1 (ONE48): 1 DSP Slice ให้สมรรถนะสูงสุด $= 500 \times 10^6\text{ ops/second}$ (500 MOPS)
* ในวิธีที่ 2 (FOUR12): 1 DSP Slice ให้สมรรถนะสูงสุด $= 4 \times 500 \times 10^6 = 2,000 \times 10^6\text{ ops/second}$ (**2.0 GOPS**)!
เนื่องจากโจทย์ต้องการเพียง $100\text{ MOPS}$ ($100,000,000$ ops/s) ทั้งสองวิธีจึงใช้เพียง 1 Slice แต่ในระบบประมวลผลขนาดใหญ่ โหมด FOUR12 ช่วย **ลดการใช้ทรัพยากร DSP ลงได้ถึง $75\%$ (ลดลง 4 เท่า)** เมื่อเทียบกับการใช้โหมดปกติ

---

### คำถามที่ 3: ข้อห้ามในการใช้ Asynchronous Reset บนโมดูล DSP48E2

เหตุใดการใส่โค้ด `if (rst_n == 0) p_out <= 0;` (Asynchronous Clear) จึงเป็นข้อห้ามร้ายแรงสำหรับวงจร DSP48E2 ใน FPGA?

---

#### ตัวเลือก:
A) เพราะทำให้แรงดันไฟฟ้าของชิปตกชั่วขณะ  
B) เพราะบล็อกฮาร์ดแวร์ DSP48E2 บนซิลิคอนมีเฉพาะขา **Synchronous Reset (RSTP, RSTA, RSTB)** เท่านั้น การใส่ Asynchronous Reset จะทำให้คอมไพเลอร์ไม่สามารถแมปลง Hard Macro ได้ และต้องดึง Flip-Flop ทั้งหมดออกไปสังเคราะห์บน Soft Fabric แทน  
C) เพราะทำให้เกิด Glitch บนสัญญาณนาฬิกา  
D) เพราะขัดต่อกฎของ Verilog-95

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เพราะบล็อกฮาร์ดแวร์ DSP48E2 บนซิลิคอนมีเฉพาะขา Synchronous Reset (RSTP, RSTA, RSTB) เท่านั้น การใส่ Asynchronous Reset จะทำให้คอมไพเลอร์ไม่สามารถแมปลง Hard Macro ได้ และต้องดึง Flip-Flop ทั้งหมดออกไปสังเคราะห์บน Soft Fabric แทน**

##### เหตุผลเชิงกายภาพของ Hard Macro:
วิศวกรผู้ออกแบบชิปของ AMD/Xilinx ได้สร้างเซลล์ DSP48E2 โดยตัดวงจรทรานซิสเตอร์สำหรับ Asynchronous Clear ออกทั้งหมด เพื่อให้สามารถทำความเร็วได้สูงถึง $700\text{ MHz}+$ และประหยัดพื้นที่ซิลิคอน ดังนั้นขาควบคุมทั้งหมด (`RSTA`, `RSTB`, `RSTC`, `RSTD`, `RSTM`, `RSTP`) จึงทำงานเฉพาะที่ **ขอบขาขึ้นของสัญญาณนาฬิกา (Synchronous)** เท่านั้น!

หากวิศวกรเขียน Sensitivity List เป็น `always_ff @(posedge clk or negedge rst_n)` คอมไพเลอร์จะไม่สามารถเชื่อมขา `rst_n` เข้าสู่เซลล์ DSP ได้โดยตรง และจะถูกบังคับให้แยก Flip-Flop ของเอาต์พุตและตัวคูณออกไปสร้างใน Logic Slices ภายนอก ทำให้สูญเสียประสิทธิภาพของ Hard DSP ไปโดยสิ้นเชิง
