# Code-Shape Card

## Metadata

- ID: `avalanchego-2026-04-30-avalanchego-p2p-networking-a9c2157265`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-allowlist-admission-gap`

## Code Shape Summary

- A transaction admission hook was added before forwarding gossip transactions to the txpool. The reusable shape is an allowlist policy enforced in one ingress path but missing from another mempool forwarding path.

## Search Motifs

- Admitter or allowlist hook added to txgossip addToPool
- txpool.Add called after a new policy check
- batched transaction admission preserves per-transaction errors

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Introduce an admission-policy interface and call it before txpool forwarding, preserving legacy pass-through only when no policy is configured.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- If the backing txpool independently enforces the same allowlist, the missing hook is duplication
- Policy disabled or nil admitter paths may intentionally preserve legacy behavior
- Do not claim block inclusion unless proposer execution uses the same unchecked path
