---
case_id: case_20190228_20e4edec61
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: staking
confidence: medium
source_quality: high
date: 2019-02-28
source_refs:
  - git:20e4edec615b38e2e1da67450cbffd1f05bc738e
  - "sdk/src/vote_program.rs:244"
  - "runtime/src/accounts.rs:253"
  - "runtime/src/bank.rs:716"
  - "sdk/src/vote_program.rs:209"
bug_class: vote-account-binding-confusion
impact_type:
  - consensus-integrity
  - authorization-integrity
tags:
  - blockchain-core
  - staking
  - vote-account
  - account-binding
  - leader-rotation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is plausibly security hardening for Solana vote account setup. The strongest evidence is the removed TODO in `sdk/src/vote_program.rs`, which explicitly warned that the old `register` flow assumed `keyed_accounts[0]` was the account creator for `keyed_accounts[1]` and that a different signed instruction in that slot could allow vote-account hijacking and leader-rotation insertion. The patch refactors the vote account setup path, adds explicit signer rejection before using `account[0]`, introduces a delegated stake path with a vote-program ownership check, and preserves vote account pubkeys during vote-state enumeration. The evidence does not prove a complete exploit path, so this should not be labeled a confirmed vulnerability fix.

## Observed Patch Facts

1. In `sdk/src/vote_program.rs`, the patch replaces `// TODO: This assumes keyed_accounts[0] is the SystemInstruction::CreateAccount` with `if keyed_accounts[0].signer_key().is_none() {`.

2. In `runtime/src/accounts.rs`, the patch replaces `.filter_map(|pubkey| self.load(fork, pubkey, true))` with `.filter_map(|pubkey| {`.

3. In `runtime/src/bank.rs`, the patch replaces `pub fn vote_states<F>(&self, cond: F) -> Vec<VoteState>` with `pub fn vote_states<F>(&self, cond: F) -> HashMap<Pubkey, VoteState>`.

4. In `sdk/src/vote_program.rs`, the patch replaces `// TODO: Deprecate the RegisterAccount instruction and its awkward delegation` with `pub fn delegate_stake(`.

## Project Context

The changed code sits primarily in `sdk/src`, `runtime/src`, which anchors the finding in the `staking` area of the project. Historical context from `sdk/src/account.rs`, `sdk/src/pubkey.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/src/native_program.rs`, `sdk/src/account.rs`. The strongest project-level identifiers around this patch are `keyed_accounts`, `account`, `pubkey`, and `ProgramError::InvalidArgument`.

## Before/After Behavior

Before the patch, vote account registration relied on positional assumptions about `keyed_accounts[0]` and then unwrapped its signer key. A removed TODO explicitly described that assumption as unsafe for vote-account control and leader rotation. After the patch, account initialization rejects a missing `account[0]` signer before deriving `staker_id`, the old register-style path is replaced with `delegate_stake(keyed_accounts, node_id)` that checks vote-program ownership at `keyed_accounts[0]`, and runtime vote account enumeration retains the vote account `Pubkey` instead of returning only account or vote-state values.

# Root Cause

The grounded issue is an unsafe or underspecified vote-account binding assumption in the old registration flow. The code evidence supports concern about positional account confusion, but does not fully establish that arbitrary account ordering was exploitable in practice or that the shown checks alone close the entire issue.

## Walkthrough

1. The old vote registration code assumed `keyed_accounts[0]` was the create-account signer associated with `keyed_accounts[1]`.

2. A removed TODO stated that another signed instruction in `keyed_accounts[0]` could allow vote-account hijacking and insertion into leader rotation.

3. The patch adds an explicit missing-signer check before using `keyed_accounts[0].signer_key()`.

4. The old register semantics are refactored into initialization and `delegate_stake` paths.

5. The delegation path checks that the relevant account is owned by the vote program.

6. `AccountsDB::get_vote_accounts` now returns vote accounts keyed by their pubkey.

7. `Bank::vote_states` now exposes vote account pubkeys to filtering logic.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/src/vote_program.rs | 209 | vote program stake delegation path; replaces awkward register semantics and checks the delegated vote account is owned by the vote program |
| sdk/src/vote_program.rs | 244 | vote account initialization path; requires account[0] to be a signer before deriving staker identity |
| runtime/src/accounts.rs | 249 | vote account index lookup; returns vote accounts keyed by their actual pubkey |
| runtime/src/bank.rs | 716 | bank vote state enumeration; exposes vote account pubkey to filtering and downstream consensus/staking logic |

## Code Snippets

## Snippet 1

Context: `sdk/src/vote_program.rs:244` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    // TODO: This assumes keyed_accounts[0] is the SystemInstruction::CreateAccount
    // that created keyed_accounts[1]. Putting any other signed instruction in
    // keyed_accounts[0] would allow the owner to highjack the vote account and
    // insert itself into the leader rotation.
    let from_id = keyed_accounts[0].signer_key().unwrap();
```
After
```rust
}

    if keyed_accounts[0].signer_key().is_none() {
        error!("account[0] should sign the transaction");
        Err(ProgramError::InvalidArgument)?;
    }

    let staker_id = keyed_accounts[0].signer_key().unwrap();
```

## Snippet 2

Context: `runtime/src/accounts.rs:253` (changes a consensus- or validator-sensitive branch)

Before
```rust
.unwrap()
            .iter()
            .filter_map(|pubkey| self.load(fork, pubkey, true))
            .collect()
    }
