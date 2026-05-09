---
case_id: case_20190301_db825b6e26
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2019-03-01
source_refs:
  - git:db825b6e2696aec4f9ae921594dc9159efeadffa
  - "programs/native/vote/src/lib.rs:22"
  - "sdk/src/vote_program.rs:273"
  - "sdk/src/transaction_builder.rs:54"
  - "sdk/src/vote_program.rs:409"
bug_class: missing-signature-check
impact_type:
  - authorization-bypass
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - vote-program
  - signature-check
  - authorization
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch moves a signer check from a blanket native vote entrypoint guard into sdk/src/vote_program.rs::process_vote, immediately before VoteState is deserialized, mutated, and serialized. This is security-relevant authorization hardening, but the provided evidence does not establish that unsigned votes were accepted through the normal runtime path before the patch, because the old entrypoint already rejected unsigned keyed_accounts[0] before dispatch.

## Observed Patch Facts

1. In `programs/native/vote/src/lib.rs`, the patch replaces `// all vote instructions require that accounts_keys[0] be a signer` with `match deserialize(data).map_err(|_| ProgramError::InvalidUserdata)? {`.

2. In `sdk/src/vote_program.rs`, the patch replaces `vote_state.process_vote(vote);` with `if keyed_accounts[0].signer_key().is_none() {`.

3. In `sdk/src/transaction_builder.rs`, the patch replaces `fn keys(&self) -> Vec<Pubkey> {` with `fn keys(&self) -> (Vec<Pubkey>, Vec<Pubkey>) {`.

4. In `sdk/src/vote_program.rs`, the patch replaces `fn test_vote_without_initialization() {` with `fn test_vote_signature() {`.

## Project Context

The changed code sits primarily in `programs/native/vote/src`, `programs/native/vote`, `sdk/src`, which anchors the finding in the `staking` area of the project. Historical context from `sdk/src/vote_transaction.rs`, `sdk/src/transaction.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/src/vote_transaction.rs`, `sdk/src/transaction.rs`. The strongest project-level identifiers around this patch are `keyed_accounts`, `ProgramError::InvalidArgument`, `Keypair::new`, and `Pubkey`. Nearby tests or test-like files include `programs/native/vote/tests/vote.rs`.

## Before/After Behavior

Before the patch, the native vote entrypoint rejected any vote-program instruction if keyed_accounts[0] was not a signer, while process_vote itself performed owner validation and then mutated VoteState without a local signer check. After the patch, the entrypoint no longer applies the blanket signer requirement, and process_vote rejects unsigned keyed_accounts[0] before vote state mutation. The transaction builder also separates signed and unsigned keys to support detecting missing required keypairs during transaction construction.

# Root Cause

The supported issue is misplaced or implicit authorization enforcement: process_vote depended on callers, such as the native entrypoint, to enforce its signer precondition. The evidence does not prove an externally reachable bypass of that precondition in normal execution.

## Walkthrough

1. The old native vote entrypoint checked keyed_accounts[0].signer_key() before dispatching any VoteInstruction.

2. The patch removes that blanket pre-dispatch signer check.

3. process_vote already checked that keyed_accounts[0].account.owner matched the vote program.

4. Before the patch, process_vote then deserialized, updated, and serialized VoteState without its own signer check.

5. After the patch, process_vote rejects unsigned keyed_accounts[0] before mutating VoteState.

6. A regression test exercises direct unsigned process_vote handling.

7. The transaction builder change is supportive client-side hardening, not runtime protocol enforcement.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/native/vote/src/lib.rs | 22 | removes blanket signer requirement from vote program entrypoint before instruction dispatch |
| sdk/src/vote_program.rs | 273 | adds vote-account signer requirement directly before vote state mutation |
| sdk/src/transaction_builder.rs | 54 | separates signed and unsigned account keys so required signatures can be checked when building transactions |
| sdk/src/vote_program.rs | 409 | adds regression coverage for rejecting unsigned vote processing |

## Code Snippets

## Snippet 1

Context: `programs/native/vote/src/lib.rs:22` (changes a sensitive control or state-update path)

Before
```rust
trace!("keyed_accounts: {:?}", keyed_accounts);

    // all vote instructions require that accounts_keys[0] be a signer
    if keyed_accounts[0].signer_key().is_none() {
        error!("account[0] is unsigned");
        Err(ProgramError::InvalidArgument)?;
    }
```
After
```rust
trace!("keyed_accounts: {:?}", keyed_accounts);

    match deserialize(data).map_err(|_| ProgramError::InvalidUserdata)? {
        VoteInstruction::InitializeAccount => vote_program::initialize_account(keyed_accounts),
```

## Snippet 2

Context: `sdk/src/vote_program.rs:273` (changes a sensitive control or state-update path)

