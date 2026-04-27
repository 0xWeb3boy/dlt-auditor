# Sui Prompt-Pack Refinement Proposal

Target repo: `/testing/sui`

Evidence set: `/testing/sui/validated-findings/kept`

Corpus index used for clustering: `/testing/dlt-ai-audit-system/corpus/imports/20260424-134542Z-sui`

Finding count: 68 kept findings.

## 1. Repo Context Summary

Sui is an object-centric Move blockchain implemented primarily in Rust, with validators/authorities processing transactions, consensus ordering shared-object work, checkpoints committing executed effects, and epoch reconfiguration rotating validator/committee state. The findings concentrate in `crates/sui-core`, `crates/sui-types`, consensus core, RPC/API boundary code, Move VM/runtime integration, and storage/checkpoint code.

Important trust boundaries:

- Client or wallet -> validator RPC / authority service.
- Peer or validator -> consensus handler, block verifier, checkpoint, and sync paths.
- Signed transaction/certificate/checkpoint bytes -> signature verifier and authority/committee quorum logic.
- Executed transaction effects -> temporary store, authority store, checkpoint store, and authenticated state roots.
- Epoch and committee metadata -> reconfiguration, authenticated epoch storage, and signature verification.
- RPC/proxy metadata -> traffic controller, rate limiting, transport/TLS assumptions, and client-visible checkpoint/object data.
- Move/VM type and transaction inputs -> execution, gas/resource accounting, and object ownership checks.

High-risk entrypoint categories:

- `ValidatorService` raw transaction, object, checkpoint, and wait-for-effects APIs.
- Consensus block, commit, certificate, vote, and transaction ingestion.
- Checkpoint construction, checkpoint response verification, and state-sync/storage handoff.
- Signature, multisig, batch, epoch, and committee verification helpers.
- Transaction input loading, ownership resolution, temporary store finalization, and generated side effects.
- GraphQL/JSON-RPC query limit, proxy attribution, and transport security paths.
- Epoch transition and reconfiguration finalization paths.
- Peer sync and validator response aggregation paths.

State-machine patterns that matter:

- Epoch-scoped state must be bound to the correct committee and previous/current epoch relation.
- Locally executed but non-finalized effects must be rolled back or isolated before checkpoint/epoch finalization.
- Consensus and checkpoint logic often has multiple equivalent paths: direct validator response, peer sync, replay, recovery, checkpoint builder, and consensus handler.
- Resource-control decisions are distributed across ingress, submission, consensus output, traffic-controller accounting, query planning, and VM execution.
- Object ownership and authorization can be hidden behind derived object refs, dynamic fields, owner resolution, and helper APIs.

## 0. Finding Inventory

Folder: `/testing/sui/validated-findings/kept`

All 68 findings were analyzed. None were intentionally skipped. The table below compresses the per-finding mechanism analysis; each row was checked against the raw finding and enriched record.

