# Lesson 142: FPGA PLL Deep Dive - Part 2 (Jitter, Phase Noise, and Stability Analysis - Period Jitter, TIE, Dual-Dirac Model, Phase Margin, Cascaded PLL Jitter Peaking & PSRR)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 อนุกรมวิธานของสัญญาณรบกวนทางเวลา (Jitter Taxonomy & Mathematical Definitions)
ในระบบดิจิทัลและ FPGA ความเร็วสูง ความไม่สมบูรณ์ของสัญญาณนาฬิกาถูกพิจารณาใน 2 มิติที่เกี่ยวเนื่องกันทางฟิสิกส์:
* **Time Domain (การแปรผันในโดเมนเวลา):** เรียกว่า **Jitter** ซึ่งคือความคลาดเคลื่อนของจังหวะขอบสัญญาณ (Edge Placement Error)
* **Frequency Domain (การแปรผันในโดเมนความถี่):** เรียกว่า **Phase Noise** ซึ่งคือการกระจายตัวของพลังงานรอบความถี่พาหะ (Spectral Regrowth / Sidebands)

```
        Time Domain (Jitter)                         Frequency Domain (Phase Noise)
  
      Ideal Clock Edge                              Power Spectral Density
            |                                                ^
            v                                                |   Carrier F_0
      +-----+     +-----+     +-----+                        |      |
      |     |     |     |     |     |                        |     /|\
  ----+     +-----+     +-----+     +--                      |    / | \   L(f) Phase Noise
      <----->                                                |   /  |  \  Sideband (dBc/Hz)
      T_1   T_2   T_3                                        |  /   |   \
      |     |     |                                          +-+----+----+------------> Offset (f)
      <----->                                                0      F_0   F_0 + df
      Period Jitter: J_per = T_n - T_0
      TIE (Time Interval Error): Cumulative phase drift
```

#### นิยามทางคณิตศาสตร์ 3 รูปแบบหลักของ Jitter:
1. **Period Jitter ($J_{per}$):**
   ความเบี่ยงเบนของคาบเวลาของสัญญาณนาฬิกาแต่ละลูกเทียบกับคาบเวลาเฉลี่ยในอุดมคติ ($T_0$):
   $$J_{per}(n) = T_n - T_0$$
   โดยมีค่า RMS Period Jitter:
   $$\sigma_{per} = \sqrt{\frac{1}{N-1} \sum_{n=1}^N (T_n - T_0)^2}$$

2. **Cycle-to-Cycle Jitter ($J_{cc}$):**
   ผลต่างระหว่างความกว้างของสองคาบเวลาที่อยู่ติดกันทันที บ่งชี้อัตราการเปลี่ยนแปลงความถี่แบบเฉียบพลัน:
   $$J_{cc}(n) = T_{n+1} - T_n$$
   $$\sigma_{cc} = \sqrt{\frac{1}{N-1} \sum_{n=1}^N (T_{n+1} - T_n)^2}$$

3. **Time Interval Error ($J_{tie}$):**
   ความคลาดเคลื่อนสะสมของตำแหน่งขอบสัญญาณนาฬิกาจริง ($t_n$) เทียบกับตำแหน่งขอบสัญญาณนาฬิกาในอุดมคติ ($n T_0$):
   $$TIE(n) = t_n - n T_0$$
   $TIE$ คือตัวแปรที่วิกฤตที่สุดสำหรับระบบ SerDes ความเร็วสูงและอินเตอร์เฟซหน่วยความจำ DDR เพราะมันคือตัวกำหนดการเปิด/ปิดของ **Data Eye Diagram** โดยตรง

---

### 1.2 แบบจำลองการแยกองค์ประกอบ Dual-Dirac Model และ Total Jitter
สัญญาณรบกวนเวลารวม (Total Jitter: $TJ$) ไม่สามารถนำค่า Peak-to-Peak ของสัญญาณสุ่มมารวมกันแบบตรงๆ ได้ แต่ต้องแยกตามแบบจำลองสถิติ **Dual-Dirac Model**:

$$TJ(BER) = DJ_{\delta\delta} + 2 \cdot Q(BER) \cdot RJ_{rms}$$

```
                Dual-Dirac Probability Density Function (PDF)
                
         DJ_dd (Deterministic Peak-to-Peak Separation)
             |<------------------------->|
             |                           |
            / \                         / \
           /   \                       /   \
          /     \                     /     \
         /  RJ   \                   /  RJ   \
        / (Gauss) \                 / (Gauss) \
  -----+-----------+---------------+-----------+------> Time Error (ps)
      -TJ/2                                    +TJ/2
       |<---------------------------------------->|
                Total Jitter @ Specified BER
```

* **Deterministic Jitter ($DJ_{\delta\delta}$):** สัญญาณรบกวนที่มีขอบเขตแน่นอน (Bounded) เช่น Periodic Jitter (PJ) จากสวิตชิ่งของเรกูเลเตอร์, Data-Dependent Jitter (DDJ / Inter-Symbol Interference: ISI), และ Duty-Cycle Distortion (DCD)
* **Random Jitter ($RJ_{rms}$):** สัญญาณรบกวนที่เกิดจากปรากฏการณ์ทางอุณหพลศาสตร์ (Thermal Noise และ Shot Noise ในซิลิคอน) มีการแจกแจงแบบเกาส์เซียน (Gaussian Distribution) ที่ไร้ขอบเขต (Unbounded)
* **$Q(BER)$:** ค่าสัมประสิทธิ์สถิติตามอัตราความผิดพลาดของบิต (Bit Error Rate):
  $$Q(BER) = \sqrt{2} \cdot \text{erfc}^{-1}(2 \cdot BER)$$

#### ตารางค่า $Q(BER)$ มาตรฐานระดับอุตสาหกรรม:
| Target Bit Error Rate (BER) | $Q(BER)$ | ตัวคูณ $2 \cdot Q(BER)$ | มาตรฐานการสื่อสาร |
|:---:|:---:|:---:|:---|
| $10^{-9}$ | $5.998$ | $11.996$ | PCI Express Gen 1 / 2 |
| $10^{-12}$ | $7.034$ | $14.069$ | 10GbE / PCIe Gen 3/4 / SATA |
| $10^{-15}$ | $7.942$ | $15.884$ | Fibre Channel / Aerospace Avionics |
| $10^{-18}$ | $8.750$ | $17.500$ | Quantum Computing / Deep Space |

---

### 1.3 การแปลง Phase Noise ในย่านความถี่สู่ RMS Phase Jitter
สัญญาณรบกวนเฟส $\mathcal{L}(f)$ มีหน่วยเป็นเดซิเบลเทียบกับสัญญาณพาหะต่อเฮิรตซ์ ($\text{dBc/Hz}$) ที่ออฟเซตความถี่ $f$ ห่างจากสัญญาณพาหะ $f_0$

