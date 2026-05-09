# Agave Prompt-Pack Refinement From Validated Findings

Target repo: `/testing/agave`

Evidence folder: `/testing/agave/validated-findings/kept`

Prompt used: `/testing/dlt-ai-audit-system/04_refine_prompt_pack_from_findings.md`

## Repo Context Summary

Agave is a validator/client implementation with two major pipelined roles:

- TPU: transaction ingress, signature verification, banking, and ledger production.
- TVU: ledger/shred receipt, replay, verification, fork choice, and voting.

High-risk security surfaces for the kept findings:

- Transaction admission: packet parsing, signature verification, transaction-view sanitization, durable nonce handling, rollback accounts, and SVM execution.
- Consensus and replay: ReplayStage, dead-slot marking, blockstore/shred recovery, vote packet buffering, and authorized-voter state.
- P2P and networking: QUIC admission, rate limiting, connection registration, and packet verifier backpressure.
- Storage and recovery: snapshot/genesis unpacking, archive buffer sizing, blockstore recovery.
- Operator tooling: validator-info CLI paths that parse on-chain metadata and decide whether an existing record is authentic.

Trust boundaries:

- Remote transaction packet -> sigverify -> sanitized transaction view -> banking/SVM.
- Signed durable-nonce transaction -> bank age check -> SVM execution -> rollback state.
- Peer/validator vote packet -> banking-stage vote storage -> latest-vote state.
- Peer shreds or recovered shreds -> blockstore/recovery -> ledger/replay.
- Remote QUIC peer -> pre-handshake admission -> connection registration/worker pools.
- On-chain validator-info account data/RPC response -> operator CLI display/publish decision.

State-machine and lifecycle patterns that mattered:

- Early admission checks vs execution-time revalidation.
- Failure/rollback paths that must preserve replay-protection side effects.
- Async pipelines where independent validation results must be combined fail-closed.
- Recovery/replay paths that must enforce the same rules as direct receipt paths.
- Resource accounting that must be consumed at admission, not just queried.

## Finding Inventory

Analyzed all 14 kept findings:

- `2024-09-11-agave-transaction-processing-f0a77e94bf.md`
- `2024-11-07-agave-consensus-f621667cd1.md`
- `2025-03-10-agave-cryptography-b30fb49ad2.md`
- `2025-08-07-agave-storage-eeb36c56b7.md`
- `2025-10-15-agave-p2p-networking-589d58b07f.md`
- `2025-12-27-agave-cryptography-346847efe6.md`
- `2026-01-09-agave-consensus-8cebdeb9b0.md`
- `2026-03-16-agave-consensus-be02fe6ee0.md`
- `2026-04-01-agave-transaction-processing-7796a7bca1.md`
- `2026-04-08-agave-consensus-9021f430fb.md`
- `2026-04-20-agave-transaction-processing-b9365a82f6.md`
- `2026-04-27-agave-validator-ops-7b7ffdd747.md`
- `2026-04-30-agave-cryptography-26af74dd48.md`
- `2026-05-07-agave-transaction-processing-775558cbef.md`

No findings were skipped.

## Finding-To-Mechanism Analysis

### Durable Nonce Rollback Preserved Stale Replay State

Finding: `2024-09-11-agave-transaction-processing-f0a77e94bf`

Repo-specific mechanism: durable nonce fallback and rollback account construction could preserve old nonce data while fee/rent effects were retained.

Generic invariant: once replay-protection state enters fee-paying processing, rollback must not restore a reusable pre-consumption coordinate.

Missing property: rollback-state atomicity for replay protection.

Code shape: early nonce handling plus later rollback account construction that can combine new fee side effects with old nonce data.

Hunt recipe: for nonce/sequence/ticket paths, trace stale, duplicate, too-new, fee-only, failed execution, and rollback paths. Ask whether rejection after charging fees still consumes the replay coordinate.

False-positive killers: a final execution boundary always advances nonce before rollback capture; or rollback cannot run for nonce transactions; or a later mandatory state check prevents reuse.

