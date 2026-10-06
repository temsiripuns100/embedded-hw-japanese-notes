# Lesson 162: FPGA Timing Closure Part 2 - Clock Skew, Clock Latency & Dedicated Clock Tree Networks (BUFG, BUFGCE, BUFG_GT, Clock Skew Physics, Clock Root Relocation & Hold-Fix Buffer Hazards)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 โครงข่ายกระจายสัญญาณนาฬิการะดับซิลิคอน (Dedicated Silicon Clock Distribution Grid)
ในสถาปัตยกรรม FPGA สมัยใหม่ระดับ Xilinx UltraScale/UltraScale+ (16nm FinFET) และ Versal ACAP (7nm) สัญญาณนาฬิกาไม่ได้ถูกส่งผ่านสายเชื่อมต่อทั่วไป (General Programmable Interconnect) แต่เดินทางผ่าน **โครงข่ายกระจายสัญญาณนาฬิกาเฉพาะทาง (Dedicated Global Clock Grid)** ที่ฝังแน่นอยู่ในชั้นโลหะหนาพิเศษระดับบนของแผ่นซิลิคอน เพื่อควบคุมความล่าช้า (Insertion Delay) และลดทอนความเบี่ยงเบนทางเวลา (Clock Skew) ให้ต่ำที่สุด:

```
                  สถาปัตยกรรม CLOCK GRID ใน ULTRASCALE+
                  
             ┌─────────────────────────────────────────────────┐
             │ CLOCK ROOT (จุดกำเนิดการกระจาย สมมาตรซ้าย-ขวา)    │
             └────────────────────────┬────────────────────────┘
                                      │ (Vertical Clock Spine)
                      ┌───────────────┴───────────────┐
                      ▼                               ▼
             [ Clock Region X0Y1 ]           [ Clock Region X1Y1 ]
             ┌───────────────────┐           ┌───────────────────┐
             │ Horizontal Tracks │           │ Horizontal Tracks │
             └─────────┬─────────┘           └─────────┬─────────┘
                       │                               │
                       ▼ (Leaf Clock Pins)             ▼ (Leaf Clock Pins)
                  [ Slice FFs ]                   [ Slice FFs ]
```

#### พรีมิทิฟบัฟเฟอร์สัญญาณนาฬิกาหลัก (Clock Buffer Primitives):
1. **`BUFGCE` (Global Clock Buffer with Clock Enable):** บัฟเฟอร์สัญญาณนาฬิกาหลักของชิป สามารถขับสายสัญญาณนาฬิกาข้ามไปยังทุก Clock Region บน Die ได้ และมีขา Enable สำหรับทำ Clock Gating ในระดับฮาร์ดแวร์เพื่อประหยัดพลังงาน
2. **`BUFGCTRL` (Global Clock Control):** วงจรสวิตช์มัลติเพล็กเซอร์สัญญาณนาฬิกาแบบไร้สัญญาณรบกวน (Glitchless Clock Multiplexer) เหมาะสำหรับการสลับแหล่งกำเนิด Clock ระหว่าง Primary และ Backup
3. **`BUFG_GT` (Gigabit Transceiver Clock Buffer):** บัฟเฟอร์ความเร็วสูงพิเศษสำหรับรับสัญญาณนาฬิกาจาก Multi-Gigabit SerDes Transceivers (GTH/GTY) พร้อมวงจรหารความถี่ในตัว ($/1, /2, /4, /8$) โดยตรง

---

### 1.2 กายวิภาคของ Clock Latency และ Clock Skew (Clock Tree Physics)

ในการวิเคราะห์ STA เวลาที่สัญญาณนาฬิกาเดินทางจากแหล่งกำเนิด (เช่น ออสซิลเลเตอร์ภายนอก) ไปจนถึงขา $CLK$ ของฟลิปฟล็อปใดๆ ถูกเรียกว่า **Clock Insertion Delay (หรือ Clock Latency)**:

$$T_{clk\_latency} = T_{source\_latency} + T_{network\_latency}$$
* **$T_{source\_latency}$:** ความล่าช้าก่อนเข้าชิป หรือความล่าช้าภายในวงจร PLL/MMCM
* **$T_{network\_latency}$:** เวลาที่สัญญาณใช้ในการเดินทางผ่านบัฟเฟอร์ BUFG, เส้นทาง Clock Spine, และกระจายลงสู่ Leaf Pins ของแต่ละฟลิปฟล็อป

```
                   กายวิภาคของ POSITIVE SKEW VS NEGATIVE SKEW
                   
    [ กรณีที่ 1: POSITIVE CLOCK SKEW (T_capture > T_launch) ]
    Launch CLK  : ──/‾‾‾\_________________ (มาถึงก่อน)
    Capture CLK : ───────/‾‾‾\____________ (มาถึงทีหลัง: Delta T_skew > 0)
    ===> ผลลัพธ์: ยืดเวลาให้ SETUP TIME ทำงานง่ายขึ้น (กู้ชีพ Critical Path)
                  แต่... บีบให้ HOLD TIME อันตรายขึ้นอย่างรุนแรง! (Hold Risk)
    
    [ กรณีที่ 2: NEGATIVE CLOCK SKEW (T_capture < T_launch) ]
    Launch CLK  : ───────/‾‾‾\____________ (มาถึงทีหลัง)
    Capture CLK : ──/‾‾‾\_________________ (มาถึงก่อน: Delta T_skew < 0)
    ===> ผลลัพธ์: ปลอดภัยจาก HOLD VIOLATION 100%
                  แต่... กินเนื้อเวลาของ SETUP TIME ทำให้ Fmax ลดลง! (Setup Penalty)
```

#### นิยามเชิงคณิตศาสตร์ของ Clock Skew:
$$\Delta T_{skew} = T_{capture\_clk} - T_{launch\_clk}$$

* **ผลต่อ Setup Slack:**
  $$\text{Slack}_{setup} \propto +\Delta T_{skew}$$
  (Positive Skew ช่วยเพิ่ม Setup Margin)