พลังงานเฟสคลาดเคลื่อนรวม (Integrated Phase Variance $\sigma_\phi^2$) ในช่วงความถี่ระหว่าง $f_{min}$ ถึง $f_{max}$ คำนวณได้จาก:

$$\sigma_\phi^2 = 2 \int_{f_{min}}^{f_{max}} 10^{\frac{\mathcal{L}(f)}{10}} \, df \quad \left[\text{rad}^2\right]$$

เมื่อแปลงความแปรปรวนของมุมเฟส $\sigma_\phi$ ให้กลายเป็น RMS Phase Jitter ในโดเมนเวลา ($\sigma_{t}$ หรือ $RJ_{rms}$):

$$\sigma_t = \frac{\sigma_\phi}{2\pi f_0} = \frac{1}{2\pi f_0} \sqrt{2 \int_{f_{min}}^{f_{max}} 10^{\frac{\mathcal{L}(f)}{10}} \, df} \quad \left[\text{วินาที (s)}\right]$$

#### การคำนวณแบบแยกส่วนเชิงเส้นบนสเกลลอการิทึม (Piecewise Log-Linear Integration):
หากกราฟ Phase Noise ประกอบด้วยจุดวัดที่ความถี่ $f_i$ มีค่า $\mathcal{L}_i$ และมีความชัน $a_i = \frac{\mathcal{L}_{i+1} - \mathcal{L}_i}{\log_{10}(f_{i+1}) - \log_{10}(f_i)}\text{ dB/decade}$:
$$\int_{f_i}^{f_{i+1}} 10^{\frac{\mathcal{L}(f)}{10}} df = \begin{cases} 
\frac{10^{\mathcal{L}_i/10}}{f_i^{a_i/10} (a_i/10 + 1)} \left( f_{i+1}^{a_i/10 + 1} - f_i^{a_i/10 + 1} \right) & \text{ถ้า } a_i \neq -10 \\
10^{\mathcal{L}_i/10} f_i \ln\left(\frac{f_{i+1}}{f_i}\right) & \text{ถ้า } a_i = -10 
\end{cases}$$

---

### 1.4 การวิเคราะห์เสถียรภาพลูปและปรากฏการณ์ Jitter Peaking (Loop Stability & Jitter Peaking)

```
        Open-Loop Bode Plot & Phase Margin
        
 Gain (dB)
    ^
 40 |------------------\
    |                   \
 20 |                    \ -20 dB/dec
    |                     \
  0 +----------------------\-------------+---------------------> Frequency
    |                       \            | Unity Gain Frequency (w_u)
-20 |                        \ -40 dB/dec|
    |                         \          |
Phase (deg)                              |
  0 +------------------------------------+--------------------->
    |                  /--------\        |
-90 |-----------------/          \-------+-- Phase at w_u = -130°
    |                                    |<---> Phase Margin PM = 180° - 130° = 50°
-180+---------------------------------------------------------->
```

#### 1.4.1 เสถียรภาพของลูป (Phase Margin & Gain Margin):
ฟังก์ชันถ่ายโอนวงเปิด $G_{open}(s)$ ประกอบด้วย:
* โพลที่จุดกำเนิดสองตัว ($s^2$): หนึ่งตัวจาก Loop Filter Integrator และอีกตัวจาก VCO ($K_{vco}/s$) ส่งผลให้ Phase Lag เริ่มต้นที่ $-180^\circ$
* ซีโร่สร้างเสถียรภาพ (Stabilizing Zero): $\omega_z = \frac{1}{R_1 C_1}$ ดึงเฟสกลับขึ้นมา $+90^\circ$
* โพลความถี่สูง (High-Frequency Pole): $\omega_{p2} \approx \frac{1}{R_1 C_2}$ กดริปเปิลความถี่สูง

**Phase Margin ($\phi_m$):**
$$\phi_m = 180^\circ + \angle G_{open}(j\omega_u) \approx \arctan\left(\frac{\omega_u}{\omega_z}\right) - \arctan\left(\frac{\omega_u}{\omega_{p2}}\right)$$
โดยที่ $\omega_u$ คือ Unity Gain Crossover Frequency ($|G_{open}(j\omega_u)| = 1 = 0\text{ dB}$)
* **เกณฑ์ความปลอดภัยวิศวกรรม:** $45^\circ \le \phi_m \le 70^\circ$ (จุดเหมาะสมที่สุดคือ $\phi_m \approx 60^\circ$ ให้ Damping Factor $\zeta \approx 0.707$)
* หาก $\phi_m < 35^\circ$: ลูปจะเกิดการแกว่ง (Severe Ringing) และเกิด **Jitter Peaking** มหาศาล!

#### 1.4.2 อันตรายของการต่อ PLL อนุกรมกัน (Cascaded PLL Jitter Peaking Hazard):
เมื่อฟังก์ชันถ่ายโอนวงปิด $H(s)$ มีค่า Damping Factor ต่ำ ($\zeta < 1.0$) กราฟการตอบสนองความถี่จะเกิดยอดแหลมที่เรียกว่า Jitter Peaking ($M_p$):

$$M_p = |H(j\omega)|_{max} = \frac{1}{2\zeta \sqrt{1 - \zeta^2}} \quad (\text{เมื่อ } \zeta < 0.707)$$

```
     Closed-Loop Transfer Function & Jitter Peaking Danger
     
 |H(jw)| (dB)
    ^
+6dB|                        /---\  <-- Jitter Peaking Peak (Mp)
+3dB|                       /     \     (Amplifies Reference Noise!)
 0dB+----------------------/       \---------------------------> Frequency
    |                               \
-3dB|                                \  -3dB Cutoff Bandwidth
-6dB|                                 \
    |                                  \
```

เมื่อนำ PLL สองตัวมาต่ออนุกรมกัน (PLL-1 ขับ PLL-2):
$$H_{cascade}(s) = H_1(s) \cdot H_2(s)$$
$$|H_{cascade}(j\omega)|_{dB} = |H_1(j\omega)|_{dB} + |H_2(j\omega)|_{dB}$$

> [!CAUTION]
> หาก PLL ตัวที่ 1 และ PLL ตัวที่ 2 มีแบนด์วิดท์ใกล้เคียงกัน ยอด Peaking จะบวกกันทางคณิตศาสตร์!  
> ตัวอย่างเช่น หากตัวแรกมี Peaking $+3.0\text{ dB}$ และตัวที่สองมี Peaking $+3.0\text{ dB}$ รวมกันเป็น **$+6.0\text{ dB}$** สัญญาณรบกวนที่ความถี่นั้นจะถูกขยายขึ้น **$200\%$ ($2$ เท่าตัว!)**  
> **กฎเหล็กวิศวกรรม (Golden Rule):** แบนด์วิดท์ของลูปที่สองต้องห่างจากลูปแรกอย่างน้อย 1 ทศวรรษ ($BW_2 \le 0.1 \cdot BW_1$ หรือ $BW_2 \ge 10 \cdot BW_1$) เสมอ!

