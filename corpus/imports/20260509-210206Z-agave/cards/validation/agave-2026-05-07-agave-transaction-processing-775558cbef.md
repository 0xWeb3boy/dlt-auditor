# Validation Card

## Metadata

- ID: `agave-2026-05-07-agave-transaction-processing-775558cbef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`

## What Confirmed The Issue

- StaticAccountKeysFrame now rejects counts above LEGACY_OR_V0_MAX_STATIC_ACCOUNTS_PER_PACKET.
- SignatureDetailsFilter storage is aligned with FILTER_SIZE for the full u8 program_id_index domain.

## What Could Have Invalidated It

- The old maximum was already equal to the format-specific bound.
- Out-of-range program_id_index values cannot be produced by serialized transaction input.

## Severity Guidance

- Expected impact band: `transaction parser bounds hardening`
- Expected severity band: `medium`
- Rationale: The commit explicitly references an OOB condition in untrusted transaction parsing, but the evidence did not show whether the old behavior caused panic, memory unsafety, or execution impact.

## False-Positive Cautions

- OOB in a memory-safe language may be a panic/DoS rather than memory corruption.
- Do not claim consensus divergence without evidence the malformed transaction can be accepted differently by validators.
