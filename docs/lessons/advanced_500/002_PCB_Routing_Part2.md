# Lesson 002: PCB Routing Part 2 - Differential Pair Routing & Signal Integrity
*(プリント基板の差動配線設計 - 差動インピーダンスとスキュー管理)*

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

คู่สัญญาณดิฟเฟอเรนเชียล (Differential Pair) เป็นมาตรฐานหลักของโปรโตคอลความเร็วสูงในปัจจุบัน เช่น PCIe Gen 4/5, USB 3.2/4, Ethernet 10G/25G (KR/CR) และ LVDS 
หลักการสำคัญระดับ Senior Engineer ไม่ใช่แค่การเดินสายคู่กันไปเรื่อยๆ แต่คือการควบคุม **Odd-Mode / Even-Mode Impedance**, การกำจัด **Intra-Pair Skew**, และการป้องกันการแปลงสัญญาณจาก Differential ไปเป็น Common-Mode Noise ($S_{cd21}$)

---

### 1.1 ความสัมพันธ์ระหว่าง $Z_{diff}$, $Z_{odd}$, และ $Z_0$
คู่สาย Differential ประกอบด้วย 2 ลายวงจรที่มีการเชื่อมโยงทางแม่เหล็กไฟฟ้า (Electromagnetic Coupling):
- **Odd Mode ($Z_{odd}$):** สภาวะที่ทั้งสองเส้นถูกขับด้วยสัญญาณตรงกันข้าม ($+V$ และ $-V$)
- **Even Mode ($Z_{even}$):** สภาวะที่ทั้งสองเส้นถูกขับด้วยสัญญาณขั้วเดียวกัน ($+V$ และ $+V$)

ค่า Differential Impedance ($Z_{diff}$) และ Common-Mode Impedance ($Z_{comm}$) คำนวณได้จาก:

$$Z_{diff} = 2 \times Z_{odd}$$
$$Z_{comm} = \frac{Z_{even}}{2}$$

สำหรับ Microstrip แบบ Edge-Coupled:
$$Z_{diff} \approx 2 \times Z_0 \left( 1 - 0.48 e^{-0.96 \frac{s}{h}} \right) \quad [\Omega]$$

- $Z_0$: Characteristic Impedance ของเส้นเดี่ยว (Single-Ended) เมื่อไม่มีคู่สาย
- $s$: ระยะห่างระหว่างเส้น (Trace Spacing / Separation)
- $h$: ความสูงของ Dielectric ถึง Reference Plane

```
          w         s         w
       ┌─────┐   ◄─────►   ┌─────┐
       │  +  │             │  -  │   t
    ───┴─────┴─────────────┴─────┴───────────────── Dielectric (εr)
                          ▲
                          │  h
    ──────────────────────▼──────────────────────── Reference Plane (GND)
```

**ข้อคิดคำนวณเชิงวิศวกรรม:**
- เมื่อระยะห่าง $s > 2h$ การเหนี่ยวนำข้ามเส้น (Coupling) จะลดลงเหลือน้อยกว่า 5% ทำให้ $Z_{diff} \approx 2 Z_0$
- แต่หากเดินคู่ชิดกันแน่นหนา (Tightly Coupled, $s \approx w \approx h$) หากมีตัวกวนจากภายนอก สัญญาณรบกวนจะตกลงทั้งสองเส้นเท่าๆ กัน (Common-Mode Rejection ที่ดีขึ้น)

---

### 1.2 Intra-Pair Skew และการเกิด Common-Mode Noise
หากความยาวของสายคู่ Differential ไม่เท่ากัน ($\Delta L$) จะเกิดความต่างของเวลาเดินทาง (Intra-Pair Skew, $\Delta t$):

$$\Delta t = \Delta L \times t_{pd}$$

ผลลัพธ์คือ สัญญาณหักล้างกันไม่สมบูรณ์ที่ปลายทาง ทำให้พลังงานส่วนหนึ่งถูกแปลงรูปไปเป็น **Common-Mode Voltage ($V_{cm}$)**:

$$V_{cm}(t) = \frac{V_+(t) + V_-(t)}{2}$$

