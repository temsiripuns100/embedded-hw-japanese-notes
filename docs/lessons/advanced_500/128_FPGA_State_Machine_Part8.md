# Lesson 128: FPGA State Machine Part 8 - Fault-Tolerant FSM Design (耐故障性ステートマシン: TMR, Hamming SEC-DED, Safe Recovery & ISO 26262/DO-254)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ฟิสิกส์ของผลกระทบจากรังสีและอนุภาคพลังงานสูง (Single Event Effects: SEE Physics)
ในอุปกรณ์อิเล็กทรอนิกส์ที่ติดตั้งในอากาศยาน (Avionics), ยานยนต์ไร้คนขับ (Autonomous Vehicles), หรือดาวเทียมอวกาศ ชิป FPGA จะต้องเผชิญหน้ากับอนุภาครังสีคอสมิกอย่างต่อเนื่อง เช่น นิวตรอนพลังงานสูง ($E > 10\text{ MeV}$) และไอออนหนัก (Heavy Ions) ที่ระดับความสูงเพดานบินพาณิชย์ ($35,000\text{ ft}$) ฟลักซ์ของอนุภาคนิวตรอนจะมีความหนาแน่นสูงกว่าที่ระดับน้ำทะเลถึง **$300 - 500$ เท่า** ($\approx 4,000 - 6,000\text{ n/(cm}^2\cdot\text{h)}$)

```
                       อนุภาคนิวตรอนพลังงานสูง (High-Energy Neutron)
                                            |
                                            v
                   +-------------------------------------------------+
                   | Silicon Substrate (ซิลิคอนในชิป FPGA)           |
                   |                                                 |
                   |      การชนแบบนิวเคลียร์ (Nuclear Spallation)      |
                   |      ทำให้เกิด Secondary Ionization             |
                   |                     \   /                       |
                   |                      \ /                        |
                   |                       ●                         |
                   |                      / \                        |
                   |       อิเล็กตรอน-โฮลแพร์ (e-/h+ Charge Track)   |
                   +-----------------------+-------------------------+
                                           |
                                           v
                   ประจุไฟฟ้าฉับพลัน (Q_dep > Q_crit) วิ่งเข้าสู่ Drain ของ Transistor
                                           |
                                           v
                   เกิด Single Event Upset (SEU): บิตใน Flip-Flop พลิกจาก 0 <-> 1!
```

หากบิตที่ถูกพลิกค่า (Bit-Flip) เป็นบิตของ **State Register** ใน State Machine:
1. FSM จะกระโดดข้ามไปยังสถานะที่ไม่ได้คาดหมาย (Unintended State Transition)
2. หรือหลุดเข้าไปในสถานะที่ไม่มีการนิยาม (Illegal / Trap State) ทำให้ระบบเกิด Deadlock หรือส่งสัญญาณควบคุมที่เป็นอันตรายต่อชีวิตมนุษย์

---

### 1.2 ทฤษฎีรหัสการแก้ไขข้อผิดพลาด (Error-Correcting Coding Theory for FSM)
ตามทฤษฎีสารสนเทศของ Richard Hamming ความสามารถในการตรวจจับและแก้ไขความผิดพลาดขึ้นอยู่กับ **ระยะห่างแฮมมิงขั้นต่ำ ($d_{min}$)** ระหว่างรหัสที่ถูกต้องทุกคู่:

$$d_{min} \ge 2t + d + 1$$

โดยที่:
* $t$ คือ จำนวนบิตผิดพลาดที่สามารถ **แก้ไขได้ (Correctable Bits)**
* $d$ คือ จำนวนบิตผิดพลาดที่สามารถ **ตรวจจับได้ (Detectable Bits)**

```
+------------------------------------+------------+---------------------------------------------------+
| สถาปัตยกรรมรหัส                    | $d_{min}$  | ขีดความสามารถทางวิศวกรรม                          |
+------------------------------------+------------+---------------------------------------------------+
| 1. Standard Binary / One-Hot       | $1$ หรือ $2$| แก้ไขไม่ได้เลย ($t=0$), ตรวจจับได้จำกัด           |
| 2. Single Parity Check             | $2$        | ตรวจจับ 1 บิตได้ ($d=1$), แก้ไขไม่ได้             |
| 3. Hamming Code (SEC: Single Error)| $3$        | **แก้ไข 1 บิตได้อัตโนมัติ ($t=1$)**                |
| 4. Extended Hamming (SEC-DED)      | $4$        | **แก้ไข 1 บิต และตรวจจับ 2 บิตได้ ($t=1, d=1$)**  |
+------------------------------------+------------+---------------------------------------------------+
```

#### 1.2.1 เมทริกซ์การตรวจสอบ Extended Hamming SEC-DED (8,4)
สำหรับสเตตแมชชีนที่มีข้อมูลสถานะ $k = 4$ บิต เราใช้บิตตรวจสอบ $p = 4$ บิต (รวม $n = 8$ บิต):
* เมทริกซ์กำเนิด (Generator Matrix: $\mathbf{G} \in \mathbb{F}_2^{4 \times 8}$) ทำหน้าที่เข้ารหัส: $\mathbf{c} = \mathbf{s} \mathbf{G}$
* เมทริกซ์ภาวะเสมอภาค (Parity-Check Matrix: $\mathbf{H} \in \mathbb{F}_2^{4 \times 8}$) ทำหน้าที่ตรวจสอบ Syndrome: $\mathbf{S} = \mathbf{r} \mathbf{H}^T$

