---
case_id: case_20260507_775558cbef
project: agave
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: hardening-or-correctness-fix
impact_type:
  - correctness-or-hardening
confidence: medium
source_quality: medium
tags:
  - infrastructure
  - transaction-processing
  - hardening-or-correctness-fix
  - correctness-or-hardening
  - signature
date: 2026-05-07
source_refs:
  - git:775558cbefadd40175d3fbe070af95748b752bb4
  - "compute-budget-instruction/src/builtin_programs_filter.rs:142"
  - "transaction-view/src/static_account_keys_frame.rs:28"
  - "runtime-transaction/src/signature_details.rs:83"
  - "runtime-transaction/src/signature_details.rs:93"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely hardens txv1-related transaction parsing and helper-cache bounds, but the provided evidence does not establish a concrete exploit impact. The grounded change is that static account count validation now uses `LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET`, while signature/program-id helper storage is aligned with `FILTER_SIZE` for the full `u8` program_id_index domain.

## Observed Patch Facts

1. In `compute-budget-instruction/src/builtin_programs_filter.rs`, the patch replaces `test_store` with `test_store.get_program_kind(FILTER_SIZE + 1, &DUMMY_PROGRAM_ID.parse().unwrap(),),`.

2. In `transaction-view/src/static_account_keys_frame.rs`, the patch replaces `const _: () = assert!(MAX_STATIC_ACCOUNTS_PER_PACKET & 0b1000_0000 == 0);` with `const _: () = assert!(LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET & 0b1000_0000 == 0);`.

3. In `runtime-transaction/src/signature_details.rs`, the patch replaces `// array of slots for all possible static and sanitized program_id_index,` with `// array of slots for all possible u8 program_id_index values,`.

4. In `runtime-transaction/src/signature_details.rs`, the patch replaces `flags: [None; FILTER_SIZE as usize],` with `flags: [None; FILTER_SIZE],`.

## Project Context

The changed code sits primarily in `compute-budget-instruction/src`, `transaction-view/src`, `runtime-transaction/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `compute-budget-instruction/src/compute_budget_instruction_details.rs`, `transaction-view/src/transaction_frame.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `compute-budget-instruction/src/compute_budget_instruction_details.rs`, `transaction-view/src/transaction_frame.rs`. The strongest project-level identifiers around this patch are `num_static_accounts`, `usize`, `flags`, and `BuiltinProgramsFilter::new`.

## Before/After Behavior

Before the patch, `StaticAccountKeysFrame::try_new` checked `num_static_accounts` against `MAX_STATIC_ACCOUNTS_PER_PACKET`. After the patch, it checks against `LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET` and keeps the compile-time one-byte assertion aligned with that same constant. `SignatureDetailsFilter` also now uses `FILTER_SIZE` directly for its array and initializer, with comments saying it covers all possible `u8 program_id_index` values. A builtin-program filter test still verifies that an index beyond `FILTER_SIZE` is treated as `ProgramKind::NotBuiltin`.

# Root Cause

The evidence supports an incorrect or ambiguous bounds model around transaction static account counts and fixed-size program_id_index caches. It does not prove whether the prior behavior led to panic, malformed transaction acceptance, memory unsafety, consensus divergence, or validator crash behavior.

## Walkthrough

1. Transaction-view parsing reads serialized transaction bytes, including txv1-related paths shown in the provided context.

2. `StaticAccountKeysFrame::try_new` reads `num_static_accounts` from the byte stream.

3. The patch changes the maximum accepted static-account count from `MAX_STATIC_ACCOUNTS_PER_PACKET` to `LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET`.

4. The compile-time assertion about the maximum fitting in one byte is changed to use the same replacement constant.

5. `SignatureDetailsFilter::is_signature` indexes a fixed `flags` array by `usize::from(index)`, where `index` is a `u8`.

6. The filter is now documented and initialized as covering all possible `u8 program_id_index` values through `FILTER_SIZE`.

7. The builtin-program filter test checks that an index beyond `FILTER_SIZE` returns `ProgramKind::NotBuiltin`.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| transaction-view/src/static_account_keys_frame.rs | 28 | parses static account key count from transaction bytes and rejects counts outside the allowed packet bound |
| runtime-transaction/src/signature_details.rs | 83 | caches signature-program classification by u8 program_id_index with a fixed-size flags array |
| runtime-transaction/src/signature_details.rs | 93 | initializes the per-program_id_index signature details filter |
| compute-budget-instruction/src/builtin_programs_filter.rs | 142 | tests out-of-bounds program index handling for builtin program lookup |
| compute-budget-instruction/src/compute_budget_program_id_filter.rs | 5 | related compute-budget program_id_index cache using the shared FILTER_SIZE concept |

## Code Snippets

## Snippet 1

Context: `compute-budget-instruction/src/builtin_programs_filter.rs:142` (changes the branch that decides whether execution stops or continues)

Before
```rust
let mut test_store = BuiltinProgramsFilter::new();
        assert_eq!(
            test_store
                .get_program_kind(FILTER_SIZE as usize + 1, &DUMMY_PROGRAM_ID.parse().unwrap(),),
            ProgramKind::NotBuiltin
        );
```
After
```rust
let mut test_store = BuiltinProgramsFilter::new();
        assert_eq!(
            test_store.get_program_kind(FILTER_SIZE + 1, &DUMMY_PROGRAM_ID.parse().unwrap(),),
            ProgramKind::NotBuiltin
        );
```

## Snippet 2

Context: `transaction-view/src/static_account_keys_frame.rs:28` (changes the branch that decides whether execution stops or continues)

