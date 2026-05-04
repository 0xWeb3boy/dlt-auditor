# AvalancheGo Prompt-Pack Refinement Proposal

Target repo: `/work/avalanchego`

Prompt-pack repo used: `/work/dlt-ai-audit-system`

Requested prompt: `/testing/dlt-ai-audit-system/04_refine_prompt_pack_from_findings.md`

Note: `/testing/dlt-ai-audit-system` is not mounted in this environment. The equivalent available checkout is `/work/dlt-ai-audit-system`.

## Repo Context Summary

AvalancheGo is a multi-chain node. The P-Chain/PlatformVM manages staking, validators, subnets, and cross-chain coordination. The C-Chain/Subnet-EVM/SAE paths reuse EVM-style transaction, txpool, header, gas, and RPC machinery with Avalanche-specific network upgrade and feature rules. Snowman consensus drives linear chains; ProposerVM wraps block production and verification around fork transitions and proposer authentication. Networking includes peer gossip, application messages, transaction propagation, and Warp message verification. Storage includes Go database layers plus Firewood/Merkle trie range proof logic.

Trust boundaries that matter for the kept findings:

- Peer-supplied blocks, proposer blocks, headers, and Warp-message-bearing transactions entering consensus or VM verification.
- RPC and gossip transactions entering txpool/mempool admission.
- Protocol/fork configuration crossing into validation of inherited EVM rules.
- Persisted staking metadata crossing into in-memory validator-set reconstruction.
- Raw Merkle trie/range query parameters crossing into authenticated proof generation.
- Staking management transactions crossing into validator lifecycle mutation.

High-risk entrypoint categories:

- Block parsing and verification: `vms/proposervm`, `plugin/evm`, `consensus/dummy`, `graft/coreth/plugin/evm`.
- Transaction admission: `core/tx_pool.go`, `core/state_transition.go`, `plugin/evm/mempool.go`, `vms/saevm/txgossip`.
- Staking lifecycle and accounting: `vms/platformvm/txs/executor`, `vms/platformvm/state`.
- Message verification: `vms/platformvm/block/executor`, `vms/platformvm/txs/executor`.
- RPC resource boundaries: `eth/gasprice/feehistory.go`.
- Authenticated state proofs: `firewood/src/merkle`, `firewood/src/iter`.

State-machine/lifecycle patterns:

- Fork activation changes object shape and validation semantics.
- Mempool admission has trusted/forced and untrusted/non-forced branches.
- Staking objects have separate reward owners, subnet owners, and management keys.
- Validator state is reconstructed from persisted transactions plus accrued metadata.
- Proof generation must bind requested bounds, returned data, and absence evidence.

## Finding Inventory

Source folder: `/work/avalanchego/validated-findings/kept`

Findings analyzed: all 17 kept findings.

No findings were intentionally skipped.

## Finding-to-Mechanism Analysis

