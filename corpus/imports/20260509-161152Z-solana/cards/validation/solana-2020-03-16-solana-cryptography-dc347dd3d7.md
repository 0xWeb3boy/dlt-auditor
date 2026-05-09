# Validation Card

## Metadata

- ID: `solana-2020-03-16-solana-cryptography-dc347dd3d7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-state-consistency-hardening`

## What Confirmed The Issue

- New accounts hash verifier is described as comparing accounts hashes with trusted validator nodes.
- Verifier comment says the node halts if a mismatch is detected from validators in the trusted set.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
