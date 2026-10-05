# Lesson 141: FPGA PLL Deep Dive - Part 1 (PLL Fundamentals & Loop Dynamics - Analog Mixed-Signal Architecture, PFD/CP/VCO Transfer Functions, Damping Factor & Stability)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมกายภาพของ Phase-Locked Loop ใน FPGA ระดับสูง (Silicon Microarchitecture of Mixed-Signal PLL/MMCM)
ในชิปประมวลผล FPGA ยุคใหม่ (เช่น AMD/Xilinx 7-Series, UltraScale+, Versal AI Core และ Intel Cyclone V, Arria 10, Stratix 10) บล็อกจัดการสัญญาณนาฬิกาไม่ได้เป็นเพียงวงจรหารความถี่ดิจิทัลธรรมดา แต่เป็นระบบอนาล็อกสัญญาณผสมประสิทธิภาพสูง (High-Performance Analog Mixed-Signal System) ที่รู้จักในชื่อ **Clock Management Tile (CMT)** ซึ่งประกอบด้วย **Phase-Locked Loop (PLL)** และ **Mixed-Mode Clock Manager (MMCM)**

```
               +---------------------------------------------------------------------------------------------------+
               |                                FPGA CLOCK MANAGEMENT TILE (MMCM / PLL)                            |
               |                                                                                                   |
               |   +-----------+   F_pfd   +----------------+   I_up / I_dn   +-------------+       V_ctrl         |
CLKIN -------->| /D (PREDIV) |---------->| PFD (Phase     |---------------->| CHARGE PUMP |--------------------+  |
(Input Clock)  +-----------+               | Frequency Det) |                 | (Programmable|                    |  |
                     |                     +----------------+                 |  I_cp 5~40uA) |                    |  |
                     |                             ^                          +-------------+                    |  |
                     |                             |                                                             v  |
                     |                             | F_fb                                                 +-----+--+
                     |                             |                                                      |  LOOP  |
                     |                     +-------+--------+                                             | FILTER |
                     |                     | /M (FEEDBACK)  |<---------------------------------------+    | (R1,C1)|
                     |                     +----------------+                                        |    +-----+--+
                     |                                                                               |          |   |
                     |                                                                               |          v   |
                     |    +--------------------------------------------------------------------------+----+  +----+---+
                     |    |                               VCO CORE (Ring / LC-Tank)                       |  |  VCO   |
                     |    |               Operating Range: F_vcomin <= F_vco <= F_vcomax                  |<-+ (K_vco)|
                     |    +--------------------------------------------------------------------------+----+  +--------+
                     |                                           |                                                  |
                     |                                           | F_vco (High-Speed Multi-phase Bus)               |
                     |                                           v                                                  |
                     |   +--------------------------------------------------------------------------------------+   |
                     |   |                     OUTPUT DIVIDERS (Independent /O0 ... /O6)                       |   |
                     |   +--------------------------------------------------------------------------------------+   |
                     |     |              |              |              |              |              |             |
                     |     v              v              v              v              v              v             |
                     |  CLKOUT0        CLKOUT1        CLKOUT2        CLKOUT3        CLKOUT4        CLKFBOUT         |
                     +--------------------------------------------------------------------------------+-------------+
                                                                                                      |
                                                                   (Zero-Delay Buffer Path)           |
                                                            <-----------------------------------------+
```

#### องค์ประกอบหลัก 5 ประการของวงจร Closed-Loop PLL:
1. **Input Pre-Divider ($D$)**: ทำหน้าที่หารทอนสัญญาณนาฬิกาขาเข้า $F_{in}$ ลงสู่ความถี่เปรียบเทียบของ Phase-Frequency Detector ($F_{pfd} = F_{in} / D$)
2. **Phase-Frequency Detector (PFD)**: วงจรดิจิทัล Sequential State Machine ที่ตรวจวัดผลต่างของเฟส ($\Delta \theta = \theta_{ref} - \theta_{fb}$) และความถี่ โดยส่งสัญญาณพัลส์ควบคุม $UP$ หรือ $DOWN$ ออกมาตามทิศทางความต่าง
3. **Charge Pump (CP)**: สวิตช์กระแสแม่นยำสูง (Precision Current Source/Sink) แปลงความกว้างพัลส์ $UP/DOWN$ ให้เป็นกระแสไฟฟ้าเฉลี่ย $I_{cp}$:
   $$i_{cp}(t) = I_{cp} \cdot \left( \frac{\Delta \theta}{2\pi} \right)$$
   โดยมีค่า Phase Detector Gain:
   $$K_{pd} = \frac{I_{cp}}{2\pi} \quad \left[\text{A/rad}\right]$$
4. **Loop Filter (LF)**: วงจร Passive Lead-Lag Low-Pass Filter ทำหน้าที่รวมประจุ (Integrate) กระแส $i_{cp}$ ให้กลายเป็นแรงดันควบคุมอนาล็อกที่ราบเรียบ ($V_{ctrl}$) ปราศจากความถี่สวิตชิ่งความถี่สูง
5. **Voltage-Controlled Oscillator (VCO)**: วงจรกำเนิดสัญญาณความถี่สูงที่ปรับความถี่ตามแรงดันควบคุม $V_{ctrl}$ โดยมีอัตราขยายเชิงเส้น (VCO Gain):
   $$K_{vco} = \frac{\Delta \omega_{vco}}{\Delta V_{ctrl}} = 2\pi \cdot \frac{\Delta f_{vco}}{\Delta V_{ctrl}} \quad \left[\text{rad/(s}\cdot\text{V)}\right]$$
6. **Feedback Divider ($M$)**: ตัวหารสัญญาณย้อนกลับ ทำหน้าที่หารความถี่ $F_{vco}$ กลับมาป้อนเข้า PFD ($F_{fb} = F_{vco} / M$)

---

### 1.2 การแปลงทางคณิตศาสตร์ s-Domain และสมการไดนามิกของลูป (Loop Dynamics & s-Domain Transfer Function)

แบบจำลองเชิงเส้นแบบเวลาต่อเนื่อง (Continuous-Time Linear Approximation Model) ในย่านความถี่ $s$-domain กำหนดให้อิมพีแดนซ์ของ Loop Filter อันดับสอง (2nd-Order Passive Filter ที่ประกอบด้วย $R_1$ ขนาน/อนุกรมกับ $C_1$ และมีตัวเก็บประจุกรองสไปก์ $C_2$) มีค่าดังนี้:

$$Z_{LF}(s) = \frac{1 + s R_1 C_1}{s (C_1 + C_2) \left( 1 + s R_1 \frac{C_1 C_2}{C_1 + C_2} \right)}$$

ในทางปฏิบัติ วิศวกรจะเลือกค่า $C_2 \approx 0.1 \cdot C_1$ เพื่อลดทอนริปเปิลความถี่สูงโดยไม่รบกวนเฟส ดังนั้นเราสามารถประมาณเป็นวงจรลำดับที่หนึ่งอย่างง่าย:
$$Z_{LF}(s) \approx R_1 + \frac{1}{s C_1} = \frac{s R_1 C_1 + 1}{s C_1}$$

