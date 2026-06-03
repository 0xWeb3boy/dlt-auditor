# Code-Shape Card

Record: `omni-cantina-m01-finalizeblock-postfinalize-error-escape`
Project: `omni-network`
Source finding: `Omni Cantina M-1`

## Search Shape

A deterministic ABCI callback performs optional post-finalize proposer prediction through local RPC and returns those local errors to consensus.

## Motifs

- `FinalizeBlock postFinalize`
- `PostFinalize isNextProposer`
- `cmtAPI.Validators`
- `validators not available`
- `return resp, err`
- `buildOptimistic`

## Negative Signals

- PostFinalize errors are always swallowed before the ABCI return.
- Optimistic build is disabled before local I/O.
- The callback does not query local mutable node state.

## Likely Fix Shape

Treat optimistic build preparation as best effort: log local query failures and never propagate them through FinalizeBlock.
