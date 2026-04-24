---
case_id: case_20221013_f4ea3fc5f2
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2022-10-13
source_refs:
  - git:f4ea3fc5f2e8a506c045a30bc59bf79c3c317f54
  - "crates/sui-core/src/node_sync/node_state.rs:510"
  - "crates/sui-core/src/authority.rs:2196"
  - "crates/sui-tool/src/db_tool/db_dump.rs:116"
  - "crates/sui-tool/src/db_tool/db_dump.rs:60"
bug_class: epoch-state-confusion
impact_type:
  - state-integrity
  - consensus-integrity
confidence: medium
tags:
  - storage
  - validator
  - consensus
  - epoch-handling
  - certificate-validation
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch addresses a stale-epoch certificate handling bug in Sui authority/node-sync storage. The supplied evidence supports a correctness and state-integrity fix around epoch transitions, but does not establish an exploitable vulnerability or a concrete protocol security failure.

## Observed Patch Facts

1. In `crates/sui-core/src/node_sync/node_state.rs`, the patch replaces `if let Some(cert) = self.state().database.read_certificate(digest)? {` with `if let Some(cert) = self.store().get_cert(epoch_id, digest)? {`.

2. In `crates/sui-core/src/authority.rs`, the patch replaces `self.database` with `// Schedule the certificate for execution`.

3. In `crates/sui-tool/src/db_tool/db_dump.rs`, the patch removes `#[tokio::test]`.

4. In `crates/sui-tool/src/db_tool/db_dump.rs`, the patch replaces `AuthorityStoreTables::<AuthoritySignInfo>::get_read_only_handle(db_path, None, None)` with `let epoch_tables = AuthorityEpochTables::<AuthoritySignInfo>::describe_tables();`.

## Project Context

The changed code sits primarily in `crates/sui-core/src/node_sync`, `crates/sui-core/src`, `crates/sui-core`, which anchors the finding in the `storage` area of the project. Historical context from `crates/sui-core/src/transaction_input_checker.rs`, `crates/sui-core/src/safe_client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/authority/authority_store.rs`, `crates/sui-core/src/transaction_input_checker.rs`. The strongest project-level identifiers around this patch are `cert`, `AuthoritySignInfo`, `digest`, and `certificate`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/gateway_state_tests.rs`, `crates/sui-core/src/unit_tests/batch_tests.rs`.

## Before/After Behavior

Before the patch, node sync could read a certificate by digest from authority storage and then check whether its epoch matched the requested epoch. The commit message describes a case where an epoch N certificate could remain only in certificate storage after an epoch transition and later be encountered in epoch N+1. After the patch, certificate retrieval uses an epoch-aware get_cert(epoch_id, digest) path, asserts the returned certificate epoch, and consensus user transaction handling schedules certificates through add_pending_certificates. Authority tables are also split into epoch-specific and perpetual tables, with db_dump updated accordingly.

# Root Cause

Epoch-specific certificate state could be persisted or retrieved through paths that were not sufficiently tied to the pending-execution workflow and active epoch. This could leave a locally unexecuted certificate from one epoch in storage and later expose it to code handling a later epoch.

## Walkthrough

1. A certificate for epoch N could be added to pending certificate handling before local execution completed.

2. The validator could advance to epoch N+1 before the certificate was executed locally.

3. The commit message states the certificate could remain only in the certificates table and miss the final checkpoint for epoch N.

4. A later request for the same transaction in epoch N+1 could encounter the stored epoch N certificate.

5. The pre-patch node-sync path read by digest and only checked the epoch after retrieving the certificate.

6. The patch changes retrieval to get_cert(epoch_id, digest), making the lookup epoch-aware.

7. The patch asserts that any returned certificate belongs to the requested epoch.

8. Consensus user transaction handling now schedules certificates through add_pending_certificates.

9. The table split separates epoch-specific authority data from perpetual authority data.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/node_sync/node_state.rs | 507 | retrieves certificates for node sync using an epoch-aware store lookup and asserts the returned certificate epoch matches the requested epoch |
| crates/sui-core/src/authority.rs | 2196 | handles consensus user transactions by scheduling certificates for execution through pending-certificate storage |
| crates/sui-tool/src/db_tool/db_dump.rs | 53 | updates database dump tooling to understand the split between epoch and perpetual authority tables |
| crates/sui-tool/src/db_tool/db_dump.rs | 110 | updates tests/imports for the split authority table layout |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/node_sync/node_state.rs:510` (changes a consensus- or validator-sensitive branch)

Before
```rust
digest: &TransactionDigest,
    ) -> SuiResult<CertifiedTransaction> {
        if let Some(cert) = self.state().database.read_certificate(digest)? {
            if cert.epoch() == epoch_id {
                return Ok(cert);
            }
            warn!(
                ?digest, ?epoch_id, cert_epoch = ?cert.epoch(),
```
After
```rust
digest: &TransactionDigest,
    ) -> SuiResult<CertifiedTransaction> {
        if let Some(cert) = self.store().get_cert(epoch_id, digest)? {
            assert_eq!(epoch_id, cert.epoch());
            return Ok(cert);
        }
```

## Snippet 2

Context: `crates/sui-core/src/authority.rs:2196` (changes a consensus- or validator-sensitive branch)

Before
```rust
);

                self.database
                    .persist_certificate_and_lock_shared_objects(*certificate, consensus_index)
                    // todo - potentially more errors from inside here needs to be mapped differently
                    .await
```
After
```rust
);

                // Schedule the certificate for execution
                self.add_pending_certificates(vec![(
                    *certificate.digest(),
                    Some(*certificate.clone()),
                )])
                .map_err(NarwhalHandlerError::NodeError)?;
```