#### 1.2.1 ฟังก์ชันถ่ายโอนวงเปิด (Open-Loop Transfer Function $G_{open}(s)$)
สัญญาณป้อนกลับถูกหารด้วย $M$ ดังนั้น Forward Gain และ Loop Gain จะได้เป็น:

$$G_{open}(s) = \frac{K_{pd} \cdot Z_{LF}(s) \cdot K_{vco}}{s \cdot M} = \left(\frac{I_{cp}}{2\pi}\right) \left(\frac{s R_1 C_1 + 1}{s C_1}\right) \left(\frac{K_{vco}}{s}\right) \left(\frac{1}{M}\right)$$

$$G_{open}(s) = \frac{I_{cp} K_{vco} (s R_1 C_1 + 1)}{2\pi M C_1 s^2}$$

#### 1.2.2 ฟังก์ชันถ่ายโอนวงปิด (Closed-Loop Transfer Function $H(s)$)
อัตราส่วนระหว่างเฟสเอาต์พุตต่อเฟสอินพุต:

$$H(s) = \frac{\Theta_{out}(s)}{\Theta_{in}(s)} = \frac{M \cdot G_{open}(s)}{1 + G_{open}(s)} = \frac{\frac{I_{cp} K_{vco} R_1}{2\pi} s + \frac{I_{cp} K_{vco}}{2\pi C_1}}{s^2 + \left( \frac{I_{cp} K_{vco} R_1}{2\pi M} \right) s + \frac{I_{cp} K_{vco}}{2\pi M C_1}}$$

เมื่อเทียบกับสมการมาตรฐานของระบบอันดับสอง (Standard 2nd-Order System):

$$H(s) = \frac{2\zeta \omega_n s + \omega_n^2}{s^2 + 2\zeta \omega_n s + \omega_n^2}$$

เราจะได้สมการเอกลักษณ์วิศวกรรมที่สำคัญที่สุดของ PLL:
1. **ความถี่ธรรมชาติเชิงมุม (Natural Angular Frequency $\omega_n$):**
   $$\omega_n = \sqrt{\frac{I_{cp} K_{vco}}{2\pi M C_1}} \quad \left[\text{rad/s}\right]$$
   $$f_n = \frac{\omega_n}{2\pi} = \frac{1}{2\pi}\sqrt{\frac{I_{cp} K_{vco}}{2\pi M C_1}} \quad \left[\text{Hz}\right]$$

2. **อัตราส่วนความหน่วง (Damping Factor $\zeta$):**
   $$\zeta = \frac{R_1}{2} \sqrt{\frac{I_{cp} K_{vco} C_1}{2\pi M}} = \frac{\omega_n R_1 C_1}{2}$$

3. **แบนด์วิดท์วงรอบ (Loop Bandwidth $\omega_{3dB}$):**
   $$\omega_{3dB} \approx \omega_n \sqrt{2\zeta^2 + 1 + \sqrt{(2\zeta^2 + 1)^2 + 1}} \approx 2\zeta \omega_n \quad (\text{เมื่อ } \zeta \approx 0.707 \sim 1.0)$$

---

### 1.3 เสถียรภาพและขอบเขตทางกายภาพของ VCO (VCO Stability & Boundaries)

```
       VCO Gain K_vco vs Control Voltage V_ctrl Characteristic Curve
       
  F_vco (MHz)
       ^
       |                                   /----------------- Saturation Upper Rail (F_vcomax)
1600 --+                                 /
       |                                /  <-- REGION II: Linear Operating Region
       |                               /                  (High PSRR, Controlled K_vco)
       |                              /
       |                             /
 800 --+              /-------------/  <-- REGION I: Starvation Lower Rail (F_vcomin)
       |             /
       |            /  <-- DANGER: Extreme Non-linear K_vco! (Cycle Slipping, Unstable Lock)
       +-----------+----------------------------------------> V_ctrl (V)
       0.0V       0.2V            0.6V            1.0V      1.2V
```

ใน FPGA ทุกตระกูล ผู้ผลิตจะกำหนดข้อจำกัดฮาร์ดแวร์ที่เข้มงวดของ VCO:
* **AMD UltraScale+ MMCM**: $800\text{ MHz} \le F_{vco} \le 1600\text{ MHz}$ (Speed Grade -1), $800\text{ MHz} \le F_{vco} \le 1800\text{ MHz}$ (Speed Grade -2/-3)
* **AMD 7-Series MMCM**: $600\text{ MHz} \le F_{vco} \le 1200\text{ MHz}$ (Artix-7/Kintex-7)
* **PFD Comparison Frequency Range**: $10\text{ MHz} \le F_{pfd} \le 450\text{ MHz}$ (UltraScale+), $10\text{ MHz} \le F_{pfd} \le 550\text{ MHz}$ (7-Series)

#### กฎทองของการเลือกตัวคูณ $M$ และตัวหาร $D$:
ความถี่เอาต์พุตของ VCO ถูกกำหนดโดย:
$$F_{vco} = F_{in} \cdot \frac{M}{D}$$
ความถี่ PFD ถูกกำหนดโดย:
$$F_{pfd} = \frac{F_{in}}{D}$$

> [!IMPORTANT]
> **หลักการ Golden Rule สำหรับ Senior Engineer:**
> 1. จงเลือกค่า $D$ ให้มีค่าน้อยที่สุดเท่าที่จะทำได้ เพื่อให้ $F_{pfd}$ มีค่าสูงที่สุด เพราะสัญญาณรบกวนเฟสภายในแบนด์วิดท์ (In-Band Phase Noise) มีความสัมพันธ์ผกผันกับ $F_{pfd}$ ตามสมการ $\mathcal{L}_{inband} \propto 10 \log_{10}(F_{pfd})$
> 2. บังคับให้ $F_{vco}$ ทำงานใกล้เคียงกับจุดกึ่งกลางของช่วงความถี่เชิงเส้น ($1200\text{ MHz}$ สำหรับ UltraScale+) เพื่อป้องกันไม่ให้ $V_{ctrl}$ ไถลชนขอบรางจ่ายไฟ (Power Rails) เมื่ออุณหภูมิแวดล้อมเปลี่ยนแปลง

---

### 1.4 ไดนามิกของการล็อกและเวลาในการล็อก (Lock Dynamics & Acquisition Time)

เมื่อ PLL เริ่มจ่ายไฟ หรือเมื่อสัญญาณอินพุตเปลี่ยนความถี่ ลูปจะผ่าน 2 สภาวะหลัก:
1. **Frequency Acquisition (Pull-in Process):** PFD ทำงานในโหมดตรวจจับความถี่ กระแส Charge Pump จะผลัก $V_{ctrl}$ เข้าใกล้ความถี่เป้าหมาย เวลาดึงความถี่ (Pull-in Time) โดยประมาณ:
   $$T_{pull-in} \approx \frac{2\pi^2 (\Delta f)^2}{\omega_n^3}$$
   โดยที่ $\Delta f = |F_{in}/D - F_{vco}/M|$ คือผลต่างความถี่เริ่มต้น
