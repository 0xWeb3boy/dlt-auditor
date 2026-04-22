---
case_id: case_20260218_0127d7834
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
bug_class: input-validation
impact_type:
  - correctness-or-hardening
confidence: low
source_quality: high
date: 2026-02-18
source_refs:
  - git:0127d7834702c97329214515e7539dd35a7388cb
  - "crates/client/metering/src/transaction.rs:61"
  - "crates/client/metering/src/meter.rs:181"
  - "crates/client/metering/src/transaction.rs:291"
  - "crates/client/metering/src/transaction.rs:137"
tags:
  - blockchain-core
  - transaction-processing
  - input-validation
  - eip-7702
  - signer-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch tightens local transaction validation in the client metering path for EIP-7702-related signer handling. Before, validation inferred the condition from account bytecode-hash metadata and whether the transaction itself was typed as 7702. After, the caller passes the sender's actual bytecode into `validate_tx`, and validation rejects signers whose present code is not EIP-7702 bytecode. The evidence supports a correctness and hardening change in this metering path, but it does not establish a demonstrated security vulnerability or broader consensus impact.

## Observed Patch Facts

1. In `crates/client/metering/src/transaction.rs`, the patch replaces `// error if account is 7702 but tx is not 7702` with `// If an account has bytecode, it MUST be EIP-7702 bytecode`.

2. In `crates/client/metering/src/meter.rs`, the patch replaces `let account = accounts` with `let (account, sender_code) = account_infos`.

3. In `crates/client/metering/src/transaction.rs`, the patch replaces `validate_tx(account, &recovered_tx, &mut l1_block_info),` with `validate_tx(account, Some(&contract_code), &recovered_tx, &mut l1_block_info),`.

4. In `crates/client/metering/src/transaction.rs`, the patch replaces `#[test]` with `fn create_signed_authorization(`.

## Project Context

The changed code sits primarily in `crates/client/metering/src`, `crates/client/metering`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/client/metering/src/rpc.rs`, `crates/client/metering/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/client/metering/src/rpc.rs`, `crates/client/metering/src/lib.rs`. The strongest project-level identifiers around this patch are `account`, `TxValidationError::AccountIs7702ButTxIsNot7702`, `TxValidationError::SignerAccountHasBytecode`, and `TxValidationError`.

## Before/After Behavior

Before the patch, `validate_tx` rejected a signer with non-empty bytecode only when `!txn.is_eip7702()`, using `account.bytecode_hash` as the signal. After the patch, the metering path passes `sender_code` into `validate_tx`, and the function rejects any present sender code that is not recognized as EIP-7702 bytecode with `SignerAccountHasBytecode`. Tests were updated to expect that stricter rejection and to add helper support for constructing signed 7702 authorization data.

# Root Cause

The validator was using incomplete information and a coarse proxy. It relied on account metadata (`bytecode_hash`) plus transaction type instead of inspecting the sender's actual bytecode, and the metering caller did not previously provide that bytecode to the validator.

## Walkthrough

1. `meter.rs` changed the validation call site from passing only `account` to passing `(account, sender_code)` from `account_infos`.

2. `validate_tx` was widened to accept `sender_code: Option<&Bytecode>`, which gives the validator direct access to the sender's code.

3. The old guard only rejected a non-empty-code account when the transaction was not 7702, using `account.bytecode_hash` as the signal.

4. The new guard rejects when sender code exists and `!bytecode.is_eip7702()`, regardless of transaction type alone.

5. The regression test was updated so a signer with ordinary contract bytecode now fails with `SignerAccountHasBytecode`.

6. A test helper for signed 7702 authorizations was added, supporting the intended valid case in tests.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/client/metering/src/transaction.rs | 43 | Primary transaction pre-validation logic; enforces the signer-account bytecode invariant before metering proceeds. |
| crates/client/metering/src/meter.rs | 175 | Bundle metering pipeline; now retrieves and forwards sender bytecode so validation can inspect actual code, not just account metadata. |
| crates/client/metering/src/transaction.rs | 269 | Regression test covering rejection of a signer account with ordinary contract bytecode. |
| crates/client/metering/src/transaction.rs | 135 | Test support for EIP-7702 authorization construction, indicating the intended valid path for 7702-capable senders. |

## Code Snippets

## Snippet 1

Context: `crates/client/metering/src/transaction.rs:61` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    // error if account is 7702 but tx is not 7702
    if account.bytecode_hash.is_some()
        && account.bytecode_hash.unwrap() != KECCAK_EMPTY
        && !txn.is_eip7702()
    {
        return Err(TxValidationError::AccountIs7702ButTxIsNot7702);
```
After
```rust
}

    // If an account has bytecode, it MUST be EIP-7702 bytecode
    if let Some(bytecode) = sender_code
        && !bytecode.is_eip7702()
    {
        return Err(TxValidationError::SignerAccountHasBytecode);
    }
```

## Snippet 2

Context: `crates/client/metering/src/meter.rs:181` (changes a sensitive control or state-update path)

Before
```rust
let value = tx.value();
            let gas_price = tx.max_fee_per_gas();
            let account = accounts
                .get(&from)
                .ok_or_else(|| eyre!("Account not found in HashMap for address: {}", from))?
                .ok_or_else(|| eyre!("Account is none for tx: {}", tx_hash))?;

            // Don't waste resources metering invalid transactions
```
After
```rust
let value = tx.value();
            let gas_price = tx.max_fee_per_gas();
            let (account, sender_code) = account_infos
                .get(&from)
                .ok_or_else(|| eyre!("Account not found in HashMap for address: {}", from))?;
            let account = account.ok_or_else(|| eyre!("Account is none for tx: {}", tx_hash))?;

            // Don't waste resources metering invalid transactions
```

