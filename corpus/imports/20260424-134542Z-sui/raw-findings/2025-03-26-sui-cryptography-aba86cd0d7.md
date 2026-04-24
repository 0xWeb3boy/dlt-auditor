---
case_id: case_20250326_aba86cd0d7
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2025-03-26
source_refs:
  - git:aba86cd0d7783798b7ba4004470e43330395634d
  - "crates/sui-types/src/object.rs:546"
  - "crates/sui-transaction-checks/src/lib.rs:549"
  - "crates/sui-types/src/programmable_transaction_builder.rs:233"
  - "crates/sui-transaction-checks/src/lib.rs:473"
bug_class: missing-consensus-object-ownership-authentication
impact_type:
  - unauthorized-object-use
  - transaction-input-authorization-bypass
confidence: medium
tags:
  - blockchain-core
  - consensus
  - authentication
  - access-control
  - transaction-validation
  - object-ownership
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely security fix in Sui transaction input validation for ConsensusV2 objects. The commit message says object ownership is now verified at signing time, and the diff adds access to ConsensusV2 authenticator metadata while separating ConsensusV2 handling from ordinary shared-object version checks. The stronger claims about replay, generic signature forgery, consensus finality, or a demonstrated exploit are not supported by the provided evidence.

## Observed Patch Facts

1. In `crates/sui-types/src/object.rs`, the patch replaces `pub fn is_immutable(&self) -> bool {` with `// Returns the object's Authenticator, if it has one.`.

2. In `crates/sui-transaction-checks/src/lib.rs`, the patch replaces `| Owner::ConsensusV2 {` with `input_initial_shared_version == *actual_initial_shared_version,`.

3. In `crates/sui-types/src/programmable_transaction_builder.rs`, the patch replaces `pub fn transfer_sui(&mut self, recipient: SuiAddress, amount: Option<u64>) {` with `// TODO: Merge with 'transfer_object' above and update existing callers.`.

4. In `crates/sui-transaction-checks/src/lib.rs`, the patch replaces `error: format!("Object {:?} is owned by account address {:?}, but given owner/signer...` with `error: format!("Object {object_id:?} is owned by account address {actual_owner:?}, bu...`.

## Project Context

The changed code sits primarily in `crates/sui-types/src`, `crates/sui-types`, `crates/sui-transaction-checks/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-types/src/authenticator_state.rs`, `crates/sui-types/src/zk_login_authenticator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/transaction.rs`, `crates/sui-types/src/sui_sdk_types_conversions.rs`. The strongest project-level identifiers around this patch are `owner`, `Owner::ConsensusV2`, `authenticator`, and `actual_initial_shared_version`. Nearby tests or test-like files include `crates/sui-types/src/unit_tests/zk_login_authenticator_test.rs`, `crates/sui-types/src/unit_tests/passkey_authenticator_test.rs`.

## Before/After Behavior

Before the patch, the shown transaction-check logic grouped `Owner::ConsensusV2` with `Owner::Shared` for a start-version comparison, and the provided `Owner` helpers did not show a way to retrieve ConsensusV2 authenticator metadata. After the patch, `Owner::authenticator()` returns authenticator metadata for `Owner::ConsensusV2`, and the transaction-check path separates ConsensusV2 handling from the shared-object branch. The provided evidence indicates this is intended to verify object ownership at signing/input-check time, but it does not show the full final validation expression.

# Root Cause

ConsensusV2-owned objects appear to have lacked a dedicated signing/input-time ownership or authenticator validation path; the visible pre-patch handling treated them like shared objects for start-version checking.

## Walkthrough

1. A transaction input object reaches `check_one_object` in `crates/sui-transaction-checks/src/lib.rs`, which validates object kind, version, digest, and ownership-related properties.

2. For address-owned objects, the surrounding code already checks that the supplied signer/owner matches the actual object owner.

3. The pre-patch evidence shows `Owner::ConsensusV2` grouped with `Owner::Shared` for an initial/start-version comparison.

4. That evidence does not show a ConsensusV2-specific check against authenticator metadata before the patch.

5. The patch adds `Owner::authenticator()` in `crates/sui-types/src/object.rs`, returning metadata only for `Owner::ConsensusV2`.

6. The transaction-check code separates `Owner::ConsensusV2` from the shared-object branch and includes access to `authenticator`, consistent with the commit message's stated signing-time ownership verification.

7. The programmable transaction builder addition for `FullObjectRef` is supporting transaction construction code, not the root cause by itself.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-types/src/object.rs | 546 | adds access to ConsensusV2 owner authenticator metadata used by validation |
| crates/sui-transaction-checks/src/lib.rs | 549 | separates ConsensusV2 object handling from Shared object checks and validates ConsensusV2-specific ownership/authenticator state |
| crates/sui-types/src/programmable_transaction_builder.rs | 233 | adds full object reference construction path for programmable transaction inputs including non-fastpath object ownership forms |
| crates/sui-transaction-checks/src/lib.rs | 421 | transaction input object ownership validation path where signer/owner checks are enforced |

## Code Snippets

## Snippet 1

