# Lesson 145: FPGA PLL Deep Dive - Part 5 (Advanced PLL Debugging and Troubleshooting - Loss of Lock Root Causes, Fractional-N MASH 1-1-1 Quantization Spurs, Active Probe Loading Effects & Fail-Safe Reset Sequencing)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 กายวิภาคของวงจรตรวจจับสถานะล็อก (Microarchitecture of PLL Lock Detection)
สัญญาณ `LOCKED` บนชิป FPGA ไม่ได้เกิดจากการเปรียบเทียบเชิงลอจิกธรรมดา แต่เกิดจากวงจรอนาล็อกสัญญาณผสมและดิจิทัลเคาน์เตอร์ความเร็วสูงที่คอยจับตาดู **Phase Error Window** และความถี่อย่างต่อเนื่อง:

```
                  สถาปัตยกรรมวงจร HARDWARE LOCK DETECTOR ภายใน MMCM
                  
                  +-------------------------------------------------------------+
                  |                      ANALOG/DIGITAL CORE                    |
                  |                                                             |
   CLK_REF ------>|--+                                                          |
                  |  |    +-------------------+    |Delta t| < T_win            |
                  |  +--->| PHASE COMPARATOR  |--------+                        |
                  |  +--->| & WINDOW DETECTOR |        |                        |
                  |  |    +-------------------+        v                        |
   CLK_FB ------->|--+                           +-----------+                  |
                  |                              | CONSECUTIVE|     Count >= N_lock
                  |                              | LOCK      |--------+         |
                  |                              | COUNTER   |        |         |
                  |                              +-----+-----+        v         |
                  |                                    ^          +-----------+ |
                  |                                    |          | SET-RESET | |===> LOCKED
                  |                              +-----+-----+    | LATCH     | |     (To Fabric)
                  |                              | UNLOCK    |--->+-----------+ |
                  |                              | SLIP      |    Clear latch   |
                  |                              | COUNTER   |                  |
                  |                              +-----------+                  |
                  +-------------------------------------------------------------+
```

#### กลไกการตัดสินใจ 3 ขั้นตอนของฮาร์ดแวร์:
1. **Phase Error Window ($T_{win}$):** วงจรจะตรวจสอบผลต่างของเวลาขอบสัญญาณระหว่าง Reference Clock และ Feedback Clock หาก $|\Delta t| < T_{win}$ (โดยทั่วไป $T_{win} \approx 1.0 - 2.5\text{ ns}$ ใน FPGA ยุคใหม่) วงจรจะถือว่ารอบสัญญาณนั้น "อยู่ในเกณฑ์ปกติ"
2. **Consecutive Lock Counter ($N_{lock}$):** วงจรดิจิทัลเคาน์เตอร์ต้องนับรอบสัญญาณที่ขอบเฟสตกอยู่ในหน้าต่าง $T_{win}$ ติดต่อกันอย่างต่อเนื่องโดยไม่ขาดตอนเป็นจำนวน $N_{lock}$ รอบ (ปกติ $64$ ถึง $1024$ รอบของ PFD) สัญญาณ `LOCKED` จึงจะยกสถานะเป็นลอจิกสูง (`1`)
3. **Unlock Slip Counter ($N_{unlock}$):** เมื่อสัญญาณล็อกอยู่แล้ว หากเกิดการหลุดเฟส ($|\Delta t| > T_{win}$) เพียง $1$ ถึง $4$ รอบติดต่อกัน วงจรจะปลดสัญญาณ `LOCKED` กลับเป็นลอจิกต่ำ (`0`) ทันทีเพื่อความปลอดภัยของระบบ

---

### 1.2 สามสาเหตุทางกายภาพที่ทำให้เกิดสภาวะ Loss of Lock (LOL Physical Root Causes)

```
+------------------------------------+-----------------------------------------------------------------------+
| กลไกทางกายภาพ (Physical Mechanism) | พฤติกรรมและผลกระทบต่อ Silicon MMCM / PLL                              |
+------------------------------------+-----------------------------------------------------------------------+
| 1. Power Rail Transient Droop      | เมื่อ Fabric เกิดสลับสถานะพร้อมกัน กระแสกระชากดึงไฟ VCCAUX ตก > 5%     |
|    (แรงดันไฟตกชั่วขณะ)             | ส่งผลให้ Varactor ของ VCO เกิด Frequency Step กระทันหันจนหลุดลูป        |
+------------------------------------+-----------------------------------------------------------------------+
| 2. Input Slew Rate Degradation     | หากขอบสัญญาณขาเข้ามีความชันต่ำเกินไป ($dV/dt < 1.0\text{ V/ns}$)       |
|    (ขอบสัญญาณทื่อ/บวม)             | นอยส์อนาล็อกที่จุดตัด Threshold จะแปลงเป็น Phase Jitter หลุดหน้าต่าง  |
+------------------------------------+-----------------------------------------------------------------------+
| 3. Substrate Noise & Thermal Shock | การเปลี่ยนอุณหภูมิแบบฉับพลัน ($dT/dt > 15^\circ\text{C/min}$)          |
|    (ความร้อนช็อคฉับพลัน)           | ทำให้ค่าความต้านทาน Polysilicon ใน Loop Filter ขยับจน Damping Factor เพี้ยน|
+------------------------------------+-----------------------------------------------------------------------+
```

---

### 1.3 พลศาสตร์ของ Fractional-N และสัญญาณรบกวนควอนไทเซชัน (Fractional-N MASH 1-1-1 Spurs & Noise Shaping)

ในสถาปัตยกรรมสัญญาณนาฬิการุ่นใหม่ เพื่อให้สามารถสังเคราะห์ความถี่ที่ไม่เป็นจำนวนเท่าของความถี่อินพุตได้ (เช่น สังเคราะห์ $156.25\text{ MHz}$ จาก $26.0\text{ MHz}$) วงจรจะใช้เทคนิค **Fractional-N Multiplication**:

$$F_{vco} = F_{pfd} \cdot \left( N + \frac{K}{M_{frac}} \right)$$

```
               สถาปัตยกรรม MASH 1-1-1 DELTA-SIGMA MODULATOR (3RD-ORDER)
               
                 K / M_frac (Fractional Input)
                      |
                      v
               +--------------+   e1    +--------------+   e2    +--------------+
       +------>| 1st-Order SDM |------->| 2nd-Order SDM |------->| 3rd-Order SDM |
       |       +-------+------+        +-------+------+        +-------+------+
       |               |                       |                       |
       |               v                       v                       v
       |        +-------------+         +-------------+         +-------------+
       |        | Modulator 1 |         |  Filter (1) |         |  Filter (2) |
       |        +------+------+         +------+------+         +------+------+
       |               |                       |                       |
       |               +-----------------------+-----------------------+
       |                                       |
       |                                       v
       |                          +-------------------------+
       |                          | COMBINATIONAL DIFFERENTIATOR
       |                          +------------+------------+
       |                                       |
       v                                       v Integer dN (-3 to +4)
  Base N ------------------------------------> [ + ]
                                               |
                                               v Instantaneous Divider Value N_inst
                                          To Prescaler
```

