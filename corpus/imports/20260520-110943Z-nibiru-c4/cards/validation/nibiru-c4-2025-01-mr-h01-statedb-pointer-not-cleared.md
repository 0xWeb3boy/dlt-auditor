# Validation Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-h01-statedb-pointer-not-cleared`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `statedb-pointer-lifecycle-cleanup-missing`

## What Confirmed The Issue

- Public C4 report section MR-H-01 rated this as High.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if StateDB is passed through context only.
- No issue if a defer always clears the pointer on every return path.

## Severity Guidance

- Expected impact band: stale StateDB pointer persists past transaction scope
- Expected severity band: high

## False-Positive Cautions

- No issue if StateDB is passed through context only.
- No issue if a defer always clears the pointer on every return path.
- No issue if nil vs non-nil does not affect consensus-visible execution.
