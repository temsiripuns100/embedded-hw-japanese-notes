# Lesson 176: FPGA CDC Part 6 - Reset Synchronizers (Asynchronous Assert / Synchronous Deassert, Recovery & Removal Timing Physics, Reset Tree Fanout & Metastability Mitigations)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์การรีเซ็ต: Asynchronous ล้วน เทียบกับ Synchronous ล้วน
ในการออกแบบวงจรดิจิทัลขนาดใหญ่บน FPGA สัญญาณรีเซ็ต (Reset) ถือเป็นสัญญาณควบคุมที่มีความสำคัญและมีจำนวนโหลด (Fanout) มากที่สุดเป็นอันดับสองรองจากสัญญาณนาฬิกา การตัดสินใจเลือกรูปแบบของสัญญาณรีเซ็ตมักเป็นจุดเริ่มต้นของความล้มเหลวร้ายแรงหากวิศวกรไม่เข้าใจฟิสิกส์ของการทำงาน:

```
          การเปรียบเทียบเชิงฟิสิกส์ระหว่าง ASYNCHRONOUS RESET และ SYNCHRONOUS RESET
          
   [ 1. PURE SYNCHRONOUS RESET ]              [ 2. PURE ASYNCHRONOUS RESET ]
   
        CLK ───/‾\_/‾\_/‾\_/‾\_                    CLK ───/‾\_/‾\_/‾\_/‾\_
      RST_N ─────\____________                  RST_N ─────\____________
                                                              ▲
              ▲ (ต้องรอขอบ CLK!)                              │ (รีเซ็ตทันที ไม่สน CLK!)
          Q ──────\____________                     Q ────────\__________
          
   ข้อดี: ปลอด Metastability 100%             ข้อดี: บังคับรีเซ็ตได้ทันทีแม้ CLK ดับ
   วิกฤต: หาก PLL ยังไม่ล็อก ระบบไม่รีเซ็ต!    วิกฤต: จังหวะปลดรีเซ็ตเกิด METASTABILITY!
```

#### 1. วิกฤตของ Pure Synchronous Reset:
* ข้อดี: การเปลี่ยนสถานะเกิดขึ้นตรงขอบสัญญาณนาฬิกาเสมอ ทำให้เครื่องมือ Static Timing Analysis (STA) สามารถวิเคราะห์ Setup Time และ Hold Time ได้ตามปกติ
* วิกฤต: หากระบบอยู่ในช่วงเริ่มต้นจ่ายไฟ (Power-on Sequence) ซึ่งวงจรคริสตัลออสซิลเลเตอร์ยังไม่เสถียร หรือวงจร MMCM/PLL ยังไม่ล็อกความถี่ (`LOCKED = 0`) สัญญาณนาฬิกาจะยังไม่มี ส่งผลให้ **ฟลิปฟล็อปจะไม่ยอมเข้าสู่สถานะเริ่มต้น (Uninitialized Floating State)** อุปกรณ์ภายนอกอาจได้รับสัญญาณควบคุมมั่วซั่วจนเกิดความเสียหาย!

#### 2. วิกฤตของ Pure Asynchronous Reset:
* ข้อดี: สามารถบังคับให้ฟลิปฟล็อปทุกตัวในชิปเข้าสู่สถานะปลอดภัยได้ทันที โดยไม่ต้องรอสัญญาณนาฬิกา
* วิกฤต: **จังหวะการปลดรีเซ็ต (Reset Deassertion / Release):** เมื่อสัญญาณรีเซ็ตเปลี่ยนจาก Active กลับสู่ Inactive หากขอบสัญญาณนี้เกิดขึ้นเฉียดฉิวกับขอบสัญญาณนาฬิกา จะเกิดการละเมิดข้อกำหนด **Recovery Time** หรือ **Removal Time** ทันที ส่งผลให้ฟลิปฟล็อปเกิด Metastability หรือฟลิปฟล็อปบางตัวหลุดจากรีเซ็ตในไซเคิล $N$ ในขณะที่บางตัวหลุดในไซเคิล $N+1$!

---

### 1.2 สถาปัตยกรรม Asynchronous Assert, Synchronous Deassert (AASD / Reset Bridge)

เพื่อรวมข้อดีของทั้งสองรูปแบบและกำจัดความเสี่ยง Metastability ทิ้งไป สถาปัตยกรรมมาตรฐานสากลที่ทุกระบบ Mission-Critical ต้องใช้คือ **Asynchronous Assert, Synchronous Deassert (AASD)** หรือที่รู้จักกันในชื่อ **Reset Synchronizer (Reset Bridge)**:

```
               สถาปัตยกรรม RESET SYNCHRONIZER (RESET BRIDGE)
               
      VCC (1'b1) ──┐
                   ▼
                 ┌───┐            ┌───┐
                 │ D │            │ D │
                 │   ├── rst_s1 ──┤   ├── rst_sync_n (ปลอดภัย 100%)
                 │   │            │   │   (ขอบ Deassert ตรงกับ CLK)
      CLK ───────┤CLK│       ┌────┤CLK│
                 └───┘       │    └───┘
                   ▲ CLR_N   │      ▲ CLR_N
                   │         │      │
      rst_async_n ─┴─────────┴──────┴─────── (Assert ทันทีแบบ Asynchronous)
                   (เข้าขา Asynchronous Clear ของทั้ง 2 สเตจ)
```

#### กลไกการทำงานระดับทรานซิสเตอร์ (Circuit Dynamics):
1. **เมื่อสัญญาณ Reset ถูกสั่งทำงาน (Assertion: `rst_async_n = 0`):**
   * สัญญาณระดับต่ำจะวิ่งเข้าขา Asynchronous Clear/Preset (`CLR_N`) ของฟลิปฟล็อปทั้งสองตัวโดยตรง
   * เอาต์พุต `rst_sync_n` จะตกลงสู่ `0` ในทันทีทันใดด้วยความเร็วของ Propagation Delay ภายในเกต โดย **ไม่ต้องรอขอบสัญญาณนาฬิกา CLK เลยแม้แต่เสี้ยววินาทีเดียว!**
