# OFAT A/B 统一端电流后处理合同（规范稿）

> Status: SPECIFICATION ONLY / NOT RUN
>
> 本文件不包含 mock 数据，不对不存在的瞬态输出作分类。

## 1. 输入合同

未来每臂必须提供：

1. 同一 VGS/VDS、source 严格关闭时的 5 个 accepted baseline 点；
2. raw `Id/Is/Ig`、原始单位、device width 来源、terminal sign mapping；
3. 同一套预声明 accepted 时间点，至少含 10/20/50/100 µs；
4. solver accepted/rejected 状态和实际偏压；
5. A/B 各自独立建立的静态母态证据。

缺少任一输入时，相应指标写 `NOT_EVALUABLE`，不得填零或插值。

## 2. 单位、基线与 floor

先把每个 terminal 转换成 A/µm，并记录公式。随后对 terminal `k` 计算：

```text
I0_k    = median(I_k,pre)
MAD_k   = median(abs(I_k,pre - I0_k))
floor_k = max(1e-12 A/µm, 5 * MAD_k)
dI_k(t) = I_k(t) - I0_k
```

current-defined candidate 的绝对门：

```text
I_SEB_GATE = max(floor_d, floor_s, 1e-6 A/µm)
```

`1e-6 A/µm = 1 mA/mm`。这不是静态 BV 门，也不是 thermal-runaway 门。

## 3. 三端配对与 KCL

在分母高于相应 floor 时计算：

```text
raw_KCL = abs(Id + Is + Ig) / max(abs(Id), abs(Is), abs(Ig))
err_DS  = abs(dId + dIs) / max(abs(dId), abs(dIs))
err_KCL = abs(dId + dIs + dIg) / max(abs(dId), abs(dIs), abs(dIg))
```

通过门：

- `raw_KCL <= 5%`；
- `err_DS <= 10%`；
- `err_KCL <= 10%`；
- dId 与 dIs 异号；
- 至少 3 个连续 accepted 点满足。

低于 floor 时比例写 `NOT_EVALUABLE`，不得用极小分母制造配对结论。

## 4. 10–100 µs 晚窗口

### 4.1 恢复到 floor 的 SET 分支

若此前存在可分辨峰值，并且：

- dId、dIs 在至少两个连续晚期 accepted 点低于各自 floor；
- 之前的衰减段 KCL 合格；
- 50→100 µs 没有二次回升；

则允许判 `SET_LIKE_CURRENT_RESPONSE`，不强迫对 floor 以下点拟合对数斜率。

### 4.2 高于 floor 的趋势分支

对 10/20/50/100 µs 中可评估点计算：

```text
Rlate = abs(dId_100us) / max(abs(dId_10us), floor_d)
Slate = slope(log10(abs(dId)), log10(t))
```

漏、源两端必须给出一致趋势，不能只看 drain。

### 4.3 四段带符号电荷积分

统一只在 postprocess 中对 raw 或 baseline-subtracted terminal current 做四段积分：

```text
Q1: strike start -> 10 ns
Q2: 10 ns -> 1 us
Q3: 1 us -> 10 us
Q4: 10 us -> 100 us
```

每段分别积分 Id、Is、Ig，并报告 `Qd+Qs+Qg` 闭合；deck 不承担积分或标签逻辑。

## 5. 一级结果与优先顺序

固定决策顺序：

1. 配置、结构或等价合同失败 → `OFAT_INVALID`；
2. 合法配置在必要证据前求解失败 → `NUMERICAL_TERMINATION`；
3. 到达 100 µs 但趋势仍未决 → `INSUFFICIENT_TIME_WINDOW`；
4. 满足持续衰减或 recovered-to-floor 分支 → `SET_LIKE_CURRENT_RESPONSE`；
5. 晚窗口中漏/源持续异号配对、KCL 合格、明显高于基线且持平或增长 →
   `CURRENT_DEFINED_SEB_CANDIDATE`。

该结果不等于：

- Revision 4 `FORMAL_SPATIAL_PHASE2_CONFIRMED`；
- `THERMAL_RUNAWAY_SEB`。

前者还需要同一保持区间 early/middle/late 三帧 `Jn` 源漏连通与横截面通量闭合；后者还需要后段
current/impact/Tmax 正反馈。

## 6. A/B 数值比较

仅当静态等价门先通过，才比较：

- 每个 accepted 时刻 raw 与 baseline-subtracted Id/Is/Ig 的对称相对误差；
- 电流低于 floor 时的绝对差；
- current-only 一级分类是否一致；
- structure build、static bias、future transient 三段 wall time；
- accepted-step、rejected-step、cutback 数；
- 相同时间点的输出完整率。

当前没有可用 A/B 运行数据，因此：

```text
POSTPROCESS_IMPLEMENTATION = SPECIFIED_NOT_IMPLEMENTED
POSTPROCESS_EXECUTION = NOT_RUN
CURRENT_ONLY_VERDICT = NOT_EVALUABLE
```

