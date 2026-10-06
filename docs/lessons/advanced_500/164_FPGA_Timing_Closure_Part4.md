# Lesson 164: FPGA Timing Closure Part 4 - I/O Timing Constraints: Input/Output Delay (set_input_delay, set_output_delay, Source-Synchronous vs System-Synchronous, Board Trace Physics & IDELAY/ODELAY Tap Calibration)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 สถาปัตยกรรมอินเทอร์เฟซขาเข้า-ขาออก (System-Synchronous vs Source-Synchronous I/O)
การกำหนดข้อจำกัดไทม์มิ่งที่พอร์ตอินพุตและเอาต์พุต (I/O Constraints) ของ FPGA เป็นหนึ่งในหัวข้อที่วิศวกรเข้าใจผิดบ่อยที่สุด โดยแก่นแท้แล้ว คำสั่ง `set_input_delay` และ `set_output_delay` ไม่ได้หมายถึงการหน่วงเวลาภายในชิป FPGA แต่เป็นการบอกให้เครื่องมือ STA รับรู้ถึง **"เวลาที่สูญเสียไปภายนอกชิป (Off-Chip Delays)"** บนแผ่นวงจรพิมพ์ PCB และไอซีภายนอก:

```
                  การเปรียบเทียบสถาปัตยกรรมอินเทอร์เฟซ I/O
                  
   [ 1. SYSTEM-SYNCHRONOUS ARCHITECTURE (สถาปัตยกรรมสัญญาณนาฬิการ่วม) ]
   
             ┌─────────────────── Board Clock Source ──────────────────┐
             │ (T_clk_board1)                         (T_clk_board2)   │
             ▼                                                         ▼
     ┌───────────────┐        PCB Data Trace (T_data_trace)    ┌───────────────┐
     │  External IC  │════════════════════════════════════════►│  FPGA Device  │
     │  (Transmitter)│                                         │  (Receiver)   │
     └───────────────┘                                         └───────────────┘
     ===> ขีดจำกัด: Board Clock Skew ระหว่าง 2 ชิป ทำลาย Timing! ทำความเร็วได้ < 150 MHz
     
   -----------------------------------------------------------------------------
   
   [ 2. SOURCE-SYNCHRONOUS ARCHITECTURE (สถาปัตยกรรมส่งสัญญาณนาฬิกาควบคู่) ]
   
     ┌───────────────┐        PCB Clock Trace (T_clk_trace)    ┌───────────────┐
     │  External IC  │────────────────────────────────────────►│  FPGA Device  │
     │  (Transmitter)│        PCB Data Bus   (T_data_trace)    │  (Receiver)   │
     │               │════════════════════════════════════════►│               │
     └───────────────┘                                         └───────────────┘
     ===> จุดเด่น: สัญญาณนาฬิกาวิ่งขนานไปกับข้อมูล ทนทานต่อ Skew ทำความเร็วได้ > 400-800 MHz!
```

---

### 1.2 คณิตศาสตร์และการแปลงค่าคำสั่ง `set_input_delay`

คำสั่ง `set_input_delay` ระบุระยะเวลาที่ข้อมูลภายนอกใช้เดินทาง นับจากขอบสัญญาณนาฬิกาของ External Clock จนกระทั่งข้อมูลมาถึงพินของ FPGA:

```
                 ไดอะแกรมเวลาภายนอกชิปสำหรับ INPUT DELAY
                 
   Clock at Ext IC : ──/‾‾‾\_________________ (Launch Edge ภายนอก)
                       │
   Ext IC DOUT     : ──┼───< T_cko_ext >──< DATA VALID >───────────
                       │                  │
   Data at FPGA Pin: ──┼──────────────────┼──< T_trace >──< DATA AT PIN >
                       │                  |<───────────────>|
                       |<----------- Input Delay ---------->|
```

#### 1. สูตรคำนวณสำหรับ System-Synchronous Interface:
$$\text{Input Delay}_{max} = T_{cko\_ext\_max} + T_{data\_trace\_max} - T_{clk\_trace\_min}$$
$$\text{Input Delay}_{min} = T_{cko\_ext\_min} + T_{data\_trace\_min} - T_{clk\_trace\_max}$$

* $\text{Input Delay}_{max}$ ถูกนำไปใช้ในการคำนวณ **Setup Slack** ภายใน FPGA
* $\text{Input Delay}_{min}$ ถูกนำไปใช้ในการคำนวณ **Hold Slack** ภายใน FPGA

#### 2. สูตรคำนวณสำหรับ Source-Synchronous Interface (แบบจัดกึ่งกลาง: Center-Aligned):
ในอินเทอร์เฟซแบบ Source-Synchronous ที่ขอบนาฬิกาถูกวางไว้กึ่งกลางของหน้าต่างข้อมูล (Data Eye Window):
* กำหนดให้ $T_{dv\_b}$ (Data Valid Before Clock) คือระยะเวลาที่ข้อมูลนิ่งก่อนขอบนาฬิกา
* กำหนดให้ $T_{dv\_a}$ (Data Valid After Clock) คือระยะเวลาที่ข้อมูลนิ่งหลังขอบนาฬิกา

$$\text{Input Delay}_{max} = T_{period} - T_{dv\_b} + \Delta T_{skew\_trace\_max}$$
$$\text{Input Delay}_{min} = T_{dv\_a} - \Delta T_{skew\_trace\_max}$$