ตามสมการ S-Parameter การแปลงสัญญาณนี้วัดด้วยค่า **$S_{cd21}$ (Differential-to-Common Mode Conversion)**:
- หาก $\Delta t$ มีค่าเพียง 10% ของ Rise Time ($0.1 \times t_r$) ค่า Common-Mode Noise ที่เกิดขึ้นสามารถทำให้การทดสอบ **FCC / CISPR Class B Radiated Emissions ตกทันที** เนื่องจากกระแส Common-Mode แม้เพียงไม่กี่ไมโครแอมแปร์ ($\mu\text{A}$) บนสายเคเบิลภายนอก ก็สามารถแผ่คลื่นแม่เหล็กไฟฟ้าเกินเกณฑ์กฎหมายได้

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน (失敗事例: Shippai Jirei)
**ปัญหา:** บอร์ดประมวลผลกล้องอุตสาหกรรมที่ใช้บัส PCIe Gen 3 (8 Gbps) เกิด Bit Error Rate (BER) สูง และเชื่อมต่อ Link ได้เพียง Gen 1 (2.5 Gbps)
**สาเหตุที่ตรวจพบ (検図での指摘):**
1. เกิด **Intra-Pair Skew สะสมกว่า 28 ps** จากการเลี้ยวโค้ง 90 องศาหลายครั้งบนบอร์ดโดยไม่มีการชดเชยความยาวทันที
2. วิศวกรไปทำการ Tuning ความยาวชดเชย (Meander Delay) ที่บริเวณปลายทางใกล้คอนเนคเตอร์ แทนที่จะทำที่จุดเกิดการเลี้ยวโค้ง ทำให้สัญญาณวิ่งแบบไม่สมดุลเป็นระยะทางยาวกว่า 60 mm เกิด Common-Mode Radiation ตลอดเส้นทาง

### กฎทองการเดินสาย Differential สำหรับ Senior Engineer:
1. **Compensate Immediately (スキュー補正は発生源直後で):**
   - เมื่อมีการเลี้ยวโค้ง ทำให้เส้นวงในสั้นกว่าเส้นวงนอก ให้ใส่หยักชดเชย (Meander Tuning) **ทันทีภายในระยะไม่เกิน 5 mm จากจุดเลี้ยวโค้ง** อย่าปล่อยให้สะสมไปแก้ที่ปลายทาง
2. **Symmetrical Geometry Around Vias:**
   - เมื่อต้องเจาะ Via เพื่อเปลี่ยน Layer ให้เจาะ Signal Via ทั้งคู่แบบสมมาตร และต้องเจาะ GND Stitching Via ประกบทั้งสองข้างเสมอ
3. **AC Coupling Capacitor Placement:**
   - สำหรับบัส PCIe หรือ SATA ที่ต้องมีตัวเก็บประจุ AC Coupling (เช่น $0.1 \ \mu\text{F}$ 0201/0402):
     - ต้องวางขนานกันในแนวระนาบเดียวกันแบบสมมาตร
     - **ตัด Copper ใต้ Pad (Anti-pad cutout):** ควรตัด Plane ชั้นใต้ Pad ของ C ออกเล็กน้อย เพื่อชดเชย Parasitic Capacitance ของ Pad ไม่ให้เกิด Impedance Dip ต่ำกว่า $85 \ \Omega$

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### ศัพท์เทคนิคสำคัญ (重要技術用語)
| คำศัพท์ | คำอ่าน (Kana) | คำแปลภาษาไทย / ภาษาอังกฤษ |
|---|---|---|
| **差動配線** | さどうはいせん (Sadō Haisen) | การเดินสายแบบดิฟเฟอเรนเชียล (Differential Routing) |
| **差動インピーダンス** | さどうインピーダンス (Sadō Inpīdansu) | Differential Impedance ($Z_{diff}$) |
| **コモンモードノイズ** | コモンモードノイズ (Komon Mōdo Noizu) | Common-Mode Noise |
| **ペア内スキュー** | ペアないスキュー (Pea-nai Sukyū) | Intra-Pair Skew (ความเหลื่อมของเวลาในคู่สายเดียวกัน) |
| **等長配線** | とうちょうはいせん (Tōchō Haisen) | Length-Matched Routing (การเดินสายความยาวเท่ากัน) |
| **ミアンダ配線** | ミアンダはいせん (Mianda Haisen) | Meander / Accordion Tuning (การเดินสายหยักเพื่อปรับความยาว) |
| **同相成分** | どうそうせいぶん (Dōsō Seibun) | Common-Mode Component |
| **逆相成分** | ぎゃくそうせいぶん (Gyakusō Seibun) | Differential-Mode Component |

