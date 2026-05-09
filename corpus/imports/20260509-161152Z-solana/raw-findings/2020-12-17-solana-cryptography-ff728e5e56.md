---
case_id: case_20201217_ff728e5e56
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: medium
date: 2020-12-17
source_refs:
  - git:ff728e5e563f7aa7459f744cd330e62ea9f84964
  - "programs/bpf_loader/src/lib.rs:343"
  - "programs/bpf_loader/src/lib.rs:1552"
  - "programs/bpf_loader/src/lib.rs:521"
  - "programs/bpf_loader/src/lib.rs:229"
bug_class: rent-exemption-undercheck
impact_type:
  - economic-invariant
confidence: medium
tags:
  - blockchain-core
  - bpf-loader
  - rent-exemption
  - account-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes an undercheck in Solana's upgradeable BPF loader deploy path. Previously, the Program account rent-exemption check used the fixed `UpgradeableLoaderState::program_len()` size, even when the account's actual `data_len()` was larger. The patched code separately rejects accounts that are too small, then requires rent exemption based on `program.data_len()`.

## Observed Patch Facts

1. In `programs/bpf_loader/src/lib.rs`, the patch replaces `if program.lamports()? < rent.minimum_balance(UpgradeableLoaderState::program_len()?) {` with `if program.data_len()? < UpgradeableLoaderState::program_len()? {`.

2. In `programs/bpf_loader/src/lib.rs`, the patch replaces `// Test Insufficient payer funds` with `// Test program account not rent exempt because data is larger than needed`.

3. In `programs/bpf_loader/src/lib.rs`, the patch replaces `// Fund ProgramData to rent-exemption, spill the rest` with `for i in &mut programdata.try_account_ref_mut()?.data`.

4. In `programs/bpf_loader/src/lib.rs`, the patch replaces `let (program, offset) = if bpf_loader_upgradeable::check_id(program_id) {` with `let (program, keyed_accounts, offset) = if bpf_loader_upgradeable::check_id(program_i...`.

## Project Context

The changed code sits primarily in `programs/bpf_loader/src`, `programs/bpf_loader`, which anchors the finding in the `cryptography` area of the project. Historical context from `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/serialization.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/serialization.rs`. The strongest project-level identifiers around this patch are `program`, `UpgradeableLoaderState::program_len`, `Account::default`, and `bpf_loader_upgradeable::check_id`.

## Before/After Behavior

Before the patch, an oversized Program account could pass deployment if its lamports satisfied rent exemption for only the fixed Program loader state length. After the patch, deployment fails if the Program account is smaller than the required state size, and rent exemption is calculated over the account's actual data length.

# Root Cause

The deploy path conflated the minimum structural size of a Program account with the size that should be used for rent accounting. It checked rent against `UpgradeableLoaderState::program_len()` instead of the Program account's actual `data_len()`.

## Walkthrough

1. `DeployWithMaxDataLen` verifies the Program account before initializing upgradeable program state.

2. The unchanged first check rejects Program accounts that are already initialized.

3. Before the fix, the rent check used `rent.minimum_balance(UpgradeableLoaderState::program_len()?)`.

4. That allowed accounts with larger actual data allocations to be assessed against a smaller fixed size.

5. The patch adds an explicit `program.data_len() < UpgradeableLoaderState::program_len()?` guard that returns `AccountDataTooSmall`.

6. The patch then checks `program.lamports()` against `rent.minimum_balance(program.data_len()?)`.

7. The added test covers a Program account that is larger than needed but not rent-exempt for its actual size.

8. The ProgramData trailing-byte zeroing appears to be adjacent hygiene and is not established as the root vulnerability by the supplied evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/lib.rs | 343 | DeployWithMaxDataLen verifies Program account size and rent exemption before initializing upgradeable program state. |
| programs/bpf_loader/src/lib.rs | 521 | ProgramData deployment copy path zeroes trailing bytes after copied buffer data. |
| programs/bpf_loader/src/lib.rs | 229 | Upgradeable executable dispatch path resolves Program state and associated ProgramData account for execution. |
| programs/bpf_loader/src/lib.rs | 1552 | Regression test for oversized program account that is not rent-exempt for its actual data length. |

## Code Snippets

## Snippet 1

Context: `programs/bpf_loader/src/lib.rs:343` (changes aggregate state or economic accounting)

Before
```rust
return Err(InstructionError::AccountAlreadyInitialized);
            }

            if program.lamports()? < rent.minimum_balance(UpgradeableLoaderState::program_len()?) {
                log!(logger, "Program account not rent-exempt");
                return Err(InstructionError::ExecutableAccountNotRentExempt);
```
After
```rust
return Err(InstructionError::AccountAlreadyInitialized);
            }
            if program.data_len()? < UpgradeableLoaderState::program_len()? {
                log!(logger, "Program account too small");
                return Err(InstructionError::AccountDataTooSmall);
            }
            if program.lamports()? < rent.minimum_balance(program.data_len()?) {
                log!(logger, "Program account not rent-exempt");
```

## Snippet 2

Context: `programs/bpf_loader/src/lib.rs:1552` (changes the branch that decides whether execution stops or continues)

