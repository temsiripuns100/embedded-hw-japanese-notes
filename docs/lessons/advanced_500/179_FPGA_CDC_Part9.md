# Lesson 179: FPGA CDC Part 9 - Reset Domain Crossing (RDC) & Power-Down Sequencing (Reset Glitch Hazards, Reset Domain Isolation, Power-On Reset & Dynamic Domain Power-Gating)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์ Reset Domain Crossing (RDC) คืออะไร?
ในหมู่วิศวกรออกแบบวงจรดิจิทัล ความเข้าใจส่วนใหญ่เกี่ยวกับปัญหา Metastability มักจำกัดอยู่เพียงเรื่องของ **Clock Domain Crossing (CDC)** คือการที่สัญญาณวิ่งข้ามระหว่างโดเมนที่มีสัญญาณนาฬิกาต่างกัน

ทว่า ในสถาปัตยกรรม System-on-Chip (SoC) และ FPGA ประสิทธิภาพสูงยุคปัจจุบัน ยังมีภัยเงียบอีกรูปแบบหนึ่งที่ร้ายแรงไม่แพ้กัน และ **เกิดขึ้นแม้ในวงจรที่ใช้สัญญาณนาฬิกาตัวเดียวกันทุกประการ ($f_{src} = f_{dst}$ และ Phase ตรงกัน $100\%$)** ภัยเงียบนี้เรียกว่า **Reset Domain Crossing (RDC - リセットドメイン・クロッシング)**:

```
               สถาปัตยกรรมวิกฤตของ RESET DOMAIN CROSSING (RDC)
               
    [ DOMAIN 1: PERIPHERAL IP ]                   [ DOMAIN 2: CORE PROCESSOR ]
    (ได้รับคำสั่ง Warm Reset อิสระ)                (กำลังประมวลผลข้อมูลสำคัญต่อเนื่อง)
    
       CLK (100MHz) ─────────────┬───────────────────────────┐ (สัญญาณนาฬิกาเดียวกัน!)
                                 │                           │
                               ┌─┴─┐                       ┌─┴─┐
                 D ───────────┤   │                       │   ├─────────── Q_core
                               │ D │                       │ D │
    rst_periph_n ──┐           │   ├── data_bus ───────────┤   │
                   ▼           └───┘ (เกิด RDC Glitch!)    └───┘
               (RESET ทันที       ▲                           ▲
                กลางไซเคิล!)      │                           │
                               [FF_A]                      [FF_B]
                                                             ▲
                                                rst_core_n ──┘ (ยังคง = 1 ไม่ถูกรีเซ็ต)
```

#### นิยามเชิงฟิสิกส์ของ RDC Hazard (Reset-Induced Metastability):
สมมติว่าฟลิปฟล็อป $FF_A$ และ $FF_B$ ทำงานด้วยสัญญาณนาฬิกา `CLK` เดียวกัน ($100\text{ MHz}$, $T = 10.0\text{ ns}$) โดยไม่มีปัญหา Clock Skew:
1. $FF_A$ ควบคุมโดยสัญญาณรีเซ็ตเฉพาะส่วน `rst_periph_n`
2. $FF_B$ ควบคุมโดยสัญญาณรีเซ็ตของระบบหลัก `rst_core_n`
3. ในขณะที่ระบบกำลังทำงานปกติ ขาเอาต์พุตของ $FF_A$ กำลังส่งข้อมูลลอจิก `1` ไปยังขา D ของ $FF_B$
4. ซอฟต์แวร์หรือวงจร Supervisor สั่งทำ **Warm Reset เฉพาะกิจ (Independent Asynchronous Reset)** เข้ามายัง `rst_periph_n` โดยสัญญาณนี้ถูกสั่งทำงานในเวลาใดก็ได้ (Asynchronous in Nature)

```
                       กลไกการเกิด GLITCH จาก ASYNCHRONOUS RESET
                       
    CLK          : ──────/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾‾‾
                                               ▲
                                        (Sampling Edge ของ FF_B)
                                         ├─────┤ (Setup/Hold Window)
    rst_periph_n : ─────────────\____________________________________ (Assert กลางคัน!)
                                 ▲
    data_bus (Q) : ══════════════\___________________________________ (ถูกบังคับดึงลง 0 ทันที!)
                                         ▲
                                 (ตกตรงขอบ CLK พอดิบพอดี!)
    ===> ผลลัพธ์: FF_B เกิดการละเมิด Setup Time / Hold Time ทันที!
         เอาต์พุต Q_core กลายเป็น METASTABLE แม้จะอยู่บน Clock เดียวกัน 100%!
```

> [!CAUTION]
> **ทำไมเครื่องมือ Static Timing Analysis (STA) และ Static CDC จึงมองไม่เห็น RDC?**
> * **STA ตาบอด:** เพราะ STA ตรวจสอบเฉพาะ Synchronous Setup/Hold paths โดยมองว่าสัญญาณรีเซ็ตเป็น Static Control Line หรือถูกตัดด้วยคำสั่ง False Path
> * **CDC Checker ตาบอด:** เพราะเครื่องมือ CDC ตรวจสอบเฉพาะจุดตัดระหว่าง **สัญญาณนาฬิกาต่างโดเมน** เมื่อสัญญาณนาฬิกาต้นทางและปลายทางเป็น `CLK` ตัวเดียวกัน เครื่องมือ CDC จะสรุปว่าเป็น "Synchronous Intra-Clock Path" และปล่อยผ่านทันที!

---

### 1.2 สมการหน้าต่างความเสี่ยงของ RDC (RDC Metastability Risk Window)

ความน่าจะเป็นที่การสั่ง Asynchronous Reset 1 ครั้ง จะทำให้ฟลิปฟล็อปในโดเมนอื่นที่ยังทำงานอยู่เกิดสภาวะ Metastable คำนวณได้จากอัตราส่วนของหน้าต่าง Setup/Hold ต่อคาบสัญญาณนาฬิกา:

$$P_{RDC\_hit} = \frac{T_{setup} + T_{hold}}{T_{clk}}$$

สมมติว่าในระบบ $f_{clk} = 250\text{ MHz}$ ($T_{clk} = 4.0\text{ ns}$):
* $T_{setup} = 0.15\text{ ns}$
* $T_{hold} = 0.10\text{ ns}$
$$P_{RDC\_hit} = \frac{0.15 + 0.10}{4.0} = \frac{0.25\text{ ns}}{4.0\text{ ns}} = 0.0625 \quad (6.25\%)$$

