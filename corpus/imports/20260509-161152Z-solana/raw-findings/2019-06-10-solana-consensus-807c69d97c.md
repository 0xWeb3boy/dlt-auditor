---
case_id: case_20190610_807c69d97c
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: medium
date: 2019-06-10
source_refs:
  - git:807c69d97cc2949961b2a4214251dc4dd8104406
  - "runtime/src/accounts.rs:553"
  - "runtime/src/accounts.rs:570"
  - "runtime/src/message_processor.rs:73"
  - "runtime/src/message_processor.rs:84"
bug_class: account-permission-invariant-hardening
impact_type:
  - runtime-authorization-hardening
  - account-state-integrity
confidence: medium
tags:
  - runtime
  - accounts
  - credit-only-accounts
  - authorization
  - state-integrity
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit verification checks for non-debitable credit-only accounts and updates account storage to carry lamport-credit metadata. This is plausibly security relevant because it concerns runtime account authorization semantics, but the provided evidence does not establish a concrete vulnerability, exploit path, or production impact. It may be part of safely implementing or refactoring the credit-only account model.

## Observed Patch Facts

1. In `runtime/src/accounts.rs`, the patch replaces `loaded: &[Result<(InstructionAccounts, InstructionLoaders)>],` with `loaded: &[Result<(InstructionAccounts, InstructionLoaders, InstructionCredits)>],`.

2. In `runtime/src/accounts.rs`, the patch replaces `#[cfg(test)]` with `fn collect_accounts<'a>(`.

3. In `runtime/src/message_processor.rs`, the patch adds `// The balance of credit-only accounts may only increase`.

4. In `runtime/src/message_processor.rs`, the patch adds `// Credit-only account data may not change.`.

## Project Context

The changed code sits primarily in `runtime/src`, which anchors the finding in the `consensus` area of the project. Historical context from `runtime/src/locked_accounts_results.rs`, `runtime/src/accounts_db.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank.rs`, `runtime/src/system_instruction_processor.rs`. The strongest project-level identifiers around this patch are `accounts`, `Result`, `loaded`, and `account`.

## Before/After Behavior

Before the patch, the visible `verify_instruction` checks covered owner changes, external lamport spend for accounts not owned by the program, and external data modification. The evidence does not show a dedicated credit-only check. After the patch, `verify_instruction` rejects lamport decreases on non-debitable accounts with `CreditOnlyLamportSpend` and rejects data changes on non-debitable accounts with `CreditOnlyDataModified`. The storage path also changes from collecting account references alone to passing account state with `LamportCredit` metadata through `collect_accounts` into `accounts_db.store`.

# Root Cause

The evidence supports that the previous code lacked explicit post-instruction checks for the credit-only/non-debitable account permission class in the shown path. It does not prove that this omission was exploitable, only that the patch made the invariant explicit and propagated related credit metadata through storage.

## Walkthrough

1. Instructions execute against loaded accounts, including accounts that may be non-debitable or credit-only.

2. After execution, `verify_instruction` compares pre-instruction lamports and data against the resulting account state.

3. The patch adds a rejection when a non-debitable account's lamports decrease.

4. The patch adds a rejection when a non-debitable account's data changes.

5. The account persistence path now receives `InstructionCredits` with loaded accounts and loaders.

6. `collect_accounts` builds a mapping from account pubkey to account state plus `LamportCredit` for storage.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/message_processor.rs | 73 | post-instruction authorization check preventing lamport decreases on credit-only accounts |
| runtime/src/message_processor.rs | 84 | post-instruction authorization check preventing data changes on credit-only accounts |
| runtime/src/accounts.rs | 553 | store_accounts now receives loaded account credits for persistence |
| runtime/src/accounts.rs | 570 | collect_accounts builds account-to-credit mapping before accounts_db storage |

## Code Snippets

## Snippet 1

Context: `runtime/src/accounts.rs:553` (changes the branch that decides whether execution stops or continues)

Before
```rust
txs: &[Transaction],
        res: &[Result<()>],
        loaded: &[Result<(InstructionAccounts, InstructionLoaders)>],
    ) {
        let mut accounts: Vec<(&Pubkey, &Account)> = vec![];
        for (i, raccs) in loaded.iter().enumerate() {
            if res[i].is_err() || raccs.is_err() {
                continue;
```
After
```rust
txs: &[Transaction],
        res: &[Result<()>],
        loaded: &[Result<(InstructionAccounts, InstructionLoaders, InstructionCredits)>],
    ) {
        let accounts = collect_accounts(txs, res, loaded);
        self.accounts_db.store(fork, &accounts);
    }
```

## Snippet 2

Context: `runtime/src/accounts.rs:570` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

#[cfg(test)]
mod tests {
```
After
```rust
}

