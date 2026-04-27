# Reth Prompt-Pack Refinement Proposal

Target repo: `/testing/reth`

Evidence folder: `/testing/reth/validated-findings/kept`

Current prompt pack: `/testing/dlt-ai-audit-system`

## Repo Context Summary

Reth is a modular Rust Ethereum execution client. The security-sensitive architecture is split across consensus and Engine API handling, EVM execution, payload building and validation, transaction pool admission, P2P networking and discovery, staged sync, database providers, static files, and authenticated trie/state-root logic.

Important trust boundaries:

- Consensus layer to execution layer via Engine API, especially `newPayload`, `forkchoiceUpdated`, payload attributes, head/safe/finalized state, and fork-specific payload versions.
- Remote peers to local P2P peer state, fetch scheduling, body/header import, transaction gossip, and session authentication.
- RPC clients to transaction construction, JWT/auth parsing, debug/admin APIs, and transaction submission.
- Untrusted blocks, headers, transactions, blob sidecars, receipts, proofs, and trie nodes to canonical validation and persistence.
- Internal cached or derived state to authoritative canonical state, especially trie updates, state overlays, precompile cache outputs, fork-local hashes, and pruning checkpoints.

High-risk entrypoint categories:

- Engine API payload and forkchoice handlers.
- Header, block body, receipt, blob, and transaction validators.
- P2P discovery, session setup, peer admission, peer scoring, request scheduling, and gossip listeners.
- Trie proof generation, sparse trie pruning, hashed-state computation, canonical persistence, and state provider overlay resolution.
- Fork, hardfork, network-upgrade, and method-version gates.
- Resource accounting in txpool limits, handshake timeouts, gas accounting, and precompile caches.

State-machine and lifecycle patterns that mattered:

- Forkchoice and canonical-chain state can be valid, invalid, syncing, sidechain, finalized, safe, or pending persistence.
- Reorg and fork ancestry can change which state overlay, trie update, or block hash is authoritative at the same height.
- Caches can carry caller-local accounting or fork-local state unless explicitly rebound.
- Special-case payloads and legacy/fork-specific compatibility branches can accidentally weaken normal validation.

## Finding Inventory

Analyzed all 52 files in `/testing/reth/validated-findings/kept`:

`2022-12-02-reth-p2p-networking-debc87177.md`, `2022-12-15-reth-transaction-processing-9208f2fd9.md`, `2023-01-13-reth-p2p-networking-5c80bc912.md`, `2023-01-20-reth-p2p-networking-eb11da8ad.md`, `2023-01-30-reth-storage-0e24093b0.md`, `2023-02-11-reth-transaction-processing-eba63b8f7.md`, `2023-03-28-reth-rpc-client-api-b55b2d618.md`, `2023-04-11-reth-transaction-processing-e0e449d5f.md`, `2023-04-12-reth-consensus-e87960ea8.md`, `2023-05-02-reth-storage-949b3639c.md`, `2023-05-02-reth-storage-be87dcc68.md`, `2023-05-04-reth-consensus-010b600f3.md`, `2023-05-18-reth-consensus-460bf13b6.md`, `2023-06-06-reth-storage-c0fb169da.md`, `2023-07-03-reth-transaction-processing-64554dd0f.md`, `2023-07-12-reth-storage-99240906a.md`, `2023-08-02-reth-p2p-networking-94dfeb3ad.md`, `2023-08-03-reth-transaction-processing-3f63a0887.md`, `2023-08-29-reth-p2p-networking-03afe376b.md`, `2023-09-21-reth-transaction-processing-6a601755c.md`, `2023-09-26-reth-storage-eb6dc5197.md`, `2023-11-16-reth-transaction-processing-2b4eb8438.md`, `2023-11-29-reth-transaction-processing-2c5a748c5.md`, `2023-12-23-reth-transaction-processing-8fb6ed9cc.md`, `2024-02-02-reth-transaction-processing-72b7caa4c.md`, `2024-02-03-reth-transaction-processing-d4dffa2ee.md`, `2024-02-15-reth-transaction-processing-945031900.md`, `2024-03-18-reth-storage-9962c3949.md`, `2024-03-19-reth-p2p-networking-1ad50d148.md`, `2024-04-16-reth-storage-33b195af3.md`, `2024-04-25-reth-rpc-client-api-33e7e0208.md`, `2024-05-21-reth-transaction-processing-5100ddd28.md`, `2024-08-05-reth-storage-08158e444.md`, `2024-09-02-reth-consensus-d59854f1d.md`, `2024-12-04-reth-transaction-processing-d298fb1b8.md`, `2025-04-19-reth-core-logic-6ef19f403.md`, `2025-04-25-reth-transaction-processing-82d650594.md`, `2025-05-28-reth-storage-1cfe50998.md`, `2025-09-25-reth-rpc-client-api-aa192c255.md`, `2025-10-29-reth-transaction-processing-77ef028ac.md`, `2026-01-29-reth-core-logic-bc5e23ddd.md`, `2026-01-29-reth-storage-edf75de4d.md`, `2026-02-03-reth-storage-4b9244c7d.md`, `2026-02-04-reth-transaction-processing-7671838c6.md`, `2026-03-04-reth-storage-d8de8afa9.md`, `2026-03-06-reth-storage-a1600ef0c.md`, `2026-03-09-reth-transaction-processing-9c33fb5d4.md`, `2026-03-21-reth-transaction-processing-b78f74f52.md`, `2026-04-01-reth-storage-7c1a43bac.md`, `2026-04-01-reth-transaction-processing-c4517d4c3.md`, `2026-04-20-reth-storage-d577814eb.md`, `2026-04-21-reth-storage-d92ad5aa3.md`.

