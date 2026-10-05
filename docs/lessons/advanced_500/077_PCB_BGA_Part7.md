# Lesson 077: PCB BGA Part 7 - High-Frequency SerDes Signal Integrity, Intra-Pair Skew, S-Parameter Compliance (IEEE 802.3ck), and TDR Optimization

---

## 1. ทฤษฎีวิศวรรรมเชิงลึก (高度なエンジニアリング理論)

ในระบบส่งข้อมูลความเร็วสูงระดับไฮเปอร์สเกล (Hyperscale Datacenters) และสวิตช์เครือข่ายความเร็วสูงยุค **800G และ 1.6T Ethernet** ซึ่งขับเคลื่อนด้วยช่องสัญญาณ **112 Gbps และ 224 Gbps PAM4 SerDes (IEEE 802.3ck)** คาบเวลาของ 1 บิตสัญลักษณ์ (Unit Interval - UI) ถูกบีบอัดลงเหลือเพียง:
$$T_{\text{UI}} = \frac{1}{\text{Baud Rate}} = \frac{1}{56\text{ GBaud}} \approx 17.86\ \text{ps}\ (112\text{G PAM4})$$
$$T_{\text{UI}} = \frac{1}{112\text{ GBaud}} \approx 8.93\ \text{ps}\ (224\text{G PAM4})$$

ที่ความถี่ไนควิสต์ (Nyquist Frequency) สูงถึง $f_N = 28\text{ GHz}$ และ $56\text{ GHz}$ รอยต่อสัญญาณใต้ตัวถัง BGA (BGA Breakout Region) ถือเป็นจุดวิกฤตที่สุดที่สามารถทำลายคุณภาพของสัญญาณทั้งระบบ วิศวกรอาวุโสต้องควบคุม **ความคลาดเคลื่อนเวลาภายในคู่สายอนุพันธ์ (Intra-Pair Differential Skew)**, **การแปลงสัญญาณเป็นโหมดร่วม (Differential-to-Common Mode Conversion: $S_{cd21}$)**, และ **การปรับจูนอิมพีแดนซ์เชิงเวลา (TDR Impedance Profile Optimization)** ด้วยเทคนิค Shadow Anti-pad

```
+-----------------------------------------------------------------------------------------+
|                  112G PAM4 Intra-Pair Skew & Mode Conversion Physics                    |
|                                                                                         |
|       Differential Input (D+ & D-)               Skewed Output (Phase Shift Delta t)    |
|       D+ ───/\───\/───/\───                     D+ ───/\───\/───/\───                   |
|       D- ───\/───/\───\/───                     D- ─────\/───/\───\/─ (Delayed by Skew!)|
|       [ Pure Differential Mode ]                [ Common-Mode Noise Generation: Scd21 ] |
|                                                                                         |
|       BGA Ball Field Breakout Region                                                    |
|           (D+) Ball        (D-) Ball                                                    |
|             ┌───┐            ┌───┐                                                      |
|             │ ● │            │ ● │                                                      |
|             └───┘            └───┘                                                      |
|               │ L_inner        │ L_outer (Turns around corner!)                         |
|               │                └────────────┐                                           |
|               ▼ Length Mismatch!            ▼                                           |
|       ════════╪═════════════════════════════╪══════ Ground Reference Plane L2          |
|              [░░░] Shadow Anti-pad         [░░░] (Cutout to Remove Capacitive Dip!)     |
+-----------------------------------------------------------------------------------------+
```

### 1.1 ฟิสิกส์ของการแปลงโหมดสัญญาณ (Mode Conversion: $S_{\text{cd21}}$) จาก Intra-Pair Skew

เมื่อสัญญาณอนุพันธ์ (Differential Signal: $V_{\text{diff}} = V_+ - V_-$) เคลื่อนที่ผ่าน BGA Breakout ซึ่งมักมีจุดเลี้ยวหักมุมเพื่อหลบพินบอลข้างเคียง เส้นทางเดินของสายสัญญาณเส้นนอก ($L_{\text{outer}}$) จะยาวกว่าเส้นใน ($L_{\text{inner}}$) ก่อให้เกิดผลต่างเวลาหน่วง (Intra-Pair Delay Skew: $\Delta t_{\text{skew}}$):

#### 1. การกำเนิดสัญญาณรบกวนโหมดร่วม (Common-Mode Voltage Generation):
$$V_{\text{comm}}(t) = \frac{V_+(t) + V_-(t)}{2}$$

ในสภาวะอุดมคติที่ไม่มี Skew ($\Delta t = 0$): $V_+(t) = -V_-(t)$ ส่งผลให้ $V_{\text{comm}}(t) = 0$  
แต่เมื่อเกิด Skew ($\Delta t_{\text{skew}} \ne 0$): ในช่วงรอยต่อของการเปลี่ยนสถานะ (Switching Transition) แรงดันขั้วบวกและขั้วลบจะไม่หักล้างกัน เกิดเป็น **Common-Mode Pulse Spike**:
$$V_{\text{comm, peak}} \approx V_{\text{diff, swing}} \cdot \left( \frac{\Delta t_{\text{skew}}}{t_{\text{rise}}} \right)$$

#### 2. สัมประสิทธิ์การแปลงโหมด (Mixed-Mode Scattering Parameter - $S_{\text{cd21}}$):
$$S_{\text{cd21}}(f) \approx \sin\left( \pi \cdot f \cdot \Delta t_{\text{skew}} \right) \approx \pi \cdot f \cdot \Delta t_{\text{skew}} \quad (\text{เมื่อ } \pi f \Delta t \ll 1)$$

- พลังงานของสัญญาณอนุพันธ์ที่มีประโยชน์ ($S_{\text{dd21}}$) จะถูกถ่ายเทแปลงสภาพกลายเป็นสัญญาณรบกวนโหมดร่วม ($S_{\text{cd21}}$)
- สัญญาณ Common Mode นี้ไม่สามารถถูกตรวจจับได้โดยตัวรับ Differential Receiver และจะสะท้อนกลับไปมาหรือแผ่กระจายเป็น **คลื่นแม่เหล็กไฟฟ้ารบกวน (Severe EMI Radiation)**
- **ข้อกำหนดมาตรฐาน IEEE 802.3ck:** กำหนดให้ค่าการแปลงโหมด $S_{\text{cd21}}$ ต้องต่ำกว่า **$-20\ \text{dB}$** ตลอดช่วงความถี่ Nyquist ($28\text{ GHz}$)
- ขีดจำกัดของ Intra-Pair Skew สูงสุดที่ยอมรับได้สำหรับ 112G PAM4:
  $$\Delta t_{\text{skew, max}} \le \frac{T_{\text{UI}}}{10} \approx \frac{17.86\ \text{ps}}{10} \approx 1.78\ \text{ps}$$
  ซึ่งคิดเป็นความยาวบนแผ่นวงจร Megtron 6 ($\epsilon_r \approx 3.6$) เพียง:
  $$\Delta L_{\text{max}} = \frac{c \cdot \Delta t_{\text{skew, max}}}{\sqrt{\epsilon_r}} = \frac{3 \times 10^8 \times 1.78 \times 10^{-12}}{\sqrt{3.6}} \approx 0.28\text{ mm}\ (280\ \mu\text{m} \approx 11\ \text{mil})$$

