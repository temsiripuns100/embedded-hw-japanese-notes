# Lesson 178: FPGA CDC Part 8 - Static CDC Verification Tools & Methodology (SpyGlass CDC, Questa CDC, Vivado report_cdc, Structural vs Functional Checks & Zero-Waiver Audit SOP)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์การตรวจสอบ CDC: ทำไม Simulation และ STA จึงตาบอดต่อข้อผิดพลาด?
ในกระบวนการออกแบบวงจรดิจิทัลมาตรฐาน วิศวกรส่วนใหญ่พึ่งพาเครื่องมือ 2 ชนิดในการตรวจสอบความถูกต้องของวงจร:
1. **RTL Dynamic Simulation (ModelSim, VCS, Xcelium):** เพื่อตรวจสอบฟังก์ชันการทำงานเชิงลอจิก
2. **Static Timing Analysis (STA / Vivado Timing Engine):** เพื่อตรวจสอบความเร็วและ Timing Closure

ทว่า สำหรับบั๊กที่เกิดจากการข้ามโดเมนสัญญาณนาฬิกา (Clock Domain Crossing - CDC) **เครื่องมือทั้งสองกลับกลายเป็น "คนตาบอด" อย่างสิ้นเชิง!**

```
            กับดักความล้มเหลวของ SIMULATION และ STA ต่อปัญหา CDC
            
    [ 1. RTL DYNAMIC SIMULATION ]               [ 2. STATIC TIMING ANALYSIS (STA) ]
    
    * สมมติฐาน: Zero-Delay หรือ Fixed Delay     * หน้าที่: ตรวจ Setup/Hold ในโดเมนเดียวกัน
    * ไม่สามารถจำลอง Metastability ได้          * เมื่อเจอ Asynchronous Clocks:
    * นาฬิกา 2 ตัวมีเฟสที่คำนวณแบบ Synchronous  * วิศวกรใส่ `set_clock_groups -asynchronous`
    * สัญญาณเปลี่ยนสถานะพร้อมกันทุกบิต          * ผลลัพธ์: STA "ปิดการตรวจเช็คทิ้ง 100%!"
    ===> โอกาสเจอ CDC Bug ต่ำกว่า 10^-8!         ===> ปิดตาไม่รับรู้ ไม่แจ้งเตือนใดๆ!
```

#### ทำไม Dynamic Simulation จึงตรวจไม่พบ CDC Bug?
* ในตัวจำลองระดับ RTL สัญญาณนาฬิกาทั้งหมดจะถูกสร้างขึ้นจากตัวคูณเวลาทางคณิตศาสตร์ใน Testbench ทำให้ความสัมพันธ์ของขอบสัญญาณนาฬิกาเป็นแบบคงที่แน่นอน (Deterministic Phase Relationship)
* ฟิสิกส์ของการเกิด Metastability และการคลายตัวแบบสุ่ม (Non-deterministic Resolution) ไม่สามารถถูกจำลองได้ในลอจิกแบบ $0, 1, X, Z$ ธรรมดา
* หากความกว้างของหน้าต่างเวลา Metastability คือ $T_w = 0.1\text{ ns}$ ในรอบสัญญาณนาฬิกา $T = 10\text{ ns}$ โอกาสที่ขอบสัญญาณใน Simulation จะตกลงตรงหน้าต่างพอดีมีน้อยมาก และต่อให้ตกลง Simulator ก็จะตัดสินใจเลือกค่า $0$ หรือ $1$ ค่าใดค่าหนึ่งตามอัลกอริทึมของโปรแกรมเสมอ ทำให้บั๊กแอบซ่อนอยู่ได้นานหลายเดือน!

---

### 1.2 สถาปัตยกรรมของ Static CDC Verification Engines

เพื่อขจัดช่องโหว่นี้ อุตสาหกรรมเซมิคอนดักเตอร์และระบบฝังตัวระดับสากลจึงต้องพึ่งพา **เครื่องมือวิเคราะห์ CDC เชิงสถิตแบบจำเพาะ (Static CDC Verification Tools)** เช่น **Synopsys SpyGlass CDC**, **Siemens Questa CDC**, และ **AMD Vivado `report_cdc`**:

```
               สถาปัตยกรรมระดับเครื่องมือของ STATIC CDC VERIFICATION
               
                      ┌─────────────────────────────────┐
                      │    RTL Source + SDC/XDC Files   │
                      └────────────────┬────────────────┘
                                       │
                                       ▼
                       [ CLOCK & RESET TREE INFERENCE ]
                       * สกัดโดเมนสัญญาณนาฬิกาทั้งหมด
                       * จัดกลุ่ม Asynchronous Clocks อัตโนมัติ
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
      [ STRUCTURAL CDC ANALYSIS ]            [ FUNCTIONAL CDC ANALYSIS ]
      (โครงสร้างฮาร์ดแวร์ & โทโพโลยี)         (พฤติกรรมโปรโตคอล & สถานะ)
      * ตรวจจับเส้นทางไม่มีตัว Sync           * ตรวจสอบ Data Stability Window
      * ตรวจจับ Bit-by-Bit บน Multi-bit      * ตรวจสอบ Handshake Protocol FSM
      * ตรวจจับ Reconvergence Hazards        * ตรวจสอบ Gray Code Sequential Order
      * ตรวจสอบ ASYNC_REG Attributes         * ตรวจสอบ FIFO Full/Empty Overflow
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                      ┌─────────────────────────────────┐
                      │    DETAILED CDC VIOLATION REPORT│
                      │  (Critical, Warning, Info, N/A) │
                      └─────────────────────────────────┘
```

#### การแบ่งประเภทการตรวจสอบ CDC เป็น 2 มิติหลัก:
1. **Structural CDC Analysis (การตรวจสอบทางโครงสร้างกายภาพ):**
   * ตรวจสอบความถูกต้องของการเชื่อมต่อระหว่าง Register ต้นทางและ Register ปลายทาง
   * ค้นหาเส้นทางที่ไม่มีวงจร Synchronizer รองรับ (Unsynchronized Crossings)
   * ตรวจสอบว่ามีลอจิก Combinational Gate ขวางกั้นอยู่หน้าขาตัว Synchronizer หรือไม่ (Glitch Hazard on Sync Input)
   * ตรวจสอบว่ามีแอตทริบิวต์ `(* ASYNC_REG = "TRUE" *)` บนฟลิปฟล็อปครบถ้วนหรือไม่
