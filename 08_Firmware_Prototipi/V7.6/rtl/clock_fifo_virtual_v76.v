// V7.6: RTL behavioral simulation reference, NO PHYSICAL OUTPUT PORTS TO DAC.
// DO NOT infer a hardware TX enable from simulation. NO FAB / NO TX.
// Master 30.72MHz; sample strobes /8 and /640. Not an output-clock
// generator; a real DAC900 requires clock waveform/timing and physical PD guard.
// Lattice FPGA pin constraints and synthesis/timing are NOT validated here.
`default_nettype none
module v76_clock_ce (
    input wire master_clk,
    input wire rst_n,
    output reg dac_sample_ce,
    output reg audio_ce,
    output wire tx_rf_permission
);
    reg [2:0] div8;
    reg [9:0] div640;
    assign tx_rf_permission=1'b0;
    always @(posedge master_clk or negedge rst_n) begin
        if (!rst_n) begin
            div8 <= 3'd0;
            div640 <= 10'd0;
            dac_sample_ce <= 1'b0;
            audio_ce <= 1'b0;
        end else begin
            dac_sample_ce <= (div8==3'd7);
            audio_ce <= (div640==10'd639);
            if (div8==3'd7) div8<=3'd0;
            else div8<=div8+3'd1;
            if (div640==10'd639) div640<=10'd0;
            else div640<=div640+10'd1;
        end
    end
endmodule

module v76_virtual_fifo_guard (
    input wire master_clk,
    input wire rst_n,
    input wire rail_ok,
    input wire config_ok,
    input wire external_clock_monitor_ok,
    input wire independent_supervisor_ok,
    input wire independent_pd_guard_ok,
    input wire in_valid,
    input wire [9:0] in_word,
    input wire sample_ce,
    output reg [9:0] sample_word_virtual,
    output reg sample_valid_virtual,
    output reg fault_latched,
    output wire [4:0] occupancy,
    output wire tx_rf_permission,
    output wire dac_pd_released,
    output wire analog_path_connected
);
    // Exactly 16 code words. Small study FIFO, NOT enough to bridge 512 audio
    // samples or tolerate an external audio clock domain.
    reg [9:0] words[0:15];
    reg [3:0] wp;
    reg [3:0] rp;
    reg [4:0] used;
    assign occupancy=used;
    assign tx_rf_permission=1'b0;
    assign dac_pd_released=1'b0;
    assign analog_path_connected=1'b0;

    always @(posedge master_clk or negedge rst_n) begin
        if(!rst_n) begin
            wp<=4'd0;
            rp<=4'd0;
            used<=5'd0;
            sample_word_virtual<=10'd0;
            sample_valid_virtual<=1'b0;
            fault_latched<=1'b0;
        end else begin
            sample_valid_virtual<=1'b0;
            if (!fault_latched) begin
                if (!(rail_ok && config_ok && external_clock_monitor_ok &&
                      independent_supervisor_ok && independent_pd_guard_ok)) begin
                    fault_latched<=1'b1;
                    used<=5'd0;
                end else if (sample_ce && used==5'd0) begin
                    fault_latched<=1'b1; // underflow; including same-cycle push
                    used<=5'd0;
                end else if (in_valid && used==5'd16 && !sample_ce) begin
                    fault_latched<=1'b1;
                    used<=5'd0;
                end else begin
                    if(in_valid) begin
                        words[wp]<=in_word;
                        wp<=wp+4'd1;
                    end
                    if(sample_ce) begin
                        sample_word_virtual<=words[rp];
                        sample_valid_virtual<=1'b1;
                        rp<=rp+4'd1;
                    end
                    if(in_valid && !sample_ce) used<=used+5'd1;
                    if(!in_valid && sample_ce) used<=used-5'd1;
                    // simultaneous read and write keeps occupancy unchanged
                end
            end
        end
    end
endmodule
`default_nettype wire
