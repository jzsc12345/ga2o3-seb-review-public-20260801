# Silvaco 批量运行与监控：提交方式、参数扫描、run 目录、后台等待与门禁

本文件规定 Silvaco ATLAS 仿真的**提交方式候选项、参数扫描候选项、run 目录与 RUN_MANIFEST 约定、一次性后台等待写法、并发上限、守护门禁与失败分类**，取代 Sentaurus 时代的 SWB / swbpy2 / gsub 三件套。

## 0. 为什么这一页要给候选项

Sentaurus 侧是 **SWB(项目树) + swbpy2(Python API) + gsub(队列提交)** 三件套一一对应；Silvaco 没有等价的三件套，同一件事有多条合法路径。因此本文件**不替用户拍板**，每类操作先给候选项表，标 **[默认]**，用户可随时改选，改选后必须写进 `RUN_MANIFEST.md`。

前置条件（未满足时不要提交任何 run）：

- 远端主机 `tcad`（RHEL 7.9，8 vCPU / 8 GB RAM，`/` 剩余 ~124 GB，2026-07-26 实测）可 SSH。
  2026-07-26 实测（详见 `preflight-and-environment.md` §1.1）：**`192.168.50.134` 是活地址且 `hostname` 即 `tcad`**；
  `192.168.107.128` 连不上（`Connection reset by peer`）；别名 `silvaco` 指向的正是有效地址 `192.168.50.134`。
- **真正的陷阱是 `ens33` 走 DHCP（`valid_lft 915sec`），地址随租约漂移，任何写死的 IP（含上面两个）都可能在下次开机后失效**。runner 里**不要硬编码任一 IP**，每次会话先探测实际可达地址并核对 `hostname` == `tcad`，再写入本次 run 的环境文件。
- 远端不可达时**不提交任何 run**；参数/语法核对可降级用本地只读镜像 `D:\knowledge\{pdf25,exp25,material_sil}`（atlas_users1.pdf / 184 个官方例子 / 材料库），凡只能由远端 `atlas.key` 裁决的结论一律标 `[待 atlas.key 复核]`。
- Silvaco 可执行不在默认 PATH：必须显式加载（见 §3）。
- 许可证走 **SFLM**：`export SFLM_SERVERS=+localhost`，`sflm_monitord` 已在运行。
- 运行区固定为远端 `/root/DECKBUILD/`。

---

## 1. 提交方式候选项（替代 `gsub`）

| 候选 | 命令 / 入口 | 适用 | 可脚本化 | 可复现 | 取舍 |
|---|---|---|---|---|---|
| **[默认] `deckbuild -run -ascii`** | `deckbuild -run -ascii <deck>.in -outfile <deck>.out` | 全部批量/无人值守 run | 是 | 强（deck + 命令行即全部输入） | 无 GUI 状态树，需自建 run 目录与 manifest |
| DeckBuild GUI `simulate` | `deckbuild <deck>.in &`（需 `export DISPLAY=:0`），窗口内点 Run / 逐行 `simulate` | 交互调试、逐语句排错 | 否 | 弱（人工步骤不留痕） | 只用于调试，**产出不得当作交付 run** |
| VWF Virtual Wafer Fab | VWF 实验 + split table，由 VWF 派发 job | 大规模 DOE、需要实验数据库 | 中（需 VWF 侧配置） | 强（实验表即记录） | 本机未验证 VWF 服务/数据库是否配置，启用前需先确认 |
| 自建 shell + Python runner | `nohup bash run_atlas.sh ... &` 包裹 `deckbuild -run` | 队列化、门禁、超时 kill、退出码分类 | 是 | 强 | 需自己维护；本文件 §8 给骨架 |

选型规则：

- 默认 **`deckbuild -run -ascii`**，并且**始终**由 §8 的 runner 骨架包裹（拿到退出码 + 超时保护）。
- GUI `simulate` 只在人肉调试单条语句时用；调试结论必须回写进 `.in`，再用默认方式重跑一遍，才算数。
- 只有当一次任务的 case 数 > 20 且用户明确要求实验数据库时，才评估 VWF；启用前先在远端确认 VWF 组件与许可可用，不要假定。
- **禁止**直接裸跑 `atlas < deck.in` 绕过 DeckBuild：那样 `set` 变量、`extract`、`loop` 等 DeckBuild 层语句不会被解释，deck 行为与交付说明不一致。

