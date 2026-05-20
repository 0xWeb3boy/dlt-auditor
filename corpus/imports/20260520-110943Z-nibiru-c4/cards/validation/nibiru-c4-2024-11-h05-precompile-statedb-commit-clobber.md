# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-h05-precompile-statedb-commit-clobber`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `precompile-statedb-commit-clobber`

## What Confirmed The Issue

- Public C4 report section H-05 rated this as High.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if nested calls share one StateDB and one commit context.
- No issue if dirty state is refreshed from the latest cache context before commit.

## Severity Guidance

- Expected impact band: ERC20/bank double-spend through stale StateDB commit
- Expected severity band: high

## False-Positive Cautions

- No issue if nested calls share one StateDB and one commit context.
- No issue if dirty state is refreshed from the latest cache context before commit.
- No issue if precompile cannot invoke user-controlled ERC20 callbacks.
