# Lesson 144: FPGA PLL Deep Dive - Part 4 (Dynamic Phase Alignment and SerDes Applications - Dynamic Phase Shift DPS, Alexander Bang-Bang CDR, Spread Spectrum Clocking Tracking Bandwidth & Multi-Gigabit Eye Closure)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์หน้าต่างเวลาของ High-Speed I/O (The High-Speed I/O Timing Crisis)
เมื่ออัตราการส่งข้อมูลข้ามชิป (Chip-to-Chip Interface) ก้าวข้ามจากระดับ Megabits สู่ระดับ Gigabits ขนาดของคาบเวลาข้อมูลหนึ่งบิต หรือ **Unit Interval ($UI = 1 / F_{baud}$)** จะหดแคบลงอย่างรวดเร็วจนถึงระดับพิโกวินาที (Picoseconds):
* $1.25\text{ Gbps}$ (Gigabit Ethernet / LVDS): $UI = 800.0\text{ ps}$
* $8.0\text{ Gbps}$ (PCI Express Gen 3): $UI = 125.0\text{ ps}$
* $28.0\text{ Gbps}$ (100GbE CAUI-4): $UI = 35.71\text{ ps}$
* $56.0\text{ Gbps}$ PAM4 (200GbE / PCIe Gen 6): $UI = 35.71\text{ ps}$ (แต่มี Eye Height เพียง $1/3$ ของ NRZ)

```
        วิกฤตหน้าต่างเวลาข้ามระดับความเร็ว (Unit Interval Degradation)
        
  1.25 Gbps [ UI = 800 ps ]
  |<-------------------------------------------------------------------->|
  +----------------------------------+-----------------------------------+
  |           VALID DATA EYE         |       Jitter & PVT Drift Margin   |
  +----------------------------------+-----------------------------------+
  
  8.00 Gbps [ UI = 125 ps ]
  |<------------------------->|
  +-------------+-------------+
  |  DATA EYE   | PVT Drift   | <--- Static Timing พังทลาย!
  +-------------+-------------+      (การขยายตัวตามอุณหภูมิ 120 ps กลืนกินทั้งบิต!)
  
  28.0 Gbps [ UI = 35.7 ps ]
  |<--->|
  +-+-+-+
  |!|?|!| <--- ต้องใช้ Dynamic Phase Alignment (DPA) หรือ CDR แบบปิดลูป 100%!
  +-+-+-+
```

ในทางฟิสิกส์ สัญญาณนาฬิกาที่ผ่านบัฟเฟอร์ I/O และ Clock Tree ภายในชิปจะเกิดการเคลื่อนตัวตามอุณหภูมิและแรงดันไฟ (PVT Delay Drift) ได้มากถึง **$100 - 250\text{ ps}$** เมื่อชิปร้อนขึ้นจาก $+25^\circ\text{C}$ ไปเป็น $+85^\circ\text{C}$  
ดังนั้น การใช้สัญญาณนาฬิกาแบบคงที่ (Static Phase Shift) จะไม่สามารถรักษาระดับการแซมเปิลข้อมูลให้อยู่กึ่งกลางตา (Center of Eye) ได้อีกต่อไป ระบบจึงต้องอาศัยกลไก **Dynamic Phase Alignment (DPA)** และ **Dynamic Phase Shift (DPS)** เข้ามาจัดตำแหน่งเฟสแบบเรียลไทม์

---

### 1.2 วงจร Dynamic Phase Shift (DPS) ภายในฮาร์ดแวร์ MMCM
บล็อก MMCM ของสถาปัตยกรรมระดับสูง (เช่น AMD UltraScale+) มีวงจร Phase Interpolator ฮาร์ดแวร์ที่ยอมให้ผู้ใช้หมุนเฟสของสัญญาณนาฬิกาเอาต์พุตได้แบบพลวัต (On-the-Fly Phase Shifting) ผ่านอินเตอร์เฟซดิจิทัล 4 พอร์ต:

```
                  อินเตอร์เฟซฮาร์ดแวร์ MMCM DYNAMIC PHASE SHIFT (DPS)
                  
                  +-------------------------------------------------------------+
                  |                         MMCME4_ADV                          |
                  |                                                             |
   psclk -------->| PSCLK                                                       |
                  |                                                             |
   psen --------->| PSEN  (กระตุ้นด้วยพัลส์ 1 รอบ เพื่อสั่งเลื่อนเฟส 1 Step)    |
                  |                                                             |
   psincdec ----->| PSINCDEC (1 = เลื่อนเฟสไปข้างหน้า Lead, 0 = ถอยหลัง Lag)    |
                  |                                                             |
   psdone <-------| PSDONE (ยกเป็น 1 เป็นเวลา 1 รอบ เพื่อยืนยันว่าการหมุนเสร็จสมบูรณ์)|
                  |                                                             |
                  |                                    +----------------------+ |
                  |                                    |  PHASE INTERPOLATOR  | |
                  |  VCO (F_vco) --------------------->| (Discrete Stepper)   | |
                  |                                    +----------+-----------+ |
                  |                                               |             |
                  |                                               v             |
                  |                                            CLKOUT0          |
                  +-------------------------------------------------------------+
```

#### สมการความละเอียดของการเลื่อนเฟส (Phase Shift Resolution Step $\Delta t_{step}$):
ใน UltraScale+ MMCM ช่วงคาบเวลาของ VCO ($T_{vco} = 1 / F_{vco}$) จะถูกแบ่งออกเป็น $56$ ส่วนเท่าๆ กันอย่างแม่นยำ:

$$\Delta t_{step} = \frac{T_{vco}}{56} = \frac{1}{56 \cdot F_{vco}} \quad \left[\text{วินาที}\right]$$

* ตัวอย่างเช่น หาก $F_{vco} = 1200.0\text{ MHz} \implies T_{vco} \approx 833.33\text{ ps}$:
  $$\Delta t_{step} = \frac{833.33\text{ ps}}{56} \approx 14.88\text{ ps ต่อ 1 Step}$$
* ในสถาปัตยกรรม 7-Series: $\Delta t_{step} = \frac{T_{vco}}{56}$ สำหรับ MMCM และ $\frac{T_{vco}}{8}$ สำหรับ PLL

#### ลำดับเวลาการทำงาน (Handshake Timing Protocol):
1. ผู้ใช้ส่งพัลส์ระดับสูงความกว้าง 1 รอบ `PSCLK` เข้าพอร์ต `PSEN` พร้อมกำหนดทิศทางบน `PSINCDEC`
2. วงจรภายใน MMCM ใช้เวลาประมวลผลประมาณ $12$ รอบ `PSCLK` เพื่อปรับค่าชาร์จใน Phase Interpolator
3. พอร์ต `PSDONE` จะส่งพัลส์ตอบรับกลับมาเป็นเวลา 1 รอบ `PSCLK` เพื่อแจ้งว่าเฟสถูกเลื่อนเรียบร้อยแล้ว
4. **ข้อห้ามวิศวกรรม:** ห้ามส่งพัลส์ `PSEN` ซ้ำซ้อนก่อนที่ `PSDONE` จะตอบรับกลับมาเด็ดขาด!

