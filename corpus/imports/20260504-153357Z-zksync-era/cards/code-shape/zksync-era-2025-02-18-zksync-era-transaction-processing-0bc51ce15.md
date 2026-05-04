# Code-Shape Card

## Metadata

- ID: `zksync-era-2025-02-18-zksync-era-transaction-processing-0bc51ce15`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `migration-state-guard`

## Code Shape Summary

- The patch changes gateway migration handling in EthWatch and EthTxAggregator. EthWatch now refreshes gateway_status and routes EventsSource::SL through L1 or settlement-layer clients depending on migration state. EthTxAggregator now reads gateway migration state and blocks commit aggregation while GatewayMigrationState::Started. This may be security relevant because it affects a protocol transition path, but the provided evidence does not prove an exploitable vulnerability, consensus failure, invalid commit, fund loss, or cryptographic bypass.

## Search Motifs

- Motif 1: Background loop uses cached migration or fork state for state-advancing decisions.
- Motif 2: Event routing chooses between L1 and settlement-layer clients during a transition.
- Motif 3: Patch blocks commits or aggregation while migration state is `Started`.

## Typical Asymmetry

- Event readers and senders may observe different migration phases unless transition state is refreshed and enforced at each sensitive operation.

## Patch Pattern

- Refresh migration state close to use, route event sources by phase, and gate state-advancing operations during the active migration window.

## False Match Warnings

- State flags that affect only metrics/logging, idempotent operations, or paths already gated elsewhere should not be overclassified.
