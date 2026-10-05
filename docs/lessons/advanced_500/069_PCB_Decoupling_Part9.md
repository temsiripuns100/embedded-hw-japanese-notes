# Lesson 069: PCB Decoupling Part 9 - High-Frequency Decoupling Architectures and Ultra-Low ESL Technologies

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในยุคของโปรเซสเซอร์ระดับกิกะเฮิรตซ์ (เช่น AI GPUs, 112Gbps SerDes, และโปรเซสเซอร์ระดับ 3nm/5nm) สัญญาณสลับของลอจิกเกตภายในซิลิคอนดายมีเวลาขึ้นของสัญญาณสั้นลงเหลือเพียงระดับพิโกวินาที ($t_r < 50 - 150\text{ ps}$) ซึ่งสอดคล้องกับย่านความถี่ความเร็วสูงตั้งแต่ **$500\text{ MHz}$ จนถึงมากกว่า $5\text{ GHz}$**

ณ ย่านความถี่ระดับนี้ กฎเกณฑ์การส่งผ่านประจุของโครงข่ายจ่ายไฟ (PDN Charge Delivery Hierarchy) จะต้องแบ่งความรับผิดชอบตามแกนเวลาอย่างเคร่งครัด เพราะความล่าช้าจากการเดินทางของสัญญาณ (Propagation Delay $t_{prop} = \sqrt{\varepsilon_r} / c_0 \approx 6.7\text{ ps/mm}$) บวกกับความเหนี่ยวนำปรสิตของ Ball Grid Array (BGA) จะทำให้ตัวเก็บประจุบนแผ่น PCB ทั่วไป **ไม่สามารถส่งประจุไปถึงทรานซิสเตอร์ได้ทันเวลา!**

```
+-------------------------------------------------------------------------+
|              PDN Charge Delivery Timeline (Transient Windows)           |
|                                                                         |
|  [ 0 - 50 ps ]     : On-Die Deep Trench / MIM Capacitors (Inside Silicon)|
|  [ 50 ps - 500 ps ]: On-Package Caps (LSC / DSC on Substrate)           |
|  [ 500 ps - 5 ns ] : Ultra-Low ESL Caps (VIPPO / IDC / Silicon Caps)     |
|  [ 5 ns - 50 ns ]  : Standard High-Frequency MLCCs (0402 / 0201)        |
|  [ 50 ns - 2 µs ]  : Mid-Frequency & Bulk Capacitors (Tantalum / Poly)   |
|  [ > 2 µs ]        : Voltage Regulator Module (VRM Feedback Control)    |
+-------------------------------------------------------------------------+
```

### 1.1 ข้อจำกัดทางฟิสิกส์ของ BGA Ball Inductance และขอบเขตของ PCB Decoupling

บอลบัดกรีของชิป BGA (Solder Ball) ทำหน้าที่เป็นตัวเหนี่ยวนำขนาดเล็กในแนวแกน $z$ คั่นกลางระหว่างแผ่น PCB และตัวถังแพ็กเกจ IC โดยแต่ละบอลมีค่าความเหนี่ยวนำปรสิต:

$$L_{ball} \approx 0.15 - 0.35\text{ nH} \quad [\text{ต่อหนึ่งคู่ Power-Ground}]$$

เมื่อรวมกับความเหนี่ยวนำของลายทองแดงและ Micro-vias บน Package Substrate ($L_{pkg} \approx 0.2 - 0.5\text{ nH}$):
ความเหนี่ยวนำรวมระหว่างแผ่น PCB กับซิลิคอนดายคือ:
$$L_{interface} = L_{ball} + L_{pkg} \approx 0.35 - 0.85\text{ nH}$$

ความเหนี่ยวนำนี้ทำหน้าที่เป็น **ตัวกรอง Low-Pass กั้นขวางกระแสสลับความถี่สูง (Inductive Isolation)** 
ความถี่ตัดข้ามผ่านสูงสุด (Maximum Effective Cutoff Frequency) ที่ตัวเก็บประจุบนแผ่น PCB จะสามารถส่งพลังงานข้ามบอล BGA เข้าไปช่วยชิปได้คือ:

$$f_{cross(PCB)} \approx \frac{1}{2\pi \sqrt{L_{interface} \cdot C_{die}}}$$

โดยทั่วไป $f_{cross(PCB)}$ จะมีค่าอยู่ที่ประมาณ **$150\text{ MHz} - 300\text{ MHz}$** 
ดังนั้น หากเกิดกระแสกระชากที่มีความชันสูงกว่า $300\text{ MHz}$ (เวลาต่ำกว่า $1\text{ ns}$) พลังงานจะต้องมาจาก **On-Package Capacitors (OPD)** หรือ **ตัวเก็บประจุแบบ Ultra-Low ESL ขั้นสูง** ที่ติดตั้งอยู่ใต้ท้อง BGA ผ่านรูเจาะ VIPPO เท่านั้น

### 1.2 สถาปัตยกรรมตัวเก็บประจุความเหนี่ยวนำต่ำพิเศษ (Ultra-Low ESL Capacitor Technologies)

เพื่อทลายขีดจำกัดความเหนี่ยวนำของตัวเก็บประจุมาตรฐาน อุตสาหกรรมได้พัฒนาโครงสร้างภายในและรูปแบบขั้วต่อขึ้นมา 4 ตระกูลหลัก:

```
[ A: Standard MLCC (0603) ]     [ B: Reverse Geometry (0306) ]
    ┌───┬───────────────┬───┐       ┌───────────────────────────┐
    │(+)│  Dielectric   │(-)│       │      Top Terminal (+)     │
    └───┴───────────────┴───┘       ├───────────────────────────┤
    Long path (ESL ~ 800 pH)        │      Dielectric Layer     │
                                    ├───────────────────────────┤
[ C: Interdigitated (IDC 0508) ]    │     Bottom Terminal (-)   │
    ┌─┬─┬─┬─┬─┬─┬─┬─┐               └───────────────────────────┘
    │+│-│+│-│+│-│+│-│               Short/Wide path (ESL ~ 150 pH)
    └─┴─┴─┴─┴─┴─┴─┴─┘
    Alternating Flux Cancellation (ESL ~ 35 - 50 pH!)
```

1. **Reverse Geometry MLCC (LW Reverse: 0306, 0508):**
   - พลิกด้านขั้วต่อมาไว้ที่ขอบด้านยาว (Wide Terminations) ทำให้ระยะทางที่กระแสเดินทางในเนื้อเซรามิกสั้นลง และมีพื้นที่หน้าตัดนำกระแสขนานกันมากขึ้น
   - ลดค่าความเหนี่ยวนำภายในลงจาก $800\text{ pH}$ เหลือเพียง **$100 - 200\text{ pH}$ (ลดลง $75\%$)**

2. **Interdigitated Capacitors (IDC / 8-Terminal & 10-Terminal MLCC):**
   - มีขั้วต่อสลับขั้วบวกและลบเรียงเป็นฟันปลาตามขอบรอบตัวถัง (เช่น $+ - + - + - + -$)
   - กระแสที่ไหลเข้าและออกจากแต่ละขั้วที่อยู่ติดกันจะไหลในทิศทางตรงกันข้าม ก่อให้เกิด **การหักล้างของสนามแม่เหล็กอย่างสมบูรณ์ (Mutual Magnetic Flux Cancellation)** ภายในตัวถัง
   - ลดค่าความเหนี่ยวนำลงเหลือเพียง **$35 - 50\text{ pH}$** (ต่ำกว่าตัวเก็บประจุมาตรฐานถึง 15 - 20 เท่า!)

3. **X2Y Balanced 3-Terminal / 4-Terminal Capacitors:**
   - โครงสร้างภายในประกอบด้วยตัวเก็บประจุสมมาตร 2 ชุดที่แชร์ขั้วชีลด์กราวด์ตรงกลาง (G1/G2)
   - กระแสที่ไหลจากขั้วสายไฟทั้งสองจะวิ่งเข้าหากราวด์ตรงกลางในทิศทางสวนทางกัน $180^{\circ}$ สนามแม่เหล็กจะหักล้างกันเองเกือบ $100\%$ ให้ค่า ESL ต่ำถึง **$30\text{ pH}$**

4. **Silicon Capacitors (Deep-Trench 3D Silicon Capacitors):**
   - ผลิตด้วยกระบวนการโฟโตลิโทกราฟีของสารกึ่งตัวนำซิลิคอน โดยกัดกร่องลึกสามมิติ (Deep Reactive-Ion Etching: DRIE) ลงบนเวเฟอร์ซิลิคอน แล้วเคลือบด้วยชั้นออกไซด์บางเฉียบระดับนาโนเมตร
   - มีความหนาตัวถังบางเฉียบ ($< 80 - 100\ \mu\text{m}$) สามารถฝังลงในรอยบากของ Substrate หรือติดใต้ BGA ได้โดยตรง
   - มีค่า ESL ต่ำที่สุดในโลก: **$ESL < 10 - 15\text{ pH}$**
   - มีความเสถียรสูงสุด: ไม่มีการสูญเสียความจุจาก DC Bias ($\Delta C_{DC} = 0\%$), ไม่มี Aging, และทนอุณหภูมิได้สูงถึง $+250^{\circ}\text{C}$

| ชนิดของตัวเก็บประจุ (Capacitor Technology) | ขนาดตัวถัง (Package) | ค่าความจุทั่วไป | ความเหนี่ยวนำภายใน (ESL) | อิมพีแดนซ์ที่ 1.0 GHz |
| :--- | :--- | :--- | :--- | :--- |
| **Standard MLCC** | 0402 | 1.0 µF | 350 - 500 pH | ~ 2.2 - 3.1 Ω (แย่มาก) |
| **Standard Small MLCC** | 0201 | 0.1 µF | 200 - 300 pH | ~ 1.3 - 1.9 Ω |
| **LW Reverse Geometry** | 0306 | 1.0 µF | 100 - 150 pH | ~ 0.6 - 0.9 Ω |
| **Interdigitated (IDC)** | 0508 (8-Term) | 2.2 µF | 35 - 50 pH | ~ 0.22 - 0.31 Ω (ดีมาก) |
| **X2Y Filter Capacitor** | 0603 | 0.1 µF | 30 - 45 pH | ~ 0.19 - 0.28 Ω |
| **Deep-Trench Silicon Cap** | 0202 (LGA) | 1.0 µF | **10 - 15 pH** | **~ 0.06 - 0.09 Ω (ยอดเยี่ยมที่สุด)** |

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)