| Finding | Repo-specific mechanism | Generic missing property | Hunt recipe | False-positive killers |
| --- | --- | --- | --- | --- |
| `2021-06-11...5fd30e32d5` | Proposer block signing/parent lookup moved from exported/stored fields to internal canonical fields and staking cert key. | Canonical signature representation binding. | Compare signed bytes, mutated signature fields, parent IDs, and verification fields for every signed consensus object with duplicate representations. | If all representations are normalized before signing/verifying, or the path is block construction only with no verifier mismatch. |
| `2021-08-03...0825857a2d` | EVM invalid-code rule used ApricotPhase4 instead of ApricotPhase3. | Exact fork activation binding. | For every fork-gated rule, build a before/at/after activation matrix and check adjacent-phase predicates. | Adjacent fork aliases or downstream mandatory rejection under the correct fork. |
| `2021-09-09...60bab8f7d4` | Pre-fork child verification needed state checks for parent/fork status after activation. | Fork-boundary parent/state consistency. | Search fork transition exceptions where type/shape checks need accepted-state facts before accepting a child. | Historical-only parsing, no current consensus reachability, or another verifier rejects inconsistent parent state. |
| `2022-11-29...3511ceac26` | Unprotected transaction policy became transaction-aware with a hash allowlist. | Narrow replay-policy exception. | Find global compatibility flags that should be exact-object allowlists. | Flag is test-only/private, or unsafe branch disabled in production. |
| `2022-11-29...652572ecf7` | Same replay-policy hardening as above through a related commit. | Narrow replay-policy exception. | Same as above. | Same as above. |
| `2023-03-01...71d7ca3337` | Initcode size and gas metering added across txpool, state transition, intrinsic gas, CREATE/CREATE2. | Multi-layer resource metering parity. | Compare all ways a payload reaches execution for the same size/gas rule. | Earlier canonical layer always rejects and alternate paths are unreachable. |
| `2023-06-14...24bcee3d95` | Stop-staker authorization changed to target continuous staker `ManagementKey()`. | Action-specific object authority. | For lifecycle actions, compare reward/owner/admin fields against the exact management authority of the object being mutated. | Authorities are provably identical by construction. |
| `2023-09-27...8e6f2f83e6` | Predicate checks now fail closed when predicate context is missing. | Required context presence. | Search verifiers taking optional context and ensure context is mandatory whenever predicates/messages require it. | Object class has no predicates or an earlier mandatory layer supplies context. |
| `2023-10-23...3a0283f107` | Non-forced mempool admission gained verification, signed-size, and gas checks. | Mempool admission resource validation. | Compare forced/local insertion with untrusted insertion; non-forced paths must validate before txpool/gossip. | Trusted recovery-only paths or a backing pool enforcing the same checks. |
| `2024-04-29...5e7c692547` | ParentBeaconRoot fork-dependent validation added. | Fork-dependent header-field validation. | For inherited fork formats, check nil/required/forbidden/value semantics for every new header field. | Dummy/test-only changes without production verifier impact. |
| `2024-08-02...07b7f15dc1` | Cancun headers must reject positive `BlobGasUsed` because Avalanche disables blobs. | Local chain-variant header invariant. | Compare upstream fork field format against local variant feature policy. | Chain actually enables the upstream feature or later verifier enforces the local invariant. |
| `2024-11-13...910a2b2392` | Warp message verification added in tx packing, manager verification, and block verification. | Protocol message verification at all acceptance ingress points. | Build a matrix of every enclosing object path that can carry an extension message and require the same verifier before acceptance. | Message is ignored by the sink or feature was unreachable before implementation. |
| `2025-01-27...9e729ab76c` | `FeeHistory` now bounds caller-controlled `rewardPercentiles`. | RPC parameter cardinality bound. | Cap every caller array dimension before loops, allocation, or result matrices. | Gateway hard caps prove local endpoint is not exposed or array is server-generated. |
| `2025-12-09...e7bd4fb988` | Range proofs now prove requested start/end bounds, including absent bounds, not only yielded keys. | Requested-boundary proof binding. | For range proofs, compare requested bounds, first/last returned key, and explicit absence proof material. | Verifier does not rely on completeness/absence or exact-key proofs only are in scope. |
| `2026-03-25...d5d9e64da0` | Auto-renewed validator weight reconstruction uses checked arithmetic. | Checked validator accounting arithmetic. | Search persisted accounting reconstruction sums before validator/stake state installation. | Protocol caps prove representability before the sum. |
| `2026-03-25...fc749bb8c1` | Same validator-weight overflow hardening as above through a related commit. | Checked validator accounting arithmetic. | Same as above. | Same as above. |
| `2026-04-30...a9c2157265` | SAE tx gossip adds an admission policy hook before txpool forwarding. | Admission policy enforcement at actual txpool sink. | Compare every txpool forwarding path against configured allowlist/admission policy. | Backing txpool independently enforces the same policy. |

## Family Clustering

### Cluster A: Fork, Feature, And Chain-Variant Validation

Findings: fork predicate mismatch, pre/post-fork child consistency, ParentBeaconRoot validation, no-blob `BlobGasUsed` validation.

Portable lesson: inherited client rules are not enough; variants need a rule matrix for field presence, value domain, fork activation, and parent/state consistency.

Current coverage: `19_consensus_fork_and_payload_rule_validation.md` is strong, but could emphasize "adjacent fork predicate" and "upstream feature format accepted while local feature disabled" as first-class hunt steps.

### Cluster B: Admission Policy At Every Ingress

Findings: replay-policy allowlist, predicate context, mempool resource validation, Warp message verification, SAE tx allowlist.

Portable lesson: policies often exist near builders/helpers but must be enforced at every untrusted path into the actual sink: txpool, block verification, manager validation, or message acceptance.

Current coverage: `01_base_hunter.md`, `10_authz`, `13_input_validation`, and `18_authoritative_state` all mention sink enforcement, but the pack lacks a compact "admission matrix" instruction for transaction/message systems.

### Cluster C: Object-Specific Authority

Finding: continuous staking stop authorization.

Portable lesson: lifecycle operations should authorize against the object's management authority, not adjacent reward/admin/owner fields.

Current coverage: `10_authz_and_role_gates.md` covers delegated permissions broadly. A sharper lifecycle-authority bullet would help without a new family.

### Cluster D: Authenticated Representation Binding

Finding: proposer block signature canonicalization.

Portable lesson: signed consensus objects with internal/exported/stored fields need one canonical representation for signing, serialization, parent lookup, ID, and verification.