No findings were intentionally skipped.

## Finding-To-Mechanism Analysis

Condensed per-finding analysis:

| Finding | Mechanism | Generic invariant | Hunt recipe | False-positive killers |
| --- | --- | --- | --- | --- |
| `debc87177` | P2P parser checked the wrong byte buffer and normalized edge-case RLP handling. | Inbound protocol parsers must bound and decode attacker-controlled bytes, not locally reconstructed bytes. | Compare transport bytes, decoded message bytes, and helper-generated bytes at handshake/parser boundaries. | Later parser rejects malformed input; checked buffer is provably the attacker-controlled buffer. |
| `9208f2fd9` | Fork selection and VM exit classification used wrong rule mapping. | Execution rule selection must match the block's active fork and fail closed on unexpected VM exits. | Search fork-to-spec maps and default VM result handling. | Equivalent fork gate exists earlier; unexpected exits cannot affect receipt or block validity. |
| `5c80bc912` | Discovery path admitted peers before fork-ID compatibility checks. | Peer admission from discovery must pass protocol compatibility validation before insertion. | Compare direct discovery handlers with centralized peer admission paths. | Handshake always rejects before resource impact; missing fork ID is intentionally allowed. |
| `eb11da8ad` | Handshake artifacts were built from separate status/filter state. | Peer authentication artifacts must be derived from one authoritative head and chain config. | Search builders that accept separate protocol status, head, fork filter, and chain spec values. | Builder is test-only or all inputs are derived atomically by construction. |
| `0e24093b0` | Empty-account state rule was enforced at wrong or incomplete fork boundary. | State persistence must enforce fork-specific account emptiness rules at the canonical fork height. | Search fork-gated state cleanup and account persistence rules. | Later trie/state-root validation enforces the same rule before persistence. |
| `eba63b8f7` | Paris activation checks omitted current difficulty at TTD boundary. | Hardfork predicates must include all transition-defining fields. | Audit every fork activation call site for missing side inputs such as current difficulty, timestamp, method version, or payload kind. | Predicate implementation ignores omitted field by design or transition is unreachable. |
| `b55b2d618` | Network tx import penalized senders for non-malicious pool failures. | Peer penalties must distinguish invalid attacker input from local capacity or state conditions. | Search `Err` mapping paths feeding reputation or penalties. | All failures indicate malicious input; no downstream penalty exists. |
| `e0e449d5f` | Legacy signature `v` accepted non-canonical values. | Signature decoders must reject non-canonical encodings before recovery. | Search parity normalization and legacy compatibility branches. | Canonicality is enforced before consensus or txpool acceptance. |
| `e87960ea8` | Forkchoice handling did not fully validate head existence before state decisions. | Externally supplied forkchoice state must be checked against local known canonical state before state transitions. | Trace Engine API forkchoice state from input to sync/valid/invalid decisions. | Engine API is unreachable or later canonical checks always run before side effects. |
| `949b3639c` | Invalid ancestry was tracked incompletely. | Known-invalid ancestry must be carried through all forkchoice and payload-status decisions. | Search invalid marker propagation across payload hash, header hash, and ancestor traversal. | Invalid status cannot be lost or downgraded to generic sync. |
| `be87dcc68` | Trie rebuild checkpoint lacked target binding. | Checkpoints must be bound to the target range or state they resume. | Search resumable rebuilds and checkpoint metadata. | Checkpoint data is invalidated whenever target parameters differ. |
| `010b600f3` | Parent hash and parent number were not cross-checked. | Parent identity must bind both hash and height before consensus validation proceeds. | Search parent lookup helpers that accept one coordinate and trust another. | Stored block lookup returns a sealed header with both fields checked at call site. |
| `460bf13b6` | Canonical recognition relied on transient indices, not DB canonical state. | Canonicality decisions must consult authoritative persisted or canonical state, not transient mirrors only. | Search `is_canonical` and DB/tree split decisions. | Transient mirror is atomically maintained and verified against DB before use. |
| `c0fb169da` | Consensus execution and sender recovery errors were classified too generically. | Invalid-block errors must remain distinguishable from internal or recoverable execution errors. | Search error flattening around block execution and sender recovery. | Higher layers do not branch on error class. |
| `64554dd0f` | Peer-supplied bodies were not validated before sealed block construction. | Network block components must be checked for header/body consistency before block assembly. | Search constructors from peer pieces into sealed or trusted block types. | Consensus validation recomputes body roots immediately before use. |
| `94dfeb3ad` | Header range validation was weaker on full-block download paths. | Peer-supplied ranges must preserve parent linkage and expected sequence before import. | Compare header-only and full-block download validation. | Later import performs identical range validation. |
| `99240906a` | Forkchoice success and payload attributes could bypass consistency checks. | Forkchoice state must be consistent before side effects and before success responses. | Search early returns and payload-attribute branches in Engine API handlers. | Engine API auth plus later checks make no side effect possible before validation. |
| `3f63a0887` | Transaction propagation policy bit was dropped across listener notification. | Exposure policy must be preserved across event/listener boundaries. | Search boolean policy fields carried into events, channels, or subscriptions. | Listener cannot broadcast or otherwise expose the event. |
| `03afe376b` | `PropagateOnly` listeners received non-propagatable transactions. | Filtered listeners must enforce the same policy at delivery as at subscription. | Compare full-stream listeners with filtered or network-facing consumers. | Downstream listener independently rechecks policy before exposure. |
| `6a601755c` | RPC transaction conversion was infallible for oversized fields. | Boundary conversions must reject values that exceed canonical protocol widths. | Search `as`, `into`, and infallible conversion from RPC-large integer types. | Downstream serializer or signer rejects before semantic use. |
| `eb6dc5197` | Blob transaction fields accepted before Cancun activation. | Fork-activated transaction fields must be rejected before their fork enables them. | Search new feature fields against fork gates in validators. | A later consensus validator enforces the gate before block acceptance. |
| `2b4eb8438` | Blob sidecar missing during reorg reinjection validation. | Revalidation must include all context required by the transaction type. | Search reorg, reinject, revalidate, and local recovery paths for missing sidecars or proofs. | Transaction type cannot require external sidecar data. |
| `2c5a748c5` | Checked and unchecked signer recovery paths diverged on high-s signatures. | Compatibility recovery must not bypass canonical signature rules on acceptance paths. | Search `recover_unchecked`, legacy recovery, and high-s checks. | Unchecked recovery only used for historical display, not validation. |
| `8fb6ed9cc` | EIP-1559 gate used Berlin instead of London. | Feature gates must use the exact fork that defines the protocol feature. | Search transaction-type gates and fork constants. | Another gate with the correct fork runs before acceptance. |
| `72b7caa4c` | Txpool truncation enforced count but not aggregate size. | Resource limits must apply the complete limit predicate at every enforcement point. | Compare limit predicates with pruning/truncation implementations. | Alternate cleanup enforces the missing dimension first. |
| `d4dffa2ee` | Blob pool evicted only when size and count exceeded, not either. | Multi-dimensional capacity checks must use the same boolean semantics everywhere. | Search `&&` versus helper predicate for count and byte limits. | Capacity breach cannot persist because insertion is blocked earlier. |
| `945031900` | Blob versioned hash was computed but not compared to declared hash. | Declared cryptographic references must match commitment-derived values before acceptance. | Search "compute/derive hash" without equality check against declared field. | Another mandatory validator binds the same commitment before use. |
| `1ad50d148` | Pending P2P session auth lacked timeout. | Unauthenticated handshake work must have bounded lifetime and concurrency. | Search pending auth futures without timeout or permit. | Outer accept loop enforces strict timeout and resource cap. |
| `33e7e0208` | Bad block-body responses did not affect peer ranking/follow-up scheduling. | Bad-response signals must feed into peer selection before follow-up work. | Compare response handlers for headers vs bodies or success vs empty paths. | Empty response is benign and later ranking consumes no peer-quality state. |
| `33b195af3` | Sidechain block-hash reconstruction confused same-height branch hashes. | Fork-local views must preserve branch identity, not just height order. | Search sidechain hash maps keyed by height or overwritten during traversal. | Code always carries block hash identity to the sink. |
| `9962c3949` | Canonicalization errors were ignored or downgraded. | Fatal canonicalization failures must surface to Engine API or import callers. | Search ignored `Result`, logging-only errors, and `let _ =` in consensus paths. | Ignored errors are non-fatal metrics or cleanup only. |
| `5100ddd28` | EIP-4844 transaction destination could represent CREATE. | Transaction-type-specific forbidden forms must be unrepresentable or fail at construction. | Search generic transaction kinds reused for type-restricted transactions. | Type validator rejects before txpool or consensus use. |
| `08158e444` | Parent-header validation was missing before block insertion. | Parent-child header invariants must be checked before import state mutation. | Search import paths that lookup parent but do not validate against parent. | Consensus validates parent relation immediately after insertion and rolls back. |
| `d59854f1d` | Debug-only bound check replaced by runtime normalization. | Release builds must enforce bounds that protect state removal and pruning. | Search `debug_assert` on consensus or persistence invariants. | Out-of-range input is impossible by construction. |
| `d298fb1b8` | OP Holocene base-fee validation needed fork-specific parent timestamp and required field checks. | Fork-specific header fields must be validated by the exact fork semantics. | Search generic validators used across chain variants. | Chain-specific wrapper adds the exact check before acceptance. |
| `82d650594` | Post-merge difficulty and nonce checks moved into canonical header validators. | Consensus validators must centralize mandatory header checks across all admission paths. | Compare block admission paths for direct, sidechain, recovery, and downloaded blocks. | All paths call one canonical header validator. |
| `6ef19f403` | Header gas-limit upper bound was missing. | Consensus resource parameters need lower and upper bounds at header validation. | Search max checks omitted where min checks exist. | Protocol max is enforced by parent delta or execution before acceptance. |
| `aa192c255` | JWT bearer parsing matched embedded substring. | Auth headers must be parsed as anchored syntax, not substring search. | Search auth parsers using `contains` or split without prefix anchoring. | Token verifier cannot receive the embedded attacker-controlled substring. |
| `77ef028ac` | OP blob-gas checks used generic helper instead of fork-specific Ecotone/Jovian rules. | Chain-variant fork rules must be validated with variant-specific field presence and values. | Search mainnet helper reuse in L2 or chain-variant validators. | Variant wrapper enforces additional checks in all paths. |
| `bc5e23ddd` | Trie mutation could leave corruption on removal error. | Authenticated state mutations must validate before mutation or rollback exactly. | Search mutate-then-validate patterns in trie/state code. | Mutation is transactional or fully rolled back on every error. |
| `edf75de4d` | Reveal validation and rollback targeted wrong subtrie location. | Rollback must restore the exact coordinate that was mutated. | Search rollback logic that recomputes path/address after partial mutation. | Tests prove failed mutation leaves the whole trie unchanged. |
| `4b9244c7d` | Empty storage proof omitted EmptyRoot and stale reveal paths survived pruning. | Proof builders must return explicit absence evidence and invalidate reveal caches after pruning. | Search empty proof returns and proof cache pruning. | Consumer treats empty proof as invalid and re-reveals after prune. |
| `7671838c6` | Amsterdam gas semantics conflated receipt-facing and header-facing accounting. | Distinct protocol accounting views must not be collapsed into one field. | Search receipt/header/execution gas values shared across fork-specific semantics. | Both views are derived independently at validation time. |
| `a1600ef0c` | Trie masking left invalid single-child hashed branch. | Proof/state representations must preserve structural validity after masking or compression. | Search branch compression and mask logic for degenerate cases. | Verifier rejects malformed branch structures before trust. |
| `d8de8afa9` | Hashing stage memory decision used next batch instead of remaining range. | Resource mode selection must consider the total remaining work, not a local window. | Search batch-loop decisions that enforce limits on only next chunk. | Outer scheduler enforces a global memory cap. |
| `9c33fb5d4` | Shared cache reused stale fork-derived prewarm state across parent hashes. | Caches in forked execution contexts must be keyed or rebound by parent state identity. | Search caches cloned across failed forks, parent hashes, or canonical/fork transitions. | Cache contents are proven fork-independent. |
| `b78f74f52` | Env-switch and zero-hash special cases broadly skipped validator checks. | Special-case payload forms may relax only non-comparable fields, never core integrity checks. | Search sentinel values and special-case branches in validators. | Branch is test-only or skipped fields are exactly non-comparable. |
| `7c1a43bac` | Precompile cache hit reused stale GasTracker/reservoir. | Cached execution outputs must not replay invocation-local resource accounting. | Search cache entries that store composite results with live accounting state. | Cache stores only immutable output bytes and deterministic cost. |
| `c4517d4c3` | Same gas-accounting cache state issue in transaction processing. | Per-call resource accounting must be reconstructed on cache hits. | Search cache-hit fast paths returning cloned execution result objects. | Current frame accounting is passed into reconstruction. |
| `d577814eb` | Engine API Amsterdam field validation depended on method version and message kind. | Protocol field presence must be checked against method version, message kind, and activation state together. | Search coarse pre/post version rules in RPC/Engine validators. | Decoder rejects unsupported fields before semantic validation. |
| `d92ad5aa3` | State overlays and revert decisions used block number instead of explicit block hash. | Fork-aware state providers must bind overlays and caches to block hash, not height alone. | Search state providers keyed by height where forks can share numbers. | Provider only serves canonical finalized state where height is unique. |

