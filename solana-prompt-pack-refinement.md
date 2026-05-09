# Solana Prompt-Pack Refinement From Validated Findings

Target repo: `/testing/solana`

Evidence set: `/testing/solana/validated-findings/kept`

Prepared from prompt: `/testing/dlt-ai-audit-system/04_refine_prompt_pack_from_findings.md`

## 1. Repo Context Summary

Solana is an account-ledger validator implementation with signed client transactions, TPU leader ingestion, TVU replay, Bank/BankForks state, SBF/BPF/native program execution, stake/vote economics, gossip/repair/shred networking, snapshots, and RPC/admin surfaces. The main security boundaries in these findings are:

- signed client transaction or instruction -> Bank/SVM/account state,
- program/CPI frame -> runtime privilege and writable-account enforcement,
- peer packet/gossip/repair/shred -> validator network, replay, and repair state,
- persisted/snapshot/ledger material -> trusted Bank reconstruction,
- stake/vote account mutation -> leader schedule, voting power, rewards, and withdrawal state,
- validator/operator configuration -> live network exposure and authority handling.

High-risk entrypoints recurring in the findings are transaction sanitization, native program processing, CPI, account locking, durable nonce handling, rent/reward/stake transitions, gossip CRDS and repair responses, QUIC/UDP ingestion, snapshot loading, fork/replay/root updates, and RPC/admin/validator ops. The state-machine patterns that matter most are admission vs execution vs replay parity, immediate reservation vs delayed logging or batching, feature/rent/stake epoch gates, failed-transaction cleanup, consensus vote/fork transitions, and startup/recovery persistence.

## 0. Finding Inventory

The kept folder contains `139` findings. All were analyzed; none were intentionally skipped.

The generated/enriched corpus bundle at `/testing/dlt-ai-audit-system/corpus/imports/20260509-161152Z-solana` now contains per-finding enriched records/cards/evals. Those records are the detailed per-finding mechanism analysis artifacts: each has violated invariant, missing property, trust boundary, entrypoint type, sensitive sink, code-shape summary, hunt motifs, and false-positive cautions.

Inventory by imported family:

| Family | Count |
| --- | ---: |
| `input_validation_and_invariant_enforcement` | 97 |
| `authz_and_role_gates` | 14 |
| `signature_binding_and_signer_scope` | 9 |
| `attestation_trust_and_freshness` | 5 |
| `checked_arithmetic_and_parameter_bounds` | 5 |
| `resource_accounting_and_limits` | 4 |
| `staking_registry_and_accountability` | 3 |
| `state_machine_and_lifecycle_consistency` | 2 |

Representative finding groups:

- Double-spend and nonce/replay state: `2018-03-02-solana-cryptography-36bb1f989d`, `2020-11-24-solana-transaction-processing-db3f154b3f`, `2022-06-03-solana-transaction-processing-5ee157f43d`, `2022-06-08-solana-cryptography-165ee12ed4`.
- Account/CPI privilege and mutability: `2019-02-15-solana-core-logic-132c664e18`, `2020-05-26-solana-storage-8c8e2c4b2b`, `2021-01-22-solana-cryptography-77572a7c53`, `2021-01-23-solana-cryptography-480a35d678`, `2021-05-28-solana-consensus-2f7f243022`, `2021-09-09-solana-transaction-processing-3eee222667`.
- Transaction/packet sanitization and boundary shape: `2019-05-20-solana-transaction-processing-ead15d294e`, `2020-05-02-solana-transaction-processing-fa254ff18f`, `2020-08-05-solana-transaction-processing-7b8e5a9f47`, `2021-07-01-solana-cryptography-03d213d764`, `2022-06-20-solana-cryptography-e71f56c3f2`.
- Network ingress and resource attribution: `2020-10-28-solana-cryptography-ae91270961`, `2020-10-29-solana-cryptography-06067dd823`, `2022-06-02-solana-cryptography-a781cff386`, `2022-06-22-solana-consensus-5b864ef97d`.
- Consensus/replay/fork/root state: `2019-03-18-solana-staking-61a4b998fa`, `2019-06-20-solana-cryptography-aacb38864c`, `2020-04-02-solana-consensus-4649378f95`, `2020-12-15-solana-consensus-db339cb925`, `2021-10-15-solana-consensus-44ff30b65b`, `2023-09-05-solana-consensus-a8e83c8720`.
- Snapshot, bootstrap, and authenticated persistence: `2019-12-20-solana-cryptography-3c361eb759`, `2020-01-15-solana-cryptography-b16c30b4c6`, `2020-02-26-solana-consensus-87cfac12dd`, `2020-03-16-solana-cryptography-dc347dd3d7`, `2022-08-26-solana-transaction-processing-c846221bb8`.
- Stake/rent/reward accountability: `2019-07-31-solana-staking-1a0003fbcc`, `2019-10-29-solana-staking-a587d05098`, `2020-08-17-solana-staking-d9ae092637`, `2021-12-07-solana-consensus-89d2f34a03`, `2022-02-24-solana-transaction-processing-3bee925967`.
- Signature, signer, and authenticated identity: `2018-10-26-solana-transaction-processing-cda9ad8565`, `2018-12-01-solana-cryptography-34c3a0cc1f`, `2019-03-08-solana-p2p-networking-c8c85ff93b`, `2020-05-08-solana-cryptography-f98bfda6f9`, `2023-02-15-solana-cryptography-cf0a149add`.

