# Lesson 146: FPGA PLL Advanced - Part 6 (Jitter Analysis and Mitigation - Intrinsic/Extrinsic Jitter, Dual-Dirac Model, Ferrite Bead Power Filters & Dedicated Clock Pin Topology MRCC/SRCC)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมทางกายภาพของสัญญาณรบกวนในบล็อก PLL (Silicon Physics of Jitter Generation)
ในระดับ Senior FPGA Engineer การทำความเข้าใจเกี่ยวกับ Phase-Locked Loop ไม่ใช่เพียงแค่การเลือกตัวคูณ ($M$) และตัวหาร ($D$) เพื่อให้ได้ความถี่ที่ต้องการ แต่คือการควบคุมและลดทอน **สัญญาณรบกวนทางเวลา (Jitter: ジッタ)** เพื่อรักษาหน้าต่างเวลา (Timing Margin) ให้เพียงพอต่อการปิด Timing Closure ในระบบความเร็วสูง

```
                  แหล่งกำเนิดและกลไกการแทรกซึมของ JITTER ใน FPGA PLL
                  
  [ EXTRINSIC NOISE: ภายนอกชิป ]                      [ INTRINSIC NOISE: ภายในซิลิคอน ]
  +--------------------------+                         +-------------------------------+
  | Switching Power Ripple   |                         | Thermal Noise (Johnson-Nyquist)|
  | (Buck Converter 1~3 MHz) |                         | Shot Noise in Charge Pump     |
  +-------------+------------+                         | Flicker Noise (1/f) in VCO    |
                |                                      +---------------+---------------+
                v                                                      |
    [ VCCAUX / VCC_PLL Pin ]                                           |
                |                                                      |
                +------------------------+                             |
                                         v                             v
  [ CLKIN Pin ] =====> [ PFD ] ===> [ CHARGE PUMP ] ===> [ LOOP FILTER ] ===> [ VCO CORE ] ===> CLKOUT
  (Input Jitter)         ^                                                        |
                         |================ [ FEEDBACK /M ] =======================+
                                         (Substrate Noise Coupling)
```

#### การจำแนกประเภทของสัญญาณรบกวนตามแหล่งกำเนิด:
1. **Intrinsic Jitter (สัญญาณรบกวนภายใน):**
   * **Thermal Noise (Johnson-Nyquist Noise):** เกิดจากการเคลื่อนที่แบบสุ่มของอิเล็กตรอนในสารกึ่งตัวนำซิลิคอน มีสเปกตรัมแบบ White Noise สม่ำเสมอ
   * **Shot Noise:** เกิดจากการข้ามรอยต่อ p-n junction ของประจุไฟฟ้าในทรานซิสเตอร์ของ Charge Pump
   * **Flicker Noise ($1/f$ Noise):** สัญญาณรบกวนย่านความถี่ต่ำที่เกิดจากการดักจับประจุที่รอยต่อ $\text{Si-SiO}_2$ ในเกตของ MOSFET ซึ่ง VCO จะผสมความถี่นี้ขึ้นมาเป็น Phase Noise ใกล้สัญญาณพาหะ (Close-in Phase Noise)
2. **Extrinsic Jitter (สัญญาณรบกวนภายนอก):**
   * **Power Supply Ripple:** สัญญาณสลับขั้วจากวงจร Buck Converter ภายนอก ($1.0 - 3.0\text{ MHz}$) แทรกซึมเข้าสู่เรล $V_{CCAUX}$ หรือ $V_{CC\_PLL}$
   * **Substrate Noise Coupling:** การสลับสถานะพร้อมกันของลอจิกขนาดใหญ่ (Simultaneous Switching Outputs: SSO) เช่น บัสหน่วยความจำหรือ DSP Slice นับพันตัว ส่งกระแสกระชากผ่าน Substrate เข้าไปกวนตัวเก็บประจุใน Loop Filter
   * **Crosstalk & I/O Coupling:** สัญญาณรบกวนจากการเหนี่ยวนำแม่เหล็กไฟฟ้าระหว่างลายวงจรที่อยู่ใกล้เคียงบน PCB หรือภายในแพ็กเกจ BGA

---

### 1.2 โทโพโลยีพินสัญญาณนาฬิกาเฉพาะกิจ MRCC vs SRCC vs HDGC (Clock Pin Routing Physics)

หนึ่งในความผิดพลาดที่ร้ายแรงที่สุดของวิศวกรคือการนำสัญญาณ Reference Clock ต่อเข้ากับพินทั่วไป (General-Purpose I/O: GPIO) แล้วต่อสายผ่าน Fabric Routing ภายในเข้าสู่ MMCM/PLL:

```
          การเปรียบเทียบการเดินสายสัญญาณนาฬิกา: DEDICATED PIN VS GENERAL I/O
          
  [ ห้ามทำเด็ดขาด: General Purpose I/O -> Fabric Routing ]
  CLKIN Pin (GPIO) ---> [ IBUF ] ---> [ Fabric Interconnect Routing ] ---> [ MMCM CLKIN ]
                                       ^                            ^
                                       |--- DANGER: RC Delay แปรผันตามอุณหภูมิ!
                                       |--- DANGER: โดน Crosstalk จากลอจิกข้างเคียงกวน!
                                       |--- ผลลัพธ์: Dynamic Jitter เพิ่มขึ้น 250 ~ 500 ps!
  
  [ มาตรฐาน Senior Engineer: Dedicated Clock Pin -> Hard Track ]
  CLKIN Pin (MRCC/SRCC) -> [ IBUFDS ] ===> [ Dedicated Hard Routing Track ] ===> [ MMCM CLKIN ]
                                            (Controlled Impedance, Zero Fabric Crosstalk)
                                            (Routing Jitter < 15 ps!)
```

#### ประเภทของ Dedicated Clock Pins ใน FPGA ตระกูล UltraScale / UltraScale+:
1. **Multi-Region Clock Capable (MRCC):**
   * พินฮาร์ดแวร์พิเศษที่มีลายวงจรเฉพาะเชื่อมต่อเข้าสู่ Clock Management Tile (CMT) โดยตรง
   * สามารถขับข้ามไปยัง Clock Region อื่นๆ ทั้งในแนวระนาบและแนวดิ่งได้โดยไม่สูญเสียคุณภาพสัญญาณ
   * มีค่า Insertion Jitter ต่ำที่สุด ($< 10 - 15\text{ ps}$)
