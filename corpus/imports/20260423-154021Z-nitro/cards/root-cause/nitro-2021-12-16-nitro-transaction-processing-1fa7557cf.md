# Root-Cause Card

## Metadata

- ID: `nitro-2021-12-16-nitro-transaction-processing-1fa7557cf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-default-service-exposure`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `explicit-service-enable-gating`

## Violated Invariant

- Invariant: A relay, broadcaster, or similar externally reachable service should stay disabled unless the operator explicitly enables it and supplies the security-relevant configuration that path depends on.

## Trust Boundary

- Boundary: `operator configuration->network-facing broadcaster or relay startup`

## Attack Surface

- Entrypoint type: `node-startup-or-configuration`
- Sensitive sink: `enabling a network-facing service or feed output path`

## Impact Pattern

- Primary impact: `network-service-exposure`
- Secondary impact: `none`

## Short Reusable Lesson

- A relay, broadcaster, or similar externally reachable service should stay disabled unless the operator explicitly enables it and supplies the security-relevant configuration that path depends on. The provided diff supports a configuration refactor in node startup, not a demonstrated vulnerability fix. It consolidates broadcaster settings into NodeConfig, renames the CLI flags, and removes a separate CreateNode parameter for feed output configuration. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
