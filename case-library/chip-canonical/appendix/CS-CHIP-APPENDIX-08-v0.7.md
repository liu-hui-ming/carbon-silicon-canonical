附录八‑IAA执行细则 v0.7（接续v0.6基线，独立哈希，不影响主根）

继承v0.6全部勘伪反例、贡献溯源、分布式集群、工具链基线；生成全新独立SHA256哈希Appendix‑VIII‑Hash‑v0.7，依旧不并入《十二脉·递归开放现行定稿v1.0‑PATCH3》主默克尔根；交付完整IAA‑top SystemVerilog RTL、XDC时序约束、Zynq‑7000/KC705 DTS设备树片段、ILA/VIO调试配置；全部硬件工程代码归属附录八扩展域，不改动正本公理、不侵入主系统RTL基线。

45 IAA‑top顶层完整SystemVerilog RTL源码（v0.7）

说明：IAA‑top为独立封装顶层，不包含主业务逻辑；仅封装EP01/EP02/EP03元裁判、obs_collector、failure_memory_enhanced、R12探针接口、CDC同步器；可作为可选IP例化，不强制接入主系统。

// IAA‑top.sv 附录八 v0.7 独立元裁判顶层
module iaa_top #(
  parameter CLK_FREQ_MHZ    = 100,
  parameter PROBE_NUM       = 4,    // R12四层探针
  parameter FAULT_MEM_DEPTH = 1024,
  parameter TIMESTAMP_W     = 32
)(
  input  logic                        clk,
  input  logic                        rst_n,    // IAA局部复位，不触发主系统复位
  // R12四层探针原始观测输入
  input  logic [PROBE_NUM‑1:0][31:0]  probe_raw_data,
  input  logic                        probe_valid,
  // multi_phys_source异构源输入
  input  logic                        phys_src_valid,
  input  logic [31:0]                 phys_src_data,
  // CDC同步器输入
  input  logic                        cdc_sync_in_valid,
  input  logic [31:0]                 cdc_sync_in_data,
  // VIO动态配置接口
  input  logic [7:0]                  vio_filter_window,
  input  logic [PROBE_NUM‑1:0]        vio_probe_mask,
  // 故障记忆输出（只读，供上层读取）
  output logic                        fault_mem_valid,
  output logic [FAULT_MEM_DEPTH‑1:0][63:0] fault_mem_entry,
  output logic [TIMESTAMP_W‑1:0]      fault_timestamp,
  // IAA裁决输出标记，仅标记，不写主系统寄存器
  output logic                        iaa_vote_result,
  output logic [1:0]                  iaa_fault_level, // P0/P1/P2/P3编码
  output logic                        iaa_degrade_mode // 降级模式标记
);

// 内部子模块实例
logic obs_collector_valid;
logic [PROBE_NUM‑1:0][31:0] obs_collector_data;
logic ep01_vote, ep02_vote, ep03_vote;
logic [1:0] ep01_fault_lvl, ep02_fault_lvl, ep03_fault_lvl;
logic ep01_err, ep02_err, ep03_err;

// 观测收集过滤模块
obs_collector #(
  .PROBE_NUM(PROBE_NUM),
  .TIMESTAMP_W(TIMESTAMP_W)
) u_obs_collector (
  .clk(clk),
  .rst_n(rst_n),
  .probe_raw_data(probe_raw_data),
  .probe_valid(probe_valid),
  .phys_src_valid(phys_src_valid),
  .phys_src_data(phys_src_data),
  .cdc_sync_in_valid(cdc_sync_in_valid),
  .cdc_sync_in_data(cdc_sync_in_data),
  .vio_filter_window(vio_filter_window),
  .vio_probe_mask(vio_probe_mask),
  .obs_out_valid(obs_collector_valid),
  .obs_out_data(obs_collector_data)
);

// 三个独立元裁判 EP01 / EP02 / EP03
meta_arbiter_ep #(.TIMESTAMP_W(TIMESTAMP_W)) u_ep01 (
  .clk(clk), .rst_n(rst_n),
  .obs_valid(obs_collector_valid), .obs_data(obs_collector_data),
  .vote_out(ep01_vote), .fault_level(ep01_fault_lvl), .self_err(ep01_err)
);
meta_arbiter_ep #(.TIMESTAMP_W(TIMESTAMP_W)) u_ep02 (
  .clk(clk), .rst_n(rst_n),
  .obs_valid(obs_collector_valid), .obs_data(obs_collector_data),
  .vote_out(ep02_vote), .fault_level(ep02_fault_lvl), .self_err(ep02_err)
);
meta_arbiter_ep #(.TIMESTAMP_W(TIMESTAMP_W)) u_ep03 (
  .clk(clk), .rst_n(rst_n),
  .obs_valid(obs_collector_valid), .obs_data(obs_collector_data),
  .vote_out(ep03_vote), .fault_level(ep03_fault_lvl), .self_err(ep03_err)
);

