# Lesson 143: FPGA PLL Deep Dive - Part 3 (Clock Distribution Networks and Skew Management - Global Clock Buffers BUFG/BUFGCE, Zero-Delay Buffer Mode, Clock Tree Insertion Delay, Source-Synchronous Timing Closure & Glitch-Free Muxing)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมโครงข่ายสัญญาณนาฬิกาภายในชิป FPGA (Silicon Clock Tree Architecture)
ในชิป FPGA ขนาดใหญ่ระดับ UltraScale+ หรือ Stratix 10 มี Flip-Flop, DSP Slice, และ BRAM กระจายตัวอยู่หลายแสนถึงหลายล้านตำแหน่ง หากสัญญาณนาฬิกาถูกขับผ่านสายเชื่อมต่อทั่วไป (General Routing Fabric) ค่าความล่าช้าแฝง (RC Delay) จะทำให้ขอบสัญญาณเดินทางไปถึงแต่ละจุดไม่พร้อมกัน เกิด **Clock Skew ($\Delta t_{skew}$)** ขนาดมหึมาหลายนาโนวินาที ซึ่งทำลายทั้ง Setup Time และ Hold Time

เพื่อแก้ไขปัญหานี้ ซิลิคอนของ FPGA จึงสร้างทางด่วนสัญญาณนาฬิกาเฉพาะกิจที่มีโครงสร้างแบบ **สมมาตร H-Tree / Clock Spine Architecture**:

```
                         สถาปัตยกรรม CLOCK SPINE / H-TREE ใน FPGA
                         
             +-----------------------[ CLOCK MANAGEMENT TILE ]-----------------------+
             |                               (MMCM / PLL)                            |
             +------------------------------------+----------------------------------+
                                                  |
                                                  v Dedicated Low-Skew Hard Track
                                            +-----------+
                                            |   BUFG    | Global Clock Buffer
                                            +-----+-----+
                                                  |
               ===================================+=================================== Main Horizontal Spine
               |                                  |                                  |
               v Regional Spine                   v Center Spine                     v Regional Spine
         +-----------+                      +-----------+                      +-----------+
         |   BUFH    |                      |   BUFH    |                      |   BUFH    |
         +-----+-----+                      +-----+-----+                      +-----+-----+
               |                                  |                                  |
     +---------+---------+              +---------+---------+              +---------+---------+
     |         |         |              |         |         |              |         |         |
     v Leaf    v Leaf    v Leaf         v Leaf    v Leaf    v Leaf         v Leaf    v Leaf    v Leaf
  [  FF  ]  [ BRAM ]  [ DSP  ]       [  FF  ]  [  FF  ]  [ BRAM ]       [ DSP  ]  [  FF  ]  [  FF  ]
```

#### บัฟเฟอร์สัญญาณนาฬิกาหลัก 4 ประเภทในสถาปัตยกรรมสมัยใหม่:
1. **Global Clock Buffer (`BUFG` / `BUFGCE`):** ขับสัญญาณนาฬิกาครอบคลุมทั้ง Die ของ FPGA ผ่าน Spine หลัก สามารถจ่ายสัญญาณให้ทุกทรัพยากรบนชิปโดยควบคุม Skew ภายในตระกูลเดียวกันให้น้อยกว่า $50 - 100\text{ ps}$
2. **Horizontal/Regional Clock Buffer (`BUFH` / `BUFR`):** ขับสัญญาณเฉพาะเจาะจงภายใน Clock Region เดียว ช่วยประหยัดพลังงาน Dynamic Power ได้มากกว่า 40% และมี Insertion Delay ต่ำกว่า `BUFG`
3. **I/O Dedicated Clock Buffer (`BUFIO`):** ขับเฉพาะเซลล์ I/O Bank โดยข้ามการเชื่อมต่อกับ Fabric ทั้งหมด มีค่า Insertion Delay ต่ำมาก เหมาะสำหรับ Source-Synchronous Receiver
4. **Glitch-Free Clock Control Buffer (`BUFGCTRL` / `BUFGMUX`):** วงจรสวิตช์สลับสัญญาณนาฬิกาสองแหล่งโดยปราศจากเศษพัลส์ (Glitch-free) ด้วยวงจร Synchronization ภายในระดับฮาร์ดแวร์

---

### 1.2 ความล่าช้าในการแทรกตัวและการชดเชยเฟส (Clock Tree Insertion Delay & Skew Physics)

เมื่อสัญญาณนาฬิกาเดินทางจากพินอินพุต ผ่านบัฟเฟอร์ `IBUF`, วงจร `MMCM`, บัฟเฟอร์ `BUFG` และผ่านโครงข่าย Spine ไปถึงขา $CLK$ ของ Flip-Flop ปลายทาง เวลาที่สูญเสียไปทั้งหมดเรียกว่า **Clock Tree Insertion Delay ($t_{insert}$)**:

$$t_{insert} = t_{IBUF} + t_{MMCM\_prop} + t_{BUFG} + t_{spine} + t_{leaf\_routing}$$

ในสภาวะไม่ชดเชย (No-Compensation Mode):
* ที่ Process Slow Corner, $V_{min}, T_{max} (+100^\circ\text{C})$: $t_{insert} \approx 2.5 - 4.0\text{ ns}$
* ที่ Process Fast Corner, $V_{max}, T_{min} (-40^\circ\text{C})$: $t_{insert} \approx 1.0 - 1.8\text{ ns}$
* ผลต่างของ Insertion Delay ข้าม PVT Corner สูงถึง **$\Delta t_{insert} \approx 1.5 - 2.2\text{ ns}$!**

```
                     NO-COMPENSATION MODE (Insertion Delay เคลื่อนตัวตาม PVT)
                     
 CLKIN (Pad)  ----+---------------------------------------------------------------+
                  |                                                               |
                  |  t_insert = 1.2ns (Fast Corner) ~ 3.5ns (Slow Corner)         |
                  v                                                               v
 CLK @ Reg FF ----+----------------------------------+----------------------------+
                  |<--- Uncompensated Delta t ------>|
```

หากอินเตอร์เฟซต้องติดต่อกับชิปภายนอกแบบ System-Synchronous หรือ Source-Synchronous ความแปรปรวนของ $t_{insert}$ จะกลืนกินหน้าต่างเวลา (Timing Margin Window) จนระบบพังทลายทันที!

---

### 1.3 สถาปัตยกรรม Zero-Delay Buffer Mode (ZDB) และกลไกทางคณิตศาสตร์

เพื่อกำจัดค่า $t_{insert}$ ให้เป็นศูนย์อย่างสมบูรณ์แบบ วงจร MMCM ถูกกำหนดค่าให้ทำงานในโหมด **Zero-Delay Buffer (ZDB)** โดยการสร้างเส้นทางป้อนกลับย้อนรอย (Negative Feedback Loop) ผ่านโครงข่ายสัญญาณนาฬิกาเดียวกัน:

```
               สถาปัตยกรรม ZERO-DELAY BUFFER (ZDB) ภายใน FPGA
               
               +---------------------------------------------------------------+
               |                             MMCM                              |
               |                                                               |
 CLKIN (Pin) ->|->[ PFD ]--->[ CP/LF ]--->[ VCO ]--->[ /O0 ]---> CLKOUT0        |
               |     ^                                            |            |
               |     |                                            v            |
               |     |                                       +---------+       |
               |     |                                       |  BUFG0  |       |
               |     |                                       +----+----+       |
               |     |                                            |            |
               |     |                                            +---+=======> TO FABRIC LOGIC
               |     |                                                |
               |     |     +------------------+                       | (Forward Tree Delay t_tree)
               |     |     |   CLKFBIN Pad    |<----------------------+
               |     |     +--------+---------+
               |     |              |
               |     |   +----------+-----------+
               |     +---| /M (Feedback Divider)|<============================= FEEDBACK PATH
               |         +----------------------+             (Compensates t_tree exactly!)
               +---------------------------------------------------------------+
```

#### สมการทางคณิตศาสตร์ของการชดเชยเฟสใน ZDB Mode:
ให้:
* $\theta_{in}$ คือเฟสของสัญญาณนาฬิกาขาเข้าที่ Pad
* $\theta_{vco}$ คือเฟสเอาต์พุตของ VCO
* $t_{tree}$ คือ Insertion Delay ของบัฟเฟอร์ `BUFG` และโครงข่ายสายสัญญาณไปยังรีจิสเตอร์
* $t_{fb}$ คือ Insertion Delay ของเส้นทางป้อนกลับจากเอาต์พุต `CLKFBOUT` ผ่าน `BUFG` ย้อนเข้าพอร์ต `CLKFBIN`

เงื่อนไขการล็อกของ PFD ที่สภาวะ Steady State:
$$\theta_{PFD\_ref} = \theta_{PFD\_fb}$$
$$\theta_{in} = \theta_{vco} - \omega \cdot t_{fb}$$
$$\theta_{vco} = \theta_{in} + \omega \cdot t_{fb}$$

เฟสของสัญญาณนาฬิกาที่เดินทางไปถึง Flip-Flop ปลายทางใน Fabric ($\theta_{dest}$):
$$\theta_{dest} = \theta_{vco} - \omega \cdot t_{tree}$$
แทนค่า $\theta_{vco}$ ลงในสมการ:
$$\theta_{dest} = (\theta_{in} + \omega \cdot t_{fb}) - \omega \cdot t_{tree} = \theta_{in} + \omega \cdot (t_{fb} - t_{tree})$$

> [!IMPORTANT]
> **บทพิสูจน์ทางฟิสิกส์:** หากเราออกแบบให้โครงข่ายป้อนกลับสมมาตรกับโครงข่ายหลัก ($t_{fb} \equiv t_{tree}$):
> $$\theta_{dest} \equiv \theta_{in}$$
> **ค่า Insertion Delay ของสัญญาณนาฬิกาภายในชิป FPGA ทั้งหมดจะถูกหักล้างจนกลายเป็น 0.00 ps เสมือนสัญญาณนาฬิกาที่ Pad วาร์ปไปปรากฏที่ขา Flip-Flop ทุกตัวในทันที!**

---

### 1.4 โหมดการทำงานของ MMCM Compensation ในเครื่องมือสังเคราะห์ (Vivado/Quartus)

```
+---------------------+-------------------------------+------------------------------------------------------+
| COMPENSATION Mode   | Feedback Source               | วัตถุประสงค์และการใช้งาน                             |
+---------------------+-------------------------------+------------------------------------------------------+
| ZHOLD / HIGH_BTT    | CLKOUT0 -> BUFG -> CLKFBIN    | ชดเชย Clock Tree ภายใน เพื่อรักษาระดับ Hold Time = 0 |
| ZDB (Zero-Delay)    | CLKFBOUT -> BUFG -> CLKFBIN   | เฟสสัญญาณภายนอก Pad ตรงกับขาสัญญาณนาฬิกาภายใน 100%   |
| EXTERNAL            | PCB Trace External Feedback   | ชดเชยทั้ง Clock Tree ใน FPGA และ Trace Delay บนบอร์ด |
| INTERNAL / NO_COMP  | VCO Direct Feedback           | ไม่ชดเชย ใช้สำหรับสัญญาณภายในที่ไม่แคร์ I/O Phase     |
+---------------------+-------------------------------+------------------------------------------------------+
```

---

### 1.5 วงจรสลับสัญญาณนาฬิกาไร้กลิตช์ (Glitch-Free Clock Multiplexing Physics)

การสลับแหล่งสัญญาณนาฬิกา (Clock Switching) ด้วยวงจร Multiplexer ปกติใน Fabric (`assign clk_out = sel ? clk_b : clk_a;`) จะก่อให้เกิด **เศษพัลส์ (Runt Pulse)** ที่มีความกว้างสั้นกว่าสเปกขั้นต่ำของทรานซิสเตอร์ ($T_{pulse} < T_{min}$):

```
                       อันตรายของ RUNT PULSE จาก FABRIC LUT MUX
                       
 CLK_A   ----+   +---+   +---+   +---+   +---+
             |   |   |   |   |   |   |   |   |
         ----+---+   +---+   +---+   +---+   +-----------------
 
 CLK_B   --------------------+   +---+   +---+   +---+   +---+
                             |   |   |   |   |   |   |   |
                             +---+   +---+   +---+   +---+   +-
 
 SEL     --------------------+================================= (สลับขั้วตรงกลางรอบสัญญาณ)
                             |
 CLK_OUT ----+   +---+   +---+! !+---+   +---+   +---+   +---+
             |   |   |   |   |! !|   |   |   |   |   |   |
         ----+---+   +---+   +-! !---+   +---+   +---+   +-----
                               ^
                               |-- DANGER: Runt Pulse (< 150 ps)!
                                   ทำลาย State Machine และสร้าง Metastability ทันที!
```

#### กลไกการทำงานของฮาร์ดแวร์ `BUFGMUX` / `BUFGCTRL`:
เพื่อป้องกัน Runt Pulse โดยเด็ดขาด ฮาร์ดแวร์ `BUFGCTRL` ภายใน FPGA ใช้หลักการ **Dual Negative-Edge Gating FSM**:
1. เมื่อสัญญาณ `S` เปลี่ยนขั้ว วงจรจะไม่สลับสัญญาณนาฬิกาทันที
2. รอจนกระทั่งสัญญาณนาฬิกาปัจจุบัน ($CLK_A$) ตกเป็นระดับต่ำ (`Low`) วงจรถึงจะตัดสวิตช์ $CLK_A$ ออก
3. สัญญาณเอาต์พุตจะถูกดึงค้างไว้ที่ระดับ `Low` อย่างปลอดภัย
4. รอจนกระทั่งสัญญาณนาฬิกาเป้าหมาย ($CLK_B$) มีระดับเป็น `Low` เช่นกัน วงจรจึงเปิดสวิตช์ให้ $CLK_B$ วิ่งผ่าน
5. สัญญาณนาฬิกาใหม่จะเริ่มทำงานจากขอบขาขึ้นสมบูรณ์ลูกแรกเท่านั้น ปราศจาก Glitch 100%!