Current coverage: `11_signature_binding_and_signer_scope.md` already covers duplicate representation binding. Add a targeted bullet for mutable signature fields and parent/ID lookup to improve transferability.

### Cluster E: Resource And Numeric Boundary Hardening

Findings: initcode metering, RPC percentile bound, validator weight overflow.

Portable lesson: resource/parameter bugs appear where one caller-controlled dimension multiplies work, or where reconstructed accounting values are installed after unchecked arithmetic.

Current coverage: `14_resource_accounting_and_limits.md` and `17_checked_arithmetic_and_parameter_bounds.md` are good. Add small refinements for reconstructed persisted accounting and multi-layer protocol resource parity.

### Cluster F: Authenticated State Range Proofs

Finding: Firewood range proof bounds.

Portable lesson: range proof generators must prove requested bounds and gaps, not just returned keys.

Current coverage: `20_authenticated_state_proof_and_persistence_integrity.md` has related language but should explicitly name requested-boundary proofs and absent boundary keys.

## Prompt-Pack Comparison And Decisions

No new prompt family is justified. Existing families can express every cluster. The improvements should be refinements to runtime prompts plus provenance mapping.

Approved refinements:

- Refine `00_protocol_mapper.md` for inherited-client/chain-variant matrices.
- Refine `01_base_hunter.md` for admission-policy matrices.
- Refine `10_authz_and_role_gates.md` for object-specific lifecycle authority.
- Refine `11_signature_binding_and_signer_scope.md` for mutable signed-object representations.
- Refine `14_resource_accounting_and_limits.md` for multi-layer protocol resource parity.
- Refine `17_checked_arithmetic_and_parameter_bounds.md` for reconstructed persisted accounting.
- Refine `19_consensus_fork_and_payload_rule_validation.md` for adjacent fork predicate and disabled upstream features.
- Refine `20_authenticated_state_proof_and_persistence_integrity.md` for requested range-boundary proof binding.

Rejected as runtime prompt changes:

- Repo-specific references to ProposerVM, Warp, SAE, Cortina, Cancun, Firewood, `ManagementKey`, `BlobGasUsed`, `ParentBeaconRoot`, and `rewardPercentiles`. These belong in corpus/provenance, not runtime prompts.

## Proposed Prompt Changes

### 1. `/work/dlt-ai-audit-system/00_protocol_mapper.md`

Add under the existing chain-variant mapping section:

```text
For forked clients, chain variants, or VM overlays that inherit upstream protocol features, build a variant-rule matrix:
- upstream rule or field,
- local feature enabled/disabled status,
- authoritative fork coordinate,
- expected field presence before activation,
- expected field presence and value after activation,
- every admission, block-building, replay, recovery, and syntactic-validation path that must enforce it.
Treat "upstream fork support exists" as distinct from "this chain enables every upstream feature."
```

Rationale: AvalancheGo had multiple issues where inherited EVM/fork machinery needed local field/value validation. This wording is transferable and excludes Avalanche-specific field names.

Overfitting risk: low; applies to any forked client, rollup, subnet VM, or chain-variant overlay.

### 2. `/work/dlt-ai-audit-system/01_base_hunter.md`

Add after the existing instructions about admission/execution/simulation comparison:

```text
For transaction, block, message, and proof admission, build an ingress-to-sink matrix. For each object type, list every path that can place it into the shared sink: RPC, gossip, local builder, forced/internal insertion, replay/recovery, block packing, manager verification, and block verification. Mark which paths are trusted bypasses and which are untrusted. Every untrusted path should run the same policy, resource, context, and protocol-message checks before the object reaches the shared sink.
```

Rationale: This would have helped with mempool checks, tx allowlist admission, Warp message verification, predicate context, and replay-policy exceptions without naming them.

Overfitting risk: low; this is a generic audit move for DLT systems.

### 3. `/work/dlt-ai-audit-system/prompts/10_authz_and_role_gates.md`

Add to Search patterns:

```text
- lifecycle operations such as stop, revoke, rotate, close, withdraw, unregister, renew, or disable where the authority to manage the object may differ from reward owner, fee recipient, namespace owner, subnet owner, issuer, or creator. Load the target object and authorize against its explicit management/controller key before mutating lifecycle state.
```

Rationale: Strengthens an already good authorization family for object-specific authority.

Excluded repo-specific details: no `StopStakerTx`, continuous staking, or `ManagementKey` names.

### 4. `/work/dlt-ai-audit-system/prompts/11_signature_binding_and_signer_scope.md`

Add to Search patterns:

```text
- signed consensus objects with internal, exported, cached, or serialized representations of the same identity. Compare the fields used to clear or write the signature, compute the ID, select the parent, serialize bytes, sign, verify, and store the object. A signature over one representation must not authorize routing or parentage from another.
```

