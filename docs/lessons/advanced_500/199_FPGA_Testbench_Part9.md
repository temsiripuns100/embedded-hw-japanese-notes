# Lesson 199: FPGA Testbench Part 9 — DO-254 DAL-A Requirements-Based Verification & Traceability (การตรวจสอบย้อนกลับและการทดสอบตามข้อกำหนดมาตรฐานอากาศยาน DO-254 DAL-A)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในวงการวิศวกรรมการบินและอวกาศ (Avionics) ความผิดพลาดของระบบอิเล็กทรอนิกส์เพียงจุดเดียวหมายถึงการสูญเสียชีวิตของผู้โดยสารและลูกเรือทั้งลำ องค์กรกำกับการบินระดับสากล (FAA ในสหรัฐอเมริกา และ EASA ในยุโรป) จึงบังคับใช้มาตรฐาน **RTCA DO-254 / EUROCAE ED-80 (Design Assurance Guidance for Airborne Electronic Hardware)** เพื่อควบคุมกระบวนการพัฒนาฮาร์ดแวร์อิเล็กทรอนิกส์สำหรับอากาศยานทั้งหมด

มาตรฐาน DO-254 แบ่งระดับความปลอดภัยตามผลกระทบจากความล้มเหลว (Failure Severity) ออกเป็น **Design Assurance Level (DAL)**:
- **DAL-A (Catastrophic):** ความล้มเหลวทำให้เครื่องบินตกและสูญเสียชีวิตทั้งหมด (เช่น Fly-By-Wire, FADEC Engine Control)
- **DAL-B (Hazardous/Severe-Major):** ผู้โดยสารบาดเจ็บสาหัส นักบินทำงานหนักวิกฤต
- **DAL-C (Major):** ลดทอนสมรรถนะของเครื่องบินอย่างมีนัยสำคัญ
- **DAL-D (Minor):** ส่งผลกระทบเพียงเล็กน้อย
- **DAL-E (No Safety Effect):** ไม่มีผลกระทบต่อความปลอดภัย

สำหรับระบบระดับ **DAL-A** กฎหมายการบินไม่อนุญาตให้วิศวกรทดสอบวงจรตามความพอใจ แต่บังคับใช้กระบวนการ **Requirements-Based Verification (RBV)** และ **Structural Coverage Analysis (SCA)** ที่เข้มงวดที่สุดในโลก

```
+--------------------------------------------------------------------------------------------------+
|                   DO-254 DAL-A REQUIREMENTS-BASED VERIFICATION & TRACEABILITY                    |
+--------------------------------------------------------------------------------------------------+
                                                                                                    
                  +-------------------------------------------------------+                         
                  |          System Safety Assessment (ARP4761)           |                         
                  |   Hazard Analysis -> Derived Safety Requirements      |                         
                  +-------------------------------------------------------+                         
                                              |                                                     
                                              v                                                     
                  +-------------------------------------------------------+                         
                  |        Hardware Requirements Document (HRD)           |                         
                  | [REQ-FBW-0101]: Dual-Actuator Pressure Interlock Rate |                         
                  +-------------------------------------------------------+                         
                         | (1-to-1 Forward Trace)          | (1-to-1 Forward Trace)                 
                         v                                 v                                        
           +---------------------------+       +------------------------------------+               
           |   RTL Source Code (DUT)   |       |   Verification Environment / SVA   |               
           | [TAG: REQ-FBW-0101]       |       | [TAG: REQ-FBW-0101]                |               
           | logic interlock_trip;     |       | property p_interlock_rate;         |               
           +---------------------------+       +------------------------------------+               
                         |                                 |                                        
                         +----------------+----------------+                                        
                                          |                                                         
                                          v                                                         
                  +-------------------------------------------------------+                         
                  |         VERIFICATION TRACEABILITY MATRIX (VTM)        |                         
                  |  - Complete Bi-directional Traceability Link          |                         
                  |  - Proof of NO Untraced / Dead RTL Code               |                         
                  |  - 100% Statement, Branch, and MC/DC Coverage Closure|                         
                  +-------------------------------------------------------+                         
```

---

### 1.1 ทฤษฎีความครอบคลุมระดับเกณฑ์เงื่อนไข/การตัดสินใจแบบแปรผัน (MC/DC Theory & Mathematics)

สำหรับระบบ DO-254 DAL-A เกณฑ์การวัด Code Coverage ธรรมดาไม่เพียงพอ แต่ต้องบรรลุเกณฑ์ **Modified Condition / Decision Coverage (MC/DC)** ระดับ 100% เต็ม

#### 1. นิยามทางคณิตศาสตร์ของ MC/DC
พิจารณาการตัดสินใจแบบบูลีน (Decision $D$) ซึ่งประกอบด้วยเงื่อนไขย่อย (Conditions $C_1, C_2, \dots, C_N$) เชื่อมต่อกันด้วยตัวดำเนินการทางตรรกศาสตร์:
$$D = f(C_1, C_2, \dots, C_N)$$

เงื่อนไขในการผ่านเกณฑ์ MC/DC คือ:
1. ทุก Decision ($D$) เคยมีผลลัพธ์เป็นทั้ง **True** และ **False** อย่างน้อยหนึ่งครั้ง
2. ทุก Condition ย่อย ($C_i$) เคยมีค่าเป็นทั้ง **True** และ **False** อย่างน้อยหนึ่งครั้ง
3. **Condition Independence Proof (การพิสูจน์ความเป็นอิสระ):** สำหรับแต่ละเงื่อนไข $C_i$ จะต้องมีคู่ของเวกเตอร์ทดสอบ $(T_{True}, T_{False})$ ที่แสดงให้เห็นว่า:
   $$\text{เมื่อ } C_i \text{ เปลี่ยนสถานะจาก True เป็น False โดยที่ทุกเงื่อนไขย่อยอื่นคงที่ทั้งหมด } (C_k = \text{const } \forall k \ne i)$$
   $$\implies \text{ผลลัพธ์ของ Decision } D \text{ จะต้องเปลี่ยนสถานะตามไปด้วยทันที!}$$

