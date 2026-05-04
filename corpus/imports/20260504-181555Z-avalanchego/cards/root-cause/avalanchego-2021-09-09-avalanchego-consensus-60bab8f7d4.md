# Root-Cause Card

## Metadata

- ID: `avalanchego-2021-09-09-avalanchego-consensus-60bab8f7d4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `fork-boundary-state-consistency`

## Violated Invariant

- Invariant: Block verification must reject objects whose type, parent state, and fork activation status are mutually inconsistent.

## Trust Boundary

- Boundary: Peer-supplied blocks cross from network gossip into consensus verification and accepted state.

## Attack Surface

- Entrypoint type: proposer VM block verification at fork transition
- Sensitive sink: accepted post-fork/pre-fork block relationship and consensus state update

## Impact Pattern

- Primary impact: consensus-failure, consensus-integrity
- Secondary impact: high_integrity

## Root Cause

- The validation path for pre-fork children after activation relied on the oracle-parent exception without the added state checks needed to distinguish a genuine pre-fork oracle parent from a parent already associated with post-fork state. ## Walkthrough 1. A pre-fork child is verified after `activationTime` in `vms/proposervm/pre_fork_block.go`. 2. The parent must pass `verifyIsOracleBlock`. 3.

## Short Reusable Lesson

- The verifier accepted a fork-boundary child based on block shape without enough state checks for the parent fork status. The reusable shape is transition logic that must combine type checks with accepted-state facts before allowing compatibility exceptions.
