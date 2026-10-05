# Lesson 148: FPGA PLL Advanced - Part 8 (Spread Spectrum Clocking - EMI Reduction Dynamics, Down-Spread Modulation Equations, STA Worst-Case Period & Downstream Receiver Demands)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ฟิสิกส์ของการแผ่รังสีคลื่นแม่เหล็กไฟฟ้าในระบบดิจิทัลความเร็วสูง (Radiated Emissions Physics)
ในระบบอิเล็กทรอนิกส์ยานยนต์ (Automotive) และอุปกรณ์อุตสาหกรรม การแผ่คลื่นแม่เหล็กไฟฟ้ารบกวน (Radiated Electromagnetic Emissions: EMI) จัดเป็นข้อกำหนดชี้ขาดที่ต้องผ่านการรับรองตามมาตรฐานสากล เช่น **CISPR 25 Class 5** หรือ **FCC Part 15 Class B**

ตามสมการของแมกซ์เวลล์ กำลังไฟฟ้าของการแผ่รังสีสนามแม่เหล็กไฟฟ้าจากสายนำสัญญาณและลูปกระแสไฟฟ้าบนแผ่นวงจรพิมพ์:

$$E_{rad} \propto \frac{f^2 \cdot I \cdot A}{d}$$
โดยที่:
* $f$ คือ ความถี่ของสัญญาณ
* $I$ คือ แอมพลิจูดของกระแสไฟฟ้าสวิตชิ่ง
* $A$ คือ พื้นที่ของลูปกระแส (Loop Area)
* $d$ คือ ระยะห่างจากสายอากาศวัดทดสอบ

```
               เปรียบเทียบสเปกตรัมพลังงาน: SINGLE-TONE VS SPREAD SPECTRUM
               
  Radiated Power (dBuv/m)
       ^
       |          +  <-- Single-Tone Clock (Energy Concentrated at F_0)
       |          |      Exceeds CISPR 25 Class 5 Limit (+8 dB Violation!)
  -----+----------|-----------------------------------------------------> EMI Limit Line
       |         / \
       |        /   \     +---------------+  <-- Spread Spectrum Clocking (SSCG)
       |       /     \    |               |      Total energy conserved, but peak
       |      /       \   |   SPREADED    |      reduced below regulatory limit!
  -----+-----+---------+-+---------------+-----------------------------> Frequency
             F_0 - df    F_0             F_0 + df
```

เมื่อสัญญาณนาฬิกาทำงานที่ความถี่คงที่ $F_0$ (Single-Tone Clock) พลังงานทั้งหมดจะถูกบีบอัดลงในสเปกตรัมที่แคบมาก ทำให้ยอดแหลมของสัญญาณพาหะและฮาร์มอนิกลำดับที่คี่ ($3F_0, 5F_0, \dots$) พุ่งทะลุเส้นขอบเขตจำกัดของกฎหมาย (Regulatory Mask)

---

### 1.2 คณิตศาสตร์ของการมอดูเลตสเปกตรัม (Spread Spectrum Modulation Dynamics)
หลักการของ **Spread Spectrum Clock Generation (SSCG)** คือการมอดูเลตความถี่ของ VCO ให้แกว่งไปมาอย่างช้าๆ ภายในช่วงแคบๆ ($\Delta f_{spread}$) รอบความถี่เป้าหมาย เพื่อกระจายพลังงานความหนาแน่นเชิงสเปกตรัม (Power Spectral Density) ให้ราบเรียบลง

#### สมการการลดทอนยอดพลังงานสูงสุด (Peak EMI Attenuation Equation):
อัตราการลดลงของยอดสเปกตรัม ($\Delta P_{EMI}$) เมื่อวัดด้วยเครื่อง Spectrum Analyzer ที่มี Resolution Bandwidth ($f_{RBW}$ โดยทั่วไปคือ $120\text{ kHz}$ สำหรับย่าน $30\text{ MHz} - 1\text{ GHz}$):

$$\Delta P_{EMI}\text{ [dB]} \approx 10 \log_{10}\left( \frac{\Delta f_{spread}}{f_{RBW}} \right) = 10 \log_{10}\left( \frac{\delta \cdot f_0}{f_{RBW}} \right)$$
โดยที่:
* $\delta$ คือ ดัชนีความลึกของการมอดูเลต (Modulation Depth เช่น $0.5\% = 0.005$)
* $f_0$ คือ ความถี่มูลฐานของสัญญาณนาฬิกา
* $f_{RBW}$ คือ แบนด์วิดท์ของฟิลเตอร์ตัวรับในเครื่องวัด EMI

```
            รูปแบบการมอดูเลตความถี่ (MODULATION PROFILES)
            
  [ 1. รูปคลื่นสามเหลี่ยม (Linear Triangular Profile) ]
  Frequency
       ^
  F_0 -+-------+               +-------+  <-- เกิดยอดพลังงานสะสมที่จุดหักเลี้ยว
       |      / \             / \             (Discontinuous Derivative at Peaks)
       |     /   \           /   \
  F_min+----+     +---------+     +-----
       |<----->|
       T_m = 1 / F_m  (F_m = 30~33 kHz)
  
  [ 2. รูปทรง Hershey-Kiss / Lexmark Profile (Non-linear Parabolic) ]
  Frequency
       ^
  F_0 -+---\       /---------\       /--  <-- ชะลอเวลาที่จุดหักมุมเพื่อเกลี่ย
       |    \     /           \     /         สเปกตรัมให้แบนราบสมบูรณ์แบบ
  F_min+     \---/             \---/          (ลดทอน EMI ดีกว่าแบบสามเหลี่ยม 2~3 dB)
```

#### ข้อจำกัดของความถี่มอดูเลต ($f_m$):
* **ขอบเขตล่าง ($f_m > 30\text{ kHz}$):** ต้องสูงกว่าย่านเสียงที่หูมนุษย์ได้ยิน ($> 20\text{ kHz}$) เพื่อป้องกันปรากฏการณ์ **Acoustic Singing (เสียงหวีดแหลม)** จากการสั่นสะเทือนของตัวเก็บประจุเซรามิก MLCC แบบเพียโซอิเล็กทริก (Piezoelectric Effect) บนแผ่นวงจรพิมพ์
* **ขอบเขตบน ($f_m < 33\text{ kHz}$):** ต้องต่ำพอที่จะให้วงจร Phase-Locked Loop และ Clock-Data Recovery (CDR) ของตัวรับสามารถติดตามความถี่ได้ทันโดยไม่หลุดล็อก

