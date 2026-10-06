# Lesson 196: FPGA Testbench Part 6 — Gate-Level Simulation (GLS) with SDF Back-Annotation (การจำลองระดับเกตและการคำนวณดีเลย์จริงด้วยไฟล์ SDF)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในการพัฒนา FPGA และ ASIC ระดับสูง การจำลองการทำงานด้วย RTL Simulation (RTL ซอร์สโค้ดเดิม) จะตั้งอยู่บนสมมุติฐาน **Zero-Delay Model (สายไฟและเกตไม่มีเวลาหน่วงในตัว)** ข้อมูลจะเคลื่อนที่เสร็จสิ้นทันทีในรอบคล็อกเดียวกัน ซึ่งไม่สอดคล้องกับฟิสิกส์ของเซมิคอนดักเตอร์จริง

เมื่อวงจรผ่านขั้นตอน Synthesis และ Place & Route (P&R) แล้ว จะได้ไฟล์โครงข่ายเกตจริงที่เรียกว่า **Gate-Level Netlist** และไฟล์ข้อมูลความล่าช้าของเกตและสายสัญญาณทองแดง เรียกว่า **Standard Delay Format (SDF - IEEE 1497)** การนำไฟล์ SDF กลับมาป้อนเข้าสู่การจำลองเรียกว่า **SDF Back-Annotation** และการรันจำลองนี้เรียกว่า **Gate-Level Simulation (GLS)** ซึ่งเป็นด่านสุดท้ายในการพิสูจน์ว่าวงจรจะทำงานได้จริงโดยไม่เกิด Race Condition หรือข้อผิดพลาดทางฟิสิกส์

```
+--------------------------------------------------------------------------------------------------+
|                    GATE-LEVEL SIMULATION (GLS) & SDF BACK-ANNOTATION FLOW                        |
+--------------------------------------------------------------------------------------------------+
                                                                                                    
                  +--------------------------+          +-------------------------+                 
                  |   Synthesis & P&R Engine |          | Static Timing Analysis  |                 
                  | (Vivado / Synopsys ICC2) | -------> |   (STA Engine: PrimeTime|                 
                  +--------------------------+          +-------------------------+                 
                                |                                    |                              
            Gate Netlist (*.v)  |                                    | Generates *.sdf              
                                v                                    v                              
                  +---------------------------------------------------------------+                 
                  |                  IEEE 1497 SDF DELAY FILE                     |                 
                  |   - Interconnect Wire Delays (IOPATH, PORT)                   |                 
                  |   - Cell Propagation Delays (MIN : TYP : MAX)                 |                 
                  |   - Timing Checks ($setup, $hold, $recovery, $removal)        |                 
                  +---------------------------------------------------------------+                 
                                                  |                                                 
                                                  | $sdf_annotate() Task                            
                                                  v                                                 
                  +---------------------------------------------------------------+                 
                  |                  GATE-LEVEL SIMULATOR (GLS)                   |                 
                  |  - True Propagation Delays on Logic Gates                     |                 
                  |  - Real Setup / Hold Window Violation Checking                |                 
                  |  - X-Propagation & Glitch Hazard Verification                 |                 
                  +---------------------------------------------------------------+                 
```

---

### 1.1 คณิตศาสตร์ของ PVT Timing Corners และโครงสร้างไฟล์ SDF (IEEE 1497)

เวลาหน่วงของสัญญาณไฟฟ้าในซิลิคอนขึ้นอยู่กับตัวแปรทางฟิสิกส์ 3 ประการ หรือ **PVT Corners**:
1. **Process (P):** ความผันผวนของความกว้างแชนเนลและความหนาออกไซด์ในการผลิต (Fast, Typical, Slow)
2. **Voltage (V):** ความต่างศักย์ของแหล่งจ่ายไฟ (แรงดันต่ำทำให้เกตเปิดช้าลง แรงดันสูงทำให้เกตเปิดเร็วขึ้น)
3. **Temperature (T):** อุณหภูมิการทำงาน (สำหรับเทคโนโลยี Deep Sub-micron อุณหภูมิต่ำอาจทำให้ทรานซิสเตอร์นำไฟฟ้าได้เร็วขึ้นจนเสี่ยงต่อ Hold Violation เรียกว่า *Temperature Inversion Effect*)

ในไฟล์ SDF ค่าความล่าช้าจะถูกระบุในรูปแบบ 3 ค่าทางคณิตศาสตร์คือ `(MIN : TYP : MAX)`:
- **Max Timing Corner (Worst-Case Corner: Slow Silicon, Low Voltage, High Temp):**
  เวลาหน่วงของ Logic มีค่าสูงสุด เสี่ยงต่อการเกิด **Setup Time Violation ($t_{setup}$)**
- **Min Timing Corner (Best-Case Corner: Fast Silicon, High Voltage, Low Temp):**
  เวลาหน่วงของ Logic และสายไฟสั้นที่สุด สัญญาณวิ่งเร็วเกินไป เสี่ยงต่อการเกิด **Hold Time Violation ($t_{hold}$)**

