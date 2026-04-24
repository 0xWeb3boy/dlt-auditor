# Validation Card

## Metadata

- ID: `rippled-2025-09-16-rippled-consensus-159d7311d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-ordering-hardening`

## What Confirmed The Issue

- Evidence 1: CanonicalTXSet::accountKey changes from zero-padding AccountID and XORing salt_ to cryptographic BLAKE3 mixing when canonicalFix_ is enabled.
- Evidence 2: RCLConsensus::Adaptor::doAccept passes the fixCanonicalTxSet validated-rule flag into CanonicalTXSet for consensus retry transaction ordering.

## What Could Have Invalidated It

- Compensating control 1: No supplied evidence shows an actual exploit path against the old XOR construction.
- Compensating control 2: No supplied evidence demonstrates validator disagreement, ledger fork, replay, authorization bypass, or denial of service.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: transaction-ordering-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No supplied evidence shows an actual exploit path against the old XOR construction.
- Caution 2: No supplied evidence demonstrates validator disagreement, ledger fork, replay, authorization bypass, or denial of service.
