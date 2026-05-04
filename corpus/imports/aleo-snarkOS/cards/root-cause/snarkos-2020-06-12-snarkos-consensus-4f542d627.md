# Root-Cause Card

## Metadata

- ID: `snarkos-2020-06-12-snarkos-consensus-4f542d627`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-difficulty-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-derived-field-validation`

## Violated Invariant

- Invariant: Consensus verifiers must recompute rule-derived header fields and reject headers whose supplied values do not match local consensus calculation.

## Trust Boundary

- Boundary: `block-producer/peer->consensus-verifier`

## Attack Surface

- Entrypoint type: `block-header-validation`
- Sensitive sink: block validity and fork-choice eligibility
- Attacker capability: produce or relay a block header; set header difficulty_target independently of consensus rules.
- Preconditions: verifier accepts peer/miner supplied headers; difficulty target is part of block validity.

## Impact Pattern

- Primary impact: invalid header acceptance.
- Secondary impact: fork-choice or work accounting distortion.
- Severity guide: `high` for `consensus-integrity` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Consensus verifiers must recompute rule-derived header fields and reject headers whose supplied values do not match local consensus calculation. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch is likely a consensus security fix for missing difficulty-target validation in block header verification. The supplied evidence supports that `verify_header` now computes an expected difficulty, adds a `DifficultyMismatch` error, and adds a regression test requiring rejection when `difficulty_target` is changed to the expected value plus one. 1. In `consensus/src/consensus.rs`, the patch adds `// expected difficulty did not match the difficulty target`. 2. In `consensus/src/consensus.rs`, the patch replaces `let future_timelimit: i64 = Utc::now().timestamp() as i64 + TWO_HOURS_UNIX;` with `let now = Utc::now().timestamp();`. 3. In `errors/src/consensus/consensus.rs`, the patch adds