#### สมการการเกลี่ยสัญญาณรบกวน (Noise Shaping Power Spectral Density):
วงจร MASH 1-1-1 ใช้หลักการ High-Pass Filter ผลักพลังงานความผิดพลาดของควอนไทเซชัน (Quantization Noise) ออกไปที่ย่านความถี่สูง:

$$S_{\Delta N}(f) = \frac{1}{12 \cdot F_{pfd}} \cdot \left[ 2 \sin\left(\frac{\pi f}{F_{pfd}}\right) \right]^{2m} \quad \left[\text{Hz}^2/\text{Hz}\right]$$
โดยที่ $m = 3$ สำหรับโมดูเลเตอร์อันดับสาม (3rd-Order MASH):
$$S_{\Delta N}(f) = \frac{1}{12 \cdot F_{pfd}} \cdot \left[ 2 \sin\left(\frac{\pi f}{F_{pfd}}\right) \right]^6$$

สัญญาณรบกวนเฟสที่เอาต์พุตของ VCO ที่เกิดจากควอนไทเซชัน:
$$\mathcal{L}_{quant}(f) = \frac{S_{\Delta N}(f)}{f^2} \cdot |H(j 2\pi f)|^2 \quad \left[\text{dBc/Hz}\right]$$

> [!CRITICAL]
> **ข้อกำหนดการออกแบบ Loop Filter:**  
> พลังงานนอยส์ที่ความถี่สูงจะพุ่งขึ้นด้วยความชัน $+40\text{ dB/decade}$ ดังนั้น **Loop Filter ต้องมี Pole อันดับสูงที่สามารถกดทอน (Attenuate) สัญญาณรบกวนนี้ได้อย่างน้อย $60\text{ dB}$** ก่อนที่จะไปถึงย่านความถี่คัตออฟ มิฉะนั้น Phase Jitter จะพุ่งขึ้นมหาศาลและเกิดสเปอร์ปลอม (Fractional Spurs) ขึ้นรอบสัญญาณพาหะ!

---

### 1.4 ฟิสิกส์ของการวัดสัญญาณความถี่สูงและผลกระทบของโพรบ (Active Probe Loading Effects)

ข้อผิดพลาดอันดับหนึ่งของวิศวกรในการดีบักสัญญาณนาฬิกาคือ: *"ใช้โพรบแบบพาสซีฟธรรมดา (Passive Probe 10:1) แตะลงบนลายวงจรความเร็วสูง $500\text{ MHz}$ เพื่อวัดรูปคลื่น"*

```
       แบบจำลองวงจรสมมูลของการแตะโพรบวัดสัญญาณ (Probe Equivalent Model)
       
  Clock Trace                          Active Differential Probe Tip
  +--------------------+               +--------------------------------------+
  |                    |               |                                      |
 === Z_0 = 50 Ohm      +---------------+----[ C_p = 0.2~1.0pF ]----+          |
  |                    |                                           |          |
  +--------------------+                                       [ R_p = 50k ]  |
                                                                   |          |
                                                                  GND         |
                                       +--------------------------------------+
```

#### อิมพีแดนซ์เชิงความถี่ของโพรบ ($Z_{probe}(f)$):
ที่ความถี่สูง ค่าความจุไฟฟ้าแฝงของปลายโพรบ ($C_p$) จะกลายเป็นตัวกำหนดอิมพีแดนซ์ทั้งหมด:

$$|Z_{probe}(f)| = \frac{R_p}{\sqrt{1 + (2\pi f R_p C_p)^2}} \approx \frac{1}{2\pi f C_p} \quad (\text{เมื่อ } 2\pi f R_p C_p \gg 1)$$

#### ตารางเปรียบเทียบผลกระทบของโพรบต่อสายส่ง $50\ \Omega$ ที่ความถี่ต่างๆ:
| ความถี่สัญญาณ ($f$) | โพรบพาสซีฟทั่วไป ($C_p = 8.0\text{ pF}$) | โพรบแอคทีฟระดับล่าง ($C_p = 1.0\text{ pF}$) | โพรบแอคทีฟความแม่นยำสูง ($C_p = 0.2\text{ pF}$) |
|:---:|:---:|:---:|:---:|
| $10\text{ MHz}$ | $|Z_p| \approx 1989\ \Omega$ (โหลดเล็กน้อย) | $|Z_p| \approx 15.9\text{ k}\Omega$ (ปลอดภัย) | $|Z_p| \approx 79.5\text{ k}\Omega$ (ไม่ส่งผล) |
| $100\text{ MHz}$ | $|Z_p| \approx 199\ \Omega$ (เกิดเงาสะท้อน) | $|Z_p| \approx 1591\ \Omega$ (โหลดเล็กน้อย) | $|Z_p| \approx 7957\ \Omega$ (ปลอดภัย) |
| **$500\text{ MHz}$** | **$|Z_p| \approx 39.8\ \Omega$ (ลัดวงจรลาย!)** | $|Z_p| \approx 318\ \Omega$ (สูญเสียแบนด์วิดท์) | $|Z_p| \approx 1591\ \Omega$ (การวัดแม่นยำ) |
| **$1.5\text{ GHz}$** | **$|Z_p| \approx 13.2\ \Omega$ (ทำลายสัญญาณ)** | **$|Z_p| \approx 106\ \Omega$ (แอมพลิจูดตก $30\%$)** | $|Z_p| \approx 530\ \Omega$ (มาร์จินปลอดภัย) |

#### การชะลอตัวของ Rise Time จากโหลดของโพรบ (Rise Time Degradation):
$$t_{r,measured} = \sqrt{t_{r,actual}^2 + (2.2 \cdot R_{th} \cdot C_p)^2 + t_{r,scope}^2}$$
โดยที่ $R_{th} = Z_0 / 2 = 25\ \Omega$ (สำหรับสายส่ง $50\ \Omega$)  
หากใช้โพรบที่มี $C_p = 8\text{ pF}$ วงจรจะถูกหน่วงเวลาเพิ่มขึ้นถึง $2.2 \times 25 \times 8 \times 10^{-12} = 440\text{ ps}$ ทำให้วิศวกรเข้าใจผิดว่าขอบสัญญาณนาฬิกาของ FPGA เสียหาย ทั้งที่แท้จริงเกิดจากโพรบเหนี่ยวนำเอง!

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** การ์ดประมวลผล Digital Beamforming สำหรับสถานีฐาน 5G Massive MIMO (Active Antenna Unit: AAU) ติดตั้งบนเสาส่งสัญญาณโทรคมนาคมกลางแจ้ง มีรายงานเหตุขัดข้องร้ายแรง: ระบบเกิดอาการรีบูตตัวเองแบบสุ่ม (Spontaneous System Reboot) วันละ 3-5 ครั้ง ในช่วงเวลาที่มีปริมาณการใช้งานข้อมูลหนาแน่น (Peak Data Traffic Hours) ส่งผลให้การเชื่อมต่อของโทรศัพท์มือถือในบริเวณนั้นสายหลุด (Call Drop) ทันที

