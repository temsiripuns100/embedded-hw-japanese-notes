# Lesson 172: FPGA CDC Part 2 - Pulse Synchronizers & Fast-to-Slow CDC (Toggle Synchronizers, Pulse Stretching Physics, Minimum Interval Bounds & Closed-Loop Acknowledge)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 วิกฤตการณ์การข้ามโดเมนจากเร็วไปช้า (The Fast-to-Slow CDC Dilemma)
เมื่อสัญญาณพัลส์ขนาดความกว้าง 1 รอบสัญญาณนาฬิกา ถูกสร้างขึ้นในโดเมนนาฬิกาความเร็วสูง (**Fast Clock: $f_{fast} = 400\text{ MHz}$, $T_{fast} = 2.5\text{ ns}$**) และจำเป็นต้องถูกส่งข้ามไปยังโดเมนนาฬิกาที่ช้ากว่ามาก (**Slow Clock: $f_{slow} = 40\text{ MHz}$, $T_{slow} = 25.0\text{ ns}$**):

หากวิศวกรนำสัญญาณพัลส์นี้ไปต่อเข้าฟลิปฟล็อป 2-Stage Synchronizer แบบธรรมดาโดยตรง จะเกิดสภาวะ **"พัลส์ล่องหน (Pulse Swallowing / Missed Pulse)"** อย่างหลีกเลี่ยงไม่ได้:

```
                   ปรากฏการณ์พัลส์ล่องหน (PULSE SWALLOWING)
                   
   Fast CLK (400MHz) : ─/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_
   Pulse In (2.5ns)  : ───/‾‾‾\________________________________________________
                          │ (กว้างเพียง 2.5ns)
   Slow CLK (40MHz)  : ───────────────────────/‾‾‾‾‾‾‾‾‾‾‾‾\___________________
                                              ▲
                                      (Sampling Edge อยู่ตรงนี้!)
   ===> ขอบสัญญาณนาฬิกาของ Slow Clock มาถึงหลังพัลส์ดับไปแล้วนานถึง 20ns!
        สัญญาณพัลส์จึง "สูญหายไปอย่างไร้ร่องรอย 100%" (Missed by Slow Clock!)
```

#### การคำนวณความน่าจะเป็นในการจับสัญญาณได้สำเร็จ ($P_{capture}$):
หากความสัมพันธ์ของเฟสระหว่างสัญญาณนาฬิกาทั้งสองเป็นแบบสุ่ม (Asynchronous Random Phase):

$$P_{capture} = \frac{T_{pulse} - (T_{setup} + T_{hold})}{T_{slow}}$$
แทนค่าตัวเลข:
$$P_{capture} = \frac{2.5\text{ ns} - (0.15\text{ ns} + 0.10\text{ ns})}{25.0\text{ ns}} = \frac{2.25\text{ ns}}{25.0\text{ ns}} = 0.090 \quad (9.0\%)$$

ความน่าจะเป็นที่จะจับพัลส์ได้มีเพียง **$9.0\%$ เท่านั้น!** หมายความว่าพัลส์คำสั่งมากกว่า **$91\%$ จะสูญหายไปในความว่างเปล่า** ก่อให้เกิดความล้มเหลวร้ายแรงของระบบ!

---

### 1.2 สถาปัตยกรรม Toggle-Based Pulse Synchronizer

เพื่อแก้ปัญหาพัลส์หาย สถาปัตยกรรมมาตรฐานสากลคือการแปลงพัลส์ชั่วขณะ ให้กลายเป็น **การเปลี่ยนระดับสัญญาณแบบถาวร (Level Transition)** โดยใช้วงจร **Toggle Synchronizer**:

```
                 สถาปัตยกรรม TOGGLE-BASED PULSE SYNCHRONIZER
                 
     [ FAST CLOCK DOMAIN (CLK_FAST) ]                 [ SLOW CLOCK DOMAIN (CLK_SLOW) ]
     
     pulse_in ──┐
                ▼
            ┌───────┐      toggle_fast               sync_q2       sync_q3
            │ T-FF  │──────────────────► [ 2-FF Sync ] ──────┬──────────┐
            │ Logic │   (สัญญาณระดับ     (ASYNC_REG)        │          ▼
            └───────┘    คงอยู่ตลอดไป)                      │       ┌──────┐
                                                            └──────►│ XOR  ├──► pulse_out
                                                                    │ Gate │   (1-Cycle Pulse)
                                                                    └──────┘
```

#### กลไกการทำงานทีละสเต็ป (Step-by-Step Dynamics):
1. **ใน Fast Domain:** ทุกครั้งที่มีสัญญาณ `pulse_in = 1` เข้ามาเพียง 1 ไซเคิล วงจร T-Flip-Flop (หรือ XOR Feedback) จะทำการ **สลับสถานะของสัญญาณ (Toggle)** จาก $0 \to 1$ หรือจาก $1 \to 0$
2. **ข้าม CDC Boundary:** สัญญาณระดับที่เพิ่งถูกสลับสถานะจะคงค้างสถานะนั้นไว้อย่างไม่มีกำหนด ทำให้โดเมน Slow Clock มีเวลาเหลือเฟือที่จะแซมเปิลการเปลี่ยนแปลงระดับนี้ผ่านวงจร 2-FF/3-FF Synchronizer
3. **ใน Slow Domain:** นำสัญญาณเอาต์พุตของ Synchronizer เข้าสู่วงจรตรวจจับขอบสัญญาณ (Edge Detector) โดยใช้ประตู XOR ระหว่างสเตจที่ 2 และสเตจที่ 3:
   $$\text{pulse\_out} = \text{sync\_q2} \oplus \text{sync\_q3}$$
   ไม่ว่าสัญญาณจะสลับจาก $0 \to 1$ หรือ $1 \to 0$ ประตู XOR จะสร้างสัญญาณ **พัลส์สะอาดขนาดกว้าง 1 ไซเคิลของ Slow Clock** ออกมาเสมอ $100\%$!