2. **Functional CDC Analysis (การตรวจสอบเชิงพฤติกรรมและโปรโตคอล):**
   * ใช้เทคนิค **Formal Model Checking** วิเคราะห์สถานะทางตรรกะว่ามีความเป็นไปได้ที่จะเกิดการละเมิดโปรโตคอลหรือไม่
   * พิสูจน์ว่าข้อมูลใน DMUX มีความเสถียร (Data Held Constant) ตลอดช่วงเวลาที่สัญญาณ Enable ข้ามโดเมนจริงหรือไม่
   * ตรวจสอบว่าพอยน์เตอร์ใน Asynchronous FIFO มีบิตเปลี่ยนมากกว่า 1 บิตในไซเคิลใดๆ หรือไม่ (Hamming Distance Proof)

---

### 1.3 กฎเกณฑ์สำคัญในเครื่องมือระดับอุตสาหกรรม (Industry Rule Standards)

#### กฎหลักของ AMD Vivado `report_cdc`:

| รหัสข้อผิดพลาด | ระดับความรุนแรง | ความหมายทางวิศวกรรม | พฤติกรรมความล้มเหลวหากไม่แก้ไข |
|:---|:---:|:---|:---|
| **CDC-1** | **Critical** | **Unsynchronized Path:** เส้นทางข้ามโดเมนนาฬิกาโดยไม่มี Synchronizer ใดๆ ขวางกั้นเลย | สัญญาณปลายทางเกิด Metastability อย่างต่อเนื่อง ระบบค้างหรือทำงานผิดพลาด |
| **CDC-2** | Warning | **Missing ASYNC_REG:** สัญญาณ 1 บิตมี 2-FF Sync แต่ฟลิปฟล็อปไม่ติดแอตทริบิวต์ `ASYNC_REG` | Placer จะวางฟลิปฟล็อปทั้งสองอยู่คนละ Slice ทำให้ MTBF ต่ำลงอย่างมาก |
| **CDC-6** | **Critical** | **Multi-bit Unsafe Crossing:** บัสข้อมูลหลายบิตใช้ 2-FF ขนานกันแบบ Bit-by-Bit | เกิด Bus Skew ทำให้ปลายทางแซมเปิลได้ข้อมูลขยะ (Data Corruption) |
| **CDC-8** | **Critical** | **Reconvergence of Synchronized Signals:** สัญญาณซิงโครไนซ์แยกกันแล้วมารวมกัน | เกิด 1-Cycle Cycle-Skew และสร้าง Glitch ขนาด 1 ไซเคิลในลอจิกปลายทาง |
| **CDC-10** | Warning | **Mux-Data Stability Warning:** มีการใช้ DMUX แต่ไม่มี Timing Constraint คุม Bus Skew | ข้อมูลบัสอาจเปลี่ยนค่าเร็วเกินไป หรือเกิด Skew เหลื่อมล้ำจน Latch ผิดรอบ |
| **CDC-11** | Warning | **Fanout from ASYNC_REG FF:** ขาเอาต์พุตของ Synchronizer มี Fanout สูงเกิน 1 โหลด | สัญญาณ Synchronized มี Routing Skew ไปถึงปลายทางแต่ละบิตไม่พร้อมกัน |

#### การเทียบเคียงกับ Synopsys SpyGlass CDC และ Siemens Questa CDC:
* **SpyGlass `Clock_Sync01`** $\iff$ **Vivado `CDC-1` / `CDC-2`** (การตรวจสอบ Synchronizer 1 บิต)
* **SpyGlass `Data_Sync01`** $\iff$ **Vivado `CDC-6`** (การตรวจสอบการซิงโครไนซ์บัสข้อมูล)
* **SpyGlass `Clock_Reconv01`** $\iff$ **Vivado `CDC-8`** (การตรวจสอบ Reconvergence Hazards)
* **Questa `cdc_enable_data`** $\iff$ **Vivado `CDC-10`** (การตรวจสอบ DMUX Data Stability)

---

### 1.4 ปรัชญาการจัดการ Waiver (Waiver Management & Audit SOP)

ในโครงการขนาดใหญ่ที่มีสัญญาณข้ามโดเมนหลายหมื่นเส้น รายงาน CDC มักมีคำเตือนเกิดขึ้นหลายร้อยบรรทัด ความผิดพลาดที่พบได้บ่อยที่สุดในหมู่วิศวกรคือ **"การออกคำสั่งขอยกเว้น (Waiver / 適用除外) แบบครอบจักรวาล"** เพียงเพื่อให้ผลการรันผ่านเป็นสีเขียว:

```tcl
# ==============================================================================
# ANTI-PATTERN: การออก WAIVER แบบอันตรายสูงสุด (ห้ามทำเด็ดขาด!)
# ==============================================================================
# วิศวกรมักง่ายใช้ Regular Expression คลุมพาธทั้งหมดเพื่อปิดปากเครื่องมือ
set_msg_config -id {CDC-6} -suppress
set_msg_config -id {CDC-8} -suppress
# หรือใน SpyGlass:
# waive -rule {Clock_Sync01 Data_Sync01} -comment "Ignore all CDC for now"
```

> [!CAUTION]
> **กฎเหล็กการออก CDC Waiver ตามมาตรฐาน DO-254 DAL-A และ ISO 26262 ASIL-D:**
> การใส่ Waiver โดยไม่มีการพิสูจน์ทางวิศวกรรมถือเป็น **การละเมิดความปลอดภัยขั้นร้ายแรง (Gross Safety Violation)** หากเกิดอุบัติเหตุขึ้นในฮาร์ดแวร์จริง ทีมสอบสวนจะตรวจสอบไฟล์ Waiver ก่อนเป็นอันดับแรก!