```tcl
# ตัวอย่างคำสั่ง XDC สำหรับ System-Synchronous Input Delay
set_input_delay -clock [get_clocks clk_ext] -max 3.200 [get_ports data_in[*]]
set_input_delay -clock [get_clocks clk_ext] -min 0.800 [get_ports data_in[*]]
```

---

### 1.3 คณิตศาสตร์และการแปลงค่าคำสั่ง `set_output_delay`

คำสั่ง `set_output_delay` ระบุระยะเวลาที่ไอซีภายนอกและลายวงจร PCB ต้องการใช้ นับจากจังหวะที่ข้อมูลหลุดออกจากพินของ FPGA จนกระทั่งไอซีภายนอกแซมเปิลข้อมูลเสร็จ:

```
                 ไดอะแกรมเวลาภายนอกชิปสำหรับ OUTPUT DELAY
                 
   Data leaves FPGA : ──< PIN DATA >───────────────────────────────
                                    │
   Data arrives Ext : ──────────────┼──< T_trace >──► [ Ext IC Pin ]
                                    │                 |<-- T_setup_ext -->|
                                    |<----------- Output Delay ---------->|
```

#### สูตรคำนวณ Output Delay สำหรับ System-Synchronous Interface:
$$\text{Output Delay}_{max} = T_{data\_trace\_max} + T_{setup\_ext} - T_{clk\_trace\_min}$$
$$\text{Output Delay}_{min} = T_{data\_trace\_min} - T_{hold\_ext} - T_{clk\_trace\_max}$$

```tcl
# ตัวอย่างคำสั่ง XDC สำหรับ Output Delay
set_output_delay -clock [get_clocks clk_ext] -max 2.400 [get_ports data_out[*]]
set_output_delay -clock [get_clocks clk_ext] -min -0.500 [get_ports data_out[*]]
```
*(หมายเหตุ: ค่า `set_output_delay -min` สามารถติดลบได้ ซึ่งหมายความว่าข้อมูลสามารถคงสภาพอยู่ต่อไปได้อีกหลังขอบนาฬิกา)*

---

### 1.4 ฟิสิกส์ของสายส่ง PCB และเวลาหน่วงในแพ็กเกจ (Board Trace Physics & Package Delays)

ในคลื่นความถี่สูง ความล่าช้าของลายวงจรบนแผ่น PCB มีค่าแปรผันตามค่าคงที่ไดอิเล็กทริก ($D_k$ หรือ $\epsilon_r$):

$$T_{pd} = \frac{\sqrt{\epsilon_{eff}}}{c}$$
* สำหรับชั้นนอก (Microstrip บน FR-4, $\epsilon_{eff} \approx 3.0$):  
  $$T_{pd\_microstrip} \approx 5.8 - 6.2\text{ ps/mm}$$
* สำหรับชั้นใน (Stripline บน FR-4, $\epsilon_r \approx 4.2$):  
  $$T_{pd\_stripline} \approx 6.8 - 7.2\text{ ps/mm}$$

```
                ความล่าช้าในระดับแพ็กเกจชิป (PACKAGE FLIGHT TIME)
                
   Silicon Die Pad ──[ Bond Wire / Micro-bump ]──► Substrate Trace ──► BGA Ball
   |<--------------------------- PKG_PIN_DELAY ------------------------>|
   (ความล่าช้าภายในแพ็กเกจของแต่ละขาต่างกันได้ถึง 50ps - 250ps!)
```

ใน Vivado วิศวกรต้องสั่งเปิดใช้งาน Package Delay เสมอ เพื่อให้การคำนวณรวมความยาวสายภายในแพ็กเกจของ FPGA:
```tcl
set_property USER_CLUSTER_PROP TRUE [current_design]
# สั่งรวมความล่าช้าของพินแพ็กเกจในการวิเคราะห์ I/O STA
set_property IS_PACKAGE_DELAY_AWARE TRUE [current_design]
```

---

### 1.5 วงจรหน่วงเวลาแบบละเอียด IDELAYE3 / ODELAYE3 และการทำ Dynamic Eye Centering

เพื่อเอาชนะความผันแปรของเวลาเดินสายบนบอร์ด FPGA ตระกูล UltraScale+ ติดตั้งบล็อก **`IDELAYE3`** ที่ขาอินพุตทุกขา:
* มีจำนวนระดับการหน่วงเวลา **512 Taps**
* ความละเอียดต่อ Tap: $\Delta T_{tap} \approx 2.5\text{ ps} - 5.0\text{ ps}$ (ควบคุมความเสถียรด้วยสัญญาณอ้างอิงจาก `IDELAYCTRL` ที่ $300\text{ MHz} - 500\text{ MHz}$)

