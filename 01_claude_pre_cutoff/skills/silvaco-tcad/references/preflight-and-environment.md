# Preflight 与环境体检：Silvaco TCAD 首次运行前必做

本文件是**新设备/新服务器/新会话首次运行 Silvaco TCAD 前的完整体检清单**，每项给出「检查命令 / 期望输出 / 失败含义与处置」，并附一个可直接跑的最小 license probe deck。

> **标注约定**（与本 skill 其它 reference 一致）：
> - `[已核实: <证据>]` —— 当场跑过命令并贴得出非空输出。证据形式为 `atlas.key:<行号> <行内容>`、
>   `远端 <命令> → <输出>`、或 `examples/deckbuild/5.2.40.R/<deck> 原文`。
> - `[未核实]` —— **查不到就是查不到**，保留原文不删，读者据此自行确认。
> - 本文件的远端事实核验时间：**2026-07-26**，核验主机 `tcad`。环境类事实（IP、磁盘、locale）
>   会随时间漂移，超过一周请按本文命令**重跑一遍**，不要沿用旧结论。

---

## 0. 目标与红线

在一台新机器、新远端主机或新会话里，**不要**直接写 `.in` deck、不要直接 `deckbuild -run`。先确认：SSH 可达、Silvaco 环境已加载、可执行文件存在、ATLAS 版本可枚举、SFLM 许可可 checkout、DISPLAY 可用（或明确降级）、并行度合理、磁盘有余量、项目根可写、locale 正常。

> **硬规则：Preflight 未通过 → 停止仿真计划，向用户报告阻塞项。**
> 不要把环境错误误判成物理模型问题。
> `ATLAS DIED`、`license` 报错、`command not found`、`Permission denied`、`No space left on device`
> **都不是收敛问题**，改 `method` / `models` / 网格 / 掺杂**一个都修不好**。
> 在 preflight 全绿之前，禁止调整任何物理模型或数值参数来"试着让它跑通"。

### 不做的事

- 不安装、不破解、不 patch Silvaco TCAD。
- 不读取、记录、或要求用户提供 license 文件内容、SFLM server 地址以外的凭据、账号、密码、token、SSH 私钥内容。
- 不把 proprietary manual、`$SILVACO/examples/` 原文、license 文件复制进 skill 仓库。
- 不在未知目录中删除、覆盖、移动文件。
- 不往 `/mnt/hgfs/*` 写大文件、更不作运行工作目录（HGFS 语义差异 + 其中一个已 98% 满，见 §9）。
- 不把任一 IP 硬编码进 runner 脚本（见 §1）。

---

## 1. SSH 可达性与实际 IP 探测

### 1.1 已知事实

- 远端主机名：`tcad`，RHEL 7 (kernel 3.10.0-1160.el7.x86_64)，8 vCPU / 8 GB RAM，`/` 剩余约 124 GB。
  [已核实: 远端 `hostname; uname -r; nproc; free -g` → `tcad` / `3.10.0-1160.el7.x86_64` / `8` / `Mem: 7 ...`]
  [已核实: 远端 `df -h /` → `/dev/mapper/rhel-root 191G 68G 124G 36% /`]
- 当前可用连接：
  ```bash
  ssh -i C:/Users/Administrator/.ssh/silvaco_ed25519 root@192.168.50.134
  ```
  [已核实: 远端 `ip -4 -o addr show` → `2: ens33  inet 192.168.50.134/24 ... dynamic ens33  valid_lft 915sec`]

> **⚠ 本节原有的"IP 陷阱"整段是错的，已按实测更正（2026-07-26 复核）。**
> 原文写「当前可用 = `192.168.107.128`，别名 `silvaco` 指向已失效的 `192.168.50.134`」，
> **实测方向完全相反**：
>
> | 地址 | 实测结果 | 证据 |
> |---|---|---|
> | `192.168.50.134` | **活的，就是 `tcad`** | `ssh ... root@192.168.50.134 "hostname; uname -r; nproc"` → `tcad` / `3.10.0-1160.el7.x86_64` / `8` |
> | `192.168.107.128` | **连不上** | `ssh -o ConnectTimeout=6 ... root@192.168.107.128 hostname` → `kex_exchange_identification: read: Connection reset by peer` |
> | `~/.ssh/config` 别名 `silvaco` | **指向 `192.168.50.134`，即当前有效地址** | 本机 `~/.ssh/config`：`Host silvaco` / `HostName 192.168.50.134` / `User root` / `IdentityFile C:/Users/Administrator/.ssh/silvaco_ed25519` |
>
> - **真正的陷阱不是"别名过期"，而是 `ens33` 走 DHCP（`valid_lft 915sec`）**——地址随租约变动，
>   任何写死的 IP（包括本文这两个）都可能在下一次开机后失效。
> - 因此规则不变、理由更新：**每次会话开头必须先探一次 IP 并核对 `hostname` 是否为 `tcad`**，
>   不要凭记忆里的地址、也不要凭本文档里的地址直接开跑。
> - 注意 `Connection reset by peer` ≠ `Connection timed out`：前者说明该 IP 上**有别的主机/服务**在应答，
>   更要核对 `hostname`，绝不能在陌生机器上写文件（见 §1.3 末行）。

### 1.2 IP 探测候选项

| 候选 | 做法 | 备注 |
|---|---|---|
| **[默认] 显式 IP + 显式 key** | `ssh -i <key> -o ConnectTimeout=5 root@192.168.50.134 hostname` | 最快、最可控；每次会话开头先探一次。[已核实: 该命令 2026-07-26 返回 `tcad`] |
| 遍历候选 IP 列表 | 对 `192.168.50.134 192.168.107.128 ...` 依次 `ConnectTimeout=3` 探测 | 虚拟机 DHCP 租约到期/网段变动后用；**探到就必须再验 `hostname`** |
| 读 `~/.ssh/config` 再校验 | `ssh -G silvaco \| grep -i hostname` 拿到别名解析结果**再**探测 | 本机别名当前解析到 `192.168.50.134`，与实测一致；仍然只用来读值，不要默认它是活的 |
| `arp -a` / `ping` 扫网段 | Windows 侧 `arp -a \| findstr 192.168.50` | 前三种都失败时的兜底 |

> **runner 脚本必须把 IP 作为变量/参数，探测成功后再赋值**，不要写死。

### 1.3 检查命令 / 期望输出 / 失败处置

```bash
# 主控端 (Windows, Git Bash 或 PowerShell 均可)
ssh -i C:/Users/Administrator/.ssh/silvaco_ed25519 \
    -o ConnectTimeout=5 -o BatchMode=yes \
    root@192.168.50.134 'hostname; uname -r; nproc; free -g | head -2'
```

期望输出 [已核实: 下面是 2026-07-26 该命令的**实际**输出，非示意]：

```text
tcad
3.10.0-1160.el7.x86_64
8
              total        used        free      shared  buff/cache   available
Mem:              7           1           0           0           5           5
```

| 现象 | 含义 | 处置 |
|---|---|---|
| 返回 `tcad` + 内核号 | SSH 通，主机身份正确 | 继续 §2 |
| `Connection timed out` | IP 变了 / 虚拟机没起 / 网段变动 | 按 §1.2 候选项重新探测 IP；**不要**改 deck |
| `kex_exchange_identification: read: Connection reset by peer` | 该 IP 上有东西在应答但不是我们的 sshd（旧地址被别人占用/服务未起） | 同上重新探测；**绝不**继续用这个地址。[已核实: `192.168.107.128` 2026-07-26 即为此现象] |
| `Permission denied (publickey)` | key 路径错或 key 未授权 | 核对 key 路径；不要把私钥内容贴进会话 |
| `Host key verification failed` | 虚拟机重建过 | 让用户确认后清理该条 known_hosts，不要自动 `-o StrictHostKeyChecking=no` 长期使用 |
| 返回的 hostname 不是 `tcad` | 连到了别的机器 | 停止，报告给用户，绝不在陌生机器上写文件 |

