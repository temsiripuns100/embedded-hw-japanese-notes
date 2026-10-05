# Lesson 153: BRAM Resource Management: Inference vs Instantiation (HDL Coding Templates, Portability vs Silicon Primitives RAMB36E2, ECC Hard Macros & Vivado Synthesis Pragmas (* ram_style = "block" | "distributed" *))

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 กลไกการถอดรหัสรูปแบบหน่วยความจำของ Synthesis Engine (Memory Inference Architecture)
ในขั้นตอนการแปลงภาษาฮาร์ดแวร์ (HDL Synthesis) เครื่องมือ EDA เช่น Vivado, Quartus หรือ Synplify Pro มีชุดอัลกอริทึม **Pattern Recognition Engine** ที่คอยตรวจจับโครงสร้างอาร์เรย์ตัวแปรในโค้ด Verilog/VHDL ว่าตรงกับแม่แบบ (Template) ของหน่วยความจำประเภทใด:

```
                  การตัดสินใจของ SYNTHESIS ENGINE ในการเลือกหน่วยความจำ
                  
  HDL Memory Array Declaration: reg [WIDTH-1:0] mem [(1<<DEPTH)-1:0];
                                |
                                v
               +----------------------------------+
               | มี Asynchronous Read หรือไม่?    |
               +----------------+-----------------+
                                |
               +----------------+----------------+
          YES  |                                 |  NO (Synchronous Read on Clock)
               v                                 v
  +--------------------------+     +----------------------------------+
  | DISTRIBUTED RAM (LUT RAM)|     | ความลึก (Depth) มีขนาดเท่าใด?    |
  | - เข้าถึงข้อมูลใน 0 Cycle|     +----------------+-----------------+
  | - สร้างจาก SLICEM LUTs   |                      |
  +--------------------------+         +------------+------------+
                                  < 64 |                         | >= 512
                                       v                         v
                         +--------------------------+  +--------------------------+
                         | DISTRIBUTED RAM (Default)|  | BLOCK RAM (RAMB36E2)     |
                         | - ประหยัด BRAM Macro     |  | - ความหนาแน่นสูง 36 Kb   |
                         +--------------------------+  +--------------------------+
```

#### สามประเภทสถาปัตยกรรมหน่วยความจำภายใน FPGA:
1. **Block RAM (BRAM / RAMB36E2):**
   * เซลล์ฮาร์ดแวร์เฉพาะกิจแบบ 6T SRAM ความหนาแน่นสูง ($36\text{ Kbits}$ ต่อบล็อก)
   * การอ่านและการเขียนต้องทำงานซิงโครไนซ์กับสัญญาณนาฬิกาเท่านั้น (Synchronous Read/Write) มี Latency ขั้นต่ำ $1$ ถึง $2$ ไซเคิล
2. **Distributed RAM (LUT RAM / SLICEM):**
   * ใช้หน่วยความจำแรมขนาดเล็กที่ฝังอยู่ในฟังก์ชันลอจิก LUT6 ของ SLICEM (เช่น RAM32X1S, RAM64X1D, RAM128X1D)
   * **ข้อได้เปรียบทางฟิสิกส์:** รองรับ **Asynchronous Read (อ่านข้อมูลออกได้ทันทีใน 0 Clock Cycle แบบ Combinational)** เหมาะสำหรับ FIFO ขนาดเล็ก, Register Files, และ State Buffers
3. **UltraRAM (URAM288 บน UltraScale+):**
   * บล็อกหน่วยความจำขนาดยักษ์ $288\text{ Kbits}$ แบบ Dual-Port Single-Clock ความลึกคงที่ $4,096 \times 72\text{ bits}$
   * เหมาะสำหรับ Framebuffer ขนาดใหญ่และ Network Packet Buffers

---

### 1.2 การเปรียบเทียบเชิงวิศวกรรม: HDL Inference vs Hard Primitive Instantiation

```
+------------------------------------+---------------------------------------+---------------------------------------+
| มิติการประเมินทางวิศวกรรม          | HDL INFERENCE (การเขียนตามแม่แบบ)     | HARD INSTANTIATION (RAMB36E2 โดยตรง)  |
+------------------------------------+---------------------------------------+---------------------------------------+
| 1. ความสามารถในการพอร์ต (Portability)| **สูงสุด (100% Portable)** ข้ามผู้ผลิต  | **ต่ำมาก (Vendor Locked)** ยึดติดตระกูล |
+------------------------------------+---------------------------------------+---------------------------------------+
| 2. การควบคุมฮาร์ดแวร์ขั้นสูง       | จำกัด (ขึ้นกับการตีความของ Synthesis) | **สมบูรณ์แบบ 100%** เข้าถึงทุกพินลึก   |
+------------------------------------+---------------------------------------+---------------------------------------+
| 3. Built-in Hardware SEC-DED ECC   | ทำไม่ได้ (ต้องเขียน ECC ลอจิกภายนอก)  | **รองรับในตัว (Zero Fabric Overhead)**|
+------------------------------------+---------------------------------------+---------------------------------------+
| 4. BRAM Direct Cascade Interconnect| พึ่งพาเครื่องมือ Synthesizer Retiming | **บังคับต่อตรงผ่านพิน CASCIN/OUT ได้**|
+------------------------------------+---------------------------------------+---------------------------------------+
| 5. พาริตีบิตอิสระ (Byte Parity)    | ยุ่งยากต่อการจัดสรร                   | กำหนดพอร์ต `DOPADOP` ได้โดยตรง        |
+------------------------------------+---------------------------------------+---------------------------------------+
```

