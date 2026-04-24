# geth-arb Prompt-Pack Refinement Proposal

Target repo: `/testing/go-ethereum`

Evidence folder: `/testing/go-ethereum/validated-findings/kept`

Corpus bundle referenced: `/testing/dlt-ai-audit-system/corpus/imports/20260424-114423Z-geth-arb`

Current prompt pack: `/testing/dlt-ai-audit-system`

Date: 2026-04-24

## Repo Context Summary

This checkout is a Go Ethereum execution-client codebase with Arbitrum/Nitro extensions mixed into the same tree. It contains the normal geth surfaces: block import and EVM execution in `core/`, state and trie persistence in `core/state`, `trie`, and `triedb`, transaction pool admission in `core/txpool`, peer sync and gossip in `eth/`, discovery and sessions in `p2p/`, RPC/API entrypoints in `internal/ethapi`, and signing/key-management surfaces in `accounts/` and `signer/`.

It also contains Arbitrum-specific execution and sequencing surfaces: `arbitrum/`, `arbitrum_types/`, `arbcrypto/`, Arbitrum transaction types in `core/types/arb_types.go`, multi-dimensional gas in `arbitrum/multigas`, Stylus/Wasm activation state in `core/state/statedb_arbitrum.go`, and delayed/generated transaction behavior in `core/state_transition.go`.

Important trust boundaries:

- Remote peers to downloader queues, block/header/body/receipt sync, tx announcements, discovery ping/pong, peer table mutation, and peer-quality feedback.
- RPC clients to transaction submission, fee-history queries, signing APIs, account access, debug/simulation paths, and external signer integration.
- Consensus layer, peer block import, or sequencer-produced data to header verification, block body commitment checks, state transition, fork-choice, and canonical chain selection.
- Transaction inputs to gas accounting, value transfer, blobpool/txpool admission, replay protection, SetCode/Blob transaction validation, and generated Arbitrum side effects.
- Operator configuration, runtime artifacts, module roots, Docker images, and validator configuration to validator/sequencer behavior.
- Cached or persisted validator progress, state journals, Wasm activation maps, and delayed-message accumulators to later validation or sequencing.
- Remote advisory feeds, signed messages, broadcast feeds, and chain IDs to signing, warning, and authenticated-message decisions.

High-risk entrypoint categories:

- `core.BlockChain.InsertChain` and the internal block import path, including linked-chain prechecks and engine header verification.
- EVM state transition and Arbitrum transaction execution in `core/state_transition.go`.
- `core/txpool/validation.go`, `core/txpool/blobpool`, and tx fetch scheduling in `eth/fetcher/tx_fetcher.go`.
- Downloader queues and peer response handling in `eth/downloader`.
- Discovery and request/reply correlation in `p2p/discover`.
- RPC transaction and fee APIs in `internal/ethapi` and `eth/gasprice`.
- Signing and contract binding helpers in `accounts`, `accounts/abi/bind`, and `signer/core`.
- State journaling, storage deletion, activation, and commit paths in `core/state`.
- Arbitrum validator, sequencer, module-root, delayed-message, and express-lane style paths.

State-machine and lifecycle patterns that matter:

- Block import is a staged state machine: syntactic ordering, header verification, body/receipt execution, state commitment, reorg, head update, and event emission.
- Peer sync is long-lived and progress-sensitive: responses must be bound to request tokens, parent/predecessor context, queue reservations, and peer-quality feedback.
- The txpool/blobpool has multiple admission gates: type/fork support, blob sidecars, max blob count, delegated sender state, account resources, and per-peer fetch scheduling.
- EVM and Arbitrum execution carry nested resource state: gas, multi-dimensional gas, scheduled transactions, retryables, Wasm activation, and state journal entries must remain synchronized across helper boundaries.
- Several findings come from chain-variant overlays: base Ethereum invariants and Arbitrum-specific invariants share code but have different authority sources, artifacts, fees, delayed-message state, and sequencing policy.

## Finding Inventory

Analyzed all 38 files in `/testing/go-ethereum/validated-findings/kept`:

