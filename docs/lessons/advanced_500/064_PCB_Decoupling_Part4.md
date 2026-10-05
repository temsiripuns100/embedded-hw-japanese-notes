# Lesson 064: PCB Decoupling Part 4 - OJT Placement, Routing Geometries, and Loop Inductance Optimization

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในวงจรดิจิทัลความถี่สูง ประสิทธิภาพในการส่งผ่านพลังงานของตัวเก็บประจุ Decoupling (Capacitor Effectiveness) ไม่ได้ถูกจำกัดด้วยค่าความจุไฟฟ้า ($C$) อีกต่อไป แต่ถูกจำกัดโดย **ความเหนี่ยวนำของลูปจ่ายกระแส 3 มิติ (3D Total Loop Inductance: $L_{loop}$)** ที่เชื่อมต่อระหว่างตัวถังตัวเก็บประจุลงสู่ระนาบ Power/Ground และขึ้นสู่ตัวถังชิป IC

```
+-------------------------------------------------------------------------+
|                  Total 3D Loop Inductance Breakdown                     |
|                                                                         |
|  L_total_loop = L_internal + L_trace_pad + L_via_vertical + L_spreading |
|                                                                         |
|      [ MLCC Body (L_internal ~ 0.2 - 0.8 nH) ]                          |
|         │                                │                              |
|      [ Surface Pad & Trace (L_trace ~ 0.5 - 1.5 nH/mm) ]                |
|         │                                │                              |
|      [ Vertical Via Pair (L_via ~ 0.2 - 1.2 nH depending on depth h) ]  |
|         │                                │                              |
|   ══════▼════════════════════════════════▼══════ Power Plane (Layer X)  |
|         │◄─── Spreading Loop Area (d) ──►│                              |
|   ══════════════════════════════════════════════ Ground Plane (Layer X+1)|
+-------------------------------------------------------------------------+
```

### 1.1 การแยกองค์ประกอบของความเหนี่ยวนำในแนวตั้ง (Vertical Via-Pair Loop Inductance)

เมื่อกระแสไฟฟ้าไหลออกจากตัวเก็บประจุบนชั้นผิวนอก (Top หรือ Bottom Layer) กระแสจะต้องเดินทางผ่านรูเจาะ Via เพื่อลงไประนาบ Power Plane และกระแสไหลกลับ (Return Current) จะไหลย้อนขึ้นผ่าน Via อีกตัวหนึ่งจาก Ground Plane 

โครงสร้าง Via สองตัวที่นำกระแสในทิศทางตรงกันข้าม (Anti-parallel Current Flow) จะสร้างความเหนี่ยวนำวงรอบในแนวตั้งฉาก (Vertical Loop Inductance) ซึ่งคำนวณได้จากทฤษฎีสนามแม่เหล็ก:

$$L_{via\_pair} = \frac{\mu_0 \cdot h}{\pi} \left[ \ln\left( \frac{s}{r_{via}} \right) + \frac{1}{4} \right] \quad [\text{H}]$$

โดยที่:
- $\mu_0 = 4\pi \times 10^{-7}\text{ H/m}$ (Permeability of Free Space)
- $h$ คือ ความลึกจากผิวนอกถึงระนาบ Power/Ground คู่แรก (**Plane Depth**, $\text{m}$)
- $s$ คือ ระยะห่างกึ่งกลางระหว่าง Via ไฟและกราวด์ (**Via-to-Via Center Spacing**, $\text{m}$)
- $r_{via}$ คือ รัศมีของรูเจาะ Via ($\text{m}$)

#### ข้อสังเกตเชิงลึกระดับ Senior:
1. **ความลึกของระนาบ ($h$) คือตัวแปรเชิงเส้นที่มีผลรุนแรงที่สุด:** หากคู่ระนาบ Power/GND อยู่ที่ Layer 2 และ 3 ($h \approx 0.15\text{ mm}$) ค่า $L_{via\_pair}$ จะมีค่าต่ำเพียง $\approx 0.15\text{ nH}$ แต่หากผู้ออกแบบจัด Stackup พลาด นำระนาบ Power/GND ไปไว้ที่ Layer 10 และ 11 ในบอร์ดหนา ($h \approx 1.2\text{ mm}$) ค่า $L_{via\_pair}$ จะพุ่งสูงขึ้นเป็น **$1.2\text{ nH} - 1.5\text{ nH}$ ทันที (สูงขึ้น 8 - 10 เท่า!)**
2. **การหักล้างของฟลักซ์แม่เหล็ก (Mutual Flux Cancellation):** ยิ่งระยะห่างระหว่าง Via ($s$) แคบลง สนามแม่เหล็กที่วนรอบ Via ทั้งสองจะหักล้างกันเองมากขึ้น ทำให้ความเหนี่ยวนำรวมลดลงตามฟังก์ชัน $\ln(s/r)$

### 1.2 ความเหนี่ยวนำการกระจายตัวบนระนาบทองแดง (Plane Spreading Inductance)

เมื่อกระแสหลุดพ้นจากกระบอกรู Via เข้าสู่ระนาบแผ่นขนาน Power/Ground กระแสจะแผ่ขยายตัวออกเป็นวงกลมในแนวระนาบ $x-y$ ก่อให้เกิด Spreading Inductance ($L_{spread}$):

