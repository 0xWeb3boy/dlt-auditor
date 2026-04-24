# Validation Card

## Metadata

- ID: `heimdall-v2-2025-08-13-heimdall-v2-storage-8b425ed5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-chain-id-validation`

## What Confirmed The Issue

- Evidence 1: the checkpoint side-message handler now fetches chain-manager params before normal checkpoint validation.
- Evidence 2: the handler returns `VOTE_NO` when params cannot be read or when `msg.BorChainId` differs from configured `BorChainId`.

## What Could Have Invalidated It

- Compensating control 1: the checkpoint proof or root-chain contract already cryptographically binds and verifies the source chain ID.
- Compensating control 2: the handler only accepts locally generated checkpoint messages that cannot cross chain domains.

## Severity Guidance

- Expected impact band: checkpoint-domain-separation / consensus-integrity hardening.
- Expected severity band: medium.

## False-Positive Cautions

- Caution 1: do not treat unrelated app event preservation or command rewiring as security evidence.
- Caution 2: do not claim prior end-to-end acceptance of wrong-chain checkpoints without a demonstrated path.