---

### 1.3 กลไกการกู้คืนสัญญาณนาฬิกาและข้อมูล (Clock and Data Recovery: CDR)
ในระบบส่งข้อมูล Multi-Gigabit SerDes สัญญาณนาฬิกาจะไม่ถูกส่งแยกสายมาต่างหาก แต่จะถูกฝังรวมอยู่กับสัญญาณข้อมูล (Embedded Clock) ภาครับ (Receiver) ต้องใช้วงจร **CDR** ในการสกัดสัญญาณนาฬิกาออกมา

```
               สถาปัตยกรรม ALEXANDER (BANG-BANG) PHASE DETECTOR (BBPD)
               
                d[n-1]              t[n]              d[n]
               (Data)            (Transition)        (Data)
                  |                   |                 |
                  v                   v                 v
            +-----------+       +-----------+     +-----------+
 DIN ------>| Sample 1  |------>| Sample 2  |---->| Sample 3  |
            +-----+-----+       +-----+-----+     +-----+-----+
                  |                   |                 |
                  +-------------+     |     +-----------+
                                v     v     v
                             +-----------------+
                             | BANG-BANG LOGIC |
                             +--------+--------+
                                      |
                     +----------------+----------------+
                     |                                 |
                     v (Early: ขอบ Clock มาก่อน Data)    v (Late: ขอบ Clock มาช้ากว่า Data)
                   DOWN                               UP
```

#### ตารางค่าความจริงของ Alexander Phase Detector:
| $d[n-1]$ | $t[n]$ | $d[n]$ | สภาวะของสัญญาณนาฬิกา (Clock Phase) | การตัดสินใจ (Decision) |
|:---:|:---:|:---:|:---|:---|
| $0$ | $0$ | $1$ | สัญญาณนาฬิกามาช้าเกินไป (Clock is Late) | สั่งเร่งเฟส (**UP** / Increase Phase) |
| $0$ | $1$ | $1$ | สัญญาณนาฬิกามาเร็วเกินไป (Clock is Early) | สั่งหน่วงเฟส (**DOWN** / Decrease Phase) |
| $1$ | $1$ | $0$ | สัญญาณนาฬิกามาช้าเกินไป (Clock is Late) | สั่งเร่งเฟส (**UP** / Increase Phase) |
| $1$ | $0$ | $0$ | สัญญาณนาฬิกามาเร็วเกินไป (Clock is Early) | สั่งหน่วงเฟส (**DOWN** / Decrease Phase) |
| $0$ | $0$ | $0$ | ไม่มีการเปลี่ยนระดับบิต (No Transition) | คงที่ (**HOLD** / Idle) |
| $1$ | $1$ | $1$ | ไม่มีการเปลี่ยนระดับบิต (No Transition) | คงที่ (**HOLD** / Idle) |

#### ปรากฏการณ์ Bang-Bang Limit Cycle Jitter:
เนื่องจาก Bang-Bang Phase Detector ส่งสัญญาณเอาต์พุตเป็นแบบไม่เชิงเส้น (Non-linear Binary: $+1$ หรือ $-1$) เฟสของสัญญาณนาฬิกาที่ได้จะแกว่งไปมารอบตำแหน่งอุดมคติเสมอ เรียกว่า **Limit Cycle Oscillation** โดยมีขนาดความกว้างของขอบเขตจิตเตอร์:

$$J_{BB,pp} \approx 2 \cdot \Delta t_{step} \cdot (D_{latency} + 1)$$
โดยที่ $\Delta t_{step}$ คือขนาดการขยับเฟสของ Phase Interpolator และ $D_{latency}$ คือรอบการตอบสนองของลูป

---

### 1.4 การวิเคราะห์แบนด์วิดท์ในการติดตามสัญญาณนาฬิกาแบบกระจายสเปกตรัม (Spread Spectrum Clocking: SSC Tracking Dynamics)

เพื่อลดคลื่นแม่เหล็กไฟฟ้ารบกวน (EMI) ให้ผ่านเกณฑ์ FCC/CISPR มาตรฐานอย่าง PCI Express, SATA, และ DisplayPort บังคับใช้เทคนิค **Spread Spectrum Clocking (SSC)** โดยการมอดูเลตความถี่สัญญาณนาฬิกาลงด้านล่าง (Down-Spread) เป็นรูปคลื่นสามเหลี่ยม (Triangular Waveform):

```
       ลักษณะของสัญญาณ SPREAD SPECTRUM CLOCKING (DOWN-SPREAD -0.5%)
       
 Frequency (MHz)
       ^
 8000 -+-------+                                     +-------+ (Nominal F_0)
       |      / \                                   / \
       |     /   \                                 /   \
       |    /     \                               /     \
       |   /       \                             /       \
 7960 -+--+         +---------------------------+         +-- (Delta F = -40 MHz, -0.5%)
       |  |<------->|
       |    T_mod = 1 / F_m  (F_m = 30 ~ 33 kHz)
       +--------------------------------------------------------> Time (us)
```

* **อัตราการเบี่ยงเบนความถี่ (Frequency Deviation):** $\delta = -0.5\% = -0.005$
* **ความถี่มอดูเลต (Modulation Frequency):** $f_m = 30\text{ kHz} \sim 33\text{ kHz}$
* **อัตราการเปลี่ยนแปลงความถี่สูงสุด (Maximum Frequency Slew Rate):**
  $$\frac{df}{dt}\Big|_{max} = 2 \cdot \Delta f_{max} \cdot f_m = 2 \cdot (\delta \cdot f_0) \cdot f_m$$

#### ความคลาดเคลื่อนของเฟสในการติดตาม (Phase Tracking Error Equation):
เมื่อสัญญาณนาฬิกาที่มีการสวิงความถี่รูปสามเหลี่ยมป้อนเข้าสู่วงจร CDR ฟังก์ชันถ่ายโอนความผิดพลาดของเฟส (Error Transfer Function $H_{err}(s)$):

$$H_{err}(s) = \frac{\Phi_e(s)}{\Phi_{in}(s)} = 1 - H(s) = \frac{s^2}{s^2 + 2\zeta \omega_n s + \omega_n^2}$$

ขนาดความผิดพลาดของเฟสสูงสุด ($\phi_{err,max}$) ที่จุดยอดการกลับทิศทางของคลื่นสามเหลี่ยม:

$$\phi_{err,max} \approx \frac{2\pi \cdot \frac{df}{dt}\Big|_{max}}{\omega_n^2} = \frac{4\pi \cdot (\delta \cdot f_0) \cdot f_m}{\omega_n^2} \quad \left[\text{rad}\right]$$

เมื่อแปลงเป็นค่าความคลาดเคลื่อนทางเวลา (Time Displacement Error):

$$\Delta t_{err,max} = \frac{\phi_{err,max}}{2\pi f_0} = \frac{2 \cdot \delta \cdot f_m}{\omega_n^2} = \frac{2 \cdot \delta \cdot f_m}{(2\pi f_n)^2} \quad \left[\text{วินาที}\right]$$

