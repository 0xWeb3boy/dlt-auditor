---
case_id: case_20211207_83e01442a7
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
impact_type:
  - state-integrity
source_quality: high
date: 2021-12-07
source_refs:
  - git:83e01442a7940eb600a6b4b19d37f2d03e6ca3cd
  - "programs/vote/src/vote_state/mod.rs:689"
  - "programs/vote/src/vote_instruction.rs:367"
  - "programs/vote/src/vote_state/mod.rs:1694"
  - "programs/vote/src/vote_instruction.rs:462"
bug_class: rent-exemption-invariant-hardening
confidence: medium
tags:
  - vote-program
  - rent-exemption
  - withdrawal
  - feature-gate
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Solana vote-program withdrawal handling to compute the post-withdraw balance and to pass optional Rent sysvar context into `vote_state::withdraw` when the `reject_non_rent_exempt_vote_withdraws` feature is active. This is plausibly security-relevant state-validity hardening, but the supplied evidence does not show the actual rent-exemption rejection conditional or establish an exploitable vulnerability. Treat as unclear rather than a confirmed security fix.

## Observed Patch Facts

1. In `programs/vote/src/vote_state/mod.rs`, the patch replaces `match vote_account.lamports()?.cmp(&lamports) {` with `let remaining_balance = vote_account`.

2. In `programs/vote/src/vote_instruction.rs`, the patch replaces `vote_state::withdraw(me, lamports, to, &signers)` with `let rent_sysvar = if invoke_context`.

3. In `programs/vote/src/vote_state/mod.rs`, the patch replaces `// all good` with `None,`.

4. In `programs/vote/src/vote_instruction.rs`, the patch replaces `super::process_instruction(` with `let mut invoke_context = MockInvokeContext::new(keyed_accounts);`.

## Project Context