fn collect_accounts<'a>(
    txs: &'a [Transaction],
    res: &'a [Result<()>],
    loaded: &'a [Result<(InstructionAccounts, InstructionLoaders, InstructionCredits)>],
) -> HashMap<&'a Pubkey, (&'a Account, LamportCredit)> {
    let mut accounts: HashMap<&Pubkey, (&Account, LamportCredit)> = HashMap::new();
```

## Snippet 3

Context: `runtime/src/message_processor.rs:73` (changes aggregate state or economic accounting)

Before
```rust
return Err(InstructionError::ExternalAccountLamportSpend);
    }
    // For accounts unassigned to the program, the data may not change.
    if *program_id != account.owner
```
After
```rust
return Err(InstructionError::ExternalAccountLamportSpend);
    }
    // The balance of credit-only accounts may only increase
    if !is_debitable && pre_lamports > account.lamports {
        return Err(InstructionError::CreditOnlyLamportSpend);
    }
    // For accounts unassigned to the program, the data may not change.
    if *program_id != account.owner
```

## Snippet 4

Context: `runtime/src/message_processor.rs:84` (changes a sensitive control or state-update path)

Before
```rust
return Err(InstructionError::ExternalAccountDataModified);
    }
    Ok(())
}
```
After
```rust
return Err(InstructionError::ExternalAccountDataModified);
    }
    // Credit-only account data may not change.
    if !is_debitable && pre_data != &account.data[..] {
        return Err(InstructionError::CreditOnlyDataModified);
    }
    Ok(())
}
```

# Fix Pattern

Add explicit invariant checks for a special account permission class and propagate the corresponding credit metadata through the storage boundary.

## How It Was Fixed

`runtime/src/message_processor.rs::verify_instruction` now rejects lamport decreases and data changes for non-debitable accounts. `runtime/src/accounts.rs::store_accounts` now accepts loaded results containing `InstructionCredits`, delegates to `collect_accounts`, and passes account state plus `LamportCredit` metadata to `accounts_db.store`.

# Why It Matters

1. Touches runtime account authorization semantics.

2. Makes credit-only account restrictions explicit after instruction execution.

3. Aligns account persistence with credit-only lamport-credit metadata.

4. Exploitability and concrete security impact are not established by the supplied evidence.

# Evidence Notes

Strongest evidence is the added `CreditOnlyLamportSpend` and `CreditOnlyDataModified` checks in `runtime/src/message_processor.rs`. Supporting evidence is the storage-path change in `runtime/src/accounts.rs` carrying `InstructionCredits` and `LamportCredit`. The evidence does not show arbitrary account modification, theft, consensus divergence, replay behavior, or a concrete malicious transaction scenario. Protocol security invariant: Accounts treated as non-debitable or credit-only should not lose lamports or have account data changed; only permitted credit effects should be carried into account storage. Verification notes: No concrete exploit path is shown by the provided patch evidence. No proof is shown that a malicious program could previously debit or modify arbitrary credit-only accounts in production. No cryptographic or replay invariant is directly evidenced despite heuristic flags. The change may be hardening for a new relaxed-lock credit-only design rather than remediation of a known vulnerability. Consensus impact is plausible because runtime account state is affected, but divergence or theft is not proven from the patch alone. No concrete exploit path is provided. No production impact is demonstrated. No cryptographic or replay invariant is evidenced. Treat as unclear security relevance rather than a confirmed or likely vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `account-permission-invariant-hardening`
Final impact type: `runtime-authorization-hardening, account-state-integrity`
Final confidence: `medium`
Final tags: `runtime, accounts, credit-only-accounts, authorization, state-integrity, hardening`

The patch evidence supports retaining this as security hardening. It adds explicit post-instruction enforcement that non-debitable credit-only accounts cannot lose lamports or have data modified, which is a security-sensitive account authorization invariant in the runtime. The evidence does not prove a concrete exploitable vulnerability or production impact, so it should not be classified as a confirmed security fix.

## Security Evidence

1. verify_instruction now rejects lamport decreases when is_debitable is false via CreditOnlyLamportSpend.
2. verify_instruction now rejects data changes when is_debitable is false via CreditOnlyDataModified.
3. The checks are in runtime account verification after instruction execution, a sensitive state-transition path.
4. Storage changes propagate InstructionCredits and LamportCredit metadata, aligning persistence with the credit-only account model.

## Missing Evidence

1. No concrete malicious transaction or exploit path is shown.
2. No proof that arbitrary account theft or unauthorized mutation was possible in production is provided.
3. No demonstrated consensus divergence, replay issue, or cryptographic invariant violation is evidenced.
4. Commit wording suggests implementation/refinement of credit-only accounts rather than an explicit vulnerability remediation.

## Claim Boundaries

1. Classify as hardening, not a confirmed vulnerability fix.
2. Do not claim proven theft, arbitrary account modification, or consensus failure from this evidence alone.
3. The validated claim is limited to tightening credit-only/non-debitable account state invariants.
4. Security relevance rests on runtime authorization semantics, not on documented exploitability.
