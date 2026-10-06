# Lesson 192: FPGA Testbench Part 2 — SystemVerilog OOP & UVM Foundations (พื้นฐานการเขียนเทสต์เบนช์เชิงวัตถุด้วย SystemVerilog OOP และระเบียบวิธี UVM)

---

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

เมื่อการออกแบบระบบบนชิป (System-on-Chip: SoC) และ FPGA มีความซับซ้อนระดับหลายสิบล้านเกต การเขียน Testbench แบบดั้งเดิมโดยใช้ `module` และ `initial` block แบบ Static จะก่อให้เกิดปัญหาหนี้ทางเทคนิค (Technical Debt) มหาศาล: โค้ดไม่สามารถนำกลับมาใช้ซ้ำได้ (Non-reusable), การขยายฟังก์ชันทำได้ยาก, และการจำลองสถานการณ์คู่ขนาน (Multi-Agent Concurrency) จะเกิดความสับสนวุ่นวาย

วงการเซมิคอนดักเตอร์ระดับโลกจึงพัฒนามาตรฐาน **Universal Verification Methodology (UVM - IEEE 1800.2)** ซึ่งสร้างขึ้นบนพื้นฐานการเขียนโปรแกรมเชิงวัตถุ (Object-Oriented Programming: OOP) ของภาษา SystemVerilog เพื่อแยกสถาปัตยกรรมการทดสอบออกเป็นเลเยอร์ที่ชัดเจนและเป็นอิสระต่อกัน (Decoupled & Layered Architecture)

```
+--------------------------------------------------------------------------------------------------+
|                            UVM COMPONENT HIERARCHY & TLM DATA FLOW                              |
+--------------------------------------------------------------------------------------------------+
                                                                                                    
                                           uvm_test                                                 
                                              |                                                     
                                              v                                                     
                                           uvm_env                                                  
                      +-----------------------------------------------+                             
                      |                                               |                             
                      v                                               v                             
                 uvm_agent (Active)                              uvm_scoreboard                     
    +-----------------------------------------+             +----------------------+                
    |                                         |             |                      |                
    |   uvm_sequencer                         |             |                      |                
    |        | (Sequence Item)                |             |                      |                
    |        v                                |             |                      |                
    |   uvm_driver                            |             |                      |                
    |        | (Pin Toggling via              |             |                      |                
    |        |  Virtual Interface)            |             |                      |                
    |        v                                |             |                      |                
    |   [DUT PINS]                            |             |                      |                
    |        ^                                |             |                      |                
    |        | (Pin Sampling)                 |             |                      |                
    |   uvm_monitor                           |             |                      |                
    |        | (TLM Packet)                   |             |                      |                
    |        +--- uvm_analysis_port --------->|============>|   uvm_analysis_imp   |                
    |                                         |             |                      |                
    +-----------------------------------------+             +----------------------+                
```

---

### 1.1 วงจรชีวิตของ UVM และกลไก Phase Execution Mechanics

ความพิเศษของ UVM อยู่ที่การแบ่งขั้นตอนการทำงานของโปรแกรมออกเป็น **Phases** ที่มีลำดับแน่นอน เพื่อแก้ปัญหาการเริ่มต้นทำงานก่อนหลัง (Race Conditions during Initialization):

1. **Build Phases (ทำงานที่เวลา $t = 0$, เป็นฟังก์ชัน ไม่กินเวลา / Non-time-consuming):**
   - `build_phase`: สร้างออบเจกต์ของคอมโพเนนต์จากบนลงล่าง (**Top-Down Hierarchy Construction**)
   - `connect_phase`: เชื่อมต่อสายสัญญาณและพอร์ต TLM จากล่างขึ้นบน (**Bottom-Up TLM Binding**)
   - `end_of_elaboration_phase`: ตรวจสอบความถูกต้องของการเชื่อมต่อและปรับแต่งคอนฟิก
2. **Run Phases (ทำงานที่เวลา $t \ge 0$, เป็นงานที่กินเวลา / Time-consuming `task`):**
   - `run_phase`: เธรดหลักที่ขับเคลื่อนสัญญาณนาฬิกา, สร้างทรานแซกชัน, และสังเกตสัญญาณพิน
   - ขับเคลื่อนด้วยกลไก **Objection Mechanism** (`phase.raise_objection(this)` และ `phase.drop_objection(this)`): การทดสอบจะดำเนินต่อไปตราบใดที่ยังมี Objection ค้างอยู่ และจะยุติลงทันทีเมื่อ Objection เป็นศูนย์ทั้งหมด
3. **Clean-up Phases (ทำงานที่เวลาสิ้นสุด, ไม่กินเวลา):**
   - `extract_phase`: ดึงข้อมูลสถิติจากโมเดล
   - `check_phase`: ตรวจสอบว่ามีข้อมูลตกค้างในคิวหรือไม่
   - `report_phase`: พิมพ์รายงานสรุป Pass/Fail

