# Heimdall V2 Prompt-Pack Refinement Proposal

Target repo: `/testing/heimdall-v2`

Evidence folder: `/testing/heimdall-v2/validated-findings/kept`

Current prompt pack: `/testing/dlt-ai-audit-system`

Date: 2026-04-24

## Repo Context Summary

Heimdall v2 is the Polygon PoS consensus client built on Cosmos SDK and CometBFT. Its security-sensitive shape is a hybrid of BFT consensus application logic, validator staking/registration, L1/Bor checkpoint validation, side transactions, and ABCI++ vote extensions.

Important architecture:

- `app/`: ABCI++ PrepareProposal, ProcessProposal, ExtendVote, VerifyVoteExtension, PreBlocker, and vote-extension utilities.
- `sidetxs/`: validator side-transaction vote plumbing.
- `x/checkpoint/`: checkpoint message admission, side-vote validation, checkpoint buffers, checkpoint ACKs, and L1/Bor checkpoint data validation.
- `x/stake/`: validator join, signer/validator ID mappings, validator set updates, and staking side messages.
- `x/chainmanager/`: trusted chain configuration, including Bor/root-chain parameters used by checkpoint validation.
- `bridge/` and `helper/`: cross-chain event and contract-call support.

Trust boundaries:

- CometBFT consensus inputs to application ABCI handlers: `ExtendedVoteInfo`, proposal tx bytes, vote extensions, proposer identity, height, round, and validator-set context.
- Validator/operator submitted messages to keeper state: validator join, checkpoint, checkpoint ACK, side-tx votes.
- L1/Bor-derived or configured chain parameters to local checkpoint validation.
- Side-tx pre/post handlers to persistent keeper state.
- Getter/helper abstractions to canonical store predicates.

High-risk entrypoint categories:

- ABCI PrepareProposal/ProcessProposal/PreBlocker vote-extension aggregation and validation.
- Checkpoint message and side-message handlers that decide whether checkpoint state advances or validators vote YES.
- Validator registration paths that bind validator IDs to signer identities.
- Cross-chain/domain validation paths where chain-manager config must be enforced before side votes.

State-machine/lifecycle patterns that matter:

- Vote extensions are height/round/proposer/validator-set scoped and must be validated before counting or proposal acceptance.
- Checkpoints are contiguous ranges; direct message handling and side-tx post-handling must enforce the same range transition.
- Validator IDs and signer mappings are persistent identity state; uniqueness must be checked by explicit store presence.
- Chain/domain parameters are trusted configuration and must be read fail-closed at consensus-facing boundaries.

## Finding Inventory

Analyzed all 6 findings in `/testing/heimdall-v2/validated-findings/kept`:

- `2024-06-24-heimdall-v2-rpc-client-api-316e7e65.md`: validator ID reuse guard.
- `2024-09-05-heimdall-v2-rpc-client-api-86680527.md`: vote-extension height binding in tallying.
- `2024-09-06-heimdall-v2-rpc-client-api-4310d22a.md`: centralized proposal vote-extension validation.
- `2025-05-08-heimdall-v2-transaction-processing-29c8c2e5.md`: checkpoint continuity and buffer fail-closed handling.
- `2025-05-08-heimdall-v2-transaction-processing-6f86ef9b.md`: same checkpoint continuity lesson in companion path.
- `2025-08-13-heimdall-v2-storage-8b425ed5.md`: checkpoint Bor chain ID/domain validation in side handler.

No findings were skipped.

## Finding-To-Mechanism Analysis