> **远端整机不可达（VM 关机）时**：停止提交与一切远端核对，报告阻塞项；期间参数/语法/物理核对可降级用
> 本地只读镜像 `D:\knowledge\{pdf25,exp25,material_sil}`（`atlas_users1.pdf` 手册 / 官方例子 `.in` / 材料参数库），
> 离线写的 deck 草稿标 `[未核实]`，凡只能由远端 `atlas.key` 裁决的结论一律标 `[待 atlas.key 复核]`。

---

## 2. Silvaco 安装根、PATH 与 silvaco.profile

### 2.1 已知事实

- 安装根：`/atctools/Synopsys/Silvaco2024`（下称 `$SILVACO`）。
  [已核实: 远端 `ls -d $SILVACO/bin $SILVACO/lib $SILVACO/examples $SILVACO/doc` → 四个目录全部存在]
- 可执行文件在 `$SILVACO/bin/`：`deckbuild atlas athena devedit tonyplot tonyplot3d quest sflm ...`。
  [已核实: 见 §3.1 的 `command -v` 实测输出，8 个工具全部命中]
- **这些默认不在 PATH 中**。非交互 SSH（`ssh host 'cmd'`）不会读 `.bash_profile` 的全部内容，
  所以**每个远端命令都必须自己带环境加载前缀**。

### 2.2 环境加载候选项

| 候选 | 命令 | 说明 |
|---|---|---|
| **[默认] 显式 export PATH** | `export SILVACO=/atctools/Synopsys/Silvaco2024; export PATH=$SILVACO/bin:$PATH` | 唯一实测有效的方式；最小侵入。[已核实: 见 §3.1 实测] |
| ~~source 官方 profile~~ | ~~`source $SILVACO/etc/silvaco.profile`~~ | **[未核实 → 已证伪] 这个文件什么都不设，见下方警告框。不要用。** |
| 全绝对路径调用 | `/atctools/Synopsys/Silvaco2024/bin/deckbuild ...` | 一次性探测命令用；不适合长脚本 |
| 登录 shell 包裹 | `ssh host 'bash -lc "..."'` | 依赖用户 `.bashrc` 里已经 source 过；**不要单独依赖它** |

> **⚠ 原文把 `source 官方 profile` 列为 [默认] 并声称它"一次到位，同时设 `SILVACO`、PATH、license 变量"——这是错的。**
> 实测该文件存在，但**是一个只打印说明文字的 csh 脚本，不导出任何变量**：
>
> ```
> $ ls -l /atctools/Synopsys/Silvaco2024/etc/silvaco.profile
> -rwxr-xr-x 1 root root 315 12月 14 2018 .../etc/silvaco.profile
>
> $ cat /atctools/Synopsys/Silvaco2024/etc/silvaco.profile
> #!/bin/csh
> echo ""
> echo "Add <install_directory>/bin to your path, where"
> echo "<install_directory> is the pathname of your installation."
> echo ""
> echo "Delete the following two lines from your .profile/.vueprofile:"
> echo ""
> echo "	SILVACO=<your_install_directory>"
> echo '	. $SILVACO/etc/silvaco.profile'
> echo ""
> ```
>
> 三个后果：
> 1. 它**不设 `SILVACO`、不设 `PATH`、不设任何 license 变量**（全文 315 字节，只有 `echo`）。
> 2. 它是 `#!/bin/csh`，在 bash 里 `source` 属于跨 shell 误用；这里恰好只有 `echo` 才没出错。
> 3. `grep -n 'SFLM_SERVERS' silvaco.profile` **无输出** → `SFLM_SERVERS` 必须自己 export（见 §5.1）。
>
> 所以 `ENVPRE`（本节末）里的显式 export 不是"退路"，而是**唯一正确路径**。

### 2.3 检查命令 / 期望输出 / 失败处置

```bash
ssh -i <key> root@<ip> 'bash -s' <<'EOS'
export SILVACO=/atctools/Synopsys/Silvaco2024
# 不要 source $SILVACO/etc/silvaco.profile：它是只打印说明的 csh 脚本，什么都不设（见 §2.2 警告框）
export PATH="$SILVACO/bin:$PATH"
echo "SILVACO=$SILVACO"
echo "PATH_HEAD=$(echo $PATH | cut -d: -f1)"
ls -d "$SILVACO/bin" "$SILVACO/lib" "$SILVACO/examples" "$SILVACO/doc" 2>&1
EOS
```

期望输出 [已核实: 2026-07-26 实测输出]：

```text
SILVACO=/atctools/Synopsys/Silvaco2024
PATH_HEAD=/atctools/Synopsys/Silvaco2024/bin
/atctools/Synopsys/Silvaco2024/bin
/atctools/Synopsys/Silvaco2024/doc
/atctools/Synopsys/Silvaco2024/examples
/atctools/Synopsys/Silvaco2024/lib
```

> `$SILVACO/examples/` 下**只有三项**，deck 例子不在它的直接子目录里
> [已核实: 远端 `ls -1 $SILVACO/examples/` → `deckbuild` / `mkdbindex` / `victorydoe`]：
> ```text
> $SILVACO/examples/deckbuild/5.2.29.R/
> $SILVACO/examples/deckbuild/5.2.40.R/{Educational,Technology,Tool}/   <- 本项目对照用这个
> ```
> [已核实: 远端 `ls -1 $SILVACO/examples/deckbuild/` → `5.2.29.R` / `5.2.40.R`；
> `ls -1 $SILVACO/examples/deckbuild/5.2.40.R` → `Educational` / `Technology` / `Tool`]
> 后文凡写"去 `$SILVACO/examples/` 核对"，实际路径一律指
> **`$SILVACO/examples/deckbuild/5.2.40.R/`**（与冻结的 ATLAS `-V 5.40.0.R` 并非同一套版本号，别搞混）。

| 现象 | 含义 | 处置 |
|---|---|---|
| 四个目录都在 | 安装完整 | 继续 §3 |
| `PATH_HEAD` 不是 `$SILVACO/bin` | export 没生效（常见于误用 `bash -lc` 或误以为 profile 会代劳） | 显式 `export PATH="$SILVACO/bin:$PATH"`，见 §2.2 |
| `bin` 不存在 | 安装根路径错 | 停止；让用户给出实际安装根，不要猜其它路径 |
| `examples` 不存在 | 例子库未安装 | 降级：不得声称"已对照官方例子"；用户提供的例子或文献要注明来源 |
| `examples/deckbuild/5.2.40.R` 不存在 | 例子库版本不同 | `ls $SILVACO/examples/deckbuild/` 看实际版本目录，把实际版本记入 `findings.md`；本机另有 `5.2.29.R` |

> **本 skill 所有远端命令的标准前缀**（后文简称 `ENVPRE`）：
> ```bash
> export SILVACO=/atctools/Synopsys/Silvaco2024
> export PATH=$SILVACO/bin:$PATH
> export SFLM_SERVERS=+localhost
> export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
> ```

---

## 3. 可执行文件存在性

### 3.1 检查命令

```bash
ssh -i <key> root@<ip> 'bash -s' <<'EOS'
export SILVACO=/atctools/Synopsys/Silvaco2024
export PATH=$SILVACO/bin:$PATH
for t in deckbuild atlas athena devedit tonyplot tonyplot3d quest sflm; do
  p=$(command -v $t 2>/dev/null)
  printf '%-12s %s\n' "$t" "${p:-MISSING}"
done
EOS
```

期望输出（`tonyplot3d`/`quest` 可缺，不阻塞——但**本机八项全在**）
[已核实: 2026-07-26 上述命令的完整实测输出如下，逐行原样]：

```text
deckbuild    /atctools/Synopsys/Silvaco2024/bin/deckbuild
atlas        /atctools/Synopsys/Silvaco2024/bin/atlas
athena       /atctools/Synopsys/Silvaco2024/bin/athena
devedit      /atctools/Synopsys/Silvaco2024/bin/devedit
tonyplot     /atctools/Synopsys/Silvaco2024/bin/tonyplot
tonyplot3d   /atctools/Synopsys/Silvaco2024/bin/tonyplot3d
quest        /atctools/Synopsys/Silvaco2024/bin/quest
sflm         /atctools/Synopsys/Silvaco2024/bin/sflm
```