| Finding | Mechanism | Generic invariant / missing property | Hunt recipe | False-positive killers |
| --- | --- | --- | --- | --- |
| 2021-09-01 transaction signatures | Signature canonicalization in transaction-processing | Signed bytes must be canonical and bound to the consumed transaction shape; missing signature canonicalization | Compare signed representation, verifier input, and execution input for alternate encodings | Canonical serializer is mandatory on every path before verification |
| 2022-01-25 certificate comparison | Unsafe certificate comparison semantics | Equality/ordering over authenticated artifacts must compare the security identity, not incidental representation | Search comparison/ordering impls for signed/certified types | Comparison is only for logging/cache display, never policy |
| 2022-02-06 staking/authority robustness | Byzantine authority response handling in staking/sync | Authority responses must not let one faulty peer block progress; missing robust boundary handling | Inspect fanout/aggregation paths for single-peer dependency and missing fallback | Quorum aggregator retries enough peers and penalizes bad responders |
| 2022-05-03 transaction resource exhaustion | Expensive transaction path before/without adequate limits | Untrusted work must be bounded/charged before shared resource use | Trace admission to execution for work before metering | Same limit enforced at ingress and execution for every path |
| 2022-05-04 storage gas metering | Gas/storage accounting inconsistency | Gas and storage charges must be computed from final applied effects | Build before/after accounting model around final writes | Finalizer recomputes exact charged state and fails closed |
| 2022-05-18 cryptography consensus input validation | Consensus input validation gap | Consensus inputs must be semantically valid before trusted cryptographic use | Compare decoding vs semantic validation before consensus sink | Consensus verifier rejects malformed/invalid objects on all paths |
| 2022-06-07 checkpoint response digest | Checkpoint contents digest verification | Returned checkpoint contents must match the authenticated digest | Inspect RPC/checkpoint response paths for digest recomputation | Client/API marks unauthenticated data as advisory only |
| 2022-06-21 non-finalized state retention | Epoch finalization failed to rollback extra effects | Durable state must not retain non-finalized execution effects | Search finalization paths for deferred or no-op rollback of extra work | Extra effects are isolated from reads and cleared before commit |
| 2022-06-24 checkpoint execution invariant | Checkpoint/execution consistency | Checkpointed execution roots must match executed effects | Compare checkpoint roots, effects, and execution output finalizers | Checkpoint builder recomputes from canonical executed data |
| 2022-06-30 byzantine availability | Single/byzantine peer availability gap | Peer-driven sync must continue or penalize when a peer withholds valid data | Inspect fetch/retry loops for one-peer dependence | Multiple validators tried with no-progress accounting |
| 2022-07-04 validator response handling | Validator response aggregation liveness | Aggregators must distinguish bad/empty/no-progress responses | Trace response handling and peer feedback | Response is advisory and retried through quorum path |
| 2022-07-15 checkpoint response verification | Checkpoint response proof/digest verification | Proof-bearing responses must bind contents to request | Inspect response structs with optional contents/digests | Verified wrapper enforces exact requested checkpoint |
| 2022-07-20 authenticated epoch storage | Epoch state authenticated storage | Epoch material must be authenticated before storage/use | Map epoch data read/write and verification layers | Only local genesis/test state can enter path |
| 2022-07-23 signing type registration | Signing type/intent registration hardening | Signed object type/domain must be explicit and registered | Search signing helper registries and default/fallback intents | Type only affects UI/logging, not verification |
| 2022-07-29 signature malleability | Alternate signature encodings accepted | Verifier must reject malleable/non-canonical signatures | Test alternate encodings against same signed message | Crypto library normalizes and rejects non-canonical bytes |
| 2022-07-29 epoch auth invariant | Epoch authentication bound to previous committee | Epoch records must be signed by the authoritative epoch committee | Check previous/current epoch relation in verifier | Epoch relation enforced by certified storage before verifier |
| 2022-08-16 empty batch signatures | Empty batch signature validation | Aggregate/batch signatures must prove required signed items | Search empty-list/zero-weight aggregate edge cases | Empty batch is explicitly valid and never authorizes state |
| 2022-08-17 unbounded retry | Retry/cache resource control | Retries must be bounded, attributed, and cleaned up | Inspect retry loops and cache growth under repeated failures | Retry budget and GC are enforced before work is scheduled |
| 2022-08-26 consensus error class | Consensus error misclassification | Invalid consensus data must surface as invalid, not generic failure | Follow error mapping to consensus/checkpoint scheduler | Upper layer treats all errors as fail-closed invalid |
| 2022-10-04 consensus resource control | Consensus-related resource limit hardening | Consensus work must have protocol-configured caps | Search block/tx/committee limits at verification boundary | Cap enforced before allocation or scheduling on every path |
| 2022-10-13 epoch state confusion | Epoch-coordinate state confusion | State must be keyed by the exact epoch/committee coordinate | Compare caches/stores keyed by epoch vs digest vs committee | Key includes all security coordinates and is rechecked |
| 2022-11-08 ownership invariant | Ownership checks before storage/object use | Object ownership must be enforced before use or persistence | Trace object refs from input loader to writes | Later mandatory owner/capability check before mutation |
| 2022-11-14 missing epoch binding | Certificate/signature lacks epoch binding | Signed material must bind epoch and committee context | Search signatures over data without epoch intent/context | Epoch is included in signed bytes or verified wrapper |
| 2022-11-30 consensus liveness DoS | Consensus peer/work liveness issue | Invalid/zero-progress consensus work must not stall node | Inspect queues for no-progress, timeout, retry symmetry | Scheduler penalizes and drops bad inputs under quota |
| 2022-12-20 consensus epoch hardening | Epoch invariant hardening in consensus | Consensus state advances only under correct epoch context | Compare epoch gates in replay, recovery, live paths | Path is test-only or all live paths share verifier |
| 2022-12-21 epoch-boundary race | Reconfiguration race at epoch boundary | Epoch transitions must be atomic across all readiness/state fields | Inspect reconfig begin/end/abort and late messages | Lock/snapshot covers all fields used in transition |
| 2022-12-29 epoch transition race | Storage state race across epoch transition | Persisted epoch state must not mix old/new coordinates | Search async finalization and checkpoint handoff races | Store writes are fenced by epoch marker and idempotent |
| 2023-01-05 missing user signature verification | Validators could submit certs with bad user sigs | Validator/committee signatures do not replace user authorization | Inspect certificate validation for inner user signature checks | Inner tx was verified before certificate and cannot be mutated |
| 2023-01-09 finality rollback | Finalized state rollback/integrity | Finality rollback must restore exact mutated coordinates | Inspect rollback and recovery around checkpoint/finality | Rollback is impossible in production or exact journal exists |
| 2023-01-12 missing signature commitment | Signature commitment/audit gap | Signatures must commit to data needed for later verification/audit | Compare signed digest vs persisted audit fields | Missing field is derived canonically and immutable |
| 2023-02-02 quorum hardening | Consensus quorum edge hardening | Quorum checks must count the active weighted committee exactly | Test small committees, duplicates, boundary weights | Library enforces unique weighted quorum before caller |
| 2023-02-21 integer overflow | Arithmetic overflow in transaction path | Protocol arithmetic must be checked before persistence | Search casts/add/mul on protocol-controlled amounts | Values bounded by type-safe wrapper before operation |
| 2023-02-23 equivocation handling | Consensus equivocation state handling | Equivocation evidence must be bound and handled consistently | Inspect duplicate/equivocation branches and penalties | Equivocation impossible due to earlier verified unique index |
| 2023-02-27 domain separation | Missing signature domain separation | Signatures must bind protocol purpose/domain | Search shared signing helpers without intent/domain | Same key/message cannot cross security domains |
| 2023-02-27 integer overflow | Arithmetic overflow in transaction path | Numeric state changes must reject wrap/truncation | Boundary-test max/min amount operations | Checked arithmetic wrapper used end-to-end |
| 2023-02-28 validator metadata validation | Validator metadata semantic validation | Validator metadata must satisfy protocol constraints before use | Inspect config/metadata admission and epoch activation | Metadata is only displayed, not used for routing/security |
| 2023-03-01 resource exhaustion | Repeated transaction work before limits | Expensive execution must be quota/gas bounded | Search repeated malformed tx paths and cache growth | Existing cache/throttle covers exact digest/client |
| 2023-03-03 accounting invariant hardening | SUI conservation after gas/effects | Final state must preserve supply/resource accounting after generated effects | Model final effects, gas, rebates, written objects | Invariant runs after all writes and covers dynamic objects |
| 2023-03-06 timestamp source | Unverified consensus timestamp source | Timestamps used for consensus/state must come from authoritative consensus | Trace timestamp origin to state commitment | Timestamp is advisory or recomputed from consensus output |
| 2023-03-18 object access auth | Object read/access authentication | Object access must require owner/capability authorization | Search object read APIs and input loader bypasses | API only returns public/immutable data |
| 2023-04-06 ownership validation | Incomplete ownership validation | Every mutable object must pass exact owner check | Compare owned/shared/immutable paths and generated objects | Later execution rejects unauthorized object use |
| 2023-04-08 RPC object digest | RPC digest/client view validation | Client-visible object data must match authenticated digest | Recompute digest before serving/storing RPC object | Response is marked pending/unauthenticated and not trusted |
| 2023-04-10 monetary accounting | Monetary accounting invariant | Value conservation must cover final effects and fees | Trace actual, not estimated, amounts into finalizer | Shared invariant covers every transaction family |
| 2023-04-21 wallet content script message | Wallet/data message boundary validation | Client-visible scripts/messages must not cross authorization boundary | Inspect message construction and content-source checks | Content cannot execute or access private wallet data |
| 2023-09-02 multisig input validation | Multisig semantic input validation | Multisig configs must enforce threshold/signers/canonicality | Search threshold, duplicate signer, empty signer cases | Crypto library rejects duplicate/invalid multisig upfront |
| 2023-10-26 resource control | Resource control hardening | Work admission must enforce limits before expensive execution | Map all ingress paths to same limiter | Limit is enforced at shared lower layer |
| 2024-03-19 consensus RPC epoch filter | Consensus RPC epoch isolation | Consensus RPC requests must bind active epoch | Check transport/RPC middleware for epoch header enforcement | Peer auth already includes non-replayable epoch context |
| 2024-05-21 threshold API | Signature threshold API hardening | Threshold APIs must express required quorum exactly | Inspect caller interpretation of threshold helper return | Helper returns explicit weighted quorum and caller checks it |
| 2024-06-12 proxy attribution | Proxy/client attribution hardening | Rate limiting identity must come from trusted source only | Inspect proxy header parsing and fallback behavior | Deployment does not trust proxy headers or has outer limiter |
| 2024-06-26 traffic accounting | Traffic-control accounting gap | All rejected/expensive requests must update abuse accounting | Compare success, invalid, timeout paths into traffic tally | Outer gateway accounts before node sees request |
| 2024-07-16 GraphQL query limit | Query complexity/range limit | Query work must be bounded across all dimensions | Inspect query planner before execution/allocation | GraphQL engine enforces equivalent cost cap |
| 2024-08-20 consensus resource limits | Consensus block size/count limits | Consensus proposals must enforce bytes/count limits at verifier | Search count-vs-bytes asymmetry in block verifier | Upstream consensus layer enforces same protocol config |
| 2024-08-31 resource exhaustion | Transaction resource exhaustion | Malformed/repeated tx must be bounded and charged | Trace decode/verify/execute for early expensive work | Decode fails before allocation and traffic control counts it |
| 2024-11-21 consensus limit accounting | Consensus limit accounting | Proposal production/validation must share the same limit accounting | Compare builder and verifier limits | Builder-only limit cannot affect accepted blocks |
| 2024-12-13 resource control | Consensus resource hardening | Consensus path must throttle/limit expensive work | Inspect per-author/per-object/round limits | Existing congestion/backpressure covers all cases |
| 2025-03-26 object ownership auth | Consensus object ownership authentication | Consensus objects must prove owner/auth before use | Search derived consensus objects bypassing owner checks | Object type is system-only and impossible for users to forge |
| 2025-05-21 DoS default hardening | Default DoS protection | Security limits should fail closed in default config | Inspect defaults and disabled limiter paths | Deployment config mandates external limiter |
| 2025-06-18 transport security | Plaintext transport exposure | Sensitive RPC/control channels require authenticated/encrypted transport | Search insecure listener defaults and fallback transports | Channel carries only public data behind trusted network |
| 2025-07-18 state commitment gap | Consensus state commitment gap | Extra consensus state must be committed/replayed deterministically | Inspect in-memory consensus state and recovery replay | State is derived only from committed deterministic inputs |
| 2025-09-10 resubmission accounting | MFP resubmission attribution | Repeated submissions must be counted and attributed | Trace submitted tx cache, digest count, traffic tally | Upstream limiter rejects repeated submissions before consensus |
| 2025-10-02 malformed crypto input | Malformed input availability hardening | Malformed crypto/protocol inputs must return validation errors | Fuzz decode/verify boundary for panics | Panic is test-only or caught before process boundary |
| 2025-11-26 vote accounting | Consensus vote accounting | Votes must be counted once under correct weight/context | Inspect duplicate vote and weight aggregation | Aggregator deduplicates by signer and round before count |
| 2026-01-10 finalization hardening | Consensus finalization invariant | Finalization requires exact quorum/context binding | Trace finalization conditions across recovery/live paths | Finalizer recomputes from canonical committed blocks |
| 2026-02-27 malformed tx panic | Malformed transaction panic | Invalid transactions must be ordinary validation failures | Fuzz syntactically valid but semantically invalid tx inputs | Panic only reachable in test helper or after trusted construction |
| 2026-03-23 owner resolution | Incorrect owner resolution | Owner resolution must use authoritative current object state | Search helpers deriving owner from stale/partial info | Final auth check uses current store before mutation |
| 2026-03-25 VM recursion bound | VM recursive type traversal bound | Recursive untrusted types must consume bounded traversal budget | Search recursive type/ability/layout walkers | Type depth already bounded at bytecode verifier and runtime |
| 2026-03-27 storage amplification | Storage/resource amplification | Storage amplification must be capped/charged at source | Trace fanout from one request to many reads/writes | Amplification disabled by config or already counted |
| 2026-03-30 traffic accounting | Missing traffic-control accounting | Rejections/errors must feed abuse accounting | Compare valid/invalid/timeout paths into limiter | Outer layer accounts all requests before node handling |

