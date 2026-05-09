# Code-Shape Card

## Metadata

- ID: `agave-2024-09-11-agave-transaction-processing-f0a77e94bf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `durable-nonce-consumption`

## Code Shape Summary

- A durable-nonce path checks transaction age and charges fees, then uses rollback account construction that can accidentally restore pre-advance nonce data for failed or fee-only transactions.

## Search Motifs

- durable nonce rollback account preserves old nonce data
- fee-only transaction with nonce account also acting as fee payer
- check transaction age fallback separates nonce check from nonce advance
- rollback combines fee lamports with stale nonce state

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Move nonce advancement into the fallback/fee-paying path and ensure rollback copies the already-advanced nonce data when reconstructing accounts.

## False Match Warnings

- Nonce advancement is persisted before any rollback state is captured.
- A later mandatory nonce-state check rejects reuse before execution.
- The changed code only alters tests or metrics without touching rollback state.
