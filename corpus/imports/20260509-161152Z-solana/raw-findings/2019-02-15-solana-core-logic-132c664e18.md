---
case_id: case_20190215_132c664e18
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: core-logic
impact_type:
  - state-integrity
confidence: medium
source_quality: high
date: 2019-02-15
source_refs:
  - git:132c664e18fe9e3239596f54db840a948cac2389
  - "sdk/src/vote_program.rs:152"
  - "programs/native/rewards/src/lib.rs:114"
  - "programs/native/rewards/src/lib.rs:108"
  - "programs/native/rewards/src/lib.rs:68"
bug_class: cross-program-state-mutation
tags:
  - blockchain-core
  - core-logic
  - ownership-boundary
  - state-integrity
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch removes rewards-program writes to vote account userdata and adds a vote-program `clear_credits` path with an owner check. The strongest supported finding is state-integrity hardening around program ownership boundaries. The evidence does not establish reward theft, arbitrary account mutation, or consensus failure.

## Observed Patch Facts

1. In `sdk/src/vote_program.rs`, the patch replaces `pub fn create_vote_account(tokens: u64) -> Account {` with `pub fn clear_credits(keyed_accounts: &mut [KeyedAccount]) -> Result<(), ProgramError> {`.

2. In `programs/native/rewards/src/lib.rs`, the patch replaces `redeem_vote_credits(&mut keyed_accounts)?;` with `redeem_vote_credits(&mut keyed_accounts)`.

3. In `programs/native/rewards/src/lib.rs`, the patch replaces `) -> Result<VoteState, ProgramError> {` with `) -> Result<(), ProgramError> {`.

4. In `programs/native/rewards/src/lib.rs`, the patch removes `// TODO: The runtime should reject this, because this program`.

## Project Context

The changed code sits primarily in `sdk/src`, `programs/native/rewards/src`, `programs/native/rewards`, which anchors the finding in the `core-logic` area of the project. Historical context from `sdk/src/account.rs`, `sdk/src/native_program.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/src/native_program.rs`, `sdk/src/account.rs`. The strongest project-level identifiers around this patch are `keyed_accounts`, `account`, `KeyedAccount::new`, and `vote_state`. Nearby tests or test-like files include `programs/native/rewards/tests/rewards.rs`.

## Before/After Behavior

Before the patch, `redeem_vote_credits` read `VoteState`, paid rewards, then cleared credits and serialized the modified vote state back into `keyed_accounts[0].account.userdata` from the rewards program. The deleted comment said the runtime should reject this because the rewards program was not the owner of the VoteState account. After the patch, rewards redemption still reads vote state and transfers rewards, but no longer mutates vote userdata. Credit clearing is moved to `sdk/src/vote_program.rs::clear_credits`, which checks that account 0 is owned by the vote program before mutating userdata.

# Root Cause

The rewards redemption path directly mutated vote-program-owned account userdata. This crossed the intended account ownership boundary, even though the supplied evidence does not prove an exploitable attack path.

## Walkthrough

1. A vote account stores vote credits in account userdata and has an owner field identifying the owning program.

2. The old rewards redemption path deserialized `VoteState` from the vote account userdata.

3. It validated signer, vote-program ownership, staker account, and stake before calculating and transferring rewards.

4. After the transfer, it called `vote_state.clear_credits()` and serialized the changed state back into the vote account userdata.

5. A deleted TODO stated that the runtime should reject this because the rewards program was not the owner of the VoteState account.

6. The patch removes that clear-and-serialize operation from rewards redemption.

7. The patch adds `vote_program::clear_credits`, which checks the account owner is `VOTE_PROGRAM` before clearing and serializing vote credits.

8. Tests/helpers were adjusted so redemption success no longer returns or implies a mutated `VoteState`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/native/rewards/src/lib.rs | 31 | Rewards redemption reads vote state, validates signer/owner/staker/stake, and transfers rewards without clearing external vote userdata after the patch. |
| programs/native/rewards/src/lib.rs | 68 | Removed cross-program mutation of vote account userdata via `vote_state.clear_credits()` and `serialize()`. |
| sdk/src/vote_program.rs | 152 | New vote-program-owned `clear_credits` path checks account ownership, clears VoteState credits, and serializes back to vote account userdata. |
| programs/native/rewards/src/lib.rs | 103 | Test helper return shape changes from returning mutated VoteState to returning only redemption success, reflecting that rewards redemption no longer mutates vote userdata. |

## Code Snippets

## Snippet 1

Context: `sdk/src/vote_program.rs:152` (changes an authorization or privilege gate)

Before
```rust
}

pub fn create_vote_account(tokens: u64) -> Account {
    let space = get_max_size();
```
After
```rust
}

pub fn clear_credits(keyed_accounts: &mut [KeyedAccount]) -> Result<(), ProgramError> {
    if !check_id(&keyed_accounts[0].account.owner) {
        error!("account[0] is not assigned to the VOTE_PROGRAM");
        Err(ProgramError::InvalidArgument)?;
    }
```

## Snippet 2

Context: `programs/native/rewards/src/lib.rs:114` (changes a consensus- or validator-sensitive branch)

