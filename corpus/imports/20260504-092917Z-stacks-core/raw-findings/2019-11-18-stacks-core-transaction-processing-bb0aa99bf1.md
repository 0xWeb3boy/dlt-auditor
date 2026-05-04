---
case_id: case_20191118_bb0aa99bf1
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2019-11-18
source_refs:
  - git:bb0aa99bf1b83077f14555755c94af525dcab081
  - "src/chainstate/stacks/db/transactions.rs:391"
  - "src/chainstate/stacks/db/transactions.rs:152"
  - "src/chainstate/stacks/db/transactions.rs:186"
  - "src/chainstate/stacks/db/transactions.rs:165"
bug_class: transaction-validation-hardening
impact_type:
  - transaction-integrity
  - authorization-validation
confidence: medium
tags:
  - transaction-processing
  - postconditions
  - authorization-mode
  - sponsored-transactions
  - fail-closed-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes transaction postcondition asset lookups from origin_account.principal to account.principal for STX, fungible-token, and non-fungible-token checks, and adds a guard that rejects sponsored token-transfer transactions before token-transfer processing. This is plausibly security-relevant validation logic, but the supplied evidence does not prove exploitability, consensus impact, loss of funds, or that the previous behavior was reachable in an unsafe way.

## Observed Patch Facts

1. In `src/chainstate/stacks/db/transactions.rs`, the patch replaces `StacksChainState::process_transaction_token_transfer(clarity_tx,tx, origin_account)?;` with `// this only works for standard authorizations`.

2. In `src/chainstate/stacks/db/transactions.rs`, the patch replaces `let amount_sent = asset_map.get_stx(&origin_account.principal).unwrap_or(0);` with `let amount_sent = asset_map.get_stx(&account.principal).unwrap_or(0);`.

3. In `src/chainstate/stacks/db/transactions.rs`, the patch replaces `let assets_sent = asset_map.get_nonfungible_tokens(&origin_account.principal, &asset_...` with `let assets_sent = asset_map.get_nonfungible_tokens(&account.principal, &asset_id).unw...`.

4. In `src/chainstate/stacks/db/transactions.rs`, the patch replaces `let amount_sent = asset_map.get_fungible_tokens(&origin_account.principal, &asset_id)...` with `let amount_sent = asset_map.get_fungible_tokens(&account.principal, &asset_id).unwrap...`.

## Project Context

