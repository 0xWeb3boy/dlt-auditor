---
case_id: case_20200731_61d9d219f9
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
confidence: high
source_quality: high
date: 2020-07-31
source_refs:
  - git:61d9d219f943a8e5935d91dcc57ffad9b6ecbb0f
  - "programs/stake/src/stake_state.rs:112"
  - "cli/src/stake.rs:1486"
  - "cli/src/stake.rs:1536"
  - "core/src/non_circulating_supply.rs:24"
bug_class: authorization-role-confusion
impact_type:
  - access-control-bypass
  - lockup-bypass
  - economic-policy-bypass
tags:
  - staking
  - lockup
  - authorization
  - role-confusion
  - signature
  - custodian
  - withdraw-authority
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a stake lockup role-confusion issue. Before the change, `Lockup::is_in_force` treated the lockup as not in force when the custodian public key appeared anywhere in a generic signer set. The commit message states this allowed a withdraw authority signature, and similarly fee-payer signing, to imply custodian authority when keys overlapped, causing lockup enforcement to be skipped. After the change, the lockup exemption is granted only when an explicit optional custodian account matches the configured custodian.

## Observed Patch Facts

1. In `programs/stake/src/stake_state.rs`, the patch replaces `pub fn is_in_force(&self, clock: &Clock, signers: &HashSet<Pubkey>) -> bool {` with `pub fn is_in_force(&self, clock: &Clock, custodian: Option<&Pubkey>) -> bool {`.

2. In `cli/src/stake.rs`, the patch replaces `let lockup = if lockup.is_in_force(clock, &HashSet::new()) {` with `let lockup = if lockup.is_in_force(clock, None) {`.

3. In `cli/src/stake.rs`, the patch replaces `let lockup = if lockup.is_in_force(clock, &HashSet::new()) {` with `let lockup = if lockup.is_in_force(clock, None) {`.

4. In `core/src/non_circulating_supply.rs`, the patch replaces `if meta.lockup.is_in_force(&clock, &HashSet::default())` with `if meta.lockup.is_in_force(&clock, None)`.

## Project Context

The changed code sits primarily in `programs/stake/src`, `programs/stake`, `cli/src`, which anchors the finding in the `staking` area of the project. Historical context from `core/src/tree_diff.rs`, `core/src/rpc_subscriptions.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/tree_diff.rs`, `core/src/rpc_subscriptions.rs`. The strongest project-level identifiers around this patch are `lockup`, `clock`, `is_in_force`, and `HashSet::new`.

## Before/After Behavior

Before the patch, `Lockup::is_in_force(clock, signers)` returned false when the stake lockup was time/epoch active but `signers.contains(&self.custodian)` was true, so custodian authority was inferred from a broad signer set. After the patch, `Lockup::is_in_force(clock, custodian)` returns false only when `custodian == Some(&self.custodian)`; otherwise it evaluates the time or epoch lockup normally. Non-custodian contexts in CLI stake-state building and non-circulating supply calculation now pass `None`.

# Root Cause

The root cause was authorization role confusion: the lockup bypass decision used membership in a generic transaction signer set instead of a role-qualified custodian input. If another role used the same public key as the custodian, that role's signature could be interpreted as satisfying the custodian exemption.

## Walkthrough

1. A stake lockup contains time/epoch constraints and a custodian public key.

2. Before the fix, the lockup check accepted a `HashSet<Pubkey>` of signers.

3. If the custodian key appeared in that signer set, the function treated the lockup as not in force.

4. The commit message states this allowed withdraw authority signing to imply custodian signing when both roles shared a public key.

5. The patch changes the function to accept `Option<&Pubkey>` representing an explicit custodian argument.

6. The lockup exemption now applies only when that explicit custodian value matches the configured custodian.

7. Call sites that are only checking lockup state without a custodian exemption now pass `None`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/stake/src/stake_state.rs | 112 | Core lockup enforcement changed from signer-set membership to explicit custodian role matching. |
| cli/src/stake.rs | 1486 | Stake-state display/build path updated to evaluate lockup without implying any custodian. |
| cli/src/stake.rs | 1536 | Initialized stake-state display/build path updated to evaluate lockup without implying any custodian. |
| core/src/non_circulating_supply.rs | 24 | Supply classification path updated to test lockup status without treating any signer set as custodian. |

## Code Snippets

## Snippet 1

Context: `programs/stake/src/stake_state.rs:112` (updates aggregate accounting or lifecycle state)

Before
```rust
impl Lockup {
    pub fn is_in_force(&self, clock: &Clock, signers: &HashSet<Pubkey>) -> bool {
        (self.unix_timestamp > clock.unix_timestamp || self.epoch > clock.epoch)
            && !signers.contains(&self.custodian)
    }
}
```
After
```rust
impl Lockup {
    pub fn is_in_force(&self, clock: &Clock, custodian: Option<&Pubkey>) -> bool {
        if custodian == Some(&self.custodian) {
            return false;
        }
        self.unix_timestamp > clock.unix_timestamp || self.epoch > clock.epoch
    }
```

## Snippet 2

Context: `cli/src/stake.rs:1486` (updates aggregate accounting or lifecycle state)