#### 1. TLM Transaction Throughput Math
การสื่อสารระหว่าง Driver, Monitor, และ Scoreboard ไม่ใช้สายสัญญาณจริง แต่ใช้ **Transaction-Level Modeling (TLM 1.0/2.0)**  
ความเร็วในการส่งผ่านข้อมูลของระบบทดสอบขึ้นอยู่กับรอบเวลาของ Transaction ($T_{trans}$):
$$T_{trans} = \sum_{i=1}^{N_{phases}} t_{phase\_i} + \Delta_{protocol\_overhead}$$
โดยมีอัตราการบริโภคหน่วยความจำ (Memory Footprint) สัมพันธ์กับจำนวนทรานแซกชันที่คงค้างใน Analysis FIFO ($N_{inflight}$):
$$Mem_{usage} = N_{inflight} \times \text{sizeof}(uvm\_sequence\_item) + Mem_{base\_env}$$
หาก Scoreboard ไม่ทำการล้าง Transaction ทิ้งหลังเปรียบเทียบ จะเกิดปัญหา Memory Leak ที่ทำให้ Simulator เกิด Out-of-Memory (OOM) Crash

---

### 1.2 Virtual Interface และการเชื่อมโยง Class กับ Hardware Module

เนื่องจาก Class ใน SystemVerilog เป็น Dynamic Memory Object (สร้างและทำลายได้ใน Heap) แต่โมดูล RTL บนฮาร์ดแวร์เป็น Static Entity ที่สังเคราะห์ขึ้นในซิลิคอน การที่ Class จะสามารถสั่งขยับสัญญาณพินของฮาร์ดแวร์ได้โดยตรงจึงต้องอาศัยตัวกลางที่เรียกว่า **Virtual Interface**:

$$\text{Class (Driver/Monitor)} \xrightarrow{\text{virtual interface}} \text{Interface Instance} \xrightarrow{\text{wire/logic}} \text{DUT (RTL)}$$

การลงทะเบียนและส่งต่อ Interface นิยามผ่านฐานข้อมูลคอนฟิกส่วนกลาง **UVM Configuration Database (`uvm_config_db`)**:
```systemverilog
// ฝั่ง Top-Level Module (Static)
uvm_config_db#(virtual axi_if)::set(null, "uvm_test_top.env.agent*", "vif", intf);

// ฝั่ง Driver Component (Dynamic)
uvm_config_db#(virtual axi_if)::get(this, "", "vif", vif);
```

---

### 1.3 RTL & SystemVerilog Code: Class-Based OOP Testbench Architecture

โค้ดชุดนี้แสดงสถาปัตยกรรม OOP ตามหลักการ UVM อย่างแท้จริง โดยจำลองคอมโพเนนต์ Sequencer, Driver, Monitor, Scoreboard, และ Agent เชื่อมโยงผ่าน Virtual Interface

```systemverilog
//=============================================================================
// Module: tb_oop_uvm_foundation
// Description: Pure SystemVerilog Class-Based OOP Verification Architecture
// Standards: IEEE 1800 SystemVerilog / IEEE 1800.2 UVM Methodology
//=============================================================================

`timescale 1ns / 1ps

//-----------------------------------------------------------------------------
// 1. Hardware Interface Definition with Clocking Block
//-----------------------------------------------------------------------------
interface packet_bus_if (input logic clk);
    logic        rst_n;
    logic        valid;
    logic        ready;
    logic [7:0]  data;
    logic        sop; // Start of Packet
    logic        eop; // End of Packet

    // Clocking block for Driver
    clocking drv_cb @(posedge clk);
        default input #1step output #1ns;
        output valid, data, sop, eop;
        input  ready;
    endclocking

    // Clocking block for Monitor
    clocking mon_cb @(posedge clk);
        default input #1step output #1ns;
        input valid, ready, data, sop, eop;
    endclocking

    modport DRV (clocking drv_cb, output rst_n);
    modport MON (clocking mon_cb, input rst_n);
endinterface

//-----------------------------------------------------------------------------
// 2. Transaction Sequence Item Class
//-----------------------------------------------------------------------------
class PacketItem;
    rand bit [7:0] payload[];
    rand int       packet_len;
    rand int       inter_packet_delay;

    // Constraints for protocol compliance
    constraint c_len {
        packet_len inside {[4:16]};
        payload.size() == packet_len;
    }

    constraint c_delay {
        inter_packet_delay inside {[0:5]};
    }

    function void print(string name = "PacketItem");
        $write("[%0t ns][%s] Len=%0d | Bytes: ", $time, name, packet_len);
        foreach (payload[i]) $write("%02h ", payload[i]);
        $display("");
    endfunction
endclass

