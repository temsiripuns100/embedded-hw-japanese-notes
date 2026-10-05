# Lesson 071: PCB BGA Part 1 - BGA Pad Architecture: NSMD vs. SMD and Pad Cratering Mechanics

---

## 1. ทฤษฎีวิศวรรรมเชิงลึก (高度なエンジニアリング理論)

ในการออกแบบจุดบัดกรีสำหรับแพ็กเกจ Ball Grid Array (BGA) การเลือกโครงสร้างแลนด์แพด (Land Pad Architecture) ถือเป็นการตัดสินใจเชิงวิศวกรรมระดับรากฐานที่ส่งผลกระทบต่อทั้ง **ความน่าเชื่อถือเชิงกล (Mechanical Reliability)**, **ความเค้นจากความร้อน (Thermal Fatigue Life)**, และ **ความสามารถในการผลิต (SMT Manufacturability)**

โครงสร้างแผ่นรองรับบอลบัดกรีของ BGA แบ่งออกเป็น 2 สถาปัตยกรรมหลักตามนิยามของช่องเปิด Solder Mask:

```
+-------------------------------------------------------------------------+
|                  NSMD vs. SMD Cross-Sectional Physics                   |
|                                                                         |
|  [ NSMD: Non-Solder Mask Defined ]    [ SMD: Solder Mask Defined ]      |
|                                                                         |
|        Solder Ball Collapses                 Solder Ball Collapses      |
|            Around Flanks!                        Only on Flat Top!      |
|               ┌──────┐                              ┌──────┐            |
|          .────┤ Solder├────.                   .────┤Solder├────.       |
|         /     └──────┘      \                 /     └──────┘     \      |
|      ┌─┴───────────────────┴─┐              ┌────────────────────┐      |
|  Mask│      Copper Pad       │Mask      Mask│     Copper Pad     │Mask  |
|  ═══ │ (Cu > Mask Opening)   │ ═══      ════╪════════════════════╪════  |
|      └───────────────────────┘              │(Mask < Cu Opening) │      |
|      FR-4 Dielectric Substrate              └────────────────────┘      |
|                                             FR-4 Dielectric Substrate   |
+-------------------------------------------------------------------------+
```

### 1.1 การเปรียบเทียบเชิงลึก: NSMD (Copper Defined) เทียบกับ SMD (Mask Defined)

#### 1. Non-Solder Mask Defined (NSMD / Copper Defined Pad):
- **โครงสร้าง:** แผ่นทองแดง (Copper Pad) มีขนาดเล็กกว่าช่องเปิดของ Solder Mask โดยมีช่องว่างฉนวนล้อมรอบ (Clearance Ring $\approx 50 - 75\ \mu\text{m}$)
- **พฤติกรรมระหว่าง Reflow:** เมื่อตะกั่วหลอมเหลว ตะกั่วบัดกรีจะไหลเปียกกระจาย (Wetting) คลุมทั้ง **ผิวด้านบน** และ **ขอบด้านข้าง (Sidewalls)** ของแผ่นทองแดง
- **กลไกการกระจายความเค้น (Stress Distribution):** 
  - การที่ตะกั่วโอบรัดขอบทองแดงทำให้พื้นที่สัมผัสเชิงกล (Effective Mechanical Surface Area) เพิ่มขึ้น
  - ไม่มีจุดรวมความเค้น (No Sharp Stress Concentration Notch) ที่รอยต่อระหว่างหน้ากากกับเนื้อตะกั่ว
  - **ทนทานต่อความล้าจากความร้อน (Thermal Fatigue Resistance under Temperature Cycling) สูงกว่า SMD ถึง $30\% - 50\%$**
- **ความแม่นยำทางมิติ:** ขนาดของ Pad ถูกกำหนดด้วยกระบวนการกัดกรดทองแดง (Copper Etching Tolerance $\pm 12 - 25\ \mu\text{m}$) ซึ่งแม่นยำกว่ากระบวนการเปิดช่อง Solder Mask

#### 2. Solder Mask Defined (SMD / Mask Defined Pad):
- **โครงสร้าง:** แผ่นทองแดงมีขนาดใหญ่กว่าช่องเปิดของ Solder Mask โดยฟิล์ม Solder Mask จะยื่นเข้ามาทับขอบทองแดงโดยรอบ
- **พฤติกรรมระหว่าง Reflow:** ตะกั่วบัดกรีสามารถสัมผัสได้เฉพาะผิวด้านบนของทองแดงที่เปิดโล่งเท่านั้น ไม่สามารถไหลลงเกาะขอบด้านข้างได้
- **ความเค้นรวมศูนย์ (Stress Concentration Notch):**
  - รอยต่อที่ฟิล์ม Solder Mask ทับแผ่นทองแดงจะสร้างรอยหยักมุมแหลม (Sharp Micro-notch) ตามแนวขอบ
  - เมื่อแผ่นบอร์ดได้รับแรงดัดงอ (PCB Bending / Thermal Expansion Mismatch) ความเค้นเฉือนจะกระจุกตัวที่มุมนี้ ทำให้เม็ดบัดกรีแตกร้าว (Solder Joint Cracking) ได้ง่ายกว่า