#### สถาปัตยกรรมฮาร์ดแวร์ SEC-DED ECC ภายใน RAMB36E2:
ในระบบอากาศยานและยานยนต์ตามมาตรฐาน DO-254 และ ISO 26262 ชิปหน่วยความจำต้องมีกลไกป้องกันอนุภาคพลังงานสูงในอวกาศ (Neutron / Alpha Particle Single-Event Upset: SEU) บล็อก `RAMB36E2` มีวงจรฮาร์ดแวร์ **Single Error Correction, Double Error Detection (SEC-DED)** แบบ $(72, 64)$ Hamming Code ฝังอยู่ในซิลิคอน:
* เมื่อเขียนข้อมูล $64\text{ บิต}$: ฮาร์ดแวร์จะคำนวณและบันทึก Parity Bits ขนาด $8\text{ บิต}$ ลงในพาริตีเซลล์โดยอัตโนมัติ
* เมื่ออ่านข้อมูล: วงจรจะตรวจจับและแก้ไขบิตที่กลับขั้ว $1$ บิตได้ในตัว (Single-Bit Correction) พร้อมยกสัญญาณเตือน `SBITERR` และหากพบการพัง $2$ บิตพร้อมกัน (Double-Bit Fault) จะยกสัญญาณ `DBITERR` เพื่อสั่งชัตดาวน์ระบบอย่างปลอดภัย!
* *ฟังก์ชันฮาร์ดแวร์ระดับเทพนี้จะเปิดใช้งานได้สมบูรณ์แบบที่สุดผ่านการทำ Hard Instantiation ของ `RAMB36E2` เท่านั้น!*

---

### 1.3 การบังคับคำสั่ง Synthesis Pragmas (`(* ram_style *)`)
เมื่อวิศวกรต้องการเขียนโค้ดที่สามารถพอร์ตได้ (Inference) แต่ต้องการบังคับให้เครื่องมือจัดสรรทรัพยากรตามที่ต้องการ จะใช้แอตทริบิวต์สังเคราะห์:

```verilog
// 1. บังคับให้แมปเป็น Block RAM Hard Macro เสมอ
(* ram_style = "block" *)
reg [63:0] packet_buffer [1023:0];

// 2. บังคับให้แมปเป็น Distributed RAM (LUT RAM) เสมอ
(* ram_style = "distributed" *)
reg [31:0] cpu_register_file [31:0];

// 3. บังคับให้แมปเป็น UltraRAM บนชิป UltraScale+
(* ram_style = "ultra" *)
reg [71:0] large_frame_buffer [16383:0];

// 4. บังคับให้แตกตัวเป็น Flip-Flops ปกติใน Slice
(* ram_style = "registers" *)
reg [7:0] delay_pipeline [15:0];
```

---

### 1.4 กับดักการผลาญทรัพยากร BRAM ในอาร์เรย์ขนาดเล็ก (The Small Memory Waste Trap)

ความผิดพลาดที่พบบ่อยที่สุดของนักออกแบบคือ: *"ปล่อยให้อาร์เรย์ขนาดเล็กถูกสังเคราะห์เป็น BRAM"*

```
             กับดักการใช้ BRAM สิ้นเปลือง: ตารางจัดเก็บ KEY ขนาด 32 คำ x 32 บิต
             
  [ การสังเคราะห์ที่ผิดพลาด: หลุดเป็น BRAM ]      [ การสังเคราะห์ที่ถูกต้อง: Distributed RAM ]
  -----------------------------------------      -------------------------------------------
  ใช้บล็อก RAMB36E2 จำนวน 1 บล็อก                ใช้ SLICEM LUT6 จำนวนเพียง 16 ตัว
  - ความจุของ BRAM: 36,864 บิต                   - พื้นที่ Logic: 2 Slices เท่านั้น
  - ข้อมูลจริงที่ใช้ : 1,024 บิต                   - Latency การอ่าน: 0 Cycle (Asynchronous)
  - สัดส่วนการสูญเปล่า: ผลาญทิ้ง 97.2%!           - ประสิทธิภาพการใช้พื้นที่: 100% สมบูรณ์แบบ!
  ===> ส่งผลให้ BRAM หมดชิปในโปรเจกต์ใหญ่!       ===> BRAM ถูกเก็บไว้ให้ Framebuffer ตัวจริง!
```

> [!IMPORTANT]
> **กฎเหล็กวิศวกรรมสากล (The Golden Boundary Rule):**  
> * **เมื่อความลึก $\le 64$ หรือ $\le 128$ คำ:** จงใส่ `(* ram_style = "distributed" *)` เสมอ เพื่อลดความล่าช้าในการอ่าน (0-cycle async read) และประหยัด BRAM Macro ไว้ให้งานขนาดใหญ่  
> * **เมื่อความลึก $\ge 512$ คำ:** จงใส่ `(* ram_style = "block" *)` เพื่อป้องกันไม่ให้ Distributed RAM ไปแย่งใช้ LUT จน logic ของชิปเต็ม

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** การ์ดเร่งความเร็วการเข้ารหัสข้อมูลในศูนย์ข้อมูลระดับ Hyperscale Data Center (Hardware Cryptographic Accelerator) บน FPGA Kintex UltraScale+ (XCKU115):
* ระบบประกอบด้วยโมดูล AES-256 GCM Core ขนานกันจำนวน 32 แชนแนล
* แต่ละแชนแนลมีตารางจัดเก็บคีย์เข้ารหัสลับ (Key Vault Table) ขนาด $32\text{ คำ} \times 256\text{ บิต}$ ($8,192\text{ บิต}$ ต่อแชนแนล)

