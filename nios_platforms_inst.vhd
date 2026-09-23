	component nios_platforms is
		port (
			clk_clk                                  : in  std_logic                    := 'X'; -- clk
			reset_reset_n                            : in  std_logic                    := 'X'; -- reset_n
			simple_led_avalon_0_conduit_end_readdata : out std_logic_vector(3 downto 0)         -- readdata
		);
	end component nios_platforms;

	u0 : component nios_platforms
		port map (
			clk_clk                                  => CONNECTED_TO_clk_clk,                                  --                             clk.clk
			reset_reset_n                            => CONNECTED_TO_reset_reset_n,                            --                           reset.reset_n
			simple_led_avalon_0_conduit_end_readdata => CONNECTED_TO_simple_led_avalon_0_conduit_end_readdata  -- simple_led_avalon_0_conduit_end.readdata
		);

