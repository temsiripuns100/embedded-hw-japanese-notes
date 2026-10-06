# Lesson 161: FPGA Timing Closure Part 1 - Static Timing Analysis (STA) Foundations: Setup & Hold Physics, Timing Slack Equations, PVT Corners & Clock Uncertainty

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 กายวิภาคของเส้นทางไทม์มิ่งพื้นฐานในวงจรซิงโครนัส (Synchronous Timing Path Anatomy)
การปิดไทม์มิ่ง (Timing Closure) เป็นขั้นตอนชี้ชะตาความสำเร็จของการออกแบบ FPGA ความเร็วสูง โดยอาศัยหลักการของ **Static Timing Analysis (STA)** ซึ่งเป็นการตรวจสอบเชิงคณิตศาสตร์เพื่อพิสูจน์ว่า ทุกๆ ฟลิปฟล็อปในชิปจะทำงานได้อย่างถูกต้องภายใต้สภาวะการทำงานสุดขั้วทุกรูปแบบ โดยไม่ต้องอาศัยการจำลองเวกเตอร์ทดสอบ (Vectorless Analysis)

เส้นทางสัญญาณนาฬิกาและข้อมูลพื้นฐานระหว่างรีจิสเตอร์ต้นทาง (Launch Flip-Flop) และรีจิสเตอร์ปลายทาง (Capture Flip-Flop) ประกอบด้วย 4 องค์ประกอบหลัก:

```
                   กายวิภาคของ SYNCHRONOUS TIMING PATH
                   
   Launch Clock Path                              Capture Clock Path
   ─────────────────                              ──────────────────
   [ Clock Source ] ════════════════════════════► [ Clock Source ]
          │                                              │
          ▼ (T_launch_clk)                               ▼ (T_capture_clk)
   ┌─────────────┐                                ┌─────────────┐
   │ Launch FF   │                                │ Capture FF  │
   │  (Source)   │───┐                            │(Destination)│
   └─────────────┘   │                            └──────▲──────┘
                     ▼                                   │
              [ Combinational Logic ]                    │
              [ & Interconnect Path ] ───────────────────┘
              (T_cko + T_data_path)
```

#### พารามิเตอร์ทางกายภาพของเซลล์มาตรฐาน (Standard Cell Timing Parameters):
1. **$T_{cko}$ (Clock-to-Output Delay):** เวลาหน่วงนับจากขอบสัญญาณนาฬิกา $CLK$ เข้าถึงฟลิปฟล็อปต้นทาง จนกระทั่งข้อมูลเอาต์พุต $Q$ เริ่มปรากฏและมีระดับแรงดันที่เสถียร
2. **$T_{data\_path}$ (Combinational Data Path Delay):** ผลรวมความล่าช้าของลอจิกเกต (LUTs, MUXs, DSPs, CARRYs) รวมกับความล่าช้าของสายส่งเหนี่ยวนำ (Interconnect Net Routing Delay)
3. **$T_{setup}$ (Setup Time):** ระยะเวลาขั้นต่ำสุดที่สัญญาณข้อมูล $D$ ที่ขาเข้าของฟลิปฟล็อปปลายทาง จะต้องคงที่นิ่งสนิท **ก่อนที่** ขอบสัญญาณนาฬิกาของ Capture Clock จะมาถึง
4. **$T_{hold}$ (Hold Time):** ระยะเวลาขั้นต่ำสุดที่สัญญาณข้อมูล $D$ จะต้องคงสถานะเดิมนิ่งสนิท **หลังจากที่** ขอบสัญญาณนาฬิกาของ Capture Clock มาถึงแล้ว

---

### 1.2 คณิตศาสตร์และสมการของ Setup Slack และ Hold Slack (Derivation of Slack Equations)

```
                 ไดอะแกรมเวลาของ SETUP AND HOLD TIME MARGINS
                 
   Launch CLK  : ──/‾‾‾\_________________/‾‾‾\_________________ (Cycle 0: Launch Edge)
                    │
   Data Launch : ───┼─────< DATA VALID >───────────────────────
                    │     |<--- T_data_arrival --->|
                    │                              │
   Capture CLK : ──────────────────────────────────/‾‾‾\_______ (Cycle 1: Capture Edge)
                                            |<--T_su-->|
                                            |<-T_hold->|
                                            ▲          ▲
                                      Required      Capture
                                        Time         Edge
```

#### 1. การวิเคราะห์ Setup Time (สภาวะทางเดินข้อมูลช้าที่สุด - Max Delay Analysis):
สัญญาณข้อมูลที่ถูกปล่อยจาก Launch Edge รอบที่ 0 จะต้องเดินทางไปถึง Capture FF ก่อนที่ Capture Edge รอบที่ 1 จะมาถึง หักลบด้วยเวลา Setup Time และความไม่แน่นอนของสัญญาณนาฬิกา:

$$\text{Data Arrival Time}_{setup} = T_{launch\_clk} + T_{cko\_max} + T_{data\_max}$$
$$\text{Data Required Time}_{setup} = T_{period} + T_{capture\_clk} - T_{setup} - T_{uncertainty}$$
$$\text{Slack}_{setup} = \text{Data Required Time}_{setup} - \text{Data Arrival Time}_{setup}$$

แทนค่ารวม:
$$\text{Slack}_{setup} = \left( T_{period} + (T_{capture\_clk} - T_{launch\_clk}) \right) - \left( T_{cko\_max} + T_{data\_max} + T_{setup} + T_{uncertainty} \right)$$

* เมื่อกำหนดให้ **Clock Skew** ($\Delta T_{skew} = T_{capture\_clk} - T_{launch\_clk}$):
$$\text{Slack}_{setup} = T_{period} + \Delta T_{skew} - (T_{cko\_max} + T_{data\_max} + T_{setup} + T_{uncertainty})$$

> [!NOTE]
> เพื่อให้วงจรทำงานได้โดยไม่มีข้อผิดพลาด: **$\text{Slack}_{setup} \ge 0$ เสมอ!**  
> หาก $\text{Slack}_{setup} < 0$ เรียกว่าเกิด **Setup Timing Violation** (ข้อมูลมาถึงช้าเกินไป) แก้ไขได้โดยการลดความถี่ของสัญญาณนาฬิกา (เพิ่ม $T_{period}$) หรือแทรก Pipeline Register ตัดทอน $T_{data}$

