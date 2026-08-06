# Read-only command register

Only read-only inspection commands were used.

## Local repository and input checks

```text
git status --short --branch
git diff --exit-code <fixed-commit> -- <Arm-A> <Arm-B>
git log -1 --format=...
Select-String active forbidden-token scan
```

## SSH identity and idle-state checks

```text
ssh -G silvaco
ssh silvaco hostname
ssh silvaco hostname -I
ssh silvaco cat /etc/redhat-release
ssh silvaco pgrep -ax atlas
ssh silvaco pgrep -ax dbascii.exe
ssh silvaco pgrep -ax deckbuild.exe
ssh silvaco tmux ls
ssh silvaco systemctl is-active sflm.service
ssh silvaco ss -lntp (port 3162)
```

## Installed tool and manual inspection

```text
read installed DeckBuild/ATLAS version directories
read /atctools/Synopsys/Silvaco2024/bin/deckbuild
read /atctools/Synopsys/Silvaco2024/bin/atlas
extract the relevant DeckBuild manual pages with pdftotext
```

## Explicitly not run

```text
deckbuild -run: NO
DevEdit: NO
ATLAS: NO
Victory*: NO
remote mkdir/copy: NO
simulation: NO
hashing: NO
```

