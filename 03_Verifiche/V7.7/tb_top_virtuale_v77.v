// V7.7 self-checking TOP testbench. All outputs are SIMULATION diagnostics.
// NO DAC/PA/antenna power or electrical pin. NO FAB / NO TX.
`timescale 1ns/1ps
module tb_top_virtuale_v77;
    reg clk=0;
    always #5 clk=~clk;  // accelerated simulation, not real 30.72MHz
    reg reset_n=0;
    reg rails=1, config_ok=1, ext_watchdog=1, supervisor=1, pd_guard=1;
    reg push=0;
    reg [9:0] word=10'h155;
    wire [9:0] diag_word;
    wire diag_sample, diag_audio, fault;
    wire [4:0] used;
    wire tx_permission,pd_released,analog_link;
    integer sample_events=0;
    v77_offline_top dut(
      .master_clk_virtual(clk), .reset_n_virtual(reset_n),
      .rail_ok_virtual(rails), .config_ok_virtual(config_ok),
      .external_clock_watchdog_ok_virtual(ext_watchdog),
      .independent_supervisor_ok_virtual(supervisor),
      .independent_pd_guard_ok_virtual(pd_guard),
      .virtual_push(push),.virtual_input_word(word),
      .diagnostic_sample_word(diag_word),
      .diagnostic_sample_strobe(diag_sample),
      .diagnostic_audio_ce(diag_audio),
      .diagnostic_fault(fault),
      .diagnostic_fifo_occupancy(used),
      .tx_rf_permission(tx_permission),
      .dac_pd_released(pd_released),
      .analog_path_connected(analog_link)
    );
    always @(negedge clk) begin
        if (tx_permission !== 1'b0 || pd_released !== 1'b0 ||
            analog_link !== 1'b0)
            $fatal(1,"virtual top must never assert a physical permission");
        if (diag_sample) begin
            sample_events=sample_events+1;
            if(diag_word!==10'h155 || fault!==1'b0)
                $fatal(1,"diagnostic FIFO sample corrupted");
        end
    end
    initial begin
        repeat(3) @(negedge clk);
        reset_n=1;
        // Fill 8 entries before first virtual consumption. No physical port.
        push=1;
        repeat(8) @(negedge clk);
        push=0;
        repeat(16) @(negedge clk);
        if (sample_events<1 || fault!==1'b0)
            $fatal(1,"virtual FIFO did not emit a safe diagnostic sample");
        // The external watchdog flag is a mathematical input, NOT a real
        // independently running clock detector.
        ext_watchdog=0;
        repeat(3) @(negedge clk);
        if(fault!==1'b1 || used!==0)
            $fatal(1,"clock watchdog status loss should latch fault");
        ext_watchdog=1;
        repeat(4) @(negedge clk);
        if(fault!==1'b1 || tx_permission!==0)
            $fatal(1,"fault must persist; TX must never be released");

        // Reinitialize to check empty FIFO underflow, without any HW gate.
        reset_n=0;
        repeat(3) @(negedge clk);
        reset_n=1;
        sample_events=0;
        repeat(16) @(negedge clk);
        if(fault!==1'b1)
            $fatal(1,"empty virtual FIFO must fault");
        $display("PASS V7.7 TOP: virtual FIFO, external-monitor flag, sticky fault, constant RF/PD/analog inhibit");
        $finish;
    end
endmodule
