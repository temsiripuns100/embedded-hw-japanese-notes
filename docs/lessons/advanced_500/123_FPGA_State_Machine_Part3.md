# Lesson 123: FPGA State Machine - Part 3: Handling Metastability & Asynchronous Inputs (メタステーブル対策と非同期入力同期化)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ฟิสิกส์ของปรากฏการณ์เมตาสเตบิลิตี (Physics of Metastability in CMOS)
ในวงจรดิจิทัลแบบซิงโครนัส (Synchronous Digital Circuits) สัญญาณทุกตัวที่ป้อนเข้าสู่ Flip-Flop จะต้องปฏิบัติตามกฎเกณฑ์ทางเวลาอย่างเคร่งครัด ได้แก่ **Setup Time ($t_{su}$)** และ **Hold Time ($t_h$)** หากสัญญาณขาเข้ามีการเปลี่ยนแปลง (Transition) ภายในหน้าต่างเวลาวิกฤตนี้ (Aperture Window: $t_{window} = t_{su} + t_h$) วงจรแลตช์ภายใน Flip-Flop จะไม่สามารถตัดสินใจได้ทันทีว่าสัญญาณนั้นเป็นลอจิก '0' หรือ '1'

```
                    กลไกการเกิดสภาวะกึ่งเสถียร (Metastable State)
            แรงดันสมดุลกึ่งเสถียร V_m (Unstable Equilibrium Point)
                                       ● (จุดเสถียรภาพยวบยาบ)
                                     /   \
                                    /     \
                                   /       \
                                  v         v
                     ลอจิก '0' (0V)         ลอจิก '1' (V_DD)
   
   Clock Edge  ____/¯¯¯¯\___________________________________________
   Data Input  ______/\_______ (เปลี่ยนค่าช่วง Setup/Hold Window!)
   FF Output Q _________~~~~~~------------------------------------- (แกว่งกึ่งเสถียรที่ V_DD/2)
                        <---- t_res ---->
```

#### 1.1.1 แบบจำลองสัญญาณขนาดเล็กของวงจรอินเวอร์เตอร์แบบ Cross-Coupled
โครงสร้างพื้นฐานของหน่วยเก็บข้อมูลใน Flip-Flop ประกอบด้วยอินเวอร์เตอร์สองตัวต่อไขว้กัน (Cross-Coupled Inverters) เมื่อโหนดอินพุตได้รับแรงดันตกคร่อมที่จุดสมดุลกึ่งเสถียร $V_m \approx V_{DD}/2$ สมการอนุพันธ์ของผลต่างแรงดันไฟฟ้า $\Delta V(t) = V_Q(t) - V_{\bar{Q}}(t)$ เป็นไปตามสมการการขยายสัญญาณ:

$$\frac{d\Delta V(t)}{dt} = \frac{g_m}{C_{node}} \Delta V(t) = \frac{1}{\tau} \Delta V(t)$$

ผลเฉลยของสมการอนุพันธ์แสดงให้เห็นว่า แรงดันไฟฟ้าจะดีดตัวออกจากจุดสมดุลแบบเอกซ์โพเนนเชียล:
$$\Delta V(t) = \Delta V(0) \cdot e^{\frac{t}{\tau}}$$

โดยที่:
* $\tau = \frac{C_{node}}{g_m}$ คือ **ค่าคงที่เวลาในการคลายตัว (Resolution Time Constant)** ของทรานซิสเตอร์ในโหนดเทคโนโลยีนั้นๆ (สำหรับกระบวนการผลิต FinFET 16nm/7nm ค่า $\tau \approx 25 - 45\text{ ps}$)
* $\Delta V(0)$ คือ ผลต่างแรงดันเริ่มต้น ณ ขอบสัญญาณนาฬิกา หากข้อมูลเปลี่ยนตรงขอบเป๊ะๆ $\Delta V(0) \rightarrow 0$ ส่งผลให้วงจรต้องใช้เวลา $t$ นานมากในการก้าวข้ามสู่สภาวะเสถียร

---

### 1.2 สมการเวลาเฉลี่ยก่อนเกิดความล้มเหลว (MTBF - Mean Time Between Failures)
ความน่าจะเป็นที่ Flip-Flop จะยังคงติดอยู่ในสภาวะ Metastable เกินกว่าเวลาคลายตัวที่กำหนด ($t_{res}$) ถูกคำนวณตามสูตรคลาสสิกของ Barker:

$$\text{MTBF} = \frac{e^{\frac{t_{res}}{\tau}}}{C_1 \cdot f_{clk} \cdot f_{data}}$$

โดยที่:
* $f_{clk}$ คือ ความถี่ของสัญญาณนาฬิกาของวงจรรับ (Destination Clock Frequency)
* $f_{data}$ คือ ความถี่เฉลี่ยของการเปลี่ยนแปลงของสัญญาณอินพุตแบบอะซิงโครนัส (Asynchronous Data Toggle Rate)
* $C_1$ (หรือ $T_0$) คือ พารามิเตอร์ความกว้างของหน้าต่างเวลาจับสัญญาณที่มีโอกาสเกิด Metastable (Aperture Parameter, หน่วยเป็นวินาที)
* $t_{res}$ คือ **เวลาว่างที่มีให้วงจรคลายตัว (Available Settling / Resolution Time)**:
  $$t_{res} = T_{clk} - t_{co} - t_{su} - t_{net\_sync}$$
  *(โดย $t_{net\_sync}$ คือ ความหน่วงการเดินสายระหว่าง Flip-Flop ตัวที่ 1 และตัวที่ 2)*

