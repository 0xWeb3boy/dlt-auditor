# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-02-07-stacks-core-p2p-networking-8778d4f74a`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-role-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization-to-state-binding`

## Violated Invariant

- Invariant: Only principals with the role, address ownership, or delegated authority required for a state transition may cause that transition to be accepted.

## Trust Boundary

- Boundary: Remote peer message crosses into networking, relay, or peer-state validation.

## Attack Surface

- Entrypoint type: `p2p_message_or_block`
- Sensitive sink: peer relay buffer, block acceptance path, or network reputation state

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: authorization-bypass

## Short Reusable Lesson

- The patch adds a coordinator check before signer command execution. This is plausibly security relevant because it prevents non-coordinator signers from processing commands, but the supplied evidence does not establish an exploit path, attacker control over commands, or a concrete protocol-security impact.
