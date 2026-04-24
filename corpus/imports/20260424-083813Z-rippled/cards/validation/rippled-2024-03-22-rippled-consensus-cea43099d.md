# Validation Card

## Metadata

- ID: `rippled-2024-03-22-rippled-consensus-cea43099d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-desync-hardening`

## What Confirmed The Issue

- Evidence 1: Consensus code previously returned true immediately when total proposals were zero.
- Evidence 2: The commit message states this could cause a peer to desync and close a non-validated ledger.

## What Could Have Invalidated It

- Compensating control 1: No proof that an attacker can deliberately trigger delayed proposal delivery or the timing condition.
- Compensating control 2: No demonstrated theft, double spend, ledger forgery, or consensus safety break.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: consensus-integrity, node-desynchronization
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No proof that an attacker can deliberately trigger delayed proposal delivery or the timing condition.
- Caution 2: No demonstrated theft, double spend, ledger forgery, or consensus safety break.