| Finding | Repo-specific mechanism | Generic invariant | Missing property | Code shape | Hunt recipe | False-positive killers |
| --- | --- | --- | --- | --- | --- | --- |
| `316e7e65` | `ValidatorJoin` and stake side handler now use `DoesValIdExist` / store `Has` instead of getter error semantics for validator ID reuse. | A privileged identity ID must not be reused once bound in canonical state. | Explicit key-presence check for identity uniqueness. | Create/join handler calls a getter to infer existence. | Compare every registration uniqueness guard with canonical store APIs; look for `GetByID` used before create. | DB uniqueness constraint, prior canonical guard, or documented getter semantics already prove exact existence. |
| `86680527` | PreBlocker passes `req.Height` into vote tallying; `aggregateVotes` rejects vote extensions whose embedded height is not `currentHeight-1`. | Attestations counted at height H must be bound to the expected source height/round. | Consensus context binding before aggregation. | Aggregator lacked authoritative context and trusted embedded payload context. | Trace vote-extension bytes from ABCI request to tally; check whether height/round/hash/domain are compared before votes count. | Consensus layer already verifies the exact context before app code, or embedded context is not decision-relevant. |
| `4310d22a` | PrepareProposal/ProcessProposal moved from narrow inline checks to `ValidateVoteExtensions` with height, round, proposer, validator set, signatures, and quorum context. | Proposal handlers must validate validator attestations before embedding or accepting vote-derived data. | Centralized validator/signature/quorum validation at proposal boundary. | Inline unmarshal/duplicate checks where a shared validator-context helper should run. | Compare PrepareProposal and ProcessProposal against VerifyVoteExtension/validator-set logic; look for syntactic checks only. | Helper is pure refactor with no added validator, signature, round, or quorum validation. |
| `29c8c2e5` | Checkpoint handlers now require `lastCheckpoint.EndBlock+1 == msg.StartBlock` and return on checkpoint-buffer read errors. | Range-based checkpoint state must advance by exact successor ranges. | Exact continuity and fail-closed buffer errors. | `previousEnd > start` rejects overlap but permits gaps. | Search checkpoint/range admission for "after tip" checks that do not reject gaps; compare buffer read errors vs not-found. | Sparse checkpoints are valid by protocol, or a later canonical verifier enforces exact continuity. |
| `6f86ef9b` | Same continuity predicate appears in direct and side-tx post-handler paths. | Equivalent transition paths for the same protocol object must enforce identical range invariants. | Cross-path consistency for checkpoint continuity. | Duplicated state-transition predicates can drift. | Compare direct tx handler, side-vote handler, post-handler, replay/recovery, and bridge submission for the same range object. | One path is unreachable or only defense-in-depth after a mandatory earlier exact check. |
| `8b425ed5` | `SideHandleMsgCheckpoint` now reads chain-manager params and votes NO if Bor chain ID mismatches configured chain ID. | Cross-chain checkpoint side votes must be domain-bound to trusted local configuration. | Chain/domain validation at side-vote boundary. | Generic checkpoint proof validation runs without first binding message domain. | Search bridge/checkpoint/state-sync handlers for `chainId`/domain fields; ensure config comparison happens before YES/accept. | Proof or contract caller cryptographically binds the same domain, or handler only processes locally generated messages. |

## Family Clustering

### Cluster A: Consensus Attestation Context And Quorum Validation

Findings: `86680527`, `4310d22a`.

Why grouped: both concern vote-extension material crossing from validator/proposer supplied ABCI data into consensus-sensitive tally/proposal decisions. The shared missing property is not generic input validation; it is context-aware attestation validation: height, round, proposer, validator-set membership, voting power, signatures, duplicate votes, and quorum.

Portability: high. Applies to ABCI++ vote extensions, bridge validator attestations, optimistic rollup batches, committee signatures, light-client votes, and any DLT side-vote or attestation layer.

### Cluster B: Checkpoint Range Continuity And Equivalent Transition Paths

Findings: `29c8c2e5`, `6f86ef9b`.

Why grouped: both teach that range state machines need exact successor validation and that the same invariant must hold across direct message handling, side-tx post-handling, and buffer-dependent paths.

Portability: high. Applies to checkpoints, epochs, spans, batches, state-sync ranges, proof windows, withdrawal batches, pruning windows, and settlement intervals.

### Cluster C: Identity Registry Existence vs Retrieval Semantics