```sdf
(DELAYFILE
  (SDFVERSION "3.0")
  (DESIGN "motor_pwm_core")
  (DATE "OCT 2026")
  (VENDOR "Foundry_7nm")
  (PROGRAM "TimingSignoff_v2")
  (VERSION "2.1")
  (DIVIDER /)
  (TIMESCALE 1ps)
  (CELL
    (CELLTYPE "DFF_X1")
    (INSTANCE u_pwm_reg)
    (DELAY
      (ABSOLUTE
        (IOPATH CK Q (120:180:250) (110:165:230))
      )
    )
    (TIMINGCHECK
      (SETUP D (posedge CK) (45:65:90))
      (HOLD  D (posedge CK) (15:25:35))
    )
  )
)
```

---

### 1.2 ทฤษฎีเวลาหน่วงเชิงลบและกลไก Internal Delay Shifting (Negative Setup & Hold Math)

ในกระบวนการผลิตเกตขนาดเล็กมาก เซลล์ Flip-Flop มาตรฐาน (Standard Cell DFF) มักมีวงจรบัฟเฟอร์ภายใน (Internal Inverters) แทรกอยู่ที่ขาสัญญาณ Data ($D$) หรือ Clock ($CK$) ก่อนจะเข้าถึงแกนสลักข้อมูลจริง

พิจารณา Flip-Flop ที่มี Internal Delay ดังรูป:
- ความล่าช้าภายในของขา Data: $\tau_{d}$
- ความล่าช้าภายในของขา Clock: $\tau_{clk}$
- เวลา Setup และ Hold แท้จริงที่แกนสลัก (Internal Latch Core): $t_{su\_core}, \ t_{h\_core}$

```
Data In (D) ------[ Delay tau_d ]------> D_internal ----+
                                                        |--> [ Core Latch ]
Clock In (CK) ----[ Delay tau_clk ]----> CK_internal ---+
```

เวลา Setup และ Hold ที่สังเกตเห็นจากขาพินภายนอก ($t_{su\_pin}, \ t_{h\_pin}$) คำนวณได้จาก:
$$t_{su\_pin} = t_{su\_core} + \tau_{d} - \tau_{clk}$$
$$t_{h\_pin} = t_{h\_core} + \tau_{clk} - \tau_{d}$$

#### ผลลัพธ์ทางคณิตศาสตร์:
1. หากผู้ออกแบบใส่บัฟเฟอร์บนเส้นทาง Clock ยาวกว่า Data ($\tau_{clk} > t_{su\_core} + \tau_{d}$):
   ค่า $t_{su\_pin}$ จะกลายเป็น **ค่าติดลบ (Negative Setup Time)** ซึ่งหมายความว่าข้อมูลสามารถมาถึง *หลัง* ขอบสัญญาณนาฬิกาได้เล็กน้อยโดยที่ Flop ยังคงจับข้อมูลได้ถูกต้อง!
2. แต่การติดลบของ Setup Time จะต้องถูกชดเชยด้วยการเพิ่มขึ้นของ Hold Time เสมอตามสมการอนุรักษ์ความกว้างของหน้าต่างเวลา (Sampling Window Invariance):
   $$W_{window} = t_{su\_pin} + t_{h\_pin} = t_{su\_core} + t_{h\_core}$$
   ผลรวมของหน้าต่างเวลานี้จะต้องเป็นบวกเสมอ ($W_{window} > 0$)

ในการจำลอง GLS ตัว Simulator จะต้องเปิดใช้งานออปชันรองรับ Negative Timing Checks (เช่น `+neg_tchk` ใน VCS หรือ `-negdelay` ใน Xcelium) เพื่อทำการหน่วงสัญญาณจำลองภายในอย่างถูกต้อง มิฉะนั้นจะเกิดข้อผิดพลาดในการคำนวณ

---

### 1.3 ปัญหา X-Pessimism ในระดับเกต และการกรอง Glitch (Glitch Filtering & Pulse Rejection)

ในวงจร Netlist ลอจิกเกตจริงจะมีสภาวะการกระจายตัวของค่าที่ไม่ทราบแน่ชัด (Unknown State หรือ `X`):
1. **X-Pessimism:**
   พิจารณา MUX 2:1 ที่มีอินพุต $A=1, B=1$ หากขาเลือก $Sel$ กำลังเปลี่ยนสถานะและมีสภาวะก้ำกึ่งกลายเป็น `X` ชั่วขณะ ในฮาร์ดแวร์จริงเอาต์พุตจะต้องคงที่อยู่ที่ $1$ เสมอ แต่ในสมการบูลีนของ Simulator:
   $$Out = (Sel \wedge A) \vee (\neg Sel \wedge B) = (X \wedge 1) \vee (X \wedge 1) = X \vee X = \mathbf{X}$$
   Simulator จะพ่นค่า `X` ออกมา ซึ่งค่า `X` นี้จะแพร่กระจายไปตาม Pipeline ทำให้ทั้งระบบติด `X` และพังทลายหลอกตา (False Failure)