$$L_{spread} = \frac{\mu_0 \cdot d}{2\pi} \ln\left( \frac{R_{load}}{r_{via}} \right) \quad [\text{H}]$$

โดยที่:
- $d$ คือ ระยะห่างไดอิเล็กทริกระหว่างระนาบ Power และ Ground (**Dielectric Thickness between planes**, $\text{m}$)
- $R_{load}$ คือ ระยะทางจาก Via ของตัวเก็บประจุไปยัง Via ของโหลดชิป IC ($\text{m}$)

สมการนี้แสดงให้เห็นว่า **ยิ่งชั้นฉนวนระหว่าง Power และ Ground บางลงเท่าใด ($d \to \text{min}$) ค่าความเหนี่ยวนำการกระจายกระแสก็จะยิ่งต่ำลงเท่านั้น** นี่คือเหตุผลทางฟิสิกส์ว่าทำไมการใช้ Prepreg ชนิดบางพิเศษ ($2 - 3\text{ mils} / 50 - 75\ \mu\text{m}$) จึงมีความสำคัญอย่างยิ่งยวดต่อระบบ PDN ความเร็วสูง

### 1.3 ปรากฏการณ์รังผึ้งรูพรุน (Swiss-Cheese Effect on Power/Ground Planes)

เมื่อวาง BGA พินหนาแน่น (เช่น BGA พิทช์ $0.8\text{ mm}$ หรือ $1.0\text{ mm}$) รูเจาะ Vias นับร้อยตัวจะเจาะทะลุผ่านระนาบทองแดง รอบรูเจาะแต่ละรูจะมีวงแหวนฉนวนทองแดง (Anti-pad Clearance Void) 

หากวิศวกรขยาย Anti-pad กว้างเกินไป ($D_{anti} > \text{Via Pitch}$) วงแหวนฉนวนจะเกิดการเชื่อมต่อซ้อนทับกัน (Merged Anti-pads) กลายเป็นร่องผ่าระนาบทองแดงขาดออกจากกัน (Swiss-Cheese Perforation):

```
Normal Plane (Solid Copper Bridge):
   ( O ) ─── Copper Bridge ─── ( O )
            (Current flows freely)

Merged Anti-pads (Swiss-Cheese Disaster):
   (     O     )XXXXXXXXX(     O     )
                 ▲
                 │ Copper is SEVERED! Current must detour!
                 ▼
   ═══════════════════════════════════ (Path elongated 3x - 5x!)
```

ผลกระทบคือ กระแสไหลกลับไม่สามารถวิ่งเป็นเส้นตรงได้ แต่ถูกบีบให้เลี้ยวอ้อมไปตามคอคอดทองแดงที่คดเคี้ยว ส่งผลให้ **Plane Inductance พุ่งสูงขึ้นกว่าปกติถึง $300\% - 500\%$** และก่อให้เกิดปรากฏการณ์ความต้านทานกระแสไฟตรง (DC IR Drop) สูงเกินสเปก

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)

**เหตุการณ์:** เมนบอร์ดสวิตช์เครือข่ายความเร็วสูงระดับศูนย์ข้อมูล (Data Center 400G Network Switch) ใช้ชิป ASIC สถาปัตยกรรม 7nm (มี 112Gbps PAM4 SerDes จำนวน 64 ช่อง) บอร์ดเป็นแบบ 18-Layer High-Tg Low-Loss PCB ความหนารวม $2.4\text{ mm}$ รางไฟคอร์ $V_{DD\_CORE} = 0.75\text{ V}$ กระแสไฟฟ้าสูงสุด $120\text{ A}$ 

**อาการล้มเหลว:**
1. ในขั้นตอนการทดสอบ Eye Diagram ของช่องสัญญาณ 112G SerDes พบค่า Jitter สูงผิดปกติ (High Random Jitter: $R_j$) และดวงตาสัญญาณปิดสนิท (Eye Closure) อัตราความผิดพลาดของบิต (Bit Error Rate: BER) อยู่ที่ $10^{-4}$ (เกณฑ์มาตรฐานต้องการ $< 10^{-12}$)
2. เมื่อตรวจสอบภาคจ่ายไฟ $0.75\text{ V}$ ใต้ BGA พบว่ามีคลื่นสัญญาณรบกวนกระเพื่อมรุนแรงถึง $65\text{ mV}_{\text{p-p}}$ (สเปกยอมรับได้ไม่เกิน $\pm 20\text{ mV}$)
3. แม้ว่าทีมงานจะติดตั้งตัวเก็บประจุ 0402 MLCC ขนาด $1.0\ \mu\text{F}$ จำนวนถึง 120 ตัวไว้ที่ด้านล่างของบอร์ด (Bottom Layer) ใต้ BGA แต่การเพิ่มตัวเก็บประจุกลับไม่ช่วยลดสัญญาณรบกวนลงเลยแม้แต่น้อย

