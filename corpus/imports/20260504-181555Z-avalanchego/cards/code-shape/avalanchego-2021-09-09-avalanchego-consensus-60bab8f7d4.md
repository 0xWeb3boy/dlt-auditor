# Code-Shape Card

## Metadata

- ID: `avalanchego-2021-09-09-avalanchego-consensus-60bab8f7d4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## Code Shape Summary

- The verifier accepted a fork-boundary child based on block shape without enough state checks for the parent fork status. The reusable shape is transition logic that must combine type checks with accepted-state facts before allowing compatibility exceptions.

## Search Motifs

- verifyPreForkChild or similar transition helpers
- oracle block exceptions near activation time
- accepted state lookups added to block-type validation

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Add fail-closed state checks at the fork-boundary verifier so parent status, accepted post-fork state, and block type agree before a child is accepted.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- Rejecting malformed historical blocks is not enough if the path cannot affect current consensus
- If activation has not occurred, post-fork state checks may not apply
- Do not generalize to all fork code without a parent/type/state inconsistency
