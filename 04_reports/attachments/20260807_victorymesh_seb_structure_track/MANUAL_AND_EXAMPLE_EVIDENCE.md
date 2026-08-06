# Victory Mesh Conformal 语法与示例依据

> Scope: 只说明本轮冻结的 mesher 路线与语法来源；不证明 Stage 2 网格合同通过。

## 1. 最终冻结路线

```text
DevEdit structure
  -> structure outf=<raw.str>
  -> go victorymesh
  -> load in=<raw.str>
  -> line x / line y
  -> remesh conformal
  -> save out=<final.str> mode=atlas
```

用户已纠正：不再调查所谓“R 开头”的网格名称。本轮唯一 mesher family 是
`Victory Mesh Conformal`，未执行 Delaunay、R-tree、regular、custom 或任何 fallback。

## 2. 本机手册依据

本机手册：`D:\knowledge\pdf25\victorymesh_users1.pdf`。

- PDF p.124：device-grid `LINE` 平面用于 Conformal remesh；`LOCATION` 固定平面，
  `SPACING` 控制相邻非固定平面。
- PDF p.340：`LINE X|Y|Z LOCATION=<value> SPACING=<value>` 正式语法。
- PDF pp.385–387：`REMESH CONFORMAL` 为结构化 conformal device mesh 路线，并保留
  piecewise-linear 输入几何边界。
- PDF p.393：`SAVE ... MODE=ATLAS` 使用 Atlas-compatible 输出设置，并保存掺杂与电极。

## 3. 本机安装例子依据

以下本机例子均采用 `load`、`line x/y`、`remesh conformal`、`save ... mode=atlas` 血统：

1. `D:\knowledge\exp25\Power_and_RF\GaN_Power_Ex11.in`
2. `D:\knowledge\exp25\Power_and_RF\Other_Power_ex07.in`
3. `D:\knowledge\exp25\Radiation_and_Reliability\Rad_Rel_ex03.in`

任务包中的 `changban3(1).in` 只用于确认 DevEdit STR 接 Victory Mesh 的流程；其中的
Delaunay、器件参数、材料、掺杂和网格数值均未复制。

## 4. 运行时确认

两次真实日志都回显了：

```text
VICTORYMESH>remesh conformal
VICTORYMESH>save ... mode=atlas
VICTORYMESH version 1.12.0.R finished
```

因此 mesher family 与实际执行命令已由运行时确认。Stage 2 的 y 向实测间距未满足合同，
这不改变 mesher family 已确认的事实。
