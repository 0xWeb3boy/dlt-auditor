# Code-Shape Card

Record: `omni-cantina-h04-malformed-consensus-pubkey-admission`
Project: `omni-network`
Source finding: `Omni Cantina H-4`

## Search Shape

The source contract and native adapter enforce key length but not curve membership; a later valsync path finally decompresses and fails.

## Motifs

- `pubkey.length == 33`
- `PubKeyBytesToCosmos`
- `CreateValidator`
- `DecompressPubkey`
- `not on secp256k1 curve`
- `insertValidatorSet`

## Negative Signals

- The first value-accepting path decompresses and curve-checks the key.
- Malformed keys are rejected atomically before source finality.
- Downstream consumers never require semantic decompression.

## Likely Fix Shape

Validate compressed secp256k1 public keys at createValidator or deliverCreateValidator before accepting/storing the validator creation.
