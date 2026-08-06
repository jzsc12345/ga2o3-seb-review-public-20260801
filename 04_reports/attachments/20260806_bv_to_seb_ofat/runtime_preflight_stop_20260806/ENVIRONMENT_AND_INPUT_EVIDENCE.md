# Environment and input evidence — stopped before G1

## Fixed input

- commit: `994d83bc444e7a17695f003b65f0d90da25c8023`
- branch at inspection: `main`
- local public worktree: clean and aligned with `origin/main`
- candidate byte comparison against the fixed commit: no difference
- no new hashes were generated

## Active forbidden-token check

The check matched only active, non-comment statements:

```text
OFAT_A_bv_devedit_static300_sourceoff_preflight.in
ACTIVE_FORBIDDEN_COUNT=0

OFAT_B_bv_direct_atlas_static300_sourceoff_preflight.in
ACTIVE_FORBIDDEN_COUNT=0
```

Patterns covered active `singleeventupset`, active `tonyplot`, and active `solve ... tfinal`.

## SSH and VM identity

```text
SSH config: silvaco -> root@192.168.50.100:22
remote hostname: tcad
remote hostname -I: 192.168.50.134
OS: Red Hat Enterprise Linux Server release 7.9 (Maipo)
SILVACO root: /atctools/Synopsys/Silvaco2024
DeckBuild versions installed: 5.2.29.R, 5.2.40.R
ATLAS versions installed: 5.38.0.R, 5.40.0.R
SFLM: service active; TCP 3162 listening
tmux: none
atlas: none
dbascii.exe: none
deckbuild.exe: none
```

## Remote workdir

Planned path:

```text
/root/DECKBUILD/preflight/OFAT_994d83b_20260806
```

Observed state:

```text
REMOTE_PREFLIGHT_NOT_CREATED
```

No remote file or directory was created in this attempt.

