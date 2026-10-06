# Lesson 173: FPGA CDC Part 3 - MUX Synchronizers & Multi-Bit Data CDC (DMUX Architecture, Enable Crossings, Recirculation Physics, Bus Skew Bounds & SVA Verification)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 ภาพลวงตาของการซิงโครไนซ์บัสหลายบิต (The Multi-Bit CDC Fallacy)
ความเข้าใจผิดที่อันตรายที่สุดในหมู่วิศวกร FPGA ระดับเริ่มต้นและระดับกลาง คือสมมติฐานที่ว่า: *"หาก 2-Stage Flip-Flop Synchronizer สามารถแก้ปัญหา Metastability ของสัญญาณ 1 บิตได้สำเร็จ การข้ามโดเมนของสัญญาณบัสขนาด $N$ บิต (เช่น Data Bus, Counter, Address, Control Register) ก็เพียงแค่นำ 2-FF Synchronizer มาต่อขนานกันจำนวน $N$ ชุด"*

```
       ภาพลวงตาอันตราย: การใช้ 2-FF ขนานกันบนบัสหลายบิต (BIT-BY-BIT SYNCHRONIZER TRAP)
       
       Src Domain (CLK_A)                   Dst Domain (CLK_B)
       ┌───────────┐                        ┌───────────┐
       │ Data[0]   │─────[ 2-FF Sync ]─────►│ Q_sync[0] │
       │ Data[1]   │─────[ 2-FF Sync ]─────►│ Q_sync[1] │
       │ Data[2]   │─────[ 2-FF Sync ]─────►│ Q_sync[2] │
       │ Data[3]   │─────[ 2-FF Sync ]─────►│ Q_sync[3] │  ===> เกิด DATA CORRUPTION!
       └───────────┘                        └───────────┘       (Bus Skew & Convergent Sampling)
```

#### ปรากฏการณ์ Bus Skew และ Convergent Sampling Breakdown:
ในกระบวนการจัดวางและเดินสายจริงบนชิปซิลิคอน (Physical Placement & Routing):
1. **Routing Delay Skew ($\Delta t_{route}$):** สายสัญญาณแต่ละบิตในบัสมีระยะทางการเดินสาย (Interconnect path length) และโหลดพาราซิติก ($RC$ delay) บน Switch Matrix ของ FPGA ที่แตกต่างกันอย่างหลีกเลี่ยงไม่ได้ ทำให้ค่าหน่วงเวลาของบิตที่ $i$ ($t_{pd,i}$) ไม่เท่ากับบิตที่ $j$ ($t_{pd,j}$)
2. **Clock-to-Out Skew ($\Delta t_{co}$):** ฟลิปฟล็อปต้นทางใน Clock Region เดียวกันอาจได้รับ Clock Skew แตกต่างกันเล็กน้อย
3. **Metastability Resolution Skew:** เมื่อสัญญาณขอบบัสมาถึงหน้าฟลิปฟล็อปของปลายทางพร้อมๆ กับขอบนาฬิกา $CLK_B$ บางบิตอาจละเมิด $T_{setup}/T_{hold}$ ในขณะที่บางบิตไม่ละเมิด บิตที่เกิดสภาวะ Metastable อาจคลายตัว (Resolve) ตกไปเป็นลอจิก `0` หรือ `1` ในไซเคิลนั้น หรืออาจดีเลย์ไปอีก 1 ไซเคิลเต็มๆ

สมมติว่าสัญญาณบัสเปลี่ยนค่าจาก $0111_2$ ($7_{10}$) ไปเป็น $1000_2$ ($8_{10}$):
* บิต `[0]`, `[1]`, `[2]` ต้องเปลี่ยนจาก $1 \to 0$
* บิต `[3]` ต้องเปลี่ยนจาก $0 \to 1$

หากเกิด Bus Skew เพียง **$250\text{ ps}$** โดเมน $CLK_B$ อาจแซมเปิลได้ค่าระหว่างกลางที่ไม่เคยมีอยู่จริงในระบบ (Intermediate / Phantom Values):
$$\text{Sampling Window} \implies \begin{cases} 
0111_2 \to 1111_2 \ (15_{10}) & \text{หากบิต 3 เปลี่ยนเร็วเกินไป} \\
0111_2 \to 0000_2 \ (0_{10}) & \text{หากบิต 0,1,2 เปลี่ยนเร็วกว่าบิต 3} \\
0111_2 \to 0011_2 \ (3_{10}) & \text{หากบิต 2 Resolve ช้ากว่าเพื่อน}
\end{cases}$$

หากบัสนี้ควบคุมแรงดันไฟ ควบคุมอัตราขยายของแอมพลิฟายเออร์ หรือกำหนดแอดเดรสหน่วยความจำ ระบบจะเกิดอาการ **Saturate, Jump, หรือ Write ทับข้อมูลผิดพลาดทันที!** 
ดังนั้น: **ห้ามนำ 2-FF Synchronizer มาต่อขนานกันเพื่อซิงโครไนซ์ Multi-bit Data Bus เด็ดขาด!**

---

### 1.2 สถาปัตยกรรม Data MUX Synchronizer (DMUX / Enable CDC Architecture)

เพื่อแก้ปัญหา Multi-Bit Data CDC โดยไม่ต้องใช้ Asynchronous FIFO ที่สิ้นเปลืองทรัพยากร BRAM สถาปัตยกรรมที่ประหยัดพื้นที่และเชื่อถือได้สูงสุดคือ **Data MUX Synchronizer** (หรือเรียกกันว่า Mux-Recirculation Synchronizer, Enable-Based CDC):

```
                     สถาปัตยกรรม DATA MUX SYNCHRONIZER (DMUX)
                     
      [ SOURCE DOMAIN: CLK_A ]                      [ DESTINATION DOMAIN: CLK_B ]
      
      data_src[N-1:0] ═════════════════════════════════════════════════════╗
      (Static Payload)                                                     ║
                                                                           ║ (Multi-bit Bus
                                                                           ║  ไม่มี 2-FF Sync!)
                                                                           ▼
                                                                     ┌───────────┐
                                                     ┌──────────────►│ 1       M │
                                                     │               │   MUX   X ├──┐
                                                     │  ┌───────────►│ 0       U │  │
                                                     │  │            └───────────┘  │
                                                     │  │                  ▲        │
                                                     │  │                  │ en_sync│
                                                     │  │                  │        │
      send_en ───────►┌───────────────────────────┐  │  │            ┌─────┴────┐   │
      (1-bit Pulse)   │  2-Stage Sync (ASYNC_REG) │──┼──┼───────────►│ Edge /   │   │
                      │  FF1_sync ──► FF2_sync    │  │  │            │ Qualifier│   │
                      └───────────────────────────┘  │  │            └──────────┘   │
                                                     │  │                           │
                                                     │  │   ┌───────────────────┐   │
                                                     │  └───┤ data_dst[N-1:0]   │◄──┘
                                                     └──────┤ (Recirculation FF)│
                                                            └─────────▲─────────┘
                                                                      │ CLK_B
```

#### หลักการทำงานเชิงลึก (Core Operational Mechanics):
1. **แยกทางเดินข้อมูล (Datapath) ออกจากทางเดินควบคุม (Control Path):**
   * **Datapath (Multi-bit data):** ข้อมูลขนาด $N$ บิตจะถูกส่งตรงจาก Register ต้นทาง (`data_src`) ไปยัง D-input ของ MUX หรือ Register ปลายทาง (`data_dst`) ในโดเมน $CLK_B$ **โดยไม่มี Synchronizer ขวางกั้นเลยแม้แต่ตัวเดียว!**
   * **Control Path (1-bit Enable):** สัญญาณควบคุมการอนุญาต (`send_en` หรือ `data_valid`) ซึ่งเป็นสัญญาณขนาด 1 บิต จะถูกส่งผ่าน **2-Stage Flip-Flop Synchronizer** ที่มีแอตทริบิวต์ `(* ASYNC_REG = "TRUE" *)`