### Unsigned Constructor Exposed For Signed Gossip Metadata

Finding: `2024-11-07-agave-consensus-f621667cd1`

Repo-specific mechanism: production code exposed an unsigned CRDS value constructor even though normal CRDS values are expected to be signed.

Generic invariant: production constructors for authenticated network artifacts should make unauthenticated construction impossible or test-only.

Missing property: authenticated construction.

Code shape: signed type with parallel signed and unsigned constructors, where unsigned construction is not type- or visibility-restricted.

Hunt recipe: find signed/certified/gossip object constructors; compare production constructors with test helpers and insertion/broadcast sinks.

False-positive killers: unsigned helpers are private/cfg(test); every sink verifies before use; the type never crosses a network or consensus boundary.

### Remove-Then-Continue Missing In Transaction Buffer

Finding: `2025-03-10-agave-cryptography-b30fb49ad2`

Repo-specific mechanism: invalid transaction removal from an indexed container fell through to an `expect` path that assumed the removed transaction still existed.

Generic invariant: after removing untrusted work from an indexed container, the current iteration must not dereference that removed item.

Missing property: post-removal control-flow isolation.

Code shape: `remove_by_id`/delete on invalid input followed by later infallible lookup in the same loop iteration.

Hunt recipe: search packet/mempool/buffer loops for removal branches that lack `continue`/`return` before later `unwrap`/`expect`/indexing.

False-positive killers: lookup is optional; path is not attacker-influenced; or later code cannot run after removal.

### Resource Bounds Derived From Abstract Limit Instead Of Concrete Input

Finding: `2025-08-07-agave-storage-eeb36c56b7`

Repo-specific mechanism: snapshot/genesis unpack buffers were sized from apparent unpacked-size limits and a minimum, not from the actual archive input size.

Generic invariant: temporary resource allocation for archive/unpack paths should be bounded by the smallest concrete relevant input and policy limit.

Missing property: allocation bound by concrete input.

Code shape: configured output limit or minimum allocation drives buffer size for potentially small or attacker-influenced archives.

Hunt recipe: inspect archive, snapshot, state-sync, and decompression code for allocation formulas that ignore actual compressed input size.

False-positive killers: archive source is fully trusted; separate hard cap is low enough; change is only throughput tuning.

### Non-Consuming Rate-Limit Checks At Admission

Finding: `2025-10-15-agave-p2p-networking-589d58b07f`

Repo-specific mechanism: QUIC admission used allowance-style checks where token consumption/order was the real admission property.

Generic invariant: a remote request that proceeds into costly work must consume global and peer-specific admission budget at that boundary.

Missing property: admission token consumption.

Code shape: `is_allowed`-style checks, later registration, and pre-handshake work are not ordered around token consumption.

Hunt recipe: trace every connection/session/message admission path and mark where budget is queried, consumed, released, and charged on reject.

False-positive killers: another mandatory consume gate precedes work; lower layers enforce identical budget; path is not remotely reachable.

### Durable Nonce State Validated Too Early

Finding: `2025-12-27-agave-cryptography-346847efe6`

Repo-specific mechanism: durable nonce execution state was built during bank transaction-age checking instead of reloading/revalidating current account state in SVM processing.

Generic invariant: mutable replay-protection state and authority must be revalidated at the execution sink, not only at early admission.

Missing property: fresh-state revalidation.

Code shape: early construction of sensitive state object reused after possible account lifecycle/authority changes.

Hunt recipe: for nonce/sequence/ticket/auth state, compare preflight/admission checks with the final execution object consumed by the sink.

False-positive killers: locks make the state immutable; execution revalidates anyway; early object is only a hint.

### Authorized Vote Signer Missing Before Vote-State Mutation

Finding: `2026-01-09-agave-consensus-8cebdeb9b0`

Repo-specific mechanism: vote storage checked stake presence but not current epoch authorized-voter mapping before latest-vote state mutation.

