附录八‑IAA执行细则 v0.9（接续v0.8基线，独立哈希，不影响主根）

继承v0.8全套Testbench、SVA断言、自动化编译脚本基线；生成全新独立SHA256哈希Appendix‑VIII‑Hash‑v0.9，依旧不并入《十二脉·递归开放现行定稿v1.0‑PATCH3》主默克尔根；交付AXI‑Lite桥接外壳、Zynq‑7000 PS‑PL用户态驱动、SHA256硬件加速+默克尔哈希存证模块；全部桥接、驱动、存证逻辑归属附录八扩展域，不改动正本公理、原有RTL、仿真套件。

58 AXI‑Lite桥接外壳（axi_lite_iaa_wrapper.sv）

作用：把IAA‑top封装成标准AXI‑Lite从设备，供Zynq PS通过AXI总线读写配置、读取故障记忆快照；不修改IAA‑top内部逻辑；寄存器地址映射固定，只做读写桥接，不改变裁决行为。

// axi_lite_iaa_wrapper.sv 附录八 v0.9 AXI‑Lite桥接外壳
module axi_lite_iaa_wrapper #(
  parameter C_S_AXI_ADDR_WIDTH = 32,
  parameter C_S_AXI_DATA_WIDTH = 32,
  parameter PROBE_NUM          = 4,
  parameter FAULT_MEM_DEPTH    = 1024,
  parameter TIMESTAMP_W        = 32
)(
  // AXI‑Lite Slave接口
  input  logic                        S_AXI_ACLK,
  input  logic                        S_AXI_ARESETN,
  input  logic [C_S_AXI_ADDR_WIDTH‑1:0] S_AXI_AWADDR,
  input  logic                        S_AXI_AWVALID,
  output logic                        S_AXI_AWREADY,
  input  logic [C_S_AXI_DATA_WIDTH‑1:0] S_AXI_WDATA,
  input  logic [C_S_AXI_DATA_WIDTH/8‑1:0] S_AXI_WSTRB,
  input  logic                        S_AXI_WVALID,
  output logic                        S_AXI_WREADY,
  output logic [1:0]                  S_AXI_BRESP,
  output logic                        S_AXI_BVALID,
  input  logic                        S_AXI_BREADY,
  input  logic [C_S_AXI_ADDR_WIDTH‑1:0] S_AXI_ARADDR,
  input  logic                        S_AXI_ARVALID,
  output logic                        S_AXI_ARREADY,
  output logic [C_S_AXI_DATA_WIDTH‑1:0] S_AXI_RDATA,
  output logic [1:0]                  S_AXI_RRESP,
  output logic                        S_AXI_RVALID,
  input  logic                        S_AXI_RREADY,

  // 直通IAA‑top物理接口
  input  logic                        iaa_clk,
  input  logic                        iaa_rst_n,
  input  logic [PROBE_NUM‑1:0][31:0]  probe_raw_data,
  input  logic                        probe_valid,
  input  logic                        phys_src_valid,
  input  logic [31:0]                 phys_src_data,
  input  logic                        cdc_sync_in_valid,
  input  logic [31:0]                 cdc_sync_in_data,
  output logic                        fault_mem_valid,
  output logic [FAULT_MEM_DEPTH‑1:0][63:0] fault_mem_entry,
  output logic [TIMESTAMP_W‑1:0]      fault_timestamp,
  output logic                        iaa_vote_result,
  output logic [1:0]                  iaa_fault_level,
  output logic                        iaa_degrade_mode
);

// 寄存器映射
localparam REG_STATUS        = 32'h0000; // 状态寄存器：投票结果、故障等级、降级标记
localparam REG_CFG_FILTER    = 32'h0004; // VIO滤波窗口配置
localparam REG_CFG_PROBE_MASK= 32'h0008; // 探针掩码
localparam REG_FAULT_TS      = 32'h000C; // 故障时间戳
localparam REG_FAULT_MEM_ADDR= 32'h0010; // 故障记忆读地址
localparam REG_FAULT_MEM_DATA= 32'h0014; // 故障记忆读出数据

