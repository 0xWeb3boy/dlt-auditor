# Root-Cause Card

## Metadata

- ID: `scroll-2025-11-28-scroll-transaction-processing-752e4e11`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-fee-bounds`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-fee-sourcing-and-bounds`

## Violated Invariant

- Invariant: Fee relay and oracle update paths should source blob base fee from the canonical L1 node view and cap propagated fee values before relaying them onward.

## Trust Boundary

- Boundary: `l1-chain-state->fee-relay-transaction`

## Attack Surface

- Entrypoint type: `transaction-handler`
- Sensitive sink: `relayed gas-oracle or fee-update transaction sent to L1/L2 components`

## Impact Pattern

- Primary impact: `policy-bypass`
- Secondary impact: `denial-of-service`

## Short Reusable Lesson

- Fee relay and oracle update paths should source blob base fee from the canonical L1 node view and cap propagated fee values before relaying them onward. The patch is security-relevant in theme but not established as a vulnerability fix by the provided evidence. What is directly supported is that the code stopped computing blob base fee locally, switched to querying the L1 node for that value, and added configured caps before relaying fee updates. That is stronger evidence for fee-correctness and liveness hardening than for a confirmed exploitable overflow bug. The robust fix is to stop computing blob fee locally, query the canonical node for the authoritative value, and cap relayed fee parameters before constructing outbound transactions.