2. **Single-Region Clock Capable (SRCC):**
   * เดินสายตรงเข้าสู่ CMT ประจำ Region นั้นๆ ได้โดยตรง
   * เหมาะสำหรับสัญญาณนาฬิกาเฉพาะส่วน หรือ Source-Synchronous Interface ที่อยู่ภายใน Region เดียวกัน
3. **High-Density Global Clock (HDGC):**
   * พินสัญญาณนาฬิกาบน High-Density I/O Bank (รองรับแรงดันไฟ $1.8\text{V} - 3.3\text{V}$) มีแบนด์วิดท์ต่ำกว่า MRCC เล็กน้อย แต่ยังคงมีทางด่วนตรงเข้าสู่ Clock Tree ดีกว่า GPIO นับร้อยเท่า

> [!WARNING]
> หากกำหนด Pin Placement ให้สัญญาณนาฬิกาเข้าที่ Regular GPIO เครื่องมือสังเคราะห์ (Vivado/Quartus) จะส่งคำเตือนหรือ Error: `[Place 30-574] Poor placement for routing between an IO pin and BUFG`.  
> หากวิศวกรแก้ไขด้วยการใส่คำสั่ง override: `set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets ...]` นี่คือการปิดตาข้างเดียว! สัญญาณนาฬิกาจะถูกส่งผ่าน LUT Interconnects ทำให้เกิด Duty-Cycle Distortion (DCD) และ Random Jitter มหาศาลจนทำลาย Timing Margin ของระบบ!

---

### 1.3 การออกแบบวงจรกรองภาคจ่ายไฟ $\pi$-Filter สำหรับ $V_{CC\_PLL}$ (Power Filter Design & Resonant Damping)

VCO ใน MMCM เป็นวงจรอนาล็อกที่มีค่าความไวต่อแรงดันไฟเลี้ยง (PSRR Sensitivity: $K_{psrr} \approx 15 - 35\text{ ps/mV}$) เพื่อป้องกันริปเปิลจากสวิตชิ่งเรกูเลเตอร์ ต้องติดตั้งวงจรกรอง Low-Pass แบบ $\pi$-Filter ร่วมกับ Ferrite Bead (FB) บนเรล $V_{CCAUX\_IO} / V_{CC\_PLL}$:

```
              วงจร $\pi$-FILTER พร้อม DAMPING RESISTOR เพื่อป้องกัน ANTI-RESONANCE
              
                 Ferrite Bead (Murata BLM18PG121)
                 +-----------[ L_fb / R_dc ]-----------+
                 |                                     |
  VCC_MAIN (1.8V)|             +---[ R_damp ]---+      |   VCC_PLL (To FPGA BGA)
  ---------------+             |                |      +------------------------->
                 |             +----[ C_damp ]--+      |
               [ C1 ]                                [ C2 ]        [ C3 ]
             (10 uF)                                (1.0 uF)      (0.1 uF)   (0.01 uF)
                 |                                     |             |           |
  GND -----------+-------------------------------------+-------------+-----------+--->
```

#### ฟิสิกส์ของการเกิด Anti-Resonance (จุดดักสลายของตัวเหนี่ยวนำ):
Ferrite Bead ที่ความถี่ต่ำจะประพฤติตัวเป็นตัวเหนี่ยวนำ ($L_{fb}$) เมื่อต่อขนานกับตัวเก็บประจุดีคัปปลิงเซรามิก ($C_2, C_3$) ที่มีค่า Equivalent Series Resistance (ESR) ต่ำมาก จะเกิดวงจรเรโซแนนซ์แบบขนาน (Parallel $LC$ Resonance):

$$f_0 = \frac{1}{2\pi \sqrt{L_{fb} \cdot C_{total}}}$$
$$Q = \frac{1}{R_{total}} \sqrt{\frac{L_{fb}}{C_{total}}}$$

หากไม่มีการหน่วง (Undamped, $Q > 5$):
* ที่ความถี่เรโซแนนซ์ $f_0$ อิมพีแดนซ์ของภาคจ่ายไฟจะพุ่งสูงขึ้นเป็นยอดแหลม (Impedance Peak สูงขึ้น $10 - 20\text{ dB}$!)
* หากความถี่สวิตชิ่งของ Buck Converter หรือฮาร์มอนิกของทราฟฟิกตรงกับ $f_0$ พอดี สัญญาณรบกวนจะถูกขยายจนเกิด Periodic Jitter มหาศาล!

#### การแก้ปัญหาด้วย Damping Resistor ($R_{damp}$):
ติดตั้งตัวต้านทานหน่วง $R_{damp}$ ขนานหรืออนุกรมกับตัวเก็บประจุอิเล็กโทรไลต์/แทนทาลัม ($C_{damp}$) เพื่อกดค่าสัมประสิทธิ์คุณภาพให้เหลือ $Q \le 1.0$:

$$R_{damp} \approx \sqrt{\frac{L_{fb}}{C_{total}}}$$

---

### 1.4 แบบจำลอง Timing Uncertainty ในไฟล์ SDC/XDC (STA Jitter Modeling)
ในเครื่องมือ Static Timing Analysis (Vivado Timing Engine) ค่าความไม่แน่นอนของสัญญาณนาฬิกา (Total Clock Uncertainty: $T_{uncert}$) บนเส้นทาง Synchronous Path ถูกคำนวณจาก:

$$T_{uncert} = \sqrt{T_{jitter\_in}^2 + T_{jitter\_sys}^2 + T_{pll\_phase\_error}^2} + T_{clock\_skew}$$