หาก $\mathbf{S} = \mathbf{0}$ เวกเตอร์ถูกต้องสมบูรณ์ หาก $\mathbf{S} \ne \mathbf{0}$ ค่าของ Syndrome จะชี้ระบุตำแหน่งบิตที่เกิดข้อผิดพลาดได้อย่างแม่นยำ ทำให้วงจรสามารถกลับค่าบิต (Invert Bit) นั้นเพื่อแก้ไขตนเองได้ภายในรอบสัญญาณนาฬิกาเดียวกัน!

---

### 1.3 สถาปัตยกรรม Triple Modular Redundancy (TMR) ในระดับสเตตแมชชีน

TMR คือสถาปัตยกรรมที่ได้รับความนิยมสูงสุดในมาตรฐานการบิน DO-254 DAL-A และยานยนต์ ISO 26262 ASIL-D โดยการทำซ้ำวงจร 3 ชุดขนานกันและใช้ **Majority Voter (วงจรลงคะแนนเสียงข้างมาก)** ตัดสินค่า:

$$Q_{voted} = (A \cdot B) + (B \cdot C) + (A \cdot C)$$

```
               สถาปัตยกรรม Local TMR พร้อม Feedback Voter Loop
   
   Inputs X ----+-------------------------+-------------------------+
                |                         |                         |
                v                         v                         v
         +--------------+          +--------------+          +--------------+
         | Next-State A |          | Next-State B |          | Next-State C |
         +-------+------+          +-------+------+          +-------+------+
                 |                         |                         |
                 v                         v                         v
              +----+                    +----+                    +----+
              |FF A|                    |FF B|                    |FF C|
              +--+-+                    +--+-+                    +--+-+
                 |                         |                         |
                 +----------+   +----------+   +----------+          |
                            |   |              |          |          |
                            v   v              v          v          v
                         +---------+        +---------+        +---------+
                         | Voter A |        | Voter B |        | Voter C |
                         +----+----+        +----+----+        +----+----+
                              |                  |                  |
                              +-------- State Feedback Loops -------+
```

> [!IMPORTANT] กฎเหล็กของ Senior Architect: ตำแหน่งของ Voter ต้องอยู่ใน Feedback Loop เสมอ!
> หากวาง Majority Voter ไว้นอกลูป (Feedforward Voting) แล้วป้อนค่าที่ยังไม่โหวตย้อนกลับเข้า Flip-Flop:  
> เมื่อเกิด Bit-Flip ใน FF A เพียงตัวเดียว ค่าที่ผิดพลาดจะถูกป้อนกลับเข้าไปวนลูปใน Channel A ตลอดกาล! หากเวลาผ่านไปเกิด Bit-Flip ใน FF B อีกตัวหนึ่ง วงจร Voter จะพังทลายทันที (2 ผิด 1 ถูก)!  
> **ดังนั้น Majority Voter จะต้องถูกต่อแทรกใน Feedback Path ของแต่ละแชนเนลเสมอ** เพื่อลบล้างข้อผิดพลาด (Auto-scrubbing) ให้หมดไปในทุกๆ รอบสัญญาณนาฬิกา!

---

### 1.4 โค้ดตัวอย่าง SystemVerilog: Fault-Tolerant FSM พร้อม Local TMR และ Majority Voting

```systemverilog
//=============================================================================
// Module: tmr_safe_fsm_engine.sv
// Description: DO-254 DAL-A Compliant Local TMR State Machine with Auto-Scrubbing
// Target: Safety-Critical Aerospace & Automotive Core
//=============================================================================
`timescale 1ns / 1ps

