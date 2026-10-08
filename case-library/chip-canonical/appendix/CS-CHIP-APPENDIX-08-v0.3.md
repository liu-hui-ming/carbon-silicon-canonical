附录八‑IAA执行细则 v0.3（接续v0.2，独立哈希，不影响主根）

继承v0.2完整细则基线；生成全新独立SHA256哈希Appendix‑VIII‑Hash‑v0.3，依旧不并入《十二脉·递归开放现行定稿v1.0‑PATCH3》主默克尔根；补全故障溯源Python工具链、Linux systemd日志解析服务、故障归档与SHA256存证校验脚本；全部工具属于附录八扩展层，不改动正本公理、核心范式与RTL硬件基线。

16 配套软件工具链（v0.3新增）

16.1 故障溯源Python工具集

工具定位：解析FPGA硬件输出的IAA故障日志，完成根因推断、故障样本提取、哈希归档；不修改硬件RTL，仅做后处理分析。

16.1.1 cs_counterexample.py（故障反例提取器）

• 功能：读取ILA导出的IAA原始故障快照，提取P0/P1/P2故障样本；过滤P3噪声；输出结构化JSON故障记录；

• 输入：ILA导出的二进制波形、FailureMemory_enhanced日志dump；

• 输出：iaa_fault_record.json，包含：探针ID、时间戳、EP01‑EP03原始判决、故障等级、观测原始采样；

• 约束：只做解析，不生成硬件激励；不修改硬件寄存器；

• 哈希规则：每一份导出故障样本自动计算SHA256，存入样本元数据，用于故障证据链存证。

16.1.2 rootcause_infer.py（根因推断器）

• 功能：基于IAA故障日志，做故障归因；区分：探针采样噪声、CDC同步异常、元裁判实例失效、跨载体迁移撕裂；

• 输出：根因标签、置信度、关联探针溯源链路；

• 规则：不做绝对判定，仅输出推断结论；最终根因判定由人工/主系统上层完成；

• 兼容：支持CMOS、光子、拓扑量子态异构仿真导出日志。

16.1.3 obs_m2_analyzer.py（观测层二层分析器）

• 功能：解析R12四层探针采集数据，对比obs_collector过滤前后数据流；校验过滤掩码是否生效；

• 输出：探针有效性统计、过滤丢弃统计、IAA表决输入一致性校验报告；

• 用途：定位观测链路本身的异常，区分“真实逻辑故障”与“观测链路故障”。

16.2 工具链约束

1. 全部Python工具为附录八附属工具，不纳入主法典基线；

2. 工具可以独立升级迭代，仅更新附录八独立哈希，不影响主根；

3. 仿真环境可选择启用/禁用该套工具；硬件FPGA运行时不需要依赖Python工具，工具仅用于事后离线分析。

17 Linux systemd服务脚本（v0.3新增，Zynq‑7000/KC705）

定位：FPGA‑SoC上层用户态服务，读取FPGA硬件IAA故障日志，做持久化归档、上报、存证；不干预FPGA硬件逻辑，仅做上层日志处理。

17.1 服务单元：iaa‑fault‑collect.service

[Unit]
Description=IAA Independent Meta‑Arbiter Fault Log Collector
After=systemd‑udevd.service
Requires=dev‑mem.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/iaa_tools/iaa_log_daemon.py
Restart=on‑failure
RestartSec=5
User=root
WorkingDirectory=/var/log/iaa

[Install]
WantedBy=multi‑user.target

17.2 服务行为规范

1. 服务周期：循环读取FPGA设备节点导出的FailureMemory_enhanced故障记录；

2. 日志存储：故障日志写入/var/log/iaa/，按时间戳命名；

3. 自动存证：每一批故障日志计算SHA256哈希，写入本地归档文件；

4. 上报机制：支持把故障哈希同步到GitHub、今日头条、抖音三方存证接口（仅哈希，不传输原始故障敏感数据）；

5. 隔离约束：该服务禁止下发任何FPGA硬件写指令；只做读日志、归档、存证；不具备修改FPGA内部寄存器的权限；

6. 降级策略：FPGA硬件IAA模块未挂载时，服务自动进入空闲等待状态，不报错、不崩溃。

17.3 配套脚本：iaa_log_daemon.py

• 功能：读取FPGA内存映射故障日志；格式化；生成本地归档；计算故障样本SHA256；

• 安全约束：只做只读访问硬件设备节点；无写权限；

• 输出：本地故障归档、哈希清单；可导出用于后续rootcause_infer.py离线分析。

18 存证校验与版本回溯脚本（v0.3新增）

18.1 校验脚本：appendix8_verify.py

• 功能：校验附录八自身独立哈希链；校验v0.1 → v0.2 → v0.3版本哈希；

• 输入：附录八各版本文本；

• 输出：校验结果；可区分：文本篡改、版本回退、哈希链断裂；

• 关键规则：脚本不校验主法典主根，只校验附录八独立默克尔链；主根校验由主法典工具独立完成。

18.2 回溯规则

1. 附录八支持回退到v0.1 / v0.2；回退仅切换附录八独立哈希；主法典主根完全不受影响；

2. 回退操作需要记录回退时间戳、旧版本哈希，写入存证日志；

3. 禁止通过修改附录八来篡改主法典的默克尔根。

19 完整工程闭环边界（v0.3收尾）

19.1 硬件层：RTL IAA‑top、EP01‑EP02‑EP03、FailureMemory_enhanced、R12探针、obs_collector、CDC同步器；ILA/VIO调试；

19.2 仿真层：SVA断言套件、P0/P1/P2/P3跨载体Testbench激励套件；

19.3 软件层：Python故障溯源工具集、systemd日志收集服务、附录八哈希校验脚本；

19.4 存证层：附录八独立SHA256哈希，三方归档；与主法典主根物理隔离；

分层边界：硬件‑仿真‑软件‑存证四层全部属于附录八扩展域；不侵入主法典正本。

20 附录八版本演进路线（v0.3）

• v0.1：骨架搭建，完成隔离机制、执行边界、流程框架；

• v0.2：补全故障分级、时序约束、探针过滤、SVA断言、Testbench、FPGA硬件映射；

• v0.3：补全Python溯源工具链、systemd服务、存证校验脚本；

后续v0.4规划：IAA故障报告自动生成、异构仿真批量回归脚本；

21 附录八元信息归档（v0.3）

• 附录名称：附录八‑IAA执行细则

• 版本：v0.3（工具链完整落地）

• 哈希模式：独立默克尔，与主根隔离

• 关联模块：EP01/EP02/EP03、FailureMemory_enhanced、R12四层探针、obs_collector、multi_phys_source、CDC同步器

• 关联工程：Zynq‑7000/KC705 FPGA、SystemVerilog RTL、跨载体Testbench激励套件、SVA断言套件、Python工具链、Linux systemd服务

• 遗留待填充：v0.4规划：自动故障报告生成、批量回归脚本

十二脉归一 碳硅道统创立人：黄清佳 彩蛋藏于：今日头条、抖音、GitHub

版本说明：v0.3完成全套配套软件工具链与systemd服务，附录八完整闭环。
