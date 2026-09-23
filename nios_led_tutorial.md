# Tutorial: การสร้าง Custom Avalon-MM LED IP สำหรับ Nios II บน Platform Designer (QSys)

บทเรียนนี้จะสอนการสร้าง Custom IP ของตัวเอง เพื่อไปเชื่อมต่อกับโปรเซสเซอร์ Nios II ผ่านบัส **Avalon Memory-Mapped (Avalon-MM)** บนระบบ Altera/Intel FPGA และการเขียนโปรแกรมภาษา C เพื่อควบคุมสัญญาณเอาต์พุตครับ

---

## 📌 ภาพรวมสถาปัตยกรรม (System Architecture)
ระบบนี้ประกอบด้วย:
1. **Nios II Processor** (Soft Core CPU)
2. **On-Chip Memory** (RAM เก็บโปรแกรม)
3. **JTAG UART** (สำหรับ Print ข้อความ Debug ออกทางคอมพิวเตอร์)
4. **Custom LED IP** (ที่เราจะสร้างขึ้นมาเอง โดยเชื่อมต่อผ่าน Avalon-MM Slave)

---

## 🛠️ Step 1: เขียนโค้ด VHDL สำหรับ Custom LED IP
หัวใจสำคัญของตัวเก็บสถานะ LED คือ เราจะใช้รีจิสเตอร์ในการจำค่าการเปิด-ปิดไฟ
เรามีความต้องการให้ Register Map ทำงานที่ระดับ **Byte Offset** ดังนี้:
* `Address 0x0` $\rightarrow$ ควบคุม LED 0 (รีจิสเตอร์ตัวที่ 0)
* `Address 0x4` $\rightarrow$ ควบคุม LED 1 (รีจิสเตอร์ตัวที่ 1)
* `Address 0x8` $\rightarrow$ ควบคุม LED 2 (รีจิสเตอร์ตัวที่ 2)
* `Address 0xC` $\rightarrow$ ควบคุม LED 3 (รีจิสเตอร์ตัวที่ 3)

### ⚠️ เรื่องสำคัญ: Word Address vs Byte Address
ในระบบ Nios II (CPU): จะมองรีจิสเตอร์ที่ขนาด 32 บิต ห่างกันทีละ 4 Bytes (Byte-addressable) ได้แก่ `0x0`, `0x4`, `0x8`, `0xC`
แต่ในมุมมองของ **Avalon-MM Slave Port** ใน VHDL: สัญญาณ `address` จะส่งเข้ามาเป็น **Word Address** (นับจำนวนคำขนาด 32 บิต)
ดังนั้น สัญญาณ `address(1 downto 0)` ขนาด 2 บิตใน VHDL จะรับค่าดังนี้:
* `address = "00"` $\rightarrow$ แทนตำแหน่ง Byte Offset `0x0`
* `address = "01"` $\rightarrow$ แทนตำแหน่ง Byte Offset `0x4`
* `address = "10"` $\rightarrow$ แทนตำแหน่ง Byte Offset `0x8`
* `address = "11"` $\rightarrow$ แทนตำแหน่ง Byte Offset `0xC`

### 💻 โค้ด VHDL: `simple_led_avalon.vhd`

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity simple_led_avalon is
    port (
        -- システム基本信号
        clk           : in std_logic;
        reset_n       : in std_logic; -- Avalon標準のアクティブ・ロー・リセット
        
        -- Avalon-MM スレーブ・インターフェース信号
        avl_address   : in std_logic_vector(1 downto 0);  -- 4つのレジスタを選択可能
        avl_read      : in std_logic;                     -- リード要求信号 (アクティブ・ハイ)
        avl_write     : in std_logic;                     -- ライト要求信号 (アクティブ・ハイ)
        avl_writedata : in std_logic_vector(31 downto 0); -- ライトデータ入力
        avl_readdata  : out std_logic_vector(31 downto 0);-- リードデータ出力
        
        -- FPGA外部出力用のハードウェアピン
        led_outputs   : out std_logic_vector(3 downto 0)  -- 4個 of LEDへの出力ピン
    );
end entity;

architecture rtl of simple_led_avalon is
    -- LEDの状態を保持する32ビットレジスタ4個を定義
    type reg_array is array(0 to 3) of std_logic_vector(31 downto 0);
    signal led_regs : reg_array;
    
