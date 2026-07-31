# 00 — 路径映射 / PATH MAP

> **本目录是 β-Ga₂O₃ / NiO 建模知识库的唯一入口。**
> 所有结论必须可回溯到下面列出的一手来源（手册 PDF、例子库 `.in`、`atlas.key`、论文）。
> 建立时间：2026-07-26　最后更新：2026-07-26 深夜（主路径切换到 `D:\knowledge`）

---

## ★ 0. 四库统一入口（2026-07-26 起为唯一主路径）

用户已把四个库合并到本地 **`D:\knowledge\`**，遇任何仿真问题按此顺序检索，禁止凭印象猜：

| 顺序 | 路径 | 内容 | 用途 |
|---|---|---|---|
| ① | `D:\knowledge\material_sil\` | 128 个 smdb XML 材料文件（0.4 MB） | **参数数值**最高权威 |
| ② | `D:\knowledge\pdf25\` | 26 本手册 PDF（225.6 MB） | **语法与语义** |
| ③ | `D:\knowledge\exp25\` | 184 个官方例子 `.in`（6 大类） | **可抄写法** |
| ④ | `D:\knowledge\paper\` | 43 个文献文件（173.6 MB，6 主题目录） | **物理依据** |

每库根都有 agent 生成的 `README.md` 导航；总导航 `D:\knowledge\README.md`。
（`F:\share24\...` 与 `G:\#24exp\...` 是同内容的历史镜像，网络盘不稳时不要依赖。）

---

## 1. 一手资料位置（本地，Windows）