## Snippet 3

Context: `crates/client/metering/src/transaction.rs:291` (changes a sensitive control or state-update path)

Before
```rust
assert_eq!(
            validate_tx(account, &recovered_tx, &mut l1_block_info),
            Err(TxValidationError::AccountIs7702ButTxIsNot7702)
        );
    }
```
After
```rust
assert_eq!(
            validate_tx(account, Some(&contract_code), &recovered_tx, &mut l1_block_info),
            Err(TxValidationError::SignerAccountHasBytecode)
        );
    }
```

## Snippet 4

Context: `crates/client/metering/src/transaction.rs:137` (changes an authorization or privilege gate)

Before
```rust
}

    #[test]
    fn test_valid_tx() {
        // Create a sample EIP-1559 transaction
        let signer = BaseAccount::Alice.signer();
```
After
```rust
}

    fn create_signed_authorization(
        chain_id: u64,
        contract_address: Address,
        nonce: u64,
        account: &BaseAccount,
    ) -> alloy_eips::eip7702::SignedAuthorization {
```

# Fix Pattern

Pass concrete execution-relevant state into validation and enforce the narrower invariant directly, instead of inferring it from indirect metadata.

## How It Was Fixed

The fix threads `sender_code` into `validate_tx`, replaces the old bytecode-hash-and-tx-type check with a direct `bytecode.is_eip7702()` check, and updates tests so ordinary contract bytecode is explicitly rejected while 7702 authorization setup is represented in test support.

# Why It Matters

1. It prevents this metering path from treating transaction type alone as sufficient when signer code is present.

2. It makes validation depend on the sender's actual bytecode rather than a weaker metadata proxy.

3. It reduces the chance that invalid code-bearing signers proceed farther into local metering work.

4. The provided evidence still does not show on-chain exploitation, privilege gain, or consensus impact.

# Evidence Notes

The strongest evidence is the `transaction.rs` hunk replacing the old `account.bytecode_hash` and `!txn.is_eip7702()` condition with a direct check on `sender_code` and `bytecode.is_eip7702()`. `meter.rs` shows this is a real data-flow change because the caller now retrieves `(account, sender_code)` from `account_infos` and passes `sender_code.as_ref()` into `validate_tx`. Test updates confirm the local behavioral change by changing the expected error to `SignerAccountHasBytecode` for a signer with ordinary contract bytecode. The added authorization helper supports tests for intended 7702 handling, but helper code alone is not evidence of a previously exploitable flaw. Protocol security invariant: In the client metering validation path, a sender with bytecode should only be accepted if the validator has the actual sender code available and that code is recognized as EIP-7702 bytecode; transaction type or a non-empty bytecode hash alone is not a sufficient proxy. Verification notes: The patch shows stricter validation in a metering/client path, not a demonstrated consensus-engine acceptance bug. It does not prove that invalid transactions were previously executed on chain; it only shows they could pass this local validation path farther than intended. The diff does not establish fund loss, privilege escalation, or state corruption. The patch does not by itself prove a practical denial-of-service condition, only that invalid transactions were not being filtered as strictly as intended. The evidence demonstrates a stricter local validation rule in the metering path. The evidence does not prove that invalid transactions were previously accepted on chain or executed successfully. The evidence does not establish fund loss, privilege escalation, state corruption, or a practical denial-of-service outcome. The updated tests cover the new rejection behavior for ordinary contract bytecode, but no end-to-end exploit or security impact is shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final tags: `blockchain-core, transaction-processing, input-validation, eip-7702, signer-validation, security-hardening`

The patch clearly tightens a security-sensitive transaction-validation rule: the metering path now passes the sender's actual bytecode into `validate_tx`, and validation rejects signers whose code is not EIP-7702 bytecode. That is stronger than the prior proxy check based on `bytecode_hash` plus transaction type, so the change is well-supported as security hardening. However, the diff does not prove a concrete exploitable bug, on-chain acceptance flaw, privilege escalation, or consensus impact, so this should not be upgraded to a confirmed security fix.

## Security Evidence

1. `validate_tx` now receives `sender_code` and checks the actual bytecode rather than only account metadata.
2. The new guard rejects any signer with present bytecode unless `bytecode.is_eip7702()` is true.
3. `meter.rs` was changed to retrieve and forward `(account, sender_code)` into validation, showing a real enforcement-path change.
4. The updated test now expects `SignerAccountHasBytecode` when a signer has ordinary contract bytecode.

## Missing Evidence

1. No evidence that previously accepted transactions could execute successfully on chain.
2. No proof of fund loss, privilege escalation, consensus divergence, or a practical denial-of-service outcome.
3. The patch does not show that this metering path is itself consensus-critical or externally exploitable.

## Claim Boundaries

1. Supported: the commit hardens signer validation for EIP-7702-related bytecode handling in the client metering path.
2. Supported: the old logic relied on an indirect proxy and the new logic enforces a stricter invariant using actual sender code.
3. Not supported: a confirmed exploitable vulnerability or concrete security incident.
4. Not supported: broad claims about consensus failure, authorization bypass, or chain-wide impact.
