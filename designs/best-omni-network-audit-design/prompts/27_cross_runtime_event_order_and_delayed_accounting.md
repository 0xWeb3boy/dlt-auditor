# Cross-Runtime Event Order And Delayed Accounting

## Family Objective

Find bugs in bridges, predeploys, VM/native adapters, event processors, and cross-domain accounting where source-side success is accepted before native-side validation, event order is changed before dependent delivery, uniqueness is checked too late, or mirrored balances become stale across asynchronous directions.

## Hunt Steps

1. Map each cross-runtime pipeline: source call, source-side value/accounting change, event emission, event extraction, local sorting or grouping, proposal inclusion, native delivery, downstream state mutation, failure handling, and recovery/retry.
2. Record full source event identity: source chain, emitter, block hash/number, transaction index, log index, event type, payload, and any dedup/progress key.
3. Compare source event order with delivery order. Search for sorting by address/topic/data, grouping by type, map iteration, or replay order that can reorder same-block dependent events.
4. Identify source-side checks and native-side checks. Any invariant enforced only at the delayed native sink can create stuck value, dropped authority changes, missed registry updates, or consensus/liveness problems after source-side success.
5. Search for unique identifiers accepted at source but reserved only at native delivery: public keys, validator IDs, operator IDs, nonces, withdrawals, claims, bridge transfer IDs, message offsets, and account names. Model front-running and duplicate identifiers.
6. For every failed native delivery path, determine whether source-side value is refunded, claimable, retried, recorded as failed, or silently lost.
7. Trace downstream consumers beyond the first native delivery function: validator-set construction, quorum calculation, bridge reserves, accounting mirrors, upgrade handlers, registry caches, relayers, monitors, and final reports.
8. For bridge balance mirrors and reserves, build a temporal ledger in both directions. Check whether delayed messages overwrite a mirror with stale state after the real balance changed, and whether later burns/withdrawals are authorized by that stale mirror.
9. Compare generated bindings and ABI conversions with contract events and native structs. Missing block number, log index, source address, or event-order fields can be security-relevant when used for replay or reconciliation.
10. For delayed native-side uniqueness checks, build a front-run matrix. For each identifier, ask whether an attacker can reserve the identifier with lower value, weaker authority, or different ownership before the honest source-side action is delivered to the native sink.
11. For every source-accepted field, trace all later semantic consumers. A field that is valid enough for first delivery may still fail when validator sets, signer derivation, registry caches, bridge backing, or accounting finalizers consume it later.
12. When bridge or reserve accounting is complex, split it out into the temporal mirror prompt and cross-reference the exact mirror variable, update mode, and consuming admission check.
13. For public keys and operator identities, do not treat length, address derivation, or allowlist checks as semantic ownership. Trace curve validation, duplicate public-key rejection, validator-set construction, signer recovery, decompression, and downstream quorum or slashing consumers.
14. Build a two-actor delayed-sink timeline for every front-run candidate: attacker source success, delayed sink reservation, victim source success, victim delayed sink rejection or downgrade, and recovery or refund status.
15. Distinguish self-loss from third-party griefing. A self-loss candidate needs strong protocol-wide impact; a two-actor griefing candidate can be valid when the victim cannot recover value, authority, identity, or expected participation.
16. For event ordering, check dependent flows beyond create-before-use. Include register-before-delegate, reserve-before-claim, deposit-before-withdraw, plan-before-cancel, grant-before-use, and key-before-signature consumers.
17. For public-key identity paths, split syntax, curve validity, source-side ownership, sink-side uniqueness, active-set use, and downstream signer/decompression consumers. Do not kill an issue after the first delivery function if a later deterministic consumer can reject or halt on the stored key.
18. For two-actor identity griefing, require less from actor A than actor B whenever the protocol permits it: lower value, weaker ownership proof, malformed-but-stored data, earlier source block, or a different source account. Then show how actor B's legitimate source-side action becomes unrecoverable, delayed, or downgraded at the sink.
19. For delayed sink failures, distinguish a logged or skipped failed message from a durable recovery mechanism. A failure record is not a recovery path unless a user or protocol process can use it to restore value, authority, or identity.

## Candidate Requirements

For every candidate, include:

- source-side entrypoint and value/accounting side effect;
- event identity and ordering key;
- delayed native sink and downstream consumers;
- invariant enforced too late or under a different representation;
- front-running, same-block, stale-mirror, or failure path;
- concrete loss, authority, accounting, liveness, or consensus consequence;
- test or trace that would confirm source success plus native failure/reorder/stale mirror.
- downstream consumer that finally makes the late validation security-relevant.
- identity-reservation or two-actor front-run matrix when the issue involves delayed uniqueness.
- public-key semantic validation matrix when an identity is later used for validator sets, signatures, rewards, slashing, or quorum accounting.

## False-Positive Controls

- Do not report failed delayed delivery as a vulnerability if the protocol explicitly commits a durable failure result and provides a recovery path.
- Do not report event reordering unless dependent events can occur in the same source block or replay batch.
- Do not report stale mirrors without showing a later authorization or accounting decision reads the stale value.
