# Sei Prompt-Pack Refinement

Target repo: `/testing/sei-chain`  
Findings source: `/testing/sei-chain/validated-findings/kept`  
Finding count: 40

## Repo Context Summary

Sei is a Cosmos-SDK based L1 with a forked Tendermint implementation, an EVM execution layer, CosmWasm/IBC integration, EVM JSON-RPC, precompiles, oracle/staking modules, and newer Autobahn consensus code. The key security surfaces in the kept findings are:

- Consensus and p2p state machines: `sei-tendermint/internal/consensus`, `internal/autobahn`, `internal/mempool`, `internal/p2p`, `internal/statesync`.
- Transaction admission and execution: `app`, `app/ante`, `app/legacyabci`, `sei-cosmos/baseapp`, `x/evm/ante`, `x/evm/state`, `giga`.
- Cross-runtime adapters: EVM precompiles, EVM/Cosmos address association, wasm query payload builders, gov/staking/IBC/solo precompile paths.
- Cross-chain/proof surfaces: IBC packet acknowledgement, IBC client recovery, Tendermint Merkle proof verification.
- Accountability and resource controls: oracle slashing, mempool peer blacklisting, CheckTx spam counters, websocket subscriptions, gas metering.

Important trust boundaries:

- Remote peers -> p2p reactors, mempool, consensus, state sync, and mux stream state.
- Submitted transactions -> ante/preprocess, mempool admission, EVM/Cosmos execution, precompiles, and block finalization.
- Cross-runtime callers -> precompile or query payload construction, canonical Cosmos SDK Msg/MsgServer paths, and address association state.
- Consensus certificates/proposals/protobuf objects -> locally stored consensus state and emitted votes.
- IBC packets/proposals/proofs -> application callback state, light-client state, and proof-verification output.
- Local config/build modes -> production execution, mock balances, crypto/key lifecycle, and RPC exposure.

State-machine patterns that matter:

- View/round transitions where prior certificates carry locks or proposal identity.
- BeginBlock/EndBlock and precompile paths where errors, gas, and return data can become consensus-visible.
- Mempool admission paths where early side effects must align with final admission.
- Peer feedback paths where invalid input must be attributed, scoped, and cleaned up with peer lifecycle.
- Alternate execution paths where accounting, store flushing, receipts, and state deltas must match canonical execution.

## Finding Inventory

All 40 files in `/testing/sei-chain/validated-findings/kept` were analyzed. No findings were intentionally skipped.

