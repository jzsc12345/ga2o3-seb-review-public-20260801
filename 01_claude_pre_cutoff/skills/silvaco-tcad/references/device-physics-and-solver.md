# ATLAS 器件物理与求解器模式：material / models / method / solve / output

> 用途：给出 Silvaco **ATLAS** 电学仿真段的字段表、模型开关族、求解器**候选项**与偏压/瞬态推进策略，并规定"求解器配置必须逐字冻结、禁止凭印象串用"的纪律。

本文只覆盖 `.in` deck 的**电学仿真部分**。结构/网格部分见 `references/structure-and-mesh.md`；运行与提交见 `references/batch-run-and-monitor.md`。

> **核实口径（全文适用）**：标 `已核实` 的条目必须能当场贴出 `atlas.key` 行或 manual 原文；贴不出来的一律标 `未核实`，条目保留不删。
> 权威表：`/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key`（ATLAS 5.40.0.R），行格式 `名字  类型(NUM/LOG/CHAR)  内部索引  默认值`。
> manual：`/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/docs/atlas_users1.pdf`（用 `pdftotext` 取语义）。
> 例子：`/atctools/Synopsys/Silvaco2024/examples/deckbuild/5.2.40.R/`。**引用例子前先 `grep -iE '^ *go ' <deck>.in`**：很多 `Rad_Rel_*` / `GaN_Power_*` / `Other_Power_*` 是 `GO victorydevice` 的 Victory Device deck，其语法不能直接当 ATLAS 依据。

---

## 0. 电学段在 deck 中的位置

本项目规定：**建模(结构)与特性仿真(电学)合并为同一个 `.in`**，中间通过 `.str` 落盘再导入。

```silvaco
go atlas simflags="-V 5.40.0.R -P 4"
# ... mesh / x.mesh / y.mesh / region / electrode / doping ...
save outf="<case>_structure.str"

go atlas simflags="-V 5.40.0.R -P 4"     # 重新进入 ATLAS
mesh inf="<case>_structure.str"          # 导入刚生成的结构
# ---- 以下即本文覆盖的电学段 ----
material ...
mobility ...
models ...
impact ...
trap ...
contact ...
thermcontact ...
method ...
output ...
solve ...
save outf="*.str"
log outf="*.log" ... log off
extract ...
quit
```

段落顺序不是随意的：**所有物理语句必须在第一条 `solve` 之前**。`solve` 之后再改 `models/method`，只对其后的 `solve` 生效，容易在 log 里造成"两段用了不同物理"的隐性不一致。

| 文件角色 | 扩展名 | 由谁产生 | 用途 |
|---|---|---|---|
| deck | `.in` | 作者 | 唯一输入，进版本管理 |
| 结构/解快照 | `.str` | `save outf=` | 空间分布诊断 + `load ... master` 续跑 |
| 曲线日志 | `.log` | `log outf=` | I-V / 瞬态曲线，`extract` 的输入 |
| 提取数据 | `.dat` | `extract` | 轻量数值结果，可回传 Windows |
| 运行日志 | `.out` | `deckbuild -outfile` | 终止状态、收敛过程、报错 |

大体积 `.str` / `.log` **不要留在主控端**：远端运行期间放 `/root/DECKBUILD/<run>/`，结束后归档到 `E:\silvaco2425\bulk\{str,log}\`。主控端 `D:\SILVACO_LOCAL` 只放 `.py` / `.md` / 轻量 `.csv` / `.png` / `.in`。

---

## 1. `material`：材料参数（宽禁带自定义材料重点）

ATLAS 自带材料库对 Si/GaAs/GaN 较全，对 β-Ga₂O₃ 这类新材料**必须显式给全参数**。标准做法是挂一个已有半导体作为默认模板，再逐项覆盖：

```silvaco
material material=BetaGa2O3 user.group=semiconductor user.default=GaN \
         affinity=4.0 eg300=4.8 nc300=3.72e18 nv300=4.2e18 \
         permittivity=10.0 mun=300 mup=10 \
         tcon.const tc.const=0.27