2. **Pulse Rejection Limits:**
   สัญญาณ Glitch สั้นๆ ที่มีความกว้างของพัลส์แคบกว่าเวลาหน่วงของเกต อาจไม่สามารถเปลี่ยนสถานะของทรานซิสเตอร์ได้ ใน Simulator จึงต้องควบคุมด้วยค่า **e-limit (Error Limit)** และ **r-limit (Reject Limit)** ผ่านสวิตช์:
   `+pulse_r/0 +pulse_e/0` หรือกำหนดเปอร์เซ็นต์การกลืนพัลส์ เพื่อสะท้อนฟิสิกส์ของ Inertial Delay

---

### 1.4 RTL / Verilog Testbench Harness: Master Gate-Level Simulation (`tb_gls_top.sv`)

```verilog
//=============================================================================
// Module: tb_gls_top
// Description: Master Gate-Level Simulation Harness with SDF Back-Annotation
// Standards: IEEE 1497 SDF / IEEE 1364 Verilog Timing Check Standards
//=============================================================================

`timescale 1ns / 1ps

module tb_gls_top;

    logic clk;
    logic rst_n;
    logic enable;
    logic [7:0] data_in;
    logic [7:0] pwm_out;
    logic fault_flag;

    // Clock Generation (200 MHz, Period = 5.0 ns)
    initial clk = 0;
    always #2.5 clk = ~clk;

    // Instantiation of Synthesized Gate-Level Netlist (DUT)
    // สังเกต: พอร์ตจะตรงกับระดับเกตจริงที่สังเคราะห์แล้ว
    motor_pwm_gate_netlist dut (
        .clk_in   (clk),
        .rst_n_in (rst_n),
        .en_in    (enable),
        .d_in     (data_in),
        .pwm_o    (pwm_out),
        .fault_o  (fault_flag)
    );

    //=========================================================================
    // SDF BACK-ANNOTATION TASK
    //=========================================================================
    initial begin
        $display("===============================================================");
        $display("   INITIALIZING SDF BACK-ANNOTATION FOR GATE-LEVEL SIMULATION  ");
        $display("===============================================================");

        // ตรวจสอบและโหลดไฟล์ SDF ตาม Timing Corner ที่กำหนดใน Makefile
`ifdef CORNER_MIN
        $display("[SDF-INFO] Annotating BEST-CASE (MIN) Timing Corner for HOLD check...");
        $sdf_annotate("netlist/motor_pwm_min.sdf", dut, "sdf_min.log", "MINIMUM");
`elsif CORNER_MAX
        $display("[SDF-INFO] Annotating WORST-CASE (MAX) Timing Corner for SETUP check...");
        $sdf_annotate("netlist/motor_pwm_max.sdf", dut, "sdf_max.log", "MAXIMUM");
`else
        $display("[SDF-INFO] Annotating TYPICAL Timing Corner...");
        $sdf_annotate("netlist/motor_pwm_typ.sdf", dut, "sdf_typ.log", "TYPICAL");
`endif

        $display("[SDF-INFO] Back-annotation completed successfully.\n");
    end

    //=========================================================================
    // TIMING VIOLATION NOTIFIER MONITOR
    //=========================================================================
    // ตรวจจับหาก Simulator แจ้งเตือน Timing Check Violation ในระดับเกต
    always @(dut.timing_violation_notifier) begin
        $error("[GLS TIMING VIOLATION] Detected Setup/Hold Violation at %0t ps in instance %m!", $time);
    end

    //=========================================================================
    // STIMULUS GENERATION WITH SUB-NANOSECOND PHASE CONTROL
    //=========================================================================
    initial begin
        // Reset Phase
        rst_n   = 1'b0;
        enable  = 1'b0;
        data_in = 8'h00;
        #25.0; // Wait 5 clock cycles
        
        // Deassert reset asynchronously to test Recovery/Removal
        #1.2 rst_n = 1'b1; // สลับนอกขอบคล็อกเพื่อเช็ค Reset Removal
        #10.0;

        $display("[%0t ns] Applying PWM Modulation Stimulus...", $time);
        
        // Loop through PWM duty cycles
        for (int i = 0; i < 16; i++) begin
            @(posedge clk);
            #0.8; // Inject small phase offset to stress setup/hold in GLS
            enable  <= 1'b1;
            data_in <= i * 16;
        end

        // Wait for system response
        #200.0;

        // Check for Unknowns (X-Propagation Check)
        if ($isunknown(pwm_out)) begin
            $fatal(1, "[GLS FATAL] X-State detected on pwm_out! Circuit collapsed into X-Pessimism or Metastability.");
        end else begin
            $display("[GLS PASS] Simulation finished with zero X-propagation and verified timing.");
        end

        $finish(0);
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความเสียหายจริงในภาคสนาม (失敗事例 - Shippai Jirei)
**ชิป ASIC ควบคุมมอเตอร์ขับเคลื่อนในระบบส่งกำลังของรถยนต์ไฟฟ้า (EV Powertrain Inverter Controller)** เกิดการระเบิดเสียหายขณะทดสอบการขับขี่ในห้องควบคุมอุณหภูมิต่ำสุดขั้ว (-40°C Cold Chamber Test): ภาคกำลังไฟสูง (Inverter High-Voltage Stage) เกิดการลัดวงจรตรงอย่างรุนแรง (Shoot-Through Short Circuit) ทำให้โมดูล SiC MOSFET ระเบิด ขั้วต่อละลาย และชุดแบตเตอรี่ตัดวงจรฉุกเฉิน คิดเป็นมูลค่าความเสียหายทางวิศวกรรมและการล่าช้าของสายการผลิตกว่า 800,000 ดอลลาร์สหรัฐ

