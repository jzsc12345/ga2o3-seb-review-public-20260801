# ATLAS 5.40 material-code and master-material audit

> Local official sources: ATLAS 5.40.0.R User's Manual, Table B-1; installed `atlas.key`; SMDB 2.16.0.R. Runtime evidence comes from the already-frozen zero-bias import test. No ATLAS command was executed in this audit.

## 1. ATLAS import rule

ATLAS User's Manual §B.2.4 states that mesh-file materials not listed in Table B-1 automatically become insulator regions with relative permittivity 3.9. Section B.2.5 documents `USER.MATERIAL`, `USER.GROUP`, and `USER.DEFAULT` for defining a new material inside an ATLAS structure/deck.

The already-completed runtime test proves that those post-import cards did not reclassify the incorrectly imported SDB records. Therefore §B.2.5 is not a proven post-import repair mechanism for this route.

## 2. Table B-1 check

Table B-1 includes `GaN` and `ZnO` as binary compound semiconductors. It does not list:

- `BetaGa2O3`;
- `Beta-Ga2O3`;
- `NiOx`;
- `NiO`.

## 3. Code audit

| Code | Current SMDB meaning | ATLAS runtime behavior | Decision |
|---:|---|---|---|
| 50 | no current SMDB `/sdbid/m50` entry found; DevEdit raw STR locally labels it Ga2O3 | imported as Silicon for the Ga₂O₃ semantic records | private/user code; not an ATLAS-recognized Ga₂O₃ identity |
| 259 | SMDB `ga2o3-beta`, SDB name `Beta-Ga2O3` | not runtime tested; name absent from ATLAS Table B-1 | valid SMDB identity, not ATLAS-import proof |
| 304 | SMDB `nio`, SDB name `NiO` | 2,228 `Unknown material #304` warnings, then insulator/SiO₂ | SMDB knows NiO; ATLAS 5.40 importer does not accept this code in the tested SDB route |

## 4. Requested spellings

`BetaGa2O3` and `NiOx` cannot be promoted as ATLAS material identities because neither has an exact installed dictionary match. The exact DevEdit wrappers `UD1(BetaGa2O3)` and `UD2(NiOx)` may be syntactically valid custom labels, but they still traverse user slots rather than an ATLAS Table B-1 material. The closest official names likewise do not appear in Table B-1. Running the label-only variant is outside this task and would not, by itself, establish a controlled material lineage.

## 5. Official ATLAS mapping mechanism

For an ATLAS-built structure, the official mechanism is `USER.MATERIAL` + `USER.GROUP` + `USER.DEFAULT`, followed by explicit `MATERIAL` parameters. For this imported SDB route, post-import reclassification has been experimentally shown nonviable. The next admissible hypothesis is therefore to transport the two semiconductor groups through the SDB using Table B-1-recognized parent identities **before** the Atlas-mode save, then bind explicit physical parameters later.

The parent identities are labels for importer classification only. They are not scientific evidence for using GaN/ZnO defaults in SEB production.