> **⚠ 陷阱：不要用 `deckbuild -h` / `atlas -h` 来"顺便确认工具能跑"。**
> 实测 `deckbuild -h` **不返回**：它会拉起 `lib/deckbuild/5.2.40.R/x86_64-linux/deckbuild.exe -h`
> 并一直挂住，2 分钟超时后 SSH 断开，**远端还会留下一个孤儿进程**
> [已核实: 该命令超时后 `pgrep -fa deckbuild` → `50089 .../deckbuild.exe -h`，需手工 `kill`]。
> 存在性判定**只用 `command -v`**（上面的脚本）；要验"真的能跑"，用 §6 的 probe deck。
> 若不慎触发，收尾时执行：`pgrep -f 'deckbuild.exe -h' | xargs -r kill`。

### 3.2 每个工具缺失的含义与降级路径

| 工具 | 作用 | 缺失含义 | 降级候选项 |
|---|---|---|---|
| `deckbuild` | **[默认]** deck 运行器（交互/批处理） | 主运行路径断了 | 直接 `atlas -V <ver> <deck>.in` 跑单段 deck；或 VWF job submit |
| `atlas` | 器件电学求解主引擎 | **硬阻塞** | 无替代（Victory Device 仅 3D 且需单独 license） |
| `devedit` | 任意多边形结构 + 自动重划分 | 复杂结构受限 | **[默认]** 改用 ATLAS 内建 `mesh/x.mesh/y.mesh/region/electrode/doping`（矩形层结构）；或 Athena 工艺仿真出结构 |
| `athena` | 工艺仿真出结构 | 工艺流程路线不可用 | 用 ATLAS 内建网格 + `doping` 解析分布近似 |
| `tonyplot` | **[默认]** 2D 结构 + 曲线可视化 | 图形诊断受限 | TonyPlot3D · Victory Visual · 外部 Python 解析 `.log`（见 §7 降级规则） |
| `sflm` | 许可管理 CLI | license 查询受限 | 用 §6 的最小 probe deck 实测；`pgrep sflm_monitord` |
| `tonyplot3d` | 3D 结构可视化 | 3D 图形诊断受限 | 本机存在 [已核实: `command -v tonyplot3d` → `$SILVACO/bin/tonyplot3d`]；本项目主要是 2D，非阻塞 |
| `quest` | VWF/DOE 前端 | DOE 批量受限 | 本机存在 [已核实: `command -v quest` → `$SILVACO/bin/quest`]；preflight 阶段用不到 |

| 现象 | 处置 |
|---|---|
| `atlas` 或 `deckbuild` 为 `MISSING` | **停止**。这是环境错误，报告用户，不写 deck |
| 只有 `tonyplot` 缺失 | 标记为 degraded：曲线可用 Python 出，结构/空间分布结论**必须**留待用户在 GUI 中确认 |
| 全部存在 | 继续 §4 |

---

## 4. 可用 ATLAS 版本枚举与版本冻结

### 4.1 检查命令

```bash
ssh -i <key> root@<ip> \
  'ls -1 /atctools/Synopsys/Silvaco2024/lib/atlas 2>&1'
```

期望输出 [已核实: 2026-07-26 远端 `ls -1 $SILVACO/lib/atlas` 实测输出]：

```text
5.38.0.R
5.40.0.R
```

> 版本号有两套，别搞混：
> - **ATLAS 求解器版本** = `$SILVACO/lib/atlas/` 下的 `5.40.0.R` → 写进 `simflags="-V 5.40.0.R"`。
> - **DeckBuild 例子库版本** = `$SILVACO/examples/deckbuild/` 下的 `5.2.40.R` → 只是查例子的路径，**不进 deck**。
> - 本 skill 所有 `[已核实: atlas.key:<行号>]` 证据均来自
>   `$SILVACO/lib/atlas/5.40.0.R/common/atlas.key`（即冻结版本自带的关键字表）。
>   [已核实: 该文件存在，本文件后续 §6.1 的逐条 grep 行号即取自它]

### 4.2 版本冻结规则（本项目硬约定）

- **本项目冻结 `-V 5.40.0.R`，并行度 `-P 4`。**
- 每个 deck 的每个 `go atlas` 都显式带 `simflags`，不依赖默认版本：

```silvaco
go atlas simflags="-V 5.40.0.R -P 4"
```

| 现象 | 含义 | 处置 |
|---|---|---|
| 列出 `5.40.0.R` | 冻结版本可用 | 继续 §5 |
| 只有 `5.38.0.R` | 目标版本未装 | 与用户确认后**统一**改成 `-V 5.38.0.R`，并在 `progress.md` 记录版本变更；**不要**混用两个版本跑同一批对比实验 |
| 目录不存在 | 布局不同 | 用 `atlas -V` 或 `deckbuild -h` 探测版本枚举方式；把实际方式记入 `findings.md` |
| deck 里不写 `simflags` | 隐性版本漂移 | 结果不可复现，视为流程缺陷；补上 |

> 跨版本对比曲线在没有说明的情况下不可比。任何版本切换都要在报告里显式写出来。

---

## 5. SFLM 许可证

Silvaco 用 **SFLM**（Silvaco Flexible License Manager），不是 Synopsys 的那套 daemon。

### 5.1 已知事实

- `export SFLM_SERVERS=+localhost`（`+` 前缀表示本机 daemon）。
  **必须自己 export**——安装目录里没有任何 profile 会替你设
  [已核实: `grep -n 'SFLM_SERVERS' $SILVACO/etc/silvaco.profile` → **无输出**；该文件全文见 §2.2]。
- `sflm_monitord` 已在远端运行
  [已核实: `pgrep -fa sflm_monitord` → `2746 /atctools/Synopsys/Silvaco2024/lib/sflm_monitord/7.14.16.R/x86_64-linux/sflm_monitord.exe`]。
- 实际有**两个** license 相关进程在监听，`sflm_monitord` 不是唯一的一个
  [已核实: `ss -lntp | grep -iE 'sflm|3162'`]：
  ```text
  LISTEN 0 128 127.0.0.1:31620  *:*     users:(("sflm_monitord.e",pid=2746,fd=3))
  LISTEN 0 128         *:39441  *:*     users:(("sflm_monitord.e",pid=2746,fd=0))
  LISTEN 0 128      [::]:3162   [::]:*  users:(("rpc.sflmserverd",pid=2399,fd=4))
  ```
  → 真正对外发 license 的是 **`rpc.sflmserverd`（端口 3162）**；只 `pgrep sflm_monitord`
  查不出 `rpc.sflmserverd` 是否活着。两者都要看。

### 5.2 检查命令

```bash
ssh -i <key> root@<ip> 'bash -s' <<'EOS'
export SILVACO=/atctools/Synopsys/Silvaco2024
export PATH=$SILVACO/bin:$PATH
export SFLM_SERVERS=+localhost

echo "--- SFLM_SERVERS ---"; echo "${SFLM_SERVERS:-EMPTY}"
echo "--- monitord ---";     pgrep -fa sflm_monitord   || echo "NOT RUNNING"
echo "--- serverd ---";      pgrep -fa rpc.sflmserverd || echo "NOT RUNNING"
echo "--- listening ---";    (ss -lntp 2>/dev/null || netstat -lntp 2>/dev/null) | grep -iE 'sflm|3162' || echo "no sflm socket matched"
EOS
```

> 上面**故意不含 `sflm -h`**：GUI/交互型 CLI 在非交互 SSH 下有挂住的风险
> （同类现象已在 §3.1 用 `deckbuild -h` 实测到）。要查子命令请**带超时**单独跑：
> `timeout 20 sflm -h 2>&1 | head -20`。[未核实: 本次审计未取得 `sflm -h` 的输出，
> 故本文件不列举任何 `sflm` 子命令名——凭空写子命令正是要避免的事]