## Family Clustering

### Cluster A: Consensus, fork, and payload rule enforcement

Findings: `9208f2fd9`, `0e24093b0`, `eba63b8f7`, `e87960ea8`, `949b3639c`, `010b600f3`, `460bf13b6`, `c0fb169da`, `99240906a`, `eb6dc5197`, `8fb6ed9cc`, `d298fb1b8`, `82d650594`, `6ef19f403`, `77ef028ac`, `7671838c6`, `b78f74f52`, `d577814eb`.

Why grouped: these are not generic malformed-input bugs. They involve exact Ethereum execution-client consensus semantics: fork activation predicates, header field presence, payload method versions, head/safe/finalized consistency, parent/ancestor validity, and special-case validation bypasses.

Portability: high for execution clients, rollups, consensus engines, bridge verifiers, and any DLT with versioned protocol rules.

### Cluster B: Authenticated state, trie proof, and persistence integrity

Findings: `be87dcc68`, `33b195af3`, `9962c3949`, `1cfe50998`, `bc5e23ddd`, `edf75de4d`, `4b9244c7d`, `a1600ef0c`, `9c33fb5d4`, `d92ad5aa3`.

Why grouped: these revolve around authenticated state correctness under forks, pruning, checkpoint resume, overlays, mutations, rollback, and proof construction. Existing prompts mention caches and authoritative state, but they do not focus enough on state-root/trie/proof-specific failure shapes.

