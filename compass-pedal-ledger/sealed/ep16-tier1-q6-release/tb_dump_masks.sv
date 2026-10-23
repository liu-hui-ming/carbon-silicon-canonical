`timescale 1ns/1ps
module tb_dump_masks;
    logic clk=0, rst_n=0, en_step=0;
    logic [5:0] cur_idx=0;
    logic [63:0] next_mask;
    logic valid;
    integer i;
    integer fd;
    t_operator_q6 dut(.*);
    initial begin clk=0; forever #5 clk=~clk; end
    initial begin
        #2 rst_n=1;
        fd=$fopen("masks_dump.txt","w");
        for(i=0;i<64;i=i+1) begin
            @(negedge clk);
            cur_idx=i[5:0]; en_step=1;
            @(posedge clk); #1;
            $fwrite(fd,"%0d %016h\n",i,next_mask);
        end
        $fclose(fd);
        $finish;
    end
endmodule
