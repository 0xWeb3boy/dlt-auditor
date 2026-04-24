# Validation Card

## Metadata

- ID: `rippled-2019-03-05-rippled-transaction-processing-c5a938de5`
- Bug family: `authz_and_role_gates`
- Bug class: `regular-key-authorization-hardening`

## What Confirmed The Issue

- Evidence 1: SetRegularKey::preflight adds an amendment-gated rejection when sfRegularKey equals sfAccount, returning temBAD_REGKEY.
- Evidence 2: Transactor::checkSingleSign is in the transaction authorization path and is reworked around signing public key validation, signer account derivation, account lookup, and...

## What Could Have Invalidated It

- Compensating control 1: No evidence shows an unauthorized third party could set another account's regular key.
- Compensating control 2: No evidence demonstrates transaction forgery, account takeover, or direct fund loss.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: authorization-integrity, key-management-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No evidence shows an unauthorized third party could set another account's regular key.
- Caution 2: No evidence demonstrates transaction forgery, account takeover, or direct fund loss.
