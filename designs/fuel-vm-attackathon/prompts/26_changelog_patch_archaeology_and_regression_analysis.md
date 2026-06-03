# Prompt Family: Changelog Patch Archaeology And Regression Analysis

## Use This For

- Reconstructing security-relevant mechanisms from local changelogs, release notes, migration notes, and git history.
- Finding fixed vulnerabilities, regression risks, and current-code invariants introduced by a patch.
- Previous-competition or benchmark audits where current `HEAD` may already contain fixes.
- VM, gas, fee, profiling, host-width, consensus-result, storage, parser, and validation fixes.

## Prompt

```text
Hunt for vulnerabilities and regression risks by reading the repository's own patch trail. Use only local repository artifacts unless the audit harness explicitly provides additional references.

Inputs to inspect:
- `CHANGELOG.md`, release notes, migration notes, upgrade guides, advisory notes, and docs sections named fixed, changed, breaking, security, or compatibility;
- local `git log`, `git show`, tags, and branch history when available;
- regression tests added near changed areas;
- code comments that mention previous behavior, compatibility, target architecture, gas schedule changes, or spec corrections.

Do not use benchmark ground truth, scorecards, prior loop artifacts, or known finding files. Do not rely on external network access. If local git history is shallow or unavailable, use the changelog wording plus current-code fix shape to reconstruct the likely missing property.

For every security-relevant fix entry, build a patch archaeology row:
- entry text and local source file (`CHANGELOG.md`, release note, commit subject, test name, or code comment);
- affected surface and function/opcode/API family;
- current-code behavior that appears to implement the fix;
- inferred pre-fix behavior;
- missing property before the fix;
- whether the mechanism is `current-live`, `fixed-by-current-head`, `regression-risk`, or `unclear`;
- what proof exists locally, and what proof is unavailable because history is shallow;
- whether current tests lock the fix.

Prioritize entries about:
- gas, fee, quota, profiler, telemetry, trace, simulation, or observer ordering;
- VM opcode semantics, system registers, panic/revert reasons, receipts, return values, and program counter behavior;
- contract/code/module/artifact load, copy, clear, zero-fill, storage fetch, and size accounting;
- host-width, `usize`, target architecture, wasm/no-std/std, allocation, and conversion behavior;
- consensus parameter validation, transaction validity, signature/predicate checks, storage persistence, and state-root/output finalization;
- changelog wording such as "fixed", "avoid conversion", "charge before", "charge for length", "max length", "profile before charging", "breaking because different errors", or "corrected".
- VM opcode entries where the patch names or implies contract/code load, code copy, clear/fill, compare, status registers, host width, panic/error behavior, profiler timing, or gas charge basis.
- entries where the current code contains a `max(...)`, precharge, precheck, status-register clearing write, or reordered conversion that looks like the fix shape.

Candidate rules:
- A patch-derived candidate is valid when the local patch trail plus current code reveal a concrete prior missing property, affected surface, and plausible impact. It may be labeled fixed if current `HEAD` contains the fix.
- Do not report fixed-by-current-head mechanisms as live exploits. Report them in a distinct "patch-derived fixed mechanism" or "regression risk" category.
- If the current code still has a related gap, split it into a live candidate and a fixed/historical candidate.
- Do not drop a patch-derived mechanism just because current validation proves the fix works. The fix is evidence of the prior missing property and a regression invariant.
- Do not overfit to one product's report titles. Generalize the mechanism: wrong charge basis, precharge expensive work, host-width result divergence, observer records post-state, status register not refreshed, or parser accepts before representability.
- A patch archaeology row with a concrete current fix shape and a concrete prior missing property should also appear in the `Candidate Findings` section with a candidate ID. Do not leave it only in the patch table.
- If a strong patch row is not promoted to a candidate, the rejected/downgraded entry must say exactly which proof element is missing: affected surface, inferred pre-fix behavior, current fix shape, sensitive sink, or security boundary.

Opcode-specific patch checks:
- For code copy/load/clear fixes, compare source bytes, requested bytes, fetched object bytes, destination bytes written, zero/default-fill bytes, and charged bytes. If current code charges a maximum across dimensions, infer what undercharged dimension the patch fixed and create a fixed/regression candidate when concrete.
- For host-width fixes, model the old conversion order and the 32-bit and 64-bit result/error classes. If both platforms fail differently and the result crosses VM output, receipts, gas, or consensus state, create a fixed/regression candidate.
- For profiler/observer fixes, compare fixed-cost and dependent-cost helpers on successful and failing paths. A fix that moves observation before charge is evidence of a prior post-state observer bug.
- For status-register fixes, verify the exact opcode helper, not only sibling helper families.

Required split candidates:
- If a host-width patch mentions changed 32-bit errors near a contract/code load opcode, create a dedicated load-opcode length-padding candidate. Do not merge it into a generic memory/index conversion dossier. The candidate must name the load opcode/helper, the requested length operand, the pre-fix narrowing/padding order, the semantic max-size check order, the narrow-host output/error class, the wide-host output/error class, and the consensus-visible receipt/result effect.
- If a profiler patch mentions profiling before or after gas charging, create a dedicated profiler/observer candidate even when the impact is Insight/diagnostic/regression-only. Do not reject it solely for lacking a consensus, authorization, or storage boundary. Severity can be low or informational, but the fixed missing property must survive when concrete.
- If both a generic host-width candidate and a load-opcode-specific host-width candidate exist, keep both or reject the generic one; do not let the generic one replace the opcode-specific one.

Validation questions:
1. What exact invariant did the patch entry claim to change?
2. Which current code line, helper, test, or assertion embodies the fix?
3. What would the pre-fix code have done if that line or check were absent or different?
4. Does the inferred pre-fix behavior cross a security boundary: fees, gas, consensus output, state, authorization, storage, receipts, or user-visible contract behavior?
5. Is the issue still live, fully fixed, partially fixed, or only a regression risk?
6. Is there a regression test? Does it check the full effect, or only a narrower example?
7. If history is unavailable, is the changelog wording specific enough to support a candidate, or should it remain an unclear patch note?
8. For a load-opcode host-width fix, what old error class did a narrow host produce before the semantic max-size check, and what old error class did a wide host produce after the semantic check? If the exact class names are unavailable, describe the class pair generically but keep the two rows separate.
9. For a profiler/observer fix, what value was observed before the patch, what value is observed now, and does a successful dependent charge as well as an out-of-gas dependent charge prove the timing difference?

Output expectations:
- Write a family scan with a patch archaeology table.
- Create candidates for strong patch-derived mechanisms, clearly marking current status.
- Promote every `fixed-by-current-head` patch row with concrete entry text, affected surface, current fix shape, and inferred missing property into a candidate dossier during canonicalization. If it is not promoted, record the exact proof gap.
- Promote concrete profiler/observer fixes as patch-derived regression risks even when their severity is only Insight/Informational. The final report can place them in a low-severity fixed-mechanisms section; it should not drop them solely because they are diagnostic.
- Promote concrete load-opcode host-width fixes as opcode-specific patch-derived candidates. A generic memory conversion candidate is not enough when the evidence points to a length-padding/max-size/error-class path.
- Record unclear or weak patch notes in rejected/downgraded ideas with the missing proof.
- Add validation priorities for any fixed mechanism whose regression test is absent or incomplete.
```
