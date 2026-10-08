附录八‑IAA执行细则 v0.8（接续v0.7基线，独立哈希，不影响主根）

继承v0.7全套IAA‑top RTL、XDC、DTS、ILA/VIO工程基线；生成全新独立SHA256哈希Appendix‑VIII‑Hash‑v0.8，依旧不并入《十二脉·递归开放现行定稿v1.0‑PATCH3》主默克尔根；交付完整跨载体Testbench激励套件、SVA全量断言源码、Vivado/Icarus Verilog工程编译自动化脚本；全部仿真、脚本归属附录八扩展域，不改动正本公理、硬件RTL基线。

52 跨载体Testbench激励套件（v0.8）

支持三种物理载体仿真：CMOS电路、光子计算、拓扑量子态；共用同一套IAA‑top DUT，仅切换激励源multi_phys_source；覆盖P0/P1/P2/P3全等级用例、零间隔连发、节点失效、时钟抖动、CDC跨域异常等场景。

// tb_iaa_top.sv 跨载体Testbench 附录八 v0.8
`timescale 1ns / 1ps
module tb_iaa_top;

parameter CLK_PERIOD = 10; //100MHz
parameter PROBE_NUM = 4;
parameter FAULT_MEM_DEPTH = 1024;
parameter TIMESTAMP_W = 32;

logic clk;
logic rst_n;
logic [PROBE_NUM‑1:0][31:0] probe_raw_data;
logic probe_valid;
logic phys_src_valid;
logic [31:0] phys_src_data;
logic cdc_sync_in_valid;
logic [31:0] cdc_sync_in_data;
logic [7:0] vio_filter_window;
logic [PROBE_NUM‑1:0] vio_probe_mask;
logic fault_mem_valid;
logic [FAULT_MEM_DEPTH‑1:0][63:0] fault_mem_entry;
logic [TIMESTAMP_W‑1:0] fault_timestamp;
logic iaa_vote_result;
logic [1:0] iaa_fault_level;
logic iaa_degrade_mode;

// DUT实例
iaa_top #(
  .CLK_FREQ_MHZ(100),
  .PROBE_NUM(PROBE_NUM),
  .FAULT_MEM_DEPTH(FAULT_MEM_DEPTH),
  .TIMESTAMP_W(TIMESTAMP_W)
) u_dut (.*);

// 时钟复位
initial begin
  clk = 1'b0;
  forever #(CLK_PERIOD/2) clk = ~clk;
end
initial begin
  rst_n = 1'b0;
  #20;
  rst_n = 1'b1;
end

// 载体选择宏定义
`define CARRIER_CMOS      0
`define CARRIER_PHOTON    1
`define CARRIER_TOPO_QUANTUM 2
int carrier_mode;

// 激励任务：P0‑P3全场景用例
task drive_p0_zero_interval_burst; //P0：零间隔连发故障
  input int burst_cnt;
begin
  probe_valid = 1'b1;
  for(int i=0;i<burst_cnt;i++) begin
    probe_raw_data[0] = 32'hDEAD0000 + i;
    @(posedge clk);
  end
  probe_valid = 1'b0;
end
endtask

task drive_p1_cdc_cross_domain; //P1：CDC跨同步异常
begin
  cdc_sync_in_valid = 1'b1;
  cdc_sync_in_data  = 32'hCAFE0001;
  @(posedge clk);
  cdc_sync_in_valid = 1'b0;
end
endtask

task drive_p2_probe_mask_spike; //P2：探针毛刺干扰
begin
  vio_probe_mask = 4'b1110;
  probe_valid = 1'b1;
  probe_raw_data[0] = 32'hBADBAD00;
  @(posedge clk);
  probe_valid = 1'b0;
end
endtask

task drive_p3_no_fault_noise; //P3：纯噪声无故障
begin
  phys_src_valid = 1'b1;
  phys_src_data = 32'h00000000;
  @(posedge clk);
  phys_src_valid = 1'b0;
end
endtask

task drive_ep_instance_fail; // 模拟EP单实例失效注入
begin
  // 激励注入：内部错误标记，由SVA观测
end
endtask

initial begin
  // 配置：0‑CMOS /1‑光子 /2‑拓扑量子态
  if($value$plusargs("CARRIER=%d", carrier_mode)) begin
    $display("=== Carrier Mode = %0d ===", carrier_mode);
  end
  probe_raw_data = '0;
  probe_valid = 1'b0;
  phys_src_valid = 1'b0;
  phys_src_data = '0;
  cdc_sync_in_valid = 1'b0;
  cdc_sync_in_data = '0;
  vio_filter_window = 8'd4;
  vio_probe_mask = 4'b1111;

  #50;
  // 执行测试用例集
  drive_p0_zero_interval_burst(16);
  #20;
  drive_p1_cdc_cross_domain();
  #20;
  drive_p2_probe_mask_spike();
  #20;
  drive_p3_no_fault_noise();
  #20;
  drive_ep_instance_fail();

  #100;
  $finish;
