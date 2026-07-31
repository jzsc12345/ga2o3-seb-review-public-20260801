# -*- coding: utf-8 -*-
"""RUN 迭代收纳箱脚手架(账本 A14;规范 docs\\RUN工程架构规范_20260727.md)。

用法:
  python scripts\\new_run.py new --tag lhd-r1 --deck decks\\sweep_bv_main.in [--goal ...] [--var ...] [--id N]
  python scripts\\new_run.py list
"""
import argparse
import datetime
import hashlib
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "outputs", "runs")
SUBDIRS = ("csv", "figs", "shots", "logs")

TEMPLATE = """# {name} — {goal}

- 日期:{date} | git:{git} | deck:`{deck}` (sha256:{sha})
- 远端:`/root/DECKBUILD/runs/{name}/` | tmux:`<发射前必填>` | 看板:`outputs\\<session>\\screenshots\\`

## 1. 目标与判据(发射前填)

{goal}
判据:<引判据条目,如 [工作判据 v0.1] / W1 功能判据 ≤1e-9>

## 2. 与上一 RUN 的差异(发射前填)

单变量:{var}
deck diff 全部行:
```
<逐行贴>
```
⚠ 物理模型改动(lat.temp/impact/trap/incomplete/材料参数):<无 | 有→列出并注明用户是否已点头(账本 A13)>

## 3. 发射前预检包(发射前填,缺一不许发射)

- 结构图:`figs\\<...png>` | 网格图:`figs\\<...png>`
- 发给用户时间:<HH:MM> | tmux 会话:<名>

## 4. 结果索引(到站后填)

- csv\\:<每文件一行说明>
- figs\\ 四图套餐:网格 / |E| / Lattice Temperature / total current density + 曲线
- 大文件:`E:\\silvaco2425\\bulk\\...\\{name}\\` | 远端后处理:`postproc/*/RUN{num}/`

## 5. 判据结论(到站后填)

<一句话结论 + 判据条目 + typescript 双门证据行(exit 0 或 finished+零 ERROR #)>
"""

INDEX_HEADER = (
    "# outputs\\runs — RUN 迭代总索引(账本 A14)\n\n"
    "> 每次仿真迭代一行;详情进各 RUN 的 README.md。规范:`docs\\RUN工程架构规范_20260727.md`。\n\n"
    "| RUN | 日期 | 目标 | 单变量 | 状态 |\n|---|---|---|---|---|\n"
)


def _git_hash():
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or "N/A"
    except Exception:
        return "N/A"


def _next_id():
    if not os.path.isdir(RUNS):
        return 1
    ids = []
    for d in os.listdir(RUNS):
        m = re.match(r"RUN(\d{3})_", d)
        if m:
            ids.append(int(m.group(1)))
    return (max(ids) + 1) if ids else 1


def cmd_new(a):
    tag = re.sub(r"[^0-9a-z\-]", "-", a.tag.lower())
    num = a.id if a.id is not None else _next_id()
    name = "RUN%03d_%s" % (num, tag)
    box = os.path.join(RUNS, name)
    if os.path.exists(box):
        sys.exit("已存在: %s" % box)
    deck_abs = os.path.join(ROOT, a.deck) if not os.path.isabs(a.deck) else a.deck
    if not os.path.isfile(deck_abs):
        sys.exit("deck 不存在: %s (先把本轮 deck 落 decks\\ 再建箱)" % a.deck)
    sha = hashlib.sha256(open(deck_abs, "rb").read()).hexdigest()[:16]

    for s in SUBDIRS:
        os.makedirs(os.path.join(box, s))
    body = TEMPLATE.format(name=name, goal=a.goal, var=a.var, deck=a.deck, sha=sha,
                           num="%03d" % num, git=_git_hash(),
                           date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    with open(os.path.join(box, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(body)

    idx = os.path.join(RUNS, "README.md")
    if not os.path.isfile(idx):
        with open(idx, "w", encoding="utf-8", newline="\n") as f:
            f.write(INDEX_HEADER)
    with open(idx, "a", encoding="utf-8", newline="\n") as f:
        f.write("| [%s](%s/README.md) | %s | %s | %s | 准备中 |\n" % (
            name, name, datetime.date.today().isoformat(), a.goal, a.var))

    print("[new_run] %s" % box)
    print("[new_run] 远端目录建议: mkdir -p /root/DECKBUILD/runs/%s" % name)
    print("[new_run] 发射前预检包四件(缺一不许发射, A14):")
    print("          ①结构图+②网格图入 figs\\  ③deck diff 填 README §2(物理改动须用户点头,A13)")
    print("          ④tmux 会话名填 README 头部;预检包发给用户后才许发射")


def cmd_list(_a):
    idx = os.path.join(RUNS, "README.md")
    if os.path.isfile(idx):
        print(open(idx, encoding="utf-8").read())
    else:
        print("(还没有任何 RUN;用 new 建第一个)")


def main():
    ap = argparse.ArgumentParser(description="RUN 收纳箱脚手架(A14)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="新建一个 RUN 收纳箱")
    n.add_argument("--tag", required=True, help="短标签,小写字母数字短横线")
    n.add_argument("--deck", required=True, help="本轮 deck 路径(须已在 decks\\)")
    n.add_argument("--goal", default="<填目标>", help="一句话目标")
    n.add_argument("--var", default="<填单变量>", help="本轮唯一变量(A8)")
    n.add_argument("--id", type=int, default=None, help="强制编号(仅示例/修复用)")
    n.set_defaults(func=cmd_new)
    l = sub.add_parser("list", help="打印总索引")
    l.set_defaults(func=cmd_list)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
