---
case_id: case_20210129_08bda35fd6
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
  - git:08bda35fd67be479d1ef9f6ed6c3d6cf907c4c72
  - "programs/bpf_loader/src/lib.rs:515"
  - "programs/bpf_loader/src/lib.rs:619"
  - "cli/src/program.rs:400"
  - "programs/bpf_loader/src/lib.rs:1682"
bug_class: access-control
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - program-upgrade
  - access-control
  - authority-check
  - feature-gated
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds a feature-gated authority-equivalence check in the upgradeable BPF loader. Previously the loader verified that the supplied account was a Buffer but ignored its authority_address in the shown deploy/upgrade verification path. After the patch, mismatched buffer and upgrade authorities fail with IncorrectAuthority, and buffer authority removal is rejected under the same feature gate.

## Observed Patch Facts

1. In `programs/bpf_loader/src/lib.rs`, the patch replaces `if let UpgradeableLoaderState::Buffer {` with `if let UpgradeableLoaderState::Buffer { authority_address } = buffer.state()? {`.

2. In `programs/bpf_loader/src/lib.rs`, the patch replaces `if authority_address == None {` with `if invoke_context.is_feature_active(&matching_buffer_upgrade_authorities::id())`.

3. In `cli/src/program.rs`, the patch replaces `let new_buffer_authority = if matches.is_present("final") {` with `let new_buffer_authority = if let Some(new_buffer_authority) =`.

4. In `programs/bpf_loader/src/lib.rs`, the patch replaces `assert!(bank_client` with `assert_eq!(`.

## Project Context

The changed code sits primarily in `programs/bpf_loader/src`, `programs/bpf_loader`, `cli/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/serialization.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `programs/bpf_loader/src/syscalls.rs`, `programs/bpf_loader/src/serialization.rs`. The strongest project-level identifiers around this patch are `UpgradeableLoaderState::Buffer`, `new_buffer_authority`, `Buffer`, and `matching_buffer_upgrade_authorities::id`.

## Before/After Behavior

Before: the Buffer verification path pattern-matched UpgradeableLoaderState::Buffer while discarding authority_address, so the provided evidence shows no comparison between the buffer authority and upgrade authority before continuing. The set-buffer-authority path allowed authority_address == None to represent an immutable buffer, and the CLI flow could produce a None final buffer authority. After: when matching_buffer_upgrade_authorities is active, the loader extracts authority_address and rejects authority_address != Some(*authority.unsigned_key()). The set-buffer-authority path rejects new_authority == None, the CLI path resolves a concrete new buffer authority in the shown flow, and regression coverage expects a mismatched-authority transaction to fail.

# Root Cause

The loader authorization check was incomplete: it validated the account state as Buffer but did not enforce that the Buffer authority matched the upgrade authority for deploy/upgrade processing. That allowed the operation to proceed past the shown check with a Buffer controlled by a different authority.

## Walkthrough

1. A deploy or upgrade reaches the upgradeable loader with a Program account, Buffer account, and authority context.

2. The old Buffer verification only checked that buffer.state()? decoded as UpgradeableLoaderState::Buffer and ignored authority_address.

3. The patch retains authority_address from the Buffer state.

4. When matching_buffer_upgrade_authorities is active, the loader compares authority_address to Some(*authority.unsigned_key()).

5. If the authorities differ, the loader logs the mismatch and returns InstructionError::IncorrectAuthority.

6. The set-buffer-authority path also rejects new_authority == None under the same feature gate.

7. The updated test evidence shows mismatched-authority behavior now expected to fail instead of succeed.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/bpf_loader/src/lib.rs | 515 | Upgradeable loader deploy/upgrade buffer verification now rejects buffers whose authority does not match the upgrade authority. |
| programs/bpf_loader/src/lib.rs | 619 | Set-buffer-authority handling rejects removing buffer authority while the matching-authorities feature is active. |
| cli/src/program.rs | 400 | CLI set-buffer-authority parsing no longer produces an optional/None final buffer authority in the updated flow. |
| programs/bpf_loader/src/lib.rs | 1682 | Regression coverage expects deploy/upgrade with mismatched buffer and upgrade authorities to fail. |

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

Context: `programs/bpf_loader/src/lib.rs:1682` (changes an authorization or privilege gate)

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

Add an explicit feature-gated authorization invariant in the loader path, then prevent state transitions that would bypass or make that invariant impossible to evaluate.

## How It Was Fixed

The code now extracts the Buffer authority, compares it to the supplied upgrade authority under matching_buffer_upgrade_authorities, and fails closed with IncorrectAuthority on mismatch. It also rejects authority removal for buffers under the same feature gate, adjusts the CLI parsing path away from producing None in the shown final-authority flow, and updates regression coverage for mismatched authorities.

# Why It Matters

1. Enforces a concrete access-control check in a program deployment and upgrade path.

2. Prevents use of a Buffer controlled by a different authority once the feature is active.

3. Keeps Buffer authority state compatible with later authorization checks.

4. The evidence does not prove arbitrary upgrade, fund theft, validator compromise, or consensus failure.

# Evidence Notes

The strongest evidence is programs/bpf_loader/src/lib.rs around the Buffer verification check and set-buffer-authority handling, plus regression coverage expecting a mismatched-authority transaction to fail. The commit subject directly states the intended invariant. The security claim should remain bounded to the feature-gated authority-mismatch check; the snippets do not establish a complete exploit transaction or broader chain impact. Protocol security invariant: For upgradeable BPF deploy or upgrade processing, the Buffer account's recorded authority must match the upgrade authority used for the operation once the matching_buffer_upgrade_authorities feature is active. The buffer authority also must remain comparable, so the feature-gated path rejects making it None. Verification notes: The patch does not by itself prove arbitrary program upgrade without any valid signer. The patch does not show a demonstrated exploit transaction or real-world impact. The new checks are feature-gated, so behavior before feature activation is not established from the snippets alone. The evidence does not prove effects on immutable programs beyond the changed buffer-authority rule. No fund theft, validator compromise, or consensus failure is proven by the provided patch evidence. Supported by direct code evidence adding authority_address comparison and IncorrectAuthority failure. Supported by feature-gated rejection of new_authority == None. Supported by updated regression expectation for mismatched authorities. No evidence provided for arbitrary program upgrade without a valid signer. No evidence provided for fund theft, validator compromise, or consensus failure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `access-control`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, program-upgrade, access-control, authority-check, feature-gated`