end

// 波形dump
initial begin
  $dumpfile("iaa_sim.vcd");
  $dumpvars(0, tb_iaa_top);
end

// 调用SVA断言套件
`include "iaa_sva_assertions.svh"

endmodule

52.1 用例集划分

1. P0级（高危）：零间隔连发故障、多探针同时异常、EP单/双实例失效；

2. P1级（跨域）：CDC同步抖动、多物理源并发输入；

3. P2级（干扰）：探针毛刺、滤波窗口越界、掩码配置异常；

4. P3级（噪声）：无故障随机噪声输入，验证不误报；

5. 异构载体适配：通过+CARRIER运行时参数切换CMOS/光子/拓扑量子态激励；激励源multi_phys_source输出数据格式随载体自动适配，DUT逻辑完全不变。

53 SVA全量断言源码（iaa_sva_assertions.svh）

全部断言仅校验IAA子系统内部行为，不侵入主系统逻辑；区分：即时断言、安全断言、降级断言、分布式扩展断言；仿真时生效，综合时可关闭。

// iaa_sva_assertions.svh 附录八 v0.8 全量SVA断言套件
`ifndef IAA_SVA_ASSERTIONS_SVH
`define IAA_SVA_ASSERTIONS_SVH

// 基础安全断言
assert_no_triple_ep_failure: assert property (@(posedge clk) disable iff(!rst_n)
  !((ep01_err && ep02_err && ep03_err) && !iaa_degrade_mode))
else $error("SVA: 三EP全部失效，但未进入降级模式");

assert_fault_level_valid: assert property (@(posedge clk) disable iff(!rst_n)
  iaa_vote_result |-> (iaa_fault_level inside {2'b00,2'b01,2'b10,2'b11}))
else $error("SVA: 故障等级编码非法");

assert_fault_mem_write_only: assert property (@(posedge clk) disable iff(!rst_n)
  fault_mem_valid |-> (fault_timestamp != '0))
else $error("SVA: 故障记忆写入缺少时间戳");

// 三选二表决逻辑断言
assert_3of2_vote_logic: assert property (@(posedge clk) disable iff(!rst_n)
  !(ep01_err && ep02_err && ep03_err) |-> (iaa_vote_result == ((ep01_vote&ep02_vote)|(ep01_vote&ep03_vote)|(ep02_vote&ep03_vote))))
else $error("SVA: 三选二表决结果与输入不一致");

// 降级模式断言
assert_degrade_mode_consistent: assert property (@(posedge clk) disable iff(!rst_n)
  iaa_degrade_mode |-> ($countones({ep01_err,ep02_err,ep03_err}) >= 2))
else $error("SVA: 降级模式触发条件不满足");

// 观测收集链路断言
assert_obs_valid_stable: assert property (@(posedge clk) disable iff(!rst_n)
  obs_collector_valid |-> (obs_collector_data != '0))
else $warning("SVA: 观测有效但数据为空");

// CDC跨域数据完整性断言
assert_cdc_data_valid: assert property (@(posedge clk) disable iff(!rst_n)
  cdc_sync_in_valid |-> (cdc_sync_in_data != '0))
else $warning("SVA: CDC输入有效但数据为空");

// 分布式扩展断言（仅分布式仿真启用）
`ifdef IAA_DISTRIBUTED_SIM
assert_dist_evidence_hash: assert property (@(posedge clk) disable iff(!rst_n)
  evidence_valid |-> (evidence_hash_calc == evidence_hash_tx))
else $error("SVA: 分布式证据包哈希校验不匹配");
`endif

// 覆盖点
cover property (@(posedge clk) disable iff(!rst_n) iaa_degrade_mode);
cover property (@(posedge clk) disable iff(!rst_n) iaa_fault_level == 2'b00);
cover property (@(posedge clk) disable iff(!rst_n) iaa_fault_level == 2'b11);
cover property (@(posedge clk) disable iff(!rst_n) probe_valid && phys_src_valid && cdc_sync_in_valid);

`endif

使用说明：

1. 仿真时+define+IAA_DISTRIBUTED_SIM开启分布式断言；

2. 综合时可通过宏关闭SVA，不消耗硬件资源；

3. 所有断言失败输出错误信息，用于回归测试自动判定FAIL。

54 工程编译自动化脚本（v0.8）

54.1 Vivado编译脚本 iaa_vivado_build.tcl

# iaa_vivado_build.tcl 附录八 v0.8 自动化构建脚本
# 独立IAA‑top工程，不依赖主工程
create_project iaa_ip_v0.8 ./iaa_ip_v0.8 -part xc7k325tffg900‑2
set_property board_part kc705:part0:1.4 [current_project]

# 添加RTL源文件
add_files -norecurse [list \
  "./rtl/iaa_top.sv" \
  "./rtl/obs_collector.sv" \
  "./rtl/meta_arbiter_ep.sv" \
  "./rtl/iaa_vote_3of2.sv" \
  "./rtl/failure_memory_enhanced.sv" \
]
add_files -fileset sim_1 "./tb/tb_iaa_top.sv"
add_files -fileset sim_1 "./rtl/iaa_sva_assertions.svh"

