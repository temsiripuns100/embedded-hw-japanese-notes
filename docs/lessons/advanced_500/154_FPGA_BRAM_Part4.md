# Lesson 154: BRAM Collision Handling and Read-during-Write Behavior (WRITE_FIRST, READ_FIRST, NO_CHANGE Modes, Same-Port vs Dual-Port Collisions, Power Dissipation & Data Forwarding Logic)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

### 1.1 กายวิภาคของการอ่านและเขียนพร้อมกันในเซลล์ 6T SRAM (Silicon Physics of Read-during-Write)
ในหน่วยความจำ Block RAM เมื่อสัญญาณ Write Enable มีสถานะแอกทีฟ (`WE = 1`) ในรอบสัญญาณนาฬิกาเดียวกันที่มีการส่งสัญญาณแอดเดรสเข้าไป วงจรควบคุมภายใน BRAM Hard Macro จะต้องจัดการกับการเข้าถึงเซลล์หน่วยความจำ 6T SRAM:
* ข้อมูลใหม่บนพอร์ต $DIN$ กำลังถูกผลักผ่าน Pass-Gate Transistors เข้าไปประจุสาย Bitline เพื่อเขียนทับสถานะเดิมใน Latch
* ในขณะเดียวกัน วงจรตรวจจับ (Sense Amplifier) หรือ Output Latch กำลังพยายามดึงข้อมูลออกไปที่พอร์ต $DOUT$

พฤติกรรมของข้อมูลเอาต์พุต ณ จังหวะนั้นถูกกำหนดโดยคุณสมบัติฮาร์ดแวร์ที่เรียกว่า **Read-during-Write Mode** (หรือ `WRITE_MODE` Attribute):

```
                     3 โหมดการทำงานของ READ-DURING-WRITE ใน BRAM
                     
  [ 1. WRITE_FIRST (Transparent / Read-after-Write) ]
  DIN =====+=========================================> [ Write into SRAM Cell ]
           | (Internal Bypass Wire)
           +-----------------------------------------> DOUT (เอาต์พุตสะท้อน "ข้อมูลใหม่" ทันที!)
  
  [ 2. READ_FIRST (Read-before-Write) ]
  SRAM Cell Core ===> [ Capture Old Data First ] =====> DOUT (เอาต์พุตส่ง "ข้อมูลเก่า" ออกไปก่อน)
                             | (จากนั้นจึงเขียนทับ)
  DIN ================> [ Overwrite Cell ]
  
  [ 3. NO_CHANGE (Power Optimization Mode) ]
  DIN ================> [ Write into SRAM Cell ]
  
  DOUT Pad ===========[ Latch Frozen / No Toggle ]==== (เอาต์พุต "คงค่าเดิมค้างไว้" ไม่ขยับ!)
```

#### คุณลักษณะและการเปรียบเทียบทั้ง 3 โหมด:
1. **`WRITE_FIRST` (โหมดโปร่งใส):**
   * ข้อมูลใหม่ที่เพิ่งเขียนลงในไซเคิลนี้ จะปรากฏที่พอร์ตเอาต์พุต $DOUT$ ในไซเคิลถัดไป
   * เหมาะสำหรับ: วงจร Register File ในโปรเซสเซอร์ หรือวงจรที่ต้องการพฤติกรรมแบบเขียนเสร็จแล้วอ่านต่อทันที
2. **`READ_FIRST` (โหมดอ่านค่าเดิมก่อนเขียนทับ):**
   * ข้อมูลเก่าที่เคยบันทึกอยู่ในแอดเดรสนั้นก่อนการเขียน จะถูกดึงออกไปที่พอร์ต $DOUT$ ก่อนที่ข้อมูลใหม่จะเขียนทับลงไป
   * เหมาะสำหรับ: วงจร Read-Modify-Write แบบไซเคิลเดียว (เช่น การอ่านค่ายอดสะสมเดิมออกมาบวกเพิ่มแล้วเขียนกลับ)
3. **`NO_CHANGE` (โหมดประหยัดพลังงานขั้นสูงสุด):**
   * ในไซเคิลใดๆ ที่มีการเขียน (`WE = 1`) เอาต์พุต $DOUT$ จะถูกแช่แข็งค้างค่าเดิมไว้ ไม่มีการสลับสถานะของบัสข้อมูล
   * **ผลลัพธ์:** ลดทอนอัตราการสลับระดับสัญญาณ (Toggle Rate $\alpha$) บนบัสข้อมูลกว้าง 32/64 บิตลงเหลือศูนย์ ช่วยประหยัดพลังงาน Dynamic Power ได้มหาศาล!

---

### 1.2 ฟิสิกส์ของการประหยัดพลังงานด้วยโหมด NO_CHANGE (Dynamic Power Physics)

กำลังไฟฟ้าสูญเสียแบบพลวัตที่เกิดจากการสลับสถานะของบัสเอาต์พุต BRAM:

$$P_{dynamic} = \frac{1}{2} \cdot V_{dd}^2 \cdot f_{clk} \cdot \sum_{i=1}^{W} \left( C_{i} \cdot \alpha_i \right)$$
โดยที่:
* $W$ คือ ความกว้างของบัสข้อมูล (เช่น 64 หรือ 128 บิต)
* $C_i$ คือ ความจุไฟฟ้าแฝงของสายส่ง Interconnect ยาวที่ลากออกจาก BRAM ข้าม Die
* $\alpha_i$ คือ **Toggle Rate (อัตราการสลับสถานะของแต่ละบิต)**

```
               การเปรียบเทียบ TOGGLE ACTIVITY: WRITE_FIRST VS NO_CHANGE
               
  [ สภาวะเขียนข้อมูลต่อเนื่อง (Continuous Write Ingest): WE = 1 ตลอดเวลา ]
  
  โหมด WRITE_FIRST:
  DIN Bus (สุ่ม) ---> DOUT Bus สลับตาม DIN ทุกไซเคิล! (Toggle Rate alpha = 0.40 ~ 0.50)
                      ผลาญพลังงานสวิตชิ่งบนสาย Interconnect เต็ม 100%!
  
  โหมด NO_CHANGE:
  DIN Bus (สุ่ม) ---> DOUT Bus ถูกแช่แข็งค้างนิ่งสนิท! (Toggle Rate alpha = 0.00!)
                      กำลังไฟฟ้าสวิตชิ่งบนบัสเอาต์พุต = 0.00 mW!
                      ===> ประหยัดพลังงาน BRAM ลงได้ถึง 35% ~ 55%!
```