Rationale: Existing duplicate-representation language is broad; this makes the signed object mutation/parent lookup asymmetry easier to hunt.

Overfitting risk: low; common in block, vote, certificate, and envelope implementations.

### 5. `/work/dlt-ai-audit-system/prompts/14_resource_accounting_and_limits.md`

Add to Search patterns:

```text
- fork or feature resource rules that must be enforced in several layers: mempool admission, intrinsic-cost calculation, state-transition validation, VM opcode or creation execution, block building, and replay. Build a parity table and flag any layer that accepts a payload shape or size that another layer only later rejects after meaningful work.
```

Rationale: Captures initcode size/gas metering without hardcoding EVM or EIP numbers.

Overfitting risk: low; applies to VMs, proof systems, transaction pools, and rollup payload rules.

### 6. `/work/dlt-ai-audit-system/prompts/17_checked_arithmetic_and_parameter_bounds.md`

Add to Search patterns:

```text
- reconstructed protocol accounting values built from persisted base values plus accrued, deferred, pending, or reward metadata. If the derived value is installed into validator weight, voting power, stake, reserves, supply, fees, or quotas, use checked arithmetic and reject unrepresentable sums before updating state.
```

Rationale: Existing arithmetic prompt covers protocol parameters; this sharpens persisted-accounting reconstruction.

Overfitting risk: low; applies to staking, ledger, rewards, reserves, and quota systems.

### 7. `/work/dlt-ai-audit-system/prompts/19_consensus_fork_and_payload_rule_validation.md`

Add to Search patterns:

```text
- adjacent fork predicate mistakes: code implementing a rule introduced at fork N guarded by fork N+1, fork N-1, a timestamp-only helper, or a generic upstream fork predicate that omits the chain variant. Test exactly before activation, at activation, and after activation.
- chain variants that import an upstream fork format but disable a subfeature. Validate both field shape and local value invariants; a field may be required by the inherited format while still constrained to nil, zero, empty, or forbidden-by-policy values by the local chain.
```

Rationale: Directly addresses two portable fork-validation lessons from AvalancheGo.

Overfitting risk: medium-low; wording avoids Cancun/blob names.

### 8. `/work/dlt-ai-audit-system/prompts/20_authenticated_state_proof_and_persistence_integrity.md`

Add to Search patterns:

```text
- range proof generators where requested start/end bounds may be absent from the tree. The proof should bind the requested boundaries and explicit absence/gap evidence, not only the first and last returned keys. Check empty ranges, missing lower bound, missing upper bound, and range edges with neighboring keys just outside the request.
```

Rationale: Makes a high-signal authenticated-state lesson explicit.

Overfitting risk: low; applies to Merkle tries, sparse trees, accumulators, and light-client proof APIs.

## New Family Prompts

No new family prompt is recommended.

Why: the clusters map cleanly to existing families. Adding a new "Avalanche-style fork hardening" or "mempool allowlist" family would overfit. The only close call is a generic "Admission Matrix" family, but `01_base_hunter.md` is the better place because it applies across families.

## Validation Notes

Hold-out check:

- Drafted the main changes using all clusters except the Firewood range-proof finding as a holdout.
- The proposed `20_authenticated_state_proof_and_persistence_integrity.md` addition was then checked against the holdout. It would direct an auditor to compare requested start/end bounds against first/last returned keys and absence evidence, which is the reusable shape of the Firewood fix.
- Also checked the admission-matrix change against the SAE tx allowlist finding after drafting from Warp/mempool/predicate examples. It still points to the missing policy hook before txpool forwarding without naming SAE.

Remaining doubts:

- Most AvalancheGo kept findings are `likely/security-hardening`, not confirmed exploit fixes. Prompt wording should preserve hardening classification and avoid teaching agents to overclaim consensus breaks.
- Some duplicated commits teach the same replay or overflow lesson; these should enrich corpus examples more than prompt text.
- The current prompt pack is already broad. Changes should be small additions, not rewrites.

Prompts that should stay unchanged for this run:

- `12_attestation_trust_and_freshness.md`: none of the kept AvalancheGo findings primarily concern attestation freshness/trust-root policy.
- `15_state_machine_and_lifecycle_consistency.md`: fork/lifecycle lessons are better handled in `10` and `19`.
- `16_staking_registry_and_accountability.md`: the staking findings here are authorization and arithmetic lessons, not registry-selection/slashing-accountability lessons.
- `21_peer_sync_progress_and_response_binding.md` and later specialized prompts: no kept finding primarily targets peer sync response binding, ZK, memory contracts, or ledger accounting.