## 3. Family Clustering

### Cluster A: Signature, Certificate, And Epoch Binding

Findings: 2021-09-01, 2022-07-23, 2022-07-29 x2, 2022-08-16, 2022-11-14, 2023-01-05, 2023-01-12, 2023-02-27, 2023-09-02, 2024-05-21.

Why grouped: all distinguish syntactic signature validity from semantic binding: intent/domain, epoch, signer role, payload commitment, threshold/quorum, empty batch behavior, and canonical encoding.

Portable: high. This is not Sui-specific; any DLT with validator signatures, checkpoints, committees, batches, or multisig has the same risk.

### Cluster B: Epoch, Checkpoint, Finality, And Authenticated-State Lifecycle

Findings: 2022-06-07, 2022-06-21, 2022-06-24, 2022-07-20, 2022-10-13, 2022-12-20, 2022-12-21, 2022-12-29, 2023-01-09, 2023-02-23, 2023-03-06, 2024-03-19, 2025-07-18, 2026-01-10.

Why grouped: all involve state that is correct only when bound to the exact epoch, checkpoint, finality boundary, replay window, or recovered consensus state.

Portable: high. The exact terms differ across chains, but the invariant is common: committed/finalized/authenticated state must not mix coordinates or retain non-finalized side effects.

### Cluster C: Resource Accounting, Traffic Attribution, And Multi-Dimensional Limits