#### โครงสร้างที่ถูกต้องของ CDC Waiver ที่ยอมรับได้ (Audit-Compliant Waiver Structure):
เอกสาร Waiver ทุกตัวจะต้องระบุข้อมูลครบถ้วนทั้ง 4 องค์ประกอบ:
1. **Exact P2P Path:** ระบุชื่อ Register ต้นทางและปลายทางอย่างเฉพาะเจาะจง ห้ามใช้ Wildcard (`*`) ครอบคลุมหลายโมดูล
2. **Specific Tool Rule:** ระบุรหัสกฎที่ขอยกเว้นชัดเจน (เช่น `CDC-10`)
3. **Mathematical & Architectural Justification:** ระบุเหตุผลทางวิศวกรรม เช่น: *"บัสนี้เป็น Quasi-static Configuration Register ที่เขียนครั้งเดียวตอน Bootloader เริ่มต้นระบบ และถูกตรึงค่าคงที่ตลอดระยะเวลาการทำงานของระบบ โดยมี SVA Property พิสูจน์ความเสถียรแล้ว"*
4. **Sign-off Authority Signature:** ลายเซ็นดิจิทัลของ Lead Chief Reviewer ที่รับผิดชอบ

---

### 1.5 สคริปต์อัตโนมัติ Vivado CDC สำหรับ CI/CD Automation Pipeline

```tcl
# ==============================================================================
# AUTOMATED VIVADO CDC AUDIT SCRIPT FOR CONTINUOUS INTEGRATION (CI/CD)
# File: run_cdc_audit.tcl
# ==============================================================================

open_checkpoint -quiet $env(DESIGN_DCP)

# 1. รันการวิเคราะห์ CDC ครอบคลุมทุกโดเมนนาฬิกา
set cdc_report_file "reports/cdc_audit_report.rpt"
report_cdc -details -severity {Critical Warning} -file $cdc_report_file

# 2. ตรวจสอบจำนวน Critical Warnings ของ CDC
set num_critical_cdc [get_property SEVERITY [get_msg_config -id {CDC-1}]]
set cdc_violations [get_cdc_violations -severity Critical]
set violation_count [llength $cdc_violations]

puts "========================================================================"
puts " CDC STATIC VERIFICATION AUDIT SUMMARY"
puts " Total Critical CDC Violations Detected: $violation_count"
puts "========================================================================"

# 3. บังคับให้ CI/CD Pipeline ล้มเหลวทันทีหากมีข้อผิดพลาด
if {$violation_count > 0} {
    puts "ERROR: [CDC_FATAL_GATE] Critical CDC violations detected in design!"
    foreach v $cdc_violations {
        puts " -> Violation: [get_property ID $v] on Path: [get_property SOURCE $v] --> [get_property DEST $v]"
    }
    puts "Terminating build pipeline with Exit Code 1..."
    exit 1
} else {
    puts "SUCCESS: [CDC_PASS_GATE] Design passed CDC static verification sign-off!"
    exit 0
}
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】เครื่องถอดรหัสรหัสพันธุกรรมความเร็วสูง (High-Throughput DNA Sequencer)
เกิดข้อมูลลำดับเบสผิดเพี้ยน (Corrupted Sequence Reads) ทุก 2-3 วันในโรงพยาบาล
จากบั๊ก Wildcard Waiver กวาดซ่อนข้อผิดพลาด CDC-6 กว่า 240 รายการใน CI/CD
================================================================================
```

#### บริบทของระบบ (System Context):
บริษัทเครื่องมือแพทย์ชั้นนำพัฒนาเครื่องตรวจวิเคราะห์ดีเอ็นเอรุ่นใหม่ (Next-Gen Gene Sequencer) โดยใช้ FPGA Xilinx Virtex UltraScale+ (`xcvu3p`):
* **Illumination Sensor Domain (`clk_optics`):** ความถี่ $80\text{ MHz}$ ทำหน้าที่รับข้อมูลภาพฟลูออเรสเซนต์จากเซนเซอร์ CMOS
* **Neural Basecalling Engine Domain (`clk_ai`):** ความถี่ $300\text{ MHz}$ ทำหน้าที่ประมวลผลเครือข่ายประสาทเทียมเพื่อถอดรหัสเบส A, T, C, G
* ระหว่างสองโดเมนมีการส่งพารามิเตอร์ขจัดสัญญาณรบกวน (Optical Calibration Coefficients) ขนาด $64\text{ บิต}$

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
เครื่องตรวจถูกส่งมอบให้ศูนย์การแพทย์และโรงพยาบาลมหาวิทยาลัยเพื่อใช้งานจริง หลังจากทำงานต่อเนื่องไปได้ 48 ถึง 72 ชั่วโมง เครื่องตรวจเริ่มรายงาน **ผลการถอดรหัสดีเอ็นเอผิดพลาด (Spurious Mutation Artifacts)** ทำให้แพทย์วินิจฉัยยีนก่อโรคมะเร็งคลาดเคลื่อน เมื่อนำบอร์ดมาตรวจสอบ พบว่าค่าพารามิเตอร์ Calibration ในฝั่ง AI มีการกระโดดกลายเป็นตัวเลขผิดปกติเป็นระยะๆ ส่งผลให้หน่วยงานกำกับดูแลเครื่องมือแพทย์ (FDA) สั่งระงับการใช้งานและเรียกคืนผลิตภัณฑ์เพื่อสอบสวนทันที!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมผลการถอดรหัสดีเอ็นเอจึงผิดเพี้ยน?**
   * *เพราะพารามิเตอร์ Optical Calibration 64 บิตที่ส่งเข้าโดเมน AI ถูกแซมเปิลได้ค่าระหว่างกลาง (Phantom Intermediate Values) เช่น จาก $0x0000\_FFFF$ กลายเป็น $0xFFFF\_FFFF$ ชั่วขณะ*
