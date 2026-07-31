# Silvaco 结构与网格模式

本文件说明在 Silvaco TCAD 中建立器件结构、划分网格、绑定材料/掺杂/电极的三条可选路径、各自的字段写法与陷阱，以及**每次改结构后必须执行的坐标审计**。

---

## 0. 建结构的候选路径 (最重要的一次选择)

Silvaco 没有单一的结构编辑器。下表是三条正式路径，按本项目默认程度排序。**不要默认只用一条；先按判据表选，再在 deck 头部注释里写清选了哪条、为什么。**

| 路径 | 入口语句 | 适用 | 不适用 | 标记 |
|---|---|---|---|---|
| **A. ATLAS 内建网格** | `go atlas` → `mesh` / `x.mesh` / `y.mesh` / `region` / `electrode` / `doping` | 矩形层叠器件、线电极、平面 MOS/HEMT/二极管、快速探索 | 任意多边形、圆角、斜坡、有厚度场板 | **[默认]** |
| **B. DevEdit** | `go devedit` → `init infile=` / `region ... polygon=` / `constr.mesh` / `mesh mode=meshbuild` / `structure outf=` | 任意多边形、有厚度场板、倒角/圆角、局部三角形重划分、需要零钝角三角形的高场结构 | 只是加一层平板（用 A 更省事、更可重复） | 多边形几何时用 |
| **C. Athena 工艺仿真** | `go athena` → 工艺语句 → `structure outf=` | 结构来自真实工艺流程（注入/扩散/氧化/刻蚀），需要工艺-器件联动 | 只想要一个理想几何做物理研究 | 有工艺卡时用 |
| C′. Victory Process (3D) | `go victoryprocess`（具体语句需在 examples 或 manual 中核对） | 3D 工艺 | 2D 项目 | 仅 3D |
| B′. Victory Device (3D 求解) | 3D 结构的电学求解 | 3D | 2D 项目 | 仅 3D |

### 选择判据

1. 器件能被一组轴对齐矩形完整描述 → **A**。
2. 出现任何非轴对齐边、圆角、有厚度金属体、斜坡台面 → **B**（通常是 **A 建 base + B 加多边形**，见 §4）。
3. 用户给的是工艺流程而不是几何尺寸 → **C**，产物 `.str` 再交给 ATLAS。
4. 需要 3D → C′/B′，并先与用户确认机时预算（本机 8 vCPU / 8 GB RAM，3D 极易 OOM）。

> 已验证的经验（本项目 β-Ga₂O₃ 场板 MOSFET）：**无厚度线电极（路径 A）是当前基准**。曾测试的有厚度场板（路径 B 多边形）在错误位置形成高场峰，且漏极电压没有加载到目标值。所以从 A 换到 B 时，几何变了 = 物理变了，必须重跑 BV/暗态基线再对比，不能直接沿用旧结论。

---

## 1. 坐标系与单位约定

- 2D 平面为 `x`（横向）与 `y`（纵向），单位 **µm**。
- **ATLAS 的 `y` 向下为正**：习惯把器件表面（半导体最上界面）取作 `y = 0`；`y < 0` 是表面之上的介质/钝化/金属/空气，`y > 0` 进入外延层与衬底。
- `mesh width=<µm>` 设定第三维宽度；ATLAS log 中电流按每 µm 器件宽度输出（换算到 A/mm 乘 1e3）。**每个新项目在第一份 log 的表头处核对一次单位**，不要凭记忆换算。
- 3D 增加 `z.mesh`（字段与 `x.mesh` 同构，具体用法需在 examples 中核对）。
- 所有坐标只用绝对值写死在 deck 里，或用 `set` 变量派生；**不要在 deck 里写相对偏移的算术表达式而不留注释**，否则坐标审计无法复核。

> **权威路径（`$SILVACO` 在本机 tcad 上登录后默认为空——先 `export SILVACO=/atctools/Synopsys/Silvaco2024` 再用该变量；未 export 时一律写下面的绝对路径。口径与本包其它文件"先 export 再用"一致）**
> - 关键字表：`/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key`
> - 示例 deck：`/atctools/Synopsys/Silvaco2024/examples/deckbuild/5.2.40.R/`（另有 `5.2.29.R/`）
> - ATLAS 手册：`/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/docs/atlas_users1.pdf`（`pdftotext` 可用）
> - DevEdit 手册：`/atctools/Synopsys/Silvaco2024/lib/devedit/help/DevEdit.pdf`
>
> **本文件的标注规则**：`[已核实: …]` 只用于**当场能贴出 grep 输出**的条目；查不到就写 `[未核实：…]` 并保留内容，
> 不删除。另外，示例 deck 用之前必须先看它的引擎：`grep -iE '^ *go ' <deck>.in` —— 本机很多 `Rad_Rel_*` /
> `GaN_Power_*` / `Other_Power_*` 例子是 `go victorydevice`（Victory Device），**语法与 ATLAS 不通用**，
> 直接照抄会引入 ATLAS 里根本不存在的关键字。

---

## 2. 路径 A：ATLAS 内建网格

### 骨架（已在本项目 5.40.0.R + `-P 4` 下验证）

```silvaco
go atlas simflags="-V 5.40.0.R -P 4"

mesh width=1.0

x.mesh loc=0.0   spac=0.80
x.mesh loc=2.0   spac=0.40
x.mesh loc=11.0  spac=0.20
x.mesh loc=13.0  spac=0.10
x.mesh loc=15.0  spac=0.020
x.mesh loc=22.0  spac=0.40
x.mesh loc=24.0  spac=0.80

y.mesh loc=-1.42 spac=0.20
y.mesh loc=-0.42 spac=0.020
y.mesh loc=-0.02 spac=0.004
y.mesh loc=0.00  spac=0.004
y.mesh loc=0.30  spac=0.020
y.mesh loc=0.50  spac=0.050

region num=1 name=ambient_air            material=air   x.min=0.0 x.max=24.0 y.min=-1.42 y.max=-0.42
region num=2 name=epilayer               user.material=BetaGa2O3 x.min=0.0 x.max=24.0 y.min=0.00 y.max=0.30
region num=3 name=substrate              user.material=BetaGa2O3 x.min=0.0 x.max=24.0 y.min=0.30 y.max=0.50
region num=4 name=Al2O3_gate_dielectric  material=Al2O3 x.min=0.0 x.max=24.0 y.min=-0.02 y.max=0.00
region num=5 name=SiO2_passivation       material=SiO2  x.min=0.0 x.max=24.0 y.min=-0.42 y.max=-0.02

electrode number=1 name=source x.min=0.0  x.max=2.0  y.min=0.00  y.max=0.00
electrode number=2 name=drain  x.min=22.0 x.max=24.0 y.min=0.00  y.max=0.00
electrode number=3 name=gate   x.min=11.0 x.max=13.0 y.min=-0.02 y.max=-0.02

doping region=2 n.type concentration=1.10e17 uniform
doping region=3 n.type concentration=1.15e16 uniform
doping gaussian n.type concentration=5.0e19 region=2 \
       x.min=0.0 x.max=2.0 y.min=0.00 y.max=0.15 y.char=0.020 direction=y

save outf="<case>_base.str"
```