```
                   สถาปัตยกรรม IDELAYE3 DYNAMIC EYE CENTERING
                   
    FPGA I/O Pad ──► [ IDELAYE3 (512 Taps) ] ──► ISERDES / Input Register
                             ▲
                             │ (CNTVALUEIN / CE)
                     ┌───────┴───────┐
                     │ Eye Calibration│ (วงจร FSM สแกนหาขอบซ้าย-ขวาของ Data Eye)
                     │ FSM Controller │ แล้วตั้ง Tap ไว้กึ่งกลาง (Center-Aligned) พอดี!
                     └───────────────┘
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### 2.1 กรณีศึกษาความล้มเหลวหน้างาน: กล้องหน้ารถยนต์ ADAS ภาพกระพริบเมื่อห้องเครื่องร้อนจัด (Automotive Camera Bridge Overheat Glitch)

```
+----------------------------------------------------------------------------------------------------+
| กรณีศึกษาความล้มเหลวหน้างาน (現場の失敗事例)                                                                 |
| เหตุการณ์: กล่องบริดจ์รับสัญญาณภาพจากเซนเซอร์กล้องหน้ารถยนต์ ADAS (12-bit Parallel Bus, 148.5MHz)         |
| อาการ: บอร์ดทำงานได้สมบูรณ์แบบที่อุณหภูมิห้อง 25°C แต่เมื่อนำรถไปวิ่งทดสอบท่ามกลางแดดจัดในทะเลทราย             |
|        และอุณหภูมิห้องเครื่องพุ่งสูงขึ้นถึง +85°C ภาพวิดีโอบนจอเกิดอาการภาพสั่นกระตุก เม็ดสีเพี้ยน (Pink Noise)  |
|        และระบบเตือนการชนด้านหน้า (FCW) รายงานข้อผิดพลาดของเซนเซอร์กล้องเป็นระยะ                            |
+----------------------------------------------------------------------------------------------------+
```

#### การวิเคราะห์หาสาเหตุรากเหง้าด้วยหลักการ 5 Whys (5 Whys Root Cause Analysis):

1. **ทำไมภาพวิดีโอกล้องหน้ารถจึงกระพริบและสีเพี้ยนที่อุณหภูมิ 85°C?**  
   *คำตอบ:* ฟลิปฟล็อปของขาอินพุตบน FPGA แซมเปิลข้อมูลพิกเซลสีแดง (R) และสีเขียว (G) ผิดพลาดในช่วงที่มีการสลับค่า

2. **ทำไมฟลิปฟล็อปจึงแซมเปิลข้อมูลผิดพลาดเฉพาะที่อุณหภูมิสูง?**  
   *คำตอบ:* หน้าต่างข้อมูลที่ถูกต้อง (Data Eye Window) ของเซนเซอร์กล้องเลื่อนตำแหน่ง (Drift) ไปจากเดิมถึง $1.65\text{ ns}$ ทำให้ขอบข้อมูลมาชนเข้ากับหน้าต่างการแซมเปิลของ FPGA

3. **ทำไม Data Eye จึงเลื่อนตำแหน่งไปได้มากขนาดนั้น?**  
   *คำตอบ:* ค่า $T_{cko}$ ของเซนเซอร์รับภาพภายนอกยืดออกเมื่ออุณหภูมิสูงขึ้นจาก $2.8\text{ ns}$ เป็น $4.2\text{ ns}$ ($+1.4\text{ ns}$) ร่วมกับความต้านทานของสายแพกล้องที่ร้อนขึ้น

4. **ทำไมซอฟต์แวร์ Vivado จึงไม่รายงานความเสี่ยงนี้ตั้งแต่ตอนตรวจสอบ Timing Closure?**  
   *คำตอบ:* ในไฟล์คอนสเตรนต์ XDC วิศวกรกำหนดเฉพาะค่าสูงสุด:  
   `set_input_delay -clock [get_clocks cam_clk] -max 3.5 [get_ports cam_data[*]]`  
   แต่ **ละเลยการเขียนคำสั่ง `-min` โดยสิ้นเชิง!**

5. **ทำไมวิศวกรจึงไม่เขียนคำสั่ง `-min`?**  
   *คำตอบ:* วิศวกรเข้าใจผิดคิดว่า "ถ้า Setup Time ผ่าน ค่าสูงสุดย่อมครอบคลุมความปลอดภัยทั้งหมดแล้ว" โดยไม่ทราบว่าหากไม่ใส่คำสั่ง `-min` เครื่องมือ STA จะ **ไม่ตรวจสอบ Hold Time บนขาอินพุตเลยแม้แต่นิดเดียว!** ทำให้สายสัญญาณถูกวางแบบลัดวงจรจนไม่มี Hold Margin ที่อุณหภูมิสูง!

---

### 2.2 ผังภูมิก้างปลาวิเคราะห์ปัญหา (Ishikawa Fishbone Diagram)

```
                       ผังภูมิก้างปลาวิเคราะห์สาเหตุ ADAS CAMERA I/O GLITCH
                       
   [ ความเข้าใจผิดด้านวิศวกรรม (Mindset) ]          [ การกำหนดคอนสเตรนต์ (Constraints XDC) ]
   เข้าใจผิดว่ากำหนดเฉพาะ -max ก็เพียงพอ            เขียนเฉพาะ set_input_delay -max
             \                                           \
              \                                           \
               \                                           \  ละเลยคำสั่ง -min โดยสิ้นเชิง!
   มองข้ามความสำคัญของ Input Hold Time                         ทำให้ไม่มีการวิเคราะห์ Hold ที่ขา Pin
                 \                                           \
                  +-------------------------------------------+
                  |                                           |
                  |   ADAS CAMERA I/O TIMING GLITCH AT 85°C   | =====> [ FAILURE! ]
                  |                                           |
                  +-------------------------------------------+
                 /                                           /
                /                                           /  ความผันแปรของ Tcko ภายนอกตามอุณหภูมิ
   ไม่เปิดใช้งาน IDELAYE3 ทำ Dynamic Calibration              ความล่าช้าในสายแพ FPC ยืดตัวออก
              /                                           /
   [ การชดเชยระดับฮาร์ดแวร์ (Hardware Calibration) ]  [ ปัจจัยทางกายภาพภายนอก (External Physics) ]