命令模板（默认路径）：

```bash
deckbuild -run -ascii igbt_bv.in -outfile igbt_bv.out
```

- `-run`：非交互直接执行。
- `-ascii`：纯文本输出，便于 grep / 解析；缺了它输出可能带控制字符，后台等待会误判。
- `-outfile`：**必须显式给**，且用绝对路径或先 `cd` 进 run 目录，避免监控到上一轮的 `.out`。

版本与并行度不写在命令行，而是写在 deck 内的 `go atlas` 行（见 §3），这样 deck 自带版本信息，sha256 一变就知道跑的不是同一件事。

---

## 2. 参数扫描候选项（替代 swbpy2 实验树）

| 候选 | 机制 | 每个 case 是否独立 deck | 适用 | 取舍 |
|---|---|---|---|---|
| **[默认] deck 内 `set` + 外部脚本模板替换** | `.in` 顶部集中 `set` 变量，Python/shell 按 case 生成一份实体 deck 落到 run 目录 | 是（每 case 一份可 sha256 的 deck） | 结构/物理/偏置任意维度扫描 | 需要一个几十行的生成脚本 |
| DeckBuild `loop` / `l.end` | deck 内 `loop steps=<N>` … `assign` … `l.end` 循环体 | 否（一份 deck 跑完全部点） | 同结构下的一维密集扫描、`extract` 汇总 | 单点失败会拖垮整个 run；无法并行；无法按 case 归档 |
| VWF split table | VWF 实验矩阵派发 | 是 | 大规模 DOE | 依赖 VWF 环境，本机未验证 |

默认写法（模板 + 替换）：

```silvaco
# ---- case parameters (generated, do not hand-edit) ----
set LGATE=1.5
set VDMAX=1200
set TLATT=300
go atlas simflags="-V 5.40.0.R -P 4"
```

生成侧只做一件事：把模板里的 `set` 行按 case 覆写，其余字节不动。这样：

- 每个 case 有**独立 deck 文件 + 独立 sha256**，manifest 可验证；
- case 之间可并行（受 §7 并发上限约束）；
- 单点失败只影响该 case。

`loop`/`l.end` 的合法用法（可以用，但要知道代价）：

```silvaco
loop steps=5
assign name=VG n.value=(0,2,4,6,8)
solve vgate=$VG
l.end
```

- 只在"同一结构、同一物理、纯偏置点密集扫描且必须放在同一条曲线里"时用。
- **不要**用 `loop` 扫结构参数：结构变了就该是不同 run、不同归档。
- `assign` 的取值列表语法在不同 ATLAS 版本上可能有差异，首次使用前需在 `$SILVACO/examples` 中核对一个同类例子。

---

## 3. 环境加载与版本冻结（每个 run 必须显式做）

```bash
export SILVACO=/atctools/Synopsys/Silvaco2024
export PATH=$SILVACO/bin:$PATH
export SFLM_SERVERS=+localhost
# 不要 source $SILVACO/etc/silvaco.profile —— 已实测证伪：该文件是只打印说明文字的
# csh 空壳（315 字节纯 echo，不设 SILVACO/PATH/任何 license 变量），
# 见 preflight-and-environment.md §2.2。显式 export（上面三行）是唯一正确路径。
```

版本冻结：本机可用 `5.38.0.R` 与 `5.40.0.R`，**本项目冻结 `5.40.0.R`，并行度 `-P 4`**，写在 deck 的每一个 `go atlas` 行上：

```silvaco
go atlas simflags="-V 5.40.0.R -P 4"
```

规则：

