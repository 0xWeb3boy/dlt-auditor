# Validation Card

## Metadata

- ID: `sui-2024-07-16-sui-core-logic-4ba06ed746`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `graphql-query-limit-hardening`

## What Confirmed The Issue

- GraphQL query depth, node, and payload limits are runtime guards for externally supplied requests.
- Commit metadata says previous __schema detection skipped requests that merely started with introspection; the new logic requires a single operation with a single __schema field.
- Commit metadata says accounting changed from counting up with checked multiplication to counting down from a predefined budget to avoid overflow issues.
- Tests exercise rejection behavior for node and nesting limits under configured zero budgets.

## What Could Have Invalidated It

- No demonstrated exploit query or proof that the old behavior allowed service-wide denial of service.
- No before/after hunk showing the exact old __schema bypass condition in full.
- No evidence of authentication, authorization, confidentiality, consensus, or state-integrity impact.
- No severity, advisory, CVE, or incident context is provided.

## Severity Guidance

- Expected impact band: denial-of-service-risk-reduction
- Expected severity band: low-medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Classify as security-hardening, not security-fix.
- Impact should be limited to resource-exhaustion or denial-of-service risk reduction for GraphQL RPC.
- Do not claim a proven exploitable vulnerability from the supplied evidence.
- Do not claim blockchain consensus or protocol safety impact.
