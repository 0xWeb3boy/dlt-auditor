# Root-Cause Card

## Metadata

- ID: `base-2026-04-07-base-cryptography-aa3b6d3ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: The network-facing publish listener must bound in-flight connection setup and broadcast work so new unauthenticated connections cannot drive unbounded memory or executor consumption before timeout-based cleanup occurs.

## Trust Boundary

- Boundary: `signed or encoded input->verification routine`

## Attack Surface

- Entrypoint type: `rpc-or-network-ingress`
- Sensitive sink: `admission of work into shared network, RPC, or challenger resources`

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `availability`

## Short Reusable Lesson

- The network-facing publish listener must bound in-flight connection setup and broadcast work so new unauthenticated connections cannot drive unbounded memory or executor consumption before timeout-based cleanup occurs. Missing admission control in the listener accept loop allowed connection pressure to create too many concurrent handshake and broadcast tasks before existing timeout mechanisms reclaimed resources. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
