# Code-Shape Card

## Metadata

- ID: `sei-chain-2024-05-09-sei-chain-transaction-processing-b36bfe41b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-or-signature-validation`

## Code Shape Summary

- The patch adds explicit chain ID checks in `x/evm/ante/sig.go` within `EVMSigVerifyDecorator.AnteHandle`. It reads the configured EVM chain ID from the keeper, reads `ethTx.ChainId()`, switches on the Ethereum transaction type, and for legacy transactions allows either chain ID zero or the configured chain ID while rejecting other nonzero chain IDs with `sdkerrors.ErrInvalidChainID`.

## Search Motifs

- Motif 1: ethTx.ChainId not compared with configured chain ID
- Motif 2: legacy tx allows arbitrary nonzero chain ID
- Motif 3: sig verifier proceeds before replay-domain check

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Validate replay-domain fields during admission, preserving explicit legacy compatibility only where intended.

## False Match Warnings

- A later signer implementation rejects mismatched chain IDs before state changes.
- The path is simulation-only and cannot broadcast transactions.