### ประโยคตัวอย่างที่ใช้จริงในการทำ Design Review (検図の指摘文例)

> **指摘事項 1:**  
> 「PCIe Tx差動ペア（`PCIE_TX0_P/N`）において、コーナー部でのペア内スキューが約15ps生じていますが、補正ミアンダが配置されていません。許容スキュー仕様（5ps以下）を満たすよう、コーナーの曲がり直後に等長補正を入れてください。」  
> *(ในคู่สาย PCIe Tx มี Intra-Pair Skew เกิดขึ้นที่มุมเลี้ยวประมาณ 15 ps แต่ไม่มีหยักชดเชยความยาว เพื่อให้ได้ตามเกณฑ์สเปกที่ไม่เกิน 5 ps กรุณาใส่ Meander ชดเชยทันทีหลังมุมเลี้ยว)*

> **指摘事項 2:**  
> 「AC結合コンデンサ（C12, C13）の実装パッド直下でL2層のGNDが抜かれておらず、TDR測定でインピーダンスが75Ωまで急峻に低下（ディップ）する懸念があります。パッド下のL2プレーンを部分的にリファレンスプレーンカット（ボイド配置）してインピーダンスを整合させてください。」  
> *(ใต้ Pad ของ AC Coupling Capacitor C12, C13 ไม่ได้ตัด Ground Plane บน L2 ออก ซึ่งมีความเสี่ยงที่จะทำให้ค่า Impedance ดิ่งลงเหลือ 75 โอห์ม ในการวัด TDR กรุณาเปิด Void ตัด Plane ใต้ Pad บางส่วนเพื่อรักษา Impedance ให้คงที่)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1 (การวิเคราะห์สาเหตุ Common-Mode Radiation)
คู่สัญญาณ Differential สำหรับ USB 3.0 (5 Gbps, $t_r = 100 \text{ ps}$) เดินบนบอร์ดด้วยความเร็ว $t_{pd} = 6.0 \text{ ps/mm}$ หากวิศวกรปล่อยให้เกิดความแตกต่างของความยาวสายบวกและลบ $\Delta L = 3.0 \text{ mm}$ ผลกระทบใดจะเกิดขึ้นอย่างเด่นชัดที่สุด?

- **ก)** สัญญาณจะสูญเสียพลังงาน DC ไปในสายทองแดงมากขึ้น 50%
- **ข)** เกิด Intra-Pair Skew เท่ากับ 18 ps คิดเป็น 18% ของ Rise Time ทำให้เกิด Common-Mode Noise สูงมากและเสี่ยงต่อการสอบตก EMC Radiated Emission
- **ค)** Differential Impedance จะเปลี่ยนจาก $90 \ \Omega$ เป็น $180 \ \Omega$ ทันที
- **ง)** ไม่เกิดผลกระทบใดๆ เพราะ Receiver มีวงจร Equalizer ชดเชยได้เสมอ

> **เฉลยและบทวิเคราะห์:**  
> **ข้อ ข)**  
> $\Delta t = \Delta L \times t_{pd} = 3.0 \text{ mm} \times 6.0 \text{ ps/mm} = 18 \text{ ps}$  
> สัดส่วน Skew ต่อ Rise time คือ $\frac{18 \text{ ps}}{100 \text{ ps}} = 18\%$  
> ตามหลักทฤษฎี High-Speed Signal Integrity เกณฑ์ Intra-pair skew ที่ยอมรับได้ทั่วไปสำหรับสัญญาณ 5 Gbps คือไม่เกิน **5 ps (หรือน้อยกว่า 5% ของ $t_r$)** ค่า Skew ที่สูงถึง 18 ps จะทำให้เกิด Common-Mode Voltage สูงมาก ซึ่งจะแปลงเป็นคลื่นวิทยุแผ่ออกจากสายและบอร์ด ส่งผลให้ไม่ผ่านการทดสอบ EMC