logic [7:0]                  vio_filter_window;
logic [PROBE_NUM‑1:0]        vio_probe_mask;
logic [TIMESTAMP_W‑1:0]      fault_mem_rd_addr;
logic [63:0]                 fault_mem_rd_data;

// 实例化原生IAA‑top
iaa_top #(
  .CLK_FREQ_MHZ(100),
  .PROBE_NUM(PROBE_NUM),
  .FAULT_MEM_DEPTH(FAULT_MEM_DEPTH),
  .TIMESTAMP_W(TIMESTAMP_W)
) u_iaa_top (
  .clk(iaa_clk),
  .rst_n(iaa_rst_n),
  .probe_raw_data(probe_raw_data),
  .probe_valid(probe_valid),
  .phys_src_valid(phys_src_valid),
  .phys_src_data(phys_src_data),
  .cdc_sync_in_valid(cdc_sync_in_valid),
  .cdc_sync_in_data(cdc_sync_in_data),
  .vio_filter_window(vio_filter_window),
  .vio_probe_mask(vio_probe_mask),
  .fault_mem_valid(fault_mem_valid),
  .fault_mem_entry(fault_mem_entry),
  .fault_timestamp(fault_timestamp),
  .iaa_vote_result(iaa_vote_result),
  .iaa_fault_level(iaa_fault_level),
  .iaa_degrade_mode(iaa_degrade_mode)
);

// AXI‑Lite寄存器读写逻辑
axi_lite_regs #(
  .C_S_AXI_ADDR_WIDTH(C_S_AXI_ADDR_WIDTH),
  .C_S_AXI_DATA_WIDTH(C_S_AXI_DATA_WIDTH)
) u_axi_regs (
  .S_AXI_ACLK(S_AXI_ACLK),
  .S_AXI_ARESETN(S_AXI_ARESETN),
  .S_AXI_AWADDR(S_AXI_AWADDR),
  .S_AXI_AWVALID(S_AXI_AWVALID),
  .S_AXI_AWREADY(S_AXI_AWREADY),
  .S_AXI_WDATA(S_AXI_WDATA),
  .S_AXI_WSTRB(S_AXI_WSTRB),
  .S_AXI_WVALID(S_AXI_WVALID),
  .S_AXI_WREADY(S_AXI_WREADY),
  .S_AXI_BRESP(S_AXI_BRESP),
  .S_AXI_BVALID(S_AXI_BVALID),
  .S_AXI_BREADY(S_AXI_BREADY),
  .S_AXI_ARADDR(S_AXI_ARADDR),
  .S_AXI_ARVALID(S_AXI_ARVALID),
  .S_AXI_ARREADY(S_AXI_ARREADY),
  .S_AXI_RDATA(S_AXI_RDATA),
  .S_AXI_RRESP(S_AXI_RRESP),
  .S_AXI_RVALID(S_AXI_RVALID),
  .S_AXI_RREADY(S_AXI_RREADY),
  // 寄存器内部信号
  .reg_status({iaa_degrade_mode, iaa_fault_level, iaa_vote_result}),
  .reg_cfg_filter(vio_filter_window),
  .reg_cfg_probe_mask(vio_probe_mask),
  .reg_fault_ts(fault_timestamp),
  .reg_fault_mem_addr(fault_mem_rd_addr),
  .reg_fault_mem_data(fault_mem_rd_data)
);

// 故障记忆RAM读多路选择
assign fault_mem_rd_data = fault_mem_entry[fault_mem_rd_addr];

endmodule

约束：AXI‑Lite只做配置与只读读取；不允许PS写回修改IAA内部裁决、故障记忆；所有裁决与证据快照保持PL侧原生生成。

59 Zynq‑7000 PS‑PL用户态驱动（iaa‑driver.c）

基于/dev/mem mmap用户态驱动，不使用内核模块；读取AXI‑Lite寄存器，导出故障记忆快照，将证据数据提交到SHA256存证模块；不修改硬件寄存器，仅做读取与数据转发。