2. **ทำไมพารามิเตอร์จึงถูกแซมเปิลได้ค่าระหว่างกลาง?**
   * *เพราะบัสข้อมูล 64 บิต ถูกส่งข้ามโดเมนโดยใช้ 2-FF Synchronizer ต่อขนานกันแบบ Bit-by-Bit โดยไม่มีวงจร DMUX หรือ Handshake ควบคุม*
3. **ทำไมการออกแบบ Bit-by-Bit Multi-bit CDC จึงหลุดรอดเข้าสู่ชิปที่ผลิตจริง?**
   * *เพราะในขั้นตอนรันสคริปต์ตรวจสอบ CDC รายงานไม่ได้ฟ้อง Error หรือระงับการบิลด์ไฟล์บิตสตรีม*
4. **ทำไมเครื่องมือตรวจสอบ Static CDC จึงไม่ระงับการบิลด์?**
   * *เพราะวิศวกรได้เขียนไฟล์สคริปต์ `waive_cdc.tcl` โดยใส่คำสั่งกวาดล้างข้อผิดพลาดด้วยเครื่องหมายดอกจัน: `create_waiver -id CDC-6 -from * -to *` เพื่อให้ผ่านระบบ CI/CD Pipeline ทันกำหนดส่งมอบสินค้า*
