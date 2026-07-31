# 宽禁带器件 / BV / 单粒子 (SEU-SEE) / SEB 参考

> 用途：在 Silvaco ATLAS 中做宽禁带 (β-Ga2O3 / GaN / p-GaN HEMT / SiC / AlGaN/GaN HEMT / Diamond) 的
> 击穿、单粒子入射、单粒子烧毁 (SEB) 与自热仿真时，本文件给出材料候选项、`singleeventupset` 用法、
> LET 单位换算、BV 与 SEB 判据、热边界与瞬态时间步策略、陷阱/半绝缘衬底建模。

---

## 0. 本文件中"已核实"与"待核实"的约定

本文件里的 ATLAS 语句分三档，写 deck 时必须区分：

| 标记 | 含义 |
|---|---|
| **[已核实]** | 直接来自远端 `$SILVACO/examples/deckbuild/5.2.40.R/**/*.in` 或 `$SILVACO/lib/atlas/5.40.0.R/common/atlas.key` / `template.lib`，可以照抄 |
| **[候选]** | 有多种等价做法，需要按项目目标选一个；已标 **[默认]** 的是本项目推荐值 |
| **[待核实]** | 参数名/数值来自物理常识或文献，**必须**在 `$SILVACO/examples` 或 ATLAS manual 中核对后再写进 deck |

> manual 的真实路径是 `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/docs/atlas_users1.pdf`
> （`$SILVACO/doc/` 目录**存在**，但里面只有安装/SFLM 文档，**没有 ATLAS 手册**——早期版本写
> "没有这个目录"与 preflight 的 `ls` 实测矛盾，疑似 `$SILVACO` 未 export 时的假阴性，
> 以 `preflight-and-environment.md` 的实测记录为准）；`pdftotext -layout` 在远端可用，语义问题查它，
> **关键字是否存在/缺省值查 `atlas.key`**。
>
> ⚠ **行号口径**：本文件引用的 `<deck>.in:N` 行号以**远端 VM 副本**为准；本地镜像
> `d:\knowledge\exp25` 中同名文件的行号普遍偏移 1–3 行（内容逐字一致；例如 `Rad_Rel_ex02.in` 的
> `METHOD max.temp=1000000 ...` 行本文记 :56、本地镜像实测在 :58）。离线核对时按**内容锚定**，不要死抠行号。

**不要凭记忆写 ATLAS 模型名。** 先在本机 examples 里 grep 同类语句：

```bash
export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
E=/atctools/Synopsys/Silvaco2024/examples/deckbuild/5.2.40.R
grep -rhiA3 'singleeventupset' $E --include='*.in' | sort -u
grep -rhi  '^ *TRAP '          $E --include='*.in' | sort -u
grep -rhi  'thermcontact'      $E --include='*.in' | sort -u
# 关键字白名单（哪些参数真的存在）：
sed -n '/SINGLEEVENTUPSET/,/CURVETRACE/p' \
  /atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key
```

### 0.1 ★ 抄例子之前必须先验"这个 deck 到底跑的是哪个仿真器" **[本项目硬规则]**

`examples/deckbuild/` 下**大量**例子跑的是 **Victory Process / Victory Mesh / Victory Device**，
**不是 ATLAS**。两者语法**不通用**：Victory Device 的 `IMPACT ... selberherr hysteresis=1 e.min=3e5`、
`METHOD ... lte.timestep constant.timestep seu.max.rad=...` 在 ATLAS 里**全部是未知关键字**。
本文件早期版本正是因为直接照抄了 `Rad_Rel_ex01.in` 的 METHOD 行而写进了 4 个不存在的参数。

```bash
grep -n -iE '^ *go ' <deck>.in     # 必须看到 `go atlas` 才算 ATLAS 例子
```

已确认是 **Victory Device** 而非 ATLAS 的常用例子（语句仍可参考，但**每个 token 都要回 `atlas.key` 复核**）：
`Rad_Rel_ex01 / ex02 / ex07 / ex11`、`Other_Power_ex08`、`GaN_Power_ex07 / ex12 / ex13`、
`SiC_Power_ex02 / ex08 / ex10`、`Bulk_ex03`。

---

## 1. 官方例子优先级（本机已核实路径）

例子根目录 **[已核实：`ls -d .../examples/deckbuild/*/` → `5.2.29.R/` `5.2.40.R/`；
`5.2.40.R/` 下有 `Educational/ Technology/ Tool/`，`Technology/` 下有 `CMOS_and_BiCMOS Display Memory
Opto_and_Photonics Power_and_RF Radiation_and_Reliability`]**：
`/atctools/Synopsys/Silvaco2024/examples/deckbuild/<ver>/Technology/`，
本机存在 `<ver>` = `5.2.29.R` 与 `5.2.40.R` 两套（与 ATLAS 的 `5.38.0.R` / `5.40.0.R` 不是同一编号体系，
本项目冻结 ATLAS `-V 5.40.0.R`，例子优先看 `5.2.40.R`）。

| 目标 | 例子目录（索引区间为 **5.2.40.R** 实测；5.2.29.R 只到 `GaN_Power_ex11` / `SiC_Power_ex10`） |
|---|---|
| β-Ga2O3 MOSFET + 自热（**本项目最近参照**） | `Power_and_RF/Other/Other_Power_ex08`（⚠ `GO victorydevice`，非 ATLAS deck） |
| 其它宽禁带/新材料功率器件 | `Power_and_RF/Other/Other_Power_ex01 … ex09` |
| GaN / p-GaN HEMT 系列（极化、陷阱、pGaN 栅） | `Power_and_RF/GaN/GaN_Power_ex01 … ex13` |
| 4H-SiC 功率器件、各向异性碰撞电离 | `Power_and_RF/SiC/SiC_Power_ex01 … ex11` |
| 单粒子 / 辐照 / 可靠性总入口 | `Radiation_and_Reliability/Radiation_and_Reliability/Rad_Rel_ex01 … ex11` |
| SEU 3D（Victory Process→Mesh→Device 全链，⚠ **非 ATLAS**） | `Rad_Rel_ex01` |
| SEU + `pcunits` + `radialgauss`（3D） | `Rad_Rel_ex03 / ex09`（`Silicon_Power_ex08` 亦有） |
| SEU + `entry=`/`exit=` 2D + `pcunits` | `Photodiode_ex13` |
| 混合模式 SEU（`device=` 指定子器件） | `Rad_Rel_ex07`（含 `device=AM3`）**[已核实：ex03 里没有 `device=`，早期版本引错]** |
| 功率器件 SEU/SEB 参照 | `Power_and_RF/Silicon/Silicon_Power_ex08` |
| 光生载流子 vs 粒子径迹对比 | `Opto_and_Photonics/Photodiodes/Photodiode_ex13` |

查例子的快捷方式：每个例子目录里都有 `.description_<name>.dat`（纯文本说明）和 `<name>.html`，
比直接读 `.in` 更快定位"这个例子到底在演示什么"。

---

## 2. 宽禁带材料候选项与建模要点差异

> **本项目默认材料：β-Ga2O3**。其余材料在这里列全，是为了当用户切换器件时不必重新调研。

### 2.1 差异总表

| 材料 | Eg (eV) | 极化 | 2DEG/2DHG | 双极性 | 热导率 κ 量级 (W/cm·K) | ATLAS 中的存在形式 |
|---|---|---|---|---|---|---|
| **β-Ga2O3 [本项目默认]** | ~4.8 | **无**（单斜、非纤锌矿，无自发/压电极化项） | 无（体导电 / MOSFET 沟道 / δ-doping） | **实质单极**：空穴自陷 (self-trapped hole)，无可用 p 型 | **~0.11–0.27，强各向异性**（[100] 最低）→ 自热最严重 | **user-defined material**：`region ... user.material=`（REGION 卡）+ `material ... user.default= user.group=`（MATERIAL 卡）**[已核实: atlas.key:327 user.material CHAR 3 (REGION 143-339)；atlas.key:2925 user.default CHAR 29 / :2926 user.group CHAR 30 (MATERIAL 1948-3072)；atlas.key 中无任何 ga2o3 逻辑量]** |
| GaN（体、PiN、垂直器件） | ~3.4 | 有（纤锌矿自发+压电），体内均匀时不产生净面电荷 | 无 | 可 p 型（Mg），但激活率低 → 需 `incomplete` | ~1.3–2.3 | 内建材料 `GaN` |
| **AlGaN/GaN HEMT**（耗尽型） | 3.4 / AlGaN 更高 | **必须开**：`polarization calc.strain` | **2DEG 由极化界面电荷产生**，不是靠掺杂 | 沟道内基本单极（电子） | ~1.3–2.3（GaN），衬底决定整体 | 内建 `GaN` / `AlGaN`（组分 x） |
| **p-GaN HEMT**（增强型） | 同上 | 同上，且 pGaN/AlGaN 界面极化决定 Vth | 2DEG + pGaN 层空穴 | pGaN 层需要 Mg 受主 + 不完全电离 | 同上 | 内建 + `trap` 描述 pGaN 深能级 |
| 4H-SiC | ~3.26 | 有（沿 c 轴），器件级通常不显式开 | 无 | **双极性良好**（n/p 都可做）→ 可做 PiN、IGBT | ~3.7–4.9（最好散热的宽禁带） | 内建：`material=4H-SiC`（polytype 名，作为 CHAR 值传入；atlas.key 只登记通用逻辑量 `sic`）+ **各向异性碰撞电离** **[已核实: atlas.key:283 sic LOG 29 (REGION) / :3007 (MATERIAL) / :5795 (MOBILITY)；atlas.key:5394 aniso LOG 22 / :5395 sic4h0001 LOG 23 t (IMPACT 5367-5619)]** |
| Diamond | ~5.47 | 无 | 表面转移掺杂可形成 2DHG（H-terminated） | p 型（B）可用，n 型极难 | **~20**（最高） | **内建 `Diamond`，不需要 user-defined** **[已核实: atlas.key:287 diamond LOG 33 (REGION) / :3014 (MATERIAL) / :5802 (MOBILITY)；manual Appendix B "Material Systems" 列有 DIAMOND；manual 示例 `material mat=Diamond TCON.POWER TC.NPOW=2 TC.CONST=1.4`]**（早期版本写"需按 user-defined 处理"是错的） |

### 2.2 每种材料写 deck 时最容易踩的坑

**β-Ga2O3 [本项目默认]**

- ATLAS 没有内建 Ga2O3（`atlas.key` 中查无 ga2o3 逻辑量），官方做法是 **user-defined material**，
  模板 **[已核实：逐字来自 `Other_Power_ex08.in:31,32,48-52,54`；每个 token 均在 `atlas.key` 对应卡上]**
  （⚠ 该 deck 是 `GO victorydevice`，不是 ATLAS deck；但下面这几行的每个关键字在 ATLAS 的
  REGION/MATERIAL/MOBILITY 卡上同样存在，可以安全照抄）：