material material=Al2O3 permittivity=9.0  tcon.const tc.const=0.03
material material=SiO2  permittivity=3.9  tcon.const tc.const=0.014
material material=air                     tcon.const tc.const=2.6e-4
material material=Nickel                  tcon.const tc.const=0.907
```

### 1.1 作用域候选项

| 写法 | 含义 | 何时用 |
|---|---|---|
| **[默认]** `material material=<名字> ...` | 按材料名批量赋值 | 结构由 ATLAS 内建语句建、材料名可靠时 |
| `material region=<N> ...` | 按 region 号赋值 | **DevEdit 重划分后**；此时用户自定义材料名的映射不一定完整保留，用 region 号更稳 |
| `material name=<region名> ...` | 按 region 名赋值 | region 命名规范且唯一时；需在 `$SILVACO/examples` 核对本版本是否支持该关键字 |

> 已验证经验：本项目"ATLAS 建基底 → DevEdit 加多边形并重划分 → 回到 ATLAS"的流程里，第二段 ATLAS 全部改用 `material region=N ...` / `mobility region=N ...` / `impact region=N ...` 才与第一段物理一致。

### 1.2 常用字段表

| 字段 | 物理含义 | 单位 | 状态 |
|---|---|---|---|
| `user.group=semiconductor` | 声明自定义材料属于半导体组 | — | 已核实：atlas.key:2926，material 卡（1948–3072） |
| `user.default=<模板材料>` | 未显式给出的参数继承该材料（本项目用 `GaN`） | — | 已核实：atlas.key:2925，material 卡 |
| `affinity` | 电子亲和能 χ | eV | material 卡（关键字无争议）；atlas.key 行号本文旧记录 :1953 与 `structure-and-mesh.md`/`wbg-radiation-and-seb.md` 的 :1961 **互为镜像**，**[待 atlas.key 复核]** |
| `eg300` | 300 K 禁带宽度 | eV | 已核实：atlas.key:1952，material 卡 |
| `nc300` | 300 K 导带有效态密度 | cm⁻³ | 已核实：material 卡 |
| `nv300` | 300 K 价带有效态密度 | cm⁻³ | 已核实：material 卡 |
| `permittivity` | 相对介电常数 | — | material 卡（关键字无争议）；atlas.key 行号本文旧记录 :1961 与 `structure-and-mesh.md`/`wbg-radiation-and-seb.md` 的 :1953 **互为镜像**，**[待 atlas.key 复核]** |
| `mun` / `mup` | 低场电子/空穴迁移率（`analytic`/常数迁移率的基准值） | cm²/V·s | 已核实：material 卡 |
| `tcon.const` | 启用常数热导率模型 `k(T)=TC.CONST`。**这是 LOG 型开关，裸写、不带等号** | — | 已核实：atlas.key:2980 `tcon.const LOG 1 f`。⚠️ **绝不能写 `tcon.const=0.13`**——数值属于下一行的 `tc.const` |
| `tc.const` | 常数热导率值（别名 `tc.c0`） | W/cm·K | 已核实：atlas.key:2036 `tc.const NUM 79`（别名 2037 `tc.c0`） |
| 温变热导率模型族 | `tcon.power`（`k(T)=TC.CONST·(T/300)^TC.NPOW`）、`tcon.polynom`、`tcon.recipro`、`tcon.comp`（组分相关，适用材料的默认）、`tcon.almabulk` | — | 已核实：manual §"Thermal Conductivity"；示例语法 `material mat=Diamond TCON.POWER TC.NPOW=2 TC.CONST=1.4`。β-Ga₂O₃ 的各向异性热导可用 `tc.aniso`（atlas.key:2394，默认 0.0），介电各向异性对应 `perm.aniso`（2393） |
| `taun0` / `taup0` | SRH 电子/空穴寿命 | s | 候选，需在 `$SILVACO/examples` 或 manual 核对本版本默认值 |
| `nsrhn` / `nsrhp` | SRH 寿命的掺杂依赖参考浓度 | cm⁻³ | 候选，需核对 |
| `augn` / `augp` | Auger 复合系数 | cm⁶/s | 候选，需核对 |
| `arichn` / `arichp` | 热电子发射 Richardson 常数 | A/cm²K² | 候选，需核对 |
| `eg300 + egalpha/egbeta` | 禁带温变（Varshni） | — | 候选，需核对参数名 |

规则：
- **禁带宽度这类关键参数一旦选定就要冻结并写进 `RUN_MANIFEST.md`**。本项目历史上 BV deck 用过 `eg300=4.4`、SEB deck 用 `eg300=4.8`，二者不可互相引用结论。
- 绝缘层/空气/金属只在开 `lat.temp` 时才必须给热导率；不开自热可以省，但**开了自热却漏给某个 region 的 `tc.const`**，会得到不可信的温度场。
- 不要用"记忆里的材料参数"。每个数值都要能追到文献或官方例子，并记进 `findings.md`。

---

## 2. `models`：模型开关族与"不要一次全开"

```silvaco
models analytic fldmob srh auger fermi incomplete bgn print lat.temp
```

| 开关 | 含义 | 代价 / 注意 |
|---|---|---|
| `analytic` | 解析迁移率模型（含掺杂/温度依赖） | 低，通常必开 |
| `fldmob` | 平行电场依赖迁移率（速度饱和） | 低，高场/高压必开 |
| `conmob` | 浓度依赖迁移率查表 | 与 `analytic` 属同类，**不要同时开**，按材料选一个 |
| `srh` | Shockley-Read-Hall 复合 | 低，几乎必开 |
| `auger` | 俄歇复合 | 低，高注入 / SET / SEB 建议开 |
| `fermi` | Fermi-Dirac 统计 | 中，重掺杂/宽禁带建议开 |
| `incomplete` | 杂质不完全电离 | 中，宽禁带深能级掺杂建议开；会拖慢收敛 |
| `bgn` | 带隙变窄 | 低 |
| `lat.temp` | 晶格热传导方程（自热） | **高**，方程数增加，必须配 `thermcontact` 与 `tc.const`。已核实：atlas.key:1019 `lat.temp LOG 43 f`（models 卡 962–1947） |
| `print` | 把生效的模型和材料参数打印到运行日志 | 零成本，**强制常开**——它是核对"物理是否真的生效"的唯一证据。已核实：atlas.key models 卡 `print LOG 12 f` |

原则（对应源技能"先跑最小物理再加模型"）：

1. **基线最小集**：`models analytic fldmob srh fermi print`。先让 `solve init` + 小偏压跑通。
2. 按目标逐项加：高注入加 `auger`；宽禁带加 `incomplete bgn`；自热/SEB 加 `lat.temp`。
3. **一次只加一族**，每加一族重跑基线偏压点，确认收敛没崩、静态工作点没有非物理跳变。
4. 不要一次全开。全开的直接后果是：收敛失败时无法定位是哪一个模型引入的，两次失败规则会被浪费在盲试上。
5. `models` 行改了就是**新的物理谱系**，旧 run 的结果不能混着报。

按任务的常见组合：

| 目标 | 典型 `models` 行 | 备注 |
|---|---|---|
| 转移/输出特性校准（低压） | `analytic fldmob srh auger fermi print` | 不开 `lat.temp`，快 |
| 反向击穿 BV | `analytic fldmob srh fermi incomplete bgn print lat.temp` | 必须配 `impact` |
| SET 瞬态（低压） | `analytic fldmob srh auger fermi print` | 等温即可，先定位电学响应 |
| SEB 瞬态（高压自热） | `analytic fldmob srh auger fermi incomplete bgn print lat.temp` | 必须配 `impact` + `thermcontact` |

---

## 3. `mobility`：场依赖与 Caughey-Thomas 参数

```silvaco
mobility material=BetaGa2O3 vsatn=2.42e7 betan=1.37 betap=1.09 \
         mu1n.caug=10 mu2n.caug=300 ncritn.caug=2e17
```

| 字段 | 含义 | 状态 |
|---|---|---|
| `vsatn` / `vsatp` | 电子/空穴饱和漂移速度（cm/s），`fldmob` 的核心参数 | **未核实**：本轮未对该字段做 atlas.key 取证（旧记录标"已验证"但拿不出 grep 输出）。条目保留，用前先 `grep -n -iE '^ *vsatn ' atlas.key` |
| `betan` / `betap` | 场依赖迁移率表达式的 β 指数 | 已核实：atlas.key:5938 `betan NUM 41 2.0` / 5939 `betap NUM 42 1.0`（mobility 卡）。**注意同名不同卡**：`impact` 卡上也有 `betan/betap`（atlas.key:5431/5433，默认均 1.0，含义是电离系数指数），`material` 卡上还有一对（2224/2226）。三处默认值和物理含义都不同，读别人的 deck 时先看它挂在哪条语句上 |
| `mu1n.caug` / `mu1p.caug` | Caughey-Thomas 低端（重掺杂极限）迁移率 | **未核实**：本轮未取到 atlas.key 行（旧记录标"已验证"，但按新口径拿不出 grep 输出即降级）。条目保留 |
| `mu2n.caug` / `mu2p.caug` | Caughey-Thomas 高端（轻掺杂极限）迁移率 | **未核实**：同上 |
| `ncritn.caug` / `ncritp.caug` | Caughey-Thomas 掺杂转折浓度（cm⁻³） | 已核实：atlas.key:5996 `ncritn.caug NUM 75 1.072e17` / 5998 `ncritp.caug NUM 76 1.606e17`（mobility 卡，全文件仅此两处）；manual Eq 3-223/3-224 中它位于 `(N/NCRITN.CAUG)^DELTAN.CAUG` 分母项，即掺杂转折点 |
| `alphan.caug` / `alphap.caug` | Caughey-Thomas 掺杂依赖指数 | **未核实**：atlas.key 中未核到该字面行。manual Eq 3-223 里这个指数写作 `DELTAN.CAUG`（`(N/NCRITN.CAUG)^DELTAN.CAUG`），写进 deck 前必须先 grep 确认拼写 |

实用技巧（本项目已用过，属于合法的"有效迁移率标定"，但**必须在 deck 注释和 `RUN_MANIFEST.md` 里写明**）：

```silvaco
# 把 Caughey-Thomas 三个参数压平 = 强制常数有效迁移率，用于拟合实测转移特性
mobility material=BetaGa2O3 vsatn=2.0e7 betan=1.0 \
         mu1n.caug=1 mu2n.caug=1 ncritn.caug=1e30 \
         mu1p.caug=0.1 mu2p.caug=0.1 ncritp.caug=1e30
```

`ncritn.caug=1e30` 的作用是让掺杂依赖失效，等效于把电子迁移率钉在 `mu1n.caug`。这是标定手段，不是物理模型；**不要把这种 deck 的迁移率当成材料属性引用**。

`mobility` 的作用域关键字与 `material` 相同：`material=` / `region=`（DevEdit 后用 `region=`）。

---

## 4. `impact`：碰撞电离（BV / SEB 必备）

```silvaco
impact material=BetaGa2O3 selb \
       an1=2.5e6 bn1=3.96e7 an2=2.5e6 bn2=3.96e7 \
       betan=1.37 egran=8e6