---

### ข้อที่ 2 (การวาง AC Coupling Capacitor)
ในการออกแบบลายวงจร PCIe Gen 4 ที่ต้องใส่ AC Coupling Capacitor ขนาด 0402 บนคู่สาย $85 \ \Omega$ เหตุใดวิศวกร Senior จึงมักสั่งให้ตัด Solid Ground ใต้ Pad ของตัวเก็บประจุ (Placing an Anti-pad / Plane Void under SMD Pad)?

- **ก)** เพื่อป้องกันไม่ให้ความร้อนจากการบัดกรีไหลลง Ground Plane มากเกินไป
- **ข)** เพื่อลด Parasitic Capacitance ของทองแดง Pad ขนาดใหญ่ที่ทำให้ค่า Impedance ดิ่งลง (Capacitive Dip) และดึงค่ากลับขึ้นมาใกล้เคียง $85 \ \Omega$
- **ค)** เพื่อเพิ่มค่า Inductance ของสายให้สามารถกรองสัญญาณรบกวนได้ดีขึ้น
- **ง)** เพื่อให้ช่างประกอบสามารถตรวจสอบรอยบัดกรีด้วยกล้อง X-ray ได้ง่ายขึ้น

> **เฉลยและบทวิเคราะห์:**  
> **ข้อ ข)**  
> Pad ทองแดงสำหรับบัดกรีอุปกรณ์ SMD จะมีความกว้างกว่าเส้น Trace ปกติมาก (เช่น Trace กว้าง 5 mil แต่ Pad กว้าง 20 mil) ทำให้เกิด Excess Capacitance ต่อ Ground Plane ส่งผลให้เกิด **Impedance Drop (Capacitive Discontinuity)** ลงมาเหลือ $65-75 \ \Omega$ ซึ่งทำให้เกิดการสะท้อนสัญญาณและ Eye Diagram ปิดตัวลง  
> การตัด Ground ใต้ Pad บน Layer ถัดไปออก (Reference Void) จะทำให้ระยะ $h$ เพิ่มขึ้นไปยัง Layer ถัดไป ช่วยลด Capacitance และดึง Impedance บริเวณรอยต่อให้กลับมาอยู่ที่ $85 \ \Omega$

---

### ข้อที่ 3 (การทำ Length Matching / Tuning)
หากต้องการชดเชยความยาวสาย Differential Pair ให้เท่ากัน บริเวณใดที่ **ห้าม** ใส่หยักเลี้ยวชดเชย (Meander Tuning) โดยเด็ดขาดตามมาตรฐานการออกแบบความเร็วสูง?

- **ก)** บริเวณที่อยู่ห่างจาก Driver ไม่เกิน 10 mm
- **ข)** บริเวณปลายทางของเส้นทางหลังจากผ่านการเลี้ยวโค้งมาแล้วหลายเซนติเมตร
- **ค)** บริเวณใกล้กับขั้ว Receiver ที่สุด
- **ง)** ถูกทั้งข้อ ข) และ ค)

> **เฉลยและบทวิเคราะห์:**  
> **ข้อ ง)**  
> การใส่หยักชดเชยที่ปลายทางหรือใกล้ Receiver (ปล่อยให้สัญญาณวิ่งไม่เท่ากันมาตลอดทาง) จะทำให้คู่สายวิ่งในสภาวะที่มี Common-Mode Noise ตลอดความยาวบอร์ด เกิดทั้งการแผ่คลื่นรบกวน (EMI) และเกิด Crosstalk ไปยังสายข้างเคียง  
> กฎเหล็กของ High-Speed Layout คือ **"Correct Skew at the Source of Mismatch"** ต้องชดเชยทันทีหลังจุดที่เกิดความไม่เท่ากัน (เช่น ทันทีหลังมุมเลี้ยวโค้ง) เพื่อให้สัญญาณวิ่งกลับเข้าสู่สภาวะ Differential ที่สมดุลตลอดเส้นทางที่เหลือ