### 字段说明

> 核实基准：`/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key`（ATLAS 5.40.0.R）。
> 行号即该文件的绝对行号，行格式为 `名字 类型 内部槽位 默认值`。
> **注意 atlas.key 登记的是截断名**（如 `concentr` / `directio` / `ratio.la`），deck 里写全称
> （`concentration=` / `direction=` / `ratio.lateral=`）同样解析；唯一前缀缩写（`loc` → `location`、
> `spac` → `spacing`、`inf`/`outf` → `infile`/`outfile`）也合法。

| 语句 | 已核实字段（附 atlas.key 证据） | 其它可用字段 / 未核实项 |
|---|---|---|
| `mesh` | `width=`（第三维宽度，µm）[已核实: atlas.key:44 `width NUM 3 1.0`] | `space.mult=`（全局疏密倍率，用于粗网格探索）[已核实: atlas.key:45 `space.mult NUM 4 1.0`]、`auto` [已核实: atlas.key:98 `auto LOG 25 f`]、3D 的 `three.d` [已核实: atlas.key:91 `three.d LOG 18 f`]、`inf=`（读回 `.str`）[已核实: atlas.key:112 `infile CHAR 1`] |
| `x.mesh` / `y.mesh` | `loc=`（坐标）、`spac=`（该处目标间距）[已核实: atlas.key:126 `location NUM 2` / atlas.key:130 `spacing NUM 4`，`loc`/`spac` 为唯一前缀缩写] | `n=`（按节点号定义的老写法）[已核实: atlas.key:125 `n NUM 1`，与 `node` 同槽]、`ratio=` [已核实: atlas.key:129 `ratio NUM 3 1.0`]。`y.mesh` 与 `x.mesh` 共用同一张参数表 [已核实: atlas.key:141 `y.mesh 6 5`] |
| `region` | `num=`、`name=`、`material=`、`user.material=`、`x.min/x.max/y.min/y.max` [已核实: atlas.key:144 `number NUM 1`、:325 `material CHAR 1`、:326 `name CHAR 2`、:327 `user.material CHAR 3`、:161–164 `x.min/x.max/y.min/y.max`] | `polygon=` **[未核实：atlas.key 全文 `grep -n -i 'polygon'` 零命中（exit 1），ATLAS `region` 卡上没有这个参数]** —— 任意多边形一律走 DevEdit（§3），不要在 ATLAS 段尝试 |
| `electrode` | `number=`、`name=`、`x.min/x.max/y.min/y.max` [已核实: atlas.key:536 `number NUM 1`、:590 `name CHAR 2`、:553–556] | `top` [已核实: atlas.key:580 `top LOG 3 f`]、`bottom` [已核实: atlas.key:581 `bottom LOG 4 f`]、`substrate` [已核实: atlas.key:582 `substrate LOG 4 f`，与 `bottom` 同槽 4 = 同义]、`material=` [已核实: atlas.key:589 `material CHAR 1`]、`thickness=` [已核实: atlas.key:571 `thickness NUM 22 0.0`] |
| `doping` | `uniform`、`gaussian`、`n.type`/`p.type`、`concentration=`、`region=`、`x.min/x.max/y.min/y.max`、`y.char=`、`direction=y` [已核实: atlas.key:341 `gaussian LOG 1 f`、:342 `uniform LOG 2 f`、:343 `p.type LOG 3 f`、:346 `n.type LOG 4 f`、:424 `concentr NUM 1`、:526 `region CHAR 11`、:433/440/445/435 `x.min/x.max/y.min/y.max`、:427 `y.char NUM 2`、:512 `directio CHAR 1`] | `x.char=` [已核实: atlas.key:430 `x.char NUM 3`，同槽别名 `lat.char`]、`ratio.lateral=` [已核实: atlas.key:441 `ratio.la NUM 9 0.70`，同槽别名 `xy.ratio`]、`peak=` [已核实: atlas.key:449 `peak NUM 13`]、`junction=` [已核实: atlas.key:437 `junction NUM 7`]、`infile=`（外部剖面）[已核实: atlas.key:513 `infile CHAR 2`] |
| `save` | `outf=`（写 `.str`）[已核实: atlas.key:7116 `save 41` / :7117 `outfile CHAR 1`] | — |

> 材料名（`air` / `Al2O3` / `SiO2` / `4H-SiC` …）是 `material=` 的**字符值**，不是 atlas.key 的关键字行，
> 因此在 atlas.key 里 grep 不到是正常的；它们的权威表在 atlas_users1.pdf 附录 B "Material Systems"
> （`Air` / `Al2O3` / `Ambient` / `BPSG` 同列，manual 文本第 78692 行）。
> `region` 卡上确实存在的材料**逻辑量**只有 `silicon`/`oxide`/`sio2`/`nitride`/`sapphire`/`sic`/`diamond` 等
> [已核实: atlas.key:248–300]，`air` 与 `al2o3` 不在其中 —— 所以必须写成 `material=air`，不能写裸标志。

### 分级加密的写法要点

- `x.mesh` / `y.mesh` 只声明**控制点**，ATLAS 在相邻控制点之间平滑过渡。要在某个坐标处形成一条真正的网格线，就必须显式写出该 `loc`。
- **关键界面必须成对声明**：例如 Al₂O₃ 层 `y=-0.02` 与 `y=0.00` 都写 `spac=0.004`，才能保证 0.02 µm 的介质里有 ≥5 层网格。只写一侧会让另一侧被邻区的粗间距吞掉。
- **加密要包夹目标**：想加密 `x=15.0` 的场板边缘，写 `14.85 / 14.95 / 15.00 / 15.05 / 15.15` 一组细 `spac`，而不是只写 `15.0`。
- 相邻控制点的 `spac` 比值控制在 2–4 倍以内；跳变过猛会产生高长宽比单元，直接伤收敛。
- 不要在每个电极边缘都插入"人为极密网格线"。本项目已验证：遵循边界 + 平滑间距的写法（5504 节点 / 10710 三角形 / 0 钝角）比盲目加密更稳、更可重复。

