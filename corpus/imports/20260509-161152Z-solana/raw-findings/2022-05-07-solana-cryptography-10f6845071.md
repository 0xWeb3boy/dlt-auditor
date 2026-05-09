---
case_id: case_20220507_10f6845071
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2022-05-07
source_refs:
  - git:10f6845071d74460ba1afd52cf8b6af5ef859771
  - "sdk/src/transaction/versioned.rs:47"
  - "sdk/program/src/message/versions/mod.rs:156"
  - "sdk/src/transaction/versioned.rs:91"
  - "rpc/src/rpc.rs:4303"
bug_class: improper-transaction-sanitization
impact_type:
  - security-policy-bypass
confidence: medium
tags:
  - blockchain-core
  - transaction-sanitization
  - versioned-transactions
  - address-lookup-table
  - program-id-validation
  - rpc
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes versioned transaction sanitization to carry an explicit require_static_program_ids policy and makes the shown RPC transaction sanitization path pass true for that policy. This supports a likely security fix for rejecting v0 transactions where program dispatch identity depends on lookup-table-loaded addresses, but the provided snippets do not show the full v0 sanitizer or prove an exploit.

## Observed Patch Facts

1. In `sdk/src/transaction/versioned.rs`, the patch replaces `impl Sanitize for VersionedTransaction {` with `impl From<Transaction> for VersionedTransaction {`.

2. In `sdk/program/src/message/versions/mod.rs`, the patch replaces `impl Sanitize for VersionedMessage {` with `impl Serialize for VersionedMessage {`.

3. In `sdk/src/transaction/versioned.rs`, the patch replaces `/// Returns the version of the transaction` with `pub fn sanitize(`.

4. In `rpc/src/rpc.rs`, the patch replaces `SanitizedTransaction::try_create(transaction, MessageHash::Compute, None, address_loa...` with `SanitizedTransaction::try_create(`.

## Project Context

The changed code sits primarily in `sdk/src/transaction`, `sdk/src`, `sdk/program/src/message/versions`, which anchors the finding in the `cryptography` area of the project. Historical context from `sdk/src/transaction/sanitized.rs`, `rpc/src/transaction_status_service.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rpc/src/transaction_status_service.rs`, `sdk/src/transaction/sanitized.rs`. The strongest project-level identifiers around this patch are `message`, `sanitize`, `std::result::Result`, and `SanitizedTransaction::try_create`.

## Before/After Behavior

Before the patch, the shown VersionedTransaction and VersionedMessage sanitization used generic Sanitize trait paths without an explicit static-program-id policy argument. After the patch, VersionedTransaction has sanitize(require_static_program_ids), forwards that flag into message sanitization, preserves signature-count checks, and the shown RPC sanitize_transaction path calls SanitizedTransaction::try_create with true for require_static_program_ids.

# Root Cause

The supported root cause is an incomplete sanitization policy boundary: the versioned transaction/message sanitization path shown did not carry a caller requirement that instruction program ids remain static message keys when that property was required.

## Walkthrough

1. A versioned transaction may use address lookup tables to load additional account keys.

2. Instruction program ids determine program dispatch and are therefore sensitive transaction metadata.

3. The earlier shown sanitization integration did not expose a require_static_program_ids policy at the VersionedTransaction sanitize boundary.

4. The patch adds an explicit policy parameter and forwards it into message sanitization before retaining the existing signature-count validation.

5. The shown RPC sanitization path now passes true for require_static_program_ids into SanitizedTransaction::try_create.

6. Based on the commit subject and the new policy threading, transactions using lookup-table-loaded program ids are intended to fail sanitization when static program ids are required.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/src/transaction/versioned.rs | 91 | Adds explicit VersionedTransaction::sanitize(require_static_program_ids) entry point and preserves signature-count validation after message sanitization. |
| sdk/program/src/message/versions/mod.rs | 156 | Routes versioned message sanitization to the concrete legacy or v0 message sanitizer where static-program-id policy can be applied. |
| rpc/src/rpc.rs | 4303 | RPC transaction sanitization calls SanitizedTransaction::try_create with require_static_program_ids set to true, rejecting transactions whose instruction program id depends on lookup-table loading. |
| sdk/src/transaction/sanitized.rs | 1 | Surrounding sanitized transaction creation path that loads address-table keys and constructs the executable transaction representation. |

## Code Snippets

## Snippet 1

Context: `sdk/src/transaction/versioned.rs:47` (changes a sensitive control or state-update path)

Before
```rust
}

impl Sanitize for VersionedTransaction {
    fn sanitize(&self) -> std::result::Result<(), SanitizeError> {
        self.message.sanitize()?;

        let num_required_signatures = usize::from(self.message.header().num_required_signatures);
        match num_required_signatures.cmp(&self.signatures.len()) {
```
After
```rust
}

impl From<Transaction> for VersionedTransaction {
    fn from(transaction: Transaction) -> Self {
```

## Snippet 2

Context: `sdk/program/src/message/versions/mod.rs:156` (changes a sensitive control or state-update path)