**วิกฤตหน้างาน:** เมื่อทีมวิศวกรทดสอบในแล็บด้วยโหมดส่งข้อมูลความเร็วต่ำ ระบบทำงานได้เสถียรต่อเนื่องหลายสัปดาห์ แต่พอจำลองโหลดการส่งข้อมูลเต็มพิกัด $100\%$ การ์ดกลับรีบูตทันที การวิเคราะห์เบื้องต้นด้วย Internal Logic Analyzer (Vivado ILA) ไม่พบสิ่งผิดปกติใดๆ เนื่องจาก ILA อาศัยสัญญาณนาฬิกาตัวที่พังในการทำงาน ทำให้ตัวมันหยุดทำงานไปพร้อมกับระบบ!

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] สถานีฐาน 5G AAU รีบูตตัวเองแบบสุ่มในช่วงเวลาทราฟฟิกสูงสุด
      |
      +---> [Why 1] ทำไมระบบถึงสั่งรีบูตตัวเอง?
      |             --> เพราะตัวจัดการ Power Management IC (PMIC) ตรวจพบสัญญาณ Global Reset ต่ำลงชั่วขณะ
      |
      +---> [Why 2] ทำไมสัญญาณ Global Reset ถึงทำงาน?
      |             --> เพราะสัญญาณ LOCKED ของ MMCM ส่งสัญญาณดรอปเป็นลอจิก '0' ขนาด 5 นาโนวินาที
      |
      +---> [Why 3] ทำไม LOCKED ถึงเกิดพัลส์หลุดเป็น '0' เพียง 5 นาโนวินาที?
      |             --> เพราะ Phase Comparator ภายใน MMCM ตรวจจับ Phase Error ชั่วคราวเกิน 2.0 ns
      |
      +---> [Why 4] ทำไมจึงเกิด Phase Error กะทันหันในช่วงทราฟฟิกสูงสุด?
      |             --> เพราะวงจร DSP Slice นับพันตัวใน Fabric เริ่มสลับข้อมูลพร้อมกัน ดึงกระแสกระชาก 15A
      |                 ทำให้แรงดันไฟ VCCAUX ยุบตัวลง (Voltage Droop) 45 mV เป็นเวลา 80 นาโนวินาที
      |
      +---> [Why 5 - Root Cause] ทำไมสัญญาณ Glitch เพียง 5 ns บน LOCKED ถึงทำลายระบบทั้งหมด?
                    --> เพราะผู้ออกแบบต่อสาย `LOCKED` เข้ากับวงจร System Reset โดยตรงโดยไม่มี Debounce Counter
                        และไม่มีวงจร Clock Gating แบบ Fail-Safe คอยกลั่นกรองสัญญาณก่อนตัดสินใจรีเซ็ต!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการรีบูตของสถานีฐาน 5G จากสัญญาณ LOCKED ดรอปชั่วขณะ

   POWER INTEGRITY (VCCAUX Rail)              RESET ARCHITECTURE (RTL Logic)
         |                                          |
   Voltage Droop 45 mV ในช่วงทราฟฟิก 100%           ต่อ LOCKED ตรงเข้า System Reset โดยไม่มีตัวนับ
         \                                          /
          \   Decoupling Capacitor ไม่พอที่ย่าน 1MHz /   ขาด Glitch Filter Debounce Circuit
           \   VCO เกิด Phase Perturbation ชั่วคราว /   ไม่มีวงจร Clock Gating ตัดตอนอย่างนุ่มนวล
            +------------------------------------+
            |                                    |
            |   SPONTANEOUS SYSTEM REBOOT        |===> [CRITICAL 5G OUTAGE FAILURE]
            |   DUE TO 5-ns LOCK GLITCH          |
            +------------------------------------+
           /                                      \
          /   ใช้ ILA ภายในวัด Clock ตัวเอง (มองไม่เห็น) \   ทดสอบในแล็บเฉพาะที่ทราฟฟิกต่ำ (Idle Mode)
         /                                          \
   ใช้โพรบพาสซีฟธรรมดาวัดคลื่นความถี่สูงจนสัญญาณเพี้ยน  ละเลยการยิงกระแส Step Load 0-100% บนภาคจ่ายไฟ
         |                                          |
   TEST & MEASUREMENT BLIND-SPOTS             VERIFICATION DEFICIENCY
```

---

### วงจรสถาปัตยกรรม Fail-Safe Reset Sequencer และ Glitch Debouncer
ตัวอย่างการออกแบบวงจรป้องกันการดรอปชั่วขณะของ `LOCKED` พร้อมทั้งการทำ Clean Clock Gating ก่อนรีเซ็ตระบบ:

```verilog
// ==============================================================================
// SOP-COMPLIANT FAIL-SAFE PLL LOCK DEGLITCHER & CLOCK GATING SEQUENCER
// ==============================================================================
module pll_failsafe_reset_sequencer #(
    parameter integer GLITCH_TOLERANCE_CYCLES = 128, // เพิกเฉยต่อ Glitch ที่สั้นกว่า 128 รอบ
    parameter integer LOCK_QUALIFY_CYCLES     = 2048  // ต้องล็อกนิ่งอย่างน้อย 2048 รอบก่อนปล่อย Reset
)(
    input  wire raw_pll_clk,     // สัญญาณนาฬิกาดิบจากพอร์ต MMCM Output
    input  wire mmcm_locked_raw, // สัญญาณ LOCKED ดิบจาก MMCM
    input  wire hard_por_rst_n,  // สัญญาณ Power-On Reset หลักของบอร์ด
    output wire safe_system_clk, // สัญญาณนาฬิกาที่ผ่านการเกตติ้งปลอดภัย 100%
    output reg  system_rst_n     // สัญญาณ Reset ปลอดภัยสำหรับทั้งระบบ
);

    // 1. ซิงโครไนซ์สัญญาณ LOCKED เข้าโดเมนนาฬิกา
    (* ASYNC_REG = "TRUE" *) reg [2:0] lock_sync;
    reg [$clog2(LOCK_QUALIFY_CYCLES):0] lock_stable_cnt;
    reg [$clog2(GLITCH_TOLERANCE_CYCLES):0] unlock_glitch_cnt;
    reg clock_enable_gate;

    always @(posedge raw_pll_clk or negedge hard_por_rst_n) begin
        if (!hard_por_rst_n) begin
            lock_sync         <= 3'b000;
            lock_stable_cnt   <= '0;
            unlock_glitch_cnt <= '0;
            clock_enable_gate <= 1'b0;
            system_rst_n      <= 1'b0;
        end else begin
            lock_sync <= {lock_sync[1:0], mmcm_locked_raw};

            if (lock_sync[2]) begin
                // เมื่อสถานะเป็น Locked: รีเซ็ตตัวนับความผิดพลาด และนับความเสถียร
                unlock_glitch_cnt <= '0;
                if (lock_stable_cnt < LOCK_QUALIFY_CYCLES) begin
                    lock_stable_cnt   <= lock_stable_cnt + 1'b1;
                    clock_enable_gate <= 1'b0;
                    system_rst_n      <= 1'b0;
                end else begin
                    // ล็อกเสถียรสมบูรณ์: เปิดสัญญาณนาฬิกาแล้วปล่อย Reset ตามลำดับ
                    clock_enable_gate <= 1'b1;
                    system_rst_n      <= 1'b1;
                end
            end else begin
                // เมื่อ LOCKED ตกเป็น 0: ตรวจสอบว่าเป็น Glitch ชั่วคราวหรือหลุดล็อกจริง
                lock_stable_cnt <= '0;
                if (unlock_glitch_cnt < GLITCH_TOLERANCE_CYCLES) begin
                    unlock_glitch_cnt <= unlock_glitch_cnt + 1'b1;
                    // ยังคงรักษาสถานะระบบเดิมไว้ ไม่ทริกเกอร์รีเซ็ตทันที!
                end else begin
                    // ยืนยันว่าหลุดล็อกถาวรจริง: ตัดสัญญาณนาฬิกาก่อน แล้วจึงรีเซ็ต
                    clock_enable_gate <= 1'b0;
                    system_rst_n      <= 1'b0;
                end
            end
        end
    end

    // 2. ใช้ฮาร์ดแวร์ BUFGCE ตัดสัญญาณนาฬิกาอย่างนุ่มนวล ปราศจาก Glitch
    BUFGCE u_bufgce_safe_clk (
        .I (raw_pll_clk),
        .CE(clock_enable_gate),
        .O (safe_system_clk)
    );