//-----------------------------------------------------------------------------
// 3. Driver Component
//-----------------------------------------------------------------------------
class PacketDriver;
    virtual packet_bus_if.DRV vif;
    mailbox #(PacketItem)     drv_mbx;

    function new(virtual packet_bus_if.DRV vif, mailbox #(PacketItem) drv_mbx);
        this.vif = vif;
        this.drv_mbx = drv_mbx;
    endfunction

    task run();
        PacketItem item;
        // Initial bus state
        vif.drv_cb.valid <= 1'b0;
        vif.drv_cb.sop   <= 1'b0;
        vif.drv_cb.eop   <= 1'b0;
        vif.drv_cb.data  <= 8'h00;

        forever begin
            drv_mbx.get(item);

            // Wait for inter-packet delay
            repeat (item.inter_packet_delay) @(vif.drv_cb);

            // Drive packet payload byte by byte
            for (int i = 0; i < item.packet_len; i++) begin
                vif.drv_cb.valid <= 1'b1;
                vif.drv_cb.data  <= item.payload[i];
                vif.drv_cb.sop   <= (i == 0);
                vif.drv_cb.eop   <= (i == item.packet_len - 1);

                // Wait for Handshake (Ready)
                do begin
                    @(vif.drv_cb);
                end while (!vif.drv_cb.ready);
            end

            // Idle after packet
            vif.drv_cb.valid <= 1'b0;
            vif.drv_cb.sop   <= 1'b0;
            vif.drv_cb.eop   <= 1'b0;
        end
    endtask
endclass

//-----------------------------------------------------------------------------
// 4. Monitor Component
//-----------------------------------------------------------------------------
class PacketMonitor;
    virtual packet_bus_if.MON vif;
    mailbox #(PacketItem)     mon_mbx;

    function new(virtual packet_bus_if.MON vif, mailbox #(PacketItem) mon_mbx);
        this.vif = vif;
        this.mon_mbx = mon_mbx;
    endfunction

    task run();
        PacketItem item;
        bit [7:0] byte_stream[$];

        forever begin
            @(vif.mon_cb);
            if (vif.mon_cb.valid && vif.mon_cb.ready) begin
                byte_stream.push_back(vif.mon_cb.data);

                if (vif.mon_cb.eop) begin
                    item = new();
                    item.packet_len = byte_stream.size();
                    item.payload = new[item.packet_len];
                    for (int i = 0; i < item.packet_len; i++) begin
                        item.payload[i] = byte_stream.pop_front();
                    end
                    mon_mbx.put(item);
                end
            end
        end
    endtask
endclass

//-----------------------------------------------------------------------------
// 5. Scoreboard Component
//-----------------------------------------------------------------------------
class PacketScoreboard;
    mailbox #(PacketItem) exp_mbx;
    mailbox #(PacketItem) act_mbx;
    int match_count = 0;
    int mismatch_count = 0;

    function new(mailbox #(PacketItem) exp_mbx, mailbox #(PacketItem) act_mbx);
        this.exp_mbx = exp_mbx;
        this.act_mbx = act_mbx;
    endfunction

    task run();
        PacketItem exp_item, act_item;
        forever begin
            exp_mbx.get(exp_item);
            act_mbx.get(act_item);

            // Compare lengths
            if (exp_item.packet_len != act_item.packet_len) begin
                $error("[SCOREBOARD] Length Mismatch! Exp=%0d, Act=%0d", 
                       exp_item.packet_len, act_item.packet_len);
                mismatch_count++;
                continue;
            end

            // Compare payload bytes
            begin
                bit pass = 1'b1;
                for (int i = 0; i < exp_item.packet_len; i++) begin
                    if (exp_item.payload[i] !== act_item.payload[i]) begin
                        $error("[SCOREBOARD] Byte[%0d] Mismatch! Exp=0x%02h, Act=0x%02h", 
                               i, exp_item.payload[i], act_item.payload[i]);
                        pass = 1'b0;
                        mismatch_count++;
                        break;
                    end
                end
                if (pass) match_count++;
            end
        end
    endtask
endclass

//-----------------------------------------------------------------------------
// 6. Device Under Test (DUT: Packet Skid Buffer Loopback with Inversion)
//-----------------------------------------------------------------------------
module packet_lut_dut (
    input  logic       clk,
    input  logic       rst_n,
    input  logic       valid_in,
    output logic       ready_in,
    input  logic [7:0] data_in,
    input  logic       sop_in,
    input  logic       eop_in,
    output logic       valid_out,
    input  logic       ready_out,
    output logic [7:0] data_out,
    output logic       sop_out,
    output logic       eop_out
);
    // Simple 1-stage registered pipeline
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_out <= 1'b0;
            data_out  <= 8'h00;
            sop_out   <= 1'b0;
            eop_out   <= 1'b0;
        end else if (ready_out) begin
            valid_out <= valid_in;
            data_out  <= data_in; // Inverted or direct data
            sop_out   <= sop_in;
            eop_out   <= eop_in;
        end
    end
    assign ready_in = ready_out;
endmodule

//-----------------------------------------------------------------------------
// 7. Top-Level Testbench Module (Orchestrator)
//-----------------------------------------------------------------------------
module tb_oop_uvm_foundation;
    logic clk;
    initial clk = 0;
    always #5 clk = ~clk; // 100 MHz

    packet_bus_if in_if(clk);
    packet_bus_if out_if(clk);

    // DUT Instantiation
    packet_lut_dut dut (
        .clk       (clk),
        .rst_n     (in_if.rst_n),
        .valid_in  (in_if.drv_cb.valid),
        .ready_in  (in_if.ready),
        .data_in   (in_if.drv_cb.data),
        .sop_in    (in_if.drv_cb.sop),
        .eop_in    (in_if.drv_cb.eop),
        .valid_out (out_if.valid),
        .ready_out (out_if.drv_cb.ready),
        .data_out  (out_if.data),
        .sop_out   (out_if.sop),
        .eop_out   (out_if.eop)
    );

    // Environment Queues
    mailbox #(PacketItem) gen2drv_mbx = new(10);
    mailbox #(PacketItem) gen2scb_mbx = new(10);
    mailbox #(PacketItem) mon2scb_mbx = new(10);

    // Class Instances
    PacketDriver     drv;
    PacketMonitor    mon;
    PacketScoreboard scb;

    // Ready signal generation for output port
    always_ff @(posedge clk) begin
        out_if.drv_cb.ready <= 1'b1; // Always ready to sink
    end

    initial begin
        $display("=== STARTING OBJECT-ORIENTED VERIFICATION RUN ===");
        
        // Instantiate OOP Components
        drv = new(in_if.DRV, gen2drv_mbx);
        mon = new(out_if.MON, mon2scb_mbx);
        scb = new(gen2scb_mbx, mon2scb_mbx);

        // Reset Sequence
        in_if.rst_n = 1'b0;
        #20 in_if.rst_n = 1'b1;
        #10;

        // Fork Execution Threads
        fork
            drv.run();
            mon.run();
            scb.run();
        join_none

        // Generate Packets
        for (int p = 0; p < 50; p++) begin
            PacketItem pkt = new();
            void'(pkt.randomize());
            gen2drv_mbx.put(pkt);
            gen2scb_mbx.put(pkt);
        end

        // Wait for pipeline drain
        #5000;

        // Final Report
        $display("\n=================================================");
        $display("          OOP UVM SUMMARY REPORT                ");
        $display("=================================================");
        $display("  Matched Packets   : %0d", scb.match_count);
        $display("  Mismatched Packets: %0d", scb.mismatch_count);
        $display("=================================================");

        if (scb.mismatch_count == 0 && scb.match_count == 50) begin
            $display("[PASS] OOP Verification Complete with 100%% Precision!");
            $finish(0);
        end else begin
            $fatal(1, "[FAIL] Test completed with errors!");
        end
    end
endmodule
```

---

## 2. ทริคหน้างาน OJT แบบ Step-by-Step (現場の実践テクニック)

### กรณีศึกษาความเสียหายจริงในภาคสนาม (失敗事例 - Shippai Jirei)
**ตัวควบคุมสวิตช์ใยแก้วนำแสงความเร็วสูง 100GbE (Data Center Optical Switch ASIC)** ประสบปัญหาร้ายแรงในการใช้งานจริงที่ศูนย์ข้อมูลคลาวด์: เมื่อเกิดสภาวะโหลดทราฟฟิกหนาแน่นสูงเป็นพิเศษ ชิปเริ่มทำการส่งแพ็กเก็ตข้ามพอร์ตผิดเส้นทาง (Port Misrouting Hazard) ส่งผลให้ทราฟฟิกระดับเพตาไบต์กระจายไปผิดเซิร์ฟเวอร์จนระบบเครือข่ายล่มทั้งโซน ความเสียหายจากการหยุดชะงักของบริการและการผลิตชิปใหม่ (Mask Respin Cost) รวมมูลค่ากว่า 2.2 ล้านดอลลาร์สหรัฐ

---

### การวิเคราะห์หาสาเหตุรากเหง้า (5 Whys Root Cause Analysis)

1. **ทำไมสวิตช์จึงส่งแพ็กเก็ตข้ามพอร์ตผิดเส้นทางเมื่อโหลดสูง?**
   - *คำตอบ:* ตรรกะควบคุม Priority-based Flow Control (PFC / IEEE 802.1Qbb) ไม่ตอบสนองต่อเฟรม Pause บางประเภทในช่องทางเสมือน (Virtual Channel 3)
2. **ทำไมตรรกะควบคุม PFC จึงไม่ตอบสนองต่อเฟรม Pause ในแชนเนลนั้น?**
   - *คำตอบ:* โค้ด RTL มีการถอดรหัสรหัสคำสั่ง (Opcode) ตกหล่นไป 1 บิตในกรณีที่แพ็กเก็ตมีขนาดยาวกว่าปกติ
3. **ทำไม Testbench ก่อนการ Tape-out จึงตรวจไม่พบบักนี้?**
   - *คำตอบ:* ทีมวิศวกรใช้ Testbench แบบ Script โบราณแยกกันในแต่ละบล็อกย่อย โดยไม่มีการสร้าง **Reusable UVM Verification IP (VIP)** ทำให้เมื่อรวมบล็อกเข้าด้วยกันในระดับ Top-Level ไม่มี Agent ตัวใดที่สามารถสร้างสถานการณ์ผสมผสานระหว่าง Max-Length Packet กับ Pause Frame ได้อย่างสมบูรณ์
4. **ทำไมจึงไม่ใช้ UVM Architecture ตั้งแต่ต้น?**
   - *คำตอบ:* ทีมวิศวกรขาดความชำนาญด้าน SystemVerilog OOP มองว่าการเขียน Class, Interface และ Phase Management เสียเวลาในการเริ่มต้นโครงการ จึงเลือกทางลัดด้วยการเขียน Verilog Tasks ธรรมดา
5. **ทำไมกระบวนการตรวจแบบ (Kenzu) จึงปล่อยให้การออกแบบหลุดไปได้?**
   - *คำตอบ:* ผู้บริหารโครงการประนีประนอมกับเกณฑ์การตรวจสอบสถาปัตยกรรม Verification โดยขาดการบังคับใช้ **Standard UVM Architecture Audit Gate**

---

### แผนผังสาเหตุและผล (Ishikawa Fishbone Diagram)

```
==================================================================================================
                                    ISHIKAWA FISHBONE CAUSE-EFFECT DIAGRAM
==================================================================================================

   MAN (บุคลากร)                                   MACHINE / TOOLS (เครื่องมือ)
   ----------------                                ---------------------------
   ขาดทักษะขั้นสูงด้าน SystemVerilog OOP           ไม่มี UVM Verification IP (VIP) มาตรฐาน
   เลี่ยงการเขียน Class เพราะคิดว่าเสียเวลา         Simulator ไม่ได้เปิดใช้งาน Assertion Binding
               \                                                /
                \                                              /
                 \                                            /
                  +------------------------------------------+
                  |                                          |
                  |  100GbE SWITCH CHIP RESPIN DISASTER      | ===>> [2.2M USD RESPIN LOSS]
                  |                                          |
                  +------------------------------------------+
                 /                                            \
                /                                              \
   METHOD (ระเบียบปฏิบัติ)                          MATERIAL / ENVIRONMENT (สภาวะแวดล้อม)
   ----------------------                          -------------------------------------
   ขาด UVM Architecture Review Gate                 สภาวะทราฟฟิกศูนย์ข้อมูลพุ่งสูงฉับพลัน
   ใช้ Script-based Testbench แบบบล็อกต่อบล็อก      PFC Pause Frame เกิดชนกับ Jumbo Frame
==================================================================================================
```

---

### คู่มือปฏิบัติการตรวจสอบ OJT หน้างาน: กฎเหล็กในการวางโครงสร้าง UVM Testbench

1. **Rule 1: การห้ามอ้างอิงลำดับชั้นฮาร์ดแวร์โดยตรงในคลาส (Strict Decoupling via Virtual Interface)**
   - ห้ามเขียน Path แบบ Hierarchical เช่น `dut.u_fifo.wr_ptr` ภายใน Class เด็ดขาด
   - ทุกการเข้าถึงสัญญาณจริง ต้องผ่าน `virtual interface` หรือ SystemVerilog DPI เท่านั้น เพื่อรักษา Reusability
2. **Rule 2: การป้องกัน Objection Leak ที่ทำให้ Simulation ค้าง (No-Leak Objection Policy)**
   - ทุกครั้งที่เรียก `phase.raise_objection(this)` ต้องจับคู่อย่างระมัดระวังกับ `phase.drop_objection(this)`
   - ครอบบล็อกการทำงานด้วยโครงสร้าง Safe Pattern เสมอ:
     ```systemverilog
     task run_phase(uvm_phase phase);
         phase.raise_objection(this);
         // ทำงานทดสอบ...
         phase.drop_objection(this);
     endtask
     ```
3. **Rule 3: การแบ่งแยกหน้าที่ชัดเจนระหว่าง Driver และ Monitor (Separation of Concerns)**
   - **Driver:** มีหน้าที่เพียง "กระทำ" (Drive) สัญญาณตาม Sequence Item ห้ามวิเคราะห์หรือตัดสินผลความถูกต้อง
   - **Monitor:** มีหน้าที่เพียง "สังเกต" (Passive Sample) และส่งต่อผ่าน Analysis Port ห้ามแก้ไขสัญญาณใดๆ บนบัส

---

## 3. คำศัพท์และประโยคภาษาญี่ปุ่นสำหรับตรวจแบบ (検図 - Kenzu)

### 3.1 คำศัพท์เทคนิคเฉพาะทาง (専門用語)

| คันจิ (Kanji) | คานะ (Kana) | โรมาจิ (Romaji) | ภาษาไทย / อังกฤษ | บริบทการใช้งานเชิงวิศวกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **オブジェクト指向検証** | オブジェクトしこうけんしょう | Obujekuto Shikou Kenshou | Object-Oriented Verification | การตรวจสอบวงจรดิจิทัลด้วยเทคนิคเชิงวัตถุ |
| **仮想インタフェース** | かそうインタフェース | Kasou Intafeesu | Virtual Interface | ตัวกลางเชื่อมโยงระหว่าง Class เชิงตรรกะกับพินฮาร์ดแวร์ |
| **異議申し立て** | いぎもうしたて | Igi Moushitate | Objection Mechanism | กลไกควบคุมการคงอยู่หรือยุติการจำลองใน UVM Phase |
| **再利用性** | さいりようせい | Sairiyousei | Reusability | ความสามารถในการนำคอมโพเนนต์หรือ VIP กลับมาใช้ซ้ำ |
| **分析ポート** | ぶんせきポート | Bunseki Pooto | Analysis Port (TLM) | พอร์ตส่งผ่านข้อมูลการวิเคราะห์แบบ One-to-Many |
| **多態性** | たたいせい | Tataisei | Polymorphism | การสืบทอดและแปรสภาพพฤติกรรมของคลาสทดสอบ |
| **階層構造** | かいそうこうぞう | Kaisou Kouzou | Hierarchical Structure | โครงสร้างลำดับชั้นของ Component Tree ใน UVM |

---

### 3.2 บทสนทนาในห้องตรวจแบบจริง (検図審議 - Kenzu Shingi)

**สถานที่:** ห้องประชุมสถาปัตยกรรมซิลิคอน (ASIC Architecture Verification Gate)  
**ผู้เข้าร่วม:**
- **ฟูจิโมโตะ (藤本):** Principal Verification Director (検証統括部長)
- **สิทธิชัย (シッティチャイ):** Senior Testbench Architect (設計担当)

---

**藤本部長 (ฟูจิโมโตะ):**  
「シッティチャイさん、次世代スイッチASICの検証環境のクラス図を確認しました。UVMの導入は進んでいるようですが、Driverの中に直接プロトコルのチェッカーロジックが埋め込まれているのはどういうことですか？これでは**関心の分離（Separation of Concerns）**が破綻していますよ。」  
*(คุณสิทธิชัยครับ ผมตรวจสอบ Class Diagram ของสภาพแวดล้อมการทดสอบสวิตช์ ASIC รุ่นถัดไปแล้ว ดูเหมือนจะนำ UVM เข้ามาใช้ แต่ทำไมใน Driver ถึงมี Checker Logic ของโปรโตคอลฝังอยู่โดยตรงล่ะครับ? แบบนี้หลักการ Separation of Concerns ก็พังทลายหมดสิครับ)*

**シッティチャイ (สิทธิชัย):**  
「藤本部長、Driver内で送信エラーをその場で検知した方がデバッグしやすいと考え、簡易的に判定ロジックを入れてしまいました。」  
*(ผู้อำนวยการฟูจิโมโตะครับ ผมคิดว่าถ้าให้ Driver ตรวจพบ Error ในจังหวะส่งได้ทันทีจะทำให้ดีบักง่ายขึ้น เลยใส่ลอจิกตัดสินผลแบบย่อเข้าไปครับ)*

**藤本部長 (ฟูจิโมโตะ):**  
「それではUVMの**再利用性（Reusability）**が台無しです！Driverはシーケンスを受け取ってピンを叩くことだけに専念すべきです。受信データの整合性監視はすべて受動的な**Monitor（受動モニタ）**がサンプリングし、**Analysis Port**を経由してScoreboardにブロードキャストするのが鉄則です。この構成では、将来ブロックをPassive AgentとしてSoC統合環境に流用した瞬間に破綻します。」  
*(ทำแบบนั้น Reusability ของ UVM ก็พังหมดสิครับ! หน้าที่ของ Driver มีเพียงรับ Sequence แล้วขับสัญญาณที่พินเท่านั้น ส่วนการตรวจสอบความถูกต้องของข้อมูลทั้งหมด ต้องปล่อยให้ Monitor แบบ Passive เป็นตัวสุ่มจับสัญญาณ แล้วบรอดแคสต์ผ่าน Analysis Port ไปยัง Scoreboard นี่คือกฎเหล็กครับ หากทำแบบเดิม พอในอนาคตเรายกบล็อกนี้ไปใช้เป็น Passive Agent ในระดับ SoC เมื่อไหร่ ระบบจะพังทันที)*

**シッティチャイ (สิทธิชัย):**  
「ご指導感謝いたします。すぐにDriverからチェッカーロジックを分離し、MonitorとScoreboard間のTLMポート接続にリファクタリングします。また、`uvm_config_db`を用いた仮想インタフェースのバインドも厳格に見直します。」  
*(ขอบพระคุณสำหรับคำชี้แนะอย่างยิ่งครับ ผมจะแยก Checker Logic ออกจาก Driver ทันที และ Refactor เป็นการเชื่อมต่อ TLM Port ระหว่าง Monitor และ Scoreboard ให้ถูกต้อง พร้อมทั้งทบทวนการผูก Virtual Interface ผ่าน `uvm_config_db` ให้เข้มงวดตามมาตรฐานครับ)*

**藤本部長 (ฟูจิโมโตะ):**  
「うむ。それから、`run_phase`での**異議申し立て（Objection）**の解除漏れがないか、タイムアウト監視タイマーとの連動も必ず確認してください。夜間リグレッションテストがハングアップして全エンジニアの作業を止めることだけは絶対に許されませんからね。」  
*(อืม ดีมาก แล้วก็ตรวจเช็คด้วยว่าใน `run_phase` ไม่มีการตกหล่นของการปลด Objection โดยต้องประสานงานกับตัวจับเวลา Watchdog เสมอ การที่ Regression Test รอบกลางคืนเกิดค้างจนทำให้งานของวิศวกรทั้งแผนกต้องหยุดชะงัก เป็นเรื่องที่ยอมรับไม่ได้เด็ดขาดครับ)*

---

## 4. ควิซวิเคราะห์ปัญหาระดับวิศวกรอาวุโส (上級技術クイズ)

### คำถามที่ 1: การจัดการ UVM Phase Deadlock จากปัญหา Objection Leakage

พิจารณาโค้ด UVM Component ต่อไปนี้ที่รันอยู่ใน `run_phase`:
```systemverilog
task run_phase(uvm_phase phase);
    PacketItem item;
    phase.raise_objection(this);
    fork
        begin
            forever begin
                seq_item_port.get_next_item(item);
                drive_item(item);
                seq_item_port.item_done();
            end
        end
        begin
            #10000;
            phase.drop_objection(this);
        end
    join_any
endtask
```
หากนำคอมโพเนนต์นี้ไปรันในระบบ Regression Test ขนาดใหญ่ ผลลัพธ์ทางวิศวกรรมข้อใดต่อไปนี้จะเกิดขึ้นอย่างแน่นอนเมื่อเวลาจำลองผ่านไปเกิน $10,000\text{ ns}$?

- **A)** การทดสอบจะยุติลงอย่างสมบูรณ์ที่ $10,000\text{ ns}$ และรายงาน Pass
- **B)** Simulation จะเกิดสภาวะ Infinite Loop และ Hang ตลอดกาล เพราะเธรด `forever` ภายใน `fork` ยังคงทำงานอยู่
- **C)** การทดสอบจะเข้าสู่ `check_phase` ได้สำเร็จ แต่เกิด Memory Overflow
- **D)** `seq_item_port` จะส่งค่า Null และทำให้เกิด Fatal Crash ทันทีที่ $10,000\text{ ns}$

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: A) การทดสอบจะยุติลงอย่างสมบูรณ์ที่ $10,000\text{ ns}$ และรายงาน Pass**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ในระเบียบวิธี UVM กลไกการคงอยู่ของ `run_phase` ถูกควบคุมโดย **Objection Mechanism** แต่เพียงผู้เดียว
2. เมื่อ `phase.raise_objection(this)` ถูกเรียก เคาน์เตอร์ Objection รวมของระบบจะมีค่า $C_{obj} \ge 1$
3. เมื่อเวลาผ่านไป $10,000\text{ ns}$ เธรดที่สองทำงานเสร็จและเรียก `phase.drop_objection(this)`
4. หากไม่มีคอมโพเนนต์อื่นในระบบถือครอง Objection อยู่ เคาน์เตอร์จะลดลงเหลือ $C_{obj} = 0$
5. เมื่อเคาน์เตอร์ Objection กลายเป็นศูนย์ UVM Phase Controller จะดำเนินการ:
   - บังคับสั่งยุติ `run_phase` ของทุกคอมโพเนนต์ทันที (Kill all remaining background threads under run_phase)
   - นำระบบก้าวเข้าสู่ขั้นตอน `extract_phase`, `check_phase`, และ `report_phase` ตามลำดับชั้น
6. ดังนั้น แม้ว่าเธรดแรกจะมีลูป `forever` ค้างอยู่ เธรดนั้นจะถูก UVM Kernel สั่ง Terminate โดยอัตโนมัติ การทดสอบจึงไม่เกิดอาการแฮงก์

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ B ผิด:** ลูป `forever` ไม่สามารถป้องกันการเปลี่ยนเฟสได้ เพราะสิทธิ์ขาดในการจบคอนโทรลเลอร์อยู่ที่ Objection Counter
- **ข้อ C ผิด:** การทำงานเปลี่ยนเฟสปกติ ไม่ได้ทำให้เกิด Memory Overflow
- **ข้อ D ผิด:** `get_next_item` เป็นบล็อกกิ้งทาสก์ปกติ เมื่อเฟสถูกตัดจบ เธรดจะหยุด ไม่ได้คืนค่า Null ออกมาสร้างข้อผิดพลาด

---

### คำถามที่ 2: ความแตกต่างในการเชื่อมโยงพอร์ต TLM Analysis Port แบบ Broadcast (1-to-Many Fanout)

ในสถาปัตยกรรม UVM หาก Monitor ของโปรโตคอล PCIe มีการส่งออกทรานแซกชันผ่าน `uvm_analysis_port #(pcie_packet) ap;`  
และในสภาพแวดล้อมมีการเชื่อมต่อพอร์ตนี้ไปยังคอมโพเนนต์ปลายทาง 3 ตัวพร้อมกัน ได้แก่:
1. `uvm_scoreboard` (เพื่อตรวจสอบความถูกต้องของข้อมูล)
2. `pcie_coverage_collector` (เพื่อบันทึก Functional Coverage)
3. `pcie_performance_tracker` (เพื่อคำนวณ Bandwidth Latency)

หาก Scoreboard ดำเนินการปรับแก้ค่าฟิลด์ภายใน Transaction Object เช่น:
```systemverilog
function void write(pcie_packet t);
    t.payload[0] = 8'hFF; // ทำการ Mask บิตแรกเพื่อการตรวจสอบ
endfunction
```
ผลกระทบเชิงระบบที่เกิดขึ้นกับคอมโพเนนต์ตัวอื่น (`coverage_collector` และ `performance_tracker`) คือข้อใด?

- **A)** ไม่ส่งผลกระทบใดๆ เพราะ UVM จะทำการคัดลอก Deep Copy ให้แต่ละคอมโพเนนต์โดยอัตโนมัติ
- **B)** เกิด Data Corruption ข้ามโมดูลทันที เพราะ TLM ส่งผ่านในรูปแบบ Object Handle (Reference Pointer) ทำให้ทุกโมดูลเห็นค่าที่ถูกดัดแปลงไปด้วย
- **C)** Simulator จะแจ้งข้อผิดพลาดระดับคอมไพล์ (Compile Error) ทันที
- **D)** พอร์ต Analysis Port จะหยุดส่งข้อมูลไปยังคอมโพเนนต์ที่เหลือ

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) เกิด Data Corruption ข้ามโมดูลทันที เพราะ TLM ส่งผ่านในรูปแบบ Object Handle (Reference Pointer) ทำให้ทุกโมดูลเห็นค่าที่ถูกดัดแปลงไปด้วย**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. ในภาษา SystemVerilog ตัวแปรประเภท Class เป็นเพียง **Handle (การชี้ไปยังแอดเดรสในหน่วยความจำ Heap)**
2. เมื่อ `uvm_analysis_port::write(t)` ทำงาน มันจะทำการเรียกฟังก์ชัน `write(t)` ของคอมโพเนนต์ปลายทางทั้งหมดแบบ Sequential โดยส่งผ่าน Handle ตัวเดียวกัน (Pass-by-Reference):
   $$\&t_{scoreboard} \equiv \&t_{coverage} \equiv \&t_{tracker} \equiv \&t_{monitor}$$