```verilog
// แม่แบบ RTL ของ Toggle-Based Pulse Synchronizer
module pulse_sync_fast2slow (
    input  wire clk_fast,
    input  wire rst_fast_n,
    input  wire pulse_fast_in,
    
    input  wire clk_slow,
    input  wire rst_slow_n,
    output wire pulse_slow_out
);

    // Fast Domain: Toggle Logic
    reg toggle_fast;
    always @(posedge clk_fast or negedge rst_fast_n) begin
        if (!rst_fast_n)
            toggle_fast <= 1'b0;
        else if (pulse_fast_in)
            toggle_fast <= ~toggle_fast;
    end

    // Slow Domain: Multi-Stage Synchronizer with Edge Detection
    (* ASYNC_REG = "TRUE" *) reg sync_ff1, sync_ff2, sync_ff3;
    always @(posedge clk_slow or negedge rst_slow_n) begin
        if (!rst_slow_n) begin
            sync_ff1 <= 1'b0;
            sync_ff2 <= 1'b0;
            sync_ff3 <= 1'b0;
        end else begin
            sync_ff1 <= toggle_fast;
            sync_ff2 <= sync_ff1;
            sync_ff3 <= sync_ff2;
        end
    end

    // Reconstruct clean 1-cycle pulse
    assign pulse_slow_out = sync_ff2 ^ sync_ff3;

endmodule
```

---

### 1.3 สมการระยะห่างขั้นต่ำระหว่างพัลส์ (Minimum Pulse Spacing / Hold-Off Bound)

> [!CAUTION]
> **ข้อจำกัดวิกฤตของ Toggle Synchronizer (The Minimum Interval Trap):**  
> วงจร Toggle Synchronizer จะทำงานได้ถูกต้อง ก็ต่อเมื่อสัญญาณพัลส์ใน Fast Domain **ไม่เกิดขึ้นซ้ำเร็วจนเกินไป**!  
> หากพัลส์ที่ 2 เข้ามาในขณะที่การ Toggle ของพัลส์แรกยังเดินทางข้าม Synchronizer ไปไม่ถึง Slow Domain สัญญาณจะ Toggle ซ้ำกลับมาเป็นค่าเดิม ส่งผลให้ Slow Domain มองไม่เห็นทั้งสองพัลส์เลย!

```
                  หายนะเมื่อพัลส์เข้ามาถี่เกินไป (PULSE COALESCING)
                  
   Fast Pulse  : ──/‾‾\____/‾‾\________________________________________ (พัลส์ 1 และ 2 มาติดกัน)
   Fast Toggle : ──/‾‾‾‾‾‾‾\___________________________________________ (0 -> 1 แล้วดีดกลับ 1 -> 0 ทันที!)
                   |<----->| สัญญาณ Toggle กว้างเพียง 5ns!
   Slow Clock  : ────────────────────────────/‾‾‾‾‾‾‾‾‾‾‾‾\____________
   ===> Slow Clock มองเห็นเป็นเส้นตรงระดับ 0 ตลอดเวลา! พัลส์ทั้งสองตัวหายวับไปคู่!
```

#### การคำนวณระยะห่างขั้นต่ำที่ปลอดภัย (Minimum Pulse Interval Equation):
เพื่อให้แน่ใจว่า Slow Domain จะจับสถานะของการ Toggle ได้อย่างน้อย 1 ครั้งเต็มๆ:

$$T_{interval\_min} \ge (N_{sync} + 1) \cdot T_{slow} + T_{fast}$$

โดยที่:
* $N_{sync}$ คือจำนวนสเตจของ Synchronizer (เช่น 2 หรือ 3 สเตจ)
* $T_{slow}$ คือคาบเวลาของสัญญาณนาฬิกาฝั่งช้า
* $T_{fast}$ คือคาบเวลาของสัญญาณนาฬิกาฝั่งเร็ว

**ตัวอย่างเช่น:** หาก $T_{slow} = 25\text{ ns}$ (40MHz), $T_{fast} = 2.5\text{ ns}$ (400MHz), และใช้ 2-Stage Sync ($N_{sync} = 2$):
$$T_{interval\_min} \ge (2 + 1) \cdot 25\text{ ns} + 2.5\text{ ns} = 75\text{ ns} + 2.5\text{ ns} = 77.5\text{ ns}$$
หมายความว่า สัญญาณพัลส์ในฝั่ง Fast จะต้องส่งห่างกันอย่างน้อย **$77.5\text{ ns}$ (หรือเว้นระยะอย่างน้อย 31 ไซเคิลของ Fast Clock)** จึงจะรับประกันว่าจะไม่มีพัลส์สูญหาย!

---

### 1.4 วงจรซิงโครไนซ์แบบตอบรับวงปิด (Closed-Loop Handshake Pulse Synchronizer)

หากในระบบจริง พัลส์มีโอกาสเกิดขึ้นแบบระเบิด (Burst) หรือไม่สามารถรับประกันระยะห่างขั้นต่ำ $T_{interval\_min}$ ได้ วิศวกรต้องเปลี่ยนมาใช้ **Closed-Loop Handshake Synchronizer** ซึ่งมีการส่งสัญญาณ Acknowledge ย้อนกลับ:

```
                สถาปัตยกรรม CLOSED-LOOP HANDSHAKE SYNCHRONIZER
                
    [ Fast Clock Domain ]                           [ Slow Clock Domain ]
    
    pulse_in ──► [ Pulse Capture ] ──(req_level)──► [ 2-FF Sync ] ──► pulse_out
                      ▲                                   │
                      │                                   ▼
                [ 2-FF Sync ] ◄──────(ack_level)──────────┘
                      │
    busy_flag ◄───────┘ (แจ้งสถานะ BUSY: ห้ามป้อนพัลส์ใหม่จนกว่าจะเสร็จสิ้น)
```