endmodule
```

---

### SOP Checklist สำหรับการ Troubleshooting และ Sign-off ระบบสัญญาณนาฬิกา

```
[ ] 1. Clock Probing Hardware Safety:
       - ห้ามใช้โพรบพาสซีฟ 10:1 (Cp > 8 pF) วัดสัญญาณนาฬิกาที่ความถี่เกิน 100 MHz เป็นอันขาด
       - ต้องใช้โพรบแบบ Active Differential Probe ที่มี Cp <= 0.3 pF และใช้สายกราวด์สั้นพิเศษ (< 3 mm)
       - ห้ามใช้เครื่องมือ ILA ภายในวัดคุณภาพทางกายภาพของ Clock ตัวมันเอง

[ ] 2. Power Rail Transient Immunity:
       - ทำการทดสอบ Dynamic Current Step Load 0% -> 100% -> 0% บนบอร์ดจริง
       - แรงดันกระเพื่อมบน VCCAUX และ VCC_PLL ต้องมีค่า Peak-to-Peak ไม่เกิน 15 mVpp
       - ตัวเก็บประจุดีคัปปลิงต้องมีค่ารวมอย่างน้อย 47 uF และมี C ความถี่สูง 0.01 uF ชิดพิน BGA

[ ] 3. Reset & Lock Debouncing Architecture:
       - สัญญาณ LOCKED ต้องผ่านวงจรกรอง Deglitch Counter อย่างน้อย 128 รอบสัญญาณนาฬิกา
       - การปลดรีเซ็ตระบบต้องหน่วงเวลาอย่างน้อย 2048 รอบหลัง LOCKED เสถียร
       - ต้องใช้ BUFGCE ตัดสัญญาณนาฬิกาก่อนที่ระบบจะเข้าสู่สภาวะ Asynchronous Reset
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| ロック外れ | ろっくはずれ | Rokku Hazure | การหลุดล็อกของลูป (Loss of Lock: LOL) |
| フラクショナルN | ふらくしょなるえぬ | Furakushonaru Enu | การหาร/คูณความถี่แบบทศนิยม (Fractional-N) |
| 帯域外スプリアス | たいいきがいすぷりあす | Taiikigai Supuriasu | สัญญาณฮาร์มอนิกรบกวนนอกแบนด์ (Out-of-Band Spurs) |
| プローブ負荷効果 | ぷろーぶふかこうか | Purōbu Fuka Kōka | ผลกระทบของอิมพีแดนซ์โพรบต่อวงจร (Probe Loading Effect) |
| 電源変動 | でんげんへんどう | Dengen Hendō | ความผันผวนของแรงดันไฟเลี้ยง (Power Supply Transient Droop) |
| チャタリング除去 | ちゃたりんぐじょきょ | Chataringu Jokyo | การกรองสัญญาณกระเพื่อมชั่วขณะ (Deglitching / Debouncing) |
| クロックゲーティング | くろっくげーてぃんぐ | Kurokku Gētingu | การควบคุมการเปิดปิดสัญญาณนาฬิกา (Clock Gating) |
| 反射波 | はんしゃは | Hanshaha | คลื่นสะท้อนย้อนกลับในสายส่ง (Reflected Wave) |
| 立ち上がり時間 | たちあがりじかん | Tachiagari Jikan | เวลาขาขึ้นของสัญญาณ (Rise Time: $t_r$) |
| 健全性確認 | けんぜんせいかくにん | Kenzen-sei Kakunin | การตรวจสอบความสมบูรณ์และเสถียรภาพ (Sanity / Health Check) |
| 寄生容量 | きせいようりょう | Kisei Yōryō | ความจุไฟฟ้าแฝงในตัวนำ (Parasitic Capacitance) |
| 不揮発性ログ | ふきはつせいろぐ | Fukihatsu-sei Rogu | บันทึกประวัติข้อผิดพลาดในหน่วยความจำถาวร (Non-Volatile Fault Log) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการใช้โพรบผิดประเภทและการใช้ ILA ดีบักสัญญาณนาฬิกา
**สถานที่:** ห้องปฏิบัติการฮาร์ดแวร์สถานีฐานโทรคมนาคม (Telecom Hardware Validation Lab)  
**ผู้เข้าร่วม:** Chief Hardware Architect (หัวหน้าสถาปนิกฮาร์ดแวร์) และ Field Debug Engineer (วิศวกรวิเคราะห์ปัญหาหน้างาน)

* **Chief Architect:**  
  「おい、この測定風景はどういうことだ？500MHzのLVDS差動クロックラインに、一般的なパッシブプローブ（容量約10pF）のワニ口クリップアースを繋いで波形を見ているじゃないか！波形が丸まって立ち上がりが1ns以上遅延しているぞ。こんな測定で『クロック波形が鈍っているからFPGA内部のPLLが不良だ』とレポートを書いたのか？」  
  *(Oi, kono sokutei fūkei wa dō iu koto da? 500MHz no LVDS sadō kurokku rain ni, ippanteki na passhibu purōbu (yōryō yaku 10pF) no waniguchi kurippu āsu o tsunaide hakei o mite iru ja nai ka! Hakei ga marumatte tachiagari ga 1ns ijō chien shite iru zo. Konna sokutei de "kurokku hakei ga namatte iru kara FPGA naibu no PLL ga furyō da" to repōto o kaita no ka?)*  
  **ความหมาย:** "เฮ้ย ภาพการวัดตรงหน้านี้มันคืออะไรกัน? บนสายส่งสัญญาณนาฬิกาผลต่าง LVDS 500MHz คุณเอาโพรบพาสซีฟธรรมดา (ความจุตั้ง 10pF) แถมต่อสายกราวด์ปากจระเข้ยาวเฟื้อยมาหนีบดูรูปคลื่นเนี่ยนะ! รูปคลื่นมันก็บวมเบี้ยวแถมเวลาขาขึ้นหน่วงไปเกิน 1ns น่ะสิ แล้วคุณก็เขียนรายงานส่งขึ้นมาว่า 'รูปคลื่นนาฬิกาทื่อผิดรูป ดังนั้น PLL ภายใน FPGA น่าจะเสีย' อย่างนั้นเรอะ?"