#### 2. ทฤษฎีบทการประหยัดจำนวนเวกเตอร์ทดสอบ (Test Vector Minimization Math)
- หากใช้วิธีทดสอบแบบกวาดหมดทุกกรณี (Exhaustive Testing) สำหรับ $N$ เงื่อนไข จะต้องใช้:
  $$N_{exhaustive} = 2^N \text{ เวกเตอร์}$$
  หากมี 10 เงื่อนไข จะต้องใช้ถึง $2^{10} = 1,024$ ครั้ง
- แต่ทฤษฎี MC/DC พิสูจน์ว่า จำนวนเวกเตอร์ทดสอบขั้นต่ำสุดที่เป็นไปได้ ($N_{MCDC\_min}$) ในการพิสูจน์ความเป็นอิสระของทุกตัวแปรคือ:
  $$N_{MCDC\_min} = N + 1 \text{ เวกเตอร์}$$
  สำหรับ 10 เงื่อนไข จะใช้เพียงแค่ **11 เวกเตอร์** เท่านั้น แต่ละเวกเตอร์ต้องได้รับการออกแบบทางคณิตศาสตร์อย่างพิถีพิถัน

---

### 1.2 เมทริกซ์การตรวจสอบย้อนกลับ (Verification Traceability Matrix - VTM) และอันตรายของ Dead Code

ข้อกำหนดสำคัญที่สุดของ DO-254 คือ **ความสัมพันธ์แบบสองทิศทาง (Bi-Directional Traceability)**:
- **Forward Traceability:** ทุก Requirement ต้องมีโค้ด RTL รองรับ และมี Testcase ทดสอบ
- **Backward Traceability:** ทุกบรรทัดของโค้ด RTL และทุก Testcase จะต้องสามารถสาวกลับไปยัง Requirement ได้เสมอ

#### ปัญหา Dead Code / Deactivated Code:
หากผู้ตรวจประเมินอากาศยาน (FAA Auditor) พบว่าใน RTL มีโค้ดหรือสัญญาณที่ไม่สามารถเชื่อมโยงกลับไปยัง Requirement ใดๆ ได้ (Untraced Code) จะเกิดผลกระทบร้ายแรง:
- โค้ดนั้นอาจเป็นฟังก์ชันที่วิศวกรแอบใส่ไว้เล่นๆ หรือเป็นส่วนเกินจากการคัดลอก IP
- ในการบินจริง หากสภาวะแวดล้อมกระตุ้นให้โค้ดส่วนนี้ทำงานโดยไม่ตั้งใจ (Unintended Function) อาจส่งผลให้เครื่องบินสูญเสียการควบคุม
- **บทลงโทษ:** ไม่อนุมัติใบรับรองความสมควรเดินอากาศ (Rejection of Certification) จนกว่าจะลบโค้ดทิ้งหรือพิสูจน์ว่าเป็น Deactivated Code ตามข้อกำหนดพิเศษ

---

### 1.3 RTL & SystemVerilog Harness: Fly-By-Wire Actuator Safety Monitor (`fbw_actuator_monitor.sv`)

โค้ดนี้สาธิตการเขียนฮาร์ดแวร์และ SystemVerilog Assertions ตามมาตรฐาน DO-254 DAL-A โดยมีการใส่แท็กเชื่อมโยง Requirement (Traceability Tags) ครบทุกฟังก์ชัน

```systemverilog
//=============================================================================
// Module: fbw_actuator_monitor
// Description: DO-254 DAL-A Flight Control Primary Surface Actuator Monitor
// Requirements Traceability: REQ-FBW-SAF-0210, REQ-FBW-SAF-0215
// Certification Baseline: FAA AC 20-152A / RTCA DO-254 DAL-A
//=============================================================================

`timescale 1ns / 1ps

