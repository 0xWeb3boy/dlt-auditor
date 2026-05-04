# Root-Cause Card

## Metadata

- ID: `snarkos-2025-03-11-snarkos-core-logic-27575e79c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integer-overflow-in-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `overflow-safe-bounds-check`

## Violated Invariant

- Invariant: Validation arithmetic over untrusted protocol heights must use checked arithmetic and preserve the intended ordering invariant at numeric boundaries.

## Trust Boundary

- Boundary: `peer/validator->sync-locator-validator`

## Attack Surface

- Entrypoint type: `query-verification-path`
- Sensitive sink: block locator validation decision
- Attacker capability: supply block locator heights or checkpoints; choose extreme height values near integer bounds.
- Preconditions: locator validation performs arithmetic on untrusted heights; overflow can alter validation result or panic behavior.

## Impact Pattern

- Primary impact: malformed locator passes/fails incorrectly.
- Secondary impact: arithmetic panic or sync disruption hardening.
- Severity guide: `medium` for `validation-hardening` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Validation arithmetic over untrusted protocol heights must use checked arithmetic and preserve the intended ordering invariant at numeric boundaries. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The supported finding is overflow-safe input validation hardening in snarkOS block locator checks. The evidence does not support the heuristic baseline's access-control theory, nor does it prove a concrete exploit, consensus split, or state corruption impact. 1. In `node/sync/locators/src/block_locators.rs`, the patch replaces `// That is, 'last_checkpoint_height + CHECKPOINT_INTERVAL'` with `// That is, we must have`. The changed code sits primarily in `node/sync/locators/src`, `node/sync/locators`, which anchors the finding in the `core-logic` area of the project. Historical context from `node/sync/locators/src/lib.rs`, `node/sync/locators/LICENSE.md` was reviewed at the same commit to und