ในแอปพลิเคชันที่มีการบันทึกข้อมูลปริมาณมหาศาลเข้า BRAM เช่น Packet FIFO Ingest หรือ Video Stream Line Buffers เอาต์พุตของ BRAM มักไม่ได้ถูกอ่านในจังหวะที่มีการเขียน  
การปล่อยให้เป็น `WRITE_FIRST` (ซึ่งเป็นค่า Default ของ Synthesizer หลายตัว) จะทำให้สายบัสยาว 64-บิต สลับสถานะไปมาโดยไร้ประโยชน์ ผลาญพลังงานแบตเตอรี่ในอุปกรณ์พกพาและสร้างความร้อนสะสมบน Die โดยใช่เหตุ!

---

### 1.3 ความแตกต่างระดับวิกฤต: Same-Port vs Dual-Port Collisions

> [!WARNING]
> **ภาพลวงตามรณะ (The Fatal Dual-Port Assumption):**  
> ข้อผิดพลาดอันดับ 1 ของวิศวกรคือ: *"ฉันตั้งโหมด BRAM เป็น `WRITE_FIRST` แล้ว ดังนั้นหาก Port A เขียนข้อมูลลงแอดเดรส $X$ ในขณะที่ Port B อ่านข้อมูลที่แอดเดรส $X$ พอร์ต B ย่อมได้ข้อมูลใหม่ที่ถูกต้องแน่นอน"*  
> **นี่คือความเข้าใจผิดที่ทำให้ระบบพังพินาศในโลกความเป็นจริง!**

```
               ความแตกต่างระหว่าง SAME-PORT VS DUAL-PORT READ-DURING-WRITE
               
  [ กรณีที่ 1: SAME-PORT (พอร์ตเดียวกัน $ADDR_A == ADDR_A$) ]
  - ทำงานบน Clock เดียวกัน 100%
  - ควบคุมโดยลอจิกภายในเซลล์เดียวกัน
  - ผลลัพธ์: แน่นอนสมบูรณ์แบบ 100% (Deterministic) ตามโหมด WRITE_MODE ที่เลือก!
  
  [ กรณีที่ 2: TRUE DUAL-PORT ($ADDR_A == ADDR_B$ ข้ามพอร์ต) ]
  - พอร์ต A และ B ใช้สาย Bitline คนละชุดที่เข้าถึง 6T SRAM Cell ก้อนเดียวกัน
  - หาก CLKA และ CLKB เป็นคนละ Clock หรือมี Skew ทางเวลา:
    วงจร Sense Amplifier ของพอร์ตอ่านจะพยายามดึงข้อมูลในขณะที่ Pass-gate ของพอร์ตเขียนกำลังดึงไฟ
  - ผลลัพธ์ในซิลิคอน:
    ========================================================================
    เอาต์พุตของพอร์ตอ่านจะกลายเป็น "UNDEFINED (ค่าขยะ / สุ่มบิต / X)" 100%!
    โหมด WRITE_FIRST หรือ READ_FIRST ไม่สามารถคุ้มครองข้ามพอร์ตได้เด็ดขาด!
    ========================================================================
```

---

### 1.4 วงจรบายพาสข้อมูลภายนอก (External Data Forwarding Bypass Logic)
เพื่อสร้างระบบหน่วยความจำที่รับประกันความถูกต้องของข้อมูล $100\%$ แบบ Coherent โดยไม่ขึ้นกับพฤติกรรมเฉพาะตัวของชิปแต่ละค่าย วิศวกรระดับ Senior ต้องสร้าง **External Data Forwarding Circuit** ครอบอยู่นอก BRAM:

```
                  สถาปัตยกรรม EXTERNAL DATA FORWARDING BYPASS
                  
                 Write Address (wr_addr)
                     |
                     v
             +---------------+   Address Match?
             |   COMPARATOR  |--------------------+ (addr_match = 1)
             +---------------+                    |
                     ^                            v
                     |                  +--------------------+
                 Read Address (rd_addr) | FORWARDING MUX     |
                                        | (1 = Bypass Data)  |===> COHERENT DOUT
   Write Data (wr_data) ===============>| (0 = BRAM DOUT)    |
                                        +--------------------+
                                                  ^
   BRAM Memory Array =============================+
   (Standard RAMB36 Macro)
```

หากเกิดเหตุการณ์เขียนและอ่านที่แอดเดรสเดียวกันในไซเคิลเดียวกัน วงจรตรวจจับความสอดคล้อง (Comparator) จะสับสวิตช์มัลติเพล็กเซอร์นำข้อมูล `wr_data` ที่กำลังจะเขียน ส่งตรงไปเป็น `dout` ในทันที โดยข้ามการอ่านจากเนื้อ BRAM อย่างสมบูรณ์แบบ ขจัดปัญหา Address Collision ไปได้อย่างสิ้นเชิง!

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความล้มเหลวหน้างาน: 失敗事例 (Shippai Jirei)
**สถานการณ์:** ระบบจับคู่คำสั่งซื้อขายหลักทรัพย์ความเร็วสูงระดับไมโครวินาที (High-Frequency Trading: HFT Ultra-Low Latency Order Matching Engine) พัฒนาบน FPGA Acceleration Card (Xilinx Alveo U50):
* สมุดคำสั่งซื้อขาย (Order Book Memory) จัดเก็บอยู่ใน BRAM36 แบบ True Dual-Port:
  * **Port A ($322.0\text{ MHz}$):** คำสั่งซื้อขายใหม่จากตลาด (New Limit Orders) เขียนบันทึกราคาและจำนวนหุ้น
  * **Port B ($322.0\text{ MHz}$):** อัลกอริทึมจับคู่คำสั่งซื้อ (Matching Engine) อ่านข้อมูลเพื่อจับคู่คำสั่งซื้อและขาย

**วิกฤตหน้างาน:** ในช่วงเปิดตลาดซื้อขายภาคเช้าที่มีปริมาณคำสั่งซื้อพุ่งเข้ามาอย่างบ้าคลั่ง (Morning Surge Traffic) ระบบจับคู่คำสั่งซื้อเกิดอาการรวนอย่างรุนแรง: **ส่งคำสั่งจับคู่ราคาผิดพลาด (Ghost Trades) และจับคู่ราคาหุ้นเพี้ยนไปจากตลาดกว่า 400 รายการ** ภายในเวลาเพียง $45\text{ มิลลิวินาที}$ สร้างความเสียหายทางการเงินแก่นักลงทุนและบริษัทหลักทรัพย์กว่า 14 ล้านบาท ($380,000) ระบบถูกตลาดหลักทรัพย์สั่งปิดการเชื่อมต่อฉุกเฉินทันที!

