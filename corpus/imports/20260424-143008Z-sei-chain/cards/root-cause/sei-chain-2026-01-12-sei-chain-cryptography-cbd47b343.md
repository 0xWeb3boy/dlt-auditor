# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-01-12-sei-chain-cryptography-cbd47b343`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `traffic-analysis-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `encrypted-frame-size-obfuscation`

## Violated Invariant

- Invariant: Encrypted transports should avoid exposing application write boundaries or message lengths when the protocol promises fixed-size framing.

## Trust Boundary

- Boundary: application p2p writes -> encrypted transport frames visible to network observers

## Attack Surface

- Entrypoint type: encrypted-connection-write-path
- Sensitive sink: emitting ciphertext frames with observable sizes/timing

## Impact Pattern

- Primary impact: metadata-leakage-reduction
- Secondary impact: traffic-analysis-mitigation

## Short Reusable Lesson

- Move send buffering into the encrypted transport layer so encrypted frame emission can be governed by protocol framing rules rather than by raw application write boundaries. Reduces potential leakage of application write sizes through ciphertext frame boundaries. Keeps buffering responsibility inside the encrypted transport layer.