```
[Defect Mechanism: Deep Plane Allocation & Swiss-Cheese Plane]
  Bottom-Side MLCC (Layer 18)
      │
      ▼ (Drill Depth h = 2.0 mm through 14 layers!)
  ═══════════════════════════════════════════════════
  ═══════════════════════════════════════════════════
  Power Plane (Placed at Layer 14/15!) ---> L_via > 2.8 nH!
  ═══════════════════════════════════════════════════
  Anti-pads merged under BGA ---> Swiss-Cheese Necking!
      │
      ▼
  ASIC Silicon Die (Layer 1) ---> STARVED OF TRANSIENT CHARGE!
```

**Root Cause Analysis (RCA):**
1. **การจัด Layer Stackup ที่ผิดหลักการอย่างร้ายแรง:** วิศวกรจัดวางระนาบรางไฟหลัก $V_{DD\_CORE}$ ไว้ที่ **Layer 14 และ 15** (เพื่อความสะดวกในการลากลายสัญญาณ High-Speed ที่เลเยอร์บนๆ) ส่งผลให้ตัวเก็บประจุ Decoupling ที่ติดตั้งอยู่ฝั่ง Bottom Layer (Layer 18) ต้องเจาะรู Via ลึกผ่านความหนา $h \approx 0.6\text{ mm}$ และตัวเก็บประจุฝั่ง Top Layer (Layer 1) ต้องเจาะลึกผ่านความหนา $h \approx 1.8\text{ mm}$ ทำให้ Loop Inductance รวมของตัวเก็บประจุพุ่งสูงถึง **$2.4\text{ nH} - 2.8\text{ nH}$ ต่อตัว** ซึ่งที่ความถี่สูงกว่า $30\text{ MHz}$ ตัวเก็บประจุเหล่านี้ถูกบล็อกด้วยความเหนี่ยวนำจนไม่สามารถจ่ายกระแสได้เลย
2. **Swiss-Cheese Effect ใต้ BGA:** รูเจาะ Escape Vias ใต้ BGA ที่มีระยะพิทช์ $0.8\text{ mm}$ มีการตั้งค่า Anti-pad Clearance ในไฟล์ CAD กว้าง $0.65\text{ mm}$ ส่งผลให้วงแหวนตัดขาดซ้อนทับกันอย่างต่อเนื่อง ระนาบกราวด์และไฟกลายเป็นตาข่ายที่มีรูพรุน กระแสไฟตรงเกิดรอยคอด เกิดแรงดันตกคร่อม $\Delta V_{IR} = 42\text{ mV}$ บนเนื้อทองแดงก่อนถึงตัวชิป

---

### Step-by-Step Engineering Checklist: กฎทองของการจัดวางและการเดินลายทองแดง Decoupling

#### ขั้นตอนที่ 1: การจัดลำดับเรขาคณิตของ Via และ Pad (Via-to-Pad Geometry Hierarchy)
ลำดับประสิทธิภาพในการลด Loop Inductance จากแย่ที่สุดไปหาดีที่สุด:

```
Rank 4 (Worst): End-Trace Connection
  [ Pad ] ── Long Trace (2mm) ── [ Via ]  ---> L_loop ~ 1.5 - 2.5 nH
  (FATAL: Avoid at all costs in high-speed designs!)

Rank 3 (Fair): End-Via Connection
  [ Pad ][ Via ]                          ---> L_loop ~ 0.8 - 1.2 nH

Rank 2 (Good): Side-Via Connection (Wide Bridge)
  [ Via ] [ Pad ]                         ---> L_loop ~ 0.4 - 0.6 nH
  (Via placed adjacent to side of pad, shortest magnetic loop)

Rank 1 (Best): Via-in-Pad Plated Over (VIPPO)
  [ (Via Inside Pad) ]                    ---> L_loop ~ 0.15 - 0.25 nH
  (Direct vertical coaxial entry, minimum loop area)
```

- **กฎเหล็ก OJT:** หากใช้ Side-Via ให้วาง Via ไฟและ Via กราวด์ให้อยู่ฝั่งตรงข้ามกันหรือขนานกันในระยะที่ใกล้ที่สุด เพื่อให้กระแสไหลสวนทางกัน เกิดการหักล้างของฟลักซ์แม่เหล็ก ($M < 0$) ช่วยลดความเหนี่ยวนำลงได้อีก $30\%$

```
+-------------------------------------------------------------+
|  Optimal Side-Via Layout (Maximum Mutual Cancellation):     |
|                                                             |
|           [ GND Via ]             [ PWR Via ]               |
|                │                       │                    |
|                ▼                       ▼                    |
|          ┌──────────┐             ┌──────────┐              |
|          │ GND Pad  │  [ MLCC ]   │ PWR Pad  │              |
|          └──────────┘  Body       └──────────┘              |
|                                                             |
|  Current:  ▲ Upward                 ▼ Downward              |
|  Flux:    (CCW Loop)               (CW Loop)                |
|            ====> Magnetic Fields Cancel Out! <====          |
+-------------------------------------------------------------+
```