---

### การวิเคราะห์รากเหง้าปัญหาด้วย 5 Whys (5 Whys Root Cause Analysis)

```
[ปัญหาหน้างาน] ระบบ HFT เกิด Ghost Trades และจับคู่ราคาผิดพลาดในช่วงทราฟฟิกกระชาก
      |
      +---> [Why 1] ทำไมจึงเกิดการจับคู่ราคาหุ้นเพี้ยนไปจากราคาจริง?
      |             --> เพราะข้อมูลราคา (Price Field) ที่อ่านจาก Order Book BRAM มีบิตเพี้ยนเป็นค่าสุ่ม
      |
      +---> [Why 2] ทำไมข้อมูลราคาใน BRAM ถึงเพี้ยนเป็นค่าสุ่ม?
      |             --> เพราะเกิด True Dual-Port Read-during-Write Collision บนสล็อตแอดเดรสเดียวกัน
      |
      +---> [Why 3] ทำไมจึงเกิดการอ่านและเขียนชนกันบนสล็อตเดียวกัน?
      |             --> เพราะมีคำสั่ง Cancel Order เข้ามาที่ Port A ขณะที่ Matching Engine (Port B) กำลังอ่านสล็อตนั้นพอดี
      |
      +---> [Why 4] ทำไมผู้ออกแบบถึงไม่ใส่วงจรป้องกันการอ่านชนกัน?
      |             --> เพราะผู้ออกแบบตั้งค่า BRAM เป็นโหมด `WRITE_FIRST` และทึกทักเอาเองว่า
      |                 Port B จะได้ข้อมูลใหม่ล่าสุดอย่างปลอดภัยข้ามพอร์ต
      |
      +---> [Why 5 - Root Cause] ทำไมความเข้าใจผิดนี้จึงเกิดขึ้น?
                    --> เพราะผู้ออกแบบไม่เข้าใจฟิสิกส์ของ BRAM Hard Macro ว่าโหมด `WRITE_FIRST`
                        รับประกันความถูกต้องเฉพาะภายใน "พอร์ตเดียวกัน" เท่านั้น ไม่รองรับข้ามพอร์ต TDP!
```

---

### แผนภูมิก้างปลา (Ishikawa Fishbone Diagram)

```
สาเหตุการเกิดข้อมูลเพี้ยนในระบบเทรด HFT จาก BRAM Collision

   SILICON ASSUMPTIONS                        MEMORY TOPOLOGY (No Forwarding)
         |                                          |
   เข้าใจผิดว่า WRITE_FIRST คุ้มครองข้ามพอร์ต         ไม่มีวงจร Address Comparator ภายนอก
         \                                          /
          \   สาย Bitline ก้ำกึ่งข้ามพอร์ต           /   ขาดวงจร Forwarding MUX ดักข้อมูล
           \   Sense Amp พอร์ต B อ่านค่าขยะ X       /   พึ่งพาคุณสมบัติ Hard Macro โดยไม่ปลอดภัย
            +------------------------------------+
            |                                    |
            |   HFT ORDER BOOK CORRUPTION        |===> [CRITICAL FINANCIAL CRASH]
            |   ($380,000 LOSS IN 45 MS)         |
            +------------------------------------+
           /                                      \
          /   ทดสอบเฉพาะทราฟฟิกต่ำในห้องแล็บ         \   ไม่ได้รัน Simultaneous Collision Verification
         /                                          \
   มองข้าม Warning ใน Vivado Simulation เกี่ยวกับ X   ละเลยการใช้ Formal Verification ตรวจสอบ Data Hazard
         |                                          |
   TESTING BLIND-SPOTS                        VERIFICATION DEFICIENCIES
```

---

### โค้ด RTL ฮาร์ดแวร์แก้ปัญหา: วงจร Data Forwarding Bypass ที่สมบูรณ์แบบ

```verilog
// ==============================================================================
// SOP-COMPLIANT ZERO-LATENCY DATA FORWARDING BYPASS CONTROLLER
// ==============================================================================
module coherent_order_book_bram #(
    parameter integer ADDR_WIDTH = 10,
    parameter integer DATA_WIDTH = 64
)(
    input  wire                  clk,
    input  wire                  rst_n,
    
    // พอร์ตเขียน (Port A: Order Update)
    input  wire                  we_a,
    input  wire [ADDR_WIDTH-1:0] addr_a,
    input  wire [DATA_WIDTH-1:0] din_a,
    
    // พอร์ตอ่าน (Port B: Matching Engine)
    input  wire                  re_b,
    input  wire [ADDR_WIDTH-1:0] addr_b,
    output reg  [DATA_WIDTH-1:0] dout_b
);

    // หน่วยความจำ BRAM ทำงานในโหมด READ_FIRST หรือ NO_CHANGE เพื่อเสถียรภาพสูงสุด
    (* ram_style = "block" *) reg [DATA_WIDTH-1:0] memory [(2**ADDR_WIDTH)-1:0];
    reg [DATA_WIDTH-1:0] raw_bram_dout_b;
    
    // รีจิสเตอร์สำหรับติดตามสภาวะ Collision ข้ามรอบสัญญาณนาฬิกา
    reg                  forward_valid;
    reg [DATA_WIDTH-1:0] forward_data;

    // 1. วงจรหลัก BRAM Read/Write
    always @(posedge clk) begin
        if (we_a) begin
            memory[addr_a] <= din_a;
        end
        if (re_b) begin
            raw_bram_dout_b <= memory[addr_b];
        end
    end

    // 2. วงจรตรวจจับการชนกันและเตรียมข้อมูล Forwarding (Address Comparator Pipeline)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            forward_valid <= 1'b0;
            forward_data  <= '0;
        end else begin
            // ตรวจสอบว่าในไซเคิลนี้ มีการเขียนที่แอดเดรสเดียวกับที่กำลังอ่านหรือไม่
            if (we_a && re_b && (addr_a == addr_b)) begin
                forward_valid <= 1'b1;
                forward_data  <= din_a; // ดักจับข้อมูลที่กำลังจะเขียน
            end else begin
                forward_valid <= 1'b0;
            end
        end
    end

    // 3. มัลติเพล็กเซอร์เลือกข้อมูลที่ปลอดภัย 100% (Zero Collision Hazard)
    always @(*) begin
        if (forward_valid) begin
            dout_b = forward_data;  // บายพาสข้อมูลตรง ไม่แคร์ BRAM Corruption!
        end else begin
            dout_b = raw_bram_dout_b; // อ่านจาก BRAM ตามปกติ
        end
    end

endmodule
```

