# Validation Card

## Metadata

- ID: `optimism-2025-08-12-optimism-storage-84164c9019`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reorg-state-validation`

## What Confirmed The Issue

- Reorg processing now checks whether the latest source block is still canonical before rewinding.
- The new common-ancestor logic derives its floor from the finalized safety head via derived_to_source(...).
- Rewind-target search walks backward until it finds a canonical source block, tightening rollback behavior on non-canonical history.
- Added activation/finalized reorg tests indicate the change is enforcing stronger consensus-state invariants rather than only refactoring metrics.

## What Could Have Invalidated It

- No advisory, CVE, or commit text states that this fixed an exploitable vulnerability.
- The patch does not show an attacker-controlled input, privilege boundary crossing, or remote trigger.
- The evidence does not demonstrate concrete outcomes such as fund loss, consensus split, or persistent corruption in production.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No advisory, CVE, or commit text states that this fixed an exploitable vulnerability.
- The patch does not show an attacker-controlled input, privilege boundary crossing, or remote trigger.
- The evidence does not demonstrate concrete outcomes such as fund loss, consensus split, or persistent corruption in production.