1. เมื่อมีพัลส์เข้าใน Fast Domain วงจรจะล็อกสถานะ `REQ = 1` และขับสัญญาณ `BUSY = 1`
2. สัญญาณ `REQ` ข้าม 2-FF ไปยัง Slow Domain เพื่อสร้าง `pulse_out` พร้อมตอบกลับ `ACK = 1`
3. สัญญาณ `ACK` ข้าม 2-FF กลับมายัง Fast Domain เพื่อปลดล็อก `REQ = 0` และปลดสัญญาณ `BUSY = 0`
4. **ผลลัพธ์:** ปลอดภัย $100\%$ โดยไม่มีวันสูญเสียพัลส์แม้แต่ตัวเดียว แต่ระบบจะต้องยอมรับความล่าช้าแบบ Round-Trip Latency

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: เครื่องกัดพลาสม่าผลิตเวเฟอร์เซมิคอนดักเตอร์ชิ้นงานพังมูลค่า 8 ล้านบาท (Semiconductor Etcher Plasma Strobe Loss)

```
+----------------------------------------------------------------------------------------------------+
| กรณีศึกษาความล้มเหลวหน้างาน (現場の失敗事例)                                                                 |
| เหตุการณ์: เครื่องกัดลายวงจรพลาสม่าบนเวเฟอร์ขนาด 300 มม. (Plasma Etch Chamber Controller) ในโรงงานชิป     |
| อาการ: เวเฟอร์ซิลิคอนที่ผ่านการกัดกรดมีความลึกของร่องทรานซิสเตอร์ไม่สม่ำเสมอทั่วทั้งแผ่น (Etch Non-Uniformity) |
|        ทำให้ชิปบนเวเฟอร์เสียหายทั้งล็อต มูลค่าความเสียหายมากกว่า 250,000 ดอลลาร์สหรัฐ (ประมาณ 8.5 ล้านบาท)  |
|        การตรวจสอบระบบควบคุมพบว่า คำสั่ง Strobe ปรับกำลังงานพลาสม่าขาดหายไปแบบสุ่มประมาณ 11% ของคำสั่งทั้งหมด |
+----------------------------------------------------------------------------------------------------+
```

#### การวิเคราะห์หาสาเหตุรากเหง้าด้วยหลักการ 5 Whys (5 Whys Root Cause Analysis):

1. **ทำไมร่องทรานซิสเตอร์บนเวเฟอร์จึงมีความลึกไม่สม่ำเสมอ?**  
   *คำตอบ:* กล่องกำเนิดคลื่นวิทยุพลาสม่า (RF Plasma Generator) ขาดการรับสัญญาณพัลส์สอบเทียบกำลังงาน (Calibration Strobe Pulses) ในบางจังหวะ

2. **ทำไมสัญญาณ Calibration Strobe จึงขาดหายไปเป็นระยะ?**  
   *คำตอบ:* สัญญาณพัลส์ที่สร้างจาก DSP Core ความเร็วสูง ($200\text{ MHz}$, กว้าง $5\text{ ns}$) ส่งข้ามไปยังโมดูลควบคุมวาล์วก๊าซและหัวจุดพลาสม่า ($20\text{ MHz}$, คาบเวลา $50\text{ ns}$) หลุดรอดการแซมเปิลไป

3. **ทำไมสัญญาณพัลส์จึงหลุดรอดการแซมเปิล?**  
   *คำตอบ:* วิศวกรต่อพัลส์ $5\text{ ns}$ ตรงเข้าสู่ 2-Stage Synchronizer ในโดเมน $20\text{ MHz}$ โดยตรง ซึ่งมีคาบเวลาใหญ่กว่าพัลส์ถึง 10 เท่า ทำให้ขอบนาฬิกาของฝั่งรับมองไม่เห็นพัลส์ในรอบส่วนใหญ่

4. **ทำไมข้อผิดพลาดร้ายแรงนี้จึงไม่ถูกตรวจพบในการจำลอง (Simulation)?**  
   *คำตอบ:* ใน Testbench ของแล็บ สัญญาณนาฬิกาทั้ง $200\text{ MHz}$ และ $20\text{ MHz}$ ถูกสร้างขึ้นจากบล็อกจำลองเดียวกันที่มีความสัมพันธ์ทางเฟสแบบซิงโครนัสพอดี ทำให้ขอบนาฬิกาบังเอิญตกลงบนพัลส์พอดี $100\%$ ตลอดการซิมูเลชัน!

5. **ทำไมวิศวกรจึงไม่ใช้วงจร Toggle Synchronizer?**  
   *คำตอบ:* วิศวกรขาดความเข้าใจเรื่องอัตราส่วนความกว้างพัลส์ต่อคาบเวลาฝั่งรับ ($T_{pulse} \ll T_{slow}$) และคิดว่า "คำว่าซิงโครไนซ์ แปลว่าใส่ 2-FF เสมอ" โดยไม่ตระหนักถึงฟิสิกส์ของการข้ามจากเร็วไปช้า!

---

### 2.2 ผังภูมิก้างปลาวิเคราะห์ปัญหา (Ishikawa Fishbone Diagram)

