// V7.9: accelerated self-checking two-clock bench; simulation ONLY.
// Clock accelerations bear NO absolute real hardware timing relation.
`timescale 1ns/1ps
module tb_slow_heartbeat_v79;
reg master_base=0, ref_clk=0,run_master=1,rst_n=0;
always #5 master_base=~master_base;
always #3 ref_clk=~ref_clk;
wire master_clk = run_master ? master_base : 1'b0;
wire wdi,alive,fault,tx,pd,analog;
integer falling_edges=0;
v79_virtual_watchdog_top #(
  .MASTER_TICKS_PER_TOGGLE(8),.REF_WATCHDOG_MAX_TICKS(40)
) dut (
 .master_clk_virtual(master_clk),
 .independent_ref_clk_virtual(ref_clk),
 .reset_n_virtual(rst_n),
 .diagnostic_wdi_virtual(wdi),
 .diagnostic_master_alive(alive),
 .diagnostic_clock_fault_latched(fault),
 .tx_rf_permission(tx),.dac_pd_released(pd),.analog_path_connected(analog)
);
always @(negedge wdi) if(rst_n) falling_edges=falling_edges+1;
always @(negedge ref_clk) begin
 if(tx !== 1'b0 || pd !== 1'b0 || analog !== 1'b0)
  $fatal(1,"hardware path must be disabled unconditionally");
end
initial begin
 repeat(4) @(negedge ref_clk);
 rst_n=1;
 repeat(110) @(negedge ref_clk);
 if(falling_edges<3 || !alive || fault)
  $fatal(1,"healthy decimated heartbeat not detected");
 // Stop master only and preserve 32k-like reference domain mathematically.
 @(negedge master_base);run_master=0;
 repeat(48) @(negedge ref_clk);
 if(!fault || alive) $fatal(1,"clock-stop not latched");
 run_master=1;
 repeat(60) @(negedge ref_clk);
 if(!fault || alive) $fatal(1,"stale fault auto-cleared");
 rst_n=0;
 repeat(5) @(negedge ref_clk);
 if(fault || alive) $fatal(1,"reset diagnostic mismatch");
 rst_n=1;
 repeat(110) @(negedge ref_clk);
 if(fault || !alive) $fatal(1,"healthy edges after explicit reset missing");
 $display("PASS V7.9 RTL: slow heartbeat, independent-ref stop latch, RF/PD/analog zero");
 $finish;
end
endmodule
