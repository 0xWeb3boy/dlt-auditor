---
case_id: case_20210129_893cc76472
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
  - git:893cc7647248a3536fb6e6d0b5e51c71446b862d
  - "programs/bpf_loader/src/lib.rs:460"
  - "programs/bpf_loader/src/lib.rs:563"
  - "cli/src/program.rs:385"
  - "programs/bpf_loader/src/lib.rs:1610"
bug_class: authorization-invariant-bypass
impact_type:
  - authorization-integrity
confidence: medium
tags:
  - blockchain-core
  - bpf-loader
  - upgrade-authority
  - access-control
  - feature-gated
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch strengthens upgradeable BPF loader authorization by requiring the buffer authority to match the upgrade authority for deploy and upgrade operations under the matching_buffer_upgrade_authorities feature. It also prevents setting buffer authority to None under the same feature and updates CLI behavior and tests around that invariant.

## Observed Patch Facts

1. In `programs/bpf_loader/src/lib.rs`, the patch replaces `if let UpgradeableLoaderState::Buffer {` with `if let UpgradeableLoaderState::Buffer { authority_address } = buffer.state()? {`.

2. In `programs/bpf_loader/src/lib.rs`, the patch replaces `if authority_address == None {` with `if invoke_context.is_feature_active(&matching_buffer_upgrade_authorities::id())`.

3. In `cli/src/program.rs`, the patch replaces `let new_buffer_authority = if matches.is_present("final") {` with `let new_buffer_authority = if let Some(new_buffer_authority) =`.

4. In `programs/bpf_loader/src/lib.rs`, the patch replaces `assert!(bank_client` with `assert_eq!(`.

## Project Context

The changed code sits primarily in `programs/bpf_loader/src`, `programs/bpf_loader`, `cli/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/serialization.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/serialization.rs`. The strongest project-level identifiers around this patch are `UpgradeableLoaderState::Buffer`, `new_buffer_authority`, `Buffer`, and `matching_buffer_upgrade_authorities::id`.

## Before/After Behavior

Before the patch, the deploy/upgrade path verified that the supplied buffer account decoded as UpgradeableLoaderState::Buffer but ignored its authority_address. After the patch, that path extracts authority_address and returns InstructionError::IncorrectAuthority when it does not equal Some(upgrade authority key), gated by matching_buffer_upgrade_authorities. Before the patch, Buffer SetAuthority could set the authority to None; after the patch, new_authority == None is rejected under the same feature. Regression evidence shows a mismatched buffer/upgrade-authority transaction changing from expected success to expected failure.

# Root Cause

The loader parsed buffer authority state but did not enforce that the buffer authority matched the program upgrade authority in the deploy/upgrade path. This allowed a buffer controlled by a different authority to be accepted for the observed operation before the new feature-gated check.

## Walkthrough

1. A deploy or upgrade instruction reaches the upgradeable BPF loader with a program account, buffer account, and authority account.

2. The old buffer verification accepted any account whose state was UpgradeableLoaderState::Buffer, without using authority_address.

3. The fixed code extracts authority_address from the buffer state.

4. When matching_buffer_upgrade_authorities is active, the loader compares authority_address with Some(*authority.unsigned_key()).

5. If the values differ, the loader logs the mismatch and returns InstructionError::IncorrectAuthority.

6. Buffer SetAuthority handling now rejects new_authority == None under the same feature.

7. The CLI set-buffer-authority flow was changed so the shown path no longer uses the final-to-None behavior.

8. Tests were updated to expect failure when buffer and upgrade authorities are mismatched.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/lib.rs | 460 | Upgradeable loader deploy/upgrade buffer verification now requires buffer authority to equal the upgrade authority under matching_buffer_upgrade_authorities. |
| programs/bpf_loader/src/lib.rs | 563 | Buffer SetAuthority handling rejects removing buffer authority when the matching-authority feature is active. |
| cli/src/program.rs | 385 | CLI set-buffer-authority flow no longer allows finalizing a buffer to no authority in this path. |
| programs/bpf_loader/src/lib.rs | 1610 | Regression test expects deploy/upgrade with mismatched buffer and upgrade authorities to fail. |

## Code Snippets

## Snippet 1

Context: `programs/bpf_loader/src/lib.rs:460` (changes bounds, limits, or capacity handling)

Before
```rust
// Verify Buffer account

            if let UpgradeableLoaderState::Buffer {
                authority_address: _,
            } = buffer.state()?
            {
            } else {
                log!(logger, "Invalid Buffer account");
```
After
```rust
// Verify Buffer account

            if let UpgradeableLoaderState::Buffer { authority_address } = buffer.state()? {
                if invoke_context.is_feature_active(&matching_buffer_upgrade_authorities::id()) {
                    if authority_address != Some(*authority.unsigned_key()) {
                        log!(logger, "Buffer and upgrade authority don't match");
                        return Err(InstructionError::IncorrectAuthority);
                    }
```