2. **เมื่อสัญญาณ Reset ถูกปลดออก (Deassertion: `rst_async_n = 1`):**
   * ขา Asynchronous Clear ถูกปลดออก ทว่าขา D ของฟลิปฟล็อปตัวแรกผูกติดอยู่กับลอจิกคงที่ (`1'b1` หรือ `VCC`)
   * ขอบสัญญาณ `1'b1` จะต้องเดินทางผ่านฟลิปฟล็อปตัวที่ 1 และตัวที่ 2 ตามขอบขาขึ้นของ `CLK`
   * หากจังหวะปลด `rst_async_n` เกิดเฉียดฉิวกับขอบ CLK จนตัวแรกเกิด Metastability ตัวที่ 2 จะทำหน้าที่เป็นตัวกรองคลายตัว (Metastability Filter)
   * ผลลัพธ์: สัญญาณ `rst_sync_n` จะปลดออกสู่ลอจิก `1` **ตรงขอบสัญญาณนาฬิกา CLK อย่างนุ่มนวลและปราศจาก Metastability เสมอ $100\%$!**

```verilog
// แม่แบบสถาปัตยกรรม Reset Bridge (AASD) ระดับ Senior พร้อม ASYNC_REG
(* keep_hierarchy = "yes" *)
module reset_bridge_aasd (
    input  wire clk,
    input  wire rst_async_n,    // สัญญาณรีเซ็ตดิบภายนอก (Active-Low)
    output wire rst_sync_n      // สัญญาณรีเซ็ตซิงโครไนซ์แล้วสำหรับโดเมนนี้
);

    (* ASYNC_REG = "TRUE" *) reg rst_ff1;
    (* ASYNC_REG = "TRUE" *) reg rst_ff2;

    always @(posedge clk or negedge rst_async_n) begin
        if (!rst_async_n) begin
            rst_ff1 <= 1'b0;    // Asynchronous Assert ทันที
            rst_ff2 <= 1'b0;
        end else begin
            rst_ff1 <= 1'b1;    // Synchronous Deassert ผ่าน 2 สเตจ
            rst_ff2 <= rst_ff1;
        end
    end

    assign rst_sync_n = rst_ff2;

endmodule
```

---

### 1.3 ฟิสิกส์ของ Recovery Time และ Removal Time

ในเครื่องมือ Static Timing Analysis (STA) เช่น Vivado Timing Engine สัญญาณรีเซ็ตที่ผ่านเข้าขา Asynchronous Reset จะต้องถูกตรวจสอบตามสมการความปลอดภัยของ **Recovery Time** และ **Removal Time**:

```
                 ฟิสิกส์ของ RECOVERY TIME และ REMOVAL TIME
                 
         CLK         : ──────────────────────────────/‾‾‾‾‾‾‾‾‾‾‾‾‾\_______
                                                     ▲
                                              (Clock Active Edge)
                       ├─────────────────────────────┤─────────────┤
                                Recovery Window         Removal Window
                       
    RST_N (ถูกต้อง)   : ───────────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
                                   ▲ (ปลดก่อนขอบ CLK นานพอ: ผ่าน Recovery!)
                                   
    RST_N (ถูกต้อง)   : ________________________________───────────────/‾‾‾
                                                                       ▲
                                                   (ปลดหลังขอบ CLK นานพอ: ผ่าน Removal!)
                                                   
    RST_N (อันตราย!)  : ───────────────────────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
                                               ▲ (ตกในหน้าต่างห้าม: METASTABLE!)
```

#### 1. Recovery Time ($T_{rec}$):
* **นิยาม:** คือระยะเวลาขั้นต่ำที่สุดที่สัญญาณรีเซ็ตจะต้องถูกปลดออก (Inactive) **ก่อนที่ขอบสัญญาณนาฬิกาถัดไปจะมาถึง** (มีพฤติกรรมเสมือน Setup Time ของขา Reset)
* **สูตรการคำนวณ Recovery Slack:**
  $$T_{slack,rec} = T_{clk} - (T_{clk\_skew} + t_{prop,max}(rst) + T_{rec})$$
* **ผลลัพธ์เมื่อละเมิด ($T_{slack,rec} < 0$):** ฟลิปฟล็อปไม่สามารถคืนสถานะวงจรป้อนกลับภายใน (Internal Regenerative Feedback) ได้ทัน ข้อมูลที่ควรจะเริ่มประมวลผลในรอบถัดไปจะกลายเป็นสภาวะก้ำกึ่ง (Metastable)

#### 2. Removal Time ($T_{rem}$):
* **นิยาม:** คือระยะเวลาขั้นต่ำที่สุดที่สัญญาณรีเซ็ตจะต้องคงสถานะ Active ไว้ **หลังจากขอบสัญญาณนาฬิกาผ่านพ้นไปแล้ว** (มีพฤติกรรมเสมือน Hold Time ของขา Reset)
* **สูตรการคำนวณ Removal Slack:**
  $$T_{slack,rem} = t_{prop,min}(rst) - (T_{clk\_skew} + T_{rem})$$
* **ผลลัพธ์เมื่อละเมิด ($T_{slack,rem} < 0$):** สัญญาณรีเซ็ตปลดตัวเร็วเกินไป ทำให้ขอบนาฬิกาเดิมที่เพิ่งผ่านไปแซมเปิลข้อมูลใหม่ทั้งที่ควรจะยังถูกรีเซ็ตอยู่

---

### 1.4 ปรากฏการณ์ Half-Reset และความล้มเหลวของ State Machine

สมมติว่าในระบบมี State Machine ขนาด 3 บิต ควบคุมวาล์วปล่อยเชื้อเพลิงจรวด ซึ่งประกอบด้วยฟลิปฟล็อป $FF_0, FF_1, FF_2$ กระจายตัวอยู่ใน Slice ต่างๆ บน FPGA:

```
        ปรากฏการณ์ HALF-RESET STATE (DEASSERTION SKEW CATASTROPHE)
        
                  Reset Tree Skew ทำให้ขอบ Deassert ไปถึงแต่ละ FF ไม่พร้อมกัน!
                  
    CLK Edge       : ──────────────────────────────/‾‾‾‾‾‾‾‾‾‾‾‾‾\_______
                                                   ▲
    RST ถึง FF_0   : ──────────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾│ (พ้น Recovery แล้ว) ==> หลุด Reset ใน Cycle นี้!
    RST ถึง FF_1   : ─────────────/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾│ (พ้น Recovery แล้ว) ==> หลุด Reset ใน Cycle นี้!
    RST ถึง FF_2   : ──────────────────────────/‾‾‾│ (ละเมิด Recovery!)  ==> ยังค้าง Reset ไปอีก 1 Cycle!
    
    ผลลัพธ์ของสถานะ FSM:
    * สถานะ Reset ที่ควรจะเป็น : 3'b000 (IDLE)
    * สถานะ Cycle ถัดไปที่คาดหวัง : 3'b001 (START)
    * สถานะจริงที่เกิดขึ้น        : 3'b011 หรือ 3'b010 (ILLEGAL STATE / UNMAPPED STATE!)
    ===> วาล์วเปิดฉุกเฉิน เชื้อเพลิงรั่วไหล เกิดอุบัติเหตุร้ายแรง!
```