Before
```rust
KeyedAccount::new(to_id, false, to_account),
        ];
        redeem_vote_credits(&mut keyed_accounts)?;
        let vote_state = VoteState::deserialize(&vote_account.userdata).unwrap();
        Ok(vote_state)
    }
```
After
```rust
KeyedAccount::new(to_id, false, to_account),
        ];
        redeem_vote_credits(&mut keyed_accounts)
    }
```

## Snippet 3

Context: `programs/native/rewards/src/lib.rs:108` (changes a consensus- or validator-sensitive branch)

Before
```rust
to_id: &Pubkey,
        to_account: &mut Account,
    ) -> Result<VoteState, ProgramError> {
        let mut keyed_accounts = [
            KeyedAccount::new(vote_id, true, vote_account),
```
After
```rust
to_id: &Pubkey,
        to_account: &mut Account,
    ) -> Result<(), ProgramError> {
        let mut keyed_accounts = [
            KeyedAccount::new(vote_id, true, vote_account),
```

## Snippet 4

Context: `programs/native/rewards/src/lib.rs:68` (changes a consensus- or validator-sensitive branch)

Before
```rust
keyed_accounts[2].account.tokens += lamports;

    // TODO: The runtime should reject this, because this program
    // is not the owner of the VoteState account.
    vote_state.clear_credits();
    vote_state.serialize(&mut keyed_accounts[0].account.userdata)?;

    Ok(())
```
After
```rust
keyed_accounts[2].account.tokens += lamports;

    Ok(())
}
```

# Fix Pattern

Move account state mutation to the owning program boundary and guard it with an owner check.

## How It Was Fixed

The rewards program no longer calls `vote_state.clear_credits()` or serializes into `keyed_accounts[0].account.userdata`. A new vote-program function performs the credit clearing after checking `check_id(&keyed_accounts[0].account.owner)`. Test helper return behavior was updated to reflect that rewards redemption no longer mutates vote userdata.

# Why It Matters

1. Preserves owner-based boundaries for account userdata mutation.

2. Prevents rewards redemption from modifying vote-program-owned state as a side effect.

3. Makes vote credit clearing an explicit vote-program operation.

4. Does not prove theft, arbitrary mutation, or consensus failure from the supplied evidence.

# Evidence Notes

Direct evidence is the removed write in `programs/native/rewards/src/lib.rs`, including the deleted TODO saying the runtime should reject the write because the rewards program is not the owner. Supporting evidence is the new `sdk/src/vote_program.rs::clear_credits` function, which checks vote-program ownership before mutation. Claims beyond ownership-boundary hardening are unsupported. Protocol security invariant: Account userdata should be mutated by the program that owns that account. Vote credits are stored in vote-program-owned account userdata, so clearing those credits should occur through the vote program after checking the account owner, not as a side effect of rewards redemption. Verification notes: The patch does not prove an arbitrary attacker could modify any external account userdata. The patch does not show whether the runtime generally allowed non-owner userdata writes outside this native program path. The patch does not prove reward theft or consensus failure by itself. The remaining TODO about verifying a following ClearCredits instruction is not resolved by the shown rewards hunk. Verified only against the provided diff excerpts and draft context. No external files, commands, or repository inspection were used. Exploitability is not established by the supplied evidence. Remaining TODO about verifying a following `ClearCredits` instruction is not shown as resolved. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cross-program-state-mutation`
Final tags: `blockchain-core, core-logic, ownership-boundary, state-integrity, security-hardening`

The supplied patch evidence clearly supports security hardening around account ownership boundaries: the rewards program previously cleared and serialized vote-program-owned userdata despite a TODO saying the runtime should reject that non-owner write, and the patch removes that write while adding a vote-program clear_credits path guarded by an owner check. The evidence does not prove a concrete exploit, theft, arbitrary account mutation, or consensus failure, so this should remain hardening rather than a confirmed security-fix case.

## Security Evidence

1. Removed rewards-program calls to vote_state.clear_credits() and serialize() on keyed_accounts[0].account.userdata.
2. Deleted comment explicitly stated the runtime should reject the write because the rewards program was not the owner of the VoteState account.
3. Added vote_program::clear_credits that checks keyed_accounts[0].account.owner against the vote program before mutating userdata.
4. Test/helper return shape was changed so rewards redemption no longer returns or implies a mutated VoteState.

## Missing Evidence

1. No proof that an attacker could trigger unauthorized arbitrary userdata mutation.
2. No proof of reward theft, fund loss, or consensus failure from the shown patch.
3. No complete transaction-level evidence showing how ClearCredits sequencing is enforced.
4. No evidence that the runtime generally allowed non-owner writes beyond this native program path.

## Claim Boundaries

1. Supported claim: the patch hardens ownership-boundary handling for vote account userdata mutation.
2. Supported claim: rewards redemption no longer directly mutates external vote-program-owned userdata.
3. Unsupported claim: this fixes a demonstrated exploitable vulnerability.
4. Unsupported claim: this proves arbitrary account corruption, reward theft, or consensus compromise.
