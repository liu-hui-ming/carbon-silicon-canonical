module sva_q6_t_operator (
    input logic clk,
    input logic rst_n,
    input logic en_step,
    input logic [5:0] cur_idx,
    input logic [63:0] next_mask
);
    property p_A1_pop6;
        @(posedge clk) disable iff (!rst_n)
        en_step |-> $countones(next_mask) == 6;
    endproperty
    assert property (p_A1_pop6) else $error("[SVA A1 FAIL] popcount not 6");

    property p_A2_noself;
        @(posedge clk) disable iff (!rst_n)
        en_step |-> next_mask[cur_idx] == 1'b0;
    endproperty
    assert property (p_A2_noself) else $error("[SVA A2 FAIL] self loop");

    property p_A3_hd1;
        @(posedge clk) disable iff (!rst_n)
        en_step |-> (\
            foreach (next_mask[i])
                next_mask[i] |-> $countones(cur_idx ^ i[5:0]) == 1
        );
    endproperty
    assert property (p_A3_hd1) else $error("[SVA A3 FAIL] hamming distance != 1");
endmodule