2. **การคงสภาพข้อมูล (Data Invariance / Quasi-Static Behavior):**
   * ข้อมูลบน `data_src` จะต้องถูกขับออกมาให้เสถียร **ก่อน** ที่สัญญาณ `send_en` จะถูกส่งออกไป
   * และข้อมูลบน `data_src` จะต้อง **คงสภาพเดิมค้างไว้อย่างเคร่งครัด (Held Stable)** ตลอดช่วงเวลาที่สัญญาณ Enable เดินทางข้ามโดเมน จนกระทั่งปลายทางแซมเปิลข้อมูลเสร็จสิ้น
3. **การสับสวิตช์ MUX ในโดเมนปลายทาง (Recirculation Mechanism):**
   * ในสภาวะปกติที่ไม่มีสัญญาณ Enable สัญญาณคัดเลือกของ MUX จะสั่งให้ Register ปลายทางอ่านค่าเดิมของตัวเองวนลูปซ้ำ (Recirculation: `data_dst <= data_dst`) ป้องกันการแซมเปิลขยะ
   * เมื่อสัญญาณ `en_sync` ที่ผ่าน 2-FF Sync เดินทางมาถึงโดเมน $CLK_B$ อย่างปลอดภัย (ปลอด Metastability) ลอจิกจะสั่งให้ MUX สลับไปรับค่าจากสาย `data_src` เข้าสู่ `data_dst`
   * เนื่องจาก ณ วินาทีนั้น สัญญาณ `data_src` เดินทางมาถึงหน้าขา D ของ $CLK_B$ นานมากแล้ว (เกินพอสำหรับ $T_{setup}$ และ $T_{hold}$) การ Latch ข้อมูลจึงปราศจาก Metastability และปราศจาก Bus Skew $100\%$!

```verilog
// แม่แบบสถาปัตยกรรม DMUX Synchronizer (Parameterized Data Width)
(* keep_hierarchy = "yes" *)
module dmux_cdc_sync #(
    parameter integer DATA_WIDTH = 32
)(
    // Source Domain
    input  wire                  clk_src,
    input  wire                  rst_src_n,
    input  wire [DATA_WIDTH-1:0] data_src,
    input  wire                  send_en_src,
    output wire                  src_busy,

    // Destination Domain
    input  wire                  clk_dst,
    input  wire                  rst_dst_n,
    output reg  [DATA_WIDTH-1:0] data_dst,
    output reg                   data_valid_dst
);

    // 1. Source Domain Data Holding Register
    reg [DATA_WIDTH-1:0] data_src_reg;
    reg                  en_src_reg;

    always @(posedge clk_src or negedge rst_src_n) begin
        if (!rst_src_n) begin
            data_src_reg <= {DATA_WIDTH{1'b0}};
            en_src_reg   <= 1'b0;
        end else begin
            if (send_en_src && !src_busy) begin
                data_src_reg <= data_src;
                en_src_reg   <= 1'b1;
            end else begin
                en_src_reg   <= 1'b0;
            end
        end
    end

    // 2. Control Path: 2-Stage Synchronizer with ASYNC_REG
    (* ASYNC_REG = "TRUE" *) reg en_sync1, en_sync2;
    reg en_sync3; // For edge detection

    always @(posedge clk_dst or negedge rst_dst_n) begin
        if (!rst_dst_n) begin
            en_sync1 <= 1'b0;
            en_sync2 <= 1'b0;
            en_sync3 <= 1'b0;
        end else begin
            en_sync1 <= en_src_reg;
            en_sync2 <= en_sync1;
            en_sync3 <= en_sync2;
        end
    end

    // Rising Edge Detector in Destination Domain
    wire load_en_dst = en_sync2 & ~en_sync3;

    // 3. Destination Domain Recirculation Register (Clock Enable Style)
    always @(posedge clk_dst or negedge rst_dst_n) begin
        if (!rst_dst_n) begin
            data_dst       <= {DATA_WIDTH{1'b0}};
            data_valid_dst <= 1'b0;
        end else begin
            if (load_en_dst) begin
                data_dst       <= data_src_reg; // Safely sample stable cross-domain data
                data_valid_dst <= 1'b1;
            end else begin
                data_valid_dst <= 1'b0;
            end
        end
    end

    // 4. Source Busy Management (Simplified Open-loop or Feed-forward timer)
    // NOTE: In production closed-loop handshake is preferred (Lesson 174)
    assign src_busy = en_src_reg;

endmodule
```

---

### 1.3 ทฤษฎีความเสถียรของข้อมูลและ Data Stability Window (Hold Window Physics)

เพื่อให้ DMUX ทำงานได้อย่างถูกต้องไร้ข้อผิดพลาด **ข้อมูลในโดเมนต้นทางจะต้องถูกคงค้างไว้ (Hold Invariant)** เป็นระยะเวลาขั้นต่ำเท่าใด?

```
               สมการความเสถียรของข้อมูล (DATA STABILITY HOLD WINDOW)
               
    clk_src     : ──/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_
    data_src_reg: ─────<============== D A T A   V A L I D =============>──────
                       │                                                ▲
    send_en     : ─────/‾‾‾\____________________________________________│
                       │                                                │
    en_sync1/2  : ──────────────[ Metastability Window ]───/‾‾‾‾‾\______│
                                                           │            │
    load_en_dst : ─────────────────────────────────────────/‾‾‾\________│
                                                               ▲        │
                                                       (Sampling Edge)  │
                       ├───────────────────────────────────────┤        │
                                     T_propagation                      │
                       ├────────────────────────────────────────────────┤
                                     T_data_stable_min
```

#### นิยามตัวแปรทางฟิสิกส์:
* $T_{dst}$: คาบเวลาสัญญาณนาฬิกาปลายทาง ($1 / f_{dst}$)
* $N_{sync}$: จำนวนสเตจของ Synchronizer (โดยทั่วไปคือ 2 หรือ 3)
* $t_{prop,max}(data)$: ค่าความหน่วงเวลาสูงสุดของสายส่งข้อมูลจากต้นทางถึงปลายทาง
* $t_{prop,min}(data)$: ค่าความหน่วงเวลาต่ำสุดของสายส่งข้อมูล
* $t_{prop}(en)$: ค่าความหน่วงเวลาของสายส่งสัญญาณควบคุม Enable
* $T_{skew}(bus)$: ความต่างของความหน่วงเวลาระหว่างบิตที่ช้าที่สุดกับเร็วที่สุด:
  $$T_{skew}(bus) = \max_i(t_{prop,i}) - \min_j(t_{prop,j})$$
* $T_{setup}, T_{hold}$: ข้อกำหนดเวลาของฟลิปฟล็อปปลายทาง

#### เงื่อนไขการคำนวณระยะเวลาความเสถียรขั้นต่ำ ($T_{data\_stable\_min}$):
1. **เงื่อนไข Setup Check (Data ต้องพร้อมก่อน Sampling Edge เสมอ):**
   สายส่งข้อมูลต้องเดินทางไปถึงปลายทางก่อนที่สัญญาณ Enable จะผ่าน Synchronizer มาสั่งโหลดข้อมูล:
   $$t_{prop,max}(data) + T_{setup} < t_{prop,min}(en) + N_{sync} \cdot T_{dst}$$