```
                       ผังภูมิก้างปลาวิเคราะห์สาเหตุ PLASMA STROBE LOSS
                       
   [ ความเข้าใจผิดด้านวิศวกรรม (Mindset) ]          [ สถาปัตยกรรมวงจร CDC (Architecture) ]
   เชื่อว่า 2-FF ใช้ได้กับสัญญาณทุกชนิด             ส่งพัลส์ 5ns เข้า 2-FF ในโดเมน 50ns ตรงๆ
             \                                           \
              \                                           \
               \                                           \  พัลส์แคบเกินกว่าจะถูกแซมเปิล
   ขาดความรู้เรื่อง Fast-to-Slow Pulse Loss                     ไม่มีวงจร Toggle หรือ Pulse Stretch
                 \                                           \
                  +-------------------------------------------+
                  |                                           |
                  |   PLASMA ETCH STROBE LOSS (WAFER SCRAP)   | =====> [ FAILURE! ]
                  |                                           |
                  +-------------------------------------------+
                 /                                           /
                /                                           /  ขาด SVA Assertion ตรวจจับพัลส์หาย
   Testbench ใช้ Clocks ที่มีเฟสล็อกตรงกันสมบูรณ์              ไม่ได้รันการจำลองแบบ Random Clock Skew
              /                                           /
   [ สภาพแวดล้อมการจำลอง (Verification Gap) ]        [ เครื่องมือและการตรวจเช็ค (Tools & Assertions) ]
```

---

### 2.3 คู่มือปฏิบัติงาน SOP: การออกแบบ Fast-to-Slow Pulse Synchronizer (Zero-Loss SOP)

#### สเต็ปที่ 1: ตรวจสอบอัตราส่วนคาบเวลาสัญญาณนาฬิกา (Clock Period Ratio Audit)
* คำนวณอัตราส่วนความถี่:
  $$\text{Ratio} = \frac{T_{slow}}{T_{fast}} = \frac{f_{fast}}{f_{slow}}$$
* หาก $\text{Ratio} > 1.5$: **ห้ามส่งสัญญาณพัลส์เข้า 2-FF โดยเด็ดขาด!** ต้องใช้วงจร Toggle Synchronizer หรือ Handshake Synchronizer เท่านั้น

#### สเต็ปที่ 2: ตรวจสอบระยะห่างขั้นต่ำของพัลส์ต้นทาง (Pulse Spacing Verification)
* คำนวณค่า $T_{interval\_min} = (N_{sync} + 1) \cdot T_{slow} + T_{fast}$
* ใส่คำสั่ง **SystemVerilog Assertion (SVA)** ใน RTL ฝั่งต้นทางเพื่อแจ้งเตือนทันทีหากมีพัลส์เข้ามาถี่เกินเกณฑ์ความปลอดภัย:

```systemverilog
// SVA ตรวจสอบระยะห่างขั้นต่ำระหว่างสองพัลส์ใน Fast Domain
property p_min_pulse_spacing;
    @(posedge clk_fast) disable iff (!rst_fast_n)
    pulse_fast_in |=> (!pulse_fast_in)[*MIN_FAST_CYCLES];
endproperty
assert property (p_min_pulse_spacing)
    else $error("[FATAL CDC ERROR] Fast pulses arrive too close! Spacing violated!");
```

#### สเต็ปที่ 3: เลือกใช้ Closed-Loop Handshake หากพัลส์มาเป็น Burst
* หากระบบไม่สามารถรับประกันระยะห่างขั้นต่ำได้ ให้เปลี่ยนไปใช้โมดูล **`xpm_cdc_handshake`** หรือวงจร Closed-Loop Acknowledge เพื่อสร้างกลไก Backpressure (สัญญาณ `busy`) ป้องกันข้อมูลล้น

#### สเต็ปที่ 4: การกำหนดคอนสเตรนต์ XDC
* กำหนด `set_max_delay -datapath_only` บนสาย Toggle Signal เพื่อจำกัดเวลาเดินสายไม่ให้เกินคาบเวลาของ Slow Clock:

```tcl
set_max_delay -from [get_cells -hierarchical *toggle_fast_reg*] \
              -to   [get_cells -hierarchical *sync_ff1_reg*] \
              -datapath_only [get_property PERIOD [get_clocks clk_slow]]
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง

| คำศัพท์คันジ / คาตากานะ | คำอ่าน (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- |
| **パルス同期化** | Parusu Doukika | Pulse Synchronization (การซิงโครไนซ์สัญญาณพัลส์) |
| **トグル同期化** | Toguru Doukika | Toggle Synchronization (การซิงโครไนซ์โดยการสลับสถานะ) |
| **サンプリング見逃し** | Sanpuringu Minogashi | Sample Miss / Pulse Swallowing (การหลุดรอดการแซมเปิล) |
| **パルス幅拡張** | Parusu-haba Kakuchou | Pulse Stretching (การยืดความกว้างพัลส์ให้ยาวขึ้น) |
| **最小パルス間隔** | Saishou Parusu Kankaku | Minimum Pulse Spacing (ระยะห่างขั้นต่ำระหว่างพัลส์) |
| **高速から低速への乗せ換え**| Kousoku kara Teisoku e no Nosekae| Fast-to-Slow CDC (การข้ามโดเมนจากคล็อกเร็วไปคล็อกช้า) |
| **ハンドシェイク応答** | Handosheiku Outou | Handshake Acknowledge (การตอบรับแบบแฮนด์เชก) |
| **エッジ検出回路** | Ejji Kenshutsu Kairo | Edge Detection Circuit (วงจรตรวจจับขอบสัญญาณ) |
| **逆流防止** | Gyakuryuu Boushi | Backpressure Control (การควบคุมแรงดันย้อนกลับ/สถานะ Busy) |
| **不連続サンプリング** | Furenzoku Sanpuringu | Discontinuous Sampling (การแซมเปิลที่ไม่ต่อเนื่อง) |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図の現場会話)

#### สถานการณ์ที่ 1: การตรวจพบการต่อพัลส์เร็วเข้าคล็อกช้าโดยตรง (Fast-to-Slow Pulse Review)
* **สถานที่:** แผนกออกแบบวงจรควบคุมเครื่องจักรผลิตเซมิคอนดักเตอร์ (Semiconductor Manufacturing Equipment R&D, Fuchu, Tokyo)  
* **ตัวละคร:** ทาคามุระ (หัวหน้าฝ่ายวิศวกรรมอาวุโส - Chief Reviewer) และ อธิป (วิศวกรออกแบบระบบ - RTL Designer)

```
高村技師長 (Takamura):
「アティップさん、プラズマチャンバー制御回路のCDC記述を見ました。
200MHzのDSPドメインから出力されるトリガーパルス（幅5ns）を、
そのまま20MHz（周期50ns）のバルブ制御回路の2段FFへ直結していますね。
この回路で本当にパルスが正しく伝達できると本気で思っているのですか？」
(คุณอธิปครับ ผมตรวจโค้ด CDC ของวงจรควบคุมแชมเบอร์พลาสม่าแล้วครับ
คุณเอาพัลส์ทริกเกอร์ขนาด 5ns จากโดเมน DSP 200MHz ต่อตรงเข้าฟลิปฟล็อป 2 สเตจ
ในโดเมนวาล์วคอนโทรล 20MHz (คาบเวลา 50ns) เลยนะครับ
นี่คุณคิดจริงๆ หรือครับว่าวงจรนี้มันจะส่งผ่านพัลส์ได้อย่างถูกต้องน่ะ?)

