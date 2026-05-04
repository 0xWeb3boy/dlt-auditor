# Code-Shape Card

## Metadata

- ID: `moonbeam-2023-10-31-moonbeam-transaction-processing-456027eece`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proxy-call-filter-hardening`

## Code Shape Summary

- The NormalFilter denied a few proxy variants but let proxy calls fall through. The patch adds an AccountCodes lookup on the real account and rejects proxy calls targeting contract accounts.

## Search Motifs

- RuntimeCall::Proxy fallback allows proxy { real, .. }
- filter checks create_pure/kill_pure but not proxy target class
- AccountCodes contains_key added to call filter

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Add explicit call-filter logic for proxy targets with deployed EVM code and charge the extra storage read in weights.

## False Match Warnings

- Proxying to contract accounts may be intended if downstream origin semantics are explicit
- A separate proxy type filter may already deny sensitive calls
- Additional DB read weight must be included to avoid accounting-only noise
