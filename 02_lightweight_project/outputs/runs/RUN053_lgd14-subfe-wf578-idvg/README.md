# RUN053_lgd14-subfe-wf578-idvg — 单变量将VTH校准到约0.9V

- 日期:2026-07-29 11:07 | git:853e21a | deck:`decks\RUN053_Wang2026_LGD14p0_FP10_subFe_wf5p78_IdVg.in` (sha256:57f1273322a917cf)
- 远端:`/root/DECKBUILD/runs/RUN053_lgd14-subfe-wf578-idvg/` | tmux:`deck_RUN053_Wang2026_LGD14p0_FP10_subFe_wf5p78_IdVg` | 看板:`outputs\runs\RUN053_lgd14-subfe-wf578-idvg\screenshots\`

## 1. 目标与判据(发射前填)

单变量将VTH校准到约0.9V
主判据：`VTH_CC@Id=1e-9A/µm`进入`0.8–1.0V`；并保留
`Id(Vg=0)`和`Id(Vg=10V)`，阈值不过闸禁止运行BV。

## 2. 与上一 RUN 的差异(发射前填)

单变量:gate work function 5.23->5.78eV
归一化输出名和头注释后，相对RUN052的唯一物理差异：
```
- set wf_gate = 5.23
+ set wf_gate = 5.78
```
⚠ 物理模型、Fe陷阱、掺杂、结构和网格均无改动；只校准接触功函数。
用户已接受推荐增强型路线并允许约0.9V烟测。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图:`..\RUN051_lgd14-subfe-structure\figs\RUN051_subFe_structure.png`
  | 网格图:`..\RUN051_lgd14-subfe-structure\figs\RUN051_subFe_mesh.png`
- 复用RUN051实测6019点/11722三角/0钝角；RUN052已证明Fe陷阱求解全程完成。
- 发给用户时间:11:08 | tmux 会话:`deck_RUN053_Wang2026_LGD14p0_FP10_subFe_wf5p78_IdVg`

## 4. 结果索引(到站后填)

- `csv\RUN052_053_IdVg_summary.csv`：WF校准前后阈值及取样电流。
- `figs\RUN052_053_IdVg_wf_calibration.png`：两条VDS=20V传输曲线。
- 大文件：`E:\silvaco2425\bulk\{log,str}\RUN053_lgd14-subfe-wf578-idvg__*`。

## 5. 判据结论(到站后填)

**PASS，增强型阈值闸门开放。** 正式tmux自然结束，ATLAS finished；
`VTH_CC@Id=1e-9A/µm=0.908921V`，命中0.8–1.0V烟测窗口。
`Id(Vg=0)=1.867e-17A/µm`，`Id(Vg=.9)=6.411e-10A/µm`，
`Id(Vg=10)=9.494e-6A/µm`。相对RUN052唯一物理变量为
`wf_gate 5.23→5.78eV`；结构/网格/Fe陷阱/掺杂/impact不变。
该功函数是项目校准值，不冒充Wang论文原文参数。
