# Root-Cause Card

## Metadata

- ID: `stellar-core-2015-08-07-stellar-core-storage-983043fc7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-consensus-configuration`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `safe-consensus-configuration-bounds`

## Violated Invariant

- Invariant: Consensus quorum configuration must derive effective thresholds from bounded parameters and reject trivially unsafe safety settings unless the operator explicitly opts in.

## Trust Boundary

- Boundary: operator-config-file -> consensus-quorum-set-used-at-startup

## Attack Surface

- Entrypoint type: node-configuration-load
- Sensitive sink: SCP quorum threshold and failure-safety configuration
- Attacker capability: Provide or influence node configuration in deployment workflows.
- Main precondition: The node accepts raw detached threshold values or zero failure-safety settings.

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: byzantine-fault-tolerance, configuration-hardening
- Severity guess: high because Unsafe quorum configuration can undermine Byzantine fault tolerance. This is confirmed hardening, not a remote exploit, so high but configuration-scoped.

## Short Reusable Lesson

- Consensus software should make unsafe quorum choices explicit and bounded because operator configuration is part of the protocol safety boundary.