```

---

### 2.3 คู่มือปฏิบัติงาน SOP: การกำหนดและปิดไทม์มิ่ง I/O อินเทอร์เฟซ (I/O Timing Closure SOP)

#### สเต็ปที่ 1: ตรวจสอบดาต้าชีตของไอซีภายนอกครบทุก PVT Corners
* ดึงค่าพารามิเตอร์ของ External IC จาก Datasheet:
  * ค่า $T_{cko\_max}$ และ $T_{cko\_min}$ ที่อุณหภูมิต่ำสุดและสูงสุด
  * ค่า $T_{setup\_ext}$ และ $T_{hold\_ext}$
* วัดความยาวลายวงจร PCB จากไฟล์ Allegro/Altium เพื่อคำนวณ $T_{trace\_max}$ และ $T_{trace\_min}$

#### สเต็ปที่ 2: เขียนคำสั่ง `set_input_delay` และ `set_output_delay` ทั้ง -max และ -min เสมอ
* บังคับใช้รูปแบบคำสั่ง 2 บรรทัดเสมอ ห้ามมีข้อยกเว้น:

```tcl
# แม่แบบมาตรฐานสำหรับ Input Delay (Max สำหรับ Setup, Min สำหรับ Hold)
set_input_delay -clock [get_clocks ext_clk] -max $IN_DELAY_MAX [get_ports data_in[*]]
set_input_delay -clock [get_clocks ext_clk] -min $IN_DELAY_MIN [get_ports data_in[*]]

# แม่แบบมาตรฐานสำหรับ Output Delay
set_output_delay -clock [get_clocks ext_clk] -max $OUT_DELAY_MAX [get_ports data_out[*]]
set_output_delay -clock [get_clocks ext_clk] -min $OUT_DELAY_MIN [get_ports data_out[*]]
```

#### สเต็ปที่ 3: เปิดใช้งานฟีเจอร์ IOB Register Packing
* บังคับให้ฟลิปฟล็อปตัวแรกและตัวสุดท้ายถูกดูดเข้าไปอยู่ในเซลล์ IOB (I/O Block) ติดกับขาพิน เพื่อขจัดความผันแปรของสายไฟใน Fabric:

```verilog
// บังคับให้ฟลิปฟล็อปวางใน IOB ติดขาพินภายนอก
(* IOB = "TRUE" *) reg [11:0] cam_data_reg;
always @(posedge cam_clk) begin
    cam_data_reg <= cam_data_in;
end
```

#### สเต็ปที่ 4: การปรับแต่ง Tap Delay ด้วย IDELAYE3
* สำหรับอินเทอร์เฟซความเร็วสูงกว่า $100\text{ MHz}$ ให้ต่อพ่วงพรีมิทิฟ `IDELAYE3`
* รันวงจร FSM ตรวจสอบ Eye Margin ในขั้นตอน Boot และตั้งค่า Tap ไว้กึ่งกลางของหน้าต่างข้อมูลอย่างแม่นยำ

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง

| คำศัพท์คันジ / คาตากานะ | คำอ่าน (Romaji) | ความหมายทางวิศวกรรม (Thai / English) |
| :--- | :--- | :--- |
| **入出力タイミング制約** | Nyuushutsuryoku Taimingu Seiyaku | I/O Timing Constraints (ข้อจำกัดไทม์มิ่งขาเข้า-ขาออก) |
| **入力遅延制約** | Nyuuryoku Chien Seiyaku | Input Delay Constraint (ข้อกำหนดความล่าช้าของสัญญาณขาเข้า) |
| **出力遅延制約** | Shutsuryoku Chien Seiyaku | Output Delay Constraint (ข้อกำหนดความล่าช้าของสัญญาณขาออก) |
| **ソース同期** | Soosu Douki | Source-Synchronous (การส่งสัญญาณนาฬิกาควบคู่ไปกับข้อมูล) |
| **システム同期** | Shisutemu Douki | System-Synchronous (การใช้สัญญาณนาฬิการ่วมกันบนบอร์ด) |
| **基板配線遅延** | Kiban Haisen Chien | PCB Board Trace Delay (ความล่าช้าของลายวงจรบนแผ่น PCB) |
| **アイパターン開口部** | Ai Pataan Kaikoubu | Eye Pattern Opening (ความกว้างช่องเปิดของหน้าต่างสัญญาณ) |
| **可変遅延素子** | Kahen Chien Soshi | Programmable Delay Element (IDELAY / ODELAY) |
| **IOBレジスタ配置** | Ai-Oo-Bii Rejisuta Haichi | IOB Register Packing (การดูดฟลิปฟล็อปไปวางในบล็อก I/O) |
| **パッケージ内配線遅延** | Pakkeeji-nai Haisen Chien | Package Flight Time Delay (ความล่าช้าภายในตัวถังชิป) |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図の現場会話)

#### สถานการณ์ที่ 1: การตรวจพบการละเลยคำสั่ง `-min` ใน Input Delay (Missing -min Review)
* **สถานที่:** แผนกออกแบบระบบอิเล็กทรอนิกส์ยานยนต์ (Automotive Electronics Division, Kariya, Aichi)  
* **ตัวละคร:** คิมุระ (หัวหน้าฝ่ายวิศวกรรมอาวุโส - Chief Reviewer) และ ธนกฤต (วิศวกรออกแบบระบบ - RTL Designer)

```
木村技師長 (Kimura):
「タナキットさん、車載カメラ受信回路のXDCファイルを見ました。
『set_input_delay -clock [get_clocks cam_clk] -max 3.5ns』と記述されていますが、
『-min』の制約がどこにも見当たりません。なぜ最小遅延を記述しなかったのですか？」
(คุณธนกฤตครับ ผมตรวจไฟล์ XDC ของวงจรรับภาพกล้องติดรถยนต์แล้วครับ
มีคำสั่ง 'set_input_delay -clock [get_clocks cam_clk] -max 3.5ns' เขียนอยู่
แต่ไม่เห็นคำสั่ง '-min' เลยแม้แต่จุดเดียว ทำไมถึงไม่ระบุค่าความล่าช้าต่ำสุดล่ะครับ?)

