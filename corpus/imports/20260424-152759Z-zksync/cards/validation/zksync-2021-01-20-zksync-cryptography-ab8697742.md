# Validation Card

## Metadata

- ID: `zksync-2021-01-20-zksync-cryptography-ab8697742`
- Bug family: `authz_and_role_gates`
- Bug class: `transaction-authentication-hardening`

## What Confirmed The Issue

- CREATE2 accounts now reject supplied Ethereum signature data.
- The rejection is applied to both single and batch verification paths.
- A panic on disabled Close account_id access is replaced with an error.

## What Could Have Invalidated It

- The extra signature field was ignored before all security decisions.
- The modified path is not reachable from submitted transactions.

## Severity Guidance

- Expected impact band: `authorization_hardening`
- Expected severity band: `medium_or_low`
- Rationale: Rejecting mismatched auth data is security-relevant, but validation did not prove a bypass or remotely triggerable DoS.

## False-Positive Cautions

- If CREATE2 address derivation was already the only accepted authority, rejecting extra signatures may be cleanup.
- A panic in unreachable disabled transaction code is not automatically exploitable.