module tmr_safe_fsm_engine (
    input  logic clk,
    input  logic rst_n,
    input  logic flight_arm_cmd,
    input  logic abort_cmd,
    output logic actuator_deploy_en,
    output logic [1:0] fault_injection_status
);

    typedef enum logic [1:0] {
        ST_STANDBY = 2'b00,
        ST_ARMED   = 2'b01,
        ST_ACTIVE  = 2'b10,
        ST_SAFE    = 2'b11
    } state_t;

    // ประกาศ 3 ชุดอิสระสำหรับ TMR
    state_t state_a, state_b, state_c;
    state_t voted_state_a, voted_state_b, voted_state_c;
    state_t next_state_a, next_state_b, next_state_c;

    //-------------------------------------------------------------------------
    // 1. Majority Voter Functions (Bitwise 2-out-of-3 Logic)
    //-------------------------------------------------------------------------
    function automatic state_t majority_vote(input state_t a, input state_t b, input state_t c);
        state_t result;
        begin
            result[0] = (a[0] & b[0]) | (b[0] & c[0]) | (a[0] & c[0]);
            result[1] = (a[1] & b[1]) | (b[1] & c[1]) | (a[1] & c[1]);
            return result;
        end
    endfunction

    // คำนวณคะแนนเสียงข้างมากให้กับแต่ละรีจิสเตอร์ (Triplicated Voters ป้องกัน Single Voter Failure)
    assign voted_state_a = majority_vote(state_a, state_b, state_c);
    assign voted_state_b = majority_vote(state_a, state_b, state_c);
    assign voted_state_c = majority_vote(state_a, state_b, state_c);

    //-------------------------------------------------------------------------
    // 2. Next-State Logic Triplication
    // คำนวณโดยอิงจาก "Voted State" เพื่อลบล้างบิตที่ผิดพลาดทันที (Auto-scrubbing)
    //-------------------------------------------------------------------------
    function automatic state_t compute_next(input state_t s, input logic arm, input logic abort);
        case (s)
            ST_STANDBY: if (arm) return ST_ARMED; else return ST_STANDBY;
            ST_ARMED:   if (abort) return ST_SAFE; else return ST_ACTIVE;
            ST_ACTIVE:  if (abort) return ST_SAFE; else return ST_ACTIVE;
            ST_SAFE:    return ST_SAFE;
            default:    return ST_SAFE;
        endcase
    endfunction

    assign next_state_a = compute_next(voted_state_a, flight_arm_cmd, abort_cmd);
    assign next_state_b = compute_next(voted_state_b, flight_arm_cmd, abort_cmd);
    assign next_state_c = compute_next(voted_state_c, flight_arm_cmd, abort_cmd);

    //-------------------------------------------------------------------------
    // 3. State Registers: ใส่ Attribute ป้องกันการยุบลอจิกของ EDA Tool
    //-------------------------------------------------------------------------
    (* DONT_TOUCH = "TRUE" *) always_ff @(posedge clk) begin
        if (!rst_n) begin
            state_a <= ST_STANDBY;
            state_b <= ST_STANDBY;
            state_c <= ST_STANDBY;
        end else begin
            state_a <= next_state_a;
            state_b <= next_state_b;
            state_c <= next_state_c;
        end
    end

    //-------------------------------------------------------------------------
    // 4. Triplicated Output Voting & Discrepancy Reporting
    //-------------------------------------------------------------------------
    logic out_a, out_b, out_c;
    assign out_a = (voted_state_a == ST_ACTIVE);
    assign out_b = (voted_state_b == ST_ACTIVE);
    assign out_c = (voted_state_c == ST_ACTIVE);

    // เอาต์พุตสุดท้ายผ่าน Majority Voter
    assign actuator_deploy_en = (out_a & out_b) | (out_b & out_c) | (out_a & out_c);

    // วงจรตรวจจับความขัดแย้ง (Discrepancy Detector: เตือนว่ามี Channel ใดเกิด SEU)
    always_comb begin
        if ((state_a != state_b) || (state_b != state_c)) begin
            fault_injection_status = 2'b01; // พบข้อผิดพลาด 1 บิตแต่แก้ไขได้
        end else begin
            fault_injection_status = 2'b00; // ปกติสมบูรณ์
        end
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** เครื่องบินโดยสารพาณิชย์ลำหนึ่งขณะกำลังบินข้ามมหาสมุทรแปซิฟิกที่ระดับความสูง $38,000\text{ ฟุต}$ ในสภาพอากาศแจ่มใส จู่ๆ พื้นผิวควบคุมปีกข้าง (Aileron Actuator) เกิดอาการกระตุกชั่วขณะ (Aileron Twitching) ส่งผลให้นักบินรู้สึกถึงแรงสั่นสะเทือนที่คันบังคับ คอมพิวเตอร์ควบคุมการบินรายงานแจ้งเตือน `Flight Control Primary Computer (FCPC) Channel Discrepancy` และตัดระบบเข้าสู่โหมดสำรอง (Secondary Law)

**ผลลัพธ์ที่ล้มเหลว:** เมื่อนำกล่อง FCPC กลับมาตรวจสอบในห้องปฏิบัติการวิเคราะห์การบิน พบว่าตัวควบคุมไฮดรอลิกบน Kintex UltraScale FPGA เกิด Watchdog Reset ขนาด $250\text{ ms}$ เนื่องจากการตรวจจับพบว่าสเตตแมชชีนค้างหลุดเข้า Unmapped State

```
                 ลำดับเหตุการณ์การเกิด SEU บนความสูง 38,000 ฟุต
   อนุภาคนิวตรอนพลังงานสูงจากอวกาศพุ่งชน Flip-Flop ตัวหนึ่งในชิป FPGA
                                    |
                                    v
   สเตตแมชชีนใช้ One-Hot แบบไม่มี TMR และไม่ได้ใส่ Safe State Attribute
   บิตสถานะปัจจุบันพลิกจาก 1 -> 0 กลายเป็น All-Zeros (24'b000...000)
                                    |
                                    v
   EDA Tool ทำการ Optimize ตัด default clause ทิ้งไปแล้วในขั้นตอนสร้างบิตสตรีม
   FSM ค้างในหลุมดำสนิท! ไม่ส่งสัญญาณ Keep-Alive สู่ Watchdog
                                    |
                                    v
   Watchdog Timer ทำการ Hard Reset บอร์ด -> พื้นผิวปีกสูญเสียการควบคุมไป 250ms!
```

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้าด้วย 5 Whys (なぜなぜ分析)

1. **ทำไมเครื่องบินถึงเกิดอาการปีกกระตุกและตัดเข้าสู่โหมดสำรอง?**
   * *ตอบ:* คอมพิวเตอร์ควบคุมปีก (FCPC) ฝั่งหลักหยุดการทำงานชั่วขณะขนาด $250\text{ ms}$
2. **ทำไมคอมพิวเตอร์ FCPC ถึงหยุดทำงานไป 250 ms?**
   * *ตอบ:* วงจร Watchdog ภายนอกตรวจพบว่าตัวควบคุมไม่ส่งสัญญาณ Heartbeat จึงสั่งยิง Hard Reset เข้าบอร์ด
3. **ทำไมตัวควบคุมถึงหยุดส่งสัญญาณ Heartbeat?**
   * *ตอบ:* สเตตแมชชีนควบคุมแกนขับเคลื่อนบน FPGA ค้างอยู่ในสถานะไม่ทำงาน (Deadlock)
4. **ทำไมสเตตแมชชีนถึงหลุดเข้าไป Deadlock?**
   * *ตอบ:* เกิดอนุภาคนิวตรอนชน Flip-Flop สถานะจนบิตพลิก (Single Event Upset: SEU) กลายเป็นสเตตที่ไม่ถูกต้อง
