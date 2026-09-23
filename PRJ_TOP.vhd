library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- =========================================================================
-- プロジェクトの最上位モジュール (Project Top-Level Entity)
-- =========================================================================
entity PRJ_TOP is
    port (
        -- FPGA外部ピン宣言 (実際の基板の物理ピンにマッピングするポート)
        fpga_clk      : in  std_logic;                    -- 外部クロック入力 (例: 50MHzオシレータ)
        fpga_reset_n  : in  std_logic;                    -- 外部リセット入力 (例: プッシュボタン)
        fpga_leds     : out std_logic_vector(3 downto 0)  -- 外部LEDピンへの出力 (4点)
    );
end entity;

architecture rtl of PRJ_TOP is

    -- =========================================================================
    -- Qsys (Platform Designer) が自動生成したシステムコンポーネント宣言
    -- (※ nios_platforms_inst.vhd に完全一致させています)
    -- =========================================================================
    component nios_platforms is
        port (
            clk_clk                                  : in  std_logic                    := 'X'; -- clk
            reset_reset_n                            : in  std_logic                    := 'X'; -- reset_n
            simple_led_avalon_0_conduit_end_readdata : out std_logic_vector(3 downto 0)         -- readdata
        );
    end component nios_platforms;

begin

    -- =========================================================================
    -- Qsys システムのインスタンス化 (Instantiation)
    -- =========================================================================
    u0 : component nios_platforms
        port map (
            clk_clk                                  => fpga_clk,     -- 外部クロック接続
            reset_reset_n                            => fpga_reset_n, -- 外部リセット接続
            simple_led_avalon_0_conduit_end_readdata => fpga_leds     -- 物理LEDピンへ接続
        );

end architecture;
