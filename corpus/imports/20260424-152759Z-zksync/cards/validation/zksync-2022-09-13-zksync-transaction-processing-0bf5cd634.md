# Validation Card

## Metadata

- ID: `zksync-2022-09-13-zksync-transaction-processing-0bf5cd634`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cross-domain-signature-replay`

## What Confirmed The Issue

- Validation builds an EIP-712 domain from chain_id before signer recovery.
- SDK signing now requires chain_id and uses typed-data signing.
- The old ECDSA signing method is deprecated for compatibility only.

## What Could Have Invalidated It

- The legacy signature was already bound to the same chain/domain elsewhere.
- The changed signing path cannot produce authorization accepted by nodes or contracts.

## Severity Guidance

- Expected impact band: `replay_or_account_authorization`
- Expected severity band: `medium_or_low`
- Rationale: Replay hardening for account-control signatures is important, but the evidence stops short of a demonstrated exploit or direct fund loss.

## False-Positive Cautions

- Do not include broad commit claims like reentrancy unless the hunks support them.
- If legacy signatures are only accepted in a non-production compatibility path, severity is lower.
