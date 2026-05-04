# Validation Card

## Metadata

- ID: `zksync-era-2025-02-18-zksync-era-transaction-processing-0bc51ce15`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `migration-state-guard`

## What Confirmed The Issue

- Evidence 1: EthTxAggregator reads gateway migration state before aggregation decisions and restricts commits while migration is Started.
- Evidence 2: EthWatch refreshes gateway status and routes settlement-layer events according to migration state.

## What Could Have Invalidated It

- Compensating control 1: Another state-machine guard already blocks commits and wrong-layer event reads during migration.
- Compensating control 2: The affected operation is idempotent and safe regardless of migration phase.

## Severity Guidance

- Expected impact band: protocol-transition-hardening
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Do not claim fund loss or invalid commits without a concrete pre-patch execution trace.
- Caution 2: Migration-state cleanup is only security-relevant when it gates protocol-sensitive operations.