```verilog
// สถาปัตยกรรมวงจร BUFGMUX Primitive ภายในฮาร์ดแวร์
BUFGMUX #(
    .CLK_SEL_TYPE("SYNC") // บังคับใช้วงจร Glitch-Free Synchronous Switchover
) u_bufgmux (
    .O   (clk_out),       // สัญญาณนาฬิกาเอาต์พุตที่ปลอดภัย
    .I0  (clk_primary),   // สัญญาณนาฬิกาหลัก (เช่น 100 MHz)
    .I1  (clk_backup),    // สัญญาณนาฬิกาสำรอง (เช่น 50 MHz)
    .S   (clk_sel)        // สัญญาณเลือกแหล่งกำเนิด
);
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** เครื่องตรวจคลื่นเสียงความถี่สูงทางการแพทย์ (Medical Ultrasound Beamformer) ใช้อินเตอร์เฟซรับข้อมูล ADC 14-บิต ความเร็ว $250.0\text{ MSPS}$ ($F_{clk} = 250\text{ MHz}$, $T_{clk} = 4.0\text{ ns}$) แบบ Source-Synchronous DDR ทำงานร่วมกับ FPGA Kintex UltraScale+ (XCKU040)

**วิกฤตหน้างาน:** ระบบผ่านการทดสอบในสายการผลิตที่อุณหภูมิห้อง $+25^\circ\text{C}$ ได้อย่างราบรื่น แต่เมื่อนำเครื่องต้นแบบเข้าทดสอบ Burn-in ที่สภาวะโหลดความร้อนสูง $+85^\circ\text{C}$ ระบบตรวจพบความผิดพลาดของข้อมูล (Image Artifacts / Bit Corruption) โดยพบการละเมิดเงื่อนไข **Hold Time Violation** บนบัสข้อมูลความเร็วสูงทุกเลน ทำให้ภาพอัลตราซาวด์แตกลายและสูญเสียความละเอียดในการตรวจวินิจฉัยทางการแพทย์!

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] อินเตอร์เฟซ ADC 250 MSPS เกิด Hold Time Violation ที่อุณหภูมิ +85°C
      |
      +---> [Why 1] ทำไมจึงเกิด Hold Violation บนบัสข้อมูลที่ +85°C?
      |             --> เพราะขอบสัญญาณนาฬิกาภายในมาช้ากว่าขอบข้อมูล ทำให้ Hold Slack กลายเป็น -380 ps
      |
      +---> [Why 2] ทำไมขอบสัญญาณนาฬิกาภายในถึงมาช้าลงที่อุณหภูมิสูง?
      |             --> เพราะค่า Clock Tree Insertion Delay ขยายตัวจาก 1.4 ns ที่ 25°C กลายเป็น 2.8 ns ที่ 85°C
      |
      +---> [Why 3] ทำไม Clock Tree Insertion Delay จึงส่งผลกระทบต่อ I/O Timing?
      |             --> เพราะ MMCM ถูกตั้งค่าแอตทริบิวต์ COMPENSATION = "INTERNAL" ซึ่งตัดวงจรป้อนกลับทิ้ง
      |
      +---> [Why 4] ทำไมผู้ออกแบบถึงตั้งค่า COMPENSATION = "INTERNAL"?
      |             --> เพราะตอนสร้างโมดูล Clocking Wizard ได้เลือก Default Mode สำหรับ Internal Synthesis
      |                 โดยไม่ได้เชื่อมต่อเส้นทาง CLKFBOUT กลับเข้าสู่ CLKFBIN ผ่าน BUFG
      |
      +---> [Why 5 - Root Cause] ทำไมความผิดพลาดนี้จึงหลุดรอดการตรวจสอบ?
                    --> เพราะผู้ออกแบบไม่ได้กำหนด SDC Constraint แบบ Source-Synchronous Multi-Corner
                        และไม่มีการรัน Report Timing Summary ที่ Fast-Corner/Slow-Corner ในขั้นตอน Sign-off!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการเกิด Hold Time Violation บนอินเตอร์เฟซ Source-Synchronous ADC

   CLOCK TOPOLOGY (MMCM Feedback)             CONSTRAINTS & EDA (Static Timing)
         |                                          |
   ตั้งค่า COMPENSATION = "INTERNAL"                 ขาดการระบุ create_clock บนพอร์ตเสมือน (Virtual Clock)
         \                                          /
          \   ไม่ต่อ CLKFBOUT ผ่าน BUFG            /   ไม่รันวิเคราะห์ Hold Slack ที่ Fast Process Corner
           \   ไม่มีการชดเชย Insertion Delay       /   ขาดคำสั่ง set_clock_latency
            +------------------------------------+
            |                                    |
            |   SOURCE-SYNCHRONOUS HOLD TIME     |===> [CRITICAL HARDWARE FAILURE]
            |   VIOLATION AT +85°C (-380 ps)     |
            +------------------------------------+
           /                                      \
          /   ขาดการคำนวณ PCB Trace Skew Mismatch   \   ทดสอบเฉพาะบอร์ดที่อุณหภูมิห้องปกติ (+25°C)
         /                                          \
   ใช้ Fabric LUT ทำ Clock Muxing แทน BUFGCTRL       ละเลยการมอนิเตอร์ Runt Pulse บนออสซิลโลสโคป
         |                                          |
   RTL DESIGN TRAPS                           MEASUREMENT / ENVIRONMENT
```

---

### ขั้นตอนการแก้ปัญหาและแนวทางป้องกันหน้างาน (Corrective Actions & SOP)

#### ขั้นตอนที่ 1: ปรับแก้โทโพโลยี MMCM ให้เป็น ZHOLD / ZDB Mode อย่างสมบูรณ์
แก้ไขโค้ดการเชื่อมต่อพอร์ต MMCM เพื่อให้เกิดการชดเชย Insertion Delay แบบปิดลูป:

```verilog
// ==============================================================================
// SOP-COMPLIANT ZERO-DELAY BUFFER CLOCK NETWORK WITH ZHOLD COMPENSATION
// ==============================================================================
wire clk_in_buf;
wire clk_fb_out;
wire clk_fb_buf;
wire clk_adc_internal;

// 1. นำสัญญาณนาฬิกาจากภายนอกเข้าบัฟเฟอร์ขาเข้าเฉพาะทาง
IBUF u_ibuf_clk (
    .I(adc_dclk_p),
    .O(clk_in_buf)
);

// 2. อินสแตนชิเอต MMCM ในโหมด ZHOLD เพื่อล็อคขอบสัญญาณภายนอกและภายในให้ตรงกัน
MMCME4_ADV #(
    .BANDWIDTH            ("OPTIMIZED"),
    .CLKIN1_PERIOD        (4.000),         // 250.0 MHz
    .CLKFBOUT_MULT_F      (4.000),         // VCO = 250 * 4 = 1000 MHz
    .DIVCLK_DIVIDE        (1),
    .CLKOUT0_DIVIDE_F     (4.000),         // Output = 1000 / 4 = 250 MHz
    .COMPENSATION         ("ZHOLD"),       // บังคับชดเชย Zero-Hold Delay ข้ามทุก Corner!
    .STARTUP_WAIT         ("FALSE")
) u_mmcm_zdb (
    .CLKIN1               (clk_in_buf),
    .CLKFBIN              (clk_fb_buf),    // ป้อนสัญญาณป้อนกลับที่ผ่าน BUFG เข้ามา
    .CLKFBOUT             (clk_fb_out),
    .CLKOUT0              (clk_adc_internal),
    .LOCKED               (mmcm_locked),
    // ... [พอร์ตควบคุมอื่นๆ]
);

// 3. ป้อนกลับสัญญาณนาฬิกาผ่าน Global Clock Tree เดียวกันเพื่อชดเชย Delay
BUFG u_bufg_fb (
    .I(clk_fb_out),
    .O(clk_fb_buf)
);

// 4. บัฟเฟอร์สัญญาณนาฬิกาหลักสำหรับส่งเข้า Fabric Logic
BUFG u_bufg_out (
    .I(clk_adc_internal),
    .O(clk_adc_global)
);
```

---

### SOP Checklist สำหรับการ Sign-off โครงข่ายสัญญาณนาฬิกา (Clock Network Sign-off)

