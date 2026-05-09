---
case_id: case_20210129_07cef5a557
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2021-01-29
source_refs:
  - git:07cef5a5572251f9b33de74e8ddd9897ed380406
  - "programs/bpf_loader/src/lib.rs:515"
  - "programs/bpf_loader/src/lib.rs:619"
  - "cli/src/program.rs:400"
  - "programs/bpf_loader/src/lib.rs:1680"
bug_class: authorization-invariant-enforcement
impact_type:
  - access-control
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - upgradeable-loader
  - authority-check
  - access-control
  - feature-gated
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds an on-chain authorization consistency check in Solana's upgradeable BPF loader. The loader now rejects deploy or upgrade processing when the buffer account's recorded authority does not match the supplied upgrade/deploy authority, and it prevents clearing buffer authority to None under the same feature gate.

## Observed Patch Facts

1. In `programs/bpf_loader/src/lib.rs`, the patch replaces `if let UpgradeableLoaderState::Buffer {` with `if let UpgradeableLoaderState::Buffer { authority_address } = buffer.state()? {`.

2. In `programs/bpf_loader/src/lib.rs`, the patch replaces `if authority_address == None {` with `if invoke_context.is_feature_active(&matching_buffer_upgrade_authorities::id())`.

3. In `cli/src/program.rs`, the patch replaces `let new_buffer_authority = if matches.is_present("final") {` with `let new_buffer_authority = if let Some(new_buffer_authority) =`.

4. In `programs/bpf_loader/src/lib.rs`, the patch replaces `assert!(bank_client` with `assert_eq!(`.

## Project Context

The changed code sits primarily in `programs/bpf_loader/src`, `programs/bpf_loader`, `cli/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/serialization.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/serialization.rs`. The strongest project-level identifiers around this patch are `UpgradeableLoaderState::Buffer`, `new_buffer_authority`, `Buffer`, and `matching_buffer_upgrade_authorities::id`.

## Before/After Behavior

Before the patch, the loader verified that the account was an UpgradeableLoaderState::Buffer but ignored its authority_address in the shown deploy/upgrade validation path. After the patch, it captures authority_address and, when matching_buffer_upgrade_authorities is active, returns InstructionError::IncorrectAuthority if it is not Some(*authority.unsigned_key()). The related SetAuthority path previously treated authority_address == None as an immutable-buffer condition; after the patch it rejects new_authority == None while the feature is active. The CLI also stops producing the shown final/None buffer-authority path and resolves a concrete new buffer authority.

# Root Cause

The upgradeable loader accepted a buffer based on its account state without enforcing that the buffer's stored authority matched the authority used for the sensitive deploy or upgrade operation. The related ability to clear buffer authority to None would also make the new comparison unenforceable, so the patch blocks that state under the feature gate.

## Walkthrough

1. A deploy or upgrade instruction enters the upgradeable loader instruction processor.

2. The pre-patch buffer check accepted any UpgradeableLoaderState::Buffer in the shown path and discarded authority_address.

3. The patch reads authority_address from the buffer state.

4. If matching_buffer_upgrade_authorities is active and the buffer authority differs from the supplied authority key, the loader logs the mismatch and returns IncorrectAuthority.

5. The SetAuthority path also rejects setting a buffer authority to None while the feature is active.

6. Regression evidence shows a mismatched-authority deploy case changed from expected success to expected failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/lib.rs | 515 | Upgradeable loader deploy/upgrade buffer verification now checks buffer authority against the upgrade authority and rejects mismatches. |
| programs/bpf_loader/src/lib.rs | 619 | Upgradeable loader SetAuthority handling rejects clearing buffer authority when the matching-authorities feature is active. |
| cli/src/program.rs | 400 | Client command parsing stops producing a None/final buffer authority and instead requires/selects a concrete new buffer authority. |
| programs/bpf_loader/src/lib.rs | 1680 | Regression coverage changes expected behavior from successful deploy with mismatched authority to IncorrectAuthority failure. |

## Code Snippets

## Snippet 1

Context: `programs/bpf_loader/src/lib.rs:515` (changes bounds, limits, or capacity handling)

Before
```rust
// Verify Buffer account

            if let UpgradeableLoaderState::Buffer {
                authority_address: _,
            } = buffer.state()?
            {
            } else {
                ic_logger_msg!(logger, "Invalid Buffer account");
```
After
```rust
// Verify Buffer account

            if let UpgradeableLoaderState::Buffer { authority_address } = buffer.state()? {
                if invoke_context.is_feature_active(&matching_buffer_upgrade_authorities::id()) {
                    if authority_address != Some(*authority.unsigned_key()) {
                        ic_logger_msg!(logger, "Buffer and upgrade authority don't match");
                        return Err(InstructionError::IncorrectAuthority);
                    }
```

## Snippet 2

Context: `programs/bpf_loader/src/lib.rs:619` (changes bounds, limits, or capacity handling)

Before
```rust
match account.state()? {
                UpgradeableLoaderState::Buffer { authority_address } => {
                    if authority_address == None {
                        ic_logger_msg!(logger, "Buffer is immutable");
```
After
```rust
match account.state()? {
                UpgradeableLoaderState::Buffer { authority_address } => {
                    if invoke_context.is_feature_active(&matching_buffer_upgrade_authorities::id())
                        && new_authority == None
                    {
                        ic_logger_msg!(logger, "Buffer authority is not optional");
                        return Err(InstructionError::IncorrectAuthority);
                    }
```

## Snippet 3

Context: `cli/src/program.rs:400` (changes the branch that decides whether execution stops or continues)