---

### 1.5 กลไกการแทรกซึมของสัญญาณรบกวนจากภาคจ่ายไฟ (PSRR Physics)
VCO ภายใน FPGA ถูกจ่ายไฟจากเรล $V_{CCAUX}$ หรือ $V_{CC\_PLL}$ สัญญาณรบกวนบนรางไฟเลี้ยง ($\Delta V_{dd}(t)$) จะเปลี่ยนค่าความจุไฟฟ้าแฝงของ Varactor ในออสซิลเลเตอร์ ทำให้เกิดความถี่แปรปรวนโดยตรง:

$$\Delta f_{vco}(t) = K_{vco\_psrr} \cdot \Delta V_{dd}(t)$$

เมื่อสัญญาณริปเปิลจาก Switching Power Supply (เช่น Buck Converter ความถี่ $1.2\text{ MHz}$) ป้อนเข้ามา:
$$\Delta V_{dd}(t) = V_{rip} \sin(2\pi f_{sw} t)$$
จะก่อให้เกิด Deterministic Periodic Jitter (PJ):
$$J_{PJ,pp} = \frac{K_{vco\_psrr} \cdot V_{rip}}{\pi f_0 f_{sw}}$$
หากความถี่สวิตชิ่ง $f_{sw}$ ไปตรงกับจุด Jitter Peaking ของ PLL พอดี สัญญาณรบกวนจะถูกขยายจนทำลาย Eye Diagram ในทันที!

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** การ์ดส่งสัญญาณเครือข่ายความเร็วสูง 10GbE SFP+ (10.3125 Gbps) บน FPGA Xilinx Kintex-7 (XC7K325T) ตกมาตรฐานการวัดความคลาดเคลื่อนบิต (Bit Error Rate Test: BERT) ที่โรงงานลูกค้า โดยมีค่า $BER = 1.2 \times 10^{-6}$ (มาตรฐานสากลบังคับ $BER \le 1.0 \times 10^{-12}$)

เมื่อตรวจสอบกราฟ Eye Diagram บน Real-Time Oscilloscope 25GHz พบว่าตามีการหรี่แคบลงอย่างรุนแรง (Eye Height เหลือ $65\text{ mV}$, Eye Width เหลือ $0.22\text{ UI}$) สัญญาณ Jitter มีลักษณะการสั่นสะเทือนแบบฮาร์มอนิกอย่างเด่นชัด

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] ลิงก์ SerDes 10.3125 Gbps เกิด BER สูงถึง 10^-6 (Eye Diagram ปิดตัวลง)
      |
      +---> [Why 1] ทำไม Eye Diagram ถึงแคบลงจนเปิดได้เพียง 0.22 UI?
      |             --> เพราะ Total Jitter (TJ) สูงถึง 75.6 ps (สเปกยอมรับได้ไม่เกิน 28 ps)
      |
      +---> [Why 2] ทำไม Total Jitter ถึงสูงผิดปกติ?
      |             --> เพราะมี Deterministic Periodic Jitter (PJ) ขนาด 42 ps ซ้อนทับอยู่บนความถี่ 1.5 MHz
      |
      +---> [Why 3] ทำไมจึงเกิดสไปก์ PJ ที่ความถี่ 1.5 MHz?
      |             --> เพราะเกิด Jitter Peaking ขยายสัญญาณรบกวนในระบบสัญญาณนาฬิกา
      |
      +---> [Why 4] ทำไมจึงเกิด Jitter Peaking ขยายตัวที่ 1.5 MHz?
      |             --> ผู้ออกแบบนำ MMCM ตัวแรก (สร้าง System Clock 156.25 MHz) ไปขับ GTX Transceiver PLL ตัวที่สอง
      |                 โดยทั้งสองตัวถูกตั้งค่า Loop Bandwidth ไว้ที่ ~1.5 MHz เท่ากันพอดี!
      |
      +---> [Why 5 - Root Cause] ทำไมสัญญาณรบกวน 1.5 MHz ถึงมีระดับความแรงสูงตั้งแต่ต้น?
                    --> เพราะวงจร Buck Converter 1.8V จ่ายไฟให้ VCCAUX ทำงานที่ Switching Frequency 1.5 MHz
                        โดย PCB ขาด Ferrite Bead กรองไฟ และตัวเหนี่ยวนำขนานกับตัวเก็บประจุเกิด Anti-Resonance
                        ที่ 1.5 MHz พอดี ทำให้ริปเปิล 35 mVpp แทรกซึมเข้าสู่ VCO โดยตรง!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการเกิด BER 10^-6 บนอินเตอร์เฟซ SerDes 10.3125 Gbps

   CIRCUIT TOPOLOGY (Cascaded PLL)            POWER INTEGRITY (Power Supply)
         |                                          |
   ต่อ MMCM และ GTX PLL อนุกรมกัน                    Buck Converter สวิตช์ที่ความถี่ 1.5 MHz
         \                                          /
          \   Bandwidth ชนกันที่ 1.5 MHz           /   ริปเปิลไฟ VCCAUX สูงถึง 35 mVpp
           \   Peaking บวกกัน +7.2 dB             /   ขาด Ferrite Bead กรองความถี่สูง
            +------------------------------------+
            |                                    |
            |   SERDES 10G EYE CLOSURE & HIGH    |===> [CRITICAL BER FAILURE]
            |   TOTAL JITTER (TJ = 75.6 ps)      |
            +------------------------------------+
           /                                      \
          /   ใช้โหมด "HIGH" Bandwidth โดยไม่จำเป็น \   วัดเฉพาะความถี่ ไม่เคยวัด TIE Jitter
         /                                          \
   ขาดวงจร CDR Filter ในการซิมูเลชัน                   ละเลยการสแกน Phase Noise Mask
         |                                          |
   DESIGN METHODOLOGY                         TEST & MEASUREMENT
```

---

### แนวทางแก้ไขเชิงปฏิบัติการ (Actionable Solutions & Design Fixes)

```
                 การแก้ไขสถาปัตยกรรมนาฬิกาและการแยกแบนด์วิดท์ (Decoupling)
                 
 [เดิม: เกิด Jitter Peaking หายนะ]
 156.25MHz Ref ---> [ MMCM (BW = 1.5MHz) ] ===> [ GTX PLL (BW = 1.5MHz) ] ---> TX Eye ปิดสนิท!
                         (Peaking +3.5dB)            (Peaking +3.7dB)           Total Peaking = +7.2dB!
 
 [แก้ไข: ขับตรงผ่าน Dedicated Clock Pin และแยกแบนด์วิดท์]
 156.25MHz Ref ---> [ MGTREFCLK Pin ] ---------> [ GTX PLL (BW = 2.0MHz) ] ---> TX Eye กว้าง 0.75 UI!
                           |
                           v (ทางแยก)
                    [ MMCM (BW = 200kHz) ] (ลด Bandwidth ลง 1 Decade เพื่อใช้กับ Internal Fabric)
