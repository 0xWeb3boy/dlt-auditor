# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-06-28-stacks-core-storage-4fd033f283`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-fork-context-reward-set-lookup`

## Code Shape Summary

- Likely security-relevant consensus/liveness fix in the Nakamoto coordinator. The patch changes reward-cycle handling to use or justify the correct fork context for reward-set lookup, with comments explaining why the canonical tip is safe at the end of prepare phase and why local-best use is only safe for the first Nakamoto reward set. The evidence supports a canonical fork-context lookup issue, but does not prove exploitability, invalid block acceptance, or a malformed transaction panic.

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