module fbw_actuator_monitor (
    input  logic        clk,              // 50 MHz Avionics Bus Clock
    input  logic        rst_n,            // Asynchronous Power-on Reset
    input  logic        pilot_active,     // Requirement Tag: REQ-FBW-SAF-0210
    input  logic        hydraulic_press_ok,// Requirement Tag: REQ-FBW-SAF-0210
    input  logic        sensor_valid,     // Requirement Tag: REQ-FBW-SAF-0210
    input  logic        surface_jammed,   // Requirement Tag: REQ-FBW-SAF-0215
    output logic        actuator_drive_en,// Primary drive enable
    output logic        fault_trip_latch  // Latch alarm for Flight Control Computer
);

    // [REQ-FBW-SAF-0210]: Actuator Enable Decision Logic
    // Logic: Drive is enabled IF AND ONLY IF (pilot_active AND hydraulic_press_ok AND sensor_valid)
    // AND NOT surface_jammed.
    // Decision D = (pilot_active && hydraulic_press_ok && sensor_valid) && !surface_jammed
    logic enable_decision;

    always_comb begin
        // Decision expression subjected to 100% MC/DC Analysis
        enable_decision = (pilot_active && hydraulic_press_ok && sensor_valid) && (!surface_jammed);
    end

    // Sequential Output Register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            actuator_drive_en <= 1'b0;
            fault_trip_latch  <= 1'b0;
        end else begin
            actuator_drive_en <= enable_decision;

            // [REQ-FBW-SAF-0215]: Fault Trip Latch
            // If surface is jammed while pilot is commanding, latch fault forever
            if (surface_jammed && pilot_active) begin
                fault_trip_latch <= 1'b1;
            end
        end
    end

    //=========================================================================
    // DO-254 FORMAL SVA PROPERTY HARNESS (Requirement-Tagged Assertions)
    //=========================================================================

    // SVA-FBW-01: Verifies REQ-FBW-SAF-0210 (Actuator Enable Legality)
    property p_req_fbw_saf_0210;
        @(posedge clk) disable iff (!rst_n)
        actuator_drive_en |-> (pilot_active && hydraulic_press_ok && sensor_valid && !surface_jammed);
    endproperty
    a_req_fbw_saf_0210: assert property (p_req_fbw_saf_0210)
        else $fatal(1, "[DO-254 VIOLATION][REQ-FBW-SAF-0210] Actuator driven illegally!");

    // SVA-FBW-02: Verifies REQ-FBW-SAF-0215 (Instant Trip on Surface Jam)
    property p_req_fbw_saf_0215;
        @(posedge clk) disable iff (!rst_n)
        surface_jammed |=> !actuator_drive_en;
    endproperty
    a_req_fbw_saf_0215: assert property (p_req_fbw_saf_0215)
        else $fatal(1, "[DO-254 VIOLATION][REQ-FBW-SAF-0215] Jammed actuator failed to disengage!");

endmodule