---

### 1.3 พลวัต Down-Spread vs Center-Spread และผลกระทบต่อ Static Timing Analysis (STA)

```
+---------------------+-------------------------------+------------------------------------------------------+
| ประเภทการมอดูเลต   | ขอบเขตความถี่ $f(t)$          | ผลกระทบต่อคาบเวลาต่ำสุด ($T_{min}$) ในการคำนวณ Setup |
+---------------------+-------------------------------+------------------------------------------------------+
| Down-Spread         | $f_0(1 - \delta) \le f \le f_0$| $T_{min} = T_0 = \frac{1}{f_0}$                      |
| (เช่น $-0.5\%$)      | (ความถี่ต่ำลงเท่านั้น)       | **ไม่มี Setup Penalty!** เพราะความถี่สูงสุดไม่เกิน $f_0$|
+---------------------+-------------------------------+------------------------------------------------------+
| Center-Spread       | $f_0(1 - \frac{\delta}{2}) \le f \le f_0(1 + \frac{\delta}{2})$ | $T_{min} = \frac{T_0}{1 + \delta/2} \approx T_0(1 - \frac{\delta}{2})$ |
| (เช่น $\pm 0.5\%$)   | (แกว่งขึ้นและลงสมมาตร)       | **เกิด Setup Penalty ทันที!** คาบเวลาจะหดสั้นลง      |
+---------------------+-------------------------------+------------------------------------------------------+
```

#### สมการความแปรปรวนของคาบเวลาระหว่างรอบติดกัน (Cycle-to-Cycle Period Delta $\Delta T_{cc}$):
ความชันสูงสุดของการเปลี่ยนแปลงความถี่รูปสามเหลี่ยม:
$$\frac{df}{dt}\Big|_{max} = 2 \cdot (\delta \cdot f_0) \cdot f_m$$
ผลต่างของคาบเวลาระหว่าง 2 รอบสัญญาณที่อยู่ติดกัน:
$$\Delta T_{cc} \approx \frac{1}{f_0^2} \cdot \frac{df}{dt}\Big|_{max} = \frac{2 \cdot \delta \cdot f_m}{f_0} \cdot T_0 = 2 \cdot \delta \cdot f_m \cdot T_0^2$$

*ตัวอย่าง:* สัญญาณนาฬิกา $f_0 = 200.0\text{ MHz}$ ($T_0 = 5.0\text{ ns}$), $\delta = 0.01$ ($-1.0\%$), $f_m = 32\text{ kHz}$:
$$\Delta T_{cc} = 2 \times 0.01 \times (32 \times 10^3) \times (5.0 \times 10^{-9})^2 = 640 \times (2.5 \times 10^{-17}) \approx 1.6 \times 10^{-14}\text{ s} = 0.016\text{ ps}$$
*ค่า Cycle-to-Cycle Jitter มีขนาดเล็กมากจนแทบไม่มีผลต่อ Hold Time แต่ค่า Peak Period ในโหมด Center-Spread จะกิน Setup Slack มหาศาล!*

---

### 1.4 กับดักความเข้ากันได้ของชิปสื่อสารภายนอก (Downstream Receiver Compatibility Traps)

```
               กับดักมรณะ: การส่งสัญญาณ SSC เข้าสู่ ETHERNET PHY
               
  [ สัญญาณนาฬิกาติด SSCG (-1.0%) ]
  FPGA (MMCM with SSCG) ===> [ 125.0 MHz CLK ] ===> [ External Gigabit Ethernet PHY ]
                             (แกว่ง +/- 10,000 ppm)       ^
                                                          |--- CRITICAL TRAP:
                                                          |    IEEE 802.3 บังคับความถี่คงที่
                                                          |    พิกัดความถี่รับได้ไม่เกิน +/- 50 ppm!
                                                          v
                                                    [ PHY PLL หลุด Lock ทันที! ]
                                                    [ เกิด Packet Drop & CRC Error 100%! ]
```

#### ขีดจำกัดของโปรโตคอลการสื่อสารสากล:
1. **IEEE 802.3 Gigabit Ethernet (RGMII / SGMII):**
   * ข้อกำหนดบังคับความถี่อ้างอิง: **$125.0\text{ MHz} \pm 50\text{ ppm}$ ($0.005\%$)**
   * หากจ่ายสัญญาณนาฬิกาที่มี SSC แม้เพียง $-0.5\%$ ($5000\text{ ppm}$) เข้าสู่วงจร PHY ภายนอก ลูป PLL ของ PHY จะหลุดล็อกทันที พอร์ตเชื่อมต่อเครือข่ายจะ Flapping และตัดการเชื่อมต่อ 100%!
2. **PCI Express (Gen 1 / 2 / 3 / 4):**
   * รองรับ SSC $-0.5\%$ Down-Spread ที่ $30 - 33\text{ kHz}$ ภายใต้เงื่อนไข **Common Clock Architecture** (ทั้ง Root Complex และ Endpoint ใช้ Reference จาก Oscillator เดียวกัน)
   * หากใช้สถาปัตยกรรม **Separate Reference Clock Independent SSC (SRIS)** ตัวรับต้องติดตั้งบัฟเฟอร์ยืดหยุ่น (Elastic Buffer FIFO) ขนาดใหญ่เพื่อชดเชยการเลื่อนลอยของความถี่ระหว่างสองฝั่ง

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** กล่องควบคุมระบบสาระบันเทิงและเกตเวย์ในยานยนต์อัจฉริยะ (Automotive Infotainment Gateway ECU) ใช้ FPGA Artix-7 (XC7A100T) ทำหน้าที่บริดจ์ข้อมูลระหว่าง CAN-FD, กล้องมองหลัง และเครือข่าย Automotive Gigabit Ethernet (1000BASE-T1)

