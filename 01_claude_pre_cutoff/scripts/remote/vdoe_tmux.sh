#!/bin/bash
# ============================================================================
# vdoe_tmux.sh -- VM 端顶层长任务驱动（tmux 会话内跑 VictoryDoE / deckbuild，
# 断开 SSH、无人值守也继续；一号机随时 attach 或抓状态）。
#
# 部署：scp 到 VM 后  install -m 755 vdoe_tmux.sh /root/bin/
# 依赖：tmux（已确认 /usr/bin/tmux 存在）、xctl、会话环境注入。
#
# 用法（在 VM 上或经 ssh 单行调用）：
#   vdoe_tmux.sh start-doe <工作区> <工程名> <split.csv> [并发=2]   # batch_vdoe 建+跑
#   vdoe_tmux.sh start-deck <工作目录> <deck.in>                    # 单 deck 后台跑
#   vdoe_tmux.sh status                                             # 所有会话+尾巴
#   vdoe_tmux.sh tail <会话名>                                      # 看某会话输出
#   vdoe_tmux.sh kill <会话名>                                      # 急停
# 会话命名：vdoe_<工程名> / deck_<deck 基名>
# ============================================================================
set -u

TOOLBOX=/atctools/Synopsys/Silvaco2024/lib/victorydoe/1.1.16.R/x86_64-linux/Toolbox

session_env() {
  # GUI/许可证会话环境（XAUTHORITY 坑的标准解法）
  local SESSPID; SESSPID=$(pgrep -f mate-session | head -1)
  if [ -n "$SESSPID" ] && [ -r "/proc/$SESSPID/environ" ]; then
    eval "$(tr '\0' '\n' < /proc/$SESSPID/environ \
      | grep -E '^(DISPLAY|XAUTHORITY|DBUS_SESSION_BUS_ADDRESS|XDG_RUNTIME_DIR|LANG)=' \
      | sed 's/^\([A-Za-z_][A-Za-z0-9_]*\)=\(.*\)$/export \1="\2"/')"
  fi
  export DISPLAY="${DISPLAY:-:0}"
  [ -z "${XAUTHORITY:-}" ] && [ -r /var/run/lightdm/root/xauthority ] \
    && export XAUTHORITY=/var/run/lightdm/root/xauthority
  export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
  export SFLM_SERVERS="${SFLM_SERVERS:-+localhost}"
}

case "${1:-}" in
  start-doe)
    WS=${2:?工作区}; PROJ=${3:?工程名}; SPLIT=${4:?split.csv}; PAR=${5:-2}
    S="vdoe_${PROJ}"
    session_env
    tmux kill-session -t "$S" 2>/dev/null
    # tmux 自带 pty，deckbuild 不再需要 xterm 包裹；桌面可见性由 GUI 打开同一工程保证
    tmux new-session -d -s "$S" \
      "cd $WS && perl $TOOLBOX/batch_vdoe.pl $PROJ $SPLIT $PAR 2>&1 | tee ${PROJ}_tmux.log; \
       echo EXIT=\$? >> ${PROJ}_tmux.log; sleep 5"
    echo "tmux 会话 $S 已启动（cd $WS; 日志 ${PROJ}_tmux.log）"
    ;;
  start-deck)
    WD=${2:?工作目录}; DECK=${3:?deck.in}; BASE=$(basename "$DECK" .in)
    S="deck_${BASE}"
    session_env
    tmux kill-session -t "$S" 2>/dev/null
    tmux new-session -d -s "$S" \
      "cd $WD && script -q -f -c 'deckbuild -ascii -run $DECK' typescript; \
       grep -a 'simulator exits with code' typescript | tail -1 > EXIT.txt; sleep 5"
    echo "tmux 会话 $S 已启动（cd $WD; 真判据看 typescript）"
    ;;
  status)
    echo "== tmux 会话 =="; tmux ls 2>/dev/null || echo "（无会话）"
    echo; echo "== 各会话末 3 行 =="
    for s in $(tmux ls -F '#S' 2>/dev/null); do
      echo "--- $s ---"; tmux capture-pane -p -t "$s" | tail -3
    done
    echo; echo "== atlas 进程 =="; ps -ef | grep -c "[a]tlas" || true
    ;;
  tail)
    tmux capture-pane -p -t "${2:?会话名}" | tail -30
    ;;
  kill)
    tmux kill-session -t "${2:?会话名}" && echo "已停 $2"
    pkill -f dbascii.exe 2>/dev/null; pkill -f atlas 2>/dev/null || true
    ;;
  *)
    grep '^#   vdoe_tmux.sh' "$0" | sed 's/^# *//'
    exit 2
    ;;
esac
