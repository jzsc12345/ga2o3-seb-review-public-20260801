# Silvaco TCAD End-to-End Agent Skill

> English companion of [README.md](README.md) (section layout differs; facts aligned at v0.3.1). When the two disagree, the Chinese README is authoritative.

[中文 README](README.md) | English README

Current version: `v0.3.1` (atlas.key audit — aligned with the Chinese README; see Changelog)

This skill is an operating manual that makes agents less careless when driving **Silvaco TCAD** (DeckBuild / ATLAS / Athena / DevEdit / TonyPlot). The primary target runtime is **OpenAI Codex** (which reads `AGENTS.md`), but every file is plain Markdown, so Claude Code, Claude.ai, OpenCode, or any agent that can read custom instructions can use it too.

It is not a Silvaco installer, and it contains no Silvaco proprietary files, licenses, manuals, or example decks. What it provides is a workflow plus a set of guardrails so TCAD work stays traceable and reproducible.

The workflow is:

```text
Problem definition → literature and documentation search → $SILVACO/examples check → run directory layout →
single merged .in deck (structure + electrical) → deckbuild -run submission → monitoring →
.out/.log/.str diagnosis → TonyPlot / Python visualization and report → knowledge capture → next iteration
```

## Porting map: one Sentaurus tool, several Silvaco options

The single most important property of this port: wherever the original had exactly **one** tool and Silvaco offers **several** ways to do the same job, the skill never silently picks one. It lists **candidate options** and tags the recommended one **[default]**. You (or the agent) may override any default, as long as the choice is stated in the run record.