- **ข้อได้เปรียบด้านการยึดเกาะทองแดง (Adhesion Anchor):**
  - แผ่นทองแดงมีพื้นที่กว้างกว่าและมีฟิล์ม Solder Mask ช่วยกดทับขอบไว้ ทำให้มี **แรงต้านทานการหลุดร่อนของแพด (Pad Shear / Peel Strength) สูงกว่า NSMD**
  - ช่วยลดความเสี่ยงของการเกิด **Pad Cratering (เนื้อเรซินใต้แพดฉีกขาด)** ภายใต้แรงกระแทกเชิงกลฉับพลัน (Mechanical Shock & Drop Test)

| พารามิเตอร์เชิงวิศวกรรม | NSMD (Non-Solder Mask Defined) | SMD (Solder Mask Defined) |
| :--- | :--- | :--- |
| **ขนาด Copper Pad เทียบกับ Mask** | Copper Pad < Mask Opening | Copper Pad > Mask Opening |
| **การเปียกของตะกั่ว (Solder Wetting)**| ทั้งผิวด้านบนและขอบด้านข้าง | เฉพาะผิวด้านบนเท่านั้น |
| **ความต้านทาน Thermal Cycling** | **ดีเยี่ยม (สูงกว่า SMD 30-50%)** | ปานกลาง (เกิดรอยร้าวที่คอ Mask ได้ง่าย) |
| **ความต้านทานแรงดึง/หลุดร่อน (Drop Test)**| เสี่ยงต่อ Pad Cratering หากดัดงอแรง | **ดีเยี่ยม (Mask ช่วยล็อกขอบทองแดง)** |
| **ความแม่นยำของขนาดรอยต่อ** | สูง (คุมด้วยกระบวนการ Etching) | ปานกลาง (คุมด้วย Photo-mask alignment) |
| **ระยะห่างระหว่าง Pad (Web Bridge)** | แคบลง (ต้องเผื่อช่องว่าง Clearance) | กว้างกว่า (เปิดทางให้เดิน Trace ได้ง่ายกว่า) |
| **การใช้งานที่แนะนำ** | **Signal Pins, พิทช์ละเอียด ($P \le 0.8\text{ mm}$)** | **Corner Ground Pins, พาวเวอร์พินรับแรงเค้น** |

### 1.2 กลไกความล้มเหลวแบบ Pad Cratering (Dielectric Fracturing Under BGA Pads)

ในยุคของโลหะบัดกรีไร้สารตะกั่ว (Lead-Free Soldering: เช่น SAC305, SAC405) โลหะบัดกรีมีความแข็งเกร็ง (Modulus of Elasticity: $E \approx 50\text{ GPa}$) สูงกว่าตะกั่วโบราณแบบ $\text{Sn63Pb37}$ ($E \approx 30\text{ GPa}$) เกือบสองเท่า เมื่อบอร์ดได้รับความเค้นดัดงอ (In-circuit Test Fixture Clamping, การขันสกรูยึดฮีตซิงก์, หรือการตกกระแทก Drop Impact) เม็ดบัดกรีจะไม่ยอมยุบตัวดูดซับแรง

ความเค้นดึง (Tensile Stress) และความเค้นเฉือน (Shear Stress) จะถูกส่งผ่านแผ่นทองแดงลงสู่เนื้อเรซินใยแก้ว FR-4 ใต้ Pad โดยตรง ก่อให้เกิดรอยแตกร้าวในเนื้อไดอิเล็กทริกที่เรียกว่า **Pad Cratering (รอยแตกรูปถ้วยใต้แพด)**:

```
[Pad Cratering Failure Mechanism]
             BGA Solder Joint (Stiff SAC305)
                   │
                   ▼ (Mechanical Bending Tensile Force)
         ┌───────────────────┐
         │    Copper Pad     │
   ══════╪═══════════════════╪══════ Solder Mask
         │                   │
   - - - ┴ - - - - - - - - - ┴ - - - Crack initiates at pad edge!
   \                               /
    \    DIELECTRIC CRATER CRACK  /  (Resin fracture beneath copper)
     ' - - - - - - - - - - - - - '
         Woven Glass Bundle (FR-4 Substrate)
```

พลังงานการเกิดรอยแตก (Fracture Toughness: $G_c$) ของเรซิน FR-4 มีค่าต่ำกว่าแรงยึดเหนี่ยวของพันธะทองแดง-อินเตอร์เมทัลลิก (IMC Layer) รอยร้าวจึงเริ่มต้นที่ **ขอบด้านนอกของ Copper Pad** และวิ่งโค้งลึกลงไปในเนื้อเรซินรอบเส้นใยแก้ว ก่อให้เกิดวงจรขาดเป็นช่วงๆ (Intermittent Open Circuit) ซึ่งตรวจจับได้ยากมากในการทดสอบทางไฟฟ้าแบบคงที่

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)

**เหตุการณ์:** บอร์ดควบคุมชุดเกียร์ยานยนต์ (Automotive Transmission Control Unit: TCU) ติดตั้งชิปไมโครคอนโทรลเลอร์ BGA 416 พิน (พิทช์ $0.8\text{ mm}$, ขนาดตัวถัง $27\text{ mm} \times 27\text{ mm}$) บนบอร์ด 8-Layer High-Tg FR-4 