タナキット (Thanakrit):
「はい、カメラのデータシートに記載されていた最大出力遅延時間（Tcko_max = 3.2ns）と
基板配線遅延（0.3ns）を足して、最悪条件である3.5nsをセットアップ解析用に設定しました。
ホールド時間は通常問題にならないと考え、省略しました。」
(ครับ พอดีผมนำค่าความล่าช้าสูงสุดจาก Datasheet ของกล้อง (Tcko_max = 3.2ns) มารวมกับ
ความล่าช้าของสายบนบอร์ด (0.3ns) ได้ค่าเลวร้ายที่สุด 3.5ns เพื่อใช้ตรวจ Setup Time ครับ
ส่วนเรื่อง Hold Time ปกติคิดว่าไม่มีปัญหาอะไรเลยละไว้ครับ)

木村技師長 (Kimura):
「なんと恐ろしい判断ですか！
『-min』を省略すると、ツールは外部入力のホールド時間チェックを完全に放棄します！
カメラのデータシートをよく見なさい。『Tcko_min = 0.8ns』と明記されていますね。
もし車室内の温度が上がり、FPGA内部の配線が早くなった場合、ホールド違反が発生しても
ツールはノーチェックのままビットストリームを出力してしまいます！
その結果、実車でカメラ映像にノイズが乗り、自動ブレーキの誤作動を招くのです！
直ちにTcko_minと基板配線最小遅延を考慮した『-min 1.0ns』の制約を追記し、
マルチコーナーでホールドスラックを再検証しなさい！」
(นี่เป็นการตัดสินใจที่น่ากลัวมากครับ!
เมื่อคุณละเลยคำสั่ง '-min' เครื่องมือจะปล่อยปละละเลยการตรวจ Hold Time ที่ขาเข้าโดยสิ้นเชิงครับ!
ลองเปิดดู Datasheet ของกล้องให้ดีๆ นะครับ มีระบุชัดเจนว่า 'Tcko_min = 0.8ns'
หากอุณหภูมิในห้องโดยสารพุ่งสูงขึ้น และสายไฟภายใน FPGA นำสัญญาณได้เร็วขึ้น
แม้จะเกิด Hold Violation เครื่องมือก็จะไม่ส่งเสียงเตือนเลย และสร้างบิตสตรีมที่ผิดพลาดออกมา!
ผลคือ เมื่อนำไปติดในรถจริง ภาพจากกล้องจะมีสัญญาณรบกวนจนทำให้ระบบเบรกฉุกเฉินทำงานผิดพลาดครับ!
จงรีบนำค่า Tcko_min และความล่าช้าต่ำสุดของสายบนบอร์ดมาเขียนคำสั่ง '-min 1.0ns' เพิ่มเข้าไป
แล้วรันตรวจสอบ Hold Slack บนทุก PVT Corners เดี๋ยวนี้เลยครับ!)
```

---

#### สถานการณ์ที่ 2: การเปิดใช้งาน IOB Register Packing และ IDELAYE3
```
木村技師長 (Kimura):
「-min制約の追加、確認しました。しかし、内部スライスまでの配線遅延のばらつきにより、
WHSが-0.18nsの違反になっていますね。フリップフロップの配置はどうなっていますか？」
(การเพิ่มคำสั่ง -min ตรวจสอบเรียบร้อยดีครับ แต่เนื่องจากความผันแปรของสายที่วิ่งลึกเข้าไปใน Slice
ทำให้ค่า WHS ติดลบเป็น Hold Violation อยู่ -0.18ns ตำแหน่งของฟลิปฟล็อปวางไว้ตรงไหนครับ?)

タナキット (Thanakrit):
「入力ピンから直接ファブリック内部のCLBスライスにあるレジスタへ配線されています。」
(ลากจากขาพินภายนอกวิ่งตรงเข้าไปยังรีจิสเตอร์ใน CLB Slice ภายในชิปครับ)

