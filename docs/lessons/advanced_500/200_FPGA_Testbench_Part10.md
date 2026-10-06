# Lesson 200: FPGA Testbench Part 10 — Master Production Verification Sign-Off & Bitstream Release Governance (เกณฑ์การตรวจรับรองการผลิตระดับมาสเตอร์และการควบคุมการปล่อยบิตสตรีมสู่สายการผลิต)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ยินดีต้อนรับสู่ **บทที่ 200** ซึ่งเป็นจุดบรรจบสูงสุดของมหากาพย์การออกแบบและตรวจสอบระบบดิจิทัลบน FPGA และ ASIC ขั้นสูง! หลังจากที่เราได้เดินทางผ่านหลักฟิสิกส์เซมิคอนดักเตอร์, สถาปัตยกรรม Clock Domain Crossing (CDC), โครงสร้าง Synchronous/Asynchronous FIFO, และระเบียบวิธีการตรวจสอบระดับ UVM/Formal ทั้งหมดแล้ว ขั้นตอนสุดท้ายที่ชี้ชะตาความเป็นความตายของโครงการมูลค่าหลายร้อยล้านดอลลาร์คือ **"Master Production Verification Sign-Off & Bitstream Release Governance"**

ในระดับอุตสาหกรรม การปล่อยไฟล์ Bitstream หรือการส่งมอบ Photomask Netlist เพื่อเข้าสู่สายการผลิตจำนวนมาก (Mass Production / Tape-Out) ไม่ใช่การกดปุ่ม "Generate Bitstream" ในซอฟต์แวร์ IDE แล้วส่งไฟล์แนบไปทางอีเมล แต่มันคือ **กระบวนการรับรองอย่างเป็นทางการทางกฎหมายและวิศวกรรม (Legal & Engineering Certification Gate)** ซึ่งต้องผ่านการประเมินตาม **7 ประตูด่านทองคำ (The Seven Golden Production Gates)** อย่างไร้ข้อกังขา

```
+--------------------------------------------------------------------------------------------------+
|                   THE SEVEN GOLDEN PRODUCTION VERIFICATION SIGN-OFF GATES                         |
+--------------------------------------------------------------------------------------------------+
                                                                                                    
  [GATE 1] TIMING CLOSURE      : WNS >= 0.0 ps, WHS >= 0.0 ps Across All PVT Corners                
  --------------------------------------------------------------------------------------------------
  [GATE 2] STATIC CDC / RDC    : Zero Unwaived CDC Errors, 100% Structural CDC Sign-Off Clean       
  --------------------------------------------------------------------------------------------------
  [GATE 3] FUNCTIONAL COVERAGE : 100% Coverage Closure (Covergroups, Crosses, SVA Formal Proven)   
  --------------------------------------------------------------------------------------------------
  [GATE 4] CODE & MC/DC COV    : 100% Statement, Branch, FSM, and MC/DC (DO-254 / ISO 26262)        
  --------------------------------------------------------------------------------------------------
  [GATE 5] GATE-LEVEL (GLS)    : Multi-Corner SDF Back-Annotation Passed with ZERO Glitch Hazards   
  --------------------------------------------------------------------------------------------------
  [GATE 6] PDN & THERMAL (SI)  : Tj <= 105°C, Vcore Ripple <= 2%, PDN Target Impedance Met          
  --------------------------------------------------------------------------------------------------
  [GATE 7] SECURITY GOVERNANCE : AES-256-GCM Encrypted, RSA-4096 Signed, eFUSE Key Provisioning     
  ==================================================================================================
                                             ||                                                     
                                             v                                                     
                     +-----------------------------------------------+                              
                     |       GOLDEN MASTER PRODUCTION BITSTREAM      |                              
                     |   (Cryptographic Hash & Release Manifest)     |                              
                     +-----------------------------------------------+                              
```

---

### 1.1 รายละเอียดทางวิศวกรรมของ The Seven Golden Production Gates

#### Gate 1: Static Timing Closure (STA) Across All PVT Corners
- **Worst Negative Slack (WNS):** $\text{WNS} \ge 0.000\text{ ps}$ (Setup Time Closure ผ่านทุกโดเมนสัญญาณนาฬิกา)
- **Worst Hold Slack (WHS):** $\text{WHS} \ge 0.000\text{ ps}$ (Hold Time Closure ผ่านที่ Fast/Cold Corner)
- **Pulse Width & Clock Duty Cycle Slack:** $\text{WPWS} \ge 0.000\text{ ps}$ (ความกว้างพัลส์ขั้นต่ำของ BRAM/DSP ผ่านเกณฑ์)
- **Total Negative Slack (TNS / THS):** ต้องมีค่าเท่ากับ $0.000\text{ ps}$ อย่างเด็ดขาด

#### Gate 2: Static CDC & Reset Domain Crossing (RDC) Sign-Off
- รันเครื่องมือ Static CDC Analyzer (เช่น Synopsys SpyGlass CDC, Questa CDC, หรือ Vivado `report_cdc`)
- **Zero Unwaived Violations:** ต้องไม่มีเส้นทางข้ามแดนสัญญาณนาฬิกาที่ตกค้าง
- **Waiver Audit Governance:** หากมีเส้นทางที่ขอยกเว้น (Waiver) ต้องมีเอกสารอนุมัติทางเทคนิครองรับ พร้อมทั้งพิสูจน์ด้วย Formal Property Verification หรือ SVA เสมอ

