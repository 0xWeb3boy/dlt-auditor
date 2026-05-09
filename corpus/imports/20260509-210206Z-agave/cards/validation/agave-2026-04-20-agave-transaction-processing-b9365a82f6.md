# Validation Card

## Metadata

- ID: `agave-2026-04-20-agave-transaction-processing-b9365a82f6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sanitization-hardening`

## What Confirmed The Issue

- Top-level sanitize now invokes header, config, signature, account access, instruction, and lookup validation.
- Signature/account sanitizers reject mismatches, excessive signatures, insufficient keys, duplicate addresses, and version-specific bound violations.

## What Could Have Invalidated It

- The old sanitize path already called equivalent checks in all construction modes.
- No untrusted serialized transaction can reach this transaction-view constructor.

## Severity Guidance

- Expected impact band: `transaction validation hardening`
- Expected severity band: `low_or_medium`
- Rationale: The patch strengthens a critical sanitizer, but the evidence did not prove a specific malformed transaction reached execution or caused consensus, fund, or availability impact.

## False-Positive Cautions

- Sanitizer centralization may be correctness cleanup unless a pre-fix malformed input is accepted.
- Do not claim signature bypass or consensus split without a concrete malformed transaction path.
