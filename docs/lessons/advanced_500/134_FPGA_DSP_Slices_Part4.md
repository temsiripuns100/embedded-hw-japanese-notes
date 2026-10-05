# Lesson 134: FPGA DSP Slices - Part 4 (Dedicated Cascade Paths & Wide Adders - PCOUT/PCIN, 96-bit Accumulator)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ทางด่วนสายโลหะเฉพาะกิจภายในคอลัมน์ DSP (Dedicated Cascade Interconnect Architecture)
ภายในสถาปัตยกรรม FPGA ระดับสูง (AMD Xilinx UltraScale/UltraScale+ และ Versal AI Core) บล็อก DSP48E2 ไม่ได้อยู่อย่างโดดเดี่ยว แต่จะถูกจัดวางเรียงต่อกันเป็นแนวดิ่งเรียกว่า **DSP Column** ซึ่งมีสายสัญญาณเชื่อมต่อระหว่างเซลล์ที่อยู่ติดกันโดยตรงในระดับฮาร์ดแวร์ซิลิคอน (Dedicated Hardwired Cascading Paths) โดยไม่ต้องผ่านสายสัญญาณ Programmable Routing Fabric:

```
              โครงสร้างสาย Cascade ทางด่วนระหว่าง DSP48E2 สองตัว
   
   +---------------------------------------------------------------+
   | DSP48E2 Slice [k] (ตัวล่าง)                                    |
   |                                                               |
   |   Inputs A, B -----> [ Multiplier ]                           |
   |                             |                                 |
   |                             v                                 |
   |   PCIN -------------> [ 48-bit ALU ]                          |
   |                             |                                 |
   |   +-------------------------+-----------------------------+   |
   |   | PCOUT (48-bit)        CARRYCASCOUT (1-bit)            |   |
   +---+-------------------------------------------------------+---+
       |                                                       |
       | Dedicated Silicon Interconnect (< 80 ps, Zero LUT)    |
       v                                                       v
   +---+-------------------------------------------------------+---+
   |   | PCIN (48-bit)         CARRYCASCIN (1-bit)             |   |
   |   +-------------------------+-----------------------------+   |
   |                             |                                 |
   |   Inputs A, B -----> [ Multiplier ]                           |
   |                             |                                 |
   |                             v                                 |
   |                      [ 48-bit ALU ]                           |
   |                             |                                 |
   |                      [ PCOUT / P ]                            |
   |                                                               |
   | DSP48E2 Slice [k+1] (ตัวบน)                                   |
   +---------------------------------------------------------------+
```

#### 1.1.1 องค์ประกอบของ Cascade Buses ภายใน DSP48E2
1. **`PCOUT` $\rightarrow$ `PCIN` (48-bit Dedicated Cascade):**
   * ส่งผ่านผลลัพธ์ขนาด 48 บิตจากเอาต์พุตของสไลซ์ตัวล่าง เข้าสู่อินพุตของ ALU สไลซ์ตัวบนโดยตรงด้วยความหน่วงเวลาระดับ sub-100 picoseconds
2. **`ACOUT` $\rightarrow$ `ACIN` (30-bit) และ `BCOUT` $\rightarrow$ `BCIN` (18-bit):**
   * ส่งผ่านข้อมูลขาเข้า $A$ และ $B$ ต่อเนื่องกันในลักษณะ Shift Register Chain โดยไม่ต้องใช้สายสัญญาณ Fabric
3. **`CARRYCASCOUT` $\rightarrow$ `CARRYCASCIN` (1-bit Dedicated Carry):**
   * **หัวใจสำคัญของการสร้าง Wide Accumulators!** ทำหน้าที่ส่งสัญญาณตัวทด (Carry-Out) จากบิตที่ 47 ของตัวล่าง เข้าสู่ตัวทด (Carry-In) ของตัวบนอย่างไร้รอยต่อ

---

### 1.2 การออกแบบวงจรบวกสะสมความแม่นยำสูง 96 บิต (96-bit Ultra-Wide Accumulator)
ในงานฟิสิกส์พลังงานสูง (Particle Accelerators), มาตรวิทยา (Metrology), และระบบนำทางเฉื่อย (Inertial Navigation Systems) ตัวสะสม 48 บิตอาจเกิดการล้นค่า (Overflow) ได้อย่างรวดเร็ว วิศวกรจำเป็นต้องขยายขนาดตัวสะสมเป็น **$96$ บิต**