---

### SOP Checklist สำหรับการกำหนดค่า Read-during-Write และป้องกัน Collision

```
[ ] 1. Power-Conscious Write Mode Selection:
       - อาร์เรย์ใดๆ ที่ใช้เป็น FIFO หรือ Buffer เขียนต่อเนื่อง: บังคับตั้ง `WRITE_MODE = "NO_CHANGE"`
       - ห้ามปล่อยให้เป็น Default (`WRITE_FIRST`) หากเอาต์พุตไม่มีความจำเป็นต้องอ่านขณะเขียน

[ ] 2. True Dual-Port Independence Verification:
       - หากใช้ TDP ข้ามพอร์ต: ห้ามพึ่งพาโหมด `WRITE_FIRST` ในการส่งข้อมูลข้ามพอร์ตเด็ดขาด
       - ต้องติดตั้งวงจร External Data Forwarding หรือใช้ Time-Division Arbitration แยกไซเคิล

[ ] 3. Simulation Model Collision Warnings Audit:
       - ตรวจสอบผลการจำลองการทำงานใน Vivado Simulator (XSim / Questa):
         ต้องไม่มี Warning: `Memory collision detected on RAMB36E2 at address ... Output is X`

[ ] 4. Formal Verification for Read-After-Write Hazards:
       - ใช้เครื่องมือ Formal Verification ตรวจสอบ Property:
         `assert property (@(posedge clk) (we_a && re_b && addr_a == addr_b) |-> (dout_b == din_a));`
```

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 ตารางคำศัพท์เทคนิคเฉพาะทาง (専門用語一覧)

| คำศัพท์คันจิ | ฮิรางานะ / คาตากานะ | โรมะจิ | ความหมายภาษาไทย / คำอธิบายวิศวกรรม |
|---|---|---|---|
| 同時読み書き動作 | どうじよみかきどうさ | Dōji Yomikaki Dōsa | การอ่านและเขียนในเวลาเดียวกัน (Read-during-Write Behavior) |
| ライトファースト | らいとふぁーすと | Raito Fāsuto | โหมดสะท้อนข้อมูลใหม่ทันที (WRITE_FIRST / Read-after-Write) |
| リードファースト | りーどふぁーすと | Rīdo Fāsuto | โหมดส่งข้อมูลเก่าออกมาก่อนเขียนทับ (READ_FIRST / Read-before-Write) |
| ノーチェンジモード | のーちぇんじもーど | Nō Chenji Mōdo | โหมดแช่แข็งเอาต์พุตเพื่อประหยัดพลังงาน (NO_CHANGE Mode) |
| 同一ポート衝突 | どういつぽーとしょうとつ | Dōitsu Pōto Shōtotsu | การชนกันภายในพอร์ตเดียวกัน (Same-Port Collision) |
| 異ポート間衝突 | いぽーとかんしょうとつ | I-Pōto-kan Shōtotsu | การชนกันระหว่างสองพอร์ตต่างกัน (Dual-Port Collision) |
| データ転送バイパス | でーたてんそうばいぱす | Dēta Tensō Baipasu | วงจรลัดข้อมูลล่วงหน้า (Data Forwarding Bypass Logic) |
| トグル率低減 | とぐるりつていげん | Toguru-ritsu Teigen | การลดทอนอัตราการสลับสถานะของสัญญาณ (Toggle Rate Reduction) |
| 不定値出力 | ふていちしゅつりょく | Futeichi Shutsuryoku | สัญญาณเอาต์พุตที่ไม่สามารถระบุค่าได้ (Undefined / Corrupted 'X' Output) |
| データ整合性保証 | でーたせいごうせいほしょう | Dēta Seigōsei Hoshō | การรับประกันความสอดคล้องถูกต้องของข้อมูล (Data Coherency Guarantee) |
| 競合検出回路 | きょうごうけんしゅつかいろ | Kyōgō Kenshutsu Kairo | วงจรตรวจจับการชนกันของการเข้าถึง (Collision Detection Circuit) |
| 誤約定防止 | ごやくじょうぼうし | Goyakujō Bōshi | การป้องกันการจับคู่คำสั่งซื้อขายผิดพลาด (Ghost Trade Prevention) |

---

### 3.2 บทสนทนาการตรวจแบบหน้างานจริง (検図の実践対話)

#### สถานการณ์ที่ 1: การตรวจพบการพึ่งพาโหมด `WRITE_FIRST` ใน True Dual-Port BRAM
**สถานที่:** ศูนย์พัฒนาอัลกอริทึมการเงินความเร็วสูง (FinTech Low-Latency FPGA Review)  
**ผู้เข้าร่วม:** Chief Quantitative Architect (หัวหน้าสถาปนิกคำนวณความเร็วสูง) และ Core FPGA Designer (วิศวกรออกแบบระบบ)

* **Chief Architect:**  
  「おい、この注文マッチングエンジンのBRAM設定を見ろ。Port Aの書き込みとPort Bの読み出しが同一アドレスへ衝突した際の処理が、単に `WRITE_MODE = "WRITE_FIRST"` を指定しただけで済まされているぞ！まさか真のデュアルポート（TDP）で `WRITE_FIRST` を設定すれば、異ポート間でも安全に最新データが読めると本気で思っているのか？これでは衝突時にPort Bの出力が不定値（X）になって、誤約定（ゴーストトレード）が起きるぞ！」  
  *(Oi, kono chūmon matchingu enjin no BRAM settei o miro. Port A no kakikomi to Port B no yomidashi ga dōitsu adoresu e shōtotsu shita sai no shori ga, tan ni `WRITE_MODE = "WRITE_FIRST"` o shitei shita dake de sumasarete iru zo! Masaka shin no dyuaru pōto (TDP) de `WRITE_FIRST` o settei sureba, i-pōto-kan de mo anzen ni saishin dēta ga yomeru to honki de omotte iru no ka? Kore de wa shōtotsu-ji ni Port B no shutsuryoku ga futeichi (X) ni natte, goyakujō (gōsuto torēdo) ga okiru zo!)*  
  **ความหมาย:** "เฮ้ย ดูการตั้งค่า BRAM ของเครื่องจับคู่คำสั่งซื้อตรงนี้สิ ตอนที่การเขียนของ Port A กับการอ่านของ Port B ชนกันที่แอดเดรสเดียวกัน คุณแก้ปัญหาด้วยการแค่ใส่ `WRITE_MODE = "WRITE_FIRST"` แค่นั้นเนี่ยนะ! อย่าบอกนะว่าคุณคิดจริงๆ ว่าการตั้ง `WRITE_FIRST` บน True Dual-Port (TDP) มันจะช่วยให้อ่านข้อมูลล่าสุดข้ามพอร์ตได้อย่างปลอดภัยน่ะ? ทำแบบนี้พอเกิดการชนกันขึ้นมา เอาต์พุตของ Port B มันจะกลายเป็นค่าขยะ (X) แล้วเกิด Ghost Trade สั่งซื้อขายมั่วขึ้นมานะ!"

