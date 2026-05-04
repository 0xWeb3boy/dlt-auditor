# Code-Shape Card

## Metadata

- ID: `stacks-core-2021-11-15-stacks-core-p2p-networking-57c711ce23`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mainnet-consensus-config-hardening`

## Code Shape Summary

- The patch adds support for TOML-supplied burnchain epochs and adds guards to reject custom epochs on Mainnet. The evidence supports a configuration safety boundary for a new testnet/regtest feature, but it does not establish that a pre-existing vulnerability was reachable or exploitable.

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