การนำ DSP48E2 สองตัวมาต่ออนุกรมกัน (Cascading):
* **DSP Slice ตัวล่าง (Lower 48 bits):**
  - ประมวลผลบิต $[47:0]$
  - สร้างตัวทดผ่านขา `CARRYCASCOUT`
* **DSP Slice ตัวบน (Upper 48 bits):**
  - ประมวลผลบิต $[95:48]$
  - รับตัวทดผ่านขา `CARRYCASCIN` โดยกำหนดโหมด $Z = P$ และ $X = 0, Y = 0$ บวกกับตัวทด

สมการบูลีนของการคำนวณ 96 บิต:

$$P_{total}[95:0] = \{P_{high}[47:0], P_{low}[47:0]\} + M[44:0]$$

$$\text{Carry}_{out, low} = (P_{low}[47:0] + M[44:0] \ge 2^{48})$$

$$P_{high}(t+1) = P_{high}(t) + \text{Carry}_{out, low}$$

```
                การแบ่งหน้าที่ระหว่าง DSP สองตัวสำหรับ 96-bit Accumulator
   
   Data In [44:0] ------------> [ DSP Lower (48-bit) ] ---> P_low [47:0]
                                         |
                                  CARRYCASCOUT
                                         | (Hard Dedicated Wire)
                                         v
                                  CARRYCASCIN
                                         |
   Zero / Sign Ext ------------> [ DSP Upper (48-bit) ] ---> P_high [47:0] (bits [95:48])
```

---

### 1.3 ขีดจำกัดทางกายภาพ: รอยต่อคอลัมน์และขอบเขต SLR (Column Boundaries & SLR Crossings)
แม้ว่าสาย Cascade จะมีความเร็วสูงมาก แต่มันมี **ข้อจำกัดทางกายภาพที่ละเมิดไม่ได้ (Physical Invariants)**:

1. **ขอบเขตคอลัมน์ DSP (DSP Column Boundary):**
   * ใน 1 คอลัมน์ของ FPGA ทั่วไปจะมี DSP Slice ต่อเนื่องกันประมาณ $24$ ถึง $48$ ตัวในแนวดิ่ง
   * หากฟิลเตอร์หรือสาย Cascade มีขนาดยาวเกินกว่าจำนวน DSP ในคอลัมน์นั้น สาย `PCOUT` **จะไม่สามารถเลี้ยวข้ามไปยังคอลัมน์ถัดไปได้ด้วยตัวเอง**!
   * เครื่องมือคอมไพเลอร์จะต้องตัดสาย Cascade ทิ้ง และดึงสัญญาณออกสู่ Fabric Routing ซึ่งจะทำให้เกิดความหน่วงกระโดดเพิ่มขึ้นทันที $1.2 - 2.0\text{ ns}$
2. **ขอบเขต Super Logic Region (SLR Boundary):**
   * ใน FPGA ขนาดใหญ่แบบ Multi-Die (SSI Technology เช่น Virtex UltraScale+) สาย Cascade ของ DSP **ถูกตัดขาดที่รอยต่อระหว่าง SLR** อย่างเด็ดขาด!
   * หากสาย Cascade ถูกวางคร่อมเส้นแบ่ง SLR การคอมไพล์จะล้มเหลว (Place Error) ทันที เว้นแต่จะสั่งหักเลี้ยวผ่าน Super Long Line (SLL)

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: 96-bit Accumulator ใช้ Cascade สมบูรณ์แบบ 100%

```systemverilog
//=============================================================================
// Module: dsp48e2_96bit_accumulator.sv
// Description: Ultra-High-Speed 96-bit Accumulator using 2 Cascaded DSP48E2 Slices
// Compliance: Target 750MHz Timing Sign-off on AMD UltraScale+
//=============================================================================
`timescale 1ns / 1ps