```

#### การแก้ไข 3 จุดวิกฤต:
1. **Clock Routing Bypass:** ยกเลิกการต่อ Cascading ที่นำสัญญาณออกจาก MMCM เข้า GTX Transceiver โดยเปลี่ยนมาป้อน Reference Clock จากออสซิลเลเตอร์ภายนอกเข้าสู่ขา `MGTREFCLK0P/N` ของ GTX Transceiver โดยตรงผ่านบัฟเฟอร์ `IBUFDS_GTE2`
2. **Bandwidth De-tuning:** หากจำเป็นต้องต่อผ่าน MMCM ให้ตั้งค่าแอตทริบิวต์ `BANDWIDTH = "LOW"` บน MMCM เพื่อบีบ Loop Bandwidth ให้ต่ำลงเหลือ $< 200\text{ kHz}$ ซึ่งห่างจาก GTX PLL ($2\text{ MHz}$) เกิน 1 Decade เพื่อตัดยอด Peaking ทิ้ง
3. **Power Filter Optimization:** ติดตั้ง Murata BLM18PG Ferrite Bead ($120\ \Omega\text{ @ }100\text{ MHz}$) คั่นที่รางไฟ $V_{CCAUX}$ และเปลี่ยนตัวเก็บประจุดีคัปปลิงเป็น $0.1\ \mu\text{F}$ (0402 X7R) ขนานกับ $10\ \mu\text{F}$ (0603 X5R) เพื่อกำจัดริปเปิล $1.5\text{ MHz}$ ให้เหลือต่ำกว่า $3.0\text{ mVpp}$

---

### ข้อกำหนด XDC Constraints และ SOP สำหรับการล็อก Timing Jitter

```tcl
# ==============================================================================
# XDC TIMING CONSTRAINTS: INJECTING ACCURATE JITTER & CLOCK UNCERTAINTY
# ==============================================================================

# 1. กำหนดสัญญาณนาฬิกาหลักจาก Ultra-Low Jitter Oscillator
create_clock -period 6.400 -name clk_mgtref -waveform {0.000 3.200} [get_ports mgtrefclk_p]

# 2. จำลอง Random Jitter และ Deterministic Jitter จากภาคจ่ายไฟจริงลงในโมเดล STA
# ตั้งค่า Input Jitter ดิบที่วัดได้จาก Oscilloscope (TJ = 15 ps)
set_input_jitter [get_clocks clk_mgtref] 0.015

# 3. กำหนดค่า System Jitter ประจำตัวของบอร์ด (Power Supply Noise Margin = 30 ps)
set_system_jitter 0.030

# 4. บังคับ Attribute บน MMCM เพื่อป้องกัน Vivado ปรับจูน Bandwidth แบบอัตโนมัติ
# บังคับใช้โหมด LOW Bandwidth เพื่อกำจัด Jitter Peaking
# set_property BANDWIDTH LOW [get_cells u_clk_gen/inst/mmcm_adv_inst]
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันジ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| 位相雑音 | いそうざつおん | Isō Zatsuon | สัญญาณรบกวนเฟส (Phase Noise: $\mathcal{L}(f)$) |
| 周期ジッタ | しゅうきじった | Shūki Jitta | จิตเตอร์แบบคาบเวลา (Period Jitter) |
| サイクル間ジッタ | さいくるかんじった | Saikuru-kan Jitta | จิตเตอร์ระหว่างคาบติดกัน (Cycle-to-Cycle Jitter) |
| 時間間隔誤差 | じかんかんかくごさ | Jikan Kankaku Gosa | ความคลาดเคลื่อนช่วงเวลา (Time Interval Error: TIE) |
| 多段接続 | ただんせつぞく | Tadan Setsuzoku | การต่อวงจรแบบอนุกรมลดหลั่น (Cascading) |
| ジッタピーキング | じったぴーきんぐ | Jitta Pīkingu | ปรากฏการณ์ยอดจิตเตอร์พุ่งสูงเกินจริง (Jitter Peaking) |
| 位相余裕 | いそうよゆう | Isō Yoyū | มาร์จินของมุมเฟส (Phase Margin: $\phi_m$) |
| 利得余裕 | りとくよゆう | Ritoku Yoyū | มาร์จินของอัตราขยาย (Gain Margin) |
| 電源変動抑圧 | でんげんへんどうよくあつ | Dengen Hendō Yokuatsu | การลดทอนความแปรปรวนจากไฟเลี้ยง (PSRR) |
| アイ開口度 | あいかいこうど | Ai Kaikōdo | ระดับการเปิดของดวงตา (Eye Opening Width/Height) |
| 符号間干渉 | ふごうかんかんしょう | Fugōkan Kanshō | สัญญาณรบกวนระหว่างสัญลักษณ์ข้อมูล (ISI) |
| 帯域分離 | たいいきぶんり | Taiiki Bunri | การแยกแบนด์วิดท์ไม่ให้ชนกัน (Bandwidth Separation) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการต่อ Cascaded PLL ที่เสี่ยงเกิด Jitter Peaking
**สถานที่:** ศูนย์วิจัยและพัฒนาผลิตภัณฑ์เครือข่ายความเร็วสูง (High-Speed Telecom R&D Center)  
**ผู้เข้าร่วม:** Chief Signal Integrity Specialist (หัวหน้าผู้เชี่ยวชาญด้าน SI/PI) และ Hardware Designer (วิศวกรฮาร์ดแวร์)