**อาการล้มเหลว:**
1. บอร์ดผ่านการทดสอบ EOL Test ที่โรงงาน SMT ได้สมบูรณ์แบบ $100\%$
2. แต่เมื่อส่งชิ้นส่วนไปประกอบเข้ากับชุดโครงอะลูมิเนียมเกียร์ และผ่านการทดสอบการสั่นสะเทือนตามมาตรฐานยานยนต์ (Random Vibration Test ตาม ISO 16750-3: $10 - 2,000\text{ Hz}$, $30\text{ g}$ RMS) บอร์ดเกิดอาการ "Communication Loss / Reset Loop" ทันทีหลังการทดสอบไปได้ 15 นาที
3. เมื่อตรวจสอบวงจรเปิด-ปิด พบว่าสัญญาณ CAN-FD Bus ขาดหายไป เมื่อนำบอร์ดไปผ่าหน้าตัดตรวจสอบด้วยกล้องจุลทรรศน์อิเล็กตรอน (Cross-section SEM Analysis) พบความล้มเหลวร้ายแรง:
   - บอลบัดกรีที่มุมทั้งสี่ของ BGA (Corner Balls: พิน A1, A26, AF1, AF26) เกิดอาการ **Pad Cratering หลุดร่อนยกตัวขึ้นทั้งแผ่นทองแดง**
   - เนื้อเรซินใต้แพดทองแดงฉีกขาดออกจากใยแก้วชั้นแรก ก่อให้เกิดรอยแยกกว้าง $18\ \mu\text{m}$

```
[Cross-Section SEM Finding: Corner Pad Cratering]
         Corner BGA Ball
               │
               ▼
         [ Copper Pad ]
        /              \  <--- Severe Resin Delamination Crack!
    ───'                '──────────────────
       Woven Glass Fabric Substrate
       (Copper pad completely ripped out from FR-4 core!)
```

**Root Cause Analysis (RCA):**
1. **การกำหนดประเภท Pad ไม่เหมาะสมกับแรงเค้น:** วิศวกรออกแบบ Pad ทุกพินบน BGA เป็นแบบ **NSMD ทั้งหมด** (ขนาด Copper Pad $0.40\text{ mm}$, Mask Opening $0.50\text{ mm}$) ที่พินบริเวณมุมทั้งสี่ของ BGA (Corner Balls) ซึ่งเป็นจุดที่รับโมเมนต์ดัดงอสูงสุด (Maximum Bending Moment & CTE Shear Strain) พื้นที่ยึดเกาะทองแดงของ NSMD ไม่เพียงพอที่จะต้านทานแรงดึงในแนวแกน $z$
2. **การขาด Dummy Balls รองรับแรงเค้น:** ขอบมุม BGA ไม่มีพิน Mechanical Dummy Balls เพื่อช่วยกระจายแรงเค้น แรงสั่นสะเทือนทั้งหมดจึงถ่ายทอดลงสู่พินสัญญาณที่อยู่ตรงมุมโดยตรง
3. **การออกแบบทางเดินลายทองแดงคอคอด:** ลายสัญญาณที่ลากออกจาก Pad มุมบอร์ดถูกลากออกด้วยความกว้างเพียง $0.10\text{ mm}$ โดยไม่มีการทำ Teardrop เมื่อ Pad ขยับตัวเพียงเล็กน้อย ลายทองแดงจึงขาดสะบั้นทันที

---

### Step-by-Step Engineering Checklist: กลยุทธ์การผสมผสานไฮบริดแพด (Hybrid Pad Strategy)

#### ขั้นตอนที่ 1: การใช้กลยุทธ์ไฮบริด (Hybrid NSMD / SMD Architecture)
วิศวกรอาวุโสจะต้องไม่เลือกใช้ NSMD หรือ SMD แบบเหมารวมทั้งชิ้นส่วน แต่ให้ใช้ **กลยุทธ์ลูกผสม (Hybrid Pad Strategy)**:

```
+-------------------------------------------------------------+
|  Hybrid BGA Pad Strategy Architecture:                      |
|                                                             |
|   (SMD) (SMD)  (NSMD) (NSMD) ... (NSMD)  (SMD) (SMD)        |
|   (SMD) (SMD)  (NSMD) (NSMD) ... (NSMD)  (SMD) (SMD)  Row B |
|   (NSMD)(NSMD) (NSMD) (NSMD) ... (NSMD)  (NSMD)(NSMD) Row C |
|     :     :      :      :          :       :     :          |
|   (SMD) (SMD)  (NSMD) (NSMD) ... (NSMD)  (SMD) (SMD)        |
|                                                             |
|   [ Corner 2x2 or 3x3 Perimeter Balls ]: SMD Configuration  |
|     ---> Extreme Anchor Strength! Zero Pad Cratering!       |
|                                                             |
|   [ Inner Matrix Signal Balls ]:         NSMD Configuration |
|     ---> Maximum Routing Channel & Thermal Fatigue Life!    |
+-------------------------------------------------------------+
```

- **พินที่มุมทั้งสี่ (Outer Corner 2x2 หรือ 3x3 Array):** กำหนดให้เป็น **SMD Pad** เสมอ เพราะ Solder Mask ที่กดทับขอบทองแดงจะทำหน้าที่เสมือนพุกยึด ช่วยเพิ่มแรงต้านทานการหลุดร่อน (Anchor Strength) ป้องกันการเกิด Pad Cratering ได้อย่างเด็ดขาด
- **พินสัญญาณภายใน (Inner Signal Balls):** กำหนดให้เป็น **NSMD Pad** เพื่อให้ได้ระยะห่างของช่องเดินสายสัญญาณ (Escape Routing Channel) กว้างที่สุด และลดความเค้นสะสมจาก Thermal Cycling

