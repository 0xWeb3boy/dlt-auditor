# Validation Card

## Metadata

- ID: `rippled-2015-07-28-rippled-core-logic-0bb570a36`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-ledger-compatibility`

## What Confirmed The Issue

- Evidence 1: Adds LedgerMaster::isCompatible to compare a candidate ledger against the current validated ledger.
- Evidence 2: Declares areCompatible helpers for ledgers that could not both be valid.

## What Could Have Invalidated It

- Compensating control 1: No demonstrated exploit path is provided.
- Compensating control 2: No shown consensus fork, validation failure, or attacker-controlled input path is proven.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: state-consistency, consensus-safety
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No demonstrated exploit path is provided.
- Caution 2: No shown consensus fork, validation failure, or attacker-controlled input path is proven.