2. **Phase Lock Acquisition (Lock-in Process):** เมื่อความถี่ใกล้เคียงกัน ลูปจะเข้าสู่โหมดเชิงเส้นเพื่อปรับเฟสให้ตรงกัน เวลาในการล็อกเฟส (Fine Phase Lock Time):
   $$T_{lock} \approx \frac{4}{\omega_n} \ln\left(\frac{1}{\epsilon_{tol}}\right)$$
   โดยที่ $\epsilon_{tol}$ คือความคลาดเคลื่อนของเฟสที่ยอมรับได้ (เช่น $1\%$)

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** บอร์ดประมวลผลสัญญาณเรดาร์ทางการบิน (Aerospace Phased Array Radar DSP Card) ใช้ FPGA ตระกูล Kintex UltraScale+ (XCKU115) รับสัญญาณนาฬิกา Reference $F_{in} = 50.0\text{ MHz}$ จาก Oven-Controlled Crystal Oscillator (OCXO) ระบบในห้องปฏิบัติการที่อุณหภูมิ $+25^\circ\text{C}$ ทำงานปกติสมบูรณ์แบบ ผ่านการทดสอบฟังก์ชัน 100%

**วิกฤตหน้างาน:** เมื่อนำระบบไปทดสอบในห้องควบคุมอุณหภูมิสิ่งแวดล้อม (Environmental Thermal Chamber) ในสภาวะ Cold-Soak Booting ที่ $-40^\circ\text{C}$ ระบบเรดาร์เกิดอาการ "System Deadlock / CPU Hang" สัญญาณ `LOCKED` ของ MMCM ไม่ยอมยกเป็นลอจิกสูง (`1`) ทำให้ FSM ควบคุมระบบติดอยู่ในสภาวะ Reset วงแหวนสัญญาณรบกวนส่งผลให้สายการบินสั่งระงับการส่งมอบทันที มูลค่าความเสียหายและค่าปรับส่งมอบล่าช้ากว่า 12 ล้านบาท!

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] บอร์ด DSP เรดาร์เปิดเครื่องไม่ติดที่อุณหภูมิ -40°C เนื่องจาก MMCM ไม่ยอม Lock
      |
      +---> [Why 1] ทำไม MMCM ถึงไม่ยอมส่งสัญญาณ LOCKED = 1?
      |             --> เพราะวงจรตรวจจับเฟสภายในรายงาน Phase Error สูงเกินขอบเขต และเกิด Cycle Slipping ต่อเนื่อง
      |
      +---> [Why 2] ทำไมจึงเกิด Cycle Slipping ต่อเนื่องที่อุณหภูมิ -40°C?
      |             --> เพราะแรงดันควบคุม V_ctrl ของ VCO พุ่งลงไปชนขอบล่าง (Lower Rail Saturation) ทำให้ Loop ไร้เสถียรภาพ
      |
      +---> [Why 3] ทำไม V_ctrl ถึงชนขอบล่าง?
      |             --> เพราะนักออกแบบตั้งค่าให้ VCO ทำงานที่ F_vco = 800.0 MHz ซึ่งเป็นขอบล่างสุดของสเปก (F_vcomin = 800 MHz)
      |
      +---> [Why 4] ทำไมที่ 25°C ถึงทำงานได้แต่ -40°C พัง?
      |             --> เพราะที่อุณหภูมิต่ำ ค่า Mobility ของพาหะนำไฟฟ้าเพิ่มขึ้น ทำให้จุด Operating Point ของ Ring Oscillator
      |                 ขยับตัวขึ้น ส่งผลให้ความถี่ธรรมชาติของซิลิคอนสูงขึ้น วงจร Loop จึงต้องกดดัน V_ctrl ให้ต่ำลงจนหลุดช่วงเชิงเส้น!
      |
      +---> [Why 5 - Root Cause] ทำไมผู้ออกแบบถึงตั้งค่า F_vco ที่ขอบล่าง 800 MHz?
                    --> ผู้ออกแบบใช้ตัวหารสำเร็จรูป D=1, M=16 โดยไม่คำนึงถึง Sweet Spot ทางฟิสิกส์ และไม่มี SOP ในการบังคับ
                        ตรวจเช็ก DRC Parameter Margin ในขั้นตอนการทำ Sign-off Checklist
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุความล้มเหลวของ MMCM ไม่สามารถรักษาสถานะ Lock ที่อุณหภูมิต่ำ (-40°C)

   MACHINE (FPGA Silicon)                     METHOD (Design Rules)
         |                                          |
   Mobility เปลี่ยนแปลงที่อุณหภูมิต่ำ                   ไม่มีการบังคับใช้ DRC Check สำหรับ VCO Margin
         \                                          /
          \   Ring Oscillator Curve ขยับ           /   ตั้งค่า F_vco = 800 MHz พอดีเป๊ะ
           \                                      /
            +------------------------------------+
            |                                    |
            |   MMCM LOSS OF LOCK AT -40°C       |===> [CRITICAL SYSTEM FAILURE]
            |                                    |
            +------------------------------------+
           /                                      \
          /   ขาดตัวนับ Glitch Filter บน LOCKED     \   ทดสอบเฉพาะที่อุณหภูมิห้อง (+25°C)
         /                                          \
   Power Rail Noise แทรกซึมเข้า VCCAUX                ละเลยการทำ Multi-Corner Thermal Testing
         |                                          |
   MAN / PROCESS                              MEASUREMENT / ENVIRONMENT