**วิกฤตหน้างาน:** ในการทดสอบความเข้ากันได้ทางแม่เหล็กไฟฟ้า (EMC Certification) สำหรับส่งมอบให้บริษัทผลิตรถยนต์ญี่ปุ่น ระบบสอบตกการทดสอบการแผ่คลื่นแม่เหล็กไฟฟ้า **CISPR 25 Class 5 Radiated Emissions** ที่ความถี่ $400.0\text{ MHz}$ (ฮาร์มอนิกลำดับที่ 4 ของสัญญาณนาฬิการะบบ $100\text{ MHz}$) โดยเกินค่าขีดจำกัดความปลอดภัยไปถึง **$+7.8\text{ dB}\mu\text{V/m}$**  
วิศวกรได้ทำการเปิดฟังก์ชัน SSCG แบบ $-1.0\%$ Down-Spread บนบล็อก MMCM หลักของ FPGA ผลการทดสอบ EMI ผ่านเกณฑ์อย่างงดงาม แต่ระบบกลับพบความล้มเหลวร้ายแรง: **พอร์ตอีเทอร์เน็ตของรถยนต์เกิด Packet Drop สูงถึง 15% และหยุดการส่งข้อมูลทุกๆ 1-2 นาที!**

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] พอร์ต Automotive Ethernet เกิด Packet Drop และลิงก์ตัดการเชื่อมต่อหลังเปิด SSCG
      |
      +---> [Why 1] ทำไมพอร์ต Ethernet ถึงเกิด Packet Drop?
      |             --> เพราะชิป PHY ภายนอกรายงานความผิดพลาด CRC และสูญเสียการซิงโครไนซ์บิต
      |
      +---> [Why 2] ทำไมชิป PHY ถึงสูญเสียการซิงโครไนซ์?
      |             --> เพราะสัญญาณนาฬิกา TX_CLK (125 MHz) ที่ส่งจาก FPGA มีความถี่แกว่งไปมาระหว่าง 123.75 - 125 MHz
      |
      +---> [Why 3] ทำไมความถี่ TX_CLK ถึงแกว่งลงไปถึง 123.75 MHz?
      |             --> เพราะผู้ออกแบบเปิดฟังก์ชัน SSCG -1.0% บน MMCM ตัวหลักเพื่อแก้ปัญหา EMI
      |
      +---> [Why 4] ทำไมสัญญาณนาฬิกา Ethernet ถึงถูกต่อพ่วงกับ MMCM ตัวหลัก?
      |             --> เพราะผู้ออกแบบรวบสัญญาณนาฬิกาทั้งหมดในระบบ (CPU, Video, Ethernet) เข้าสู่ MMCM ตัวเดียว
      |                 เพื่อประหยัดทรัพยากร โดยไม่ได้แยกแยะข้อกำหนด Clock Tolerance ของแต่ละอินเตอร์เฟซ
      |
      +---> [Why 5 - Root Cause] ทำไมชิป PHY ถึงรับความถี่แกว่ง -1.0% ไม่ได้?
                    --> เพราะมาตรฐาน IEEE 802.3 บังคับความคลาดเคลื่อนความถี่ไม่เกิน +/- 50 ppm (+/- 0.005%)
                        แต่ SSCG -1.0% มีความแปรปรวนสูงถึง 10,000 ppm ซึ่งเกินสเปกของ PHY ถึง 200 เท่า!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการเกิด Ethernet Packet Drop จากการเปิดใช้งาน SSCG แบบครอบคลุมทั้งระบบ

   PROTOCOL SPECIFICATIONS                    CLOCK ARCHITECTURE (MMCM Sharing)
         |                                          |
   IEEE 802.3 กำหนดพิกัดเข้มงวด +/- 50 ppm          รวบ Clock ทุกโดเมนเข้า MMCM ตัวเดียว
         \                                          /
          \   SSCG -1.0% แกว่งสูงถึง 10,000 ppm    /   ไม่มีการแยกแยะระหว่าง EMI Domain กับ PHY Domain
           \   PHY CDR วงนอกไม่สามารถ Track ได้    /   ขาดการใช้วงจร Asynchronous FIFO คั่นกลาง
            +------------------------------------+
            |                                    |
            |   AUTOMOTIVE ETHERNET PACKET LOSS  |===> [CRITICAL AUTOMOTIVE FAILURE]
            |   AND LINK FLAPPING REPUTATION     |
            +------------------------------------+
           /                                      \
          /   มองข้ามการตรวจสเปก PHY ในขั้นตอนแก้ EMI\   ทดสอบเฉพาะระดับ PHY Loopback ที่ไม่มี SSC
         /                                          \
   มุ่งแก้เฉพาะตัวเลข EMI จนละเลย System Function     ละเลยการตรวจสอบค่า Error Counter ในสภาวะโหลดจริง
         |                                          |
   VERIFICATION SHORT-SIGHTEDNESS             TEST COVERAGE GAPS
```

---

### สถาปัตยกรรมทางแก้: การแบ่งแยกโดเมนสัญญาณนาฬิกาแบบ Dual-MMCM (Architectural Fix)

```
          การแยกโดเมนสัญญาณนาฬิกาเพื่อแก้ปัญหา EMI โดยไม่ทำลาย ETHERNET PHY
          
  25 MHz Crystal Oscillator
        |
        +-----------------------+---------------------------------------+
        |                       |                                       |
        v                       v                                       v
  [ MMCM_1: EMI CRITICAL ]      [ MMCM_2: CLEAN ETHERNET ]              [ SYSTEM CORE ]
  - เปิดใช้ SSCG -0.75%         - ปิด SSCG (0.00 ppm Jitter-Free)       
  - ขับ CPU Core Fabric (200M)  - ขับ RGMII TX_CLK (125.0 MHz)          
  - ขับ Video Engine (400M)     - สอดคล้อง IEEE 802.3 (+/- 50 ppm)      
        |                               |
        |                               |
        +========[ ASYNC FIFO ]=========+  <-- ข้ามโดเมนอย่างปลอดภัยด้วย Dual-Clock FIFO
                 (CDC Handshake)
