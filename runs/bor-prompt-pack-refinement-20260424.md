# Bor Prompt-Pack Refinement

Target repo: `/testing/bor`

Evidence folder: `/testing/bor/validated-findings/kept`

Date: 2026-04-24

## Repo Context Summary

Bor is Polygon PoS's Go execution client, forked from go-ethereum. Its distinctive security shape is not just normal Ethereum execution: it has Bor PoA consensus in `consensus/bor`, Heimdall-derived validator/span/milestone/state-sync inputs, sprint-based block production, state-sync system transactions during finalization, BlockSTM/parallel execution, downloader and witness sync paths, JSON-RPC filters/tracing, txpool subpools, fork schedules in `params`, and canonical state/persistence code under `core`, `trie`, `ethdb`, and `core/rawdb`.

Important trust boundaries:

- Peer network to local sync state: discovery, downloader, header/body/witness fetch, tx announcement, required-block and fork-id checks.
- Heimdall to Bor consensus: spans, validator sets, milestones, checkpoints, state-sync events, no-ack state, and time/height queries.
- RPC user to node resources or signing state: `eth_sign`, transaction submission, filters/logs, tracing, fee history, admin/mining APIs.
- Consensus block/header/body to canonical state: `VerifyHeader(s)`, `Finalize`, `FinalizeAndAssemble`, state processors, fork-choice, state-sync transaction/receipt accounting.
- Storage/cache to authenticated state: trie roots, chunk/content-address checks, journal/revert semantics, root-hash APIs, forkchoice/canonical DB state.

High-risk entrypoints:

- `consensus/bor/bor.go`: header validation, state-sync, finalization, validator/sprint checks.
- `core/state_processor.go` and `core/parallel_state_processor.go`: equivalent serial/parallel execution and finalization sinks.
- `eth/downloader/*`: peer-driven chain/witness/header sync and milestone whitelist state.
- `eth/filters/api.go`, `eth/tracers/*`, `internal/ethapi/*`: expensive RPC and tracing paths.
- `core/txpool/*`: subpool admission and shared sender/authority resources.
- `core/blockchain.go`, `core/forkchoice.go`, `consensus/bor/api.go`: canonical head, reorg, root range, and verifier maintenance decisions.

## Finding Inventory

Analyzed all 75 markdown findings in `/testing/bor/validated-findings/kept`. No files were skipped.

Compact inventory by mechanism:

- Consensus/fork/finalization validation: `2014-11-12-bor-transaction-processing-60cdb1148`, `2015-01-13-bor-transaction-processing-82beaabf6`, `2017-05-12-bor-transaction-processing-a5f6a1cb7`, `2019-01-24-bor-transaction-processing-c7664b063`, `2021-12-04-bor-transaction-processing-a7d97ce58`, `2022-06-29-bor-cryptography-d12b1a91c`, `2022-12-20-bor-transaction-processing-b818e73ef`, `2023-03-13-bor-transaction-processing-d0a9e0db2`, `2024-04-30-bor-cryptography-bd8fe6260`, `2025-05-22-bor-transaction-processing-20ad4f500`, `2025-11-28-bor-cryptography-544e6b7c7`, `2025-12-02-bor-cryptography-647b061a9`, `2026-01-26-bor-transaction-processing-2641b6be6`, `2026-02-26-bor-cryptography-b69ad46c1`, `2026-04-13-bor-transaction-processing-bc8857fc8`, `2026-04-16-bor-transaction-processing-11ecb6aa7`.
- Heimdall, validator-set, and external-consensus snapshot binding: `2019-09-25-bor-storage-48c074596`, `2020-05-13-bor-cryptography-0f8d3b100`, `2020-05-17-bor-rpc-client-api-868dc81c8`, `2023-03-21-bor-storage-d53c1ec21`, `2025-06-30-bor-cryptography-94f2beea9`, `2025-09-08-bor-consensus-abe386cf7`, `2026-03-25-bor-rpc-client-api-7e59d7195`.
- Peer sync, discovery, and response binding: `2015-01-19-bor-p2p-networking-e252c634c`, `2015-03-25-bor-cryptography-de7af720d`, `2015-05-14-bor-transaction-processing-a4246c2da`, `2015-05-15-bor-core-logic-5c1a7b965`, `2015-05-15-bor-core-logic-cd2fb0905`, `2015-05-21-bor-core-logic-52db6d8be`, `2015-07-01-bor-p2p-networking-d6f2c0a76`, `2016-11-28-bor-p2p-networking-e949a2ed2`, `2018-02-12-bor-p2p-networking-9123eceb0`, `2022-05-04-bor-p2p-networking-ecae8e4f6`, `2024-08-21-bor-p2p-networking-f88af2000`, `2025-04-14-bor-p2p-networking-c5c75977a`, `2025-10-01-bor-storage-83ab606c4`, `2026-01-27-bor-rpc-client-api-df8f2a879`.
- Authenticated state, persistence, reorg, and canonical-anchor consistency: `2016-11-24-bor-storage-12d654a6f`, `2017-02-13-bor-storage-e23e86921`, `2017-08-25-bor-storage-08f27428b`, `2018-09-20-bor-storage-d6254f827`, `2023-01-03-bor-storage-fcf3d0048`, `2023-07-04-bor-storage-0f9d7d61c`, `2023-10-19-bor-consensus-a9c57370c`, `2024-09-05-bor-transaction-processing-8262eae9e`, `2025-02-03-bor-storage-a34426824`, `2026-01-27-bor-transaction-processing-0850faf21`, `2026-02-25-bor-storage-752f43932`.
- Resource accounting and bounded work: `2015-03-20-bor-cryptography-d8fe8f60e`, `2019-03-12-bor-transaction-processing-7504dbd6e`, `2022-05-23-bor-transaction-processing-ba47d800b`, `2022-12-06-bor-p2p-networking-50a778207`, `2023-01-11-bor-transaction-processing-793f0f9ec`, `2023-03-28-bor-transaction-processing-fd94b4fcf`, `2024-05-07-bor-transaction-processing-e4b8058d5`, `2025-04-08-bor-transaction-processing-2e739fce5`, `2026-02-18-bor-transaction-processing-bff847a3d`, `2026-03-18-bor-transaction-processing-70f86c4d2`, `2026-03-18-bor-transaction-processing-858c6ae6d`, `2026-03-18-bor-transaction-processing-b1829ef95`, `2026-03-19-bor-transaction-processing-7d6a68d8b`.
- Signature, signer scope, replay, and signing trust boundaries: `2016-10-28-bor-transaction-processing-b59c8399f`, `2018-09-25-bor-cryptography-d3441ebb5`, `2020-12-04-bor-transaction-processing-15339cf1c`, `2020-12-08-bor-transaction-processing-ed0670cb1`, `2021-02-23-bor-transaction-processing-142fbcfd6`, `2021-04-06-bor-transaction-processing-706683ea7`, `2021-12-15-bor-cryptography-a10f79dc2`, `2021-12-15-bor-cryptography-e2b938562`, `2022-05-23-bor-rpc-client-api-1b5304405`, `2026-02-17-bor-cryptography-d9fac7a4c`.

## Family Clustering And Mechanisms

### Cluster A: External Consensus Snapshot Determinism

Findings: `2020-05-13`, `2020-05-17`, `2023-03-21`, `2025-06-30`, `2025-09-08`, `2026-03-25`, plus parts of `2019-09-25`.

Mechanism: Bor makes consensus decisions from Heimdall-derived state. Bugs appear when validator sets, state-sync events, milestones, checkpoint locks, or signer snapshots are read from an implicit "latest" or fallback source instead of one canonical snapshot boundary matching the Bor block, sprint, span, or cutoff timestamp.

Portable lesson: Any execution client that consumes external consensus-client or bridge-client data needs snapshot identity binding: time alone, height alone, local latest, or retry fallback is not enough if multiple validators can observe different external views.

Existing coverage: `12_attestation_trust_and_freshness.md`, `18_authoritative_state_and_boundary_enforcement.md`, and `19_consensus_fork_and_payload_rule_validation.md` cover parts of this, but none explicitly names external-consensus oracle reads as consensus inputs requiring deterministic snapshot coordinates.

### Cluster B: Fail-Closed Finalization And Equivalent Execution Paths

Findings: `2020-05-17`, `2021-12-04`, `2026-01-26`, `2026-04-13`, `2026-04-16`, plus `2024-09-05`.