## Snippet 3

Context: `crates/sui-tool/src/db_tool/db_dump.rs:116` (changes a consensus- or validator-sensitive branch)

Before
```rust
#[cfg(test)]
mod test {
    use sui_core::authority::authority_store_tables::AuthorityStoreTables;
    use sui_types::crypto::AuthoritySignInfo;

    use crate::db_tool::db_dump::{dump_table, list_tables, StoreName};

    #[tokio::test]
```
After
```rust
#[cfg(test)]
mod test {
    use sui_core::authority::authority_store_tables::AuthorityEpochTables;
    use sui_core::authority::authority_store_tables::AuthorityPerpetualTables;
    use sui_types::crypto::AuthoritySignInfo;

    use crate::db_tool::db_dump::{dump_table, list_tables, StoreName};
```

## Snippet 4

Context: `crates/sui-tool/src/db_tool/db_dump.rs:60` (changes a consensus- or validator-sensitive branch)

Before
```rust
match store_name {
        StoreName::Validator => {
            AuthorityStoreTables::<AuthoritySignInfo>::get_read_only_handle(db_path, None, None)
                .dump(table_name, page_size, page_number)
        }
        StoreName::Gateway => AuthorityStoreTables::<EmptySignInfo>::get_read_only_handle(
            db_path, None, None,
        )
```
After
```rust
match store_name {
        StoreName::Validator => {
            let epoch_tables = AuthorityEpochTables::<AuthoritySignInfo>::describe_tables();
            if epoch_tables.contains_key(table_name) {
                AuthorityEpochTables::<AuthoritySignInfo>::open_readonly(&db_path).dump(
                    table_name,
                    page_size,
                    page_number,
```

# Fix Pattern

Separate epoch-scoped state from perpetual state, use epoch-aware certificate lookup, and place consensus certificates into the pending-execution path instead of relying on certificate persistence alone.

## How It Was Fixed

The patch splits AuthorityStoreTables into AuthorityEpochTables and AuthorityPerpetualTables. Node sync changes certificate lookup from read_certificate(digest) to get_cert(epoch_id, digest) and asserts the returned epoch. Authority consensus handling schedules user transaction certificates with add_pending_certificates. Tooling and tests are updated for the table split.

# Why It Matters

1. Prevents stale epoch certificates from being treated as current local state.

2. Improves validator state consistency across epoch transitions.

3. Keeps pending execution state explicit.

4. The evidence does not prove asset theft, signature forgery, attacker control, or a full consensus safety failure.

# Evidence Notes

Strongest evidence is the commit message's stale epoch-N certificate scenario, node_sync/node_state.rs changing digest-only certificate lookup to epoch-aware get_cert(epoch_id, digest), and authority.rs scheduling certificates through add_pending_certificates. db_dump changes are ancillary support for the table split. The provided evidence does not establish external exploitability or concrete security impact, so security classification should not be stronger than unclear. Protocol security invariant: Validator certificate handling should be epoch-scoped: a certificate retrieved or scheduled for a given epoch should belong to that epoch, and epoch-specific authority state should not be reused across epoch transitions as if it were current. Verification notes: The patch does not prove that an attacker can intentionally force epoch advancement at the vulnerable point. The patch does not prove execution of the wrong-epoch certificate would lead to asset theft or signature forgery. The patch does not show a full consensus safety failure, only an invalid local validator execution path risk. DB dump changes appear ancillary and are not themselves security-relevant. No proof that an attacker can force the timing window. No proof of asset theft or signature forgery. No proof of a complete consensus safety violation. Patch is best treated as correctness/security-adjacent hardening unless additional evidence shows exploitability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `epoch-state-confusion`
Final impact type: `state-integrity, consensus-integrity`
Final confidence: `medium`
Final tags: `storage, validator, consensus, epoch-handling, certificate-validation, state-integrity`

The supplied evidence supports keeping this as security hardening, not a confirmed exploitable security fix. The patch moves certificate lookup and storage behavior toward epoch-scoped handling in validator/node-sync code, and the commit message describes a path where a stale certificate from epoch N could later be used during epoch N+1. That is a security-sensitive consensus/state-integrity invariant, but the evidence does not prove attacker control, asset loss, signature bypass, or a concrete consensus safety violation.

## Security Evidence

1. Validator/node-sync code changes certificate retrieval from digest-only storage lookup to get_cert(epoch_id, digest).
2. The new path asserts that the returned certificate epoch matches the requested epoch.
3. Commit message explicitly describes a stale epoch-N certificate later causing an attempt to execute a certificate from the wrong epoch.
4. Consensus transaction handling now schedules certificates through add_pending_certificates instead of only persisting certificate data.
5. Authority storage is split into epoch-specific and perpetual tables, reinforcing epoch isolation.

## Missing Evidence

1. No proof that an external attacker can reliably create or exploit the timing window.
2. No demonstrated asset theft, unauthorized state transition, or signature forgery.
3. No evidence of a full consensus safety or liveness failure across validators.
4. DB dump changes are maintenance/tooling support and not independently security-relevant.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Do not claim confirmed exploitability from the supplied patch alone.
3. Do not claim financial loss, authentication bypass, or cryptographic failure.
4. The supported claim is limited to tightening epoch-scoped certificate/state handling in validator consensus-adjacent code.
