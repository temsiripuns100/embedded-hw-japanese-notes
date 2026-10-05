# Lesson 061: PCB Decoupling Part 1 - Power Distribution Network (PDN) Fundamentals and Target Impedance

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในระบบดิจิทัลความเร็วสูงและโปรเซสเซอร์ประมวลผลขั้นสูง (เช่น FPGAs, Multi-core SoCs, AI Accelerators, และ DDR5/LPDDR5 Memory) แรงดันไฟฟ้าของคอร์ (Core Voltage: $V_{DD}$) ลดต่ำลงเรื่อยๆ จนเหลือเพียง $0.75\text{ V} - 0.90\text{ V}$ ในขณะที่อัตราการบริโภคกระแสไฟฟ้าชั่วขณะ (Transient Current Step: $\Delta I$) พุ่งสูงขึ้นถึง $20\text{ A} - 100\text{ A}$ โดยมีเวลาสลับสัญญาณสั้นเพียงระดับ Sub-nanosecond ($t_r < 200 - 500\text{ ps}$)

การส่งมอบพลังงานอย่างมีเสถียรภาพภายใต้สภาวะดังกล่าว จำเป็นต้องมองโครงข่ายจ่ายไฟทั้งหมดตั้งแต่ **VRM (Voltage Regulator Module)** ผ่าน **แผ่น PCB**, **ตัวเก็บประจุ Decoupling Capacitors**, **ระนาบ Ground/Power Planes**, **BGA Solder Balls**, **IC Package Substrate**, จนถึง **On-Die Metallization** รวมกันเป็นโครงสร้างเดียว เรียกว่า **Power Distribution Network (PDN)**

```
+-------------------------------------------------------------------------+
|                  Complete Multi-Tier PDN Hierarchy                      |
|                                                                         |
|  [VRM / PMIC] ──► [Bulk Caps] ──► [MLCC Caps] ──► [Plane Pair] ──►     |
|   (DC - 100kHz)    (10k - 1MHz)    (100k-50MHz)    (10M-300MHz)         |
|                                                                         |
|  ──► [Package BGA] ──► [Package Caps] ──► [On-Die Caps] ──► [Silicon Die]|
|       (50M - 500MHz)    (100M - 1GHz)       (> 1GHz)       (Gate Load)  |
+-------------------------------------------------------------------------+
```

### 1.1 แนวคิด Target Impedance ($Z_{target}$) และสมการกำหนดขอบเขตเสถียรภาพ

เป้าหมายสูงสุดของวิศวกร PDN คือการควบคุมให้ค่าแรงดันกระเพื่อมของรางจ่ายไฟ (Peak-to-Peak Power Rail Ripple, $\Delta V_{ripple}$) อยู่ภายในแถบความคลาดเคลื่อนที่กำหนด (Voltage Tolerance Window เช่น $\pm 3\%$ หรือ $\pm 5\%$) ตลอดเวลา 

ตามทฤษฎี **Larry Smith Target Impedance Method** หากสมมติว่าฮาร์โมนิกของกระแสชั่วขณะ ($\Delta I$) ในย่านความถี่ต่างๆ มีขนาดไม่เกินกระแสสลับสูงสุด ค่าอิมพีแดนซ์ของโครงข่ายจ่ายไฟที่มองจากตัวถังชิปจะต้องไม่เกินขีดจำกัด **Target Impedance ($Z_{target}$)** ตลอดทุกย่านความถี่:

$$Z_{target} = \frac{\Delta V_{allowed}}{\Delta I_{transient}} = \frac{V_{DD} \cdot (\% \text{Tolerance})}{I_{max} \cdot (\% \text{Step})}$$

โดยที่:
- $V_{DD}$ คือ แรงดันระบุของรางจ่ายไฟ (Nominal Rail Voltage, $\text{V}$)
- $\% \text{Tolerance}$ คือ เปอร์เซ็นต์แรงดันตก/เกินสูงสุดที่ยอมรับได้ (เช่น $\pm 3\% \implies 0.03$)
- $I_{max}$ คือ กระแสไฟฟ้าสูงสุดที่ชิปบริโภค ($\text{A}$)
- $\% \text{Step}$ คือ สัดส่วนกระแสชั่วขณะที่สลับไปมาระหว่าง Idle กับ Full Load (มักกำหนดที่ $50\% - 100\%$ หรือ $0.5 - 1.0$)

**ตัวอย่างสเปกระดับเซิร์ฟเวอร์:**
สำหรับชิปประมวลผล $V_{DD} = 0.85\text{ V}$, จ่ายกระแสสูงสุด $I_{max} = 60\text{ A}$, อัตราก้าวของกระแส $\Delta I = 50\% = 30\text{ A}$, ความทนทานต่อแรงดันกระเพื่อม $\pm 3\%$ ($\Delta V = 0.85 \times 0.03 = 25.5\text{ mV}$):

$$Z_{target} = \frac{25.5 \times 10^{-3}\text{ V}}{30\text{ A}} = 0.85 \times 10^{-3}\ \Omega = 0.85\text{ m}\Omega \ (850\ \mu\Omega)$$

อิมพีแดนซ์ในระดับต่ำกว่า **$1\text{ m}\Omega$** ถือเป็นความท้าทายขั้นสูงสุด ซึ่งไม่สามารถบรรลุได้ด้วยตัวเก็บประจุเพียงตัวเดียว แต่ต้องอาศัยการผสมผสานตัวเก็บประจุหลากหลายเทคโนโลยีขนานกันเป็นลำดับขั้น