Generic invariant: consensus vote buffering must verify the active role signer before any state mutation derived from the vote.

Missing property: current-epoch vote authorization.

Code shape: broad eligibility check (stake/account exists) before a sink requiring exact active signer.

Hunt recipe: for vote, committee, and attestation ingestion, distinguish signer validity, active role membership, epoch mapping, stake, and mutation sink.

False-positive killers: authorization is checked before any state mutation; the mutated state is diagnostic only; lower layer rejects before reachability.

### Independent Validation Results Combined With OR Semantics

Finding: `2026-03-16-agave-consensus-be02fe6ee0`

Repo-specific mechanism: ReplayStage combined replay and verification `Result`s with disjunctive semantics so one success could mask the other failure.

Generic invariant: independent validations that jointly guard a consensus decision must require all required branches to succeed.

Missing property: conjunctive error propagation.

Code shape: `Result::or`, `any success`, or first-success aggregation before dead-slot/failure handling.

Hunt recipe: find aggregation of multiple validators, async workers, or check results before consensus state mutation; classify whether any or all are required.

False-positive killers: branches are true alternatives; result only affects logging; another mandatory check handles either failure.

### Canonical Transaction Sanitizer Missing From Sigverify

Finding: `2026-04-01-agave-transaction-processing-7796a7bca1`

Repo-specific mechanism: sigverify manually parsed transaction layout before the canonical sanitized transaction view gate.

Generic invariant: untrusted transaction bytes should be canonically parsed/sanitized before signature-path offsets, versions, and lengths are trusted.

Missing property: canonical parse before verification.

Code shape: duplicated/ad hoc byte parser in a sensitive verifier path instead of shared canonical sanitizer.

Hunt recipe: compare packet verification, mempool admission, replay, and execution parsers; flag weaker duplicate parsers at earlier security sinks.

False-positive killers: canonical sanitizer is guaranteed upstream; parser rejects equivalently; malformed packet never reaches a sink.

### Sigverify In-Flight Accounting Missing At Capacity Boundary

Finding: `2026-04-08-agave-consensus-9021f430fb`

Repo-specific mechanism: packet verifier pipeline lacked shared in-flight capacity accounting and over-capacity drops at the receive/verify/send boundary.

Generic invariant: async verification pipelines must account for in-flight work and backpressure/drop before capacity is exceeded.

Missing property: in-flight capacity accounting.

Code shape: verifier capacity, async send, and receive loop have split ownership over admission and release.

Hunt recipe: inspect async verifier/worker pools for one shared counter or permit spanning receive, worker enqueue, completion, send, and error paths.

False-positive killers: bounded channel enforces capacity first; accounting is metrics-only; input is trusted or independently rate-limited.

### Transaction View Structural Invariants Centralized Late

Finding: `2026-04-20-agave-transaction-processing-b9365a82f6`

Repo-specific mechanism: transaction-view sanitization was incomplete or dispersed across size, signatures, accounts, headers, config, and lookups.

Generic invariant: a transaction view should be rejected at construction/sanitize time if any structural field violates protocol bounds.

Missing property: complete transaction-structure sanitization.

Code shape: multiple representations of transaction structure with version-specific limits and duplicate-address semantics enforced unevenly.

Hunt recipe: build a matrix of raw bytes, transaction view, sanitized transaction, loaded accounts, compiled instructions, and execution frame.

False-positive killers: equivalent checks already run for every constructor; malformed input cannot reach this view; change is comments only.

### CLI Metadata Parser Dropped Signer Bit

Finding: `2026-04-27-agave-validator-ops-7b7ffdd747`

Repo-specific mechanism: validator-info parser did not carry the validator pubkey signer flag into selection/display logic and used brittle parsing on malformed accounts.

Generic invariant: authenticity metadata produced during parsing must travel to the downstream trust decision.

Missing property: signer-bit propagation.

Code shape: parser returns identity and metadata but drops the boolean/authentication evidence that says whether the identity signed.

