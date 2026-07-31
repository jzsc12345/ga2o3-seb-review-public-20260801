# Public repository audit adjudication — 2026-08-01

审计对象：`jzsc12345/ga2o3-seb-review-public-20260801`  
裁决原则：先认 deck/CSV/STR/PDF 原表，再认后写说明；不因审计措辞强烈就直接改生产 deck。

## 1. 逐项裁决

| 审计项 | 裁决 | 理由与证据 |
|---|---|---|
| P0-1 尚未复现 Wang2026 | 接受 | RUN096 仅 394.152 K，后段电流持续衰减；这是状态闸门，不是新发现的代码缺陷。 |
| P0-2 RUN119 无有效瞬态 | 接受 | `outputs/runs/RUN119.../README.md:74`：878.9508057 V、16 次折半、首个 2 ps 前停止。 |
| P0-3 `user.default=GaN` 导致未知继承 | **降为 P1“参数闭包尚未完整留痕”** | 不能仅由 parent 名字判定实跑 GaN。RUN096 在 `decks/RUN096...in:187-284` 已逐区显式给出 Eg/χ/ε/Nc/Nv、SRH、Auger、incomplete、热学、电子/空穴 Caughey、FLDMOB 和 IMPACT；现有 STR CSV 也实测回显 Eg=4.85、Nc=3.718e18、Nv=6.44e20、τ=1.2e-8、κ=0.27、C=3.332。剩余问题是没有把 `MODELS PRINT` 的逐区闭包表归档，不是已经证明“GaN 六模型在跑”。 |
| P1-1 Y 晶向偏离 Wang Table II | 接受 | Wang2026 Table II 明列 AN/AP=7.06e5 cm⁻¹、BN/BP=2.10e7 V/cm；RUN096 `:270-284` 使用 Y 组 2.16e6/1.77e7。当前 Y 组只能标为保守晶向敏感性臂，不能标为论文参数基线。 |
| P1-2 线接触/`common=gate` 证据不足 | **降为 P2 文档缺口** | 当前最终几何是 no-FP，根本不存在 `gate_fp`，所以 `common=gate` 对 RUN096 不适用。源/漏/栅均为 DevEdit 零面积 line-region（`:134-139`）；RUN093/RUN094 已记录 11,672 点、22,992 三角形、0 error/warning。若未来恢复 FP，才必须重新验 `common=gate` 与端点节点。 |
| P1-3 n 型背景 + Fe 深受主 | 接受 | `nd_sub=1.5e15`、`Nt=2e18`、`Ec-Et=0.8 eV`、`σ=5e-15 cm²`；没有 p-type 2e6。 |

## 2. 对三个建议实验的反审计

### 2.1 不接受“直接把 user.default 改成 Ga2O3 后跑完整瞬态”

原因：`user.default` 是 user material 的父材料，不是把自定义材料名再指向自身的普通替换项；直接换 parent 会同时改变未知数量的默认槽位，既可能 parser 失败，也不是严格单变量。

替代方案：先做 parser-only 参数闭包审计，只执行 `MODELS PRINT + solve init`，逐区对照目标表。任何未显式闭合且影响已激活模型的槽位先列出，不跑高压、不打粒子。

### 2.2 接受 z/Y 晶向对照，但驳回审计者的方向性预测

Selberherr 单段近似 `alpha=a*exp(-b/E)` 下：

| E (MV/cm) | alpha_Y (cm⁻¹) | alpha_Z (cm⁻¹) | Y/Z |
|---:|---:|---:|---:|
| 2 | 309.70 | 19.44 | 15.93 |
| 3 | 5917.20 | 643.79 | 9.19 |
| 4 | 25864.30 | 3704.75 | 6.98 |

所以 Y 组在相关场强下比 Wang 的 z 组强约 7–16 倍。换回 z 组是**论文一致性修正**，物理预期是更弱雪崩、更低温升，而不是更容易形成持续电流丝。若 z 组反而显著升温，应优先怀疑求解分支或场分布改变。

### 2.3 拒绝“放宽 UID/衬底或 mesh 直到 1000/1200 V”

RUN096 已经在同一最终几何建立 1000 V 静态母态；RUN119 只把 UID donor 加倍后反而在 878.95 V 失去静态准入。因此“只要静态母态建立就出现四阶段”的实验前提已经被 RUN096 否定。把 UID、衬底和 mesh 混在一起调到收敛还会把物理变量与数值变量混淆。

替代方案：先用 RUN096 现成 STR 做 50/100/500 ns 的电子电流、Joule 热、电子浓度、带电 Fe 同色标二维连通图，定位导电丝具体在哪一层断掉；这是零 ATLAS 机时、可直接证伪的分析。

## 3. 冻结后的下一步顺序

1. **RUN120 parser-only 参数闭包**：不爬压、不打粒子；输出逐区材料/模型矩阵。
2. **ANALYSIS096-H04 零机时空间闭包**：补四时刻同色标 Je/Joule/electron/Fe 图。
3. **RUN121 z-axis 严格 OFAT**：仅在前两项通过后，把 IMPACT Y 组换成 Wang Table II z 组；其余结构、网格、LET、Fe、热模型、solver 和时间表全部冻结。

在 RUN120/RUN121 的 A13/A14 四件包核签前，不修改 RUN096 正本，不发射生产仿真。