### 1.2 แบนด์วิดท์สูงสุดของการวิเคราะห์ PDN ($f_{knee}$ & $f_{max}$)

ความถี่สูงสุดที่โครงข่ายจ่ายไฟบนแผ่น PCB ต้องควบคุมอิมพีแดนซ์ ถูกกำหนดโดยเวลาขึ้นของกระแสชั่วขณะ (Current Slew Rate, $di/dt$):

$$f_{max} \approx f_{knee} = \frac{0.5}{t_r} \quad \text{หรือ} \quad \frac{0.35}{t_r}$$

อย่างไรก็ตาม ในทางกายภาพของแพ็กเกจ เซมิคอนดักเตอร์ชิปจะมีตัวเหนี่ยวนำปรสิตของ Ball Grid Array (BGA) และ Bond Wires / C4 Bumps คั่นกลาง ($L_{pkg} \approx 0.1 - 0.5\text{ nH}$) ซึ่งตัวเหนี่ยวนำนี้จะทำหน้าที่เป็นฟิลเตอร์ Low-Pass ปิดกั้นไม่ให้ตัวเก็บประจุบน PCB สามารถตอบสนองความถี่สูงเกินกว่าจุดตัดนี้ได้:

$$f_{cutoff(PCB)} \approx \frac{1}{2\pi \sqrt{L_{pkg} \cdot C_{die}}}$$

โดยทั่วไป บนแผ่นวงจร PCB จะต้องรับผิดชอบช่วงความถี่ตั้งแต่ **DC ถึงประมาณ $100\text{ MHz} - 200\text{ MHz}$** ส่วนความถี่ที่สูงกว่า $200\text{ MHz}$ ขึ้นไปจนถึงระดับกิกะเฮิรตซ์ จะต้องอาศัย Package Capacitors และ On-Die Decoupling Capacitance (Deep Trench Capacitors หรือ MIM Caps) ภายในซิลิคอนดายเท่านั้น

```
Impedance |Z| (Ohms)
   ▲
   │        Peak Anti-Resonance Violation!
   │              /\
   │   VRM       /  \    MLCC Caps     PCB Plane   Package / On-Die
   │   └───.    /    \   .────────.    .───────.   .───────────────.
   │        \  /      \ /          \  /         \ /
   ├─────────\/────────X────────────\/───────────X─────────────────── Z_target (Flat line)
   │
   └──────────┴────────┴─────────────┴───────────┴──────────────────► Frequency (Hz)
             10kHz    1MHz         50MHz       300MHz             1GHz
```

### 1.3 ความแตกต่างระหว่าง Dynamic Voltage Droop และ Static DC IR Drop

ในการตรวจรับแบบเชิงวิศวกรรม ต้องแยกความแตกต่างระหว่างการสูญเสียแรงดัน 2 รูปแบบอย่างชัดเจน:

1. **DC IR Drop (Static Loss):** 
   - เกิดจากความต้านทานกระแสตรง ($\text{DCR}$) ของลายทองแดงระนาบ Power/Ground:
     $$\Delta V_{DC} = I_{DC} \cdot R_{DC(copper)}$$
   - ส่งผลให้แรงดันปลายทางตกอย่างถาวรในสภาวะ Steady-State แก้ไขได้ด้วยการขยายความกว้างทองแดง เพิ่มความหนาทองแดง ($2\text{ oz}$), หรือเพิ่ม Remote Sense Pin ของชิป VRM ไปวัดแรงดันที่ใต้ตัวถัง IC โดยตรง

2. **AC Dynamic Voltage Droop (Transient Noise):**
   - เกิดจากความเหนี่ยวนำปรสิต ($\text{Loop Inductance}: L_{loop}$) เมื่อกระแสเปลี่ยนทิศทางอย่างรวดเร็ว:
     $$\Delta V_{AC} = L_{loop} \cdot \frac{di}{dt} + \Delta I \cdot Z_{PDN}(f)$$
   - ก่อให้เกิดคลื่นสั่นพริ้ว (Under-shoot / Over-shoot Ringing) ทันทีที่แกนประมวลผลเริ่มทำงาน หากแรงดันตกลงต่ำกว่าเกณฑ์ต่ำสุด (Under-shoot threshold) แม้เพียง $1\text{ ns}$ ชิปจะเกิดภาวะ Logic State Inversion นำไปสู่การแฮงก์ (Crash / Blue Screen) ทันที

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)

**เหตุการณ์:** บอร์ดการ์ดเร่งความเร็วการประมวลผลวิดีโอ (High-Performance FPGA Accelerator Card) ใช้ FPGA สถาปัตยกรรม 16nm มีรางไฟคอร์ $V_{CCINT} = 0.85\text{ V}$ กระแสทำงานปกติ $25\text{ A}$ 

