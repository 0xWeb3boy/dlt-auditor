# Validation Card

## Metadata

- ID: `go-ethereum-2015-03-25-go-ethereum-cryptography-de7af720d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-reflection-amplification`

## What Confirmed The Issue

- Evidence 1: Commit message explicitly identifies a DDoS amplification attack vector using spoofed findnode source addresses.
- Evidence 2: Inline code comment at the new findnode guard describes preventing the same amplification attack.

## What Could Have Invalidated It

- Compensating control 1: Applies to UDP discovery findnode handling and neighbors responses.
- Compensating control 2: Supports a DDoS reflection/amplification fix, not a general cryptography vulnerability.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Applies to UDP discovery findnode handling and neighbors responses.
- Caution 2: Supports a DDoS reflection/amplification fix, not a general cryptography vulnerability.
