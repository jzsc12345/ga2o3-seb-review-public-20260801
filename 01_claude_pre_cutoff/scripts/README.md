# scripts\ — 自动化脚本（只放 `.py`）

> 本目录是主控端与远端 Silvaco VM 之间的全部自动化封装。**只允许 `.py` 与本 README**。
> 布局合规由 `check_layout.py` 检查（烟测 S0 步）。

## 运行链路脚本（核心四件）

| 脚本 | 用途 | 典型命令 |
|---|---|---|
| `silvaco_remote.py` | SSH 控制层：双 IP 探测 / GUI 会话环境注入（XAUTHORITY+DBus）/ deckbuild pty 后台启动 / 轮询 / 大文件归档 E 盘 | `python silvaco_remote.py preflight` |
| `lhd_pareto.py` | B12 寻优回路：LHD 拉丁超立方采样 → aux.in SWEEP list 生成 + 帕累托前沿判定 + 收缩箱迭代（victorydoe_ctl.py 已随废案归档删除） | `python lhd_pareto.py pareto outputs\reports\sweep_bv_summary.csv` |
| `screenshot_watch.py` | 每 N 秒抓 VM 桌面截图到 `outputs\<session>\screenshots\`，可 `--until-status` 跟随运行 | `python screenshot_watch.py --session X --interval 180` |
| `inbox_watch.py` | 常驻看守 `inbox\`：二号机结果包到货自动解包/统计/出对比图/写 REPORT/追加运行日志 | `python inbox_watch.py --interval 60` |

## 离线双机

| 脚本 | 用途 |
|---|---|
| `make_offline_bundle.py` | 把 golden deck + split 展平成零依赖 case.in（数值字面量化、宏消除、E1 修正内嵌），打包给二号机 |

## 物理计算小工具（可独立运行，结论已进 knowledge\）

| 脚本 | 结论 |
|---|---|
| `let_calc.py` | LET 换算（10⇒0.0604 / 75⇒0.4529 / 81.5⇒0.492 pC/µm，三点交叉验证） |
| `impact_axis_compare.py` | 晶向电离系数 x/y/z 对比；现 deck 系数低 3-4 量级 |
| `sub_leak_estimate.py` | n 1.5e15 衬底旁路漏电量级（与实测 Jt=3.13e-6 A/µm 吻合） |
| `ni_and_substrate_choice.py` | p=2e6 假半绝缘数值不可行，深受主补偿才是正路 |

## 布局与守则

| 脚本 | 用途 |
|---|---|
| `check_layout.py` | 全仓布局合规检查（各目录允许扩展名、skills 冻结校验），烟测第一步跑它 |

**三大坑已封装勿重踩**：deckbuild 必须 pty（xterm+script）；GUI 必须会话环境注入；
subprocess 发远端脚本必须 bytes（text=True 会 CRLF 污染）。细节见根 README §4。