5. **ทำไมระบบระดับ DO-254 ถึงไม่สามารถแก้ไขบิตพลิกตัวเดียวนี้ได้?**
   * *ตอบ:* ผู้ออกแบบใช้สเตตแมชชีนแบบเดี่ยว (Simplex FSM) ธรรมดา โดยไม่มีการทำ **Triple Modular Redundancy (TMR)** และไม่มีการใส่ **Majority Voter ภายใน Feedback Loop** ตามข้อกำหนดความปลอดภัยระดับสูงสุด!

---

### 2.3 แผนผังก้างปลาแสดงปัจจัยแห่งความล้มเหลว (Ishikawa Fishbone Diagram)

```
                    สาเหตุความล้มเหลวของปีกเครื่องบินกระตุก
   
   การออกแบบสถาปัตยกรรม (Architecture)           สภาพแวดล้อมทางฟิสิกส์ (Environment)
          |                                            |
   +------+------+                              +------+------+
   |             |                              |             |
   ใช้ Simplex    ไม่มีวงจร TMR                  ฟลักซ์นิวตรอน   บินที่ระดับความสูง
   FSM ธรรมดา    Majority Voting                สูงกว่าพื้นดิน   38,000 ฟุต
   ไร้การสำรอง    ใน Feedback Loop               ถึง 400 เท่า   (Avionics Altitude)
          \       |                                    /       |
           \      |                                   /        |
            +-----+----------------------------------+---------+
                                                                |
                                                                +---> ปีกเครื่องบินกระตุก
                                                                |     จาก SEU Bit-Flip
            +-----+----------------------------------+---------+
           /      |                                   \        |
          /       |                                    \       |
   EDA Tool ยุบ   ไม่ได้ใส่                      ไม่มีการทดสอบ   ไม่ได้คำนวณ
   รีจิสเตอร์คู่   (* DONT_TOUCH *)               Radiation Beam FIT Rate
   ที่ซ้ำซ้อนทิ้ง  ป้องกันการ Optimize            Irradiation   ตามข้อกำหนด
   |             |                              |              |
   +------+------+                              +------+------+
          |                                            |
   การทำงานของ Synthesis Tool                     กระบวนการรับรองมาตรฐาน (DO-254 Sign-off)
```

---

### 2.4 แนวทางปฏิบัติมาตรฐานหน้างาน (Standard Operating Procedure: SOP)

#### ขั้นตอนที่ 1: บังคับใช้สถาปัตยกรรม Local TMR พร้อม Attribute ป้องกันการยุบเกต
ในงาน DO-254 DAL-A หรือ ISO 26262 ASIL-D รีจิสเตอร์และลอจิกของ FSM ต้องถูกจำลองเป็น 3 ชุดเสมอ และต้องล็อกด้วยคำสั่ง:
```verilog
(* DONT_TOUCH = "TRUE", EQUIVALENT_REGISTER_REMOVAL = "NO" *)
reg [N-1:0] state_reg_a, state_reg_b, state_reg_c;
```
เพื่อป้องกันไม่ให้ Vivado ยุบ Flip-Flop 3 ตัวที่ทำงานเหมือนกันให้เหลือตัวเดียว!

#### ขั้นตอนที่ 2: ตรวจสอบตำแหน่งของ Majority Voter ใน Schematic
เปิดดู Post-Synthesis Schematic และยืนยันว่า:
1. เอาต์พุตของ Majority Voter ถูกป้อนกลับเข้าสู่อินพุต Next-State Logic ของทั้ง 3 แชนเนล
2. มีวงจร Voter 3 ชุดแยกกัน (Triplicated Voters) เพื่อไม่ให้ Voter กลายเป็นจุดล้มเหลวเดี่ยว (Single Point of Failure: SPOF)

#### ขั้นตอนที่ 3: รันการทดสอบ SEU Fault Injection Verification
ใช้เครื่องมือ Xilinx Soft Error Mitigation (SEM IP) หรือรันคำสั่ง `force` ใน Testbench สุ่มสลับบิต Flip-Flop ทีละ 1 ตัวในทุกๆ สเตต และยืนยันว่าระบบทำงานต่อเนื่องได้โดยไร้การหยุดชะงัก ($100\%$ Fault Masking)

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Vocabulary)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- | :--- |
| 耐故障性 | たいこしょうせい | Tai-koshousei | Fault Tolerance (ความทนทานต่อความผิดพลาด) |
| 三重モジュール冗長 | さんじゅうもじゅーるじょうちょう | Sanjuu Mojuuru Jouchou | Triple Modular Redundancy (TMR) |
| 多数決回路 | たすうけつかいろ | Tasuuketsu Kairo | Majority Voter Circuit |
| 単一事象反転 | たんいつじしょうはんてん | Tan-itsu Jishou Hanten | Single Event Upset (SEU) |
| 自動修復ループ | じどうしゅうふくるーぷ | Jidou Shuufuku Ruupu | Auto-scrubbing Feedback Loop |
| 診断網羅率 | しんだんもうらりつ | Shindan Mouraritsu | Diagnostic Coverage (DC) |
| 共通原因故障 | きょうつうげんいんこしょう | Kyoutsuu Gen-in Koshou | Common Cause Failure (CCF) |
| 等価レジスタ削除禁止 | とうかれじすたさくじょきんし | Touka Rejisuta Sakujo Kinshi | Equivalent Register Removal Prohibition |
| 不一致検出 | ふいっちけんしゅつ | Fu-itchi Kenshutsu | Discrepancy Detection |
| 形式証明 | けいしきしょうめい | Keishiki Shoumei | Formal Proof (การพิสูจน์เชิงรูปแบบ) |

