# Root-Cause Card

## Metadata

- ID: `movement-2025-04-24-movement-cryptography-d16aa9e0d`
- Bug family: `authz_and_role_gates`
- Bug class: `transaction-validation-bypass`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `mandatory-baseline-transaction-prevalidation`

## Violated Invariant

- Invariant: Optional policy configuration such as a signer whitelist must not decide whether baseline transaction validation runs; validation of encoding and signatures must be mandatory on every ingestion path.

## Trust Boundary

- Boundary: Submitted DA light-node sequencer transactions crossing from external batch_write input into accepted sequencer batches.

## Attack Surface

- Entrypoint type: sequencer batch_write transaction ingestion
- Sensitive sink: acceptance of submitted transactions into the DA sequencer batch

## Impact Pattern

- Primary impact: Baseline validation bypass in no-whitelist sequencer configuration.
- Secondary impact: Potential acceptance of malformed or unsigned transaction data depending on validator responsibilities.

## Short Reusable Lesson

- Baseline Aptos transaction prevalidation was coupled to optional whitelist configuration. With no whitelist, the sequencer installed no prevalidator and batch_write could skip validation. The fix always constructs a validator and makes whitelist enforcement an optional mode inside it. Always instantiate and invoke the baseline transaction validator, use with_whitelist only to add optional sender policy, and accept only Prevalidated transactions while discarding validation errors.