```
[ ] 1. MMCM Compensation Verification:
       - อินเตอร์เฟซ I/O ใดๆ ที่ส่งข้อมูลความเร็วสูง ต้องใช้ COMPENSATION = "ZHOLD" หรือ "ZDB" เท่านั้น
       - ห้ามปล่อยให้เป็น "INTERNAL" เด็ดขาดหากมีการสื่อสารข้ามชิปผ่าน Source-Synchronous Bus

[ ] 2. Dedicated Feedback Loop Path:
       - ตรวจสอบว่าพอร์ต CLKFBOUT ต่อเข้ากับ BUFG และวนกลับเข้า CLKFBIN โดยตรง ไม่มีการใส่ลอจิกคั่น
       - ความยาวสายจำลอง (Routing Skew) ของ Feedback ต้องแมตช์กับเส้นทางหลัก

[ ] 3. Glitch-Free Clock Switching:
       - ห้ามใช้เกต AND/OR หรือคำสั่ง `assign clk = sel ? clk1 : clk0;` ใน RTL เด็ดขาด
       - ต้องใช้ฮาร์ดแวร์พรีมิทิฟ BUFGMUX หรือ BUFGCTRL ที่มีพารามิเตอร์ CLK_SEL_TYPE = "SYNC"

[ ] 4. Multi-Corner STA Sign-off:
       - ตรวจสอบ Setup Slack ที่ Slow-Corner (100°C, Vmin) ต้องมากกว่า +150 ps
       - ตรวจสอบ Hold Slack ที่ Fast-Corner (-40°C, Vmax) ต้องมากกว่า +100 ps
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| クロック配線網 | くろっくはいせんもう | Kurokku Haisen-mō | โครงข่ายกระจายสัญญาณนาฬิกา (Clock Distribution Network) |
| スキュー調整 | すきゅーちょうせい | Sukyū Chōsei | การปรับจูนความเหลื่อมเวลาของสัญญาณ (Skew Management) |
| ゼロ遅延バッファ | ぜろちえんばっふぁ | Zero Chien Baffa | โหมดบัฟเฟอร์ความล่าช้าเป็นศูนย์ (Zero-Delay Buffer: ZDB) |
| 挿入遅延 | そうにゅうちえん | Sōnyū Chien | ความล่าช้าจากการแทรกตัวของเครือข่าย (Insertion Delay) |
| ラントパルス | らんとぱるす | Ranto Parusu | เศษพัลส์ที่แคบเกินมาตรฐานจนเกิดอันตราย (Runt Pulse) |
| 無瞬断切り替え | むしゅんだんきりかえ | Mushundan Kirikae | การสลับสัญญาณนาฬิกาโดยไร้การสะดุดและไร้กลิตช์ (Glitch-free Switching) |
| 外部帰還 | がいぶきかん | Gaibu Kikan | การป้อนกลับภายนอกผ่านลายวงจรบอร์ด (External Feedback) |
| 遅延補償 | ちえんほしょう | Chien Hoshō | การชดเชยความล่าช้าของเวลา (Delay Compensation) |
| ソース同期 | そーすどうき | Sōsu Dōki | การส่งสัญญาณนาฬิกาควบคู่ไปกับข้อมูล (Source-Synchronous) |
| ホールド時間違反 | ほーるどじかんいはん | Hōrudo Jikan Ihan | การละเมิดเงื่อนไขเวลาค้างข้อมูล (Hold Time Violation) |
| 物理専用配線 | ぶつりせんようはいせん | Butsuri Sen'yō Haisen | สายสัญญาณฮาร์ดแวร์เฉพาะกิจ (Dedicated Physical Routing) |
| 位相不整合 | いそうふせいごう | Isō Fuseigō | ความไม่สอดคล้องหรือความคลาดเคลื่อนของเฟส (Phase Mismatch) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการใช้ Fabric LUT ทำ Clock Muxing แทน `BUFGMUX`
**สถานที่:** ห้องปฏิบัติการทดสอบระบบเรดาร์ตรวจการณ์ทางเรือ (Defense Naval Radar Labs)  
**ผู้เข้าร่วม:** Lead Chief Engineer (หัวหน้าวิศวกรผู้เชี่ยวชาญ) และ FPGA RTL Designer (วิศวกรออกแบบ RTL)

* **Lead Chief Engineer:**  
  「おい、このRTLコードのクロックセレクタ部分を見ろ。`assign sys_clk = sel ? clk_fast : clk_slow;` と記述しているな。まさかファブリックのLUTでクロックをマルチプレクスしているのか？こんな初歩的な禁じ手を誰が承認したんだ！非同期クロックをLUTで切り替えたら、切り替えの瞬間にサブナノ秒のラントパルス（微小ヒゲ状パルス）が確実に発生するぞ。」  
  *(Oi, kono RTL kōdo no kurokku serekuta bubun o miro. `assign sys_clk = sel ? clk_fast : clk_slow;` to kijutsu shite iru na. Masaka faburikku no LUT de kurokku o maruchipurekusu shite iru no ka? Konna shohoteki na kinjite o dare ga shōnin shita n da! Hidōki kurokku o LUT de kirikaetara, kirikae no shunkan ni sabu-nanobyō no ranto parusu (bishō higejō parusu) ga kakujitsu ni hassei suru zo.)*  
  **ความหมาย:** "เฮ้ย ดูตรงตัวเลือกสัญญาณนาฬิกาในโค้ด RTL ตรงนี้สิ เขียนว่า `assign sys_clk = sel ? clk_fast : clk_slow;` งั้นเรอะ? นี่คุณเอา Fabric LUT มาทำ Multiplex สัญญาณนาฬิกาจริงๆ หรือเนี่ย? ใครอนุมัติให้ใช้วิธีต้องห้ามระดับพื้นฐานแบบนี้! ถ้าสลับสัญญาณนาฬิกาที่อะซิงโครนัสกันด้วย LUT ในจังหวะที่สลับมันจะเกิด Runt Pulse (เศษพัลส์ระดับต่ำกว่านาโนวินาที) ขึ้นมาแน่นอน!"

* **RTL Designer:**  
  「セレクタ信号 `sel` は同期化回路を通してあるので安全かと判断していました。クロックライン自体に直接グリッチが生じる物理的リスクまで深く考えていませんでした。」  
  *(Serekuta shingō `sel` wa dōkika kairo o tōshite aru node anzen ka to handan shite imashita. Kurokku rain jitai ni chokusetsu guritchi ga shōjiru butsuri-teki risuku made fukaku kangaete imasen deshita.)*  
  **ความหมาย:** "สัญญาณเลือก `sel` ผมต่อผ่านวงจร Synchronizer มาแล้วเลยคิดว่าน่าจะปลอดภัยครับ ไม่ทันได้คิดลึกไปถึงความเสี่ยงทางกายภาพที่จะเกิด Glitch สับบนเส้นสัญญาณนาฬิกาโดยตรงครับ"

* **Lead Chief Engineer:**  
  「同期化しても、2つのクロックのエッジタイミングが異なれば、LUTのゲート遅延差（Hazard）でグリッチが出るのは物理の必然だ！ラントパルスが後段のFSMに入れば、ステートが未定義領域に吹き飛んでシステムが全停止する。直ちにFPGAハードウェア専用の `BUFGMUX` もしくは `BUFGCTRL` プリミティブに置き換えろ。両方のクロックがLowレベルに落ちたことを確認してから安全に切り替えるシーケンスにするんだ！」  
  *(Dōkika shite mo, 2-tsu no kurokku no ejji taimingu ga kotonareba, LUT no gēto chien-sa (hazādo) de guritchi ga deru no wa butsuri no hitsuzen da! Ranto parusu ga kōdan no FSM ni haireba, sutēto ga miteigi ryōiki ni fukitonde shisutemu ga zen-teishi suru. Tadachini FPGA hādowea sen'yō no `BUFGMUX` moshiku wa `BUFGCTRL` purimitibu ni okikaero. Ryōhō no kurokku ga Low reberu ni ochita koto o kakunin shite kara anzen ni kirikaeru shīkensu ni suru n da!)*  
  **ความหมาย:** "ต่อให้ซิงโครไนซ์แล้ว แต่ถ้าจังหวะขอบของ Clock ทั้งสองตัวไม่ตรงกัน ความต่างของ Gate Delay ใน LUT (Hazard) มันจะคลอด Glitch ออกมาตามหลักฟิสิกส์อย่างหลีกเลี่ยงไม่ได้! ถ้า Runt Pulse นั้นหลุดเข้า FSM ข้างหลัง สถานะจะเตลิดเข้าเขต Undefined แล้วระบบจะหยุดทำงานสนิท จงไปเปลี่ยนเป็นฮาร์ดแวร์พรีมิทิฟเฉพาะทาง `BUFGMUX` หรือ `BUFGCTRL` ทันที และต้องตั้งให้มันรอจนขอบสัญญาณทั้งคู่ตกลงเป็น Low ก่อนถึงจะสลับได้อย่างปลอดภัย!"

---

#### สถานการณ์ที่ 2: การตรวจสอบปัญหา Hold Time Violation จากการขาดการชดเชย Zero-Delay Buffer
* **Lead Chief Engineer:**  
  「ADCのソース同期インターフェースだが、Timing SummaryでFast Corner側（マイナス40℃）のホールドマージンがマイナス380psで赤く染まっている。MMCMの接続を見ると、フィードバックが `COMPENSATION = "INTERNAL"` になっているじゃないか。これではClock Treeの挿入遅延（約2.5ns）が全く補償されないぞ。」  
  *(ADC no sōsu dōki intāfēsu da ga, Timing Summary de Fast Corner-gawa (mainasu 40-do) no hōrudo mājin ga mainasu 380ps de akaku somatte iru. MMCM no setsuzoku o miru to, fīdobakku ga `COMPENSATION = "INTERNAL"` ni natte iru ja nai ka. Kore de wa Clock Tree no sōnyū chien (yaku 2.5ns) ga mattaku hoshō sarenai zo.)*  
  **ความหมาย:** "ตรงอินเตอร์เฟซ Source-Synchronous ของ ADC ใน Timing Summary ช่อง Hold Margin ฝั่ง Fast Corner ($-40^\circ\text{C}$) มันติดลบแดงเถือกไป -380ps พอดูการต่อ MMCM ปรากฏว่าเส้นทางป้อนกลับถูกตั้งเป็น `COMPENSATION = "INTERNAL"` อยู่นี่นา แบบนี้ Insertion Delay ของ Clock Tree (ราวๆ 2.5ns) ก็ไม่ได้รับการชดเชยเลยสักนิด!"

* **RTL Designer:**  
  「Clocking Wizardの初期設定のまま流用してしまいました。外部クロックと内部クロックの遅延を合わせるには、ZDBモードに直す必要がありますね。」  
  *(Clocking Wizard no shoki settei no mama ryūyō shite shimaimashita. Gaibu kurokku to naibu kurokku no chien o awaseru ni wa, ZDB mōdo ni naosu hitsuyō ga arimasu ne.)*  
  **ความหมาย:** "ผมก๊อปปี้ค่าตั้งต้นมาจาก Clocking Wizard โดยตรงครับ ถ้าจะให้ Delay ภายนอกกับภายในตรงกัน ต้องปรับเป็นโหมด ZDB สินะครับ"

* **Lead Chief Engineer:**  
  「そうだ。`CLKFBOUT` から `BUFG` を通して `CLKFBIN` に戻し、`COMPENSATION = "ZHOLD"` を明示的に宣言しろ。そうすればPVT変動によるクロックツリー遅延が完全に打ち消され、ホールド違反はゼロになる。今すぐ修正してBitstreamを再生成し、実機チャンバーで温度試験をやり直せ。」  
  *(Sō da. `CLKFBOUT` kara `BUFG` o tōshite `CLKFBIN` ni modoshi, `COMPENSATION = "ZHOLD"` o meijiteki ni sengen shiro. Sō sureba PVT hendō ni yoru kurokku tsurī chien ga kanzen ni uchikesare, hōrudo ihan wa zero ni naru. Ima sugu shūsei shite Bitstream o sai-seisei shi, jikki chanbā de ondo shiken o yarinaose.)*  
  **ความหมาย:** "ถูกต้อง! ต่อเส้น `CLKFBOUT` ผ่าน `BUFG` กลับเข้า `CLKFBIN` แล้วประกาศแอตทริบิวต์ `COMPENSATION = "ZHOLD"` ให้ชัดเจน ทำแบบนี้ความผันผวนของ Clock Tree Delay ตามสภาวะ PVT จะถูกหักล้างจนหมดสิ้น และ Hold Violation จะกลายเป็นศูนย์ทันที ไปแก้โค้ดตอนนี้ เจนเนอเรต Bitstream ใหม่ แล้วเอาไปทดสอบในตู้ควบคุมอุณหภูมิซ้ำอีกรอบ!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณ Timing Budget และ Hold Slack ในโหมด ZDB vs Non-Compensated (Source-Synchronous Timing Budgeting)
ในระบบรับส่งข้อมูลภาพทางการแพทย์ความเร็วสูง บัสข้อมูลแบบขนาน 16-บิต รับส่งข้อมูลแบบ Single Data Rate (SDR):
* คาบเวลาของสัญญาณนาฬิกา: $T_{clk} = 4.000\text{ ns}$ ($F_{clk} = 250.0\text{ MHz}$)
* ความคลาดเคลื่อนของเวลาส่งข้อมูลจากชิปต้นทางภายนอก:
  * $t_{co,max} = 1.800\text{ ns}$
  * $t_{co,min} = 0.900\text{ ns}$
* ความเหลื่อมล้ำของลายทองแดงบนแผ่นวงจรพิมพ์ (PCB Trace Skew Mismatch):
  * $t_{pcb,skew} = \pm 0.050\text{ ns} = \pm 50\text{ ps}$
* ข้อกำหนด Timing ของ Flip-Flop ขาเข้าใน FPGA (IOB Storage Element):
  * $t_{setup} = 0.250\text{ ns} = 250\text{ ps}$
  * $t_{hold} = 0.150\text{ ns} = 150\text{ ps}$
* Clock Uncertainty และ Phase Jitter รวม: $t_{uncert} = 0.100\text{ ns} = 100\text{ ps}$

หากในสถาปัตยกรรมแบบ **ไม่ชดเชย (Non-Compensated Mode)** สัญญาณนาฬิกาภายในมีค่า Insertion Delay แปรผันตามอุณหภูมิ:
* $t_{insert,min} = 1.200\text{ ns}$ (ที่ Fast Corner)
* $t_{insert,max} = 2.800\text{ ns}$ (ที่ Slow Corner)

และในสถาปัตยกรรมแบบ **Zero-Delay Buffer Mode (ZDB)** ค่า Insertion Delay สุทธิถูกควบคุมให้เหลือ:
* $t_{insert,net} = 0.000\text{ ns} \pm 0.040\text{ ns}$ (残留スキュー Residual Skew)

จงคำนวณหาค่า **Worst-Case Hold Slack ($t_{hold\_slack}$)** ภายใต้ทั้งสองสถาปัตยกรรม (โดยที่ค่าติดลบหมายถึงเกิด Timing Violation):

A) Non-Compensated: $t_{hold\_slack} = -2.100\text{ ns}$, \quad ZDB: $t_{hold\_slack} = +0.560\text{ ns}$  
B) Non-Compensated: $t_{hold\_slack} = -0.500\text{ ns}$, \quad ZDB: $t_{hold\_slack} = +1.100\text{ ns}$  
C) Non-Compensated: $t_{hold\_slack} = +0.350\text{ ns}$, \quad ZDB: $t_{hold\_slack} = +0.800\text{ ns}$  
D) Non-Compensated: $t_{hold\_slack} = -1.250\text{ ns}$, \quad ZDB: $t_{hold\_slack} = +0.220\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: ทำความเข้าใจสมการ Hold Slack สำหรับอินเตอร์เฟซขาสัญญาณเข้า (Input Interface)**
สมการวิศวกรรมสำหรับ Hold Slack:
$$t_{hold\_slack} = t_{data\_arrival\_min} - t_{clock\_arrival\_max} - t_{hold}$$
โดยที่:
* $t_{data\_arrival\_min} = t_{co,min} - |t_{pcb,skew}| = 0.900\text{ ns} - 0.050\text{ ns} = 0.850\text{ ns}$
* $t_{hold} = 0.150\text{ ns}$

**ขั้นตอนที่ 2: คำนวณกรณี Non-Compensated Mode**
ในโหมดไม่ชดเชย สัญญาณนาฬิกามาถึง Flip-Flop ช้าเนื่องจากเดินทางผ่าน Clock Tree ($t_{insert}$):
* สัญญาณนาฬิกามาช้าที่สุดที่จุด Slow Corner:
  $$t_{clock\_arrival\_max} = t_{insert,max} + t_{uncert} = 2.800\text{ ns} + 0.100\text{ ns} = 2.900\text{ ns}$$
* คำนวณ Hold Slack:
  $$t_{hold\_slack} = 0.850\text{ ns} - 2.900\text{ ns} - 0.150\text{ ns} = 0.850 - 3.050 = -2.200\text{ ns}$$
  หรือหากพิจารณา Clock Uncertainty แบบสมมาตร ($t_{clock\_arrival} = 2.800\text{ ns}$):
  $$t_{hold\_slack} = 0.850\text{ ns} - 2.800\text{ ns} - 0.150\text{ ns} = -2.100\text{ ns}$$
  *(เกิด Hold Violation รุนแรงมาก ข้อมูลใหม่วิ่งเข้ามาทับข้อมูลเก่ายับเยิน!)*

**ขั้นตอนที่ 3: คำนวณกรณี Zero-Delay Buffer Mode (ZDB)**
ในโหมด ZDB การหน่วงเวลา $t_{insert}$ ถูกชดเชยเหลือเพียง Residual Skew $\pm 0.040\text{ ns}$:
* สัญญาณนาฬิกามาถึงจริง:
  $$t_{clock\_arrival\_max} = +0.040\text{ ns} + t_{uncert} = 0.040\text{ ns} + 0.100\text{ ns} = 0.140\text{ ns}$$
  (หรือหาก $t_{uncert}$ คิดแยกในสมการ Timing Analyzer: $t_{clock\_arrival} \approx 0.040\text{ ns}$)
* คำนวณ Hold Slack:
  $$t_{hold\_slack} = t_{data\_arrival\_min} - t_{clock\_arrival\_max} - t_{hold}$$
  $$t_{hold\_slack} = 0.850\text{ ns} - 0.140\text{ ns} - 0.150\text{ ns} = 0.850 - 0.290 = +0.560\text{ ns}$$
  *(มี Hold Margin เหลือเฟือถึง $+560\text{ ps}$ ปลอดภัยสมบูรณ์แบบ 100%)*

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบที่ถูกต้องคือ **A** ($t_{hold\_slack} = -2.100\text{ ns}$ สำหรับ Non-Compensated และ $+0.560\text{ ns}$ สำหรับ ZDB)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคำนวณการหน่วงเวลาของ Clock Tree ผิดพลาดโดยใช้ค่า Fast Corner มาคิด Hold Violations ซึ่งตามกฎ STA การเกิด Worst-case Hold ข้ามชิปเกิดเมื่อ Clock มาช้าที่สุดเทียบกับ Data ที่มาเร็วที่สุด
* ข้อ C ผิด เพราะทึกทักว่าไม่มี Insertion Delay ในโหมดปกติ
* ข้อ D มีการคำนวณ Residual Skew ผิดทิศทาง

---

### คำถามที่ 2: การคำนวณความยาวลายวงจรป้อนกลับภายนอก (PCB External Feedback Trace Matching)
ในการออกแบบระบบ Radar Beamforming หลายบอร์ดเชื่อมต่อกัน สัญญาณนาฬิกา $100.0\text{ MHz}$ ถูกกระจายจาก Master Clock Generator ไปยัง FPGA จำนวน 4 ตัวบนบอร์ดเดียวกัน โดยใช้ MMCM ในโหมด **External Feedback ZDB**

ข้อมูลทางกายภาพของแผ่นวงจรพิมพ์ PCB (วัสดุ Megtron-6 ความถี่สูง):
* ค่าคงที่ไดอิเล็กทริกยังผล (Effective Dielectric Constant): $\epsilon_r = 3.61$
* ความเร็วการเดินทางของคลื่นแม่เหล็กไฟฟ้าในตัวกลาง:
  $$v = \frac{c}{\sqrt{\epsilon_r}} = \frac{3.0 \times 10^8\text{ m/s}}{\sqrt{3.61}} = \frac{3.0 \times 10^8}{1.90} \approx 1.579 \times 10^8\text{ m/s}$$
* ค่าความล่าช้าต่อหน่วยความยาว (Propagation Delay per Unit Length):
  $$\tau_{prop} = \frac{1}{v} \approx 6.333\text{ ps/mm} \approx 160.86\text{ ps/inch}$$

หากลายวงจรที่ส่งสัญญาณนาฬิกาไปยังโหลดปลายทาง (Destination Clocks) มีความยาวเฉลี่ย $L_{dest} = 120.0\text{ mm}$  
และระบบต้องการควบคุม Phase Skew ระหว่างขาสัญญาณนาฬิกาภายนอกกับสัญญาณนาฬิกาภายใน FPGA ให้มีความคลาดเคลื่อนไม่เกิน $|\Delta t_{skew}| \le 20.0\text{ ps}$

จงคำนวณหาช่วงความยาวของลายทองแดงป้อนกลับภายนอก ($L_{fb}$) ที่ต้องเดินจากพอร์ต `CLKFBOUT` ย้อนกลับมาเข้าพอร์ต `CLKFBIN`:

A) $116.84\text{ mm} \le L_{fb} \le 123.16\text{ mm} \quad (\Delta L \le \pm 3.16\text{ mm})$  
B) $110.50\text{ mm} \le L_{fb} \le 129.50\text{ mm} \quad (\Delta L \le \pm 9.50\text{ mm})$  
C) $118.42\text{ mm} \le L_{fb} \le 121.58\text{ mm} \quad (\Delta L \le \pm 1.58\text{ mm})$  
D) $119.50\text{ mm} \le L_{fb} \le 120.50\text{ mm} \quad (\Delta L \le \pm 0.50\text{ mm})$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: วิเคราะห์ความสัมพันธ์ของความยาวลายวงจรกับความล่าช้า**
ความล่าช้าของสัญญาณบนลายวงจรแปรผันตรงกับความยาว:
$$\Delta t_{skew} = \tau_{prop} \cdot (L_{fb} - L_{dest})$$
โดยที่:
$$\tau_{prop} = 6.333\text{ ps/mm}$$
$$|\Delta t_{skew}| \le 20.0\text{ ps}$$

**ขั้นตอนที่ 2: คำนวณความคลาดเคลื่อนความยาวสูงสุดที่ยอมรับได้ ($\Delta L_{max}$)**
$$\Delta L_{max} = \frac{|\Delta t_{skew}|}{\tau_{prop}} = \frac{20.0\text{ ps}}{6.333\text{ ps/mm}} \approx 3.158\text{ mm} \approx 3.16\text{ mm}$$

**ขั้นตอนที่ 3: กำหนดช่วงความยาวที่ปลอดภัย ($L_{fb}$)**
ความยาวอ้างอิง: $L_{dest} = 120.0\text{ mm}$
$$L_{fb,min} = 120.0\text{ mm} - 3.16\text{ mm} = 116.84\text{ mm}$$
$$L_{fb,max} = 120.0\text{ mm} + 3.16\text{ mm} = 123.16\text{ mm}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($116.84\text{ mm} \le L_{fb} \le 123.16\text{ mm}$) ซึ่งสะท้อนข้อจำกัดของกระบวนการออกแบบ PCB High-Speed Routing ที่ต้องกำหนด Tolerance $\pm 3.16\text{ mm}$ ในกฎการเดินสาย (Length Matching Rule)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคำนวณโดยใช้ความเร็วแสงในสุญญากาศ ($c$) โดยลืมคูณตัวหาร $\sqrt{\epsilon_r}$
* ข้อ C ผิด เพราะคิดว่าสัญญาณต้องเดินทางไปกลับ (Round-Trip) ซึ่งในสถาปัตยกรรม External Feedback สัญญาณเดินทางทิศทางเดียวจาก Out ไป In
* ข้อ D มีการตั้งขอบเขตแคบเกินความเป็นจริงโดยไม่สอดคล้องกับงบประมาณ $20\text{ ps}$

---

### คำถามที่ 3: การวิเคราะห์รอบเวลาในการสลับสัญญาณนาฬิกาไร้กลิตช์ด้วย BUFGCTRL (Glitch-Free Switchover Timing & Latency Analysis)
ในระบบรักษาความปลอดภัยเซิร์ฟเวอร์แบบ Fail-Safe วงจรฮาร์ดแวร์ `BUFGCTRL` ทำหน้าที่สลับแหล่งสัญญาณนาฬิกาอัตโนมัติจากสัญญาณนาฬิกาหลัก $CLK_0 = 100.0\text{ MHz}$ ($T_0 = 10.0\text{ ns}$) ไปยังสัญญาณนาฬิกาสำรอง $CLK_1 = 50.0\text{ MHz}$ ($T_1 = 20.0\text{ ns}$) เมื่อเกิดข้อผิดพลาด

กำหนดโครงสร้างการทำงานภายในของ `BUFGCTRL` ในโหมด `SYNC` (Glitch-Free Mode):
* วงจรตรวจจับสัญญาณสลับ `S` ด้วย Double Flip-Flop Synchronizer ทำงานที่ขอบขาลง (Falling Edge) ของ $CLK_0$
* เมื่อผ่านการสลับ สัญญาณเอาต์พุตจะถูกกักขังไว้ที่ระดับ `Low` เป็นเวลาอย่างน้อย $1$ คาบเวลาขอบขาลงของ $CLK_1$ ก่อนที่จะเปิดให้ขอบขาขึ้นสมบูรณ์ลูกแรกของ $CLK_1$ วิ่งออกมา
* ความกว้างพัลส์ระดับต่ำที่ต่ำที่สุดที่เกิดขึ้นระหว่างรอยต่อสลับ (Inter-Clock Dead-Band Time: $t_{dead}$) ขึ้นอยู่กับความสัมพันธ์ของเฟสระหว่างทั้งสองนาฬิกา

หากสัญญาณสั่งสลับ $S$ ถูกกระตุ้นแบบอะซิงโครนัสในจังหวะที่แย่ที่สุด (Worst-Case Timing Alignment):
จงคำนวณหา:
1. เวลาแฝงสูงสุด (Maximum Latency $t_{latency,max}$) นับจากจังหวะที่สัญญาณ $S$ เปลี่ยนแปลง จนกระทั่งขอบขาขึ้นแรกของ $CLK_1$ ปรากฏที่เอาต์พุต
2. ความกว้างพัลส์ต่ำสุดของขอบสัญญาณที่เอาต์พุตเพื่อยืนยันว่าจะไม่เกิด Runt Pulse ($T_{pulse} \ge T_{min}$)

A) $t_{latency,max} \approx 15.0\text{ ns}, \quad T_{pulse,min} = 5.0\text{ ns}$  
B) $t_{latency,max} \approx 45.0\text{ ns}, \quad T_{pulse,min} = 5.0\text{ ns}$  
C) $t_{latency,max} \approx 65.0\text{ ns}, \quad T_{pulse,min} = 10.0\text{ ns}$  
D) $t_{latency,max} \approx 100.0\text{ ns}, \quad T_{pulse,min} = 2.5\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: วิเคราะห์ลำดับสเต็ปการสลับของ `BUFGCTRL` ในโหมด SYNC**
1. **จังหวะรอขอบขาลงของ $CLK_0$ (Disable Current Clock):**
   ในจังหวะแย่ที่สุด สัญญาณ $S$ เปลี่ยนหลังขอบขาลงของ $CLK_0$ พอดี ดังนั้นต้องรอ $CLK_0$ ครบ 1 รอบเต็ม:
   $$t_{wait\_clk0} \le T_0 = 10.0\text{ ns}$$
   จากนั้น Double Synchronizer ขาลงต้องการ $1.5$ ถึง $2$ รอบขาลงของ $CLK_0$:
   $$t_{sync\_clk0} \approx 2 \cdot T_0 = 20.0\text{ ns}$$
2. **จังหวะรอขอบขาลงของ $CLK_1$ (Enable Next Clock):**
   หลังจากเอาต์พุตถูกดึงลงเป็น Low แล้ว วงจรต้องรอขอบขาลงของ $CLK_1$ เพื่อทำการ Unmask:
   ในจังหวะแย่ที่สุด ต้องรอ $CLK_1$ วิ่งมาชนขอบขาลง:
   $$t_{wait\_clk1} \le T_1 = 20.0\text{ ns}$$
3. **จังหวะสร้างขอบขาขึ้นแรกของ $CLK_1$:**
   เมื่อเปิดสวิตช์ที่ขอบขาลงแล้ว ต้องรออีกครึ่งคาบเวลา ($T_1 / 2$) เพื่อให้เกิดขอบขาขึ้นลูกแรก:
   $$t_{rise\_clk1} = \frac{T_1}{2} = \frac{20.0\text{ ns}}{2} = 10.0\text{ ns}$$

**ขั้นตอนที่ 2: รวมเวลาแฝงสูงสุด (Worst-Case Latency)**
$$t_{latency,max} \approx t_{wait\_clk0} + t_{sync\_clk0} + t_{wait\_clk1} + t_{rise\_clk1} \approx 10.0\text{ ns} + 15.0\text{ ns} + 10.0\text{ ns} + 10.0\text{ ns} \approx 45.0\text{ ns}$$

**ขั้นตอนที่ 3: วิเคราะห์ความกว้างพัลส์ต่ำสุด ($T_{pulse,min}$)**
เนื่องจากวงจรเปิดและปิดที่ **ขอบขาลง (Falling Edge)** เสมอ:
* พัลส์ High สุดท้ายของ $CLK_0$ จะมีความกว้างเต็มครึ่งคาบ: $T_{high,clk0} = T_0 / 2 = 5.0\text{ ns}$
* พัลส์ High แรกของ $CLK_1$ จะมีความกว้างเต็มครึ่งคาบ: $T_{high,clk1} = T_1 / 2 = 10.0\text{ ns}$
* ดังนั้นพัลส์ระดับสูงที่แคบที่สุดที่เกิดขึ้นในระบบคือพัลส์ของ $CLK_0$ ซึ่งเท่ากับ $5.0\text{ ns}$ สมบูรณ์แบบ ไม่มีการหดสั้นเป็น Runt Pulse แต่อย่างใด!

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **B** ($t_{latency,max} \approx 45.0\text{ ns}, T_{pulse,min} = 5.0\text{ ns}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะมองข้ามเวลา Synchronization ของสัญญาณนาฬิกาสำรอง ทำให้คำนวณเวลาแฝงต่ำเกินไปมาก
* ข้อ C ผิด เพราะคิดว่า $T_{pulse,min}$ ต้องเท่ากับของ $CLK_1$ ทั้งที่พัลส์ของ $CLK_0$ มีความกว้าง $5.0\text{ ns}$
* ข้อ D ผิด เพราะคิดว่าเกิด Runt Pulse จากการสลับ ซึ่งขัดแย้งกับหลักการทำงานของฮาร์ดแวร์ `BUFGCTRL`
