# Code-Shape Card

## Metadata

- ID: `zksync-2022-09-13-zksync-transaction-processing-0bf5cd634`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cross-domain-signature-replay`

## Code Shape Summary

- ChangePubKey Ethereum authorization moves from raw-message ECDSA toward EIP-712 typed data with an explicit chain_id domain, and the legacy SDK signing path is deprecated. The reusable shape is an account-control signature verified without sufficient domain/action binding.

## Search Motifs

- Eip712Domain::new(chain_id) added near signer recovery
- sign_typed_data replaces sign_message for account key-change auth
- legacy ECDSA ChangePubKey method deprecated or hidden

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Require chain_id, construct an EIP-712 domain, sign and verify typed transaction data, and steer normal callers away from raw legacy signatures.

## False Match Warnings

- Do not include broad commit claims like reentrancy unless the hunks support them.
- If legacy signatures are only accepted in a non-production compatibility path, severity is lower.
- EIP-712 adoption is not always a security fix without a replay-sensitive action.
