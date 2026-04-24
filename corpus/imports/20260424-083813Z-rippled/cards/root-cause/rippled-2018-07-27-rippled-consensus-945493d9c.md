# Root-Cause Card

## Metadata

- ID: `rippled-2018-07-27-rippled-consensus-945493d9c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `censorship-detection-observability`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-safety-invariant`

## Violated Invariant

- Invariant: Consensus participants must only advance local safety or liveness state from messages that satisfy the current quorum, ordering, timing, and validator-role rules.

## Trust Boundary

- Boundary: peer/validator consensus data -> local consensus and ledger-close machinery

## Attack Surface

- Entrypoint type: consensus-message-or-ledger-close-path
- Sensitive sink: ledger close decision, validator set decision, or consensus safety state

## Impact Pattern

- Primary impact: censorship-detection, security-monitoring, auditability
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch is best classified as security hardening for censorship observability in rippled consensus processing.
