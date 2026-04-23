# Validation Card

## Metadata

- ID: `go-ethereum-2022-06-29-go-ethereum-cryptography-d12b1a91c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-terminal-block-validation-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject states the invariant: only the latest PoW block is a valid TTD block.
- Evidence 2: Beacon header verification now calls verifyTerminalPoWBlock before collecting mixed PoW/PoS verification results.

## What Could Have Invalidated It

- Compensating control 1: Classify as consensus validation hardening, not a proven exploitable vulnerability.
- Compensating control 2: Do not claim cryptographic primitive failure or signature-validation weakness.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: Classify as consensus validation hardening, not a proven exploitable vulnerability.
- Caution 2: Do not claim cryptographic primitive failure or signature-validation weakness.