begin
    -- 1. レジスタへの書き込み処理 (ライト・プロセス)
    process(clk)
    begin
        if rising_edge(clk) then
            if reset_n = '0' then
                -- 初期化時にすべてのLEDを消灯 (0クリア)
                led_regs(0) <= (others => '0');
                led_regs(1) <= (others => '0');
                led_regs(2) <= (others => '0');
                led_regs(3) <= (others => '0');
            else
                -- ライト要求があれば、指定アドレスのレジスタに書き込み
                if avl_write = '1' then
                    led_regs(to_integer(unsigned(avl_address))) <= avl_writedata;
                end if;
            end if;
        end if;
    end process;
    
    -- 2. レジスタからの読み出し処理 (リード・プロセス - 組み合わせ回路)
    -- リード要求 (avl_read) があるときのみデータを出力し、それ以外は0を出力 (低消費電力・ノイズ防止)
    avl_readdata <= led_regs(to_integer(unsigned(avl_address))) when avl_read = '1' else (others => '0');
    
    -- 3. 各レジスタのビット0を実際のLEDピンに出力
    led_outputs(0) <= led_regs(0)(0); -- アドレス0x0 (LED0) のビット0
    led_outputs(1) <= led_regs(1)(0); -- アドレス0x4 (LED1) のビット0
    led_outputs(2) <= led_regs(2)(0); -- アドレス0x8 (LED2) のビット0
    led_outputs(3) <= led_regs(3)(0); -- アドレス0xC (LED3) のビット0
    
end architecture;
```

---

## 📦 Step 2: สร้าง Custom IP ใน Platform Designer (QSys)

เมื่อเราเขียน VHDL ตัวนี้เสร็จแล้ว ให้เปิดโปรแกรม Platform Designer (หรือ QSys เดิม) แล้วทำตามขั้นตอนนี้เพื่อแพ็คเกจไอพี:

1. คลิกที่ **File -> New Component...** เพื่อเปิดหน้าต่าง Component Editor
2. ในแถบ **Files** $\rightarrow$ เพิ่มไฟล์ `simple_led_avalon.vhd` เข้ามา แล้วกด **Analyze Synthesis Files** เพื่อให้ระบบตรวจสอบความถูกต้องทาง Syntax
3. ในแถบ **Signals** $\rightarrow$ กำหนด Interface Type ให้สัญญาณต่างๆ:
   * `clk` $\rightarrow$ **Clock Input**
   * `reset_n` $\rightarrow$ **Reset Input** (เลือก `Associated Clock` ให้เป็น `clk`)
   * `avl_address`, `avl_read`, `avl_write`, `avl_writedata`, `avl_readdata` $\rightarrow$ **Avalon Memory Mapped Slave** (เลือก `Associated Clock` เป็น `clk` และ `Associated Reset` เป็น `reset_n`)
   * `led_outputs` $\rightarrow$ **Conduit** (สำหรับส่งออกสัญญาณไปข้างนอกบอร์ด)
4. ในแถบ **Interfaces** $\rightarrow$ ตรวจสอบชื่อขาและการแมป ให้แน่ใจว่าไม่มี Error แจ้งเตือนสีแดง
5. กด **Finish** เพื่อบันทึกไฟล์ไอพี (มันจะได้ไฟล์ชื่อ `simple_led_avalon_hw.tcl` โผล่ขึ้นมาในโปรเจกต์)

---

## 🔌 Step 3: ประกอบระบบใน Platform Designer

1. ดึงคอมโพเนนต์เหล่านี้เข้ามาในโปรเจกต์ QSys:
   * **Nios II Processor** (เช่น Nios II/e หรือ Nios II/f)
   * **On-Chip Memory (RAM)** (กำหนดขนาด 32KB หรือตามพื้นที่แรมบนชิป)
   * **JTAG UART** (สำหรับปริ้นต์คุยใน Console)
   * **Simple LED IP** (ไอพีที่เราเพิ่งทำเสร็จ จะอยู่ในหมวดหมู่ด้านซ้ายล่าง)
2. **การเชื่อมต่อบัส (Bus Connections):**
   * เชื่อมต่อ `clk` และ `reset` ของทุกตัวเข้าด้วยกัน
   * เชื่อม `Nios II Data Master` เข้ากับ `On-Chip Memory Slave`, `JTAG UART Slave` และ `Simple LED IP Slave`
   * เชื่อม `Nios II Instruction Master` เข้ากับ `On-Chip Memory Slave` เท่านั้น (เนื่องจาก CPU จะอ่านชุดคำสั่งจากแรม)
3. **กำหนด Base Address:** 
   * กด **System -> Assign Base Addresses** เพื่อให้ระบุแอดเดรสอัตโนมัติ 
   * สมมติว่า Custom LED ของเราได้แอดเดรสเริ่มต้นที่: `0x00041000` (ตัวแปร Base Address ในซอฟต์แวร์จะเป็น `SIMPLE_LED_AVALON_0_BASE`)
4. กด **Generate HDL...** เพื่อนำโค้ดระบบทั้งหมดไปต่อกับโปรเจกต์ Quartus และคอมไพล์บอร์ดต่อไป

---

## 💻 Step 4: เขียน Nios II C Software ควบคุม LED

หลังจากออกแบบฮาร์ดแวร์เสร็จและ Gen BSP (Board Support Package) แล้ว คุณจะได้ไฟล์ `system.h` ซึ่งบันทึก Base Address ของฮาร์ดแวร์เอาไว้ ในฝั่งซอฟต์แวร์ C เราจะควบคุม LED โดยเข้าถึงแอดเดรสโดยตรงครับ

### 💡 วิธีเข้าถึงหน่วยความจำ (Direct Register Access)
ใน Nios II Software Build Tools (SBT) จะมีไลบรารีชื่อ `<io.h>` ที่จัดเตรียมฟังก์ชัน/มาโครในการเขียนและอ่านหน่วยความจำโดยเฉพาะ:
* `IOWR_32DIRECT(BASE, OFFSET, DATA)` : เขียนข้อมูลขนาด 32 บิต ลงใน Base address ที่ระบุ Offset (นับหน่วยเป็น Byte)
* `IORD_32DIRECT(BASE, OFFSET)` : อ่านข้อมูลขนาด 32 บิต จาก Base address และ Offset

### 💻 โค้ดภาษา C: `main.c`

```c
#include <stdio.h>
#include <unistd.h>      // 遅延処理用のusleep関数
#include "system.h"      // ベースアドレス定義ヘッダ
#include "io.h"          // レジスタ直叩き用I/Oマクロ

