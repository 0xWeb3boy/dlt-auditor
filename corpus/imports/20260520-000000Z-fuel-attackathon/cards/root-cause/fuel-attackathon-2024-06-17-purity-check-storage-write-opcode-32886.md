# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-purity-check-storage-write-opcode-32886`
- Bug family: `authz_and_role_gates`
- Bug class: `read-only-effect-gate-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `effect-permission-enforcement`

## Violated Invariant

- A function declared storage(read) or pure must not compile a path that can mutate storage.

## Trust Boundary

- Boundary: `read-only-contract-call->storage-write`
- Entrypoint type: `compiler-semantic-check`
- Sensitive sink: `storage mutation from a function advertised as read-only`

## Attack Surface

- Write inline assembly or reachable call paths containing a storage-write opcode.
- Expose the function as read-only to users or callers.

## Exploit Preconditions

- The purity checker classifies a write-capable opcode as a read.
- No runtime guard blocks storage writes from read-only contexts.

## Impact Pattern

- Primary impact: `unauthorized-action`
- Secondary impact: `state-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Effect systems are security gates when users rely on read-only labels; opcode classifications must be complete and conservative.
