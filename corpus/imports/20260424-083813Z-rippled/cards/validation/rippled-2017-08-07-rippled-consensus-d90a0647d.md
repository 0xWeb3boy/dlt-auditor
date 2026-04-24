# Validation Card

## Metadata

- ID: `rippled-2017-08-07-rippled-consensus-d90a0647d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## What Confirmed The Issue

- Evidence 1: Commit message explicitly mentions Byzantine fault tolerance and preventing quorum 0.
- Evidence 2: Main.cpp now rejects configured quorum value 0 instead of accepting it.

## What Could Have Invalidated It

- Compensating control 1: No proof that an attacker can control the quorum configuration.
- Compensating control 2: No proof that validator lists are attacker-controlled in the affected deployment model.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: consensus-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No proof that an attacker can control the quorum configuration.
- Caution 2: No proof that validator lists are attacker-controlled in the affected deployment model.