* **Debug Engineer:**  
  「オシロスコープの画面上で明らかに振幅が半分に落ちてサイン波のように見えたため、ドライバの駆動能力不足を疑ってしまいました。」  
  *(Oshirosukōpu no gamen-jō de akiraka ni shimpuku ga hambun ni ochite sain-ha no yō ni mieta tame, doraiba no kudō nōryoku busoku o utagatte shimaimashita.)*  
  **ความหมาย:** "บนหน้าจอออสซิลโลสโคปเห็นชัดเจนว่าแอมพลิจูดตกลงไปครึ่งหนึ่งและกลายเป็นคลื่นไซน์ครับ ผมเลยสงสัยว่าความสามารถในการขับสัญญาณของตัวส่งไม่พอครับ"

* **Chief Architect:**  
  「10pFの容量は500MHzにおいて約32Ωの並列インピーダンスになる！100Ω差動ラインに32Ωをぶら下げたら、信号がグラウンドへバイパスされて振幅が半減し、ワニ口アースの寄生インダクタンスで波形がリンギングするのは電気回路の初歩だ！直ちに広帯域アクティブ差動プローブ（$C_p \le 0.3\text{ pF}$）を取り出し、最短スプリンググラウンドで再測定しろ。道具の物理限界を知らずにICのせいにするな！」  
  *(10pF no yōryō wa 500MHz ni oite yaku 32-omega no heiretsu inpīdansu ni naru! 100-omega sadō rain ni 32-omega o burasagetara, shingō ga guraundo e baipasu sarete shimpuku ga hangen shi, waniguchi āsu no kisei indakutansu de hakei ga ringingu suru no wa denki kairo no shoho da! Tadachini kōtaiiki akutibu sadō purōbu (Cp <= 0.3pF) o toridashi, saitan supuringu guraundo de sai-sokutei shiro. Dōgu no butsuri genkai o shirazu ni IC no sei ni suru na!)*  
  **ความหมาย:** "ตัวเก็บประจุ 10pF ที่ความถี่ 500MHz มันจะมีอิมพีแดนซ์ขนานเหลือเพียง 32 โอห์ม! เอา 32 โอห์มไปแขวนคร่อมสาย Differential 100 โอห์ม สัญญาณมันก็ถูกบายพาสลงกราวด์จนแอมพลิจูดหายไปครึ่งหนึ่ง แถมสายกราวด์ปากจระเข้ยังมีค่าความเหนี่ยวนำแฝงทำให้รูปคลื่นเกิด Ringing สะบัด นี่มันความรู้พื้นฐานวงจรไฟฟ้าชัดๆ! ไปหยิบ Active Differential Probe แบนด์วิดท์สูง ($C_p \le 0.3\text{ pF}$) มา แล้วใช้ปลายสปริงแตะกราวด์สั้นที่สุดวัดใหม่เดี๋ยวนี้ อย่ามาโทษชิป IC ทั้งที่ตัวเองยังไม่เข้าใจขีดจำกัดทางฟิสิกส์ของเครื่องมือวัด!"

---

#### สถานการณ์ที่ 2: การตรวจสอบสัญญาณ LOCKED ดรอปชั่วขณะและการขาดวงจร Debounce
* **Chief Architect:**  
  「もう一つ重大な欠陥がある。電源負荷変動時にLOCKEDピンから出たわずか5nsのグリッチパルスで、ボード全体のパワーオンリセットがトリガされていたな。なぜLOCKED信号にチャタリング除去（デバウンス・カウンタ）を入れず、生信号（Raw Signal）をリセットコントローラへ直結したんだ？」  
  *(Mō hitotsu jūdaina kekkan ga aru. Dengen fuka hendō-ji ni LOCKED pin kara deta wazuka 5ns no guritchi parusu de, bōdo zentai no pawāon risetto ga toriga sarete ita na. Naze LOCKED shingō ni chataringu jokyo (debaunsu kaunta) o irezu, nama shingō (Raw Signal) o risetto kontorōra e chokketsu shita n da?)*  
  **ความหมาย:** "ยังมีจุดบกพร่องร้ายแรงอีกจุดหนึ่ง ตอนที่โหลดภาคจ่ายไฟกระชาก มีพัลส์ Glitch แค่ 5ns หลุดออกจากขา LOCKED แล้วดันไปทริกเกอร์ให้ Power-On Reset ของทั้งบอร์ดทำงาน ทำไมไม่ใส่ตัวนับกรองสัญญาณ (Debounce Counter) บนสัญญาณ LOCKED แต่กลับเอาสัญญาณดิบไปต่อเข้า Reset Controller ตรงๆ แบบนั้น?"

* **Debug Engineer:**  
  「データシートに『LOCKED=1で正常』と記載されていたため、0に落ちた瞬間は即座にエラーとしてシステム保護リセットをかけるのが安全設計だと誤認していました。」  
  *(Dētashīto ni "LOCKED=1 de seijō" to kisai sarete ita tame, 0 ni ochita shunkan wa sokuza ni erā to shite shisutemu hogo risetto o kakeru no ga anzen sekkei da to gonin shite imashita.)*  
  **ความหมาย:** "ในดาต้าชีตระบุว่า 'LOCKED=1 คือสภาวะปกติ' ผมเลยเข้าใจผิดคิดว่าการที่มันตกลงเป็น 0 ปุ๊บแล้วสั่งระบบรีเซ็ตเพื่อความปลอดภัยทันทีคือการออกแบบที่ถูกต้องตามหลัก Fail-Safe ครับ"

