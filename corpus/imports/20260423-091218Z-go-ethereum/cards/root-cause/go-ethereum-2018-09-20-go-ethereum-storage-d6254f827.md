# Root-Cause Card

## Metadata

- ID: `go-ethereum-2018-09-20-go-ethereum-storage-d6254f827`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-choice-tie-break-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `policy-aware fork-choice tie-break`

## Violated Invariant

- Invariant: Canonical-chain selection should use an explicit tie-break policy for equal-strength competitors instead of a random branch that can discard trusted local work.

## Trust Boundary

- Boundary: Externally imported competing blocks -> local canonical-chain selection.

## Attack Surface

- Entrypoint type: Block import and fork-choice decision.
- Sensitive sink: Reorganizing the canonical head under equal-total-difficulty competition.

## Impact Pattern

- Primary impact: Canonical-state or reorg policy integrity.
- Secondary impact: Reduced resistance to adversarial tie-break races against locally mined blocks.

## Short Reusable Lesson

- Randomness is a poor substitute for policy in consensus-adjacent tie-breaks. If equal-score competitors are possible, the implementation should make its preference rules explicit so external inputs cannot win solely because the local node flips a coin.