* **ผลต่อ Hold Slack:**
  $$\text{Slack}_{hold} \propto -\Delta T_{skew}$$
  (Positive Skew ทำลาย Hold Margin โดยตรง!)

---

### 1.3 กลไกการย้ายจุดศูนย์กลางสัญญาณนาฬิกา (USER_CLOCK_ROOT Optimization)

ในสถาปัตยกรรม UltraScale+ การกระจายสัญญาณนาฬิกาจะเริ่มต้นจากจุดศูนย์กลางที่เรียกว่า **Clock Root**:
* โดยค่าเริ่มต้น ซอฟต์แวร์ Vivado จะเลือกตำแหน่ง Clock Root ให้อยู่กึ่งกลางของพื้นที่ที่ใช้งานสัญญาณนาฬิกานั้นๆ
* แต่หากการออกแบบมีลอจิกกระจายตัวไม่สมมาตร (เช่น ฝั่ง Launch อยู่ใน Clock Region `X0Y0` แต่ฝั่ง Capture อยู่ใน `X3Y4`) การปล่อยให้เครื่องมือเลือก Clock Root แบบสุ่ม อาจทำให้เกิด Clock Skew สูงถึง **$1.5\text{ ns} - 2.5\text{ ns}$**!

```
                  การปรับเปลี่ยนตำแหน่ง USER_CLOCK_ROOT
                  
   [ สภาวะแย่: Clock Root วางริมขอบ ]        [ สภาวะเหมาะสม: Clock Root วางกึ่งกลาง ]
   Root ──► Region 0 ──► Region 1 ──► Region 2       Region 0 ◄── Root ──► Region 1
   Skew = T_reg2 - T_reg0 = มหาศาล! (2.2ns)          Skew สมมาตรซ้ายขวา = ต่ำมาก! (< 150ps)
```

วิศวกรสามารถใช้คำสั่ง XDC บังคับย้ายตำแหน่ง Clock Root ไปยัง Clock Region ที่เหมาะสมที่สุด เพื่อปรับสมดุลความยาวสายและบดขยี้ Clock Skew ลงเหลือต่ำกว่า $200\text{ ps}$:

```tcl
# บังคับย้าย Clock Root ไปไว้ที่กึ่งกลางของ Die เพื่อลด Skew ข้ามโซน
set_property USER_CLOCK_ROOT X2Y2 [get_nets -hierarchical -filter {NAME =~ *clk_core_bufg*}]
```

---

### 1.4 ปรากฏการณ์ลูกโซ่ทำลายล้าง: Hold-Fix Buffer Explosion & The Push-Pull Effect

> [!CAUTION]
> **ภัยพิบัติของการใช้ General Routing เป็นสาย Clock (Fabric Clock Trap):**  
> ข้อผิดพลาดร้ายแรงที่สุดคือการสร้างสัญญาณนาฬิกาจาก LUT หรือ Register (เช่น วงจรหารความถี่ด้วยลอจิก) แล้วต่อเข้าฟลิปฟล็อปโดย **ไม่ผ่าน BUFGCE**!  
> สัญญาณนาฬิกาจะถูกบังคับให้วิ่งผ่านสายลอจิกธรรมดา ซึ่งไม่มีการปรับสมดุลความล่าช้า ทำให้เกิด Clock Skew ข้ามชิปสูงถึง **$3.0\text{ ns} - 5.0\text{ ns}$**!

เมื่อเกิด Hold Violation มหาศาลจาก Clock Skew เครื่องมือ Routing (Vivado Router) จะพยายามแก้ปัญหาโดยอัตโนมัติด้วยกลไก **Hold-Fix Buffer Insertion**:

```
                 กลไกการแทรก HOLD-FIX BUFFERS ของ ROUTER
                 
   Launch FF ──► [ LUT Delay Buffer ] ──► [ Route Detour (ขดสายอ้อม) ] ──► Capture FF
                 (เพิ่มความล่าช้า 1.5ns)   (เพิ่มความจุไฟฟ้า C_wire)
```

#### หายนะของ Push-Pull Effect (ความขัดแย้งระหว่าง Hold และ Setup):
1. เพื่อแก้ Hold Violation บนเส้นทางที่วิ่งเร็ว Router จะแทรก LUT6 ทำหน้าที่เป็น Delay Buffer นับพันตัว หรือสั่งให้สายไฟวิ่งอ้อมขดไปมาข้ามหลาย Clock Regions
2. การแทรก Delay Buffers และ Route Detours มหาศาล ก่อให้เกิดความแออัดของสายสัญญาณพุ่งทะลุพิกัด (**Routing Congestion > 95%**)
3. สายไฟที่ถูกขดอ้อมจะไปเบียดบังช่องทางเดินสายของเส้นทางวิกฤต (Critical Paths) ของ Setup Time
4. ผลลัพธ์: Hold Violation ได้รับการแก้ไข แต่ **Setup Violation ระเบิดขึ้นมาแทนที่ (WNS ติดลบมหาศาล)!** กลายเป็นวงจรอุบาทว์ที่ทำให้ Place & Route ลูปไม่รู้จบและคอมไพล์ไม่ผ่าน!

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: เรดาร์ Phased-Array เสียหายจาก Hold-Fix Buffer นับหมื่นตัว (Phased-Array Radar Routing Congestion Explosion)

```
+----------------------------------------------------------------------------------------------------+
| กรณีศึกษาความล้มเหลวหน้างาน (現場の失敗事例)                                                                 |
| เหตุการณ์: ระบบประมวลผลสัญญาณเรดาร์ดิจิทัล 64 ช่องสัญญาณ (AESA Radar Digital Beamformer) บน UltraScale+     |
| อาการ: ขั้นตอน Implementation ของ Vivado ค้างอยู่ที่ขั้นตอน 'Route Design' นานกว่า 14 ชั่วโมง              |
|        และจบลงด้วยความล้มเหลวอย่างสิ้นเชิง: Routing Congestion พุ่งสูงถึง 99.4% ในโซน X2Y2 ถึง X3Y3        |
|        พร้อมรายงานว่าเครื่องมือพยายามแทรก LUT Delay Buffers มากกว่า 16,000 ตัวเพื่อแก้ Hold Timing!           |
+----------------------------------------------------------------------------------------------------+
```