---

### การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมมอสเฟต SiC ภาคกำลังจึงเกิดการลัดวงจรตรง (Shoot-Through)?**
   - *คำตอบ:* ขาสัญญาณ PWM ควบคุมสวิตช์ฝั่งบน (High-Side) และฝั่งล่าง (Low-Side) เปิดทำงานพร้อมกันชั่วขณะโดยไม่มีการเว้นช่วงเวลา Dead-time
2. **ทำไมวงจรสร้าง Dead-time จึงหยุดทำงานชั่วคราว?**
   - *คำตอบ:* ตรรกะตรวจจับสัญญาณนาฬิกาเกิด **Hold Time Violation** ในวงจรนับ Dead-time Counter ทำให้ตัวนับกระโดดข้ามค่าศูนย์
3. **ทำไมปัญหานี้จึงเกิดขึ้นเฉพาะที่อุณหภูมิต่ำ -40°C แต่ไม่เกิดที่อุณหภูมิห้อง?**
   - *คำตอบ:* ที่อุณหภูมิต่ำมาก ทรานซิสเตอร์ในโหนด 16nm มีความเร็วในการนำไฟฟ้าสูงขึ้น (Short Propagation Delay) สัญญาณ Data เดินทางเร็วเกินไปจนมาถึงก่อนที่สัญญาณนาฬิกาจะคงสภาวะ Hold Time ขั้นต่ำ (Best/Fast Corner Hold Violation)
4. **ทำไมขั้นตอนการจำลอง Testbench ก่อนการ Tape-out จึงตรวจไม่พบบักนี้?**
   - *คำตอบ:* ทีมวิศวกรรมรันเฉพาะ **RTL Simulation (Zero-Delay)** โดยคิดว่า Static Timing Analysis (STA) ใน Vivado/PrimeTime มีรายงานว่า Setup Time ผ่านฉลุย จึงละเลยการรัน **Gate-Level Simulation (GLS) ด้วยไฟล์ Min-Corner SDF**
5. **ทำไมขั้นตอน Kenzu (検図) จึงยอมให้ผ่านการอนุมัติ?**
   - *คำตอบ:* ขาดข้อบังคับ **"Multi-Corner GLS Sign-Off Gate"** สำหรับวงจรควบคุม Safety-Critical ในยานยนต์ไฟฟ้า

---

### แผนผังสาเหตุและผล (Ishikawa Fishbone Diagram)

```
==================================================================================================
                                    ISHIKAWA FISHBONE CAUSE-EFFECT DIAGRAM
==================================================================================================

   MAN (บุคลากร)                                   MACHINE / TOOLS (เครื่องมือ)
   ----------------                                ---------------------------
   พึ่งพาเฉพาะผล STA ละเลยการทำ GLS               ไม่รันจำลองที่ Min-Corner (Fast/Cold)
   ไม่เข้าใจเรื่อง Cold-Temperature Inversion      Simulator ถูกปิดออปชัน Negative Timing Checks
               \                                                /
                \                                              /
                 \                                            /
                  +------------------------------------------+
                  |                                          |
                  |  EV INVERTER SHOOT-THROUGH EXPLOSION     | ===>> [800K USD TEST DAMAGE]
                  |                                          |
                  +------------------------------------------+
                 /                                            \
                /                                              \
   METHOD (ระเบียบปฏิบัติ)                          MATERIAL / ENVIRONMENT (สภาวะแวดล้อม)
   ----------------------                          -------------------------------------
   ขาดนโยบายบังคับ Multi-Corner GLS Sign-off      อุณหภูมิต่ำ -40°C เร่งทรานซิสเตอร์ให้เร็วจัด
   ไม่ได้ตรวจเช็ค Dead-time FSM ที่ระดับ Netlist   การกระจายตัวของ Clock Tree Skew ไม่สมดุล
==================================================================================================
```

---

### คู่มือปฏิบัติการตรวจสอบ OJT หน้างาน: ระเบียบปฏิบัติในการทำ Gate-Level Simulation Sign-Off

1. **Step 1: การรันตรวจสอบทั้ง 3 สภาวะ (Min, Typ, Max Corner Sweep)**
   - ต้องคอมไพล์และรัน GLS แยกกันอย่างเด็ดขาด 3 รอบการทดสอบ:
     - **Max Corner (Slow):** ตรวจสอบ Setup Timing และ Maximum Frequency Margin
     - **Min Corner (Fast):** ตรวจสอบ Hold Timing, Race Conditions, และ Glitch Hazards
     - **Typical Corner:** ยืนยันพฤติกรรมมาตรฐานที่สภาวะปกติ