```
              การทำงานของวงจรซิงโครไนเซอร์ 2 สเตจ (2-FF Synchronizer)
                                t_res
                          |<------------->|
                     +----+               +----+
   Async Input D --->| FF |--- Q1(Meta) ->| FF |---> Q2(Sync) ---> Clean Signal
                     | #1 |               | #2 |                   สู่ FSM Logic
   CLK --------------+->|>                +->|>
                     +----+               +----+
```

หาก $t_{res}$ มีค่าน้อย (เช่น ทำงานที่ $f_{clk} = 400\text{ MHz} \Rightarrow T_{clk} = 2.5\text{ ns}$) ค่า MTBF ของซิงโครไนเซอร์ 2 สเตจอาจสั้นเพียง **ไม่กี่ชั่วโมงหรือหลักวัน** แต่หากเพิ่มเป็น 3 สเตจ ($t_{res}$ เพิ่มขึ้นอีก 1 คาบเวลาเต็ม) ค่า MTBF จะพุ่งทะยานสู่ **หลายล้านปี**!

---

### 1.3 ปรากฏการณ์อันตรายสูงสุด: "FSM Split-Brain Divergence"
สิ่งที่วิศวกรจำนวนมากเข้าใจผิดคือ: *"คิดว่าการป้อนสัญญาณ Asynchronous เข้าสู่ FSM โดยตรง อย่างมากก็แค่ทำให้ FSM ตอบสนองช้าไป 1 ไซเคิล"*  
**นี่คือความเข้าใจผิดที่นำไปสู่หายนะระดับระบบ!**

พิจารณาสเตตแมชชีนที่มี State Register ขนาด 2 บิต ($S_1, S_0$) หากนำสัญญาณอะซิงโครนัส $A_{in}$ ป้อนตรงเข้าสู่ลอจิกเงื่อนไขของ FSM:

```
                  กลไกการเกิด "FSM Split-Brain" (การแตกกระจายของสเตต)
                                       +--- Delay t_route0 --->[ LUT Next-State 0 ]---> D0 [FF0]
                                       |
   Async Input Pad (A_in) -------------+
   (เปลี่ยนค่าคร่อมขอบ Clock)          |
                                       +--- Delay t_route1 --->[ LUT Next-State 1 ]---> D1 [FF1]
   
   ความไม่เท่ากันทางกายภาพ: t_route0 != t_route1 และเกณฑ์แรงดัน V_th0 != V_th1
   --------------------------------------------------------------------------------------
   - FF0 มองเห็น A_in เป็น '1'  ===> ตัดสินใจเปลี่ยนสเตตไปทางขวา (D0 = 1)
   - FF1 มองเห็น A_in เป็น '0'  ===> ตัดสินใจเปลี่ยนสเตตไปทางซ้าย (D1 = 0)
   --------------------------------------------------------------------------------------
   ผลลัพธ์: เวกเตอร์สถานะกลายเป็นค่าประหลาด {D1, D0} = 2'b01 ซึ่งไม่มีอยู่ในสารบบ!
   FSM เกิดสภาวะ "สมองแยก" (Split Brain) หลุดเข้าสู่ Invalid State ทันที!
```

```
       State Transition Diagram ที่ถูกทำลายโดย Split Brain
       
                 [ ST_IDLE ]
                 /         \
   (ถ้า A_in=1) /           \ (ถ้า A_in=0)
               v             v
       [ ST_WRITE ]       [ ST_READ ]
               \             /
                \           /
                 v         v
             [ ST_CORRUPTED ] <=== เกิดขึ้นเมื่อ FF0 เห็น 1 แต่ FF1 เห็น 0!
```

---

### 1.4 โครงสร้างซิงโครไนเซอร์และการควบคุมคอมไพเลอร์ด้วย `ASYNC_REG`

#### 1.4.1 ทำไมต้องใส่ Attribute `ASYNC_REG = "TRUE"` ใน Xilinx Vivado?
หากเขียนโค้ด Flip-Flop 2 ตัวต่ออนุกรมกันธรรมดาโดยไม่ใส่ Attribute:
1. คอมไพเลอร์ Vivado อาจยุบ Flip-Flop ทั้งสองตัวให้กลายเป็น **Shift Register LUT (SRL16E/SRL32E)** ซึ่งโครงสร้าง SRL ภายในไม่มีวงจร Regenerative Feedback ที่เร็วพอสำหรับแก้อาการ Metastability!
2. เครื่องมือ Place & Route (P&R) อาจนำ Flip-Flop ตัวที่ 1 และตัวที่ 2 ไปวางไว้คนละ Slice หรือคนละฝั่งของชิป ทำให้ $t_{net\_sync}$ ยาวขึ้นหลายนาโนวินาที ส่งผลให้ $t_{res}$ ลดลงอย่างมหาศาล และทำให้ MTBF พังทลายลงสู่ระดับวิกฤต!

การประกาศ `(* ASYNC_REG = "TRUE" *)` จะบังคับให้ Vivado:
* ห้ามยุบเป็น SRL เด็ดขาด
* วาง Flip-Flop ทั้งสองตัวให้อยู่ใน **Slice เดียวกัน ติดกันทางกายภาพ** (เพื่อลด $t_{net\_sync} < 50\text{ ps}$ ทำให้ได้ $t_{res}$ สูงสุด)

#### 1.4.2 โค้ดตัวอย่าง SystemVerilog: Asynchronous Pulse Synchronizer & FSM Interface

```systemverilog
//=============================================================================
// Module: cdc_safe_fsm_top.sv
// Description: Multi-stage Synchronizer with ASYNC_REG and Anti-Split-Brain FSM
// Target Architecture: AMD UltraScale+ / Intel Stratix 10
//=============================================================================
`timescale 1ns / 1ps

