# Root-Cause Card

## Metadata

- ID: `stellar-core-2015-06-01-stellar-core-cryptography-a0bd68890`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vblocking-threshold-off-by-one`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-threshold-arithmetic`

## Violated Invariant

- Invariant: A v-blocking set predicate must implement the protocol threshold formula exactly, including off-by-one boundaries for N - T + 1 blocking membership.

## Trust Boundary

- Boundary: received-consensus-statements -> local quorum/blocking-classification

## Attack Surface

- Entrypoint type: consensus-predicate-evaluation
- Sensitive sink: SCP quorum and v-blocking decision logic
- Attacker capability: Participate in or influence observed validator statement sets.
- Main precondition: The implementation computes N - T instead of N - T + 1.

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: consensus-liveness, threshold-misclassification
- Severity guess: high because Consensus threshold arithmetic is safety-critical, but the finding is likely hardening because no concrete network-level exploit is demonstrated.

## Short Reusable Lesson

- Consensus predicates are arithmetic specifications; off-by-one errors at threshold boundaries can turn valid quorum assumptions into wrong safety or liveness decisions.