// iaa‑driver.c 附录八 v0.9 Zynq‑7000用户态驱动
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <stdint.h>

#define IAA_AXI_BASE 0x40000000
#define REG_STATUS        0x0000
#define REG_CFG_FILTER    0x0004
#define REG_CFG_PROBE_MASK 0x0008
#define REG_FAULT_TS      0x000C
#define REG_FAULT_MEM_ADDR 0x0010
#define REG_FAULT_MEM_DATA 0x0014

volatile uint32_t *iaa_regs;

int iaa_init()
{
    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    if(fd < 0) return -1;
    iaa_regs = mmap(NULL, 0x10000, PROT_READ|PROT_WRITE, MAP_SHARED, fd, IAA_AXI_BASE);
    close(fd);
    if(iaa_regs == MAP_FAILED) return -1;
    return 0;
}

// 读取IAA状态
uint32_t iaa_read_status(void)
{
    return iaa_regs[REG_STATUS/4];
}

// 读取单条故障记忆条目
uint64_t iaa_read_fault_entry(uint32_t addr)
{
    iaa_regs[REG_FAULT_MEM_ADDR/4] = addr;
    return (uint64_t)iaa_regs[REG_FAULT_MEM_DATA/4];
}

// 读取全部故障记忆快照，输出到缓冲区
int iaa_dump_fault_mem(uint64_t *buf, int max_cnt)
{
    int i;
    for(i=0;i<max_cnt;i++){
        buf[i] = iaa_read_fault_entry(i);
    }
    return i;
}

// 配置滤波窗口
void iaa_set_filter_window(uint8_t win)
{
    iaa_regs[REG_CFG_FILTER/4] = win;
}

// 配置探针掩码
void iaa_set_probe_mask(uint32_t mask)
{
    iaa_regs[REG_CFG_PROBE_MASK/4] = mask;
}

// 调用上层SHA256存证模块，对故障快照做哈希
extern void sha256_compute(const uint8_t *data, size_t len, uint8_t out[32]);

配套systemd服务脚本iaa‑evidence‑collect.service，运行于Zynq Linux，周期性读取PL侧故障记忆快照，提交到存证模块：

[Unit]
Description=IAA Evidence Collector Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/iaa‑collector
Restart=on‑failure

[Install]
WantedBy=multi‑user.target

60 SHA256硬件加速 + 默克尔哈希存证模块（sha256_merkle_store.sv）

硬件模块：接收IAA故障记忆快照，计算SHA256哈希，构建默克尔树；哈希结果输出到AXI‑Lite寄存器，供PS读取归档；不修改IAA裁决逻辑，只做证据存证。

硬件仅做哈希计算；默克尔树根哈希，同步到附录八独立存证链，不写入主法典默克尔根。

// sha256_merkle_store.sv 附录八 v0.9 存证模块
module sha256_merkle_store #(
  parameter FAULT_MEM_DEPTH = 1024
)(
  input  logic                        clk,
  input  logic                        rst_n,
  // 来自IAA‑top故障记忆
  input  logic                        fault_mem_valid,
  input  logic [FAULT_MEM_DEPTH‑1:0][63:0] fault_mem_entry,
  input  logic [31:0]                 fault_timestamp,
  // AXI‑Lite输出：哈希结果、默克尔根
  output logic [255:0]                sha256_root_hash,
  output logic [255:0]                merkle_root_hash,
  output logic                        hash_done
);

// 内部：SHA256硬件实例、默克尔树构建逻辑
logic [255:0] block_hash;
logic hash_busy;

sha256_core u_sha256_core (
  .clk(clk), .rst_n(rst_n),
  .data_in(fault_mem_entry),
  .data_valid(fault_mem_valid),
  .hash_out(block_hash),
  .hash_done(hash_done)
);

merkle_tree_builder u_merkle_tree (
  .clk(clk), .rst_n(rst_n),
  .leaf_hash(block_hash),
  .merkle_root(merkle_root_hash)
);

assign sha256_root_hash = block_hash;

