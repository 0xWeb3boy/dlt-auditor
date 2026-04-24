# Validation Card

## Metadata

- ID: `optimism-2022-09-08-optimism-transaction-processing-a6101c460a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Adds minGossipSize = 66 and rejects decoded gossip messages smaller than a signature plus payload before data[:65] / data[65:] handling.
- The changed code is in BuildBlocksValidator, a peer-facing pubsub validation path for inbound gossip.
- Moves BlockSigningHash and crypto.SigToPub verification ahead of later payload unmarshaling.
- Immediately checks the recovered signer against cfg.P2PSequencerAddress, reducing processing of unauthenticated data.

## What Could Have Invalidated It

- No direct proof in the provided patch that the pre-patch short-input path caused a remotely triggerable panic or node crash.
- No advisory, test, or exploit evidence establishes the real-world impact or attacker requirements.
- The snippets do not show that forged or unauthorized blocks were previously accepted; signature verification already existed and was reordered.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: availability-or-liveness
- Expected severity band: medium_or_low

## False-Positive Cautions

- No direct proof in the provided patch that the pre-patch short-input path caused a remotely triggerable panic or node crash.
- No advisory, test, or exploit evidence establishes the real-world impact or attacker requirements.
- The snippets do not show that forged or unauthorized blocks were previously accepted; signature verification already existed and was reordered.
