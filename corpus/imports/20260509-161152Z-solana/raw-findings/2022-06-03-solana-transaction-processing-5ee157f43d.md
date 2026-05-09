---
case_id: case_20220603_5ee157f43d
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2022-06-03
source_refs:
  - git:5ee157f43d86d4a70b5117c9e66246f65b177d90
  - "cli/src/nonce.rs:334"
  - "runtime/src/bank.rs:13204"
  - "runtime/src/bank.rs:12353"
  - "cli/src/nonce.rs:599"
bug_class: replay-domain-collision
impact_type:
  - transaction-replay
  - double-execution
tags:
  - infrastructure
  - transaction-processing
  - durable-nonce
  - blockhash-domain-separation
  - replay-protection
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The commit fixes a replay-domain collision between Solana durable nonce values and normal blockhashes. The commit message explicitly states that AdvanceNonceAccount could update a nonce to a raw blockhash, allowing a durable transaction to be executed both as a normal transaction and as a nonce transaction when that blockhash was used as recent_blockhash. The patch separates the domains and updates observed runtime and CLI nonce consumers to use the nonce accessor instead of direct blockhash field access.

## Observed Patch Facts

1. In `cli/src/nonce.rs`, the patch replaces `if &data.blockhash != nonce_hash {` with `if &data.blockhash() != nonce_hash {`.

2. In `runtime/src/bank.rs`, the patch replaces `// Caught by the system program because the tx hash is valid` with `// SanitizedMessage::get_durable_nonce returns None because nonce`.

3. In `runtime/src/bank.rs`, the patch replaces `Ok(nonce::State::Initialized(ref data)) => Some(data.blockhash),` with `Ok(nonce::State::Initialized(ref data)) => Some(data.blockhash()),`.

4. In `cli/src/nonce.rs`, the patch replaces `nonce_account.nonce = Some(data.blockhash.to_string());` with `nonce_account.nonce = Some(data.blockhash().to_string());`.

## Project Context

