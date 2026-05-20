# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m07-batched-evm-nonce-replay`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `batched-evm-nonce-regression`

## Code Shape Summary

- ApplyEvmMsg manually set nonce for contract creation but delegated normal call nonce handling to evmObj.Call, which did not increment the sender nonce.

## Search Motifs

- contractCreation stateDB.SetNonce msg.Nonce
- evmObj.Call does not increment sender nonce
- multiple EVM messages in one Cosmos tx
- MsgEthereumTx nonce replay

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Set the sender nonce to msg.Nonce()+1 for both contract creation and non-creation EVM message paths, with batched-message regression tests.

## False Match Warnings

- No issue if batching MsgEthereumTx is impossible.
- No issue if normal calls set nonce to msg.Nonce()+1 after execution.
- No issue if ante and execution both enforce final monotonic sequence.
