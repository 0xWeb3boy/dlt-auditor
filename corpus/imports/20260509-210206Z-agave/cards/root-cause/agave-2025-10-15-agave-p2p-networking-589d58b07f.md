# Root-Cause Card

## Metadata

- ID: `agave-2025-10-15-agave-p2p-networking-589d58b07f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `connection-rate-limit-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `admission-token-consumption`

## Violated Invariant

- Invariant: Every accepted remote connection attempt should consume the appropriate global and per-peer admission budget before expensive work continues.

## Trust Boundary

- Boundary: `remote-peer->quic-listener`

## Attack Surface

- Entrypoint type: `p2p-connection-admission`
- Sensitive sink: QUIC connection registration and token-bucket rate limiter
- Attacker capability: Open many QUIC connection attempts from one or more IP addresses.
- Key precondition: The limiter exposes a non-consuming allowed check in an admission path.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `resource-exhaustion`
- Severity guidance: `medium` because Remote connection admission is an availability boundary; token-accounting bugs can amplify load, but no concrete DoS reproduction or resource measurements were provided.

## Short Reusable Lesson

- A QUIC ingress path checks whether requests are allowed but does not consistently consume token-bucket capacity at the point where connection work proceeds.
- Structural fix: Replace non-consuming allowance checks with explicit token consumption and add early global request-budget gates before continuing connection handling.