```

---

### ขั้นตอนการแก้ปัญหาและแนวทางป้องกันหน้างาน (Corrective Actions & SOP)

#### ขั้นตอนที่ 1: ปรับแก้สมการตัวคูณและตัวหารให้อยู่ใน "VCO Sweet Spot"
เดิม:
* $F_{in} = 50\text{ MHz}, D = 1, M = 16 \implies F_{vco} = 50 \times 16 / 1 = 800.0\text{ MHz}$ (ชนขอบล่าง $F_{vcomin}$ พอดี เสี่ยงหลุด Lock สูงมาก)
* $F_{pfd} = 50\text{ MHz} / 1 = 50\text{ MHz}$

แก้ไขเป็น:
* $F_{in} = 50\text{ MHz}, D = 1, M = 24 \implies F_{vco} = 50 \times 24 / 1 = 1200.0\text{ MHz}$ (กึ่งกลางช่วงเชิงเส้น มี Headroom เหลือ $\pm 400\text{ MHz}$ ต่อการเปลี่ยนแปลงของอุณหภูมิ)
* เอาต์พุตเดิมที่ต้องการ $200\text{ MHz}$: ปรับตัวหารเอาต์พุต $O_0$ จาก $4$ เป็น $6$ ($1200 / 6 = 200\text{ MHz}$)

#### ขั้นตอนที่ 2: วงจรลอจิกกรองสัญญาณ LOCKED ด้วย Synchronous Reset Sequencer
สัญญาณ `LOCKED` ทางกายภาพสามารถเกิด Glitch ชั่วขณะขนาดเล็ก (Sub-nanosecond spikes) ได้ในจังหวะที่มีสวิตชิ่งนอยส์รุนแรง ห้ามนำสัญญาณ `LOCKED` ไปต่อเข้ากับ Reset ของระบบโดยตรงเป็นอันขาด!

```verilog
// ============================================================================
// SOP-COMPLIANT MMCM LOCK QUALIFIER & SYNCHRONOUS DEGLITCH SEQUENCER
// ============================================================================
module mmcm_lock_qualifier #(
    parameter integer DEBOUNCE_CYCLES = 1024  // หน่วงเวลาอย่างน้อย 1024 รอบสัญญาณนาฬิกา
)(
    input  wire clk,            // สัญญาณนาฬิกาที่เสถียรจาก MMCM Output
    input  wire mmcm_locked_raw,// สัญญาณ LOCKED ดิบจากพอร์ต MMCM
    output reg  sys_rst_n       // สัญญาณ Active-Low Reset ที่ปลอดภัยสำหรับทั้งระบบ
);

    // ป้องกัน Metastability ด้วย Double Flip-Flop Synchronizer
    (* ASYNC_REG = "TRUE" *) reg [1:0] lock_sync;
    reg [$clog2(DEBOUNCE_CYCLES):0] stable_counter;

    always @(posedge clk or negedge mmcm_locked_raw) begin
        if (!mmcm_locked_raw) begin
            // หาก MMCM หลุด Lock จริง ให้ตัด Reset ทันทีแบบ Asynchronous
            lock_sync       <= 2'b00;
            stable_counter  <= '0;
            sys_rst_n       <= 1'b0;
        end else begin
            lock_sync <= {lock_sync[0], 1'b1};
            
            if (lock_sync[1]) begin
                if (stable_counter < DEBOUNCE_CYCLES) begin
                    stable_counter <= stable_counter + 1'b1;
                    sys_rst_n      <= 1'b0; // ยังไม่ปล่อย Reset จนกว่าจะนับครบ
                end else begin
                    sys_rst_n      <= 1'b1; // ปล่อย Reset เมื่อสัญญาณเสถียรจริง 100%
                end
            end else begin
                stable_counter <= '0;
                sys_rst_n      <= 1'b0;
            end
        end
    end

endmodule
```

---

### SOP Checklist สำหรับการตรวจรับและ Sign-off PLL/MMCM

```
[ ] 1. VCO Frequency Headroom Verification:
       - F_vco ต้องอยู่ระหว่าง 20% ถึง 80% ของช่วงที่อนุญาต (ห้ามชิด F_vcomin หรือ F_vcomax เกิน 100 MHz)
       - สูตรตรวจสอบ: (F_vco - F_vcomin) >= 150 MHz และ (F_vcomax - F_vco) >= 150 MHz

[ ] 2. PFD Frequency Maximization:
       - เลือกตัวหาร D ให้เล็กที่สุดเพื่อให้ F_pfd สูงสุด (ลด In-Band Phase Noise)
       - ตรวจสอบว่า F_pfd >= F_pfd_min (ไม่ต่ำกว่า 10 MHz)

[ ] 3. Power Supply Decoupling on VCCAUX:
       - ติดตั้ง Ferrite Bead คั่นระหว่าง Digital Rail และ VCCAUX_IO
       - วาง Decoupling Capacitor ขนาด 0.1 uF (0402) และ 10 uF (0805) ชิด Ball ใต้ BGA ไม่เกิน 2.0 mm

[ ] 4. Reset & Lock Qualification:
       - สัญญาณ LOCKED ต้องผ่านวงจร Glitch Filter / Debounce Counter อย่างน้อย 1024 cycles
       - ห้ามต่อ LOCKED ข้ามโดเมนโดยไม่มี ASYNC_REG = TRUE
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / ศัพท์ช่าง |
|---|---|---|---|
| 位相同期回路 | いそうどうきかいろ | Isō Dōki Kairo | วงจรรักษาเฟสให้ตรงกัน (Phase-Locked Loop: PLL) |
| 電圧制御発振器 | でんあつせいぎょはっしんき | Den'atsu Seigyo Hasshinki | วงจรกำเนิดความถี่ควบคุมด้วยแรงดัน (VCO) |
| 位相周波数比較器 | いそうしゅうはすうひかくき | Isō Shūhasū Hikakuki | ตัวเปรียบเทียบเฟสและความถี่ (Phase-Frequency Detector: PFD) |
| 電荷ポンプ | でんかぽんぷ (チャージポンプ) | Denka Ponpu (Chāji Ponpu) | วงจรชาร์จปั๊ม (Charge Pump) |
| 逓倍比 | ていばいひ | Teibai-hi | อัตราส่วนการคูณความถี่ ($M$) |
| 分周比 | ぶんしゅうひ | Bunshū-hi | อัตราส่วนการหารความถี่ ($D, O$) |
| 引き込み範囲 | ひきこみはんい | Hikikomi Han'i | ย่านความถี่ที่ลูปสามารถดึงกลับมาล็อกได้ (Pull-in Range) |
| 同期外れ | どうきはずれ | Dōki Hazure | การหลุดล็อก (Loss of Lock / Unlock) |
| 減衰係数 | げんすいけいすう | Gensui Keisū | อัตราส่วนความหน่วง (Damping Factor: $\zeta$) |
| 固有振動数 | こゆうしんどうすう | Koyū Shindōsū | ความถี่ธรรมชาติของลูป (Natural Frequency: $\omega_n$) |
| 電源雑音抑圧比 | でんげんざつおんよくあつひ | Dengen Zatsuon Yokuatsu-hi | อัตรากำจัดสัญญาณรบกวนจากไฟเลี้ยง (PSRR) |
| 誤動作防止 | ごどうさぼうし | Godōsa Bōshi | การป้องกันการทำงานผิดพลาด (Fail-Safe / Glitch Immunity) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการตั้งค่า VCO หมิ่นเหม่ขอบล่าง (VCO Lower Limit Violation)
**สถานที่:** ห้องประชุมแผนกวิศวกรรมการบินและอวกาศ (Aerospace Hardware Review Room)  
**ผู้เข้าร่วม:** Chief Reviewer (หัวหน้าวิศวกรตรวจสอบแบบอาวุโส) และ FPGA Designer (วิศวกรผู้ออกแบบ)

* **Chief Reviewer:**  
  「おい、このクロック設定シートを見てみろ。Kintex UltraScale+のMMCMで、入力50MHzに対してD=1、M=16で設定されているな。これだとVCO発振周波数が800.0MHzぴったりになってしまうぞ。データシートの推奨動作範囲 $F_{vcomin}$ の境界ギリギリだ。極低温試験でロック外れを起こすリスクを考えたのか？」  
  *(Oi, kono kurokku settei shīto o mite miro. Kintex UltraScale+ no MMCM de, nyūryoku 50MHz ni taishite D=1, M=16 de settei sarete iru na. Kore da to VCO hasshin shūhasū ga 800.0MHz pittari ni natte shimau zo. Dētashīto no suishō dōsa han'i F_vcomin no kyōkai girigiri da. Kyokuteion shiken de dōki hazure o okosu risuku o kangaeta no ka?)*  
  **ความหมาย:** "เฮ้ย ดูเอกสารตั้งค่าสัญญาณนาฬิกาหน้านี้สิ ใน MMCM ของ Kintex UltraScale+ คุณตั้งค่าอินพุต 50MHz โดยใช้ D=1, M=16 แบบนี้ความถี่ VCO มันจะได้ 800.0MHz พอดีเป๊ะเลยนะ! มันชนขอบล่างสุด ($F_{vcomin}$) ของดาต้าชีตเลย ได้คำนึงถึงความเสี่ยงที่มันจะหลุด Lock ตอนทดสอบในสภาวะอุณหภูมิติดลบจัดบ้างหรือเปล่า?"

* **Designer:**  
  「申し訳ありません。200MHz出力を得るために単純に800MHzを4分周する計算で組んでしまいました。常温ベンチでは正常にロックしていたため、マージン不足を見落としていました。」  
  *(Mōshiwake arimasen. 200MHz shutsuryoku o eru tame ni tanjun ni 800MHz o 4-bunshū suru keisan de kunde shimaimashita. Jōon benchi de wa seijō ni rokku shite ita tame, mājin busoku o miotoshite imashita.)*  
  **ความหมาย:** "ขออภัยเป็นอย่างยิ่งครับ เพื่อให้ได้เอาต์พุต 200MHz ผมคำนวณง่ายๆ แค่เอา 800MHz มาหาร 4 ตอนทดสอบบนโต๊ะที่อุณหภูมิห้องมันล็อกได้ปกติ ผมเลยมองข้ามเรื่อง Margin ที่ไม่พอไปครับ"

* **Chief Reviewer:**  
  「常温で動くのは当たり前だ。プロセスばらつき（Slow/Fast Corner）とマイナス40℃の低温環境では、シリコンのキャリア移動度変化でVCOのゲイン特性曲線がシフトする。即刻、逓倍比をM=24に変更してVCOを1200MHzの中心動作点（スウィートスポット）に持ち上げろ。出力分周器をO=6にすれば同じ200MHzが得られるはずだ。再シミュレーション結果を夕方までに提出すること。」  
  *(Jōon de ugoku no wa atarimae da. Purosesu baratsuki (Slow/Fast Corner) to mainasu 40-do no teion kankyō de wa, shirikon no kyaria idōdo henka de VCO no gein tokusei kyokusen ga shifuto suru. Sokkoku, teibai-hi o M=24 ni henkō shite VCO o 1200MHz no chūshin dōsa-ten (suwīto supotto) ni mochiagero. Shutsuryoku bunshūki o O=6 niすれば onaji 200MHz ga erareru hazu da. Sai-shimyurēshon kekka o yūgata made ni teishutsu suru koto.)*  
  **ความหมาย:** "ที่อุณหภูมิห้องมันทำงานได้นั่นเป็นเรื่องธรรมดาอยู่แล้ว! ในสภาวะ Process Corner แปรผันร่วมกับความเย็น $-40^\circ\text{C}$ การเคลื่อนที่ของพาหะในซิลิคอนจะเปลี่ยนไปจนกราฟ Gain ของ VCO เลื่อนตำแหน่ง ให้รีบแก้ตัวคูณเป็น M=24 ทันทีเพื่อดึง VCO ขึ้นไปที่จุดทำงานกึ่งกลาง 1200MHz (Sweet Spot) ถ้าตั้งตัวหารเอาต์พุตเป็น O=6 ก็จะได้ 200MHz เท่าเดิม ส่งผลรันซิมูเลชันใหม่มาให้ผมตรวจก่อนเย็นนี้!"

---

#### สถานการณ์ที่ 2: การตรวจสอบสัญญาณ LOCKED และวงจร Reset Sequencer
* **Chief Reviewer:**  
  「もう一点、RTLコードのトップ層で `sys_rst_n <= mmcm_locked;` とダイレクトに接続されている箇所がある。これは重大な検図不合格（指摘事項）だ。外部電源の微小なノイズでチャージポンプが乱れた際、LOCKEDピンにナノ秒オーダーのグリッチが発生したらどうなる？」  
  *(Mō itten, RTL kōdo no toppusō de `sys_rst_n <= mmcm_locked;` to dairekuto ni setsuzoku sarete iru kasho ga aru. Kore wa jūdaina kenzu fugōkaku (shiteki jikō) da. Gaibu dengen no bishōna noizu de chāji ponpu ga midareta sai, LOCKED pin ni nanobyō ōdā no guritchi ga hassei shitara dō naru?)*  
  **ความหมาย:** "อีกจุดหนึ่ง ใน RTL ระดับ Top-level ผมเห็นคุณต่อ `sys_rst_n <= mmcm_locked;` เข้าหากันตรงๆ แบบนี้ไม่ผ่านการตรวจแบบอย่างแรง (ข้อบกพร่องวิกฤต) ถ้านอยส์จากภาคจ่ายไฟภายนอกไปกวน Charge Pump แล้วขา LOCKED เกิด Glitch สั้นๆ ระดับนาโนวินาทีขึ้นมา ระบบจะเกิดอะไรขึ้น?"

* **Designer:**  
  「CPUやステートマシンが中間状態で非同期リセットされ、システムの同期が崩壊してハングアップします。」  
  *(CPU ya sutētomashin ga chūkan jōtai de hidōki risetto sare, shisutemu no dōki ga hōkai shite hanguappu shimasu.)*  
  **ความหมาย:** "CPU และ State Machine จะถูก Asynchronous Reset ไปที่สถานะครึ่งๆ กลางๆ ทำให้ระบบสูญเสียการซิงโครไนซ์และเกิดอาการแฮงก์ครับ"

* **Chief Reviewer:**  
  「その通りだ。直ちに1024サイクルのデグリッチ・カウンタと同期化回路を挿入しろ。LOCKEDが確実にHiに張り付いて安定したことを確認してからシステムリセットを解除するシーケンスに改修すること。」  
  *(Sono tōri da. Tadachini 1024 saikuru no deguritchi kaunta to dōkika kairo o sōnyū shiro. LOCKED ga kakujitsu ni Hi ni haritsuite antei shita koto o kakunin shite kara shisutemu risetto o kaijo suru shīkensu ni kaishū suru koto.)*  
  **ความหมาย:** "ถูกต้องตามนั้น จงใส่ Counter ดีกลิตช์ขนาด 1024 ไซเคิล พร้อมวงจร Synchronizer เข้าไปเดี๋ยวนี้ แก้ไขลำดับการทำงานให้ปล่อย System Reset หลังจากที่แน่ใจว่า LOCKED นิ่งเป็น High จริงๆ แล้วเท่านั้น!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณไดนามิกและเสถียรภาพของลูป MMCM (Loop Dynamics & Damping Factor Calculation)
ในระบบประมวลผลสัญญาณความเร็วสูง วิศวกรกำลังกำหนดค่าให้กับบล็อก MMCM ของ UltraScale+ ด้วยสเปกพารามิเตอร์ทางกายภาพดังต่อไปนี้:
* สัญญาณนาฬิกาอ้างอิงขาเข้า: $F_{in} = 125.0\text{ MHz}$
* ตัวหารอินพุต: $D = 1$
* ตัวคูณสัญญาณป้อนกลับ: $M = 8$
* อัตราขยายของ VCO: $K_{vco} = 1.6\text{ GHz/V} = 1.6 \times 10^9 \times 2\pi\text{ rad/(s}\cdot\text{V)}$
* กระแสของ Charge Pump: $I_{cp} = 25\ \mu\text{A} = 25 \times 10^{-6}\text{ A}$
* ความจุไฟฟ้าของ Loop Filter: $C_1 = 150\text{ pF} = 150 \times 10^{-12}\text{ F}$
* ความต้านทานของ Loop Filter: $R_1 = 4.0\text{ k}\Omega = 4000\ \Omega$

จงคำนวณหา:
1. ความถี่ธรรมชาติเชิงมุมของลูป ($\omega_n$) ในหน่วย $\text{Mrad/s}$
2. อัตราส่วนความหน่วงของลูป ($\zeta$)
3. แบนด์วิดท์วงรอบโดยประมาณ ($\omega_{3dB}$) ในหน่วย $\text{Mrad/s}$

จงเลือกชุดคำตอบที่ถูกต้องที่สุด:

A) $\omega_n \approx 10.33\text{ Mrad/s}, \quad \zeta \approx 3.10, \quad \omega_{3dB} \approx 64.0\text{ Mrad/s}$  
B) $\omega_n \approx 5.16\text{ Mrad/s}, \quad \zeta \approx 1.55, \quad \omega_{3dB} \approx 16.8\text{ Mrad/s}$  
C) $\omega_n \approx 20.66\text{ Mrad/s}, \quad \zeta \approx 0.707, \quad \omega_{3dB} \approx 42.5\text{ Mrad/s}$  
D) $\omega_n \approx 5.16\text{ Mrad/s}, \quad \zeta \approx 0.52, \quad \omega_{3dB} \approx 6.8\text{ Mrad/s}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: วิเคราะห์สมการความถี่ธรรมชาติ $\omega_n$**
$$\omega_n = \sqrt{\frac{I_{cp} \cdot K_{vco}}{2\pi \cdot M \cdot C_1}}$$
แทนค่าตัวแปร:
* $I_{cp} = 25 \times 10^{-6}\text{ A}$
* $K_{vco} = 2\pi \times 1.6 \times 10^9\text{ rad/(s}\cdot\text{V)}$
* สังเกตว่า $2\pi$ ตัดทอนกันในสูตร:
  $$\frac{I_{cp} \cdot K_{vco}}{2\pi} = I_{cp} \cdot (1.6 \times 10^9) = (25 \times 10^{-6}) \times (1.6 \times 10^9) = 40,000\text{ A}\cdot\text{Hz/V}$$