`2014-11-12-go-ethereum-transaction-processing-60cdb1148c.md`, `2015-01-13-go-ethereum-transaction-processing-82beaabf6a.md`, `2015-03-25-go-ethereum-cryptography-de7af720d6.md`, `2015-05-14-go-ethereum-transaction-processing-a4246c2da6.md`, `2015-05-15-go-ethereum-core-logic-5c1a7b965c.md`, `2015-05-15-go-ethereum-core-logic-cd2fb09051.md`, `2015-05-21-go-ethereum-core-logic-52db6d8be5.md`, `2015-07-01-go-ethereum-p2p-networking-d6f2c0a76f.md`, `2016-10-28-go-ethereum-transaction-processing-b59c8399fb.md`, `2016-11-24-go-ethereum-storage-12d654a6fc.md`, `2017-02-13-go-ethereum-storage-e23e86921b.md`, `2017-05-12-go-ethereum-transaction-processing-a5f6a1cb7c.md`, `2017-06-22-go-ethereum-storage-0042f13d47.md`, `2017-08-25-go-ethereum-storage-08f27428b4.md`, `2018-02-12-go-ethereum-p2p-networking-9123eceb0f.md`, `2018-09-20-go-ethereum-storage-d6254f827b.md`, `2018-09-25-go-ethereum-cryptography-d3441ebb56.md`, `2020-12-04-go-ethereum-transaction-processing-15339cf1c9.md`, `2020-12-08-go-ethereum-transaction-processing-ed0670cb17.md`, `2021-02-23-go-ethereum-transaction-processing-142fbcfd6f.md`, `2021-07-22-go-ethereum-transaction-processing-97aacd9b35.md`, `2022-01-26-go-ethereum-transaction-processing-b5048b881e.md`, `2022-03-17-go-ethereum-storage-368fbe57cb.md`, `2022-03-17-go-ethereum-transaction-processing-c4a31f0842.md`, `2022-04-10-go-ethereum-transaction-processing-3a9ee37539.md`, `2022-04-17-go-ethereum-transaction-processing-f990e534ab.md`, `2022-06-01-go-ethereum-transaction-processing-37c04d56b5.md`, `2022-06-29-go-ethereum-cryptography-d12b1a91cd.md`, `2022-09-07-go-ethereum-transaction-processing-4f32fd7c77.md`, `2022-12-20-go-ethereum-transaction-processing-b818e73ef3.md`, `2023-10-13-go-ethereum-storage-f88557d061.md`, `2024-04-07-go-ethereum-transaction-processing-ac07554f71.md`, `2024-05-07-go-ethereum-transaction-processing-e4b8058d5a.md`, `2024-12-20-go-ethereum-transaction-processing-a719c5c923.md`, `2025-04-08-go-ethereum-transaction-processing-2e739fce58.md`, `2025-05-22-go-ethereum-transaction-processing-20ad4f500e.md`, `2025-12-11-go-ethereum-transaction-processing-56d201b0fe.md`, `2026-03-11-go-ethereum-transaction-processing-8fe83188ce.md`.

No findings were intentionally skipped.

## Finding-To-Mechanism Analysis