Portability: high for account/state tries, Merkle stores, sparse trees, LSM/static-file state, light-client proof systems, and bridge state proofs.

### Cluster C: P2P peer admission, parser, scoring, and handshake hardening

Findings: `debc87177`, `5c80bc912`, `eb11da8ad`, `b55b2d618`, `64554dd0f`, `94dfeb3ad`, `33e7e0208`, `1ad50d148`.

Why grouped: each issue is about untrusted peer data entering peer state, protocol parsing, admission, response handling, or request scheduling before enough validation or bounding.

Portability: high for all P2P DLT nodes.

### Cluster D: Transaction, signature, blob, and duplicate-representation binding

Findings: `e0e449d5f`, `6a601755c`, `2b4eb8438`, `2c5a748c5`, `945031900`, `5100ddd28`, `aa192c255`.

Why grouped: these enforce exact canonical encodings, bounded conversions, transaction-type-specific fields, sidecar context, cryptographic commitment binding, and anchored auth syntax.

Portability: high for transaction admission, RPC-to-core conversion, proof-bearing transactions, sidecar-based protocols, auth headers, and signed message systems.

### Cluster E: Resource accounting, limits, and invocation-local accounting isolation

Findings: `72b7caa4c`, `d4dffa2ee`, `d8de8afa9`, `7c1a43bac`, `c4517d4c3`.