---

#### 2. การวิเคราะห์ Hold Time (สภาวะทางเดินข้อมูลเร็วที่สุด - Min Delay Analysis):
สัญญาณข้อมูลใหม่ที่เกิดจาก Launch Edge รอบเดียวกัน (หรือรอบถัดไป) จะต้องเดินทางมา **ช้ากว่า** ระยะเวลา Hold Time ของ Capture FF เพื่อป้องกันไม่ให้ข้อมูลใหม่วิ่งทะลุเข้าไปเขียนทับข้อมูลเก่าก่อนที่ Capture FF จะแซมเปิลเสร็จ:

$$\text{Data Arrival Time}_{hold} = T_{launch\_clk} + T_{cko\_min} + T_{data\_min}$$
$$\text{Data Required Time}_{hold} = T_{capture\_clk} + T_{hold} + T_{uncertainty}$$
$$\text{Slack}_{hold} = \text{Data Arrival Time}_{hold} - \text{Data Required Time}_{hold}$$

แทนค่ารวม:
$$\text{Slack}_{hold} = (T_{cko\_min} + T_{data\_min}) - \Delta T_{skew} - (T_{hold} + T_{uncertainty})$$

> [!CRITICAL]
> **กฎเหล็กเรื่อง Hold Violation (The Fatal Truth):**  
> สังเกตว่าในสมการของ $\text{Slack}_{hold}$ **ไม่มีพจน์ของคาบเวลาสัญญาณนาฬิกา ($T_{period}$) ปรากฏอยู่เลยแม้แต่น้อย!**  
> หมายความว่า: **หากชิปเกิด Hold Violation ในซิลิคอนจริง คุณไม่สามารถแก้ไขได้ด้วยการลดความถี่สัญญาณนาฬิกา!**  
> แม้จะลด Clock จาก 500MHz เหลือ 1Hz วงจรก็ยังคงพังพินาศเหมือนเดิม 100%! ข้อผิดพลาด Hold Time จะต้องถูกปิดให้ผ่าน ($Slack \ge 0$) ตั้งแต่อยู่ในขั้นตอนวางแบบเท่านั้น!

---

### 1.3 สภาวะสุดขั้ว PVT Corners (Process, Voltage, Temperature Operating Corners)

ความเร็วในการส่งผ่านประจุของทรานซิสเตอร์ MOSFET แปรผันอย่างรุนแรงตามปัจจัยทางกายภาพ 3 ประการ (PVT):

```
                   เมทริกซ์การวิเคราะห์ PVT CORNERS ใน STA
                   
   [ 1. SLOW CORNER (Worst-Case for Setup Time) ]
   - Process : Slow Silicon (ความหนาแน่นสารเจือปนต่ำ, รอยต่อกว้าง)
   - Voltage : Minimum Operating VDD (เช่น 0.85V - 5% = 0.807V)
   - Temp    : Maximum Junction Temp (+100°C ถึง +125°C)
   ===> ทรานซิสเตอร์ขับกระแสได้ช้าที่สุด, ความต้านทานช่องนำกระแสสูงสุด!
        ใช้สำหรับตรวจจับ: SETUP VIOLATIONS (Max Delay)
   
   [ 2. FAST CORNER (Worst-Case for Hold Time) ]
   - Process : Fast Silicon (สารเจือปนสูง, รอยต่อแคบ)
   - Voltage : Maximum Operating VDD (เช่น 0.85V + 5% = 0.892V)
   - Temp    : Minimum Junction Temp (-40°C ถึง 0°C)
   ===> สภาพความคล่องตัวของอิเล็กตรอนพุ่งสูง, เกตสลับสถานะเร็วปานสายฟ้า!
        ใช้สำหรับตรวจจับ: HOLD VIOLATIONS (Min Delay)
```

#### ปรากฏการณ์ Temperature Inversion ในเทคโนโลยี FinFET สมัยใหม่:
ในกระบวนการผลิตระดับเก่า (เช่น 65nm planar) อุณหภูมิสูงจะทำให้ทรานซิสเตอร์ช้าลงเสมอ แต่ในเทคโนโลยี FinFET 16nm/7nm ที่แรงดันไฟต่ำ ($V_{dd} < 0.8\text{ V}$) จะเกิดปรากฏการณ์ **Temperature Inversion**:  
ที่อุณหภูมิต่ำ (เช่น $-40^\circ\text{C}$) แรงดันขีดเริ่ม ($V_{th}$) จะขยับสูงขึ้นจนทำให้กระแสขับต่ำลง ส่งผลให้ **อุณหภูมิติดลบอาจกลายเป็น Slowest Corner สำหรับ Setup Time** ได้ด้วยเช่นกัน!  
ดังนั้น เครื่องมือ STA ยุคใหม่จึงจำเป็นต้องตรวจสอบ Multi-Corner STA ทั้ง $-40^\circ\text{C}$, $+25^\circ\text{C}$, และ $+125^\circ\text{C}$ อย่างเข้มงวด

---

### 1.4 การสร้างแบบจำลองความไม่แน่นอนของสัญญาณนาฬิกา (Clock Uncertainty Modeling)

ในโลกความเป็นจริง ขอบของสัญญาณนาฬิกาไม่ได้มาถึงอย่างสมบูรณ์แบบตามเวลาทางทฤษฎี แต่มีความผันผวนแฝงตัวอยู่เสมอ:

$$T_{uncertainty} = T_{jitter} + T_{phase\_error} + T_{pessimism\_guard}$$

```
                องค์ประกอบของ CLOCK UNCERTAINTY ในระบบ FPGA
                
   Clock Uncertainty (T_uncertainty)
   ├── Clock Jitter (ความสั่นไหวของคาบเวลา)
   │   ├── Period Jitter (การเบี่ยงเบนของความกว้างคาบเวลา)
   │   └── Cycle-to-Cycle Jitter (ความต่างของคาบติดกัน)
   ├── Phase Error (ความคลาดเคลื่อนทางเฟสของ MMCM/PLL)
   └── Clock Tree Jitter (Jitter ที่ถูกขยายโดยบัฟเฟอร์ BUFG ตลอดทาง)
```