- 一份 `.in` 里可能有多个 `go atlas`（建结构一次、电学求解一次），**每个都要带同样的 `simflags`**，否则第二段可能落到默认版本。
- 不要在命令行和 deck 里同时指定版本；只在 deck 里指定，命令行保持 §1 模板不变。
- GUI 工具（TonyPlot 等）前必须 `export DISPLAY=:0`；批量 run 本身不需要 DISPLAY，runner 里不要引入它。

---

## 4. run 目录约定（替代 node number `n<N>`）

Sentaurus 用纯数字节点号定位一次仿真；Silvaco 侧用 **run 目录名**：

```
/root/DECKBUILD/RUN_<case>_<UTCstamp>/
```

- 前缀 `RUN_` 是**强制**的，本包其余文件（`preflight-and-environment.md` / `structure-and-mesh.md` / `device-physics-and-solver.md` / `wbg-radiation-and-seb.md` / `results-and-reporting.md`）一律按 `RUN_<case>_<stamp>` 定位一次仿真；不带前缀的目录名一律视为不合规。
- `<case>`：小写、下划线、能读懂的短名，例如 `igbt_bv`、`gan_hemt_idvg`、`sic_mos_seb`。
- `<UTCstamp>`：`date -u +%Y%m%dT%H%M%SZ`，例如 `20260726T101500Z`。
- 完整例子：`/root/DECKBUILD/RUN_igbt_bv_20260726T101500Z/`
- 复述这个 run 时就用目录名，不要说"第 3 个"、"刚才那个"。

目录内容固定：

```
RUN_igbt_bv_20260726T101500Z/
├── igbt_bv.in            # 本次实际执行的 deck（结构+电学合并，见 §13）
├── igbt_bv.out           # deckbuild 运行输出（-outfile）
├── RUN_MANIFEST.md       # 必填，见 §5
├── env.sh                # 本次实际用的 PATH/SFLM/版本，可原样 source 复现
├── .exit                 # runner 写入的退出码（后台等待的唯一完成信号）
├── *.str                 # 结构/解快照
└── *.log                 # ATLAS log（I-V / 瞬态曲线）
```

- run 目录**一旦跑过就只读**。要改参数就开新 run 目录，不要就地覆盖重跑——覆盖会让 manifest 里的 sha256 与实际产物对不上。
- 远端只保留正在迭代的 run；结束后按 §13 回传归档。

---

## 5. `RUN_MANIFEST.md` 必填字段

每个 run 目录**必须**有 `RUN_MANIFEST.md`，在**提交前**写好前半段（输入），在**结束后**补完后半段（结果）。缺字段的 run 视为不可交付。

| 字段 | 内容 | 取值来源 |
|---|---|---|
| run id | 目录名 `RUN_<case>_<UTCstamp>`（`RUN_` 前缀强制，见 §4） | 目录名本身 |
| deck sha256 | `sha256sum igbt_bv.in` 的完整哈希 | 提交前算，事后必须能重算一致 |
| ATLAS 版本 | `5.40.0.R` | deck 内 `simflags` |
| 并行度 `-P N` | `-P 4` | deck 内 `simflags` |
| method 行 | 逐字抄 deck 里的 `method ...`（如 `method block newton carriers=2 climit=1e-4 itlimit=...`） | deck |
| models 行 | 逐字抄 `models ...` / `material ...` / `mobility ...` / `impact ...` / `trap ...` | deck |
| 热边界 | 是否 `models lat.temp`；`thermcontact` 的 `ext.temper` / `alpha`；`material tcon.const`；无热模型则写 `isothermal 300K` | deck |
| 偏置点 | 扫描量、起止、步长、终止条件（如 `solve vdrain=0→1200 step=5`） | deck `solve` 段 |
| 终止判据 | 本 run 认定"成功结束"的信号（见 §6）与"提前失败"的信号 | runner 常量 |
| 输出清单 | 预期产出的 `.str` / `.log` 文件名逐个列出 | deck `save outf=` / `log outf=` |
| 主机与目录 | `tcad` 的实际 IP + run 目录绝对路径 | 提交时探测 |
| 起止 UTC 时间 | 提交与结束时刻 | runner |
| 退出码 | `.exit` 内容 | runner |
| 结果分类 | ok / license / syntax / mesh / nonconverged / diverged / timeout（见 §11） | 结束后判定 |
| 归档路径 | `E:\silvaco2425\bulk\{str,log}\<run id>\` | 回传后填 |

模板：

```markdown
# RUN_MANIFEST — RUN_igbt_bv_20260726T101500Z