```tcl
# ==============================================================================
# XDC JITTER AND UNCERTAINTY INJECTION FOR SENIOR SIGN-OFF
# ==============================================================================

# 1. กำหนดความถี่สัญญาณนาฬิกาหลัก (156.25 MHz)
create_clock -period 6.400 -name clk_ref_156m [get_ports refclk_156m_p]

# 2. ป้อนค่า Random & Deterministic Input Jitter ที่วัดได้จาก Signal Source (12 ps)
set_input_jitter [get_clocks clk_ref_156m] 0.012

# 3. กำหนดค่า System Jitter ประจำบอร์ดจาก Power Supply Ripple (25 ps)
set_system_jitter 0.025

# 4. กำหนด Clock Uncertainty พิเศษสำหรับเส้นทางวิกฤตข้ามโดเมน (CDC Boundary)
set_clock_uncertainty -from [get_clocks clk_ref_156m] -to [get_clocks clk_dsp_core] 0.080 -setup
set_clock_uncertainty -from [get_clocks clk_ref_156m] -to [get_clocks clk_dsp_core] 0.040 -hold
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** บอร์ดประมวลผลวิดีโอระดับมืออาชีพ 4K 60fps Broadcast Video Processing Card (HDMI 2.0 / 12G-SDI) ใช้ FPGA Kintex UltraScale (XCKU060) เกิดอาการจอดับกะพริบ (Video Blanking / Frame Dropping) สุ่มเกิดขึ้นทุกๆ 15-30 นาที เมื่อต่อเข้ากับจอมอนิเตอร์มาตรฐานอุตสาหกรรม

**วิกฤตหน้างาน:** ระบบผ่านการทดสอบในขั้นตอน RTL Simulation 100% และไม่มี Setup/Hold Timing Violation ในรายงานของ Vivado (Worst Negative Slack $WNS > +200\text{ ps}$) แต่เมื่อนำบอร์ดจริงไปวัดสัญญาณนาฬิกา Pixel Clock ($594.0\text{ MHz}$) พบว่าค่า Total Jitter สูงถึง $68.5\text{ ps}$ (มาตรฐาน HDMI 2.0 บังคับห้ามเกิน $28.0\text{ ps}$)

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] ภาพวิดีโอ 4K 60fps บนจอ HDMI 2.0 กะพริบดับสุ่มเนื่องจาก Total Jitter เกินสเปก
      |
      +---> [Why 1] ทำไมภาพถึงกะพริบดับ?
      |             --> เพราะตัวรับสัญญาณจอภาพ (HDMI Receiver PHY) สูญเสียการ Sync ขอบบิต
      |
      +---> [Why 2] ทำไมตัวรับถึงสูญเสียการ Sync?
      |             --> เพราะสัญญาณนาฬิกา 594 MHz มี Total Jitter สูงถึง 68.5 ps (Eye Margin หายไป)
      |
      +---> [Why 3] ทำไม Jitter ของสัญญาณนาฬิกาจึงพุ่งสูงผิดปกติ?
      |             --> เพราะสัญญาณ Reference Clock 27 MHz ภายนอกถูกนำเข้าที่ขา GPIO ธรรมดาของ Bank 64
      |                 และเดินสายผ่าน Fabric Routing ข้าม Die ไปเข้า MMCM ใน Bank 44!
      |
      +---> [Why 4] ทำไมผู้ออกแบบถึงต่อสัญญาณนาฬิกาเข้าพิน GPIO?
      |             --> เพราะในขั้นตอนออกแบบ Schematics ผู้ออกแบบไม่ได้ตรวจสอบคู่มือ Pinout และเลือกขาตามความสะดวก
      |                 แล้วใช้คำสั่ง `CLOCK_DEDICATED_ROUTE FALSE` เพื่อหลบ Error ของ Vivado!
      |
      +---> [Why 5 - Root Cause] ทำไมสัญญาณรบกวนถึงรุนแรงยิ่งขึ้นไปอีก?
                    --> เพราะ Ferrite Bead บนเรล VCCAUX_IO เกิดการเรโซแนนซ์ขนาน (Anti-Resonance)
                        ที่ความถี่ 2.2 MHz ขยายริปเปิลจาก Buck Converter เพิ่มขึ้น 14 dB ป้อนเข้าสู่ MMCM!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการเกิด Total Jitter 68.5 ps บนพิกเซลคล็อก 594 MHz (HDMI 2.0)

   PCB LAYOUT & PINOUT                        POWER INTEGRITY (VCCAUX Filter)
         |                                          |
   ต่อ Reference Clock เข้า GPIO ทั่วไป              Ferrite Bead เกิด Anti-Resonance ที่ 2.2 MHz
         \                                          /
          \   ใช้คำสั่ง CLOCK_DEDICATED_ROUTE FALSE/   ขาด Damping Resistor ในวงจร Pi-Filter
           \   สัญญาณวิ่งตัด Fabric Routing ข้ามชิป /   ริปเปิลสวิตชิ่งถูกขยาย +14 dB
            +------------------------------------+
            |                                    |
            |   HDMI 2.0 PIXEL CLOCK JITTER      |===> [CRITICAL VIDEO SYNC FAILURE]
            |   EXCEEDS SPEC (TJ = 68.5 ps)      |
            +------------------------------------+
           /                                      \
          /   ไม่ป้อนค่า Jitter ลงในไฟล์ XDC        \   วัดสัญญาณด้วยโพรบที่ไม่มีการแมตช์อิมพีแดนซ์
         /                                          \
   มองข้ามคำเตือน Warning Place 30-574 ใน Vivado      ละเลยการทดสอบ Phase Noise บน Spectrum Analyzer
         |                                          |
   EDA PROCESS & VERIFICATION                 MEASUREMENT METHODOLOGY
```

---

### ขั้นตอนการแก้ปัญหาและแนวทางป้องกันหน้างาน (Corrective Actions & SOP)

#### ขั้นตอนที่ 1: ย้ายลายวงจร PCB สัญญาณ Reference Clock เข้าพิน MRCC โดยตรง
ทำการแก้ไข Layout บอร์ด (PCB Revision Update):
* ย้ายสัญญาณนาฬิกาอ้างอิงจาก GPIO เดิมไปยังพิน **`IO_L12P_T1U_N10_GC_44` (MRCC Pin)** ซึ่งเชื่อมต่อด้วยเส้นทาง Hard Track ไปยัง CMT ประจำ Bank 44 โดยตรง
* ลบคำสั่ง `set_property CLOCK_DEDICATED_ROUTE FALSE` ออกจากไฟล์ XDC Constraint ทั้งหมด

#### ขั้นตอนที่ 2: ปรับวงจรกรอง $\pi$-Filter เพื่อกด Anti-Resonance
* ติดตั้งตัวต้านทานแดมปิ้ง $R_{damp} = 1.0\ \Omega$ อนุกรมกับตัวเก็บประจุแทนทาลัม $C_{damp} = 22\ \mu\text{F}$ ขนานคร่อมที่เอาต์พุตของ Ferrite Bead
* ผลลัพธ์: Impedance Peak ที่ความถี่ $2.2\text{ MHz}$ ลดลงจาก $18.5\ \Omega$ เหลือเพียง $1.2\ \Omega$ กำจัด Periodic Jitter ไปได้อย่างสมบูรณ์