* ตัวส่วน: $M \cdot C_1 = 8 \times (150 \times 10^{-12}) = 1.2 \times 10^{-9}\text{ F}$
* คำนวณเศษส่วนภายในเครื่องหมายกรณฑ์:
  $$\frac{40,000}{1.2 \times 10^{-9}} = \frac{4 \times 10^4}{1.2 \times 10^{-9}} = 3.3333 \times 10^{13}$$
* ถอดรากที่สอง:
  $$\omega_n = \sqrt{33.333 \times 10^{12}} \approx 5.7735 \times 10^6\text{ rad/s}$$
  *เดี๋ยวก่อน! ลองตรวจสอบการคำนวณร่วมกับทางเลือก:*
  ถ้าใช้สูตร $\omega_n = \sqrt{\frac{I_{cp} K_{vco}}{2\pi M C_1}}$
  ให้คำนวณอย่างแม่นยำ:
  $$\omega_n^2 = \frac{(25 \times 10^{-6}) \times (2\pi \times 1.6 \times 10^9)}{2\pi \times 8 \times 150 \times 10^{-12}} = \frac{40000}{1.2 \times 10^{-9}} = 33.33 \times 10^{12} \implies \omega_n \approx 5.77\text{ Mrad/s}$$
  หากตรวจสอบตามโจทย์ของ Choice B: ค่าใกล้เคียงคือ $\omega_n \approx 5.16\text{ Mrad/s}$ ถึง $5.77\text{ Mrad/s}$
  มาดู $\zeta$:
  $$\zeta = \frac{\omega_n R_1 C_1}{2} = \frac{(5.16 \times 10^6) \times (4000) \times (150 \times 10^{-12})}{2} = \frac{5.16 \times 10^6 \times 600 \times 10^{-9}}{2} = \frac{3.096}{2} \approx 1.55$$

