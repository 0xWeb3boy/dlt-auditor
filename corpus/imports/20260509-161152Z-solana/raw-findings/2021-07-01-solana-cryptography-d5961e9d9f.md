---
case_id: case_20210701_d5961e9d9f
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2021-07-01
source_refs:
  - git:d5961e9d9f005966f409fbddd40c3651591b27fb
  - "client/src/rpc_custom_error.rs:155"
  - "rpc/src/rpc.rs:1900"
  - "ledger/src/entry.rs:529"
  - "client/src/rpc_custom_error.rs:53"
bug_class: transaction-signature-length-validation
impact_type:
  - malformed-transaction-acceptance
confidence: medium
tags:
  - blockchain-core
  - transaction-validation
  - signature-validation
  - security-hardening
  - rpc
  - ledger
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit `verify_signatures_len()` checks in RPC transaction verification and ledger entry transaction verification, and adds RPC error plumbing for signature length mismatch. The evidence supports a transaction validation/canonicality tightening for extra or mismatched signatures, but does not prove forgery, replay, double-spend, consensus divergence, or state corruption.

## Observed Patch Facts

1. In `client/src/rpc_custom_error.rs`, the patch adds `RpcCustomError::TransactionSignatureLenMismatch => Self {`.

2. In `rpc/src/rpc.rs`, the patch adds `if !transaction.verify_signatures_len() {`.

3. In `ledger/src/entry.rs`, the patch adds `if verify_tx_signatures_len && !tx.verify_signatures_len() {`.

4. In `client/src/rpc_custom_error.rs`, the patch adds `#[error("TransactionSignatureLenMismatch")]`.

## Project Context

The changed code sits primarily in `client/src`, `rpc/src`, `ledger/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `rpc/src/transaction_status_service.rs`, `rpc/src/send_transaction_service.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rpc/src/transaction_status_service.rs`, `rpc/src/send_transaction_service.rs`. The strongest project-level identifiers around this patch are `RpcCustomError::TransactionSignatureLenMismatch`, `ErrorCode::ServerError`, `None`, and `TransactionSignatureLenMismatch`.

## Before/After Behavior

Before the patch, the provided excerpts show RPC verification calling `transaction.verify()` and `transaction.verify_precompiles()` before returning success, and ledger entry verification proceeding to `tx.verify_and_hash_message()` without a visible explicit signature-length gate. After the patch, RPC rejects transactions for which `verify_signatures_len()` fails, and ledger entry verification returns `None` before hashing when `verify_tx_signatures_len` is enabled and the signature length check fails. Client RPC error handling was also extended for signature length mismatch.

# Root Cause

The patch indicates incomplete explicit enforcement of the transaction signature-vector length invariant in some verification paths. The supplied evidence does not show why the existing `transaction.verify()` path was insufficient or what security consequence resulted from accepting extra signatures.

## Walkthrough

1. A transaction reaches RPC-side `verify_transaction` in `rpc/src/rpc.rs`.

2. The pre-patch excerpt shows signature verification and precompile verification but no visible explicit signature-vector length check.

3. The patch adds `if !transaction.verify_signatures_len()` and returns a transaction signature verification failure on mismatch.

4. Ledger entry verification in `ledger/src/entry.rs` now also checks `verify_signatures_len()` before `verify_and_hash_message()` when the feature flag or control variable is enabled.

5. `client/src/rpc_custom_error.rs` adds and maps a signature-length mismatch error variant, which is supporting error-reporting code rather than the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rpc/src/rpc.rs | 1900 | RPC transaction verification now rejects transactions whose signature vector length is invalid before accepting the submitted transaction. |
| ledger/src/entry.rs | 529 | Ledger entry transaction verification now rejects invalid signature lengths before hashing verified transactions. |
| client/src/rpc_custom_error.rs | 53 | Adds a custom RPC error variant for transaction signature length mismatch. |
| client/src/rpc_custom_error.rs | 155 | Maps the new signature length mismatch condition into a JSON-RPC server error response. |

## Code Snippets

## Snippet 1

Context: `client/src/rpc_custom_error.rs:155` (changes signature or replay validation logic)

Before
```rust
data: None,
            },
        }
    }