Before
```rust
.delegation
                .stake_activating_and_deactivating(current_epoch, Some(stake_history));
            let lockup = if lockup.is_in_force(clock, &HashSet::new()) {
                Some(lockup.into())
            } else {
```
After
```rust
.delegation
                .stake_activating_and_deactivating(current_epoch, Some(stake_history));
            let lockup = if lockup.is_in_force(clock, None) {
                Some(lockup.into())
            } else {
```

## Snippet 3

Context: `cli/src/stake.rs:1536` (updates aggregate accounting or lifecycle state)

Before
```rust
lockup,
        }) => {
            let lockup = if lockup.is_in_force(clock, &HashSet::new()) {
                Some(lockup.into())
            } else {
```
After
```rust
lockup,
        }) => {
            let lockup = if lockup.is_in_force(clock, None) {
                Some(lockup.into())
            } else {
```

## Snippet 4

Context: `core/src/non_circulating_supply.rs:24` (updates aggregate accounting or lifecycle state)

Before
```rust
match stake_account {
            StakeState::Initialized(meta) => {
                if meta.lockup.is_in_force(&clock, &HashSet::default())
                    || withdraw_authority_list.contains(&meta.authorized.withdrawer)
                {
```
After
```rust
match stake_account {
            StakeState::Initialized(meta) => {
                if meta.lockup.is_in_force(&clock, None)
                    || withdraw_authority_list.contains(&meta.authorized.withdrawer)
                {
```

# Fix Pattern

Replace broad signer-set authorization checks with explicit role-qualified authority input for security-sensitive exemptions.

## How It Was Fixed

`Lockup::is_in_force` was changed from taking `&HashSet<Pubkey>` to taking `Option<&Pubkey>`. The function now bypasses lockup only when the supplied custodian option matches `self.custodian`; otherwise it checks `unix_timestamp > clock.unix_timestamp || epoch > clock.epoch`. Supporting call sites in `cli/src/stake.rs` and `core/src/non_circulating_supply.rs` were updated to pass `None` where no custodian role should be implied.

# Why It Matters

1. Preserves separation between withdraw authority, fee-payer, and custodian roles.

2. Prevents lockup bypass from generic signer-set membership.

3. Keeps stake lockup enforcement tied to an explicit custodian role.

4. Avoids treating overlapping public keys as interchangeable authorities.

# Evidence Notes

Strongest evidence is the `programs/stake/src/stake_state.rs` change from `signers.contains(&self.custodian)` to `custodian == Some(&self.custodian)`. The commit message directly states the pre-patch behavior could let withdraw authority or fee-payer signing imply custodian authority and skip lockup enforcement. The provided evidence does not establish arbitrary unauthenticated withdrawal, exploit frequency, or monetary impact magnitude. CLI and non-circulating supply changes are supporting semantic updates, not independent root causes. Protocol security invariant: Stake lockup constraints may be bypassed only by the stake account's custodian role being explicitly supplied for the lockup check; generic signer presence, withdraw authority signing, or fee-payer signing must not implicitly satisfy the custodian exemption. Verification notes: The patch does not prove arbitrary stake withdrawal by unauthenticated users. The evidence only supports bypass where another transaction role or signer could be confused with custodian authority. No monetary impact magnitude is established by the provided patch evidence. The CLI and supply-calculation updates support semantic consistency but are not themselves proof of exploitability. Confirmed by code diff in `Lockup::is_in_force`. Confirmed by commit message describing skipped lockup enforcement. No evidence provided for arbitrary unauthenticated access. No evidence provided for impact magnitude. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `authorization-role-confusion`
Final impact type: `access-control-bypass, lockup-bypass, economic-policy-bypass`
Final tags: `staking, lockup, authorization, role-confusion, signature, custodian, withdraw-authority`

The supplied commit message and patch evidence directly support a security-relevant fix: stake lockup enforcement previously depended on membership in a generic signer set, allowing withdraw authority or fee-payer signing to be treated as custodian authorization when public keys overlapped. The patch changes the enforcement API to require an explicit custodian account value, preserving role separation for a lockup bypass decision. The original accounting/state-drift framing is too broad and somewhat misleading; this is better retained as an authorization role-confusion lockup bypass fix.

## Security Evidence

1. Commit message states withdraw authority signature could imply custodian signature and lockup would not be enforced.
2. Core stake lockup check changed from `signers.contains(&self.custodian)` to explicit `custodian == Some(&self.custodian)`.
3. Non-custodian call sites now pass `None`, preventing ambient signer sets from granting the custodian exemption.
4. Touched code controls whether time/epoch stake lockup constraints remain in force.

## Missing Evidence

1. No evidence establishes arbitrary unauthenticated withdrawal.
2. No evidence quantifies monetary impact or exploit frequency.
3. No full withdraw-instruction call path is provided beyond the lockup helper and supporting call sites.

## Claim Boundaries

1. Supported claim: generic signer-set membership could incorrectly satisfy the custodian lockup exemption.
2. Supported claim: the fix enforces explicit custodian role selection for lockup bypass.
3. Unsupported claim: any attacker without a relevant signing key could bypass lockup.
4. Unsupported claim: this was primarily an RPC or accounting/state-drift bug.