Mechanism: Finalization, state-sync system transactions, receipt counts, genesis effects, and state reads can fail open when an interface lacks an error channel, callers ignore the error, or serial and parallel processors do not enforce the same invariant.

Portable lesson: Consensus-sensitive helpers should return explicit semantic failure, and every equivalent processing path should propagate it before committing state or reporting success.

Existing coverage: `19` has error-classification text, `13` has general invariant enforcement, and `01` asks for equivalent path comparison. This cluster suggests strengthening "finalization/post-execution sinks" specifically.

### Cluster C: Peer Response Binding, Progress, And Peer Feedback

Findings: `2015-03-25`, `2015-05-14`, `2015-05-15` x2, `2015-05-21`, `2015-07-01`, `2018-02-12`, `2024-08-21`, `2025-10-01`, `2026-01-27`.

Mechanism: Peer-driven paths accepted partial context: block hash without exact parent, pong without exact ping, claimed stronger chain without actual header progress, witness page counters without consistency checks, or non-terminal duplicate responses without progress feedback.

Portable lesson: A response should satisfy the exact request context and advance a tracked local state machine, and invalid/empty/zero-progress cases should update penalties or stop scheduling work.

Existing coverage: `21_peer_sync_progress_and_response_binding.md` already captures this well. It should add termination/stronger-chain checks and reflection/bonding gates.

### Cluster D: Canonical Anchor, Reorg, And Persistence Identity

Findings: `2016-11-24`, `2017-02-13`, `2018-09-20`, `2023-01-03`, `2023-10-19`, `2025-02-03`, `2026-02-25`.

Mechanism: State or forkchoice decisions were keyed by weak coordinates: current tip instead of range end, number instead of hash/parent relation, any queued parent instead of expected parent, random equal-score tie-break, or content-address key without recomputation.

Portable lesson: For canonical state, the governing identity is usually a tuple: hash, number, parent, root, fork, range, finality status, and source chain status. Prompts should push auditors to check the exact tuple.

Existing coverage: `18`, `19`, and `20` cover much of this. `20` should more explicitly ask about range APIs and reorg-stability anchors, not only caches/checkpoints.

### Cluster E: Resource Budgets Across All Dimensions And Entrypoints

Findings: `2015-07-01`, `2019-03-12`, `2022-05-23`, `2023-03-28`, `2024-05-07`, `2025-04-08`, `2025-05-22`, `2026-02-18`, and the four March 2026 filter range findings.

Mechanism: Bounds existed on one dimension or one path but not all: block count but not reward percentile count, txpool subpool but not shared authority/sender, header verifier start point but not full range, RPC range check missing in replay/Bor-specific paths, symbolic selectors not normalized before budget arithmetic, JS/native tracer memory paths diverging.

Portable lesson: Resource checks must cover all equivalent entrypoints, all cost dimensions, and the same normalized coordinates the expensive sink will use.

Existing coverage: `14_resource_accounting_and_limits.md` is strong but should add symbolic range normalization and background verifier/work-window anchoring.

### Cluster F: Fork-Specific Encoding, Numeric Width, And Replay Domains

Findings: `2016-10-28`, `2020-12-08`, `2021-02-23`, `2021-04-06`, `2021-12-15` x2, `2024-04-30`, `2025-11-28`, `2025-12-02`, `2026-02-17`.

Mechanism: Domains or encodings were fork-unaware or width-unsound: raw `eth_sign`, Homestead signer reuse, `eth_chainId` path divergence, seal hash omitting BaseFee, AUTHCALL stack operand mismatch, Difficulty narrowing before representability check, block-number continuity checked through `Uint64`.

Portable lesson: Prompts should force checks against the exact canonical typed object and fork-aware serializer, with explicit representability checks before narrowing and signer/replay domains at RPC boundaries.

Existing coverage: `11`, `13`, `17`, and `19` cover most of this. `17` is currently too narrow around parameter derivation and should include canonical numeric width before consensus comparison.

### Cluster G: Startup, Constructor, And Maintenance Dependency Readiness

Findings: `2018-09-25`, `2022-05-23`, `2025-04-14`, `2026-02-18`, `2026-03-05`.

