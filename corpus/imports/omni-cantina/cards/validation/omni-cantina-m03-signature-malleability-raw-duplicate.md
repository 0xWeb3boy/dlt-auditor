# Validation Card

Record: `omni-cantina-m03-signature-malleability-raw-duplicate`
Project: `omni-network`
Source finding: `Omni Cantina M-3`

## Positive Confirmation

Trace k1util.Verify recovery acceptance and then isDoubleSign returning an error for the same attestation id and validator with different signature bytes.

## Preconditions To Confirm

- A prior vote for an unfinalized attestation exists.
- ProcessProposal accepts valid in-window replayed votes.
- k1util.Verify accepts malleable encodings.
- isDoubleSign compares raw bytes for identical votes.

## False-Positive Cautions

- The crypto wrapper enforces low-S canonical signatures.
- The duplicate path compares semantic signer/message only.
- Replayed prior votes are not accepted by ProcessProposal.

## Minimal Reproduction Or Check

Persist one vote, submit a high-S/toggled-recovery duplicate for the same root, and assert proposal validation succeeds while AddVotes finalization errors.
