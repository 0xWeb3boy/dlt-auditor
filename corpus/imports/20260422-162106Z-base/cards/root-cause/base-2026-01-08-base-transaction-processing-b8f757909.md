# Root-Cause Card

## Metadata

- ID: `base-2026-01-08-base-transaction-processing-b8f757909`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `deadline-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `deadline-enforcement`

## Violated Invariant

- Invariant: The challenger should treat any in-progress dispute game as no longer active for challenge decisions once the live on-chain deadline has passed, regardless of proposal status.

## Trust Boundary

- Boundary: `transaction, batch, or proof input->execution or derivation pipeline`

## Attack Surface

- Entrypoint type: `challenge-orchestration`
- Sensitive sink: `challenge outcome selection or dispute progression state`

## Impact Pattern

- Primary impact: `challenge-decision-errors`
- Secondary impact: `none`

## Short Reusable Lesson

- The challenger should treat any in-progress dispute game as no longer active for challenge decisions once the live on-chain deadline has passed, regardless of proposal status. The challenger's local sync logic tied deadline expiry to proposal status instead of to the dispute deadline itself. As a result, expired but still Unchallenged games could be treated as locally challengeable during cache refresh. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
