# Validation Card

## Metadata

- ID: `bor-2021-12-04-bor-transaction-processing-a7d97ce58`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-state-transition`

## What Confirmed The Issue

- Both Finalize and FinalizeAndAssemble now call changeContractCodeIfNeeded(headerNumber, state) before computing the post-state root.
- The new early-return error handling prevents finalization from proceeding after contract-code change failures.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No body of changeContractCodeIfNeeded is shown, so the exact security invariant being enforced is not fully visible.
- No proof is provided that malformed genesis or block-allocation data is attacker-controlled in a deployed network.