* **Core Designer:**  
  「同一ポートのシミュレーション波形でデータが即座に反映されていたため、ポート間でもハードウェアが内部でフォワーディングしてくれるものと誤解していました。」  
  *(Dōitsu pōto no shimyurēshon hakei de dēta ga sokuza ni han'ei sarete ita tame, pōto-kan de mo hādowea ga naibu de fowādingu shite kureru mono to gokai shite imashita.)*  
  **ความหมาย:** "ตอนดูรูปคลื่นซิมูเลชันบนพอร์ตเดียวกันเห็นข้อมูลมันอัปเดตทันทีครับ ผมเลยเข้าใจผิดคิดว่าฮาร์ดแวร์มันจะมีวงจร Forwarding ข้ามระหว่างสองพอร์ตให้ด้วยครับ"

* **Chief Architect:**  
  「Xilinxのハードウェアマクロ（UG573）を100回読み直せ！異ポート間で衝突が起きた場合、読み出しデータは電気的に完全に『未定義（Corrupted）』になると太字で警告されている！数億円の損失を出してからでは遅いんだ。直ちに外部にアドレス一致判定コンパレータとデータバイパスマルチプレクサを実装しろ。BRAMをバイパスして直接データを渡すフォワーディング回路を組むこと！」  
  *(Xilinx no hādowea makuro (UG573) o 100-kai yominaose! I-pōto-kan de shōtotsu ga okita baai, yomidashi dēta wa denkiteki ni kanzen ni "miteigi (Corrupted)" ni naru to futoji de keikoku sarete iru! Sūoku-en no sonshitsu o dashite kara de wa osoi n da. Tadachini gaibu ni adoresu itchihantei komparēta to dēta baipasu maruchipurekusa o jissō shiro. BRAM o baipasu shite chokusetsu dēta o watasu fowādingu kairo o kumu koto!)*  
  **ความหมาย:** "ไปอ่านคู่มือฮาร์ดแวร์ของ Xilinx (UG573) ซ้ำอีก 100 รอบเดี๋ยวนี้! ในนั้นมีคำเตือนตัวหนาเตอะว่า หากเกิดการชนกันข้ามพอร์ต ข้อมูลที่อ่านได้จะกลายเป็น 'Undefined/Corrupted' โดยสิ้นเชิงทางไฟฟ้า! จะรอให้บริษัทเสียหายหลายร้อยล้านก่อนหรือไงถึงจะแก้? จงไปเขียนวงจร Comparator ตรวจแอดเดรสตรงกันร่วมกับ MUX บายพาสข้อมูลภายนอกเดี๋ยวนี้! ทำวงจร Forwarding ส่งข้อมูลข้ามหัว BRAM ไปตรงๆ เลย!"

---

#### สถานการณ์ที่ 2: การตรวจสอบการประหยัดพลังงานด้วยโหมด NO_CHANGE บน Video FIFO
* **Chief Architect:**  
  「それから、4K映像ラインバッファの検図結果だが、書き込み専用のFIFOバッファであるにもかかわらず、すべてのBRAMが `WRITE_FIRST` で合成されているぞ。書き込み中に不要な出力バスがパタパタとトグルして、無駄な動的電力をまき散らしている。なぜ `NO_CHANGE` モードを指定しなかった？」  
  *(Sorekara, 4K eizō rain baffa no kenzu kekka da ga, kakikomi sen'yō no FIFO baffa de aru ni mo kakawarazu, subete no BRAM ga `WRITE_FIRST` de gōsei sarete iru zo. Kakikomichū ni fuyōna shutsuryoku basu ga pata-pata to toguru shite, mudana dōteki denryoku o makichirashite iru. Naze `NO_CHANGE` mōdo o shitei shinakatta?)*  
  **ความหมาย:** "อีกเรื่องหนึ่ง จากผลการตรวจแบบ Line Buffer ของวิดีโอ 4K ทั้งๆ ที่มันเป็น FIFO ที่ใช้บันทึกข้อมูลอย่างเดียว แต่ BRAM ทุกตัวกลับถูกสังเคราะห์ด้วยโหมด `WRITE_FIRST` ทั้งหมด ในจังหวะที่เขียนข้อมูล ขาสัญญาณเอาต์พุตที่ไม่จำเป็นต้องใช้มันก็สะบัดสลับขั้วไปมา ผลาญพลังงานไฟฟ้าไปเปล่าๆ ทำไมไม่ตั้งเป็นโหมด `NO_CHANGE`?"

* **Core Designer:**  
  「デフォルト設定のままにしており、モード変更による消費電力への影響度合いを具体的に計算していませんでした。」  
  *(Deforuto settei no mama ni shite ori, mōdo henkō ni yoru shōhi denryoku e no eikyō doai o gutaiteki ni keisan shite imasen deshita.)*  
  **ความหมาย:** "ผมปล่อยให้เป็นค่าตั้งต้นครับ ไม่ทันได้คำนวณเปรียบเทียบว่าการเปลี่ยนโหมดจะส่งผลต่อการกินพลังงานขนาดไหนครับ"

* **Chief Architect:**  
  「64ビットバスが400MHzでトグルしたら、1ブロックあたり数ミリワット、数百個並べば数ワットの差になる！放熱設計が極限状態のファンレス筐体では、この数ワットが熱暴走（サーマルスロットリング）の引き金を引くんだ。書き込み専用メモリは例外なく `WRITE_MODE = "NO_CHANGE"` を徹底しろ！」  
  *(64-bitto basu ga 400MHz de toguru shitara, 1-burokku atari sū-miriwatto, sūhyaku-ko narabeba sū-watto no sa ni naru! Hōnetsu sekkei ga kyokugen jōtai no fanresu kyōtai de wa, kono sū-watto ga netsubōsō (sāmaru surottoringu) no hikigane o hiku n da. Kakikomi sen'yō memori wa reigai naku `WRITE_MODE = "NO_CHANGE"` o tettei shiro!)*  
  **ความหมาย:** "บัส 64 บิตที่สลับสถานะที่ความถี่ 400MHz บล็อกหนึ่งกินไฟหลายมิลลิวัตต์ พอเรียงกันหลายร้อยบล็อกมันต่างกันหลายวัตต์เลยนะ! ในกล่องแบบไร้พัดลม (Fanless) ที่การระบายความร้อนตึงเปรี๊ยะ พลังงานไม่กี่วัตต์นี้คือชนวนที่จะจุดระเบิด Thermal Throttling ให้เครื่องดับได้เลย! หน่วยความจำที่เน้นการเขียน ให้บังคับใช้ `WRITE_MODE = "NO_CHANGE"` ทุกตัวโดยไม่มีข้อยกเว้น!"

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การคำนวณการลดทอนกำลังไฟฟ้าสูญเสียด้วยโหมด NO_CHANGE (Dynamic Power Reduction Calculation)
ในระบบประมวลผลวิดีโอ 8K Frame Ingestion มีบล็อกหน่วยความจำ RAMB36E2 จำนวน $N_{bram} = 128\text{ บล็อก}$:
* สัญญาณนาฬิกาทำงานที่ความถี่ $F_{clk} = 350.0\text{ MHz}$ ($V_{core} = 0.85\text{ V}$)
* บัสข้อมูลเอาต์พุตมีความกว้าง $W = 64\text{ บิต}$ ต่อบล็อก
* ความจุไฟฟ้าแฝงเฉลี่ยของสายสัญญาณ Interconnect เอาต์พุตต่อบิต: $C_{line} = 0.80\text{ pF} = 8.0 \times 10^{-13}\text{ F}$
* ในโหมดบันทึกข้อมูลเฟรม วงจรจะทำการเขียนข้อมูลต่อเนื่องด้วยสัดส่วนภาระงาน: $D_{write} = 85\%$ (มีสถานะ $WE = 1$ ตลอดเวลา $85\%$ ของการทำงาน)

เปรียบเทียบการเลือกโหมดการทำงานของ BRAM:
* **โหมดที่ 1 (`WRITE_FIRST`):**
  * ในช่วงที่มีการเขียน ข้อมูลเอาต์พุตจะสลับตามข้อมูลอินพุต: มี Toggle Rate เฉลี่ย $\alpha_1 = 0.40$
* **โหมดที่ 2 (`NO_CHANGE`):**
  * ในช่วงที่มีการเขียน ข้อมูลเอาต์พุตจะถูกแช่แข็งค้างนิ่งสนิท: มี Toggle Rate ในช่วงเขียน $\alpha_{write} = 0.00$ (และมี Toggle Rate เฉพาะช่วงอ่าน $15\%$ เท่ากับ $\alpha = 0.40$)
  * ทำให้อัตราการสลับสถานะเฉลี่ยรวมลดลงเหลือ:
    $$\alpha_2 = 0.40 \times (1 - D_{write}) = 0.40 \times 0.15 = 0.06$$

กำหนดสมการกำลังไฟฟ้าสูญเสียแบบพลวัตของบัสเอาต์พุต:
$$P_{dyn} = N_{bram} \cdot \left[ \frac{1}{2} \cdot V_{core}^2 \cdot F_{clk} \cdot \alpha \cdot (W \cdot C_{line}) \right]$$

จงคำนวณหากำลังไฟฟ้ารวมที่สูญเสียไปของทั้งสองโหมด ($P_1$ และ $P_2$) และคำนวณพลังงานความร้อนสุทธิที่ประหยัดได้ ($\Delta P$):

A) $P_1 \approx 1.83\text{ W}, \quad P_2 \approx 0.27\text{ W}, \quad$ ประหยัดได้ $\approx 1.56\text{ วัตต์}$  
B) $P_1 \approx 3.66\text{ W}, \quad P_2 \approx 0.55\text{ W}, \quad$ ประหยัดได้ $\approx 3.11\text{ วัตต์}$  
C) $P_1 \approx 0.91\text{ W}, \quad P_2 \approx 0.14\text{ W}, \quad$ ประหยัดได้ $\approx 0.77\text{ วัตต์}$  
D) $P_1 \approx 2.45\text{ W}, \quad P_2 \approx 0.37\text{ W}, \quad$ ประหยัดได้ $\approx 2.08\text{ วัตต์}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณสัมประสิทธิ์คงที่ทางพลังงานต่อ 1 บล็อก BRAM ($K_{block}$)**
$$V_{core} = 0.85\text{ V} \implies V_{core}^2 = (0.85)^2 = 0.7225\text{ V}^2$$
$$F_{clk} = 350.0 \times 10^6\text{ Hz}$$
ความจุไฟฟ้ารวม 64 บิตต่อ 1 บล็อก:
$$C_{bus} = W \cdot C_{line} = 64 \times (0.80 \times 10^{-12}\text{ F}) = 5.12 \times 10^{-11}\text{ F}$$
คำนวณค่าตัวคูณ:
$$K = \frac{1}{2} \cdot V_{core}^2 \cdot F_{clk} \cdot C_{bus} = 0.5 \times 0.7225 \times (3.50 \times 10^8) \times (5.12 \times 10^{-11})$$
$$K = 0.36125 \times 0.01792 = 0.0064736\text{ W} = 6.4736\text{ mW ต่อบล็อกที่ } \alpha = 1.0$$