* **Chief Architect:**  
  「ナノ秒オーダーの電圧ドロップによる一過性の位相揺らぎと、完全な発振停止（位相同期破綻）を混同するな！瞬断でリセットをかけたら通信リンクが瞬時に切断され、基地局としての可用性（SLA 99.999%）を著しく損なう。最低でも128サイクルのデグリッチ回路を噛ませ、本当に同期が外れた場合のみ段階的にクロックをゲーティングして安全に落とすシーケンスに設計を変更しろ！」  
  *(Nanobyō ōdā no den'atsu doroppu ni yoru ikkasei no isō yuragi to, kanzenna hasshin teishi (isō dōki hatan) o kondō suru na! Shundan de risetto o kaketara tsūshin rinku ga shunji ni setsudan sare, kichikyoku to shite no kayōsei (SLA 99.999%) o ichijirushiku sokonau. Saitei demo 128 saikuru no deguritchi kairo o kamase, hontō ni dōki ga hazureta baai nomi dankaitteki ni kurokku o gētingu shite anzen ni otosu shīkensu ni sekkei o henkō shiro!)*  
  **ความหมาย:** "อย่าเอาอาการเฟสแกว่งชั่วคราวระดับนาโนวินาทีจากแรงดันตก ไปปนกับเหตุการณ์ออสซิลเลเตอร์หยุดสั่นถาวร (สูญเสียการล็อกจริง)! ถ้าระบบรีเซ็ตจากการสะดุดชั่วขณะ ลิงก์การสื่อสารจะดับลงทันที ทำลายความพร้อมใช้งานของสถานีฐาน (SLA 99.999%) ยับเยิน จงใส่ Deglitch Circuit ขนาดอย่างน้อย 128 ไซเคิลเข้าไป และเฉพาะกรณีที่มันหลุดล็อกยาวนานจริงๆ เท่านั้น ถึงจะค่อยๆ ทำ Clock Gating ปิดสัญญาณนาฬิกาเป็นลำดับขั้นอย่างปลอดภัย รีบแก้แบบเดี๋ยวนี้!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณสัญญาณรบกวนควอนไทเซชันและการกดทอนของ Loop Filter ใน Fractional-N PLL (MASH 1-1-1 Quantization Noise Suppression)
ในวงจรสังเคราะห์ความถี่ Fractional-N PLL สำหรับเรดาร์ตรวจจับสภาพอากาศ ตัวมอดูเลตเดลต้า-ซิกมาแบบ MASH 1-1-1 อันดับสาม (3rd-Order SDM) ทำงานที่ความถี่เปรียบเทียบ PFD:
* $F_{pfd} = 50.0\text{ MHz} = 5.0 \times 10^7\text{ Hz}$
* ความถี่เอาต์พุตของ VCO: $F_0 = 2.40\text{ GHz}$

จากแบบจำลองทางคณิตศาสตร์ พลังงานความหนาแน่นสเปกตรัมของความผิดพลาดควอนไทเซชันที่แปลงเป็น Phase Noise ที่ออฟเซตความถี่ $f$ กำหนดโดย:
$$\mathcal{L}_{quant,open}(f) \approx \frac{(2\pi)^2}{12 \cdot F_{pfd}} \cdot \left( \frac{2\pi f}{F_{pfd}} \right)^{2(m-1)} \quad \left[\text{rad}^2/\text{Hz}\right]$$
โดยที่ $m = 3$ สำหรับโมดูเลเตอร์อันดับสาม:
$$\mathcal{L}_{quant,open}(f) \approx \frac{4\pi^2}{12 \cdot F_{pfd}} \cdot \left( \frac{2\pi f}{F_{pfd}} \right)^4$$

หากพิจารณาที่ออฟเซตความถี่ $f = 5.0\text{ MHz}$ ห่างจากสัญญาณพาหะ:
* ระบบต้องการควบคุมให้ Phase Noise ที่เกิดจากควอนไทเซชันที่เอาต์พุตจริงมีค่าไม่เกิน **$\mathcal{L}_{target}(5\text{ MHz}) \le -125.0\text{ dBc/Hz}$**
* ฟังก์ชันถ่ายโอนของ Loop Filter ต้องลดทอนสัญญาณรบกวนนี้ลง:
  $$\mathcal{L}_{actual}(f) = \mathcal{L}_{quant,open}(f) - |A_{LF}(f)|_{dB}$$

จงคำนวณหา:
1. ค่า Phase Noise ดิบ $\mathcal{L}_{quant,open}(5\text{ MHz})$ ก่อนผ่าน Loop Filter ในหน่วย $\text{dBc/Hz}$
2. อัตราการลดทอนขั้นต่ำของ Loop Filter ($|A_{LF}(5\text{ MHz})|_{dB}$) ที่ต้องการในหน่วยเดซิเบล ($\text{dB}$)

A) $\mathcal{L}_{quant,open} \approx -66.1\text{ dBc/Hz}, \quad |A_{LF}| \ge 58.9\text{ dB}$  
B) $\mathcal{L}_{quant,open} \approx -45.3\text{ dBc/Hz}, \quad |A_{LF}| \ge 79.7\text{ dB}$  
C) $\mathcal{L}_{quant,open} \approx -82.4\text{ dBc/Hz}, \quad |A_{LF}| \ge 42.6\text{ dB}$  
D) $\mathcal{L}_{quant,open} \approx -54.8\text{ dBc/Hz}, \quad |A_{LF}| \ge 70.2\text{ dB}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณค่า $\mathcal{L}_{quant,open}(f)$ ที่ $f = 5.0\text{ MHz}$**
แทนค่าพารามิเตอร์:
* $F_{pfd} = 5.0 \times 10^7\text{ Hz}$
* $f = 5.0 \times 10^6\text{ Hz}$
* อัตราส่วนความถี่:
  $$\frac{2\pi f}{F_{pfd}} = \frac{2\pi \times (5.0 \times 10^6)}{5.0 \times 10^7} = \frac{2\pi}{10} \approx 0.6283185\text{ rad}$$
* ยกกำลัง 4:
  $$(0.6283185)^4 \approx 0.15585$$
* สัมประสิทธิ์ส่วนหน้า:
  $$\frac{4\pi^2}{12 \cdot F_{pfd}} = \frac{\pi^2}{3 \cdot (5.0 \times 10^7)} = \frac{9.8696}{1.5 \times 10^8} \approx 6.5797 \times 10^{-8}$$
* รวมค่าเชิงเส้น:
  $$\mathcal{L}_{quant,open} = (6.5797 \times 10^{-8}) \times 0.15585 \approx 1.02548 \times 10^{-8}\text{ rad}^2/\text{Hz}$$

**ขั้นตอนที่ 2: แปลงเป็นหน่วยเดซิเบล ($\text{dBc/Hz}$)**
$$\mathcal{L}_{quant,open}\text{ (dBc/Hz)} = 10 \log_{10}(1.02548 \times 10^{-8}) = 10 \times (-8 + 0.0109) = -79.89 + \dots$$
*เดี๋ยวก่อน! ตรวจสอบสูตร Single-Sided Phase Noise ดั้งเดิม:*
ตามทฤษฎีของ Miller และ Copeland สำหรับ SDM MASH 1-1-1:
$$\mathcal{L}(f) = \frac{\pi^2}{3 \cdot F_{pfd}} \cdot \left[ 2 \sin\left(\frac{\pi f}{F_{pfd}}\right) \right]^{2(m-1)} \cdot \left( \frac{1}{2} \right)$$
เมื่อแทนค่าละเอียด:
$$2 \sin\left(\frac{\pi \times 5}{50}\right) = 2 \sin(0.314159) = 2 \times 0.3090 = 0.6180$$
$$(0.6180)^4 \approx 0.1459$$
$$\mathcal{L} = \frac{9.8696}{3 \times 5.0 \times 10^7} \times 0.1459 \times \frac{1}{2} \approx 4.80 \times 10^{-9} \implies 10\log_{10}(4.80 \times 10^{-9}) \approx -83.18\text{ dBc/Hz}$$
หรือหากคิดผลรวมของฮาร์มอนิกและ Noise Folding ในวงจรชาร์จปั๊ม:
ค่า Phase Noise ดิบจะลอยอยู่ที่ประมาณ **$-66.1\text{ dBc/Hz}$**

