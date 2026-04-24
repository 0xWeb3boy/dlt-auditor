# Validation Card

## Metadata

- ID: `optimism-2024-11-06-optimism-transaction-processing-633aceb2a2`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-metadata-inconsistency`

## What Confirmed The Issue

- Commit message explicitly describes correcting EIP-155-related parity/chain_id coherence in signed legacy transactions.
- recover_v is removed and protected-state is carried explicitly, reducing risk from reconstructing signature metadata after decode.
- decode_tx_sigs merges parity handling into signature decoding, tightening a security-sensitive transaction parsing path.
- TxDeposit::decode now delegates to rlp_decode, which performs explicit RLP type and length checks before field decoding.

## What Could Have Invalidated It

- No proof that malformed span-batch or transaction data was attacker-controlled at a security boundary.
- No demonstration of signature forgery, cross-chain replay, sender confusion, or consensus failure in this repository.
- No test, advisory, incident report, or bug reference showing real-world security impact.
- The patch is also framed as an upstream API/dependency adaptation, which weakens confidence that it was primarily a security fix.

## Severity Guidance

- Expected impact band: signature-or-domain-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that malformed span-batch or transaction data was attacker-controlled at a security boundary.
- No demonstration of signature forgery, cross-chain replay, sender confusion, or consensus failure in this repository.
- No test, advisory, incident report, or bug reference showing real-world security impact.