---

### 1.2 การปรับจูนอิมพีแดนซ์ในโดเมนเวลา (TDR Impedance Tuning) ด้วย Shadow Anti-pad

เมื่อส่งคลื่นทดสอบ Time Domain Reflectometry (TDR) ผ่านจุดเชื่อมต่อ BGA กราฟอิมพีแดนซ์มักจะแสดงลักษณะความไม่ต่อเนื่องอย่างชัดเจน:

```
TDR Impedance Profile (Ohms)
  60 ──┬────────────────────────────────────────────────────────────
       │                         ▲ Inductive Via Spike (+5 to +10 Ohms)
  50 ──┼─────────┐             ┌─/\───────══════════════════════════ 50 Ohm Trace
       │         │             │   \     /
  40 ──┼─────────\             /    └───┘
       │          \───░░░░░───/  ▼ Capacitive BGA Pad Dip (Drops to 38-42 Ohms!)
  30 ──┼────────────────────────────────────────────────────────────
       └───┬─────────────┬─────────────┬─────────────┬──────────────
          Pkg Substrate BGA Pad      Inner Via     Inner Stripline
```

#### 1. สาเหตุของ Capacitive Dip ใต้ BGA Pad:
แผ่นแลนด์แพดทองแดงของ BGA (ขนาด $D \approx 0.40\text{ mm}$) มีพื้นที่ผิวหน้าตัดกว้างกว่าเส้นนำสัญญาณทั่วไป ($W \approx 0.10\text{ mm}$) มากถึง $4 - 5$ เท่า เมื่อวางอยู่เหนือระนาบกราวด์อ้างอิงชั้น L2 ที่ระยะห่างฉนวนเพียง $h = 75\ \mu\text{m}$ จะสร้างความจุไฟฟ้าส่วนเกิน (Excess Parasitic Capacitance):
$$C_{\text{pad}} \approx \epsilon_0 \epsilon_r \cdot \frac{\pi (D_{\text{pad}}/2)^2}{h} \approx 300\text{ ถึง }500\ \text{fF}$$
ส่งผลให้อิมพีแดนซ์ตกฮวบลง (Capacitive Dip) จาก $50\ \Omega$ เหลือเพียง $38 - 42\ \Omega$ ก่อให้เกิดการสะท้อนกลับของคลื่นอย่างรุนแรง ($S_{\text{dd11}} > -10\ \text{dB}$)

#### 2. กลไกการชดเชยด้วย Shadow Anti-pad (Reference Plane Cutout):
- ทำการเจาะเปิดช่องว่างระนาบทองแดง (Aperture Cutout / Void) ในชั้นระนาบอ้างอิง L2 ตรงตำแหน่งใต้ BGA Pad พอดิบพอดี
- บังคับให้เส้นสนามไฟฟ้าของ BGA Pad ต้องยิงทะลุข้ามไปจับกับระนาบอ้างอิงชั้น L3 ซึ่งอยู่ลึกกว่า ($h_{\text{eff}} \approx 200\ \mu\text{m}$)
- ความจุไฟฟ้าจะลดลงตามสัดส่วน $C \propto \frac{1}{h}$:
  $$C_{\text{pad, compensated}} \approx C_{\text{pad}} \times \left( \frac{h_{\text{L2}}}{h_{\text{L3}}} \right) \approx 120\text{ ถึง }180\ \text{fF}$$
- **ผลลัพธ์:** TDR Dip จะถูกยกตัวกลับคืนสู่ระดับ **$48.5\ \Omega - 51.5\ \Omega$** ราบเรียบเกือบสมบูรณ์แบบ

---

### 1.3 ดัชนีความปลอดภัยของช่องสัญญาณตาม IEEE 802.3ck: Channel Operating Margin (COM)

สำหรับการส่งสัญญาณระดับ 112G PAM4 การวัดเพียงพารามิเตอร์ $S_{21}$ หรือ Eye Height แบบเดิมไม่เพียงพออีกต่อไป มาตรฐานสากลใช้เครื่องมือทางคณิตศาสตร์ที่เรียกว่า **Channel Operating Margin (COM)**:

$$COM = 20 \log_{10} \left( \frac{A_s}{\sigma_N} \right) \ge 3.0\ \text{dB}$$

โดยที่:
- $A_s$ = แอมพลิจูดของสัญญาณที่จุดศูนย์กลางของรูปตาสัญญาณหลังผ่านกระบวนการ CTLE และ DFE Equalization
- $\sigma_N$ = ผลรวมทางสถิติของสัญญาณรบกวนทั้งหมด (ISI Noise + Crosstalk Noise + Jitter Noise + Thermal Noise)

หากช่องสัญญาณ BGA Breakout มี Return Loss หรือ Mode Conversion แย่ลงเพียงเล็กน้อย ค่า $\sigma_N$ จะพุ่งสูงขึ้นอย่างรวดเร็ว และดึงค่า COM ให้ร่วงลงต่ำกว่าเกณฑ์วิกฤต $3.0\ \text{dB}$ ซึ่งส่งผลให้อัตราความผิดพลาดของบิต (BER) พุ่งเกินขีดจำกัดที่ตัวแก้ไขรหัส Forward Error Correction (RS-FEC) จะกู้คืนได้

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน (失敗事例 - Shippai Jirei)

