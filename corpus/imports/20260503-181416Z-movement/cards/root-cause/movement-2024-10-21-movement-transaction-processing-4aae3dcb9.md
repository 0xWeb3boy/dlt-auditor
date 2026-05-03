# Root-Cause Card

## Metadata

- ID: `movement-2024-10-21-movement-transaction-processing-4aae3dcb9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sequence-number-admission`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `centralized-duplicate-sequence-admission-guard`

## Violated Invariant

- Invariant: Every transaction admission route must apply the same sender sequence-number validity check before forwarding or storing a transaction; duplicate submissions should not bypass the shared guard.

## Trust Boundary

- Boundary: User transaction submission crossing from client/test harness into execution mempool forwarding.

## Attack Surface

- Entrypoint type: transaction submission path
- Sensitive sink: mempool forwarding or downstream execution scheduling

## Impact Pattern

- Primary impact: Duplicate transaction admission or forwarding.
- Secondary impact: Replay/order hardening and reduced unnecessary mempool work.

## Short Reusable Lesson

- An inline committed-state sequence check was replaced by a shared has_invalid_sequence_number helper, and tests were updated so duplicate submissions are not forwarded again. The reusable pattern is centralizing nonce/sequence validation so all admission routes enforce pending-state and committed-state constraints consistently. Replace ad hoc committed-state checks with a shared invalid-sequence helper, invoke it before acceptance, and update regression tests around duplicate submission behavior.
