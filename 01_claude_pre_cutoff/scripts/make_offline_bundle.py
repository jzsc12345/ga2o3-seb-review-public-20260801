#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_offline_bundle.py -- 生成给二号机（无 Claude、有 Silvaco2024 VM）的离线自治工程包。

设计原则：二号机零智能、零依赖 —— 所有 DoE split 在一号机就展开成具体的独立 case.in
（数值全部由本脚本解析成字面量，不指望 DeckBuild 的变量算术），VictoryDoE 的
@cnode/@m1node 宏同样在打包时替换掉。二号机只需要跑一个 run_all.sh。

同时套用本项目已实测验证的两个修正：
  * E1 单变量实验结论：DC 爬压段去掉 lat.temp（672 次折半 -> 0），瞬态前重新打开；
  * tstart 不是 ATLAS 参数（实测 Invalid parameter），deck 已是 tstop 写法。

产物：outputs/offline/OFFLINE_SEB_BUNDLE_<日期>/ 目录 + 同名 .tar.gz
"""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import re
import shutil
import sys
import tarfile
from pathlib import Path

ROOT = Path(r"D:\SILVACO_LOCAL")
DECKS = ROOT / "decks"
OUTDIR = ROOT / "outputs" / "offline"

GOLDEN = DECKS / "SEB_Ga2O3_VDOE.sdb"
SPLIT = DECKS / "split_SEB_TEMP_DIAG.csv"
TRANSFER = DECKS / "wang2026_ga2o3_emode_transfer.in"


# --------------------------------------------------------------------------
# golden deck 展平
# --------------------------------------------------------------------------
_SET_RE = re.compile(r"^\s*set\s+([A-Za-z_][\w]*)\s*=\s*(.+?)\s*(##!!)?\s*$", re.I)
_NUM_RE = re.compile(r"^[-+0-9.eE]+$")


def _eval_expr(expr: str, env: dict[str, float]) -> float:
    """解析 set 表达式（只含 + - * / () 与 $var 引用），出错就抛。"""
    py = re.sub(r"\$([A-Za-z_][\w]*)", lambda m: repr(env[m.group(1)]), expr)
    if not re.match(r"^[-+*/(). 0-9eE]+$", py):
        raise ValueError(f"unsupported expression: {expr!r}")
    return float(eval(py, {"__builtins__": {}}))  # noqa: S307 - 受上面的白名单约束


def load_golden(path: Path) -> tuple[dict[str, str], list[str]]:
    """返回 (set 变量表, go internal 之后的正文行)。"""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    sets: dict[str, str] = {}
    body_start = None
    for i, ln in enumerate(lines):
        m = _SET_RE.match(ln)
        if m:
            sets[m.group(1)] = m.group(2)
        # 正文从第一个 go atlas 开始（go internal 段只有变量与注释）
        if body_start is None and re.match(r"^\s*go\s+atlas", ln, re.I):
            body_start = i
    if body_start is None:
        raise SystemExit(f"no `go atlas` found in {path}")
    return sets, lines[body_start:]


def resolve_sets(sets: dict[str, str], overrides: dict[str, str]) -> dict[str, str]:
    """把全部 set 解析成字面量字符串（数值算术在这里做掉）。"""
    merged = {**sets, **overrides}
    out: dict[str, str] = {}
    env: dict[str, float] = {}
    pending = dict(merged)
    for _ in range(8):  # 多轮直到不再有可解析项
        progressed = False
        for k, v in list(pending.items()):
            v = v.strip()
            if _NUM_RE.match(v):
                env[k] = float(v)
                out[k] = v
                del pending[k]
                progressed = True
            else:
                try:
                    val = _eval_expr(v, env)
                    env[k] = val
                    out[k] = f"{val:g}"
                    del pending[k]
                    progressed = True
                except Exception:
                    pass
        if not pending or not progressed:
            break
    for k, v in pending.items():   # 非数值（如字符串 tag）原样保留
        out[k] = v
    return out


def flatten_case(sets: dict[str, str], body: list[str], tag: str,
                 overrides: dict[str, str]) -> str:
    resolved = resolve_sets(sets, overrides)
    hdr = [
        "# " + "=" * 76,
        f"# OFFLINE CASE: {tag}",
        f"# generated {_dt.datetime.now():%Y-%m-%d %H:%M} by make_offline_bundle.py",
        f"# overrides: {overrides}",
        "# 修正已内嵌: DC 爬压段无 lat.temp (E1 实测), 瞬态前重开; 无 tstart。",
        "# " + "=" * 76,
        "",
    ]
    hdr += [f"set {k} = {v}" for k, v in resolved.items()]
    hdr.append("")

    out: list[str] = []
    models_line = None
    for ln in body:
        # VDoE 宏 -> case tag；source 行删除
        ln = ln.replace("@cnode", tag).replace("@m1node", tag)
        if re.match(r"^\s*source\s+", ln):
            continue
        if re.match(r"^\s*system\s+echo\s+finished", ln, re.I):
            continue
        m = re.match(r"^\s*models\s+(.*)$", ln, re.I)
        if m and "lat.temp" in ln:
            models_line = ln.strip()
            # E1 修正：DC 段先不带 lat.temp
            out.append("# [E1 修正] DC 爬压段关闭 lat.temp（避免 min.temp=120K 钳位折半）")
            out.append(re.sub(r"\s*lat\.temp", "", ln))
            continue
        out.append(ln)
        # 在 prestrike 保存之后重开 lat.temp
        if models_line and re.search(r"save\s+outf\s*=\s*\S*prestrike", ln, re.I):
            out.append("")
            out.append("# [E1 修正] 瞬态前重开自热并在同一偏置点重收敛")
            out.append(models_line)
            out.append("solve prev")
            models_line = None
    return "\n".join(hdr + out) + "\n"


# --------------------------------------------------------------------------
# runner（VM 内执行，纯 bash，自治）
# --------------------------------------------------------------------------
RUN_ALL = r'''#!/bin/bash
# ============================================================================
# run_all.sh -- 二号机自治 runner。在 Silvaco VM 内执行：
#     cd <解包目录> && nohup bash runner/run_all.sh > run_all.out 2>&1 &
# 特性：断点续跑（case 目录有 STATUS=done 即跳过）；最多 2 个并发（8 vCPU × -P 4）；
#       deckbuild 需要 pty —— 有 X 用 xterm 包，无 X 退回 script-only 并告警；
#       全部结束后自动调 pack_results.sh 打包。
# ============================================================================
set -u
cd "$(dirname "$0")/.." || exit 9
BASE=$(pwd)
MAX_PAR=${MAX_PAR:-2}
CASE_TIMEOUT=${CASE_TIMEOUT:-28800}   # 每 case 上限 8h

export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
export SFLM_SERVERS=${SFLM_SERVERS:-+localhost}
export DISPLAY=${DISPLAY:-:0}
[ -z "${XAUTHORITY:-}" ] && [ -r /var/run/lightdm/root/xauthority ] \
  && export XAUTHORITY=/var/run/lightdm/root/xauthority

echo "== preflight =="
command -v deckbuild >/dev/null || { echo "FATAL: deckbuild 不在 PATH"; exit 1; }
pgrep -f sflm >/dev/null || echo "WARN: 未见 sflm 进程，若 license 报错请先启动 SFLM"
if DISPLAY=$DISPLAY xdpyinfo >/dev/null 2>&1; then XOK=1; echo "X display OK ($DISPLAY)"
else XOK=0; echo "WARN: 无 X display，退回 script-only 模式（若 deckbuild 卡住需开桌面）"; fi
NPROC=$(nproc); echo "nproc=$NPROC  MAX_PAR=$MAX_PAR  CASE_TIMEOUT=${CASE_TIMEOUT}s"

run_case() {
  local d="$1"; local name; name=$(basename "$d")
  cd "$d" || return 1
  if [ "$(cat STATUS 2>/dev/null)" = "done" ]; then echo "[skip] $name (done)"; cd "$BASE"; return 0; fi
  echo "running" > STATUS; date +%s > t_start
  rm -f typescript
  local cmd='script -q -f -c "deckbuild -ascii -run case.in" typescript'
  echo "[start] $name"
  if [ "$XOK" = 1 ]; then
    timeout "$CASE_TIMEOUT" xterm -geometry 150x40 -T "OFFLINE_$name" -e bash -lc "$cmd"
  else
    timeout "$CASE_TIMEOUT" bash -lc "$cmd"
  fi
  local rc=$?
  # 真判据：typescript 里的 simulator 退出行（exit_code 会撒谎）
  local verdict="unknown"
  if grep -aq "simulator exits with code 0" typescript 2>/dev/null; then verdict=done
  elif grep -aqE "ERROR #|simulator exits with code [1-9]" typescript 2>/dev/null; then verdict=failed
  elif [ $rc -eq 124 ]; then verdict=timeout
  elif grep -aq "Total time" typescript 2>/dev/null; then verdict=done; fi
  echo "$verdict" > STATUS; date +%s > t_end
  echo "[end]   $name -> $verdict (rc=$rc)"
  cd "$BASE"
}

# 简易并发池
PIDS=()
for d in "$BASE"/cases/*/; do
  run_case "$d" &
  PIDS+=($!)
  while [ "$(jobs -rp | wc -l)" -ge "$MAX_PAR" ]; do sleep 20; done
done
wait

echo "== all cases finished =="
grep -H . "$BASE"/cases/*/STATUS
bash "$BASE/runner/pack_results.sh"
'''

PACK_RESULTS = r'''#!/bin/bash
# pack_results.sh -- 收集所有 case 的轻量产物打成 RESULTS_<host>_<时间>.tar.gz
# 大 .str 默认不带（INCLUDE_STR=1 可带 <50MB 的）。人工把包拷回一号机 D:\SILVACO_LOCAL\inbox\
set -u
cd "$(dirname "$0")/.." || exit 9
BASE=$(pwd)
STAMP=$(date +%Y%m%dT%H%M%S)
OUT="RESULTS_$(hostname)_${STAMP}"
mkdir -p "$OUT"
for d in cases/*/; do
  name=$(basename "$d"); mkdir -p "$OUT/$name"
  cp -f "$d"/STATUS "$d"/t_start "$d"/t_end "$OUT/$name/" 2>/dev/null
  cp -f "$d"/*.log "$d"/*.csv "$d"/*.result "$OUT/$name/" 2>/dev/null
  [ -f "$d/typescript" ] && tail -300 "$d/typescript" | tr -d '\r' > "$OUT/$name/typescript_tail.txt"
  if [ "${INCLUDE_STR:-0}" = 1 ]; then
    find "$d" -name "*.str" -size -50M -exec cp -f {} "$OUT/$name/" \; 2>/dev/null
  fi
done
( cd "$OUT" && find . -type f -exec sha256sum {} \; > MANIFEST.sha256 )
tar czf "$OUT.tar.gz" "$OUT" && rm -rf "$OUT"
echo "打包完成: $BASE/$OUT.tar.gz  ->  拷回一号机 D:\\SILVACO_LOCAL\\inbox\\"
'''

README_OP = """# 二号机操作手册（人工三步，无需 Claude）