Findings: `316e7e65`.

Why grouped: single finding, but the mechanism is fundamental and portable: a privileged identity namespace uses a value getter as a proxy for key existence.

Portability: medium-high. Applies to validator registries, operator IDs, signer maps, committee slots, relayer registrations, bridge validator sets, and keyed capability stores.

### Cluster D: Cross-Domain Checkpoint/Bridge Domain Binding

Findings: `8b425ed5`.

Why grouped: single finding, but it sharpens an existing family: domain/chain config must be enforced at the side-vote or validation boundary, not only inside generic proof validity.

Portability: high for bridge, checkpoint, state-sync, oracle, and external-consensus-client code.

## Prompt-Pack Comparison

### Cluster A

Affected prompts: `00_protocol_mapper.md`, `12_attestation_trust_and_freshness.md`, `19_consensus_fork_and_payload_rule_validation.md`, `02_validation_and_impact.md`.

Current coverage: strong but split. `00` maps signed/proof artifacts and consensus surfaces; `12` discusses signer sets and freshness; `19` discusses consensus validation; `02` includes freshness and replay protection. What is weak is the explicit instruction to map vote-extension/side-vote artifacts as attestation pipelines with both observation and enforcement layers, and to distinguish syntactic payload validity from validator-set/quorum validity.

Recommendation: refine existing prompts; no new family.

### Cluster B

Affected prompts: `13_input_validation_and_invariant_enforcement.md`, `15_state_machine_and_lifecycle_consistency.md`, `20_authenticated_state_proof_and_persistence_integrity.md`.

Current coverage: `13` mentions structural invariants and state updates from request fields; `15` mentions checkpoint lifecycle; `20` mentions checkpoint resume and proof windows. What is weak is the exact range-continuity motif (`previousEnd > start` vs `previousEnd+1 == start`) and explicit comparison of all equivalent paths for range objects.

Recommendation: refine `13` and `15`; optionally `20` for authenticated range/proof pipelines.

### Cluster C

Affected prompts: `16_staking_registry_and_accountability.md`, `13_input_validation_and_invariant_enforcement.md`, `18_authoritative_state_and_boundary_enforcement.md`.

Current coverage: `16` covers stake/deposit/election and liveness, but does not explicitly tell auditors to inspect identity registry uniqueness predicates or distinguish `Get` from `Has`. `13` has a broad state-update line; `18` covers authoritative state but not registry existence semantics.

Recommendation: refine `16` and lightly refine `13`.

### Cluster D

Affected prompts: `12_attestation_trust_and_freshness.md`, `18_authoritative_state_and_boundary_enforcement.md`, `13_input_validation_and_invariant_enforcement.md`.

Current coverage: strong after prior Bor/Reth refinements. `12` already mentions external consensus-client and checkpoint reads, and `13` mentions chain/domain scoping. What is weak is fail-closed side-vote behavior when trusted domain config is unavailable, and "domain check before YES vote" as a recurring bridge/checkpoint validation pattern.

Recommendation: refine `12` or `18` with a narrow side-vote/domain-binding line.

## Proposed Prompt Changes

### Change 1: Strengthen `00_protocol_mapper.md`

Target file: `/testing/dlt-ai-audit-system/00_protocol_mapper.md`

Add under Step 2, after item 3:

```text
3a. For each attestation-like artifact, including vote extensions, side votes, checkpoint signatures, committee approvals, bridge validator votes, and oracle reports, map:
  - who creates it,
  - which height, round, block hash, chain/domain, signer set, and voting-power snapshot it is supposed to bind,
  - where syntactic decoding happens,
  - where validator/signature/quorum validation happens,
  - where the attestation is finally counted, persisted, or used to accept a proposal/state transition.
```

Rationale: Heimdall's vote-extension findings show that a generic "signed artifact" map is too shallow unless it separates decoding, signature/quorum validation, and the counting sink.

