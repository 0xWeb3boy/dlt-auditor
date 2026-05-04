# Code-Shape Card

## Metadata

- ID: `stacks-core-2019-11-18-stacks-core-storage-73eb572ac2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-equivocation-detection-gap`

## Code Shape Summary

- The supported finding is a protocol-level microblock equivocation detection fix. The patch broadens conflict handling so signed microblocks that share a parent are treated as conflicting, and PoisonMicroblock deserialization accepts evidence when headers share either sequence number or parent block hash.

## Search Motifs

- Motif 1: lookup by height without fork id or canonical tip
- Motif 2: equivocation evidence requires overly narrow matching fields
- Motif 3: reward set or signer set loaded without canonical context

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Thread canonical chain context into validation and reject evidence or lookups that do not match the active fork/tip rules.

## False Match Warnings

- The value may be used only for display or diagnostics.
- Another validation layer may enforce canonical context before finalization.
