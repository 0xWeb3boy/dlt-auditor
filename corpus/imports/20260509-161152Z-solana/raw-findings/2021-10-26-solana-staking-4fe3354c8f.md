---
case_id: case_20211026_4fe3354c8f
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: staking
source_quality: medium
date: 2021-10-26
source_refs:
  - git:4fe3354c8f78cc140c71ea9897cd663ac33dde11
  - "sdk/program/src/sysvar/instructions.rs:38"
  - "sdk/program/src/sysvar/instructions.rs:89"
  - "sdk/program/src/sysvar/instructions.rs:279"
  - "programs/bpf/rust/instruction_introspection/src/lib.rs:37"
bug_class: unchecked-sysvar-account-input
impact_type:
  - input-validation
  - account-spoofing-resistance
confidence: medium
tags:
  - blockchain-core
  - sysvar
  - instruction-introspection
  - account-validation
  - sdk-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds safer Solana instructions-sysvar helper APIs and updates an example caller to use one of them. The evidence supports security-relevant hardening around sysvar identity checks and relative instruction lookup error handling, but not a confirmed vulnerability fix.

## Observed Patch Facts

1. In `sdk/program/src/sysvar/instructions.rs`, the patch replaces `/// Store the current instruction's index in the Instructions Sysvar data` with `/// Load the current 'Instruction''s index in the currently executing`.

2. In `sdk/program/src/sysvar/instructions.rs`, the patch replaces `#[cfg(test)]` with `/// Returns the 'Instruction' relative to the current 'Instruction' in the`.

3. In `sdk/program/src/sysvar/instructions.rs`, the patch replaces `instruction1,` with `Err(ProgramError::InvalidArgument),`.

4. In `programs/bpf/rust/instruction_introspection/src/lib.rs`, the patch replaces `.map_err(|_| ProgramError::InvalidAccountData)?;` with `)?;`.

## Project Context

The changed code sits primarily in `sdk/program/src/sysvar`, `sdk/program/src`, `programs/bpf/rust/instruction_introspection/src`, which anchors the finding in the `staking` area of the project. Historical context from `sdk/program/src/sysvar/mod.rs`, `sdk/program/src/sysvar/slot_history.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/program/src/sysvar/mod.rs`, `sdk/program/src/feature.rs`. The strongest project-level identifiers around this patch are `ProgramError`, `instruction_sysvar_account_info`, `Instruction`, and `account_info`.

## Before/After Behavior

Before the patch, callers could use load_current_index(data: &[u8]) on arbitrary borrowed bytes, and that helper could not verify that the bytes came from the instructions sysvar account. After the patch, load_current_index_checked(AccountInfo) checks the account key with check_id, returns UnsupportedSysvar for the wrong sysvar account, borrows the account data, and then reads the current instruction index. The patch also adds get_instruction_relative(relative_index, AccountInfo), with tests covering an invalid negative relative lookup and valid relative offsets. The BPF instruction-introspection example now uses load_current_index_checked instead of the raw byte-slice helper, although the shown code already asserted the sysvar key before reading.

# Root Cause

The issue was unsafe-by-default SDK ergonomics: a current-index helper accepted only raw bytes, so it could not enforce that the source was the authentic instructions sysvar. The evidence does not prove that an existing deployed program was exploitable.

## Walkthrough

1. The instructions sysvar module exposed load_current_index(data: &[u8]), which reconstructs a u16 from the final two bytes of the supplied slice.

2. Because that helper receives only bytes, it cannot validate the source account identity.

3. The patch adds load_current_index_checked(AccountInfo), which rejects accounts whose key fails check_id before reading the current index.

4. The existing load_instruction_at_checked path already checked the sysvar id before deserializing an instruction by absolute index.

5. The patch adds get_instruction_relative(relative_index, AccountInfo), giving callers a checked path for relative instruction lookup.

6. Tests construct three instructions, store current index 1, verify relative -2 returns InvalidArgument, and verify -1, 0, and 1 return the expected instructions.

7. The instruction_introspection BPF example is updated to call load_current_index_checked.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/program/src/sysvar/instructions.rs | 38 | Adds checked current-instruction-index loading that rejects non-instructions-sysvar accounts. |
| sdk/program/src/sysvar/instructions.rs | 89 | Adds relative instruction lookup using the current index with sysvar identity validation and error handling. |
| sdk/program/src/sysvar/instructions.rs | 279 | Adds regression coverage for invalid negative relative lookup and valid relative offsets. |
| programs/bpf/rust/instruction_introspection/src/lib.rs | 37 | Updates an instruction-introspection BPF program to use the checked current-index helper. |

## Code Snippets

## Snippet 1

Context: `sdk/program/src/sysvar/instructions.rs:38` (changes a sensitive control or state-update path)

Before
```rust
}

/// Store the current instruction's index in the Instructions Sysvar data
pub fn store_current_index(data: &mut [u8], instruction_index: u16) {
    let last_index = data.len() - 2;
```
After
```rust
}

/// Load the current `Instruction`'s index in the currently executing
/// `Transaction`
pub fn load_current_index_checked(
    instruction_sysvar_account_info: &AccountInfo,
) -> Result<u16, ProgramError> {
    if !check_id(instruction_sysvar_account_info.key) {
```

