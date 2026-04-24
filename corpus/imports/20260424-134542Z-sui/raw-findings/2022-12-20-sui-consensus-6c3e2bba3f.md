---
case_id: case_20221220_6c3e2bba3f
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2022-12-20
source_refs:
  - git:6c3e2bba3f36e647011ca6a374f8bcfac8747857
  - "crates/sui-core/src/authority.rs:2597"
  - "crates/sui-core/src/authority.rs:2699"
  - "crates/sui-core/src/authority/authority_store.rs:184"
  - "crates/sui-core/src/authority/authority_per_epoch_store.rs:543"
bug_class: consensus-epoch-invariant-hardening
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - consensus
  - reconfiguration
  - epoch-isolation
  - validator
  - state-management
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a consensus/reconfiguration correctness hardening: the patch carries an intended epoch into transaction-processing paths and adds checked loading of the per-epoch store. It does not establish a vulnerability, attacker influence, exploitability, consensus fork, asset loss, or other concrete security impact.

## Observed Patch Facts

1. In `crates/sui-core/src/authority.rs`, the patch replaces `match &transaction.kind {` with `let epoch_store = match self.load_epoch_store(current_epoch) {`.

2. In `crates/sui-core/src/authority.rs`, the patch replaces `if let Some((index, roots)) = self.database.last_checkpoint(round)? {` with `let epoch_store = self.load_epoch_store(current_epoch)?;`.

3. In `crates/sui-core/src/authority/authority_store.rs`, the patch replaces `/// Returns the TransactionEffects if we have an effects structure for this transacti...` with `// TODO: Deprecate this once we replace all calls with load_epoch_store.`.

4. In `crates/sui-core/src/authority/authority_per_epoch_store.rs`, the patch replaces `pub fn finish_consensus_transaction_process(` with `/// Caller is responsible to call consensus_message_processed before this method`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, `crates/sui-core/src/authority`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/sui-core/src/transaction_manager.rs`, `crates/sui-core/src/transaction_orchestrator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/transaction_manager.rs`, `crates/sui-core/src/storage.rs`. The strongest project-level identifiers around this patch are `epoch_store`, `transaction`, `load_epoch_store`, and `store`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/authority_tests.rs`, `crates/sui-core/src/unit_tests/batch_transaction_tests.rs`.

## Before/After Behavior

Before the patch, the shown consensus transaction and checkpoint-boundary paths used the active store or database paths without an explicit shown guard that the loaded per-epoch state matched the epoch being processed. After the patch, these paths call load_epoch_store(current_epoch), return early if the active epoch store no longer matches, check certificate.epoch() against current_epoch, and read checkpoint state through the epoch-local store.

# Root Cause

The prior code did not consistently enforce, at the shown call sites, that the per-epoch store being used matched the epoch carried by consensus processing. During reconfiguration, the active epoch store can be swapped, so the patch adds explicit mismatch detection.

## Walkthrough

1. Consensus transaction processing now receives or uses current_epoch in the affected path.

2. AuthorityState::process_consensus_transaction calls self.load_epoch_store(current_epoch) before handling the transaction kind.

3. AuthorityStore::load_epoch_store loads the active epoch store and checks store.epoch() == intended_epoch.

4. If the epoch store does not match, process_consensus_transaction logs the mismatch and returns Ok(None), with a comment saying the epoch changed while the transaction was being processed.

5. User transaction handling adds a certificate.epoch() != current_epoch check.

6. Checkpoint-boundary lookup now loads the checked epoch store and reads last_checkpoint(round) and final_epoch_checkpoint() from it.

