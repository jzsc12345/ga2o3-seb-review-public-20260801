# Stage-isolation blocker

## Required contract

```text
G1 parser-only
  → PASS required
G2 structure and mesh
  → PASS required
G3 source-off 300 V static
  → always stop before transient
```

The same authorization forbids candidate modification, auto-fix, stage skipping, and automatic expansion.

## Candidate execution topology

### Arm A

```text
go devedit
  → geometry and mesh
  → structure outf=...
go atlas
  → mesh inf=...
  → material/models/thermcontact
  → solve init and static ramp to 300 V
  → five solve previous
```

### Arm B

```text
go atlas
  → mesh lines
  → region/electrode definitions
  → material/models/thermcontact
  → solve init and static ramp to 300 V
  → five solve previous
```

Neither candidate has a stage selector.

## Tool capability evidence

DeckBuild 5.2.40.R manual, Chapter 3, pages 24–25, says batch mode automatically executes the entire input deck. Its documented batch options do not provide parse-only or start/stop-line execution.

The installed `deckbuild` wrapper exposes `-ascii`, `-run`, output/error routing and related batch options, but no stage selector. The installed `atlas` wrapper forwards simulator options and has no syntax-only/check-only mode.

## Consequence

Launching either committed candidate through the approved standard runner would not provide a guaranteed stop after G1. Truncating the deck, inserting `quit`, or generating stage wrappers would create new execution inputs that the current authorization did not approve.

Therefore the only compliant action is:

```text
STOPPED_BEFORE_G1
PARSER_A=NOT_EXECUTED
PARSER_B=NOT_EXECUTED
NO_AUTO_FIX_AFTER_FAILURE
```

This is an authorization/execution-contract blocker, not evidence about either arm's physics or parser validity.