The supplied patch directly adds a feature-gated authority check in the upgradeable BPF loader so a Buffer account's recorded authority must match the supplied upgrade authority, and rejects making buffer authority optional under that feature. This is clearly security-sensitive authorization hardening in a program deploy/upgrade path, but the evidence does not prove a concrete exploit, arbitrary upgrade, or state corruption impact strongly enough to keep the original high-confidence security-fix/state-corruption framing.

## Security Evidence

1. Deploy/upgrade buffer verification now extracts authority_address instead of discarding it.
2. The loader returns InstructionError::IncorrectAuthority when buffer authority does not match the upgrade authority under matching_buffer_upgrade_authorities.
3. The buffer-authority update path rejects new_authority == None under the same feature gate.
4. Regression evidence changes a mismatched-authority deploy/upgrade transaction from success expectation to failure expectation.
5. The commit subject explicitly states the authority invariant being enforced.

## Missing Evidence

1. No demonstrated exploit transaction is provided.
2. No evidence proves arbitrary program upgrade without a valid signer.
3. No evidence proves fund theft, validator compromise, consensus failure, or broader chain impact.
4. Feature-gated behavior means the patch alone does not establish behavior before activation.
5. The evidence does not prove state corruption as the primary bug class.

## Claim Boundaries

1. Valid claim: feature-gated authorization hardening for upgradeable BPF deploy/upgrade buffer authority matching.
2. Valid claim: mismatched buffer and upgrade authorities are rejected after the patch when the feature is active.
3. Do not claim arbitrary code execution or arbitrary program upgrade from this evidence alone.
4. Do not claim fund theft, validator compromise, or consensus failure.
5. Do not classify as state-corruption based only on the supplied patch.
