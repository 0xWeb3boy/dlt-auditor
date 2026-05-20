# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-h02-shared-statedb-consensus-gas`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `shared-statedb-query-state-leakage`

## What Confirmed The Issue

- Public C4 report section H-02 rated this as High.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if the pointer is scoped only to the current transaction context.
- No issue if read-only queries use isolated keeper copies.

## Severity Guidance

- Expected impact band: consensus gas nondeterminism
- Expected severity band: high

## False-Positive Cautions

- No issue if the pointer is scoped only to the current transaction context.
- No issue if read-only queries use isolated keeper copies.
- No issue if nil vs non-nil has no consensus-visible behavior or gas difference.
