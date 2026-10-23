`timescale 1ns/1ps
module t_operator_q6 #(
    parameter integer IDX_W = 6,
    parameter integer MASK_W = 64
) (
    input  logic                 clk,
    input  logic                 rst_n,
    input  logic                 en_step,
    input  logic [IDX_W-1:0]     cur_idx,
    output logic [MASK_W-1:0]    next_mask,
    output logic                 valid
);
    logic [MASK_W-1:0] mask;

    function automatic logic [MASK_W-1:0] t_transition_mask(input logic [IDX_W-1:0] idx);
        logic [MASK_W-1:0] m;
        integer k;
        logic [IDX_W-1:0] flip_mask;
        logic [IDX_W-1:0] nxt;
        begin
            m = '0;
            for (k = 0; k < IDX_W; k = k + 1) begin
                flip_mask = 6'b000001 << k; // Icarus 12.0: avoid sized literal '$countones' bug only applies in TB checker.
                nxt = idx ^ flip_mask;
                m[nxt] = 1'b1;
            end
            t_transition_mask = m;
        end
    endfunction

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mask  <= '0;
            valid <= 1'b0;
        end else if (en_step) begin
            mask  <= t_transition_mask(cur_idx);
            valid <= 1'b1;
        end else begin
            valid <= 1'b0;
        end
    end

    assign next_mask = mask;
endmodule