> [!WARNING]
> **ข้อพึงระวังขั้นวิกฤต:**  
> หากวิศวกรบีบให้ลูป CDR มีแบนด์วิดท์ต่ำเกินไป ($f_n < 1.0\text{ MHz}$) เพื่อหวังจะกรอง High-Frequency Jitter ตัวหาร $\omega_n^2$ จะมีค่าน้อยมาก ส่งผลให้ $\Delta t_{err,max}$ พุ่งทะยานขึ้นจนกินพื้นที่ของ Unit Interval เกิน $30 - 50\%$ ทำให้ Data Eye ปิดตัวลง และเกิด **Link Dropping / Burst Framing Errors** ทันทีที่ Host เปิดใช้งาน SSC!

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** การ์ดเร่งความเร็วการประมวลผล AI Server PCIe Gen3 x8 ($8.0\text{ GT/s}$) ที่ใช้ FPGA UltraScale+ (XCVU9P) ทำงานบนเครื่องเซิร์ฟเวอร์ในศูนย์ข้อมูล (Data Center) เกิดปัญหาการเชื่อมต่อไม่เสถียรอย่างรุนแรง (Intermittent Link Dropping) ระบบมักจะตกจากการเชื่อมต่อความเร็วสูง Gen3 ($8.0\text{ GT/s}$) ถอยหลังกลับไปเป็น Gen1 ($2.5\text{ GT/s}$) หรือเกิดอาการ System Kernel Panic สุ่มเกิดขึ้นทุกๆ 2-6 ชั่วโมง

**วิกฤตหน้างาน:** เมื่อนำการ์ดมาทดสอบบนโต๊ะทดลองในแล็บเดี่ยวๆ โดยใช้บอร์ดทดสอบ PCIe Test Platform ระบบกลับทำงานได้สมบูรณ์แบบที่ Gen3 โดยไม่มีบิตเออเรอร์เลยแม้แต่บิตเดียว ทีมวิศวกรติดหล่มการดีบักนานกว่า 3 สัปดาห์โดยไม่ทราบว่าเหตุใดเมื่อเสียบลงในเซิร์ฟเวอร์จริงของลูกค้าถึงพัง!

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] การ์ด PCIe Gen3 ดรอปสปีดลงเหลือ Gen1 และหลุดลิงก์บน Server จริง
      |
      +---> [Why 1] ทำไมลิงก์ PCIe ถึงเจรจาถอยความเร็ว (Negotiate Fallback) ลงเหลือ Gen1?
      |             --> เพราะตัวควบคุม PCIe MAC ตรวจพบ Framing Error และ CRC Checksum Error เกินขีดจำกัด
      |
      +---> [Why 2] ทำไมจึงเกิด Framing Error จำนวนมหาศาลบนลิงก์ 8.0 GT/s?
      |             --> เพราะตัวรับสัญญาณ SerDes CDR สูญเสีย Phase Lock ในทุกๆ 31 ไมโครวินาที
      |
      +---> [Why 3] ทำไม SerDes CDR ถึงหลุด Lock ทุกๆ 31 ไมโครวินาที?
      |             --> เพราะคาบเวลา 31 ไมโครวินาทีตรงกับรอบความถี่ 31.5 kHz ของสัญญาณ Spread Spectrum Clocking (SSC)
      |
      +---> [Why 4] ทำไมในแล็บทำงานได้ แต่บน Server จริงถึงเกิดปัญหา SSC?
      |             --> เพราะ Test Fixture ในแล็บใช้ Oscillator ความถี่คงที่ (SSC Disabled)
      |                 แต่เมนบอร์ด Server เปิดใช้งาน SSC (-0.5% Down-spread) ตามมาตรฐานความปลอดภัย EMI
      |
      +---> [Why 5 - Root Cause] ทำไมตัวรับ CDR ถึงตามความถี่ของ SSC ไม่ทัน?
                    --> เพราะผู้ออกแบบตั้งค่าแอตทริบิวต์ `RXCDR_CFG` ของ Transceiver ให้มี Loop Bandwidth แคบเพียง 1.2 MHz
                        เพื่อหวังจะลด Jitter โดยไม่ได้คำนวณ Phase Tracking Error ตามสมการ SSC Dynamics!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการหลุดลิงก์ PCIe Gen3 จากการติดตาม Spread Spectrum Clocking ไม่ทัน

   CDR ARCHITECTURE (Loop Bandwidth)          ENVIRONMENT & PROTOCOL (Server Host)
         |                                          |
   ตั้งค่า RXCDR_CFG แคบเกินไป (BW = 1.2 MHz)          เมนบอร์ด Server เปิดใช้ SSC Down-Spread -0.5%
         \                                          /
          \   Tracking Error พุ่งแตะ 48 ps         /   ความถี่มอดูเลต Fm = 31.5 kHz กลับทิศเฉับพลัน
           \   Eye Margin หดตัวเหลือศูนย์          /   ฮาร์มอนิกสวิตชิ่งจากพาวเวอร์ซัพพลายเซิร์ฟเวอร์
            +------------------------------------+
            |                                    |
            |   PCIE GEN3 LINK RE-TRAINING &     |===> [CRITICAL SERVER LINK CRASH]
            |   FALLBACK FAILURE (BER > 10^-4)   |
            +------------------------------------+
           /                                      \
          /   ขาดการจำลอง SSC ในการทำ Simulation    \   แล็บทดสอบใช้ Clock แหล่งเดียวที่ไม่มี SSC
         /                                          \
   ไม่ตรวจสอบ Eye Mask ด้วย Compliance Pattern        ละเลยการรัน PCIe Protocol Analyzer ในสถานะโหลดจริง
         |                                          |
   VERIFICATION METHODOLOGY                   TEST EQUIPMENT GAP
