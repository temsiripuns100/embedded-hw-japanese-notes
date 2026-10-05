# Lesson 001: PCB Routing Part 1 - High-Speed Microstrip & Transmission Line Design
*(プリント基板の高速配線設計 - マイクロストリップ線路と伝送線路理論)*

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

ในการออกแบบฮาร์ดแวร์ระดับ Senior Engineer การเดินลายวงจรความถี่สูง (High-Speed Trace Routing) จะไม่ถูกมองว่าเป็นเพียง "สายไฟนำสัญญาณ" (Lumped Element) อีกต่อไป แต่ต้องปฏิบัติตามทฤษฎี **ระบบสายส่ง (Transmission Line Theory)** และ **ทฤษฎีคลื่นแม่เหล็กไฟฟ้า (Electromagnetic Field Distribution)** 

### 1.1 เงื่อนไขที่วงจรกลายเป็น Transmission Line ($L_{crit}$)
วิศวกรต้องคำนวณหาความยาววิกฤต (Critical Trace Length, $L_{crit}$) เสมอ หากความยาวของ Trace ($L$) มากกว่า $L_{crit}$ จะเกิดผลกระทบของคลื่นสะท้อน (Transmission Line Reflections) หากไม่มีการทำ Impedance Matching:

$$L_{crit} = \frac{t_r}{2 \times t_{pd}}$$

โดยที่:
- $t_r$ คือ Rise Time ของสัญญาณ (10% ถึง 90% หรือ 20% ถึง 80%) เช่น สัญญาณจาก FPGA Xilinx UltraScale+ หรือ MCU STM32H7 ที่มี $t_r \approx 0.5 \text{ ns}$
- $t_{pd}$ คือ Propagation Delay ต่อหน่วยความยาว:
  $$t_{pd} = \frac{\sqrt{\epsilon_{eff}}}{c} \approx 84.72 \times \sqrt{\epsilon_{eff}} \quad [\text{ps/inch}]$$
  สำหรับชั้นนอก (Microstrip บน FR-4 ทั่วไปที่ $\epsilon_r = 4.2, \epsilon_{eff} \approx 3.0$):
  $$t_{pd} \approx 84.72 \times \sqrt{3.0} \approx 146.7 \text{ ps/inch} \ (5.77 \text{ ps/mm})$$

**ตัวอย่างการคำนวณจริง:**
หาก $t_r = 500 \text{ ps}$:
$$L_{crit} = \frac{500 \text{ ps}}{2 \times 146.7 \text{ ps/inch}} \approx 1.70 \text{ inches} \ (43.2 \text{ mm})$$
*ข้อสรุปหน้างาน:* ลายวงจรใดที่มีความยาวเกิน **43.2 mm** จะต้องควบคุม Characteristic Impedance ($Z_0$) อย่างเข้มงวด 100% มิฉะนั้นสัญญาณจะเกิด Overshoot/Undershoot และ Ringing จนรบกวน Logic Threshold

---

### 1.2 สมการ Characteristic Impedance ($Z_0$) ของ Surface Microstrip
ตามมาตรฐาน IPC-2141 ค่า $Z_0$ สำหรับ Microstrip คำนวณได้จาก:

$$Z_0 = \frac{87}{\sqrt{\epsilon_r + 1.41}} \ln \left( \frac{5.98h}{0.8w + t} \right) \quad [\Omega]$$

*(ใช้ได้เมื่อ $0.1 < \frac{w}{h} < 3.0$)*

- $w$: ความกว้างของ Trace (Trace width)
- $h$: ความหนาของ Dielectric (ความสูงระหว่าง Trace ถึง Ground Reference Plane)
- $t$: ความหนาของฟอยล์ทองแดง (Copper thickness: 1 oz $\approx 35 \ \mu\text{m} \approx 1.37 \text{ mil}$, 0.5 oz $\approx 18 \ \mu\text{m} \approx 0.7 \text{ mil}$)
- $\epsilon_r$: Dielectric Constant ของวัสดุ Substrate (FR-4 Standard $\approx 4.2 - 4.5$, Isola FR408HR $\approx 3.68$, Panasonic Megtron 6 $\approx 3.4$)

```
     Trace (w, t)  ────>  ┌───────┐
                          │       │  t
   ───────────────────────┴───────┴──────────────────────── Dielectric (εr)
                              ▲
                              │  h
   ───────────────────────────▼────────────────────────────
     Reference Plane (Solid GND)
```

