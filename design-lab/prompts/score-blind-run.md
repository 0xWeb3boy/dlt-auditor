# Prompt: Score Blind Audit Run

Use this after an audit design has completed a blind run on a previous competition.

## Objective

Compare the design's produced findings against the known competition findings without rewarding shallow keyword overlap.

## Scoring Standard

A known finding counts as **found** only if the blind audit output identifies the same reusable vulnerability mechanism:

- same or equivalent root cause,
- same affected protocol surface or trust boundary,
- same missing property,
- compatible attacker capability or trigger,
- compatible impact category.

Exact title, wording, file path, and line number do not need to match. A vague family-level mention is not enough.

## Required Output

Write `scorecard.md` with:

- benchmark name,
- design name,
- audit run path,
- ground truth path,
- total known findings,
- found count,
- missed count,
- partial count,
- false positives,
- duplicate findings,
- recall by severity if severity is available,
- recall by bug family or missing property,
- precision notes.

Write `result-record.json` with exact machine-readable result details:

- comparable numeric `score`,
- total known findings,
- every found ground-truth finding id/title/severity,
- matching blind-audit candidate id(s),
- files in the audit output that contain the matching evidence,
- every partially found finding and what was missing,
- every missed finding,
- false-positive audit candidates,
- duplicate groups.

Write `misses.md` with one section per missed or partial finding:

- finding id/title,
- expected mechanism,
- expected surface,
- what the design did inspect nearby, if anything,
- why it was missed:
  - mapper gap,
  - corpus retrieval gap,
  - family prompt gap,
  - target-code search gap,
  - validation/downgrade gap,
  - reporting/dedup gap,
  - unclear/insufficient evidence in ground truth,
- what general audit lesson would have helped,
- overfitting details that must **not** be copied into the design.

## Constraints

- Do not change the design during scoring.
- Do not score a finding as found merely because the design named a broad family.
- Be explicit about partial credit.
- Mark ambiguous cases separately instead of forcing found/missed.
- The exact found/partial/missed finding ids must be recoverable from `result-record.json`; do not leave that information only in prose.