**วิกฤตหน้างาน:** ในระหว่างการประกอบรวมระบบระดับ Top-Level (System Integration) ร่วมกับส่วนประมวลผลเครือข่าย 100GbE การรันคำสั่ง Place & Route ใน Vivado ล้มเหลวทันทีด้วยข้อผิดพลาด:  
`[Place 30-484] Not enough BRAM blocks available in the target device. Required: 1180, Available: 1080.`  
โครงการไม่สามารถสังเคราะห์ Bitstream ได้ กำหนดการส่งมอบให้กับลูกค้าระดับองค์กรหยุดชะงัก ผู้บริหารสั่งประชุมด่วนและเตรียมเปลี่ยนชิปเป็นเบอร์ใหญ่ขึ้นซึ่งจะเพิ่มต้นทุนบอร์ดบานปลายกว่า 45 ล้านบาท!

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] ทรัพยากร BRAM บนชิปเต็ม (ขาด 100 บล็อก) ไม่สามารถคอมไพล์ระบบได้
      |
      +---> [Why 1] ทำไม BRAM ถึงถูกใช้งานเกินจำนวนที่มีบนชิป (1,180 / 1,080)?
      |             --> เพราะโมดูล AES Core 32 แชนแนลเพียงตัวเดียว ดึง BRAM ไปใช้งานถึง 256 บล็อก!
      |
      +---> [Why 2] ทำไม AES Core 32 ตัวถึงกิน BRAM มหาศาลขนาดนั้น?
      |             --> เพราะตาราง Key Vault แต่ละตัวดึง BRAM36 ไปถึง 8 บล็อกต่อแชนแนล (32 x 8 = 256 บล็อก)
      |
      +---> [Why 3] ทำไมตาราง Key Vault ขนาดเพียง 32 คำ x 256 บิต ถึงใช้ BRAM36 ตั้ง 8 บล็อก?
      |             --> เพราะผู้ออกแบบเขียน Verilog โดยไม่มีคำสั่งกำกับ และ Vivado ตัดสินใจเลือก BRAM36 ให้
      |                 เนื่องจากโครงสร้างบัสกว้าง 256 บิต ทำให้ต้องวาง BRAM เรียงขนานกันถึง 8 ตัว!
      |
      +---> [Why 4] ทำไมผู้ออกแบบถึงไม่ได้ระบุ ram_style เป็น Distributed RAM?
      |             --> เพราะผู้ออกแบบเข้าใจว่า "เมื่อเป็น Array หน่วยความจำ ก็ต้องใช้ Block RAM เสมอ"
      |                 โดยไม่ได้คำนวณสัดส่วนการสูญเปล่าของความจุภายใน Macro
      |
      +---> [Why 5 - Root Cause] ข้อมูลจริงที่ใช้เทียบกับความจุของ BRAM ที่สูญเสียไปเป็นเท่าใด?
                    --> ข้อมูลจริงต่อแชนแนลมีเพียง 8,192 บิต แต่ BRAM36 จำนวน 8 ตัวมีความจุถึง 294,912 บิต
                        เกิดการสูญเปล่าทางซิลิคอนสูงถึง 97.2% โดยไร้ประโยชน์!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการเกิด BRAM Resource Exhaustion ในระบบเข้ารหัสข้อมูล 100G

   CODING PRACTICES (No Pragmas)              SYNTHESIS HEURISTICS (EDA Tool)
         |                                          |
   เขียนโค้ด Memory Array โดยไม่มี pragma กำกับ      Vivado เลือกใช้ BRAM อัตโนมัติเมื่อพบบัสกว้าง 256 บิต
         \                                          /
          \   ความลึก 32 คำ สั้นเกินไปสำหรับ BRAM   /   วาง BRAM36 ขนาน 8 ตัวเพื่อตอบสนองความกว้างบัส
           \   ผลาญทิ้ง 97.2% ของความจุซิลิคอน      /   ขาดการตรวจสอบ Synthesis Utilization Breakdown
            +------------------------------------+
            |                                    |
            |   BRAM UTILIZATION OVERFLOW        |===> [CRITICAL BUILD TAPE-OUT FAILURE]
            |   (1,180 / 1,080 BLOCKS EXCEEDED)  |
            +------------------------------------+
           /                                      \
          /   ขาดการประสานงานระหว่างทีม Crypto และ IP\   ทดสอบเฉพาะระดับบล็อกเดี่ยว (Standalone Test)
         /                                          \
   ไม่มีการกำหนด Budgeting ทรัพยากรต่อโมดูล           ละเลยการตรวจสอบจำนวน Hard Macro ในขั้นตอน Architecture
         |                                          |
   PROJECT GOVERNANCE                         INTEGRATION TESTING GAPS
```

---

### ขั้นตอนการแก้ปัญหาและแนวทางปรับปรุงสถาปัตยกรรม (Corrective Actions & SOP)

#### ขั้นตอนที่ 1: บังคับใช้ `(* ram_style = "distributed" *)` บนตาราง Key Vault
แก้ไขโค้ด RTL ในโมดูล AES Key Vault เพื่อบังคับให้เครื่องมือแมปข้อมูลลงใน SLICEM LUT RAM:

```verilog
// ==============================================================================
// SOP-COMPLIANT AES KEY VAULT USING DISTRIBUTED RAM (ZERO BRAM CONSUMPTION!)
// ==============================================================================
module aes_key_vault_lutram #(
    parameter integer KEY_DEPTH = 32,
    parameter integer KEY_WIDTH = 256
)(
    input  wire                   clk,
    input  wire                   we,
    input  wire [$clog2(KEY_DEPTH)-1:0] addr,
    input  wire [KEY_WIDTH-1:0]   din,
    output wire [KEY_WIDTH-1:0]   dout // อ่านแบบ Asynchronous ได้ใน 0 Cycle!
);

    // บังคับใช้ Distributed RAM เพื่อประหยัด BRAM Macro ไว้ให้โมดูลอื่น
    (* ram_style = "distributed" *) reg [KEY_WIDTH-1:0] key_mem [KEY_DEPTH-1:0];

    always @(posedge clk) begin
        if (we) begin
            key_mem[addr] <= din;
        end
    end

    // การอ่านแบบอะซิงโครนัสช่วยลด Latency ของการค้นหาคีย์ลง 1 รอบทันที!
    assign dout = key_mem[addr];

endmodule
```

#### ผลลัพธ์หลังการปรับปรุง:
* จำนวน BRAM ที่ใช้งานในโมดูลเข้ารหัสลดลงจาก **$256\text{ บล็อก} \implies \mathbf{0\text{ บล็อก!}}$**
* ทรัพยากร BRAM รวมทั้งชิปลดลงเหลือ **$924 / 1,080\text{ บล็อก}$ (คิดเป็น $85.5\%$ มี Margin เหลือเฟือ)**
* การใช้ Slice LUT เพิ่มขึ้นเพียงเล็กน้อย (ใช้เพียง $128\text{ LUTs}$ ต่อแชนแนล ซึ่งคิดเป็นไม่ถึง $0.5\%$ ของชิป)
* ระบบผ่านการคอมไพล์ Bitstream สำเร็จ $100\%$ โดยไม่ต้องเปลี่ยนเบอร์ชิป ประหยัดเงินของโครงการได้กว่า 45 ล้านบาท!

---

### SOP Checklist สำหรับการตรวจสอบและจัดสรรทรัพยากรหน่วยความจำ (Memory Resource Allocation Sign-Off)

```
[ ] 1. Memory Depth Audit Rule:
       - อาร์เรย์ใดๆ ที่มีความลึก <= 128 คำ: บังคับใส่ `(* ram_style = "distributed" *)` ในโค้ด RTL
       - ห้ามปล่อยให้อาร์เรย์ขนาดเล็กถูกแมปเข้า Block RAM โดยเด็ดขาด