| Finding | Repo-specific failure mechanism | Generic invariant and missing property | Hunt recipe | False-positive killers |
| --- | --- | --- | --- | --- |
| `60cdb1148c` | Block processing had transaction commitment validation present but disabled. | Block bodies must match the header commitment before execution; missing `block-body-commitment-integrity`. | Compare every block import path for body/root recomputation before execution. | A mandatory canonical validator recomputes tx root before any state transition. |
| `82beaabf6a` | Consensus-sensitive contract-creation gas error and uncle ancestor depth handling were corrected. | All nodes must apply identical gas, error, and ancestry rules; missing `consensus-rule-consistency`. | Search consensus edge cases where nested errors or boundary constants differ across execution paths. | Exact edge case is debug-only or another consensus layer enforces the same rule before state commit. |
| `de7af720d6` | Discovery `findnode` could trigger larger neighbor responses before reachability/bonding. | Small spoofable requests must not cause amplified responses; missing `request-response-cost-symmetry`. | Inspect UDP request handlers for response size asymmetry before source validation. | Reachability token or bonding check gates all larger responses and table mutations. |
| `a4246c2da6` | Downloader could conflate no ready block with unknown parent. | Sync progress must distinguish benign emptiness from invalid parentage; missing `parent-availability-progress-check`. | Search queue APIs returning nil/empty for both no work and invalid lineage. | Caller separately checks parent existence and penalizes or aborts on unknown parent. |
| `5c1a7b965c` | Peer downloader cross-check cleared based only on returned block hash. | A response must match the expected parent/context tuple; missing `peer-response-parent-binding`. | Trace pending validation records and ask what exact request context clears them. | Pending check stores and compares the full expected parent/hash/height tuple. |
| `cd2fb09051` | Hash response replay could contribute zero new hashes without being rejected. | Peer batches must make progress or be treated as invalid/no-progress; missing `duplicate-response-deduplication`. | Search queue insertion results that ignore the count of actually new items. | Zero-new batches are final, explicitly harmless, or still feed peer-quality penalties. |
| `52db6d8be5` | Downloader accepted a parent hash because it existed somewhere in the queue. | Cross-checks must bind to the expected predecessor, not broad membership; missing `queued-parent-cross-check-binding`. | Hunt for membership checks where exact predecessor or request context is required. | A later import validates the exact predecessor before any progress or trust update. |
| `d6f2c0a76f` | Downloader hash loop continued requesting after batches without bounding forward progress. | Peer-driven loops need request-bounded progress and stop conditions; missing `request-bounded-resource-use`. | Search recursive/looping peer requests that continue after empty, duplicate, or already-known results. | Strong per-peer limits, progress checks, and penalties bound the loop. |
| `b59c8399fb` | `eth_sign` semantics were domain-separated from transaction signing. | General signing APIs must domain-separate arbitrary messages; missing `signature-domain-separation`. | Compare raw signing helpers against typed transaction signing and prefix/hash rules. | API only signs typed protocol objects or includes explicit domain, chain, and purpose in signed bytes. |
| `12d654a6fc` | Touched-account state was not journaled consistently around empty account semantics. | Consensus-visible state touches must journal and revert symmetrically; missing `state-transition-journal-consistency`. | Inspect transient flags and journal entries that affect deletion, emptiness, or trie commitment. | Touch flags are recomputed from canonical state before commit or do not affect roots. |
| `e23e86921b` | Swarm chunk store request needed key/content hash comparison. | Content-addressed data must hash to the requested key before storage; missing `content-address-integrity`. | Search content-addressed stores for claimed key accepted without recomputing payload hash. | Consumer or store recomputes and rejects mismatches before persistence or forwarding. |
| `a5f6a1cb7c` | Chain config compatibility omitted a fork activation field. | Fork configuration must cover every active fork boundary; missing `fork-config-compatibility`. | Compare chain-config compatibility checks against all fork fields used by rule selection. | Omitted fork is not active in persisted history or is checked in a shared compatibility helper. |
| `0042f13d47` | State sync queue/timeouts/dedup were hardened. | Sync state delivery needs request identity, deduplication, and timeouts; missing `sync-request-deduplication-and-timeout`. | Compare state sync with header/body sync for stale delivery and duplicate response handling. | Duplicate or stale deliveries cannot allocate, retry, or change queue state. |
| `08f27428b4` | EVM CREATE needed occupied-account collision check. | Contract creation must reject occupied destinations; missing `account-creation-collision-check`. | Search create/bind/register operations where uniqueness is inferred indirectly. | Canonical account nonce/code existence is checked at the creation sink. |
| `9123eceb0f` | Discovery pong accepted based on peer identity rather than reply token. | Replies must correlate to exact challenge/request token; missing `request-reply-correlation`. | Inspect ping/pong callbacks for peer-only matching instead of nonce/hash matching. | Reply token is verified before liveness, bonding, or request completion. |
| `d6254f827b` | Equal-total-difficulty fork choice used random reorg tie-breaking. | Fork-choice tie breaks should be deterministic and policy-correct; missing `deterministic-fork-choice`. | Search equal-score/equal-height selection that uses randomness or local heuristics. | Consensus or policy explicitly defines and tests the tie-break behavior. |
| `d3441ebb56` | Clef signer policy warnings were made fail-closed by default. | Signing policy failures should stop before key use; missing `signing-policy-fail-closed`. | Search signing middleware where warnings, validation errors, or UI prompts continue by default. | A separate mandatory policy engine denies before the signature sink. |
| `15339cf1c9` | Version/advisory feed added signed feed validation. | Security advisory feeds must be authenticated before operator trust decisions; missing `advisory-feed-authenticity`. | Search remote security metadata consumers that trust transport or URL rather than publisher signatures. | Feed is advisory-only and verified by a pinned signature or offline trusted channel. |
| `ed0670cb17` | Contract binding helpers exposed chain-ID-aware signing paths. | Transaction helper APIs should bind chain ID by default; missing `chain-id-replay-protection`. | Search convenience signing constructors with unsafe legacy defaults. | Unsafe helper is deprecated, unavailable by default, or guarded by explicit chain ID requirement. |
| `142fbcfd6f` | RPC submission rejects unprotected transactions unless explicitly allowed. | Public submission must enforce replay protection before txpool/broadcast; missing `chain-id-replay-protection`. | Compare raw RPC submit, wallet, contract binding, and direct txpool admission paths. | Operator override is explicit and default is fail-closed. |
| `97aacd9b35` | EIP-1559 balance precheck omitted transferred value. | Affordability checks must include fee liability and transferred value; missing `fee-and-value-balance-precheck`. | Build before/after accounting for transaction-type-specific balance formulas. | Execution rechecks balance and reverts before any state change or pool admission. |
| `b5048b881e` | Sequencer admission filters preferred aggregator mismatch. | Sequencer admission must enforce authoritative fee/aggregator policy; missing `sequencer-admission-policy`. | Search privileged admission paths whose policy comes from account or chain state. | The sequencer sink independently reloads and rejects mismatched policy. |
| `368fbe57cb` | Validator startup gained mode and chain-access preflight checks. | Validator configuration must fail closed before participation; missing `validator-configuration-preflight`. | Compare startup constructors with steady-state verification assumptions. | Missing dependency only disables optional behavior and cannot reach validation or node action generation. |
| `c4a31f0842` | Validator progress was bound to block hash to survive same-height reorgs. | Persisted progress must bind canonical hash, not just height; missing `canonical-chain-progress-binding`. | Search recovery/progress stores keyed by height alone. | All later actions reload canonical hash and reject stale progress before signing or submission. |
| `3a9ee37539` | Machine loading validates explicit/latest module root identity. | Runtime artifacts must prove measured identity before use; missing `executable-artifact-root-binding`. | Search loaders where alias/default/root selection is not compared to reported artifact identity. | The artifact cannot influence validation or its measured root is checked at the sink. |
| `f990e534ab` | Node Docker image moved from root to non-root runtime user. | Production service runtime should be least privilege; missing `runtime-least-privilege`. | Check deployment images and service units for unnecessary root defaults. | Container is strictly sandboxed and has no sensitive writable mounts or privileged capabilities. |
| `37c04d56b5` | Withdrawal destination control was narrowed in staker withdrawal path. | Privileged fund sinks should derive destination from trusted state; missing `withdrawal-destination-authority`. | Search sensitive sinks whose caller supplies an address that can be derived from contract state. | Destination is fully authorized and rechecked by the sink or contract. |
| `d12b1a91cd` | Beacon transition header verifier validates terminal total difficulty for mixed batches. | Fork-boundary validators must handle mixed pre/post transition batches; missing `fork-boundary-consensus-validation`. | Search batch validators spanning fork boundaries for per-item split and transition checks. | Batches cannot span the transition or are split before validation. |
| `4f32fd7c77` | Broadcast feed checks contiguous sequence numbers and signing/order metadata. | Signed streams must bind sequence/order/domain before ingestion; missing `sequenced-message-order-and-signature-binding`. | Search feed ingestion where signature covers payload but not sequence continuity. | Downstream consumer independently rejects gaps, duplicates, and wrong-domain messages. |
| `b818e73ef3` | Beacon engine header verification splits batches around The Merge boundary. | Header batch validation must preserve fork-boundary semantics; missing `fork-boundary-consensus-validation`. | Compare per-header vs batch validation around hardfork or consensus-mode switches. | Shared verifier returns exact per-header errors for mixed batches. |
| `f88557d061` | Stylus/Wasm activation returns updated mutable gas and burns consumed gas. | Offloaded helpers must return consumed/remaining budget to the authoritative meter; missing `gas-metering-consistency`. | Search cross-runtime calls where mutable gas/quota is passed in but not returned or reconciled. | The callee charges the same authoritative meter directly. |
| `ac07554f71` | Access predicate inverted owner/error handling. | Authorization must fail closed on lookup errors; missing `authorization-error-handling`. | Search predicates combining role booleans with `err` checks. | Error path always denies and a separate sink-level gate exists. |
| `e4b8058d5a` | FeeHistory caps caller-supplied reward percentile fanout. | RPC query fanout must cap every dimension before scheduling work; missing `request-bounded-resource-use`. | Look for range APIs whose work is block count multiplied by per-block options. | Both range and per-item option lists are capped before goroutines/cache keys. |
| `a719c5c923` | Express-lane processing checks current round matches message round. | Privileged queues must revalidate round freshness at execution/dequeue; missing `round-scoped-admission-binding`. | Search enqueue/dequeue loops where authorization or freshness is checked only at admission. | Dequeue and replay reload authoritative round/controller state before sequencing. |
| `2e739fce58` | Blobpool/SetCode admission rejects delegated sender resource conflicts. | Txpool subpools must share sender/resource isolation; missing `txpool-resource-isolation`. | Compare new tx types across legacy pool, blobpool, delegation, and replacement logic. | One shared reservation policy guards every pool and sender state transition. |
| `20ad4f500e` | Blobpool validation adds explicit max blob count. | Per-transaction sidecar/blob counts must be bounded at admission; missing `blob-count-bound`. | Search validation options that omit count while later code assumes a protocol maximum. | Protocol max is enforced in the same path before pool insertion. |
| `56d201b0fe` | Tx fetcher validates announcement metadata before fetch work. | Peer announcements must be checked before scheduling bandwidth; missing `announcement-metadata-validation`. | Search announcement handlers that enqueue fetches before known-hash, type, size, or metadata validation. | Fetch scheduler skips known/invalid metadata and penalizes abusive peers. |
| `8fe83188ce` | Delayed-message sequencing runs accumulator/reorg validation in MEL mode. | Sequencing must run accumulator validation in every mode; missing `sequencing-accumulator-validation`. | Compare delayed-message/live/replay/MEL paths for one mode skipping the same accumulator check. | A later sequencer/verifier rejects the bad accumulator before state or message order is committed. |