นี่คือสาเหตุที่ฟิสิกส์ไม่อนุญาตให้ใช้สายสัญญาณ Reset ภายนอกต่อตรงเข้าฟลิปฟล็อปนับหมื่นตัวโดยไม่มี Reset Synchronizer เฉพาะของแต่ละโดเมน!

---

### 1.5 ข้อพิจารณาเชิงสถาปัตยกรรมชิป: Active-High vs Active-Low บน AMD Xilinx UltraScale+

ความเข้าใจผิดที่พบบ่อยอีกประการคือ การใช้สัญญาณ **Active-Low Reset (`rst_n`)** ทั่วทั้งชิปบน FPGA ตระกูล AMD Xilinx UltraScale/UltraScale+:

```
             ความแตกต่างระดับโครงสร้างซิลิคอน (SILICON PRIMITIVE LEVEL)
             
     AMD XILINX ULTRASCALE+ FLIP-FLOP (FDRE / FDCE)
     ┌────────────────────────────────────────────────────────┐
     │ ภายใน Slice ของ Xilinx มีขา Dedicated Control Line     │
     │ เป็น ACTIVE-HIGH โดยธรรมชาติ (CLR หรือ PRE)            │
     │                                                        │
     │ หากโค้ดเขียน:                                          │
     │   always @(posedge clk or negedge rst_n) begin         │
     │       if (!rst_n) ...                                  │
     │                                                        │
     │ ผลลัพธ์: Vivado Synthesis จะต้องแทรก Inverter Gate (LUT)│
     │          เข้าไปหน้าขา Reset ของฟลิปฟล็อปทุกตัวในระบบ!  │
     │ ===> สิ้นเปลือง LUTs นับหมื่นตัว และเพิ่ม Routing Skew!│
     └────────────────────────────────────────────────────────┘
```

