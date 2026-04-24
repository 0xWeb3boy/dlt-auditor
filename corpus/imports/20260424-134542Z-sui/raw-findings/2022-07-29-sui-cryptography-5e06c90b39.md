---
case_id: case_20220729_5e06c90b39
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2022-07-29
source_refs:
  - git:5e06c90b3975c43f33d4665b242bf02102891eb6
  - "crates/sui-core/src/authority.rs:1032"
  - "crates/sui-types/src/messages.rs:1884"
  - "crates/sui-core/src/epoch/reconfiguration.rs:67"
  - "crates/sui-types/src/messages.rs:1799"
bug_class: epoch-authentication-invariant
impact_type:
  - consensus-integrity
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - consensus
  - epoch-authentication
  - signature-verification
  - validator-committee
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch strengthens Sui epoch authentication checks by making signed and certified epoch verification reject records whose authentication epoch is not exactly the immediately previous epoch. It also changes epoch data modeling so `EpochInfo` carries the committee for the epoch itself and updates authority startup to initialize genesis authenticated epoch state. The evidence supports security hardening of epoch reconfiguration, but it does not prove a concrete exploit or signature forgery path.

## Observed Patch Facts

1. In `crates/sui-core/src/authority.rs`, the patch replaces `} else if let Some(latest_epoch) = store.get_latest_authenticated_epoch() {` with `store`.

2. In `crates/sui-types/src/messages.rs`, the patch replaces `self.epoch_info.verify()?;` with `/// Verify the signature of this certified epoch. The committee to verify this must b...`.

3. In `crates/sui-core/src/epoch/reconfiguration.rs`, the patch replaces `let last_checkpoint = if let Some(checkpoints) = &self.state.checkpoints {` with `let next_checkpoint = if let Some(checkpoints) = &self.state.checkpoints {`.

4. In `crates/sui-types/src/messages.rs`, the patch replaces `/// The epoch number of this epoch info.` with `/// The committee of this epoch.`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, `crates/sui-types/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-types/src/committee.rs`, `crates/sui-core/src/authority_client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/authority_client.rs`, `crates/sui-core/src/authority_aggregator.rs`. The strongest project-level identifiers around this patch are `epoch`, `committee`, `checkpoints`, and `genesis`. Nearby tests or test-like files include `crates/sui-core/src/epoch/tests/reconfiguration_tests.rs`, `crates/sui-core/src/checkpoints/tests/checkpoint_tests.rs`.

## Before/After Behavior

Before the patch, `CertifiedEpoch::verify` verified `epoch_info` and then verified `auth_sign_info` against a supplied committee without the shown explicit check that the signing metadata epoch matched `epoch_info.epoch() - 1`. `EpochInfo` also modeled a next-epoch committee relationship, and authority startup could derive the active committee from `latest_epoch.epoch_info().next_epoch_committee()`. After the patch, signed and certified epoch verification computes the epoch from `epoch_info` and enforces `epoch != 0 && epoch - 1 == self.auth_sign_info.epoch` before signature verification. `EpochInfo` now stores the committee for the epoch itself, genesis authenticated epoch state is initialized for an empty database, and existing startup reloads the committee from the authenticated epoch's own `committee()` value.

# Root Cause

The supported root cause is an insufficiently explicit verification invariant tying an authenticated epoch record to the epoch whose committee signed it. The prior representation also relied on an indirect next-epoch committee relationship, which made epoch committee selection less direct.

## Walkthrough

1. Epoch reconfiguration uses authenticated epoch data to identify committee state across epoch boundaries.

2. The old `EpochInfo` representation included an epoch/next-epoch-committee relationship rather than directly carrying the committee for the represented epoch.

3. The shown certified epoch verification path did not explicitly reject authentication metadata from an epoch other than the immediately previous one.

4. The patch changes `EpochInfo` to carry `committee: Committee` for the epoch itself.

5. The patch adds verification checks requiring non-genesis epoch data to have `auth_sign_info.epoch == epoch_info.epoch() - 1`.

6. Authority startup now initializes genesis authenticated epoch data on an empty database and reloads the active committee from the persisted authenticated epoch state.

7. The checkpoint variable rename in reconfiguration is not, by itself, evidence of a security fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-types/src/messages.rs | 1873 | Adds signed epoch verification that the epoch info is authenticated by the immediately previous epoch. |
| crates/sui-types/src/messages.rs | 1884 | Adds the same previous-epoch binding check for certified epoch verification. |
| crates/sui-types/src/messages.rs | 1799 | Changes `EpochInfo` to carry the committee for the epoch itself instead of relying on a next-epoch committee relationship. |
| crates/sui-core/src/authority.rs | 1006 | Initializes genesis authenticated epoch data on empty database and reloads committee from persisted authenticated epoch state. |
| crates/sui-core/src/epoch/reconfiguration.rs | 66 | Updates epoch-change checkpoint handling in the reconfiguration path. |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/authority.rs:1032` (changes a consensus- or validator-sensitive branch)

Before
```rust
.await
                .expect("Cannot bulk insert genesis objects");
            genesis_committee
        } else if let Some(latest_epoch) = store.get_latest_authenticated_epoch() {
            latest_epoch.epoch_info().next_epoch_committee().clone()
        } else {
            genesis_committee
        };