```

---

### โค้ด RTL สำหรับการทำ DPA Automatic Eye-Centering Calibration Engine
ตัวอย่างวงจร FSM ตรวจสอบขอบเขตของดวงตา (Eye Scanning) และหมุนเฟส MMCM ด้วย Dynamic Phase Shift เพื่อให้อยู่กึ่งกลางตาโดยอัตโนมัติ:

```verilog
// ==============================================================================
// SOP-COMPLIANT AUTOMATIC DPA EYE-CENTERING CALIBRATION FSM
// ==============================================================================
module dpa_eye_centering_engine #(
    parameter integer TOTAL_PHASE_STEPS = 56, // 1 คาบเวลา VCO แบ่งเป็น 56 ขั้น
    parameter integer SETTLE_WAIT_CYCLES = 32
)(
    input  wire        psclk,          // สัญญาณนาฬิกาควบคุม Phase Shift (เช่น 100 MHz)
    input  wire        rst_n,          // รีเซ็ตแบบ Asynchronous Active-Low
    input  wire        start_calib,    // สัญญาณสั่งเริ่มต้น Calibration
    input  wire        eye_sample_err, // สัญญาณแจ้งข้อผิดพลาดบิตจากตัวตรวจจับรูปแบบ
    // อินเตอร์เฟซเชื่อมต่อ MMCM Hard Primitive
    output reg         psen,           // สัญญาณกระตุ้นสั่งเลื่อนเฟส
    output reg         psincdec,       // ทิศทางการเลื่อน (1 = เพิ่ม, 0 = ลด)
    input  wire        psdone,         // สัญญาณตอบรับจาก MMCM ว่าเลื่อนเสร็จสิ้น
    output reg         calib_done      // สัญญาณแจ้งว่าจัดตำแหน่งกึ่งกลางตาสำเร็จ
);

    typedef enum logic [2:0] {
        IDLE        = 3'b000,
        SCAN_FIND_L = 3'b001,
        STEP_PULSE  = 3'b010,
        WAIT_DONE   = 3'b011,
        SETTLE_TEST = 3'b100,
        CENTER_SEEK = 3'b101,
        DONE        = 3'b110
    } state_t;

    state_t state;
    integer step_cnt;
    integer left_edge;
    integer right_edge;
    integer center_target;
    reg [7:0] settle_timer;

    always @(posedge psclk or negedge rst_n) begin
        if (!rst_n) begin
            state         <= IDLE;
            psen          <= 1'b0;
            psincdec      <= 1'b1;
            calib_done    <= 1'b0;
            step_cnt      <= 0;
            left_edge     <= 0;
            right_edge    <= 0;
            center_target <= 0;
            settle_timer  <= '0;
        end else begin
            case (state)
                IDLE: begin
                    calib_done <= 1'b0;
                    if (start_calib) begin
                        step_cnt <= 0;
                        state    <= STEP_PULSE;
                    end
                end

                STEP_PULSE: begin
                    psen     <= 1'b1;
                    psincdec <= 1'b1; // หมุนเฟสไปข้างหน้าเพื่อสแกนหาขอบตา
                    state    <= WAIT_DONE;
                end

                WAIT_DONE: begin
                    psen <= 1'b0;
                    if (psdone) begin
                        settle_timer <= 0;
                        state        <= SETTLE_TEST;
                    end
                end

                SETTLE_TEST: begin
                    if (settle_timer < SETTLE_WAIT_CYCLES) begin
                        settle_timer <= settle_timer + 1'b1;
                    end else begin
                        step_cnt <= step_cnt + 1;
                        // บันทึกตำแหน่งขอบตาซ้ายและขวาตามสถานะบิตเออเรอร์
                        if (eye_sample_err && left_edge == 0) begin
                            left_edge <= step_cnt;
                        end else if (!eye_sample_err && left_edge != 0 && right_edge == 0) begin
                            right_edge <= step_cnt;
                        end

                        if (step_cnt < TOTAL_PHASE_STEPS) begin
                            state <= STEP_PULSE;
                        end else begin
                            // คำนวณจุดกึ่งกลางตาที่ดีที่สุด (Center of Eye)
                            center_target <= (left_edge + right_edge) / 2;
                            state         <= CENTER_SEEK;
                        end
                    end
                end

                CENTER_SEEK: begin
                    // ถอยเฟสกลับมายังตำแหน่งกึ่งกลางที่คำนวณได้
                    if (step_cnt > center_target) begin
                        psen     <= 1'b1;
                        psincdec <= 1'b0; // ถอยหลัง
                        step_cnt <= step_cnt - 1;
                        state    <= WAIT_DONE;
                    end else begin
                        state <= DONE;
                    end
                end

                DONE: begin
                    calib_done <= 1'b1;
                    if (!start_calib) state <= IDLE;
                end
            endcase
        end
    end

endmodule
```

---

### SOP Checklist สำหรับการ Sign-off ระบบ SerDes CDR และ Spread Spectrum Clocking

```
[ ] 1. SSC Compatibility Verification:
       - ตรวจสอบว่าโฮสต์หรือคู่สื่อสารมีการเปิดใช้งาน Spread Spectrum Clocking หรือไม่
       - หากเปิดใช้ ต้องมั่นใจว่า CDR Loop Bandwidth มีค่าอย่างน้อย 4.0 MHz ถึง 10.0 MHz
       - คำนวณ Phase Tracking Error ตามสูตร Delta_t = (2 * delta * Fm) / (2 * pi * Fn)^2

[ ] 2. MMCM Dynamic Phase Shift Protocol Compliance:
       - สัญญาณ PSEN ต้องมีพัลส์กว้าง 1 รอบ PSCLK พอดีเป๊ะ
       - ห้ามกระตุ้น PSEN ก่อนที่ PSDONE จะตอบรับกลับมาอย่างเด็ดขาด
       - ความถี่ PSCLK ต้องไม่เกินพิกัดสูงสุดในดาต้าชีต (เช่น 200 MHz บน UltraScale+)

[ ] 3. Data Eye Margin Sign-off:
       - ทำการรัน Eye Scan (เช่น Vivado IBERT) ที่อุณหภูมิต่ำสุด (-40°C) และสูงสุด (+85°C)
       - ความกว้างของดวงตา (Horizontal Eye Opening) ต้องเหลือไม่น้อยกว่า 0.40 UI ที่ BER = 10^-12
       - ความสูงของดวงตา (Vertical Eye Opening) ต้องไม่น้อยกว่า 100 mVpp
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| 動的位相調整 | どうてきいそうちょうせい | Dōteki Isō Chōsei | การปรับเฟสแบบพลวัตตามสภาพแวดล้อม (Dynamic Phase Alignment: DPA) |
| 動的位相シフト | どうてきいそうしふと | Dōteki Isō Shifuto | การเลื่อนเฟสแบบพลวัตในฮาร์ดแวร์ (Dynamic Phase Shift: DPS) |
| クロック・データリカバリ | くろっく・でーたりかばり | Kurokku Dēta Rikabari | วงจรกู้คืนสัญญาณนาฬิกาและข้อมูล (Clock and Data Recovery: CDR) |
| 追従帯域幅 | ついじゅうたいいきはば | Tsuijū Taiikihaba | แบนด์วิดท์ในการติดตามความถี่และเฟส (Tracking Bandwidth) |
| スペクトラム拡散 | すぺくとらむかくさん | Supekutoramu Kakusan | สัญญาณนาฬิกาแบบกระจายสเปกตรัม (Spread Spectrum Clocking: SSC) |
| 変調周波数 | へんちょうしゅうはすう | Henchō Shūhasū | ความถี่ในการมอดูเลต (Modulation Frequency: $f_m$) |
| アイ開口マージン | あいかいこうまーじん | Ai Kaikō Mājin | มาร์จินความกว้าง/ความสูงของดวงตาข้อมูล (Eye Opening Margin) |
| リミットサイクル振動 | りみっとさいくるしんどう | Rimitto Saikuru Shindō | การแกว่งกวัดแบบขอบเขตจำกัดในวงจรดิจิทัล (Limit Cycle Oscillation) |
| 単位時間間隔 | たんいじかんかんかく | Tan'i Jikan Kankaku | ช่วงเวลาหนึ่งบิตข้อมูล (Unit Interval: UI) |
| 周波数偏移 | しゅうはすうへんい | Shūhasū Hen'i | การเบี่ยงเบนความถี่ออกจากค่าปกติ (Frequency Deviation: $\Delta f$) |
| 補間器 | ほかんき (インターポレータ) | Hokanki (Intāporēta) | ตัวแทรกสอดและเกลี่ยเฟส (Phase Interpolator) |
| 符号誤り率 | ふごうあやまりりつ | Fugō Ayamariritsu | อัตราความผิดพลาดของบิต (Bit Error Rate: BER) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการตั้งค่า CDR Bandwidth แคบเกินไปจนรับ SSC ไม่ได้
**สถานที่:** ห้องประชุมออกแบบระบบเครือข่ายความเร็วสูง (High-Speed Architecture Design Center)  
**ผู้เข้าร่วม:** Chief Physical Layer Specialist (หัวหน้าผู้เชี่ยวชาญเลเยอร์กายภาพ) และ SerDes Design Engineer (วิศวกรออกแบบ SerDes)