**ตัวเลขมาตรฐานหน้างานสำหรับบอร์ด 50 $\Omega$ Single-Ended (Stackup 4-Layer / 6-Layer):**
- Prepreg 2116 ($h \approx 4.0 \text{ mil}, \epsilon_r = 4.2$)
- ทองแดง Base Copper 0.5 oz เคลือบ Plating รวมเป็น 1 oz ($t \approx 1.4 \text{ mil}$)
- คำนวณความกว้าง Trace ($w$) เพื่อให้ได้ $Z_0 = 50 \ \Omega$:
  $$w \approx 6.8 - 7.2 \text{ mil} \ (0.17 - 0.18 \text{ mm})$$

---

### 1.3 การกระจายตัวของกระแสย้อนกลับ (Return Current Distribution)
กระแสความถี่สูงไม่ไหลผ่านเส้นทางที่มีความต้านทานต่ำสุด (Least Resistance) แต่จะไหลตาม **เส้นทางที่มี Inductance ต่ำสุด (Least Inductance Path)**
ความหนาแน่นของกระแสย้อนกลับ $J(x)$ บน Reference Plane ใต้ Trace คำนวณตามสูตรของ Dr. Howard Johnson:

$$J(x) = \frac{I_0}{\pi h} \cdot \frac{1}{1 + \left(\frac{x}{h}\right)^2}$$

- $x$: ระยะห่างในแนวระนาบจากกึ่งกลางของ Trace
- $h$: ความสูงของ Dielectric จาก Trace ถึง Plane

**ความหมายเชิงวิศวกรรม:**
- กระแสย้อนกลับกว่า **80%** กระจุกตัวอยู่ภายในพื้นที่ระยะกว้าง $3h$ ใต้ Trace
- หากมีรอยตัด (Slot / Split Plane) ตัดผ่านใต้ Trace แม้เพียง 0.2 mm กระแสย้อนกลับจะถูกบังคับให้ไหลอ้อมรอบรอยตัด ทำให้ Loop Area ขยายใหญ่ขึ้นทันทีเหนี่ยวนำให้เกิด **EMI Radiation สูงขึ้นมากกว่า 20-30 dB** และทำให้ค่า $Z_0$ พุ่งสูงขึ้นเกิด Impedance Discontinuity

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน (失敗事例: Shippai Jirei)
**ปัญหา:** บอร์ดส่งสัญญาณ SPI Clock ความถี่ 50 MHz ไปยัง Flash Memory เกิดสัญญาณรบกวนตกขอบ (Jitter) สูง และไม่ผ่านการทดสอบ EMC Radiated Emissions ที่ย่านความถี่ 250 MHz และ 350 MHz
**สาเหตุที่ตรวจพบ (検図での指摘):**
วิศวกร Layout เดินสาย SPI_CLK ข้ามรอยแยกของ Plane ระหว่าง $+3.3\text{V}$ Plane และ $+1.8\text{V}$ Plane (スリット跨ぎ) ทำให้ Loop Area กว้างกว่า 12 $\text{cm}^2$

### ขั้นตอนการแก้ไขและเกณฑ์การตรวจแบบ (検図チェックリスト):
1. **Rule of Continuous Reference Plane:**
   - สายสัญญาณความถี่สูง ($t_r < 2 \text{ ns}$ หรือ $f > 10 \text{ MHz}$) ต้องมีระนาบ Solid Ground ต่อเนื่องตลอดความยาวเส้นทาง 100% ห้ามเดินข้าม Split Plane โดยเด็ดขาด
2. **กรณีจำเป็นต้องเปลี่ยน Layer (Via Transition):**
   - เมื่อ Trace มุดข้าม Layer จาก Top ไป Bottom ผ่าน Ground Plane ทั้งสองชั้น จะต้องวาง **GND Return Stitching Via** ห่างจาก Signal Via ไม่เกิน **$0.5 \text{ mm}$ (20 mil)** เพื่อให้กระแสย้อนกลับมีเส้นทางเชื่อมโยงระหว่าง Layer ได้ทันที
