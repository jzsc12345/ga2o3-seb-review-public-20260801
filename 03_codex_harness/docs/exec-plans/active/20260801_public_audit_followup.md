# Active plan — public audit follow-up

## 目标

关闭公开审计留下的两个真实缺口：参数闭包留痕，以及 Wang Table II impact 参数一致性；同时不重复 UID/mesh 盲扫。

## 阶段与闸门

### A. RUN120 parser-only

- 从 RUN096 复制到新 deck；不改任何材料数值。
- 只运行到 `MODELS PRINT + solve init`。
- 逐区抽取 Eg、χ、ε、Nc/Nv、τn/τp、Auger、incomplete、mobility、impact、κ、C。
- 若任何激活模型仍依赖无法说明的父材料槽位，STOP，先查 atlas.key/手册/例子。

### B. ANALYSIS096-H04

- 不跑 ATLAS；只读现成 50/100/500 ns STR。
- 同色标输出 Je、Joule heat、electron、ionized Fe 四类二维图及轻量 CSV。
- 定位从漏极到源极的首个连通断点；不得只看峰值。

### C. RUN121 z-axis impact OFAT

- 单变量：`2.16e6/1.77e7` → Wang Table II `7.06e5/2.10e7`，电子/空穴成对替换。
- 其余 SHA 冻结；先静态 1000 V 准入，再到 500 ns。
- 预期：impact、后段电流和温升下降；若相反，触发求解分支审计。

## 成功条件

- 参数闭包表每项都有 deck 行、运行回显和证据标签。
- 空间图能指出持续通道在哪一层、哪个 x 区间、哪个时间段断开。
- z/Y 比较只宣称晶向敏感性，不把更弱的 z 组包装成升温修复。

## 禁止事项

- 不改 RUN096 正本。
- 不把 `user.default=Ga2O3` 当作未经 parser 验证的机械替换。
- 不混改 UID、衬底和 mesh 来“调到收敛”。
- 未核签 A13/A14 四件包前不发射 RUN120/RUN121。