* **Chief Specialist:**  
  「このクロックツリーのブロック図を見てくれ。外部の156.25MHzをファブリック用MMCMに入れて、その出力をさらにGTXトランシーバのCPLLに突っ込んでいるな。これは完全な設計ミスだ。MMCMのループ帯域とGTX CPLLの帯域がどちらも約1.5MHz付近に設定されている。両者のジッタピーキングが重なって、トランシーバのアイパターンを直撃して閉じてしまうぞ。なぜ外部クロックをトランシーバ専用ピン（MGTREFCLK）へ直接配線しなかったんだ？」  
  *(Kono kurokku tsurī no burokku-zu o mite kure. Gaibu no 156.25MHz o faburikku-yō MMCM ni irete, sono shutsuryoku o sara ni GTX toranshība no CPLL ni tsukkonde iru na. Kore wa kanzenna sekkei misu da. MMCM no rūpu taiiki to GTX CPLL no taiiki ga dochira mo yaku 1.5MHz fukin ni settei sarete iru. Ryōsha no jitta pīkingu ga kasanatte, toranshība no ai patān o chokugeki shite tojite shimau zo. Naze gaibu kurokku o toranshība sen'yō pin (MGTREFCLK) e chokusetsu haisen shinakatta n da?)*  
  **ความหมาย:** "ดูบล็อกไดอะแกรมของ Clock Tree ตัวนี้หน่อย คุณเอาสัญญาณภายนอก 156.25MHz ป้อนเข้า MMCM ของ Fabric แล้วเอาต์พุตดันวิ่งต่อไปเข้า CPLL ของตัวส่ง GTX Transceiver อีกทอด นี่มันความผิดพลาดในการออกแบบชัดๆ! แบนด์วิดท์ของ MMCM กับของ GTX CPLL ดันตั้งไว้ใกล้กันที่ราวๆ 1.5MHz ทั้งคู่ แบบนี้ Jitter Peaking ของสองตัวมันจะซ้อนทับกันแล้วยิงตรงเข้าปิด Eye Pattern ของตัวรับส่งข้อมูลจนบอดสนิท! ทำไมถึงไม่เดินสาย Reference ภายนอกตรงเข้าขาเฉพาะของ Transceiver (MGTREFCLK)?"

* **Hardware Designer:**  
  「ピン配置の都合で、基板上のクロック発振器を減らしてコストダウンを図るため、MMCMでファンアウトして共用しようと考えてしまいました。ピーキングの加算効果（累積）について考慮が及んでいませんでした。」  
  *(Pin haichi no tsugō de, kibanjō no kurokku hasshinki o herashite kosuto daun o hakaru tame, MMCM de fan'auto shite kyōyō shiyō to kangaete shimaimashita. Pīkingu no kasan kōka (ruiseki) ni tsuite kōryo ga oyonde imasen deshita.)*  
  **ความหมาย:** "เป็นเพราะข้อจำกัดเรื่องพินและต้องการลดจำนวน Oscillator บนบอร์ดเพื่อประหยัดต้นทุนครับ ผมเลยกะว่าจะใช้ MMCM ขยายสัญญาณแล้วจ่ายพ่วงกัน ไม่ทันได้เฉลียวใจถึงผลกระทบของการสะสมของ Jitter Peaking ครับ"

* **Chief Specialist:**  
  「コストダウンのために10GリンクのBERが全滅したら本末転倒だ！多段接続（カスケード）する場合は、最低でも帯域幅を1ディケード（10倍）離すのが鉄則だ。だが今回はSerDesのジッタ要件が厳格だから、MGT専用の超低ジッタ発振器（RJ < 300fs）から直接専用差動ピンへ引き込み直せ。基板改版（リビジョンアップ）のパターン変更指示書を直ちに作成すること。」  
  *(Kosuto daun no tame ni 10G rinku no BER ga zenmetsu shitara hommatsutentō da! Tadan setsuzoku (kasukēdo) suru baai wa, saitei demo taiikihaba o 1 dikēdo (10-bai) hanasu no ga tessoku da. Daga konkai wa SerDes no jitta yōken ga genkakuda kara, MGT sen'yō no chō-tei jitta hasshinki (RJ < 300fs) kara chokusetsu sen'yō sadō pin e hikikominaose. Kiban kaihan (ribijon'appu) no patān henkō指示書 o tadachini sakusei suru koto.)*  
  **ความหมาย:** "เพื่อลดต้นทุนแต่ทำให้ BER ของลิงก์ 10G พังพินาศหมด มันคือการจับแพะชนแกะชัดๆ! หากจำเป็นต้องต่อแบบ Cascading กฎเหล็กคือต้องแยกแบนด์วิดท์ให้ห่างกันอย่างน้อย 1 Decade (10 เท่า) แต่งานนี้ข้อกำหนด Jitter ของ SerDes มันโหดมาก ให้เดินสายตรงจาก Ultra-Low Jitter Oscillator (RJ < 300fs) เข้าขา Differential เฉพาะของ MGT โดยตรงทันที รีบทำเอกสารสั่งแก้ลายวงจรบนบอร์ด (PCB Revision Update) มาเดี๋ยวนี้!"

---

#### สถานการณ์ที่ 2: การตรวจสอบสัญญาณรบกวนบนรางไฟเลี้ยง VCCAUX (Power Supply Noise Inspection)
* **Chief Specialist:**  
  「もう一つ見逃せない点がある。スイッチング電源のスイッチング周波数が1.5MHzだが、VCCAUX端子直近でプロービングしたリップル波形が35mVppもあるぞ。電源のスイッチングノイズがVCOの感度特性（$K_{psrr}$）に乗って周期ジッタ（PJ）を生成している。なぜフェライトビーズと0.1uFの高周波パスコンをBGA直下に配置しなかった？」  
  *(Mō hitotsu minogasenai ten ga aru. Suitchingu dengen no suitchingu shūhasū ga 1.5MHz da ga, VCCAUX tanshi chokkin de purōbingu shita rippuru hakei ga 35mVpp mo aru zo. Dengen no suitchingu noizu ga VCO no kando tokusei (K_psrr) ni notte shūki jitta (PJ) o seisei shite iru. Naze feraito bīzu to 0.1uF no kōshūha pasukon o BGA chokka ni haichi shinakatta?)*  
  **ความหมาย:** "ยังมีอีกจุดที่จะปล่อยผ่านไปไม่ได้ ความถี่สวิตชิ่งของเรกูเลเตอร์คือ 1.5MHz แต่พอเอาโพรบวัดริปเปิลชิดขา VCCAUX ดันพบสูงถึง 35mVpp สัญญาณรบกวนจากสวิตชิ่งมันวิ่งผ่านเกนความไวของ VCO ($K_{psrr}$) แล้วแปลงเป็น Periodic Jitter เต็มๆ ทำไมไม่ใส่ Ferrite Bead กับ Capacitor กรองความถี่สูง 0.1uF ไว้ใต้ท้อง BGA?"

* **Hardware Designer:**  
  「裏面のパスコン配置スペースが配線密集で厳しかったため、少し離れた場所にまとめて置いてしまいました。」  
  *(Uramen no pasukon haichi supēsu ga haisen misshū de kibishikatta tame, sukoshi hanareta basho ni matomete oite shimaimashita.)*  
  **ความหมาย:** "พื้นที่ใต้ท้อง BGA ด้านหลังมีรอยต่อสายสัญญาณแน่นมากครับ ผมเลยขยับตัวเก็บประจุดีคัปปลิงออกไปวางรวมกันห่างออกไปหน่อยครับ"

* **Hardware Specialist:**  
  「離れたパスコンは寄生インダクタンスのせいで1.5MHz以上の高周波では全く無意味だ。リップルを5mVpp以下に抑え込めなければ検図の承認（サインオフ）は出せないぞ。BGA裏面のビア配置を見直し、0402コンデンサを直下最短で再配置しろ。」  
  *(Hanareta pasukon wa kisei indakutansu no sei de 1.5MHz ijō no kōshūha de wa mattaku muimi da. Rippuru o 5mVpp ika ni osaekomenakereba kenzu no shōnin (sain'ofu) wa dasenai zo. BGA uramen no bia haichi o minaoshi, 0402 kondensa o chokka saitan de sai-haichi shiro.)*  
  **ความหมาย:** "ตัวเก็บประจุที่วางห่างออกไป มันจะหมดประโยชน์โดยสิ้นเชิงที่ความถี่สูงเกิน 1.5MHz เพราะค่า Parasitic Inductance ของลายทองแดง! ถ้ากดริปเปิลลงต่ำกว่า 5mVpp ไม่ได้ ผมไม่อนุมัติ Sign-off แบบนี้เด็ดขาด จงรื้อการวางเวียบอร์ดใต้ BGA แล้วยัด C ขนาด 0402 ลงไปชิดขาที่สุดเดี๋ยวนี้!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณการแปลง Phase Noise เป็น RMS Phase Jitter และ Total Jitter (Phase Noise Integration & Dual-Dirac Math)
ในระบบสื่อสารอวกาศ Deep Space Downlink ความถี่สัญญาณนาฬิกาพาหะ $f_0 = 500.0\text{ MHz}$ ($T_0 = 2.0\text{ ns}$) วิศวกรใช้ Spectrum Analyzer บันทึกเส้นโค้ง Phase Noise ($\mathcal{L}(f)$) ของ Ultra-Low Phase Noise MMCM ได้ข้อมูลดังต่อไปนี้:
* ที่ออฟเซต $10\text{ kHz}$ ถึง $100\text{ kHz}$: ความชันสม่ำเสมอ $-20\text{ dB/dec}$, โดยที่ $\mathcal{L}(10\text{ kHz}) = -90.0\text{ dBc/Hz}$ และ $\mathcal{L}(100\text{ kHz}) = -110.0\text{ dBc/Hz}$
* ที่ออฟเซต $100\text{ kHz}$ ถึง $1.0\text{ MHz}$: ความชันสม่ำเสมอ $-20\text{ dB/dec}$, โดยที่ $\mathcal{L}(1.0\text{ MHz}) = -130.0\text{ dBc/Hz}$
* ที่ออฟเซต $1.0\text{ MHz}$ ถึง $10.0\text{ MHz}$: พื้นราบคงที่ (White Phase Noise Floor) $\mathcal{L}(f) = -140.0\text{ dBc/Hz}$

หากระบบมี Deterministic Jitter จากลายวงจรและ ISI บนบอร์ด $DJ_{\delta\delta} = 12.0\text{ ps}$  
จงคำนวณหา:
1. ค่า RMS Phase Jitter ($\sigma_t$ หรือ $RJ_{rms}$) จากการรวมพลังงานในช่วงออฟเซต $10\text{ kHz}$ ถึง $10\text{ MHz}$
2. ค่า Total Jitter ($TJ$) ที่ข้อกำหนด $BER = 10^{-12}$ ($Q \approx 7.034$, ตัวคูณ $2Q \approx 14.069$)

จงเลือกคำตอบที่ถูกต้องที่สุด:

A) $RJ_{rms} \approx 0.45\text{ ps}, \quad TJ(10^{-12}) \approx 18.33\text{ ps}$  
B) $RJ_{rms} \approx 1.42\text{ ps}, \quad TJ(10^{-12}) \approx 31.98\text{ ps}$  
C) $RJ_{rms} \approx 2.85\text{ ps}, \quad TJ(10^{-12}) \approx 52.10\text{ ps}$  
D) $RJ_{rms} \approx 4.50\text{ ps}, \quad TJ(10^{-12}) \approx 75.31\text{ ps}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: อินทิเกรต Phase Noise ทีละย่านความถี่ (Piecewise Integration)**
สูตรอินทิเกรตสำหรับย่านที่มีความชัน $a = -20\text{ dB/dec}$ (นั่นคือ $10^{\mathcal{L}(f)/10} = K / f^2$):
$$\int_{f_1}^{f_2} \frac{K}{f^2} df = K \left[ -\frac{1}{f} \right]_{f_1}^{f_2} = K \left( \frac{1}{f_1} - \frac{1}{f_2} \right)$$
โดยที่ $K = 10^{\mathcal{L}(f_1)/10} \cdot f_1^2$

* **ย่านที่ 1: $10\text{ kHz}$ ถึง $100\text{ kHz}$**
  $f_1 = 10^4\text{ Hz}, \quad \mathcal{L}(f_1) = -90\text{ dBc/Hz} \implies 10^{-9}$
  $K_1 = 10^{-9} \times (10^4)^2 = 10^{-9} \times 10^8 = 0.1$
  $$I_1 = \int_{10^4}^{10^5} 10^{\mathcal{L}/10} df = 0.1 \times \left( \frac{1}{10^4} - \frac{1}{10^5} \right) = 0.1 \times \left( 10^{-4} - 10^{-5} \right) = 0.1 \times 9 \times 10^{-5} = 9.0 \times 10^{-6}\text{ rad}^2$$

* **ย่านที่ 2: $100\text{ kHz}$ ถึง $1\text{ MHz}$**
  $f_2 = 10^5\text{ Hz}, \quad \mathcal{L}(f_2) = -110\text{ dBc/Hz} \implies 10^{-11}$
  $K_2 = 10^{-11} \times (10^5)^2 = 10^{-11} \times 10^{10} = 0.1$
  $$I_2 = \int_{10^5}^{10^6} 10^{\mathcal{L}/10} df = 0.1 \times \left( \frac{1}{10^5} - \frac{1}{10^6} \right) = 0.1 \times 9 \times 10^{-6} = 9.0 \times 10^{-7}\text{ rad}^2$$

* **ย่านที่ 3: $1\text{ MHz}$ ถึง $10\text{ MHz}$ (White Noise Floor $a = 0$)**
  $\mathcal{L}(f) = -140\text{ dBc/Hz} \implies 10^{-14}$
  $$I_3 = \int_{10^6}^{10^7} 10^{-14} df = 10^{-14} \times (10^7 - 10^6) = 10^{-14} \times 9 \times 10^6 = 9.0 \times 10^{-8}\text{ rad}^2$$

**ขั้นตอนที่ 2: คำนวณความแปรปรวนเฟสรวม $\sigma_\phi^2$**
$$\sigma_\phi^2 = 2 \cdot (I_1 + I_2 + I_3) = 2 \cdot (9.0 \times 10^{-6} + 0.9 \times 10^{-6} + 0.09 \times 10^{-6}) = 2 \cdot (9.99 \times 10^{-6}) \approx 1.998 \times 10^{-5}\text{ rad}^2$$
$$\sigma_\phi = \sqrt{1.998 \times 10^{-5}} \approx 4.47 \times 10^{-3}\text{ rad}$$

**ขั้นตอนที่ 3: แปลงเป็น RMS Phase Jitter ($\sigma_t$)**
$$f_0 = 500 \times 10^6\text{ Hz} \implies 2\pi f_0 = 2\pi \times 500 \times 10^6 = \pi \times 10^9 \approx 3.14159 \times 10^9\text{ rad/s}$$
$$\sigma_t = \frac{\sigma_\phi}{2\pi f_0} = \frac{4.47 \times 10^{-3}}{3.14159 \times 10^9} \approx 1.4228 \times 10^{-12}\text{ s} \approx 1.42\text{ ps}$$

**ขั้นตอนที่ 4: คำนวณ Total Jitter ($TJ$) ด้วย Dual-Dirac Model**
$$TJ(10^{-12}) = DJ_{\delta\delta} + 2 \cdot Q(10^{-12}) \cdot RJ_{rms}$$
$$TJ(10^{-12}) = 12.0\text{ ps} + (14.069 \times 1.42\text{ ps}) = 12.0\text{ ps} + 19.98\text{ ps} \approx 31.98\text{ ps}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **B** ($RJ_{rms} \approx 1.42\text{ ps}, TJ \approx 31.98\text{ ps}$) สอดคล้องกับผลการคำนวณอย่างแม่นยำ

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะลืมคูณเลข 2 หน้าอินทิกรัลสำหรับ Double-Sided Sidebands ทำให้ค่าความแปรปรวนต่ำกว่าจริงครึ่งหนึ่ง
* ข้อ C ผิด เพราะใช้สูตร $2\pi f_0$ สลับกับ $f_0$ ทำให้ค่า Jitter สูงเกินจริงไป $\approx 2$ เท่า
* ข้อ D ผิด เพราะนำค่า Peak-to-Peak ของ Random Jitter มาบวกตรงๆ โดยไม่ใช้ตัวคูณ $Q(BER)$

---

### คำถามที่ 2: การคำนวณการขยายตัวของ Jitter Peaking ใน Cascaded PLL (Cascaded Peaking Penalty on High-Speed Serial Link)
ในระบบเครือข่ายใยแก้วนำแสง $10.3125\text{ Gbps}$ ($1\text{ UI} \approx 96.97\text{ ps}$) สัญญาณนาฬิกาถูกสร้างผ่าน PLL 2 ตัวต่ออนุกรมกัน:
* **PLL-1 (System Clock Tile):** มี Damping Factor $\zeta_1 = 0.50$
* **PLL-2 (SerDes Transceiver Core):** มี Damping Factor $\zeta_2 = 0.55$

ทั้งสองลูปมีอัตราขยายยอดแหลม Jitter Peaking ตามสมการฟิสิกส์:
$$M_p = \frac{1}{2\zeta \sqrt{1 - \zeta^2}}$$
หากสัญญาณนาฬิกาอินพุตของ PLL-1 มีสัญญาณรบกวน Deterministic Sinusoidal Jitter ปนเปื้อนมาที่ความถี่เรโซแนนซ์เท่ากับ $A_{in} = 2.0\text{ ps}$  
จงคำนวณหา:
1. อัตราขยาย Jitter Peaking รวม ($M_{p,total} = M_{p1} \cdot M_{p2}$)
2. ขนาดของ Jitter เอาต์พุตที่ถูกขยาย ($A_{out}$)
3. สัดส่วนการปิดของ Data Eye Diagram ที่เพิ่มขึ้นอันเนื่องมาจาก Cascaded Peaking ในหน่วยเปอร์เซ็นต์ของ Unit Interval ($\% \text{UI}$)

A) $M_{p,total} \approx 1.15\text{ เท่า}, \quad A_{out} \approx 2.30\text{ ps}, \quad \text{Eye Closure} \approx 2.37\% \text{ UI}$  
B) $M_{p,total} \approx 1.45\text{ เท่า}, \quad A_{out} \approx 2.90\text{ ps}, \quad \text{Eye Closure} \approx 2.99\% \text{ UI}$  
C) $M_{p,total} \approx 1.25\text{ เท่า}, \quad A_{out} \approx 2.50\text{ ps}, \quad \text{Eye Closure} \approx 2.58\% \text{ UI}$  
D) $M_{p,total} \approx 1.25 \times 1.09 \approx 1.36\text{ เท่า}, \quad A_{out} \approx 2.72\text{ ps}, \quad \text{Eye Closure} \approx 2.80\% \text{ UI}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณ $M_{p1}$ สำหรับ PLL-1 ($\zeta_1 = 0.50$)**
$$\sqrt{1 - \zeta_1^2} = \sqrt{1 - 0.25} = \sqrt{0.75} \approx 0.8660$$
$$2\zeta_1 \sqrt{1 - \zeta_1^2} = 2 \times 0.50 \times 0.8660 = 0.8660$$
$$M_{p1} = \frac{1}{0.8660} \approx 1.1547 \quad (\approx +1.25\text{ dB})$$

