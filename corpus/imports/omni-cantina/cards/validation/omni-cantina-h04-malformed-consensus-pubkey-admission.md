# Validation Card

Record: `omni-cantina-h04-malformed-consensus-pubkey-admission`
Project: `omni-network`
Source finding: `Omni Cantina H-4`

## Positive Confirmation

Trace length-only pubkey acceptance through deliverCreateValidator to valsync DecompressPubkey.

## Preconditions To Confirm

- Staking.sol checks only pubkey length.
- deliverCreateValidator converts bytes without curve validation.
- valsync later decompresses the key in FinalizeBlock.

## False-Positive Cautions

- All reachable callers are forced through a CLI that validates keys and direct contract calls are impossible.
- The native adapter rejects off-curve keys before Cosmos staking.
- The error is handled without consensus callback failure.

## Minimal Reproduction Or Check

Submit a 33-byte off-curve key and assert the fixed path rejects before validator creation or deposit acceptance.