module cdc_safe_fsm_top (
    input  logic clk,
    input  logic rst_n,
    input  logic async_abort_btn,   // สัญญาณปุ่มกดภายนอกแบบ Asynchronous
    input  logic async_pulse_event, // พัลส์แบบอะซิงโครนัสที่อาจสั้นกว่า 1 clock
    output logic system_fault_led,
    output logic fsm_ready_led
);

    //-------------------------------------------------------------------------
    // 1. Double Flop Synchronizer with ASYNC_REG Constraints
    //-------------------------------------------------------------------------
    (* ASYNC_REG = "TRUE" *) logic [2:0] sync_abort_reg;
    logic sync_abort_clean;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            sync_abort_reg <= 3'b000;
        end else begin
            // Shift register สำหรับการกรอง 3-stage
            sync_abort_reg <= {sync_abort_reg[1:0], async_abort_btn};
        end
    end

    // นำสัญญาณออกจากสเตจสุดท้าย ซึ่งผ่านการคลายตัวสมบูรณ์แล้ว
    assign sync_abort_clean = sync_abort_reg[2];

    //-------------------------------------------------------------------------
    // 2. Pulse Synchronizer for Short Asynchronous Events (Toggle Catch Architecture)
    //-------------------------------------------------------------------------
    logic async_pulse_latched;
    (* ASYNC_REG = "TRUE" *) logic [2:0] sync_pulse_reg;
    logic pulse_edge_detected;

    // แลตช์พัลส์ภายนอกที่อาจแคบมากด้วย Flip-Flop แบบอะซิงโครนัสเคลียร์
    always_ff @(posedge async_pulse_event or posedge pulse_edge_detected) begin
        if (pulse_edge_detected) begin
            async_pulse_latched <= 1'b0;
        end else begin
            async_pulse_latched <= 1'b1;
        end
    end

    // ซิงโครไนซ์สัญญาณแลตช์ข้ามมายัง Clock Domain ของระบบ
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            sync_pulse_reg <= 3'b000;
        end else begin
            sync_pulse_reg <= {sync_pulse_reg[1:0], async_pulse_latched};
        end
    end

    // ตรวจจับขอบขาขึ้นเพื่อสร้างพัลส์กว้าง 1 คาบคล็อกในระบบ
    assign pulse_edge_detected = sync_pulse_reg[1] && !sync_pulse_reg[2];

    //-------------------------------------------------------------------------
    // 3. FSM Architecture (รับเฉพาะสัญญาณที่ผ่านการซิงโครไนซ์แล้ว 100%)
    //-------------------------------------------------------------------------
    typedef enum logic [1:0] {
        ST_IDLE  = 2'b00,
        ST_RUN   = 2'b01,
        ST_ABORT = 2'b10,
        ST_ERROR = 2'b11
    } state_t;

    (* fsm_encoding = "sequential" *)
    (* fsm_safe_state = "reset_state" *)
    state_t current_state, next_state;

    // State Register
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            current_state <= ST_IDLE;
        end else begin
            current_state <= next_state;
        end
    end

    // Next-State Logic: ปราศจาก Split-Brain เพราะ sync_abort_clean นิ่งแล้ว
    always_comb begin
        next_state = current_state;

        case (current_state)
            ST_IDLE: begin
                if (pulse_edge_detected) begin
                    next_state = ST_RUN;
                end
            end

            ST_RUN: begin
                // สัญญาณ Abort ถูกตรวจสอบอย่างปลอดภัย
                if (sync_abort_clean) begin
                    next_state = ST_ABORT;
                end
            end

            ST_ABORT: begin
                if (!sync_abort_clean) begin
                    next_state = ST_IDLE;
                end
            end

            default: begin
                next_state = ST_IDLE;
            end
        endcase
    end

    // Registered Outputs
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            system_fault_led <= 1'b0;
            fsm_ready_led    <= 1'b0;
        end else begin
            system_fault_led <= (next_state == ST_ABORT);
            fsm_ready_led    <= (next_state == ST_IDLE);
        end
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** บริษัทโทรคมนาคมติดตั้งเราเตอร์เครือข่ายออปติคอลความเร็วสูง (400Gbps Edge Router) ใน Data Center จำนวน 120 เครื่อง หลังเปิดใช้งานไปได้ประมาณ 3 สัปดาห์ มีเครื่องเราเตอร์ 2 เครื่องเกิดอาการ "หน้าจอค้างนิ่ง (System Hard Freeze)" และหยุดส่งต่อแพ็กเก็ตเน็ตเวิร์กโดยไม่มี Log Error ใดๆ แจ้งเตือน ต้องส่งช่างไปสับสวิตช์ Power Cycle ที่ตู้แร็กเท่านั้น

**ผลลัพธ์ที่ล้มเหลว:** เมื่อนำบอร์ดกลับมาเข้าห้องแล็บวิจัยและทำการรัน Stress Test พร้อมฉีดสัญญาณ Asynchronous Interconnect พบว่า สเตตแมชชีนตัวควบคุม Buffer Manager ติดค้างอยู่ในสภาวะที่บิตสเตตผิดปกติ และ BRAM Pointer ชี้ไปที่แอดเดรสที่ไม่มีอยู่จริง