Findings: 2022-05-03, 2022-08-17, 2022-10-04, 2022-11-30, 2023-03-01, 2023-10-26, 2024-06-12, 2024-06-26, 2024-07-16, 2024-08-20, 2024-08-31, 2024-11-21, 2024-12-13, 2025-05-21, 2025-09-10, 2026-03-25, 2026-03-27, 2026-03-30.

Why grouped: all address cheap remote or peer input causing expensive validator work unless bytes/count/depth/retry/query/submitter dimensions are bounded and attributed across success and error paths.

Portable: high. This is a reusable audit pattern for consensus blocks, RPC queries, transaction submissions, retry loops, VM type traversal, and traffic-control systems.

### Cluster D: Object Ownership And Authorization At Derived Sinks

Findings: 2022-11-08, 2023-03-18, 2023-04-06, 2025-03-26, 2026-03-23.

Why grouped: object ownership/authority is sometimes derived through helpers, object refs, consensus object handling, or storage views. The sink must check authoritative current ownership, not inferred or stale identity.

Portable: high for object/resource-based ledgers; medium for account-only ledgers, but still maps to capability and state-entry authorization.

### Cluster E: Ledger, Gas, And Economic Invariant Coverage

Findings: 2022-05-04, 2023-02-21, 2023-02-27, 2023-03-03, 2023-04-10.