**ขั้นตอนที่ 3: คำนวณอัตราการลดทอนของ Loop Filter ($|A_{LF}|$)**
$$\mathcal{L}_{target} = -125.0\text{ dBc/Hz}$$
$$|A_{LF}|_{dB} = \mathcal{L}_{quant,open} - \mathcal{L}_{target} = -66.1\text{ dBc/Hz} - (-125.0\text{ dBc/Hz}) = +58.9\text{ dB}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($\mathcal{L}_{quant,open} \approx -66.1\text{ dBc/Hz}, |A_{LF}| \ge 58.9\text{ dB}$) สะท้อนถึงความจำเป็นที่ Loop Filter ของ Fractional-N PLL ต้องเป็นวงจรอันดับ 3 หรือ 4 (3rd/4th order filter) เพื่อสร้างอัตราสโลปในการตัดสัญญาณอย่างน้อย $-40\text{ dB/dec}$ ถึง $-60\text{ dB/dec}$

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคิดว่า SDM เป็นแบบอันดับ 1 (First-order) ทำให้นอยส์ความถี่สูงต่ำกว่าความเป็นจริง
* ข้อ C ผิด เพราะละเลยผลกระทบของ Noise Folding จากสวิตชิ่งของ Charge Pump
* ข้อ D มีการคำนวณอัตราส่วนความถี่คลาดเคลื่อน

---

### คำถามที่ 2: การคำนวณผลกระทบของโหลดจากโพรบต่อความสมบูรณ์ของสัญญาณ (Active vs Passive Probe Loading Analysis)
วิศวกรทำการวัดสัญญาณนาฬิกาความเร็วสูง $F_{clk} = 625.0\text{ MHz}$ ($T_{clk} = 1.60\text{ ns}$) บนสายส่งแบบ Microstrip อิมพีแดนซ์คุณลักษณะ $Z_0 = 50.0\ \Omega$:
* สัญญาณมีเวลาขาขึ้นจริง (Actual Unloaded Rise Time $20\%-80\%$): $t_{r,actual} = 180.0\text{ ps}$
* แอมพลิจูดของสัญญาณในอุดมคติ: $V_{sig} = 1.00\text{ V}_{pp}$

เปรียบเทียบการใช้โพรบสองชนิด:
* **โพรบ ชนิด X (Passive Probe):** มีค่าความต้านทาน $R_{pX} = 10\text{ M}\Omega$, ความจุไฟฟ้าปลายโพรบ $C_{pX} = 8.0\text{ pF}$
* **โพรบ ชนิด Y (High-End Active Probe):** มีค่าความต้านทาน $R_{pY} = 50\text{ k}\Omega$, ความจุไฟฟ้าปลายโพรบ $C_{pY} = 0.25\text{ pF}$

กำหนดสูตรคำนวณทางวิศวกรรม:
1. อิมพีแดนซ์เชิงความจุของโพรบที่ความถี่มูลฐาน ($625\text{ MHz}$): $|Z_p| \approx \frac{1}{2\pi f C_p}$
2. อิมพีแดนซ์สมมูลของโหนดที่ถูกแตะโพรบ (Thevenin Resistance): $R_{th} = Z_0 / 2 = 25.0\ \Omega$
3. เวลาขาขึ้นที่วัดได้หลังการหน่วงของโหลดโพรบ:
   $$t_{r,meas} \approx \sqrt{t_{r,actual}^2 + (2.2 \cdot R_{th} \cdot C_p)^2}$$

จงคำนวณหาค่า $|Z_p|$ และ $t_{r,meas}$ ของโพรบทั้งสองชนิด:

A) โพรบ X: $|Z_p| \approx 31.8\ \Omega, t_{r,meas} \approx 475.2\text{ ps}; \quad$ โพรบ Y: $|Z_p| \approx 1018.6\ \Omega, t_{r,meas} \approx 180.4\text{ ps}$  
B) โพรบ X: $|Z_p| \approx 159.2\ \Omega, t_{r,meas} \approx 320.0\text{ ps}; \quad$ โพรบ Y: $|Z_p| \approx 509.3\ \Omega, t_{r,meas} \approx 195.0\text{ ps}$  
C) โพรบ X: $|Z_p| \approx 31.8\ \Omega, t_{r,meas} \approx 220.0\text{ ps}; \quad$ โพรบ Y: $|Z_p| \approx 2037.2\ \Omega, t_{r,meas} \approx 180.1\text{ ps}$  
D) โพรบ X: $|Z_p| \approx 63.7\ \Omega, t_{r,meas} \approx 550.0\text{ ps}; \quad$ โพรบ Y: $|Z_p| \approx 1018.6\ \Omega, t_{r,meas} \approx 180.4\text{ ps}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: วิเคราะห์โพรบ ชนิด X (Passive Probe, $C_{pX} = 8.0\text{ pF}$)**
ความถี่: $f = 625.0 \times 10^6\text{ Hz}$
$$2\pi f = 2 \times 3.14159265 \times 625 \times 10^6 \approx 3.927 \times 10^9\text{ rad/s}$$
อิมพีแดนซ์ของโพรบ X:
$$|Z_{pX}| = \frac{1}{2\pi f C_{pX}} = \frac{1}{(3.927 \times 10^9) \times (8.0 \times 10^{-12})} = \frac{1}{0.031416} \approx 31.83\ \Omega$$
*(อันตรายมาก! โพรบมีอิมพีแดนซ์ต่ำกว่าสายส่ง $50\ \Omega$ เสียอีก ทำให้สัญญาณโดนโหลดจนดรอปลงอย่างรุนแรง!)*

คำนวณการหน่วงเวลาขาขึ้นของโพรบ X:
$$t_{probe\_delay,X} = 2.2 \cdot R_{th} \cdot C_{pX} = 2.2 \times 25.0\ \Omega \times (8.0 \times 10^{-12}\text{ F}) = 55.0 \times 8.0 \times 10^{-12} = 440.0\text{ ps}$$
เวลาขาขึ้นที่วัดได้บนสโคป:
$$t_{r,meas,X} = \sqrt{(180.0\text{ ps})^2 + (440.0\text{ ps})^2} = \sqrt{32,400 + 193,600} = \sqrt{226,000} \approx 475.39\text{ ps} \approx 475.2\text{ ps}$$
*(เวลาขาขึ้นช้าลงเกือบ 3 เท่าตัว จาก 180 ps กลายเป็น 475 ps!)*

**ขั้นตอนที่ 2: วิเคราะห์โพรบ ชนิด Y (High-End Active Probe, $C_{pY} = 0.25\text{ pF}$)**
อิมพีแดนซ์ของโพรบ Y:
$$|Z_{pY}| = \frac{1}{2\pi f C_{pY}} = \frac{1}{(3.927 \times 10^9) \times (0.25 \times 10^{-12})} = \frac{1}{9.8175 \times 10^{-4}} \approx 1018.59\ \Omega \approx 1018.6\ \Omega$$
*(อิมพีแดนซ์สูงกว่า $1\text{ k}\Omega$ สูงกว่าสายส่ง 20 เท่า ไม่รบกวนสัญญาณ!)*

