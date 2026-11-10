// V7.9: decimated heartbeat for STUDY ONLY. NO PHYSICAL FPGA, WATCHDOG OR DAC.
// Nominal 30.72MHz master / 307200 yields a toggle every 10 ms;
// falling WDI edges every 20ms. No external output pad is assigned.
// A TPS3430 is NOT physically driven, powered or mounted. NO FAB / NO TX.
`default_nettype none
module v79_slow_heartbeat #(
    parameter integer MASTER_TICKS_PER_TOGGLE=307200
) (
    input wire master_clk_virtual,
    input wire reset_n_virtual,
    output reg wdi_virtual,
    output wire tx_rf_permission,
    output wire dac_pd_released,
    output wire analog_path_connected
);
    // 32-bit counter for parameter portability; 19 bits would suffice for
    // the 307200-tick default. Synthesis is generic, NOT device-mapped.
    reg [31:0] count;
    assign tx_rf_permission=1'b0;
    assign dac_pd_released=1'b0;
    assign analog_path_connected=1'b0;
    always @(posedge master_clk_virtual or negedge reset_n_virtual) begin
        if (!reset_n_virtual) begin
            count<=32'd0;
            wdi_virtual<=1'b0;
        end else if (count==MASTER_TICKS_PER_TOGGLE-1) begin
            count<=32'd0;
            wdi_virtual<=~wdi_virtual;
        end else begin
            count<=count+32'd1;
        end
    end
endmodule

module v79_virtual_watchdog_top #(
    parameter integer MASTER_TICKS_PER_TOGGLE=307200,
    parameter integer REF_WATCHDOG_MAX_TICKS=1311
) (
    input wire master_clk_virtual,
    input wire independent_ref_clk_virtual,
    input wire reset_n_virtual,
    output wire diagnostic_wdi_virtual,
    output wire diagnostic_master_alive,
    output wire diagnostic_clock_fault_latched,
    output wire tx_rf_permission,
    output wire dac_pd_released,
    output wire analog_path_connected
);
    wire heartbeat;
    wire wdi_rf, wdi_pd, wdi_analog;
    wire ref_rf,ref_pd,ref_analog;
    v79_slow_heartbeat #(.MASTER_TICKS_PER_TOGGLE(MASTER_TICKS_PER_TOGGLE)) hb (
       .master_clk_virtual(master_clk_virtual),
       .reset_n_virtual(reset_n_virtual),
       .wdi_virtual(heartbeat),
       .tx_rf_permission(wdi_rf),
       .dac_pd_released(wdi_pd),
       .analog_path_connected(wdi_analog)
    );
    // Imported V7.8 generic reference-domain monitor; reference clock is
    // still SIMULATED. No fault-tolerant physical reset circuitry.
    v78_independent_ref_monitor #(
       .MAX_NO_EDGE_REF_TICKS(REF_WATCHDOG_MAX_TICKS)
    ) mon (
       .independent_ref_clk_virtual(independent_ref_clk_virtual),
       .reset_n_virtual(reset_n_virtual),
       .heartbeat_async_virtual(heartbeat),
       .monitored_master_alive_virtual(diagnostic_master_alive),
       .missing_heartbeat_fault_latched(diagnostic_clock_fault_latched),
       .tx_rf_permission(ref_rf),
       .dac_pd_released(ref_pd),
       .analog_path_connected(ref_analog)
    );
    assign diagnostic_wdi_virtual=heartbeat;
    assign tx_rf_permission=1'b0;
    assign dac_pd_released=1'b0;
    assign analog_path_connected=1'b0;
endmodule
`default_nettype wire
