# Root-Cause Card

## Metadata

- ID: `heimdall-v2-2025-05-08-heimdall-v2-transaction-processing-29c8c2e5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-continuity-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: exact checkpoint continuity validation.

## Violated Invariant

- Invariant: after a stored checkpoint ending at block N, the next accepted checkpoint must start at N+1 unless the protocol explicitly supports sparse ranges.

## Trust Boundary

- Boundary: submitted checkpoint message or side-transaction result crossing into checkpoint keeper state.

## Attack Surface

- Entrypoint type: checkpoint message handler and side-transaction post-handler.
- Sensitive sink: stored checkpoint sequence and checkpoint buffer.

## Impact Pattern

- Primary impact: checkpoint sequence integrity.
- Secondary impact: fail-closed handling of unreadable checkpoint buffer state.

## Short Reusable Lesson

- Range-based protocol state needs exact successor checks, not merely "not behind the tip" checks. Reject overlap and gaps at every admission path, and treat buffer read errors differently from valid absence.