5. **ทำไมวิศวกรจึงกล้าใส่คำสั่ง Blanket Waiver เช่นนั้น?**
   * *เพราะทีมพัฒนาขาดระบบ Audit Review สำหรับตรวจสอบความถูกต้องของ Waiver และไม่มีการกำหนดผู้มีอำนาจลงนามอนุมัติ (Sign-off Authority Gate) ทำให้วิศวกรใช้ Waiver เป็นทางลัดในการแก้ปัญหา Warning ที่ค้างอยู่ในระบบ!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                       สาเหตุของความล้มเหลว: DNA SEQUENCING CORRUPTION
                       
   METHOD (กระบวนการอนุมัติ Waiver)            MACHINE (เครื่องมือและ CI/CD Pipeline)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ใช้ Blanket Waiver `from * to *`│         │ Bit-by-Bit Sync บนบัส 64-bit   │
   │ ขาดระเบียบปฏิบัติ CDC Audit SOP│          │ CI/CD Pipeline ปล่อยผ่าน Waiver│
   │ ขาดการตรวจทานในห้อง Kenzu      │          │ การเกิด Bus Skew บน UltraScale+│
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ กำหนดการส่งมอบสินค้ากระชั้นชิด │          │ ไม่เคยตรวจนับจำนวน Waiver จริง │
   │ ขาดการตรวจสอบมาตรฐานเครื่องมือแพทย์│      │ ขาดการทำ Functional Assertion  │
   │ ความรู้เรื่อง CDC-6 ไม่เพียงพอ  │         │ Testbench ไม่เคยยิง Asyn Jitter│
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (วัฒนธรรมองค์กรและเวลา)             MEASUREMENT (การตรวจสอบคุณภาพ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขทางวิศวกรรม (Engineering Fixes):
1. **เพิกถอนคำสั่ง Blanket Waiver ทั้งหมดใน Git Repository:** ลบไฟล์ `waive_cdc.tcl` เดิมทิ้งทันที และรัน `report_cdc` แบบ Zero-Tolerance
2. **แก้ไขวงจรส่งข้อมูลพารามิเตอร์ 64 บิต:**
   * เปลี่ยนเป็นสถาปัตยกรรม **DMUX Synchronizer** ร่วมกับสัญญาณ `coeff_valid` ที่ซิงโครไนซ์ผ่าน 2-FF
   * หรือใช้ **4-Phase Handshake CDC** เนื่องจากเป็นพารามิเตอร์ที่อัปเดตนานๆ ครั้ง
   * กำหนดข้อจำกัด `set_bus_skew` และ `set_max_delay -datapath_only` ในไฟล์ XDC
3. **ติดตั้งระบบ Zero-Waiver Enforcement ใน CI/CD:** บังคับให้บิลด์ล้มเหลวหากมีคำสั่ง Waiver ใหม่ปรากฏขึ้นใน Pull Request โดยไม่มีลายเซ็น Lead Architect

#### ใบตรวจสอบมาตรฐาน SOP สำหรับ CDC Sign-Off (Senior SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | รายงาน `report_cdc` มีจำนวน Critical Warnings เป็นศูนย์หรือไม่? | **ต้องเป็น 0 เสมอ ($100\%$)** | [ ] ผ่าน |
| 2 | มีการใช้ Blanket Waiver (การใช้ `*` ครอบคลุมหลายโมดูล) หรือไม่? | **ห้ามมีเด็ดขาด (Strictly Banned)** | [ ] ผ่าน |
| 3 | Waiver ทุกรายการที่ยังจำเป็นต้องมี ได้รับการบันทึกเหตุผลทางคณิตศาสตร์ครบถ้วน? | Full Technical Justification | [ ] ผ่าน |
| 4 | มีลายเซ็นอนุมัติของ Chief Reviewer กำกับในไฟล์ Waiver หรือไม่? | Authorized Signature | [ ] ผ่าน |
| 5 | สคริปต์ CI/CD มีการตรวจสอบการเพิ่มขึ้นของจำนวน Waiver (Waiver Creep Check)? | Zero Regression Allowed | [ ] ผ่าน |
| 6 | รันการตรวจสอบ Functional CDC Assertion ครบทุกพาธสำคัญหรือไม่? | Formal Verification Pass | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | 静的CDC検証 | せいてきCDCけんしょう | Seiteki CDC kenshō | Static CDC Verification |
| 2 | 構造解析ルール | こうぞうかいせきルール | Kōzō kaiseki rūru | Structural Analysis Rules (Linting) |
| 3 | 機能的プロトコル検証 | きのうてきプロトコルけんしょう | Kinōteki purotokoru kenshō | Functional Protocol Verification |
| 4 | 適用除外 / ウェイバー | てきようじょがい / ウェイバー | Tekiyō jogai / Weibā | Waiver (การยกเว้นข้อผิดพลาด) |
| 5 | 包括的除外 | ほうかつてきじょがい | Hōkatsuteki jogai | Blanket / Indiscriminate Waiver |
| 6 | 疑似警告 / 誤検知 | ぎじけいこく / ごけんち | Giji keikoku / Gokenchi | False Positive (การแจ้งเตือนผิดพลาด) |
| 7 | リリース判定ゲート | リリースはんていゲート | Rirīsu hantei gēto | Quality Release Gate (ประตูตรวจรับรอง) |
| 8 | 未知のメタステーブル | みちのメタステーブル | Michi no metastēburu | Undetected Metastability |
| 9 | 監査証跡 | かんさしょうせき | Kansa shōseki | Audit Trail / Justification Log |
| 10 | ゼロ・ワーニング運用 | ゼロ・ワーニングうんよう | Zero wāningu un'yō | Zero-Warning Policy |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ศูนย์ตรวจสอบคุณภาพอุปกรณ์การแพทย์ (Medical Devices Quality Assurance Division), เมืองโกเบ (Kobe)  
**ผู้เข้าร่วม:**
* **นากามุระซัง (Nakamura-san):** ผู้จัดการอาวุโสฝ่ายประกันคุณภาพและตรวจแบบ (Senior QA Review Director / 統括技師長)
* **วีรภัทร (Weeraphat):** วิศวกรออกแบบระบบประมวลผลสัญญาณดีเอ็นเอ (Bio-signal FPGA Designer)

---

**中村技師長 (Nakamura):**  
「ウィーラパット君、このDNAシーケンサー用FPGAのCI/CDパイプライン設定とリリース判定レポートを見たよ。ビルドは正常終了（PASS）になっているが、リポジトリに追加された`cdc_waiver.tcl`を開いて驚いた。`create_waiver -id CDC-6 -from * -to *`という記述で、光学センサーとAIエンジンの間のマルチビットCDC警告240件を一括で握りつぶしているじゃないか！なぜこんな恐ろしいスクリプトをコミットしたのかね？」  
*(Wīrapatto-kun, kono DNA shīkensā-yō FPGA no CI/CD paipurain settei to rirīsu hantei repōto wo mita yo. Birudo wa seijō shūryō ni natte iru ga, ripojitori ni tsuika sareta cdc_waiver.tcl wo aite odoroita. create_waiver -id CDC-6 -from * -to * to iu kijutsu de, kōgaku sensā to AI enjin no aida no maruchibitto CDC keikoku 240-ken wo ikkatsu de nigiritsubushite iru ja nai ka! Naze konna osoroshī sukuriputo wo komitto shita no kane?)*  
**คำแปล:** คุณวีรภัทร ผมได้ตรวจการตั้งค่า CI/CD Pipeline และรายงาน Release Gate ของ FPGA เครื่องตรวจดีเอ็นเอนี้แล้ว สถานะบิลด์ผ่านเป็น PASS ก็จริง แต่พอเปิดดูไฟล์ `cdc_waiver.tcl` ที่เพิ่มเข้ามาใน Git ผมตกใจมากเลยนะ คุณเขียนคำสั่ง `create_waiver -id CDC-6 -from * -to *` กวาดซ่อนคำเตือน Multi-bit CDC ระหว่างเซนเซอร์กับเอนจิน AI หายไปทีเดียว 240 รายการเลยไม่ใช่หรือ! ทำไมถึงกล้าคอมมิตสคริปต์ที่น่าสะพรึงกลัวขนาดนี้เข้ามาครับ?

**ウィーラパット (Weeraphat):**  
「申し訳ございません、中村技師長……！来週の医療機器認証申請のマイルストーンが迫っており、CI/CDでCritical Warningが1つでも残っているとビルドが完了しない設定になっていたため、一時的にテストを通す目的で包括的ウェイバー（Blanket Waiver）を適用してしまいました。係数データは頻繁に変わるものではないため、実機でも誤動作は起きないと高を括っておりました。」  
*(Mōshiwake gozaimasen, Nakamura-gishichō...! Raishū no iryō kiki ninshō shinsei no mairusutōn ga sematte ori, CI/CD de Critical Warning ga hitotsu demo nokotte iru to birudo ga kanryō shinai settei ni natte ita tame, ichijiteki ni tesuto wo tōsu mokuteki de hōkatsuteki weibā wo tekiyō shite shimaimashita. Keisū dēta wa himpan ni kawaru mono dewa nai tame, jikki demo godōsa wa okinai to taka wo kukutte orimashita.)*  
**คำแปล:** กราบขออภัยเป็นอย่างยิ่งครับหัวหน้าช่างนากามุระ...! เนื่องจากกำหนดส่งเอกสารขอการรับรองเครื่องมือแพทย์ในสัปดาห์หน้ากระชั้นชิดมาก และการตั้งค่าใน CI/CD หากมี Critical Warning เหลืออยู่แม้แต่อันเดียวบิลด์จะไม่ยอมรันต่อ ผมจึงใส่ Blanket Waiver เพื่อให้การทดสอบผ่านไปก่อนชั่วคราวครับ และผมประเมินต่ำไปคิดว่าข้อมูลสัมประสิทธิ์นี้ไม่ได้เปลี่ยนบ่อย ในเครื่องจริงคงไม่เกิดปัญหาอะไรครับ

**中村技師長 (Nakamura):**  
「何を言っているんだ！これは人の命を預かる医療機器だよ！頻度が低かろうが、64ビットの補正パラメータがCDC境界でバススキューによって化けたら、ガン細胞の変異検出結果が真逆になってしまう。患者の誤診につながる致命的な不具合を『マイルストーンに間に合わせるため』に隠蔽したと言うのかね！？これは我が社の品質倫理規定に対する重大な違反行為だよ！」  
*(Nani wo itte iru n da! Kore wa hito no inochi wo azukaru iryō kiki da yo! Hindo ga hikukarō ga, 64-bit no hosei paramēta ga CDC kyōkai de basu sukyū ni yotte baketara, gan-saibō no hen'i kenshutsu kekka ga magyaku ni natte shimau. Kanja no goshin ni tsunagaru chimeiteki na fuguai wo "mairusutōn ni maniawaseru tame" ni impei shita to iu no kane!? Kore wa wagasha no hinshitsu rinri kitei ni taisuru jūdai na ihan kōi da yo!)*  
**คำแปล:** พูดอะไรออกมาน่ะ! นี่คือเครื่องมือแพทย์ที่ต้องรับผิดชอบชีวิตคนนะ! ไม่ว่าจะเปลี่ยนไม่บ่อยแค่ไหน หากพารามิเตอร์ 64 บิตเกิดเพี้ยนจาก Bus Skew ตรงรอยต่อ CDC ผลการตรวจการกลายพันธุ์ของเซลล์มะเร็งอาจกลายเป็นตรงกันข้ามทันที คุณกำลังบอกว่าคุณปกปิดข้อบกพร่องร้ายแรงที่นำไปสู่การวินิจฉัยโรคผู้ป่วยผิดพลาด เพียงเพื่อให้ทันกำหนดส่งมอบงานงั้นหรือ!? นี่เป็นการละเมิดจริยธรรมด้านคุณภาพของบริษัทเราอย่างร้ายแรงที่สุดเลยนะ!

**ウィーラパット (Weeraphat):**  
「深く反省しております……。取り返しのつかない事態になるところでした。直ちに包括的ウェイバーを全件差し戻し、64ビットバスをDMUXおよびハンドシェイク同期回路へ全面的に改修いたします。」  
*(Fukaku hansei shite orimasu... Torikaeshi no tsukanai jitai ni naru tokoro deshita. Tadachini hōkatsuteki weibā wo zenken sashimodoshi, 64-bit basu wo DMUX oyobi handosheiku dōki kairo e zemmenteki ni kaishū itashimasu.)*  
**คำแปล:** ผมสำนึกผิดและเสียใจจากใจจริงครับ... เกือบจะเกิดเหตุการณ์ที่ไม่อาจแก้ไขได้ขึ้นแล้ว ผมจะรีบยกเลิก Blanket Waiver ทั้งหมดทันที และจะยกเครื่องบัส 64 บิตให้เป็นวงจรซิงโครไนซ์แบบ DMUX และ Handshake ทั้งหมดเดี๋ยวนี้ครับ

**中村技師長 (Nakamura):**  
「そうだ。そして今後、CI/CDの設定には『新規ウェイバー追加の自動ブロック機能』を導入し、Chief Reviewerの暗号署名がないウェイバーは受け付けない仕組みにしなさい。すべてのCDC-6違反を物理的に解消し、静的検証レポートでWarningが完全に『ゼロ』になったことを確認してから、再度私のところへ検図を受けに来ること！」  
*(Sō da. Soshite kongo, CI/CD no settei ni wa "shinki weibā tsuika no jidō burokku kinō" wo dōnyū shi, Chief Reviewer no angō shomei ga nai weibā wa uketsukenai shikumi ni shinasai. Subete no CDC-6 ihan wo butsuri-teki ni kaishō shi, seiteki kenshō repōto de Warning ga kanzen ni "zero" ni natta koto wo kakunin shite kara, saido watashi no tokoro e kenzu wo uke ni kuru koto!)*  
**คำแปล:** ถูกต้อง และต่อไปนี้ ในการตั้งค่า CI/CD จะต้องติดตั้งระบบบล็อกการเพิ่ม Waiver ใหม่อัตโนมัติ โดยจะไม่ยอมรับ Waiver ที่ไม่มีลายเซ็นเข้ารหัสของ Chief Reviewer กำกับเด็ดขาด จงแก้ไขข้อผิดพลาด CDC-6 ทางกายภาพให้หมดสิ้น และเมื่อตรวจสอบว่ารายงาน Static CDC มี Warning เป็น "ศูนย์" อย่างสมบูรณ์แล้ว ค่อยกลับมาให้ผมตรวจแบบอีกครั้ง!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การจำแนกประเภทข้อผิดพลาดในรายงาน Vivado `report_cdc`
ในระหว่างการทำ Static CDC Audit บนโครงการดาวเทียมสำรวจอวกาศ วิศวกรได้รับรายงานสรุปผลลัพธ์จาก Vivado `report_cdc` ดังนี้:
1. `Violation 1: [CDC-1] Unsynchronized sub-path from reg_a to reg_b`
2. `Violation 2: [CDC-6] Multi-bit data bus 'tx_data[15:0]' synchronized using separate 2-FF synchronizers per bit`
3. `Violation 3: [CDC-8] Synchronized control signals 'fsm_start' and 'fsm_abort' reconverge at next-state logic in destination clock domain`
4. `Violation 4: [CDC-10] Mux-Data topology detected without set_bus_skew constraint on 'sensor_val[31:0]'`

หากจำเป็นต้องจัดลำดับความสำคัญตาม **ความรุนแรงของความเสี่ยงต่อความอยู่รอดของภารกิจ (Mission-Critical Hazard Severity)** จากสูงสุดไปหาต่ำสุด ข้อใดต่อไปนี้จัดลำดับได้อย่างถูกต้องที่สุดตามมาตรฐาน DO-254 DAL-A?

---

#### ตัวเลือก:
* **ก)** CDC-10 $\to$ CDC-8 $\to$ CDC-6 $\to$ CDC-1
* **ข)** CDC-1 $\to$ CDC-6 $\to$ CDC-8 $\to$ CDC-10
* **ค)** CDC-6 $\to$ CDC-10 $\to$ CDC-1 $\to$ CDC-8
* **ง)** ทุกข้อมีความรุนแรงเท่ากันหมด ไม่สามารถจัดลำดับได้

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **อันดับ 1: `CDC-1` (Unsynchronized Path):**
   * มีความรุนแรงสูงสุดอย่างเด็ดขาด เพราะเป็นเส้นทางที่ไม่มีการดักจับ Metastability เลยแม้แต่สเตจเดียว
   * เมื่อสัญญาณเดินทางข้ามโดเมน ฟลิปฟล็อปปลายทางจะเกิดสภาวะ Metastable และส่งต่อค่าที่ไม่แน่นอนเข้าสู่คอร์ประมวลผลโดยตรง ซึ่งนำไปสู่ความล้มเหลวของฮาร์ดแวร์ในระดับวินาทีหรือนาที