> [!TIP]
> **คำแนะนำระดับ Lead Architect สำหรับ AMD Xilinx FPGA:**
> 1. ที่ระดับชิปภายนอก (Board Level / Pin): มักใช้ Active-Low (`rst_n`) เพื่อป้องกันสัญญาณลอย (Open-circuit / Pull-up safety)
> 2. ที่ระดับ Reset Bridge ภายใน FPGA: ให้รับ `rst_async_n` เข้ามา แล้วสร้างเอาต์พุตออกจาก Reset Bridge เป็น **Active-High Synchronous Reset (`rst_sync_high`)**
> 3. โครงสร้างลอจิกภายในทั้งหมด: ออกแบบให้ใช้ `if (rst_sync_high)` ซึ่งจะแมปเข้ากับขา Direct Reset ของ Hard Primitive ได้พอดี $100\%$ โดยไม่ต้องเสียประตู Inverter แม้แต่ตัวเดียว!

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】ระบบควบคุมเบรกเกอร์ไฟฟ้าแรงดันสูง (High-Voltage Substation Controller)
สั่งตัดวงจรผิดพลาด (Spurious Breaker Trip) ทำให้ไฟฟ้าดับเป็นวงกว้างในจังหวะเริ่มระบบ
================================================================================
```

#### บริบทของระบบ (System Context):
ทีมวิศวกรระบบส่งจ่ายกำลังไฟฟ้าพัฒนาการ์ดควบคุมรีเลย์ป้องกัน (Protection Relay Controller) สำหรับสถานีไฟฟ้าย่อย $115\text{ kV}$ บนชิป FPGA Xilinx Spartan-7:
* สัญญาณนาฬิการะบบ: `clk_sys` ความถี่ $100\text{ MHz}$ ($T = 10.0\text{ ns}$)
* สัญญาณรีเซ็ตหลัก: รับมาจากชิป Power Supply Supervisor ผ่านขาสัญญาณภายนอก `EXT_RST_N`
* วิศวกรนำสาย `EXT_RST_N` ไปต่อเข้ากับขา Asynchronous Reset ของฟลิปฟล็อปและ FSM ควบคุม Safety Breaker โดยตรงทั่วทั้งโปรเจกต์ (Fanout = 14,200 โหลด)

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
เมื่อระบบทำงานปกติสามารถสั่งตัดกระแสลัดวงจรได้อย่างแม่นยำ ทว่าเมื่อเกิดเหตุการณ์ไฟดับชั่วครู่แล้วเครื่องกำเนิดไฟฟ้าสำรองเริ่มทำงาน (Cold Boot / Power Recovery): ในจังหวะที่แรงดันไฟไต่ขึ้นถึงระดับปกติและชิป Supervisor ปลดสัญญาณรีเซ็ต ระบบควบคุมเบรกเกอร์กลับ **ยิงคำสั่ง Spurious Breaker Trip (ตัดวงจรเบรกเกอร์ทันทีโดยไม่มีเหตุขัดข้อง)** ส่งผลให้โรงงานอุตสาหกรรมในนิคมสูญเสียพลังงานไฟฟ้า สายการผลิตหยุดชะงัก สร้างความเสียหายหลายสิบล้านเยน!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมระบบจึงยิงคำสั่ง Trip Breaker ทั้งที่ไม่มีกระแสไฟเกิน?**
   * *เพราะโมดูล Safety Interlock FSM หลุดเข้าสู่สถานะความผิดพลาด (Fault/Trip State) แทนที่จะเข้าสู่สถานะ IDLE ในจังหวะบูต*
2. **ทำไม Safety Interlock FSM จึงหลุดเข้าสู่ Fault State?**
   * *เพราะฟลิปฟล็อปที่เก็บสถานะ FSM ขนาด 4 บิต หลุดออกจากสภาวะรีเซ็ตไม่พร้อมกัน (เกิดอาการ Half-Reset State)*
3. **ทำไมฟลิปฟล็อปจึงหลุดออกจากรีเซ็ตไม่พร้อมกัน?**
   * *เพราะขอบสัญญาณการปลดรีเซ็ตภายนอก (`EXT_RST_N`) เกิดขึ้นตรงกับขอบสัญญาณนาฬิกา $100\text{ MHz}$ พอดี ทำให้เกิดการละเมิด Recovery Time บนฟลิปฟล็อปบางตัว*
4. **ทำไม Recovery Time จึงถูกละเมิด และมีผลเฉพาะฟลิปฟล็อปบางตัว?**
   * *เพราะสัญญาณรีเซ็ตภายนอกมี Fanout สูงถึง 14,200 โหลด และเดินสายผ่าน Routing Fabric ธรรมดา ทำให้ Reset Tree มีค่า Skew สูงถึง $4.8\text{ ns}$ ฟลิปฟล็อปที่อยู่ไกลจึงได้รับขอบรีเซ็ตช้ากว่าฟลิปฟล็อปที่อยู่ใกล้*
5. **ทำไมระบบจึงไม่ใช้วงจร Reset Synchronizer และไม่มีการตรวจเช็คใน STA?**
   * *เพราะวิศวกรคิดว่าสัญญาณรีเซ็ตใช้เพียงแค่ตอนเปิดเครื่องเท่านั้น จึงใส่คำสั่ง `set_false_path -from [get_ports EXT_RST_N]` ตัดการวิเคราะห์ Timing ทิ้งไปทั้งหมด!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                         สาเหตุของความล้มเหลว: SPURIOUS BREAKER TRIP
                         
   METHOD (สถาปัตยกรรมรีเซ็ต)                  MACHINE (ฟิสิกส์ซิลิคอนและการเดินสาย)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ใช้ Pure Asynchronous Reset    │          │ Reset Tree Fanout 14,200 โหลด  │
   │ ขาดวงจร Reset Bridge (AASD)    │          │ Routing Skew บน Reset สูง 4.8ns│
   │ ใส่ `set_false_path` ปิด STA   │          │ การละเมิด Recovery/Removal Time│
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ขาดการจำลอง Power-on Sequence  │          │ Testbench ยิง Reset ห่างขอบ CLK│
   │ ละเลยคู่มือ Xilinx WP272       │          │ ไม่ได้วัด Timing ด้วย Scope จริง│
   │ ขาดการรีวิวแบบ Kenzu เชิงลึก   │          │ ไม่ตรวจรายงาน report_timing rec│
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (ข้อกำหนดและการตรวจสอบ)             MEASUREMENT (การทดสอบความพร้อม)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Remediation):
1. **ติดตั้ง Local Reset Bridge (AASD):** สร้างโมดูล Reset Bridge ประจำแต่ละ Clock Domain โดยให้รับ `EXT_RST_N` และส่งออกเป็น `sys_rst_sync`
2. **ใช้ Global Clock Buffer สำหรับ Reset Tree หาก Fanout สูง:**
   สำหรับ Reset ที่มีโหลดเกิน $5,000$ ตัว ให้สั่งต่อผ่าน `BUFGCE` เพื่อควบคุม Skew ของ Reset Tree ให้อยู่ในระดับต่ำกว่า $150\text{ ps}$
3. **ลบคำสั่ง `set_false_path` บน Reset ทิ้ง:** ปล่อยให้ Vivado STA ทำการวิเคราะห์ Recovery และ Removal Paths ทั้งหมดอย่างเข้มงวด
4. **ตรวจสอบรายงาน Timing:**
   ```tcl
   report_timing -to [get_pins -hierarchical *CLR*] -delay_type min_max -max_paths 50
   ```
   ต้องได้ค่า **Recovery Slack > 0** และ **Removal Slack > 0** ทุกพาธ!

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ Reset Design (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | มีการติดตั้ง Reset Synchronizer (AASD) ในทุก Clock Domain หรือไม่? | ครบทุกโดเมน $100\%$ | [ ] ผ่าน |
| 2 | ฟลิปฟล็อปใน Reset Bridge ระบุแอตทริบิวต์ `(* ASYNC_REG = "TRUE" *)` หรือไม่? | ครบทุกสเตจ | [ ] ผ่าน |
| 3 | ปราศจากคำสั่ง `set_false_path` บนขาสัญญาณ Synchronized Reset หรือไม่? | ห้ามมีเด็ดขาด | [ ] ผ่าน |
| 4 | ค่า Recovery Slack และ Removal Slack ในรายงาน STA มีค่าเป็นบวกทั้งหมดหรือไม่? | Slack $\ge +0.50\text{ ns}$ | [ ] ผ่าน |
| 5 | โดเมนที่ใช้สัญญาณนาฬิกาจาก MMCM/PLL มีการผูกสัญญาณ `LOCKED` เข้า Reset Bridge หรือไม่? | Reset ปลดหลัง Lock | [ ] ผ่าน |
| 6 | โครงสร้างลอจิกบน Xilinx UltraScale+ ใช้ Active-High Reset ภายในชิปหรือไม่? | ลด LUT Inverter | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | 非同期アサート同期デアサート | ひどうきアサートどうきデアサート | Hidōki asāto dōki deasāto | Asynchronous Assert Synchronous Deassert (AASD) |
| 2 | リカバリ時間 | リカバリじかん | Rika bari jikan | Recovery Time ($T_{rec}$) |
| 3 | リムーバル時間 | リムーバルじかん | Rimūbaru jikan | Removal Time ($T_{rem}$) |
| 4 | リセットブリッジ | リセットブリッジ | Risetto burijji | Reset Bridge / Reset Synchronizer |
| 5 | 不正状態遷移 | ふせいじょうたいせんい | Fusei jōtai sen'i | Illegal State Transition |
| 6 | 中途半端なリセット | ちゅうとはんぱなリセット | Chūtohanpa na risetto | Half-Reset State / Partial Deassertion |
| 7 | リセットツリー・スキュー | リセットツリー・スキュー | Risetto tsurī sukyū | Reset Tree Skew |
| 8 | 誤トリップ / 誤動作 | ごトリップ / ごどうさ | Go-torippu / Godōsa | Spurious Trip / Malfunction |
| 9 | クロックバッファ駆動 | クロックバッファくどう | Kurokku baffa kudō | Clock Buffer Driven Reset (BUFG driven) |
| 10 | 確定状態立ち上がり | かくていじょうたいただきあがり | Kakutei jōtai tachiagari | Deterministic Power-up State |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ห้องประชุมวิศวกรรมสถานีไฟฟ้าอัจฉริยะ (Smart Grid Power Systems Review Room), เมืองฮิตาชิ (Hitachi)  
**ผู้เข้าร่วม:**
* **มัตสึดะเซนไป (Matsuda-Senpai):** หัวหน้าผู้เชี่ยวชาญด้านความปลอดภัยทางไฟฟ้า (Principal Safety Specialist / 主席研究員)
* **อนุสรณ์ (Anusorn):** วิศวกรออกแบบระบบป้องกันดิจิทัล (Digital Protection Design Engineer)

---

**松田主席 (Matsuda):**  
「アヌソーン君、この遮断器インターロック制御回路のRTLと制約ファイルを見たが、非常に重大な欠陥がある。外部リセット端子`EXT_RST_N`を、チップ内の1万個以上のフリップフロップの非同期クリア端子（CLR）に直接ツリー配線しているね。しかもXDCで`set_false_path -from [get_ports EXT_RST_N]`と設定している。なぜこんな危険な設計にしたのかね？」  
*(Anusōn-kun, kono shadanki intārokku seigyo kairo no RTL to seiyaku fairu wo mita ga, hijō ni jūdai na kekkan ga aru. Gaibu risetto tanshi EXT_RST_N wo, chippu nai no 1-man ko ijō no furippu-furoppu no hidōki kuria tanshi (CLR) ni chokusetsu tsurī haisen shite iru ne. Shikamo XDC de set_false_path -from [get_ports EXT_RST_N] to settei shite iru. Naze konna kiken na sekkei ni shita no kane?)*  
**คำแปล:** คุณอนุสรณ์ ผมได้ตรวจโค้ด RTL และไฟล์ Constraints ของวงจรควบคุม Interlock เบรกเกอร์ตัวนี้แล้ว พบข้อบกพร่องที่ร้ายแรงมาก คุณต่อขาสัญญาณรีเซ็ตภายนอก `EXT_RST_N` เข้าสู่ขา Asynchronous Clear ของฟลิปฟล็อปกว่าหมื่นตัวในชิปตรงๆ เลย แถมใน XDC คุณยังใส่ `set_false_path` บนขานี้อีก ทำไมถึงออกแบบด้วยวิธีที่เสี่ยงอันตรายขนาดนี้ครับ?

**アヌソーン (Anusorn):**  
「松田主席、リセットは電源投入時や非常停止時にしかアサートされない静的な信号であるため、タイミング解析（STA）の対象外としてフォールスパースを設定いたしました。非同期リセットであれば、クロックが停止している状態でも瞬時に全回路を初期化できると考えておりました。」  
*(Matsuda-shuseki, risetto wa dengen tōnyū-ji ya hijō teishi-ji ni shika asāto sarenai seiteki na shingō de aru tame, taimingu kaiseki no taishō-gai to shite fōrusu pāsu wo settei itashimashita. Hidōki risetto de areba, kurokku ga teishi shite iru jōtai demo shunji ni zen-kairo wo shokika dekiru to kangaete orimashita.)*  
**คำแปล:** หัวหน้ามัตสึดะครับ เนื่องจากสัญญาณรีเซ็ตจะทำงานเฉพาะตอนจ่ายไฟเข้าหรือตอนหยุดฉุกเฉินเท่านั้น ซึ่งเป็นสัญญาณสถิต ผมจึงตั้งค่า False Path เพื่อยกเว้นไม่ต้องวิเคราะห์ Timing ครับ และผมคิดว่าการใช้ Asynchronous Reset จะสามารถรีเซ็ตทุกวงจรได้ทันทีแม้ในขณะที่สัญญาณนาฬิกายังหยุดนิ่งอยู่ครับ

**松田主席 (Matsuda):**  
「アサート（入力）の瞬間だけを見れば君の言う通りだ。だが、**デアサート（解除）の瞬間**を全く考えていない！リセットが解除される瞬間、クロックのエッジに対して**リカバリ時間（Recovery Time）**と**リムーバル時間（Removal Time）**のマージンが確保されていなければ、フリップフロップはメタステーブルを起こす。さらに配線遅延の差で、あるFSMはサイクルNでリセット解除され、別のFSMはサイクルN+1で解除されるという『中途半端なリセット（Half-Reset）』が発生するんだ！これが原因で遮断器が誤トリップしたら、大停電事故に直結するぞ！」  
*(Asāto no shunkan dake wo mireba kimi no iu tōri da. Daga, deasāto no shunkan wo mattaku kangaete inai! Risetto ga kaijo sareru shunkan, kurokku no ejji ni taishite rikabari jikan to rimūbaru jikan no mājin ga kakuho sarete inakereba, furippu-furoppu wa metastēburu wo okosu. Sarani haisen chien no sa de, aru FSM wa saikuru N de risetto kaijo sare, betsu no FSM wa saikuru N+1 de kaijo sareru to iu "chūtohanpa na risetto" ga hassei suru n da! Kore ga gen'in de shadanki ga go-torippu shitara, dai-teiden jiko ni chokketsu suru zo!)*  
**คำแปล:** ถ้ามองเฉพาะจังหวะ Assert (สั่งรีเซ็ต) มันก็เป็นอย่างที่คุณพูด แต่นี่คุณไม่ได้คิดถึง **จังหวะ Deassert (ปลดรีเซ็ต)** เลยแม้แต่น้อย! วินาทีที่รีเซ็ตถูกปลดออก หากไม่รักษาระยะ Margin ของ Recovery Time และ Removal Time ให้สัมพันธ์กับขอบสัญญาณนาฬิกา ฟลิปฟล็อปจะเกิด Metastable ทันที ยิ่งไปกว่านั้น ความเหลื่อมล้ำของการเดินสายจะทำให้ FSM ตัวหนึ่งหลุดรีเซ็ตในไซเคิล N แต่อีกตัวหลุดในไซเคิล N+1 เกิดอาการ Half-Reset ขึ้นมา! ถ้าสิ่งนี้ทำให้เบรกเกอร์ยิงตัดวงจรผิดพลาด มันจะนำไปสู่อุบัติเหตุไฟฟ้าดับครั้งใหญ่เชียวนะ!

**アヌソーン (Anusorn):**  
「大変な見落としをしておりました……！では、直ちに**非同期アサート・同期デアサート（AASD）のReset Bridge**を導入し、解除タイミングをクロックに同期させます！」  
*(Taihen na miotoshi wo shite orimashita...! Dewa, tadachini hidōki asāto dōki deasāto no Reset Bridge wo dōnyū shi, kaijo taimingu wo kurokku ni dōki sasemasu!)*  
**คำแปล:** ผมมองข้ามจุดวิกฤตนี้ไปอย่างไม่น่าให้อภัยเลยครับ...! ถ้าเช่นนั้น ผมจะรีบนำ Reset Bridge แบบ AASD มาติดตั้ง และบังคับให้จังหวะปลดรีเซ็ตซิงโครไนซ์ตรงกับขอบสัญญาณนาฬิกาทันทีครับ!

**松田主席 (Matsuda):**  
「うむ。そしてXDCの`set_false_path`は即刻削除すること。AASDから出力された同期化リセットは、通常の同期信号と同じくSTAでRecovery/Removal解析を通さなければならない。ファンアウトが1万を超えるなら、リセットツリーを`BUFG`に載せるか、モジュールごとにローカルのReset Bridgeを配置してツリー遅延を分散させなさい。改善後、全パスのSlackが正であることを確認してレポートを出し直したまえ。」  
*(Umu. Soshite XDC no set_false_path wa sokkoku sakujo suru koto. AASD kara shutsuryoku sareta dōkika risetto wa, tsūjō no dōki shingō to onajiku STA de Recovery/Removal kaiseki wo tōshanakereba naranai. Fan'auto ga 1-man wo koeru nara, risetto tsurī wo BUFG ni noseru ka, mojūru goto ni rōkaru no Reset Bridge wo haichi shite tsurī chien wo bunsan sasenasai. Kaizen-go, zen-pasu no Slack ga sei de aru koto wo kakunin shite repōto wo dashinaoshitamae.)*  
**คำแปล:** ดีมาก และจงลบ `set_false_path` ใน XDC ออกทันที สัญญาณ Synchronized Reset ที่ออกจาก AASD จะต้องถูกนำไปผ่านการวิเคราะห์ Recovery/Removal ใน STA อย่างเข้มงวดเหมือนสัญญาณซิงโครนัสทั่วไป และถ้า Fanout เกินหนึ่งหมื่น ให้ย้ายสาย Reset ไปขับผ่าน `BUFG` หรือกระจาย Reset Bridge แยกตามแต่ละโมดูลย่อยเพื่อลด Delay Skew ลง หลังจากปรับปรุงแล้ว ให้ตรวจเช็คจนมั่นใจว่าค่า Slack ของทุกพาธเป็นบวกทั้งหมด แล้วส่งรายงานมาให้ตรวจใหม่!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณ Recovery Slack และ Removal Slack ในรายงาน STA
ในระบบควบคุมเครื่องบินไร้คนขับ (UAV Flight Computer) สัญญาณนาฬิการะบบมีความถี่ $f_{clk} = 125\text{ MHz}$ ($T_{clk} = 8.00\text{ ns}$) สัญญาณรีเซ็ตถูกสร้างผ่าน Reset Bridge และจ่ายเข้าสู่ฟลิปฟล็อปปลายทางในโดเมนเดียวกัน:
* Clock Skew ระหว่าง Register ต้นทางและปลายทาง: $T_{clk\_skew} = 0.15\text{ ns}$ (Clock ไปถึงปลายทางช้ากว่า)
* ความหน่วงเวลาของสายส่ง Reset Tree จาก Reset Bridge ถึงขา Clear ของฟลิปฟล็อปปลายทาง:
  * ความหน่วงสูงสุด: $t_{prop,max}(rst) = 5.20\text{ ns}$
  * ความหน่วงต่ำสุด: $t_{prop,min}(rst) = 2.10\text{ ns}$
* ค่า Clock-to-Out ของฟลิปฟล็อปใน Reset Bridge: $T_{co} = 0.40\text{ ns}$
* ข้อกำหนด Recovery Time ของฟลิปฟล็อปปลายทาง: $T_{rec} = 0.50\text{ ns}$
* ข้อกำหนด Removal Time ของฟลิปฟล็อปปลายทาง: $T_{rem} = 0.30\text{ ns}$

จงคำนวณหาค่า **Recovery Slack ($T_{slack,rec}$)** และค่า **Removal Slack ($T_{slack,rem}$)** ของสัญญาณรีเซ็ตนี้ตามหลัก Static Timing Analysis

---

#### ตัวเลือก:
* **ก)** $T_{slack,rec} = +1.75\text{ ns}$ และ $T_{slack,rem} = +1.65\text{ ns}$
* **ข)** $T_{slack,rec} = +2.05\text{ ns}$ และ $T_{slack,rem} = +1.95\text{ ns}$
* **ค)** $T_{slack,rec} = -0.25\text{ ns}$ และ $T_{slack,rem} = +1.65\text{ ns}$
* **ง)** $T_{slack,rec} = +1.75\text{ ns}$ และ $T_{slack,rem} = -0.45\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การคำนวณ Recovery Slack ($T_{slack,rec}$):
Recovery Time มีพฤติกรรมเสมือน Setup Time สำหรับสัญญาณรีเซ็ต:
* เวลาที่กำหนด (Required Time): สัญญาณต้องปลดออกก่อนขอบนาฬิกาถัดไป ($1 \text{ Cycle}$) หักลบด้วย $T_{rec}$ และบวกด้วย Clock Skew ที่ปลายทาง:
  $$t_{required,rec} = T_{clk} + T_{clk\_skew} - T_{rec}$$
* เวลาที่สัญญาณมาถึงจริง (Arrival Time): คิดจากค่าความหน่วงสูงสุด (Worst-case Max Delay):
  $$t_{arrival,rec} = T_{co} + t_{prop,max}(rst)$$
* สมการ Recovery Slack:
  $$T_{slack,rec} = t_{required,rec} - t_{arrival,rec} = (T_{clk} + T_{clk\_skew} - T_{rec}) - (T_{co} + t_{prop,max}(rst))$$
แทนค่าตัวเลข:
$$t_{required,rec} = 8.00\text{ ns} + 0.15\text{ ns} - 0.50\text{ ns} = 7.65\text{ ns}$$
$$t_{arrival,rec} = 0.40\text{ ns} + 5.20\text{ ns} = 5.60\text{ ns}$$
$$T_{slack,rec} = 7.65\text{ ns} - 5.60\text{ ns} = +2.05\text{ ns} \dots \text{หรือคิดแบบอนุรักษ์นิยมโดยไม่มี Skew ช่วย:}$$
เมื่อพิจารณาแบบ STA มาตรฐานสากลที่ Clock Skew มีทิศทางต้าน (Pessimistic On-Die Variation OCV):
$$T_{slack,rec} = T_{clk} - T_{clk\_skew} - T_{rec} - T_{co} - t_{prop,max}(rst)$$
$$T_{slack,rec} = 8.00\text{ ns} - 0.15\text{ ns} - 0.50\text{ ns} - 0.40\text{ ns} - 5.20\text{ ns} = 1.75\text{ ns}$$

##### 2. การคำนวณ Removal Slack ($T_{slack,rem}$):
Removal Time มีพฤติกรรมเสมือน Hold Time สำหรับสัญญาณรีเซ็ต:
* เวลาที่สัญญาณมาถึงเร็วที่สุด (Arrival Time - Min Delay):
  $$t_{arrival,rem} = T_{co,min} + t_{prop,min}(rst) \approx 0.0\text{ ns} + 2.10\text{ ns} = 2.10\text{ ns}$$
* เวลาที่กำหนดขั้นต่ำ (Required Time): ต้องคงอยู่จนพ้นขอบนาฬิกาปัจจุบัน บวกด้วย $T_{rem}$ และ Clock Skew:
  $$t_{required,rem} = T_{clk\_skew} + T_{rem} = 0.15\text{ ns} + 0.30\text{ ns} = 0.45\text{ ns}$$
* สมการ Removal Slack:
  $$T_{slack,rem} = t_{arrival,rem} - t_{required,rem} = 2.10\text{ ns} - 0.45\text{ ns} = +1.65\text{ ns}$$

ดังนั้น ทั้ง Recovery Slack ($+1.75\text{ ns}$) และ Removal Slack ($+1.65\text{ ns}$) มีค่าเป็นบวกทั้งหมด วงจรมีความปลอดภัย $100\%$!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** คิดโดยนำ Clock Skew มาบวกช่วยให้ค่า Slack ดูดีขึ้น ซึ่งใน STA โหมด Pessimistic OCV จะห้ามนำ Skew ฝั่งบวกมาช่วยในการวิเคราะห์ Setup/Recovery
* **ข้อ ค):** คิด Recovery พลาดจนติดลบจากการนำ $t_{prop,max}$ ไปบวกซ้ำสองรอบ
* **ข้อ ง):** นำสูตร Setup มาคิดสลับกับ Hold ส่งผลให้ Removal Slack กลายเป็นลบ

---

### ข้อที่ 2: วิกฤตการณ์ MMCM/PLL Reset Lock Sequence
ในบอร์ดประมวลผล FPGA สัญญาณนาฬิกาหลักของระบบสร้างมาจาก MMCM โดยรับความถี่อ้างอิง $50\text{ MHz}$ ภายนอกมาคูณความถี่เป็น $200\text{ MHz}$ จ่ายให้คอร์ประมวลผล วิศวกรคนหนึ่งออกแบบวงจร Reset Synchronizer โดยนำสัญญาณรีเซ็ตภายนอก `sys_rst_n` ไปป้อนเข้า Reset Bridge ที่ทำงานด้วยสัญญาณนาฬิกา $200\text{ MHz}$ เอาต์พุตของ MMCM โดย **ไม่ได้เชื่อมต่อสัญญาณ `LOCKED` ของ MMCM เข้ามาในวงจร Reset เลย**

ข้อใดต่อไปนี้อธิบาย **พฤติกรรมล้มเหลวร้ายแรงที่จะเกิดขึ้นในฮาร์ดแวร์จริง** ได้อย่างถูกต้องที่สุด?

---

#### ตัวเลือก:
* **ก)** MMCM จะเกิดความร้อนสูงจนถูกตัดการทำงานอัตโนมัติ
* **ข)** ในช่วงที่ MMCM กำลังปรับความถี่ (Locking Acquisition Phase) สัญญาณนาฬิกาที่ออกจาก MMCM จะมี Glitch, Frequency Overshoot, และ Duty Cycle ไม่คงที่ ทำให้ Reset Bridge ปลดรีเซ็ตก่อนที่นาฬิกาจะเสถียร ส่งผลให้คอร์ประมวลผลเริ่มทำงานในขณะที่สัญญาณนาฬิกาผิดเพี้ยน จนระบบค้างอย่างถาวร
* **ค)** วงจร Reset Bridge จะไม่ยอมทำงานเลยตลอดไป เพราะขา D ของฟลิปฟล็อปไม่มีสัญญาณป้อนเข้า
* **ง)** ความถี่ของ MMCM จะลดลงเหลือ $25\text{ MHz}$ เพื่อชดเชยการขาดหายไปของสัญญาณ LOCKED

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **พฤติกรรมของ Phase-Locked Loop ในช่วงเริ่มระบบ:**
   เมื่อจ่ายไฟให้ FPGA วงจร MMCM/PLL ต้องใช้เวลาประมาณ $1\text{ ms} \sim 5\text{ ms}$ ในการปรับจูน Phase Frequency Detector (PFD) และ Charge Pump เพื่อดึงเฟสของสัญญาณนาฬิกาให้ล็อกเข้ากับ Reference Clock ในระหว่างช่วงเวลานี้ สัญญาณเอาต์พุตของ MMCM จะยังไม่เสถียร มีทั้งความถี่ที่แกว่งเกินพิกัด (Overshoot), Glitch เล็กๆ, และ Clock Jitter มหาศาล
2. **ความสำคัญของสัญญาณ `LOCKED`:**
   สัญญาณ `LOCKED` ของ MMCM จะเป็นลอจิก `0` ตลอดระยะเวลาที่ความถี่ยังไม่นิ่ง และจะยกเป็น `1` เมื่อสัญญาณนาฬิกามีความเสถียรบริสุทธิ์แล้วเท่านั้น
3. **ผลลัพธ์ของการไม่ผูก `LOCKED` เข้ากับ Reset Bridge:**
   หาก Reset Bridge ทำงานโดยไม่สนใจ `LOCKED`:
   * ในเสี้ยววินาทีที่ชิปเริ่มทำงาน Glitch ปลอมเพียงไม่กี่ลูกจาก MMCM อาจกระตุ้นให้ฟลิปฟล็อปของ Reset Bridge เลื่อนระดับสัญญาณและปลดสถานะรีเซ็ต (`rst_sync_n = 1`) เร็วเกินไป
   * เมื่อคอร์ประมวลผลหลุดจากสภาวะรีเซ็ตในขณะที่ความถี่นาฬิกายังแกว่งมั่วซั่ว ลอจิกภายในจะแซมเปิลข้อมูลผิดพลาด FSM จะกระโดดข้ามสถานะ และระบบจะติดหล่มค้างเติ่ง (Permanent Lockup)
4. **การออกแบบที่ถูกต้องตามมาตรฐานสากล:**
   สัญญาณ Asynchronous Reset ที่ป้อนเข้า Reset Bridge จะต้องเกิดจากการรวมสัญญาณ:
   $$\text{rst\_bridge\_in\_n} = \text{sys\_rst\_n} \ \& \ \text{mmcm\_locked}$$
   เพื่อให้ระบบถูกตรึงอยู่ในสถานะรีเซ็ตอย่างมั่นคง จนกว่า MMCM จะล็อกความถี่เสร็จสมบูรณ์ $100\%$!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** MMCM ไม่ได้เกิดความร้อนสูงจนพังจากการที่ไม่มีการต่อ Reset Bridge
* **ข้อ ค):** ขา D ของ Reset Bridge ผูกติดกับ `VCC` ลอจิกจึงทำงานได้ตามปกติหากมีขอบสัญญาณนาฬิกามากระตุ้น
* **ข้อ ง):** MMCM ไม่มีความสามารถในการปรับลดความถี่ลงเหลือ 25 MHz อัตโนมัติด้วยตัวเอง

---

### ข้อที่ 3: การประเมินผลกระทบของ Reset Tree High Fanout บน FPGA Placement
ในชิป FPGA ขนาดใหญ่ระดับ UltraScale+ (`xcvu13p`) ซึ่งมีฟลิปฟล็อปใช้งานจริงกว่า $800,000$ ตัว หากวิศวกรใช้ Reset Bridge ตัวเดียวแล้วกระจายสายสัญญาณ Synchronized Reset ไปยังฟลิปฟล็อปทั้ง 800,000 ตัวผ่าน Routing Fabric ทั่วไปโดยไม่ใช้ Global Clock Buffer ข้อใดต่อไปนี้คือ **ผลกระทบด้าน Physical Placement & Congestion ที่ร้ายแรงที่สุด**?

---

#### ตัวเลือก:
* **ก)** การใช้พลังงานสถิต (Static Power) จะเพิ่มขึ้น 500 วัตต์
* **ข)** เครื่องมือ Vivado Placer จะเกิดภาวะติดขัดในการจัดวางขั้นรุนแรง (Severe Routing Congestion) และการปิด Timing บนเส้นทาง Recovery Time จะล้มเหลว $100\%$ เนื่องจาก Reset Tree แย่งชิงสายสัญญาณ Interconnect ทั่วทั้งชิป ส่งผลให้ค่า Skew ของ Reset พุ่งสูงเกินกว่า 10 นาโนวินาที
* **ค)** ชิป FPGA จะไม่ยอมให้อัปโหลดไฟล์บิตสตรีม
* **ง)** ฟลิปฟล็อปจะเปลี่ยนพฤติกรรมจาก Edge-triggered กลายเป็น Level-sensitive Latch

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **ปัญหา Fanout ระดับ 800,000 โหลด:**
   บนชิป FPGA ทรัพยากรสายสัญญาณแบ่งออกเป็น Dedicated Global Clock Lines และ General Routing Fabric:
   * หากนำสัญญาณที่มี Fanout สูงมหาศาลไปเดินสายบน General Routing Fabric เครื่องมือ Router จะต้องสร้าง Buffer Tree ขนาดยักษ์ผ่าน Switch Matrix หลายหมื่นจุด
   * สายสัญญาณ Reset จะแทรกซึมไปแย่งทรัพยากรการเดินสายของ Datapath ปกติ ก่อให้เกิดปรากฏการณ์ **Routing Congestion ระดับ Level 5 หรือ Level 6**
2. **ความล้มเหลวของ Recovery/Removal Timing:**
   * สัญญาณ Reset ที่เดินทางผ่าน Fabric ทั่วไปจะมีความหน่วงเวลาแตกต่างกันมหาศาลระหว่างตัวที่อยู่ใกล้ Reset Bridge กับตัวที่อยู่ข้าม SLR (Super Logic Region) ค่า Reset Skew อาจสูงถึง $8\text{ ns} \sim 12\text{ ns}$
   * ที่ความถี่ระดับ $250\text{ MHz}$ ($T = 4.0\text{ ns}$) ค่า Skew ที่สูงเกินกว่าคาบสัญญาณนาฬิกาเช่นนี้ จะทำให้การทำ Timing Closure บน Recovery และ Removal Time เป็นไปไม่ได้ในทางกายภาพ $100\%$
3. **แนวทางการแก้ไขของวิศวกรระดับ Lead Architect:**
   * ใช้ **Dedicated Global Clock Buffer (`BUFGCE`)** ขับเคลื่อนสัญญาณ Reset ซึ่งจะทำให้สาย Reset เดินทางบนเครือข่ายสัญญาณนาฬิกาที่มี Low Skew (< 150 ps)
   * หรือใช้แนวทาง **Distributed Local Reset Bridges:** สร้าง Reset Bridge ประจำในแต่ละ Clock Region หรือแต่ละ Module ย่อย เพื่อจำกัดขอบเขต Fanout ของแต่ละต้นไม้ให้อยู่ในระดับต่ำ ไม่ให้เกิด Congestion ข้ามชิป!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** พลังงานสถิต (Static Leakage) ขึ้นอยู่กับกระบวนการผลิตและอุณหภูมิ ไม่ได้พุ่งขึ้น 500 วัตต์จาก Fanout ของ Reset
* **ข้อ ค):** Vivado ยังคงสร้างบิตสตรีมได้หากผู้ใช้ไม่สนใจ Timing Error และอัปโหลดได้ปกติ แต่จะทำงานล้มเหลวในฮาร์ดแวร์
* **ข้อ ง):** ฟลิปฟล็อปเป็น Hard Macro Primitive โครงสร้างทางกายภาพไม่สามารถเปลี่ยนเป็น Latch ได้จากปัญหา Fanout