### 掺杂候选写法

| 需求 | 候选 | 标记 |
|---|---|---|
| 体区背景浓度 | `doping region=N n.type concentration=<c> uniform` | **[默认]** |
| 源漏注入 / 表面重掺 | `doping gaussian ... y.char=<µm> direction=y` + 窗口 `x.min/x.max/y.min/y.max` | **[默认]** |
| 工艺真实剖面 | 由 Athena（路径 C）生成结构后 `mesh inf=` 继承 [已核实: atlas.key:112 `infile CHAR 1`（mesh 卡），`inf` 为唯一前缀] | 有工艺卡时 |
| 外部实测/SIMS 剖面 | `doping ... infile=<file>` [已核实: atlas.key:513 `infile CHAR 2`（doping 卡）]；文件格式（`master` / `ascii` 等）另有开关，[未核实：本次未核对格式关键字] | 可用 |

高斯掺杂的 `y.char` 是**高风险参数**：特征长度过大会穿透关键界面并补偿沟道。经验规则：`y.char ≤ 目标层厚 / 5`，并在坐标审计里显式写出"剖面 1e-2 衰减深度 vs 层底坐标"。

---

## 3. 路径 B：DevEdit（任意多边形 + 重划分）

### 骨架（已在本项目实跑通过；语法出处见块后说明）

> **核实基准不同于 §2**：DevEdit 不在 `atlas.key` 里（`grep -n -E '^(devedit|athena) ' atlas.key` 零命中），
> 本机也**没有** DevEdit 关键字表（`/atctools/Synopsys/Silvaco2024/lib/devedit/2.8.26.R/common/` 下只有
> `athenares`）。而且本机 `examples/deckbuild/5.2.40.R` 里**一个 `go devedit` deck 都没有**
> （`grep -rl -i 'go devedit' ... --include='*.in' | wc -l` → `0`）。
> 因此下面每一行只能用两种权威之一标注：
> **(a)** `/atctools/Synopsys/Silvaco2024/lib/devedit/help/DevEdit.pdf`（`pdftotext -layout` 后按行号引用）；
> **(b)** 本项目实跑通过（≠ 文档核实）。

```silvaco
go devedit
init infile="<case>_base.str" mesh=false
work.area x1=0.0 y1=-1.42 x2=24.0 y2=0.50

region reg=20 name=fieldplate mat=Nickel elec.id=4 work.func=0 \
       color=0xffff96 pattern=0xe \
       polygon="13.0,-0.42 15.0,-0.42 15.0,-0.47 13.0,-0.47 13.0,-0.42"
       # ↑ polygon= [未核实]，DevEdit.pdf 只登记 points=；文档写法为 points="13.0,-0.42 ... 13.0,-0.42"
constr.mesh region=20 default        # 官方缩写是 reg=20

base.mesh height=0.20 width=0.50
bound.cond apply=false max.slope=28 max.ratio=20 rnd.unit=0.0005 \
           line.straightening=1 align.points when=automatic
           # ↑ apply=false [未核实]，DevEdit.pdf 8.16 参数表里没有 apply
imp.refine min.spacing=0.002

constr.mesh max.angle=90 max.ratio=20 max.height=0.50 max.width=1.00 \
            min.height=0.001 min.width=0.001
constr.mesh type=Semiconductor default
constr.mesh type=Insulator default
constr.mesh type=Metal default
constr.mesh type=Other default

# 逐层约束
constr.mesh x1=0.0 x2=24.0 y1=-0.42 y2=-0.02 max.height=0.020 max.width=0.20
constr.mesh x1=0.0 x2=24.0 y1=-0.02 y2=0.00  max.height=0.004 max.width=0.15
constr.mesh x1=0.0 x2=24.0 y1=0.00  y2=0.30  max.height=0.020 max.width=0.20

# 接触边缘盒式加密
constr.mesh x1=12.90 x2=13.10 y1=-0.50 y2=0.08 max.height=0.010 max.width=0.020
# 高场 ROI / 轨迹管
constr.mesh x1=14.85 x2=15.15 y1=-0.52 y2=0.05 max.height=0.020 max.width=0.020

mesh mode=meshbuild                  # [未核实] DevEdit.pdf 8.25 登记的是 mode=mesh.build（带点）
structure outf="<case>_structure.str"
```

### 上面这段骨架的逐行核实结论