## Family Clustering

### 1. Peer Progress, Response Binding, And Cost Symmetry

Findings: `de7af720d6`, `a4246c2da6`, `5c1a7b965c`, `cd2fb09051`, `52db6d8be5`, `d6f2c0a76f`, `0042f13d47`, `9123eceb0f`, `56d201b0fe`.

Why grouped: all involve long-lived peer/discovery/sync/fetch state where the peer can satisfy a request too weakly, avoid progress, trigger work before metadata validation, or exploit request/response cost asymmetry.

Portability: high for any DLT node with peer sync, discovery, gossip, transaction fetch, or state sync.

### 2. Consensus Commitments, Fork Boundaries, And Chain-Variant Rules

Findings: `60cdb1148c`, `82beaabf6a`, `a5f6a1cb7c`, `d12b1a91cd`, `b818e73ef3`, plus parts of `97aacd9b35` and `d6254f827b`.

Why grouped: these are consensus-sensitive but not all fit generic malformed-input validation. They ask whether header/body commitments, state transition edge cases, fork config compatibility, terminal difficulty, and deterministic fork choice are enforced in every equivalent path.

Portability: high for execution clients, rollup clients, bridge header verifiers, and consensus engines.

### 3. State Commitment, Journaling, Content Addressing, And Artifact Identity