```
After
```rust
.await
                .expect("Cannot bulk insert genesis objects");
            store
                .init_genesis_epoch(genesis_committee.clone())
                .expect("Init genesis epoch data must not fail");
            genesis_committee
        } else {
            store
```

## Snippet 2

Context: `crates/sui-types/src/messages.rs:1884` (changes signature or replay validation logic)

Before
```rust
impl CertifiedEpoch {
    pub fn verify(&self, committee: &Committee) -> SuiResult {
        self.epoch_info.verify()?;
        self.auth_sign_info.verify(&self.epoch_info, committee)?;
        Ok(())
    }
}
```
After
```rust
impl CertifiedEpoch {
    /// Verify the signature of this certified epoch. The committee to verify this must be the
    /// committee from the previous epoch, as this is signed by a quorum from the previous epoch.
    pub fn verify(&self, committee: &Committee) -> SuiResult {
        let epoch = self.epoch_info.epoch();
        fp_ensure!(
            epoch != 0 && epoch - 1 == self.auth_sign_info.epoch,
```

## Snippet 3

Context: `crates/sui-core/src/epoch/reconfiguration.rs:67` (changes a consensus- or validator-sensitive branch)

Before
```rust
let epoch = self.state.committee.load().epoch;
        info!(?epoch, "Finishing epoch change");
        let last_checkpoint = if let Some(checkpoints) = &self.state.checkpoints {
            let mut checkpoints = checkpoints.lock();
            assert!(
```
After
```rust
let epoch = self.state.committee.load().epoch;
        info!(?epoch, "Finishing epoch change");
        let next_checkpoint = if let Some(checkpoints) = &self.state.checkpoints {
            let mut checkpoints = checkpoints.lock();
            assert!(
```

## Snippet 4

Context: `crates/sui-types/src/messages.rs:1799` (changes signature or replay validation logic)

Before
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpochInfo {
    /// The epoch number of this epoch info.
    /// Although we could derive it from the epoch number of `next_epoch_committee`, a potential
    /// byzantine node may set next_epoch_committee.epoch as 0, which will make it very
    /// inconvenient to obtain the epoch number.
    epoch: EpochId,
    /// The committee of the NEXT epoch. The committee of the epoch identified by the `epoch`
```
After
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpochInfo {
    /// The committee of this epoch.
    committee: Committee,
    /// The first checkpoint included in this epoch.
    first_checkpoint: CheckpointSequenceNumber,
}
```

# Fix Pattern

Make the cross-epoch authentication invariant explicit in verification and data modeling: store epoch-local committee data directly and reject signed or certified epoch records whose authentication epoch does not match the immediately previous epoch.

## How It Was Fixed

`crates/sui-types/src/messages.rs` adds an `epoch != 0 && epoch - 1 == self.auth_sign_info.epoch` guard for signed and certified epoch verification before verifying signatures with the previous epoch committee. `EpochInfo` is changed to carry the committee for the epoch itself. `crates/sui-core/src/authority.rs` initializes genesis authenticated epoch data and reloads the committee from the authenticated epoch record's `committee()` accessor.

# Why It Matters

1. Epoch changes depend on accepting committee data authenticated by the correct prior committee.

2. The added guard reduces the chance of accepting epoch data with mismatched authentication metadata.

3. The patch is security-relevant to consensus and validator committee handling.

4. The provided evidence supports hardening, not a demonstrated exploitable vulnerability.

# Evidence Notes

The strongest evidence is the added verification guard in `crates/sui-types/src/messages.rs` requiring the authenticated signing epoch to be exactly one less than the epoch being verified. Supporting evidence is the `EpochInfo` model change from next-epoch committee data to committee-for-this-epoch data and authority startup initialization of genesis authenticated epoch state. The provided hunks do not fully show the storage indexing change referenced in the commit subject and do not establish a concrete remote attack path. Protocol security invariant: Authenticated epoch data for epoch N must be accepted only when its authentication metadata comes from epoch N-1 and is verified with the previous epoch committee that signed it. Verification notes: The patch does not prove that an attacker could forge epoch data without quorum signatures. The patch does not show a concrete remote exploit path. The storage indexing changes are not fully visible in the provided hunks. The checkpoint variable rename alone is not security-relevant. The evidence supports epoch authentication hardening more than a confirmed consensus break. No evidence proves signature forgery was possible. No evidence proves a concrete exploit path. The checkpoint rename should not be treated as security-relevant on its own. Classification is kept at medium confidence because the security invariant is clear but exploitability is not shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `epoch-authentication-invariant`
Final impact type: `consensus-integrity, state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, epoch-authentication, signature-verification, validator-committee`

The supplied patch evidence supports retaining this as security hardening. The strongest change is an explicit verification guard requiring authenticated epoch data for epoch N to be signed by metadata from epoch N-1, in validator/committee epoch-transition code. The evidence does not prove a concrete exploitable vulnerability, signature forgery, or state corruption incident, so it should not be labeled as a security-fix or as a specific state-corruption bug.

## Security Evidence

1. Signed and certified epoch verification now checks `epoch != 0 && epoch - 1 == self.auth_sign_info.epoch`.
2. The code comments state that epoch data must be verified by the previous epoch committee because it is signed by that committee.
3. The changed data model removes the indirect next-epoch committee relationship and stores the committee for the epoch itself.
4. Authority startup now initializes genesis authenticated epoch state and loads committee state from authenticated epoch data.
5. The surrounding subsystem is validator epoch reconfiguration and committee authentication, which is security-sensitive in a blockchain core.

## Missing Evidence

1. No concrete exploit path is shown.
2. No evidence shows an attacker could bypass quorum signatures or forge authenticated epoch data.
3. The storage indexing change named in the commit subject is not fully represented in the supplied hunks.
4. The checkpoint variable rename does not independently support a security claim.
5. No regression test details are provided showing rejection of a malicious or malformed epoch record.

## Claim Boundaries

1. Classify as security-hardening, not security-fix.
2. Do not claim proven signature forgery, consensus takeover, or exploitable state corruption.
3. The supported claim is explicit tightening of epoch authentication invariants.
4. The impact should be framed conservatively as consensus/state integrity hardening.
5. The checkpoint rename should be treated as incidental unless additional evidence is supplied.
