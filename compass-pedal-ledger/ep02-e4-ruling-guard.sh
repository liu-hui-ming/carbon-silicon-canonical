#!/usr/bin/env bash
# ============================================================
# ep02-e4-ruling-guard.sh — EP02-MOTIVE-OS-R1.2 落盘前置校验脚本
# 版本：v1.0 ｜ 生成：2026-10-22 20:48 ｜ 生成方：帝王龙虾·穹主
# 依据：创立人黄清佳落盘执行纪律（刚性约束）定稿
# 纯文本实现：仅依赖 bash + grep + sha256sum，无 YAML 解析器
# 用法：
#   ./ep02-e4-ruling-guard.sh check            # 三项校验（阻塞项/哈希空值/时间阈值）
#   ./ep02-e4-ruling-guard.sh verify FILE...   # 逐文件 sha256sum 全量实测
#   ./ep02-e4-ruling-guard.sh force-rename FILE... # E4-02 到期强制执行 MOTIVE-L1~L4 全局替换
# 退出码：0=全部通过  1=存在 FAIL  2=存在 WARN  3=参数错误
# ============================================================

set -u
LEDGER="${LEDGER:-$(dirname "$0")/ep02-motive-os-R1.2-pending-rulings.yaml}"
DEADLINE_EPOCH="${DEADLINE_EPOCH:-$(date -d '2026-10-23 20:00:00 +0800' +%s)}"
NOW_EPOCH="$(date +%s)"
PASS=0; FAIL=0; WARN=0

ok()   { echo "  [PASS] $1"; PASS=$((PASS+1)); }
bad()  { echo "  [FAIL] $1"; FAIL=$((FAIL+1)); }
warn() { echo "  [WARN] $1"; WARN=$((WARN+1)); }