```

| 字段 | 含义 | 状态 |
|---|---|---|
| `selb` | 选择 Selberherr 碰撞电离模型 | 已核实：atlas.key:5370 `selb LOG 3 t`。**默认已是 t**，写它是显式声明而非"打开"；manual §"Selberherr's Model  IMPACT SELB  Recommended for most cases." |
| `an1` / `bn1` | **高场段（E > `egran`）**电子电离系数 A、B | 高低场语义已核实：manual "Index 1 (AP1, BP1, AN1, and BN1) corresponds to field values greater than EGRAN, and index 2 ... corresponds to field values less than EGRAN"（另见 "for electric fields >EGRAN V/cm, the parameters are AN1, AP1, BN1, BP1"）；**本行原先写反了**。关键字与缺省值（`an1` 7.03e5 / `bn1` 1.231e6）无争议，但 atlas.key 行号本文旧记录（an1 :5419 / bn1 :5422）与 `wbg-radiation-and-seb.md` §5.1（bn1 :5421）**互斥**，**[待 atlas.key 复核]** |
| `an2` / `bn2` | **低场段（E < `egran`）**电子电离系数 A、B | 索引 2 = 低场段（语义同上行，已核实）。atlas.key 行号本文旧记录（an2 :5421 / bn2 :5424）与 `wbg-radiation-and-seb.md` §5.1（an2 :5420 / bn2 :5422）**互斥**，**[待 atlas.key 复核]** |
| `egran` | 两段模型的电场分界（V/cm） | 已核实：atlas.key:5435 `egran NUM 13 4.0e5`（Si 默认 4.0e5 V/cm；manual 的非 Si 材料表里为 0.0） |
| `betan` / `betap` | 电离系数指数（`α = A·exp(-(B/E)^BETA)`，manual Eq 3-449/3-450） | 已核实：atlas.key:5431 `betan NUM 11 1.0` / 5433 `betap NUM 12 1.0`。**与 §3 `mobility` 卡的同名字段不是一回事**（mobility 卡 `betan` 默认 2.0），不要跨卡搬运数值 |
| `ap1/bp1/ap2/bp2` | 空穴对应系数（索引约定同上：1=高场段、2=低场段） | 已核实：atlas.key IMPACT 卡（别名 `an1=n.ioniza`、`bn1=ecn.ii`、`ap1=p.ioniza`、`bp1=ecp.ii`）。宽禁带材料常缺可靠数据；缺数据时明确说明"只启用电子电离" |

> **一次性纠错记录**：本表 `an1/bn1` 与 `an2/bn2` 的高低场归属曾长期写反（索引 1 被当成低场段）。若历史 deck 是按旧表填的系数，两组值互换后 BV 会变，**旧 run 的 BV 数值不可与新 run 直接比较**。

规则：
- **不需要击穿的仿真不要开 `impact`**。开着会显著拖慢收敛，还会在高场网格粗的地方制造假的雪崩热点。
- 系数必须成套引用同一篇文献。`an1=2.5e6/bn1=3.96e7` 与 `an1=7.9e5/bn1=2.92e7` 是本项目用过的**两套不同来源**，不可混用、不可跨 run 比较 BV 数值。
- 开 `impact` 时网格必须在高场区（栅漏边缘、场板边缘）加密，否则 BV 数值随网格漂移。

---

## 5. `trap`：体陷阱与界面态

```silvaco
trap region=3 acceptor e.level=0.8 density=2.0e18 \
     degen.fac=1 sign=5.0e-15 sigp=5.0e-15
```

| 字段 | 含义 | 状态 |
|---|---|---|
| `donor` / `acceptor` | 陷阱类型（二选一，决定占据时的净电荷符号） | 已核实：atlas.key:6963 `donor LOG 1 f` / 6964 `acceptor LOG 2 f`。**两者默认都是 f**，必须显式给一个。manual：受主型陷阱空时电中性、被填充（电离）后带负电 |
| `e.level` | 陷阱能级（eV）。ATLAS 约定：`acceptor` 相对**导带底**（Ec−Et）、`donor` 相对**价带顶**（Et−Ev） | 已核实：atlas.key:6989 `e.level NUM 1 -999`（-999 = 未设哨兵值，必须给）。能级基准已在 manual 落实，不再是待办：TRAP 参数表原文 "For acceptors, E.LEVEL is relative to the conduction band edge. For donors, it is relative to the valence band edge."，另见 atlas_users1.pdf Figure 3-1。故上面例子的 `acceptor e.level=0.8` = Ec−0.8 eV |
| `density` | 陷阱**体密度**（cm⁻³） | 已核实：atlas.key:6995 `density NUM 7 -999`。注意 `trap` 卡上永远是体密度 cm⁻³；面密度（cm⁻²）是 `inttrap` 界面态才有的口径，两者差 8 个量级，不要混写 |
| `sign` / `sigp` | 电子/空穴俘获截面（cm²） | 已核实：atlas.key:6992 `sign NUM 4 -999` / 6993 `sigp NUM 5 -999` |
| `degen.fac` | 简并因子 | 已核实：atlas.key:6994 `degen.fac NUM 6 -999`。deck 里常见的 `degen=` 是它的唯一前缀缩写，atlas.key 只登记 `degen.fac` |
| `region=` / `material=` | 作用域 | 已核实：atlas.key:7113 `region CHAR 14` / 7101 `material CHAR 2`（注意 `region` 在 trap 卡上是 **CHAR** 型，`region=3` 按字符字段传入） |
| `name=` / `taun=` / `taup=` | 陷阱标签 / 与陷阱关联的电子、空穴寿命 | 已核实：均在 trap 卡（atlas.key 6962–7115）。**`label=` 不是 trap 卡参数**（atlas.key 里 `label` 只属于独立的 LABEL 卡，5646/5648/5649），从例子 deck 抄 `trap ... label=...` 会带进非法关键字 |

界面态候选项：

| 候选 | 用途 |
|---|---|
| **[默认]** `trap region=<N> ...` | 体陷阱（半绝缘衬底补偿、Fe 掺杂深受主等） |
| `inttrap ...` | 界面态（介质/半导体界面）。**语句名是 `inttrap`（两个 t），不是 `intrap`** — 已核实：atlas.key 该卡起于 7615，`donor`/`acceptor`/`fast`/`density.prot`/`s.i` 五个字段位于 7616–7620。<br>已核实的用法要点：① `s.i` 默认为 **t**（半导体/绝缘体界面），裸写 `inttrap` 就已经指向该界面；② `density` 单位是 **cm⁻²（面密度）**，与 `trap` 卡的 cm⁻³ 差 8 个量级；③ `depth` 默认 5.0e-3 µm，是陷阱向绝缘层内的穿透深度；④ `e.level` 基准与 `trap` 一致（受主 Ec−Et、施主 Et−Ev，manual INTTRAP 条目 + Figure 22-6）。<br>**未核实**：`density.prot` 与 `fast` 在 manual INTTRAP 条目中查无描述（仅 atlas.key 有行），用前须另找依据 |

注意：
- **`trap` 语句与 `method` 行里的 `trap` 关键字完全无关**。前者是物理陷阱，后者是求解器"发散时自动减步"。deck 里两者常同时出现，评审时不要看混。
- 陷阱会显著改变收敛行为和阈值电压。加陷阱后**必须重跑未加陷阱的基线**做对照，否则无法区分"陷阱效应"和"收敛路径变了"。

---

## 6. `contact`：电极边界条件

```silvaco
contact name=source
contact name=drain
contact name=gate       workfunc=5.23
contact name=fieldplate workfunc=5.23 common=gate short
contact name=substrate
```

> 官方例子里常见的 `workf=5.23` 是 `workfunc=` 的合法前缀缩写，两者等价；本文统一写全称，理由见下表。

| 字段 | 含义 | 状态 |
|---|---|---|
| `name=` | 对应 `electrode`/DevEdit 里定义的电极名 | 已核实：atlas.key:4590 `name CHAR 1`（contact 卡 4460–4605） |
| `workfunc=`（可缩写 `workf=`） | 金属功函数（eV），决定肖特基势垒/MOS 平带电压 | 已核实：atlas.key:4462 `workfunc NUM 2 -999`。**`workf` 在 contact 卡上没有自己的行**，它只是 `workfunc` 的唯一前缀缩写（atlas.key:1962 那条 `workf` 属于 **material 卡**，是另一个参数）。缩写可用（官方例子 `CONTACT name=gate workf=4.5`），但推荐写全 `workfunc=`，这样才 grep 得到 |
| `common=<另一电极>` | **把本电极的偏压锁定到另一电极**（不是合并成一个节点） | 已核实：atlas.key:4593 `common CHAR 3`。manual 原文 "Although the electrodes are linked, separate currents will be saved for both electrodes unless SHORT is also specified. The electrode refered to in NAME should not appear on any SOLVE statments"。即：`common` 只联动偏压，**电流仍分两路统计** |
| `short` | 与 `common` 配合，**把两电极的电流合并为一路**写入 `.log` / 运行输出 | 已核实：atlas.key:4538 `short LOG 15 f`。manual 原文 "the two electrodes will be treated as one and only one value will be written to log files and in the run time output"。"只剩一个可加压端子"这件事 `common` 单独就做到了，`short` 管的是日志里的电流合并 |
| 不写任何字段 | 欧姆接触（默认） | 已核实（语义）：manual "An electrode in contact with semiconductor material is assumed by default to be ohmic. If a work function is defined, the electrode is treated as a Schottky contact."；另 "If you don't specify a work function, the contacts will be Ohmic regardless of its material."。contact 卡上没有裸 `ohmic` 关键字（只有 `auto.ohmic` LOG，atlas.key:4547），所以这是默认行为而非可写字段 |
| `neutral` / `surf.rec` / `barrier` / `resist=` / `current` | 中性接触、表面复合、势垒降低、串联电阻、恒流驱动 | 候选，用前在 examples/atlas.key 核对 |

规则：
- **电极名和 region 名不要重名**，否则后续 `contact` / `probe` / `extract` 的作用对象容易指错。
- 场板与栅短接写 `common=gate short`。**（已纠错）**旧版本这里写的是"漏 `short` 会留下一个可独立加压的浮空端子，静态工作点会与预期不符"——这是**错的**：按 manual，`common=` 本身就已经把该电极的偏压绑定到目标电极、并禁止它出现在 `solve` 语句里；漏写 `short` 的唯一后果是 `.log` 里出现**两路分开的电流**而不是合并的一路，静态工作点不受影响。要按"一个端子一路电流"解析 `.log`（例如场板+栅的合并电流）时才必须补 `short`。
- `workfunc` 改了就是新的器件。BV 结论不能跨 `workfunc` 引用。

---

## 7. `thermcontact`：热边界（开 `lat.temp` 时必配）

```silvaco
thermcontact number=1 elec.number=1 ext.temper=300
thermcontact number=2 elec.number=2 ext.temper=300
thermcontact number=3 x.min=0.0 x.max=24.0 \
             y.min=0.50 y.max=0.50 ext.temper=300 alpha=200
