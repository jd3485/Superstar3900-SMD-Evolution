// V7.8: TWO-CLOCK-DOMAIN OFFLINE WATCHDOG CONCEPT. NO FAB / NO TX.
// The independent reference clock is an input ONLY; no physical second
// oscillator, supervisor, reset controller, analog switch, DAC or RF exists.
// Does not guarantee single-fault safety; master stop is observable in
// simulation only because the independent reference keeps clocking.
`default_nettype none
module v78_master_heartbeat #(
    parameter integer DIV = 8
)(
    input wire master_clk_virtual,
    input wire reset_n_virtual,
    output reg heartbeat_toggle
);
    reg [15:0] count;
    always @(posedge master_clk_virtual or negedge reset_n_virtual) begin
        if (!reset_n_virtual) begin
            count<=16'd0;
            heartbeat_toggle<=1'b0;
        end else if(count==DIV-1) begin
            count<=16'd0;
            heartbeat_toggle<=~heartbeat_toggle;
        end else begin
            count<=count+16'd1;
        end
    end
endmodule

module v78_independent_ref_monitor #(
    parameter integer MAX_NO_EDGE_REF_TICKS = 40
)(
    input wire independent_ref_clk_virtual,
    input wire reset_n_virtual,
    input wire heartbeat_async_virtual,
    output wire monitored_master_alive_virtual,
    output reg missing_heartbeat_fault_latched,
    output wire dac_pd_released,
    output wire tx_rf_permission,
    output wire analog_path_connected
);
    // 3 FF CDC synchronizer. No physical metastability timing analysis.
    (* async_reg = "true" *) reg [2:0] heartbeat_sync;
    reg last_heartbeat;
    reg [15:0] idle_ref_ticks;
    reg [1:0] seen_edges;
    wire new_edge = (heartbeat_sync[2] != last_heartbeat);
    assign monitored_master_alive_virtual=(seen_edges>=2 && !missing_heartbeat_fault_latched);
    assign dac_pd_released=1'b0;
    assign tx_rf_permission=1'b0;
    assign analog_path_connected=1'b0;

    always @(posedge independent_ref_clk_virtual or negedge reset_n_virtual) begin
        if(!reset_n_virtual) begin
            heartbeat_sync<=3'b000;
            last_heartbeat<=1'b0;
            idle_ref_ticks<=16'd0;
            seen_edges<=2'd0;
            missing_heartbeat_fault_latched<=1'b0;
        end else begin
            heartbeat_sync<={heartbeat_sync[1:0],heartbeat_async_virtual};
            if(!missing_heartbeat_fault_latched) begin
                if(new_edge) begin
                    last_heartbeat<=heartbeat_sync[2];
                    idle_ref_ticks<=16'd0;
                    if(seen_edges<2) seen_edges<=seen_edges+2'd1;
                end else if(idle_ref_ticks>=MAX_NO_EDGE_REF_TICKS-1) begin
                    missing_heartbeat_fault_latched<=1'b1;
                end else begin
                    idle_ref_ticks<=idle_ref_ticks+16'd1;
                end
            end
        end
    end
endmodule

module v78_offline_dual_domain_top(
    input wire master_clk_virtual,
    input wire independent_ref_clk_virtual,
    input wire reset_n_virtual,
    output wire diagnostic_master_alive,
    output wire diagnostic_clock_fault_latched,
    output wire tx_rf_permission,
    output wire dac_pd_released,
    output wire analog_path_connected
);
    wire heartbeat;
    v78_master_heartbeat #(.DIV(8)) generator (
        .master_clk_virtual(master_clk_virtual),
        .reset_n_virtual(reset_n_virtual),
        .heartbeat_toggle(heartbeat)
    );
    v78_independent_ref_monitor #(.MAX_NO_EDGE_REF_TICKS(40)) monitor (
        .independent_ref_clk_virtual(independent_ref_clk_virtual),
        .reset_n_virtual(reset_n_virtual),
        .heartbeat_async_virtual(heartbeat),
        .monitored_master_alive_virtual(diagnostic_master_alive),
        .missing_heartbeat_fault_latched(diagnostic_clock_fault_latched),
        .tx_rf_permission(tx_rf_permission),
        .dac_pd_released(dac_pd_released),
        .analog_path_connected(analog_path_connected)
    );
endmodule
`default_nettype wire