#### ขั้นตอนที่ 2: การออกแบบ Stackup เพื่อควบคุม Plane Depth ($h$)
- **Power Rail คอร์หลัก ($V_{DD} < 1.0\text{ V}$) ต้องอยู่ติดกับชั้นผิวที่สุด:**
  - หากชิ้นส่วนวางบน Top Layer: ให้วาง Power Plane ไว้ที่ Layer 2 หรือ Layer 3 โดยมี GND Plane ประกบติดกันทันที
  - หากชิ้นส่วนเป็น BGA ขนาดใหญ่ที่มีตัวเก็บประจุอยู่ใต้ท้องบอร์ด (Bottom Layer): ให้จัดวางระนาบ Power/GND ของคอร์นั้นไว้ที่ **Layer รองสุดท้าย (เช่น L16/L17 ในบอร์ด 18 ชั้น)** เพื่อให้ความลึกของรูเจาะจากตัวเก็บประจุสั้นที่สุด ($h \le 0.15 - 0.20\text{ mm}$)
- **ระยะห่างระหว่าง Power และ GND (Dielectric Thickness $d$):**
  - กำหนดความหนาของชั้น Prepreg ระหว่างระนาบคู่ให้อยู่ระหว่าง **$50\ \mu\text{m} - 75\ \mu\text{m}$ ($2 - 3\text{ mils}$)** เพื่อเพิ่ม Inter-plane Capacitance และลด Spreading Inductance

#### ขั้นตอนที่ 3: การควบคุม Anti-Pad เพื่อป้องกัน Swiss-Cheese Effect
- **คำนวณสะพานทองแดงขั้นต่ำ (Copper Web Bridge):**
  $$\text{Web Width} = \text{Via Pitch} - D_{anti} \ge 0.15 - 0.20\text{ mm} \ (6 - 8\text{ mils})$$
- ในบริเวณใต้ BGA ที่มี Via หนาแน่น ห้ามให้ Anti-pad สัมผัสหรือซ้อนทับกันเด็ดขาด หากช่องว่างไม่พอ ให้พิจารณาลดขนาด Drill Hole (เช่น จาก $0.25\text{ mm}$ เป็น $0.20\text{ mm}$) หรือใช้เทคโนโลยี Micro-via / HDI แทน Through-hole

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คันจิ (Kanji) | คานะ (Kana) | คำอ่าน (Romaji) | ภาษาอังกฤษ / คำแปลภาษาไทย |
| :--- | :--- | :--- | :--- |
| **ループインダクタンス** | るーぷいんだくたんす | Rūpu Indakutansu | Loop Inductance (ความเหนี่ยวนำวงรอบ) |
| **ビア近接配置** | びあきんせつはいち | Bia Kinsetsu Haichi | Proximity Via Placement (การวางเวียชิดแพด) |
| **スイスチーズ現象** | すいすちーずげんしょう | Suisu Chīzu Genshō | Swiss-Cheese Effect (การพรุนของระนาบทองแดง) |
| **磁束相殺** | じそくそうさい | Jisoku Sōsai | Magnetic Flux Cancellation (การหักล้างฟลักซ์) |
| **プレーン層深さ** | ぷれーんそうふかさ | Purēn-sō Fukasa | Plane Layer Depth ($h$) |
| **アンチパッド間ブリッジ** | あんちぱっどかんぶりっじ | Anchi-paddo-kan Burijji | Anti-pad Web Bridge Width |
| **パッドオンビア** | ぱっどおんびあ | Paddo-on-Bia | Via-in-Pad (VIPPO) |
| **面内拡散インダクタンス**| めんないかくさんいんだくたんす | Mennai Kakusan Indakutansu | Plane Spreading Inductance |
| **逃げ配線** | にげはいせん | Nige Haisen | Escape Routing (ลายวงจรหลบออกจาก BGA) |
| **層間厚み** | そうかんあつみ | Sōkan Atsumi | Inter-layer Dielectric Thickness ($d$) |
| **電流集中** | でんりゅうしゅうちゅう | Denryū Shūchū | Current Crowding (การกระจุกตัวของกระแส) |
| **リターン経路寸断** | りたーんけいろすんだん | Ritān Keiro Sundan | Return Path Disruption |

---

### 3.2 บันทึกการตรวจแบบของ Senior Engineer (検図指摘事項 - Kenzu Comments)

#### คอมเมนต์ที่ 1: ตรวจพบการจัด Stackup วางระนาบ Power ไว้ลึกเกินไป ทำลายคุณสมบัติ Decoupling
> **検図指摘 (Kenzu Feedback 1):**  
> 「14層高多層基板におけるFPGAコア電源（$V_{CCINT} = 0.85\text{V}$、消費電流35A）の層構成（スタックアップ）について重大な指摘を行います。設計データでは、コア電源プレーンがL10、GNDプレーンがL11に配置されています。この構成では、表面（L1）および裏面（L14）に実装されたデカップリングコンデンサから電源プレーンまでの垂直距離（深さ$h$）が1.0mm以上となり、ビア対の寄生インダクタンス（$L_{via\_pair}$）が単体で$1.4\text{nH}$を超過します。結果として、コンデンサの実装共振周波数が20MHz以下に制限され、高速トランジェントノイズに対するバイパス機能が破綻します。層構成を緊急改訂し、コア電源およびリターンGNDのペアをL2/L3（表面直下）またはL12/L13（裏面直下）へ再配置し、層間プリプレグ厚を$60\mu\text{m}$以下に設定して垂直ループ面積を極小化してください。」  
> *(คำแปล: ขอคอมเมนต์ร้ายแรงเกี่ยวกับการจัด Stackup ของรางไฟ FPGA Core (0.85V, 35A) ในบอร์ด 14 ชั้น ข้อมูลระบุว่า Power Plane ถูกวางไว้ที่ L10 และ GND อยู่ที่ L11 โครงสร้างนี้ทำให้ระยะทางในแนวดิ่งจากตัวเก็บประจุบนชั้น L1 และ L14 ลงสู่ระนาบมีความลึกมากกว่า 1.0 mm ส่งผลให้ความเหนี่ยวนำของคู่ Via พุ่งสูงเกิน 1.4 nH ทำให้ความถี่เรโซแนนซ์ถูกจำกัดเหลือต่ำกว่า 20 MHz และสูญเสียคุณสมบัติในการกรองสัญญาณรบกวนความเร็วสูง ขอให้ปรับแก้ Stackup ด่วน โดยย้ายคู่ระนาบ Power/GND มาไว้ที่ L2/L3 (ใต้ผิวบน) หรือ L12/L13 (เหนือผิวล่าง) พร้อมทั้งคุมความหนา Prepreg ระหว่างชั้นให้ต่ำกว่า 60 µm เพื่อลดพื้นที่ลูปในแนวดิ่งให้เหลือน้อยที่สุด)*