```
             เปรียบเทียบผลลัพธ์ของรูปคลื่นสัญญาณนาฬิกา 594 MHz
             
 [ก่อนแก้ไข: GPIO Routing + Anti-Resonance]
 --------------------------------------------------
 - Routing Jitter: 42.0 ps
 - Periodic Jitter (2.2 MHz): 18.5 ps
 - Random Jitter: 8.0 ps
 ==> Total Jitter (TJ @ 10^-12): 68.5 ps (ตกมาตรฐาน HDMI!)
 
 [หลังแก้ไข: MRCC Dedicated Pin + Damped Pi-Filter]
 --------------------------------------------------
 - Routing Jitter: < 2.0 ps (Dedicated Track)
 - Periodic Jitter: < 1.5 ps (Damped Filter)
 - Random Jitter: 1.1 ps
 ==> Total Jitter (TJ @ 10^-12): 16.9 ps (ผ่านเกณฑ์ < 28 ps อย่างปลอดภัย!)
```

---

### SOP Checklist สำหรับการตรวจรับและ Sign-off พินสัญญาณนาฬิกาและวงจรกรอง

```
[ ] 1. Clock Pin Allocation Verification:
       - สัญญาณนาฬิกาภายนอกทุกเส้นต้องเชื่อมต่อเข้ากับพินที่มีสัญลักษณ์ GC, MRCC, หรือ SRCC เท่านั้น
       - ห้ามมีคำสั่ง `CLOCK_DEDICATED_ROUTE FALSE` ในไฟล์ XDC เด็ดขาด (Zero Tolerance Rule)

[ ] 2. Power Supply Decoupling & Resonance Damping:
       - Ferrite Bead บน VCCAUX ต้องมี Damping Resistor หรือใช้ Ferrite ชนิด Low-Q
       - อิมพีแดนซ์ของรางจ่ายไฟต้องต่ำกว่า 0.5 Ohm ตลอดช่วงความถี่ 100 kHz ถึง 50 MHz

[ ] 3. Accurate Timing Uncertainty Modeling:
       - ต้องระบุ `set_input_jitter` ตามสเปกของ Oscillator ภายนอก
       - ต้องระบุ `set_system_jitter` เพื่อครอบคลุม Power Supply Ripple บนบอร์ดจริง

[ ] 4. Physical Measurement Validation:
       - วัด Total Jitter บน SMA Connector ภายนอกด้วย Real-Time Oscilloscope แบนด์วิดท์ >= 13 GHz
       - ยืนยันว่าค่า TJ ที่ BER = 10^-12 มี Margin เหลือไม่น้อยกว่า 30% ของมาตรฐาน I/O
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| 専用クロック端子 | せんようくろっくたんし | Sen'yō Kurokku Tanshi | พินสัญญาณนาฬิกาเฉพาะกิจ (Dedicated Clock Pin: MRCC/SRCC) |
| 配線ジッタ | はいせんじった | Haisen Jitta | จิตเตอร์ที่เกิดจากการเดินสายผ่านแฟบริก (Interconnect / Routing Jitter) |
| 反共振 | はんきょうしん | Hankyōshin | ปรากฏการณ์เรโซแนนซ์ต้านขนาน (Anti-Resonance) |
| 制振抵抗 | せいしんていこう | Seishin Teikō | ตัวต้านทานหน่วงเพื่อสลายการแกว่ง (Damping Resistor: $R_{damp}$) |
| 周期ジッタ | しゅうきじった | Shūki Jitta | จิตเตอร์แบบคาบเวลา (Period Jitter) |
| 確定ジッタ | かくていじった | Kakutei Jitta | สัญญาณรบกวนที่มีขอบเขตแน่นอน (Deterministic Jitter: DJ) |
| ランダムジッタ | らんだむじった | Randamu Jitta | สัญญาณรบกวนแบบสุ่มตามเกาส์เซียน (Random Jitter: RJ) |
| 総ジッタ | そうじった | Sō Jitta | สัญญาณรบกวนเวลารวม (Total Jitter: TJ) |
| クロック不確定性 | くろっくふかくていせい | Kurokku Fukakutei-sei | ความไม่แน่นอนของเวลาสัญญาณนาฬิกา (Clock Uncertainty) |
| 検図指摘事項 | けんずしてきじこう | Kenzu Shiteki Jikō | ข้อบกพร่องที่ตรวจพบในการรีวิวแบบ (Review Finding / Action Item) |
| 電源インピーダンス | でんげんいんぴーだんす | Dengen Inpīdansu | อิมพีแดนซ์ของโครงข่ายจ่ายพลังงาน (Power Distribution Impedance) |
| 波形歪み | はけいゆがみ | Hakei Yugami | ความผิดรูปของสัญญาณและดิวตี้ไซเคิล (Waveform / Duty-Cycle Distortion) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการต่อสัญญาณนาฬิกาเข้าขา General Purpose I/O
**สถานที่:** ห้องประชุมตรวจสอบแบบวงจรระดับหัวหน้าวิศวกร (Board Hardware Review Council)  
**ผู้เข้าร่วม:** Chief Verification Engineer (หัวหน้าวิศวกรตรวจสอบแบบอาวุโส) และ Board Layout Designer (วิศวกรผู้ออกแบบ PCB)

* **Chief Engineer:**  
  「おい、この回路図と制約ファイル（XDC）を見てみろ。外部の27MHzリファレンスクロックが、Bank 64の一般GPIOピンに入力されているじゃないか！おまけにVivadoのエラーを握りつぶすために `CLOCK_DEDICATED_ROUTE FALSE` を設定しているな。誰がこんな暴挙を承認したんだ？一般ファブリック配線を通せば、LUTの遅延ばらつきとスイッチングノイズで数百ピコ秒の配線ジッタが乗ることは明白だ！」  
  *(Oi, kono kaikozu to seiyaku fairu (XDC) o mite miro. Gaibu no 27MHz rifarensu kurokku ga, Bank 64 no ippan GPIO pin ni nyūryoku sarete iru ja nai ka! Omake ni Vivado no erā o nigiritsubusu tame ni `CLOCK_DEDICATED_ROUTE FALSE` o settei shite iru na. Dare ga konna bōkyo o shōnin shita n da? Ippan faburikku haisen o tōseba, LUT no chien baratsuki to suitchingu noizu de sūhyaku pikobyō no haisen jitta ga noru koto wa meihaku da!)*  
  **ความหมาย:** "เฮ้ย ดูวงจรกับไฟล์ XDC ตรงนี้สิ สัญญาณ Reference Clock 27MHz จากภายนอก ดันต่อเข้าพิน General GPIO ธรรมดาของ Bank 64 เนี่ยนะ! แถมยังใส่คำสั่ง `CLOCK_DEDICATED_ROUTE FALSE` เพื่อปิดปาก Error ของ Vivado ไว้อีก ใครอนุมัติให้ทำเรื่องบ้าบิ่นแบบนี้? ถ้าปล่อยให้สัญญาณนาฬิกาวิ่งผ่านสาย General Fabric ความแปรปรวนของเกตใน LUT กับสัญญาณสวิตชิ่งกวนจะยัด Routing Jitter เข้าไปหลายร้อยพิโกวินาที นี่มันชัดเจนอยู่แล้ว!"

* **Layout Designer:**  
  「申し訳ありません。BGAのファンアウト配線が密集しており、専用クロックピン（MRCC）までの配線引き回しが困難だったため、近場の空きピンを流用してしまいました。ソフトウェア側でエラーを回避できるため、問題ないものと安易に判断していました。」  
  *(Mōshiwake arimasen. BGA no fan'auto haisen ga misshū shite ori, sen'yō kurokku pin (MRCC) made no haisen hikimawashi ga konnan datta tame, chikaba no aki-pin o ryūyō shite shimaimashita. Sofutowea-gawa de erā o kaihi dekiru tame, mondai nai mono to an'i ni handan shite imashita.)*  
  **ความหมาย:** "ขออภัยเป็นอย่างยิ่งครับ ลายวงจร Fan-out ใต้ BGA มันหนาแน่นมาก การลากลายวงจรยาวไปถึงขา Dedicated Clock (MRCC) ทำได้ลำบาก ผมเลยหยิบขาว่างใกล้ๆ มาใช้แทน เห็นว่าในซอฟต์แวร์สามารถใส่คำสั่งข้าม Error ได้ เลยด่วนสรุปไปเองว่าง่ายๆ คงไม่มีปัญหาครับ"

* **Chief Engineer:**  
  「『ツールが通るから大丈夫』というのは最低の素人判断だ！HDMI 2.0のピクセルクロック（594MHz）はジッタ許容量が28psしかない。ファブリック配線で40psもジッタが増えたら、実機で画面がブラックアウトするのは物理の法則だ。直ちにパターンを引き直し、Bank 44のGC専用差動ピンへ直結させろ。基板改版の出図日程をリスケジュールすること！」  
  *("Tsūru ga tōru kara daijōbu" to iu no wa saitei no shirōto handan da! HDMI 2.0 no pikuseru kurokku (594MHz) wa jitta kyoyōryō ga 28ps shika nai. Faburikku haisen de 40ps mo jitta ga fuetara, jikki de gamen ga burakkuauto suru no wa butsuri no hōsoku da. Tadachini patān o hikinaoshi, Bank 44 no GC sen'yō sadō pin e chokketsu sasero. Kiban kaihan no shutsuzu nittei o risukejūru suru koto!)*  
  **ความหมาย:** "'เครื่องมือยอมให้ผ่าน แปลว่าไม่เป็นไร' นี่มันตรรกะของมือสมัครเล่นชัดๆ! สัญญาณ Pixel Clock 594MHz ของ HDMI 2.0 มีระยะเผื่อ Jitter ได้แค่ 28ps เองนะ ถ้าการเดินสายผ่าน Fabric เพิ่ม Jitter เข้าไปถึง 40ps บนเครื่องจริงหน้าจอมันก็ดับมืดสนิทตามกฎฟิสิกส์น่ะสิ! ไปแก้ลายวงจรใหม่เดี๋ยวนี้ แล้วต่อตรงเข้าขา Dedicated Differential GC ของ Bank 44 จัดการเลื่อนตารางส่งแบบผลิตบอร์ดใหม่ซะ!"

---

#### สถานการณ์ที่ 2: การตรวจสอบปัญหาเรโซแนนซ์ต้าน (Anti-Resonance) บนวงจรกรอง VCCAUX
* **Chief Engineer:**  
  「それから、電源層の検図結果だが、VCCAUX端子の前に挿入したフェライトビーズ（120Ω @ 100MHz）と後段のセラミックコンデンサで、2.2MHz付近に激しい反共振（インピーダンスピーク）が発生しているぞ。スイッチング電源のリプルがこの周波数と一致して、18.5psもの周期ジッタを吐き出している。なぜダンピング抵抗を入れて共振のQ値を落とさなかった？」  
  *(Sorekara, dengensō no kenzu kekka da ga, VCCAUX tanshi no mae ni sōnyū shita feraito bīzu (120-omega @ 100MHz) to kōdan no seramikku kondensa de, 2.2MHz fukin ni hageshii hankyōshin (inpīdansu pīku) ga hassei shite iru zo. Suitchingu dengen no rippuru ga kono shūhasū to itchi shite, 18.5ps mono shūki jitta o hakidashite iru. Naze dampingu teikō o irete kyōshin no Q-chi o otosanakatta?)*  
  **ความหมาย:** "อีกเรื่องหนึ่ง จากผลการตรวจแบบชั้นไฟเลี้ยง Ferrite Bead (120 โอห์ม @ 100MHz) ที่ใส่ไว้หน้าขา VCCAUX กับตัวเก็บประจุเซรามิกข้างหลัง มันเกิด Anti-Resonance (Impedance Peak พุ่งกระฉูด) แถวๆ ความถี่ 2.2MHz อยู่นะ! แล้วริปเปิลของ Switching Supply ดันวิ่งมาชนความถี่นี้พอดี ทำให้มันปล่อย Periodic Jitter ออกมาตั้ง 18.5ps ทำไมไม่ใส่ Damping Resistor ดึงค่า Q ของการเรโซแนนซ์ลงมา?"

* **Layout Designer:**  
  「フェライトビーズのデータシート推奨回路をそのままコピーして載せていました。コンデンサの低ESR特性と組み合わせることで反共振が起きることまで計算できていませんでした。」  
  *(Feraito bīzu no dētashīto suishō kairo o sonomama kopī shite nosete imashita. Kondensa no tei-ESR tokusei to kumiawaseru koto de hankyōshin ga okiru koto made keisan dekite imasen deshita.)*  
  **ความหมาย:** "ผมคัดลอกวงจรแนะนำจากดาต้าชีตของ Ferrite Bead มาใช้ตรงๆ ครับ ไม่ทันได้คำนวณว่าการจับคู่กับตัวเก็บประจุ Low-ESR จะเหนี่ยวนำให้เกิด Anti-Resonance ขึ้นมาครับ"

* **Chief Engineer:**  
  「低ESRのMLCCは高周波ノイズには強いが、ビーズのインダクタンス成分と組むと必ず鋭い共振峰を作る。直ちに1.0Ωのダンピング抵抗を直列に入れた電解またはタンタルコンデンサを並列に追加しろ。共振ピークを平坦化（Q < 1）させて、電源インピーダンスを全帯域で0.5Ω以下に抑え込むこと！」  
  *(Tei-ESR no MLCC wa kōshūha noizu ni wa tsuyoi ga, bīzu no indakutansu seibun to kumu to kanarazu surudoi kyōshinhō o tsukuru. Tadachini 1.0-omega no dampingu teikō o chokuretsu ni ireta denkai matawa tantaru kondensa o heiretsu ni tsuika shiro. Kyōshin pīku o heitanka (Q < 1) sasete, dengen inpīdansu o zen-taiiki de 0.5-omega ika ni osaekomu koto!)*  
  **ความหมาย:** "MLCC ที่มี ESR ต่ำมันกรองนอยส์ความถี่สูงได้ดีก็จริง แต่พอไปประกบกับความเหนี่ยวนำของ Ferrite Bead มันจะสร้างยอดเขาเรโซแนนซ์ที่แหลมคมเสมอ! ไปเพิ่มตัวเก็บประจุแทนทาลัมที่ต่ออนุกรมกับตัวต้านทานหน่วง 1.0 โอห์มขนานเข้าไปเดี๋ยวนี้ เพื่อกดให้ยอดเรโซแนนซ์ราบเรียบลง ($Q < 1$) และคุมอิมพีแดนซ์ของภาคจ่ายไฟให้ต่ำกว่า 0.5 โอห์มตลอดทุกย่านความถี่!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณงบประมาณสัญญาณรบกวนเวลารวมด้วย Dual-Dirac Model (Total Jitter Budgeting Calculation)
ในระบบส่งสัญญาณภาพดิจิทัล HDMI 2.0 ($F_{pixel} = 594.0\text{ MHz}$, คาบเวลา $T_{pixel} \approx 1683.5\text{ ps}$):
* ข้อกำหนดสากลบังคับว่า สัญญาณนาฬิกาต้องมี Total Jitter รวมที่อัตราความผิดพลาด $BER = 10^{-12}$ ไม่เกิน **$TJ_{spec} \le 28.0\text{ ps}$**
* ในการวิเคราะห์องค์ประกอบของสัญญาณรบกวน:
  1. **Deterministic Jitter ($DJ_{\delta\delta}$):**
     * สัญญาณรบกวนจากการเดินสายผิดพลาดผ่าน Fabric I/O: $DJ_{routing} = 14.5\text{ ps}$
     * สัญญาณรบกวน Periodic Jitter จากเรโซแนนซ์ของภาคจ่ายไฟ: $PJ = 8.2\text{ ps}$
     * สัญญาณรบกวน Duty-Cycle Distortion ของทรานซิสเตอร์: $DCD = 3.3\text{ ps}$
     * รวมเป็น: $DJ_{\delta\delta} = DJ_{routing} + PJ + DCD$
  2. **Random Jitter ($RJ_{rms}$):**
     * ค่า RMS Random Jitter จาก Thermal/Shot Noise ของ MMCM รวมกับ Oscillator: $RJ_{rms} = 0.95\text{ ps}$

โดยใช้สมการ Dual-Dirac Model มาตรฐาน:
$$TJ(BER) = DJ_{\delta\delta} + 2 \cdot Q(BER) \cdot RJ_{rms}$$
โดยที่สำหรับ $BER = 10^{-12}$ มีค่า $2 \cdot Q(10^{-12}) \approx 14.069$

จงคำนวณหาค่า $TJ(10^{-12})$ และวิเคราะห์ว่าระบบผ่านเกณฑ์ HDMI 2.0 หรือไม่ และหากต้องการให้ผ่านเกณฑ์ จะต้องลด $DJ_{routing}$ ลงเหลือไม่เกินกี่พิโกวินาที (กำหนดให้องค์ประกอบอื่นคงที่):

A) $TJ \approx 39.37\text{ ps}$ (ไม่ผ่านเกณฑ์), \quad ต้องลด $DJ_{routing} \le 3.13\text{ ps}$  
B) $TJ \approx 42.15\text{ ps}$ (ไม่ผ่านเกณฑ์), \quad ต้องลด $DJ_{routing} \le 5.80\text{ ps}$  
C) $TJ \approx 27.50\text{ ps}$ (ผ่านเกณฑ์อย่างเฉียดฉิว), \quad ไม่จำเป็นต้องแก้ไข  
D) $TJ \approx 52.80\text{ ps}$ (ไม่ผ่านเกณฑ์), \quad ต้องลด $DJ_{routing} \le 0.00\text{ ps}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณ Deterministic Jitter รวม ($DJ_{\delta\delta}$)**
$$DJ_{\delta\delta} = DJ_{routing} + PJ + DCD = 14.5\text{ ps} + 8.2\text{ ps} + 3.3\text{ ps} = 26.0\text{ ps}$$

**ขั้นตอนที่ 2: คำนวณองค์ประกอบ Random Jitter ที่ $BER = 10^{-12}$**
$$RJ_{component} = 2 \cdot Q(10^{-12}) \cdot RJ_{rms} = 14.069 \times 0.95\text{ ps} \approx 13.36555\text{ ps} \approx 13.37\text{ ps}$$

**ขั้นตอนที่ 3: คำนวณ Total Jitter รวม ($TJ$)**
$$TJ = DJ_{\delta\delta} + RJ_{component} = 26.0\text{ ps} + 13.36555\text{ ps} = 39.36555\text{ ps} \approx 39.37\text{ ps}$$
เมื่อเทียบกับสเปก: $39.37\text{ ps} > 28.0\text{ ps}$ (**ล้มเหลว ตกมาตรฐาน HDMI 2.0 อย่างชัดเจน!**)

**ขั้นตอนที่ 4: คำนวณหาค่า $DJ_{routing}$ สูงสุดที่ยอมรับได้เพื่อให้ $TJ \le 28.0\text{ ps}$**
$$DJ_{\delta\delta,max} \le TJ_{spec} - RJ_{component} = 28.0\text{ ps} - 13.36555\text{ ps} = 14.63445\text{ ps}$$
เนื่องจาก:
$$DJ_{\delta\delta,max} = DJ_{routing,max} + PJ + DCD$$
$$14.63445\text{ ps} = DJ_{routing,max} + 8.2\text{ ps} + 3.3\text{ ps} = DJ_{routing,max} + 11.5\text{ ps}$$
$$DJ_{routing,max} \le 14.63445\text{ ps} - 11.5\text{ ps} = 3.13445\text{ ps} \approx 3.13\text{ ps}$$
*(หมายความว่าการเดินสายผ่าน Regular Fabric ซึ่งสร้าง Jitter สูงถึง $14.5\text{ ps}$ เป็นไปไม่ได้ที่จะผ่านเกณฑ์ จำเป็นต้องย้ายไปใช้พิน Dedicated MRCC ซึ่งมี Jitter $< 2.0\text{ ps}$ เท่านั้น!)*

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($TJ \approx 39.37\text{ ps}$, ต้องลด $DJ_{routing} \le 3.13\text{ ps}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคำนวณตัวคูณเกาส์เซียน $2Q$ สลับกับ $10^{-9}$ ($2Q \approx 12.0$)
* ข้อ C ผิด เพราะนำค่า $RJ_{rms}$ ไปบวกตรงๆ โดยไม่คูณค่า $2Q(BER)$
* ข้อ D ผิด เพราะคิดว่า $RJ$ มีค่าแปรผันแบบเชิงเส้นเต็มสเกล

---

### คำถามที่ 2: การวิเคราะห์ความถี่เรโซแนนซ์และสัมประสิทธิ์คุณภาพของวงจรกรอง $\pi$-Filter (Power Filter Anti-Resonance & Q-Factor Math)
บนบอร์ดประมวลผลสัญญาณ FPGA ขาไฟเลี้ยงอนาล็อก $V_{CCAUX}$ ($1.8\text{V}$) ถูกกรองด้วย Ferrite Bead และตัวเก็บประจุเซรามิก:
* ค่าความเหนี่ยวนำยังผลของ Ferrite Bead ที่ความถี่ต่ำ: $L_{fb} = 1.20\ \mu\text{H} = 1.20 \times 10^{-6}\text{ H}$
* ค่าความต้านทานไฟฟ้ากระแสตรงของบีด: $R_{dc} = 0.050\ \Omega$
* ค่าความจุไฟฟ้ารวมของตัวเก็บประจุเซรามิกหลังบีด (MLCC $10\ \mu\text{F} \parallel 1.0\ \mu\text{F} \parallel 0.1\ \mu\text{F}$):
  $$C_{total} \approx 11.1\ \mu\text{F} = 11.1 \times 10^{-6}\text{ F}$$
* ค่าความต้านทานอนุกรมสมมูลรวมของตัวเก็บประจุเซรามิก (Equivalent Series Resistance):
  $$ESR_{total} \approx 0.015\ \Omega$$

กำหนดสมการความถี่เรโซแนนซ์แบบขนาน ($f_0$) และสัมประสิทธิ์คุณภาพ ($Q$):
$$f_0 = \frac{1}{2\pi \sqrt{L_{fb} \cdot C_{total}}}$$
$$Q = \frac{1}{R_{total}} \sqrt{\frac{L_{fb}}{C_{total}}} \quad \text{โดยที่ } R_{total} = R_{dc} + ESR_{total}$$

จงคำนวณหา:
1. ความถี่เรโซแนนซ์ต้าน ($f_0$) ในหน่วยกิโลเฮิรตซ์ ($\text{kHz}$)
2. ค่าสัมประสิทธิ์คุณภาพ ($Q$) ของวงจรเดิม (ก่อนใส่ Damping Resistor)
3. ค่าความต้านทานแดมปิ้งที่เหมาะสม ($R_{damp}$) เพื่อกดให้ $Q \approx 1.0$ (Critically Damped):

A) $f_0 \approx 43.6\text{ kHz}, \quad Q \approx 5.06, \quad R_{damp} \approx 0.33\ \Omega$  
B) $f_0 \approx 138.0\text{ kHz}, \quad Q \approx 16.90, \quad R_{damp} \approx 1.20\ \Omega$  
C) $f_0 \approx 43.6\text{ kHz}, \quad Q \approx 16.90, \quad R_{damp} \approx 0.33\ \Omega$  
D) $f_0 \approx 87.2\text{ kHz}, \quad Q \approx 8.45, \quad R_{damp} \approx 0.65\ \Omega$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณความถี่เรโซแนนซ์ $f_0$**
$$L_{fb} \cdot C_{total} = (1.20 \times 10^{-6}\text{ H}) \times (11.1 \times 10^{-6}\text{ F}) = 1.332 \times 10^{-11}\text{ s}^2$$
$$\sqrt{L_{fb} \cdot C_{total}} = \sqrt{13.32 \times 10^{-12}} \approx 3.649657 \times 10^{-6}\text{ s}$$
$$f_0 = \frac{1}{2\pi \times (3.649657 \times 10^{-6})} = \frac{1}{2.29315 \times 10^{-5}} \approx 43,608\text{ Hz} \approx 43.6\text{ kHz}$$

**ขั้นตอนที่ 2: คำนวณค่า $Q$ ดั้งเดิม**
ความต้านทานรวม:
$$R_{total} = R_{dc} + ESR_{total} = 0.050\ \Omega + 0.015\ \Omega = 0.065\ \Omega$$
อิมพีแดนซ์คุณลักษณะของวงจรเรโซแนนซ์ ($Z_0$):
$$Z_0 = \sqrt{\frac{L_{fb}}{C_{total}}} = \sqrt{\frac{1.20 \times 10^{-6}}{11.1 \times 10^{-6}}} = \sqrt{0.108108} \approx 0.3288\ \Omega \approx 0.33\ \Omega$$
คำนวณสัมประสิทธิ์คุณภาพ:
$$Q = \frac{Z_0}{R_{total}} = \frac{0.3288\ \Omega}{0.065\ \Omega} \approx 5.058 \approx 5.06$$
*(ค่า $Q \approx 5.06$ สูงมาก บ่งชี้ว่าจะเกิด Impedance Peak ขยายสัญญาณรบกวนที่ความถี่ $43.6\text{ kHz}$ ขึ้นมากกว่า $14\text{ dB}$!)*

**ขั้นตอนที่ 3: คำนวณหาค่าความต้านทานแดมปิ้งที่ต้องการ ($R_{damp}$)**
เพื่อให้ได้สภาวะวิกฤต $Q \approx 1.0$:
$$R_{req} \approx Z_0 = \sqrt{\frac{L_{fb}}{C_{total}}} \approx 0.3288\ \Omega \approx 0.33\ \Omega$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($f_0 \approx 43.6\text{ kHz}, Q \approx 5.06, R_{damp} \approx 0.33\ \Omega$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคำนวณ $C_{total}$ โดยคิดเฉพาะตัวเก็บประจุ $1.0\ \mu\text{F}$ ตัวเดียว
* ข้อ C มีการคำนวณค่า $Q$ ผิดพลาดจากการใช้ความต้านทานต่ำกว่าความเป็นจริง
* ข้อ D เกิดจากการลืมตัวคูณ $2\pi$ ในการคำนวณความถี่เชิงมุม

---

### คำถามที่ 3: การวิเคราะห์ผลกระทบของ Routing Jitter ต่อ Setup Timing Slack (Setup Slack Degradation with Fabric Clock Routing)
ในวงจรประมวลผลข้อมูลความเร็วสูง สัญญาณนาฬิกา $F_{clk} = 200.0\text{ MHz}$ ($T_{clk} = 5.000\text{ ns}$):
* เส้นทางข้อมูลวิกฤต (Critical Datapath):
  * ความล่าช้าของ Flip-Flop ต้นทาง: $t_{co} = 0.450\text{ ns}$
  * ความล่าช้าของวงจร Combinational Logic (LUTs): $t_{logic} = 3.800\text{ ns}$
  * ความล่าช้าของสายส่งข้อมูล (Routing Delay): $t_{net} = 0.400\text{ ns}$
  * เวลาจัดเตรียมข้อมูลของ Flip-Flop ปลายทาง: $t_{setup} = 0.120\text{ ns}$
* ความไม่แน่นอนของเวลาในสภาวะปกติ (Baseline Clock Uncertainty): $T_{uncert\_base} = 0.080\text{ ns} = 80\text{ ps}$
* สัญญาณนาฬิกาใน **กรณีที่ 1 (ต่อผ่านพิน MRCC):**
  * มีค่า Routing Jitter บนโครงข่ายสัญญาณนาฬิกา: $J_{clk,MRCC} = 0.015\text{ ns} = 15\text{ ps}$
* สัญญาณนาฬิกาใน **กรณีที่ 2 (ต่อผ่านพิน GPIO + Fabric Routing):**
  * เกิด Routing Jitter และ Duty-Cycle Distortion สะสม: $J_{clk,GPIO} = 0.280\text{ ns} = 280\text{ ps}$

กำหนดสมการ Setup Slack:
$$t_{slack} = T_{clk} - (t_{co} + t_{logic} + t_{net} + t_{setup}) - (T_{uncert\_base} + J_{clk})$$

จงคำนวณหาค่า $t_{slack}$ ของทั้งสองกรณี และวิเคราะห์ผลกระทบต่อ Timing Closure:

A) กรณี 1: $t_{slack} = +0.135\text{ ns}$ (ผ่านเกณฑ์), \quad กรณี 2: $t_{slack} = -0.130\text{ ns}$ (เกิด Timing Violation ล้มเหลว)  
B) กรณี 1: $t_{slack} = +0.250\text{ ns}$ (ผ่านเกณฑ์), \quad กรณี 2: $t_{slack} = +0.020\text{ ns}$ (ผ่านเกณฑ์)  
C) กรณี 1: $t_{slack} = +0.050\text{ ns}$ (ผ่านเกณฑ์), \quad กรณี 2: $t_{slack} = -0.320\text{ ns}$ (ล้มเหลว)  
D) กรณี 1: $t_{slack} = -0.010\text{ ns}$ (ล้มเหลว), \quad กรณี 2: $t_{slack} = -0.275\text{ ns}$ (ล้มเหลว)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณความล่าช้าในเส้นทางข้อมูลรวม ($T_{data}$)**
$$T_{data} = t_{co} + t_{logic} + t_{net} + t_{setup}$$
$$T_{data} = 0.450\text{ ns} + 3.800\text{ ns} + 0.400\text{ ns} + 0.120\text{ ns} = 4.770\text{ ns}$$

**ขั้นตอนที่ 2: คำนวณเวลาที่เหลือจากรอบสัญญาณนาฬิกา ($T_{avail}$)**
$$T_{avail} = T_{clk} - T_{data} = 5.000\text{ ns} - 4.770\text{ ns} = 0.230\text{ ns} = 230\text{ ps}$$

**ขั้นตอนที่ 3: คำนวณ Setup Slack ในกรณีที่ 1 (พิน MRCC)**
$$T_{uncert,1} = T_{uncert\_base} + J_{clk,MRCC} = 0.080\text{ ns} + 0.015\text{ ns} = 0.095\text{ ns}$$
$$t_{slack,1} = T_{avail} - T_{uncert,1} = 0.230\text{ ns} - 0.095\text{ ns} = +0.135\text{ ns} = +135\text{ ps}$$
*(มีค่าเป็นบวก ระบบปิด Timing Closure สำเร็จอย่างปลอดภัย!)*

**ขั้นตอนที่ 4: คำนวณ Setup Slack ในกรณีที่ 2 (พิน GPIO + Fabric)**
$$T_{uncert,2} = T_{uncert\_base} + J_{clk,GPIO} = 0.080\text{ ns} + 0.280\text{ ns} = 0.360\text{ ns}$$
$$t_{slack,2} = T_{avail} - T_{uncert,2} = 0.230\text{ ns} - 0.360\text{ ns} = -0.130\text{ ns} = -130\text{ ps}$$
*(ค่า Slack ติดลบ เกิด Setup Violation ทันที ระบบจะทำงานผิดพลาดเมื่อนำไปรันบนชิปจริง!)*

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** (กรณี 1: $t_{slack} = +0.135\text{ ns}$, กรณี 2: $t_{slack} = -0.130\text{ ns}$) สะท้อนให้เห็นว่าการละเมิดกฎ Clock Pinout สามารถเปลี่ยนการออกแบบที่ผ่าน Timing ให้กลายเป็นความล้มเหลวระดับฮาร์ดแวร์ได้ทันที

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะลืมนำค่า Baseline Uncertainty $80\text{ ps}$ มาหักลบ
* ข้อ C ผิด เพราะคำนวณความล่าช้าของลอจิกซ้ำซ้อน
* ข้อ D ผิด เพราะคิดว่ากรณีที่ 1 มีค่าติดลบ
