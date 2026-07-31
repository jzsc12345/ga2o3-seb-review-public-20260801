# 结果可视化、拟合报告与经验沉淀 (Silvaco ATLAS)

> 本文件规定 Silvaco TCAD 仿真跑完之后怎么看、怎么出图、怎么写报告、怎么把经验沉淀下来。
> 核心是四层诊断顺序 `.out → .log → .str → 文献/examples`,以及"出图必须带 provenance、拟合必须带误差表"。

---

## 0. 完成仿真后的必做项 (逐条打勾,不允许跳)

1. 读 `tail -40 <run>.out` 判断 ATLAS 的**终止状态**(见 §2 终止串候选项表)。
2. 解析 `.log` 看曲线,提取关键指标 (Vth / Ion / Ioff / Ron / BV / 峰值电流 / 峰值温度 …)。
3. 打开 `.str` 看空间分布,定位电场、电流路径、载流子、碰撞电离、晶格温度。
4. 导出至少一个**持久化结果**:`.png` 图 + `.md` 表格/报告 (二者都要,不是二选一)。
5. 为每张 2D 空间图写 **provenance manifest** 行 (见 §9)。
6. 更新三件套 `progress.md` / `findings.md` / `RUN_MANIFEST.md` (见 §10)。
7. 把大体积 `.str` / `.log` 从远端回传归档到 `E:\silvaco2425\bulk\{str,log}\<run id>\` (按 run 建子目录,层级与 batch-run-and-monitor.md §5 一致;见 §11)。
8. 若交付物是给人读的报告/论文/专利说明,最后再做一次自然化润色;代码、deck、manifest 不润色。

**禁止**:只看 `.out` 就下物理结论;只看 `.log` 曲线就断言机理;没有 `.str` 就声称"已定位高场区/热点"。

---

## 1. 分层诊断顺序 (固定,不可打乱)

| 层 | 文件 | 位置 | 目的 | 不能回答的问题 |
|---|---|---|---|---|
| 1 | `<run>.out` | `deckbuild -run -ascii ... -outfile <run>.out` 的 stdout 落盘 | 跑完没有 / 死在哪一条语句 / 收敛与 license 报错 / 每个 bias 点的迭代数 | 任何物理问题 |
| 2 | `<run>.log` | `log outf="<run>.log"` | I-V、瞬态等**宏观曲线**;提取 Vth/Ion/Ioff/Ron/BV/峰值 | 现象发生在器件的**哪里** |
| 3 | `<run>_*.str` | `save outf="<run>_<tag>.str"` | 电流路径、高场区、载流子分布、碰撞电离、晶格温度的**空间**定位 | 这个数值对不对、和文献差多少 |
| 4 | 文献 / examples / manual | — | 解释根因、给出下一轮修正、判定是否已达标 | — |

第 4 层三个权威源在本机的**实际路径** (已核实,勿再写 `$SILVACO/doc/`):

| 用途 | 实际路径 | 说明 |
|---|---|---|
| 关键字是否存在 / 默认值 | `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key` | 唯一的存在性权威。行格式 `名字 类型(NUM/LOG/CHAR) 内部索引 默认值`;**查不到 = 该参数在 ATLAS 5.40.0.R 里不存在** |
| 语义 / 单位 / 公式 | `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/docs/atlas_users1.pdf` | 本机有 `pdftotext`,可 `pdftotext -layout ... out.txt` 后 grep |
| 真实用法 | `/atctools/Synopsys/Silvaco2024/examples/deckbuild/5.2.40.R/` | 另有 `5.2.29.R`。**引用 example 前必须先 `grep -iE '^ *go ' <deck>.in` 查清它是 `go atlas` 还是 `GO victorydevice`** —— 两者语法不通用,本技能包历史上多个错误参数就是从 Victory Device deck 抄来的 |

> `$SILVACO/doc/` 里**只有安装/SFLM 手册** (`installation_guide.pdf`、`2014sflm_users1.pdf` …),**没有 ATLAS manual**。历史文档里指向 `$SILVACO/doc/` 查 ATLAS 用法的说法一律作废。

层与层之间的关系:`.out` 说"跑成没跑成",`.log` 说"发生了什么",`.str` 说"在哪里发生的",第 4 层说"为什么、对不对、下一步"。
**跳层写结论 = 报告作废。**

---

## 2. 第 1 层:`.out` (DeckBuild stdout) 判读

运行与落盘的默认写法:

```bash
export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
export SFLM_SERVERS=+localhost
cd /root/DECKBUILD/RUN_<case>_<UTCstamp>
deckbuild -run -ascii <case>.in -outfile <case>.out
echo "deckbuild exit=$?"
```

### 2.1 终止串候选项 (grep 这些,不要 grep `Error`)

| 判定 | 候选终止特征 | 说明 |
|---|---|---|
| **[默认] 正常结束** | deck 末尾 `quit` 执行完毕 + `deckbuild` 进程退出码 `0` | 退出码是最可靠的单一信号 |
| 崩溃 | `ATLAS DIED` | ATLAS 内部致命错误,通常伴随上一条语句名 |
| 不收敛 | `Convergence failure` / `solution did not converge` / 迭代数持续撞 `itlimit` | 常见于大偏压步、雪崩打开、自热耦合 |
| 主动中止 | deck 里 `fail.quit` 被触发 | 这是**设计内**的中止,不是 bug |
| 许可证 | 含 `License` / `SFLM` 的报错行 | 先查 `sflm_monitord` 与 `SFLM_SERVERS=+localhost`,不要当成物理问题去改模型 |

> 上表是候选集合。**首次在本机跑通一个 deck 后,把实际出现的终止串抄进 `RUN_MANIFEST.md` 固化下来**,后续 runner 用固化后的串。

### 2.2 一次性后台等待 (不要轮询 `pgrep`)

```bash
# 只在提交后设置一次;覆盖成功与失败两种终止
until grep -qE "ATLAS DIED|Convergence failure|solution did not converge|License" <case>.out 2>/dev/null \
      || ! kill -0 "$ATLAS_PID" 2>/dev/null; do
  sleep 60
