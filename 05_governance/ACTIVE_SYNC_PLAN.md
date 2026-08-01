# Synchronization plan — completed public-safe record

Objective: publish two review surfaces without inheriting restricted source history.

Completed gates:

1. Rule semantics independently rechecked: 16/16 pass.
2. Candidate inventory closed: 25 accounted, zero unaccounted.
3. Root and Harness discovery repaired and validated.
4. User's conditional seal authorization bound to the canonical payload digest.
5. Source layout, lock, package, links, provenance, cutoff, candidates, and protected hashes pass.
6. Private Case-B allowlist built, validated, committed, and pushed without source history.
7. User's final acceptance and ratification recorded as `USR-SEAL-004` and `USR-SEAL-005`.
8. Private and public sanitized `main` branches synchronized by fast-forward push.

Completed public gate:

- rebuilt the current HEAD from an explicit allowlist;
- retained prior public Git history without rewriting it;
- verified zero restricted extensions, raw transcripts, high-confidence secrets, oversized files,
  absolute local paths, message/session identifiers, broken links, and manifest mismatches;
- pushed only the current `main` branch with no force or mirror operation.

RUN121 and all new simulation or physics changes remain outside this plan.
