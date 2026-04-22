# Validation Card

## Metadata

- ID: `scroll-2024-04-12-scroll-transaction-processing-71f88b04`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-binding`

## What Confirmed The Issue

- Evidence 1: In `common/types/encoding/codecv1/codecv1.go`, the patch replaces `return nil, nil, err` with `return nil, common.Hash{}, nil, err`.
- Evidence 2: In `common/types/encoding/codecv1/codecv1.go`, the patch replaces `blob, z, err := constructBlobPayload(batch.Chunks)` with `blob, blobVersionedHash, z, err := constructBlobPayload(batch.Chunks)`.
- Evidence 3: In `common/types/encoding/codecv1/codecv1.go`, the patch replaces `return nil, nil, err` with `return nil, common.Hash{}, nil, err`.

## What Could Have Invalidated It

- Compensating control 1: If the downstream verifier always recomputes and enforces the same canonical hash before accepting the proof, a similar omission may be non-exploitable.
- Compensating control 2: Auxiliary refactors that only change return signatures are not enough; the real issue is whether the canonical hash reaches the challenge preimage.
- Compensating control 3: The evidence supports cryptographic hardening, not a proven end-to-end acceptance flaw.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the downstream verifier always recomputes and enforces the same canonical hash before accepting the proof, a similar omission may be non-exploitable.
- Caution 2: Auxiliary refactors that only change return signatures are not enough; the real issue is whether the canonical hash reaches the challenge preimage.
- Caution 3: The evidence supports cryptographic hardening, not a proven end-to-end acceptance flaw.