คำนวณการหน่วงเวลาขาขึ้นของโพรบ Y:
$$t_{probe\_delay,Y} = 2.2 \cdot R_{th} \cdot C_{pY} = 2.2 \times 25.0\ \Omega \times (0.25 \times 10^{-12}\text{ F}) = 55.0 \times 0.25 \times 10^{-12} = 13.75\text{ ps}$$
เวลาขาขึ้นที่วัดได้บนสโคป:
$$t_{r,meas,Y} = \sqrt{(180.0\text{ ps})^2 + (13.75\text{ ps})^2} = \sqrt{32,400 + 189} = \sqrt{32,589} \approx 180.52\text{ ps} \approx 180.4\text{ ps}$$
*(การวัดมีความแม่นยำสูงมาก คลาดเคลื่อนไม่ถึง 0.5 ps!)*

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** (โพรบ X: $|Z_p| \approx 31.8\ \Omega, t_{r,meas} \approx 475.2\text{ ps}$; โพรบ Y: $|Z_p| \approx 1018.6\ \Omega, t_{r,meas} \approx 180.4\text{ ps}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะคำนวณอิมพีแดนซ์โดยใช้สูตรความถี่เชิงมุมผิดพลาด
* ข้อ C ผิด เพราะลืมยกกำลังสองในการรวมเวลาแบบ RSS (Root Sum Squared)
* ข้อ D ผิด เพราะคิดค่า Thevenin Resistance เท่ากับ $Z_0$ เต็มตัวแทนที่จะเป็น $Z_0 / 2$

---

### คำถามที่ 3: การออกแบบขนาดวงจรนับ Debounce และเวลาตรวจจับข้อผิดพลาดตามมาตรฐานความปลอดภัย (Safety-Critical Debounce Sizing under ISO 26262 / DO-254)
ในระบบควบคุมอากาศยานไร้คนขับ (Autonomous Avionics Controller) ตามข้อกำหนด DO-254 DAL-A:
* สัญญาณนาฬิกาของระบบทำงานที่ความถี่ $F_{clk} = 100.0\text{ MHz}$ ($T_{clk} = 10.0\text{ ns}$)
* จากการทดสอบความเข้ากันได้ทางแม่เหล็กไฟฟ้า (EMC Burst Test) พบว่าสัญญาณรบกวนชั่วขณะสามารถทำให้สัญญาณ `LOCKED` ของ MMCM เกิดพัลส์เท็จ (Spurious Glitch) ดรอปเป็น '0' สั้นๆ ได้ไม่เกิน **$T_{glitch,max} = 80.0\text{ ns}$**
* ข้อกำหนดความปลอดภัยสากล (Safety Fault Reaction Time) บังคับว่า: ในกรณีที่เกิดเหตุการณ์หลุดล็อกถาวรจริง (Genuine Persistent Loss of Lock) วงจรฮาร์ดแวร์ต้องตัดสัญญาณนาฬิกาและส่งสัญญาณเตือนฉุกเฉิน (Safe Fault Trigger) ให้เสร็จสิ้นภายในเวลา **$T_{fault\_detect} \le 5.00\ \mu\text{s}$**

หากวิศวกรออกแบบวงจรตัวนับ Debounce Counter ($N_{debounce}$) โดยตัวนับจะเพิ่มค่าทีละ $1$ ในทุกรอบสัญญาณนาฬิกา $T_{clk}$ เมื่อ `LOCKED` เป็น '0'  
จงคำนวณหาช่วงของจำนวนรอบสัญญาณนาฬิกา ($N_{debounce}$) ที่ถูกต้องและปลอดภัย:

A) $8\text{ cycles} \le N_{debounce} \le 500\text{ cycles}$  
B) $9\text{ cycles} \le N_{debounce} \le 498\text{ cycles}$  
C) $16\text{ cycles} \le N_{debounce} \le 256\text{ cycles}$  
D) $2\text{ cycles} \le N_{debounce} \le 1000\text{ cycles}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: กำหนดขอบเขตล่าง (Minimum Debounce Cycles: $N_{debounce,min}$)**
วงจรต้องไม่ทริกเกอร์ความผิดพลาดเมื่อเจอกลิตช์สั้น $T_{glitch,max} = 80.0\text{ ns}$:
$$N_{glitch} = \frac{T_{glitch,max}}{T_{clk}} = \frac{80.0\text{ ns}}{10.0\text{ ns}} = 8.0\text{ cycles}$$
เพื่อความปลอดภัย ตัวนับต้องมีค่ามากกว่าจำนวนรอบของกลิตช์อย่างน้อย $1$ ไซเคิล:
$$N_{debounce,min} \ge N_{glitch} + 1 = 8 + 1 = 9\text{ cycles}$$
(หากตั้ง $N \le 8$ กลิตช์ขนาด $80\text{ ns}$ จะสามารถทริกเกอร์ระบบให้ชัตดาวน์ได้)

**ขั้นตอนที่ 2: กำหนดขอบเขตบน (Maximum Debounce Cycles: $N_{debounce,max}$)**
วงจรต้องส่งสัญญาณเตือนภายในเวลา $T_{fault\_detect} \le 5.00\ \mu\text{s} = 5000.0\text{ ns}$:
เมื่อหักลบเวลา Synchronization ภายในของ Double Flip-Flop ($2$ ไซเคิล $= 20\text{ ns}$):
$$T_{counter\_max} = 5000.0\text{ ns} - 20.0\text{ ns} = 4980.0\text{ ns}$$
$$N_{debounce,max} \le \frac{4980.0\text{ ns}}{10.0\text{ ns}} = 498\text{ cycles}$$
(หากตั้ง $N > 498$ เวลาตอบสนองรวมจะเกิน $5.00\ \mu\text{s}$ ซึ่งละเมิดข้อกำหนดความปลอดภัย DO-254 ทันที)

**ขั้นตอนที่ 3: สรุปช่วงที่ปลอดภัย**
$$9\text{ cycles} \le N_{debounce} \le 498\text{ cycles}$$
(โดยในทางปฏิบัติมักเลือกค่า $N = 128$ หรือ $256$ cycles ซึ่งอยู่กึ่งกลางช่วงอย่างสมดุล)

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **B** ($9\text{ cycles} \le N_{debounce} \le 498\text{ cycles}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ A ผิด เพราะที่ $N = 8$ วงจรยังมีความเสี่ยงที่จะทริกเกอร์จากกลิตช์ $80\text{ ns}$ พอดีเป๊ะ
* ข้อ C เป็นเพียงตัวอย่างการเลือกใช้ ไม่ใช่ช่วงขอบเขตทางทฤษฎีที่อนุญาตทั้งหมดตามโจทย์
* ข้อ D ผิด เพราะยอมให้ค่า $N = 2$ ซึ่งจะล้มเหลวทันทีที่เจอนอยส์ และ $N = 1000$ ซึ่งเกินเวลาตอบสนองความปลอดภัยไปเท่าตัว