**เหตุการณ์:** บอร์ดประมวลผลเครือข่ายความเร็วสูงระดับดาต้าเซ็นเตอร์ (800G Data Center Core Switch Card) ที่ใช้งานชิป Switching ASIC ตัวถัง FC-BGA ขนาด $65 \times 65\text{ mm}$ จำนวน 3,600 พิน ขับสัญญาณ 112 Gbps PAM4 SerDes จำนวน 64 เลน ผ่านแผงวงจร 24 ชั้น (Low-loss Megtron 6 laminate):
1. ในขั้นตอนการทดสอบความสอดคล้องตามมาตรฐาน IEEE 802.3ck พบว่าช่องสัญญาณในกลุ่มพอร์ต 33 ถึง 48 มีค่า COM สอบตกที่ $1.9\text{ dB}$ (เกณฑ์มาตรฐานบังคับ $\ge 3.0\text{ dB}$)
2. รูปตาสัญญาณ PAM4 ทั้ง 3 ช่องตา (Upper, Middle, Lower Eyes) ถูกสัญญาณรบกวนบีบจนความสูงตา (Eye Height) เหลือเพียง $14\ \text{mV}$ และความกว้างตา (Eye Width) แคบกว่า $0.12\ \text{UI}$ ส่งผลให้เกิดปัญหาการหลุดการเชื่อมต่อ (Link Flapping) อย่างต่อเนื่อง

```
+-----------------------------------------------------------------------------------------+
|                  RCA: 112G PAM4 COM Failure & Skew Dispersion Mechanics                 |
|                                                                                         |
|   [ ปัญหาที่ 1: TDR Capacitive Dip (No Cutout) ]  [ ปัญหาที่ 2: Delayed Skew Matching ] |
|                                                                                         |
|       BGA Pad L1      Solid GND Plane L2            BGA Breakout (Skew Accumulated)     |
|       ┌─────────┐     ══════════════════            D+ ──────────────────────┐ (Short)  |
|       │ Copper  │     (Excessive C_pad = 420 fF)    D- ──────────────────────┴─┐ (Long) |
|       └───┬─────┘                                   <────── Delta L = 0.65 mm ───────>  |
|           ▼                                         Accumulated Skew = 3.9 ps!          |
|       TDR Dips to 37.5 Ohms!                        [ Jog Compensation placed 50 mm away]
|       Sdd11 = -8.5 dB (Severe Reflection!)          High-Frequency Phase Destroyed!     |
|                                                     Scd21 degraded to -11.2 dB!         |
+-----------------------------------------------------------------------------------------+
```

#### การวิเคราะห์หาสาเหตุรากเหง้า (Root Cause Analysis - RCA):
1. **สาเหตุของ Capacitive Dip และ Return Loss พังทลาย:**
   - การตรวจสอบเลเยอร์สแตกอัปพบว่า ใต้พินบอล BGA ของคู่สายสัญญาณความเร็วสูง ระนาบกราวด์ชั้น L2 เป็นแผ่นทองแดงทึบ (Solid Copper) โดยไม่มีการเปิดช่อง Shadow Anti-pad
   - การวัด TDR ระบุว่าอิมพีแดนซ์บริเวณ BGA Pad ตกวูบลงเหลือ $37.5\ \Omega$ (Capacitive Notch ลึก $-12.5\ \Omega$) ส่งผลให้ค่า Return Loss ($S_{\text{dd11}}$) ที่ความถี่ Nyquist $28\text{ GHz}$ เลวร้ายแตะ $-8.5\ \text{dB}$ พลังงานสัญญาณสะท้อนกลับไปรบกวนต้นทางอย่างรุนแรง
2. **สาเหตุของการแปลงโหมดสัญญาณและการสูญเสียรูปตา (Severe Mode Conversion):**
   - ในขั้นตอนการคลี่สายออกจาก BGA พินบอลถูกจัดวางในแนวเฉียง ทำให้สายสัญญาณฝั่งขวา ($D_-$) ต้องเลี้ยวอ้อมไกลกว่าฝั่งซ้าย ($D_+$) เป็นระยะทางถึง $\Delta L = 0.65\text{ mm}$ ก่อให้เกิด Delay Skew สะสมถึง $3.9\ \text{ps}$ (คิดเป็นกว่า $22\%$ ของ Unit Interval!)
   - **ความผิดพลาดมหันต์ของวิศวกร Layout:** วิศวกรไปทำการปรับความยาวชดเชย (Jog Tuning / Serpentine Matching) ที่บริเวณปลายทางห่างออกไปถึง $50\text{ mm}$ นอกตัวถัง BGA
   - **หลักฟิสิกส์คลื่น:** ในระยะทาง $50\text{ mm}$ ที่สัญญาณเดินทางไปด้วยสภาวะ Skew นั้น คลื่นได้แปลงสภาพเป็น Common Mode ไปเรียบร้อยแล้ว การไปปรับความยาวชดเชยที่ปลายทางไม่สามารถกู้คืนเฟสของฮาร์มอนิกความถี่สูงกลับมาได้ ส่งผลให้ $S_{\text{cd21}}$ สูงถึง $-11.2\ \text{dB}$ ทำลายดวงตาสัญญาณ PAM4 จนปิดสนิท
3. **ผลกระทบจากแนวเส้นใยแก้ว (Fiber-Weave Effect):**
   - แผงบอร์ดใช้ผ้าใยแก้วมาตรฐานแบบเบอร์ 1080 ซึ่งมีช่องว่างอากาศระหว่างมัดเส้นใยแก้วกว้าง เส้นสัญญาณเส้นหนึ่งวิ่งทับบนมัดแก้ว ($\epsilon_r \approx 6.0$) ขณะที่อีกเส้นวิ่งทับบนโพรงเรซิน ($\epsilon_r \approx 3.0$) เพิ่ม Skew แบบสุ่มอีกกว่า $2.5\ \text{ps}$

#### มาตรการแก้ไขเชิงวิศวกรรม (Engineering Countermeasures):
1. **ติดตั้ง Shadow Anti-pad บนระนาบ L2:**
   - ออกแบบช่องเปิดทองแดงทรงกลมบนชั้น L2 ใต้ BGA Pad ทุกตัว โดยมีขนาดใหญ่กว่าขอบแพด $0.10\text{ mm}$ เพื่อลดค่า $C_{\text{pad}}$ ลงเหลือ $140\ \text{fF}$
   - ปรับแต่ง TDR Profile ให้ยกตัวขึ้นมาอยู่ในช่วง $49.0\ \Omega \pm 1.5\ \Omega$ และผลักดันค่า $S_{\text{dd11}}$ ให้ดีกว่า $-16.5\ \text{dB}$ ตลอดช่วง $0 - 30\text{ GHz}$
2. **บังคับใช้กฎ Local Skew Compensation (ภายในระยะ $\le 1.0\text{ mm}$):**
   - กำหนดกฎเหล็กว่าการชดเชยความยาวภายในคู่สาย (Intra-pair Skew Matching) ต้องกระทำทันที ณ จุดที่สัญญาณหลุดพ้นจากรูเวีย BGA ภายในระยะทางไม่เกิน $1.0\text{ mm}$ โดยไม่อนุญาตให้สะสม Skew ข้ามโซน
   - ควบคุมค่า Skew สะสมรวมให้ต่ำกว่า **$0.8\text{ ps}$** ($< 5\%\text{ UI}$)
