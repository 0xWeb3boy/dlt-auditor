---
case_id: case_20221221_bd9fbd18d3
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: high
date: 2022-12-21
source_refs:
  - git:bd9fbd18d32619ca1dca248a0b70cc9f706508dd
  - "crates/sui-core/src/authority_server.rs:350"
  - "crates/sui-core/src/authority/authority_per_epoch_store.rs:431"
  - "crates/sui-core/src/authority/authority_per_epoch_store.rs:420"
  - "crates/sui-core/src/authority/authority_per_epoch_store.rs:5"
bug_class: epoch-boundary-reconfiguration-race
impact_type:
  - consensus-invariant-hardening
tags:
  - blockchain-core
  - consensus
  - validator
  - reconfiguration
  - epoch-boundary
  - race-condition
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch makes Sui validator certificate handling acquire and check the per-epoch reconfiguration read lock earlier, before certificate verification and later pending-consensus storage. It also changes pending consensus insertion to require a ReconfigState read-lock guard for user transactions and assert that user certificates are still accepted. The evidence supports a consensus/reconfiguration invariant hardening or likely security fix, but does not prove a practical exploit, consensus divergence, double execution, or fund loss.

## Observed Patch Facts

1. In `crates/sui-core/src/authority_server.rs`, the patch replaces `let cert_verif_metrics_guard = metrics.cert_verification_latency.start_timer();` with `// code block within reconfiguration lock`.

2. In `crates/sui-core/src/authority/authority_per_epoch_store.rs`, the patch replaces `self.pending_consensus_certificates` with `let state = lock.expect("Must pass reconfiguration lock when storing certificate");`.

3. In `crates/sui-core/src/authority/authority_per_epoch_store.rs`, the patch replaces `) -> SuiResult {` with `/// When submitting a certificate caller **must** provide a ReconfigState lock guard`.

4. In `crates/sui-core/src/authority/authority_per_epoch_store.rs`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, `crates/sui-core/src/authority`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/sui-core/src/transaction_manager.rs`, `crates/sui-core/src/transaction_orchestrator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/transaction_manager.rs`, `crates/sui-core/src/consensus_handler.rs`. The strongest project-level identifiers around this patch are `lock`, `certificate`, `state`, and `transaction`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/consensus_tests.rs`, `crates/sui-core/src/unit_tests/authority_tests.rs`.

## Before/After Behavior

Before the patch, the shown certificate path verified a submitted certificate against the epoch committee before the new reconfiguration-lock block, and pending-consensus insertion did not require a ReconfigState lock parameter. After the patch, handle_certificate obtains get_reconfig_state_read_lock_guard(), checks should_accept_user_certs(), rejects when user certificates are no longer accepted, and the storage API requires a lock guard and asserts the locked state permits user certificates before storing user consensus transactions.

# Root Cause

The grounded issue is an ordering gap around epoch-boundary reconfiguration. The certificate submission path did not require the reconfiguration read lock early enough, and pending user consensus certificate storage did not require proof that the caller still held a lock whose state allowed user certificates.

## Walkthrough

1. A user certificate reaches ValidatorService::handle_certificate through the validator certificate handling path.

2. The handler checks already-executed status and rejects unsupported fullnode or system-certificate cases.

3. Before the change, the supplied hunk shows certificate verification using the epoch committee before the new lock-based reconfiguration check.

4. After the change, the handler obtains the per-epoch reconfiguration read lock early and checks should_accept_user_certs().

5. If user certificates are no longer accepted, the handler records the epoch-boundary rejection metric and rejects before continuing.

6. insert_pending_consensus_transactions now accepts an optional ReconfigState read-lock guard.

7. For ConsensusTransactionKind::UserTransaction, the store requires the lock and asserts that the locked state still allows user certificates.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/authority_server.rs | 350 | Validator RPC certificate handling now acquires the per-epoch reconfiguration read lock early and rejects user certificates at the epoch boundary before verification/execution flow continues. |
| crates/sui-core/src/authority/authority_per_epoch_store.rs | 420 | Pending consensus transaction insertion API now requires a ReconfigState read-lock guard when submitting certificates. |
| crates/sui-core/src/authority/authority_per_epoch_store.rs | 431 | Storage of pending user consensus certificates asserts the caller holds a lock whose state still allows user certificates. |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/authority_server.rs:350` (changes signature or replay validation logic)

Before
```rust
)));
        }
        let cert_verif_metrics_guard = metrics.cert_verification_latency.start_timer();
        let certificate = {
            let epoch_store = state.epoch_store();
            certificate.verify(epoch_store.committee())?
        };
        cert_verif_metrics_guard.stop_and_record();