| Finding | Mechanism |
| --- | --- |
| `2021-04-12...2a4fd03c4` | IBC callback state was not transactionally tied to acknowledgement success. |
| `2021-05-27...46c2d2fbd` | IBC client recovery copied proposal-selected state instead of canonical substitute latest state. |
| `2022-02-02...a613471d8` | Raw error strings reached consensus-visible acknowledgement bytes. |
| `2022-11-15...d9d950ab7` | Contract registration lacked canonical creator authorization. |
| `2022-12-19...e3373eba5` | Wasm sudo lifecycle execution used an infinite gas meter. |
| `2023-01-12...e52126b92` | CheckTx failure counters were not tied to peer eviction. |
| `2023-02-03...562746653` | Oracle abstentions were omitted from slashing participation accounting. |
| `2023-02-17...b5f113295` | Oracle consensus processing depended on unordered map traversal. |
| `2023-03-20...b8d1c3a2d` | Malformed Merkle proof shape returned ambiguous nil roots instead of errors. |
| `2024-03-19...b6bdd9fc5` | Account association signature recovery used a placeholder hash. |
| `2024-03-19...d63321d8e` | Same signed-message binding gap in account association. |
| `2024-04-15...56ce9a974` | Wasm/EVM payload builders accepted unassociated addresses. |
| `2024-04-15...78eb1d663` | Same address-association check gap. |
| `2024-04-15...a2aa14179` | Same address-association check gap. |
| `2024-05-03...e8e4b3bf4` | RPC websocket listener allocation lacked a configured cap. |
| `2024-05-08...a2ab1c532` | EVM surplus/supply accounting was inconsistent across ante, EndBlock, and migration. |
| `2024-05-09...b36bfe41b` | EVM tx admission lacked explicit chain-ID/replay-domain validation. |
| `2025-05-06...4523d3d13` | Oracle spam counter check and set were not atomic. |
| `2025-06-06...beccf236c` | Gov precompile direct keeper calls bypassed canonical Msg validation path. |
| `2025-07-23...0332c4a9d` | Solo precompile generic claim path lost concrete message scope and runtime boundary. |
| `2025-07-24...9836e33a2` | Crypto dependency CVE update plus public-key parsing API migration. |
| `2025-07-31...1da04435c` | Consensus PartSet sizing fields lacked consistent bounds before allocation/state use. |
| `2025-08-18...d35634422` | Unprotected legacy EVM txs were accepted outside test mode. |
| `2025-09-30...caebdeaa5` | Consensus block processing did not consistently recover/propagate panics and errors. |
| `2025-10-29...48090d81b` | Mempool pending nonce was recorded before final admission. |
| `2025-11-13...f6d7875ab` | P2P invalid-input errors did not consistently evict/penalize peers. |
| `2025-12-03...0156e75d7` | Precompile error strings could become consensus-visible result data. |
| `2025-12-03...b5f8936e8` | Same consensus-visible precompile error-data nondeterminism. |
| `2025-12-16...7c3df71f7` | Peer blacklist trigger needed narrower abuse scope before enabling by default. |
| `2026-01-12...cbd47b343` | Encrypted transport leaked application write-size metadata. |
| `2026-01-29...bded875b1` | Mock balance mutation needed production-network fail-closed guards. |
| `2026-02-09...d9f1de1a4` | Giga EVM execution lost finalized surplus and failed to flush alternate store state. |
| `2026-02-12...f45028f01` | Commit-step reconstruction could use stale or mismatched proposal state. |
| `2026-02-19...4d45fcdc8` | Autobahn PushQC mutation used incoming QC data outside the needed-and-verified predicate. |
| `2026-02-19...1a3758d85` | Consensus proposal validation needed leader, lane, signature, and hash-link checks. |
| `2026-03-06...f5844b5a6` | Timeout votes dropped inherited PrepareQC lock across consecutive timeouts. |
| `2026-04-08...65bedcfef` | Peer failure-counter ownership belonged in the reactor with peer lifecycle cleanup. |
| `2026-04-08...8d751f648` | Protobuf-to-domain conversion accepted empty TimeoutQC vote sets. |
| `2026-04-10...107c8e793` | P2P mux stream kind was missing or inconsistent across stream lifecycle. |
| `2026-04-21...9b9e33970` | Ed25519 secret-key runtime lifecycle and cleanup needed hardening. |

## Finding-To-Mechanism Analysis

Rather than repeat 40 full dossiers, this table lists each reusable hunt recipe and false-positive killer.