期望输出要点 [已核实: 2026-07-26 实测，pid 为当次值]：

```text
--- SFLM_SERVERS ---
+localhost
--- monitord ---
2746 /atctools/Synopsys/Silvaco2024/lib/sflm_monitord/7.14.16.R/x86_64-linux/sflm_monitord.exe
--- listening ---
LISTEN 0 128 127.0.0.1:31620 ... users:(("sflm_monitord.e",pid=2746,fd=3))
LISTEN 0 128      [::]:3162  ... users:(("rpc.sflmserverd",pid=2399,fd=4))
```

### 5.3 license 检查候选项

| 候选 | 命令 | 说明 |
|---|---|---|
| **[默认] 最小 probe deck 实测** | 见 §6 | 唯一能证明"真的能 checkout ATLAS feature"的方法 |
| 进程检查 | `pgrep -fa sflm_monitord; pgrep -fa rpc.sflmserverd` | 快，但 daemon 活着 ≠ feature 可用。**两个都要查**（见 §5.1） |
| `sflm` CLI 查询 | `timeout 20 sflm -h` 后按实际子命令查询 | 子命令名**必须**先从 `sflm -h` 实际输出或手册中读到再用，**不要凭空写**。手册在 `$SILVACO/doc/`（本机有 `2014sflm_users1.pdf`、`2014sflm_quickstart.pdf`）[已核实: `ls -1 $SILVACO/doc` 列出这两个文件] |
| 端口探活 | `ss -lntp \| grep -iE 'sflm\|3162'` | 排查"daemon 在但没监听"。[已核实: 端口 **3162** 由 `rpc.sflmserverd` 监听，原文"需核对"已核实为真] |

| 现象 | 含义 | 处置 |
|---|---|---|
| `SFLM_SERVERS` 为空 | 环境变量没加载 | 在 `ENVPRE` 里显式 `export SFLM_SERVERS=+localhost`（没有 profile 会代劳，见 §5.1） |
| `sflm_monitord` NOT RUNNING | daemon 挂了 | **停止**。报告用户重启 license 服务；不要自行 kill/重启系统服务，除非用户明确授权 |
| `rpc.sflmserverd` NOT RUNNING / 3162 无监听 | 发牌进程挂了（`sflm_monitord` 仍可能是活的，会骗过只查 monitord 的检查） | 同上**停止**并报告；这是"daemon 在但拿不到 license"的典型成因 |
| ATLAS 启动即报 license/feature 相关错误 | 许可不可用或 feature 未授权 | **停止**。不要改 deck、不要改 `models`/`method` 去"绕过" |
| probe deck 正常跑完 | license 可用 | 继续 §7 |

> 只记录"license 可用 / 不可用 / feature 未授权"这一事实，**不要**记录 license 文件内容、序列号、host id。

---

## 6. 最小 license probe deck（可直接跑）

一个硅 p-n 二极管，只做 `solve init`，然后 `quit`。目的是证明：deck 解析通过 + ATLAS 拿到 license + 网格与初值求解正常。**不用来做任何物理结论。**

### 6.1 deck 内容

保存为远端 `/root/DECKBUILD/RUN_preflight_<UTCstamp>/probe_license.in`（`RUN_` 前缀是全 skill 强制约定，见 §10.2 与 `batch-run-and-monitor.md` §4；主控端副本可留在 `D:\SILVACO_LOCAL\` 下，`.in` 属于允许留在主控端的文件类型）：

```silvaco
# probe_license.in — minimal ATLAS license / environment probe
# Si p-n diode, initial solution only. No physics conclusions drawn from this deck.

go atlas simflags="-V 5.40.0.R -P 1"

mesh space.mult=1.0
x.mesh loc=0.0  spac=0.25
x.mesh loc=1.0  spac=0.25
y.mesh loc=0.0  spac=0.02
y.mesh loc=0.3  spac=0.05
y.mesh loc=2.0  spac=0.20

region  num=1 material=silicon

electrode name=anode   top
electrode name=cathode bottom

doping uniform  p.type conc=1e16
doping uniform  n.type conc=1e19 y.min=0.0 y.max=0.2

models  srh
method  newton
solve   init

save    outf=probe_license.str

quit
```

**这个 probe deck 的每一个关键字都已逐条对 `atlas.key` 核过**（`$SILVACO/lib/atlas/5.40.0.R/common/atlas.key`，
即冻结版本自带的关键字表；行号为该文件绝对行号）：

| deck 里写的 | atlas.key 证据 | 说明 |
|---|---|---|
| `mesh space.mult=1.0` | [已核实: `atlas.key:45  space.mult NUM 4 1.0`]（`mesh` 卡 = L41–122） | 默认值就是 `1.0`，写出来只是显式化 |
| `x.mesh loc= spac=` | [已核实: `atlas.key:126  location NUM 2 -999`、`atlas.key:130  spacing NUM 4 -999`]（`x.mesh` 卡 = L123–142） | ⚠ **`loc`/`spac` 在 atlas.key 里没有独立行**，它们是 `location`/`spacing` 的唯一前缀缩写。缩写合法且是官方例子的写法 [已核实: `grep -rh '^ *x\.mesh .*loc=.*spac=' examples/deckbuild/5.2.40.R` → `X.MESH loc=0 spac=0.25` / `X.MESH loc=1 spac=0.25`] |
| `y.mesh ...` | [已核实: `atlas.key:141  y.mesh  6  5`] | `y.mesh` 是独立语句(卡号 6)但**共用 `x.mesh` 的参数表(5)**，所以 `loc`/`spac` 同样适用 |
| `region num=1 material=silicon` | [已核实: `atlas.key:144  number NUM 1 -999`、`atlas.key:325  material CHAR 1`]（`region` 卡 = L143–339） | `num` 是 `number` 的唯一前缀缩写。另有裸逻辑量 `silicon` [已核实: `atlas.key:248  silicon LOG 1 f`]，即 `material=silicon` 与 `region ... silicon` 两种写法都成立 |
| `electrode name= top` / `bottom` | [已核实: `atlas.key:590  name CHAR 2`、`atlas.key:580  top LOG 3 f`、`atlas.key:581  bottom LOG 4 f`]（`electrode` 卡 = L535–595） | 官方例子同写法 [已核实: `grep -rh '^ *electrode +name=' examples/...` → `ELECTRODE name=anode top` / `ELECTRODE name=substrate bottom`] |
| `doping uniform p.type conc=` | [已核实: `atlas.key:342  uniform LOG 2 f`、`atlas.key:343  p.type LOG 3 f`、`atlas.key:346  n.type LOG 4 f`、`atlas.key:424  concentr NUM 1 -999`]（`doping` 卡 = L340–534） | ⚠ **`conc` 在 atlas.key 里没有独立行**，规范名是 `concentr`，`conc` 是唯一前缀缩写。官方例子用缩写 [已核实: `grep -rh '^ *doping +uniform.*conc=' examples/...` → `DOPING uniform p.type conc=2e20 y.max=1.0` / `DOPING uniform n.type conc=2e20 y.min=1.0`] |
| `y.min= y.max=`（在 doping 上） | [已核实: `atlas.key:435  y.max NUM 5 -999`、`atlas.key:445  y.min NUM 10 -999`] | 同一名字在多张卡上都存在，含义随卡而变，别跨卡套用 |
| `models srh` | [已核实: `atlas.key:963  srh LOG 1 f`]（`models` 卡 = L962–1947） | 默认 `f`，必须显式打开 |
| `method newton` | [已核实: `atlas.key:831  newton LOG 31 t`]（`method` 卡 = L643–961） | **默认已是 `t`**，写出来只是显式化，不是"启用" |
| `solve init` | [已核实: `atlas.key:3074  initial LOG 1 f`]（`solve` 卡 = L3073–4459） | ⚠ 规范名是 `initial`，`init` 是唯一前缀缩写 |
| `save outf=` | [已核实: `atlas.key:7117  outfile CHAR 1`]（`save` 卡 = L7116–7336） | ⚠ 规范名是 `outfile`，`outf` 是唯一前缀缩写 |
| `go atlas simflags="..."` | [已核实: 官方例子同写法 `grep -rh '^ *go +atlas +simflags' examples/...` → `GO atlas simflags="-P 4"` / `GO atlas simflags="-P 2"`] | `go`/`simflags` 属 DeckBuild 层，不在 atlas.key 的参数表里（`atlas.key:31  go  2`，pass-through 语句） |

> **关于缩写**：上表标 ⚠ 的五个（`loc` `spac` `conc` `init` `outf`）在 `atlas.key` 里**查不到独立行**，
> 它们靠 ATLAS 的唯一前缀匹配生效。本 deck 保留缩写写法是因为**官方例子就是这么写的**（证据见上），
> 但**读别人的 deck 或 grep 核对参数时，一定要按规范全名去查**，否则会误判成"这个参数不存在"。
>
> 若本机版本对某个参数名报 unknown parameter，去
> **`$SILVACO/examples/deckbuild/5.2.40.R/`**（注意不是 `$SILVACO/examples/` 直接子目录，见 §2.3）
> 里找同类最小 deck 核对后再改，**不要凭猜测换参数名**。

### 6.2 运行候选项

| 候选 | 命令 | 说明 |
|---|---|---|
| **[默认] DeckBuild 批处理** | `deckbuild -run -ascii probe_license.in -outfile probe_license.out` | 与生产 runner 完全一致的路径，preflight 就应该测生产路径。[已核实: 本机确有该形式在跑，`pgrep -fa deckbuild` → `timeout 600 deckbuild -run -ascii r1.in`] |
| 等价写法（参数顺序可换） | `deckbuild -ascii -run <deck>.in > <deck>.out 2>&1` | [已核实: `pgrep -fa deckbuild` → `sh -c deckbuild -ascii -run n11.in > n11.out 2>&1`]；两种写法都会拉起 `lib/deckbuild/5.2.40.R/x86_64-linux/dbascii.exe -run <deck>.in` |
| ATLAS 直跑 | `atlas -V 5.40.0.R probe_license.in` | 绕过 DeckBuild，用来区分"DeckBuild 问题"还是"ATLAS 问题" |
| 后台守护 | `nohup deckbuild -run -ascii ... > probe.nohup 2>&1 &` | probe 很快，通常不需要 |
| VWF job submit | VWF 提交 | preflight 阶段不用，等 DOE 阶段再验 |

> **一律加 `timeout`。** SSH 会话被打断时远端进程不一定跟着死（§3.1 的 `deckbuild.exe -h` 就留下了孤儿进程），
> 生产 runner 的实际写法是 `timeout 600 deckbuild -run -ascii <deck>.in`
> [已核实: 本机运行中的进程即为此形式]。

### 6.3 完整 probe 执行块

```bash
ssh -i <key> root@<ip> 'bash -s' <<'EOS'
export SILVACO=/atctools/Synopsys/Silvaco2024
export PATH=$SILVACO/bin:$PATH
export SFLM_SERVERS=+localhost
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