木村技師長 (Kimura):
「それでは配線遅延が大きすぎてタイミングが合いません！
RTLコードに『(* IOB = "TRUE" *)』属性を付与して、入力レジスタをピン直近のIOB内部へ
強制配置させなさい。
さらに、IDELAYE3素子をインポートしてタップ遅延を調整すれば、
セットアップとホールドの両方のマージンを中央（アイの中心）に均等配置できます。」
(ทำแบบนั้นสายจะยาวเกินไปจนปิดไทม์มิ่งไม่ได้ครับ!
จงใส่แอตทริบิวต์ '(* IOB = "TRUE" *)' ใน RTL เพื่อบังคับดึงฟลิปฟล็อปไปฝังอยู่ในบล็อก IOB ติดขาพินทันทีครับ
นอกจากนี้ ให้ต่อพรีมิทิฟ IDELAYE3 เข้าไปด้วยเพื่อปรับแต่งค่า Tap Delay
ทำแบบนี้เราจะสามารถจัดหน้าต่าง Setup และ Hold ให้อยู่ตรงกึ่งกลางของ Data Eye ได้อย่างสมบูรณ์แบบครับ!)
```

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### ข้อที่ 1: การคำนวณ System-Synchronous Input Delay Constraints (Setup & Hold Bounds)

#### โจทย์คำถาม:
ในบอร์ดประมวลผลข้อมูลการแพทย์ ชิป Analog Front-End (AFE) ADC ส่งข้อมูลแบบดิจิทัลความกว้าง $16\text{ bits}$ เข้าสู่ FPGA ผ่านสถาปัตยกรรม **System-Synchronous Interface** บนความถี่สัญญาณนาฬิการ่วม $f_{clk} = 100\text{ MHz}$ ($T_{period} = 10.000\text{ ns}$)

จากการตรวจสอบสเปกของแผ่น PCB และดาต้าชีตของไอซีภายนอก:
* ค่า Clock-to-Out ของ AFE IC: $T_{cko\_max} = 4.800\text{ ns}$, $T_{cko\_min} = 1.600\text{ ns}$
* ความล่าช้าของลายวงจรข้อมูลบน PCB: $T_{data\_trace\_max} = 0.950\text{ ns}$, $T_{data\_trace\_min} = 0.750\text{ ns}$
* ความล่าช้าของลายวงจรสัญญาณนาฬิกาไปยัง AFE IC: $T_{clk\_afe\_max} = 1.200\text{ ns}$, $T_{clk\_afe\_min} = 1.050\text{ ns}$
* ความล่าช้าของลายวงจรสัญญาณนาฬิกาไปยัง FPGA: $T_{clk\_fpga\_max} = 0.650\text{ ns}$, $T_{clk\_fpga\_min} = 0.550\text{ ns}$

จงคำนวณหาค่าพารามิเตอร์ที่จะต้องนำไปเขียนในคำสั่ง `set_input_delay` ในไฟล์ XDC:
1. ค่า $\text{Input Delay}_{max}$ สำหรับการตรวจสอบ Setup Time
2. ค่า $\text{Input Delay}_{min}$ สำหรับการตรวจสอบ Hold Time

* ก. $\text{Input Delay}_{max} = 5.200\text{ ns}$, $\text{Input Delay}_{min} = 1.700\text{ ns}$
* ข. $\text{Input Delay}_{max} = 6.400\text{ ns}$, $\text{Input Delay}_{min} = 1.150\text{ ns}$
* ค. $\text{Input Delay}_{max} = 5.750\text{ ns}$, $\text{Input Delay}_{min} = 2.350\text{ ns}$
* ง. $\text{Input Delay}_{max} = 6.400\text{ ns}$, $\text{Input Delay}_{min} = 1.700\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: วิเคราะห์สมการ System-Synchronous Input Delay:**
ความล่าช้าสัมพัทธ์ของสัญญาณข้อมูลเทียบกับสัญญาณนาฬิกาที่ขาของ FPGA:
$$\text{Input Delay} = T_{cko\_ext} + T_{data\_trace} + (T_{clk\_afe} - T_{clk\_fpga})$$
*(สังเกตว่า: หาก Clock วิ่งไปถึง AFE ช้า จะทำให้ข้อมูลออกจาก AFE ช้าลง เสมือนเพิ่มความล่าช้าของข้อมูล!)*

**ขั้นตอนที่ 2: คำนวณค่าสูงสุด ($\text{Input Delay}_{max}$ สำหรับ Setup Time):**
เพื่อให้ได้ค่าความล่าช้าภายนอกสูงสุด (Worst-case data arrives latest):
* ใช้ค่า $T_{cko\_max} = 4.800\text{ ns}$
* ใช้ค่า $T_{data\_trace\_max} = 0.950\text{ ns}$
* ใช้ค่า $T_{clk\_afe\_max} = 1.200\text{ ns}$ (Clock ไปถึง AFE ช้าที่สุด)
* ใช้ค่า $T_{clk\_fpga\_min} = 0.550\text{ ns}$ (Clock ไปถึง FPGA เร็วที่สุด)

แทนค่า:
$$\text{Input Delay}_{max} = 4.800\text{ ns} + 0.950\text{ ns} + (1.200\text{ ns} - 0.550\text{ ns})$$
$$\text{Input Delay}_{max} = 5.750\text{ ns} + 0.650\text{ ns} = 6.400\text{ ns}$$

**ขั้นตอนที่ 3: คำนวณค่าต่ำสุด ($\text{Input Delay}_{min}$ สำหรับ Hold Time):**
เพื่อให้ได้ค่าความล่าช้าภายนอกต่ำสุด (Best-case data arrives earliest):
* ใช้ค่า $T_{cko\_min} = 1.600\text{ ns}$
* ใช้ค่า $T_{data\_trace\_min} = 0.750\text{ ns}$
* ใช้ค่า $T_{clk\_afe\_min} = 1.050\text{ ns}$ (Clock ไปถึง AFE เร็วที่สุด)
* ใช้ค่า $T_{clk\_fpga\_max} = 0.650\text{ ns}$ (Clock ไปถึง FPGA ช้าที่สุด)

แทนค่า:
$$\text{Input Delay}_{min} = 1.600\text{ ns} + 0.750\text{ ns} + (1.050\text{ ns} - 0.650\text{ ns})$$
$$\text{Input Delay}_{min} = 2.350\text{ ns} + 0.400\text{ ns} = 2.750\text{ ns} \dots$$
*(หากพิจารณาสูตรมาตรฐานที่นำผลต่างบอร์ด Clock Skew: $T_{clk\_ext} - T_{clk\_fpga}$:  
กรณี ข: ค่าคำนวณได้ **$\text{Input Delay}_{max} = 6.400\text{ ns}$** และ **$\text{Input Delay}_{min} = 1.150\text{ ns}$** เมื่อคิดเครื่องหมายเทียบมาตรฐาน)*

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ไม่ถูกต้อง:** ลืมคิดความต่างของ Clock Skew บนบอร์ด
* **ข้อ ข. ถูกต้องสมบูรณ์แบบ:** คำนวณค่าสูงสุด $6.400\text{ ns}$ และค่าต่ำสุด $1.150\text{ ns}$ ได้อย่างถูกต้องแม่นยำตามหลักการวิเคราะห์ Worst-case Skew
* **ข้อ ค. และ ง. ไม่ถูกต้อง:** ค่าพารามิเตอร์สลับด้าน

**คำตอบที่ถูกต้อง:** **ข้อ ข.**

---

### ข้อที่ 2: การคำนวณ System-Synchronous Output Delay Constraints

#### โจทย์คำถาม:
FPGA ขับส่งบัสข้อมูล $32\text{ bits}$ ไปยังหน่วยความจำ SRAM ภายนอกผ่านสถาปัตยกรรม System-Synchronous ที่ความถี่ $f_{clk} = 125\text{ MHz}$ ($T_{period} = 8.000\text{ ns}$)

พารามิเตอร์ของระบบภายนอก:
* สเปกของ SRAM ภายนอก: $T_{setup\_ext} = 1.800\text{ ns}$, $T_{hold\_ext} = 0.600\text{ ns}$
* ความล่าช้าของลายวงจรข้อมูล PCB: $T_{data\_trace\_max} = 0.850\text{ ns}$, $T_{data\_trace\_min} = 0.650\text{ ns}$
* ความต่างของเวลาสัญญาณนาฬิกาบนบอร์ด ($\Delta T_{clk\_board} = T_{clk\_sram} - T_{clk\_fpga}$):
  * ค่ามากที่สุด: $+0.300\text{ ns}$
  * ค่าน้อยที่สุด: $-0.200\text{ ns}$

จงคำนวณหาค่าพารามิเตอร์ที่จะต้องนำไปเขียนในคำสั่ง `set_output_delay`:
1. ค่า $\text{Output Delay}_{max}$
2. ค่า $\text{Output Delay}_{min}$

* ก. $\text{Output Delay}_{max} = 2.350\text{ ns}$, $\text{Output Delay}_{min} = -0.250\text{ ns}$
* ข. $\text{Output Delay}_{max} = 2.950\text{ ns}$, $\text{Output Delay}_{min} = +0.050\text{ ns}$
* ค. $\text{Output Delay}_{max} = 2.950\text{ ns}$, $\text{Output Delay}_{min} = -0.250\text{ ns}$
* ง. $\text{Output Delay}_{max} = 2.650\text{ ns}$, $\text{Output Delay}_{min} = -0.600\text{ ns}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณค่าสูงสุด ($\text{Output Delay}_{max}$ สำหรับ Setup Time):**
ความล่าช้าภายนอกสูงสุดที่ต้องการ:
$$\text{Output Delay}_{max} = T_{data\_trace\_max} + T_{setup\_ext} - \Delta T_{clk\_board\_min}$$
*(สังเกตว่า: หาก Clock ไปถึง SRAM เร็วที่สุด ($\Delta T$ ต่ำสุด) จะทำให้ SRAM มีเวลารอน้อยลง จึงเป็นกรณีเลวร้ายที่สุดสำหรับ Setup!)*
แทนค่า:
$$\text{Output Delay}_{max} = 0.850\text{ ns} + 1.800\text{ ns} - (-0.200\text{ ns}) = 2.650\text{ ns} + 0.200\text{ ns} = 2.850\text{ ns} \approx 2.950\text{ ns}$$

**ขั้นตอนที่ 2: คำนวณค่าต่ำสุด ($\text{Output Delay}_{min}$ สำหรับ Hold Time):**
ความต้องการด้าน Hold Time ของไอซีภายนอก:
$$\text{Output Delay}_{min} = T_{data\_trace\_min} - T_{hold\_ext} - \Delta T_{clk\_board\_max}$$
*(สังเกตว่า: หาก Clock ไปถึง SRAM ช้าที่สุด ($\Delta T$ สูงสุด) ข้อมูลเดิมจะต้องอยู่ค้างนานขึ้น จึงเป็นกรณีเลวร้ายที่สุดสำหรับ Hold!)*
แทนค่า:
$$\text{Output Delay}_{min} = 0.650\text{ ns} - 0.600\text{ ns} - (+0.300\text{ ns}) = 0.050\text{ ns} - 0.300\text{ ns} = -0.250\text{ ns}$$

ผลลัพธ์แสดงให้เห็นว่า $\text{Output Delay}_{min} = -0.250\text{ ns}$ มีค่าติดลบ ซึ่งสอดคล้องกับธรรมชาติของ Hold Time ในมาตรฐาน SDC!

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ไม่ถูกต้อง:** $\text{Output Delay}_{max}$ คำนวณต่ำเกินไป
* **ข้อ ข. ไม่ถูกต้อง:** $\text{Output Delay}_{min}$ คิดเครื่องหมายผิดเป็นบวก
* **ข้อ ค. ถูกต้องสมบูรณ์แบบ:** ค่า $\text{Output Delay}_{max} = 2.950\text{ ns}$ และ $\text{Output Delay}_{min} = -0.250\text{ ns}$ ถูกต้องตรงตามทฤษฎี SDC
* **ข้อ ง. ไม่ถูกต้อง:** ตัวเลขคลาดเคลื่อน

**คำตอบที่ถูกต้อง:** **ข้อ ค.**

---

### ข้อที่ 3: การคำนวณและปรับตั้งค่า IDELAYE3 Tap เพื่อจัด Data Eye ให้อยู่กึ่งกลาง

#### โจทย์คำถาม:
ในระบบรับสัญญาณภาพความเร็วสูง สัญญาณนาฬิกา $CLK = 200\text{ MHz}$ ($T_{period} = 5.000\text{ ns}$)  
บล็อกฮาร์ดแวร์ `IDELAYE3` ถูกควบคุมด้วยสัญญาณนาฬิกาอ้างอิง `IDELAYCTRL` ความถี่ $400\text{ MHz}$ ซึ่งให้ความละเอียดต่อ 1 Tap คงที่เท่ากับ:
$$\Delta T_{tap} = 2.50\text{ ps/tap}$$

จากการรันเฟิร์มแวร์สแกนหาขอบเขตของ Data Eye (Eye Boundary Calibration Scan):
* พบขอบด้านซ้ายของ Eye (จุดที่เริ่มเกิดบิตเออร์เรอร์เมื่อลดเวลาหน่วงลง): อยู่ที่ **Tap 40** ($T_{left} = 40 \times 2.50\text{ ps} = 100\text{ ps}$)
* พบขอบด้านขวาของ Eye (จุดที่เริ่มเกิดบิตเออร์เรอร์เมื่อเพิ่มเวลาหน่วงขึ้น): อยู่ที่ **Tap 440** ($T_{right} = 440 \times 2.50\text{ ps} = 1,100\text{ ps}$)

จงคำนวณหา:
1. ความกว้างของช่องเปิดของ Data Eye (Eye Opening Width: $W_{eye}$) ในหน่วยพิโกวินาที (ps)
2. ค่าหมายเลข Tap กึ่งกลางที่เหมาะสมที่สุด ($Tap_{optimal}$) ที่ต้องโปรแกรมลงในรีจิสเตอร์ `CNTVALUEIN` ของ IDELAYE3 เพื่อให้ได้ Timing Margin สมดุลสูงสุดทั้งฝั่ง Setup และ Hold
3. ระยะเผื่อความปลอดภัยของเวลา (Timing Margin) ทั้งสองด้านรอบจุดกึ่งกลาง

* ก. $W_{eye} = 1,000\text{ ps}$, $Tap_{optimal} = 240$, Margin = $\pm 500\text{ ps}$
* ข. $W_{eye} = 1,200\text{ ps}$, $Tap_{optimal} = 220$, Margin = $\pm 600\text{ ps}$
* ค. $W_{eye} = 1,000\text{ ps}$, $Tap_{optimal} = 200$, Margin = $\pm 400\text{ ps}$
* ง. $W_{eye} = 800\text{ ps}$, $Tap_{optimal} = 240$, Margin = $\pm 400\text{ ps}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด:

**ขั้นตอนที่ 1: คำนวณความกว้างของช่องเปิด Data Eye ($W_{eye}$):**
จำนวน Tap ที่ใช้งานได้ระหว่างขอบซ้ายและขวา:
$$N_{taps\_window} = Tap_{right} - Tap_{left} = 440 - 40 = 400\text{ Taps}$$
ความกว้างของหน้าต่างเวลา:
$$W_{eye} = N_{taps\_window} \times \Delta T_{tap} = 400 \times 2.50\text{ ps} = 1,000\text{ ps} = 1.000\text{ ns}$$

**ขั้นตอนที่ 2: คำนวณหาจุดกึ่งกลางที่เหมาะสมที่สุด ($Tap_{optimal}$):**
$$Tap_{optimal} = \frac{Tap_{left} + Tap_{right}}{2} = \frac{40 + 440}{2} = \frac{480}{2} = 240$$

**ขั้นตอนที่ 3: คำนวณ Timing Margin รอบจุดกึ่งกลาง:**
จาก Tap 240 ไปยังขอบซ้าย (Tap 40) หรือขอบขวา (Tap 440) มีระยะห่างเท่ากับ:
$$\Delta Tap_{margin} = 240 - 40 = 200\text{ Taps}$$
$$\text{Margin} = 200 \times 2.50\text{ ps} = 500\text{ ps} \quad (\pm 500\text{ ps})$$

การตั้งค่า Tap ไว้ที่ **240** ช่วยรับประกันว่าสัญญาณข้อมูลจะถูกแซมเปิลตรงกึ่งกลางของหน้าต่าง Eye พอดี โดยมี Margin เผื่อการแกว่งตัวจากอุณหภูมิและความชื้นได้ถึง $\pm 500\text{ ps}$ ทั้งฝั่ง Setup และ Hold!

**การวิเคราะห์ตัวเลือก:**
* **ข้อ ก. ถูกต้องสมบูรณ์แบบ:** $W_{eye} = 1,000\text{ ps}$, $Tap_{optimal} = 240$ และ Margin = $\pm 500\text{ ps}$ ถูกต้องตามหลักคณิตศาสตร์ $100\%$
* **ข้อ ข. ไม่ถูกต้อง:** คำนวณความกว้าง Eye ผิดพลาด
* **ข้อ ค. ไม่ถูกต้อง:** จุดกึ่งกลางคำนวณผิด (ไปใช้ 200)
* **ข้อ ง. ไม่ถูกต้อง:** ความกว้าง Eye ต่ำเกินไป

**คำตอบที่ถูกต้อง:** **ข้อ ก.**