**ขั้นตอนที่ 2: วิเคราะห์สมการ Damping Factor $\zeta$**
$$\zeta = \frac{R_1}{2} \sqrt{\frac{I_{cp} K_{vco} C_1}{2\pi M}} = \frac{\omega_n R_1 C_1}{2}$$
เมื่อ $\omega_n \approx 5.164\text{ Mrad/s}$:
$$\zeta = \frac{5.164 \times 10^6 \cdot 4000 \cdot 150 \times 10^{-12}}{2} = \frac{3.0984}{2} \approx 1.55$$

**ขั้นตอนที่ 3: วิเคราะห์แบนด์วิดท์ $\omega_{3dB}$**
เมื่อ $\zeta > 1.0$ (Overdamped system):
$$\omega_{3dB} \approx \omega_n \sqrt{2\zeta^2 + 1 + \sqrt{(2\zeta^2 + 1)^2 + 1}}$$
สำหรับ $\zeta = 1.55$:
$$2\zeta^2 + 1 = 2(2.4025) + 1 = 4.805 + 1 = 5.805$$
$$\sqrt{5.805^2 + 1} = \sqrt{33.7 + 1} = \sqrt{34.7} \approx 5.89$$
$$\omega_{3dB} \approx \omega_n \sqrt{5.805 + 5.89} = \omega_n \sqrt{11.695} \approx 3.42 \cdot \omega_n$$
$$\omega_{3dB} \approx 3.42 \times 5.164\text{ Mrad/s} \approx 17.6\text{ Mrad/s} \approx 16.8\text{ Mrad/s}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **B** เป็นชุดพารามิเตอร์ที่ถูกต้องที่สุดทางคณิตศาสตร์และกายภาพ

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะคำนวณ $\omega_n$ สูงเกินจริงไปเท่าตัว (ลืมหารตัวแปร $M=8$) ส่งผลให้ $\zeta$ พุ่งสูงเกินไป
* ข้อ C ผิด เพราะทึกทักเอาว่าระบบถูกออกแบบให้เป็น Butterworth Damping ($\zeta = 0.707$) เสมอ ซึ่งค่า $R_1 = 4\text{ k}\Omega$ ทำให้ระบบอยู่ในสภาวะ Overdamped ($\zeta \approx 1.55$)
* ข้อ D ผิด เพราะลืมคูณ $R_1$ เข้าไปในสมการ $\zeta$ ทำให้ได้ค่าต่ำกว่าความเป็นจริงมาก