Before
```rust
pub(crate) fn try_new(bytes: &[u8], offset: &mut usize) -> Result<Self> {
        // Max size must not have the MSB set so that it is size 1.
        const _: () = assert!(MAX_STATIC_ACCOUNTS_PER_PACKET & 0b1000_0000 == 0);

        let num_static_accounts = read_byte(bytes, offset)?;
        if num_static_accounts == 0 || num_static_accounts > MAX_STATIC_ACCOUNTS_PER_PACKET {
            return Err(TransactionViewError::ParseError);
        }
```
After
```rust
pub(crate) fn try_new(bytes: &[u8], offset: &mut usize) -> Result<Self> {
        // Max size must not have the MSB set so that it is size 1.
        const _: () = assert!(LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET & 0b1000_0000 == 0);

        let num_static_accounts = read_byte(bytes, offset)?;
        if num_static_accounts == 0
            || num_static_accounts > LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET
        {
```

## Snippet 3

Context: `runtime-transaction/src/signature_details.rs:83` (changes a sensitive control or state-update path)

Before
```rust
struct SignatureDetailsFilter {
    // array of slots for all possible static and sanitized program_id_index,
    // each slot indicates if a program_id_index has not been checked, or is
    // already checked with result that can be reused.
    flags: [Option<ProgramIdStatus>; FILTER_SIZE as usize],
}
```
After
```rust
struct SignatureDetailsFilter {
    // array of slots for all possible u8 program_id_index values,
    // each slot indicates if a program_id_index has not been checked, or is
    // already checked with result that can be reused.
    flags: [Option<ProgramIdStatus>; FILTER_SIZE],
}
```

## Snippet 4

Context: `runtime-transaction/src/signature_details.rs:93` (changes a sensitive control or state-update path)

Before
```rust
fn new() -> Self {
        Self {
            flags: [None; FILTER_SIZE as usize],
        }
    }
```
After
```rust
fn new() -> Self {
        Self {
            flags: [None; FILTER_SIZE],
        }
    }
```

# Fix Pattern

Use the format-specific maximum for transaction account-count parsing and ensure fixed-size program_id_index caches cover the full index domain they accept.

## How It Was Fixed

The parser bound in `transaction-view/src/static_account_keys_frame.rs` was switched to `LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET`. The signature-details cache in `runtime-transaction/src/signature_details.rs` was aligned with `FILTER_SIZE` without the prior cast. The builtin-program filter test continues to cover out-of-range lookup behavior.

# Why It Matters

1. Transaction parsing handles untrusted serialized bytes.

2. Incorrect count bounds can allow malformed transaction layouts to reach later code.

3. Program indexes are used as fixed-array indexes in helper filters.

4. The patch suggests OOB prevention, but the provided evidence does not prove concrete exploitability.

# Evidence Notes

Strongest evidence is the commit subject `Fix txv1 OOB (#12302)`, the static account count bound change in `transaction-view/src/static_account_keys_frame.rs`, and fixed-size `program_id_index` cache alignment in `runtime-transaction/src/signature_details.rs`. Unsupported claims removed: no proof of remote exploitability, memory unsafety, signature bypass, compute-budget bypass, consensus divergence, or validator crash. Protocol security invariant: Serialized transaction data must be parsed with account-count and program_id_index bounds that match the transaction format and the fixed-size helper caches used downstream. Verification notes: The patch does not prove remote exploitability beyond malformed transaction handling. The patch does not show memory unsafety; Rust bounds checks may have limited impact to panic/error behavior. The patch does not prove signature verification bypass or compute-budget bypass. The patch does not show consensus divergence or validator crash behavior directly. The FILTER_SIZE cast cleanup alone is not security-relevant without the txv1 OOB context. No direct pre-fix failing test or exploit trace is provided. No values for `MAX_STATIC_ACCOUNTS_PER_PACKET`, `LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET`, or `FILTER_SIZE` are provided. Rust bounds behavior means OOB impact cannot be assumed beyond likely rejection or panic risk. Treat the FILTER_SIZE cast cleanup as supporting evidence, not independently security-significant. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The evidence supports retaining this as security hardening, not as a concrete security fix. The patch changes transaction parsing bounds for static account counts to a format-specific maximum and the commit explicitly describes a txv1 out-of-bounds fix. Because the affected path parses serialized transaction data and rejects invalid counts, this is security-sensitive hardening. However, the supplied evidence does not prove exploitability, validator crash, memory unsafety, consensus divergence, or bypass impact.

## Security Evidence

1. Commit subject says "Fix txv1 OOB".
2. StaticAccountKeysFrame::try_new reads transaction bytes and now rejects num_static_accounts above LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET.
3. The parser returns TransactionViewError::ParseError on out-of-range static account counts.
4. SignatureDetailsFilter indexes a fixed flags array by u8-derived program_id_index and is documented as covering all possible u8 values.

## Missing Evidence

1. No pre-fix failing test or exploit input is supplied.
2. No values are provided for MAX_STATIC_ACCOUNTS_PER_PACKET, LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET, or FILTER_SIZE.
3. No evidence shows whether the prior OOB caused panic, invalid acceptance, consensus divergence, or denial of service.
4. No evidence shows memory unsafety or signature/compute-budget bypass.

## Claim Boundaries

1. Validate only as security-hardening, not a proven security-fix.
2. Do not claim remote exploitability from the supplied patch alone.
3. Do not claim memory corruption; Rust bounds checks may limit impact.
4. Treat FILTER_SIZE cast cleanup as supporting context, not independently security-significant.