| Finding group | Generic invariant and missing property | Hunt recipe | False-positive killers |
| --- | --- | --- | --- |
| IBC callback and client recovery | Cross-domain state must commit only after protocol success; recovery must derive copied state from verified current client state. | Compare callback mutation, acknowledgement, recovery, and proposal paths for cached context use and caller-selected historical ranges. | Whole operation already runs in a transactional context; recovery fields are ignored or rederived from verified state. |
| Consensus-visible determinism | Consensus-visible bytes and iteration order must be deterministic across nodes. | Search error strings, precompile return data, acknowledgements, map iteration, and node-local diagnostics that can enter app hash/results hash. | Data is not committed; strings are fixed protocol constants; final state is order-independent. |
| Authorization and identity binding | Privileged state changes must authorize against canonical ownership/association state; signatures must bind exact message and replay domain. | Compare default-derived identities, placeholder signature hashes, chain-ID branches, and registration sinks against canonical owner/mapping state. | Later sink revalidates the exact identity; generated payload is read-only; path is disabled or test-only. |
| Cross-runtime precompile adapters | Alternate runtimes must use canonical Msg validation and enforce concrete entrypoint scope before value transfer or governance mutation. | Compare EVM precompiles to native Cosmos MsgServer paths; inspect generic/scoped entrypoints that discard concrete validated message types. | Direct keeper method performs identical validation; downstream transfer independently scopes amount/type/runtime. |
| Resource and peer abuse controls | Untrusted work must be bounded and peer-attributed with correctly scoped penalties and lifecycle cleanup. | Inspect gas meters in lifecycle hooks, subscription maps, CheckTx counters, peer eviction hooks, and blacklisting scopes. | Endpoint is private/rate-limited; failure is ordinary user invalidity, not peer abuse; counters are diagnostic only. |
| Ledger/execution parity | Alternate execution and mempool bookkeeping must record side effects only at the same boundary as final acceptance and canonical accounting. | Build before/after accounting models for ante, EndBlock, giga/alternate execution, pending nonce, surplus, store flushes, and migrations. | Alternate path is disabled; invariant finalizer aborts before commit; bookkeeping is advisory only. |
| Consensus certificate and proposal lifecycle | Consensus proposal, timeout, and certificate state must be bound to verified role, range, header, lock, and commit identity across transitions. | Trace view/round/commit transitions, needed-and-verified predicates, stored versus incoming certificate data, reconstruction over stale proposal state, and lock inheritance. | Canonical verifier rechecks before mutation; protocol restores locks elsewhere; mismatched proposals are cleared before commit. |
| Proof and decode boundary validation | Proof/domain objects must reject malformed structure and required empty fields explicitly before callers can treat them as valid. | Search nil/empty sentinels, protobuf conversion, missing required vote lists, proof reconstruction, and callers that treat no-error as success. | Object is local-only; later Verify always rejects before use. |
| Production-mode and secret lifecycle hardening | Test/mock state mutation and secret-key memory lifecycle must fail closed in production and preserve intended runtime reachability. | Inspect build tags, mock funding, read paths that mutate balances, cleanup/finalizer callbacks, raw key pointers, and signing keepalive. | Build cannot ship to production; all mutation paths have direct network guards; key path handles only public/test material. |

## Family Clustering

1. Consensus-visible determinism and result serialization  
Findings: `a613471d8`, `b5f113295`, `0156e75d7`, `b5f8936e8`. Portable. Existing prompts mention determinism, but they underemphasize error-return data and precompile/ABCI result data as consensus sinks.

2. Consensus certificate/proposal lifecycle binding  
Findings: `f45028f01`, `4d45fcdc8`, `1a3758d85`, `f5844b5a6`, `8d751f648`, `1da04435c`, `caebdeaa5`. Portable. Existing consensus prompt is close, but should add lock/certificate inheritance and "needed-and-verified predicate must also gate mutation."

3. Cross-runtime adapter and precompile parity  
Findings: `56ce9a974`, `78eb1d663`, `a2aa14179`, `beccf236c`, `0332c4a9d`, `b36bfe41b`, `d35634422`. Portable across chains with EVM/Cosmos/Wasm/precompile adapters. Existing auth/signature prompts partly cover it; Base Hunter should more directly ask for native-vs-adapter parity.

4. Peer feedback, resource bounds, and abuse-scope hygiene  
Findings: `e3373eba5`, `e52126b92`, `e8e4b3bf4`, `1da04435c`, `f6d7875ab`, `7c3df71f7`, `65bedcfef`, `107c8e793`. Portable. Existing peer/resource prompts cover some pieces, but not penalty scope and lifecycle ownership strongly enough.