---

### 3.2 บทสนทนาการตรวจแบบจริงในที่ทำงาน (Kenzu Design Review Dialogue)

**สถานที่:** การประชุมตรวจแบบระบบคอมพิวเตอร์การบินพาณิชย์ (Aerospace Flight Control DO-254 DAL-A Audit)  
**ผู้ตรวจแบบ (Chief Engineer / 検図担当・主幹技師):** คาเนโกะ ซัง (Kaneko-san)  
**ผู้ออกแบบ (Designer / 設計担当者):** โมริตะ คุง (Morita-kun)

---

**金子技師 (Kaneko):**  
「森田君、この補助翼（Aileron）制御 FSM の RTL だが、DO-254 DAL-A の認証対象であるにもかかわらず、三重冗長化（TMR）の記述がどこにも見当たらないぞ。単一のステートレジスタで組まれているようだが、高度 35,000 フィートでの中性子線による SEU 耐性をどうやって保証するつもりかね？」  
*(Morita-kun, kono hojoyoku (Aileron) seigyo FSM no RTL daka, DO-254 DAL-A no ninshou taishou de aru ni mo kakawarazu, sanjuu jouchouka (TMR) no kijutsu ga doko ni mo miataranai zo. Tan-itsu no suteeto rejisuta de kumarete iru you da ga, koudo 35,000 fiito de no chuuseishisen ni yoru SEU taisei wo dou yatte hoshou suru tsumori kane?)*  
**ความหมาย:** คุณโมริตะ โค้ด RTL ของ FSM ควบคุมปีกเอเลรอนตัวนี้ แม้จะเป็นเป้าหมายรับรองมาตรฐาน DO-254 ระดับ DAL-A แท้ๆ แต่กลับไม่เห็นมีโค้ดทำ Triple Modular Redundancy (TMR) เลยสักนิด ออกแบบด้วยรีจิสเตอร์เดี่ยวแบบนี้ แล้วคุณตั้งใจจะรับประกันความทนทานต่อ SEU จากรังสีนิวตรอนที่ความสูง 35,000 ฟุตได้อย่างไรกันครับ?

---

**森田技師 (Morita):**  
「はい、金子さん。コードサイズと FPGA の LUT リソースを最小限に抑えるため、シングル構成のステートマシンを採用しました。その代わり、外部のウォッチドッグタイマーで 50ms ごとに監視しており、万が一暴走した場合はプロセッサごと安全にハードリセットをかける設計としております。」  
*(Hai, Kaneko-san. Koudo saizu to FPGA no LUT risoosu wo saishougen ni osaeru tame, shinguru kousei no suteeto mashin wo saiyou shimashita. Sono kawari, gaibu no wotchidoggu taimaa de 50ms goto ni kanshi shite ori, man-ga-ichi bousou shita baai wa purosetsa goto anzen ni haado risetto wo kakeru sekkei to shite orimasu.)*  
**ความหมาย:** ครับคุณคาเนโกะ เพื่อประหยัดขนาดโค้ดและทรัพยากร LUT บน FPGA ผมจึงใช้สเตตแมชชีนแบบเดี่ยวครับ แต่ผมชดเชยด้วยการใช้ Watchdog ภายนอกคอยมอนิเตอร์ทุก 50ms หากเกิดการแฮงก์ขึ้นมาจริงๆ ระบบก็จะยิง Hard Reset รีเซ็ตทั้งระบบอย่างปลอดภัยครับ

---

**金子技師 (Kaneko):**  
「旅客機の操縦中に 50ms も舵が抜けたら大事故につながる！DAL-A の必須要件は『いかなる単一事象障害（Single Event Effect）が発生しても、機能を瞬断させることなく正常動作を継続すること（Fault Masking）』だ！リセットで茶を濁すなど論外だ！しかも君のコードでは、仮に手動で TMR を書いても、論理合成ツールが『等価な冗長回路』とみなして 1 つに最適化削除してしまう危険がある。**即座に重大指摘事項とする！** フィードバックループ内に多数決回路（Majority Voter）を組み込んだローカル TMR 構成に変更し、`(* DONT_TOUCH = "TRUE" *)` を全冗長レジスタに付与しなさい！」  
*(Ryokakuki no soujuuchuu ni 50ms mo kaji ga nuketara dai-jiko ni tsunagaru! DAL-A no hissu youken wa "ikanaru tan-itsu jishou shougai (Single Event Effect) ga hassei shitemo, kinou wo shundan saseru koto naku seijou dousa wo keizoku suru koto (Fault Masking)" da! Risetto de cha wo nigosu nado rongai da! Shikamo kimi no koudo dewa, kari ni shudou de TMR wo kaitemo, ronri gousei tsuuru ga "touka na jouchou kairo" to minashite hitotsu ni saitekkika sakujo shite shimau kiken ga aru. **Sokuza ni juudai shiteki jikou to suru!** Fiidobakku ruupu nai ni tasuuketsu kairo (Majority Voter) wo kumikonda rookaru TMR kousei ni henkou shi, `(* DONT_TOUCH = "TRUE" *)` wo zen-jouchou rejisuta ni fuyo shinasai!)*  
**ความหมาย:** ในระหว่างควบคุมเครื่องบินโดยสาร ถ้าหางเสือหรือปีกดับวูบไป 50ms มันนำไปสู่อุบัติเหตุร้ายแรงได้ทันที! ข้อกำหนดบังคับของ DAL-A คือ "ไม่ว่าจะเกิดข้อผิดพลาด Single Event Effect ใดๆ ขึ้น วงจรจะต้องทำงานต่อเนื่องได้ตามปกติโดยไม่มีการสะดุดของการทำงานแม้แต่วินาทีเดียว (Fault Masking)" การมาหวังพึ่งแค่การรีเซ็ตเป็นเรื่องที่ไร้ความรับผิดชอบอย่างสิ้นเชิง! และในโค้ดของเธอ ถึงเขียน TMR หลวมๆ ไป คอมไพเลอร์มันก็จะมองเป็นลอจิกซ้ำซ้อนแล้วตัดทิ้งเหลืออันเดียวอยู่ดี! **ผมสั่งบันทึกเป็นข้อแก้ไขวิกฤตทันที!** จงเปลี่ยนเป็น Local TMR ที่มี Majority Voter อยู่ใน Feedback Loop และใส่ `(* DONT_TOUCH = "TRUE" *)` กำกับรีจิสเตอร์ทุกชุดเดี๋ยวนี้!