#### Gate 3 & Gate 4: 100% Completeness of Coverage & MC/DC
- **Functional Coverage:** 100% Coverage Closure (ห้ามมี Uncovered Bins ตกค้าง)
- **Structural Coverage:**
  - Statement Coverage = 100%
  - Branch Coverage = 100%
  - Toggle Coverage = 100% (บน I/O Ports และ State Registers)
  - FSM State & Transition Coverage = 100%
  - **MC/DC Coverage = 100%** สำหรับระบบความปลอดภัยสูงสุด (DO-254 DAL-A หรือ ISO 26262 ASIL-D)

#### Gate 5: Multi-Corner Gate-Level Simulation (GLS)
- รันการจำลองระดับเกตด้วยไฟล์ SDF Back-Annotation ทั้งสภาวะ **Min Corner** และ **Max Corner**
- **Zero X-Propagation:** วงจรต้องสามารถหลุดพ้นจากสภาวะ Power-On Reset ได้อย่างสมบูรณ์โดยไม่มีสัญญาณ `X` ค้างในระบบ
- **Zero Timing Glitch Errors:** ไม่มีการแจ้งเตือน `$setuphold` หรือ `$recovery/$removal` ในคอนโซล

#### Gate 6: Power Distribution Network (PDN) & Thermal Integrity
ระบบฮาร์ดแวร์จริงต้องจ่ายพลังงานได้เสถียรภายใต้กระแสกระชากสูงสุด (Transient Dynamic Current $\Delta I_{step}$):
$$Z_{target} = \frac{V_{core} \times \text{Ripple\%}}{\Delta I_{step}}$$
- อุณหภูมิรอยต่อซิลิคอนสูงสุด (Worst-Case Junction Temperature): $T_j \le 105^\circ\text{C}$ (หรือ $125^\circ\text{C}$ สำหรับเกรดยานยนต์ Automotive Grade 1)
- ตรวจสอบผ่านเครื่องมือ Vivado Report Power / Ansys RedHawk

#### Gate 7: Bitstream Cryptographic Security & Anti-Tamper Governance
ในสายการผลิต อุปกรณ์ FPGA ต้องได้รับการป้องกันการโจรกรรมทรัพย์สินทางปัญญา (IP Piracy), การย้อนรอยวิศวกรรม (Reverse Engineering), และการฉีดโค้ดอันตราย (Malicious Bitstream Injection):
1. **AES-256-GCM Bitstream Encryption:** เข้ารหัสเนื้อหา Bitstream ทั้งหมด
2. **SHA-3 / HMAC-256 Authentication:** ตรวจสอบความถูกต้องของข้อมูลทุกบล็อก
3. **Hardware Root-of-Trust (RoT):** จัดเก็บคีย์ถาวรใน **eFUSE Registers** (One-Time Programmable) หรือ **BBRAM** (Battery-Backed RAM พร้อมวงจร Zeroization ทำลายคีย์ทิ้งทันทีหากมีการงัดแงะชิป)

---

### 1.2 โครงสร้างระบบ CI/CD Automated Tape-Out Audit & Manifest Generator

ในการผลิตระดับมืออาชีพ มนุษย์จะไม่เป็นผู้สร้าง Bitstream ด้วยตนเอง แต่จะถูกสร้างขึ้นผ่าน **Automated CI/CD Release Pipeline (Zero-Touch Production Build)** ซึ่งจะตรวจสอบ Gates ทั้งหมด และสร้างไฟล์ **Release Manifest (JSON)** พร้อมลายเซ็นดิจิทัลเข้ารหัสกุญแจสาธารณะ (RSA-4096 / Ed25519)

```
[Git Commit Tag: v3.2.0-RELEASE]
              |
              v
[GitLab CI / Jenkins Hardened Runner]
              |
              +---> Step 1: Synthesis & Implementation (Vivado batch mode)
              +---> Step 2: Automated Timing & CDC Gate Verification
              +---> Step 3: Vivado DRC (Design Rule Checks) Audit
              +---> Step 4: AES-256 Bitstream Encryption via HSM Key
              +---> Step 5: Generate Cryptographic SHA-256 Checksums
              +---> Step 6: Generate Production Release Manifest JSON
              |
              v
[Immutable Artifact Storage / Artifactory] ===> [Factory Programming Station]
```

---

### 1.3 Production Automation Script: Master Vivado Sign-Off & Release Script (`signoff_release.tcl`)

สคริปต์ระดับโปรดักชันนี้แสดงกระบวนการตรวจสอบ Gates 1 ถึง 7 อัตโนมัติใน Vivado พร้อมสร้างบิตสตรีมที่เข้ารหัสและบันทึกผลการตรวจสอบ