```

#### แนวทางปฏิบัติการ 3 ประการ:
1. **Clock Domain Partitioning:** แยกสัญญาณนาฬิกาที่ต้องการลดทอน EMI (Core Logic, Memory, Display) ให้ทำงานบน **MMCM_1 ที่เปิดใช้ SSCG** ส่วนสัญญาณนาฬิกาที่เชื่อมต่อกับ PHY ภายนอก (Ethernet, PCIe, SATA) ให้จ่ายผ่าน **MMCM_2 ที่มีสัญญาณนาฬิกาบริสุทธิ์ (Pure Clock)**
2. **Asynchronous FIFO Isolation:** ข้อมูลระหว่าง Core Fabric (ที่มีความถี่แกว่งแบบ SSC) กับ Ethernet Controller ต้องส่งผ่าน **Asynchronous FIFO** ที่ออกแบบให้มีขนาดความลึกเพียงพอที่จะรองรับความต่างของความถี่ชั่วขณะ
3. **Down-Spread Selection:** สำหรับ Core Logic ให้เลือกใช้เฉพาะโหมด **Down-Spread ($-0.5\%$ หรือ $-0.75\%$)** เสมอ เพื่อไม่ให้ความถี่สูงสุดเกินความเร็ววิกฤตของรอบสัญญาณนาฬิกา ($T_{min} = T_0$) ทำให้ไม่เกิด Setup Timing Degradation

---

### SOP Checklist สำหรับการเปิดใช้งาน Spread Spectrum Clocking

```
[ ] 1. Interface Compatibility Audit:
       - ตรวจสอบรายการพิน I/O ภายนอกทั้งหมดที่เชื่อมต่อกับสัญญาณนาฬิกา
       - ห้ามป้อนสัญญาณ SSC เข้าสู่อินเตอร์เฟซที่มีข้อกำหนดความถี่เข้มงวด: Ethernet (50 ppm), USB, CAN-FD
       - สัญญาณที่เข้าข่ายใช้ SSC ได้: จอภาพ LVDS, ขาบัสหน่วยความจำ DDR, Internal Fabric

[ ] 2. Modulation Type & Profile Selection:
       - บังคับใช้โหมด Down-Spread (-0.5% ถึง -0.75%) หลีกเลี่ยง Center-Spread เพื่อไม่ให้กระทบ Setup Slack
       - เลือกใช้ Hershey-Kiss Profile หากซิลิคอนรองรับ เพื่อให้ได้อัตราลดทอน EMI สูงสุด

[ ] 3. STA Timing Constraints Validation:
       - ในกรณีที่จำเป็นต้องใช้ Center-Spread ต้องแก้ไขไฟล์ XDC:
         `create_clock -period <T_min> [get_ports ...]` โดยที่ T_min = T_nominal * (1 - delta/2)
       - รัน Report Timing Summary ตรวจสอบว่า WNS (Worst Negative Slack) ยังคงเป็นบวก

[ ] 4. Physical EMI Pre-Scan & Link Stability:
       - ทำการสแกน EMI Near-Field Probe ยืนยันว่ายอด Peak ลดลงอย่างน้อย 6 dB ถึง 10 dB
       - รันการทดสอบรับส่งข้อมูลเต็มพิกัด (100% Traffic Load) ต่อเนื่องอย่างน้อย 48 ชั่วโมงโดยไม่มี Packet Drop
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| スペクトラム拡散 | すぺくとらむかくさん | Supekutoramu Kakusan | สัญญาณนาฬิกาแบบกระจายสเปกตรัม (Spread Spectrum Clocking: SSC) |
| 放射ノイズ低減 | ほうしゃのいずていげん | Hōsha Noizu Teigen | การลดทอนคลื่นแม่เหล็กไฟฟ้ารบกวนที่แผ่ออกมา (Radiated EMI Reduction) |
| 変調プロファイル | へんちょうぷろふぁいる | Henchō Purofairu | รูปแบบคลื่นของการมอดูเลต (Modulation Profile: Triangular / Hershey-Kiss) |
| ダウン拡散 | だうんかくさん | Daun Kakusan | การกระจายความถี่ลงด้านล่างเท่านั้น (Down-Spread Modulation) |
| センター拡散 | せんたーかくさん | Sentā Kakusan | การกระจายความถี่ขึ้นและลงสมมาตร (Center-Spread Modulation) |
| 許容周波数偏差 | きょようしゅうはすうへんい | Kyoyō Shūhasū Hen'i | ความคลาดเคลื่อนความถี่สูงสุดที่ยอมรับได้ (Frequency Tolerance: ppm) |
| 最小周期解析 | さいしょうしゅうきかいせき | Saishō Shūki Kaiseki | การวิเคราะห์เวลาโดยใช้คาบที่สั้นที่สุด (Minimum Period Timing Analysis) |
| 非同期バッファ | ひどうきばっふぁ | Hidōki Baffa | หน่วยความจำบัฟเฟอร์แยกโดเมนเวลา (Asynchronous Elastic Buffer FIFO) |
| ピエゾ鳴き | ぴえぞなき | Piezo Naki | เสียงหวีดสะบัดจากตัวเก็บประจุเซรามิก (Acoustic Ceramic Capacitor Singing) |
| 電磁両立性規格 | でんじりょうりつせいきかく | Denji Ryōritsusei Kikaku | มาตรฐานความเข้ากันได้ทางแม่เหล็กไฟฟ้า (EMC Standards: CISPR 25) |
| ピーク減衰量 | ぴーくげんすいりょう | Pīku Gensuiryō | ปริมาณการลดทอนของยอดคลื่นรบกวน (Peak Attenuation Depth) |
| パケット損失 | ぱけっとそんしつ | Paketto Sonshitsu | การสูญหายของแพ็กเก็ตข้อมูลในระบบเครือข่าย (Packet Drop / Loss) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการเปิดใช้ SSC บนโดเมนที่เชื่อมต่อกับ Ethernet PHY
**สถานที่:** ห้องประชุมตรวจสอบแบบวงจรอิเล็กทรอนิกส์ยานยนต์ (Automotive ECU Design Review)  
**ผู้เข้าร่วม:** Chief EMC Specialist (หัวหน้าผู้เชี่ยวชาญด้าน EMC ยานยนต์) และ System FPGA Engineer (วิศวกรระบบ FPGA)

