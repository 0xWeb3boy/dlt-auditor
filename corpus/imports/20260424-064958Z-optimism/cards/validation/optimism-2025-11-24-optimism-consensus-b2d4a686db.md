# Validation Card

## Metadata

- ID: `optimism-2025-11-24-optimism-consensus-b2d4a686db`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-invariant-enforcement`

## What Confirmed The Issue

- Commit message explicitly says deposit-only payload conversion was not correctly filtering non-deposit payloads.
- New unit test for OpAttributesWithParent::as_deposits_only asserts non-deposit transaction types are stripped.
- BuildTask::start_build now derives forkchoice version and submits payload attributes from attributes_envelope.attributes, indicating corrected propagation of the filtered payload.
- The change is in protocol/engine build logic, a security-sensitive consensus path in a blockchain client.

## What Could Have Invalidated It

- No provided hunk shows the full pre-patch implementation of as_deposits_only failing in production code.
- No evidence shows attacker control, exploit steps, or remotely triggerable abuse.
- No evidence demonstrates real-world consensus divergence, chain split, or funds impact.
- The excerpts do not fully define the semantic difference between inner and attributes beyond the observed fix.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No provided hunk shows the full pre-patch implementation of as_deposits_only failing in production code.
- No evidence shows attacker control, exploit steps, or remotely triggerable abuse.
- No evidence demonstrates real-world consensus divergence, chain split, or funds impact.