Findings: `12d654a6fc`, `e23e86921b`, `08f27428b4`, `3a9ee37539`, `c4a31f0842`, `8fe83188ce`.

Why grouped: each is about a value that becomes authoritative later: journaled state touches, content-addressed chunks, occupied account identity, runtime module roots, canonical progress hashes, or delayed-message accumulators.

Portability: high for state tries, content-addressed stores, VM/prover artifacts, validator progress stores, and proof/sequencing pipelines.

### 4. Signing, Replay Protection, Feed Authenticity, And Ordered Message Streams

Findings: `b59c8399fb`, `15339cf1c9`, `ed0670cb17`, `142fbcfd6f`, `4f32fd7c77`.

Why grouped: cryptographic validity is not enough. The signed or authenticated artifact must bind purpose, chain ID, publisher identity, sequence, order, and message domain.

Portability: high for wallets, transaction helpers, relays, signed feeds, bridge messages, advisory feeds, and sequencer broadcast streams.

### 5. Resource Accounting Across RPC, Txpool, Gas, And Offloaded Execution

Findings: `e4b8058d5a`, `2e739fce58`, `20ad4f500e`, `f88557d061`, `f990e534ab`.

Why grouped: all involve resource boundaries: nested RPC query fanout, txpool/blobpool sender isolation, sidecar count limits, mutable gas returned from an offloaded runtime, and process privilege containment.

Portability: high for mempools, RPC services, gas metering, VM offload boundaries, and deployment hardening.

### 6. Authorization And Fail-Closed Policy At The Sink

Findings: `d3441ebb56`, `b5048b881e`, `37c04d56b5`, `ac07554f71`, `a719c5c923`.

Why grouped: authorization or policy information existed but needed to be checked at the exact sensitive sink or with fail-closed error handling: signer warnings, sequencer aggregator policy, withdrawal destinations, owner lookup errors, and round freshness.

Portability: high for sequencers, signers, admin/cache APIs, withdrawals, and privileged queues.

### 7. Corpus/Provenance Only