| 写法 | 结论 |
|---|---|
| `init infile= mesh=false` | [已核实: DevEdit.pdf 8.23 INITIALIZE，`FILE.NAME=<c> (file, infile, inf)`、`MESH[=<boolean>]`，文本行 2902/2908/2914；`mesh=false` 明确表示"只读几何不读旧网格"] |
| `work.area x1= y1= x2= y2=` | [已核实: DevEdit.pdf 8.37 WORK.AREA，文本行 3585 `X1=<n> (LEFT)` … 3588 `Y2=<n> (BOTTOM)`] |
| `region reg= name= mat= elec.id= work.func= color= pattern=` | [已核实: DevEdit.pdf 8.31 REGION，语法行 3217–3220 + 3222 `Preferred Abbreviation: REG` + 3258 `ELECTRODE.ID[=<n>] (ELEC.ID)`、3266 `WORK.FUNCTION=<n>`。`mat=Nickel` 的材料名见 DevEdit.pdf 通用材料表第 4395 行 `77 "Nickel" "Ni"`] |
| `region ... polygon="..."` | **[未核实：DevEdit.pdf 8.31 的语法行只登记 `POINTS=<point2d_list>`（文本行 3219/3257，示例 3277/3284/3289），全文 `grep -n -i 'polygon *='` 零命中（exit 1）]**。本项目实跑通过，但按本机文档应写 **`points="13.0,-0.42 15.0,-0.42 …"`**。不要删掉这行——它是"跑得通但查不到出处"的典型。 |
| `constr.mesh ... x1= x2= y1= y2= max.angle= max.ratio= max.height= max.width= min.height= min.width=` | [已核实: DevEdit.pdf 8.17 CONSTRAINT.MESH，语法行 2400–2406 + 参数表 2460 `MAXIMUM.ANGLE[=<n>] (MAX.ANGLE)` / 2467 `MINIMUM.HEIGHT (MIN.H)` / 2469 `MINIMUM.WIDTH (MIN.W)`；`Preferred Abbreviation: constr.mesh` 见 2397] |
| `constr.mesh type=Semiconductor\|Insulator\|Metal\|Other` | [已核实: DevEdit.pdf 文本行 2443 `MATERIAL.TYPE=<c> (MAT.TYPE, TYPE) … Values can be: Semiconductor, Metal, Insulator, Other` —— `type=` 是官方登记的缩写] |
| `constr.mesh region=<n> default` | [已核实: DevEdit.pdf 文本行 2439 `REGION.ID=<n> (REG)` / 2441 `REGION.NAME=<c> (REG)`、2458 `DEFAULT Before setting specified values, reset all values …`]。官方示例写 `constr.mesh reg=1 …`（文本行 2488）；**建议改用 `reg=`**，`region=` 同时是 `region.id`/`region.name` 的前缀。 |
| `base.mesh height= width=` | [已核实: DevEdit.pdf 8.15 BASE.MESH，文本行 2299 `BASE.MESH [HEIGHT=<N>] [WIDTH=<N>]`] |
| `bound.cond max.slope= max.ratio= rnd.unit= line.straightening= align.points when=automatic` | [已核实: DevEdit.pdf 8.16 BOUNDARY.CONDITIONING，语法行 2332–2334 + 2342 `[WHEN=] never\|once\|automatic (default = automatic)`、2346 `MAXIMUM.SLOPE=<n> (max.slope)`、2356 `MAXIMUM.RATIO=<n> (MAX.RATIO`、2357 `ROUNDING.UNIT=<n> (RND.UNIT, RND)`、2365 `LINE.STRAIGHTENING=<n> (LINE.STR)`、2368 `ALIGN.POINTS[=<BOOLEAN>]`；`Preferred Abbreviation: bound.cond or bnd.cond` 见 2329] |
| `bound.cond apply=false` | **[未核实：DevEdit.pdf 8.16 的参数表里没有 `apply`；只在 "Replaces Card" 的老式写法里出现 `[NoSet] [NoApply]`（文本行 2382）]**。本项目实跑没报错，但无文档出处。 |
| `imp.refine min.spacing=` | [已核实: DevEdit.pdf 8.22 IMPURITY REFINE，文本行 2839 `IMPURITY.REFINE MINIMUM.SPACING=<N>`、2843 `Preferred Abbreviation: imp.ref`、2870 `MINIMUM.SPACING=<n> (MIN.SPAC)`] |
| `mesh mode=meshbuild` | **[未核实：DevEdit.pdf 8.25 MESH 登记的取值是带点的 `MESH.BUILD`（语法行 2985 `MESH[[MODE=]MESH.BUILD\|TENSOR.PRODUCT\|DELETE]]`，官方示例 3008 `mesh mode=mesh.build`）；无点写法在本机文档中查不到]**。本项目实跑通过，但建议统一改成 `mesh mode=mesh.build`。 |
| `structure outf=` | [已核实: DevEdit.pdf 8.35 STRUCTURE，文本行 3505 `STRUCTURE OUTFILE=<C>`、3511 `FILE.NAME=<c> (FILE, OUTFILE, OUTF)`] |

### `constr.mesh` 常用约束速查

| 形式 | 作用 |
|---|---|
| `constr.mesh max.angle= max.ratio= max.height= max.width= min.height= min.width=` | 全局单元形状与尺寸上下限。`max.angle` 官方取值范围 **90–180 度**，写 90 即"完全不允许钝角"（DevEdit.pdf 2460–2461）；`min.height`/`min.width` 的语义是"比这更矮/更窄的三角形在杂质细化时不再被切分"（同上 2467/2469），不是硬性下限 |
| `constr.mesh type=Semiconductor\|Insulator\|Metal\|Other default` | 按材料类别恢复默认约束，必须四类都写，漏写的类别可能不受控（`type` = `material.type` 的官方缩写，DevEdit.pdf 2443） |
| `constr.mesh reg=<reg> default` | 新加多边形区域的默认约束（官方缩写是 `reg=`，见 DevEdit.pdf 2439/2488；写 `region=` 会同时前缀命中 `region.id` 与 `region.name`） |
| `constr.mesh x1= x2= y1= y2= max.height= max.width=` | **盒式局部加密**（逐层、接触边缘、高场 ROI、SEU 轨迹管都用这个） |
| `base.mesh height= width=` | 重划分的基准单元尺寸（相当于"最粗" backbone） |
| `bound.cond max.slope= max.ratio= rnd.unit= line.straightening= align.points` | 边界拟合与点对齐；`rnd.unit`（= `rounding.unit`）是坐标吸附粒度——"All boundary points are rounded to an even multiple of this unit"（DevEdit.pdf 2357–2358），太大会吃掉薄层。注意官方还提醒 `max.slope` **必须小于** `max.ratio`（同上 2353：“must always be less than the maximum triangle ratio (max.ratio)”） |
| `imp.refine min.spacing=` | 按掺杂梯度自动细化时的最小三角形尺寸（`minimum.spacing`，DevEdit.pdf 2839/2870） |

> `rnd.unit` 与最薄层的关系必须检查：本项目 `rnd.unit=0.0005` vs 最薄层 0.02 µm，比值 **40 倍（≈1.6 个量级）**。
> 经验规则写作"`rnd.unit` 至少比最薄层小 1–2 个量级"；早先文档里的"至少小两个量级"与本项目自己的取值不自洽，已修正。
> 判据仍然是：`最薄层厚度 / rnd.unit ≥ 20`，否则薄介质会被吸附成零厚度。

---

## 4. A → B 衔接（本项目的标准双段写法）

**一个 `.in` 文件内完成建模 + 电学**（文件落位纪律见 §9）：

```
go atlas   ──► 建矩形 base（region/electrode/doping/user.material）──► save outf=*_base.str
go devedit ──► init infile=*_base.str mesh=false ──► region polygon= ──► constr.mesh ──► mesh mode=meshbuild ──► structure outf=*_structure.str
go atlas   ──► mesh inf=*_structure.str ──► material/mobility/impact 按 region 重绑定 ──► contact/thermcontact ──► method ──► solve
```

### 衔接的四个已验证陷阱（都真实发生过，逐条防）