3. **เปลี่ยนวัสดุเป็นผ้าใยแก้วชนิดกระจายตัวแบน (Spread Glass 1067 / 1078) ร่วมกับการเดินสายเอียง $10^\circ$:**
   - เปลี่ยนวัสดุ Laminate เป็นชนิด Spread Glass ที่เส้นใยถักทอแนบสนิทไร้ช่องว่าง และกำหนดในแบบสั่งผลิตให้หมุนวางลายวงจรเอียงทำมุม $10^\circ$ กับแกนผ้าใยแก้ว (Zig-zag / Angled Routing) เพื่อขจัดปัญหา Fiber-weave Skew ให้เหลือศูนย์

---

### รายการตรวจสอบวิศวกรรม SerDes ความเร็วสูงใต้ BGA (112G SerDes Checklist)

| ลำดับ | รายการตรวจสอบทางวิศวกรรม | เกณฑ์การยอมรับ (Acceptance Criteria) | ความเสี่ยงหากละเลย |
| :---: | :--- | :--- | :--- |
| 1 | **Intra-Pair Skew ภายในคู่สายอนุพันธ์** | Skew $\le 1.5\text{ ps}$ ($\le 1.0\text{ ps}$ สำหรับ 112G PAM4) | เกิดการแปลงโหมด ($S_{\text{cd21}}$) ทำลายตาสัญญาณ PAM4 |
| 2 | **ตำแหน่งการชดเชยความยาวคู่สาย (Jog Tuning)**| ต้องชดเชยภายในระยะ $\le 1.0\text{ mm}$ หลังออกจากจุดเลี้ยว | เฟสสัญญาณความถี่สูงถูกทำลายถาวร ชดเชยปลายทางไม่ได้ผล |
| 3 | **การทำ Shadow Anti-pad ใต้ BGA Pad** | เจาะเปิดระนาบ L2 ให้ TDR Dip ลึกไม่เกิน $\pm 2.5\ \Omega$ | สัญญาณสะท้อนกลับรุนแรง ($S_{\text{dd11}} > -10\ \text{dB}$) |
| 4 | **การควบคุม Via Stub (Back-drill Residual)** | ติ่งเวียตกค้าง $h_{\text{stub}} \le 0.125\text{ mm}$ ($5\text{ mil}$) | เกิด Quarter-wave Resonance Notch ลบพลังงานสัญญาณ |
| 5 | **การเลือกชนิดผ้าใยแก้ว (Laminate Weave)** | บังคับใช้ Spread Glass (เช่น 1067, 1078) หรือเดินสายเอียง $10^\circ$| Glass Skew สุ่มตามแนวเส้นใย ดึงเฟสสัญญาณคลาดเคลื่อน |
| 6 | **ระยะห่างระหว่างคู่สายต่างกัน (Inter-Pair Space)**| รักษาระยะห่างข้ามคู่สาย $\ge 4W$ หรือคั่นด้วย GND Vias | สัญญาณกวนข้ามช่อง (FEXT/NEXT) ดึงค่า COM สอบตก |
| 7 | **เกณฑ์ Channel Operating Margin (COM)** | COM $\ge 3.0\text{ dB}$ ตามมาตรฐาน IEEE 802.3ck | อัตราความผิดพลาดของบิต (BER) สูงเกินกว่า FEC จะแก้ไขได้ |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง

| คำศัพท์ภาษาญี่ปุ่น (คันจิ/คะนะ) | คำอ่าน (Romaji) | ภาษาอังกฤษ (Technical Term) | คำอธิบายความหมายเชิงวิศวกรรม |
| :--- | :--- | :--- | :--- |
| **同相モード変換** | Dōsō mōdo henkan | Common-mode conversion ($S_{cd21}$)| การที่พลังงานสัญญาณอนุพันธ์รั่วไหลกลายเป็นสัญญาณรบกวนโหมดร่วม |
| **ペア内スキュー** | Pea-nai sukyū | Intra-pair skew | ผลต่างของเวลาหน่วงระหว่างขั้วบวกและขั้วลบในคู่สายสัญญาณเดียวกัน |
| **シャドウアンチパッド**| Shadō anchipaddo | Shadow anti-pad | การเจาะเปิดระนาบอ้างอิงใต้แพด BGA เพื่อลดค่า Parasitic Capacitance |
| **特性インピーダンス低下**| Tokusei inpiidansu teika| Capacitive impedance dip | ภาวะที่ค่าความต้านทานจำเพาะตกวูบลงเนื่องจากความจุไฟฟ้าเฉพาะจุด |
| **ガラス織り目効果** | Garasu orime kōka | Fiber-weave effect | ความแปรปรวนของค่าไดอิเล็กทริกจากโครงสร้างการถักทอของเส้นใยแก้ว |
| **開口余裕度** | Kaikō yoyūdo | Channel Operating Margin (COM) | ดัชนีมาร์จินความปลอดภัยทางสัญญาณตามมาตรฐาน IEEE |
| **局所等長配線** | Kyokusho tōchō haisen| Local length matching | การปรับชดเชยความยาวคู่สายทันที ณ จุดกำเนิดความคลาดเคลื่อน |
| **斜め配線** | Naname haisen | Angled / Zig-zag routing | การเดินสายเอียงทำมุมกับแนวเส้นใยแก้วเพื่อเฉลี่ยค่าคงที่ไดอิเล็กทริก |
| **目玉波形開口率** | Medama hakei kaikō ritsu| Eye diagram opening ratio | อัตราส่วนความกว้างและความสูงของรูปตาสัญญาณ PAM4 |
| **時間領域反射測定** | Jikan ryōiki hansha sokutei| Time Domain Reflectometry (TDR)| เทคนิคการวัดอิมพีแดนซ์ตามฟังก์ชันของเวลาและระยะทางเดินคลื่น |

---

### 3.2 ประโยคตรวจแบบที่ใช้จริงในโรงงานญี่ปุ่น (指摘事項 - Shiteki Jikō)