| 项 | 值 |
|---|---|
| run id | RUN_igbt_bv_20260726T101500Z |
| host / dir | tcad(<探测到的IP>) : /root/DECKBUILD/RUN_igbt_bv_20260726T101500Z |
| deck | igbt_bv.in |
| deck sha256 | <64-hex> |
| ATLAS 版本 | 5.40.0.R |
| 并行度 | -P 4 |
| method | method block newton carriers=2 climit=1e-4 |
| models | models ... / material ... / mobility ... / impact ... |
| 热边界 | models lat.temp + thermcontact num=1 ext.temper=300 alpha=... |
| 偏置点 | solve vdrain 0 → 1200 V, step 5 V |
| 终止判据 | 成功=exit 0 且 .out 无 ATLAS DIED；失败串见 §6 |
| 输出清单 | igbt_str.str, igbt_bv_bias.str, igbt_bv.log |
| start / end UTC | 2026-07-26T10:15:00Z / <end> |
| exit code | <n> |
| 结果分类 | <ok / ...> |
| 归档 | E:\silvaco2425\bulk\{str,log}\RUN_igbt_bv_20260726T101500Z\ |
```

---

## 6. 一次性后台等待（唯一正确写法）

### 6.1 完成信号：退出码哨兵文件，不是进程、不是 "Error"

runner 把 `deckbuild -run` 的退出码写进 `.exit`；后台等待**只**等这个文件出现。

```bash
RUN=/root/DECKBUILD/RUN_igbt_bv_20260726T101500Z
# 一次性后台等待（提交后立刻执行，只跑一轮，不做持续轮询汇报）
until [ -f "$RUN/.exit" ]; do sleep 60; done
printf 'exit=%s\n' "$(cat "$RUN/.exit")"
tail -30 "$RUN/igbt_bv.out"
```

为什么是这个写法：

- 哨兵文件由 wrapper 在 `deckbuild` 返回后写入，**既覆盖成功也覆盖失败**，不会漏掉崩溃退出；
- 不依赖任何日志措辞，跨 ATLAS 版本稳定；
- `sleep 60` 单轮阻塞，不刷屏、不抢 CPU。

### 6.2 没有哨兵文件时的退化写法（例如 job 不是自己起的）

只有在拿不到退出码时才用日志串等待，并且**必须同时匹配成功与失败终止串**：

```bash
OUT=/root/DECKBUILD/RUN_igbt_bv_20260726T101500Z/igbt_bv.out
# 注意：串集合里唯一的"成功"分支 "Total cpu time" 只是候选（[未核实]，见下表），
# 若本机实际统计行措辞不同，成功 run 将永远不命中——所以必须带最大轮数兜底，禁止无限等。
N=0; MAX=360   # 360 x 60s = 6h，对齐 wallclock 预算；超时按"未判定"人工查看
until grep -qE "ATLAS DIED|Convergence failure|solution did not converge|License|Total cpu time" "$OUT" 2>/dev/null; do
  N=$((N+1)); [ "$N" -ge "$MAX" ] && { echo "WAIT GAVE UP after $((MAX*60))s, inspect manually"; break; }
  sleep 60