Why grouped: these are about enforcing full multi-dimensional limits and avoiding stale caller-local gas or reservoir state.

Portability: high for mempools, caches, gas metering, queues, batch processors, and schedulers.

### Cluster F: Propagation and listener policy preservation

Findings: `3f63a0887`, `03afe376b`.

Why grouped: policy bits were correctly known at one layer but were lost or not enforced at event/listener delivery.

Portability: medium-high for gossip networks, event buses, subscriptions, pubsub, and bridge relayers.

## Prompt-Pack Comparison

Cluster A should become a new family prompt. `13_input_validation_and_invariant_enforcement.md` mentions fork-gated fields, and `18_authoritative_state_and_boundary_enforcement.md` mentions head/fork rules, but neither gives enough action-oriented guidance for Engine API, payload versions, header semantic fields, forkchoice consistency, parent/ancestor invalidity, or chain-variant fork rules.

Cluster B should also become a new family prompt. `15_state_machine_and_lifecycle_consistency.md` and `18_authoritative_state_and_boundary_enforcement.md` partially cover caches and authoritative state, but Reth's kept findings show repeated authenticated state/proof-specific patterns: EmptyRoot evidence, checkpoint target binding, state overlay hash binding, rollback atomicity, pruning invalidation, and fork-local hash reconstruction.

Cluster C should refine `01_base_hunter.md`, `13_input_validation_and_invariant_enforcement.md`, and `14_resource_accounting_and_limits.md`. Existing prompts mention P2P handlers and resource limits, but they underemphasize peer-quality feedback loops, admission from discovery, protocol parser checking of original attacker bytes, and penalty misclassification.

Cluster D should refine `11_signature_binding_and_signer_scope.md`, `13_input_validation_and_invariant_enforcement.md`, and `02_validation_and_impact.md`. The pack already handles duplicate representation binding well, but should explicitly include "computed but not compared" and "sidecar context absent during revalidation" as hunt motifs.

Cluster E should refine `14_resource_accounting_and_limits.md` with multi-dimensional predicate consistency and cache-hit accounting isolation. It should not become a new family because the existing resource prompt can express it cleanly.

Cluster F should refine `15_state_machine_and_lifecycle_consistency.md` and `18_authoritative_state_and_boundary_enforcement.md` with listener/event policy preservation. It should not become a new family because only two findings support it and the mechanism is a sharpening of existing boundary enforcement.

## Proposed Prompt Changes

### Change 1: Add new family `prompts/19_consensus_fork_and_payload_rule_validation.md`

Rationale: This cluster appears in more than one-third of the kept Reth findings. Existing generic input-validation text is too broad to reliably steer an auditor into Engine API method versions, forkchoice state consistency, header semantic fields, and fork-variant payload rules.

