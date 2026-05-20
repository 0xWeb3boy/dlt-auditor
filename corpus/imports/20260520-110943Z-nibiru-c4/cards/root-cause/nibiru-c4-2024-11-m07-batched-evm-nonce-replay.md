# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m07-batched-evm-nonce-replay`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `batched-evm-nonce-regression`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `nonce monotonicity across batched messages`

## Violated Invariant

- Invariant: Every EVM message in a batch must leave the sender account sequence at least msg.Nonce()+1, regardless of contract creation vs call execution path.

## Trust Boundary

- Boundary: signed batched EVM transaction->account sequence state

## Attack Surface

- Entrypoint type: MsgEthereumTx execution in a Cosmos SDK tx
- Sensitive sink: stateDB account nonce commit after ApplyEvmMsg

## Impact Pattern

- Primary impact: nonce replay window
- Secondary impact: batched transaction sequence inconsistency

## Short Reusable Lesson

- ApplyEvmMsg manually set nonce for contract creation but delegated normal call nonce handling to evmObj.Call, which did not increment the sender nonce.
