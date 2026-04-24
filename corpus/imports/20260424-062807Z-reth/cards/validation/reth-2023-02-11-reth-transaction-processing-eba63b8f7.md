# Validation Card

## Metadata

- ID: `reth-2023-02-11-reth-transaction-processing-eba63b8f7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-transition-check`

## What Confirmed The Issue

- Consensus-sensitive call sites changed from active_at_ttd(total_difficulty) to active_at_ttd(total_difficulty, current_difficulty).
- new_payload pre-merge rejection logic now uses the refined TTD check, affecting externally supplied payload validation.

## What Could Have Invalidated It

- No test, reproducer, or failing scenario shows acceptance of invalid blocks or rejection of valid ones before the patch
- No evidence demonstrates a concrete attacker-controlled exploit path or remote trigger beyond transition-boundary correctness

## Severity Guidance

- Expected impact band: consensus_or_protocol_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No test, reproducer, or failing scenario shows acceptance of invalid blocks or rejection of valid ones before the patch
- No evidence demonstrates a concrete attacker-controlled exploit path or remote trigger beyond transition-boundary correctness