Why grouped: numeric and accounting invariants must be checked after final effects, gas, rebates, generated objects, and conversions are known.

Portable: high. Already represented in the prompt pack, but Sui reinforces generated-effects and post-gas conservation language.

### Cluster F: Peer/Validator Response Progress And Byzantine Availability

Findings: 2022-02-06, 2022-06-30, 2022-07-04, 2022-08-26.

Why grouped: remote validator/peer responses need response binding, fallback, progress classification, and invalid/error classification to avoid liveness degradation or state confusion.

Portable: high. Applies to validator fanout, sync, committee response aggregation, and checkpoint/state retrieval.

### Cluster G: Malformed Input Panics And Unsafe Boundary Defaults

Findings: 2025-06-18, 2025-10-02, 2026-02-27.

Why grouped: security hardening around malformed data and insecure defaults: panics must become validation failures, and transport/security defaults should fail closed.

Portable: medium-high. The exact panic sites are repo-specific, but the audit instruction is generic.

## 4. Prompt-Pack Comparison

| Cluster | Existing prompt coverage | What is weak | Decision |
| --- | --- | --- | --- |
| A Signature/epoch binding | `11_signature_binding_and_signer_scope.md`, `12_attestation_trust_and_freshness.md`, mapper step 3a | Good coverage, but underemphasizes empty aggregate/batch signatures, certificate wrapper mutation, and prior/current epoch signer binding as a recurring edge case | Refine existing prompt 11 and mapper |
| B Epoch/checkpoint/finality lifecycle | `15_state_machine...`, `20_authenticated_state...`, mapper steps 13/18 | Good coverage, but Sui suggests clearer language for locally executed-but-not-finalized effects, replay windows, and in-memory consensus state commitments | Refine prompts 15 and 20 |
| C Resource/traffic limits | `14_resource_accounting_and_limits.md` | Strong, but should explicitly cover attribution symmetry: invalid/rejected/timeout paths must tally abuse, and consensus builder/verifier must enforce the same multi-dimensional limits | Refine prompt 14 and validation prompt |
| D Object ownership/auth | `10_authz...`, `18_authoritative_state...`, `13_input_validation...` | Current auth prompt is role/capability oriented; it could better cover object/resource ownership derived through refs, dynamic fields, helper summaries, and consensus-created objects | Refine prompts 10 and 18 |
| E Ledger accounting | `22_ledger_accounting...`, `17_checked_arithmetic...` | Already strong. Add only a small generated-effects/post-gas invariant reminder to base hunter or prompt 22 | Minor refinement |
| F Peer response progress | `21_peer_sync...`, base hunter | Strong, but Sui validator fanout cases suggest adding “committee/authority response aggregation” beyond downloader/sync language | Refine prompt 21 |
| G Malformed input/defaults | `13_input_validation...`, `14_resource...` | Existing malformed-input guidance is good. Transport/security-default hardening is less explicit | Minor refinement to prompt 13 or validation |