Before
```rust
let (buffer_authority_signer, buffer_authority_pubkey) =
                signer_of(matches, "buffer_authority", wallet_manager)?;
            let new_buffer_authority = if matches.is_present("final") {
                None
            } else if let Some(new_buffer_authority) =
                pubkey_of_signer(matches, "new_buffer_authority", wallet_manager)?
            {
                Some(new_buffer_authority)
```
After
```rust
let (buffer_authority_signer, buffer_authority_pubkey) =
                signer_of(matches, "buffer_authority", wallet_manager)?;
            let new_buffer_authority = if let Some(new_buffer_authority) =
                pubkey_of_signer(matches, "new_buffer_authority", wallet_manager)?
            {
                new_buffer_authority
            } else {
                let (_, new_buffer_authority) =
```

## Snippet 4

Context: `programs/bpf_loader/src/lib.rs:1680` (changes an authorization or privilege gate)

Before
```rust
Some(&mint_keypair.pubkey()),
        );
        assert!(bank_client
            .send_and_confirm_message(&[&mint_keypair, &program_keypair], message)
            .is_ok());
        assert_eq!(None, bank.get_account(&buffer_address));
        let post_program_account = bank.get_account(&program_keypair.pubkey()).unwrap();
        assert_eq!(post_program_account.lamports, min_program_balance);
```
After
```rust
Some(&mint_keypair.pubkey()),
        );
        assert_eq!(
            TransactionError::InstructionError(1, InstructionError::Custom(0)),
            bank_client
                .send_and_confirm_message(
                    &[&mint_keypair, &program_keypair, &upgrade_authority_keypair],
                    message
```

# Fix Pattern

Enforce the authority invariant at the on-chain loader boundary by comparing persisted buffer authority against the operation authority before continuing, and prevent state transitions that would remove the authority needed for that check.

## How It Was Fixed

The loader now captures buffer authority_address during buffer validation and checks it against authority.unsigned_key() under matching_buffer_upgrade_authorities. It returns InstructionError::IncorrectAuthority on mismatch. The buffer SetAuthority path rejects None as a new authority under the same feature, CLI command handling was aligned to use a concrete authority, and tests were updated for mismatched-authority failure.

# Why It Matters

1. The changed code is in the upgradeable BPF loader, a critical program deploy and upgrade path.

2. The added check is an access-control invariant, not a refactor or cleanup.

3. The strongest supported impact is prevention of mismatched-authority deploy/upgrade buffer use.

4. The evidence does not prove fund theft or unauthorized upgrade without any required signer.

5. Behavior depends on activation of the matching_buffer_upgrade_authorities feature.

# Evidence Notes

Grounded evidence comes from programs/bpf_loader/src/lib.rs around the buffer validation block, where authority_address is now compared to Some(*authority.unsigned_key()) and mismatches return IncorrectAuthority; the SetAuthority block, where new_authority == None is rejected under the feature; cli/src/program.rs, where the final/None buffer-authority branch is removed in the shown command handling; and tests that now expect failure for a mismatched-authority deploy scenario. Claims about non-upgradeable loaders, complete exploitability, fund theft, or bypassing all signer requirements are not supported by the provided evidence. Protocol security invariant: When the matching_buffer_upgrade_authorities feature is active, an upgradeable BPF deploy or upgrade must use a buffer whose stored authority matches the authority supplied for the deploy or upgrade operation. Buffer authority must remain concrete so the loader can enforce that comparison. Verification notes: The patch evidence does not prove that an attacker could steal funds or upgrade a program without any required signer. The patch evidence does not show impact on non-upgradeable BPF loaders. The feature gate means behavior depends on activation of matching_buffer_upgrade_authorities. The CLI change alone is not the security boundary; the on-chain loader check is the relevant enforcement point. Verified from provided diff excerpts only. No external files, commands, or repository inspection used. Security classification rests on the new on-chain IncorrectAuthority check and regression expectation for mismatched authority. Feature-gated behavior should be preserved in any corpus labeling. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authorization-invariant-enforcement`
Final impact type: `access-control, state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, upgradeable-loader, authority-check, access-control, feature-gated`

The supplied patch clearly adds an on-chain authority consistency check in the upgradeable BPF loader and changes a mismatched-authority deploy path from success to IncorrectAuthority failure. That is security-relevant access-control hardening. However, the evidence does not prove a full unauthorized program upgrade, signer bypass, or state corruption impact, so the original confirmed security-fix/state-corruption/high framing is too strong for the corpus.

## Security Evidence

1. Deploy/upgrade buffer validation now reads authority_address and rejects when it differs from the supplied authority under matching_buffer_upgrade_authorities.
2. The SetAuthority path rejects clearing buffer authority to None while the same feature is active, preserving the enforceable authority invariant.
3. Regression evidence shows a previously successful mismatched-authority deploy is now expected to fail with IncorrectAuthority.
4. The enforcement is in programs/bpf_loader/src/lib.rs, an on-chain loader path rather than only CLI-side validation.

## Missing Evidence

1. No proof that an attacker could upgrade a program without the program upgrade authority signer.
2. No demonstrated fund theft, arbitrary state corruption, or consensus failure.
3. No evidence outside the feature-gated behavior of matching_buffer_upgrade_authorities.
4. No complete exploit walkthrough showing attacker prerequisites and victim impact.

## Claim Boundaries

1. Keep the claim to enforcing matching buffer and upgrade authority for deploys/upgrades.
2. Do not claim bypass of all signature checks.
3. Do not claim non-upgradeable BPF loader impact.
4. Do not classify as state-corruption based only on the supplied patch.
