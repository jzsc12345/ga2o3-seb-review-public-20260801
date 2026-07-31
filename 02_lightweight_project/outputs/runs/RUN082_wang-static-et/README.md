# RUN082_wang-static-et — 补齐Wang静态电热模块并测量2720V处Id/Tmax及1/5/16mA每毫米交点

- 日期:2026-07-29 21:46 | git:853e21a | deck:`D:\SILVACO_LOCAL\decks\RUN082_Wang2026_LGD20p0_FP11_subFe_impactY_staticET.in`
- deck SHA-256:`60552FE00F98EB473A6397B61BDAFF04DC49A6F810AC744B8801945A92444345`
- 远端:`/root/DECKBUILD/runs/RUN082_wang-static-et/`
- tmux:`deck_RUN082_Wang2026_LGD20p0_FP11_subFe_impactY_staticET`
- 看板:`D:\SILVACO_LOCAL\outputs\runs\RUN082_wang-static-et\screenshots\`

## 1. 目标与判据(发射前填)

补齐Wang静态电热模块并测量2720V处Id/Tmax及1/5/16mA每毫米交点

判据：

1. 论文正文靶点：`VGS=0 V`、`BV=2720 V`、局部晶格温度 `>1500 K`。
2. Fig.2(c) 读图近似：终端电流约 `15–16 mA/mm`；不是正文精确数值。
3. 项目电流口径：`1 mA/mm=1e-6 A/µm`，停止线
   `16 mA/mm=1.6e-5 A/µm`。
4. 必须同时报告扫描方向、折半次数、`Tmax/Tmin` 完整轨迹；若出现
   `120 K`，以 SSF 收敛点判 A/B：只在 Newton/折半中瞬时出现=发散伴随；
   写入已收敛 SSF 点=热边界错误。

## 2. 与上一 RUN 的差异(发射前填)

单变量:相对RUN078仅新增完整静态电热模块；结构与迁移率冻结

deck 全量精确 diff：
`logs\deck_diff_vs_RUN078.txt`
（SHA-256:
`7A86C7EB5AD75F7E5359C3A0008048262E224E809B24CC83B9E48DC80B87B9C7`）

已机检逐字冻结：

- DevEdit `work.area` 至 `mesh mode=MeshBuild`：相同，2882/2882 字符。
- 五区 `mobility`：相同，1702/1702 字符。
- 五区 y/[010] `impact`：相同，797/797 字符。
- region=11 Fe `trap`：相同，100/100 字符。
- `climit=1e-4 / maxtraps=10 / itlimit=50 / compliance=1.6e-5`
  和原电压步长数值不变。
- 禁止参数 `2.5e6 / 3.96e7 / impact betan=1.37 / p-type 2e6`
  零命中。

唯一物理模块增量（用户 2026-07-29 明确要求“补齐 Wang 静态电热模块”，
满足 A13 点头）：

- 五个 Ga₂O₃ region：`tcon.const tc.const=0.27` 与
  `hc.std hc.a=3.332`。数值来自 Wang Table I；常数模型是论文未给
  温度律时的最少假设 ATLAS 映射。
- SiO₂/HfO₂：`tc.const=0.014/0.023`，为 RUN035 实跑通过的项目平替。
- `models ... lat.temp joule.heat`；高压段只在原求解器数字上增加
  `block` 与 `max.temp=5000`。
- source/drain：`ext.temp=300, alpha=1000`；5 µm 底边：
  `ext.temp=300, alpha=3`。三者均为项目热边界代理，Wang 未报告其数值。
- 追加 `Tmax/Tmin/JouleMax/HeatMax/Tsource/Tdrain/Tbottom` 探针和热场输出。
- 同一 ATLAS 进程等温爬到 2400 V → 原地开启热方程 → 1 V 精扫，
  不使用 DevEdit master 重载。

特意不混改：HfO₂→Al₂O₃、结构、网格、迁移率、impact、Fe `Nt/σ`、
L_GD、FP、功函数、compliance、climit、maxtraps。

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图:`figs\RUN082_structure_preflight_same_geometry.png`
  （SHA-256:`49EB5841CBA2D8DAEEDBD84EAFD904B1F3D5D70D16E47E6E54794CF966C1A3D0`）
- 网格图:`figs\RUN082_mesh_preflight_same_geometry.png`
  （SHA-256:`48444ADCCA9415DFCE809CDA9E81A39B734962C992D11B680812C4D3610C332D`）
- 两图逐字复用 RUN078，因为结构/网格块逐字相同；RUN078 实测
  `6925 points / 13492 triangles / 0 obtuse`。
- 发给用户时间:2026-07-29 21:48 +08:00
- tmux 会话:`deck_RUN082_Wang2026_LGD20p0_FP11_subFe_impactY_staticET`

## 4. 结果索引

- 状态：`COMPLETED_MODULE_PASS / WANG_STATIC_TARGET_FAIL`。2026-07-29
  21:48 +08:00 经 `/root/bin/vdoe_tmux.sh start-deck` 正式发射；
  ATLAS 最终打印 `version 5.40.0.R finished`，但 2720 V 求解未收敛。
- 314 个收敛 SSF 点；最后收敛于 `Vd=2707.192902 V`，
  `|Id|=2.920164569e-15 A/µm=2.920164569e-9 mA/mm`，
  `Tmax/Tmin=300.0000036/300.0000035 K`。
- 真实 2700 V 点：
  `|Id|=1.418076612e-14 A/µm=1.418076612e-8 mA/mm`，
  `Tmax/Tmin=300.0000021/300.0000020 K`。
- 1/5/16 mA/mm 三条交点均不存在；`Taking smaller bias` 原始消息 26 行，
  `Cannot trap` 2 行。
- 电压—电流—温度机器表：
  `csv\RUN082_staticET_trace.csv`、`csv\RUN082_staticET_summary.csv`。
- 2700 V 空间 hotspot 机器表：
  `csv\RUN082_staticET_spatial_summary.csv`；原始 VictoryExtract
  cutline CSV 与 hotspot TXT 在 `csv\spatial\`。
- 四图证据：
  - 结构：`figs\RUN082_structure_preflight_same_geometry.png`
  - 网格：`figs\RUN082_mesh_preflight_same_geometry.png`
  - Id/T–V：`figs\RUN082_staticET_Id_T_vs_V.png`
  - 空间切线：`figs\RUN082_staticET_V2700_cutlines.png`
  - 实际空间采样：`figs\RUN082_staticET_V2700_spatial_samples.png`
- 大文件已归档：
  `E:\silvaco2425\bulk\log\RUN082_wang-static-et__*` 与
  `E:\silvaco2425\bulk\str\RUN082_wang-static-et__*`。
- 失败后执行的 `SAVE` 会沿用/污染最后状态；名字含 `V2720` 与
  `final` 的 `.str` 不得冒充真实 2720 V 解。空间裁决只采用精确收敛的
  `...staticET_V2700.str`。

## 5. 判据结论

1. **电热模块通过**：同一进程等温母解→开启 `LAT.TEMP+JOULE.HEAT` 成功，
   三热边界与温度/热源探针均有数值，2700 V 真收敛。
2. **Wang 静态三元目标失败**：未到 2720 V；电流比 Fig.2(c) 读图的
   15–16 mA/mm 低约 9 个数量级；全轨迹 `Tmax≤300.0000036 K`，
   没有 1500 K 温升。
3. **120 K A/B 未触发**：所有已收敛点 `Tmin≥300.0 K`，既没有 Newton
   瞬时 120 K 证据，也没有收敛到 120 K 的热边界错误证据。
4. **空间裁决**：2700 V 全域 `|E|max=3.42575 MV/cm`，精确位于
   FP11 端点 `(11,-0.42) µm`；impact、Joule、Jtotal 峰分别在漏侧
   `x≈26.24/26.05/25.85 µm,y≈0`。场板接管了最高静电场，但电流种子太小，
   `J·E` 不足以启动电热正反馈。
5. 下一步不应先扫 κ(T) 或 `alpha`：温度没有离开 300 K 时这些参数几乎
   不参与因果。推荐保持结构/迁移率/impact/电热模块冻结，单变量检查 Fe
   深受主占据/补偿是否把静态电流支路锁死；用户核签前不执行。

完整裁决：
`D:\SILVACO_LOCAL\docs\RUN082_Wang静态电热模块_结果裁决_20260729.md`