```

| 字段 | 含义 | 状态 |
|---|---|---|
| `number=`（可缩写 `num=`） | 热接触编号 | 已核实：atlas.key:7597 `number NUM 1`（thermcontact 卡 7593–7614）。manual 补充两条硬约束：**编号范围 1–20，且必须按递增顺序给；每条 `thermcontact` 都必须写 `number`** |
| `elec.number=`（可写 `elec.num=` / `elec=`） | 把热接触绑到第 N 号电极（源/漏金属散热） | 已核实：atlas.key:7605 `elec.number NUM 8 0`。**atlas.key 里没有 `elec.num` 这一字面行**，它是唯一前缀缩写；manual 与官方 deck 两种写法都用（`THERMCONTACT NUM=1 ELEC.NUM=3 TEMP=400`） |
| `x.min/x.max/y.min/y.max` | 用几何盒定义热接触（如背面衬底面：`y.min=y.max`） | 已核实：atlas.key:7598/7599/7600/7601。3D 另有 `z.min`/`z.max`（7606/7607）。缺省值为器件对应边界，单位 µm |
| `ext.temper=` | 外部环境温度（K） | 已核实：atlas.key:7603 `ext.temper NUM 7 300`。**`temperature`/`temper`/`temp` 与它共用内部索引 7，是完全等价的别名**（atlas.key:7604），所以别人 deck 里的 `TEMP=300` / `temperat=300` / `ext.temp=300` 指的是同一个量 |
| `alpha=` | 界面换热系数，**单位 W/(cm²·K)**；`alpha = 1/Rth`。不给 `alpha` = 理想等温（Dirichlet 定温）边界 | 已核实：atlas.key:7602 `alpha NUM 6 0`；单位见 manual Table 8-8 `THERMCONTACT ALPHA W/(cm2K)`（该表默认值单元格是 ∞ 符号，pdftotext 会丢字形）。语义见 manual §8.2.9："Equation 8-32 is used if a value is specified for α. Otherwise, Equation 8-31 is used"，而 Eq 8-31 就是 `T_L = TEMPER` 的定温条件 |
| `stefan=` / `blackbody` | 黑体辐射散热项（Eq 8-34）。`stefan` 默认 5.67051e-12 W/(cm²·K⁴)，非理想发射体就调它当发射率用 | 已核实：均在 thermcontact 卡（atlas.key 7593–7614），全文件唯一出处 |
| `beta=` | **边界热容项**（Eq 8-35，单位 J·cm⁻²·K⁻¹），不是黑体参数 | 已核实：atlas.key:7609 `beta NUM ... 0.0`；manual Table 8-8 给单位。总热流 Eq 8-36 = `ALPHA(Tl−TEMPER) + BETA·dTl/dt + STEFAN(Tl⁴−TEMPER⁴)`。**SEB 这类 ns 级热脉冲里 `beta` 比 `blackbody` 更相关**，它决定边界层吸热的快慢 |
| `boundary`（默认 t）/ `modify` / `f.contemp=` | 边界作用位置开关 / 在两条 `solve` 之间改热边界 / 用 C 函数给出随时间变化的接触温度 | 已核实：atlas.key:7594 `boundary LOG ... t`、7596 `modify`、`f.contemp` 均在本卡。要点：器件**内部**的热接触必须写 `^boundary`，否则该接触被忽略；`modify` 只能改 BC 类型/数值，不能改几何 |

> **关于 `alpha=0` 的一个反直觉点**：atlas.key 里 `alpha` 的默认值literal 是 `0`，但那是"未给值"的哨兵，触发的是 Dirichlet 定温分支（= 理想散热）。若**显式**写 `alpha=0` 去理解成通量边界，按 `Rth = 1/ALPHA` 反而是 Rth→∞ 即**绝热**。结论：想要理想等温就**别写 `alpha`**，不要写 `alpha=0`。

规则：
- 开 `lat.temp` 却没定义任何 `thermcontact` = 器件绝热，温度会无界上升，`max.temp` 会被撞到，结果无物理意义。
- **热边界是 SEB 结论的第一敏感项**。`alpha` 和背面边界位置必须冻结并写进 `RUN_MANIFEST.md`，不同热边界的 SEB 阈值电压之间**禁止直接比较**。
- 等温对照跑（不开 `lat.temp`）永远值得先做一遍：先确认电学响应对，再引入热。

---

## 8. `method`：求解器候选项表（本文最需要谨慎的一节）

### 8.1 候选项

| 候选 | 写法 | 适用场景 | 典型失败征兆 |
|---|---|---|---|
| Gummel（解耦） | `method gummel` | 初始解、低偏压、弱耦合 | 高注入/强耦合时残差长期不降，迭代次数打满但不发散 |
| Newton（全耦合） | `method newton` | 常规静态 DC，中低偏压 | 初值差时直接发散；大电压步跳步失败 |
| **[默认·低压静态]** Gummel→Newton | `method gummel newton carriers=2` | 转移/输出特性、实验数据标定 | 高压强非线性区仍可能在某个电压点卡死 |
| **[默认·高压/自热]** Block Newton | `method block newton carriers=2` | BV 扫描、`lat.temp` 自热、SEB 瞬态 | 慢；`max.temp` 撞顶；网格差时在高场区反复减步 |
| 载流子数控制 | `carriers=2` / `carriers=1 elec` / `carriers=0` | 2=电子+空穴；1=单载流子；0=仅 Poisson | `carriers=0` 得不到电流，只能看电场/电位 |

取证情况：`newton`（默认 t）、`gummel`、`block`、`carriers`（atlas.key:729，默认 2）四个关键字均已核实在 METHOD 卡（atlas.key 643–961）。`block` 的语义有 manual 背书："Block method only has meaning when either lattice heating or energy balance is included in the simulation. For isothermal drift diffusion simulations, BLOCK is [ignored]"，且执行顺序为 "GUMMEL then BLOCK then NEWTON"——所以 `method block newton carriers=2` 是文档支持的组合。**但要注意**：本机 examples 里 grep 不到这一整行组合（`^ *method.*block.*newton` 零命中），它是"manual 支持、例子未见"，不是"从官方 deck 逐字抄来"。

### 8.2 修饰字段

| 字段 | 含义 | 使用建议 |
|---|---|---|
| `trap` | 不收敛时自动减小偏压/时间步重试 | 常开，但**不能靠它掩盖不稳定路径** |
| `maxtraps=` | 允许的自动减步（发散重试）次数 | 已核实：atlas.key:666 `maxtraps NUM ... 4`（默认 4）。**manual 明确写"The value of MAXTRAPS may range from 1 to 10"**，所以 `30` / `100` 超出文档范围——例子里出现这些值的 deck 全是 `GO victorydevice`，不是 ATLAS。本项目冻结值：BV/SEB `4`，标定 `6~10`，**上限按 10 封顶**。另注意：它与 deck 里的 `trap` 物理语句条数无关，纯粹是求解器重试计数 |
| `fail.quit` | 超过 `maxtraps` 后直接终止而不是硬撑 | **强烈建议常开**——它把"失败"变成明确终止串，便于自动化守候。<br>*未核实：本轮未对该关键字做 atlas.key 取证* |
| `climit=` | **求解器要分辨的最小载流子浓度（归一化量、无量纲），不是残差/收敛容差** | 已核实：atlas.key:688 `climit NUM 51 10000`（默认 **1e4**）。详见下方专段 |
| `clim.dd=` / `climit.dd=`（同义） | 同一物理量的 **cm⁻³ 版本**（`= CLIMIT × (Nc·Nv)^(1/4)`，**四次方根**，manual p.1122 Eq 20-2/20-3） | 已核实（manual）：p.1417 METHOD 参数表**同时列出** `CLIM.DD` 与 `CLIMIT.DD`（均 Real、默认 4.5e13 cm⁻³）；p.1426 原文 "CLIMIT.DD — This is an alias for CLIM.DD"——**两个拼写在手册层面都合法**，旧版"`clim.dd` 照 manual 抄会写错"的警告不成立，已作废。atlas.key 的登记名与行号（包内旧记录 :725 `clim.dd` 与 :726 `climit.dd`；manual 两拼写并列为两个参数，这两行可能同时存在、各登记一个拼写，归属待查）**[待 atlas.key 复核]**。想直接按 cm⁻³ 设定就用它（Si 默认 ≈4.5e13 cm⁻³，manual p.1122 建议击穿仿真降到 ~1e8 cm⁻³） |
| `itlimit=` | 单个偏压点最大迭代次数 | 已核实：atlas.key:644 `itlimit`（默认 25）。本项目：BV `25`，标定 `35~50`，历史 `150` 不推荐 |
| `max.temp=` | `lat.temp` 求解的晶格温度上限（K） | 已核实：atlas.key METHOD 卡，**默认 2000.0 K**。本项目冻结 `5000`（高于默认 = 放宽）；撞顶说明热边界或网格有问题，不要盲目调大。⚠️ 写 `max.temp=1000` 是**收紧**而非放宽，别在 SEB deck 里误用 |
| `min.temp=` | `lat.temp` 求解的晶格温度下限（K） | 已核实：atlas.key METHOD 卡，默认 120.0 K。manual："should be set to suitably low temperature when doing cryogenic simulations" —— **300 K 常温 SEB deck 不需要动它**，看到 `min.temp=3.0` 那是低温 deck 抄来的 |
| `dt.min=` | 瞬态最小时间步 | 已核实：atlas.key:665（METHOD，默认 -999 = 自动）。**同名参数在 `solve` 卡上也存在**（atlas.key:3504，默认 1e-15），两处都能写。SEU/SET 瞬态冻结 `1.0e-18` |
| `dt.max=` | 瞬态最大时间步 | 已核实：atlas.key:714 `dt.max`，缺省 1.0e10（manual p.1417 METHOD 表同：DT.MAX 默认 1.0×10¹⁰ s）。内部槽位号本文旧记 NUM 74 与 `wbg-radiation-and-seb.md` §8.2 的 NUM 72 互斥，**[待 atlas.key 复核]**。**只在 `method` 上有，`solve` 卡上没有** |
| `seu.integrate` | SEU 源在时间步内做积分而非取样 | 已核实：atlas.key METHOD 卡。与 `singleeventupset` 配合 |
| `bicgst` / `pam.bicgst` / `pam.gmres` | 切换线性求解器 | 已核实存在：atlas.key:851 `bicgst`、930 `pam.bicgst`、`pam.gmres`，均在 METHOD 卡（643–961）。manual："ILUCGS ... is the default iterative solver in 3D"，`bicgst` 是从它切走的第一候选 |
| `block.tran` | 瞬态使用 block 求解 | 高压/自热瞬态配 `block newton` 使用。<br>*未核实：本轮未对该关键字做 atlas.key 取证，写进正式 deck 前先 grep* |
| `lte2step` | 瞬态局部截断误差的另一种评估方式 | 已核实：atlas.key:904 `lte2step LOG 101 f`。⚠️ **注意不存在 `lte.timestep` 这个参数**（atlas.key 零命中），网上/别人 deck 里出现的那个写法是 Victory Device 语法。ATLAS 默认就用 LTE 自适应步长，通常什么都不用写 |

> ### ★ `climit` 的正确理解（本节最容易被讲反的一条）
>
> **atlas.key 原始行**：`   climit       NUM     51      10000` —— 默认值是 **1e4**。
>
> 三个必须记住的事实：
> 1. **它不是残差容差。** manual 原文："CLIMIT or CLIM.DD specify minimal values of concentrations to be resolved by the solver." 它进入 X-norm（载流子浓度更新量的归一化），设定求解器**愿意去分辨的最低浓度**。任何"climit 越小 = 收敛判据越严"的说法都是错的，必须改掉。
> 2. **它是无量纲的（归一化量）。** 带 cm⁻³ 单位的是另一个参数 `CLIM.DD`，同义别名 `CLIMIT.DD`（manual p.1426 原文 "CLIMIT.DD — This is an alias for CLIM.DD"；p.1417 参数表两拼写并列，均默认 4.5e13 cm⁻³；atlas.key 登记名/行号 [待 atlas.key 复核]）。换算是**四次方根**：`CLIM.DD = CLIMIT × (Nc·Nv)^(1/4)`（manual p.1122 Eq 20-2/20-3，`c* = ⁴√(Nc·Nv)`；自检：1e4 × (2.8e19×1.04e19)^(1/4) ≈ 4.1e13 ≈ Si 默认 4.5e13 ✓，写成 `4·sqrt(...)` 差 10 个量级）。所以**不要写"climit 单位 cm⁻³"**；要写 cm⁻³ 就换用 `clim.dd`/`climit.dd`。
> 3. **`climit=1e-4` 是 manual 亲自推荐的击穿设置，不是隐患。** 原文："A value of CLIMIT=1e-4 is recommended for all simulations of breakdown, where the pre-breakdown current is small."，并直接给出 `METHOD CLIMIT=1e-4` 作为范例；反过来**不调低**才会得到 "false solution"。官方 examples 里 `climit=1e-4` 出现 85 次（远端全量树计数 [待复核]；本地镜像 `d:\knowledge\exp25` 实测 79 次）、`climit=1.0e-4` 11 次、`climit=1e-5` 10 次，是整个例子库里最常见的取值。
>
> 一句话：调小 `climit` = 让求解器去分辨更低的载流子浓度（击穿/低漏电场景必需），**不是**"收紧收敛容差"。本项目冻结 `climit=1.0e-4` 的做法本身没问题，需要改的只是描述口径。

### 8.3 三条已冻结的正式配置（逐字引用）

**低压静态标定 / 低压 SET 前置**

```silvaco
method gummel newton carriers=2 trap maxtraps=10 fail.quit \
       climit=1e-4 itlimit=50