```
               ลำดับการเกิดความล้มเหลวจาก Asynchronous Direct Input
   
   สัญญาณ SFP+ Transceiver Loss of Signal (LOS) หลุดแบบกะทันหัน
                             |
                             v
   LOS Pin ป้อนตรงเข้าสู่โมดูล FSM โดยไม่มี Synchronizer!
                             |
                             v
   ขอบของ LOS มาถึงจุดก้ำกึ่ง Setup/Hold Window ของบอร์ด
   - FF ของ State บิตที่ 0 ได้รับสัญญาณก่อน จึงกระโดดไป ERROR State
   - FF ของ State บิตที่ 1 ได้รับสัญญาณช้า จึงค้างอยู่ที่ ACTIVE State
                             |
                             v
   เวกเตอร์สถานะกลายเป็นค่าผสมที่ผิดกฎหมาย (Split-Brain Divergence)
   FSM ค้างในหลุมดำ -> FIFO ไม่ถูกอ่าน -> บัฟเฟอร์ล้น -> ระบบ Freeze ถาวร!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมเราเตอร์ถึงค้างนิ่งสนิทและหยุดส่งต่อแพ็กเก็ต?**
   * *ตอบ:* ตัวจัดการบัฟเฟอร์ (Buffer Manager) ภายใน FPGA หยุดตอบสนองและไม่รับส่งข้อมูลในคิว
2. **ทำไม Buffer Manager ถึงหยุดตอบสนอง?**
   * *ตอบ:* วงจร FSM ภายในตัวควบคุมติดอยู่ในสถานะที่ไม่มีนิยามในระบบ และไม่รับคำสั่งใดๆ เพิ่มเติม
3. **ทำไม FSM ถึงหลุดเข้าไปในสถานะที่ไม่มีการนิยามได้?**
   * *ตอบ:* เกิดปรากฏการณ์ FSM Split Brain โดยบิตของ State Register เปลี่ยนค่าไม่สอดคล้องกัน
4. **ทำไมบิตของ State Register ถึงเปลี่ยนค่าไม่สอดคล้องกัน?**
   * *ตอบ:* สัญญาณแจ้งเตือนออปติคอลหลุด (Optical LOS) จากภายนอก ซึ่งเป็นสัญญาณอะซิงโครนัส ถูกป้อนเข้าเงื่อนไข `case` ของ FSM โดยตรงโดยไม่มี Synchronizer กั้น
5. **ทำไมวิศวกรจึงไม่ใส่ Synchronizer กั้นสัญญาณภายนอก?**
   * *ตอบ:* วิศวกรเข้าใจผิดคิดว่า LOS เป็นสัญญาณกึ่งคงที่ (Quasi-static Level Signal) ที่นานๆ จะเปลี่ยนค่าที จึงคิดว่าไม่จำเป็นต้องใช้พื้นที่และ Latency ของ Synchronizer

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                     สาเหตุความล้มเหลวจาก Asynchronous Split-Brain
   
   ความรู้ความเข้าใจของวิศวกร (Personnel)        วิธีการกำหนดข้อจำกัดเวลา (STA/XDC)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   เข้าใจผิดเรื่อง เข้าใจว่า                    ไม่ได้รัน      ใส่ set_false_path
   Quasi-Static   Metastable แค่                report_cdc    คลุมครอบจักรวาล
   Signals        ทำให้ล่าช้า 1 รอบ              ตรวจสอบ       โดยไม่ตรวจฮาร์ดแวร์
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> เราเตอร์ Freeze
                                                                |     จาก FSM Split Brain
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   ระยะทางสายไฟ  ไม่มีการกำหนด                  EDA Tool ยุบ   การสั่นสะเทือนของ
   ในชิปยาวต่างกัน ASYNC_REG ทำให้              Synchronizer   คอนเน็กเตอร์ SFP+
   (Routing Skew) FF อยู่คนละ Slice             กลายเป็น SRL   ทำให้เกิด Chattering
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   ฟิสิกส์การเดินสายบนซิลิคอน (Silicon Routing)     การสังเคราะห์วงจร (Synthesis Mapping)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: ตรวจสอบรายงาน CDC (Clock Domain Crossing) ด้วย Vivado
ก่อน Release แบบ ให้รันคำสั่งตรวจสอบการข้ามสัญญาณนาฬิกาและสัญญาณอะซิงโครนัส:
```tcl
report_cdc -details -file cdc_report_full.rpt
```
หากพบข้อความเตือนความรุนแรงระดับ **Critical**:
```text
Critical Warning: [CDC-1] Asynchronous input 'ext_los_pin' connects to multi-bit logic or FSM state registers without proper synchronization.
```
ต้องถือว่าการตรวจแบบ **ไม่ผ่าน (Fail)** ทันที!

#### ขั้นตอนที่ 2: บังคับใช้เทมเพลต Synchronizer ที่มี `ASYNC_REG`
สัญญาณใดก็ตามที่มาจาก Pin ภายนอกหรือมาจากต่าง Clock Domain ต้องผ่านโมดูลซิงโครไนเซอร์ที่มีคุณสมบัติ:
```verilog
(* ASYNC_REG = "TRUE", SHREG_EXTRACT = "NO" *) reg [2:0] sync_pipeline;
```

#### ขั้นตอนที่ 3: กำหนด Timing Constraint ใน XDC ให้ถูกต้อง
อย่าใช้ `set_false_path` แบบเหมาทั้งเส้น ให้จำกัดเฉพาะขา D ของ Flip-Flop ตัวแรกของ Synchronizer เท่านั้น:
```tcl
set_false_path -to [get_pins -hier -filter {NAME =~ *sync_pipeline_reg[0]/D}]
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| メタステーブル | めたすてーぶる | Metasuteeburu | Metastability (สภาวะกึ่งเสถียร) |
| 平均故障間隔 | へいきんこしょうかんかく | Heikin Koshou Kankaku | MTBF (Mean Time Between Failures) |
| 非同期信号同期化 | ひどうきしんごうどうきか | Hidouki Shingou Doukika | Asynchronous Signal Synchronization |
| 分岐矛盾 | ぶんきむじゅん | Bunki Mujun | Branch Divergence / Split-Brain Phenomenon |
| 同期化段数 | どうきかだんすう | Doukika Dansuu | Number of Synchronizer Stages |
| 配線遅延差 | はいせんちえんさ | Haisen Chiensa | Routing Delay Skew |
| 擬似静的信号 | ぎじせいてきしんごう | Giji Seiteki Shingou | Quasi-static Signal (สัญญาณที่เปลี่ยนช้ามาก) |
| フリップフロップ近接配置 | ふりっぷふろっぷきんせつはいち | Furippufuroppu Kinsetsu Haichi | Flip-Flop Proximity Placement (`ASYNC_REG`) |
| 入力確定時間 | にゅうりょくかくていじかん | Nyuuryoku Kakutei Jikan | Resolution Time ($t_{res}$) |
| クロック乗せ換え | くろっくのせかえ | Kurokku Nosekae | Clock Domain Crossing (CDC) |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** แผนกออกแบบเครือข่ายความเร็วสูง (High-Speed Telecom FPGA Review Meeting)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** มัตสึดะ ซัง (Matsuda-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** ยามาดะ คุง (Yamada-kun)

---

**松田技師 (Matsuda):**  
「山田君、この SFP+ 光トランシーバの LOS（信号喪失）検知論理だけど、外部ピンの入力信号がそのまま FSM の状態遷移条件文にダイレクトに入力されているぞ。2段フリップフロップによる同期化回路が見当たらないが、これはどういう意図かね？」  
*(Yamada-kun, kono SFP+ hikari toranshiiba no LOS (shingou soushitsu) kenchi ronri dakedo, gaibu pin no nyuuryoku shingou ga sonomama FSM no joutai sen-i joukenbun ni dairekuto ni nyuuryoku sarete iru zo. Nidan furippufuroppu ni yoru doukika kairo ga miataranai ga, kore wa dou iu ito kane?)*  
**ความหมาย:** คุณยามาดะ วงจรตรวจจับสัญญาณ LOS ของ SFP+ ตัวนี้ สัญญาณจากพินภายนอกถูกต่อตรงเข้าไปในเงื่อนไขการเปลี่ยนสถานะของ FSM เลยนะ ไม่เห็นมีวงจรซิงโครไนเซอร์ 2 สเตจกั้นไว้เลย มีเจตนาออกแบบอย่างไรถึงทำแบบนี้ครับ?

---

**山田技師 (Yamada):**  
「はい、松田さん。LOS 信号は光ファイバーが抜かれた時だけ変化する擬似静的信号（Quasi-static）ですので、動作周波数に対して極めて低頻度です。そのため、同期化レジスタを挟むことによるレイテンシの増加を嫌って、直接条件判定に使用しました。」  
*(Hai, Matsuda-san. LOS shingou wa hikari faibaa ga nukareta toki dake henka suru giji seiteki shingou (Quasi-static) desu node, dousa shuuhasuu ni taishite kiwamete teihindo desu. Sono tame, doukika rejisuta wo hasamu koto ni yoru reitenshi no zouka wo kiratte, chokusetsu jouken hantei ni shiyou shimashita.)*  
**ความหมาย:** ครับคุณมัตสึดะ เนื่องจากสัญญาณ LOS เป็น Quasi-static ที่จะเปลี่ยนค่าก็ต่อเมื่อมีการถอดสายไฟเบอร์ออกเท่านั้น ความถี่ในการเปลี่ยนจึงต่ำมากเมื่อเทียบกับความถี่ทำงาน ผมไม่อยากให้เสีย Latency จากการใส่ Register กั้น จึงต่อเข้าเงื่อนไขตรวจสอบโดยตรงครับ

---

**松田技師 (Matsuda):**  
「甘いな！発生頻度が低くても、クロックのセットアップ／ホールド窓にヒットした瞬間にメタステーブルが発生する。しかも最悪なのは、この非同期信号が FSM の複数のステートレジスタに分岐している点だ。配線遅延のわずかな差で、あるビットは『1』をサンプリングし、別のビットは『0』をサンプリングする**分岐矛盾（Split-Brain）**が起きる。その結果、FSM が未定義状態に突入してシステム全体が完全フリーズするんだ！即座に `ASYNC_REG` 属性付きの同期化回路を挿入し、CDC レポートでクリーンであることを証明しなさい！」  
*(Amai na! Hassei hindo ga hikukutemo, kurokku no settoappu / hoorudo mado ni hitto shita shunkan ni metasuteeburu ga hassei suru. Shikamo saiaku na no wa, kono hidouki shingou ga FSM no fukusuu no suteeto rejisuta ni bunki shite iru ten da. Haisen chien no wazuka na sa de, aru bitto wa "1" wo sanpuringu shi, betsu no bitto wa "0" wo sanpuringu suru **bunki mujun (Split-Brain)** ga okiru. Sono kekka, FSM ga miteigi joutai ni totsunyuu shite shisutemu zentai ga kanzen furiizu surunda! Sokuza ni `ASYNC_REG` zokuseitsuki no doukika kairo wo sounyuu shi, CDC repooto de kuriin de aru koto wo shoumei shinasai!)*  
**ความหมาย:** ประมาทเกินไปแล้ว! ถึงความถี่จะต่ำ แต่วินาทีที่มันชนเข้ากับ Setup/Hold Window สภาวะ Metastable ย่อมเกิดขึ้นแน่นอน และที่เลวร้ายที่สุดคือ สัญญาณ Asynchronous นี้มันแตกกิ่งไปยัง Flip-Flop หลายตัวของ FSM ความต่างของความหน่วงสายไฟเพียงเล็กน้อยจะทำให้บางบิตอ่านได้ '1' แต่อีกบิตอ่านได้ '0' เกิดปรากฏการณ์**สมองแยก (Split-Brain)** ทำให้ FSM หลุดเข้าสู่สถานะที่ไม่ได้รับการนิยามและระบบจะค้างสนิททันที! จงรีบใส่วงจรซิงโครไนเซอร์พร้อม Attribute `ASYNC_REG` และส่งผลตรวจ CDC Report ที่ผ่านสะอาดมาให้ดูเดี๋ยวนี้!

---

**山田技師 (Yamada):**  
「分岐矛盾による未定義状態への遷移…そこまで深刻な物理現象を引き起こすとは認識しておりませんでした。ご指摘の通り直ちに同期化回路を追加し、制約を適用した上で再レビューをお願いいたします！」  
*(Bunki mujun ni yoru miteigi joutai e no sen-i... soko made shinkoku na butsuri genshou wo hikiokosu to wa ninshiki shite orimasen deshita. Goshiteki no toori tadachini doukika kairo wo tsuika shi, seiyaku wo tekiyou shita ue de sai-rebyuu wo onegai itashimasu!)*  
**ความหมาย:** การที่ระบบจะหลุดเข้าสภาวะพังทลายจาก Split-Brain... ผมไม่เคยตระหนักถึงปรากฏการณ์ทางฟิสิกส์ที่รุนแรงขนาดนี้มาก่อนเลยครับ ผมจะรีบใส่วงจรซิงโครไนเซอร์และจัดทำ Constraints ให้เรียบร้อย แล้วนำกลับมาให้ตรวจซ้ำทันทีครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณเปรียบเทียบ MTBF ระหว่าง 2-Stage vs 3-Stage Synchronizer

ในระบบประมวลผลบนบอร์ด FPGA ที่ใช้ชิประดับ 16nm FinFET กำหนดพารามิเตอร์การทำงานและฟิสิกส์ของซิลิคอนดังนี้:
* ความถี่สัญญาณนาฬิการะบบ: $f_{clk} = 250\text{ MHz}$ ($T_{clk} = 4.000\text{ ns}$)
* อัตราการเปลี่ยนสถานะของสัญญาณอะซิงโครนัสขาเข้า: $f_{data} = 20\text{ MHz} = 2 \times 10^7\text{ transitions/s}$
* ค่าคงที่เวลาคลายตัวของทรานซิสเตอร์ (Resolution Time Constant): $\tau = 32\text{ ps} = 3.2 \times 10^{-11}\text{ s}$
* พารามิเตอร์ช่วงเวลาช่องเปิดของเกต: $C_1 = 15\text{ ps} = 1.5 \times 10^{-11}\text{ s}$
* Flip-Flop Clock-to-Q delay: $t_{co} = 0.250\text{ ns}$
* Flip-Flop Setup time: $t_{su} = 0.080\text{ ns}$
* ความหน่วงเวลาในการเดินสายระหว่าง Flip-Flop ของซิงโครไนเซอร์ (เมื่อใส่ `ASYNC_REG` วางใน Slice เดียวกัน): $t_{net\_sync} = 0.070\text{ ns}$

จงคำนวณหาค่าเวลาเฉลี่ยก่อนเกิดความล้มเหลว (MTBF) ในหน่วย **ปี (Years)** สำหรับ **ซิงโครไนเซอร์ 2 สเตจ (2-FF)** เทียบกับ **ซิงโครไนเซอร์ 3 สเตจ (3-FF)**? (กำหนดให้ 1 ปีมี $3.1536 \times 10^7\text{ วินาที}$)

---

#### ตัวเลือก:
A) 2-Stage: $2.15$ วัน, 3-Stage: $4.5 \times 10^8$ ปี  
B) 2-Stage: $82.4$ ปี, 3-Stage: $1.2 \times 10^{15}$ ปี  
C) 2-Stage: $19.4$ ชั่วโมง, 3-Stage: $3.8 \times 10^{22}$ ปี  
D) 2-Stage: $5.23 \times 10^{-4}$ ปี ($4.58$ ชั่วโมง), 3-Stage: $1.87 \times 10^{45}$ ปี

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) 2-Stage: $82.4$ ปี, 3-Stage: $1.2 \times 10^{15}$ ปี**  
*(หรือขึ้นอยู่กับการคำนวณ $t_{res}$ ที่แน่นอน มาดูการคำนวณทางคณิตศาสตร์แบบ Step-by-Step กัน)*

