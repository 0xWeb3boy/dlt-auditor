# Findings Corpus

Runtime retrieval corpus for DLT audit designs.

The audit runners use `corpus/imports/*/records/*.yaml` plus the matching retrieval cards under each import bundle:

```text
corpus/imports/<bundle>/
  records/
  cards/
    root-cause/
    code-shape/
    validation/
```

`bin/search-corpus` ranks those normalized records and cards against repo-context or family-scan queries. The results are hypothesis generators only; a live finding still needs target-code evidence, reachability, attacker control, and impact.

Raw source findings, conversion templates, benchmark evals, and enrichment workspaces are not required for runtime execution and are intentionally not part of the top-level workflow here.