[ ] 2. Large Buffer Memory Audit:
       - อาร์เรย์ใดๆ ที่มีความจุ >= 288 Kbits บน UltraScale+: บังคับใส่ `(* ram_style = "ultra" *)`
       - ตรวจสอบว่าพอร์ตใช้งานทั้งสองพอร์ตทำงานบน Clock เดียวกันตามข้อกำหนดของ UltraRAM

[ ] 3. Safety-Critical Hardware ECC Enforcement:
       - ในระบบมาตรฐาน DO-254 / ISO 26262: หน่วยความจำ BRAM ที่เก็บข้อมูลสำคัญต้องเปิดใช้ SEC-DED ECC
       - ยืนยันว่ามีการดึงพินสัญญาณ `SBITERR` และ `DBITERR` เข้าสู่ตัวจัดการ Safety Interrupt

[ ] 4. Synthesis Log Memory Cross-Check:
       - ตรวจสอบตาราง "RAM Extraction Table" ใน Vivado Synthesis Log
       - ยืนยันว่าไม่มีคำเตือนการตกหล่นของหน่วยความจำ หรือการสร้าง MUX ขนาดใหญ่เกินจำเป็น
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| メモリ推論 | めもりすいろん | Memori Suiron | การอนุมานหน่วยความจำอัตโนมัติจากโค้ด (Memory Inference) |
| プリミティブ直接配置 | ぷりみてぃぶちょくせつはいち | Purimitibu Chokusetsu Haichi | การอินสแตนชิเอตฮาร์ดแวร์โดยตรง (Hard Macro Instantiation) |
| 分散RAM | ぶんさんらむ | Bunsan Ramu | หน่วยความจำแบบกระจายบน LUT (Distributed RAM / LUT RAM) |
| 誤り訂正符号 | あやまりていせいふごう | Ayamari Teisei Fugō | รหัสตรวจจับและแก้ไขข้อผิดพลาด (Error Correcting Code: ECC) |
| 単一ビット誤り訂正 | たんいつびっとあやまりていせい | Tan'itsu Bitto Ayamari Teisei | การแก้ไขบิตผิดพลาดเดี่ยว (Single Error Correction: SEC) |
| 2ビット誤り検出 | にびっとあやまりけんしゅつ | Ni-Bitto Ayamari Kenshutsu | การตรวจจับบิตผิดพลาดคู่ (Double Error Detection: DED) |
| 資源浪費 | しげんろうひ | Shigen Rōhi | การผลาญทรัพยากรบนชิปโดยสูญเปล่า (Resource Wastage) |
| 属性記述 | ぞくせいきじゅつ | Zokusei Kijutsu | การระบุแอตทริบิวต์สังเคราะห์ (Synthesis Attribute / Pragma) |
| アスペクト比変換 | あすぺくとひへんかん | Asupekuto-hi Henkan | การแปลงอัตราส่วนความกว้างต่อความลึกของพอร์ต (Port Aspect Ratio) |
| カスケード配線 | かすけーどはいせん | Kasukēdo Haisen | สายสัญญาณเชื่อมต่อภายในระหว่างบล็อก (Dedicated Cascade Routing) |
| 移植性維持 | いしょくせいいじ | Ishokusei Iji | การรักษาความสามารถในการพอร์ตโค้ดข้ามตระกูล (Code Portability) |
| 合成ログ検証 | ごうせいろぐけんしょう | Gōsei Rogu Kenshō | การตรวจสอบความถูกต้องของบันทึกการสังเคราะห์ (Synthesis Log Audit) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการใช้อาร์เรย์ขนาดเล็กใน BRAM จนทรัพยากรล้นชิป
**สถานที่:** ห้องประชุมวิศวกรรมสถาปัตยกรรมระบบ FPGA (FPGA Architecture Review Meeting)  
**ผู้เข้าร่วม:** Chief Hardware Architect (หัวหน้าสถาปนิกฮาร์ดแวร์) และ Crypto Subsystem Designer (วิศวกรผู้ออกแบบระบบย่อย)

* **Chief Architect:**  
  「おい、このPlace & Routeの失敗ログを見ろ。BRAMの使用数が1180ブロックで、デバイスの上限1080を超過して配置配線がエラー停止しているじゃないか！犯人は暗号化コアだ。わずか32エントリしかないKey Vaultテーブルに、なぜBRAM36を丸ごと8個も割り当てているんだ？32ワード×256ビットなら合計8Kbit程度だぞ。36KbitのBRAMを8個並べたら290Kbit以上ある。シリコン容量の97%をドブに捨てている自覚はあるのか？」  
  *(Oi, kono Place & Route no shippai rogu o miro. BRAM no shiyōsū ga 1180-burokku de, debaisu no jōgen 1080 o chōka shite haichi haisen ga erā teishi shite iru ja nai ka! Hannin wa angōka koa da. Wazuka 32-entori shika nai Key Vault tēburu ni, naze BRAM36 o marugoto 8-ko mo wariadete iru n da? 32-wādo x 256-bitto nara gōkei 8Kbit teido da zo. 36Kbit no BRAM o 8-ko narabetara 290Kbit ijō aru. Shirikon yōryō no 97% o dobu ni sutete iru jikaku wa aru no ka?)*  
  **ความหมาย:** "เฮ้ย ดู Log ข้อผิดพลาดของ Place & Route ตรงนี้สิ การใช้ BRAM พุ่งไปถึง 1180 บล็อก เกินเพดาน 1080 ของอุปกรณ์จนคอมไพล์ค้างไปแล้ว! ตัวการคือโมดูลเข้ารหัสนี่เอง ตาราง Key Vault ที่มีความลึกแค่ 32 แถว ทำไมคุณถึงปล่อยให้มันดึง BRAM36 ไปตั้ง 8 บล็อกเต็มๆ? 32 เวิร์ด $\times$ 256 บิต ข้อมูลจริงมันแค่ราวๆ 8Kbit เองนะ แต่การเอา BRAM36 มาเรียงกัน 8 ก้อนมันมีความจุตั้ง 290Kbit คุณรู้ตัวไหมว่ากำลังโยนเนื้อซิลิคอนทิ้งน้ำไปเปล่าๆ ถึง 97% น่ะ?"