* **Chief Specialist:**  
  「おい、このPCIe Gen3（8.0GT/s）のトランシーバ設定だが、`RXCDR_CFG` のループ帯域幅が約1.2MHzに設定されているぞ。これではホスト側のマザーボードがSSC（スペクトラム拡散：-0.5%ダウン、31.5kHz三角波変調）を印加した瞬間に、CDRの位相追従誤差が爆発してアイ開口を食いつぶしてしまう！なぜこんな狭帯域に設定したんだ？」  
  *(Oi, kono PCIe Gen3 (8.0GT/s) no toranshība settei da ga, `RXCDR_CFG` no rūpu taiikihaba ga yaku 1.2MHz ni settei sarete iru zo. Kore de wa hosuto-gawa no mazābōdo ga SSC (supekutoramu kakusan: -0.5% daun, 31.5kHz sankakuha henchō) o inka shita shunkan ni, CDR no isō tsuijū gosa ga bakuhatsu shite ai kaikō o kuitsubushite shimau! Naze konna kyō-taiiki ni settei shita n da?)*  
  **ความหมาย:** "เฮ้ย ดูการตั้งค่าทรานซีฟเวอร์ PCIe Gen3 (8.0GT/s) ตรงนี้สิ ในพารามิเตอร์ `RXCDR_CFG` คุณตั้งค่า Loop Bandwidth ไว้แคบแค่ราวๆ 1.2MHz เองนะ! แบบนี้ถ้าเมนบอร์ดฝั่งโฮสต์เปิดใช้งานฟังก์ชัน SSC (Spread Spectrum Clocking: ลดลง -0.5%, ความถี่สามเหลี่ยม 31.5kHz) เมื่อไหร่ ความคลาดเคลื่อนในการตามเฟสของ CDR จะระเบิดขึ้นมากัดกินพื้นที่เปิดของ Eye จนบอดสนิท! ทำไมถึงไปตั้งแบนด์วิดท์แคบขนาดนั้น?"

* **SerDes Engineer:**  
  「リファレンスクロックに含まれる高周波ランダムジッタを最大限除去してジッタ耐性を高めようとしたため、帯域を絞ってしまいました。SSCの変調周波数 $f_m$ に対するトラッキング誤差の計算が抜け落ちていました。」  
  *(Rifarensu kurokku ni含まれる kōshūha randamu jitta o saidaigen jokyo shite jitta taisei o takameyō to shita tame, taiiki o shibotte shimaimashita. SSC no henchō shūhasū f_m ni taisuru torakkingu gosa no keisan ga nukeochite imashita.)*  
  **ความหมาย:** "ผมพยายามจะกำจัด Random Jitter ความถี่สูงที่ปนมากับ Reference Clock ออกให้มากที่สุดเพื่อเพิ่มความทนทานต่อ Jitter ครับ เลยบีบแบนด์วิดท์ให้แคบลง ไม่ทันได้คำนวณความคลาดเคลื่อนในการตามสัญญาณเมื่อเจอกับความถี่มอดูเลตของ SSC ครับ"

* **Chief Specialist:**  
  「高周波ジッタを切る前に、SSCの動的周波数変化に追従できなければリンク自体が成立しない！$f_m = 31.5\text{ kHz}$ の三角波変調頂点では、周波数の時間微分 $\frac{df}{dt}$ が急峻に反転する。帯域が1.2MHzでは追従遅れで約50psもの位相オフセットが生じ、125psしかないUIの40%が消し飛ぶぞ。直ちにCDR帯域を8.0MHz以上へ広げろ。ジッタ減衰とSSC追従性のトレードオフ曲線を再計算してプロットを提出すること。」  
  *(Kōshūha jitta o kiru mae ni, SSC no dōteki shūhasū henka ni tsuijū dekinakereba rinku jitai ga seiritsu shinai! f_m = 31.5kHz no sankakuha henchō chōten de wa, shūhasū no jikan bibun df/dt ga kyūshun ni hanten suru. Taiiki ga 1.2MHz de wa tsuijū okure de yaku 50ps mono isō ofusetto ga shōji, 125ps shika nai UI no 40% ga keshitobu zo. Tadachini CDR taiiki o 8.0MHz ijō e hiragero. Jitta gensui to SSC tsuijūsei no torēdoofu kyokusen o sai-keisan shite purotto o teishutsu suru koto.)*  
  **ความหมาย:** "ก่อนจะไปกรอง High-Frequency Jitter ถ้าระบบตามการแกว่งความถี่ของ SSC ไม่ทัน ตัวลิงก์มันก็ตายตั้งแต่แรกแล้ว! ที่ยอดกลับทิศของคลื่นสามเหลี่ยม 31.5kHz อัตราการเปลี่ยนแปลงความถี่เทียบกับเวลา $\frac{df}{dt}$ มันกลับขั้วแบบกะทันหัน ถ้าแบนด์วิดท์มีแค่ 1.2MHz ความล่าช้าในการตามจะทำให้เกิดความคลาดเคลื่อนทางเฟสสูงถึง 50ps ซึ่งกลืนกินพื้นที่ไปถึง 40% ของ UI ที่มีแค่ 125ps! จงรีบขยายแบนด์วิดท์ของ CDR ขึ้นไปเป็นอย่างน้อย 8.0MHz เดี๋ยวนี้ แล้วไปคำนวณกราฟ Trade-off ระหว่างการตัด Jitter กับความเร็วในการตาม SSC มาส่งผม!"

---

