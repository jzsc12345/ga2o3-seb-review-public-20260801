# Current-HEAD exclusions

The current public HEAD excludes:

- raw session transcripts and message/turn identifiers;
- PDFs, ZIP archives, simulator structure files, raw logs, terminal transcripts, and EXIT files;
- raw heatmap and native-vertex extraction grids;
- browser, VM, license, credential, cookie, and secret material;
- unredacted governance manifests containing local asset paths;
- presentation files whose embedded notes contain local paths;
- files larger than 95 MiB;
- source Git history from the production workspace.

Earlier public commits are not rewritten. Their existence must not be interpreted as evidence that
the current allowlist was retroactively applied to historical commits.