// カスタムIPのベースアドレス設定
// (Platform Designerで自動生成されたsystem.hของ定数を流用)
#define LED_BASE SIMPLE_LED_AVALON_0_BASE

// VHDL設計に基づいたバイトオフセット値
#define OFFSET_LED0 0x0
#define OFFSET_LED1 0x4
#define OFFSET_LED2 0x8
#define OFFSET_LED3 0xC

int main()
{
    printf("Nios II Custom LED Control Started!\n");
    
    // 起動時にすべてのLEDを消灯
    IOWR_32DIRECT(LED_BASE, OFFSET_LED0, 0);
    IOWR_32DIRECT(LED_BASE, OFFSET_LED1, 0);
    IOWR_32DIRECT(LED_BASE, OFFSET_LED2, 0);
    IOWR_32DIRECT(LED_BASE, OFFSET_LED3, 0);
    
    while(1)
    {
        // 1. LEDを順番に点灯（LED0 -> LED1 -> LED2 -> LED3）
        printf("LED chasing sequence started...\n");
        
        IOWR_32DIRECT(LED_BASE, OFFSET_LED0, 1); // LED0点灯
        usleep(500000); // 500ms遅延（デバッグ用に見やすく設定）
        IOWR_32DIRECT(LED_BASE, OFFSET_LED0, 0); // LED0消灯
        
        IOWR_32DIRECT(LED_BASE, OFFSET_LED1, 1); // LED1点灯
        usleep(500000); // 500ms遅延
        IOWR_32DIRECT(LED_BASE, OFFSET_LED1, 0); // LED1消灯
        
        IOWR_32DIRECT(LED_BASE, OFFSET_LED2, 1); // LED2点灯
        usleep(500000); // 500ms遅延
        IOWR_32DIRECT(LED_BASE, OFFSET_LED2, 0); // LED2消灯
        
        IOWR_32DIRECT(LED_BASE, OFFSET_LED3, 1); // LED3点灯
        usleep(500000); // 500ms遅延
        IOWR_32DIRECT(LED_BASE, OFFSET_LED3, 0); // LED3消灯
        
        usleep(1000000); // 次のシーケンス開始まで1秒待機
    }
    
    return 0;
}
```

---

## 🇯🇵 ภาษาญี่ปุ่นวันละคำในโปรเจกต์ FPGA
* **レジスタマップ** (Rejisuta Mappu) = Register Map (แผนผังระบุตำแหน่งรีจิสเตอร์และออฟเซ็ต)
* **カスタムIP** (Kasutamu IP) = Custom IP (โมดูลที่เราประดิษฐ์ขึ้นมาเอง)
* **ワードアドレス** (Wādo Adoresu) = Word Address / แอดเดรสระดับคำ
* **バイトアドレス** (Baito Adoresu) = Byte Address / แอดเดรสระดับไบต์