module dsp48e2_96bit_accumulator (
    input  logic              clk,
    input  logic              rst_sync,
    input  logic              accum_en,
    input  logic              clr_accum,
    // อินพุตข้อมูลบวกขนาด 45 บิต
    input  logic signed [44:0] data_in,
    // เอาต์พุตผลลัพธ์การสะสมความแม่นยำสูง 96 บิต
    output logic [95:0]       accum_out_96
);

    // สายสัญญาณ Cascade ระหว่าง DSP ตัวล่างและตัวบน
    logic [47:0] p_low_cascade;
    logic        carry_cascade;

    // Output Registers ของแต่ละสเตจ
    logic [47:0] p_low_reg;
    logic [47:0] p_high_reg;

    //-------------------------------------------------------------------------
    // DSP Slice 1 (Lower 48 bits: Bits [47:0])
    // จัดการข้อมูลขาเข้าและสร้าง Carry-Out เข้า CARRYCASCOUT
    //-------------------------------------------------------------------------
    logic [47:0] next_p_low;
    logic        next_carry;

    always_comb begin
        if (clr_accum) begin
            {next_carry, next_p_low} = {1'b0, 3'b000, data_in};
        end else if (accum_en) begin
            {next_carry, next_p_low} = p_low_reg + {3'b000, data_in};
        end else begin
            {next_carry, next_p_low} = {1'b0, p_low_reg};
        end
    end

    // บังคับ Synchronous Reset และดูดซับเข้า PREG
    (* use_dsp = "yes" *)
    always_ff @(posedge clk) begin
        if (rst_sync) begin
            p_low_reg     <= '0;
            carry_cascade <= 1'b0;
        end else begin
            p_low_reg     <= next_p_low;
            carry_cascade <= next_carry; // จะถูกแมปเป็น CARRYCASCOUT
        end
    end

    //-------------------------------------------------------------------------
    // DSP Slice 2 (Upper 48 bits: Bits [95:48])
    // รับตัวทดจาก CARRYCASCIN และบวกสะสมในระดับบน
    //-------------------------------------------------------------------------
    logic [47:0] next_p_high;

    always_comb begin
        if (clr_accum) begin
            next_p_high = '0;
        end else if (accum_en) begin
            next_p_high = p_high_reg + carry_cascade; // บวกเฉพาะ Carry
        end else begin
            next_p_high = p_high_reg;
        end
    end

    (* use_dsp = "yes" *)
    always_ff @(posedge clk) begin
        if (rst_sync) begin
            p_high_reg <= '0;
        end else begin
            p_high_reg <= next_p_high;
        end
    end

    assign accum_out_96 = {p_high_reg, p_low_reg};

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ในระบบตรวจวัดตำแหน่งลำอนุภาคในเครื่องเร่งอนุภาคพลังงานสูง (Synchrotron Beam Position Monitor) มีการคำนวณอินทิกรัลเชิงตัวเลขด้วยตัวสะสม 96 บิต บนชิป Virtex UltraScale+ ชนิด Multi-Die (VU9P ที่มี 3 Super Logic Regions: SLR0, SLR1, SLR2) ทำงานที่ความถี่สัญญาณนาฬิกา $450\text{ MHz}$ ($T_{clk} = 2.222\text{ ns}$) วิศวกรเขียนโค้ด RTL โดยไม่ได้กำหนดตำแหน่งฮาร์ดแวร์

**ผลลัพธ์ที่ล้มเหลว:** เครื่องมือ Vivado Place & Route นำ DSP Slice ตัวล่างไปวางไว้ที่ขอบบนของ **SLR0** และนำ DSP Slice ตัวบนไปวางไว้ที่ขอบล่างของ **SLR1** ข้ามรอยต่อระหว่างชิป ส่งผลให้สายสัญญาณตัวทด (Carry) ไม่สามารถใช้ `CARRYCASCOUT` ได้ และถูกบังคับให้วิ่งผ่านสาย Inter-SLR SLL ข้าม Die เกิดความหน่วงเวลาเดินสายพุ่งสูงถึง $1.850\text{ ns}$ รายงาน STA ฟ้องความเสี่ยงขั้นวิกฤต: $WNS = -1.150\text{ ns}$ และในการทำงานจริงเกิดอาการตัวทดหลุด (Carry Dropped) ข้อมูลวิถีลำอนุภาคเพี้ยน ส่งผลให้ระบบยิงสัญญาณฉุกเฉินดับลำแสง (Beam Dump Interruption)!

```
                    หายนะจากการวาง Cascaded DSP ข้ามขอบเขต SLR
   
   [ สภาพในซิลิคอนจริง: สาย Cascade ถูกตัดขาดข้าม Die ]
   +-------------------------------------------------------------+
   | SLR1 (Die ตัวบน)                                            |
   |   [ DSP Slice ตัวบน (Upper 48-bit) ]                        |
   +------------------------------^------------------------------+
                                  |
              สายไฟข้าม Die (Inter-SLR SLL Delay = 1.85 ns!)
              (สายทางด่วน Hard Cascade ข้าม Die ไม่ได้!)
                                  |
   +------------------------------+------------------------------+
   | SLR0 (Die ตัวล่าง)                                          |
   |   [ DSP Slice ตัวล่าง (Lower 48-bit) ]                      |
   +-------------------------------------------------------------+
   
   ผลลัพธ์: สัญญาณตัวทดข้าม Die ไม่ทันขอบนาฬิกา -> เกิด Carry Drop ทันที!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมเครื่องเร่งอนุภาคถึงตัดการทำงานของลำแสง (Beam Dump)?**
   * *ตอบ:* ค่าพิกัดลำอนุภาคที่คำนวณได้กระโดดผิดปกติเกินเกณฑ์ความปลอดภัย
2. **ทำไมค่าพิกัดถึงกระโดดผิดปกติ?**
   * *ตอบ:* ตัวสะสม 96 บิตบน FPGA คำนวณบิตบน $[95:48]$ ผิดพลาดเนื่องจากทำตัวทดตกหล่น (Carry Dropped)
3. **ทำไมตัวทดถึงตกหล่น?**
   * *ตอบ:* เส้นทางสัญญาณตัวทดระหว่าง DSP ตัวล่างและตัวบนเกิด Setup Time Violation อย่างรุนแรงที่ $450\text{ MHz}$
4. **ทำไมเส้นทางสัญญาณตัวทดถึงเกิด Setup Violation รุนแรง?**
   * *ตอบ:* สัญญาณตัวทดไม่ได้เดินทางผ่านสายทางด่วน Hard Cascade แต่ถูกลากข้ามผ่านรอยต่อระหว่าง Die (SLR0 ไปยัง SLR1)
5. **ทำไมเครื่องมือถึงนำ DSP สองตัวไปวางข้าม SLR กัน?**
   * *ตอบ:* ผู้ออกแบบไม่ได้กำหนดข้อจำกัดพื้นที่ (Placement Constraints / Pblock) และไม่ได้ล็อกให้ DSP ทั้งสองตัวอยู่ใน **คอลัมน์และ SLR เดียวกัน** อย่างเคร่งครัด!

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของ 96-bit Accumulator
   
   การกำหนดข้อจำกัดพื้นที่ (Physical Constraints)   ความเข้าใจโครงสร้างชิป (Multi-Die Physics)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ไม่ได้ใส่      ปล่อยให้ Tool                  ไม่รู้ว่าสาย   ชิปเป็นแบบ
   Pblock ล็อก   กระจาย DSP                     Cascade ข้าม   Multi-SLR
   ในคอลัมน์เดียว ข้าม Die ได้                  SLR ไม่ได้     (3 Die บนบอร์ด)
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> สัญญาณตัวทดตกหล่น
                                                                |     ระบบเร่งอนุภาคดับ
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   สาย Inter-SLR ความจุสาย                     ไม่ได้ตรวจดู   ขาดการใส่
   มีความหน่วงสูง ข้าม Die สูง                  Vivado Device  RLOC เพื่อบังคับ
   ถึง 1.85ns    ทำให้ Skew บวม                 View เชิงลึก   ให้อยู่ติดกัน
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   ฟิสิกส์การเดินสาย (Inter-Die Routing)           การตรวจสอบก่อนส่งมอบ (Design Sign-off)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ล็อกตำแหน่ง DSP ที่ Cascade ให้อยู่ในคอลัมน์เดียวกันด้วย Pblock
สร้างข้อกำหนดในไฟล์ XDC เพื่อบังคับให้เซลล์ DSP ทั้งคู่ถูกจัดวางใน SLR และคอลัมน์เดียวกัน:
```tcl
# ล็อกให้ DSP ทั้งสองตัวอยู่ใน SLR0 คอลัมน์เดียวกัน
create_pblock pblock_accum96
add_cells_to_pblock [get_pblocks pblock_accum96] [get_cells -hier *dsp*accum*]
resize_pblock [get_pblocks pblock_accum96] -add {DSP48E2_X0Y0:DSP48E2_X0Y1}
```

#### ขั้นตอนที่ 2: ตรวจสอบการเชื่อมต่อ `CARRYCASCOUT` ในเน็ตลิสต์
รันคำสั่ง Tcl เพื่อยืนยันว่าไม่มีสายสัญญาณตัวทดรั่วไหลออกสู่ Fabric:
```tcl
get_pins -of_objects [get_nets -hier *carry_cascade*]
```
เอาต์พุตต้องเชื่อมต่อระหว่างพิน `CARRYCASCOUT` และ `CARRYCASCIN` โดยตรง 100%

#### ขั้นตอนที่ 3: ตรวจสอบความต่อเนื่องของคอลัมน์ (Column Continuity Check)
ต้องมั่นใจว่าไม่มีการวางบล็อก Cascade ข้ามขอบล่างหรือขอบบนสุดของคอลัมน์ เพื่อป้องกันไม่ให้สาย Cascade ขาดตอน

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| カスケード専用配線 | かすけーどせんようはいせん | Kasukeedo Sen-you Haisen | Dedicated Cascade Routing (`PCIN/PCOUT`) |
| 桁上げ伝搬 | けたあげでんぱん | Keta-age Denpan | Carry Propagation (`CARRYCASCOUT`) |
| 多倍長加算器 | たばいちょうかさんき | Tabaichou Kasanki | Multi-Precision / Wide Adder (96-bit) |
| 列配置境界 | れつはいちきょうかい | Retsu Haichi Kyoukai | DSP Column Boundary |
| スライス分断 | すらいすぶんだん | Suraisu Bundan | Slice Splitting / Disconnection |
| ダイ間跨ぎ | だいかんまたぎ | Dai-kan Matagi | Inter-Die / SLR Boundary Crossing |
| 桁落ち障害 | けたおちしょうがい | Keta-ochi Shougai | Carry Dropping Defect |
| 配置制約ブロック | はいちせいやくぶろっく | Haichi Seiyaku Burokku | Placement Constraint Block (Pblock) |
| 相対配置制約 | そうたいはいちせいやく | Soutai Haichi Seiyaku | Relative Location Constraint (RLOC) |
| 演算桁あふれ | えんざんけたあふれ | Enzan Keta-afure | Arithmetic Overflow |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** สถาบันวิจัยฟิสิกส์นิวเคลียร์และเครื่องเร่งอนุภาค (Synchrotron Beam Control Design Review)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** มิมุระ ซัง (Mimura-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** ซากาโมโตะ คุง (Sakamoto-kun)

---

**三村技師 (Mimura):**  
「坂本君、このビーム位置計測用 96 ビット数値積分器の配置結果（Device View）を確認したが、下位 48 ビットの DSP が SLR0 に、上位 48 ビットの DSP が SLR1 に配置されているぞ！桁上げ信号（Carry）が SLR を跨ぐインターダイ配線（SLL）を通って 1.8ns も遅延しているが、なぜ専用の `CARRYCASCOUT` カスケード配線を使って同一列内に閉じ込めなかったのかね？」  
*(Sakamoto-kun, kono biimu ichi keisoku-you 96-bitto suuchi sekibinki no haichi kekka (Device View) wo kakunin shita ga, kai 48-bitto no DSP ga SLR0 ni, joui 48-bitto no DSP ga SLR1 ni haichi sarete iru zo! Keta-age shingou (Carry) ga SLR wo matagu intaa-dai haisen (SLL) wo tootte 1.8ns mo chien shite iru ga, naze sen-you no `CARRYCASCOUT` kasukeedo haisen wo tsukatte douitsu retsunai ni tojikomenakatta no kane?)*  
**ความหมาย:** คุณซากาโมโตะ ผมตรวจผลการจัดวาง (Device View) ของตัวรวมค่า 96 บิตสำหรับวัดตำแหน่งลำแสงตัวนี้แล้ว พบว่า DSP 48 บิตล่างถูกวางไว้ใน SLR0 แต่ DSP 48 บิตบนกลับลอยไปอยู่ใน SLR1! สัญญาณตัวทด (Carry) วิ่งข้าม Die ผ่านสาย SLL ช้าไปถึง 1.8ns ทำไมถึงไม่ใช้สายทางด่วน `CARRYCASCOUT` ล็อกให้อยู่ในคอลัมน์เดียวกันครับ?

---

**坂本技師 (Sakamoto):**  
「はい、三村さん。フロアプランの制約は特に記述せず、ツールの自動配置配線（Auto P&R）に任せておりました。論理記述上は 96 ビットの加算として書いてあるため、Vivado が最もタイミングの緩いスロットを適切に選んでくれたものと考えておりました。」  
*(Hai, Mimura-san. Furoapuran no seiyaku wa tokuni kijutsu sezu, tsuuru no jidou haichi haisen (Auto P&R) ni makasete orimashita. Ronri kijutsujou wa 96-bitto no kasan to shite kaite aru tame, Vivado ga mottomo taimingu no yurui surotto wo tekisetsu ni erande kureta mono to kangaete orimashita.)*  
**ความหมาย:** ครับคุณมิมุระ ผมไม่ได้เขียนข้อกำหนด Floorplan ไว้ ปล่อยให้ Tool ทำการจัดวางอัตโนมัติครับ ในเมื่อโค้ดระบุการบวก 96 บิตไว้ชัดเจน ผมจึงเข้าใจว่า Vivado คงจะเลือกสล็อตที่มีช่องว่างเหมาะสมให้เองครับ

---

**三村技師 (Mimura):**  
「ツール任せにするからこういう致命的なミスが起きるんだ！SLR を跨いだ時点で、DSP48E2 同士を垂直に直結する超高速カスケード配線（遅延 80 ピコ秒以下）は物理的に完全に切断される！その結果、通常のファブリック配線と SLL を経由することになり、450MHz のクロック周期（2.22ns）に対して桁上げが間に合わず、実機でビーム暴走を引き起こす『桁落ち障害』が確実に発生する！**重大是正事項とする！** 直ちに Pblock 制約を記述して両 DSP を同一 SLR かつ同一カスケード列内に物理固定し、専用キャリー配線を 100% 成立させなさい！」  
*(Tsuuru makase ni suru kara kou iu chimeiteki na misu ga okirunda! SLR wo mataida jiten de, DSP48E2 doushi wo suichoku ni chokketsu suru chou-kousoku kasukeedo haisen (chien 80 pikobyou ika) wa butsuriteki ni kanzen ni setsudan sareru! Sono kekka, tsuujou no faburikku haisen to SLL wo keiyu suru koto ni nari, 450MHz no kurokku shuuki (2.22ns) ni taishite keta-age ga maniawazu, jikki de biimu bousou wo hikiokosu "keta-ochi shougai" ga kakujitsu ni hassei suru! **Juudai zeisei jikou to suru!** Tadachini Pblock seiyaku wo kijutsu shite ryou DSP wo douitsu SLR katsu douitsu kasukeedo retsunai ni butsuri kotei shi, sen-you kyarii haisen wo 100% seiritsu sasenasai!)*  
**ความหมาย:** ปล่อยให้ Tool ตัดสินใจเองถึงได้เกิดความผิดพลาดขั้นวิกฤตแบบนี้ไงล่ะ! วินาทีที่มันข้าม SLR สายทางด่วนความเร็วสูงระดับ sub-80ps ที่เชื่อมตรงระหว่าง DSP จะถูกตัดขาดในทางกายภาพทันที! ผลลัพธ์คือมันต้องอ้อมไปวิ่งผ่านสาย Fabric และ SLL จนส่งตัวทดไม่ทันคาบเวลา 2.22ns ที่ความถี่ 450MHz เกิดอาการตัวทดตกหล่นจนลำอนุภาคสูญเสียการควบคุมอย่างแน่นอน! **ผมสั่งเป็นข้อแก้ไขเร่งด่วน!** จงรีบเขียน Pblock ล็อกให้ DSP ทั้งสองตัวอยู่ใน SLR เดียวกันและในคอลัมน์ Cascade เดียวกันทางกายภาพ เพื่อให้สาย Carry ทำงานได้ 100% เดี๋ยวนี้!

---

**坂本技師 (Sakamoto):**  
「マルチダイ FPGA におけるカスケード配線の物理的切断リスクを深く認識しておりませんでした…！直ちに Pblock 制約を追加して同一 DSP 列に固定し、桁上げ遅延が 100 ピコ秒以下で収まっていることを確認して再提出いたします！」  
*(Maruchi-dai FPGA ni okeru kasukeedo haisen no butsuriteki setsudan risuku wo fukaku ninshiki shite orimasen deshita...! Tadachini Pblock seiyaku wo tsuika shite douitsu DSP retsu ni kotei shi, keta-age chien ga 100 pikobyou ika de osamatte iru koto wo kakunin shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ผมไม่ได้ตระหนักถึงความเสี่ยงของการที่สาย Cascade ถูกตัดขาดข้าม Multi-Die เลยครับ...! ผมจะรีบใส่ Pblock ล็อกให้อยู่ในคอลัมน์เดียวกันทันที และยืนยันว่าเวลาเดินทางของตัวทดต่ำกว่า 100ps แล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณเปรียบเทียบความเร็วตัวทดระหว่าง Dedicated Carry Cascade vs Fabric Routing

ในการสร้างตัวสะสมขนาด 96 บิตด้วย DSP48E2 สองตัวทำงานที่ $V_{DD} = 0.85\text{ V}$ บน UltraScale+:
* Flip-Flop Clock-to-Q ของตัวทดใน DSP ตัวล่าง: $t_{co\_carry} = 0.200\text{ ns}$
* Setup Time ของขารับตัวทดใน DSP ตัวบน: $t_{su\_carry} = 0.080\text{ ns}$
* Clock Uncertainty: $T_{unc} = 0.100\text{ ns}$

หากเปรียบเทียบการเชื่อมต่อสัญญาณตัวทด 2 รูปแบบ:
* **รูปแบบที่ 1 (ใช้ Hard `CARRYCASCOUT` $\rightarrow$ `CARRYCASCIN` ในคอลัมน์เดียวกัน):**
  ความหน่วงเวลาของสายโลหะเฉพาะกิจ: $t_{wire\_hard} = 0.075\text{ ns}$
* **รูปแบบที่ 2 (หลุดออกสู่ Soft Fabric ข้าม SLR):**
  สัญญาณต้องผ่าน LUT แปลงสายและผ่านสาย Inter-SLR SLL: $t_{wire\_soft} = 1.850\text{ ns}$

จงคำนวณหาความถี่สัญญาณนาฬิกาสูงสุด ($F_{max}$) ของ **รูปแบบที่ 1** เทียบกับ **รูปแบบที่ 2**?

---

#### ตัวเลือก:
A) รูปแบบที่ 1: $2,197.8\text{ MHz}$, รูปแบบที่ 2: $448.4\text{ MHz}$  
B) รูปแบบที่ 1: $2,739.7\text{ MHz}$, รูปแบบที่ 2: $448.4\text{ MHz}$  
C) รูปแบบที่ 1: $741.0\text{ MHz}$ (ติด Silicon DSP Cap), รูปแบบที่ 2: $448.4\text{ MHz}$  
D) รูปแบบที่ 1: $1,500.0\text{ MHz}$, รูปแบบที่ 2: $550.0\text{ MHz}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: C) รูปแบบที่ 1: $741.0\text{ MHz}$ (ติด Silicon DSP Cap), รูปแบบที่ 2: $448.4\text{ MHz}$**

##### ขั้นตอนที่ 1: คำนวณคาบเวลาขั้นต่ำของรูปแบบที่ 2 (Soft Fabric ข้าม SLR)
เส้นทางความหน่วงของตัวทดผ่าน Fabric:
$$T_{path2} = t_{co\_carry} + t_{wire\_soft} + t_{su\_carry} = 0.200\text{ ns} + 1.850\text{ ns} + 0.080\text{ ns} = 2.130\text{ ns}$$
รวม Clock Uncertainty:
$$T_{clk\_min2} = T_{path2} + T_{unc} = 2.130\text{ ns} + 0.100\text{ ns} = 2.230\text{ ns}$$
คำนวณ $F_{max}$:
$$F_{max2} = \frac{1}{2.230 \times 10^{-9}\text{ s}} \approx 448.43\text{ MHz}$$
(ไม่สามารถทำงานที่ $450\text{ MHz}$ ได้ เกิด Setup Violation ทันที!)

##### ขั้นตอนที่ 2: คำนวณคาบเวลาขั้นต่ำของรูปแบบที่ 1 (Hard Carry Cascade)
เส้นทางความหน่วงของตัวทดผ่าน Hard Cascade:
$$T_{path1} = t_{co\_carry} + t_{wire\_hard} + t_{su\_carry} = 0.200\text{ ns} + 0.075\text{ ns} + 0.080\text{ ns} = 0.355\text{ ns}$$
รวม Clock Uncertainty:
$$T_{clk\_min1} = T_{path1} + T_{unc} = 0.355\text{ ns} + 0.100\text{ ns} = 0.455\text{ ns}$$
ความถี่ทางทฤษฎีเฉพาะเส้นทางตัวทด:
$$F_{path1} = \frac{1}{0.455 \times 10^{-9}\text{ s}} \approx 2,197.8\text{ MHz}$$

ทว่าในโลกความเป็นจริงของชิป FPGA UltraScale+ Speed Grade -2 ความถี่สูงสุดของบล็อก DSP48E2 ถูกจำกัดด้วยเพดานทางกายภาพของเซลล์ (Silicon Hard Ceiling Limit):
$$F_{max\_dsp\_cap} = 741.0\text{ MHz} \quad (T_{clk} \approx 1.350\text{ ns})$$
ดังนั้น วงจรจึงสามารถทำงานได้ที่ความเร็วเต็มเพดานของชิปคือ **$741.0\text{ MHz}$** โดยไม่มีปัญหาคอขวดจากเส้นทางตัวทดเลยแม้แต่น้อย!

---

### คำถามที่ 2: การสร้างตัวคูณขนาดกว้าง $35 \times 35$ บิตด้วยการแยกส่วนประกอบ Partial Products

ตัวคูณ DSP48E2 มีขนาดฮาร์ดแวร์จริงคือ $27 \times 18$ บิตแบบคิดเครื่องหมาย หากต้องการสร้างตัวคูณขนาด $35 \times 35$ บิตแบบไม่คิดเครื่องหมาย (Unsigned Multiplier) ด้วยวิธีแยกส่วนประกอบคลาสสิก (Partial Product Decomposition):
$$A = A_H \cdot 2^{17} + A_L, \quad B = B_H \cdot 2^{17} + B_L$$
โดยที่ $A_L, B_L$ มีขนาด 17 บิต และ $A_H, B_H$ มีขนาด 18 บิต

จะต้องใช้บล็อก DSP48E2 จำนวนอย่างน้อยที่สุดกี่ตัวในการคำนวณผลคูณ $35 \times 35$ บิตนี้?

---

#### ตัวเลือก:
A) 2 ตัว  
B) 3 ตัว  
C) 4 ตัว  
D) 6 ตัว

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: C) 4 ตัว**

##### การวิเคราะห์ทางพีชคณิต:
การกระจายผลคูณ $(A_H \cdot 2^{17} + A_L)(B_H \cdot 2^{17} + B_L)$:
$$A \times B = (A_L \times B_L) + (A_L \times B_H) \cdot 2^{17} + (A_H \times B_L) \cdot 2^{17} + (A_H \times B_H) \cdot 2^{34}$$

พิจารณาขนาดของแต่ละคู่การคูณ:
1. $A_L \times B_L$: ขนาด $17 \times 17$ บิต $\rightarrow$ ลงใน DSP ตัวที่ 1 ได้ ($27 \times 18$)
2. $A_L \times B_H$: ขนาด $17 \times 18$ บิต $\rightarrow$ ลงใน DSP ตัวที่ 2 ได้
3. $A_H \times B_L$: ขนาด $18 \times 17$ บิต $\rightarrow$ ลงใน DSP ตัวที่ 3 ได้
4. $A_H \times B_H$: ขนาด $18 \times 18$ บิต $\rightarrow$ ลงใน DSP ตัวที่ 4 ได้

ผลคูณย่อยทั้ง 4 ส่วนจะต้องคำนวณผ่าน DSP ทั้งสิ้น **4 ตัว** โดยสามารถใช้สาย Cascade `PCOUT` เชื่อมต่อเพื่อบวกทบค่าเลื่อนบิต ($2^{17}$ และ $2^{34}$) เข้าด้วยกันได้อย่างสมบูรณ์แบบ

---

### คำถามที่ 3: จะเกิดอะไรขึ้นหากสาย Cascade `PCOUT` ถูกสั่งให้เชื่อมต่อไปยัง DSP ในคอลัมน์อื่น?

ในโค้ด RTL หากวิศวกรบังคับให้เอาต์พุต `PCOUT` ของ DSP ในคอลัมน์ A วิ่งไปเข้า `PCIN` ของ DSP ในคอลัมน์ B ผลลัพธ์ในขั้นตอนการคอมไพล์จะเป็นอย่างไร?

---

#### ตัวเลือก:
A) Vivado จะสร้างสายส่งเฉพาะกิจเลี้ยวแนวนอนให้โดยอัตโนมัติ  
B) Vivado จะเกิดข้อผิดพลาดรุนแรงระดับ Critical Error: `[Place 30-574] Dedicated cascade route failed between non-adjacent columns` และการสร้างบิตสตรีมจะล้มเหลว  
C) ชิปจะทำงานช้าลง 10% แต่ไม่มี Error  
D) สัญญาณจะเปลี่ยนเป็นบัส AXI4 อัตโนมัติ

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) Vivado จะเกิดข้อผิดพลาดรุนแรงระดับ Critical Error: `[Place 30-574] Dedicated cascade route failed between non-adjacent columns` และการสร้างบิตสตรีมจะล้มเหลว**

##### เหตุผลทางกายภาพของโครงสร้างฮาร์ดแวร์:
พิน `PCIN` และ `PCOUT` ถูกผูกขาดทางกายภาพเฉพาะกับคอลัมน์แนวดิ่งเดียวกันเท่านั้น (Hard-wired Point-to-Point Silicon Segment) โดยไม่มีสวิตช์เมทริกซ์ใดๆ ในแนวระนาบแนวนอนมาเชื่อมต่อได้
ดังนั้น หากมีคำสั่งหรือการจัดวางที่บังคับให้ `PCOUT` ข้ามไปคอลัมน์อื่น เครื่องมือ Place & Route จะฟ้อง Error ขั้นวิกฤตทันทีเพราะไม่มีทางเดินสายจริงในชิปซิลิคอน