#### ตัวอย่างข้อคิดเห็นที่ 1: การตรวจพบ Intra-Pair Skew และการสั่งแก้ไขด้วย Local Tuning
> **日本語:**  
> 「112Gbps PAM4 SerDes差動信号（Lane 0〜15）のBGA引き出し部において、ピン配置の制約から差動ペア内に約0.6mmの配線長差（遅延スキュー換算で約3.6ps）が発生しています。しかしながら、等長補正（蛇行配線）がBGAから40mm以上離れた外層領域で実施されており、高周波領域における同相モード変換損失（Scd21）が-12dBまで劣化する見込みです。IEEE 802.3ck規格（COM≧3.0dB）を遵守するため、スキュー補正はBGAエスケープ直後（1.0mm以内）の局所領域で直ちに完了させ、ペア内スキューを0.8ps以下に厳格管理してください。」  
> **คำแปลภาษาไทย:**  
> "ในบริเวณคลี่สาย BGA ของสัญญาณอนุพันธ์ 112Gbps PAM4 SerDes (เลน 0 ถึง 15) เนื่องจากข้อจำกัดของการจัดวางพิน ทำให้เกิดผลต่างความยาวภายในคู่สายประมาณ 0.6 มม. (คิดเป็น Delay Skew ประมาณ 3.6 ps) อย่างไรก็ตาม การปรับชดเชยความยาว (ลายเลี้ยวคดเคี้ยว) กลับถูกนำไปทำในบริเวณชั้นนอกที่ห่างจากตัวถัง BGA ออกไปกว่า 40 มม. ซึ่งจะทำให้การสูญเสียจากการแปลงโหมดร่วม (Scd21) ในย่านความถี่สูงเลวร้ายลงแตะ -12dB เพื่อให้เป็นไปตามมาตรฐาน IEEE 802.3ck (COM ไม่ต่ำกว่า 3.0dB) การชดเชย Skew จะต้องกระทำในบริเวณเฉพาะที่ทันทีหลังออกจาก BGA (ภายในระยะ 1.0 มม.) และควบคุม Intra-pair Skew ให้ต่ำกว่า 0.8 ps อย่างเคร่งครัด"

#### ตัวอย่างข้อคิดเห็นที่ 2: การสั่งเจาะ Shadow Anti-pad บนระนาบ L2 เพื่อแก้ TDR Dip
> **日本語:**  
> 「高速トランシーバBGAパッド直下の内層L2（GND層）がベタ銅箔のままとなっており、TDRシミュレーションにおいて約38Ωの急峻な容量性ディップ（Capacitive Dip）が観測されています。この不連続点はNyquist周波数（28GHz）における反射損失（Sdd11）を著しく悪化させ、アイパターンの閉塞原因となります。L2層のパッド直下領域に直径0.50mmのシャドウアンチパッド（銅箔抜き）を配置し、寄生容量を低減することで、TDRインピーダンスを49Ω±2Ωの範囲内に平坦化させてください。」  
> **คำแปลภาษาไทย:**  
> "ในชั้นใน L2 (ระนาบกราวด์) บริเวณใต้แลนด์แพด BGA ของตัวรับส่งสัญญาณความเร็วสูงโดยตรงยังคงเป็นเนื้อทองแดงทึบ ซึ่งผลการจำลอง TDR แสดงให้เห็นหลุมอิมพีแดนซ์แบบคาปาซิทีฟ (Capacitive Dip) ตกฮวบลงลึกถึง 38 โอห์ม จุดความไม่ต่อเนื่องนี้จะทำให้ค่า Return Loss (Sdd11) ที่ความถี่ Nyquist (28GHz) เลวร้ายลงอย่างมีนัยสำคัญ และเป็นต้นเหตุให้รูปตาสัญญาณปิดสนิท ขอให้เจาะเปิดช่อง Shadow Anti-pad (เว้นทองแดง) ขนาดเส้นผ่านศูนย์กลาง 0.50 มม. บนชั้น L2 ใต้แพดโดยตรง เพื่อลดค่าความจุไฟฟ้าปรสิต และปรับระดับ TDR อิมพีแดนซ์ให้ราบเรียบอยู่ในช่วง 49 โอห์ม บวกลบ 2 โอห์ม"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณ Intra-Pair Skew และขีดจำกัดการแปลงโหมดสัญญาณ (Mode Conversion & Skew Limit)

**โจทย์:**  
ช่องสัญญาณความเร็วสูง 112 Gbps PAM4 ทำงานที่อัตราสัญญาณสัญลักษณ์ $56\ \text{GBaud}$ (คาบเวลา Unit Interval $T_{\text{UI}} = 17.857\text{ ps}$, ความถี่ Nyquist $f_N = 28\text{ GHz}$)  
สัญญาณอนุพันธ์มีระดับแรงดันแกว่งเต็มสเกล $V_{\text{diff, p-p}} = 800\text{ mV}$ และมีเวลาขาขึ้น (Rise Time $20\% - 80\%$) $t_{\text{rise}} = 12.0\text{ ps}$  
แผงวงจรผลิตจากวัสดุ Megtron 6 ที่มีค่าความเร็วการแพร่กระจายคลื่นในชั้น Stripline $v_p = 1.60 \times 10^8\ \text{m/s}$ (เวลาหน่วงการเดินทาง $t_{\text{delay}} = 6.25\ \text{ps/mm}$)

1. ตามข้อกำหนดมาตรฐานความสมบูรณ์ของสัญญาณ สัญญาณรบกวนโหมดร่วมสูงสุด ($V_{\text{comm, peak}}$) ที่เกิดขึ้นจากความไม่สมดุลของคู่สายต้องถูกควบคุมให้ **ไม่เกิน $5\%$ ของขนาดสัญญาณอนุพันธ์** ($V_{\text{comm, peak}} \le 0.05 \cdot V_{\text{diff, p-p}} = 40\text{ mV}$) จงคำนวณหา **ค่า Intra-Pair Delay Skew สูงสุดที่ยอมรับได้ ($\Delta t_{\text{skew, max}}$)**
2. แปลงค่า Delay Skew สูงสุดที่คำนวณได้เป็น **ผลต่างความยาวทางกายภาพบนแผ่น PCB ($\Delta L_{\text{skew, max}}$)** ในหน่วยไมครอน ($\mu\text{m}$) และมิลลิเมตร ($\text{mm}$)
3. หากวิศวกรออกแบบปล่อยให้เกิดผลต่างความยาวใน BGA Breakout $\Delta L = 0.40\text{ mm}$ จงคำนวณค่าสัมประสิทธิ์การแปลงโหมด $S_{\text{cd21}}$ ที่ความถี่ $28\text{ GHz}$ (ในหน่วย $\text{dB}$) และตัดสินว่าผ่านเกณฑ์มาตรฐาน IEEE 802.3ck ($S_{\text{cd21}} \le -20\text{ dB}$) หรือไม่

<details>
<summary>เฉลยและบทวิเคราะห์เชิงวิศวกรรม</summary>

**ขั้นตอนการคำนวณ:**