```silvaco
region  number=2 user.material=Ga2O3 y.min=0.0 y.max=0.3
region  number=3 user.material=Ga2O3 y.min=0.3

material material=Ga2O3 user.default=GaN user.group=semiconductor \
  affinity=4.0 eg300=4.8 nc300=3.72e18 nv300=3.72e18 permittivity=10.0 \
  mun=118 mup=50 tcon.const tc.const=0.13
material material=Al2O3 tcon.const tc.const=0.33
material region=3 mun=20
mobility tmun=2.0
```

- 关键字归属（写错卡就报未知关键字）**[已核实]**：`user.material=` 在 **REGION** 卡
  （`atlas.key:327`，另 ELECTRODE 卡 `:591` 也有），`user.default=` / `user.group=` 在 **MATERIAL** 卡
  （`atlas.key:2925 / :2926`）。上面模板的写法是对的，但别把 `user.material` 写到 `material` 语句上。
- **类型陷阱**：`tcon.const` 是 **LOG 开关**（`atlas.key:2980 tcon.const LOG 1 f`），
  `tc.const` 才是 **NUM 数值**（`atlas.key:2036 tc.const NUM 79 -999`）。
  **绝对不要写 `tcon.const=0.13`**，正确写法是 `tcon.const tc.const=0.13`（一个裸开关 + 一个赋值）。
- `user.default=GaN` 只是**借 GaN 的模型骨架**（温度指数、复合模型形式），不代表物理等同 GaN；
  凡是你关心的量（`eg300 / affinity / nc300 / nv300 / permittivity / mun / tc.const`）都必须显式覆盖。
- 官方卡里的 `mup=50` **不是物理值**，只是让求解器有一个非零空穴迁移率。β-Ga2O3 空穴自陷，
  报告里不要把它当成真实空穴输运结论。**不要**在 β-Ga2O3 上做需要真实双极输运的结论（如电导调制）。
- `tc.const=0.13` 是官方例子取的各向同性等效值（关键字 **[已核实: atlas.key:2036]**，
  数值逐字来自 `Other_Power_ex08.in:51`）。真实 β-Ga2O3 κ 各向异性接近 2 倍以上；
  若结论对峰值温度敏感，需要按晶向重取并在报告里注明 **[待核实：κ 各向异性数值需文献]**。
  若确实要做方向性 κ，ATLAS 有 `tc.aniso`（**[已核实: atlas.key:2394 tc.aniso NUM 362 0.0]**，MATERIAL 卡）
  与 `perm.aniso`（`atlas.key:2393`），不必只能用各向同性的 0.13。
- **不要**在 β-Ga2O3 上写 `polarization` / `calc.strain`——没有这个物理，开了只会引入伪界面电荷。

**AlGaN/GaN HEMT & p-GaN HEMT**

- 极化必须显式开，**且要给 scale**
  **[已核实: atlas.key:1189 polarization LOG 181 / :1195 calc.strain LOG 184 / :1743 polar.scale NUM 167 1.0 /
  :1772 psp.scale NUM 189 1.0 / :1825 piezo.scale NUM 239 1.0 / :975 print LOG 12（均在 MODELS 卡 962-1947）；
  第一行逐字等于 `GaN_Power_ex07.in:139` 与 `GaN_Power_ex08.in:134`]**：

```silvaco
models polarization calc.strain polar.scale=0.8 print
# 或分开缩放自发/压电分量：
models calc.strain polarization psp.scale=0.6 piezo.scale=0.6 print
# 例子中还出现过 tensor.scale（张量分量缩放）：
# models polarization calc.strain tensor.scale=0 psp.scale=0.8 piezo.scale=0.8
```

  这五个 scale 参数在 **REGION 卡上同样存在**（`atlas.key:212/219/242/273/278`），需要分区域缩放时用得上。

  `polar.scale` 在官方例子里从 `0.15` 到 `1.0` 都出现过——它是**校准旋钮**（补偿表面态/界面钉扎），
  不是物理常数。选值必须能追溯到"用它把 Vth/Ns 校准到了某个实测/文献值"，不能随手填 1.0。

- 2DEG 面密度可以从极化电荷积分反推来自检——这**不是"思路"，是可直接照抄的 EXTRACT 语句**
  **[已核实：逐字来自 `GaN/GaN_Power_ex01/GaN_Power_ex01_aux.in:43-46`]**：

```silvaco
extract init inf="GaN_Power_ex01.str"
extract name="AlGaN_interface_charge" \
 (1e-4/1.62019e-19) * area from curve(depth,impurity="polarization charge conc" \
 material="All" x.val=0.5) where x.min=0.015 and x.max=0.025
```

  量名就是 `"polarization charge conc"`，除的是 q=1.62019e-19，`1e-4` 是 µm→cm 的单位因子；
  反号（另一侧界面）时把系数写成 `(-1e-4/1.62019e-19)`。做完结构后先验一次 Ns 量级，
  比直接看 Id 更能定位"极化没生效"。
  （这个量名是 TonyPlot/EXTRACT 层的曲线名，`atlas.key` 里查不到属正常——`atlas.key` 只收语句参数。）
- p-GaN 栅：Vth 由 pGaN 厚度、Mg 有效受主浓度、AlGaN barrier 厚度/组分**共同**决定，改一个必须重报另外两个。
  官方例子用 `trap` 描述 pGaN 层的施主/受主深能级
  **[已核实: atlas.key:7112 name CHAR 13 / :6964 acceptor LOG 2 / :6963 donor LOG 1 / :6995 density NUM 7 /
  :6989 e.level NUM 1 / :6990 taun NUM 2 / :6991 taup NUM 3（TRAP 卡 6962-7115）；
  逐字来自 `GaN_Power_ex12.in:184-185`]**：

```silvaco
trap name=pGaN acceptor density=4e16   e.level=0.85 degen=2 taun=0.13 taup=1
trap name=pGaN donor    density=3.2e16 e.level=0.49 degen=2 taun=0.13 taup=1
```

  - `degen` 是 `degen.fac` 的**唯一前缀缩写**（`atlas.key:6994 degen.fac NUM 6`，裸 `degen` 本身无独立行）；
    两种写法在官方 deck 里都出现过。
  - ⚠ 源例子那两行末尾还有 `label=pgan_acc` / `label=pgan_don`，**`label` 不是 TRAP 卡参数**
    （`atlas.key` 里只有独立的 LABEL 语句 `:5648`）。上面已经删掉了，**再去抄例子时不要把它带回来**。

- 栅金属功函数是第一顺位敏感参数。**规范写法是 `contact number=<n> workfunc=<eV>`**
  **[已核实: atlas.key:4461 number NUM 1 / :4462 workfunc NUM 2 -999（CONTACT 卡 4460-4605）]**。
  官方 deck 里写的 `contact num=2 workf=5.23`（`Other_Power_ex08.in:63`）是前缀缩写，能跑，
  但 **`num` / `workf` 在 CONTACT 卡上没有自己的 `atlas.key` 行**（裸 `workf` 那一行 `:1962` 属于 MATERIAL 卡），
  grep 不到，所以本项目统一写全称。p-GaN 栅常取接近 5.8 eV 量级
  **[待核实：以所参照的例子/文献为准。本机唯一能查到的实数是 Ga2O3 MOSFET 的 5.23 eV，栅叠层不同，不可挪用]**。

**4H-SiC**

- 碰撞电离有专用各向异性参数集
  **[已核实: atlas.key:5394 aniso LOG 22 f / :5395 sic4h0001 LOG 23 **t** / :5396 sic4h1120 LOG 24 f /
  :5375 e.side LOG 9 / :5368 material CHAR 1 / :5383 okuto LOG 17 / :5393 gradqfl LOG 21（IMPACT 卡 5367-5619）]**：

```silvaco
impact aniso sic4h0001 e.side                    # SiC 各向异性（0001 面）
impact material=4H-SiC okuto gradqfl             # Okuto 模型
# impact material=4H-SiC selberherr e.side       # ✗ 未核实：selberherr 不在 IMPACT 卡上
```

  - ⚠ **`selberherr` 不是 IMPACT 卡的参数**（**未核实：`atlas.key` 中 `selberherr` 只有一行 `:1482`，
    属于 **MODELS** 卡 962-1947）。IMPACT 卡上的 Selberherr 开关叫 **`selb`**
    （**[已核实: atlas.key:5370 selb LOG 3 **t**]**，而且**默认就是 t**）。
    shipped deck 里写 `IMPACT ... selberherr` 的（`SiC_Power_ex08` / `Adv_CMOS_ex06/07` /
    `Silicon_Power_ex01/02`）**全部是 `GO victorydevice` deck**，那是 Victory Device 语法，ATLAS 不认。
  - `sic4h0001` 的缺省值是 **t**：一旦开了 `aniso`，它就是默认取向，写出来是"自我文档"而非"激活"。
    另一个取向是 **`sic4h1120`**（不是 `sic4h1100`——那个拼法只存在于 MOBILITY 卡的 `sic4h1100.n/.p`）。
  - 相配的 0001 面系数 `ae0001 / ah0001 / be0001 / bh0001` 也在 IMPACT 卡上（NUM 100-103，有真实缺省值）。
  - 做 SiC BV 不要直接套 Si 的 `impact selb` 默认系数。
- SiC 是唯一双极性好用的宽禁带候选，SEB 里要注意寄生 BJT/闩锁路径，别只看 MOS 沟道。

**Diamond**

- **Diamond 是 ATLAS 内建材料，不需要走 Ga2O3 那套 user-defined 流程**
  **[已核实: atlas.key:287 diamond LOG 33（REGION 143-339）/ :3014（MATERIAL 1948-3072）/ :5802（MOBILITY 5724-6474）；
  manual Appendix B "Material Systems" 列有 DIAMOND]**。早期版本写"需按 user-defined material 处理"是错的。
  直接写即可，manual 给的可用语法：

```silvaco
material mat=Diamond tcon.power tc.npow=2 tc.const=1.4     # 温度相关 κ，manual 原文示例
```

- 要覆盖具体参数时照常用 MATERIAL 卡的 `eg300 / affinity / permittivity / tc.const`
  **[已核实: atlas.key:1952 eg300 NUM 3 / :2036 tc.const NUM 79]**（`permittivity`/`affinity` 两关键字
  在 MATERIAL 卡上存在无争议，但行号本文旧记录 :1953/:1961 与 `device-physics-and-solver.md` §1.2 的
  :1961/:1953 **互为镜像**，必有一边抄错，**[待 atlas.key 复核]**），
  但**不必**再声明 `user.default` / `user.group`。
- κ ~20 W/cm·K，自热几乎不是瓶颈；反过来说，若你在 diamond 上算出显著温升，先怀疑热边界写错了。

### 2.3 宽禁带公共 `models` 起手式 **[候选]**

宽禁带禁带宽、本征载流子极低，Boltzmann + 完全电离常常给出错误的费米能级和杂质激活率：