**อาการล้มเหลว:**
1. ในขั้นตอนการทดสอบบอร์ดเดี่ยว (Factory Diagnostics) วิ่งผ่านการทดสอบแบบโหลดต่ำได้ปกติทุกประการ
2. แต่เมื่อรันอัลกอริทึมเข้ารหัสวิดีโอ 8K (Full Pipeline Processing) FPGA จะหยุดการทำงานแบบสุ่ม (Random System Freeze) หลังจากทำงานไปได้ $2 - 30$ วินาที
3. เมื่อจับสัญญาณ $V_{CCINT}$ ด้วยออสซิลโลสโคปแบนด์วิดท์ $4\text{ GHz}$ พร้อมโพรบวัดไฟแบบ Active Differential โพรบแสดงภาพแรงดันร่วงลงอย่างรวดเร็ว (First Droop Ringing) จาก $0.85\text{ V}$ ตกฮวบลงไปถึง $0.77\text{ V}$ (Drop ลงไปถึง $80\text{ mV}$ หรือ $-9.4\%$ ซึ่งเกินสเปกกำหนด $\pm 3\% = \pm 25.5\text{ mV}$)
4. หลังจากเกิด Under-shoot จะตามมาด้วยการแกว่ง Over-shoot สูงถึง $0.94\text{ V}$ ที่ความถี่เรโซแนนซ์ประมาณ $12\text{ MHz}$

```
[Waveform Capture: Severe PDN Rail Collapse]
   0.85V Nominal ───────────────────┐
                                    │
   0.8245V Limit (-3%) ─────────────┼──────────────
                                    │  Under-shoot Ringing (12 MHz)
   0.77V Measured  ─────────────────┴──/\────/\────/\───────────
   (LOGIC COLLAPSE!)                  /  \  /  \  /  \
                                     /    \/    \/    \
```

**Root Cause Analysis (RCA):**
1. **การกำหนด Target Impedance ผิดพลาด:** วิศวกรผู้ออกแบบคำนวณ $Z_{target}$ โดยใช้กระแสเฉลี่ย ($I_{avg} = 10\text{ A}$) แทนที่จะใช้กระแสชั่วขณะก้าวกระโดดจริง ($\Delta I = 22\text{ A}$) ทำให้ตั้งค่า $Z_{target}$ ไว้หลวมเกินไปที่ $2.55\text{ m}\Omega$ ในขณะที่ความเป็นจริงต้องการ $Z_{target} \le 1.15\text{ m}\Omega$
2. **การเกิด Anti-resonance Peak ที่ 12 MHz:** เพื่อประหยัดพื้นที่ วิศวกรใส่ตัวเก็บประจุ Bulk Cap แบบ Tantalum Polymer $470\ \mu\text{F}$ จำนวน 2 ตัว ($ESL \approx 1.5\text{ nH}$) ขนานร่วมกับ MLCC ขนาดเล็ก $0.1\ \mu\text{F}$ (0402) โดยไม่มีตัวเก็บประจุค่ากลาง ($1\ \mu\text{F}$ และ $10\ \mu\text{F}$) คั่น ส่งผลให้เกิดการเรโซแนนซ์แบบขนาน (Parallel Anti-Resonance) ระหว่างความเหนี่ยวนำของ Bulk Caps กับความจุของ MLCC ก่อให้เกิดยอดเสาอิมพีแดนซ์สูงถึง **$18\text{ m}\Omega$ ที่ความถี่ $12\text{ MHz}$**
3. **การวางทางเดิน Via คอขวด:** ตัวเก็บประจุ MLCC เชื่อมต่อลงระนาบกราวด์และเพาเวอร์ด้วยรูเจาะ Via ร่วมกัน (Shared Vias) และเดินลายทองแดงยาว $2.5\text{ mm}$ จาก Pad ก่อนลงรู ทำให้ Loop Inductance พุ่งสูงกว่า $1.8\text{ nH}$ ต่อตัว ตัดขาดความสามารถในการจ่ายกระแสความถี่สูง

---

### Step-by-Step Engineering Checklist: กระบวนการออกแบบและคำนวณ PDN ตามมาตรฐาน Senior

#### ขั้นตอนที่ 1: การรวบรวมข้อมูลจำเพาะของชิปและคำนวณ $Z_{target}$
คำนวณค่าเป้าหมายที่แท้จริงโดยใช้ตารางคำนวณมาตรฐาน:
- **ระบุค่า $V_{DD, min}$ และ $V_{DD, max}$:** เช่น $0.85\text{ V} \pm 3\%$ ($\Delta V = 25.5\text{ mV}$)
- **กำหนด Dynamic Current Step ($\Delta I$):** ประเมินจาก Power Estimation Tool ของผู้ผลิตชิป (เช่น Xilinx Power Estimator: XPE หรือ Intel Quartus Power Analyzer) สำหรับการสลับสภาวะจาก Clock Gating สู่ Full Vector Execution (โดยทั่วไปใช้ $\Delta I \approx 50\% - 70\%$ ของ $I_{dynamic}$)
- **คำนวณ $Z_{target}$:**
  $$Z_{target} = \frac{\Delta V_{allowed}}{\Delta I} = \frac{0.0255\text{ V}}{20\text{ A}} = 1.275\text{ m}\Omega$$

#### ขั้นตอนที่ 2: การจัดสรรโครงสร้างตัวเก็บประจุเป็นชั้นๆ (Tiered Decoupling Strategy)
แบ่งความรับผิดชอบของตัวเก็บประจุออกเป็น 3 ย่านความถี่:

```
+---------------------------------------------------------------+
|  Tier 1: Low-Frequency Bulk (DC - 500 kHz)                    |
|    - Aluminum Polymer / Tantalum (100 µF - 470 µF)            |
|    - Governed by VRM response time and bulk capacitance       |
+---------------------------------------------------------------+
|  Tier 2: Mid-Frequency Decoupling (500 kHz - 20 MHz)          |
|    - High-Cap MLCC (0805 / 0603: 10 µF - 47 µF)               |
|    - Dampens anti-resonance peaks between Bulk and Small MLCC |
+---------------------------------------------------------------+
|  Tier 3: High-Frequency Local (20 MHz - 150 MHz)              |
|    - Low-ESL MLCC (0402 / 0201: 0.1 µF - 1.0 µF)              |
|    - Placed directly under BGA via VIPPO                      |
+---------------------------------------------------------------+
```

