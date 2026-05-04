# Root-Cause Card

## Metadata

- ID: `stellar-core-2017-04-24-stellar-core-transaction-processing-00515f37c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-accounting-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `minted-versus-redistributed-value-separation`

## Violated Invariant

- Invariant: Aggregate supply counters must increase only by newly minted value, not by value redistributed from existing fee pools or payout mechanics.

## Trust Boundary

- Boundary: inflation-operation-execution -> ledger-header-monetary-aggregate

## Attack Surface

- Entrypoint type: protocol-state-transition
- Sensitive sink: total supply or totalCoins ledger accounting
- Attacker capability: Trigger or participate in protocol inflation distribution when eligible.
- Main precondition: The accounting path mixes newly minted inflation with existing fee-pool redistribution.

## Impact Pattern

- Primary impact: monetary-supply-integrity
- Secondary impact: ledger-accounting, consensus-determinism
- Severity guess: high because Supply accounting is consensus critical, though the finding does not prove attacker control or direct profit, so high but not critical.

## Short Reusable Lesson

- Consensus accounting should distinguish creation from redistribution; payout mechanics must not leak into monetary supply counters.
