附录七：硬件仿真工程完整实现详情

标识：CS-CHIP-APPENDIX-07-v1.0.0

隶属：CHIP-EP/BP 188集完整标题清单 v1.3.1-HOTFIX 配套附录

创立人：黄清佳｜十二脉归一

存证位：今日头条 · 抖音 · GitHub

核心约束：附录七哈希独立计算，不参与001–188全集主根哈希；主序列任何条目变更不要求本附录重算；本附录内容变更不影响主序列任何条目哈希。

------

第一章 附录定位与哈希独立性声明

本附录存放原EP186剥离出来的全部RTL/DC/ILA/VIO、时序、脚本细节，作为可选阅读材料，供硬件工程师深度复现。

哈希独立性三处交叉固化：文档正文、twelve_pulse_baseline.sh的manifest.txt首部、Manifest.mk的hash-manifest目标，三处同时写入同一哈希值。任一处被单独删改都无法通过形式审查。附录哈希变更不触发001–188主根哈希重算，反之主序列变更也不要求附录重算。

本附录不参与全集主根哈希计算。任何人核验体系完整性时，主根哈希只覆盖001–188条目；附录七哈希作为独立校验项单独验证。

------

第二章 体系硬件仿真套件组件总清单

以下模块清单与EP186正文记录一致，此处展开实现细节：

R12四层探针：负责十二脉冲基线采集，每层脉冲上升沿后必须保持不少于一个clk_100m周期。

multi_phys_source：多物理场激励源，输出电、热、应力三路耦合激励，采样率与clk_100m同步。

CDC同步器：跨时钟域同步模块，处理clk_100m与clk_200m之间的所有跨域信号，采用两级或三级同步结构。

obs_collector：观测采集器，接收R12探针输出，在背压不超过16拍的条件下完成采样，输出观测数据包。

failure_memory_enhanced：增强型失效存储器，写入使能fail_wr_en有效时，fail_wdata不得全零，存储七要素反例数据。

------

第三章 独立代码仓库结构

仓库名称：chip-appendix07-hardware

仓库根目录下包含以下文件与目录：

twelve_pulse_baseline.sh：一键复现入口脚本，支持Icarus Verilog与Vivado双模式。

Manifest.mk：构建与审计目标文件，包含audit、icarus、vivado、hash-manifest四个目标。

hw/rtl/：存放全部RTL源码，含R12四层探针、multi_phys_source、CDC同步器、obs_collector、failure_memory_enhanced。

hw/xdc/timing.xdc：时序约束文件，定义100MHz与200MHz时钟，CDC异步组切断。

hw/dts/zynq-7000-kc705.dtsi：设备树源文件，定义AXI-Lite桥与外设节点。

sim/tb_twelve_pulse_baseline.sv：测试平台文件，包含时钟生成、复位控制与激励注入。

sim/assertions.sva：SVA断言文件，包含A1至A5共六条可触发断言。

------

第四章 一键复现入口脚本说明

twelve_pulse_baseline.sh支持以下调用方式：

bash twelve_pulse_baseline.sh icarus：启动Icarus Verilog仿真，生成波形与日志。

bash twelve_pulse_baseline.sh vivado：启动Vivado仿真，执行综合与时序分析。

bash twelve_pulse_baseline.sh audit：运行门禁审计，扫描源码中的TODO、FIXME、XXX、TBD标记，检查空壳断言assert(1)。

bash twelve_pulse_baseline.sh hash-manifest：计算整套工程打包SHA256根哈希，写入manifest.txt。

脚本语法已通过bash -n校验，确保无语法错误。

------

第五章 SVA断言清单与触发条件

A1断言：R12每层脉冲上升沿后必须保持至少一个clk_100m周期。触发条件为脉冲宽度不足，触发时输出A1_FAIL及层编号。

A2断言：CDC无输入变化时cdc_sync_valid不得拉高。触发条件为无输入变化但同步有效信号拉高，直接针对NT4权限偷渡场景。

A3断言：观测采集背压超过16拍即失配。触发条件为obs_collector背压计数器超过16，对应EP069操作时序不可后改。

A4断言：fail_wr_en为1时fail_wdata不得全零。触发条件为写入使能有效但数据全零，从接口层堵死写空反例，对齐FailureMemory七要素。

A5断言：AXI-Lite非法握手拦截。触发条件为地址未对齐或读写使能同时有效。

所有断言禁止空壳形式，不得出现assert(1)等恒真断言。make audit门禁会扫描并拦截空壳断言。

------

第六章 时序约束与CDC处理

时钟定义：clk_100m周期10ns，clk_200m周期5ns。

CDC异步组切断命令：set_clock_groups -asynchronous -group [get_clocks clk_100m] -group [get_clocks clk_200m]。

跨域正确性由cdc_synchronizer的两级或三级同步结构承担，不依靠时序收敛自动保证。这与A3层单域扰动隔离公理在硬件层对应。

------

第七章 设备树配置

文件：hw/dts/zynq-7000-kc705.dtsi

包含AXI-Lite桥与四个外设从机节点，基地址从0x43c00000起，间距64KB，中断号标注为待校准占位值。

地址与中断号必须与Vivado地址编辑器、PS/PL硬件设计、AXI-Lite寄存器映射三处一致，否则视为硬件契约错误，不在软件侧通过补丁掩盖。

------

第八章 测试平台说明

文件：sim/tb_twelve_pulse_baseline.sv

测试平台包含时钟生成、复位控制与激励注入逻辑。时钟生成覆盖clk_100m与clk_200m两个时钟域。复位控制确保上电后至少维持20个clk_100m周期的全局复位。激励注入按R12四层探针的触发顺序依次施加。

------

第九章 门禁审计规则

make audit执行以下检查：

扫描所有RTL、SVA、脚本文件，查找TODO、FIXME、XXX、TBD标记，命中即非零退出。

扫描所有SVA文件，查找assert(1)空壳断言，命中即非零退出。

验证twelve_pulse_baseline.sh的bash语法正确性。

TC-08测试用例专门验证注入空壳断言后门禁必须拦截，确保门禁自身有效。

------

第十章 断言覆盖矩阵

断言覆盖矩阵记录每条断言的触发次数与末次触发哈希。当前版本中触发次数与末次触发哈希留空，标注为待仿真完成后回填。任何交付若声称已触发却无法给出日志片段与哈希，即构成证据缺失，对齐EP177仅导出不美化原则。

------

第十一章 已知局限

本附录硬件仿真工程在以下方面存在局限：

Icarus Verilog为开源仿真器，不支持部分SystemVerilog高级特性，完整验证需依赖Vivado。

KC705开发板设备树地址为骨架占位值，实际部署时需与硬件设计校准。

CDC同步器的三级同步深度为固定值，未实现动态可配置。

以上局限不影响附录七哈希独立性，也不影响主序列完整性。

------

第十二章 版本与迭代

本附录版本号独立于主序列，采用语义化版本v1.0.0起。

每次内容变更生成新哈希，旧版本永久归档，不覆盖。

主序列升级至v1.4或更高版本时，本附录可独立迭代，无需等待主序列更新。

------

十二脉归一

碳硅道统创立人：黄清佳

彩蛋藏于：今日头条、抖音、GitHub