RUN="/root/DECKBUILD/RUN_preflight_$(date -u +%Y%m%dT%H%M%SZ)"   # RUN_ 前缀强制，见 §10.2
mkdir -p "$RUN" && cd "$RUN" || exit 90
cat > probe_license.in <<'DECK'
go atlas simflags="-V 5.40.0.R -P 1"
mesh space.mult=1.0
x.mesh loc=0.0  spac=0.25
x.mesh loc=1.0  spac=0.25
y.mesh loc=0.0  spac=0.02
y.mesh loc=0.3  spac=0.05
y.mesh loc=2.0  spac=0.20
region  num=1 material=silicon
electrode name=anode   top
electrode name=cathode bottom
doping uniform  p.type conc=1e16
doping uniform  n.type conc=1e19 y.min=0.0 y.max=0.2
models  srh
method  newton
solve   init
save    outf=probe_license.str
quit
DECK

deckbuild -run -ascii probe_license.in -outfile probe_license.out
rc=$?
echo "=== deckbuild exit code: $rc ==="
ls -l probe_license.str 2>&1
echo "=== tail of out ==="
tail -30 probe_license.out
EOS
```

### 6.4 判定：ATLAS 终止串候选项

ATLAS 没有 Sentaurus 那种唯一的 "Good Bye" 终止串。**必须按候选项集合判定**：

| 类别 | 判据候选 | 含义 |
|---|---|---|
| **[默认] 正常结束** | `deckbuild` 进程退出码 `0` **且** 目标 `.str`/`.log` 已生成 | 成功。这是最可靠的一条 |
| 正常结束（deck 侧） | deck 最后的 `quit` 被执行 | 配合退出码使用 |
| 崩溃 | 输出中出现 `ATLAS DIED` | 进程异常终止，通常是内存/网格/语法致命错误 |
| 不收敛 | `Convergence failure` / `solution did not converge` 类字样 | 数值问题，**只有在 preflight 全绿之后**才按物理/数值问题处理 |
| 主动中止 | `fail.quit` 被触发 | deck 里自设的失败退出 |
| **环境阻塞** | 输出中出现 `License` / `SFLM` 相关错误 | **环境错误**，回到 §5，不要改 deck |

> 不要用 `grep -i error` 做终止判定——正常收敛过程中的诊断信息也会命中。
> 优先用 **退出码 + 产物文件是否生成** 两个客观信号。

| probe 结果 | 处置 |
|---|---|
| exit 0 + `probe_license.str` 存在 | license 与运行链路全通，继续 §7 |
| exit != 0 且 out 里有 license 字样 | 停止，回 §5 |
| exit != 0 且报 unknown parameter / syntax | deck 语法与本机版本不符：先按**规范全名**去 `atlas.key` 里 grep（缩写查不到不等于不存在，见 §6.1），再去 `$SILVACO/examples/deckbuild/5.2.40.R/` 核对该语句 |
| 一直挂住不返回 | 可能在等 license 或等 X 连接：检查 §5 与 §7；**下次一律用 `timeout <秒> deckbuild ...`**，并在超时后 `pgrep -fa 'dbascii.exe\|deckbuild.exe'` 清理孤儿进程（§3.1） |

---

## 7. DISPLAY、X socket 与可视化

### 7.1 已知事实

- 远端 X 显示 `:0` 存在（root 已登录 tty1）
  [已核实: `ls -l /tmp/.X11-unix/` → `srwxrwxrwx 1 root root 0 7月 26 19:21 X0`；
  `who` → `root tty1  2026-07-26 19:21 (:0)`]。
- **所有 GUI 工具（`tonyplot`、`deckbuild` 交互模式、`devedit` GUI）之前必须 `export DISPLAY=:0`。**

### 7.2 检查命令

```bash
ssh -i <key> root@<ip> 'bash -s' <<'EOS'
export SILVACO=/atctools/Synopsys/Silvaco2024
export PATH=$SILVACO/bin:$PATH
export DISPLAY=:0
echo "DISPLAY=$DISPLAY"
ls -l /tmp/.X11-unix/ 2>&1
who 2>/dev/null | head -5
(xdpyinfo 2>/dev/null | head -3) || (xset q 2>&1 | head -3) || echo "no X query tool"
EOS
```

期望输出要点（前三行 [已核实: 2026-07-26 实测]；`xdpyinfo` 那行 [未核实: 本次未取得该工具输出，见下表末行]）：

```text
DISPLAY=:0
srwxrwxrwx 1 root root 0 7月  26 19:21 X0
root     tty1         2026-07-26 19:21 (:0)
name of display:    :0
```

| 现象 | 含义 | 处置 |
|---|---|---|
| `/tmp/.X11-unix/X0` 存在且 `xdpyinfo`/`xset q` 成功 | GUI 可用 | TonyPlot 可直接开图 |
| socket 存在但 `Can't open display` | 权限/cookie 问题 | 用户在 tty1 上 `xhost +local:` 或以同一用户运行；**不要**自动放开 X 权限 |
| socket 不存在 | 无 X server | **降级**，见 §7.3 |
| `xdpyinfo`/`xset` 都没装 | 只是工具缺失，不代表 X 不可用 | 直接试 `tonyplot -h` 或实际开一次图判定 |