Mechanism: Security-sensitive dependencies or background loops can start with weak defaults: signer warning policy not blocking by default, privileged API/mining setup split from account manager state, peer dropper not started, pending-header verifier without bounded milestone source, persisted milestone lock not sanitized at startup.

Portable lesson: Constructor/startup/maintenance loops deserve the same fail-closed dependency checks as live request paths.

Existing coverage: `01`, `11`, `15`, and `18` mention startup but not enough as a recurring audit motif.

## Proposed Prompt Changes

No new family prompt is justified. Bor's lessons are portable, but the current family set can express them cleanly if sharpened.

### `/testing/dlt-ai-audit-system/prompts/12_attestation_trust_and_freshness.md`

Add under "Search patterns":

```text
- external consensus-client, bridge-client, checkpoint, milestone, or oracle reads that feed local consensus should be pinned to one deterministic snapshot boundary. Check whether time-based, latest, retry, or fallback queries are converted into an explicit height, hash, epoch, finalized checkpoint, or signer-set identity before the data affects block validity, finalization, or state derivation.
```

Rationale: Captures Bor's Heimdall state-sync and validator-set failures without naming Heimdall.

### `/testing/dlt-ai-audit-system/prompts/13_input_validation_and_invariant_enforcement.md`

Add under "Search patterns":

```text
- consensus or protocol finalization helpers that signal invalid state indirectly through nil, empty collections, partial outputs, logs, or panics instead of returning an explicit validation error that every caller must handle
- equivalent execution paths, such as serial, parallel, stateless, replay, simulation, or recovery processors, where one path validates receipt counts, generated system work, unsupported fields, or post-execution invariants and another path only trusts helper output
```

Rationale: Bor repeatedly had errors hidden behind nil receipts, panics, or path-specific enforcement.

### `/testing/dlt-ai-audit-system/prompts/14_resource_accounting_and_limits.md`

Add under "Search patterns":

```text
- historical-range, log, trace, fee-history, proof, or witness APIs where the configured range limit is checked in one entrypoint but not in stored-filter replay, chain-specific variants, symbolic latest/pending/finalized selectors, or helper paths that construct the same expensive query
- background verification, sync-maintenance, pruning, and repair loops that derive their work window from current head minus a checkpoint, milestone, or finalized boundary. Check that the trusted boundary is fresh, the window is capped before materializing work, and missing boundary data disables or defers the loop instead of scanning an unbounded range.
```

Rationale: Directly transfers the Bor RPC range-limit and pending-header OOM patterns.

### `/testing/dlt-ai-audit-system/prompts/15_state_machine_and_lifecycle_consistency.md`

Add under "Search patterns":

```text
- startup, constructor, and background-maintenance paths that initialize security-sensitive loops from persisted state. Oversized, stale, impossible, or fork-incompatible persisted values should be sanitized or rejected before they drive reorg, milestone, sync, verifier, or peer-churn decisions.
- finalization, replay, and recovery paths where internally generated protocol work must remain grouped with the parent block or operation; dropping, filtering, or failing the generated work should rewind or reject the whole group when that is the consensus rule.
```

Rationale: Covers Bor milestone lock sanitation and state-sync finalization atomicity.

### `/testing/dlt-ai-audit-system/prompts/17_checked_arithmetic_and_parameter_bounds.md`

Add under "Search patterns":

```text
- consensus-significant numeric fields parsed as arbitrary precision, RLP integers, decimal strings, or big integers and then narrowed to fixed-width types before checking canonical representability
- block numbers, timestamps, epochs, milestone numbers, fork heights, and confirmation offsets where adding, subtracting, or converting across signed and unsigned widths can turn invalid future, past, or impossible values into plausible local state
```

Add question:

```text
6. Is the code checking representability and canonical encoding before narrowing or comparing, and do sanity checks enforce the same width as consensus verification?
```

Rationale: Bor had multiple width/offset issues around Difficulty, block numbers, and timestamps.

### `/testing/dlt-ai-audit-system/prompts/18_authoritative_state_and_boundary_enforcement.md`

Add under "Search patterns":