2. **อันดับ 2: `CDC-6` (Multi-bit Bit-by-Bit Synchronizers):**
   * มีความรุนแรงระดับวิกฤตอันดับสอง เพราะแม้จะมี 2-FF ดักจับ Metastability ของแต่ละบิตได้
   * แต่เกิดปรากฏการณ์ **Bus Skew และ Convergent Sampling Failure** อย่างแน่นอน ทำให้ปลายทางแซมเปิลได้ค่าขยะและข้อมูลเสียหายในทุกๆ ครั้งที่มีการเปลี่ยนสถานะบัสหลายบิตพร้อมกัน
3. **อันดับ 3: `CDC-8` (Reconvergence of Synchronized Signals):**
   * มีความรุนแรงระดับวิกฤตอันดับสาม เกิดจากสภาวะ **1-Cycle Synchronizer Skew**
   * ซึ่งแม้จะไม่เกิดทุกครั้งที่สัญญาณเปลี่ยนสถานะ (เกิดขึ้นเฉพาะเมื่อสัญญาณตกในหน้าต่าง Metastability Window $\approx 1\% - 2\%$) แต่สามารถสร้าง Spurious Glitch ขนาด 1 ไซเคิลทำให้สเตตแมชชีนปลายทางเปลี่ยนสถานะผิดพลาดได้
