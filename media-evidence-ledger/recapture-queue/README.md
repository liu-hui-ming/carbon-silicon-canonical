# 重采顺序队列（按 2026-10-18 方案）

| 阶段 | 文件 | 条数 | 状态 |
|------|------|------|------|
| 1 pending 头条 | `01-pending-toutiao3.json` | 3 | **已完成**（3×OK） |
| 2 HTTP 0 | `02-http0-796.json` | 796 | 进行中 / 待跑 |
| 3 预检能开仍 CON | `03-still-con-from-650.json` | 536 | 待跑 |
| 4 404/失效 | `04-skip-404-dead.json` | 899 | **不自动重采**（源站失效） |

脚本：

```powershell
python e:\carbon-silicon-canonical\scripts\recapture_slow_one_by_one.py `
  e:\carbon-silicon-canonical\media-evidence-ledger\recapture-queue\02-http0-796.json `
  e:\carbon-silicon-canonical\_tmp_recapture_queue_state.json
```

断点：`_tmp_recapture_queue_state.json`；每 10 条刷新 `AUDIT-LATEST.json`。