Draft text:

```text
# Prompt Family: Consensus, Fork, And Payload Rule Validation

## Use This For

- Engine API, consensus API, block import, and payload validation paths.
- Forkchoice head, safe, finalized, invalid, syncing, and payload-attribute handling.
- Fork, hardfork, network-upgrade, L2 variant, method-version, or payload-version gates.
- Header, receipt, blob gas, base fee, difficulty, nonce, timestamp, parent, and state-root semantics.
- Special-case replay, synthetic block, legacy, benchmark, migration, or compatibility branches that may weaken normal validation.

## Prompt

Hunt for consensus-rule validation bugs in a blockchain or DLT codebase.

Focus on externally supplied or consensus-layer supplied blocks, headers, payloads, forkchoice states, receipts, sidecars, and payload attributes before they affect canonical state, payload building, execution, or success responses.

Search patterns:

- A fork or feature predicate called with fewer inputs than the protocol rule requires, such as height without timestamp, parent total difficulty without current difficulty, method version without message kind, or activation state without chain variant.
- A generic mainnet or base-chain validator reused for a chain variant that has different field presence, value, or timing rules.
- Header or payload fields checked in one import path but omitted in sidechain, downloaded, recovery, optimistic, reorg, replay, or Engine API paths.
- Early returns that process payload attributes, return VALID, or update head/safe/finalized state before forkchoice consistency checks run.
- Parent, ancestor, finalized, safe, or invalid-state decisions keyed by one coordinate while the protocol identity includes hash, number, parent hash, and validity status.
- Special cases for synthetic payloads, segmented blocks, zero hashes, legacy fixtures, or compatibility modes that skip broad validation instead of only the specific non-comparable field.
- Error paths that collapse invalid-block, invalid-header, or sender-recovery failures into generic execution or internal errors that higher layers cannot treat as invalid.

Questions to answer:

1. Which protocol rule is authoritative for this block, payload, fork, method version, chain variant, and timestamp or height?
2. Are all fields required by that rule present and checked before any canonical state update, payload build, or success response?
3. Does every equivalent entrypoint call the same canonical validator?
4. Do special-case or compatibility branches preserve core identity checks such as block hash, parent relation, state root, transaction root, receipt root, gas semantics, and fork-specific fields?
5. Can invalid ancestry, unknown head, inconsistent safe/finalized state, or known-invalid payload state be downgraded into syncing, generic error, or success?

Severity guidance:

- High if malformed consensus data can be accepted as canonical, finalized, valid, or execution-ready.
- Medium for security hardening where validation is tightened in consensus-sensitive paths but exploitability or end-to-end reachability is not proven.
- Low for test-only, benchmark-only, or offline compatibility branches that cannot influence production validation.
```

Repo-specific details intentionally excluded: Reth crate names, exact EIPs, commit hashes, and function names. The wording uses generic concepts like method version, chain variant, payload attributes, and forkchoice state.

Overfitting risk check: Low. The same checks apply to Ethereum clients, L2 execution clients, consensus engines, bridges that validate finalized headers, and rollup derivation pipelines.

### Change 2: Add new family `prompts/20_authenticated_state_proof_and_persistence_integrity.md`

Rationale: The current pack has state-machine and authoritative-state prompts, but not a focused family for authenticated state roots, trie proofs, proof caches, rollback atomicity, fork overlays, and persistence handoff. Reth had enough repeated examples to justify a separate portable family.

Draft text:

```text
# Prompt Family: Authenticated State, Proof, And Persistence Integrity

## Use This For

- Merkle, MPT, sparse trie, accumulator, commitment tree, state-root, and proof generation code.
- Canonical persistence, checkpoint resume, state rebuild, pruning, static-file handoff, and rollback paths.
- Fork-aware state providers, overlays, caches, prewarm state, and derived trie updates.
- Light-client, bridge, RPC, or internal proof APIs that return inclusion or non-existence evidence.

## Prompt

Hunt for bugs where authenticated state, proof material, or derived persistence data can become incomplete, stale, misbound, or non-atomic.

Focus on data that is derived from canonical state but later treated as authoritative: roots, proofs, revealed paths, trie updates, overlays, checkpoints, state-provider caches, fork-local hash views, and persisted ranges.

Search patterns:

- Checkpoints or resumable rebuild state that are not bound to the target range, root, block hash, fork, or table set they resume.
- State overlays, providers, or caches keyed by block number, range, or implicit current head where competing forks can share that coordinate.
- Proof builders that return an empty proof for absence instead of explicit empty-root or non-existence evidence.
- Pruning or compression that changes node representation without invalidating revealed paths, proof caches, or derived metadata.
- Mutate-then-validate flows in authenticated trees where rollback may not restore the exact node, subtrie, path, or account that was changed.
- Canonical persistence paths that assume trie updates, state diffs, or derived roots exist for fork ancestry instead of detecting and recomputing missing data.
- Sidechain or fork-local hash reconstruction keyed by height instead of block hash and parent relation.
- Error results ignored or logged-only in canonicalization, persistence, or state-root paths.

Questions to answer:

1. What object is authoritative: block hash, state root, trie node, proof, checkpoint target, canonical DB state, or in-memory overlay?
2. Is every derived object bound to that authority before it is reused?
3. If the code resumes, prunes, rolls back, or switches forks, which cached or derived data must be invalidated?
4. Can an absence proof be distinguished from missing proof material?
5. Are mutations atomic, or can failed validation leave a partially modified authenticated state?
6. Does persistence fail closed when required derived state is missing?

Severity guidance:

- High if a malformed proof or state root can be accepted by another trust domain, bridge, light client, or consensus path.
- Medium for state-integrity hardening where proof, trie, cache, or persistence correctness is improved but exploitability is not proven.
- Low for offline maintenance tools with no production trust boundary.
```