4. **อันดับ 4: `CDC-10` (Mux-Data missing `set_bus_skew`):**
   * มีความรุนแรงในระดับคำเตือน (Warning)
   * โทโพโลยีของวงจรเป็นแบบ DMUX ที่ถูกต้องแล้ว แต่ขาดเพียงคำสั่งควบคุมระยะเวลาการเดินสายของบัสข้อมูลใน XDC ซึ่งหากความถี่ของสัญญาณนาฬิกาไม่สูงมากหรือการจัดวางไม่กระจัดกระจาย วงจรอาจยังทำงานได้ถูกต้อง แต่มีความเสี่ยงเมื่ออุณหภูมิเปลี่ยนแปลง

ดังนั้น การจัดลำดับความเร่งด่วนที่ถูกต้องคือ: **CDC-1 $\to$ CDC-6 $\to$ CDC-8 $\to$ CDC-10**

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** เรียงลำดับจากเบาไปหาหนัก สลับขั้วความปลอดภัยทางวิศวกรรม
* **ข้อ ค):** ประเมินความอันตรายของ CDC-1 (ไม่มี Sync เลย) ต่ำกว่า CDC-6 ซึ่งขัดแย้งกับหลักการฟิสิกส์พื้นฐาน
* **ข้อ ง):** ขาดทักษะการประเมิน Risk Prioritization ในระดับวิศวกรอาวุโส

---

### ข้อที่ 2: เงื่อนไขการอนุมัติ CDC Waiver บน Quasi-Static Configuration Bus
ในระหว่างการตรวจแบบโครงการสถานีเรดาร์ป้องกันภัยทางอากาศ วิศวกรตรวจพบข้อความเตือน `CDC-10` บนบัสพารามิเตอร์ `cfg_threshold[15:0]` ซึ่งต่อข้ามจากโดเมนไมโครโปรเซสเซอร์ ($50\text{ MHz}$) ไปยังโดเมนประมวลผลเรดาร์ ($200\text{ MHz}$) โดยไม่มีวงจร Handshake แต่วิศวกรเสนอขอออกคำสั่ง **Waiver** โดยอ้างว่าเป็นสัญญาณ Quasi-Static

ข้อใดต่อไปนี้คือ **เงื่อนไขทางวิศวกรรมที่จำเป็นต้องได้รับการพิสูจน์ (Mandatory Engineering Proof)** ก่อนที่ Lead Chief Reviewer จะสามารถลงนามอนุมัติ Waiver นี้ได้อย่างถูกต้องตามหลักความปลอดภัย?

---

#### ตัวเลือก:
* **ก)** ไมโครโปรเซสเซอร์ต้องใช้ภาษา C ในการเขียนโปรแกรมเท่านั้น
* **ข)** ต้องพิสูจน์ว่า: (1) มีการใช้ Hardware Interlock ปิดการทำงาน (Disable) ของโมดูลเรดาร์ปลายทางก่อนทำการเขียนค่าลงใน `cfg_threshold` เสมอ, (2) ค่าพารามิเตอร์ถูกเขียนและคงที่อยู่นิ่งเป็นเวลาอย่างน้อย 10 รอบของนาฬิกาปลายทางก่อนที่โมดูลเรดาร์จะถูก Enable ให้กลับมาทำงานใหม่, และ (3) มี SystemVerilog Assertion กำกับยืนยันในระดับ Formal Verification
* **ค)** ต้องลดความถี่ของเรดาร์ลงเหลือ $50\text{ MHz}$ ให้เท่ากับไมโครโปรเซสเซอร์
* **ง)** ต้องเปลี่ยนชิป FPGA เป็นเกรดทหาร (Military Grade) จึงจะสามารถออก Waiver ได้

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **นิยามของ Quasi-Static Crossing ที่ปลอดภัย:**
   สัญญาณ Quasi-Static (กึ่งสถิต) หมายถึง สัญญาณที่ไม่มีการเปลี่ยนแปลงสถานะในระหว่างการประมวลผลปกติ ทว่า ในจังหวะที่มีการอัปเดตค่า บัส 16 บิตจะยังคงเกิด Bus Skew ได้เสมอ