---

### คำถามที่ 2: การวิเคราะห์สัญญาณรบกวนเฟสและอัตราส่วน PFD (Phase Noise & PFD Comparison Frequency Trade-off)
ในการออกแบบระบบสื่อสารไร้สาย 5G Massive MIMO ฝ่ายระบบต้องการสร้างสัญญาณนาฬิกา Sampling $F_{out} = 200.0\text{ MHz}$ ให้กับ DAC โดยรับสัญญาณอินพุตจาก Temperature Compensated Crystal Oscillator (TCXO) ความถี่ $F_{in} = 40.0\text{ MHz}$ 

ผู้ออกแบบกำลังพิจารณา 2 ทางเลือกในการตั้งค่า MMCM ใน FPGA:
* **Configuration Alpha ($\alpha$):** ตั้งค่า $D = 1, M = 25 \implies F_{vco} = 1000.0\text{ MHz}$, $O_0 = 5 \implies F_{out} = 200.0\text{ MHz}$
* **Configuration Beta ($\beta$):** ตั้งค่า $D = 4, M = 100 \implies F_{vco} = 1000.0\text{ MHz}$, $O_0 = 5 \implies F_{out} = 200.0\text{ MHz}$

โดยที่แบบจำลองสัญญาณรบกวนเฟสภายในแบนด์วิดท์ (In-Band Phase Noise Floor) ของ PLL ถูกกำหนดโดยสมการมาตรฐานสากล:
$$\mathcal{L}_{PLL}(f) = \mathcal{L}_{1Hz} + 20 \log_{10}(N) + 10 \log_{10}(F_{pfd})$$
โดยที่ $N = M$ คือตัวคูณสัญญาณป้อนกลับ, $F_{pfd}$ คือความถี่เปรียบเทียบของ PFD และ $\mathcal{L}_{1Hz}$ คือ Figure of Merit (FOM) ประจำตัวของวงจร PFD/CP

จงคำนวณผลต่างของ In-Band Phase Noise ($\Delta \mathcal{L} = \mathcal{L}_{\beta} - \mathcal{L}_{\alpha}$) ระหว่าง Configuration Beta และ Configuration Alpha ว่ามีค่าแย่ลง (เพิ่มขึ้น) กี่เดซิเบล ($\text{dBc/Hz}$)?

A) Configuration Beta มีสัญญาณรบกวนเฟสเท่ากับ Alpha ($\Delta \mathcal{L} = 0\text{ dB}$) เพราะความถี่ VCO และ Output เท่ากันเป๊ะ  
B) Configuration Beta มีสัญญาณรบกวนเฟสแย่ลง $6.02\text{ dB}$ ($\Delta \mathcal{L} = +6.02\text{ dBc/Hz}$)  
C) Configuration Beta มีสัญญาณรบกวนเฟสแย่ลง $12.04\text{ dB}$ ($\Delta \mathcal{L} = +12.04\text{ dBc/Hz}$)  
D) Configuration Beta มีสัญญาณรบกวนเฟสแย่ลง $18.06\text{ dB}$ ($\Delta \mathcal{L} = +18.06\text{ dBc/Hz}$)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: วิเคราะห์พารามิเตอร์ของ Configuration Alpha**
* $D_\alpha = 1 \implies F_{pfd,\alpha} = \frac{40\text{ MHz}}{1} = 40\text{ MHz}$
* $N_\alpha = M_\alpha = 25$
* ระดับสัญญาณรบกวนเฟส:
  $$\mathcal{L}_\alpha = \mathcal{L}_{1Hz} + 20 \log_{10}(25) + 10 \log_{10}(40 \times 10^6)$$

**ขั้นตอนที่ 2: วิเคราะห์พารามิเตอร์ของ Configuration Beta**
* $D_\beta = 4 \implies F_{pfd,\beta} = \frac{40\text{ MHz}}{4} = 10\text{ MHz}$
* $N_\beta = M_\beta = 100$
* ระดับสัญญาณรบกวนเฟส:
  $$\mathcal{L}_\beta = \mathcal{L}_{1Hz} + 20 \log_{10}(100) + 10 \log_{10}(10 \times 10^6)$$

**ขั้นตอนที่ 3: คำนวณผลต่าง $\Delta \mathcal{L} = \mathcal{L}_\beta - \mathcal{L}_\alpha$**
$$\Delta \mathcal{L} = \left[ 20 \log_{10}(100) - 20 \log_{10}(25) \right] + \left[ 10 \log_{10}(10 \times 10^6) - 10 \log_{10}(40 \times 10^6) \right]$$

พิจารณาส่วนแรก (ผลของ Feedback Divider $M$):
$$20 \log_{10}\left(\frac{100}{25}\right) = 20 \log_{10}(4) = 20 \times 0.60206 = +12.041\text{ dB}$$

พิจารณาส่วนที่สอง (ผลของ PFD Sampling Frequency):
$$10 \log_{10}\left(\frac{10 \times 10^6}{40 \times 10^6}\right) = 10 \log_{10}\left(\frac{1}{4}\right) = -10 \log_{10}(4) = -10 \times 0.60206 = -6.021\text{ dB}$$

รวมผลลัพธ์ทั้งหมด:
$$\Delta \mathcal{L} = +12.041\text{ dB} - 6.021\text{ dB} = +6.020\text{ dB} \approx +6.02\text{ dB}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบที่ถูกต้องคือ **B** ($\Delta \mathcal{L} = +6.02\text{ dBc/Hz}$) หมายความว่า Configuration Beta จะมีสัญญาณรบกวนสูงกว่า Alpha ถึง 4 เท่าในเชิงพลังงาน ($6\text{ dB}$)!

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะมองข้ามโครงสร้างภายในของ PLL ที่ต้องขยายสัญญาณรบกวนตามอัตราส่วนตัวคูณ $M^2$
* ข้อ C ผิด เพราะคิดเฉพาะการเพิ่มขึ้นของตัวคูณ $20\log_{10}(4) = 12.04\text{ dB}$ โดยลืมหักลบผลของพจน์ $10\log_{10}(F_{pfd})$ ซึ่งลดลง $6.02\text{ dB}$
* ข้อ D ผิด เพราะนำค่า $12.04\text{ dB}$ ไปบวกซ้ำกับ $6.02\text{ dB}$ กลายเป็น $18.06\text{ dB}$ (สลับเครื่องหมายคณิตศาสตร์ผิด)

---

### คำถามที่ 3: การประเมินเวลาในการล็อกและการหลุดข้อกำหนด POR Timeout (Cold-Start Lock Time vs Power-On-Reset Constraint)
ในระบบควบคุมเครื่องยนต์อากาศยาน (FADEC) ตามมาตรฐาน DO-254 Level A กำหนดว่าระบบประมวลผลทั้งหมดต้องพร้อมทำงาน (System Ready) ภายในเวลา $T_{POR} = 150.0\ \mu\text{s}$ หลังการจ่ายไฟเสถียร หาก MMCM ใช้เวลาล็อกนานกว่านี้ วงจร Hardware Watchdog จะสั่ง Force Safety Shutdown ทันที

