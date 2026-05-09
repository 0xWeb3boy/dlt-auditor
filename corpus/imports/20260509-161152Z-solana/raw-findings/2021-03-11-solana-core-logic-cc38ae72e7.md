---
case_id: case_20210311_cc38ae72e7
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
impact_type:
  - state-integrity
confidence: medium
source_quality: high
date: 2021-03-11
source_refs:
  - git:cc38ae72e7c98fa69bfeff919254b3e1f6d0a562
  - "programs/bpf_loader/src/serialization.rs:479"
  - "programs/bpf_loader/src/serialization.rs:427"
  - "programs/bpf_loader/src/serialization.rs:126"
  - "programs/bpf_loader/src/serialization.rs:40"
bug_class: writable-account-boundary-hardening
tags:
  - blockchain-core
  - bpf-loader
  - deserialization
  - readonly-account
  - access-control
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant writable-account boundary issue in Solana's BPF loader deserialization. The supplied evidence shows that the unaligned deserializer previously copied account fields such as lamports from the program output buffer for every non-duplicate account, with no shown writable-account condition. The patch threads a skip_ro_deserialization flag through the dispatcher and gates that copy-back path on keyed_account.is_writable() or readonly deserialization being disabled.

## Observed Patch Facts

1. In `programs/bpf_loader/src/serialization.rs`, the patch adds `let de_accounts = accounts.clone();`.

2. In `programs/bpf_loader/src/serialization.rs`, the patch replaces `// check serialize_parameters_unaligned` with `let de_accounts = accounts.clone();`.

3. In `programs/bpf_loader/src/serialization.rs`, the patch replaces `start += size_of::<Pubkey>(); // pubkey` with `if keyed_account.is_writable() || !skip_ro_deserialization {`.

4. In `programs/bpf_loader/src/serialization.rs`, the patch replaces `deserialize_parameters_unaligned(keyed_accounts, buffer)` with `skip_ro_deserialization: bool,`.

## Project Context

The changed code sits primarily in `programs/bpf_loader/src`, `programs/bpf_loader`, which anchors the finding in the `core-logic` area of the project. Historical context from `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/lib.rs`. The strongest project-level identifiers around this patch are `start`, `size_of`, `buffer`, and `LittleEndian::read_u64`.

## Before/After Behavior

Before the patch, deserialize_parameters dispatched to aligned or unaligned deserialization without a readonly-skipping policy flag, and the shown unaligned path unconditionally copied serialized account state back into each non-duplicate KeyedAccount. After the patch, deserialize_parameters accepts skip_ro_deserialization and passes it through, and the shown unaligned path skips account-state copy-back for readonly accounts when that flag is enabled.

# Root Cause

The evidenced unaligned BPF loader deserialization path did not distinguish readonly from writable accounts before copying serialized output back into runtime account state. This could violate the writable-account privilege boundary if readonly deserialization skipping is enabled and no other path prevented the mutation.

## Walkthrough

1. The BPF loader deserialization dispatcher now accepts a skip_ro_deserialization boolean.

2. The dispatcher forwards that flag to both aligned and unaligned deserialization functions.

3. In the shown unaligned path, the code iterates non-duplicate keyed accounts and advances through serialized metadata.

4. Before the patch, it read lamports and continued account-state copy-back without a shown writability check.

5. After the patch, the copy-back block runs only when keyed_account.is_writable() is true or skip_ro_deserialization is false.

6. Tests were expanded to create cloned account sets with readonly and writable KeyedAccount entries for deserialization checks.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/serialization.rs | 38 | Dispatcher now accepts skip_ro_deserialization and passes it to aligned or unaligned account deserialization. |
| programs/bpf_loader/src/serialization.rs | 118 | Unaligned deserialization now applies serialized account state only when the account is writable or readonly skipping is disabled. |
| programs/bpf_loader/src/serialization.rs | 421 | Regression test setup clones accounts and marks a prefix readonly before deserialization checks. |
| programs/bpf_loader/src/serialization.rs | 473 | Regression test verifies account fields against AccountInfo and then tests deserialization with readonly accounts. |

## Code Snippets

## Snippet 1

Context: `programs/bpf_loader/src/serialization.rs:479` (changes an authorization or privilege gate)

Before
```rust
assert_eq!(account.rent_epoch, account_info.rent_epoch);
        }
    }
```
After
```rust
assert_eq!(account.rent_epoch, account_info.rent_epoch);
        }

        let de_accounts = accounts.clone();
        let de_keyed_accounts: Vec<_> = keys
            .iter()
            .zip(&de_accounts)
            .enumerate()
```

## Snippet 2

Context: `programs/bpf_loader/src/serialization.rs:427` (changes an authorization or privilege gate)

Before
```rust
}

        // check serialize_parameters_unaligned
```
After
```rust
}

        let de_accounts = accounts.clone();
        let de_keyed_accounts: Vec<_> = keys
            .iter()
            .zip(&de_accounts)
            .enumerate()
            .map(|(i, (key, account))| {
```

## Snippet 3

Context: `programs/bpf_loader/src/serialization.rs:126` (changes bounds, limits, or capacity handling)

