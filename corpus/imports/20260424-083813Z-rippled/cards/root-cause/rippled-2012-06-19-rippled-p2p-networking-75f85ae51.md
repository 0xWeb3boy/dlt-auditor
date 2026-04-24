# Root-Cause Card

## Metadata

- ID: `rippled-2012-06-19-rippled-p2p-networking-75f85ae51`
- Bug family: `authz_and_role_gates`
- Bug class: `consensus-role-gating`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: A protocol operation must be authorized for the exact account, delegate, asset, role, and feature state before it can reach a privileged ledger-state transition.

## Trust Boundary

- Boundary: remote peer message -> local node networking/resource manager

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: peer session state, fetch scheduling, handshake slots, or local resource accounting

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The patch adds explicit mValidating and mProposing state in LedgerConsensus and gates proposal updates, initial proposal publication, and validation creation/relay on those flags.
