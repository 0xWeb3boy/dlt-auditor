---
case_id: case_20230202_7ec4bccdd4
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2023-02-02
source_refs:
  - git:7ec4bccdd4f3a7cc7afca6f0789398b8a1827173
  - "crates/sui-types/src/messages_checkpoint.rs:250"
  - "crates/sui-types/src/messages_checkpoint.rs:9"
  - "crates/sui-core/src/checkpoints/mod.rs:907"
  - "crates/sui-types/src/messages_checkpoint.rs:271"
bug_class: consensus-quorum-hardening
impact_type:
  - consensus-safety
  - fork-risk-reduction
confidence: medium
tags:
  - infrastructure
  - consensus
  - checkpointing
  - quorum-threshold
  - validator-quorum
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Sui checkpoint certification by replacing `AuthorityWeakQuorumSignInfo` with `AuthorityStrongQuorumSignInfo` for `CertifiedCheckpointSummary` and related aggregation paths. The evidence supports consensus/checkpoint quorum hardening, not signature forgery, replay, nonce misuse, or a fully demonstrated exploit.

## Observed Patch Facts

1. In `crates/sui-types/src/messages_checkpoint.rs`, the patch replaces `pub type CertifiedCheckpointSummary = CheckpointSummaryEnvelope<AuthorityWeakQuorumSi...` with `pub type CertifiedCheckpointSummary = CheckpointSummaryEnvelope<AuthorityStrongQuorum...`.

2. In `crates/sui-types/src/messages_checkpoint.rs`, the patch replaces `AuthoritySignInfo, AuthoritySignInfoTrait, AuthorityWeakQuorumSignInfo, Signature,` with `AuthoritySignInfo, AuthoritySignInfoTrait, AuthorityStrongQuorumSignInfo, Signature,`.

3. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `) -> Result<AuthorityWeakQuorumSignInfo, ()> {` with `) -> Result<AuthorityStrongQuorumSignInfo, ()> {`.

4. In `crates/sui-types/src/messages_checkpoint.rs`, the patch replaces `auth_signature: AuthorityWeakQuorumSignInfo::new_from_auth_sign_infos(` with `auth_signature: AuthorityStrongQuorumSignInfo::new_from_auth_sign_infos(`.

## Project Context

The changed code sits primarily in `crates/sui-types/src`, `crates/sui-types`, `crates/sui-core/src/checkpoints`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-types/src/crypto.rs`, `crates/sui-types/src/messages.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/crypto.rs`, `crates/sui-types/src/messages.rs`. The strongest project-level identifiers around this patch are `summary`, `CertifiedCheckpointSummary`, `AuthorityWeakQuorumSignInfo`, and `AuthorityStrongQuorumSignInfo`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/messages_tests.rs`, `crates/sui-core/src/unit_tests/gas_tests.rs`.

## Before/After Behavior

Before the change, certified checkpoint summaries and checkpoint aggregation used `AuthorityWeakQuorumSignInfo`, allowing certification with a weak f+1 quorum. After the change, the public checkpoint certificate type, certificate construction, and checkpoint signature aggregator use `AuthorityStrongQuorumSignInfo`, requiring a strong 2f+1 quorum.

# Root Cause

The checkpoint certificate abstraction used a weak quorum signature type for certified checkpoints. The commit message says this was considered sufficient for minimal safety, but stronger 2f+1 certification was chosen to reduce forks if nondeterministic execution causes validators to produce divergent checkpoint digests.

## Walkthrough

1. `messages_checkpoint.rs` previously imported `AuthorityWeakQuorumSignInfo` for checkpoint certificate handling.

2. `CertifiedCheckpointSummary` was previously defined as `CheckpointSummaryEnvelope<AuthorityWeakQuorumSignInfo>`.

3. `CertifiedCheckpointSummary::aggregate` previously constructed certificates with `AuthorityWeakQuorumSignInfo::new_from_auth_sign_infos(...)`.

4. `CheckpointSignatureAggregator::try_aggregate` previously returned `AuthorityWeakQuorumSignInfo`.

5. The patch changes these paths to `AuthorityStrongQuorumSignInfo`, aligning certificate representation and aggregation with a stronger quorum threshold.

6. The commit rationale states the goal is avoiding forks under possible nondeterministic execution bugs and reducing their blast radius.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-types/src/messages_checkpoint.rs | 9 | imports strong quorum signature type for checkpoint certificate handling instead of weak quorum type |
| crates/sui-types/src/messages_checkpoint.rs | 250 | defines CertifiedCheckpointSummary as an envelope requiring AuthorityStrongQuorumSignInfo |
| crates/sui-types/src/messages_checkpoint.rs | 271 | aggregates signed checkpoint summaries into a strong-quorum certificate |
| crates/sui-core/src/checkpoints/mod.rs | 907 | checkpoint signature aggregator now returns strong quorum certification info |

## Code Snippets

## Snippet 1

Context: `crates/sui-types/src/messages_checkpoint.rs:250` (changes a consensus- or validator-sensitive branch)

Before
```rust
// clients and more efficient sync protocols.

pub type CertifiedCheckpointSummary = CheckpointSummaryEnvelope<AuthorityWeakQuorumSignInfo>;

impl CertifiedCheckpointSummary {
```
After
```rust
// clients and more efficient sync protocols.

pub type CertifiedCheckpointSummary = CheckpointSummaryEnvelope<AuthorityStrongQuorumSignInfo>;

impl CertifiedCheckpointSummary {
```

## Snippet 2

Context: `crates/sui-types/src/messages_checkpoint.rs:9` (changes signature or replay validation logic)