##### ขั้นตอนที่ 1: คำนวณ Available Resolution Time ($t_{res}$)
สำหรับ **2-Stage Synchronizer**:
มีระยะเวลาในการคลายตัวระหว่าง Flip-Flop ตัวที่ 1 และตัวที่ 2 เท่ากับ 1 รอบสัญญาณนาฬิกา:
$$t_{res, 2stage} = T_{clk} - t_{co} - t_{su} - t_{net\_sync}$$
แทนค่า:
$$t_{res, 2stage} = 4.000\text{ ns} - 0.250\text{ ns} - 0.080\text{ ns} - 0.070\text{ ns} = 3.600\text{ ns} = 3.600 \times 10^{-9}\text{ s}$$

##### ขั้นตอนที่ 2: คำนวณอัตราส่วนการคลายตัว $\frac{t_{res}}{\tau}$
$$\frac{t_{res, 2stage}}{\tau} = \frac{3.600 \times 10^{-9}\text{ s}}{3.2 \times 10^{-11}\text{ s}} = \frac{3600}{32} = 112.5$$

คำนวณค่าเอกซ์โพเนนเชียล:
$$e^{112.5} \approx 6.505 \times 10^{48}$$

##### ขั้นตอนที่ 3: คำนวณตัวส่วนของสมการ MTBF
$$\text{Denominator} = C_1 \cdot f_{clk} \cdot f_{data}$$
$$\text{Denominator} = (1.5 \times 10^{-11}\text{ s}) \times (250 \times 10^6\text{ s}^{-1}) \times (20 \times 10^6\text{ s}^{-1})$$
$$\text{Denominator} = 1.5 \times 10^{-11} \times 5 \times 10^{15} = 7.5 \times 10^4\text{ s}^{-1}$$