```silvaco
# 起手（先跑通基线，再逐项加）：
models fermi incomplete bgn srh print
# 迁移率二选一（先低阶）：
models   conmob fldmob           # [默认] 先用简单场相关，收敛快
mobility fmct.n fmct.p           # 高场 FMCT 模型 [待核实：按 examples 中同材料例子选]
```

⚠ **`models fmct` 是错的**（**未核实：MODELS 卡 962-1947 内 `fmct` 出现次数为 0；
`atlas.key` 中根本没有裸 `fmct` 这个关键字**）。真实关键字是 **MOBILITY 卡**上的
`fmct.n` / `fmct.p`（**[已核实: atlas.key:5784 fmct.n LOG 56 f / :5785 fmct.p LOG 57 f（MOBILITY 5724-6474）]**，
配套系数 `mu1n.fmct / mu1p.fmct / mu2n.fmct / mu2p.fmct` 在 `:6221-6224`）。写法是 `mobility fmct.n fmct.p`。

对应源技能里的 `ExtendedPrecision(80)`，在 ATLAS 中没有一一对应的"提精度"开关；等价手段是
**降低求解器要分辨的载流子浓度下限 + 放宽迭代上限**：

```silvaco
method newton climit=1e-4 itlimit=100 maxtraps=10
# 需要低温/自热时再按 §7.3 配 min.temp / max.temp
```

- `climit=1e-4` **[已核实: atlas.key:688 climit NUM 51 10000]** —— ⚠ **`climit` 不是残差/收敛容差**，
  详见 §7.3 的完整说明；这里只强调一点：**不要说"climit 越小越严格"**。
- `itlimit=100` **[已核实: atlas.key:644 itlimit NUM 1 25]**（缺省 25，100 是放宽）。
- `maxtraps=10` **[已核实: atlas.key:666 maxtraps NUM 31 4]**（缺省 4；manual 规定取值范围 **1–10**，见 §9.3）。
- 早期版本把 `min.temp=3.0 max.temp=1000.0` 放在这条"通用起手式"里是不合适的：
  `min.temp` 缺省 120 K，调到 3.0 只对**低温/深冷**仿真有意义（其出处 `Bulk_ex03` 就是深冷 deck）；
  `max.temp` 缺省 **2000 K**，写 1000.0 是**收紧**而不是放宽。两者已移到 §7.3 并改正。

---

## 3. 单粒子入射：`singleeventupset` 两条路线

### 3.1 关键字白名单（来自 `atlas.key` 5.40.0.R）**[已核实：整卡逐行核对，19/19 全中]**

`SINGLEEVENTUPSET` 卡在 `atlas.key` 的 **7999–8025** 行（8026 起是 `CURVETRACE`）：

```
singleeventupset                                    # atlas.key:7999  card 51
  CHAR : entrypoint(1)  exitpoint(2)  f.seu(3)  device(4)=structure(4)
  NUM  : radius(1)  density(2)  b.density(3)  t0(4)  tc(5)
         a1(6) a2(7) a3(8) a4(9)  b1(10) b2(11) b3(12) b4(13)
         tfinal.seu(14)  beam.radius(15)
  LOG  : pcunits(1)  radialgauss(2)  radialsin2(3)  uniform(4)  rescale(5)
```

（`device` 与 `structure` 共用槽位 4，是同义词；所有 NUM 缺省均为 `-999` 即"未设"。）

**重要更正 [已核实：全文件 grep `b.time` 返回 0 行]**：本项目早期映射表里写的 `b.time`
**在 5.40.0.R 的 `atlas.key` 中确实不存在**。时间参数是 `t0`（峰值产生率时刻）与 `tc`（特征衰减时间）。

`entrypoint`/`exitpoint` 可缩写为 `entry`/`exit`（ATLAS 关键字前缀匹配），官方例子两种写法都有。
⚠ 但 **`exit` 同时也是 DeckBuild/ATLAS 的顶层终止语句**（`atlas.key:38 exit 3`），
为免歧义本项目**优先写全称 `entrypoint=` / `exitpoint=`**。

### 3.2 路线 A：内建高斯径迹 **[默认]**

坐标串在 2D 是 `"x,y"`，在 3D 是 `"x,y,z"`（单位 µm）。

```silvaco
# --- 2D，直接用 LET（pC/µm）---  [已核实：Photodiode_ex13 风格]
#     （早期版本标"Rad_Rel_ex02 风格"是引错：ex02 用的是 entrypoint=/exitpoint= 全称）
set LET=75
set density=0.006038*$LET          # β-Ga2O3 系数，推导见 §4
singleeventupset entry="0, 1" exit="0, 2" \
  radius=0.2 b.density=$density pcunits t0=5e-12 tc=1e-13

# --- 3D，径向高斯 ---            [已核实：Rad_Rel_ex03 / ex09 风格]
#     （早期版本写 "ex07/ex09"：ex07 里根本没有 radialgauss，它是下面的 device=AM3 混合模式 deck）
singleeventupset entrypoint="0,0,0" exitpoint="0,8.5,0" radialgauss \
  b.density=$density pcunits radius=0.07 t0=1e-14 tc=1e-15

# --- 3D，直接给体产生密度（cm^-3，不带 pcunits）--- [已核实：Rad_Rel_ex01，逐字一致]
singleeventupset entry="$x1,$y1,$z1" exit="$x2,$y2,$z2" \
  radius=0.04 density=1.e21 t0=1.e-10 tc=2.e-11

# --- 混合模式，打在指定子器件上 --- [已核实：Rad_Rel_ex07]
#     （早期版本标 Rad_Rel_ex03 是引错：ex03 里没有任何 device=）
singleeventupset entrypoint="$strike,0,0" exitpoint="$Xexit,$Yexit,$Zexit" \
  b.density=$density pcunits radius=0.02 t0=5e-12 tc=2e-13 device=AM3
```

参数含义与选法：

| 参数 | 含义 | 选法 |
|---|---|---|
| `entrypoint` / `exitpoint` | 径迹入射点 / 出射点 | **出射点要落在结构外**（如 `z2=20.0` 而器件只有几 µm），保证径迹贯穿；入射点同理取到结构外或表面上方 |
| `radius` | 径迹半径 (µm) | 典型 0.02–0.2。**网格必须能分辨**：径迹核心至少 3–5 个节点跨过 `radius`，否则电荷被数值抹平 |
| `density` | 体产生密度 `cm^-3`（**不加** `pcunits`） | 需要自己把 LET 折算成体密度，易错，仅在复现老 deck 时用 |
| `b.density` + `pcunits` | 线电荷密度 `pC/µm` | **[默认]** 与实验 LET 直接对应，见 §4 |
| `t0` | 产生率峰值时刻 (s) | 必须**晚于**偏置建立完成的时刻，见 §7 |
| `tc` | 特征衰减时间 (s) | 常取 `t0` 的 1/10 ~ 1/50（例子里 `t0=5e-12, tc=1e-13`；`t0=1e-10, tc=2e-11`） |
| `radialgauss` / `radialsin2` / `uniform` | 径向剖面 | **[默认] `radialgauss`**（高斯，最接近实际）；`uniform` 只用于对比/调试 |
| `beam.radius` / `a1..a4` / `b1..b4` / `tfinal.seu` / `rescale` | 高级径迹整形 | **[已核实：关键字存在，见 §3.1 白名单]** + **[待核实：用法]**——本机 examples 中**无任何 deck 使用**，需 manual 核对后再用 |

配套的求解器开关：

```silvaco
# ✅ 本项目推荐（每个 token 均可在 atlas.key 的 METHOD 卡 643-961 内 grep 到）
method bicgst seu.integrate climit=1e-4 dt.min=1e-17 maxtraps=10
```

**[已核实: atlas.key:851 bicgst LOG 50 f / :943 seu.integrate LOG 135 f / :688 climit NUM 51 10000 /
:665 dt.min NUM 30 -999 / :666 maxtraps NUM 31 4 / :930 pam.bicgst LOG 122 f（均在 METHOD 卡 643-961）]**

> ### ⚠ 早期版本的这一行有 4 个不存在的参数（保留在此以示警戒）
>
> ```silvaco
> # ✗ 不要用：
> # method newton pam.bicgst lte.timestep seu.integrate \
> #   seu.max.rad=0.2 seu.max.inc=1.0 seu.n.inc=30
> ```
>
> | token | 结论 |
> |---|---|
> | `newton` | **[已核实: atlas.key:831 newton LOG 31 t]**（本来就是缺省） |
> | `pam.bicgst` | **[已核实: atlas.key:930 pam.bicgst LOG 122 f]** |
> | `seu.integrate` | **[已核实: atlas.key:943 seu.integrate LOG 135 f]** |
> | `lte.timestep` | **[未核实：`grep -n -i 'lte.timestep' atlas.key` 返回 0 行 —— ATLAS 5.40.0.R 中不存在]** |
> | `seu.max.rad` | **[未核实：grep 返回 0 行 —— 不存在]** |
> | `seu.max.inc` | **[未核实：grep 返回 0 行 —— 不存在]** |
> | `seu.n.inc` | **[未核实：grep 返回 0 行 —— 不存在]** |
>
> 来源已定位：这四个是从 **`Rad_Rel_ex01.in:93`** 抄来的，而 `Rad_Rel_ex01` 是
> **`GO victorydevice`** deck，不是 ATLAS deck（见 §0.1）。这是本文件全部缺陷的同一个根因。

`seu.integrate` 让 ATLAS 对径迹产生项做子网格积分——**打单粒子必开**，否则粗网格下总电荷严重偏低。
它是一个**裸开关，没有配套的精细度参数**：早期版本声称由 `seu.max.rad / seu.max.inc / seu.n.inc`
控制积分精细度，这三个参数在 ATLAS 中并不存在，该说法一并作废 **[未核实]**。
真正能控制积分分辨率的是**网格密度**本身（径迹核心 3–5 个节点跨过 `radius`，见上表）。

### 3.3 路线 B：`F.SEU` C 解释器自定义时空分布 **[候选]**

当需要非高斯剖面、多条径迹叠加、径迹沿深度变 LET（Bragg 峰）、或与外部径迹结构耦合时用。
入口签名 **[已核实：逐字符匹配 `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/template.lib:3145`；
`f.seu` 见 atlas.key:8001 f.seu CHAR 3]**：

```c
/*
 * SEU generation rate as a function of position and time (3D)
 * Statement: SINGLEEVENTUPSET
 * Parameter: F.SEU
 * Arguments:
 *   x, y, z   location (microns)
 *   time      time (seconds)
 *   *rat      generation rate per cc per sec.   <-- 你要填这个
 */
int seu(double x, double y, double z, double time, double *rat)
{
    return(0);   /* 0 = OK, non-zero = error */
}
```

deck 侧调用：

```silvaco
singleeventupset f.seu="seu_track.c"
```

要点：