* **Subsystem Designer:**  
  「データ幅が256ビットと非常に広かったため、通常のRAM記述を行ったところ、合成ツールが自動的にBRAMを選択してしまいました。小規模メモリをLUTで構成するプラグマの指定が漏れていました。」  
  *(Dēta-haba ga 256-bitto to hijō ni hirokatta tame, tsūjō no RAM kijutsu o okonatta tokoro, gōsei tsūru ga jidōteki ni BRAM o sentaku shite shimaimashita. Shōkibo memori o LUT de kōsei suru puraguma no shitei ga morete imashita.)*  
  **ความหมาย:** "เพราะความกว้างบัสข้อมูลมันกว้างถึง 256 บิตครับ พอเขียนอาร์เรย์แบบปกติ เครื่องมือมันเลยจัดแจงเลือก BRAM ให้เองโดยอัตโนมัติ ผมลืมใส่ Pragma กำกับให้ใช้ LUT สำหรับหน่วยความจำขนาดเล็กครับ"

* **Chief Architect:**  
  「幅が広くても深さが32なら、分散RAM（`ram_style = "distributed"`）を使うのが定石だ！LUTなら非同期読み出しができるから、暗号鍵のルックアップレイテンシも1サイクル短縮できる。直ちに属性指定を追加して再合成しろ。BRAMを1ブロックも使わずに解決できるはずだ！」  
  *(Haba ga hirokute mo fukasa ga 32 nara, bunsan RAM (`ram_style = "distributed"`) o tsukau no ga jōseki da! LUT nara hidōki yomidashi ga dekiru kara, angōkagi no rukkuappu reitenshi mo 1-saikuru tanshuku dekiru. Tadachini zokusei shitei o tsuika shite sai-gōsei shiro. BRAM o 1-burokku mo tsukawazu ni kaiketsu dekiru hazu da!)*  
  **ความหมาย:** "ต่อให้บัสจะกว้าง แต่ถ้าความลึกแค่ 32 กฎเหล็กตามตำราคือต้องใช้ Distributed RAM (`ram_style = "distributed"`)! ยิ่งไปกว่านั้นถ้าเป็น LUT มันอ่านแบบ Asynchronous ได้ ช่วยลด Latency ในการดึงคีย์ลงได้อีก 1 ไซเคิลทันที ไปใส่แอตทริบิวต์กำกับแล้วรันใหม่เดี๋ยวนี้ งานนี้ต้องแก้ได้โดยไม่ต้องผลาญ BRAM แม้แต่บล็อกเดียว!"

---

#### สถานการณ์ที่ 2: การตรวจสอบมาตรฐานความปลอดภัย Functional Safety และการใช้ Hardware ECC
* **Chief Architect:**  
  「航空宇宙安全規格（DO-254 DAL-A）のチェック項目だが、テレメทリフレームを格納する重要BRAMにECCエラー訂正回路が入っていない。ソフトロジックでパリティを計算しているようだが、ソフトで組んだらLUTを大量消費するし、マルチビット化け（DBITERR）の検出も不完全だ。なぜRAMB36E2に内蔵されているハードウェアSEC-DED ECCを使わないんだ？」  
  *(Kōkū uchū anzen kikaku (DO-254 DAL-A) no chekku kōmoku da ga, terem push tori furēmu o kakunō suru jūyō BRAM ni ECC erā teisei kairo ga haitte inai. Sofuto rojikku de pariti o keisan shite iru yō da ga, sofuto de kundara LUT o tairyō shōhi suru shi, maruchibitto bake (DBITERR) no kenshutsu mo fukanzen da. Naze RAMB36E2 ni naizō sarete iru hādowea SEC-DED ECC o tsukawanai n da?)*  
  **ความหมาย:** "ในข้อกำหนดความปลอดภัยอากาศยาน DO-254 DAL-A บน BRAM สำคัญที่เก็บเฟรมข้อมูล Telemetry คุณไม่ได้ใส่วงจรแก้ข้อผิดพลาด ECC เข้าไป เห็นเขียนลอจิกคำนวณพาริตีด้วยซอฟต์แวร์ภายนอก แต่วิธีนั้นมันผลาญ LUT มหาศาล แถมการดักจับข้อผิดพลาดหลายบิต (DBITERR) ก็ทำได้ไม่สมบูรณ์ ทำไมไม่เรียกใช้ฮาร์ดแวร์ SEC-DED ECC ที่ฝังมาในบล็อก RAMB36E2?"

