// ============================================================
// sva_dual_axis_state_machine.sv  v0.4
// 状态：PROPOSED / REVIEW_REQUIRED / NOT_COMPILED / NOT_SIMULATED
// 变更：断言4 改用标准 SystemVerilog 1800-2017 s_always 算子
//       断言1 已按 D01 处置移除（方案A/B 待会审表决）
// 注：原文提交中 `rose(...)` 缺 `$`、`s_always[1:]` 缺 `$`，已按标准补全，
//     语义不变；s_always 后必须跟常数或 $（本文用 [1:$]）。
// ============================================================
module sva_dual_axis_state_machine;
  typedef enum logic [2:0] {
    E_PROPOSED, E_DEFINED, E_ESTIMATED, E_TESTED_SCOPE, E_REPLICATED, E_CONTRADICTED, E_UNKNOWN
  } evidence_state_t;

  typedef enum logic [1:0] {
    G_ACTIVE, G_SUSPENDED, G_RETIRED, G_ARCHIVED
  } governance_state_t;

  evidence_state_t e_state;
  governance_state_t g_state;
  logic g_retired_sig;

  assign g_retired_sig = (g_state == G_RETIRED);

  // 断言2：CONTRADICTED 可以保持 ACTIVE（证伪存案合法稳态）
  a_contradicted_active_legal: assert property (@(posedge clk)
    (e_state == E_CONTRADICTED) |-> (g_state == G_ACTIVE) || (g_state == G_RETIRED) || (g_state == G_ARCHIVED));

  // 断言3：UNKNOWN 不是终态，允许后续证据升级
  a_unknown_not_terminal: assert property (@(posedge clk)
    (e_state == E_UNKNOWN) |-> ##[1:$] (e_state != E_UNKNOWN) || (g_state == G_ARCHIVED));

  // 断言4｜标准SV s_always：ARCHIVED上升沿之后永久锁定
  a_archived_immutable: assert property (@(posedge clk)
    $rose(g_state == G_ARCHIVED) |-> s_always [1:$] (g_state == G_ARCHIVED));
  // 备选弱约束（老旧仿真器兼容 / 业务允许解封时启用，改名 a_archived_sticky_once）
  // a_archived_sticky_once: assert property (@(posedge clk)
  //   $past(g_state == G_ARCHIVED) |-> g_state == G_ARCHIVED);

  // 断言5：证据进入CONTRADICTED，不能自动边沿触发RETIRED；下线必须是独立治理动作
  a_no_cross_axis_auto_retire: assert property (@(posedge clk)
    (e_state == E_CONTRADICTED) |-> !$rose(g_retired_sig));
endmodule
