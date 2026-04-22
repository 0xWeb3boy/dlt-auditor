# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-05-07-oasis-core-rpc-client-api-e55738ce6`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `key-scope-isolation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `key-scope-isolation`

## Violated Invariant

- Invariant: Key-management responses and stored key material should be scoped to the intended runtime or contract and authenticated through the runtime attestation key when exposed over shared runtime paths. The provided snippets suggest movement toward that model, but they do not establish the full protocol or a concrete violated invariant before the patch.

## Trust Boundary

- Boundary: `remote-peer->rpc-verifier`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: `attestation acceptance state`

## Impact Pattern

- Primary impact: `cross-scope-data-access`
- Secondary impact: `authenticated-response-integrity`

## Short Reusable Lesson

- Key-management responses and stored key material should be scoped to the intended runtime or contract and authenticated through the runtime attestation key when exposed over shared runtime paths. The provided snippets suggest movement toward that model, but they do not establish the full protocol or a concrete violated invariant before the patch. In this pattern, not established by the provided evidence. At most, the patch appears to tighten an incompletely integrated keymanager/runtime design by routing signing through a shared interface and reducing handler scope, but the snippets do not prove the original flaw beyond that. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
