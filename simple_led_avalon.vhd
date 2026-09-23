library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity simple_led_avalon is
    port (
        -- システム基本信号
        clk           : in std_logic;
        reset_n       : in std_logic; -- Avalon標準のアクティブ・ロー・リセット
        
        -- Avalon-MM スレーブ・インターフェース信号
        avl_address   : in std_logic_vector(7 downto 0);  -- 4つのレジスタを選択可能
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
    -- 1. レジスタへの書き込み処理 (ライト・プロセス - 同期回路)
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
