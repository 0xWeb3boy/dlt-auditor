# Validation Card

## Metadata

- ID: `avalanchego-2025-12-09-avalanchego-storage-e7bd4fb988`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `range-proof-boundary-hardening`

## What Confirmed The Issue

- Evidence: Commit message states clients previously could not prove absence between requested bounds and yielded keys.
- Evidence: Patch generates a start proof from the requested start key even when that key is absent from the trie.
- Evidence: Patch adds bounded iteration with stop_after_key(last_key), supporting enforcement of requested range limits.

## What Could Have Invalidated It

- Compensating control: No proof that malformed or incomplete proofs were accepted by verifiers.
- Compensating control: No demonstrated attacker-controlled call path or exploit scenario.
- Compensating control: No evidence of consensus failure, state forgery, or remote impact.

## Severity Guidance

- Expected impact band: medium_high_integrity
- Expected severity band: high_or_medium
- Severity rationale: Authenticated data structure boundary mistakes can affect proof integrity, but this record does not prove client acceptance of forged state.

## False-Positive Cautions

- Caution: Classify as security hardening for proof completeness, not as a confirmed exploitable security fix.
- Caution: Do not claim forged blockchain state acceptance from the supplied evidence.
- Caution: Do not claim memory safety, access control, denial of service, or consensus impact.