done
tail -40 <case>.out
```

要点:
- 不要 `grep "Error"` — ATLAS 正常输出里就有含 error 的收敛信息 (如 residual error),会误触发。
- 不要用 `pgrep atlas` 判完成 — 并行多 run 时进程名无法区分。
- 人工看进度只 `tail -40`,不要读整个 `.out`。

### 2.3 `.out` 里值得抄进报告的东西

- 实际生效的版本行 (确认 `simflags="-V 5.40.0.R"` 生效、`-P 4` 并行度生效)。
- 网格统计:节点数 / 三角形数 (节点爆炸的第一现场)。
- 每个偏压点的 Newton 迭代数与残差趋势 (迭代数单调上升 = 该点附近要减步长)。
- 第一次出现警告的语句名 (warning 的位置比 warning 本身更有信息量)。

#### 迭代数上升时到底该改什么 (纠正:`method block newton carriers=2` 不是解药)

`block` / `newton` / `carriers` 三个关键字都存在于 METHOD 卡,但**它们写出来的就是默认值**,对等温漂移扩散 deck 属于空操作:

```
$ grep -n -E '^(method|models) +[0-9]+' atlas.key
643:method          12
962:models          13
$ grep -n -iE '^ *(block|newton|carriers|itlimit|climit) ' atlas.key
644:   itlimit      NUM     1       25
688:   climit       NUM     51      10000
729:   carriers     NUM     87       2
830:   block        LOG     30       t
831:   newton       LOG     31       t
```

- `carriers` 默认就是 **2**,`newton` 默认 **t**,`block` 默认 **t** (三行都在 METHOD 卡 643–961 内)。
- manual 22.36 `BLOCK`:*"The Block method only has meaning when either lattice heating or energy balance is included in the simulation. For isothermal drift diffusion simulations, BLOCK is equivalent to NEWTON."*
- manual 22.36 `GUMMEL`:*"The order that the solution methods will be applied is GUMMEL then BLOCK then NEWTON. If no solution methods are specified NEWTON is applied by default."*

所以:**只有开了 `models lat.temp` 或能量平衡时,`block` 才有独立含义**;等温 BV/IdVg deck 写 `method block newton carriers=2` 不会改变任何行为,把它当成"换了求解器"是自欺。迭代数上升时真正该做的,按代价从低到高:

| 手段 | 写法 | 适用 | 证据 |
|---|---|---|---|
| **[默认] 减小偏压/时间步长** | `solve ... vstep=` 减半 / `method dt.min=` | 所有情况,永远先试这个 | — |
| 加 Gummel 预热阶段 | `method gummel newton` | 初始猜测差、刚打开新模型 | manual 22.36 GUMMEL:三种方法依次施加直到收敛 |
| 放宽迭代上限 | `method itlimit=100` | 迭代数逼近 25 但残差仍在下降 | [已核实: atlas.key:644 `itlimit NUM 1 25`] |
| 降低待分辨浓度 | `method climit=1e-4` | **击穿/低漏电仿真** | 见下方 climit 说明 |
| 换线性求解器 | `method bicgst` / `pam.bicgst` / `pam.gmres` | 大规模/3D,直接解器吃内存 | manual p.1146:*"the default method for 2D simulations is a direct solver … By default, ILUCGS is applied to 3D simulations"* |

**关于 `climit` (重要纠正,本包历史表述有误):**

```
$ grep -n -i 'climit' atlas.key
688:   climit       NUM     51      10000
```

- `climit` **不是残差/收敛容差**,不要说"越小越严格"。manual p.86:*"CLIMIT or CLIM.DD specify minimal values of concentrations to be resolved by the solver"* —— 它是**求解器需要分辨的最低载流子浓度归一化因子**。
- `climit` **无量纲**;带 cm⁻³ 量纲的同义参数是 `clim.dd`,且 manual p.1426 明确登记 `CLIMIT.DD`:*"This is an alias for CLIM.DD"*——两个拼写在手册层面都合法,atlas.key 的实际登记名与行号 [待 atlas.key 复核]。二者关系 `CLIM.DD = CLIMIT·(Nc·Nv)^(1/4)`(**四次方根**,manual p.86 Eq 2-3 = p.1122 Eq 20-2/20-3;旧版误转写为 `CLIMIT·√(Nc·Nv)`,平方根会差 10 个量级)。数值自检:默认 `climit=1e4` × (2.8e19×1.04e19)^(1/4) ≈ 4.1e13,与 manual p.1122 给出的 Si 默认 `clim.dd ≈ 4.5e13 cm⁻³` 吻合。
- **调小是击穿仿真的官方推荐做法,不是收敛隐患**:manual p.86 *"A value of CLIMIT=1e-4 is recommended for all simulations of breakdown, where the pre-breakdown current is small"*,并在 p.94 直接给出 `METHOD CLIMIT=1e-4`;manual p.1122 警告不调小会得到 *"false" solution*。远端 examples 全量树里 `climit=1e-4` 统计为 85 次 [待远端复核];本地 `d:\knowledge\exp25\` 子集实测 79 次(另有 `climit=1.0e-4` 写法 11 次),仍是最常见取值。
- 结论:BV / 漏电 deck 里看到 `climit=1e-4` **不要"修正"回默认值**;要用 cm⁻³ 直观表达就改写 `clim.dd`(manual p.1122:Si 二极管击穿建议 `CLIM.DD ~1e8 cm⁻³`;另见 p.804 官方例句 `METHOD CLIM.DD=1.E8 DVMAX=1.E6`)。

---

## 3. 第 2 层:ATLAS `.log` 格式与解析

### 3.1 格式事实

- ATLAS `.log` 是 **ASCII 文本 + 表头**,不是二进制;可以直接 `head -30` 肉眼看。
- 前若干行是元信息/注释 (版本、日期、注释行),随后是**一行列名**,再往下全是等宽或空白分隔的数值行。
- 列名是"量(电极)"形式,典型如 `v(drain)`、`i(drain)`、`v(gate)`、`i(gate)`、`v(source)`、`i(source)`;瞬态 deck 会多出时间列 (`time` / `t`);自热 deck 会多出温度列。
- 一次 `log outf=` 到 `log off` 之间的所有 `solve` 点会追加进同一个 `.log`;**换扫描类型必须换 log 文件**,否则 IdVg 和 IdVd 会混进同一张表。

> **[未核实:列名拼写]** 列名的确切拼写 (例如温度列到底叫 `temp`、`lat.temp` 还是别的) 随 deck 里 `models`/`probe` 设置而变,而 `.log` 表头是 ATLAS 运行期生成的,**atlas.key 查不到**——它只登记语句参数,不登记输出列名。因此这一条只能靠**跑一次真 deck 后 `head -30 <run>.log` 实测**,并把实测列名固化到 `RUN_MANIFEST.md`。下面的解析器不依赖具体列名,自动探测表头,因此拼写不确定不影响使用。
>
> 已核实的是**开关侧**而非列名侧:`models lat.temp` 存在 [已核实: atlas.key:1019 `lat.temp LOG 43 f`,在 models 卡 962–1947 内],`probe lat.temp` 也存在 [已核实: atlas.key:8164,在 probe 卡 8119–8404 内]。二者默认均为 `f`,不写就没有温度输出。

### 3.2 可直接用的 Python 解析骨架

放在 `D:\SILVACO_LOCAL\` 下 (主控端只放 `.py` / `.md` / 轻量 `.csv` / `.png` / `.in`)。

```python
"""atlas_log.py — 解析 Silvaco ATLAS .log 曲线文件为 pandas DataFrame / CSV。
表头自动探测:最后一个"非纯数值行"即列名行,其后为数据区。"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd

_NUM = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eEdD][+-]?\d+)?$")


def _is_numeric_row(line: str) -> bool:
    toks = line.replace(",", " ").split()
    return bool(toks) and all(_NUM.match(t) for t in toks)


def _clean(name: str) -> str:
    """v(drain) -> v_drain ; I(Drain) -> i_drain ; 保证列名可用作属性。"""
    s = name.strip().lower()
    s = s.replace("(", "_").replace(")", "").replace(".", "_")
    s = re.sub(r"[^0-9a-z_]+", "_", s).strip("_")
    return s or "col"


def read_atlas_log(path: str | Path, csv_out: str | Path | None = None) -> pd.DataFrame:
    path = Path(path)
    raw = path.read_text(errors="replace").splitlines()

    # 1) 找到第一条数据行
    first_data = next((i for i, l in enumerate(raw) if _is_numeric_row(l)), None)
    if first_data is None:
        raise ValueError(f"{path}: 没有找到数值数据区(仿真可能在第一个 solve 前就死了,先看 .out)")

    # 2) 表头 = 数据区之前最后一条非空、非注释行
    header = None
    for l in reversed(raw[:first_data]):
        s = l.strip()
        if s and not s.startswith(("#", "*")):
            header = s
            break

    rows = [l.replace(",", " ").split() for l in raw[first_data:] if _is_numeric_row(l)]
    ncol = max(len(r) for r in rows)

    if header:
        cols = [_clean(c) for c in header.replace(",", " ").split()]
    else:
        cols = []
    if len(cols) != ncol:                      # 表头缺失/错位时退化为位置列名
        cols = [f"c{i}" for i in range(ncol)]

    seen: dict[str, int] = {}
    uniq = []
    for c in cols:                             # 列名去重:v_drain, v_drain_1, ...
        n = seen.get(c, 0)
        seen[c] = n + 1
        uniq.append(c if n == 0 else f"{c}_{n}")

    df = pd.DataFrame(
        [[float(v.replace("D", "E").replace("d", "e")) for v in r] + [float("nan")] * (ncol - len(r))
         for r in rows],
        columns=uniq,
    )
    df.attrs["source_log"] = str(path)
    df.attrs["source_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    df.attrs["header_line"] = header or "(auto-generated)"

    if csv_out:
        df.to_csv(csv_out, index=False)
    return df


def pick(df: pd.DataFrame, *candidates: str) -> str:
    """在自动清洗后的列名里挑第一个存在的候选列名,挑不到就报出全部列名。"""
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"候选列 {candidates} 都不存在;实际列名: {list(df.columns)}")


if __name__ == "__main__":
    import sys
    d = read_atlas_log(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(d.attrs["header_line"])
    print(d.head())
    print(d.describe().T)
```

用法:

```bash
python atlas_log.py E:/silvaco2425/bulk/log/RUN_pgan_idvg_20260726T031200Z/pgan_idvg.log idvg.csv
```

### 3.3 从 DataFrame 提指标

```python
import numpy as np

def vth_constant_current(df, vg="v_gate", id_="i_drain", i_crit=1e-6, w_um=None):
    """恒流法 Vth。w_um 给定时按 mA/mm 归一化后再判据;返回线性插值的 Vg。"""
    v = df[vg].to_numpy()
    i = np.abs(df[id_].to_numpy())
    if w_um:
        i = i / (w_um * 1e-3)        # A -> A/mm  (确认 deck 的 width 设定后再用)
    k = np.argmax(i >= i_crit)
    if k == 0 or i[k] < i_crit:
        return float("nan")          # 整条曲线都没过判据,不要硬外推
    return float(np.interp(i_crit, [i[k - 1], i[k]], [v[k - 1], v[k]]))

def ron_linear(df, vd="v_drain", id_="i_drain", vd_max=0.1):
    m = df[vd].abs() <= vd_max
    s = np.polyfit(df.loc[m, vd], df.loc[m, id_], 1)[0]
    return 1.0 / s                    # Ohm (未归一化)

def bv_at_current(df, vd="v_drain", id_="i_drain", i_crit=1e-3):
    i = df[id_].abs().to_numpy(); v = df[vd].abs().to_numpy()
    k = np.argmax(i >= i_crit)
    return float(np.interp(i_crit, [i[k - 1], i[k]], [v[k - 1], v[k]])) if k else float("nan")
```

**判据必须写进报告**:同一条 IdVg,`i_crit=1e-6 A/mm` 和 `1e-7 A/mm` 给出的 Vth 能差几百 mV。没写判据的 Vth 视为无效数字。

### 3.4 各仿真类型该看哪条曲线

| 仿真 | 横轴 / 纵轴 (清洗后列名候选) | 关键指标 |
|---|---|---|
| IdVg | `v_gate` / `i_drain` | Vth (恒流法)、Ion、Ioff、SS、gm=d(Id)/d(Vg) |
| IdVd | `v_drain` / `i_drain` (按 `v_gate` 分组) | Ron、饱和电流、膝点、输出电导 |
| BV | `v_drain` / `i_drain` (log 纵轴) | BV @ 电流判据、漏电基线、击穿起始斜率 |
| 栅漏电 | `v_gate` / `i_gate` | 栅极泄漏、pGaN 栅正向导通拐点 |
| SEU / 单粒子瞬态 | `time` / `i_drain`,同轴叠 `i_source` | 峰值电流、收集电荷 ∫I dt、恢复时间、是否不恢复(SEB) |
| 自热 / 热瞬态 | `time` / 温度列 + `i_drain` | 峰值晶格温度、热时间常数、是否热失控 |
| 退化前后对比 | 两条 IdVg 叠加 | ΔVth、gm 退化率 |

---

## 4. 第 3 层:`.str` 空间诊断顺序

`.str` 是 ATLAS 的结构 + 解快照。要能画什么,取决于 deck 里 `output` 开了什么、`save outf=` 在哪个偏压点存的。

```silvaco
output con.band val.band e.field j.electron j.hole j.total charge impact recomb flowlines
solve vdrain=100
save outf="RUN_pgan_bv_vd100.str"
```

上面这一行 `output` 的 10 个字段**逐个核实通过**,全部落在 OUTPUT 卡内 (`output 42` 在 atlas.key:7337,下一张卡 `defects 43` 在 7507,故 7337–7506 为 OUTPUT 卡):

```
$ grep -n -iE '^ *(con\.band|val\.band|e\.field|j\.electron|j\.hole|j\.total|charge|impact|recomb|flowlines) ' atlas.key
7339:   e.field      LOG    2         t
7345:   impact       LOG    7         t
7350:   recomb       LOG    12        t
7351:   j.electron   LOG    13        t
7354:   j.hole       LOG    16        t
7357:   j.total      LOG    19        t
7369:   flowlines    LOG    30        f
7370:   charge       LOG    31        f
7375:   val.band     LOG    36        f
7376:   con.band     LOG    37        f
```

要点:
- **只有 `flowlines` / `charge` / `val.band` / `con.band` 默认关闭 (`f`)**,其余 6 个默认就是 `t`——写出来是自我文档化,不是"打开了新东西"。
- 自热 run 另需 `l.temper` [已核实: atlas.key:7383 `l.temper LOG 44 t`],默认已开,但**前提是 deck 里有 `models lat.temp`**,否则没有温度解可存。
- 常见易错:`ex.velo` / `ey.velo` **不是**正确拼写,正规名是 `ex.velocity` / `ey.velocity` [已核实: atlas.key:7371/7372];且它们是**电子**速度分量,空穴对应 `hx.velocity` / `hy.velocity` (7373/7374)。
- `impact` 在 OUTPUT 卡上是"存碰撞电离率场"的开关,与 `impact` **语句**(atlas.key:5367 起的独立卡) 同名不同物,不要混。

> 新字段名一律**先 grep atlas.key 再写进 deck**,不要凭印象加参数。核对命令模板见 §1 第 4 层路径表。

### 4.1 固定看图顺序

1. **Net Doping / 结构与区域** — 先确认建的结构是你想要的 (层厚、电极位置、region 编号)。几何错了,后面全白看。
2. **Mesh** — 高场区/沟道/界面是否加密,是否有畸形三角形。
3. **Potential** — 势分布是否单调合理,有没有悬空区。
4. **Electric Field (含 vector)** — 峰值电场在哪,是否落在预期的场板/栅角/结边缘。
5. **Electron Conc / Hole Conc** — 沟道 2DEG/2DHG、耗尽区、注入区。
6. **Total Current Density (含 vector / flowlines)** — 电流路径是否走沟道,有没有走 buffer 漏电通路。
7. **Impact Generation Rate** — 击穿/雪崩发生的具体位置。
8. **Lattice Temperature** (仅 `models lat.temp` 的 run) — 热点位置与峰值,是否与失效点重合。

每一步都要回答一句话:"这张图证实/证伪了哪个假设"。不能回答就说明这张图不该出现在报告里。

### 4.2 何时存 `.str`

- 初始态 (`solve init` 之后) 存一张,用于结构自检。
- 每个关键工作点存一张:阈值附近、饱和区、击穿前一步、SEU 峰值时刻、温度峰值时刻。
- 不要每个偏压点都存 —— `.str` 是体积大头,8 GB 内存 / 123 GB 磁盘的远端会被扫描 run 塞满。

---

## 5. 可视化候选项 (显式选择,不要默认只用一个)

| 工具 | 定位 | 调用 | 何时用 | 限制 |
|---|---|---|---|---|
| **TonyPlot** | 快速查看 (2D 结构 + 曲线) | `export DISPLAY=:0; tonyplot <run>.str &` / `tonyplot <run>.log &` | **交互排查第一选择**:结构自检、曲线速览、拿坐标 | 需要 X;默认样式不达出版标准 |
| TonyPlot3D | 3D 结构/解 | `tonyplot3d <run>.str &` | Victory Process/Device 的 3D 结果 | 需要 X;2D run 不必用 |
| **Victory Visual** | **[出版级导出优先]** | `victoryvisual <run>.str &` (脚本/批处理接口需按本机版本核对) | 需要高质量导出的 2D/3D 场图、云图 | 版本较新,选项与 TonyPlot 不通用 |
| **外部 matplotlib** | **[默认 — 最终出图]** | `python plot_*.py`,数据来自 §3 解析器 | **所有进入报告/论文/专利的曲线图** | 画不了 `.str` 空间场;不能替代 §4 |

### 5.1 选择规则 (硬规则)

- **曲线图 (I-V、瞬态、拟合对比) 一律用外部 matplotlib 出最终图**,因为只有它能保证 DPI/字号/配色/双轴一致,并且能把文献参考点画上去。
- **空间场图 (`.str` 云图) 用 Victory Visual 导出为首选**,TonyPlot 作为快速查看与坐标读取。
- 无论用哪个,**每张进入报告的 2D 空间图必须有 §9 的 manifest 行**,否则不得引用。

### 5.2 无显示环境的降级记录 (必须原文写进报告)

本项目远端 `tcad` 上 X 显示 `:0` 存在 (root 已登录 tty1),GUI 工具前必须先 `export DISPLAY=:0`。若 DISPLAY 不可用:

```markdown
### 可视化状态
- `.log` 曲线:已用 Python 解析 + matplotlib 出图,路径:D:\SILVACO_LOCAL\outputs\*.png (`.png` 属主控端,不进 bulk,见 §11)
- `.str` 空间分布:未查看 / 用户截图已检查 / TonyPlot 已打开 / Victory Visual 已导出
- 限制:当前会话 DISPLAY 不可用,**不得声称已完成空间诊断**;高场区、热点、电流路径结论一律标注为"待 .str 验证"。
```

---

## 6. 批处理导出与已知坑

### 6.1 TonyPlot `.set` 批处理

TonyPlot 的显示设置 (量、色标范围、缩放、图例) 可保存为 `.set` 文件并复用:

```bash
export DISPLAY=:0
export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
tonyplot -st efield_2d.set RUN_pgan_bv_vd100.str
```

**流程 (不要跳):**
1. 先在 GUI 里手工调好一张图 (选量、定色标上下限、定缩放),**从 GUI 保存 `.set`**。
2. 再把这个 `.set` 套用到同一批的其它 `.str`,保证一组图色标一致、可横向比较。
3. 把 `.set` 文件与 `.in` deck 一起纳入版本记录 (`.set` 是轻量文本,可留在主控端)。

### 6.2 已知坑

| 现象 | 真实原因 | 正确处理 |
|---|---|---|
| `tonyplot -st x.set` 报语法错误 / 图打不开 | **`.set` 模板本身写错或版本不匹配 —— 不是 `.str` 数据损坏** | 回到 GUI 重新保存一份 `.set`;不要重跑仿真,不要怀疑数据 |
| 一组图色标各不相同,无法比较 | 未固定 `scale_min/scale_max`,工具按每张图自动定标 | 在 `.set` 里锁定色标范围,并把范围写进 manifest |
| 批处理脚本在无 DISPLAY 的会话里挂住 | GUI 工具仍需 X | `export DISPLAY=:0`;或改由外部 Python 出曲线图,空间图延后 |
| 导出的 PNG 分辨率不够 | GUI 截屏而非导出 | 用工具的导出/打印功能设置像素尺寸,达到 DPI ≥ 300 的等效分辨率 |
| 手动截图当成导出图 | 无 provenance、无色标数值 | 截图只能进 `progress.md` 当过程记录,**不得进正式报告** |

> **[未核实:Victory Visual 批处理接口]** 其脚本调用方式随版本变化较大,本次审计**未能在本机核实**具体选项。首次使用前先 `victoryvisual -h` 实测,核对结果写进 `RUN_MANIFEST.md`,不要凭猜写脚本。
> 注意:**不要去 `$SILVACO/doc/` 找**——该目录下只有安装与 SFLM 手册,没有任何 ATLAS / Victory 工具手册;ATLAS manual 的实际位置见 §1 第 4 层路径表。

---

## 7. 出版级出图规范

### 7.1 硬性参数

- DPI ≥ **300** (`savefig(..., dpi=300)`),矢量场合另存 `.pdf`/`.svg`。
- 字号 ≥ **12 pt** (轴标签、刻度、图例全部),标题可 14 pt。
- 线宽 **1.5–2 pt**;标记点尺寸与线宽匹配,数据点稀疏时才画 marker。
- **colorblind-safe 配色**,禁止使用 matplotlib 默认循环色;推荐 Okabe–Ito 或 `tab10` 的受限子集,并且**同时用线型区分** (实线/虚线/点划线),保证黑白打印可读。
- 坐标轴必须带单位:`I_D (mA/mm)`、`V_G (V)`、`V_D (V)`、`Time (ns)`、`T_lattice (K)`。
- **双轴规范**:左轴 = 电流,右轴 = 温度 (自热/SEU 图固定这个约定);两轴颜色与对应曲线一致,右轴标签注明量与单位。
- log 轴只在跨量级 (漏电、BV) 时使用;**用户/专利要求线性轴时不得擅自改 log**。
- 图内不写中文 (期刊/专利兼容);中文说明写在图注和正文里。

### 7.2 骨架

```python
import matplotlib as mpl
import matplotlib.pyplot as plt

OKABE_ITO = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000"]
mpl.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.size": 12, "axes.labelsize": 13, "axes.titlesize": 14,
    "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 11,
    "lines.linewidth": 1.8, "axes.linewidth": 1.2,
    "axes.prop_cycle": mpl.cycler(color=OKABE_ITO),
})

fig, ax = plt.subplots(figsize=(5.0, 3.6))
ax.plot(t_ns, i_ma, color=OKABE_ITO[0], ls="-",  label="Sim. $I_D$")
ax.set_xlabel("Time (ns)"); ax.set_ylabel("$I_D$ (mA/mm)", color=OKABE_ITO[0])
ax2 = ax.twinx()                                   # 左电流 / 右温度
ax2.plot(t_ns, t_lat, color=OKABE_ITO[1], ls="--", label="Sim. $T_{lattice}$")
ax2.set_ylabel("$T_{lattice}$ (K)", color=OKABE_ITO[1])
ax.scatter(ref_t, ref_i, marker="o", facecolors="none",
           edgecolors=OKABE_ITO[6], zorder=5, label="Ref. [12]")   # 文献参考点
fig.legend(loc="upper right", bbox_to_anchor=(0.98, 0.95), frameon=False)
fig.savefig("D:/SILVACO_LOCAL/outputs/RUN_pgan_seu_20260726T031200Z_id_temp.png")
```

---

## 8. 拟合报告规范 (与文献/实测对齐时**强制**)

任何"拟合到文献/实测"的说法,报告里必须**同时**给出下面 4 样。缺一样,该结论视为未验证。

### 8.1 四件套

1. **仿真曲线** — 来自 `.log` 的连续曲线,标注 deck 文件名与 run tag。
2. **文献/实测参考点** — 以散点 (空心圆/方块) 叠在同一张图上,图例写清出处 `Ref. [n]` 或 `Meas.`,正文给完整引用与取点方式 (原图数字化 / 表格数据 / 实测)。
3. **误差表** — 逐点相对误差,不是只给一句"吻合良好"。
4. **文字结论段** — 明确写四件事:**已拟合到什么程度 / 未拟合什么 / 原因 / 补齐方案**。

### 8.2 误差表模板

| 工作点 | 参考值 (来源) | 仿真值 | 绝对误差 | **相对误差 %** | 是否达标 (阈值) |
|---|---|---|---|---|---|
| Vth @ Id=1e-6 A/mm | 1.65 V (Ref.[12] Fig.3) | 1.58 V | -0.07 V | **-4.2 %** | 达标 (≤10 %) |
| Ion @ Vg=6 V, Vd=10 V | 480 mA/mm (Ref.[12]) | 412 mA/mm | -68 mA/mm | **-14.2 %** | 不达标 (≤10 %) |
| BV @ Id=1e-3 A/mm | 720 V (Ref.[15] Tab.II) | 690 V | -30 V | **-4.2 %** | 达标 (≤10 %) |

规则:
- 相对误差 = (仿真 − 参考) / |参考| × 100 %,**保留符号**,让读者看出系统性高估/低估。
- 每行必须写参考值出处到图/表编号,不能只写文献号。
- 达标阈值在报告开头统一声明 (不同指标可不同:Vth ≤10 %、BV ≤10 %、Ion ≤20 % 等),事后不得改阈值凑达标。

### 8.3 结论段模板 (照抄格式)

```markdown
**拟合状态 (RUN_pgan_idvg_20260726T031200Z)**
- 已拟合:亚阈区斜率与 Vth (相对误差 -4.2 %),转移特性形状一致。
- 未拟合:大电流区 Ion 系统性偏低 14.2 %;Vd>15 V 的输出特性尚未与文献比对。
- 原因判断:接入电阻未建模 + 沟道迁移率场依赖参数取默认值;非收敛问题 (.out 退出码 0,无 Convergence failure)。
- 补齐方案:(1) 在源漏加 `contact name=<电极> resistance=<Ω>` 校准接入电阻;(2) 用文献给的低场迁移率标定 `mobility` 参数;
  (3) 补 Vd 0–25 V 的 IdVd 与 Ref.[12] Fig.4 对齐。预计 1 轮迭代,不需要改网格。
```

> `contact ... resistance=` [已核实],但核实过程本身值得记一笔:atlas.key 里**没有** `resistance` 这一行,CONTACT 卡上登记的是**截断名** `resistan`(`grep -n -iE '^ *resistan ' atlas.key` → `4465:   resistan     NUM     5       -999`,CONTACT 卡为 4460–4605)。同卡的 `capacita`(4466) 同样是 `capacitance` 的截断写法。完整拼写在 Silvaco 自带 deck 里被大量使用,例如本地已核 `d:\knowledge\exp25\CMOS_ands_BiCMOS\SOI_ex11.in:340: CONTACT name=gate RESISTANCE=5e4 ohms`(:340–343 共 4 条,gate/gate_1/gate_2/gate_3;旧记 `:338` 行号有偏移,该行实为注释 `# Series resistances to Gate contacts`),本地 exp25 子集 `contact ... resistance` 共 20 处/9 个 deck。`Adv_CMOS_ex10.in:499: CONTACT name=drain resistance=$Rsd` 与"共 30+ 处"出自远端全量 examples 树,本地 exp25 无该文件 [待远端复核]。
> **通用教训:atlas.key 里 grep 不到某个全拼,不等于该参数不存在——先用词根截断再 grep 一次**(如 `grep -iE '^ *resist' `),确认不是截断名之后才判定"不存在"。

**禁止表述**:"基本吻合"、"趋势一致"、"误差在可接受范围内" —— 除非后面立刻跟数字和阈值。

---

## 9. 2D 图 provenance manifest

每一张进入报告的 2D 空间场图 (`.str` 云图),在 `RUN_MANIFEST.md` 里对应**一行**。字段固定如下:

| 字段 | 含义 | 示例 |
|---|---|---|
| `png_file` | 图片绝对路径 (`.png` 属主控端,不进 bulk,见 §11) | `D:\SILVACO_LOCAL\outputs\RUN_pgan_bv_20260726T031200Z_efield.png` |
| `source_str` | 生成该图的 `.str` 归档绝对路径 (bulk 按 run 建子目录) | `E:\silvaco2425\bulk\str\RUN_pgan_bv_20260726T031200Z\pgan_bv_vd100.str` |
| `time_s` | 该快照对应的物理时刻 (s);稳态填 `steady` | `1.2e-9` / `steady` |
| `scalar_display_name` | 所画标量在工具里的显示名 | `Electric Field` |
| `unit` | 该标量单位 | `V/cm` |
| `scale_type` | 色标类型 | `linear` / `log` |
| `scale_min` | 色标下限 (锁定值,非自动) | `0` |
| `scale_max` | 色标上限 (锁定值,非自动) | `3.5e6` |
| `export_tool` | 导出工具 | `VictoryVisual` / `TonyPlot` / `matplotlib` |
| `export_version` | 工具版本字符串 | `5.40.0.R` |
| `source_sha256` | `.str` 文件 SHA-256 | `9f2c…` |
| `png_sha256` | PNG 文件 SHA-256 | `41ab…` |
| `acceptance_status` | 验收状态 | `accepted` / `provisional` / `rejected` |

规则:
- `scale_min`/`scale_max` **必须是锁定值**。自动定标的图只能标 `provisional`,不得用于跨条件对比。
- `acceptance_status=provisional` 的图可以放进 `progress.md`,**不得**进入对外报告/论文/专利稿。
- 两个 sha256 用于事后追溯:图和源数据对不上号时,以 sha256 为准,不以文件名为准。

生成 sha256:

```bash
sha256sum RUN_pgan_bv_20260726T031200Z_vd100.str RUN_pgan_bv_20260726T031200Z_efield.png
```

```python
import hashlib, pathlib
def sha256(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
```

manifest 行的机器可读形式 (追加到 `RUN_MANIFEST.md` 的表格,或并行维护一份轻量 `manifest.csv` 留在主控端):

```csv
png_file,source_str,time_s,scalar_display_name,unit,scale_type,scale_min,scale_max,export_tool,export_version,source_sha256,png_sha256,acceptance_status
```

---

## 10. 三件套:progress.md / findings.md / RUN_MANIFEST.md

三个文件职责**不重叠**,不要互相抄。

| 文件 | 回答的问题 | 时间性 | 谁看 |
|---|---|---|---|
| `progress.md` | **我这一轮做了什么、结果如何、下一步做什么** | 按 session 追加,永不删除历史 | 你自己 + 用户跟进 |
| `findings.md` | **我学到了什么可复用的知识/规则** | 按知识点组织,可合并可提炼 | 未来的自己 + 别的项目 |
| `RUN_MANIFEST.md` | **这次 run 到底是什么配置、产出了哪些文件、图从哪来** | 每个 run 一节,只增不改 (改要留痕) | 复现者 + 审稿人 |

### 10.1 `progress.md` 模板

```markdown
## 2026-07-26 Session: pGaN HEMT BV 拟合第 2 轮

### 已执行
- run tag: `RUN_pgan_bv_20260726T031200Z`
- deck: `D:\SILVACO_LOCAL\decks\pgan_bv.in` (结构 + 电学合并,单文件)
- 远端运行目录: `/root/DECKBUILD/RUN_pgan_bv_20260726T031200Z`
- 提交: `deckbuild -run -ascii pgan_bv.in -outfile pgan_bv.out` (simflags `-V 5.40.0.R -P 4`)
- 修改点: 漏端 mesh 加密;`impact selb` 打开;`method climit=1e-4`(击穿必需,见 §2.3)
- 监控终止串: 退出码 0 / `ATLAS DIED` / `Convergence failure`

### 结果
| run tag | 关键参数 | .out 终止 | 关键指标 | 判定 | 图/表 |
|---|---|---|---|---|---|
| RUN_pgan_bv_20260726T031200Z | field plate Lfp=2 um | exit 0 | BV=690 V @1e-3 A/mm | 达标(-4.2%) | outputs\...efield.png |

### 诊断
- `.out`: 无 Convergence failure;Vd>650 V 后迭代数由 6 升至 21 → 已减步长
- `.log`: 击穿拐点陡,漏电基线 2e-9 A/mm,符合预期
- `.str`: 峰值电场 3.2e6 V/cm 位于场板末端,与 Ref.[15] 描述一致
- 根因判断: 上一轮 BV 偏低源于场板末端网格过粗,不是模型问题

### 下一步
- 补 IdVd 与 Ref.[12] Fig.4 对齐;标定接入电阻
```

### 10.2 `findings.md` 模板

```markdown
## 发现:pGaN HEMT BV 对场板末端网格密度极敏感
- 来源: 本项目 RUN_pgan_bv_20260726T0312 vs ...T0140 对比 + Ref.[15]
- 证据: 场板末端 y 向网格 50 nm→10 nm,BV 由 610 V 升到 690 V,峰值电场位置不变
- 适用范围: 带场板的横向 GaN 器件、impact 打开的 BV 仿真
- 不适用/风险: 不适用于无场板结构;网格再细收益递减且节点数翻倍
- 后续规则: BV deck 一律先做一次网格收敛性检查再报 BV 数字
```

### 10.3 `RUN_MANIFEST.md` 模板

```markdown
## RUN_pgan_bv_20260726T031200Z

### 环境 (事实,不是假设)
- host `tcad` (RHEL 7.9, 8 vCPU / 8 GB) — SSH 前先探测实际 IP,不硬编码
- Silvaco root: `/atctools/Synopsys/Silvaco2024` (bin 默认不在 PATH,须显式 export)
- 版本锁定: `simflags="-V 5.40.0.R -P 4"`;license: SFLM `SFLM_SERVERS=+localhost`
- 远端运行目录: `/root/DECKBUILD/RUN_pgan_bv_20260726T031200Z`

### 输入
- deck: `pgan_bv.in` (sha256 …)
- 显示设置: `efield_2d.set` (sha256 …)

### 产物与归档
| 远端文件 | 归档位置 | 大小 |
|---|---|---|
| pgan_bv.out | E:\silvaco2425\bulk\log\RUN_pgan_bv_20260726T031200Z\ | 1.2 MB |
| pgan_bv_idvd.log | E:\silvaco2425\bulk\log\RUN_pgan_bv_20260726T031200Z\ | 340 KB |
| pgan_bv_vd100.str | E:\silvaco2425\bulk\str\RUN_pgan_bv_20260726T031200Z\ | 86 MB |

### 已核对的本机事实 (固化,后续 run 直接复用)
- 实际出现的终止串: `…`
- `.log` 表头实际列名: `…`
- `output` 可用字段: `…`

### 2D 图 provenance
| png_file | source_str | time_s | scalar_display_name | unit | scale_type | scale_min | scale_max | export_tool | export_version | source_sha256 | png_sha256 | acceptance_status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| …efield.png | …vd100.str | steady | Electric Field | V/cm | linear | 0 | 3.5e6 | VictoryVisual | 5.40.0.R | 9f2c… | 41ab… | accepted |
```

---

## 11. 归档与文件放置纪律 (用户硬规则,复述于此)

- 主控端 `D:\SILVACO_LOCAL` **只放**:`.py` 脚本 / `.md` 技术文档 / 轻量 `.csv` / `.png` 截图与图 / `.in` deck。
- `.in` deck 必须把**建模(结构)与特性仿真(电学)合并为同一个文件**:
  `go atlas`(建结构) → `save outf=*.str` → `go atlas`(重新进入) → `mesh inf=*.str` → 电学求解。
- **一切大体积 `.str` / `.log` 归档到 `E:\silvaco2425\bulk\{str,log}\<run id>\`**(按 run 建子目录,层级与 batch-run-and-monitor.md §5 一致);远端运行期间产物留在
  `/root/DECKBUILD/RUN_<case>_<UTCstamp>/`,run 结束后回传归档。
- 远端 `/root/DECKBUILD` 是唯一正在迭代的运行区;**不要把整套远端工程复制回 Windows**。
- 不要往 `/mnt/hgfs/{share_wm,share24,16sil_share}` 写大文件 —— 已 98% 满。

回传示例 (IP 先探测,别用失效的 SSH 别名)。

> **[已核实,并纠正本文件旧版记载]** 本文件此前写 "别名 silvaco 指向已失效的 192.168.50.134",**方向写反了**。2026-07-26 实测:
> ```
> $ ssh -i ~/.ssh/silvaco_ed25519 root@192.168.50.134 "hostname; hostname -I; cat /etc/redhat-release"
> tcad
> 192.168.50.134 192.168.122.1
> Red Hat Enterprise Linux Server release 7.9 (Maipo)     → exit 0
> $ ssh -i ~/.ssh/silvaco_ed25519 root@192.168.107.128 "hostname"
> kex_exchange_identification: read: Connection reset by peer   → exit 255
> ```
> 即 **`192.168.50.134` 是活的、`192.168.107.128` 是死的**。规则不变(每次会话先探测 IP、不硬编码),但默认值改回 `192.168.50.134`。

```bash
HOST=192.168.50.134           # 2026-07-26 实测可达 (hostname=tcad, RHEL 7.9);先探测再用
KEY=C:/Users/Administrator/.ssh/silvaco_ed25519
RUN=RUN_pgan_bv_20260726T031200Z
mkdir -p E:/silvaco2425/bulk/log/$RUN E:/silvaco2425/bulk/str/$RUN   # 按 run 建子目录 (batch-run §5)
scp -i "$KEY" root@$HOST:/root/DECKBUILD/$RUN/*.log E:/silvaco2425/bulk/log/$RUN/
scp -i "$KEY" root@$HOST:/root/DECKBUILD/$RUN/*.out E:/silvaco2425/bulk/log/$RUN/
scp -i "$KEY" root@$HOST:/root/DECKBUILD/$RUN/*.str E:/silvaco2425/bulk/str/$RUN/
```

回传后立刻算 sha256 并写进 `RUN_MANIFEST.md`,再删除远端不再需要的 `.str` (远端 `/` 只剩 ~123 GB)。

---

## 12. 经验沉淀

- 可复用规则写进 `findings.md`;跨项目通用的写进本技能的 references,并注明"本机已核对"。
- 外部文献 PDF 归入文献库;Silvaco 用法、examples 摘录、manual 结论写成条目化知识,**注明来源路径 + 行号**。合法来源只有 §1 第 4 层路径表里那三个:
  `.../lib/atlas/5.40.0.R/common/atlas.key`(存在性/默认值)、`.../lib/atlas/5.40.0.R/docs/atlas_users1.pdf`(语义)、`.../examples/deckbuild/5.2.40.R/`(用法)。**不要再写 `$SILVACO/doc/...`**,那里没有 ATLAS manual。
- **标注纪律 (硬规则)**:`[已核实]` 只能用于**当场贴得出 grep 命令与非空输出**的条目,格式如 `[已核实: atlas.key:688 climit NUM 51 10000]`。贴不出证据就写 `[未核实]`——**这是允许的答案,而且比编一个参数好得多**。已写下的 `[未核实]` 条目**不许删除**,它记录的是知识边界。
- **example 溯源纪律**:引用任何 example deck 之前先 `grep -iE '^ *go ' <deck>.in`。`GO victorydevice` / `victoryprocess` 的 deck **不是 ATLAS deck**,其语法不能直接搬进 `go atlas` deck——本技能包历史上的多个虚构参数(`lte.timestep`、`seu.max.rad`、`constant.timestep`、`impact ... hysteresis`/`e.min`)全部来自这一类误抄。
- **不要把失败隐去**。一次 `Convergence failure` 的根因记录,价值高于三张漂亮的图。
- 每条沉淀都要带**适用范围**和**不适用/风险**两栏 —— 没有边界的经验会在下一个器件上误导你。
- 两次失败规则:同类失败最多试两次;第二次仍失败就停止盲试,回到第 4 层 (文献/examples) 做根因分析。
