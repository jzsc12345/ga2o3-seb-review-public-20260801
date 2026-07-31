#!/bin/bash
# ============================================================================
# harvest_aux_set.sh — 收割官方例子库的 SWEEP/aux 产线语料
# 采集范围（保留相对目录结构）：
#   1) *_aux.in / *aux*.in        —— aux 子 deck（单点求解+EXTRACT）
#   2) *.set                      —— TonyPlot / VictoryVisual 视图配置
#   3) 含 "GO internal" 且含 "SWEEP" 或 "LOAD infile=" 的主 deck —— 扫参引擎实例
# 产物：/tmp/aux_set_harvest.tar.gz + 同名 .index.txt（清单+SWEEP 语法行摘录）
# 用法：bash harvest_aux_set.sh   （在 VM 上跑；一号机经 ssh stdin 调用亦可）
# ============================================================================
set -u
EX=/atctools/Synopsys/Silvaco2024/examples/deckbuild/5.2.40.R
OUT=/tmp/aux_set_harvest
rm -rf "$OUT"; mkdir -p "$OUT"
cd "$EX" || { echo "例子库不存在: $EX"; exit 1; }

# 1+2) aux 与 set
find . -type f \( -name "*aux*.in" -o -name "*.set" \) > /tmp/_h_list.txt

# 3) 含扫参引擎的主 deck
grep -rlE "^[[:space:]]*(GO|go)[[:space:]]+internal" --include="*.in" . 2>/dev/null | while read -r f; do
  if grep -qiE "^[[:space:]]*(SWEEP|LOAD[[:space:]]+infile=)" "$f"; then echo "$f"; fi
done >> /tmp/_h_list.txt

sort -u /tmp/_h_list.txt > /tmp/_h_uniq.txt
N=$(wc -l < /tmp/_h_uniq.txt)
echo "命中 $N 个文件"

# 复制（保结构）+ 索引
while read -r f; do
  d="$OUT/$(dirname "$f")"; mkdir -p "$d"; cp "$f" "$d/"
done < /tmp/_h_uniq.txt

{
  echo "# aux/set/SWEEP 语料索引  $(date '+%F %T')  共 $N 文件"
  echo; echo "## SWEEP 语法实例（主 deck 内的原行）"
  grep -rHnE "^[[:space:]]*SWEEP" --include="*.in" "$OUT" | sed "s|$OUT/||"
  echo; echo "## LOAD infile= 实例"
  grep -rHnE "^[[:space:]]*LOAD[[:space:]]+infile=" --include="*.in" "$OUT" | sed "s|$OUT/||" | head -40
  echo; echo "## 文件清单（相对例子库根）"
  ( cd "$OUT" && find . -type f | sort )
} > "$OUT.index.txt"

tar czf "$OUT.tar.gz" -C "$OUT" .
echo "打包: $OUT.tar.gz ($(du -h $OUT.tar.gz | cut -f1))  索引: $OUT.index.txt"
