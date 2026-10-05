# Lesson 132: FPGA DSP Slices - Part 2 (Pipelining & Maximum Fmax Retiming - MREG, PREG, INMODE Pipeline Registers)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ลำดับขั้นของรีจิสเตอร์ภายใน DSP48E2 (Internal Pipeline Stage Anatomy)
ความเร็วสูงสุด ($F_{max}$) ของบล็อก DSP บน FPGA ถูกกำหนดโดยฟิสิกส์ของการเชื่อมต่อวงจรคูณและวงจรบวกสะสม หากไม่มีการกั้นรีจิสเตอร์ สัญญาณไฟฟ้าจะต้องเดินทางผ่านโครงสร้าง Carry-Save Adder Array ขนาดใหญ่ภายในตัวคูณ ต่อเนื่องไปยัง 48-bit Carry-Propagate Adder ใน ALU ซึ่งจะก่อให้เกิดความหน่วงเวลาคอมบิเนชันสะสมสูงถึง $4.5 - 6.0\text{ ns}$ ส่งผลให้ความเร็วถูกจำกัดไว้ไม่เกิน $160 - 220\text{ MHz}$

เพื่อให้สามารถเร่งความเร็วไปแตะเพดานฟิสิกส์ของซิลิคอนที่ **$741\text{ MHz} - 891\text{ MHz}$** สถาปัตยกรรม DSP48E2 จึงถูกออกแบบให้มีรีจิสเตอร์ฝังในตัว (Dedicated Hard Pipeline Registers) มากถึง 4 ลำดับขั้น:

```
              โครงสร้าง Pipeline ภายใน DSP48E2 Hard Macro
   
   Inputs
   D, A, B --->[ AREG / BREG / DREG ] (Stage 1: Input Registers)
                          |
                          v
               [ Pre-Adder (D +/- A) ]
                          |
                          v
               [      ADREG         ] (Stage 2: Pre-Adder Register)
                          |
                          v
               [ 27 x 18 Multiplier  ]
                          |
                          v
               [      MREG          ] (Stage 3: Multiplier Register - กรอง Glitch!)
                          |
                          v
               [ 48-bit Full ALU     ]
                          |
                          v
   Outputs <---[      PREG          ] (Stage 4: Accumulator / Output Register)
```

#### 1.1.1 รายละเอียดการตั้งค่ารีจิสเตอร์แต่ละสเตจ
1. **Input Registers (`AREG = 1 or 2`, `BREG = 1 or 2`, `DREG = 1`):**
   * สำหรับพอร์ต $A$ และ $B$ สามารถเลือกใส่ Register ได้ถึง 2 ระดับ (`AREG=2, BREG=2`) เพื่อช่วยในการจัดสมดุลเวลา (Time Balancing) เมื่อข้อมูลต้องเดินทางข้ามคอลัมน์ DSP ที่อยู่ห่างไกล
2. **Pre-Adder Register (`ADREG = 1`):**
   * กั้นผลลัพธ์ระหว่าง Pre-Adder และ Multiplier ตัดทอนเส้นทางวิกฤตของตัวคูณ
3. **Multiplier Register (`MREG = 1`):**
   * **นี่คือรีจิสเตอร์ที่สำคัญที่สุดในระบบ!** ทำหน้าที่แลตช์ผลคูณ 45 บิตก่อนส่งเข้า ALU
   * *ประโยชน์ด้านพลังงาน:* โครงสร้าง Multiplier Array จะสร้าง Glitch ปริมาณมหาศาล การเปิดใช้งาน `MREG` จะดักจับ Glitch ไม่ให้ทะลุเข้าไปสลับขั้วใน 48-bit ALU ช่วยลด Dynamic Power ลงได้ถึง **$30 - 45\%$**!
4. **Output Register (`PREG = 1`):**
   * แลตช์ผลลัพธ์สุดท้าย 48 บิตที่ขา $P$ และส่งต่อไปยังสายทางด่วน Cascade ($PCOUT$)

---

### 1.2 แบบจำลองทางคณิตศาสตร์ของความถี่ $F_{max}$ เทียบกับจำนวนสเตจ Pipeline

```
+--------------------+-------------+--------------------+---------------------------------------------------+
| การกำหนดคอนฟิก     | Latency รวม | ความถี่ $F_{max}$  | พฤติกรรมทางเวลา (Timing Decomposition)            |
+--------------------+-------------+--------------------+---------------------------------------------------+
| 0-Stage (No Reg)   | 0 Clocks    | $180 - 220\text{ MHz}$| $T_{clk} \ge T_{in} + T_{mult} + T_{alu} + T_{out}$|
| 1-Stage (PREG only)| 1 Clock     | $320 - 380\text{ MHz}$| $T_{clk} \ge T_{in} + T_{mult} + T_{alu}$         |
| 2-Stage (MREG+PREG)| 2 Clocks    | $520 - 580\text{ MHz}$| $T_{clk} \ge \max(T_{mult}, T_{alu})$             |
| 3-Stage (A+M+P)    | 3 Clocks    | $680 - 750\text{ MHz}$| เส้นทางแยกขาดสมบูรณ์                              |
| 4-Stage (A+AD+M+P) | 4 Clocks    | $741 - 891\text{ MHz}$| **ขีดจำกัดสูงสุดของซิลิคอน (Silicon Limit)**       |
+--------------------+-------------+--------------------+---------------------------------------------------+
```