ในคำสั่งคอนสเตรนต์ XDC/SDC เครื่องมือจะคำนวณ Jitter พื้นฐานจากพารามิเตอร์ของ MMCM โดยอัตโนมัติ แต่วิศวกรระดับ Senior ต้องเผื่อค่า Margin เพิ่มเติมโดยใช้คำสั่ง:

```tcl
# กำหนดค่า Clock Uncertainty เพิ่มเติมเพื่อชดเชย Board Noise และ Power Supply Ripple
set_clock_uncertainty -setup 0.150 [get_clocks clk_core]
set_clock_uncertainty -hold  0.080 [get_clocks clk_core]
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: สถานีฐาน 5G Telecom ดับกลางหิมะจากบั๊ก Hold Violation (5G Base Station Sub-Zero Hold Timing Failure)

```
+----------------------------------------------------------------------------------------------------+
| กรณีศึกษาความล้มเหลวหน้างาน (現場の失敗事例)                                                                 |
| เหตุการณ์: กล่องประมวลผลสัญญาณดิจิทัล RRU (Remote Radio Unit) ติดตั้งบนเสาส่งสัญญาณโทรคมนาคม 5G           |
| อาการ: ผ่านการทดสอบรับรองในห้องแล็บที่อุณหภูมิห้อง (25°C) และห้องอบร้อน (85°C) ผ่าน 100% ไร้ข้อผิดพลาด         |
|        แต่เมื่อนำไปติดตั้งจริงบนยอดเขาในแถบสแกนดิเนเวีย ในช่วงฤดูหนาวที่อุณหภูมิลดลงเหลือ -25°C                  |
|        ระบบเกิดอาการบิตข้อมูลในบัส I/Q สลับที่ (Data Stream Corruption) จนสถานีฐานตัดการเชื่อมต่อลูกค้าทั้งเมือง |
+----------------------------------------------------------------------------------------------------+
```

#### การวิเคราะห์หาสาเหตุรากเหง้าด้วยหลักการ 5 Whys (5 Whys Root Cause Analysis):

1. **ทำไมระบบประมวลผล I/Q จึงเกิดการเสียหายของข้อมูลที่อุณหภูมิ -25°C?**  
   *คำตอบ:* ฟลิปฟล็อปของวงจร Digital Down-Converter (DDC) แซมเปิลข้อมูลได้ค่าขยะและบิตข้อมูลเลื่อนตำแหน่งไป 1 ไซเคิล

2. **ทำไมฟลิปฟล็อปจึงแซมเปิลข้อมูลผิดพลาดที่อุณหภูมิติดลบ แต่ทำงานได้ที่อุณหภูมิห้อง?**  
   *คำตอบ:* เกิดสภาวะ **Hold Timing Violation ($\text{Slack}_{hold} = -180\text{ ps}$)** สัญญาณข้อมูลจากรีจิสเตอร์ต้นทางวิ่งมาถึงเร็วเกินไปจนเหยียบขอบ Hold Time ของรีจิสเตอร์ปลายทาง

3. **ทำไมสัญญาณข้อมูลจึงวิ่งเร็วผิดปกติจนเกิด Hold Violation?**  
   *คำตอบ:* ที่อุณหภูมิ $-25^\circ\text{C}$ ทรานซิสเตอร์ FinFET ทำงานในสภาวะ **Fast Process Corner** สายตัวนำโลหะมีความต้านทานลดลงอย่างมาก ทำให้ค่าความล่าช้าของสายส่ง ($T_{data\_min}$) สั้นลงกว่าที่อุณหภูมิห้องถึง $35\%$

4. **ทำไมเครื่องมือ Vivado จึงไม่รายงานข้อผิดพลาด Hold Violation ก่อนปล่อยไฟล์ Bitstream?**  
   *คำตอบ:* ในกระบวนการปิดไทม์มิ่ง วิศวกรเปิดรายงานเฉพาะ Summary Report ที่รันบน **Slow Corner เท่านั้น** เนื่องจากเข้าใจผิดคิดว่าถ้าผ่านความถี่สูงสุดที่สภาวะช้าที่สุดแล้ว สภาวะอื่นย่อมผ่านทั้งหมด

5. **ทำไมทีมงานจึงละเลยการตรวจสอบ Fast Corner Hold Timing?**  
   *คำตอบ:* สคริปต์การทำ Sign-Off ของทีมงานถูกคัดลอกมาจากโปรเจกต์เก่าที่ตัดคำสั่งตรวจสอบ `report_timing -delay_type min_max` ออกเพื่อประหยัดเวลารันสคริปต์ ทำให้ข้อผิดพลาด Hold Time หลุดรอดสายตาไปจนถึงบอร์ดจริง!

---

### 2.2 ผังภูมิก้างปลาวิเคราะห์ปัญหา (Ishikawa Fishbone Diagram)

```
                       ผังภูมิก้างปลาวิเคราะห์สาเหตุ 5G SUB-ZERO HOLD VIOLATION
                       
   [ บุคลากรและความเข้าใจ (People & Mindset) ]      [ ขั้นตอนการตรวจสอบและสคริปต์ (Methodology) ]
   เข้าใจผิดว่าเช็คแค่ Setup Time ก็เพียงพอ          รัน STA เฉพาะ Slow Corner (ละเลย Fast Corner)
             \                                           \
              \                                           \
               \                                           \  ใช้คำสั่ง report_timing -delay_type max
   ขาดความรู้เรื่องพฤติกรรมซิลิคอนที่อุณหภูมิต่ำ                ปิดตาการตรวจสอบ Hold Violations
                 \                                           \
                  +-------------------------------------------+
                  |                                           |
                  |   5G RRU COLD-WEATHER HOLD TIME CRASH     | =====> [ FAILURE! ]
                  |                                           |
                  +-------------------------------------------+
                 /                                           /
                /                                           /  Clock Skew สวิงกว้างระหว่างบล็อก
   อุณหภูมิสภาพแวดล้อมติดลบ (-25°C) เร่งความเร็วเกต             ละเลยการควบคุม Routing Delay สั้นเกินไป
              /                                           /
   [ สภาพแวดล้อมทางกายภาพ (Environment) ]            [ กายวิภาคของวงจรและชิป (Hardware & Routing) ]