Before
```rust
}

impl Sanitize for VersionedMessage {
    fn sanitize(&self) -> Result<(), SanitizeError> {
        match self {
            Self::Legacy(message) => message.sanitize(),
            Self::V0(message) => message.sanitize(),
        }
```
After
```rust
}

impl Serialize for VersionedMessage {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
```

## Snippet 3

Context: `sdk/src/transaction/versioned.rs:91` (changes a sensitive control or state-update path)

Before
```rust
}

    /// Returns the version of the transaction
    pub fn version(&self) -> TransactionVersion {
```
After
```rust
}

    pub fn sanitize(
        &self,
        require_static_program_ids: bool,
    ) -> std::result::Result<(), SanitizeError> {
        self.message.sanitize(require_static_program_ids)?;
```

## Snippet 4

Context: `rpc/src/rpc.rs:4303` (changes a sensitive control or state-update path)

Before
```rust
address_loader: impl AddressLoader,
) -> Result<SanitizedTransaction> {
    SanitizedTransaction::try_create(transaction, MessageHash::Compute, None, address_loader)
        .map_err(|err| Error::invalid_params(format!("invalid transaction: {}", err)))
}
```
After
```rust
address_loader: impl AddressLoader,
) -> Result<SanitizedTransaction> {
    SanitizedTransaction::try_create(
        transaction,
        MessageHash::Compute,
        None,
        address_loader,
        true, // require_static_program_ids
```

# Fix Pattern

Thread an explicit validation policy through transaction/message sanitization and set it at the boundary that creates sanitized transaction representations.

## How It Was Fixed

The patch adds VersionedTransaction::sanitize(require_static_program_ids: bool), calls self.message.sanitize(require_static_program_ids), keeps the required-signature-count validation, and updates the shown RPC sanitize_transaction helper to call SanitizedTransaction::try_create with require_static_program_ids set to true.

# Why It Matters

1. Program dispatch identity is security-sensitive.

2. Lookup tables should not supply executable program targets when static program ids are required.

3. The evidence supports a sanitization rejection rule, not signature forgery, replay, or demonstrated fund loss.

4. Reachability beyond the shown RPC/sanitization path is not established by the snippets.

# Evidence Notes

Grounded evidence includes sdk/src/transaction/versioned.rs showing the new sanitize(require_static_program_ids) method, rpc/src/rpc.rs passing true with the require_static_program_ids comment, and the commit subject stating that transaction sanitization should fail when an instruction program id uses a lookup table. The provided evidence does not include the full v0 message sanitizer implementation, a concrete exploit transaction, validator-wide reachability, or demonstrated financial impact. Protocol security invariant: When static program ids are required, transaction sanitization must reject a versioned transaction whose instruction program id is supplied through an address lookup table rather than the static message account keys. Verification notes: The patch does not prove signature forgery or replay by itself. The patch does not show a concrete exploit transaction or demonstrated fund loss. The evidence does not establish whether the issue was reachable on all validator execution paths versus specific RPC/sanitization paths. The provided snippets do not show the full v0 message sanitizer implementation, only its integration points. Do not classify this as cryptography, replay, or signature validation based on the provided evidence. The strongest supported subsystem is transaction sanitization for versioned messages/address lookup tables. Confidence is medium because the key enforcement implementation is inferred from integration points and commit text, not shown directly. Keep in the security corpus as a likely security fix rather than confirmed exploit remediation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-transaction-sanitization`
Final impact type: `security-policy-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-sanitization, versioned-transactions, address-lookup-table, program-id-validation, rpc`

The supplied evidence supports retaining this as security hardening, not as a proven security fix. The commit explicitly makes transaction sanitization fail when an instruction program id comes from a lookup table, and the patch threads a require_static_program_ids policy into versioned transaction sanitization with at least one RPC boundary passing true. That tightens a security-sensitive transaction validation invariant, but the snippets do not show the concrete v0 enforcement logic, an exploit, validator-wide reachability, or a replay/signature-validation flaw.

## Security Evidence

1. Commit subject states that transaction sanitization should fail when an instruction program id uses a lookup table.
2. VersionedTransaction gains sanitize(require_static_program_ids) and forwards the policy into message sanitization.
3. RPC sanitize_transaction passes true for require_static_program_ids into SanitizedTransaction::try_create.
4. Instruction program ids control dispatch identity, making lookup-table-sourced program ids a security-sensitive validation condition.

## Missing Evidence

1. Full v0 message sanitizer implementation is not shown.
2. No concrete malformed transaction or exploit path is provided.
3. No demonstrated replay, signature forgery, fund loss, or authorization bypass is shown.
4. Evidence does not prove the issue was reachable on all validator execution paths.

## Claim Boundaries

1. Classify as transaction sanitization hardening, not cryptographic signature validation.
2. Do not claim replay or request forgery impact from the supplied patch alone.
3. Do not claim confirmed exploit remediation or financial impact.
4. Supported claim is rejection of lookup-table-loaded program ids where static program ids are required.