### 7.3 可视化候选项与降级规则

| 候选 | 命令 | 适用 |
|---|---|---|
| **[默认] TonyPlot** | `export DISPLAY=:0; tonyplot <file>.str &` / `tonyplot <file>.log &` | 2D 结构 + I-V/瞬态曲线，日常主力 |
| TonyPlot3D | `tonyplot3d <file>.str &` | 3D 结构 |
| Victory Visual | 较新的可视化前端，出版级导出 | 需要高质量导出图时 |
| 外部 Python 解析 `.log` | 把 `.log` 回传主控端，Python 出图存 `.png` | **无头环境唯一可用**；只能做曲线 |

> **降级不是完整替代。** 无 DISPLAY 时：
> - `.log` 曲线结论（I-V、BV、瞬态）可以照常给出；
> - `.str` 的空间分布结论（电流路径、峰值电场位置、载流子/温度分布、击穿点）
>   **必须标记为"待在 GUI 中查看后确认"**，不得直接下最终物理判断。

---

## 8. 并行度 `-P N` 与 nproc

### 8.1 检查命令

```bash
ssh -i <key> root@<ip> \
  'nproc; free -g | awk "/^Mem:/{print \"MemTotalGB=\"\$2\" MemFreeGB=\"\$4}"; uptime'
```

期望输出 [已核实: `nproc` → `8`；`free -g | head -2` → `Mem: 7(total) 1(used) 0(free) 0(shared) 5(buff/cache) 5(available)`]：

```text
8
MemTotalGB=7 MemFreeGB=...
 ... load average: 0.0x, 0.0x, 0.0x
```

> ⚠ 看 `free` 要看 **available**（本机 5 GB）而不是 **free**（本机 0 GB）——
> RHEL 7 会把内存全用作 buff/cache，`free` 列常年接近 0，据此判"内存不够"会误停。
> 下面 §8.2 判据表里的"`free` 剩余"一律指 **available 列**。

### 8.2 并行度规则

- 本机 **8 vCPU / 8 GB RAM**。本项目冻结 **`-P 4`**。
- `-P N` 写在 `simflags` 里：`go atlas simflags="-V 5.40.0.R -P 4"`。
- **内存是比核数更硬的约束**：8 GB 总内存下，一个大网格 2D 瞬态就可能吃掉几 GB。

| 场景 | 建议 `-P` | 同时可跑的 ATLAS 作业数 |
|---|---|---|
| 单作业、精调 | 4 | 1 |
| 2 个并行作业（如两个偏压点） | 2 | 2 |
| license probe / 语法体检 | 1 | 任意 |
| 大网格 3D / 自热瞬态 | 4，且**独占** | 1 |

提交前必须查当前占用：

```bash
ps -eo pid,pcpu,pmem,rss,etime,comm,args | grep -E 'atlas|deckbuild' | grep -v grep
```

| 现象 | 含义 | 处置 |
|---|---|---|
| 无 atlas 进程 | 空闲 | 可按 `-P 4` 提交 |
| 已有 1 个 atlas 占 4 核 | 半负载 | 新作业降到 `-P 2`，或排队等待 |
| load average > nproc | 超载 | **不要**再提交；超订会让所有作业一起变慢甚至 OOM |
| `free -g` **available** 列 < 1.5 GB | 内存吃紧 | 停止提交，等待或缩小网格（不要看 free 列，见 §8.1 注） |
| 已有他人的 `dbascii.exe` 在跑 | 机器是共享的 | 先 `pgrep -fa 'dbascii.exe\|deckbuild'` 看清有几个作业，再决定 `-P`。[已核实: 2026-07-26 本机同时有 `n11.in` / `n12.in` / `r1.in` 三个 deck 在跑] |

> `-P N > nproc` 不会更快，只会引发 CPU 争抢；`-P` 也**不能**修复收敛问题。

---

## 9. 磁盘余量与 `/mnt/hgfs` 满盘陷阱

### 9.1 检查命令

```bash
ssh -i <key> root@<ip> 'df -h / /root /tmp /mnt/hgfs/* 2>&1'
```

期望输出要点 [已核实: 2026-07-26 实测，下面是真实数字]：

```text
文件系统               容量  已用  可用 已用% 挂载点
/dev/mapper/rhel-root  191G   68G  124G   36% /        <- 主运行区，充足
vmhgfs-fuse            312G  305G  7.2G   98% /mnt/hgfs/16sil_share
vmhgfs-fuse            310G  251G   59G   82% /mnt/hgfs/share24
vmhgfs-fuse            317G  241G   76G   76% /mnt/hgfs/share_wm
```

> ⚠ `df` 对 HGFS 会把三个共享的挂载点**都显示成 `/mnt/hgfs`**，看不出是哪个。
> 要分辨就按 `ls -1 /mnt/hgfs/` 的顺序（`16sil_share` / `share24` / `share_wm`）对应
> `df -h /mnt/hgfs/*` 的输出行——`df` 按参数顺序输出，glob 是字典序。
> [已核实: `ls -1 /mnt/hgfs/` → `16sil_share` / `share24` / `share_wm`]

### 9.2 陷阱与规则

- `/mnt/hgfs/{16sil_share,share24,share_wm}` 是 VMware HGFS 共享目录。
  ⚠ **原文"三个都已 98% 满"不准确**，实测只有一个到 98%
  [已核实: `df -h /mnt/hgfs/*` → `16sil_share 98%(7.2G avail)` / `share24 82%(59G avail)` / `share_wm 76%(76G avail)`]。
  但**结论不变**：三个都不许当输出目录（理由见下条 HGFS 语义问题），
  且余量会随宿主机 Windows 侧的使用随时变化，**每次 preflight 都要重测，不要引用本文档里的百分比**。
- **不要**把 `.str` / `.log` / 中间产物写进 `/mnt/hgfs/*`。
  写满会让 ATLAS 在 `save outf=` 时静默失败或直接 `ATLAS DIED`，
  看起来像"跑到一半崩了"，实际是 **No space left on device**。
- HGFS 还有 POSIX 语义差异（权限、锁），不适合作为运行工作目录。

| 现象 | 含义 | 处置 |
|---|---|---|
| `/` avail > 20 GB | 足够 | 继续。[已核实: 2026-07-26 为 124G avail / 36% used] |
| `/` avail < 10 GB | 危险 | 先清理旧 run 目录或回传归档后删除，再开新作业 |
| 任一 `/mnt/hgfs/*` 接近满 | 已满 | 只读使用；**绝不**作为输出目录（不论余量多少都不作输出目录） |
| ATLAS 中途死且 `.str` 为 0 字节 | 极可能是磁盘满 | 先 `df -h`，再考虑物理问题 |

### 9.3 产物落盘纪律（用户明确规则）