* **Subsystem Designer:**  
  「コードのポータビリティ（他社FPGAへの移植性）を維持したかったため、Xilinx専用のプリミティブ直接インスタンス化を避けていました。」  
  *(Kōdo no pōtabiriti (tasha FPGA e no ishokusei) o iji shitakatta tame, Xilinx sen'yō no purimitibu chokusetsu insutansu-ka o sakete imashita.)*  
  **ความหมาย:** "เพราะผมต้องการรักษาความสามารถในการพอร์ตโค้ดข้ามค่ายครับ เลยเลี่ยงการเรียกใช้พรีมิทิฟเฉพาะของ Xilinx โดยตรงครับ"

* **Subsystem Specialist:**  
  「人命に関わる航空宇宙機器において、ポータビリティを理由にシリコンの安全保護機能を犠牲にするのは本末転倒だ！RAMB36E2のECCハードマクロはLUT消費ゼロで単一ビット反転をリアルタイム修復できる。安全クリティカルなブロックはプリミティブ直叩き（ハードインスタンス化）に切り替えろ。`SBITERR` と `DBITERR` のステータス割り込みピンを安全監視プロセッサへ接続すること！」  
  *(Jinmei ni kakawaru kōkū uchū kiki ni oite, pōtabiriti o riyū ni shirikon no anzen hogo kinō o gisei ni suru no wa hommatsutentō da! RAMB36E2 no ECC hādomakuro wa LUT shōhi zero de tan'itsu bitto hanten o riarutaimu shūfuku dekiru. Anzen kuritikaru na burokku wa purimitibu jikatataki (hādo insutansu-ka) ni kirikaero. `SBITERR` to `DBITERR` no sutētasu warikomi pin o anzen kanshi purosessa e setsuzoku suru koto!)*  
  **ความหมาย:** "ในอุปกรณ์การบินที่เกี่ยวกับชีวิตมนุษย์ การเอาเรื่อง Portability มาเป็นข้ออ้างเพื่อสละระบบความปลอดภัยของเนื้อซิลิคอน มันคือการจับแพะชนแกะอย่างร้ายแรง! ฮาร์ดแวร์ ECC ใน RAMB36E2 มันซ่อมบิตกลับขั้วได้แบบเรียลไทม์โดยไม่กิน LUT เลยแม้แต่ตัวเดียว บล็อกที่เป็น Safety-Critical ให้เปลี่ยนไปเรียกใช้ Primitive โดยตรงทันที แล้วต่อขาขัดจังหวะ `SBITERR` กับ `DBITERR` เข้าสู่ซีพียูตรวจสอบความปลอดภัยเดี๋ยวนี้!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณประสิทธิภาพการใช้พื้นที่ซิลิคอนและทรัพยากรระหว่าง BRAM vs Distributed RAM (Silicon Utilization Efficiency Calculation)
ในระบบประมวลผลเครือข่ายความเร็วสูง วิศวกรต้องการสร้างอาร์เรย์หน่วยความจำขนาดเล็กจำนวน $K = 16\text{ ตัว}$ แต่ละตัวมีขนาด:
* ความลึก: $64\text{ คำ}$
* ความกว้างบัสข้อมูล: $128\text{ บิต}$
* ข้อมูลจริงต่อตัว: $64 \times 128 = 8,192\text{ บิต}$

เปรียบเทียบการเลือกโครงสร้างฮาร์ดแวร์สองทางเลือกบน UltraScale+:
* **ทางเลือก A (สังเคราะห์เป็น BRAM36):**
  * พอร์ตความกว้างสูงสุดของ RAMB36E2 ในโหมดตัวเดียวคือ $72\text{ บิต}$ (หรือ $64\text{ บิต}$ เมื่อไม่ใช้พาริตี)
  * ดังนั้นความกว้าง $128\text{ บิต}$ ต้องใช้ BRAM36 จำนวน $2\text{ บล็อกต่อหนึ่งตัว}$
  * ความจุรวมของซิลิคอนที่ BRAM จัดสรรให้: $2 \times 36,864\text{ บิต} = 73,728\text{ บิตต่อตัว}$
* **ทางเลือก B (สังเคราะห์เป็น Distributed RAM บน SLICEM LUTs):**
  * ในสถาปัตยกรรม UltraScale+ เซลล์ RAM64X1D ใช้ $1\text{ LUT6}$
  * สำหรับความลึก 64 คำ ความกว้าง 128 บิต ต้องใช้ LUT6 จำนวน:
    $$N_{lut} = 128\text{ LUTs ต่อหนึ่งตัว}$$
  * การใช้ BRAM: $0\text{ บล็อก}$

จงคำนวณหา:
1. ประสิทธิภาพการใช้พื้นที่ข้อมูลของ BRAM ในทางเลือก A ($\eta_{A} = \frac{\text{ข้อมูลจริง}}{\text{ความจุ BRAM ที่จัดสรร}} \times 100\%$)
2. จำนวนบล็อก BRAM ทั้งหมดที่สูญเสียไปสำหรับทั้ง 16 อาร์เรย์ในทางเลือก A
3. จำนวน Slice LUTs ทั้งหมดที่ต้องใช้ในทางเลือก B:

A) $\eta_A \approx 11.11\%, \quad \text{ใช้ BRAM รวม} = 32\text{ บล็อก}, \quad \text{ใช้ LUT รวม} = 2,048\text{ LUTs}$  
B) $\eta_A \approx 22.22\%, \quad \text{ใช้ BRAM รวม} = 16\text{ บล็อก}, \quad \text{ใช้ LUT รวม} = 1,024\text{ LUTs}$  
C) $\eta_A \approx 5.55\%, \quad \text{ใช้ BRAM รวม} = 64\text{ บล็อก}, \quad \text{ใช้ LUT รวม} = 4,096\text{ LUTs}$  
D) $\eta_A \approx 50.00\%, \quad \text{ใช้ BRAM รวม} = 32\text{ บล็อก}, \quad \text{ใช้ LUT รวม} = 512\text{ LUTs}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณประสิทธิภาพการใช้พื้นที่ของ BRAM ในทางเลือก A**
ข้อมูลจริงต่ออาร์เรย์:
$$\text{Data Size} = 64 \times 128 = 8,192\text{ บิต}$$
ความจุของ BRAM ที่จัดสรรต่ออาร์เรย์ (ใช้ BRAM36 จำนวน 2 ตัวเพื่อรองรับความกว้าง 128 บิต):
$$\text{Allocated Size} = 2 \times 36,864\text{ บิต} = 73,728\text{ บิต}$$
ประสิทธิภาพการใช้ความจุ:
$$\eta_A = \frac{8,192\text{ บิต}}{73,728\text{ บิต}} \times 100\% = \frac{1}{9} \times 100\% \approx 11.111\% \approx 11.11\%$$
*(เกิดการสูญเปล่าของเนื้อซิลิคอนสูงถึง $100\% - 11.11\% = 88.89\%$!)*