#### ขั้นตอนที่ 2: การคำนวณขนาด Pad และ Mask Opening สำหรับพิทช์ต่างๆ
อ้างอิงมาตรฐาน **IPC-7351B** และคำแนะนำจากผู้ผลิตชิป BGA:

| BGA Ball Pitch ($P$) | ขนาดเส้นผ่านศูนย์กลางบอล ($D_{ball}$) | ขนาด Copper Pad (NSMD) | ขนาด Mask Opening (NSMD) | ขนาด Copper Pad (SMD) | ขนาด Mask Opening (SMD) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1.00 mm** | 0.50 mm (20 mils) | **0.40 mm (16 mils)** | 0.50 mm (20 mils) | 0.55 mm (22 mils) | **0.45 mm (18 mils)** |
| **0.80 mm** | 0.40 mm (16 mils) | **0.35 mm (14 mils)** | 0.45 mm (18 mils) | 0.45 mm (18 mils) | **0.35 mm (14 mils)** |
| **0.65 mm** | 0.35 mm (14 mils) | **0.30 mm (12 mils)** | 0.40 mm (16 mils) | 0.40 mm (16 mils) | **0.30 mm (12 mils)** |
| **0.50 mm (Fine)** | 0.30 mm (12 mils) | **0.25 mm (10 mils)** | 0.35 mm (14 mils) | 0.35 mm (14 mils) | **0.25 mm (10 mils)** |
| **0.40 mm (Ultra)**| 0.25 mm (10 mils) | **0.20 mm (8 mils)** | 0.28 mm (11 mils) | 0.28 mm (11 mils) | **0.20 mm (8 mils)** |

- **กฎความกว้างแนวกันหน้ากาก (Solder Mask Web / Dam):**
  สำหรับ NSMD ต้องตรวจสอบว่ามีระยะห่างของเนื้อ Solder Mask ระหว่างช่องเปิดที่อยู่ติดกัน:
  $$\text{Mask Dam Width} = \text{Pitch} - D_{mask\_opening} \ge 75\ \mu\text{m} \ (3\text{ mils})$$
  หาก $\text{Mask Dam} < 75\ \mu\text{m}$ ฟิล์มหน้ากากจะฉีกขาดหรือหลุดล่อนระหว่างการล้างบอร์ด ทำให้เกิดสะพานเชื่อมบัดกรี (Solder Bridging) ลัดวงจรทันที

#### ขั้นตอนที่ 3: การเพิ่ม Teardrop และการเสริมความแข็งแรงเชิงกล
- **ใส่ Teardrop ทุก Pad:** ที่จุดเชื่อมต่อระหว่าง BGA Pad กับลายเส้นทองแดง Fanout Trace ต้องใส่ทรงหยดน้ำ (Teardrop Fillet) เสมอ เพื่อลดความเค้นรวมศูนย์และป้องกันลายเส้นขาดที่คอ Pad เมื่อเกิดการสั่นสะเทือน
- **เลือกใช้วัสดุ PCB ชนิด Low-Modulus / High-Toughness Resin:**
  สำหรับผลิตภัณฑ์ยานยนต์ ให้ระบุสเปกวัสดุ PCB ลามิเนตที่มีค่า **Fracture Toughness สูง ($G_c > 200\text{ J/m}^2$)** และมีค่าการขยายตัวเนื่องจากความร้อนต่ำ ($\alpha_z < 35\text{ ppm/}^{\circ}\text{C}$) ตามมาตรฐาน IPC-4101/126

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คันจิ (Kanji) | คานะ (Kana) | คำอ่าน (Romaji) | ภาษาอังกฤษ / คำแปลภาษาไทย |
| :--- | :--- | :--- | :--- |
| **パッド設計仕様** | ぱっどせっけいしよう | Paddo Sekkei Shiyō | Pad Design Specification |
| **銅箔定義ランド** | どうはくていぎらんど | Dōhaku Teigi Rando | Non-Solder Mask Defined (NSMD) |
| **レジスト定義ランド** | れじすとていぎらんど | Rejisuto Teigi Rando | Solder Mask Defined (SMD) |
| **パッド剥離 / クレーター**| ぱっどはくり / くれーたー | Paddo Hakuri / Kurētā | Pad Peeling / Pad Cratering |
| **レジストダム幅** | れじすとだむはば | Rejisuto Damu-haba | Solder Mask Dam / Web Width |
| **熱疲労寿命** | ねつひろうじゅみょう | Netsu Hirō Jumyō | Thermal Fatigue Life |
| **応力集中** | おうりょくしゅうちゅう | Ōryoku Shūchū | Stress Concentration |
| **四隅補強ランド** | よすみほきょうらんど | Yosumi Hokyō Rando | Corner Reinforced / Dummy Pads |
| **ティアドロップ** | てぃあどろっぷ | Tiadoroppu | Teardrop Fillet Connection |
| **落下衝撃試験** | らっかしょうげきしけん | Rakka Shōgeki Shiken | Mechanical Shock / Drop Test |
| **はんだブリッジ** | はんだぶりっじ | Handa Burijji | Solder Bridging (การลัดวงจรของตะกั่ว) |
| **金属間化合物** | きんぞくかんかごうぶつ | Kinzoku-kan Kagōbutsu | Intermetallic Compound (IMC Layer) |

---

### 3.2 บันทึกการตรวจแบบของ Senior Engineer (検図指摘事項 - Kenzu Comments)