## 2. Finding-To-Mechanism Analysis

Per-finding analysis is materialized in the enriched records:

- Record path pattern: `/testing/dlt-ai-audit-system/corpus/imports/20260509-161152Z-solana/records/solana-<finding>.yaml`
- Root-cause card path pattern: `/testing/dlt-ai-audit-system/corpus/imports/20260509-161152Z-solana/cards/root-cause/solana-<finding>.md`
- Code-shape card path pattern: `/testing/dlt-ai-audit-system/corpus/imports/20260509-161152Z-solana/cards/code-shape/solana-<finding>.md`
- Validation card path pattern: `/testing/dlt-ai-audit-system/corpus/imports/20260509-161152Z-solana/cards/validation/solana-<finding>.md`

The reusable mechanisms extracted from those records are:

| Mechanism | Generic invariant | Hunt recipe | False-positive killers |
| --- | --- | --- | --- |
| Immediate reservation and delayed accounting | Accepted spend, nonce, or reservation state must update before later checks can observe stale availability. | Compare admission, logging, batching, failed execution, replay, and retry paths for state recorded before or after acceptance. | Shared finalizer updates state on every path; delayed state is never consulted for future acceptance; path is test-only. |
| Account privilege and mutability containment | The final write/CPI/syscall sink must enforce the exact owner, signer, writable, duplicate-account, and read-only constraints consumed by execution. | Trace account metas from transaction message through sanitization, CPI propagation, duplicate account handling, and copy-back. | Runtime callee revalidates all account privileges; helper consumes canonical account metadata; caller cannot choose account aliases. |
| Canonical sanitization before classification | Malformed packet, transaction, signature, sysvar, or native-loader input must be rejected before it is classified, scheduled, parsed with panicking helpers, or used to allocate. | Compare raw transport bytes, sanitized transaction/message type, and final runtime classification. Look for weak fast paths and helper builders. | Canonical parser is mandatory on all paths; panics are unreachable after type-level validation; malformed cases return structured errors. |
| Peer/network endpoint and resource attribution | Untrusted network input must be bound to a canonical peer/endpoint and charged or bounded before it triggers larger responses or retained state. | Compare UDP/QUIC/gossip/repair ingress, spoofable source metadata, per-stake admission, invalid input accounting, and response amplification. | Endpoint is cryptographically or session-bound; pre-auth limits are tighter than post-auth; invalid/duplicate/no-progress outcomes update accounting. |
| Consensus replay and fork-state transition parity | Vote, fork, duplicate-slot, repair, and root decisions must use the same verified identity and state coordinate that later mutates replay/fork-choice state. | Compare live replay, startup replay, duplicate recovery, repair retry, vote generation, root setting, and status publication. | Object was verified as needed for the current transition; stale/unneeded evidence cannot mutate state; all equivalent replay modes call the same validator. |
| Authenticated persistence and snapshot/bootstrap binding | Snapshot, accounts hash, genesis, bootstrap, and state-root material must be recomputed or bound to the requested slot/root/fork before trust or service readiness. | Map startup/recovery paths and compare archive, snapshot dir, status cache, accounts hash, slot deltas, and bootstrap trust checks. | Startup fails closed on missing/mismatched material; derived artifacts are range/root bound; verification covers every later-used artifact. |
| Stake/rent/reward and epoch accountability | Stake, vote, rent, withdrawal, reward, and redelegation transitions must preserve epoch-scoped economic invariants and dependent state. | Build before/after models for stake activation, withdrawal, rent exemption, reward settlement, and pending operations. | A mandatory final invariant pass covers all dependent entries; settlement uses immutable earning-period snapshot; pending operations are capped cumulatively. |
| Signature/signer/authenticated identity scope | A verified signature must bind the exact message type, domain, signer role, replay coordinate, and downstream identity used by the sink. | Compare signing and verifying constructors, legacy branches, disabled verification modes, signature length checks, and payload/metadata splits. | Canonical typed message includes all sink-relevant fields; disabled verification is unreachable in production; exact-length and domain checks happen before authorization. |
| Hardening-only evidence discipline | Boundary-tightening commits should be retained as hunt lessons without overstating exploitability. | When a finding is likely/security-hardening, keep the invariant and code shape but require attacker capability and end-to-end reachability before severity inflation. | Patch is diagnostic, test-only, or operator-only; exploitability is not demonstrated; compensating control already exists in production path. |

