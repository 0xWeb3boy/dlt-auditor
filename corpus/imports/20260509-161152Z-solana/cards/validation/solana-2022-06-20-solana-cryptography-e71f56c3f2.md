# Validation Card

## Metadata

- ID: `solana-2022-06-20-solana-cryptography-e71f56c3f2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-packet-slice-access`

## What Confirmed The Issue

- Commit message explicitly says packets are usually from untrusted sources and raw indexing can open attack vectors when offsets are invalid.
- Raw `packet.data()[readonly_signer_offset]` access is replaced with `packet.data(readonly_signer_offset).ok_or(PacketError::InvalidSignatureLen)?`.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: availability_or_resource_exhaustion
- Expected severity band: Medium
- Rationale: The impact primarily affects availability, liveness, or validator resource consumption rather than direct fund theft.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