```

---

### 2.3 คู่มือปฏิบัติงาน SOP: ขั้นตอนการวิเคราะห์และปิดไทม์มิ่ง STA ระดับศูนย์ข้อผิดพลาด (Zero-Defect STA SOP)

#### สเต็ปที่ 1: ตรวจสอบความสมบูรณ์ของ Timing Constraints ในรายงาน Check Timing
* ก่อนดูค่า Slack ต้องรันคำสั่งตรวจสอบความสมบูรณ์ของคอนสเตรนต์เสมอ:
  `check_timing -verbose -file check_timing.rpt`
* ตรวจสอบว่าต้องไม่มีข้อผิดพลาดในกลุ่ม:
  * `no_clock`: ต้องไม่มีฟลิปฟล็อปใดที่ขาดสัญญาณนาฬิกา
  * `unconstrained_internal_endpoints`: ต้องไม่มีจุดปลายทางใดที่หลุดรอดจากการวิเคราะห์

#### สเต็ปที่ 2: รันการวิเคราะห์ไทม์มิ่งแบบครอบคลุมทั้ง Max และ Min (Min_Max Analysis)
* ห้ามดูเฉพาะ Setup Time เด็ดขาด ให้สร้างรายงานที่ครอบคลุมทั้ง Setup (Max) และ Hold (Min) ครบทุก PVT Corners:

```tcl
# สร้างรายงานสรุปไทม์มิ่งแบบสมบูรณ์
report_timing_summary -delay_type min_max \
                      -check_timing_verbose \
                      -max_paths 10 \
                      -nworst 1 \
                      -input_pins \
                      -routable_nets \
                      -file timing_summary_full.rpt
```

#### สเต็ปที่ 3: ตรวจสอบตัวชี้วัด WNS, TNS, WHS, THS
* ยืนยันว่าค่าตัวชี้วัดทั้ง 4 ตัวต้องผ่านเกณฑ์อย่างเข้มงวด:
  1. **WNS (Worst Negative Slack - Setup):** ต้อง $\ge 0.000\text{ ns}$ (แนะนำให้มี Positive Margin $> +0.200\text{ ns}$)
  2. **TNS (Total Negative Slack - Setup):** ต้อง $= 0.000\text{ ns}$
  3. **WHS (Worst Hold Slack - Hold):** ต้อง $\ge 0.000\text{ ns}$ (แนะนำให้มี Positive Margin $> +0.050\text{ ns}$)
  4. **THS (Total Hold Slack - Hold):** ต้อง $= 0.000\text{ ns}$

#### สเต็ปที่ 4: การแก้ไข Hold Violation โดยอัตโนมัติใน Vivado Router
* หากพบ Hold Violation เล็กน้อย ให้สั่งคำสั่ง Physical Optimization และ Route Optimization เพื่อให้เครื่องมือแทรกสายอ้อม (Route Detour) ซ่อมแซมอย่างปลอดภัย:

```tcl
# ขั้นตอนการซ่อมแซม Hold Violation ในขั้นตอน Place & Route
phys_opt_design -hold_fix
route_design -tns_cleanup
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง

| คำศัพท์คันジ / คาตากานะ | คำอ่าน (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- |
| **静的タイミング解析 (STA)** | Seiteki Taimingu Kaiseki | Static Timing Analysis (การวิเคราะห์ไทม์มิ่งแบบสถิต) |
| **セットアップ時間** | Settuappu Jikan | Setup Time (เวลาจัดเตรียมสัญญาณก่อนขอบนาฬิกา) |
| **ホールド時間** | Hoorudo Jikan | Hold Time (เวลาหน่วงคงสถานะสัญญาณหลังขอบนาฬิกา) |
| **タイミングスラック** | Taimingu Surakku | Timing Slack (ระยะเผื่อความปลอดภัยของเวลา) |
| **動作条件コーナー (PVT)** | Dousa Jouken Koonaa | PVT Corners (ขอบเขตสภาวะการทำงาน: กระบวนการ/แรงดัน/อุณหภูมิ) |
| **クロックジッタ** | Kurokku Jitta | Clock Jitter (ความกระเพื่อมสั่นไหวของสัญญาณนาฬิกา) |
| **クロックスキュー** | Kurokku Sukyuu | Clock Skew (ความต่างของเวลามาถึงของขอบนาฬิกา) |
| **クリティカルパス** | Kuritikaru Pasu | Critical Path (เส้นทางวิกฤตที่กินเวลาหน่วงสูงสุด) |
| **遅延ばらつき** | Chien Baratsuki | Delay Variation / Dispersion (ความผันแปรของความล่าช้า) |
| **タイミング収束** | Taimingu Shuusoku | Timing Closure (การปรับปรุงจนผ่านเกณฑ์ไทม์มิ่งทั้งหมด) |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図の現場会話)

#### สถานการณ์ที่ 1: การตรวจพบการละเลย Hold Violation ในรายงานไทม์มิ่ง (Hold Slack Neglect Review)
* **สถานที่:** แผนกออกแบบวงจรรวมสำหรับอุปกรณ์สื่อสารไร้สาย (Wireless Telecom R&D Center, Shinagawa, Tokyo)  
* **ตัวละคร:** คิมุระ (หัวหน้าฝ่ายวิศวกรรมอาวุโส - Chief Reviewer) และ ธนพล (วิศวกรออกแบบระบบ FPGA - RTL Designer)