```
After
```rust
.unwrap()
            .iter()
            .filter_map(|pubkey| {
                if let Some(account) = self.load(fork, pubkey, true) {
                    Some((*pubkey, account))
                } else {
                    None
                }
```

## Snippet 3

Context: `runtime/src/bank.rs:716` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    pub fn vote_states<F>(&self, cond: F) -> Vec<VoteState>
    where
        F: Fn(&VoteState) -> bool,
    {
        self.accounts()
            .get_vote_accounts(self.id)
```
After
```rust
}

    pub fn vote_states<F>(&self, cond: F) -> HashMap<Pubkey, VoteState>
    where
        F: Fn(&Pubkey, &VoteState) -> bool,
    {
        self.accounts()
            .get_vote_accounts(self.id)
```

## Snippet 4

Context: `sdk/src/vote_program.rs:209` (changes an authorization or privilege gate)

Before
```rust
}

// TODO: Deprecate the RegisterAccount instruction and its awkward delegation
// semantics.
pub fn register(keyed_accounts: &mut [KeyedAccount]) -> Result<(), ProgramError> {
    if !check_id(&keyed_accounts[1].account.owner) {
        error!("account[1] is not assigned to the VOTE_PROGRAM");
```
After
```rust
}

pub fn delegate_stake(
    keyed_accounts: &mut [KeyedAccount],
    node_id: Pubkey,
) -> Result<(), ProgramError> {
    if !check_id(&keyed_accounts[0].account.owner) {
        error!("account[0] is not assigned to the VOTE_PROGRAM");
```

# Fix Pattern

Replace implicit positional account assumptions with explicit signer and owner validation, while preserving vote account identity through runtime vote-state enumeration.

## How It Was Fixed

The patch rejects missing signer input before deriving staker identity, refactors the awkward registration semantics into explicit initialization and stake delegation paths, checks vote-program ownership in delegation, and changes vote account collection APIs to keep the `Pubkey` associated with each vote account or vote state.

# Why It Matters

1. The removed TODO directly identifies a leader-rotation hijack risk.

2. Vote account identity affects consensus-sensitive validator and staking behavior.

3. Preserving pubkeys reduces the risk of detached vote-state handling.

4. Exploitability is not fully demonstrated by the supplied evidence.

# Evidence Notes

Supported by supplied hunks in `sdk/src/vote_program.rs`, `runtime/src/accounts.rs`, and `runtime/src/bank.rs`. The security claim rests mainly on the removed TODO describing hijack risk. Claims about stolen funds, signature forgery, remote exploitability, or a complete attack path are unsupported. The runtime `HashMap` changes may also be API refactoring unless connected to specific downstream identity checks. Protocol security invariant: Vote account setup and delegation should bind vote-account identity, staker authority, and leader-rotation eligibility to the intended signed and vote-program-owned accounts, not to an incidental signed account position. Verification notes: The patch does not prove a complete remote exploit path by itself. The evidence does not show whether pre-patch transaction validation allowed arbitrary signed account ordering in practice. The runtime HashMap change may be partly refactor/API cleanup unless tied to vote-account identity checks at call sites. No evidence is provided of stolen funds, signature forgery, or unauthorized private key use. The commit subject frames this as refactoring, so the safest label is hardening/likely security rather than confirmed vulnerability fix. No full transaction validation path is provided. No call-site evidence proves arbitrary signed account ordering was accepted. No regression test evidence is supplied in the excerpts. Commit subject says refactor, so classify as likely hardening rather than confirmed security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `vote-account-binding-confusion`
Final impact type: `consensus-integrity, authorization-integrity`
Final tags: `blockchain-core, staking, vote-account, account-binding, leader-rotation, security-hardening`

The supplied patch evidence supports retaining this as security hardening, but not as a confirmed vulnerability fix. The strongest evidence is the removed TODO explicitly describing a vote-account hijack and leader-rotation insertion risk from unsafe positional assumptions in vote account registration. The refactor adds explicit signer rejection, introduces a delegation path with vote-program ownership validation, and preserves vote account pubkeys in runtime enumeration. However, the excerpts do not prove the full transaction path accepted exploitable arbitrary account ordering or that these changes completely closed the described issue.

## Security Evidence

1. Removed comment explicitly described a vote-account hijack and leader-rotation insertion risk.
2. Vote account initialization now rejects a missing signer before deriving staker identity from account[0].
3. Delegation path checks that the relevant account is owned by the vote program.
4. Runtime vote account APIs now retain vote account pubkeys, reducing detached vote-state handling risk in consensus-sensitive code.

## Missing Evidence

1. No complete exploit path or transaction validation path is shown.
2. No call-site evidence proves arbitrary signed account ordering was accepted pre-patch.
3. No regression test excerpt demonstrates the hijack scenario or its prevention.
4. Commit subject frames the change as a refactor, not an explicit security fix.

## Claim Boundaries

1. Do not classify as a confirmed security-fix from the supplied patch alone.
2. Do not claim stolen funds, signature forgery, or private-key compromise.
3. Do not assume the HashMap/pubkey-preservation changes are independently security fixes without downstream evidence.
4. Supported claim is limited to security hardening around vote-account binding, delegation, and leader-rotation-sensitive identity handling.