#### คอมเมนต์ที่ 2: ปัญหา Swiss-Cheese Effect ใต้ BGA ขัดขวางกระแสไฟตรงและไฟสลับ
> **検図指摘 (Kenzu Feedback 2):**  
> 「ASIC直下（0.8mmピッチBGAエリア）の内層電源プレーンのボイド形状を検図しました。ファンアウトビア（穴径0.25mm、ランド径0.45mm）に対するアンチパッド直径が0.70mmで一律生成されており、隣接するアンチパッド同士が広範囲にわたり連結（マージ）しています。これにより、電源プレーンが網目状に寸断される『スイスチーズ現象』が発生し、プレーン抵抗が3倍以上に悪化、直流IRドロップが設計許容値（15mV）を大幅に超過しています。また、プレーン拡散インダクタンスも急増しています。アンチパッド径を0.60mmに縮小するとともに、長円形（オーバル）アンチパッドを採用してビア間に最低$0.18\text{mm}$以上の銅箔ブリッジ（Web幅）を確保し、ベタプレーンの導通性を回復させてください。」  
> *(คำแปล: ตรวจสอบรูปทรง Void บนระนาบ Power ใต้ชิป ASIC (พิทช์ 0.8 mm) พบว่า Anti-pad ของ Fanout Vias ถูกกำหนดขนาดไว้ 0.70 mm ส่งผลให้ Anti-pad ที่อยู่ติดกันเกิดการซ้อนทับกันเป็นวงกว้าง เกิดเป็นปรากฏการณ์ Swiss-Cheese ที่ตัดขาดระนาบทองแดง ทำให้ความต้านทานระนาบเพิ่มขึ้นกว่า 3 เท่า และค่า DC IR Drop สูงเกินเกณฑ์ 15 mV อีกทั้งยังเพิ่ม Spreading Inductance อีกด้วย ขอให้ลดขนาด Anti-pad เหลือ 0.60 mm หรือใช้ทรงวงรี (Oval) เพื่อรักษาแนวสะพานทองแดงระหว่าง Via ให้กว้างไม่ต่ำกว่า 0.18 mm เพื่อฟื้นฟูสภาพการนำกระแสของระนาบทองแดงให้สมบูรณ์)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณเปรียบเทียบ Vertical Loop Inductance ตามความลึกของระนาบใน Stackup

บอร์ดประมวลผล 12-Layer ความหนารวม $H = 2.0\text{ mm}$ มีตัวเก็บประจุ 0402 MLCC ติดตั้งอยู่ที่ Top Layer (Layer 1) โดยเชื่อมต่อลงระนาบ Power และ Ground ด้วยรูเจาะคู่ขนาดรัศมี $r_{via} = 0.125\text{ mm}$ (Drill Diameter $0.25\text{ mm}$) วางห่างกันด้วยระยะกึ่งกลาง $s = 0.75\text{ mm}$

วิศวกรเปรียบเทียบการจัดวาง Stackup 2 รูปแบบ:
- **รูปแบบที่ 1 (Shallow Plane Pair):** ระนาบ Power อยู่ที่ Layer 2 และ Ground อยู่ที่ Layer 3 โดยระยะกึ่งกลางระหว่าง Layer 1 ถึงระนาบคือความลึก $h_1 = 0.15\text{ mm}$
- **รูปแบบที่ 2 (Deep Plane Pair):** ระนาบ Power อยู่ที่ Layer 8 และ Ground อยู่ที่ Layer 9 โดยระยะกึ่งกลางระหว่าง Layer 1 ถึงระนาบคือความลึก $h_2 = 1.35\text{ mm}$

กำหนดสูตรคำนวณความเหนี่ยวนำของกระบอกรูเจาะคู่ขนาน:

$$L_{via\_pair} \approx \frac{\mu_0 \cdot h}{\pi} \left[ \ln\left( \frac{s}{r_{via}} \right) + 0.25 \right]$$

โดยที่ $\mu_0 = 4\pi \times 10^{-7}\text{ H/m} \implies \frac{\mu_0}{\pi} = 4 \times 10^{-7}\text{ H/m} = 0.4\text{ nH/mm}$