3. UVM **ไม่ได้ทำ Deep Copy** ให้โดยอัตโนมัติเนื่องจากต้องการประสิทธิภาพสูงสุดและประหยัดเวลา CPU
4. ดังนั้น หาก Scoreboard ดัดแปลงค่า `t.payload[0] = 8'hFF` ค่าในตัวแปรของ Coverage Collector และ Performance Tracker จะถูกเปลี่ยนตามไปด้วยทันที ส่งผลให้การเก็บ Coverage บิดเบือนไปจากความจริง
5. วิธีการแก้ไขระดับมาตรฐานคือ หากโมดูลใดต้องการแก้ไขข้อมูล ต้องสั่ง `$cast(t_clone, t.clone())` เพื่อสร้างสำเนาอิสระก่อนเสมอ

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** เป็นความเข้าใจผิดที่อันตรายมาก UVM TLM ไม่เคยทำ Deep Copy อัตโนมัติ
- **ข้อ C ผิด:** โค้ดนี้ถูกหลักไวยากรณ์ จึงคอมไพล์ผ่านปกติ แต่เกิด Runtime Semantic Bug
- **ข้อ D ผิด:** การส่งข้อมูลยังคงดำเนินต่อไปจนครบทุก Subscriber ในลิสต์

---

### คำถามที่ 3: การประเมินประสิทธิภาพเชิงคำนวณและ Memory Footprint ของ UVM Scoreboard

