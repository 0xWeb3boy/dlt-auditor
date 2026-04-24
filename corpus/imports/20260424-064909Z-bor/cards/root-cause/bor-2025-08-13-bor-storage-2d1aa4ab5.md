# Root-Cause Card

## Metadata

- ID: `bor-2025-08-13-bor-storage-2d1aa4ab5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-header-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus invariant enforcement`

## Violated Invariant

- Invariant: Persisted or peer-supplied state must be verified against its expected hash, path, or schema before being trusted by consensus or sync logic.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: integrity
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- Test/setup drift: the receipt-oriented test paths were using an import path that did not explicitly perform the header insertion step that later chain-state assertions rely on. The provided evidence does not establish a production security flaw.
