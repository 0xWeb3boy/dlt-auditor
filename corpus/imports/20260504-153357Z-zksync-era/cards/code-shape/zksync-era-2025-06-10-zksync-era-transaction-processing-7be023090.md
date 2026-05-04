# Code-Shape Card

## Metadata

- ID: `zksync-era-2025-06-10-zksync-era-transaction-processing-7be023090`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The supported security-relevant change is that private RPC dispatch moved away from permissive fallback delegation and blacklist-style filtering toward explicit handler allowlisting. The strongest direct evidence is that the default handler for unregistered methods changed from forwarding the caller-supplied method and params to the target RPC to returning an unauthorized response.

## Search Motifs

- Motif 1: JSON-RPC proxy falls back to forwarding unknown methods to an upstream target.
- Motif 2: Registry blocks selected forbidden methods instead of requiring explicit allowed handlers.
- Motif 3: Patch changes default handler from delegate/forward to unauthorized.

## Typical Asymmetry

- The proxy's intended API surface is narrower than the upstream RPC surface; fallback delegation erases that boundary.

## Patch Pattern

- Replace fallback forwarding and blacklist filtering with explicit allowlisting, deny unknown methods, and add coverage checks for handler registration.

## False Match Warnings

- A fallback to a safe local error handler is not vulnerable. A trusted-only internal proxy with an upstream allowlist may reduce severity.