จงคำนวณ:
1. ค่าความเหนี่ยวนำของกระบอกรูเจาะคู่ ($L_{via\_pair}$) ของรูปแบบที่ 1 และ 2
2. หากตัวเก็บประจุมีค่า $C = 0.1\ \mu\text{F}$ และมีค่าความเหนี่ยวนำภายในตัวถัง $ESL_{cap} = 0.30\text{ nH}$ จงคำนวณหาความถี่เรโซแนนซ์ใช้งานจริง ($f_{SRF}$) ของทั้งสองรูปแบบ
3. สรุปผลกระทบต่อความสามารถในการ Bypass สัญญาณรบกวนที่ความถี่ $50\text{ MHz}$?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณความเหนี่ยวนำของกระบอกรูเจาะคู่ ($L_{via\_pair}$):**
- พจน์เรขาคณิตในวงเล็บ:
  $$\frac{s}{r_{via}} = \frac{0.75\text{ mm}}{0.125\text{ mm}} = 6.0$$
  $$\ln(6.0) + 0.25 \approx 1.7918 + 0.25 = 2.0418$$
- สัมประสิทธิ์ความเหนี่ยวนำต่อหน่วยความยาว:
  $$\frac{L}{h} = (0.4\text{ nH/mm}) \times 2.0418 \approx 0.8167\text{ nH/mm}$$

- **รูปแบบที่ 1 ($h_1 = 0.15\text{ mm}$):**
  $$L_{via\_pair, 1} = 0.8167\text{ nH/mm} \times 0.15\text{ mm} \approx 0.1225\text{ nH} = 122.5\text{ pH}$$
- **รูปแบบที่ 2 ($h_2 = 1.35\text{ mm}$):**
  $$L_{via\_pair, 2} = 0.8167\text{ nH/mm} \times 1.35\text{ mm} \approx 1.1026\text{ nH}$$

**2. คำนวณความถี่ Self-Resonant Frequency ($C = 0.1\ \mu\text{F} = 1.0 \times 10^{-7}\text{ F}$):**
- **รูปแบบที่ 1 ($L_{total, 1} = ESL_{cap} + L_{via, 1} = 0.30 + 0.1225 = 0.4225\text{ nH}$):**
  $$f_{SRF, 1} = \frac{1}{2\pi \sqrt{(0.4225 \times 10^{-9}) \cdot (1.0 \times 10^{-7})}} = \frac{1}{2\pi \sqrt{4.225 \times 10^{-17}}} \approx \frac{1}{2\pi \times 6.50 \times 10^{-9}} \approx 24.49\text{ MHz}$$
- **รูปแบบที่ 2 ($L_{total, 2} = ESL_{cap} + L_{via, 2} = 0.30 + 1.1026 = 1.4026\text{ nH}$):**
  $$f_{SRF, 2} = \frac{1}{2\pi \sqrt{(1.4026 \times 10^{-9}) \cdot (1.0 \times 10^{-7})}} = \frac{1}{2\pi \sqrt{1.4026 \times 10^{-16}}} \approx \frac{1}{2\pi \times 1.1843 \times 10^{-8}} \approx 13.44\text{ MHz}$$

**3. คำนวณอิมพีแดนซ์ที่ความถี่ $50\text{ MHz}$ ($f = 50 \times 10^6\text{ Hz}$):**
ที่ความถี่ $50\text{ MHz}$ สูงกว่าจุด SRF ทั้งคู่ อิมพีแดนซ์ถูกกำหนดโดย $X_L \approx 2\pi f L_{total}$:
- **รูปแบบที่ 1:**
  $$|Z_1| \approx 2\pi \times (50 \times 10^6) \times (0.4225 \times 10^{-9}) \approx 0.1327\ \Omega = 132.7\text{ m}\Omega$$
- **รูปแบบที่ 2:**
  $$|Z_2| \approx 2\pi \times (50 \times 10^6) \times (1.4026 \times 10^{-9}) \approx 0.4406\ \Omega = 440.6\text{ m}\Omega$$

**บทสรุปของ Senior Engineer:**
- การย้ายระนาบ Power/GND จาก Layer 2 ไปเป็น Layer 8 ทำให้ค่าอิมพีแดนซ์ที่ความถี่ $50\text{ MHz}$ **พุ่งสูงขึ้นถึง $3.3$ เท่า** (จาก $133\text{ m}\Omega$ เป็น $441\text{ m}\Omega$)
- การจัดวางระนาบไว้ตื้นติดกับชิ้นส่วนจึงเป็นปัจจัยชี้ขาดความสำเร็จของการออกแบบ PDN

---

### คำถามที่ 2: การวิเคราะห์การหักล้างของสนามแม่เหล็ก (Mutual Inductance Cancellation) จากการจัดวาง Via