ความสัมพันธ์ระหว่างคาบเวลาต่ำสุด ($T_{clk\_min}$) ถูกกำหนดโดยเส้นทางย่อยที่ช้าที่สุด (Min-Max Bottleneck Formulation):

$$T_{clk\_min} = \max \left( T_{AREG \rightarrow ADREG}, T_{ADREG \rightarrow MREG}, T_{MREG \rightarrow PREG} \right) + T_{uncertainty}$$

หากขาด `MREG` เส้นทางวิกฤตจะกลายเป็นการรวมกันของ $T_{mult} + T_{alu} \approx 1.85\text{ ns} + 1.45\text{ ns} = 3.30\text{ ns}$ ซึ่งทำให้ $F_{max}$ ดิ่งลงเหลือเพียง $300\text{ MHz}$ ทันที

---

### 1.3 กับดักการดูดซับรีจิสเตอร์ (Register Absorption Failure & Clock Enable Traps)
แม้ว่าวิศวกรจะเขียน D-Flip-Flop ดักหน้าดักหลังในโค้ด Verilog ครบ 4 สเตจ แต่บ่อยครั้งที่พบว่า **Vivado ไม่ยอมดึง Flip-Flop เหล่านั้นเข้าไปอยู่ใน DSP48E2 (Failed to Absorb)** และทิ้งให้มันลอยอยู่บน Fabric Slices ภายนอก!

สาเหตุหลักที่ขัดขวางไม่ให้เกิด Register Absorption:
1. **การใช้ Asynchronous Reset:** DSP48E2 ไม่มีขารีเซ็ตแบบ Asynchronous
2. **Clock Enable Mismatch:** หากสัญญาณ `enable` ของรีจิสเตอร์ภายนอกไม่ตรงกับขา `CEA`, `CEB`, `CEM`, หรือ `CEP`
3. **การดึงสัญญาณกึ่งกลางออกไปใช้งานภายนอก (Internal Tap Fan-Out):** หากดึงเอาต์พุตของตัวคูณไประบายเข้าสู่โมดูลอื่นพร้อมๆ กัน Tool จะไม่สามารถแพ็คเข้าไปใน `MREG` ได้

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Fully Pipelined DSP48E2 พร้อมการควบคุม Directives

```systemverilog
//=============================================================================
// Module: fully_pipelined_dsp48e2.sv
// Description: Maximum Performance (741MHz+) DSP48E2 with Full Pipeline Absorption
// Target: AMD UltraScale+ Architecture (Speed Grade -2/-3)
//=============================================================================
`timescale 1ns / 1ps