| # | 现象 | 根因 | 强制做法 |
|---|---|---|---|
| 1 | 第二段 ATLAS 只读到 3 个电极；log 出现 `Contact number given (...) is out of range.` | DevEdit 导入的 base 结构使用了**超出可见材料区数量的内部 region ID**；新多边形用 `reg=6` 与内部源极区撞号 | 新增多边形一律用高号（如 `reg=20`）；并在 runner 里加后置检查：最终结构必须导入**恰好 N 个电极**且无 out-of-range 警告 |
| 2 | ATLAS 打印 `Eg = 1.08 eV` / `epsilon = 11.8`（硅默认），暗态电流高几个量级 | DevEdit 重划分保留了"半导体"属性但**丢弃了 `user.material` 名字**，第二段里 `material=BetaGa2O3` 的语句被静默忽略 | 第二段一律用 **`material region=<N> ...`** 绑定物理参数，不要用 `material material=<自定义名>`；并在 log 中确认没有 `Statement ignored` 与 missing-default-material 警告 |
| 3 | 重载 ATLAS master checkpoint 报 G-record read error | ATLAS 5.40 无法重载由 DevEdit 非结构网格保存的 master checkpoint | 不跨 run 复用 checkpoint；瞬态 deck 必须**在同一进程内**重跑 prebias 并从内存态继续 |
| 4 | 怀疑重划分改变了掺杂 | — | 用 box-limited extract 在 drift / substrate / source 注入盒 / drain 注入盒四处提取净掺杂并与设计值对比（本项目实测：`1.10e17` / `1.15e16` / `5.011e19` / `5.011e19`，与设计一致，DevEdit 重划分**确实保留**掺杂）。把这四条提取固化为每个 case 的 runner gate |

### 电极实现候选

| 候选 | 写法 | 标记 |
|---|---|---|
| 无厚度线电极 | ATLAS `electrode ... y.min=y.max=<面>` [已核实: atlas.key:555/556 `y.min NUM 8` / `y.max NUM 9`（electrode 卡）] | **[默认]**（本项目已验证基准） |
| 有厚度金属体电极 | DevEdit `region ... mat=<Metal> elec.id=<n> work.func=` + 多边形（多边形写法见 §3 的 `points=` 未核实项） [已核实: DevEdit.pdf 8.31，文本行 3258/3266] | 需要真实金属体/场板厚度时；改用后必须重验高场位置与偏压加载 |
| 场板与栅短接 | 第二段 ATLAS `contact name=fieldplate workfunc=<eV> common=gate short` [已核实: atlas.key:4590 `name CHAR 1`、:4462 `workfunc NUM 2 -999`、:4593 `common CHAR 3`、:4538 `short LOG 15 f`] | 场板器件 |

> **`workf=` vs `workfunc=`**：CONTACT 卡上真正登记的是 `workfunc`（atlas.key:4462）；
> 裸 `workf`（atlas.key:1962）是 **MATERIAL 卡**的参数。`contact ... workf=` 能跑通只是因为它是
> `workfunc` 在 contact 卡内的唯一前缀缩写（Silvaco 自带 deck 也这么写）。**本包统一写 `workfunc=`**，
> 因为只有这个拼法能直接 grep 到。
>
> **`common` 与 `short` 不是一回事**（manual 22.x CONTACT 参数表）：
> - `common=<另一电极>`：把本电极的**偏压**锁定到另一电极；两个电极的**电流仍分开统计**。
>   被 `name=` 指到的那个电极不能再出现在任何 `solve` 语句里，它的偏压由 `common` 指向的电极决定。
> - `short`：与 `common` 配合，把两个电极**当成一个**，`.log` 与运行输出里只写**一路**电流。
>
> 所以"只写 `common=` 会留下一个可独立加压的浮空端子"是**错的**——漏写 `short` 的唯一后果是
> `.log` 里出现两路分开的电流。场板器件要不要 `short`，取决于你想不想把场板电流并入栅极电流。

---

## 5. 路径 C：Athena → ATLAS

接口契约是稳定的，工艺语句本身按项目的工艺卡在 `/atctools/Synopsys/Silvaco2024/examples/deckbuild/5.2.40.R/` 中核对（Athena 语句不在 `atlas.key` 里，`grep -n -E '^(athena|devedit) ' atlas.key` 零命中）：

```silvaco
go athena
# ... 工艺语句（注入 / 扩散 / 氧化 / 刻蚀 / 淀积）— 具体关键字需在 examples/deckbuild/5.2.40.R 核对 ...
structure outf="<case>_process.str"

go atlas simflags="-V 5.40.0.R -P 4"
mesh inf="<case>_process.str"
# 工艺结构的 region 编号由 Athena 决定 —— 必须先 TonyPlot 或 log 核对 region 号，再写 material/mobility 绑定
```

工艺结构的 region 号和电极名**不是你写的**，因此 §4 陷阱 #2 同样适用：先核对 region 编号表，再按 region 绑定物理。

---

## 6. 自定义材料 `user.material`

### 声明

```silvaco
material material=BetaGa2O3 user.group=semiconductor user.default=GaN \
        affinity=4.0 eg300=4.8 nc300=3.72e18 nv300=4.2e18 \
        permittivity=10.0 mun=300 mup=10 tcon.const tc.const=0.27
```

[已核实（全部在 MATERIAL 卡 atlas.key:1948–3072 内）: :2897 `material CHAR 2`、:2926 `user.group CHAR 30`、:2925 `user.default CHAR 29`、:1961 `affinity NUM 11`、:1952 `eg300 NUM 3`、:1967 `nc300 NUM 15`、:1969 `nv300 NUM 16`、:1953 `permittivity NUM 4`、:1956 `mun NUM 7`、:1963 `mup NUM 12`、:2980 `tcon.const LOG 1 f`、:2036 `tc.const NUM 79`]（注意：`affinity`/`permittivity` 两条的行号与 device-physics-and-solver.md 所记恰好互为镜像——该文件写 affinity=:1953、permittivity=:1961——两边至多一边正确。本文件的行号随槽位号单调递增（:1952 槽3 → :1953 槽4 → :1956 槽7 → :1961 槽11）自洽性更高，但行号仍 [待 atlas.key 复核]；参数存在性不受影响）

> **`tcon.const` 是 LOG 开关，`tc.const` 才是数值**（atlas.key:2980 是 `LOG`，:2036 是 `NUM`）。
> 绝对不要写成 `tcon.const=0.27`。想要温度相关的热导率，改用 `tcon.power tc.npow=<n> tc.const=<k300>`
> [已核实: atlas.key:2981 `tcon.power LOG 2 f`、:2038 `tc.npow NUM 80`；manual 文本行 29645–29646
> "Enabling TCON.POWER: `material mat=Diamond TCON.POWER TC.NPOW=2 TC.CONST=1.4`"]。
> β-Ga₂O₃ 的各向异性热导率另有 `tc.aniso` [已核实: atlas.key:2394 `tc.aniso NUM 362 0.0`]，
> 但其取值与效果 **[未核实：本项目未实测]**。