#### คอมเมนต์ที่ 1: ตรวจพบการใช้ NSMD ที่มุม BGA เสี่ยงต่อ Pad Cratering จากแรงสั่นสะเทือน
> **検図指摘 (Kenzu Feedback 1):**  
> 「パワートレイン制御ECU基板上のMCU（BGA-416ピン、0.8mmピッチ）ランド設計を検図しました。現在、全ピンに対して一律でNSMD（銅箔径$\phi 0.35\text{mm}$、レジスト開口$\phi 0.45\text{mm}$）が適用されています。車載環境におけるランダム振動試験（ISO 16750-3）およびヒートシンク締結荷重を考慮した場合、熱応力および曲げモーメントが最大となるパッケージ四隅のコーナーループ部（A1, A26, AF1, AF26ピン周辺の各2x2エリア）において、基板樹脂層の破壊（パッドクレーター現象：Pad Cratering）を引き起こすリスクが極めて高いです。四隅の角部ピン各4箇所（計16ピン）について、レジストが銅箔エッジを覆いアンカー効果を持つ『SMD仕様（銅箔径$\phi 0.45\text{mm}$、レジスト開口$\phi 0.35\text{mm}$）』へ変更してください。また、引き出し配線との接続部には必ずティアドロップを追加して応力緩和を図ってください。」  
> *(คำแปล: ตรวจสอบแบบ Pad ใต้ MCU (BGA-416 พิน, พิทช์ 0.8 mm) บนบอร์ดควบคุมระบบส่งกำลัง พบว่ากำหนดเป็น NSMD ทั้งหมด (Copper 0.35 mm, Mask 0.45 mm) เมื่อพิจารณาการสั่นสะเทือนของยานยนต์ตาม ISO 16750-3 ร่วมกับแรงกดขันยึดฮีตซิงก์ ความเค้นดัดงอสูงสุดจะตกที่มุมทั้งสี่ของ BGA (โซน 2x2 รอบพิน A1, A26, AF1, AF26) ซึ่งเสี่ยงสูงมากที่จะเกิดการฉีกขาดของเนื้อเรซินใต้แพด (Pad Cratering) ขอให้ปรับพินที่มุมทั้งสี่รวม 16 พินให้เป็นแบบ SMD (Copper 0.45 mm, Mask 0.35 mm) เพื่อให้หน้ากากช่วยล็อกขอบทองแดง และต้องเพิ่ม Teardrop ที่จุดเชื่อมต่อลายวงจรทุกจุดเพื่อผ่อนคลายความเค้น)*

#### คอมเมนต์ที่ 2: ความกว้างแนวกันหน้ากาก (Solder Mask Dam) แคบเกินพิกัด เสี่ยงต่อ Solder Bridging
> **検図指摘 (Kenzu Feedback 2):**  
> 「0.5mmピッチFPGA（BGA-484）のNSMDランド開口寸法について指摘します。設計データ上、銅箔ランド径$\phi 0.25\text{mm}$に対してレジスト開口径が$\phi 0.38\text{mm}$に設定されています。この場合、隣接する開口間のレジストダム残存幅（Mask Dam Width）が$0.50\text{mm} - 0.38\text{mm} = 0.12\text{mm}$（実効クリアランスは製造公差$\pm 25\mu\text{m}$考慮で$70\mu\text{m}$未満）となり、基板製造メーカーの最小現像限界（$75\mu\text{m}$）を下回ります。量産時にソルダーレジストの剥離や欠けが発生し、リフロー工程で隣接ボール間のはんだブリッジ（短絡不良）を大量誘発します。レジスト開口径を$\phi 0.33\text{mm}$に修正し、レジストダム幅を最低$0.17\text{mm}$（実効公差後で$100\mu\text{m}$以上）確保できるようガーバーデータを改訂してください。」  
> *(คำแปล: ขอคอมเมนต์ขนาดช่องเปิด NSMD ของ FPGA พิทช์ 0.5 mm (BGA-484) ข้อมูลระบุ Copper Pad 0.25 mm และ Mask Opening 0.38 mm ทำให้แนวกันหน้ากาก Solder Mask Dam ระหว่าง Pad เหลือเพียง 0.12 mm และเมื่อคิดความเผื่อในการผลิต ±25 µm จะเหลือพื้นที่จริงต่ำกว่า 70 µm ซึ่งต่ำกว่าขีดจำกัดของโรงงานผลิตแผ่นวงจร (75 µm) ในการผลิตจริงจะเกิดฟิล์มหน้ากากหลุดล่อน นำไปสู่สะพานบัดกรีลัดวงจรระหว่างลูกบอล BGA ได้ ขอให้ปรับลดขนาดช่องเปิด Solder Mask เหลือ 0.33 mm เพื่อรักษาแนว Mask Dam ให้กว้างอย่างน้อย 0.17 mm เพื่อป้องกันการลัดวงจรอย่างเด็ดขาด)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณพื้นที่หน้าตัดและแรงดึงยึดเกาะเชิงกล (Shear Strength) ระหว่าง NSMD และ SMD

วิศวกรกำลังประเมินความแข็งแรงของจุดเชื่อมต่อบอลบัดกรี SAC305 บน BGA พิทช์ $0.8\text{ mm}$ (เส้นผ่านศูนย์กลางบอล $D_{ball} = 0.40\text{ mm}$) 