#### การวิเคราะห์หาสาเหตุรากเหง้าด้วยหลักการ 5 Whys (5 Whys Root Cause Analysis):

1. **ทำไมขั้นตอน Route Design จึงเกิด Routing Congestion พุ่งสูงถึง 99.4% และคอมไพล์ล้มเหลว?**  
   *คำตอบ:* ทรัพยากรสายส่งสัญญาณในแกนแนวนอนและแนวตั้งถูกใช้งานจนหมดเกลี้ยง (Over-congested) จากการแทรกสายอ้อมแก้ Hold

2. **ทำไม Vivado จึงแทรก LUT Delay Buffers มากถึง 16,000 ตัวลงในวงจร?**  
   *คำตอบ:* มีเส้นทางข้อมูลมากกว่า 25,000 เส้นทางในระบบเชื่อมโยงระหว่างโมดูลรับข้อมูล ADC กับโมดูล Beamforming ติดลบค่า Hold Slack รุนแรง ($\text{WHS} = -2.85\text{ ns}$)

3. **ทำไมเส้นทางข้อมูลจำนวนมากจึงเกิด Hold Violation รุนแรงถึง $-2.85\text{ ns}$?**  
   *คำตอบ:* เกิด **Clock Skew ขนาดมหาศาลถึง $3.40\text{ ns}$** ระหว่างฟลิปฟล็อปต้นทางและปลายทาง ทั้งๆ ที่ทำงานด้วยความถี่เดียวกัน ($250\text{ MHz}$)

4. **ทำไม Clock Skew จึงสูงถึง $3.40\text{ ns}$ ทั้งที่อยู่ในชิปเดียวกัน?**  
   *คำตอบ:* สัญญาณนาฬิกาของวงจร ADC ไม่ได้ถูกขับผ่านโครงข่าย Clock Tree เฉพาะทาง แต่ถูกขับออกมาจากโมดูลหารความถี่ใน RTL ที่เขียนโดยใช้เคาน์เตอร์ธรรมดา:  
   `always @(posedge clk_master) clk_adc_div <= ~clk_adc_div;`  
   แล้วลากสายสัญญาณ `clk_adc_div` ไปจ่ายให้แก่ฟลิปฟล็อปหลายพันตัวผ่าน Programmable Fabric Routing!

5. **ทำไมทีมงานจึงไม่ต่อสัญญาณเข้าบัฟเฟอร์ `BUFGCE`?**  
   *คำตอบ:* วิศวกรผู้รับผิดชอบเห็นว่าชิปมีสัญญาณนาฬิกาหลายโดเมน จึงกลัวว่าทรัพยากร BUFG จะหมด (BUFG Depletion) จึงจงใจละเว้นการต่อ BUFG เข้ากับ Clock ตัวนี้ โดยไม่ตระหนักว่าสัญญาณนาฬิกาที่วิ่งบน Fabric Routing จะถูกทำลายด้วย Skew ระดับหายนะ!

---

### 2.2 ผังภูมิก้างปลาวิเคราะห์ปัญหา (Ishikawa Fishbone Diagram)

```
                       ผังภูมิก้างปลาวิเคราะห์สาเหตุ HOLD BUFFER EXPLOSION
                       
   [ ความเข้าใจผิดด้านวิศวกรรม (Mindset) ]          [ สถาปัตยกรรมสัญญาณนาฬิกา (Architecture) ]
   กลัว BUFG หมด จึงเลี่ยงการใช้บัฟเฟอร์            ใช้สัญญาณจาก Flip-Flop ขับเป็น Clock ตรงๆ
             \                                           \
              \                                           \
               \                                           \  สัญญาณวิ่งบน Fabric Routing
   เข้าใจผิดว่าความถี่ 250MHz วิ่งบน Fabric ได้                 เกิด Clock Skew มหาศาล (> 3.4ns)
                 \                                           \
                  +-------------------------------------------+
                  |                                           |
                  |   HOLD-FIX 16,000 BUFFERS ROUTE COLLAPSE  | =====> [ FAILURE! ]
                  |                                           |
                  +-------------------------------------------+
                 /                                           /
                /                                           /  Router แทรก Delay Buffers มหาศาล
   ขาดการกำหนดข้อจำกัด Max Clock Skew ในไฟล์ XDC                สาย Detour ก่อให้เกิด Congestion 99%
              /                                           /
   [ การกำหนดคอนสเตรนต์ (Constraints) ]             [ เครื่องมือและการจัดสรรทรัพยากร (Tools) ]
```

---

### 2.3 คู่มือปฏิบัติงาน SOP: การออกแบบโครงข่ายสัญญาณนาฬิกาและขจัด Hold Buffer ระดับมืออาชีพ (Zero-Skew SOP)

#### สเต็ปที่ 1: บังคับใช้ Clock Buffer เฉพาะทางสำหรับสัญญาณนาฬิกาทุกเส้น (Strict Dedicated Buffering)
* สัญญาณใดๆ ก็ตามที่ต่อเข้าขา Clock (`.C` หรือ `.CLK`) ของฟลิปฟล็อปหรือหน่วยความจำ **ต้องมาจากเอาต์พุตของบัฟเฟอร์ `BUFGCE`, `BUFGCTRL`, หรือ `BUFG_GT` เท่านั้น $100\%$**:

```verilog
// รูปแบบที่ถูกต้องในการสร้างสัญญาณนาฬิกาหารสองโดยไม่ใช้ Fabric Clocking
// ใช้ BUFGCE ร่วมกับขาสัญญาณ CE เพื่อทำ Clock Gating / Division
wire clk_div2;
BUFGCE #(
    .SIM_DEVICE("ULTRASCALE_PLUS")
) u_bufgce_div (
    .I  (clk_master),
    .CE (div2_enable), // Toggle ทุกๆ 1 ไซเคิล
    .O  (clk_div2)
);
```