3. **การหลบเลี่ยง Void ของ BGA Escape:**
   - บริเวณใต้ตัว BGA ที่มี Via เจาะหนาแน่น (Via Anti-pads) มักจะเกิดสภาวะ Anti-pad ซ้อนทับกันจนตัดขาด Plane (Swiss Cheese Effect) ให้ขยับระยะ Pitch ของ Via หรือปรับขนาด Anti-pad เพื่อให้มีเนื้อทองแดงเชื่อมต่อกันอย่างน้อย 4 mil ระหว่าง Via

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### ศัพท์เทคนิคสำคัญ (重要技術用語)
| คำศัพท์ | คำอ่าน (Kana) | คำแปลภาษาไทย / ภาษาอังกฤษ |
|---|---|---|
| **高速配線** | こうそくはいせん (Kōsoku Haisen) | การเดินสายความถี่สูง (High-Speed Routing) |
| **特性インピーダンス** | とくせいインピーダンス (Tokusei Inpīdansu) | Characteristic Impedance ($Z_0$) |
| **整合性** | せいごうせい (Seigōsei) | Consistency / Matching |
| **リターンパス** | リターンパス (Ritān Pasu) | Return Path |
| **スリット跨ぎ** | スリットまたぎ (Suritto Matagi) | การเดินสายข้ามรอยแยกเพลน (Trace crossing split plane) |
| **プレーン不連続** | プレーンふれんぞく (Purēn Furenzoku) | Reference Plane Discontinuity |
| **グランドステッチビア** | グランドステッチビア (Gurando Sutetchi Bia) | Ground Stitching Via |
| **表皮効果** | ひょうひこうか (Hyōhi Kōka) | Skin Effect |
| **誘電正接** | ゆうでんせいせつ (Yūdenseisetsu) | Loss Tangent / Dissipation Factor ($\tan \delta$) |

### ประโยคตัวอย่างที่ใช้จริงในการทำ Design Review (検図の指摘文例)

> **指摘事項 1:**  
> 「L1層のクロック配線（NET: `CLK_50M`）が、L2層の+3.3Vと+1.8Vの電源スリットを跨いで配線されています。リターンパス不連続による放射ノイズ（EMI）悪化および波形乱れの要因となるため、GNDベタ面のみを参照するように配線ルートを変更してください。」  
> *(สาย Clock บน Layer 1 เดินข้ามรอยแยก Power Plane บน Layer 2 ซึ่งทำให้เกิด Return Path Discontinuity ส่งผลให้ EMI แย่ลงและรูปคลื่นผิดเพี้ยน กรุณาย้ายเส้นทางให้ทับอยู่บน Solid GND เท่านั้น)*

> **指摘事項 2:**  
> 「差動信号ラインがビアで層間移動していますが、近傍（0.5mm以内）にGNDステッチングビアが配置されていません。層間リターンパスを確保するため、GNDビアを追加してください。」  
> *(คู่สัญญาณ Differential มีการเปลี่ยน Layer ผ่าน Via แต่ไม่มี Ground Stitching Via ในระยะ 0.5 mm กรุณาเพิ่ม GND Via เพื่อรักษาระนาบ Return Path ข้าม Layer)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1 (การคำนวณ Transmission Line)
วิศวกรออกแบบระบบส่งสัญญาณความเร็วสูง $t_r = 200 \text{ ps}$ บนบอร์ดวัสดุ FR-4 ชั้นนอกที่มี $\epsilon_{eff} = 3.2$ หากเส้นทางลายวงจรมีความยาว $25 \text{ mm}$ ถามว่า:
ลายวงจรนี้จำเป็นต้องคำนวณและควบคุม Characteristic Impedance ($Z_0$) หรือไม่ เพราะเหตุใด?

- **ก)** ไม่จำเป็น เพราะความยาว 25 mm สั้นมาก ยังไม่ถึง 1 นิ้ว
- **ข)** จำเป็น เพราะ $L_{crit} \approx 16.5 \text{ mm}$ ซึ่งสั้นกว่าความยาวลายวงจรจริง 25 mm
- **ค)** ไม่จำเป็น เพราะสัญญาณจะสะท้อนเฉพาะเมื่อความถี่สูงกว่า 1 GHz เท่านั้น
- **ง)** จำเป็นเฉพาะในกรณีที่เป็นสาย Differential Pair เท่านั้น

> **เฉลยและบทวิเคราะห์:**  
> **ข้อ ข)**  
> คำนวณ $t_{pd} = 84.72 \times \sqrt{3.2} \approx 151.5 \text{ ps/inch} \ (5.96 \text{ ps/mm})$  
> คำนวณ $L_{crit} = \frac{t_r}{2 \times t_{pd}} = \frac{200 \text{ ps}}{2 \times 5.96 \text{ ps/mm}} \approx 16.78 \text{ mm}$  
> เมื่อความยาวจริง $25 \text{ mm} > L_{crit} (16.78 \text{ mm})$ ลายวงจรนี้มีพฤติกรรมเป็น **Transmission Line** โดยสมบูรณ์ จึงจำเป็นต้องควบคุม $Z_0$ เพื่อป้องกันสัญญาณสะท้อน

---