Before
```rust
}

    let mut vote_state = VoteState::deserialize(&keyed_accounts[0].account.userdata)?;
    vote_state.process_vote(vote);
```
After
```rust
}

    if keyed_accounts[0].signer_key().is_none() {
        error!("account[0] should sign the transaction");
        Err(ProgramError::InvalidArgument)?;
    }

    let mut vote_state = VoteState::deserialize(&keyed_accounts[0].account.userdata)?;
```

## Snippet 3

Context: `sdk/src/transaction_builder.rs:54` (changes a sensitive control or state-update path)

Before
```rust
/// Return pubkeys referenced by all instructions, with the ones needing signatures first.
    /// No duplicates and order is preserved.
    fn keys(&self) -> Vec<Pubkey> {
        let mut key_and_signed: Vec<_> = self
            .instructions
            .iter()
            .flat_map(|ix| ix.accounts.iter())
            .collect();
```
After
```rust
/// Return pubkeys referenced by all instructions, with the ones needing signatures first.
    /// No duplicates and order is preserved.
    fn keys(&self) -> (Vec<Pubkey>, Vec<Pubkey>) {
        let mut keys_and_signed: Vec<_> = self
            .instructions
            .iter()
            .flat_map(|ix| ix.accounts.iter())
            .collect();
```

## Snippet 4

Context: `sdk/src/vote_program.rs:409` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    #[test]
    fn test_vote_without_initialization() {
```
After
```rust
}

    #[test]
    fn test_vote_signature() {
        let from_id = Keypair::new().pubkey();
        let mut from_account = Account::new(100, 0, Pubkey::default());
        let vote_id = Keypair::new().pubkey();
        let mut vote_account = create_vote_account(100);
```

# Fix Pattern

Place authorization checks directly in the state-mutating function that requires them, while avoiding overbroad entrypoint assumptions for unrelated instruction variants.

## How It Was Fixed

The patch added a keyed_accounts[0].signer_key().is_none() guard inside process_vote before VoteState mutation, removed the blanket entrypoint-level signer check, and updated transaction-builder key handling to distinguish required signer keys from unsigned keys.

# Why It Matters

1. Keeps the vote mutation helper from relying solely on caller-enforced signer checks.

2. Allows instruction-specific signer requirements instead of one blanket entrypoint rule.

3. Improves transaction-construction diagnostics for missing signer keypairs.

4. Does not prove theft, reward manipulation, or consensus divergence from the supplied hunks.

# Evidence Notes

Grounded evidence includes removal of the blanket signer check in programs/native/vote/src/lib.rs, addition of a signer check in sdk/src/vote_program.rs::process_vote, transaction-builder changes separating signed and unsigned keys, and a test for unsigned vote processing. The evidence does not show the full call graph or demonstrate that the missing local check was exploitable through the normal native vote entrypoint. Protocol security invariant: Vote state mutation should require the vote account at keyed_accounts[0] to be owned by the vote program and to have signed when processing a Vote instruction. Verification notes: Does not prove that unsigned votes were accepted through the normal native vote entrypoint before this patch. Does not prove theft, stake redirection, or validator reward manipulation from the shown hunks alone. Does not show consensus divergence by itself; it shows authorization guard placement around vote state mutation. Transaction builder assertion is not a runtime protocol enforcement mechanism. No proof that unsigned votes were accepted through the standard entrypoint before the patch. No proof of stake theft, stake redirection, reward manipulation, or consensus divergence. Transaction builder changes should be treated as client-side hardening unless tied to runtime enforcement. Classified as unclear rather than confirmed or likely security fix because the vulnerability thesis is not established by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-signature-check`
Final impact type: `authorization-bypass, state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, vote-program, signature-check, authorization, security-hardening`

The supplied patch clearly moves signer enforcement into the vote state mutation path itself and adds a regression test for rejecting unsigned vote processing. The evidence does not prove an externally exploitable pre-patch bypass through the normal native entrypoint, because that entrypoint already had a blanket signer check, so this should not be treated as a confirmed security fix. It is still appropriate as security hardening because it tightens a signature/authorization invariant directly around a sensitive vote-state update and improves missing-signer handling in transaction construction.

## Security Evidence

1. process_vote now rejects keyed_accounts[0] when signer_key() is none before deserializing and mutating VoteState.
2. The removed entrypoint-level blanket signer check is replaced with instruction-specific signer enforcement for Vote processing.
3. A new test named test_vote_signature exercises unsigned process_vote behavior.
4. TransactionBuilder changes separate signed and unsigned keys, supporting detection of missing required signatures.

## Missing Evidence

1. No proof that unsigned votes reached process_vote through the standard native vote entrypoint before the patch.
2. No demonstrated exploit, consensus divergence, reward manipulation, or stake theft.
3. No full call graph proving process_vote was externally reachable without the old entrypoint guard.

## Claim Boundaries

1. Classify as security-hardening, not confirmed security-fix.
2. Limit the bug class to missing or misplaced signature authorization enforcement.
3. Do not claim concrete state corruption, fund loss, or consensus compromise from the supplied evidence.
4. Treat transaction-builder changes as supportive hardening rather than runtime protocol enforcement.