กำหนดระบบ UVM Testbench ที่ทำการทดสอบแพ็กเก็ต Ethernet 400GbE ที่มีอัตราส่งข้อมูล $500,000\text{ packets/sec}$ ในการทดสอบแบบเร่งความเร็ว  
- แต่ละ Transaction (`PacketItem`) กินพื้นที่หน่วยความจำเฉลี่ย: $S_{item} = 2.5\text{ KB}$ (รวม Metadata และ Dynamic Payload Array)  
- สภาพแวดล้อมรันบนเครื่องเซิร์ฟเวอร์จำลองที่มีขีดจำกัด RAM สำหรับโปรเซส Simulator: $RAM_{max} = 32\text{ GB}$  
- Base Simulator Memory Overhead (โหลดโมเดล RTL และ Netlist): $RAM_{base} = 8\text{ GB}$  
- หาก Monitor ผลักข้อมูลเข้า Scoreboard แต่ตัวเปรียบเทียบใน Scoreboard มีปัญหาความเร็วประมวลผลช้ากว่า ทำให้มี Transaction สะสมในคิวเฉลี่ยเพิ่มขึ้น $12,000\text{ packets}$ ต่อวินาที

จงคำนวณหาเวลาการจำลองสูงสุด ($t_{crash\_max}$) ก่อนที่โปรเซส Simulator จะเกิดสภาวะหน่วยความจำล้นและถูกระบบปฏิบัติการ Linux ฆ่าทิ้ง (**Out-of-Memory / OOM Killer Termination**):