5. Ledger/accounting and alternate execution parity  
Findings: `a2ab1c532`, `48090d81b`, `d9f1de1a4`, `562746653`, `4523d3d13`, `bded875b1`. Portable. Existing ledger prompt is strong; add alternate execution and early bookkeeping boundaries.

6. Proof/decode fail-closed boundaries  
Findings: `b8d1c3a2d`, `8d751f648`, `9836e33a2`, `9b9e33970`. Mostly existing prompts cover these; refine proof/decode required-field language and keep crypto dependency/secret lifecycle mostly corpus/provenance unless a repo has similar crypto surface.

## Prompt-Pack Comparison

| Cluster | Current coverage | Decision |
| --- | --- | --- |
| Consensus determinism | Split across `13`, `19`, `22`, `02`; lacks a crisp "consensus-visible diagnostics/result bytes" hunt. | Refine `19` and `02`. |
| Consensus certificate lifecycle | `19` covers proposal validation, but weak on view-change lock inheritance and needed/verified mutation symmetry. | Refine `00`, `01`, `19`, `02`. |
| Cross-runtime adapters | `10`, `11`, `22` cover pieces, but native-vs-adapter parity should be elevated. | Refine `00`, `01`, `10`, `11`, `22`. |
| Peer/resource abuse scope | `21` is strong for sync, weaker for mempool penalty scope and counter ownership. | Refine `21`, `14`, `01`, `02`. |
| Ledger/alternate execution parity | `22` is strong, but add alternate store flush and early mempool bookkeeping. | Refine `22`, `01`, `02`. |
| Proof/decode fail-closed | `13` and `20` are good; add nil/empty sentinel and required-field domain conversion wording. | Refine `13`, `20`. |
| Production-mode/secret lifecycle | Too dependent on repo features; existing `13` can mention production guard and key lifecycle. | Small refine to `13`; no new family. |

## Proposed Prompt Changes

### `/testing/dlt-ai-audit-system/00_protocol_mapper.md`

Add under the architecture/trust-boundary mapping steps:

```text
Map all cross-runtime adapter surfaces separately: precompiles, wasm query payload builders, EVM-to-native message dispatch, native-to-EVM receipt/accounting bridges, and legacy compatibility adapters. For each adapter, identify the canonical native path it should match, the exact identity/address association source, the validation function or MsgServer it should reuse, and the final value-transfer, governance, or accounting sink.

Map consensus-visible result data separately from state writes. Include acknowledgements, ABCI result data, precompile return bytes, error strings, receipt data, app-hash or results-hash inputs, and any deterministic ordering assumptions such as map iteration.

For consensus certificates and view/round transitions, map which certificate is authoritative, which locks or proposal identities it carries forward, where verification happens, and where the verified certificate data is later used to mutate local state or emit votes.
```

Rationale: This would have pushed an auditor toward Sei's precompile parity, nondeterministic error data, IBC acknowledgement, and Autobahn lock/certificate findings without naming those paths.

### `/testing/dlt-ai-audit-system/01_base_hunter.md`

Add to the search checklist:

```text
Compare adapter entrypoints against their canonical native entrypoints. For every precompile, cross-runtime query helper, legacy RPC adapter, or compatibility transaction path, ask whether it reuses the same validation, address association, chain/replay domain, message type, and final sink as the native path.

Search for early side effects that are recorded before final admission or success: pending nonces, peer penalties, callback writes, accounting deltas, generated receipts, cached proposal blocks, and temporary store writes. Check whether every later rejection, timeout, panic, or failed acknowledgement rolls them back or avoids recording them until acceptance.

In consensus and p2p lifecycles, compare the predicate that verifies an object with the predicate that later mutates state from it. A certificate, peer response, stream discriminator, or proposal that was not needed or verified for the current transition must not still drive stored state, emitted votes, or allocation.
```

Rationale: Captures the strongest recurring Sei code shape: validation and mutation decisions living at different boundaries.

### `/testing/dlt-ai-audit-system/02_validation_and_impact.md`

