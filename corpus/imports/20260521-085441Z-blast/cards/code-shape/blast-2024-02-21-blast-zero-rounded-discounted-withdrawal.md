# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-zero-rounded-discounted-withdrawal`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `zero-rounded-positive-value-lifecycle`

## Code Shape Summary

- The withdrawal queue allows realAmount == 0 for a positive nominal request; messenger first-submission assertions then fail before writing retry state.

## Search Motifs

- realAmount == 0
- nominalAmount * sharePrice / 1e27
- _value > 0 && msg.value == 0
- failedMessages not written

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Reject positive nominal claims that discount to zero before finalization, or teach messenger/portal replay state to represent zero-rounded positive messages.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
