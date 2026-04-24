# Validation Card

## Metadata

- ID: `rippled-2018-07-27-rippled-consensus-945493d9c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `censorship-detection-observability`

## What Confirmed The Issue

- Evidence 1: Commit message directly frames the change as detecting transaction censorship attempts in XRP Ledger consensus.
- Evidence 2: RCLConsensus.h includes RCLCensorshipDetector, and traced context shows detector state keyed by TxID and ledger sequence.

## What Could Have Invalidated It

- Compensating control 1: No excerpt shows a concrete exploit, attack reproduction, or prior vulnerability condition.
- Compensating control 2: No evidence shows consensus rules were changed to prevent censorship or force transaction inclusion.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: censorship-detection, security-monitoring, auditability
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No excerpt shows a concrete exploit, attack reproduction, or prior vulnerability condition.
- Caution 2: No evidence shows consensus rules were changed to prevent censorship or force transaction inclusion.