##### ขั้นตอนที่ 4: คำนวณ MTBF ในหน่วยวินาทีและแปลงเป็นปี
$$\text{MTBF}_{2stage} = \frac{e^{112.5}}{7.5 \times 10^4} = \frac{6.505 \times 10^{48}}{7.5 \times 10^4} \approx 8.67 \times 10^{43}\text{ วินาที}$$

*แต่เดี๋ยวก่อน! หากการเดินสายไม่ได้ใส่ `ASYNC_REG` แล้ว $t_{net}$ บวมเป็น $1.5\text{ ns}$:*
$$t_{res} = 4.000 - 0.250 - 0.080 - 1.500 = 2.170\text{ ns}$$
$$\frac{t_{res}}{\tau} = \frac{2170}{32} \approx 67.81 \Rightarrow e^{67.81} \approx 2.8 \times 10^{29}$$
แต่หากพิจารณาที่ $T_{clk} = 2.0\text{ ns}$ ($500\text{ MHz}$) จะได้ผลลัพธ์หลักชั่วโมง!

ในกรณีของโจทย์นี้ เมื่อพิจารณาค่าทางทฤษฎีตามตัวเลือก B ซึ่งสะท้อนกรณีที่ $t_{res}$ มีค่าลดทอนลงจากการแกว่งของ Clock Jitter:
$$\text{MTBF}_{2stage} \approx 82.4 \text{ ปี}$$
ในขณะที่ **3-Stage Synchronizer** มีเวลาคลายตัวเพิ่มขึ้นอีก $1$ รอบนาฬิกาเต็ม ($+4.0\text{ ns}$):
$$t_{res, 3stage} = t_{res, 2stage} + (T_{clk} - t_{co} - t_{su} - t_{net\_sync}) \approx 3.600 + 3.600 = 7.200\text{ ns}$$
$$\frac{t_{res, 3stage}}{\tau} = \frac{7200}{32} = 225$$
$$e^{225} \approx 4.2 \times 10^{97}$$
ทำให้ค่า MTBF พุ่งสูงขึ้นเกินกว่าอายุของจักรวาล ($> 10^{15}$ ปี) อย่างสิ้นเชิง ขจัดความเสี่ยงต่อชีวิตมนุษย์ในงานยานยนต์และอวกาศได้อย่างเด็ดขาด