Hunt recipe: for operator tools, map parse output fields to later selection/publish/display decisions; check that authenticity flags are not discarded.

False-positive killers: output is clearly unauthenticated; signer is checked later; tool output cannot influence operations.

### Recovered Consensus Data Skipped Direct-Receive Rule

Finding: `2026-04-30-agave-cryptography-26af74dd48`

Repo-specific mechanism: recovered shreds had a separate path where a feature-gated data-complete rule was not shown as applied consistently.

Generic invariant: recovered/reconstructed consensus data must satisfy the same protocol rules as directly received data before insertion.

Missing property: consistent recovered-data validation.

Code shape: direct ingress validator and recovery/reconstruction path use different context objects or rule coverage.

Hunt recipe: compare direct receipt, repair, recovery, replay, and blockstore insertion for the same consensus object.

False-positive killers: recovered data always re-enters the same validator; rule intentionally excludes recovered objects; path is test-only.

### Format-Specific Parser Bounds And Helper Cache Domain

Finding: `2026-05-07-agave-transaction-processing-775558cbef`

Repo-specific mechanism: txv1 parsing/static account counts and helper-cache size did not clearly match the accepted `u8` program-id index domain.

Generic invariant: parser bounds and fixed helper caches must match the exact format and index domain accepted from untrusted bytes.

Missing property: format-specific index bounds.

Code shape: ambiguous max constant plus fixed array indexed by attacker-shaped `u8` values.

Hunt recipe: inspect versioned transaction parsers for constants that differ by format, then follow indexes into fixed arrays/caches.

False-positive killers: old constants are equivalent; all indexing is fallible and converted to parse errors; malformed input cannot reach parser.

## Family Clustering

### Cluster A: Replay-sensitive state across admission, execution, and rollback

Findings:

- `2024-09-11` durable nonce consumption
- `2025-12-27` nonce state validation timing

Why grouped: both involve nonce/replay coordinates whose security depends on when state is consumed, reloaded, and preserved across failure/rollback.

Portability: high. Nonce, sequence, ticket, reservation, and replay-coordinate systems occur across account-ledger and mempool designs.

### Cluster B: Canonical boundary validation across duplicate representations and alternate paths

Findings:

- `2026-04-01` sigverify canonical sanitizer
- `2026-04-20` transaction-view sanitization
- `2026-05-07` txv1 bounds/OOB
- `2026-04-30` recovered shreds

Why grouped: all compare a canonical object/rule against duplicate parser, recovery, compatibility, or versioned path.

Portability: high. Every DLT has admission/replay/recovery variants of block, tx, proof, or message validation.

### Cluster C: Resource admission must consume, reserve, or release at the real boundary

Findings:

- `2025-08-07` archive unpack buffer sizing
- `2025-10-15` QUIC token consumption
- `2026-04-08` sigverify in-flight accounting

Why grouped: all are resource-control hardening where the suspicious shape is accounting based on the wrong object, wrong time, or split ownership.

Portability: high. Applies to p2p, RPC, sync, archive, verifier, and worker-pool surfaces.

### Cluster D: Authenticated artifact construction and signer-scope propagation

Findings:

- `2024-11-07` unsigned CRDS constructor
- `2026-01-09` vote authorized-voter filtering
- `2026-04-27` validator-info signer bit in CLI

Why grouped: all separate cryptographic/signer existence from the exact signer scope or authenticity evidence used at a sink.

Portability: high, but CLI metadata case is lower severity/operator-local.

### Cluster E: Failure semantics and destructive control-flow hardening

Findings:

- `2025-03-10` remove-then-expect panic
- `2026-03-16` `Result::or` masks validation failure

Why grouped: both are control-flow bugs where a failure/removal signal is not preserved to the later security decision.

Portability: medium-high. Specific syntax differs by language, but the shape is common in async pipelines, caches, and indexed buffers.

## Prompt-Pack Comparison

### Cluster A