ตัวเก็บประจุ 0603 ถูกออกแบบเชื่อมต่อด้วย Via 2 รูปแบบที่ระดับความลึกระนาบเท่ากัน ($h = 0.5\text{ mm}$, $r_{via} = 0.15\text{ mm}$):
- **แบบ A (Wide Separation):** Via ไฟและกราวด์ถูกวางแยกกันคนละด้าน โดยมีระยะห่างกึ่งกลาง $s_A = 2.4\text{ mm}$
- **แบบ B (Ultra-Close Side Placement):** Via ไฟและกราวด์ถูกวางชิดกันที่ขอบข้างของ Pad โดยมีระยะห่างกึ่งกลาง $s_B = 0.5\text{ mm}$

จงคำนวณ:
1. ค่าความเหนี่ยวนำของคู่ Via ($L_{via\_pair}$) ของแบบ A และแบบ B
2. เปอร์เซ็นต์การลดลงของความเหนี่ยวนำที่ได้รับจากการนำ Via มาวางชิดกัน
3. อธิบายพฤติกรรมของฟลักซ์แม่เหล็ก (Magnetic Field Distribution) และเหตุใดการจัดวางแบบ B จึงช่วยลดการแพร่กระจายของสัญญาณรบกวน EMI ข้ามไปยังร่องสัญญาณข้างเคียง?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณความเหนี่ยวนำคู่ Via ($L = \frac{\mu_0 \cdot h}{\pi} [\ln(s/r) + 0.25]$):**
- สัมประสิทธิ์ $\frac{\mu_0 \cdot h}{\pi} = (0.4\text{ nH/mm}) \times 0.5\text{ mm} = 0.20\text{ nH}$

- **แบบ A ($s_A = 2.4\text{ mm}, r = 0.15\text{ mm}$):**
  $$\frac{s_A}{r} = \frac{2.4}{0.15} = 16.0$$
  $$\ln(16.0) + 0.25 \approx 2.7726 + 0.25 = 3.0226$$
  $$L_{via\_pair, A} = 0.20\text{ nH} \times 3.0226 \approx 0.6045\text{ nH} = 604.5\text{ pH}$$

- **แบบ B ($s_B = 0.5\text{ mm}, r = 0.15\text{ mm}$):**
  $$\frac{s_B}{r} = \frac{0.5}{0.15} \approx 3.3333$$
  $$\ln(3.3333) + 0.25 \approx 1.2040 + 0.25 = 1.4540$$
  $$L_{via\_pair, B} = 0.20\text{ nH} \times 1.4540 \approx 0.2908\text{ nH} = 290.8\text{ pH}$$

**2. คำนวณเปอร์เซ็นต์การลดลงของความเหนี่ยวนำ:**
$$\% \text{Reduction} = \frac{0.6045 - 0.2908}{0.6045} \times 100\% = \frac{0.3137}{0.6045} \times 100\% \approx 51.9\%$$
*(ความเหนี่ยวนำลดลงไปมากกว่าครึ่งหนึ่ง!)*

**3. บทวิเคราะห์ทางฟิสิกส์แม่เหล็กและผลกระทบต่อ EMI:**
- **Ampère's Law & Field Cancellation:** กระแสใน Via ทั้งสองไหลในทิศทางตรงกันข้าม ($+I$ และ $-I$) กระแสแต่ละเส้นจะสร้างสนามแม่เหล็กวนรอบตัวถังในทิศทางตรงกันข้าม (ตามกฎมือขวา)
- เมื่อเลื่อน Via ทั้งสองเข้ามาใกล้กันที่ระยะ $s = 0.5\text{ mm}$ สนามแม่เหล็กจากกระแสขากลับจะซ้อนทับและหักล้างกับสนามแม่เหล็กจากกระแสขาไปในพื้นที่ภายนอกเกือบสมบูรณ์ (Dipole Field Decay $\propto 1/r^2$ แทนที่จะเป็น Monopole Field $\propto 1/r$)
- **ประโยชน์ด้าน EMI:** การกักเก็บสนามแม่เหล็กให้อยู่เฉพาะในช่องว่างแคบๆ ระหว่าง Via ทั้งสอง จะป้องกันไม่ให้เส้นแรงแม่เหล็กแผ่ออกไปตัดกับรอยต่อของสัญญาณความเร็วสูงข้างเคียง (ขจัด Inductive Crosstalk) และลดสัญญาณรบกวนการแผ่รังสีสนามแม่เหล็ก (Radiated Emissions) ของบอร์ดลงได้อย่างมหาศาล

---

### คำถามที่ 3: การประเมิน Swiss-Cheese Effect ต่อการเพิ่มขึ้นของค่า Plane Resistance และ DC IR Drop

บนระนาบทองแดง Power Plane หนา $1\text{ oz}$ ($t = 35\ \mu\text{m}$, สภาพต้านทานจำเพาะของทองแดง $\rho = 1.72 \times 10^{-8}\ \Omega\cdot\text{m}$) กระแสไฟตรง $I_{DC} = 40\text{ A}$ ไหลผ่านพื้นที่กว้าง $W = 20\text{ mm}$ ยาว $L = 30\text{ mm}$ ใต้ตัวถังชิป BGA