Finding: `368fbe57cb` is useful evidence for validator configuration preflight, but the current `00_protocol_mapper`, `11_signature_binding_and_signer_scope`, `15_state_machine_and_lifecycle_consistency`, and `18_authoritative_state_and_boundary_enforcement` already cover startup/constructor fail-closed checks. It should stay in corpus/provenance unless more repos show the same validator-config-specific pattern.

## Prompt-Pack Comparison

The current prompt pack already includes major families that earlier repos justified: `19_consensus_fork_and_payload_rule_validation.md`, `20_authenticated_state_proof_and_persistence_integrity.md`, `21_peer_sync_progress_and_response_binding.md`, and `22_ledger_accounting_and_invariant_coverage.md`. The geth-arb corpus does not justify a brand-new family. It does, however, identify five weak spots:

1. `21_peer_sync_progress_and_response_binding.md` handles request tokens and no-progress loops, but it should more explicitly mention UDP/discovery amplification and made-progress return values.
2. `19_consensus_fork_and_payload_rule_validation.md` covers fork/payload rules, but it should more explicitly include block-body/header commitments and state-transition side effects such as journaling, gas, generated work, and deterministic tie-breaks.
3. `14_resource_accounting_and_limits.md` already covers mutable budgets and historical APIs, but it should call out nested fanout APIs where `range * options` controls work, and transaction subpool resource isolation for delegated/new transaction types.
4. `10_authz_and_role_gates.md` should add fail-closed predicate/error handling and sensitive-sink parameter narrowing.
5. `00_protocol_mapper.md` and `18_authoritative_state_and_boundary_enforcement.md` should be sharpened for forked-client or chain-variant overlays where base-client and rollup-specific invariants share execution code but have different authority sources.

## Proposed Prompt Changes

### Change 1: Refine `prompts/21_peer_sync_progress_and_response_binding.md`

Add these search patterns after the existing discovery ping/pong bullet:

```text
- spoofable or unauthenticated discovery requests that can trigger larger responses, table lookups, peer-table mutation, or recursive lookup work before bonding, reachability, nonce, or token validation
- queue insertion, response-processing, or hash/body/state delivery APIs that return only success/failure when callers need to know whether the peer contributed new work, made zero progress, returned duplicate data, or revealed an unknown parent
- transaction, block, or state announcements where metadata validation, known-object checks, type support, and size bounds happen after the fetch request is already scheduled
```

Add these questions:

```text
7. Does the response handler distinguish made-progress, duplicate/no-progress, stale, unknown-parent, invalid, and benign-empty outcomes?
8. Can a small request or announcement force a larger response, lookup, or fetch before the peer has proven reachability or supplied valid metadata?
```

Rationale: This would help surface the discovery amplification, duplicate-hash replay, unknown-parent stall, zero-progress downloader, and tx announcement metadata findings without naming geth-specific functions.

Repo-specific details intentionally excluded: `findnode`, `TakeBlocks`, historical downloader function names, and tx fetcher internals.

Overfitting risk check: Low. The same peer-state shapes appear in discovery, gossip, header/body/state sync, transaction fetchers, and bridge relayers.

### Change 2: Refine `prompts/19_consensus_fork_and_payload_rule_validation.md`

Add these search patterns:

```text
- block, batch, or payload bodies where canonical commitments such as transaction root, receipt root, withdrawal root, blob commitment, state root, or generated-system-work root are present in the header but recomputation/equality checks are disabled, delayed, or only performed in one import path
- execution-state side effects that influence consensus roots, such as account touches, empty-account deletion, gas accounting, generated transactions, receipts, logs, refunds, or storage journaling, where one edge-case path updates the committed state but not the journal or rollback state
- equal-score, equal-work, same-height, or same-round competitor selection where tie-breaking is random, local, or nondeterministic instead of explicitly defined by protocol or node policy
```

Add this question:

```text
9. Does every execution path that can affect the state root, receipt root, generated work, or fork-choice result journal and validate the same side effects as the canonical path?
```

Rationale: The current prompt already covers fork and payload validation well. This geth corpus adds body commitment re-enablement, state journaling, uncle/fork boundary constants, and deterministic fork-choice lessons.

Repo-specific details intentionally excluded: Ethereum uncle terminology, exact EIPs, historical constants, and file names.

Overfitting risk check: Low. Header/body commitments, execution side effects, rollback journals, generated work, and deterministic tie-breaks are portable across execution clients, rollups, and consensus engines.

### Change 3: Refine `prompts/14_resource_accounting_and_limits.md`

Add these search patterns:

```text
- RPC, query, history, trace, log, proof, or fee APIs where total work is the product of a range and caller-supplied per-item options. Cap every dimension before spawning goroutines, allocating result matrices, or building cache keys.
- transaction pools with multiple subpools, delegated senders, blob/sidecar data, replacement rules, or feature-specific transaction types. Check that sender-level and resource-level isolation is enforced consistently across every subpool, not only the legacy pool.
- offloaded or cross-runtime execution that receives a mutable gas, quota, or multi-resource budget. The caller's authoritative meter must receive the post-call remaining budget and burn the consumed amount before state activation or persistence.
```

Add this question:

```text
12. Is the true cost a single scalar, or does it multiply across range length, requested percentiles/options, sidecar count, delegated sender state, or offloaded runtime work?
```

Rationale: Existing resource guidance is strong, but geth-arb shows three concrete refinements: nested FeeHistory-style fanout, blobpool/SetCode subpool resource isolation, and Stylus/Wasm mutable gas reconciliation.

Repo-specific details intentionally excluded: `FeeHistory`, `SetCode`, `BlobPool`, Stylus, and Arbitrum-specific gas names.

Overfitting risk check: Low. Nested query fanout, multi-pool mempools, and offloaded VM gas handoff recur in many DLT systems.

### Change 4: Refine `prompts/10_authz_and_role_gates.md`

Add these search patterns:

```text
- authorization predicates that combine a boolean result with an error result. Errors from role, owner, policy, or registry lookup should fail closed and must not be treated as proof of access.
- sensitive sinks that accept a caller-supplied destination, recipient, authority, fee recipient, aggregator, controller, or round value when the sink can derive that value from authoritative state.
- privileged queues where admission checks authorization, owner, policy, or round freshness but dequeue, replay, retry, or execution uses cached state or a weaker predicate.
- signing or approval middleware where validation warnings, policy failures, or UI-mediated prompts default to continue instead of requiring explicit approval under a clearly unsafe mode.
```

Add these questions:

```text
9. If the role or policy lookup returns both `(allowed, error)`, which combinations grant access, and do all errors deny?
10. Can the privileged sink derive the sensitive recipient, authority, or policy value itself instead of trusting a caller-supplied parameter?
11. Are admission, dequeue, replay, and execution checking the same authority and freshness source?
```

Rationale: This captures access-control error inversion, signer fail-closed policy, sequencer fee policy, withdrawal destination narrowing, and round-scoped privileged submission checks.

Repo-specific details intentionally excluded: chain owner cache names, express lane terminology, and Arbitrum withdrawal method names.

Overfitting risk check: Low. Boolean-plus-error authorization bugs, sink parameter narrowing, and queue-stage authorization drift are common outside this repo.

### Change 5: Refine `00_protocol_mapper.md`

Add a step after current chain-variant and generated-work mapping:

```text
20. If the repository is a fork, extension, rollup adaptation, or chain-variant of a larger client, map base-client invariants separately from variant-specific invariants:
  - which transaction/header/block types are inherited unchanged,
  - which validators are shared but parameterized by variant-specific fork, timestamp, gas, sequencer, or artifact state,
  - which generated side effects or internal transactions are added by the variant,
  - which base-client caches, pools, signers, or state journals are reused by the variant,
  - where the variant's authoritative source of truth overrides or augments base-client assumptions.
```

Rationale: The target repo mixes geth and Arbitrum semantics. The existing mapper has excellent individual sections for fork rules, artifacts, generated work, and extraction pipelines, but the geth-arb corpus shows that auditors need to explicitly map where a forked client shares code with a chain variant.

Repo-specific details intentionally excluded: Geth, Nitro, Arbitrum, Stylus, MEL, and express-lane names.

Overfitting risk check: Low. This applies to OP Stack, Polygon/Bor, Avalanche subnet clients, Cosmos SDK app chains, rollup forks, and any execution client with chain-variant extensions.

### Change 6: Refine `prompts/18_authoritative_state_and_boundary_enforcement.md`

Add these search patterns:

```text
- chain-variant or rollup adapters that reuse base-client pools, signers, state journals, gas meters, or block import helpers while adding variant-specific authority such as sequencer policy, delayed-message accumulators, module roots, or generated transactions
- runtime artifact loaders where `latest`, default, local cache, or config shorthand is accepted before comparing the measured module/root/version/genesis identity against the chain, challenge, or validator expectation
- validator or sequencer progress stores keyed by height, count, local read progress, or optional reader state where the authoritative identity includes block hash, accumulator, finalized boundary, module root, or delayed-message sequence
```

Add this question:

```text
10. If this code extends a base client, which layer is authoritative for the variant-specific fact, and is that fact rechecked at the shared base-client sink?
```

Rationale: This strengthens the prompt for module-root validation, validator reorg progress, delayed-message accumulator validation, and chain-variant sequencer policy without creating a new family.

Repo-specific details intentionally excluded: module root file names, Arbitrum delayed message names, and exact validator types.

Overfitting risk check: Low. This is a general forked-client and chain-variant audit pattern.

### Change 7: Refine `02_validation_and_impact.md`

Add these missing-property options to the existing list:

```text
  - request-response cost symmetry
  - made-progress and zero-progress classification
  - block-body commitment recomputation
  - execution-side-effect journaling
  - mutable budget handoff across runtime boundaries
  - authorization error fail-closed handling
  - variant-specific authority at shared base-client sinks
```

Add this impact prompt:

```text
15. If the issue appears in a forked client or chain-variant overlay, distinguish base-client consensus impact from variant-local sequencer, validator, gas, artifact, or delayed-message impact. Do not claim base-chain consensus breakage when the evidence only proves variant-local hardening.
```

Rationale: Phase-4 kept many findings as security hardening. The validation prompt should help agents avoid overclaiming when a finding affects a chain variant, signer warning, advisory feed, Docker runtime, or local validator progress rather than a direct consensus break.

Repo-specific details intentionally excluded: Arbitrum-specific subsystem names and exact findings.

Overfitting risk check: Low. This reduces false positives and overclaiming for all forked-client audits.

## New Family Prompts

No new family prompt is justified.

The current pack already has the right family structure:

- `19_consensus_fork_and_payload_rule_validation.md` covers consensus/fork/header/body validation.
- `20_authenticated_state_proof_and_persistence_integrity.md` covers trie, proof, state, and persistence issues.
- `21_peer_sync_progress_and_response_binding.md` covers downloader, tx fetcher, discovery, and peer response binding.
- `14_resource_accounting_and_limits.md` covers gas, query fanout, mempool, and budget issues.
- `10_authz_and_role_gates.md` covers the sequencer/signer/admin authorization subset.
- `18_authoritative_state_and_boundary_enforcement.md` covers runtime artifact identity and stale authoritative state.

The geth-arb corpus sharpens these prompts but does not expose a portable mechanism that current families cannot express cleanly.

## Validation Notes

Holdout method: I drafted the proposed changes primarily from the early Ethereum/geth clusters: block commitment, downloader response binding, discovery amplification, signing/replay protection, and state journaling. I then checked the wording against later Arbitrum/Nitro-flavored findings: Stylus gas handoff (`f88557d061`), access-control error handling (`ac07554f71`), FeeHistory fanout (`e4b8058d5a`), express-lane round binding (`a719c5c923`), blobpool/SetCode resource isolation (`2e739fce58`), tx announcement metadata (`56d201b0fe`), and delayed-message accumulator validation (`8fe83188ce`).

Result: the proposed changes would still steer an auditor toward the held-out tail cases without naming them:

- Change 3 covers FeeHistory fanout, blobpool resource isolation, and mutable gas handoff.
- Change 4 covers authorization error handling and round-scoped privileged queues.
- Change 6 covers delayed-message accumulators and chain-variant authoritative state at shared sinks.
- Change 7 prevents overclaiming variant-local hardening as base-client consensus breakage.

Remaining doubts:

- Some older 2014-2015 findings are historically specific to now-removed downloader and block-manager internals. Their lessons are portable, but the exact code paths are not current.
- The target checkout contains both geth and Nitro/Arbitrum code. Prompt text should treat this as a generic forked-client/chain-variant pattern, not an instruction to search for Arbitrum-specific names.
- `container-least-privilege-hardening` is valid corpus evidence but should not drive a new runtime prompt; it is sufficiently covered by resource/deployment hardening guidance.

Prompts that should stay unchanged:

- `16_staking_registry_and_accountability.md`: the kept set has no strong staking/slashing registry lesson beyond generic validator config hardening.
- `17_checked_arithmetic_and_parameter_bounds.md`: numeric bounds appear indirectly in gas/fee/resource checks, but not enough to change the arithmetic prompt.
- `22_ledger_accounting_and_invariant_coverage.md`: geth-arb adds one balance precheck case, but the rippled-driven ledger prompt already covers richer accounting patterns.
- `12_attestation_trust_and_freshness.md`: advisory feed authenticity is relevant, but the existing trust prompt already covers trust-list and remote trust material well; the more direct refinement belongs in signature/feed authenticity and validation impact.
