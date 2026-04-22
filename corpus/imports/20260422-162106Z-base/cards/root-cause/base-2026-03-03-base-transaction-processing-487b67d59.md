# Root-Cause Card

## Metadata

- ID: `base-2026-03-03-base-transaction-processing-487b67d59`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: When derivation loads blobs for a block, the fetched and validated blob set should match what the batch data actually consumes exactly; leftover validated blobs should be rejected rather than silently ignored.

## Trust Boundary

- Boundary: `transaction, batch, or proof input->execution or derivation pipeline`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `security-sensitive execution or state transition`

## Impact Pattern

- Primary impact: `correctness-or-hardening`
- Secondary impact: `none`

## Short Reusable Lesson

- When derivation loads blobs for a block, the fetched and validated blob set should match what the batch data actually consumes exactly; leftover validated blobs should be rejected rather than silently ignored. The shown pre-fix code tracked consumed blob count with `blob_index` but lacked a final exact-consumption validation, so a mismatch between consumed blobs and fetched blobs was tolerated instead of being surfaced as an error. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
