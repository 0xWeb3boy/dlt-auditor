---
case_id: case_20230412_97f265501
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2023-04-12
source_refs:
  - git:97f265501b0479cbe3236f2278ca42994491b5c4
  - "keymanager/src/crypto/kdf.rs:465"
  - "keymanager/src/runtime/methods.rs:421"
  - "keymanager/src/crypto/kdf.rs:385"
  - "keymanager/src/crypto/kdf.rs:1893"
bug_class: untrusted-secret-validation
impact_type:
  - integrity-risk
confidence: medium
tags:
  - cryptography
  - key-management
  - secret-replication
  - integrity-checks
  - state-scoping
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence shows security-relevant hardening in key-manager rotation handling, but it does not establish a concrete vulnerability. The strongest supported reading is stricter validation and scoping for replicated secrets and proposal state, combined with some robustness-oriented cleanup.

## Observed Patch Facts

1. In `keymanager/src/crypto/kdf.rs`, the patch replaces `let vs = master_secret_fetcher(generation)?;` with `let (secret, prev_checksum) = provider`.

2. In `keymanager/src/runtime/methods.rs`, the patch replaces `/// Fetch master secret from another key manager enclave.` with `/// Key manager client for master and ephemeral secret replication.`.

3. In `keymanager/src/crypto/kdf.rs`, the patch replaces `let last = epoch + 1;` with `let to = epoch + 1;`.

4. In `keymanager/src/crypto/kdf.rs`, the patch replaces `let result = Kdf::load_master_secret_proposal(&storage);` with `let runtime_id = Namespace([2; NAMESPACE_SIZE]);`.

## Project Context

The changed code sits primarily in `keymanager/src/crypto`, `keymanager/src`, `keymanager/src/runtime`, which anchors the finding in the `cryptography` area of the project. Historical context from `keymanager/src/crypto/packing.rs`, `keymanager/src/crypto/types.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `keymanager/src/crypto/packing.rs`, `keymanager/src/secrets/mock.rs`. The strongest project-level identifiers around this patch are `secret`, `Kdf::load_master_secret_proposal`, `generation`, and `epoch`.

## Before/After Behavior

Before the patch, the shown master-secret recovery path consumed a single fetched record via `master_secret_fetcher(generation)?` and rejected immediately if that one record did not fit the expected checksum chain. After the patch, it iterates provider-supplied candidates and selects one whose derived chain matches. Before the patch, startup ephemeral-secret replication scanned all epochs from `0` through `epoch + 1`; after the patch, it scans only a bounded recent window based on `EPHEMERAL_SECRET_CACHE_SIZE`. In the shown tests, master-secret proposal save/load helpers previously lacked explicit `runtime_id` and `generation` parameters; after the patch, they are passed explicitly and a wrong-generation lookup returns `None`.

# Root Cause

The supported evidence points to weaker pre-patch state selection and scoping in the rotation path: the code depended on a single fetched master-secret candidate, and the shown proposal helper API was less explicitly bound to runtime and generation. That supports a narrow thesis of validation/scoping hardening, but not a proven exploitable vulnerability.

## Walkthrough

1. In `keymanager/src/crypto/kdf.rs`, the pre-patch master-secret path fetched one candidate with `master_secret_fetcher(generation)?`, derived `prev_checksum`, and failed if that single candidate did not match the expected chain.

2. The patched code replaces that with `provider.master_secret_iter(generation).find_map(...)`, evaluating multiple replicated candidates and accepting one that fits the checksum chain while still treating fetched data as untrusted.

3. In the same file's initialization path, pre-patch startup replication walked every epoch from `0` to `epoch + 1`; the patched code limits this to a recent window derived from `EPHEMERAL_SECRET_CACHE_SIZE`.

4. The tests in `keymanager/src/crypto/kdf.rs` now call proposal save/load helpers with explicit `runtime_id` and `generation`, and they check that loading with `generation + 1` returns `None`.

5. Commit metadata also mentions separate sealing context for proposals and rotation-failure scenarios, but the direct code excerpts provided here do not independently prove the security impact of those parts.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| keymanager/src/crypto/kdf.rs | 348 | startup replication path for ephemeral secrets during key-manager initialization |
| keymanager/src/crypto/kdf.rs | 459 | master-secret replication and checksum-chain verification against untrusted fetched values |
| keymanager/src/runtime/methods.rs | 391 | runtime RPC path used to replicate master and ephemeral secrets from peer enclaves |
| keymanager/src/crypto/kdf.rs | 1891 | regression coverage showing master-secret proposals are now loaded/stored with runtime and generation binding |

## Code Snippets

## Snippet 1

Context: `keymanager/src/crypto/kdf.rs:465` (changes a sensitive control or state-update path)

Before
```rust
// Master secret wasn't found and needs to be fetched from another enclave.
            // Fetched values are untrusted and need to be verified.
            let vs = master_secret_fetcher(generation)?;
            let (secret, prev_checksum) = match vs.checksum.is_empty() {
                true => (vs.secret, runtime_id.0.to_vec()),
                false => (vs.secret, vs.checksum),
            };
            let next_checksum = Self::checksum_master_secret(&secret, &prev_checksum);