**1. คำนวณหา Delay Skew สูงสุดที่ยอมรับได้ ($\Delta t_{\text{skew, max}}$):**
ความสัมพันธ์ระหว่างยอดแรงดันโหมดร่วมและ Delay Skew ในช่วงเวลาขาขึ้น:
$$V_{\text{comm, peak}} \approx V_{\text{diff, p-p}} \cdot \left( \frac{\Delta t_{\text{skew}}}{2 \cdot t_{\text{rise}}} \right)$$
*(หมายเหตุ: ตัวหารเป็น $2 \cdot t_{\text{rise}}$ เนื่องจากคิดเฉลี่ยผลต่างสองขั้วสัญญาณ)*  
จัดรูปสมการเพื่อหา $\Delta t_{\text{skew}}$:
$$\Delta t_{\text{skew, max}} = \frac{2 \cdot V_{\text{comm, limit}} \cdot t_{\text{rise}}}{V_{\text{diff, p-p}}}$$
แทนค่า:
$$\Delta t_{\text{skew, max}} = \frac{2 \times 40\ \text{mV} \times 12.0\ \text{ps}}{800\ \text{mV}} = \frac{960}{800} = 1.20\ \text{ps}$$
**คำตอบส่วนที่ 1:** ยอมรับค่า Delay Skew ได้สูงสุดไม่เกิน **$1.20\ \text{ps}$** (คิดเป็นเพียง $6.72\%$ ของ $T_{\text{UI}}$)

---

**2. คำนวณหาผลต่างความยาวทางกายภาพ ($\Delta L_{\text{skew, max}}$):**
จากความเร็วการแพร่กระจายคลื่น $v_p = 1.60 \times 10^8\ \text{m/s}$:
$$\Delta L_{\text{skew, max}} = v_p \cdot \Delta t_{\text{skew, max}} = (1.60 \times 10^8\ \text{m/s}) \times (1.20 \times 10^{-12}\ \text{s})$$
$$\Delta L_{\text{skew, max}} = 1.92 \times 10^{-4}\ \text{m} = 0.192\text{ mm} = 192\ \mu\text{m}\ (\approx 7.56\ \text{mil})$$
**คำตอบส่วนที่ 2:** ผลต่างความยาวทางกายภาพระหว่างสายสองเส้นในคู่เดียวกันต้องถูกควบคุมให้ **ไม่เกิน $192\ \mu\text{m}$ ($0.192\text{ mm}$)**

---

**3. คำนวณ $S_{\text{cd21}}$ ที่ความถี่ $28\text{ GHz}$ กรณี $\Delta L = 0.40\text{ mm}$:**
- คำนวณค่า Delay Skew จริงที่เกิดขึ้น:
  $$\Delta t_{\text{skew, actual}} = \frac{\Delta L}{v_p} = \frac{0.40 \times 10^{-3}\ \text{m}}{1.60 \times 10^8\ \text{m/s}} = 2.50 \times 10^{-12}\ \text{s} = 2.50\ \text{ps}$$
- คำนวณค่า $S_{\text{cd21}}$ เชิงเส้น:
  $$S_{\text{cd21}}(f) = \sin\left( \pi \cdot f \cdot \Delta t_{\text{skew}} \right)$$
  แทนค่า $f = 28\text{ GHz} = 28 \times 10^9\ \text{Hz}$ และ $\Delta t = 2.50 \times 10^{-12}\ \text{s}$:
  $$\theta = \pi \times (28 \times 10^9) \times (2.50 \times 10^{-12}) = \pi \times 0.070 = 0.2199\ \text{เรเดียน}\ (\approx 12.6^\circ)$$
  $$S_{\text{cd21, linear}} = \sin(0.2199) \approx 0.2181$$
- แปลงเป็นหน่วย $\text{dB}$:
  $$S_{\text{cd21, dB}} = 20 \log_{10}(0.2181) \approx -13.22\ \text{dB}$$

**การประเมินผลตามเกณฑ์ IEEE 802.3ck:**  
- เกณฑ์มาตรฐานบังคับ: $S_{\text{cd21}} \le -20\ \text{dB}$
- ค่าที่ได้จริง: $-13.22\ \text{dB}$ (สูงกว่าเกณฑ์ที่ยอมรับได้ถึง $+6.78\ \text{dB}$!)
- **ผลการตัดสิน:** **สอบตกอย่างรุนแรง (FAIL)**  
  พลังงานสัญญาณอนุพันธ์จะรั่วไหลกลายเป็นสัญญาณรบกวนโหมดร่วมมหาศาล ทำให้รูปตาสัญญาณ PAM4 ปิดสนิท และจะแผ่คลื่นแม่เหล็กไฟฟ้าไม่ผ่านการทดสอบ FCC/CISPR EMI อย่างแน่นอน

</details>

---

### ข้อที่ 2: การคำนวณการชดเชย TDR Capacitive Dip ด้วย Shadow Anti-pad

**โจทย์:**  
บนแผงวงจรส่งสัญญาณ 56 Gbps PAM4 เส้นส่งสัญญาณ Stripline มีความต้านทานจำเพาะเป้าหมาย $Z_0 = 50.0\ \Omega$ (มีค่าความจุต่อหน่วยความยาว $C_0 = 120\ \text{fF/mm}$ และความเหนี่ยวนำต่อหน่วยความยาว $L_0 = 0.30\ \text{nH/mm}$)  
ที่จุดบัดกรี BGA Pad มีเส้นผ่านศูนย์กลาง $D_{\text{pad}} = 0.40\text{ mm}$ และตั้งอยู่เหนือระนาบกราวด์ชั้น L2 ที่ระยะฉนวน $h_1 = 80\ \mu\text{m}$ (ไดอิเล็กทริก $\epsilon_r = 3.6$) ก่อให้เกิดความจุไฟฟ้าปรสิตเฉพาะจุด $C_{\text{pad}} = 450\ \text{fF}$ โดยไม่มีความเหนี่ยวนำชดเชย  
พิจารณาช่วงรอยต่อ BGA Pad ที่มีความยาวเชิงกายภาพเทียบเท่า $l_{\text{pad}} = 0.50\text{ mm}$ (ซึ่งมีความเหนี่ยวนำของแผ่นทองแดง $L_{\text{pad}} = L_0 \cdot l_{\text{pad}} = 0.15\text{ nH} = 150\ \text{pH}$):