Context: `crates/sui-types/src/object.rs:546` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    pub fn is_immutable(&self) -> bool {
        matches!(self, Owner::Immutable)
```
After
```rust
}

    // Returns the object's Authenticator, if it has one.
    pub fn authenticator(&self) -> Option<&Authenticator> {
        match self {
            Self::ConsensusV2 { authenticator, .. } => Some(authenticator.as_ref()),
            Self::Immutable
            | Self::AddressOwner(_)
```

## Snippet 2

Context: `crates/sui-transaction-checks/src/lib.rs:549` (changes an authorization or privilege gate)

Before
```rust
Owner::Shared {
                        initial_shared_version: actual_initial_shared_version,
                    }
                    | Owner::ConsensusV2 {
                        start_version: actual_initial_shared_version,
                        ..
                    } => {
                        fp_ensure!(
```
After
```rust
Owner::Shared {
                        initial_shared_version: actual_initial_shared_version,
                    } => {
                        fp_ensure!(
                            input_initial_shared_version == *actual_initial_shared_version,
                            UserInputError::SharedObjectStartingVersionMismatch
                        )
                    }
```

## Snippet 3

Context: `crates/sui-types/src/programmable_transaction_builder.rs:233` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    pub fn transfer_sui(&mut self, recipient: SuiAddress, amount: Option<u64>) {
        let rec_arg = self.pure(recipient).unwrap();
```
After
```rust
}

    // TODO: Merge with `transfer_object` above and update existing callers.
    pub fn transfer_object_full(
        &mut self,
        recipient: SuiAddress,
        full_object_ref: FullObjectRef,
    ) -> anyhow::Result<()> {
```

## Snippet 4

Context: `crates/sui-transaction-checks/src/lib.rs:473` (changes an authorization or privilege gate)

Before
```rust
owner == &actual_owner,
                        UserInputError::IncorrectUserSignature {
                            error: format!("Object {:?} is owned by account address {:?}, but given owner/signer address is {:?}", object_id, actual_owner, owner),
                        }
                    );
```
After
```rust
owner == &actual_owner,
                        UserInputError::IncorrectUserSignature {
                            error: format!("Object {object_id:?} is owned by account address {actual_owner:?}, but given owner/signer address is {owner:?}"),
                        }
                    );
```

# Fix Pattern

Expose owner authenticator metadata and use a ConsensusV2-specific transaction input validation path instead of relying only on shared-object start-version checks.

## How It Was Fixed

The patch adds an `Owner::authenticator()` accessor for ConsensusV2 ownership metadata and changes transaction input checking so `Owner::ConsensusV2` is handled separately from `Owner::Shared`. Based on the commit message and changed code shape, this adds signing/input-time object ownership authentication for ConsensusV2 objects.

# Why It Matters

1. ConsensusV2 objects carry ownership/authenticator metadata that should constrain who can submit them as transaction inputs.

2. A start-version comparison alone is not evidence of ownership authentication.

3. Rejecting invalid object inputs before execution protects transaction admission and state-transition authorization.

4. The evidence does not establish replay, signature forgery, or consensus-finality impact.

# Evidence Notes

Strongest evidence is the commit text: `Verify object ownership at signing time`, plus the subject `Implement authentication checks for ConsensusV2 objects`. Code evidence shows `Owner::authenticator()` added for `Self::ConsensusV2`, and transaction checks separating `Owner::ConsensusV2` from `Owner::Shared`. The actual full post-patch validation logic is not included in the snippets, so confidence is medium rather than high. The error formatting change is not security-relevant. The `transfer_object_full` builder change appears supportive unless further evidence shows it is the root cause. Protocol security invariant: ConsensusV2 object inputs should be checked against the actual on-chain ownership/authenticator metadata during transaction signing or input validation, rather than being accepted based only on shared-object-style start-version matching. Verification notes: No concrete exploit transaction is shown in the provided evidence. No proof is provided that consensus safety or finality could be violated. No post-execution authorization bypass is shown; the commit says no post-execution checks are currently needed. The patch does not prove generic signature forgery or replay beyond missing ConsensusV2 object authentication at signing/input-check time. The formatting-only error message change is not itself security-relevant. No concrete exploit transaction is provided. No proof of consensus safety or finality impact is provided. No post-execution authorization bypass is shown; the commit says post-execution checks are not currently needed. The security finding is bounded to missing or incomplete ConsensusV2 object ownership validation at signing/input-check time. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-consensus-object-ownership-authentication`
Final impact type: `unauthorized-object-use, transaction-input-authorization-bypass`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, authentication, access-control, transaction-validation, object-ownership`

The supplied evidence supports keeping this as security hardening, not a fully proven security fix. The commit explicitly says it verifies object ownership at signing time and implements authentication checks for ConsensusV2 objects, and the patch exposes ConsensusV2 authenticator metadata while separating ConsensusV2 from ordinary shared-object validation. However, the snippets do not show the complete final validation expression, a concrete bypass, or demonstrated exploitability, so replay/signature-forgery claims are too specific.

## Security Evidence

1. Commit subject states authentication checks were implemented for ConsensusV2 objects.
2. Commit body states object ownership is verified at signing time.
3. Owner::authenticator() was added and returns authenticator metadata only for ConsensusV2 owners.
4. Transaction checks separate ConsensusV2 handling from the shared-object start-version branch.
5. The touched path is transaction input/object ownership validation.

## Missing Evidence

1. Full post-patch ConsensusV2 validation logic is not shown in the supplied snippets.
2. No regression test excerpt demonstrates rejection of an unauthorized ConsensusV2 object use.
3. No exploit transaction or proof of a prior authorization bypass is provided.
4. No evidence supports replay, generic signature forgery, or consensus-finality impact.

## Claim Boundaries

1. Validate as security hardening for ConsensusV2 object ownership/authentication checks.
2. Do not claim a proven replay vulnerability from the supplied evidence.
3. Do not claim generic signature forgery from the supplied evidence.
4. Do not treat formatting-only error message changes as security evidence.
5. Do not infer post-execution authorization impact; the commit says no post-execution checks are currently needed.
