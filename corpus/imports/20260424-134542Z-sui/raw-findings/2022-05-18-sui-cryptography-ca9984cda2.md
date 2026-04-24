---
case_id: case_20220518_ca9984cda2
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2022-05-18
source_refs:
  - git:ca9984cda22979a9e9dd076759972e22056f6f62
  - "sui_core/src/authority.rs:1053"
  - "sui_core/src/authority.rs:512"
  - "sui_core/src/authority.rs:502"
  - "test_utils/src/authority.rs:31"
bug_class: consensus-input-validation
impact_type:
  - consensus-integrity
tags:
  - blockchain-core
  - consensus
  - validator
  - input-validation
  - shared-objects
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a security-hardening classification for shared-object consensus input validation. The patch adds a local certificate.contains_shared_object() guard before shared-object consensus handling continues. It does not establish a confirmed exploit, cryptographic flaw, arbitrary finalization, or proven state corruption.

## Observed Patch Facts

1. In `sui_core/src/authority.rs`, the patch replaces `// Ensure an idempotent answer.` with `// Ensure the input is a shared object certificate. Remember that Byzantine authorities`.

2. In `sui_core/src/authority.rs`, the patch replaces `match self` with `if self.shared_locks_exist(&certificate).await? {`.

3. In `sui_core/src/authority.rs`, the patch replaces `// If we already executed this transaction, return the sign effects.` with `// If we already executed this transaction, return the signed effects.`.

4. In `test_utils/src/authority.rs`, the patch replaces `NetworkConfig::generate_with_rng(&config_dir, TEST_COMMITTEE_SIZE, rng)` with `let mut configs = NetworkConfig::generate_with_rng(&config_dir, TEST_COMMITTEE_SIZE,...`.

## Project Context