Before
```rust
use crate::committee::{EpochId, StakeUnit};
use crate::crypto::{
    AuthoritySignInfo, AuthoritySignInfoTrait, AuthorityWeakQuorumSignInfo, Signature,
};
use crate::error::SuiResult;
```
After
```rust
use crate::committee::{EpochId, StakeUnit};
use crate::crypto::{
    AuthoritySignInfo, AuthoritySignInfoTrait, AuthorityStrongQuorumSignInfo, Signature,
};
use crate::error::SuiResult;
```

## Snippet 3

Context: `crates/sui-core/src/checkpoints/mod.rs:907` (changes a sensitive control or state-update path)

Before
```rust
&mut self,
        data: CheckpointSignatureMessage,
    ) -> Result<AuthorityWeakQuorumSignInfo, ()> {
        let their_digest = data.summary.summary.digest();
        let author = data.summary.auth_signature.authority;
```
After
```rust
&mut self,
        data: CheckpointSignatureMessage,
    ) -> Result<AuthorityStrongQuorumSignInfo, ()> {
        let their_digest = data.summary.summary.digest();
        let author = data.summary.auth_signature.authority;
```

## Snippet 4

Context: `crates/sui-types/src/messages_checkpoint.rs:271` (changes a sensitive control or state-update path)

Before
```rust
let certified_checkpoint = CertifiedCheckpointSummary {
            summary: signed_checkpoints[0].summary.clone(),
            auth_signature: AuthorityWeakQuorumSignInfo::new_from_auth_sign_infos(
                signed_checkpoints
                    .into_iter()
```
After
```rust
let certified_checkpoint = CertifiedCheckpointSummary {
            summary: signed_checkpoints[0].summary.clone(),
            auth_signature: AuthorityStrongQuorumSignInfo::new_from_auth_sign_infos(
                signed_checkpoints
                    .into_iter()
```

# Fix Pattern

Encode the stronger quorum requirement in the checkpoint certificate type and aggregation path by replacing weak quorum signature information with strong quorum signature information.

## How It Was Fixed

The patch imports `AuthorityStrongQuorumSignInfo`, redefines `CertifiedCheckpointSummary` as `CheckpointSummaryEnvelope<AuthorityStrongQuorumSignInfo>`, constructs certified checkpoints with `AuthorityStrongQuorumSignInfo::new_from_auth_sign_infos(...)`, and updates `CheckpointSignatureAggregator::try_aggregate` to return strong quorum certification info.

# Why It Matters

1. Checkpoint certificates are consensus-sensitive artifacts used for synchronization and catch-up.

2. A stronger quorum increases overlap between certified checkpoint views.

3. The stated risk is fork reduction when nondeterministic execution produces divergent checkpoint digests.

4. The evidence supports hardening of a protocol threshold, not proof of direct exploitability.

# Evidence Notes

Grounded evidence is the coordinated replacement of `AuthorityWeakQuorumSignInfo` with `AuthorityStrongQuorumSignInfo` in `crates/sui-types/src/messages_checkpoint.rs` and `crates/sui-core/src/checkpoints/mod.rs`, plus the commit message explaining the move from weak f+1 to strong 2f+1 quorum. Unsupported claims removed: signature forgery, replay, nonce-binding failure, invalid signature acceptance, and demonstrated exploitation. Protocol security invariant: Certified checkpoints should require enough validator stake signatures to make conflicting checkpoint certificates harder to form when validators diverge, such as under nondeterministic execution. The patch raises checkpoint certification from weak f+1 quorum information to strong 2f+1 quorum information. Verification notes: The patch does not prove an attacker could forge validator signatures. The patch does not show a replay vulnerability or nonce-binding bug. The commit states weak f+1 was sufficient for minimal safety, so this is stronger quorum hardening rather than a clear correction of invalid acceptance logic. The concrete nondeterministic execution accident is not included in the provided evidence. Exploitability depends on validators producing divergent checkpoint digests; that path is not demonstrated here. Direct code evidence shows a quorum type change in checkpoint certification paths. Commit text supplies the stated fork-avoidance rationale. No provided evidence demonstrates the underlying nondeterministic execution accident. No provided evidence proves attacker-controlled signature forgery or replay. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-quorum-hardening`
Final impact type: `consensus-safety, fork-risk-reduction`
Final confidence: `medium`
Final tags: `infrastructure, consensus, checkpointing, quorum-threshold, validator-quorum, security-hardening`

The supplied evidence supports retaining this as security hardening: checkpoint certification moved from a weak f+1 quorum to a strong 2f+1 quorum, and the commit explicitly frames the change as reducing fork blast radius under nondeterministic execution bugs. The evidence does not support the original replay/signature-forgery framing or a concrete exploitable vulnerability, so the corpus entry should be narrowed to consensus quorum hardening.

## Security Evidence

1. CertifiedCheckpointSummary changed from AuthorityWeakQuorumSignInfo to AuthorityStrongQuorumSignInfo.
2. Checkpoint aggregation now constructs AuthorityStrongQuorumSignInfo certificates.
3. CheckpointSignatureAggregator now returns a strong quorum signature info type.
4. Commit message states the prior weak quorum could allow larger fork blast radius if nondeterministic execution caused divergent checkpoint digests.

## Missing Evidence

1. No demonstrated attacker-controlled exploit path is provided.
2. No evidence of signature forgery, replay, nonce misuse, or invalid signature acceptance is shown.
3. The referenced recent accident and nondeterministic execution bug are not included in the supplied evidence.
4. The patch does not prove that weak quorum violated the protocol's stated minimal safety model.

## Claim Boundaries

1. Treat as consensus/checkpoint quorum hardening, not as a replay or request-forgery fix.
2. Do not claim concrete exploitability from the patch alone.
3. Do not claim cryptographic signature validation was broken; the change is the quorum threshold/type used for checkpoint certification.
4. Security relevance is fork/blast-radius reduction in a validator consensus subsystem.