```

**高压反向击穿 BV（自热开启）**

```silvaco
method block newton carriers=2 trap maxtraps=4 fail.quit \
       climit=1.0e-4 itlimit=25 max.temp=5000
```

**高压 SEB 瞬态（自热 + SEU 注入）**

```silvaco
method block newton carriers=2 trap maxtraps=4 fail.quit \
       climit=1.0e-4 itlimit=25 max.temp=5000 \
       dt.min=1.0e-18 seu.integrate block.tran
```

> **纪律（每个求解器配置块都适用）：不同任务（低压 SET / 高压 BV / 高压 SEB）的 `method` 行禁止凭印象串用。**
> 要用哪一条，就从对应的正式 deck 里**逐字复制**，并把该行原文连同来源 deck 路径与 SHA-256 写进本次运行的 `RUN_MANIFEST.md`。
> 记忆里"大概是 block newton carriers=2 加个 maxtraps"这种复述，等于换了求解器，结果不具可比性。

低压 SET deck 里在注入 SEU 后同样要切到 `block newton ... seu.integrate block.tran`——**切换点也必须冻结**：在哪一条 `solve` 之前切、切之前是否已 `save`，都写进 manifest。

---

## 9. `solve`：渐进偏压策略

核心原则：**永远从 `solve init` 出发，用明确的小步进爬到目标偏压，不依赖求解器自动找路。**

```silvaco
solve init
solve vgate=-0.05 name=gate
solve vgate=-0.10 name=gate
solve vgate=-0.20 name=gate
solve vgate=-0.50 name=gate
solve vgate=-0.75 name=gate
solve vgate=-1.00 name=gate
solve vstep=-0.25 vfinal=-5.00  name=gate previous
solve vstep=-0.05 vfinal=-20.00 name=gate previous
save outf="<case>_prebias.str"
```

漏极高压扫描（BV）：

```silvaco
log outf="<case>.log"
solve prev
solve vdrain=0.01 name=drain previous
solve vdrain=0.10 name=drain previous
solve vdrain=0.50 name=drain previous
solve vdrain=1.0 vstep=1.0 vfinal=10.0 name=drain previous
solve vstep=5.0 vfinal=$bvfinal name=drain previous \
      compliance=0.1 cname=drain