The changed code sits primarily in `sui_core/src`, `test_utils/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `sui_core/src/transaction_input_checker.rs`, `sui_core/src/safe_client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sui_core/src/safe_client.rs`, `sui_core/src/gateway_types.rs`. The strongest project-level identifiers around this patch are `digest`, `transaction`, `certificate`, and `NetworkConfig::generate_with_rng`. Nearby tests or test-like files include `sui_core/src/unit_tests/batch_tests.rs`, `sui_core/src/unit_tests/authority_tests.rs`.

## Before/After Behavior

Before the patch, the provided handle_consensus_transaction snippet shows a user certificate being unpacked and then proceeding to digest/idempotency handling without the shown shared-object certificate guard. After the patch, the handler rejects certificates that do not contain shared-object inputs with SuiError::NotASharedObjectTransaction. The try_skip_consensus context also shows the same shared-object precondition before returning existing effects or attempting lock-based execution. The Narwhal parameter changes are test support.

# Root Cause

The observed shared-object consensus path lacked a local validation check, in the supplied before snippet, that the certified transaction actually contained shared-object inputs before downstream shared-object handling. The patch comment indicates this matters because Byzantine authorities may submit arbitrary inputs into consensus.

## Walkthrough

1. A consensus transaction reaches AuthorityState::handle_consensus_transaction and is unpacked as a user certificate.

2. The pre-patch snippet proceeds from unpacking into digest-based handling without the shown shared-object certificate guard.

3. The patched comment explicitly treats Byzantine authorities as possible sources of arbitrary consensus input.

4. The patch adds certificate.contains_shared_object() as a local precondition.

5. Non-shared-object certificates now fail with NotASharedObjectTransaction before the observed shared-object consensus handling continues.

6. The try_skip_consensus path also shows the same shared-object precondition before shortcut handling.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sui_core/src/authority.rs | 1048 | Consensus transaction handler now rejects user certificates that do not contain shared-object inputs before shared-object execution proceeds. |
| sui_core/src/authority.rs | 494 | Skip-consensus path enforces the shared-object certificate requirement and only reuses existing shared locks when they are attributed to the transaction. |
| test_utils/src/authority.rs | 30 | Test network Narwhal timing parameters adjusted to make consensus/shared-object tests run quickly; not itself a security path. |

## Code Snippets

## Snippet 1

Context: `sui_core/src/authority.rs:1053` (changes signature or replay validation logic)

Before
```rust
let ConsensusTransaction::UserTransaction(certificate) = transaction;

        // Ensure an idempotent answer.
        let digest = certificate.digest();
        if self.database.effects_exists(digest)? {
            let info = self.make_transaction_info(digest).await?;
            debug!(tx_digest =? digest, "Shared-object transaction already executed");
            return Ok(bincode::serialize(&info).unwrap());
```
After
```rust
let ConsensusTransaction::UserTransaction(certificate) = transaction;

        // Ensure the input is a shared object certificate. Remember that Byzantine authorities
        // may input anything into consensus.
        fp_ensure!(
            certificate.contains_shared_object(),
            SuiError::NotASharedObjectTransaction
        );
```

## Snippet 2

Context: `sui_core/src/authority.rs:512` (changes persisted or aggregate state handling)

Before
```rust
// This can happen to transaction previously submitted to consensus that failed execution
        // due to missing dependencies.
        match self
            .database
            .sequenced(digest, certificate.shared_input_objects())?[0]
        {
            Some(_) => {
                // Attempt to execute the transaction. This will only succeed if the authority
```
After
```rust
// This can happen to transaction previously submitted to consensus that failed execution
        // due to missing dependencies.
        if self.shared_locks_exist(&certificate).await? {
            // Attempt to execute the transaction. This will only succeed if the authority
            // already executed all its dependencies and if the locks are correctly attributed to
            // the transaction (ie. this transaction is the next to be executed).
            debug!("Shared-locks already assigned to {digest:?} - executing now");
            let confirmation = ConfirmationTransaction { certificate };
```

## Snippet 3

Context: `sui_core/src/authority.rs:502` (changes a sensitive control or state-update path)

Before
```rust
);

        // If we already executed this transaction, return the sign effects.
        let digest = certificate.digest();
        if self.database.effects_exists(digest)? {
```
After
```rust
);

        // If we already executed this transaction, return the signed effects.
        let digest = certificate.digest();
        if self.database.effects_exists(digest)? {
```

## Snippet 4

Context: `test_utils/src/authority.rs:31` (changes a consensus- or validator-sensitive branch)

Before
```rust
let config_dir = tempfile::tempdir().unwrap().into_path();
    let rng = StdRng::from_seed([0; 32]);
    NetworkConfig::generate_with_rng(&config_dir, TEST_COMMITTEE_SIZE, rng)
}
```
After
```rust
let config_dir = tempfile::tempdir().unwrap().into_path();
    let rng = StdRng::from_seed([0; 32]);
    let mut configs = NetworkConfig::generate_with_rng(&config_dir, TEST_COMMITTEE_SIZE, rng);
    for config in configs.validator_configs.iter_mut() {
        let parameters = &mut config.consensus_config.narwhal_config;
        // NOTE: the following parameters are important to ensure tests run fast. Using the default
        // Narwhal parameters may result in tests taking >60 seconds.
        parameters.header_size = 1;
```

# Fix Pattern

Add an explicit validation guard at the consensus execution boundary and fail closed with a typed error when the certified transaction does not satisfy the shared-object invariant.

## How It Was Fixed

The runtime change adds fp_ensure!(certificate.contains_shared_object(), SuiError::NotASharedObjectTransaction) in the consensus transaction handler before continuing with shared-object execution behavior. The try_skip_consensus path also shows the shared-object certificate requirement. The Narwhal configuration changes are treated as test support, not as the root cause.

# Why It Matters

1. Consensus input may include arbitrary submissions from Byzantine authorities.

2. Authorities should not rely on upstream consensus participants to preserve the shared-object transaction invariant.

3. The patch blocks non-shared-object certificates from the observed shared-object consensus handling path.

4. Exploitability is not proven by the supplied evidence.

# Evidence Notes

Primary evidence is from sui_core/src/authority.rs around handle_consensus_transaction line 1048 and try_skip_consensus line 494. The grounded security-relevant change is the added certificate.contains_shared_object() guard and NotASharedObjectTransaction error. The evidence does not support claims of cryptographic verification failure, confirmed state corruption, arbitrary transaction finalization, or a production Narwhal configuration vulnerability. Protocol security invariant: The shared-object consensus execution path should only process certified transactions that actually contain shared-object inputs, and each authority should enforce that locally because consensus input may include arbitrary submissions from Byzantine authorities. Verification notes: Exploitability is not proven by the patch. No evidence shows a cryptographic signature verification flaw. No evidence shows arbitrary transaction finalization or confirmed state corruption. The Narwhal config changes are test support, not a production security fix. The patch is best classified as consensus input-validation hardening unless external advisory context proves a vulnerability. No external advisory or exploit evidence is provided. The classification is security hardening, not a confirmed vulnerability fix. Test utility Narwhal timing changes are support code only. Confidence is medium because the invariant is explicit, but impact is not demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-input-validation`
Final impact type: `consensus-integrity`
Final tags: `blockchain-core, consensus, validator, input-validation, shared-objects`

The patch evidence supports a conservative security-hardening classification. It adds an explicit shared-object certificate precondition at a consensus execution boundary, with an in-code comment noting that Byzantine authorities may submit arbitrary inputs into consensus. That is security-sensitive validation hardening, but the supplied evidence does not prove an exploitable vulnerability, state corruption, cryptographic failure, or concrete impact.

## Security Evidence

1. Adds fp_ensure!(certificate.contains_shared_object(), SuiError::NotASharedObjectTransaction) before shared-object consensus handling continues.
2. Patch comment explicitly frames the boundary as exposed to arbitrary input from Byzantine authorities.
3. try_skip_consensus also enforces the shared-object certificate invariant before shortcut execution behavior.
4. shared_locks_exist change appears to tighten lock attribution before immediate execution.

## Missing Evidence

1. No exploit scenario or advisory is provided.
2. No evidence shows non-shared-object certificates could cause state corruption or unauthorized finalization.
3. No cryptographic verification or signature-validation flaw is demonstrated.
4. Narwhal configuration changes are test-speed support, not production security evidence.

## Claim Boundaries

1. Classify as consensus input-validation hardening, not a confirmed vulnerability fix.
2. Do not retain the original cryptography or signature framing.
3. Do not claim proven state corruption or arbitrary transaction finalization.
4. Impact should be limited to protecting consensus/shared-object execution invariants.