ทุกครั้งที่มีการกดปุ่ม Reset โดเมนย่อย หรือสั่งซอฟต์แวร์ Warm Reset จะมีโอกาสสูงถึง **$6.25\%$** ที่คอร์หลักของระบบจะติดสภาวะ Metastable และเกิด Data Corruption หรือค้างสนิททันที!

---

### 1.3 สถาปัตยกรรม Reset Domain Isolation (RDC Isolation Gate)

เพื่อป้องกันไม่ให้ Glitch จากการรีเซ็ตของโดเมนหนึ่งรั่วไหลเข้าไปทำลายโดเมนอื่น สถาปัตยกรรมระดับ Senior Engineer กำหนดให้ต้องติดตั้ง **Reset Domain Isolation Logic (วงจรแยกโดเมนรีเซ็ต)** ขวางกั้นทุกเส้นทางของสัญญาณที่เชื่อมต่อระหว่างโดเมน:

```
               สถาปัตยกรรม RESET DOMAIN ISOLATION CIRCUIT
               
      [ RESET DOMAIN A (TX) ]                     [ RESET DOMAIN B (RX) ]
      (สามารถถูก Reset ได้อิสระ)                   (ทำงานต่อเนื่อง ปลอดภัย 100%)
      
                      ┌──────────────────────┐
                      │    ISOLATION CELL    │
                      │                      │
      data_tx ────────┤ Data_In              │
                      │                      ├──── data_rx_safe ────► [ FF_RX ]
      iso_enable ─────┤ ISO_EN (Clamp Control│                        (CLK เดียวกัน)
                      │ (AND / OR Gate)      │
                      └──────────────────────┘
                                 ▲
                                 │
                      ┌──────────┴───────────┐
                      │ RESET & ISO SEQUENCER│
                      │ (ลำดับขั้นตอนตัดต่อ) │
                      └──────────────────────┘
```

#### ชนิดของ Isolation Cells (การเลือกตามระดับลอจิกที่ปลอดภัย):
1. **Low-Clamping Isolation (AND-Gate Based):** เมื่อเปิด Isolation สัญญาณเอาต์พุตจะถูกตรึงไว้ที่ลอจิก `0` เสมอ (เหมาะสำหรับสัญญาณ Data Bus, Valid Strobe, หรือ Active-High Signals):
   $$\text{data\_safe} = \text{data\_tx} \ \& \ (\sim\text{iso\_enable})$$
2. **High-Clamping Isolation (OR-Gate Based):** เมื่อเปิด Isolation สัญญาณจะถูกดึงขึ้นลอจิก `1` เสมอ (เหมาะสำหรับสัญญาณ Active-Low Control, Ready Signals, หรือ I2C/SPI Pull-up Lines):
   $$\text{data\_safe} = \text{data\_tx} \ | \ \text{iso\_enable}$$

---

### 1.4 โพรโทคอลลำดับเวลาการตัดต่อโดเมน (Power-Down & Reset Sequencing Protocol)

การสั่งรีเซ็ตโดเมนย่อยต้องดำเนินไปตามลำดับเวลา 6 ขั้นตอนอย่างเคร่งครัด (Strict Handshake Sequencing):

```
             ลำดับเวลามาตรฐาน 6 ขั้นตอนของ RDC RESET SEQUENCING
             
    Normal Operation ──► Step 1: Quiesce Traffic (หยุดธุรกรรม)
                     ──► Step 2: Assert Isolation (เปิดเกตตัดสัญญาณ: ISO_EN = 1)
                     ──► Step 3: Assert Reset (สั่งรีเซ็ตโดเมน A: RST_A = 1)
                     ──► Step 4: Deassert Reset (ปลดรีเซ็ตโดเมน A พร้อม AASD)
                     ──► Step 5: Deassert Isolation (ปลดเกตตัดสัญญาณ: ISO_EN = 0)
                     ──► Step 6: Resume Traffic (เปิดให้ส่งข้อมูลตามปกติ)
```

```
                        TIMING DIAGRAM OF SAFE RDC RESET
                        
    Traffic Active : ‾‾‾‾‾‾‾‾‾‾\_______________________________________/‾‾‾‾‾‾‾‾‾‾
                               ▲ Step 1: หยุดส่งข้อมูล
    iso_enable     : ____________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\________________
                                 ▲ Step 2: ตรึงสายส่ง    ▲ Step 5: ปลด Isolation
    rst_domain_a_n : ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\__________________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
                                     ▲ Step 3: รีเซ็ต   ▲ Step 4: ปลดรีเซ็ต
    data_rx_safe   : ════════════════< CLAMPED TO 0 >══════════════════< DATA >═══
                     (ปลอดภัย 100%: ไม่มี Glitch ใดๆ หลุดข้ามไปยังโดเมน B เลย!)
```

---

### 1.5 โค้ดแม่แบบภาษา Verilog สำหรับ RDC Sequencer และ Isolation Logic

