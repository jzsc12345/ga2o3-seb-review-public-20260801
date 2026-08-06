# 网页端交接：DevEdit 系列与两组历史 mesh 案例的三端电流配对审计

> Provenance: Codex-generated / post-2026-07-27-09:20 / lower-trust；需网页端独立复核
> 日期：2026-08-06
> 任务性质：只读证据交接，不包含 SSH、仿真、修改 deck、创建 RUN 或调参授权
> 方法合同：已由网页端接受的 Revision 4——端电流配对、保持时间、空间 `Jn` 连通与横截面通量闭合分开裁决

## 1. 网页端先读的结论

用户当前看到的表象是：

> DevEdit 建模的 RUN 没有表现出漏极电流与源极电流绝对值相等；历史 mesh 建模案例表现出了。

只读原始日志给出的更准确答案是：

1. **历史两个 mesh 案例都明确形成了后段漏—源端电流配对。**
2. **RUN038、RUN039、RUN040、RUN096 的 accepted 日志也出现过后段漏—源配对。** 因此不能继续写成“它们始终只有漏—栅配对”。
3. 真正没有闭合的是正式空间 Phase 2：现有案例普遍缺少同一保持区间的 early/middle/late 三帧 `Jn` 连通与横截面通量闭合证据。
4. 两个历史 mesh 案例的热行为不同：第一个到 `1 µs` 仍升温，第二个在微秒段达峰后冷却。只有漏—源端电流相等，不足以证明热失控 SEB。

因此，当前应该把结论拆成两层：

```text
TERMINAL_DEFINED_DRAIN_SOURCE_PAIRING
    与
SPATIALLY_CONFIRMED_PHASE2 / THERMAL_RUNAWAY_SEB
```

第一层在两个历史案例中已经实锤；第二层仍未完成。

## 2. 答案一：RUN038–040、RUN096 与第一历史 mesh x=10 案例

### 2.1 第一历史 mesh 案例

远端只读目录：

```text
/root/Desktop/sharer24/SEB/def/x=10um——T30min_meshcu/
```

目录没有生成 deck，只有终端日志与 STR，因此材料、impact、热边界、粒子源函数、求解器和器件宽度不可完整追溯。

原始 accepted 日志观察到：

```text
10 fs–100 fs：|Id| 与 |Ig| 幅值接近
约 1.9 ns：开始出现漏—源反向配对
3.588 ns–1 µs：连续 48 个 accepted 点保持漏—源配对
```

`t=1 µs`：

```text
Is = -1.180625726e-5      （SSF 原始电流数值）
Id = +1.179280559e-5
Ig = +4.694299133e-8
漏—源配对误差 = 0.114%
三端 raw KCL 误差 = 0.284%
温度字段 = 557.83 K
```

注意：早期 `|Id|≈|Ig|` 只是幅值接近；SSF 原始符号同号且 raw KCL 未闭合，不能把 TonyPlot 的箭头直接替代符号/KCL 证据。

空间上，4 ps STR 中 `SEU Generation Rate` 主柱在 `x=10 µm`，贯穿 channel→UID→substrate。但最长漏—源保持区间缺少约 `0.337–0.668 µs` 的 middle STR，也没有可独立确认的 `Jn` 字段血统，因此正式 Phase 2 仍为：

```text
RAW_TERMINAL_DS_PAIRING = OBSERVED
FORMAL_SPATIAL_PHASE2 = NOT_EVALUABLE
PRIMARY_LIMIT = OUTPUT_SAMPLING_INSUFFICIENT
```

### 2.2 对 RUN038–040、RUN096 原命题的修正

RUN038、RUN039、RUN040、RUN096 的 accepted 日志同样出现了后段漏—源配对。它们不是“始终漏极≈栅极”。此前容易产生误判的原因包括：

- 图只突出早期峰值或局部窗口；
- 终端电流没有统一做符号、KCL 和连续区间筛查；
- 空间 STR 与终端保持区间没有绑定；
- RUN040 存在明确数值终止，不能与正常到站的历史案例等价比较。

第一历史案例与当前 RUN 也不是同构对照：

| 维度 | 历史 mesh x=10 | RUN038–040 | RUN096 |
|---|---|---|---|
| 器件横向长度 | 15 µm | 20 µm | 20 µm |
| 半导体深度 | 0.15–0.75 µm | 0–0.35 µm | 0–5.35 µm |
| 栅控结构 | NiO 双层 + 栅下高阻区 | HfO₂ MOS + FP | HfO₂ MOS、无 FP |
| 漏压 | 约 300 V | 1200/1400/1500 V | 1000 V |
| xion | 10 µm | 13 µm | 11 µm |
| Fe 衬底 | 无 deck，未核实 | 无 | 有 |

所以第一份答案不是“找到一个参数错误”，而是：

> 历史曲线更直观，但当前 RUN 的日志也存在后段漏—源配对；现有证据不足以把差异归因于 DevEdit、材料模型或某一个参数。

## 3. 答案二：第二历史 mesh `seb_2` 案例

远端只读目录：

```text
/root/Desktop/16sil_share/huizong/0405/seb_2/
```

这一目录包含 `seb.in`、`Vds300_X8.log`、打击前 STR 和 14 张瞬态 STR，运行血统比第一历史案例完整。

