# Root-Cause Card

## Metadata

- ID: `bor-2026-01-27-bor-rpc-client-api-df8f2a879`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-peer-data-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource limit and input validity enforcement`

## Violated Invariant

- Invariant: RPC-facing code must fail closed and enforce request limits and authorization before exposing backend state or privileged behavior.

## Trust Boundary

- Boundary: external RPC client to node service boundary

## Attack Surface

- Entrypoint type: public or administrative RPC method
- Sensitive sink: backend state access, privileged API behavior, or response serialization

## Impact Pattern

- Primary impact: integrity-risk
- Secondary impact: resource-exhaustion

## Short Reusable Lesson

- The visible issue is that the shown witness-fetch call sites did not consistently use the verification-aware request path. The patch centralizes those requests and adds a metadata-query helper with basic guards. The provided evidence does not prove a stronger root cause such as a consensus break, full witness forgery acceptance, or a demonstrated denial-of-service vulnerability.
