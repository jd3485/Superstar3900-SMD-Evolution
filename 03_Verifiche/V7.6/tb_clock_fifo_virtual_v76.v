// Self-checking Icarus Verilog simulation for V7.6; NO physical pins.
`timescale 1ns/1ps
module tb_clock_fifo_virtual_v76;
    reg clk=0;
    always #5 clk=~clk; // 100MHz simulation acceleration, counters /8 /640
    reg rst_n=0;
    wire dac_ce,audio_ce,clock_tx_permitted;
    v76_clock_ce clock_model(.master_clk(clk),.rst_n(rst_n),
        .dac_sample_ce(dac_ce),.audio_ce(audio_ce),
        .tx_rf_permission(clock_tx_permitted));
    reg rail_ok=1,config_ok=1,ext_clock_ok=1,supervisor_ok=1,pd_guard_ok=1;
    reg in_valid=0,sample_ce=0;
    reg [9:0] in_word=0;
    wire [9:0] word_virtual;
    wire sample_valid_virtual, fault_latched;
    wire [4:0] occupancy;
    wire tx_permission,pd_released,analog_link;
    v76_virtual_fifo_guard fifo_model(
        .master_clk(clk),.rst_n(rst_n),
        .rail_ok(rail_ok),.config_ok(config_ok),
        .external_clock_monitor_ok(ext_clock_ok),
        .independent_supervisor_ok(supervisor_ok),
        .independent_pd_guard_ok(pd_guard_ok),
        .in_valid(in_valid),.in_word(in_word),.sample_ce(sample_ce),
        .sample_word_virtual(word_virtual),
        .sample_valid_virtual(sample_valid_virtual),
        .fault_latched(fault_latched),.occupancy(occupancy),
        .tx_rf_permission(tx_permission),.dac_pd_released(pd_released),
        .analog_path_connected(analog_link));
    integer i,dac_count,audio_count;
    task automatic push_word(input [9:0] v);
    begin
        @(negedge clk);
        in_word=v; in_valid=1;
        @(negedge clk);
        in_valid=0;
    end
    endtask
    task automatic pop_word(input [9:0] expected);
    begin
        @(negedge clk);
        sample_ce=1;
        @(negedge clk);
        sample_ce=0;
        if(!sample_valid_virtual || word_virtual !== expected || fault_latched)
            $fatal(1,"virtual FIFO wrong pop: expected=%d actual=%d fault=%b",expected,word_virtual,fault_latched);
    end
    endtask
    task automatic restart;
    begin
        @(negedge clk); rst_n=0; in_valid=0; sample_ce=0;
        rail_ok=1; config_ok=1; ext_clock_ok=1; supervisor_ok=1; pd_guard_ok=1;
        repeat(2) @(negedge clk);
        rst_n=1;
    end
    endtask
    initial begin
        dac_count=0; audio_count=0;
        repeat(2) @(negedge clk);
        rst_n=1;
        for(i=0;i<1280;i=i+1) begin
            @(negedge clk);
            if(dac_ce) dac_count=dac_count+1;
            if(audio_ce) begin
                audio_count=audio_count+1;
                if (!dac_ce) $fatal(1,"audio strobe not aligned with DAC strobe");
            end
            if(clock_tx_permitted !== 1'b0 || tx_permission !== 1'b0 ||
               pd_released !== 1'b0 || analog_link !== 1'b0)
                $fatal(1,"nonzero hardware permissions");
        end
        if (dac_count != 160 || audio_count != 2)
            $fatal(1,"divider mismatch dac=%d audio=%d",dac_count,audio_count);

        push_word(10'd123);
        push_word(10'd456);
        if(occupancy!==5'd2) $fatal(1,"expected 2 FIFO entries");
        pop_word(10'd123);
        pop_word(10'd456);
        if(occupancy!==5'd0) $fatal(1,"FIFO not drained");

        @(negedge clk); sample_ce=1;
        @(negedge clk); sample_ce=0;
        if(!fault_latched || occupancy!==0) $fatal(1,"underflow not latched");
        push_word(10'd800);
        if(occupancy!==0 || !fault_latched) $fatal(1,"fault should inhibit enqueue");

        restart();
        for(i=0;i<16;i=i+1) push_word(i);
        if(occupancy!==5'd16) $fatal(1,"FIFO not full");
        push_word(10'd17);
        if(!fault_latched || occupancy!==0) $fatal(1,"overflow did not latch");

        restart();
        push_word(10'd100);
        @(negedge clk); pd_guard_ok=0;
        @(negedge clk);
        if(!fault_latched || occupancy!==0) $fatal(1,"independent guard fault not latched");
        pd_guard_ok=1;
        repeat(8) @(negedge clk);
        if(!fault_latched || tx_permission!==0 || pd_released!==0) $fatal(1,"fault auto-cleared");

        restart();
        push_word(10'd100);
        @(negedge clk); ext_clock_ok=0;
        @(negedge clk);
        if(!fault_latched) $fatal(1,"external watchdog flag not latched");
        if(analog_link!==0) $fatal(1,"RF analog link should be absent");
        $display("PASS V7.6 RTL: coherent /8 /640 strobes, virtual FIFO and latched faults; RF always disabled");
        $finish;
    end
endmodule
