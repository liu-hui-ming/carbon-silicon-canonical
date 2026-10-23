`timescale 1ns/1ps
module tb_minimal_q6;
    logic clk, rst_n, en_step;
    logic [5:0] cur_idx;
    logic [63:0] next_mask;
    logic valid;
    integer i, hd;
    logic [5:0] xor_bits;
    logic [5:0] iv;
    t_operator_q6 dut(.*);

    initial begin clk=0; forever #5 clk=~clk; end
    initial begin
        rst_n=0; en_step=0; cur_idx=0;
        #20; rst_n=1;
        $display("=== MINIMAL TEST idx=0 ===");
        @(negedge clk); cur_idx=0; en_step=0;
        @(negedge clk); en_step=1;
        @(posedge clk); #1;
        $display("capture: cur_idx=%0d mask=%016h valid=%b",cur_idx,next_mask,valid);
        for(i=0;i<64;i=i+1) if(next_mask[i]) begin
            iv=i[5:0]; xor_bits=cur_idx ^ iv;
            hd=xor_bits[0]+xor_bits[1]+xor_bits[2]+xor_bits[3]+xor_bits[4]+xor_bits[5];
            $display("neighbor i=%0d iv=%06b xor=%06b hd=%0d",i,iv,xor_bits,hd);
        end
        @(negedge clk); en_step=0;
        #2; $finish;
    end
endmodule
