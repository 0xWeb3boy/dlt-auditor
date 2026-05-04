# Root-Cause Card

## Metadata

- ID: `stacks-core-2021-11-15-stacks-core-p2p-networking-57c711ce23`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mainnet-consensus-config-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-consensus-context-validation`

## Violated Invariant

- Invariant: Consensus decisions must validate evidence, fork context, canonical tip monotonicity, and signer sets against the authoritative chain view before accepting results.

## Trust Boundary

- Boundary: Remote peer message crosses into networking, relay, or peer-state validation.

## Attack Surface

- Entrypoint type: `p2p_message_or_block`
- Sensitive sink: peer relay buffer, block acceptance path, or network reputation state

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: configuration-integrity

## Short Reusable Lesson

- The patch adds support for TOML-supplied burnchain epochs and adds guards to reject custom epochs on Mainnet. The evidence supports a configuration safety boundary for a new testnet/regtest feature, but it does not establish that a pre-existing vulnerability was reachable or exploitable.
