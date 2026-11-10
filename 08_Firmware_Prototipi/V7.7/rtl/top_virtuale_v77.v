// V7.7 simulation/synthesis TOP - no DAC, PA, PTT or RF pins.
// All output words below are DIAGNOSTICS, NOT data routed to an external DAC.
// Entire hardware TX is absent, all device placement remains DNP. NO FAB / NO TX.
`default_nettype none
module v77_offline_top (
    input wire master_clk_virtual,
    input wire reset_n_virtual,
    input wire rail_ok_virtual,
    input wire config_ok_virtual,
    input wire external_clock_watchdog_ok_virtual,
    input wire independent_supervisor_ok_virtual,
    input wire independent_pd_guard_ok_virtual,
    input wire virtual_push,
    input wire [9:0] virtual_input_word,
    output wire [9:0] diagnostic_sample_word,
    output wire diagnostic_sample_strobe,
    output wire diagnostic_audio_ce,
    output wire diagnostic_fault,
    output wire [4:0] diagnostic_fifo_occupancy,
    output wire tx_rf_permission,
    output wire dac_pd_released,
    output wire analog_path_connected
);
    wire virtual_dac_ce, virtual_audio_ce;
    wire clock_permission;
    wire fifo_permission;
    wire fifo_pd_release;
    wire fifo_analog_connected;

    v76_clock_ce divider (
        .master_clk(master_clk_virtual),
        .rst_n(reset_n_virtual),
        .dac_sample_ce(virtual_dac_ce),
        .audio_ce(virtual_audio_ce),
        .tx_rf_permission(clock_permission)
    );

    v76_virtual_fifo_guard fifo (
        .master_clk(master_clk_virtual),
        .rst_n(reset_n_virtual),
        .rail_ok(rail_ok_virtual),
        .config_ok(config_ok_virtual),
        .external_clock_monitor_ok(external_clock_watchdog_ok_virtual),
        .independent_supervisor_ok(independent_supervisor_ok_virtual),
        .independent_pd_guard_ok(independent_pd_guard_ok_virtual),
        .in_valid(virtual_push),
        .in_word(virtual_input_word),
        .sample_ce(virtual_dac_ce),
        .sample_word_virtual(diagnostic_sample_word),
        .sample_valid_virtual(diagnostic_sample_strobe),
        .fault_latched(diagnostic_fault),
        .occupancy(diagnostic_fifo_occupancy),
        .tx_rf_permission(fifo_permission),
        .dac_pd_released(fifo_pd_release),
        .analog_path_connected(fifo_analog_connected)
    );
    assign diagnostic_audio_ce = virtual_audio_ce;
    // No conditional logic can enable hardware - these are explicit constants.
    assign tx_rf_permission=1'b0;
    assign dac_pd_released=1'b0;
    assign analog_path_connected=1'b0;
endmodule
`default_nettype wire