| Sentaurus concept (removed) | Silvaco candidates |
|---|---|
| Sentaurus TCAD | Silvaco TCAD |
| Sentaurus Workbench / SWB | **[default] DeckBuild** (interactive/batch runner) · VWF Virtual Wafer Fab (DOE / split table) · plain shell or Python runner |
| swbpy2 (Python project API) | **[default] DeckBuild `set` variables + external Python/shell deck generation** · VWF Automation Tools · DeckBuild `loop` / `l.end` |
| gsub (submit) | **[default] `deckbuild -run -ascii <deck>.in -outfile <deck>.out`** · `simulate` (from inside DeckBuild) · VWF job submit · `nohup ... &` daemon runner |
| node number `n<N>` | run directory name / case tag, e.g. `RUN_<case>_<UTCstamp>` |
| SDE / Structure Editor (scheme) | **[default] ATLAS built-in mesh statements** `mesh / x.mesh / y.mesh / region / electrode / doping` (rectangular layer stacks) · **DevEdit** (arbitrary polygons + automatic remeshing, `go devedit`) · **Athena** (structure from process simulation) · Victory Process (3D process) |
| SDevice | **[default] ATLAS** (`models / material / mobility / impact / trap / contact / thermcontact / method / solve`) · Victory Device (3D) |
| SVisual | **[default] TonyPlot** (2D structure + curves) · TonyPlot3D · **Victory Visual** (newer, publication-grade export) · external Python parsing of `.log` |
| `.cmd` deck | `.in` deck |
| `.tdr` (spatial) | `.str` (structure / solution snapshot) |
| `.plt` (curves) | `.log` (ATLAS log file — I-V / transient curves) |
| `STDB` | project root (this project: remote `/root/DECKBUILD`) |
| `STROOT` / `STRELEASE` | Silvaco install root (this machine: `/atctools/Synopsys/Silvaco2024`); pin the version explicitly with `simflags="-V 5.40.0.R"` |
| Synopsys license daemon | **SFLM** — `SFLM_SERVERS=+localhost`, `sflm_monitord`, `sflm` CLI |
| Applications Library | `$SILVACO/examples/` (Silvaco Examples) · ATLAS manual at `$SILVACO/lib/atlas/5.40.0.R/docs/atlas_users1.pdf` — **not** in `$SILVACO/doc/` (that directory holds only 13 install / SFLM / quickstart PDFs) · parameter authority `$SILVACO/lib/atlas/5.40.0.R/common/atlas.key` |
| Termination strings "Good Bye" / FATAL / "Step-size is too small" | ATLAS termination **candidates**: normal end `quit` / process exit 0 · `ATLAS DIED` · `Convergence failure` / `solution did not converge` · `fail.quit` triggered · `License` error — **unverified**: none of these strings has been confirmed against a real `.out` yet (`atlas.key` only registers statement parameters, not runtime messages); calibrate the exact wording/casing during the first preflight, and until then match case-insensitively (`grep -Ei`) with a process-gone fallback (mirrors the notice under §7.5 of the Chinese README) |
| `ExtendedPrecision(80)` | No exact equivalent. Closest levers: `method climit=1e-4` (**not** a precision knob — see the correction note below the table) · `itlimit=` [verified: `atlas.key:644  itlimit NUM 1 25`] · `max.temp=` [verified: `atlas.key:711  max.temp NUM 71 2000.0` — note the default is already 2000 K, so *raising* it is what relaxes a self-heating run]; for wide-bandgap use `models fermi incomplete bgn` |
| Newton / Gummel / Coupled | `method newton` · `method gummel` · **`method block newton carriers=2`** (first choice for high-voltage / self-heating) [verified: `atlas.key:829 gummel LOG 29 t` / `830 block LOG 30 t` / `831 newton LOG 31 t` / `729 carriers NUM 87 2`, all inside the METHOD card 643–961] |
| HeavyIon statement | `singleeventupset` (built-in Gaussian track) · `singleeventupset F.SEU=<file>.c` (C-interpreter custom space/time distribution) [verified: `atlas.key:7999 singleeventupset 51`, `8002 f.seu CHAR 3`] |
| Traps section | `trap` statement (`donor/acceptor e.level sign sigp density`) [verified: `atlas.key:6962 trap 40`, `6963 donor LOG 1`, `6964 acceptor LOG 2`] · `inttrap` — **two `t`s** — for interface states [verified: `atlas.key:7615 inttrap 45`; the spelling `intrap` returns **zero** hits in atlas.key and does not exist]. Unit trap: `trap density` is a volume density (cm⁻³), `inttrap density` is an area density (cm⁻²) |
| Thermodynamic / thermal models | `models lat.temp` [verified: `atlas.key:1019 lat.temp LOG 43 f`, MODELS card] + `thermcontact` (`ext.temper` [`atlas.key:7603`, default 300 K, exact synonym `temperature` on the same slot at `7604`], `alpha` = 1/R_th, units W/(cm²·K) [`atlas.key:7602 alpha NUM 6 0`]) + `material tcon.const` — a bare LOG flag [`atlas.key:2980`], the value goes in `tc.const=` [`atlas.key:2036`], never `tcon.const=0.13`. Omitting `alpha` selects the fixed-temperature (Dirichlet) branch = ideal isothermal sink; writing `alpha=0` literally is *not* a perfect heat sink |
| `Plot` / `Save` sections | `save outf="*.str"` · `output <fields>` · `log outf="*.log"` / `log off` |

> **Correction — what `climit` actually is.** `climit` is **not** a residual or convergence tolerance, and "smaller = stricter/better" is wrong. It is a **dimensionless concentration normalization factor** that sets the minimum carrier concentration the solver bothers to resolve.
>
> ```text
> $ grep -n -i 'climit' /atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key
> 688:   climit       NUM     51      10000
> 726:   climit.dd    NUM     85
> 728:   climit.eb    NUM     86       0.
> ```
>
> So the default is `1e4` — a *large* number, not a small tolerance. The ATLAS manual (`atlas_users1.pdf`, `pdftotext` lines 3375–3380) says: "CLIMIT or CLIM.DD specify minimal values of concentrations to be resolved by the solver. … **A value of CLIMIT=1e-4 is recommended for all simulations of breakdown**, where the pre-breakdown current is small. CLIM.DD is equivalent to CLIMIT but uses the more convenient units of cm-3 for the critical concentration." And at line 53386: "The default value of CLIMIT is set at 10⁴ (the corresponding default value for CLIM.DD in Silicon is 4.5·10¹³ cm-3). In simulation of breakdown, a lower value of CLIM.DD (~10⁸ cm-3 for Silicon diodes) should be specified. Otherwise, a 'false' solution may be obtained."
>
> Consequences for this skill: (a) `climit=1e-4` in a breakdown / low-leakage deck is the **manual's own recommendation**, not a convergence hazard; (b) never describe it as "tightening the convergence tolerance"; (c) `climit` is unitless — for the same knob in cm⁻³ the manual's METHOD defaults table (`atlas_users1.pdf` p.1417) lists **both** `CLIM.DD` and `CLIMIT.DD` as synonymous parameters (Si default 4.5e13 cm⁻³ for both). Note a discrepancy this package cannot currently resolve: the grep record above shows `climit.dd` at `atlas.key:726`, while the Chinese README recorded `clim.dd` at `:725` — the exact registered name/line is **[pending atlas.key re-check]** (remote VM offline), so grep `atlas.key` before writing either spelling into a deck.

