# Code-Shape Card

## Metadata

- ID: `fuel-core-2022-03-02-fuel-core-storage-10a47d0a77`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `block-malleability`

## Code Shape Summary

- Execution code recorded transaction status and commitment material while the block id or canonical transaction bytes were still provisional, then later finalized the block through a separate path.

## Search Motifs

- status persisted before block id is finalized
- commitment built from pre-malleated transaction
- witness data omitted from transaction root
- placeholder block id in transaction status

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Delay status persistence until final block identity is available and compute commitments from canonical serialized transaction data, including witness-bearing malleated fields.

## False Match Warnings

- Pure refactors of transaction status storage are not enough without a commitment/status ordering issue.
- If canonical serialization is already the sole commitment input before persistence, the motif is not a bug.