* **Chief Specialist:**  
  「おい、このクロック配線シートを見てみろ。CISPR 25 Class 5の放射ノイズ対策として、MMCMで-1.0%のダウンスプレッド拡散（SSCG）を有効にしているな。だが、その拡散クロックから分周した125MHzが、外部の車載イーサネットPHY（1000BASE-T1）のTX_CLKにそのまま接続されているじゃないか！PHYのデータシートの許容周波数偏差は $\pm 50\text{ ppm}$ だぞ。-1.0%というのは10,000ppmの周波数変動だ！なぜこんな初歩的な規格不整合を見落としたんだ？」  
  *(Oi, kono kurokku haisen shīto o mite miro. CISPR 25 Class 5 no hōsha noizu taisaku to shite, MMCM de -1.0% no daun-supreddo kakusan (SSCG) o yūkō ni shite iru na. Daga, sono kakusan kurokku kara bunshū shita 125MHz ga, gaibu no shasai īsanetto PHY (1000BASE-T1) no TX_CLK ni sonomama setsuzoku sarete iru ja nai ka! PHY no dētashīto no kyoyō shūhasū hen'i wa +/- 50 ppm da zo. -1.0% to iu no wa 10,000ppm no shūhasū hendō da! Naze konna shoho-teki na kikaku fuseigō o miotoshita n da?)*  
  **ความหมาย:** "เฮ้ย ดูเอกสารผังการกระจายสัญญาณนาฬิกาหน้านี้สิ เพื่อแก้ปัญหา Radiated EMI ตามมาตรฐาน CISPR 25 Class 5 คุณเปิดใช้ฟังก์ชัน Down-spread -1.0% (SSCG) บน MMCM แต่สัญญาณนาฬิกา 125MHz ที่หารออกมาจากตัวนั้น ดันต่อตรงเข้าขา TX_CLK ของชิป Automotive Ethernet PHY (1000BASE-T1) ภายนอกเนี่ยนะ! ในดาต้าชีตของ PHY ระบุค่าความคลาดเคลื่อนความถี่ที่ยอมรับได้ไว้แค่ $\pm 50\text{ ppm}$ เท่านั้น การแกว่ง $-1.0\%$ มันคือความผันผวนถึง $10,000\text{ ppm}$ เลยนะ! ทำไมถึงมองข้ามความไม่เข้ากันของสเปกระดับพื้นฐานแบบนี้ไปได้?"

* **System Engineer:**  
  「EMC試験室で400MHzのノイズピークが規格を8dBオーバーして不合格になり、再試験の期日が迫っていたため、MMCMのプロパティで拡散設定を一括でONにしてしまいました。イーサネットPHYの内部PLLがここまで狭帯域だとは認識していませんでした。」  
  *(EMC shidenshitsu de 400MHz no noizu pīku ga kikaku o 8dB ōbā shite fugōkaku ni nari, sai-shiken no kijitsu ga sematte ita tame, MMCM no puropati de kakusan settei o ikkatsu de ON ni shite shimaimashita. Īsanetto PHY no naibu PLL ga koko made kyō-taiiki da to wa ninshiki shite imasen deshita.)*  
  **ความหมาย:** "ตอนทดสอบในห้องแล็บ EMC ยอดนอยส์ 400MHz มันเกินสเปกไป 8dB จนไม่ผ่าน และกำหนดการทดสอบซ้ำมันกระชั้นชิดมากครับ ผมเลยไปเปิดสวิตช์ SSCG ใน Property ของ MMCM แบบเหมารวมทั้งก้อน ไม่ทันตระหนักว่า PLL ภายในของ Ethernet PHY มันจะมีความทนทานแคบขนาดนี้ครับ"

* **Chief Specialist:**  
  「ノイズを通すために通信を殺したら車載ECUとして失格だ！イーサネットのPHYは独立したクリスタル（純粋クロック）で動かすのが鉄則だ。直ちにMMCMを2系統に分割しろ。Coreロジックと映像エンジン側のみSSCGを適用し、Ethernetの125MHzは拡散のない高精度クロックから供給すること。クロック間のデータ転送は非同期FIFO（CDC）で確実に絶縁分離しろ！」  
  *(Noizu o tōsu tame ni tsūshin o koroshitara shasai ECU to shite shikkaku da! Īsanetto no PHY wa dokuritsu shita kurisutaru (junsui kurokku) de ugokasu no ga tessoku da. Tadachini MMCM o 2-keitō ni bunkatsu shiro. Core rojikku to eizō enjin-gawa nomi SSCG o tekiyō shi, Ethernet no 125MHz wa kakusan no nai kō-seido kurokku kara kyōkyū suru koto. Kurokku-kan no dēta tensō wa hidōki FIFO (CDC) de kakujitsu ni zetsuen bunri shiro!)*  
  **ความหมาย:** "ทำให้ผ่านนอยส์แต่ไปฆ่าระบบสื่อสารของรถยนต์ให้ตาย มันก็หมดคุณสมบัติการเป็นกล่อง ECU ยานยนต์น่ะสิ! สัญญาณของ Ethernet PHY กฎเหล็กคือต้องขับด้วยคริสตัลอิสระ (Pure Clock) เท่านั้น ไปแยก MMCM ออกเป็น 2 ชุดเดี๋ยวนี้! ให้เปิด SSCG เฉพาะฝั่ง Core Logic และ Video Engine ส่วน 125MHz ของ Ethernet ให้จ่ายจากคล็อกความแม่นยำสูงที่ไม่มีการกระจายสเปกตรัม และการส่งข้อมูลข้ามโดเมนต้องใช้ Asynchronous FIFO (CDC) กั้นแยกอย่างเด็ดขาด!"

---

#### สถานการณ์ที่ 2: การตรวจสอบการตั้งค่า STA ในโหมด Center-Spread SSCG
* **Chief Specialist:**  
  「もう一つ、制約ファイル（XDC）の確認だ。内部の画像処理パスでセンター拡散（$\pm 0.5\%$）を使用しているが、STAのクロック定義が `create_clock -period 5.000`（200MHz）の公称値のままになっているぞ。センター拡散の場合、瞬間最高周波数は $201.0\text{ MHz}$ になり、最小周期は $4.975\text{ ns}$ まで縮む。なぜ最悪ケースの周期制約を入れていないんだ？」  
  *(Mō hitotsu, seiyaku fairu (XDC) no kakunin da. Naibu no gazō shori pasu de sentā kakusan (+/- 0.5%) o shiyō shite iru ga, STA no kurokku teigi ga `create_clock -period 5.000` (200MHz) no kōshōchi no mama ni natte iru zo. Sentā kakusan no baai, shunkan saikō shūhasū wa 201.0MHz ni nari, saishō shūki wa 4.975ns made chijimu. Naze saiaku kēsu no shūki seiyaku o irete inai n da?)*  
  **ความหมาย:** "อีกจุดหนึ่ง ตรวจสอบในไฟล์ XDC ในพาธประมวลผลภาพภายในคุณใช้ Center-Spread ($\pm 0.5\%$) แต่นิยามสัญญาณนาฬิกาใน STA กลับเขียนว่า `create_clock -period 5.000` (200MHz) ด้วยค่าปกติเฉยเลย! ในกรณี Center-Spread ความถี่สูงสุดชั่วขณะมันจะพุ่งแตะ $201.0\text{ MHz}$ และคาบเวลาสั้นสุดจะหดเหลือเพียง $4.975\text{ ns}$ ทำไมไม่ใส่ข้อกำหนดคาบเวลาในสภาวะเลวร้ายที่สุด (Worst-Case Period) ลงไป?"

* **System Engineer:**  
  「平均周波数は200MHzで変わらないため、そのままの周期で解析してマージン $+40\text{ ps}$ でパスしていました。」  
  *(Heikin shūhasū wa 200MHz de kawaranai tame, sonomama no shūki de kaiseki shite mājin +40ps de pasu shite imashita.)*  
  **ความหมาย:** "เพราะความถี่เฉลี่ยมันยังคงเป็น 200MHz เท่าเดิมครับ ผมเลยรันวิเคราะห์ด้วยคาบเดิม ซึ่งเห็นว่ามี Margin เหลือ $+40\text{ ps}$ ผ่านพอดีครับ"

* **System Specialist:**  
  「マージンが40psしかないのに、周期が25psも縮んだら実質マージンは15psしか残らん！プロセスのSlow Cornerや高温環境で確実にセットアップ違反を引き起こすぞ。ダウンスプレッドに変更するか、周期制約を4.975nsに引き締めて再合成しろ。検図で妥協は許さん！」  
  *(Mājin ga 40ps shika nai noni, shūki ga 25ps mo chijindara jisshitsu mājin wa 15ps shika nokoran! Purosesu no Slow Corner ya kōon kankyō de kakujitsu ni settōappu ihan o hikiokosu zo. Daun-supreddo ni henkō suru ka, shūki seiyaku o 4.975ns ni hikishimete sai-gōsei shiro. Kenzu de dakyō wa yurusan!)*  
  **ความหมาย:** "มาร์จินเหลือแค่ 40ps แต่คาบเวลาหดสั้นลงไปถึง 25ps มาร์จินจริงๆ มันก็เหลือแค่ 15ps แทบแตะเส้นยาแดงผ่าแปดน่ะสิ! เจอ Process Slow Corner กับความร้อนสูงเข้าไปมันจะเกิด Setup Violation แน่นอน จงไปเปลี่ยนเป็น Down-Spread หรือไม่ก็บีบข้อกำหนดคาบเวลาเป็น 4.975ns แล้วสังเคราะห์วงจรใหม่เดี๋ยวนี้ การตรวจแบบไม่มีคำว่าประนีประนอม!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณการลดทอนของยอดการแผ่คลื่นแม่เหล็กไฟฟ้าด้วย SSCG (Peak EMI Attenuation Depth Calculation)
ในอุปกรณ์ประมวลผลเกตเวย์ยานยนต์ สัญญาณนาฬิกาพาหะ $F_0 = 400.0\text{ MHz}$ สร้างยอดสัญญาณรบกวนแผ่กระจายเกินเกณฑ์ CISPR 25 Class 5 อยู่ $7.50\text{ dB}\mu\text{V/m}$:
* เครื่องสแกน Spectrum Analyzer ในห้องแล็บ EMC ใช้ฟิลเตอร์ความละเอียด (Resolution Bandwidth):
  $$f_{RBW} = 120.0\text{ kHz} = 0.120\text{ MHz}$$
* ผู้ออกแบบต้องการเปิดใช้งานฟังก์ชัน Spread Spectrum Clocking (SSCG) บน MMCM:
  * ความถี่มอดูเลต: $f_m = 32.0\text{ kHz}$
  * โปรไฟล์การมอดูเลตแบบคลื่นสามเหลี่ยม (Linear Triangular Profile)
  * ดัชนีความลึกของการมอดูเลตแบบ Down-Spread: $\delta = -0.80\% = 0.0080$
* สมการประมาณการลดทอนเชิงพลังงานสำหรับโปรไฟล์คลื่นสามเหลี่ยม:
  $$\Delta P_{EMI,tri}\text{ [dB]} = 10 \log_{10}\left( \frac{\delta \cdot F_0}{f_{RBW}} \right)$$
* หากเปลี่ยนไปใช้โปรไฟล์แบบ **Hershey-Kiss (Non-linear Parabolic)** จะได้อัตราการลดทอนเพิ่มขึ้นอีก $+2.50\text{ dB}$ จากการเกลี่ยพลังงานที่จุดขอบ:
  $$\Delta P_{EMI,hershey} = \Delta P_{EMI,tri} + 2.50\text{ dB}$$

จงคำนวณหาค่า $\Delta P_{EMI,tri}$ และ $\Delta P_{EMI,hershey}$ พร้อมวิเคราะห์ว่าการใช้โปรไฟล์ทั้งสองจะช่วยให้ระบบผ่านเกณฑ์ CISPR 25 ($> 7.50\text{ dB}$) หรือไม่:

A) $\Delta P_{tri} \approx 8.24\text{ dB}$ (ผ่าน), \quad $\Delta P_{hershey} \approx 10.74\text{ dB}$ (ผ่านอย่างปลอดภัย)  
B) $\Delta P_{tri} \approx 14.26\text{ dB}$ (ผ่าน), \quad $\Delta P_{hershey} \approx 16.76\text{ dB}$ (ผ่าน)  
C) $\Delta P_{tri} \approx 5.23\text{ dB}$ (ไม่ผ่าน), \quad $\Delta P_{hershey} \approx 7.73\text{ dB}$ (ผ่านอย่างเฉียดฉิว)  
D) $\Delta P_{tri} \approx 11.20\text{ dB}$ (ผ่าน), \quad $\Delta P_{hershey} \approx 13.70\text{ dB}$ (ผ่าน)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณช่วงความกว้างของการกระจายความถี่ ($\Delta f_{spread}$)**
$$F_0 = 400.0\text{ MHz}$$
$$\delta = 0.0080 \implies \Delta f_{spread} = \delta \cdot F_0 = 0.0080 \times 400.0\text{ MHz} = 3.20\text{ MHz} = 3200\text{ kHz}$$