## Snippet 2

Context: `sdk/program/src/sysvar/instructions.rs:89` (changes a sensitive control or state-update path)

Before
```rust
}

#[cfg(test)]
mod tests {
```
After
```rust
}

/// Returns the `Instruction` relative to the current `Instruction` in the
/// currently executing `Transaction`
pub fn get_instruction_relative(
    index_relative_to_current: i64,
    instruction_sysvar_account_info: &AccountInfo,
) -> Result<Instruction, ProgramError> {
```

## Snippet 3

Context: `sdk/program/src/sysvar/instructions.rs:279` (changes the branch that decides whether execution stops or continues)

Before
```rust
);

        assert_eq!(
            instruction1,
            load_instruction_at_checked(0, &account_info).unwrap()
        );
        assert_eq!(
            instruction2,
```
After
```rust
);

        assert_eq!(
            Err(ProgramError::InvalidArgument),
            get_instruction_relative(-2, &account_info)
        );
        assert_eq!(
            instruction0,
```

## Snippet 4

Context: `programs/bpf/rust/instruction_introspection/src/lib.rs:37` (changes a sensitive control or state-update path)

Before
```rust
secp_instruction_index as usize,
        instruction_accounts,
    )
    .map_err(|_| ProgramError::InvalidAccountData)?;

    let current_instruction =
        instructions::load_current_index(&instruction_accounts.try_borrow_data()?);
    let my_index = instruction_data[1] as u16;
```
After
```rust
secp_instruction_index as usize,
        instruction_accounts,
    )?;

    let current_instruction = instructions::load_current_index_checked(instruction_accounts)?;
    let my_index = instruction_data[1] as u16;
    assert_eq!(current_instruction, my_index);
```

# Fix Pattern

Add checked SDK helper APIs that accept AccountInfo, validate the expected sysvar id before reading, return typed ProgramError values for invalid inputs, and add regression tests for boundary behavior.

## How It Was Fixed

The patch introduced load_current_index_checked, introduced get_instruction_relative, added tests for invalid and valid relative lookups, and updated the BPF instruction-introspection example to use the checked current-index helper.

# Why It Matters

1. Programs inspecting transaction instructions should avoid accidentally trusting bytes from a non-sysvar account.

2. Relative instruction lookup needs clear invalid-index behavior.

3. Centralized checked helpers reduce duplicated caller-side validation logic.

4. The evidence supports hardening, not a proven consensus or privilege-escalation fix.

# Evidence Notes

The changed paths are in sdk/program/src/sysvar/instructions.rs and a BPF instruction-introspection example, not staking. The evidence shows sysvar id checks, ProgramError handling, and tests for relative lookup bounds. It does not prove a consensus-critical runtime flaw, arbitrary instruction spoofing in deployed programs, or exploitability of the prior example. Protocol security invariant: Programs that inspect transaction instructions through the instructions sysvar should read from the authentic instructions sysvar account and handle instruction-index lookups that fall outside the transaction instruction list. The provided evidence shows new checked helper APIs for these cases, but does not establish a concrete exploitable protocol vulnerability. Verification notes: Does not prove a consensus-critical runtime vulnerability. Does not prove arbitrary transaction instruction spoofing in deployed programs. Does not prove the previous BPF example was exploitable, since it already asserted the sysvar key. Does not show a staking subsystem issue. Does not show privilege escalation beyond safer SDK helper behavior. No external context or file inspection was used. Claims about exploitability were downgraded because the supplied evidence only shows SDK helper hardening. keep_in_security_corpus is false because the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unchecked-sysvar-account-input`
Final impact type: `input-validation, account-spoofing-resistance`
Final confidence: `medium`
Final tags: `blockchain-core, sysvar, instruction-introspection, account-validation, sdk-hardening`

The supplied patch evidence supports a conservative security-hardening classification, not a confirmed vulnerability fix. The change adds checked instructions-sysvar helpers that validate the sysvar account key before reading instruction data and adds bounds/error handling for relative instruction lookup. However, the evidence does not prove an exploitable deployed bug, and the original staking/state-corruption framing is misleading.

## Security Evidence

1. Adds load_current_index_checked(AccountInfo) with check_id validation before reading sysvar data.
2. Adds get_instruction_relative(AccountInfo) with sysvar identity validation and invalid-index error behavior.
3. Updates an instruction-introspection BPF example to use the checked current-index helper.
4. Tests cover invalid relative lookup returning ProgramError::InvalidArgument.

## Missing Evidence

1. No evidence that an existing deployed program was exploitable through the old raw byte-slice helper.
2. No evidence of consensus failure, staking impact, or state corruption.
3. No evidence that the unchecked load_current_index API was removed or that all callers were migrated.
4. The shown example already asserted the instructions sysvar key before the patch.

## Claim Boundaries

1. Classify as SDK/API hardening around instructions sysvar account validation.
2. Do not claim a confirmed vulnerability or exploit path.
3. Do not classify this as staking-related.
4. Do not claim state corruption or consensus-critical impact from the supplied evidence alone.