module fully_pipelined_dsp48e2 #(
    parameter int D_W = 27,
    parameter int A_W = 27,
    parameter int B_W = 18,
    parameter int P_W = 48
)(
    input  logic              clk,
    input  logic              rst_sync, // บังคับ Synchronous Reset 100%
    input  logic              clk_en,   // สัญญาณ Enable ร่วมกันเพื่อดูดซับสมบูรณ์
    // ข้อมูลขาเข้า
    input  logic signed [D_W-1:0] d_in,
    input  logic signed [A_W-1:0] a_in,
    input  logic signed [B_W-1:0] b_in,
    input  logic signed [P_W-1:0] c_in,
    // ข้อมูลขาออก
    output logic signed [P_W-1:0] p_out
);

    // กำหนด Synthesis Attribute สั่งให้ Vivado แมปปิ้งและดูดซับ Register เต็มรูปแบบ
    (* use_dsp = "yes" *)
    logic signed [D_W-1:0] d_pipe1;
    logic signed [A_W-1:0] a_pipe1;
    logic signed [B_W-1:0] b_pipe1, b_pipe2;
    logic signed [P_W-1:0] c_pipe1, c_pipe2, c_pipe3;

    // Stage 1: Input Registers (DREG, AREG1, BREG1, CREG)
    always_ff @(posedge clk) begin
        if (rst_sync) begin
            d_pipe1 <= '0;
            a_pipe1 <= '0;
            b_pipe1 <= '0;
            c_pipe1 <= '0;
        end else if (clk_en) begin
            d_pipe1 <= d_in;
            a_pipe1 <= a_in;
            b_pipe1 <= b_in;
            c_pipe1 <= c_in;
        end
    end

    // Stage 2: Pre-Adder Stage (ADREG & BREG2)
    logic signed [D_W-1:0] ad_pipe;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            ad_pipe <= '0;
            b_pipe2 <= '0;
            c_pipe2 <= '0;
        end else if (clk_en) begin
            ad_pipe <= d_pipe1 + a_pipe1; // แมปลง Pre-adder ในชิป
            b_pipe2 <= b_pipe1;           // แมปลง BREG2
            c_pipe2 <= c_pipe1;           // ดีเลย์ C ให้ตรงจังหวะ
        end
    end

    // Stage 3: Multiplier Stage (MREG)
    logic signed [44:0] m_pipe;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            m_pipe  <= '0;
            c_pipe3 <= '0;
        end else if (clk_en) begin
            m_pipe  <= ad_pipe * b_pipe2; // แมปลง MREG ในชิป
            c_pipe3 <= c_pipe2;
        end
    end

    // Stage 4: ALU Accumulator / Adder Stage (PREG)
    logic signed [P_W-1:0] p_pipe;

    always_ff @(posedge clk) begin
        if (rst_sync) begin
            p_pipe <= '0;
        end else if (clk_en) begin
            p_pipe <= m_pipe + c_pipe3;   // แมปลง 48-bit ALU และ PREG
        end
    end

    assign p_out = p_pipe;

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในโครงการพัฒนาการ์ดประมวลผลสัญญาณเบสแบนด์ 5G Massive MIMO Beamforming บนชิป UltraScale+ FPGA สัญญาณนาฬิกาของระบบถูกกำหนดไว้ที่ $f_{clk} = 491.52\text{ MHz}$ ($T_{clk} = 2.035\text{ ns}$) วิศวกรเขียนโค้ดตัวคูณสะสมโดยใส่ D-Flip-Flop คั่นไว้ครบ 3 ระดับตามตำรา แต่เขียนคำสั่งรีเซ็ตเป็นแบบอะซิงโครนัส: `always_ff @(posedge clk or negedge rst_n)` ในทุกบล็อก

**ผลลัพธ์ที่ล้มเหลว:** เมื่อรัน Timing Analysis รายงาน STA แจ้งเตือนข้อผิดพลาดรุนแรง: $WNS = -0.920\text{ ns}$ เมื่อซูมดูผังวงจรจริงใน Vivado Device View พบว่า บล็อก DSP48E2 ถูกใช้งานเฉพาะตัวคูณเปล่าๆ ในขณะที่ Flip-Flop ทั้ง 3 ระดับ **ถูกเตะออกไปวางอยู่ใน Slice ภายนอกที่ห่างออกไปถึง 2.3 มิลลิเมตร** ทำให้เกิดความหน่วงเวลาเดินสายข้ามผืนชิปบวมขึ้นอย่างมหาศาล