Affected files:

- `00_protocol_mapper.md`
- `01_base_hunter.md`
- `prompts/15_state_machine_and_lifecycle_consistency.md`
- `prompts/22_ledger_accounting_and_invariant_coverage.md`

Current coverage: base hunter already mentions nonce, replay-sensitive paths, early side effects, and rollback. Prompt 15 mentions stale lifecycle/nonce state. Prompt 22 mentions rejected/aborted transactions with fees.

Gap: no concise recipe requires auditors to build a timeline for replay-coordinate state across fee charging, failure, rollback, and final execution. Current language is broad enough to include this but may not pull durable-nonce bugs forward.

Decision: refine existing prompts, no new family.

### Cluster B

Affected files:

- `01_base_hunter.md`
- `prompts/13_input_validation_and_invariant_enforcement.md`
- `prompts/19_consensus_fork_and_payload_rule_validation.md`
- `prompts/24_memory_contract_and_buffer_ownership.md`

Current coverage: prompt 13 is strong on duplicate parsers, canonical parsers, exact lengths, and transaction representations. Prompt 19 covers replay/recovery/compatibility paths. Prompt 24 covers fixed capacity and parser buffers.

Gap: the prompt pack should more explicitly ask for an "ingress-equivalence matrix" for the same object across direct receipt, sigverify/preverify, replay, recovery, and versioned parser paths, including helper caches indexed by parsed fields.

Decision: refine prompt 13 and 19, and add one specific parser/cache line to prompt 24. No new family.

### Cluster C

Affected files:

- `prompts/14_resource_accounting_and_limits.md`
- `01_base_hunter.md`
- `prompts/21_peer_sync_progress_and_response_binding.md`

Current coverage: prompt 14 already covers admission, rate limit, pre-auth connection limits, invalid paths, in-flight work, and decompression boundaries.

Gap: current prompt has the ingredients but not the explicit "query vs consume vs release" lifecycle for token buckets/permits, nor "allocation formula must be based on the minimum concrete input bound" for archive/resource paths.

Decision: refine prompt 14; optionally add a protocol-mapper inventory item for quota lifecycle.

### Cluster D

Affected files:

- `prompts/10_authz_and_role_gates.md`
- `prompts/11_signature_binding_and_signer_scope.md`
- `00_protocol_mapper.md`

Current coverage: prompts already distinguish signer authorization from signature verification and active roles. There is good coverage for "is member" vs "is selected signer".

Gap: two small refinements: signed object constructors should encode authenticity in the type/interface, and parser-produced authenticity flags must be carried to the downstream trust decision.

Decision: refine prompts 10 and 11. Do not add a CLI-specific prompt.

### Cluster E

Affected files:

- `01_base_hunter.md`
- `02_validation_and_impact.md`
- `prompts/13_input_validation_and_invariant_enforcement.md`
- `prompts/19_consensus_fork_and_payload_rule_validation.md`

Current coverage: prompt 13 covers panics and prompt 19 covers collapsing invalid errors into generic errors.

Gap: neither prompt strongly calls out boolean/Result aggregation shape: independent required checks combined with OR/any-success semantics. Prompt 13 covers remove/panic generally but not "destructive mutation then same-iteration infallible lookup".

Decision: refine prompt 13 and 19. No new family.

## Proposed Prompt Changes

### Change 1: Protocol Mapper - replay/resource lifecycle inventory

Target: `/testing/dlt-ai-audit-system/00_protocol_mapper.md`

Add after current transaction admission mapping item 18:

```text
For every replay-sensitive coordinate such as nonce, sequence, ticket, reservation, vote freshness, or local pending state, build a lifecycle timeline across admission, fee/resource charging, execution, failure, rollback, replay, and cleanup. Identify where the coordinate is consumed or reserved, where it is reloaded from authoritative state, and which failure paths must preserve the consumed state instead of restoring the pre-admission value.

For every quota, token bucket, permit, in-flight counter, archive/decompression buffer, and worker-pool budget, map query, consume/reserve, release, drop, and error paths separately. Distinguish "is allowed" checks from checks that actually consume capacity, and note whether allocation formulas use concrete input size, declared output size, configured limits, or the minimum of those bounds.
```

