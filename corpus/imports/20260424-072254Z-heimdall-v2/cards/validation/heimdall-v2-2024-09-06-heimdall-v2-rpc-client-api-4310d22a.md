# Validation Card

## Metadata

- ID: `heimdall-v2-2024-09-06-heimdall-v2-rpc-client-api-4310d22a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-extension-validation`

## What Confirmed The Issue

- Evidence 1: PrepareProposal now validates local last-commit vote extensions with consensus context before proposal construction.
- Evidence 2: ProcessProposal now rejects proposals when centralized vote-extension validation fails, with comments indicating signature and two-thirds-majority checks.

## What Could Have Invalidated It

- Compensating control 1: identical validation was already mandatory in a lower layer before both handlers.
- Compensating control 2: the new helper only rewrapped the same unmarshalling and duplicate checks without added signature, quorum, or validator-set validation.

## Severity Guidance

- Expected impact band: consensus-integrity / validator-attestation-integrity.
- Expected severity band: medium.

## False-Positive Cautions

- Caution 1: do not classify test setup or switch-to-if refactors as the security fix.
- Caution 2: do not claim confirmed forged votes, chain halt, or fund loss without proof beyond the call-site hardening.