```
                 หายนะของการใช้ Asynchronous Reset บน DSP Pipeline
   
   [ จินตนาการ: คาดหวังให้ Register ทั้งหมดถูกดูดเข้าไปใน DSP48E2 ]
   Inputs ---> [ AREG ] ---> [ Multiplier ] ---> [ MREG ] ---> [ PREG ] ---> Out (ล้มเหลว!)
   
   [ ความเป็นจริงในซิลิคอน: DSP ปฏิเสธ Async Reset! ]
               +---------------------------------------------+
               | Fabric Slice (ข้างนอก)                      |
               | [ Flip-Flops ที่มีขา Async Reset ]          |
               +----------------------+----------------------+
                                      |
                         สายไฟข้ามชิปยาว 2.3 mm (Delay = 1.45 ns)
                                      |
                                      v
               +---------------------------------------------+
               | Hard Macro DSP48E2                          |
               | (ตัวคูณและ ALU กลายเป็น Combinational ล้วน!)|
               +----------------------+----------------------+
                                      |
                         สายไฟวิ่งกลับไป Slice (Delay = 1.50 ns)
                                      |
                                      v
               +---------------------------------------------+
               | Fabric Slice Capture Register               |
               +---------------------------------------------+
   
   ผลลัพธ์: สัญญาณวิ่งเข้า-ออกระหว่าง Slice และ DSP ซ้ำซ้อน -> Slack ติดลบ -0.92ns!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมระบบประมวลผล 5G MIMO ถึงปิด Timing ไม่ลงที่ 491.52 MHz?**
   * *ตอบ:* เส้นทางสัญญาณคูณสะสมใน DSP มีความหน่วงเกินคาบเวลา $2.035\text{ ns}$
2. **ทำไมเส้นทางสัญญาณถึงมีความหน่วงเวลาเกินกว่าที่กำหนด?**
   * *ตอบ:* รีจิสเตอร์ไปป์ไลน์ทั้ง 3 สเตจไม่ได้ถูกบรรจุเข้าไปในเซลล์ DSP48E2 แต่ลอยอยู่นอกชิปบนผืน Fabric
3. **ทำไมรีจิสเตอร์ถึงไม่ถูกดูดซับ (Absorb) เข้าไปใน DSP48E2?**
   * *ตอบ:* คอมไพเลอร์ Vivado ไม่สามารถแมปรีจิสเตอร์ที่มีขารีเซ็ตแบบอะซิงโครนัสเข้ากับเซลล์ DSP ได้
4. **ทำไม Vivado ถึงไม่ยอมแมปรีจิสเตอร์ที่มีขารีเซ็ตอะซิงโครนัส?**
   * *ตอบ:* เซลล์ฮาร์ดแวร์จริงของ DSP48E2 บนซิลิคอนมีเฉพาะโครงสร้างขารีเซ็ตแบบ **Synchronous Reset** เท่านั้น
5. **ทำไมวิศวกรถึงใส่ขารีเซ็ตอะซิงโครนัสในโค้ด DSP?**
   * *ตอบ:* วิศวกรใช้เทมเพลตมาตรฐานของบริษัทที่กำหนดให้ทุกโมดูลต้องมี `if (!rst_n)` โดยไม่ได้ยกเว้นสำหรับบล็อกฮาร์ดแวร์เฉพาะกิจความเร็วสูง (Hard Macro)

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ DSP Pipeline Absorption
   
   เทมเพลตโค้ดองค์กร (Coding Template)           สถาปัตยกรรมระดับซิลิคอน (Silicon Architecture)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   บังคับใช้      ขาดข้อยกเว้น                  DSP48E2       ไม่มีวงจร
   Async Reset   สำหรับ Hard                    รองรับเฉพาะ    Async Reset
   กับทุกโมดูล   Macro IP                       Sync Reset    บนเซลล์ฮาร์ดแวร์
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> WNS ติดลบ -0.92ns
                                                                |     ระบบ 5G MIMO ล้มเหลว
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   ระยะทางสายไฟ  ความจุสาย                     ไม่ได้ดู       ขาดการตรวจ
   ระหว่าง Slice สูงจากการ                     DSP Pipeline   Post-Synthesis
   และ DSP > 2mm ลากสายไกล                     Report         Cell Primitives
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   ผลกระทบทางกายภาพ (Physical Layout)             การตรวจสอบในขั้นตอนคอมไพล์ (Verification)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ตรวจสอบสถานะการดูดซับ Pipeline Registers ใน Log File
เปิดไฟล์ `runme.log` และตรวจสอบตารางคุณสมบัติของ DSP:
```text
DSP Report: Generating DSP u_mimo/u_dsp_inst, operation Mode is: (A+D)*B+C
DSP48E2 Registers Utilization:
  AREG: 1 (Absorbed)
  BREG: 1 (Absorbed)
  MREG: 1 (Absorbed)  <--- ต้องขึ้นคำว่า Absorbed เท่านั้น!
  PREG: 1 (Absorbed)  <--- ห้ามขึ้นว่า Fabric Slices เด็ดขาด!
```

#### ขั้นตอนที่ 2: เปลี่ยนสถาปัตยกรรมรีเซ็ตเป็น Synchronous Reset
แก้ไข Sensitivity List ใน RTL ให้มีเฉพาะ `posedge clk`:
```systemverilog
// กฎเหล็กสำหรับการเขียน Pipeline ใน DSP
always_ff @(posedge clk) begin
    if (rst_sync) begin
        // รีเซ็ตแบบซิงโครนัสเท่านั้น
    end else begin
        // ดำเนินการตามปกติ
    end