- `user.group=semiconductor`：告诉 ATLAS 这是半导体（而非绝缘体/金属）。[已核实: atlas.key:2926 `user.group CHAR 30`（material 卡）；取值 `semiconductor` / `insulator` / `conductor` 见 atlas_users1.pdf B.2.5（manual 文本行 78591 起，取值行 78599–78601）]
- `user.default=<内建材料>`：**所有你没显式给出的参数都从这个基材继承**。选一个能带结构/输运特性最接近的基材（本项目宽禁带 β-Ga₂O₃ 选 `GaN`），并在 deck 注释里写明这个选择的依据。[已核实: atlas.key:2925 `user.default CHAR 29`（material 卡）；manual 文本行 78605 `user.default=known_atlas_material_name`]
- `region` 语句里引用自定义材料要用 `user.material=<Name>`，而不是 `material=<Name>`。[已核实: atlas.key:327 `user.material CHAR 3`（**region** 卡），material 卡上没有这个参数；manual B.2.5 完整示例正是 `region num=1 … user.material=my_oxynitirde`（文本行 78618，原文含拼写笔误）+ `material material=my_oxynitride user.group=insulator user.default=oxide permittivity=9`（文本行 78627）；另见 78603 `user.material=material_name`]
- 同名参数 `user.material` 在 `electrode` 卡上也存在 [已核实: atlas.key:591]，用于把电极也标成自定义材料。

### 陷阱

1. **两段 ATLAS 都要声明**。第一段建结构时的 `material` 语句不会自动带到第二段。
2. **过了 DevEdit 就按 region 绑定**（§4 陷阱 #2）。这是硬性规则，不是可选优化。
3. 每次跑完必须在 log 里核对 ATLAS 实际打印的 `Eg` / `epsilon` / 迁移率是否等于设计值。看到硅默认值（`Eg = 1.08`、`epsilon = 11.8`）就说明绑定失败，**立即停止，不要继续解电学**。这条正是 manual 自己的建议：B.2.5 结尾写 "After creating your new material in Atlas, include a print on your MODELS statement to echo the parameter values used for the material."（manual 文本行 78632）。所以自定义材料的 deck 应当固定带 `models print` [已核实: atlas.key:975 `print LOG 12 f`（models 卡，962–1947）]。
4. 未显式给出的参数（如 SRH 寿命、Auger 系数、碰撞电离系数）会静默继承基材的值。宽禁带器件必须显式给 `impact` 和 `mobility`，不能依赖继承。IMPACT 卡上这几个字段全部存在 [已核实（IMPACT 卡 atlas.key:5367–5619）: :5370 `selb LOG 3 t`、:5419 `an1 NUM 3 7.03e5`、:5421 `an2 NUM 4 7.03e5`、:5422 `bn1 NUM 5 1.231e6`、:5424 `bn2 NUM 6 1.231e6`、:5431 `betan NUM 11 1.0`、:5435 `egran NUM 13 4.0e5`]（注意：`an2`/`bn1`/`bn2` 的行号与 wbg-radiation-and-seb.md 所记 :5420/:5421/:5422 不一致，两组至多一组正确，行号 [待 atlas.key 复核]；参数存在性与默认值不受影响），但**下标含义容易写反，本包统一按 manual 口径**：
   - **`an1`/`bn1`/`ap1`/`bp1` = 高场段，E > `egran`**；**`an2`/`bn2`/`ap2`/`bp2` = 低场段，E < `egran`**（manual 文本行 13053–13054：“you can define a value of electric field, EGRAN V/cm, where for electric fields, >EGRAN V/cm, the parameters are: AN1, AP1, BN1, BP1, while for electric fields, <EGRAN V/cm, the …”）。写反会让高低场两段的电离系数整体互换，BV 直接算错。
   - `selb` 的默认值就是 `t`，显式写出来是为了让 deck 自解释，不是为了"打开"它。
   - `betan`/`betap` **同名跨卡**：IMPACT 卡上两者默认均为 1.0（atlas.key:5431/5433）；MOBILITY 卡上两者默认值**不同**——`betan` 默认 **2.0**、`betap` 默认 **1.0**（本地已核：atlas_users1.pdf p.230 Table 3-90 "User-Definable Parameters in the Field-Dependent Mobility Model"：`MOBILITY BETAN 2.0` / `MOBILITY BETAP 1.0`；此前笼统写"MOBILITY 卡上默认 2.0"有误。atlas.key:5938/5939 行号 [待 atlas.key 复核]），含义完全不同。写的时候必须确认自己在哪张卡上。
5. 自定义材料名不要与内建材料重名。特别注意 **Diamond 是 ATLAS 内建材料**（`diamond` 逻辑量在 region/material/mobility 三张卡上都有：atlas.key:287 / 3014 / 5802），可以直接 `material mat=Diamond ...`，**不需要**走 `user.material` 这一套；而 Ga₂O₃ 没有内建条目，才必须自定义。

### 自定义材料的候选做法

| 候选 | 说明 | 标记 |
|---|---|---|
| `material material=<Name> user.group= user.default=` | 结构阶段声明新材料名 [已核实: atlas.key:2897/2926/2925] | **[默认]**（路径 A） |
| `material region=<N> user.group= user.default= ...` | 按 region 号绑定 [已核实: atlas.key:2935 `region CHAR 39`（material 卡，**CHAR 型**，可传区号或区名）] | **[默认]**（路径 B/C，DevEdit/Athena 之后） |
| 借用内建材料名并覆写全部关键参数 | 少写一层间接，但语义上会误导后续读者 | 不推荐，仅在 `user.material` 明确不可用时 |

---

## 7. 分级网格策略

原则：**关键区细、非关键区粗；先保证物理量被解析，再控制节点数。**

| 区域 | 细化建议 | 理由 |
|---|---|---|
| 栅介质 / 势垒层（薄介质） | 垂直方向 ≥5 层网格（如 0.02 µm 介质用 `spac=0.004`） | 栅控、隧穿、界面场 |
| 沟道 / 异质界面 / 2DEG | 垂直 0.001–0.003 µm | 极化电荷与二维电子气 |
| 栅边缘 / 漏侧高场 / 场板边缘 | 横向 0.02–0.1 µm，用 3–5 条控制线包夹 | BV、雪崩起始点、SEB 触发位置 |
| SEU / 重离子轨迹管 | 沿轨迹的窄盒 `constr.mesh`，径向 ≈ `radius/3` | 瞬态电荷密度梯度极陡 |
| 漂移区体内 | 0.02–0.05 µm | 电场分布与耗尽扩展 |
| 衬底 / buffer / 空气 | 0.1–0.5 µm | 非关键体区，避免拖慢 |

