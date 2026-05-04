# Code-Shape Card

## Metadata

- ID: `moonbeam-2026-02-18-moonbeam-cryptography-18b6a81dad`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `permit-deadline-validation`

## Code Shape Summary

- The permit guard divided the current millisecond timestamp by 1000, creating a floor-rounding window. The fix multiplies the deadline to milliseconds with checked_mul and compares directly.

## Search Motifs

- timestamp / 1000 compared to deadline
- permit deadline checked after unit conversion with flooring
- checked_mul(1000) added to authorization expiry guard

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Normalize deadline and current time to the same unit, use checked arithmetic for conversion, and reject expired or overflowing permits.

## False Match Warnings

- If both timestamp and deadline are already same units, unit normalization is not a bug
- A grace period explicitly specified by protocol may be intentional
- Read-only signature checks without state mutation have lower impact