end
```

#### ขั้นตอนที่ 3: เปิดดู Schematic และยืนยันว่าไม่มีขาข้าม Slice
ใน Vivado ให้คลิกขวาที่เซลล์ DSP48E2 แล้วเลือก `Schematic` เพื่อยืนยันว่าสัญญาณขาเข้าและขาออกเชื่อมต่อกับ Hard Macro Pins (`A`, `B`, `M`, `P`) โดยไม่มี D-Flip-Flop ภายนอกมาขวาง

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| パイプライン吸収 | ぱいぷらいんきゅうしゅう | Paipurain Kyuushuu | Pipeline Absorption (การดูดซับรีจิสเตอร์เข้า DSP) |
| 乗算器レジスタ | じょうざんきれじすた | Jouzanki Rejisuta | Multiplier Register (`MREG`) |
| 出力レジスタ | しゅつりょくれじすた | Shutsuryoku Rejisuta | Output Register (`PREG`) |
| 非同期リセット不整合 | ひどうきりせっとふせいごう | Hidouki Risetto Fuseigou | Asynchronous Reset Incompatibility |
| 配線遅延増大 | はいせんちえんぞうだい | Haisen Chien Zoudai | Excessive Routing Delay |
| グリッチ抑制 | ぐりっちよくせい | Guritchi Yokusei | Glitch Suppression |
| 同期リセット化 | どうきりせっとか | Douki Risettoka | Synchronous Reset Conversion |
| タイミング収束限界 | たいみんぐしゅうそくげんかい | Taimingu Shuusoku Genkai | Timing Closure Margin |
| 動作周波数最大化 | どうさしゅうはすうさいだいか | Dousa Shuuhasuu Saidaika | Maximize Operating Frequency ($F_{max}$) |
| カスケード配線 | かすけーどはいせん | Kasukeedo Haisen | Dedicated Cascade Interconnect |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** ศูนย์พัฒนาอุปกรณ์โทรคมนาคมไร้สาย 5G/6G (5G Baseband Hardware Review Meeting)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** โคบายาชิ ซัง (Kobayashi-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** ชิบาตะ คุง (Shibata-kun)

---

**小林技師 (Kobayashi):**  
「柴田君、この 5G ビームフォーミング積和演算モジュールのタイミングレポートを見たが、491.52MHz の目標に対して WNS が $-0.920\text{ ns}$ もショートしている。Device View で物理配置を確認すると、DSP48E2 の内部レジスタ（MREG や PREG）が全く使われず、周囲のスライスファブリックにフリップフロップが吐き出されているが、これはどういうことかね？」  
*(Shibata-kun, kono 5G biimufoomingu sekiwa enzan mojyuuru no taimingu repooto wo mita ga, 491.52MHz no mokuhyou ni taishite WNS ga $-0.920\text{ ns}$ mo shooto shite iru. Device View de butsuri haichi wo kakunin suru to, DSP48E2 no naibu rejisuta (MREG ya PREG) ga mattaku tsukawarezu, shuui no suraisu faburikku ni furippufuroppu ga hakidasarete iru ga, kore wa dou iu koto kane?)*  
**ความหมาย:** คุณชิบาตะ ผมดูรายงาน Timing ของโมดูลคูณสะสม 5G Beamforming ตัวนี้แล้ว พบว่าที่เป้าหมาย 491.52MHz ค่า WNS ขาดทุนไปถึง $-0.920\text{ ns}$ พอไปดูใน Device View กลับพบว่ารีจิสเตอร์ภายใน DSP48E2 (ทั้ง MREG และ PREG) ไม่ถูกใช้งานเลยแม้แต่ตัวเดียว และ Flip-Flop ถูกเตะออกไปอยู่นอก Slice โดยรอบ มันเกิดอะไรขึ้นครับ?

---

**柴田技師 (Shibata):**  
「はい、小林さん。RTL の記述では、乗算段と加算段の間にそれぞれ 1 段ずつ確実に D-FF を挿入してパイプライン化しております。社内の RTL コーディング標準規約に従い、すべてのレジスタに非同期リセット（`always_ff @(posedge clk or negedge rst_n)`）を適用しました。論理的には 3 段のパイプラインになっているはずです。」  
*(Hai, Kobayashi-san. RTL no kijutsu de wa, jouzandan to kasandan no aida ni sorezore ichidan zutsu kakujitsu ni D-FF wo sounyuu shite paipurain-ka shite orimasu. Shanai no RTL koodingu hyoujun kiyaku ni shitagai, subete no rejisuta ni hidouki risetto (`always_ff @(posedge clk or negedge rst_n)`) wo tekiyou shimashita. Ronriteki ni wa sandan no paipurain ni natte iru hazu desu.)*  
**ความหมาย:** ครับคุณโคบายาชิ ในโค้ด RTL ผมได้แทรก D-FF คั่นระหว่างสเตจคูณและสเตจสะสมไว้ครบถ้วนสเตจละ 1 ตัวแล้วครับ และปฏิบัติตามกฎมาตรฐานการเขียนโค้ดของบริษัท โดยใส่ Asynchronous Reset ให้กับทุกรีจิสเตอร์ ทางตรรกะแล้วมันมี Pipeline ครบ 3 สเตจแน่นอนครับ

---

**小林技師 (Kobayashi):**  
「形式的な規約遵守が物理的な破滅を招いている典型例だ！DSP48E2 のハードマクロには非同期リセットピンなど存在しない！君が `negedge rst_n` を書いた瞬間に、合成ツールは『ハードマクロ内にレジスタを吸収（Absorb）できない』と判断して、スライスファブリックへ追い出してしまうんだ！その結果、DSP とスライスの間を長い配線で行き来することになり、配線遅延だけで 2ns 以上浪費している。**即座に重大指摘事項とする！** DSP 周りのレジスタから非同期リセットを全廃して完全同期リセット（Synchronous Reset）へ書き直し、MREG と PREG を 100% 吸収させて 491.52MHz のタイミングを完全に収束させなさい！」  
*(Keishikiteki na kiyaku junshu ga butsuriteki na hametsu wo maneite iru tenkeirei da! DSP48E2 no haado makuro ni wa hidouki risetto pin nado sonzai shinai! Kimi ga `negedge rst_n` wo kaita shunkan ni, gousei tsuuru wa "haado makuro nai ni rejisuta wo kyuushuu (Absorb) dekinai" to handan shite, suraisu faburikku e oidashite shimaunda! Sono kekka, DSP to suraisu no aida wo nagai haisen de ikiki suru koto ni nari, haisen chien dake de 2ns ijou rouhi shite iru. **Sokuza ni juudai shiteki jikou to suru!** DSP mawari no rejisuta kara hidouki risetto wo zenpai shite kanzen douki risetto (Synchronous Reset) e kakinaoshi, MREG to PREG wo 100% kyuushuu sasete 491.52MHz no taimingu wo kanzen ni shuusoku sasenasai!)*  
**ความหมาย:** การทำตามกฎแบบท่องจำกำลังนำไปสู่หายนะทางกายภาพนะ! ใน Hard Macro ของ DSP48E2 มันไม่มีขา Asynchronous Reset อยู่จริง! วินาทีที่เธอเขียน `negedge rst_n` เครื่องมือสังเคราะห์จะตัดสินใจทันทีว่า 'ไม่สามารถดูดซับรีจิสเตอร์เข้าสู่ Hard Macro ได้' แล้วเตะมันออกไปอยู่นอก Slice! ทำให้สัญญาณต้องวิ่งไปมาระหว่าง DSP และ Slice ผ่านสายไฟยาวๆ เสียเวลาไปเปล่าๆ กว่า 2ns! **ผมสั่งเป็นข้อแก้ไขวิกฤตทันที!** จงตัด Asynchronous Reset รอบตัว DSP ทิ้งให้หมดแล้วเปลี่ยนเป็น Synchronous Reset เพื่อให้ MREG และ PREG ถูกดูดซับเข้าไปในชิป 100% และปิด Timing ที่ 491.52MHz ให้ผ่านเดี๋ยวนี้!

---

**柴田技師 (Shibata):**  
「ハードマクロの物理的制約と非同期リセットの背反関係を全く理解できておりませんでした…！直ちに完全同期リセットへ修正し、Vivado のログで MREG と PREG が完全に吸収（Absorbed）されたことを確認して再提出いたします！」  
*(Haado makuro no butsuriteki seiyaku to hidouki risetto no haihan kankei wo mattaku rikai dekite orimasen deshita...! Tadachini kanzen douki risetto e shuusei shi, Vivado no rogu de MREG to PREG ga kanzen ni kyuushuu (Absorbed) sareta koto wo kakunin shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ผมไม่เคยเข้าใจความขัดแย้งระหว่างข้อจำกัดทางกายภาพของ Hard Macro กับ Asynchronous Reset มาก่อนเลยครับ...! ผมจะรีบแก้เป็น Synchronous Reset ทันที และตรวจสอบใน Log ของ Vivado ให้ขึ้นสถานะ Absorbed ทั้งหมดแล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณเปรียบเทียบความถี่ $F_{max}$ เมื่อเปิดใช้งาน MREG และ PREG

ในบล็อก DSP48E2 บนชิป UltraScale+ (Speed Grade -2) กำหนดพารามิเตอร์ความหน่วงเวลาภายในเซลล์ฮาร์ดแวร์ดังนี้:
* ความหน่วงเวลาของตัวคูณภายใน (Multiplier Internal Delay): $t_{mult} = 1.450\text{ ns}$
* ความหน่วงเวลาของ 48-bit ALU ภายใน: $t_{alu} = 1.150\text{ ns}$
* ความหน่วง Flip-Flop Clock-to-Q ของรีจิสเตอร์ภายใน ($t_{co}$): $t_{co\_dsp} = 0.220\text{ ns}$
* Flip-Flop Setup time ของรีจิสเตอร์ภายใน ($t_{su}$): $t_{su\_dsp} = 0.080\text{ ns}$
* ค่าความไม่แน่นอนของสัญญาณนาฬิกา (Clock Uncertainty): $T_{unc} = 0.100\text{ ns}$

หากเปรียบเทียบสองกรณี:
* **กรณีที่ 1 (เปิดเฉพาะ PREG):** ข้อมูลวิ่งผ่านตัวคูณและ ALU ต่อเนื่องกันโดยไม่มี MREG กั้นกลาง
* **กรณีที่ 2 (เปิดทั้ง MREG และ PREG):** มี MREG คั่นกลางระหว่างตัวคูณและ ALU

จงคำนวณหาความถี่สัญญาณนาฬิกาสูงสุด ($F_{max}$) ของ **กรณีที่ 1** เทียบกับ **กรณีที่ 2**?

---

#### ตัวเลือก:
A) กรณีที่ 1: $333.33\text{ MHz}$, กรณีที่ 2: $540.54\text{ MHz}$  
B) กรณีที่ 1: $333.33\text{ MHz}$, กรณีที่ 2: $606.06\text{ MHz}$  
C) กรณีที่ 1: $384.62\text{ MHz}$, กรณีที่ 2: $689.65\text{ MHz}$  
D) กรณีที่ 1: $277.78\text{ MHz}$, กรณีที่ 2: $485.44\text{ MHz}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) กรณีที่ 1: $333.33\text{ MHz}$, กรณีที่ 2: $540.54\text{ MHz}$**

##### ขั้นตอนที่ 1: คำนวณเส้นทางวิกฤตของกรณีที่ 1 (PREG เท่านั้น)
สัญญาณเริ่มต้นจากอินพุต (สมมติผ่าน AREG/BREG) วิ่งทะลุผ่านตัวคูณและทะลุผ่าน ALU เข้าสู่ PREG:
$$T_{path1} = t_{co\_dsp} + t_{mult} + t_{alu} + t_{su\_dsp}$$
แทนค่า:
$$T_{path1} = 0.220\text{ ns} + 1.450\text{ ns} + 1.150\text{ ns} + 0.080\text{ ns} = 2.900\text{ ns}$$

รวม Clock Uncertainty:
$$T_{clk\_min1} = T_{path1} + T_{unc} = 2.900\text{ ns} + 0.100\text{ ns} = 3.000\text{ ns}$$
คำนวณ $F_{max}$:
$$F_{max1} = \frac{1}{3.000 \times 10^{-9}\text{ s}} \approx 333.33\text{ MHz}$$

##### ขั้นตอนที่ 2: คำนวณเส้นทางวิกฤตของกรณีที่ 2 (เปิดทั้ง MREG และ PREG)
เส้นทางจะถูกแบ่งออกเป็น 2 ช่วงอิสระ:
1. ช่วงที่ 1 (จาก AREG/BREG ผ่านตัวคูณ เข้าสู่ MREG):
   $$T_{seg1} = t_{co\_dsp} + t_{mult} + t_{su\_dsp} = 0.220 + 1.450 + 0.080 = 1.750\text{ ns}$$
2. ช่วงที่ 2 (จาก MREG ผ่าน ALU เข้าสู่ PREG):
   $$T_{seg2} = t_{co\_dsp} + t_{alu} + t_{su\_dsp} = 0.220 + 1.150 + 0.080 = 1.450\text{ ns}$$

เส้นทางที่ยาวที่สุดคือช่วงที่ 1 ($1.750\text{ ns}$):
$$T_{clk\_min2} = T_{seg1} + T_{unc} = 1.750\text{ ns} + 0.100\text{ ns} = 1.850\text{ ns}$$
คำนวณ $F_{max}$:
$$F_{max2} = \frac{1}{1.850 \times 10^{-9}\text{ s}} \approx 540.54\text{ MHz}$$

การเปิดใช้งาน `MREG` ช่วยดันความถี่ $F_{max}$ ขึ้นจาก $333\text{ MHz}$ สู่ **$540.5\text{ MHz}$ (เพิ่มขึ้นถึง $62.2\%$)** ทันทีโดยไม่ต้องเพิ่มลอจิกภายนอกแม้แต่ตัวเดียว!

---

### คำถามที่ 2: การจัดสมดุลความล่าช้า (Latency Balancing) สำหรับเส้นทาง Bypass

ในระบบประมวลผลฟิลเตอร์ที่มีเส้นทางคู่ขนาน:
* **เส้นทางหลัก (DSP Path):** เปิดใช้งานไปป์ไลน์เต็มรูปแบบ (`AREG=1, MREG=1, PREG=1`) รวม Latency เท่ากับ $3$ รอบสัญญาณนาฬิกา
* **เส้นทางรอง (Bypass Tag Path):** สัญญาณควบคุม `valid_tag` วิ่งคู่ขนานไปกับข้อมูลเพื่อระบุชนิดของแพ็กเก็ต

เพื่อป้องกันไม่ให้ข้อมูลและ Tag หลุดเฟสกัน (Latency Skew Mismatch) วิศวกรต้องจัดการสัญญาณ `valid_tag` ในเส้นทางรองอย่างไร?

---

#### ตัวเลือก:
A) ส่งสัญญาณตรงโดยไม่ต้องหน่วงเวลา  
B) แทรก Shift Register LUT (SRL16E) หรือ Flip-Flop จำนวน 3 สเตจในเส้นทางรอง เพื่อให้ Latency ชดเชยตรงกัน $3$ รอบสัญญาณนาฬิกาพอดี  
C) ลด Latency ของ DSP ลงเหลือ 0 รอบ  
D) เพิ่มความถี่ของสัญญาณนาฬิกาเป็น 3 เท่า

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) แทรก Shift Register LUT (SRL16E) หรือ Flip-Flop จำนวน 3 สเตจในเส้นทางรอง เพื่อให้ Latency ชดเชยตรงกัน $3$ รอบสัญญาณนาฬิกาพอดี**

##### เหตุผลทางวิศวกรรม:
เมื่อเราเพิ่มความลึกของ Pipeline ใน DSP Path เพื่อเร่งความเร็ว ($F_{max}$) สัญญาณข้อมูลจะเดินทางมาถึงช้าลง 3 คาบเวลา หากเส้นทางควบคุมหรือ Tag ไม่ถูกหน่วงเวลาให้เท่ากัน สัญญาณควบคุมจะวิ่งไปถึงปลายทางก่อนข้อมูลจริง 3 ไซเคิล ทำให้ปลายทางประมวลผลข้อมูลผิดแพ็กเก็ต!

ใน FPGA สถาปัตยกรรม Xilinx การใช้ **SRL16E** (Shift Register ที่สร้างจาก 1 LUT) สามารถสร้างความหน่วงได้ตั้งแต่ 1 ถึง 16 ไซเคิลโดยใช้พื้นที่เพียง 1 LUT และใช้พลังงานต่ำมาก จึงเป็นวิธีมาตรฐานสากลในการทำ Latency Balancing คู่ขนานกับ DSP Slices

---

### คำถามที่ 3: ปรากฏการณ์ Glitch Power Reduction เมื่อเปิดใช้งาน MREG

เหตุใดการเปิดใช้งาน `MREG` ภายในตัวคูณของ DSP48E2 จึงสามารถช่วยลดการสูญเสียกำลังไฟฟ้าไดนามิก ($P_{dyn}$) ของทั้งชิปได้อย่างมีนัยสำคัญ?

---

#### ตัวเลือก:
A) เพราะทำให้แรงดันไฟฟ้าของตัวคูณลดลง  
B) เพราะตัวคูณแบบ Carry-Save Array จะสร้างการสลับบิตชั่วขณะ (Combinational Hazards/Glitches) นับร้อยครั้งในแต่ละรอบ การใส่ MREG จะกักและกรองสัญญาณรบกวนเหล่านี้ไว้ไม่ให้แพร่กระจายต่อไปยัง 48-bit ALU และสายไฟเอาต์พุต  
C) เพราะ MREG ปิดการทำงานของสัญญาณนาฬิกาโดยอัตโนมัติ  
D) เพราะ MREG เปลี่ยนลอจิกให้เป็น Floating Point

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) เพราะตัวคูณแบบ Carry-Save Array จะสร้างการสลับบิตชั่วขณะ (Combinational Hazards/Glitches) นับร้อยครั้งในแต่ละรอบ การใส่ MREG จะกักและกรองสัญญาณรบกวนเหล่านี้ไว้ไม่ให้แพร่กระจายต่อไปยัง 48-bit ALU และสายไฟเอาต์พุต**

##### คำอธิบายเชิงฟิสิกส์ซิลิคอน:
ในวงจรตัวคูณดิจิทัล $27 \times 18$ บิต จะประกอบด้วยเกต Full Adder ต่อไขว้กันหลายร้อยตัว สัญญาณ Partial Products จะเดินทางมาถึง Adder แต่ละชั้นด้วยเวลาที่เหลื่อมกัน ทำให้เกิด Glitch สวิงขึ้นลงนับครั้งไม่ถ้วน (Spurious Transitions) ก่อนที่ผลคูณสุดท้ายจะนิ่ง

หากไม่มี `MREG` สัญญาณ Glitch เหล่านี้ทั้งหมดจะทะลักเข้าสู่ 48-bit ALU และขับประจุสายไฟขนาดใหญ่ ทำให้ตัวเก็บประจุของเกตใน ALU ถูกชาร์จและดิสชาร์จอย่างไร้ประโยชน์ ส่งผลให้สูญเสียพลังงาน $P = C V^2 f$ มหาศาล
การเปิด `MREG` จะทำหน้าที่เป็น **"เขื่อนกัก Glitch"** ให้จบลงแค่ในตัวคูณ ทำให้ ALU สลับสถานะเฉพาะเมื่อข้อมูลนิ่งแล้วเท่านั้น ช่วยประหยัดพลังงานได้ถึง $30 - 45\%$!
