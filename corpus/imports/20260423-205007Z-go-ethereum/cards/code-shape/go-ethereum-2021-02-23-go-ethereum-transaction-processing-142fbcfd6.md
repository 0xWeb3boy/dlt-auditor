# Code-Shape Card

## Metadata

- ID: `go-ethereum-2021-02-23-go-ethereum-transaction-processing-142fbcfd6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-replay-protection-enforcement`

## Code Shape Summary

- The RPC submission path did not show a default validation gate requiring EIP-155 replay protection before forwarding submitted transactions to SendTx. The provided evidence does not establish whether later code could also reject such transactions.

## Search Motifs

- Motif 1: rpc method missing exact checks for missing replay protection enforcement
- Motif 2: security-sensitive path reaches expensive RPC-side computation, allocation, or response construction before rejecting malformed or unauthorized input
- Motif 3: Add a default-deny validation gate at the RPC boundary for replay-sensitive legacy transaction inputs, with an explicit configuration override for compatibility

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Add a default-deny validation gate at the RPC boundary for replay-sensitive legacy transaction inputs, with an explicit configuration override for compatibility.

## False Match Warnings

- Classify as default-policy security hardening, not a proven vulnerability fix.
- Do not claim state corruption is demonstrated by the patch.
