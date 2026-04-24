# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-08-18-sei-chain-transaction-processing-d35634422`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-legacy-transaction-acceptance`

## Code Shape Summary

- The patch changes EVM transaction preprocessing so unprotected legacy Ethereum transactions are rejected during normal operation. Previously, when `ethTx.Protected()` was false, `Preprocess` still computed the transaction hash with `ethtypes.FrontierSigner{}.Hash(ethTx)` and continued to sender derivation. After the patch, that fallback is allowed only when `isBlockTest` is enabled;

## Search Motifs

- Motif 1: ethTx.Protected false branch continues in production
- Motif 2: FrontierSigner hash used as fallback
- Motif 3: isBlockTest or test mode exception missing

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Fail closed on unsafe legacy transaction formats in normal operation and isolate compatibility behavior behind test flags.

## False Match Warnings

- The network intentionally supports unprotected legacy transactions and scopes them safely.
- A later ante stage rejects the transaction before execution.