The changed code sits primarily in `src/chainstate/stacks/db`, `src/chainstate/stacks`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/chainstate/stacks/db/mod.rs`, `src/chainstate/stacks/db/headers.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/chainstate/stacks/transaction.rs`, `src/chainstate/stacks/mod.rs`. The strongest project-level identifiers around this patch are `condition_code`, `amount_sent`, `check`, and `asset_id`.

## Before/After Behavior

Before the patch, the shown postcondition checks queried asset_map using origin_account.principal and logged origin_account on failure. After the patch, they query and log account.principal. Before the patch, token-transfer payload processing directly called process_transaction_token_transfer. After the patch, it first rejects transactions with tx.auth.sponsor().is_some() using Error::InvalidStacksTransaction and the message "Sponsored transactions cannot transfer tokens".

# Root Cause

The grounded issue is a mismatch between the account parameter passed to check_transaction_postconditions and the principal used for asset_map lookups. The evidence also shows the token-transfer path lacked an explicit sponsored-authorization rejection, but does not prove that this omission caused a security vulnerability.

## Walkthrough

1. check_transaction_postconditions receives tx, account, and asset_map.

2. The STX postcondition lookup changed from asset_map.get_stx(&origin_account.principal) to asset_map.get_stx(&account.principal).

3. The fungible-token postcondition lookup changed from asset_map.get_fungible_tokens(&origin_account.principal, &asset_id) to asset_map.get_fungible_tokens(&account.principal, &asset_id).

4. The non-fungible-token postcondition lookup changed from asset_map.get_nonfungible_tokens(&origin_account.principal, &asset_id) to asset_map.get_nonfungible_tokens(&account.principal, &asset_id).

5. The failure debug messages were updated to report account instead of origin_account.

6. The TransactionPayload::TokenTransfer branch now checks tx.auth.sponsor().is_some() before calling process_transaction_token_transfer.

7. If a sponsor is present, the patched code returns Error::InvalidStacksTransaction instead of continuing.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/chainstate/stacks/db/transactions.rs | 146 | transaction postcondition validation entry point; evaluates STX, fungible, and non-fungible asset conditions against the transaction account |
| src/chainstate/stacks/db/transactions.rs | 152 | STX postcondition amount lookup changed from origin_account principal to account principal |
| src/chainstate/stacks/db/transactions.rs | 165 | fungible-token postcondition amount lookup changed from origin_account principal to account principal |
| src/chainstate/stacks/db/transactions.rs | 186 | non-fungible-token postcondition lookup changed from origin_account principal to account principal |
| src/chainstate/stacks/db/transactions.rs | 391 | payload processing now rejects sponsored token-transfer transactions before executing the token-transfer path |

## Code Snippets

## Snippet 1

Context: `src/chainstate/stacks/db/transactions.rs:391` (changes an authorization or privilege gate)

Before
```rust
let stx_burned = match tx.payload {
            TransactionPayload::TokenTransfer(_) => {
                StacksChainState::process_transaction_token_transfer(clarity_tx,tx, origin_account)?;
```
After
```rust
let stx_burned = match tx.payload {
            TransactionPayload::TokenTransfer(_) => {
                // this only works for standard authorizations
                if tx.auth.sponsor().is_some() {
                    let msg = "Sponsored transactions cannot transfer tokens".to_string();
                    warn!("{}", &msg);

                    return Err(Error::InvalidStacksTransaction(msg));
```

## Snippet 2

Context: `src/chainstate/stacks/db/transactions.rs:152` (changes a sensitive control or state-update path)

Before
```rust
match postcond {
                TransactionPostCondition::STX(ref condition_code, ref amount_sent_condition) => {
                    let amount_sent = asset_map.get_stx(&origin_account.principal).unwrap_or(0);
                    if !condition_code.check(*amount_sent_condition as i128, amount_sent) {
                        debug!("Post-condition check failure on STX owned by {:?}: {:?} {:?} {}", origin_account, amount_sent_condition, condition_code, amount_sent);
                        return false;
                    }
```
After
```rust
match postcond {
                TransactionPostCondition::STX(ref condition_code, ref amount_sent_condition) => {
                    let amount_sent = asset_map.get_stx(&account.principal).unwrap_or(0);
                    if !condition_code.check(*amount_sent_condition as i128, amount_sent) {
                        debug!("Post-condition check failure on STX owned by {:?}: {:?} {:?} {}", account, amount_sent_condition, condition_code, amount_sent);
                        return false;
                    }
```

## Snippet 3

Context: `src/chainstate/stacks/db/transactions.rs:186` (changes a sensitive control or state-update path)

Before
```rust
let empty_assets = vec![];
                    let assets_sent = asset_map.get_nonfungible_tokens(&origin_account.principal, &asset_id).unwrap_or(&empty_assets);
                    if !condition_code.check(&asset_sent_condition, assets_sent) {
                        debug!("Post-condition check failure on non-fungible asset {:?} owned by {:?}: {:?} {:?}", &asset_id, origin_account, &asset_sent_condition, condition_code);
                        return false;
                    }
```
After
```rust
let empty_assets = vec![];
                    let assets_sent = asset_map.get_nonfungible_tokens(&account.principal, &asset_id).unwrap_or(&empty_assets);
                    if !condition_code.check(&asset_sent_condition, assets_sent) {
                        debug!("Post-condition check failure on non-fungible asset {:?} owned by {:?}: {:?} {:?}", &asset_id, account, &asset_sent_condition, condition_code);
                        return false;
                    }
```

## Snippet 4

Context: `src/chainstate/stacks/db/transactions.rs:165` (changes a sensitive control or state-update path)

Before
```rust
};

                    let amount_sent = asset_map.get_fungible_tokens(&origin_account.principal, &asset_id).unwrap_or(0);
                    if !condition_code.check(*amount_sent_condition as i128, amount_sent) {
                        debug!("Post-condition check failure on fungible asset {:?} owned by {:?}: {:?} {:?} {}", &asset_id, origin_account, amount_sent_condition, condition_code, amount_sent);
                        return false;
                    }
```
After
```rust
};

                    let amount_sent = asset_map.get_fungible_tokens(&account.principal, &asset_id).unwrap_or(0);
                    if !condition_code.check(*amount_sent_condition as i128, amount_sent) {
                        debug!("Post-condition check failure on fungible asset {:?} owned by {:?}: {:?} {:?} {}", &asset_id, account, amount_sent_condition, condition_code, amount_sent);
                        return false;
                    }
```

# Fix Pattern

Align validation lookups with the account parameter being checked, and fail closed for an authorization mode that the token-transfer path comments say is unsupported.

## How It Was Fixed

The patch replaced origin_account.principal with account.principal in the STX, fungible-token, and non-fungible-token postcondition asset_map lookups. It also added an early sponsored-transaction rejection in the token-transfer payload branch.

# Why It Matters

1. Touches transaction validation logic.

2. Changes which principal is used for postcondition accounting.

3. Adds an explicit validity guard for sponsored token transfers.

4. Security impact is not established by the supplied evidence.

# Evidence Notes

Evidence is limited to changed hunks in src/chainstate/stacks/db/transactions.rs around postcondition checks and token-transfer payload processing. The commit subject says "a little bit of refactoring; fix unit test," which does not support a security-fix conclusion. No call-site evidence, failing test, exploit scenario, peer acceptance behavior, or consensus effect is provided. Protocol security invariant: Transaction postcondition checks should be evaluated against the intended account principal, and transaction authorization modes unsupported by a processing path should be rejected before that path runs. The provided evidence shows code moving in that direction, but does not establish a concrete vulnerability or exploit path. Verification notes: The patch does not by itself prove a practical exploit or loss of funds. The patch does not show whether malformed transactions could be mined or accepted by all peers before the fix. The patch does not prove consensus divergence, only a transaction-validation/accounting invariant change. The commit subject frames the change as refactoring and unit-test repair, so the security classification is based on code behavior, not author intent. Confirmed by provided diff snippets only; no independent file inspection was performed. Do not treat as confirmed security fix without call-site or test evidence showing unsafe pre-patch behavior. Helper or unrelated files are not implicated as root cause by the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-validation-hardening`
Final impact type: `transaction-integrity, authorization-validation`
Final confidence: `medium`
Final tags: `transaction-processing, postconditions, authorization-mode, sponsored-transactions, fail-closed-validation`

The supplied patch evidence does not prove a concrete exploitable vulnerability, loss of funds, or consensus impact, so it should not be treated as a confirmed security-fix. However, it does clearly tighten security-sensitive transaction validation: postcondition accounting is changed to use the account being checked, and sponsored token transfers are rejected before entering a path explicitly documented as only working for standard authorization. That supports retaining it as security-hardening with conservative metadata.

## Security Evidence

1. Transaction payload processing now rejects sponsored token-transfer transactions with InvalidStacksTransaction before executing token-transfer logic.
2. The added comment states the token-transfer path only works for standard authorizations, supporting a fail-closed validation interpretation.
3. Postcondition checks for STX, fungible tokens, and non-fungible tokens now query asset_map using account.principal instead of origin_account.principal.
4. The changed code is in transaction-processing validation paths for asset postconditions and authorization mode handling.

## Missing Evidence

1. No exploit scenario or concrete unsafe transaction example is provided.
2. No failing test or call-site evidence shows that the pre-patch behavior was reachable in production validation.
3. No evidence establishes fund loss, consensus divergence, or acceptance of invalid blocks/transactions.
4. The commit subject frames the change as refactoring and unit-test repair rather than a security fix.

## Claim Boundaries

1. Classify as security-hardening, not a confirmed security-fix.
2. Do not claim proven state corruption, loss of funds, or consensus failure from the supplied evidence alone.
3. Do not rely on multisig or signature-specific claims beyond the shown sponsored-authorization guard.
4. The supported claim is limited to stricter transaction validation and corrected postcondition principal accounting.