Before
```rust
start += 1; // is_dup
        if !is_dup {
            start += size_of::<u8>(); // is_signer
            start += size_of::<u8>(); // is_writable
            start += size_of::<Pubkey>(); // pubkey
            keyed_account.try_account_ref_mut()?.lamports =
                LittleEndian::read_u64(&buffer[start..]);
            start += size_of::<u64>() // lamports
```
After
```rust
start += 1; // is_dup
        if !is_dup {
            if keyed_account.is_writable() || !skip_ro_deserialization {
                start += size_of::<u8>(); // is_signer
                start += size_of::<u8>(); // is_writable
                start += size_of::<Pubkey>(); // key
                keyed_account.try_account_ref_mut()?.lamports =
                    LittleEndian::read_u64(&buffer[start..]);
```

## Snippet 4

Context: `programs/bpf_loader/src/serialization.rs:40` (changes bounds, limits, or capacity handling)

Before
```rust
keyed_accounts: &[KeyedAccount],
    buffer: &[u8],
) -> Result<(), InstructionError> {
    if *loader_id == bpf_loader_deprecated::id() {
        deserialize_parameters_unaligned(keyed_accounts, buffer)
    } else {
        deserialize_parameters_aligned(keyed_accounts, buffer)
    }
```
After
```rust
keyed_accounts: &[KeyedAccount],
    buffer: &[u8],
    skip_ro_deserialization: bool,
) -> Result<(), InstructionError> {
    if *loader_id == bpf_loader_deprecated::id() {
        deserialize_parameters_unaligned(keyed_accounts, buffer, skip_ro_deserialization)
    } else {
        deserialize_parameters_aligned(keyed_accounts, buffer, skip_ro_deserialization)
```

# Fix Pattern

Thread an explicit readonly-deserialization policy flag to the deserialization copy-back point and enforce a writable-account gate before applying serialized account state.

## How It Was Fixed

programs/bpf_loader/src/serialization.rs changed deserialize_parameters to accept skip_ro_deserialization and pass it to loader-specific deserializers. The unaligned deserializer now wraps account-state reads and mutations in keyed_account.is_writable() || !skip_ro_deserialization. Tests add readonly KeyedAccount coverage around deserialization behavior.

# Why It Matters

1. Protects the writable-account privilege boundary in the BPF loader copy-back path.

2. Prevents readonly accounts from being treated like writable accounts in the evidenced unaligned deserializer when skipping is enabled.

3. Reduces risk that program-controlled serialized output changes account state without writable permission.

# Evidence Notes

The evidence supports a likely writable-gate security fix in the unaligned BPF loader deserialization path. The stronger claim of confirmed exploitability is not established: the snippets do not show an end-to-end attack, the exact feature activation or caller behavior, or the internal aligned deserialization gate. No cryptographic, replay, signature-verification, or memory-safety claim is supported. Protocol security invariant: After BPF execution, program-supplied serialized account state should only be copied back into runtime account state for accounts that are writable, unless readonly deserialization is explicitly allowed by policy. Verification notes: The patch does not prove that an attacker could bypass transaction-level writable-account validation end to end. The provided evidence does not show the exact feature activation path in sdk/src/feature_set.rs. The evidence does not show whether aligned deserialization has identical internal gating, only that the dispatcher passes the flag to it. No cryptographic, replay, or signature-verification invariant is shown to be changed. The patch should not be classified as memory safety without additional evidence of out-of-bounds or unsafe memory behavior. Grounded in programs/bpf_loader/src/serialization.rs dispatcher and unaligned deserializer snippets. Regression-test snippets show readonly KeyedAccount setup but not a full expected-failure or exploit case. Aligned deserialization behavior is only evidenced through flag forwarding, not internal gating. Feature activation in sdk/src/feature_set.rs is not shown in the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `writable-account-boundary-hardening`
Final tags: `blockchain-core, bpf-loader, deserialization, readonly-account, access-control`

The supplied patch evidence shows a security-sensitive tightening: BPF loader deserialization now avoids copying program-controlled serialized account state back into readonly accounts when readonly deserialization skipping is enabled. That supports retaining the case as security hardening, but the evidence does not prove an end-to-end exploitable state-corruption bug, so security-fix is too strong.

## Security Evidence

1. Deserializer now receives a skip_ro_deserialization policy flag.
2. Unaligned deserialization now gates account-state copy-back on keyed_account.is_writable() or disabled readonly skipping.
3. The copied fields include lamports and account data sourced from the serialized output buffer.
4. Tests were expanded to exercise deserialization with readonly and writable KeyedAccount entries.

## Missing Evidence

1. No commit message or advisory states this fixed a vulnerability.
2. No end-to-end exploit path shows a program mutating readonly accounts through this path.
3. Feature activation and caller behavior for skip_ro_deserialization are not shown.
4. Aligned deserialization internals are not shown, only flag forwarding.

## Claim Boundaries

1. Treat as security hardening of a writable-account boundary, not a confirmed exploit fix.
2. Do not claim cryptographic, replay, or signature-verification impact.
3. Do not claim memory-safety impact from the provided snippets.
4. State-integrity impact is plausible but not proven as an exploited vulnerability.
