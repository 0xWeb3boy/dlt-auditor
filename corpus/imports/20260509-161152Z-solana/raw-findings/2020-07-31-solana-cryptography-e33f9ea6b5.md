---
case_id: case_20200731_e33f9ea6b5
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: high
source_quality: high
date: 2020-07-31
source_refs:
  - git:e33f9ea6b587a5828c83aa0e5a165e68b5eac96a
  - "programs/stake/src/stake_state.rs:112"
  - "core/src/non_circulating_supply.rs:24"
  - "core/src/non_circulating_supply.rs:31"
  - "programs/stake/src/stake_state.rs:823"
bug_class: authorization-role-confusion
impact_type:
  - lockup-bypass
  - authorization-bypass
tags:
  - infrastructure
  - stake-program
  - authorization
  - role-confusion
  - lockup-bypass
  - withdrawal
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a stake lockup bypass caused by treating custodian authorization as membership in a generic signer set. The strongest grounded claim is authority-role confusion in stake withdrawal lockup enforcement, not replay, cryptography, network, or validator repair logic.

## Observed Patch Facts

1. In `programs/stake/src/stake_state.rs`, the patch replaces `pub fn is_in_force(&self, clock: &Clock, signers: &HashSet<Pubkey>) -> bool {` with `pub fn is_in_force(&self, clock: &Clock, custodian: Option<&Pubkey>) -> bool {`.

2. In `core/src/non_circulating_supply.rs`, the patch replaces `if meta.lockup.is_in_force(&clock, &HashSet::default())` with `if meta.lockup.is_in_force(&clock, None)`.

3. In `core/src/non_circulating_supply.rs`, the patch replaces `if meta.lockup.is_in_force(&clock, &HashSet::default())` with `if meta.lockup.is_in_force(&clock, None)`.

4. In `programs/stake/src/stake_state.rs`, the patch replaces `signers: &HashSet<Pubkey>,` with `withdraw_authority: &KeyedAccount,`.

## Project Context