**ขั้นตอนที่ 2: คำนวณการใช้ BRAM รวมทั้ง 16 ตัวในทางเลือก A**
$$\text{Total BRAMs} = 16 \times 2 = 32\text{ บล็อก RAMB36E2}$$
*(ผลาญ BRAM36 ไปถึง 32 ก้อน ซึ่งสามารถนำไปทำบัฟเฟอร์ภาพ 4K ได้หลายเฟรม!)*

**ขั้นตอนที่ 3: คำนวณการใช้ Slice LUTs รวมทั้ง 16 ตัวในทางเลือก B**
จำนวน LUT ต่ออาร์เรย์:
$$N_{lut\_single} = 128\text{ LUTs (เนื่องจากความลึก 64 คำพอดีกับขนาด 1 LUT6)}$$
สำหรับทั้ง 16 อาร์เรย์:
$$N_{lut\_total} = 16 \times 128\text{ LUTs} = 2,048\text{ LUTs}$$
บนชิป Kintex UltraScale+ ที่มี LUT มากกว่า 300,000 ตัว การใช้ $2,048\text{ LUTs}$ คิดเป็นเพียง **$< 0.7\%$** เท่านั้น!

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($\eta_A \approx 11.11\%, \text{ใช้ BRAM รวม} = 32\text{ บล็อก}, \text{ใช้ LUT รวม} = 2,048\text{ LUTs}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคิดว่าใช้ BRAM36 เพียง 1 ตัวต่ออาร์เรย์ ซึ่งเป็นไปไม่ได้ทางกายภาพเพราะ 1 BRAM36 รับบัสได้กว้างสุดเพียง 72 บิต
* ข้อ C คิดจำนวน BRAM เกินจริงไปเท่าตัว
* ข้อ D มีการคำนวณสัดส่วนประสิทธิภาพผิดพลาด

---

### คำถามที่ 2: การคำนวณจำนวนพาริตีบิตสำหรับฮาร์ดแวร์ SEC-DED ECC (Hardware SEC-DED ECC Parity Calculation)
ในระบบควบคุมอากาศยานตามมาตรฐาน DO-254 บล็อก `RAMB36E2` ถูกตั้งค่าในโหมดฮาร์ดแวร์ **SEC-DED ECC** (Single Error Correction, Double Error Detection):
* ความกว้างบัสข้อมูลดิบ (Data Word Width): $M = 64\text{ บิต}$
* ระบบใช้รหัส Hamming Code แบบขยาย (Extended Hamming Code $(N, M)$) ที่มีคุณสมบัติ:
  1. สามารถแก้ไขข้อผิดพลาดบิตเดี่ยว (Correct 1-bit error)
  2. สามารถตรวจจับข้อผิดพลาดบิตคู่ (Detect 2-bit error)
  3. ไม่สร้างสัญญาณลวงเมื่อเกิดข้อผิดพลาด 2 บิต

กำหนดอสมการแฮมมิง (Hamming Rule for SEC-DED):
$$2^{k-1} \ge M + k$$
โดยที่ $k$ คือจำนวนบิตพาริตีตรวจสอบ (Parity / Check Bits)

จงคำนวณหา:
1. จำนวนบิตพาริตีขั้นต่ำ ($k$) ที่จำเป็นต้องใช้สำหรับข้อมูล $M = 64\text{ บิต}$
2. ความกว้างของคำข้อมูลรวมทั้งหมดที่จัดเก็บในเซลล์ BRAM ($N = M + k$)
3. จำนวนกลุ่มตรวจสอบข้อผิดพลาด (Syndrome Bit Combinations) ทั้งหมดที่เกิดขึ้นได้จากบิตพาริตี $k$:

A) $k = 7\text{ บิต}, \quad N = 71\text{ บิต}, \quad \text{Syndromes} = 128$  
B) $k = 8\text{ บิต}, \quad N = 72\text{ บิต}, \quad \text{Syndromes} = 256$  
C) $k = 6\text{ บิต}, \quad N = 70\text{ บิต}, \quad \text{Syndromes} = 64$  
D) $k = 9\text{ บิต}, \quad N = 73\text{ บิต}, \quad \text{Syndromes} = 512$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: ตรวจสอบอสมการแฮมมิงสำหรับ SEC-DED**
อสมการสำหรับ SEC-DED (Extended Hamming Code):
$$2^{k-1} \ge M + k$$
ข้อมูลนำเข้า: $M = 64\text{ บิต}$

* ทดสอบ $k = 7$:
  $$2^{7-1} = 2^6 = 64$$
  $$M + k = 64 + 7 = 71$$
  เนื่องจาก $64 < 71$ (**ไม่ผ่าน!** $k = 7$ ไม่เพียงพอสำหรับ SEC-DED บน 64 บิต)
* ทดสอบ $k = 8$:
  $$2^{8-1} = 2^7 = 128$$
  $$M + k = 64 + 8 = 72$$
  เนื่องจาก $128 \ge 72$ (**ผ่านเกณฑ์อย่างสมบูรณ์!**)

**ขั้นตอนที่ 2: คำนวณความกว้างคำข้อมูลรวม ($N$)**
$$N = M + k = 64\text{ บิต} + 8\text{ บิต} = 72\text{ บิต}$$
*(นี่คือเหตุผลทางฟิสิกส์ว่าทำไม BRAM36 จึงถูกออกแบบให้มีขนาด $512 \times 72\text{ bits}$ หรือ $64\text{ data bits} + 8\text{ parity bits}$ พอดีเป๊ะ!)*

**ขั้นตอนที่ 3: คำนวณจำนวนสถานะ Syndrome Vector**
เวกเตอร์ Syndrome มีขนาด $k = 8\text{ บิต}$:
$$\text{จำนวนสถานะทั้งหมด} = 2^k = 2^8 = 256\text{ รูปแบบ}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **B** ($k = 8\text{ บิต}, N = 72\text{ บิต}, \text{Syndromes} = 256$) สอดคล้องกับโครงสร้างฮาร์ดแวร์ $(72, 64)$ ECC ของ RAMB36E2 ใน FPGA จริง

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะ $k = 7$ เพียงพอสำหรับ SEC ปกติ (Single Error Correct) แต่ไม่พอสำหรับ SEC-DED (ต้องการบิต Over-Parity เพิ่มอีก 1 บิตเพื่อดักจับ 2-bit error)
* ข้อ C และ D มีการคำนวณจำนวนบิตผิดพลาดตามทฤษฎีสารสนเทศ