#### สเต็ปที่ 2: ตรวจสอบรายงาน Clock Networks ใน Vivado
* รันคำสั่งตรวจสอบโครงข่ายสัญญาณนาฬิกาทั้งหมด:
  `report_clock_networks -file clock_networks.rpt`
* ตรวจสอบว่าในคอลัมน์ **"Clock Type"** ต้องแสดงเป็น **Global Clock (BUFG)** ทุกเส้น ห้ามมีเส้นใดแสดงเป็น **Local Clock (Fabric Interconnect)** เด็ดขาด!

#### สเต็ปที่ 3: ตรวจสอบและปรับแต่งตำแหน่ง Clock Root
* ตรวจสอบค่า Clock Skew ในรายงานไทม์มิ่ง หากพบว่า Skew ข้าม Clock Region สูงเกินกว่า $500\text{ ps}$ ให้ทำการย้าย Clock Root ไปยังตำแหน่งศูนย์กลางของโหลด:
  `report_clock_utilization -clock_roots -file clock_roots.rpt`
* กำหนดคำสั่ง `USER_CLOCK_ROOT` ในไฟล์ XDC ดังที่ระบุในหัวข้อ 1.3

#### สเต็ปที่ 4: การตั้งค่า Router ไม่ให้แทรก Hold Buffer จนเกิด Congestion
* ป้องกันไม่ให้ Router แก้ Hold จนทำลาย Setup Time โดยกำหนดนโยบาย Directive ในการ Route:
  `route_design -directive Explore` หรือใช้ `route_design -tns_cleanup`
* ตรวจสอบให้แน่ใจว่าค่า WHS และ WNS สมดุลกันโดยไม่มีการสร้าง Delay Buffer แปลกปลอมเกิน 50 ตัวในทั้งโปรเจกต์

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง

| คำศัพท์คันジ / คาตากานะ | คำอ่าน (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- |
| **クロックツリー** | Kurokku Tsurii | Clock Tree (โครงข่ายต้นไม้กระจายสัญญาณนาฬิกา) |
| **クロックバッファ** | Kurokku Baffa | Clock Buffer (บัฟเฟอร์ขับสัญญาณนาฬิกากระจายทั่วชิป) |
| **クロックスキュー** | Kurokku Sukyuu | Clock Skew (ความต่างของเวลามาถึงของสัญญาณนาฬิกา) |
| **クロックルート** | Kurokku Ruuto | Clock Root (จุดกำเนิดการกระจายสัญญาณนาฬิกาบนชิป) |
| **ホールド修復バッファ** | Hoorudo Shuufuku Baffa | Hold-Fix Delay Buffer (บัฟเฟอร์หน่วงเวลาที่แทรกเพื่อแก้ Hold) |
| **配線混雑度** | Haisen Konzatsudo | Routing Congestion (ความแออัดของสายสัญญาณในการเดินสาย) |
| **ファブリック配線クロック**| Faburikku Haisen Kurokku | Fabric-Routed Clock (สัญญาณนาฬิกาที่วิ่งบนสายลอจิกทั่วไป) |
| **有効スキュー** | Yuukou Sukyuu | Useful Skew (การจงใจเบี่ยงเบน Skew เพื่อช่วย Setup Time) |
| **挿入遅延** | Sounyuu Chien | Insertion Delay / Clock Latency (เวลาหน่วงในการเดินทางของ Clock) |
| **デトア配線** | Detoa Haisen | Route Detour (การเดินสายอ้อมเพื่อเพิ่มเวลาหน่วง) |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図の現場会話)

#### สถานการณ์ที่ 1: การตรวจพบสัญญาณนาฬิกาวิ่งบน Fabric Routing (Fabric Clock Review)
* **สถานที่:** แผนกออกแบบระบบเรดาร์ตรวจจับระยะไกล (Defense Radar System Engineering Center, Kamakura, Kanagawa)  
* **ตัวละคร:** คาวามุระ (หัวหน้าฝ่ายวิศวกรรมอาวุโส - Chief Reviewer) และ ธนา (วิศวกรออกแบบระบบ FPGA - RTL Designer)

