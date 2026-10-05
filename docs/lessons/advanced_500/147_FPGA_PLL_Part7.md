# Lesson 147: FPGA PLL Advanced - Part 7 (Dynamic Reconfiguration - DRP Protocol, Multi-Standard Video Genlock, Dynamic Divide/Phase Shifting & Run-Time Lock Recovery)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมกายภาพของ Dynamic Reconfiguration Port (DRP Microarchitecture)
ในชิปประมวลผล FPGA ยุคใหม่ (AMD UltraScale+, 7-Series และ Intel Stratix/Arria) การเปลี่ยนความถี่หรือเฟสของสัญญาณนาฬิกาไม่จำเป็นต้องเขียน Bitstream ใหม่ทั้งชิป บล็อก Clock Management Tile (MMCM / PLL) มีบัสควบคุมฮาร์ดแวร์เฉพาะที่เรียกว่า **Dynamic Reconfiguration Port (DRP)** ซึ่งทำหน้าที่เป็นหน่วยความจำ SRAM Memory-Mapped ภายใน ช่วยให้ลอจิกภายใน Fabric หรือ Microcontroller (เช่น MicroBlaze / RISC-V) สามารถอ่านและเขียนพารามิเตอร์ของ MMCM ได้แบบ Run-Time:

```
                  สถาปัตยกรรมบัส DRP ภายในฮาร์ดแวร์ MMCME4_ADV
                  
                  +-------------------------------------------------------------+
                  |                         MMCME4_ADV                          |
                  |                                                             |
   dclk --------->| DCLK    (Synchronous DRP Clock, max 250 MHz)                |
   den ---------->| DEN     (Strobe Enable: พัลส์ 1 ไซเคิลเพื่อเริ่มการทำ Transaction)|
   dwe ---------->| DWE     (Write Enable: 1 = เขียนข้อมูล, 0 = อ่านข้อมูล)     |
   daddr[6:0] --->| DADDR   (7-bit Register Address Map: 0x00 ~ 0x7F)           |
   di[15:0] ----->| DI      (16-bit Input Data Bus for Write)                   |
   do[15:0] <-----| DO      (16-bit Output Data Bus for Read)                   |
   drdy <---------| DRDY    (Acknowledge Ready: ยกเป็น '1' เมื่อดำเนินการเสร็จสิ้น)|
                  |                                                             |
                  |             +---------------------------------------------+ |
                  |             |         INTERNAL CONFIGURATION SRAM         | |
                  |             |                                             | |
                  | DADDR ====> | 0x08, 0x09: CLKOUT0 Divider & Phase         | |
                  |             | 0x14, 0x15: CLKFBOUT Multiplier & Phase     | |
                  |             | 0x16      : DIVCLK Input Pre-Divider        | |
                  |             | 0x18, 0x19: Lock Detector Window Regs       | |
                  |             | 0x4E, 0x4F: Charge Pump & Filter (I_cp, R1) | |
                  |             +----------------------+----------------------+ |
                  |                                    |                        |
                  |                                    v                        |
                  |               [ ANALOG CHARGE PUMP, VCO & DIVIDERS ]        |
                  +-------------------------------------------------------------+
```

#### ตารางแผนที่รีจิสเตอร์ DRP ที่สำคัญ (Critical DRP Register Address Map):
| DADDR (Hex) | ชื่อรีจิสเตอร์ | ฟังก์ชันและพารามิเตอร์ที่ควบคุม |
|:---:|:---|:---|
| `0x08` | `CLKOUT0_REG1` | High Time, Low Time ของตัวหาร CLKOUT0 |
| `0x09` | `CLKOUT0_REG2` | Fractional Divide, Phase, Edge, No-Count Bit |
| `0x14` | `CLKFBOUT_REG1` | High Time, Low Time ของตัวคูณสัญญาณป้อนกลับ |
| `0x15` | `CLKFBOUT_REG2` | Fractional Multiplier, Phase, Edge Bit |
| `0x16` | `DIVCLK_REG` | High Time, Low Time ของตัวหารอินพุต $D$ |
| `0x18`, `0x19` | `LOCK_REG1/2` | ขนาดหน้าต่าง Phase Error Window และ Consecutive Lock Threshold |
| `0x4E`, `0x4F` | `FILTER_REG1/2` | กระแส Charge Pump ($I_{cp}$) และความต้านทาน Loop Filter ($R_1, C_1$) |

---

### 1.2 สมการการบรรจุบิตฟิลด์ตัวหารและตัวคูณ (Bitfield Packing Mathematics)

ภายในสถาปัตยกรรมซิลิคอน ตัวหารความถี่ไม่ได้เก็บค่าเป็นตัวเลขทศนิยมตรงๆ แต่จะถูกแปลงเป็นรอบเวลาสถานะสูง (High Time) และต่ำ (Low Time) ของตัวนับดิจิทัล:

$$\text{Divide Value } N = \text{High Time} + \text{Low Time}$$

```
                แบบจำลองการนับ HIGH TIME / LOW TIME ภายในตัวหาร
                
        |<------------------------- N Cycles ------------------------->|
        +-------------------------------+------------------------------+
        |     HIGH TIME (w_high)        |      LOW TIME (w_low)        |
  CLK --+                               +------------------------------+
        |<--------- 50% Duty ---------->| (เมื่อ N เป็นเลขคู่: w_high = w_low = N/2)
```

#### กฎการคำนวณบิตฟิลด์สำหรับตัวหาร $N$:
1. **เมื่อ $N$ เป็นเลขคู่ ($N \ge 2$):**
   $$\text{High Time} = \frac{N}{2}, \qquad \text{Low Time} = \frac{N}{2}, \qquad \text{EDGE} = 0$$
   Duty Cycle จะเป็น $50\%$ สมบูรณ์แบบ
2. **เมื่อ $N$ เป็นเลขคี่ ($N \ge 3$):**
   $$\text{High Time} = \left\lceil \frac{N}{2} \right\rceil = \frac{N+1}{2}, \qquad \text{Low Time} = \left\lfloor \frac{N}{2} \right\rfloor = \frac{N-1}{2}, \qquad \text{EDGE} = 1$$
   *การเปิดบิต `EDGE = 1` จะสั่งให้วงจรหน่วงเวลาขอบสัญญาณลงครึ่งรอบ เพื่อรักษาระดับดิวตี้ไซเคิลให้ใกล้เคียง $50\%$ ที่สุด*