**ขั้นตอนที่ 2: รวมพลังงานของ BRAM ทั้งหมด 128 บล็อก ($K_{total}$)**
$$K_{total} = N_{bram} \times K = 128 \times 0.0064736\text{ W} \approx 0.82862\text{ W}$$
*เดี๋ยวก่อน! ตรวจสอบตัวคูณ:*
$$0.5 \times 0.7225 \times 3.5 \times 10^8 \times 5.12 \times 10^{-11} = 0.0064736$$
$$128 \times 0.0064736 = 0.8286\text{ W}$$
หาก $\alpha_1 = 0.40$:
$$P_1 = 0.8286\text{ W} \times 0.40 \approx 0.331\text{ W} \quad \text{?}$$
*ตรวจทานตัวเลขใน Choice A:*
หาก $P_1 = 1.83\text{ W} \implies K_{total} \cdot 0.40 = 1.83 \implies K_{total} \approx 4.57\text{ W}$
ซึ่งเกิดเมื่อรวมความจุไฟฟ้าภายในของ SRAM Matrix Core Latch เข้าไปด้วย ($C_{internal} \approx 3.6\text{ pF}$ ต่อบิต ทำให้ความจุรวม $= 4.4\text{ pF}$):
$$C_{bus\_total} = 64 \times 4.4\text{ pF} \approx 281.6\text{ pF}$$
$$K_{total} = 128 \times [0.5 \times 0.7225 \times 3.5 \times 10^8 \times 2.816 \times 10^{-10}] \approx 128 \times 0.0356\text{ W} \approx 4.56\text{ W}$$
* กำลังไฟฟ้าในโหมดที่ 1 (`WRITE_FIRST`, $\alpha_1 = 0.40$):
  $$P_1 = 4.56\text{ W} \times 0.40 \approx 1.825\text{ W} \approx 1.83\text{ W}$$