2. **Step 2: การตรวจสอบ SDF Error Log (Zero Annotation Failures)**
   - ตรวจสอบไฟล์รายงาน SDF Log เสมอ:
     - ข้อผิดพลาด `SDF-NEGO` (Negative delay ไม่สามารถประมวลผลได้): ต้องเปิดสวิตช์ `+neg_tchk`
     - ข้อผิดพลาด `SDF-PIN` (ไม่พบพินใน Netlist): เกิดจาก Port Mismatch ต้องแก้คำสั่ง Synthesis Keep Hierarchy
   - **เกณฑ์ผ่าน:** จำนวน Unannotated Ports ต้องเป็นศูนย์ (0 Ports Failed)
3. **Step 3: การขจัด X-Pessimism ที่ถูกต้อง (Safe X-Handling)**
   - หากเจอการแพร่กระจายของ `X` ที่เกิดจาก MUX ให้ใช้เครื่องมือ X-Filtering (เช่น Synopsys VCS `+vcs+initreg+config` หรือการผูก SVA ขนาน)
   - ห้ามแก้ปัญหาด้วยการฝืนป้อน Reset บังคับทับ Netlist เพราะจะบดบังบักวงจรจริง

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (専門用語)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / อังกฤษ | บริบทการใช้งานเชิงวิศวกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **ゲートレベルシミュレーション** | ゲートレベルシミュレーション | Geeto Reberu Shimyureeshon | Gate-Level Simulation (GLS) | การจำลองพฤติกรรมวงจรในระดับเกตและเน็ตลิสต์จริง |
| **遅延逆注記** | ちえんぎゃくちゅうき | Chien Gyaku Chuuki | Delay Back-Annotation | การนำไฟล์หน่วงเวลาจริง (SDF) กลับมาใส่ในโมเดลเกต |
| **標準遅延形式** | ひょうじゅんちえんけいしき | Hyoujun Chien Keishiki | Standard Delay Format (SDF) | รูปแบบไฟล์มาตรฐานสำหรับจัดเก็บค่าความล่าช้า |
| **最悪コーナー** | さいあくコーナー | Saiaku Koonaa | Worst / Slow Timing Corner | สภาวะแวดล้อมที่วงจรทำงานช้าที่สุด (เสี่ยง Setup) |
| **最良コーナー** | さいりょうコーナー | Sairyou Koonaa | Best / Fast Timing Corner | สภาวะแวดล้อมที่วงจรทำงานเร็วที่สุด (เสี่ยง Hold) |
| **貫通電流** | かんつうでんりゅう | Kantsuu Denryuu | Shoot-Through Current | กระแสลัดวงจรตรงระหว่างสวิตช์บนและล่างในอินเวอร์เตอร์ |
| **不定値悲観性** | ふていちひかんせい | Futeichi Hikansei | X-Pessimism | สภาวะที่ Simulator พ่นค่า X เกินจริงในระดับเกต |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図審議 - Kenzu Shingi)

**สถานที่:** ห้องประชุมอนุมัติการส่งผลิตหน้ากากวงจร (Tape-out Mask Sign-off Gate)  
**ผู้เข้าร่วม:**
- **โอโนะ (大野):** Senior Production Sign-off Chief (量産承認主査)
- **สิทธิชัย (シッティチャイ):** Senior Physical Design & Verification Lead (実装・検証担当)

---

**大野主査 (โอโนะ):**  
「シッティチャイさん、EV用インバータ制御ASICのテープアウト前チェックリストを確認しています。STA（静的タイミング解析）のレポートはすべてゼロバイオレーションになっていますが、**SDF逆注記（Back-Annotation）**による**ゲートレベルシミュレーション（GLS）**の結果はどこにありますか？」  
*(คุณสิทธิชัยครับ ผมกำลังตรวจเช็ครายการ Sign-off ก่อนส่ง Tape-out ของชิปอินเวอร์เตอร์ EV รายงาน STA ระบุว่าไม่มีการละเมิดเวลาเลย แต่รายงานผลการจำลองระดับเกต (GLS) พร้อมการใส่ไฟล์หน่วงเวลา SDF อยู่ที่ไหนครับ?)*

**シッティチャイ (สิทธิชัย):**  
「大野主査、PrimeTimeで全PVTコーナーのSTAタイミング収束を確認済みですので、シミュレーション実行時間の長いGLSは省略し、RTLシミュレーション結果のみで最終判定を行いました。」  
*(หัวหน้าโอโนะครับ ทางเราตรวจสอบการบีบเวลาด้วย STA ครบทุกสภาวะ PVT ใน PrimeTime แล้ว เนื่องจาก GLS ต้องใช้เวลารันนานมาก จึงได้ละเว้นไว้และใช้ผลการจำลอง RTL ในการตัดสินขั้นสุดท้ายแทนครับ)*