เปรียบเทียบ 2 ทางเลือก:
- **ทางเลือกที่ 1 (NSMD Pad):** แผ่นทองแดงหนา $t_{Cu} = 35\ \mu\text{m}$ ($1\text{ oz}$) ทรงกลมเส้นผ่านศูนย์กลาง $d_1 = 0.35\text{ mm}$ ช่องเปิด Solder Mask กว้าง $0.45\text{ mm}$ ทำให้ตะกั่วเปียกคลุมทั้งผิวด้านบนและขอบด้านข้างทรงกระบอกรอบตัวถัง
- **ทางเลือกที่ 2 (SMD Pad):** แผ่นทองแดงเส้นผ่านศูนย์กลาง $0.45\text{ mm}$ แต่ช่องเปิด Solder Mask มีเส้นผ่านศูนย์กลาง $d_2 = 0.35\text{ mm}$ ตะกั่วเปียกเฉพาะผิวเรียบด้านบนที่เป็นวงกลมขนาด $d_2$ เท่านั้น

กำหนดให้ค่าความต้านทานแรงเฉือนของชั้นสารประกอบเชิงโลหะ (Intermetallic Compound - IMC Shear Strength) ของตะกั่วกับทองแดงมีค่าเฉลี่ย $\tau_{IMC} = 45\text{ MPa} = 45\text{ N/mm}^2$

จงคำนวณ:
1. พื้นที่หน้าตัดสัมผัสจริงของเนื้อตะกั่วกับทองแดง ($A_{contact}$) ของทั้งสองทางเลือก
2. แรงเฉือนสูงสุดทางทฤษฎี ($F_{shear} = \tau_{IMC} \cdot A_{contact}$) ที่จุดเชื่อมต่อของแต่ละทางเลือกสามารถรับได้ก่อนจะขาด
3. เปอร์เซ็นต์ความแข็งแรงที่ NSMD สูงกว่า SMD อันเกิดจากการโอบรัดขอบด้านข้าง?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณพื้นที่หน้าตัดสัมผัสจริง ($A_{contact}$):**
- **ทางเลือกที่ 2 (SMD Pad):**
  ตะกั่วเกาะเฉพาะพื้นที่วงกลมด้านบนเส้นผ่านศูนย์กลาง $d_2 = 0.35\text{ mm}$:
  $$A_{contact, SMD} = \frac{\pi \cdot d_2^2}{4} = \frac{\pi \cdot (0.35\text{ mm})^2}{4} \approx \frac{\pi \times 0.1225}{4} \approx 0.09621\text{ mm}^2$$

- **ทางเลือกที่ 1 (NSMD Pad):**
  ตะกั่วเกาะทั้งพื้นที่วงกลมด้านบน ($A_{top}$) และพื้นที่ผิวด้านข้างทรงกระบอก ($A_{side}$):
  $$A_{top} = \frac{\pi \cdot d_1^2}{4} = \frac{\pi \cdot (0.35\text{ mm})^2}{4} \approx 0.09621\text{ mm}^2$$
  พื้นที่ผิวด้านข้างทรงกระบอก (ความสูง $t_{Cu} = 35\ \mu\text{m} = 0.035\text{ mm}$):
  $$A_{side} = \pi \cdot d_1 \cdot t_{Cu} = \pi \times (0.35\text{ mm}) \times (0.035\text{ mm}) \approx 0.03848\text{ mm}^2$$
  พื้นที่สัมผัสรวมของ NSMD:
  $$A_{contact, NSMD} = A_{top} + A_{side} = 0.09621 + 0.03848 = 0.13469\text{ mm}^2$$

**2. คำนวณแรงเฉือนสูงสุดที่รับได้ ($F_{shear}$):**
- **สำหรับ SMD:**
  $$F_{shear, SMD} = \tau_{IMC} \cdot A_{contact, SMD} = (45\text{ N/mm}^2) \times 0.09621\text{ mm}^2 \approx 4.33\text{ N}$$
- **สำหรับ NSMD:**
  $$F_{shear, NSMD} = \tau_{IMC} \cdot A_{contact, NSMD} = (45\text{ N/mm}^2) \times 0.13469\text{ mm}^2 \approx 6.06\text{ N}$$

**3. เปรียบเทียบความแข็งแรงเชิงกล:**
$$\% \text{Improvement} = \frac{6.06\text{ N} - 4.33\text{ N}}{4.33\text{ N}} \times 100\% = \frac{1.73}{4.33} \times 100\% \approx 40.0\%$$

**บทวิเคราะห์ของ Senior Engineer:**
- โครงสร้างแบบ NSMD ให้ความแข็งแรงต่อแรงเฉือนของเนื้อรอยต่อบัดกรี **สูงกว่า SMD ถึง $40\%$** เนื่องจากความหนาของขอบทองแดง ($35\ \mu\text{m}$) ทำหน้าที่เป็นสมอยึดรอบทิศทาง
- นี่คือเหตุผลทางคณิตศาสตร์ว่าทำไม NSMD จึงมีอายุการใช้งานต่อการทดสอบ Thermal Cycling สูงกว่า SMD อย่างมีนัยสำคัญ

---

### คำถามที่ 2: การคำนวณความเค้นเฉือนจากสัมประสิทธิ์การขยายตัวเนื่องจากความร้อน ($\Delta\text{CTE}$) ตามสมการ Coffin-Manson