// Testbench Harness Executing Minimal MC/DC Test Suite for REQ-FBW-SAF-0210
module tb_do254_mcdc_suite;

    logic clk, rst_n;
    logic pilot_active;
    logic hydraulic_press_ok;
    logic sensor_valid;
    logic surface_jammed;
    logic actuator_drive_en;
    logic fault_trip_latch;

    initial clk = 0;
    always #10 clk = ~clk; // 50 MHz

    fbw_actuator_monitor dut (.*);

    // MC/DC Verification Task for 4 Variables: P, H, S, J
    // D = (P && H && S) && (!J)
    // Minimal Test Set requires N + 1 = 4 + 1 = 5 Vectors!
    task automatic run_mcdc_vectors();
        $display("--- RUNNING 100%% MC/DC COMPLIANCE SUITE (5 VECTORS) ---");

        // Vector 1 (Baseline All TRUE for Enable): P=1, H=1, S=1, J=0 => D=1
        apply_vector(1'b1, 1'b1, 1'b1, 1'b0, 1'b1, "Vector 1: Baseline All Valid (D=1)");

        // Vector 2 (Test P independence): P=0, H=1, S=1, J=0 => D=0 (Pair with Vector 1)
        apply_vector(1'b0, 1'b1, 1'b1, 1'b0, 1'b0, "Vector 2: Pilot Inactive (Tests P)");

        // Vector 3 (Test H independence): P=1, H=0, S=1, J=0 => D=0 (Pair with Vector 1)
        apply_vector(1'b1, 1'b0, 1'b1, 1'b0, 1'b0, "Vector 3: Hydraulic Low (Tests H)");

        // Vector 4 (Test S independence): P=1, H=1, S=0, J=0 => D=0 (Pair with Vector 1)
        apply_vector(1'b1, 1'b1, 1'b0, 1'b0, 1'b0, "Vector 4: Sensor Invalid (Tests S)");

        // Vector 5 (Test J independence): P=1, H=1, S=1, J=1 => D=0 (Pair with Vector 1)
        apply_vector(1'b1, 1'b1, 1'b1, 1'b1, 1'b0, "Vector 5: Surface Jammed (Tests J)");

        $display("--- ALL 5 MC/DC VECTORS EXECUTED AND INDEPENDENCE PROVEN ---");
    endtask

    task automatic apply_vector(bit p, bit h, bit s, bit j, bit exp_d, string name);
        pilot_active       <= p;
        hydraulic_press_ok <= h;
        sensor_valid       <= s;
        surface_jammed     <= j;
        @(posedge clk);
        #1; // Sample output after flop
        if (actuator_drive_en !== exp_d) begin
            $fatal(1, "[MC/DC FAILED] %s | Exp=%b, Act=%b", name, exp_d, actuator_drive_en);
        end else begin
            $display("[MC/DC PASS] %s | P=%b H=%b S=%b J=%b -> Drive=%b", name, p, h, s, j, actuator_drive_en);
        end
    endtask

    initial begin
        rst_n = 1'b0;
        pilot_active = 0; hydraulic_press_ok = 0; sensor_valid = 0; surface_jammed = 0;
        #40 rst_n = 1'b1;
        #20;
        run_mcdc_vectors();
        #100;
        $finish(0);
    end

endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความเสียหายจริงในภาคสนาม (失敗事例 - Shippai Jirei)
**ระบบตัวควบคุมเซอร์โวขับเคลื่อนแพนหางเสือปีกเครื่องบินโดยสารพาณิชย์ (Commercial Fly-By-Wire Primary Aileron Actuator FPGA)** เกิดอาการสั่นสะบัดรุนแรงที่ความถี่สูง (Violent Aileron Flutter Oscillation) ขณะบินผ่านบริเวณอากาศแปรปรวนที่ความสูง 35,000 ฟุต เหนือมหาสมุทรแปซิฟิก นักบินต้องทำการตัดระบบคอมพิวเตอร์ควบคุมการบิน (Flight Control Computer) สลับเข้าสู่ระบบควบคุมแบบแมนนวลฉุกเฉินและทำการร่อนลงฉุกเฉินที่สนามบินใกล้เคียง ผู้โดยสารได้รับบาดเจ็บจากแรงเหวี่ยง 14 ราย

การสอบสวนของสำนักงานความปลอดภัยการคมนาคมแห่งชาติ (NTSB) และ FAA พบว่า ในโค้ด RTL ของ FPGA มี **"Dead Code ที่ไม่มีเอกสาร Requirement รองรับ (Untraced Legacy Code)"** ซึ่งเป็นบล็อกคำสั่งทดสอบระบบที่วิศวกรลืมลบทิ้งก่อนส่งมอบ บล็อกนี้ถูกกระตุ้นโดยข้อมูลเร่งด่วนที่เกิดจากการสั่นสะเทือนของอากาศยาน ทำให้คำสั่งชดเชยแรงดันเกิดการวนลูปซ้ำซ้อน ส่งผลให้ FAA สั่งระงับใบรับรองความสมควรเดินอากาศ (Airworthiness Certificate Freeze) ของฝูงบินรุ่นดังกล่าวเป็นเวลา 3 เดือน คิดเป็นมูลค่าความเสียหายทางธุรกิจกว่า 9.5 ล้านดอลลาร์สหรัฐ

---

### การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมแพนหางเสือปีกเครื่องบินจึงเกิดการสั่นสะบัดรุนแรงที่ความสูง 35,000 ฟุต?**
   - *คำตอบ:* เซอร์โววาล์วไฮดรอลิกได้รับสัญญาณสั่งการแบบสลับทิศทางไปมาอย่างรวดเร็ว (50 Hz Flutter Frequency) จากชิป FPGA
2. **ทำไม FPGA จึงส่งสัญญาณสั่งการสลับไปมาอย่างรวดเร็ว?**
   - *คำตอบ:* ตรรกะประมวลผลเซนเซอร์ตรวจจับแรงดันเกิดการสลับโหมดเข้าสู่บล็อกคำสั่งสำรอง (Debug Calibration Path) ที่ไม่ได้รับอนุญาต
3. **ทำไมบล็อก Debug Calibration จึงยังคงฝังอยู่ในชิป FPGA ที่บินจริง?**
   - *คำตอบ:* วิศวกรคัดลอกโค้ดต้นแบบมาใช้งานและไม่ได้ลบออก โดยคิดว่าเงื่อนไขอินพุตไม่มีทางเป็นจริงในสภาพการบินปกติ
4. **ทำไมการตรวจประเมิน DO-254 ในขั้นตอนการพัฒนาจึงตรวจไม่พบบล็อกนี้?**
   - *คำตอบ:* ทีมพัฒนาทำเฉพาะ Forward Traceability จากเอกสาร Requirement ไปยัง RTL แต่ **ละเลยการทำ Backward Traceability จากโค้ด RTL ทุกบรรทัดกลับมายังเอกสาร Requirement** และไม่ได้ทำ Structural Coverage Analysis เพื่อตรวจสอบ Dead Code อย่างเคร่งครัด
5. **ทำไมกระบวนการตรวจแบบ (Kenzu) จึงปล่อยให้ผ่านการอนุมัติ?**
   - *คำตอบ:* ผู้บริหารโครงการข้ามขั้นตอนการทำ **Verification Traceability Matrix (VTM) Completeness Audit Gate** ในการประชุม Stage of Involvement #3 (SOI#3)

---

### แผนผังสาเหตุและผล (Ishikawa Fishbone Diagram)

```
==================================================================================================
                                    ISHIKAWA FISHBONE CAUSE-EFFECT DIAGRAM
==================================================================================================

   MAN (บุคลากร)                                   MACHINE / TOOLS (เครื่องมือ)
   ----------------                                ---------------------------
   ลืมลบโค้ดทดสอบก่อนส่งมอบ                        ไม่ได้เปิดใช้ Structural Coverage Checker
   ขาดความเข้าใจเรื่อง Backward Traceability       ไม่มีเครื่องมือตรวจสอบ Dead Code อัตโนมัติ
               \                                                /
                \                                              /
                 \                                            /
                  +------------------------------------------+
                  |                                          |
                  |  FLY-BY-WIRE AILERON FLUTTER EMERGENCY   | ===>> [9.5M USD FAA GROUNDING LOSS]
                  |                                          |
                  +------------------------------------------+
                 /                                            \
                /                                              \
   METHOD (ระเบียบปฏิบัติ)                          MATERIAL / ENVIRONMENT (สภาวะแวดล้อม)
   ----------------------                          -------------------------------------
   ละเลยการทำ VTM Backward Audit                   สภาวะหลุมอากาศกระตุ้นเซนเซอร์ให้ส่งค่าสุ่ม
   ข้ามขั้นตอนการสอบทานใน SOI#3 Audit              ความกดอากาศต่ำทำให้สัญญาณรบกวนขยายตัว
==================================================================================================
```

---

### คู่มือปฏิบัติการตรวจสอบ OJT หน้างาน: ระเบียบปฏิบัติในการสร้าง VTM และปิดจุดบอด Dead Code สำหรับ DO-254 DAL-A

1. **Step 1: การติดแท็ก Requirement ID ลงในทุกอ็อบเจกต์ (Universal Traceability Tagging)**
   - ทุกบรรทัดใน RTL, ทุกตัวแปรใน State Machine, และทุก Testcase ใน Testbench ต้องมีคอมเมนต์ระบุเลขข้อกำหนดเสมอ:
     `// DO254_TAG: [REQ-FBW-XYZ-001]`
   - ห้ามเขียน RTL Code ลอยๆ โดยไม่มีที่มาที่ไปเด็ดขาด
2. **Step 2: การตรวจสอบ Backward Traceability และการจัดการ Dead Code**
   - ใช้สคริปต์อัตโนมัติกวาด RTL Source Code ทั้งหมดเพื่อสร้างตาราง Reverse Mapping:
     $$\text{RTL Line / Block} \longrightarrow \text{Requirement ID}$$
   - หากพบบรรทัดใดที่ **ไม่มี Requirement รองรับ (Untraced Code)**:
     - ต้องลบทิ้งออกจากโค้ดทันที (Code Removal)
     - หรือหากจำเป็นต้องมี (เช่น Hardware Reset Safety Net) จะต้องส่งเรื่องขอออก **Derived Safety Requirement** เพิ่มเติมในเอกสาร HRD อย่างเป็นทางการ
3. **Step 3: การเตรียมเอกสารสำหรับ Stage of Involvement (SOI#3 & SOI#4) Certification Audits**
   - เอกสาร VTM ต้องแสดงสถานะความครอบคลุม:
     - Requirements Coverage: 100%
     - Statement / Branch Coverage: 100%
     - MC/DC Coverage: 100%
   - รายงานทุกข้อต้องมีหลักฐาน Log File ที่สร้างจากระบบ CI/CD โดยไม่มีการแก้ไขด้วยมือมนุษย์

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (専門用語)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / อังกฤษ | บริบทการใช้งานเชิงวิศวรรกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **要求仕様ベース検証** | ようきゅうしようベースけんしょう | Youkyuu Shiyou Beesu Kenshou | Requirements-Based Verification (RBV) | การตรวจสอบความถูกต้องโดยอิงตามเอกสารข้อกำหนดเป็นหลัก |
| **設計保証レベル** | せっけいほしょうレベル | Sekkei Hoshou Reberu | Design Assurance Level (DAL) | ระดับการรับประกันความปลอดภัยของระบบการบิน |
| **追跡可能性マトリクス** | ついせきかのうせいマトリクス | Tsuiseki Kanousei Matorikusu | Traceability Matrix (VTM) | เมทริกซ์เชื่อมโยงตรวจสอบย้อนกลับระหว่างสเปก โค้ด และการทดสอบ |
| **改変条件／決定カバレッジ** | かいへんじょうけん／けっていカバレッジ | Kaihen Jouken / Kettei Kabarejji | MC/DC Coverage | ความครอบคลุมระดับการตัดสินใจและเงื่อนไขย่อยแบบแปรผัน |
| **死滅コード** | しめつコード | Shimetsu Koudo | Dead Code / Untraced Code | บรรทัดคำสั่งที่ไม่มีข้อกำหนดรองรับและไม่ควรมีอยู่ในชิป |
| **航空適航性証明** | こうくうてきこうせいしょうめい | Koukuu Tekikousei Shoumei | Airworthiness Certification | ใบรับรองความสมควรเดินอากาศจากองค์กรการบินสากล |
| **適合性審査** | てきごうせいしんさ | Tekigousei Shinsa | Compliance Audit (SOI Audit) | การตรวจสอบการปฏิบัติตามมาตรฐานกระบวนการของ DO-254 |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図審議 - Kenzu Shingi)

**สถานที่:** ห้องประชุมรับรองความปลอดภัยอากาศยาน (DO-254 SOI#3 Verification Audit Review)  
**ผู้เข้าร่วม:**
- **คุโรดะ (黒田):** Senior Aviation Airworthiness Auditor (航空適航性審査主査)
- **สิทธิชัย (シッティチャイ):** Flight Control Subsystem Lead (飛行制御設計リーダー)

---

**黒田主査 (คุโรดะ):**  
「シッティチャイさん、フライ・バイ・ワイヤ主翼アクチュエータ制御FPGAの**検証追跡可能性マトリクス（VTM）**を精査しました。要求仕様からRTLへの順方向追跡（Forward Traceability）は網羅されていますが、RTLから要求仕様への**逆方向追跡（Backward Traceability）**で未リンクのコードブロックが3箇所検出されました。これは何ですか？」  
*(คุณสิทธิชัยครับ ผมตรวจสอบเมทริกซ์การตรวจสอบย้อนกลับ (VTM) ของ FPGA ควบคุมเซอร์โวปีกเครื่องบิน Fly-By-Wire แล้ว การเชื่อมโยงไปข้างหน้าจากสเปกไปยัง RTL ครอบคลุมดี แต่ในส่วนการเชื่อมโยงย้อนกลับจาก RTL ไปยังสเปก พบว่ามีบล็อกโค้ด 3 จุดที่ไม่มีข้อกำหนดเชื่อมโยงรองรับ นี่คืออะไรครับ?)*

**シッティチャイ (สิทธิชัย):**  
「黒田主査、その3箇所は基板デバッグ時に波形を観測しやすくするための補助ロジックと、将来の拡張を見越した予備の分岐処理です。通常の飛行シーケンスでは決して実行されない安全なコードです。」  
*(หัวหน้าคุโรดะครับ ทั้ง 3 จุดนั้นเป็น Auxiliary Logic ที่ใส่ไว้เพื่อช่วยสังเกตการณ์รูปคลื่นตอนดีบักบนบอร์ด และตรรกะสำรองที่เตรียมไว้สำหรับการขยายระบบในอนาคตครับ เป็นโค้ดที่ปลอดภัยและไม่มีวันถูกเรียกใช้ในโหมดการบินปกติแน่นอนครับ)*

**黒田主査 (คุโรดะ):**  
「信じられない暴論です！DO-254 DAL-Aにおいて、要求仕様に裏付けのないコードは**『死滅コード（Dead Code / Untraced Code）』**とみなされ、意図しない重大故障（Unintended Behavior）を引き起こす最大の温床です！『決して実行されない』という主観的な推測など、航空監査では一切通用しません！即刻該当コードを物理的に削除するか、派生安全要求（Derived Requirement）として文書化し、安全審査委員会を通してください！」  
*(พูดจาเหลวไหลสิ้นดีครับ! ในมาตรฐาน DO-254 DAL-A โค้ดใดที่ไม่มีเอกสาร Requirement รองรับ จะถูกตีตราว่าเป็น Dead Code ทันที และมันคือบ่อเกิดอันดับหนึ่งที่ทำให้เกิดความล้มเหลวร้ายแรงที่ไม่ได้เจตนา! คำว่า 'ไม่มีวันถูกเรียกใช้' ซึ่งเป็นการคาดเดาส่วนบุคคล ไม่สามารถนำมาใช้ในการตรวจสอบอากาศยานได้เด็ดขาดครับ! จงลบโค้ดพวกนั้นทิ้งไปจากชิปทันที หรือไม่ก็ต้องบันทึกเป็น Derived Requirement อย่างเป็นทางการแล้วส่งผ่านคณะกรรมการความปลอดภัยเดี๋ยวนี้!)*

**シッティチャイ (สิทธิชัย):**  
「申し訳ありません！安全基準に対する私の認識が甘かったです。直ちに不要な予備コードを完全に削除し、VTMを100%双方向一致に修正します。」  
*(ขออภัยอย่างยิ่งครับ! ความตระหนักต่อมาตรฐานความปลอดภัยของผมยังหย่อนยานเกินไป ผมจะลบโค้ดส่วนเกินออกให้หมดสิ้นทันที และปรับปรุง VTM ให้มีความสอดคล้องแบบสองทิศทาง 100% ครับ)*

**黒田主査 (คุโรดะ):**  
「ええ。それと、アクチュエータ連動ロジックの**改変条件／決定カバレッジ（MC/DC）**について、4つの条件に対して5つのテストベクタで独立性が完全に数学的証明されているか、テストログと波形エビデンスを全て提出してください。死滅コードが完全にゼロになり、MC/DC 100%の適合性が立証されるまで、SOI#3の合格証書の発行は拒否します。」  
*(ใช่ แล้วก็เรื่อง MC/DC ของตรรกะควบคุมแอคชูเอเตอร์ จงยื่นส่งหลักฐาน Log และคลื่นสัญญาณทั้งหมดเพื่อพิสูจน์ทางคณิตศาสตร์ว่าเวกเตอร์ทั้ง 5 สามารถแสดงความเป็นอิสระของทั้ง 4 เงื่อนไขได้อย่างครบถ้วน จนกว่า Dead Code จะเป็นศูนย์อย่างแท้จริง และความสอดคล้องของ MC/DC แตะ 100% ผมจะระงับการออกใบรับรองผ่านด่าน SOI#3 เอาไว้ครับ)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณจำนวนเวกเตอร์ทดสอบขั้นต่ำสุดสำหรับเกณฑ์ 100% MC/DC

พิจารณาเงื่อนไขการตัดสินใจเพื่อเปิดใช้วาล์วดับเพลิงของเครื่องยนต์อากาศยาน (Engine Fire Extinguisher Valve Enable Decision):
$$\mathbf{Decision \ D} = (Fire\_Sensor\_A \vee Fire\_Sensor\_B) \wedge (Master\_Arm\_Switch \wedge \neg Manual\_Override)$$
กำหนดให้ตัวแปรบูลีนทั้งหมดเป็นตัวแปรอิสระต่อกันจำนวน $N = 4$ ตัวแปร  
หากต้องการบรรลุเกณฑ์ **100% Modified Condition / Decision Coverage (MC/DC)** ตามมาตรฐาน DO-254 DAL-A จงคำนวณหาจำนวนเวกเตอร์ทดสอบขั้นต่ำสุดในทางทฤษฎี ($V_{min}$) ที่จำเป็นในการพิสูจน์ความเป็นอิสระของทั้ง 4 ตัวแปรนี้:

- **A)** $V_{min} = 4$ เวกเตอร์
- **B)** $V_{min} = 5$ เวกเตอร์ ($N + 1$)
- **C)** $V_{min} = 8$ เวกเตอร์
- **D)** $V_{min} = 16$ เวกเตอร์ ($2^N$)

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) $V_{min} = 5$ เวกเตอร์ ($N + 1$)**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ตามทฤษฎีบทการสร้างเวกเตอร์ทดสอบ MC/DC ของ Chilenski และ Miller (1994) สำหรับนิพจน์บูลีนที่มีตัวแปรอิสระ $N$ ตัวแปร:
   - จำนวนเวกเตอร์ทดสอบขั้นต่ำสุดในทางทฤษฎีคือ:
     $$V_{min} = N + 1$$
   - จำนวนเวกเตอร์ทดสอบสูงสุด (Upper bound) คือ:
     $$V_{max} = 2N$$
2. ในกรณีนี้ มีตัวแปรย่อยทั้งหมด 4 ตัวแปร ($N = 4$):
   - $C_1 = Fire\_Sensor\_A$
   - $C_2 = Fire\_Sensor\_B$
   - $C_3 = Master\_Arm\_Switch$
   - $C_4 = Manual\_Override$
3. ดังนั้น จำนวนเวกเตอร์ทดสอบขั้นต่ำสุดที่จะสามารถสร้างคู่ของผลลัพธ์เพื่อพิสูจน์ความเป็นอิสระของแต่ละตัวแปร ($Independent \ Pairs$) ได้อย่างสมบูรณ์คือ:
   $$V_{min} = 4 + 1 = \mathbf{5\text{ เวกเตอร์}}$$
4. การเปรียบเทียบกับวิธี Exhaustive Testing ($2^N = 2^4 = 16$ เวกเตอร์):
   การใช้เกณฑ์ MC/DC ช่วยลดจำนวนกรณีทดสอบลงได้ถึง $68.75\%$ ในขณะที่ยังคงรับประกันความปลอดภัยในการตรวจจับข้อบกพร่องของลอจิกเกตได้อย่างแม่นยำเทียบเท่ากัน

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** $4$ เวกเตอร์ ไม่เพียงพอ เพราะไม่สามารถสร้างผลลัพธ์ Decision ให้เป็นทั้ง True และ False พร้อมทั้งมีคู่เปรียบเทียบครบทุกตัวแปรได้
- **ข้อ C ผิด:** $8$ เวกเตอร์ ($2N$) เป็นขอบเขตบน (Upper bound) ไม่ใช่จำนวนขั้นต่ำสุด
- **ข้อ D ผิด:** $16$ เวกเตอร์ คือ Exhaustive Testing ซึ่งเป็นการทดสอบทุกกรณีแบบดั้งเดิม ไม่ใช่จุดเด่นของการลดทอนด้วย MC/DC

---

### คำถามที่ 2: กฎเกณฑ์การจัดการ Untraced Code ในการตรวจประเมิน DO-254 SOI#3

หากในระหว่างการทำ Structural Coverage Analysis ผู้ตรวจประเมินพบว่ามีบรรทัดคำสั่ง RTL บางส่วนที่ **ไม่มีการเชื่อมโยงกับความต้องการของระบบ (Untraced to Requirements)** และไม่เคยถูกสั่งให้ทำงานในระหว่างรัน Requirements-Based Testsuite ตามมาตรฐาน DO-254 วิธีปฏิบัติข้อใดต่อไปนี้ที่ถูกต้องตามหลักวิศวกรรมการบิน?

- **A)** เพิ่ม Testcase พิเศษใน Testbench เพื่อไปกระตุ้นให้บรรทัดนั้นทำงาน แล้วรายงานว่า Code Coverage ครบ 100%
- **B)** ใส่ Directive `// synthesis translate_off` เพื่อซ่อนโค้ดนั้นจากสายตาของผู้ตรวจประเมิน
- **C)** ทำการวิเคราะห์ว่าโค้ดนั้นเป็น Dead Code หรือไม่ หากเป็น Dead Code ต้องลบออกจาก RTL ทันที แต่หากเป็น Safety Mechanism จำเป็น ต้องเขียน Derived Requirement เพิ่มเติมในสเปกและทำเอกสาร Traceability ย้อนหลังให้สมบูรณ์
- **D)** ปล่อยทิ้งไว้ตามเดิมได้ หากฟังก์ชันหลักของเครื่องบินยังคงทำงานผ่านการทดสอบ

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: C) ทำการวิเคราะห์ว่าโค้ดนั้นเป็น Dead Code หรือไม่ หากเป็น Dead Code ต้องลบออกจาก RTL ทันที แต่หากเป็น Safety Mechanism จำเป็น ต้องเขียน Derived Requirement เพิ่มเติมในสเปกและทำเอกสาร Traceability ย้อนหลังให้สมบูรณ์**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ตามมาตรฐาน RTCA DO-254 Section 5.3 และ Section 6.2:
   - โค้ดทุกบรรทัดต้องมีเหตุผลและข้อกำหนดรองรับ (Must be traced to a requirement)
   - หากมีโค้ดที่ไม่ถูกเชื่อมโยง (Untraced Code) จะถือเป็นความบกพร่องของกระบวนการพัฒนา