```
木村技師長 (Kimura):
「タナポンさん、5G RRUのベースバンド処理モジュールのタイミング解析結果を見ました。
WNSは+0.35nsでセットアップは合格していますが、WHS（Worst Hold Slack）が『-0.12ns』になっていますよ！
THSもマイナス値を示しているのに、なぜインプリメンテーション完了として承認申請を出したのですか？」
(คุณธนพลครับ ผมดูผลการวิเคราะห์ไทม์มิ่งของโมดูลเบสแบนด์ 5G RRU แล้วครับ
ค่า WNS อยู่ที่ +0.35ns ฝั่ง Setup สอบผ่านดี แต่ทำไมค่า WHS (Worst Hold Slack) ถึงติดลบ '-0.12ns' ล่ะครับ!
ค่า THS ก็ติดลบอยู่ชัดๆ ทำไมถึงส่งเรื่องขออนุมัติว่า Implement เสร็จสมบูรณ์แล้วล่ะครับ?)

タナポン (Thanapon):
「申し訳ありません。動作周波数は245.76MHzですが、セットアップスラックに十分な余裕があったため、
実機で動かしてみて問題があれば、クロック周波数を少し落として調整すればカバーできると判断しました。」
(ขออภัยด้วยครับ พอดีความถี่ทำงานมันคือ 245.76MHz แล้วเห็นว่า Setup Slack มันเหลือ Margin พอสมควร
ผมเลยคิดว่าเดี๋ยวลองเอาไปรันบนบอร์ดจริงดู ถ้ามีปัญหาก็ค่อยลดความถี่ Clock ลงนิดหน่อยก็น่าจะครอบคลุมได้ครับ)

木村技師長 (Kimura):
「なんと恐ろしい勘違いをしているのですか！
セットアップ違反なら周波数を下げれば救済できますが、ホールド違反は『クロック周期（Tperiod）』に
一切依存しない物理現象です！
周波数を1MHzまで下げようが、0.1Hzまで落とそうが、データが早すぎてホールド時間を破壊している事実は
1ミリも変わりません！ シリコン上で100%データが化けます！
ホールド違反を放置して出荷するなど、爆弾を抱えたまま客先に納品するようなものです。
直ちにFast Cornerにおける配線遅延を調査し、ルーターのホールド修正オプションを適用して
WHSをプラス領域へ収束させなさい！」
(นี่คุณกำลังเข้าใจผิดอย่างน่ากลัวมากเลยนะครับ!
ถ้าเป็น Setup Violation คุณยังพอลดความถี่เพื่อช่วยชีวิตได้ แต่วงจร Hold Violation มันเป็นปรากฏการณ์ทางฟิสิกส์
ที่ 'ไม่ขึ้นกับคาบเวลาของสัญญาณนาฬิกา (Tperiod)' เลยแม้แต่น้อยนะครับ!
ต่อให้คุณลดความถี่ลงเหลือ 1MHz หรือเหลือ 0.1Hz แต่ความจริงที่ว่าข้อมูลมันวิ่งเร็วเกินไปจนเหยียบขอบ Hold Time
มันไม่ได้เปลี่ยนไปเลยแม้แต่มิลลิเมตรเดียวครับ! ข้อมูลจะพังบนซิลิคอนจริง 100%!
การปล่อยให้ Hold Violation หลุดรอดไปส่งมอบ มันเหมือนการกอดระเบิดเวลาไปส่งให้ลูกค้านะครับ!
จงรีบไปตรวจสอบความล่าช้าของสายใน Fast Corner แล้วเปิดออปชัน Hold Fix ของเราเตอร์
เพื่อดึงค่า WHS กลับมาเป็นบวกเดี๋ยวนี้เลยครับ!)
```

---

#### สถานการณ์ที่ 2: การตรวจสอบความไม่แน่นอนของสัญญาณนาฬิกา (Clock Uncertainty Verification)
```
木村技師長 (Kimura):
「修正後のレポートでWHSが+0.04nsに改善されたことを確認しました。
次はクロック不確定性（Clock Uncertainty）の設定です。
XDCファイル内で『set_clock_uncertainty 0』と上書きされている箇所がありますが、これは何ですか？」
(รายงานที่แก้ไขแล้ว WHS ดีขึ้นเป็น +0.04ns ยืนยันเรียบร้อยครับ
ต่อไปเป็นการตรวจการตั้งค่า Clock Uncertainty ครับ
ในไฟล์ XDC มีจุดที่ถูกเขียนทับว่า 'set_clock_uncertainty 0' ตรงนี้คืออะไรครับ?)

タナポン (Thanapon):
「はい、タイミングスラックがギリギリだったため、Vivadoが自動計算したMMCMのジッタマージン（約120ps）を
無効化してスラックを稼ぐために記述しました。」
(ครับ พอดีตอนแรก Timing Slack มันเฉียดฉิวมาก ผมเลยเขียนปิดค่า Jitter Margin ของ MMCM (ประมาณ 120ps)
ที่ Vivado คำนวณให้อัตโนมัติ เพื่อเพิ่มตัวเลข Slack ให้ดูผ่านน่ะครับ)

木村技師長 (Kimura):
「そんな数値の偽装は絶対に認められません！
MMCMのVCOジッタや電源ノイズによる位相変動は、物理的に確実に存在します。
制約上でゼロにしたところで、現実のチップ上でジッタが消えるわけではありません！
これをやると、試作基板では動いても、電源電圧が揺れた量産機で歩留まりが全滅します。
直ちにJitter設定を復元し、代わりにロジックのパイプライン化でスラックを稼ぎなさい。」
(การตกแต่งตัวเลขหลอกตัวเองแบบนั้นผมไม่อนุมัติเด็ดขาดครับ!
VCO Jitter ของ MMCM หรือการแกว่งของเฟสจาก Noise บนรางจ่ายไฟ มันมีอยู่จริงทางกายภาพอย่างแน่นอนครับ
การที่คุณไปสั่งเป็นศูนย์ในไฟล์คอนสเตรนต์ ไม่ได้ทำให้ Jitter บนชิปจริงหายไปนะครับ!
ถ้าทำแบบนี้ บอร์ดทดลองอาจจะรอด แต่พอนำไปผลิตล็อตใหญ่ที่มีแรงดันกระเพื่อม ยอด Yield จะพังพินาศยับเยินครับ!
รีบไปกู้คืนค่า Jitter ให้ถูกต้อง แล้วใช้วิธีแทรกไปป์ไลน์ในลอจิกเพื่อเพิ่ม Slack แทนเดี๋ยวนี้ครับ!)
```

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณ Setup Slack ภายใต้ผลกระทบของ Clock Skew และ Clock Uncertainty