done
tail -30 "$OUT"
```

ATLAS 终止串**候选项**（首次成功 run 后必须把本机实际串抄进 runner 常量，不要长期依赖猜测）：

| 情形 | 候选特征 | 备注 |
|---|---|---|
| 正常结束 | deckbuild 进程退出码 0；`.out` 末尾出现 `quit` 回显与 CPU 时间统计行 | 确切统计行措辞需在首个成功 run 的 `.out` 中核对后固化 |
| 求解器崩溃 | `ATLAS DIED` | 崩溃即无产物，直接判 fail |
| 不收敛 | `Convergence failure` / `solution did not converge` | 可能仍有部分 `.log` 数据 |
| deck 主动终止 | deck 中若使用 `fail.quit` 类终止，会提前 `quit` | 该关键字是否被 5.40.0.R 支持需在 `$SILVACO/examples` 或 manual 中核对 |
| 许可证 | 输出含 `License` / SFLM 相关报错 | 属环境错误，不要改 deck |

### 6.3 明确禁止

- **不要 `grep "Error"`**：ATLAS 每个 Newton 迭代都会打印误差相关字样，正常收敛过程就会命中，等待会立刻假阳性返回。
- **不要用 `pgrep` / `ps` 判断完成**：多个并发 ATLAS 同名进程互相混淆，且 DeckBuild 与 atlas 是父子两层进程，父退子未退或反之都会误判。（`pgrep -c` 仅可用于 §7 的并发**计数**，不可用于判完成。）
- **不要持续轮询汇报**：等待就是一次性的，等到了再看 `tail -30`。
- **不要 `cat` 整个 `.out`**：只读 `tail -30` / `tail -50`，需要定位再针对性 grep 具体串。
- **不要用相对路径等待**：工作目录一变就会盯上别的 run 的 `.out`。

---

## 7. 并发上限

硬约束来自远端实测配置：**8 vCPU / 8 GB RAM**，本项目冻结 `-P 4`。

| 项 | 值 | 依据 |
|---|---|---|
| 单 ATLAS 线程数 | 4 | deck `simflags="-P 4"` |
| **同时运行的 ATLAS 上限** | **2** | 8 vCPU ÷ 4 线程 = 2；超了只会互相抢核变慢，不会更快 |
| 内存约束 | 同样封顶 2 | 8 GB 总内存，2D 精细网格单 job 可达 1–3 GB；3D / Victory Device 需降到 1 |
| 提交前检查 | `pgrep -xc atlas`（按进程名精确计数，仅计数） | ≥2 就排队等，不要硬提交。⚠ 不要用 `-fc`：`-f` 匹配完整命令行，`bash run_atlas.sh ...` 或含 "atlas" 的 case 名会被自计入，闸门恒多计 1 |

```bash
# 提交前的并发闸门：数够了就不提交
# -x 按进程名(comm)精确匹配 atlas 二进制；-f 会连自身脚本命令行里的 "atlas" 一起计入（自匹配）
RUNNING=$(pgrep -xc atlas || true)
if [ "${RUNNING:-0}" -ge 2 ]; then
  echo "busy: $RUNNING atlas running, hold submission"
  exit 3
fi
```

其它规则：

- 大扫描先用 1–2 个探索性 case 验证流程（粗网格、窄扫描），跑通再铺开。
- 共享目录 `/mnt/hgfs/{share_wm,share24,16sil_share}` 已 98% 满，**任何 run 都不要把 `.str` / `.log` 写进去**，会直接写满导致全部 job 失败。

---

## 8. runner 骨架

放在远端 run 目录同级，或由本地 Python 生成后 `scp` 上去。这是 §1 默认提交方式的**唯一**执行入口。

```bash
#!/usr/bin/env bash
# run_atlas.sh <deck.in> <case> [wallclock]
set -uo pipefail

DECK="$1"; CASE="$2"; WALL="${3:-6h}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN="/root/DECKBUILD/RUN_${CASE}_${STAMP}"   # RUN_ 前缀强制，见 §4

# --- 1) 环境（写成文件，manifest 可复现） ---
mkdir -p "$RUN"
cat > "$RUN/env.sh" <<'EOF'
export SILVACO=/atctools/Synopsys/Silvaco2024
export PATH=$SILVACO/bin:$PATH
export SFLM_SERVERS=+localhost
EOF
. "$RUN/env.sh"

# --- 2) 并发闸门 ---
# -x 精确匹配进程名 atlas；本脚本命令行含 "atlas"（run_atlas.sh），用 -f 会自匹配、恒多计 1
RUNNING=$(pgrep -xc atlas || true)
if [ "${RUNNING:-0}" -ge 2 ]; then
  echo "HOLD: ${RUNNING} atlas already running (cap=2)"; exit 3
