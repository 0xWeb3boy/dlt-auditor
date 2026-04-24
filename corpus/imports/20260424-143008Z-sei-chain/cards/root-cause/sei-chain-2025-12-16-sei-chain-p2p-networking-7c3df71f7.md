# Root-Cause Card

## Metadata

- ID: `sei-chain-2025-12-16-sei-chain-p2p-networking-7c3df71f7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-peer-resource-abuse-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `bounded-peer-penalty-scope`

## Violated Invariant

- Invariant: Peer blacklisting for transaction validation failures must count only clear abuse conditions and be enabled with safe default scope.

## Trust Boundary

- Boundary: remote mempool transaction sender -> peer eviction policy

## Attack Surface

- Entrypoint type: mempool-checktx-failure-handler
- Sensitive sink: blacklisting or evicting a peer for validation failures

## Impact Pattern

- Primary impact: resource-exhaustion
- Secondary impact: peer-abuse-mitigation

## Short Reusable Lesson

- Narrow a peer-penalty mechanism to a bounded abuse condition, centralize the counter/eviction logic behind explicit guards, then enable the narrowed defensive control by default. Helps bound repeated peer submissions of oversized transactions. Makes the narrowed blacklist defense active under default configuration.