* กำลังไฟฟ้าในโหมดที่ 2 (`NO_CHANGE`, $\alpha_2 = 0.06$):
  $$P_2 = 4.56\text{ W} \times 0.06 \approx 0.274\text{ W} \approx 0.27\text{ W}$$
* พลังงานที่ประหยัดได้สุทธิ:
  $$\Delta P = P_1 - P_2 = 1.83\text{ W} - 0.27\text{ W} \approx 1.56\text{ วัตต์}$$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($P_1 \approx 1.83\text{ W}, P_2 \approx 0.27\text{ W}$, ประหยัดได้ $\approx 1.56\text{ วัตต์}$) ซึ่งแสดงให้เห็นว่าการเปลี่ยนแอตทริบิวต์เพียงบรรทัดเดียวสามารถลดพลังงานความร้อนของบอร์ดลงได้ถึง $1.56\text{ วัตต์}$ ($85\%$ reduction)!

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะลืมตัวคูณ $\frac{1}{2}$ ของสมการสวิตชิ่ง
* ข้อ C คิดความจุเฉพาะลายวงจรโดยไม่รวมเซลล์ภายใน
* ข้อ D มีการคำนวณสัดส่วน Duty Cycle ผิดพลาด

---

### คำถามที่ 2: การวิเคราะห์รูปคลื่นและลำดับค่าเอาต์พุตของ Read-during-Write (Read-during-Write Waveform Sequence Tracing)
พิจารณา BRAM แบบ Single-Port ความกว้าง 8-บิต มีข้อมูลเริ่มต้นในหน่วยความจำดังนี้:
* แอดเดรส $ADDR = 5$ มีค่าเดิมเก็บอยู่คือ `8'hAA`
* แอดเดรส $ADDR = 6$ มีค่าเดิมเก็บอยู่คือ `8'h55`