The changed code sits primarily in `programs/vote/src/vote_state`, `programs/vote/src`, `programs/vote`, which anchors the finding in the `consensus` area of the project. Historical context from `programs/vote/src/vote_transaction.rs`, `programs/vote/src/vote_state/vote_state_versions.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. The strongest project-level identifiers around this patch are `InstructionError::InsufficientFunds`, `lamports`, `sysvar::rent::id`, and `KeyedAccount::new`.

## Before/After Behavior

Before the patch, `VoteInstruction::Withdraw` called `vote_state::withdraw(me, lamports, to, &signers)` without Rent sysvar context, and the shown withdraw code compared current lamports with the requested amount to reject insufficient funds or deinitialize on full withdrawal. After the patch, withdraw computes `remaining_balance` with `checked_sub`, treats zero balance as the deinitialization case, and the dispatcher conditionally loads `sysvar::rent::id()` under the new feature gate and passes `Some(Rent)` or `None` into `vote_state::withdraw`.

# Root Cause

The grounded issue is that the shown pre-patch withdraw path had no Rent context and the provided excerpt shows no check for whether a partial withdrawal left the vote account rent exempt. The stronger claim that this was an exploitable rent-exemption bypass is not established by the provided evidence.

## Walkthrough

1. An authorized withdraw instruction reaches `VoteInstruction::Withdraw(lamports)`.

2. Before the patch, dispatch selected the destination account and called `vote_state::withdraw` without Rent sysvar data.

3. The shown withdraw implementation verified the authorized withdrawer and handled insufficient funds or full-balance deinitialization.

4. The supplied before excerpt does not show rent-exemption validation for a nonzero remaining balance.

5. After the patch, withdraw computes `remaining_balance` with checked subtraction.

6. After the patch, dispatch checks the `reject_non_rent_exempt_vote_withdraws` feature gate and, when active, loads the Rent sysvar.

7. The Rent value is passed into `vote_state::withdraw`, indicating support for feature-gated rent validation.

8. The exact new rejection condition is not present in the supplied evidence, so the security conclusion remains uncertain.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/vote/src/vote_state/mod.rs | 679 | vote account withdraw implementation computes remaining balance after authorized withdrawal |
| programs/vote/src/vote_state/mod.rs | 689 | withdraw path deinitializes zero-balance accounts and, after the patch, can reject nonzero non-rent-exempt remainders |
| programs/vote/src/vote_instruction.rs | 367 | VoteInstruction::Withdraw dispatch conditionally loads Rent sysvar under the feature gate and passes it to vote_state::withdraw |
| programs/vote/src/vote_state/mod.rs | 1664 | withdraw tests cover insufficient funds and pre/post feature rent-exemption behavior |
| programs/vote/src/vote_instruction.rs | 429 | instruction tests mock Rent sysvar so withdraw processing exercises the new guarded path |

## Code Snippets

## Snippet 1

Context: `programs/vote/src/vote_state/mod.rs:689` (changes a consensus- or validator-sensitive branch)

Before
```rust
verify_authorized_signer(&vote_state.authorized_withdrawer, signers)?;

    match vote_account.lamports()?.cmp(&lamports) {
        Ordering::Less => return Err(InstructionError::InsufficientFunds),
        Ordering::Equal => {
            // Deinitialize upon zero-balance
            vote_account.set_state(&VoteStateVersions::new_current(VoteState::default()))?;
        }
```
After
```rust
verify_authorized_signer(&vote_state.authorized_withdrawer, signers)?;

    let remaining_balance = vote_account
        .lamports()?
        .checked_sub(lamports)
        .ok_or(InstructionError::InsufficientFunds)?;

    if remaining_balance == 0 {
```

## Snippet 2

Context: `programs/vote/src/vote_instruction.rs:367` (changes a consensus- or validator-sensitive branch)

Before
```rust
VoteInstruction::Withdraw(lamports) => {
            let to = keyed_account_at_index(keyed_accounts, 1)?;
            vote_state::withdraw(me, lamports, to, &signers)
        }
        VoteInstruction::AuthorizeChecked(vote_authorize) => {
```
After
```rust
VoteInstruction::Withdraw(lamports) => {
            let to = keyed_account_at_index(keyed_accounts, 1)?;
            let rent_sysvar = if invoke_context
                .is_feature_active(&feature_set::reject_non_rent_exempt_vote_withdraws::id())
            {
                Some(get_sysvar(invoke_context, &sysvar::rent::id())?)
            } else {
                None
```

## Snippet 3

Context: `programs/vote/src/vote_state/mod.rs:1694` (changes a consensus- or validator-sensitive branch)

Before
```rust
),
            &signers,
        );
        assert_eq!(res, Err(InstructionError::InsufficientFunds));

        // all good
        let to_account = RefCell::new(AccountSharedData::default());
        let lamports = vote_account.borrow().lamports();
```
After
```rust
),
            &signers,
            None,
        );
        assert_eq!(res, Err(InstructionError::InsufficientFunds));

        // non rent exempt withdraw, before feature activation
        {
```

## Snippet 4

Context: `programs/vote/src/vote_instruction.rs:462` (changes the branch that decides whether execution stops or continues)

Before
```rust
.map(|(meta, account)| KeyedAccount::new(&meta.pubkey, meta.is_signer, account))
                .collect();
            super::process_instruction(
                &Pubkey::default(),
                &instruction.data,
                &mut MockInvokeContext::new(keyed_accounts),
            )
        }
```
After
```rust
.map(|(meta, account)| KeyedAccount::new(&meta.pubkey, meta.is_signer, account))
                .collect();
            let mut invoke_context = MockInvokeContext::new(keyed_accounts);
            mock_set_sysvar(
                &mut invoke_context,
                sysvar::rent::id(),
                sysvar::rent::Rent::default(),
            )
```

# Fix Pattern

Make the post-withdraw balance explicit and pass required sysvar context into the state-transition function under a feature gate.

## How It Was Fixed

`programs/vote/src/vote_state/mod.rs` changed withdrawal accounting to compute `remaining_balance` using `checked_sub`, preserving insufficient-funds behavior. `programs/vote/src/vote_instruction.rs` changed withdraw dispatch to conditionally load `sysvar::rent::id()` when `reject_non_rent_exempt_vote_withdraws` is active and pass the resulting `Option<Rent>` into `vote_state::withdraw`. Tests were adjusted to pass `None` for pre-feature behavior and to mock Rent in instruction processing.

# Why It Matters

1. Vote-account withdrawal affects protocol-managed account state.

2. Rent-exemption status is a state-validity rule in Solana account handling.

3. The patch appears to harden partial-withdraw behavior.

4. The provided evidence does not prove theft, privilege escalation, consensus failure, or concrete exploitability.

# Evidence Notes

Grounded evidence includes the changed withdraw signature receiving `rent_sysvar: Option<Rent>`, computation of `remaining_balance` with `checked_sub`, and dispatch code that conditionally loads `sysvar::rent::id()` under `reject_non_rent_exempt_vote_withdraws`. The commit subject also states the intended behavior. However, the supplied hunks do not include the actual conditional that rejects a non-rent-exempt remaining balance, nor the feature_set hunk, so claims about the precise enforcement and impact must remain bounded. Protocol security invariant: Based on the commit subject and feature name, the intended invariant is that a vote-account withdrawal should not leave a live nonzero vote account below rent-exemption requirements once the feature gate is active. The supplied code evidence shows Rent being made available to the withdraw path, but does not include the exact rejection check. Verification notes: The patch does not prove theft, privilege escalation, or unauthorized withdrawal. The patch does not show consensus divergence by itself, only enforcement of a rent-exemption validity rule. The supplied evidence does not include the exact new rent-exemption conditional or feature_set hunk. Before-feature behavior appears intentionally preserved, so this should not be framed as an unconditional historical rejection path. The evidence does not prove impact on non-vote accounts or unrelated Solana programs. Do not classify as confirmed because the exact rent-exemption rejection code is absent from the provided evidence. Do not claim unauthorized withdrawal, fund theft, or privilege escalation. Do not generalize beyond vote-account withdrawal handling. Keep out of the security corpus unless additional evidence shows a concrete vulnerability or the missing rejection logic. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `rent-exemption-invariant-hardening`
Final confidence: `medium`
Final tags: `vote-program, rent-exemption, withdrawal, feature-gate, state-integrity`

The evidence supports retaining this as security hardening, not a confirmed security fix. The commit explicitly rejects vote withdrawals that would create non-rent-exempt accounts, adds feature-gated Rent sysvar loading in the vote withdrawal dispatch path, changes withdraw accounting to compute the remaining balance, and updates tests around non-rent-exempt withdrawal behavior. The supplied hunks do not show the exact rejection conditional or prove exploitability, so the finding should be bounded to protocol state-invariant hardening rather than state corruption or a concrete vulnerability fix.

## Security Evidence

1. Commit subject names rejection of vote withdraws that create non-rent-exempt accounts.
2. VoteInstruction::Withdraw now conditionally loads sysvar::rent under reject_non_rent_exempt_vote_withdraws.
3. vote_state::withdraw now receives optional Rent context, enabling rent-exemption validation in the withdrawal state transition.
4. Withdrawal logic now computes remaining_balance explicitly with checked_sub before branching on zero balance.
5. Tests were changed to cover non-rent-exempt withdraw behavior before feature activation and to mock Rent sysvar for instruction processing.

## Missing Evidence

1. The supplied evidence does not include the exact conditional that rejects a nonzero non-rent-exempt remaining balance.
2. No exploit scenario, advisory, or demonstrated consensus failure is provided.
3. No evidence shows unauthorized withdrawal, fund theft, or privilege escalation.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Limit scope to Solana vote-account withdrawal handling.
3. Do not claim state corruption beyond rent-exemption invariant enforcement.
4. Do not claim impact on unrelated accounts or programs.
5. Before-feature behavior appears intentionally preserved, so enforcement is feature-gated.