```
川村技師長 (Kawamura):
「タナーさん、ビームフォーミング処理回路の配置配線レポートを確認しましたが、
恐ろしいことにルーターが16,000個ものLUTを『ホールド時間修復用遅延バッファ』として
勝手に挿入し、チップ中央の配線混雑度が99%に達して配置配線が破綻しています！
クロックネットワークレポートを調べたところ、ADC用サンプリングクロックがBUFGを通っておらず、
汎用ファブリック配線で駆動されていますね。これは一体どういうことですか？」
(คุณธนาครับ ผมตรวจรายงาน Place & Route ของวงจร Beamforming แล้ว
ปรากฏเรื่องน่าตกใจมากครับ ตัวเราเตอร์แอบแทรก LUT ไปถึง 16,000 ตัวเพื่อทำเป็น 'Delay Buffer ซ่อม Hold Time'
จนความแออัดของสายส่งตรงกลางชิปพุ่งทะลุ 99% และทำให้กระบวนการเดินสายพังทลายลงครับ!
พอผมเช็ค Clock Network Report พบว่า Clock แซมเปิลของ ADC ไม่ได้ต่อผ่าน BUFG แต่กลับวิ่งบนสายลอจิก Fabric ทั่วไป
นี่มันเกิดอะไรขึ้นครับ?)

タナー (Thana):
「申し訳ありません！ MMCMの出力端子が足りなくなってしまい、ロジック内でカウンタを組んで
クロック分周回路を作りました。
BUFGのリソースを節約するために、分周出力をそのままレジスタのクロック端子に直結してしまいました…」
(ขออภัยอย่างสูงครับ! พอดีขาพอร์ตเอาต์พุตของ MMCM มันไม่พอใช้ ผมเลยสร้างวงจรเคาน์เตอร์ในลอจิก
เพื่อทำเป็นวงจรหารความถี่ของสัญญาณนาฬิกาขึ้นมาครับ
แล้วเพื่อประหยัดทรัพยากร BUFG ผมเลยเอาเอาต์พุตของตัวหารนั้นต่อตรงเข้าขา Clock ของฟลิปฟล็อปเลยครับ...)

川村技師長 (Kawamura):
「なんという愚行ですか！
FPGAのファブリック配線は抵抗成分と容量成分が非常に大きく、バッファなしで数千のレジスタへ
分配すれば、クロックスキューは3ns以上にも跳ね上がります！
周期4ns（250MHz）の回路で3nsのスキューが発生すれば、後段のレジスタはデータが届く前に次のクロックで
叩かれ、全ビットで致命的なホールド違反を引き起こすのは物理の必然です！
ルーターはそれを無理やり抑え込むために、何万本もの配線を迂回させ、LUTバッファを乱造したのです。
直ちに分周ロジックの後段に『BUFGCE』を挿入し、専用クロックツリーへ乗せ換えなさい！」
(ช่างเป็นการกระทำที่อันตรายมากครับ!
สายไฟ Fabric ธรรมดาของ FPGA มันมีทั้งความต้านทานและความจุไฟฟ้าแฝงสูงมาก การลากสายไปแจกจ่ายให้ฟลิปฟล็อป
หลายพันตัวโดยไม่มีบัฟเฟอร์ Clock จะทำให้เกิด Clock Skew พุ่งสูงเกินกว่า 3ns ทันทีครับ!
ในระบบที่คาบเวลาคือ 4ns (250MHz) แต่เกิด Skew ถึง 3ns ฟลิปฟล็อปตัวหลังจะถูกขอบนาฬิกาเข้าตีแซงหน้าข้อมูลเดิม
ทำให้เกิด Hold Violation ร้ายแรงทุกบิตอย่างหลีกเลี่ยงไม่ได้ในทางฟิสิกส์ครับ!
ตัวเราเตอร์เลยจำใจต้องขดสายอ้อมโลกและสร้าง LUT Buffer ขึ้นมานับหมื่นตัวเพื่อแก้ปัญหานี้จนชิปตัน!
จงรีบนำเอาต์พุตตัวหารนั้นต่อเข้า 'BUFGCE' แล้วส่งผ่านโครงข่าย Clock Tree เฉพาะทางเดี๋ยวนี้เลยครับ!)
```

---

#### สถานการณ์ที่ 2: การปรับตำแหน่ง Clock Root เพื่อแก้ Skew ข้ามโซน
```
川村技師長 (Kawamura):
「BUFGCEの挿入により、16,000個の遅延バッファが完全に消滅しましたね。素晴らしい改善です。
しかし、タイミグレポートを見ると、依然としてスライス間のクロックスキューが約850ps残っており、
WNSがわずかにマイナス（-0.08ns）になっています。クロックルートの配置を確認しましたか？」
(การใส่ BUFGCE ทำให้ Delay Buffer 16,000 ตัวหายไปจนหมดเกลี้ยง ยอดเยี่ยมมากครับ
แต่พอตรวจ Timing Report ดู ยังพบว่ามี Clock Skew ระหว่าง Slice หลงเหลืออยู่ประมาณ 850ps
ทำให้ WNS ติดลบอยู่นิดหน่อย (-0.08ns) คุณได้ตรวจสอบตำแหน่ง Clock Root หรือยังครับ?)

タナー (Thana):
「確認したところ、Vivadoが自動配置したクロックルートが最下段のClock Region X0Y0に固定されており、
最上段のX3Y4にあるDSPブロックまでクロックが到達するのに大きな時間差が生じていました。」
(พอตรวจสอบดู พบว่า Vivado วางตำแหน่ง Clock Root อัตโนมัติไว้ที่ Clock Region X0Y0 ด้านล่างสุดครับ
ทำให้สัญญาณนาฬิกาต้องเดินทางไกลมากจนกว่าจะไปถึงบล็อก DSP ที่อยู่ด้านบนสุดที่ X3Y4 จนเกิดผลต่างเวลาสูงครับ)

川村技師長 (Kawamura):
「その通りです。XDC制約ファイルに『set_property USER_CLOCK_ROOT X2Y2』を追記し、
クロックルートをDSP配置領域の中心へ強制移動させなさい。
ツリーの配線長が上下左右で対称になれば、スキューは200ps以下に圧縮され、
セットアップスラックは確実にプラスへ転換します！」
(ถูกต้องเลยครับ จงเพิ่มคำสั่ง 'set_property USER_CLOCK_ROOT X2Y2' ลงในไฟล์ XDC
เพื่อบังคับย้าย Clock Root ไปไว้ที่กึ่งกลางของพื้นที่บล็อก DSP ทันทีครับ
เมื่อสายของต้นไม้มีความยาวสมมาตรทั้งบน-ล่าง-ซ้าย-ขวา ค่า Skew จะถูกบดขยี้เหลือต่ำกว่า 200ps
และ Setup Slack จะพลิกกลับมาเป็นบวกได้อย่างแน่นอนครับ!)
```

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การใช้ประโยชน์จาก Useful Skew เพื่อกู้ชีพ Setup Critical Path

#### โจทย์คำถาม:
ในโมดูลคำนวณ FFT ความเร็วสูง เส้นทางข้อมูลที่วิกฤตที่สุดเชื่อมต่อระหว่าง Launch FF และ Capture FF โดยระบบทำงานที่ความถี่สัญญาณนาฬิกา $f_{clk} = 400\text{ MHz}$ ($T_{period} = 2.500\text{ ns}$)

พารามิเตอร์ทางกายภาพของเส้นทางนี้ (ที่ Slow Corner) มีดังนี้:
* ค่า Clock-to-Out สูงสุด: $T_{cko\_max} = 0.350\text{ ns}$
* ความล่าช้าของ Data Path (Combinational + Net Delay): $T_{data\_max} = 2.250\text{ ns}$
* ค่า Setup Time ของ Capture FF: $T_{setup} = 0.120\text{ ns}$
* ค่า Clock Uncertainty รวม: $T_{uncertainty} = 0.100\text{ ns}$
* ในสภาวะเดิม สัญญาณนาฬิกาเดินทางถึง Launch FF และ Capture FF พร้อมกันแบบสมบูรณ์ ($\Delta T_{skew} = 0.000\text{ ns}$)