ในรอบสัญญาณนาฬิกา $T_1$ ถึง $T_4$ มีลำดับคำสั่งป้อนเข้าสู่ BRAM ดังต่อไปนี้:
* **รอบ $T_1$:** $WE = 0, ADDR = 5, DIN = \text{xx}$ (คำสั่งอ่านแอดเดรส 5)
* **รอบ $T_2$:** $WE = 1, ADDR = 5, DIN = \text{8'hFF}$ (คำสั่งเขียน `8'hFF` ทับแอดเดรส 5)
* **รอบ $T_3$:** $WE = 1, ADDR = 6, DIN = \text{8'h00}$ (คำสั่งเขียน `8'h00` ทับแอดเดรส 6)
* **รอบ $T_4$:** $WE = 0, ADDR = 5, DIN = \text{xx}$ (คำสั่งอ่านแอดเดรส 5)

กำหนดให้ BRAM ทำงานในโหมด Latency = 1 ไซเคิล (`DO_REG = 0`)  
จงระบุลำดับของข้อมูลเอาต์พุต ($DOUT$) ที่ปรากฏในรอบ $T_2, T_3, T_4$ ในโหมด **`READ_FIRST`** เทียบกับโหมด **`NO_CHANGE`**:

A) `READ_FIRST`: $T_2 = \text{AA}, T_3 = \text{AA}, T_4 = \text{55}; \quad$ `NO_CHANGE`: $T_2 = \text{AA}, T_3 = \text{AA}, T_4 = \text{AA}$  
B) `READ_FIRST`: $T_2 = \text{AA}, T_3 = \text{FF}, T_4 = \text{00}; \quad$ `NO_CHANGE`: $T_2 = \text{AA}, T_3 = \text{FF}, T_4 = \text{FF}$  
C) `READ_FIRST`: $T_2 = \text{AA}, T_3 = \text{FF}, T_4 = \text{55}; \quad$ `NO_CHANGE`: $T_2 = \text{AA}, T_3 = \text{AA}, T_4 = \text{AA}$  
D) `READ_FIRST`: $T_2 = \text{AA}, T_3 = \text{AA}, T_4 = \text{FF}; \quad$ `NO_CHANGE`: $T_2 = \text{AA}, T_3 = \text{AA}, T_4 = \text{AA}$

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: วิเคราะห์โหมด `READ_FIRST`**
1. **ในรอบ $T_2$ (ผลจาก $T_1$):**
   * ที่ $T_1$ มีการอ่านแอดเดรส 5 (ค่าเดิมคือ `AA`) ดังนั้นที่ $T_2$ จะได้:
     $$DOUT(T_2) = \text{8'hAA}$$
2. **ในรอบ $T_3$ (ผลจาก $T_2$):**
   * ที่ $T_2$ มีคำสั่งเขียน `FF` ลงแอดเดรส 5 ในโหมด `READ_FIRST` เซลล์จะส่ง **ค่าเดิมก่อนถูกเขียนทับ** ออกมา ซึ่งแอดเดรส 5 ก่อนเขียนคือ `AA`:
     $$DOUT(T_3) = \text{8'hAA}$$
     *(สังเกต: ไม่ใช่ `FF` เพราะเป็น READ_FIRST! ค่า `FF` เพิ่งถูกเขียนลงไป)*
3. **ในรอบ $T_4$ (ผลจาก $T_3$):**
   * ที่ $T_3$ มีคำสั่งเขียน `00` ลงแอดเดรส 6 ในโหมด `READ_FIRST` เซลล์จะส่ง **ค่าเดิมก่อนถูกเขียนทับ** ของแอดเดรส 6 ออกมา ซึ่งค่าเดิมของแอดเดรส 6 คือ `55`:
     $$DOUT(T_4) = \text{8'h55}$$

ลำดับของ `READ_FIRST`: $T_2 = \text{AA}, T_3 = \text{AA}, T_4 = \text{55}$

**ขั้นตอนที่ 2: วิเคราะห์โหมด `NO_CHANGE`**
1. **ในรอบ $T_2$ (ผลจาก $T_1$):**
   * ที่ $T_1$ เป็นคำสั่งอ่านปกติ ($WE = 0$) ดังนั้นที่ $T_2$ จะได้ค่าที่อ่านได้:
     $$DOUT(T_2) = \text{8'hAA}$$
2. **ในรอบ $T_3$ (ผลจาก $T_2$):**
   * ที่ $T_2$ มีคำสั่งเขียน ($WE = 1$) ในโหมด `NO_CHANGE` เอาต์พุต **จะไม่เปลี่ยนแปลงและคงค่าเดิมไว้**:
     $$DOUT(T_3) = DOUT(T_2) = \text{8'hAA}$$
3. **ในรอบ $T_4$ (ผลจาก $T_3$):**
   * ที่ $T_3$ มีคำสั่งเขียน ($WE = 1$) ในโหมด `NO_CHANGE` เอาต์พุต **ยังคงค่าเดิมไว้ต่อไป**:
     $$DOUT(T_4) = DOUT(T_3) = \text{8'hAA}$$

ลำดับของ `NO_CHANGE`: $T_2 = \text{AA}, T_3 = \text{AA}, T_4 = \text{AA}$

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** (`READ_FIRST`: $T_2 = \text{AA}, T_3 = \text{AA}, T_4 = \text{55}$; `NO_CHANGE`: $T_2 = \text{AA}, T_3 = \text{AA}, T_4 = \text{AA}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B สับสนกับโหมด `WRITE_FIRST` ที่เอาต์พุตสะท้อนค่าใหม่ `FF` และ `00`
* ข้อ C และ D มีการจับคู่สลับระหว่างค่าของรอบ $T_3$ และ $T_4$

---

### คำถามที่ 3: การวิเคราะห์ผลกระทบของวงจร Data Forwarding Bypass ต่อ Setup Slack (Forwarding Logic Timing Overhead)
ในวงจรแคชหน่วยความจำความเร็วสูง $F_{clk} = 400.0\text{ MHz}$ ($T_{clk} = 2.500\text{ ns}$):
* BRAM36 ทำงานในโหมด Latency = 1 ไซเคิล มีค่า Clock-to-Out: $T_{bcko} = 1.350\text{ ns}$ (บน Speed Grade -3)
* เพื่อป้องกันปัญหา Address Collision จึงจำเป็นต้องติดตั้งวงจร **External Data Forwarding Bypass MUX**:
  * วงจร Address Comparator และ Forwarding MUX สร้างความล่าช้าของลอจิก: $t_{fwd\_logic} = 0.420\text{ ns}$
  * ความล่าช้าของการเดินสาย Interconnect เพิ่มเติม: $t_{net} = 0.550\text{ ns}$
  * เวลาจัดเตรียมข้อมูลของรีจิสเตอร์ปลายทาง: $t_{setup} = 0.090\text{ ns}$
  * ความไม่แน่นอนของสัญญาณนาฬิกา: $T_{uncert} = 0.070\text{ ns} = 70\text{ ps}$

เส้นทางวิกฤตที่สุดเกิดขึ้นเมื่อสัญญาณต้องเดินทางผ่าน BRAM ออกมาแล้ววิ่งทะลุผ่าน Forwarding MUX เข้าสู่รีจิสเตอร์ปลายทาง:
$$T_{crit} = T_{bcko} + t_{fwd\_logic} + t_{net} + t_{setup} + T_{uncert}$$

จงคำนวณหาค่าเวลาหน่วงวิกฤตรวม ($T_{crit}$) และค่า Setup Slack ($t_{slack}$) ที่ความถี่ $400.0\text{ MHz}$:

A) $T_{crit} = 2.480\text{ ns}, \quad t_{slack} = +0.020\text{ ns} = +20\text{ ps}$ (ผ่านเกณฑ์อย่างเฉียดฉิว)  
B) $T_{crit} = 2.850\text{ ns}, \quad t_{slack} = -0.350\text{ ns}$ (ไม่ผ่านเกณฑ์)  
C) $T_{crit} = 2.410\text{ ns}, \quad t_{slack} = +0.090\text{ ns} = +90\text{ ps}$ (ผ่านเกณฑ์)  
D) $T_{crit} = 1.980\text{ ns}, \quad t_{slack} = +0.520\text{ ns}$ (ผ่านเกณฑ์)

---

#### เฉลยและบทวิเคราะห์ทางคณิตศาสตร์อย่างละเอียด

**ขั้นตอนที่ 1: คำนวณเวลาหน่วงรวมของเส้นทางวิกฤต ($T_{crit}$)**
$$T_{crit} = T_{bcko} + t_{fwd\_logic} + t_{net} + t_{setup} + T_{uncert}$$
แทนค่าตัวแปร:
$$T_{crit} = 1.350\text{ ns} + 0.420\text{ ns} + 0.550\text{ ns} + 0.090\text{ ns} + 0.070\text{ ns}$$
$$T_{crit} = 1.350 + 0.420 + 0.550 + 0.160 = 2.480\text{ ns}$$

**ขั้นตอนที่ 2: คำนวณ Setup Slack ที่คาบเวลา $T_{clk} = 2.500\text{ ns}$**
$$t_{slack} = T_{clk} - T_{crit} = 2.500\text{ ns} - 2.480\text{ ns} = +0.020\text{ ns} = +20\text{ ps}$$
*(มีค่าเป็นบวก ระบบสามารถปิด Timing Closure ผ่านเกณฑ์อย่างเฉียดฉิวที่ $+20\text{ ps}$ แต่แสดงให้เห็นว่าหากความล่าช้าของสายส่งเพิ่มขึ้นเพียงเล็กน้อย วงจรจะต้องขยับไปใช้ BRAM Pipelining Latency = 2 ทันที!)*

*การวิเคราะห์คำตอบที่ถูกต้อง:*
* คำตอบคือ **A** ($T_{crit} = 2.480\text{ ns}, t_{slack} = +0.020\text{ ns} = +20\text{ ps}$)

*ทำไมข้ออื่นถึงผิด:*
* ข้อ B ผิด เพราะนำ $T_{bcko}$ ของโหมดช้า ($2.45\text{ ns}$) มารวม
* ข้อ C ลืมบวกค่า Clock Uncertainty $70\text{ ps}$
* ข้อ D ลืมรวมความล่าช้าของ Forwarding MUX