ชิป BGA ขนาด $30\text{ mm} \times 30\text{ mm}$ ตัวถังเซรามิก (Ceramic BGA) มีค่าสัมประสิทธิ์การขยายตัวเนื่องจากความร้อน $\alpha_{pkg} = 6.5\text{ ppm/}^{\circ}\text{C}$ ติดตั้งบนบอร์ด FR-4 ที่มี $\alpha_{pcb} = 16.5\text{ ppm/}^{\circ}\text{C}$ 

ระบบผ่านการทดสอบรอบอุณหภูมิยานยนต์ตั้งแต่ $T_{min} = -40^{\circ}\text{C}$ ถึง $T_{max} = +125^{\circ}\text{C}$ ($\Delta T = 165^{\circ}\text{C}$) 
- ความสูงของบอลบัดกรีหลังประกอบ (Solder Standoff Height): $h = 0.30\text{ mm} = 300\ \mu\text{m}$
- ระยะห่างจากจุดกึ่งกลางชิป (Neutral Point) ไปยังบอลที่มุมนอกสุด (Distance to Neutral Point: DNP) คือ:
  $$DNP = \sqrt{\left(\frac{30}{2}\right)^2 + \left(\frac{30}{2}\right)^2} = \sqrt{15^2 + 15^2} = \sqrt{450} \approx 21.21\text{ mm}$$

จงคำนวณ:
1. การเคลื่อนที่สัมพัทธ์ในแนวระนาบ ($\Delta L$) ระหว่างตัวถังชิปกับแผ่นบอร์ดที่ตำแหน่งบอลมุมนอกสุด
2. ความเครียดเฉือนเฉลี่ย (Shear Strain: $\gamma = \frac{\Delta L}{h}$) ที่กระทำต่อเม็ดบัดกรี
3. หากแบบจำลองความล้าของ Coffin-Manson ระบุว่าจำนวนรอบการทดสอบก่อนเกิดรอยร้าว ($N_f$) แปรผกผันกับกำลังสองของความเครียด ($N_f \propto \gamma^{-2}$) จงคำนวณว่า หากผู้ออกแบบใช้ Pad แบบ SMD ซึ่งทำให้ Standoff Height ยุบตัวลงเหลือ $h_{SMD} = 0.22\text{ mm}$ อายุการใช้งานจะลดลงเหลือกี่เปอร์เซ็นต์ของเดิม?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณการเคลื่อนที่สัมพัทธ์ที่จุดมุมนอกสุด ($\Delta L$):**
ความต่างของอัตราการขยายตัว:
$$\Delta\alpha = \alpha_{pcb} - \alpha_{pkg} = 16.5 - 6.5 = 10.0\text{ ppm/}^{\circ}\text{C} = 10.0 \times 10^{-6}\text{ /}^{\circ}\text{C}$$
การเคลื่อนที่สัมพัทธ์:
$$\Delta L = DNP \cdot \Delta\alpha \cdot \Delta T = (21.21\text{ mm}) \cdot (10.0 \times 10^{-6}) \cdot 165$$
$$\Delta L = 21.21 \times 0.00165 \approx 0.0350\text{ mm} = 35.0\ \mu\text{m}$$

**2. คำนวณความเครียดเฉือน ($\gamma$ ที่ $h = 0.30\text{ mm} = 300\ \mu\text{m}$):**
$$\gamma_1 = \frac{\Delta L}{h} = \frac{35.0\ \mu\text{m}}{300\ \mu\text{m}} \approx 0.1167 = 11.67\%$$

**3. คำนวณความเครียดเฉือนเมื่อใช้ SMD ($h_{SMD} = 0.22\text{ mm} = 220\ \mu\text{m}$):**
เนื่องจากใน SMD ตะกั่วไม่เกาะขอบด้านข้าง ตะกั่วจะยุบตัวแบนลง ทำให้ความสูง Standoff ลดลง:
$$\gamma_2 = \frac{\Delta L}{h_{SMD}} = \frac{35.0\ \mu\text{m}}{220\ \mu\text{m}} \approx 0.1591 = 15.91\%$$

**4. คำนวณการลดลงของอายุการใช้งานตามกฎ Coffin-Manson ($N_f \propto \gamma^{-2}$):**
$$\frac{N_{f, 2}}{N_{f, 1}} = \left( \frac{\gamma_1}{\gamma_2} \right)^2 = \left( \frac{0.1167}{0.1591} \right)^2 = (0.7335)^2 \approx 0.538 = 53.8\%$$

**บทสรุปของ Senior Engineer:**
- การที่ Standoff Height ยุบตัวลงจาก $300\ \mu\text{m}$ เหลือ $220\ \mu\text{m}$ ทำให้ความเครียดเฉือนพุ่งสูงขึ้น ส่งผลให้อายุการใช้งานก่อนเกิดรอยร้าวหลุดร่อน **หดสั้นลงเหลือเพียง $53.8\%$ (อายุการใช้งานหายไปเกือบครึ่งหนึ่ง!)**
- นี่คือเหตุผลทางกลศาสตร์ว่าทำไมพินสัญญาณทั่วไปจึงควรใช้ NSMD เพื่อรักษาความสูง Standoff ให้สูงที่สุด ช่วยดูดซับแรงเฉือนจากความต่างของ CTE ได้ดีกว่า

---

### คำถามที่ 3: การประเมินความสามารถในการผลิต DFM และการตรวจสอบความกว้าง Solder Mask Dam

วิศวกรเลย์เอาต์กำลังออกแบบบอร์ดสำหรับชิป BGA พิทช์ละเอียดพิเศษ $P = 0.40\text{ mm}$ (เส้นผ่านศูนย์กลางบอล $D_{ball} = 0.25\text{ mm}$) 