fi

# --- 3) 落 deck + 指纹 ---
cp "$DECK" "$RUN/$(basename "$DECK")"
DECKFILE="$RUN/$(basename "$DECK")"
sha256sum "$DECKFILE" | awk '{print $1}' > "$RUN/.deck.sha256"

# --- 4) 后台执行：超时保护 + 退出码哨兵 ---
cd "$RUN" || exit 1
nohup bash -c "
  timeout -k 60 ${WALL} deckbuild -run -ascii '$(basename "$DECKFILE")' -outfile '${CASE}.out'
  echo \$? > '$RUN/.exit'
" >/dev/null 2>&1 &

echo "SUBMITTED $RUN"
echo "WAIT: until [ -f $RUN/.exit ]; do sleep 60; done"
```

要点：

- `timeout -k 60 <wall>`：先 TERM，60 s 后 KILL，防止发散 run 占满机器；超时会以退出码 124 体现。
- `echo $? > .exit` **必须**在 `timeout` 之后无条件执行（不要 `&&`），否则失败时哨兵不落地，后台等待会永久卡住。
- runner 只负责"起 + 保护 + 落退出码"，不做结果判断；判断在 §9/§10/§11。
- `deckbuild` 的退出码是否忠实传递 ATLAS 内部失败，需在首个人为构造的失败 case 上核对一次；核对结果写进 manifest 的"终止判据"。在未核对前，退出码与 §6.2 的日志串**同时**检查。

配套的一次性等待 + 收尾：

```bash
RUN=<runner 打印的路径>
until [ -f "$RUN/.exit" ]; do sleep 60; done
EXIT=$(cat "$RUN/.exit")
echo "exit=$EXIT"
tail -30 "$RUN"/*.out
ls -lh "$RUN"/*.str "$RUN"/*.log 2>/dev/null
```

---

## 9. 守护与门禁

门禁不是"多做点检查"，是**在烧掉几小时机时之前把明显错误的 run 拦下来**。四道闸门：

| 闸门 | 触发条件 | 动作 |
|---|---|---|
| 场强上限 | 峰值电场超过材料临界场很多倍且 deck 未开 `impact`（碰撞电离） | 判为结构/边界错误而非物理结果；停止扫描，回查电极与掺杂 |
| 暗电流 / 漏电上限 | 关态电流超出该器件类别合理量级（例如比预期高 6 个数量级） | 优先怀疑寄生导电路径、接触定义、网格穿孔；不要靠调 `method` 掩盖 |
| 超时 | 超过 wallclock 预算（探索 30m–1h，定稿 4–6h） | `timeout -k 60` 自动 kill，退出码 124，记为 timeout |
| 退出码 | 见 §10 | 按类分流，不进入物理分析 |

数值取值必须**逐器件设定并写进 manifest**，本文件不给通用阈值（不同材料体系差几个数量级）。参考起点：临界场按材料手册值（Si / SiC / GaN 差一个数量级以上），关态电流按用户给的器件规格书或目标指标。

提取用于门禁的标量，两种候选：

| 候选 | 做法 | 取舍 |
|---|---|---|
| **[默认] deck 内 `extract` + 解析 `.out`** | 在 deck 末尾写 `extract` 语句，结果回显到 `.out`，门禁脚本 grep `.out` 取值 | 纯文本、零依赖；`extract` 具体表达式语法（如 `xintercept(maxslope(curve(...)))`、`datafile=`）需在 `$SILVACO/examples` 中核对同类例子后再写 |
| 外部 Python 解析 `.log` | 用 Python 读 ATLAS `.log` 曲线数据算指标 | 更灵活，但要先确认本版本 `.log` 的实际格式（表头/分隔），核对前不要假定列序 |
| TonyPlot 目视 | GUI 打开 `.str` / `.log` | 只用于人工确认，不能作为自动门禁 |

场点探针（峰值电场）如需自动取值，可评估 ATLAS `probe` 语句；其参数名需在 manual / examples 中核对后再写进 deck，不要凭印象拼参数。

---

## 10. 退出码分类

| 退出码 | 含义 | 处置 |
|---|---|---|
| 0 | deckbuild 正常返回 | 仍需 §6.2 串检查确认 ATLAS 未静默失败，再判 ok |
| 1 / 2 | deck 语法或工具级错误 | 看 `.out` 首个报错行；属 syntax 类 |
| 3 | runner 并发闸门拒绝（自定义） | 未提交，排队后重来 |
| 124 | `timeout` 触发（TERM） | timeout 类；先查是否发散，再考虑放宽 wallclock |
| 137 | SIGKILL（`timeout -k` 或 OOM killer） | 内存不足或 kill 硬超时；降网格 / 降并发到 1 |
| 其它非 0 | 未分类 | 抄原始退出码进 manifest，不要猜 |

---

## 11. 失败分类表

拿到 `.exit` 与 `tail -30 *.out` 后，**先分类再动手**。分错类会把环境问题当物理问题修，浪费整轮迭代。

| 类别 | 典型信号（候选，首次遇到后固化本机实际串） | 归属 | 正确动作 | 禁止动作 |
|---|---|---|---|---|
| license | `.out` 含 `License` / SFLM 报错；或 run 秒退 | 环境 | 查 `SFLM_SERVERS=+localhost`、`sflm_monitord` 是否在跑、`sflm` CLI 查状态 | 改 deck、改 `method`、换版本"绕过" |
| 语法 | `.out` 在某一行处报未知语句/未知参数，无 `.log` 产出 | deck | 定位该行，对照 `$SILVACO/examples` 同类例子改写 | 逐参数试错乱猜 |
| 网格 | 建结构阶段失败；节点数异常大/小；`mesh infile=*.str` 读入失败 | 结构 | 回 `x.mesh/y.mesh/region/electrode` 检查坐标闭合与区域覆盖；`.str` 缺失就是结构没存成 | 直接加密全局网格（节点爆炸） |
| 不收敛 | `Convergence failure` / `solution did not converge`；停在某个偏置点 | 数值 | 换 `method block newton carriers=2`；减小偏置步长；检查该点物理是否已进入雪崩/自热 | 无依据地反复调 `climit`/`itlimit` |
| 发散 | 电流/温度单调爆到非物理量级；或 `ATLAS DIED` | 物理/数值 | 查 `impact`、`lat.temp`+`thermcontact` 是否缺 `alpha` 导致热失控；查接触定义 | 把发散当"击穿结果"上报 |
| 超时 | 退出码 124 / 137 | 资源 | 先判断是不是发散导致步长塌缩；不是才放宽 wallclock 或粗化网格 | 无脑加 wallclock 重跑 |

**两次失败规则**：同类失败最多试两次。第二次仍失败就停止盲试，回到 `$SILVACO/examples`、manual 或文献查根因，把结论写进 `findings.md` 再动 deck。

---

## 12. 队列追踪脚本（仅辅助记录；**该脚本目前不存在，需先创建**）

> ⚠ 移植残留更正：`scripts/sim_queue.py` 与状态目录 `claude_tmp/silvaco/` 在本仓库**都不存在**
> [已核实: `D:\SILVACO_LOCAL\scripts\` 实有 silvaco_remote.py / victorydoe_ctl.py / let_calc.py 等 9 个脚本，
> 无 sim_queue.py；`D:\SILVACO_LOCAL\claude_tmp\` 目录不存在——`claude_tmp/` 是源包 Claude 时代的路径约定]。
> 队列追踪不是必需环节：`RUN_MANIFEST.md` 才是可复现凭证。若确需队列脚本，**先创建再用**，
> 状态文件路径在创建时显式约定（不要沿用 `claude_tmp/`）。以下接口仅作创建时的设计参考：

```bash
python3 scripts/sim_queue.py add  <run_id> <run_dir> "description"
python3 scripts/sim_queue.py done <run_id> "result"
python3 scripts/sim_queue.py fail <run_id> "reason"
python3 scripts/sim_queue.py status
```

规则：

- 它**只记录**提交/完成/失败三态；状态文件路径在创建脚本时显式约定并写进脚本头注释（不要用不存在的 `claude_tmp/silvaco/`）。
- 它**不替代** `RUN_MANIFEST.md`（manifest 才是可复现凭证），也**不替代** `deckbuild -run` 与 `.exit` 哨兵。
- 用法节奏：runner 打印 `SUBMITTED` 后立即 `add`；后台等待返回、退出码为 0 且串检查通过后 `done`；命中 §11 任一失败类后 `fail`，reason 写**分类名 + 一行证据**（例如 `nonconverged: stops at vdrain=980V, "solution did not converge"`）。
- 队列脚本里的 run_id 必须与 run 目录名逐字一致，不要另起简称。

---

## 13. 文件落位与归档（强制）

- **主控端 `D:\SILVACO_LOCAL` 只放**：`.py` 脚本 / `.md` 技术文档 / 轻量 `.csv` / `.png` 截图与图 / `.in` deck。
- **`.in` deck 必须把建模（结构）与特性仿真（电学）合并为同一个文件**：

```silvaco
go atlas simflags="-V 5.40.0.R -P 4"
# 结构：mesh / x.mesh / y.mesh / region / electrode / doping
save outf="igbt_str.str"

go atlas simflags="-V 5.40.0.R -P 4"
mesh infile="igbt_str.str"
# 电学：models / material / mobility / impact / contact / thermcontact / method / solve
log outf="igbt_bv.log"
solve ...
save outf="igbt_bv_bias.str"
```

- 读回结构模板统一写规范全名 `mesh infile=`。官方例子两种写法都有 [已核实: 本地 `d:\knowledge\exp25` 中 `MESH infile=` 为多数（Fin_GAA_ex01.in:114 等），`MESH inf=` 亦见于 Bip_Dio_ex01.in:47、Solar_ex05.in:73、TFT_ex19.in:119 等]——`inf=` 是 `infile=` 的前缀缩写，读别人 deck 时认得即可，本包模板不用缩写（grep 核对参数一律按规范全名，理由见 `preflight-and-environment.md` §6.1）。
- **一切大体积 `.str` / `.log` 归档到 Windows `E:\silvaco2425\bulk\{str,log}\<run id>\`**；运行期间产物留在 `/root/DECKBUILD/<run>`，结束后回传：

```bash
# 从 Windows 侧拉回（IP 用实际探测值，不要写死）
scp -i C:/Users/Administrator/.ssh/silvaco_ed25519 \
    root@<probed-ip>:/root/DECKBUILD/RUN_igbt_bv_20260726T101500Z/'*.str' \
    E:/silvaco2425/bulk/str/RUN_igbt_bv_20260726T101500Z/
```

- 远端 `/root/DECKBUILD` 是唯一正在迭代的运行区；**不要**把整套远端工程复制回 Windows。
- 归档完成后把归档路径回填进 `RUN_MANIFEST.md`，该 run 才算收尾。

---

## 14. 反模式速查（命中任意一条即视为无效交付）

1. 裸跑 `atlas < deck.in`，绕过 DeckBuild。
2. 用 GUI `simulate` 出的结果当交付，deck 未回写、未重跑。
3. run 目录就地覆盖重跑，manifest sha256 与产物对不上。
4. `RUN_MANIFEST.md` 缺字段（尤其 deck sha256 / method 行 / 热边界 / 终止判据）。
5. 后台等待用 `grep "Error"` 或 `pgrep` 判完成。
6. 持续轮询刷屏，或 `cat` 整个 `.out`。
7. 同时跑 ≥3 个 ATLAS（`-P 4` 下超出 8 vCPU）。
8. 把 `.str` / `.log` 写进 `/mnt/hgfs/*`（已 98% 满）。
9. 把 license 失败当成收敛问题去调 `method`。
10. 在 runner 或 deck 里硬编码 `192.168.50.134` / `192.168.107.128`（必须运行时探测）。
11. 编造未核对的 ATLAS 参数名；不确定就写成候选项并注明"需在 `$SILVACO/examples` 或 manual 中核对"。
