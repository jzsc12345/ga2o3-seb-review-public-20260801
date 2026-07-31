# skills\ — 技能包（🔒 冻结区）

> **本目录下的两个技能包已封版，后续不再修改。**
> 允许的文件类型：`.md` / `.py` / `.sh` / `.json`，其余一律不准进入
> （由 `scripts\check_layout.py` 强制检查）。发现缺陷不改包本体——
> 把勘误写到 `docs\` 并在此 README 登记指针。

## 包清单

| 包 | 定位 | 状态 |
|---|---|---|
| `silvaco-tcad\` | **通用方法论**：Sentaurus 技能包的 Silvaco 移植（preflight/结构网格/物理求解/批量运行/辐照 SEB/结果报告 6 篇 references） | 🔒 已封版。经 285-token 逐条核实 + 复审修复，可用性 8/10；账目见包内 `AUDIT_修复报告_20260726.md` |
| `victorydoe-gui-flow\` | **GUI 强制可见工作流**：SWB-GUI 哲学移植（VictoryDoE 工程树 + xctl 点击 + 截图留痕 + VictoryExtract/Visual 后处理 + 11 步烟测教程） | 🔒 已封版。新眼验收通过（无发明菜单名/无死链/烟测依赖闭合） |
| `handoff-longmemory\` | **自制长记忆协议**：约束账本（含撤回区防旧要求复活）+ 会话四动作（启动回读/实时留痕/checkpoint/交接）+ 防跑偏自检 + git 防篡改 | 🌱 活协议（允许迭代完善，非冻结；配套 `knowledge\CONSTRAINTS_用户约束账本.md`） |
| `report-writer\` | **汇报生成**：体裁 A 组会 PPTX（推理文字压倒图片、晦涩概念自动插科普页、模型边界声明必备页）+ 体裁 B 外人向图解 HTML（钩子问题+扫盲节置顶）。模板逆向自用户已验收真稿；配套 `scripts\make_report_pptx.py`（outline.md→pptx，自测通过） | 🌱 活协议 |

## 三区分工（引用时别搞混）

- `skills\` = **怎么做**（通用方法论，跨项目可复用，冻结）
- `D:\knowledge\` + `SILVACO_LOCAL\knowledge\` = **查什么**（四库一手资料 + 本器件分析结论）
- `docs\` = **做过什么**（本项目实录/handoff/框架/日志）

## 勘误登记

（暂无。发现问题写 `docs\skills勘误_<日期>.md` 后在此加一行指针。）
