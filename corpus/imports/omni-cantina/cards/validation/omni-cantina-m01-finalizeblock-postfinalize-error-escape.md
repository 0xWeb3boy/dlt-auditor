# Validation Card

Record: `omni-cantina-m01-finalizeblock-postfinalize-error-escape`
Project: `omni-network`
Source finding: `Omni Cantina M-1`

## Positive Confirmation

Trace FinalizeBlock to PostFinalize to isNextProposer and confirm local Comet validator-query errors propagate to the ABCI caller.

## Preconditions To Confirm

- Optimistic EVM build is enabled.
- PostFinalize runs after SDK finalization.
- isNextProposer queries local validator state and propagates an error or unavailable validator set.

## False-Positive Cautions

- The helper is disabled or cmtAPI is nil on every deployed path.
- The error is swallowed before the consensus callback return.
- The code runs outside committed block application.

## Minimal Reproduction Or Check

Mock cmtAPI.Validators to fail during PostFinalize and assert FinalizeBlock returns a non-error app response after the fix.