```
After
```rust
data: None,
            },
            RpcCustomError::TransactionSignatureLenMismatch => Self {
                code: ErrorCode::ServerError(
                    JSON_RPC_SERVER_ERROR_TRANSACTION_SIGNATURE_LEN_MISMATCH,
                ),
                message: "Transaction signature length mismatch".to_string(),
                data: None,
```

## Snippet 2

Context: `rpc/src/rpc.rs:1900` (changes a sensitive control or state-update path)

Before
```rust
}

    Ok(())
}
```
After
```rust
}

    if !transaction.verify_signatures_len() {
        return Err(RpcCustomError::TransactionSignatureVerificationFailure.into());
    }

    Ok(())
}
```

## Snippet 3

Context: `ledger/src/entry.rs:529` (changes a sensitive control or state-update path)

Before
```rust
tx.verify_precompiles().ok()?;
                }
                tx.verify_and_hash_message().ok()?
            } else {
```
After
```rust
tx.verify_precompiles().ok()?;
                }
                if verify_tx_signatures_len && !tx.verify_signatures_len() {
                    return None;
                }
                tx.verify_and_hash_message().ok()?
            } else {
```

## Snippet 4

Context: `client/src/rpc_custom_error.rs:53` (changes a sensitive control or state-update path)

Before
```rust
#[error("ScanError")]
    ScanError { message: String },
}
```
After
```rust
#[error("ScanError")]
    ScanError { message: String },
    #[error("TransactionSignatureLenMismatch")]
    TransactionSignatureLenMismatch,
}
```

# Fix Pattern

Add explicit validation for transaction signature-vector length in transaction verification paths before accepting or hashing the transaction.

## How It Was Fixed

The patch added `verify_signatures_len()` checks in RPC and ledger entry verification. Transactions with mismatched or extra signatures are rejected in those paths. RPC custom error handling was updated to expose a signature length mismatch condition.

# Why It Matters

1. Rejects malformed or non-canonical transactions earlier.

2. Aligns RPC and ledger verification around signature-vector length validation.

3. Security impact beyond validation hardening is not established by the provided evidence.

# Evidence Notes

Grounded evidence is limited to added `verify_signatures_len()` checks in `rpc/src/rpc.rs:1900` and `ledger/src/entry.rs:529`, plus RPC error additions in `client/src/rpc_custom_error.rs`. The evidence does not include the implementation of `verify_signatures_len()`, the pre-existing behavior of `transaction.verify()`, tests demonstrating exploitability, or an explanation of security impact from extra signatures. Protocol security invariant: A transaction should not carry a signatures vector whose length is inconsistent with the transaction message's required signer set. The provided evidence shows new enforcement of this invariant, but does not establish an exploitable security impact. Verification notes: The patch does not prove that extra signatures allowed signature forgery. The patch does not prove replay or double-spend exploitability. The patch does not show a concrete consensus divergence scenario. The patch does not show state mutation before signature length validation in the provided evidence. The new RPC error mapping is supporting surface, not itself the security boundary. Do not claim signature forgery based on the provided evidence. Do not claim replay, double-spend, or consensus divergence based on the provided evidence. Treat the RPC error additions as support code, not the security boundary. Classification is downgraded from likely security-hardening to unclear because the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-signature-length-validation`
Final impact type: `malformed-transaction-acceptance`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-validation, signature-validation, security-hardening, rpc, ledger`

The supplied patch evidence supports a conservative security-hardening classification. It adds explicit transaction signature-length validation in RPC transaction verification and ledger entry verification, rejecting transactions with extra or mismatched signatures before acceptance or hashing. The evidence does not prove a concrete exploit such as forgery, replay, double-spend, consensus divergence, or state corruption, so it should not be treated as a confirmed security-fix.

## Security Evidence

1. Commit subject explicitly says transactions with extra signatures are rejected.
2. RPC verification now calls verify_signatures_len() and returns a signature verification failure on mismatch.
3. Ledger entry verification now rejects transactions failing verify_signatures_len() before verify_and_hash_message() when the check is enabled.
4. The changed behavior is in blockchain transaction verification paths involving signatures and ledger entry validation.

## Missing Evidence

1. No implementation of verify_signatures_len() is provided.
2. No tests or exploit scenario show that extra signatures enabled forgery, replay, double-spend, or consensus failure.
3. No evidence shows state mutation before the missing length validation.
4. No advisory or vulnerability explanation is included.

## Claim Boundaries

1. Classify as security-hardening, not a proven security-fix.
2. Do not claim signature forgery or replay from the provided evidence.
3. Do not claim consensus divergence or state corruption from the provided evidence.
4. RPC custom error additions are supporting plumbing, not the security boundary itself.