Repo-specific details intentionally excluded: Reth trie module names, exact sparse-node types, and commit-specific terminology.

Overfitting risk check: Low. This transfers to any blockchain using authenticated state commitments or resumable state persistence.

### Change 3: Refine `00_protocol_mapper.md`

Add under "Step 2: Build the protocol map":

```text
11. Map consensus-rule validation surfaces separately from generic input validation:
  - Engine or consensus APIs,
  - block import and sidechain import,
  - forkchoice or head/safe/finalized updates,
  - payload building and payload validation,
  - chain-variant or rollup-specific validators,
  - replay, recovery, migration, and compatibility validators.
  For each surface, note which canonical validator should run and which fork, method-version, timestamp, height, chain variant, or payload-type gates define the accepted fields.
12. Map authenticated-state derivation surfaces:
  - state roots,
  - trie or accumulator proofs,
  - checkpoints,
  - pruning and compaction,
  - fork overlays,
  - state-provider caches,
  - canonical persistence handoffs.
  For each, identify what binds derived data to the canonical block, root, range, fork, or target.
```

Rationale: Reth findings show the mapper needs to force a specific inventory of Engine API and authenticated-state surfaces before hunting. This improves transferability by teaching what to map, not where Reth stores it.

### Change 4: Refine `01_base_hunter.md`

Add to the numbered task list after item 11:

```text
12. Compare every special-case, compatibility, replay, migration, benchmark, recovery, sidechain, and fork-specific path against the normal validation path. Ask whether it skips only the exact non-comparable field or accidentally skips core identity, parent, root, accounting, authorization, or policy checks.
13. Search for feedback loops where untrusted peer, transaction, or proof outcomes should update reputation, penalties, scheduling, listener filtering, cache invalidation, or cleanup state. Check whether success, empty, invalid, timeout, abort, and retry paths update that state symmetrically.
14. Search for cached execution, proof, or state-provider outputs that include invocation-local state. On cache hits, the code should rebind or reconstruct caller-local accounting, fork identity, verifier context, and authoritative state instead of cloning stale composite objects.
```

Rationale: These are cross-family hunt moves that would have helped surface Reth's env-switch validation bypass, peer-quality handling, propagation listener policy gaps, precompile gas cache bugs, and fork-overlay state binding issues.

### Change 5: Refine `02_validation_and_impact.md`

Add to the missing-property list:

```text
   - fork/version/method-specific consensus rule coverage
   - chain-variant rule coverage
   - parent/ancestor/forkchoice consistency
   - explicit absence-proof evidence
   - authenticated-state rollback atomicity
   - cache context rebinding
   - peer-quality feedback enforcement
   - listener or event policy preservation
```

Add to impact assessment:

```text
5. Is the finding proven to cross a production trust boundary, or is it best classified as security hardening because it tightens a consensus, proof, peer, or resource-control path without a demonstrated exploit?
6. If the bug is in consensus validation, distinguish invalid-block acceptance, invalid-block rejection, syncing/liveness confusion, payload-building side effects, and error-classification hardening.
7. If the bug is in authenticated state or proof code, distinguish proof-generation ambiguity, verifier acceptance, local state corruption, persistence correctness, and consensus-visible state-root impact.
```

Rationale: Phase 4 downgraded all kept cases to `security-hardening`, including 3 confirmed hardening cases. The validation prompt should preserve this conservative distinction instead of pushing agents toward overclaiming.

### Change 6: Refine `13_input_validation_and_invariant_enforcement.md`

Add to search patterns:

```text
- code that computes, derives, parses, or canonicalizes a protocol value but does not compare it against the declared value before acceptance
- protocol objects whose validity depends on sidecar data, proof data, parent data, or fork context that may be missing in revalidation, reorg, reinjection, or recovery paths
- transaction or header types represented with a generic enum that can express forms forbidden for that type
- parser guards that check locally generated bytes, decoded bytes, or wrapper bytes instead of the original attacker-controlled transport bytes
- auth or protocol header parsing that accepts substring matches instead of anchored grammar
```

