# Root-Cause Card

## Metadata

- ID: `bor-2022-05-23-bor-rpc-client-api-1b5304405`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `privileged-api-exposure`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `consensus invariant enforcement`

## Violated Invariant

- Invariant: RPC-facing code must fail closed and enforce request limits and authorization before exposing backend state or privileged behavior.

## Trust Boundary

- Boundary: external RPC client to node service boundary

## Attack Surface

- Entrypoint type: public or administrative RPC method
- Sensitive sink: backend state access, privileged API behavior, or response serialization

## Impact Pattern

- Primary impact: unauthorized-signing
- Secondary impact: exposed-wallet-surface

## Short Reusable Lesson

- The shown code mixed server-local signing setup with the node-wide account manager and did not explicitly track the case where consensus authorization had already been completed before StartMining. The evidence supports a design-tightening change, not a demonstrated exploit.
