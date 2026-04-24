# Root-Cause Card

## Metadata

- ID: `sei-chain-2024-05-03-sei-chain-transaction-processing-e8e4b3bf4`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `subscription-resource-limit`

## Violated Invariant

- Invariant: Long-lived RPC subscriptions must be bounded before listener allocation or registration.

## Trust Boundary

- Boundary: remote RPC/WebSocket client -> node subscription resources

## Attack Surface

- Entrypoint type: rpc-subscription-handler
- Sensitive sink: allocating and retaining listener/subscription state

## Impact Pattern

- Primary impact: availability-hardening
- Secondary impact: availability-or-resource-control

## Short Reusable Lesson

- Add a configuration-backed resource limit at the allocation/registration point, and perform the count-and-insert sequence under the mutex protecting the listener map. Bounds active server-side eth_newHeads listener registration. Rejects excess subscriptions before insertion into the tracked listener map. Reduces plausible resource-exhaustion risk in the websocket subscription service.
