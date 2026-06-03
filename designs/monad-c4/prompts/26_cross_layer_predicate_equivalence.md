# Prompt Family: Cross-Layer Predicate Equivalence

## Use This For

- Objects validated by multiple layers: RPC, mempool, peer forwarding, proposal building, block validation, execution, replay, simulation, archive import, and sync recovery.
- Differences in predicate order, special-case handling, feature gates, type-specific rules, and failure disposition.
- "Accepted here, rejected later" bugs that cause liveness, resource exhaustion, free spam, or canonical-state disagreement.

## Prompt

```text
Hunt for cross-layer predicate-equivalence bugs in a blockchain or DLT codebase.

For each externally supplied object, build an equivalence matrix of every path that accepts, forwards, queues, proposes, validates, executes, simulates, stores, replays, or serves it. The goal is not that every layer performs every check, but that earlier acceptance cannot create exploitable work that a later authoritative layer rejects or interprets differently.

Prioritize objects with multiple variants or special cases:
- legacy and typed transactions
- delegated, sponsored, authorized, system, privileged, blob, sidecar, or proof-bearing transactions
- blocks, headers, payload attributes, receipts, withdrawals, logs, votes, certificates, peer messages, snapshots, and state-sync chunks
- simulation/debug/raw API objects that manually reconstruct canonical objects

Search patterns:
- the same predicate exists in two layers but runs in a different order, and the first failing predicate changes whether the whole object is rejected or only a sub-object is ignored
- one layer treats a malformed child object as non-fatal while another treats it as fatal to the parent object
- type-specific branches collapse into a generic helper in one layer but remain distinct in execution
- front-door admission checks a lower bound, cheaper fee, smaller size, or weaker signature domain than proposal or execution
- block or batch prepasses compute a global summary before ordered execution, while an earlier item should not see later side effects
- simulation, trace, estimate, debug, replay, or raw import uses hand-rolled parsing or default fields instead of the canonical validator
- forwarding or gossip accepts an object based on transport/authentication checks but does not preserve the identity needed by the consumer
- failure at a later layer leaves the object in a queue, hot pool, retry set, pending map, or replacement cache where it will be selected again
- feature/fork checks are performed against different coordinates or chain variants across layers
- duplicate field representations are compared in one path but trusted independently in another
- special sender, system account, delegated authority, sponsored fee payer, or authorization child checks where chain id, signature recovery, nonce, special-address, code-state, and feature-gate predicates run in different orders. Record whether each failing predicate rejects only the child, rejects the parent transaction, rejects the whole block, or silently skips side effects.
- fee affordability predicates where one layer checks base fee, another checks full effective bid, another checks legacy gas price, and another checks reserve/emptying rules. Include what happens to the object after failure: evict, pending, tracked, retry, vote rejection, execution rejection, or kept hot.
- EIP-7702 wrong-chain child plus system/special authority: compare txpool, block validator, block policy, and execution ordering. A wrong-chain child may be skipped by one layer before the system-authority check, while another layer may treat system authority as fatal before reaching chain-id skip.
- EIP-7702 delegated-status timing: compare txpool proposal's ordered mutation of authority `is_delegated` with block policy's whole-block recovered-authority prepass. A later authorization must not reclassify an earlier transaction unless txpool used the same ordering.
- Legacy transaction fee semantics: compare helper formulas for effective gas bid against execution's type-specific gas charge. Do not collapse legacy and EIP-1559 transactions into one formula without proving execution does the same.
- outer-authenticated peer messages that contain inner role, validator, or group claims. Compare router, primary, secondary, and final state mutation layers; ensure the outer recovered author survives to the final predicate.
- raw/debug/RPC output encoders that expose typed protocol objects. Compare internal root/hash serialization, storage serialization, RPC object serialization, and raw-byte API serialization with an external standard decoder.

Required matrix:
- Object type and variant.
- Ingress/admission path.
- Forwarding/gossip path.
- Queue or pool retention and replacement path.
- Proposal/build path.
- Receiver/block validation path.
- Execution/state-transition path.
- Replay/recovery/sync path.
- Simulation/debug/RPC path, if present.
- Predicate differences, order differences, type-specific differences, and failure disposition.

Questions to answer:
1. Which layer is authoritative for each property: signature, signer/sender, fee, balance, nonce, chain id, special account, size, gas, fork field, side effect, and wire encoding?
2. Does an earlier layer accept any object or child object that a later layer rejects as fatal?
3. If later rejection occurs, is the object evicted, charged, penalized, quarantined, or can it be selected again?
4. Are type-specific semantics preserved for every transaction/message/header variant?
5. Are predicates merely present, or do they run in an order that preserves the same parent/child validity result?
6. Do global summaries and precomputed side-effect sets respect ordered execution and final validity filters?
7. Can a producer-supplied field reach execution even though consensus checked only a defaulted or separately represented field?
8. For every invalid child object, does each layer agree whether the parent transaction, message, or block remains valid?
9. Does each failed pool/proposal predicate remove work from the hot path, or can the same object be selected repeatedly?
10. For EIP-7702 child authorizations, does every layer agree whether a wrong-chain system-authority child makes the child ignored, the parent transaction invalid, or the whole block invalid?
11. For transaction affordability, does every layer use the same cost formula for legacy versus typed transactions and for insert/forward/proposal/block validation?
12. For delegated-status/reserve checks, does an earlier transaction's classification depend on a later transaction's authorization in any layer but not another?

High-signal evidence:
- A malformed child is ignored by admission but makes the parent invalid during block validation.
- A transaction passes pool admission because a cheaper affordability formula is used, then repeatedly fails proposal/execution while staying hot.
- A special sender, delegated authority, sponsor, or system account check can be short-circuited differently across layers.
- A global signer/authority/reserve summary gives earlier operations access to side effects from later operations.
- Simulation or debug output uses a different typed encoding or field default than canonical execution/RPC standards.
- A router validates a packet signature, drops the recovered signer, and a downstream state machine trusts an inner validator or group id.
- A raw receipt or transaction API emits bytes that internal tests accept but standard clients reject.
- Txpool admits an EIP-7702 parent because a wrong-chain child is skipped before checking system authority, while block validation rejects because system authority is fatal before chain-id skip.
- Txpool admission or forwarding accepts transactions funded only for base fee, while proposal/block policy rejects them at full bid and leaves them tracked for repeated selection.
- A block-policy whole-block prepass marks an authority delegated before checking an earlier transaction, while txpool proposal would have checked that earlier transaction before including the later authorization.

False-positive filters:
- Do not report deliberate layered validation when the earlier layer only performs cheap prechecks and later rejection cannot cause retained work, repeated selection, voting, free spam, or user-visible compatibility failure.
- Do not report a missing early check if the object is immediately revalidated by the canonical sink before any expensive work, queue retention, or consensus action.
- Do not report harmless predicate reordering when all failing predicates produce the same parent validity result and cleanup behavior.

Severity guidance:
- High if an accepted object can make valid-looking blocks invalid, halt consensus/execution, bypass fees, or corrupt canonical state.
- Medium if it causes realistic node DoS, persistent pool starvation, repeated expensive work, or externally visible incompatibility.
- Low for defense-in-depth differences without attacker control or meaningful retained work.
```