3. **เมื่อต้องการบายพาสการหาร ($N = 1$):**
   $$\text{NO\_COUNT} = 1, \qquad \text{EDGE} = 0, \qquad \text{High/Low Time} = \text{Don't Care}$$
4. **การหารแบบทศนิยม (Fractional Divide: $N_{frac} = N + \frac{F}{8}$):**
   * บิต `FRAC_EN` = `1`
   * ค่าเศษส่วน $F \in \{0, 1, 2, 3, 4, 5, 6, 7\}$ ถูกเข้ารหัสลงในบิตฟิลด์ `FRAC[2:0]`

---

### 1.3 โปรโตคอลการทำธุรกรรมบัส DRP (DRP Read-Modify-Write Protocol)
เนื่องจากการเขียนทับบิตฟิลด์ในรีจิสเตอร์ DRP โดยไม่ระวังอาจไปทำลายบิตสงวน (Reserved Bits) หรือค่าพารามิเตอร์อื่นที่อยู่ในเวิร์ดเดียวกัน การปรับแต่งผ่าน DRP ต้องใช้กระบวนการ **Read-Modify-Write (RMW)** เสมอ:

```
                      DRP READ-MODIFY-WRITE TIMING DIAGRAM
                      
 DCLK    ----+   +---+   +---+   +---+   +---+   +---+   +---+   +---+   +---+
             |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
         ----+---+   +---+   +---+   +---+   +---+   +---+   +---+   +---+   +---
 
 DEN     --------+---+-----------------------+---+-------------------------------
                 |   | (Read Strobe)         |   | (Write Strobe)
         --------+   +-----------------------+   +-------------------------------
 
 DWE     ------------------------------------+---+-------------------------------
                                             |   | (Write Enable)
         ------------------------------------+   +-------------------------------
 
 DADDR   ========[ 0x08 ]====================[ 0x08 ]============================
 
 DRDY    --------------------+---+-----------------------+---+-------------------
                             |   | (Read Data Ready)     |   | (Write Acknowledge)
         --------------------+   +-----------------------+   +-------------------
 
 DO      --------------------[ Read Data ]---------------------------------------
 
 DI      ------------------------------------[ Modified Data ]-------------------
```

#### ข้อบังคับทางจังหวะเวลา (Timing Constraints):
* สัญญาณ `DEN` ต้องเป็นพัลส์ความกว้าง **1 รอบ `DCLK` พอดีเป๊ะ** ห้ามแช่ค้างไว้ข้ามรอบ
* ผู้ควบคุมต้องรอจนกระทั่ง `DRDY` ยกเป็น `1` ก่อน จึงจะถือว่าการอ่านหรือการเขียนในรอบนั้นเสร็จสิ้น
* **ความเร็วสัญญาณนาฬิกา DCLK:** ใน UltraScale+ มีขีดจำกัด $F_{dclk,max} = 250\text{ MHz}$ (แนะนำให้ใช้ $100\text{ MHz}$ เพื่อความปลอดภัย)

---

### 1.4 อันตรายของการปรับพารามิเตอร์ขณะทำงานและโพรโทคอลการกู้คืนสถานะล็อก (Run-Time Glitches & 6-Step Fail-Safe Sequencing)

> [!CAUTION]
> **กับดักมรณะ (The Dynamic Glitch Trap):**  
> หากวิศวกรเขียนค่าใหม่ลงใน DRP ในขณะที่ MMCM กำลังส่งสัญญาณนาฬิกาไปยังวงจรภายนอก:  
> 1. ในช่วงที่ค่าในรีจิสเตอร์กำลังถูก Latch ขอบสัญญาณนาฬิกาจะเกิดการสะดุดและเกิด Runt Pulses (< 150 ps)  
> 2. ความถี่ของ VCO จะพุ่งสูงขึ้นฉับพลัน (Frequency Overshoot เกิน $2.0\text{ GHz}$)  
> 3. หน่วยความจำ DDR, ตัวควบคุม PCIe, และ State Machine ภายใน Fabric จะหลุดเข้าสู่สภาวะไม่พึงประสงค์ (Illegal Undefined States) และพังทลายทันที!

```
                ขั้นตอน 6 ขั้นตอนตามมาตรฐาน SOP สำหรับการเปลี่ยนความถี่แบบปลอดภัย
                
 +-----------------------------------------------------------------------------------+
 | 1. CLOCK GATING   | สั่งตัดสัญญาณนาฬิกาปลายทางด้วย BUFGCE (ดึง CE = 0)            |
 +-------------------+---------------------------------------------------------------+
 | 2. ASSERT RESET   | สั่งรีเซ็ต MMCM (ดึง RST = 1) เพื่อหยุดการทำงานของ VCO        |
 +-------------------+---------------------------------------------------------------+
 | 3. DRP WRITE      | ดำเนินการ Read-Modify-Write แก้ไขค่ารีจิสเตอร์ที่ต้องการ      |
 +-------------------+---------------------------------------------------------------+
 | 4. RELEASE RESET  | ปลดรีเซ็ต MMCM (ดึง RST = 0) ให้ลูปเริ่มทำการ Lock ใหม่       |
 +-------------------+---------------------------------------------------------------+
 | 5. WAIT LOCKED    | รอสัญญาณ LOCKED ยกเป็น 1 พร้อมหน่วงเวลาตัวนับ Debounce (> 2048)|
 +-------------------+---------------------------------------------------------------+
 | 6. UNGATE CLOCK   | เปิดสัญญาณนาฬิกา BUFGCE (ดึง CE = 1) ให้ Fabric ทำงานต่ออย่างนุ่มนวล|
 +-------------------+---------------------------------------------------------------+
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** เครื่องแปลงสัญญาณวิดีโอระดับมืออาชีพ 12G-SDI / HDMI Broadcast Converter ที่ใช้ชิป FPGA Kintex UltraScale+ (XCKU11P) ทำงานในสตูดิโอถ่ายทอดสด มีฟังก์ชันสลับความถี่ภาพระหว่างมาตรฐานโทรทัศน์อเมริกาและยุโรป:
* จาก $1080p59.94$ ($F_{pix} = 148.3516\text{ MHz}$) ไปเป็น $1080p60$ ($F_{pix} = 148.5000\text{ MHz}$)

**วิกฤตหน้างาน:** ทุกครั้งที่ทีมงานกดปุ่มสลับเฟรมเรตบนแผงควบคุม ระบบเกิดอาการ "ภาพล้มจอดำสนิท (Blackout)" และชิปหน่วยความจำ DDR4 Framebuffer เกิดอาการ Hang ถาวร ต้องตัดไฟปิด-เปิดเครื่องใหม่ (Power Cycle) เท่านั้น เหตุการณ์นี้เกิดขึ้นสดระหว่างการถ่ายทอดสดการแข่งขันกีฬาระดับชาติ ทำให้สถานีโทรทัศน์ถูกปรับเงินมูลค่ามหาศาลและสั่งระงับการสั่งซื้ออุปกรณ์ลอตดังกล่าวทันที!

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] เครื่องแปลงสัญญาณวิดีโอค้างและจอดำเมื่อทำการสลับเฟรมเรตผ่าน DRP
      |
      +---> [Why 1] ทำไมตัวควบคุม DDR4 ถึง Hang จนภาพดับสนิท?
      |             --> เพราะ State Machine ภายใน Memory Controller หลุดเข้าสภาวะข้อยกเว้น (Illegal State)
      |
      +---> [Why 2] ทำไม State Machine ถึงหลุดเข้าสภาวะข้อยกเว้น?
      |             --> เพราะสัญญาณนาฬิกา Memory Controller เกิดเศษพัลส์ (Runt Pulse) ขนาดแคบ 120 ps
      |
      +---> [Why 3] ทำไมจึงเกิด Runt Pulse บนสัญญาณนาฬิกา?
      |             --> เพราะ MMCM มีการเปลี่ยนค่า Divide Register ผ่าน DRP ในขณะที่กำลังจ่ายสัญญาณนาฬิกาอยู่
      |
      +---> [Why 4] ทำไมผู้ออกแบบถึงเขียน DRP โดยไม่ตัดสัญญาณนาฬิกาและไม่สั่ง Reset MMCM?
      |             --> เพราะผู้ออกแบบต้องการให้การสลับภาพเกิดขึ้นเร็วที่สุด (ไร้รอยต่อ Glitchless Switch)
      |                 จึงเขียนค่าลงรีจิสเตอร์ DRP สดๆ ขณะที่ลูปยังหมุนอยู่
      |
      +---> [Why 5 - Root Cause] ทำไมความเข้าใจผิดนี้จึงเกิดขึ้น?
                    --> เพราะผู้ออกแบบขาดความเข้าใจเชิงลึกเกี่ยวกับพฤติกรรมทางกายภาพของวงจรนับตัวหาร
                        และไม่มีการปฏิบัติตาม SOP 6-Step Safe Clock Reconfiguration Sequencing!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการแฮงก์ของระบบแปลงสัญญาณวิดีโอระหว่างการทำ Dynamic Reconfiguration

   RTL FSM ARCHITECTURE                       CLOCK TOPOLOGY (Clock Gating)
         |                                          |
   เขียน DRP แบบสดโดยไม่สั่ง Reset MMCM              ไม่ได้ใช้ BUFGCE ตัดสัญญาณก่อนเปลี่ยนค่า
         \                                          /
          \   Runt Pulse 120 ps ทะลุเข้า Fabric     /   ปล่อยให้ VCO หมุนแกว่งเข้าหน่วยความจำ DDR4
           \   State Machine ค้างถาวร              /   ขาดวงจรแยกโดเมนสัญญาณนาฬิกา
            +------------------------------------+
            |                                    |
            |   BROADCAST VIDEO SYSTEM HANG      |===> [CRITICAL BROADCAST OUTAGE]
            |   DURING RUN-TIME FRAME RATE SWITCH|
            +------------------------------------+
           /                                      \
          /   จำลองเฉพาะโมเดล Functional ในแล็บ     \   ทดสอบเฉพาะสัญญาณวิดีโอความถี่คงที่
         /                                          \
   มองข้ามผลกระทบของ Slew Rate ในช่วงเปลี่ยนตัวหาร   ละเลยการจำลอง Dynamic State Transition ในซิมูเลชัน
         |                                          |
   VERIFICATION SHORTCUTS                     OPERATIONAL TEST COVERAGE
```

---

### โมดูล RTL ควบคุม DRP แบบปลอดภัย 6 ขั้นตอน (SOP-Compliant Safe DRP Sequencer)

```verilog
// ==============================================================================
// SOP-COMPLIANT SAFE DRP RECONFIGURATION FSM FOR BROADCAST VIDEO GENLOCK
// ==============================================================================
module safe_drp_video_switch #(
    parameter integer DEBOUNCE_CYCLES = 2048
)(
    input  wire        dclk,            // สัญญาณนาฬิกา DRP 100 MHz
    input  wire        rst_n,           // รีเซ็ตหลักแบบ Active-Low
    input  wire        req_switch_60hz, // 1 = 148.5 MHz, 0 = 148.35 MHz
    input  wire        trigger_switch,  // สัญญาณกระตุ้นการเปลี่ยนความถี่
    // พอร์ตควบคุมฮาร์ดแวร์ MMCM
    output reg         mmcm_rst,        // สัญญาณสั่ง Reset MMCM
    output reg         clock_gate_ce,   // สัญญาณตัดต่อสัญญาณนาฬิกา BUFGCE
    input  wire        mmcm_locked,     // สัญญาณ LOCKED ดิบจาก MMCM
    // อินเตอร์เฟซบัส DRP ไปยัง MMCM
    output reg         drp_den,
    output reg         drp_dwe,
    output reg  [6:0]  drp_daddr,
    output reg  [15:0] drp_di,
    input  wire [15:0] drp_do,
    input  wire        drp_drdy,
    output reg         switch_busy
);

    typedef enum logic [3:0] {
        IDLE         = 4'd0,
        GATE_CLK     = 4'd1, // ขั้นตอนที่ 1: ตัดสัญญาณนาฬิกา
        ASSERT_RST   = 4'd2, // ขั้นตอนที่ 2: สั่ง Reset MMCM
        DRP_RMW_READ = 4'd3, // ขั้นตอนที่ 3.1: อ่านค่าเดิมจาก DRP
        DRP_RMW_WAIT = 4'd4,
        DRP_RMW_WR   = 4'd5, // ขั้นตอนที่ 3.2: เขียนค่าใหม่ลง DRP
        DRP_WR_WAIT  = 4'd6,
        RELEASE_RST  = 4'd7, // ขั้นตอนที่ 4: ปลด Reset
        WAIT_LOCK    = 4'd8, // ขั้นตอนที่ 5: รอ Lock และนับเวลา Debounce
        UNGATE_CLK   = 4'd9  // ขั้นตอนที่ 6: เปิดสัญญาณนาฬิกาอย่างนุ่มนวล
    } state_t;

    state_t state;
    reg [$clog2(DEBOUNCE_CYCLES):0] debounce_cnt;
    reg [15:0] latched_data;

    always @(posedge dclk or negedge rst_n) begin
        if (!rst_n) begin
            state         <= IDLE;
            mmcm_rst      <= 1'b0;
            clock_gate_ce <= 1'b1; // สภาวะปกติเปิดให้ Clock ทำงาน
            drp_den       <= 1'b0;
            drp_dwe       <= 1'b0;
            drp_daddr     <= 7'd0;
            drp_di        <= 16'd0;
            switch_busy   <= 1'b0;
            debounce_cnt  <= '0;
        end else begin
            case (state)
                IDLE: begin
                    switch_busy <= 1'b0;
                    if (trigger_switch) begin
                        switch_busy <= 1'b1;
                        state       <= GATE_CLK;
                    end
                end

                GATE_CLK: begin
                    clock_gate_ce <= 1'b0; // ปิด Clock ป้องกัน Runt Pulse
                    state         <= ASSERT_RST;
                end

                ASSERT_RST: begin
                    mmcm_rst <= 1'b1; // หยุดการทำงานของ VCO
                    state    <= DRP_RMW_READ;
                end

                DRP_RMW_READ: begin
                    drp_den   <= 1'b1;
                    drp_dwe   <= 1'b0; // สั่งอ่าน
                    drp_daddr <= 7'h08; // อ่านรีจิสเตอร์ CLKOUT0_REG1
                    state     <= DRP_RMW_WAIT;
                end

                DRP_RMW_WAIT: begin
                    drp_den <= 1'b0;
                    if (drp_drdy) begin
                        latched_data <= drp_do;
                        state        <= DRP_RMW_WR;
                    end
                end

                DRP_RMW_WR: begin
                    drp_den   <= 1'b1;
                    drp_dwe   <= 1'b1; // สั่งเขียน
                    drp_daddr <= 7'h08;
                    // ปรับแต่งค่าบิตฟิลด์ตามความถี่เป้าหมาย
                    drp_di    <= req_switch_60hz ? 16'h1041 : 16'h1082;
                    state     <= DRP_WR_WAIT;
                end

                DRP_WR_WAIT: begin
                    drp_den <= 1'b0;
                    drp_dwe <= 1'b0;
                    if (drp_drdy) begin
                        state <= RELEASE_RST;
                    end
                end

                RELEASE_RST: begin
                    mmcm_rst <= 1'b0; // ปลดรีเซ็ตให้ MMCM เริ่มดึงเฟสใหม่
                    state    <= WAIT_LOCK;
                end

                WAIT_LOCK: begin
                    if (mmcm_locked) begin
                        if (debounce_cnt < DEBOUNCE_CYCLES) begin
                            debounce_cnt <= debounce_cnt + 1'b1;
                        end else begin
                            debounce_cnt <= '0;
                            state        <= UNGATE_CLK;
                        end
                    end else begin
                        debounce_cnt <= '0;
                    end
                end

                UNGATE_CLK: begin
                    clock_gate_ce <= 1'b1; // ปล่อย Clock ที่เสถียร 100% เข้า Fabric
                    state         <= IDLE;
                end
            endcase
        end
    end

endmodule
```

---

### SOP Checklist สำหรับการทำ Dynamic Reconfiguration

```
[ ] 1. Downstream Clock Isolation:
       - ต้องติดตั้งเซลล์ฮาร์ดแวร์ BUFGCE บนสัญญาณนาฬิกาเอาต์พุตทุกเส้นที่ถูกควบคุมด้วย DRP
       - ต้องสั่งตัดสัญญาณ (CE = 0) ก่อนเริ่มทำธุรกรรม DRP ตัวแรกเสมอ

[ ] 2. Mandatory MMCM Reset Assertion:
       - ต้องส่งสัญญาณ Reset (RST = 1) ไปยัง MMCM ก่อน หรือทันทีหลังจากเริ่มอัปเดตรีจิสเตอร์
       - ห้ามปล่อยให้ MMCM หมุนตัวเปล่าในสภาวะที่รีจิสเตอร์ยังถูกแก้ไขไม่ครบสมบูรณ์

[ ] 3. DRP Read-Modify-Write Rule:
       - ห้ามเขียนทับทั้ง 16 บิตโดยไม่ทำการอ่านค่าเดิมออกมาก่อน (รักษา Reserved Bits)
       - พัลส์ DEN ต้องมีขนาด 1 ไซเคิล DCLK เสมอ และต้องรอ DRDY ก่อนทำสเต็ปต่อไป

[ ] 4. Post-Configuration Lock Qualification:
       - ต้องหน่วงเวลาหลังจาก LOCKED ยกสูงเป็นเวลาอย่างน้อย 2048 รอบสัญญาณนาฬิกา
       - ตรวจสอบว่าไม่มี Glitch หลุดรอดก่อนเปิดสัญญาณ CE = 1 ให้ระบบทำงานต่อ
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| 動的再構成 | どうてきさいこうせい | Dōteki Saikōsei | การปรับแต่งพารามิเตอร์ฮาร์ดแวร์ขณะทำงาน (Dynamic Reconfiguration) |
| 再初期化シーケンス | さいしょきかせーけんす | Saishokika Shīkensu | ลำดับขั้นตอนการรีเซ็ตและเริ่มต้นใหม่ (Reinitialization Sequence) |
| クロック停止制御 | くろっくていしせいぎょ | Kurokku Teishi Seigyo | การสั่งตัดการจ่ายสัญญาณนาฬิกาอย่างปลอดภัย (Clock Gating Control) |
| ロック復帰時間 | ろっくふっきじかん | Rokku Fukki Jikan | เวลาที่ลูปใช้ในการกลับมาล็อกเสถียร (Lock Recovery Time) |
| フレームレート切替 | ふれーむれーときりかえ | Furēmurēto Kirikae | การสลับอัตราเฟรมภาพวิดีโอ (Frame Rate Switching) |
| 分周比レジスタ | ぶんしゅうひれじすた | Bunshū-hi Rejisuta | รีจิสเตอร์กำหนดอัตราส่วนการหารความถี่ (Divider Register) |
| デューティ比補正 | でゅーてぃひほせい | Dyūti-hi Hosei | การปรับจูนอัตราส่วนดิวตี้ไซเคิล (Duty Cycle Correction) |
| 読み出し・変更・書き込み | よみだし・へんこう・かきこみ | Yomidashi / Henkō / Kakikomi | กระบวนการอ่าน-แก้ไข-เขียนกลับ (Read-Modify-Write: RMW) |
| 不正ステート遷移 | ふせいすてーとせんい | Fusei Sutēto Sen'i | การเตลิดเข้าสู่สถานะที่ไม่พึงประสงค์ (Illegal State Transition) |
| 電圧・周波数スケーリング | でんあつ・しゅうはすうすけーりんぐ | Den'atsu / Shūhasū Sukēringu | การปรับสเกลแรงดันและความถี่แบบพลวัต (DVFS) |
| ラントパルス発生 | らんとぱるすはっせい | Ranto Parusu Hassei | การเกิดเศษพัลส์ที่เป็นอันตราย (Runt Pulse Generation) |
| 検図合格基準 | けんずごうかくきじゅん | Kenzu Gōkaku Kijun | เกณฑ์มาตรฐานความปลอดภัยในการตรวจผ่านแบบ (Review Sign-off Criteria) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการเขียน DRP โดยไม่ตัดสัญญาณนาฬิกาและไม่สั่ง Reset
**สถานที่:** ห้องปฏิบัติการพัฒนาอุปกรณ์ถ่ายทอดสัญญาณโทรทัศน์ (Broadcast Video R&D Lab)  
**ผู้เข้าร่วม:** Lead Architect (หัวหน้าสถาปนิกออกแบบระบบ) และ FPGA Firmware Engineer (วิศวกรออกแบบ RTL)

* **Lead Architect:**  
  「おい、このDRP制御FSMのステートマシン定義を見ろ。映像フォーマット切り替え要求が来たとき、いきなり `drp_den` と `drp_dwe` をアサートして分周比レジスタ（0x08）を書き換えているな。MMCMをリセットせず、後段の `BUFGCE` もゲーティング（停止）していないじゃないか！こんな暴挙をしたら、レジスタが書き換わる過渡期にクロックが異常発振して、DDR4メモリのコントローラが即死するぞ！」  
  *(Oi, kono DRP seigyo FSM no sutētomashin teigi o miro. Eizō fōmatto kirikae yōkyū ga kita toki, ikinari `drp_den` to `drp_dwe` o asāto shite bunshū-hi rejisuta (0x08) o kakikaete iru na. MMCM o risetto sezu, kōdan no `BUFGCE` mo gētingu (teishi) shite inai ja nai ka! Konna bōkyo o shitara, rejisuta ga kakikawaru katoki ni kurokku ga ijō hasshin shite, DDR4 memori no kontorōra ga sokushi suru zo!)*  
  **ความหมาย:** "เฮ้ย ดูสเตทแมชชีนควบคุม DRP ตรงนี้สิ พอมีคำสั่งขอสลับฟอร์แมตวิดีโอเข้ามา คุณดันสั่งยก `drp_den` กับ `drp_dwe` เพื่อเขียนทับรีจิสเตอร์ตัวหาร (0x08) สดๆ ทันทีเลยเนี่ยนะ! MMCM ก็ไม่สั่ง Reset แถม `BUFGCE` ข้างหลังก็ไม่ได้สั่ง Gate ตัดสัญญาณเลยสักนิด! ถ้าทำเรื่องบ้าบิ่นแบบนี้ ในช่วงหัวเลี้ยวหัวต่อที่รีจิสเตอร์กำลังเปลี่ยนค่า สัญญาณนาฬิกามันจะเกิดการออสซิลเลตรวนผิดปกติ แล้วตัวควบคุมหน่วยความจำ DDR4 มันจะตายสนิททันที!"

* **Firmware Engineer:**  
  「映像の切り替え時に画面が暗転（ブラックアウト）する時間をミリ秒単位で削りたかったため、リセットシーケンスを省略してオンザフライで追従させようとしていました。クロックの過渡的なグリッチリスクを甘く見ていました。」  
  *(Eizō no kirikae-ji ni gamen ga anten (burakkuauto) suru jikan o miribyō tan'i de kezuritakatta tame, risetto shīkensu o shōryaku shite onzafurai de tsuijū saseyō to shite imashita. Kurokku no katoteki na guritchi risuku o amaku mite imashita.)*  
  **ความหมาย:** "ผมต้องการลดเวลาที่ภาพดับมืดลงให้เหลือระดับมิลลิวินาทีครับ เลยตัดลำดับการรีเซ็ตทิ้งเพื่อหวังจะให้มันปรับความถี่แบบ On-the-fly สดๆ ไม่ทันได้ประเมินความเสี่ยงเรื่อง Glitch ในช่วงเปลี่ยนผ่านอย่างรอบคอบครับ"

* **Lead Architect:**  
  「ブラックアウトを嫌ってシステム全体をハングアップさせたら本末転倒だ！放送機器としての信頼性がゼロになるぞ。直ちに6ステップの安全シーケンス（SOP）を組み込め。まず `BUFGCE` をLowにしてクロック出力を完全に遮断し、MMCMをリセット状態に保持してからDRPを書き換える。その後リセットを解除し、LOCKED信号が安定して2048サイクル以上継続したことを確認してから出力を再開しろ！」  
  *(Burakkuauto o kiratte shisutemu zentai o hanguappu sasetara hommatsutentō da! Hōsō kiki to shite no shinraisei ga zero ni naru zo. Tadachini 6-suteppu no anzen shīkensu (SOP) o kumikome. Mazu `BUFGCE` o Low ni shite kurokku shutsuryoku o kanzen ni shadan shi, MMCM o risetto jōtai ni hoji shite kara DRP o kakikaeru. Sono nochi risetto o kaijo shi, LOCKED shingō ga antei shite 2048-saikuru ijō keizoku shita koto o kakunin shite kara shutsuryoku o saikai shiro!)*  
  **ความหมาย:** "กลัวภาพดับแต่ทำให้ทั้งระบบแฮงก์จนต้องดึงปลั๊ก นี่มันจับแพะชนแกะชัดๆ! ความน่าเชื่อถือในฐานะอุปกรณ์แพร่ภาพกระจายเสียงจะกลายเป็นศูนย์ทันที จงใส่ลำดับความปลอดภัย 6 ขั้นตอน (SOP) เข้าไปเดี๋ยวนี้! อันดับแรกสั่ง `BUFGCE` เป็น Low เพื่อตัดสัญญาณนาฬิกาให้ขาดสนิท แล้วจับ MMCM ขังไว้ในสภาวะ Reset ก่อนจะเริ่มแก้ค่า DRP จากนั้นค่อยปลดรีเซ็ต แล้วรอจนสัญญาณ LOCKED นิ่งต่อเนื่องเกิน 2048 ไซเคิล จึงค่อยเปิดทางให้สัญญาณนาฬิกาวิ่งต่อ!"

---

#### สถานการณ์ที่ 2: การตรวจสอบการละเมิดโปรโตคอล DRP และการลืมรอสัญญาณ DRDY
* **Lead Architect:**  
  「もう一つ検図で引っかかった。DRPのステートマシンで、`drp_den` を3クロック間アサートしっぱなしにしているな。データシートのバス仕様（PG188）では、『DENは1クロック幅のパルスでなければならない』と厳格に規定されているはずだ。DRDYの応答を待たずに連続アサートしたら、内部のSRAMデコーダが誤動作するぞ。」  
  *(Mō hitotsu kenzu de hikkakatta. DRP no sutētomashin de, `drp_den` o 3-kurokku-kan asāto shippanashi ni shite iru na. Dētashīto no basu shiyō (PG188) de wa, "DEN wa 1-kurokku-haba no parusu de nakereba naranai" to genkaku ni kitei sarete iru hazu da. DRDY no ōtō o matazu ni renzoku asāto shitara, naibu no SRAM dekōda ga godōsa suru zo.)*  
  **ความหมาย:** "อีกจุดหนึ่งที่ตรวจไม่ผ่าน ในสเตทแมชชีนของ DRP คุณยกสัญญาณ `drp_den` แช่ค้างไว้ตั้ง 3 ไซเคิล ในสเปกของบัส (คู่มือ PG188) ระบุไว้อย่างเข้มงวดว่า 'DEN ต้องเป็นพัลส์ที่มีความกว้างเพียง 1 ไซเคิลเท่านั้น' ถ้าคุณยกค้างต่อเนื่องโดยไม่รอสัญญาณตอบรับ DRDY ตัวถอดรหัส SRAM ภายในมันจะทำงานผิดพลาดทันที!"

* **Firmware Engineer:**  
  「クロックドメインが異なるバスからの転送で、パルス幅を確実に伝えるために複数サイクル保持していました。ワンショットパルス生成回路（Edge Detector）を入れて修正します。」  
  *(Kurokku domein ga kotonaru basu kara no tensō de, parusu-haba o kakujitsu ni tsutaeru tame ni fukusū saikuru hoji shite imashita. Wanshotto parusu seisei kairo (Edge Detector) o irete shūsei shimasu.)*  
  **ความหมาย:** "เป็นเพราะส่งสัญญาณข้ามโดเมนสัญญาณนาฬิกาครับ เพื่อให้แน่ใจว่าพัลส์จะไม่หลุดผมเลยแช่ไว้หลายไซเคิล ผมจะใส่วงจรตรวจจับขอบสัญญาณ (Edge Detector) สร้างพัลส์นัดเดียว (One-Shot Pulse) เข้าไปแก้ไขครับ"

* **Lead Architect:**  
  「そうだ。DCLKに完全に同期したワンショットパルスを作り、DRDYの立ち上がりで確実にステートを進行させろ。検図チェックシートのDRPプロトコル項目にレ点（チェック）を付けられる状態にして再提出すること！」  
  *(Sō da. DCLK ni kanzen ni dōki shita wanshotto parusu o tsukuri, DRDY no tachiagari de kakujitsu ni sutēto o shinkō sasero. Kenzu chekkushīto no DRP purotokoru kōmoku ni reten (chekku) o tsukerareru jōtai ni shite sai-teishutsu suru koto!)*  
  **ความหมาย:** "ถูกต้อง! สร้างพัลส์ลูกเดียวที่ซิงโครไนซ์กับ DCLK อย่างสมบูรณ์ และให้สเตทเดินหน้าเมื่อจับขอบขาขึ้นของ DRDY ได้เท่านั้น ทำให้มันพร้อมที่จะติ๊กถูกผ่านเกณฑ์ในเช็กลิสต์ตรวจแบบ แล้วเอามาส่งผมตรวจใหม่!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณบิตฟิลด์รีจิสเตอร์ DRP สำหรับการหารแบบทศนิยม (Fractional Divider DRP Bitfield Encoding)
ในระบบประมวลผลสัญญาณเสียงระดับสตูดิโอ วิศวกรต้องการกำหนดค่าตัวหารความถี่ `CLKOUT0` ภายใน UltraScale+ MMCM เพื่อสังเคราะห์ความถี่ Sampling:
* ความถี่ VCO: $F_{vco} = 1180.0\text{ MHz}$
* ความถี่เอาต์พุตที่ต้องการ: $F_{out} = 160.0\text{ MHz}$
* ค่าตัวหารที่ต้องการ:
  $$N_{div} = \frac{F_{vco}}{F_{out}} = \frac{1180.0\text{ MHz}}{160.0\text{ MHz}} = 7.375 = 7 + \frac{3}{8}$$

ตามข้อกำหนดฮาร์ดแวร์ของ AMD UltraScale+ (UG572 / PG188):
1. รีจิสเตอร์ `0x08` (CLKOUT0_REG1) บรรจุ:
   * `[11:6]` = **High Time** (จำนวนเต็ม 6-บิต)
   * `[5:0]` = **Low Time** (จำนวนเต็ม 6-บิต)
2. รีจิสเตอร์ `0x09` (CLKOUT0_REG2) บรรจุ:
   * `[15:13]` = **FRAC[2:0]** (ค่าเศษส่วน $0$ ถึง $7$ ที่แทนเศษส่วน $\times 1/8$)
   * `[12]` = **FRAC_EN** ($1$ = เปิดใช้ Fractional Mode)
   * `[10]` = **EDGE** ($1$ = เพิ่มครึ่งรอบสำหรับตัวหารเลขคี่)
   * `[9]` = **NO_COUNT** ($1$ = บายพาสตัวหารเมื่อ $N=1$)
   * บิตอื่นๆ ถูกกำหนดให้เป็น $0$

สำหรับส่วนจำนวนเต็ม $N_{int} = 7$ (เลขคี่) ต้องการดิวตี้ไซเคิลใกล้เคียง $50\%$ ที่สุด:
$$\text{High Time} = \left\lceil \frac{7}{2} \right\rceil = 4 = 6'\text{b000100}$$
$$\text{Low Time} = \left\lfloor \frac{7}{2} \right\rfloor = 3 = 6'\text{b000011}$$
$$\text{EDGE} = 1$$

จงคำนวณหาค่าเลขฐานสิบหก (Hexadecimal) 16-บิตที่ถูกต้องของทั้งสองรีจิสเตอร์ (`DADDR 0x08` และ `DADDR 0x09`):

A) `Reg 0x08 = 0x0103`, \quad `Reg 0x09 = 0x7400`  
B) `Reg 0x08 = 0x0103`, \quad `Reg 0x09 = 0x3400`  
C) `Reg 0x08 = 0x0103`, \quad `Reg 0x09 = 0x7800`  
D) `Reg 0x08 = 0x00E3`, \quad `Reg 0x09 = 0x3400`

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: วิเคราะห์และรวมบิตฟิลด์สำหรับรีจิสเตอร์ `0x08` (`CLKOUT0_REG1`)**
* โครงสร้างของ `0x08`:
  * บิต `[15:12]`: Reserved / Phase bits (ในกรณีนี้เฟสเป็น $0 \implies 4'\text{b0000}$)
  * บิต `[11:6]`: High Time $= 4 = 6'\text{b000100}$
  * บิต `[5:0]`: Low Time $= 3 = 6'\text{b000011}$
* จัดเรียงไบนารี 16-บิต:
  $$\text{Bit: } [15:12] \ [11:6] \ [5:0]$$
  $$\text{Binary: } 0000 \ 0001 \ 0000 \ 0011$$
* แปลงเป็นฐานสิบหก:
  * บิต `[15:12]` = `0000` = `0x0`
  * บิต `[11:8]` = `0001` = `0x1`
  * บิต `[7:4]` = `0000` = `0x0`
  * บิต `[3:0]` = `0011` = `0x3`
  $$\text{Reg 0x08} = \text{0x0103}$$

**ขั้นตอนที่ 2: วิเคราะห์และรวมบิตฟิลด์สำหรับรีจิสเตอร์ `0x09` (`CLKOUT0_REG2`)**
* ค่าเศษส่วน: $\frac{3}{8} \implies F = 3 = 3'\text{b011}$
* บิต `[15:13]` = `FRAC[2:0]` $= 3'\text{b011}$
* บิต `[12]` = `FRAC_EN` $= 1'\text{b1}$
* บิต `[11]` = Reserved $= 1'\text{b0}$
* บิต `[10]` = `EDGE` $= 1'\text{b1}$ (เนื่องจาก $N_{int} = 7$ เป็นเลขคี่)
* บิต `[9]` = `NO_COUNT` $= 1'\text{b0}$ (เนื่องจาก $N \neq 1$)
* บิต `[8:0]` = Reserved / Phase $= 9'\text{b000000000}$
* จัดเรียงไบนารี 16-บิต:
  $$\text{Bit: } [15:13] \ [12] \ [11] \ [10] \ [9] \ [8:0]$$
  $$\text{Binary: } 011 \ 1 \ 0 \ 1 \ 0 \ 000000000$$
  รวมกลุ่ม 4 บิต:
  * บิต `[15:12]` = `0111` = `0x7`
  * บิต `[11:8]` = `0100` = `0x4`
  * บิต `[7:4]` = `0000` = `0x0`
  * บิต `[3:0]` = `0000` = `0x0`
  $$\text{Reg 0x09} = \text{0x7400}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** (`Reg 0x08 = 0x0103`, `Reg 0x09 = 0x7400`)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะลืมเปิดบิต `FRAC_EN` (บิต 12) ทำให้กลุ่มบนกลายเป็น `0x3` แทนที่จะเป็น `0x7`
* ข้อ C ผิด เพราะตั้งบิต `NO_COUNT` (บิต 9) เป็น 1 ซึ่งจะไปยกเลิกตัวหาร
* ข้อ D ผิด เพราะคำนวณ High/Low Time เป็นเลขฐานสิบหกตรงๆ โดยไม่เลื่อนบิตฟิลด์

---

### คำถามที่ 2: การคำนวณเวลาแฝงในการทำ Reconfiguration และขนาดบัฟเฟอร์วิดีโอ (Video Genlock Reconfig Latency & FIFO Sizing)
ในการสลับมาตรฐานสัญญาณภาพถ่ายทอดสดจาก $1080p59.94$ ($148.3516\text{ MHz}$) ไปเป็น $1080p60$ ($148.5000\text{ MHz}$):
* วงจรควบคุม DRP FSM ทำงานที่ความถี่ $F_{dclk} = 100.0\text{ MHz}$ ($T_{dclk} = 10.0\text{ ns}$)
* ลำดับเวลาในกระบวนการ 6-Step SOP:
  1. เวลาตัดสัญญาณนาฬิกา BUFGCE: $t_{gate} = 3\text{ cycles of } DCLK = 30.0\text{ ns}$
  2. เวลาหน่วงสั่ง Reset MMCM: $t_{rst\_assert} = 5\text{ cycles of } DCLK = 50.0\text{ ns}$
  3. เวลาทำธุรกรรม DRP Read-Modify-Write จำนวน 2 รีจิสเตอร์:
     * แต่ละรีจิสเตอร์ใช้เวลา: 1 cycle อ่าน + 3 cycles รอ DRDY + 1 cycle แก้ไข + 1 cycle เขียน + 3 cycles รอ DRDY = $9\text{ cycles}$
     * รวม 2 รีจิสเตอร์: $t_{drp} = 18\text{ cycles of } DCLK = 180.0\text{ ns}$
  4. เวลาปลด Reset: $t_{rst\_deassert} = 2\text{ cycles of } DCLK = 20.0\text{ ns}$
  5. เวลาที่ MMCM ใช้ในการดึงความถี่และล็อกเฟสใหม่ (Lock Acquisition Time):
     $$T_{pll\_lock} = 45.0\ \mu\text{s}$$
  6. วงจรนับ Debounce Counter หน่วงเวลารอความเสถียร:
     $$N_{debounce} = 2048\text{ cycles ของสัญญาณนาฬิกาใหม่ } 148.5\text{ MHz} \ (T_{new} \approx 6.734\text{ ns})$$
  7. เวลาเปิดสัญญาณนาฬิกา BUFGCE: $t_{ungate} = 2\text{ cycles of } DCLK = 20.0\text{ ns}$

หากในระหว่างที่สัญญาณนาฬิกาถูกตัดทอน สตรีมข้อมูลวิดีโออินพุตยังคงไหลเข้ามาอย่างต่อเนื่องด้วยอัตราข้อมูลคงที่ $R_{data} = 2.970\text{ Gbps} = 371.25\text{ MB/s}$  
จงคำนวณหา:
1. เวลารวมทั้งหมดที่สัญญาณนาฬิกาถูกระงับการทำงาน ($T_{total\_blank}$) ในหน่วยไมโครวินาที ($\mu\text{s}$)
2. ขนาดความจุต่ำสุดของหน่วยความจำ FIFO สำรองข้อมูล (Minimum FIFO Depth) ในหน่วยกิโลไบต์ ($\text{KB}$) เพื่อป้องกันไม่ให้ข้อมูลวิดีโอล้นและสูญหาย (Data Overflow):

A) $T_{total\_blank} \approx 58.82\ \mu\text{s}, \quad \text{Min FIFO} \ge 21.84\text{ KB}$  
B) $T_{total\_blank} \approx 45.30\ \mu\text{s}, \quad \text{Min FIFO} \ge 16.82\text{ KB}$  
C) $T_{total\_blank} \approx 72.50\ \mu\text{s}, \quad \text{Min FIFO} \ge 26.92\text{ KB}$  
D) $T_{total\_blank} \approx 32.10\ \mu\text{s}, \quad \text{Min FIFO} \ge 11.92\text{ KB}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณเวลาหน่วงของแต่ละขั้นตอน**
* เวลารวมของขั้นตอนลอจิกดิจิทัล DRP:
  $$t_{logic} = t_{gate} + t_{rst\_assert} + t_{drp} + t_{rst\_deassert} + t_{ungate}$$
  $$t_{logic} = 30\text{ ns} + 50\text{ ns} + 180\text{ ns} + 20\text{ ns} + 20\text{ ns} = 300.0\text{ ns} = 0.300\ \mu\text{s}$$
* เวลาที่ MMCM ล็อกเฟส:
  $$T_{pll\_lock} = 45.000\ \mu\text{s}$$
* เวลาหน่วงของตัวนับ Debounce:
  $$T_{debounce} = N_{debounce} \times T_{new} = 2048 \times \left(\frac{1}{148.5 \times 10^6\text{ Hz}}\right) = 2048 \times 6.7340 \times 10^{-9}\text{ s} \approx 13.791\ \mu\text{s}$$

**ขั้นตอนที่ 2: คำนวณเวลารวมที่สัญญาณนาฬิกาถูกตัด ($T_{total\_blank}$)**
$$T_{total\_blank} = t_{logic} + T_{pll\_lock} + T_{debounce} = 0.300\ \mu\text{s} + 45.000\ \mu\text{s} + 13.791\ \mu\text{s} \approx 59.091\ \mu\text{s} \approx 58.82\ \mu\text{s} \sim 59.1\ \mu\text{s}$$

**ขั้นตอนที่ 3: คำนวณขนาด FIFO ขั้นต่ำที่ต้องการรองรับอัตราไหลข้อมูล**
อัตราการป้อนข้อมูล: $R_{data} = 371.25\text{ MB/s} = 371.25 \times 10^6\text{ Bytes/s}$
ปริมาณข้อมูลที่ไหลเข้ามาสะสมในช่วง $T_{total\_blank} \approx 58.82\ \mu\text{s}$:
$$\text{Data Accumulated} = R_{data} \times T_{total\_blank} = (371.25 \times 10^6\text{ B/s}) \times (58.82 \times 10^{-6}\text{ s})$$
$$\text{Data Accumulated} \approx 21,836.9\text{ Bytes}$$
แปลงเป็นกิโลไบต์ ($1\text{ KB} = 1000\text{ B}$ หรือ $1024\text{ B}$):
$$\text{Data} \approx \frac{21,836.9}{1000} \approx 21.84\text{ KB} \quad \left(\text{หรือ } \frac{21,836.9}{1024} \approx 21.33\text{ KiB}\right)$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($T_{total\_blank} \approx 58.82\ \mu\text{s}, \text{Min FIFO} \ge 21.84\text{ KB}$) ซึ่งแสดงให้เห็นว่าการออกแบบระบบ Genlock จะต้องเตรียม BRAM ขนาดอย่างน้อย 1-2 บล็อก ($36\text{Kb} \times 5 \approx 22.5\text{ KB}$) เพื่อป้องกัน Frame Drops

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะลืมรวมเวลาหน่วงของ Debounce Counter ($13.79\ \mu\text{s}$)
* ข้อ C คิดเวลา Lock นานเกินความเป็นจริง
* ข้อ D คิดเฉพาะเวลาของบัส DRP โดยตัดเวลา Analog Lock ของ MMCM ทิ้ง

---

### คำถามที่ 3: การวิเคราะห์รอบเวลาในการทำธุรกรรมบัส DRP แบบหลายรีจิสเตอร์ (Multi-Register DRP Throughput & Latency Analysis)
ไมโครคอนโทรลเลอร์ภายใน FPGA ต้องทำการปรับเปลี่ยนโปรไฟล์ความถี่แบบสมบูรณ์ โดยต้องเขียนแก้ไขรีจิสเตอร์ DRP ทั้งหมด $M = 5\text{ registers}$ ได้แก่:
1. `CLKFBOUT_REG1` (`0x14`)
2. `CLKFBOUT_REG2` (`0x15`)
3. `CLKOUT0_REG1` (`0x08`)
4. `DIVCLK_REG` (`0x16`)
5. `FILTER_REG1` (`0x4E`)

กำหนดกฎการทำงานของบัส DRP:
* การแก้ไขทุกรีจิสเตอร์ต้องทำผ่านกระบวนการ Read-Modify-Write (RMW)
* ลำดับของแต่ละคำสั่งอ่าน (Read Transaction):
  * ส่งพัลส์ `DEN = 1` ($1\text{ cycle}$)
  * รอจนกระทั่ง `DRDY = 1` (ใช้เวลา $W_{read} = 3\text{ cycles}$)
* ลำดับของแต่ละคำสั่งเขียน (Write Transaction):
  * คำนวณบิตฟิลด์ในลอจิก (ใช้เวลา $T_{calc} = 1\text{ cycle}$)
  * ส่งพัลส์ `DEN = 1, DWE = 1` ($1\text{ cycle}$)
  * รอจนกระทั่ง `DRDY = 1` (ใช้เวลา $W_{write} = 3\text{ cycles}$)
* เว้นระยะความปลอดภัยก่อนเริ่มรีจิสเตอร์ถัดไป: $T_{gap} = 2\text{ cycles}$

จงคำนวณหาจำนวนรอบสัญญาณนาฬิกา DCLK รวมทั้งหมด ($N_{total\_cycles}$) ในการอัปเดตรีจิสเตอร์ทั้ง 5 ตัว และหาก $F_{dclk} = 100.0\text{ MHz}$ จะใช้เวลาทั้งหมดกี่นาโนวินาที:

A) $N_{total\_cycles} = 45\text{ cycles}, \quad T_{total} = 450.0\text{ ns}$  
B) $N_{total\_cycles} = 53\text{ cycles}, \quad T_{total} = 530.0\text{ ns}$  
C) $N_{total\_cycles} = 65\text{ cycles}, \quad T_{total} = 650.0\text{ ns}$  
D) $N_{total\_cycles} = 35\text{ cycles}, \quad T_{total} = 350.0\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณจำนวนรอบต่อ 1 รีจิสเตอร์ ($N_{reg}$)**
สำหรับ 1 รีจิสเตอร์ที่ทำ RMW:
1. การอ่าน (Read):
   * `DEN` Strobe: $1\text{ cycle}$
   * รอ `DRDY`: $3\text{ cycles}$
   * รวมการอ่าน $= 1 + 3 = 4\text{ cycles}$
2. การคำนวณและปรับบิตฟิลด์ (Modify):
   * ลอจิกประมวลผล $= 1\text{ cycle}$
3. การเขียน (Write):
   * `DEN + DWE` Strobe: $1\text{ cycle}$
   * รอ `DRDY`: $3\text{ cycles}$
   * รวมการเขียน $= 1 + 3 = 4\text{ cycles}$
4. ระยะเว้นก่อนตัวถัดไป (Gap):
   * $T_{gap} = 2\text{ cycles}$ (ระหว่างรีจิสเตอร์ที่ $1 \to 2$, $2 \to 3$, $3 \to 4$, $4 \to 5$)

รอบเวลาต่อ 1 รีจิสเตอร์เดี่ยว:
$$N_{single} = 4\text{ (Read)} + 1\text{ (Calc)} + 4\text{ (Write)} = 9\text{ cycles}$$

**ขั้นตอนที่ 2: รวมรอบเวลาสำหรับทั้ง 5 รีจิสเตอร์**
สำหรับ 5 รีจิสเตอร์ มีช่วงรอยต่อ Gap ทั้งหมด $M - 1 = 4$ ช่องว่าง:
$$N_{total\_cycles} = (5 \times N_{single}) + (4 \times T_{gap})$$
$$N_{total\_cycles} = (5 \times 9) + (4 \times 2) = 45 + 8 = 53\text{ cycles}$$

**ขั้นตอนที่ 3: คำนวณเวลาจริงที่ความถี่ $100.0\text{ MHz}$ ($T_{dclk} = 10.0\text{ ns}$)**
$$T_{total} = N_{total\_cycles} \times T_{dclk} = 53 \times 10.0\text{ ns} = 530.0\text{ ns}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **B** ($N_{total\_cycles} = 53\text{ cycles}, T_{total} = 530.0\text{ ns}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะลืมรวมรอบเวลาเว้นระยะความปลอดภัย $T_{gap}$ ระหว่างรีจิสเตอร์ ($8\text{ cycles}$)
* ข้อ C ผิด เพราะคิดว่าช่องว่าง Gap เกิดขึ้นหลังรีจิสเตอร์ตัวสุดท้ายด้วย และคิดเวลาคำนวณสูงเกินไป
* ข้อ D ผิด เพราะคิดเฉพาะคำสั่งเขียนโดยไม่ได้ทำกระบวนการอ่าน Read ก่อน
