# Root-Cause Card

## Metadata

- ID: `go-ethereum-2018-09-20-go-ethereum-storage-d6254f827`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-choice-tie-break-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `deterministic-fork-choice`

## Violated Invariant

- Invariant: When an imported block has total difficulty equal to the current canonical chain, fork choice should not randomly replace a locally authored canonical block with an external same-height competitor. The patch makes local-author preservation an explicit tie-break input, with Clique exempted due to a documented deadlock concern.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `expensive RPC-side computation, allocation, or response construction`

## Impact Pattern

- Primary impact: `canonical-chain-integrity`
- Secondary impact: `reorg-resistance`

## Short Reusable Lesson

- The evidence supports a security-hardening finding, not a confirmed vulnerability.