#### โจทย์คำถาม:
ในวงจรประมวลผล DSP ความเร็วสูง เส้นทางข้อมูลเชื่อมต่อระหว่างรีจิสเตอร์ต้นทาง (Launch FF) และรีจิสเตอร์ปลายทาง (Capture FF) ทำงานที่ความถี่สัญญาณนาฬิกา $f_{clk} = 300\text{ MHz}$ ($T_{period} = 3.333\text{ ns}$)

จากการวิเคราะห์ Static Timing Analysis (STA) ที่สภาวะ **Slow Corner (Worst-Case)** พบพารามิเตอร์ทางกายภาพดังนี้:
* ความล่าช้าของสัญญาณนาฬิกาไปยัง Launch FF: $T_{launch\_clk} = 1.850\text{ ns}$
* ความล่าช้าของสัญญาณนาฬิกาไปยัง Capture FF: $T_{capture\_clk} = 2.150\text{ ns}$
* ค่า Clock-to-Out สูงสุดของ Launch FF: $T_{cko\_max} = 0.380\text{ ns}$
* ค่าความล่าช้ารวมของ Combinational Logic และ Interconnect สายส่ง: $T_{data\_max} = 2.450\text{ ns}$
* ค่า Setup Time ของ Capture FF: $T_{setup} = 0.120\text{ ns}$
* ค่าความไม่แน่นอนของสัญญาณนาฬิการวม (Clock Uncertainty: Jitter + Phase Error): $T_{uncertainty} = 0.140\text{ ns}$

จงคำนวณหา:
1. ค่า Clock Skew ($\Delta T_{skew}$) ระหว่างสองรีจิสเตอร์นี้ (และระบุว่าเป็น Positive หรือ Negative Skew)
2. ค่า Data Arrival Time ($T_{arrival}$)
3. ค่า Data Required Time ($T_{required}$)
4. ค่า Setup Slack ($\text{Slack}_{setup}$) ของเส้นทางนี้ และระบุว่าผ่านเกณฑ์ไทม์มิ่งหรือไม่

* ก. $\Delta T_{skew} = +0.300\text{ ns}$ (Positive Skew), $T_{arrival} = 4.680\text{ ns}$, $T_{required} = 5.223\text{ ns}$, $\text{Slack}_{setup} = +0.543\text{ ns}$ (ผ่านเกณฑ์)
* ข. $\Delta T_{skew} = -0.300\text{ ns}$ (Negative Skew), $T_{arrival} = 4.680\text{ ns}$, $T_{required} = 4.623\text{ ns}$, $\text{Slack}_{setup} = -0.057\text{ ns}$ (ไม่ผ่านเกณฑ์)
* ค. $\Delta T_{skew} = +0.300\text{ ns}$ (Positive Skew), $T_{arrival} = 2.830\text{ ns}$, $T_{required} = 3.073\text{ ns}$, $\text{Slack}_{setup} = +0.243\text{ ns}$ (ผ่านเกณฑ์)
* ง. $\Delta T_{skew} = +0.300\text{ ns}$ (Positive Skew), $T_{arrival} = 4.680\text{ ns}$, $T_{required} = 4.923\text{ ns}$, $\text{Slack}_{setup} = +0.243\text{ ns}$ (ผ่านเกณฑ์)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณ Clock Skew ($\Delta T_{skew}$):**
$$\Delta T_{skew} = T_{capture\_clk} - T_{launch\_clk} = 2.150\text{ ns} - 1.850\text{ ns} = +0.300\text{ ns}$$
เนื่องจากสัญญาณนาฬิกามาถึง Capture FF ช้ากว่า Launch FF ค่า Skew จึงเป็น **บวก (Positive Clock Skew)** ซึ่งมีคุณสมบัติช่วยเพิ่มระยะเวลา (Margin) ให้กับ Setup Time!

**ขั้นตอนที่ 2: คำนวณ Data Arrival Time ($T_{arrival}$):**
$$T_{arrival} = T_{launch\_clk} + T_{cko\_max} + T_{data\_max}$$
$$T_{arrival} = 1.850\text{ ns} + 0.380\text{ ns} + 2.450\text{ ns} = 4.680\text{ ns}$$

**ขั้นตอนที่ 3: คำนวณ Data Required Time ($T_{required}$):**
ขอบสัญญาณนาฬิกาสำหรับ Capture เกิดขึ้นในรอบถัดไป ($T_{period}$):
$$T_{required} = T_{period} + T_{capture\_clk} - T_{setup} - T_{uncertainty}$$
$$T_{required} = 3.333\text{ ns} + 2.150\text{ ns} - 0.120\text{ ns} - 0.140\text{ ns} = 5.483\text{ ns} - 0.260\text{ ns} = 5.223\text{ ns}$$

**ขั้นตอนที่ 4: คำนวณ Setup Timing Slack ($\text{Slack}_{setup}$):**
$$\text{Slack}_{setup} = T_{required} - T_{arrival} = 5.223\text{ ns} - 4.680\text{ ns} = +0.543\text{ ns}$$
เนื่องจาก $\text{Slack}_{setup} > 0$ เส้นทางนี้จึง **สอบผ่านเกณฑ์ Setup Timing อย่างปลอดภัย!**

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ถูกต้องสมบูรณ์แบบ:** คำนวณค่าทุกพจน์ตรงตามสมการ Static Timing Analysis สากล $100\%$
* **ข้อ ข. ไม่ถูกต้อง:** เครื่องหมายของ Clock Skew สลับด้าน
* **ข้อ ค. ไม่ถูกต้อง:** ลืมรวมค่าความล่าช้าของ Clock Path ในส่วน Arrival Time
* **ข้อ ง. ไม่ถูกต้อง:** คำนวณ Required Time ผิดพลาด

**คำตอบที่ถูกต้อง:** **ข้อ ก.**