**เหตุการณ์:** การ์ดเร่งความเร็วปัญญาประดิษฐ์ (PCIe Gen 5 AI Inference Card) ใช้ชิป AI SoC ขนาด 5nm มีรางไฟคอร์ $V_{DD\_CORE} = 0.75\text{ V}$ กินกระแสพีคชั่วขณะ $\Delta I = 80\text{ A}$ ภายในเวลา $200\text{ ps}$ เมื่อเริ่มรันคำสั่ง Large Language Model (LLM Matrix Multiplication) 

**อาการล้มเหลว:**
1. บอร์ดผ่านการบูตระบบและรันการทดสอบฟังก์ชันพื้นฐานได้ปกติ แต่ทันทีที่เริ่มโหลดโมเดล AI ขนาดใหญ่ ชิป SoC จะเกิดอาการหยุดทำงาน (Crash / Machine Check Exception: MCE) ทันทีในรอบ Clock แรกของการประมวลผลเมทริกซ์
2. ออสซิลโลสโคปความเร็วสูง $16\text{ GHz}$ จับภาพแรงดันที่พิน Sense ของตัวถัง พบว่าภายในช่วงเวลา **$150\text{ ps}$** แรก แรงดันคอร์ร่วงดิ่งลงจาก $0.75\text{ V}$ เหลือเพียง **$0.61\text{ V}$ (Voltage Droop สูงถึง $140\text{ mV}$ หรือ $-18.7\%$)** ซึ่งต่ำกว่าจุดตัดขั้นต่ำของเกต ($0.68\text{ V}$) อย่างรุนแรง
3. ทั้งที่บนแผ่น PCB ใต้ชิป BGA ทีมวิศวกรได้ติดตั้งตัวเก็บประจุ 0402 MLCC ขนาด $1.0\ \mu\text{F}$ ไว้ถึง 60 ตัว แต่พบว่าการจัดวางใช้การลากสายแบบ Dog-bone ยาว $0.5\text{ mm}$ จาก Pad ไปยัง Via

```
[Waveform Capture: Sub-nanosecond Core Voltage Collapse]
  0.75V Nominal ────────────────┐
                                │ Droop occurs within 150 ps!
  0.68V Minimum Limit ──────────┼───────────────
                                │
  0.61V Measured (CRASH!) ──────┴──/\───────────
  PCB MLCC charge has not even arrived! BGA & Trace inductance blocked it!
```

**Root Cause Analysis (RCA):**
1. **The Sub-nanosecond Charge Starvation:** 
   สัญญาณกระชากเกิดขึ้นภายใน $200\text{ ps}$ คลื่นแม่เหล็กไฟฟ้าบน PCB ใช้เวลาเดินทางผ่านความหนาบอร์ด $1.6\text{ mm}$ และลากสาย Dog-bone อีก $0.5\text{ mm}$ คิดเป็นเวลาหน่วงในการเดินทาง (Time-of-flight Delay):
   $$t_{flight} \approx 2.5\text{ mm} \times 7\text{ ps/mm} \approx 17.5\text{ ps}$$
   แต่ความเหนี่ยวนำของลาย Dog-bone รวมกับ Via ($L_{total} \approx 0.95\text{ nH}$) ต้านทานการเปลี่ยนแปลงกระแสตามสมการ $V = L \cdot \frac{di}{dt}$:
   $$\Delta V_{L} = (0.95\text{ nH} / 60) \times \left( \frac{80\text{ A}}{200\text{ ps}} \right) = (15.8\text{ pH}) \times (4 \times 10^{11}\text{ A/s}) \approx 6.33\text{ V}!$$
   ความเหนี่ยวนำทำให้ประจุจากตัวเก็บประจุบน PCB **ถูกบล็อกอย่างสิ้นเชิง** ในช่วง $200\text{ ps}$ แรก พลังงานจึงต้องถูกดึงมาจาก On-Die Capacitance เพียงอย่างเดียว ซึ่งมีประจุไม่เพียงพอ แรงดันจึงยุบตัวลงทันที
2. **การจัดเรียงพิน BGA พาวเวอร์-กราวด์แบบกระจุกตัว:** พิน Power และ Ground ใต้ BGA ถูกวางแยกเป็นกลุ่มก้อน (Clustered Pins) แทนที่จะวางสลับฟันปลา ทำให้ความเหนี่ยวนำของ BGA บอลไม่เกิดการหักล้างของฟลักซ์แม่เหล็ก ($L_{ball}$ สูงถึง $0.35\text{ nH}$)

---

### Step-by-Step Engineering Checklist: การออกแบบ High-Frequency Decoupling และ BGA Co-Design

#### ขั้นตอนที่ 1: การจัดเรียงพิน BGA แบบหมากรุก (Checkerboard Power/GND Pattern)
ร่วมมือกับทีมออกแบบแพ็กเกจ IC (Package Co-Design):
- **ห้ามจัดพิน Power และ Ground เป็นแถวทึบแยกกัน:** เพราะกระแสจะไหลขนานกันในทิศทางเดียวกัน ก่อให้เกิดความเหนี่ยวนำร่วมเสริมแรงกัน (Positive Mutual Inductance) ทำให้ความเหนี่ยวนำพุ่งสูงขึ้น
- **จัดพินเป็นลายตารางหมากรุก (Interleaved / Checkerboard Pattern):**
  วางพิน Power สลับกับ Ground ทุกๆ พิน ($V - G - V - G$) กระแสในบอลบัดกรีที่อยู่ติดกันจะไหลสวนทางกัน สนามแม่เหล็กจะหักล้างกันเองอย่างสมบูรณ์ ช่วยลดความเหนี่ยวนำของบอล BGA ลงได้ถึง **$60\% - 75\%$** (จาก $0.30\text{ nH}$ เหลือเพียง $0.08\text{ nH}$ ต่อคู่)