#### ขั้นตอนที่ 3: กฎการลด Loop Inductance ระดับ OJT
ประสิทธิภาพของตัวเก็บประจุ Decoupling ขึ้นอยู่กับ **Loop Inductance รวม ($L_{loop}$)** มากกว่าค่าความจุไฟฟ้า ($C$):

$$L_{loop} = L_{via} + L_{trace} + L_{pad} + ESL_{cap}$$

- **กฎข้อที่ 1:** วาง Via ให้แนบชิดกับ Pad ของตัวเก็บประจุที่สุด (Side-via placement) หลีกเลี่ยงการลากลายเส้นทองแดง (Trace length $\to 0$)
- **กฎข้อที่ 2:** สำหรับรางไฟ $V_{DD} < 1.0\text{ V}$ แนะนำให้ใช้เทคโนโลยี **Via-in-Pad (VIPPO)** เจาะรูลงบน Pad ของตัวเก็บประจุโดยตรง ซึ่งจะลด Loop Inductance ลงได้ถึง $60\% - 75\%$
- **กฎข้อที่ 3:** วางระนาบ Power และ Ground ใน Stackup ให้ห่างกันน้อยที่สุด (เช่น ใช้ Prepreg หนา $50\ \mu\text{m} - 75\ \mu\text{m}$) เพื่อเพิ่ม Plane Capacitance และลด Spreading Inductance

