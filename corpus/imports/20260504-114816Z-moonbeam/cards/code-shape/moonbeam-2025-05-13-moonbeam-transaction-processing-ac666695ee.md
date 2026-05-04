# Code-Shape Card

## Metadata

- ID: `moonbeam-2025-05-13-moonbeam-transaction-processing-ac666695ee`
- Bug family: `resource_accounting_and_limits`
- Bug class: `evm-resource-accounting-and-reentrancy-hardening`

## Code Shape Summary

- Runtime API paths hand-rolled transaction length/proof-size estimates. The patch constructs pallet_ethereum::TransactionData and enables forbid-evm-reentrancy.

## Search Motifs

- manual estimated_transaction_len arithmetic in EVM API
- proof_size_base_cost computed outside owning pallet type
- forbid-evm-reentrancy feature added with accounting refactor

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Replace duplicated local size accounting with canonical pallet transaction data and enable the pallet-provided reentrancy guard feature.

## False Match Warnings

- Manual estimation may be safe if covered by exact tests against canonical encoding
- RPC simulation-only undercharging may not affect block production
- Feature enabling alone is not proof of a prior reentrancy exploit