```
+-------------------------------------------------------------+
|  BGA Pin Assignment Optimization:                           |
|                                                             |
|  Bad: Clustered (High L ~ 0.30 nH)  Good: Checkerboard (L ~ 0.08 nH)
|    [PWR] [PWR] [PWR] [PWR]             [PWR] [GND] [PWR] [GND]
|    [PWR] [PWR] [PWR] [PWR]             [GND] [PWR] [GND] [PWR]
|    [GND] [GND] [GND] [GND]             [PWR] [GND] [PWR] [GND]
|    [GND] [GND] [GND] [GND]             [GND] [PWR] [GND] [PWR]
|    (Flux adds up constructively)       (Flux cancels out destructively!)
+-------------------------------------------------------------+
```

#### ขั้นตอนที่ 2: การใช้เทคโนโลยี Deep-Trench Silicon Capacitors ใต้ท้อง BGA
สำหรับชิปประมวลผลที่กินกระแสความชันสูง ($di/dt > 100\text{ A/ns}$):
- ติดตั้ง **Silicon Capacitors (เช่น Murata SiCap หรือ Empower IVR)** ขนาด 0202 หรือ 0404 ไว้ตรงช่องเปิดใต้ท้อง BGA (Center Cavity)
- เนื่องจากตัวถังซิลิคอนมีความบางพิเศษ ($< 100\ \mu\text{m}$) จึงสามารถเชื่อมต่อด้วยเทคโนโลยี **Micro-via in Pad (VIPPO)** ลงสู่ระนาบไฟชั้นบนสุดได้ทันที ให้ค่า Loop Inductance ต่ำเป็นประวัติการณ์ **$< 25\text{ pH}$** สามารถจ่ายประจุได้ทันเวลาภายใน $100\text{ ps}$

#### ขั้นตอนที่ 3: กฎการเชื่อมต่อแบบ Interdigitated Capacitors (IDC Multi-Via Layout)
เมื่อเลือกใช้ตัวเก็บประจุแบบ IDC (เช่น 8-Terminal ขนาด 0508):
- ต้องเจาะรูเจาะ Via อิสระประกบติดกับขั้วทั้ง 8 ขั้ว (ห้ามแชร์ Via เด็ดขาด!)
- จัดทิศทางการเชื่อมต่อสลับขั้ว $+ - + - + -$ เพื่อให้กระแสไหลวนในท่อ Via ที่อยู่ติดกันในทิศทางตรงกันข้าม เกิดการหักล้างของสนามแม่เหล็กทั้งภายในตัวถังและในกระบอก Via