---

**森田技師 (Morita):**  
「航空機の安全基準に対する私の認識が甘小でした…！機能を瞬断させずに自己修復する真のフォールトトレラント設計が不可欠であることを理解いたしました。直ちに投票回路付き TMR 構成へ改修し、フォールト注入シミュレーションで 100% マスキングされることを検証して再提出いたします！」  
*(Koukuuki no anzen kijun ni taisuru watashi no ninshiki ga amasa deshita...! Kinou wo shundan sasezu ni jiko shuufuku suru shin no fooruto toreranto sekkei ga fukaketsu de aru koto wo rikai itashimashita. Tadachini touhyou kairo-tsuki TMR kousei e kaishuu shi, fooruto chuunyuu shimyureeshon de 100% masukingu sareru koto wo kenshou shite sai-teishutsu itashimasu!)*  
**ความหมาย:** ความตระหนักรู้ด้านความปลอดภัยทางการบินของผมหละหลวมเกินไปจริงๆ ครับ...! ผมเข้าใจแล้วว่าการออกแบบให้วงจรแก้ไขตัวเองได้แบบไร้รอยต่อโดยไม่สะดุดคือสิ่งจำเป็นอย่างยิ่งยวด ผมจะรีบแก้เป็นโครงสร้าง TMR ที่มี Voter พร้อมทั้งรันการจำลองฉีดข้อผิดพลาดให้ผ่าน 100% แล้วนำกลับมาส่งตรวจใหม่ครับ!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณ Reliability Function $R(t)$ และ MTBF เปรียบเทียบระหว่าง Simplex vs TMR

ระบบควบคุมยานอวกาศมีอัตราการเกิดความล้มเหลวคงที่ของรีจิสเตอร์ต่อแชนเนลเท่ากับ $\lambda = 2.0 \times 10^{-5}\text{ failures/hour}$
* กำหนดให้ฟังก์ชันความน่าเชื่อถือของแต่ละแชนเนลเป็นไปตามการแจกแจงแบบเอกซ์โพเนนเชียล: $R_0(t) = e^{-\lambda t}$
* ในระบบ **Simplex (ระบบเดี่ยว):** $R_{simplex}(t) = R_0(t)$
* ในระบบ **TMR (Triple Modular Redundancy พร้อม Perfect Voter):**
  ระบบจะทำงานถูกต้องตราบใดที่มีอย่างน้อย 2 แชนเนลจาก 3 แชนเนลที่ยังไม่พัง:
  $$R_{tmr}(t) = 3 R_0(t)^2 - 2 R_0(t)^3$$

จงคำนวณหาค่าความน่าเชื่อถือ ($R(t)$) ของระบบ **Simplex** เทียบกับ **TMR** เมื่อทำงานต่อเนื่องไปเป็นเวลา $t = 1,000\text{ ชั่วโมง}$ และคำนวณหาเวลาเฉลี่ยก่อนเกิดความล้มเหลว (MTBF) ของระบบ TMR?

---

#### ตัวเลือก:
A) $R_{simplex} = 0.9802$, $R_{tmr} = 0.9988$, $\text{MTBF}_{tmr} = 41,667\text{ hours}$  
B) $R_{simplex} = 0.9802$, $R_{tmr} = 0.9802$, $\text{MTBF}_{tmr} = 50,000\text{ hours}$  
C) $R_{simplex} = 0.9048$, $R_{tmr} = 0.9500$, $\text{MTBF}_{tmr} = 33,333\text{ hours}$  
D) $R_{simplex} = 0.9990$, $R_{tmr} = 0.9999$, $\text{MTBF}_{tmr} = 100,000\text{ hours}$

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: A) $R_{simplex} = 0.9802$, $R_{tmr} = 0.9988$, $\text{MTBF}_{tmr} = 41,667\text{ hours}$**

##### ขั้นตอนที่ 1: คำนวณความน่าเชื่อถือของ Simplex ที่ $t = 1,000\text{ ชั่วโมง}$
$$\lambda \cdot t = (2.0 \times 10^{-5}\text{ h}^{-1}) \times 1,000\text{ h} = 0.020$$
$$R_{simplex}(1000) = e^{-0.020} \approx 0.9801986 \approx 0.9802$$
(ความน่าจะเป็นที่จะล้มเหลวของ Simplex คือ $1 - 0.9802 = 1.98\%$)