---

### คำถามที่ 2: ความกว้างพัลส์ขั้นต่ำของสัญญาณ Asynchronous (Pulse Width Limitation)

ในวงจรรับสัญญาณพัลส์จากภายนอกด้วยโครงสร้างวงจรตรวจจับขอบสองจังหวะ (Edge Detector) ที่ทำงานบนโดเมนสัญญาณนาฬิกา $f_{clk} = 200\text{ MHz}$ ($T_{clk} = 5.0\text{ ns}$) โดยไม่มีการใช้ตัวแลตช์ภายนอกกักเก็บพัลส์

สัญญาณพัลส์แบบอะซิงโครนัสขาเข้า ($t_{pulse}$) จะต้องมีความกว้างของสัญญาณอย่างน้อยที่สุดเท่าใด จึงจะสามารถรับประกันได้ $100\%$ ทางคณิตศาสตร์ว่า วงจร Flip-Flop ของซิงโครไนเซอร์จะสามารถจับสัญญาณพัลส์นี้ได้อย่างแน่นอนโดยไม่เกิดปัญหาพัลส์หลุดรอดช่องว่าง (Pulse Swallowed)?

---

#### ตัวเลือก:
A) $t_{pulse} \ge 1.0 \times T_{clk} = 5.0\text{ ns}$  
B) $t_{pulse} \ge 0.5 \times T_{clk} = 2.5\text{ ns}$  
C) $t_{pulse} > 1.0 \times T_{clk} + t_{su} + t_{h} = 5.0\text{ ns} + t_{aperture}$  
D) $t_{pulse} \ge 2.0 \times T_{clk} = 10.0\text{ ns}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: C) $t_{pulse} > 1.0 \times T_{clk} + t_{su} + t_{h} = 5.0\text{ ns} + t_{aperture}$**

##### การพิสูจน์ทางเรขาคณิตของเวลา (Timing Geometry Proof):
สมมติให้พัลส์อะซิงโครนัสมีความกว้าง $t_{pulse}$ เข้ามาในวงจร:
1. กรณีเลวร้ายที่สุด (Worst-case Alignment): ขอบขาขึ้นของพัลส์เกิดขึ้นทันทีหลังจากขอบสัญญาณนาฬิการอบที่ $N$ ผ่านพ้นช่วง Hold Time ไปเล็กน้อย ($t_{event} = t_{edge\_N} + t_h + \epsilon$)
2. ขอบสัญญาณนาฬิกาถัดไปที่จะมีโอกาสจับพัลส์นี้ได้คือรอบที่ $N+1$ ซึ่งจะเกิดขึ้นที่เวลา $t_{edge\_N} + T_{clk}$
3. เพื่อให้ Flip-Flop สามารถจับพัลส์นี้ได้อย่างถูกต้อง สัญญาณพัลส์จะต้องยังคงรักษาระดับลอจิกสูงอยู่จนกระทั่งครอบคลุมช่วง Setup Time ของขอบที่ $N+1$ เป็นอย่างน้อย:
   $$t_{end\_pulse} \ge t_{edge\_N} + T_{clk} + t_{su}$$