```
+-------------------------------------------------------------+
|  IDC 8-Terminal Multi-Via Layout Pattern:                   |
|                                                             |
|    (PWR Via)   (GND Via)   (PWR Via)   (GND Via)            |
|        │           │           │           │                |
|     ┌──┴──┐     ┌──┴──┐     ┌──┴──┐     ┌──┴──┐             |
|     │ (+) │     │ (-) │     │ (+) │     │ (-) │  [ 0508 IDC]│
|     ├──┬──┤     ├──┬──┤     ├──┬──┤     ├──┬──┤  Body       |
|     │ (-) │     │ (+) │     │ (-) │     │ (+) │             |
|     └──┬──┘     └──┬──┘     └──┬──┘     └──┬──┘             |
|        │           │           │           │                |
|    (GND Via)   (PWR Via)   (GND Via)   (PWR Via)            |
+-------------------------------------------------------------+
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คันจิ (Kanji) | คานะ (Kana) | คำอ่าน (Romaji) | ภาษาอังกฤษ / คำแปลภาษาไทย |
| :--- | :--- | :--- | :--- |
| **超低ESLコンデンサ** | ちょうていいーえすえるこんでんさ | Chō-tei-ESL Kondensa | Ultra-low ESL Capacitor |
| **シリコンキャパシタ** | しりこんきゃぱした | Shirikon Kyapashita | Deep-Trench Silicon Capacitor |
| **インターディジテッド** | いんたーでぃじてっど | Intādijiteddo | Interdigitated Capacitor (IDC) |
| **パッケージ直下実装** | ぱっけーじちょっかじっそう | Pakkēji Chokka Jissō | Land-Side Cavity Placement under BGA |
| **格子状配置** | こうしじょうはいち | Kōshijō Haichi | Checkerboard / Interleaved Pin Pattern |
| **磁束相殺効果** | じそくそうさいこうか | Jisoku Sōsai Kōka | Magnetic Flux Cancellation Effect |
| **超高速過渡応答** | ちょうこうそくかとおうとう | Chō-kōsoku Kato Ōtō | Sub-nanosecond Transient Response |
| **電圧サグ** | でんあつさぐ | Den'atsu Sagu | Transient Voltage Sag / Droop |
| **寄生インダクタンス分離**| きせいいんだくたんすぶんり | Kisei Indakutansu Bunri | Inductive Isolation / Shielding |
| **オンダイ容量** | おんだいようりょう | On-dai Yōryō | On-Die Capacitance (MIM/DTC) |
| **貫通ビア共有禁止** | かんつうびあきょうゆうきんし | Kantsū Bia Kyōyū Kinshi | Prohibition of Shared Vias |
| **反共振フリー** | はんきょうしんふりー | Han-kyōshin Furī | Anti-resonance Free PDN |

---

### 3.2 บันทึกการตรวจแบบของ Senior Engineer (検図指摘事項 - Kenzu Comments)

#### คอมเมนต์ที่ 1: ตรวจพบการลากสาย Dog-bone ใต้ BGA ทำลายความสามารถของ High-Frequency Decoupling
> **検図指摘 (Kenzu Feedback 1):**  
> 「AIプロセッサコア電源（$V_{DD} = 0.75\text{V}$、スルーレート$di/dt \ge 200\text{A/ns}$）のBGA裏面パスコン配線を検図しました。0402サイズMLCC（C501〜C560）のランドからファンアウトビアまでの間に、長さ0.5mm〜0.8mmの引き出し配線（ドッグボーン形状）が残存しています。この微小な配線パターンにより、1個あたり約$0.6\text{nH}$の寄生インダクタンスが付加され、コンデンサの実装ループインダクタンスが$1.1\text{nH}$まで増大しています。サブナノ秒（$< 500\text{ps}$）の超高速負荷過渡応答時において、基板側パスコンからの電荷供給がインダクタンスにより完全に遮断され、コア電圧が許容下限（$0.68\text{V}$）を割り込む重大な電圧サグ（$130\text{mV}$ドロップ）を招きます。ドッグボーン配線を直ちに全廃し、パッド内に直接ビアを形成する『VIPPO（ビアインパッド）』へ変更してください。また、中央キャビティ部には極低ESLのインターディジテッドコンデンサ（IDC 0508、ESL $\le 45\text{pH}$）またはシリコンキャパシタを採用することを強く要求します。」  
> *(คำแปล: ตรวจสอบการเดินลาย Decoupling ใต้ BGA ของ AI Processor Core (0.75V, di/dt ≥ 200A/ns) พบว่ามีลายเส้น Dog-bone ยาว 0.5-0.8 mm คั่นระหว่าง Pad 0402 กับ Via การมีลายเส้นนี้เพิ่มความเหนี่ยวนำอีก 0.6 nH ทำให้ Loop Inductance รวมพุ่งถึง 1.1 nH ในช่วงสวิตชิ่งระดับ Sub-nanosecond (< 500 ps) การส่งผ่านประจุจากตัวเก็บประจุบน PCB จะถูกความเหนี่ยวนำบล็อกอย่างสิ้นเชิง ส่งผลให้เกิด Voltage Droop ถึง 130 mV ทะลุขีดจำกัดต่ำสุด (0.68V) ขอให้ยกเลิกลายเส้น Dog-bone ทั้งหมดทันที และเปลี่ยนเป็น Via-in-Pad (VIPPO) พร้อมทั้งเปลี่ยนตัวเก็บประจุตรงใจกลาง BGA ไปเป็นแบบ IDC 0508 (ESL ≤ 45 pH) หรือ Silicon Capacitor เพื่อรองรับกระแสความเร็วสูง)*

#### คอมเมนต์ที่ 2: พิน BGA ขาดการสลับขั้ว Power/GND ก่อให้เกิด Mutual Inductance สูง
> **検図指摘 (Kenzu Feedback 2):**  
> 「ICパッケージ設計チームとの協調検図（Co-Design Review）において、BGAボールマップの電源/GNDピンアサインを確認しました。現在、コア電源ピン（$V_{DD}$）とGNDピンがそれぞれ4x4のブロック単位で偏在（クラスタリング配置）しています。同方向の電流が密集して流れることで正の相互インダクタンス（Positive Mutual Inductance）が重畳し、BGAボール単体での実効ループインダクタンスが$0.32\text{nH}$まで悪化しています。これでは基板側でいかに低ESLコンデンサを配置しても、ボールネックによるインピーダンス障壁を突破できません。パッケージ設計側に対し、電源ピンとGNDピンを市松模様状に交互配置する『チェッカーボード（Checkerboard）配列』への改訂を正式要求してください。これにより磁束相殺効果を最大化し、ボール部寄生インダクタンスを$0.10\text{nH}$以下へ低減させる必要があります。」  
> *(คำแปล: ในการทำ Co-Design Review ร่วมกับทีมออกแบบ Package IC ตรวจสอบผังพิน BGA พบว่าพิน Power และ GND ถูกวางแยกกันเป็นกลุ่มก้อน 4x4 บล็อก กระแสที่ไหลไปในทิศทางเดียวกันก่อให้เกิด Positive Mutual Inductance ซ้อนทับกัน ทำให้ความเหนี่ยวนำของบอล BGA พุ่งสูงถึง 0.32 nH ซึ่งต่อให้บนแผ่น PCB จะใช้ตัวเก็บประจุที่ดีเพียงใด ก็ไม่สามารถข้ามคอขวดของบอล BGA ได้ ขอให้ส่งข้อกำหนดอย่างเป็นทางการไปยังทีมแพ็กเกจ ให้แก้ไขผังพินเป็นแบบตารางหมากรุก (Checkerboard) สลับขั้ว Power/GND เพื่อสร้าง Magnetic Flux Cancellation ดึงความเหนี่ยวนำของบอล BGA ลงมาให้ต่ำกว่า 0.10 nH ทันที)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณเปรียบเทียบอิมพีแดนซ์ที่ความถี่ 1.5 GHz ระหว่าง Standard MLCC, IDC, และ Silicon Capacitor

ในระบบส่งสัญญาณความเร็วสูง 112Gbps PAM4 SerDes มีสัญญาณรบกวนฮาร์โมนิกของสัญญาณนาฬิกาพุ่งสูงสุดที่ความถี่ $f = 1.5\text{ GHz} = 1.5 \times 10^9\text{ Hz}$ โดยมีสเปกของรางไฟกำหนดว่า อิมพีแดนซ์ที่ความถี่นี้ต้องไม่เกิน $Z_{target} = 25\text{ m}\Omega$

วิศวกรเปรียบเทียบการเลือกใช้ตัวเก็บประจุ 3 เทคโนโลยีที่มีขนาดความจุเท่ากันคือ $C = 1.0\ \mu\text{F}$ เมื่อประกอบลงบอร์ดด้วยเทคโนโลยี VIPPO:
- **เทคโนโลยี A (Standard 0402 MLCC):** มีความเหนี่ยวนำรวม $L_{total, A} = 0.40\text{ nH} = 400\text{ pH}$, ความต้านทาน $ESR_A = 6.0\text{ m}\Omega$
- **เทคโนโลยี B (Interdigitated Capacitor IDC 0508 8-Terminal):** มีความเหนี่ยวนำรวม $L_{total, B} = 0.045\text{ nH} = 45\text{ pH}$, ความต้านทาน $ESR_B = 3.0\text{ m}\Omega$
- **เทคโนโลยี C (Deep-Trench Silicon Capacitor 0202):** มีความเหนี่ยวนำรวม $L_{total, C} = 0.012\text{ nH} = 12\text{ pH}$, ความต้านทาน $ESR_C = 2.0\text{ m}\Omega$

จงคำนวณ:
1. อิมพีแดนซ์เดี่ยว ($|Z_{single}|$) ของตัวเก็บประจุแต่ละชนิดที่ความถี่ $1.5\text{ GHz}$
2. จำนวนตัวเก็บประจุขั้นต่ำที่ต้องนำมาต่อขนานกัน ($N_{min}$) ของแต่ละเทคโนโลยี เพื่อให้อิมพีแดนซ์รวมต่ำกว่า $Z_{target} = 25\text{ m}\Omega$
3. วิเคราะห์ความเป็นไปได้ในการติดตั้งลงในพื้นที่จำกัดใต้ BGA?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณอิมพีแดนซ์เดี่ยวที่ความถี่ $1.5\text{ GHz}$ ($f = 1.5 \times 10^9\text{ Hz}$):**
ที่ความถี่ $1.5\text{ GHz}$ สูงกว่าจุด SRF ของตัวเก็บประจุทุกตัวมาก ค่ารีแอกแตนซ์ของความจุ $X_C \approx 0.1\text{ m}\Omega$ (ละเลยได้) อิมพีแดนซ์ถูกครอบงำด้วยความเหนี่ยวนำอย่างสิ้นเชิง ($|Z| \approx \sqrt{ESR^2 + (2\pi f L)^2} \approx 2\pi f L$):
- ค่าสัมประสิทธิ์เชิงมุม:
  $$\omega = 2\pi f = 2\pi \times (1.5 \times 10^9\text{ Hz}) \approx 9.4248 \times 10^9\text{ rad/s}$$

- **เทคโนโลยี A (Standard 0402, $L = 400\text{ pH}$):**
  $$X_{L, A} = (9.4248 \times 10^9) \times (400 \times 10^{-12}\text{ H}) \approx 3.770\ \Omega$$
  $$|Z_A| \approx \sqrt{(0.006)^2 + (3.770)^2} \approx 3.770\ \Omega = 3,770\text{ m}\Omega$$
- **เทคโนโลยี B (IDC 0508, $L = 45\text{ pH}$):**
  $$X_{L, B} = (9.4248 \times 10^9) \times (45 \times 10^{-12}\text{ H}) \approx 0.4241\ \Omega$$
  $$|Z_B| \approx \sqrt{(0.003)^2 + (0.4241)^2} \approx 0.4241\ \Omega = 424.1\text{ m}\Omega$$
- **เทคโนโลยี C (Silicon Capacitor, $L = 12\text{ pH}$):**
  $$X_{L, C} = (9.4248 \times 10^9) \times (12 \times 10^{-12}\text{ H}) \approx 0.1131\ \Omega$$
  $$|Z_C| \approx \sqrt{(0.002)^2 + (0.1131)^2} \approx 0.1131\ \Omega = 113.1\text{ m}\Omega$$

**2. คำนวณจำนวนตัวเก็บประจุขนานกัน ($N \ge \frac{|Z_{single}|}{25\text{ m}\Omega}$):**
- **เทคโนโลยี A:**
  $$N_A \ge \frac{3,770\text{ m}\Omega}{25\text{ m}\Omega} = 150.8 \implies \mathbf{151\ \text{ตัว}}$$
- **เทคโนโลยี B:**
  $$N_B \ge \frac{424.1\text{ m}\Omega}{25\text{ m}\Omega} = 16.96 \implies \mathbf{17\ \text{ตัว}}$$
- **เทคโนโลยี C:**
  $$N_C \ge \frac{113.1\text{ m}\Omega}{25\text{ m}\Omega} = 4.52 \implies \mathbf{5\ \text{ตัว}}$$

**3. บทวิเคราะห์ระดับ Senior Architect:**
- การใช้ Standard 0402 ต้องการตัวเก็บประจุถึง **151 ตัว** ซึ่งเป็นไปไม่ได้ที่จะวางลงในพื้นที่รอบ SerDes Receiver พิน
- การใช้ **IDC** ต้องการเพียง **17 ตัว** ซึ่งสามารถวางลงใต้ท้อง BGA ได้
- การใช้ **Silicon Capacitor** ต้องการเพียง **5 ตัวเท่านั้น!** ประหยัดพื้นที่ได้มากกว่า $96\%$ เมื่อเทียบกับ Standard MLCC และให้ความน่าเชื่อถือสูงสุดที่ความถี่ระดับกิกะเฮิรตซ์

---

### คำถามที่ 2: การวิเคราะห์การส่งมอบประจุในหน้าต่างเวลา Sub-nanosecond (The 200 ps Charge Starvation)

ชิป AI Core สถาปัตยกรรม 5nm มีตัวเก็บประจุสะสมประจุภายในดายซิลิคอน (On-Die MIM Capacitance) รวม $C_{die} = 120\text{ nF}$ โดยไม่มีตัวเก็บประจุบน Package Substrate

เมื่อชิปสลับคำสั่ง เกิดกระแสกระชากก้าวกระโดด $\Delta I = 60\text{ A}$ โดยมีความชันคงที่ตลอดช่วงเวลา $t_{rise} = 200\text{ ps} = 2.0 \times 10^{-10}\text{ s}$ 
ความเหนี่ยวนำของบอล BGA และโครงสร้างแพ็กเกจคั่นกลางระหว่างดายกับแผ่น PCB รวมกันคือ $L_{pkg} = 0.25\text{ nH}$ 

เนื่องจากความเหนี่ยวนำ $L_{pkg}$ ขัดขวางกระแส ในช่วง $200\text{ ps}$ แรก กระแสทั้งหมดที่จ่ายให้ลอจิกเกตจะต้องมาจาก $C_{die}$ เพียงแหล่งเดียวเท่านั้น

จงคำนวณ:
1. ปริมาณประจุไฟฟ้าทั้งหมด ($\Delta Q_{transient}$) ที่โหลดต้องการในช่วงเวลา $200\text{ ps}$ (พื้นที่ใต้กราฟรูปสามเหลี่ยมของกระแสกระชาก)
2. แรงดันตกคร่อมรอยต่อในดายซิลิคอน ($\Delta V_{droop}$) ที่เกิดจากการสูญเสียประจุของ $C_{die}$ เพียงลำพัง
3. หากรางไฟคอร์มีแรงดันระบุ $0.75\text{ V}$ และชิปจะแฮงก์ทันทีหากแรงดันตกเกิน $10\%$ ($\Delta V_{limit} = 75\text{ mV}$) จงวิเคราะห์ว่าระบบจะรอดพ้นจากการแฮงก์หรือไม่ และต้องเพิ่ม On-Package Capacitor (OPD) ขนาดเท่าใดจึงจะควบคุมให้อยู่ในสเปก?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณปริมาณประจุไฟฟ้าที่ต้องการ ($\Delta Q_{transient}$):**
เนื่องจากกระแสเพิ่มขึ้นเป็นเส้นตรงจาก $0\text{ A}$ ถึง $60\text{ A}$ ภายในเวลา $t_{rise} = 200\text{ ps}$:
$$\Delta Q_{transient} = \text{พื้นที่ใต้กราฟกระแส} = \frac{1}{2} \cdot \Delta I \cdot t_{rise}$$
$$\Delta Q_{transient} = \frac{1}{2} \times 60\text{ A} \times (200 \times 10^{-12}\text{ s}) = 6.0 \times 10^{-9}\text{ C} = 6.0\text{ nC}$$

**2. คำนวณแรงดันตกคร่อม ($\Delta V_{droop}$):**
ประจุทั้งหมด $6.0\text{ nC}$ ถูกดึงออกจากตัวเก็บประจุภายในดาย $C_{die} = 120\text{ nF} = 120 \times 10^{-9}\text{ F}$:
$$\Delta V_{droop} = \frac{\Delta Q_{transient}}{C_{die}} = \frac{6.0 \times 10^{-9}\text{ C}}{120 \times 10^{-9}\text{ F}} = 0.050\text{ V} = 50\text{ mV}$$

เมื่อรวมกับแรงดันตกคร่อมความต้านทานอนุกรมของโครงข่าย On-Die Metallization ($\text{ESR}_{die} \approx 0.5\text{ m}\Omega \implies \Delta V_{ESR} \approx 60\text{ A} \times 0.5\text{ m}\Omega = 30\text{ mV}$):
$$\Delta V_{total\_droop} \approx 50\text{ mV} + 30\text{ mV} = 80\text{ mV}$$

**3. บทวิเคราะห์ความน่าเชื่อถือและการแก้ไข:**
- แรงดันตกคร่อมจริงคือ **$80\text{ mV}$** ซึ่งทะลุขีดจำกัดความปลอดภัย ($75\text{ mV}$) ชิปจะเกิดอาการ Logic Crash ทันทีในรอบ Clock แรก!
- **การเพิ่ม On-Package Decoupling (OPD):**
  เพื่อให้แรงดันตกคร่อม $\Delta V_{droop} \le 35\text{ mV}$ (เหลือ Margin ให้ ESR):
  $$C_{req} = \frac{\Delta Q}{\Delta V_{allowed}} = \frac{6.0 \times 10^{-9}\text{ C}}{0.035\text{ V}} \approx 171.4\text{ nF}$$
  ความจุที่ต้องเพิ่มขึ้น:
  $$\Delta C = 171.4\text{ nF} - 120\text{ nF} \approx 51.4\text{ nF}$$
- **สรุป:** ทางผู้ผลิตแพ็กเกจ IC จะต้องติดตั้ง Land-Side Silicon Capacitors (LSC) ขนาดอย่างน้อย **$100\text{ nF}$** ลงบนตัวถัง Substrate ใกล้กับดายซิลิคอนโดยตรง จึงจะสามารถข้ามผ่านหน้าต่างเวลา Sub-nanosecond นี้ได้อย่างปลอดภัย

---

### คำถามที่ 3: การประเมิน Mutual Inductance Cancellation ในโครงสร้าง BGA Checkerboard Pattern

เปรียบเทียบคู่บอล BGA พิทช์ $P = 1.0\text{ mm}$ ความสูงบอล $h = 0.4\text{ mm}$ รัศมีบอล $r = 0.2\text{ mm}$:
- **กรณีที่ 1 (Isolated Loop):** บอล Power และ Ground อยู่ห่างกัน $s_1 = 3.0\text{ mm}$ สนามแม่เหล็กแทบไม่หักล้างกัน
- **กรณีที่ 2 (Checkerboard Adjacent):** บอล Power และ Ground วางติดกันในตารางหมากรุกที่ระยะพิทช์ $s_2 = 1.0\text{ mm}$

กำหนดสมการความเหนี่ยวนำของคู่บอล BGA:
$$L_{loop} = 2 \cdot (L_{self} - M) \approx \frac{\mu_0 \cdot h}{\pi} \left[ \ln\left( \frac{s}{r} \right) + 0.25 \right]$$

จงคำนวณ:
1. ความเหนี่ยวนำของคู่บอลในกรณีที่ 1 ($L_{loop, 1}$) และกรณีที่ 2 ($L_{loop, 2}$)
2. หากมีกระแสสลับ $di/dt = 10\text{ A/ns} = 10^{10}\text{ A/s}$ ไหลผ่านบอลคู่นี้ จงคำนวณแรงดันสัญญาณรบกวน Ground Bounce เหนี่ยวนำ ($V_{bounce} = L_{loop} \cdot \frac{di}{dt}$) ของทั้งสองกรณี?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณความเหนี่ยวนำของคู่บอล BGA ($h = 0.4\text{ mm}$, $r = 0.2\text{ mm}$):**
- สัมประสิทธิ์ $\frac{\mu_0 \cdot h}{\pi} = (0.4\text{ nH/mm}) \times 0.4\text{ mm} = 0.16\text{ nH}$

- **กรณีที่ 1 ($s_1 = 3.0\text{ mm}$):**
  $$\frac{s_1}{r} = \frac{3.0}{0.2} = 15.0$$
  $$\ln(15.0) + 0.25 \approx 2.708 + 0.25 = 2.958$$
  $$L_{loop, 1} = 0.16\text{ nH} \times 2.958 \approx 0.4733\text{ nH} = 473.3\text{ pH}$$

- **กรณีที่ 2 ($s_2 = 1.0\text{ mm}$):**
  $$\frac{s_2}{r} = \frac{1.0}{0.2} = 5.0$$
  $$\ln(5.0) + 0.25 \approx 1.6094 + 0.25 = 1.8594$$
  $$L_{loop, 2} = 0.16\text{ nH} \times 1.8594 \approx 0.2975\text{ nH} = 297.5\text{ pH}$$
  *(และเมื่อคิดผลรวมของบอลข้างเคียงในรูปแบบ Checkerboard 2 มิติ ฟลักซ์จะถูกหักล้าง 4 ทิศทาง ทำให้ความเหนี่ยวนำประสิทธิผลจริงลดลงเหลือต่ำกว่า **$120\text{ pH}$**)*

**2. คำนวณแรงดัน Ground Bounce เหนี่ยวนำ ($di/dt = 10^{10}\text{ A/s}$):**
- **กรณีที่ 1:**
  $$V_{bounce, 1} = (0.4733 \times 10^{-9}\text{ H}) \times (10^{10}\text{ A/s}) \approx 4.733\text{ V}!$$
- **กรณีที่ 2 (แบบมี Mutual Cancellation รอบทิศทาง $L_{eff} \approx 120\text{ pH}$):**
  $$V_{bounce, 2} = (0.120 \times 10^{-9}\text{ H}) \times (10^{10}\text{ A/s}) \approx 1.200\text{ V}$$

**บทสรุปของ Senior Engineer:**
- การจัดเรียงบอล BGA แบบ Checkerboard ช่วยลดการเกิด Ground Bounce และ Power Sag เหนี่ยวนำลงได้มากกว่า **$75\%$**
- การออกแบบ PDN ความถี่สูงจึงเป็นงานที่ต้องผสานกันระหว่างวิศวกรแผ่นวงจรพิมพ์ (PCB) และวิศวกรออกแบบแพ็กเกจชิป (Package IC) อย่างแยกกันไม่ออก
