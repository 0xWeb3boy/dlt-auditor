# Code-Shape Card

Record: `omni-cantina-m05-fake-attestation-root-retention`
Project: `omni-network`
Source finding: `Omni Cantina M-5`

## Search Shape

Valid-looking fake attestation roots from a validator are admitted and retained long enough that EndBlock approval and cleanup paths must iterate growing pending state.

## Motifs

- `VerifyVoteExtension voteExtLimit`
- `66 fake attestation roots`
- `attTable InsertReturningId`
- `Status_Pending`
- `Approve list pending`
- `deleteBefore cTrimLag 72000`
- `consensus chain attestations`

## Negative Signals

- Fake roots require quorum before pending insertion.
- Consensus-chain fake roots are pruned quickly.
- Approve and cleanup have bounded per-block work independent of stored pending count.

## Likely Fix Shape

Tighten root admission, lower/parameterize consensus trim lag, cap pending roots per validator/offset, and make lifecycle scans bounded or indexed by actionable work.
