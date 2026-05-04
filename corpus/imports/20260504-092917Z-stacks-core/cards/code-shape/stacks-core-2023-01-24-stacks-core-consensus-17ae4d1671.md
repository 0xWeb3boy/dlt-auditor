# Code-Shape Card

## Metadata

- ID: `stacks-core-2023-01-24-stacks-core-consensus-17ae4d1671`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-unaware-consensus-lookup`

## Code Shape Summary

- The patch appears to fix a consensus-relevant fork-awareness bug in burnchain database lookups. Before the change, some paths selected burnchain operations or anchor block commit metadata using identifiers that did not include burnchain fork context. The patch adds burn block hash/header context to operation lookup and changes anchor metadata selection so canonical fork context can be considered before choosing the commit used in affirmation-map construction.

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
