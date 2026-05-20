# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-bytecode-root-empty-infinite-loop-33186`
- Bug family: `resource_accounting_and_limits`
- Bug class: `empty-input-nontermination`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `empty-input-termination`

## Violated Invariant

- Bytecode-root helpers must terminate or reject input for empty bytecode.

## Trust Boundary

- Boundary: `user-controlled-bytecode->verification-helper`
- Entrypoint type: `library-function`
- Sensitive sink: `unbounded loop inside bytecode root computation`

## Attack Surface

- Provide or select an empty bytecode blob or contract id with empty bytecode.
- Place the verifier in a queue or withdrawal path.

## Exploit Preconditions

- The loop break condition is unreachable for zero-length bytecode.
- The transaction path does not bound iterations before funds or queue progress is blocked.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `funds-freeze`
- Blast radius: `contract-local`
- Severity guess: `medium`

## Short Reusable Lesson

- Merkle and bytecode helpers need explicit zero-length cases; loop logic written for one-or-more chunks is brittle.