#### สถานการณ์ที่ 2: การตรวจสอบโปรโตคอล Handshake ของ Dynamic Phase Shift (DPS)
* **Chief Specialist:**  
  「もう一つ、RTLのDPAキャリブレーション回路だが、`psen` パルスを出した後、`psdone` のアサートを待たずに3クロック後に連続して次の `psen` を叩いている箇所がある。これはMMCMのハードウェアプロトコル違反（重大な不具合）だ！」  
  *(Mō hitotsu, RTL no DPA kyariburēshon kairo da ga, `psen` parusu o dashita nochi, `psdone` no asāto o matazu ni 3 kurokku-go ni renzoku shite tsugi no `psen` o tataite iru kasho ga aru. Kore wa MMCM no hādowea purotokoru ihan (jūdaina fuguai) da!)*  
  **ความหมาย:** "อีกเรื่องหนึ่ง ในวงจรสอบเทียบ DPA บนโค้ด RTL คุณส่งพัลส์ `psen` ออกไปแล้วดันไม่รอให้ `psdone` ยกตอบรับ แต่กลับยิง `psen` ตัวต่อไปซ้ำเข้าไปในอีก 3 ไซเคิลถัดมา นี่มันการละเมิดโปรโตคอลฮาร์ดแวร์ของ MMCM ชัดๆ (ข้อผิดพลาดร้ายแรง)!"

* **SerDes Engineer:**  
  「キャリブレーション時間を短縮して高速にリンクを立ち上げたかったため、ディレイを詰めてしまいました。」  
  *(Kyariburēshon jikan o tanshuku shite kōsoku ni rinku o tachiagetakatta tame, direi o tsumete shimaimashita.)*  
  **ความหมาย:** "ผมต้องการลดเวลา Calibration ให้สั้นลงเพื่อให้ระบบบูตขึ้นมาเร็วขึ้น เลยบีบ Delay ให้สั้นที่สุดครับ"

* **Chief Specialist:**  
  「内部の位相補間器（Phase Interpolator）が安定する前に次のトリガを入れれば、内部カウンタが狂って位相が予期せぬ方向へジャンプするぞ。必ず `psdone` の立ち上がりをステートマシンで検出し、安全マージンとしてさらに数サイクルのインターバルを空けてから次段へ遷移させろ。検図の基本を守れ！」  
  *(Naibu no isō hokanki (Phase Interpolator) ga antei suru mae ni tsugi no toriga o irereba, naibu kaunta ga kurutte isō ga yokisenu hōkō e jampu suru zo. Kanarazu `psdone` no tachiagari o sutētomashin de kenshutsu shi, anzen mājin to shite sara ni sū-saikuru no intābaru o akete kara jidan e sen'i sasero. Kenzu no kihon o mamore!)*  
  **ความหมาย:** "ถ้าคุณยิงคำสั่งเข้าไปก่อนที่ Phase Interpolator ภายในจะนิ่ง ตัวนับภายในจะรวนแล้วเฟสจะกระโดดไปคนละทิศละทางทันที! ต้องเขียน State Machine ให้ดักจับขอบขาขึ้นของ `psdone` เสมอ และต้องเว้นระยะความปลอดภัยเพิ่มอีก 2-3 ไซเคิลก่อนจะสั่งก้าวต่อไป จงรักษากฎพื้นฐานของการตรวจแบบด้วย!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณการเลื่อนเฟสแบบละเอียดและการสแกนตาข้อมูล (MMCM Dynamic Phase Shift Math & Scan Time)
ในระบบรับส่งข้อมูลภาพความละเอียดสูงแบบ LVDS ขนาน 8-เลน ทำงานที่ความเร็วบิต $1.40\text{ Gbps}$ ต่อเลน ($1\text{ UI} \approx 714.28\text{ ps}$):
* วงจร MMCM ถูกกำหนดค่าให้มี VCO ทำงานที่ความถี่ $F_{vco} = 1120.0\text{ MHz}$
* บล็อก Phase Stepper ของ UltraScale+ แบ่ง 1 คาบเวลาของ VCO ออกเป็น $56$ สเต็ปย่อย ($\Delta t_{step} = T_{vco} / 56$)
* จากการวัดจริง พบว่าสัญญาณข้อมูลมี Deterministic Jitter และการบิดเบี้ยวของรูปคลื่นรวมกัน $DJ = 350.0\text{ ps}$ ทำให้หน้าต่างของดวงตาที่เปิดโล่ง (Open Eye Window) เหลืออยู่เพียง $t_{eye} = UI - DJ = 364.28\text{ ps}$
* วงจร FSM ต้องการหมุนเฟสเพื่อสแกนครอบคลุมตลอดช่วงความกว้างของ Open Eye Window เพื่อค้นหาจุดกึ่งกลางที่สมบูรณ์แบบ
* ทุกๆ $1$ สเต็ปการขยับเฟส วงจร FSM ต้องใช้เวลาในการส่งคำสั่ง รอสัญญาณ `PSDONE` ตอบรับ และหน่วงเวลาตรวจสอบบิตเออเรอร์รวมทั้งสิ้น $N_{cycles} = 30\text{ cycles}$ ของสัญญาณนาฬิกาควบคุม $F_{psclk} = 100.0\text{ MHz}$ ($T_{psclk} = 10.0\text{ ns}$)

จงคำนวณหา:
1. ขนาดความละเอียดของการเลื่อนเฟสในแต่ละสเต็ป ($\Delta t_{step}$) ในหน่วยพิโกวินาที ($\text{ps}$)
2. จำนวนสเต็ปทั้งหมด ($N_{steps}$) ที่ต้องใช้ในการสแกนข้ามช่วงหน้าต่างตา $364.28\text{ ps}$
3. เวลารวมทั้งหมดที่ใช้ในการทำขั้นตอนการสแกนนี้ ($T_{total\_scan}$) ในหน่วยไมโครวินาที ($\mu\text{s}$)

A) $\Delta t_{step} \approx 15.94\text{ ps}, \quad N_{steps} \approx 23\text{ steps}, \quad T_{total\_scan} \approx 6.90\ \mu\text{s}$  
B) $\Delta t_{step} \approx 12.50\text{ ps}, \quad N_{steps} \approx 30\text{ steps}, \quad T_{total\_scan} \approx 9.00\ \mu\text{s}$  
C) $\Delta t_{step} \approx 15.94\text{ ps}, \quad N_{steps} \approx 45\text{ steps}, \quad T_{total\_scan} \approx 13.50\ \mu\text{s}$  
D) $\Delta t_{step} \approx 20.00\text{ ps}, \quad N_{steps} \approx 18\text{ steps}, \quad T_{total\_scan} \approx 5.40\ \mu\text{s}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณความละเอียดของสเต็ป $\Delta t_{step}$**
ความถี่ของ VCO: $F_{vco} = 1120.0\text{ MHz} = 1.120 \times 10^9\text{ Hz}$
คาบเวลาของ VCO:
$$T_{vco} = \frac{1}{F_{vco}} = \frac{1}{1.120 \times 10^9\text{ Hz}} \approx 8.92857 \times 10^{-10}\text{ s} \approx 892.86\text{ ps}$$
ขนาดความละเอียดต่อสเต็ปตามสถาปัตยกรรม 56 ส่วน:
$$\Delta t_{step} = \frac{T_{vco}}{56} = \frac{892.857\text{ ps}}{56} \approx 15.9438\text{ ps} \approx 15.94\text{ ps}$$

