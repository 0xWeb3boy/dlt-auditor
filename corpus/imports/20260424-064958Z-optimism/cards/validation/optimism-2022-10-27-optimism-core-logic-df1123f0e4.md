# Validation Card

## Metadata

- ID: `optimism-2022-10-27-optimism-core-logic-df1123f0e4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## What Confirmed The Issue

- EngineQueue.Finalize no longer blindly assigns finalized L1 input.
- Older finalized signals are rejected with a monotonicity check on block number.
- New logic only accepts finalization for L1 blocks previously processed by the node.
- Inline comment explicitly cites defense against a corrupt L1 provider causing inconsistent chain recognition.

## What Could Have Invalidated It

- No proof that an external attacker can control or spoof the L1 provider in deployment.
- No demonstrated exploit, incident, or concrete invalid-state acceptance from the old behavior.
- The full post-patch acceptance logic over finalityData is not shown.
- No direct evidence of impact such as chain split, fund risk, or remote denial of service.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an external attacker can control or spoof the L1 provider in deployment.
- No demonstrated exploit, incident, or concrete invalid-state acceptance from the old behavior.
- The full post-patch acceptance logic over finalityData is not shown.