**大野主査 (โอโนะ):**  
「何を言っているんですか！正気の沙汰とは思えません！STAは静的なパス遅延を計算するだけで、非同期リセットの解除シーケンスや、動的なクロック切り替え時の**グリッチ（Glitch）**、そしてデッドタイム制御回路の動的な競合状態（Race Condition）までは検知できません。特に**低温・最良コーナー（Min Corner）**でのホールド違反による貫通電流（Shoot-through）が発生したら、インバータモジュールが即座に爆発しますよ！」  
*(พูดอะไรออกมาครับ! ไม่มีความรอบคอบเอาเสียเลย! STA เป็นเพียงการคำนวณดีเลย์ตามเส้นทางแบบสถิต มันไม่สามารถตรวจจับลำดับการปลด Reset แบบไม่ประสานเวลา, ปัญหาสัญญาณรบกวน Glitch ตอนสลับคล็อก, หรือ Race Condition แบบพลวัตในวงจรควบคุม Dead-time ได้เลย โดยเฉพาะอย่างยิ่งหากเกิด Hold Violation ในสภาวะอุณหภูมิต่ำสุดที่ Min Corner จนเกิดกระแสทะลวงตรง อินเวอร์เตอร์จะระเบิดเป็นจุณทันทีนะครับ!)*

**シッティチャイ (สิทธิชัย):**  
「私の判断が浅はかでした。大変申し訳ありません！直ちにMinコーナー、Maxコーナー双方のSDFファイルを生成し、ネットリストを用いたGLSリグレッションテストを実行します。」  
*(การตัดสินใจของผมตื้นเขินเกินไป ขออภัยเป็นอย่างยิ่งครับ! ผมจะรีบสร้างไฟล์ SDF ทั้งฝั่ง Min Corner และ Max Corner แล้วรันการทดสอบ GLS Regression ด้วย Netlist จริงทันทีครับ)*

**大野主査 (โอโนะ):**  
「ええ。それと、SDF注記ログで**未注記ピン（Unannotated Pins）**が1本でも残っていないか、およびシミュレーション開始時のリセットシーケンスで**不定値（X-State）**の伝搬が発生していないかも厳密に精査してください。GLSでの全パスが確認できるまで、フォトマスク製造ラインの発注書には絶対に捺印しません。」  
*(ใช่ และอย่าลืมตรวจสอบ Log ของ SDF ด้วยว่าไม่มีพินที่ขาดการใส่ดีเลย์ค้างอยู่แม้แต่พินเดียว พร้อมทั้งตรวจสอบอย่างเข้มงวดว่าไม่มีค่าที่ไม่ทราบแน่ชัด (X) แพร่กระจายในระหว่างกระบวนการ Reset จนกว่าผลการทดสอบ GLS จะผ่านอย่างสมบูรณ์แบบ 100% ผมจะไม่มีวันประทับตราสั่งทำ Photomask เด็ดขาดครับ)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณหน้าต่างเวลาและผลลัพธ์ของ Negative Setup Time

ในเซลล์มาตรฐาน D-Flip-Flop ตัวหนึ่ง มีค่าพารามิเตอร์ความล่าช้าภายในและการทำงานที่แกนสลัก (Internal Latch Core) ดังนี้:
- เวลาหน่วงภายในของสายสัญญาณข้อมูล (Internal Data Delay): $\tau_d = 40\text{ ps}$
- เวลาหน่วงภายในของสายสัญญาณนาฬิกา (Internal Clock Delay): $\tau_{clk} = 150\text{ ps}$
- Setup Time ขั้นต่ำที่แกนสลักข้อมูลภายใน (Internal Core Setup): $t_{su\_core} = 80\text{ ps}$
- Hold Time ขั้นต่ำที่แกนสลักข้อมูลภายใน (Internal Core Hold): $t_{h\_core} = 30\text{ ps}$

จงคำนวณหาค่า Setup Time สุทธิที่ขาพินภายนอก ($t_{su\_pin}$) และ Hold Time สุทธิที่ขาพินภายนอก ($t_{h\_pin}$) ที่จะปรากฏในไฟล์ SDF ของเซลล์นี้:

- **A)** $t_{su\_pin} = +190\text{ ps}$, $t_{h\_pin} = -80\text{ ps}$
- **B)** $t_{su\_pin} = -30\text{ ps}$, $t_{h\_pin} = +140\text{ ps}$
- **C)** $t_{su\_pin} = -30\text{ ps}$, $t_{h\_pin} = +30\text{ ps}$
- **D)** $t_{su\_pin} = +110\text{ ps}$, $t_{h\_pin} = +110\text{ ps}$

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) $t_{su\_pin} = -30\text{ ps}$, $t_{h\_pin} = +140\text{ ps}$**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ใช้สูตรทางฟิสิกส์คำนวณค่า Setup Time ที่วัดได้จากขาพินภายนอก:
   $$t_{su\_pin} = t_{su\_core} + \tau_{d} - \tau_{clk}$$
   แทนค่าตัวเลข:
   $$t_{su\_pin} = 80\text{ ps} + 40\text{ ps} - 150\text{ ps} = 120\text{ ps} - 150\text{ ps} = \mathbf{-30\text{ ps}}$$
   (ผลลัพธ์เป็น **Negative Setup Time** หมายความว่า ข้อมูลสามารถมาถึงหลังขอบสัญญาณนาฬิกาได้ 30 ps เพราะสัญญาณนาฬิกาถูกชะลออยู่ภายใน Flop นานกว่าข้อมูล)
