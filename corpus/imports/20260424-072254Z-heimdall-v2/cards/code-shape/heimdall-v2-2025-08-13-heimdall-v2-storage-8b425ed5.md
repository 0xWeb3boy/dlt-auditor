# Code-Shape Card

## Metadata

- ID: `heimdall-v2-2025-08-13-heimdall-v2-storage-8b425ed5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-chain-id-validation`

## Code Shape Summary

- A checkpoint side-vote handler validated checkpoint structure without first comparing the message chain ID to trusted local chain configuration. The patch loads chain params, rejects config read failures, and votes NO on chain-ID mismatch.

## Search Motifs

- Motif 1: bridge/checkpoint/state-sync messages include `chainId`, `domainId`, `networkId`, or source chain fields.
- Motif 2: handler calls proof/checkpoint validation before comparing message domain with configured domain.
- Motif 3: patch adds `GetParams` or config lookup followed by mismatch rejection or `VOTE_NO`.

## Typical Asymmetry

- A proof can be structurally valid for the wrong domain unless the handler binds it to local trusted configuration.

## Patch Pattern

- Fetch trusted domain config at the side-vote boundary, fail closed if config is unavailable, and reject mismatched message domains before deeper validation.

## False Match Warnings

- Avoid flagging pure event-preservation or command rewiring changes. Confirm that a trusted-domain comparison was added to a security-sensitive validation path.