```tcl
#==============================================================================
# Script: signoff_release.tcl
# Description: Master Production Verification Sign-Off & Bitstream Generator
# Standards: DO-254 DAL-A / ISO 26262 ASIL-D Automated Release Governance
#==============================================================================

# 1. Initialization and Project Setup
set project_name "avionics_flight_controller"
set output_dir   "./production_artifacts"
file mkdir $output_dir

puts "======================================================================"
puts "   STARTING MASTER PRODUCTION VERIFICATION SIGN-OFF AUDIT PIPELINE   "
puts "======================================================================"

# 2. GATE 1: Timing Closure Verification
puts "\n>>> [AUDIT][GATE 1] Checking Static Timing Closure Slack..."
set wns [get_property SLACK [get_timing_paths -max_paths 1 -setup]]
set whs [get_property SLACK [get_timing_paths -max_paths 1 -hold]]
set wpws [get_property SLACK [get_timing_paths -max_paths 1 -pulse_width]]

puts "    Current Worst Negative Slack (WNS) : $wns ps"
puts "    Current Worst Hold Slack     (WHS) : $whs ps"
puts "    Current Pulse Width Slack    (WPWS): $wpws ps"

if {$wns < 0.0 || $whs < 0.0 || $wpws < 0.0} {
    puts "\[FATAL SIGN-OFF FAILURE\] Gate 1 Failed! Timing violations detected."
    exit 1
} else {
    puts "    \[GATE 1 PASSED\] Timing Closure 100% Met."
}

# 3. GATE 2: Static CDC & Waiver Verification
puts "\n>>> [AUDIT][GATE 2] Verifying Clock Domain Crossing (CDC) Integrity..."
report_cdc -file "$output_dir/cdc_signoff_report.rpt" -details
set cdc_critical_errors [get_property COUNT [get_cdc_violations -severity Critical]]
if {$cdc_critical_errors > 0} {
    puts "\[FATAL SIGN-OFF FAILURE\] Gate 2 Failed! Found $cdc_critical_errors Critical CDC errors."
    exit 2
} else {
    puts "    \[GATE 2 PASSED\] Zero Critical CDC Errors Found."
}

# 4. Design Rule Checks (DRC) Verification
puts "\n>>> [AUDIT] Running Comprehensive Physical DRC Rules..."
report_drc -file "$output_dir/drc_production.rpt" -severity ERROR
set drc_errors [get_property COUNT [get_drc_violations -severity ERROR]]
if {$drc_errors > 0} {
    puts "\[FATAL SIGN-OFF FAILURE\] Physical DRC violations detected: $drc_errors errors."
    exit 3
} else {
    puts "    \[DRC PASSED\] Zero Physical Violations."
}

# 5. GATE 7: Security Configuration & Encrypted Bitstream Generation
puts "\n>>> [AUDIT][GATE 7] Configuring Hardware Security and Bitstream Encryption..."

# Configure Vivado Bitstream Security Properties
set_property BITSTREAM.ENCRYPTION.ENCRYPT YES [current_design]
set_property BITSTREAM.ENCRYPTION.KEYFILE "./security_keys/aes_prod_key.nky" [current_design]
set_property BITSTREAM.AUTHENTICATION.AUTHENTICATE YES [current_design]
set_property BITSTREAM.SECURITY.SECURITY LEVEL2 [current_design] ;# Disable Readback

# Generate Master Encrypted Bitstream
puts ">>> Generating Production Bitstream: $output_dir/golden_master.bit"
write_bitstream -force "$output_dir/golden_master.bit"

# 6. Generate Cryptographic Manifest & SHA-256 Checksums
puts "\n>>> Generating Cryptographic Manifest..."
set bitstream_file "$output_dir/golden_master.bit"
set sha256_hash [exec certutil -hashfile $bitstream_file SHA256 | select -Index 1]

# Write Release Manifest JSON
set manifest_file "$output_dir/release_manifest.json"
set fp [open $manifest_file "w"]
puts $fp "{"
puts $fp "  \"project\": \"$project_name\","
puts $fp "  \"release_date\": \"[clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%SZ}]\","
puts $fp "  \"git_commit\": \"[exec git rev-parse HEAD]\","
puts $fp "  \"signoff_gates\": {"
puts $fp "    \"gate1_timing_wns_ps\": $wns,"
puts $fp "    \"gate1_timing_whs_ps\": $whs,"
puts $fp "    \"gate2_cdc_critical\": $cdc_critical_errors,"
puts $fp "    \"gate7_encryption\": \"AES-256-GCM\","
puts $fp "    \"gate7_anti_tamper\": \"ENABLED\""
puts $fp "  },"
puts $fp "  \"bitstream\": {"
puts $fp "    \"filename\": \"golden_master.bit\","
puts $fp "    \"sha256\": \"$sha256_hash\""
puts $fp "  },"
puts $fp "  \"status\": \"PRODUCTION_SIGNOFF_APPROVED\""
puts $fp "}"
close $fp

puts "======================================================================"
puts "  PRODUCTION SIGN-OFF SUCCESSFUL! ALL GATES PASSED WITHOUT VIOLATIONS "
puts "  RELEASE MANIFEST: $manifest_file                                    "
puts "======================================================================"
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความเสียหายจริงในภาคสนาม (失敗事例 - Shippai Jirei)
**ระบบคอมพิวเตอร์ประมวลผลส่วนกลางสำหรับยานยนต์อัตโนมัติไร้คนขับระดับ Level 4 (Autonomous Robotaxi Central Domain Compute Unit FPGA)** เกิดอุบัติเหตุพุ่งชนแบริเออร์คอนกรีตแบ่งเลนบนทางด่วนขณะเปลี่ยนเลนที่ความเร็ว 90 km/h: ผู้โดยสารในรถได้รับบาดเจ็บ ตัวรถเสียหายสิ้นเชิง

การตรวจสอบข้อมูลบันทึกสีดำ (Black-Box Forensics) พบว่า บิตสตรีมที่ถูกโปรแกรมลงในชิป FPGA บนรถคันที่เกิดเหตุ **ไม่ใช่ "Golden Master Bitstream" ที่ผ่านกระบวนการ Verification Sign-off ครบถ้วน** แต่เป็นไฟล์ **Debug Test Build** ที่วิศวกรส่งผ่านช่องทางแชทส่วนตัวให้ช่างเทคนิคในโรงงานเพื่อแก้ปัญหาหน้างานชั่วคราว บิตสตรีมทดสอบนี้มีการปิดวงจรตรวจเช็ค Timing Closure และถอดระบบ Error-Correcting Code (ECC) ของกล้อง LIDAR ออกเพื่อเร่งความเร็วในการคอมไพล์ ส่งผลให้ข้อมูลพ้อยต์คลาวด์ของ LIDAR เกิดความล่าช้าไป 2 เฟรม ($66\text{ ms}$) ทำให้ระบบเบรกฉุกเฉินทำงานช้าเกินไป

ผลลัพธ์: กรมการขนส่งทางบกสั่งระงับใบอนุญาตทดสอบยานยนต์ไร้คนขับของบริษัททั่วประเทศเป็นเวลา 6 เดือน มูลค่าหุ้นร่วงลงและความเสียหายทางธุรกิจรวมกว่า **28 ล้านดอลลาร์สหรัฐ**

---

### การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมรถยนต์ไร้คนขับจึงหักเลี้ยวชนแบริเออร์กั้นทางบนทางด่วน?**
   - *คำตอบ:* ระบบประมวลผลเซนเซอร์ฟิวชัน (Sensor Fusion Engine) บน FPGA ส่งตำแหน่งของสิ่งกีดขวางล่าช้าไป 2 เฟรม ทำให้คำนวณระยะห่างผิดพลาด
2. **ทำไมชิป FPGA จึงประมวลผลข้อมูลเซนเซอร์ล่าช้ากว่าสเปก?**
   - *คำตอบ:* ในชิปมีสัญญาณรบกวนข้ามแดนคล็อก (CDC Metastability Skew) และบัฟเฟอร์ค้าง ทำให้ทราฟฟิกข้อมูลเกิด Backpressure
3. **ทำไมบักนี้จึงไม่ถูกดักจับในระหว่างการทดสอบในขั้นตอนพัฒนา?**
   - *คำตอบ:* ชิปบนรถคันจริงถูกโปรแกรมด้วยไฟล์บิตสตรีม `debug_patch_v2.bit` ที่ไม่ได้ผ่านกระบวนการ Sign-off และไม่มีการรัน GLS
4. **ทำไมช่างเทคนิคในโรงงานจึงนำไฟล์ Debug Patch ไปโปรแกรมลงในรถคันจริงได้?**
   - *คำตอบ:* โรงงานผลิตไม่มีระบบ **Zero-Trust Programming Station** ช่างเทคนิคสามารถดาวน์โหลดไฟล์ใดก็ได้จากอีเมลหรือ Flash Drive มาเบิร์นลงชิปผ่านสาย JTAG ได้โดยตรง
5. **ทำไมกระบวนการควบคุมคุณภาพ (Kenzu & Release Governance) จึงเกิดช่องโหว่นี้?**
   - *คำตอบ:* องค์กรขาด **Bitstream Release Governance Policy** ไม่มีการบังคับใช้ลายเซ็นดิจิทัลเข้ารหัส (Cryptographic Signing & eFUSE RoT) เพื่อปฏิเสธการบูตบิตสตรีมที่ไม่ได้รับการรับรอง

---

### แผนผังสาเหตุและผล (Ishikawa Fishbone Diagram)

```
==================================================================================================
                                    ISHIKAWA FISHBONE CAUSE-EFFECT DIAGRAM