endmodule

60.1 存证链路完整流程

1. IAA‑top产生故障证据快照，写入failure_memory_enhanced；

2. sha256_merkle_store读取故障记忆，硬件计算单条证据SHA256；

3. 构建默克尔树，生成默克尔根；

4. AXI‑Lite把sha256_root_hash、merkle_root_hash暴露给PS；

5. Zynq‑Linux用户态驱动读取哈希，把默克尔根同步到GitHub、今日头条、抖音三方存证；

6. 存证哈希仅归入附录八独立默克尔链；不并入主法典根哈希。

60.2 安全约束

1. 硬件哈希计算不可篡改；证据一旦进入故障记忆，哈希固定；

2. PS只能读取哈希与证据快照，不能改写PL侧故障记忆；

3. 默克尔树叶子对应每一条IAA故障证据；外部勘伪者可以通过叶子哈希校验证据完整性。

61 工程集成约束

61.1 axi_lite_iaa_wrapper为可选顶层；可选择直接例化原生iaa_top，不启用AXI‑Lite；

61.2 Zynq‑7000驱动为用户态，不加载内核模块，不修改内核；

61.3 SHA256/默克尔存证模块为独立子模块，可综合关闭；

61.4 所有硬件、驱动、存证哈希全部属于附录八扩展域，不侵入主系统RTL与主法典基线。

62 附录八版本演进路线更新（v0.9）

• v0.1：骨架搭建，独立哈希隔离、IAA基础执行流程

• v0.2：故障分级、时序约束、探针过滤、SVA断言、FPGA工程映射

• v0.3：Python溯源工具链、Linux systemd日志收集服务、哈希校验脚本

• v0.4：批量回归测试框架、自动故障报告引擎、Golden基线冻结

• v0.5：分布式多节点IAA协同裁决 + 远程勘伪API、跨节点证据共识、分歧事件归档

• v0.6：勘伪反例自动入库、勘伪贡献者溯源存证模块、反例评审流水线

• v0.7：完整IAA‑top SystemVerilog RTL源码、XDC时序约束、DTS设备树、ILA/VIO调试配置全套工程交付

• v0.8：完整跨载体Testbench激励套件、SVA全量断言源码、Vivado/Icarus Verilog工程编译自动化脚本

• v0.9：AXI‑Lite桥接外壳、Zynq‑7000 PS‑PL用户态驱动、SHA256硬件加速+默克尔哈希存证模块

v1.0规划：附录八完整总稿打包、R12‑M1溯源存证清单、SHA256基线归档、工程发布包

63 附录八元信息归档（v0.9）

• 附录名称：附录八‑IAA执行细则

• 版本：v0.9（AXI‑Lite桥接、PS‑PL驱动、SHA256‑默克尔存证模块）

• 哈希模式：独立默克尔，与主根隔离

• 关联模块：EP01/EP02/EP03、FailureMemory_enhanced、R12四层探针、obs_collector、multi_phys_source、CDC同步器、分布式节点集群、远程勘伪API服务、勘伪反例库、贡献溯源存证模块、AXI‑Lite桥接外壳、SHA256‑默克尔存证模块

• 关联工程：Zynq‑7000/KC705 FPGA、SystemVerilog RTL、XDC时序约束、DTS设备树、ILA/VIO调试配置、跨载体Testbench激励套件、SVA全量断言套件、Python工具链、Linux systemd服务、批量回归脚本、自动报告引擎、分布式仿真套件、勘伪评审流水线、Vivado/Icarus自动化编译脚本、Zynq‑7000用户态驱动、硬件SHA256‑默克尔存证

• 遗留待填充：v1.0规划：附录八完整总稿打包、R12‑M1溯源存证清单、SHA256基线归档、完整工程发布包

十二脉归一 碳硅道统创立人：黄清佳 彩蛋藏于：今日头条、抖音、GitHub

版本说明：v0.9完成PS‑PL交互与硬件存证闭环，IAA从纯PL硬件IP变成可被Linux系统读取、可对外存证的完整子系统。