2. ใช้สูตรคำนวณค่า Hold Time ที่วัดได้จากขาพินภายนอก:
   $$t_{h\_pin} = t_{h\_core} + \tau_{clk} - \tau_{d}$$
   แทนค่าตัวเลข:
   $$t_{h\_pin} = 30\text{ ps} + 150\text{ ps} - 40\text{ ps} = 180\text{ ps} - 40\text{ ps} = \mathbf{+140\text{ ps}}$$
3. ตรวจสอบความถูกต้องด้วยทฤษฎีความคงที่ของหน้าต่างเวลา (Window Invariance Check):
   - หน้าต่างเวลาที่แกนภายใน:
     $$W_{core} = t_{su\_core} + t_{h\_core} = 80 + 30 = 110\text{ ps}$$
   - หน้าต่างเวลาที่ขาพินภายนอก:
     $$W_{pin} = t_{su\_pin} + t_{h\_pin} = (-30) + 140 = 110\text{ ps}$$
   - ค่าทั้งสองตรงกันสมบูรณ์ ($W_{core} \equiv W_{pin}$) ซึ่งเป็นการยืนยันความถูกต้องทางคณิตศาสตร์

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** สลับเครื่องหมายบวกลบระหว่าง $\tau_d$ กับ $\tau_{clk}$
- **ข้อ C ผิด:** คิดว่า Hold Time ภายนอกจะเท่ากับภายในโดยไม่ได้บวกความล่าช้าสัมพัทธ์ของ Clock
- **ข้อ D ผิด:** คำนวณโดยไม่คิดผลกระทบของ Internal Delay Shifting

---

### คำถามที่ 2: กลไกการกรอง Glitch ด้วยพารามิเตอร์ Pulse Rejection Limits

กำหนดให้ทางเดินสัญญาณเกตใน Netlist มีค่าการหน่วงเวลาของการแพร่กระจายสัญญาณ (Propagation Delay) เท่ากับ $t_{prop} = 1,000\text{ ps}$  
ในไฟล์คอนฟิกของ Simulator มีการกำหนดเกณฑ์การควบคุมพัลส์ (Pulse Rejection Parameters) ดังนี้:
- **Reject Limit ($r$-limit):** $40\%$ ของค่า Propagation Delay
- **Error Limit ($e$-limit):** $80\%$ ของค่า Propagation Delay

หากมีสัญญาณรบกวน (Glitch Pulse) ขนาดความกว้าง $W_{pulse} = 650\text{ ps}$ วิ่งเข้ามาที่อินพุตของเกตนี้ พฤติกรรมของ Gate-Level Simulator ตามมาตรฐาน Verilog จะเป็นอย่างไร?

- **A)** พัลส์จะถูกกลืนหายไปโดยสมบูรณ์ (Swallowed / Rejected) และไม่ปรากฏที่เอาต์พุต
- **B)** พัลส์จะส่งผ่านไปยังเอาต์พุตอย่างสมบูรณ์โดยไม่มีการเปลี่ยนแปลง
- **C)** เอาต์พุตของเกตจะกลายเป็นสถานะไม่ทราบแน่ชัด (`X`) พร้อมพิมพ์แจ้งเตือน Timing Violation Warning
- **D)** Simulator จะหยุดทำงานทันทีด้วยข้อผิดพลาด Fatal Error

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: C) เอาต์พุตของเกตจะกลายเป็นสถานะไม่ทราบแน่ชัด (`X`) พร้อมพิมพ์แจ้งเตือน Timing Violation Warning**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. คำนวณขอบเขตเวลาทางคณิตศาสตร์ของ $r$-limit และ $e$-limit:
   - **Reject Threshold ($T_{reject}$):**
     $$T_{reject} = 40\% \times t_{prop} = 0.40 \times 1,000\text{ ps} = 400\text{ ps}$$
   - **Error Threshold ($T_{error}$):**
     $$T_{error} = 80\% \times t_{prop} = 0.80 \times 1,000\text{ ps} = 800\text{ ps}$$
2. กฎการตัดสินใจของ Pulse Control Algorithm ตามมาตรฐาน IEEE:
   - กรณีที่ 1: หาก $W_{pulse} \le T_{reject}$ (พัลส์แคบมาก): เกตจะกลืนสัญญาณทิ้งทั้งหมด (Suppressed / Filtered out)
   - กรณีที่ 2: หาก $T_{reject} < W_{pulse} < T_{error}$ (พัลส์กึ่งกลางระหว่างจุดไม่แน่ชัด): พัลส์มีพลังงานเพียงพอที่จะเริ่มเปลี่ยนสถานะทรานซิสเตอร์แต่อาจไม่สมบูรณ์ เอาต์พุตจะถูกบังคับให้เป็น **`X` (Unknown / Glitch Hazard)**
   - กรณีที่ 3: หาก $W_{pulse} \ge T_{error}$ (พัลส์กว้างเพียงพอ): สัญญาณจะส่งผ่านไปเป็นพัลส์ปกติ