```
After
```rust
)));
        }
        // code block within reconfiguration lock
        let certificate = {
            let epoch_store = state.epoch_store();
            let reconfiguration_lock = epoch_store.get_reconfig_state_read_lock_guard();
            if !reconfiguration_lock.should_accept_user_certs() {
                metrics.num_rejected_cert_in_epoch_boundary.inc();
```

## Snippet 2

Context: `crates/sui-core/src/authority/authority_per_epoch_store.rs:431` (changes an authorization or privilege gate)

Before
```rust
.insert(&transaction.key(), transaction)?;
        if let ConsensusTransactionKind::UserTransaction(cert) = &transaction.kind {
            self.pending_consensus_certificates
                .lock()
```
After
```rust
.insert(&transaction.key(), transaction)?;
        if let ConsensusTransactionKind::UserTransaction(cert) = &transaction.kind {
            let state = lock.expect("Must pass reconfiguration lock when storing certificate");
            // Caller is responsible for performing graceful check
            assert!(
                state.should_accept_user_certs(),
                "Reconfiguration state should allow accepting user transactions"
            );
```

## Snippet 3

Context: `crates/sui-core/src/authority/authority_per_epoch_store.rs:420` (changes a sensitive control or state-update path)

Before
```rust
}

    pub fn insert_pending_consensus_transactions(
        &self,
        transaction: &ConsensusTransaction,
    ) -> SuiResult {
        self.tables
```
After
```rust
}

    /// When submitting a certificate caller **must** provide a ReconfigState lock guard
    /// and verify that it allows new user certificates
    pub fn insert_pending_consensus_transactions(
        &self,
        transaction: &ConsensusTransaction,
        lock: Option<&RwLockReadGuard<ReconfigState>>,
```

## Snippet 4

Context: `crates/sui-core/src/authority/authority_per_epoch_store.rs:5` (changes a sensitive control or state-update path)

Before
```rust
use futures::FutureExt;
use narwhal_executor::ExecutionIndices;
use parking_lot::Mutex;
use parking_lot::RwLock;
use rocksdb::Options;
use serde::{Deserialize, Serialize};
```
After
```rust
use futures::FutureExt;
use narwhal_executor::ExecutionIndices;
use parking_lot::RwLock;
use parking_lot::{Mutex, RwLockReadGuard};
use rocksdb::Options;
use serde::{Deserialize, Serialize};
```

# Fix Pattern

Acquire the reconfiguration read lock at the certificate submission boundary, check the epoch acceptance state while holding it, and pass the lock requirement into the lower-level pending-consensus storage API.

## How It Was Fixed

authority_server.rs now obtains the reconfiguration read-lock guard and checks should_accept_user_certs() before the certificate verification and consensus flow proceeds. authority_per_epoch_store.rs now adds a lock parameter to insert_pending_consensus_transactions, documents the caller requirement, requires the lock for user transactions, and asserts that the locked state still accepts user certificates.

# Why It Matters

1. Preserves the epoch-boundary acceptance invariant for user certificates.

2. Reduces a race between certificate submission and reconfiguration state changes.

3. Prevents pending-consensus storage from bypassing the reconfiguration-state check.

4. Evidence does not establish signature bypass, proven divergence, double execution, or loss of funds.

# Evidence Notes

The strongest evidence is the commit message stating the lock must be acquired and checked early before signature verification and certificate execution, plus the authority_server.rs hunk adding get_reconfig_state_read_lock_guard() and should_accept_user_certs(), and the authority_per_epoch_store.rs hunk requiring a RwLockReadGuard<ReconfigState> for pending user consensus transactions. Claims beyond an epoch-boundary consensus/reconfiguration ordering issue are unsupported. Protocol security invariant: A validator should not accept or store user certificates for consensus after the per-epoch reconfiguration state stops accepting user certificates; that decision must be checked while holding the ReconfigState read lock so the state cannot change between acceptance and pending-consensus insertion. Verification notes: The patch does not prove a remote attacker could trigger the race reliably. The patch does not show a cryptographic signature bypass. The patch does not prove actual consensus divergence, double execution, or loss of funds occurred. The patch does not establish that non-user or system certificates were affected. The evidence supports an epoch-boundary safety invariant fix, not a general authorization bypass. No external exploitability evidence is provided. No test output or full diff is provided in the input. The classification is downgraded from confirmed/high to likely/medium because impact is inferred from consensus invariants rather than demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `epoch-boundary-reconfiguration-race`
Final impact type: `consensus-invariant-hardening`
Final tags: `blockchain-core, consensus, validator, reconfiguration, epoch-boundary, race-condition, security-hardening`

The supplied patch evidence supports retaining this as security hardening, not a proven concrete security fix. The change moves acquisition and checking of the reconfiguration read lock earlier in validator certificate handling and requires the same lock when storing pending user consensus certificates. That clearly tightens a consensus/reconfiguration invariant around accepting user certificates at epoch boundaries, but the evidence does not prove exploitability, consensus divergence, double execution, signature bypass, or fund loss.

## Security Evidence

1. Certificate submission now acquires get_reconfig_state_read_lock_guard() before proceeding through verification and consensus handling.
2. The code rejects user certificates when should_accept_user_certs() is false and records an epoch-boundary rejection metric.
3. Pending consensus insertion now requires a ReconfigState read-lock guard for user transactions.
4. The storage path asserts that user transactions are only stored while the locked reconfiguration state still accepts user certificates.
5. The commit message explicitly says the lock must be acquired and checked very early before signature verification and certificate execution.

## Missing Evidence

1. No evidence of a demonstrated exploit or attacker-controlled trigger is provided.
2. No evidence proves actual consensus divergence, double execution, or fund loss.
3. No evidence shows a cryptographic signature verification bypass.
4. No full test result or failing regression scenario is included in the supplied input.
5. No external advisory, vulnerability report, or explicit security label is provided.

## Claim Boundaries

1. Classify as consensus/reconfiguration invariant hardening rather than a confirmed consensus safety failure.
2. Do not claim fund loss, double spend, or double execution from the supplied evidence.
3. Do not claim signature bypass or authentication bypass.
4. Do not claim all certificate types were affected; the shown guard is specifically about user certificates.
5. Do not treat the assert as sufficient evidence of a remotely exploitable denial of service.