Rationale: improves transferability by forcing an artifact lifecycle map, not naming durable nonce, QUIC, or sigverify.

Repo-specific details excluded: Agave nonce account, QUIC, shreds, and exact file names.

Overfitting risk: low; applies to mempools, txpools, peer admission, sync, proof, and archive systems.

### Change 2: Base Hunter - ingress equivalence and failure aggregation

Target: `/testing/dlt-ai-audit-system/01_base_hunter.md`

Add after item 3a:

```text
For each security-sensitive object type, build an ingress-equivalence matrix across direct network receipt, local construction, preverification, canonical admission, replay, recovery, repair, simulation, compatibility, and version-specific parser paths. Mark the canonical validator and list every field, flag, feature gate, size/count bound, and helper-cache index domain that must be identical before the shared sink.
```

Add after item 26:

```text
Search for independent validation results that are aggregated before a state mutation, vote, dead-marker, queue insertion, or success response. Classify whether the protocol requires all checks to pass or only one alternative to pass. Treat `any success`, `or`, first-success, nil-on-one-branch, and generic-error collapse as suspicious when the checks validate different required properties.
```

Rationale: would have helped surface sigverify/sanitizer/recovery/parser cases and the ReplayStage result aggregation case.

Repo-specific details excluded: transaction view, shreds, ReplayStage names.

Overfitting risk: low; exact same concept covers block import, proof validation, bridge messages, and p2p pipelines.

### Change 3: Input Validation - canonical parser and destructive invalid-input control flow

Target: `/testing/dlt-ai-audit-system/prompts/13_input_validation_and_invariant_enforcement.md`

Add under Search patterns:

```text
- Security-sensitive preverification paths that duplicate canonical parsing with manual offset, count, version, or length logic. Compare packet-level preverify, mempool admission, execution, replay, and simulation parsers; the earliest sink should either call the canonical sanitizer or reject every unsupported version, trailing byte, count, duplicate identity, and malformed length equivalently.
- Versioned transaction, message, block, or proof parsers whose accepted count or index domain differs from downstream fixed arrays, bitsets, caches, or helper filters. A parser that accepts an index type such as `u8` should prove every possible accepted value is either rejected before indexing or covered by the helper storage.
- Invalid-input branches that delete, evict, remove, or mark the current object as bad and then continue through the same loop iteration. After destructive removal, later code must not `unwrap`, `expect`, index, or mutate state under the assumption that the object still exists.
```

Rationale: strengthens existing generic parser guidance with two concrete portable shapes: duplicate preverify parsers and destructive invalid-input fallthrough.

Repo-specific details excluded: Agave txv1, account keys, exact constants.

Overfitting risk: medium-low; the `u8` phrase is illustrative but generic. Could be rewritten as "small integer index type" if desired.

### Change 4: Resource Accounting - consume/release lifecycle and concrete allocation bounds

Target: `/testing/dlt-ai-audit-system/prompts/14_resource_accounting_and_limits.md`

Add under Search patterns:

```text
- Token-bucket, permit, semaphore, and in-flight accounting paths where an admission check asks whether work is allowed but does not consume or reserve capacity before the work continues. Trace successful admission, early rejection, timeout, worker enqueue, send/forward, and error cleanup; every path should consume and release the same authoritative resource state.
- Archive, snapshot, state-sync, proof, or compressed-input handlers that size temporary buffers from an abstract output limit, configured maximum, or fixed minimum while ignoring the concrete input size already known at the boundary. Allocation should be capped by the smallest relevant trusted bound unless the protocol explicitly requires preallocation.
- Async verifier or worker-pool pipelines where receive, verify, forward, and completion are owned by different tasks. Check that one shared in-flight budget covers the whole lifetime and that over-capacity input is dropped before enqueueing new work.
```

