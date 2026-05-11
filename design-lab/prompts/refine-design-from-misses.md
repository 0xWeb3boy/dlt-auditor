# Prompt: Refine Audit Design From Misses

Use this only after a blind audit run has been scored against known competition findings.

## Objective

Improve the audit design so it is more likely to find the missed mechanisms in future unknown codebases, while keeping the design general and portable.

The refinement agent has broad edit authority inside the candidate design snapshot. It may rewrite, delete, add, split, merge, or reorganize any prompt/design artifact if the change helps the target class of finding be discovered in future unknown repositories.

## Inputs

- The audit design folder being refined.
- `scorecard.md`.
- `misses.md`.
- `result-record.json`.
- The blind audit outputs.
- The known findings only as post-run evidence, never as runtime audit input.

## Process

1. Cluster misses by reusable failure mechanism.
2. For each cluster, identify where the current design failed:
   - repository mapping,
   - corpus search query generation,
   - family prompt coverage,
   - target-code search motifs,
   - validation strictness,
   - dedup/reporting.
3. Decide whether to:
   - rewrite an existing prompt,
   - delete weak or misleading prompt text,
   - add a corpus-search query pattern,
   - delete or replace a noisy corpus-search query pattern,
   - add or refine a template field,
   - add a new family prompt,
   - merge or split family prompts,
   - improve final coverage checks,
   - change the generated audit workflow,
   - change output templates,
   - change candidate validation rules,
   - change parallel-worker instructions,
   - change corpus retrieval/scoring instructions,
   - leave the lesson out because it is too specific.
4. Draft concrete changes.
5. Check overfitting risk.
6. If more than one prompt-pack variant is worth testing, define separate candidate names and keep them as archived candidates rather than new top-level designs.

## Allowed Candidate Changes

Inside `design-lab/runs/<loop>/candidates/<candidate>/design/`, the improvement agent may change anything needed to make the relevant class of finding discoverable:

- Rewrite any `.md` prompt file completely.
- Delete prompt sections that create noise, false confidence, or shallow checklist behavior.
- Add new prompt files for new vulnerability families or cross-family mechanisms.
- Remove, merge, split, rename, or reorder family prompts.
- Change the protocol mapper, base hunter, corpus search, validation, refinement, or final reporting prompts.
- Change templates, required output fields, quality gates, candidate IDs, and coverage tables.
- Change the design scaffolder or runner scripts if the prompt workflow needs different generated files or execution order.
- Add small helper scripts or templates if they support general search, triage, deduplication, or validation.
- Change wording aggressively; preserving old prompt style is not required.

The standard is not "minimal edit." The standard is: can this prompt/design now reliably lead an auditor toward the same class of bug in a new codebase?

## Required Output

Write `design-refinement-plan.md` with:

- summary of score movement needed,
- missed mechanism clusters,
- proposed design changes by file,
- exact draft text or patch description,
- why each change is portable,
- historical details intentionally excluded,
- expected effect on recall,
- expected false-positive risk,
- holdout/next-round check plan.
- recommended candidate name(s) for the next experiment.
- exact files to edit inside the candidate design snapshot.
- any deleted or replaced prompt logic, with the reason it was removed.
- runnable-design checks needed after the edits.

## Constraints

- Do not include exact historical file paths, function names, constants, exploit payloads, or competition-specific answer trails in runtime prompts.
- Do not make the design explicitly target the benchmark's known answer locations.
- Do not edit benchmark ground truth, scorecards, or result records to make a candidate look better.
- Do not edit the audited competition repo as part of prompt improvement.
- Keep the candidate runnable through `bin/design-lab start-round`.
- Prefer family-level hunt logic over one prompt per missed finding.
- Prefer concrete class-level search/validation logic over broad vague warnings.
- If a miss is too repo-specific, record it as corpus/provenance material instead of runtime prompt logic.
- Do not place experimental candidates in `designs/`; keep them under `design-lab/runs/<loop>/candidates/` until the best scored result is promoted.
