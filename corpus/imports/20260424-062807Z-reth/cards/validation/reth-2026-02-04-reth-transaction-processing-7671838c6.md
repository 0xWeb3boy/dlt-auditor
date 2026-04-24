# Validation Card

## Metadata

- ID: `reth-2026-02-04-reth-transaction-processing-7671838c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## What Confirmed The Issue

- Consensus validation code now explicitly distinguishes header gas_used semantics from receipt cumulative_gas_used semantics under Amsterdam/EIP-7778.
- crates/stateless/src/validation.rs changed from passing None to Some(output.gas_used) into post-execution validation, showing a real logic fix rather than comment-only cleanup.

## What Could Have Invalidated It

- No failing test, reproducer, or execution trace is provided showing concrete invalid acceptance or rejection before the fix
- No advisory, commit text, or patch evidence states attacker exploitability or an observed chain split

## Severity Guidance

- Expected impact band: consensus_or_protocol_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No failing test, reproducer, or execution trace is provided showing concrete invalid acceptance or rejection before the fix
- No advisory, commit text, or patch evidence states attacker exploitability or an observed chain split
