# Validation Card

## Metadata

- ID: `nibiru-2024-10-26-nibiru-transaction-processing-c6249126`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `precompile-rollback-hardening`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: SDK multistore cache snapshots, StateDB journal, and commit path.
- Evidence 2: The validated finding ties the change to this invariant: All native side effects produced during a precompile call must share the same transaction journal and rollback boundary as the EVM call that triggered them.

## What Could Have Invalidated It

- Compensating control 1: Do not flag read-only precompiles
- Compensating control 2: Need a state-changing native side effect plus possible revert/error path

## Severity Guidance

- Expected impact band: `state_integrity`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Broken rollback boundaries in precompile execution can leave inconsistent committed state, though the evidence did not prove a concrete value loss.