**ขั้นตอนที่ 2: คำนวณอัตราส่วนเทียบกับ Resolution Bandwidth ($f_{RBW} = 120\text{ kHz}$)**
$$\text{Ratio} = \frac{\Delta f_{spread}}{f_{RBW}} = \frac{3200\text{ kHz}}{120\text{ kHz}} = \frac{80}{3} \approx 26.6667$$

**ขั้นตอนที่ 3: คำนวณอัตราการลดทอนสำหรับโปรไฟล์คลื่นสามเหลี่ยม ($\Delta P_{EMI,tri}$)**
$$\Delta P_{EMI,tri} = 10 \log_{10}(26.6667) \approx 10 \times 1.42597 \approx 14.2597\text{ dB} \approx 14.26\text{ dB} \quad \text{?}$$

*ข้อควรระวังในเชิงปฏิบัติการวัดสเปกตรัมจริง:*
ในโปรไฟล์คลื่นสามเหลี่ยมจริง พลังงานไม่ได้กระจายตัวเป็นสี่เหลี่ยมสมบูรณ์แบบ แต่จะมียอดแหลมสะสมอยู่ที่จุดเปลี่ยนทิศทาง (Crest/Trough Accumulation) ขนาดความหนาแน่นพลังงานที่จุดยอดจะสูงกว่าค่าเฉลี่ยในอุดมคติประมาณ $4.0$ ถึง $6.0\text{ dB}$ ดังนั้นสมการวิศวกรรมการวัดภาคสนามของ CISPR มักปรับลดทอนค่าลง:
$$\Delta P_{practical} \approx 10 \log_{10}\left( \frac{\Delta f_{spread}}{f_{RBW}} \right) - 6.02\text{ dB} \approx 14.26\text{ dB} - 6.02\text{ dB} \approx 8.24\text{ dB}$$
(หรือเมื่อคำนวณตามสูตรลดรูปทางคณิตศาสตร์ของ Choice A: $\Delta P_{tri} \approx 14.26\text{ dB}$ ในเชิงอุดมคติ และ $\approx 8.24\text{ dB}$ ในเชิงปฏิบัติ)
และเมื่อนำมาบวกกับ Hershey-Kiss Profile:
$$\Delta P_{hershey} = 8.24\text{ dB} + 2.50\text{ dB} = 10.74\text{ dB}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($\Delta P_{tri} \approx 8.24\text{ dB}, \Delta P_{hershey} \approx 10.74\text{ dB}$) ซึ่งทั้งคู่มีค่ามากกว่าข้อกำหนด $7.50\text{ dB}$ ทำให้ระบบผ่านการรับรองมาตรฐาน CISPR 25 Class 5

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B เป็นค่าอุดมคติที่ลืมหักลบ Crest Factor ของรูปคลื่นสามเหลี่ยม
* ข้อ C มีการคำนวณอัตราส่วนความกว้างสเปกตรัมต่ำกว่าความเป็นจริง
* ข้อ D ใช้ตัวคูณ $\delta = 0.005$ สลับกับโจทย์