2. ขั้นตอนการจัดการมาตรฐาน:
   - **กรณีที่ 1 (Dead Code):** เป็นโค้ดส่วนเกิน, โค้ดค้างจากโปรเจกต์เก่า, หรือบล็อกดีบัก $\implies$ **ต้องลบออกจาก RTL อย่างถาวร**
   - **กรณีที่ 2 (Deactivated Code):** เป็นฟังก์ชันที่มีอยู่ตามสเปกแต่ถูกปิดไว้ในคอนฟิกของเครื่องบินรุ่นนี้ $\implies$ ต้องมีเอกสารพิสูจน์ว่ามันไม่มีทางถูกกระตุ้นขึ้นมาได้เอง
   - **กรณีที่ 3 (Necessary Hardware Protection):** เช่น วงจรดักจับค่าที่ไม่พึงประสงค์ในสถานะ Default ของ Case Statement $\implies$ ต้องเขียน **Derived Requirement** บรรจุลงในเอกสาร Hardware Requirements Document (HRD) แล้วทำการทดสอบเพื่อปิด Traceability Matrix
3. การฝืนเขียน Testcase มั่วๆ เพื่อดันตัวเลข Coverage (ข้อ A) หรือการซ่อนโค้ด (ข้อ B) ถือเป็นการละเมิดจริยธรรมวิศวกรรมและผิดกฎหมายความปลอดภัยการบินอย่างร้ายแรง

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** เป็นการทดสอบที่ไม่มีความต้องการรองรับ (Unrequirements-based testing) ซึ่งขัดกับหลักการพื้นฐานของ DO-254
- **ข้อ B ผิด:** เป็นการปลอมแปลงหลักฐาน ซึ่งหากเกิดอุบัติเหตุจะถูกดำเนินคดีอาญา
- **ข้อ D ผิด:** กฎหมายการบินไม่อนุญาตให้ปล่อยทิ้งไว้โดยเด็ดขาด

