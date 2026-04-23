# Validation Card

## Metadata

- ID: `go-ethereum-2016-10-28-go-ethereum-transaction-processing-b59c8399f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-separation`

## What Confirmed The Issue

- Evidence 1: Commit body states eth_sign now prefixes arbitrary messages with the Ethereum Signed Message string, hashes with keccak256, then signs.
- Evidence 2: crypto.Sign documentation explicitly warns that chosen-plaintext signing can leak private-key information and advises hashing input before signing.

## What Could Have Invalidated It

- Compensating control 1: Classify as RPC/account-signing hardening, not transaction-processing.
- Compensating control 2: Do not claim a confirmed transaction replay vulnerability.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Classify as RPC/account-signing hardening, not transaction-processing.
- Caution 2: Do not claim a confirmed transaction replay vulnerability.