Rationale: Strengthens existing input validation without adding repo-specific Reth examples.

### Change 7: Refine `14_resource_accounting_and_limits.md`

Add to search patterns:

```text
- multi-dimensional limits where one path enforces count but not bytes, bytes but not count, or uses `both limits exceeded` where the policy says `any limit exceeded`
- cleanup or truncation paths that use a weaker predicate than insertion/admission paths
- cache-hit paths that return stored execution or precompile result objects containing gas, quota, reservoir, refund, or caller-local accounting state
- batch-mode decisions that choose clean, incremental, bounded, or unbounded work based only on the next local window instead of the full remaining range
```

Rationale: Captures Reth's txpool, blobpool, hashing-stage memory, and precompile gas-accounting lessons inside the existing family.

### Change 8: Refine `15_state_machine_and_lifecycle_consistency.md`

Add to search patterns:

```text
- event, listener, subscription, or gossip paths where a policy bit is checked at admission but dropped before delivery
- fork, reorg, retry, failed-prewarm, abort, or recovery paths that reuse caches from a prior parent hash, verifier state, peer state, or execution context
- rollback paths in authenticated or persisted state that restore a nearby object but not the exact mutated coordinate
- invalid, syncing, timeout, empty-response, and already-known states that update state in one path but not the analogous path
```

Rationale: This would help rediscover propagation policy loss, cache-state isolation issues, and rollback asymmetries without naming Reth.

### Change 9: Refine `18_authoritative_state_and_boundary_enforcement.md`

Add to search patterns:

```text
- state, overlay, provider, or cache lookups keyed by height, range, current head, or implicit context where the authoritative identity is a block hash, root, parent, fork, or target tuple
- helper-produced fork filters, protocol statuses, checkpoints, or derived roots built from separate source inputs that should come from one authoritative snapshot
- proof-carried or caller-supplied artifacts that can replace the locally authoritative verifier, root, target, fork, or state source at the sink
- canonicality checks that rely on transient indices when persisted canonical state is the source of truth
```

Rationale: Reth had repeated height-vs-hash, checkpoint-target, transient-canonicality, and handshake-status/fork-filter binding lessons.

### Change 10: Update provenance only after prompt changes are accepted

If these changes are implemented, append a Reth section to `finding-to-prompt-map.md` rather than adding Reth commit names to runtime prompts. Map each kept finding to one primary prompt family, especially the two proposed new families.

Rationale: Keeps operational prompts generic while preserving why the taxonomy changed.

## New Family Prompts

Approved as justified:

- `prompts/19_consensus_fork_and_payload_rule_validation.md`
- `prompts/20_authenticated_state_proof_and_persistence_integrity.md`

Existing families were insufficient because the Reth findings were not isolated examples. Cluster A and Cluster B each appeared repeatedly and represent portable security review surfaces, not merely Reth implementation details.

Not justified as new families:

- P2P peer-quality and admission hardening should refine existing input/resource/lifecycle prompts.
- Transaction sidecar and duplicate-representation binding should refine existing signature/input prompts.
- Propagation listener policy should refine lifecycle and authoritative-boundary prompts.

## Validation Notes

Held-out checks:

- I drafted Cluster A wording primarily from forkchoice, fork-gating, and header-rule findings, then checked it against `2026-04-20-reth-storage-d577814eb.md`. The proposed wording would still lead an auditor to method-version, message-kind, activation-state, and field-presence checks without naming Amsterdam or Reth.
- I drafted Cluster B wording primarily from trie checkpoint, mutation, and EmptyRoot examples, then checked it against `2026-04-21-reth-storage-d92ad5aa3.md`. The proposed wording would still lead an auditor to height-vs-block-hash binding in fork-aware state providers.
- I drafted resource prompt refinements from txpool/blobpool limits, then checked them against `2026-04-01-reth-storage-7c1a43bac.md` and `2026-04-01-reth-transaction-processing-c4517d4c3.md`. The cache-hit accounting text covers those cases without naming precompiles.

Remaining doubts:

- Several kept findings are hardening-only and lack demonstrated exploitability. Runtime prompts should not imply that every match is a vulnerability.
- Some Reth patterns are Ethereum-execution-client specific. The proposed wording translates them into generic concepts like fork activation, method version, chain variant, payload fields, and authenticated state.
- Exact severity should remain conservative. Most findings should start as medium or low-medium until production reachability and exploit impact are shown.

Prompts that should stay unchanged for now:

- `10_authz_and_role_gates.md` needs no major change beyond the proposed base/validation additions. Only one Reth kept finding maps cleanly to authz-style validation bypass.
- `12_attestation_trust_and_freshness.md` is not materially informed by Reth's kept set.
- `16_staking_registry_and_accountability.md` is not informed by Reth's kept set.
- `17_checked_arithmetic_and_parameter_bounds.md` gets no direct update. Reth had numeric bound checks, but they are better covered by consensus and input-validation refinements than arithmetic-overflow taxonomy.