The changed code sits primarily in `programs/stake/src`, `programs/stake`, `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `programs/stake/src/stake_instruction.rs`, `core/src/window_service.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/stake/src/stake_instruction.rs`, `core/src/window_service.rs`. The strongest project-level identifiers around this patch are `clock`, `meta`, `is_in_force`, and `signers`.

## Before/After Behavior

Before the change, `Lockup::is_in_force` accepted a general signer set and waived lockup enforcement when that set contained the custodian pubkey. The commit states this let a withdraw authority signature imply a custodian signature when the withdraw authority and custodian had the same public key, and that the fee-payer could also imply withdraw authority or custodian in related handling. After the change, `is_in_force` accepts an explicit optional custodian pubkey and waives lockup only when that explicit custodian matches the configured custodian. The withdraw path now receives explicit withdraw authority and optional custodian accounts, and non-circulating-supply checks pass `None` when no custodian context exists.

# Root Cause

The root cause was using a generic transaction signer set to decide whether the custodian role had authorized a lockup waiver. Because withdraw authority, custodian, and fee-payer are distinct roles, signer-set membership could conflate those roles when the same pubkey appeared in the signer context.

## Walkthrough

1. `programs/stake/src/stake_state.rs` previously implemented `Lockup::is_in_force` with `signers.contains(&self.custodian)` as the condition that disabled lockup enforcement.

2. That made the lockup waiver depend on generic signer membership rather than on an explicitly supplied custodian account.

3. The commit message identifies the failure mode: a withdraw authority signature could imply a custodian signature when both roles used the same public key, so lockup was not enforced.

4. The patch changes `Lockup::is_in_force` to accept `custodian: Option<&Pubkey>` and return not-in-force only when that explicit custodian equals the configured custodian.

5. The withdraw implementation now accepts `withdraw_authority: &KeyedAccount` and `custodian: Option<&KeyedAccount>` separately instead of receiving one shared signer set.

6. The withdraw path constructs its withdraw-authority signer set from the explicit withdraw authority account and checks that role separately.

7. `core/src/non_circulating_supply.rs` now calls `is_in_force(&clock, None)` for stake-account classification, making clear that supply calculation has no custodian waiver context.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/stake/src/stake_state.rs | 112 | Lockup::is_in_force now distinguishes explicit custodian presence from arbitrary transaction signer membership. |
| programs/stake/src/stake_state.rs | 819 | StakeAccount::withdraw now receives explicit withdraw_authority and optional custodian accounts instead of a shared signer set. |
| core/src/non_circulating_supply.rs | 24 | Initialized stake supply classification calls lockup checking with no custodian context. |
| core/src/non_circulating_supply.rs | 31 | Staked account supply classification calls lockup checking with no custodian context. |
| programs/stake/src/stake_instruction.rs | 3 | Stake instruction handling context for keyed accounts and explicit account roles used by withdraw processing. |

## Code Snippets

## Snippet 1

Context: `programs/stake/src/stake_state.rs:112` (changes a consensus- or validator-sensitive branch)

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

Context: `core/src/non_circulating_supply.rs:24` (changes a sensitive control or state-update path)

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

## Snippet 3

Context: `core/src/non_circulating_supply.rs:31` (changes a sensitive control or state-update path)

Before
```rust
}
            StakeState::Stake(meta, _stake) => {
                if meta.lockup.is_in_force(&clock, &HashSet::default())
                    || withdraw_authority_list.contains(&meta.authorized.withdrawer)
                {
```
After
```rust
}
            StakeState::Stake(meta, _stake) => {
                if meta.lockup.is_in_force(&clock, None)
                    || withdraw_authority_list.contains(&meta.authorized.withdrawer)
                {
```

## Snippet 4

Context: `programs/stake/src/stake_state.rs:823` (changes a sensitive control or state-update path)

Before
```rust
clock: &Clock,
        stake_history: &StakeHistory,
        signers: &HashSet<Pubkey>,
    ) -> Result<(), InstructionError> {
        let (lockup, reserve, is_staked) = match self.state()? {
            StakeState::Stake(meta, stake) => {
                meta.authorized.check(signers, StakeAuthorize::Withdrawer)?;
                // if we have a deactivation epoch and we're in cooldown
```
After
```rust
clock: &Clock,
        stake_history: &StakeHistory,
        withdraw_authority: &KeyedAccount,
        custodian: Option<&KeyedAccount>,
    ) -> Result<(), InstructionError> {
        let mut signers = HashSet::new();
        let withdraw_authority_pubkey = withdraw_authority
            .signer_key()
```

# Fix Pattern

Replace generic signer-set checks for privileged role bypasses with explicit account-role binding, so each authorization decision is tied to the specific role account being evaluated.

## How It Was Fixed

The fix changed lockup waiver logic from `signers.contains(&self.custodian)` to `custodian == Some(&self.custodian)`. It also refactored withdraw handling to receive separate keyed accounts for withdraw authority and optional custodian, and updated non-circulating-supply callers to pass `None` when no custodian account is present.

# Why It Matters

1. Prevents withdraw authority from implicitly waiving stake lockup constraints.

2. Preserves separation between withdraw authority, custodian, and fee-payer roles.

3. Makes lockup bypass require an explicit custodian account argument.

4. Avoids overbroad authorization decisions based on incidental signer-set membership.

# Evidence Notes

Evidence directly supports a stake withdraw lockup authority-role-confusion fix. It does not support the heuristic claims of replay handling, general cryptographic validation, network/shred-path impact, arbitrary withdrawal without a valid withdraw authority, quantified economic loss, or established production exploitation. Protocol security invariant: Stake lockup must remain enforced until its configured timestamp or epoch expires unless the withdraw instruction explicitly supplies the authorized custodian account. A withdraw authority or fee-payer signature must not implicitly satisfy the separate custodian role. Verification notes: The evidence supports lockup-bypass prevention, not a general cryptographic replay issue. The patch does not prove arbitrary unauthorized withdrawal without valid withdraw authority. The patch does not show network, shred, or validator repair-path impact despite traced unrelated core contexts. The evidence does not quantify economic impact or whether affected accounts existed in production. Confirmed by the before/after change to `Lockup::is_in_force` in `programs/stake/src/stake_state.rs`. Confirmed by the withdraw signature path changing from a shared signer set to explicit withdraw authority and optional custodian accounts. Supported by the commit message describing withdraw authority and fee-payer implication of custodian or withdraw authority roles. Supporting supply-calculation changes pass `None` for custodian context and are not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `authorization-role-confusion`
Final impact type: `lockup-bypass, authorization-bypass`
Final tags: `infrastructure, stake-program, authorization, role-confusion, lockup-bypass, withdrawal`

The supplied commit message and patch evidence support a real security-relevant authorization fix: stake lockup enforcement previously depended on a generic signer set, allowing withdraw authority or fee-payer signer context to satisfy a distinct custodian role under some key/account arrangements. The patch changes the API and call sites to require an explicit optional custodian account for lockup waiver decisions. The original replay/cryptography framing is too broad and misleading, but the authority-role-confusion lockup bypass claim is well supported.

## Security Evidence

1. Commit message states withdraw authority signature could imply custodian signature when both used the same public key, causing lockup not to be enforced.
2. Lockup::is_in_force changed from checking signers.contains(custodian) to checking an explicit optional custodian pubkey.
3. Withdraw handling changed from accepting a shared signer set to accepting separate withdraw_authority and optional custodian accounts.
4. Non-circulating supply callers now pass None when there is no custodian context, preserving lockup enforcement outside explicit custodian authorization.

## Missing Evidence

1. No evidence of production exploitation or affected account counts.
2. No evidence supporting replay, request forgery, network, shred, or validator repair impact.
3. No quantified economic impact is shown.
4. Patch evidence does not show arbitrary withdrawal without a valid withdraw authority.

## Claim Boundaries

1. Keep the finding scoped to stake lockup authorization and explicit custodian role binding.
2. Do not classify this as a cryptographic replay or request-forgery issue.
3. Do not claim general validator or network consensus compromise beyond the stake program authorization path shown.
4. Do not claim exploitability for accounts where withdraw authority and custodian were distinct unless separately evidenced.
