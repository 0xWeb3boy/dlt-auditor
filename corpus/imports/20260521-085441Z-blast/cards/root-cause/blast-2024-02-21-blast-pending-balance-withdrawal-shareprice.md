# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-pending-balance-withdrawal-shareprice`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-provider-loss-checkpoint`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authoritative-provider-state-refresh`

## Violated Invariant

- Invariant: Withdrawal checkpoints should not price pending or claimable provider exits at par when their realized value is already knowable and below nominal.

## Trust Boundary

- Boundary: external yield provider state -> L1 withdrawal queue checkpoint

## Attack Surface

- Entrypoint type: YieldManager.finalize before Lido claim/report catches up
- Sensitive sink: WithdrawalQueue finalized checkpoint share price

## Impact Pattern

- Primary impact: insolvency-risk
- Secondary impact: value-transfer-between-cohorts

## Short Reusable Lesson

- Withdrawal checkpoints should not price pending or claimable provider exits at par when their realized value is already knowable and below nominal. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
