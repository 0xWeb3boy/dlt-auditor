# Code-Shape Card

## Metadata

- ID: `moonbeam-2023-01-19-moonbeam-transaction-processing-b133edf7fd`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-hardening`

## Code Shape Summary

- The precompile compared caller gas to request limits without adding subcall overhead and lacked a conservative remaining-gas check for fulfillment. The fix uses checked_add and upfront max-cost checks.

## Search Motifs

- gas_limit checked without adding subcall_overhead
- checked_add added around gas accounting
- fulfillment starts before max prepare/finish cost check

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Use checked arithmetic for gas-plus-overhead and reject calls early when remaining gas cannot cover worst-case preparation and finish costs.

## False Match Warnings

- Gas checks are less security-critical if all downstream work is separately metered and atomic
- Overflow-safe types alone do not prove exploitable undercharging
- Read-only precompile calls have lower impact
