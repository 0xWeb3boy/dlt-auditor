# Root-Cause Card

## Metadata

- ID: `zksync-era-2025-06-10-zksync-era-transaction-processing-7be023090`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A private RPC proxy must expose only explicitly registered and reviewed methods; unknown methods must not be forwarded by default.

## Trust Boundary

- Boundary: External JSON-RPC callers cross into a private upstream RPC target.

## Attack Surface

- Entrypoint type: JSON-RPC method dispatch.
- Sensitive sink: Upstream RPC method execution with caller-supplied method and params.

## Impact Pattern

- Primary impact: Unauthorized private RPC method exposure.
- Secondary impact: Reduced risk from blacklist gaps and newly added upstream methods.

## Short Reusable Lesson

- RPC proxies should fail closed. If a method is not in the reviewed handler registry, the proxy should reject it rather than transparently delegating it upstream.
