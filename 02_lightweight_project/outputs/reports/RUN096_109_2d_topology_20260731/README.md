# RUN096 / RUN109 2-D current-path topology audit

本目录保存 2026-07-31 的零 ATLAS 机时二维拓扑审计轻量交付。

正式裁决：

`D:\SILVACO_LOCAL\docs\RUN096_RUN109_二维电流路径拓扑审计_20260731.md`

## 目录

- `figs\RUN096_109_native_vertex_paths.png`：最终主证据；原生 STR 顶点、无滤波、
  带符号漏→源 widest path，黄色 × 为瓶颈，红箭头为搜索方向。
- `figs\RUN096_109_topology_sensitivity.png`：HEATMAP filter 1/3/5 与原生顶点对照。
- 其余 `figs\`：规则网格全域/浅层 `Je`、electron、impact、RUN109/RUN096 空间比值。
- `csv\RUN096_109_native_vertex_metrics.csv`：最终原生顶点定量表。
- `csv\RUN096_109_topology_sensitivity.csv`：滤波、端点、原生顶点全部敏感性结果。
- `csv\RUN096_109_native_vertex_path_points.csv`：六条最终路径的轻量点表。
- `csv\RUN096_109_directed_path_signcheck.csv`：六态逐边双端电流投影机检；
  `nonpositive_edge_count` 全为 0。
- `evidence\`：两次 VictoryExtract 的原始 `typescript` 留痕。

12 份约 50 MB 的规则网格原始 CSV 与 6 份原生顶点 CSV 不进入 D 盘仓库；
权威远端副本分别在：

- `/root/DECKBUILD/postproc/RUN096_109_2d_topology_20260731/raw/`
- `/root/DECKBUILD/postproc/RUN096_109_2d_vertex_20260731/raw/`

本审计读取冻结 STR，没有运行 ATLAS，也没有修改 RUN096/RUN109 母 deck。原生顶点图
只覆盖 `y=0–0.35 µm`；“全深最优路径不选 Fe 衬底”来自 `y=0–5.35 µm` 的
HEATMAP filter=1/3/5 交叉检查，不代表衬底局部电流为零。