cmd_check() {
  echo "== EP02-E4 落盘前置校验 $(date '+%F %T %z') =="
  echo "[1] 元数据文件存在性"
  if [ -f "$LEDGER" ]; then ok "ledger 存在: $LEDGER"; else bad "ledger 缺失: $LEDGER"; echo "== 结果: $PASS P / $FAIL F / $WARN W (exit 1) =="; exit 1; fi

  echo "[2] 时间阈值校验"
  if [ "$NOW_EPOCH" -lt "$DEADLINE_EPOCH" ]; then
    ok "未超裁定截止（剩余 $(( (DEADLINE_EPOCH-NOW_EPOCH)/60 )) 分钟，截止 2026-10-23 20:00+08:00）"
  else
    warn "已过裁定截止——触发 E4-02 强制执行路径，其余四项未裁则整卷延后"
  fi

  echo "[3] 阻塞项 RUL-PEND-E4-02（MOTIVE-L1~L4 命名空间，evidence_grade: A）"
  # 判定是否已裁定：裁定后应为 resolved: true（或裁定栏存在），否则视为未裁
  if grep -qE 'RUL-PEND-E4-02:.*resolved[[:space:]]*:.*true' "$LEDGER" \
     || grep -qE 'E4-02_status[[:space:]]*:[[:space:]]*RESOLVED' "$LEDGER"; then
    ok "E4-02 已裁定闭环"
  else
    if [ "$NOW_EPOCH" -lt "$DEADLINE_EPOCH" ]; then
      bad "E4-02 未裁定且为 blocking: true——阻塞整卷归档，须会签或到期强制执行"
    else
      warn "E4-02 超期未裁——按纪律强制执行 force-rename（MOTIVE-L1~L4 全局替换）"
    fi
  fi

  echo "[4] 非阻塞项 E4-01/03/04/05 处置状态"
  for id in 01 03 04 05; do
    if grep -qE "RUL-PEND-E4-${id}:.*resolved[[:space:]]*:.*true" "$LEDGER" \
       || grep -qE "E4-${id}_status[[:space:]]*:[[:space:]]*RESOLVED" "$LEDGER"; then
      ok "E4-${id} 已裁定"
    else
      warn "E4-${id} 未裁定（非阻塞，可延后至落盘动作前；到点未裁则整卷归档延后，绝不降级放行）"
    fi
  done

  echo "[5] 哈希空值校验（铁则：落盘前必须 PENDING，禁止预填；落盘瞬间实测回填）"
  # 兼容两种格式：单行 file_hash_status:[...] 或逐件 hash: PENDING（lineage 块）
  HASHLINE="$(grep -E 'file_hash_status' "$LEDGER" | head -1)"
  PERLINE="$(grep -cE '(^|[[:space:],{])hash:[[:space:]]*PENDING' "$LEDGER")"
  case "$HASHLINE" in
    *PENDING*)
      # 单行格式：逐 token 校验
      # 落盘阶段：允许已实测回填（64 位十六进制），禁止占位/伪造值
      PLACEHOLDER=0; REAL=0
      for h in $(echo "$HASHLINE" | grep -oE '[A-Za-z0-9]+' | grep -vE '^(file_hash_status)$'); do
        if [ "$h" = "PENDING" ]; then PLACEHOLDER=$((PLACEHOLDER+1));
        elif echo "$h" | grep -qE '^[0-9a-f]{64}$'; then REAL=$((REAL+1));
        else PLACEHOLDER=$((PLACEHOLDER+1)); bad "非法哈希占位值: $h（既非 PENDING 也非 64 位实测值，疑似伪造）"; fi
      done
      if [ "$PLACEHOLDER" -eq 0 ] && [ "$REAL" -eq 4 ]; then
        ok "四件哈希均为 64 位实测回填（落盘完成态）——建议跑 verify 复核实测一致性"
      elif [ "$PLACEHOLDER" -gt 0 ] && [ "$REAL" -gt 0 ]; then
        warn "部分回填（实测 $REAL / PENDING $PLACEHOLDER）——逐件落盘进行中，继续至 4/4"
      fi;;
    *)
      # 逐件格式（lineage 块 hash: PENDING）
      if [ "$PERLINE" -eq 4 ]; then
        ok "四件哈希均为 PENDING（lineage 逐件格式，落盘前正确状态）"
      elif [ "$PERLINE" -eq 0 ]; then
        bad "未找到任何哈希状态位（file_hash_status 与 hash: 均缺失）"
      else
        # 逐件格式下的回填进度：统计 64 位实测值
        REAL="$(grep -cE '(^|[[:space:],{])hash:[[:space:]]*[0-9a-f]{64}' "$LEDGER")"
        warn "部分回填（实测 $REAL / PENDING $PERLINE）——逐件落盘进行中，继续至 4/4"
        PLACEHOLDER_HOLD=1
      fi;;
  esac

  echo "== 结果: $PASS PASS / $FAIL FAIL / $WARN WARN =="
  if   [ "$FAIL" -gt 0 ]; then echo "判定: BLOCKED（阻塞项未闭环）"; exit 1
  elif [ "$WARN" -gt 0 ]; then echo "判定: CONDITIONAL（可继续，带警示）"; exit 2
  else echo "判定: GO（五项前置齐备，可触发落盘）"; exit 0; fi
}

cmd_verify() {
  [ $# -ge 1 ] || { echo "用法: $0 verify FILE..."; exit 3; }
  echo "== sha256sum 全量实测（唯一完成态凭据） =="
  for f in "$@"; do
    if [ -f "$f" ]; then sha256sum "$f"; else bad "文件缺失: $f"; fi
  done
  [ "$FAIL" -eq 0 ] || exit 1
  exit 0
}

cmd_force_rename() {
  # E4-02 强制执行：裸 L1~L4 → MOTIVE-L1~MOTIVE-L4
  # 铁律：仅替换裸 L 编号 token，不触碰已带前缀的 ARC-/STACK-/PIPE- 命名空间
  [ $# -ge 1 ] || { echo "用法: $0 force-rename FILE..."; exit 3; }
  echo "== force-rename（E4-02 超期强制执行） =="
  for f in "$@"; do
    [ -f "$f" ] || { bad "文件缺失: $f"; continue; }
    sed -i -E 's/(^|[^A-Za-z0-9-])L([1-4])([^A-Za-z0-9-]|$)/\1MOTIVE-L\2\3/g' "$f"
    if grep -qE '(^|[^A-Za-z0-9-])L[1-4]([^A-Za-z0-9-]|$)' "$f"; then
      bad "残留裸 L 编号: $f"
    else
      ok "替换完成且无残留: $f"
    fi
  done
  [ "$FAIL" -eq 0 ] || exit 1
  exit 0
}

case "${1:-}" in
  check)        cmd_check;;
  verify)       shift; cmd_verify "$@";;
  force-rename) shift; cmd_force_rename "$@";;
  *) echo "用法: $0 check | verify FILE... | force-rename FILE..."; exit 3;;
esac