==================================================================================================

   MAN (บุคลากร)                                   MACHINE / TOOLS (เครื่องมือ)
   ----------------                                ---------------------------
   วิศวกรส่งไฟล์ Debug ทางแชทส่วนตัว               โรงงานขาด Secure Programming Station
   ช่างเทคนิคนำไฟล์แปลกปลอมไปเบิร์นลงรถ            ชิปไม่ได้เปิดใช้ eFUSE Hardware Root-of-Trust
               \                                                /
                \                                              /
                 \                                            /
                  +------------------------------------------+
                  |                                          |
                  |  ROBOTAXI CRASH & 28M USD PERMIT FREEZE  | ===>> [BUSINESS CRITICAL DISASTER]
                  |                                          |
                  +------------------------------------------+
                 /                                            \
                /                                              \
   METHOD (ระเบียบปฏิบัติ)                          MATERIAL / ENVIRONMENT (สภาวะแวดล้อม)
   ----------------------                          -------------------------------------
   ขาด Bitstream Release Governance               การขับขี่ความเร็วสูงบนทางด่วนต้องการ Low-Latency
   ไม่มีระบบตรวจสอบ Cryptographic Manifest        ไฟล์ทดสอบถูกถอดวงจร Timing & ECC ออก
==================================================================================================
```

---

### คู่มือปฏิบัติการตรวจสอบ OJT หน้างาน: ระเบียบปฏิบัติในการควบคุมการปล่อยบิตสตรีม (Zero-Trust Release SOP)

1. **Step 1: การแบนการโปรแกรมบิตสตรีมด้วยตนเองในสายการผลิต (Absolute Ban on Manual JTAG Programming)**
   - ในโรงงานผลิต ห้ามช่างเทคนิคเปิดคอมพิวเตอร์แล้วกดเบิร์นชิปผ่าน Vivado Hardware Manager เด็ดขาด
   - เครื่องโปรแกรมมิ่งในสายพานผลิตต้องเป็น **Automated Secure Station** ที่ดึงบิตสตรีมจาก Secure Server เท่านั้น
2. **Step 2: การตรวจสอบลายเซ็นดิจิทัลและแฮชก่อนโปรแกรม (Pre-Flash Cryptographic Validation)**
   - สคริปต์ในเครื่องเบิร์นต้องตรวจสอบความสมบูรณ์ของไฟล์:
     $$\text{Calculated\_SHA256}(\text{bitstream.bit}) \stackrel{?}{=} \text{Manifest\_SHA256}$$
   - ตรวจสอบลายเซ็นดิจิทัล RSA-4096 / ECDSA ว่าตรงกับ Public Key ของบริษัทหรือไม่ หากไม่ตรง เครื่องต้องปฏิเสธการเบิร์นทันที
3. **Step 3: การล็อก Hardware Root-of-Trust ผ่าน eFUSE Programming**
   - ในขั้นตอนประกอบชิ้นส่วนสุดท้าย ต้องสั่งเบิร์น eFUSE:
     - เบิร์นกุญแจถอดรหัส AES-256 ลงใน eFUSE Key Registers
     - เบิร์นบิตล็อก `RSA_AUTH_ENABLE` และ `JTAG_DISABLE` เพื่อป้องกันการใช้สาย JTAG เจาะระบบหรืออ่านโค้ดออกจากชิปในอนาคต

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (専門用語)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / อังกฤษ | บริบทการใช้งานเชิงวิศวกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **量産出荷判定** | りょうさんしゅっかはんてい | Ryousan Shukka Hantei | Mass Production Sign-Off | การประชุมอนุมัติขั้นสุดท้ายเพื่อปล่อยผลิตภัณฑ์สู่สายการผลิต |
| **ビットストリーム署名** | ビットストリームしょめい | Bittosutoriimu Shomei | Bitstream Cryptographic Signature | ลายเซ็นดิจิทัลเข้ารหัสเพื่อรับรองความถูกต้องของไฟล์บิตสตรีม |
| **改ざん防止** | かいざんぼうし | Kaizan Boushi | Anti-Tamper / Tamper Resistance | กลไกป้องกันการงัดแงะหรือดัดแปลงแก้ไขวงจรฮาร์ดแวร์ |
| **静的検証承認** | せいてきけんしょうしょうにん | Seiteki Kenshou Shounin | Static Verification Sign-Off | การรับรองความสมบูรณ์ของการวิเคราะห์สถิต (STA, CDC, Lint) |
| **確定版製造データ** | かくていばんせいぞうデータ | Kakuteiban Seizou Deeta | Golden Master Production Data | ข้อมูลการผลิตเวอร์ชันสมบูรณ์แบบที่ล็อกถาวรห้ามแก้ไข |
| **逸脱管理** | いつだつかんり | Itsudatsu Kanri | Deviation / Waiver Governance | ระเบียบการควบคุมและการอนุมัติขอยกเว้นข้อผิดพลาด |
| **暗号化ヒューズ** | あんごうかヒューズ | Angouka Hyuuzu | Cryptographic eFUSE | สะพานฟิวส์ซิลิคอนสำหรับบันทึกกุญแจความลับถาวรบนชิป |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図審議 - Kenzu Shingi)

**สถานที่:** ห้องประชุมใหญ่คณะกรรมการเทคโนโลยีบริหาร (Executive Boardroom - Final Tape-out Sign-off Gate)  
**ผู้เข้าร่วม:**
- **มุราคามิ (村上):** Executive Chief Technology Officer / Principal Sign-off Reviewer (最高技術責任者 / 検図統括役)
- **สิทธิชัย (シッティチャイ):** Senior Principal FPGA Systems Architect (システム設計主席)

---

**村上統括役 (มุราคามิ):**  
「シッティチャイ主席、全200回の過酷な設計・検証プロセス、本当にお疲れ様でした。いよいよ次世代ミッションクリティカルSoC-FPGAの**量産出荷判定（Mass Production Sign-Off）**の最終審議に入ります。準備された**セブン・ゴールデン・ゲート（The Seven Golden Gates）**の完了エビデンスを提示してください。」  
*(คุณสิทธิชัยหัวหน้าสถาปนิกครับ เหน็ดเหนื่อยกับกระบวนการออกแบบและตรวจสอบอันทรหดตลอด 200 บทมามากจริงๆ ในที่สุดเราก็มาถึงการประชุมพิจารณาขั้นสุดท้ายเพื่ออนุมัติปล่อยผลิตจำนวนมาก (Mass Production Sign-Off) ของชิป SoC-FPGA สำหรับภารกิจวิกฤติแล้ว ขอให้แสดงหลักฐานยืนยันความสมบูรณ์ของ 'The Seven Golden Gates' ทั้งหมดมาดูสิครับ)*

**シッティチャイ (สิทธิชัย):**  
「村上統括役、ご報告いたします！
1. **Gate 1 (STA):** 全PVTコーナーにおいてWNS = +120ps、WHS = +45psで完全タイミング収束達成。
2. **Gate 2 (CDC):** SpyGlass CDCにて未承認エラーゼロ件、全交差パスの形式検証完了。
3. **Gate 3 & 4 (Coverage):** 機能カバレッジ100%、ステートマシン遷移100%、そしてDO-254 DAL-A基準のMC/DCカバレッジ100%を完全達成。
4. **Gate 5 (GLS):** Min/MaxコーナーのSDF逆注記シミュレーションにて、グリッチおよびX伝搬ゼロ件を確認済み。
5. **Gate 6 (PDN/Thermal):** ジャンクション温度最高82℃、コア電源リップル1.2%以内を確認。
6. **Gate 7 (Security):** AES-256-GCM暗号化およびRSA-4096署名を施した**確定版製造データ（Golden Master）**を生成し、SHA-256ハッシュ付きマニフェストを作成完了しております。」  
*(ท่านประธานมุราคามิครับ ขอรายงานดังนี้ครับ!
1. Gate 1 (STA): บีบเวลาผ่านทุก PVT corners โดยมี WNS = +120ps และ WHS = +45ps ครบถ้วน
2. Gate 2 (CDC): ไร้ข้อผิดพลาด CDC ตกค้างใน SpyGlass และผ่าน Formal Verification ทุกจุด
3. Gate 3 & 4 (Coverage): ปิด Functional Coverage 100%, FSM 100%, และบรรลุ MC/DC 100% ตามเกณฑ์ DO-254 DAL-A สมบูรณ์
4. Gate 5 (GLS): รัน GLS ทั้ง Min/Max corners โดยปราศจาก Glitch และไม่พบการแพร่กระจายของค่า X
5. Gate 6 (PDN/Thermal): อุณหภูมิสูงสุด 82°C และแรงดันแกนกระเพื่อมไม่เกิน 1.2%
6. Gate 7 (Security): สร้าง Golden Master Bitstream ที่เข้ารหัส AES-256-GCM และลงนาม RSA-4096 พร้อม Release Manifest ที่มีค่าแฮช SHA-256 ครบถ้วนแล้วครับ)*

**村上統括役 (มุราคามิ):**  
「完璧です！寸分の隙もない、まさにエンジニアリングの極致と言えるSign-Offレポートです。手動による現場パッチの混入を防ぐゼロトラスト・パイプラインも完全に機能していますね。この回路は、深宇宙探査でも、自動運転車でも、航空機でも、極限環境で人命とミッションを守り抜くことができると確信しました。」  
*(สมบูรณ์แบบไร้ที่ติ! เป็นรายงาน Sign-Off ที่เรียกได้ว่าเป็นที่สุดของความเป็นเลิศทางวิศวกรรมจริงๆ ครับ ระบบ Zero-Trust Pipeline เพื่อป้องกันไฟล์ Patch แปลกปลอมหน้างานก็ทำงานได้อย่างสมบูรณ์ ผมมั่นใจอย่างยิ่งว่าวงจรนี้ ไม่ว่าจะนำไปใช้ในการสำรวจอวกาศห้วงลึก, ยานยนต์ไร้คนขับ, หรือเครื่องบินพาณิชย์ จะสามารถปกป้องชีวิตมนุษย์และภารกิจในสภาพแวดล้อมสุดขั้วได้อย่างแน่นอน)*

**シッティチャイ (สิทธิชัย):**  
「身に余るお言葉、光栄に存じます！」  
*(เป็นเกียรติอย่างยิ่งสำหรับคำชมเชยนี้ครับ!)*

**村上統括役 (มุราคามิ):**  
「ここに、第200課の集大成として、量産ビットストリームの正式リリース承認印を捺印します！これにて全検証完了、**製造ラインへ直ちにロールアウト（Rollout to Production）**してください！」  
*(ในโอกาสนี้ ในฐานะบทสรุปอันยิ่งใหญ่ของบทเรียนที่ 200 ผมขอประทับตราอนุมัติปล่อยบิตสตรีมเข้าสู่สายการผลิตอย่างเป็นทางการ! ขอประกาศให้การตรวจสอบทั้งหมดเสร็จสิ้นสมบูรณ์ ณ บัดนี้ และจงส่งมอบเข้าสู่สายการผลิตจริงได้ทันที!)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณ Target Impedance ของระบบจ่ายพลังงาน (PDN Design Calculation)

ในการออกแบบโครงข่ายจ่ายพลังงาน (Power Distribution Network: PDN) บนแผงวงจรพิมพ์ (PCB) หลายชั้นสำหรับชิป FPGA ประสิทธิภาพสูง:
- แรงดันไฟเลี้ยงแกนหลัก (Core Voltage): $V_{core} = 0.85\text{ V}$
- ค่าความผันผวนของแรงดันไฟฟ้าสูงสุดที่ยอมรับได้ (Maximum Allowed Ripple Tolerance): $\pm 2.0\%$ (Peak-to-Peak Window = $4.0\%$)
- กระแสไฟฟ้ากระชากชั่วขณะที่เกิดจากการสลับสถานะของ DSP Slices และ BRAM พร้อมกัน (Transient Step Current): $\Delta I_{step} = 17.0\text{ A}$ ในเวลา $2.0\text{ ns}$

จงคำนวณหาค่าอิมพีแดนซ์เป้าหมายสูงสุด (Target Impedance: $Z_{target}$) ของเครือข่าย PDN ที่ความถี่ตั้งแต่ DC ไปจนถึงความถี่เรโซแนนซ์ เพื่อป้องกันไม่ให้แรงดันแกนตกจนชิปเกิดสภาวะ Reset Crash:

- **A)** $Z_{target} \le 1.00\text{ m}\Omega$
- **B)** $Z_{target} \le 2.00\text{ m}\Omega$
- **C)** $Z_{target} \le 4.00\text{ m}\Omega$
- **D)** $Z_{target} \le 10.0\text{ m}\Omega$

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) $Z_{target} \le 2.00\text{ m}\Omega$**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. คำนวณช่วงการแกว่งของแรงดันไฟฟ้าที่ยอมรับได้สูงสุด (Allowed Voltage Ripple Window $\Delta V_{allowed}$):
   - แรงดันแกน $V_{core} = 0.85\text{ V}$
   - กำหนดให้ยอมรับความคลาดเคลื่อน $\pm 2.0\%$ (นั่นคือ จากจุดกึ่งกลางสามารถตกหรือเกินได้ $2\%$):
     $$\Delta V_{allowed} = V_{core} \times 2.0\% = 0.85\text{ V} \times 0.02 = 0.017\text{ V} = 17.0\text{ mV}$$
   (หากคิดแบบ Peak-to-Peak Window เต็มช่วง $4\%$ เพื่อรองรับการสวิงสองฝั่ง จะได้ $34.0\text{ mV}$)
2. ใช้สมการของ Smith & Larry (PDN Target Impedance Formula):
   $$Z_{target} = \frac{\Delta V_{allowed}}{\Delta I_{step}}$$
   แทนค่าตัวเลข:
   $$Z_{target} = \frac{17.0\text{ mV}}{17.0\text{ A}} = \frac{0.017\text{ V}}{17.0\text{ A}} = 0.001\text{ }\Omega \times 2 \approx \mathbf{2.00\text{ m}\Omega}$$
   (สำหรับ Peak-to-Peak Window เต็มช่วง $34\text{ mV} / 17\text{ A} = 2.00\text{ m}\Omega$)
3. **การวิเคราะห์ทางวิศวกรรม:**
   ค่า $Z_{target} \le 2.00\text{ m}\Omega$ เป็นข้อกำหนดที่ท้าทายมาก วิศวกรฮาร์ดแวร์จะต้องจัดวางตัวเก็บประจุแบบเซรามิก (Decoupling Capacitors) ขนาดต่างๆ (0402, 0201) ต่อขนานกันนับร้อยตัว และวางใกล้กับ BGA Pins ใต้ท้องชิปมากที่สุดเพื่อกดเส้นกราฟอิมพีแดนซ์ไม่ให้เกินเส้น $2\text{ m}\Omega$ ตลอดย่านความถี่

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** $1.00\text{ m}\Omega$ คิดบนฐาน Ripple เพียง $\pm 1\%$ ซึ่งเข้มงวดเกินความจำเป็น
- **ข้อ C ผิด:** $4.00\text{ m}\Omega$ จะทำให้แรงดันตกถึง $68\text{ mV}$ ซึ่งเกินขีดจำกัด $\pm 2\%$ และทำให้ทรานซิสเตอร์เกิด Timing Violation ทันที
- **ข้อ D ผิด:** $10.0\text{ m}\Omega$ สูงเกินไปมาก วงจรจะล่มแน่นอนเมื่อเกิดกระแสกระชาก

---

### คำถามที่ 2: การเปรียบเทียบสถาปัตยกรรมความปลอดภัยระดับฮาร์ดแวร์: eFUSE เทียบกับ BBRAM

ในการจัดเก็บกุญแจเข้ารหัส AES-256 (Bitstream Decryption Key) ภายในชิป FPGA สำหรับอุปกรณ์ควบคุมขีปนาวุธป้องกันภัยทางอากาศ (Defense Guidance System):
- ทางเลือกที่ 1: จัดเก็บใน **BBRAM (Battery-Backed RAM)**
- ทางเลือกที่ 2: จัดเก็บใน **eFUSE (Non-Volatile One-Time Programmable Polysilicon Fuse)**

หากเป้าหมายหลักคือการป้องกัน **การโจมตีด้วยการแกะฝาชิปเพื่อส่องกล้องจุลทรรศน์อิเล็กตรอน (Physical Decapping & Scanning Electron Microscope / SEM Inspection)** และป้องกัน **การตกค้างของพลังงานหลังถูกยิงตก (Zeroization upon Tamper Detection)** ทางเลือกใดมีความปลอดภัยตามมาตรฐานความมั่นคงทางทหารสูงสุด?

- **A)** eFUSE ปลอดภัยกว่า เพราะเป็นฟิวส์ถาวร ไม่ต้องพึ่งพาแบตเตอรี่ภายนอก
- **B)** BBRAM ปลอดภัยกว่า เพราะเมื่อเซนเซอร์ตรวจจับการแกะฝาหรือแรงสั่นสะเทือน (Anti-Tamper Sensor) ตรวจพบการบุกรุก วงจรสามารถตัดไฟเลี้ยงและสั่งชอร์ตประจุทิ้งเพื่อล้างกุญแจลับให้กลายเป็นศูนย์ (**Instant Zeroization**) ภายในไม่กี่นาโนวินาที ทำให้ศัตรูไม่สามารถกู้คืนกุญแจได้เลยแม้จะใช้กล้อง SEM ส่อง
- **C)** ทั้งสองทางเลือกมีความปลอดภัยเท่ากัน เพราะใช้กุญแจ 256 บิตเหมือนกัน
- **D)** ห้ามใช้ทั้งสองวิธี ต้องเก็บกุญแจไว้ในแฟลชภายนอก (External SPI Flash) เสมอ

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) BBRAM ปลอดภัยกว่า เพราะเมื่อเซนเซอร์ตรวจจับการแกะฝาหรือแรงสั่นสะเทือน (Anti-Tamper Sensor) ตรวจพบการบุกรุก วงจรสามารถตัดไฟเลี้ยงและสั่งชอร์ตประจุทิ้งเพื่อล้างกุญแจลับให้กลายเป็นศูนย์ (Instant Zeroization) ภายในไม่กี่นาโนวินาที ทำให้ศัตรูไม่สามารถกู้คืนกุญแจได้เลยแม้จะใช้กล้อง SEM ส่อง**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. **จุดอ่อนของ eFUSE ในงานความมั่นคงขั้นสูง (Physical Decapping Vulnerability):**
   - eFUSE ทำงานโดยการยิงกระแสไฟฟ้าแรงดันสูงเพื่อเผาสะพานซิลิไซด์ (Silicide link) ให้ขาดออกจากกัน
   - เมื่อข้าศึกนำชิปไปแช่กรดเพื่อเปิดฝาแพ็กเกจ (Decapping) แล้วส่องด้วยกล้องจุลทรรศน์อิเล็กตรอน (SEM) หรือกล้อง Atomic Force Microscope (AFM) พวกเขาสามารถ **"มองเห็นด้วยตา" (Visual Bit Readout)** ได้ว่าฟิวส์ตัวไหนขาดและตัวไหนต่ออยู่ ทำให้กู้คืนกุญแจ AES-256 ได้สำเร็จ
2. **จุดเด่นของ BBRAM ร่วมกับ Anti-Tamper Zeroization:**
   - BBRAM เก็บข้อมูลในรูปของประจุไฟฟ้าบนเซลล์ SRAM แบบลบเลือนได้ (Volatile Storage) โดยอาศัยแบตเตอรี่เซลล์เหรียญภายนอกหล่อเลี้ยง
   - บนซิลิคอนจะมีวงจรตรวจจับแสง, ตรวจจับอุณหภูมิ, และสายตรวจจับการเจาะเปลือก (Tamper Mesh)
   - ทันทีที่มีการงัดแงะ วงจร **Active Zeroization** จะสั่งลัดวงจรขาไฟเลี้ยงและเขียนทับข้อมูลด้วยศูนย์ทันทีในเวลา $< 10\text{ ns}$
   - เมื่อไม่มีประจุหลงเหลืออยู่ ต่อให้ใช้กล้อง SEM ส่องก็จะไม่พบร่องรอยทางกายภาพใดๆ เลย
3. ดังนั้น สำหรับงานป้องกันการโจรกรรมระดับรัฐหรือการทหาร BBRAM ร่วมกับ Zeroization จึงได้รับมาตรฐาน FIPS 140-3 Level 4 สูงสุด

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** eFUSE สะดวกที่ไม่ต้องใช้แบตเตอรี่ แต่เสี่ยงต่อการถูก Reverse Engineer ทางกายภาพด้วยกล้อง SEM
- **ข้อ C ผิด:** ความยาวกุญแจเท่ากัน แต่ความคงทนต่อการโจมตีทางกายภาพ (Physical Tamper Resistance) ต่างกันคนละชั้น
- **ข้อ D ผิด:** การเก็บกุญแจไว้ในแฟลชภายนอกเป็นการกระทำที่อันตรายที่สุด เพราะศัตรูสามารถดักจับสัญญาณบนสายบัส PCB ได้โดยไม่ต้องแกะชิป

---

### คำถามที่ 3: กฎเหล็กการกำกับดูแล Waiver (CDC & Timing Deviation Governance)

ในการประชุม Mass Production Sign-Off ตามมาตรฐานความปลอดภัยสากล (ISO 26262 ASIL-D และ DO-254 DAL-A) หากทีมออกแบบต้องการขอยกเว้น (Waiver) ข้อผิดพลาด **Clock Domain Crossing (CDC) Violation** ในโมดูลควบคุมความปลอดภัย เงื่อนไขข้อใดต่อไปนี้ที่ **ไม่อนุญาต (STRICTLY FORBIDDEN)** ให้ลงนามอนุมัติ Waiver โดยเด็ดขาด?

- **A)** เส้นทาง CDC นั้นได้รับการพิสูจน์ด้วย Formal Verification แล้วว่าไม่มีทางเกิด Metastability ในทุก Reachable States
- **B)** ขอยกเว้นเนื่องจากเวลาการส่งมอบกระชั้นชิด และทีมงานคาดเดาว่า "ในการทดสอบบนโต๊ะทดลอง 3 วันไม่เคยพบอาการผิดปกติ"
- **C)** มีการเขียนเอกสารวิเคราะห์ผลกระทบด้านความปลอดภัย (FMEA / FMEDA) และมีลายเซ็นรับรองร่วมจาก Chief Safety Officer
- **D)** เส้นทางนั้นเป็นสัญญาณ Quasi-Static Configuration Register ที่ถูกเขียนค่าเพียงครั้งเดียวตอนเปิดเครื่องและมีวงจร Double-Flop กรอง

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) ขอยกเว้นเนื่องจากเวลาการส่งมอบกระชั้นชิด และทีมงานคาดเดาว่า "ในการทดสอบบนโต๊ะทดลอง 3 วันไม่เคยพบอาการผิดปกติ"**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ในมาตรฐานวิศวกรรมความปลอดภัยระดับวิกฤต (Safety-Critical Engineering):
   - **กฎข้อห้ามเด็ดขาด (Cardinal Rule):** "การทดสอบไม่พบข้อผิดพลาด ไม่ได้เป็นหลักฐานพิสูจน์ว่าไม่มีข้อผิดพลาด (Testing proves the presence of bugs, never their absence)"
   - สภาวะ CDC Metastability เป็นปรากฏการณ์ความน่าจะเป็นที่มีค่า MTBF อาจยาวนานนับเดือนหรือนับปี การรันบนโต๊ะแล็บเพียง 3 วันมีความน่าจะเป็นในการตรวจพบต่ำมาก
2. การขอ Waiver โดยอ้างเหตุผลเรื่องกำหนดเวลาส่งมอบ (Schedule Pressure) หรือการคาดเดาส่วนตัว เป็นการละเมิดจริยธรรมวิศวกรรมอย่างร้ายแรง และหากเกิดอุบัติเหตุ ผู้ลงนามจะต้องรับผิดชอบทางกฎหมายอาญา
3. **เงื่อนไขที่อนุญาตให้ Waiver ได้อย่างถูกกฎหมาย:**
   - ข้อ A: มีบทพิสูจน์ทางคณิตศาสตร์แบบ Formal Proof
   - ข้อ C: ผ่านกระบวนการวิเคราะห์ความปลอดภัย FMEA ตามระเบียบ ISO 26262
   - ข้อ D: เป็นสัญญาณแบบคงที่ (Quasi-Static) ที่ได้รับการกรองและจำกัดเวลาการเปลี่ยนแปลงอย่างรัดกุม

ดังนั้น ข้อ B จึงเป็นสิ่งต้องห้ามและยอมรับไม่ได้อย่างเด็ดขาดในระดับ Senior/Principal Engineer!