**ขั้นตอนที่ 2: คำนวณ $M_{p2}$ สำหรับ PLL-2 ($\zeta_2 = 0.55$)**
$$\sqrt{1 - \zeta_2^2} = \sqrt{1 - 0.3025} = \sqrt{0.6975} \approx 0.83516$$
$$2\zeta_2 \sqrt{1 - \zeta_2^2} = 2 \times 0.55 \times 0.83516 = 1.10 \times 0.83516 \approx 0.91868$$
$$M_{p2} = \frac{1}{0.91868} \approx 1.0885 \quad (\approx +0.74\text{ dB})$$

**ขั้นตอนที่ 3: คำนวณอัตราขยายรวม $M_{p,total}$ และขนาด Jitter เอาต์พุต $A_{out}$**
$$M_{p,total} = M_{p1} \times M_{p2} = 1.1547 \times 1.0885 \approx 1.2569 \approx 1.26\text{ เท่า}$$
$$A_{out} = A_{in} \times M_{p,total} = 2.0\text{ ps} \times 1.2569 \approx 2.514\text{ ps} \approx 2.50\text{ ps}$$

**ขั้นตอนที่ 4: คำนวณ Eye Closure Penalty เทียบกับ UI**
ความกว้างของ Unit Interval:
$$UI = \frac{1}{10.3125 \times 10^9\text{ Hz}} \approx 96.97\text{ ps}$$
ผลกระทบของ Sinusoidal Jitter แบบ Peak-to-Peak:
$$DJ_{pp} = 2 \cdot A_{out} = 2 \times 2.514\text{ ps} = 5.028\text{ ps} \quad \text{หรือคิดเป็นแอมพลิจูดเดี่ยว} \ A_{out} / UI \approx 2.514 / 96.97 \approx 2.59\%$$
หากคิดการสูญเสียของ Eye จาก Jitter ที่เพิ่มขึ้นโดยตรง:
$$\Delta \text{Eye} = \frac{2.514\text{ ps}}{96.97\text{ ps}} \times 100\% \approx 2.59\% \text{ UI}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **C** ($M_{p,total} \approx 1.25\text{ เท่า}, A_{out} \approx 2.50\text{ ps}, \text{Eye Closure} \approx 2.58\%$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะคิดเฉพาะค่า Peaking ของ PLL-1 ตัวเดียว ($M_{p1} \approx 1.15$) โดยลืมนำ PLL-2 มาคูณสะสม
* ข้อ B ผิด เพราะนำค่า Peaking ในหน่วย dB ไปบวกกันแบบเชิงเส้นธรรมดาทำให้ค่าพุ่งสูงเกินจริง
* ข้อ D มีการปัดเศษคลาดเคลื่อนทางคณิตศาสตร์

---

### คำถามที่ 3: การประเมินข้อกำหนด Power Supply Noise และขีดจำกัด Ripple Voltage (PSRR Jitter Budgeting)
ในการออกแบบบอร์ดประมวลผลเครือข่าย 100GbE (4x25Gbps) สัญญาณนาฬิกา $F_0 = 644.53125\text{ MHz}$ งบประมาณสัญญาณรบกวนสุ่มและคงที่ (Total Jitter Budget) ที่จัดสรรให้กับภาคจ่ายไฟ $V_{CCAUX}$ ($1.8\text{V}$) ถูกกำหนดไว้อย่างเข้มงวดว่า:
* สัญญาณรบกวนแบบ Periodic Jitter ($PJ_{pp}$) ที่เกิดจากริปเปิลของ Buck Converter ต้องไม่เกิน **$1.80\text{ ps}_{pp}$**

จากสเปกซิลิคอนของ FPGA:
* ค่าความไวต่อไฟเลี้ยงของ VCO (VCO PSRR Sensitivity): $K_{vco\_psrr} = 25.0\text{ ps / (mV}\cdot\text{s)}$
* ความถี่สวิตชิ่งของสวิตชิ่งเรกูเลเตอร์: $f_{sw} = 2.0\text{ MHz}$
* ความถี่พาหะของสัญญาณนาฬิกา: $f_0 = 644.53125\text{ MHz}$
* สมการความสัมพันธ์ระหว่าง Periodic Jitter กับ Ripple Voltage ($V_{rip}$ ในหน่วย $\text{mV}_{pp}$):
  $$PJ_{pp} = \frac{K_{vco\_psrr} \cdot V_{rip}}{\pi \cdot f_0 \cdot f_{sw}}$$
  (โดยที่ $K_{vco\_psrr}$ ได้รับการ Norm ให้มีมิติสอดคล้องกับเฟสเชิงเวลา: $\Delta t = \frac{K_v \cdot V_{rip}}{\pi f_{sw}}$)

หากสมการวิศวกรรมเฉพาะตัวของ CMT ใน FPGA กำหนดว่า:
$$PJ_{pp} = \frac{V_{rip\ (mV)}}{f_{sw\ (MHz)}} \cdot 0.35 \quad \left[\text{ps}_{pp}\right]$$

จงคำนวณหา:
1. แรงดันริปเปิลสูงสุด ($V_{rip,max}$) ที่ยอมให้เกิดขึ้นได้บนรางไฟ $1.8\text{V } V_{CCAUX}$ ในหน่วย $\text{mV}_{pp}$
2. หากเรกูเลเตอร์ปัจจุบันสร้างริปเปิล $30.0\text{ mV}_{pp}$ จะต้องออกแบบฟิลเตอร์ LC Low-Pass เพื่อลดทอนสัญญาณลงอย่างน้อยกี่เดซิเบล ($\text{dB}$)?

A) $V_{rip,max} \le 10.28\text{ mV}_{pp}, \quad \text{Attenuation} \ge 9.30\text{ dB}$  
B) $V_{rip,max} \le 5.14\text{ mV}_{pp}, \quad \text{Attenuation} \ge 15.32\text{ dB}$  
C) $V_{rip,max} \le 2.57\text{ mV}_{pp}, \quad \text{Attenuation} \ge 21.34\text{ dB}$  
D) $V_{rip,max} \le 1.28\text{ mV}_{pp}, \quad \text{Attenuation} \ge 27.36\text{ dB}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณหาระดับ Ripple Voltage สูงสุดที่ยอมรับได้ ($V_{rip,max}$)**
จากสมการความสัมพันธ์:
$$PJ_{pp} = \frac{V_{rip}}{f_{sw}} \cdot 0.35$$
แทนค่า $PJ_{pp} \le 1.80\text{ ps}_{pp}$ และ $f_{sw} = 2.0\text{ MHz}$:
$$1.80 = \frac{V_{rip,max}}{2.0} \cdot 0.35$$
$$1.80 = V_{rip,max} \cdot 0.175$$
$$V_{rip,max} = \frac{1.80}{0.175} \approx 10.2857\text{ mV}_{pp}$$

