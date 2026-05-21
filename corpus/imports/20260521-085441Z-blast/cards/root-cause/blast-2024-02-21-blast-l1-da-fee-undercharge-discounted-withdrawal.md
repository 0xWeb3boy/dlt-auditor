# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-l1-da-fee-undercharge-discounted-withdrawal`
- Bug family: `resource_accounting_and_limits`
- Bug class: `fee-recovery-discount-mismatch`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `request-response-cost-symmetry`

## Violated Invariant

- Invariant: Fees charged to recover L1 data availability costs should settle to the L1 fee recipient at the nominal amount unless a discount policy is explicit.

## Trust Boundary

- Boundary: L2 L1/DA fee accounting -> L1 fee recipient withdrawal

## Attack Surface

- Entrypoint type: L1FeeVault withdrawal during negative yield
- Sensitive sink: remote fee-vault payout through discounted withdrawal path

## Impact Pattern

- Primary impact: fee-bypass
- Secondary impact: protocol-cost-underrecovery

## Short Reusable Lesson

- Fees charged to recover L1 data availability costs should settle to the L1 fee recipient at the nominal amount unless a discount policy is explicit. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
