# Code-Shape Card

## Metadata

- ID: `moonbeam-2023-02-07-moonbeam-transaction-processing-edf1a33ae4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `precompile-call-policy-hardening`

## Code Shape Summary

- Multiple precompile dispatch paths had local delegatecall/callcode checks. The patch routes them through shared common_checks and common policy configuration.

## Search Motifs

- local DELEGATECALL check duplicated in precompile_set
- common_checks introduced at precompile dispatch
- bespoke selector pre_check removed in favor of shared policy

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Centralize call-mode and recursion policy in shared precompile check infrastructure and invoke it from every dispatch path.

## False Match Warnings

- Refactoring to shared checks is not a vulnerability if all old local checks were equivalent
- Pure view precompiles may tolerate broader call modes
- Tests-only check summary changes are not security evidence alone