```text
- range, root, proof, log, or aggregate APIs that compute for `[start,end]` or another explicit target but validate cache freshness, reorg stability, or canonicality against current head, latest state, or a nearby proxy instead of the target block hash/root/range tuple
- external consensus, checkpoint, milestone, or validator-set data selected by timestamp, latest state, local cache, or retry fallback where all validators must instead derive the same snapshot identity before local execution consumes it
```

Rationale: Captures `GetRootHash` wrong-anchor and Heimdall deterministic-state-sync lessons.

### `/testing/dlt-ai-audit-system/prompts/19_consensus_fork_and_payload_rule_validation.md`

Add under "Search patterns":

```text
- finalization, post-execution, state-sync, deposit, withdrawal, or system-transaction paths that derive extra receipts, generated transactions, or state changes. Check that the block body, locally derived system work, receipts, and state root are cross-checked before success and that unsupported fields fail closed.
- fork-aware hashing, signing, opcode decoding, and header sanity paths where the canonical object shape changes by fork. Check that every verifier, signer, replay path, and helper includes exactly the fields active for that fork and rejects fields forbidden before or after the fork.
- consensus validation that depends on an external chain or consensus client. Check that time-based or latest queries are first pinned to a deterministic height/hash/finality boundary, and that all validators would query the same snapshot for the same local block.
```

Rationale: Strengthens existing consensus prompt for Bor's finalization, state-sync, fork-aware seal hash, and deterministic external-client inputs.

### `/testing/dlt-ai-audit-system/prompts/20_authenticated_state_proof_and_persistence_integrity.md`

Add under "Search patterns":

```text
- state, receipt, log, root, witness, or proof helpers that are parameterized by a range, block number, page number, or requested key but only validate the returned data against current head, total count, local cache state, or malformed-but-plausible pagination metadata
- content-addressed, page-addressed, or key-addressed peer payloads where both the payload hash/key and the page/order metadata must be recomputed and checked before storing, scheduling follow-up requests, or reporting completion
```

Rationale: Transfers Bor chunk integrity, witness-page validation, and range-root anchoring.

### `/testing/dlt-ai-audit-system/prompts/21_peer_sync_progress_and_response_binding.md`

Add under "Search patterns":

```text
- sync termination or "peer has stronger chain" decisions that accept a peer's claim without proving header progress, expected parentage, or a concrete chain segment beyond the local head
- discovery, bonding, ping/pong, or handshake responses where a reply of the right type is accepted without matching the exact challenge, nonce, peer identity, previous bond, or request token that authorized the larger response or state transition
```

Rationale: Existing prompt is very close; this adds Bor-specific recurring shapes in generic language.

### `/testing/dlt-ai-audit-system/02_validation_and_impact.md`

Add to the missing-property list:

```text
   - deterministic external-consensus snapshot binding
   - explicit finalization error propagation
   - canonical numeric representability before narrowing
```

Add under impact assessment:

```text
8. If the issue involves an external consensus client, checkpoint source, bridge oracle, or validator-set provider, distinguish stale local trust, nondeterministic data selection across honest nodes, fail-open unavailability, and direct forged-state acceptance.
9. If the issue involves finalization or generated system work, distinguish unsupported-field rejection, generated-work mismatch, receipt/accounting mismatch, and state-root divergence.
```

Rationale: Helps validation classify Bor-style hardening cases without overclaiming exploitability.

## Validation Notes

Holdout check: I held back the March-April 2026 Bor findings while drafting the first cluster wording. The proposed additions still help surface:

- `2026-03-25` deterministic state-sync by asking for external consensus-client snapshot binding.
- `2026-04-13` and `2026-04-16` finalization fail-closed behavior by asking for explicit finalization errors and serial/parallel path parity.
- The March 2026 range-limit findings by asking for stored-filter replay, symbolic selector normalization, and equivalent entrypoints.

Prompts that should stay unchanged for now:

- `10_authz_and_role_gates.md`: Bor had some privileged API/signer boundary cases, but existing auth guidance is adequate.
- `16_staking_registry_and_accountability.md`: Bor's validator-set findings are better treated as external consensus snapshot and signer-role validation than staking/economic accountability.

Remaining doubt: Several Bor findings are explicitly classified as security-hardening or unclear. The proposed text uses hunt motifs and validation questions rather than treating every historical patch as a confirmed vulnerability.
