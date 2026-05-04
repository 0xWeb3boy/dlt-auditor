# Code-Shape Card

## Metadata

- ID: `stellar-core-2015-02-28-stellar-core-transaction-processing-117a83b23`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-transaction-sequence-validation`

## Code Shape Summary

- The apply path accepted a transaction after broad validation while the supporting sequence read was not keyed by every dimension of the sequence invariant.

## Search Motifs

- transaction apply continues after checkValid without sequence comparison
- sequence lookup by account id without sequence slot
- bad sequence checked only during mempool admission
- fee handling for bad sequence transactions

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Add an explicit pre-application bad-sequence guard and make the ledger lookup use the same account and slot keys required by the invariant.

## False Match Warnings

- Pure test changes around sequence numbers are not enough without an apply-path guard.
- A separate consensus rule may already reject wrong sequence slots before application.
- Single-slot account sequence systems do not need per-slot lookup dimensions.