---

### ข้อที่ 2: การวิเคราะห์ Hold Timing Violation ในสภาวะ Fast Corner (Sub-Zero Fast Path Analysis)

#### โจทย์คำถาม:
จากวงจรเดิมในข้อที่ 1 เมื่อนำมารันการวิเคราะห์ Static Timing Analysis ที่สภาวะ **Fast Corner (Worst-Case for Hold Time)** ที่อุณหภูมิ $-40^\circ\text{C}$ และแรงดันไฟฟ้าสูงสุด:

พบพารามิเตอร์ของ Fast Corner ดังนี้:
* ความล่าช้าของสัญญาณนาฬิกาไปยัง Launch FF: $T_{launch\_clk\_fast} = 0.950\text{ ns}$
* ความล่าช้าของสัญญาณนาฬิกาไปยัง Capture FF: $T_{capture\_clk\_fast} = 1.350\text{ ns}$
* ค่า Clock-to-Out ต่ำสุดของ Launch FF: $T_{cko\_min} = 0.150\text{ ns}$
* ค่าความล่าช้ารวมต่ำสุดของ Combinational Logic และสายส่ง: $T_{data\_min} = 0.320\text{ ns}$
* ค่า Hold Time ของ Capture FF: $T_{hold} = 0.090\text{ ns}$
* ค่าความไม่แน่นอนของสัญญาณนาฬิกาฝั่ง Hold: $T_{uncertainty\_hold} = 0.060\text{ ns}$

จงคำนวณหา:
1. ค่า Clock Skew ในสภาวะ Fast Corner ($\Delta T_{skew\_fast}$)
2. ค่า Data Arrival Time ฝั่ง Hold ($T_{arrival\_hold}$)
3. ค่า Data Required Time ฝั่ง Hold ($T_{required\_hold}$)
4. ค่า Hold Slack ($\text{Slack}_{hold}$) และระบุว่าเกิด Hold Violation หรือไม่

* ก. $\Delta T_{skew\_fast} = +0.400\text{ ns}$, $T_{arrival\_hold} = 1.420\text{ ns}$, $T_{required\_hold} = 1.500\text{ ns}$, $\text{Slack}_{hold} = -0.080\text{ ns}$ (เกิด Hold Violation!)
* ข. $\Delta T_{skew\_fast} = +0.400\text{ ns}$, $T_{arrival\_hold} = 1.420\text{ ns}$, $T_{required\_hold} = 1.350\text{ ns}$, $\text{Slack}_{hold} = +0.070\text{ ns}$ (ผ่านเกณฑ์)
* ค. $\Delta T_{skew\_fast} = -0.400\text{ ns}$, $T_{arrival\_hold} = 1.420\text{ ns}$, $T_{required\_hold} = 1.500\text{ ns}$, $\text{Slack}_{hold} = -0.080\text{ ns}$ (เกิด Hold Violation!)
* ง. $\Delta T_{skew\_fast} = +0.400\text{ ns}$, $T_{arrival\_hold} = 0.470\text{ ns}$, $T_{required\_hold} = 0.550\text{ ns}$, $\text{Slack}_{hold} = -0.080\text{ ns}$ (เกิด Hold Violation!)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณ Clock Skew ในสภาวะ Fast Corner:**
$$\Delta T_{skew\_fast} = T_{capture\_clk\_fast} - T_{launch\_clk\_fast} = 1.350\text{ ns} - 0.950\text{ ns} = +0.400\text{ ns}$$
สังเกตว่า Positive Skew ที่เคยช่วยให้ Setup Time ผ่านในข้อที่ 1 ได้กลายมาเป็น **ศัตรูตัวร้ายของ Hold Time** ในข้อนี้!

**ขั้นตอนที่ 2: คำนวณ Data Arrival Time ฝั่ง Hold:**
$$T_{arrival\_hold} = T_{launch\_clk\_fast} + T_{cko\_min} + T_{data\_min}$$
$$T_{arrival\_hold} = 0.950\text{ ns} + 0.150\text{ ns} + 0.320\text{ ns} = 1.420\text{ ns}$$

**ขั้นตอนที่ 3: คำนวณ Data Required Time ฝั่ง Hold:**
การตรวจสอบ Hold จะตรวจสอบเทียบกับขอบนาฬิการอบเดียวกันที่ Capture FF:
$$T_{required\_hold} = T_{capture\_clk\_fast} + T_{hold} + T_{uncertainty\_hold}$$
$$T_{required\_hold} = 1.350\text{ ns} + 0.090\text{ ns} + 0.060\text{ ns} = 1.500\text{ ns}$$

**ขั้นตอนที่ 4: คำนวณ Hold Timing Slack ($\text{Slack}_{hold}$):**
$$\text{Slack}_{hold} = T_{arrival\_hold} - T_{required\_hold} = 1.420\text{ ns} - 1.500\text{ ns} = -0.080\text{ ns} = -80\text{ ps}$$
เนื่องจาก $\text{Slack}_{hold} < 0$ จึงเกิด **Hold Timing Violation อย่างชัดเจน!**  
ข้อมูลใหม่มาถึงก่อนเวลาที่กำหนดถึง $80\text{ ps}$ ทำให้เสี่ยงต่อการทำลายข้อมูลเก่าใน Capture FF หากปล่อยลงบอร์ดจริง!

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ถูกต้องสมบูรณ์แบบ:** ตัวเลขคำนวณทุกพจน์สอดคล้องกับหลักวิชาการ STA สากล $100\%$
* **ข้อ ข. ไม่ถูกต้อง:** ลืมรวมค่า $T_{hold}$ และ $T_{uncertainty}$ ใน Required Time
* **ข้อ ค. ไม่ถูกต้อง:** เครื่องหมายของ Skew ผิด
* **ข้อ ง. ไม่ถูกต้อง:** Arrival และ Required ไม่ได้คิด Clock Tree Latency (Relative Calculation แบบไม่สมบูรณ์)

**คำตอบที่ถูกต้อง:** **ข้อ ก.**

---