1. จงคำนวณหาค่าความต้านทานจำเพาะยังผล ($Z_{\text{pad, uncompensated}}$) ของบริเวณ BGA Pad เมื่อระนาบกราวด์ชั้น L2 เป็นแผ่นทองแดงทึบ (Solid Copper)
2. คำนวณค่าสัมประสิทธิ์การสะท้อนกลับของแรงดัน ($\Gamma$) และค่า Return Loss ($S_{11}$ ในหน่วย $\text{dB}$) ที่เกิดขึ้นจากจุดรอยต่อนี้
3. เพื่อขจัด Capacitive Dip และฟื้นฟูอิมพีแดนซ์ให้กลับมาเป็น $50.0\ \Omega$ วิศวกรต้องการเจาะช่อง **Shadow Anti-pad** บนระนาบ L2 เพื่อให้เส้นสนามไฟฟ้ายิงทะลุลงไปจับกับระนาบ L3 ที่ระยะความลึก $h_2 = 240\ \mu\text{m}$  
   จงคำนวณค่าความจุไฟฟ้าใหม่ของแพด ($C_{\text{pad, new}}$) และพิสูจน์ว่าอิมพีแดนซ์ใหม่จะกลับคืนสู่ค่า $50\ \Omega$ หรือไม่

<details>
<summary>เฉลยและบทวิเคราะห์เชิงวิศวกรรม</summary>

**ขั้นตอนการคำนวณ:**

**1. คำนวณอิมพีแดนซ์ของ BGA Pad ที่ไม่มีการชดเชย:**
- ความเหนี่ยวนำรวมในบริเวณรอยต่อ:
  $$L_{\text{total}} = 0.15\ \text{nH} = 150 \times 10^{-12}\ \text{H}$$
- ความจุไฟฟ้ารวมในบริเวณรอยต่อ (ความจุเส้นเดิมรวมกับความจุของแพด):
  $$C_{\text{line}} = C_0 \cdot l_{\text{pad}} = 120\ \text{fF/mm} \times 0.50\text{ mm} = 60\ \text{fF}$$
  $$C_{\text{total}} = C_{\text{line}} + C_{\text{pad}} = 60\ \text{fF} + 450\ \text{fF} = 510\ \text{fF} = 510 \times 10^{-15}\ \text{F}$$
- คำนวณอิมพีแดนซ์ยังผล:
  $$Z_{\text{pad}} = \sqrt{\frac{L_{\text{total}}}{C_{\text{total}}}} = \sqrt{\frac{150 \times 10^{-12}}{510 \times 10^{-15}}} = \sqrt{\frac{150}{0.510}} = \sqrt{294.12} \approx 17.15\ \Omega$$
  *(หากพิจารณาเฉพาะความจุแบบ Lumped ในระบบส่งคลื่น $50\ \Omega$ อิมพีแดนซ์ TDR Dip จะตกฮวบลงสู่ประมาณ $36 - 38\ \Omega$)*  
  ตามแบบจำลอง TDR Discontinuity:
  $$Z_{\text{TDR}} \approx \frac{Z_0}{\sqrt{1 + \frac{C_{\text{pad}}}{C_{\text{line, ref}}}}} \approx 37.2\ \Omega$$

---

**2. คำนวณค่าการสะท้อนกลับและ Return Loss ($S_{11}$):**
กำหนดให้อิมพีแดนซ์ตกฮวบลงเหลือ $Z_{\text{dip}} = 37.2\ \Omega$ เทียบกับเส้นส่งคลื่นหลัก $Z_0 = 50.0\ \Omega$:
- สัมประสิทธิ์การสะท้อนกลับ:
  $$\Gamma = \frac{Z_{\text{dip}} - Z_0}{Z_{\text{dip}} + Z_0} = \frac{37.2 - 50.0}{37.2 + 50.0} = \frac{-12.8}{87.2} \approx -0.1468$$
- Return Loss ($S_{11}$):
  $$S_{11} = 20 \log_{10}(|\Gamma|) = 20 \log_{10}(0.1468) \approx -16.67\ \text{dB}$$
  (ซึ่งหากรวมอิทธิพลของความถี่สูงที่ $28\text{ GHz}$ ค่า $S_{11}$ จะเลวร้ายลงแตะช่วง $-9$ ถึง $-11\ \text{dB}$)

---

**3. คำนวณการชดเชยด้วย Shadow Anti-pad บน L2:**
เมื่อเจาะเปิดช่องว่างระนาบ L2 เส้นสนามไฟฟ้าจะวิ่งลงสู่ L3 ที่ระยะ $h_2 = 240\ \mu\text{m}$ แทนที่ $h_1 = 80\ \mu\text{m}$:
เนื่องจากค่าความจุแปรผกผันกับระยะห่างระหว่างตัวนำ ($C \propto \frac{1}{h}$):
$$\frac{C_{\text{pad, new}}}{C_{\text{pad, old}}} = \frac{h_1}{h_2} = \frac{80\ \mu\text{m}}{240\ \mu\text{m}} = \frac{1}{3}$$
$$C_{\text{pad, new}} = \frac{450\ \text{fF}}{3} = 150\ \text{fF}$$

- ความจุไฟฟ้ารวมใหม่ในบริเวณรอยต่อ:
  $$C_{\text{total, new}} = C_{\text{line}} + C_{\text{pad, new}} = 60\ \text{fF} + 150\ \text{fF} = 210\ \text{fF}$$
- และการเจาะช่องระนาบ L2 จะทำให้เส้นทางกระแสไหลกลับถอยห่างออกไปเล็กน้อย ซึ่งช่วยเพิ่มค่าความเหนี่ยวนำวงรอบขึ้นเป็น $L_{\text{total, new}} \approx 0.52\ \text{nH} = 520\ \text{pH}$:
  $$Z_{\text{compensated}} = \sqrt{\frac{L_{\text{total, new}}}{C_{\text{total, new}}}} = \sqrt{\frac{520 \times 10^{-12}\ \text{H}}{210 \times 10^{-15}\ \text{F}}} = \sqrt{2,476.19} \approx 49.76\ \Omega$$

**บทสรุปการพิสูจน์:**  
ค่าอิมพีแดนซ์ได้รับการฟื้นฟูกลับคืนสู่ **$49.76\ \Omega$** ซึ่งใกล้เคียงเป้าหมาย $50.0\ \Omega$ อย่างยอดเยี่ยม (คลาดเคลื่อนเพียง $-0.48\%$) ขจัด Capacitive Dip ได้อย่างหมดจด

</details>

---

### ข้อที่ 3: การประเมิน Channel Operating Margin (COM) และอิทธิพลของ Via Stub Resonance

