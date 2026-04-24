# Validation Card

## Metadata

- ID: `reth-2023-11-29-reth-transaction-processing-2c5a748c5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-malleability`

## What Confirmed The Issue

- A new checked recover_signer rejects signatures where s > SECP256K1N_HALF.
- The old behavior is preserved under an explicitly named recover_signer_unchecked compatibility API.

## What Could Have Invalidated It

- No caller-side diff is shown proving validation paths were switched to the checked API
- No evidence shows previously accepted high-s signatures could reach canonical processing after EIP-2 rules should apply

## Severity Guidance

- Expected impact band: signature_or_transaction_authenticity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No caller-side diff is shown proving validation paths were switched to the checked API
- No evidence shows previously accepted high-s signatures could reach canonical processing after EIP-2 rules should apply