- **สภาวะปกติ (Solid Copper Plane):** ระนาบทองแดงทึบเต็มแผ่นไม่มีรูเจาะ
- **สภาวะ Swiss-Cheese Effect (Perforated Plane):** มีรูเจาะ BGA พิทช์ $1.0\text{ mm}$ เรียงเป็นตาราง โดยมีเส้นผ่านศูนย์กลาง Anti-pad $D_{anti} = 0.85\text{ mm}$ ทำให้สะพานทองแดงระหว่างรูเหลือความกว้างเพียง $W_{web} = 1.0\text{ mm} - 0.85\text{ mm} = 0.15\text{ mm}$ (พื้นที่ทองแดงนำกระแสจริงหายไป $85\%$ เหลือเพียง $15\%$) นอกจากนี้ เส้นทางเดินกระแสต้องคดเคี้ยวอ้อมรูเจาะ ทำให้ความยาวประสิทธิผลเพิ่มขึ้น $40\%$ ($L_{eff} = 1.4 \cdot L$)

จงคำนวณ:
1. ค่าความต้านทานกระแสไฟตรง ($R_{DC}$) และค่าแรงดันตกคร่อม ($\Delta V_{IR}$) ในสภาวะปกติ
2. ค่าความต้านทานกระแสไฟตรง ($R_{DC, swiss}$) และค่าแรงดันตกคร่อม ($\Delta V_{IR, swiss}$) ในสภาวะ Swiss-Cheese
3. หากรางไฟคอร์มีพิกัด $0.80\text{ V} \pm 3\%$ ($\Delta V_{total\_margin} = 24\text{ mV}$) สภาวะ Swiss-Cheese จะส่งผลอย่างไรต่อการทำงานของระบบ?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณสภาวะปกติ (Solid Plane):**
- พื้นที่หน้าตัดทองแดง:
  $$A_{cross, 1} = W \cdot t = (20 \times 10^{-3}\text{ m}) \times (35 \times 10^{-6}\text{ m}) = 7.0 \times 10^{-7}\text{ m}^2$$
- ความต้านทานกระแสไฟตรง:
  $$R_{DC, 1} = \rho \cdot \frac{L}{A_{cross, 1}} = (1.72 \times 10^{-8}\ \Omega\cdot\text{m}) \times \frac{30 \times 10^{-3}\text{ m}}{7.0 \times 10^{-7}\text{ m}^2} \approx 7.37 \times 10^{-4}\ \Omega = 0.737\text{ m}\Omega$$
- แรงดันตกคร่อม DC IR Drop:
  $$\Delta V_{IR, 1} = I_{DC} \cdot R_{DC, 1} = 40\text{ A} \times 0.737\text{ m}\Omega \approx 29.48\text{ mV}$$
  *(หมายเหตุ: หากคิด 2 ฝั่งไป-กลับ หรือกระจายกระแสจริงจะลดลงครึ่งหนึ่ง แต่ในที่นี้คิดก้อนระนาบเดี่ยว)*

**2. คำนวณสภาวะ Swiss-Cheese Effect:**
- พื้นที่หน้าตัดประสิทธิผลเหลือเพียง $15\%$ ของเดิม ($W_{eff} = 20\text{ mm} \times 0.15 = 3.0\text{ mm}$):
  $$A_{cross, 2} = (3.0 \times 10^{-3}\text{ m}) \times (35 \times 10^{-6}\text{ m}) = 1.05 \times 10^{-7}\text{ m}^2$$
- ความยาวประสิทธิผลเพิ่มขึ้น $40\%$ ($L_{eff} = 30\text{ mm} \times 1.4 = 42\text{ mm} = 0.042\text{ m}$):
- ความต้านทานประสิทธิผลใหม่:
  $$R_{DC, swiss} = (1.72 \times 10^{-8}) \times \frac{0.042\text{ m}}{1.05 \times 10^{-7}\text{ m}^2} \approx 6.88 \times 10^{-3}\ \Omega = 6.88\text{ m}\Omega$$
  *(ความต้านทานพุ่งสูงขึ้นกว่าเดิมถึง **$9.3$ เท่า!**)*
- แรงดันตกคร่อม DC IR Drop ใหม่:
  $$\Delta V_{IR, swiss} = I_{DC} \cdot R_{DC, swiss} = 40\text{ A} \times 6.88\text{ m}\Omega \approx 275.2\text{ mV}!$$

**3. บทวิเคราะห์ผลกระทบระดับระบบ:**
- งบประมาณความผันผวนของแรงดันทั้งหมดมีเพียง **$24\text{ mV}$** แต่แรงดันตกคร่อม DC จากปรากฏการณ์ Swiss-Cheese เพียงอย่างเดียวพุ่งสูงถึง **$275.2\text{ mV}$ (เกินงบประมาณไปกว่า 11 เท่า!)**
- แรงดันที่ไปถึงแกนประมวลผลของชิปจะเหลือเพียง $0.80\text{ V} - 0.275\text{ V} = 0.525\text{ V}$ ซึ่งไม่เพียงพอต่อการทำงานของทรานซิสเตอร์ ชิปจะดับสนิท (Brown-out Reset) ทันทีที่เริ่มจ่ายโหลด
- นอกจากนี้ ความร้อนสูญเสียบนคอคอดทองแดง ($P = I^2 R = 40^2 \times 0.00688 \approx 11.0\text{ W}$) จะก่อให้เกิดความร้อนสะสมเฉพาะจุด (Localized Hotspot) จนแผ่น PCB อาจไหม้พอง (Delamination) ได้ในระยะยาว