- **A)** $t_{crash\_max} \approx 400$ วินาที ($\approx 6.67$ นาที)
- **B)** $t_{crash\_max} \approx 800$ วินาที ($\approx 13.33$ นาที)
- **C)** $t_{crash\_max} \approx 1,200$ วินาที ($\approx 20.00$ นาที)
- **D)** $t_{crash\_max} \approx 2,400$ วินาที ($\approx 40.00$ นาที)

---

#### เฉลยและคำอธิบายทางคณิตศาสตร์อย่างละเอียด

**คำตอบที่ถูกต้องคือ: B) $t_{crash\_max} \approx 800$ วินาที ($\approx 13.33$ นาที)**

**การคำนวณและบทพิสูจน์ทางวิศวกรรม:**
1. คำนวณปริมาณหน่วยความจำ RAM ที่เหลืออยู่ให้โปรเซสจัดสรรสำหรับ Transaction Object:
   $$RAM_{available} = RAM_{max} - RAM_{base} = 32\text{ GB} - 8\text{ GB} = 24\text{ GB}$$
   แปลงเป็นหน่วยกิโลไบต์ (KB):
   $$RAM_{available} = 24 \times 1024 \times 1024\text{ KB} = 25,165,824\text{ KB}$$
2. อัตราการสะสมของหน่วยความจำจาก Transaction คั่งค้างใน Scoreboard ต่อวินาที ($R_{leak}$):
   $$R_{leak} = \text{Leak Rate (packets/s)} \times S_{item} = 12,000 \times 2.5\text{ KB/s} = 30,000\text{ KB/s}$$
   (หรือเท่ากับ $30\text{ MB/s}$)
3. คำนวณหาเวลาจนกระทั่งหน่วยความจำเต็มพิกัด $24\text{ GB}$:
   $$t_{crash\_max} = \frac{RAM_{available}}{R_{leak}} = \frac{25,165,824\text{ KB}}{30,000\text{ KB/s}} \approx 838.86\text{ วินาที}$$
   เมื่อปัดเศษตามสมการจริงและการกระจายหน่วยความจำใน Heap Fragmentation (ประมาณ $5\%$) จะได้ค่าเวลาประมาณ **800 วินาที** หรือราว 13 นาทีครึ่ง

**การวิเคราะห์ตัวเลือกอื่น:**
- **ข้อ A ผิด:** $400$ วินาที เป็นการคิดบนฐานที่ว่า RAM ว่างเพียง $12\text{ GB}$
- **ข้อ C ผิด:** $1,200$ วินาที เกิดจากการคิด $RAM_{max} = 32\text{ GB}$ เต็มจำนวนโดยลืมหัก Base Overhead ออก
- **ข้อ D ผิด:** $2,400$ วินาที คำนวณอัตราการรั่วไหลต่ำกว่าความเป็นจริงเท่าตัว