**ขั้นตอนที่ 2: คำนวณอัตราการลดทอนที่ต้องการ (Filter Attenuation in dB)**
แรงดันริปเปิลเริ่มต้น: $V_{in,rip} = 30.0\text{ mV}_{pp}$  
แรงดันริปเปิลเป้าหมาย: $V_{out,rip} = 10.2857\text{ mV}_{pp}$  
อัตราการลดทอน (Attenuation Ratio):
$$\text{Ratio} = \frac{V_{in,rip}}{V_{out,rip}} = \frac{30.0}{10.2857} \approx 2.9167$$
แปลงเป็นหน่วยเดซิเบล ($\text{dB}$):
$$\text{Attenuation (dB)} = 20 \log_{10}(2.9167) \approx 20 \times 0.4649 \approx 9.298\text{ dB} \approx 9.30\text{ dB}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบที่ถูกต้องคือ **A** ($V_{rip,max} \le 10.28\text{ mV}_{pp}, \text{Attenuation} \ge 9.30\text{ dB}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคิดว่า $PJ$ กำหนดแบบ RMS แทนที่จะเป็น Peak-to-Peak ทำให้หาร 2 เกินความจำเป็น
* ข้อ C และ D ผิด เพราะคำนวณสูตรเดซิเบลแบบ Power ($10\log_{10}$) ปนกับ Voltage ($20\log_{10}$) และตั้งสมมติฐานริปเปิลต่ำเกินจริง