アティップ (Athip):
「はい、非同期クロック乗せ換えなので、メタスタビリティを防ぐために教科書通り
2段の同期化FFを通しました。シミュレーションでも問題なくパルスが検出されていましたが…」
(ครับ เพราะมันเป็นการข้ามโดเมนนาฬิกา เพื่อป้องกัน Metastability ผมเลยใส่ FF 2 สเตจ
ตามตำราเรียนเป๊ะๆ เลยครับ ในการจำลอง Simulation ก็เห็นพัลส์ถูกตรวจจับได้ปกติดีนี่ครับ...)

高村技師長 (Takamura):
「シミュレーションのテストベンチが、2つのクロックの位相を固定したおもちゃだったから見落としただけです！
20MHzのクロック周期は50nsです。幅5nsのパルスなど、10回のうち9回はクロックのエッジが来ない
空白地帯に落ちて消滅します！ 捕捉確率はわずか10%以下です！
だから実機でプラズマの点火ミスが多発し、800万円ものウェハーがスクラップになったのですよ！
高速から低速へパルスを渡す際は、パルスをレベル信号に変換する『トグル同期化回路（Toggle Synchronizer）』
を採用するのがエンジニアの常識です！
直ちにトグルフリップフロップと受信側のXORエッジ検出ロジックへ書き換えなさい！」
(นั่นเพราะ Testbench ในซิมูเลชันของคุณมันเป็นแค่ของเล่นที่ล็อกเฟสของสองคล็อกไว้ตรงกันต่างหากล่ะครับ!
คาบเวลาของคล็อก 20MHz มันคือ 50ns นะครับ พัลส์กว้างแค่ 5ns มันย่อมร่วงลงไปในช่องว่างที่ไม่มีขอบนาฬิกา
ถึง 9 ใน 10 ครั้งและสูญหายไปในความมืดครับ! โอกาสจับได้มีไม่ถึง 10% ด้วยซ้ำ!
นี่คือสาเหตุที่เครื่องจักรจุดพลาสม่าพลาดบ่อยๆ บนบอร์ดจริงจนเวเฟอร์ราคา 8 ล้านบาทพังยับเยินไงครับ!
การส่งพัลส์จากเร็วไปช้า การใช้วงจร 'Toggle Synchronizer' แปลงพัลส์เป็นระดับสัญญาณ มันเป็นสามัญสำนึกของวิศวกรเลยนะครับ!
จงรีบเปลี่ยนไปใช้ Toggle FF ร่วมกับลอจิกตรวจจับขอบ XOR ในฝั่งรับเดี๋ยวนี้เลยครับ!)
```

---

#### สถานการณ์ที่ 2: การตรวจสอบเงื่อนไข Minimum Pulse Spacing และการใส่ SVA
```
高村技師長 (Takamura):
「トグル同期化回路への書き換え、確認しました。
これで幅5nsのパルスでも確実に低速側へ届くようになります。
しかし、入力パルスの最短発生間隔（Minimum Pulse Spacing）の保護ロジックがありませんね。」
(การแก้เป็น Toggle Synchronizer ตรวจสอบเรียบร้อยดีครับ
เท่านี้พัลส์กว้าง 5ns ก็จะวิ่งไปถึงฝั่งช้าได้อย่างแน่นอนแล้ว
แต่ผมยังไม่เห็นลอจิกป้องกันระยะห่างขั้นต่ำระหว่างพัลส์ (Minimum Pulse Spacing) เลยนะครับ)

アティップ (Athip):
「トグル回路なので、パルスが来ればいつでも反転して伝送できると考えていましたが…」
(เพราะมันเป็นวงจร Toggle ผมเลยคิดว่าเมื่อไหร่ที่มีพัลส์มา มันก็แค่สลับสถานะแล้วส่งต่อได้ตลอดเวลานี่ครับ...)