## 3. Family Clustering

All clusters are portable across account-ledger, validator, p2p, and VM-based DLT systems. None is Solana-only, but several are especially visible in Solana because account metadata and replay paths are first-class protocol state.

| Cluster | Findings grouped | Portable lesson | Runtime prompt action |
| --- | --- | --- | --- |
| Immediate reservation and delayed accounting | double spend, durable nonce, failed transaction state, replay-domain collision | Admission and future eligibility cannot depend on state updated later by logging, batching, or replay. | Refine `01_base_hunter.md`, `15_state_machine...`, `22_ledger_accounting...`. |
| Account privilege and mutability containment | read-only mutation, writable-account validation, CPI duplicate privilege, owner validation | Account meta privileges are capabilities; every adapter and nested call must preserve or narrow them. | Refine `10_authz...`, `13_input_validation...`, `24_memory_contract...`. |
| Canonical sanitization before classification | signature length, packet bounds, off-curve address, sysvar/native-loader input, transaction sanitization order | Reject malformed raw bytes and semantically invalid shapes before classification, allocation, or scheduling. | Refine `13_input_validation...`, `11_signature...`, `24_memory_contract...`. |
| Peer/network endpoint and resource attribution | UDP reflection, QUIC stake admission, network admission, ingress resource limiting | Peer work needs endpoint binding plus symmetric accounting for invalid and no-progress input. | Refine `14_resource...`, `21_peer_sync...`. |
| Consensus replay and fork-state transition parity | locktower, invalid fork handling, duplicate slots, repair retry, consensus state publication race | Verified evidence must be current and needed for the mutation it drives. | Refine `19_consensus...`, `15_state_machine...`. |
| Authenticated persistence and bootstrap binding | snapshot validation, accounts-hash alignment, bootstrap trust, genesis blockhash | Startup/recovery should not launder unbound persisted material into trusted Bank state. | Refine `20_authenticated_state...`, `12_attestation...`, `00_protocol_mapper.md`. |
| Stake/rent/reward accountability | stake withdrawal, redelegation, rent exemption, reward accounting | Economic/accountability state often spans pending, epoch, and dependent-object coordinates. | Refine `16_staking...`, `22_ledger_accounting...`. |
| Signature and identity scope | incomplete signature verification, gossip signature integrity, disabled verification path, signature commitment | Signature validity is not signer scope, domain binding, or production-mode enforcement. | Refine `11_signature...`, `02_validation...`. |

## 4. Prompt-Pack Comparison

The current prompt pack already covers most Solana lessons in broad form. The weak points are not missing top-level families; they are places where prompts mention the abstract concept but do not sufficiently push the auditor toward Solana-style account-ledger shapes:

- Account capability propagation is split across authz, input validation, and memory/runtime prompts. The pack should explicitly tell auditors to trace account metas/privileges through nested execution and copy-back.
- Network amplification and endpoint spoofing are covered by resource and peer-sync prompts, but UDP/QUIC-style unauthenticated pre-session response amplification should be called out more directly.
- Durable nonce and failed transaction side effects are present in base hunter/state-machine prompts, but ledger accounting should also ask about failed execution carrying persistent nonce, rent, fee, or reservation effects.
- Consensus replay prompts cover forks/payloads well, but Solana findings show a need to phrase “verified object was needed/current for this transition” as a reusable sink-side mutation check.
- Validation prompt already has hardening guidance, but Solana has 114 likely hardening findings, so a sharper checklist for not overclaiming hardening impact would improve consistency.

No new family prompt is justified. Existing families can express the lessons cleanly:

- `22_ledger_accounting_and_invariant_coverage.md` covers account-ledger economics.
- `24_memory_contract_and_buffer_ownership.md` covers packet/buffer/syscall boundary issues.
- `21_peer_sync_progress_and_response_binding.md` covers peer-driven progress/resource issues.
- `19_consensus_fork_and_payload_rule_validation.md` covers replay/fork/duplicate-slot state.

## 5. Proposed Prompt Changes

### Change A: strengthen `01_base_hunter.md`

Target: `/testing/dlt-ai-audit-system/01_base_hunter.md`

Add after item `25`:

```text
25a. Search delayed-accounting pipelines where an operation is accepted before the state used for future eligibility is updated, such as spend balance, nonce, replay cache, reservation counter, duplicate signature set, rent status, fee debit, or pending stake/reward state. Compare immediate admission, logging, batching, replay, failed execution, and retry paths; a later operation must not observe stale availability created by delayed persistence.
```

Rationale: Solana had recurring stale balance, nonce, retry, and delayed accounting patterns. This wording is generic and avoids accountant/historian or Solana-specific naming.

Overfitting risk check: low. Applies to any DLT with nonces, reservations, mempool/replay state, or batched persistence.

### Change B: strengthen `13_input_validation_and_invariant_enforcement.md`

Target: `/testing/dlt-ai-audit-system/prompts/13_input_validation_and_invariant_enforcement.md`

Add to search patterns near existing transaction/header generic enum bullets:

```text
- account-ledger transaction objects where raw account metas, signer flags, writable flags, duplicate-account aliases, sysvar/native-account markers, address-table entries, or off-curve derived addresses are sanitized in one layer but consumed in another. Build a raw-message -> sanitized-message -> loaded-account -> execution-frame matrix and require exact cardinality, canonical account identity, and privilege monotonicity before state transition.
- packet, frame, or transaction buffers that are classified, sliced, or scheduled before exact signature length, payload length, trailing bytes, and minimum header boundaries are checked against the original attacker-controlled bytes.
```

Rationale: Captures Solana’s transaction sanitization ordering, packet bound, account mutability, sysvar, and off-curve-address lessons without naming Solana.

Overfitting risk check: medium-low. “Account-ledger” is a generic architecture class; the instruction translates to UTXO/account/VM systems with account metadata.

### Change C: strengthen `10_authz_and_role_gates.md`

Target: `/testing/dlt-ai-audit-system/prompts/10_authz_and_role_gates.md`

Add to search patterns near account/object authorization bullets:

```text
- nested execution, adapter, or cross-program calls where the caller supplies multiple references to the same underlying state object. Verify that signer, writable, readonly, owner, delegate, and duplicate-alias privileges are intersected or re-derived at the final sink, never widened by a later alias or copied from an unchecked frame.
- lifecycle or withdrawal authority that is distinct from reward owner, vote signer, stake controller, fee payer, program upgrade authority, or broad account owner. Check that each sink loads the authority field that governs that exact transition instead of accepting any related signer.
```

Rationale: Solana findings repeatedly involved account aliases, CPI privilege propagation, vote/stake authority distinctions, and unsafe broad authority assumptions.

Overfitting risk check: low. Generic for account/object ledgers, cross-runtime adapters, staking, and upgradeable programs.

### Change D: strengthen `14_resource_accounting_and_limits.md`

Target: `/testing/dlt-ai-audit-system/prompts/14_resource_accounting_and_limits.md`

Add to search patterns near pre-authentication peer connection and invalid-input accounting bullets:

```text
- unauthenticated or weakly authenticated datagram, gossip, discovery, repair, or handshake requests where a spoofable source address or cheap request can trigger a larger response, table lookup, signature verification fanout, stake lookup, retransmit, or connection allocation. Bind the response to a proven endpoint/session or cap the response to non-amplifying work before any expensive or larger output is produced.
- stake-, weight-, or reputation-tiered resource policies where the tier is looked up after accepting packets, opening streams, or allocating buffers. The cheapest pre-tier boundary should enforce a conservative default limit, and invalid or unverifiable tier claims should be charged to the lowest tier.
```

Rationale: Solana’s UDP/QUIC and stake-weighted ingress hardening cluster benefits from more explicit endpoint-amplification wording.

Overfitting risk check: low. Applies to any p2p DLT using UDP, QUIC, discovery, repair, gossip, or stake-weighted QoS.

### Change E: strengthen `15_state_machine_and_lifecycle_consistency.md`

Target: `/testing/dlt-ai-audit-system/prompts/15_state_machine_and_lifecycle_consistency.md`

Add to search patterns near replay/recovery and asynchronous validation bullets:

```text
- validator or executor state reconstructed after restart, snapshot load, replay, or repair where live execution retained a wider window of nonce, reservation, duplicate, congestion, vote, or progress state than recovery rebuilds. The recovered state must be either committed in an authenticated digest/snapshot or conservatively fail closed.
- evidence-driven state transitions where an object was verified earlier as syntactically valid, fresh, or useful, but the later mutation occurs after fork view, root, duplicate-slot status, peer state, or local progress has changed. Re-check that the evidence is still needed for the exact transition before mutating state, emitting votes, or scheduling repair.
```

Rationale: Solana’s replay, duplicate slot, repair retry, and restart-precondition findings teach sink-time freshness of evidence, not just validation at observation time.

Overfitting risk check: low. Portable to consensus clients, rollups, bridge relayers, and p2p repair/sync systems.

### Change F: strengthen `19_consensus_fork_and_payload_rule_validation.md`

Target: `/testing/dlt-ai-audit-system/prompts/19_consensus_fork_and_payload_rule_validation.md`

Add to search patterns near proposal/validation consensus and duplicate suppression:

```text
- replay or repair paths that can mark a slot, block, proposal, or batch as dead, duplicate, confirmed, repaired, or safe based on evidence gathered under an older fork view. The mutation should bind evidence hash, parent, root, duplicate status, and current fork-choice context, and should distinguish invalid data from temporarily incomplete data.
- vote-generation or fork-switch logic where the selected target is derived from latest, heaviest, propagated, duplicate-confirmed, or same-voted-fork state. Check that every target passes the same lockout, switch-threshold, duplicate, propagation, and ancestor checks immediately before vote emission.
```

Rationale: Sharpens replay/vote/fork transition analysis for Solana-like Tower/BFT systems while staying generic.

Overfitting risk check: low. Applies to any fork-choice protocol with replay, repair, duplicate proposals, or vote lockouts.

### Change G: strengthen `20_authenticated_state_proof_and_persistence_integrity.md`

Target: `/testing/dlt-ai-audit-system/prompts/20_authenticated_state_proof_and_persistence_integrity.md`

Add to search patterns near snapshots and catchup verification:

```text
- snapshot or checkpoint loaders that restore execution status caches, account/storage deltas, epoch metadata, rent/reward state, or recent-blockhash queues alongside the root state. Verify every restored auxiliary artifact is bound to the same slot/root/hash range as the account state before replay or client serving uses it.
- account-hash or state-root verification that compares only the final aggregate while auxiliary state, skipped ranges, zero-lamport/deleted entries, or duplicate storage entries can change the reconstructed bank semantics. Build an artifact matrix for account data, metadata, status cache, slot deltas, and replay roots.
```

Rationale: Solana findings included snapshot validation, accounts-hash alignment, and validator-state consistency hardening.

Overfitting risk check: medium-low. “Account/storage deltas” are generic for account-ledger and state-root systems.

### Change H: strengthen `16_staking_registry_and_accountability.md`

Target: `/testing/dlt-ai-audit-system/prompts/16_staking_registry_and_accountability.md`

Add to search patterns:

```text
- stake, vote, reward, rent, or withdrawal transitions whose validity depends on an epoch boundary or historical earning period. Compare admission-time account state, pending operations, effective stake, deactivation/activation state, and settlement-time snapshot; live state must not rewrite the history that earned the payout or accountability obligation.
- cumulative pending operations such as redelegation, withdrawal, split, merge, close, deactivate, or rent-state changes where each operation is individually valid but the aggregate pending set can violate minimum balance, rent exemption, reward denominator, slashability, or validator eligibility invariants.
```

Rationale: Solana’s stake/rent/reward findings are strongest when framed as epoch/pending-set accountability, not only generic stake checks.

Overfitting risk check: low. Applies to staking, validator collateral, delegator accounting, and committee bonds.

### Change I: strengthen `02_validation_and_impact.md`

Target: `/testing/dlt-ai-audit-system/02_validation_and_impact.md`

Add after the existing security-hardening paragraph:

```text
When many findings in a family are hardening-only, explicitly separate three evidence levels:
1. direct exploit fix: attacker-controlled input reaches the sink and the patch blocks it;
2. boundary hardening: a consensus, validator, peer, or accounting boundary is tightened but exploitability is not demonstrated;
3. diagnostic or safety posture: tests, logs, config warnings, or operator defaults improve safety but do not change production acceptance.
Only level 1 should drive High/Critical impact claims. Level 2 can remain Medium when the boundary is consensus-, funds-, validator-, or resource-sensitive. Level 3 should usually be Low or Informational unless a production trust boundary is proven.
```

Rationale: The Solana set has 114 likely/security-hardening items. This would reduce overclaiming while preserving reusable hunt value.

Overfitting risk check: low. Applies to all historical corpus imports and future audits.

### Change J: update provenance, not runtime prompts

Target: `/testing/dlt-ai-audit-system/finding-to-prompt-map.md`

Add a Solana calibration addendum summarizing the 139 findings by family and a compact mapping table generated from `manifest.json`. Keep this out of runtime prompts.

Rationale: The prompt pack already has provenance sections for Oasis, Reth, and Go-Ethereum. Solana adds strong account-ledger, CPI, stake/rent, replay, and network-ingress calibration without leaking answer paths into runtime prompts.

Overfitting risk check: low if kept as provenance only.

## 6. New Family Prompts

No new prompt family is justified.

The tempting candidate would be “account-ledger privilege and metadata consistency,” but it is better expressed as refinements to:

- `10_authz_and_role_gates.md`,
- `13_input_validation_and_invariant_enforcement.md`,
- `22_ledger_accounting_and_invariant_coverage.md`,
- `24_memory_contract_and_buffer_ownership.md`.

A new family would likely duplicate those prompts and make the taxonomy muddier.

## 7. Validation Notes

Holdout check performed:

- Held out signature-length/packet-boundary findings: `2021-07-01-solana-cryptography-03d213d764`, `2021-07-01-solana-cryptography-d5961e9d9f`, `2022-06-20-solana-cryptography-e71f56c3f2`. Proposed Changes B and C would still steer an auditor toward exact original-byte length checks and runtime boundary contracts.
- Held out rent/epoch-accountability findings: `2020-08-17-solana-staking-d9ae092637`, `2021-12-07-solana-consensus-89d2f34a03`, `2022-02-24-solana-transaction-processing-3bee925967`. Proposed Changes H and A would still steer an auditor toward pending/epoch/rent final-state invariants.
- Held out duplicate-slot/replay recovery finding: `2023-09-05-solana-consensus-a8e83c8720`. Proposed Changes E and F would still steer an auditor toward evidence freshness at mutation time.

Remaining doubts:

- The kept findings are historical and many are hardening-classified. The proposals intentionally strengthen hunt heuristics and validation discipline, not severity language.
- Some Solana findings are old pre-modern-architecture files; runtime prompts should not import historical file names or exact functions.
- The current prompt pack is already very broad. Applying every proposed line verbatim may increase prompt length; Changes A, B, D, E, F, H, and I are highest value.

Prompts that should stay unchanged:

- `23_zk_circuit_witness_and_public_data_binding.md`: Solana zk-token proof findings in this set did not surface a distinct circuit/witness-binding lesson beyond current coverage.
- `24_memory_contract_and_buffer_ownership.md`: already strong; Solana packet/buffer cases are better handled by linking it from `13` and `14` via Changes B/D rather than changing `24`.

