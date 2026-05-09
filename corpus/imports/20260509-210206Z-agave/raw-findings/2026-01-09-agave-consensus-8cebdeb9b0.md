---
case_id: case_20260109_8cebdeb9b0
project: agave
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2026-01-09
source_refs:
  - git:8cebdeb9b0a33b10dd25a7af25699beb310b339f
  - "core/src/banking_stage/vote_storage.rs:399"
  - "core/src/banking_stage/vote_storage.rs:214"
  - "core/src/banking_stage/latest_validator_vote_packet.rs:57"
  - "core/src/banking_stage/vote_storage.rs:356"
bug_class: improper-vote-authorization-filtering
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - consensus
  - validator
  - vote-handling
  - authorization
  - hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an authorization-consistency filter before `VoteStorage::insert_batch_with_replenish` updates latest-vote state. The evidence supports a likely security fix in consensus-facing vote packet handling, but it does not prove finality impact, invalid consensus acceptance, denial of service, fund loss, or whether later execution checks would have rejected the same packets.

## Observed Patch Facts

1. In `core/src/banking_stage/vote_storage.rs`, the patch replaces `fn test_reinsert_packets() -> Result<(), Box<dyn Error>> {` with `fn test_reinsert_packets() {`.

2. In `core/src/banking_stage/vote_storage.rs`, the patch replaces `if let Some(vote) = self.update_latest_vote(vote, should_replenish_taken_votes) {` with `if self`.

3. In `core/src/banking_stage/latest_validator_vote_packet.rs`, the patch replaces `let vote_account_index = instruction` with `let ix_key = |offset| {`.

4. In `core/src/banking_stage/vote_storage.rs`, the patch replaces `std::{error::Error, sync::Arc},` with `std::sync::Arc,`.

## Project Context

The changed code sits primarily in `core/src/banking_stage`, `core/src`, which anchors the finding in the `consensus` area of the project. Historical context from `core/src/banking_stage/vote_worker.rs`, `core/src/banking_stage/vote_packet_receiver.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/validator.rs`, `core/src/replay_stage.rs`. The strongest project-level identifiers around this patch are `DeserializedPacketError::VoteTransaction`, `vote`, `Keypair::new`, and `genesis_utils::create_genesis_config_with_leader`.

## Before/After Behavior

Before the change, the observed vote-storage insertion path skipped zero-stake vote accounts and then proceeded to `update_latest_vote` without an observed comparison against `cached_epoch_stakes.epoch_authorized_voters()`. After the change, it also drops votes when the vote account is absent from the epoch authorized-voter map or when the mapped authorized voter differs from `vote.authorized_voter_pubkey()`. A related parser change refactors instruction account-key extraction, but the supplied evidence only partially shows how that supports authorized-voter handling.

# Root Cause

The observed root cause was that vote storage enforced stake presence but did not enforce the current epoch authorized-voter mapping before mutating latest-vote state in this buffering path.

## Walkthrough

1. A vote transaction is parsed into a `LatestValidatorVote` in `latest_validator_vote_packet.rs`.

2. The parser code changed from first-account-specific extraction toward an offset-based helper for instruction account keys.

3. `VoteStorage::insert_batch_with_replenish` receives latest validator votes for banking-stage handling.

4. The function already skipped vote accounts with zero stake.

5. Before the patch, the next observed operation was updating latest-vote storage.

6. After the patch, the function checks `cached_epoch_stakes.epoch_authorized_voters().get(&vote.vote_pubkey())`.

7. Votes with no epoch authorized-voter entry, or with a mismatched authorized voter, are skipped before `update_latest_vote` runs.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/banking_stage/vote_storage.rs | 200 | Filters incoming latest validator votes by stake and current epoch authorized voter before updating vote storage state. |
| core/src/banking_stage/latest_validator_vote_packet.rs | 34 | Deserializes vote transactions and extracts instruction account keys used to identify vote account and authorized voter for downstream filtering. |
| core/src/banking_stage/vote_storage.rs | 395 | Regression test setup now creates validator vote accounts and exercises reinsertion behavior under the authorization-aware model. |

## Code Snippets

## Snippet 1

Context: `core/src/banking_stage/vote_storage.rs:399` (changes signature or replay validation logic)

Before
```rust
#[test]
    fn test_reinsert_packets() -> Result<(), Box<dyn Error>> {
        let node_keypair = Keypair::new();
        let genesis_config =
            genesis_utils::create_genesis_config_with_leader(100, &node_keypair.pubkey(), 200)
                .genesis_config;
        let (bank, _bank_forks) = Bank::new_with_bank_forks_for_tests(&genesis_config);
```
After
```rust
#[test]
    fn test_reinsert_packets() {
        let keypair = ValidatorVoteKeypairs::new_rand();
        let genesis_config =
            genesis_utils::create_genesis_config_with_vote_accounts(100, &[&keypair], vec![200])
                .genesis_config;
        let (bank, _bank_forks) = Bank::new_with_bank_forks_for_tests(&genesis_config);
```

## Snippet 2