### 3.1 用户的两个观察均得到确认

**约 16 分钟：**

- 日志建立：05:59:15；
- `1 µs` STR 建立：06:14:53–54；
- 到达 `1 µs` 用时约 15 min 38–39 s；
- deck 随后继续到 `1 s`，完整运行约 21 min 13–14 s。

**最终 `|Id|=|Is|`：**

`t=1 s`：

```text
Is = -3.466793615e-7 A
Id = +3.466769071e-7 A
Ig = -3.763242063e-11 A
漏—源配对误差 = 0.000708%
三端 raw KCL 误差 = 0.0116%
```

最长连续漏—源配对区间为：

```text
4.642 ns–1 s
205 个 accepted 点
区间最大漏—源配对误差 5.04%
区间最大 raw KCL 误差 3.91%
```

### 3.2 它不是热失控金标准

该案例的 accepted 温度峰值为：

```text
411.75 K @ 3.55 µs
```

保存的 `10 µs` STR 对应 397.55 K，`1 s` 已回落到 314.69 K；漏极电流也从 `50 ns` 的约 `1.066e-5 A` 总体衰减到 `1 s` 的约 `3.467e-7 A`。

因此：

```text
RAW_TERMINAL_DS_PAIRING = OBSERVED_STRONG
THERMAL_RUNAWAY_SEB = NOT_OBSERVED
FORMAL_SPATIAL_PHASE2 = NOT_EVALUABLE
PRIMARY_LIMIT = OUTPUT_SAMPLING_INSUFFICIENT
```

这更像一条被粒子打通、但随后逐渐变窄和冷却的漏—源路径，不是 `Id↑ + impact↑ + Tmax↑` 的持续热正反馈。

### 3.3 deck 中值得注意但不得复制的历史配置

```text
VDS = 300 V
xion = 8 µm
离子径迹 y = -2.3 → +2.6 µm（贯穿器件全深度）
channel / UID = 2e17 / 1.5e15 cm^-3
substrate = Boron 2e6 cm^-3
栅下深受主 Et=4.0 eV, Nt=1.8e17 cm^-3
lat.temp 开启；source/drain ext.temp=300 K；底部热极注释
历史 impact = 2.5e6 / 3.96e7 / betan=1.37
Ga₂O₃、NiO 使用 GaN 父材料并仅覆盖部分参数
```

p 型 `2e6` 衬底和这组三个旧 impact 数值违反当前生产约束，只能作为历史血统证据，禁止复制进现役 deck。

## 4. 两份答案合并后的科研裁决

| 对象 | 后段漏—源配对 | 温度趋势 | 正式空间 Phase 2 | 当前用途 |
|---|---|---|---|---|
| 第一历史 mesh x=10 | 3.588 ns–1 µs，已观察 | 到 557.83 K，终点仍升 | NOT_EVALUABLE | 端电流两阶段参考 |
| 第二历史 mesh x=8 | 4.642 ns–1 s，强观察 | 3.55 µs 达峰后冷却 | NOT_EVALUABLE | 长期 DS 配对阳性参考 |
| RUN038–040/RUN096 | 日志中也有后段 DS 配对 | 各 RUN 不同 | 未统一通过 | 当前拟合线，不能再标“只有 DG” |

最重要的修正是：

> **建模方式不是当前已证明的因果变量。** “DevEdit vs mesh”与结构、偏压、xion、衬底厚度、NiO/HfO₂、Fe、粒子源、输出时间共同变化。没有同一结构的 OFAT 对照，不能说“因为 DevEdit 所以没有漏—源通路”。

## 5. 网页端需要独立裁决的三个问题

1. 是否接受把两个历史案例标为 `TERMINAL_DEFINED_PHASE2_POSITIVE`，同时保留 `FORMAL_SPATIAL_PHASE2_NOT_EVALUABLE`？
2. 第一历史案例缺生成 deck；在无法恢复 deck 时，它是否只能作为现象参考而不能作为参数母线？
3. 若未来另行授权新实验，最小可证伪实验应否固定同一结构/物理/偏压/粒子源，只比较：
   - 原 mesh STR；
   - 从同一结构重建的 DevEdit mesh；
   - 相同 accepted 时间点和相同 `Jn` 横截面通量闭合；
   而不是继续跨结构调材料参数？

## 6. 授权边界

本文件只恢复证据与问题，不继承任何执行权：

```text
NO_SSH_AUTHORIZATION
NO_SIMULATION_AUTHORIZATION
NO_DECK_MODIFICATION_AUTHORIZATION
NO_NEW_RUN_AUTHORIZATION
NO_PARAMETER_SWEEP_AUTHORIZATION
```

## 7. 可直接发给网页端的提示词

```text
请完整读取本交接文档，并区分以下三层：
1. raw 三端电流配对事实；
2. Revision 4 正式空间 Phase 2；
3. 热失控 SEB。

请不要沿用“DevEdit RUN 完全没有漏—源配对”的旧前提，因为 accepted 日志已经显示
RUN038–040/RUN096 也存在后段漏—源配对。请独立审查两个历史 mesh 案例能证明什么、
不能证明什么，并回答第5节三个问题。不得把审阅解释为 SSH、仿真、修改 deck 或新 RUN 授权。
```