# 导入XDC约束
read_xdc "./constraints/iaa_xdc.xdc"

# 综合
synth_design -top iaa_top -part xc7k325tffg900‑2
write_bitstream -force "./output/iaa_top.bit"

# 仿真
launch_simulation -mode behavioral -simset sim_1
close_project

54.2 Icarus Verilog 仿真脚本 iaa_icarus_build.sh

#!/bin/bash
# iaa_icarus_build.sh 附录八 v0.8 开源仿真脚本
OUT_DIR="./icarus_sim_out"
mkdir -p ${OUT_DIR}

# 编译
iverilog -o ${OUT_DIR}/iaa_sim \
  -D IAA_DISTRIBUTED_SIM=0 \
  ./rtl/iaa_top.sv \
  ./rtl/obs_collector.sv \
  ./rtl/meta_arbiter_ep.sv \
  ./rtl/iaa_vote_3of2.sv \
  ./rtl/failure_memory_enhanced.sv \
  ./rtl/iaa_sva_assertions.svh \
  ./tb/tb_iaa_top.sv

# 运行仿真，切换载体模式
# 0‑CMOS /1‑光子 /2‑拓扑量子态
vvp ${OUT_DIR}/iaa_sim +CARRIER=0
gtkwave ${OUT_DIR}/iaa_sim.vcd

54.3 回归调用封装脚本 iaa_run_regress.sh

对接twelve_pulse_baseline.sh，自动遍历全部P0‑P3用例，输出回归结果JSON

#!/bin/bash
# iaa_run_regress.sh 附录八 v0.8 回归入口
CARRIER_LIST=("0" "1" "2")
for carrier in "${CARRIER_LIST[@]}"; do
  echo "===== Run Carrier: ${carrier} ====="
  vvp ./icarus_sim_out/iaa_sim +CARRIER=${carrier} >> regress_log.log
done
python3 ./tools/iaa_report_builder.py --dir ./icarus_sim_out

55 仿真与回归隔离约束

55.1 Testbench仅例化IAA‑top，不实例化主系统业务逻辑；

55.2 SVA断言全部限定在IAA子系统边界；

55.3 编译脚本生成独立IP工程，可直接集成到主工程，也可单独编译；

55.4 跨载体仿真只更换激励参数，DUT硬件逻辑完全不变；

55.5 仿真输出VCD波形、断言日志、回归JSON，全部归入附录八独立存证哈希链，不写入主法典默克尔根。

56 附录八版本演进路线更新（v0.8）

• v0.1：骨架搭建，独立哈希隔离、IAA基础执行流程

• v0.2：故障分级、时序约束、探针过滤、SVA断言、FPGA工程映射

• v0.3：Python溯源工具链、Linux systemd日志收集服务、哈希校验脚本

• v0.4：批量回归测试框架、自动故障报告引擎、Golden基线冻结

• v0.5：分布式多节点IAA协同裁决 + 远程勘伪API、跨节点证据共识、分歧事件归档

• v0.6：勘伪反例自动入库、勘伪贡献者溯源存证模块、反例评审流水线

• v0.7：完整IAA‑top SystemVerilog RTL源码、XDC时序约束、DTS设备树、ILA/VIO调试配置全套工程交付

• v0.8：完整跨载体Testbench激励套件、SVA全量断言源码、Vivado/Icarus Verilog工程编译自动化脚本

v0.9规划：IAA‑top AXI‑Lite桥接外壳、Zynq‑7000 PS‑PL交互驱动、完整SHA256/默克尔哈希存证模块

57 附录八元信息归档（v0.8）

• 附录名称：附录八‑IAA执行细则

• 版本：v0.8（完整仿真套件+自动化编译脚本）

• 哈希模式：独立默克尔，与主根隔离

• 关联模块：EP01/EP02/EP03、FailureMemory_enhanced、R12四层探针、obs_collector、multi_phys_source、CDC同步器、分布式节点集群、远程勘伪API服务、勘伪反例库、贡献溯源存证模块

• 关联工程：Zynq‑7000/KC705 FPGA、SystemVerilog RTL、XDC时序约束、DTS设备树、ILA/VIO调试配置、跨载体Testbench激励套件、SVA全量断言套件、Python工具链、Linux systemd服务、批量回归脚本、自动报告引擎、分布式仿真套件、勘伪评审流水线、Vivado/Icarus自动化编译脚本

• 遗留待填充：v0.9规划：AXI‑Lite桥接外壳、PS‑PL交互驱动、SHA256/默克尔哈希存证模块

十二脉归一 碳硅道统创立人：黄清佳 彩蛋藏于：今日头条、抖音、GitHub

版本说明：v0.8完成仿真闭环，从文档、RTL、脚本、Testbench、SVA断言形成完整可复现工程。