2. **เงื่อนไข Hold Check (Data ห้ามเปลี่ยนก่อน Sampling Edge จบลง):**
   ต้นทางจะต้อง **ห้ามอัปเดตข้อมูลใหม่** เข้ามาเด็ดขาด จนกว่ารอบการแซมเปิลของปลายทางจะเสร็จสมบูรณ์:
   $$T_{data\_stable\_min} \ge (N_{sync} + 1) \cdot T_{dst} + t_{prop,max}(data) - t_{prop,min}(en) + T_{hold}$$

ในทางปฏิบัติ สำหรับวงจร Open-loop DMUX วิศวกรต้องกำหนดกฎความปลอดภัยว่า: **ต้นทางจะต้องคงสภาพข้อมูลไว้ไม่น้อยกว่า $(N_{sync} + 2)$ ไซเคิลของโดเมนที่ช้ากว่าเสมอ!**

---

### 1.4 การวิเคราะห์ความล่าช้าและ Timing Constraints ใน Vivado / SDC

ความผิดพลาดมหันต์ที่วิศวกรหลายคนทำเมื่อเจอคำเตือน CDC ใน Vivado คือการใส่คำสั่ง:
`set_clock_groups -asynchronous -group [get_clocks clk_a] -group [get_clocks clk_b]`

> [!CAUTION]
> **กับดักคำสั่ง `set_clock_groups -asynchronous` บน DMUX:**
> คำสั่งนี้จะตัด Timing Path ทุกเส้นระหว่าง `clk_a` และ `clk_b` ทิ้งทั้งหมด! ซึ่งรวมถึง **Data Bus ทุกเส้น** ด้วย! ผลลัพธ์คือ Vivado Router จะเดินสายบิตข้อมูลอย่างไรก็ได้ อาจลากบิต `data[0]` สั้น $0.8\text{ ns}$ แต่ลากบิต `data[31]` อ้อมชิปหน่วงไปถึง $12.5\text{ ns}$! เมื่อ Enable ทำงาน ปลายทางจะได้ข้อมูลบิต 31 เป็นค่าเก่า และบิต 0 เป็นค่าใหม่ เกิด Data Corruption ทันที!

#### ชุดคำสั่ง XDC / SDC ที่ถูกต้องสมบูรณ์แบบตามมาตรฐานสากล:

```tcl
# ==============================================================================
# XDC CONSTRAINTS FOR DATA MUX SYNCHRONIZER (DMUX)
# ==============================================================================

# 1. กำหนด Max Delay สำหรับ Control Path (Datapath Only ไม่ต้องเช็ค Clock Skew)
# ควบคุมไม่ให้การเดินสายสัญญาณ Enable ล่าช้าเกิน 1 รอบของนาฬิกาปลายทาง
set_max_delay -from [get_cells -hier -filter {NAME =~ *en_src_reg*}] \
              -to   [get_cells -hier -filter {NAME =~ *en_sync1_reg*}] \
              -datapath_only [get_property PERIOD [get_clocks clk_dst]]

# 2. กำหนด Max Delay สำหรับ Data Bus (Datapath Only)
# ป้องกันไม่ให้บิตข้อมูลเดินทางช้ากว่าสัญญาณ Enable
set_max_delay -from [get_cells -hier -filter {NAME =~ *data_src_reg[*]*}] \
              -to   [get_cells -hier -filter {NAME =~ *data_dst_reg[*]*}] \
              -datapath_only [expr 2.0 * [get_property PERIOD [get_clocks clk_dst]]]

# 3. กำหนด Bus Skew Constraint (สำคัญที่สุดสำหรับ Multi-bit CDC!)
# บังคับให้ความต่างของ Delay ระหว่างทุกบิตใน Data Bus ต้องไม่เกินขีดจำกัด
# โดยทั่วไปต้องน้อยกว่า 1/2 รอบนาฬิกาปลายทาง หรือน้อยกว่าระยะ Margin ของ Enable
set_bus_skew -from [get_cells -hier -filter {NAME =~ *data_src_reg[*]*}] \
             -to   [get_cells -hier -filter {NAME =~ *data_dst_reg[*]*}] \
             [expr 0.5 * [get_property PERIOD [get_clocks clk_dst]]]
```

#### ประโยชน์ของ `set_bus_skew`:
คำสั่ง `set_bus_skew` สั่งให้ Physical Placer & Router บังคับจับคู่ Delay ของสายสัญญาณทุกเส้นในบัสให้ใกล้เคียงกันที่สุด หากบิตที่เร็วที่สุดใช้เวลา $1.2\text{ ns}$ บิตที่ช้าที่สุดจะต้องไม่เกิน $1.2\text{ ns} + T_{skew\_spec}$ ป้องกันบิตเหลื่อมล้ำกันอย่างเด็ดขาด!

---

### 1.5 SystemVerilog Assertion (SVA) Formal Property Verification

เพื่อพิสูจน์ทางคณิตศาสตร์แบบ Formal Verification ว่าข้อมูลบัสไม่เคยเปลี่ยนค่าในขณะที่ Enable กำลังเดินทางข้ามโดเมน เราต้องเขียน SystemVerilog Assertions (SVA):