---

### คำถามที่ 3: การประเมิน Latency ในวงจรแคชความเร็วสูง: Distributed RAM vs BRAM (Cache Tag Lookup Latency & Timing Slack)
ในหน่วยประมวลผลความเร็วสูง RISC-V บน FPGA วงจรแคช L1 Tag Lookup ต้องทำการเปรียบเทียบแอดเดรสและส่งสัญญาณแคชฮิต (Cache Hit Strobe) กลับมาตัดสินใจ:
* ความถี่สัญญาณนาฬิกา: $F_{clk} = 250.0\text{ MHz} \implies T_{clk} = 4.000\text{ ns}$
* ความล่าช้าของวงจรเปรียบเทียบและลอจิกควบคุม Hit: $t_{comp\_logic} = 1.650\text{ ns}$
* Setup time ของรีจิสเตอร์ปลายทาง: $t_{setup} = 0.150\text{ ns}$
* Routing delay รวม: $t_{net} = 0.800\text{ ns}$

เปรียบเทียบการจัดเก็บ Tag Memory ขนาด $64\text{ คำ} \times 24\text{ บิต}$:
* **กรณีที่ 1 (ใช้ BRAM36 ในโหมด Unregistered `DOA_REG = 0`):**
  * มี Clock-to-Out delay: $T_{bcko} = 2.400\text{ ns}$
  * ข้อมูลจะถูกอ่านออกมาในรอบสัญญาณนาฬิกาถัดไป (Read Latency = $1\text{ cycle}$)
* **กรณีที่ 2 (ใช้ Distributed RAM ในโหมด Asynchronous Read):**
  * เมื่อแอดเดรสมาถึง สัญญาณจะวิ่งทะลุผ่าน LUT RAM ทันทีแบบ Combinational:
    $$t_{lutram\_access} = 0.650\text{ ns}$$
  * สามารถอ่านและเปรียบเทียบผลได้เสร็จสิ้นภายใน **รอบสัญญาณนาฬิกาเดียวกัน (0-cycle Latency)**

จงคำนวณหา:
1. เวลาหน่วงรวมของพาธในรอบเดียวกันสำหรับกรณีที่ 2 ($T_{path2}$) และวิเคราะห์ว่าผ่าน Timing หรือไม่
2. ข้อได้เปรียบด้านจำนวนรอบ Latency ในการรู้ผล Cache Hit ของกรณีที่ 2 เทียบกับกรณีที่ 1:

A) $T_{path2} = 3.250\text{ ns}$ (ผ่านเกณฑ์, Slack $+0.750\text{ ns}$); \quad กรณี 2 เร็วกว่ากรณี 1 อยู่ $1\text{ Clock Cycle}$  
B) $T_{path2} = 4.850\text{ ns}$ (ไม่ผ่านเกณฑ์); \quad กรณี 2 เร็วกว่ากรณี 1 อยู่ $2\text{ Cycles}$  
C) $T_{path2} = 3.250\text{ ns}$ (ผ่านเกณฑ์); \quad ทั้งสองกรณีใช้เวลาจำนวนรอบเท่ากัน  
D) $T_{path2} = 2.450\text{ ns}$ (ผ่านเกณฑ์); \quad กรณี 2 เร็วกว่ากรณี 1 อยู่ $1\text{ Clock Cycle}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณความล่าช้ารวมในรอบเดียวกันสำหรับกรณีที่ 2 (Distributed RAM)**
ในกรณีที่ 2 แอดเดรสวิ่งเข้า Distributed RAM แล้วทะลุเข้าสู่วงจร Comparator ทันที:
$$T_{path2} = t_{lutram\_access} + t_{comp\_logic} + t_{net} + t_{setup}$$
แทนค่าตัวแปร:
$$T_{path2} = 0.650\text{ ns} + 1.650\text{ ns} + 0.800\text{ ns} + 0.150\text{ ns} = 3.250\text{ ns}$$
คำนวณ Setup Slack ที่คาบเวลา $T_{clk} = 4.000\text{ ns}$:
$$t_{slack} = T_{clk} - T_{path2} = 4.000\text{ ns} - 3.250\text{ ns} = +0.750\text{ ns} = +750\text{ ps}$$
*(มีค่าเป็นบวก ปิด Timing Closure ผ่านอย่างปลอดภัยภายใน 1 รอบสัญญาณนาฬิกา!)*

**ขั้นตอนที่ 2: วิเคราะห์ความได้เปรียบด้าน Latency**
* **กรณีที่ 1 (BRAM):** ต้องใช้ $1$ ไซเคิลเพื่ออ่าน Tag ออกมา จากนั้นต้องใช้ไซเคิลที่ $2$ ในการรัน Comparator รวมเป็น **$2\text{ Clock Cycles}$** ก่อนที่ CPU จะรู้ผลว่า Hit หรือ Miss
* **กรณีที่ 2 (Distributed RAM):** อ่าน Tag และรัน Comparator จบในไซเคิลแรกทันที (**$1\text{ Clock Cycle}$**)
* ดังนั้นกรณีที่ 2 **เร็วกว่ากรณีที่ 1 อยู่ $1\text{ Clock Cycle}$ เต็มๆ** ซึ่งเพิ่มคะแนน IPC (Instructions Per Cycle) ของซีพียูได้อย่างมหาศาล!

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($T_{path2} = 3.250\text{ ns}$, ผ่านเกณฑ์, Slack $+0.750\text{ ns}$; กรณี 2 เร็วกว่าอยู่ $1\text{ Clock Cycle}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะนำ $T_{bcko}$ ของ BRAM มารวมกับ Distributed RAM
* ข้อ C ผิด เพราะไม่เข้าใจว่า Asynchronous Read ช่วยลด Latency ลง 1 ไซเคิล
* ข้อ D ลืมรวมค่าความล่าช้าของสายส่ง $t_{net}$