```
Bad (High ESL ~ 1.8 nH):
  [ Pad ] ──Trace (2mm)── [ Via ] ══════════════ (Huge Loop Area)
  [ Pad ] ──Trace (2mm)── [ Via ]

Good: Side-Via (ESL ~ 0.6 nH):
  [ Via ] [ Pad ]
  [ Via ] [ Pad ]

Best: Via-in-Pad VIPPO (ESL ~ 0.2 nH):
  [ (Via Inside Pad) ]
  [ (Via Inside Pad) ]
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คันจิ (Kanji) | คานะ (Kana) | คำอ่าน (Romaji) | ภาษาอังกฤษ / คำแปลภาษาไทย |
| :--- | :--- | :--- | :--- |
| **電源供給網** | でんげんきょうきゅうもう | Dengen Kyōkyū-mō | Power Distribution Network (PDN) |
| **目標インピーダンス** | もくひょういんぴーだんす | Mokuhyō Inpīdansu | Target Impedance ($Z_{target}$) |
| **過渡電流** | かとでんりゅう | Kato Denryū | Transient / Dynamic Current Step ($\Delta I$) |
| **電圧降下** | でんあつこうか | Den'atsu Kōka | Voltage Drop / Droop |
| **反共振** | はんきょうしん | Han-kyōshin | Anti-resonance (การเรโซแนนซ์แบบขนาน) |
| **パスコン** | ぱすこん | Pasukon | Bypass / Decoupling Capacitor |
| **寄生インダクタンス** | きせいいんだくたんす | Kisei Indakutansu | Parasitic Inductance ($ESL$) |
| **面間容量** | めんかんようりょう | Menkan Yōryō | Inter-plane Capacitance |
| **許容リップル** | きょようりっぷる | Kyoyō Rippuru | Allowable Voltage Ripple |
| **ループ面積** | るーぷめんせき | Rūpu Menseki | Loop Area (พื้นที่ลูปเหนี่ยวนำ) |
| **急峻な負荷変動** | きゅうしゅんなふかへんどう | Kyūshun-na Fuka Hendō | Fast Transient Load Step |
| **電源プレーン共振** | でんげんぷれーんきょうしん | Dengen Purēn Kyōshin | Power Plane Cavity Resonance |

---

### 3.2 บันทึกการตรวจแบบของ Senior Engineer (検図指摘事項 - Kenzu Comments)

#### คอมเมนต์ที่ 1: ตรวจพบค่า Target Impedance สูงเกินเกณฑ์ และการเกิดเสา Anti-Resonance
> **検図指摘 (Kenzu Feedback 1):**  
> 「SoCコア電源（$V_{DD\_CORE} = 0.80\text{V}$、最大消費電流45A）のPDNインピーダンス解析結果を確認しました。仕様書の目標インピーダンス（$Z_{target} = 0.8\text{m}\Omega$、許容リップル$\pm 3\%$）に対し、8MHz〜15MHzの周波数帯においてバルクコンデンサ（タンタル$330\mu\text{F}$）の等価直列インダクタンス（ESL）と小型セラミックコンデンサ（$0.1\mu\text{F}$）の容量成分による反共振（アンチレゾナンス）ピークが観測され、実効インピーダンスが$9.2\text{m}\Omega$まで跳ね上がっています。この状態では、急峻な負荷変動（$di/dt$）発生時に80mV以上のコア電圧ドロップ（Under-shoot）が発生し、プロセッサの論理停止（ハングアップ）を招くリスクが極めて高いです。反共振を減衰（ダンピング）させるため、ESRが適度に管理された中容量MLCC（$4.7\mu\text{F} \sim 22\mu\text{F}$、0603/0805サイズ）を複数個並列に追加配置し、全周波数帯において$Z_{target}$以下フラットに維持するプロファイルを再設計してください。」  
> *(คำแปล: ตรวจสอบผลวิเคราะห์ PDN Impedance ของรางไฟ Core ของ SoC (0.80V, กระแสสูงสุด 45A) พบว่าเทียบกับค่าเป้าหมาย Z_target = 0.8 mΩ (Ripple ±3%) แล้ว ในช่วงความถี่ 8 MHz - 15 MHz เกิดยอด Anti-resonance พุ่งสูงถึง 9.2 mΩ อันเกิดจาก ESL ของ Tantalum 330µF ทำปฏิกิริยากับ C ของ MLCC 0.1µF ในสภาวะนี้เมื่อโหลดสวิตชิ่งฉับพลัน จะเกิด Voltage Droop เกิน 80 mV ส่งผลให้โปรเซสเซอร์แฮงก์ได้ เพื่อแดมป์ยอดเรโซแนนซ์นี้ ขอให้เพิ่ม MLCC ขนาดกลาง (4.7µF - 22µF) ที่มี ESR เหมาะสมเข้าไปขนานเพิ่มเติม เพื่อกดให้โปรไฟล์อิมพีแดนซ์แบนราบอยู่ใต้ Z_target ตลอดทุกย่านความถี่)*

#### คอมเมนต์ที่ 2: การเดินลายเส้น Decoupling Capacitor ส่งผลให้ Loop Inductance สูงเกินพิกัด
> **検図指摘 (Kenzu Feedback 2):**  
> 「BGA裏面のデカップリングコンデンサ（C401〜C420、0402サイズ $1.0\mu\text{F}$）の配線パターンについて検図指摘します。コンデンサ電極パッドからスルーホールビアまでの間に約2.0mmの引き出し配線（トレース）が介在しており、さらに電源側とGND側のビアが同一方向に離れて配置されています。この幾何構造によりループ面積が拡大し、ループインダクタンスが実測で約$1.6\text{nH}$まで増大しています。これではせっかくの高周波MLCCが数十MHz帯で機能せず、無効化されています。引き出し配線を全廃し、パッドの直近側面にビアを近接配置する『サイドビア構造』、可能であればパッド内部にビアを直接形成する『パッドオンビア（VIPPO）』へ設計変更してください。これにより寄生インダクタンスを$0.3\text{nH}$以下に抑制し、過渡応答特性を改善してください。」  
> *(คำแปล: ขอคอมเมนต์การเดินลายทองแดงของตัวเก็บประจุ Decoupling ใต้ BGA (C401-C420 ขนาด 0402 1.0µF) พบว่ามีลายเส้นยาวประมาณ 2.0 mm จาก Pad ไปยัง Via และรูเจาะฝั่งไฟกับกราวด์ถูกวางแยกห่างกัน โครงสร้างนี้ขยายพื้นที่ลูป ทำให้ Loop Inductance พุ่งสูงถึง 1.6 nH ส่งผลให้ MLCC สูญเสียความสามารถในการทำงานที่ความถี่สูงไปอย่างสิ้นเชิง ขอให้ยกเลิกลายเส้นลากเชื่อม และเปลี่ยนเป็นแบบ Side-Via หรือใช้ Via-in-Pad (VIPPO) วางรูเจาะใน Pad โดยตรง เพื่อคุมให้ Parasitic Inductance ต่ำกว่า 0.3 nH เพื่อฟื้นฟูคุณสมบัติ Transient Response ให้เป็นไปตามสเปก)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณ Target Impedance และขนาดของตัวเก็บประจุ Bulk รวมเพื่อรองรับ Transient Step

โมดูล AI Accelerator ประมวลผล Tensor Core บนสถาปัตยกรรม 7nm ใช้รางไฟหลัก $V_{DD} = 0.75\text{ V}$ มีพฤติกรรมการดึงกระแสสลับอย่างรวดเร็ว (Transient Step) จากสภาวะ Sleep Mode ($I_{min} = 5\text{ A}$) ขึ้นสู่สภาวะ Full Inference Load ($I_{max} = 55\text{ A}$) โดยมีอัตราการเปลี่ยนแปลงกระแส $\frac{di}{dt} = 50\text{ A/ns}$

ข้อกำหนดความน่าเชื่อถือของชิประบุว่า แรงดันกระเพื่อมสูงสุดที่ยอมรับได้คือ $\pm 4\%$ ของแรงดันระบุ ภาคจ่ายไฟสวิตชิ่ง (VRM) บนบอร์ดมีความถี่การทำงาน (Switching Frequency) $f_{sw} = 1.0\text{ MHz}$ และมีเวลาในการตอบสนองของลูปควบคุมป้อนกลับ (Closed-loop Response Time) $\Delta t_{VRM} = 2.5\ \mu\text{s}$

จงคำนวณ:
1. ค่า Target Impedance ($Z_{target}$) สูงสุดที่ยอมรับได้ของระบบ PDN
2. ขนาดความจุไฟฟ้าของตัวเก็บประจุ Bulk รวมขั้นต่ำ ($C_{bulk, min}$) ที่ต้องติดตั้งบนบอร์ด เพื่อทำหน้าที่จ่ายพลังงานให้กับชิปในช่วงที่ VRM ยังไม่ตอบสนอง โดยสมมติว่าตัวเก็บประจุจ่ายพลังงานฝ่ายเดียวตลอดช่วงเวลา $2.5\ \mu\text{s}$
3. ค่า Equivalent Series Resistance (ESR) สูงสุดของตัวเก็บประจุ Bulk รวม ที่ยอมรับได้เพื่อไม่ให้เกิด $\Delta V$ เกินพิกัด?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณค่า Target Impedance ($Z_{target}$):**
- แรงดันกระเพื่อมสูงสุดที่ยอมรับได้:
  $$\Delta V_{allowed} = V_{DD} \times 4\% = 0.75\text{ V} \times 0.04 = 0.030\text{ V} = 30\text{ mV}$$
- ขนาดของกระแส Transient Step:
  $$\Delta I = I_{max} - I_{min} = 55\text{ A} - 5\text{ A} = 50\text{ A}$$
- คำนวณ $Z_{target}$:
  $$Z_{target} = \frac{\Delta V_{allowed}}{\Delta I} = \frac{0.030\text{ V}}{50\text{ A}} = 0.0006\ \Omega = 0.6\text{ m}\Omega \ (600\ \mu\Omega)$$

**2. คำนวณขนาดความจุ Bulk รวมขั้นต่ำ ($C_{bulk, min}$):**
ในช่วงเวลาที่ VRM ยังไม่เริ่มตอบสนอง ($\Delta t_{VRM} = 2.5\ \mu\text{s} = 2.5 \times 10^{-6}\text{ s}$) พลังงานประจุทั้งหมดที่จ่ายกระแส $\Delta I = 50\text{ A}$ จะต้องมาจากตัวเก็บประจุ Bulk บนแผ่น PCB:
$$I = C \cdot \frac{dv}{dt} \implies C_{bulk, min} \ge \frac{\Delta I \cdot \Delta t_{VRM}}{\Delta V_{allowed}}$$

แทนค่าในสมการ:
$$C_{bulk, min} \ge \frac{50\text{ A} \times (2.5 \times 10^{-6}\text{ s})}{0.030\text{ V}} = \frac{1.25 \times 10^{-4}}{0.030} \approx 4.167 \times 10^{-3}\text{ F} = 4,167\ \mu\text{F}$$

ดังนั้น ต้องใช้ตัวเก็บประจุแบบ Low-ESR Polymer Tantalum ขนาด $470\ \mu\text{F}$ จำนวนอย่างน้อยที่สุด **9 - 10 ตัว** ขนานกันเพื่อรองรับประจุในช่วงแรก

**3. คำนวณค่า ESR สูงสุดที่ยอมรับได้:**
ทันทีที่กระแสสลับพุ่งขึ้น จะเกิดแรงดันตกคร่อมความต้านทานภายในตัวเก็บประจุทันที ($\Delta V_{ESR} = \Delta I \cdot ESR$):
หากยอมให้แรงดันตกจาก ESR คิดเป็นครึ่งหนึ่งของงบประมาณแรงดันกระเพื่อม ($\Delta V_{ESR} \le \frac{\Delta V_{allowed}}{2} = 15\text{ mV}$):
$$ESR_{total} \le \frac{15\text{ mV}}{50\text{ A}} = 0.3\text{ m}\Omega$$

**บทสรุปของ Senior Engineer:** หากเลือกใช้ตัวเก็บประจุ Polymer ขนาด $470\ \mu\text{F}$ ที่มีค่า $ESR = 4.5\text{ m}\Omega$ ต่อตัว การต่อขนานกัน 10 ตัวจะให้ค่า $ESR_{total} = \frac{4.5}{10} = 0.45\text{ m}\Omega$ ซึ่งเกือบแตะเพดานที่ยอมรับได้ จึงจำเป็นต้องเสริมด้วย MLCC ขนาดใหญ่ ($100\ \mu\text{F}$) เพื่อดึงค่า ESR รวมลงมาให้ต่ำกว่า $0.3\text{ m}\Omega$

---

### คำถามที่ 2: การวิเคราะห์ปรากฏการณ์ Anti-Resonance ระหว่าง Bulk Capacitor และ High-Frequency MLCC

ระบบจ่ายไฟมีตัวเก็บประจุ 2 กลุ่มต่อขนานกันบนระนาบรางจ่ายไฟเดียวกัน:
- **กลุ่มที่ 1 (Bulk Polymer Cap):** มีความจุ $C_1 = 220\ \mu\text{F}$, มีความเหนี่ยวนำรวม $L_1 = 1.2\text{ nH}$, และมีความต้านทาน $R_1 (ESR_1) = 6\text{ m}\Omega$
- **กลุ่มที่ 2 (MLCC Array):** มีความจุรวม $C_2 = 2.2\ \mu\text{F}$, มีความเหนี่ยวนำรวม $L_2 = 0.2\text{ nH}$, และมีความต้านทานต่ำมาก $R_2 (ESR_2) = 1.5\text{ m}\Omega$

จงคำนวณ:
1. ความถี่เรโซแนนซ์อนุกรมเฉพาะตัว (Series Self-Resonant Frequency: SRF) ของทั้งสองกลุ่ม ($f_{SRF1}$ และ $f_{SRF2}$)
2. ความถี่ที่เกิดยอดเรโซแนนซ์ขนาน (Parallel Anti-Resonant Frequency: $f_{anti}$) ระหว่างความเหนี่ยวนำของกลุ่มที่ 1 กับความจุของกลุ่มที่ 2
3. ขนาดของอิมพีแดนซ์สูงสุด ณ จุดยอดเรโซแนนซ์ขนาน ($|Z_{peak}|$) โดยประมาณ และอธิบายเหตุใดระบบจึงเสี่ยงต่อการเกิด Voltage Collapse หากความถี่สวิตชิ่งของโหลดไปตรงกับจุดนี้?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณความถี่ Self-Resonant Frequency (SRF):**
$$f_{SRF} = \frac{1}{2\pi \sqrt{L \cdot C}}$$

- **สำหรับกลุ่มที่ 1 ($C_1 = 220\ \mu\text{F}, L_1 = 1.2\text{ nH}$):**
  $$f_{SRF1} = \frac{1}{2\pi \sqrt{(1.2 \times 10^{-9}) \cdot (220 \times 10^{-6})}} = \frac{1}{2\pi \sqrt{2.64 \times 10^{-13}}} \approx \frac{1}{2\pi \times 5.138 \times 10^{-7}} \approx 309.7\text{ kHz}$$
- **สำหรับกลุ่มที่ 2 ($C_2 = 2.2\ \mu\text{F}, L_2 = 0.2\text{ nH}$):**
  $$f_{SRF2} = \frac{1}{2\pi \sqrt{(0.2 \times 10^{-9}) \cdot (2.2 \times 10^{-6})}} = \frac{1}{2\pi \sqrt{4.4 \times 10^{-16}}} \approx \frac{1}{2\pi \times 2.098 \times 10^{-8}} \approx 7.587\text{ MHz}$$

**2. คำนวณความถี่ Anti-Resonance ($f_{anti}$):**
ในช่วงความถี่ระหว่าง $f_{SRF1}$ กับ $f_{SRF2}$ ($310\text{ kHz} < f < 7.6\text{ MHz}$):
กลุ่มที่ 1 จะทำตัวเป็นตัวเหนี่ยวนำ ($L_1 = 1.2\text{ nH}$) ในขณะที่กลุ่มที่ 2 ยังคงทำตัวเป็นตัวเก็บประจุ ($C_2 = 2.2\ \mu\text{F}$)
การต่อขนานกันของ $L_1$ และ $C_2$ ก่อให้เกิดวงจรเรโซแนนซ์แบบขนาน (Tank Circuit):

$$f_{anti} \approx \frac{1}{2\pi \sqrt{L_1 \cdot C_2}}$$
$$f_{anti} \approx \frac{1}{2\pi \sqrt{(1.2 \times 10^{-9}) \cdot (2.2 \times 10^{-6})}} = \frac{1}{2\pi \sqrt{2.64 \times 10^{-15}}} \approx \frac{1}{2\pi \times 5.138 \times 10^{-8}} \approx 3.097\text{ MHz}$$

**3. คำนวณขนาดของอิมพีแดนซ์ยอดแหลม ($|Z_{peak}|$):**
อิมพีแดนซ์ของวงจรขนาน $LC$ ที่มีค่าความต้านทานอนุกรม $R_{total} = R_1 + R_2$:
$$|Z_{peak}| \approx \frac{L_1}{C_2 \cdot (R_1 + R_2)}$$

แทนค่าตัวเลข:
- $R_{total} = 6\text{ m}\Omega + 1.5\text{ m}\Omega = 7.5\text{ m}\Omega = 7.5 \times 10^{-3}\ \Omega$
$$|Z_{peak}| \approx \frac{1.2 \times 10^{-9}\text{ H}}{(2.2 \times 10^{-6}\text{ F}) \cdot (7.5 \times 10^{-3}\ \Omega)} = \frac{1.2 \times 10^{-9}}{1.65 \times 10^{-8}} \approx 0.0727\ \Omega = 72.7\text{ m}\Omega$$

**บทวิเคราะห์ของ Senior Engineer:**
- ค่าอิมพีแดนซ์ปกติของตัวเก็บประจุทั้งสองอยู่ที่ $1.5 - 6\text{ m}\Omega$ แต่ ณ ความถี่ **$3.1\text{ MHz}$** ค่าอิมพีแดนซ์กลับพุ่งขึ้นสูงถึง **$72.7\text{ m}\Omega$ (สูงขึ้นกว่าเดิมกว่า 10 - 50 เท่า!)**
- หากวงจรประมวลผลมีสัญญาณ Clock หรือฮาร์โมนิกของการสลับโหลดเกิดขึ้นที่ความถี่ใกล้เคียง $3.1\text{ MHz}$ กระแสชั่วขณะเพียง $2\text{ A}$ จะสร้างแรงดันตกคร่อม $\Delta V = 2\text{ A} \times 72.7\text{ m}\Omega = 145.4\text{ mV}$ ซึ่งจะทำให้รางไฟพังทลายทันที
- การแก้ไขคือการเพิ่มตัวเก็บประจุค่ากลาง ($10\ \mu\text{F} - 22\ \mu\text{F}$) ที่มีค่า ESR พอเหมาะเข้ามาคั่นกลาง เพื่อดึงยอด Anti-resonance ให้ราบลง (ESR Damping Method)

---

### คำถามที่ 3: การคำนวณ Loop Inductance ของ Decoupling Capacitor ตามโครงสร้าง Via Placement

ตัวเก็บประจุ MLCC ขนาด 0402 ($1.0\text{ mm} \times 0.5\text{ mm}$) ค่า $0.1\ \mu\text{F}$ มีค่าความเหนี่ยวนำภายในตัวถัง $ESL_{cap} = 0.35\text{ nH}$ ติดตั้งบนชั้นผิว Top Layer ของบอร์ด 8 เลเยอร์ โดยมีระนาบ Ground อยู่ที่ Layer 2 (ลึก $h = 0.1\text{ mm}$) 

วิศวกรเปรียบเทียบการเดินลายทองแดง 2 วิธี:
- **วิธีที่ 1 (End-Trace Placement):** เดินลายเส้นทองแดงกว้าง $0.25\text{ mm}$ ยาว $1.5\text{ mm}$ จากปลาย Pad ทั้งสองฝั่งไปยังรูเจาะ Via ขนาด Drill $0.25\text{ mm}$ ทำให้เกิด Loop Area กว้าง
- **วิธีที่ 2 (Side-Via VIPPO Placement):** วางรูเจาะ Via ชิดติดข้าง Pad (Side-Via) โดยมีระยะห่างศูนย์กลางระหว่าง Via กราวด์และไฟเพียง $s = 0.6\text{ mm}$

ความเหนี่ยวนำของกระบอกรู Via คู่ข้ามระยะลึก $h = 0.1\text{ mm}$ ที่มีระยะห่าง $s$ คำนวณได้โดยประมาณจาก:

$$L_{via-pair} \approx \frac{\mu_0 \cdot h}{\pi} \ln\left( \frac{s}{r_{via}} \right)$$

กำหนดให้:
- วิธีที่ 1: มีความเหนี่ยวนำลายเส้น $L_{trace} \approx 0.8\text{ nH}$ และ $L_{via-pair} \approx 0.45\text{ nH}$
- วิธีที่ 2: ไม่มีลายเส้น ($L_{trace} = 0$) และระยะชิดทำให้ $L_{via-pair} \approx 0.12\text{ nH}$

จงคำนวณ:
1. Loop Inductance รวม ($L_{total}$) ของทั้งสองวิธี
2. ความถี่เรโซแนนซ์ใช้งานจริง ($f_{SRF, real}$) ของทั้งสองวิธี
3. อิมพีแดนซ์ของตัวเก็บประจุที่ความถี่สัญญาณนาฬิกา $100\text{ MHz}$ ($Z_{cap} \approx 2\pi f L_{total}$) เปรียบเทียบระหว่างสองวิธี?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณ Loop Inductance รวม ($L_{total} = ESL_{cap} + L_{trace} + L_{via-pair}$):**
- **วิธีที่ 1 (End-Trace):**
  $$L_{total, 1} = 0.35\text{ nH} + 0.80\text{ nH} + 0.45\text{ nH} = 1.60\text{ nH}$$
- **วิธีที่ 2 (Side-Via):**
  $$L_{total, 2} = 0.35\text{ nH} + 0.00\text{ nH} + 0.12\text{ nH} = 0.47\text{ nH}$$

**2. คำนวณความถี่เรโซแนนซ์ใช้งานจริง ($C = 0.1\ \mu\text{F} = 1.0 \times 10^{-7}\text{ F}$):**
- **วิธีที่ 1:**
  $$f_{SRF, 1} = \frac{1}{2\pi \sqrt{L_{total, 1} \cdot C}} = \frac{1}{2\pi \sqrt{(1.60 \times 10^{-9}) \cdot (1.0 \times 10^{-7})}} = \frac{1}{2\pi \sqrt{1.60 \times 10^{-16}}} \approx \frac{1}{2\pi \times 1.265 \times 10^{-8}} \approx 12.58\text{ MHz}$$
- **วิธีที่ 2:**
  $$f_{SRF, 2} = \frac{1}{2\pi \sqrt{L_{total, 2} \cdot C}} = \frac{1}{2\pi \sqrt{(0.47 \times 10^{-9}) \cdot (1.0 \times 10^{-7})}} = \frac{1}{2\pi \sqrt{4.70 \times 10^{-17}}} \approx \frac{1}{2\pi \times 6.856 \times 10^{-9}} \approx 23.21\text{ MHz}$$

**3. คำนวณอิมพีแดนซ์ที่ความถี่ $100\text{ MHz}$ ($f = 100 \times 10^6\text{ Hz}$):**
ที่ความถี่ $100\text{ MHz}$ ซึ่งสูงกว่า SRF มาก ตัวเก็บประจุจะแสดงพฤติกรรมเป็นตัวเหนี่ยวนำอย่างสมบูรณ์ ($Z \approx 2\pi f L_{total}$):
- **วิธีที่ 1:**
  $$Z_1 = 2\pi \times (100 \times 10^6\text{ Hz}) \times (1.60 \times 10^{-9}\text{ H}) \approx 1.005\ \Omega$$
- **วิธีที่ 2:**
  $$Z_2 = 2\pi \times (100 \times 10^6\text{ Hz}) \times (0.47 \times 10^{-9}\text{ H}) \approx 0.295\ \Omega$$

**บทสรุปของ Senior Engineer:**
- ที่ความถี่ $100\text{ MHz}$ วิธีที่ 2 ให้ค่าอิมพีแดนซ์ **ต่ำกว่าวิธีที่ 1 ถึง $3.4$ เท่า** ($0.295\ \Omega$ เทียบกับ $1.005\ \Omega$)
- การลากลายเส้นยาวเพียง $1.5\text{ mm}$ ได้ทำลายประสิทธิภาพของตัวเก็บประจุ 0402 ไปมากกว่า $70\%$ นี่คือเหตุผลที่ในงาน High-Speed PDN ต้องเข้มงวดกับตำแหน่งของ Via ติดชิด Pad เสมอ