| 代号 | 路径 | 说明 |
|---|---|---|
| `MAN` | `D:\knowledge\pdf25\` | Silvaco 2025 手册 PDF 全集（26 本） |
| `MAN/atlas` | `…\pdf25\atlas_users1.pdf` | **14.7 MB** ATLAS 主手册 —— 物理模型、语句、参数的第一权威 |
| `MAN/vdev` | `…\pdf25\victorydevice_users1.pdf` | **16.4 MB** Victory Device（3D 器件） |
| `MAN/vdoe` | `…\pdf25\victorydoe_users1.pdf` | VictoryDoE（拉偏 / DOE） |
| `MAN/vwf` | `…\pdf25\vwf_users1.pdf` | **24.0 MB** VWF（批量/DOE，最大一本） |
| `MAN/deck` | `…\pdf25\deckbuild_users1.pdf` | DeckBuild：`set` 变量、`go <tool>`、C 解释器 |
| `MAN/devedit` | `…\pdf25\devedit_users1.pdf` | DevEdit（多边形建模） |
| `MAN/vextract` | `…\pdf25\victoryextract_users1.pdf` | 结果提取 |
| `MAN/tonyplot` | `…\pdf25\tonyplot_users1.pdf` / `tonyplot3d_users1.pdf` | 可视化 |
| `MAN/athena` | `…\pdf25\athena_users1.pdf` | 工艺仿真 |
| `EXP` | `D:\knowledge\exp25\` | 官方例子库，**184 个 `.in`** |
| `EXP/power` | `…\exp25\Power_and_RF\` | 功率器件（GaN/SiC/Si/Other 各 ex01…） |
| `EXP/rad` | `…\exp25\Radiation_and_Reliability\` | **辐照与可靠性 Rad_Rel_ex01…ex11**（单粒子主战场） |
| `EXP/opto` | `…\exp25\Opto_and_Photonics\` | LED/OLED/激光（Poole-Frenkel 例子在此） |
| `EXP/cmos` | `…\exp25\CMOS_ands_BiCMOS\` | CMOS/BiCMOS |
| `EXP/mem` | `…\exp25\Memory\` | 存储器（ReRAM 含热模型） |
| `EXP/disp` | `…\exp25\Dosplay\` | 显示（TFT，含 Poole-Frenkel） |
| `MATSIL` | `D:\knowledge\material_sil\` | **Silvaco 官方材料参数库（smdb XML），124 个材料** |
| `MATSIL/ga2o3` | `…\material_sil\betaga2o3` | **11.6 KB —— β-Ga₂O₃ 完整参数文件，materialcode m259，本项目最高价值单文件** |
| `MATSIL/nio` | `…\material_sil\nio` | NiO（materialcode 304，内容偏薄，见 `20_NiO_*.md`） |
| `MATSIL/sic4h` | `…\material_sil\sic-4h` | 8.7 KB —— 「对齐 SiC 完备度」的参照基准 |
| `MATSIL/gan` | `…\material_sil\gan` | 6.8 KB —— `user.default=GaN` 实际继承的来源 |
| `MATSIL/*` | `al2o3` `sio2` `hfo2` `zno` `diamond` `silicon` … | 介质与对照材料 |
| `PAPER` | `D:\knowledge\paper\` | 文献库，43 个文件，按主题分目录 |
| `PAPER/seb` | `…\paper\paper_seb\` | 单粒子烧毁 |
| `PAPER/PFE` | `…\paper\paper_PFE\` | **Poole-Frenkel 发射**（`Fre_emode_PFE.pdf`、`Gui_emode_sbd_PFE.pdf`） |
| `PAPER/trap` | `…\paper\paper_trap\` | 陷阱 / 深能级 |
| `PAPER/emode` | `…\paper\paper_emode_Vthoverszero\` | 增强型 Vth>0（含 `ZXZ_变掺杂 (2).in` 可直接参考的 deck 与网格图） |
| `PAPER/BV` | `…\paper\paper_BV_lapian\` | 场板与击穿 |
| `PAPER/model` | `…\paper\paper_model\` | 解析模型 |

> **强制检索顺序（用户 2026-07-26 指令）**：遇到任何问题，一律按
> `MATSIL` → `MAN`(pdf25) → `EXP`(exp25) → `PAPER` 的顺序查证，**不允许凭印象猜**。
> `atlas.key` 仅在远端可得，远端不可达时相关条目标 `[待 atlas.key 复核]`。

## 2. 远端（Silvaco VM，RHEL 7.9，hostname `tcad`）

```bash
ssh -i C:/Users/Administrator/.ssh/silvaco_ed25519 root@<IP>
# IP 在 192.168.107.128 / 192.168.50.134 之间漂移，用 scripts/silvaco_remote.py 自动探测
```

| 代号 | 路径 | 说明 |
|---|---|---|
| `KEY` | `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key` | **关键字表 345 KB —— 判断「参数是否存在」的唯一裁决依据** |
| `RMAN` | `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/docs/atlas_users1.pdf` | 远端手册（远端有 `pdftotext`） |
| `REXP` | `/atctools/Synopsys/Silvaco2024/examples/deckbuild/5.2.40.R/` | 远端例子库 |
| `RUN` | `/root/DECKBUILD/` | 生产运行区（**2026-07-27 起有架构**，导航见远端 `README.txt`） |
| `RUN/runs` | `/root/DECKBUILD/runs/<工程>/<步>/` | 新单 deck 运行统一入口（特例：冻结书写死的 `W1_static/` 平级保留） |
| `RUN/post` | `/root/DECKBUILD/postproc/{csv,cutlines,figs,shots}/<tag>/` | ★ 后处理集散地；`<tag>` 与主控端 archive tag 一致（如 `W1D1`），两端对号 |
| `RUN/lab` | `/root/DECKBUILD/_lab/<主题>/` | 语法试验场（历史 `_ve_*`/`_loop_lab` 原地保留） |
| `VDOE` | `/root/SilvacoVDoE/<组>/<工程>/work/` | ⚠ 已弃产线（账本 B12）的历史工作区；仅寻址旧产物，勿新建/复跑工程 |

`atlas.key` 行格式：

```
<card>          <id>
   <param>      <TYPE>   <index>   <default>
```

`TYPE` ∈ `NUM` / `LOG` / `CHAR`。**参数不在 `atlas.key` 里 = ATLAS 5.40.0.R 中不存在。**

## 3. 论文与器件资料

| 代号 | 路径 |
|---|---|
| `P/Wang2026` | ★ **本项目唯一拟合目标论文**（用户 2026-07-27 收束令）。主控端正本：`D:\SILVACO_LOCAL\archive\Wang 等 - 2026 - ###nihe_Simulation of the single event burnout in lateral enhancement mode β-Ga2 O3.pdf`（archive\ 整体禁引，唯此件例外准许只读引用）；仓外备份 `D:\LocalUserFolders\Desktop\sebpaper\` 同名文件 |
| `P/Tan2025` | `D:\LocalUserFolders\Desktop\Tan 等 - 2025 - Ultralow on-resistance high-voltage β-Ga2 O3 MOSFET with an extended p-NiO gat.pdf`（仅背景参考/图风格对标，**非拟合对象**） |
| `P/Wang2023` | `D:\LocalUserFolders\Desktop\Wang 等 - 2023 - Demonstration of the β-Ga₂O₃ MOS-JFETs with suppressed gate leakage current and large gate swing.pdf`（仅背景参考，**非拟合对象**；复现其隧穿模型的旧要求已撤回，见账本 §R） |
| `P/impact` | `D:\LocalUserFolders\Desktop\2db282712b39472264f88bf21d87dc95.png` — 表2.3 Chynoweth 晶向系数 |
| `MATLIB` | `D:\OneDrive\Desktop\SILVACO_WS\10_materials_models\material_sil\{betaga2o3,nio,al2o3,sio2,sic-4h,gan}` |

## 4. 本工作区（主控端）

| 路径 | 只放 |
|---|---|
| `D:\SILVACO_LOCAL\knowledge\` | **本知识库**（`.md`） |
| `D:\SILVACO_LOCAL\docs\` | handoff / 操作指南（`.md`） |
| `D:\SILVACO_LOCAL\decks\` | `.in` / `.sdb` deck（split.csv 已随 VDoE 废案归档删除，B12） |
| `D:\SILVACO_LOCAL\scripts\` | `.py` |
| `D:\SILVACO_LOCAL\outputs\` | `.png` / 轻量 `.csv` |
| `E:\silvaco2425\bulk\{str,log}\` | 大体积 `.str` / `.log` 归档 |
| `D:\SILVACO_LOCAL\silvaco\` | 历史 handoff 与证据（只读为主） |

## 5. 例子库索引（按语句实测统计，184 个 `.in`）

以下命中数由 `Select-String` 在 `EXP` 全库统计得出，是选模板的起点：

| 语句 / 模型 | 命中 | 最有参考价值的例子 |
|---|---|---|
| `Ga2O3` | **1** | `Other_Power_ex08.in` ← **Silvaco 官方唯一 Ga₂O₃ 例子** |
| `user.material` / `user.group` / `user.default` | 6 | `Other_Power_ex08`, `Adv_CMOS_ex07`, `LED_OLED_ex08/09/12`, `CIS_CCD_ex06` |
| `trap`（体陷阱） | 5 | `GaN_Power_ex07/ex08/Ex11`, `SiC_Power_ex05`, `Silicon_Power_ex15` |
| `inttrap` / `interface qf` | 35 | `Bulk_ex01/03/04`, `Adv_CMOS_ex01…04`, `55_HV` |
| `incomplete` | 10 | **`SiC_Power_ex01/ex06/ex07`**, `GaN_Power_Ex11`, `LED_OLED_ex01…03` |
| `impact` / `selb` | 49 | `SiC_Power_*`, `Bip_Dio_ex01/04/05`, `55_HV` |
| `lat.temp` + `thermcontact` | 19 | `SOI_ex04/05/07/08/09/12/13`, `Adv_CMOS_ex08`, `Bip_Dio_ex05`, `Bulk_ex03` |
| `singleeventupset` | **8** | **`Rad_Rel_ex01/02/03/06/07/09`**, `Silicon_Power_ex08`, `Photodiode_ex13` |
| FN 隧穿（`fnord`/`f.n`/`fnpp`/`fnholes`） | 11 | `Adv_CMOS_ex01…04/ex08`, `Bulk_ex01`, `55_HV`, `LED_OLED_ex07/ex10` |
| **Poole-Frenkel** | **3** | **`LED_OLED_ex05.in`, `LED_OLED_ex08.in`, `TFT_ex15.in`** ← ATLAS 确有内建 PF |
| BBT / TAT / trap tunnelling | 110 | 广泛存在，`Adv_CMOS_*`、`55_HV` 等 |
| `cvt` | 48 | CMOS 类为主 |
| `conmob` | 35 | 硅器件为主 |
| `fldmob` | 67 | 广泛 |
| `NiO` | **0** | 例子库中无 NiO，必须自建（见 `20_NiO_*.md`） |
| `curvetrace` | 0 | 例子库中无，手册中有（见击穿章节） |

## 6. 已冻结的换算与常数（本项目自有，已交叉验证）

β-Ga₂O₃：ρ = 5.88 g/cm³，Ei = 15.6 eV

```
LET(ehp/µm) = LET(MeV·cm²/mg) × ρ(mg/cm³) ÷ Ei(eV) × 1e-4
charge(pC/µm) = LET(ehp/µm) × 1.6022e-19 × 1e12
```

| LET (MeV·cm²/mg) | pC/µm | 出处 / 交叉验证 |
|---|---|---|
| 10 | **0.0604** | 与 WKJ 基线 `LET0=0.06` 独立吻合 ✅ |
| 75 | **0.4529** | Wang2026 指定值 |
| 81.5 | 0.492 | Liu2025 已用实验标定，目录名 `Ta82` ✅ |
| 59.6 | 0.360 | 现有 deck 的废弃历史值 ❌ |

`singleeventupset ... b.density=<pC/µm> pcunits` 与 `mySEU.c` 的 `LET` 常数同一单位。

## 7. 阅读顺序

1. 本文件（路径映射）
2. `10_Ga2O3_材料参数完全表.md`
3. `11_models_激活与作用域.md` ← 「模型开了却没生效」的根源都在这里
4. `12_mobility_电子与空穴.md`
5. `13_impact_晶向碰撞电离.md`
6. `14_incomplete_非完全电离.md`
7. `15_interface_Qf_与体陷阱.md`
8. `16_热模型与自热.md`
9. `20_NiO_p型建模.md`
10. `30_栅漏_FNT_PFE_TAT.md`
11. `40_singleeventupset_源项.md`

## 8. 证据规则（对本目录所有文档强制）

> **`[已核实]` 只能用于当场贴得出证据的条目** —— `atlas.key` 的 grep 输出、手册原文引用（注明 PDF 与页/行）、或例子库 `.in` 的实际行。
> 查不到就写 `[未核实]`，这是允许的答案。**不允许凭印象写参数名。**

历史教训：前一轮曾产出 `lte.timestep`、`seu.max.rad`、`seu.max.inc`、`seu.n.inc`、
`impact hysteresis`、`impact e.min` 六个**根本不存在**的参数，并且标了「已核实」。
凡从本目录复制到 deck 的语句，跑挂的代价由 deck 承担，所以宁可标未核实。