นอกจากนี้ ในสภาวะ **Fast Corner** สำหรับการตรวจสอบ Hold Time:
* ค่า Data Path ต่ำสุด: $T_{data\_min} = 0.450\text{ ns}$
* ค่า Clock-to-Out ต่ำสุด: $T_{cko\_min} = 0.120\text{ ns}$
* ค่า Hold Time ของ Capture FF: $T_{hold} = 0.080\text{ ns}$
* ค่า Hold Uncertainty: $T_{unc\_hold} = 0.050\text{ ns}$

หากสถาปัตยกรรมอนุญาตให้ใช้วิธี **Useful Skew Scheduling** โดยการหน่วงเวลาสัญญาณนาฬิกาที่ขาเข้าของ Capture FF เพื่อเพิ่มค่า Positive Skew ($\Delta T_{skew} > 0$):

จงคำนวณหา:
1. ค่า Setup Slack เดิม ($\text{Slack}_{setup\_orig}$) ก่อนทำ Useful Skew (ติดลบเท่าใด?)
2. ค่า Positive Clock Skew ขั้นต่ำที่สุด ($\Delta T_{skew\_min}$) ที่ต้องใส่เข้าไปเพื่อให้ $\text{Slack}_{setup} \ge +0.050\text{ ns}$
3. ภายใต้ค่า Skew ใหม่นี้ ค่า Hold Slack ($\text{Slack}_{hold}$) ในสภาวะ Fast Corner จะยังคงผ่านเกณฑ์ความปลอดภัยหรือไม่?

* ก. $\text{Slack}_{setup\_orig} = -0.320\text{ ns}$, ต้องการ $\Delta T_{skew} \ge +0.370\text{ ns}$, $\text{Slack}_{hold} = +0.070\text{ ns}$ (ผ่านเกณฑ์ Hold!)
* ข. $\text{Slack}_{setup\_orig} = -0.320\text{ ns}$, ต้องการ $\Delta T_{skew} \ge +0.370\text{ ns}$, $\text{Slack}_{hold} = -0.050\text{ ns}$ (ไม่ผ่านเกณฑ์ Hold!)
* ค. $\text{Slack}_{setup\_orig} = -0.220\text{ ns}$, ต้องการ $\Delta T_{skew} \ge +0.270\text{ ns}$, $\text{Slack}_{hold} = +0.170\text{ ns}$ (ผ่านเกณฑ์ Hold!)
* ง. $\text{Slack}_{setup\_orig} = -0.420\text{ ns}$, ต้องการ $\Delta T_{skew} \ge +0.470\text{ ns}$, $\text{Slack}_{hold} = -0.030\text{ ns}$ (ไม่ผ่านเกณฑ์ Hold!)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณ Setup Slack เดิมก่อนปรับ Skew ($\Delta T_{skew} = 0$):**
$$\text{Data Required Time} = T_{period} - T_{setup} - T_{uncertainty} = 2.500\text{ ns} - 0.120\text{ ns} - 0.100\text{ ns} = 2.280\text{ ns}$$
$$\text{Data Arrival Time} = T_{cko\_max} + T_{data\_max} = 0.350\text{ ns} + 2.250\text{ ns} = 2.600\text{ ns}$$
$$\text{Slack}_{setup\_orig} = T_{required} - T_{arrival} = 2.280\text{ ns} - 2.600\text{ ns} = -0.320\text{ ns}$$
เส้นทางเดิมติดลบค่า Setup Slack อยู่ $320\text{ ps}$!

**ขั้นตอนที่ 2: คำนวณหาค่า Positive Skew ขั้นต่ำที่ต้องการ ($\Delta T_{skew\_min}$):**
เมื่อใส่ Positive Skew เข้าไป:
$$\text{Slack}_{setup\_new} = \text{Slack}_{setup\_orig} + \Delta T_{skew}$$
กำหนดให้ $\text{Slack}_{setup\_new} \ge +0.050\text{ ns}$:
$$-0.320\text{ ns} + \Delta T_{skew} \ge +0.050\text{ ns}$$
$$\Delta T_{skew} \ge 0.050\text{ ns} - (-0.320\text{ ns}) = +0.370\text{ ns}$$
ดังนั้นต้องการค่า Positive Skew ขั้นต่ำคือ **$+0.370\text{ ns}$**

**ขั้นตอนที่ 3: ตรวจสอบความปลอดภัยของ Hold Slack ที่ Fast Corner:**
สมการ Hold Slack เมื่อมี Clock Skew:
$$\text{Slack}_{hold} = (T_{cko\_min} + T_{data\_min}) - \Delta T_{skew} - (T_{hold} + T_{unc\_hold})$$
แทนค่าตัวแปร:
$$\text{Data Arrival}_{hold} = 0.120\text{ ns} + 0.450\text{ ns} = 0.570\text{ ns}$$
$$\text{Data Required}_{hold} = \Delta T_{skew} + T_{hold} + T_{unc\_hold} = 0.370\text{ ns} + 0.080\text{ ns} + 0.050\text{ ns} = 0.500\text{ ns}$$
คำนวณ Slack:
$$\text{Slack}_{hold} = 0.570\text{ ns} - 0.500\text{ ns} = +0.070\text{ ns} = +70\text{ ps}$$
เนื่องจาก $\text{Slack}_{hold} > 0$ แสดงว่าการยืมเวลาด้วย Useful Skew $+0.370\text{ ns}$ สามารถช่วยกู้ชีพ Setup Time ได้สำเร็จ **โดยไม่ทำให้เกิด Hold Violation!**

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ถูกต้องสมบูรณ์แบบ:** คำนวณค่า Slack ทั้งสองสภาวะและค่า Skew ได้อย่างถูกต้องตรงตามทฤษฎี $100\%$
* **ข้อ ข. ไม่ถูกต้อง:** คำนวณ Hold Slack ผิดพลาดโดยคิดว่าติดลบ
* **ข้อ ค. ไม่ถูกต้อง:** คำนวณ Setup Slack เดิมผิดพลาด
* **ข้อ ง. ไม่ถูกต้อง:** ตัวเลข Arrival Time ผิด

