# Prompt: Refine Prompt Pack From Validated Findings

Use this when you have a blockchain or DLT repo that already contains confirmed findings under `validated-findings/kept` and you want to improve the reusable prompt pack in this repository.

## Objective

Learn reusable hunt logic from real confirmed findings without overfitting the runtime prompts to one codebase.

## Prompt

```text
You are refining the reusable prompt pack in `/testing/dlt-ai-audit-system` using a blockchain or DLT repository that already contains confirmed findings in `validated-findings/kept`.

Your job is not to re-audit the target repo from scratch and not just to summarize the known findings.

Your job is to answer this question:
"What reusable audit instructions, hunt heuristics, validation questions, or bug-family prompts would have materially increased the chance of finding these issues in a fresh audit of this codebase, without leaking the exact answers into the prompt pack?"

Inputs:
- The target repository source code and docs
- The target repository's `validated-findings/kept` folder
- The current prompt pack in `/testing/dlt-ai-audit-system`:
  - `00_protocol_mapper.md`
  - `01_base_hunter.md`
  - `02_validation_and_impact.md`
  - `prompts/`
  - optionally `prompt-provenance.md` and `finding-to-prompt-map.md` for calibration

Before doing any prompt-refinement work:
- Locate `validated-findings/kept` in the target repository.
- Enumerate the findings inside it.
- Treat those finding files as the primary evidence set for this task.
- If the folder is missing or empty, say so clearly and stop instead of guessing.

Step 1: Build repo context first.
- Read enough of the target repo to understand architecture, trust boundaries, terminology, major state machines, privileged roles, and high-risk entrypoints.
- Do not analyze findings in a vacuum.

Step 2: Analyze each confirmed finding in repo context.
For each finding in `validated-findings/kept`:
1. Locate the relevant code path.
2. Reconstruct the failure mechanism in repo-specific terms first.
3. Extract the reusable elements:
   - violated invariant
   - missing property
   - trust boundary crossed
   - entrypoint type
   - sensitive sink
   - code shape or asymmetry
   - early suspicious signals an auditor could have noticed before knowing the answer
   - false-positive killers or compensating controls that would have invalidated the hypothesis
4. Write a short "candidate hunt recipe" for how an auditor could have been led toward this bug family without naming the exact known issue.

Step 3: Cluster findings by reusable failure mechanism.
- Cluster by missing property, invariant failure, and code shape.
- Do not cluster primarily by repo module name, subsystem label, or exact vulnerable function.
- If several findings teach the same lesson, produce one family-level cluster instead of one prompt per finding.

Step 4: Compare those clusters against the existing prompt pack.
For each cluster, decide whether it should:
- strengthen `00_protocol_mapper.md`
- strengthen `01_base_hunter.md`
- strengthen `02_validation_and_impact.md`
- strengthen one existing family prompt in `prompts/`
- become a new family prompt in `prompts/`
- or stay only in corpus/provenance because it is too repo-specific to improve runtime prompts

Step 5: Apply strict anti-overfitting rules.
- Do not copy the answer path into the prompt.
- Do not anchor on repo-specific function names, file names, constants, or role names unless they can be translated into generic blockchain/DLT concepts.
- Prefer instructions like "compare all transition paths that clear validator readiness state" over "inspect function X for field Y".
- If a lesson is only useful for this repo or one implementation style, keep it out of the runtime prompt pack.

Step 6: Use a high bar for new prompt families.
- Add a new family only if the existing families cannot express the hunt cleanly without becoming muddy.
- A new family is more justified when:
  - the mechanism appears in multiple findings, or
  - it is clearly fundamental and portable across blockchain/DLT systems, even if this repo has only one example
- If the finding merely sharpens an existing family, update that family instead of creating a new one.

Step 7: Validate your own proposed improvements.
- For every proposed prompt change, explain why it improves transferability rather than just describing a known bug after the fact.
- If enough findings exist, hold out at least one finding or cluster while drafting the wording, then check whether the revised prompt would still help surface the held-out case.
- If a real holdout is not possible, say so explicitly.

Required output:

1. Repo context summary
- Architecture summary
- Trust boundaries
- High-risk entrypoint categories
- State-machine or lifecycle patterns that matter for these findings

0. Finding inventory
- path to the target repo's `validated-findings/kept` folder
- list of findings analyzed
- any findings intentionally skipped and why

2. Finding-to-mechanism analysis
For each finding:
- finding id or title
- repo-specific failure mechanism
- generic violated invariant
- generic missing property
- code-shape summary
- hunt recipe
- false-positive killers

3. Family clustering
For each cluster:
- cluster name
- findings grouped into it
- why they belong together
- whether the lesson is portable or repo-specific

4. Prompt-pack comparison
For each cluster:
- existing prompt file affected, if any
- what the current prompt misses or handles weakly
- whether to refine, add, or reject
- why

5. Proposed prompt changes
For each approved change:
- target file path
- exact draft text to add or replace
- rationale
- repo-specific details intentionally excluded
- overfitting risk check

6. New family prompts, if justified
- draft file name
- objective
- full prompt text
- explanation of why existing families were insufficient

7. Validation notes
- held-out check result, if performed
- remaining doubts
- prompts that should stay unchanged

Constraints:
- Favor family-level prompt improvements over finding-specific prompts.
- Keep runtime prompts generic, portable, and action-oriented.
- Keep provenance and repo-specific evidence separate from runtime instructions.
- Be willing to conclude that some findings should refine the corpus only and not change the prompt pack.
```