7. Some consensus certificate bookkeeping is moved into AuthorityPerEpochStore, but the provided evidence supports treating that as supporting restructuring rather than the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/authority.rs | 2597 | Consensus transaction processing now loads the per-epoch store for current_epoch and stops processing if the loaded store epoch mismatches. |
| crates/sui-core/src/authority.rs | 2597 | User transaction certificate processing now rejects or skips certificates whose certificate.epoch() differs from current_epoch. |
| crates/sui-core/src/authority.rs | 2699 | Checkpoint boundary lookup now uses the current epoch's AuthorityPerEpochStore instead of the global database path. |
| crates/sui-core/src/authority/authority_store.rs | 184 | Adds load_epoch_store(intended_epoch), enforcing that the active epoch store matches the caller's intended epoch. |
| crates/sui-core/src/authority/authority_per_epoch_store.rs | 543 | Moves consensus certificate recording into the per-epoch store path, tying consensus progress bookkeeping to epoch-local state. |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/authority.rs:2597` (changes a consensus- or validator-sensitive branch)

Before
```rust
}) = transaction;
        let tracking_id = transaction.get_tracking_id();
        match &transaction.kind {
            ConsensusTransactionKind::UserTransaction(certificate) => {
                let authority = (&consensus_output.header.author).into();
                if self.database.sent_end_of_publish(&authority)? {
                    // This can not happen with valid authority
                    // With some edge cases narwhal might sometimes resend previously seen certificate after EndOfPublish
```
After
```rust
}) = transaction;
        let tracking_id = transaction.get_tracking_id();
        let epoch_store = match self.load_epoch_store(current_epoch) {
            Ok(s) => s,
            Err(err) => {
                // Epoch has changed while this transaction is being processed. Ignore it.
                debug!(
                    "Error loading epoch store in process_consensus_transaction: {:?}",
```

## Snippet 2

Context: `crates/sui-core/src/authority.rs:2699` (changes a consensus- or validator-sensitive branch)

Before
```rust
//
        // Only after CheckpointService::notify_checkpoint stores checkpoint in it's store we update checkpoint boundary
        if let Some((index, roots)) = self.database.last_checkpoint(round)? {
            let final_checkpoint_round = self.database.final_epoch_checkpoint()?;
            let final_checkpoint = match final_checkpoint_round.map(|r| r.cmp(&round)) {
                Some(CmpOrdering::Less) => {
```
After
```rust
//
        // Only after CheckpointService::notify_checkpoint stores checkpoint in it's store we update checkpoint boundary
        let epoch_store = self.load_epoch_store(current_epoch)?;
        if let Some((index, roots)) = epoch_store.last_checkpoint(round)? {
            let final_checkpoint_round = epoch_store.final_epoch_checkpoint()?;
            let final_checkpoint = match final_checkpoint_round.map(|r| r.cmp(&round)) {
                Some(CmpOrdering::Less) => {
```

## Snippet 3

Context: `crates/sui-core/src/authority/authority_store.rs:184` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    pub fn epoch_store(&self) -> Guard<Arc<AuthorityPerEpochStore>> {
        self.epoch_store.load()
    }

    /// Returns the TransactionEffects if we have an effects structure for this transaction digest
    pub fn get_effects(
```
After
```rust
}

    // TODO: Deprecate this once we replace all calls with load_epoch_store.
    pub fn epoch_store(&self) -> Guard<Arc<AuthorityPerEpochStore>> {
        self.epoch_store.load()
    }

    pub fn load_epoch_store(
```

## Snippet 4

Context: `crates/sui-core/src/authority/authority_per_epoch_store.rs:543` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    pub fn finish_consensus_transaction_process(
        &self,
```
After
```rust
}

    /// Caller is responsible to call consensus_message_processed before this method
    pub async fn record_owned_object_cert_from_consensus(
        &self,
        transaction: &ConsensusTransaction,
        certificate: &VerifiedCertificate,
        consensus_index: ExecutionIndicesWithHash,
```

# Fix Pattern

Propagate the intended epoch to consensus processing, use an epoch-checked accessor for per-epoch state, and stop or reject processing when the active store or certificate epoch does not match.

## How It Was Fixed

The patch adds AuthorityStore::load_epoch_store(intended_epoch), which returns StoreAccessEpochMismatch when the loaded store epoch differs. Consensus transaction processing uses this accessor, ignores work when the epoch changed mid-processing, checks certificate epochs, and shifts checkpoint-boundary reads to the checked per-epoch store.

# Why It Matters

1. Consensus reconfiguration is sensitive to epoch boundaries.

2. Using state from the wrong epoch could cause incorrect processing or bookkeeping.

3. The evidence shows invariant hardening, not a proven exploitable vulnerability.

# Evidence Notes

Grounded evidence comes from authority.rs, authority_store.rs, and authority_per_epoch_store.rs hunks showing load_epoch_store(current_epoch), StoreAccessEpochMismatch, certificate.epoch() checks, and movement of some operations into per-epoch storage. The commit message describes epoch propagation and table movement, not a security fix. Claims of remote exploitability, adversary control, validator equivocation, asset loss, or a consensus fork are unsupported. Protocol security invariant: Consensus work that is scoped to an epoch should read and update the AuthorityPerEpochStore for that same epoch, and certificates should not be processed under a mismatched consensus epoch. Verification notes: The patch does not prove remote exploitability. The patch does not prove an adversary can force an epoch-store race. The patch does not prove validator equivocation, asset loss, or consensus fork occurred. Checkpoint-related epoch propagation is explicitly described as incomplete and deferred to a separate PR. Some changes are structural movement into per-epoch tables, so the security claim is limited to epoch-invariant enforcement shown in the hunks. No exploit scenario is demonstrated by the provided evidence. No advisory, issue text, or test proving a security failure is included. Checkpoint epoch propagation is described by the commit body as incomplete and deferred to a separate PR. Classified as unclear security relevance rather than confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-epoch-invariant-hardening`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, reconfiguration, epoch-isolation, validator, state-management, hardening`

The supplied patch evidence supports retaining this as security hardening, not as a proven security fix. The code adds explicit epoch matching for consensus transaction processing and checkpoint-boundary access, rejects or skips mismatched epoch work, and moves state access toward per-epoch storage. Those are meaningful invariant checks in a security-sensitive consensus/validator path, but the evidence does not prove exploitability, an actual consensus break, asset loss, or attacker control.

## Security Evidence

1. Consensus transaction processing now loads the epoch store through load_epoch_store(current_epoch).
2. AuthorityStore::load_epoch_store enforces store.epoch() == intended_epoch and returns StoreAccessEpochMismatch otherwise.
3. The consensus path ignores processing when the epoch changed while a transaction is being processed.
4. User transaction handling adds a certificate.epoch() != current_epoch check.
5. Checkpoint-boundary reads are moved from global database access to the checked per-epoch store.

## Missing Evidence

1. No advisory, CVE, issue, or commit text identifies this as a security vulnerability.
2. No test or proof shows an exploitable consensus fork or validator safety violation.
3. No evidence shows an attacker can trigger or control the epoch-store mismatch.
4. No demonstrated impact such as asset loss, unauthorized execution, or network compromise.

## Claim Boundaries

1. Validate only as consensus epoch-invariant hardening.
2. Do not claim a concrete exploitable vulnerability from the supplied patch alone.
3. Do not claim confirmed consensus failure, fork, or asset loss.
4. Checkpoint-related propagation was described as incomplete and deferred to a later PR.
