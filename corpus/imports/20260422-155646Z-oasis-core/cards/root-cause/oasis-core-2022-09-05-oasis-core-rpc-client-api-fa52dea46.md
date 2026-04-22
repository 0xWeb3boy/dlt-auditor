# Root-Cause Card

## Metadata

- ID: `oasis-core-2022-09-05-oasis-core-rpc-client-api-fa52dea46`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `freshness-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `freshness`

## Violated Invariant

- Invariant: If client or TEE freshness is enforced, the decision should rely on recent consensus-anchored evidence rather than a bare transaction-submission success result. The provided excerpts only show plumbing toward that invariant, not the full enforcement point.

## Trust Boundary

- Boundary: `remote-peer->rpc-verifier`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: `attestation acceptance state`

## Impact Pattern

- Primary impact: `stale-attestation-acceptance`
- Secondary impact: `none`

## Short Reusable Lesson

- If client or TEE freshness is enforced, the decision should rely on recent consensus-anchored evidence rather than a bare transaction-submission success result. The provided excerpts only show plumbing toward that invariant, not the full enforcement point. In this pattern, not established by the provided evidence. The observable change is that the runtime-host path previously lacked an end-to-end way to submit a freshness-related transaction and receive a consensus inclusion proof back through the API layers. The excerpts do not show whether stale TEE evidence was previously accepted, where verification happened, or whether this is a new feature versus a fix for an exploitable bug. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
