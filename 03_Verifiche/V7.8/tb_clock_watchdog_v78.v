// V7.8 self-checking behavioral bench: TWO simulated clocks.
// There is no independent hardware watchdog, no physical DAC/PA/antenna.
`timescale 1ns/1ps
module tb_clock_watchdog_v78;
  reg master_base=0, refclk=0, master_run=1, rst_n=0;
  always #5 master_base=~master_base;
  always #3 refclk=~refclk;
  wire virtual_master_clk=master_run ? master_base : 1'b0;
  wire healthy,fault,rf,release_pd,analog;
  v78_offline_dual_domain_top dut(
    .master_clk_virtual(virtual_master_clk),
    .independent_ref_clk_virtual(refclk),
    .reset_n_virtual(rst_n),
    .diagnostic_master_alive(healthy),
    .diagnostic_clock_fault_latched(fault),
    .tx_rf_permission(rf),
    .dac_pd_released(release_pd),
    .analog_path_connected(analog)
  );
  always @(negedge refclk) begin
    if(rf !== 1'b0 || release_pd !== 1'b0 || analog !== 1'b0)
      $fatal(1,"hardware outputs must remain unconditionally inhibited");
  end
  initial begin
    repeat(4) @(negedge refclk);
    if(healthy!==1'b0) $fatal(1,"startup must not claim healthy");
    rst_n=1'b1;
    repeat(100) @(negedge refclk);
    if(healthy!==1'b1 || fault!==1'b0)
       $fatal(1,"healthy master clocks should yield diagnostic alive");
    // Stop ONLY the master clock while independent reference still runs.
    @(negedge master_base);
    master_run=1'b0;
    repeat(55) @(negedge refclk);
    if(fault!==1'b1 || healthy!==1'b0)
       $fatal(1,"clock-stop must latch fault in independent reference domain");
    master_run=1'b1;
    repeat(100) @(negedge refclk);
    if(fault!==1'b1 || healthy!==1'b0)
       $fatal(1,"fault cannot auto-clear on master clock recovery");
    rst_n=1'b0;
    repeat(5) @(negedge refclk);
    if(healthy!==1'b0 || fault!==1'b0)
       $fatal(1,"reset clears diagnostics only; not a physical safety reset");
    rst_n=1'b1;
    repeat(100) @(negedge refclk);
    if(healthy!==1'b1 || fault!==1'b0)
       $fatal(1,"healthy diagnostics may return only after new edges");
    $display("PASS V7.8 RTL: independent reference detects master stop, fault latch; no RF/PD/analog output");
    $finish;
  end
endmodule