高村技師長 (Takamura):
「反転した信号が20MHz側の2段FFを通り抜ける前に、次のパルスが来て再び反転してしまったら
どうなりますか？ 信号は元の値に戻り、20MHz側からは『何も変化しなかった』ように見えて
両方のパルスが消滅します！
20MHz（50ns）に2段FFを通すなら、パルス間隔は最低でも『(2+1)×50ns + 5ns = 155ns』、
すなわち200MHzドメインで『31サイクル以上』空ける必要があります！
RTLにこの間隔を監視するSVAアサーションを埋め込み、仕様書に最短パルス間隔の規定を明記しなさい！」
(ถ้าสัญญาณที่สลับไป มันยังเดินทางผ่าน 2-FF ฝั่ง 20MHz ไม่ทันเสร็จ แล้วมีพัลส์ที่สองเข้ามาสลับมันกลับคืน
จะเกิดอะไรขึ้นล่ะครับ? สัญญาณจะดีดกลับไปเป็นค่าเดิม แล้วฝั่ง 20MHz ก็จะมองเห็นว่า 'ไม่มีอะไรเปลี่ยนแปลง'
จนพัลส์ทั้งสองตัวหายวับไปพร้อมกันทันทีครับ!
ในระบบ 20MHz (50ns) ที่ใช้ 2-FF คุณต้องเว้นระยะห่างระหว่างพัลส์อย่างน้อยที่สุด '(2+1)×50ns + 5ns = 155ns'
หรือคิดเป็น '31 ไซเคิลขึ้นไป' ในโดเมน 200MHz ครับ!
จงฝัง SVA Assertion เพื่อเฝ้าระวังระยะห่างนี้ลงใน RTL และระบุข้อกำหนดนี้ลงในเอกสาร Spec ให้ชัดเจนเดี๋ยวนี้ครับ!)
```

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณความน่าจะเป็นของการสูญเสียพัลส์ในระบบ Fast-to-Slow แบบไร้ Toggle Logic

#### โจทย์คำถาม:
ในโมดูลประมวลผลเรดาร์ตรวจจับวัตถุ สัญญาณพัลส์ระบุตำแหน่งเป้าหมาย (Target Strobe) มีขนาดความกว้าง $1\text{ ไซเคิล}$ ถูกสร้างขึ้นในโดเมนนาฬิกาเร็ว $f_{fast} = 300\text{ MHz}$ ($T_{fast} = 3.333\text{ ns}$)

พัลส์นี้ถูกส่งตรงเข้าสู่วงจรฟลิปฟล็อป 2-Stage Synchronizer ในโดเมนนาฬิกาช้า $f_{slow} = 33.333\text{ MHz}$ ($T_{slow} = 30.000\text{ ns}$) โดยไม่มีวงจรยืดพัลส์ (Pulse Stretching) หรือ Toggle Logic ใดๆ กั้นกลาง

พารามิเตอร์ทางกายภาพของฟลิปฟล็อปฝั่งรับ:
* Setup Time: $T_{su} = 0.150\text{ ns}$
* Hold Time: $T_{hold} = 0.100\text{ ns}$
* หน้าต่างเวลาวิกฤตสำหรับการแซมเปิลที่สมบูรณ์: $T_{window} = T_{su} + T_{hold} = 0.250\text{ ns}$
* สมมติว่าความสัมพันธ์ทางเฟสระหว่าง $CLK_{fast}$ และ $CLK_{slow}$ มีการกระจายตัวแบบสุ่มสม่ำเสมอ (Uniform Random Distribution)

จงคำนวณหา:
1. ช่วงเวลาที่ขอบสัญญาณนาฬิกาของ $CLK_{slow}$ สามารถแซมเปิลพัลส์ได้อย่างถูกต้องโดยไม่ละเมิด Setup/Hold ($T_{capture\_valid}$)
2. ความน่าจะเป็นทางคณิตศาสตร์ที่พัลส์จะถูกจับได้สำเร็จ ($P_{capture}$)
3. อัตราการสูญเสียพัลส์ (Pulse Loss Rate: $P_{loss}$) ของระบบนี้

* ก. $T_{capture\_valid} = 3.083\text{ ns}$, $P_{capture} \approx 10.28\%$, อัตราการสูญเสียพัลส์ $P_{loss} \approx 89.72\%$
* ข. $T_{capture\_valid} = 3.333\text{ ns}$, $P_{capture} \approx 11.11\%$, อัตราการสูญเสียพัลส์ $P_{loss} \approx 88.89\%$
* ค. $T_{capture\_valid} = 3.083\text{ ns}$, $P_{capture} \approx 5.14\%$, อัตราการสูญเสียพัลส์ $P_{loss} \approx 94.86\%$
* ง. $T_{capture\_valid} = 2.500\text{ ns}$, $P_{capture} \approx 8.33\%$, อัตราการสูญเสียพัลส์ $P_{loss} \approx 91.67\%$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณช่วงเวลาที่การแซมเปิลถูกต้อง ($T_{capture\_valid}$):**
พัลส์มีความกว้างทั้งหมดเท่ากับคาบเวลาฝั่งเร็ว:
$$T_{pulse} = T_{fast} = 3.333\text{ ns}$$
เพื่อให้การแซมเปิลสำเร็จ ขอบของสัญญาณนาฬิกาฝั่งรับจะต้องตกลงมาหลังจากที่ข้อมูลเริ่มนิ่งแล้วอย่างน้อย $T_{su}$ และต้องเกิดขึ้นก่อนที่พัลส์จะดับลงอย่างน้อย $T_{hold}$:
$$T_{capture\_valid} = T_{pulse} - (T_{su} + T_{hold}) = 3.333\text{ ns} - (0.150\text{ ns} + 0.100\text{ ns}) = 3.333\text{ ns} - 0.250\text{ ns} = 3.083\text{ ns}$$

**ขั้นตอนที่ 2: คำนวณความน่าจะเป็นในการจับสัญญาณได้ ($P_{capture}$):**
เนื่องจากขอบของ Slow Clock มีโอกาสตกลง ณ เวลาใดๆ ภายในคาบเวลา $T_{slow} = 30.000\text{ ns}$ ด้วยความน่าจะเป็นที่สม่ำเสมอ:
$$P_{capture} = \frac{T_{capture\_valid}}{T_{slow}} = \frac{3.083\text{ ns}}{30.000\text{ ns}} \approx 0.102766 \approx 10.28\%$$

**ขั้นตอนที่ 3: คำนวณอัตราการสูญเสียพัลส์ ($P_{loss}$):**
$$P_{loss} = 1 - P_{capture} = 1 - 0.102766 = 0.897234 \approx 89.72\%$$

ผลลัพธ์แสดงให้เห็นชัดเจนว่า การต่อพัลส์เร็วข้ามไปยังคล็อกช้าโดยตรง จะทำให้พัลส์สูญหายไปเกือบ **$90\%$** ของพัลส์ทั้งหมด!

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ถูกต้องสมบูรณ์แบบ:** ตัวเลข $3.083\text{ ns}$, $P_{capture} \approx 10.28\%$ และ $P_{loss} \approx 89.72\%$ ตรงตามหลักคณิตศาสตร์ความน่าจะเป็น $100\%$
* **ข้อ ข. ไม่ถูกต้อง:** ลืมหักค่า Setup/Hold Window ($0.250\text{ ns}$)
* **ข้อ ค. และ ง. ไม่ถูกต้อง:** ค่าความน่าจะเป็นคำนวณคลาดเคลื่อน

**คำตอบที่ถูกต้อง:** **ข้อ ก.**

---

### ข้อที่ 2: การคำนวณระยะห่างขั้นต่ำและความถี่สูงสุดของพัลส์ใน Toggle Synchronizer

#### โจทย์คำถาม:
ในระบบประมวลผลการแพทย์ วงจร Toggle-Based Pulse Synchronizer รับสัญญาณพัลส์จากโดเมน $CLK_{fast} = 200\text{ MHz}$ ($T_{fast} = 5.000\text{ ns}$) ข้ามไปยังโดเมน $CLK_{slow} = 50\text{ MHz}$ ($T_{slow} = 20.000\text{ ns}$)  
วงจรในโดเมนฝั่งรับใช้ **3-Stage Synchronizer** ($N_{sync} = 3$) เพื่อให้ได้ค่า MTBF ระดับสูงมาก

จงคำนวณหา:
1. ระยะเวลาขั้นต่ำสุดในหน่วยเวลาจริง ($T_{interval\_min}$) ที่ต้องเว้นระยะห่างระหว่างสองพัลส์ที่เข้ามาใน Fast Domain เพื่อรับประกันว่าจะไม่เกิดสภาวะพัลส์ชนกันจนสูญหาย (No Pulse Coalescing)
2. จำนวนรอบสัญญาณนาฬิกาขั้นต่ำ ($Cycles_{fast\_min}$) ของโดเมน $CLK_{fast}$ ที่ต้องเว้นระยะห่าง
3. อัตราการส่งพัลส์สูงสุดในเชิงทฤษฎี (Maximum Sustainable Pulse Rate: $R_{pulse\_max}$) ในหน่วย Mega-Pulses per Second (Mpps)

* ก. $T_{interval\_min} = 85.000\text{ ns}$, $Cycles_{fast\_min} = 17\text{ cycles}$, $R_{pulse\_max} \approx 11.76\text{ Mpps}$
* ข. $T_{interval\_min} = 65.000\text{ ns}$, $Cycles_{fast\_min} = 13\text{ cycles}$, $R_{pulse\_max} \approx 15.38\text{ Mpps}$
* ค. $T_{interval\_min} = 85.000\text{ ns}$, $Cycles_{fast\_min} = 17\text{ cycles}$, $R_{pulse\_max} \approx 50.00\text{ Mpps}$
* ง. $T_{interval\_min} = 105.000\text{ ns}$, $Cycles_{fast\_min} = 21\text{ cycles}$, $R_{pulse\_max} \approx 9.52\text{ Mpps}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณระยะเวลาห่างขั้นต่ำ ($T_{interval\_min}$):**
เมื่อใช้ 3-Stage Synchronizer ($N_{sync} = 3$):
สัญญาณ Toggle ต้องเดินทางผ่านฟลิปฟล็อปทั้ง 3 ตัว และต้องได้รับการแซมเปิลโดยวงจร Edge Detector ในรอบถัดไป:
$$T_{interval\_min} \ge (N_{sync} + 1) \cdot T_{slow} + T_{fast}$$
แทนค่าตัวแปร:
$$T_{interval\_min} = (3 + 1) \times 20.000\text{ ns} + 5.000\text{ ns} = (4 \times 20.000\text{ ns}) + 5.000\text{ ns} = 80.000\text{ ns} + 5.000\text{ ns} = 85.000\text{ ns}$$

**ขั้นตอนที่ 2: คำนวณจำนวนรอบเวลาใน Fast Domain ($Cycles_{fast\_min}$):**
$$Cycles_{fast\_min} = \left\lceil \frac{T_{interval\_min}}{T_{fast}} \right\rceil = \left\lceil \frac{85.000\text{ ns}}{5.000\text{ ns}} \right\rceil = 17\text{ รอบสัญญาณนาฬิกา}$$

**ขั้นตอนที่ 3: คำนวณอัตราการส่งพัลส์สูงสุด ($R_{pulse\_max}$):**
$$R_{pulse\_max} = \frac{1}{T_{interval\_min}} = \frac{1}{85.000 \times 10^{-9}\text{ s}} \approx 11,764,705\text{ pulses/sec} \approx 11.76\text{ Mpps}$$

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ถูกต้องสมบูรณ์แบบ:** $T_{interval} = 85\text{ ns}$, 17 ไซเคิล และอัตรา $11.76\text{ Mpps}$ สอดคล้องกับสูตรวิศวกรรม $100\%$
* **ข้อ ข. ไม่ถูกต้อง:** คิดจำนวนสเตจเป็น 2-FF (ได้ 65ns)
* **ข้อ ค. ไม่ถูกต้อง:** อัตราพัลส์คำนวณผิด (ไปใช้ความถี่ Slow Clock ตรงๆ)
* **ข้อ ง. ไม่ถูกต้อง:** จำนวนสเตจคิดเกินไปเป็น 4 สเตจ

**คำตอบที่ถูกต้อง:** **ข้อ ก.**

---

### ข้อที่ 3: การเปรียบเทียบ Latency ระหว่าง Toggle Synchronizer กับ Closed-Loop Handshake

#### โจทย์คำถาม:
ในสถาปัตยกรรมตัวควบคุมอากาศยาน วิศวกรกำลังเปรียบเทียบกลไกการส่งผ่านพัลส์สองรูปแบบ ระหว่างโดเมนส่ง ($CLK_A = 100\text{ MHz}$, $T_A = 10\text{ ns}$) และโดเมนรับ ($CLK_B = 50\text{ MHz}$, $T_B = 20\text{ ns}$):

* **แบบที่ 1 (Open-Loop Toggle Synchronizer):** ใช้ 2-FF Sync ฝั่งรับ
  * มีค่า Forward Latency ($L_{forward}$) เฉลี่ยเท่ากับความล่าช้าในการข้าม 2-FF ของโดเมน B บวกกับวงจร Edge Detection 1 ไซเคิล
* **แบบที่ 2 (Closed-Loop Handshake Synchronizer):** ใช้ 2-FF Sync ในทิศทางส่ง (REQ) และใช้ 2-FF Sync ในทิศทางตอบรับ (ACK) กลับมายังโดเมน A
  * ระบบจะต้องรอจนกระทั่งสัญญาณ ACK เดินทางกลับมาถึงโดเมน A ก่อนจึงจะปลดสถานะ `BUSY` เพื่อรับพัลส์ถัดไปได้ (Round-Trip Latency: $L_{round\_trip}$)

จงคำนวณหา:
1. ค่า Forward Latency เฉลี่ยของแบบที่ 1 (นับตั้งแต่พัลส์เข้าโดเมน A จนพัลส์ออกที่โดเมน B)
2. ค่า Round-Trip Latency ขั้นต่ำของแบบที่ 2 (เวลาที่โดเมน A ติดสถานะ `BUSY`)

* ก. แบบที่ 1: $L_{forward} \approx 50\text{ ns}$ (2.5 ไซเคิลของ B), แบบที่ 2: $L_{round\_trip} \approx 90\text{ ns}$
* ข. แบบที่ 1: $L_{forward} \approx 60\text{ ns}$ (3.0 ไซเคิลของ B), แบบที่ 2: $L_{round\_trip} \approx 100\text{ ns}$
* ค. แบบที่ 1: $L_{forward} \approx 40\text{ ns}$ (2.0 ไซเคิลของ B), แบบที่ 2: $L_{round\_trip} \approx 60\text{ ns}$
* ง. แบบที่ 1: $L_{forward} \approx 60\text{ ns}$ (3.0 ไซเคิลของ B), แบบที่ 2: $L_{round\_trip} \approx 140\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณ Forward Latency ของแบบที่ 1 (Toggle Sync):**
ในโดเมน B สัญญาณต้องผ่าน 2-FF Synchronizer (2 ไซเคิล) และผ่าน XOR Edge Detection Register อีก 1 ไซเคิล:
$$Total\_Cycles_B = 2_{sync} + 1_{edge} = 3\text{ ไซเคิลของ } CLK_B$$
เวลาหน่วง:
$$L_{forward} = 3 \times T_B = 3 \times 20\text{ ns} = 60\text{ ns}$$

**ขั้นตอนที่ 2: คำนวณ Round-Trip Latency ของแบบที่ 2 (Closed-Loop Handshake):**
ลำดับเวลาการเดินทางไป-กลับ:
1. ขาไป (REQ จาก A ไป B): ผ่าน 2-FF ในโดเมน B $= 2 \times T_B = 2 \times 20\text{ ns} = 40\text{ ns}$
2. การตอบสนองในโดเมน B (สร้าง ACK): ใช้เวลา $1\text{ ไซเคิลของ } B = 1 \times 20\text{ ns} = 20\text{ ns}$
3. ขากลับ (ACK จาก B กลับมา A): ผ่าน 2-FF ในโดเมน A $= 2 \times T_A = 2 \times 10\text{ ns} = 20\text{ ns}$
4. การปลดสถานะในโดเมน A (Clear REQ & BUSY): ใช้เวลา $1-2\text{ ไซเคิลของ } A \approx 10-20\text{ ns}$

ผลรวม Round-Trip ทั้งหมด:
$$L_{round\_trip} \approx 40\text{ ns} + 20\text{ ns} + 20\text{ ns} + 20\text{ ns} = 100\text{ ns}$$

การใช้ Closed-Loop Handshake ต้องแลกด้วยการติดสถานะ BUSY นานถึง **$100\text{ ns}$** ในขณะที่ Open-Loop Toggle ส่งข้อมูลถึงปลายทางได้ในเวลาเพียง **$60\text{ ns}$**!

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ข. ถูกต้องสมบูรณ์แบบ:** Forward Latency $60\text{ ns}$ และ Round-Trip Latency $100\text{ ns}$ สอดคล้องกับพฤติกรรมวงจรจริง $100\%$
* **ข้อ ก. ไม่ถูกต้อง:** คิดจำนวนสเตจของ Edge Detector ต่ำไป
* **ข้อ ค. ไม่ถูกต้อง:** ไม่ได้คิดสเตจตรวจจับขอบ
* **ข้อ ง. ไม่ถูกต้อง:** เวลา Round-Trip สูงเกินจริง

**คำตอบที่ถูกต้อง:** **ข้อ ข.**