- 返回的是**体产生率 `cm^-3 s^-1`**，不是电荷、不是线密度。归一化必须自己做：
  对 `rat` 在空间和时间上积分应等于总 ehp 数。写完后**务必**用一次积分自检。
- 2D 仿真里 `z` 仍会被传入，一般忽略即可（但不要在函数里对 `z` 做未定义行为的假设）。
- `template.lib` 就是官方模板库，**复制它里面的函数骨架，不要凭记忆写签名**：

```bash
grep -n -A20 'int seu(' /atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/template.lib
```

- C 解释器每个网格点每个时间步都要调用，写得复杂会显著拖慢；能用内建高斯就别用 `F.SEU`。

### 3.4 选路线的判据

| 需求 | 选择 |
|---|---|
| 单条直径迹、固定 LET、扫电压/扫 LET | **[默认] 内建 `singleeventupset` + `radialgauss` + `pcunits`** |
| 与实验 LET 表直接对齐 | 内建 + `b.density` + `pcunits` |
| 多径迹 / Bragg 峰 / 任意剖面 | `F.SEU=<file>.c` |
| 混合模式电路里打某一个器件 | 内建 + `device=<子器件名>` |

---

## 4. LET 单位换算（必须写进报告，不能只给一个数）

### 4.1 完整公式

```
LET(ehp/µm) = LET(MeV·cm²/mg) × ρ(mg/cm³) × 1e6(MeV→eV) ÷ Ei(eV) × 1e-4(cm→µm)

Q(pC/µm)   = LET(ehp/µm) × 1.602e-19 (C/ehp) × 1e12 (C→pC)
```

合并成一个系数，方便直接写进 deck：

```
coef_ehp = 100 × ρ(mg/cm³) / Ei(eV)          [ (ehp/µm) per (MeV·cm²/mg) ]
coef_pC  = 1.602e-5 × ρ(mg/cm³) / Ei(eV)     [ (pC/µm)  per (MeV·cm²/mg) ]

deck 里：  set LET=<MeV·cm²/mg>
          set density=coef_pC*$LET
          singleeventupset ... b.density=$density pcunits
```

**公式自检（用官方例子反推）** **[已核实：`grep -rhi '0.01035' examples/deckbuild/5.2.40.R --include='*.in'`
→ `SET density=0.01035*$LET`]**：对 Si：ρ=2.329 g/cm³=2329 mg/cm³，Ei=3.6 eV，
`coef_pC = 1.602e-5 × 2329 / 3.6 = 1.0363e-2` ≈ **0.01035** ✓。
说明上面的公式与 Silvaco 官方口径一致，可以放心用到其它材料。
（这一条的"已核实"指的是**与官方常数 0.01035 吻合**，不是指某条 `atlas.key` 行——
算术推导本来就不在 `atlas.key` 的管辖范围内。）