Repo-specific details intentionally excluded: CometBFT, `ExtendedVoteInfo`, `ValidateVoteExtensions`, and Heimdall file names.

Overfitting risk check: low; the instruction applies to many DLT attestation systems.

### Change 2: Strengthen `12_attestation_trust_and_freshness.md`

Target file: `/testing/dlt-ai-audit-system/prompts/12_attestation_trust_and_freshness.md`

Add under Search patterns:

```text
- attestation aggregation paths where payloads are syntactically valid but not yet bound to the exact height, round, block hash, chain/domain, signer-set snapshot, or voting-power quorum expected by the consuming consensus step
- side-vote, checkpoint, bridge, or oracle handlers that can return an accept/YES/trusted decision before trusted domain configuration is loaded and compared against the message-carried domain
```

Rationale: Captures both Heimdall vote-extension context binding and checkpoint chain-ID side-vote hardening without naming either case.

Repo-specific details intentionally excluded: BorChainId, checkpoint keeper, side txs.

Overfitting risk check: medium-low; useful broadly, but should stay in `12` instead of a new family because it is an attestation/trust-boundary sharpening.

### Change 3: Strengthen `13_input_validation_and_invariant_enforcement.md`

Target file: `/testing/dlt-ai-audit-system/prompts/13_input_validation_and_invariant_enforcement.md`

Add under Search patterns:

```text
- range, checkpoint, epoch, batch, span, or proof-window objects where the code rejects old or overlapping starts but does not require the next start to be the exact successor of the stored end when the protocol expects contiguous progression
- create, join, register, or bind operations that infer uniqueness from getter failures instead of using an explicit canonical key-existence check before writing identity, signer, operator, validator, or committee state
```

Rationale: These are precise code shapes that would have raised the Heimdall checkpoint and validator-ID findings while remaining generic.

Repo-specific details intentionally excluded: `lastCheckpoint.EndBlock`, `msg.StartBlock`, `DoesValIdExist`.

Overfitting risk check: medium; the range-continuity line must include "when the protocol expects contiguous progression" to avoid flagging sparse-checkpoint designs.

### Change 4: Strengthen `15_state_machine_and_lifecycle_consistency.md`

Target file: `/testing/dlt-ai-audit-system/prompts/15_state_machine_and_lifecycle_consistency.md`

Add under Search patterns:

```text
- equivalent transition paths for the same range-based protocol object, such as direct message handling, side-vote handling, post-consensus handling, replay, recovery, bridge submission, and buffer flushing, where one path enforces exact successor continuity or fail-closed storage errors and another path only enforces freshness or overlap prevention
```

Rationale: Heimdall's checkpoint findings are a transition-path parity lesson more than a one-off validation bug.

Repo-specific details intentionally excluded: checkpoint module and buffer function names.

Overfitting risk check: low; this generalizes to any range/lifecycle object with multiple mutation paths.

### Change 5: Strengthen `16_staking_registry_and_accountability.md`

Target file: `/testing/dlt-ai-audit-system/prompts/16_staking_registry_and_accountability.md`

Add under Search patterns:

```text
- validator, operator, signer, committee, relayer, or node registration paths where an ID-to-signer or ID-to-owner mapping is checked through a value lookup rather than an explicit presence/absence predicate on the canonical registry key
- registry joins or reactivations that check signer uniqueness but not stable numeric ID, slot, operator ID, or historical participation identifiers that the protocol treats as non-reusable
```

Rationale: The existing staking prompt focuses on economics and accountability but underweights registry identity invariants.

Repo-specific details intentionally excluded: Heimdall validator ID names and keeper APIs.

Overfitting risk check: low; staking/registry systems commonly have several identity namespaces with different reuse rules.

### Change 6: Strengthen `19_consensus_fork_and_payload_rule_validation.md`

Target file: `/testing/dlt-ai-audit-system/prompts/19_consensus_fork_and_payload_rule_validation.md`

Add under Search patterns:

```text
- ABCI, consensus API, proposal-building, or proposal-processing paths that embed or consume validator vote extensions, side votes, committee votes, or aggregate approvals. Check that every path validates signer identity, signature, duplicate votes, voting power, quorum, height, round, proposer, and block/domain context before proposal acceptance or tallying.
```

Rationale: `19` currently focuses on block/payload/fork validation. Heimdall shows a consensus-client class where the sensitive payload is vote-extension data rather than a block body.

Repo-specific details intentionally excluded: ABCI++ can remain as one example, but the text also names generic consensus APIs and committee votes.

Overfitting risk check: low; applies to Tendermint/CometBFT, HotStuff-style votes, bridge quorums, and committee attestations.

### Change 7: Strengthen `02_validation_and_impact.md`

Target file: `/testing/dlt-ai-audit-system/02_validation_and_impact.md`

Add to the missing-property list:

```text
   - attestation quorum/context binding
   - exact range-continuity enforcement
   - explicit registry key-existence validation
```

Add under impact assessment:

```text
10. If the issue involves validator votes, vote extensions, side votes, or committee attestations, distinguish syntactic validity, signature validity, validator-set membership, voting-power quorum, freshness, and domain separation. Do not treat one property as proof of the others.
11. If the issue involves ranges such as checkpoints, epochs, spans, batches, or proof windows, distinguish overlap prevention, exact continuity, gap tolerance by design, and downstream enforcement by another verifier or contract.
```

Rationale: Heimdall's validations needed careful downgrade from "confirmed exploit" to "security hardening"; these questions would reduce overclaiming.

Repo-specific details intentionally excluded: checkpoint names, side tx names, Polygon/Bor labels.

Overfitting risk check: low; the additions are validation discipline, not hunt spoilers.

## New Family Prompts

No new family prompt is justified.

Reasons:

- Attestation context binding fits `12_attestation_trust_and_freshness.md` plus a `19` consensus-surface sharpening.
- Checkpoint continuity fits `13_input_validation_and_invariant_enforcement.md` and `15_state_machine_and_lifecycle_consistency.md`.
- Validator ID reuse fits `16_staking_registry_and_accountability.md`.
- Cross-domain checkpoint validation fits `12` and `18`.

Creating a Heimdall-specific "vote extension" or "checkpoint" family would overfit. The prompt pack is better improved through small portable additions.

## Validation Notes

Holdout check: I drafted the attestation/quorum wording using `86680527` as the main example, then checked it against the held-out `4310d22a`. The same wording would have pushed an auditor from "does the vote-extension payload unmarshal?" toward "where are signatures, quorum, validator-set membership, height, round, and proposer context validated before proposal acceptance?", which is exactly the missing hunt direction.

For checkpoint continuity, I used `29c8c2e5` to draft the range-continuity wording and held out `6f86ef9b`. The proposed `15` wording still catches the held-out case because it asks for parity across direct, side-vote, post-consensus, buffer, replay, and recovery paths.

Remaining doubts:

- The kept findings are all validated as security hardening, not confirmed exploit fixes. Prompt text should therefore use "hunt/check/compare" language and validation safeguards, not imply that every mismatch is exploitable.
- Heimdall-specific terminology in the raw findings, especially `BorChainId`, `SideHandleMsgCheckpoint`, and `ExtendedVoteInfo`, should stay in corpus/provenance, not runtime prompts.

Prompts that should stay unchanged for now:

- `10_authz_and_role_gates.md`: none of the six kept Heimdall findings primarily teach authorization-role gating.
- `11_signature_binding_and_signer_scope.md`: vote-extension signatures appear in the evidence, but the reusable issue is broader attestation context/quorum validation and belongs in `12`/`19`.
- `14_resource_accounting_and_limits.md`, `17_checked_arithmetic_and_parameter_bounds.md`, `20_authenticated_state_proof_and_persistence_integrity.md`, and `21_peer_sync_progress_and_response_binding.md`: no direct new Heimdall lesson in this kept set beyond existing coverage.