Add to validation questions:

```text
If bytes returned from an error path can enter consensus-visible results, acknowledgements, receipts, or hashes, prove they are deterministic protocol bytes rather than raw error strings, stack details, local paths, map iteration order, or environment-dependent diagnostics.

If the issue is in an adapter path, compare it to the canonical native path and state exactly which property differs: address association, message validation, chain/replay domain, concrete entrypoint scope, gas/accounting, return-data determinism, or final sink authorization.

If the issue is in peer penalty or blacklisting logic, distinguish peer abuse from ordinary invalid user transactions. A real issue should show either under-penalized invalid peer input, over-broad penalties that can harm honest peers, or lifecycle cleanup that lets stale counters affect future decisions.
```

Rationale: Improves severity discipline for likely hardening cases, especially where Sei findings were retained but not proven exploitable.

### `/testing/dlt-ai-audit-system/prompts/10_authz_and_role_gates.md`

Add to search patterns:

```text
- Cross-runtime adapters, precompiles, and query payload builders that accept an identity in one address namespace and execute or construct payloads in another. Require explicit state-backed association at the adapter boundary and revalidate concrete message type, caller runtime, and destination before any value transfer or privileged state mutation.
- Alternate entrypoints that call keepers, managers, or storage helpers directly instead of constructing the canonical message object and using the same validation/dispatch path as native transactions.
```

Rationale: Generalizes the wasm/EVM address-association, gov precompile, and Solo precompile findings.

### `/testing/dlt-ai-audit-system/prompts/11_signature_binding_and_signer_scope.md`

Add to search patterns:

```text
- Account association, address binding, or identity-linking transactions where signer recovery uses a placeholder hash, empty message, legacy compatibility signer, or side-channel message field instead of the exact serialized message the user signed.
- Replay-domain checks that differ between legacy and typed transaction formats. Verify that compatibility branches reject unsafe unprotected formats unless an explicit non-production or test mode is active.
```

Rationale: Transfers the AssociateTx and EVM chain-ID/legacy tx lessons without hardcoding Sei.

### `/testing/dlt-ai-audit-system/prompts/13_input_validation_and_invariant_enforcement.md`

Add to search patterns:

```text
- Protobuf, JSON, RLP, or domain-conversion code that turns empty lists, nil roots, absent required fields, or malformed nested structures into valid domain objects. Required consensus/proof fields should fail closed at the conversion boundary, not later through panics, nil sentinels, logs, or partial outputs.
- Production safety guards for test, mock, simulation, or fixture-only state mutation helpers. A read path should not lazily mint, top off, or mutate state, and production-network guards should sit on every mutation sink rather than only on constructors.
```

Rationale: Covers Merkle proof shape, TimeoutQC decode validation, and mock-balance guard patterns.

### `/testing/dlt-ai-audit-system/prompts/14_resource_accounting_and_limits.md`

Add to search patterns:

```text
- Lifecycle-triggered contract execution, precompile execution, and block hook callbacks that swap gas meters, temporary stores, or execution contexts. The temporary meter must inherit the parent bound, and expected out-of-gas errors should fail closed without hiding unexpected panics.
- Long-lived subscriptions, listeners, peer maps, and stream state where the allocation/registration point is separate from config parsing. Enforce limits under the same lock or reservation policy that mutates the retained collection.
```

Rationale: Captures Wasm sudo gas and websocket subscription limit findings.

### `/testing/dlt-ai-audit-system/prompts/19_consensus_fork_and_payload_rule_validation.md`

Add to search patterns:

```text
- Consensus-visible error, acknowledgement, receipt, precompile return, or result data built from raw errors or local diagnostics. These bytes must be deterministic protocol outputs if they can affect app hashes, results hashes, or replicated state.
- View, round, timeout, or commit transitions where a certificate carries a lock, proposal identity, part-set header, or latest quorum state into the next step. Verify that state clearing, reconstruction, timeout vote emission, and commit handling preserve the certified identity rather than falling back to empty or stale local state.
- Verification predicates such as "needed", "current", "fresh", or "verified" must gate every later mutation derived from that object. Do not let stale or unnecessary certificates update ranges, headers, block matching, or emitted votes.
```