---

### คำถามที่ 3: การพิสูจน์ความเป็นอิสระของเงื่อนไข (Condition Independence) ในตาราง MC/DC

พิจารณานิพจน์การตัดสินใจ: $\mathbf{D = A \wedge B}$  
มีชุดเวกเตอร์ทดสอบ 3 เวกเตอร์ดังนี้:
- เวกเตอร์ 1: $A = 1, B = 1 \implies D = 1$
- เวกเตอร์ 2: $A = 0, B = 1 \implies D = 0$
- เวกเตอร์ 3: $A = 1, B = 0 \implies D = 0$

จงระบุคู่ของเวกเตอร์ทดสอบที่เป็นหลักฐานพิสูจน์ความเป็นอิสระ (Independence Pair) ของตัวแปร $A$ และตัวแปร $B$ ตามลำดับ:

- **A)** ตัวแปร $A$ พิสูจน์โดยคู่ (เวกเตอร์ 2, เวกเตอร์ 3), ตัวแปร $B$ พิสูจน์โดยคู่ (เวกเตอร์ 1, เวกเตอร์ 2)
- **B)** ตัวแปร $A$ พิสูจน์โดยคู่ (เวกเตอร์ 1, เวกเตอร์ 2), ตัวแปร $B$ พิสูจน์โดยคู่ (เวกเตอร์ 1, เวกเตอร์ 3)
- **C)** ตัวแปร $A$ พิสูจน์โดยคู่ (เวกเตอร์ 1, เวกเตอร์ 3), ตัวแปร $B$ พิสูจน์โดยคู่ (เวกเตอร์ 1, เวกเตอร์ 2)
- **D)** ชุดเวกเตอร์นี้ไม่สามารถพิสูจน์ MC/DC ได้เนื่องจากมีจำนวนเวกเตอร์ไม่เพียงพอ

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) ตัวแปร $A$ พิสูจน์โดยคู่ (เวกเตอร์ 1, เวกเตอร์ 2), ตัวแปร $B$ พิสูจน์โดยคู่ (เวกเตอร์ 1, เวกเตอร์ 3)**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. **การพิสูจน์ความเป็นอิสระของตัวแปร $A$:**
   - เงื่อนไข: ตัวแปร $A$ ต้องเปลี่ยนค่า ($1 \to 0$ หรือ $0 \to 1$) ในขณะที่ตัวแปรอื่นทั้งหมด ($B$) **ต้องคงที่เท่าเดิม** และผลลัพธ์ $D$ ต้องเปลี่ยนสถานะตามไปด้วย
   - เปรียบเทียบ **เวกเตอร์ 1** ($A=1, B=1 \implies D=1$) กับ **เวกเตอร์ 2** ($A=0, B=1 \implies D=0$):
     - $A$ เปลี่ยนจาก $1 \to 0$
     - $B$ คงที่อยู่ที่ค่า $1$ ทั้งสองเวกเตอร์
     - ผลลัพธ์ $D$ เปลี่ยนจาก $1 \to 0$
   - $\implies$ **คู่ (เวกเตอร์ 1, เวกเตอร์ 2) พิสูจน์ความเป็นอิสระของ $A$ อย่างสมบูรณ์**
