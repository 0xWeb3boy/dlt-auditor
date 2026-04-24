# Root-Cause Card

## Metadata

- ID: `sui-2024-07-16-sui-core-logic-4ba06ed746`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `graphql-query-limit-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Untrusted work must be bounded, attributed, and charged or throttled before it can consume shared validator resources.

## Trust Boundary

- Boundary: untrusted protocol input -> privileged core state

## Attack Surface

- Entrypoint type: state-transition
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: denial-of-service-risk-reduction
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch rewrites Sui GraphQL query limit accounting and tightens several limit-checking behaviors. The evidence supports a correctness and hardening change in a resource-limit guard, but it does not establish a concrete vulnerability, exploit path, or externally demonstrated denial of service.