Rationale: This is the highest-impact Sei refinement: it would have helped surface Autobahn and consensus-result determinism issues.

### `/testing/dlt-ai-audit-system/prompts/21_peer_sync_progress_and_response_binding.md`

Add to search patterns:

```text
- Peer-abuse counters whose ownership is split from peer lifecycle ownership. If the reactor owns peer identity, disconnect, and cleanup events, counters that drive eviction should live there or be explicitly cleaned up there.
- Blacklist or eviction triggers attached to broad validation failures. Distinguish malformed, oversized, invalid-protocol, no-progress, and ordinary application-invalid inputs before penalizing a peer.
- P2P mux or stream discriminators where a missing kind, mismatched kind, or default kind can create or reuse a stream under the wrong resource bucket.
```

Rationale: Transfers the mempool blacklist, stale counter, invalid peer, and mux stream-kind lessons.

### `/testing/dlt-ai-audit-system/prompts/22_ledger_accounting_and_invariant_coverage.md`

Add to search patterns:

```text
- Alternate execution engines or fast paths that finalize state through different stores, caches, or deferred metadata. Check that finalized deltas, fee/surplus accounting, receipt data, and writes are propagated and flushed before canonical bank, EndBlock, or invariant code reads them.
- Mempool or admission bookkeeping that affects future transaction ordering, nonce eligibility, or promotion. Record it only at final admission or prove every later rejection path rolls it back.
```

Rationale: Covers Giga EVM accounting, EVM surplus, and stale pending nonce without overfitting to Sei names.

## New Family Prompts

No new prompt family is justified. Every reusable mechanism fits cleanly into existing families:

- Cross-runtime adapter parity belongs in authz/signature/ledger plus Base Hunter.
- Consensus certificate lifecycle belongs in consensus fork/payload validation.
- Peer penalty ownership belongs in peer sync/progress.
- Deterministic consensus-visible result data belongs in consensus validation and validation/impact severity discipline.

Creating a new "Sei precompile" or "Autobahn" family would overfit.

## Validation Notes

Holdout check: I drafted the consensus certificate lifecycle wording using `4d45fcdc8`, `1a3758d85`, and `f45028f01`, then checked it against the held-out `f5844b5a6` timeout-lock finding. The proposed `19` text about lock-bearing certificates and emitted votes would have led an auditor to inspect exactly the right class of transition without naming PrepareQC or Autobahn.

Second holdout check: I drafted the cross-runtime adapter wording from the address-association and gov-precompile findings, then checked it against the held-out Solo precompile claim-scope finding. The proposed `10` and `01` text still applies because it asks for concrete message type, caller runtime, and final value-transfer sink parity.

Remaining doubts:

- Crypto dependency CVE and Ed25519 memory lifecycle findings are useful corpus examples but weak runtime prompt drivers unless a target repo has similar crypto ownership APIs.
- Traffic-analysis hardening is portable but lower-priority; the current trust/crypto prompts can absorb it through encrypted transport mapping rather than a new prompt.
- Some likely-hardening findings should influence validation severity wording more than hunting instructions, because the hunt signal is real but exploitability is intentionally bounded.

Prompts that can stay structurally unchanged:

- `12_attestation_trust_and_freshness.md`: no Sei cluster required a new attestation/trust-root concept.
- `17_checked_arithmetic_and_parameter_bounds.md`: none of the kept findings were primarily arithmetic.
- `18_authoritative_state_and_boundary_enforcement.md` and `20_authenticated_state_proof_and_persistence_integrity.md`: already cover most proof/state-boundary lessons; the small additions above to `13`/`20` are enough.