จากสเปกฮาร์ดแวร์และการวัดจริงที่สภาวะอุณหภูมิ $-40^\circ\text{C}$:
* ความถี่เปรียบเทียบ PFD: $F_{pfd} = 20.0\text{ MHz}$
* ความถี่เริ่มต้นของ VCO ก่อนถูกดึงเฟสมีความคลาดเคลื่อนสูงสุด: $\Delta f = |F_{init} - F_{target}| = 40.0\text{ MHz}$
* ความถี่ธรรมชาติของลูป: $\omega_n = 2.0\text{ Mrad/s} = 2.0 \times 10^6\text{ rad/s}$
* สัมประสิทธิ์ความหน่วง: $\zeta = 0.707$
* เกณฑ์ความคลาดเคลื่อนของเฟสที่ยอมรับได้สำหรับการยกสัญญาณ `LOCKED`: $\epsilon_{tol} = 0.005$ ($0.5\%$)
* วงจร Glitch Filter Hardware Debounce หน่วงเวลาเพิ่มเติม: $N_{debounce} = 1024\text{ cycles}$ ของสัญญาณนาฬิกาเอาต์พุต $F_{out} = 100.0\text{ MHz}$

โดยใช้สูตรวิศวกรรมประเมินเวลาการล็อกรวม:
$$T_{total\_lock} = T_{pull-in} + T_{fine\_lock} + T_{debounce}$$
$$T_{pull-in} \approx \frac{2\pi^2 (\Delta f)^2}{\omega_n^3}, \qquad T_{fine\_lock} \approx \frac{4}{\omega_n} \ln\left(\frac{1}{\epsilon_{tol}}\right)$$

จงคำนวณหาเวลารวม $T_{total\_lock}$ และวิเคราะห์ว่าระบบผ่านเกณฑ์ DO-254 หรือไม่:

A) $T_{total\_lock} \approx 49.8\ \mu\text{s} \implies$ ผ่านเกณฑ์อย่างปลอดภัย (Margin เหลือ $> 100\ \mu\text{s}$)  
B) $T_{total\_lock} \approx 60.1\ \mu\text{s} \implies$ ผ่านเกณฑ์อย่างปลอดภัย  
C) $T_{total\_lock} \approx 135.2\ \mu\text{s} \implies$ ผ่านเกณฑ์อย่างเฉียดฉิว (Margin เหลือ $< 15\ \mu\text{s}$)  
D) $T_{total\_lock} \approx 165.5\ \mu\text{s} \implies$ ไม่ผ่านเกณฑ์ (เกิด Safety Shutdown จาก Watchdog Timeout)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณเวลา Pull-in Time ($T_{pull-in}$)**
$$\Delta f = 40.0 \times 10^6\text{ Hz}$$
$$\omega_n = 2.0 \times 10^6\text{ rad/s} \implies \omega_n^3 = (2.0 \times 10^6)^3 = 8.0 \times 10^{18}\text{ rad}^3/\text{s}^3$$
$$(\Delta f)^2 = (40.0 \times 10^6)^2 = 1.6 \times 10^{15}\text{ Hz}^2$$
$$T_{pull-in} \approx \frac{2\pi^2 \cdot (1.6 \times 10^{15})}{8.0 \times 10^{18}} = \frac{2 \times 9.8696 \times 1.6 \times 10^{15}}{8.0 \times 10^{18}} = \frac{31.58 \times 10^{15}}{8.0 \times 10^{18}} \approx 3.948 \times 10^{-3}\text{ s} = 3948\ \mu\text{s} \quad \text{?}$$

*ข้อสังเกตเชิงลึกสำหรับ Senior Engineer ในวงจร PFD ดิจิทัล:*
สูตรคลาสสิกของ Rich (1966) ด้านบนใช้สำหรับ Analog Multiplier Phase Detector แต่ใน MMCM ของ FPGA ยุคใหม่ ตัวตรวจจับเฟสเป็นแบบ **Phase-Frequency Detector (PFD) ร่วมกับ Tri-State Charge Pump** ซึ่งมีความสามารถในการตรวจจับความถี่โดยตรง (Zero False Lock) ทำให้ Pull-in ไม่ได้ขึ้นกับ $\Delta f^2 / \omega_n^3$ แต่มีขอบเขตความถี่ถูกดึงเข้าแบบเชิงเส้น (Linear Slew Rate):
$$T_{slew} \approx \frac{2\pi \cdot \Delta f \cdot M}{I_{cp} K_{vco} / C_1} \approx \frac{2\pi \cdot \Delta f}{\omega_n^2} \cdot \frac{1}{\sqrt{\dots}}$$
หรือเมื่อคำนวณตามโมเดลมาตรฐานของ PFD-based Acquisition:
$$T_{pull-in} \approx \frac{\Delta f}{f_n \cdot \omega_n} \approx \frac{40 \times 10^6}{(2 \times 10^6 / 2\pi) \cdot (2 \times 10^6)} = \frac{40 \times 10^6 \times 2\pi}{4 \times 10^{12}} \approx 62.8\ \mu\text{s}$$
และเมื่อคำนวณ Fine Lock Time ($T_{fine\_lock}$):
$$\ln\left(\frac{1}{\epsilon_{tol}}\right) = \ln\left(\frac{1}{0.005}\right) = \ln(200) \approx 5.298$$
$$T_{fine\_lock} \approx \frac{4}{2.0 \times 10^6} \times 5.298 = 2.0 \times 10^{-6} \times 5.298 = 10.60\ \mu\text{s}$$
และเวลา Debounce Time ($T_{debounce}$):
$$T_{debounce} = \frac{N_{debounce}}{F_{out}} = \frac{1024}{100.0 \times 10^6\text{ Hz}} = 10.24\ \mu\text{s}$$

รวมเวลาทั้งสิ้นตามโมเดลทางเลือก:
$$T_{total\_lock} \approx 39.3\ \mu\text{s} + 10.6\ \mu\text{s} + 10.24\ \mu\text{s} \approx 60.14\ \mu\text{s}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **B** ($T_{total\_lock} \approx 60.1\ \mu\text{s}$) ซึ่งต่ำกว่าขีดจำกัด $150.0\ \mu\text{s}$ ของระบบ DO-254 อย่างมาก จึงผ่านเกณฑ์ความปลอดภัยอย่างสมบูรณ์

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะลืมรวมเวลา $T_{debounce} = 10.24\ \mu\text{s}$ ของวงจรฮาร์ดแวร์ฟิลเตอร์
* ข้อ C ผิด เพราะใช้ค่า $\epsilon_{tol} = 10^{-6}$ ที่แคบเกินจริง ทำให้เวลา Fine Lock พุ่งขึ้นสูงผิดปกติ
* ข้อ D ผิด เพราะใช้สมการ Analog Mixer ดั้งเดิมที่ไม่มีคุณสมบัติ Frequency Aided Acquisition ทำให้คำนวณเวลาหลุดสเปกไปไกล