**คำตอบที่ถูกต้อง:** **ข้อ ก.**

---

### ข้อที่ 2: การวิเคราะห์ผลลัพธ์ของการย้ายตำแหน่ง USER_CLOCK_ROOT ต่อค่า Clock Skew ข้ามชิป

#### โจทย์คำถาม:
ในชิป Kintex UltraScale+ วงจรประมวลผลวิดีโอมีรีจิสเตอร์กระจายตัวอยู่ใน 3 Clock Regions เรียงในแนวตั้ง ได้แก่ `X1Y0`, `X1Y1`, และ `X1Y2`  
พารามิเตอร์ความล่าช้าของสายส่งสัญญาณนาฬิกา (Clock Spine Delay) มีค่าความล่าช้าเฉลี่ย $T_{spine\_hop} = 0.450\text{ ns}$ ต่อ 1 ช่วง Clock Region และความล่าช้าในการกระจายสัญญาณภายในแต่ละ Region มีค่าผันแปรสูงสุด $\pm 0.080\text{ ns}$

* **กรณีที่ A (Default Placement):** เครื่องมือวาง Clock Root ไว้ที่ด้านล่างสุดของชิป ณ Clock Region **`X1Y0`**
* **กรณีที่ B (Optimized Placement):** วิศวกรใช้คำสั่ง XDC ย้ายตำแหน่ง Clock Root ไปไว้ที่กึ่งกลาง ณ Clock Region **`X1Y1`**

จงคำนวณหา:
1. ค่า Clock Skew สูงสุดระหว่างรีจิสเตอร์ที่เร็วที่สุดและช้าที่สุดในกรณีที่ A ($\Delta T_{skew\_A}$)
2. ค่า Clock Skew สูงสุดในกรณีที่ B ($\Delta T_{skew\_B}$)
3. เปอร์เซ็นต์การลดลงของ Clock Skew ที่ได้จากการย้าย Clock Root

* ก. $\Delta T_{skew\_A} = 1.060\text{ ns}$, $\Delta T_{skew\_B} = 0.610\text{ ns}$, ลดลงได้ $42.5\%$
* ข. $\Delta T_{skew\_A} = 0.900\text{ ns}$, $\Delta T_{skew\_B} = 0.450\text{ ns}$, ลดลงได้ $50.0\%$
* ค. $\Delta T_{skew\_A} = 1.060\text{ ns}$, $\Delta T_{skew\_B} = 0.320\text{ ns}$, ลดลงได้ $69.8\%$
* ง. $\Delta T_{skew\_A} = 0.540\text{ ns}$, $\Delta T_{skew\_B} = 0.270\text{ ns}$, ลดลงได้ $50.0\%$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: วิเคราะห์กรณีที่ A (Clock Root วางที่ X1Y0 ด้านล่างสุด):**
* ความล่าช้าไปยัง Region `X1Y0`:
  $$T_{min} = 0\text{ hops} - 0.080\text{ ns} = -0.080\text{ ns} \quad (\text{หรือเทียบสัมพันธ์เท่ากับ } T_0)$$
* ความล่าช้าไปยัง Region `X1Y2` (ห่างออกไป 2 ช่วงบล็อก):
  $$T_{max} = 2 \times T_{spine\_hop} + 0.080\text{ ns} = (2 \times 0.450\text{ ns}) + 0.080\text{ ns} = 0.900\text{ ns} + 0.080\text{ ns} = 0.980\text{ ns}$$
* ผลต่างความล่าช้าสูงสุด (Clock Skew รวมความผันแปรภายใน):
  $$\Delta T_{skew\_A} = (2 \times 0.450\text{ ns}) + (2 \times 0.080\text{ ns}) = 0.900\text{ ns} + 0.160\text{ ns} = 1.060\text{ ns}$$

**ขั้นตอนที่ 2: วิเคราะห์กรณีที่ B (Clock Root วางที่ X1Y1 ตรงกลาง):**
* เมื่อวาง Root ไว้ที่ `X1Y1`:
  * วิ่งลงไปยัง `X1Y0`: เดินทางเพียง 1 ช่วงบล็อก ($1 \times 0.450\text{ ns}$)
  * วิ่งขึ้นไปยัง `X1Y2`: เดินทางเพียง 1 ช่วงบล็อก ($1 \times 0.450\text{ ns}$)
  * อยู่ใน `X1Y1`: เดินทาง 0 ช่วงบล็อก
* ความต่างของระยะทางมากที่สุดคือระหว่างบล็อกใน Region เดียวกันกับบล็อกที่ห่างไป 1 ช่วง:
  $$\Delta T_{skew\_B} = (1 \times 0.450\text{ ns}) + (2 \times 0.080\text{ ns}) = 0.450\text{ ns} + 0.160\text{ ns} = 0.610\text{ ns}$$

**ขั้นตอนที่ 3: คำนวณเปอร์เซ็นต์การลดลงของ Clock Skew:**
$$\text{Reduction} = \frac{\Delta T_{skew\_A} - \Delta T_{skew\_B}}{\Delta T_{skew\_A}} \times 100\% = \frac{1.060\text{ ns} - 0.610\text{ ns}}{1.060\text{ ns}} \times 100\% = \frac{0.450}{1.060} \times 100\% \approx 42.45\% \approx 42.5\%$$

การย้าย Clock Root มาไว้ที่จุดศูนย์กลางสามารถบดขยี้ Clock Skew ลงได้ถึง **$42.5\%$** ซึ่งส่งผลมหาศาลต่อการปิด Setup และ Hold Timing พร้อมกัน!

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ถูกต้องสมบูรณ์แบบ:** ตัวเลข $1.060\text{ ns}$, $0.610\text{ ns}$ และเปอร์เซ็นต์ลดลง $42.5\%$ ถูกต้องครบถ้วน
* **ข้อ ข. ไม่ถูกต้อง:** ลืมคิดความผันแปรของ Leaf Pin ภายใน Region
* **ข้อ ค. ไม่ถูกต้อง:** คำนวณ Skew ของกรณี B ต่ำเกินจริง
* **ข้อ ง. ไม่ถูกต้อง:** คิดจำนวน Hop ผิดพลาด