วิศวกรเลือกใช้แพดแบบ NSMD โดยกำหนดขนาด Copper Pad เส้นผ่านศูนย์กลาง $d_{Cu} = 0.20\text{ mm}$ และต้องการเปิดช่อง Solder Mask Clearance กว้างฝั่งละ $c = 0.05\text{ mm}$ ($50\ \mu\text{m}$) รอบทิศทาง 

กำหนดขีดจำกัดความสามารถของโรงงานผลิตแผ่นวงจรพิมพ์ (PCB Fabrication Design Rules):
- ค่าพิกัดความเผื่อความคลาดเคลื่อนในการวางฟิล์มหน้ากาก (Solder Mask Registration Tolerance): $\pm 25\ \mu\text{m}$
- ความกว้างของแนวกันหน้ากากขั้นต่ำสุดที่สามารถล้างและอบแข็งได้โดยไม่หลุดร่อน (Minimum Resolvable Solder Mask Dam): $W_{dam, min} = 65\ \mu\text{m}$

จงคำนวณ:
1. เส้นผ่านศูนย์กลางของช่องเปิด Solder Mask ($D_{mask}$) ตามที่วิศวกรกำหนด
2. ความกว้างของแนวกันหน้ากาก (Mask Dam Width: $W_{dam, nominal}$) ที่สภาวะสมบูรณ์แบบ
3. ความกว้างของแนวกันหน้ากากในสภาวะแย่ที่สุด (Worst-case Mask Dam) เมื่อฟิล์มเลื่อนตัวเต็มพิกัดความเผื่อ ($\pm 25\ \mu\text{m}$) และตรวจสอบว่าโรงงานจะสามารถผลิตได้โดยไม่เกิดข้อบกพร่อง Solder Bridging หรือไม่?

#### เฉลยและบทวิเคราะห์เชิงลึก:

**1. คำนวณเส้นผ่านศูนย์กลางช่องเปิด Solder Mask ($D_{mask}$):**
$$D_{mask} = d_{Cu} + 2 \cdot c = 0.20\text{ mm} + 2(0.05\text{ mm}) = 0.30\text{ mm} = 300\ \mu\text{m}$$

**2. คำนวณความกว้างแนวกันหน้ากากที่สภาวะ Nominal ($W_{dam, nominal}$):**
ระยะห่างระหว่างศูนย์กลางพินคือ $P = 0.40\text{ mm} = 400\ \mu\text{m}$:
$$W_{dam, nominal} = P - D_{mask} = 0.40\text{ mm} - 0.30\text{ mm} = 0.10\text{ mm} = 100\ \mu\text{m}$$

**3. คำนวณสภาวะแย่ที่สุด (Worst-Case Analysis):**
เมื่อพิจารณาความคลาดเคลื่อนของการจัดวางหน้ากาก (Misregistration Tolerance $\pm 25\ \mu\text{m}$):
- หากฟิล์มเลื่อนไปทางขวา $25\ \mu\text{m}$ ช่องเปิดของสองแพดที่อยู่ติดกันจะเคลื่อนที่เข้าหากัน:
  $$W_{dam, worst} = W_{dam, nominal} - \text{Tolerance} = 100\ \mu\text{m} - 25\ \mu\text{m} = 75\ \mu\text{m}$$
  *(และในกระบวนการกัดกรด Undercut หรือการบวมตัว อาจลดลงเหลือต่ำกว่า $50\ \mu\text{m}$)*
- หากเปรียบเทียบกับขีดจำกัดโรงงาน:
  - แม้ว่า $75\ \mu\text{m}$ จะดูเหมือนสูงกว่า $65\ \mu\text{m}$ เล็กน้อย แต่มี Margin เหลือเพียง $10\ \mu\text{m}$ เท่านั้น
  - ในความเป็นจริง สำหรับ BGA พิทช์ $0.40\text{ mm}$ การเปิด Clearance ฝั่งละ $50\ \mu\text{m}$ กว้างเกินไปอย่างยิ่ง เสี่ยงต่อการที่ฟิล์ม Mask Dam ขาดสะบั้นกลายเป็นช่องเปิดเชื่อมกัน (Mask Breakage) ทำให้ตะกั่วของสองลูกบอลไหลรวมกันเป็น **Solder Bridge (วงจรลัด)**

**บทสรุปและแนวทางแก้ไขของ Senior Engineer:**
- สำหรับ BGA พิทช์ละเอียดระดับ $0.40\text{ mm}$ **ห้ามใช้ Clearance กว้าง $50\ \mu\text{m}$ เด็ดขาด**
- ต้องลด Clearance ลงเหลือเพียง **$25 - 30\ \mu\text{m}$** (ทำให้ $D_{mask} \approx 0.25 - 0.26\text{ mm}$) ซึ่งจะเพิ่ม $W_{dam, nominal}$ เป็น **$140 - 150\ \mu\text{m}$**
- หรือเปลี่ยนไปใช้กระบวนการ **SMD Pad** สำหรับพิทช์ $0.40\text{ mm}$ (Copper Pad $0.26\text{ mm}$, Mask Opening $0.20\text{ mm}$) ซึ่งจะทำให้แนวกันหน้ากากมีความกว้างเหลือเฟือถึง **$200\ \mu\text{m}$** ขจัดความเสี่ยงจากการลัดวงจรได้อย่างสิ้นเชิง