**反模式**：对整个材料界面做全局细化（无论用 ATLAS 全局 `spac` 还是 DevEdit 全局 `constr.mesh`）。它会连同无用的 buffer/衬底界面一起细化，节点数爆炸。永远优先 **region-based** 或 **盒式(box) 加密**。

---

## 8. 节点数、内存与 `-P` 并行

本机事实：远端 `tcad` 为 RHEL 7.9、**8 vCPU / 8 GB RAM**，本项目冻结 `simflags="-V 5.40.0.R -P 4"`。

| 阶段 | 节点数量级 | 说明 |
|---|---|---|
| 探索 / 流程冒烟 | 3k–8k | 本项目线电极基准：**5504 节点 / 10710 三角形 / 0 钝角** |
| 生产（BV、静态扫描） | 10k–30k | 8 GB 下安全 |
| 高负载（多边形 + 瞬态 + 自热） | 30k–60k | 本项目 DevEdit 场板案例：**48807 节点 / 96943 三角形 / 0 钝角**，可跑但要留意内存 |
| >100k | — | 8 GB 下高风险；先减 ROI 范围或降 `-P`，不要直接提交 |

规则：

- **钝角三角形必须为 0**（DevEdit `constr.mesh max.angle=90`）。有钝角就先修网格，不要去调求解器。
- `-P N` 不改变物理解，但**必须与 ATLAS 版本一起冻结**才能保证逐字节可重复。本项目已用两次独立冷启动验证：固定 `-V 5.40.0.R -P 4` 时，两次的电场 CSV / IV 数据 / 提取结果逐字节一致。
- 8 vCPU 上不要同时跑超过 2 个 `-P 4` 任务（会超订 CPU 且抢内存）。
- 内存吃紧时优先**缩小加密盒**，其次降 `-P`，最后才降物理精度。

---

## 9. 文件落位纪律（用户硬性规则）

- 主控端 `D:\SILVACO_LOCAL` **只放**：`.py` 脚本 / `.md` 技术文档 / 轻量 `.csv` / `.png` 图 / `.in` deck。
- `.in` deck 必须把**建模（结构）与特性仿真（电学）合并为同一个文件**：
  `go atlas`（建结构）→ `save outf=*.str` →〔可选 `go devedit`〕→ `go atlas`（重新进入）→ `mesh inf=*.str` → 电学求解。