2. **กลไกการรับประกันความปลอดภัย (Safe Operating Sequence):**
   การจะยอมให้บัสข้อมูลข้ามโดเมนได้โดยไม่มี Synchronizer หรือไม่มี Bus Skew Constraint ได้นั้น ระบบจะต้องมี **Software/Hardware Protocol ควบคุมลำดับเวลา (Sequencing Interlock)** อย่างเคร่งครัด:
   * **สเต็ป 1:** ไมโครโปรเซสเซอร์ส่งคำสั่งปิด (Disable/Freeze) โมดูลปลายทาง เพื่อไม่ให้มีการนำค่าในเรจิสเตอร์ไปประมวลผล
   * **สเต็ป 2:** เขียนค่าใหม่ลงใน `cfg_threshold` และหน่วงเวลาให้นานพอจนสัญญาณทุกบิตเดินทางถึงปลายทางและคงตัวนิ่งสนิท
   * **สเต็ป 3:** ส่งคำสั่งเปิด (Enable/Unfreeze) โมดูลปลายทางให้กลับมาทำงาน
3. **การพิสูจน์หลักฐาน (Evidence & Sign-off):**
   จะต้องมีโค้ด **SVA Formal Assertion** กำกับเพื่อยืนยันว่าไม่มีการอ่านค่าในขณะที่ค่ากำลังเปลี่ยน และมีบันทึกขั้นตอนการทำงานนี้แนบในเอกสาร Waiver อย่างครบถ้วน จึงจะถือว่ามีคุณสมบัติเพียงพอในการอนุมัติ!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** ภาษาโปรแกรมที่ใช้เขียนเฟิร์มแวร์ไม่มีความเกี่ยวข้องกับฟิสิกส์ของสัญญาณฮาร์ดแวร์บนซิลิคอน
* **ข้อ ค):** การลดความถี่ไม่ได้เปลี่ยนความจริงที่ว่าสัญญาณนาฬิกาทั้งสองมีเฟสไม่สัมพันธ์กัน (Asynchronous)
* **ข้อ ง):** เกรดของชิป (Commercial vs Military) เกี่ยวข้องกับช่วงอุณหภูมิ ไม่ได้ช่วยแก้ปัญหา Timing Skew ข้ามโดเมน

---

### ข้อที่ 3: สถาปัตยกรรม CI/CD Automated Zero-Regression Gate
ในการสร้าง Continuous Integration (CI) Pipeline สำหรับการพัฒนาฮาร์ดแวร์ FPGA ระดับองค์กร หากต้องการป้องกันไม่ให้มี "Waiver Creep" (การแอบเพิ่มคำสั่ง Waiver โดยไม่ผ่านการตรวจสอบ) ข้อใดต่อไปนี้คือ **กลไกการตรวจสอบอัตโนมัติ (Automated Gate Mechanism)** ที่มีประสิทธิภาพและรัดกุมสูงสุด?

---

#### ตัวเลือก:
* **ก)** ส่งอีเมลแจ้งเตือนไปยังผู้จัดการโครงการทุกครั้งที่มีการกด Commit โค้ด
* **ข)** การกำหนดให้สคริปต์ CI รันการตรวจสอบแบบสองขั้นตอน (Two-Tier Enforcement): (1) สกัดรายการและนับจำนวนคำสั่ง Waiver ทั้งหมดในไฟล์ constraints/tcl หากจำนวน Waiver เพิ่มขึ้นจาก Master Baseline แม้เพียง 1 รายการ ให้สั่ง Build Fail ทันที, และ (2) ตรวจสอบไฟล์ Waiver ทุกตัวว่าต้องมี Git Commit Signed-off-by Tag จากบัญชีคีย์ GPG ของ Lead Chief Reviewer เท่านั้น จึงจะอนุญาตให้ทำการ Merge
* **ค)** ลบคำสั่ง `report_cdc` ออกจากสคริปต์ CI เพื่อไม่ให้มีรายงานข้อผิดพลาด
* **ง)** สั่งให้โปรแกรมสร้างไฟล์บิตสตรีมซ้ำ 3 ครั้งเพื่อเปรียบเทียบ Checksum

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **ปรากฏการณ์ Waiver Creep:**
   ในโครงการขนาดใหญ่ที่มีนักพัฒนาหลายสิบคน มักเกิดเหตุการณ์ที่วิศวกรแอบเพิ่ม Waiver เล็กๆ น้อยๆ เพื่อแก้ปัญหาโค้ดของตนเองให้ผ่าน CI ซึ่งเมื่อเวลาผ่านไป จำนวน Waiver จะสะสมจากหลักสิบกลายเป็นหลายร้อยรายการ จนระบบกลายเป็นช่องโหว่ขนาดใหญ่
2. **กลไก Two-Tier Zero-Regression Gate:**
   * **Tier 1 (Waiver Count Freezing):** ระบบ CI จะเก็บค่าตัวเลขรวมของ Waiver ที่ได้รับอนุมัติในโปรดักชัน หาก Pull Request ใดทำให้ตัวเลขรวมนี้ขยับสูงขึ้น จะถูกปฏิเสธ (Reject) อัตโนมัติทันที
   * **Tier 2 (Cryptographic Sign-off Audit):** ทุกบรรทัดของการยกเว้นจะต้องผูกโยงกับลายเซ็นดิจิทัล (GPG Signed Commit) ของวิศวกรระดับ Lead Architect ทำให้มีหลักฐาน Audit Trail ที่โปร่งใสและตรวจสอบย้อนหลังได้ตามมาตรฐาน ISO 26262 / DO-254 อย่างสมบูรณ์แบบ!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** การส่งอีเมลไม่สามารถระงับ (Block) การ Merge โค้ดที่ผิดพลาดเข้าสู่สาขาหลักได้
* **ข้อ ค):** เป็นการปิดตาละทิ้งการตรวจสอบ ซึ่งนำไปสู่หายนะของผลิตภัณฑ์
* **ข้อ ง):** Checksum ของไฟล์บิตสตรีมเป็นเพียงผลลัพธ์ของไฟล์คอมไพล์ ไม่สามารถตรวจสอบความถูกต้องของสถาปัตยกรรม CDC ได้