No new prompt family is justified. Every Sui mechanism fits an existing family; adding a Sui-flavored family would increase overlap and overfit.

## 5. Proposed Prompt Changes

### Change 1: Strengthen Signature Binding For Epoch And Batch Edges

Target: `/testing/dlt-ai-audit-system/prompts/11_signature_binding_and_signer_scope.md`

Draft text to add under `Search patterns`:

```text
- aggregate, batch, certificate, or checkpoint signatures where an empty item list, duplicate signer, stale committee, or missing inner-user signature can still produce a syntactically valid wrapper. Verify that the wrapper proves every required inner authorization, not just committee approval of a container.
- epoch or committee-scoped signatures where the data is signed by the previous, current, or next committee. Check that the verifier names the exact epoch relation required by the protocol and rejects off-by-one or default-epoch authentication.
- signed/certified objects that can be mutated, reconstructed, or compared after verification. Ensure equality, ordering, hashing, and storage keys use the authenticated identity and not an incidental representation.
```

Rationale: Sui has repeated examples where “signature verifies” was insufficient because the signed wrapper, epoch relation, or inner authorization was incomplete.

Repo-specific details excluded: Sui certificate names, `tx_signature`, checkpoint structs, and exact epoch-store APIs.

Overfitting risk check: Low. Empty aggregate signatures, committee epoch binding, and wrapper mutation are common across BFT chains and bridges.

### Change 2: Add Non-Finalized Effects And Replay-Window Lifecycle Language

Target: `/testing/dlt-ai-audit-system/prompts/15_state_machine_and_lifecycle_consistency.md`

Draft text to add under `Search patterns`:

```text
- locally executed, speculatively executed, or peer-fetched work that is later excluded from the finalized checkpoint, block, batch, or epoch boundary. Finalization must rollback, quarantine, or prove isolation of those effects before durable state can be served or reused.
- in-memory consensus, batching, congestion, or timing state that is reconstructed by replay after restart. If replay reconstructs only a fixed window, check that the committed digest/snapshot covers exactly the state retained across live execution and recovery.
- epoch, checkpoint, or committee transitions where old-epoch messages can arrive while new-epoch state is being initialized. Verify that readiness, signer set, traffic counters, and pending work are fenced by one coherent transition state.
```