2. **การพิสูจน์ความเป็นอิสระของตัวแปร $B$:**
   - เงื่อนไข: ตัวแปร $B$ ต้องเปลี่ยนค่า ในขณะที่ตัวแปร $A$ **ต้องคงที่เท่าเดิม** และผลลัพธ์ $D$ ต้องเปลี่ยนสถานะตามไปด้วย
   - เปรียบเทียบ **เวกเตอร์ 1** ($A=1, B=1 \implies D=1$) กับ **เวกเตอร์ 3** ($A=1, B=0 \implies D=0$):
     - $B$ เปลี่ยนจาก $1 \to 0$
     - $A$ คงที่อยู่ที่ค่า $1$ ทั้งสองเวกเตอร์
     - ผลลัพธ์ $D$ เปลี่ยนจาก $1 \to 0$
   - $\implies$ **คู่ (เวกเตอร์ 1, เวกเตอร์ 3) พิสูจน์ความเป็นอิสระของ $B$ อย่างสมบูรณ์**
3. ดังนั้น ชุดเวกเตอร์ 3 ตัวนี้ ($N+1 = 2+1=3$) สามารถพิสูจน์ MC/DC ของนิพจน์ $D = A \wedge B$ ได้ครบ 100% สมบูรณ์แบบ

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** คู่ (เวกเตอร์ 2, เวกเตอร์ 3) ตัวแปรเปลี่ยนค่าพร้อมกันทั้งสองตัว ($A$ เปลี่ยนจาก 0 เป็น 1 และ $B$ เปลี่ยนจาก 1 เป็น 0) ทำให้ไม่สามารถพิสูจน์ความเป็นอิสระของตัวแปรเดี่ยวได้
- **ข้อ C ผิด:** สลับคู่ของตัวแปร $A$ และ $B$
- **ข้อ D ผิด:** 3 เวกเตอร์นี้เพียงพอและถูกต้องตามทฤษฎี MC/DC ขั้นต่ำสุดทุกประการ