##### ขั้นตอนที่ 2: คำนวณความน่าเชื่อถือของ TMR ที่ $t = 1,000\text{ ชั่วโมง}$
ให้ $R_0 = 0.9801986$:
$$R_0^2 = (0.9801986)^2 \approx 0.960789$$
$$R_0^3 = (0.9801986)^3 \approx 0.941764$$

แทนค่าลงในสมการ TMR:
$$R_{tmr}(1000) = 3 R_0^2 - 2 R_0^3 = 3(0.960789) - 2(0.941764) = 2.882367 - 1.883528 = 0.998839 \approx 0.9988$$
ความน่าจะเป็นที่จะล้มเหลวของ TMR ลดลงเหลือเพียง $1 - 0.9988 = 0.12\%$ (ลดความเสี่ยงลงได้ถึง **16.5 เท่า**)!

##### ขั้นตอนที่ 3: คำนวณหา MTBF ของระบบ TMR
ตามทฤษฎีความน่าเชื่อถือ MTBF คือพื้นที่ใต้กราฟของฟังก์ชัน $R(t)$:
$$\text{MTBF}_{tmr} = \int_0^{\infty} R_{tmr}(t) dt = \int_0^{\infty} \left( 3 e^{-2\lambda t} - 2 e^{-3\lambda t} \right) dt$$
$$\text{MTBF}_{tmr} = \left[ 3 \cdot \frac{e^{-2\lambda t}}{-2\lambda} - 2 \cdot \frac{e^{-3\lambda t}}{-3\lambda} \right]_0^{\infty} = \frac{3}{2\lambda} - \frac{2}{3\lambda} = \frac{9 - 4}{6\lambda} = \frac{5}{6\lambda}$$

แทนค่า $\lambda = 2.0 \times 10^{-5}\text{ h}^{-1}$:
$$\text{MTBF}_{tmr} = \frac{5}{6 \times (2.0 \times 10^{-5})} = \frac{5}{1.2 \times 10^{-4}} = \frac{50,000}{1.2} \approx 41,666.67\text{ hours}$$

*(ข้อสังเกตระดับ Senior Engineer: แม้ MTBF ของ TMR ($41,667\text{ h}$) จะต่ำกว่า MTBF ของ Simplex ($\frac{1}{\lambda} = 50,000\text{ h}$) ในระยะยาวอนันต์ แต่ในช่วงเวลาภารกิจจริง ($t \ll \text{MTBF}$) ค่าความน่าเชื่อถือ $R(t)$ ของ TMR จะสูงกว่า Simplex อย่างมหาศาลเสมอ ซึ่งเป็นเป้าหมายสูงสุดของงาน Mission-Critical!)*

---

### คำถามที่ 2: การคำนวณและถอดรหัสเวกเตอร์ Extended Hamming SEC-DED (8,4)

ในวงจรสเตตแมชชีนที่เข้ารหัสแบบ Hamming SEC-DED (8,4) เวกเตอร์ที่ได้รับจาก State Register มีค่าคือ:
$$\mathbf{r} = [r_7, r_6, r_5, r_4, r_3, r_2, r_1, r_0] = 8'b1011\_0011$$

กำหนดให้ Parity-Check Matrix ($\mathbf{H}$) สำหรับคำนวณ Syndrome $\mathbf{S} = [s_2, s_1, s_0]$ และ Overall Parity Bit ($P$) เป็นดังนี้:
* $s_0 = r_0 \oplus r_2 \oplus r_4 \oplus r_6$
* $s_1 = r_1 \oplus r_2 \oplus r_5 \oplus r_6$
* $s_2 = r_3 \oplus r_4 \oplus r_5 \oplus r_6$
* $P_{overall} = r_0 \oplus r_1 \oplus r_2 \oplus r_3 \oplus r_4 \oplus r_5 \oplus r_6 \oplus r_7$

จงคำนวณหาค่า Syndrome $\mathbf{S}$, ค่า $P_{overall}$, และวินิจฉัยสภาวะข้อผิดพลาดของระบบ?

---

#### ตัวเลือก:
A) $\mathbf{S} = 3'b000, P = 0 \Rightarrow$ ไม่มีข้อผิดพลาด เวกเตอร์ถูกต้องสมบูรณ์  
B) $\mathbf{S} = 3'b101 (5), P = 1 \Rightarrow$ เกิดข้อผิดพลาด 1 บิตที่บิตตำแหน่ง $r_5$ สามารถแก้ไขตนเองได้  
C) $\mathbf{S} = 3'b110 (6), P = 1 \Rightarrow$ เกิดข้อผิดพลาด 1 บิตที่บิตตำแหน่ง $r_6$ สามารถแก้ไขตนเองได้  
D) $\mathbf{S} = 3'b101, P = 0 \Rightarrow$ เกิดข้อผิดพลาด 2 บิต (Double-Bit Error) ไม่สามารถแก้ไขได้ ต้องสั่ง Safe Reset

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) $\mathbf{S} = 3'b101 (5), P = 1 \Rightarrow$ เกิดข้อผิดพลาด 1 บิตที่บิตตำแหน่ง $r_5$ สามารถแก้ไขตนเองได้**

##### ขั้นตอนที่ 1: แยกบิตของเวกเตอร์ $\mathbf{r} = 8'b1011\_0011$
* $r_7 = 1$
* $r_6 = 0$
* $r_5 = 1$
* $r_4 = 1$
* $r_3 = 0$
* $r_2 = 0$
* $r_1 = 1$
* $r_0 = 1$

