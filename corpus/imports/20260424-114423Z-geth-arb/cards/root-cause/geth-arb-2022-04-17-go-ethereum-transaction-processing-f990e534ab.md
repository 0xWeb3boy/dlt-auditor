# Root-Cause Card

## Metadata

- ID: `geth-arb-2022-04-17-go-ethereum-transaction-processing-f990e534ab`
- Bug family: `authz_and_role_gates`
- Bug class: `container-least-privilege-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `runtime-least-privilege`

## Violated Invariant

- Invariant: Service containers should run with the minimum user privileges needed so application compromise does not immediately become root-level container control.

## Trust Boundary

- Boundary: container image/runtime -> host and container privilege boundary

## Attack Surface

- Entrypoint type: deployment image startup
- Sensitive sink: process privileges inside the production container

## Impact Pattern

- Primary impact: privilege-containment
- Secondary impact: deployment-hardening
- Severity guide: low-medium

## Short Reusable Lesson

- The node distribution image ran as root and was hardened by switching the runtime user to a non-root account. Create/select an unprivileged user in the image and set it as the default runtime identity.