## Supported agent environments

| Environment | Recommended use | Notes |
|---|---|---|
| OpenAI Codex | Keep `AGENTS.md` at the repo root pointing to `SKILL.md`; keep `references/` alongside it | Primary target; no `.skill` packaging required |
| Claude Code | Copy the files into `~/.claude/skills/silvaco-tcad/`, or reference them from the project | `references/` are loaded on demand |
| Claude.ai / Claude Desktop | Attach `SKILL.md` and the needed `references/*.md` as project knowledge | Good for planning, review, deck generation; commands still run on your Silvaco host |
| OpenCode / OpenClaw / other LLM agents | Drop the Markdown files into the agents / skills / instructions directory | Read `SKILL.md` first, then load references as needed; adapt tool calls and shell permissions yourself |

For new users: **this is an operating manual for agents, not a Silvaco installer.** You need a licensed, working Silvaco TCAD environment before this skill can help.

## When to use this skill

Use this skill when you want an agent to help with:

- Creating or repairing a Silvaco run directory and its merged `.in` deck.
- Writing structure, doping, contact, and mesh definitions (ATLAS mesh statements, DevEdit, or Athena — pick from the candidates).
- Writing ATLAS `models / material / mobility / impact / trap / contact / thermcontact / method / solve` blocks.
- Running Id-Vg, Id-Vd, BV, single-event upset (`singleeventupset`), SEB, TID, ESD, or self-heating simulations.
- Diagnosing convergence failures, abnormal leakage, breakdown location, or SEB criteria.
- Working on GaN HEMT, p-GaN HEMT, radiation effects, and reliability simulations.
- Keeping results reviewable: `.log` curves, `.str` snapshots, TonyPlot views, plots, and reports.

## Core rules

The skill instructs the agent to follow these rules:

1. **Research before simulation**
   Physics models, material parameters, traps, polarization, impact ionization, SEU tracks, and thermal boundary conditions must be backed by `$SILVACO/examples`, documentation, literature, or verified experience. If the remote VM is offline/unreachable, verify against the local read-only mirrors under `D:\knowledge\` instead (`pdf25\atlas_users1.pdf` = ATLAS manual, `exp25\` = official example decks, `material_sil\` = official material parameter library); claims that only the remote `atlas.key` can settle (registered name / line / default) stay tagged **[pending atlas.key re-check]** until the remote is back — never assert them from memory.

2. **Every run lives in its own run directory**
   Create `/root/DECKBUILD/RUN_<case>_<UTCstamp>/` and keep the deck, `.out`, `.log`, and `.str` of one experiment together. No orphan decks scattered across the project root.

3. **One deck contains both structure and electrical simulation**

   ```silvaco
   go atlas simflags="-V 5.40.0.R -P 4"
   mesh space.mult=1.0
   x.mesh loc=0.0 spac=0.1
   # ... region / electrode / doping ...
   save outf=dev_struct.str

   go atlas simflags="-V 5.40.0.R -P 4"
   mesh inf=dev_struct.str
   models fermi incomplete bgn print
   method block newton carriers=2
   solve init
   log outf=idvg.log
   solve vgate=0 vstep=0.1 vfinal=5.0 name=gate
   log off
   save outf=dev_final.str
   quit
   ```

4. **Submit through the chosen runner (default: DeckBuild batch)**

   ```bash
   export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
   export SFLM_SERVERS=+localhost
   deckbuild -run -ascii dev.in -outfile dev.out
   ```

   Candidates: `deckbuild -run` **[default]** · `simulate` inside an interactive DeckBuild session · VWF job submit · `nohup ... &` daemon runner for long jobs.

5. **Do not hardcode paths or IPs**
   The Silvaco `bin/` directory is **not** on `PATH` by default — `export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH` explicitly. Do **not** source `/atctools/Synopsys/Silvaco2024/etc/silvaco.profile`: probing showed it is a 315-byte csh stub that only prints echo text and sets no variables (see `references/preflight-and-environment.md` §2.2). The SSH host IP must be probed at runtime (see the environment section below).

6. **Start a one-shot background monitor after submission**

   ```bash
   until grep -qEi "ATLAS DIED|Convergence failure|solution did not converge|License" dev.out 2>/dev/null \
         || ! pgrep -f "atlas.*dev\.in" >/dev/null 2>&1; do sleep 60; done
   tail -30 dev.out
   ```

   Pick the termination condition from the candidate list in the mapping table; state which one you used. Do not grep for a bare `Error`, and do not read the whole `.out` file — `tail -20`/`tail -30` is enough for a progress check. The authoritative completion signal is the runner's `.exit` exit-code sentinel file (see `references/batch-run-and-monitor.md` §6/§8); the grep + process-gone loop above is only the degraded fallback when no runner wrapper exists — never rely on `pgrep`/`ps` alone to declare a run finished.

7. **Inspect both `.log` and `.str` results**
   `.log` files hold the I-V / transient curves; `.str` files hold the spatial distribution. Terminal output alone is never a conclusion.

8. **Persist results + the two-failure rule**
   Produce at least a PNG plot, a Markdown table, or a report, and update the progress and findings notes. For repeated failures of the same kind, attempt at most **two** fixes; if the second attempt still fails, stop blind tuning and go back to reference search and root-cause analysis (mirrors rule 8 of the Chinese README).

## Verified environment (facts for this user)

These were probed on this machine; state them as facts, do not re-derive them from guesses.

- Remote host: `tcad`, RHEL 7.9, 8 vCPU / 8 GB RAM, ~124 GB free on `/` (probed 2026-07-26; drifts with use).
- SSH: `ssh -i C:/Users/Administrator/.ssh/silvaco_ed25519 root@192.168.50.134` (probed alive on 2026-07-26, hostname `tcad`; `192.168.107.128` was unreachable the same day).
  The remote `ens33` address comes from DHCP (`valid_lft 915sec`), so the IP drifts across boots; the alias `silvaco` currently resolves to the **live** `192.168.50.134`. **Probe the IP and verify `hostname` == `tcad` at the start of every session, and never hardcode either address into a runner** (see `references/preflight-and-environment.md` §1).
- Silvaco install root: `/atctools/Synopsys/Silvaco2024`, executables in `bin/` (`deckbuild atlas athena devedit tonyplot quest sflm ...`). **Not on `PATH` by default.**
- Available ATLAS versions: `5.38.0.R` and `5.40.0.R`. This project freezes `-V 5.40.0.R -P 4`.
- License: SFLM, `export SFLM_SERVERS=+localhost`; `sflm_monitord` is already running.
- GUI: X display `:0` exists (root logged in on tty1). Export `DISPLAY=:0` before any GUI tool.
- Shared folders: `/mnt/hgfs/{share_wm,share24,16sil_share}` (VMware HGFS, already 98% full — do not write large files there).
- Production project directory: `/root/DECKBUILD/`.

## File-placement discipline

This is the user's explicit rule and the skill repeats it wherever it matters:

- The control machine `D:\SILVACO_LOCAL` holds **only**: `.py` scripts, `.md` technical docs, lightweight `.csv`, `.png` screenshots and figures, and `.in` decks.
- Each `.in` deck **merges structure building and electrical characterization into one file**:
  `go atlas` (build) → `save outf=*.str` → `go atlas` (re-enter) → `mesh inf=*.str` → electrical solve.
- **All bulky `.str` / `.log` artifacts are archived to Windows `E:\silvaco2425\bulk\{str,log}\`**; during a run they stay in `/root/DECKBUILD/<run>` and are pulled back afterwards.
- Remote `/root/DECKBUILD` is the one and only live iteration area. Do not mirror the whole remote project tree back to Windows.

## Repository layout

```text
skills/silvaco-tcad/
├── AGENTS.md                          # Codex entry point; points at SKILL.md
├── SKILL.md                           # Main skill entry: triggers, workflow, hard rules
├── references/
│   ├── preflight-and-environment.md   # First-run environment check on a new machine
│   ├── structure-and-mesh.md          # ATLAS mesh vs DevEdit vs Athena: geometry, contacts, doping, mesh
│   ├── device-physics-and-solver.md   # ATLAS models / material / mobility / impact / trap / method / solve
│   ├── batch-run-and-monitor.md       # DeckBuild / VWF / shell runner candidates, submission, monitoring
│   ├── wbg-radiation-and-seb.md       # Wide-bandgap devices, BV, singleeventupset, SEB methodology
│   └── results-and-reporting.md       # TonyPlot, .log/.str diagnosis, plotting, reports
├── evals/
│   └── evals.json                     # Example trigger prompts
├── README.md                          # Chinese README
└── README_EN.md                       # English README
```

These six are the **only** reference filenames that exist. Earlier revisions of this README (and of `AGENTS.md`) advertised `new-device-preflight.md`, `deckbuild-runner.md`, `structure-mesh-patterns.md`, `atlas-patterns.md`, `gan-hemt-and-seb.md`, and `results-reporting.md` — none of those files were ever shipped, so any link to them is dead. `SKILL.md` §5 has always carried the correct set.

## Changelog

### v0.3.1 (atlas.key audit)

Every ATLAS keyword claim in the package was re-checked against `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key` (ATLAS 5.40.0.R). Changes landing in this file:

- **`intrap` → `inttrap`** (two `t`s) in the mapping table. `intrap` has zero hits in `atlas.key`; `inttrap` is card 45 at line 7615.
- **`climit` semantics corrected.** It was presented as a precision / convergence-tolerance knob (the `ExtendedPrecision(80)` row). It is a dimensionless concentration normalization factor with default `1e4`; see the correction note under the mapping table.
- **Repository layout fixed.** Six reference filenames listed here never existed; replaced with the six that ship. Same for the "minimum useful set" block and the preflight cross-reference.
- **Evidence tags added** to the ATLAS-syntax rows (`method`, `singleeventupset`, `trap`/`inttrap`, `thermcontact`/`material`) in the form `[verified: atlas.key:<line>]`.
- **Two guardrails added** to the "What problems does it prevent?" table: the grep-or-未核实 tagging rule, and the Victory Device provenance check.

### v0.3.0 (Silvaco port)

- Replaced every Sentaurus-specific proper noun with its Silvaco equivalent, per the mapping table above.
- Wherever Silvaco offers several tools for one job, the skill now emits an explicit candidate list with a **[default]** tag instead of silently choosing.
- Retargeted at OpenAI Codex (`AGENTS.md`) while staying readable by any Markdown-reading agent.
- Baked in this user's verified environment: `/atctools/Synopsys/Silvaco2024`, SFLM `+localhost`, ATLAS `-V 5.40.0.R -P 4`, project root `/root/DECKBUILD`.
- Added the file-placement discipline (control machine keeps text-scale files; bulk `.str`/`.log` archive to `E:\silvaco2425\bulk\`).
- Replaced node-number tracking with run-directory tags `RUN_<case>_<UTCstamp>`, and replaced the fixed termination string with a candidate list.

## Installation

### Option A: OpenAI Codex

Keep `AGENTS.md`, `SKILL.md`, and `references/` in the repository Codex opens. Codex reads `AGENTS.md` automatically; `AGENTS.md` tells it to read `SKILL.md` first and pull `references/*.md` on demand.

### Option B: Claude Code

```bash
mkdir -p ~/.claude/skills/silvaco-tcad
cp SKILL.md ~/.claude/skills/silvaco-tcad/
cp -r references ~/.claude/skills/silvaco-tcad/
```

Reload Claude Code afterwards, then ask: "Use the silvaco-tcad skill to ...".

### Option C: Other agent environments

Place `SKILL.md` and `references/` in whatever skill / instruction / knowledge directory your platform supports. The only thing that matters is that the agent reads `SKILL.md` first and loads reference files on demand.

If the platform has no formal "skill" concept, use the files as project-level system instructions. The minimum useful set is:

```text
SKILL.md
references/preflight-and-environment.md
references/batch-run-and-monitor.md
references/results-and-reporting.md
```

Add `references/structure-and-mesh.md`, `references/device-physics-and-solver.md`, or `references/wbg-radiation-and-seb.md` when the task needs them.

## Prerequisites

You need your own licensed Silvaco TCAD installation. This repository contains no Silvaco software, licenses, manuals, or example decks.

Recommended setup:

- Working `deckbuild`, `atlas`, `devedit`, `tonyplot` commands (after exporting the Silvaco `bin/` on `PATH`).
- A writable project root, e.g. `/root/DECKBUILD/`.
- A reachable SFLM license server (`SFLM_SERVERS`, `sflm_monitord`).
- Access to `$SILVACO/examples/`, the ATLAS manual at `$SILVACO/lib/atlas/<ver>/docs/atlas_users1.pdf`, and the parameter table `$SILVACO/lib/atlas/<ver>/common/atlas.key` (`$SILVACO/doc/` holds only install / SFLM / quickstart PDFs — the ATLAS manual is **not** there).
- Literature search tools such as Zotero, institutional access, or public databases.

On a new machine, ask the agent to run a full preflight before writing decks or submitting jobs. At minimum:

```bash
export PATH=/atctools/Synopsys/Silvaco2024/bin:$PATH
export SFLM_SERVERS=+localhost
command -v deckbuild atlas devedit tonyplot
printf '%s\n' "$SILVACO" "$SFLM_SERVERS" "$DISPLAY"
test -d /root/DECKBUILD && test -w /root/DECKBUILD
pgrep -a sflm_monitord
```

The preflight should also confirm which ATLAS versions are installed, that a trivial deck actually checks out a license, that `DISPLAY=:0` works if GUI tools are wanted, and that `$SILVACO/examples` is readable. See `references/preflight-and-environment.md` for the full checklist.

If preflight fails, the agent must stop the simulation plan and report the blocker. License, `PATH`, project-root, or display failures are **not** physics-model problems and must not be "fixed" by editing models.

## Example prompts

### First run on a new machine

```text
Use the silvaco-tcad skill to check whether this server can run Silvaco simulations. Do not write decks or launch deckbuild yet; run the new-device preflight first and verify PATH, the Silvaco install root, SFLM license, available ATLAS versions, DISPLAY, $SILVACO/examples, and write permission on /root/DECKBUILD.
```

### Create a p-GaN HEMT run from scratch

```text
Use the silvaco-tcad skill to build a p-GaN HEMT run from scratch. Run IdVg first to check Vth > 1.2 V, then BV up to 900 V. Search $SILVACO/examples and the literature first, then tell me which structure-building candidate you picked (ATLAS mesh statements / DevEdit / Athena) and why, and give me one merged .in deck plus the runner command and the result-logging flow.
```

### Diagnose a BV convergence failure

```text
My GaN HEMT BV run stops converging around 720 V and the .out file shows a convergence failure near the gate edge. Do not blindly tune parameters; diagnose it through .out → .log → .str → reference search → fix, and tell me whether the fix belongs in mesh, models, or method.
```

### Single-event upset / SEB threshold scan

```text
I need an SEB threshold scan using singleeventupset at a fixed LET with several load-voltage cases. Generate the cases with the runner candidate you recommend, submit them, and output curves, a table, and the criteria you used.
```

## Quick start for new users

1. Make sure you already have a licensed, working Silvaco TCAD environment.
2. Put `AGENTS.md` + `SKILL.md` + `references/` where your agent reads instructions (see Installation).
3. On the first run on a new machine, ask the agent to run preflight:
   ```text
   Use the silvaco-tcad skill to check whether this machine can run Silvaco simulations. Do not write decks or launch deckbuild yet.
   ```
4. After preflight passes, describe your device, simulation targets, and required outputs.
5. When a run finishes, ask for the run directory tag, the `.out` termination status, the `.log` curve conclusion, the `.str` spatial diagnosis, and a persistent report.

## What problems does it prevent?

| Problem | Skill behavior |
|---|---|
| Agent silently picks one Silvaco tool where several exist | Requires an explicit candidate list with a **[default]** tag, and requires recording the choice |
| Structure and electrical decks drift apart in separate files | Requires one merged `.in` deck: `go atlas` → `save outf=*.str` → `go atlas` → `mesh inf=*.str` → solve |
| Agent only reads the `.out` log | Requires `.out` → `.log` → `.str` layered diagnosis |
| Models and parameters are guessed | Requires evidence from `$SILVACO/examples`, docs, or literature; unverified syntax must be written as a candidate to check, never as fact |
| A keyword is tagged "verified" on the strength of memory | **Standing rule: a claim may be tagged 已核实 / verified only if you can paste the `grep` command and its non-empty output.** The existence authority is `/atctools/Synopsys/Silvaco2024/lib/atlas/5.40.0.R/common/atlas.key` (rows read `name  TYPE  index  default`); a parameter absent from `atlas.key` does not exist in ATLAS 5.40.0.R. Anything you cannot substantiate is tagged 未核实 and **left in place** — never silently deleted |
| Victory Device syntax copied into an ATLAS deck | Many shipped example decks start with `GO victorydevice` / `GO victoryprocess`, not `go atlas`, and their statements are **not** interchangeable (this is the documented origin of the invented `lte.timestep` / `seu.max.rad` / `impact hysteresis` / `impact e.min` lines that this audit removed). Requires running `grep -iE '^ *go ' <deck>.in` on any example before citing it as ATLAS evidence |
| Version and license drift between runs | Requires `simflags="-V 5.40.0.R -P 4"` and `SFLM_SERVERS=+localhost` |
| Hardcoded stale SSH IP or missing `PATH` | Requires probing the live IP and exporting the Silvaco `bin/` every session |
| Bulky `.str`/`.log` files pile up on the control machine | Requires archiving to `E:\silvaco2425\bulk\{str,log}\` and keeping `D:\SILVACO_LOCAL` text-scale |
| Results exist only as terminal text | Requires persistent plots, tables, or reports |
| Huge monolithic skill instructions | Keeps `SKILL.md` short and moves details into `references/` |

## Security and compliance

- This repository contains no Silvaco software, licenses, PDFs, or official example decks.
- Users must ensure they hold a valid Silvaco license.
- Commands here are workflow templates. Do not run them blindly without checking paths, run tags, and version flags.
- Any destructive or overwriting operation requires a backup and explicit user confirmation — in particular, never overwrite an existing `/root/DECKBUILD/RUN_*` directory or an archived `.str`.
- Do not write large files into `/mnt/hgfs/*`; those shares are already ~98% full.
- (`SECURITY.md` is not shipped in this package — the security notes are the bullets above.)

## License

MIT License. (`LICENSE` is not shipped in this package; the licence statement is this line.)

## Contributing

Contributions are welcome, especially:

- New references for SiC, CMOS, power, or photonic devices.
- Verified ATLAS syntax that replaces a "check this in `$SILVACO/examples` or the manual" candidate with a confirmed statement. Attach the `grep` against `atlas.key` (or `atlas_users1.pdf` via `pdftotext`) that proves it — a claim without pasteable output stays tagged 未核实, and please check the example deck's `go` line so Victory Device syntax does not leak in as ATLAS.
- More robust TonyPlot / Victory Visual / Python export templates.
- Runner recipes for VWF, so the VWF candidate becomes as concrete as the DeckBuild default.
- Installation notes for Codex, OpenCode, OpenClaw, and other agent environments.

Maintenance principle: **keep `SKILL.md` concise; put detailed domain knowledge into `references/`; and whenever Silvaco offers more than one way, add a candidate instead of a hidden decision.**