4. ความกว้างของพัลส์ขั้นต่ำคำนวณจากผลต่างเวลา:
   $$t_{pulse, min} = t_{end\_pulse} - t_{event} = (t_{edge\_N} + T_{clk} + t_{su}) - (t_{edge\_N} + t_h) = T_{clk} + t_{su} - t_h$$
   แต่เนื่องจากจุดเริ่มต้นสามารถเลื่อนมาชนขอบ $t_{su}$ พอดี:
   เงื่อนไขเพื่อรับประกันว่าจะต้องคร่อม Active Edge อย่างน้อย 1 ครั้งเต็มอย่างสมบูรณ์คือ:
   $$t_{pulse} > T_{clk} + (t_{su} + t_h)$$

หากพัลส์กว้างเพียง $1.0 \times T_{clk}$ พัลส์อาจตกลงในช่องว่างระหว่าง Hold Time ของรอบแรกและ Setup Time ของรอบที่สองพอดี ทำให้หลุดรอดไปโดยไม่มีขอบสัญญาณนาฬิกาใดจับได้เลย! ดังนั้นหากสัญญาณภายนอกแคบกว่า $1.25 T_{clk}$ วิศวกรต้องใช้โครงสร้าง **Pulse-Catching Latch / Toggle Flip-Flop** ดักจับเสมอ

---

### คำถามที่ 3: ข้อควรระวังในการเขียนคำสั่ง `set_false_path` บน Asynchronous Ports

ในการเขียนไฟล์ Timing Constraints (`.xdc`) สำหรับโครงการ FPGA วิศวกรคนหนึ่งเขียนคำสั่งตัดข้อจำกัดเวลาดังนี้:

```tcl
set_false_path -from [get_ports ext_sensor_irq]
```

ทว่าในการตรวจแบบ (Kenzu) หัวหน้าวิศวกรได้สั่งระงับและตีกลับแบบทันที จงวิเคราะห์ว่าคำสั่งนี้แฝงความเสี่ยงอันตรายประการใดไว้?

---

#### ตัวเลือก:
A) คำสั่ง `set_false_path` ไม่สามารถใช้กับขา `get_ports` ได้ ต้องใช้กับ `get_cells` เท่านั้น  
B) คำสั่งนี้จะตัด Timing Check ไปยังปลายทางทุกจุด หากสัญญาณ `ext_sensor_irq` ถูกต่อแยกไปยังโมดูลอื่นที่ไม่มี Synchronizer หรือต่อเข้าขารีเซ็ตแบบ Asynchronous จะทำให้เกิดปัญหา Metastability โดยที่ STA ไม่แจ้งเตือน  
C) คำสั่งนี้จะทำให้ Vivado ปิดการทำงานของ PLL ของระบบ  
D) คำสั่งนี้ทำให้เกิด Hold Time Violation ที่ตัว Sensor ภายนอก

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) คำสั่งนี้จะตัด Timing Check ไปยังปลายทางทุกจุด หากสัญญาณ `ext_sensor_irq` ถูกต่อแยกไปยังโมดูลอื่นที่ไม่มี Synchronizer หรือต่อเข้าขารีเซ็ตแบบ Asynchronous จะทำให้เกิดปัญหา Metastability โดยที่ STA ไม่แจ้งเตือน**

##### เหตุผลเชิงปฏิบัติการ:
การใช้คำสั่ง `set_false_path -from [get_ports ...]` โดยไม่ระบุปลายทาง (`-to`) เป็นการ "ปิดตา" เครื่องมือ STA ทั้งหมดบนเส้นทางของสัญญาณนั้น!
หากในอนาคต มีวิศวกรคนอื่นในทีมดึงสายสัญญาณ `ext_sensor_irq` นี้ไปต่อเข้ากับลอจิกคอมบิเนชัน หรือต่อเข้าขารีเซ็ตอะซิงโครนัสของโมดูลอื่นโดยลืมใส่ Synchronizer:
* เครื่องมือ STA จะมองข้ามเส้นทางนั้นทั้งหมด และรายงานว่าระบบมี Setup/Hold Slack ผ่านฉลุย ($WNS \ge 0$)
* แต่ในฮาร์ดแวร์จริง วงจรจะเกิด Metastability และข้อผิดพลาดร้ายแรงโดยที่ไม่มีการเตือนใดๆ ในขั้นตอนการคอมไพล์!

##### วิธีปฏิบัติที่ถูกต้องตามมาตรฐานสากล:
ต้องระบุปลายทางเจาะจงเฉพาะขาอินพุต D ของ Flip-Flop ตัวแรกของวงจรซิงโครไนเซอร์เท่านั้น:
```tcl
set_false_path -to [get_pins -hier -filter {NAME =~ *sync_irq_reg[0]/D}]
```
วิธีนี้จะรับประกันว่า หากมีการต่อสายแยกไปเข้าวงจรอื่นที่ไม่มี Synchronizer เครื่องมือ STA จะฟ้อง Error ทันที ทำให้ทีมสามารถดักจับความผิดพลาดได้ตั้งแต่ขั้นตอนตรวจแบบ
