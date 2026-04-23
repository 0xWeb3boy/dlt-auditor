# Root-Cause Card

## Metadata

- ID: `go-ethereum-2022-06-29-go-ethereum-cryptography-d12b1a91c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-terminal-block-validation-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `consensus-validation`

## Violated Invariant

- Invariant: During the Merge transition, a mixed PoW/PoS header batch must treat only the final pre-PoS PoW header as the valid terminal PoW block; earlier pre-headers must not already have crossed the configured terminal total difficulty.

## Trust Boundary

- Boundary: Peer-supplied synchronization or protocol data crossing into local validation and scheduling logic.

## Attack Surface

- Entrypoint type: `p2p message`
- Sensitive sink: `canonical-chain selection or persistent chain-state update`

## Impact Pattern

- Primary impact: `consensus-validation`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The patch fixes a consensus validation gap in go-ethereum's beacon transition header verification.