Context: `core/src/banking_stage/vote_storage.rs:214` (changes a consensus- or validator-sensitive branch)

Before
```rust
continue;
            }
            if let Some(vote) = self.update_latest_vote(vote, should_replenish_taken_votes) {
                match vote.source() {
```
After
```rust
continue;
            }

            if self
                .cached_epoch_stakes
                .epoch_authorized_voters()
                .get(&vote.vote_pubkey())
                .is_none_or(|authorized| authorized != &vote.authorized_voter_pubkey())
```

## Snippet 3

Context: `core/src/banking_stage/latest_validator_vote_packet.rs:57` (changes a consensus- or validator-sensitive branch)

Before
```rust
if instruction_filter(&vote_state_update_instruction) =>
            {
                let vote_account_index = instruction
                    .accounts
                    .first()
                    .copied()
                    .ok_or(DeserializedPacketError::VoteTransaction)?;
                let vote_pubkey = vote
```
After
```rust
if instruction_filter(&vote_state_update_instruction) =>
            {
                let ix_key = |offset| {
                    let index = instruction
                        .accounts
                        .get(offset)
                        .copied()
                        .ok_or(DeserializedPacketError::VoteTransaction)?;
```

## Snippet 4

Context: `core/src/banking_stage/vote_storage.rs:356` (changes a sensitive control or state-update path)

Before
```rust
solana_vote::vote_transaction::new_tower_sync_transaction,
        solana_vote_program::vote_state::TowerSync,
        std::{error::Error, sync::Arc},
    };
```
After
```rust
solana_vote::vote_transaction::new_tower_sync_transaction,
        solana_vote_program::vote_state::TowerSync,
        std::sync::Arc,
    };
```

# Fix Pattern

Add an authorization check at the vote-storage ingestion boundary before mutating buffered latest-vote state.

## How It Was Fixed

The patch added an `epoch_authorized_voters()` lookup keyed by `vote.vote_pubkey()` and compares it with `vote.authorized_voter_pubkey()`. Mismatches and missing entries now `continue` out of insertion processing. Tests were adjusted to use genesis vote-account setup rather than only a leader key setup.

# Why It Matters

1. Prevents this vote-storage layer from retaining votes inconsistent with epoch authorization.

2. Places the check before latest-vote state mutation.

3. The affected path is consensus-facing banking-stage vote handling.

4. Broader consensus or exploit impact is not established by the supplied evidence.

# Evidence Notes

Strongest evidence is the added `epoch_authorized_voters()` comparison in `core/src/banking_stage/vote_storage.rs`. The commit message supports the intent to filter unauthorized votes, but the supplied hunks do not independently prove signature-check semantics. The parser change in `latest_validator_vote_packet.rs` is relevant support code, not clearly the root cause from the provided evidence. The test changes support authorization-aware coverage but are not themselves vulnerability evidence. Protocol security invariant: The banking-stage vote-storage path should only update latest-vote state for staked vote accounts whose packet-declared authorized voter matches the current epoch authorized voter for that vote account. Verification notes: The patch does not by itself prove an attacker could finalize invalid votes or alter consensus outcomes. The evidence does not show whether unauthorized packets would pass later bank or vote-program execution checks. The exact signature-validation implementation is not fully visible in the provided hunks, beyond the commit message and parser changes. No denial-of-service, fund loss, or slashing impact is proven from the patch alone. Confirmed by diff evidence that an authorized-voter map check was added before `update_latest_vote`. No evidence supplied that unauthorized packets could bypass later bank or vote-program checks. No evidence supplied for finality corruption, fund loss, slashing impact, or denial of service. Confidence is medium because the local invariant is clear but end-to-end security impact is bounded by missing context. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-vote-authorization-filtering`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, validator, vote-handling, authorization, hardening`

The supplied patch clearly adds an authorization-consistency filter in a consensus-facing vote-storage path before latest-vote state is updated. That supports retaining the case as security hardening. The evidence does not prove an exploitable security bug, invalid finality, state corruption, replay impact, or bypass of later vote-program execution checks, so the original security-fix and state-corruption framing is too strong.

## Security Evidence

1. VoteStorage now checks cached_epoch_stakes.epoch_authorized_voters() for the vote account before update_latest_vote runs.
2. Votes with no authorized-voter entry or a mismatched authorized voter are skipped.
3. The commit body explicitly says it filters unauthorized votes and checks the authorized voter has signed.
4. The changed path is banking-stage validator vote handling, which is consensus-sensitive.

## Missing Evidence

1. No end-to-end proof that unauthorized packets could pass later bank or vote-program validation.
2. No demonstrated exploit path or attacker-controlled scenario.
3. No evidence of finality failure, fund loss, slashing impact, denial of service, or concrete state corruption.
4. The supplied parser hunk only partially shows how authorized-voter extraction changed.

## Claim Boundaries

1. Validated only as authorization hardening in vote-storage ingestion.
2. Do not claim confirmed consensus compromise or state corruption from this evidence alone.
3. Do not claim replay vulnerability unless additional evidence shows replay acceptance.
4. Do not rely on the test cleanup or import cleanup as security evidence.