前提：二号机的 Silvaco2024 VM 能开机、桌面已登录（和一号机同一个镜像即可）。

## 第 1 步 · 把包送进 VM
把整个 `OFFLINE_SEB_BUNDLE_*.tar.gz` 拷进 VM（共享文件夹 /mnt/hgfs/... 或 U 盘均可），然后在 VM 终端：

```bash
mkdir -p /root/OFFLINE && cd /root/OFFLINE
tar xzf /mnt/hgfs/<你的共享目录>/OFFLINE_SEB_BUNDLE_*.tar.gz
cd OFFLINE_SEB_BUNDLE_*
```

## 第 2 步 · 一条命令启动（后台自治，可断点续跑）
```bash
nohup bash runner/run_all.sh > run_all.out 2>&1 &
tail -f run_all.out        # 想看进度就 tail，Ctrl-C 退出 tail 不影响运行
```
- 最多 2 个 case 并发（8 核 -P 4 的最快组合），每个 case 上限 8 小时
- 中途关机也没事：重新跑同一条命令，`STATUS=done` 的 case 自动跳过

## 第 3 步 · 拷回结果
全部跑完后目录里会出现 `RESULTS_<主机名>_<时间>.tar.gz`（只含日志/CSV/状态，很小）。
把它拷回一号机放进 **`D:\\SILVACO_LOCAL\\inbox\\`** —— 一号机的看守脚本会自动解包、统计、出图。