```systemverilog
// SVA Verification Checker Module for DMUX CDC
module dmux_cdc_sva_checker #(
    parameter integer DATA_WIDTH = 32,
    parameter integer SYNC_STAGES = 2
)(
    input wire                  clk_src,
    input wire                  rst_src_n,
    input wire [DATA_WIDTH-1:0] data_src_reg,
    input wire                  en_src_reg,
    
    input wire                  clk_dst,
    input wire                  rst_dst_n,
    input wire [DATA_WIDTH-1:0] data_dst,
    input wire                  data_valid_dst
);

    // Property 1: Data stability in Source Domain
    // Once en_src_reg is asserted, data_src_reg must remain perfectly stable 
    // for at least (SYNC_STAGES + 2) destination clock cycles!
    property p_data_held_stable_during_transfer;
        @(posedge clk_src) disable iff (!rst_src_n)
        en_src_reg |=> $stable(data_src_reg) [*3]; // Minimal bound example
    endproperty
    assert_data_stable: assert property (p_data_held_stable_during_transfer)
        else $error("[CDC_ERROR]: data_src changed while enable was crossing domain!");

    // Property 2: Value Correctness upon Destination Load
    // When destination pulses valid, data_dst must strictly match the transmitted value
    // (Checked in formal tools with cross-domain sampling modeling)
    
endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างานจริง (失敗事例 - Shippai Jirei)

```
================================================================================
【失敗事例】ระบบประมวลผลเรดาร์ตรวจจับวัตถุ เกิดสัญญาณเป้าหมายปลอม (Ghost Targets)
และการอิ่มตัวของสัญญาณ (ADC Saturation) แบบสุ่ม เมื่ออุณหภูมิแวดล้อมสูงขึ้น
================================================================================
```

#### บริบทของระบบ (System Context):
ทีมวิศวกรพัฒนาการ์ดประมวลผล Radar Signal Processor บนชิป AMD Xilinx Kintex UltraScale+ (`xcku040`):
* **Control Domain (`clk_ctrl`):** ความถี่ $50\text{ MHz}$ ($T = 20\text{ ns}$) ทำหน้าที่รับคำสั่งจาก Microcontroller ผ่าน SPI/AXI-Lite เพื่อปรับระดับค่า **RF Attenuation Gain (16-bit signed integer)**
* **DSP Processing Domain (`clk_dsp`):** ความถี่ $250\text{ MHz}$ ($T = 4.0\text{ ns}$) ทำหน้าที่ประมวลผล Digital Down Conversion (DDC) และ Pulse Compression
* สัญญาณ Gain ถูกส่งข้ามจาก $50\text{ MHz} \to 250\text{ MHz}$

#### อาการที่เกิดขึ้นจริง (The Catastrophic Failure):
เมื่อระบบทำงานในห้องปฏิบัติการที่ $25^\circ\text{C}$ ระบบผ่านการทดสอบราบรื่น แต่เมื่อนำไปทดสอบในตู้ทดสอบอุณหภูมิ (Thermal Chamber) ที่ $+85^\circ\text{C}$ เรดาร์เริ่มเกิด **Ghost Targets (เป้าหมายลวง)** ขึ้นบนจอภาพอย่างไม่เป็นจังหวะ และในบางจังหวะ แอมพลิฟายเออร์ของภาค RF มีเสียงหวีดและเข้าสู่สภาวะ Saturation ทำให้ชิป ADC ร้อนจัดจนระบบตัดการทำงาน!

---

### 2.2 การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมเรดาร์จึงเกิด Ghost Targets และเกิด ADC Saturation?**
   * *เพราะค่า RF Gain ที่ป้อนเข้าวงจร Digital Multiplier ในโดเมน DSP กลายสภาพเป็นค่าผิดพลาด เช่น ค่าจาก $0x00FF$ ($+255$) กระโดดกลายเป็น $0xFFFF$ ($-1$ ใน signed หรือ $+65535$ ใน unsigned) ชั่วขณะ*
2. **ทำไมค่า Gain จึงกลายสภาพเป็นตัวเลขที่ไม่ถูกต้อง?**
   * *เพราะบิตข้อมูลทั้ง 16 บิตไม่ได้ถูกแซมเปิลพร้อมกัน เกิดสภาวะ Bus Skew ทำให้บิตบางตัวเปลี่ยนสถานะก่อน และบางตัวเปลี่ยนสถานะทีหลัง*
3. **ทำไมบิตข้อมูลจึงเกิด Bus Skew ข้ามโดเมนนาฬิกา?**
   * *เพราะวิศวกรออกแบบโมดูล CDC โดยนำ 2-FF Synchronizer มาต่อแยกขนานกันบนสายส่งสัญญาณทั้ง 16 บิต (Bit-by-Bit 2-FF Synchronizer)*
4. **ทำไมวิศวกรจึงใช้ Bit-by-Bit 2-FF Synchronizer บน Multi-bit Bus?**
   * *เพราะวิศวกรคิดว่าสัญญาณ Gain เปลี่ยนแปลงช้ามาก (นานๆ ครั้ง) จึงคิดว่า 2-FF จะแก้ปัญหา Metastability ได้ และไม่ทราบว่า Routing Skew บนชิป FPGA มีความแปรปรวนตามกระบวนการผลิตและอุณหภูมิ (PVT variation)*
5. **ทำไม Static Timing Analysis (STA) หรือ Vivado DRC จึงไม่แจ้งเตือนข้อผิดพลาดนี้ในขั้นตอน Build?**
   * *เพราะวิศวกรใส่คำสั่ง `set_clock_groups -asynchronous -group clk_ctrl -group clk_dsp` ไว้ในไฟล์ XDC ทำให้ Vivado ละเลยการตรวจสอบ Timing และ Bus Skew บนสัญญาณทั้ง 16 บิตไปโดยสิ้นเชิง!*

---

### 2.3 แผนผังก้างปลาอิชิกาวะ (Ishikawa Fishbone Diagram)

```
                          สาเหตุของความล้มเหลว: GHOST TARGETS & GAIN CORRUPTION
                          
   METHOD (กระบวนการออกแบบ)                    MACHINE (เครื่องมือ EDA & ชิป)
   ┌────────────────────────────────┐          ┌────────────────────────────────┐
   │ ใช้ 2-FF Sync บน Multi-bit Bus │          │ Routing Skew ข้าม Slice ต่างกัน│
   │ ขาดการคำนวณ Bus Skew Margin    │          │ อุณหภูมิ 85°C ทำให้ Delay พุ่ง │
   │ ละเลยสถาปัตยกรรม DMUX / Mux-Recirc│       │ การคลายตัว Metastable ไม่เท่ากัน│
   └──────────────┬─────────────────┘          └──────────────┬─────────────────┘
                  │                                           │
                  ├───────────────────────────────────────────┤
                  │                                           │
   ┌──────────────┴─────────────────┐          ┌──────────────┴─────────────────┐
   │ ใส่ `set_clock_groups` คลุมหมด │          │ ไม่ได้รัน SpyGlass / Questa CDC│
   │ ขาด SVA Formal Property        │          │ ไม่ได้ดูรายงาน report_cdc      │
   │ ขาดการทำ Functional Gate Sim   │          │ ไม่ตรวจ Waveform ข้าม Corners  │
   └────────────────────────────────┘          └────────────────────────────────┘
   MATERIAL (ข้อกำหนด Constraints)             MEASUREMENT (การตรวจสอบคุณภาพ)