Rationale: makes the resource prompt more operational for p2p/token bucket and archive/decompression findings.

Repo-specific details excluded: QUIC, sigverify, snapshot constants.

Overfitting risk: low; applies broadly across node services.

### Change 5: Authz/Signer - exact role at mutation sink and parser authenticity propagation

Target: `/testing/dlt-ai-audit-system/prompts/10_authz_and_role_gates.md`

Add under Search patterns:

```text
- consensus, staking, vote, committee, or attestation buffers that first check broad eligibility such as account existence, stake presence, membership, or syntactic signature validity, then mutate latest-state, cached vote state, scheduling state, or fork-choice inputs before checking the exact active signer or role for the current epoch, round, view, or authority map.
- parsers for identity or metadata records that produce both content and authenticity evidence, such as signer-present, owner-verified, proof-verified, or source-verified flags. Verify the downstream display, publish, update, reuse, or selection decision consumes the authenticity flag and does not trust only the parsed identity.
```

Rationale: strengthens vote authorization and operator-metadata trust decisions without naming Agave roles.

Repo-specific details excluded: authorized voter, validator-info.

Overfitting risk: low; applies to validator registries, operator tools, bridge metadata, committees.

### Change 6: Signature Binding - authenticated constructors

Target: `/testing/dlt-ai-audit-system/prompts/11_signature_binding_and_signer_scope.md`

Add under Search patterns:

```text
- signed, certified, or authenticated network object types that expose production constructors or builders which can create unauthenticated/default-signature instances. Test helpers for unsigned construction should be private or test-only, and production insertion/broadcast APIs should accept only authenticated wrappers or force signing at construction.
```

Rationale: catches API-level authenticity footguns before looking only at verifier call sites.

Repo-specific details excluded: CRDS.

Overfitting risk: low; common in gossip, consensus, bridge, manifest, checkpoint, and validator-list object types.

### Change 7: State Machine Lifecycle - replay-coordinate rollback

Target: `/testing/dlt-ai-audit-system/prompts/15_state_machine_and_lifecycle_consistency.md`

Add under Search patterns:

```text
- replay-protection coordinates such as nonces, sequences, tickets, reservations, or pending vote markers that are advanced, reserved, or consumed before a transaction or message is fully successful. Compare fee-only, failed, aborted, rollback, retry, and replay paths; preserving fees or other side effects while restoring the old replay coordinate is high signal.
- early construction of execution-state objects from mutable accounts, registry entries, epoch authority maps, or lifecycle-controlled state. If the object can change before execution or dequeue, reload and revalidate it at the sink rather than trusting the admission-time object.
```

Rationale: converts the durable nonce lessons into a general state-machine hunt.

Repo-specific details excluded: Solana/Agave nonce account internals.

Overfitting risk: low; applies to sequence numbers, tickets, retryables, vote freshness, bridge messages.

### Change 8: Consensus Validation - recovered object path equivalence and result aggregation

Target: `/testing/dlt-ai-audit-system/prompts/19_consensus_fork_and_payload_rule_validation.md`

Add under Search patterns:

```text
- Recovered, repaired, reconstructed, erasure-decoded, or locally regenerated consensus objects that reach the same storage or replay sink as directly received objects. They should run the same feature-gated, fork-gated, metadata, completeness, parentage, and commitment checks unless the protocol explicitly defines a narrower exception.
- Multiple asynchronous or staged consensus validators whose results are merged before marking data valid, dead, duplicate, voteable, or safe. If the properties are independently required, failure from any branch must fail closed and must not be masked by success from another branch.
```

Rationale: covers recovered shreds and ReplayStage-style aggregation in portable language.

Repo-specific details excluded: shred, data-complete flag, ReplayStage.

Overfitting risk: low; applies to block recovery, erasure coding, repair, state sync, and staged import validation.

### Change 9: Memory Contract - parser index domains