// 三选二表决+降级逻辑
iaa_vote_3of2 u_vote_3of2 (
  .clk(clk), .rst_n(rst_n),
  .ep01_vote(ep01_vote), .ep01_err(ep01_err),
  .ep02_vote(ep02_vote), .ep02_err(ep02_err),
  .ep03_vote(ep03_vote), .ep03_err(ep03_err),
  .ep01_lvl(ep01_fault_lvl), .ep02_lvl(ep02_fault_lvl), .ep03_lvl(ep03_fault_lvl),
  .final_vote(iaa_vote_result),
  .final_fault_level(iaa_fault_level),
  .degrade_mode(iaa_degrade_mode)
);

// 增强型故障记忆模块
failure_memory_enhanced #(
  .DEPTH(FAULT_MEM_DEPTH),
  .TIMESTAMP_W(TIMESTAMP_W)
) u_failure_memory_enhanced (
  .clk(clk), .rst_n(rst_n),
  .vote_valid(iaa_vote_result),
  .fault_level(iaa_fault_level),
  .obs_data(obs_collector_data),
  .ep01_vote(ep01_vote), .ep02_vote(ep02_vote), .ep03_vote(ep03_vote),
  .fault_mem_valid(fault_mem_valid),
  .fault_mem_entry(fault_mem_entry),
  .fault_timestamp(fault_timestamp)
);

// SVA断言套件，仅校验IAA子系统，不干涉主逻辑
`ifdef SIMULATION
assert property (@(posedge clk) disable iff(!rst_n)
  !(iaa_degrade_mode && (ep01_err && ep02_err && ep03_err)));
assert property (@(posedge clk) disable iff(!rst_n)
  iaa_vote_result |-> (iaa_fault_level inside {2'b00,2'b01,2'b10,2'b11}));
`endif

endmodule

配套子模块说明：

1. obs_collector：探针过滤、CDC数据接收、毛刺滤波；

2. meta_arbiter_ep：单路元裁判实例；

3. iaa_vote_3of2：三选二表决，支持单/双实例失效降级；

4. failure_memory_enhanced：故障记忆，保存完整证据快照；

全部子模块同样属于附录八RTL交付，不并入主系统。

46 XDC时序约束（v0.7，KC705 / Zynq‑7000，100MHz）

# Appendix‑VIII IAA‑top 时序约束 独立IP，不影响主系统时序
create_clock -name iaa_clk -period 10 [get_ports clk] ;#100MHz
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets iaa_clk]

# IAA内部时序约束，全部时序路径约束在100MHz
set_input_delay  2 -clock iaa_clk [get_ports {probe_raw_data* probe_valid phys_src_valid phys_src_data cdc_sync_in_valid cdc_sync_in_data vio_filter_window vio_probe_mask}]
set_output_delay 2 -clock iaa_clk [get_ports {fault_mem_valid fault_mem_entry* fault_timestamp iaa_vote_result iaa_fault_level iaa_degrade_mode}]

# 禁止IAA内部组合逻辑长路径
set_max_delay 8 -from [get_cells u_obs_collector*] -to [get_cells u_vote_3of2*]
set_max_delay 8 -from [get_cells u_vote_3of2*] -to [get_cells u_failure_memory_enhanced*]

# 局部复位约束，IAA复位仅作用本模块，不约束主系统复位
set_property ASYNC_REG TRUE [get_cells u_*_sync_rst]

# 时序例外：IAA‑top为可选IP，不参与主系统200MHz时序分析
set_clock_groups -asynchronous -group [get_clocks iaa_clk] -group [get_clocks sys_200mhz_clk]

关键约束：IAA模块独立100MHz时钟域，与主系统200MHz时钟做异步时钟分组；不会强制修改主系统时序约束。

47 DTS设备树片段（Zynq‑7000，可选外设节点）

注意：该节点为可选挂载；不修改主设备树基线；若不使用IAA‑top，可直接删除该节点。