```verilog
// ==============================================================================
// RESET DOMAIN ISOLATION & SEQUENCER CONTROLLER
// Senior Gold Standard: Glitch-free Domain Reset & Power-Down Sequencing
// ==============================================================================
(* keep_hierarchy = "yes" *)
module rdc_safe_subsystem (
    input  wire        clk,
    input  wire        sys_rst_n,
    
    // Command from Processor
    input  wire        req_warm_reset,
    output reg         reset_busy,
    
    // Domain A (Subsystem being reset)
    output wire        rst_subsystem_a_n,
    
    // Interface Data between Domains
    input  wire [31:0] data_from_subsystem_a,
    output wire [31:0] data_to_core_safe
);

    // -------------------------------------------------------------------------
    // 1. Reset Sequencing FSM
    // -------------------------------------------------------------------------
    localparam [2:0] S_NORMAL      = 3'b000,
                     S_QUIESCE     = 3'b001,
                     S_ASSERT_ISO  = 3'b010,
                     S_ASSERT_RST  = 3'b011,
                     S_DEASSERT_RST= 3'b100,
                     S_RELEASE_ISO = 3'b101;

    reg [2:0] state;
    reg [7:0] timer;
    reg       iso_enable;
    reg       subsystem_a_rst_n_raw;

    always @(posedge clk or negedge sys_rst_n) begin
        if (!sys_rst_n) begin
            state                 <= S_NORMAL;
            timer                 <= 8'd0;
            iso_enable            <= 1'b0;
            subsystem_a_rst_n_raw <= 1'b1;
            reset_busy            <= 1'b0;
        end else begin
            case (state)
                S_NORMAL: begin
                    iso_enable            <= 1'b0;
                    subsystem_a_rst_n_raw <= 1'b1;
                    if (req_warm_reset) begin
                        reset_busy <= 1'b1;
                        state      <= S_QUIESCE;
                        timer      <= 8'd16; // หน่วงเวลารอให้ธุรกรรมค้างท่อจบลง
                    end else begin
                        reset_busy <= 1'b0;
                    end
                end

                S_QUIESCE: begin
                    if (timer > 0)
                        timer <= timer - 1'b1;
                    else begin
                        state      <= S_ASSERT_ISO;
                        iso_enable <= 1'b1; // เปิดเกต Isolation ตรึงค่าทันที
                        timer      <= 8'd4;
                    end
                end

                S_ASSERT_ISO: begin
                    if (timer > 0)
                        timer <= timer - 1'b1;
                    else begin
                        state                 <= S_ASSERT_RST;
                        subsystem_a_rst_n_raw <= 1'b0; // ยิงคำสั่ง Reset
                        timer                 <= 8'd32; // คงสถานะ Reset ไว้ 32 ไซเคิล
                    end
                end

                S_ASSERT_RST: begin
                    if (timer > 0)
                        timer <= timer - 1'b1;
                    else begin
                        state                 <= S_DEASSERT_RST;
                        subsystem_a_rst_n_raw <= 1'b1; // ปลดรีเซ็ต
                        timer                 <= 8'd16; // รอให้ AASD และ PLL นิ่ง
                    end
                end

                S_DEASSERT_RST: begin
                    if (timer > 0)
                        timer <= timer - 1'b1;
                    else begin
                        state      <= S_RELEASE_ISO;
                        iso_enable <= 1'b0; // ปลด Isolation ให้สัญญาณไหลผ่าน
                        timer      <= 8'd4;
                    end
                end

                S_RELEASE_ISO: begin
                    if (timer > 0)
                        timer <= timer - 1'b1;
                    else begin
                        state      <= S_NORMAL;
                        reset_busy <= 1'b0;
                    end
                end

                default: state <= S_NORMAL;
            endcase
        end
    end

    // -------------------------------------------------------------------------
    // 2. Synchronous Reset Deassertion (AASD) for Subsystem A
    // -------------------------------------------------------------------------
    (* ASYNC_REG = "TRUE" *) reg rst_sync1, rst_sync2;
    always @(posedge clk or negedge subsystem_a_rst_n_raw) begin
        if (!subsystem_a_rst_n_raw) begin
            rst_sync1 <= 1'b0;
            rst_sync2 <= 1'b0;
        end else begin
            rst_sync1 <= 1'b1;
            rst_sync2 <= rst_sync1;
        end
    end
    assign rst_subsystem_a_n = rst_sync2;

    // -------------------------------------------------------------------------
    // 3. Glitch-Free Isolation Cell Implementation (AND-Clamping)
    // -------------------------------------------------------------------------
    genvar i;
    generate
        for (i = 0; i < 32; i = i + 1) begin : gen_isolation
            assign data_to_core_safe[i] = data_from_subsystem_a[i] & (~iso_enable);
        end
    endgenerate

endmodule
```

---

### 1.6 เครื่องมือตรวจสอบ Static RDC Verification (SpyGlass RDC / Questa RDC)