### ข้อที่ 2 (การวิเคราะห์ปัญหาหน้างาน EMC & SI)
ในระหว่างการวัดด้วย Oscilloscope ขนาด 4 GHz ตรวจพบ Ringing บนสัญญาณ 3.3V LVCMOS ที่ปลายทาง Receiver อย่างรุนแรง โดยบอร์ดใช้ Microstrip $50 \ \Omega$ ยาว 100 mm และ Driver มี Output Impedance ภายใน ($R_o$) เท่ากับ $18 \ \Omega$ ถามว่าวิธีแก้ปัญหาที่ต้นทางที่ถูกต้องและเป็นไปตามหลักวิศวกรรมที่สุดคืออะไร?

- **ก)** ใส่ Pull-up Resistor $50 \ \Omega$ ที่ปลายทางต่อเข้ากับไฟ 3.3V
- **ข)** ใส่ Series Damping Resistor ขนาดประมาณ $33 \ \Omega$ วางชิดขา Output ของ Driver ทันที
- **ค)** ใส่ Capacitor $100 \text{ pF}$ ขนานลงกราวด์ที่ขา Output ของ Driver
- **ง)** ลดความกว้างของ Trace ลงครึ่งหนึ่งเพื่อเพิ่มความต้านทานของเส้นทองแดง

> **เฉลยและบทวิเคราะห์:**  
> **ข้อ ข)**  
> ต้นเหตุเกิดจาก Impedance Mismatch ที่ต้นทาง: $R_o = 18 \ \Omega < Z_0 = 50 \ \Omega$ ทำให้เกิดค่าสัมประสิทธิ์การสะท้อนที่ต้นทางเป็นลบ ($\Gamma_s < 0$) คลื่นสะท้อนจากปลายทาง (Receiver มี Input Impedance สูงมาก $\Gamma_L \approx +1$) จึงสะท้อนกลับไปกลับมาเกิดเป็น Underdamped Ringing  
> การแก้ไขตามหลัก Source Termination คือการใส่ตัวต้านทานอนุกรม $R_s$:  
> $$R_s = Z_0 - R_o = 50 - 18 = 32 \ \Omega \quad (\text{เลือกใช้ค่ามาตรฐาน } 33 \ \Omega)$$  
> โดยต้องวางชิดขา Driver ที่สุดเพื่อไม่ให้เกิด Stub เล็กๆ ระหว่าง Driver กับ $R_s$

---

### ข้อที่ 3 (คำศัพท์และการตรวจแบบ 検図)
หากในเอกสาร 検図報告書 (Kenzu Inspection Report) หัวหน้าวิศวกรชาวญี่ปุ่นเขียนคอมเมนต์ระบุว่า:
> *"クロックラインのスタブ長が過大です。T字分岐を廃止し、デイジーチェーン配線へ修正のこと。"*

ข้อความนี้หมายถึงข้อบกพร่องใดในงาน Layout และต้องดำเนินการแก้ไขอย่างไร?

- **ก)** ความกว้างของสาย Clock กว้างเกินไป ให้ลดขนาดลงและเดินแบบขนาน
- **ข)** ลายวงจร Clock มีติ่งแยก (Stub) ยาวเกินไปจากการแยกแบบรูปตัว T ให้ยกเลิกและเปลี่ยนเป็นเดินแบบ Daisy-Chain (Fly-by) ต่อเนื่องทีละตัว
- **ค)** สาย Clock มีการข้ามเลเยอร์มากเกินไป ให้ตัดสัญญาณทิ้งแล้วเดินเฉพาะชั้นบนสุด
- **ง)** Ground Plane ใต้สาย Clock มีรอยตัด ให้ถมทองแดงแบบ Daisy-Chain

> **เฉลยและบทวิเคราะห์:**  
> **ข้อ ข)**  
> คำว่า **スタブ長 (Stub-chō)** คือความยาวของติ่งแยก (Transmission Line Stub) ซึ่งทำให้เกิดการสะท้อนสัญญาณและแหว่งของรูปคลื่น (Notch filtering at resonance)  
> คำว่า **T字分岐 (T-ji bunki)** คือการแยกกิ่งแบบตัว T ซึ่งมักสร้าง Stub ยาวที่ควบคุม Impedance ไม่ได้  
> คำว่า **デイジーチェーン配線 (Deijīchēn haisen)** คือการเดินสายแบบ Daisy-chain (เข้า IC ตัวที่ 1 แล้วออกต่อไปยัง IC ตัวที่ 2) โดยไม่มีติ่งแยก ซึ่งเป็นมาตรฐานสำหรับ Clock และ Address bus (เช่น DDR3/DDR4 Fly-by topology)