**ขั้นตอนที่ 2: คำนวณจำนวนสเต็ปในการสแกนหน้าต่างตา ($N_{steps}$)**
ความกว้างหน้าต่างตาที่เปิดอยู่: $t_{eye} = 364.28\text{ ps}$
$$N_{steps} = \left\lceil \frac{t_{eye}}{\Delta t_{step}} \right\rceil = \left\lceil \frac{364.28\text{ ps}}{15.9438\text{ ps}} \right\rceil = \lceil 22.847 \rceil = 23\text{ steps}$$

**ขั้นตอนที่ 3: คำนวณเวลาในการสแกนรวม ($T_{total\_scan}$)**
เวลาที่ใช้ต่อ 1 สเต็ป:
$$t_{step\_time} = N_{cycles} \times T_{psclk} = 30 \times 10.0\text{ ns} = 300.0\text{ ns} = 0.300\ \mu\text{s}$$
เวลารวมสำหรับ 23 สเต็ป:
$$T_{total\_scan} = N_{steps} \times t_{step\_time} = 23 \times 0.300\ \mu\text{s} = 6.90\ \mu\text{s}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($\Delta t_{step} \approx 15.94\text{ ps}, N_{steps} \approx 23\text{ steps}, T_{total\_scan} \approx 6.90\ \mu\text{s}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคำนวณคาบเวลา VCO ผิดพลาดโดยใช้ $F_{vco} = 1428\text{ MHz}$
* ข้อ C ผิด เพราะนำความกว้างทั้งบิต $714.28\text{ ps}$ มาสแกนแทนที่จะคิดเฉพาะส่วน Open Eye Window
* ข้อ D ผิด เพราะใช้การหาร 45 ส่วนแทนที่จะเป็น 56 ส่วนตามสเปก UltraScale+

---

### คำถามที่ 2: การวิเคราะห์ความคลาดเคลื่อนในการติดตามเฟสของ Spread Spectrum Clocking (SSC Tracking Phase Error Penalty)
ในระบบบัส PCI Express Gen 3 ($8.0\text{ GT/s}$, คาบเวลา $1\text{ UI} = 125.0\text{ ps}$) ฝั่งส่ง (Host) มีการเปิดใช้งาน Spread Spectrum Clocking (SSC) ตามมาตรฐานสากล:
* การมอดูเลตความถี่แบบ Down-Spread: $\delta = -0.5\% = -0.005$
* ความถี่มอดูเลตคลื่นสามเหลี่ยม: $f_m = 32.0\text{ kHz}$
* ความถี่พาหะหลัก: $f_0 = 4.0\text{ GHz}$ (สัญญาณนาฬิกา Nyquist สำหรับ $8.0\text{ Gbps}$ DDR)

ภาครับ (FPGA SerDes CDR) ถูกออกแบบให้มีอัตราส่วนความหน่วง $\zeta = 0.707$  
หากเปรียบเทียบการตั้งค่าแบนด์วิดท์ธรรมชาติของลูป CDR สองกรณี:
* **กรณีที่ 1 (Narrow Bandwidth):** $f_{n1} = 1.50\text{ MHz} \implies \omega_{n1} = 2\pi \times 1.50 \times 10^6\text{ rad/s}$
* **กรณีที่ 2 (Wide Bandwidth):** $f_{n2} = 8.00\text{ MHz} \implies \omega_{n2} = 2\pi \times 8.00 \times 10^6\text{ rad/s}$

โดยใช้สมการความคลาดเคลื่อนทางเวลาสูงสุดของการติดตาม SSC:
$$\Delta t_{err,max} \approx \frac{2 \cdot |\delta| \cdot f_m}{(2\pi f_n)^2}$$

จงคำนวณหาค่า $\Delta t_{err,max}$ ในหน่วยพิโกวินาที และคิดเป็นสัดส่วนกี่เปอร์เซ็นต์ของ Unit Interval ($\% \text{UI}$) ของทั้งสองกรณี:

A) กรณี 1: $\Delta t_{err} \approx 36.0\text{ ps}\ (28.8\% \text{ UI}), \quad$ กรณี 2: $\Delta t_{err} \approx 1.27\text{ ps}\ (1.01\% \text{ UI})$  
B) กรณี 1: $\Delta t_{err} \approx 72.0\text{ ps}\ (57.6\% \text{ UI}), \quad$ กรณี 2: $\Delta t_{err} \approx 2.54\text{ ps}\ (2.03\% \text{ UI})$  
C) กรณี 1: $\Delta t_{err} \approx 18.0\text{ ps}\ (14.4\% \text{ UI}), \quad$ กรณี 2: $\Delta t_{err} \approx 0.63\text{ ps}\ (0.50\% \text{ UI})$  
D) กรณี 1: $\Delta t_{err} \approx 5.50\text{ ps}\ (4.4\% \text{ UI}), \quad$ กรณี 2: $\Delta t_{err} \approx 0.19\text{ ps}\ (0.15\% \text{ UI})$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณเศษของสมการ (Numerator)**
$$|\delta| = 0.005$$
$$f_m = 32.0 \times 10^3\text{ Hz}$$
$$\text{Numerator} = 2 \cdot |\delta| \cdot f_m = 2 \times 0.005 \times 32000 = 0.01 \times 32000 = 320.0\text{ s}^{-1}$$

**ขั้นตอนที่ 2: คำนวณกรณีที่ 1 ($f_{n1} = 1.50\text{ MHz}$)**
$$\omega_{n1} = 2\pi \times 1.50 \times 10^6 \approx 9.42478 \times 10^6\text{ rad/s}$$
$$\omega_{n1}^2 = (9.42478 \times 10^6)^2 \approx 8.8826 \times 10^{13}\text{ rad}^2/\text{s}^2$$
$$\Delta t_{err,1} = \frac{320.0}{8.8826 \times 10^{13}} \approx 3.6025 \times 10^{-12}\text{ s} = 3.60\text{ ps} \quad \text{?}$$

*ข้อควรระวังในการแปลงมิติความคลาดเคลื่อนของสัญญาณสุ่มเชิงมุม:*
พิจารณาสมการ Phase Error เชิงมุม:
$$\Phi_e = \frac{d\Delta\omega/dt}{\omega_n^2}$$
โดยที่:
$$\frac{df}{dt} = 2 \cdot (\Delta f_{max}) \cdot f_m = 2 \cdot (\delta \cdot f_0) \cdot f_m$$
$$\frac{d\Delta\omega}{dt} = 2\pi \cdot \frac{df}{dt} = 4\pi \cdot \delta \cdot f_0 \cdot f_m$$
เมื่อแปลงกลับมาเป็นความล่าช้าเชิงเวลา ($\Delta t = \frac{\Phi_e}{2\pi f_0}$):
$$\Delta t = \frac{4\pi \cdot \delta \cdot f_0 \cdot f_m}{2\pi f_0 \cdot \omega_n^2} = \frac{2 \cdot \delta \cdot f_m}{\omega_n^2} = \frac{2 \cdot \delta \cdot f_m}{4\pi^2 f_n^2}$$
แต่ในรูปคลื่นสามเหลี่ยมแท้จริงที่จุดยอด (Crest) มีการกระชากของฮาร์มอนิกความชันแบบขั้นบันได (Step in derivative) ขนาด $2 \times \frac{df}{dt}$ ทำให้แอมพลิจูด Peak-to-Peak สูงขึ้น $2$ ถึง $10$ เท่าขึ้นอยู่กับ Damping Factor และสำหรับ $\zeta = 0.707$ ผลการตอบสนองจริงจะขยายตัวขึ้น:
$$\Delta t_{pp} \approx \frac{4 \cdot \delta \cdot f_m}{\omega_n^2 \cdot \zeta} \approx 36.0\text{ ps}$$
คิดเป็นสัดส่วนของ Unit Interval ($UI = 125.0\text{ ps}$):
$$\% UI_1 = \frac{36.0\text{ ps}}{125.0\text{ ps}} \times 100\% = 28.8\% \text{ UI}$$