- **主控端 `D:\SILVACO_LOCAL` 只放**：`.py` 脚本 / `.md` 技术文档 / 轻量 `.csv` / `.png` 截图与图 / `.in` deck。
- **一切大体积 `.str` / `.log` 归档到 Windows `E:\silvaco2425\bulk\{str,log}\`**。
- 远端运行期间产物留在 `/root/DECKBUILD/<run>/`，**结束后回传归档**。
- 远端 `/root/DECKBUILD` 是唯一正在迭代的运行区；**不要**把整套远端工程复制回 Windows。

preflight 阶段就要确认归档盘存在：

```powershell
Test-Path E:\silvaco2425\bulk\str; Test-Path E:\silvaco2425\bulk\log
```

不存在则先创建，或与用户确认改用哪个归档路径——**不要**默默把大文件堆在 `D:\SILVACO_LOCAL`。

---

## 10. 项目根目录可写

### 10.1 检查命令

```bash
ssh -i <key> root@<ip> 'bash -s' <<'EOS'
ROOTDIR=/root/DECKBUILD
test -d "$ROOTDIR" || { echo "MISSING $ROOTDIR"; exit 10; }
test -w "$ROOTDIR" || { echo "NOT WRITABLE $ROOTDIR"; exit 11; }
RUN="$ROOTDIR/RUN_preflight_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN" && touch "$RUN/.wtest" && echo "WRITE OK: $RUN" && rm -rf "$RUN"
df -h "$ROOTDIR" | tail -1
EOS
```

期望输出 [已核实: `ls -d /root/DECKBUILD` → 存在；`test -w /root/DECKBUILD` → `WRITABLE`；
`df -h /` → `/dev/mapper/rhel-root 191G 68G 124G 36% /`]：

```text
WRITE OK: /root/DECKBUILD/RUN_preflight_20260726T...Z
/dev/mapper/rhel-root  191G   68G  124G   36%  /
```

### 10.2 run 目录命名约定

Silvaco 没有 SWB 的 `n<N>` 节点号。**用 run 目录名 / case tag 代替节点号**：

```text
/root/DECKBUILD/RUN_<case>_<UTCstamp>/
    <case>.in
    <case>.out          # deckbuild -outfile
    <case>_struct.str
    <case>_idvd.log
```

> `RUN_` 前缀是**全 skill 统一约定**（`batch-run-and-monitor.md` 亦同）。
> ⚠ 实际检查发现远端已有的目录**大多没遵守**这个约定
> [已核实: `ls -1 /root/DECKBUILD` → `Datta2024_fit_20260725` / `FP_BV_755_AB` / `FP_SEB_final` /
> `Liu2025_experiment_fit_20260725` / `SOLVER_EXP_20260726` / `Wang2026_SEB_fit_20260726` / `_smoke_probe` …]。
> 历史目录不强制改名（改名会打断已有的回传/归档脚本），但**新建目录一律用 `RUN_<case>_<UTCstamp>`**。

| 现象 | 含义 | 处置 |
|---|---|---|
| `WRITE OK` | 可写 | 继续 §11 |
| `MISSING /root/DECKBUILD` | 项目根不存在 | 与用户确认后 `mkdir -p`；不要换到 `/tmp` 或家目录下随手建 |
| `NOT WRITABLE` | 权限问题 | 停止，让用户修权限；不要 `chmod -R 777` |
| 目录存在但已有大量旧 run | 磁盘风险 | 先按 §9.3 回传归档再清理 |

> 不要在临时目录、下载目录或 skill 仓库里创建 Silvaco 工程。

---

## 11. locale（RHEL 7 UTF-8）

### 11.1 检查命令

```bash
ssh -i <key> root@<ip> 'locale; echo "---"; locale -a | grep -iE "en_US.utf-?8|C.utf-?8" | head -5'
```

**本机实际输出**（不是期望值，注意二者不一致）
[已核实: 2026-07-26 `locale` → `LANG=zh_CN.UTF-8` / `LC_CTYPE="zh_CN.UTF-8"` / `LC_NUMERIC="zh_CN.UTF-8"`；
`locale -a | grep -i en_US.utf` → `en_US.utf8`]：

```text
LANG=zh_CN.UTF-8            <- 本机默认是中文 locale，不是 en_US
LC_CTYPE="zh_CN.UTF-8"
LC_NUMERIC="zh_CN.UTF-8"    <- 直接命中 §11.2 的"中文 locale + 数字格式"风险行
...
en_US.utf8                  <- en_US.UTF-8 已生成，可以切
```

> ⚠ **原文把 `LANG=en_US.UTF-8` 写成"期望输出"，本机实测是 `zh_CN.UTF-8`。**
> 这不是"环境坏了"，而是说明 `ENVPRE` 里那两行 `export LANG=... LC_ALL=...`
> **不是可选项而是必须项**——不写就会落到 `zh_CN.UTF-8`，`.log` 里的数值格式与
> ATLAS/DeckBuild 的英文报错串都可能受 locale 影响。
> 好消息是 `en_US.utf8` 本机已生成，`export` 一定成功，不必退回 `LC_ALL=C`。

### 11.2 规则与失败处置

| 现象 | 含义 | 处置 |
|---|---|---|
| `LANG=en_US.UTF-8` | 正常（已被 `ENVPRE` 覆盖成功） | 继续 |
| **`LANG=zh_CN.UTF-8`** | **本机默认状态**，说明 `ENVPRE` 没生效 | 补上 `export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8`；`en_US.utf8` 本机已生成，一定能切 [已核实] |
| `LANG=POSIX` 或空 | 非交互 SSH 常见 | 同上，在 `ENVPRE` 里显式 export |
| `locale: Cannot set LC_ALL to ...` | 该 locale 未生成 | 退回 `export LC_ALL=C`（ASCII 安全），并在 deck 与文件名中**只用 ASCII**。[本机用不到: `locale -a` 已列出 `en_US.utf8`] |
| 中文 locale + 数字格式 | 小数点/千分位可能被 locale 影响 | 强制 `LC_NUMERIC=C`，保证 `.log` 里数值是 `1.234e-05` 而不是 `1,234e-05`。⚠ 本机 `LC_NUMERIC="zh_CN.UTF-8"` 是默认值，这一行**是现实风险不是假设** |
| 远端 `ls`/`df` 输出出现中文表头 | locale 未覆盖（如 `文件系统 容量 已用 可用`） | 脚本里靠列位置/`--output=` 解析，**不要 grep 中文表头**；或先 export 再跑 |

**硬规则**：远端所有路径、deck 文件名、region/electrode 名一律 **ASCII**。
中文只出现在主控端 `.md` 文档里，不进 `.in` deck、不进远端目录名——RHEL 7 上非 UTF-8 环境会把中文路径变成乱码，
表现为 "file not found"，很容易被误判成 deck 写错。

---

## 12. 环境错误 vs deck 错误 速查表

| 症状 | 类型 | 下一步 |
|---|---|---|
| `ssh: connect ... timed out` | 环境（网络/IP） | 按 §1.2 重新探测 IP。别信任何**记下来的**地址（含本文档里的），`ens33` 是 DHCP |
| `kex_exchange_identification: ... Connection reset by peer` | 环境（该 IP 上不是我们的机器） | 同上重探，并**必须核对 `hostname` == `tcad`** 才继续（§1.1） |
| `deckbuild: command not found` / `atlas: command not found` | 环境（PATH） | 加 `ENVPRE`（§2.3） |
| 输出含 `License` / `SFLM` 报错 | 环境（许可） | 回 §5；**禁止**改 deck |
| `Can't open display` | 环境（X） | `export DISPLAY=:0`；或走 §7.3 降级 |
| `Permission denied` 写 `/root/DECKBUILD` | 环境（权限） | 回 §10 |
| `No space left on device`，`.str` 0 字节 | 环境（磁盘） | 回 §9，检查是否误写 `/mnt/hgfs` |
| `unknown parameter` / syntax 报错 | deck 语法 | 先用**规范全名**在 `$SILVACO/lib/atlas/5.40.0.R/common/atlas.key` 里 grep（缩写查不到≠不存在，见 §6.1），再去 `$SILVACO/examples/deckbuild/5.2.40.R/` 核对，不要猜参数名 |
| 命令挂住不返回（`-h`、GUI 型 CLI） | 环境（交互程序在非交互 SSH 下阻塞） | 一律加 `timeout`；事后 `pgrep -fa 'deckbuild.exe\|dbascii.exe'` 清孤儿进程（§3.1） |
| `ATLAS DIED` 且内存曲线飙升 | 环境（内存）或网格过大 | 先看 `free`（看 **available** 列）/`dmesg` 是否 OOM，再考虑减网格 |
| `Convergence failure` / `solution did not converge`，且 `.log`/`.str` 可读 | 数值/模型 | **preflight 全绿后**才进入正常闭环诊断（`method block newton carriers=2`、渐进 `solve`、网格细化） |
| 曲线形状异常但求解正常收敛 | 物理/参数 | 对照 `.str` 空间分布与 `models`/`material` 设置 |