**โจทย์:**  
ช่องสัญญาณส่งข้อมูล 56 GBaud PAM4 ทำงานบนบอร์ดความหนา $2.80\text{ mm}$ ชั้นสัญญาณวิ่งอยู่ในเลเยอร์ L4 (ความลึก $0.40\text{ mm}$ จากผิวด้านบน)  
กระบอกรูเวียเจาะทะลุลงไปถึงชั้นล่างสุด L20 ก่อให้เกิด Via Stub ยาว $h_{\text{stub}} = 2.40\text{ mm}$  
วัสดุบอร์ดมีค่าความเร็วคลื่น $v_p = 1.55 \times 10^8\ \text{m/s}$  
จากการวัด S-parameters พบว่าติ่งเวียทำให้เกิด Quarter-Wave Resonance Notch ในกราฟ $S_{\text{dd21}}$ ที่ความถี่ $f_{\text{notch}} = 16.15\text{ GHz}$ ด้วยความลึก $-28\ \text{dB}$  
ในระบบ PAM4 นี้ ซอฟต์แวร์ประเมินค่า COM จำลองผลได้ดังนี้:
- เมื่อมี Via Stub ($h_{\text{stub}} = 2.40\text{ mm}$): อัตราส่วนกำลังสัญญาณต่อสัญญาณรบกวนคือ $A_s = 22\ \text{mV}$ และค่าสัญญาณรบกวนรวมคือ $\sigma_N = 18.5\ \text{mV}$
- หากทำการ Back-drilling ล้างติ่งเวียให้เหลือสั้นเพียง $h_{\text{stub}} = 0.10\text{ mm}$: หลุม Resonance จะถูกผลักดันออกไปอยู่ที่ความถี่ $> 100\text{ GHz}$ ส่งผลให้ $A_s$ เพิ่มขึ้นเป็น $48\ \text{mV}$ และสัญญาณรบกวนสะท้อนลดลงเหลือ $\sigma_N = 11.2\ \text{mV}$

1. จงคำนวณหาค่า Channel Operating Margin ($COM$) ของทั้งสองกรณี (ก่อนและหลังทำ Back-drilling)
2. ตัดสินว่ากรณีใดที่ผ่านเกณฑ์มาตรฐาน IEEE 802.3ck ($COM \ge 3.0\ \text{dB}$)
3. อธิบายบทบาทของตัวปรับแต่งสัญญาณแบบ DFE (Decision Feedback Equalizer) ในชิปรับสัญญาณ SerDes ว่าเหตุใดจึงไม่สามารถชดเชยการสูญเสียสัญญาณจาก Via Stub Resonance Notch ที่ความถี่ $16.15\text{ GHz}$ ได้

<details>
<summary>เฉลยและบทวิเคราะห์เชิงวิศวกรรม</summary>

**ขั้นตอนการคำนวณ:**

**1. คำนวณค่า COM ของทั้งสองกรณี:**
สูตรคำนวณ Channel Operating Margin:
$$COM = 20 \log_{10} \left( \frac{A_s}{\sigma_N} \right)$$

- **กรณีที่ 1: ก่อนทำ Back-drilling ($h_{\text{stub}} = 2.40\text{ mm}$):**
  $$COM_1 = 20 \log_{10} \left( \frac{22\ \text{mV}}{18.5\ \text{mV}} \right) = 20 \log_{10} (1.1892) \approx 20 \times 0.07525 \approx 1.51\ \text{dB}$$

- **กรณีที่ 2: หลังทำ Back-drilling ($h_{\text{stub}} = 0.10\text{ mm}$):**
  $$COM_2 = 20 \log_{10} \left( \frac{48\ \text{mV}}{11.2\ \text{mV}} \right) = 20 \log_{10} (4.2857) \approx 20 \times 0.6320 \approx 12.64\ \text{dB}$$

---

**2. การตัดสินผลตามเกณฑ์ IEEE 802.3ck:**
- เกณฑ์มาตรฐานกำหนด: $COM \ge 3.0\ \text{dB}$
- **กรณีที่ 1 (ก่อน Back-drill):** $COM = 1.51\ \text{dB} < 3.0\ \text{dB}$ $\to$ **สอบตกอย่างสิ้นเชิง (FAIL)** (ระบบจะเกิด Bit Error สูง ลิงก์ไม่สามารถเปิดใช้งานได้)
- **กรณีที่ 2 (หลัง Back-drill):** $COM = 12.64\ \text{dB} \ge 3.0\ \text{dB}$ $\to$ **ผ่านเกณฑ์อย่างยอดเยี่ยม (PASS with Excellent Margin)** (มี Margin ความปลอดภัยสูงถึง $+9.64\ \text{dB}$)

---

**3. บทวิเคราะห์ว่าเหตุใด DFE/CTLE จึงไม่สามารถชดเชย Via Stub Notch ได้:**
1. **ธรรมชาติของหลุมเรโซแนนซ์ (Sharp Null / Infinite Attenuation):** วงจรกรอง CTLE (Continuous Time Linear Equalizer) ในภาครับถูกออกแบบมาเพื่อชดเชยการลดทอนแบบสม่ำเสมอที่แปรตามความถี่ (Smooth $\sqrt{f}$ dielectric & skin effect loss) แต่หลุมเรโซแนนซ์จาก Via Stub เป็นรอยเว้าแคบที่ลึกมาก (Deep Notch Null) หากวงจรกำเนิดเกน (Gain Booster) พยายามจะบูสต์สัญญาณที่ความถี่นี้ มันจะบูสต์สัญญาณรบกวน (Noise Amplification) ขึ้นมาเท่ากัน ทำให้อัตราส่วน SNR ไม่ดีขึ้น
2. **ขีดจำกัดของ DFE Taps (Delay Span Limitation):** ตัวกรอง Decision Feedback Equalizer (DFE) ใช้การหักล้างการแทรกสอดระหว่างสัญลักษณ์ (Post-cursor ISI) โดยใช้จำนวนแท็ปจำกัด (เช่น 16 ถึง 32 Taps) การสะท้อนกลับของคลื่นจากปลายติ่งเวียที่ปลายเปิด (Open Stub) จะสะท้อนไปกลับหลายรอบ (Multiple Round-trip Reflections) จนมีระยะเวลาหน่วงยาวเกินกว่าช่วงเวลาที่ DFE Taps จะครอบคลุมถึง สัญญาณสะท้อนตกค้างจึงกลายเป็นสัญญาณรบกวนที่ไม่สามารถกำจัดได้
3. **ข้อสรุปเชิงวิศวกรรม:** ความบกพร่องทางกายภาพจาก Via Stub **ไม่สามารถแก้ไขได้ด้วยอัลกอริทึมหรือ Equalizer ในชิป** ต้องแก้ไขที่ต้นตอทางกายภาพของแผ่น PCB ด้วยการทำ **Back-drilling** เท่านั้น

</details>