```
After
```rust
// Master secret wasn't found and needs to be fetched from another enclave.
            // Fetched values are untrusted and need to be verified.
            let (secret, prev_checksum) = provider
                .master_secret_iter(generation)
                .find_map(|vs| {
                    let prev_checksum = if vs.checksum.is_empty() {
                        runtime_id.0.to_vec()
                    } else {
```

## Snippet 2

Context: `keymanager/src/runtime/methods.rs:421` (changes signature or replay validation logic)

Before
```rust
}

/// Fetch master secret from another key manager enclave.
fn fetch_master_secret(
    generation: u64,
    nodes: &Vec<signature::PublicKey>,
    client: &RemoteClient,
) -> Result<VerifiableSecret> {
```
After
```rust
}

/// Key manager client for master and ephemeral secret replication.
fn key_manager_client_for_replication(ctx: &mut RpcContext) -> RemoteClient {
```

## Snippet 3

Context: `keymanager/src/crypto/kdf.rs:385` (changes a consensus- or validator-sensitive branch)

Before
```rust
// On startup replicate ephemeral secrets.
        if next_generation == 0 {
            let last = epoch + 1;
            for epoch in (0..=last).rev() {
                if let Ok(secret) = ephemeral_secret_fetcher(epoch) {
                    let mut inner = self.inner.write().unwrap();
                    inner.verify_runtime_id(&runtime_id)?;
                    inner.add_ephemeral_secret(secret, epoch);
```
After
```rust
// On startup replicate ephemeral secrets.
        if next_generation == 0 {
            let to = epoch + 1;
            let from = to.saturating_sub(EPHEMERAL_SECRET_CACHE_SIZE as u64);

            for epoch in (from..=to).rev() {
                let secret = match provider.ephemeral_secret_iter(epoch).next() {
                    Some(secret) => secret,
```

## Snippet 4

Context: `keymanager/src/crypto/kdf.rs:1893` (changes the branch that decides whether execution stops or continues)

Before
```rust
let secret = Secret([0; SECRET_SIZE]);
        let new_secret = Secret([1; SECRET_SIZE]);

        // Empty storage.
        let result = Kdf::load_master_secret_proposal(&storage);
        assert!(result.is_none());

        // Happy path.
```
After
```rust
let secret = Secret([0; SECRET_SIZE]);
        let new_secret = Secret([1; SECRET_SIZE]);
        let runtime_id = Namespace([2; NAMESPACE_SIZE]);
        let generation = 3;

        // Empty storage.
        let result = Kdf::load_master_secret_proposal(&storage, &runtime_id, generation);
        assert!(result.is_none());
```

# Fix Pattern

Tighten rotation-state validation and scoping by selecting only checksum-consistent replicated candidates, binding proposal state to runtime and generation, and limiting initialization to a bounded replication window.

## How It Was Fixed

The patch swaps one-shot secret fetches for provider-backed iteration so non-matching replicated candidates can be skipped, constrains startup ephemeral-secret import to a recent bounded range, and makes proposal persistence explicitly runtime/generation-scoped in the shown tests. These changes harden integrity and robustness of the rotation flow, but the supplied evidence does not prove a full attack scenario.

# Why It Matters

1. Untrusted replicated secret material should not drive rotation state unless it matches the expected checksum chain.

2. Proposal state should not be reusable across the wrong runtime or generation.

3. Bounding startup replication reduces dependence on large historical secret scans.

4. The evidence supports integrity hardening more clearly than a confirmed vulnerability fix.

# Evidence Notes

Direct evidence supports three concrete claims: the master-secret path now searches multiple provider-supplied candidates instead of trusting one fetched result; startup ephemeral-secret replication is now bounded; and proposal save/load helpers in tests are explicitly keyed by runtime and generation. The provided excerpts do not directly show an end-to-end exploit, a checksum-verification bypass, secret disclosure, or the actual diff for the sealing-context split. Protocol security invariant: Replicated or persisted master-secret state should only affect rotation when it is bound to the correct runtime and generation and matches the expected checksum chain; replicated values are untrusted until verified. Verification notes: The patch does not by itself prove secret disclosure, key recovery, or ciphertext forgery. The evidence does not show a confirmed bypass of checksum verification; it shows stricter selection and scoping of candidate secrets. Remote exploitability is not demonstrated from the provided diff excerpts alone. Some changes in the commit, such as limiting replicated ephemeral secrets or refactoring fetchers into a provider, may also serve availability and robustness goals rather than a standalone security fix. No provided snippet demonstrates that checksum verification was previously bypassable; it shows stricter candidate selection. No supplied evidence proves secret disclosure, ciphertext forgery, or remote exploitability. Commit metadata suggests security relevance, but the vulnerability thesis is not established strongly enough to keep this as a confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `untrusted-secret-validation`
Final impact type: `integrity-risk`
Final confidence: `medium`
Final tags: `cryptography, key-management, secret-replication, integrity-checks, state-scoping`

The supplied patch evidence supports retaining this as a security-hardening case, not a confirmed vulnerability fix. The strongest code-level signal is in a security-sensitive key-manager path that explicitly treats replicated secrets as untrusted and changes selection from a single fetched value to iterating candidates until one matches the checksum chain. The tests also show proposal state becoming explicitly scoped by runtime and generation. That is meaningful integrity hardening around secret replication and state binding, but the excerpts do not prove a concrete exploitable bug, replay flaw, or signature-validation issue.

## Security Evidence

1. Master-secret recovery handles replicated values marked as untrusted and verifies them against the checksum chain before use.
2. The patch replaces one-shot fetch behavior with provider iteration over candidates, reducing acceptance/failure on a single untrusted replicated record.
3. Proposal save/load tests now bind state to both runtime_id and generation, showing tighter scoping of sensitive key-manager state.
4. The affected code is in key-manager cryptographic and replication paths, which are security-sensitive by design.

## Missing Evidence

1. No provided diff directly shows the commit-message claim about separate sealing and proposal contexts.
2. No excerpt proves that pre-patch code accepted attacker-controlled secrets or mixed proposal state across runtimes/generations in production.
3. No evidence demonstrates secret disclosure, key recovery, replay exploitation, or remote attacker reachability.
4. The bounded ephemeral-secret replication window can also be explained by robustness or performance, not standalone security impact.

## Claim Boundaries

1. Supported claim: the patch hardens validation and scoping for replicated key-manager secret state.
2. Not supported: a confirmed replay, signature-validation, or consensus-bypass vulnerability.
3. Not supported: concrete exploitability or attacker-triggered compromise from the shown excerpts alone.
4. The most defensible corpus entry is security hardening for untrusted secret replication and proposal-state binding, not a full security fix.