`b.density` + `pcunits` = **pC/µm** 这个单位约定，也由 Silvaco 自己的例子说明文档确认
**[已核实：examples 中 `*.html` 原文 "the LET value needs to be multiplied by 0.01035 for silicon material …
the units of the strike are specified to be these same pico coulomb units, by the parameter *pcunits*"]**。
对照 §3.2 第三段：**不带 `pcunits` 的 `density=` 是 cm⁻³**，两者差十几个数量级。

### 4.2 算例：β-Ga2O3，LET = 75 MeV·cm²/mg **[本项目默认工况]**

给定 ρ = 5.88 g/cm³ = 5880 mg/cm³，Ei = 15.6 eV：

```
LET(ehp/µm) = 75 × 5880 × 1e6 / 15.6 × 1e-4
            = 75 × 3.769e4
            = 2.827e6  ehp/µm       ≈ 2.83e6 ehp/µm

Q(pC/µm)    = 2.827e6 × 1.602e-19 × 1e12
            = 4.529e-13 C/µm × 1e12
            = 0.4529 pC/µm          ≈ 0.453 pC/µm
```

写进 deck：

```silvaco
set LET=75                       # MeV*cm2/mg
set density=0.006038*$LET        # beta-Ga2O3: 1.602e-5 * 5880 / 15.6
                                 # -> 0.453 pC/um at LET=75
singleeventupset entry="$xin,$yin" exit="$xout,$yout" radialgauss \
  b.density=$density pcunits radius=0.05 t0=1e-11 tc=5e-13
```

### 4.3 各候选材料的换算系数

| 材料 | ρ (g/cm³) | Ei (eV) | `coef_ehp` (ehp/µm per LET) | `coef_pC` (pC/µm per LET) | 来源 |
|---|---|---|---|---|---|
| Si（校验基准） | 2.329 | 3.6 | 6.469e4 | **0.01036**（官方 0.01035） | **[已核实：examples 中 `SET density=0.01035*$LET`，见 §4.1 自检]** |
| **β-Ga2O3 [默认]** | 5.88 | 15.6 | 3.769e4 | **0.006038** | 本项目冻结值 |
| GaN | 6.15 | ~8.9 | 6.91e4 | 0.01107 | **[待核实：Ei 需文献]** |
| 4H-SiC | 3.21 | ~7.8 | 4.12e4 | 0.006593 | **[待核实：Ei 需文献]** |
| Diamond | 3.515 | ~13 | 2.70e4 | 0.004332 | **[待核实：Ei 需文献]** |

`Ei` 的量级自检用 Klein 经验式 `Ei ≈ 2.8·Eg + (0.5~1.0) eV`：
β-Ga2O3 Eg=4.8 → 14.0–14.4 eV，与本项目采用的 15.6 eV 同量级，可接受；
**但报告里必须写清 Ei 的出处**，不能只写"取 15.6"。

多层结构（如 Ga2O3-on-substrate、AlGaN/GaN/Si）中每层 ρ、Ei 都不同。ATLAS 的
`b.density` 是**全局单值**，严格处理需要 `F.SEU` 分层给 `rat`；若只关心有源层，
按有源层材料取系数并在报告中说明这一简化。

---

## 5. BV 仿真流程（宽禁带尤其要按顺序来）

### 5.1 分阶段，不要一步到位

1. **先不开碰撞电离**跑通阻断态：只有 `models` + `method`，`solve` 逐步升 Vd，确认场分布合理、
   没有伪泄漏路径（`output con.band val.band flowline` 后在 TonyPlot 里看电场与流线）。
2. **再开 `impact`**。宽禁带材料一定要用材料专用系数：

```silvaco
impact aniso sic4h0001 e.side                  # SiC 各向异性参数集
impact material=4H-SiC okuto gradqfl           # SiC，Okuto 模型
impact name=Channel selb e.side gradqfl \
  an1=2.98e8 an2=2.98e8 ap1=2.23e7 ap2=2.23e7 \
  bn1=3.44e7 bn2=3.44e7 bp1=2.7e8 bp2=2.7e8    # GaN 沟道系数（数值取自例子，见下方警告）
impact selb                                    # 通用 Selberherr（缺省即 t，宽禁带不要直接套 Si 系数）
```

**[已核实（IMPACT 卡 = atlas.key 5367-5619）: :5368 material CHAR 1 / :5370 selb LOG 3 t / :5372 name CHAR 3 /
:5375 e.side LOG 9 / :5383 okuto LOG 17 / :5393 gradqfl LOG 21 / :5394 aniso LOG 22 / :5395 sic4h0001 LOG 23 t]**
`an1/an2/bn1/bn2/ap1/ap2/bp1/bp2` 八个关键字在 IMPACT 卡上存在、缺省值（an1 7.03e5 / bn1 1.231e6 /
ap1 6.71e5 / bp1 1.693e6）无争议，但其 **atlas.key 行号**本文旧记录（:5419–:5426 连续排布）与
`device-physics-and-solver.md` §4（an2 :5421 / bn1 :5422 / bn2 :5424）**互斥，至多一组正确**，
**[待 atlas.key 复核]**。
（别名：`an1=n.ioniza`、`bn1=ecn.ii`、`ap1=p.ioniza`、`bp1=ecp.ii`。）

> ### ⚠ 早期版本这一段有两个不存在的 IMPACT 参数（保留以示警戒）
>
> ```silvaco
> # ✗ 不要用：
> # impact name=Channel selb e.side gradqfl hysteresis=1 e.min=3e5 ...
> # impact material=4H-SiC selberherr e.side
> ```
>
> | token | 结论 |
> |---|---|
> | `hysteresis=1` | **[未核实：`grep -n -i 'hysteresis' atlas.key` 返回 0 行 —— ATLAS 中不存在]** |
> | `e.min=3e5` | **[未核实：`grep -n -i 'e\.min' atlas.key` 返回 0 行 —— ATLAS 中不存在]** |
> | `selberherr`（在 IMPACT 上） | **[未核实：`atlas.key:1482 selberherr LOG 449` 属 **MODELS** 卡，不在 IMPACT 卡上]**；IMPACT 上要写 `selb` |
>
> 来源已定位：这两个 token 逐字来自 `GaN_Power_ex12.in` / `GaN_Power_ex13.in`，
> 而它们是 **`GO victorydevice`** deck（见 §0.1）。**Victory Device 的 IMPACT 语法与 ATLAS 不通用。**
> 同一行里的 `an1/an2/ap1/ap2/bn1/bn2/bp1/bp2` 数值仍可参考（这些关键字在 ATLAS IMPACT 卡上确实存在），
> 但 `hysteresis` / `e.min` 必须删掉。
>
> **不要**拿 IMPACT 卡上的 `jnx.min / jpx.min / jny.min / …`（NUM 108-113）去顶替 `e.min`——
> 那是**电流密度下限**，不是电场下限，物理含义完全不同 **[已核实：两者在 atlas.key 中是不同的参数族]**。

  - **原来那句"`e.min` 设一个下限场…对收敛帮助很大"的建议一并作废** **[未核实]**：ATLAS 没有这个开关。
    低场区电离噪声的正解是用 `gradqfl` + 合理网格，不是靠一个不存在的截断场。
  - `gradqfl` 用准费米梯度而不是纯电场，能缓解高场低载流子区的数值噪声（对应源技能里
    "GaN BV 优先 `eAvalanche` 而不是完整 Avalanche"的同一思路）**[已核实: atlas.key:5393]**。
  - β-Ga2O3 是 user-defined material，**没有内建电离系数**（`atlas.key` 中确实查不到任何 Ga2O3 材料标志，
    这一点与 `diamond` 不同），必须显式给 `an1/ap1/bn1/bp1`——**关键字本身已核实在 IMPACT 卡上
    （具体 atlas.key 行号本文与 `device-physics-and-solver.md` 记录互斥，见上文 **[待 atlas.key 复核]** 注），
    但 Ga2O3 的具体数值 [待核实：需文献并在报告中注明出处]**。
  - ⚠ 索引 1 / 2 的含义（manual 原文）：**index 1（an1/bn1/ap1/bp1）对应 E > `egran` 的高场段，
    index 2 对应 E < `egran` 的低场段**（`egran` 见 `atlas.key:5435`，缺省 4.0e5 V/cm）。别记反。

3. **compliance 保护**：不加 compliance，击穿点会让 Newton 直接崩掉且看不到拐点。
   **[已核实（SOLVE 卡 = atlas.key 3073-4459）: :3257 vstep NUM 11 / :3282 vfinal NUM 35 /
   :3191 name CHAR 4 / :3290 compliance NUM 36 / :3194 cname CHAR 7]**

```silvaco
solve vstep=1 vfinal=1200 name=drain compliance=1e-6 cname=drain
# 双极性/负电压：compliance=-1e-3 cname=anode
```

   注：官方 deck 普遍写缩写 `compl=`，能跑（`compliance` 是唯一前缀匹配，`e.compliance` 以 `e.` 开头不冲突），
   但 **`compl` 在 `atlas.key` 里没有自己的行**，grep 不到，本项目统一写全称 `compliance=`。

4. **逐步 vstep**：接近击穿时把步长压小，分段写：

```silvaco
solve vstep=20 vfinal=800  name=drain compliance=1e-6 cname=drain
solve vstep=5  vfinal=1000 name=drain compliance=1e-6 cname=drain
solve vstep=1  vfinal=1200 name=drain compliance=1e-6 cname=drain
```

### 5.2 BV 判据 **[候选]**

| 判据 | 写法 | 适用 |
|---|---|---|
| **[默认] 电流阈值截距** | `extract.curve name=BV_[V] expression="intercept(y=1e-6, abs(curve.<name>))"` **[已核实：examples 中逐字存在 `EXTRACT.curve name = BV_[V] expression = "intercept(y = 1.0e-6, abs(curve.Secondary_breakdown))"`]** | 与实验"额定漏电"口径一致，最常用 |
| 电离积分 = 1 | 对 `curve.iava` 取截距 **[已核实：examples 中逐字 `EXTRACT.CURVE name=Vbreakdown_4k expression="intercept(y=1e-4, curve.iava)"`]** | 物理判据，抗网格影响 |
| compliance 触发点 | 记 `compliance` 被触发时的 V | 快，但强依赖 compliance 取值，只做粗筛 |
| `curvetrace` 曲线追踪 | `curvetrace contr.name=... step.init= end.val= ...` **[已核实：关键字存在 — atlas.key:8026 curvetrace card 52；contr.name CHAR 1 / step.init NUM 15 缺省 0.1 / end.val NUM 17 缺省 0.0]**，但本机 5.2.40.R examples 中 **0 个 `.in` 使用**，**[待核实：用法]** | 需要过击穿拐点/负阻段（snapback）时 |

> `EXTRACT` / `EXTRACT.CURVE` 的**权威不是 `atlas.key`**：`atlas.key:33` 只把 `extract` 登记为一个
> 无参数的透传语句，语法属于 **DeckBuild 层**。上表这几条的"已核实"依据是 **examples 中逐字出现**。
>
> `curve.<name>` 里的 `<name>` 是 **log/曲线名**（由 `log outfile=` / `extract` 注册），不一定是电极名。
>
> 做 snapback 时 examples 里无例可抄，`curvetrace` 上真正要用的模式开关是
> `volt.cont` / `curr.cont` / `step.cont`（LOG 2/3/4）与 `turningpoint`（LOG 1），以及 `beg.val`（NUM 16）。

**必须**同时存 `.str` 快照看空间证据：

```silvaco
save outf="BV_800V.str"
output con.band val.band flowline e.field impact
```

BV 报告里要给：BV 数值 + 判据 + 击穿点位置（体内 / 栅角 / 场板端 / 终端）。
只给数不给位置的 BV 结论没有价值。

---

## 6. SEB 方法论

### 6.1 流程

1. 先完成 IdVg / IdVd 基线校准，确认器件在直流下合理。
2. 完成 BV（§5），知道测试电压相对 BV 的比例。
3. 选入射位置：高场区、场板/终端末端、栅角、外延/衬底界面——每个位置一个 case。
4. 固定 LET 扫 `V_load`，或固定 `V_load` 扫 LET。**先做粗筛（3–4 个点定包围区间），再细分**。
5. 用瞬态电流是否回落、峰值晶格温度、时间步是否坍缩、`.str` 中的电流路径共同判定。

### 6.2 SEB 判据候选项 **[候选]**

**不要只用单一数字判定**，至少 `.log` 曲线 + `.str` 空间分布两条证据。

| # | 判据 | 观测量 | 说明 |
|---|---|---|---|
| 1 | **[默认] 电流持续上升不回落** | `.log` 中漏/阳极电流，瞬态末段仍单调上升 | 最直接的正反馈证据。要跑到足够长的 `tfinal`（至少到 1e-7~1e-6 s）才能区分"慢回落"与"不回落" |
| 2 | 峰值晶格温度超阈 | `probe lat.temp ... max` **[已核实: atlas.key:8164 lat.temp LOG 10 / :8156 max LOG 2（PROBE 卡 8119-8404）]** | 阈值按材料取（熔点/分解温度的某个比例），必须在报告里写死阈值来源 |
| 3 | 不可逆导通 | SEU 结束后重新 `solve` 直流，Id 不回到辐照前值 | 最贴近"烧毁"的工程定义，但要多跑一段，代价高 |
| 4 | 峰值电流比基线高 N 个量级 | `.log` peak/baseline | N 由项目定义（常用 1e3）；只做辅助 |
| 5 | 时间步坍缩到 `dt.min` | `.log` 里步长历史 | **数值信号，不是物理判据**。可能是 SEB，也可能是网格/模型问题，必须交叉验证 |
| 6 | 电流路径贯通 | `.str` 中 `flowline` / 电流矢量形成源-漏或阳-阴贯通通道 | 空间证据，最有说服力 |
| 7 | 碰撞电离集中在某点并自持 | `.str` 中 `impact` 场分布 | 机理证据（雪崩触发 vs 纯热失控） |

推荐的探针配置 **[已核实（PROBE 卡 = atlas.key 8119-8404）: :8164 lat.temp LOG 10 f / :8395 name CHAR 1 /
:8120 x NUM 1 0.0 / :8121 y NUM 2 0.0 / :8155 min LOG 1 / :8156 max LOG 2 /
:8123 x.max NUM 4 / :8125 x.min NUM 5 / :8127 y.min NUM 6 / :8129 y.max NUM 7]**：

```silvaco
# 点探针
probe lat.temp name="Tpeak_channel"  x=<x> y=<y>
probe lat.temp name="Tpeak_junction" x=<x> y=<y>
# 区域取极值（manual 22.48 明确支持 MIN | MAX | INTEGRATED + 区域盒）
probe lat.temp max x.min=.. x.max=.. y.min=.. y.max=.. name="Tmax_region"
```

manual 22.48 原文："PROBE allows you to output the value of several distributed quantities to the log file.
The value at a specified location **or the minimum, maximum, or integrated value within a specified area**
of the device will be saved to the log file at each bias or time point."
→ 原来标 **[待核实用法]** 的区域取极值写法**已升级为 [已核实]**，可以直接用（`name=` 实践上必填）。

⚠ **拼写陷阱**：ATLAS 的关键字是 **`max`**。examples 里能看到 `PROBE name="max-field" maximum ...`，
但那些是 Victory Device deck，且 **`maximum` 不是 `max` 的前缀**，在 ATLAS 里不合法 **[未核实：勿照抄 `maximum`]**。

### 6.3 测试电压选取

经验上 SEB 阈值扫描从 **BV 的 50–80%** 起步；若目标是阈值本身，逐步扫描直到判据 1
从"回落"翻转为"持续上升"，然后在翻转区间二分。**每个 case 只改一个变量**（电压或 LET），
否则无法归因。

---

## 7. 自热与热边界

### 7.1 打开热模型

```silvaco
models lat.temp print                                # 晶格热方程
material material=Ga2O3 tcon.const tc.const=0.13     # 材料热导率（各向同性常数）
material material=Al2O3 tcon.const tc.const=0.33
```

**[已核实: atlas.key:1019 lat.temp LOG 43 f / :975 print LOG 12 f（MODELS 卡 962-1947）；
:2897 material CHAR 2 / :2980 tcon.const LOG 1 f / :2036 tc.const NUM 79 -999（MATERIAL 卡 1948-3072）；
本块逐字来自 `Other_Power_ex08.in:49-52,55`]**
（⚠ `Other_Power_ex08` 是 **Victory Device** deck，见 §0.1；但以上每个 token 在 ATLAS 对应卡上都存在，可安全照抄。
本文件其它引用该 deck 的地方同此说明——**不要再把它称作"官方 ATLAS 例子"**。）

`tcon.const` + `tc.const=` 表示"用常数热导率"。若需要**温度相关 κ**，ATLAS 有一整族模型
**[已核实：升级自原 [待核实]。atlas.key:2980 tcon.const / :2981 tcon.power / :2982 tcon.polynom /
:2983 tcon.recipro / :3031 tcon.comp / :3063 tcon.almabulk（均 MATERIAL 卡 LOG）；
系数 :2038 tc.npow / :1994 tc.a / :1996 tc.b / :1998 tc.c / :2039 tc.d / :2040 tc.e / :2394 tc.aniso]**：

| 模型开关 | 形式 | 关键系数 |
|---|---|---|
| `tcon.const` | κ = `tc.const` | `tc.const`（别名 `tc.c0`） |
| `tcon.power` | κ(T) = `tc.const`·(T/300)^`tc.npow` | `tc.const`, `tc.npow` |
| `tcon.polynom` | 多项式 | `tc.a` `tc.b` `tc.c` `tc.d` `tc.e` |
| `tcon.recipro` | 倒数式 | 同上 |
| `tcon.comp` | 随组分变化（适用材料的缺省） | — |
| `tcon.almabulk` | ALMA 体材料库 | — |

manual 原文示例（可直接用于 Diamond）：`material mat=Diamond TCON.POWER TC.NPOW=2 TC.CONST=1.4`。
需要方向性 κ（β-Ga2O3 的强各向异性）时用 `tc.aniso`（`atlas.key:2394`，缺省 0.0）。

### 7.2 热接触候选项 **[候选]**

`thermcontact` 关键字白名单 **[已核实：整卡逐行核对，THERMCONTACT = `atlas.key` **7593–7614**]**：

```
thermcontact                            # atlas.key:7593  card 44
  LOG  : boundary(1) 默认 t   blackbody(2) f   modify(3) f
  NUM  : number(1)  x.min(2)  x.max(3)  y.min(4)  y.max(5)  alpha(6) 缺省 0
         ext.temper(7)=temperature(7) 缺省 300   elec.number(8) 缺省 0
         z.min(9)  z.max(10)  stefan(11) 缺省 5.67051e-12   beta(12) 缺省 0.0
  CHAR : name(1)  device(2)=structure(2)  f.contemp(3)
```

补充规则（manual 22.64 / 8.2.9，原白名单遗漏）：

- `number` **必须写**，且取值 **1–20**，多条 `thermcontact` 要**按递增顺序**给号。
- `device` 有同义词 **`structure`**（同槽位 2），原白名单漏了。
- `f.contemp` 指向一个 C 解释器文件，可把接触温度写成**时间的函数**——做 SEB 瞬态时很有用。
- `boundary` 缺省 t；对 2D 器件**内部**的热接触必须写 `^boundary`，否则该接触会被忽略。
- `modify` 允许在两条 `solve` 之间**改边界条件的类型/数值**（几何不能改）——SEB 中段换热沉时用。

**注意**：规范名是 `ext.temper`，`temperature` 是它的同名槽位（同为槽位 7）；官方 examples 里普遍写成缩写
`ext.temp=300`（唯一前缀匹配，等价）。两种都能跑，本项目统一写 **`ext.temp=300`** 与例子保持一致。

| 方案 | 写法 | 适用 |
|---|---|---|
| **[默认] 底部散热面 + 有限换热系数** | `thermcontact num=1 x.min=.. x.max=.. y.min=<bottom> y.max=<bottom> alpha=200 ext.temp=300` **[已核实: atlas.key:7597 number / :7598-7601 x.min/x.max/y.min/y.max / :7602 alpha / :7603 ext.temper；`alpha=200` 逐字来自 `Other_Power_ex08.in:58`]** | 最物理：`alpha` **单位 W/(cm²·K)** **[已核实：manual Table 8-8]**，代表衬底/贴片/散热器的等效热阻，`Rth = 1/alpha`（manual Eq 8-33） |
| 电极热接触 | `thermcontact num=2 elec=1 ext.temp=300` **[已核实: atlas.key:7605 elec.number NUM 8；逐字来自 `Other_Power_ex08.in:59-60`]** | 源/漏金属也散热；三条一起用（底部+源+漏）是该 Ga2O3 例子的做法 |
| 理想恒温面（**不写 `alpha`**） | `thermcontact num=1 y.min=0.5 y.max=0.5` **[已核实：写法本身；语义见右]** | **不写 `alpha` ⇒ ATLAS 走 Dirichlet 定温分支（manual Eq 8-31），即理想等温面**；温升会被**低估**，只用于快速探索 |
| 按名字绑定 | `thermcontact name=substrate ext.temp=300 alpha=1000` **[已核实: atlas.key:7610 name CHAR 1；该整行在两个 example deck 中逐字存在]** | **`name=` 绑定的是电极名（ELECTRODE），不是命名区域** **[已核实：manual 22.64 "Specifies an electrode name that the thermal contact is coincident with"]** |
| 黑体辐射 | `blackbody` + `stefan` **[已核实: atlas.key:7595 blackbody LOG 2 f / :7608 stefan NUM 11 5.67051e-12；manual Eq 8-34]** | 只在真空/高温封装场景。`stefan` 兼作**发射率旋钮**（非理想发射体时改它） |
| 边界热容（瞬态） | `beta=<J·cm⁻²·K⁻¹>` **[已核实: atlas.key:7609 beta NUM 12 0.0；manual Eq 8-35]** | ⚠ **`beta` 不是黑体参数**（早期版本把它和 `blackbody`/`stefan` 并列，是错的）。它是**瞬态边界热容**项，决定边界层多快吸收 ns 级热脉冲——**对 SEB 比 blackbody 更相关** |

> 总热流是 manual Eq 8-36：`ALPHA·(Tl−TEMPER) + BETA·dTl/dt + STEFAN·(Tl⁴−TEMPER⁴)`。
> 三项分别对应"有限换热系数 / 瞬态热容 / 辐射"，不要混为一谈。
>
> ### ⚠ 关于 `alpha` 缺省值的一处physics 更正
>
> `atlas.key:7602` 字面写着 `alpha NUM 6 0`，所以"缺省=0"作为**键文件事实**没错。
> 但早期版本据此推出的 **"`alpha=0` 即完美热沉"是物理上反的**：
> 既然 `Rth = 1/ALPHA`，`ALPHA=0` ⇒ `Rth = ∞` ⇒ **绝热**（最坏情况），不是完美热沉。
>
> 真实机制是另一回事：manual 8.2.9 原文 "Equation 8-32 is used **if a value is specified for** [alpha].
> **Otherwise, Equation 8-31 is used**" —— **不写** `alpha` 才会切到 Dirichlet 定温分支（Eq 8-31），
> 那才是理想等温面。0 在这里是"未提供"的哨兵值，不是一个真的通量系数。
> **结论不变（温升被低估、只用于快速探索），但理由必须改成"不写 alpha ⇒ 定温边界"。**

官方 Ga2O3 例子的完整热边界（可直接照抄改坐标）
**[已核实：逐字来自 `Other_Power_ex08.in:57-60`（"Wide Bandgap Ga2O3 MOSFET"）；
每个 token 均在 ATLAS `thermcontact` 卡 `atlas.key:7593-7613` 上存在。
⚠ 该 deck 跑的是 `GO victorydevice`，不是 ATLAS——语句可用，但别称它为 ATLAS 例子]**：

```silvaco
thermcontact num=1 x.min=-2.0 x.max=22.0 y.min=0.5 y.max=0.5 alpha=200 ext.temp=300
thermcontact num=2 elec=1 ext.temp=300
thermcontact num=3 elec=3 ext.temp=300
```

`alpha` 的量级决定一切：`alpha=200` 与 `alpha=1000` 能差出几十到上百 K 的峰值温升。
**`alpha` 必须来自封装/实测热阻反推，并写进报告**；它是 SEB 热判据的头号敏感参数。

### 7.3 热瞬态的 `method`

```silvaco
# SEB / 自热瞬态推荐（注意 max.temp 要往上抬，不是往下压）
method newton climit=1e-4 itlimit=100 maxtraps=10 max.temp=1e6
# 高压/自热强耦合首选块解法：
method block newton carriers=2 climit=1.0e-4
```

**[已核实（METHOD 卡 = atlas.key 643-961）: :831 newton LOG 31 t / :830 block LOG 30 t /
:729 carriers NUM 87 缺省 2 / :688 climit NUM 51 缺省 10000 / :644 itlimit NUM 1 缺省 25 /
:666 maxtraps NUM 31 缺省 4 / :710 min.temp NUM 70 缺省 **120.0** / :711 max.temp NUM 71 缺省 **2000.0**]**

#### ★ `climit` 的正确含义（本项目此前一直写错，必须改口径）

```
atlas.key:688     climit       NUM     51      10000
```

- **`climit` 不是残差/收敛容差**，"越小越严格"的说法是错的 **[更正]**。
  manual 原文："CLIMIT or CLIM.DD specify **minimal values of concentrations to be resolved by the solver**."
  它是 X-norm（载流子浓度相对更新量）里的**浓度归一化因子**。
- **`climit` 是无量纲的**；带 `cm⁻³` 单位的是 **`CLIM.DD`（同义别名 `CLIMIT.DD`）**
  **[已核实：manual p.1417 METHOD 参数表两个拼写并列（均 Real、默认 4.5e13 cm⁻³）；
  p.1426 原文 "CLIMIT.DD — This is an alias for CLIM.DD"]**（atlas.key 行号包内有
  :725 `clim.dd` 与 :726 `climit.dd` 两种记录——manual 既然两拼写并列为两个参数，
  这两行可能**同时存在**、各登记一个拼写，确切行号归属 **[待 atlas.key 复核]**）。
  换算是**四次方根**：`CLIM.DD = CLIMIT × (Nc·Nv)^(1/4)`
  **[已核实：manual p.1122 Eq 20-2/20-3，`c* = ⁴√(Nc·Nv)`；自检：Si 取 1e4 × (2.8e19×1.04e19)^(1/4)
  ≈ 4.1e13 ≈ 手册默认 4.5e13 ✓]**——早期版本写成 `4·sqrt(Nc·Nv)` 会差约 10 个数量级，已作废。
  **不要写"climit 单位 cm⁻³"。**
- **缺省 1e4；调小 = 让求解器去分辨更低的载流子浓度。**
- **`climit=1e-4` 是 manual 明确推荐的击穿设定，不是"收敛隐患"** **[已核实]**：
  manual 原文 "A value of **CLIMIT=1e-4 is recommended for all simulations of breakdown**,
  where the pre-breakdown current is small"，并给出配方 `IMPACT SELB` / `METHOD CLIMIT=1e-4`；
  反过来**不调小**才会得到 "false solution"。
  本机 examples 里 `climit=1e-4` 出现 **85 次**（远端全量树计数 [待复核]；本地镜像
  `d:\knowledge\exp25` 实测 79 次。另 `1.0e-4` 11 次、`1e-5` 10 次、`1e-6` 11 次），
  是整个例子树里最常见的取值；`Other_Power_ex08.in:66` 就是 `METHOD climit=1e-4 maxtraps=10`。
- 想直接用 cm⁻³ 口径就写 `clim.dd`（或其别名 `climit.dd`，manual p.1426 两者等价；
  Si 缺省 4.5e13 cm⁻³，manual p.1122：击穿建议降到 ~1e8 cm⁻³）。

#### `min.temp` / `max.temp`

`min.temp` / `max.temp` 是**求解器允许的温度范围**（Gummel 迭代中晶格温度的上下夹逼），不是物理边界。

- `max.temp` **缺省 2000 K**。⚠ 早期版本推荐的 `max.temp=1000.0` 其实是把上限**压低**了，
  与"放宽温度上限"的说法自相矛盾 **[更正]**。SEB 里峰值温度可能很高，压低上限会让求解器提前判失败。
  examples 中 `Rad_Rel_ex02.in:56` 用的是 `max.temp=1000000` **[已核实：逐字存在]**，
  即"实质取消上限"，这才是 SEB deck 该有的方向。
- `min.temp` **缺省 120 K**，manual 说它"should be set to suitably low temperature when doing
  **cryogenic** simulations"。⚠ `min.temp=3.0` 出自深冷 deck `Bulk_ex03.in:58`，
  **在 300 K 的 SEB 仿真里没有意义**，已从推荐行中移除 **[更正]**。

---

## 8. 瞬态时间步策略（位移电流污染问题）

### 8.1 问题

从 DC 稳态直接切到 transient 时，第一个/前几个时间步会出现**巨大的位移电流尖峰**——那是
数值上把稳态解重新投影到瞬态方程的伪迹，不是物理。如果这段落进主日志，
后面画 Id(t) 时基线是脏的，SEB 判据 1（"是否回落到基线"）就没法用。

### 8.2 解法 **[默认]**：独立预热段 + 主日志从预热后起

结构上把瞬态分成两段，**`log` 文件分开**：

```silvaco
# ---- 段 1：预热 / settle，日志单独存或干脆丢弃 ----
method newton climit=1e-4 dt.min=1e-17 maxtraps=10
log outf="RUN_ga2o3_seb/pre_settle.log"
solve tfinal=1e-12 tstep=1e-15        # 让位移电流衰减掉
log off

# ---- 段 2：主瞬态，SEU 在这一段内触发 ----
set LET=75
set density=0.006038*$LET
singleeventupset entry="$xin,$yin" exit="$xout,$yout" radialgauss \
  b.density=$density pcunits radius=0.05 t0=1e-11 tc=5e-13

method bicgst seu.integrate climit=1e-4 dt.min=1e-17 maxtraps=10
log outf="RUN_ga2o3_seb/main_trans.log"
solve tfinal=5e-11 tstep=1e-13
solve tfinal=1e-10 tstep=5e-13
solve tfinal=1e-9  tstep=5e-12
save outf="RUN_ga2o3_seb/peak_SEU.str"
solve tfinal=1e-8  tstep=1e-10
solve tfinal=1e-7  tstep=1e-9
solve tfinal=1e-6  tstep=1e-7
log off
save outf="RUN_ga2o3_seb/final_SEU.str"
```

规则：

- **`t0` 必须晚于预热段结束时间**，且不要正好落在两个 `solve` 段的边界上（对应源技能里
  "HeavyIon time 取 1.001 而不是 1.0"的同一防呆）。本项目取 `t0` ≥ 10×预热段 `tfinal`。
- **分段递增 `tstep`**：径迹注入前后用 fs~ps 级步长，收集/复合阶段放宽到 ns，
  长尾（判断是否回落）放宽到 100 ns 级。`Rad_Rel_ex01.in:107-117` 就是这么写的
  **[已核实：分段模式逐字存在；`atlas.key:3268 tfinal NUM 17` / `:3264 tstep NUM 14`，均在 SOLVE 卡 3073-4459。
  ⚠ 但 `Rad_Rel_ex01` 是 `GO victoryprocess → victorymesh → victorydevice` deck，**不是 ATLAS 例子**，见 §0.1]**。
- ⚠ **早期版本这里推荐的两个开关都不存在，已作废**：
  - `constant.timestep` —— **[未核实：`grep -n -i 'constant.timestep' atlas.key` 返回 0 行。
    全文件搜 `timestep` 只有 `:3263 timestep NUM 14`（SOLVE 卡上 `tstep` 的同槽别名），
    根本没有任何 `*.timestep` 逻辑开关]**。出处同样是 `Rad_Rel_ex01.in:103`（Victory Device）。
    → **要密采样就写 `method dt.min=<x> dt.max=<x>` 把上下限夹死**
    （`dt.max` **[已核实: atlas.key:714，缺省 1.0e10；manual p.1417 METHOD 表同：DT.MAX 默认 1.0×10¹⁰ s。
    内部槽位号本文旧记 NUM 72 与 `device-physics-and-solver.md` §8.2 的 NUM 74 互斥，[待 atlas.key 复核]]**，
    注意 `dt.max` 只在 METHOD 卡上，
    SOLVE 卡没有；`dt.min` 则 METHOD `:665` 与 SOLVE `:3504` 两张卡上都有）。
  - `lte.timestep` —— **[未核实：grep 返回 0 行，不存在]**（与 §3.2 是同一个缺陷的第二处）。
    → ATLAS **缺省就是基于 LTE 的自适应步长，不需要任何开关**。
    METHOD 卡上唯一的 lte 相关关键字是 `lte2step`
    **[已核实: atlas.key:904 lte2step LOG 101 f]**，manual："Use an alternative method for evaluating
    Local Truncation Error during a transient" —— 含义与 `lte.timestep` 并不相同，别当替身用。
- 关键时刻单独 `save outf=*.str`（峰值时刻、末态各一张），不要每步都存——`.str` 体积极大。
- 瞬态求解器 **[候选]**：`method newton`（稳、慢）· `method gummel`（弱耦合时快）·
  **[默认] `method block newton carriers=2`**（高压 + 自热 + 强耦合首选）；
  线性求解器 `pam.bicgst` / `bicgst` / `pam.gmres`
  **[已核实存在: atlas.key:930 pam.bicgst LOG 122 / :851 bicgst LOG 50 / :908 pam.gmres LOG 104（METHOD 卡 643-961）；
  另有 64 位版 `pam.bicgst.64 :931` / `bicgst.64 :897` / `pam.gmres.64 :926`]**，
  发散时优先换线性求解器再换非线性方法。
  补充：**3D 的缺省迭代求解器是 `ilucgs`**（manual："ILUCGS is slightly more stable than BICGST and is
  the default iterative solver in 3D"），所以"换线性求解器"时 `ilucgs` 也是一个候选落点。
  `block` 只在开了 `lat.temp` 或能量平衡时才有意义（等温漂移扩散下会被忽略），
  求解顺序是 GUMMEL → BLOCK → NEWTON **[已核实：manual 22.36]**。

### 8.3 收敛塌方时的排查顺序

| 症状 | 先查 |
|---|---|
| 注入瞬间就发散 | `radius` 太小 / 网格没细化到径迹尺度；先加密再说 |
| 步长坍缩到 `dt.min` 且温度还在涨 | 可能是**真 SEB**，先跑等温对照（关掉 `lat.temp`）区分热失控 vs 纯电学 |
| 步长坍缩但温度不涨、电流不涨 | 数值问题：换线性求解器、放宽 `max.temp`、加 `maxtraps` |
| 预热段就不稳 | DC 解本身不好，回去修 §5 的直流基线，不要在瞬态里硬扛 |
| 总电荷明显低于 LET 预期 | 忘了 `seu.integrate`，或径迹网格太粗 |

**两次失败规则**（沿用源技能）：同类失败最多试两次；第二次仍失败就停止盲调参数，
回到 examples / manual / 文献做根因分析。

---

## 9. 陷阱与半绝缘衬底建模

### 9.1 `trap` 关键字白名单 **[已核实：整卡逐行核对，TRAP = `atlas.key` **6962–7115**]**

```
trap                                    # atlas.key:6962  card 40
  LOG : donor(1) acceptor(2) fast(3) generation(4) midgap(5)
        tat.trap(6) hj.tnl.trap(7) qwell(8) ...        # 6963-6970，顺序与此完全一致
  NUM : e.level(1) taun(2) taup(3) sign(4) sigp(5) degen.fac(6) density(7) number(8)   # 6989-6996
        x.min(9) x.max(10) y.min(11) y.max(12) z.min(13) z.max(14) e.activation(15)    # 6997-7003
  CHAR: device(1)=structure(1)  material(2)  name(13)  region(14)  ...
```

（`degen` 是 `degen.fac` 的唯一前缀缩写；`region` 是 **CHAR**，所以 `region=3` 按字符字段传入。）

⚠ **`label` 不是 TRAP 卡参数** **[已核实：`grep -nE '^ *label ' atlas.key` 只有 `:5646/:5648/:5649`，
属独立的 LABEL 语句 card 32]**。examples 里的 `TRAP ... label=pgan_acc` 是 Victory Device 写法，
**照抄时必须去掉 `label=`**。

界面态语句是 **`inttrap`（两个 t）**，不是 `intrap` —— **本项目早期映射表里的 `intrap` 是笔误**
**[已核实: atlas.key:7615 inttrap card 45；:7616 donor LOG 1 / :7617 acceptor LOG 2 / :7618 fast LOG 3 /
:7619 density.prot LOG 4 / :7620 s.i LOG 5 **t**]**。
关键字**存在性已核实**；**语义**部分仍 **[待核实]**：manual 22.26 有 DONOR / ACCEPTOR / S.I / S.S / S.M / S.X /
DEGEN.FAC / DENSITY / DEPTH / E.LEVEL / E0N / E0P 的条目，但**全篇没有 `DENSITY.PROT` 与 `FAST` 的说明**。
本机 5.2.40.R examples 中亦无 `inttrap` 用例。

写 `inttrap` 时三个必知事实 **[已核实：manual 22.26]**：

- **`inttrap` 的 `density` 单位是 cm⁻²（面密度）**，而 `trap` 的 `density` 是 cm⁻³（体密度）——
  搞混直接差 8 个数量级，且不会报错。
- `s.i` 缺省为 **t**，所以裸写 `inttrap` 默认作用在**半导体/绝缘体界面**。
- `depth` 缺省 5.0e-3 µm，是陷阱向绝缘体内的穿透深度。

`e.level` 的参考基准 **[已核实：升级自原 [待核实]。manual Figure 3-1 及正文
"the position of the trap is defined relative to the conduction or valence bands using E.LEVEL so for instance,
**an acceptor trap at 0.4eV would be 0.4eV below the conduction band**"；
manual 22.26 INTTRAP E.LEVEL 条目亦同：受主参照导带、施主参照价带]**：

> **受主陷阱从导带底往下算 (Ec − Et)、施主陷阱从价带顶往上算 (Et − Ev)**，`trap` 与 `inttrap` 同此约定。

这条已在 manual 中确认，不必每次重查；但换材料时深能级**数值**本身仍需文献支撑。

### 9.2 Fe-doped 半绝缘衬底 / GaN buffer **[默认配方]**

半绝缘 GaN 衬底（Fe 补偿）与 C-doped buffer 的作用是把背景 n 型钉住、抬高纵向击穿、
并主导 buffer 陷阱相关的电流崩塌。本项目默认配方：

```silvaco
# Fe 深受主，半绝缘 GaN 衬底/buffer
trap acceptor e.level=0.8 density=2e18 sign=5e-15 sigp=5e-15 \
  degen.fac=1 material=GaN region=<substrate_region>
```

- `e.level=0.8` = Ec 以下 0.8 eV（受主参照导带，见 §9.1；Fe³⁺/²⁺ 深受主的常用取值）。
- `density=2e18 cm^-3`、`sign=sigp=5e-15 cm²` 为本项目冻结值；换文献时三个数要一起换，
  不能只改一个。
- 语法与 examples 中真实的 GaN 陷阱语句同形
  **[已核实：逐字符匹配 `GaN_Power_ex07.in:131`；关键字见 atlas.key:6964 acceptor / :6989 e.level /
  :6995 density / :7101 material / :6994 degen.fac / :6992 sign / :6993 sigp。
  ⚠ 该 deck 是 `GO victoryd`，非 ATLAS；但七个 token 都在 ATLAS TRAP 卡上，可安全照抄]**：
  `trap acceptor e.level=1.5 density=1e16 material=GaN degen.fac=1 sign=1e-13 sigp=1e-13`。

对比：p-GaN 栅层用**成对**的施主+受主深能级描述 Mg 相关态
**[已核实：`GaN_Power_ex12.in:184-185`（另在 312/313、464/465 重复）]**（见 §2.2）。

### 9.3 陷阱与 SEB 的相互作用（容易被忽略）

- 深受主会**延长**辐照后的恢复尾巴：判据 1（"是否回落"）的观测窗口必须比陷阱发射时间常数长，
  否则会把"慢恢复"误判成 SEB。发射时间常数量级 ~ `1/(sign·vth·Nc·exp(-Et/kT))`，
  深能级 + 低温下可以到 µs~ms 量级。
- 陷阱会显著改变阻断态的场分布 → 先有 trap 的 BV，再做 SEB；不要用无 trap 的 BV 去定 `V_load`。

> ### ⚠ `maxtraps` 与 `trap` 语句**毫无关系**（早期版本在这里犯了同形词错误）
>
> 早期版本写"陷阱数量多时 `maxtraps` 要放大"，**这是错的** **[更正]**。
> manual 22.36 原文：**"MAXTRAPS Specifies the number of times the trap procedure will be repeated
> in case of divergence. The value of MAXTRAPS may range from 1 to 10. The alias for this parameter is STACK."**
>
> 即 `maxtraps` 是求解器的**发散重试 / 步长二分次数**（"trap down" = 砍偏压或时间步重试），
> 与 deck 里写了几条 `trap` 语句**没有任何因果关系**。
>
> - 正确说法：**收敛困难、需要多次二分步长时**把 `maxtraps` 放大
>   **[已核实: atlas.key:666 maxtraps NUM 31 缺省 4]**。
> - **取值上限是 10**（manual 明确规定 1–10）。examples 里的 `maxtraps=30 / 100`
>   **[未核实：超出 manual 规定范围；且使用它们的 `Rad_Rel_ex01/ex02/ex11`、`SiC_Power_ex02`、
>   `CIS_CCD_ex03` 全部是 Victory Device deck，没有一个是 `go atlas`]**。
>   本项目 ATLAS deck **一律封顶 `maxtraps=10`**（examples 中 `maxtraps=10` 出现 24 次，是安全值）。

---

## 10. 文件落盘纪律（本项目硬规则，做 SEB 尤其重要）

SEB 一个 case 就能产出几百 MB 的 `.str`，必须严格分流：

| 内容 | 位置 |
|---|---|
| `.in` deck / `.py` 脚本 / `.md` 文档 / 轻量 `.csv` / `.png` | 主控端 `D:\SILVACO_LOCAL`（**只放这些**） |
| 运行期产物（`.str` / `.log` / `.set`） | 远端 `/root/DECKBUILD/RUN_<case>_<UTCstamp>/` |
| 归档后的大体积 `.str` / `.log` | Windows `E:\silvaco2425\bulk\str\` 与 `E:\silvaco2425\bulk\log\` |

- **`.in` deck 必须建模 + 特性仿真合并为同一个文件**：
  `go atlas`（建结构）→ `save outf=*.str` → `go atlas`（重新进入）→ `mesh inf=*.str` → 电学/瞬态求解。
  SEB deck 也一样：结构段 → 保存 → 重入 → 直流升压 → 预热 → SEU 瞬态。
- 远端 `/root/DECKBUILD` 是唯一正在迭代的运行区，**不要**把整套远端工程复制回 Windows。
- `/mnt/hgfs/{share_wm,share24,16sil_share}` 已 98% 满，**不要**往共享目录写 `.str`。
- 远端 `/` 只剩 ~123 GB：每个 case 结束后立刻回传归档并清理 `RUN_*` 目录里的中间 `.str`。

运行与归档的最小骨架：

```bash
# 远端（先设 PATH，Silvaco 默认不在 PATH 里）
export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
export SFLM_SERVERS=+localhost
RUN=/root/DECKBUILD/RUN_ga2o3_seb_$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$RUN" && cd "$RUN"
deckbuild -run -ascii ga2o3_seb.in -outfile ga2o3_seb.out

# 回传归档（在 Windows 主控端执行；按 batch-run-and-monitor.md §5 的约定
# 归档进 bulk\{str,log}\<run id>\ 的按 run 子目录，不要平铺）
# scp -i C:/Users/Administrator/.ssh/silvaco_ed25519 \
#     root@<实测IP>:$RUN/'*.str' E:/silvaco2425/bulk/str/RUN_ga2o3_seb_<stamp>/
# scp ... :$RUN/'*.log' E:/silvaco2425/bulk/log/RUN_ga2o3_seb_<stamp>/
```

SSH 目标 IP **每次都要先探测**：VM 的 ens33 走 DHCP，地址会在 `192.168.50.134` / `192.168.107.128`
之间漂移（2026-07-26 实测：`50.134` 存活且 `hostname` = `tcad`，`107.128` 连不上；别名 `silvaco`
当时指向的正是**存活**地址——早期版本把方向写反了，以 `preflight-and-environment.md` 的实测记录为准）。
**两个 IP 都不要硬编码进 runner**，每次会话先探测、连上后核对 `hostname` 输出为 `tcad`。

ATLAS 终止串判定 **[候选]**（用于后台等待循环）：正常结束看 `quit` / 进程退出码 0；
异常看 `ATLAS DIED`、`Convergence failure` / `solution did not converge`、`License` 报错。
不要用 `grep Error`——正常收敛信息里也有 "error"。

---

## 11. SEB 闭环记录模板

每个 case 在 `progress.md` 里落一段，缺项就是没做完：

```markdown
### RUN_<case>_<UTCstamp>: 材料=<β-Ga2O3/GaN/SiC/...>, LET=<?> MeV·cm²/mg, V_load=<?> V, 入射位置=<?>
- ATLAS 版本 / 并行: -V 5.40.0.R -P 4
- 前置 BV: <?> V（判据: intercept(y=1e-6)）；测试电压比例: <?>% BV
- 结构/热边界: thermcontact alpha=<?> ext.temp=300, 电极热接触=<有/无>, tc.const=<?>
- 陷阱: <trap 语句摘要 / 无>
- LET 换算: coef_pC=<?> → b.density=<?> pC/µm（公式见 wbg-radiation-and-seb.md §4）
- 径迹: radius=<?> µm, t0=<?> s, tc=<?> s, 剖面=<radialgauss/uniform/F.SEU>
- 终止状态: <quit / ATLAS DIED / Convergence failure>；关键行: ...
- .log: baseline I=<?>, peak I=<?>, t_final=<?>, 是否回落=<是/否/未跑够>
- .str: 电流路径=<?>, 峰值 T=<?> K @ <坐标>, impact 集中区=<?>
- 判定: Survive / SEB / 不确定（依据判据编号: <1,2,6>）
- 归档: E:\silvaco2425\bulk\str\<...>.str, E:\silvaco2425\bulk\log\<...>.log
- 下一步: 升/降 V_load、换位置、改 alpha、补文献、做等温对照...
```

---

## 12. 常见错误清单

| 错误 | 后果 | 正确做法 |
|---|---|---|
| **照抄 Victory Device deck 的语句到 ATLAS** | 一整行未知关键字；本文件此前的全部缺陷都出自这里 | 抄之前先 `grep -iE '^ *go ' <deck>.in`，必须是 `go atlas`；再逐 token 回 `atlas.key` 复核（§0.1） |
| 用 `b.time` 作为 SEU 时间参数 | ATLAS 报未知关键字 | 用 `t0` / `tc`（`atlas.key` 中无 `b.time`） |
| `method ... lte.timestep` / `constant.timestep` | 未知关键字（两者在 ATLAS 中都不存在） | 自适应是**缺省行为**，不需要开关；固定步长用 `dt.min=` + `dt.max=` 夹死 |
| `method ... seu.max.rad / seu.max.inc / seu.n.inc` | 未知关键字（三者都不存在） | `seu.integrate` 是裸开关；积分精度靠**网格密度**保证 |
| `impact ... hysteresis=1` / `e.min=` | 未知关键字（IMPACT 卡上都没有） | 删掉；低场噪声用 `gradqfl` + 合理网格解决 |
| `impact ... selberherr` | `selberherr` 在 MODELS 卡，不在 IMPACT 卡 | IMPACT 上写 **`selb`**（且缺省已是 t） |
| `models fmct` | `fmct` 不是 MODELS 参数（`atlas.key` 无裸 `fmct`） | 写 **`mobility fmct.n fmct.p`** |
| 把 `maxtraps` 当"陷阱条数上限" | 参数含义完全理解错，还常被写到 30/100 超出范围 | 它是**发散重试次数**，范围 **1–10**，与 `trap` 语句无关 |
| 说"`climit` 越小 = 收敛越严格" | 口径错误，会误导后续所有调参 | `climit` 是**浓度归一化因子（无量纲，缺省 1e4）**；击穿仿真 manual **推荐** `climit=1e-4` |
| 为了"放宽上限"写 `max.temp=1000.0` | 缺省本就是 2000 K，这是**压低**上限，SEB 会被误判为失败 | SEB 用 `max.temp=1e6` 之类实质取消上限 |
| 在 300 K 器件上写 `min.temp=3.0` | 无意义（该值出自深冷 deck） | 常温仿真不写；深冷仿真才调 |
| 把 Diamond 当 user-defined material | 白写一整套 `user.default/user.group` | Diamond 是**内建材料**，直接 `material mat=Diamond ...` |
| 忘了 `pcunits` 却给了 pC/µm 数值 | 电荷量差十几个数量级 | `b.density` + `pcunits` 成对出现 |
| 忘了 `method ... seu.integrate` | 总沉积电荷严重偏低，假"抗辐照" | 打单粒子必开 |
| 在 β-Ga2O3 上写 `polarization` | 引入不存在的界面电荷 | 只有纤锌矿 GaN/AlGaN 体系才开极化 |
| 把 `user.default=GaN` 当成物理等同 | 材料参数悄悄用了 GaN 的值 | 显式覆盖 `eg300/affinity/nc300/nv300/permittivity/mun/tc.const` |
| 用 β-Ga2O3 的空穴迁移率下结论 | 双极结论不成立 | 只做单极输运结论，`mup` 视为数值占位 |
| `impact selb` 默认系数直接用于宽禁带 | BV 偏差可达数倍 | 用材料专用参数集或显式给 `an1/bn1/ap1/bp1`（index 1 = 高场段，index 2 = 低场段） |
| DC→transient 首步位移电流进主日志 | 基线脏，无法判断"是否回落" | 独立预热段 + `log off` 后再开主日志 |
| 不写 `alpha` 当理想散热用 | 走 Dirichlet 定温分支，峰值温度被**低估**，热判据失效 | 用实测/封装反推的 `alpha`，并写进报告。注意 `alpha=0` **不是**完美热沉——按通量式 `Rth=1/alpha` 它反而是绝热 |
| 把 `beta` 当黑体参数 | 用错物理项 | `blackbody`+`stefan` 是辐射；`beta` 是**瞬态边界热容**（SEB 里更相关） |
| `trap ... label=` | `label` 不是 TRAP 卡参数 | 从例子里抄 `trap` 行时删掉 `label=` |
| 只报 BV 数字不报击穿位置 | 结论不可复现 | `.str` + `flowline`/`e.field`/`impact` 给空间证据 |
| 把 `.str` 写进 `/mnt/hgfs/*` | 共享盘已 98% 满，写失败或拖垮宿主 | 写 `/root/DECKBUILD/RUN_*`，结束后归档到 `E:\silvaco2425\bulk\` |
