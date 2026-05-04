# Code-Shape Card

## Metadata

- ID: `moonbeam-2025-04-28-moonbeam-transaction-processing-0e600693f7`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- Runtime proxy filtering had an unconditional allow branch and a misclassified target branch. The fix classifies targets by code/precompile status and only allows intended target classes.

## Search Motifs

- ProxyType::Any => true in EVM proxy filtering
- precompile predicate used in wrong direction for simple-account branch
- AccountCodesMetadata or target classifier added to proxy precompile

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Replace unconditional proxy allow logic with explicit target classification and whitelist-style policy for precompiles, no-code accounts, and contracts.

## False Match Warnings

- ProxyType::Any may intentionally allow all targets only if user consent covers contract calls
- Read-only target calls have lower impact than state-changing calls
- A downstream target whitelist may make the broad branch harmless
