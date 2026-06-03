# Raw Finding Summary

Source: Omni Cantina `M-1`
Title: FinalizeBlock is non-deterministic; will lead to consensus failures
Severity: `medium`

## Normalized Summary

The report describes PostFinalize calling isNextProposer inside FinalizeBlock. That helper queries local Comet validator state and can return nondeterministic errors, which are propagated back to CometBFT after app finalization.

## Reusable Failure Shape

A deterministic ABCI callback performs optional post-finalize proposer prediction through local RPC and returns those local errors to consensus.

## Missing Property

`deterministic-finalization-callback-isolation`: FinalizeBlock must not return errors from optional, node-local helper work after deterministic application finalization has succeeded.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `M-1`