**คำตอบที่ถูกต้อง:** **ข้อ ก.**

---

### ข้อที่ 3: การประเมินผลกระทบของการแทรก Hold-Fix Delay Buffer ต่อความแออัดของสายสัญญาณ

#### โจทย์คำถาม:
ในขั้นตอน Place & Route ของชิป FPGA ขนาดใหญ่ วงจรเกิด Hold Violation บนเส้นทางสั้นจำนวน $M = 5,000\text{ เส้นทาง}$ โดยแต่ละเส้นทางติดลบค่า Hold Slack เฉลี่ย $\text{Slack}_{hold} = -0.450\text{ ns}$

กำหนดให้:
* วงจร Router สามารถแก้ Hold Violation ได้โดยการแทรก Slice LUT ที่ต่อแบบ Buffer หรือ Route-through โดยแต่ละตัวสร้างความล่าช้าเฉลี่ย $T_{lut\_delay} = 0.200\text{ ns}$
* การแทรก LUT Delay Buffer 1 ตัว จะดึงสายสัญญาณ Interconnect เข้ามาเชื่อมต่อเพิ่มเติมเฉลี่ย $3\text{ เส้นสายส่ง}$ (Routing Wires)
* บริเวณ Clock Region ที่เกิดปัญหามีช่องทางเดินสายว่างคงเหลือ (Available Routing Tracks) ทั้งสิ้น $25,000\text{ tracks}$

จงคำนวณหา:
1. จำนวน LUT Delay Buffer ขั้นต่ำที่ต้องแทรกในแต่ละเส้นทางเพื่อให้ Hold Slack กลายเป็นบวก
2. จำนวน LUT Delay Buffer รวมทั้งหมดที่ถูกแทรกลงในชิป ($Total\_LUTs_{hold}$)
3. จำนวนสายส่งสัญญาณเพิ่มเติมที่ต้องถูกใช้ไปเพื่อเชื่อมต่อบัฟเฟอร์เหล่านี้ และเปอร์เซ็นต์ของ Routing Resource ที่ถูกกลืนกินไป

* ก. เส้นทางละ 2 ตัว, $Total\_LUTs = 10,000\text{ ตัว}$, กินสายส่ง $30,000\text{ tracks}$ ($120.0\%$ - Routing ล้นทะลัก พังทลาย!)
* ข. เส้นทางละ 3 ตัว, $Total\_LUTs = 15,000\text{ ตัว}$, กินสายส่ง $45,000\text{ tracks}$ ($180.0\%$ - Routing ล้นทะลัก พังทลาย!)
* ค. เส้นทางละ 3 ตัว, $Total\_LUTs = 15,000\text{ ตัว}$, กินสายส่ง $15,000\text{ tracks}$ ($60.0\%$ - ผ่านการเดินสาย)
* ง. เส้นทางละ 1 ตัว, $Total\_LUTs = 5,000\text{ ตัว}$, กินสายส่ง $15,000\text{ tracks}$ ($60.0\%$ - ผ่านการเดินสาย)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณจำนวน Buffer ต่อเส้นทาง:**
ความล่าช้าที่ต้องเพิ่มขึ้นเพื่อแก้ Hold Slack ติดลบ $-0.450\text{ ns}$:
$$N_{buf\_per\_path} = \left\lceil \frac{0.450\text{ ns}}{0.200\text{ ns}} \right\rceil = \lceil 2.25 \rceil = 3\text{ ตัว/เส้นทาง}$$
(การใส่ 2 ตัวจะได้เพียง $0.400\text{ ns}$ ซึ่งยังคงติดลบ $-0.050\text{ ns}$ จึงต้องใส่ 3 ตัวเพื่อเพิ่มความล่าช้า $0.600\text{ ns}$)

**ขั้นตอนที่ 2: คำนวณจำนวน LUT ทั้งหมดที่ถูกแทรก:**
$$Total\_LUTs_{hold} = 5,000\text{ paths} \times 3\text{ buffers/path} = 15,000\text{ ตัว}$$

**ขั้นตอนที่ 3: คำนวณผลกระทบต่อสายส่งสัญญาณ (Routing Consumption):**
แต่ละตัวกินสายส่ง 3 เส้น:
$$Total\_Wires = 15,000 \times 3 = 45,000\text{ routing tracks}$$
เปรียบเทียบกับทรัพยากรว่างที่มีอยู่ $25,000\text{ tracks}$:
$$\text{Utilization} = \frac{45,000}{25,000} \times 100\% = 180.0\%$$

ความต้องการสายส่งพุ่งสูงถึง **$180\%$ ของที่มีอยู่จริง!**  
นี่คือภาพสะท้อนอันชัดเจนว่าทำไมการปล่อยให้เกิด Hold Violation จำนวนมากจาก Clock Skew จึงนำไปสู่ **Routing Congestion Explosion (การระเบิดของความแออัดสายส่ง)** จนทำให้เราเตอร์ล้มเหลว $100\%$!

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ไม่ถูกต้อง:** 2 ตัวต่อเส้นทางไม่เพียงพอในการแก้ Slack ติดลบ $-0.450\text{ ns}$
* **ข้อ ข. ถูกต้องสมบูรณ์แบบ:** คำนวณ 3 ตัวต่อเส้นทาง รวม 15,000 ตัว และกินสายส่ง 45,000 tracks คิดเป็น $180\%$ ได้อย่างถูกต้องแม่นยำ
* **ข้อ ค. ไม่ถูกต้อง:** คิดจำนวนสายส่งต่อ LUT ต่ำเกินไป (คิดแค่ 1 เส้น)
* **ข้อ ง. ไม่ถูกต้อง:** 1 ตัวต่อเส้นทางไม่สามารถแก้ Hold ได้

**คำตอบที่ถูกต้อง:** **ข้อ ข.**