Before
```rust
);

        // Test Insufficient payer funds
        bank.clear_signatures();
```
After
```rust
);

        // Test program account not rent exempt because data is larger than needed
        bank.clear_signatures();
        bank.store_account(&buffer_address, &buffer_account);
        bank.store_account(&program_keypair.pubkey(), &Account::default());
        bank.store_account(&programdata_address, &Account::default());
        let mut instructions = bpf_loader_upgradeable::deploy_with_max_program_len(
```

## Snippet 3

Context: `programs/bpf_loader/src/lib.rs:521` (changes a sensitive control or state-update path)

Before
```rust
[programdata_data_offset..programdata_data_offset + buffer_data_len]
                .copy_from_slice(&buffer.try_account_ref()?.data[buffer_data_offset..]);

            // Fund ProgramData to rent-exemption, spill the rest
```
After
```rust
[programdata_data_offset..programdata_data_offset + buffer_data_len]
                .copy_from_slice(&buffer.try_account_ref()?.data[buffer_data_offset..]);
            for i in &mut programdata.try_account_ref_mut()?.data
                [programdata_data_offset + buffer_data_len..]
            {
                *i = 0
            }
```

## Snippet 4

Context: `programs/bpf_loader/src/lib.rs:229` (changes a sensitive control or state-update path)

Before
```rust
let first_account = next_keyed_account(account_iter)?;
    if first_account.executable()? {
        let (program, offset) = if bpf_loader_upgradeable::check_id(program_id) {
            if let UpgradeableLoaderState::Program {
                programdata_address,
```
After
```rust
let first_account = next_keyed_account(account_iter)?;
    if first_account.executable()? {
        let (program, keyed_accounts, offset) = if bpf_loader_upgradeable::check_id(program_id) {
            if let UpgradeableLoaderState::Program {
                programdata_address,
```

# Fix Pattern

Separate minimum layout validation from economic/accounting validation, and compute rent exemption from the actual account allocation.

## How It Was Fixed

The upgradeable loader deploy path now first validates that the Program account data length is at least `UpgradeableLoaderState::program_len()`, then computes the rent-exempt minimum balance using `program.data_len()` instead of the fixed loader state length. Regression coverage was added for the oversized, underfunded Program account case.

# Why It Matters

1. Preserves rent-exemption accounting for initialized Program accounts.

2. Prevents oversized Program accounts from being deployed with lamports calculated for only the minimum loader state size.

3. Keeps the deploy-time account invariant aligned with later executable loader use.

4. Evidence does not support stronger claims such as arbitrary code execution, privilege escalation, or information disclosure.

# Evidence Notes

The strongest evidence is the direct guard change in `programs/bpf_loader/src/lib.rs`: the rent check changed from `UpgradeableLoaderState::program_len()` to `program.data_len()`, with a new `AccountDataTooSmall` guard. The test label explicitly describes a Program account that is not rent-exempt because its data is larger than needed. The cryptography framing from the heuristic baseline is unsupported. The zeroing change is not enough to claim a separate disclosure issue. Protocol security invariant: Upgradeable BPF Program accounts should only be initialized when they are large enough to hold the loader Program state and rent-exempt for their actual allocated data length. Verification notes: The patch does not prove arbitrary code execution or privilege escalation. The patch does not show that rent collection would actually reclaim or corrupt an executable account in practice. The zeroing change is not enough by itself to prove an information disclosure bug from the provided context. The evidence supports an account-rent invariant violation, not a cryptography issue. Supported by implementation diff in the upgradeable loader deploy path. Supported by added regression test scenario for oversized underfunded Program accounts. Security impact is bounded to a protocol rent-exemption invariant violation. No evidence provided for arbitrary execution, privilege escalation, corruption, or data disclosure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `rent-exemption-undercheck`
Final impact type: `economic-invariant`
Final confidence: `medium`
Final tags: `blockchain-core, bpf-loader, rent-exemption, account-validation, security-hardening`

The supplied patch evidence supports a security-hardening classification, not a concrete security-fix. The loader deploy path now rejects too-small Program accounts and computes rent exemption from the Program account's actual data length, closing an undercheck in a blockchain runtime account invariant. The original cryptography, signature, and state-corruption framing is unsupported by the provided evidence.

## Security Evidence

1. Deploy validation changed from rent based on fixed UpgradeableLoaderState::program_len() to rent based on program.data_len().
2. A new guard rejects Program accounts whose data length is smaller than the required Program state length.
3. Regression test explicitly covers a Program account that is larger than needed but not rent-exempt for its actual size.
4. The affected code is in the upgradeable BPF loader, a security-sensitive blockchain runtime path.

## Missing Evidence

1. No evidence shows arbitrary code execution, privilege escalation, consensus failure, or account takeover.
2. No evidence proves that an underfunded executable Program account would be reclaimed or corrupted in practice.
3. The ProgramData trailing-byte zeroing is not tied to a demonstrated information disclosure issue.
4. The provided context does not support classifying this as cryptography or signature-related.

## Claim Boundaries

1. Validate only as rent-exemption/account-validation hardening in the upgradeable BPF loader.
2. Do not claim a concrete exploit or direct fund theft from the supplied patch alone.
3. Do not treat the zeroing change as a separate proven confidentiality fix.
4. Do not retain the original state-corruption or cryptography framing.
