---
name: report-writer
description: Generate two kinds of research reports from the project's handoff chain — (A) group-meeting PPTX where physics reasoning text dominates over figures, with dedicated concept-explainer pages for every obscure semiconductor term, and (B) outsider-facing illustrated HTML explainers. Use when the user asks for 汇报/组会PPT/进展汇报/科普图解/给老师看的/给外人看的. Templates reverse-engineered from the user's own accepted reports.
---

# report-writer — 组会 PPT 与科普图解生成

> 源材料永远是 handoff 链：`docs\HANDOFF_*.md` + `docs\AGENT_运行日志` §4 + 冻结计划书 + 论文框架。
> 两种体裁**侧重相反**：A 给自己/课题组（推理密度优先），B 给外人（先扫盲后看图）。
> 模板锚点（用户已验收的真实样例，风格以它们为准）：
> A = `d:\WeChat Files\...\2026-07\组会汇报_MIS-HEMT_HPM损伤机理进展_20260711.pptx`（19 页实测解剖见 §2）
> B = `d:\WeChat Files\...\2026-07\MIS介质击穿双稳态图解报告.html`

## 1. 体裁选择

| 问句特征 | 体裁 |
|---|---|
| 组会/导师/进展汇报/中期 | **A：PPTX**（文字推理为主） |
| 给外人/科普/朋友能看懂/分享 | **B：HTML 图解**（钩子问题+扫盲+图） |

## 2. 体裁 A 解剖（从真实模板逆向，页均 ~270 字、图 0-2 张/页）

19 页骨架照抄其节奏，替换内容：

```
p1  标题页（主标题 + 三个关键词副标）
p2  本期进展一页看板（表格：做了什么/结论/证据在哪）
p3  研究定位：查新空白 + 实验/文献锚定
p4  方法体系（校准链 + 判据体系，本项目= LET换算链+WKJ判据+温度判据）
p5-9   发现①②③…每个发现 1-2 页：机理箭头链为主体，图只当证据；
       每个发现配「电学指纹/判据可自动化」一句
★科普页：每引入一个晦涩概念（半绝缘衬底/深能级/碰撞电离/RESURF电荷平衡/闩锁…）
       单独插 1 页：大白话定义 → 括号比喻 → 一条箭头因果链 → 为什么本项目在乎它
p10-12 矩阵/全家福/自检页（DoE 结果表、拟合对齐性）
p13    超出预期的新现象（诚实列，没有就删此页）
p14    与实验/文献的对应 + 模型边界声明（诚实：拟合到什么程度、没拟合什么、为什么）
p15-17 深挖链（本项目= 热失控正反馈链 / 加固结构机理 / 假设的定量验证）
p18    进行中与下一步（对齐 8 周计划当前格）
p19    结论（≤4 条，每条带证据指针）
```

硬性风格（沿承 `silvaco\HANDOFF_..._ADDENDUM` §10 的既有验收口径）：
约 20-24 页不回 34 页堆料稿；deck 语法/求解器细节**进备注栏**不进正文；
每页最多两图，图旁必标偏置/LET/时间/单位/证据状态；表格少用，期刊式因果分析多用；
关键结论可加粗标红，但不要代码感版式。

## 2.5 体裁 C/D（本项目已验收的另两种真稿，按需选用）

**C · STR 机理叙事**（模板 `...\2026-07\Ga2O3_SEE_SEB_midterm_STR_mechanism_v6.pptx`，17 页实测）：
编号物理章节推进（1 场板电静力学 → 2 多物理耦合 → 3 校准+分岔 → 4.1-4.4 载流子动力学 → 5 抗 SEB 设计
→ 7 证据边界 → 9 方法复盘）；特征页型=**快照族页**（一页 4-8 张同标量不同时刻的 2D 图，
如"4.4 雪崩再生"一页 8 图）——机理演化用图阵讲，文字压到 ~300 字/页。适合：机理深挖专场。

**D · 证据审计**（模板 `silvaco\outputs\...\Ga2O3_SEE_SEB_midterm_journal_evidence_v2.pptx`，34 页实测）：
全大写英文节头的 qualification 链（DEVICE DEFINITION → MESH/MATERIAL/PHYSICS QUALIFICATION →
分 STAGE 逐层证据 → STR PROVENANCE → REPEATABILITY → EVIDENCE CLOSURE → NEXT MATRIX）；
页均 400-700 字、图仅 0-2 张当证物。适合：审稿式自查、答辩前证据链固化。
体裁选择追加：机理专场→C；证据自查/预答辩→D；常规组会→A；对外→B。

## 3. 体裁 B 解剖（给外人）

```
h1 = 钩子问题（"同一器件同一电压，为什么一个烧到1500K一个只到600K？"式）
① 先认识 N 个词（扫盲节置顶！每词=大白话+括号比喻，不许行话）
②-⑥ 编号可视化节：每节一张主图（温度曲线/电流/2D等高线/机理示意）+ 一段人话解读
⑦ 这对论文意味着什么（收口到价值）
```
自包含 HTML（内联 style/script），图用本地 png 相对引用或 base64。

## 4. 生成流程

```
① 收集：按时间读 handoff 链，抽「发现/证据/未决」三类条目
② 提纲：写 outputs\reports\<名>_outline.md（§5 语法）给用户过目（体裁A可跳过直接生成初版）
③ 生成：python scripts\make_report_pptx.py <outline.md> [-o out.pptx]   # 体裁A
        体裁B直接手写 HTML（或用 Artifact 预览后落盘）
④ 图源：优先用 outputs\ 已有截图/等高线；缺的图列「待补图清单」占位灰框，不硬凑
⑤ 交付：文件落 outputs\reports\，运行日志留痕；不覆盖用户唯一主稿（另存新名）
```

## 5. outline.md 语法（生成器契约）

```markdown
# 幻灯片标题            ← 每个一级标题=一页
正文行（每行一个要点或一段推理；行内箭头→保留）
![说明文字](D:\...\fig.png)   ← 本页配图（≤2张）
> 备注栏内容（deck语法/求解器/出处都放这）
---koupu: 概念名        ← 该行触发插入科普页模板（定义/比喻/箭头链/为何在乎）
```

## 6. 红线

不发明数据——每个数值必须能指回 handoff/运行日志/论文框架；拟合没到位就写"没到位+原因+补法"
（模板 p14 的模型边界声明是必备页，删了=不合格）；两种体裁不混体——组会 PPT 里塞大图少字
或科普 HTML 里堆推理密文都算跑偏。