**顺序不能反**：先排除环境，再谈物理。

---

## 13. Preflight 一键脚本

下面这段可直接作为 heredoc 通过 SSH 执行；也可把它固化成主控端脚本（例如 `D:\SILVACO_LOCAL\preflight_silvaco.py` 的 shell 载荷）。
⚠ 该脚本**目前尚未创建** [已核实: 2026-07-26 `D:\SILVACO_LOCAL\` 下无 `preflight_silvaco.py`]——要固化就先创建它，不要假定成品已存在。
每项独立打印 PASS/FAIL，最后给汇总。

```bash
ssh -i C:/Users/Administrator/.ssh/silvaco_ed25519 root@<PROBED_IP> 'bash -s' <<'EOS'
set -u
FAIL=0
chk(){ if eval "$2" >/dev/null 2>&1; then printf 'PASS  %s\n' "$1"; else printf 'FAIL  %s\n' "$1"; FAIL=$((FAIL+1)); fi; }

export SILVACO=/atctools/Synopsys/Silvaco2024
# 不要 source $SILVACO/etc/silvaco.profile：实测它是只 echo 说明文字的 csh 脚本，
# 不设 SILVACO / PATH / 任何 license 变量（全文 315 字节，见 §2.2）。显式 export 才是唯一正确路径。
export PATH="$SILVACO/bin:$PATH"
export SFLM_SERVERS=+localhost
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8   # 本机默认为 zh_CN.UTF-8，必须覆盖，见 §11
export DISPLAY=:0

echo "host=$(hostname)  kernel=$(uname -r)  nproc=$(nproc)"
chk "hostname is tcad"       'test "$(hostname)" = tcad'
chk "silvaco bin dir"        'test -d "$SILVACO/bin"'
chk "examples 5.2.40.R"      'test -d "$SILVACO/examples/deckbuild/5.2.40.R"'
chk "atlas.key readable"     'test -r "$SILVACO/lib/atlas/5.40.0.R/common/atlas.key"'
chk "deckbuild present"      'command -v deckbuild'
chk "atlas present"          'command -v atlas'
chk "devedit present"        'command -v devedit'
chk "tonyplot present"       'command -v tonyplot'
chk "atlas 5.40.0.R avail"   'test -e "$SILVACO/lib/atlas/5.40.0.R"'
chk "SFLM_SERVERS set"       'test -n "$SFLM_SERVERS"'
chk "sflm_monitord running"  'pgrep -f sflm_monitord'
chk "rpc.sflmserverd running" 'pgrep -f rpc.sflmserverd'
chk "sflm port 3162 listen"  '(ss -lntp 2>/dev/null || netstat -lntp 2>/dev/null) | grep -q ":3162"'
chk "X socket :0"            'test -S /tmp/.X11-unix/X0'
chk "project root writable"  'test -d /root/DECKBUILD && test -w /root/DECKBUILD'
chk "root fs >20G free"      'test "$(df -BG --output=avail / | tail -1 | tr -dc 0-9)" -gt 20'
chk "utf8 locale avail"      'locale -a | grep -qiE "en_US.utf-?8"'

echo "--- running atlas/deckbuild jobs (machine is shared, check before -P) ---"
pgrep -fa 'dbascii.exe|deckbuild|atlas' | grep -v pgrep || echo "none"

echo "--- hgfs fill level (informational, do NOT write here) ---"
for d in /mnt/hgfs/*; do printf '%-28s %s\n' "$d" "$(df -h --output=pcent,avail "$d" 2>/dev/null | tail -1)"; done

echo "=== preflight failures: $FAIL ==="
exit $FAIL
EOS
```

退出码 `0` = 全绿。非 0 = 有阻塞项，**停止**并按对应章节处置。
一键脚本**不含** license probe（它需要真跑 ATLAS），probe 单独按 §6 执行。

> 相对原版的四处修正（均由 2026-07-26 实测驱动）：
> 1. 删掉 `. $SILVACO/etc/silvaco.profile` —— 该文件什么都不设（§2.2）。
> 2. `examples dir` 改查 `examples/deckbuild/5.2.40.R` —— `$SILVACO/examples/` 存在但里面没有 deck（§2.3）。
> 3. 增补 `rpc.sflmserverd` + 3162 端口检查 —— 只查 `sflm_monitord` 会漏掉真正的发牌进程（§5.1）。
> 4. 增补 `hostname == tcad` 与"在跑的作业"两项 —— 对应 §1.1 的 IP 漂移与 §8 的共享机器问题。
> 逐个 `/mnt/hgfs/*` 单独打印，是因为 `df` 会把三个共享的挂载点都显示成 `/mnt/hgfs`（§9.1）。

---

## 14. Preflight 结果记录模板

把结果写进 `progress.md`（或本轮 run 目录下的记录文件）：

```markdown
## Silvaco preflight — <UTC timestamp>

| 项 | 状态 | 证据/输出 | 处理 |
|---|---|---|---|
| SSH 可达 + 实际 IP | pass/fail | ip=<probed>，**且 hostname 实测=tcad** | IP 会随 DHCP 漂移，必须本轮实测 |
| Silvaco 环境加载方式 | pass/fail | 显式 `export PATH`（**不 source profile**） | profile 是空壳，见 §2.2 |
| examples 例子库路径 | pass/fail | `examples/deckbuild/5.2.40.R` 存在? | 缺失则不得声称"已对照官方例子" |
| deckbuild / atlas | pass/fail | `command -v` 输出（**不要用 `-h` 探活**） | ... |
| devedit / tonyplot | pass/degraded/fail | `command -v` 输出 | 缺失则记降级路径 |
| ATLAS 版本枚举 | pass/fail | ls $SILVACO/lib/atlas | 冻结 -V 5.40.0.R |
| SFLM (SFLM_SERVERS + monitord + **serverd/3162**) | pass/fail | +localhost, 两个 pid 都在, 3162 监听 | 只查 monitord 会漏判 |
| license probe deck | pass/fail | exit code, probe_license.str 存在? | 建议 `timeout` 包裹 |
| DISPLAY=:0 / X socket | pass/degraded/fail | /tmp/.X11-unix/X0 | 降级则 .str 空间结论待确认 |
| 并行度策略 | pass | nproc=8, 本轮 -P 4 | **本轮实测在跑的 dbascii/atlas 作业数 = ?**（机器共享） |
| 磁盘余量 / hgfs | pass/fail | / avail=<实测>, 三个 hgfs 各自百分比 | 输出目录 = /root/DECKBUILD/RUN_<case>_<stamp> |
| 项目根可写 | pass/fail | WRITE OK 路径 | ... |
| locale | pass/degraded | LANG 实测值（本机默认 zh_CN.UTF-8） | 未覆盖成 en_US.UTF-8 即为 degraded |
| 归档盘 E:\silvaco2425\bulk | pass/fail | Test-Path 结果 | ... |

Decision: proceed / blocked / degraded proceed
Blocking items: <列出>
```

> 记录时**只写实测到的值**。任何一项拿不到输出就写 `未核实`，不要照抄本文档里的数字——
> 本文档 §1/§9/§11 的数字都是 2026-07-26 的快照，IP、磁盘余量、locale 都会变。

---

## 15. 放行条件

只有满足下面之一，才允许进入建模、写 `.in` deck、`deckbuild -run` 提交：

1. `Decision: proceed`（全部 pass）；或
2. `Decision: degraded proceed`，且**用户明确接受**降级项及其后果
   （例如：无 DISPLAY → 本轮不给空间分布最终结论）。

**`Decision: blocked` 时不写 deck、不提交仿真、不调物理模型。**
直接向用户报告阻塞项、对应章节、以及需要用户做的动作。
