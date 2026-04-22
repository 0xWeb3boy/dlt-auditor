# Root-Cause Card

## Metadata

- ID: `base-2026-04-15-base-consensus-6f64e2506`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: The RPC ingress should place a bounded limit on concurrent work, reject excess requests when saturated, and ensure request timeouts include time spent waiting for admission so burst traffic cannot create unbounded internal backlog against downstream actor channels.

## Trust Boundary

- Boundary: `on-chain dispute or engine state->off-chain consensus actor`

## Attack Surface

- Entrypoint type: `rpc-or-network-ingress`
- Sensitive sink: `admission of work into shared network, RPC, or challenger resources`

## Impact Pattern

- Primary impact: `availability`
- Secondary impact: `none`

## Short Reusable Lesson

- The RPC ingress should place a bounded limit on concurrent work, reject excess requests when saturated, and ensure request timeouts include time spent waiting for admission so burst traffic cannot create unbounded internal backlog against downstream actor channels. Missing admission control at the RPC ingress. In the provided pre-patch code, requests were subject to a timeout but not to an explicit concurrency bound or immediate overload rejection path, leaving the service more exposed to backlog growth under bursty or flood-like request pressure. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