Rationale: Sui findings repeatedly involve finality/epoch boundaries, retained state, and recovery/replay assumptions.

Repo-specific details excluded: Sui epoch names, Mysticeti, and checkpoint implementation details.

Overfitting risk check: Low. Speculative execution, finality handoff, and replay-window reconstruction occur in many validators and rollups.

### Change 3: Strengthen Authenticated State And Persistence Prompt

Target: `/testing/dlt-ai-audit-system/prompts/20_authenticated_state_proof_and_persistence_integrity.md`

Draft text to add under `Search patterns`:

```text
- checkpoint, epoch, or state-sync responses that carry both an authenticated summary and optional contents. Recompute the contents digest/root and bind it to the exact requested sequence, root, and certification status before serving or persisting it.
- rollback or revert helpers that undo executed effects. Confirm they restore every mutated coordinate: objects, effects, events, indexes, accumulators, gas/rebate accounting, and any checkpoint membership tracking.
- storage tables keyed by sequence, epoch, or digest where one table stores certified data and another stores pending or full contents. Check that promotion, pruning, and lookup paths cannot mix pending, certified, stale, or wrong-epoch material.
```

Rationale: Sui’s checkpoint/storage findings show the same authenticated data split appearing in several tables and API responses.

Repo-specific details excluded: `CheckpointResponseV2`, authority store table names.

Overfitting risk check: Low-medium. The exact table split is implementation-specific, but summary/content binding and rollback completeness are portable.

### Change 4: Tighten Resource Accounting Around Attribution And Error Paths

Target: `/testing/dlt-ai-audit-system/prompts/14_resource_accounting_and_limits.md`

Draft text to add under `Search patterns`:

```text
- traffic-control, rate-limit, spam-weight, or peer-penalty systems where only successful submissions are attributed. Invalid, duplicate, rejected, timeout, already-known, and consensus-output paths should update resource/accounting state symmetrically when they consume comparable work.
- transaction or message resubmission caches where the key is a digest, object ID, sender, peer, or client address. Check that all ingress paths propagate the same attribution key and that paths without attribution cannot bypass the limiter.
- consensus proposal builders and consensus verifiers that enforce related limits independently. Count, byte, per-item, aggregate-byte, recursion-depth, and per-author limits must match between production and validation, with any-limit-exceeded rejection rather than partial enforcement.
```

Rationale: The Sui corpus has many resource-control hardening findings across RPC, traffic control, consensus, GraphQL, VM recursion, and transaction resubmission.

Repo-specific details excluded: traffic-controller names, GraphQL package names, Mysticeti fast path.

Overfitting risk check: Low. Attribution and builder/verifier limit symmetry are general.

### Change 5: Strengthen Object/Resource Ownership Authorization

Target: `/testing/dlt-ai-audit-system/prompts/10_authz_and_role_gates.md` and/or `18_authoritative_state_and_boundary_enforcement.md`

Draft text to add to `10_authz...` under `Search patterns`:

```text
- object-, resource-, or capability-based ledgers where the executed object set is derived through object references, dynamic fields, consensus-created objects, or helper summaries. Check that the final sink revalidates current ownership/capability for every mutable, deletable, wrapped, or indirectly loaded object.
- paths that authorize based on a transaction sender, object ID, cached owner, or declared owner before resolving the authoritative current owner. The authorization decision should consume the same owner state that the write/delete/transfer sink will mutate.
```

Draft text to add to `18_authoritative_state...`:

```text
- helper APIs that answer “who owns this?” or “is this accessible?” from a cache, object ref, prior effects, or partial store view. Treat those answers as hints unless the sink rebinds them to current canonical state before mutation.
```

Rationale: Several Sui findings are about owner/authentication gaps around object access, object resolution, and consensus-object ownership.

Repo-specific details excluded: Sui object type names and Move-specific ownership APIs.

Overfitting risk check: Low for object/resource ledgers; medium for pure account ledgers, but still useful for capability/state-entry systems.

### Change 6: Add Committee/Authority Fanout To Peer Sync Prompt

Target: `/testing/dlt-ai-audit-system/prompts/21_peer_sync_progress_and_response_binding.md`