เนื่องจากเครื่องมือ CDC ทั่วไปไม่สามารถตรวจจับปัญหานี้ได้ ผู้ผลิตซอฟต์แวร์ EDA ชั้นนำจึงได้พัฒนาเครื่องมือตรวจสอบ RDC โดยเฉพาะ:
* **Synopsys SpyGlass RDC:** ตรวจจับพาธที่ขาด Isolation Cell ผ่านกฎ `RDC_No_Iso`, `RDC_Glitch_Data`, `RDC_Reset_Cycle`
* **Siemens Questa RDC:** ตรวจจับเส้นทางข้ามโดเมนรีเซ็ตและสร้าง Verification Matrix วิเคราะห์สภาวะอิสระของ Reset Tree
* **กฎทองคำของ RDC Sign-Off:** *ทุกเส้นทางของสัญญาณที่เชื่อมต่อระหว่างสอง Register ที่ใช้สัญญาณรีเซ็ตต่างชื่อกัน จะต้องมี Isolation Gate หรือ Handshake Protocol คั่นกลางเสมอ มิฉะนั้นถือว่าไม่ผ่านเกณฑ์ส่งมอบชิป!*

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】คอนโทรลเลอร์จัดเก็บข้อมูลความเร็วสูง Enterprise NVMe SSD
เกิดอาการข้อมูลในตาราง Flash Translation Table (FTL) เสียหาย และไดรฟ์ล็อก (Brick)
เมื่อระบบโฮสต์สั่งทำ PCIe Warm Reset ในขณะที่ SSD กำลังทำ Background Garbage Collection
================================================================================
```

#### บริบทของระบบ (System Context):
บริษัทผู้ผลิตอุปกรณ์จัดเก็บข้อมูล Data Center พัฒนาคอนโทรลเลอร์ Enterprise NVMe SSD ระดับ Gen4 บน FPGA Xilinx UltraScale+ (`xcku15p`):
* ทั้งชิปทำงานบนสัญญาณนาฬิกาแกนหลักเดียวกัน: `clk_core = 250.00 MHz` ($T = 4.0\text{ ns}$) จาก MMCM ตัวเดียวกัน
* **PCIe Endpoint Subsystem:** มีวงจรรีเซ็ตแยกต่างหาก `rst_pcie_n` เพื่อรองรับคำสั่ง Hot-Reset / Warm-Reset จากระบบปฏิบัติการของเซิร์ฟเวอร์
* **Flash Translation Layer (FTL) & DRAM Controller:** ควบคุมโดย `rst_sys_n` ซึ่งต้องทำงานต่อเนื่องเพื่อคอยจัดเรียงบล็อกข้อมูล NAND Flash (Garbage Collection & Wear Leveling) แม้ในยามที่การเชื่อมต่อ PCIe หลุดชั่วคราว
* มีบัสสถานะ `pcie_rx_status[31:0]` ส่งตรงจาก PCIe Controller ไปยัง FTL Engine บนความถี่ $250\text{ MHz}$ เดียวกันโดยไม่มี Isolation

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
เมื่อนำ SSD ไปทดสอบในเซิร์ฟเวอร์คลาวด์ที่มีการรีบูตโฮสต์แบบสุ่ม (Hot-Reboot Stress Test): หลังจากรันไปได้ประมาณ 40,000 รอบ SSD เกิดอาการ **ไดรฟ์ล็อกสนิท (Drive Bricked / Fatal Panic)** ไม่ตอบสนองต่อคำสั่งใดๆ ข้อมูลตารางแมปปิ้งหน่วยความจำ (FTL Mapping Table) ใน DRAM เสียหายจนกู้คืนไม่ได้ ข้อมูลของลูกค้าสูญหายอย่างถาวร!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมข้อมูลตาราง FTL ในหน่วยความจำ DRAM จึงเสียหาย?**
   * *เพราะเอนจิน FTL มีการเขียนข้อมูลขยะทับลงในหน่วยความจำตารางแอดเดรสของแฟลช*
2. **ทำไมเอนจิน FTL จึงเขียนข้อมูลขยะทับลงในตาราง?**
   * *เพราะสเตตแมชชีนภายใน FTL กระโดดข้ามสถานะ (FSM Invalid State Jump) ไปสู่ขั้นตอน Flush Table ด้วยพอยน์เตอร์ที่เป็นศูนย์*
3. **ทำไมสเตตแมชชีน FTL จึงกระโดดข้ามสถานะผิดพลาด?**
   * *เพราะฟลิปฟล็อปที่รับสัญญาณ `pcie_rx_status[31:0]` ในโดเมน FTL เกิดสภาวะ Metastable ในจังหวะที่เซิร์ฟเวอร์สั่งรีเซ็ต PCIe*
4. **ทำไมจึงเกิด Metastability ทั้งที่ทั้งสองโมดูลใช้สัญญาณนาฬิกา 250 MHz เดียวกัน?**
   * *เพราะเกิดสภาวะ Reset Domain Crossing (RDC) โดยสัญญาณรีเซ็ตของ PCIe (`rst_pcie_n`) ถูกยิงเข้ามาแบบ Asynchronous กลางรอบสัญญาณนาฬิกา ทำให้สายส่งสถานะตกลงสู่ศูนย์ทันทีและละเมิด Setup Time ของฟลิปฟล็อปในฝั่ง FTL*
5. **ทำไมทีมวิศวกรจึงไม่ติดตั้งวงจร Isolation Gate และไม่พบข้อผิดพลาดนี้ในขั้นตอนตรวจแบบ?**
   * *เพราะวิศวกรเข้าใจว่าปัญหา Metastability เกิดขึ้นเฉพาะเมื่อ Clock ต่างความถี่กันเท่านั้น เมื่อเห็นว่าทั้งสองบล็อกใช้ `clk_core` เดียวกัน จึงคิดว่าเป็น Synchronous Design ที่ปลอดภัย 100% และเครื่องมือ Static CDC ทั่วไปไม่ได้แจ้งเตือนข้อผิดพลาดนี้เลย!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                          สาเหตุของความล้มเหลว: FTL CORRUPTION & SSD BRICK
                          
   METHOD (สถาปัตยกรรมรีเซ็ต)                  MACHINE (ฟิสิกส์ซิลิคอนและการเดินสาย)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ปล่อย RDC ข้ามโดยไม่มี Isolation│          │ Asynchronous Reset กลางรอบ CLK │
   │ ขาดการจัดลำดับ Quiesce Protocol │          │ การละเมิด Setup Time บน 250MHz │
   │ คิดว่า Clock เดียวกันปลอดภัย 100%│        │ FSM Metastable & Illegal Jump  │
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ใช้เฉพาะเครื่องมือ CDC ไม่รัน RDC│         │ Testbench ไม่เคยยิง PCIe Reset │
   │ ขาด SVA RDC Stability Checks   │          │ ในขณะที่ FTL กำลัง Flush Table │
   │ ขาดการรีวิวคู่มือ RDC Standards│          │ Zero-Delay Sim ซ่อน RDC Glitch │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (เครื่องมือและข้อกำหนด)             MEASUREMENT (สภาวะการทดสอบระบบ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediations):
1. **ติดตั้ง Isolation Cell Gate:** นำสายสัญญาณทั้งหมดที่ข้ามจาก PCIe Subsystem มายัง FTL ผ่านวงจร AND-Clamping Isolation Cell
2. **สร้าง Hardware RDC Sequencer FSM:**
   * เมื่อมีคำสั่ง PCIe Warm Reset เข้ามา Sequencer จะต้องสั่ง Pause FTL Interface และเปิด `iso_enable = 1` ให้เสร็จก่อนอย่างน้อย 4 ไซเคิล
   * จากนั้นจึงยิง Asynchronous Assert ไปที่ PCIe
   * เมื่อปลดรีเซ็ตเสร็จและผ่านวงจร AASD สมบูรณ์แล้ว จึงค่อยปลด `iso_enable = 0`
3. **นำเครื่องมือ Questa RDC หรือ SpyGlass RDC มาใช้ใน Flow การตรวจสอบ:** ตรวจจับและยืนยันว่าไม่มี Un-isolated RDC Paths หลงเหลืออยู่ในโปรเจกต์แม้แต่เส้นทางเดียว

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Reset Domain Crossing (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | มีสัญญาณเชื่อมต่อระหว่างโมดูลที่ใช้สัญญาณ Reset คนละตัวกันหรือไม่? | ตรวจสอบ Reset Netlist | [ ] ผ่าน |
| 2 | หากมี RDC ได้มีการติดตั้ง Isolation Cell (AND/OR Gate) ครบทุกเส้นทาง? | $100\%$ Isolation Coverage | [ ] ผ่าน |
| 3 | มีวงจรควบคุมลำดับเวลา (Sequencer) ทำการ Quiesce และ Clamping ก่อน Reset? | Verified Sequence Protocol | [ ] ผ่าน |
| 4 | มีการใช้ Reset Bridge (AASD) บนสัญญาณรีเซ็ตของแต่ละโดเมนอิสระหรือไม่? | Synchronous Deassert | [ ] ผ่าน |
| 5 | มีการรันเครื่องมือ Static RDC Verification (Questa RDC / SpyGlass RDC)? | Zero RDC Violations | [ ] ผ่าน |
| 6 | เขียน SVA Assertion พิสูจน์ว่าไม่มี Glitch หลุดข้ามในระหว่าง Reset Cycle? | Formal Proof Passed | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | リセットドメイン・クロッシング | リセットドメイン・クロッシング | Risetto domein kurosshingu | Reset Domain Crossing (RDC) |
| 2 | リセット起因メタステーブル | リセットきいんメタステーブル | Risetto kiin metastēburu | Reset-Induced Metastability |
| 3 | アイソレーション・ゲート | アイソレーション・ゲート | Aisorēshon gēto | Isolation Gate / Isolation Cell |
| 4 | クワイエス制御 / 静止化 | クワイエスせいぎょ / せいしか | Kuwaiesu seigyo / Seishika | Quiesce Control / Traffic Halting |
| 5 | 独立ウォームリセット | どくりつウォームリセット | Dokuritsu wōmu risetto | Independent Warm Reset |
| 6 | 同一クロック非同期リセット | どういつクロックひどうきリセット | Dōitsu kurokku hidōki risetto | Same-Clock Asynchronous Reset |
| 7 | 固定値クランプ | こていちクランプ | Koteichi kuranpu | Clamping to Fixed Value (0 or 1) |
| 8 | 復帰シーケンス不全 | ふっきシーケンスふぜん | Fukki shīkensu fuzen | Power-up / Recovery Sequence Failure |
| 9 | 潜在的ハザード | せんざいてきハザード | Senzaiteki hazādo | Latent Hazard / Silent Defect |
| 10 | 領域分離検証 | りょういきぶんりけんしょう | Ryōiki bunri kenshō | Domain Isolation Verification |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ห้องปฏิบัติการพัฒนาคอนโทรลเลอร์จัดเก็บข้อมูลศูนย์ข้อมูล (Enterprise Storage Controller Lab), เมืองโยโกฮาม่า (Yokohama)  
**ผู้เข้าร่วม:**
* **โอคาดะกิโช (Okada-Gichou):** หัวหน้าวิศวกรผู้เชี่ยวชาญด้านสถาปัตยกรรมระบบความปลอดภัยสูง (Chief Storage Architect / 統括技監)
* **ธีรภัทร์ (Teeraphat):** วิศวกรออกแบบระบบ FPGA Controller (FPGA Core Designer)

---

**岡田技監 (Okada):**  
「ティーラパット君、このNVMe SSDコントローラのトップレベル結線図とリセット系統樹を確認したよ。PCIeサブシステムとFTL管理ブロックは、どちらも同一の250MHzクロックで動作しているね。しかし、PCIe側にはホストからの独立ウォームリセット信号`rst_pcie_n`が直接入っており、FTLブロックとの間のステータスバス32ビットには**アイソレーション回路（Isolation Cell）**が一切挟まれていない。この設計で、ホストがPCIeを突然リセットした時の挙動はどうなるのかね？」  
*(Tīrapatto-kun, kono NVMe SSD kontorōra no toppureberu kessenzu to risetto keitōju wo kakunin shita yo. PCIe sabushisutemu to FTL kanri burokku wa, dochira mo dōitsu no 250MHz kurokku de dōsa shite iru ne. Shikashi, PCIe-gawa ni wa hosuto kara no dokuritsu wōmu risetto shingō rst_pcie_n ga chokusetsu haitte ori, FTL burokku to no aida no sutētasu basu 32-bit ni wa aisorēshon kairo ga issai hasamarete inai. Kono sekkei de, hosuto ga PCIe wo totsuzen risetto shita toki no kyodō wa dō naru no kane?)*  
**คำแปล:** คุณธีรภัทร์ ผมได้ตรวจผังการเชื่อมต่อวงจรระดับบนสุดและแผนผังระบบรีเซ็ตของ SSD คอนโทรลเลอร์ตัวนี้แล้ว ทั้งบล็อก PCIe และบล็อก FTL ทำงานด้วยสัญญาณนาฬิกา $250\text{ MHz}$ เดียวกันสินะ แต่ฝั่ง PCIe มีสัญญาณรีเซ็ตอิสระ `rst_pcie_n` จากโฮสต์ต่อเข้ามาตรงๆ และบนบัสสถานะขนาด 32 บิตที่ต่อไปยังบล็อก FTL กลับไม่มีวงจร Isolation Cell คั่นไว้เลยแม้แต่ตัวเดียว ในการออกแบบนี้ หากโฮสต์สั่งรีเซ็ต PCIe กะทันหัน จะเกิดพฤติกรรมอย่างไรขึ้นหรือครับ?

**ティーラパット (Teeraphat):**  
「岡田技監、両方のブロックは同一のMMCMから供給される完全同期の250MHzクロックで駆動されております。そのため、クロック間の位相差はなく、通常のSTAタイミング検証でもSetupおよびHold解析を完全にパスしておりますので、CDCの問題は発生しないと判断いたしました。」  
*(Okada-gikan, ryōhō no burokku wa dōitsu no MMCM kara kyōkyū sareru kanzen dōki no 250MHz kurokku de kudō sarete orimasu. Sono tame, kurokku-kan no位相差 wa naku, tsūjō no STA taimingu kenshō demo Setup oyobi Hold kaiseki wo kanzen ni pasu shite orimasu node, CDC no mondai wa hassei shinai to handan itashimashita.)*  
**คำแปล:** หัวหน้าโอคาดะครับ ทั้งสองบล็อกทำงานด้วยสัญญาณนาฬิกา $250\text{ MHz}$ ที่ซิงโครไนซ์กันอย่างสมบูรณ์จาก MMCM ตัวเดียวกันครับ จึงไม่มีความต่างของเฟสระหว่างสัญญาณนาฬิกา และในการตรวจ STA Timing ปกติก็ผ่านทั้ง Setup และ Hold ครบถ้วน ผมจึงตัดสินว่าไม่มีปัญหาเรื่อง CDC ครับ

**岡田技監 (Okada):**  
「それがまさに、多くの技術者が嵌る**『RDC（リセットドメイン・クロッシング）の盲点』**だよ！CDCがないからといって、メタステーブルが起きないわけではない！ホストからの非同期リセットがサイクルの中途でアサートされた瞬間、PCIe側のレジスタ出力はクロックエッジを待たずに強制的にゼロへ叩き落とされる。そのデータ遷移が、稼働中のFTL側レジスタのSetup/Hold時間に突き刺さるんだ！250MHzなら1サイクルのうち6%以上の確率でFTLがメタステーブル化し、最悪の場合フラッシュ変換テーブルが不正値で上書きされてSSDが文鎮化（Brick）するぞ！」  
*(Sore ga masa ni, ōku no gijutsusha ga hamaru "RDC no mōten" da yo! CDC ga nai kara to itte, metastēburu ga okinai wake dewa nai! Hosuto kara no hidōki risetto ga saikuru no chūto de asāto sareta shunkan, PCIe-gawa no rejisuta shutsuryoku wa kurokku ejji wo matazu ni kyōseitēki ni zero e tataki-otosareru. Sono dēta sen'i ga, kadō-chū no FTL-gawa rejisuta no Setup/Hold jikan ni tsukisasaru n da! 250MHz nara 1-saikuru no uchi 6% ijō no kakuritsu de FTL ga metastēburu-ka shi, saiaku no baai furasshu henkan tēburu ga fuseichi de uwagaki sarete SSD ga bunchin-ka suru zo!)*  
**คำแปล:** นั่นแหละคือ **"จุดบอดของ RDC (Reset Domain Crossing)"** ที่วิศวกรจำนวนมากตกม้าตายล่ะ! การที่ไม่มีปัญหา CDC ไม่ได้แปลว่าจะไม่เกิด Metastability เสียหน่อย! วินาทีที่ Asynchronous Reset จากโฮสต์ทำงานขึ้นมากลางไซเคิล เอาต์พุตของรีจิสเตอร์ฝั่ง PCIe จะถูกกระชากลงสู่ศูนย์ทันทีโดยไม่รอขอบสัญญาณนาฬิกา และขอบสัญญาณนั้นจะพุ่งเสียบเข้าหน้าต่าง Setup/Hold Time ของรีจิสเตอร์ฝั่ง FTL ที่กำลังทำงานอยู่พอดี! ที่ความถี่ $250\text{ MHz}$ จะมีโอกาสเกิด Metastability สูงกว่า $6\%$ ในทุกๆ ครั้งที่รีเซ็ต และกรณีเลวร้ายที่สุด ตาราง FTL จะถูกเขียนทับด้วยข้อมูลขยะจน SSD กลายเป็นที่ทับกระดาษ (Bricked) ไปเลยนะ!

**ティーラパット (Teeraphat):**  
「ハッ……！同一クロックであっても、非同期リセットによってデータパス上にグリッチが発生し、それがサンプリングエッジと衝突すればメタステーブルを引き起こす……！完全に盲点でした！」  
*(Ha'... Dōitsu kurokku de attemo, hidōki risetto ni yotte dētapasu-jō ni guricchi ga hassei shi, sore ga sanpuringu ejji to shōtotsu sureba metastēburu wo hikiokosu...! Kanzen ni mōten deshita!)*  
**คำแปล:** อ๊ะ...! ต่อให้เป็น Clock เดียวกัน แต่ถ้า Asynchronous Reset สร้าง Glitch ขึ้นบน Datapath แล้วไปชนกับ Sampling Edge มันก็ทำให้เกิด Metastability ได้เหมือนกัน...! เป็นจุดบอดที่ผมมองข้ามไปอย่างสิ้นเชิงเลยครับ!

**岡田技監 (Okada):**  
「そうだ。直ちにリセットシーケンサを組み込みなさい。ホストからのリセット要求を検知したら、まずFTLへのトラフィックを静止化（Quiesce）し、次にアイソレーションゲートを有効化して信号線を安全値にクランプする。その後に初めてPCIeのリセットを実行し、復帰後にアイソレーションを解除するという6段階のシーケンスを徹底すること。Questa RDCによる検証ログを添えて再提出したまえ。」  
*(Sō da. Tadachini risetto shīkensa wo kumikominasai. Hosuto kara no risetto yōkyū wo kenchi shitara, mazu FTL e no torafikku wo seishika shi, tsugi ni aisorēshon gēto wo yūkōka shite shingōsen wo anzenchi ni kuranpu suru. Sono nochi ni hajimete PCIe no risetto wo jikkō shi, fukki-go ni aisorēshon wo kaijo suru to iu roku-dankai no shīkensu wo tettei suru koto. Questa RDC ni yoru kenshō rogu wo soete sai-teishutsu shitamae.)*  
**คำแปล:** ถูกต้อง จงรีบนำ Reset Sequencer มาติดตั้งเดี๋ยวนี้ เมื่อตรวจพบคำสั่ง Reset จากโฮสต์ อันดับแรกต้องสั่งหยุดส่งข้อมูล (Quiesce) ไปยัง FTL ก่อน จากนั้นสั่งเปิด Isolation Gate เพื่อ Clamp สายสัญญาณให้อยู่ในสถานะปลอดภัย แล้วจึงค่อยสั่งรีเซ็ต PCIe เมื่อกู้คืนระบบเสร็จค่อยปลด Isolation ตามขั้นตอน 6 ลำดับนี้อย่างเคร่งครัด แล้วแนบบันทึกผลการตรวจสอบจาก Questa RDC มายื่นตรวจใหม่อีกครั้ง

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การวิเคราะห์ความน่าจะเป็นของ RDC Metastability ในระบบ Synchronous Multi-Core
ในระบบประมวลผลเครือข่ายความเร็วสูง คอร์ประมวลผล $Core_A$ และ $Core_B$ ทำงานบนสัญญาณนาฬิกา $f_{clk} = 400\text{ MHz}$ ($T_{clk} = 2.50\text{ ns}$) จากแหล่งจ่ายเดียวกัน:
* $Core_A$ สามารถถูกสั่ง Asynchronous Reset ผ่านซอฟต์แวร์ Watchdog โดยเฉลี่ยวันละ 100 ครั้ง ($N_{rst} = 100\text{ ครั้ง/วัน}$)
* สัญญาณรีเซ็ตเกิดขึ้นในเวลาสุ่ม (Uniformly Distributed Random Time) เมื่อเทียบกับสัญญาณนาฬิกา
* ข้อกำหนด Timing ของฟลิปฟล็อปปลายทางใน $Core_B$: $T_{setup} = 0.12\text{ ns}$, $T_{hold} = 0.08\text{ ns}$
* เวลาในการคลายตัว (Resolution Time Constant) ของกระบวนการผลิตชิป: $\tau = 0.10\text{ ns}$
* มีสัญญาณบัสสถานะขนาด 16 บิต เชื่อมต่อจาก $Core_A$ ไปยัง $Core_B$ โดยตรงโดยไม่มี Isolation Cell

หากในจังหวะที่เกิด Reset บัสทั้ง 16 บิตมีบิตที่กำลังส่งลอจิก `1` อยู่จำนวน 8 บิต (ซึ่งจะถูกดึงลงเป็น `0` พร้อมกันทันทีเมื่อเกิด Reset) จงคำนวณหาความน่าจะเป็นที่การสั่ง Reset 1 ครั้ง จะทำให้เกิดการละเมิด Setup/Hold บนบิตใดบิตหนึ่ง ($P_{violation}$) และคำนวณหาความถี่ที่ระบบจะเกิดเหตุการณ์นี้ใน 1 ปี (Violations Per Year)

---

#### ตัวเลือก:
* **ก)** $P_{violation} = 8.0\%$, เกิดขึ้นประมาณ 2,920 ครั้งต่อปี
* **ข)** $P_{violation} = 48.0\%$, เกิดขึ้นประมาณ 17,520 ครั้งต่อปี
* **ค)** $P_{violation} \approx 0\%$, ไม่เคยเกิดขึ้นเพราะทำงานบน Clock 400 MHz เดียวกัน
* **ง)** $P_{violation} = 100\%$, เกิดขึ้นทุกครั้งที่กด Reset

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การคำนวณหน้าต่างความเสี่ยงของสัญญาณ 1 บิต ($T_{window}$):
ความกว้างของช่วงเวลาต้องห้ามรอบขอบสัญญาณนาฬิกาคือ:
$$T_{window} = T_{setup} + T_{hold} = 0.12\text{ ns} + 0.08\text{ ns} = 0.20\text{ ns}$$

##### 2. ความน่าจะเป็นที่ Asynchronous Reset จะตกในหน้าต่างความเสี่ยง ($P_{hit}$):
เนื่องจากสัญญาณรีเซ็ตเกิดขึ้นแบบสุ่มอิสระในคาบเวลา $T_{clk} = 2.50\text{ ns}$:
$$P_{hit} = \frac{T_{window}}{T_{clk}} = \frac{0.20\text{ ns}}{2.50\text{ ns}} = 0.080 \quad (8.0\%)$$

##### 3. การประเมินสำหรับบัสข้อมูล:
เนื่องจากทั้ง 8 บิตถูกกระชากลงสู่ลอจิก `0` พร้อมกันด้วยสัญญาณรีเซ็ตตัวเดียวกัน ขอบการเปลี่ยนระดับของทั้ง 8 บิตจึงเกิดขึ้นในจังหวะเวลาเดียวกัน (มีความต่างเพียง Routing Delay เล็กน้อย):
* ความน่าจะเป็นที่สัญญาณรีเซ็ตจะตกลงในหน้าต่างเวลาเสี่ยงของปลายทางคือ $P_{violation} = 8.0\%$ ต่อการกดรีเซ็ต 1 ครั้ง

##### 4. การคำนวณความถี่ของการเกิดเหตุการณ์ใน 1 ปี:
* จำนวนครั้งของการรีเซ็ตต่อวัน: $100\text{ ครั้ง}$
* จำนวนครั้งของการรีเซ็ตใน 1 ปี: $100 \times 365 = 36,500\text{ ครั้ง}$
* จำนวนครั้งที่เกิดการละเมิด Timing ใน 1 ปี:
  $$\text{Violations/Year} = 36,500 \times 0.080 = 2,920\text{ ครั้งต่อปี!}$$
นั่นหมายความว่า หากไม่มีการติดตั้ง Isolation Gate ระบบจะเกิดการกระชากของสัญญาณจนเกิด Metastability และเสี่ยงต่อ Data Corruption มากถึง **เกือบ 3,000 ครั้งในแต่ละปี!**

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** คำนวณแบบบวกความน่าจะเป็นของทั้ง 8 บิตเข้าด้วยกัน ($8 \times 8.0\% = 64\%$) ซึ่งผิดหลักสถิติเพราะเหตุการณ์การรีเซ็ตเป็นเหตุการณ์ร่วมกัน (Common Cause Event) ไม่ใช่อิสระจากกัน
* **ข้อ ค):** ตกหลุมพรางความเข้าใจผิดพื้นฐานว่า "Clock เดียวกันไม่มีทางเกิด Metastability"
* **ข้อ ง):** สมมติว่าทุกครั้งจะชนขอบเสมอ ซึ่งไม่เป็นความจริงเพราะช่วงเวลาที่เหลือ ($92\%$) อยู่นอกหน้าต่าง $T_{window}$

---

### ข้อที่ 2: การเลือกประเภทของ Isolation Cell ตามบริบทของสัญญาณ
ในการออกแบบวงจรแยกโดเมนรีเซ็ต (RDC Isolation) สำหรับสัญญาณอินเทอร์เฟซ AXI4-Stream ระหว่างบล็อกเร่งความเร็ว AI และหน่วยความจำหลัก:
1. สัญญาณ `TVALID`: Active-High ควบคุมความถูกต้องของข้อมูล
2. สัญญาณ `TREADY`: Active-High ตอบรับความพร้อมของฝั่งรับ
3. สัญญาณ `ARESETN`: Active-Low สัญญาณรีเซ็ตหลักของบัส

หากบล็อก AI กำลังจะถูกสั่ง Power-Down หรือ Warm Reset ข้อใดต่อไปนี้คือ **การกำหนดสถานะ Clamping ของ Isolation Gate ที่ถูกต้องและปลอดภัยที่สุด** เพื่อป้องกันไม่ให้ระบบหลักเกิด Deadlock หรือแซมเปิลข้อมูลขยะ?

---

#### ตัวเลือก:
* **ก)** Clamping ทุกสัญญาณให้เป็น `1` ทั้งหมด
* **ข)** Clamping ทุกสัญญาณให้เป็น `0` ทั้งหมด
* **ค)** ใช้ AND-Gate Clamping ดึง `TVALID` ลงเป็น `0` (เพื่อบอกว่าไม่มีข้อมูลส่งมา), ใช้ OR-Gate Clamping ดึง `TREADY` ขึ้นเป็น `1` (เพื่อไม่ให้ค้างท่อ หรือดึงเป็น 0 เพื่อหยุดส่งตามข้อกำหนด Flow Control), และตรึงบัสข้อมูล `TDATA` ไว้ที่ `0`
* **ง)** ตัดสายสัญญาณทิ้งแบบ High-Impedance (Hi-Z Floating)

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ค)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **พฤติกรรมของ `TVALID`:**
   หากบล็อกที่ถูกรีเซ็ตปล่อยให้ `TVALID` ลอยขึ้นเป็น `1` ฝั่งรับจะคิดว่ามีข้อมูลส่งมา และจะแซมเปิลเอาต์พุตขยะจากบล็อกที่กำลังรีเซ็ตเข้าไปประมวลผลทันที ดังนั้น `TVALID` จะต้องถูก **Clamped to 0 (AND-Gate)** เสมอ
2. **พฤติกรรมของ `TREADY`:**
   หากฝั่งรับถูกรีเซ็ตและตัดสัญญาณ `TREADY` ค้างไว้ที่ `0` ฝั่งส่งจะคิดว่าฝั่งรับไม่ว่างตลอดกาล และจะเกิดสภาวะ Pipeline Hang (Deadlock) หรือหากฝั่งส่งถูกรีเซ็ต ฝั่งรับต้องจัดการให้ `TREADY` สอดคล้องกับโปรโตคอล
3. **การหลีกเลี่ยง Hi-Z Floating (ข้อ ง):**
   ในวงจรดิจิทัลภายในชิป (On-chip Logic) **ห้ามปล่อยสายสัญญาณให้ลอย (Floating Hi-Z) เด็ดขาด** เพราะจะทำให้เกตปลายทางเกิดสภาวะแรงดันกึ่งกลาง (Intermediate Voltage) ดึงกระแสไฟทะลุผ่าน (Crowbar Current) จนชิปร้อนจัดและพังทลาย!
   ดังนั้น การกำหนด Clamping แบบเฉพาะเจาะจงตามความหมายของโปรโตคอล (ข้อ ค) จึงเป็นวิธีที่ถูกต้องตามมาตรฐานสากล $100\%$!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** การดึง `TVALID` เป็น 1 จะทำให้เกิด Spurious Data Transaction ทันที
* **ข้อ ข):** การดึงทุกอย่างเป็น 0 อาจทำให้สัญญาณที่ต้องการ Active-Low เกิดสภาวะสั่งการผิดพลาด
* **ข้อ ง):** การใช้ Hi-Z ภายใน FPGA เป็นข้อห้ามเด็ดขาดและนำไปสู่ความเสียหายทางกายภาพ

---

### ข้อที่ 3: ความแตกต่างเชิงกลไกระหว่าง Static CDC Checker และ Static RDC Checker
ข้อใดต่อไปนี้อธิบาย **ความแตกต่างพื้นฐานทางเทคโนโลยี** ระหว่างเครื่องมือ Static CDC Verification (เช่น Vivado `report_cdc`) และเครื่องมือ Static RDC Verification (เช่น Questa RDC / SpyGlass RDC) ได้อย่างถูกต้องที่สุด?

---

#### ตัวเลือก:
* **ก)** เครื่องมือ CDC ใช้เวลาทำงานนานกว่า RDC 100 เท่า
* **ข)** เครื่องมือ CDC จะสร้างรายงานความสัมพันธ์ของสัญญาณนาฬิกา (Clock Tree Topology) และตรวจสอบเฉพาะเส้นทางที่ต้นทางและปลายทางอยู่บนสัญญาณนาฬิกาคนละตัวกัน จึงละเลยเส้นทางที่ใช้สัญญาณนาฬิกาเดียวกันไปทั้งหมด; ในขณะที่เครื่องมือ RDC จะตรวจสอบโครงสร้าง **Reset Tree Topology** เพื่อหาเส้นทางที่ Register ต้นทางและปลายทางถูกควบคุมด้วยสัญญาณรีเซ็ตต่างกัน แม้จะอยู่บนสัญญาณนาฬิกาเดียวกันก็ตาม
* **ค)** เครื่องมือ RDC ตรวจสอบเฉพาะแรงดันไฟฟ้า (Voltage Drop) ไม่ได้ตรวจสอบลอจิก
* **ง)** เครื่องมือ CDC สามารถตรวจสอบปัญหา RDC ได้อย่างสมบูรณ์แบบอยู่แล้ว จึงไม่จำเป็นต้องใช้เครื่องมือ RDC แยกต่างหาก

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **กระบวนการทำงานของ CDC Checker:**
   อัลกอริทึมของเครื่องมือ CDC จะเริ่มต้นด้วยการทำ Clock Tracing เพื่อจัดกลุ่ม Register ตามแหล่งกำเนิด Clock และตรวจสอบเฉพาะคู่ Register ที่มี Clock แตกต่างกัน เมื่อเจอคู่ที่ใช้ Clock เดียวกัน เครื่องมือจะข้ามไปเพราะถือว่าเป็น Synchronous Domain
2. **กระบวนการทำงานของ RDC Checker:**
   อัลกอริทึมของ RDC Checker จะทำ Reset Domain Tracing โดยเฉพาะ:
   * จัดกลุ่ม Register ตาม Reset Tree (เช่น `rst_a` vs `rst_b`)
   * ค้นหาเส้นทาง Datapath ที่เชื่อมระหว่างสองโดเมนรีเซ็ตที่ต่างกัน
   * ตรวจสอบว่ามี Isolation Cell, Quiesce Logic, หรือ Handshake Protocol ควบคุมอยู่หรือไม่
   * หากไม่มี จะออกรายงานข้อผิดพลาด `RDC_UNISOLATED_PATH` ทันที!
นี่คือเหตุผลที่โครงการระดับ Mission-Critical จำเป็นต้องมีกระบวนการตรวจสอบทั้ง CDC และ RDC ควบคู่กันเสมอ!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ความเร็วในการทำงานขึ้นอยู่กับขนาดของ Netlist ไม่ได้ต่างกัน 100 เท่า
* **ข้อ ค):** RDC Checker เป็นเครื่องมือ Static Functional & Structural Linter ไม่ใช่โปรแกรมจำลองไฟแบบ SPICE
* **ข้อ ง):** ขัดแย้งกับความเป็นจริงทางวิศวกรรม เพราะ CDC ไม่สามารถตรวจจับ RDC ได้ตามที่พิสูจน์แล้ว
