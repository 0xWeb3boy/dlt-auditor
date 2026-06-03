# Validation Card

Record: `omni-cantina-m05-fake-attestation-root-retention`
Project: `omni-network`
Source finding: `Omni Cantina M-5`

## Positive Confirmation

Confirm fake but valid-shaped roots are inserted pending, retained by cTrimLag, and iterated by Approve/deleteBefore.

## Preconditions To Confirm

- Vote extension limit allows many votes.
- Fake roots pass validation for the consensus chain/source window.
- Pending roots are inserted in the attestation DB.
- Consensus-chain trim lag retains them for about 72000 blocks.

## False-Positive Cautions

- The roots cannot pass VerifyVoteExtension without real external evidence.
- The table stores only quorum-approved roots.
- EndBlock processing uses bounded pagination/work queues.

## Minimal Reproduction Or Check

Generate many fake consensus-chain attestation roots and measure pending-row growth plus EndBlock scan time before and after the fix.
