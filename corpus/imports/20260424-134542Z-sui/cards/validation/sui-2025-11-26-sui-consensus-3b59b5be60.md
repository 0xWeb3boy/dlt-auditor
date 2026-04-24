# Validation Card

## Metadata

- ID: `sui-2025-11-26-sui-consensus-3b59b5be60`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-accounting-hardening`

## What Confirmed The Issue

- Consensus commit finalizer now skips votes when retained ancestry is incomplete due to possible GC.
- Patch comment explicitly says the GC'ed block may have rejected pending transactions, so the current block cannot be assumed to accept them.
- The changed logic affects accept-vote aggregation for pending transactions in validator consensus finalization.
- A metric was added to observe blocks skipped by the new conservative vote-accounting path.

## What Could Have Invalidated It

- No proof that an attacker can cause or influence the GC state needed to trigger the issue.
- No demonstrated exploit, consensus fork, invalid finalization, or safety failure is shown.
- No security advisory, CVE, or explicit vulnerability language is provided.
- Protocol-config and metrics changes are ancillary and do not independently establish security impact.

## Severity Guidance

- Expected impact band: consensus-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Classify as hardening of consensus vote accounting, not a confirmed exploitable security fix.
- Do not claim remote exploitability or attacker-controlled GC from the supplied evidence.
- Do not claim a concrete liveness or safety failure beyond possible incorrect accept-vote aggregation.
- Do not rely on the ancillary feature-flag cleanup as security evidence.