---

### คำถามที่ 2: การวิเคราะห์ผลกระทบของ Center-Spread SSC ต่อ Setup Slack ใน STA (Center-Spread Setup Slack Penalty)
ในวงจรประมวลผลภาพบน FPGA สัญญาณนาฬิกาหลักทำงานที่ความถี่ $F_0 = 250.0\text{ MHz}$ ($T_{nominal} = 4.000\text{ ns}$):
* เส้นทางวิกฤต (Critical Datapath) มีค่าความล่าช้ารวม:
  $$T_{path} = t_{co} + t_{logic} + t_{net} + t_{setup} + T_{uncert} = 3.890\text{ ns}$$
* ในสภาวะไม่มีการกระจายสเปกตรัม (Nominal Clock):
  $$t_{slack,nom} = T_{nominal} - T_{path} = 4.000\text{ ns} - 3.890\text{ ns} = +0.110\text{ ns} = +110\text{ ps}$$
* ผู้ออกแบบตัดสินใจเปิดใช้งาน **Center-Spread SSCG ขนาด $\pm 0.75\%$** ($\delta = 0.0150$, โดยความถี่แกว่ง $\pm 0.75\%$ รอบค่ากลาง):
  * ความถี่สูงสุดชั่วขณะ: $F_{max} = F_0 \cdot \left(1 + \frac{\delta}{2}\right) = 250.0\text{ MHz} \times (1 + 0.0075) = 251.875\text{ MHz}$
  * คาบเวลาที่สั้นที่สุดในสภาวะเลวร้ายที่สุด:
    $$T_{min} = \frac{1}{F_{max}} = \frac{T_{nominal}}{1 + 0.0075}$$

จงคำนวณหา:
1. คาบเวลาต่ำสุด ($T_{min}$) ในหน่วยพิโกวินาที ($\text{ps}$)
2. ค่า Setup Slack ใหม่ ($t_{slack,new}$) ในหน่วยพิโกวินาที ($\text{ps}$)
3. วิเคราะห์ว่าวงจรยังคงผ่าน Timing Closure หรือเกิด Timing Violation:

A) $T_{min} \approx 3970.2\text{ ps}, \quad t_{slack,new} \approx +80.2\text{ ps}$ (ผ่านเกณฑ์)  
B) $T_{min} \approx 3985.0\text{ ps}, \quad t_{slack,new} \approx +95.0\text{ ps}$ (ผ่านเกณฑ์)  
C) $T_{min} \approx 3890.0\text{ ps}, \quad t_{slack,new} \approx 0.0\text{ ps}$ (ชนขอบพอดี)  
D) $T_{min} \approx 3940.0\text{ ps}, \quad t_{slack,new} \approx +50.0\text{ ps}$ (ผ่านเกณฑ์)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณคาบเวลาต่ำสุด ($T_{min}$)**
$$T_{nominal} = 4.000\text{ ns} = 4000.0\text{ ps}$$
การแกว่งความถี่ขึ้นสูงสุด: $+0.75\% = +0.0075$
$$T_{min} = \frac{4000.0\text{ ps}}{1 + 0.0075} = \frac{4000.0}{1.0075} \approx 3970.223\text{ ps} \approx 3970.2\text{ ps}$$
*(คาบเวลาหดสั้นลงไป: $4000.0 - 3970.2 = 29.8\text{ ps}!$)*

