# Root-Cause Card

## Metadata

- ID: `nitro-2024-12-20-nitro-transaction-processing-a719c5c92`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-machine-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `round-bound-state-machine`

## Violated Invariant

- Invariant: Round-scoped sequencing logic should stop when the round or authorization context changes and should not advance to the next queued item until the current item is explicitly acknowledged.

## Trust Boundary

- Boundary: `queued privileged submissions->round-scoped sequencing loop`

## Attack Surface

- Entrypoint type: `sequencing-or-queue-processing`
- Sensitive sink: `sequencing an express-lane or otherwise privileged transaction`

## Impact Pattern

- Primary impact: `transaction-ordering-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Round-scoped sequencing logic should stop when the round or authorization context changes and should not advance to the next queued item until the current item is explicitly acknowledged. This patch tightens express-lane transaction sequencing by binding processing to the current round and adding an explicit notifier before advancing to the next queued transaction. The code is security-relevant, and one inline comment mentions a security concern, but the provided evidence does not establish a concrete vulnerability or exploit path. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