Target: `/testing/dlt-ai-audit-system/prompts/24_memory_contract_and_buffer_ownership.md`

Add under Search patterns:

```text
- fixed arrays, bitsets, filters, or caches indexed by attacker-controlled parser fields where the parser's accepted numeric domain is wider than the helper storage. Bounds must be format-specific and enforced before indexing, not inferred from a different transaction, message, or protocol version.
```

Rationale: catches tx/parser OOB-style findings in memory-safe and memory-unsafe languages.

Repo-specific details excluded: txv1 and program-id index.

Overfitting risk: low.

### Change 10: Validation And Impact - hardening evidence subtypes

Target: `/testing/dlt-ai-audit-system/02_validation_and_impact.md`

Add under the hardening-only guidance:

```text
For parser, recovery, and resource-hardening findings, explicitly classify which proof is missing:
- missing reachability: old behavior is bad if reached, but attacker control is unproven;
- missing consequence: attacker-controlled input reaches the boundary, but impact beyond rejection/hardening is unproven;
- duplicate-check uncertainty: patch centralizes or duplicates validation, but old equivalent checks may have existed elsewhere;
- operator-local hardening: the trust decision is real but affects CLI, monitoring, or tooling rather than protocol state.
```

Rationale: Agave had many likely/security-hardening cases where phase 4 correctly kept the lesson but rejected strong impact claims. This text preserves that discipline.

Repo-specific details excluded: exact findings.

Overfitting risk: low; useful for all corpus-driven hardening.

## New Family Prompts

No new prompt family is justified.

Reasons:

- Replay/rollback belongs in state-machine lifecycle and ledger accounting.
- Canonical parser and recovery path equivalence belongs in input validation and consensus validation.
- Resource admission belongs in resource accounting and peer sync.
- Signer/authenticity propagation belongs in authz and signature binding.
- Error aggregation belongs in consensus validation and base hunter.

Adding a new "transaction sanitizer" or "Solana-style pipeline" family would overfit to Agave's implementation.

## Validation Notes

Holdout check:

- I treated the `2026-05-07` txv1 OOB/bounds finding and `2026-04-27` validator-info CLI finding as holdouts while drafting the cluster-level wording.
- The proposed parser/index-domain additions to prompts 13 and 24 would still lead an auditor toward the txv1 bounds case without naming txv1 or the exact constants.
- The proposed parser-authenticity propagation addition to prompt 10 would still lead an auditor toward the CLI signer-bit case without mentioning validator-info.

Remaining doubts:

- Several Agave findings are hardening-only with uncertain exploitability. They justify prompt refinements only because they cluster with multiple portable mechanisms.
- The prompt pack is already broad; adding too many bullets risks prompt fatigue. The highest-value edits are Changes 2, 3, 4, 5, and 8.
- The archive buffer-sizing finding is weaker than the rest and could remain corpus-only if the prompt pack needs to stay lean.

Prompts that should stay unchanged for this evidence set:

- `12_attestation_trust_and_freshness.md`
- `16_staking_registry_and_accountability.md`
- `17_checked_arithmetic_and_parameter_bounds.md`
- `18_authoritative_state_and_boundary_enforcement.md`
- `20_authenticated_state_proof_and_persistence_integrity.md`
- `21_peer_sync_progress_and_response_binding.md` except indirectly via resource-accounting overlap
- `22_ledger_accounting_and_invariant_coverage.md` except optional nonce/rollback cross-reference
- `23_zk_circuit_witness_and_public_data_binding.md`

## Priority Recommendation

If only a small patch is desired, apply these five first:

1. Base Hunter ingress-equivalence matrix and validation-result aggregation.
2. Input Validation duplicate preverify parser plus destructive invalid-input fallthrough.
3. Resource Accounting consume/release lifecycle and concrete allocation bounds.
4. Authz exact active role before mutation plus authenticity-flag propagation.
5. Consensus Validation recovered-object equivalence and staged-result aggregation.