log off
```

| 字段 | 含义 | 要点 |
|---|---|---|
| `solve init` | 求初始平衡解 | 必须是第一条 solve |
| `v<电极名>=` | 直接指定该电极偏压 | 头几步用绝对小值手写，比 `vstep` 稳 |
| `vstep=` / `vfinal=` | 步进值 / 终点 | 越接近击穿越要减小 `vstep` |
| `name=` | 被扫描的电极名 | 必须与 `contact name=` 一致 |
| `previous`（`prev`） | 用上一步收敛解作初值，而非外推 | 已核实：atlas.key:3075 `previous LOG 2 f`（solve 卡 3073–4459；另有 65 行的同名参数属 **mesh 卡**，别看混）。`prev` 在 atlas.key 里**没有独立行**，是 `previous` 的唯一前缀缩写，manual 与官方 deck 大量使用（`SOLVE PREV`）。<br>**可重复性的关键**；本项目已验证：加 `previous` 后两次冷启动结果逐字节一致 |
| `compliance=`（可缩写 `compl=`）+ `cname=` | 对某电极限流 | 已核实：atlas.key solve 卡 `compliance NUM 36` + `cname`。`compl` 无独立行，是前缀缩写；本文写全称。BV 扫描必备，避免击穿后电流发散撑爆求解 |
| `tfinal=` / `tstep=` | 瞬态终点 / 时间步 | 已核实：atlas.key:3268 `tfinal`、3264 `tstep`（均在 solve 卡）。用法见 §13 |

规则：
- 结构名里的电压是**目标**，不是成果。`.str` 里存的才是实际收敛到的最后一个偏压；报告 BV 时必须从 `.log`/`.str` 读实际值。
- 强非线性区卡住时的第一手段是**减小 `vstep`**，不是加大 `maxtraps`。
- 栅预偏置和漏扫描要分成两段 log（见 §11），否则 I-V 曲线会把预偏置段也画进去。

---

## 10. `save` / `load ... master`：checkpoint 与已知坑

```silvaco
save outf="<case>_prebias.str"                 # 写出结构 + 当前解
load infile="<case>_prebias.str" master        # 重新载入为"可继续求解"的状态
```

| 用法 | 效果 |
|---|---|
| `save outf="*.str"` | 结构 + 解快照。TonyPlot 可直接看 |
| `load infile="*.str" master` | 载入**主结构与解状态**，可继续 `solve` |
| `load infile="*.str"`（不带 `master`） | 只作显示/几何用途，不保证能继续求解 |

**`master` 关键字不能省。** 少写它，后续 `solve` 可能从一个不完整的状态起步，收敛路径与原 run 不同，可重复性直接失效。

### 已知坑（本环境实测）

1. **DevEdit 非结构化网格的 master checkpoint 在 ATLAS 5.40 重载会报 G-record read error。**
   对策：DevEdit 重划分过的结构，**不要跨阶段 reload master**；把预偏置和瞬态放在同一次 ATLAS 会话里，用内存中已收敛的状态直接往下 `solve`。checkpoint 仍然照常 `save`，但只作证据/可视化，不作续跑入口。
2. ATLAS 内建矩形网格建的结构，`load ... master` 工作正常，是首选的"每次从同一预偏置起跑"手段。
3. `probe` 语句要在**载入 checkpoint 之后**定义；本项目已确认插入探针本身不改变收敛结果，但定义顺序要固定，否则 log 列顺序会变，下游解析脚本会错位。
4. checkpoint 文件很大。运行期留在 `/root/DECKBUILD/<run>/`，结束后归档到 `E:\silvaco2425\bulk\str\`，不要写进 `/mnt/hgfs/*`（HGFS 共享目录已 98% 满）。

---

## 11. `log`：分段曲线日志

```silvaco
log outf="<case>_dark.log"
solve prev
... 漏极扫描 ...
log off

log outf="<case>_transient.log"
... 瞬态 ...
log off
```

规则：
- **每个物理阶段一个 `.log`**：预偏置、静态暗态、瞬态各自独立。对应源技能里 `NewCurrentFile/Prefix` 的作用。
- `log off` 必须成对出现。漏写会把下一阶段的数据续写进上一个文件，`extract` 出来的曲线是两段拼接的，极易误判。
- 不需要曲线的段（例如纯粹为了推进偏压的爬坡）就别开 log，能显著减小文件。
- `extract` 从 log 取曲线：

```silvaco
extract init inf="<case>_transient.log"
extract name="<case>_Id_t" curve(time, i."drain") outfile="<case>_Id_t.dat"
```

`.dat` 是轻量文本，可以回传主控端做 Python 出图；`.log` 本体归档到 `E:\silvaco2425\bulk\log\`。

---

## 12. `output`：`.str` 中保存哪些场

`output` 决定 `save outf=` 写进 `.str` 的空间场。**保存不足 = 事后无法诊断，只能重跑。**

已核实可用字段（OUTPUT 卡 = atlas.key 7337–7506）：

```silvaco
output flowlines ex.velocity ey.velocity e.mobility h.mobility \
       band.param band.temp e.field impact photogen l.temper
output con.band val.band e.field impact flowlines l.temper
```

> **（已纠错）**本段旧版写的是 `ex.velo` / `ey.velo`。atlas.key 里**没有这两个字面行**（`grep '^ *(ex\.velo|ey\.velo) '` 退出码 1、零输出），正确关键字是 `ex.velocity`（atlas.key:7371）/ `ey.velocity`（7372）。缩写形式在 manual 正文里确实出现过（`OUTPUT FLOWLINES EX.VELO EY.VELO`），靠唯一前缀能解析，但**官方例子一律写全称**（`OUTPUT e.velocity ex.velocity`，8 次 `ex.velocity` / 2 次 `ey.velocity`，缩写 0 次）。本文统一写全称，这样才 grep 得到。

| 字段 | 内容 | 状态 |
|---|---|---|
| `e.field` | 电场（模）。**分量另有独立开关** `ex.field` / `ey.field` / `ez.field` | 已核实：atlas.key:7339 `e.field LOG 2 t`（别名 `efield` 同索引，7340）；分量 7341/7342，索引 3/4/52，**四者默认全为 t**，所以只写 `e.field` 实际也会得到分量 |
| `flowlines` | 电流流线 | 已核实：atlas.key:7369 `flowlines LOG 30 f`（**默认 f，必须显式写**） |
| `impact` | 碰撞电离产生率 | 已核实：atlas.key:7345 `impact LOG 7 t`（默认已开）。⚠️ 与 `impact` **语句**（atlas.key:5367）同名不同物，评审时别看混——同 §5 对 `trap` 的提醒 |
| `photogen` | 光生/SEU 生成率（看离子径迹必需） | 已核实：atlas.key:7363 `photogen LOG 25 t`（默认已开） |
| `l.temper` | 晶格温度 | 已核实：atlas.key:7383 `l.temper LOG 44 t`。**默认就是 t**，开 `lat.temp`（models 卡，atlas.key:1019）时不写也会存；显式写只是留痕 |
| `con.band` / `val.band` | 导带/价带边 | 已核实：atlas.key:7376 `con.band LOG 37 f` / 7375 `val.band LOG 36 f`（默认均 f） |
| `band.param` | 能带参数：Eg、ni、Nc、Nv、χ | 已核实：atlas.key:7385 `band.param LOG 46 f`；manual 逐项列出上述五个量 |
| `band.temp` | **温度相关的能带参数**（Eg、Nc、Nv、Ec、Ev、sqrt(n·p)） | 已核实：atlas.key:7424 `band.temp LOG 81 f`。**（已纠错）**旧描述"能带温度相关量"易被误读成"能带温度"；manual 明确它输出的是上述六个随温度变化的能带量，没有任何"温度"场 |
| `ex.velocity` / `ey.velocity` | **电子**速度分量（不是"载流子"）；空穴分量是 `hx.velocity` / `hy.velocity` | 已核实：atlas.key:7371 `ex.velocity LOG 32 f` / 7372 `ey.velocity LOG 33 f`（空穴对应 7373/7374，索引 34/35）。**（已纠错）**旧写法 `ex.velo`/`ey.velo` 及"载流子速度分量"的说法见上方纠错框 |
| `e.mobility` / `h.mobility` | 电子/空穴迁移率场 | 已核实：atlas.key:7343 `e.mobility LOG 5 f` / 7344 `h.mobility LOG 6 f` |
| `qfn` / `qfp` | 电子/空穴准费米能级 | 候选，需核对 |
| `charge` / `recomb` / `traps` | 空间电荷 / 净复合 / 陷阱占据 | 候选，需核对 |
| `j.electron` / `j.hole` / `j.total` | 电流密度分量 | 候选，需核对 |

诊断优先级（对应源技能的分层诊断）：
1. `.out` 运行日志 → 成功/失败、卡在哪个偏压或时刻；
2. `.log`/`.dat` 曲线 → 宏观现象（I-V 是否击穿、Id(t) 是否恢复）；
3. `.str` 空间场 → 根因位置（高场点、电流路径、温度热点、雪崩/径迹分布）。

**只看曲线不看 `.str` 不能下物理结论。**

---

## 13. 瞬态求解

### 13.1 时间推进语法候选项

| 候选 | 写法 | 说明 |
|---|---|---|
| **[默认]** 分段终点式 | `solve tfinal=<t_end> tstep=<dt>` | 已核实：`tfinal` atlas.key:3268、`tstep` atlas.key:3264（均在 solve 卡）。本项目全部瞬态 deck 冻结用法：一行推进到一个时间里程碑，然后 `save` |
| 终点+固定步长式 | `solve tstop=<t_end> dt=<dt> prev` | `tstop`/`dt`/`prev` 本项目 ATLAS 实测可用；同形写法见官方例子 `Rad_Rel_ex02.in:77` `SOLVE tstop=1e-12 dt=1e-13 prev`（本地镜像 `d:\knowledge\exp25\Radiation_and_Reliability\`；⚠ 该 deck 是 Victory Device，仅作形态参照，参数以本项目实测为准）。⚠ **`solve tstart=` 已证伪**：本项目实测报 `Invalid parameter ==> tstart`，SOLVE 卡上没有它，见下方留档框 |
| 步长上下限 | 追加 `dt.min=` / `dt.max=`（写在 `method` 上） | 两者均**已核实**：`dt.min` atlas.key:665（method，默认 -999=自动；solve 卡 3504 也有，默认 1e-15）、`dt.max` atlas.key:714（**method 卡，默认 1.0e10**）。⚠️ `dt.max` 在 solve 卡上**没有**，只能写在 `method` 行 |

> **不存在的写法（曾被误用，特此留档）**：`constant.timestep` 和 `lte.timestep` 在 ATLAS 5.40.0.R 的 atlas.key 里**零命中**（全文件 `timestep` 只有 solve 卡 3263 一行，是 `tstep` 的别名槽）。两者的来源是 `Rad_Rel_ex01.in` 这类 `GO victorydevice` 的 Victory Device deck，**语法不通用**。要固定密采样就写 `method dt.min=<x> dt.max=<x>`；要自适应就什么都不写（ATLAS 默认即 LTE 自适应步长），或用真实存在的 `lte2step`（atlas.key:904）。另：**`solve tstart=` 同属不存在的写法**——本项目 ATLAS 实测报 `Invalid parameter ==> tstart`；瞬态起点无需指定（从当前解的时刻继续推进），终点用 `tstop=` 或 `tfinal=`。

### 13.2 典型 SEU/SEB 瞬态推进

```silvaco
log outf="<case>_transient.log"
solve tfinal=1.0e-13 tstep=1.0e-14
solve tfinal=1.0e-12 tstep=5.0e-14
solve tfinal=4.0e-12 tstep=1.0e-13
save outf="<case>_t4ps.str"
solve tfinal=1.0e-11 tstep=2.0e-13
solve tfinal=5.0e-11 tstep=1.0e-12
solve tfinal=1.0e-10 tstep=2.0e-12
save outf="<case>_t100ps.str"
solve tfinal=2.0e-10 tstep=2.0e-12
save outf="<case>_t200ps.str"
solve tfinal=1.0e-9  tstep=1.0e-11
solve tfinal=1.0e-8  tstep=1.0e-10
solve tfinal=1.0e-7  tstep=1.0e-9
save outf="<case>_t100ns.str"
solve tfinal=1.0e-6  tstep=1.0e-8
save outf="<case>_t1us.str"
log off
```

要点：
- **时间步必须跟着物理时标走**：离子脉冲宽度（如 `tc=2 ps`）附近用 `tstep ≤ 1e-13`，进入 ns/µs 恢复段再放宽。全程用同一个粗步 = 把脉冲抹平，Id(t) 峰值失真。
- 每个数量级至少 `save` 一个 `.str`。SEB 的判据（电流是否持续上升、温度热点位置）只能从这些快照读。
- 瞬态开始前必须先建立并确认**暗态**：单独一段 log 记录静态偏压点，确认 `|Id_dark|` 和峰值电场在预期范围内，再注入离子。
- SEU 注入语句的两个候选：

| 候选 | 写法 | 说明 |
|---|---|---|
| **[默认·可复现]** 内建高斯径迹 | `singleeventupset entrypoint="15.0,0.0,0" exitpoint="15.0,0.5,0" radius=0.05 b.density=0.06 pcunits radialgauss t0=4.0e-12 tc=2.0e-12` | 已核实：`entrypoint`/`exitpoint`/`radius`/`density`/`b.density`/`pcunits`/`radialgauss`/`t0`/`tc` 全部在 SINGLEEVENTUPSET 卡（atlas.key 7999–8025）。单位口径：**`b.density` + `pcunits` = pC/µm；不写 `pcunits` 的 `density=` 是 cm⁻³**，两者不可混。参数全在 deck 里，可逐字冻结 |
| 自定义 C 时空分布 | `singleeventupset f.seu=<file>.c` | 已核实：`f.seu` 在 SEU 卡上。灵活，但 `.c` 文件本身也必须冻结并记 SHA-256；其内部标度的物理单位若无文档，**禁止在报告里标称 LET 数值** |

> SEU 卡上还有 `beam.radius` / `a1..a4` / `b1..b4` / `tfinal.seu` / `rescale` / `radialsin2` / `uniform` / `device`(=`structure`)：**关键字均已核实存在**（atlas.key 7999–8025），但**用法未核实**——本机 examples 里没有任何 deck 用过它们，写进正式 deck 前必须查 manual。另：`b.time` **确实不存在**（atlas.key 零命中），这条否定判断是对的。

---

## 14. 终止状态与收敛诊断

守候运行结束时，`.out` 里的终止串有多种候选，**不要只 grep 一个**：

| 候选终止串 | 含义 |
|---|---|
| 进程退出码 0 + deck 末尾 `quit` 已执行 | 正常结束 |
| `ATLAS DIED` | 求解器异常终止 |
| `Convergence failure` / `solution did not converge` | 收敛失败 |
| `fail.quit` 触发导致提前终止 | 减步次数超限，属预期内的"明确失败" |
| `License` 相关报错 | SFLM 问题，不是物理问题（先查 `SFLM_SERVERS=+localhost`、`sflm_monitord`） |

不要用 `grep "Error"` 做终止判据（正常收敛信息里也含该词），也不要用 `pgrep atlas` 判断完成（并行 run 同名进程会混淆）。

### 常见症状 → 优先修正

| 症状 | 优先修正 |
|---|---|
| `solve init` 就不收敛 | 查结构：region/electrode/doping 是否完整，接触是否落在正确材料上；先 `carriers=0` 只解 Poisson 定位 |
| 栅预偏置爬不上去 | 手写更多小绝对值偏压点，`vstep` 减半，全部加 `previous` |
| 漏极高压卡在固定电压 | 减小 `vstep`；检查该电压下 `.str` 的电场峰值位置与网格密度；确认 `compliance` 未过早触发 |
| BV 数值随网格变化大 | `impact` 区域网格不足；先做网格收敛性扫描再谈 BV 数值 |
| 开 `lat.temp` 后撞 `max.temp` | 热边界缺失或 `alpha` 不合理，不要直接调大 `max.temp` |
| 瞬态在脉冲期反复减步 | `tstep` 相对 `tc` 太大；`dt.min` 太大；确认 `seu.integrate block.tran` 已加 |
| 两次冷启动结果不一致 | 检查是否漏了 `previous`、是否漏了 `master`、`simflags` 是否两段都锁了 `-V 5.40.0.R -P 4` |
| 结果"莫名其妙变好/变坏" | 先 diff deck 与上一次 run 的 `RUN_MANIFEST.md`，八成是 `models`/`method`/材料参数被无意改动 |

**两次失败规则**：同一类失败最多盲试两次。第二次仍失败就停下，回到 `$SILVACO/examples`、manual 和文献做根因分析，把结论写进 `findings.md`。

---

## 15. 本节的强制留痕

每次运行的 `RUN_MANIFEST.md` 里，物理与求解器部分至少要有：

- deck 路径 + SHA-256；
- `simflags` 原文（版本与并行度）；
- `material` / `mobility` / `impact` / `trap` 各行原文及参数来源（文献或例子）；
- `models` 行原文；
- **每一条 `method` 行原文**，以及它是从哪个正式 deck 逐字复制来的；
- 偏压推进序列（含 `vstep`/`vfinal`/`compliance`）；
- 瞬态时间分段与每段 `tstep`；
- checkpoint 策略（`load ... master` 还是内存续算，以及为什么）；
- `.str` / `.log` 的最终归档路径（`E:\silvaco2425\bulk\{str,log}\`）。

缺任何一项，这次 run 的结论都不能与其他 run 横向比较。