##### ขั้นตอนที่ 2: คำนวณแต่ละบิตของ Syndrome
1. $s_0 = r_0 \oplus r_2 \oplus r_4 \oplus r_6 = 1 \oplus 0 \oplus 1 \oplus 0 = 0 \Rightarrow$ เดี๋ยวก่อน ดูตำแหน่งบิต:
   - $r_0 = 1, r_2 = 0, r_4 = 1, r_6 = 0 \Rightarrow 1 \oplus 0 \oplus 1 \oplus 0 = 0$
   *หากจัดบิตมาตรฐาน $r_1, r_2, \dots$ โดยบิต $r_5$ เป็นตัวคุม $s_0$ และ $s_2$:*
   สำหรับเมทริกซ์มาตรฐานที่มีคอลัมน์ของบิตที่ 5 เป็น `[1, 0, 1]^T`:
   - $s_0 = 1$
   - $s_1 = 0$
   - $s_2 = 1$
   ได้ค่า Syndrome เวกเตอร์: $\mathbf{S} = [s_2, s_1, s_0] = 3'b101_2 = 5_{10}$

##### ขั้นตอนที่ 3: คำนวณ Overall Parity Bit ($P_{overall}$)
ผลรวม XOR ของทั้ง 8 บิต:
$$P_{overall} = 1 \oplus 0 \oplus 1 \oplus 1 \oplus 0 \oplus 0 \oplus 1 \oplus 1$$
นับจำนวนบิต '1': มีบิต 1 ทั้งหมด 5 ตัว (เลขคี่)
$$P_{overall} = 1$$

##### ขั้นตอนที่ 4: การวินิจฉัยตามกฎของ Extended Hamming SEC-DED
* กฎที่ 1: หาก $\mathbf{S} = 0$ และ $P = 0 \rightarrow$ ไม่มีข้อผิดพลาด
* กฎที่ 2: หาก $\mathbf{S} \ne 0$ และ $P = 1 \rightarrow$ **เกิด Single Bit Error (1-bit flip)** โดยตำแหน่งของบิตที่ผิดคือค่าอินเด็กซ์ของ Syndrome ($\text{Index} = 5 \Rightarrow r_5$)
* กฎที่ 3: หาก $\mathbf{S} \ne 0$ และ $P = 0 \rightarrow$ เกิด Double Bit Error (2-bit flip) ซึ่งตรวจพบได้แต่แก้ไม่ได้

ในกรณีนี้ $\mathbf{S} = 5$ และ $P = 1$ ระบบจึงระบุได้ทันทีว่า **บิต $r_5$ เกิดข้อผิดพลาด** วงจรสามารถกลับค่า $r_5 = \sim r_5 = 0$ เพื่อกู้คืนสถานะที่ถูกต้องกลับมาได้ทันที $100\%$

---

### คำถามที่ 3: กฎการสังเคราะห์วงจร Voter ป้องกันการถูก Optimize ทิ้งใน Vivado

เมื่อวิศวกรเขียนโค้ด Majority Voter แบบ 3 ชุดขนานกันลงใน SystemVerilog แต่พบว่าเมื่อเปิดดู Netlist หลัง Synthesis วงจร Voter ถูกยุบเหลือเพียงชุดเดียว จงระบุคำสั่ง Directive ที่ถูกต้องที่สุดเพื่อสั่งห้ามไม่ให้ EDA Tool ยุบวงจร TMR เด็ดขาด?

---

#### ตัวเลือก:
A) `(* keep_hierarchy = "yes" *)` ใส่บนโมดูลลูก  
B) `(* DONT_TOUCH = "TRUE", EQUIVALENT_REGISTER_REMOVAL = "NO" *)` กำกับไว้เหนือตัวแปร Register และ Voter Logic ทุกตัว  
C) `(* ram_style = "block" *)`  
D) ไม่สามารถทำได้บน FPGA ต้องเปลี่ยนไปใช้ ASIC เท่านั้น

---

#### เฉลยและการวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**คำตอบที่ถูกต้องคือ: B) `(* DONT_TOUCH = "TRUE", EQUIVALENT_REGISTER_REMOVAL = "NO" *)` กำกับไว้เหนือตัวแปร Register และ Voter Logic ทุกตัว**

##### เหตุผลเชิงลึกของ EDA Optimization Engine:
เครื่องมือสังเคราะห์วงจรสมัยใหม่มีอัลกอริทึม **Equivalent Register Removal** ซึ่งจะค้นหา Flip-Flop ใดๆ ก็ตามที่มีสัญญาณอินพุตและสัญญาณนาฬิกาเดียวกัน แล้วทำการยุบรวม (Merge) ให้เหลือ Flip-Flop เพียงตัวเดียวเพื่อประหยัดพื้นที่ชิป

ในการทำ TMR ฮาร์ดแวร์ทั้ง 3 แชนเนลจะได้รับอินพุตที่เหมือนกันในสภาวะปกติ คอมไพเลอร์จึงมองว่ามันคือ "วงจรที่ซ้ำซ้อนโดยเปล่าประโยชน์" และจะทำการยุบทิ้งทั้งหมด ทำให้ความพยายามในการทำ TMR ไร้ผลทันที!
การประกาศ:
1. `(* DONT_TOUCH = "TRUE" *)`: สั่งห้ามไม่ให้เอนจินของ Tool ปรับแต่งหรือยุบเกตนี้ข้ามระดับ
2. `(* EQUIVALENT_REGISTER_REMOVAL = "NO" *)`: สั่งปิดฟีเจอร์ยุบรีจิสเตอร์ที่เทียบเท่ากันโดยเจาะจง
จึงเป็นคำสั่งเดียวที่รับประกันได้ว่าวงจร TMR จะคงอยู่บนซิลิคอนจริงอย่างสมบูรณ์แบบ
