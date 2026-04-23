# Code-Shape Card

## Metadata

- ID: `go-ethereum-2021-02-23-go-ethereum-transaction-processing-142fbcfd6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-replay-protection-enforcement`

## Code Shape Summary

- The patch hardens go-ethereum RPC transaction submission by rejecting non-EIP-155, non-replay-protected transactions before SendTx unless rpc.allow-unprotected-txs is explicitly enabled.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
