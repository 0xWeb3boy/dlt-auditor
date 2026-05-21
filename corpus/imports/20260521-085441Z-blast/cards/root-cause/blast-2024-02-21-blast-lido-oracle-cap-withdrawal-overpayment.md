# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-lido-oracle-cap-withdrawal-overpayment`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `external-oracle-loss-lag`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `loss-freshness-before-withdrawal`

## Violated Invariant

- Invariant: External provider losses that are known or pending must be reflected before withdrawal checkpoints can pay exiting users at par.

## Trust Boundary

- Boundary: Lido oracle/provider truth -> Blast withdrawal settlement

## Attack Surface

- Entrypoint type: YieldManager.finalize during oracle-cap or delayed-loss window
- Sensitive sink: withdrawal checkpoint share price and payout amount

## Impact Pattern

- Primary impact: insolvency-risk
- Secondary impact: value-transfer-between-cohorts

## Short Reusable Lesson

- External provider losses that are known or pending must be reflected before withdrawal checkpoints can pay exiting users at par. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