## Snippet 2

Context: `programs/bpf_loader/src/lib.rs:563` (changes bounds, limits, or capacity handling)

Before
```rust
match account.state()? {
                UpgradeableLoaderState::Buffer { authority_address } => {
                    if authority_address == None {
                        log!(logger, "Buffer is immutable");
```
After
```rust
match account.state()? {
                UpgradeableLoaderState::Buffer { authority_address } => {
                    if invoke_context.is_feature_active(&matching_buffer_upgrade_authorities::id())
                        && new_authority == None
                    {
                        log!(logger, "Buffer authority is not optional");
                        return Err(InstructionError::IncorrectAuthority);
                    }
```

## Snippet 3

Context: `cli/src/program.rs:385` (changes the branch that decides whether execution stops or continues)

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

Context: `programs/bpf_loader/src/lib.rs:1610` (changes an authorization or privilege gate)

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

Add an explicit feature-gated authority-equality guard in the loader path and reject authority states that cannot satisfy the new invariant.

## How It Was Fixed

programs/bpf_loader/src/lib.rs now reads authority_address from UpgradeableLoaderState::Buffer during deploy/upgrade verification and rejects mismatches against the supplied upgrade authority under matching_buffer_upgrade_authorities. The same file rejects attempts to remove buffer authority under that feature. cli/src/program.rs was adjusted away from the shown final-to-None buffer authority flow, and tests were updated to assert that mismatched authorities fail.

# Why It Matters

1. Enforces a concrete access-control invariant in upgradeable BPF deploy and upgrade handling.

2. Prevents accepting a program data buffer controlled by a different authority than the upgrade authority.

3. Keeps buffer authority state compatible with the new matching-authority rule.

4. Impact is bounded to upgradeable BPF deploy, upgrade, and buffer authority handling shown in the evidence.

# Evidence Notes

Primary evidence is the buffer verification change in programs/bpf_loader/src/lib.rs around line 460, where authority_address changes from ignored to compared against the upgrade authority under matching_buffer_upgrade_authorities. Supporting evidence includes the Buffer SetAuthority rejection of new_authority == None around line 563, the CLI set-buffer-authority change around cli/src/program.rs line 385, and regression expectations around programs/bpf_loader/src/lib.rs line 1610. The evidence does not establish arbitrary code execution, fund theft, cluster-wide exploitability, or impact outside the upgradeable BPF loader paths shown. Protocol security invariant: For upgradeable BPF program deploys and upgrades, the buffer account supplying program data must have an authority matching the program upgrade authority when matching_buffer_upgrade_authorities is active. Buffer authority removal is also rejected under that feature so buffers cannot be made incompatible with the matching-authority invariant. Verification notes: The patch does not prove arbitrary code execution by itself. The patch does not prove theft of funds or direct account balance loss. The patch does not show whether the issue was exploitable before feature activation on all clusters. The patch does not establish impact outside upgradeable BPF program deploy, upgrade, and buffer authority handling. Patch evidence directly shows a new IncorrectAuthority failure on authority mismatch. Regression evidence shows mismatched authorities are expected to fail after the change. Signer handling appears in the surrounding path, but the provided evidence does not require treating signer enforcement as the main new fix. No broader exploit mechanics are proven by the provided input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authorization-invariant-bypass`
Final impact type: `authorization-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, bpf-loader, upgrade-authority, access-control, feature-gated`

The provided patch clearly tightens a security-sensitive authorization invariant in Solana's upgradeable BPF loader by requiring the buffer authority to match the upgrade authority and rejecting authority removal under the feature gate. That supports retaining it as security hardening. However, the evidence does not confidently prove a concrete exploit, state corruption, fund loss, or broader consensus impact, so the original security-fix/state-corruption framing is too strong.

## Security Evidence

1. Deploy/upgrade buffer verification changed from ignoring authority_address to comparing it against the supplied upgrade authority.
2. Mismatch now returns InstructionError::IncorrectAuthority.
3. Buffer SetAuthority now rejects new_authority == None under the same matching-authority feature.
4. Regression evidence expects mismatched buffer and upgrade authorities to fail after the patch.

## Missing Evidence

1. No concrete exploit path is shown from the patch alone.
2. No evidence proves state corruption, fund theft, arbitrary code execution, or consensus failure.
3. Feature-gated behavior leaves deployment scope and activation context unclear.
4. The provided snippets do not prove impact outside upgradeable BPF deploy, upgrade, and buffer authority handling.

## Claim Boundaries

1. Valid claim: the patch enforces a new buffer-authority and upgrade-authority matching invariant.
2. Valid claim: the patch strengthens access control around upgradeable BPF loader operations.
3. Do not claim proven state corruption from the supplied evidence.
4. Do not claim arbitrary code execution, theft, or cluster-wide exploitability.
