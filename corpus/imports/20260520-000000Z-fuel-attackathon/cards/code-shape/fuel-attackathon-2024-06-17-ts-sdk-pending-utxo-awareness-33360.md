# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ts-sdk-pending-utxo-awareness-33360`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `pending-utxo-reservation-missing`

## Code Shape Summary

- The SDK selected UTXOs only from confirmed GraphQL state and kept no local pending-spend reservation set.

## Search Motifs

- getResourcesToSpend stateless
- fund multiple transactions same block
- already used UTXO
- pending transaction input reservation

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Track locally reserved pending UTXOs or query txpool-aware resources, and exclude them when funding subsequent transactions.

## False Match Warnings

- No issue if the wallet serializes funding until prior transactions confirm.
- No issue if node resource queries exclude txpool-pending inputs for that owner.
