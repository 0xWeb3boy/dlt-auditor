# Code-Shape Card

## Metadata

- ID: `bor-2026-02-17-bor-cryptography-d9fac7a4c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- The evidence supports a set of validation hardening changes in consensus and crypto code, especially replacing Uint64()-based block-number continuity checks with explicit big.Int arithmetic in Clique and Bor. That is a real correctness improvement in sensitive code, but the provided material does not establish a concrete vulnerability, exploit path, or security impact, so the change should be treated as security-relevant hardening at most, not a confirmed security fix. Root cause: Validation logic relied on implicit or narrower checks instead of explicit structural validation. In the clearest case, consensus code used a Uint64() comparison for block-number continuity rather than full-precision arithmetic; adjacent changes likewise add explicit malformed-input checks that were previously assumed away.

## Search Motifs

- input decoder feeds state-changing logic before semantic validation
- error path logs or ignores invalid data instead of failing closed
- security-relevant state changes occur before all invariants are checked

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Add explicit structural validation at trust boundaries and use exact representations for numeric checks instead of truncated conversions or downstream assumptions.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