The changed code sits primarily in `cli/src`, `runtime/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `runtime/src/system_instruction_processor.rs`, `runtime/src/nonce_keyed_account.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/system_instruction_processor.rs`, `runtime/src/accounts.rs`. The strongest project-level identifiers around this patch are `data`, `blockhash`, `nonce`, and `Some`.

## Before/After Behavior

Before the change, observed code read nonce account data through data.blockhash, so the durable nonce value could coincide with a normal blockhash. After the change, observed call sites use data.blockhash(), and the regression test expects BlockhashNotFound when a read-only nonce account is not recognized as a durable nonce and the domain-separated nonce is absent from the normal blockhash queue.

# Root Cause

AdvanceNonceAccount used or exposed nonce values in the same value domain as normal recent blockhashes, violating replay-domain separation between normal transactions and durable nonce transactions.

## Walkthrough

1. A nonce account stores a value later used as a transaction recent_blockhash for durable nonce processing.

2. Before the fix, observed runtime and CLI code paths accessed the stored value directly as data.blockhash.

3. The commit message states that this allowed a transaction using that blockhash as recent_blockhash to be executed once as a normal transaction and again as a durable nonce transaction.

4. The patch separates nonce and blockhash domains by hashing the blockhash with a fixed string when advancing the nonce account, according to the commit message.

5. Observed consumers in cli/src/nonce.rs and runtime/src/bank.rs are updated to call data.blockhash(), aligning validation, display, and test helper behavior with the separated nonce value.

6. The updated runtime test documents that when durable nonce detection fails because the nonce account is read-only, the transaction is rejected as BlockhashNotFound rather than proceeding on the normal blockhash path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/program/src/nonce/state/current.rs | 1 | nonce state representation/accessor; commit context indicates nonce blockhash is domain-separated here |
| runtime/src/nonce_keyed_account.rs | 1 | AdvanceNonceAccount execution path that updates nonce account state |
| runtime/src/bank.rs | 12350 | bank test helper reads initialized nonce account value via domain-separated data.blockhash() |
| runtime/src/bank.rs | 13176 | regression test for transaction processing when durable nonce detection fails and separated nonce is not in blockhash queue |
| cli/src/nonce.rs | 329 | client-side nonce account validation compares provided nonce hash against domain-separated account nonce |
| cli/src/nonce.rs | 584 | CLI nonce display reports the domain-separated nonce value |

## Code Snippets

## Snippet 1

Context: `cli/src/nonce.rs:334` (changes a sensitive control or state-update path)

Before
```rust
match state_from_account(nonce_account)? {
        State::Initialized(ref data) => {
            if &data.blockhash != nonce_hash {
                Err(Error::InvalidHash {
                    provided: *nonce_hash,
                    expected: data.blockhash,
                }
                .into())
```
After
```rust
match state_from_account(nonce_account)? {
        State::Initialized(ref data) => {
            if &data.blockhash() != nonce_hash {
                Err(Error::InvalidHash {
                    provided: *nonce_hash,
                    expected: data.blockhash(),
                }
                .into())
```

## Snippet 2

Context: `runtime/src/bank.rs:13204` (changes a sensitive control or state-update path)

Before
```rust
nonce_hash,
        );
        // Caught by the system program because the tx hash is valid
        assert_eq!(
            bank.process_transaction(&tx),
            Err(TransactionError::InstructionError(
                0,
                InstructionError::InvalidArgument
```
After
```rust
nonce_hash,
        );
        // SanitizedMessage::get_durable_nonce returns None because nonce
        // account is not writable. Durable nonce and blockhash domains are
        // separate, so the recent_blockhash (== durable nonce) in the
        // transaction is not found in the hash queue.
        assert_eq!(
            bank.process_transaction(&tx),
```

## Snippet 3

Context: `runtime/src/bank.rs:12353` (changes signature or replay validation logic)

Before
```rust
StateMut::<nonce::state::Versions>::state(&acc).map(|v| v.convert_to_current());
            match state {
                Ok(nonce::State::Initialized(ref data)) => Some(data.blockhash),
                _ => None,
            }
```
After
```rust
StateMut::<nonce::state::Versions>::state(&acc).map(|v| v.convert_to_current());
            match state {
                Ok(nonce::State::Initialized(ref data)) => Some(data.blockhash()),
                _ => None,
            }
```

## Snippet 4

Context: `cli/src/nonce.rs:599` (changes signature or replay validation logic)

Before
```rust
};
        if let Some(data) = data {
            nonce_account.nonce = Some(data.blockhash.to_string());
            nonce_account.lamports_per_signature = Some(data.fee_calculator.lamports_per_signature);
            nonce_account.authority = Some(data.authority.to_string());
```
After
```rust
};
        if let Some(data) = data {
            nonce_account.nonce = Some(data.blockhash().to_string());
            nonce_account.lamports_per_signature = Some(data.fee_calculator.lamports_per_signature);
            nonce_account.authority = Some(data.authority.to_string());
```

# Fix Pattern

Domain-separate replay identifiers used by distinct transaction acceptance paths, then update nonce readers to consume the domain-separated nonce value rather than the raw stored blockhash field.

## How It Was Fixed

The patch changes observed nonce consumers from direct data.blockhash field access to data.blockhash(). The commit message states that AdvanceNonceAccount now hashes the blockhash with a fixed string so a blockhash cannot also be a valid nonce value. The bank regression test was updated to assert BlockhashNotFound for a case where the recent_blockhash equals the durable nonce but the nonce account is read-only.

# Why It Matters

1. Preserves one-execution replay semantics across normal and durable nonce paths.

2. Prevents a blockhash from also serving as a valid durable nonce value.

3. Keeps CLI nonce validation and display consistent with runtime nonce semantics.

4. The evidence supports replay prevention, not broader claims such as account takeover or arbitrary fund theft.

# Evidence Notes

Strongest evidence is the commit body, which explicitly describes double execution and the domain-separation fix. The provided hunks show supporting call-site changes from data.blockhash to data.blockhash() and a regression test expectation changing to BlockhashNotFound. The accessor implementation itself is not shown in the provided hunks, so claims about its internals should rely on the commit message rather than direct code evidence. Protocol security invariant: A transaction recent_blockhash value must not be valid in both the normal recent-blockhash queue and the durable-nonce path; otherwise the same signed transaction can cross replay domains and be accepted more than once. Verification notes: The patch evidence does not prove arbitrary fund theft or account takeover. The patch evidence does not quantify economic impact from double execution. The CLI changes are supporting consistency; consensus enforcement is in runtime/nonce transaction processing. The provided hunks do not show the full implementation of the fixed-string hashing accessor, only its use and commit description. The patch supports replay prevention across normal and durable nonce domains, not a broader signature verification flaw. Commit message directly states the vulnerability condition and intended prevention. Runtime test change supports separation between durable nonce and normal blockhash handling. CLI changes appear to be consistency updates, not the root enforcement point. No evidence supports claims beyond nonce/blockhash replay-domain collision. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `replay-domain-collision`
Final impact type: `transaction-replay, double-execution`
Final tags: `infrastructure, transaction-processing, durable-nonce, blockhash-domain-separation, replay-protection`

The supplied commit message explicitly describes a replay-domain collision where a durable transaction could be executed twice, once as a normal transaction and once as a nonce transaction. The provided patch evidence supports this by showing nonce consumers moved from raw blockhash field access to a nonce accessor and a runtime regression expectation changing to BlockhashNotFound when the separated durable nonce is not in the normal blockhash queue. This is security-relevant replay prevention, though the original input-validation classification is too generic.

## Security Evidence

1. Commit body states durable nonce and blockhash shared a domain could permit double execution.
2. Commit body states the fix separates nonce and blockhash domains by hashing blockhash with a fixed string.
3. Runtime test comment says durable nonce and blockhash domains are separate and expects BlockhashNotFound.
4. Runtime and CLI call sites now use data.blockhash() instead of directly reading data.blockhash.

## Missing Evidence

1. Provided hunks do not show the accessor implementation that performs fixed-string hashing.
2. Provided evidence does not quantify economic impact or prove arbitrary fund theft.
3. Provided evidence does not show full transaction acceptance logic before and after the fix.

## Claim Boundaries

1. Supports a transaction replay or double-execution fix across normal blockhash and durable nonce paths.
2. Does not support broader claims such as account takeover, signature forgery, or arbitrary fund theft.
3. CLI changes are supporting consistency; the security-relevant behavior is transaction processing and nonce domain separation.
