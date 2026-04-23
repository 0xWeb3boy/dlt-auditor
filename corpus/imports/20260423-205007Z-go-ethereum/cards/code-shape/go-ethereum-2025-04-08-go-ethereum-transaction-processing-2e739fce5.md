# Code-Shape Card

## Metadata

- ID: `go-ethereum-2025-04-08-go-ethereum-transaction-processing-2e739fce5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-resource-exhaustion`

## Code Shape Summary

- The issue was missing EIP-7702-aware txpool admission and reservation policy across blobpool and legacy-pool paths. That gap allowed the spam, eviction, and later cancellation pattern described in the commit message when delegated accounts or pending authorities interacted with blob transactions and SetCode transactions.

## Search Motifs

- Motif 1: transaction admission path missing exact checks for mempool resource exhaustion
- Motif 2: security-sensitive path reaches shared txpool reservation, scheduling, or eviction state before rejecting malformed or unauthorized input
- Motif 3: Add conservative mempool admission checks around EIP-7702 delegation state and shared address reservations: limit delegated senders to one executable blobpool transaction and reject SetCode authorities already reserved elsewhere

## Typical Asymmetry

- Small externally controlled inputs can reach a disproportionately sensitive state, validation, or resource-management sink.

## Patch Pattern

- Add conservative mempool admission checks around EIP-7702 delegation state and shared address reservations: limit delegated senders to one executable blobpool transaction and reject SetCode authorities already reserved elsewhere.

## False Match Warnings

- Classify as txpool resource-control hardening for EIP-7702/blobpool interactions.
- Do not claim a complete fix for all cross-subpool races.
