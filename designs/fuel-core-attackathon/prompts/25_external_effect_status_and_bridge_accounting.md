# Prompt Family: External Effect Status And Bridge Accounting

## Use This For

- Bridge messages, withdrawals, deposits, relayed transactions, and cross-domain proofs.
- Receipts, logs, outbox roots, event roots, or proof APIs that expose effects outside the local transaction.
- Asset accounting where message/data/payload shape changes query or spend semantics.
- Reverted, failed, skipped, simulated, dry-run, retryable, and partially applied execution paths.

## Prompt

```text
Hunt for bugs where an externally visible effect is committed, proven, indexed, or relayed under a different success/status/accounting rule than the state transition that should authorize it.

Focus on:
- emitted receipts, logs, events, outbox roots, inbox roots, message queues, withdrawal queues, bridge proofs, and API proof material
- transaction success, failure, revert, skipped, dry-run, validation, import, replay, rollback, and retryable states
- deposits, withdrawals, messages, forced transactions, portal events, burn/mint flows, and cross-domain asset movements
- balance, coin, UTXO, message, and SDK/query projections of imported bridge assets
- non-empty message payloads that still carry native/base-asset value
- transaction-builder and validity distinctions between message-coin inputs and message-data inputs

Search patterns:
- output messages, withdrawal receipts, event roots, or proof leaves collected before final transaction status is known
- failed or reverted executions whose externally consumed receipts remain in a block, proof tree, event root, bridge queue, or public API response
- state rollback that reverts local burn/mint/accounting but leaves an external-domain message, proof, or relayable commitment
- proof APIs that allow a client or relayer to prove an effect from a failed, reverted, skipped, or otherwise non-successful transaction
- transaction-status filters in public APIs that disagree with the on-chain root or stored proof material
- imported messages or deposits where payload/data changes whether the asset is indexed as spendable balance, coin, message coin, or message data
- query/indexer filters that treat "empty payload" as the definition of asset value, spendability, or coin-ness
- transaction builders or validators that classify the same imported asset differently based on payload shape
- code paths named like `messages_iter`, `owned_messages`, `message_coin`, `message_data`, `MessageDataSigned`, `MessageCoinSigned`, `message_data_signed`, `message_coin_signed`, `NoSpendableInput`, `spendable`, `coins_to_spend`, `coinsToSpend`, `balance`, or `AssetQuery`
- filters such as `message.data().is_empty()` or `data.is_empty()` that decide whether a value-bearing message is counted as a coin or spendable base-asset balance
- a deposit/portal message event carrying both nonzero amount and non-empty data that is imported into state but excluded from balance, coin selection, or spendable input checks
- SDK/client builder behavior where a non-empty payload selects a message-data input variant even though the message amount is nonzero
- live execution vs dry-run vs validation/import paths where one path emits an external effect and another path suppresses local state
- message/retryable semantics where non-retryable asset movement and retryable data execution share one representation
- burn-before-send or send-before-burn orderings where one side can be rolled back independently
- receipt/log/event emission from nested calls where parent failure status does not clearly suppress external commitments

Questions to answer:
1. What exact local state change authorizes the external effect?
2. Is the external effect collected before or after the success/failure/revert status is final?
3. If execution reverts, which receipts, logs, roots, messages, and proofs remain observable?
4. Can a bridge relayer, client, or proof API consume an effect whose authorizing state change was reverted or never committed?
5. Does balance/query/indexing count every asset-bearing representation, including data-carrying messages or non-empty payloads?
6. Does transaction validation treat every asset-bearing imported message as spendable when the protocol says value is present?
7. Are proof/status APIs using the same success predicate as the external bridge or verifier?
8. Is the behavior consistent across live production, block import, replay, rollback, dry-run, and failed execution variants?
9. If a message has both `amount > 0` and `data` non-empty, which APIs count it as base-asset balance, which APIs return it as a coin, and which transaction input variant spends it?
10. Does the "message has data" representation lose or hide the asset amount from balance, coin selection, or `NoSpendableInput` checks?

Candidate retention rules:
- Keep value-bearing data-message accounting candidates separate from generic "large message data" resource candidates.
- Keep the candidate when the amount is imported and stored but public balance/coin APIs filter it out based on non-empty data, even if the same message remains visible through a generic messages API.
- Keep the candidate when transaction builders or validators treat `MessageData*` inputs as non-spendable despite the message carrying base-asset value.
- Reject only if an authoritative finalizer proves all non-empty-data value messages are intentionally non-spendable and cannot carry withdrawable/transferable base-asset value.

Severity guidance:
- Medium by default for external-effect/status mismatches with realistic availability or accounting impact.
- Raise when a bridge, withdrawal, deposit, or proof path can create unbacked external claims or lock/lose funds.
```
