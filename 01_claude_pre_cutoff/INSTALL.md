# INSTALL — SILVACO_LOCAL 框架安装教程（GitHub 风格）

> 把「agent 主控 + Silvaco VM + 四库知识体系」装到一台新电脑（朋友的机器 / 二号机）。
> 打包：`python scripts\pack_framework.py` → 生成 `SILVACO_LOCAL_framework_<日期>.zip`。

## 0. 前置条件

| 项 | 要求 |
|---|---|
| 主控端 | Windows 10+，Python 3.10+（含 numpy/pandas/matplotlib），git，OpenSSH 客户端 |
| 计算端 | VMware 里的 Silvaco 2024 VM（RHEL7，含 ATLAS 5.40.0.R / VictoryDoE / SFLM 许可证），桌面已登录 |
| agent | Codex / Claude Code 任一（无 agent 也可手动跑 scripts） |

## 1. 安装五步

```powershell
# ① 解包框架到 D:\
Expand-Archive SILVACO_LOCAL_framework_*.zip -DestinationPath D:\
# 得到 D:\SILVACO_LOCAL\（框架）；四库知识库单独拷贝到 D:\knowledge\（material_sil/pdf25/exp25/paper）

# ② 配 SSH 免密（把公钥装进 VM）
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\silvaco_ed25519 -N '""'
type $env:USERPROFILE\.ssh\silvaco_ed25519.pub | ssh root@<VM_IP> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
# 然后编辑 scripts\silvaco_remote.py 顶部 HOST_CANDIDATES 为你的 VM IP（可填多个候选）

# ③ 大文件归档盘（按本机实际改盘符后，同步改 silvaco_remote.py 的 BULK_ROOT）
mkdir E:\silvaco2425\bulk\str, E:\silvaco2425\bulk\log

# ④ 首验（三连）
cd D:\SILVACO_LOCAL\scripts
python check_layout.py            # 布局合规
python silvaco_remote.py preflight # VM 连通+工具链（烟测 S1）
git log --oneline | Select -First 3  # 版本历史在

# ⑤ VM 端部署长任务驱动
scp scripts\remote\vdoe_tmux.sh root@<VM_IP>:/root/bin/ ; ssh root@<VM_IP> "chmod 755 /root/bin/vdoe_tmux.sh"
```

## 2. 验收 = 跑 GUI 烟测

按 `skills\victorydoe-gui-flow\references\smoke-test.md` 的 S1→S11 逐步执行，全绿即安装成功。

## 3. 给 agent 的启动指令（复制到新窗口第一句）

```text
工作目录 D:\SILVACO_LOCAL。先读 README.md，再按 skills\handoff-longmemory\SKILL.md 的
启动动作执行：读 knowledge\CONSTRAINTS_用户约束账本.md（特别是 §R 撤回区）→
docs\AGENT_运行日志 §4 末 20 行 → 最新 HANDOFF。遇仿真问题按 D:\knowledge 四库检索，禁止猜参数。
```

## 4. 目录速览（详见各目录 README.md）

```
SILVACO_LOCAL\  README.md INSTALL.md .git\
├ knowledge\  本器件分析结论 + 约束账本 + 错误知识库
├ docs\       handoff/运行日志/论文框架/计划
├ decks\      仿真 deck（原始基线在根：SEB.in mySEU.c 勿动）
├ scripts\    自动化（remote/DoE/截图/离线包/看守/巡检/错误提取；remote\vdoe_tmux.sh 部署到 VM）
├ outputs\    png/csv/报告（errors\ 收错误截图）
├ skills\     🔒 冻结技能包 ×2 + handoff-longmemory 协议
├ inbox\      二号机结果包投递口
└ archive\    归档收容
```

## 5. 二号机纯离线模式（无 agent 的电脑）

不需要装框架——只要 `outputs\offline\OFFLINE_*.tar.gz` 一个包：
拷进 VM → `tar xzf` → `nohup bash runner/run_all.sh &` → 把生成的 `RESULTS_*.tar.gz`
拷回一号机 `inbox\`。详见包内 `README_操作手册.md`。

## 6. 常见安装问题

| 症状 | 解法 |
|---|---|
| preflight 连不上 | VM IP 漂移：`HOST_CANDIDATES` 填全候选；VM 桌面必须已登录 |
| GUI 打不开 | 不是 bug，是 XAUTHORITY——脚本已封装，手动操作看 README §4 |
| deckbuild 挂死 | 必须 pty：用 vdoe_tmux.sh 或 xterm+script 包裹，别裸跑 |
| git 提示 CRLF | 无害；框架混合换行符，已在 .gitignore/流程中处理 |