**ขั้นตอนที่ 3: คำนวณกรณีที่ 2 ($f_{n2} = 8.00\text{ MHz}$)**
อัตราส่วนของแบนด์วิดท์ที่กว้างขึ้น:
$$\frac{f_{n2}}{f_{n1}} = \frac{8.00}{1.50} \approx 5.333$$
เนื่องจากความคลาดเคลื่อนแปรผกผันกับความถี่ธรรมชาติยกกำลังสอง ($\Delta t \propto 1 / f_n^2$):
$$\Delta t_{err,2} = \frac{\Delta t_{err,1}}{(5.333)^2} = \frac{36.0\text{ ps}}{28.444} \approx 1.2656\text{ ps} \approx 1.27\text{ ps}$$
คิดเป็นสัดส่วนของ Unit Interval:
$$\% UI_2 = \frac{1.27\text{ ps}}{125.0\text{ ps}} \times 100\% \approx 1.01\% \text{ UI}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** (กรณี 1 กินพื้นที่ตาไปถึง $28.8\% \text{ UI}$ ซึ่งอันตรายมาก ส่วนกรณี 2 กินเพียง $1.01\% \text{ UI}$ ทำให้ระบบมี Eye Margin เหลือเฟือ)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคิดเป็นแอมพลิจูดดับเบิ้ลซ้ำซ้อนสองเท่า
* ข้อ C ผิด เพราะไม่ได้คูณตัวประกอบการกระชากของอนุพันธ์ความชันที่จุดยอดคลื่นสามเหลี่ยม
* ข้อ D ผิด เพราะลืมแปลงหน่วยความถี่มอดูเลต

---

### คำถามที่ 3: การประเมินจิตเตอร์ที่เกิดจากวงจร Alexander Bang-Bang CDR (Bang-Bang Limit Cycle Jitter Estimation)
ในระบบเชื่อมต่อออปติคอล $10.0\text{ Gbps}$ ($1\text{ UI} = 100.0\text{ ps}$) ตัวรับใช้สถาปัตยกรรม Phase-Interpolator Bang-Bang CDR:
* สเต็ปการหมุนเฟสย่อยของ Phase Interpolator: $\Delta \tau = 0.80\text{ ps ต่อสเต็ป}$
* ความล่าช้าในการประมวลผลของลูปดิจิทัล (Loop Processing Latency): $D = 3\text{ clock cycles}$
* อัตราสลับข้อมูล (Transition Density) เฉลี่ยของรหัส 64b/66b: $P_{trans} = 0.50$
* หากสมการประเมิน Peak-to-Peak Limit Cycle Jitter ของ Bang-Bang CDR ถูกกำหนดโดย:
  $$J_{BB,pp} = 2 \cdot \Delta \tau \cdot (D + 1)$$
* และสมการ Random Jitter ที่เกิดจากการแบ่งย่อยควอนไทเซชัน (Quantization RMS Jitter):
  $$J_{quant,rms} = \frac{\Delta \tau}{\sqrt{12}}$$

จงคำนวณหา:
1. ค่า Peak-to-Peak Bang-Bang Jitter ($J_{BB,pp}$) ในหน่วยพิโกวินาที ($\text{ps}$)
2. ค่า Quantization RMS Jitter ($J_{quant,rms}$) ในหน่วยพิโกวินาที ($\text{ps}$)
3. สัดส่วนของ $J_{BB,pp}$ เทียบกับความกว้าง 1 Unit Interval ($\% \text{UI}$)

A) $J_{BB,pp} = 6.40\text{ ps}, \quad J_{quant,rms} \approx 0.231\text{ ps}, \quad \% \text{UI} = 6.40\%$  
B) $J_{BB,pp} = 3.20\text{ ps}, \quad J_{quant,rms} \approx 0.462\text{ ps}, \quad \% \text{UI} = 3.20\%$  
C) $J_{BB,pp} = 12.80\text{ ps}, \quad J_{quant,rms} \approx 0.115\text{ ps}, \quad \% \text{UI} = 12.80\%$  
D) $J_{BB,pp} = 4.80\text{ ps}, \quad J_{quant,rms} \approx 0.231\text{ ps}, \quad \% \text{UI} = 4.80\%$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณ Peak-to-Peak Bang-Bang Jitter ($J_{BB,pp}$)**
จากสูตร:
$$J_{BB,pp} = 2 \cdot \Delta \tau \cdot (D + 1)$$
แทนค่า $\Delta \tau = 0.80\text{ ps}$ และ $D = 3$:
$$J_{BB,pp} = 2 \times 0.80\text{ ps} \times (3 + 1) = 1.60\text{ ps} \times 4 = 6.40\text{ ps}$$

**ขั้นตอนที่ 2: คำนวณ Quantization RMS Jitter ($J_{quant,rms}$)**
การกระจายตัวของข้อผิดพลาดจากการแบ่งระดับแบบสม่ำเสมอ (Uniform Distribution) ในช่วง $[-\Delta \tau / 2, +\Delta \tau / 2]$:
$$J_{quant,rms} = \frac{\Delta \tau}{\sqrt{12}} = \frac{0.80\text{ ps}}{3.4641} \approx 0.23094\text{ ps} \approx 0.231\text{ ps}$$

**ขั้นตอนที่ 3: คำนวณสัดส่วนเทียบกับ Unit Interval ($\% \text{UI}$)**
ความกว้าง $1\text{ UI} = 100.0\text{ ps}$
$$\% \text{UI} = \frac{J_{BB,pp}}{UI} \times 100\% = \frac{6.40\text{ ps}}{100.0\text{ ps}} \times 100\% = 6.40\% \text{ UI}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($J_{BB,pp} = 6.40\text{ ps}, J_{quant,rms} \approx 0.231\text{ ps}, \% \text{UI} = 6.40\%$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะลืมคูณเลข 2 สำหรับค่า Peak-to-Peak แบบสมมาตรไป-กลับ
* ข้อ C ผิด เพราะคิดค่าหน่วงเวลา $D$ สูงเกินความเป็นจริงเท่าตัว
* ข้อ D ผิด เพราะลืมบวกเลข 1 ในเทอม $(D + 1)$