### ข้อที่ 3: การคำนวณความถี่สัญญาณนาฬิกาสูงสุด ($F_{max}$) และการปรับปรุง Critical Path

#### โจทย์คำถาม:
ในบล็อกประมวลผลการเข้ารหัสข้อมูล เส้นทาง Critical Path ที่มีความล่าช้าสูงสุดระหว่างสองรีจิสเตอร์มีพารามิเตอร์ดังต่อไปนี้ (วิเคราะห์ที่ Slow Corner):
* ค่า Clock-to-Out สูงสุด: $T_{cko\_max} = 0.420\text{ ns}$
* ความล่าช้าของ Combinational Logic (LUT 6 ระดับ): $T_{logic} = 1.850\text{ ns}$
* ความล่าช้าของสายส่ง Interconnect: $T_{net} = 1.630\text{ ns}$
* ค่า Setup Time ของ Capture FF: $T_{setup} = 0.150\text{ ns}$
* ค่า Clock Uncertainty: $T_{uncertainty} = 0.100\text{ ns}$
* ค่า Clock Skew สุทธิเป็นลบ (Negative Skew ทำลาย Setup): $\Delta T_{skew} = -0.250\text{ ns}$

จงคำนวณหา:
1. คาบเวลาต่ำสุดของสัญญาณนาฬิกา ($T_{period\_min}$) ที่วงจรนี้จะสามารถทำงานได้โดยไม่เกิด Setup Violation
2. ความถี่สัญญาณนาฬิกาสูงสุดทางทฤษฎี ($F_{max}$) ของบล็อกนี้
3. หากวิศวกรทำการตัดตอน Critical Path โดยการแทรก Pipeline Register ตรงกึ่งกลางของลอจิก ทำให้ $T_{logic}$ ลดลงเหลือ $0.950\text{ ns}$ และ $T_{net}$ ลดลงเหลือ $0.800\text{ ns}$ (พารามิเตอร์อื่นคงเดิม) ความถี่ $F_{max}$ ใหม่จะกลายเป็นเท่าใด?

* ก. $T_{period\_min} = 4.400\text{ ns}$, $F_{max} = 227.27\text{ MHz}$, หลัง Pipeline $F_{max} = 374.53\text{ MHz}$
* ข. $T_{period\_min} = 3.900\text{ ns}$, $F_{max} = 256.41\text{ MHz}$, หลัง Pipeline $F_{max} = 450.00\text{ MHz}$
* ค. $T_{period\_min} = 4.400\text{ ns}$, $F_{max} = 227.27\text{ MHz}$, หลัง Pipeline $F_{max} = 450.00\text{ MHz}$
* ง. $T_{period\_min} = 4.150\text{ ns}$, $F_{max} = 240.96\text{ MHz}$, หลัง Pipeline $F_{max} = 400.00\text{ MHz}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณหาคาบเวลาขั้นต่ำ ($T_{period\_min}$):**
จากสมการ Setup Slack:
$$\text{Slack}_{setup} = T_{period} + \Delta T_{skew} - (T_{cko\_max} + T_{logic} + T_{net} + T_{setup} + T_{uncertainty})$$
ที่สภาวะขีดจำกัดพอดี ($\text{Slack}_{setup} = 0$):
$$T_{period\_min} = (T_{cko\_max} + T_{logic} + T_{net} + T_{setup} + T_{uncertainty}) - \Delta T_{skew}$$
แทนค่าตัวเลข:
$$T_{period\_min} = (0.420 + 1.850 + 1.630 + 0.150 + 0.100) - (-0.250)$$
$$T_{period\_min} = 4.150\text{ ns} - (-0.250\text{ ns}) = 4.150\text{ ns} + 0.250\text{ ns} = 4.400\text{ ns}$$
*(สังเกตว่า Negative Skew ทำให้วงจรต้องการคาบเวลาที่ยาวขึ้นอีก $0.250\text{ ns}$)*

**ขั้นตอนที่ 2: คำนวณความถี่สูงสุด $F_{max}$ เดิม:**
$$F_{max} = \frac{1}{T_{period\_min}} = \frac{1}{4.400 \times 10^{-9}\text{ s}} \approx 227,272,727\text{ Hz} \approx 227.27\text{ MHz}$$

**ขั้นตอนที่ 3: คำนวณคาบเวลาและความถี่ใหม่หลังแทรก Pipeline Register:**
ความล่าช้าใหม่ของเส้นทาง:
$$T_{period\_min\_new} = (T_{cko\_max} + T_{logic\_new} + T_{net\_new} + T_{setup} + T_{uncertainty}) - \Delta T_{skew}$$
แทนค่า:
$$T_{period\_min\_new} = (0.420 + 0.950 + 0.800 + 0.150 + 0.100) - (-0.250)$$
$$T_{period\_min\_new} = 2.420\text{ ns} + 0.250\text{ ns} = 2.670\text{ ns}$$
คำนวณ $F_{max}$ ใหม่:
$$F_{max\_new} = \frac{1}{2.670 \times 10^{-9}\text{ s}} \approx 374,531,835\text{ Hz} \approx 374.53\text{ MHz}$$

การแทรก Pipeline Register เพียง 1 สเตจ ช่วยปลดล็อกให้ความถี่ของวงจรพุ่งขึ้นจาก $227.27\text{ MHz}$ เป็น $374.53\text{ MHz}$ (เพิ่มขึ้นถึง $64.8\%$)!

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ถูกต้องสมบูรณ์แบบ:** คำนวณคาบเวลาเดิม $4.400\text{ ns}$, ความถี่เดิม $227.27\text{ MHz}$ และความถี่ใหม่ $374.53\text{ MHz}$ ถูกต้องตามหลัก STA $100\%$
* **ข้อ ข. ไม่ถูกต้อง:** ลืมคิดผลกระทบของ Negative Skew
* **ข้อ ค. ไม่ถูกต้อง:** ความถี่หลัง Pipeline คำนวณผิด
* **ข้อ ง. ไม่ถูกต้อง:** นำ Negative Skew ไปหักลบแทนที่จะบวกเพิ่ม

**คำตอบที่ถูกต้อง:** **ข้อ ก.**