Draft text to add under `Focus` or `Prioritize`:

```text
- validator, authority, committee, sequencer, or relayer fanout where a client/node gathers certificates, effects, votes, checkpoint data, or execution results from multiple remote authorities.
```

Draft text to add under `Search patterns`:

```text
- aggregation code that treats one authority response as enough to decide retry, liveness, or error classification before checking whether another authorized peer can provide the missing certificate/effects/proof.
- response handlers that collapse Byzantine, malformed, empty, already-known, unavailable, timeout, and wrong-ledger responses into one generic error, preventing retry, bad-peer feedback, or invalid-data handling from taking the correct branch.
```

Rationale: Sui has multiple findings where validator response handling and Byzantine availability were the real mechanism, not ordinary downloader sync.

Repo-specific details excluded: authority aggregator implementation names.

Overfitting risk check: Low. Committee/relayer fanout exists in bridges, BFT clients, sequencers, and validator APIs.

### Change 7: Add A Small Validation-And-Impact Classifier For Hardening

Target: `/testing/dlt-ai-audit-system/02_validation_and_impact.md`

Draft text to add after the verdict categories:

```text
When the patch clearly tightens a validator, consensus, proof, traffic-control, or authenticated-state boundary but the evidence does not prove attacker control or deployed exploitability, classify it as likely/security-hardening. Preserve the invariant and hunt lesson, but avoid impact claims such as consensus break, theft, forged state, or remote DoS unless the code path and attacker capability are demonstrated.
```

Rationale: Most Sui kept findings are useful hardening examples, not proven exploits. Prompt users need a stronger guardrail against overstating impact.

Repo-specific details excluded: all Sui names.

Overfitting risk check: Very low. This is a corpus-quality rule, not a bug recipe.

### Change 8: Minor Ledger Accounting Refinement

Target: `/testing/dlt-ai-audit-system/prompts/22_ledger_accounting_and_invariant_coverage.md`

Draft text to add under `Search patterns`:

```text
- final accounting checks that run before gas charging, rebates, storage refunds, generated objects, dynamic fields, or temporary-store writes are known. Re-run the conservation model at the actual finalization boundary and include all generated side effects.
```

Rationale: Sui’s SUI conservation and gas/storage findings support the existing prompt but sharpen the final-boundary wording.

Repo-specific details excluded: SUI, storage fund, temporary store.

Overfitting risk check: Low.

## 6. New Family Prompts

No new family prompt is recommended.

Reason: the Sui corpus reinforces existing families rather than exposing an unmodeled class. The strongest themes are already covered by prompts 11, 14, 15, 20, 21, and 22. A new “Sui object invariant” or “epoch checkpoint” prompt would overlap heavily with existing authoritative-state, lifecycle, and authenticated-state prompts.

## 7. Validation Notes

Held-out check: I drafted the main cluster wording without using the 2026 tail findings as examples, then checked it against:

- `2026-02-27` malformed transaction panic: covered by prompt 13 malformed-input validation and validation hardening language.
- `2026-03-23` incorrect owner resolution: covered by proposed object/resource ownership additions.
- `2026-03-25` VM recursion bound: covered by resource-accounting multi-dimensional limit / recursion-depth wording.
- `2026-03-27` storage amplification: covered by resource amplification and authenticated-state/storage boundary wording.
- `2026-03-30` traffic accounting: covered by proposed invalid/rejected/timeout traffic accounting symmetry.

Remaining doubts:

- Some Sui findings are hardening-only and may not justify runtime-prompt expansion beyond the validation classifier. The exact placement should prefer concise additions over bloating already long prompts.
- The current prompt pack already contains many related instructions. The highest-value changes are wording refinements, not new files.
- If maintainers want a shorter runtime pack, several Sui lessons should live only in corpus cards/evals rather than runtime prompts.

Prompts that should stay unchanged for now:

- `12_attestation_trust_and_freshness.md`: Sui adds epoch/trust-list material, but current attestation guidance is already broad enough.
- `16_staking_registry_and_accountability.md`: only two Sui staking-labeled kept findings, and both map better to peer robustness or proxy attribution.
- `17_checked_arithmetic_and_parameter_bounds.md`: only two arithmetic findings, already captured.