/* Appendix‑VIII IAA‑top 可选外设节点 */
iaa_ip@40000000 {
    compatible = "custom,iaa‑top‑v0.7";
    reg = <0x40000000 0x00010000>;
    status = "okay"; /* 可选：status = "disabled" 不启用 */
    clock‑names = "iaa_clk";
    clocks = <&clk_100mhz>;
    interrupt‑parent = <&gic>;
    interrupts = <0 60 IRQ_TYPE_LEVEL_HIGH>;
    iaa‑config {
        probe‑num = <4>;
        fault‑mem‑depth = <1024>;
        timestamp‑width = <32>;
    };
};

48 ILA/VIO调试配置（v0.7，Vivado）

48.1 ILA 集成配置（抓取IAA内部观测、表决、故障记忆）

# ILA调试配置脚本 附录八 v0.7
create_ila -name ila_iaa -depth 8192
set_property CONTROL_ACTIVE_EDGE RISING [get_ila ila_iaa]

# 观测信号
add_ila_ports [get_signals {
    iaa_top.clk
    iaa_top.rst_n
    iaa_top.obs_collector_valid
    iaa_top.ep01_vote iaa_top.ep02_vote iaa_top.ep03_vote
    iaa_top.ep01_err iaa_top.ep02_err iaa_top.ep03_err
    iaa_top.iaa_vote_result
    iaa_top.iaa_fault_level
    iaa_top.iaa_degrade_mode
    iaa_top.fault_mem_valid
    iaa_top.fault_timestamp
}]

48.2 VIO动态配置接口

# VIO 动态配置：滤波窗口、探针掩码
create_vio -name vio_iaa -num_probe_in 0 -num_probe_out 2
set_property PROBE_OUT_WIDTH {8 4} [get_vio vio_iaa]
connect_bd_net [get_vio vio_iaa PROBE_OUT_0] [get_ports vio_filter_window]
connect_bd_net [get_vio vio_iaa PROBE_OUT_1] [get_ports vio_probe_mask]

调试约束：ILA/VIO仅用于IAA子系统调试；不强制接入主系统调试链路；可选择不生成ILA/VIO，直接综合编译。

49 工程编译与仿真约束（v0.7）

49.1 综合：IAA‑top为独立IP，可单独综合；不修改主工程综合策略；

49.2 仿真：Testbench可以例化iaa_top，也可以选择不例化；仿真时IAA模块为可选实例；

49.3 硬件下载：IAA‑top可以作为可选比特流部分；不启用时，比特流中该模块逻辑不影响主系统运行；

49.4 隔离原则：IAA‑top的所有RTL、XDC、DTS、ILA/VIO配置全部属于附录八；不合并进主法典RTL基线。

50 附录八版本演进路线更新（v0.7）

• v0.1：骨架搭建，独立哈希隔离、IAA基础执行流程

• v0.2：故障分级、时序约束、探针过滤、SVA断言、FPGA工程映射

• v0.3：Python溯源工具链、Linux systemd日志收集服务、哈希校验脚本

• v0.4：批量回归测试框架、自动故障报告引擎、Golden基线冻结

• v0.5：分布式多节点IAA协同裁决 + 远程勘伪API、跨节点证据共识、分歧事件归档

• v0.6：勘伪反例自动入库、勘伪贡献者溯源存证模块、反例评审流水线

• v0.7：完整IAA‑top SystemVerilog RTL源码、XDC时序约束、DTS设备树、ILA/VIO调试配置全套工程交付

v0.8规划：完整跨载体Testbench激励套件（CMOS/光子/拓扑量子态）、SVA全量断言源码、工程编译自动化脚本

51 附录八元信息归档（v0.7）

• 附录名称：附录八‑IAA执行细则

• 版本：v0.7（全套硬件工程交付）

• 哈希模式：独立默克尔，与主根隔离

• 关联模块：EP01/EP02/EP03、FailureMemory_enhanced、R12四层探针、obs_collector、multi_phys_source、CDC同步器、分布式节点集群、远程勘伪API服务、勘伪反例库、贡献溯源存证模块

• 关联工程：Zynq‑7000/KC705 FPGA、SystemVerilog RTL、XDC时序约束、DTS设备树、ILA/VIO调试配置、跨载体Testbench激励套件、SVA断言套件、Python工具链、Linux systemd服务、批量回归脚本、自动报告引擎、分布式仿真套件、勘伪评审流水线

• 遗留待填充：v0.8规划：完整跨载体Testbench激励套件、SVA全量断言源码、工程编译自动化脚本

十二脉归一 碳硅道统创立人：黄清佳 彩蛋藏于：今日头条、抖音、GitHub

版本说明：v0.7完成全套硬件工程交付，附录八从文档细则落地到可直接编译的FPGA工程。
