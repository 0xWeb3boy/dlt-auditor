# Root-Cause Card

## Metadata

- ID: `nibiru-2026-01-28-nibiru-rpc-client-api-9d08af56`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vulnerable-dependency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `patched dependency baseline`

## Violated Invariant

- Invariant: Consensus and networking dependencies with published security advisories must be upgraded to a patched version across every module that can build or test the node.

## Trust Boundary

- Boundary: Application dependency lockfiles cross into upstream consensus/networking implementation code.

## Attack Surface

- Entrypoint type: build-time dependency selection for node, SDK, and test modules
- Sensitive sink: CometBFT consensus/networking library version used by the application

## Impact Pattern

- Primary impact: upstream vulnerability remediation
- Secondary impact: consensus or network exposure depending on advisory

## Short Reusable Lesson

- A security advisory remediation upgraded the CometBFT dependency to a patched version across module manifests and checksums.
