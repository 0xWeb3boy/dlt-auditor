# Validation Card

## Metadata

- ID: `reth-2023-04-11-reth-transaction-processing-e0e449d5f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-input-validation`

## What Confirmed The Issue

- Legacy signature decoding now rejects v values other than 27 or 28.
- Pre-patch code derived parity from (v - 27) != 0 without explicit legacy-value validation.

## What Could Have Invalidated It

- No proof that malformed legacy v values were accepted into execution or consensus-critical flows
- No test or report showing signature forgery, replay, chain split, or sender-recovery abuse

## Severity Guidance

- Expected impact band: signature_or_transaction_authenticity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that malformed legacy v values were accepted into execution or consensus-critical flows
- No test or report showing signature forgery, replay, chain split, or sender-recovery abuse