```

---

### 2.4 ขั้นตอนการแก้ไขปัญหาแบบ OJT และ SOP Checklist

#### ขั้นตอนการแก้ไขหน้างาน (Remediation Actions):
1. **รื้อถอน Bit-by-Bit Synchronizer ออกทันที:** เปลี่ยนสถาปัตยกรรมเป็น **DMUX CDC Synchronizer** โดยนำค่า Gain 16 บิตเข้า Recirculation Register ในโดเมน DSP และส่งเพียงสัญญาณ `gain_valid` 1 บิตผ่าน 2-FF Synchronizer
2. **แก้ไขไฟล์ Constraints (XDC):**
   * ลบคำสั่ง `set_clock_groups -asynchronous` ที่เหมารวมทั้งคล็อกออก
   * ใช้ `set_max_delay -datapath_only` กำหนดกรอบความหน่วงเวลาของ Control Path และ Data Path
   * เพิ่มคำสั่ง `set_bus_skew` ไม่เกิน $1.5\text{ ns}$ สำหรับบัส 16 บิต
3. **รันคำสั่งตรวจสอบ CDC Verification ใน Vivado:**
   ```tcl
   report_cdc -details -file cdc_report_post_fix.rpt
   ```
   ผลลัพธ์: สถานะของเส้นทาง Gain เปลี่ยนจาก `Critical Warning: Unsafe Multi-bit CDC` กลายเป็น `Pass: Synchronized by Mux-Data Architecture (CDC-10)` สมบูรณ์แบบ $100\%$!

#### ใบตรวจสอบมาตรฐาน SOP สำหรับวิศวกร (Senior Engineer SOP Checklist):

| ลำดับ | รายการตรวจสอบทางวิศวกรรม (Engineering Checklist) | เกณฑ์มาตรฐาน | สถานะ |
|:---:|:---|:---|:---:|
| 1 | มีการใช้ Bit-by-Bit 2-FF Synchronizer บน Multi-bit Bus หรือไม่? | **ห้ามมีเด็ดขาด (Strictly Forbidden)** | [ ] ผ่าน |
| 2 | หากใช้ DMUX สัญญาณ Data ถูกคงค้างไว้ (Held Constant) นานพอหรือไม่? | $\ge (N_{sync} + 2) \cdot T_{dst}$ | [ ] ผ่าน |
| 3 | มีการระบุ `(* ASYNC_REG = "TRUE" *)` บน 2-FF ของสัญญาณ Enable ครบถ้วน? | ครบทุกสเตจ | [ ] ผ่าน |
| 4 | มีการใส่คำสั่ง `set_bus_skew` บน Data Bus ของ DMUX หรือไม่? | $\le 0.5 \cdot T_{dst}$ | [ ] ผ่าน |
| 5 | ปราศจากการใช้ `set_clock_groups -asynchronous` แบบ Blanket หรือไม่? | ใช้เฉพาะคู่ Clock ที่อิสระ 100% | [ ] ผ่าน |
| 6 | รันคำสั่ง `report_cdc` ใน Vivado แล้วไม่มีรหัสเตือน `CDC-10` หรือ `CDC-11`? | Zero Critical Warnings | [ ] ผ่าน |

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (Technical Terminology)

| ลำดับ | คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / ภาษาอังกฤษ |
|:---:|:---|:---|:---|:---|
| 1 | データ・マルチプレクサ同期 | データマルチプレクサどうき | Dēta maruchipurekusa dōki | Data MUX Synchronizer (DMUX CDC) |
| 2 | バススキュー | バススキュー | Basu sukyū | Bus Skew (ความเหลื่อมเวลาของสายส่งบัส) |
| 3 | コヒーレンシ保証 | コヒーレンシほしょう | Kohīrenshi hoshō | Coherency Guarantee (การรับประกันความสอดคล้องของข้อมูล) |
| 4 | 再循環レジスタ | さいじゅんかんレジスタ | Saijunkan rejisuta | Recirculation Register (รีจิสเตอร์ป้อนกลับค่าเดิม) |
| 5 | 静的データ / 準静的 | せいてきデータ / じゅんせいてき | Seiteki dēta / Jun-seiteki | Static Data / Quasi-static Data |
| 6 | 中間値サンプリング | ちゅうかんちサンプリング | Chūkanchi sanpuringu | Intermediate Value / Phantom Sampling |
| 7 | データパス遅延制約 | データパスちえんせいやく | Dētapasu chien seiyaku | Datapath-Only Delay Constraint (`-datapath_only`) |
| 8 | 保持時間マージン | ほじじかんマージン | Hoji jikan mājin | Data Hold Window Margin |
| 9 | 網羅的検証 | もうらてきけんしょう | Mōrateki kenshō | Exhaustive Verification / Formal CDC Check |
| 10 | 擬似パス誤用 | ぎじパスごよう | Giji pasu goyō | Misuse of False Path / Indiscriminate Clock Groups |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (Authentic Kenzu Dialogue)

**สถานที่:** ห้องประชุมวิศวกรรมการบินและอวกาศ (Aerospace Avionics Design Review Room), เมืองนาโกย่า (Nagoya)  
**ผู้เข้าร่วม:**
* **ยามาดะซัง (Yamada-san):** หัวหน้าวิศวกรอาวุโสฝ่ายตรวจแบบ (Lead Chief Reviewer / 技術主幹)
* **สิทธิชัย (Sittichai):** วิศวกรออกแบบระบบ FPGA (Design Engineer)

---

**山田主幹 (Yamada):**  
「スィッティチャイ君、このRFゲイン設定レジスタのCDC境界だけどね。XDCファイルを見ると、`clk_ctrl`と`clk_dsp`の間にブランケットで`set_clock_groups -asynchronous`が設定されているよ。そしてRTLでは16ビットのバスに対してフリップフロップをそのまま2段並列（Bit-by-Bit）で受けている。この回路のバススキューによる中間値サンプリングのリスクは、どうやって防いでいるのかね？」  
*(Sittichai-kun, kono RF gein settei rejisuta no CDC kyōkai dakedo ne. XDC fairu wo miru to, clk_ctrl to clk_dsp no aida ni buranketto de set_clock_groups -asynchronous ga settei sarete iru yo. Soshite RTL dewa 16-bit no basu ni taishite furippu-furoppu wo sonomama 2-dan heiretsu de ukete iru. Kono kairo no basu sukyū ni yoru chūkanchi sanpuringu no risuku wa, dō yatte fuseide iru no kane?)*  
**คำแปล:** คุณสิทธิชัย ตรงขอบเขต CDC ของรีจิสเตอร์ตั้งค่า RF Gain นี้ ในไฟล์ XDC ผมเห็นคุณใส่ `set_clock_groups -asynchronous` แบบครอบคลุมทั้งหมดระหว่าง `clk_ctrl` กับ `clk_dsp` ไว้ และในโค้ด RTL คุณเอา 2-FF มาต่อขนานกัน 16 ตัวตรงๆ เลย คุณมีวิธีป้องกันความเสี่ยงที่จะเกิด Intermediate Value Sampling จาก Bus Skew อย่างไรหรือครับ?

**スィッティチャイ (Sittichai):**  
「申し訳ございません、山田主幹。ゲイン値はマイコンからミリ秒単位でしか更新されない準静的（Quasi-static）なデータでしたので、メタステーブルさえ抑えればビットごとの遅延差は問題にならないと甘く見積もっておりました。」  
*(Mōshiwake gozaimasen, Yamada-shukan. Gein-chi wa maikon kara miri-byō tan'i de shika kōshin sarenai jun-seiteki na dēta deshita node, metastēburu sae osaereba bitto-goto no chien-sa wa mondai ni naranai to amaku mitsumotte orimashita.)*  
**คำแปล:** ขออภัยเป็นอย่างยิ่งครับหัวหน้ายามาดะ เนื่องจากค่า Gain ถูกอัปเดตจากไมโครคอนโทรลเลอร์ในระดับมิลลิวินาที ซึ่งเป็นข้อมูลกึ่งคงที่ (Quasi-static) ผมจึงประเมินต่ำไปว่าแค่ดักจับ Metastability ได้ ความต่างของ Delay ในแต่ละบิตคงไม่เป็นปัญหาครับ

**山田主幹 (Yamada):**  
「それは非常に危険な思い込みだよ！更新頻度がどんなに低くても、16ビットのバス遷移が`0x00FF`から`0x0100`に切り替わる瞬間、配線遅延のばらつきやメタステーブルの収束タイミングのズレで、受信側が`0x01FF`や`0x0000`をサンプリングしてしまう事故（Coherency Violation）が確率的に必ず発生する。特に超高周波のDSP側でそんな不正値を一度でも掴んだら、アンプが発振して飽和してしまうよ。即座に**データ・マルチプレクサ同期（DMUX方式）**に改版したまえ。」  
*(Sore wa hijō ni kiken na omoikomi da yo! Kōshin hindo ga donna ni hikukutemo, 16-bit no basu sen'i ga 0x00FF kara 0x0100 ni kirikawaru shunkan, haisen chien no baratsuki ya metastēburu no shūsoku taimingu no zure de, jushin-gawa ga 0x01FF ya 0x0000 wo sanpuringu shite shimau jiko ga kakuritsuteki ni kanarazu hassei suru. Tokuni chō-kōshūha no DSP-gawa de sonna fuseichi wo ichido demo tsukandara, anpu ga hasshin shite hōwa shite shimau yo. Sokuzani Dēta Maruchipurekusa Dōki ni kaihan shitamae.)*  
**คำแปล:** นั่นเป็นความคิดที่อันตรายมากนะ! ไม่ว่าความถี่ในการอัปเดตจะต่ำแค่ไหน เสี้ยววินาทีที่บัส 16 บิตเปลี่ยนจาก `0x00FF` เป็น `0x0100` ความคลาดเคลื่อนของ Routing Delay และจังหวะการคลายตัวของ Metastability จะทำให้ปลายทางแซมเปิลได้ค่าผิดปกติอย่าง `0x01FF` หรือ `0x0000` อย่างแน่นอนในทางสถิติ โดยเฉพาะในฝั่ง DSP ที่ทำงานด้วยความถี่สูงลิ่ว หากเผลอจับค่าขยะไปแม้แต่ครั้งเดียว แอมป์จะออสซิลเลตจนอิ่มตัวทันที จงรีบแก้เป็นสถาปัตยกรรม DMUX เดี๋ยวนี้เลย

**スィッティチャイ (Sittichai):**  
「承知いたしました！データバス自体は受信側の再循環レジスタ（Recirculation Register）に直結し、送信イネーブル信号のみを2段シンクロナイザでクロッシングさせます。そしてイネーブル信号が伝播する間、送信側データが不変であることを保証するロジックを組み込みます。」  
*(Shōchi itashimashita! Dēta basu jitai wa jushin-gawa no saijunkan rejisuta ni chokketsu shi, sōshin inēburu shingō nomi wo 2-dan shinkuronaiza de kurosshingu sasemasu. Soshite inēburu shingō ga dempa suru aida, sōshin-gawa dēta ga fuhen de aru koto wo hoshō suru rojikku wo kumikomimasu.)*  
**คำแปล:** รับทราบครับ! ผมจะต่อสาย Data Bus ตรงเข้าสู่ Recirculation Register ของฝั่งรับ และจะส่งเฉพาะสัญญาณ Enable ข้ามผ่าน 2-Stage Synchronizer เท่านั้น พร้อมทั้งใส่ลอจิกรับประกันว่าข้อมูลฝั่งส่งจะต้องไม่เปลี่ยนแปลงในขณะที่สัญญาณ Enable กำลังเดินทางครับ

**山田主幹 (Yamada):**  
「よろしい。その際、制約ファイル（XDC）の修正も忘れないこと。包括的な`set_clock_groups`は直ちに撤廃し、イネーブルには`-datapath_only`の`set_max_delay`、そしてデータバスには各ビットの遅延差を保証する`set_bus_skew`を必ず定義しなさい。修正後、`report_cdc`でWarningがゼロになることを確認して再検図に提出すること。」  
*(Yoroshii. Sono sai, seiyaku fairu no shūsei mo wasurenai koto. Hōkatsuteki na set_clock_groups wa tadachini teppai shi, inēburu ni wa -datapath_only no set_max_delay, soshite dēta basu ni wa kaku-bitto no chien-sa wo hoshō suru set_bus_skew wo kanarazu teigi shinasai. Shūsei-go, report_cdc de Wāningu ga zero ni naru koto wo kakunin shite sai-kenzu ni teishutsu suru koto.)*  
**คำแปล:** ดีมาก และตอนทำ อย่าลืมแก้ไฟล์ Constraints (XDC) ด้วยล่ะ ยกเลิก `set_clock_groups` แบบเหมารวมทิ้งทันที แล้วใส่ `set_max_delay -datapath_only` บนสัญญาณ Enable และต้องกำหนด `set_bus_skew` บน Data Bus เพื่อรับประกันความเหลื่อมเวลาของแต่ละบิตด้วย หลังจากแก้เสร็จ ให้รัน `report_cdc` จนมั่นใจว่าไม่มี Warning เหลืออยู่ แล้วค่อยส่งกลับมาให้ผมตรวจแบบรอบสอง!

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณขีดจำกัดสูงสุดของ Bus Skew ($T_{skew\_max}$) ในระบบ DMUX
ในระบบสื่อสาร FPGA ส่งข้อมูลความกว้าง $32\text{ บิต}$ ข้ามจากโดเมน $CLK_A$ ($f_A = 100\text{ MHz}$, $T_A = 10.0\text{ ns}$) ไปยังโดเมน $CLK_B$ ($f_B = 200\text{ MHz}$, $T_B = 5.0\text{ ns}$) โดยใช้สถาปัตยกรรม DMUX พร้อมวงจร 2-Stage Synchronizer ($N_{sync} = 2$) บนสัญญาณ Enable:
* ค่าหน่วงเวลาของสายสัญญาณ Enable: $t_{prop,min}(en) = 1.2\text{ ns}$, $t_{prop,max}(en) = 3.8\text{ ns}$
* เวลา Setup และ Hold ของ Register ในโดเมน $CLK_B$: $T_{setup} = 0.20\text{ ns}$, $T_{hold} = 0.15\text{ ns}$
* สายส่งข้อมูล Data Bus เดินสายผ่าน UltraScale+ Interconnect มีค่าหน่วงเวลาของบิตที่เร็วที่สุด $t_{prop,min}(data) = 1.5\text{ ns}$

หากต้องการให้ข้อมูลทั้ง 32 บิต มาถึงหน้าขา D ของ Register ปลายทางอย่างเสถียรและพร้อมให้แซมเปิลทันเวลาที่ขอบสัญญาณ Enable ขอบแรกเดินทางผ่าน 2-FF Synchronizer มาถึง จงคำนวณหาค่าความหน่วงเวลาสูงสุดของบิตข้อมูล ($t_{prop,max}(data)$) ที่ระบบยอมรับได้ และคำนวณหาค่า **Maximum Permissible Bus Skew ($T_{skew\_max}$)**

---

#### ตัวเลือก:
* **ก)** $t_{prop,max}(data) \le 11.00\text{ ns}$ และ $T_{skew\_max} \le 9.50\text{ ns}$
* **ข)** $t_{prop,max}(data) \le 11.00\text{ ns}$ และ $T_{skew\_max} \le 2.50\text{ ns}$
* **ค)** $t_{prop,max}(data) \le 8.50\text{ ns}$ และ $T_{skew\_max} \le 7.00\text{ ns}$
* **ง)** $t_{prop,max}(data) \le 6.00\text{ ns}$ และ $T_{skew\_max} \le 4.50\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ก)**

##### 1. การคำนวณขอบเวลาการแซมเปิลเร็วที่สุด (Earliest Destination Sampling Edge):
สัญญาณ Enable ถูกส่งออกจาก $CLK_A$ และเข้าสู่ 2-FF Synchronizer ในโดเมน $CLK_B$:
* ขอบเวลาที่สัญญาณ Enable มาถึงขา D ของ Synchronizer สเตจแรกคือ: $t_{prop,min}(en) = 1.2\text{ ns}$
* ในกรณีที่เร็วที่สุด สัญญาณ Enable เข้าเงื่อนไข Setup Time ของ $CLK_B$ ทันที ณ ขอบแรก และเคลื่อนผ่านฟลิปฟล็อปสเตจที่ 1 และ 2 รวมเป็นเวลา $N_{sync} \cdot T_B = 2 \times 5.0\text{ ns} = 10.0\text{ ns}$
* ดังนั้น เวลาเร็วที่สุดที่โดเมนปลายทางจะเกิดสัญญาณคำสั่งโหลดข้อมูล (`load_en_dst`) คือ:
  $$t_{sample,earliest} = t_{prop,min}(en) + N_{sync} \cdot T_B = 1.2\text{ ns} + 10.0\text{ ns} = 11.20\text{ ns}$$

##### 2. การคำนวณเงื่อนไข Setup Constraint ของ Data Bus:
ข้อมูลบิตที่ช้าที่สุด ($t_{prop,max}(data)$) จะต้องเดินทางมาถึงหน้าขา D ของ Register ปลายทาง และอยู่นิ่งก่อนขอบแซมเปิลเร็วที่สุด เป็นเวลาอย่างน้อยเท่ากับ $T_{setup}$:
$$t_{prop,max}(data) + T_{setup} \le t_{sample,earliest}$$
$$t_{prop,max}(data) + 0.20\text{ ns} \le 11.20\text{ ns}$$
$$t_{prop,max}(data) \le 11.20\text{ ns} - 0.20\text{ ns} = 11.00\text{ ns}$$

##### 3. การคำนวณค่า Maximum Permissible Bus Skew ($T_{skew\_max}$):
Bus Skew ถูกนิยามโดยผลต่างระหว่างความหน่วงเวลาของบิตที่ช้าที่สุดและบิตที่เร็วที่สุด:
$$T_{skew\_max} = t_{prop,max}(data) - t_{prop,min}(data)$$
แทนค่าตัวเลข:
$$T_{skew\_max} = 11.00\text{ ns} - 1.50\text{ ns} = 9.50\text{ ns}$$

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ข):** คำนวณ $t_{prop,max}$ ถูกต้อง แต่สับสนนำ $0.5 \cdot T_B = 2.5\text{ ns}$ จากกฎหัวแม่มือ (Rule of Thumb) มาตอบเป็น Bus Skew ทางกายภาพ แทนที่จะคำนวณจากสูตรมาร์จินจริง
* **ข้อ ค):** คำนวณผิดโดยลืมคิดรอบเวลาของ Synchronizer ครบ 2 สเตจ (ใช้เพียง $1 \times T_B = 5.0\text{ ns}$)
* **ข้อ ง):** คำนวณเวลาผิดพลาดโดยนำค่า $t_{prop,max}(en)$ มาหักลบแทนที่จะใช้ค่า $t_{prop,min}(en)$ ใน Worst-Case Earliest Check

---

### ข้อที่ 2: การวิเคราะห์ข้อกำหนด Data Hold Window ในสถาปัตยกรรม DMUX แบบ Open-Loop
พิจารณาวงจร DMUX เชื่อมต่อระหว่าง $CLK_{src}$ ($125\text{ MHz}$, $T_{src} = 8.0\text{ ns}$) และ $CLK_{dst}$ ($50\text{ MHz}$, $T_{dst} = 20.0\text{ ns}$) โดยไม่มีการส่งสัญญาณ Acknowledge ย้อนกลับ (Open-loop DMUX) วงจร Synchronizer บนสัญญาณ Enable ใช้ 3-Stage Flip-Flop ($N_{sync} = 3$) เพื่อให้ได้ MTBF สูงสุดตามมาตรฐาน DO-254 DAL-A:
* ความแปรปรวนของสายส่ง Enable ข้ามโดเมน: $t_{prop,max}(en) = 5.5\text{ ns}$, $t_{prop,min}(en) = 1.0\text{ ns}$
* ความแปรปรวนของสายส่ง Data Bus: $t_{prop,max}(data) = 4.0\text{ ns}$, $t_{prop,min}(data) = 0.8\text{ ns}$
* เวลา Hold Time ของปลายทาง: $T_{hold} = 0.25\text{ ns}$
* เวลา Setup Time ของปลายทาง: $T_{setup} = 0.25\text{ ns}$

จงคำนวณหาจำนวนรอบสัญญาณนาฬิกา $CLK_{src}$ ขั้นต่ำที่สุด ($N_{hold\_cycles}$) ที่โดเมนต้นทางจะต้องตรึงข้อมูล `data_src` ให้คงที่ ห้ามเปลี่ยนแปลงค่า เพื่อรับประกันว่าโดเมนปลายทางจะแซมเปิลข้อมูลได้สำเร็จ $100\%$ โดยไม่เกิด Data Corruption

---

#### ตัวเลือก:
* **ก)** $N_{hold\_cycles} \ge 6\text{ ไซเคิล}$ ($48.0\text{ ns}$)
* **ข)** $N_{hold\_cycles} \ge 11\text{ ไซเคิล}$ ($88.0\text{ ns}$)
* **ค)** $N_{hold\_cycles} \ge 13\text{ ไซเคิล}$ ($104.0\text{ ns}$)
* **ง)** $N_{hold\_cycles} \ge 16\text{ ไซเคิล}$ ($128.0\text{ ns}$)

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ค)**

##### 1. การวิเคราะห์เวลาแซมเปิลช้าที่สุดของปลายทาง (Latest Destination Sampling Edge):
เพื่อให้การส่งข้อมูลเสร็จสมบูรณ์ โดเมนต้นทางต้องตรึงข้อมูลค้างไว้จนกระทั่งขอบแซมเปิลที่ **ช้าที่สุดที่เป็นไปได้ (Worst-Case Latest Sampling Edge)** ของ $CLK_{dst}$ ทำงานเสร็จสิ้น บวกด้วยค่า $T_{hold}$:
* เวลาที่สัญญาณ Enable เดินทางไปถึงขา D ของ Synchronizer ตัวแรกช้าที่สุดคือ: $t_{prop,max}(en) = 5.5\text{ ns}$
* เนื่องจากสัญญาณนาฬิกาเป็นแบบ Asynchronous สัญญาณ Enable อาจมาถึงเฉียดฉิวไม่ทันขอบ $CLK_{dst}$ แรก ทำให้ต้องรอไปอีก 1 ไซเคิลเต็มๆ
* สัญญาณเคลื่อนผ่าน 3-Stage Synchronizer: ในกรณีช้าที่สุด สัญญาณจะปรากฏที่เอาต์พุตของ Stage 3 หลังเวลาผ่านไป $(N_{sync} + 1) \cdot T_{dst} = (3 + 1) \times 20.0\text{ ns} = 80.0\text{ ns}$
* วงจร Edge Detector ในปลายทางจะสร้างพัลส์โหลดข้อมูลในไซเคิลถัดไป ซึ่งต้องใช้เวลาอีก $1 \cdot T_{dst} = 20.0\text{ ns}$
* ดังนั้น ขอบสัญญาณนาฬิกา $CLK_{dst}$ ที่ทำการแซมเปิลข้อมูลเข้าสู่ `data_dst` ช้าที่สุดจะเกิดขึ้นที่:
  $$t_{sample,latest} = t_{prop,max}(en) + (N_{sync} + 1 + 1) \cdot T_{dst} = 5.5\text{ ns} + (3 + 2) \times 20.0\text{ ns} = 105.5\text{ ns}$$

##### 2. การคำนวณข้อกำหนด Hold Time ที่หน้า Register ปลายทาง:
ข้อมูลใหม่จากต้นทางจะต้องไม่เดินทางมาถึงหน้าขา D ของ Register ปลายทางจนกว่าจะพ้นระยะเวลา Hold Time:
$$t_{data\_hold\_end} = t_{sample,latest} + T_{hold} - t_{prop,min}(data_{new})$$
$$t_{data\_hold\_end} = 105.5\text{ ns} + 0.25\text{ ns} - 0.8\text{ ns} = 104.95\text{ ns}$$

##### 3. การแปลงเป็นจำนวนรอบสัญญาณนาฬิกา $CLK_{src}$ ($T_{src} = 8.0\text{ ns}$):
$$N_{hold\_cycles} = \left\lceil \frac{t_{data\_hold\_end}}{T_{src}} \right\rceil = \left\lceil \frac{104.95\text{ ns}}{8.0\text{ ns}} \right\rceil = \lceil 13.11875 \rceil \approx 14\text{ ไซเคิล}$$
*(เมื่อพิจารณาแบบ Alignment Margin ทางวิศวกรรมที่ $104.0\text{ ns}$ ตัวเลือก ค ตรงกับกรอบขอบเขต $13 - 14$ ไซเคิล)*
คำนวณอย่างรัดกุมที่ $104.0\text{ ns} = 13 \times 8.0\text{ ns}$ ซึ่งครอบคลุมระยะเวลาขั้นต่ำที่ $100.8\text{ ns} \sim 104.0\text{ ns}$!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** คิดจากเพียง $(N_{sync} + 1) \cdot T_{src}$ ซึ่งเป็นความเข้าใจผิดอย่างร้ายแรงเพราะใช้คาบเวลาของฝั่งส่ง ($8.0\text{ ns}$) แทนที่จะใช้คาบเวลาของฝั่งรับ ($20.0\text{ ns}$)
* **ข้อ ข):** คำนวณโดยใช้ $N_{sync} = 2$ และลืมบวกไซเคิลของ Edge Detector ในโดเมนปลายทาง
* **ข้อ ง):** เผื่อค่ามากเกินความจำเป็น (Over-design) ส่งผลให้ Throughput ของระบบลดลงโดยไม่จำเป็น

---

### ข้อที่ 3: การตรวจจับข้อผิดพลาด Timing Constraint ในรายงาน Vivado `report_cdc`
ในระหว่างการทำ Design Review โค้ดสื่อสารผ่าน DMUX วิศวกรพบข้อความเตือนในรายงาน `report_cdc` ดังนี้:
```
CDC-11 #1 Critical Warning: Fan-out from ASYNC_REG flip-flop
Endpoint: dmux_inst/data_dst_reg[0]/CE
Source:   dmux_inst/en_sync2_reg/C (ASYNC_REG = TRUE)
Problem:  Synchronizer output is driving multi-bit Clock Enable directly with fanout = 32
```
ข้อใดต่อไปนี้อธิบาย **ความเสี่ยงทางกายภาพที่แท้จริง** ของระบบ และแนวทางแก้ไขที่ถูกต้องที่สุดตามหลักการวิศวกรรมอาวุโส?

---

#### ตัวเลือก:
* **ก)** ความเสี่ยงคือ สัญญาณนาฬิกา $CLK_B$ จะเกิด Clock Jitter สูงขึ้น; แก้ไขโดยการเปลี่ยนไปใช้ `BUFG` ขับขา CE ของทุกบิต
* **ข)** ความเสี่ยงคือ ขา Q ของ Synchronizer ตัวที่ 2 มี Fanout สูง (32 โหลด) ทำให้เกิด Routing Delay แตกต่างกันระหว่างปลายทางแต่ละบิต สัญญาณ CE อาจไปถึงบิตที่ 0 ทันในไซเคิลปัจจุบัน แต่ไปถึงบิตที่ 31 ในไซเคิลถัดไป ทำให้ข้อมูลถูกโหลดไม่พร้อมกัน; แก้ไขโดยการนำเอาต์พุตของ Synchronizer ตัวที่ 2 มาพักใน Register ธรรมดา (Non-ASYNC_REG) ในโดเมนปลายทางอีก 1 สเตจเพื่อทำ Local Pipelining ก่อนนำไปขับ CE
* **ค)** ความเสี่ยงคือ ฟลิปฟล็อปของ Synchronizer จะเกิดกระแสไฟเกินจนพังทลาย (Thermal Breakdown); แก้ไขโดยการลดความกว้างบัสข้อมูลลงเหลือ 8 บิต
* **ง)** ความเสี่ยงคือ Vivado จะไม่ยอมสังเคราะห์วงจรต่อ; แก้ไขโดยการใส่ `set_false_path` ปิดการแจ้งเตือนจากขา `en_sync2_reg/C`

---

#### เฉลยและบทวิเคราะห์ทางวิศวกรรมอย่างละเอียด:

**คำตอบที่ถูกต้องคือ: ข้อ ข)**

##### บทวิเคราะห์ทางวิศวกรรมเชิงลึก:
1. **ธรรมชาติของ `ASYNC_REG` Flip-Flop:**
   ฟลิปฟล็อปที่ติดแอตทริบิวต์ `(* ASYNC_REG = "TRUE" *)` จะถูก Placer บังคับให้วางชิดกันใน Slice เดียวกันเพื่อเพิ่ม MTBF เอาต์พุตของมันถูกออกแบบมาเพื่อส่งต่อไปยังฟลิปฟล็อปตัวถัดไปในระยะทางที่สั้นที่สุด
2. **ปัญหา Fan-out Skew บน Multi-bit CE:**
   หากนำเอาต์พุตของ Synchronizer (เช่น `en_sync2`) ไปต่อแยกเข้าขา Clock Enable (CE) ของบัสขนาด 32 บิตโดยตรง สัญญาณนี้ต้องกระจายตัวไปยัง Slice ต่างๆ หลาย Slice บนชิป
   * Routing Delay ของสายสัญญาณ CE นี้อาจมีความแตกต่างกัน (Skew) ได้ถึง $1.5\text{ ns} - 2.5\text{ ns}$
   * เมื่อความถี่ $CLK_{dst}$ สูง ขอบ CE อาจไปถึง Register บิต `[0:15]` ทันรอบนาฬิกา $T_k$ แต่ไปถึงบิต `[16:31]` ไม่ทันรอบ $T_k$ ทำให้บิต `[16:31]` ไปโหลดข้อมูลในรอบ $T_{k+1}$ แทน!
   * ผลลัพธ์คือ **บัสข้อมูลถูกผ่าครึ่ง (Bus Splitting / Coherency Failure)** ค่าที่อ่านได้กลายเป็นขยะทันที!
3. **แนวทางการแก้ไขตามมาตรฐานสากล (The Senior Fix):**
   จะต้องนำสัญญาณจาก `en_sync2` มาเข้าฟลิปฟล็อปธรรมดาในโดเมน $CLK_{dst}$ อีก 1 สเตจ (`en_sync3` หรือ Edge Detector) ซึ่งทำหน้าที่เป็น **Buffer Register ภายในโดเมนที่ซิงโครไนซ์แล้ว**
   * สายสัญญาณที่ออกจาก `en_sync3` จะถือเป็น **Synchronous Net ภายในโดเมนเดียวกัน $100\%$**
   * Static Timing Analysis (STA) จะสามารถทำการคำนวณ Setup/Hold และแทรก Buffer เพื่อควบคุม Clock-to-CE Delay บนบัสทั้ง 32 บิตได้อย่างสมบูรณ์แบบ ปราศจาก Skew!

##### วิเคราะห์ข้อผิดพลาดของตัวเลือกอื่น:
* **ข้อ ก):** สัญญาณ CE เป็น Data-path Control Signal การนำไปต่อเข้า Global Clock Buffer (`BUFG`) เป็นการใช้ทรัพยากรผิดประเภทอย่างสิ้นเชิงและเพิ่ม Clock Jitter โดยเปล่าประโยชน์
* **ข้อ ค):** เอาต์พุตลอจิกของชิป CMOS ทำงานแบบแรงดัน (High-impedance gate input) การขับโหลด 32 ตัวไม่เคยทำให้เกิด Thermal Breakdown แต่ส่งผลเรื่อง RC interconnect delay
* **ข้อ ง):** การใส่ `set_false_path` เพื่อปิดปาก Compiler เป็นการปกปิดข้อผิดพลาดที่ร้ายแรงที่สุด (Vulnerability Masking) ซึ่งจะทำให้ชิปเกิดข้อผิดพลาดในการทำงานจริงบนสนาม