## case 一览
| case | 含义 |
|---|---|
| A_orig_baseline | 复现现状（LET 0.36 pC/µm, 打击 x=20, VDS 300） |
| B_let75 | 只修 LET → 0.4529（论文 75 MeV·cm²/mg） |
| C_strike_fpedge | 再修打击点 → 场板边缘 x=12.5 |
| D_vds600 / E_vds1200 | 逐级提偏压 |
| W_transfer | Wang2026 论文器件转移特性（拟合 VTH=1.2 V，独立烟测） |

阶梯目的：同一 deck 逐项隔离每个因素对 Tmax 的贡献。
所有 case 已内嵌两项实测修正（DC 段关 lat.temp；无 tstart）。

## 出问题查这里
- deckbuild 卡住不动 → VM 桌面没登录（deckbuild 需要 pty/X）；登录桌面后重跑
- license 报错 → `export SFLM_SERVERS=+localhost` 且确认 sflm 进程在
- 某 case failed → 看该 case 目录 `typescript_tail.txt` 最后几十行
"""


# --------------------------------------------------------------------------
def sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> int:
    stamp = _dt.datetime.now().strftime("%Y%m%d")
    bundle = OUTDIR / f"OFFLINE_SEB_BUNDLE_{stamp}"
    if bundle.exists():
        shutil.rmtree(bundle)
    (bundle / "cases").mkdir(parents=True)
    (bundle / "runner").mkdir()

    sets, body = load_golden(GOLDEN)

    with SPLIT.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        name = row.pop("name").strip()
        tag = name
        case_dir = bundle / "cases" / name
        case_dir.mkdir()
        overrides = {k.strip(): v.strip() for k, v in row.items()}
        deck = flatten_case(sets, body, tag, overrides)
        (case_dir / "case.in").write_text(deck, encoding="utf-8", newline="\n")
        print(f"[case] {name:<18} overrides={overrides}")

    # 转移特性 deck 原样收入（它本就是独立可跑的 $"var" 风格）
    wt = bundle / "cases" / "W_transfer"
    wt.mkdir()
    txt = TRANSFER.read_text(encoding="utf-8")
    (wt / "case.in").write_text(txt.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
    print("[case] W_transfer         (wang2026 transfer, 原样)")

    (bundle / "runner" / "run_all.sh").write_text(RUN_ALL, encoding="utf-8", newline="\n")
    (bundle / "runner" / "pack_results.sh").write_text(PACK_RESULTS, encoding="utf-8", newline="\n")
    (bundle / "README_操作手册.md").write_text(README_OP, encoding="utf-8")

    # manifest
    lines = []
    for p in sorted(bundle.rglob("*")):
        if p.is_file():
            lines.append(f"{sha256(p)}  {p.relative_to(bundle).as_posix()}")
    (bundle / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

    tgz = bundle.with_suffix(".tar.gz")
    if tgz.exists():
        tgz.unlink()
    with tarfile.open(tgz, "w:gz") as tf:
        tf.add(bundle, arcname=bundle.name)
    print(f"\n[bundle] {tgz}  ({tgz.stat().st_size/1024:.0f} KB)")
    print("[next] 拷给二号机，按包内 README_操作手册.md 三步走")
    return 0


if __name__ == "__main__":
    sys.exit(main())