- 一切大体积 `.str` / `.log` 归档到 Windows `E:\silvaco2425\bulk\{str,log}\RUN_<case>_<UTCstamp>\`（按 run 建子目录，层级口径与 batch-run-and-monitor.md §5 一致）。
- 远端运行期间产物留在 `/root/DECKBUILD/RUN_<case>_<UTCstamp>/`（运行目录命名与本包其它参考文件一致，统一带 `RUN_` 前缀），结束后回传归档；`/root/DECKBUILD` 是唯一正在迭代的运行区，不要把整套远端工程复制回 Windows。
- 不要往 `/mnt/hgfs/{share_wm,share24,16sil_share}` 写大文件（HGFS 共享已 98% 满）。

---

## 10. 强制坐标审计（每次改结构后必做）

**在提交任何仿真之前**，先写出坐标审计表并逐行核对守恒关系。审计不通过就不要跑，更不要把几何错误当成物理模型问题去调参数。

### 10.1 模板（复制到 `progress.md` 或 case 目录）

**表 1 — 垂直层叠（y 向下为正）**

| 层 / region | 材料 | y.min | y.max | 厚度 | 设计厚度 | 一致? |
|---|---|---:|---:|---:|---:|:--:|
| | | | | | | |
| **合计** | | `y_top` | `y_bot` | Σ厚度 | `y_bot - y_top` | 必须相等 |

**表 2 — 横向分段（x）**

| 段 | x.start | x.end | 长度 | 设计长度 | 一致? |
|---|---:|---:|---:|---:|:--:|
| | | | | | |
| **合计** | `x_min` | `x_max` | Σ长度 | `x_max - x_min` | 必须相等 |

**表 3 — 电极 / 接触**

| 名称 | number / elec.id | x 范围 | y（线电极为单值） | 落在哪个界面 | contact 名 ≠ region 名? |
|---|---|---|---|---|:--:|
| | | | | | |

**表 4 — 掺杂窗口**

| 剖面 | 类型 | 峰值浓度 | 窗口 x | 窗口 y | 特征长度 | 1e-2 衰减深度 | 是否穿透关键界面? |
|---|---|---:|---|---|---:|---:|:--:|
| | | | | | | | |

**表 5 — 网格关键线**

| 关注对象 | 坐标 | 该处 `spac` / `max.height` | 该层内层数 | 是否达标 |
|---|---:|---:|---:|:--:|
| | | | | |

### 10.2 已填写的工作示例（β-Ga₂O₃ 场板 MOSFET，24 µm × 1.92 µm）

**表 1 — 垂直层叠**

| 层 / region | 材料 | y.min | y.max | 厚度 | 设计厚度 | 一致? |
|---|---|---:|---:|---:|---:|:--:|
| 1 ambient_air | air | -1.42 | -0.42 | 1.00 | 1.00 | ✓ |
| 5 SiO2_passivation | SiO2 | -0.42 | -0.02 | 0.40 | 0.40 | ✓ |
| 4 Al2O3_gate_dielectric | Al2O3 | -0.02 | 0.00 | 0.02 | 0.02 | ✓ |
| 2 epilayer (drift) | BetaGa2O3 | 0.00 | 0.30 | 0.30 | 0.30 | ✓ |
| 3 substrate | BetaGa2O3 | 0.30 | 0.50 | 0.20 | 0.20 | ✓ |
| **合计** | | **-1.42** | **0.50** | **1.92** | **1.92** | ✓ |

**表 2 — 横向分段**

| 段 | x.start | x.end | 长度 | 设计长度 | 一致? |
|---|---:|---:|---:|---:|:--:|
| source 接触 | 0.0 | 2.0 | 2.0 | 2.0 | ✓ |
| L_sg（源-栅） | 2.0 | 11.0 | 9.0 | 9.0 | ✓ |
| L_g（栅长） | 11.0 | 13.0 | 2.0 | 2.0 | ✓ |
| L_gd（栅-漏） | 13.0 | 22.0 | 9.0 | 9.0 | ✓ |
| drain 接触 | 22.0 | 24.0 | 2.0 | 2.0 | ✓ |
| **合计** | **0.0** | **24.0** | **24.0** | **24.0** | ✓ |
| 场板投影（叠加在 L_gd 上） | 13.0 | 15.0 | 2.0 | 2.0 | ✓（起点必须= 栅右缘 13.0） |

**表 3 — 电极**

| 名称 | number / elec.id | x 范围 | y | 落在哪个界面 | contact 名 ≠ region 名? |
|---|---|---|---:|---|:--:|
| source | 1 | 0.0–2.0 | 0.00 | Al2O3/epilayer 顶面 | ✓ |
| drain | 2 | 22.0–24.0 | 0.00 | Al2O3/epilayer 顶面 | ✓ |
| gate | 3 | 11.0–13.0 | -0.02 | SiO2/Al2O3 界面 | ✓ |
| fieldplate | 4（DevEdit `reg=20`） | 13.0–15.0 | -0.42 … -0.47 | SiO2 内，厚 0.05 | ✓ |

导入后检查：第二段 ATLAS 必须报告**恰好 4 个电极**，且无 `Contact number ... is out of range`。

**表 4 — 掺杂窗口**

| 剖面 | 类型 | 峰值浓度 | 窗口 x | 窗口 y | `y.char` | 1e-2 衰减深度 ≈ 3.03·y.char | 穿透关键界面? |
|---|---|---:|---|---|---:|---:|:--:|
| drift 背景 | uniform n | 1.10e17 | 0–24 | 0.00–0.30 | — | — | 否 |
| substrate 背景 | uniform n | 1.15e16 | 0–24 | 0.30–0.50 | — | — | 否 |
| source 注入 | gaussian n | 5.0e19 | 0–2 | 0.00–0.15 | 0.020 | ≈0.061 → 深至 ≈0.21 | 否（drift 底在 0.30） |
| drain 注入 | gaussian n | 5.0e19 | 22–24 | 0.00–0.15 | 0.020 | ≈0.061 → 深至 ≈0.21 | 否 |

后验：box-limited extract 实测 `1.10e17` / `1.15e16` / `5.011e19` / `5.011e19`，与设计一致。

**表 5 — 网格关键线**

| 关注对象 | 坐标 | `spac` / `max.height` | 层内层数 | 达标 |
|---|---:|---:|---:|:--:|
| Al2O3 上界面 | y = -0.02 | 0.004 | 0.02/0.004 = 5 | ✓ |
| Al2O3 下界面（半导体表面） | y = 0.00 | 0.004 | 同上 | ✓ |
| 场板右缘高场点 | x = 15.00 | 0.020（14.85/14.95/15.00/15.05/15.15 包夹） | — | ✓ |
| SEU 轨迹管 | x = 15.0, y = 0.0→0.5 | 盒 `x1=14.95 x2=15.05` max 0.020 | radius=0.05 → ≥2 单元/半径 | ✓ |
| 全局 | — | 5504 节点 / 10710 三角形 / **0 钝角** | — | ✓ |

### 10.3 审计检查清单

- [ ] 表 1 Σ厚度 == `y_bot - y_top`，且**没有负厚度、没有未预期重叠**。
- [ ] 表 2 Σ长度 == `x_max - x_min`。
- [ ] 每个 region 的 `x/y` 范围都在 `work.area` 内。
- [ ] contact 名 ≠ region 名。
- [ ] 电极坐标落在真实存在的界面上（线电极 `y.min == y.max` 必须等于某个层边界）。
- [ ] 掺杂窗口在目标材料内，特征长度不穿透关键界面。
- [ ] 关键薄层的垂直网格层数 ≥5。
- [ ] 探针/轨迹坐标与几何特征点对齐（如探针 `y=-0.41999` 是刻意落在 `y=-0.42` 界面的介质一侧）。
- [ ] DevEdit 路径：新多边形 `reg=` 用高号、导入后电极数正确、`material` 按 region 绑定、log 中 `Eg`/`epsilon` 是设计值。
- [ ] 钝角三角形 = 0。
- [ ] 节点数在 §8 的预算区间内。

---

## 11. 常见失败诊断

| 现象 | 可能原因 | 检查 |
|---|---|---|
| `Contact number given (...) is out of range.` | DevEdit 新增多边形 `reg=` 与内部电极区撞号 | 改用高号 `reg=20`；核对导入后电极数量 |
| log 打印 `Eg = 1.08` / `epsilon = 11.8` | `user.material` 名在重划分后丢失，`material material=<Name>` 被忽略 | 改成 `material region=<N> ...`；搜 log 里的 `Statement ignored` |
| 结构导入后电极少了 / 名字变了 | region ID 冲突或 `elec.id` 与 `electrode number` 不匹配 | TonyPlot 打开 `.str` 目视核对电极，再看 log 的电极列表 |
| 重载 checkpoint 报 G-record read error | DevEdit 非结构网格的 ATLAS master checkpoint 不可跨 run 重载 | 同进程内重跑 prebias，从内存态继续 |
| 网格节点暴涨 / 跑不动 | 全局细化、加密盒过大、`base.mesh` 过细 | 改盒式局部加密；核对 §8 预算 |
| 出现钝角三角形 / 收敛差 | `constr.mesh max.angle` 未生效、相邻 `spac` 跳变过猛 | 加 `max.angle=90`；把相邻 `spac` 比值压到 ≤4 |
| 薄介质"消失" | `rnd.unit` 与最薄层同量级，坐标被吸附到该单位的整数倍 | `最薄层厚度 / rnd.unit ≥ 20`（本项目 0.02 / 0.0005 = 40） |
| 沟道电流为 0 / Vth 严重偏移 | 高斯 tail 穿透关键界面并补偿沟道 | 查表 4 的衰减深度；缩小 `y.char` |
| 高场峰出现在预期外的位置 | 几何从线电极换成了有厚度体电极 | 承认几何变了=物理变了，重跑暗态与 BV 基线再对比 |
| 掺杂疑似被重划分改动 | — | box-limited extract 四点审计（§4 陷阱 #4） |

---

## 12. 结构检查的可视化候选

| 候选 | 用法 | 标记 |
|---|---|---|
| **TonyPlot** | `export DISPLAY=:0` 后打开 `.str`，目视核对区域/电极/掺杂云图 | **[默认]** |
| TonyPlot3D | 3D 结构 | 仅 3D |
| Victory Visual | 较新，出版级导出 | 出图定稿时 |
| ATLAS `extract` box-limited | 在 deck 内直接提取指定盒内的净掺杂/场强，写成 runner gate | **[默认] 的自动化核对手段** |
| 外部 Python 解析导出的 `.csv`/`.dat` | 曲线与剖面复核（`.str` 二进制格式需先确认版本） | 批量比对时 |

目视只能发现"明显错"，**数值提取才能证明"确实对"**。两者都要做。
