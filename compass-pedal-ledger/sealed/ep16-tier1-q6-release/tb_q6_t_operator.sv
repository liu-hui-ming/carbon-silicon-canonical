`timescale 1ns/1ps
module tb_q6_t_operator;
    localparam integer IDX_W = 6;
    localparam integer MASK_W = 64;
    localparam integer N_NODE = 64;

    logic clk, rst_n, en_step;
    logic [IDX_W-1:0] cur_idx;
    logic [MASK_W-1:0] next_mask;
    logic valid;
    logic [MASK_W-1:0] adj_mat [0:N_NODE-1];
    integer err_cnt;
    integer distance [0:N_NODE-1];
    bit visited [0:N_NODE-1];
    integer q [0:N_NODE-1];
    integer q_head, q_tail;
    integer i, j, r, c, scan_idx;

    t_operator_q6 dut(.*);

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    task automatic fail(input string msg);
        begin
            $display("ERROR: %s", msg);
            err_cnt = err_cnt + 1;
        end
    endtask



    function automatic integer popcount64(input logic [63:0] v);
        integer k;
        begin
            popcount64 = 0;
            for (k=0; k<64; k=k+1) popcount64 = popcount64 + v[k];
        end
    endfunction

    task automatic check_a1(input integer idx, input logic [63:0] msk);
        integer n;
        begin
            n = popcount64(msk);
            if (n != 6) begin
                $display("[A1 FAIL] idx=%0d popcount=%0d expected=6", idx, n);
                err_cnt = err_cnt + 1;
            end
        end
    endtask

    task automatic check_a2(input integer idx, input logic [63:0] msk);
        begin
            if (msk[idx] !== 1'b0) begin
                $display("[A2 FAIL] self-loop idx=%0d", idx);
                err_cnt = err_cnt + 1;
            end
        end
    endtask

    task automatic check_a3(input integer idx, input logic [63:0] msk);
        integer n, hd;
        logic [5:0] iv, xor_bits;
        begin
            for (n = 0; n < 64; n = n + 1) begin
                if (msk[n]) begin
                    iv = n[5:0];
                    xor_bits = idx[5:0] ^ iv;
                    hd = $countones(xor_bits);
                    if (hd != 1) begin
                        $display("[A3 FAIL] idx=%0d neighbor=%0d hd=%0d xor=%06b", idx, n, hd, xor_bits);
                        err_cnt = err_cnt + 1;
                    end
                end
            end
        end
    endtask

    task automatic check_a4;
        integer rr, cc;
        begin
            for (rr = 0; rr < N_NODE; rr = rr + 1)
                for (cc = 0; cc < N_NODE; cc = cc + 1)
                    if (adj_mat[rr][cc] !== adj_mat[cc][rr]) begin
                        $display("[A4 FAIL] asymmetry row=%0d col=%0d", rr, cc);
                        err_cnt = err_cnt + 1;
                    end
        end
    endtask

    task automatic bfs(input integer start);
        integer u, v, qi;
        begin
            for (qi = 0; qi < N_NODE; qi = qi + 1) begin
                distance[qi] = -1;
                visited[qi] = 1'b0;
            end
            q_head = 0;
            q_tail = 0;
            distance[start] = 0;
            visited[start] = 1'b1;
            q[q_tail] = start;
            q_tail = q_tail + 1;
            while (q_head < q_tail) begin
                u = q[q_head];
                q_head = q_head + 1;
                for (v = 0; v < N_NODE; v = v + 1) begin
                    if (adj_mat[u][v] && !visited[v]) begin
                        visited[v] = 1'b1;
                        distance[v] = distance[u] + 1;
                        q[q_tail] = v;
                        q_tail = q_tail + 1;
                    end
                end
            end
        end
    endtask

    task automatic check_a5;
        integer rr, cc, total_directed, max_dist;
        bit all_reachable;
        begin
            total_directed = 0;
            max_dist = 0;
            all_reachable = 1'b1;
            for (rr = 0; rr < N_NODE; rr = rr + 1) begin
                bfs(rr);
                for (cc = 0; cc < N_NODE; cc = cc + 1) begin
                    if (distance[cc] < 0) all_reachable = 1'b0;
                    if (distance[cc] > max_dist) max_dist = distance[cc];
                    if (adj_mat[rr][cc]) total_directed = total_directed + 1;
                end
            end
            if (!all_reachable) begin
                $display("[A5a FAIL] graph is disconnected");
                err_cnt = err_cnt + 1;
            end
            if (max_dist != 6) begin
                $display("[A5b FAIL] diameter=%0d expected=6", max_dist);
                err_cnt = err_cnt + 1;
            end
            if ((total_directed / 2) != 192) begin
                $display("[A5c FAIL] undirected edges=%0d expected=192", total_directed / 2);
                err_cnt = err_cnt + 1;
            end
        end
    endtask

    initial begin
        err_cnt = 0;
        rst_n = 1'b0;
        en_step = 1'b0;
        cur_idx = '0;
        for (i = 0; i < N_NODE; i = i + 1) adj_mat[i] = '0;
        repeat (2) @(negedge clk);
        rst_n = 1'b1;
        $display("=== Q6 T-OPERATOR FULL SCAN START ===");

        for (scan_idx = 0; scan_idx < N_NODE; scan_idx = scan_idx + 1) begin
            @(negedge clk);
            cur_idx = scan_idx[5:0];
            en_step = 1'b1;
            @(posedge clk);
            #1;
            if (valid !== 1'b1) begin
                $display("[CTRL FAIL] valid not asserted idx=%0d", scan_idx);
                err_cnt = err_cnt + 1;
            end
            adj_mat[scan_idx] = next_mask;
            check_a1(scan_idx, next_mask);
            check_a2(scan_idx, next_mask);
            check_a3(scan_idx, next_mask);
            @(negedge clk);
            en_step = 1'b0;
            @(posedge clk);
            #1;
            if (valid !== 1'b0) begin
                $display("[CTRL FAIL] valid not cleared idx=%0d", scan_idx);
                err_cnt = err_cnt + 1;
            end
        end

        check_a4();
        check_a5();
        $display("Scanned nodes: %0d", N_NODE);
        if (err_cnt == 0)
            $display("ALL CHECKS PASS, err_cnt=0");
        else
            $display("CHECKS FAILED, err_cnt=%0d", err_cnt);
        $finish;
    end
endmodule