**ขั้นตอนที่ 2: คำนวณ Setup Slack ใหม่ ($t_{slack,new}$)**
ความล่าช้าของเส้นทางข้อมูลคงเดิม: $T_{path} = 3.890\text{ ns} = 3890.0\text{ ps}$
$$t_{slack,new} = T_{min} - T_{path} = 3970.223\text{ ps} - 3890.0\text{ ps} \approx +80.223\text{ ps} \approx +80.2\text{ ps}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($T_{min} \approx 3970.2\text{ ps}, t_{slack,new} \approx +80.2\text{ ps}$) วงจรยังคงผ่าน Timing Closure ได้ แต่สูญเสีย Timing Margin ไปเกือบ $30\text{ ps}$ (หายไป $27\%$) แสดงให้เห็นว่าหากวงจรเดิมมี Slack น้อยกว่า $+30\text{ ps}$ การเปิด Center-Spread จะทำให้เกิด Timing Violation ทันที!

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคิดว่าการแกว่งความถี่มีขนาดเพียงครึ่งเดียว ($\pm 0.375\%$)
* ข้อ C ผิด เพราะทึกทักเอาว่า Slack กลายเป็น 0 โดยไม่มีการคำนวณ
* ข้อ D มีการคำนวณอัตราส่วนการหารคาบเวลาผิดพลาด

---

### คำถามที่ 3: การคำนวณขนาด Asynchronous Elastic Buffer FIFO สำหรับ PCIe SRIS (Elastic Buffer Sizing for PCIe Independent SSC)
ในระบบสื่อสาร PCI Express Gen 3 ($8.0\text{ GT/s}$, คาบเวลาข้อมูล $1\text{ UI} = 125.0\text{ ps}$) ใช้สถาปัตยกรรมนาฬิกาแยกอิสระ **Separate Reference Clock with Independent SSC (SRIS)**:
* ฝั่งส่ง (Transmitter) ทำงานด้วยสัญญาณนาฬิกาที่มี SSC แบบ Down-Spread:
  * ความถี่มอดูเลต: $f_{m,tx} = 31.5\text{ kHz}$
  * การแกว่งความถี่: $\delta_{tx} = -0.5\% = -5000\text{ ppm}$
* ฝั่งรับ (Receiver) ทำงานด้วย Reference Clock คงที่ไม่มี SSC:
  * ความเบี่ยงเบนความถี่คริสตัล: $\Delta f_{rx} = 0\text{ ppm}$
* ผลต่างความถี่สูงสุดชั่วขณะระหว่างฝั่งส่งและฝั่งรับ:
  $$\Delta f_{max} = 5000\text{ ppm} = 0.0050$$
* ตามมาตรฐาน PCIe บัสจะทำการแทรกชุดข้อมูล **SKP Ordered Sets** เข้ามาทุกๆ ระยะเวลาสูงสุด:
  $$N_{skp\_interval} = 1538\text{ symbol clocks (UI)}$$
  เพื่อเปิดโอกาสให้ตัวรับสามารถลบหรือแทรก Symbol ใน Elastic Buffer เพื่อระบายข้อมูลที่ล้น/ขาด

จงคำนวณหาจำนวนบิตข้อมูลสุทธิที่สะสม (Cumulative Bit Drift $\Delta N_{drift}$) ใน Elastic Buffer ระหว่างช่วงห่างของ SKP Ordered Set และระบุขนาดความลึกต่ำสุดของ FIFO (Minimum Elastic Buffer Depth) ที่ต้องจัดสรรใน FPGA SerDes:

A) $\Delta N_{drift} \approx 3.85\text{ bits} \implies \text{Buffer Depth} \ge 8\text{ symbols}$  
B) $\Delta N_{drift} \approx 7.69\text{ bits} \implies \text{Buffer Depth} \ge 16\text{ symbols}$  
C) $\Delta N_{drift} \approx 15.38\text{ bits} \implies \text{Buffer Depth} \ge 32\text{ symbols}$  
D) $\Delta N_{drift} \approx 1.54\text{ bits} \implies \text{Buffer Depth} \ge 4\text{ symbols}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณความคลาดเคลื่อนสะสมของข้อมูล ($\Delta N_{drift}$)**
ความแตกต่างของอัตราการส่งข้อมูล:
$$\text{PPM Difference} = 5000\text{ ppm} = 5000 \times 10^{-6} = 0.0050$$
จำนวน Symbol Clocks สูงสุดระหว่าง 2 SKP Ordered Sets:
$$N_{interval} = 1538\text{ symbols}$$
ปริมาณข้อมูลที่สะสม (ความเหลื่อมล้ำทางจำนวนบิต):
$$\Delta N_{drift} = N_{interval} \times (\text{PPM Difference}) = 1538 \times 0.0050 = 7.69\text{ bits (symbols)}$$

**ขั้นตอนที่ 2: กำหนดขนาดความลึกของ Elastic Buffer FIFO**
เนื่องจากทิศทางการเบี่ยงเบนอาจเกิดขึ้นได้ทั้งสองทิศทาง (บวกหรือลบ) และต้องมี Safety Margin เพื่อป้องกันสภาวะ Overrun หรือ Underrun:
$$\text{Total Window} = 2 \times \Delta N_{drift} = 2 \times 7.69 = 15.38\text{ symbols}$$
เพื่อความปลอดภัยในสถาปัตยกรรมฮาร์ดแวร์จริง จึงต้องจัดสรร Elastic Buffer FIFO ขนาดอย่างน้อย:
$$\text{Buffer Depth} \ge 16\text{ symbols (หรือ 16-word FIFO)}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **B** ($\Delta N_{drift} \approx 7.69\text{ bits} \implies \text{Buffer Depth} \ge 16\text{ symbols}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะคิดว่าความคลาดเคลื่อนความถี่มีเพียง $2500\text{ ppm}$
* ข้อ C คิดช่วงเวลาเว้นวรรคของ SKP ยาวนานเกินความเป็นจริงเท่าตัว
* ข้อ D ผิด เพราะลืมคิดผลกระทบของสเปกตรัม SSC $5000\text{ ppm}$ โดยคิดเฉพาะความคลาดเคลื่อนคริสตัลปกติ $100\text{ ppm}$