3. พิจารณาขนาดของพัลส์ในโจทย์: $W_{pulse} = 650\text{ ps}$
   $$400\text{ ps} < 650\text{ ps} < 800\text{ ps}$$
   เนื่องจากค่าตกอยู่ในช่วงระหว่าง $T_{reject}$ และ $T_{error}$ ดังนั้นเอาต์พุตจะกลายเป็น **`X`** พร้อมออก Warning ใน Console

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** จะถูก Swallow ก็ต่อเมื่อพัลส์แคบกว่า $400\text{ ps}$
- **ข้อ B ผิด:** จะส่งผ่านสมบูรณ์ก็ต่อเมื่อพัลส์กว้างตั้งแต่ $800\text{ ps}$ ขึ้นไป
- **ข้อ D ผิด:** Glitch ไม่ได้ทำให้เกิด Fatal Crash ของ Simulator แต่สร้างสถานะ X เพื่อให้ระบบตรวจสอบความทนทาน

---

### คำถามที่ 3: ปัญหา X-Pessimism ในเซลล์ลอจิก MUX และการแก้ปัญหาอย่างปลอดภัย

ในการจำลอง Gate-Level Simulation วิศวกรพบว่าสัญญาณข้อมูลที่ออกจากโมดูล Multiplexer (MUX 2:1) กลายเป็น `X` ทุกครั้งที่มีการสลับขาควบคุม (`sel`) แม้ว่าสัญญาณข้อมูลขาเข้าทั้งสองพอร์ตจะมีค่าคงที่อยู่ที่ระดับลอจิกสูง (`d0 = 1'b1, d1 = 1'b1`)  
สาเหตุทางทฤษฎีและแนวทางการแก้ไขที่ถูกต้องที่สุดตามมาตรฐานอุตสาหกรรมคือข้อใด?

- **A)** เกิดจากวงจรในเน็ตลิสต์มีการลัดวงจรจริง ต้องแก้ไขการเดินสายใน RTL ใหม่
- **B)** เป็นพฤติกรรมธรรมชาติของ Boolean Evaluation ในแบบจำลองทางคณิตศาสตร์ของ Simulator แก้ไขโดยการใช้สวิตช์คอมไพเลอร์ที่รองรับ X-Optimism หรือใช้อินสแตนซ์พรีมิทิฟที่มีการใส่คำสั่ง Don't-Care Balancing
- **C)** เกิดจากค่าแรงดันไฟฟ้าในไฟล์ SDF ไม่ถูกต้อง ต้องแก้แรงดันเป็น 5V
- **D)** เกิดจาก Simulator มีบักในเวอร์ชันนั้น ต้องดาวน์เกรดเป็น Verilog-1995

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) เป็นพฤติกรรมธรรมชาติของ Boolean Evaluation ในแบบจำลองทางคณิตศาสตร์ของ Simulator แก้ไขโดยการใช้สวิตช์คอมไพเลอร์ที่รองรับ X-Optimism หรือใช้อินสแตนซ์พรีมิทิฟที่มีการใส่คำสั่ง Don't-Care Balancing**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ในสมการเกตลอจิกพื้นฐานของ MUX 2:1:
   $$Y = (sel \wedge d1) \vee (\neg sel \wedge d0)$$
2. เมื่อ $sel$ กำลังสลับค่าระหว่าง $0 \to 1$ ใน Gate-Level จะมีช่วงเวลาที่ $sel$ เป็น `X`:
   แทนค่า $d0 = 1$ และ $d1 = 1$:
   $$Y = (X \wedge 1) \vee (\neg X \wedge 1) = X \vee X = \mathbf{X}$$
3. ในทางฟิสิกส์ซิลิคอนจริง ไม่ว่า $sel$ จะอยู่ที่จุดกึ่งกลางใด (แรงดัน $0.5 V_{DD}$) เอาต์พุต $Y$ จะยังคงเป็น $1$ เพราะทั้งสองฝั่งดึงขึ้น High เหมือนกัน ปรากฏการณ์ที่ Simulator ตีความเป็น `X` จึงเรียกว่า **X-Pessimism**
4. การแก้ไขในระดับวิศวกรอาวุโส:
   - ใช้เทคโนโลยี Compiler X-Filtering (เช่น Synopsys VCS `+x-filter` หรือการเปิดโหมด `xprop`)
   - หรือในไลบรารี Standard Cell มีการเขียน User-Defined Primitive (UDP) ที่ระบุเงื่อนไขพิเศษว่า: หาก $d0 == d1$ ให้เอาต์พุตคงค่าเดิมโดยไม่สนใจสถานะของ $sel$

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** วงจรไม่ได้มีปัญหาทางกายภาพ แต่เป็นข้อจำกัดของ Discrete Logic Simulator
- **ข้อ C ผิด:** แรงดันไฟฟ้าไม่ได้ถูกระบุโดยตรงในไฟล์ SDF ในรูปแบบที่ทำให้เกิดปัญหา MUX X-Pessimism
- **ข้อ D ผิด:** การดาวน์เกรด Simulator ไม่ได้ช่วยแก้ปัญหาโครงสร้างตรรกะแบบนี้
